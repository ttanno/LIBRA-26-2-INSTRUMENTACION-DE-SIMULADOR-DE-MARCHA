# T-INT2 — Adquisición simultánea de todos los sensores (ESP32)

Sketch y script para la prueba **T-INT2** (`Reportes-Semanales/S12/Resumen-Semana12.md`, secc. 2.3): la celda (HX711), los dos ToF (VL53L1X) y el IMU (BNO055) leyendo a la vez en la galleta durante 5 min. Se obtienen la frecuencia real de cada sensor, las muestras perdidas y los errores o conflictos en los buses.

## 1. Conexionado

Es el mismo de la galleta 70×90 y de la PCB final (`../PCB_placa_superior_PINOUT.md`, Registro C-29). No hay que cambiar nada.

| Sensor | Bus / pines | Dirección |
|---|---|---|
| HX711 (celda) | DT = GPIO32, SCK = GPIO33 | — |
| ToF1 (U3) | `Wire` SDA 21 / SCL 22, SHUT = GPIO25 | 0x30 (reasignada) |
| ToF2 (U2) | `Wire` SDA 21 / SCL 22, SHUT = GPIO26 | 0x29 |
| BNO055 | `Wire1` SDA 17 / SCL 16 | 0x28 |

## 2. Qué cambia respecto a los sketches individuales

En `test_hx711.ino` y `test_tof.ino` la lectura espera a que el sensor tenga el dato (`wait_ready_timeout()`, `read()` bloqueante). Con tres sensores en el mismo loop, cada uno frenaría a los demás y la frecuencia medida sería la del loop. Aquí cada sensor se lee **solo cuando ya tiene un dato listo**:

- HX711: `is_ready()`, que es una lectura del pin DT y no ocupa el bus.
- ToF: `dataReady()` cada 5 ms y luego `read(false)`.
- BNO055: cada 100 ms con base de tiempo fija, igual que `test_wifi_ap_bno055.ino`.

Cada muestra lleva la marca de tiempo del ESP32 (`micros()`) y un contador global de líneas. Con eso el análisis separa dos casos: una muestra que el sensor no entregó (hueco en el tiempo) y una línea que se perdió en el Serial (salto del contador).

Esta prueba no usa WiFi y el roll sale crudo, sin EMA, cero ni `corregirRoll()`: se evalúa la adquisición, no el ángulo.

## 3. Software

1. Librerías (Arduino IDE > Administrar bibliotecas), las mismas de los otros sketches: **HX711** (Bogdan Necula), **VL53L1X** (Pololu) y **DFRobot_BNO055**.
2. Cargar `test_integracion_sensores.ino`. El core de ESP32 debe ser 2.x o superior, por `Serial.setTxBufferSize()`.
3. En el PC: `pip install -r visor_python/requirements.txt`

## 4. Procedimiento

1. **Antes de la tanda:** hacer commit del firmware y anotar la configuración en el Registro de Trazabilidad.
2. Plataforma quieta. La celda queda sin carga o con una carga fija, y los ToF apuntando a su objetivo en el montaje final.
3. Cerrar el Monitor Serie del IDE y correr:

   ```
   cd visor_python
   python log_integracion.py --port COM7
   ```

   El script espera el reporte inicial del ESP32 y lo muestra: escaneo de `Wire` y `Wire1` con OK/FALTA y estado de cada sensor. Después descarta 10 s de asentamiento, reinicia los contadores (`r`) y registra 300 s.

   Opciones: `--duracion 60` para una prueba corta, `--descartar 10`, `--carpeta ../../../Evidencias/integracion-sensores-S13`.
4. Si el escaneo marca **FALTA** o algún sensor sale **FALLA** en `# INIT`, conviene cortar y revisar ese conector (T-INT1) antes de seguir.
5. Para volver a analizar un registro: `python log_integracion.py --analizar int2_<fecha>_raw.log`

## 5. Resultados

| Archivo | Contenido |
|---|---|
| `int2_<fecha>_raw.log` | Todo lo que llegó por el Serial, con la hora del PC |
| `_hx711.csv`, `_tof.csv`, `_imu.csv` | Datos por sensor (t_s en el reloj del ESP32) |
| `_estado.csv` | Contadores acumulados por segundo (muestras, errores, loop máximo, bloqueos del Serial) |
| `_errores.csv` | Líneas `E` (sensor, motivo, detalle) |
| `_resumen.md` | Tabla de criterios, frecuencias, huecos y errores |
| `_intervalos.png` | Δt entre muestras de cada sensor y duración de cada lectura del BNO055 |

### Criterios propuestos

La tabla de T-INT2 no fija criterios. Estos se proponen y se pueden ajustar al inicio del script:

| Criterio | Valor |
|---|---|
| Líneas perdidas o malformadas en el Serial | 0 |
| Bloqueos del buffer del Serial | 0 |
| Frecuencia real del IMU | ±5 % de la nominal (10 Hz) |
| Frecuencia de la celda | Informativa: con el oscilador interno del HX711 sale ~11.5 Hz (P-18), no 10 Hz |
| Frecuencia de los ToF | Informativa: periodo de 100 ms (10 Hz, decisión del 2026-11-10), pero el oscilador interno del VL53L1X corre ~8 % rápido y sale ~10.8 Hz |
| Muestras perdidas por sensor | ≤ 0.1 % |
| Errores por sensor (I2C, sin datos > 500 ms, lectura fallida) | 0 |
| IMU con valores idénticos ≥ 10 s | REVISAR: un IMU muy quieto puede repetir valores; mover levemente la plataforma y ver si responde |
| Celda congelada o saturada | No |

### Cómo leer los resultados

- **«Generadas (ESP32)» > «Muestras»:** se perdieron líneas en el enlace Serial, no en el sensor.
- **Huecos en un solo sensor:** es un problema de ese sensor o de su conector.
- **Huecos en todos a la vez:** algo frenó el loop. Mirar la duración máxima del loop y `serialBloq`.
- **Duración de la lectura del BNO055 con picos de varios ms:** `Wire1` se está trabando (clock stretching del BNO055).
- **Errores `i2c` en un ToF:** revisar el conector J4/J5 y el pull-up del bus `Wire`.

## 6. Comandos por Serial

- `i`: vuelve a imprimir el reporte inicial con el escaneo I2C hecho al arrancar. No vuelve a escanear: las transacciones vacías del escaneo sacan al BNO055 del modo de fusión y desde ahí `getEul()` devuelve 0.00 (verificado el 2026-11-10). Por eso el escaneo se hace una sola vez en `setup()`, antes de iniciar el BNO055.
- `r`: reinicia los contadores. El script lo envía solo al empezar a registrar.
