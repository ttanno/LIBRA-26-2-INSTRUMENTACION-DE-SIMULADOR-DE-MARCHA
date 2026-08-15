# Pendientes — Semana 1 (actualizado 11/08/2026, integración de referencias en la revisión bibliográfica)

Nota de trabajo informal (no es parte de los reportes formales), para triar qué buscar, editar, sintetizar o borrar. Referencias entre `[ ]` apuntan a `Estado-del-arte/Revision bibliografica - Semana 1-2.md` salvo que se indique otro archivo. Este archivo se actualiza cada semana; al cerrar la semana, copiar los pendientes que sigan abiertos al `Pendientes.md` de la semana siguiente.

## Buscar

- [ ] [2] Confirmar autor/año exacto de la tesis de maestría (R. Davis, Cleveland State Univ.) contra OhioLINK — accession `csu1396786747`.
- [ ] [4] Nie et al. — documento IEEE muy reciente, no indexado en las búsquedas realizadas; requiere acceso directo a IEEE Xplore.
- [ ] [12] "Evaluating shear and normal force with the use of an instrumented transtibial socket" — sin autor identificado.
- [ ] [15] "Instrumented socket inserts for sensing interaction at the limb-socket interface" — sin autor identificado.
- [ ] [9] Confirmar método de filtrado de deriva usado (Kalman vs. complementario) — no especificado en la fuente.
- [ ] Confirmación formal del asesor (Dante Elias) sobre el simulador existente: ya hay una estructura base construida y es transtibial únicamente. Hoy solo está confirmado informalmente por un compañero de laboratorio.
- [x] Método de marcadores M1–M4 — resuelto (07/08/2026): es solo verificación puntual, no requerimiento de la plataforma ni parte del protocolo formal de validación.
- [ ] P3 y P6 de ISO 10328 sin verificación confiable (P3 tiene candidato no confirmado en [39]; P6 solo un dato suelto) — no priorizar salvo que el proyecto deba cubrir usuarios >100 kg.

## Diseño de sensórica (hallazgos de literatura, 10/08/2026)

