# Revisión Bibliográfica — Plataforma Móvil Instrumentada para Simulador de Marcha

**Proyecto:** Plataforma Móvil Instrumentada para Simulador de Marcha  
**Alumno:** Alessandro Jesus Felix Tello  
**Asesor:** Dante Angel Elias Giordano  
**Formato de citación:** IEEE   
**Estado:** Semana 1–2 — revisión del estado del arte y definición de requerimientos

> Nota general sobre citas: las entradas marcadas con (*) tienen información de autor incompleta o no verificada con certeza en la búsqueda. Deben confirmarse contra la fuente original antes de usarse en el informe final.

---

## 1. Simuladores de marcha con sensórica embebida

| Ref. | Tipo | Sensores | Variables medidas | Ventajas | Limitaciones |
|---|---|---|---|---|---|
| [1] | Tesis doctoral (EngD, Univ. of Bath) | Transductor de presión, encoder, sensor ATI de 6 ejes, sensor de fuerza, medición de GRF | Cinemática (ángulos, movimiento), cinética (momentos, potencia, trabajo), GRF, velocidad de marcha | Pruebas sin exponer pacientes en etapas tempranas, repetibles, controla GRF | Hardware especializado, control complejo (EILC + hidráulica) |
| [2] | Tesis de maestría | Encoders incrementales, interruptor de límite, celda de carga en el shank | Cinemática (ángulos cadera/muslo/rodilla/shank, desplazamiento vertical, velocidad), cinética (GRF aproximada, torque, corriente) | Elimina variabilidad de sujetos, repetible, simula compensación humana (BBO) | 2 DOF en plano sagital; celda de carga no mide GRF directa; prótesis pasiva no reproduce GRF real |
| [3] | Artículo científico | Dinamómetro Kistler 9129AA, dSPACE MicroLabBox, Plataforma Stewart 6 DOF | Cinemática (CoM, orientación tronco), cinética (GRF vertical/horizontal, torque cadera) | Combina ventajas de modelo y robot; primer ensayo HiL exitoso | Rendimiento limitado del actuador en antepié; modelo VPP simplificado |
| [4] | Artículo científico | Encoders UR10E (500 Hz), VICON 10+1 cámaras (100 Hz) | Cinemática (ángulos rodilla/tobillo/cadera, trayectoria muslo). Sin GRF | Mayor rango de movimiento que Stewart; ILC reduce error de seguimiento | Sin control de fuerza (límite 250 N); no replica fase de apoyo; discrepancia 5–10°; n=1 |
| [5] | Artículo científico | 2 IMU 9 ejes, sensor de ángulo rotativo, celda de carga en pilón, RealGait (17 IMU) | Cinemática (ángulos), cinética (GRF como umbral), simetría de marcha | Motor único, sensores de bajo costo, reconocimiento de fase ≥96.4% | Solo simetría de rodilla; no probado en amputados; n=1 sano |
| [6] | Artículo científico | 8 FSR (125 Hz) + acelerómetro LSM6DS3, Arduino Nano 33 IoT | GRF (3 componentes), centro de presión (2 componentes) vía LSTM | Alternativa portátil y de bajo costo a plataformas de fuerza | Componente medio-lateral sigue siendo un reto; solo sujetos sanos |

---

## 2. Concordancia entre IMU y sistemas ópticos de captura de movimiento

| Ref. | IMU | Referencia óptica | Variables | Métricas | Resultados |
|---|---|---|---|---|---|
| [7] | 3× Xsens DOT | Qualisys (10+2 cámaras, 100 Hz) | Ángulos de hombro (escapular/frontal) | RMSE, Pearson r | RMSE 6.7°/7.5°; r>0.9 |
| [8] | 17× HWT901B + Kalman | NOKOV (12 cámaras, 100 Hz) | Zancada, CoM, rodilla, codo | RMSE, correlación, prueba t | RMSE 0.01–0.03 m, 5–7°; r>0.91; p>0.05 (sin diferencia significativa) |
| [9] | MPU6050 + flex sensor | Goniómetro de alta precisión | Step/stride length, cadencia, flexión de rodilla | % exactitud, MAE | Exactitud 94.8%; MAE rodilla 2.1° |

---

## 3. Calibración y validación de IMU de bajo costo

| Ref. | IMU | Qué calibra | Método | Resultados |
|---|---|---|---|---|
| [10] | YIS106 (Yesense) | Alineación sensor-a-segmento | Algoritmo automático en tiempo real (frame estático + dinámico, cuaternión) | RMSE: No Align 19.1° → Manual 4.5° → Automático 2.1° (p<0.05) |
| [11] | 2 IMU sin magnetómetro | Centro articular de cadera | Optimización Levenberg-Marquardt sobre restricción geométrica | Convergencia ≤4 iteraciones; error ≈1.23°; error vs. óptico ≈2° |
| [9] | MPU6050 | Deriva del IMU y flex sensor | Filtro suplementario (no especificado) | Drift 0.7°/min; SD 2.4°→0.9° |

---

## 4. Celdas de carga y sensores fuerza-torque en prótesis y bancos de prueba

