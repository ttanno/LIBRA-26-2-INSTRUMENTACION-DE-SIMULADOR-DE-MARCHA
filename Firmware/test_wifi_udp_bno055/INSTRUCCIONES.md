# Test envío de datos por WiFi (UDP) — BNO055 DFRobot (ESP32)

Versión para BNO055 de `Firmware/test_wifi_udp/` (esa carpeta usa el MPU6050 con la librería Adafruit). Esta usa la librería **`DFRobot_BNO055`** — la del módulo Fermion (SEN0374) que estás usando, no `Adafruit_BNO055` como `test_bno055.ino` — y mantiene el mismo cero absoluto persistente en flash que ya tenías (comandos `z`/`c`), ahora también disponible por WiFi.

## 1. Conexionado

Idéntico a `test_bno055.ino` (ver esa carpeta): I2C, `BNO055 VCC→3V3, GND→GND, SDA→GPIO21, SCL→GPIO22`, dirección por defecto `0x28` (pad I2C_ADDR del módulo sin puentear).

## 2. Configurar el sketch antes de cargar

Editar al inicio de `test_wifi_udp_bno055.ino`:

```cpp
const char* WIFI_SSID     = "TU_RED_WIFI";
const char* WIFI_PASSWORD = "TU_PASSWORD";
const char* PC_IP         = "192.168.1.100";
```

`PC_IP` es la IP local de la laptop que corre el visor — `visor_wifi_bno055.py` la imprime al arrancar (sección 4). Usa el puerto UDP **4211** (distinto del ejemplo del MPU6050, que usa 4210) por si algún día corres los dos sketches de WiFi a la vez sin que se pisen.

## 3. Software (Arduino IDE)

1. Instalar la librería **DFRobot_BNO055**: Sketch > Include Library > Add .ZIP Library... y seleccionar el `SEN0374_bno055intelligent9axissensor_library_v1.zip` que ya tienes (o copiar la carpeta `DFRobot_BNO055-master` a tu carpeta `Arduino/libraries/`, renombrada a `DFRobot_BNO055`).
2. `WiFi.h`/`WiFiUdp.h` ya vienen en el core de ESP32 — no instalar nada aparte.
3. Cargar y abrir el Monitor Serie a 115200 baudios — sigue imprimiendo el mismo texto por Serial como respaldo, útil para confirmar que el sensor responde aunque el visor de WiFi no reciba nada todavía.

## 4. Visor en tiempo real (Python)

```
cd visor_python
pip install -r requirements.txt
python visor_wifi_bno055.py
```

Al arrancar imprime tu IP local — cópiala en `PC_IP` (paso 2) antes de cargar el sketch. El gráfico es igual al de `visor_imu.py` (heading/roll/pitch arriba, aceleración lineal en m/s² abajo, estado de calibración en el título) y tiene los mismos 3 botones:

- **"Zero grafico (local)"**: offset solo visual en este script, no toca el ESP32.
- **"Cero absoluto (flash)"**: manda el comando `z` — pero ahora **por WiFi** en vez de por el cable. El visor recién puede mandarlo después de recibir al menos un paquete del ESP32 (así descubre su IP solo, sin que la configures a mano).
- **"Borrar cero (flash)"**: manda `c` por WiFi, igual que el anterior.

## 5. Diferencias de unidades frente a `test_bno055.ino` (Adafruit) — importante si comparas datos

- La librería DFRobot da la aceleración lineal en **mg** (miligravedad); el sketch la convierte a **m/s²** (factor 9.80665/1000) para que sea comparable directo con `test_bno055.ino` y `test_mpu6050.ino`.
- `getEul()` ya da heading/roll/pitch en grados, igual que Adafruit.
- Esta librería **no expone un método público de temperatura** (a diferencia de `Adafruit_BNO055::getTemp()`), así que este sketch no reporta temperatura — es la única diferencia real de contenido frente a `test_bno055.ino`.

## 6. Qué esperar / cómo depurar si no llega nada

Mismos puntos que `test_wifi_udp/INSTRUCCIONES.md` (MPU6050): revisar que `PC_IP` sea exactamente la que imprimió el visor, revisar el firewall de Windows la primera vez que corres el script (puede pedir permiso para el puerto UDP), y confirmar que ESP32 y laptop estén en la misma red WiFi (sin aislamiento de clientes entre sí).

## 7. Limitación de UDP (léelo antes de usar esto como registro final)

Igual que con el MPU6050: UDP no confirma entrega ni garantiza orden — un paquete perdido por interferencia simplemente no llega, sin aviso. Sirve para *ver* los datos en vivo y probar el cero absoluto por WiFi, pero **no es la base para el registro/almacenamiento sincronizado multi-sensor** que pide el objetivo de Software del proyecto (`README.md`). El siguiente paso natural si hace falta más robustez (varios sensores/ESP32 a la vez, reconexión automática, confirmación de entrega) es MQTT — el payload de texto que ya usas no cambiaría, solo el transporte.
