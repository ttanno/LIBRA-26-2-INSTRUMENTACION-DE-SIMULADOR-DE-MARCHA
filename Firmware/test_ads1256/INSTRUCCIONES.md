# Driver de prueba ADS1256 — celda de carga (ESP32)

Sketch de prueba para el ADC ADS1256 (24 bits, 8 canales, SPI), elegido en la
[comparativa de sensores de fuerza](../../Estado-del-arte/SENSORES%20DE%20FUERZA/PYLON/Comparativa-Sensores-Fuerza-Axial-Pylon.md)
para leer la celda de carga del pylon. A diferencia de los sketches de IMU
(BNO055/MPU6050, I2C con librerías Adafruit ya hechas), acá no hay librería
de Arduino Library Manager para el ADS1256, así que el protocolo (SPI +
registros) está implementado directo en `test_ads1256.ino`.

**Por qué ADS1256 y no HX711:** el HX711 trae amplificador + ADC integrados
y es más simple de usar, pero es un ADC dedicado (1-2 canales). El ADS1256
tiene 8 canales y la idea es **compartirlo** con los 6 canales analógicos de
la plataforma AMTI (Fx,Fy,Fz,Mx,My,Mz) más adelante — ver
`Reportes-Semanales/S4/Pendientes.md`, sección de la AMTI. Ese trabajo de
multiplexar los 6 canales de la AMTI **sigue pendiente**; este sketch solo
deja listo el canal de la celda de carga (AIN0) y el MUX preparado para
extenderse.

**Estado de la celda de carga:** todavía no hay celda final elegida (ver
Pendientes S4). Por eso este sketch no trae un factor de escala de fábrica:
implementa tara + calibración con una masa patrón conocida, igual que se
haría con cualquier celda. Cuando se elija la celda definitiva, esta misma
rutina de calibración sirve sin cambios.

## 1. Conexionado

**Si tu módulo es el genérico de placa roja que se vende como "Teyleten
Robot ADS1256 24-bit 8-Channel"** (mismo diseño vendido también como
HiLetgo/JESSINIE/otros — ver Secc. 7.1), el header ya viene simplificado a
estos pines (no expone AVDD/DVDD/AGND/DGND/VREFP/VREFN/CLKIN por separado,
ni un pin RESET):

| Módulo (silkscreen) | ESP32 | Notas |
|---|---|---|
| DIN | GPIO23 | MOSI |
| DOUT | GPIO19 | MISO — **ver aviso de niveles lógicos abajo** |
| SCLK | GPIO18 | |
| CS | GPIO5 | |
| DRDY | GPIO4 | entrada; el ADS1256 la pone en LOW cuando hay un dato nuevo listo — **ver aviso de niveles lógicos abajo** |
| PDWN | 5V del módulo | siempre encendido, no se controla por software acá |
| 5V | fuente 5V (no el 3.3V del ESP32) | el módulo es de 5V fijo |
| GND | GND del ESP32 (común) | |
| AIN0...AIN7 | — | canales analógicos; este sketch usa AIN0 (señal) + AINCOM (común, ya interna del módulo) |

No hay pin RESET expuesto en este módulo — por eso el sketch trae
`ADS1256_USE_RESET_PIN` en `0` por defecto (usa solo el comando de software
RESET/init, no un pin físico).

**⚠️ Aviso de niveles lógicos:** este módulo se alimenta a 5V fijos (no se
encontró versión con jumper a 3.3V). Sus salidas hacia el ESP32 (**DOUT** y
**DRDY**) quedan entonces en lógica de 5V, y los pines del ESP32 **no son
tolerantes a 5V** (máximo absoluto ~3.6V) — conectarlos directo puede dañar
el ESP32. Hace falta un **conversor de nivel lógico** (level shifter
bidireccional barato, ej. módulo con TXS0108E o BSS138) entre el módulo y
el ESP32 antes de alimentar todo por primera vez. Para DIN/SCLK/CS/PDWN
(sentido ESP32 → módulo) un 3.3V suele registrar como HIGH igual, pero no
está garantizado por el fabricante — si van a armar el level shifter de
todas formas, pasen esas 4 líneas también.

Si en cambio tenés el módulo con el chip "pelado" (SSOP-28, para diseño de
placa propia) o un breakout distinto que sí expone AVDD/DVDD/AGND/DGND/
VREFP/VREFN/CLKIN por separado, esos pines no son intercambiables con la
tabla de arriba — revisar el datasheet/silkscreen de ese módulo específico
(pinout completo del chip en la Secc. 7.1).

