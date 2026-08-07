**INFORME SEMANAL DE AVANCE DEL PROYECTO DE INVESTIGACIÓN**

**Proyecto:** Diseño e integración de una plataforma móvil que incluya sensores para medir variables cinemáticas y cinéticas en un simulador de marcha para validar prótesis transtibiales

**Período del informe:** 31/07/2026 al 07/08/2026

**Responsable:** Alessandro Jesus Felix Tello

**1. Resumen Ejecutivo**

Durante la primera semana del proyecto se realizó la revisión del estado del arte correspondiente a las semanas 1-2 del cronograma (8 bloques temáticos, 39 referencias en formato IEEE) y se derivaron requerimientos técnicos preliminares para las 4 áreas del proyecto. Se verificaron los valores numéricos de la norma ISO 10328 contra fuentes primarias (P4 y P5 confirmados; P3 y P6 quedan pendientes) y se corrigieron 7 de las 11 referencias bibliográficas que estaban incompletas. Al cierre de la semana surgió una aclaración de alcance relevante, tras revisar fotos del simulador físico ya construido en el laboratorio y conversarlo con un compañero de laboratorio: el Objetivo 1 no es diseñar la plataforma mecánica desde cero, sino instrumentar una plataforma que ya existe, y el simulador es transtibial únicamente (no multi-protésico, aunque sí permite ajustar el nivel de amputación simulado). Esta aclaración cambia el alcance real del Objetivo 1 y está documentada en la revisión bibliográfica; queda pendiente confirmarla formalmente con el asesor.

**2. Actividades Realizadas**

1. **Revisión bibliográfica inicial.** Qué: se revisaron y organizaron en tablas comparativas las fuentes correspondientes a simuladores de marcha con sensórica embebida, validación de IMU frente a sistemas ópticos, calibración de IMU de bajo costo, y celdas de carga en prótesis. Cómo: búsqueda documental estructurada y análisis comparativo por variables medidas, ventajas y limitaciones. Para qué: identificar el estado actual de la tecnología y las brechas que justifican el desarrollo de la plataforma. Resultado: documento de revisión bibliográfica con 4 bloques temáticos y 22 fuentes iniciales.

2. **Ampliación del estado del arte.** Qué: se incorporaron 4 bloques adicionales (protocolos de calibración robótica/mecatrónica, normas ISO de ensayo de prótesis, arquitecturas de software de sincronización multi-sensor, diseño mecánico de plataformas móviles). Resultado: 16 referencias adicionales incorporadas y citadas en formato IEEE.

3. **Síntesis frente a objetivos del proyecto.** Qué: se construyó una tabla que cruza los 8 bloques del estado del arte con los 4 objetivos específicos del proyecto. Resultado: tabla de síntesis con la brecha central identificada — ningún sistema revisado integra plataforma móvil + IMU + celda de carga + software sincronizado + validación normativa en una arquitectura de bajo costo.

4. **Derivación de requerimientos técnicos preliminares.** Qué: se tradujeron los hallazgos bibliográficos en especificaciones técnicas orientativas (DOF, tipo de IMU, rango de fuerza de la celda de carga, arquitectura de software, protocolo de validación). Resultado: sección de requerimientos técnicos, incluyendo aclaración de alcance acordada con el equipo (sensado continuo, sin lazo de control en tiempo real).

5. **Verificación de valores normativos (ISO 10328).** Qué: se contrastaron los valores de carga (niveles P3-P6) reportados inicialmente contra fuentes primarias. Resultado: P4 confirmado (proof 2065 N, ultimate 4130 N, cíclico 1230 N) y P5 corregido (2240/4480 N); P3 tiene un candidato sin confirmar (Bonacini et al. 2009) y P6 sigue sin verificar. Recomendación adoptada: dimensionar la celda de carga sobre P5 salvo que se necesite cubrir usuarios >100 kg.

6. **Corrección de referencias bibliográficas incompletas.** Qué: se completaron autor/año/revista/DOI de 7 de las 11 referencias marcadas como incompletas ([1], [5], [6], [13], [16], [31], [34]). Cómo: búsqueda cruzada y, en el caso de [31], descarga y lectura del texto completo del PDF, que reveló que la referencia tenía en realidad 4 autores y no 1 (los metadatos web solo mostraban al autor de correspondencia). También se corrigió el nombre de la revista de la referencia [32] (es *Medical Engineering & Physics*, no *Mechanism and Machine Theory* como se había reportado). Resultado: 7 referencias verificadas; [2] parcialmente verificado; [4], [12], [15] siguen sin resolver (fuentes no indexadas o sin autor identificable).

7. **Descarga de material de referencia adicional.** Qué: se guardaron notas de texto completo (extraídas de PDFs de acceso abierto) de 3 fuentes adicionales relevantes: diseño/fabricación de celda de carga tipo strain gauge (Al-Dahiree et al. 2022), arquitecturas de software embebido para wearables multi-sensor (Toptsis et al. 2026), y valores de ensayo ISO 10328 de un pie protésico real (Bonacini et al. 2009). Se creó la subcarpeta `Estado-del-arte/SOFTWARE` para la segunda. Nota: el sandbox de trabajo no tiene permiso de red para descargar directamente los PDF binarios, por lo que se guardó el texto completo extraído en su lugar.

