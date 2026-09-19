# Driver de prueba HX711 — celda de carga (ESP32)

Sketch de prueba para el módulo HX711 (ADC de 24 bits + amplificador
integrado, dedicado a celdas de carga). Es una vía **en paralelo** al
[driver del ADS1256](../test_ads1256/INSTRUCCIONES.md), no un reemplazo: el
ADS1256 sigue siendo el ADC elegido a largo plazo para LIBRA (8 canales, para
compartir después con la plataforma AMTI — ver la
[comparativa de sensores](../../Estado-del-arte/SENSORES%20DE%20FUERZA/PYLON/Comparativa-Sensores-Fuerza-Axial-Pylon.md)).

**Por qué probar el HX711 ahora:** sirve para verificar rápido si la celda de
carga y su cableado están bien, aislado del ADS1256 — útil mientras se sigue
diagnosticando el ruido tipo diente de sierra que aparece con ese driver. Si
con el HX711 la lectura sale limpia, el problema está más del lado del
ADS1256/su cableado (o de la fuente/tierra compartida) que de la celda en sí.

## 1. Conexionado

Módulo HX711 genérico (la placa chiquita con capacitores que casi siempre se
vende junto con celdas de carga tipo "barra"/"balanza"):

| Módulo (silkscreen) | ESP32 | Notas |
|---|---|---|
| VCC / VDD | 3.3V | ver aviso de niveles lógicos abajo — **no** usar 5V por ahora |
| GND | GND | común con la celda y el resto del circuito |
| DT (DOUT / DAT) | GPIO32 | salida de datos del módulo → entrada del ESP32 |
| SCK (CLK) | GPIO33 | reloj → salida del ESP32 hacia el módulo |
| E+ (rojo) | — | ya conectado internamente al VCC del módulo (excitación) |
| E- (negro) | — | ya conectado internamente al GND del módulo |
| A+ (verde) | señal + de la celda | canal A, ganancia 128 por defecto |
| A- (blanco) | señal − de la celda | |
| B+ / B- | libres | canal B, ganancia fija en 32 — para una segunda celda, no se usa acá |

### ⚠️ Por qué este módulo NO necesita level shifter (a diferencia del ADS1256)

El chip HX711 acepta alimentación (VCC) entre **2.6V y 5.5V**. Alimentándolo
con el 3.3V del propio ESP32 (en vez de una fuente de 5V separada, como sí
hace falta con el módulo ADS1256 genérico — ver su INSTRUCCIONES.md), sus
pines digitales (DT de salida, SCK de entrada) quedan directamente en lógica
de 3.3V: compatibles con el ESP32 **sin ningún conversor de nivel lógico**.

Contrapartida: la excitación de la celda (E+/E−) también queda a 3.3V en vez
de 5V (el módulo ata E+ al mismo VCC), así que la señal de la celda (mV/V)
sale algo más chica que alimentando a 5V. Para una prueba/comparación rápida
no debería ser problema.

Si más adelante hace falta el máximo rango alimentando a 5V, ahí sí hay que
volver a cuidar los niveles lógicos: DT saldría en lógica de 5V (el ESP32 no
la tolera) y SCK, siendo entrada del HX711, necesitaría ~0.7×5V=3.5V para
registrar HIGH de forma confiable (el 3.3V del ESP32 queda justo por debajo)
— por eso conviene arrancar con 3.3V y no con 5V.

**Tasa de muestreo:** fija por hardware según el pin RATE del módulo — la
gran mayoría de los breakouts genéricos lo dejan fijo en **10 SPS** (algunos
traen un puente/jumper para 80 SPS). No se controla desde este sketch.

## 2. Software (Arduino IDE)

