**INFORME SEMANAL DE AVANCE DEL PROYECTO DE INVESTIGACIÓN**

**Proyecto:** Diseño e integración de una plataforma móvil que incluya sensores para medir variables cinemáticas y cinéticas en un simulador de marcha para validar prótesis transtibiales

**Período del informe:** 05/09/2026 al 11/09/2026

**Responsable:** Alessandro Jesus Felix Tello

**1. Resumen Ejecutivo**

Durante la sexta semana el trabajo se concentró en dejar funcionando de forma confiable la transmisión inalámbrica del sensor BNO055 (WiFi en modo Access Point propio del ESP32), lo que llevó a encontrar y corregir un bug en la librería `DFRobot_BNO055` que impedía leer el sensor de forma sostenida. A partir de ahí se construyeron las herramientas necesarias para validar y mejorar la precisión del "cero" de referencia del sensor: registro de pruebas con estadística de ruido, elección de un filtro simple (promedio móvil exponencial) para suavizar micro-variaciones, y una rutina de calibración de acelerómetro de 6 posiciones que se guarda en la flash del ESP32. En paralelo se avanzó el diseño mecánico del bloque del pylon (versión preliminar vs. versión actual) y se registró el montaje de la electrónica bajo la plataforma. No se presentaron situaciones adversas esta semana.

**2. Actividades Realizadas**

1. **Transmisión WiFi del BNO055 y corrección de bug en la librería.** Se armaron sketches de ESP32 que envían las lecturas del BNO055 por WiFi (UDP), en modo Access Point propio para evitar la autenticación enterprise de la red de la universidad. Se encontró que la librería `DFRobot_BNO055` reinicializaba el bus I2C en cada lectura, rompiendo la comunicación después de los primeros segundos; se corrigió en el código fuente de la librería.

2. **Validación de ruido del sensor y elección de filtro.** Se construyó una herramienta de registro a CSV con cálculo automático de desviación estándar, se corrieron pruebas de "sensor quieto", y se decidió usar un filtro de promedio móvil exponencial (EMA) para suavizar micro-variaciones, en vez de un filtro de Kalman o un modelo de machine learning, dado que el BNO055 ya hace fusión sensorial interna equivalente.

3. **Mejora de precisión del cero absoluto y calibración de acelerómetro.** Se mejoró la función que fija el cero de referencia del sensor (más muestras, reporte de precisión lograda, rechazo si el sensor se movió durante la captura) y se construyó una calibración de acelerómetro de 6 posturas estáticas que se aplica al chip y persiste en la flash del ESP32.

4. **Avance del diseño mecánico del pylon y registro del montaje de electrónica.** Se actualizó el diseño del bloque superior del pylon (versión preliminar vs. versión actual) en Fusion 360, y se documentó una vista del montaje de la electrónica (ESP32 y un módulo adicional) bajo la plataforma.

**3. Actividades Planificadas vs. Actividades Ejecutadas**

| Actividad Planificada | Estado (Ejecutada / En proceso / No ejecutada) | Comentarios (justificación si aplica) |
| :---- | :---- | :---- |
| Confirmar con el vendedor el tipo de salida eléctrica de la celda de carga comprada | No ejecutada | Sin avance esta semana; el foco pasó a destrabar la transmisión WiFi del BNO055 |
| Imprimir la versión imprimible del bloque del pylon y correr pruebas de ajuste en el simulador | En proceso | Se actualizó el diseño (preliminar vs. actual) en Fusion 360; falta imprimir y probar |
| Correr la validación estructural en Fusion 360 de la versión final del bloque del pylon | No ejecutada | Sin avance esta semana |
| Decidir y comprar el reemplazo de IMU (LSM6DSR o ICM-45686) y diseñar un tope mecánico de referencia | No ejecutada | Se prioriza primero dejar el BNO055 actual funcionando y calibrado antes de decidir si conviene reemplazarlo |
| Resolver las interferencias del adaptador del sensor de distancia con la placa base | No ejecutada | Sin avance esta semana |
| *(no planificada)* Corrección del bug de la librería DFRobot_BNO055 y transmisión WiFi funcional | Ejecutada | Se volvió prerequisito: sin esto no se podía avanzar ninguna prueba del BNO055 |
| *(no planificada)* Validación de ruido, elección de filtro, y calibración de acelerómetro de 6 posiciones | Ejecutada | Trabajo necesario para que el cero de referencia del pivote sea confiable |

**4. Dificultades o Problemas Presentados**

No se presentaron dificultades o problemas relevantes esta semana. El único inconveniente técnico (un bug en la librería `DFRobot_BNO055` que impedía leer el sensor de forma sostenida) se identificó y corrigió dentro de la misma semana, sin bloquear el avance general.

**5. Lecciones Aprendidas / Recomendaciones**

Cuando el comportamiento de un sensor en campo no calza con lo esperado, conviene revisar el código fuente de la librería antes de asumir que el problema es de cableado o calibración — en este caso la causa fue una llamada interna redundante, no el hardware. También quedó confirmado que mejorar la precisión de un ángulo ya fusionado (Euler) requiere corregir el sensor en su propio firmware (registros de offset del chip), no alcanza con corregir el dato solo en el post-procesamiento.

**6. Actividades Planificadas para la Siguiente Semana**

| Actividad | Objetivo |
| :---- | :---- |
| Correr la calibración de acelerómetro y repetir las pruebas de ruido para confirmar la mejora | Objetivo específico 2 |
| Evaluar si el magnetómetro (heading) hace falta para el caso de uso del pivote, o si basta con roll/pitch calibrados | Objetivo específico 2 |
| Retomar la decisión de reemplazo de IMU (LSM6DSR/ICM-45686) ahora que el BNO055 funciona de forma confiable por WiFi | Objetivo específico 2 |
| Imprimir la versión imprimible del bloque del pylon y correr pruebas de ajuste en el simulador | Objetivo específico 1 |
| Evaluar agregar un sensor Hall de referencia en el punto de 0° del pivote | Objetivo específico 3 y 4 |

**7. Anexos o Evidencias**

Documento `Reportes-Semanales/S6/Resumen-Semana6.md` (resumen narrativo con el detalle técnico completo). Análisis de las pruebas de ruido en `Evidencias/pruebas-imu-S5/Analisis-Prueba-Quieto-S5.md`. Imágenes del diseño del pylon y del montaje de electrónica en `Evidencias/diseno-pylon-S6/`. Sketches de firmware en `Firmware/test_wifi_ap_bno055/` y `Firmware/test_wifi_udp_bno055/`.
