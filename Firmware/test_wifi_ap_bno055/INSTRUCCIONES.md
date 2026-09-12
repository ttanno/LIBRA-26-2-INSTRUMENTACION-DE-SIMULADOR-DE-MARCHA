# Test WiFi con red propia del ESP32 (modo Access Point) — BNO055 DFRobot

Versión de `test_wifi_udp_bno055.ino` que **no depende de ninguna red WiFi existente**. En vez de que el ESP32 se una a tu WiFi de casa o de la universidad, aquí el ESP32 crea su propia red (modo Access Point / AP) y tu laptop se conecta directo a esa red — sin router de por medio, sin login enterprise de la universidad, sin depender de que haya WiFi disponible donde estés probando el simulador.

Útil especialmente porque el WiFi de la universidad (PUCP-Alumnos, eduroam) normalmente pide usuario + contraseña (WPA2-Enterprise) y **no** funciona con el código simple de `WiFi.begin(ssid, password)` que usan las otras dos carpetas de WiFi — esta variante evita el problema por completo.

## 1. Conexionado

Igual que siempre: BNO055 → ESP32, VCC-3V3, GND-GND, SDA-GPIO21, SCL-GPIO22.

## 2. Configurar el sketch (opcional)

Por defecto ya funciona sin tocar nada:

```cpp
const char* AP_SSID     = "LIBRA_ESP32";
const char* AP_PASSWORD = "libra2026";
```

Puedes cambiar el nombre/contraseña de la red si quieres — el password debe tener **mínimo 8 caracteres**, si no el ESP32 crea la red sin contraseña (abierta). A diferencia de las otras dos carpetas de WiFi, **aquí no hay ninguna IP que configurar a mano** — todo es automático (ver la sección "Cómo funciona" abajo si quieres entender por qué).

## 3. Software (Arduino IDE)

Misma librería que `test_wifi_udp_bno055.ino`: **DFRobot_BNO055**. Carga el sketch y abre el Monitor Serie a 115200 — debería mostrar algo como:

```
Red WiFi propia creada: "LIBRA_ESP32"
IP del ESP32 (siempre es esta en modo AP): 192.168.4.1
BNO055 detectado correctamente.
```

## 4. Conectar tu laptop a la red del ESP32

En el panel de WiFi de Windows, busca y conéctate a **"LIBRA_ESP32"** (o el nombre que hayas puesto) con la contraseña configurada — exactamente como te conectas a cualquier otra red.

**Mientras estés conectado a esta red, tu laptop probablemente pierda acceso a internet** — es normal, el ESP32 no reenvía tráfico a internet, solo sirve como canal directo entre él y tu laptop. Si necesitas internet a la vez (para buscar algo, etc.), tendrás que desconectarte de esta red momentáneamente o usar otro dispositivo.

## 5. Visor en tiempo real (Python)

```
cd visor_python
pip install -r requirements.txt
python visor_wifi_ap_bno055.py
```

A diferencia de `visor_wifi_bno055.py`, este **no imprime ninguna IP para copiar a ningún lado** — el ESP32 siempre es `192.168.4.1` en este modo, así que ya viene fijo en el script. En cuanto tu laptop esté conectada a la red del ESP32 (paso 4), el gráfico debería empezar a moverse solo.

Los botones son los mismos de siempre ("Zero grafico local", "Cero absoluto (flash)", "Borrar cero (flash)") — la diferencia es que aquí ya saben de entrada a qué IP mandar los comandos, no necesitan aprenderla de un primer paquete.

## 6. Cómo funciona la direcciones IP en este modo (por si te preguntas por qué no hay que configurar nada)

- El ESP32 en modo Access Point **siempre** es `192.168.4.1` — es el valor por defecto de la librería WiFi de Espressif, no depende de tu red.
- Tu laptop, al conectarse, recibe automáticamente una IP en el mismo rango (típicamente `192.168.4.2`) que el propio ESP32 le asigna — no necesitas verla ni escribirla en ningún lado.
- El ESP32 manda los datos por **broadcast** a `192.168.4.255` en vez de a una IP fija de PC — le llega a cualquier laptop conectada a su red, así que no hace falta el paso de "averigua tu IP y cópiala en el sketch" que sí tenían las otras dos versiones.

## 7. Cuándo conviene esta versión vs. las otras dos

- **Esta (AP propio):** ideal para pruebas de banco/laboratorio sin depender de infraestructura de red, o cuando la única red disponible es la de la universidad (enterprise). Límite: el alcance es el del propio WiFi del ESP32 (más corto que un router de verdad), y solo funciona mientras tu laptop esté conectada a ESA red (no a la de siempre).
- **`test_wifi_udp_bno055` (se une a una red existente):** mejor si ya tienes un WiFi doméstico o un hotspot de celular confiable en el lugar de la prueba, y quieres que tu laptop mantenga acceso a internet a la vez.

Las dos comparten la misma limitación de fondo: UDP sin confirmación de entrega — ver la sección correspondiente en `test_wifi_udp_bno055/INSTRUCCIONES.md` si no la has leído.
