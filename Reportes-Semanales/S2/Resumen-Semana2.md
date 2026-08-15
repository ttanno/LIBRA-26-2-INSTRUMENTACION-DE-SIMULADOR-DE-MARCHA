# Resumen de trabajo — Semana 2

**Período:** 10/08/2026 – 14/08/2026
**Responsable:** Alessandro Jesus Felix Tello

Resumen narrativo de la semana, complementario al Informe Semanal y Reporte de Avance (formato PUCP) y al detalle línea por línea en `Reportes-Semanales/S1/Pendientes.md`.

## 1. Reunión con el asesor — arquitectura de sensores por DOF

Dante confirmó una arquitectura de sensado con un sensor dedicado por cada grado de libertad del simulador, en vez de un solo sensor de posición genérico:

- **GRF (fuerza de reacción del suelo):** prioridad. Se mide con una plataforma de fuerza alineada/centrada bajo el punto de apoyo del pie.
- **Interfaz pylon–plataforma (celda de carga):** pasa a ser secundaria — se mantiene, sigue siendo útil (dimensionamiento ISO 10328), pero invierte la prioridad que tenía antes.
- **Traslación (horizontal y vertical):** sensor láser de distancia (ToF).
- **Rotación (flexo-extensión):** encoder rotativo o potenciómetro, montado en el propio eje.

Requisito explícito de Dante: la plataforma de fuerza debe integrarse mecánicamente con el simulador y su adquisición debe ser **sincrónica** con el resto de sensores.

## 2. Confirmación del equipo: AMTI BP400600

Se confirmó que el laboratorio ya cuenta físicamente con una plataforma de fuerza AMTI BP400600 (modelo OPT400600-2000) con amplificador Optima OPT-SC (S/N 4305) — no es necesario adquirir una nueva. Esto resuelve la pregunta abierta de "qué plataforma usar" y cambia el problema de selección a uno de integración.

## 3. Integración de la plataforma de fuerza

El software oficial de AMTI (GEN5 → AMTI-NetForce → BioAnalysis) es un flujo de **grabación por lotes** (duración fija, guarda archivos `.bsf`, análisis offline con llave Sentinel) — no ofrece acceso en tiempo real, lo cual es un problema para sincronización y para un eventual lazo de control PID.

Revisando físicamente el amplificador se confirmó que sí existe una **salida analógica independiente** (conector DB25S, ±5V, DAC de 16 bit), separada del enlace USB. Se obtuvo:

- El pinout completo del conector DB25S (pines 1–6 = Fx, Fy, Fz, Mx, My, Mz).
- Las dos fórmulas de conversión voltaje→fuerza según el modo de salida configurado (MSA-6 Compatible, con matriz de calibración 6×6; o Fully Conditioned, conversión lineal simple por canal).
- Confirmación de que la configuración se guarda en el propio amplificador — solo se necesita una PC con GEN5 para el setup inicial, no para el uso normal.

Esto habilita leer los 6 canales de fuerza directamente con un ADC propio (ADS1256), en paralelo con el resto de sensores, sin depender del software de AMTI durante la operación.

**Confirmación con fuente oficial (14/08/2026):** se obtuvo el manual técnico completo del amplificador (AMTI Gen 5 User Manual, guardado en `Estado-del-arte/SENSORES DE FUERZA/AMTI-Gen5-User-Manual.pdf`), que confirma el pinout del conector DB25S ya identificado:

| Pin | Señal | Pin | Señal |
|---|---|---|---|
| 1 | Fx analog out | 14 | Voltage Ref |
| 2 | Fy analog out | 15–20 | Ground Ref |
| 3 | Fz analog out | 21–22 | NC |
| 4 | Mx analog out | 23 | Auto zero (opcional) |
| 5 | My analog out | 24–25 | Power (opcional) |
| 6 | Mz analog out | 7–13 | NC / power (opcional) |

## 4. Rol del IMU frente al encoder

Se resolvió la duda sobre si el IMU seguía siendo necesario ahora que cada DOF tiene su propio sensor dedicado: el IMU se mantiene, no como medición primaria de ángulo (eso lo hace el encoder, con mayor precisión), sino como **validación cruzada** — detecta holgura, backlash o desalineamiento del pivote que el encoder solo no puede ver.

## 5. Selección de sensor de posición

Se descartaron sensores de proximidad tipo ultrasónico (resolución insuficiente, ~cm, haz cónico) y se aclaró que un magnetómetro simple no mide posición lineal (mide orientación respecto al campo terrestre, no distancia). Se confirmó el láser ToF como la opción recomendada, ya alineada con lo indicado por Dante.

## 6. Sincronización

Se evaluaron tres caminos para sincronizar el reloj de la plataforma de fuerza con el resto del sistema: lectura directa por ADC propio (ideal, un solo reloj), pulso de disparo compartido vía la entrada Genlock/Trigger del amplificador (confirmada físicamente en el panel trasero), y Lab Streaming Layer como estándar de la industria si se necesitara sincronizar sistemas en máquinas separadas.

## 7. Costo: conectar vs. construir

Se comparó el costo de instrumentar la plataforma AMTI ya existente (~USD 50 en ADC y cableado) frente a construir una plataforma de fuerza propia desde cero (celdas de carga, placa rígida, acondicionamiento por canal, y sobre todo calibración multi-eje para eliminar crosstalk — el verdadero costo, en tiempo de ingeniería). Conectar la existente resulta claramente más barato y de menor riesgo para el cronograma.

## Diagrama de arquitectura

![Arquitectura de sensores por DOF — integración AMTI](https://raw.githubusercontent.com/ttanno/LIBRA-26-2-INSTRUMENTACION-DE-SIMULADOR-DE-MARCHA/main/Evidencias/arquitectura-sensores-AMTI-S2.png)

Diagrama de las cuatro rutas de sensado (GRF, pylon, traslación, rotación) convergiendo en un data frame sincronizado vía ESP32.

## Próximos pasos

- Confirmar el modo de salida analógica configurado actualmente en el amplificador (MSA-6 Compatible vs. Fully Conditioned) sin alterar la configuración compartida del laboratorio.
- Ubicar el certificado de calibración físico de la plataforma (matriz de sensibilidad real, no la de ejemplo).
- Solicitar a soporte de AMTI el pinout/manual técnico oficial del OPT-SC (formulario enviado, pendiente respuesta).
- Diseñar la interfaz de lectura de los 6 canales con el ADS1256.
- Actualizar Secc. 4.1, 9 y 10 de la revisión bibliográfica con el cambio de prioridad GRF/pylon y la arquitectura de sensores por DOF.
