# Pendientes — Semana 3 (abierto 19/08/2026, cerrado 28/08/2026)

> **Cerrado (histórico).** Los ítems que seguían abiertos al cierre de la S3 (incluyendo las observaciones de referencia de posición absoluta del 26/08 y 27/08) se trasladaron a [`Reportes-Semanales/S4/Pendientes.md`](../S4/Pendientes.md).

Nota de trabajo informal (no es parte de los reportes formales). Continúa el mismo formato de `Reportes-Semanales/S1/Pendientes.md`, que quedó cerrado como histórico — la Semana 2 no generó su propio `Pendientes.md` (se usó `Resumen-Semana2.md` como resumen narrativo), así que este archivo retoma directamente lo que seguía abierto de la S1 y suma lo nuevo de la S3. Referencias entre `[ ]` apuntan a `Estado-del-arte/Revision bibliografica - Semana 1-2.md` salvo que se indique otro archivo.

## Prioridad — GRF vs. pylon (decidir y documentar)

- [ ] **Resolver la disyuntiva de prioridad:** en la reunión del 12/08 Dante confirmó GRF (plataforma AMTI) como prioridad y el pylon como secundario. Entrando a la S3, Victoria (asesora del día a día) pidió priorizar el pylon. Falta dejar por escrito con Dante y Victoria cuál es la prioridad real de esta semana, para no generar una desalineación de expectativas.
- [ ] Documentar el cambio de foco como decisión de asesoría (no como un olvido) en el próximo Informe Semanal / Reporte de Avance, para que quede trazable si Dante pregunta por qué el foco de la semana fue el pylon y no el GRF.
- [x] Mientras se resuelve, se avanzó investigación de sensores del lado del pylon (ver abajo) sin descartar el trabajo ya hecho del lado GRF/AMTI (Secc. "Integración AMTI" de la S1, `Resumen-Semana2.md`).

## Diseño mecánico del pylon (foco de esta semana si se prioriza a Victoria)

- [ ] Diseñar el bracket/adaptador para montar la celda de carga elegida en el punto de anclaje del simulador (pernos del marco rojo, ya identificados en las fotos de `Evidencias/simulador/`).
- [ ] Hacer un boceto físico de la ubicación real de la celda (no solo el diagrama lógico de bloques).
- [ ] Validación estructural del bracket/placa en Fusion 360 (Static Stress Simulation) — pendiente de la S1, sigue abierto.
- [ ] **Caso de carga puntual, ~1200 N (observación, 26/08):** además de la validación estructural general, correr una simulación con una carga puntual de ~1200 N aplicada en un solo punto de la placa/bracket (no repartida uniformemente) — en la práctica la carga real a veces no se distribuye equitativamente sobre la superficie de apoyo, y ese caso concentrado puede dar un esfuerzo (von Mises) más alto que el caso con carga distribuida ya simulado en `Evidencias/simulacion-ansys/`. Definir el punto más desfavorable (borde/esquina de la placa) para el peor caso.

## Selección de sensor de fuerza del pylon

- [x] **Candidata TAL107F-10kg descartada por subdimensionada** (10 kg ≈ 98 N frente a 4480 N de carga última ISO 10328 P5) — reemplazada por una comparativa de celdas axiales de 1 eje dimensionadas para el rango real. Ver `Estado-del-arte/SENSORES DE FUERZA/PYLON/Comparativa-Sensores-Fuerza-Axial-Pylon.md`.
- [ ] Elegir una candidata final de la comparativa y cerrar el pedido/cotización.
- [ ] [40] Ítem de la S1 ("confirmar si Matray et al. 2025 usa efectivamente TAL107F-10kg") queda sin objeto — ya no es la candidata del proyecto, no seguir esa verificación salvo interés puramente bibliográfico.
- [ ] Definir el ADC final para la celda: ADS1256 (24-bit, ya usado del lado GRF, permite compartir un solo ADC con la plataforma AMTI) vs. HX711 (más simple, dedicado). Evaluar si conviene un solo ADC para todo o uno por sensor.
- [ ] Rango de la celda: mantener el criterio de margen ~1.5–2× sobre la carga última P5 (4480 N) para no dañar el sensor en ensayos cíclicos — verificar que la candidata elegida lo cumpla.

## Sensores de distancia y ángulo (investigados en paralelo)

- [x] Investigación de sensores de distancia (VL53L1X, TF-Luna, Baumer OM70) y de ángulo (AS5600, encoder Omron E6B2-CWZ6C, potenciómetro multivuelta) — ver `Estado-del-arte/Sensores-LIBRA-Presentacion.pptx`.
- [ ] Elegir sensor final de traslación (láser ToF, recomendado por Dante en la S2) y de rotación (encoder), y cerrar BOM.

## Heredado de la S1 — bibliografía (sigue abierto)

- [ ] [2] Confirmar autor/año exacto de la tesis de maestría (R. Davis, Cleveland State Univ.) contra OhioLINK — accession `csu1396786747`.
- [ ] [4] Nie et al. — documento IEEE no indexado en las búsquedas realizadas; requiere acceso directo a IEEE Xplore.
- [ ] [12] "Evaluating shear and normal force with the use of an instrumented transtibial socket" — sin autor identificado.
- [ ] [15] "Instrumented socket inserts for sensing interaction at the limb-socket interface" — sin autor identificado.
- [ ] P3 y P6 de ISO 10328 sin verificación confiable — no priorizar salvo que el proyecto deba cubrir usuarios >100 kg.
- [ ] Decidir el alcance de sensores de presión distribuida (FSR array) vs. solo celda de carga puntual, y ajustar la Secc. 6 de la revisión bibliográfica en consecuencia.