| Ref. | Tipo de sensor | Ubicación | Variables | Resultados | Relevancia |
|---|---|---|---|---|---|
| [12]* | Load cell | Interfaz socket–liner | Fuerza normal y cizalla | Cizalla 0.4–7.8 kPa; normal 2.7–61.9 kPa | Media — confort/riesgo cutáneo, no cinética de marcha |
| [13] | Sensor magnético (deflexión) | Adaptador piramidal (pylon) | Fuerza axial, momento sagital | Hasta 2500 N / 120 Nm; no linealidad 8.3%/2.1% | Alta — arquitectura de montaje estándar |
| [14] | Sensor magnético (deflexión) | Estructura de carga de prótesis robótica | Fuerza y momento estructural | Buena linealidad, validado en marcha real | Alta — compara sensado magnético vs. strain gauge |
| [15]* | Proximidad + FSR + inductivo | Inserto de socket CAD/CAM | Colocación, presión gradual, pistoning | 3/3 proximidad correctos; 3/4 FSR correctos | Media-alta — sensórica multimodal de bajo costo |
| [16] | Strain gauge (Wheatstone) | Banco de pruebas genérico | Fuerza axial | Sensibilidad ~15 mV/N; 300 N máx.; error 6%; 20 g | Alta — único proceso completo de diseño/fabricación propio |
| [17] | N/A (patente US20210247249A1) | Integrado en dispositivo protésico | Fuerza y torque | Documenta limitación de strain gauges (costo/volumen) | Media — fundamenta el problema |
| [18] | Capacitivo MEMS | Interfaz socket–muñón | 3 fuerzas + 2 torques | Linealidad >99%; sobrecarga segura >15N | Alta — diseño miniaturizado para prótesis |
| [19] | FlexiForce A201 | Modelo de esqueleto | Cargas en húmero/fémur/tibia | Lineal, exactitud ±5% | Media — sensor de bajo costo, no contexto protésico real |
| [20] | No especificado | Miembros pélvicos animal | Distribución de carga | 62.3% vs. 37.7% | Baja — solo ejemplo conceptual |
| [21] | ATI Nano17 | Banco externo | Fuerzas de agarre/pinza | 15.5 N (agarre), 8.69 N (pinza) | Media — patrón de banco replicable |
| [22] | Múltiple (yema de dedos) | Prótesis de mano | Fuerza de contacto, tensión de tendones | Sin datos cuantitativos de validación | Baja — contexto histórico (2003) |

---

## 5. Protocolos de calibración/validación de instrumentación en sistemas robóticos y mecatrónicos *(bloque nuevo)*

| Ref. | Sistema | Qué calibra/valida | Método | Resultados |
|---|---|---|---|---|
| [23] | Robot 6-DOF (Stäubli TX 200) + tracking óptico, banco de ensayo de cadera | Precisión de posicionamiento robótico vs. movimiento manual de referencia | Comparación de TCP robótico vs. trayectorias manuales registradas ópticamente | SD del TCP: 0.3–0.9 mm por eje; desviación robot-manual: -0.36 a +3.44 mm |
| [24] | Sensores F/T 6 ejes, robot humanoide iCub3 | Modelo de calibración fuerza/torque (afín vs. polinomial no lineal + temperatura) | Optimización con regularización L1 (LASSO) sobre cargas conocidas (1–10 kg) | RMSE: 4.58 N (afín) → 2.09 N (polinomio grado 4); mejora ≈54% |
| [25] | Norma general | Calibración de sistemas de medición de fuerza en máquinas de ensayo estático | Verificación trazable a patrones; evalúa ganancia, offset, no linealidad, ruido | Norma de referencia (ISO 7500-1:2018), sin resultados experimentales propios |

Relevancia: fuentes deliberadamente no biomédicas — dan respaldo metodológico de calibración aplicable directamente a la celda de carga y el IMU de la plataforma, sin depender del contexto de marcha humana.

---

## 6. Normas ISO de ensayo estructural de prótesis *(bloque nuevo)*

Importante: [26] y [27] **no son normas de sensores ni de instrumentación** — son normas de ingeniería mecánica/seguridad que especifican cómo ensayar la resistencia estructural de la prótesis (cargas, ciclos, criterios de falla). Se incluyen aquí porque los niveles y perfiles de carga que definen sirven para dimensionar el rango que debe cubrir la celda de carga del proyecto, no porque califiquen o calibren sensores (eso lo cubre [25], ISO 7500-1, en la Sección 5).

| Norma | Qué certifica | Alcance | Uso en el proyecto |
|---|---|---|---|
| [26] | Resistencia estructural de la prótesis (que no se rompa/deforme bajo uso simulado) | Ensayos estáticos (carga máxima) y cíclicos (hasta 3 millones de ciclos) de prótesis de miembro inferior completas o por componente (pie-tobillo, rodilla) | Indirecto — sus niveles de carga (P3–P8 según peso/actividad del usuario) informan el rango a medir por la celda de carga, no un requisito del sensor en sí |
| [27] | Resistencia estructural cíclica de dispositivos tobillo-pie | Ensayo cíclico que reproduce la fase completa de apoyo (heel strike a toe-off) mediante perfiles estandarizados de GRF vertical/horizontal y ángulo de tibia | Indirecto — el perfil de carga que define es el que la plataforma debería reproducir mecánicamente; da trazabilidad normativa al protocolo de validación (objetivo 4), no calibra instrumentación |

