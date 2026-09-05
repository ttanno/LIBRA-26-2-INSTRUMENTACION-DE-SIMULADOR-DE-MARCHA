**REPORTE DE AVANCE – PROYECTO DE INVESTIGACIÓN EN LIBRA**

| INFORMACIÓN GENERAL | |
| :---- | :---- |
| Título del Proyecto | Diseño e integración de una plataforma móvil que incluya sensores para medir variables cinemáticas y cinéticas en un simulador de marcha para validar prótesis transtibiales |
| Nombre del alumno/a | Alessandro Jesus Felix Tello |
| Nombre del asesor/a | Dante Angel Elias Giordano |
| Laboratorio de Investigación | Laboratorio de Investigación en Biomecánica y Robótica Aplicada |
| Fecha de entrega | 28/08/2026 |

**Objetivos (general y específicos) del proyecto de investigación ejecutado en LIBRA**

| Objetivo | Nivel Avance (%) |
| :---- | :---- |
| OG: Diseñar e integrar una plataforma móvil instrumentada con sensores para medir variables cinemáticas y cinéticas en un simulador de marcha, para apoyar la validación experimental de prótesis transtibiales | 26% *(propuesto — ajustar según tu criterio)* |
| OE1: Diseño Mecánico — diseñar la plataforma móvil considerando los requerimientos mecánicos y funcionales del simulador | 17% *(propuesto — ajustar según tu criterio)* |
| OE2: Sistema Electrónico — seleccionar e integrar sensores y sistema electrónico de adquisición y procesamiento | 32% *(propuesto — ajustar según tu criterio)* |
| OE3: Software — desarrollar el software para sincronizar, visualizar, registrar y gestionar los datos del sistema | 14% *(propuesto — ajustar según tu criterio)* |
| OE4: Validación — calibrar y validar la plataforma mediante pruebas experimentales | 8% *(propuesto — ajustar según tu criterio)* |

**Resultados del proyecto de investigación ejecutado en LIBRA**

| Resultado | Nivel Avance (%) |
| :---- | :---- |
| R1: Plataforma diseñada e integrada al simulador | 14% *(propuesto — ajustar según tu criterio)* |
| R2: Sistema de sensores (cinemáticos y cinéticos) operativo | 20% *(propuesto — ajustar según tu criterio)* |
| R3: Sistema electrónico de adquisición de datos en tiempo real | 10% *(propuesto — ajustar según tu criterio)* |
| R4: Software de monitoreo, almacenamiento y visualización | 5% *(propuesto — ajustar según tu criterio)* |

**Síntesis de lo ejecutado durante la semana**

| Actividad | Objetivo | Descripción | Resultados |
| :---- | :---- | :---- | :---- |
| A1: Prueba base y sobremuestreo del BNO055 | OE2 | Sketch de verificación I2C/orientación y sketch adicional que promedia N lecturas (vector seno/coseno) para reducir ruido aleatorio sin hardware extra | Comunicación y orientación confirmadas; seguimiento consistente del ángulo verificado contra una regla (cualitativo); falta la validación cuantitativa (desviación estándar) |
| A2: Prueba del MPU6050 con filtro complementario | OE2 | Sketch con filtro complementario propio (acelerómetro + giroscopio) y demostración deliberada de la deriva del yaw sin magnetómetro | Roll/pitch estables vía filtro; confirmado el rol de validación cruzada del sensor, no medición primaria |
| A3: Estado del arte de referencia de posición absoluta sin goniómetro | OE3/OE4 | Revisión de homing en CNC/impresoras 3D, mastering de robots industriales, y referencias de laboratorios de marcha (Ottobock, Vicon) | Confirma que un evento físico fijo como referencia (gravedad, imán, switch) es el patrón estándar; valida el enfoque elegido para LIBRA |
| A4: Prototipo de homing del pivote por acelerómetro | OE3 | Firmware que fija un cero absoluto persistente en flash usando la gravedad como referencia, con visor y control remoto por Serial | Sketch funcional en banco de pruebas; IMU montado por primera vez sobre el pylon real; falta validación cuantitativa en esa posición |
| A5: Prototipo de homing del husillo por sensor Hall | OE1/OE3 | Firmware de homing en dos etapas (rápida + lenta) con imán en collarín impreso y sensor Hall fijo al chasis | Firmware probado; falta medir el eje real, imprimir el collarín y validar en el motor real |

**Situaciones surgidas en el desarrollo del proyecto**

| Eventos | Fecha de Ocurrencia | Actividad Afectada | Acciones Tomadas |
| :---- | :---- | :---- | :---- |
| E1: Falta de referencia de posición absoluta persistente en la plataforma (heredado de la S3) | Detectado 26/08/2026, en trabajo esta semana | A4 y A5: prototipos de homing | Se prototiparon dos soluciones parciales (pivote por acelerómetro, husillo por sensor Hall); ninguna validada cuantitativamente aún; pendiente combinar con límite físico de fin de carrera para el recorrido completo del riel |
| E2: Falta de datos cuantitativos en las pruebas de IMU | 28/08/2026 | A1 y A4: validación del BNO055 y del homing en el pylon real | Verificación solo cualitativa por ahora (regla, inspección visual); se deja como actividad prioritaria de la próxima semana |