Se usaron los pines VSPI por defecto del ESP32 (18/19/23 + CS en GPIO5) a
propósito, para dejar libres GPIO21/22 (I2C) que ya usan los sketches de IMU
— así se puede tener el ADS1256 (SPI) y un IMU (I2C) conectados al mismo
ESP32 al mismo tiempo sin conflicto de pines, que es justo la arquitectura
multi-sensor que pide el proyecto.

**Señal de entrada:** este sketch lee AIN0 contra AINCOM (single-ended), y
asume que ya le llega una señal **acondicionada** (amplificador de
instrumentación, ej. INA818, como quedó anotado en la comparativa) — el
ADS1256 por sí solo NO amplifica lo suficiente la salida cruda de un puente
de Wheatstone. Si todavía no tienes el amplificador armado, podés probar el
sketch igual conectando una fuente de voltaje conocida (ej. un divisor
resistivo) a AIN0 para verificar que el driver lee bien antes de meter la
celda real.

## 2. Software (Arduino IDE)

1. No hace falta instalar ninguna librería extra para el ADS1256 (usa
   `SPI.h`, que ya viene con el core de ESP32).
2. Abrir `test_ads1256.ino` como sketch independiente (misma estructura que
   los demás sketches de `Firmware/`).
3. Revisar las constantes de configuración al inicio del archivo
   (`ADS1256_VREF`, `ADS1256_PGA_CODE`/`ADS1256_PGA_GANANCIA`,
   `ADS1256_DRATE_CODE`) contra tu hardware real antes de cargar.
4. Cargar y abrir el Monitor Serie a **115200 baudios**.

## 3. Calibración (tara + masa patrón)

Al arrancar, si ya calibraste antes, el sketch carga la tara y el factor de
escala guardados en flash (NVS) — igual mecanismo que usa
`homing_absoluto.ino` para el cero del pivote.

Para calibrar desde cero (o recalibrar):

1. Con la celda **sin ninguna carga**, escribir `t` y Enter en el Monitor
   Serie. El sketch promedia 20 lecturas y guarda ese voltaje como tara.
2. Poner una **masa patrón conocida** (ej. una pesa de 5 kg) sobre la celda.
3. Escribir `k5.0` y Enter (reemplazando `5.0` por la masa real en kg). El
   sketch promedia 20 lecturas, calcula el delta de voltaje contra la tara y
   guarda el factor de escala (N/V) en flash.
4. Listo — la columna `force_N` de la salida ya refleja la calibración.

Para borrar la tara/calibración guardadas: escribir `r` y Enter.

**Mientras no hayas calibrado** (`calibrated=0` en la salida), la columna
`force_N` se imprime en 0.0 y **no debe tomarse como una lectura real** —
solo sirve para verificar que el ADC está respondiendo.

## 4. Qué esperar

Salida CSV: `raw_code,voltage_V,force_N,tared,calibrated`

- `raw_code`: código crudo de 24 bits con signo que entrega el ADC (rango
  aprox. ±8 388 607).
- `voltage_V`: `raw_code` convertido a voltios en la entrada del ADS1256,
  según el Vref y la ganancia configurados — **sin** restar la tara.
- `force_N`: `(voltage_V - tara) * factor_escala`, en Newtons. Solo válido
  si `calibrated=1`.
- `tared` / `calibrated`: 1/0 según si ya se hizo `t` / `k<masa>` (o se
  cargó una calibración guardada de flash).

Si ves el mensaje `ERROR: timeout esperando DRDY del ADS1256`, el sketch no
está recibiendo el pulso de "dato listo" — lo más común es un problema de
cableado (DRDY, CS, alimentación) o que el CLKIN del ADS1256 no está
oscilando (revisar que el cristal del breakout esté bien montado).

## 5. Siguiente paso

- Definir y armar el acondicionamiento analógico real (puente de Wheatstone
  + INA818) una vez que se cierre la elección de celda de carga (Pendientes
  S4, "Selección de sensor de fuerza del pylon" — sigue abierto).
- Diseñar la lectura multiplexada de los 6 canales de la AMTI compartiendo
  este mismo ADS1256 (Pendientes S4, sección AMTI) — implica rotar el
  registro MUX entre conversiones y sincronizar contra el DRDY de cada una,
  algo que este sketch todavía no hace (solo lee un canal fijo).
- Una vez con la celda real montada, validar la calibración con al menos 2-3
  masas patrón distintas (no solo una) para confirmar linealidad, en línea
  con el objetivo de validación cruzada trazable a ISO 7500-1.

