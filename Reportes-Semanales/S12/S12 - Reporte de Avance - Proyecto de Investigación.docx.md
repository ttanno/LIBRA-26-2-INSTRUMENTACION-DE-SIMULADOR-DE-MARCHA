**REPORTE DE AVANCE – PROYECTO DE INVESTIGACIÓN EN LIBRA**

| INFORMACIÓN GENERAL | |
| :---- | :---- |
| Título del Proyecto | Diseño e integración de una plataforma móvil que incluya sensores para medir variables cinemáticas y cinéticas en un simulador de marcha para validar prótesis transtibiales |
| Nombre del alumno/a | Alessandro Jesus Felix Tello |
| Nombre del asesor/a | Dante Angel Elias Giordano |
| Laboratorio de Investigación | Laboratorio de Investigación en Biomecánica y Robótica Aplicada |
| Fecha de entrega | 06/11/2026 |

**Objetivos (general y específicos) del proyecto de investigación ejecutado en LIBRA**

| Objetivo | Nivel Avance (%) |
| :---- | :---- |
| OG: Diseñar e integrar una plataforma móvil instrumentada con sensores para medir variables cinemáticas y cinéticas en un simulador de marcha, para apoyar la validación experimental de prótesis transtibiales | 47% *(propuesto — ajustar según tu criterio)* |
| OE1: Diseño Mecánico — diseñar la plataforma móvil considerando los requerimientos mecánicos y funcionales del simulador | 40% *(propuesto — ajustar según tu criterio)* |
| OE2: Sistema Electrónico — seleccionar e integrar sensores y sistema electrónico de adquisición y procesamiento | 66% *(propuesto — ajustar según tu criterio)* |
| OE3: Software — desarrollar el software para sincronizar, visualizar, registrar y gestionar los datos del sistema | 20% *(propuesto — ajustar según tu criterio)* |
| OE4: Validación — calibrar y validar la plataforma mediante pruebas experimentales | 29% *(propuesto — ajustar según tu criterio)* |

**Resultados del proyecto de investigación ejecutado en LIBRA**

| Resultado | Nivel Avance (%) |
| :---- | :---- |
| R1: Plataforma diseñada e integrada al simulador | 38% *(propuesto — ajustar según tu criterio)* |
| R2: Sistema de sensores (cinemáticos y cinéticos) operativo | 47% *(propuesto — ajustar según tu criterio)* |
| R3: Sistema electrónico de adquisición de datos en tiempo real | 35% *(propuesto — ajustar según tu criterio)* |
| R4: Software de monitoreo, almacenamiento y visualización | 10% *(propuesto — ajustar según tu criterio)* |

**Síntesis de lo ejecutado durante la semana**

| Actividad | Objetivo | Descripción | Resultados |
| :---- | :---- | :---- | :---- |
| A1: Montaje de la caja de la placa | OE1 | Caja impresa fijada a la placa base del cuerpo con ganchos deslizantes; tapa con seguro | Placa alojada en el simulador sin perforar el cuerpo |
| A2: Integración del sensor de distancia | OE1, OE2 | VL53L1X en soporte impreso sobre la caja, ubicado a ≥ 40 mm del objetivo en todo el recorrido | Sensor dentro de su rango útil en toda la carrera |
| A3: Integración del IMU | OE1, OE2 | BNO055 montado en la pieza inferior de la plataforma, con cable y recorrido revisado en el ensamble | IMU en su posición final |
| A4: Ajuste de holguras | OE1 | Adaptación de las piezas impresas al cuerpo real | Piezas montadas sin forzar |
| A5: Plan de pruebas de validación | OE4 | Pruebas para ToF, IMU, integración en la galleta y sincronización con la AMTI | Protocolos listos para ejecutar |

**Situaciones surgidas en el desarrollo del proyecto**

| Eventos | Fecha de Ocurrencia | Actividad Afectada | Acciones Tomadas |
| :---- | :---- | :---- | :---- |
| E1: Simulador ocupado en la implementación del control | F1: 31/10/2026 – 06/11/2026 | Repetición de la comparación con la AMTI | Se reprograma para la próxima semana y se evalúa una sincronización por hardware (ADS1256 o pulso de disparo) |
| E2: Piezas impresas con interferencias en el cuerpo real | F2: 31/10/2026 – 06/11/2026 | A1–A3: Montaje de sensores | Se ajustaron las holguras de las piezas |
