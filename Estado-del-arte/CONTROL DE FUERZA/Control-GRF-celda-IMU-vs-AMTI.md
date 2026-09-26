# Control de fuerza del simulador con celda de carga + IMU, usando el AMTI como referencia

**Fecha:** 24/09/2026 · **Responsable:** Alessandro Jesus Felix Tello
**Pregunta:** ¿se puede usar la celda de carga del pylon y el IMU para controlar el simulador, de modo que la fuerza sobre el AMTI tenga una forma parecida a la GRF de una marcha real?

> **Ojo con el alcance:** el README define el control en lazo cerrado como *trabajo futuro*. Este documento es un análisis de factibilidad; conviene validarlo con Dante antes de meterlo en el cronograma.

---

## 1. Cómo funciona el AMTI (BP400600 / OPT400600-2000 + amplificador Gen 5 / Optima)

**Principio físico.** La plataforma es un transductor de galgas extensométricas. Bajo la placa superior hay elementos elásticos con **puentes de Wheatstone**, y cada uno de los 6 canales (Fx, Fy, Fz, Mx, My, Mz) tiene su propio grupo de galgas. El amplificador excita cada puente (normalmente a 10 V) y recibe una tensión de pocos mV proporcional a esa componente de la carga.

**Cadena de señal (Gen 5 User Manual, Secc. 2.1, 2.5 y specs):**

| Etapa | Qué hace |
|---|---|
| Excitación | Independiente por canal y seleccionable por software |
| Anti-aliasing | Pasa-bajos Butterworth de 2 polos a 1 kHz |
| Muestreo | Hasta 2000 Hz por canal, con sobremuestreo y DSP |
| Corrección | Ganancias y excitaciones calibradas de fábrica, pérdidas por el cable y **crosstalk mediante una matriz de corrección de la plataforma** (6×6 en una plataforma estándar) |
| Salida analógica (DB25) | Un DAC de 16 bit por canal, ±5 V, refresco a 2 kHz y filtro de reconstrucción de 3 polos a 1 kHz |

**Qué tiene de particular Optima.** En vez de usar solo una matriz 6×6, AMTI calibra con hasta 4000 mediciones en hasta 400 puntos de la superficie, y el amplificador aplica esa corrección. Según el brochure, la plataforma queda con un error de COP menor a 0.2 mm, crosstalk de ±0.05 % y exactitud de ±0.1 % (HPS, con más de ~220 N aplicados).

**Qué entrega.** Las 3 fuerzas y los 3 momentos, y de ahí el **centro de presión**: COPx ≈ −My/Fz y COPy ≈ Mx/Fz (más el término del espesor de cobertura). Es decir, mide la GRF **completa**, dónde se aplica y cómo se desplaza del talón a la punta.

**Qué implica para el control.** Con la salida analógica leída por el ADS1256 (ver `S2/Resumen-Semana2.md`), el AMTI puede funcionar como sensor de realimentación en tiempo real, con ancho de banda de sobra (1 kHz frente a los <15 Hz de la GRF de marcha). No hace falta pasar por el software NetForce/BioAnalysis.

---

## 2. Qué ve la celda del pylon frente a lo que ve el AMTI (la física)

Tomamos como cuerpo libre todo lo que queda **debajo** de la celda (adaptador inferior, pie protésico y la parte del pylon bajo la celda), con masa *m*:

```
F_GRF + F_celda + m·g = m·a
```

- Si el simulador es **lento (cuasi-estático)**, `m·a ≈ 0`. Tras tarar el peso propio, **la celda y el AMTI ven la misma fuerza**, con signo opuesto.
- **La diferencia importante es la dirección, no la magnitud.** La celda es de **1 eje** y mide solo la fuerza **a lo largo del pylon**. El AMTI mide en ejes fijos al suelo. Si θ es la inclinación del segmento tibial respecto de la vertical:

```
F_axial = Fz·cos θ + Fx·sin θ          (convención de signos a fijar)
```

  Para despejar Fz hace falta θ, **y ese es el papel del IMU**. Aun así, con un solo eje no se puede separar Fz de Fx. Si Fx es chica frente a Fz, `Fz ≈ F_axial / cos θ` funciona razonablemente bien. En los extremos del apoyo, con θ ~ ±15–20° y la cortante (frenado o propulsión) en su máximo, el error crece. **Hay que medirlo contra el AMTI, no asumirlo.**
