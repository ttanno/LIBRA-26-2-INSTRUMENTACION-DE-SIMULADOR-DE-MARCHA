# Comparativa — IMU de bajo drift para el homing del pivote (LIBRA)

**Fecha:** 31/08/2026
**Contexto:** complementa `Estado-del-arte/REFERENCIA DE POSICION ABSOLUTA/Arquitecturas-Referencia-Absoluta-sin-Goniometro.md` y el prototipo `Firmware/homing_absoluto/`. Origen: al fijar el cero del pivote (comando `z`) y volver físicamente a esa misma posición más tarde, el ángulo reportado por el MPU6050 no coincide exactamente con el cero guardado — se pidió evaluar IMU de menor drift, hasta el extremo de sensores "grado espacial/aeroespacial" con referencia casi absoluta.

---

## 1. Diagnóstico — por qué "vuelvo a 0" no da exactamente 0

Antes de la comparativa, vale separar tres causas distintas, porque cada una se ataca con una solución distinta (y no todas son "comprar mejor IMU"):

1. **Bias sistemático del acelerómetro (offset de fábrica + deriva térmica).** El homing por gravedad (`homing_absoluto.ino`) promedia ~1 s de lecturas del acelerómetro para fijar el cero — eso reduce el *ruido aleatorio* (la desviación estándar baja como `std/√N`, el mismo principio ya validado con el sobreamuestreo del BNO055 en la S4), pero **no corrige el bias sistemático**: si el eje Z del acelerómetro tiene un offset de fábrica de, por ejemplo, 10–20 mg, ese error se repite igual sin importar cuánto se promedie, y además cambia con la temperatura del chip. El MPU6050 no trae calibración de fábrica de este offset (a diferencia de los IMU industriales de la Sección 3).
2. **Deriva del giroscopio (bias instability) si el ángulo se integra entre eventos**, no solo se lee la gravedad de forma instantánea. El propio firmware de la S4 ya documenta esto a propósito con el `yaw_solo_giro` del MPU6050 (deriva visible con el sensor quieto). Para roll/pitch el filtro complementario limita el efecto porque el acelerómetro "ancla" la lectura, pero el giroscopio sigue empujando el valor entre correcciones.
3. **Holgura/backlash mecánico real del pivote** — no es un problema de sensor. Ningún IMU, por bueno que sea, corrige que el pivote físico no vuelva exactamente al mismo punto mecánico. Esto solo se descarta comparando contra una referencia externa rígida (o viendo si el error es sistemático y del mismo signo siempre, lo que apuntaría más a bias del sensor que a holgura aleatoria).

La causa 1 (bias del acelerómetro) es la más probable de ser la dominante en este caso puntual, porque el homing es una lectura de inclinación estática, no una integración continua — por eso la comparativa de abajo prioriza el **bias/repetibilidad del acelerómetro** (a veces publicado como "in-run bias stability" o "zero-g offset") tanto como el del giroscopio, que es la especificación que casi todas las comparativas de IMU enfatizan por defecto (pensando en navegación, no en homing estático).

---

## 2. Clasificación de grado de IMU (para calibrar expectativas de costo)

La industria clasifica los IMU MEMS por la estabilidad de bias del giroscopio (°/hr), que es también un buen proxy del nivel de calibración/fusión de todo el sensor:

| Grado | Bias instability típico (giro) | Costo típico | Ejemplos | Uso real |
|---|---|---|---|---|
| **Consumer** (lo que ya se probó) | ~10–100+ °/hr, sin calibración de fábrica fina | US$1–10 | MPU6050, MPU9250, BMI270 | Celulares, drones de juguete, wearables |
| **Consumer+ / MEMS moderno** | mejor ruido y estabilidad térmica que el anterior, sigue sin ser "°/hr" publicado | US$3–30 | LSM6DSR, ICM-45686, BNO085 | Drones FPV, tracking de movimiento (VR), robótica hobby |
| **Industrial / táctico (AHRS con EKF integrado)** | ~5–10 °/hr, con calibración de fábrica multi-temperatura | US$300–1000+ | Xsens MTi-3, VectorNav VN-100, Analog ADIS16470 | Drones profesionales, UGV/AGV, instrumentación de laboratorio, robótica industrial |
| **Navegación / "grado espacial" (FOG, RLG)** | ~0.001–1 °/hr | US$10 000–200 000+ | Honeywell HG4930, KVH 1750, Northrop LN-200 | Aviónica, satélites, submarinos, misiles guiados |

**Sobre "sensores de entornos espaciales":** los IMU realmente usados en satélites/aviónica (grado navegación) usan giroscopios de fibra óptica (FOG) o láser en anillo (RLG), no MEMS — cuestan entre US$10 000 y más de US$200 000, están sujetos a control de exportación (ITAR) en varios casos, y están diseñados para navegación inercial autónoma de horas sin ninguna referencia externa. Para el homing de un pivote de banco de pruebas (que sí tiene una referencia externa disponible: la gravedad, y potencialmente un tope mecánico) esto es varios órdenes de magnitud de sobre-ingeniería — el problema real no es "el giroscopio deriva en vuelo", es "la lectura de inclinación estática no es perfectamente repetible", que se resuelve en el nivel industrial/táctico (Sección 3.2) o, más barato todavía, con una referencia física adicional (Sección 4).

