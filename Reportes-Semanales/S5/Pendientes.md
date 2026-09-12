# Pendientes — Semana 5 (abierto 29/08/2026)

Nota de trabajo informal (no es parte de los reportes formales). Continúa el mismo formato de `Reportes-Semanales/S4/Pendientes.md`, que quedó cerrado como histórico — retoma lo que seguía abierto de la S4 y suma lo nuevo de la S5 (compra del sensor de fuerza, comparativa de IMU de bajo drift, diseño del pylon en dos versiones).

## Selección de sensor de fuerza del pylon (foco de esta semana)

- [x] Comparativa de celdas de carga y electrónica de Amazon documentada (`Comparativa-LoadCells-S5.md`).
- [x] Celda de carga comprada: opción #4 (fuelle, patrón 3×M4), variante 220 lb (~978 N) — dimensionada para el caso de carga puntual ~1200 N (S3), no para el ensayo P5 completo.
- [ ] Escribir al vendedor para confirmar tipo de salida real (mV/V crudo vs. "Push-Pull") y compatibilidad con el ADS1256.
- [x] Disponibilidad del ADS1256 confirmada como comprable con envío a Perú (~US$27).

## Diseño mecánico del pylon (avance esta semana)

- [x] Versión A del bloque superior diseñada, con patrón de agujeros dimensionado para el sensor comprado.
- [x] Versión B (imprimible, con insertos roscados + tornillos como referencia mecánica temporal) diseñada, para no bloquear pruebas del simulador.
- [x] Guardar las 4 imágenes del diseño en `Evidencias/diseno-pylon-S5/` y activar los enlaces del resumen.
- [ ] Imprimir la versión B y correr pruebas de ajuste/ensamblaje en el simulador.
- [ ] Validación estructural en Fusion 360 (Static Stress Simulation) de la versión A, una vez confirmada la capacidad final del sensor — sigue abierto desde la S1.
- [ ] Caso de carga puntual ~1200 N (observación de la S3, 26/08) — sigue sin correr.

## IMU de bajo drift (avance esta semana)

- [x] Comparativa de IMU de bajo drift documentada (`Comparativa-IMU-Bajo-Drift.md`), incluyendo diagnóstico de las 3 causas posibles del problema de repetibilidad del homing.
- [ ] Decidir y comprar el reemplazo de Nivel A (LSM6DSR o ICM-45686) para el MPU6050 actual.
- [ ] Diseñar una marca/tope mecánico de referencia para el pivote (combinar con el IMU, no reemplazarlo).
- [ ] Repetir la validación cuantitativa del homing (heredado de la S4) una vez cambiado el IMU y/o agregado el tope mecánico.

## Pruebas de IMU (BNO055 y MPU6050)

- [x] **Primera prueba "dejarlo quieto" corrida (10/09, 30 s, ver `Evidencias/pruebas-imu-S5/`):** roll std ≈0.31°, pitch std ≈1.84° (más ruidoso que roll), heading con wrap-around en 0°/360° (no analizable con desviación estándar lineal, hace falta estadística circular).
- [ ] **BUG encontrado (10/09):** durante toda esa prueba `calib_sys/gyro/accel/mag` salió en `0,0,0,0` — ni siquiera el giroscopio calibró estando quieto, lo cual es raro. Revisar si `getCalStatus()` está leyendo bien el registro o si el sensor de verdad no está calibrado (correr la rutina de calibración: figura de 8 para el magnetómetro, varias orientaciones para el acelerómetro) antes de confiar en los números de ruido.
- [ ] **BUG encontrado (10/09):** una segunda prueba de 30 s salió con **las 287 filas en exactamente 0.000** en las 10 columnas — no es ruido real, algo falló (posiblemente ligado al comando de borrar cero que el script manda al iniciar). Repetir mirando el Monitor Serie en vivo para confirmar si el ESP32 se cuelga o hay un bug en el manejo del comando 'c'. Archivo no usable para análisis (`bno055_20260910_162052.csv`).
- [x] **Decisión de filtrado (10/09):** empezar con un filtro simple (promedio móvil exponencial / EMA) en vez de machine learning — el ruido observado es instrumental (gaussiano, sin patrón) y el BNO055 ya hace fusión tipo Kalman internamente (modo NDOF), así que ML estaría sobre-dimensionado. Con los datos de la Prueba 1, EMA alpha=0.05 bajó el std de pitch de 1.84° a 1.16° (ver `Evidencias/pruebas-imu-S5/filtro-ema-comparacion-pitch-S5.png`). Pendiente: no tiene sentido optimizar el filtro hasta resolver el bug de calibración de arriba.
- [ ] Prueba lado a lado BNO055 vs. MPU6050 sobre el mismo movimiento.
- [ ] Confirmar el MPU6050 (o su reemplazo Nivel A) contra el inventario del laboratorio.

## Referencia de posición absoluta — husillo (heredado, sin avance esta semana)

- [ ] Medir el diámetro real del eje del motor (calibre) y diseñar/imprimir el collarín con el imán de neodimio.
- [ ] Montar el sensor Hall + collarín y validar el homing en el motor real.
- [ ] Definir y combinar con un límite físico de fin de carrera del riel (switch mecánico/óptico/Hall).

## Referencia de posición absoluta — pivote (flexo-extensión) (nuevo, 10/09)

