**REPORTE DE AVANCE – PROYECTO DE INVESTIGACIÓN EN LIBRA**

| INFORMACIÓN GENERAL | |
| :---- | :---- |
| Título del Proyecto | Diseño e integración de una plataforma móvil que incluya sensores para medir variables cinemáticas y cinéticas en un simulador de marcha para validar prótesis transtibiales |
| Nombre del alumno/a | Alessandro Jesus Felix Tello |
| Nombre del asesor/a | Dante Angel Elias Giordano |
| Laboratorio de Investigación | Laboratorio de Investigación en Biomecánica y Robótica Aplicada |
| Fecha de entrega | 23/10/2026 |

**Objetivos (general y específicos) del proyecto de investigación ejecutado en LIBRA**

| Objetivo | Nivel Avance (%) |
| :---- | :---- |
| OG: Diseñar e integrar una plataforma móvil instrumentada con sensores para medir variables cinemáticas y cinéticas en un simulador de marcha, para apoyar la validación experimental de prótesis transtibiales | 41% *(propuesto — ajustar según tu criterio)* |
| OE1: Diseño Mecánico — diseñar la plataforma móvil considerando los requerimientos mecánicos y funcionales del simulador | 30% *(propuesto — ajustar según tu criterio)* |
| OE2: Sistema Electrónico — seleccionar e integrar sensores y sistema electrónico de adquisición y procesamiento | 60% *(propuesto — ajustar según tu criterio)* |
| OE3: Software — desarrollar el software para sincronizar, visualizar, registrar y gestionar los datos del sistema | 17% *(propuesto — ajustar según tu criterio)* |
| OE4: Validación — calibrar y validar la plataforma mediante pruebas experimentales | 20% *(propuesto — ajustar según tu criterio)* |

**Resultados del proyecto de investigación ejecutado en LIBRA**

| Resultado | Nivel Avance (%) |
| :---- | :---- |
| R1: Plataforma diseñada e integrada al simulador | 28% *(propuesto — ajustar según tu criterio)* |
| R2: Sistema de sensores (cinemáticos y cinéticos) operativo | 40% *(propuesto — ajustar según tu criterio)* |
| R3: Sistema electrónico de adquisición de datos en tiempo real | 32% *(propuesto — ajustar según tu criterio)* |
| R4: Software de monitoreo, almacenamiento y visualización | 8% *(propuesto — ajustar según tu criterio)* |

**Síntesis de lo ejecutado durante la semana**

| Actividad | Objetivo | Descripción | Resultados |
| :---- | :---- | :---- | :---- |
| A1: Placa electrónica superior terminada (galleta 70×90 mm) | OE2 | Armado de la placa provisional con ESP32, HX711, borneras (celda y 5 V) y conectores Molex KK con traba para BNO055, 2× VL53L1X y Hall, respetando el pinout de la PCB final | Placa completa, lista para verificación eléctrica e integración |
| A2: Diseño de la caja de la placa | OE1 | Bandeja con 4 standoffs (82.2×60.3 mm), 20 mm libres y ventanas para USB, borneras y cables; evaluación de varios anclajes hasta el definitivo (columnas + brida superior con M3, sin perforar el cuerpo metálico) | Modelo 3D final con soporte integrado para un VL53L1X |
| A3: Impresión 3D de la caja y la brida | OE1 | Fabricación de la versión final del diseño de A2 | Piezas impresas, pendientes de montaje en el cuerpo |

**Situaciones surgidas en el desarrollo del proyecto**

| Eventos | Fecha de Ocurrencia | Actividad Afectada | Acciones Tomadas |
| :---- | :---- | :---- | :---- |
| E1: No se puede mandar a fabricar la PCB principal por ahora | F1: 17/10/2026 – 23/10/2026 | A1: Placa electrónica superior | Se armó una placa provisional en galleta con el mismo pinout de la PCB, para no detener la integración ni cambiar el firmware después |
| E2: El cuerpo del simulador tenía partes soldadas que no se consideraron en la primera iteración del diseño de la caja | F2: 22/10/2026 – 23/10/2026 | A2: Diseño de la caja de la placa | Se descartó el primer anclaje al nervio central, que interfería con esas partes, y se rediseñó la fijación sobre la placa superior del cuerpo (columnas + brida superior), sin perforar el metal |
