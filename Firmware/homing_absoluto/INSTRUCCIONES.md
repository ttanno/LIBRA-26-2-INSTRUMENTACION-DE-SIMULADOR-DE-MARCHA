# Homing / cero absoluto persistente (MPU6050)

Prototipo para probar la idea de usar el acelerómetro (referencia de gravedad) para establecer un **cero absoluto del pivote de flexo-extensión**, y que ese cero sobreviva a apagar/encender el sistema (se guarda en la memoria flash del ESP32, no en RAM).

## Conexionado

Igual que `test_mpu6050.ino`: VCC→3V3, GND→GND, SDA→GPIO21, SCL→GPIO22, AD0→GND (dirección 0x68).

## Librerías

Adafruit MPU6050, Adafruit Unified Sensor, Adafruit BusIO. `Preferences.h` (usada para guardar el cero en flash) ya viene incluida en el core de ESP32, no hay que instalar nada extra.

## Cómo probarlo

1. Cargar el sketch, abrir el Monitor Serie a 115200 baudios.
2. Poner el pivote/pylon en la posición física que quieres que sea "cero grados" (por ejemplo, perfectamente vertical) y mantenerlo quieto.
3. Escribir **`z`** y Enter en el Monitor Serie — el sketch promedia ~1 s de lecturas del acelerómetro y guarda ese ángulo como el cero absoluto en flash.
4. Mueve el pivote: la columna `roll_abs`/`pitch_abs` ahora reporta el ángulo **relativo a esa posición de referencia**, no un valor arbitrario.
5. **Apaga y vuelve a encender el ESP32** (o presiona reset): al arrancar, el mensaje debería decir "Cero absoluto cargado de la memoria flash..." con los mismos valores — confirma que el cero sobrevive al reinicio, que es el problema que estábamos resolviendo.
6. Escribir **`c`** y Enter para borrar el cero guardado y volver a "sin calibrar".

## Qué SÍ resuelve y qué NO

- **Sí resuelve:** referencia de posición absoluta para el eje de rotación (flexo-extensión), siempre que el "cero mecánico" corresponda a una orientación reconocible respecto a la gravedad, y que se pueda hacer un homing quieto al inicio de cada sesión de ensayo.
- **No resuelve:** el eje de traslación (husillo/riel) — ese sigue necesitando un encoder absoluto o un switch de home físico, como quedó anotado en `Reportes-Semanales/S3/Pendientes.md`.
- Es una rutina de homing puntual (al iniciar sesión), no una medición continua — durante el movimiento real el acelerómetro mezcla gravedad con aceleración dinámica y no sirve para esto.

## Portar esto al BNO055

La parte de guardar/cargar el cero en flash (`establecerZeroActual`, `guardarZeroEnFlash`, `cargarZeroDesdeFlash`) es igual para cualquier sensor — solo cambiarías de dónde sale `roll`/`pitch` (en el BNO055 vendría directo de `VECTOR_EULER` en vez del filtro complementario). Puedo armar esa versión si les resulta mejor opción que el MPU6050 para esto.

## Visor + control en Python

`visor_python/visor_homing.py` no es solo un visor — tiene dos botones que mandan de verdad los comandos `z`/`c` por Serial, así no necesitas escribirlos a mano en el Monitor Serie de Arduino:

```
cd visor_python
pip install -r requirements.txt
python visor_homing.py --port COM5
```

- **"Establecer cero (z)"**: manda `z` al ESP32 — mantén el pivote quieto en la posición de referencia antes de presionarlo, porque el ESP32 va a promediar ~1 s de lecturas del acelerómetro justo después.
- **"Borrar cero (c)"**: manda `c`, borra el cero guardado en flash.
- Panel superior: `roll_abs`/`pitch_abs` (relativos al cero guardado — esto es lo que te interesa para el ensayo).
- Panel inferior: `roll`/`pitch` crudos del filtro, sin restar el cero, para comparar.
- El título de la ventana indica si ya hay un cero absoluto guardado en flash o no.

Los mensajes de arranque/calibración/homing del ESP32 (que no son líneas CSV) se imprimen en la consola donde corres el script, no en el gráfico.
