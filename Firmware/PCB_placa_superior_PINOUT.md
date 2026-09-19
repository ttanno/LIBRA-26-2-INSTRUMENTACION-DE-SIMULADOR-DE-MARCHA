# Pinout de referencia — Placa superior (ESP32 + 2x VL53L1X + entrada HX711)

Referencia de conexionado para la placa que va **arriba** (ESP32-WROOM-32U +
los dos sensores de distancia ToF VL53L1X + entrada para el módulo HX711 +
borneras de tornillo para la celda de carga). El **BNO055 va en una placa
aparte**, montada abajo en la plataforma — no está en este documento (ver
`test_bno055/` y `test_bno055_oversampling/`).

Todos los datos de abajo están verificados contra hojas de datos/documentación
oficial (fuentes al final).

## 0. Topología general: el ESP32 es el único "cerebro"

No hay ningún microcontrolador en la placa de abajo — esa placa es solo el
BNO055 + un conector. **Todo** (HX711, los 2 ToF, y el BNO055) se conecta al
mismo ESP32 de la placa de arriba: HX711 y los ToF directo en la misma
placa, y el BNO055 por un cable/conector entre las dos placas.

Para el BNO055, en vez de compartir el mismo bus I2C de los ToF (que ya tiene
que manejar la secuencia de SHUT + reasignación de direcciones, y le llegaría
por un cable más largo entre placas, con más chance de ruido), conviene usar
el **segundo bus I2C que trae el ESP32** (tiene dos periféricos I2C
independientes por hardware) dedicado solo al BNO055:

| Señal | GPIO | Notas |
|---|---|---|
| SDA2 (bus dedicado al BNO055) | GPIO17 | libre, no strapping, no solo-entrada |
| SCL2 (bus dedicado al BNO055) | GPIO16 | libre, no strapping, no solo-entrada |

Así el BNO055 queda solo en su propio bus (sin competir por direcciones con
los ToF) y el conector entre las dos placas lleva 4 hilos: **3.3V, GND,
GPIO17 (SDA2), GPIO16 (SCL2)**.

## 1. ESP32-WROOM-32U DevKitC — pinout físico de 30 pines

Layout estándar del devkit de 30 pines (el mismo que aparece en el
esquemático, `U6`):

| Columna izquierda (de arriba hacia abajo) | Columna derecha (de arriba hacia abajo) |
|---|---|
| EN | 3V3 |
| VP (GPIO36, solo entrada) | GND |
| VN (GPIO39, solo entrada) | GPIO15 |
| GPIO34 (solo entrada) | GPIO2 |
| GPIO35 (solo entrada) | GPIO0 |
| GPIO32 | GPIO4 |
| GPIO33 | GPIO16 |
| GPIO25 | GPIO17 |
| GPIO26 | GPIO5 |
| GPIO27 | GPIO18 |
| GPIO14 | GPIO19 |
| GPIO12 | GND |
| GPIO13 | GPIO21 |
| GND | RX0 |
| VIN (5V) | TX0 |
| | GPIO22 |
| | GPIO23 |

**Pines a evitar para señales críticas de este diseño:**

- **Strapping pins (afectan el arranque):** GPIO0, GPIO2, GPIO5, GPIO12,
  GPIO15 — no usar para SHUT/XSHUT ni SCK si se puede evitar (un glitch en el
  arranque podría interferir con el modo de boot del ESP32).
- **Solo entrada (no pueden manejar salidas):** GPIO34, GPIO35, GPIO36 (VP),
  GPIO39 (VN) — no sirven para SCK (HX711) ni para SHUT (ToF), que necesitan
  ser salidas. Sí podrían usarse para una señal que solo se lee (ej. un INT
  de un ToF, si se decide rutearlo).
- **Reservados para la flash SPI interna (no exponer, no usar):** GPIO6-11 —
  no vienen en el header de este devkit de 30 pines, así que no aplica acá,
  pero importante no repetirlos si se diseña un módulo ESP32 "pelado" a
  futuro.

## 2. VL53L1X (sensor de distancia ToF, I2C) — pinout del breakout

Pinout típico de un breakout VL53L1X (I2C + XSHUT + interrupción), que
coincide con las etiquetas `VCC/GND/SDA/SCL/INT/SHUT` del esquemático (`U2`,
`U3`):

| Pin del breakout | Función | Notas |
|---|---|---|
| VCC (VIN) | Alimentación | Acepta 3V-5V en la mayoría de los breakouts (traen su propio regulador a la tensión del chip); revisar el datasheet específico del módulo `MYTOF400C-VL53L1X` antes de fijarlo, pero 3.3V del ESP32 es la opción segura |
| GND | Tierra | Común con el ESP32 |
| SCL | Reloj I2C | Al bus I2C del ESP32 (GPIO22 recomendado) — necesita resistencia pull-up (los breakouts suelen traerla integrada, ~10kΩ) |
| SDA | Datos I2C | Al bus I2C del ESP32 (GPIO21 recomendado) — mismo pull-up |
| INT (GPIO1 del chip) | Salida de interrupción, nivel 2.8V | Opcional — se puede dejar sin conectar (NC) si el firmware va a leer por *polling* en vez de por interrupción |
| SHUT (XSHUT) | Reset/apagado, **activo en bajo** | Nivel desplazado (compatible 3V/5V) — **imprescindible un GPIO independiente por cada sensor**, ver Secc. 4 |

