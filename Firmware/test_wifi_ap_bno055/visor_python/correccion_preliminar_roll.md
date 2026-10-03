# Corrección preliminar del roll – BNO055 (29/09/2026)

**Estado:** PRELIMINAR. Basada en 1 sesión (`angulos_20260929_171116`), ensayos 1,2,4,5,6,7 (ensayo 3 excluido).
Solo 2 ángulos ≠ 0 (20°, 30°) con 1 toma cada uno → validar con más datos antes de darla por buena.

## Modelo (ajuste lineal, mínimos cuadrados)

    roll_medido = 0.9694 · angulo_real − 1.867°      (R² = 0.9999, s_res = 0.15°, SE pendiente = 0.005)

Corrección a aplicar:

    roll_corregido = (roll_medido + 1.867) / 0.9694

| Real | Medido | Corregido | Error antes | Error después |
|---|---|---|---|---|
| 0°  | −1.69 | 0.18  | −1.69 | +0.18 |
| 0°  | −2.01 | −0.15 | −2.01 | −0.15 |
| 0°  | −2.00 | −0.14 | −2.00 | −0.14 |
| 20° | 17.47 | 19.95 | −2.53 | −0.05 |
| 0°  | −1.75 | 0.12  | −1.75 | +0.12 |
| 30° | 27.25 | 30.04 | −2.75 | +0.04 |

Error residual tras corregir: < 0.2° en todos los puntos (antes hasta −2.75°).

## Interpretación
- Offset ≈ −1.9°: posible desnivel del sensor en el soporte / sesgo de fusión.
- Ganancia ≈ 0.97 (−3 %): posible desalineación del eje del sensor respecto al eje de giro, o agujeros del soporte fuera de cota.

## Pendiente para trazabilidad
- Repetir 0/10/20/30° (y negativos si el soporte lo permite), ≥3 repeticiones por ángulo, en orden aleatorio.
- Descartar/marcar tomas con señal congelada (std = 0) y los primeros segundos de asentamiento.
- Registrar calibración del BNO055 (sys/gyro/accel/mag) al inicio de cada toma.
- Verificar cota real de los agujeros del soporte con inclinómetro/goniómetro de referencia.
- Reajustar el modelo con intervalos de confianza y validarlo en una sesión independiente.
