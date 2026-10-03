**INFORME SEMANAL DE AVANCE DEL PROYECTO DE INVESTIGACIÓN**

**Proyecto:** Diseño e integración de una plataforma móvil que incluya sensores para medir variables cinemáticas y cinéticas en un simulador de marcha para validar prótesis transtibiales

**Período del informe:** 26/09/2026 al 02/10/2026

**Responsable:** Alessandro Jesus Felix Tello

**1. Resumen Ejecutivo**

Semana centrada en el IMU (BNO055): se diagnosticó y resolvió una falla de conexión (cable en el pin INT en vez de SDA/SCL), se calibró el acelerómetro, y se corrió una caracterización completa de linealidad/exactitud/histéresis en 0-60°. Resultado: muy buena linealidad (R²>0.999) con un error de escala sistemático de ~3%, corregible con un filtro lineal simple. También se avanzó un primer diseño CAD del adaptador del sensor de fuerza.

**2. Actividades Realizadas**

1. **Diagnóstico y reparación del BNO055:** aislado paso a paso (brownout de alimentación → sensor no detectado → cable mal puesto en INT). Conexión estable de nuevo.
2. **Calibración de 6 posiciones del acelerómetro:** `Calib[accel,mag]` pasó de 0/3 a 3/3.
3. **Prueba de linealidad 0-60°:** 13 ángulos × 3 repeticiones × 2 direcciones (subida/bajada) con el soporte de arco indexado, usando un script con disparo automático por movimiento+quietud.
4. **Simulación de filtro de corrección lineal:** reduce el error máximo de ~2.4° a ~0.5°.
5. **Primer diseño CAD del adaptador del sensor de fuerza** (parantes + mordaza para la celda de carga del pylon).

**3. Actividades Planificadas vs. Actividades Ejecutadas**

| Actividad Planificada | Estado | Comentarios |
| :---- | :---- | :---- |
| Aplicar fix del EMA, corregir falso contacto y repetir pruebas del BNO055 | Ejecutada | El "falso contacto" resultó ser un cable en el pin INT; resuelto |
| Calibración de acelerómetro y prueba de linealidad 0-60° (parte del plan de repetir pruebas del BNO055) | Ejecutada | R²>0.999 ambas direcciones; error de escala ~3% corregible con filtro lineal |
| *(no planificada)* Diseño CAD preliminar del adaptador de fuerza | Ejecutada | — |

**4. Dificultades o Problemas Presentados**

La reconexión intermitente del BNO055 durante la toma de datos (manipuleo constante del soporte de ángulos) obligó a repetir varias posiciones de la prueba de linealidad — documentado en el propio script de procesamiento. No bloqueó el resultado final, solo alargó la toma de datos.

**5. Lecciones Aprendidas / Recomendaciones**

Diagnosticar leyendo el puerto serial crudo (en vez de asumir la causa) permitió separar tres problemas distintos que se presentaban juntos: alimentación (brownout), pinout (I2C) y un cable en el pin equivocado (INT). Verificar con datos reales qué eje del IMU responde al movimiento (roll, no pitch, con este montaje) evitó construir una tabla de resultados sin sentido.

**6. Actividades Planificadas para la Siguiente Semana**

| Actividad | Objetivo |
| :---- | :---- |
| Atender las observaciones pendientes de la S7 (estructura del pylon, reprogramación, trazabilidad, migración a Drive) | — |
| Aplicar el filtro de corrección lineal del roll en el firmware | Objetivo específico 2 |
| Avanzar el diseño CAD del adaptador de fuerza (patrón de pernos, holguras) | Objetivo específico 1 |
| Evaluar la propuesta de barras guía contra cizalla para la celda de carga | Objetivo específico 1 |

**7. Anexos o Evidencias**

Documento [Resumen-Semana9.md](https://github.com/ttanno/LIBRA-26-2-INSTRUMENTACION-DE-SIMULADOR-DE-MARCHA/blob/main/Reportes-Semanales/S9/Resumen-Semana9.md) (detalle técnico completo). Evidencias en [Evidencias/pruebas-imu-S9/](https://github.com/ttanno/LIBRA-26-2-INSTRUMENTACION-DE-SIMULADOR-DE-MARCHA/tree/main/Evidencias/pruebas-imu-S9) y [Evidencias/diseno-cad-preliminar-S9/](https://github.com/ttanno/LIBRA-26-2-INSTRUMENTACION-DE-SIMULADOR-DE-MARCHA/tree/main/Evidencias/diseno-cad-preliminar-S9). Scripts en [Firmware/test_wifi_ap_bno055/visor_python/](https://github.com/ttanno/LIBRA-26-2-INSTRUMENTACION-DE-SIMULADOR-DE-MARCHA/tree/main/Firmware/test_wifi_ap_bno055/visor_python).
