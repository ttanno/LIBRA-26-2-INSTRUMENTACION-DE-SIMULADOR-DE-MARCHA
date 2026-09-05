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

## Pruebas de IMU (BNO055 y MPU6050) — heredado, sin avance esta semana

- [ ] BNO055: validación cuantitativa del sobremuestreo — desviación estándar crudo vs. promediado.
- [ ] Prueba lado a lado BNO055 vs. MPU6050 sobre el mismo movimiento.
- [ ] Confirmar el MPU6050 (o su reemplazo Nivel A) contra el inventario del laboratorio.

## Referencia de posición absoluta — husillo (heredado, sin avance esta semana)

- [ ] Medir el diámetro real del eje del motor (calibre) y diseñar/imprimir el collarín con el imán de neodimio.
- [ ] Montar el sensor Hall + collarín y validar el homing en el motor real.
- [ ] Definir y combinar con un límite físico de fin de carrera del riel (switch mecánico/óptico/Hall).

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