### 6.1. Niveles de carga ISO 10328 (P3–P6)

La norma define 6 niveles de carga (P3–P8) según la masa corporal máxima del usuario simulado; aquí se listan P3–P6 por ser los más relevantes para un banco de pruebas de laboratorio de bajo costo. Condición I = contacto inicial de talón; Condición II = despegue de antepié.

**Nivel de carga por masa corporal:**

| Nivel | Masa corporal máx. |
|---|---|
| P3 | ≤ 60 kg |
| P4 | ≤ 80 kg |
| P5 | ≤ 100 kg |
| P6 | ≤ 125 kg |

**Ensayo cíclico (hasta 3×10⁶ ciclos, carga sinusoidal, retorno mínimo ≈50 N):**

| Nivel | Condición I (talón) | Condición II (antepié) |
|---|---|---|
| P3 | 905 N | 795 N |
| P4 | 1230 N | 1085 N |
| P5 | 1565 N | 1370 N |
| P6 | 2010 N | 1760 N |

**Ensayo estático — Condición I (carga de prueba 30 s / carga última = 2×prueba, límite de deformación plástica <5 mm):**

| Nivel | Fuerza de prueba ($F_{proof}$) | Fuerza última ($F_{ultimate}$) |
|---|---|---|
| P3 | 1540 N | 3080 N |
| P4 | 2065 N | 4130 N |
| P5 | 2240 N | 4480 N |
| P6 | 3375 N | 6750 N |

P4 confirmado por [36] (S. Lapapong *et al.*, reproduce Tabla 1 de ISO 10328:2006). P5 confirmado por [37] (Y. Bader *et al.*, reproduce Tabla 2 de ISO 10328:2016). P3 y P6 son valores de referencia sin confirmar con fuente primaria (ver `Pendientes.md`).

**Recomendación práctica:** dimensionar la celda de carga con margen sobre P5 (4480 N Condición I) — cubre hasta 100 kg de masa corporal simulada — salvo que el proyecto deba representar usuarios >100 kg.

---

## 7. Arquitecturas de software para adquisición sincronizada multi-sensor *(bloque nuevo — objetivo 3)*

| Ref. | Sistema | Qué resuelve | Método | Resultados |
|---|---|---|---|---|
| [28] | WiSSDA: exoesqueleto 3D impreso + encoders rotativos + plantillas de presión | Sincronización espacial/temporal de cinemática articular + fuerza de contacto + centro de presión, en tiempo real | Interfaz de código abierto que combina datos de encoder y FSR con biofeedback visual | Sistema portátil, ambulatorio, validado en marcha guiada |
| [29] | GRAIL (cinta + realidad virtual) + EEG/fNIRS + cinética | Sincronización de múltiples dispositivos multicanal independientes | Ecosistema Lab Streaming Layer (LSL) | Prueba de concepto exitosa de sincronización en tiempo real |
| [30] | Sensores biomédicos inalámbricos multicanal | Alineación temporal entre dispositivos BLE de distintos fabricantes | Método a nivel de capa de aplicación | Diferencia de tiempo absoluta: 69±71 µs (TI), 477±490 µs (Nordic) |
| [31] | Revisión general de arquitecturas embebidas para wearables multi-sensor | Sincronización de streams, RTOS, gestión de energía, protocolos inalámbricos | Revisión sistemática | Marco de referencia con escalabilidad modular |

Relevancia directa: [28] es conceptualmente el más cercano al objetivo 3 (cinemática + fuerza en un sistema portátil de bajo costo), aunque en exoesqueleto wearable, no en plataforma de simulador. [29] aporta el patrón de arquitectura de sincronización de streams heterogéneos.

---

## 8. Diseño mecánico de plataformas móviles y mecanismos de traslación en bancos de prueba *(bloque nuevo — objetivo 1)*

> **Contexto del simulador:** el simulador de marcha (estructura mecánica, traslación horizontal por riel + cadena, traslación vertical por husillo + motor paso a paso, y punto de flexo-extensión en el soporte de la prótesis) ya existe construido en el laboratorio, de un proyecto anterior. El diseño mecánico del Objetivo 1 parte de esta base construida para integrar los sensores (IMU, celda de carga), e incluye tanto adaptadores/soportes externos como, de ser necesario, modificaciones a la estructura existente según lo requiera la integración final.

<table>
<tr>
<td><img src="../Evidencias/simulador/vista-periferica.jpg" width="280"><br><sub>Vista general — riel horizontal, husillo vertical y soporte de prótesis</sub></td>
<td><img src="../Evidencias/simulador/parte-de-atras.jpg" width="280"><br><sub>Vista posterior — motores, husillos y cadena de traslación</sub></td>
<td><img src="../Evidencias/simulador/parte-instrumentada.jpg" width="280"><br><sub>Detalle del soporte donde se monta la prótesis</sub></td>
</tr>
</table>