8. **Aclaración de alcance del Objetivo 1.** Qué: al revisar fotos del simulador físico existente en el laboratorio, se confirmó que la estructura mecánica (traslación horizontal por riel + cadena, traslación vertical por husillo + motor, punto de flexo-extensión) ya está construida de un proyecto anterior, y que el simulador es transtibial únicamente (con nivel de amputación ajustable: alto, medio o bajo), no multi-protésico. Cómo: análisis de fotografías del equipo y conversación con un compañero de laboratorio (Luis Plasencia). Para qué: evitar planificar actividades de diseño mecánico desde cero que no corresponden al alcance real. Resultado: el Objetivo 1 se redefine como instrumentación (diseño de soportes/adaptadores de montaje de sensores) sobre la plataforma existente, documentado en la revisión bibliográfica. Pendiente confirmación formal del asesor.

9. **Discusión de método de referencia cinemática por marcadores.** Qué: se discutió con Luis Plasencia un método de 4 marcadores (M1-M4) sobre fotos/video de la pierna montada en el simulador, para obtener el ángulo de inclinación del segmento tibial (θ) como referencia independiente para validar la IMU. Resultado: se confirmó que el ángulo es equivalente ya sea que se calcule con referencia anatómica (marcador en el muslo) o con referencia geométrica del propio simulador — lo que sugiere que también puede obtenerse analíticamente desde la posición comandada del mecanismo, sin necesidad de marcadores. Queda pendiente decidir si este método se incorpora al protocolo formal de validación (Objetivo 4).

**3. Actividades Planificadas vs. Actividades Ejecutadas**

| Actividad Planificada | Estado (Ejecutada / En proceso / No ejecutada) | Comentarios (justificación si aplica) |
| :---- | :---- | :---- |
| Revisión del estado del arte | Ejecutada | Completada según cronograma (semanas 1-2) |
| Definición de requerimientos técnicos preliminares | Ejecutada | Actualizada tras la aclaración de alcance (instrumentación, no diseño desde cero); sujeta a validación formal con el asesor |
| Verificación de valores de norma ISO 10328 | En proceso | P4 y P5 verificados con fuente primaria; P3 tiene candidato sin confirmar, P6 sigue pendiente. Se recomienda no seguir invirtiendo tiempo salvo que se necesite cubrir usuarios >100 kg |
| Completar citas bibliográficas incompletas | En proceso | 7 de 11 referencias resueltas esta semana; quedan [2] (parcial), [4], [12], [15] |
| Aclarar alcance real del Objetivo 1 | Ejecutada (informal) | Confirmado con compañero de laboratorio; pendiente confirmación formal del asesor |

**4. Dificultades o Problemas Presentados**

**Norma ISO 10328 es un documento de pago con valores discrepantes entre fuentes secundarias.** Causa probable: la norma es un documento de pago (ISO Store), y distintos papers reportan valores de carga para componentes distintos (socket vs. rodilla vs. pilón) o ediciones distintas de la norma (2006 vs. 2016). Impacto: riesgo de dimensionar la celda de carga con un valor incorrecto. Acción correctiva: acceso institucional gratuito vía sala de lectura virtual de Normas Técnicas Peruanas (INACAL, biblioteca PUCP), priorizando fuentes que citan textualmente la norma vigente (2016) sobre resúmenes de terceros.

**Metadatos web incompletos en fuentes académicas.** Causa probable: la vista previa/metadatos de una página web de un artículo no siempre incluye la lista completa de autores (solo el autor de correspondencia), como ocurrió con la referencia [31]. Impacto: riesgo de citar mal la autoría si no se verifica contra el texto completo. Acción correctiva: para referencias marcadas como inciertas, se descargó y leyó el texto completo del PDF en vez de confiar solo en los metadatos de la página.

**5. Lecciones Aprendidas / Recomendaciones**

Es indispensable verificar los valores numéricos de normas técnicas contra fuentes primarias (o secundarias que citen textualmente la norma con permiso de reproducción) antes de utilizarlos en decisiones de diseño. De forma similar, los metadatos de una página web no son suficientes para verificar autoría de una referencia — el texto completo del PDF puede revelar información distinta (como ocurrió con [31], que tiene 4 autores y no 1). También quedó claro que antes de planificar actividades de diseño mecánico conviene verificar el estado real del equipo físico disponible en el laboratorio: de no haberse revisado las fotos del simulador, se habría planificado erróneamente el diseño de una estructura que ya existe. Para las próximas semanas, se recomienda obtener la confirmación formal del asesor sobre el alcance real del Objetivo 1 antes de avanzar en el diseño de los soportes de sensores.

**6. Actividades Planificadas para la Siguiente Semana**

| Actividad | Objetivo |
| :---- | :---- |
| Confirmar formalmente con el asesor el alcance real del Objetivo 1 (instrumentación de plataforma existente, simulador transtibial) | Evitar retrabajo y alinear expectativas antes de diseñar soportes de sensores |
| Diseñar los soportes/adaptadores de montaje para IMU y celda de carga sobre la plataforma existente | Objetivo específico 1 (redefinido) y 2 |
| Completar las referencias bibliográficas pendientes ([2], [4], [12], [15]) y decidir si se incorpora el método de marcadores M1-M4 al protocolo de validación | Dejar la revisión bibliográfica y el protocolo de validación (Objetivo 4) listos para el informe final |

**7. Anexos o Evidencias**

Documento `Estado-del-arte/Revision bibliografica - Semana 1-2.md` (revisión del estado del arte completa, síntesis, requerimientos técnicos, y notas de aclaración de alcance). Notas de texto completo de 3 fuentes adicionales guardadas en `Estado-del-arte/SENSORES DE FUERZA`, `Estado-del-arte/SOFTWARE` y `Estado-del-arte/ISO`. Fotos del simulador físico y de la conversación con Luis Plasencia sobre el método de marcadores M1-M4, en `Evidencias/simulador/` (referenciadas e incrustadas en la revisión bibliográfica, Sección 8.1-8.2).