- **Qué NO puede dar la pareja celda + IMU:** Fx y Fy por separado, momentos, ni COP. El COP depende del rollover del pie y solo lo mide el AMTI (o una celda de 3–6 ejes tipo Smart Pyramid o iPecs, que ya figuran como camino de upgrade en la revisión).
- **Dinámica.** Si el simulador corre a velocidad real, al término `m·a` hay que sumarle la aceleración del IMU. Con ~1 kg bajo la celda y aceleraciones de algunos m/s², el término es de pocos N, pequeño frente a cientos de N. Donde sí importa es en el choque de talón.

**Conclusión de esta sección:** para la **fuerza vertical (Fz)**, la celda + IMU puede ser un buen sustituto del AMTI una vez calibrada contra él. Para la GRF completa, no.

---

## 3. Antecedentes: ¿alguien ya controla la GRF en un simulador?

Sí. Además, el patrón que más se repite coincide con lo que tiene el laboratorio (actuador controlado en posición, placa de fuerza debajo del pie).

| Ref. | Sistema | Sensor de fuerza | Cómo controla la GRF | Resultado |
|---|---|---|---|---|
| Aubin, Cowley y Ledoux, *IEEE TBME* 55(3), 2008 | Robot paralelo 6-DOF (R-2000) que mueve la tibia | Placa Kistler sobre la plataforma | **Control por aprendizaje iterativo (ILC) proporcional**: entre ciclos corrige solo la **posición vertical** de la trayectoria, según el error de vGRF del ciclo anterior | RMSE de vGRF de 78.7 N a **9.4 N en 6 iteraciones** con ciclo lento (6 s); **35 N** al acelerar a 1.5 s |
| Aubin *et al.*, *IEEE TBME*, 2012 (simulador cadavérico robótico) | Igual, más 9 tendones | Placa Kistler | Jerárquico: PID en tiempo real para los tendones y **lógica difusa iterativa** que ajusta la altura de la placa ciclo a ciclo | **5.6 % BW RMS** (frente a 30 % BW por prueba y error) |
| Yang, tesis EngD, Univ. of Bath, 2020 (ref. [1]) | Simulador hidráulico para prótesis | Sensor F/T ATI de 6 ejes bajo el pie | EILC (ILC) sobre actuadores hidráulicos hasta converger a la GRF objetivo | Ya está en la revisión bibliográfica, Secc. 1.1 |
| Richter, Simon *et al.*, *Appl. Math. Model.* 2015 / reporte técnico CSU | Robot de prueba de prótesis sobre cinta | Celda de carga en el pie | **Sin realimentación de fuerza**: solo sigue posición de cadera y muslo. Los autores advierten que la GRF resultante no es realista | Pico de ~450 N, sin control de forma. Es el caso a evitar |
| Davis, Richter, Simon y van den Bogert, *ACC* 2014 (ref. [2]) | Mismo robot | Celda / cinta | Optimización evolutiva de parámetros para acercar la GRF a la de referencia | Muestra que la GRF se puede "sintonizar" offline |
| Fakoorian, Simon *et al.* (EKF, 2016; *JDSMC* 2017) | Modelo robot/prótesis de 4 DOF | — (estimación) | **Estima** la GRF con filtro de Kalman a partir de las mediciones cinemáticas | Error medio de 2.9 N con 4 mediciones y 20 N con 1 |
| Natsakis *et al.*, *J. Biomech.* 48(2), 2015 ("inertial control") | Simulador cadavérico sagital | Placa de fuerza | **No** impone vGRF: impone la cinemática y deja que la fuerza "salga" | R² = 0.956 frente a in vivo. Es la alternativa a controlar la fuerza |
| Máquinas ISO 22675 (Thelkin, Shore Western, STEP Lab) | Plataforma basculante + actuador | Celda del actuador | **Control de fuerza** para seguir el perfil pulsante de doble pico de la norma | Es el estándar industrial para la forma de la carga |
| Sudeesh *et al.*, *Med. Eng. Phys.* 2024 (ref. [30]) | 3 DOF sagitales con servos y husillo de bolas | Datos de placa como entrada | Solo reproduce trayectorias (servos con entrada analógica) | La misma arquitectura de 3 DOF que el simulador del laboratorio |

**Lección principal:** nadie hace control de fuerza "puro" en tiempo real con un actuador rígido de posición. Lo que funciona es **seguir la posición en tiempo real y corregir la trayectoria ciclo a ciclo con la fuerza medida (ILC)**. Eso encaja con el husillo + paso a paso y con la restricción del README de no exigir baja latencia.

