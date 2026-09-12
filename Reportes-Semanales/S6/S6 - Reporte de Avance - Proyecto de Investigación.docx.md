**REPORTE DE AVANCE – PROYECTO DE INVESTIGACIÓN EN LIBRA**

| INFORMACIÓN GENERAL | |
| :---- | :---- |
| Título del Proyecto | Diseño e integración de una plataforma móvil que incluya sensores para medir variables cinemáticas y cinéticas en un simulador de marcha para validar prótesis transtibiales |
| Nombre del alumno/a | Alessandro Jesus Felix Tello |
| Nombre del asesor/a | Dante Angel Elias Giordano |
| Laboratorio de Investigación | Laboratorio de Investigación en Biomecánica y Robótica Aplicada |
| Fecha de entrega | 11/09/2026 |

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
| A1: Transmisión WiFi del BNO055 y corrección de bug en la librería | OE2 | Sketches de ESP32 con transmisión UDP en modo Access Point propio; se encontró que `DFRobot_BNO055` reinicializaba el bus I2C en cada lectura, rompiendo la comunicación | Bug corregido en el código fuente de la librería; transmisión WiFi funcional y estable |
| A2: Validación de ruido del sensor y elección de filtro | OE2/OE3 | Registro a CSV con cálculo de desviación estándar en pruebas "sensor quieto"; comparación de opciones de filtrado (EMA, complementario, Kalman) | Se eligió un filtro EMA por ser suficiente y mucho más simple que Kalman, dado que el BNO055 ya fusiona internamente |
| A3: Mejora de precisión del cero absoluto y calibración de acelerómetro | OE2/OE4 | Captura de cero con más muestras y rechazo si el sensor se movió; calibración de acelerómetro de 6 posturas estáticas aplicada al chip | Cero de referencia más confiable; calibración persiste en la flash del ESP32, no hay que repetirla en cada sesión |
| A4: Avance del diseño del pylon y registro de montaje de electrónica | OE1 | Actualización del bloque superior del pylon (versión preliminar vs. actual) en Fusion 360; vista del montaje de ESP32 y módulo adicional bajo la plataforma | Avance visual documentado; falta detallar los cambios específicos entre versiones e imprimir/probar |

**Situaciones surgidas en el desarrollo del proyecto**

No se presentaron situaciones adversas esta semana.
