**REPORTE DE AVANCE – PROYECTO DE INVESTIGACIÓN EN LIBRA**

| INFORMACIÓN GENERAL | |
| :---- | :---- |
| Título del Proyecto | Diseño e integración de una plataforma móvil que incluya sensores para medir variables cinemáticas y cinéticas en un simulador de marcha para validar prótesis transtibiales |
| Nombre del alumno/a | Alessandro Jesus Felix Tello |
| Nombre del asesor/a | Dante Angel Elias Giordano |
| Laboratorio de Investigación | Laboratorio de Investigación en Biomecánica y Robótica Aplicada |
| Fecha de entrega | 14/08/2026 |

**Objetivos (general y específicos) del proyecto de investigación ejecutado en LIBRA**

| Objetivo | Nivel Avance (%) |
| :---- | :---- |
| OG: Diseñar e integrar una plataforma móvil instrumentada con sensores para medir variables cinemáticas y cinéticas en un simulador de marcha, para apoyar la validación experimental de prótesis transtibiales | 15% *(propuesto — ajustar según tu criterio)* |
| OE1: Diseño Mecánico — diseñar la plataforma móvil considerando los requerimientos mecánicos y funcionales del simulador | 8% |
| OE2: Sistema Electrónico — seleccionar e integrar sensores y sistema electrónico de adquisición y procesamiento | 18% |
| OE3: Software — desarrollar el software para sincronizar, visualizar, registrar y gestionar los datos del sistema | 8% |
| OE4: Validación — calibrar y validar la plataforma mediante pruebas experimentales | 5% |

**Resultados del proyecto de investigación ejecutado en LIBRA**

| Resultado | Nivel Avance (%) |
| :---- | :---- |
| R1: Plataforma diseñada e integrada al simulador | 5% *(propuesto — ajustar según tu criterio)* |
| R2: Sistema de sensores (cinemáticos y cinéticos) operativo | 8% |
| R3: Sistema electrónico de adquisición de datos en tiempo real | 8% |
| R4: Software de monitoreo, almacenamiento y visualización | 0% |

**Síntesis de lo ejecutado durante la semana**

| Actividad | Objetivo | Descripción | Resultados |
| :---- | :---- | :---- | :---- |
| A1: Reunión con el asesor — arquitectura de sensores | OE1-OE3 | Definición de un sensor dedicado por grado de libertad: GRF (plataforma de fuerza, prioridad), pylon (celda de carga, secundaria), traslación (láser), rotación (encoder) | Arquitectura de sensado por DOF confirmada; invierte la prioridad GRF/pylon que se tenía en la semana 1 |
| A2: Confirmación del equipo existente | OE2 | Verificación de que el laboratorio ya cuenta con la plataforma de fuerza AMTI BP400600 y su amplificador | Elimina la necesidad de seleccionar/adquirir una plataforma de fuerza nueva |
| A3: Investigación de integración de la plataforma de fuerza | OE2, OE3 | Identificación de la salida analógica del amplificador (independiente del software oficial), su pinout y las fórmulas de conversión de voltaje a fuerza | Camino de lectura en tiempo real definido, compatible con adquisición sincronizada y un eventual lazo de control |
| A4: Aclaración del rol del IMU | OE2 | Definición del IMU como validación cruzada del encoder de rotación, no como medición primaria de ángulo | Arquitectura de sensores de posición/rotación cerrada (láser + encoder + IMU) |
| A5: Comparación de costo — conectar vs. construir | OE1, OE2 | Análisis de costo/tiempo entre integrar la plataforma de fuerza existente y construir una nueva | Justificación documentada para priorizar la integración del equipo existente |

**Situaciones surgidas en el desarrollo del proyecto**

| Eventos | Fecha de Ocurrencia | Actividad Afectada | Acciones Tomadas |
| :---- | :---- | :---- | :---- |
| E1: Documentación de operación de AMTI no cubre acceso analógico ni fórmulas de conversión | 13/08/2026 | A3: Investigación de integración | Se obtuvo el manual técnico completo del amplificador (Gen 5 User Manual) por fuera del material del laboratorio; pinout y fórmulas confirmados contra fuente oficial |
| E2: No es posible cambiar la configuración del amplificador sin afectar a otros usuarios del laboratorio | 14/08/2026 | A3: Investigación de integración | Se documentó también la ruta de conversión para el modo de salida actual (MSA-6 Compatible), como alternativa a solicitar el cambio de configuración |
| E3: Formulario de soporte técnico enviado a AMTI, sin respuesta aún | 13/08/2026 | A3: Investigación de integración | Se continuó la investigación por fuentes públicas mientras se espera respuesta; pendiente de seguimiento la siguiente semana |
