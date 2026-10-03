**REPORTE DE AVANCE – PROYECTO DE INVESTIGACIÓN EN LIBRA**

| INFORMACIÓN GENERAL | |
| :---- | :---- |
| Título del Proyecto | Diseño e integración de una plataforma móvil que incluya sensores para medir variables cinemáticas y cinéticas en un simulador de marcha para validar prótesis transtibiales |
| Nombre del alumno/a | Alessandro Jesus Felix Tello |
| Nombre del asesor/a | Dante Angel Elias Giordano |
| Laboratorio de Investigación | Laboratorio de Investigación en Biomecánica y Robótica Aplicada |
| Fecha de entrega | 02/10/2026 |

**Objetivos (general y específicos) del proyecto de investigación ejecutado en LIBRA**

| Objetivo | Nivel Avance (%) |
| :---- | :---- |
| OG: Diseñar e integrar una plataforma móvil instrumentada con sensores para medir variables cinemáticas y cinéticas en un simulador de marcha, para apoyar la validación experimental de prótesis transtibiales | 36% *(propuesto — ajustar según tu criterio)* |
| OE1: Diseño Mecánico — diseñar la plataforma móvil considerando los requerimientos mecánicos y funcionales del simulador | 23% *(propuesto — ajustar según tu criterio)* |
| OE2: Sistema Electrónico — seleccionar e integrar sensores y sistema electrónico de adquisición y procesamiento | 50% *(propuesto — ajustar según tu criterio)* |
| OE3: Software — desarrollar el software para sincronizar, visualizar, registrar y gestionar los datos del sistema | 17% *(propuesto — ajustar según tu criterio)* |
| OE4: Validación — calibrar y validar la plataforma mediante pruebas experimentales | 20% *(propuesto — ajustar según tu criterio)* |

**Resultados del proyecto de investigación ejecutado en LIBRA**

| Resultado | Nivel Avance (%) |
| :---- | :---- |
| R1: Plataforma diseñada e integrada al simulador | 22% *(propuesto — ajustar según tu criterio)* |
| R2: Sistema de sensores (cinemáticos y cinéticos) operativo | 37% *(propuesto — ajustar según tu criterio)* |
| R3: Sistema electrónico de adquisición de datos en tiempo real | 21% *(propuesto — ajustar según tu criterio)* |
| R4: Software de monitoreo, almacenamiento y visualización | 8% *(propuesto — ajustar según tu criterio)* |

**Síntesis de lo ejecutado durante la semana**

| Actividad | Objetivo | Descripción | Resultados |
| :---- | :---- | :---- | :---- |
| A1: Diagnóstico y reparación del BNO055 | OE2 | Aislamiento sistemático de 3 fallas encadenadas: brownout de alimentación, pinout I2C, cable en pin INT | Conexión estable restaurada; causa raíz documentada |
| A2: Calibración de 6 posiciones del acelerómetro | OE2/OE4 | Offset guardado en flash del ESP32 | `Calib[accel,mag]` de 0/3 a 3/3 |
| A3: Prueba de linealidad 0-60° (subida/bajada) | OE4 | 13 ángulos × 3 repeticiones × 2 direcciones con soporte de arco indexado; script con disparo automático por movimiento+quietud | R²>0.999 ambas direcciones; error de escala sistemático ~3%; histéresis pequeña (+0.18°±0.44°) |
| A4: Simulación de filtro de corrección lineal | OE2/OE4 | Corrección post-procesamiento sobre los datos de A3 | Error máximo reducido de ~2.4° a ~0.5° |
| A5: Diseño CAD preliminar del adaptador de fuerza | OE1 | Parantes + mordaza central para la celda de carga del pylon | Primer modelo 3D, pendiente definir patrón de pernos y holguras |

**Situaciones surgidas en el desarrollo del proyecto**

| Eventos | Fecha de Ocurrencia | Actividad Afectada | Acciones Tomadas |
| :---- | :---- | :---- | :---- |
| E1: Interrupciones intermitentes de la conexión del BNO055 (cables sueltos por el manipuleo del soporte de ángulos) | F1: 28/09/2026 – 02/10/2026 | A1: Prueba de linealidad 0-60° (subida/bajada) | Diagnóstico sistemático por puerto serial (reset manual, lectura cruda) y corrección del cableado; se repitieron las posiciones afectadas, sin perder el resultado final |
| E2: No se llegó a integrar el sensor de fuerza con el adaptador preliminar porque no se habían previsto las fuerzas de cizalla sobre la celda de carga | F2: 30/09/2026 | A2: Integración del sensor de fuerza al adaptador del pylon | Se documentó como pendiente evaluar barras guía de cizalla antes de integrar (ver `Reportes-Semanales/S9/Pendientes.md`); la integración queda para cuando esté resuelto ese punto |
