**INFORME SEMANAL DE AVANCE DEL PROYECTO DE INVESTIGACIÓN**

**Proyecto:** Diseño e integración de una plataforma móvil que incluya sensores para medir variables cinemáticas y cinéticas en un simulador de marcha para validar prótesis transtibiales

**Período del informe:** 22/08/2026 al 28/08/2026

**Responsable:** Alessandro Jesus Felix Tello

**1. Resumen Ejecutivo**

Durante la cuarta semana el trabajo se concentró en firmware de sensórica: pruebas de los dos candidatos de IMU (BNO055 y MPU6050) para confirmar que entregan orientación coherente, y dos prototipos de referencia de posición absoluta para la plataforma — homing del pivote de rotación con el propio IMU (usando la gravedad como referencia) y homing del eje del husillo con un sensor Hall y un imán — a partir del problema de falta de cero absoluto detectado la semana pasada. Se documentó además un estado del arte de arquitecturas de referencia absoluta usadas en CNC, robótica industrial y laboratorios de marcha, que confirmó que el enfoque elegido (evento físico fijo como referencia) es consistente con la práctica establecida. El IMU se montó físicamente, por primera vez, sobre el pylon real de la plataforma. Queda pendiente la validación cuantitativa de ambos prototipos de homing y la decisión final entre BNO055 y MPU6050.

**2. Actividades Realizadas**

1. **Prueba base y sobremuestreo del BNO055.** Sketch de verificación I2C y orientación (`test_bno055.ino`), y sketch adicional de sobremuestreo (`test_bno055_oversampling.ino`) que promedia N lecturas para reducir ruido aleatorio sin hardware extra. Resultado: comunicación y orientación confirmadas; verificación cualitativa contra una regla mostró seguimiento consistente del ángulo físico; falta la validación cuantitativa (desviación estándar).

2. **Prueba del MPU6050 con filtro complementario.** Sketch (`test_mpu6050.ino`) que programa un filtro complementario propio (el MPU6050 no trae fusión integrada) y demuestra en vivo la deriva del yaw sin corregir por falta de magnetómetro. Resultado: roll/pitch estables vía filtro; confirmado que el rol de este sensor es de validación cruzada, no medición primaria (según arquitectura definida en la S2/S3).

3. **Estado del arte de referencia de posición absoluta.** Investigación de cómo CNC/impresoras 3D, robots industriales (FANUC/KUKA/ABB) y laboratorios de marcha (Ottobock L.A.S.A.R., Vicon Plug-in Gait) resuelven el cero absoluto sin goniómetro manual, documentada en `Estado-del-arte/REFERENCIA DE POSICION ABSOLUTA/`. Resultado: confirma que un evento físico fijo (switch, imán, postura estática) como referencia es el patrón estándar, validando el enfoque ya elegido para LIBRA.

4. **Prototipo de homing del pivote por acelerómetro.** `homing_absoluto.ino` usa el MPU6050 como referencia de gravedad para fijar un cero absoluto persistente en flash, con comandos de fijar/borrar cero y visor gráfico con control remoto (`visor_homing.py`). Resultado: sketch funcional en banco de pruebas; esta semana se montó físicamente el IMU sobre el pylon real (primera vez en hardware real, más allá del protoboard); falta la validación cuantitativa en esa posición.

5. **Prototipo de homing del husillo por sensor Hall.** `homing_husillo_hall.ino` da un cero repetible del eje del motor por vuelta, con homing en dos etapas (aproximación rápida + lenta, igual que una CNC). Resultado: firmware probado; falta medir el diámetro real del eje, diseñar/imprimir el collarín con el imán y validar en el motor real.

**3. Actividades Planificadas vs. Actividades Ejecutadas**