| Ref. | Mecanismo | DOF | Resultados / relevancia |
|---|---|---|---|
| [32] | Plataforma compacta y modular, traslación vertical y horizontal + flexo-extensión | 3 (plano sagital) | Determinaron que 3 DOF sagitales bastan para ensayar rodillas protésicas — validado con simulación hardware-in-the-loop. **Muy alta relevancia**: el simulador físico ya existente en el laboratorio usa el mismo principio de traslación vertical + horizontal + flexo-extensión que describe este paper, aunque con una disposición de ejes distinta. Sirve como respaldo bibliográfico de que la arquitectura ya construida (3 DOF sagitales) es una elección válida, no como referencia de diseño a implementar |
| [33] | Banco de ensayo con actuación para cargas realistas | No especificado | Documenta limitaciones prácticas (velocidad y longitud de paso limitadas) a anticipar en el diseño propio |
| [34] | Plataforma Gough-Stewart, 6 actuadores lineales Festo EPCO | 6 | Arquitectura de referencia de actuación lineal motorizada (guía + servomotor + husillo) aplicable a una versión simplificada de la plataforma |

**Qué más aporta [32] más allá de la arquitectura (relevante para Objetivo 4 — validación):**

- **Metodología para justificar el número de DOF, no solo el resultado.** No asumieron que 3 DOF bastan: partieron de un modelo "ideal" de 6 DOF y compararon sistemáticamente distintos casos de DOF "congelados" (arrestados) contra ese ideal, hasta encontrar el mínimo conjunto (flexo-extensión + traslación vertical + traslación horizontal, plano sagital) que reproduce el comportamiento relevante. Es un método replicable si en algún momento se quisiera re-justificar o cuestionar los 3 DOF del simulador ya construido, en vez de darlos por sentado.
- **Aplicación real de validación cruzada simulador–sujeto humano.** Usaron el simulador para validar una rodilla protésica policéntrica propia (IITM Polycentric Knee, IPK) — específicamente para confirmar que la rodilla se extiende sin necesidad de un resorte de asistencia a la extensión durante el balanceo (*swing phase*). Luego, con 3 sujetos que usan prótesis pasivas regularmente, compararon marcha real (con su prótesis habitual y con la IPK) contra las predicciones del simulador, encontrando correlación amplia entre ambos.
- **Por qué importa para este proyecto:** es el ejemplo más cercano encontrado de un protocolo de validación de dos niveles — (1) simulador vs. modelo/hipótesis de diseño, (2) simulador vs. sujetos humanos reales — que es exactamente el tipo de protocolo que el Objetivo 4 de este proyecto necesita definir para la plataforma instrumentada, sustituyendo la validación con sujetos humanos por una validación cruzada IMU/celda de carga vs. posición controlada del motor/encoder (ver Sección 10, Validación).

### 8.1. Alcance protésico del simulador existente — confirmado

> **Confirmado 07/08/2026, vía conversación con Luis Plasencia (compañero de laboratorio):** el simulador **es transtibial únicamente**, no multi-protésico. Sí permite ajustar el nivel de amputación simulado (longitud del segmento tibial residual: alto, medio o bajo). No es una confirmación formal del asesor (Dante Elias) — si se necesita para el informe final o para justificar el objetivo 1 ante el curso, conviene pedirle la confirmación explícita a él también.

### 8.2. Método de referencia cinemática por marcadores

Método para obtener el ángulo de inclinación del segmento tibial (θ) como referencia visual independiente, usando 4 marcadores sobre fotos/video de la pierna montada en el simulador:

- **M1** — tobillo/pie (marcado con cinta).
- **M2** — muslo, marcador anatómico sobre la piel (segmento proximal).
- **M3, M4** — cerca de la rodilla, siguiendo la geometría propia del mecanismo del simulador (no son puntos anatómicos).
- **θ** — ángulo entre el segmento tibial (línea M1–rodilla) y una línea de referencia vertical u horizontal.

<table>
<tr>
<td><img src="../Evidencias/simulador/angulo-lineaHorizontal.jpeg" width="320"><br><sub>θ medido respecto a una línea de referencia horizontal</sub></td>
<td><img src="../Evidencias/simulador/angulo-lineaVertical.jpeg" width="220"><br><sub>θ medido respecto a una línea de referencia vertical (mismo valor de ángulo, distinta referencia)</sub></td>
</tr>
</table>

θ da el mismo valor numérico ya sea que se calcule con la referencia anatómica (M2) o con la geométrica del simulador (M3/M4), a lo largo de todo el ciclo de marcha — por lo que también puede obtenerse analíticamente a partir de la posición comandada del propio mecanismo, sin necesidad de marcadores ni cámara. Verificación puntual; no forma parte del protocolo formal de validación del Objetivo 4.

---

## 9. Síntesis: estado del arte vs. objetivos específicos del proyecto