- [ ] Confirmar arquitectura de sensado: celda de carga (validación normativa ISO 10328) + IMU (cinemática) — casi ningún proyecto revisado integra ambos en una sola plataforma; sigue siendo el diferenciador del proyecto frente al estado del arte.
- [ ] Celda de carga candidata: **TAL107F-10kg** (34×34×1.5mm, 10 kg, 1.0mV/V±0.2) — usada en un simulador de rollover muy similar al nuestro (Matray et al., 2025, J. Biomechanics).
- [ ] Arquitectura electrónica de referencia: ESP32-WROOM + ADS1256 (ADC 24-bit, 8 canales) + BNO055 (IMU 9 ejes) + celdas de carga, todo en una sola placa — BOM real de ~$39 documentado (Bulbul et al., 2024, ETASR). Sirve de punto de partida para nuestra propia lista de materiales.
- [ ] Punto de medición de fuerza: se descartó instrumentar la prótesis (pylon wearable, tipo iPecs) por costo/complejidad y por añadir masa a la prótesis bajo prueba. Alternativa decidida: instrumentar la sujeción fija del simulador (donde se monta el pylon), no la prótesis ni el suelo.
- [x] Aclaración importante (10/08/2026): nuestras prótesis de prueba NO tienen socket — el pylon se articula directamente a la plataforma. Por lo tanto, los métodos derivados de socket (presión de interfaz de Matray, traducción a "momento articular" tipo iPecs que asume centro articular biológico) no aplican. Sí aplica el dato crudo de fuerza/momento en el pylon (sin traducción a socket), que es exactamente lo que necesitamos para validación normativa ISO 10328.
- [x] Validez del simulador vs. cuerpo real (10/08/2026): la validez del sensor (¿mide bien la fuerza aplicada?) no se reduce por usar un rig mecánico en vez de una persona — de hecho ISO 10328 en sí es un ensayo puramente mecánico (mandril alineado, sin sujeto humano). Lo que sí se reduce es la validez biomecánica/ecológica (no captura activación muscular, balance, tejido blando) — limitación ya reconocida en la literatura (Matray lo llama "preliminar"), mencionar en la discusión del informe pero no bloquea el uso del simulador para validación normativa.
- [ ] Validación estructural de soportes/placas: usar Fusion 360 (Static Stress Simulation) en vez de ANSYS — suficiente salvo que se necesite simular fatiga cíclica (relevante para ensayos ISO 10328 cíclicos, evaluar más adelante).
- [x] Protocolo de referencia para pruebas de alineamiento — **resuelto (11/08/2026)**, ver nota abajo: no es 11 sujetos ni 3°/6°/5mm/10mm; son 10 sujetos, 2°/4°/6° angular y 5/10/15mm traslacional (Kobayashi et al. 2014, *Clin. Biomech.* = [41]).
- [x] Papers de referencia guardados para citar — incorporados (11/08/2026) en `Revision bibliografica - Semana 1-2.md` como [40]–[43], Secc. 4 y 4.1: Matray et al. 2025 (roll-over simulator + celdas de carga en socket), Kobayashi et al. 2012 (Smart Pyramid, momentos de reacción del socket), Bulbul et al. 2024 (sensor de tobillo 3-DOF, ESP32+ADS1256+BNO055, BOM ≈US$39). Corrección: "Fiedler et al. 2014" no existe con ese autor — el artículo real es S. R. Koehler, Y. Y. Dhaher, y A. H. Hansen, "Cross-validation of a portable, six-degree-of-freedom load cell..." *J. Biomech.*, 2014 (verificado vía Crossref).
- [x] [41] **Resuelto (11/08/2026), texto completo leído directamente (PDF proporcionado por el usuario):** el protocolo detallado NO está en Kobayashi et al. 2012 (*J. Biomech.*, vol. 45) ni en el companion paper de *Gait & Posture* 2013 — está en un tercer artículo del mismo grupo: T. Kobayashi, A. K. Arabian, M. S. Orendurff, T. G. Rosenbaum-Chou, D. A. Boone, "Effect of alignment changes on socket reaction moments while walking in transtibial prostheses with energy storage and return feet," *Clin. Biomech.*, vol. 29, no. 1, pp. 47–56, 2014, doi: 10.1016/j.clinbiomech.2013.11.005 — agregado a la revisión bibliográfica como **[41]**. Dato de notas de trabajo era impreciso en dos cosas: son **10 sujetos** (no 11), y el protocolo real usa **2°/4°/6°** angular (no solo 3°/6°) y **5/10/15 mm** traslacional (no solo 5/10 mm), sobre pies ESR específicamente. Smart Pyramid: 3.22 cm alto, 0.14 kg, muestreo 100 Hz, Bluetooth, calibración R²=0.998/0.996, RMSE 2.08%/2.80%.
- [ ] [40] Confirmar contra texto completo de Matray et al. 2025 si la celda de carga usada es efectivamente la TAL107F-10kg (dato de nota de trabajo, no verificado en la fuente primaria).

## Ubicación y selección de sensores (decisión, 10/08/2026)