## 6. Visor en tiempo real (Python)

Igual que con los sketches de IMU, hay un visor gráfico en
`visor_python/visor_ads1256.py` que lee el puerto serial y grafica el
voltaje crudo y la fuerza calibrada en vivo.

```
cd visor_python
pip install -r requirements.txt
python visor_ads1256.py --port COM5
```

El visor muestra si la lectura está tarada/calibrada (según las columnas
`tared`/`calibrated` de cada línea) y permite reenviar los comandos `t`,
`k<masa>` y `r` directo desde la ventana del gráfico (sin volver al Monitor
Serie del Arduino IDE), para no tener que andar cambiando de programa a
mitad de la calibración.

## 7. Pinout de referencia de los componentes

Verificado contra las hojas de datos oficiales de Texas Instruments (ver
fuentes al final). Esto complementa la tabla de la Secc. 1 (esa es la que
importa para cablear con el ESP32); acá está el pinout completo de cada
chip, útil si diseñan su propia placa o si necesitan mapear los pines de un
breakout/módulo a la función real del chip.

### 7.1 ADS1256 (chip "pelado", encapsulado SSOP-28)

| Pin | Nombre | Función |
|---|---|---|
| 1 | AVDD | Alimentación analógica |
| 2 | AGND | Tierra analógica |
| 3 | VREFN | Referencia negativa |
| 4 | VREFP | Referencia positiva |
| 5 | AINCOM | Entrada analógica común (usada como "AINN" en modo single-ended) |
| 6 | AIN0 | Entrada analógica 0 |
| 7 | AIN1 | Entrada analógica 1 |
| 8 | AIN2 | Entrada analógica 2 |
| 9 | AIN3 | Entrada analógica 3 |
| 10 | AIN4 | Entrada analógica 4 |
| 11 | AIN5 | Entrada analógica 5 |
| 12 | AIN6 | Entrada analógica 6 |
| 13 | AIN7 | Entrada analógica 7 |
| 14 | SYNC/PDWN | Sincronización / apagado (activo en LOW) |
| 15 | RESET | Reset (activo en LOW) |
| 16 | DVDD | Alimentación digital |
| 17 | DGND | Tierra digital |
| 18 | XTAL2 | Cristal (salida del oscilador) |
| 19 | XTAL1/CLKIN | Cristal (entrada) o reloj externo |
| 20 | CS | Chip select (activo en LOW) |
| 21 | DRDY | Dato listo (salida, activo en LOW) |
| 22 | DOUT | Salida de datos SPI (MISO) |
| 23 | DIN | Entrada de datos SPI (MOSI) |
| 24 | SCLK | Reloj SPI |
| 25 | D0/CLKOUT | GPIO 0 / salida de reloj |
| 26 | D1 | GPIO 1 |
| 27 | D2 | GPIO 2 |
| 28 | D3 | GPIO 3 |

Nota: AIN0-AIN7 y AINCOM son los 8 canales que se piensan compartir con la
celda de carga (AIN0, ya usado por este sketch) y los 6 canales de la AMTI
(AIN1-AIN6 quedarían libres para eso, ver Secc. 5).

**Si usan un módulo/breakout** (ej. Waveshare "High Precision AD/DA Board",
o el clon genérico vendido como "Teyleten Robot"/HiLetgo/JESSINIE — placa
roja de 24 bits/8 canales, mismo diseño de fábrica reempaquetado bajo varias
marcas) en vez del chip suelto: el módulo ya trae AVDD/DVDD, AGND/DGND,
VREFP/VREFN y el cristal de XTAL1/XTAL2 resueltos internamente, y expone
solo un subconjunto simplificado de pines en el header.

No existe un datasheet propio publicado por "Teyleten Robot" — es un
revendedor de este diseño genérico, no el fabricante del chip ni de la
placa. Confirmado cruzando la ficha de este mismo módulo bajo otras marcas
(Agarwal Electronics y HiLetgo, ver fuentes): el header trae **5V, GND,
SCLK, DIN, DOUT, CS, DRDY, PDWN** + los 8 canales analógicos `AIN0`...`AIN7`
— **sin** un pin RESET separado, y con una referencia de voltaje a bordo
(típico ADR03, 2.5V — coincide con `ADS1256_VREF` del sketch). Esos son los
pines que se cablearon en la Secc. 1, junto con el aviso de niveles lógicos
(el módulo es de 5V fijo, sin jumper a 3.3V en ninguna de las fichas
revisadas). **Si tu unidad física trae un silkscreen distinto, verificalo
contra las fotos del vendedor antes de energizar** — entre revendedores del
mismo diseño a veces cambia el rotulado, aunque el circuito sea idéntico.

