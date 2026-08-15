**INFORME SEMANAL DE AVANCE DEL PROYECTO DE INVESTIGACIÓN**

**Proyecto:** Diseño e integración de una plataforma móvil que incluya sensores para medir variables cinemáticas y cinéticas en un simulador de marcha para validar prótesis transtibiales

**Período del informe:** 08/08/2026 al 14/08/2026

**Responsable:** Alessandro Jesus Felix Tello

**1. Resumen Ejecutivo**

Durante la segunda semana el foco del proyecto cambió de la revisión bibliográfica a una decisión de arquitectura concreta, tras una reunión con el asesor. Dante definió una arquitectura de sensado con un sensor dedicado por cada grado de libertad del simulador: la fuerza de reacción del suelo (GRF), medida con una plataforma de fuerza, pasa a ser la prioridad, mientras que la celda de carga en la interfaz pylon-plataforma (antes la ubicación principal) pasa a ser secundaria. Además se confirmó que el laboratorio ya cuenta físicamente con la plataforma de fuerza necesaria (AMTI BP400600), lo que cambió el problema de "qué plataforma comprar" a "cómo integrar la que ya existe". Se investigó esa integración, identificando una vía de lectura en tiempo real (salida analógica del amplificador) independiente del software oficial de AMTI, y se documentó su pinout y las fórmulas de conversión necesarias. También se aclaró el rol del IMU frente al encoder de rotación y se definió la estrategia de sensado para traslación (láser).

**2. Actividades Realizadas**

1. **Reunión con el asesor — arquitectura de sensores por DOF.** Dante confirmó una arquitectura con un sensor dedicado por grado de libertad: GRF (prioridad, plataforma de fuerza), interfaz pylon-plataforma (secundaria), traslación horizontal/vertical (láser) y rotación de flexo-extensión (encoder/potenciómetro). Requisito explícito: la plataforma de fuerza debe integrarse mecánicamente con el simulador y adquirir datos de forma sincrónica con el resto de sensores.

2. **Confirmación y caracterización del equipo existente.** Se confirmó que el laboratorio ya posee una plataforma de fuerza AMTI BP400600 con amplificador Optima OPT-SC, evitando la necesidad de adquirir un equipo nuevo. Resultado: el problema pasa de selección de plataforma a integración de la ya disponible.

3. **Investigación de integración de la plataforma de fuerza.** Se identificó que el software oficial de AMTI (GEN5 → NetForce → BioAnalysis) es un flujo de grabación por lotes, no apto para lectura en tiempo real ni para un eventual lazo de control. Se confirmó físicamente que el amplificador tiene una salida analógica independiente del USB, y se obtuvo (documentación oficial del fabricante) el pinout completo del conector de salida y las fórmulas de conversión de voltaje a fuerza para los dos modos de operación posibles. Resultado: camino de integración en tiempo real definido, sin depender del software propietario durante la operación.

4. **Aclaración del rol del IMU frente al encoder.** Se resolvió si el IMU seguía siendo necesario ahora que cada grado de libertad tiene su propio sensor dedicado: se mantiene, no como medición primaria de ángulo, sino como validación cruzada del encoder (detecta holgura o desalineamiento mecánico que el encoder solo no puede ver).

5. **Definición de arquitectura de sensor de posición.** Se descartaron sensores de proximidad ultrasónicos (resolución insuficiente) y se aclaró la diferencia entre un magnetómetro simple (no mide posición) y un encoder magnético lineal. Se confirmó el láser de distancia (ToF) como la opción recomendada.

6. **Comparación de costo — conectar vs. construir.** Se justificó la decisión de integrar la plataforma de fuerza existente en vez de construir una nueva, por menor costo y menor riesgo de cronograma frente al trabajo de calibración multi-eje que implicaría una plataforma propia.

**3. Actividades Planificadas vs. Actividades Ejecutadas**

