# Conexiones — Placa del ESP32 (hub de sensores), Semana 5

**Fecha:** 10/09/2026
**Contexto:** avance sobre el pendiente de diseño mecánico/electrónico de la S5 (`Reportes-Semanales/S5/Pendientes.md`). Esta nota define el conexionado eléctrico propuesto para la placa que centraliza el ESP32, con el ADS1256 y las entradas de los demás sensores (IMU, distancia, ángulo, fuerza) como "salidas" hacia el resto del sistema. Es un punto de partida para el ruteo físico (protoboard/PCB), no un cierre — hay decisiones pendientes marcadas explícitamente abajo.

---

## 1. Pines que el firmware actual ya fija (no mover sin actualizar los `.ino`)

| Función | Pin(es) ESP32 | Fuente |
|---|---|---|
| I2C (SDA / SCL) | GPIO21 / GPIO22 | `test_bno055.ino`, `test_mpu6050.ino`, `homing_absoluto.ino` |
| Driver del husillo — STEP | GPIO26 | `homing_husillo_hall.ino` |
| Driver del husillo — DIR | GPIO27 | `homing_husillo_hall.ino` |
| Driver del husillo — ENABLE (activo en bajo) | GPIO25 | `homing_husillo_hall.ino` |
| Sensor Hall (homing husillo) — entrada con pull-up | GPIO34 | `homing_husillo_hall.ino` |

Estos seis pines quedan fijos tal como están; el resto de la placa se diseña alrededor de ellos.

## 2. Bus SPI propuesto — ADS1256 (ADC de la celda de carga / AMTI)

Aún no hay pines de SPI asignados en ningún `.ino`. Propuesta usando el bus VSPI por defecto del ESP32 (no choca con los pines de la sección 1):

| Señal ADS1256 | Pin ESP32 | Nota |
|---|---|---|
| SCK | GPIO18 | VSPI por defecto |
| MISO (DOUT) | GPIO19 | VSPI por defecto |
| MOSI (DIN) | GPIO23 | VSPI por defecto |
| CS (SYNC/CS) | GPIO5 | Pin de strapping del ESP32 — no debe quedar forzado a nivel bajo durante el arranque; usar resistencia pull-up externa de 10 kΩ si se observan resets raros |
| DRDY | GPIO4 | Entrada, idealmente con interrupción (`attachInterrupt`) para no hacer polling |
| RESET / PDWN | 3V3 (fijo) | La mayoría de módulos ADS1256 ya traen estos pines a nivel alto en la propia placa — verificar en el módulo Teyleten Robot comprado antes de cablear un GPIO extra para esto |

**Entradas analógicas del ADS1256 (8 canales / 4 pares diferenciales):**

- **AIN0/AIN1 (diferencial):** celda de carga (puente de Wheatstone) — *pendiente confirmar con el vendedor si la salida es realmente mV/V cruda; si resulta ser "Push-Pull" como advierte `Comparativa-LoadCells-S5.md`, este par no sirve tal cual y hay que revisar acondicionamiento antes de cablear.*
- **AIN2..AIN7:** libres por ahora. **La integración de los 6 canales de la AMTI con el ADS1256 queda despriorizada por decisión del 10/09** (no descartada) hasta cerrar la celda de carga del pylon y el VL53L1X. Cuando se retome, sigue habiendo el mismo problema de fondo ya identificado: con solo 4 pares diferenciales en el chip, 6 canales AMTI + 1 de la celda no caben todos en modo diferencial — faltará decidir single-ended (si la AMTI está referenciada a tierra común, según el modo MSA-6 Compatible vs. Fully Conditioned, aún sin confirmar) vs. un segundo ADC/mux.

## 3. Bus I2C compartido — IMU y sensor de ángulo

Todo lo que sea I2C comparte GPIO21 (SDA) / GPIO22 (SCL) ya fijados:

