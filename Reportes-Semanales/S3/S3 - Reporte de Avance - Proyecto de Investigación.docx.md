**REPORTE DE AVANCE – PROYECTO DE INVESTIGACIÓN EN LIBRA**

| INFORMACIÓN GENERAL | |
| :---- | :---- |
| Título del Proyecto | Diseño e integración de una plataforma móvil que incluya sensores para medir variables cinemáticas y cinéticas en un simulador de marcha para validar prótesis transtibiales |
| Nombre del alumno/a | Alessandro Jesus Felix Tello |
| Nombre del asesor/a | Dante Angel Elias Giordano |
| Laboratorio de Investigación | Laboratorio de Investigación en Biomecánica y Robótica Aplicada |
| Fecha de entrega | 21/08/2026 |

**Objetivos (general y específicos) del proyecto de investigación ejecutado en LIBRA**

| Objetivo | Nivel Avance (%) |
| :---- | :---- |
| OG: Diseñar e integrar una plataforma móvil instrumentada con sensores para medir variables cinemáticas y cinéticas en un simulador de marcha, para apoyar la validación experimental de prótesis transtibiales | 20% *(propuesto — ajustar según tu criterio)* |
| OE1: Diseño Mecánico — diseñar la plataforma móvil considerando los requerimientos mecánicos y funcionales del simulador | 15% *(propuesto — ajustar según tu criterio)* |
| OE2: Sistema Electrónico — seleccionar e integrar sensores y sistema electrónico de adquisición y procesamiento | 24% *(propuesto — ajustar según tu criterio)* |
| OE3: Software — desarrollar el software para sincronizar, visualizar, registrar y gestionar los datos del sistema | 8% *(sin cambio — no fue foco esta semana)* |
| OE4: Validación — calibrar y validar la plataforma mediante pruebas experimentales | 5% *(sin cambio — no fue foco esta semana)* |

**Resultados del proyecto de investigación ejecutado en LIBRA**

| Resultado | Nivel Avance (%) |
| :---- | :---- |
| R1: Plataforma diseñada e integrada al simulador | 12% *(propuesto — ajustar según tu criterio)* |
| R2: Sistema de sensores (cinemáticos y cinéticos) operativo | 12% *(propuesto — ajustar según tu criterio)* |
| R3: Sistema electrónico de adquisición de datos en tiempo real | 8% *(sin cambio — no fue foco esta semana)* |
| R4: Software de monitoreo, almacenamiento y visualización | 0% |

**Síntesis de lo ejecutado durante la semana**

| Actividad | Objetivo | Descripción | Resultados |
| :---- | :---- | :---- | :---- |
| A1: Comparativa de sensores por variable sensada | OE2 | Comparativa con tablas de sensores de distancia (TF-Luna vs. VL53L1X vs. Baumer OM70), ángulo (AS5600 vs. encoder óptico vs. potenciómetro) y fuerza (celda propia vs. S-type genérico vs. Transducer Techniques vs. FUTEK LCM300), documentada en `Sensores-LIBRA-Presentacion.pptx` | Distancia (TF-Luna) y ángulo (AS5600) definidos; IMU probable (MPU6050); fuerza sigue abierta, ahora buscando proveedores peruanos |
| A2: Definición de material y configuración de impresión | OE1 | Documento Excel propio con propiedades de material (PETG) y parámetros de impresión (altura de capa, paredes, patrón y % de relleno) | Insumo directo para el Engineering Data de la simulación en ANSYS |
| A3: Simulación estructural ANSYS de la placa | OE1 | Cinco corridas Static Structural sobre el mismo material, comparando espesor (15/20/25 mm sólidos) y geometría (vaciado central a 20 mm, refuerzo en cruz a 15 mm) | La placa sólida de 25 mm es la única con factor de seguridad >1 (1.15); las variantes con menos material mejoran frente a su espesor base (vaciado central: 0.92, refuerzo en cruz: 0.63) pero no cruzan el umbral todavía |

**Situaciones surgidas en el desarrollo del proyecto**

| Eventos | Fecha de Ocurrencia | Actividad Afectada | Acciones Tomadas |
| :---- | :---- | :---- | :---- |
| E1: Disyuntiva de prioridad GRF vs. pylon (Dante vs. Victoria) sigue sin resolver formalmente | Arrastrado desde el 19/08/2026 | A3 de la Semana 2 (integración AMTI) | Se avanzó en paralelo la investigación de sensores del lado del pylon sin descartar el trabajo ya hecho del lado GRF; pendiente decisión final por escrito con ambos asesores |
| E2: Factor de seguridad por debajo de 1 en la mayoría de las configuraciones de placa simuladas | 21/08/2026 | A3: Simulación estructural ANSYS | Se iteró sobre cinco configuraciones de espesor y geometría; se identificó que solo la placa sólida de 25 mm cumple el criterio, y se sigue buscando una alternativa con menos material que también lo cumpla |