### 7.2 INA818 (amplificador de instrumentación, 8 pines SOIC/VSSOP)

Es el amplificador propuesto en la comparativa de sensores para acondicionar
la salida cruda mV/V del puente de Wheatstone antes de entregarla al ADS1256
(ver nota de la Secc. 1). Todavía no está armado ni elegido en definitiva
(la celda de carga tampoco lo está), así que esto es la referencia para
cuando se arme el circuito.

| Pin | Nombre | Función |
|---|---|---|
| 1 | RG | Resistencia de ganancia (junto con el pin 8) |
| 2 | –IN | Entrada inversora |
| 3 | +IN | Entrada no inversora |
| 4 | –VS | Alimentación negativa |
| 5 | REF | Entrada de referencia (offset de salida) |
| 6 | OUT | Salida |
| 7 | +VS | Alimentación positiva |
| 8 | RG | Resistencia de ganancia (junto con el pin 1) |

- **Ganancia:** `G = 1 + (50 kΩ / RG)`. Ej.: RG=1kΩ -> G≈51; RG=499Ω -> G≈101.
  El valor exacto depende de cuánto entregue el puente de la celda elegida
  (mV/V) y cuánto rango de entrada quieran usarle al ADS1256 — todavía
  pendiente de calcular hasta cerrar la celda.
- **Alimentación:** acepta single-supply 4.5-36V o dual ±2.25-18V. Con el
  ESP32 a 3.3V, probablemente convenga alimentar el INA818 con una fuente
  separada de 5V (no directo del ESP32) para tener margen de swing en la
  salida.
- **REF (pin 5):** en single-supply, TI recomienda llevarlo a un nivel de
  offset preciso de media alimentación (ej. 2.5V con fuente de 5V) mediante
  una fuente de bajo-impedancia dedicada (ej. un divisor resistivo con buffer,
  o un IC de referencia) — **no** dejarlo flotando ni conectarlo directo a
  VREFP del ADS1256 (esa referencia debe quedar limpia para el propio ADC).
  Esto centra la salida en el "cero" de fuerza y deja rango simétrico para
  compresión/tracción si la celda mide en ambos sentidos.
- **Salida (pin 6) -> AIN0 del ADS1256** (canal ya configurado en el sketch).

### 7.3 Celda de carga genérica (puente de Wheatstone, 4 hilos)

Todavía sin celda final elegida (ver Pendientes S4), pero el código de
colores de 4 hilos es el mismo para casi todas las candidatas de la
comparativa (S-type, donut, strain-gauge propia):

| Color (convención más común) | Función |
|---|---|
| Rojo | Excitación + (E+ / EXC+) |
| Negro | Excitación – (E– / EXC–) |
| Verde | Señal + (S+ / SIG+) |
| Blanco | Señal – (S– / SIG–) |

**Importante:** este código de colores NO es 100% universal entre
fabricantes (algunos usan amarillo/azul para la señal, por ejemplo) —
verificar siempre contra la hoja de datos de la celda que se termine
eligiendo. E+/E– van a la excitación del puente (alimentación de la galga,
típicamente 5-10V regulados y estables); S+/S– son la salida diferencial de
pocos mV que entra a IN+/IN– del INA818.

### Fuentes consultadas

- [ADS1256 datasheet (SBAS288) — Texas Instruments](https://www.ti.com/lit/ds/symlink/ads1256.pdf)
- [INA818 datasheet — Texas Instruments](https://www.ti.com/lit/ds/symlink/ina818.pdf)
- [Teyleten Robot ADS1256 24-bit 8-Channel ADC Module — listado en Amazon](https://www.amazon.com/Teyleten-Robot-8-Channel-High-Precision-Acquisition/dp/B0F4DPM9J1) (sin datasheet propio publicado; mismo diseño que las fuentes siguientes)
- [ADS1256 24-Bit ADC Module — ficha técnica, Agarwal Electronics](https://www.agarwalelectronics.com/product/7580/) (mismo diseño de módulo, header/pines confirmados)
- [HiLetgo ADS1256 5V 8 Channel 24 Bit ADC Module — manual, Manuals+](https://manuals.plus/asin/B09KGXC44Q) (mismo diseño de módulo, header/pines confirmados por segunda fuente independiente)
