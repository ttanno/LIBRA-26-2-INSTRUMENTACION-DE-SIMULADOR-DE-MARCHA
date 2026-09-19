**INFORME SEMANAL DE AVANCE DEL PROYECTO DE INVESTIGACIÓN**

**Proyecto:** Diseño e integración de una plataforma móvil que incluya sensores para medir variables cinemáticas y cinéticas en un simulador de marcha para validar prótesis transtibiales

**Período del informe:** 12/09/2026 al 18/09/2026

**Responsable:** Alessandro Jesus Felix Tello

**1. Resumen Ejecutivo**

La semana se dividió entre el IMU (BNO055) y el sensor de fuerza del pylon. En el IMU se llevó el filtro EMA al firmware, se agregó un chequeo de salud de conexión, y se encontraron dos hallazgos: un bug de inicialización del filtro (arranca en 0°, transitorio de ~30 muestras) y un salto de ruido por un conector flojo. En el sensor de fuerza se hizo la primera calibración física con el HX711, en paralelo al diagnóstico del ruido del ADS1256. También se escribió el primer documento de pinout de la PCB superior. No hubo situaciones adversas, aunque los dos hallazgos del IMU siguen sin cerrar.

**2. Actividades Realizadas**

1. **Filtro EMA embebido en firmware + chequeo de salud de conexión (BNO055).** El filtro, antes solo en post-procesamiento, ahora corre en el ESP32 con corrección circular para ángulos 0°/360°, más una alerta automática si la desviación estándar de roll/pitch supera un umbral.

2. **Bug encontrado: el filtro EMA arranca en cero.** Comparando dato crudo vs. filtrado se encontró que el filtro se siembra en 0° al iniciar en vez de tomar el primer valor real, con un transitorio de ~30 muestras.

3. **Hallazgo: salto de ruido por conector flojo.** Las últimas dos tandas de un mismo día mostraron una desviación estándar muy por encima de las anteriores, lo que motivó el chequeo de salud de conexión del punto 1.

4. **Intento de completar la calibración del acelerómetro (offset + radius).** Se agregó la escritura del registro `ACC_RADIUS` — cambio experimental, pendiente de confirmar con una nueva tanda de pruebas.

5. **Primera prueba física del sensor de fuerza con el HX711.** Calibración completa (tara + masa patrón de 2 kg) con una celda real, verificada contra una segunda masa no usada en la calibración.

6. **Primer documento de diseño de PCB (pinout de la placa superior).** Arquitectura de conexionado completa: ESP32, dos sensores ToF y entrada del sensor de fuerza, con bus I2C dedicado para el BNO055 y asignación final de pines.

**3. Actividades Planificadas vs. Actividades Ejecutadas**

| Actividad Planificada | Estado (Ejecutada / En proceso / No ejecutada) | Comentarios (justificación si aplica) |
| :---- | :---- | :---- |
| Correr la calibración de acelerómetro y repetir las pruebas de ruido para confirmar la mejora | En proceso | Se agregó `ACC_RADIUS`; falta repetir la tanda de 5 pruebas de la S6 |
| Evaluar si el magnetómetro (heading) hace falta para el caso de uso del pivote | No ejecutada | El foco pasó a los dos hallazgos nuevos del filtro y la conexión |
| Imprimir la versión imprimible del bloque del pylon y correr pruebas de ajuste en el simulador | No ejecutada | El foco pasó al sensor de fuerza y al diseño de PCB |
| Evaluar agregar un sensor Hall de referencia en el punto de 0° del pivote | No ejecutada | Sin avance esta semana |
| *(no planificada)* Filtro EMA embebido en firmware + chequeo de salud de conexión | Ejecutada | Consecuencia directa de los datos de ruido de esta semana |
| *(no planificada)* Bug de inicialización del filtro y hallazgo de conector flojo | Ejecutada (diagnóstico); fix pendiente de confirmar | Encontrados al analizar las tandas del 15/09 |
| *(no planificada)* Primera prueba física del sensor de fuerza (HX711) | Ejecutada | Diagnóstico en paralelo al ruido del ADS1256 |
| *(no planificada)* Pinout de la placa superior (primer documento de PCB) | Ejecutada | Pendiente el sketch de los ToF |

**4. Dificultades o Problemas Presentados**

Dos hallazgos técnicos quedaron sin cerrar del todo: el filtro EMA arranca en 0° (transitorio de ~30 muestras), y una tanda del 15/09 mostró un salto de ruido compatible con un conector flojo, sin confirmar aún el cable/conector exacto. Ninguno bloqueó el avance de la semana, pero ambos deben confirmarse antes de tomar los próximos datos de ruido como definitivos.

**5. Lecciones Aprendidas / Recomendaciones**

Comparar crudo contra filtrado en la misma línea de datos permitió encontrar el bug de inicialización, que habría pasado desapercibido mirando solo el filtrado. Medir el ruido por tanda (en vez de un promedio único al final del día) permitió ubicar en el tiempo el cambio físico del conector. Para el sensor de fuerza, probar con un ADC distinto (HX711) sobre la misma celda separa directamente "problema del ADC/alimentación" de "problema de la celda/cableado".

**6. Actividades Planificadas para la Siguiente Semana**

| Actividad | Objetivo |
| :---- | :---- |
| Confirmar el fix del bug de inicialización del filtro EMA y repetir una tanda de capturas | Objetivo específico 2 |
| Repetir las pruebas de ruido de la S6 con la escritura de `ACC_RADIUS` activa | Objetivo específico 2 |
| Investigar el conector/cable detrás del salto de ruido del 15/09 | Objetivo específico 2 |
| Correr la misma calibración con masa patrón en el ADS1256 (misma celda, mismo cableado) para aislar el diente de sierra | Objetivo específico 2 y 4 |
| Escribir el sketch de prueba de los dos VL53L1X con reasignación de dirección I2C | Objetivo específico 2 |

**7. Anexos o Evidencias**

Documento `Reportes-Semanales/S7/Resumen-Semana7.md` (detalle técnico completo). Imágenes y CSV en `Evidencias/pruebas-imu-S7/` y `Evidencias/pruebas-fuerza-S7/`. Sketches en `Firmware/test_wifi_ap_bno055/`, `Firmware/test_hx711/` y `Firmware/test_ads1256/`. Documento de diseño en `Firmware/PCB_placa_superior_PINOUT.md`.