| Actividad Planificada | Estado (Ejecutada / En proceso / No ejecutada) | Comentarios (justificación si aplica) |
| :---- | :---- | :---- |
| Confirmar formalmente con el asesor el estado del simulador existente | Ejecutada (ampliada) | Se obtuvo, además, la arquitectura completa de sensores por DOF, no solo la confirmación del simulador |
| Definir el diagrama de bloques del sistema | Ejecutada | Diagrama de arquitectura de sensores por DOF, incluyendo la ruta de integración de la plataforma AMTI (ver anexos) |
| Seleccionar el sensor de IMU y de celda de carga, y definir su ubicación | En proceso | Rol del IMU aclarado (validación cruzada); la celda de carga mantiene el candidato de la semana 1, pero pasa a ubicación secundaria tras el cambio de prioridad hacia GRF |
| Definir el material de absorción de impacto para la fase de apoyo | No ejecutada | No fue foco esta semana; el trabajo se concentró en la arquitectura de sensado tras la reunión con el asesor |
| Elaborar un boceto de la ubicación de cada componente sobre la plataforma | En proceso | Diagrama de arquitectura lógica completo; falta el boceto físico/mecánico de ubicación sobre la plataforma real |
| Completar las referencias bibliográficas pendientes | No ejecutada | Postergado; el foco de la semana fue la decisión de arquitectura con el asesor |

**4. Dificultades o Problemas Presentados**

**Documentación oficial de AMTI incompleta para el caso de uso.** El manual de operación disponible en el laboratorio cubre el uso del software (calibración, captura, análisis) pero no el acceso a la salida analógica ni las fórmulas de conversión necesarias para una integración de bajo nivel. Se resolvió consiguiendo el manual técnico completo del amplificador (Gen 5 User Manual) por fuera del material del laboratorio.

**Configuración del amplificador es equipo compartido.** No se puede cambiar el modo de salida analógica (actualmente parece estar en modo MSA-6 Compatible, más complejo de convertir a unidades de fuerza) sin afectar a otros usuarios del laboratorio. Se documentó también la ruta de conversión para ese modo, como alternativa a solicitar el cambio de configuración.

**5. Lecciones Aprendidas / Recomendaciones**

Antes de plantear el diseño o la compra de sensores nuevos, conviene verificar primero qué equipo ya existe físicamente en el laboratorio — este hallazgo cambió la prioridad completa del proyecto, de construir/adquirir una plataforma de fuerza a integrar la ya disponible. También quedó claro que la documentación de operación de un equipo no necesariamente cubre lo necesario para integración a nivel de señal; en esos casos conviene buscar directamente la documentación técnica/de servicio del fabricante, no solo el manual de usuario.

**6. Actividades Planificadas para la Siguiente Semana**

| Actividad | Objetivo |
| :---- | :---- |
| Confirmar el modo de salida analógica configurado actualmente en el amplificador (sin alterar la configuración compartida) y ubicar la matriz de calibración real de la unidad | Objetivo específico 2 y 3 |
| Diseñar la interfaz de lectura de los 6 canales analógicos de la plataforma de fuerza con el ADC (ADS1256) | Objetivo específico 2 y 3 |
| Continuar la selección y definición de ubicación del IMU y la celda de carga sobre la plataforma | Objetivo específico 1 y 2 |
| Actualizar las secciones 4.1, 9 y 10 de la revisión bibliográfica con el cambio de prioridad GRF/pylon y la nueva arquitectura de sensores por DOF | Dejar la revisión bibliográfica alineada con las decisiones tomadas esta semana |
| Completar las referencias bibliográficas pendientes | Dejar la revisión bibliográfica lista para el informe final |

**7. Anexos o Evidencias**

Documento `Reportes-Semanales/S2/Resumen-Semana2.md` (resumen narrativo de la semana). Diagrama `Evidencias/arquitectura-sensores-AMTI-S2.png` (arquitectura de sensores por DOF y ruta de integración de la plataforma AMTI). Manuales técnicos de la plataforma de fuerza guardados en `Estado-del-arte/SENSORES DE FUERZA/` (manual de operación del laboratorio y Gen 5 User Manual, con el pinout y las fórmulas de conversión). Detalle completo de hallazgos y pendientes en `Reportes-Semanales/S1/Pendientes.md`.
