**INFORME SEMANAL DE AVANCE DEL PROYECTO DE INVESTIGACIÓN**

**Proyecto:** Diseño e integración de una plataforma móvil que incluya sensores para medir variables cinemáticas y cinéticas en un simulador de marcha para validar prótesis transtibiales

**Período del informe:** 31/10/2026 al 06/11/2026

**Responsable:** Alessandro Jesus Felix Tello

**1. Resumen Ejecutivo**

Semana dedicada a la integración física de los sensores en el simulador. Se imprimió y montó la caja de la placa con sus ganchos deslizantes, se fijó el sensor de distancia (VL53L1X) en una posición donde la distancia al objetivo nunca baja de ~40 mm, el mínimo de su rango útil, y se montó el IMU en la pieza inferior de la plataforma con su cable. Las piezas impresas necesitaron ajustes de holgura para entrar en el cuerpo real. También se definieron las pruebas de validación de los sensores de distancia, del IMU y de la sincronización con la AMTI. La comparación con la AMTI no se pudo repetir porque el simulador estuvo ocupado en la implementación del control.

**2. Actividades Realizadas**

1. **Montaje de la caja de la placa:** caja impresa y fijada a la placa base del cuerpo con dos ganchos deslizantes, sin perforar el cuerpo. Tapa deslizante con seguro por resalte elástico.
2. **Integración del sensor de distancia:** VL53L1X en un soporte impreso unido a la caja, ubicado para trabajar siempre por encima de ~40 mm.
3. **Integración del IMU:** BNO055 montado en la pieza inferior de la plataforma, con su cable hacia la galleta y su recorrido revisado en el ensamble.
4. **Ajuste de holguras:** adaptación de las piezas impresas al cuerpo real.
5. **Corrección del roll en el firmware:** el ESP32 envía el roll corregido con la recta de calibración de la S9 (ganancia 0.9697, offset −0.514°), además de la lectura original para poder recalibrar.
6. **Plan de pruebas:** pruebas de exactitud, ruido, rango mínimo, interferencia y seguimiento dinámico para los ToF; ruido, exactitud angular, validación de la corrección del roll y efecto de la vibración para el IMU; verificación y adquisición simultánea en la galleta; opciones de sincronización con la AMTI.

**3. Actividades Planificadas vs. Actividades Ejecutadas**

| Actividad Planificada | Estado | Comentarios |
| :---- | :---- | :---- |
| Confirmar la unidad del export de la AMTI y expresar la comparación como ganancia N/N | Pendiente | El simulador se usó para implementar el control |
| Repetir la comparación con la AMTI sin saturar y con evento de sincronización | Pendiente | Misma causa; se evaluará además una sincronización por hardware |
| Imprimir la nueva caja y los ganchos; probar el ajuste sobre la placa base | Ejecutada | Caja montada; se ajustaron holguras |
| Verificación eléctrica de la galleta y primera adquisición con todos los sensores | En proceso | Sensores montados y cableados; falta la adquisición simultánea |
| Aplicar el filtro de corrección lineal del roll en el firmware | Ejecutada | Corrección aplicada en el ESP32 con el ajuste de la S9; se confirmará con la prueba de exactitud angular en el montaje final |
| *(No planificada)* Integración física del ToF y del IMU | Ejecutada | Posición del ToF elegida para no bajar de su rango mínimo |
| *(No planificada)* Definición del plan de pruebas de validación | Ejecutada | Pruebas para ToF, IMU, integración y sincronización con la AMTI |

**4. Dificultades o Problemas Presentados**

- La AMTI no estuvo disponible: el simulador se usó para la implementación del control.
- Las piezas impresas necesitaron ajustes de holgura para montarse sobre el cuerpo real.

**5. Lecciones Aprendidas / Recomendaciones**

El uso del simulador es compartido, así que los ensayos con la AMTI deben coordinarse con anticipación. Para no depender de alinear registros a mano, conviene que la señal de la AMTI y la de los sensores queden en el mismo reloj: leer la salida analógica de la AMTI con el ADS1256 o marcar ambos registros con un pulso de disparo común. En la ubicación de los sensores ópticos de distancia hay que considerar el rango mínimo además del máximo.

**6. Actividades Planificadas para la Siguiente Semana**

| Actividad | Objetivo |
| :---- | :---- |
| Definir e implementar la sincronización con la AMTI (salida analógica con ADS1256 o pulso de disparo) | Objetivo específico 3 |
| Repetir la comparación de la celda con la AMTI y confirmar la unidad del export | Objetivo específico 4 |
| Verificación eléctrica de la galleta y adquisición simultánea de todos los sensores | Objetivo específico 2 |
| Pruebas de exactitud y ruido de los ToF en el montaje final | Objetivo específico 4 |
| Pruebas de ruido y exactitud angular del IMU en el montaje final | Objetivo específico 4 |

**7. Anexos o Evidencias**

Documento [Resumen-Semana12.md](https://github.com/ttanno/LIBRA-26-2-INSTRUMENTACION-DE-SIMULADOR-DE-MARCHA/blob/main/Reportes-Semanales/S12/Resumen-Semana12.md) (detalle técnico y plan de pruebas). Fotos del montaje en [Evidencias/integracion-sensores-S12/](https://github.com/ttanno/LIBRA-26-2-INSTRUMENTACION-DE-SIMULADOR-DE-MARCHA/tree/main/Evidencias/integracion-sensores-S12).
