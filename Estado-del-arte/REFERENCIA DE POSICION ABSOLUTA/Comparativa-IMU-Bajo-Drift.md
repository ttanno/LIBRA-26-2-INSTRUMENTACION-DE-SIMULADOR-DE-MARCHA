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


---

## 5. Ejemplos reales — qué IMU usa cada robot/plataforma comparable, y para qué

Complementa la Sección 2 (grados de IMU) y la Sección 3 (opciones investigadas) con casos concretos de robots y prótesis reales que enfrentan el mismo problema de fondo que LIBRA — estimar orientación/posición sin un sensor de referencia absoluta perfecto — para ver qué grado de IMU eligió cada uno y por qué.

| Robot / dispositivo | IMU usado | Grado (Sección 2) | Qué hace el IMU ahí |
|---|---|---|---|
| **Cassie** (robot bípedo de investigación, Agility Robotics / Univ. Michigan / Caltech) | **VectorNav VN-100** | Industrial/táctico (Nivel B — el mismo que recomienda este documento) | Alimenta un filtro de Kalman extendido que estima la pose de la "base flotante" del robot (orientación, velocidad, posición) — el equivalente exacto al problema de LIBRA: el robot no puede medir esos grados de libertad con sus encoders de las piernas, así que depende del IMU como referencia. Validación directa de que el VN-100 es la opción real usada en un robot de marcha bípedo con requerimientos similares a los de LIBRA. |
| **HyQ** (cuadrúpedo de investigación, IIT) | **KVH-1775** (giroscopio de fibra óptica) y **3DM-GX5-15** (MicroStrain) — el mismo HyQ trae ambos para comparar | KVH-1775: navegación (Nivel C) · 3DM-GX5-15: industrial (Nivel B) | Estimación del estado de la base del robot (orientación y velocidad) para controlar el balance al caminar. Sirve como referencia de cuánto mejora (o no) pasar de un IMU industrial a uno de grado navegación en un robot de patas — la comparación en la que se basa buena parte de la literatura de "state estimation" para legged robots. |
| **Spot** (Boston Dynamics, robot cuadrúpedo comercial) | **3DM-GQ7** (MicroStrain), un GNSS/INS con IMU de precisión integrado | Industrial/táctico, con fusión GNSS | Navegación autónoma con posiciones de hasta ±1 cm (con correcciones RTK) y mantiene la estimación de posición cuando no hay señal GPS (dentro de edificios, túneles) — un caso de "referencia casi absoluta" real y en producción, aunque resuelve un problema distinto al de LIBRA (navegación de largo alcance, no repetibilidad de un homing estático). |
| **Rodilla protésica "i-Inspire"** (prototipo académico de bajo costo, magnetorreológico, MDPI 2024) | **GY-521** (el módulo breakout del **MPU6050**) | Consumer | Detecta la inclinación de la rodilla hacia adelante/atrás respecto al suelo para que el controlador distinga entre caminar, estar de pie o sentarse, fusionando acelerómetro y giroscopio con un filtro complementario (no Kalman, por costo de cómputo). Es el caso más parecido al punto de partida de LIBRA en la S3/S4 (mismo chip, MPU6050/GY-521, antes de migrar al BNO055 en la S6 — ver nota de corrección al final del documento), con las mismas limitaciones de bias/drift ya diagnosticadas en la Sección 1. |
| **Exoesqueleto de miembro inferior** (sistema Imocap-GIS, revisión académica) | Sistema propietario con hasta 4 IMU inerciales-magnéticos simultáneos (sin modelo de chip publicado) | No especificado (grado no publicado) | Coloca varios IMU en puntos del miembro inferior del usuario para reconstruir el ángulo de cada articulación y sincronizar el movimiento del exoesqueleto con la intención del usuario en tiempo real (latencia de 20–30 ms) — ejemplo de usar *varios* IMU de menor grado en vez de uno solo de mayor grado, otra estrategia distinta a "comprar un IMU mejor". |