---

## 4. ¿Se puede? Sí, para la fuerza vertical, y por pasos

### 4.1 Idea central

El pie protésico se comporta como un **resorte no lineal**: la fuerza que ve el AMTI depende de cuánto baja el husillo (z) y de en qué parte del rollover está el pie (θ). Entonces:

```
Fz ≈ K(z, θ)        →        z_comando(t) = K⁻¹( Fz_objetivo(t), θ(t) )
```

Con eso, **controlar la forma de la fuerza equivale a elegir bien la trayectoria vertical**. El ILC corrige lo que el modelo K no capturó:

```
z_{k+1}(t) = z_k(t) + L · Q[ e_k(t + δ) ]        con  e_k = Fz_objetivo − Fz_medida,k
```

(L: ganancia de aprendizaje, en mm/N; Q: filtro pasa-bajos que evita amplificar ruido; δ: adelanto que compensa el retardo del sistema)

### 4.2 Qué sensor cumple cada rol

| Rol | Sensor | Por qué |
|---|---|---|
| **Referencia y "maestro"** (validación, entrenamiento) | AMTI por DB25 → ADS1256 | Es la GRF verdadera, con 1 kHz de ancho de banda |
| **Realimentación a bordo** (cuando no está el AMTI, o para el ILC) | Celda del pylon + IMU (θ) | Fz ≈ F_axial / cos θ, **corregido con un modelo ajustado contra el AMTI** |
| **Estado del rollover** | IMU (θ del segmento), encoder o ToF | Indica en qué parte de la curva se está y alimenta K(z, θ) |
| **Seguridad** | Celda del pylon | Límite de fuerza: el husillo **no es retro-conducible**, así que un error de posición contra un pie rígido puede disparar la carga |

### 4.3 Perfil objetivo

La vGRF de marcha normal tiene la forma de "M": un primer pico de ~1.1–1.2 BW (aceptación de carga), un valle de ~0.7–0.8 BW en el apoyo medio y un segundo pico de ~1.1–1.2 BW (despegue), escalado al peso corporal simulado. Hay dos opciones:

- (a) Curva normalizada de la literatura (Winter), escalada.
- (b) El perfil de doble pico de ISO 22675, que da trazabilidad normativa y encaja con el Objetivo 4.

---

## 5. Limitaciones y riesgos concretos

1. **Velocidad del ADC.** El HX711 a 10 u 80 SPS **no sirve para un lazo en tiempo real**. Para ILC ciclo a ciclo, 80 SPS en un ciclo lento (~5 s) da ~400 puntos, que alcanza. Para cualquier cosa más rápida hay que usar el ADS1256, lo que obliga a resolver primero el "diente de sierra".
2. **Paso a paso en lazo abierto.** Bajo carga puede perder pasos. El ILC compensa errores repetibles, pero no los aleatorios. Conviene comparar el ToF o el encoder contra los pasos comandados.
3. **Velocidad del ciclo.** Hay que empezar **lento (cuasi-estático, 5–10× más lento que la marcha real)**, como Aubin (6 s por ciclo). La forma de la fuerza sí se puede reproducir lento, porque la fija la compresión y no la inercia. Al acelerar, el error sube (en Aubin, de 9 N a 35 N).
4. **Solo Fz.** Con 1 eje, la forma de Fx (frenado/propulsión) no se controla ni se mide a bordo. Solo se ve en el AMTI.
5. **Capacidad del simulador.** Falta confirmar la fuerza máxima que puede ejercer el husillo con el motor actual. Si no llega a ~1.2 BW del usuario simulado, hay que escalar el objetivo.
6. **DOF de flexo-extensión.** Si el pivote es **pasivo**, el rollover (y por lo tanto COP y Fx) queda definido por el pie y la traslación horizontal, no por el control. Hay que confirmar si está motorizado.
7. **Quién mueve los motores.** Hay que confirmar si la trayectoria del simulador anterior se puede modificar ciclo a ciclo desde el ESP32 (STEP/DIR ya previstos en `S5/Conexiones-PlacaESP32-S5.md`) o si depende de otro controlador.

---

## 6. Plan de experimentos propuesto (de menor a mayor riesgo)