- [ ] Ubicación primaria de fuerza: interfaz pylon–sujeción de la plataforma (punto único, arriba). Reemplaza directamente lo que en la literatura es el socket — no necesitamos traducción a "momento articular", solo fuerza/momento crudo en ese punto, que es lo que exige la validación ISO 10328.
- [ ] Ubicación secundaria (opcional, fase 2): placa de contacto pie-plataforma (abajo), si se quiere caracterizar rollover/COP como en Matray o Bulbul. No prioritaria frente a la de arriba.
- [ ] Celda de carga: empezar con 1 eje (axial, tipo TAL107F o similar) por costo/simplicidad; dejar como upgrade path pasar a 3 o 6 ejes (tipo Smart Pyramid/iPecs) si se necesita momento, no solo fuerza axial.
- [ ] Rango de la celda: dimensionar con margen (~1.5–2x) sobre la carga máxima esperada del nivel P de ISO 10328 ya verificado (P4/P5), para no dañar el sensor en ensayos cíclicos.
- [ ] Frecuencia de muestreo: 50–100 Hz es suficiente para ensayos cuasi-estáticos/cíclicos accionados por motor (referencia: Matray muestreó celdas a 50Hz); no se necesita 1000Hz como una plataforma de fuerza de impacto real.
- [ ] IMU: preferir un IMU de 9 ejes con fusión de sensores integrada (tipo BNO055) para no tener que resolver el filtrado de deriva por software — responde directamente el pendiente abierto sobre Kalman vs. complementario.
- [ ] ADC: usar un ADC dedicado de resolución alta (24-bit, tipo ADS1256 o HX711) para leer la celda de carga — la señal de mV que da la celda necesita amplificación/resolución adecuada, no un ADC genérico de microcontrolador.
- [ ] Montaje: diseñar bracket/interfaz impresa en 3D (tipo espaciadores ABS de Bulbul) para adaptar la celda de carga al punto de anclaje existente del marco rojo de la plataforma (pernos ya visibles en las fotos del simulador).

## Ubicación del IMU y precisión del encoder (pendiente, 12/08/2026)

- [ ] **Preguntar al asesor mañana:** ¿el motor paso a paso de la plataforma tiene retroalimentación real (encoder óptico/magnético en el eje) o es solo conteo de pasos en lazo abierto? Si es lazo abierto, la "posición comandada" no garantiza la posición real (backlash de husillo, holgura de cadena, pasos perdidos bajo carga) — esto cambia si vale la pena poner el IMU cerca de la plataforma/celda de carga como chequeo independiente, en vez de solo abajo cerca del pie.
- [ ] Aclaración técnica: el IMU no es buen sensor para validar **posición lineal** (traslación horizontal/vertical) — la posición se obtiene integrando dos veces la aceleración y acumula deriva en segundos. Para eso conviene comparar contra el método de marcadores M1–M4 (Secc. 8.2) o un sensor de posición dedicado (encoder lineal, potenciómetro de hilo, láser de distancia), no contra el IMU.
- [ ] El IMU sí sirve para validar **ángulo** (fusión acelerómetro+giroscopio, corregida por gravedad, razonablemente estable en el tiempo) — ahí la comparación IMU vs. encoder/marcadores sí tiene sentido.
- [ ] Implicación: probablemente se necesiten dos validaciones separadas, no una sola "IMU vs. encoder" — (1) ángulo: IMU (o par de IMUs, uno arriba/uno abajo, como [5]) vs. encoder/marcadores; (2) posición lineal: marcadores o sensor de posición dedicado vs. encoder. Decidir ubicación final del IMU después de confirmar con el asesor si el encoder es lazo abierto o cerrado.

### Respuesta de Dante (12/08/2026) — arquitectura de sensores por DOF

Alessandro habló con el asesor. Indicaciones recibidas, una por cada grado de libertad del simulador (en vez de un solo sensor de posición genérico):

