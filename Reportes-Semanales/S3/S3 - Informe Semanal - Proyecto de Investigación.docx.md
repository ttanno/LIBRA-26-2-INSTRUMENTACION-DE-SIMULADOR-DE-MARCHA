**INFORME SEMANAL DE AVANCE DEL PROYECTO DE INVESTIGACIÓN**

**Proyecto:** Diseño e integración de una plataforma móvil que incluya sensores para medir variables cinemáticas y cinéticas en un simulador de marcha para validar prótesis transtibiales

**Período del informe:** 15/08/2026 al 21/08/2026

**Responsable:** Alessandro Jesus Felix Tello

**1. Resumen Ejecutivo**

Durante la tercera semana el trabajo se concentró en dos frentes: la selección de sensores, organizada por variable sensada en vez de por comparación aislada de componentes, y el inicio de la etapa de simulación estructural de la placa del pylon. En sensores, quedaron definidos el sensor de distancia (TF-Luna) y el de ángulo/rotación (AS5600), con una comparativa completa documentada; el IMU probablemente sea el MPU6050 (la opción más simple, ya disponible en el laboratorio); y la celda de fuerza sigue abierta, con la búsqueda enfocada esta semana en marcas y proveedores peruanos. En simulación, se definieron las propiedades de material e impresión en una hoja de cálculo propia (PETG) y se corrieron cinco configuraciones distintas de la placa en ANSYS (tres espesores sólidos y dos variantes con menos material), encontrando que solo la placa sólida de 25 mm cumple un factor de seguridad mayor a 1 hasta el momento. Sigue sin resolverse formalmente con los asesores la disyuntiva de prioridad entre GRF y pylon planteada la semana pasada.

**2. Actividades Realizadas**

1. **Comparativa de sensores por variable sensada.** Se armó una comparativa con tablas para cada sensor aún abierto (distancia, ángulo, fuerza), en vez de un cuadro único de componentes, documentada en `Estado-del-arte/Sensores-LIBRA-Presentacion.pptx`. Resultado: sensor de distancia (TF-Luna, 0.2–8 m, 100 Hz, ~US$25) y de ángulo/rotación (AS5600, 0.088° de resolución, I2C, ~US$3–8) definidos; alternativas descartadas documentadas con su justificación.

2. **Selección probable de IMU.** Se evaluó el rol del IMU (validación cruzada del encoder, no medición primaria) frente a tres candidatos (MPU6050, MPU9250+HMC5883L, BNO055). Resultado: MPU6050 como opción probable — es la más simple, ya está disponible en el inventario del laboratorio y no se justifica la fusión de sensores de 9 ejes de un BNO055 para un rol de validación cruzada. Queda pendiente confirmar contra el inventario si las unidades registradas son físicamente distintas.

3. **Búsqueda de sensor de fuerza en proveedores peruanos.** La comparativa de celdas de carga por nivel de costo (bajo costo/DIY, semi-profesional, grado investigación) ya existía de la semana anterior; esta semana el foco pasó específicamente a buscar marcas/proveedores peruanos, para reducir costo de importación y tiempo de entrega. Resultado: sin candidato local cerrado todavía.

4. **Definición de materiales y configuración de impresión.** Se armó un documento Excel propio (`Estado-del-arte/SIMULADOR DE MARCHA/LIBRA_Config_Impresion_y_Calculo_Material.xlsx`) con las propiedades de material (PETG) y los parámetros de impresión (altura de capa, número de paredes, patrón y porcentaje de relleno) como insumo directo para el Engineering Data de la simulación en ANSYS.

5. **Simulación estructural de la placa (ANSYS).** Se corrieron cinco configuraciones distintas de la placa (Static Structural, mismo material): tres espesores sólidos (15, 20 y 25 mm) y dos variantes con menos material (20 mm con vaciado central, 15 mm con refuerzo en cruz). Resultado: el factor de seguridad mínimo mejora con el espesor (0.52 → 0.85 → 1.15) y solo la placa sólida de 25 mm cumple el criterio de factor de seguridad >1; las variantes livianas (vaciado central: 0.92, refuerzo en cruz: 0.63) mejoran frente a su espesor base pero no cruzan el umbral todavía. En las cinco corridas el punto crítico se ubica en la misma zona, cerca de un agujero de perno.

**3. Actividades Planificadas vs. Actividades Ejecutadas**