| Paso | Qué hacer | Salida / métrica |
|---|---|---|
| **E0 – Línea base** | Correr la trayectoria actual **sin control** y registrar a la vez AMTI Fz (y Fx, COP), celda e IMU | Primera curva "cruda". ¿Qué tan lejos está de la "M"? |
| **E1 – Celda + IMU vs. AMTI** | Ajustar `Fz_AMTI ≈ a·F_axial/cos θ + b` (o una regresión con θ y F_axial) | RMSE en N y en % BW; ¿en qué fase del apoyo falla? |
| **E2 – Rigidez del pie** | Bajar el husillo en escalones, cuasi-estático, a varios θ fijos, registrando Fz | Mapa K(z, θ) del pie usado |
| **E3 – Feedforward** | Calcular z(t) = K⁻¹(Fz_objetivo, θ(t)) y correr un ciclo | RMSE de la primera iteración, sin aprendizaje |
| **E4 – ILC con AMTI** | 5–10 iteraciones de la ley de 4.1, realimentando con el AMTI | RMSE vs. iteración; meta de referencia: ≤ ~6 % BW (Aubin 2012) |
| **E5 – ILC con celda + IMU** | Repetir E4 realimentando con la estimación de E1 y validando con el AMTI | ¿Se mantiene el error sin el AMTI? Esto es lo que demuestra la idea |

E0 y E1 **caben dentro del alcance actual** (solo sensado sincronizado) y ya responden la mitad de la pregunta. E2–E5 son el trabajo de control propiamente dicho.

---

## 7. Veredicto

- **Factible para la forma de la fuerza vertical.** Hay precedente directo (Aubin 2008/2012, Yang 2020) con la misma lógica: actuador en posición, placa de fuerza y corrección iterativa. Con el pie como resorte y un ciclo lento, el husillo + paso a paso alcanza, siempre que tenga la fuerza necesaria.
- **La celda + IMU sirve como realimentación de Fz** una vez calibrada contra el AMTI. No reemplaza al AMTI para Fx, momentos ni COP.
- **No hace falta tiempo real duro:** con ILC ciclo a ciclo, incluso el HX711 alcanza para una primera demostración.
- **Siguiente decisión:** hacer E0 + E1 ahora (dentro del alcance) y decidir con Dante si E2–E5 entran al proyecto o quedan como trabajo futuro documentado.

---

## Fuentes

- AMTI, *Gen 5 User Manual* (2010), Secc. 2.1, 2.5 y especificaciones. Copia local: `SENSORES DE FUERZA/GRF-AMTI/AMTI-Gen5-User-Manual.pdf`
- [AMTI — FAQs (Optima, crosstalk, calibración)](https://www.amti.biz/support/faqs/)
- [AMTI — Optima Brochure](https://www.amti.biz/wp-content/uploads/2022/02/AMTI-Optima-Brochure.pdf)
- [Aubin, Cowley, Ledoux — Gait Simulation via a 6-DOF Parallel Robot With Iterative Learning Control, IEEE TBME 2008](https://www.academia.edu/333436/Gait_Simulation_via_a_6_DOF_Parallel_Robot_With_Iterative_Learning_Control)
- [Aubin et al. — A Robotic Cadaveric Gait Simulator With Fuzzy Logic Vertical GRF Control, IEEE TBME 2012](https://ieeexplore.ieee.org/document/6029994/) ([PDF](http://courses.washington.edu/bioen520/notes/Aubin_(IEEE_2012).pdf))
- [Richter et al. — Development of a Leg Prosthesis Test Robot (reporte técnico CSU)](https://academic.csuohio.edu/richter-hanz/wp-content/uploads/sites/61/2022/06/techreport01.pdf) · [Appl. Math. Model. 2015](https://sciencedirect.com/science/article/pii/S0307904X14003096)
- [Fakoorian, Simon et al. — GRF Estimation in Prosthetic Legs with an EKF](https://engagedscholarship.csuohio.edu/enece_facpub/382/) · [versión JDSMC 2017](https://asmedigitalcollection.asme.org/dynamicsystems/article/139/11/111004/474403/Ground-Reaction-Force-Estimation-in-Prosthetic)
- [Natsakis et al. — Inertial control as novel technique for in vitro gait simulations, J. Biomech. 2015](https://www.sciencedirect.com/science/article/abs/pii/S0021929014006332)
- [STEP Lab — ISO 22675](https://step-lab.com/iso/iso-22675/) · [Thelkin — ISO 22675 Foot Test System](https://www.thelkin.com/media/attachments/2021/06/28/thelkin---iso-22675-foot-test-system-en.pdf)
- Refs. [1], [2] y [30] de `Revision bibliografica - Semana 1-2.md` (Yang 2020; Davis et al. 2014; Sudeesh et al. 2024)