- [x] **GRF — aclarado (12/08/2026):** Dante quiere GRF como prioridad. Plataforma de fuerza (contacto pie-suelo) = ubicación **primaria**. La celda de carga en la interfaz pylon-plataforma (Secc. 4.1) pasa a ser **secundaria**, pero se mantiene — sigue siendo útil (dimensionamiento ISO 10328, dato complementario), no se descarta. Esto invierte la prioridad que tenía anotada el 10/08 ("ubicación secundaria, opcional, fase 2" para el punto de abajo) — ahora es al revés.
- [ ] Requisito clave que puso Dante: la plataforma de fuerza debe **integrarse mecánicamente con el simulador** (alineada/centrada bajo el punto donde pisa el pie) y su adquisición debe ser **sincrónica** con el resto de sensores (celda de carga, IMU, sensores de posición/rotación).
- [ ] Ojo: una plataforma de fuerza comercial normalmente trae su propio sistema de adquisición separado (no se conecta directo al ESP32 como una celda de carga simple). La justificación de la Secc. 10 ("Software") de que no hace falta LSL/BLE porque todo está cableado a un solo microcontrolador ya no aplica tal cual si entra una plataforma de fuerza con DAQ propio — revisar si conviene retomar una arquitectura de sincronización tipo LSL ([27], GRAIL) para este caso. Pendiente definir qué plataforma de fuerza se va a usar (¿ya hay una en el laboratorio? ¿cuál DAQ/software trae?) antes de decidir el método de sincronización.
- [ ] Actualizar Secc. 4.1, Secc. 9 y Secc. 10 de la revisión bibliográfica con este cambio de prioridad (GRF primario / pylon secundario) una vez que esté confirmado del todo con Dante.
- [ ] **Traslación (horizontal y vertical):** usar láseres (sensor de distancia tipo ToF) u otra arquitectura equivalente para medir ambos ejes de traslación de la plataforma — confirma lo que ya se había identificado el 11/08: el IMU no sirve para posición lineal, hace falta un sensor dedicado. Láser queda como la opción recomendada por el asesor (antes se habían barajado también encoder lineal o potenciómetro de hilo).
- [ ] **Rotación (flexo-extensión):** encoder rotativo, potenciómetro, u otra arquitectura conocida, montado en el propio eje de rotación — sensor dedicado de ángulo mecánico, independiente del IMU.
- [x] **Resuelto (13/08/2026) — rol del IMU tras la arquitectura por DOF de Dante:** el IMU se mantiene en el diseño, junto al encoder/potenciómetro de rotación — no es redundante, cada uno cumple un rol distinto. El encoder es la medición primaria del ángulo de flexo-extensión (precisión directa sobre el eje mecánico, sin deriva). El IMU no reemplaza eso; sirve como validación cruzada independiente: mide la orientación del segmento en el espacio (respecto a la gravedad), por lo que puede detectar backlash, holgura o desalineamiento del pivote que el encoder solo no vería (el encoder solo reporta el ángulo del eje, no si el eje realmente está rígido). Esto es justo el objetivo 4 del README ("validación cruzada IMU vs. encoder de la plataforma"), así que la arquitectura de Dante no desplaza al IMU, lo confirma como sensor de validación del sistema.
- [ ] Actualizar Secc. 10 (Requerimientos técnicos) de la revisión bibliográfica con esta arquitectura de sensores por DOF (incluyendo el rol confirmado del IMU) una vez que se resuelva la duda de la plataforma de fuerza.

### Integración AMTI BP400600 — pinout y fórmula de conversión (13-14/08/2026)

- [x] **Resuelto — plataforma confirmada en el laboratorio:** AMTI BP400600 (OPT400600-2000), amplificador Optima OPT-SC S/N 4305. Confirmado físicamente (foto del panel trasero del amplificador): tiene salida analógica independiente (DB25S) además del USB — habilita lectura en tiempo real con ADC propio, sin depender de NetForce/BioAnalysis.
- [x] **Resuelto — pinout del conector DB25S (Analog Output), fuente oficial: AMTI Gen 5 User Manual, Secc. 8.5** (PDF guardado en `Estado-del-arte/SENSORES DE FUERZA/AMTI-Gen5-User-Manual.pdf`, subido por el usuario 14/08/2026, confirma lo ya extraído de un espejo público del manual — MIT wiki):