**Lectura para LIBRA:** el patrón se repite en los tres niveles de la Sección 2 — el chip que LIBRA probó primero (MPU6050/GY-521, en la S3/S4, antes de migrar al BNO055 en la S6 — ver nota de corrección al final del documento) es literalmente el mismo que usa un prototipo académico de rodilla protésica con el mismo tipo de limitación de inclinación estática; y el VN-100 recomendado en la Sección 3.2 no es una elección teórica de esta comparativa, sino el sensor que un robot bípedo real (Cassie) usa hoy para resolver el mismo tipo de problema (estimar una pose que el propio robot no puede medir con sus otros sensores). Ningún robot de esta lista usa IMU de grado espacial/navegación (Nivel C) como solución principal — el KVH-1775 de HyQ aparece solo como comparación de investigación, no como la opción elegida para producción, lo que refuerza la recomendación de la Sección 4 de evitar ese nivel para LIBRA.

### Fuentes adicionales (Sección 5)

- [MicroStrain by HBK — Spot's Autonomous Adventure](https://www.microstrain.com/blog/spots-autonomous-adventure) — modelo 3DM-GQ7 GNSS/INS y su rol en navegación autónoma de Spot.
- [Fink & Semini, 2020 — Proprioceptive Sensor Fusion for Quadruped Robot State Estimation (IIT)](https://iit-dlslab.github.io/papers/fink20iros.pdf) — KVH-1775 y 3DM-GX5-15 en HyQ.
- [Reher et al., 2019 — Dynamic Walking with Compliance on a Cassie Bipedal Robot](http://ames.caltech.edu/reher2019dynamic.pdf) — confirma el VectorNav VN-100 como IMU de Cassie y su uso en el EKF de estimación de base flotante.
- [Design, Analysis, and Development of Low-Cost State-of-the-Art Magnetorheological-Based Microprocessor Prosthetic Knee (MDPI Sensors 2024)](https://www.mdpi.com/1424-8220/24/1/255) — GY-521/MPU6050 en la rodilla protésica "i-Inspire" y su uso con filtro complementario.
- [Integration of Inertial Sensors in a Lower Limb Robotic Exoskeleton (PMC)](https://pmc.ncbi.nlm.nih.gov/articles/PMC9229016/) — sistema Imocap-GIS con múltiples IMU para exoesqueleto de miembro inferior.


---

## 6. Catálogo de DFRobot (categoría "IMU Sensors") — qué venden y si sirve para LIBRA

Corrección: la sección 5 no había revisado esta fuente. A pedido, se revisó directamente el catálogo de [DFRobot — categoría 65 "IMU Sensors"](https://www.dfrobot.com/category-65.html) (proveedor habitual de breakouts para Arduino/hobby). La página carga productos por scroll infinito, así que esta lista cubre los ~20 productos visibles al cargar la página sin scroll adicional — puede haber más ítems no capturados aquí.

### 6.1 Módulos con giroscopio (candidatos reales a IMU de orientación)

| Producto DFRobot | Precio | Chip real | Lectura para LIBRA |
|---|---|---|---|
| **Fermion: MPU-6050 6DOF (SEN0142)** | US$12.90 | MPU6050 | Es el chip que LIBRA usó en sus primeras pruebas (S3/S4), no el que usa actualmente (ver nota de corrección al final del documento) — no aporta nada nuevo, solo confirma que DFRobot también lo vende (más caro que un breakout genérico de ~US$1-3). |
| **Gravity: I2C BMI160 (SEN0250)** | US$9.90 | Bosch BMI160 | Según la comparativa de SlimeVR ya citada en la Sección 3.1, el BMI160 está en la lista de **"evitar"**: reset time de solo 5–15 min (similar al MPU6050) y ~20% de unidades con fallas de fábrica (DOA). No es una mejora sobre el problema actual. |
| **Fermion: BNO055 (SEN0374)** | US$17.90 | Bosch/CEVA BNO055 | **Es el sensor que LIBRA usa realmente desde la S6** (con la librería `DFRobot_BNO055`) — no quedó descartado por costo como se afirmaba antes en este documento; ver nota de corrección al final. Aquí sale más barato que el precio de referencia (~US$38) usado en la Sección 3.1. Su reset time reportado por SlimeVR (1–10 min) es mediocre frente al LSM6DSR/ICM-45686 del Nivel A, pero LIBRA ya está atacando el bias por calibración física de 6 posiciones (S6) en vez de depender solo de la especificación del chip; el sucesor BNO085 (Sección 3.1) no aparece en este catálogo de DFRobot. |
| **Gravity: 10 DOF IMU AHRS (SEN0253)** | US$25.90 | BNO055 + BMP280 | Mismo chip base que el anterior (BNO055) con barómetro agregado — mismas limitaciones de drift, más caro. |
| **Arduino 9 Axes Motion Shield (DFR0407)** | US$29.00 | BNO055 | Mismo chip, en formato shield para Arduino Uno — mismas limitaciones, el precio más alto de los tres es por el formato shield, no por mejor sensor. |
| **Gravity: 10DOF IMU Sensor (SEN0696)** | US$19.90 | **Bosch BMI323** (accel+giro) + BMM350 (magnetómetro) + BMP581 (barómetro) | Chip más nuevo que no aparece en la comparativa de SlimeVR ya citada (esa lista cubre BMI160 pero no BMI323), así que **no hay dato de reset time verificado** para confirmar si mejora sobre el MPU6050 — sería una incógnita, no una recomendación confirmada como sí lo son el LSM6DSR/ICM-45686 de la Sección 3.1. |
| **Gravity: 9DOF IMU Sensor (SEN0694)** / **Fermion: Compact 9/10DOF (SEN0695/SEN0697)** | US$13.90–17.90 | Misma familia BMI323 (según la librería oficial `DFRobot_Multi_DOF_IMU` que agrupa SEN0692/SEN0694/SEN0696) | Mismo caso que el anterior: chip nuevo, sin dato de drift verificado en esta investigación. |
| **Fermion: 10 DOF IMU Sensor (SEN0140)** | US$12.90 | ADXL345 + ITG3205 + VCM5883L + BMP280 (módulo antiguo, ADXL345 ya está en la lista de acelerómetros de la tabla siguiente) | Combinación de chips más antiguos y ya superados por las opciones de la Sección 3.1; el ITG3205 (giroscopio) es previo incluso al MPU6050 en la línea de productos de InvenSense. |
| **Tilt Compensated Magnetic Compass (SEN0183)** | US$29.90 | CMPS12 (brújula con compensación de inclinación) | Es un sensor de rumbo (heading), no un IMU de propósito general — resuelve un problema distinto (orientación respecto al norte magnético) y no es aplicable al homing del pivote de LIBRA. |

### 6.2 Acelerómetros sin giroscopio (no sirven solos para el homing)

DFRobot también vende varios acelerómetros de 3 ejes sin giroscopio integrado: **LIS2DW12** (SEN0405/SEN0409, US$3.90), **LIS2DH** (SEN0224, US$4.90), **ADXL345** (SEN0032, US$5.90), **BMA220** (SEN0168, US$4.90, stock limitado), **H3LIS200DL** (SEN0412/SEN0408, ~US$14) y **LIS331HH** (SEN0407, US$15.50) — estos últimos dos de alto rango (±100–200g), pensados para detectar impactos/vibración, no inclinación fina. Ninguno trae giroscopio, por lo que **no pueden reemplazar al MPU6050 por sí solos**: el homing de LIBRA necesita la combinación acelerómetro+giroscopio (o más ejes) que ya tiene el MPU6050, no menos sensores.

### 6.3 Conclusión de esta sección

**Corrección importante (ver Sección 7): el sensor real que usa LIBRA hoy es el BNO055 de DFRobot (Fermion SEN0374), no el MPU6050** — este análisis se escribió comparando el catálogo contra el MPU6050 por error. Con esa corrección: LIBRA ya tiene el sensor que este catálogo ofrece (BNO055), el BMI160 sigue sin ser una mejora (lista de "evitar"), y el BMI323 (el chip más nuevo del catálogo) no tiene datos de drift verificados en esta investigación como para preferirlo sobre el BNO055 ya calibrado. **Los dos chips de Nivel A (LSM6DSR e ICM-45686, Sección 3.1) siguen sin estar disponibles en este catálogo de DFRobot** — seguirían sin poder conseguirse ahí si se decide migrar más adelante.

### Fuentes adicionales (Sección 6)

- [DFRobot — Categoría 65: IMU Sensors](https://www.dfrobot.com/category-65.html) — catálogo revisado.
- [DFRobot Wiki — SEN0250 (BMI160)](https://wiki.dfrobot.com/sen0250/), [SEN0140 (10 DOF)](https://wiki.dfrobot.com/sen0140/), [SEN0253 (BNO055+BMP280)](https://wiki.dfrobot.com/sen0253/) — fichas técnicas de los módulos citados.
- [DFRobot — Product 3126 (SEN0696)](https://www.dfrobot.com/product-3126.html) — confirma chips Bosch BMI323/BMM350/BMP581.
- [GitHub — DFRobot_Multi_DOF_IMU](https://github.com/DFRobot/DFRobot_Multi_DOF_IMU) — confirma que SEN0692/SEN0694/SEN0696 comparten la misma familia de chips.


---

## 7. Nota de corrección (21/09/2026) — el sensor real en uso es el BNO055, no el MPU6050

Las Secciones 5 y 6 de este documento (agregadas en esta misma sesión) asumieron que el MPU6050 seguía siendo el IMU actual de LIBRA, siguiendo lo que dice la Sección 1 (redactada el 31/08, durante la S5). Eso quedó desactualizado: revisando `Reportes-Semanales/S3` a `S7`, la línea de tiempo real es:

- **S3 (26/08):** se elige el MPU6050/GY-521 como "probable" IMU por estar ya disponible en el laboratorio; el BNO055 se deja de lado en ese momento **solo por no estar en inventario** (había que comprarlo, ~US$30–35) — no por rendimiento.
- **S4:** se prueban ambos en paralelo (`test_bno055.ino` y `test_mpu6050.ino`) y se prototipa el homing (`homing_absoluto.ino`) sobre el MPU6050, que es lo que motivó el diagnóstico de drift de la Sección 1 y la comparativa de las Secciones 2–4 de este documento.
- **S6 (05–11/09):** el proyecto **pivotea al BNO055 comprado a DFRobot (Fermion SEN0374)** — se corrige un bug crítico en la librería `DFRobot_BNO055` (llamada redundante a `Wire.begin()` que rompía la lectura I2C), se construyen herramientas de validación de ruido y una calibración de acelerómetro de 6 posiciones, y se deja explícitamente pendiente "retomar la decisión de la S5 sobre el reemplazo de IMU (LSM6DSR/ICM-45686) — ahora con el BNO055 funcionando de forma confiable, evaluar si sigue conviniendo migrar o si el BNO055 calibrado ya cubre el caso de uso".
- **S7 (12–18/09):** todo el trabajo de IMU es sobre el BNO055 — calibración `ACC_RADIUS`, filtro EMA embebido en firmware, y el hallazgo de que buena parte del ruido reportado en S6 era un conector flojo (std sube de ~0.0005° a 0.35–0.63° con el conector mal puesto), no necesariamente el chip.

**En limpio:** el MPU6050 fue el IMU de las Secciones 1–4 (S4/S5), pero **desde la S6 LIBRA usa el BNO055 de DFRobot** como sensor activo, con trabajo de calibración y depuración en curso (no descartado por costo como decían las Secciones 5–6 antes de esta corrección). La decisión de migrar a LSM6DSR/ICM-45686 (Nivel A) sigue abierta según la propia S6 — no se ha tomado ni se ha revertido —, así que la recomendación de la Sección 4 no está descartada, solo pendiente de esa evaluación con el BNO055 ya calibrado como punto de comparación real.

**Pendiente para la próxima actualización de este documento:** repetir el análisis de las Secciones 5 y 6 comparando explícitamente contra el BNO055 calibrado (no contra el MPU6050), y con los datos de ruido reales de la S6/S7 (roll std ≈0.06–0.5°, pitch std ≈0.29–0.54° sin calibración de acelerómetro completa) en vez de solo el "reset time" genérico del SlimeVR.

### Fuentes (Sección 7)

- `Reportes-Semanales/S3/Resumen-Semana3.md` y `Pendientes.md` — elección inicial del MPU6050 por disponibilidad, no por rendimiento.
- `Reportes-Semanales/S4/Resumen-Semana4.md` — prueba en paralelo de BNO055 y MPU6050, prototipo de homing sobre MPU6050.
- `Reportes-Semanales/S5/Resumen-Semana5.md` — origen de este documento y de la recomendación de migrar a LSM6DSR/ICM-45686.
- `Reportes-Semanales/S6/Resumen-Semana6.md` — pivote al BNO055 (DFRobot Fermion SEN0374), corrección del bug de `DFRobot_BNO055`, calibración de 6 posiciones.
- `Reportes-Semanales/S7/Resumen-Semana7.md` — calibración `ACC_RADIUS`, filtro EMA embebido, diagnóstico del ruido por conector flojo.