1. Instalar la librería **"HX711" de Bogdan Necula**
   ([github.com/bogde/HX711](https://github.com/bogde/HX711)) desde el
   Library Manager: Herramientas > Administrar Bibliotecas > buscar `HX711` >
   instalar la de Bogdan Necula (a diferencia del ADS1256, acá sí hay una
   librería estándar y muy usada — no hace falta implementar el protocolo a mano).
2. Abrir `test_hx711.ino` como sketch independiente (misma estructura que los
   demás sketches de `Firmware/`).
3. Revisar los pines (`PIN_HX711_DT`, `PIN_HX711_SCK`) contra tu cableado real
   antes de cargar.
4. Cargar y abrir el Monitor Serie a **115200 baudios**.

## 3. Calibración (tara + masa patrón)

Mismo esquema que `test_ads1256.ino` — al arrancar, si ya calibraste antes,
el sketch carga la tara y el factor de escala guardados en flash (NVS).

Para calibrar desde cero (o recalibrar):

1. Con la celda **sin ninguna carga**, escribir `t` y Enter en el Monitor
   Serie. El sketch promedia 20 lecturas y guarda esa cuenta cruda como tara.
2. Poner una **masa patrón conocida** (ej. una pesa de 5 kg) sobre la celda.
3. Escribir `k5.0` y Enter (reemplazando `5.0` por la masa real en kg). El
   sketch promedia 20 lecturas, calcula el delta de cuentas contra la tara y
   guarda el factor de escala (N/cuenta) en flash.
4. Listo — la columna `force_N` de la salida ya refleja la calibración.

Para borrar la tara/calibración guardadas: escribir `r` y Enter.

**Mientras no hayas calibrado** (`calibrated=0` en la salida), la columna
`force_N` se imprime en 0.0 y **no debe tomarse como una lectura real** —
solo sirve para verificar que el HX711 está respondiendo.

## 4. Qué esperar

Salida CSV: `raw_code,force_N,tared,calibrated`

- `raw_code`: cuenta cruda de 24 bits con signo que entrega el HX711 (SIN
  restar la tara). A diferencia del ADS1256, el HX711 no tiene una referencia
  de voltaje bien definida y pública, así que **no** se convierte a voltios
  — se calibra directo de cuentas crudas a Newtons.
- `force_N`: `(raw_code - tara) * factor_escala`, en Newtons. Solo válido si
  `calibrated=1`.
- `tared` / `calibrated`: 1/0 según si ya se hizo `t` / `k<masa>` (o se cargó
  una calibración guardada de flash).

Si ves el mensaje `ERROR: timeout esperando datos del HX711`, el sketch no
está recibiendo respuesta del módulo — lo más común es un problema de
alimentación (VCC/GND) o de cableado de DT/SCK.

## 5. Comparación con el ADS1256

Si el HX711 da una lectura limpia (sin el diente de sierra que se vio con el
ADS1256) usando la **misma celda y el mismo cableado físico de la celda**
(solo cambiando el ADC), es una señal fuerte de que el problema está en el
lado del ADS1256/su alimentación/su tierra — no en la celda ni en su
cableado. Si el HX711 **también** sale ruidoso, el problema es más probable
que esté en la celda, su cableado (EXC+/EXC-/SIG+/SIG-) o la fuente que la
alimenta, independiente del ADC usado.

## 6. Visor en tiempo real (Python)

Igual que con el ADS1256, hay un visor gráfico en
`visor_python/visor_hx711.py` que lee el puerto serial y grafica las cuentas
crudas y la fuerza calibrada en vivo, con una caja de texto para mandar los
comandos `t`, `k<masa>` y `r` sin volver al Monitor Serie.

```
cd visor_python
pip install -r requirements.txt
python visor_hx711.py --port COM5
```

## 7. Registro a CSV (Python)

Para grabar una sesión de pesaje a un archivo CSV (sin gráficos), usar
`visor_python/log_csv_hx711.py` — mismo patrón que `log_csv_ads1256.py`.
Antes de grabar, calibrar una vez con el Monitor Serie o `visor_hx711.py`
(queda guardado en flash):

```
cd visor_python
python log_csv_hx711.py --port COM7 --duracion 30
```

## 8. Siguiente paso

- Una vez confirmado si el HX711 reproduce o no el ruido visto con el
  ADS1256 (ver Secc. 5), volver al diagnóstico de `test_ads1256/` con esa
  información: si el HX711 sale limpio, revisar alimentación/tierra del
  módulo ADS1256 y del level shifter; si también sale ruidoso, revisar la
  celda y su cableado físico (EXC+/EXC-/SIG+/SIG-) antes que el ADC.
- El HX711 es un ADC dedicado de 1-2 canales — **no** sirve para compartirlo
  después con los 6 canales de la AMTI (a diferencia del ADS1256, que sí
  tiene 8 canales para eso). Este sketch es solo para pruebas/diagnóstico,
  no reemplaza al ADS1256 en la arquitectura final de LIBRA.

## 9. Pinout completo del chip HX711 (para diseño de PCB propia)

Si en vez del módulo genérico vas a diseñar tu propia placa con el chip HX711
"pelado" (encapsulado SOP-16L, 16 pines), esto es el pinout completo
verificado contra la hoja de datos oficial de Avia Semiconductor (fabricante
del chip — ver fuente al final):

| Pin | Nombre | Función (hoja de datos) | Qué conectar en tu PCB |
|---|---|---|---|
| 1 | VSUP | Alimentación del regulador interno, 2.7-5.5V | Ver "regulador interno" abajo — en el uso simple, unir a AVDD/DVDD |
| 2 | BASE | Salida de control del regulador analógico interno (transistor PNP externo) | NC (sin conectar) si no usás el regulador interno |
| 3 | AVDD | Alimentación analógica, 2.6-5.5V | Tu fuente de 3.3V (misma que DVDD si no usás el regulador — igual que el módulo genérico) |
| 4 | VFB | Entrada de realimentación del regulador | A AGND si no usás el regulador interno |
| 5 | AGND | Tierra analógica | GND — **único pin de tierra del chip**, no hay DGND separado en este encapsulado |
| 6 | VBG | Salida de bypass de la referencia interna | Capacitor de 0.1uF a AGND, lo más cerca posible del pin |
| 7 | INA- | Entrada negativa, canal A | Señal− de la celda de carga (canal usado en `test_hx711.ino`) |
| 8 | INA+ | Entrada positiva, canal A | Señal+ de la celda de carga |
| 9 | INB- | Entrada negativa, canal B | Libre, o ruteala a un header por si más adelante hace falta una 2da celda |
| 10 | INB+ | Entrada positiva, canal B | Libre (ganancia fija en 32, no configurable) |
| 11 | PD_SCK | Reloj serie + control de power-down (activo en alto) | GPIO del ESP32 (salida) — GPIO33 en el sketch actual |
| 12 | DOUT | Salida de datos serie | GPIO del ESP32 (entrada) — GPIO32 en el sketch actual |
| 13 | XO | Salida del oscilador a cristal | NC si usás el oscilador interno (ver nota) |
| 14 | XI | Entrada del oscilador a cristal, o reloj externo. 0 = usa el oscilador interno | A AGND para usar el oscilador interno (recomendado, no hace falta cristal) |
| 15 | RATE | Selección de tasa de datos: 0=10Hz, 1=80Hz | A AGND para 10Hz (recomendado para una celda de carga estática/cuasi-estática) |
| 16 | DVDD | Alimentación digital, 2.6-5.5V | Misma fuente de 3.3V que AVDD |

### Notas para el diseño de la PCB

- **Regulador interno:** el HX711 trae un LDO interno (VSUP + BASE + VFB + un
  transistor PNP externo tipo S8550) para generar una AVDD estable a partir
  de una fuente más ruidosa. Para un prototipo simple como el que ya
  validaste con el módulo genérico **no hace falta usarlo**: alimentás AVDD y
  DVDD directo con 3.3V, dejás BASE sin conectar y VFB a AGND — así vienen
  armados la mayoría de los módulos breakout genéricos.
- **Una sola tierra:** a diferencia del ADS1256 (AGND y DGND separados en sus
  28 pines), el HX711 solo tiene un pin de tierra (AGND, pin 5) — analógico y
  digital comparten la misma referencia en este chip.
- **Oscilador:** no hace falta cristal externo — atando XI a AGND (y dejando
  XO sin conectar) el chip usa su oscilador interno, igual que los módulos
  genéricos.
- **Excitación de la celda (medición ratiométrica):** conectá el EXC+ de la
  celda de carga directo a AVDD (la misma alimentación del chip, no una
  fuente aparte) y EXC- a AGND. Esto es clave: como la referencia interna del
  ADC deriva de AVDD, cualquier variación en la alimentación afecta por igual
  a la excitación de la celda y a la referencia — se cancela y no mete error.
  Por eso el HX711 no necesita una fuente de excitación regulada aparte, a
  diferencia de un ADC con referencia fija como el ADS1256.
- **Desacople:** capacitor cerámico de 0.1uF bien cerca de AVDD/DVDD a AGND,
  más uno de mayor valor (ej. 10uF) en la entrada de alimentación general —
  práctica estándar de buen diseño aunque el datasheet no lo detalle para
  este modo simplificado.
- **Filtro en las entradas (opcional, recomendado):** un filtro RC chico (ej.
  100Ω en serie + 100nF entre INA+/INA- a tierra) ayuda a rechazar ruido de
  RF/EMI captado por cables largos hacia la celda — varios diseños de
  referencia lo incluyen.
- **Encapsulado:** SOP-16L (16 pines, montaje superficial). Para el footprint
  exacto (dimensiones, paso entre pines) revisar el dibujo mecánico en la
  hoja de datos completa (fuente abajo), o buscar una librería ya hecha para
  KiCad/Eagle/Altium — es un chip muy común, probablemente ya exista un
  footprint listo.

### Fuentes consultadas

- [HX711 24-Bit ADC — Pinout, Datasheet, Interfacing Examples](https://microcontrollerslab.com/hx711-adc-weigh-scales/) (rango de alimentación 2.6-5.5V, ganancias por canal, pin RATE 10/80 SPS)
- [GroundStudio HX711 module datasheet](https://mm.digikey.com/Volume0/opasdata/d220001/medias/docus/5864/HX711%20Module.PDF) (etiquetas del breakout: VCC/GND/DAT/CLK/E+/E-/A+/A-/B+/B-, rango de alimentación 2.7-5.5V)
- [HX711 Arduino Library — Bogdan Necula, GitHub](https://github.com/bogde/HX711) (librería usada en este sketch: begin, wait_ready_timeout, read, read_average, tare, set_scale)
- [HX711 datasheet — Avia Semiconductor (mirror SparkFun)](https://cdn.sparkfun.com/datasheets/Sensors/ForceFlex/hx711_english.pdf) (pinout completo del chip SOP-16L, circuito de aplicacion, regulador interno)
