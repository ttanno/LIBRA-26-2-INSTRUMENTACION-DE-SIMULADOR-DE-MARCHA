**INFORME SEMANAL DE AVANCE DEL PROYECTO DE INVESTIGACIÓN**

**Proyecto:** Diseño e integración de una plataforma móvil que incluya sensores para medir variables cinemáticas y cinéticas en un simulador de marcha para validar prótesis transtibiales

**Período del informe:** 31/07/2026 al 07/08/2026

**Responsable:** Alessandro Jesus Felix Tello

**1. Resumen Ejecutivo**

Durante la primera semana del proyecto se realizó una revisión del estado del arte de alrededor de 40 referencias en formato IEEE, cubriendo los principales bloques temáticos del proyecto, y se derivaron requerimientos técnicos preliminares para sus 4 áreas. Se verificaron los valores normativos clave de la ISO 10328 contra fuentes primarias y se corrigieron varias referencias bibliográficas que estaban incompletas. También se trabajó en entender el funcionamiento, el alcance y las limitantes del simulador ya existente en el laboratorio, conversando con un compañero de laboratorio, lo que ayudó a definir mejor el alcance real del proyecto. Queda pendiente confirmar este alcance formalmente con el asesor.

**2. Actividades Realizadas**

1. **Revisión y ampliación del estado del arte.** Se amplió y organizó por bloques temáticos la revisión bibliográfica del proyecto (simuladores de marcha, sensórica IMU, celdas de carga, normas técnicas de prótesis, arquitecturas de software, diseño mecánico de plataformas), como base transversal para los 4 objetivos específicos. Resultado: documento de revisión bibliográfica consolidado en formato IEEE.

2. **Síntesis frente a objetivos del proyecto.** Se contrastó lo encontrado en el estado del arte contra cada uno de los 4 objetivos específicos del proyecto. Resultado: identificación de la brecha central que justifica el proyecto — ningún sistema revisado integra plataforma móvil, sensórica de fuerza y cinemática, software sincronizado y validación normativa en una sola arquitectura de bajo costo.

3. **Requerimientos técnicos preliminares.** Se derivaron especificaciones orientativas para las áreas de diseño mecánico, sensórica, software y validación (Objetivos 1 a 4), incluyendo la aclaración de que el sensado de la plataforma será continuo, sin lazo de control en tiempo real.

4. **Verificación normativa (ISO 10328).** Se verificaron contra fuentes primarias los rangos de fuerza y resistencia que la norma exige según el peso simulado del usuario, insumo directo para el Objetivo 2 (dimensionamiento de la celda de carga). Se confirmaron los niveles de carga más relevantes para el proyecto; los correspondientes a pesos menos comunes quedan pendientes de verificar. Resultado: recomendación de dimensionar la celda de carga sobre el nivel de carga que cubre el rango de usuarios más probable del proyecto.

5. **Consolidación de referencias bibliográficas.** Se corrigieron las referencias que estaban incompletas, verificando autor, año, revista y DOI contra las fuentes originales, para asegurar la trazabilidad del estado del arte (Objetivos 1 a 4). Quedan pendientes las que no están indexadas o no tienen autor identificable. Resultado: notas de texto completo guardadas para fuentes adicionales sobre celdas de carga, software embebido y ensayos normativos.

6. **Entendimiento del simulador existente.** Revisión de fotos del simulador físico y conversación con un compañero de laboratorio sobre su geometría y alcance protésico. Se confirmó que ya existe una estructura mecánica base construida y que el simulador es transtibial únicamente, con nivel de amputación ajustable. Pendiente confirmación formal del asesor.

**3. Actividades Planificadas vs. Actividades Ejecutadas**