| Objetivo específico | Qué aporta el estado del arte | Brecha remanente | Fuentes clave |
|---|---|---|---|
| **1. Diseño mecánico** (parte de una estructura base ya construida — ver nota Secc. 8; el diseño puede incluir adaptadores externos y/o modificaciones a esa estructura según lo requiera la integración de sensores) | Simuladores con prótesis móvil sobre plataforma fija (Secc. 1); evidencia de que 3 DOF sagitales bastan, coincidente con la arquitectura ya construida en el laboratorio | Ningún sistema revisado documenta específicamente cómo integrar sensores (IMU + celda de carga) a una plataforma de este tipo ya existente sin alterar su cinemática original | Secc. 1, [32], [33], [34] |
| **2. Sistema electrónico (sensores)** | Validación extensa de IMU de bajo costo (RMSE 2–7°, r>0.9); calibración automática (<3° error); arquitecturas de celda de carga; normas de prótesis usadas solo para inferir el rango de carga a medir | Sensor de presión distribuida integrado a una plataforma fija sigue sin precedente directo; ningún estudio combina IMU + celda de carga + presión en un solo sistema | Secc. 2, 3, 4, [26]*, [27]* (*uso indirecto, no son normas de sensores) |
| **3. Software** | Arquitecturas de sincronización multi-sensor (LSL, BLE, master-slave); ejemplo directo de sincronización cinemática+cinética en tiempo real | Ninguna fuente sincroniza específicamente IMU + celda de carga en plataforma fija; todas son wearables o multi-dispositivo clínico | [28]–[31] |
| **4. Validación** | Calibración de IMU (automática, sin magnetómetro); calibración de celdas de carga con trazabilidad (ISO 7500-1); protocolo de calibración robótica biomecánica; normas de perfil de carga de marcha | Nadie ancla la validación de una plataforma de bajo costo a ISO 10328/22675 junto con calibración cruzada IMU-encoder, que es una referencia "gold standard" de bajo costo disponible en este proyecto | Secc. 3, 4, [23]–[25], [26], [27] |

**Brecha central que justifica el proyecto:** ningún sistema de los revisados integra plataforma móvil + IMU + celda de carga/presión + software sincronizado + protocolo de validación anclado a norma ISO, en una arquitectura de bajo costo y completamente documentada.

---

## 10. Requerimientos técnicos derivados (cierre de semana 2)

> **Aclaración de alcance (confirmada con el equipo):** la plataforma sensa fuerza y cinemática de forma **continua** durante el uso de la prótesis en la simulación, para registro/visualización. **No** implementa control en lazo cerrado en tiempo real (p. ej. un controlador PID que corrija al simulador con los datos del sensor) — eso queda como trabajo futuro, fuera del alcance de este proyecto. Esta distinción es importante porque cambia los requerimientos de software y validación: no se exige baja latencia de lazo cerrado, solo sensado sincronizado y confiable.

**Mecánica.** La plataforma con 3 DOF en plano sagital (flexo-extensión, traslación vertical por husillo + motor, traslación horizontal por riel + cadena) **ya existe físicamente**; [32] respalda que esta arquitectura es suficiente para el ensayo de prótesis, y [34] sirve como referencia de actuación lineal comparable pero no es la que se va a construir. El diseño mecánico del proyecto parte de esa estructura ya construida e incluye, como mínimo: (a) diseñar los soportes/adaptadores para montar la IMU y la celda de carga sobre la estructura existente, y (b) verificar que la posición de montaje capture las variables cinemáticas/cinéticas relevantes del ciclo de marcha simulado. Según lo que exija la integración final de los sensores, esto podría extenderse a modificar o rediseñar partes de la estructura existente — está por definirse conforme avance el diseño.

**IMU.** Sensor MEMS de bajo costo (MPU6050 / ICM-20948), muestreo ≥100 Hz (estándar en fuentes validadas de Secc. 2), error objetivo <5° con calibración automática sensor-a-segmento tipo [10].

**Celda de carga / presión.** Rango de fuerza orientativo según ISO 10328 [26] (ver tabla verificada en 6.1): a nivel P5 (≤100 kg) Condición I, proof load = 2240 N y ultimate = 4480 N (fuente primaria [37]); a nivel P4 (≤80 kg), proof load = 2065 N y ultimate = 4130 N, cíclico = 1230 N (fuente primaria [36] + confirmación cruzada, ver 6.1) — la norma certifica la prótesis, no el sensor; se usa aquí solo para saber qué rango de fuerza debe poder medir la celda de carga. P3 y P6 aún no verificados con fuente primaria (ver 6.1); recomendación práctica: dimensionar sobre P5 (4480 N) con margen, salvo que se necesite cubrir usuarios >100 kg. No linealidad objetivo <8% (referencia [13], [16]). Considerar arreglo FSR de bajo costo para presión distribuida si se amplía el alcance (referencia [6], 8 sensores a 125 Hz).

