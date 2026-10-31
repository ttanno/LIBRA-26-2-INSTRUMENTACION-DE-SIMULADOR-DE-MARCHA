**INFORME SEMANAL DE AVANCE DEL PROYECTO DE INVESTIGACIÓN**

**Proyecto:** Diseño e integración de una plataforma móvil que incluya sensores para medir variables cinemáticas y cinéticas en un simulador de marcha para validar prótesis transtibiales

**Período del informe:** 24/10/2026 al 30/10/2026

**Responsable:** Alessandro Jesus Felix Tello

**1. Resumen Ejecutivo**

Semana con dos frentes. Primero, se comparó por primera vez la celda de carga (con HX711) contra la plataforma de fuerza AMTI del laboratorio, aplicando carga en escalones sobre ambas a la vez. La celda sigue a la AMTI de forma lineal (R² = 0.999, error de ~5 N) y repetible entre ensayos. Para eso se agregó al visor de la celda la grabación a CSV con la hora de la PC, que permite alinear los dos registros. Segundo, se rediseñó la caja de la placa electrónica: la nueva versión es más baja y se fija al cuerpo con dos ganchos deslizantes, sin pernos ni perforaciones.

**2. Actividades Realizadas**

1. **Grabación con marca de tiempo en el visor de la celda:** botón Grabar/Detener en `visor_hx711.py` que guarda cada muestra con la hora de la PC al llegar por el puerto serie, para sincronizar con otros equipos.
2. **Ensayo celda + HX711 vs. AMTI (27/10):** carga en escalones sobre la celda montada en la AMTI; dos ensayos completos (Trial00530 y Trial00533). Alineación temporal de los registros y ajuste lineal sobre las mesetas: F_celda = 5.15·Fz − 26 y F_celda = 5.03·Fz − 20, ambos con R² = 0.999 y RMSE ≈ 5 N.
3. **Rediseño de la caja de la placa:** bandeja abierta para la placa de 90 × 70 mm con rieles para tapa deslizante, ala lateral con canal para la salida de cables y dos ganchos en C que se deslizan por ranuras en T de la base y abrazan la placa base del cuerpo.

**3. Actividades Planificadas vs. Actividades Ejecutadas**

| Actividad Planificada | Estado | Comentarios |
| :---- | :---- | :---- |
| Verificación eléctrica de la galleta | Pendiente | Se priorizó la comparación con la AMTI |
| Montar la galleta en la caja y la caja en el cuerpo | En proceso | Se rediseñó la caja con un anclaje por ganchos; falta imprimir la nueva versión |
| Primera adquisición con todos los sensores en la misma placa | Pendiente | Se pasa a la siguiente semana |
| Aplicar el filtro de corrección lineal del roll en el firmware | Pendiente | Se pasa a la siguiente semana |
| Avanzar el adaptador de fuerza y evaluar las barras guía contra cizalla | Pendiente | Se pasa a la siguiente semana |
| *(No planificada)* Comparación de la celda contra la AMTI | Ejecutada | Primera validación de la medición de fuerza contra la referencia del laboratorio |

**4. Dificultades o Problemas Presentados**

- La AMTI se saturó a partir de ~580 N (medidos en la celda), por lo que la comparación solo cubre ese rango. Hay que revisar el rango del amplificador antes de repetir.
- No se confirmó la unidad de la Fz exportada por la AMTI, así que la pendiente todavía no se puede expresar como ganancia N/N.
- La celda se cargó hasta ~1270 N, por encima de su capacidad nominal (~978 N).
- Los equipos no comparten reloj; el desfase (−2.04 s y +1.28 s) se corrigió manualmente.

**5. Lecciones Aprendidas / Recomendaciones**

Antes de comparar contra la AMTI conviene revisar su rango configurado y fijar la carga máxima según el sensor de menor capacidad. Un evento de sincronización al inicio de cada registro simplifica la alineación. Con frecuencias de muestreo tan distintas (11.5 Hz vs. 1000 Hz), la comparación es confiable en las mesetas y no en las transiciones, así que los ensayos deben tener escalones de carga sostenidos.

**6. Actividades Planificadas para la Siguiente Semana**

| Actividad | Objetivo |
| :---- | :---- |
| Confirmar la unidad del export de la AMTI y expresar la comparación como ganancia N/N | Objetivo específico 4 |
| Repetir la comparación con la AMTI sin saturar, dentro de la capacidad nominal de la celda y con evento de sincronización | Objetivo específico 4 |
| Imprimir la nueva caja y los ganchos; probar el ajuste sobre la placa base del cuerpo | Objetivo específico 1 |
| Verificación eléctrica de la galleta y primera adquisición con todos los sensores | Objetivo específico 2 |
| Aplicar el filtro de corrección lineal del roll en el firmware | Objetivo específico 2 |

**7. Anexos o Evidencias**

Documento [Resumen-Semana11.md](https://github.com/ttanno/LIBRA-26-2-INSTRUMENTACION-DE-SIMULADOR-DE-MARCHA/blob/main/Reportes-Semanales/S11/Resumen-Semana11.md) (detalle técnico completo). Evidencias en [Evidencias/pruebas-fuerza-amti-S11/](https://github.com/ttanno/LIBRA-26-2-INSTRUMENTACION-DE-SIMULADOR-DE-MARCHA/tree/main/Evidencias/pruebas-fuerza-amti-S11) (comparación con la AMTI) y [Evidencias/caja-pcb-S11/](https://github.com/ttanno/LIBRA-26-2-INSTRUMENTACION-DE-SIMULADOR-DE-MARCHA/tree/main/Evidencias/caja-pcb-S11) (modelo STEP y vistas de la nueva caja).
