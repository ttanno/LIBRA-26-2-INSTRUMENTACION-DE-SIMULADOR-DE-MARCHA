**REPORTE DE AVANCE – PROYECTO DE INVESTIGACIÓN EN LIBRA**

| INFORMACIÓN GENERAL | |
| :---- | :---- |
| Título del Proyecto | Diseño e integración de una plataforma móvil que incluya sensores para medir variables cinemáticas y cinéticas en un simulador de marcha para validar prótesis transtibiales |
| Nombre del alumno/a | Alessandro Jesus Felix Tello |
| Nombre del asesor/a | Dante Angel Elias Giordano |
| Laboratorio de Investigación | Laboratorio de Investigación en Biomecánica y Robótica Aplicada |
| Fecha de entrega | 18/09/2026 |

**Objetivos (general y específicos) del proyecto de investigación ejecutado en LIBRA**

| Objetivo | Nivel Avance (%) |
| :---- | :---- |
| OG: Diseñar e integrar una plataforma móvil instrumentada con sensores para medir variables cinemáticas y cinéticas en un simulador de marcha, para apoyar la validación experimental de prótesis transtibiales | 31% *(propuesto — ajustar según tu criterio)* |
| OE1: Diseño Mecánico — diseñar la plataforma móvil considerando los requerimientos mecánicos y funcionales del simulador | 21% *(propuesto — ajustar según tu criterio, sin avance esta semana)* |
| OE2: Sistema Electrónico — seleccionar e integrar sensores y sistema electrónico de adquisición y procesamiento | 41% *(propuesto — ajustar según tu criterio)* |
| OE3: Software — desarrollar el software para sincronizar, visualizar, registrar y gestionar los datos del sistema | 16% *(propuesto — ajustar según tu criterio)* |
| OE4: Validación — calibrar y validar la plataforma mediante pruebas experimentales | 10% *(propuesto — ajustar según tu criterio)* |

**Resultados del proyecto de investigación ejecutado en LIBRA**

| Resultado | Nivel Avance (%) |
| :---- | :---- |
| R1: Plataforma diseñada e integrada al simulador | 18% *(propuesto — ajustar según tu criterio, sin avance esta semana)* |
| R2: Sistema de sensores (cinemáticos y cinéticos) operativo | 29% *(propuesto — ajustar según tu criterio)* |
| R3: Sistema electrónico de adquisición de datos en tiempo real | 15% *(propuesto — ajustar según tu criterio)* |
| R4: Software de monitoreo, almacenamiento y visualización | 7% *(propuesto — ajustar según tu criterio)* |

**Síntesis de lo ejecutado durante la semana**

| Actividad | Objetivo | Descripción | Resultados |
| :---- | :---- | :---- | :---- |
| A1: Filtro EMA embebido y chequeo de salud de conexión (BNO055) | OE2/OE3 | Filtro de suavizado movido de post-procesamiento a firmware, con corrección circular; chequeo automático de desviación estándar cada ~5 s con umbral basado en datos reales | Suavizado en tiempo real disponible; alerta automática ante ruido alto/conector flojo |
| A2: Bug de inicialización del filtro y hallazgo de conector flojo | OE2 | Comparación de dato crudo vs. filtrado con herramienta nueva; comparación de ruido por tanda de prueba a lo largo del día | Filtro arranca en 0° (transitorio de ~30 muestras, fix anotado en código); salto de ruido asociado a conector flojo identificado, pendiente de confirmar |
| A3: Intento de completar calibración de acelerómetro (offset + radius) | OE2/OE4 | Escritura del registro `ACC_RADIUS` (no expuesto por la librería), complemento al offset ya calibrado en la S6 | Cambio experimental aplicado; efecto sobre `calib_accel` pendiente de confirmar con nueva tanda de pruebas |
| A4: Primera prueba física del sensor de fuerza (HX711) | OE2/OE4 | Driver de prueba en paralelo al ADS1256 (que muestra ruido tipo diente de sierra); calibración con tara + masa patrón de 2 kg, verificada con una segunda masa | Calibración funcional y consistente con las masas de prueba; sirve de diagnóstico para aislar el problema del ADS1256 |
| A5: Pinout de la placa superior (primer documento de PCB) | OE1/OE2 | Arquitectura de conexionado completa: ESP32 + 2 sensores ToF + entrada del sensor de fuerza, con bus I2C dedicado para el BNO055 en placa aparte | Asignación de pines definida, evitando pines críticos de arranque del ESP32; falta el sketch de prueba de los ToF |

**Situaciones surgidas en el desarrollo del proyecto**

No se presentaron situaciones adversas que bloquearan el avance. Quedan dos hallazgos técnicos sin cerrar del todo: el bug de inicialización del filtro EMA (fix anotado en el código, sin confirmar con una nueva prueba) y el salto de ruido asociado a un conector flojo del BNO055 (sin identificar el cable/conector específico todavía).
