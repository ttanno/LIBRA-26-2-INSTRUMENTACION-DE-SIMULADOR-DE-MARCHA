# Test IMU BNO055 (ESP32)

Sketch mínimo para verificar que el BNO055 comunica por I2C y entrega datos coherentes, antes de decidir si se integra al simulador (ver comparativa de IMU en `Estado-del-arte/`).

## 1. Conexionado

| BNO055 | ESP32 |
|---|---|
| VIN | 3V3 |
| GND | GND |
| SDA | GPIO21 |
| SCL | GPIO22 |
| ADR | GND (dirección 0x28, la que usa el sketch por defecto) |
| RST | sin conectar |

Si el módulo específico trae otros pines de I2C por defecto, ajustar `Wire.begin(21, 22)` en el sketch.

## 2. Software (Arduino IDE)

1. Instalar el core de ESP32 en el Arduino IDE (Preferencias → URLs de gestor de tarjetas adicionales) si aún no está.
2. Administrador de bibliotecas → instalar **Adafruit BNO055** y **Adafruit Unified Sensor** (esta última es dependencia de la primera).
3. Abrir `test_bno055.ino`, seleccionar la placa ESP32 correspondiente y el puerto COM.
4. Cargar el sketch y abrir el Monitor Serie a **115200 baudios**.

## 3. Qué esperar

- Al iniciar: `BNO055 detectado correctamente.` Si en cambio aparece el mensaje de error, revisar alimentación, cableado SDA/SCL y dirección I2C (multímetro o un sketch de escaneo I2C si hace falta).
- Cada 200 ms se imprime una línea con:
  - **Calib[sys,gyro,accel,mag]**: cada valor va de 0 (sin calibrar) a 3 (calibración completa). El BNO055 calibra solo con movimiento:
    - Giroscopio: dejarlo quieto unos segundos.
    - Acelerómetro: orientarlo en distintas posiciones (ejes X/Y/Z arriba/abajo) y mantener cada una un momento.
    - Magnetómetro: moverlo describiendo figuras en 8 en el aire.
    - Sistema: sube a 3 cuando los tres anteriores están calibrados.
  - **Euler[heading,roll,pitch]**: orientación en grados.
  - **LinAccel[x,y,z]**: aceleración lineal en m/s² (gravedad ya restada).
  - **Temp**: temperatura del chip en °C (sirve como indicador rápido de que el sensor responde, no es una medición de precisión).

## 4. Siguiente paso

Con `sys=3` estable, mover el sensor a mano replicando aproximadamente los ejes de interés (flexo-extensión) y verificar que el ángulo reportado tiene sentido físico y no hay saltos/ruido excesivo. Si el comportamiento es consistente, este mismo patrón de lectura (`getEvent` + `getCalibration`) es la base para el firmware de adquisición sincronizada mencionado en el README.

## 5. Sobremuestreo (oversampling) — `test_bno055_oversampling/test_bno055_oversampling.ino`

**Nota:** este sketch vive en su propia carpeta `Firmware/test_bno055_oversampling/` (no dentro de `test_bno055/`) porque Arduino IDE compila juntos todos los `.ino` de una misma carpeta como un solo sketch -- tenerlos separados evita choques de `bno`, `setup()`, `loop()` duplicados.

Este segundo sketch promedia N lecturas crudas del BNO055 antes de reportar cada dato, para reducir el ruido aleatorio de la señal sin agregar hardware (mismo principio estadístico que promediar varios IMUs físicos, pero solo ataca ruido aleatorio — no corrige bias/drift sistemático, para eso hace falta calibración).

- Los ángulos se promedian como vector (seno/coseno) y no como número directo, porque el heading da la vuelta en 0/360 y un promedio ingenuo daría resultados incorrectos cerca de ese punto.
- Configurable en el código: `N_SAMPLES` (muestras por bloque) y `SAMPLE_INTERVAL_MS` (separación entre muestras crudas). La tasa de salida resultante es `1000 / (N_SAMPLES * SAMPLE_INTERVAL_MS)` Hz — con los valores por defecto (10 y 10 ms) da 10 Hz. Si necesitas mantener el ≥100 Hz de salida del requerimiento técnico del README, baja `N_SAMPLES`.
- Salida por Serial en formato CSV: `raw_heading,raw_roll,raw_pitch,avg_heading,avg_roll,avg_pitch,n,sys,gyro,accel,mag` (raw = primera muestra cruda del bloque, avg = promedio del bloque), lista para pegar en un `.csv` y analizar.

**Cómo comprobar que realmente reduce el ruido:** con el sensor quieto sobre una superficie estable, registra ~30 s con `test_bno055.ino` (dato crudo) y ~30 s con este sketch (dato promediado), calcula la desviación estándar de cada columna en Excel/Python, y compara — la del promedio debería salir menor, idealmente cerca de `std_crudo / sqrt(N_SAMPLES)`.