| Pin | Descripción | Pin | Descripción |
|---|---|---|---|
| 1 | Fx: analog out | 14 | Voltage Ref, 1mA max |
| 2 | Fy: analog out | 15–20 | Ground Ref |
| 3 | Fz: analog out | 21–22 | NC |
| 4 | Mx: analog out | 23 | Auto zero input opcional** |
| 5 | My: analog out | 24 | Power plus input opcional |
| 6 | Mz: analog out | 25 | Power minus input opcional* |
| 7–10 | NC | 11 | Power minus input opcional* |
| | | 12 | Power plus input opcional |
| | | 13 | Power minus input opcional* |

\* Con jumper de zero channel (R281) instalado. \*\* Con switch momentáneo a ground ref.

- [ ] Pendiente: confirmar el modo de salida configurado actualmente en el amplificador del laboratorio (MSA-6 Compatible vs. Fully Conditioned, Secc. 11 del mismo manual) sin alterar la configuración compartida — y ubicar la matriz de calibración/certificado real de esta unidad (S/N 9544M), no la de ejemplo del manual.
- [ ] Pendiente: respuesta de soporte de AMTI (formulario enviado 13/08/2026) sobre pinout/documentación técnica específica del OPT-SC.

## Inventario de IMUs disponibles en laboratorio (11/08/2026)

Lista tal cual se tiene por el momento, sin filtrar duplicados ni verificar specs — pendiente elegir uno contra el requerimiento de la Secc. "Ubicación y selección de sensores":

- HMC5883L (magnetómetro 3 ejes, standalone — no es IMU completo, se combina con un acelerómetro/giroscopio)
- ArduIMU v3
- MPU-92/65
- MPU6050-PCB
- MPU 6050
- GY-521
- MPU6050
- MPU9250
- MPU6050 GY-521
- V1350 YP-05

- [ ] Ninguno de estos es un BNO055 (la preferencia registrada arriba, "IMU: preferir tipo BNO055 por fusión de sensores integrada") — decidir si se compra un BNO055 o si se elige entre lo disponible (más probable: MPU9250 o MPU6050 + HMC5883L, ambos requieren resolver el filtrado de deriva por software, ya que no traen fusión integrada).
- [ ] Confirmar qué es exactamente "V1350 YP-05" — nombre no identificado con certeza, verificar antes de descartarlo o considerarlo.
- [ ] Duplicados aparentes en la lista (MPU6050 / MPU 6050 / MPU6050-PCB / GY-521 / MPU6050 GY-521 parecen ser el mismo chip en distintas presentaciones/breakouts) — confirmar si son unidades físicas distintas o el mismo ítem contado varias veces.

## Editar

- [x] Revisar si el % de avance de OE1 en el Reporte de Avance (quedó en 5%) debe ajustarse tras la aclaración de alcance — es criterio tuyo, no lo toqué.
- [ ] Decidir el alcance de sensores de presión distribuida (FSR array) vs. solo celda de carga puntual, y ajustar la Sección 6 de la revisión bibliográfica en consecuencia.

## Sintetizar

- [x] La lista de 9 "Actividades Realizadas" del Informe Semanal es bastante extensa — si el curso pide algo más compacto, se puede condensar en 4–5 puntos agrupando por tema (revisión bibliográfica, verificación normativa, corrección de citas, aclaración de alcance).
- [x] Las Secciones 8.1/8.2 de la revisión bibliográfica (alcance transtibial, método de marcadores M1–M4) están bastante detalladas para ser notas preliminares — conviene resumirlas una vez que el asesor confirme el alcance y se decida si se usa el método de marcadores.

## Borrar

- [x] Referencia [35] ("valores numéricos iniciales de P3–P6, sin verificar") — eliminada de la revisión bibliográfica (07/08/2026).
- [x] Referencia [20] (Hincapié-Riaño et al., prótesis de pata para tucán) — eliminada de la revisión bibliográfica (11/08/2026): sin sensor, calibración ni metodología transferible al proyecto, solo ejemplo conceptual de "% de distribución de carga".
- [x] Referencia [22] (Dario et al., proyecto CyberHand, 2003) — eliminada de la revisión bibliográfica (11/08/2026): prótesis de mano, sin datos cuantitativos de validación, solo contexto histórico.
- [ ] Nada más identificado como candidato claro a borrar por ahora.