**Software.** Adquisición continua y sincronizada por timestamp compartido — no requiere protocolo inalámbrico complejo tipo LSL/BLE ([28]–[30]) porque los sensores están fijos en la plataforma, no en un sujeto, y no hay lazo de control en tiempo real que cerrar (ver aclaración de alcance arriba). Comunicación I2C/SPI para IMU y ADC dedicado para celda de carga. Registro, visualización y almacenamiento continuo durante toda la simulación. Arquitectura modular para agregar sensores sin rediseño (recomendación de [31]) — este mismo diseño modular es lo que permitiría, a futuro y fuera de alcance actual, incorporar un lazo de control (p. ej. PID) sin rehacer la adquisición de datos.

**Validación.** Protocolo de dos niveles, enfocado en la precisión y confiabilidad del sensado continuo (no en control en tiempo real): (1) calibración estática y dinámica de IMU y celda de carga con trazabilidad a pesos/ángulos conocidos (ISO 7500-1 [25] para fuerza); (2) validación cruzada IMU vs. posición controlada del motor/encoder de la plataforma como referencia de bajo costo, reemplazando la necesidad de un sistema óptico. Perfil de carga de ensayo referenciado a ISO 22675 [27]. Estructura de protocolo inspirada en [32] (ver nota ampliada en Sección 8): ellos validaron primero contra un modelo/hipótesis de diseño (número de DOF) y luego contra sujetos humanos reales; aquí el equivalente sería validar primero el sensado contra referencias controladas de laboratorio (paso 1 y 2 arriba) y, si el alcance se ampliara a futuro, contra datos de marcha humana real como referencia adicional.

**Trabajo futuro (fuera de alcance actual).** Control en lazo cerrado en tiempo real (p. ej. controlador PID) que use el sensado de esta plataforma para retroalimentar y autocorregir al simulador de marcha. Requeriría, cuando se aborde, definir presupuesto de latencia end-to-end (sensor → procesamiento → actuador) y posiblemente rediseñar la capa de comunicación para reducir tiempos de respuesta.

---

## Referencias (formato IEEE)

[1] Z. Yang, "Development of a Gait Simulator for Testing Lower Limb Prostheses," Doctor of Engineering (EngD) thesis, Dept. of Mechanical Engineering, Univ. of Bath, Bath, U.K., Jul. 2020. [Online]. Available: https://researchportal.bath.ac.uk/files/205696121/Thesis_phD_Final_version.pdf — **verificado: autor, título exacto, institución y fecha confirmados vía Bath Research Portal (supervisores: P. Iravani, A. Plummer, M. Pan). Nota: el título real difiere del que se había reportado inicialmente ("...Hydraulic Gait Simulator..."); el título oficial de la tesis es el indicado arriba, y el grado es EngD (doctorado profesional), no PhD.**

[2] R. Davis, "Evolutionary ground reaction force control of a prosthetic leg testing robot," M.S. thesis, Cleveland State Univ., 2013. [Online]. Available: https://etd.ohiolink.edu/acprod/odb_etd/ws/send_file/send?accession=csu1396786747&disposition=inline — **parcialmente verificado: se confirmó por búsqueda cruzada que existe un artículo estrechamente relacionado, del mismo grupo (Cleveland State Univ.), con título casi idéntico: R. Davis, H. Richter, D. Simon, and A. van den Bogert, "Evolutionary ground reaction force optimization of a prosthetic leg testing robot," in *Proc. 2014 American Control Conf. (ACC)*, Portland, OR, USA, 2014 (nótese "optimization" en el artículo vs. "control" en la tesis). No se pudo acceder directamente a la página de OhioLINK para confirmar año/autor exactos de la tesis; se recomienda verificar antes de citar en el informe final.**

[3] C. Insam *et al.*, "Hardware-in-the-loop test of a prosthetic foot," *Appl. Sci.*, vol. 11, no. 20, art. 9492, 2021. doi: 10.3390/app11209492.

[4] Nie *et al.*, "Gait simulator for testing and evaluating lower limb prosthesis," in *Proc. IEEE Conf.* [Online]. Available: https://ieeexplore.ieee.org/abstract/document/11175829 — **aún sin verificar: no se encontró en búsqueda web (documento probablemente muy reciente); requiere acceso directo a IEEE Xplore para confirmar autores, nombre del congreso y año.**

[5] W. Cao, H. Yu, W. Chen, Q. Meng, and C. Chen, "Design and evaluation of a novel microprocessor-controlled prosthetic knee," *IEEE Access*, vol. 7, pp. 178553–178562, 2019. [Online]. Available: https://ieeexplore.ieee.org/document/8924708 — **verificado: autores, revista, volumen y páginas confirmados por búsqueda cruzada.**

[6] V. Civeriati, B. L. Pugliese, C. Carraro, *et al.*, "A sensorized insole to estimate ground reaction forces and center of pressure during gait," in *Proc. IEEE Int. Workshop on Sport, Technology and Research (STAR)*, 2024. [Online]. Available: https://ieeexplore.ieee.org/document/10636002 — **verificado y corregido: el apellido del primer autor es "Civeriati" (no "Cierviati" como se había reportado inicialmente); lista completa de autores aún por confirmar contra la fuente.**

