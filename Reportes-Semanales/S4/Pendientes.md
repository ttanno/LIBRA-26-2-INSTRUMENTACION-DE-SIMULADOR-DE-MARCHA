# Pendientes — Semana 4 (abierto 22/08/2026)

Nota de trabajo informal (no es parte de los reportes formales). Continúa el mismo formato de `Reportes-Semanales/S3/Pendientes.md`, que quedó cerrado como histórico — retoma lo que seguía abierto de la S3 y suma lo nuevo de la S4 (pruebas de IMU y prototipos de homing).

## Referencia de posición absoluta de la plataforma (foco de esta semana)

- [x] Estado del arte de arquitecturas de referencia absoluta sin goniómetro documentado (`Estado-del-arte/REFERENCIA DE POSICION ABSOLUTA/Arquitecturas-Referencia-Absoluta-sin-Goniometro.md`).
- [x] Prototipo de homing del pivote por acelerómetro escrito, con comandos de fijar/borrar cero y persistencia en flash (`Firmware/homing_absoluto/homing_absoluto.ino`) y visor con control remoto (`visor_homing.py`).
- [x] Montaje físico inicial del IMU sobre el pylon real de la plataforma (foto evidencia en `Evidencias/pruebas-imu-S4/`) — primer paso hacia validar en hardware real.
- [ ] Validar cuantitativamente el homing en el pylon real: confirmar que el cero mecánico ("pylon perfectamente vertical") corresponde a una orientación reconocible respecto a la gravedad, y registrar los datos (no solo el montaje físico).
- [x] Prototipo de homing del eje del husillo por sensor Hall + imán escrito (`Firmware/homing_husillo_hall/homing_husillo_hall.ino`), probado solo a nivel de firmware.
- [ ] Medir el diámetro real del eje del motor (calibre) y diseñar/imprimir el collarín con el imán de neodimio.
- [ ] Montar el sensor Hall + collarín y validar el homing en el motor real (desacoplado del husillo primero, por seguridad).
- [ ] Definir y combinar con un límite físico de fin de carrera del riel (switch mecánico/óptico/Hall) para tener el cero absoluto de todo el recorrido, no solo por vuelta del motor.
- [ ] Evaluar si conviene además una marca/pin mecánico de refuerzo para el homing del pivote, en caso el nivelado por gravedad resulte problemático en la práctica.

## Pruebas de IMU (BNO055 y MPU6050)

- [x] BNO055: prueba base de comunicación I2C y orientación (`Firmware/test_bno055/test_bno055.ino`).
- [x] BNO055: sketch de sobremuestreo para reducir ruido aleatorio (`Firmware/test_bno055_oversampling/test_bno055_oversampling.ino`), verificado cualitativamente contra una regla (fotos en `Evidencias/pruebas-imu-S4/`).
- [ ] BNO055: validación cuantitativa del sobremuestreo — desviación estándar crudo vs. promediado (~30 s cada uno) y comparar contra `std_crudo / sqrt(N_SAMPLES)`.
- [x] MPU6050: prueba base con filtro complementario propio y demostración de deriva del yaw sin corregir (`Firmware/test_mpu6050/test_mpu6050.ino`).
- [ ] Prueba lado a lado BNO055 vs. MPU6050 sobre el mismo movimiento (los dos visores en paralelo), para confirmar la decisión de la S3 (MPU6050 como candidato final de IMU).
- [ ] Confirmar el MPU6050 contra el inventario del laboratorio (heredado S1/S3 — sigue abierto, ver sección de abajo).

## Selección de sensor de fuerza del pylon — heredado, sin avance esta semana

- [ ] Elegir una candidata final de la comparativa (celda propia escalada vs. FUTEK LCM300 vs. otras opciones) y cerrar el pedido/cotización.
- [ ] Cerrar la búsqueda de marcas/proveedores peruanos (sigue sin candidato local).
- [ ] Definir el ADC final para la celda: ADS1256 (compartido con la AMTI) vs. HX711 (dedicado).
- [ ] Verificar que la candidata elegida cumple el margen ~1.5–2× sobre la carga última P5 (4480 N).

## Diseño mecánico del pylon — heredado, sin avance esta semana

- [ ] Diseñar el bracket/adaptador para montar la celda de carga elegida en el punto de anclaje del simulador.
- [ ] Boceto físico de la ubicación real de la celda (no solo el diagrama lógico de bloques).
- [ ] Validación estructural del bracket/placa en Fusion 360 (Static Stress Simulation) — sigue abierto desde la S1.
- [ ] Caso de carga puntual ~1200 N (observación de la S3, 26/08) — simulación con carga concentrada en el punto más desfavorable de la placa/bracket, todavía sin correr.

## Sensores de distancia y ángulo — heredado, cerrar BOM

- [ ] Elegir sensor final de traslación (TF-Luna) y de rotación (AS5600), y cerrar el BOM de sensores.

## Heredado de la S1 — bibliografía (sigue abierto)

- [ ] [2] Confirmar autor/año exacto de la tesis de maestría (R. Davis, Cleveland State Univ.) contra OhioLINK — accession `csu1396786747`.
- [ ] [4] Nie et al. — documento IEEE no indexado en las búsquedas realizadas; requiere acceso directo a IEEE Xplore.
- [ ] [12] "Evaluating shear and normal force with the use of an instrumented transtibial socket" — sin autor identificado.
- [ ] [15] "Instrumented socket inserts for sensing interaction at the limb-socket interface" — sin autor identificado.
- [ ] P3 y P6 de ISO 10328 sin verificación confiable — no priorizar salvo que el proyecto deba cubrir usuarios >100 kg.
- [ ] Decidir el alcance de sensores de presión distribuida (FSR array) vs. solo celda de carga puntual, y ajustar la Secc. 6 de la revisión bibliográfica en consecuencia.
- [ ] Actualizar Secc. 4.1, 9 y 10 de la revisión bibliográfica con el cambio de prioridad GRF/pylon y la arquitectura de sensores por DOF (pendiente desde la S2).

## Heredado de la S1/S2/S3 — plataforma AMTI (sigue abierto)

- [ ] Confirmar el modo de salida analógica configurado actualmente en el amplificador (MSA-6 Compatible vs. Fully Conditioned) sin alterar la configuración compartida del laboratorio.
- [ ] Ubicar el certificado de calibración real de la plataforma (matriz de sensibilidad real, no la de ejemplo del manual).
- [ ] Seguimiento del formulario de soporte técnico enviado a AMTI (sin respuesta aún).
- [ ] Diseñar la interfaz de lectura de los 6 canales de la AMTI con el ADS1256.
- [ ] Confirmar qué es exactamente "V1350 YP-05" en el inventario — nombre no identificado con certeza.
- [ ] Preguntar al asesor si el motor paso a paso de la plataforma tiene retroalimentación real (encoder en el eje) o es solo conteo de pasos en lazo abierto.

## Sin dueño claro — verificar antes de cerrar la semana

- [ ] Confirmación formal del asesor sobre el simulador existente (transtibial únicamente, estructura ya construida) — sigue informal desde la S1.
