**INFORME SEMANAL DE AVANCE DEL PROYECTO DE INVESTIGACIÓN**

**Proyecto:** Diseño e integración de una plataforma móvil que incluya sensores para medir variables cinemáticas y cinéticas en un simulador de marcha para validar prótesis transtibiales

**Período del informe:** 29/08/2026 al 04/09/2026

**Responsable:** Alessandro Jesus Felix Tello

**1. Resumen Ejecutivo**

Durante la quinta semana se cerró el pendiente heredado de selección de sensor de fuerza del pylon: se comparó una nueva tanda de celdas de carga y electrónica de lectura disponibles en Amazon contra los requisitos ya fijados, y se compró la celda #4 (tipo fuelle, patrón de pernos 3×M4 documentado), en la variante de 220 lb (~978 N), dimensionada para el caso de carga puntual de ~1200 N observado en la S3, no para el ensayo P5 completo. En paralelo, al usar el prototipo de homing del pivote (`homing_absoluto.ino`, S4) se detectó que el cero guardado no se repite exactamente al volver físicamente a esa posición; se investigó el problema y se documentó una comparativa de IMU de menor drift (incluyendo sensores de grado industrial y de grado espacial, a modo de referencia de costos), con recomendación de reemplazo de bajo costo (LSM6DSR o ICM-45686) combinado con un tope mecánico físico. Por último, se avanzó el diseño mecánico del bloque superior del pylon en dos versiones: una dimensionada para el sensor ya comprado, y una versión simplificada e imprimible de inmediato para no bloquear las pruebas de ajuste en el simulador. Queda pendiente confirmar con el vendedor el tipo de salida eléctrica real de la celda comprada, imprimir y probar la versión simplificada, y decidir el reemplazo de IMU.

**2. Actividades Realizadas**

1. **Comparativa de celdas de carga y electrónica de lectura.** `Comparativa-LoadCells-S5.md` compara 4 celdas de carga y 2 módulos de electrónica de Amazon contra los requisitos de la comparativa de la S4 (fuerza de prueba P5 = 2240 N, última = 4480 N, interfaz de placa atornillada). Resultado: la opción #4 (fuelle, 3×M4) es la única con el patrón de pernos confirmado en ficha; se confirma también la disponibilidad del ADS1256 ya decidido, comprable con envío a Perú (~US$27).

2. **Compra de la celda de carga.** Se adquirió la opción #4 en la variante de 220 lb (~978 N), dimensionada para el caso de carga puntual de ~1200 N (observación de la S3), no para el ensayo P5 completo. Resultado: sensor en camino; queda pendiente confirmar con el vendedor si la salida eléctrica es mV/V cruda o "Push-Pull" (posible incompatibilidad directa con el ADS1256).

3. **Comparativa de IMU de bajo drift.** A partir del problema detectado de repetibilidad del homing del pivote, `Comparativa-IMU-Bajo-Drift.md` diagnostica tres causas posibles (bias sistemático del acelerómetro, deriva del giroscopio, holgura mecánica) y compara alternativas de IMU por nivel de costo (consumer, industrial/táctico, grado espacial). Resultado: recomendación de reemplazar el MPU6050 por un LSM6DSR o ICM-45686 (mismo bus I2C, unos pocos dólares) combinado con un tope mecánico físico de referencia; se descarta explícitamente el nivel industrial/táctico y el de grado espacial por costo desproporcionado frente al problema real.

4. **Diseño de la versión final del bloque superior del pylon.** Bloque con el patrón de agujeros dimensionado para la celda de carga comprada (pernos de montaje 3×M4 y agujeros adicionales de cableado/alineación), apoyado sobre la transición cónica hacia el resto del pylon. Resultado: geometría lista; falta validación estructural en Fusion 360 (Static Stress Simulation) de esta versión específica.

5. **Diseño de la versión imprimible del bloque superior del pylon.** Misma huella general que la versión final, pero con insertos roscados (heat-set) y tornillos como referencia mecánica temporal, sin el cuerpo del sensor real. Resultado: geometría lista para imprimir de inmediato, pensada para no bloquear las pruebas de ajuste/ensamblaje en el simulador mientras se espera la llegada física de la celda comprada.

**3. Actividades Planificadas vs. Actividades Ejecutadas**

