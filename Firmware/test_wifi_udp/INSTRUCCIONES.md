# Test envío de datos por WiFi (UDP), sin cable (ESP32)

Es el mismo MPU6050 y la misma lógica de `test_mpu6050.ino` (filtro complementario propio para roll/pitch, más `yaw_solo_giro` para ver el drift) — lo único que cambia es el transporte: en vez de mandar el CSV por el cable USB (Serial), el ESP32 lo manda por WiFi como paquetes UDP directo a la IP de la PC. Es la forma más simple de sacar el cable de en medio: no requiere instalar ningún servidor/broker, solo que el ESP32 y la PC estén en la misma red WiFi (no hace falta internet real, basta la red local del laboratorio o del celular en hotspot).

## 1. Conexionado

Igual que `test_mpu6050.ino` — ver esa carpeta. El ESP32 sigue necesitando alimentación (USB o una fuente de 5V aparte); lo que ya no necesita es que el cable USB esté conectado a la PC del visor mientras mide.

## 2. Configurar el sketch antes de cargar

Editar estas 3 líneas al inicio de `test_wifi_udp.ino`:

```cpp
const char* WIFI_SSID     = "TU_RED_WIFI";
const char* WIFI_PASSWORD = "TU_PASSWORD";
const char* PC_IP         = "192.168.1.100";
```

`PC_IP` es la IP local de la laptop que va a correr el visor **en esa misma red WiFi** — el propio `visor_wifi_udp.py` la imprime apenas lo corres (sección 4), para copiarla aquí. Si cambias de red (de casa al laboratorio, por ejemplo) hay que volver a cargar el sketch con la IP nueva, porque las IPs locales suelen cambiar de red a red.

## 3. Software (Arduino IDE)

1. Mismas librerías que `test_mpu6050.ino`: **Adafruit MPU6050**, **Adafruit Unified Sensor**, **Adafruit BusIO**.
2. `WiFi.h` y `WiFiUdp.h` ya vienen incluidas en el core de ESP32 — no hay que instalar nada aparte, solo tener seleccionada una placa ESP32 en Herramientas > Placa.
3. Cargar y abrir el Monitor Serie a 115200 baudios — sigue imprimiendo el mismo CSV por Serial además de mandarlo por WiFi, útil para confirmar que el sensor funciona aunque el visor de WiFi todavía no reciba nada.

## 4. Visor en tiempo real (Python)

```
cd visor_python
pip install -r requirements.txt
python visor_wifi_udp.py
```

Al arrancar, imprime la IP local de tu PC — cópiala en `PC_IP` del sketch (paso 2) antes de cargarlo, si todavía no lo hiciste. Por defecto escucha en el puerto UDP 4210 (igual que `UDP_PORT` en el `.ino`); si lo cambias en uno, cámbialo en el otro.

El gráfico es idéntico al de `visor_mpu6050.py` (roll/pitch/yaw arriba, aceleración cruda al medio, giro crudo abajo) — el botón "Zero / Reset" sigue siendo solo un offset visual, no reinicia el drift real que se sigue acumulando dentro del ESP32.

## 5. Qué esperar / cómo depurar si no llega nada

- Si el Monitor Serie muestra el CSV pero el visor de Python no dibuja nada: lo más probable es la IP (verifica que `PC_IP` en el sketch sea exactamente la que imprimió el visor) o el **firewall de Windows** bloqueando el puerto UDP 4210 entrante — la primera vez que corres `visor_wifi_udp.py` puede aparecer un aviso de firewall, hay que permitir el acceso.
- Confirma que el ESP32 y la laptop estén en la **misma red** (mismo WiFi, no uno en WiFi y otro compartiendo datos móviles, y ojo con routers que aíslan clientes entre sí — "AP/client isolation" — algunos WiFi de universidades o de celulares en hotspot lo activan por defecto).
- Si el WiFi se cae a medias, el sketch reintenta conectarse solo (ver `loop()`), pero es bloqueante mientras reconecta — los datos de esos segundos se pierden, no se guardan en cola.

## 6. Limitación de UDP (léelo antes de confiar en esto para el registro final)

UDP no confirma entrega ni garantiza orden: si un paquete se pierde por interferencia de WiFi, simplemente no llega — no hay reintento automático ni error visible. Para *ver* los datos en vivo en el banco de pruebas esto es aceptable (mismo riesgo que ya existe con Serial si se satura el buffer), pero **no es la base para el registro/almacenamiento sincronizado que pide el objetivo de Software del proyecto** (`README.md`). Si más adelante hace falta:

- Confirmación de entrega o mandar comandos de vuelta al ESP32 → considerar TCP o WebSocket.
- Varios ESP32/sensores publicando a la vez de forma ordenada, con reconexión automática robusta → considerar **MQTT** (broker tipo Mosquitto corriendo en la misma PC o en un Raspberry Pi del laboratorio, librería `PubSubClient` en el ESP32, `paho-mqtt` en Python) — el payload CSV que ya usas no cambiaría, solo el transporte.

Este sketch es un punto de partida para probar el concepto de "sensor sin cable", no el diseño final de adquisición sincronizada multi-sensor.