## Heredado de la S1 — electrónica / IMU (sigue abierto)

- [ ] Inventario de IMUs del laboratorio: ninguno es BNO055 (la preferencia registrada por fusión de sensores integrada) — decidir si se compra un BNO055 o se usa lo disponible (MPU9250 / MPU6050 + HMC5883L, que requieren resolver el filtrado de deriva por software).
- [ ] Confirmar qué es exactamente "V1350 YP-05" en el inventario — nombre no identificado con certeza.
- [ ] Confirmar si los duplicados aparentes del inventario de IMUs (MPU6050 / MPU 6050 / MPU6050-PCB / GY-521 / MPU6050 GY-521) son unidades físicas distintas o el mismo ítem contado varias veces.
- [ ] Preguntar al asesor si el motor paso a paso de la plataforma tiene retroalimentación real (encoder en el eje) o es solo conteo de pasos en lazo abierto — sigue sin confirmarse explícitamente.

## Heredado de la S1/S2 — plataforma AMTI (sigue abierto, ver también `Resumen-Semana2.md`)

- [ ] Confirmar el modo de salida analógica configurado actualmente en el amplificador (MSA-6 Compatible vs. Fully Conditioned) sin alterar la configuración compartida del laboratorio.
- [ ] Ubicar el certificado de calibración real de la plataforma (matriz de sensibilidad real, no la de ejemplo del manual).
- [ ] Seguimiento del formulario de soporte técnico enviado a AMTI (sin respuesta aún).
- [ ] Diseñar la interfaz de lectura de los 6 canales de la AMTI con el ADS1256.
- [ ] Actualizar Secc. 4.1, 9 y 10 de la revisión bibliográfica con el cambio de prioridad GRF/pylon y la arquitectura de sensores por DOF (pendiente desde la S2, aún no hecho).

## Resuelto en la S2 (ya no arrastrar, referencia solo)

- [x] Arquitectura de sensado por grado de libertad confirmada por Dante: GRF (plataforma), pylon (celda de carga), traslación (láser ToF), rotación (encoder/potenciómetro) — IMU como validación cruzada, no medición primaria. Ver `Resumen-Semana2.md`.
- [x] Plataforma AMTI BP400600 confirmada físicamente en el laboratorio, con salida analógica DB25S y pinout documentado.
- [x] Rol del IMU frente al encoder — el IMU no reemplaza al encoder, sirve como validación cruzada de holgura/backlash.

## Sin dueño claro — verificar antes de cerrar la semana

- [ ] Confirmación formal del asesor sobre el simulador existente (transtibial únicamente, estructura ya construida) — quedó informal en la S1; revisar si la reunión del 12/08 la dejó implícitamente confirmada.

## Referencia de posición absoluta de la plataforma (observación, 26/08)

- [ ] **Problema detectado por Alessandro:** el simulador actual no tiene una referencia de posición inicial absoluta. Sin ella, cualquier sensor incremental (encoder relativo, conteo de pasos del motor paso a paso) solo sabe su posición *relativa* a dónde estaba el eje cuando se encendió el sistema — no a una posición física real y repetible. Esto se conecta directamente con el pendiente ya abierto de la S1 sobre si el motor paso a paso tiene retroalimentación real o es lazo abierto (ver sección "Heredado de la S1 — electrónica / IMU").
- [ ] Buscar/evaluar un sensor de posición **absoluta** que mantenga la referencia en el tiempo (incluso tras apagar y encender) sin necesitar una rutina de homing manual cada vez. Candidatos a investigar:
  - Encoder rotativo/lineal **absoluto** (a diferencia del incremental, entrega la posición real desde el primer instante, sin necesidad de referenciarse).
  - Sensor de home/límite (switch óptico, magnético o mecánico de fin de carrera) para establecer el cero mecánico en cada arranque, combinado con el encoder incremental ya elegido (AS5600).
- [ ] Definir si el problema de referencia absoluta aplica solo al eje de traslación (husillo/riel) o también al pivote de rotación (flexo-extensión) — probablemente ambos ejes lo necesiten.
- [x] **Prototipo en prueba (27/08):** para el eje de rotación, `Firmware/homing_absoluto/homing_absoluto.ino` implementa un homing con el acelerómetro del MPU6050 (gravedad como referencia absoluta) que guarda el cero en la memoria flash del ESP32 (persistente entre reinicios). Pendiente: validar en el pivote real y confirmar que la posición mecánica de "cero" corresponde a una orientación reconocible respecto a la gravedad. El eje de traslación (husillo/riel) sigue sin resolver — sigue necesitando encoder absoluto o switch de home.
- [x] **Prototipo en prueba (27/08), eje de traslación:** `Firmware/homing_husillo_hall/homing_husillo_hall.ino` implementa homing del eje del motor con un imán montado en un collarín impreso + sensor Hall fijo al chasis (índice físico, dos etapas rápida/lenta para precisión, sin necesidad de flash porque se re-homea en cada encendido). Da un cero repetible del EJE DEL MOTOR por vuelta — falta combinarlo con un límite físico en un extremo del riel (switch) para tener el cero absoluto de todo el recorrido, no solo por vuelta. Pendiente: diseñar/imprimir la pieza física (medir diámetro real del eje) y validar en el motor real.
- [ ] Evaluar si esto debe resolverse por hardware (sensor absoluto o de home) o si basta con un procedimiento de calibración manual al inicio de cada sesión de ensayo, documentado en el protocolo de validación.
