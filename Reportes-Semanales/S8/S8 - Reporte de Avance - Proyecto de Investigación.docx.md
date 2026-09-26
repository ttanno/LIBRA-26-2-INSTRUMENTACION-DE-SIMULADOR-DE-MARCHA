**REPORTE DE AVANCE – PROYECTO DE INVESTIGACIÓN EN LIBRA**

| INFORMACIÓN GENERAL | |
| :---- | :---- |
| Título del Proyecto | Diseño e integración de una plataforma móvil que incluya sensores para medir variables cinemáticas y cinéticas en un simulador de marcha para validar prótesis transtibiales |
| Nombre del alumno/a | Alessandro Jesus Felix Tello |
| Nombre del asesor/a | Dante Angel Elias Giordano |
| Laboratorio de Investigación | Laboratorio de Investigación en Biomecánica y Robótica Aplicada |
| Fecha de entrega | 25/09/2026 |

**Objetivos (general y específicos) del proyecto de investigación ejecutado en LIBRA**

| Objetivo | Nivel Avance (%) |
| :---- | :---- |
| OG: Diseñar e integrar una plataforma móvil instrumentada con sensores para medir variables cinemáticas y cinéticas en un simulador de marcha, para apoyar la validación experimental de prótesis transtibiales | 34% *(propuesto — ajustar según tu criterio)* |
| OE1: Diseño Mecánico — diseñar la plataforma móvil considerando los requerimientos mecánicos y funcionales del simulador | 21% *(propuesto — ajustar según tu criterio, sin avance esta semana)* |
| OE2: Sistema Electrónico — seleccionar e integrar sensores y sistema electrónico de adquisición y procesamiento | 47% *(propuesto — ajustar según tu criterio)* |
| OE3: Software — desarrollar el software para sincronizar, visualizar, registrar y gestionar los datos del sistema | 16% *(propuesto — ajustar según tu criterio, sin avance esta semana)* |
| OE4: Validación — calibrar y validar la plataforma mediante pruebas experimentales | 15% *(propuesto — ajustar según tu criterio)* |

**Resultados del proyecto de investigación ejecutado en LIBRA**

| Resultado | Nivel Avance (%) |
| :---- | :---- |
| R1: Plataforma diseñada e integrada al simulador | 20% *(propuesto — ajustar según tu criterio)* |
| R2: Sistema de sensores (cinemáticos y cinéticos) operativo | 34% *(propuesto — ajustar según tu criterio)* |
| R3: Sistema electrónico de adquisición de datos en tiempo real | 19% *(propuesto — ajustar según tu criterio)* |
| R4: Software de monitoreo, almacenamiento y visualización | 7% *(propuesto — ajustar según tu criterio, sin avance esta semana)* |

**Síntesis de lo ejecutado durante la semana**

| Actividad | Objetivo | Descripción | Resultados |
| :---- | :---- | :---- | :---- |
| A1: PCB de la placa superior y del breakout del BNO055 | OE1/OE2 | Esquemático y vista 3D de ambas placas; conectores XH con traba en el breakout | Diseño listo, pendiente de revisión antes de fabricar |
| A2: Calibración del HX711 | OE2/OE4 | Tara + masa patrón de 2 kg, verificada con una segunda masa | Respuesta lineal y repetible confirmada |
| A3: Prueba de los 2 ToF VL53L1X | OE2/OE4 | Reasignación de dirección I2C y medición a 20/40 cm | Ambos sensores distinguen bien las distancias, error <10% |
| A4: Estado del arte (IMU y control de fuerza) | OE2 | Corrección de la comparativa de IMU; nuevo análisis de factibilidad de control con celda + IMU + AMTI | Sensor real (BNO055) documentado; factibilidad confirmada para fuerza vertical |

**Situaciones surgidas en el desarrollo del proyecto**

No se atendieron las observaciones del Dr. Elías sobre el informe de la S7, por organización de tiempo (no por un impedimento técnico); quedan como prioridad para la S9.