[7] G. Carnevale *et al.*, "A M-IMU-to-segment alignment procedure for shoulder angles estimation," in *Proc. MetroInd4.0&IoT*, 2024.

[8] Zhang *et al.*, "Design and validation of an inertial motion capture system for human dynamic balance assessment," in *Proc. WRRC*, 2024.

[9] Lanso *et al.*, "A wearable knee brace system for real-time gait monitoring and abnormality detection," in *Proc. ICBMESH*, 2025.

[10] Fan *et al.*, "IMU-based real-time biofeedback wristband with automatic sensor-to-segment calibration," *IEEE Sensors J.*, 2025.

[11] Ju *et al.*, "Magnetometer-free IMU-based joint axis calibration and estimation," in *Proc. IEEE ROBIO*, 2021.

[12] "Evaluating shear and normal force with the use of an instrumented transtibial socket: A case study." — **(*) fuente sin autor/año identificados; completar antes de citar formalmente.**

[13] L. Gabert and T. Lenzi, "Instrumented pyramid adapter for amputee gait analysis and powered prosthesis control," *IEEE Sensors J.*, vol. 19, no. 18, pp. 8272–8282, Sep. 2019. [Online]. Available: https://ieeexplore.ieee.org/document/8727476 — **verificado: revista, volumen, número y páginas confirmados por búsqueda cruzada.**

[14] M. R. Haque, G. Berkeley, and X. Shen, "Force-moment sensor for prosthesis structural load measurement," *Sensors*, vol. 23, no. 2, art. 938, 2023. doi: 10.3390/s23020938.

[15] "Instrumented socket inserts for sensing interaction at the limb-socket interface." — **(*) fuente sin autor/año identificados; completar antes de citar formalmente.**

[16] O. Al-Dahiree, M. O. Tokhi, N. Hassan Hadi, N. Rasheid Hmoad, R. Ariffin Raja Ghazilla, H. Yap, and E. Abdullah Albaadani, "Design and shape optimization of strain gauge load cell for axial force measurement for test benches," *Sensors*, vol. 22, no. 19, art. 7508, 2022. doi: 10.3390/s22197508. — **verificado: autores, revista, volumen y DOI confirmados.**

[17] US Patent 20210247249A1, "Force and torque sensor for prosthetic and orthopedic devices."

[18] D. Alveringh *et al.*, "A large range multi-axis capacitive force/torque sensor," 2014.

[19] R. Lara-Padilla *et al.*, "Design and evaluation of a low-cost mechatronic system," 2017.

[20] Hincapié-Riaño *et al.*, "Foot prosthesis for *Ramphastos tucanus*," 2021.

[21] Z. Xu *et al.*, "JTP hand — wrist-powered partial hand prosthesis," 2018.

[22] P. Dario *et al.*, "Interfacing neural and artificial systems," 2003.

[23] M. Rychlik, G. Wendland, M. Jackowski, R. Rennert, K.-D. Schaser, and J. Nowotny, "Calibration procedure and biomechanical validation of an universal six degree-of-freedom robotic system for hip joint testing," *J. Orthop. Surg. Res.*, vol. 18, art. 164, 2023. doi: 10.1186/s13018-023-03601-2.

[24] H. A. O. Mohamed, G. Nava, P. R. Vanteddu, F. Braghin, and D. Pucci, "Nonlinear in-situ calibration of strain-gauge force/torque sensors for humanoid robots," *arXiv:2312.09846*, 2023.

[25] ISO 7500-1:2018, *Metallic materials — Calibration and verification of static uniaxial testing machines — Part 1: Tension/compression testing machines — Calibration and verification of the force-measuring system*, Int. Org. Standardization, Geneva, Switzerland, 2018.

[26] ISO 10328:2016, *Prosthetics — Structural testing of lower-limb prostheses — Requirements and test methods*, Int. Org. Standardization, Geneva, Switzerland, 2016.

[27] ISO 22675:2016, *Prosthetics — Testing of ankle-foot devices and foot units — Requirements and test methods*, Int. Org. Standardization, Geneva, Switzerland, 2016 (rev. 2024).

[28] I. Sanz-Pena, J. Blanco, and J. H. Kim, "Computer interface for real-time gait biofeedback using a wearable integrated sensor system for data acquisition," *IEEE Trans. Human-Mach. Syst.*, vol. 51, no. 5, pp. 484–493, Oct. 2021. doi: 10.1109/THMS.2021.3097067.

[29] S. A. Maas, T. Göcking, R. Stojan, C. Voelcker-Rehage, and D. F. Kutz, "Synchronization of neurophysiological and biomechanical data in a real-time virtual gait analysis system (GRAIL): A proof-of-principle study," *Sensors*, vol. 24, no. 12, art. 3779, 2024. doi: 10.3390/s24123779.

[30] J. Li, E. Quintin, H. Wang, B. E. McDonald, T. R. Farrell, X. Huang, and E. A. Clancy, "Application-layer time synchronization and data alignment method for multichannel biosignal sensors using BLE protocol," *Sensors*, vol. 23, no. 8, art. 3954, 2023. doi: 10.3390/s23083954.

