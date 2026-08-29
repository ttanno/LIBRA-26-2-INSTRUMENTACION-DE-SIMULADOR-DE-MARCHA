# Test IMU MPU6050 (ESP32)

Sketch de prueba para el MPU6050/GY-521 que ya tienen en inventario (ver `Reportes-Semanales/S3/Resumen-Semana3.md`, tabla de IMU). A diferencia del BNO055, este sketch SÍ programa el filtro de fusión (complementario) por software, porque el MPU6050 no lo trae integrado.

## 1. Conexionado

| MPU6050 / GY-521 | ESP32 |
|---|---|
| VCC | 3V3 (la mayoría de módulos GY-521 traen regulador a bordo, revisa el tuyo si acepta 3.3V directo) |
| GND | GND |
| SDA | GPIO21 |
| SCL | GPIO22 |
| AD0 | GND (dirección 0x68, la que usa el sketch) o 3V3 (0x69) |
| INT | sin conectar (no se usa) |

## 2. Software (Arduino IDE)

1. Administrador de bibliotecas → instalar **Adafruit MPU6050**, **Adafruit Unified Sensor** y **Adafruit BusIO** (dependencias entre sí).
2. Abrir `test_mpu6050.ino` como sketch independiente (está en su propia carpeta, igual que hicimos con `test_bno055_oversampling`).
3. Cargar y abrir el Monitor Serie a **115200 baudios**.

## 3. Qué esperar

- Al iniciar, el sketch pide mantener el sensor quieto ~2 segundos mientras calibra el offset del giroscopio (bias) — esto es necesario porque, a diferencia del BNO055, el MPU6050 no se autocalibra.
- Salida CSV: `raw_ax,raw_ay,raw_az,raw_gx,raw_gy,raw_gz,roll,pitch,yaw_solo_giro,temp_C`
  - `raw_a*`: aceleración cruda en m/s² (con gravedad incluida, no es aceleración lineal).
  - `raw_g*`: velocidad angular en rad/s, ya con el offset de calibración restado.
  - `roll,pitch`: ángulos del **filtro complementario** (acelerómetro + giroscopio) — esto reemplaza la fusión que el BNO055 hacía solo.
  - `yaw_solo_giro`: **a propósito sin corregir** — es la integración pura del giro en Z. Sirve para que veas en vivo el drift del que hablamos: con el sensor quieto, este valor se va a ir alejando de 0 poco a poco. No lo uses como dato válido, es solo demostrativo.
  - `temp_C`: temperatura del chip.

## 4. Limitaciones frente al BNO055 (recordatorio)

- **Sin magnetómetro**: no hay forma de obtener un heading/yaw absoluto — por eso `yaw_solo_giro` deriva sin límite.
- **Sin fusión integrada**: el roll/pitch que ves aquí depende del filtro complementario que programamos, no de un chip dedicado como en el BNO055.
- El peso del filtro (`GYRO_WEIGHT`, por defecto 0.98) controla el balance entre respuesta rápida (más giro) y estabilidad (más acelerómetro) — pueden ajustarlo si ven roll/pitch muy ruidoso o muy lento para seguir el movimiento real.

## 5. Siguiente paso

Como el MPU6050 tiene rol de validación cruzada (no medición primaria — ese es el AS5600), lo más útil es comparar su `roll`/`pitch` contra el ángulo del AS5600 en el mismo movimiento, y ver si detecta holgura/desalineamiento del pivote como se planteó en la arquitectura de sensores de la S2.

## 6. Visor en tiempo real (Python)

Igual que con el BNO055, hay un visor gráfico en `visor_python/visor_mpu6050.py` que lee el puerto serial y grafica roll/pitch/yaw en vivo, más los datos crudos de acelerómetro y giroscopio.

```
cd visor_python
pip install -r requirements.txt
python visor_mpu6050.py --port COM5
```

Detalles a tener en cuenta:

- El panel superior muestra `roll`/`pitch` (ya filtrados) y, en rojo punteado, `yaw (solo giro, DERIVA)` — está ahí a propósito para que veas el drift en vivo: con el sensor quieto, esa línea se va a ir alejando de 0 con el tiempo, mientras roll/pitch se mantienen estables gracias a la corrección del acelerómetro.
- El botón "Zero / Reset (solo vista)" solo aplica un offset visual en el gráfico — **no reinicia el drift real** que sigue acumulándose dentro del ESP32 (a diferencia del visor del BNO055, aquí es importante dejarlo claro porque el yaw sin corregir seguiría creciendo aunque resetees la vista).
- Si quieres comparar directamente contra el visor del BNO055 (`Firmware/test_bno055/visor_python/visor_imu.py`), puedes correr ambos sketches en dos ESP32/puertos distintos y abrir las dos ventanas en paralelo.
