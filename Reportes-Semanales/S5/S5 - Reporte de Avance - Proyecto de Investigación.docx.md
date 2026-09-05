**REPORTE DE AVANCE – PROYECTO DE INVESTIGACIÓN EN LIBRA**

| INFORMACIÓN GENERAL | |
| :---- | :---- |
| Título del Proyecto | Diseño e integración de una plataforma móvil que incluya sensores para medir variables cinemáticas y cinéticas en un simulador de marcha para validar prótesis transtibiales |
| Nombre del alumno/a | Alessandro Jesus Felix Tello |
| Nombre del asesor/a | Dante Angel Elias Giordano |
| Laboratorio de Investigación | Laboratorio de Investigación en Biomecánica y Robótica Aplicada |
| Fecha de entrega | 04/09/2026 |

**Objetivos (general y específicos) del proyecto de investigación ejecutado en LIBRA**

| Objetivo | Nivel Avance (%) |
| :---- | :---- |
| OG: Diseñar e integrar una plataforma móvil instrumentada con sensores para medir variables cinemáticas y cinéticas en un simulador de marcha, para apoyar la validación experimental de prótesis transtibiales | 29% *(propuesto — ajustar según tu criterio)* |
| OE1: Diseño Mecánico — diseñar la plataforma móvil considerando los requerimientos mecánicos y funcionales del simulador | 21% *(propuesto — ajustar según tu criterio)* |
| OE2: Sistema Electrónico — seleccionar e integrar sensores y sistema electrónico de adquisición y procesamiento | 36% *(propuesto — ajustar según tu criterio)* |
| OE3: Software — desarrollar el software para sincronizar, visualizar, registrar y gestionar los datos del sistema | 14% *(propuesto — ajustar según tu criterio)* |
| OE4: Validación — calibrar y validar la plataforma mediante pruebas experimentales | 8% *(propuesto — ajustar según tu criterio)* |

**Resultados del proyecto de investigación ejecutado en LIBRA**

| Resultado | Nivel Avance (%) |
| :---- | :---- |
| R1: Plataforma diseñada e integrada al simulador | 18% *(propuesto — ajustar según tu criterio)* |
| R2: Sistema de sensores (cinemáticos y cinéticos) operativo | 24% *(propuesto — ajustar según tu criterio)* |
| R3: Sistema electrónico de adquisición de datos en tiempo real | 10% *(propuesto — ajustar según tu criterio)* |
| R4: Software de monitoreo, almacenamiento y visualización | 5% *(propuesto — ajustar según tu criterio)* |

**Síntesis de lo ejecutado durante la semana**

| Actividad | Objetivo | Descripción | Resultados |
| :---- | :---- | :---- | :---- |
| A1: Comparativa de celdas de carga y electrónica de lectura | OE2 | Comparación de 4 celdas de carga y 2 módulos de electrónica de Amazon contra los requisitos P5 (2240/4480 N) e interfaz de placa atornillada, fijados en la comparativa de la S4 | Opción #4 (fuelle, 3×M4) identificada como la única con patrón de pernos confirmado en ficha; disponibilidad del ADS1256 confirmada (~US$27 con envío) |
| A2: Compra de la celda de carga | OE1/OE2 | Adquisición de la opción #4, variante 220 lb (~978 N), dimensionada para el caso de carga puntual ~1200 N (S3) | Sensor en camino; pendiente confirmar con el vendedor el tipo de salida eléctrica real y su compatibilidad con el ADS1256 |
| A3: Comparativa de IMU de bajo drift | OE2/OE3 | Diagnóstico de las causas del problema de repetibilidad del homing (bias del acelerómetro, deriva del giroscopio, holgura mecánica) y comparativa de IMU por nivel de costo (consumer, industrial/táctico, grado espacial) | Recomendación de reemplazar el MPU6050 por LSM6DSR o ICM-45686, combinado con un tope mecánico de referencia; se descartan las opciones industrial/táctico y grado espacial por costo desproporcionado |
| A4: Diseño de la versión final del bloque superior del pylon | OE1 | Bloque con patrón de agujeros dimensionado para la celda de carga comprada (pernos 3×M4 + agujeros de cableado/alineación) | Geometría lista; falta validación estructural en Fusion 360 (Static Stress Simulation) |
| A5: Diseño de la versión imprimible del bloque superior del pylon | OE1 | Misma huella que la versión final, con insertos roscados y tornillos como referencia mecánica temporal, sin el cuerpo del sensor real | Geometría lista para imprimir de inmediato; permite avanzar pruebas de ajuste en el simulador sin esperar la llegada del sensor comprado |

**Situaciones surgidas en el desarrollo del proyecto**

| Eventos | Fecha de Ocurrencia | Actividad Afectada | Acciones Tomadas |
| :---- | :---- | :---- | :---- |
| E1: Repetibilidad del homing del pivote — el cero guardado no coincide exactamente al volver a esa posición física | Detectado durante la S5 (semana del 29/08 al 04/09/2026), usando `homing_absoluto.ino` (S4) | A3: comparativa de IMU de bajo drift | Se diagnosticaron tres causas posibles y se comparó una alternativa de IMU de bajo costo (LSM6DSR/ICM-45686) combinada con un tope mecánico; no implementado aún, queda como prioridad de la próxima semana |
| E2: Ambigüedad de la salida eléctrica de la celda de carga comprada ("Push-Pull" en ficha, posible incompatibilidad con el ADS1256) | 31/08/2026 (identificado en `Comparativa-LoadCells-S5.md`) | A1 y A2: selección y compra de la celda de carga | Documentado como pendiente prioritario; se debe confirmar con el vendedor antes de integrar la celda al banco de pruebas |