| Actividad Planificada | Estado (Ejecutada / En proceso / No ejecutada) | Comentarios (justificación si aplica) |
| :---- | :---- | :---- |
| Confirmar el modo de salida analógica del amplificador AMTI | No ejecutada | El foco de la semana se volcó a la comparativa de sensores y a iniciar la simulación estructural; se retoma la próxima semana |
| Diseñar la interfaz de lectura de los 6 canales de la AMTI con el ADS1256 | No ejecutada | Mismo motivo que el punto anterior |
| Continuar la selección y definición de ubicación del IMU y la celda de carga | En proceso | IMU probablemente MPU6050 (pendiente confirmar contra inventario); celda de carga sigue abierta, ahora buscando específicamente proveedores peruanos |
| Actualizar las secciones 4.1, 9 y 10 de la revisión bibliográfica | No ejecutada | Sigue pendiente desde la Semana 2 |
| Completar las referencias bibliográficas pendientes | No ejecutada | Sigue pendiente |
| *(no planificada)* Comparativa de sensores de distancia y ángulo, con definición de candidato final | Ejecutada | Trabajo adicional no incluido en el plan de la semana anterior |
| *(no planificada)* Simulación estructural ANSYS de la placa (cinco configuraciones) | Ejecutada | Trabajo adicional no incluido en el plan de la semana anterior |

**4. Dificultades o Problemas Presentados**

**Disyuntiva de prioridad GRF vs. pylon sigue sin resolver.** Desde la Semana 2 Dante había confirmado GRF (plataforma AMTI) como prioridad y el pylon como secundario; entrando a la Semana 3, Victoria pidió priorizar el pylon. La discrepancia sigue sin resolverse formalmente por escrito con ambos asesores, lo que retrasó el trabajo directo sobre la integración de la AMTI (ver actividades no ejecutadas arriba). Mientras se resuelve, se avanzó en paralelo la investigación de sensores del lado del pylon.

**Factor de seguridad por debajo de 1 en la mayoría de configuraciones de placa simuladas.** Solo la configuración sólida de 25 mm cumple el criterio; las demás (15 mm, 20 mm, y las variantes con menos material) quedan por debajo del umbral en el mismo punto crítico, cerca de un agujero de perno. Se seguirá iterando la próxima semana combinando espesor y refuerzo/vaciado para buscar una solución que cumpla sin sobredimensionar toda la placa.

**5. Lecciones Aprendidas / Recomendaciones**

Comparar variantes de geometría (vaciado central, refuerzo en cruz) además de simplemente escalar el espesor permite encontrar soluciones más eficientes en peso/material — por ejemplo, la placa de 20 mm con vaciado central superó en factor de seguridad a la placa sólida del mismo espesor. También quedó claro que, para sensores con rol de validación cruzada (como el IMU en esta arquitectura), conviene evitar sobre-especificar el componente: el MPU6050, la opción más simple y ya disponible, es suficiente y evita tiempo/costo de compra de una unidad de gama alta que no aporta valor adicional al rol que cumple.

**6. Actividades Planificadas para la Siguiente Semana**

| Actividad | Objetivo |
| :---- | :---- |
| Resolver formalmente con Dante y Victoria la prioridad GRF vs. pylon de la semana | Evitar seguir avanzando sobre un frente que luego se tenga que repriorizar |
| Definir el diseño final de la placa combinando refuerzo/vaciado central con un espesor intermedio (entre 20 y 25 mm) | Objetivo específico 1 — buscar factor de seguridad >1 con menos material que la opción sólida de 25 mm |
| Cerrar la búsqueda de sensor de fuerza en proveedores peruanos | Objetivo específico 2 |
| Confirmar el MPU6050 como candidato final de IMU contra el inventario del laboratorio | Objetivo específico 2 |
| Confirmar el modo de salida analógica del amplificador AMTI y diseñar la interfaz de lectura con el ADS1256 | Objetivo específico 2 y 3 |
| Actualizar las secciones 4.1, 9 y 10 de la revisión bibliográfica y completar las referencias pendientes | Dejar la revisión bibliográfica alineada con las decisiones tomadas |

**7. Anexos o Evidencias**

Documento `Reportes-Semanales/S3/Resumen-Semana3.md` (resumen narrativo de la semana, con las tablas comparativas de sensores y el detalle de las cinco corridas de simulación). Comparativa `Estado-del-arte/Sensores-LIBRA-Presentacion.pptx` y `Estado-del-arte/SENSORES DE FUERZA/PYLON/Comparativa-Sensores-Fuerza-Axial-Pylon.md`. Configuración de material `Estado-del-arte/SIMULADOR DE MARCHA/LIBRA_Config_Impresion_y_Calculo_Material.xlsx`. Imágenes de las cinco corridas de simulación en `Evidencias/simulacion-ansys/`. Lista de trabajo activa en `Reportes-Semanales/S3/Pendientes.md`.