| Actividad Planificada | Estado (Ejecutada / En proceso / No ejecutada) | Comentarios (justificación si aplica) |
| :---- | :---- | :---- |
| Resolver formalmente con Dante y Victoria la prioridad GRF vs. pylon | No ejecutada | El foco de la semana se volcó a firmware de IMU y homing; se retoma la próxima semana |
| Definir el diseño final de la placa combinando refuerzo/vaciado con un espesor intermedio (20-25 mm) | No ejecutada | Mismo motivo; ver `Estado-del-arte/SIMULADOR DE MARCHA/` |
| Cerrar la búsqueda de sensor de fuerza en proveedores peruanos | No ejecutada | Sin avance esta semana |
| Confirmar el MPU6050 como candidato final de IMU contra el inventario del laboratorio | En proceso | Se probó el sensor en firmware; falta la comparación lado a lado con el BNO055 y la verificación de inventario |
| Confirmar el modo de salida analógica del amplificador AMTI y diseñar la interfaz de lectura con el ADS1256 | No ejecutada | Sin avance esta semana |
| Actualizar las secciones 4.1, 9 y 10 de la revisión bibliográfica | No ejecutada | Sigue pendiente desde la Semana 2 |
| *(no planificada)* Prototipos de homing (pivote por acelerómetro, husillo por sensor Hall) | Ejecutada | Trabajo adicional a partir de la observación de la S3 sobre falta de referencia absoluta |
| *(no planificada)* Estado del arte de referencia de posición absoluta sin goniómetro | Ejecutada | Trabajo adicional, insumo directo para los dos prototipos de homing |

**4. Dificultades o Problemas Presentados**

**Falta de referencia de posición absoluta en la plataforma (heredado de la S3, en trabajo).** Ningún sensor incremental (encoder relativo, conteo de pasos) resuelve por sí solo una posición física repetible tras apagar/encender el sistema. Se prototiparon dos soluciones parciales esta semana (pivote por acelerómetro, husillo por sensor Hall), pero ninguna está aún validada cuantitativamente en hardware real, y el eje de traslación todavía necesita combinarse con un límite físico de fin de carrera para cubrir el recorrido completo del riel, no solo una vuelta del motor.

**Falta de datos cuantitativos en las pruebas de IMU.** Tanto la verificación del sobremuestreo del BNO055 como el montaje del IMU sobre el pylon real se evaluaron solo de forma cualitativa esta semana (a ojo, contra una regla, o por inspección visual del montaje); falta registrar datos (desviación estándar, ángulos de referencia repetibles) antes de considerar cualquiera de las dos pruebas cerrada.

**5. Lecciones Aprendidas / Recomendaciones**

Antes de diseñar un prototipo de homing desde cero, conviene revisar cómo lo resuelven sistemas ya maduros (CNC, robots industriales, laboratorios de marcha) — en este caso confirmó que usar un evento físico fijo como referencia (gravedad para el pivote, imán fijo para el husillo) no es una solución improvisada sino el patrón estándar de la industria, lo que da mayor confianza en la dirección tomada. También quedó claro que probar un sketch en banco de protoboard y probarlo montado en el hardware real son dos pasos distintos: el montaje físico del IMU en el pylon esta semana fue solo el primero, y no reemplaza la validación cuantitativa que todavía falta.

**6. Actividades Planificadas para la Siguiente Semana**

| Actividad | Objetivo |
| :---- | :---- |
| Validar cuantitativamente el homing del pivote con el IMU ya montado en el pylon real | Objetivo específico 3 y 4 |
| Correr la prueba lado a lado BNO055 vs. MPU6050 y cerrar la decisión de IMU | Objetivo específico 2 |
| Medir el eje del motor del husillo, diseñar/imprimir el collarín con el imán y validar el homing Hall en el motor real | Objetivo específico 1 y 3 |
| Definir el límite físico de fin de carrera del riel para el cero absoluto de todo el recorrido | Objetivo específico 1 |
| Resolver formalmente con Dante y Victoria la prioridad GRF vs. pylon | Evitar seguir avanzando sobre un frente que luego se tenga que repriorizar |
| Retomar el diseño final de la placa y la búsqueda de sensor de fuerza en proveedores peruanos | Objetivo específico 1 y 2 |

**7. Anexos o Evidencias**

Documento `Reportes-Semanales/S4/Resumen-Semana4.md` (resumen narrativo con el detalle técnico de las pruebas de IMU y los prototipos de homing). Firmware en `Firmware/test_bno055/`, `Firmware/test_bno055_oversampling/`, `Firmware/test_mpu6050/`, `Firmware/homing_absoluto/`, `Firmware/homing_husillo_hall/`. Estado del arte en `Estado-del-arte/REFERENCIA DE POSICION ABSOLUTA/Arquitecturas-Referencia-Absoluta-sin-Goniometro.md`. Fotos del banco de pruebas y del montaje sobre el pylon real en `Evidencias/pruebas-imu-S4/`. Lista de trabajo activa en `Reportes-Semanales/S4/Pendientes.md`.
