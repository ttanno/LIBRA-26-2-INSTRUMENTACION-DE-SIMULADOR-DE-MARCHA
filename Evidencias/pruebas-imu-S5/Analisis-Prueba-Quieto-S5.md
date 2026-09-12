# Análisis — prueba "sensor quieto" BNO055 (10/09/2026)

Dos grabaciones hechas con `log_csv_bno055.py` (COM7, `test_wifi_ap_bno055.ino`), sensor inmóvil en una posición que visualmente se ve como 0°. Datos crudos en esta misma carpeta: `bno055_20260910_161442.csv` y `bno055_20260910_162052.csv`.

## Prueba 1 (16:14:42, ~28.7 s, 251 filas)

| variable | promedio | desv. estándar | mín | máx |
|---|---|---|---|---|
| heading | 338.46° | 82.41°* | 0.00° | 359.94° |
| roll | -1.36° | 0.31° | -2.19° | 0.06° |
| pitch | 1.59° | 1.84° | -2.00° | 6.00° |
| ax | -0.09 | 0.05 | -0.32 | 0.08 |
| ay | -0.02 | 0.31 | -0.66 | 0.75 |
| az | -0.24 | 0.01 | -0.28 | -0.20 |

*El std de heading no es real: la lectura cruza el límite 0°/360° (llega a 359.94° y también a 0.00°), y el promedio/desviación estándar calculados de forma lineal sobre un ángulo circular no tienen sentido en ese caso. Para heading hace falta estadística circular (o "desenrollar" el ángulo) antes de sacar conclusiones.

**Calibración durante toda la prueba: `sys=0, gyro=0, accel=0, mag=0`.** El BNO055 nunca reportó estar calibrado — ni siquiera el giroscopio, que normalmente sube a 3/3 en pocos segundos con el sensor quieto. Esto es sospechoso por dos motivos: o el sensor de verdad no está calibrado (lo cual invalida cualquier conclusión de ruido, porque un heading/pitch sin calibrar es normal que se vea inestable), o `getCalStatus()` no está leyendo bien el registro. Antes de sacar conclusiones de ruido hay que resolver esto — ver pendientes abajo.

## Prueba 2 (16:20:52, ~30.0 s, 287 filas)

**Las 287 filas salieron en exactamente `0.000` en las 10 columnas (heading, roll, pitch, ax, ay, az), sin ninguna variación.** Esto no es un sensor "muy estable" — es físicamente imposible que un IMU real dé el mismo valor exacto miles de veces seguidas, especialmente en heading (que depende del magnetómetro). Lo más probable es que el sensor dejó de mandar datos en vivo justo después de que el script mandara el comando de borrar cero ('c') al iniciar, y lo que se grabó fue un valor congelado o un error silencioso de lectura I2C. **Este archivo no sirve para análisis de ruido** — hay que repetir la prueba mirando el Monitor Serie en vivo (no solo el CSV al final) para confirmar si el ESP32 se quedó pegado o si de verdad hay un bug en el manejo del comando 'c'.

## Filtro: EMA (promedio móvil exponencial) vs. Machine Learning

Decisión: empezar con un filtro simple, no con ML.

Razón: el ruido que se ve en la Prueba 1 (pitch con std ~1.8°) tiene toda la pinta de ruido instrumental normal (gaussiano, sin patrón), no un problema de reconocer una forma compleja en los datos — para eso un filtro clásico es exactamente la herramienta correcta, es barato de correr en el ESP32, no necesita datos de entrenamiento, y es fácil de explicar/justificar en el informe. El BNO055 además ya corre internamente una fusión sensorial tipo Kalman (modo NDOF, combina acelerómetro + giroscopio + magnetómetro) — meter otra capa de ML encima sería resolver con una herramienta pesada un problema que ya está parcialmente resuelto por el propio sensor. ML tendría sentido si el "ruido" tuviera un patrón dependiente del contexto (por ejemplo, error que cambia según la temperatura o la posición), que no es lo que se ve aquí.

Filtro propuesto: **promedio móvil exponencial (EMA)**:

```
filtrado[i] = alpha * crudo[i] + (1 - alpha) * filtrado[i-1]
```

`alpha` más chico = más suavizado pero más lento en reaccionar a un cambio real de orientación (más "delay"). Como el proyecto no exige baja latencia de lazo cerrado (ver README), se puede usar un alpha bajo sin problema.

Prueba con los datos reales de pitch (Prueba 1):

| filtro | desv. estándar |
|---|---|
| crudo | 1.840° |
| EMA alpha=0.15 | 1.545° |
| EMA alpha=0.05 | 1.164° |

Ver `filtro-ema-comparacion-pitch-S5.png` — el filtro reduce el ruido, pero **no es un sustituto de resolver el problema de calibración de arriba**: si el sensor no está bien calibrado, el filtro solo suaviza una señal que de por sí está sesgada, no corrige el sesgo.

## Pendientes que salen de este análisis

1. Confirmar por qué la calibración se queda en 0,0,0,0 durante toda la prueba (¿`getCalStatus()` mal leído, o el sensor de verdad sin calibrar?). Probar la rutina de calibración del BNO055 (mover en figura de 8 para el magnetómetro, rotar por varias orientaciones para el acelerómetro, dejar quieto unos segundos para el giroscopio) y repetir la prueba.
2. Repetir la Prueba 2 mirando el Monitor Serie en vivo — confirmar si el "todo en cero" es un cuelgue del ESP32, un bug del comando 'c', o un error de lectura I2C puntual.
3. Para heading, usar una métrica circular (o desenrollar el ángulo) en vez de std lineal si se necesita cuantificar su ruido.
4. Si después de calibrar bien el ruido sigue siendo un problema, implementar el EMA directamente en el firmware (una línea por eje, muy barato) en vez de solo en post-proceso Python.