- [x] **Diagnóstico (10/09):** el motor paso a paso del pivote es lazo abierto puro (sin encoder) — parte de -65°, cuenta pasos hasta +65°, e infiere el 0° a partir de ese conteo. Si el motor pierde pasos bajo carga (justo cuando la prótesis pisa/carga el sistema — el momento más importante del ensayo), el conteo se desfasa respecto al ángulo real, y el pivote ya no vuelve al 0° real al terminar la prueba aunque el conteo diga que sí. Es la razón de fondo de por qué no basta con contar pasos y de por qué ya existe `homing_absoluto.ino` (el IMU mide inclinación real respecto a la gravedad, no depende del conteo de pasos).
- [ ] Evaluar agregar un **sensor Hall + imán en el punto de 0° (horizontal) del pivote**, análogo a `homing_husillo_hall.ino` en el husillo — daría un evento físico de referencia independiente del conteo de pasos, para re-calibrar el cero con confianza entre pruebas. Limitación: no corrige el desfase a mitad de un ciclo de marcha, solo permite volver a 0° real de forma confiable al reiniciar/re-homear.
- [ ] Confirmar si el IMU (actual o su reemplazo de bajo drift, ver sección "IMU de bajo drift") es suficiente por sí solo para detectar el desfase en tiempo real durante el ensayo, o si conviene combinarlo con el Hall del punto anterior — mismo patrón ya identificado en `Arquitecturas-Referencia-Absoluta-sin-Goniometro.md` (todo sistema repetible usa un evento físico fijo, no solo un sensor).
- Relacionado: el ángulo real de los dos limit switches del pivote tampoco está confirmado al 100% todavía (ver sección AMTI más abajo, heredado ahí por organización del documento, no porque sea parte de la AMTI).

## Sensores de distancia y ángulo — heredado, cerrar BOM

- [x] Sensor de traslación decidido (10/09): **VL53L1X** (I2C), no TF-Luna — coherente con el adaptador que ya se está diseñando en Fusion 360 (`Evidencias/diseno-adaptador-sensor-S5/`, ver `Resumen-Semana5.md` sección 4). `Conexiones-PlacaESP32-S5.md` actualizado en consecuencia.
- [ ] Sensor de rotación (AS5600) sigue sin cerrar.
- [ ] Cerrar el BOM completo de sensores.

## Mecanismo de elevación — espesor de la plataforma superior (nuevo, 08/09)

- [ ] Medir cuánta distancia se levanta el mecanismo (carrera del actuador/husillo entre la plataforma inferior y la superior) para determinar el espesor necesario de la plataforma de arriba.

## Heredado de la S1 — bibliografía (sigue abierto)

- [ ] [2] Confirmar autor/año exacto de la tesis de maestría (R. Davis, Cleveland State Univ.) contra OhioLINK — accession `csu1396786747`.
- [ ] [4] Nie et al. — documento IEEE no indexado en las búsquedas realizadas; requiere acceso directo a IEEE Xplore.
- [ ] [12] "Evaluating shear and normal force with the use of an instrumented transtibial socket" — sin autor identificado.
- [ ] [15] "Instrumented socket inserts for sensing interaction at the limb-socket interface" — sin autor identificado.
- [ ] P3 y P6 de ISO 10328 sin verificación confiable — no priorizar salvo que el proyecto deba cubrir usuarios >100 kg.
- [ ] Decidir el alcance de sensores de presión distribuida (FSR array) vs. solo celda de carga puntual, y ajustar la Secc. 6 de la revisión bibliográfica en consecuencia.
- [ ] Actualizar Secc. 4.1, 9 y 10 de la revisión bibliográfica con el cambio de prioridad GRF/pylon y la arquitectura de sensores por DOF (pendiente desde la S2).

## Heredado de la S1/S2/S3 — plataforma AMTI (despriorizada por ahora, 10/09)

**Decisión (10/09):** el foco de electrónica pasa a cerrar la celda de carga del pylon + el VL53L1X; la integración de la AMTI con el ADS1256 queda en pausa (no descartada, solo sin trabajo activo por ahora). Los puntos de abajo siguen abiertos tal cual.

- [x] Modo de salida analógica del amplificador confirmado (10/09): **Fully Conditioned** (no MSA-6 Compatible).
- [ ] Ubicar el certificado de calibración real de la plataforma (matriz de sensibilidad real, no la de ejemplo del manual) — con el amplificador en Fully Conditioned, la matriz de sensibilidad convierte volts ya acondicionados (ganancia+offset aplicados por el amplificador) directo a fuerza/momento, a diferencia de MSA-6 Compatible; confirmar que el certificado que se ubique corresponda a este modo.
- [ ] Seguimiento del formulario de soporte técnico enviado a AMTI — sigue sin respuesta (confirmado 10/09).
- [ ] Diseñar la interfaz de lectura de los 6 canales de la AMTI con el ADS1256.
- [x] Confirmado (10/09): el motor paso a paso del pivote (flexo-extensión) **no tiene encoder real** — la posición se deriva por conteo de pasos en lazo abierto respecto a los pasos que debe dar el motor. Tiene **dos limit switches en ángulos supuestamente conocidos**, pero **el ángulo absoluto de esos switches todavía NO está confirmado al 100%** — son un punto de referencia física candidato, no una referencia ya validada. Relevante para `Estado-del-arte/REFERENCIA DE POSICION ABSOLUTA/Arquitecturas-Referencia-Absoluta-sin-Goniometro.md` y el problema de repetibilidad del homing por IMU (`homing_absoluto.ino`, S4/S5).
- [ ] Medir/verificar el ángulo real de al menos uno de los dos limit switches (ej. con el mismo IMU ya montado, o un goniómetro externo, en el momento en que el switch se activa) antes de poder usarlos como referencia absoluta confiable para el homing del pivote.

## Sin dueño claro — verificar antes de cerrar la semana

- [ ] Confirmación formal del asesor sobre el simulador existente (transtibial únicamente, estructura ya construida) — sigue informal desde la S1.