**Dirección I2C:** los VL53L1X vienen todos con la dirección fija de fábrica
**0x29**. Como tenés **dos sensores idénticos en el mismo bus**, no se pueden
diferenciar solo por dirección — hay que usar el pin **SHUT** de cada uno
para reconfigurar la dirección de uno de los dos por software en el arranque
(secuencia típica: mantener ambos en reset, sacar a uno del reset,
reasignarle una dirección I2C distinta con `setAddress()` o equivalente de la
librería que se use, y recién ahí sacar al segundo del reset con la
dirección 0x29 que le queda por default).

## 3. HX711 (módulo breakout, no el chip pelado) — pinout

Ya documentado en detalle en
[`test_hx711/INSTRUCCIONES.md`](test_hx711/INSTRUCCIONES.md) — se repite acá
para tener todo junto:

| Pin del módulo (`XWF-HX711` en el esquemático) | Conexión |
|---|---|
| VCC | 3.3V del ESP32 (sin level shifter — ver justificación en `test_hx711/INSTRUCCIONES.md`) |
| GND | GND común |
| DT (DOUT) | GPIO del ESP32, entrada — GPIO32 en el sketch actual |
| SCK (CLK) | GPIO del ESP32, salida — GPIO33 en el sketch actual |
| E+ / E- | A la bornera de tornillo → Rojo/Negro de la celda de carga (excitación) |
| A+ / A- | A la bornera de tornillo → Verde/Blanco de la celda de carga (señal, canal A) |
| B+ / B- | Libres (canal B, ganancia fija 32 — para una segunda celda si hiciera falta) |

**Código de colores de la celda de carga (4 hilos):** Rojo=EXC+, Negro=EXC-,
Verde=SIG+, Blanco=SIG- (verificar contra el datasheet de la celda que se
termine usando — no es 100% universal entre fabricantes).

## 4. Asignación de pines recomendada para esta placa

Juntando todo lo anterior, evitando strapping pins y pines de solo-entrada:

| Señal | GPIO ESP32 | Justificación |
|---|---|---|
| I2C SDA (compartido, ambos ToF) | GPIO21 | pin I2C por default del ESP32 |
| I2C SCL (compartido, ambos ToF) | GPIO22 | pin I2C por default del ESP32 |
| SHUT ToF1 (U3) | GPIO25 | salida, no strapping |
| SHUT ToF2 (U2) | GPIO26 | salida, no strapping |
| HX711 DT | GPIO32 | ya usado en `test_hx711.ino`, mantiene el firmware actual sin cambios |
| HX711 SCK | GPIO33 | ya usado en `test_hx711.ino`, mantiene el firmware actual sin cambios |
| INT ToF1 / ToF2 (opcional) | sin conectar (NC), o GPIO27/GPIO14 si se decide usar interrupciones | no hace falta para lectura por polling |
| I2C SDA2 (bus dedicado, BNO055 en la otra placa) | GPIO17 | segundo periferico I2C del ESP32, ver Secc. 0 |
| I2C SCL2 (bus dedicado, BNO055 en la otra placa) | GPIO16 | segundo periferico I2C del ESP32, ver Secc. 0 |

Con esta asignación, GPIO0/2/5/12/15 (strapping) y GPIO34/35/36/39 (solo
entrada) quedan libres para lo que haga falta después (ej. UART/JTAG de
debug, otro sensor, etc.) sin comprometer el arranque del ESP32 ni necesitar
salidas donde no se puede.

## 5. Siguiente paso

- Confirmar en el datasheet específico del módulo `MYTOF400C-VL53L1X` (no
  solo el chip VL53L1X genérico) el rango de alimentación exacto y si trae
  pull-ups I2C integradas, antes de rutear VCC/SDA/SCL en la placa.
- Escribir el sketch de prueba para los dos VL53L1X con secuencia de
  SHUT + reasignación de dirección I2C (pendiente, ver conversación del
  Firmware — análogo a como se hizo `test_hx711.ino` para la celda).

### Fuentes consultadas

- [ESP32-DevKitC V4 Pinout Diagram + Safe GPIOs](https://esp32.co.uk/esp32-devkitc-v4-pinout-diagram-safe-gpios/) (categorías de pines: input-only, strapping, flash)
- [ESP32 Pinout Reference — Last Minute Engineers](https://lastminuteengineers.com/esp32-pinout-reference/) (layout físico de 30 pines izquierda/derecha)
- [Adafruit VL53L1X — Pinouts](https://learn.adafruit.com/adafruit-vl53l1x/pinouts) (VIN/GND/SCL/SDA/GPIO(INT)/XSHUT, dirección I2C 0x29, nivel logico de XSHUT)
- `Firmware/test_hx711/INSTRUCCIONES.md` (pinout del módulo HX711 y de la celda de carga, ya verificado en este mismo proyecto)