| Actividad Planificada | Estado (Ejecutada / En proceso / No ejecutada) | Comentarios (justificación si aplica) |
| :---- | :---- | :---- |
| Revisión del estado del arte | Ejecutada | Completada según cronograma (semanas 1-2) |
| Definición de requerimientos técnicos preliminares | Ejecutada | Actualizada tras confirmar que ya existe una estructura base construida; sujeta a validación formal con el asesor |
| Verificación de valores de norma ISO 10328 | En proceso | P4 y P5 verificados con fuente primaria; P3 tiene candidato sin confirmar, P6 sigue pendiente. Se recomienda no seguir invirtiendo tiempo salvo que se necesite cubrir usuarios >100 kg |
| Completar citas bibliográficas incompletas | En proceso | 7 de 11 referencias resueltas esta semana; quedan [2] (parcial), [4], [12], [15] |
| Confirmar estado del simulador existente | Ejecutada (informal) | Confirmado con compañero de laboratorio; pendiente confirmación formal del asesor |

**4. Dificultades o Problemas Presentados**

**Acceso a la norma ISO 10328.** Es un documento de pago; no se consiguió vía INACAL ni otras fuentes institucionales. Los valores de carga se verificaron de forma indirecta, contra papers que citan la norma. Se seguirá buscando acceso institucional.

**Suspensión del sistema de bibliotecas por matrícula.** El Sistema de Bibliotecas de la PUCP suspendió el acceso a bases de datos y el servicio de préstamo desde el 4 de agosto, por el proceso de matrícula 2026-2. Limita el acceso a fuentes indexadas hasta que se restablezca el jueves 13 de agosto.

**Metadatos web incompletos en fuentes académicas.** Los metadatos de algunas páginas web no incluyen todos los autores de un artículo, con riesgo de citar mal la autoría. Se verificó contra el texto completo del PDF en los casos con duda.

**5. Lecciones Aprendidas / Recomendaciones**

Conviene verificar siempre contra fuentes primarias, tanto los valores numéricos de normas técnicas como la autoría de las referencias — los metadatos web y resúmenes de terceros pueden ser incompletos o incorrectos. También quedó claro que antes de planificar el diseño mecánico conviene verificar primero el estado real del equipo disponible en el laboratorio, para no planificar sobre supuestos incorrectos. Se recomienda obtener la confirmación formal del asesor sobre el estado del simulador antes de avanzar en el diseño de los soportes de sensores.

**6. Actividades Planificadas para la Siguiente Semana**

| Actividad | Objetivo |
| :---- | :---- |
| Confirmar formalmente con el asesor el estado del simulador existente | Evitar retrabajo y alinear expectativas antes de diseñar soportes de sensores |
| Definir el diagrama de bloques del sistema (arquitectura general: sensores, procesamiento, adquisición) | Objetivo específico 1, 2 y 3 |
| Seleccionar el sensor de IMU y de celda de carga más adecuados para el propósito (sin sobre-especificar) y definir dónde se montará cada uno sobre la plataforma | Objetivo específico 1 y 2 |
| Definir el material de absorción de impacto para la fase de apoyo (resistencia vs. elasticidad; la plataforma actual usa TPU) | Objetivo específico 1 |
| Elaborar un boceto de la ubicación de cada componente (sensores, procesador, etc.) sobre la plataforma | Objetivo específico 1 y 2 |
| Completar las referencias bibliográficas pendientes | Dejar la revisión bibliográfica lista para el informe final |

**7. Anexos o Evidencias**

Documento `Estado-del-arte/Revision bibliografica - Semana 1-2.md` (revisión del estado del arte completa, síntesis, requerimientos técnicos y contexto del simulador). Notas de texto completo de 3 fuentes adicionales guardadas en `Estado-del-arte/SENSORES DE FUERZA`, `Estado-del-arte/SOFTWARE` y `Estado-del-arte/ISO`. Fotos del simulador físico y del método de marcadores M1-M4 en `Evidencias/simulador/` (referenciadas e incrustadas en la revisión bibliográfica, Sección 8.1-8.2).
