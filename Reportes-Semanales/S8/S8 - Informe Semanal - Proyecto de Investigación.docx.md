**INFORME SEMANAL DE AVANCE DEL PROYECTO DE INVESTIGACIÓN**

**Proyecto:** Diseño e integración de una plataforma móvil que incluya sensores para medir variables cinemáticas y cinéticas en un simulador de marcha para validar prótesis transtibiales

**Período del informe:** 19/09/2026 al 25/09/2026

**Responsable:** Alessandro Jesus Felix Tello

**1. Resumen Ejecutivo**

Semana centrada en diseño de PCB (placa superior y breakout del BNO055), calibración exitosa del sensor de fuerza con HX711, y primera prueba de los 2 sensores ToF VL53L1X. Se agregaron dos documentos de estado del arte. No se atendieron las observaciones de la S7 por una mala organización de tiempo; quedan como prioridad 1 para la S9.

**2. Actividades Realizadas**

1. **PCB de la placa superior:** esquemático y vista 3D (ESP32, IMU, HX711, alimentación, sensor Hall, 2 ToF).
2. **PCB del breakout del BNO055:** conectores XH con traba (apunta al falso contacto detectado en la S7).
3. **Calibración del HX711:** con masa patrón de 2 kg, verificada con una segunda masa — respuesta lineal y repetible.
4. **Prueba de los 2 ToF VL53L1X:** reasignación de dirección I2C confirmada en hardware (0x29/0x30); medición a 20 y 40 cm con error <10%.
5. **Estado del arte:** corrección en la comparativa de IMU (el sensor en uso desde la S6 es el BNO055, no el MPU6050) y nuevo documento sobre factibilidad de control de fuerza (celda + IMU) usando el AMTI como referencia.

**3. Actividades Planificadas vs. Actividades Ejecutadas**

| Actividad Planificada | Estado | Comentarios |
| :---- | :---- | :---- |
| Confirmar fix del bug de inicialización del EMA y repetir tanda de capturas | No ejecutada | Pasa a prioridad 1 de la S9 |
| Repetir pruebas de ruido con `ACC_RADIUS` activo | No ejecutada | Pasa a prioridad 1 de la S9 |
| Investigar conector/cable del salto de ruido (falso contacto) | No ejecutada | El nuevo breakout con conectores XH apunta a esto, sin confirmar aún |
| Calibración con masa patrón en el ADS1256 | No ejecutada | Sin avance esta semana |
| Sketch de prueba de los 2 VL53L1X con reasignación I2C | Ejecutada | — |
| *(no planificada)* PCB de la placa superior y del breakout del BNO055 | Ejecutada | — |
| *(no planificada)* Calibración del HX711 | Ejecutada | — |
| *(no planificada)* 2 documentos de estado del arte | Ejecutada | — |

**4. Dificultades o Problemas Presentados**

No se atendieron las observaciones del Dr. Elías sobre el informe de la S7 (por organización de tiempo, no por un impedimento técnico). Se corrigió un problema menor de buffer serial en los visores de ToF.

**5. Lecciones Aprendidas / Recomendaciones**

Usar conectores con traba en vez de cables sueltos ataca directamente el falso contacto detectado en la S7. Repetir el análisis de estado del arte contra el sensor real en uso (no el original) evita arrastrar una conclusión desactualizada.

**6. Actividades Planificadas para la Siguiente Semana**

| Actividad | Objetivo |
| :---- | :---- |
| Aplicar el fix del EMA, corregir el falso contacto y repetir pruebas del BNO055 | Objetivo específico 2 |
| Precisar la definición de "estructura del pylon" | Objetivo específico 1 |
| Reprogramar el cronograma con lo no ejecutado en la S7 y S8 | — |
| Crear registro de trazabilidad de pruebas | Objetivo específico 4 |
| Coordinar migración del repositorio al Drive de LIBRA | — |
| Revisar la PCB antes de fabricar | Objetivo específico 2 |
| Calibrar el offset de los ToF y definir su montaje | Objetivo específico 2 y 4 |

**7. Anexos o Evidencias**

Documento [Resumen-Semana8.md](https://github.com/ttanno/LIBRA-26-2-INSTRUMENTACION-DE-SIMULADOR-DE-MARCHA/blob/main/Reportes-Semanales/S8/Resumen-Semana8.md) (detalle técnico completo). Evidencias en [Evidencias/pcb-S8/](https://github.com/ttanno/LIBRA-26-2-INSTRUMENTACION-DE-SIMULADOR-DE-MARCHA/tree/main/Evidencias/pcb-S8), [Evidencias/graficos-fuerza-S8/](https://github.com/ttanno/LIBRA-26-2-INSTRUMENTACION-DE-SIMULADOR-DE-MARCHA/tree/main/Evidencias/graficos-fuerza-S8) y [Evidencias/pruebas-tof-S8/](https://github.com/ttanno/LIBRA-26-2-INSTRUMENTACION-DE-SIMULADOR-DE-MARCHA/tree/main/Evidencias/pruebas-tof-S8). Sketch en [Firmware/test_tof/](https://github.com/ttanno/LIBRA-26-2-INSTRUMENTACION-DE-SIMULADOR-DE-MARCHA/tree/main/Firmware/test_tof). Pinout en [PCB_placa_superior_PINOUT.md](https://github.com/ttanno/LIBRA-26-2-INSTRUMENTACION-DE-SIMULADOR-DE-MARCHA/blob/main/Firmware/PCB_placa_superior_PINOUT.md).
