**INFORME SEMANAL DE AVANCE DEL PROYECTO DE INVESTIGACIÓN**

**Proyecto:** Diseño e integración de una plataforma móvil que incluya sensores para medir variables cinemáticas y cinéticas en un simulador de marcha para validar prótesis transtibiales

**Período del informe:** 31/07/2026 al 07/08/2026

**Responsable:** Alessandro Jesus Felix Tello

**1. Resumen Ejecutivo**

Durante la primera semana del proyecto se realizó la revisión del estado del arte correspondiente a las semanas 1-2 del cronograma (8 bloques temáticos, 39 referencias en formato IEEE) y se derivaron requerimientos técnicos preliminares para las 4 áreas del proyecto. Se verificaron los valores numéricos de la norma ISO 10328 contra fuentes primarias (P4 y P5 confirmados; P3 y P6 quedan pendientes) y se corrigieron 7 de las 11 referencias bibliográficas que estaban incompletas. Además, se confirmó que ya existe una estructura mecánica base construida en el laboratorio y que el simulador es transtibial únicamente (no multi-protésico, aunque sí permite ajustar el nivel de amputación simulado). Esto no cambia el Objetivo 1, pero sí el punto de partida del diseño mecánico: no se parte de cero, y es posible que se requiera modificar o rediseñar partes de la estructura existente para integrar los nuevos sensores. Queda pendiente confirmarlo formalmente con el asesor.

**2. Actividades Realizadas**

1. **Revisión y ampliación del estado del arte.** Documento de revisión bibliográfica con 8 bloques temáticos y 39 referencias en formato IEEE: simuladores de marcha con sensórica embebida, validación de IMU frente a sistemas ópticos, calibración de IMU de bajo costo, celdas de carga en prótesis, protocolos de calibración robótica/mecatrónica, normas ISO de ensayo de prótesis, arquitecturas de software de sincronización multi-sensor y diseño mecánico de plataformas móviles.

2. **Síntesis frente a objetivos del proyecto.** Tabla que cruza los 8 bloques del estado del arte con los 4 objetivos específicos. Brecha central identificada: ningún sistema revisado integra plataforma móvil + IMU + celda de carga + software sincronizado + validación normativa en una arquitectura de bajo costo.

3. **Requerimientos técnicos preliminares.** Especificaciones orientativas para las 4 áreas del proyecto (DOF, tipo de IMU, rango de fuerza de la celda de carga, arquitectura de software, protocolo de validación), incluyendo la aclaración de alcance del sensado (continuo, sin lazo de control en tiempo real).

4. **Verificación normativa (ISO 10328).** P4 confirmado (proof 2065 N, ultimate 4130 N, cíclico 1230 N) y P5 corregido (2240/4480 N) contra fuentes primarias; P3 tiene un candidato sin confirmar y P6 sigue sin verificar. Recomendación adoptada: dimensionar la celda de carga sobre P5 salvo que se necesite cubrir usuarios >100 kg.

5. **Consolidación de referencias bibliográficas.** 7 de 11 referencias incompletas corregidas ([1], [5], [6], [13], [16], [31], [34]) con autor/año/revista/DOI verificados; quedan pendientes [2] (parcial), [4], [12], [15]. Se guardaron además notas de texto completo de 3 fuentes adicionales relevantes (celda de carga tipo strain gauge, arquitecturas de software embebido, ensayo ISO 10328 de un pie protésico real).

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

**Norma ISO 10328 es un documento de pago con valores discrepantes entre fuentes secundarias.** Causa probable: la norma es un documento de pago (ISO Store), y distintos papers reportan valores de carga para componentes distintos (socket vs. rodilla vs. pilón) o ediciones distintas de la norma (2006 vs. 2016). Impacto: riesgo de dimensionar la celda de carga con un valor incorrecto. Acción correctiva: acceso institucional gratuito vía sala de lectura virtual de Normas Técnicas Peruanas (INACAL, biblioteca PUCP), priorizando fuentes que citan textualmente la norma vigente (2016) sobre resúmenes de terceros.

**Metadatos web incompletos en fuentes académicas.** Causa probable: la vista previa/metadatos de una página web de un artículo no siempre incluye la lista completa de autores (solo el autor de correspondencia), como ocurrió con la referencia [31]. Impacto: riesgo de citar mal la autoría si no se verifica contra el texto completo. Acción correctiva: para referencias marcadas como inciertas, se descargó y leyó el texto completo del PDF en vez de confiar solo en los metadatos de la página.

**5. Lecciones Aprendidas / Recomendaciones**

Es indispensable verificar los valores numéricos de normas técnicas contra fuentes primarias (o secundarias que citen textualmente la norma con permiso de reproducción) antes de utilizarlos en decisiones de diseño. De forma similar, los metadatos de una página web no son suficientes para verificar autoría de una referencia — el texto completo del PDF puede revelar información distinta (como ocurrió con [31], que tiene 4 autores y no 1). También quedó claro que antes de planificar actividades de diseño mecánico conviene verificar el estado real del equipo físico disponible en el laboratorio: de no haberse revisado las fotos del simulador, se habría planificado erróneamente el diseño de una estructura que ya existe. Para las próximas semanas, se recomienda obtener la confirmación formal del asesor sobre el estado del simulador existente antes de avanzar en el diseño de los soportes de sensores.

**6. Actividades Planificadas para la Siguiente Semana**

| Actividad | Objetivo |
| :---- | :---- |
| Confirmar formalmente con el asesor el estado del simulador existente (estructura base ya construida, transtibial únicamente) | Evitar retrabajo y alinear expectativas antes de diseñar soportes de sensores |
| Diseñar los soportes/adaptadores de montaje para IMU y celda de carga sobre la plataforma existente | Objetivo específico 1 y 2 |
| Completar las referencias bibliográficas pendientes ([2], [4], [12], [15]) y decidir si se incorpora el método de marcadores M1-M4 al protocolo de validación | Dejar la revisión bibliográfica y el protocolo de validación (Objetivo 4) listos para el informe final |

**7. Anexos o Evidencias**

Documento `Estado-del-arte/Revision bibliografica - Semana 1-2.md` (revisión del estado del arte completa, síntesis, requerimientos técnicos y contexto del simulador). Notas de texto completo de 3 fuentes adicionales guardadas en `Estado-del-arte/SENSORES DE FUERZA`, `Estado-del-arte/SOFTWARE` y `Estado-del-arte/ISO`. Fotos del simulador físico y del método de marcadores M1-M4 en `Evidencias/simulador/` (referenciadas e incrustadas en la revisión bibliográfica, Sección 8.1-8.2).