| Dispositivo | Dirección I2C típica | Estado |
|---|---|---|
| MPU6050 (actual) | 0x68 (AD0→GND) | En uso hoy |
| LSM6DSR (candidato reemplazo Nivel A) | 0x6A / 0x6B (según SDO) | Pendiente de decisión (`Comparativa-IMU-Bajo-Drift.md`) |
| ICM-45686 (candidato reemplazo Nivel A) | 0x68 / 0x69 (según AP_AD0) | Mismo pendiente — **si se elige este y se mantiene el MPU6050 en la placa a la vez, hay que fijar direcciones distintas (AD0/AP_AD0) para no chocar** |
| BNO055 (pruebas) | 0x28 (COM3→GND) / 0x29 (COM3→3V3) | Solo pruebas de banco por ahora — confirmar si queda en la placa final o si el proyecto se queda con un único IMU. **Si el módulo es el DFRobot SEN0374 (Fermion BNO055), ver nota 3.1 abajo** |
| AS5600 (ángulo, BOM sin cerrar) | 0x36 (fija, no configurable) | Sensor final de rotación aún sin elegir en firme (`Pendientes.md` S5, sección BOM) |

**Punto a vigilar (resuelto en la sección 4):** BNO055 (dirección 0x29 si se puentea) y VL53L1X (dirección de fábrica también 0x29) chocarían en el mismo bus si ambos quedan en 0x29 — la decisión del 10/09 es dejar el BNO055 en 0x28 (default) para evitar el choque sin tocar el XSHUT del VL53L1X.

### 3.1 Módulo DFRobot SEN0374 (Fermion BNO055) — según el esquemático subido

El esquemático que compartiste (`SEN0374_bno055intelligent9axissensor_schematics_v1.pdf`) confirma que **no es el chip BNO055 pelado**, sino un módulo con acondicionamiento propio, lo que simplifica bastante la placa del ESP32:

- **Regulador propio (U2, ME6206A30M3G):** el módulo acepta una alimentación VCC (típicamente 5 V) y la regula internamente a 3.3 V para el chip — no hace falta que la placa del ESP32 le entregue 3.3 V regulado aparte, con 5 V a su VCC alcanza.
- **Level-shifting de I2C integrado (Q1/Q2, 2N7002):** SDA/SCL salen del conector ya desplazados de nivel entre el dominio interno de 3.3 V del BNO055 y el VCC del conector — es decir, el módulo se puede conectar directo al bus I2C del ESP32 (3.3 V) sin resistencias de pull-up adicionales de tu parte; el módulo ya trae las suyas (R14–R17, 10 kΩ).
- **Pad I2C_ADDR seleccionable:** hay un puente/pad dedicado para elegir entre las dos direcciones I2C del BNO055 (0x28 por defecto / 0x29). Esto es justo lo que resuelve el conflicto con el VL53L1X mencionado arriba — si terminas usando este módulo junto con un VL53L1X, puedes dejar el BNO055 en 0x28 sin tocar el firmware de dirección del VL53L1X.
- **Pines de P2 (RST, BL_IND, PS2, PS1, nBOOT):** están para modo de programación/bootloader del propio módulo y ya tienen sus resistencias de pull-up/pull-down correctas en la placa (R2–R4, R9) para arrancar en modo normal — **no es necesario cablearlos al ESP32**, solo quedan expuestos por si algún día se necesita reprogramar el módulo directamente.
- **Conexión mínima real a la placa del ESP32:** VCC, GND, SDA→GPIO21, SCL→GPIO22, y opcionalmente INT si se quiere usar la interrupción de datos del BNO055 en vez de hacer polling (dejarlo en un GPIO libre, p. ej. GPIO33, si se decide usarlo).
- **Confirmado con la librería `DFRobot_BNO055` y el datasheet Bosch (rev 1.4) que subiste:** el chip solo expone I2C y UART a nivel de hardware (no SPI), y la librería de DFRobot solo implementa la clase I2C (`DFRobot_BNO055_IIC`, dirección por defecto `0x28`) — coherente con dejarlo en el mismo bus I2C de la sección 3 y no reservarle pines de SPI. Si se usa el pin INT con esta librería en el ESP32, el ejemplo `interrupt.ino` de DFRobot usa la sintaxis vieja de Arduino Uno (`attachInterrupt(0, ...)`); en ESP32 hay que cambiarla por `attachInterrupt(digitalPinToInterrupt(PIN), ...)` con el GPIO real.

## 4. Sensor de distancia — VL53L1X (decidido 10/09)

