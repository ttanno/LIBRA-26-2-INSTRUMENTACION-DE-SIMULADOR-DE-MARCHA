**INFORME SEMANAL DE AVANCE DEL PROYECTO DE INVESTIGACIÓN**

**Proyecto:** Diseño e integración de una plataforma móvil que incluya sensores para medir variables cinemáticas y cinéticas en un simulador de marcha para validar prótesis transtibiales

**Período del informe:** 17/10/2026 al 23/10/2026

**Responsable:** Alessandro Jesus Felix Tello

**1. Resumen Ejecutivo**

Semana centrada en la integración física del sistema electrónico. Se terminó la placa superior en su versión provisional en galleta de 70×90 mm, con el ESP32, el HX711, las borneras de la celda y la alimentación, y conectores con traba para el BNO055, los dos VL53L1X y el sensor Hall. También se diseñó, en varias iteraciones, la caja que aloja esa placa y la fija al cuerpo del simulador sin perforarlo. La versión final, con marco de columnas, brida superior y soporte para un sensor ToF, ya está impresa en 3D.

**2. Actividades Realizadas**

1. **Placa electrónica terminada (galleta 70×90 mm):** armado completo de la placa superior según el pinout final (`Wire1` en GPIO17/16 para el BNO055, I2C en GPIO21/22 para los ToF, HX711 en GPIO32/33, Hall en GPIO34 con pull-up de 10 kΩ). Todos los sensores entran por conectores Molex KK con traba.
2. **Diseño de la caja de la placa:** bandeja con 4 standoffs para la galleta, 20 mm libres sobre la placa y ventanas para el USB, las borneras y los cables. Se evaluaron varios anclajes (abrazadera al nervio central, clips en C sobre la placa superior) hasta llegar al definitivo: 2 columnas con cartelas y una brida superior que prensa la placa superior del cuerpo con pernos M3, sin perforar el metal.
3. **Soporte del sensor ToF integrado** en la pared exterior de la caja (VL53L1X).
4. **Impresión 3D de la caja y la brida** (versión final).

**3. Actividades Planificadas vs. Actividades Ejecutadas**

| Actividad Planificada | Estado | Comentarios |
| :---- | :---- | :---- |
| Terminar la placa electrónica superior (galleta provisional mientras no se fabrica la PCB) | Ejecutada | Placa armada con el pinout final y conectores con traba |
| Diseñar e imprimir la caja de la placa | Ejecutada | Versión final impresa; anclaje sin perforar el cuerpo |
| Aplicar el filtro de corrección lineal del roll en el firmware | Pendiente | Se pasa a la siguiente semana |
| Avanzar el diseño del adaptador de fuerza y evaluar las barras guía contra cizalla | Pendiente | Se pasa a la siguiente semana |

**4. Dificultades o Problemas Presentados**

- Todavía no se puede mandar a fabricar la PCB principal. Para no detener la integración, se armó una placa provisional en galleta que mantiene el mismo pinout, así el firmware no cambia cuando llegue la PCB.
- En la primera iteración de la caja no se consideraron unas partes soldadas del cuerpo del simulador, que interferían con el anclaje al nervio central. Por eso se descartó esa versión y se rediseñó la fijación sobre la placa superior del cuerpo, también sin perforar, porque el cuerpo es metálico.

**5. Lecciones Aprendidas / Recomendaciones**

Antes de diseñar sobre una pieza existente conviene comparar la pieza física con su modelo 3D: las partes soldadas del cuerpo no estaban en el modelo y obligaron a rehacer el anclaje. Detectarlo antes de imprimir evitó gastar material en una versión que no iba a encajar. Respetar en la galleta el mismo pinout de la PCB final evita tener que reprogramar cuando se cambie de placa.

**6. Actividades Planificadas para la Siguiente Semana**

| Actividad | Objetivo |
| :---- | :---- |
| Verificación eléctrica de la galleta (continuidad, alimentación y lectura de cada sensor: BNO055, HX711, 2× VL53L1X, Hall) | Objetivo específico 2 |
| Montar la galleta en la caja y la caja en el cuerpo; revisar ajuste, rigidez y paso de cables | Objetivo específico 1 |
| Primera adquisición con todos los sensores conectados a la misma placa | Objetivo específico 2 / 4 |
| Aplicar el filtro de corrección lineal del roll en el firmware | Objetivo específico 2 |
| Avanzar el adaptador de fuerza y evaluar las barras guía contra cizalla | Objetivo específico 1 |

**7. Anexos o Evidencias**

Documento [Resumen-Semana10.md](https://github.com/ttanno/LIBRA-26-2-INSTRUMENTACION-DE-SIMULADOR-DE-MARCHA/blob/main/Reportes-Semanales/S10/Resumen-Semana10.md) (detalle técnico completo). Evidencias en [Evidencias/pcb-S10/](https://github.com/ttanno/LIBRA-26-2-INSTRUMENTACION-DE-SIMULADOR-DE-MARCHA/tree/main/Evidencias/pcb-S10) (plano de armado de la galleta) y [Evidencias/caja-pcb-S10/](https://github.com/ttanno/LIBRA-26-2-INSTRUMENTACION-DE-SIMULADOR-DE-MARCHA/tree/main/Evidencias/caja-pcb-S10) (modelo STEP y vistas de la caja).