---

## 3. Opciones investigadas, por nivel

### 3.1 Nivel A — Reemplazo directo de bajo costo (mismo bus I2C/SPI, sin rediseño de PCB)

Comparativa basada en datos de la comunidad de tracking de movimiento (SlimeVR), que evalúa específicamente cuánto tarda cada chip en mostrar drift perceptible desde un cero fijado — el mismo tipo de problema que el homing de LIBRA:

| Opción | Precio aprox. | Tiempo hasta drift perceptible ("reset time") | Notas |
|---|---|---|---|
| **MPU6050 (el ya usado)** | US$1–3 | 1–5 min | Clasificado por la comunidad como "evitar" — alta tasa de fallas de fábrica y drift rápido; consistente con lo observado en LIBRA. |
| **LSM6DSR** ✅ | US$3–4 | 25–30 min | Mejor relación costo/beneficio; mismo footprint I2C/SPI que el MPU6050, breakout boards disponibles (Adafruit/SparkFun). |
| **ICM-42688-P** | ~US$8 | 25–30 min | Usado en controladoras de vuelo (Pixhawk/CubePilot) por su bajo ruido; sensible a deriva térmica sin compensación activa. |
| **ICM-45686** ✅ | ~US$7 | 45–60 min | Mejor resultado de la comparativa citada — mismo rango de precio que el MPU6050 casi 10× más caro, pero sigue siendo de un solo dígito de dólares. |
| **BNO085 (sucesor del BNO055, ya evaluado en S3)** | ~US$25–30 (Adafruit) | No cuantificado en esta búsqueda | Trae fusión de sensores on-chip mejorada respecto al BNO055 (mismo fabricante, misma familia CEVA/Bosch), calibración dinámica en background. Mismo pin-out I2C que el BNO055 ya descartado por costo en la S3 — si se reconsidera, es la opción de mayor fusión de sensores sin salir del rango "hobby". |

**Lectura para LIBRA:** el MPU6050 actual es, según esta misma comparativa, el peor chip de esta lista para el problema exacto que se está observando (repetibilidad del cero). Cambiar a LSM6DSR o ICM-45686 es un reemplazo casi directo (mismo bus I2C, breakout de tamaño similar, sin rediseño del soporte impreso) y, por precio, es una mejora que cuesta centavos de dólar más que seguir con el MPU6050.

### 3.2 Nivel B — Industrial / táctico (AHRS con calibración de fábrica y EKF integrado)

Esta es la categoría que da lo más cercano a "control casi absoluto de la referencia espacial" sin salir del rango de precio de un componente de laboratorio universitario (no de una misión espacial):

| Opción | Bias giro (in-run) | Bias/estabilidad acelerómetro | Exactitud estática roll/pitch | Precio aprox. | Interfaz |
|---|---|---|---|---|---|
| **Analog Devices ADIS16470** | 8 °/hr | 13 µg (in-run bias stability) | — (no publicado directamente en la ficha consultada) | desde US$345 (1ku) | SPI |
| **VectorNav VN-100** | 5–10 °/hr | 0.04 mg (40 µg) in-run bias stability | **0.5° RMS estático** / 1° RMS dinámico | ~US$400–600 (referencial, no confirmado en esta búsqueda) | UART / SPI, hasta 400 Hz orientación |
| **Xsens MTi-3** | no confirmado en esta búsqueda (ficha requiere descarga directa del PDF) | — | — | ~US$300–400 (referencial) | I2C / SPI / UART, kit de desarrollo disponible en Movella/SparkFun |

Los tres traen **calibración de fábrica multi-temperatura** (compensan el bias que el MPU6050 no corrige) y filtro de fusión (EKF) integrado en el propio chip/módulo, no en el ESP32. La especificación más relevante para el problema puntual de LIBRA es la **exactitud estática de roll/pitch del VN-100 (0.5° RMS)** — eso es directamente "qué tan repetible es leer la inclinación en reposo", que es exactamente el uso que le da el homing del pivote, y cumple con margen el requerimiento del proyecto de error <5°.

**Contras a tener en cuenta:** son 10–20× más caros que el BNO085 y 100× más caros que el MPU6050 actual; el ADS1256/HX711 y el resto de la arquitectura I2C ya definida no cambian, pero probablemente implicarían una nueva compra fuera del presupuesto ya ajustado de "bajo costo" que el proyecto ha mantenido consistentemente (mismo criterio usado para descartar el BNO055 en la S3 por costo, siendo este 10× más caro que el BNO055).

### 3.3 Nivel C — Navegación / "grado espacial" (mención de referencia, no recomendado)

