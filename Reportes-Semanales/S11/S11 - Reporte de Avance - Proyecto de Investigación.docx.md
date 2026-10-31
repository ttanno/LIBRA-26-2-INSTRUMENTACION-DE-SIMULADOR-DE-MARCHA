**REPORTE DE AVANCE – PROYECTO DE INVESTIGACIÓN EN LIBRA**

| INFORMACIÓN GENERAL | |
| :---- | :---- |
| Título del Proyecto | Diseño e integración de una plataforma móvil que incluya sensores para medir variables cinemáticas y cinéticas en un simulador de marcha para validar prótesis transtibiales |
| Nombre del alumno/a | Alessandro Jesus Felix Tello |
| Nombre del asesor/a | Dante Angel Elias Giordano |
| Laboratorio de Investigación | Laboratorio de Investigación en Biomecánica y Robótica Aplicada |
| Fecha de entrega | 30/10/2026 |

**Objetivos (general y específicos) del proyecto de investigación ejecutado en LIBRA**

| Objetivo | Nivel Avance (%) |
| :---- | :---- |
| OG: Diseñar e integrar una plataforma móvil instrumentada con sensores para medir variables cinemáticas y cinéticas en un simulador de marcha, para apoyar la validación experimental de prótesis transtibiales | 44% *(propuesto — ajustar según tu criterio)* |
| OE1: Diseño Mecánico — diseñar la plataforma móvil considerando los requerimientos mecánicos y funcionales del simulador | 33% *(propuesto — ajustar según tu criterio)* |
| OE2: Sistema Electrónico — seleccionar e integrar sensores y sistema electrónico de adquisición y procesamiento | 62% *(propuesto — ajustar según tu criterio)* |
| OE3: Software — desarrollar el software para sincronizar, visualizar, registrar y gestionar los datos del sistema | 20% *(propuesto — ajustar según tu criterio)* |
| OE4: Validación — calibrar y validar la plataforma mediante pruebas experimentales | 27% *(propuesto — ajustar según tu criterio)* |

**Resultados del proyecto de investigación ejecutado en LIBRA**

| Resultado | Nivel Avance (%) |
| :---- | :---- |
| R1: Plataforma diseñada e integrada al simulador | 31% *(propuesto — ajustar según tu criterio)* |
| R2: Sistema de sensores (cinemáticos y cinéticos) operativo | 44% *(propuesto — ajustar según tu criterio)* |
| R3: Sistema electrónico de adquisición de datos en tiempo real | 34% *(propuesto — ajustar según tu criterio)* |
| R4: Software de monitoreo, almacenamiento y visualización | 10% *(propuesto — ajustar según tu criterio)* |

**Síntesis de lo ejecutado durante la semana**

| Actividad | Objetivo | Descripción | Resultados |
| :---- | :---- | :---- | :---- |
| A1: Grabación con marca de tiempo en el visor de la celda | OE3 | Botón Grabar/Detener en `visor_hx711.py`; cada muestra se guarda con la hora de la PC al llegar por el puerto serie | CSV listos para alinearse con equipos externos (AMTI) |
| A2: Comparación celda + HX711 vs. plataforma AMTI | OE4 | Carga en escalones sobre la celda montada en la AMTI; 2 ensayos, alineación temporal y ajuste lineal sobre mesetas | Respuesta lineal y repetible: pendientes 5.15 y 5.03, R² = 0.999, RMSE ≈ 5 N (rango de 0 a ~580 N) |
| A3: Rediseño de la caja de la placa | OE1 | Caja más baja sobre la placa base del cuerpo, con rieles para tapa, ala de salida de cables y 2 ganchos en C deslizantes por ranuras en T | Modelo 3D terminado, pendiente de impresión |

**Situaciones surgidas en el desarrollo del proyecto**

| Eventos | Fecha de Ocurrencia | Actividad Afectada | Acciones Tomadas |
| :---- | :---- | :---- | :---- |
| E1: La AMTI se saturó a partir de ~580 N | F1: 27/10/2026 | A2: Comparación con la AMTI | El ajuste se limitó al rango no saturado; se revisará el rango del amplificador antes de repetir |
| E2: La celda se cargó por encima de su capacidad nominal (~1270 N frente a ~978 N) | F2: 27/10/2026 | A2: Comparación con la AMTI | Se fijará la carga máxima de los próximos ensayos en la capacidad nominal y se revisará el cero de la celda |
| E3: Unidad del export de la AMTI sin confirmar | F3: 27/10/2026 – 30/10/2026 | A2: Comparación con la AMTI | Se confirmará en el software de la AMTI para expresar la ganancia en N/N |