## Actualización estado del arte (11/08/2026, segunda pasada)

- [x] Agregada Secc. 1.1 a la revisión bibliográfica: qué variable de fuerza mide cada simulador [1]-[6] y el mecanismo real de medición (ATI 6 ejes + EILC en [1]; Kistler FTS + co-simulación VPP hardware-in-the-loop en [3]).
- [x] Agregada Secc. 4.2: taxonomía de 8 principios físicos de sensado de fuerza (strain gauge, magnético, capacitivo, FSR, piezoeléctrico, proximidad/inductivo, F/T comercial, proxy de corriente de motor) mapeados a las referencias que los usan.
- [x] Reforzada la nota sobre [13]/[38] en Secc. 4.1: el "pyramid adapter" es literalmente el punto de unión socket-pylon estándar en prostética; al no haber socket en este proyecto, ese punto coincide exactamente con la interfaz pylon-plataforma ya decidida (no es solo una referencia parecida).
- [x] Secc. 9 (síntesis) y README.md actualizados con las nuevas subsecciones.

## Actualización estado del arte (11/08/2026, tercera pasada — PDFs subidos)

- [x] Usuario subió dos PDFs de texto completo: (1) Kobayashi et al. 2014, *Clin. Biomech.*, doi 10.1016/j.clinbiomech.2013.11.005 (protocolo de alineamiento con pies ESR); (2) Insam et al. 2021, *Appl. Sci.* (= [3], ya citada). Ambos leídos completos.
- [x] Primer intento: agregar el PDF de Kobayashi 2014 como referencia nueva **[41]**, separada de [38] (J. Biomech. 2012, doi 10.1016/j.jbiomech.2012.08.014) — son técnicamente dos DOIs, revistas, años y listas de autores distintos (Arabian/Rosenbaum-Chou vs. Zhang).
- [x] **Decisión del usuario (11/08/2026): fusionar todo en [38], sin crear [41].** El usuario confirmó que solo quiere dos referencias en esta zona: [13] (Gabert & Lenzi, sensor magnético) y [38] (Kobayashi, Smart Pyramid). Revertido: se eliminó la entrada [41]; el detalle del protocolo exacto (10 sujetos, 25 condiciones, 2°/4°/6° angular, 5/10/15mm traslacional, specs físicas del Smart Pyramid) quedó incorporado directamente en la nota y fila de tabla de **[38]**, con una aclaración de que ese detalle proviene del texto completo del PDF proporcionado (aunque su DOI no coincide exactamente con el de [38] — queda registrado aquí por transparencia, no se objeta más la decisión).
- [x] Numeración de referencias sigue en 1–40 (sin [41]).
- [x] Nota de [3] (Insam) enriquecida con detalle confirmado por texto completo: FTS = Kistler 9129AA piezoeléctrico, modelo VPP modificado de Maus et al. (basado en SLIP), dSPACE MicroLabBox dS1202, ΔT=0.0002s/0.001s, limitación reconocida por los autores (parámetros del modelo no biomecánicamente realistas: 30kg, 1m de pierna). Esto no fue objetado por el usuario, se mantiene.
- [x] README.md: se mantiene en 40 referencias.

## Editar (numeración)

- [x] Renumeradas todas las referencias de forma secuencial 1–40, sin huecos, tras borrar [20], [22] y [35] (11/08/2026). Todas las citas cruzadas en tablas y texto (Secc. 4, 4.1, 6, 9, 10) se actualizaron en el mismo pase. Mapa completo de renumeración no se conserva por separado — si se necesita rastrear una referencia antigua, usar el historial de git del archivo.