[31] M. Toptsis, N. Karkanis, A. Giannakoulas, and T. Kaifas, "A review of embedded software architectures for multi-sensor wearable devices: Sensor fusion techniques and future research directions," *Electronics*, vol. 15, no. 2, art. 295, 2026. doi: 10.3390/electronics15020295. — **verificado y corregido: al descargar el texto completo del PDF se encontró que la lista de autores tiene 4 nombres (Dept. of Electrical and Computer Engineering, Democritus Univ. of Thrace, Grecia); los metadatos web solo mostraban al autor de correspondencia (T. Kaifas), lo que había llevado a reportarlo erróneamente como autor único.**

[32] S. Sudeesh, M. S. Shunmugam, and S. Sujatha, "A compact and cost-effective gait simulator to advance prosthesis development with reduced reliance on human subject testing: Development, validation and application," *Medical Engineering & Physics*, vol. 134, art. 104254, 2024. doi: 10.1016/j.medengphy.2024.104254 — **corregido: la revista es Medical Engineering & Physics (grupo R2D2, IIT Madras), no Mechanism and Machine Theory como se había reportado inicialmente; verificado contra la página de publicaciones del laboratorio (r2d2.iitm.ac.in) y ScienceDirect (PII S1350453324001553, prefijo ISSN 1350-4533 = Med. Eng. Phys.).**

[33] J. Thiele, S. Gallinger, P. Seufert, and M. Kraft, "The gait simulator for lower limb exoprostheses — overview and first measurements for comparison of microprocessor controlled knee joints," *Facta Univ., Ser. Mech. Eng.*, 2015.

[34] S. M. Güttler, A. M. Poliakov, and V. I. Pakhaliuk, "Universal mechatronic test bench-gait simulator for testing lower limb prostheses," in *Proc. 2022 IEEE 23rd Int. Conf. of Young Professionals in Electron Devices and Materials (EDM)*, 2022. [Online]. Available: https://ieeexplore.ieee.org/document/9855100 — **verificado por búsqueda cruzada (autores y nombre del congreso); recomendable confirmar contra IEEE Xplore antes del informe final.**

[36] S. Lapapong, S. Sucharitpwatskul, N. Pitaksapsin, C. Srisurangkul, S. Lerspalungsanti, R. Naewngerndee, K. Sedchaicharn, W. Chonnaparamutt, and J. Pipitpukdee, "Finite element modeling and validation of a four-bar linkage prosthetic knee under static and cyclic strength tests," *J. Assist. Rehabil. Ther. Technol.*, vol. 2, art. 23211, 2014. doi: 10.3402/jartt.v2.23211. — **fuente primaria confirmada: reproduce Tabla 1 de ISO 10328:2006 para nivel P4.**

[37] Y. Bader, D. Langlois, N. Baddour, and E. D. Lemaire, "Development of an integrated powered hip and microprocessor-controlled knee for a hip–knee–ankle–foot prosthesis," *Bioengineering*, vol. 10, no. 5, art. 614, 2023. doi: 10.3390/bioengineering10050614. — **fuente primaria confirmada: reproduce Tabla 2 de ISO 10328:2016 para nivel P5 Condición I, con permiso de reproducción de SCC/ISO.**

[38] M. K. Owen and J. D. DesJardins, "Transtibial prosthetic socket strength: The use of ISO 10328 in the comparison of standard and 3D-printed sockets," *J. Prosthet. Orthot.*, vol. 32, no. 2, pp. 93–100, 2020. — citada como referencia adicional de ensayo P5 Condición II en sockets (valor histórico ≈4025 N, no directamente comparable por tratarse de otro componente y posible edición anterior de la norma). Nota adicional: el mismo artículo reporta también el valor superior de ultimate static test force para P7 (4840 N según el texto de discusión, aunque 5300 N según el texto de resultados — **discrepancia interna del propio artículo, no resuelta**; no usar como fuente de P7 sin aclarar esta inconsistencia con el autor o la norma original).

[39] D. Bonacini, B. Mangiante, L. Vergani, and C. Colombo, "Design of a new prosthetic foot which complies with ISO 10328 and allows high performance," presented at ETDCM9 — 9th Seminar on Experimental Techniques and Design in Composite Materials, Vicenza, Italy, Sep. 30–Oct. 2, 2009. [Online]. Available: https://www.roadrunnerfoot.com/wp-content/uploads/2021/03/8.ETDCM-2009.pdf — reporta prueba estática = 1610 N, última = 2415 N, cíclico = 1330 N × 2×10⁶ ciclos, torsión = 50 Nm; **posible candidato para nivel P3, pero no confirmado (ver Sección 6.1) — no usar aún para dimensionamiento.**

---

*Los pendientes de esta revisión bibliográfica (referencias por confirmar, verificación de P3/P6, decisiones de alcance) se llevan en el `Pendientes.md` de la semana en curso, dentro de `Reportes-Semanales/S<n>/`.*