Cerrado: **VL53L1X** (I2C), no TF-Luna — coherente con el adaptador que ya se está diseñando en Fusion 360 (`Evidencias/diseno-adaptador-sensor-S5/`). Va en el bus I2C compartido de la sección 3, dirección de fábrica 0x29.

**Punto a resolver junto con esta decisión:** el BNO055 (sección 3.1) puede configurarse en esa misma dirección 0x29 (COM3→3V3) — para que no choquen, dejar el BNO055 en su dirección **por defecto 0x28** (pad I2C_ADDR del módulo sin puentear). Así no hace falta ni cablear el XSHUT del VL53L1X para este caso puntual; ese GPIO (sección 3, ej. GPIO32) queda como opción solo si más adelante se agrega un segundo dispositivo en 0x29.

El GPIO16/17 que se había reservado para TF-Luna (UART2) queda libre — ya no se necesita.

## 5. Alimentación y tierra

- Riel de 3.3 V para IMU, AS5600, y lógica del ADS1256 (según el módulo).
- Riel de 5 V (o el que pida el puente de la celda de carga como excitación — verificar en la ficha una vez confirmado el proveedor) para la excitación del puente de Wheatstone.
- Referencia de tierra común entre ESP32, ADS1256 y la celda de carga — al ser la parte más sensible a ruido de la placa (24 bits de resolución), conviene mantenerla separada de la tierra de potencia del driver del husillo (STEP/DIR/ENABLE) y unirlas en un solo punto (tierra en estrella) en vez de un plano compartido sin cuidado.

## 6. Resumen de pines libres usados en esta propuesta

GPIO4, 5, 18, 19, 23 (y 32 si más adelante se necesita XSHUT para un segundo dispositivo en 0x29, y 33 si se usa el INT del BNO055). Todos libres respecto a lo que ya usan los `.ino` actuales (21, 22, 25, 26, 27, 34). GPIO16/17 quedan libres — ya no se reservan para TF-Luna (descartado, ver sección 4).

---

## Pendiente antes de cerrar el diseño de la placa

- [ ] Confirmar con el vendedor el tipo de salida real de la celda de carga (mV/V vs. Push-Pull) — bloquea el cableado de AIN0/AIN1.
- [ ] Interfaz de los 6 canales de la AMTI con el ADS1256 — **despriorizada por decisión del 10/09**, retomar más adelante (single-ended vs. mux adicional sigue siendo la pregunta de fondo cuando se retome).
- [ ] Decidir el reemplazo de IMU (LSM6DSR vs. ICM-45686 vs. mantener MPU6050) y si el BNO055 queda o no en la placa final.
- [x] Sensor de distancia del BOM: **VL53L1X** (decidido 10/09) — bus I2C compartido, ver sección 4.

## Fuentes

- `Firmware/test_bno055/test_bno055.ino`, `Firmware/test_mpu6050/test_mpu6050.ino`, `Firmware/homing_absoluto/homing_absoluto.ino`, `Firmware/homing_husillo_hall/homing_husillo_hall.ino` — pines ya fijados en firmware.
- `Reportes-Semanales/S5/Comparativa-LoadCells-S5.md` — ADS1256 decidido, alerta de salida "Push-Pull" de la celda candidata #4.
- `Estado-del-arte/REFERENCIA DE POSICION ABSOLUTA/Comparativa-IMU-Bajo-Drift.md` — candidatos de reemplazo de IMU.
- `Reportes-Semanales/S4/Pendientes.md`, `Reportes-Semanales/S5/Pendientes.md` — pendientes heredados de interfaz AMTI/ADS1256 y BOM de sensores.
- `SEN0374_bno055intelligent9axissensor_schematics_v1.pdf` (DFRobot, esquemático del módulo Fermion BNO055) — confirma regulador y level-shifting integrados, y el pad de selección de dirección I2C.
- `SEN0374_bno055intelligent9axissensor_datasheet_v1.pdf` (Bosch, datasheet BNO055 rev 1.4) — confirma interfaces I2C/UART (sin SPI) y rangos de VDD/VDDIO.
- `SEN0374_bno055intelligent9axissensor_library_v1.zip` (librería Arduino `DFRobot_BNO055`) — confirma que solo implementa I2C (dirección `0x28` por defecto) y el patrón de uso de la interrupción.