| Actividad Planificada | Estado (Ejecutada / En proceso / No ejecutada) | Comentarios (justificación si aplica) |
| :---- | :---- | :---- |
| Validar cuantitativamente el homing del pivote con el IMU montado en el pylon real | No ejecutada | Se priorizó diagnosticar la causa del problema de repetibilidad detectado (comparativa de IMU) antes de repetir la validación |
| Correr la prueba lado a lado BNO055 vs. MPU6050 y cerrar la decisión de IMU | No ejecutada | Sin avance esta semana; la decisión de IMU ahora depende también de si se cambia a un chip de menor drift |
| Medir el eje del motor del husillo, diseñar/imprimir el collarín e imán, y validar el homing Hall en el motor real | No ejecutada | Sin avance esta semana |
| Definir el límite físico de fin de carrera del riel | No ejecutada | Sin avance esta semana |
| Retomar el diseño final de la placa y la búsqueda de sensor de fuerza en proveedores peruanos | En proceso | Se cerró la compra del sensor (Amazon, no proveedor peruano) y se avanzó el diseño del bloque superior en dos versiones; falta la validación estructural |
| *(no planificada)* Comparativa de IMU de bajo drift | Ejecutada | Trabajo adicional a partir del problema de repetibilidad del homing detectado esta semana |

**4. Dificultades o Problemas Presentados**

**Repetibilidad del homing del pivote (nuevo, en trabajo).** Al fijar el cero del pivote y volver físicamente a esa misma posición, el ángulo reportado por el MPU6050 no coincide exactamente con el cero guardado. Se identificaron tres causas posibles (bias sistemático del acelerómetro, deriva del giroscopio, holgura mecánica del pivote) y se investigó una comparativa de IMU de menor drift, pero el reemplazo de sensor y/o el tope mecánico de refuerzo todavía no se han implementado ni validado.

**Ambigüedad de la salida eléctrica de la celda de carga comprada.** La ficha del producto especifica "Push-Pull" como tipo de salida, lo que normalmente describe una etapa digital/de conmutación y no un puente de Wheatstone crudo (mV/V) — esto podría no ser compatible directo con el ADS1256 ya decidido. Queda pendiente confirmarlo con el vendedor antes de integrar la celda al banco de pruebas.

**5. Lecciones Aprendidas / Recomendaciones**

Ante un problema de repetibilidad de un sensor, conviene separar explícitamente las causas posibles (bias sistemático, deriva por integración, holgura mecánica) antes de asumir que la solución es solo "comprar un mejor sensor" — en este caso, ni siquiera un IMU de grado espacial corrige la holgura mecánica del pivote si esa fuera la causa dominante, y la solución más barata (un tope físico de referencia) resultó ser la misma que ya se había identificado como pendiente desde la S4. También se confirmó el valor de avanzar una versión simplificada e imprimible de una pieza en paralelo a la versión final dimensionada a un componente comprado: permite seguir con las pruebas físicas del simulador sin quedar bloqueado por el tiempo de envío del componente real.

**6. Actividades Planificadas para la Siguiente Semana**

| Actividad | Objetivo |
| :---- | :---- |
| Confirmar con el vendedor el tipo de salida eléctrica real de la celda comprada y su compatibilidad con el ADS1256 | Objetivo específico 2 |
| Imprimir la versión imprimible del bloque superior del pylon y correr pruebas de ajuste/ensamblaje en el simulador | Objetivo específico 1 y 4 |
| Correr la validación estructural en Fusion 360 (Static Stress Simulation) de la versión final del bloque, incluyendo el caso de carga puntual ~1200 N | Objetivo específico 1 |
| Decidir y comprar el reemplazo de IMU de bajo costo (LSM6DSR o ICM-45686) y diseñar un tope mecánico de referencia para el pivote | Objetivo específico 2 y 3 |
| Repetir la validación cuantitativa del homing del pivote una vez cambiado el IMU y/o agregado el tope mecánico | Objetivo específico 3 y 4 |

**7. Anexos o Evidencias**

Documento `Reportes-Semanales/S5/Resumen-Semana5.md` (resumen narrativo con el detalle técnico completo). Comparativas en `Reportes-Semanales/S5/Comparativa-LoadCells-S5.md` y `Estado-del-arte/REFERENCIA DE POSICION ABSOLUTA/Comparativa-IMU-Bajo-Drift.md`. Imágenes de las dos versiones del diseño del bloque superior del pylon en `Evidencias/diseno-pylon-S5/`. Lista de trabajo activa en `Reportes-Semanales/S5/Pendientes.md`.