Para contexto, ya que se pidió explícitamente: familias como el Honeywell HG4930, KVH 1750 o Northrop Grumman LN-200 (giroscopio de fibra óptica) logran bias instability de 0.001–1 °/hr — miles de veces mejor que el MPU6050 — pero cuestan entre US$10 000 y más de US$200 000, pesan/consumen mucho más, y algunos modelos tienen restricciones de exportación. Están diseñados para navegación inercial de una nave sin ninguna referencia externa durante horas o días (aviones, satélites, submarinos). No se investigó a más detalle porque no es una opción viable ni necesaria para este proyecto — se incluye solo para responder directamente la pregunta de "qué tan buenos son los sensores de grado espacial".

---

## 4. Recomendación

1. **Cambio inmediato de bajo costo (recomendado primero):** reemplazar el MPU6050 por un **LSM6DSR** o **ICM-45686** (Nivel A) — mismo bus I2C, mismo tipo de breakout, unos pocos dólares de diferencia, y según la comparativa consultada reduce drasticamente la deriva de corto plazo frente al chip actual, que es el peor evaluado de esa lista para este problema específico.
2. **Si el presupuesto permite ~US$300–400 y se quiere una repetibilidad de inclinación estática documentada (0.5° RMS) con calibración de fábrica real:** VectorNav VN-100 o Xsens MTi-3 (Nivel B) son la opción más cercana a "referencia casi absoluta" que tiene sentido de costo para un proyecto de pregrado — muy por debajo de un IMU de grado espacial, pero con especificaciones de esa misma familia de diseño (EKF integrado, calibración multi-temperatura).
3. **Evitar:** cualquier IMU de grado navegación/espacial (FOG/RLG) — resuelve un problema distinto (navegación autónoma sin referencia externa) al que tiene LIBRA (repetibilidad de una lectura de inclinación estática con referencia de gravedad disponible), a un costo 100–1000× mayor que la Sección 3.2.
4. **Punto importante, independiente del sensor elegido:** ningún IMU —ni siquiera un VN-100 o un IMU de grado espacial— corrige por sí solo el bias sistemático a menos que se calibre, ni elimina la holgura mecánica del pivote si existe. El propio `Pendientes.md` de la S4 ya tenía anotado como abierto *"evaluar si conviene además una marca/pin mecánico de refuerzo para el homing del pivote, en caso el nivelado por gravedad resulte problemático en la práctica"* — con el problema ya observado (el cero cambia al volver a él), esto deja de ser una opción a evaluar y pasa a ser la solución más barata y más alineada con el patrón ya identificado en `Arquitecturas-Referencia-Absoluta-sin-Goniometro.md` (todos los sistemas repetibles usan un evento físico fijo, no solo un sensor). Combinar un IMU mejor (Nivel A) **con** una marca o tope mecánico de referencia en el pivote resolvería el problema sin depender de comprar un IMU industrial.

---

## Fuentes consultadas

- [SlimeVR – IMU Comparison](https://docs.slimevr.dev/diy/imu-comparison.html) — tabla de "reset time" (tiempo hasta drift perceptible) por chip, incluye MPU6050, LSM6DSR, ICM-45686, ICM-42688.
- [Analog Devices – ADIS16470 Datasheet y ficha de producto](https://www.analog.com/en/products/adis16470.html) — bias instability giro (8°/hr) y acelerómetro (13 µg), precio de lista.
- [VectorNav VN-100 SMD Datasheet (Hardware v7.0)](https://metromatics.com.au/wp-content/uploads/2025/12/VN100SMD-Datasheet-v7.0-DS100-SMD-70-R1.pdf) — bias instability giro (5–10°/hr), bias acelerómetro (0.04 mg), exactitud estática/dinámica de roll/pitch.
- [Xsens MTi-3 AHRS](https://www.xsens.com/sensor-modules/xsens-mti-3-ahrs) y [ficha DigiKey](https://www.digikey.com/en/products/detail/xsens-technologies-bv/MTI-3-T/9607411) — referencia de producto y disponibilidad (specs de bias no confirmadas en esta búsqueda, requieren descarga directa del datasheet).
- [Adafruit – BNO085 Breakout Guide](https://learn.adafruit.com/adafruit-9-dof-orientation-imu-fusion-breakout-bno085) — precio (US$29.50) y confirmación de familia/fusión de sensores respecto al BNO055.
- [Aerowint – Choosing an ultra-stable, low-drift IMU: ICM-42688P](https://blog.aerowint.com/blog/choosing-ultra-stable-low-drift-imu-icm42688p/) — criterio de selección (ruido, no drift cuantificado) frente a otros MEMS modernos.
- Búsqueda general sobre clasificación de grado de IMU (consumer/táctico/navegación) y ejemplos de IMU de grado navegación (FOG/RLG): Honeywell HG4930, KVH 1750, Northrop Grumman LN-200 — mencionados como referencia de mercado, sin datasheet propio consultado en esta sesión.
