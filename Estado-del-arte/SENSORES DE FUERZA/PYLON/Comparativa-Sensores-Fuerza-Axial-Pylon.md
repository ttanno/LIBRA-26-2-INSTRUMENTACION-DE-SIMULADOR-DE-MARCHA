# Comparativa — Sensores de fuerza axial para interfaz pylon–plataforma (LIBRA)

**Fecha:** 19/08/2026
**Contexto:** complementa `Estado-del-arte/SENSORES DE FUERZA/` y la Secc. 4.1 de la revisión bibliográfica. Busca reemplazar/validar la celda de carga candidata actual (TAL107F-10kg) con opciones dimensionadas correctamente para el rango que exige ISO 10328.

---

## 1. Punto de partida (tomado de los documentos ya existentes en el repo)

- **Ubicación:** interfaz pylon–plataforma (arriba, en el punto de anclaje del pylon al soporte fijo), no en el socket ni en el suelo. Prioridad **secundaria** desde la reunión de Semana 2 (la GRF con la plataforma AMTI BP400600 pasó a ser prioritaria), pero se mantiene porque dimensiona la validación contra ISO 10328.
- **Rango requerido:** dimensionar con margen sobre nivel **P5** — fuerza de prueba (proof) **2240 N**, fuerza última **4480 N**, cubre hasta 100 kg de masa corporal simulada.
- **Eje:** 1 eje (fuerza axial) es suficiente para el objetivo actual; se dejó abierto un *upgrade path* a 3–6 ejes solo si más adelante se necesita medir momento.
- **No linealidad objetivo:** <8%.
- **Interfaz mecánica real:** por las fotos (`parte-instrumentada.jpg`) y el CAD (`imagen.png`), el pylon termina en una **placa plana atornillada** al soporte del pivote de flexo-extensión — no hay un pyramid adapter roscado estándar de prótesis. Esto favorece sensores tipo *pancake*/*donut* o un bloque strain-gauge a medida, montados por pernos entre dos placas, sobre sensores exclusivamente roscados en línea.
- **Electrónica ya decidida:** ADS1256 (ADC dedicado de 24 bits, 8 canales) como lectura de la celda de carga, en paralelo con IMU y encoder. Esto favorece sensores de **salida cruda mV/V** (puente de Wheatstone) en vez de módulos con amplificador/salida digital integrada tipo HX711, para no duplicar acondicionamiento.
- **Punto ciego detectado:** la candidata actual del estado del arte, **TAL107F-10kg** (34×34×1.5 mm, ~10 kg ≈ 98 N), está sobredimensionada en sentido inverso — su capacidad es ~23× menor que la fuerza de prueba P5 (2240 N) y ~46× menor que la última (4480 N). No sirve para el ensayo normativo tal como está definido; como mucho serviría para un sub-ensayo de banco a escala reducida.

---

## 2. Opciones investigadas, por nivel de costo

### Nivel A — Bajo costo / DIY (concordante con el enfoque ya usado en el proyecto)

| Opción | Capacidad | Dimensiones aprox. | Salida | Costo estimado | Notas |
|---|---|---|---|---|---|
| **Celda propia tipo [16] (Al-Dahiree), escalada** | Diseñada a medida (recalcular *t* y *D* de las ecuaciones del paper para ~2500–5000 N en vez de 300 N) | Bloque de aluminio 6061, ~40–60×40–60×15–20 mm (mayor que el prototipo original de 30×30×10 mm) | mV/V crudo (puente medio, INA818 opcional) | ~US$30–60 en materiales + galgas + mecanizado CNC | Mismo método ya documentado en el repo (FEM en Fusion 360 + galgas CEA + puente Wheatstone). Permite diseñar la geometría exacta del bloque para atornillarse directo al patrón de pernos que ya existe en la placa del pylon (visible en `parte-instrumentada.jpg`). Requiere calibración propia con pesas conocidas, como en [16]. |
| **S-type / donut genérico (ATO, Amazon, AliExpress)** | 200–1000 kg (cubre 2240–4480 N con margen) | Variable según modelo | mV/V (~1–2 mV/V) | US$20–150 | Precisión y repetibilidad no garantizadas por el fabricante (hoja de datos genérica); requiere calibración propia igual que la opción anterior. Es la opción más barata pero con más incertidumbre en no linealidad real. |

### Nivel B — Semi-profesional

| Opción | Capacidad | Dimensiones | Salida | Costo estimado | Notas |
|---|---|---|---|---|---|
| **Transducer Techniques THA/THB (thru-hole/donut)** | THA: 50–500 lb (222–2224 N) / THB: 100–2000 lb (445–8896 N) | THA: Ø1.00" / THB: Ø1.50", acero inoxidable 17-4 PH | mV/V | US$590–630 (nuevo, precio de catálogo) | Diseño *donut*: el perno/varilla del pylon pasa por el centro y la fuerza se transmite por compresión entre dos placas — encaja bien con una interfaz de placa atornillada como la del simulador. |
| **TE Connectivity / Measurement Specialties XFTC301 (roscado compacto)** | 500 N / 1000 N / 2000 N / 5000 N / 10000 N | Compacto, dos espárragos roscados (M) | ±10–15 mV/V según modelo | Sin precio público (verificar disponibilidad — la página indica "no disponible actualmente", contactar distribuidor) | El modelo de 5000 N da margen justo sobre la fuerza última P5 (4480 N); el de 2000 N cubre la fuerza de prueba (2240 N) casi al límite — mejor elegir el de 5000 N para no operar al borde del rango. |
| **TE Connectivity FX1901-0001-0200-L (compression, referencia guardada 26/08)** | 200 lbf (~890 N) | OEM compression load cell, cuerpo compacto | 100 mV @ 5 VDC excitación (~20 mV/V) | US$ sin publicar — página TE indica "no disponible actualmente" | ±1% precisión. **Insuficiente para el ensayo P5 completo** (890 N < 2240 N de prueba, < 4480 N última) — mismo problema de subdimensionamiento que TAL107F, aunque con ~9× más margen. Podría alcanzar para el caso de carga puntual ~1200 N si se acepta operar sobre el 100% de su rango (no recomendable), pero no para el ensayo normativo. |
| **TE Connectivity FC2211-0000-0100-L (compression, referencia guardada 26/08)** | 100 lbf (~445 N) | OEM compression load cell, cuerpo compacto | 100 mV/V @ 5 VDC | US$ sin publicar — página TE indica "no disponible actualmente" | ±1% precisión, ±0.05%/°C estabilidad térmica, -40 a 85°C. Aún más subdimensionado que el FX1901 — mismos comentarios, más lejos todavía del rango P5. |

### Nivel C — Grado investigación (usados en biomecánica/robótica académica)

| Opción | Capacidad | Dimensiones | Salida | Costo estimado | Notas |
|---|---|---|---|---|---|
| **FUTEK LCM300 (roscado en línea, tracción/compresión)** | 50–1000 lb (23–454 kg / ~102–4448 N) | Ø ~2.5 cm, cuerpo acero inox. 17-4 PH | mV/V, ±0.25% no linealidad e histéresis | ~US$400–700 nuevo; ~US$190 visto de segunda mano (250 lb) | El modelo de 500 lb (2224 N) coincide casi exactamente con la fuerza de prueba P5 (2240 N); el de 1000 lb (4448 N) coincide casi exactamente con la fuerza última P5 (4480 N) — es el ajuste más preciso encontrado entre capacidad comercial y el requerimiento normativo. Ampliamente citado en literatura de robótica/biomecánica, lo que facilita justificar la elección en el informe. |
| **Interface SM / SMT2 (S-type roscado)** | SM: 10–1000 lbf (50 N–5 kN); SMT2 disponible en 1000 N | ~2 × 0.75 × 2.5 in (SM) | 2 mV/V, galgas compensadas en temperatura | SM: US$330–520 según capacidad (precio de catálogo EE.UU.); SMT2-1000N visto de segunda mano ~US$320 | Buena repetibilidad y bajo *creep* (0.025%), pero precio de catálogo alto para un proyecto de pregrado; considerar solo si se consigue de segunda mano o hay presupuesto de laboratorio. |

---

## 3. Recomendación

Dado que la celda de pylon **ya no es la prioridad** del semestre (esa es la plataforma AMTI, ya resuelta) pero sigue siendo necesaria para trazar el ensayo a ISO 10328, y que el proyecto ha mostrado preferencia consistente por soluciones de bajo costo bien documentadas (el mismo criterio "conectar vs. construir" usado para la plataforma de fuerza):

1. **Opción recomendada por costo/consistencia metodológica:** escalar el diseño propio tipo [16] (Al-Dahiree) a ~2500–5000 N, reutilizando el mismo flujo ya validado en el repo (FEM en Fusion 360, galgas CEA, puente de Wheatstone, amplificador INA818, calibración con pesas conocidas). Mantiene el enfoque "de bajo costo y completamente documentado" que ya justifica el proyecto, y permite diseñar la pieza para el patrón de pernos existente sin adaptadores adicionales.
2. **Opción recomendada si se prefiere no fabricar:** **FUTEK LCM300** en capacidad de 500 lb o 1000 lb — es el único candidato comercial cuyo rango de capacidad coincide casi exactamente con los valores normativos de prueba/última de P5 (2240 N / 4480 N), con no linealidad conocida y documentada (0.25%), y con salida mV/V compatible directamente con el ADS1256 ya elegido.
3. **Evitar por ahora:** TAL107F-10kg tal como está en el estado del arte — actualizar la Secc. 4.1 para marcarla como insuficiente para el ensayo normativo completo, dejándola solo como referencia de principio de sensado (galga extensométrica) si se decide fabricar la celda propia.

**Antes de decidir:** confirmar el patrón de pernos/dimensiones exactas de la placa superior del pylon (para saber si un donut/pancake o un bloque a medida encaja sin adaptador), y verificar cuánto presupuesto de laboratorio queda disponible ahora que la plataforma AMTI resolvió la partida más cara del sistema de sensores.

---

## Fuentes consultadas

- [FX1901-0001-0200-L datasheet — TE Connectivity](https://www.te.com/commerce/DocumentDelivery/DDEController?Action=srchrtrv&DocNm=FX19&DocType=Data%20Sheet&DocLang=English&PartCntxt=FX1901-0001-0200-L&DocFormat=pdf)
- [FX1901-0001-0200-L product page — TE Connectivity](https://www.te.com/en/product-FX1901-0001-0200-L.html)
- [FC2211-0000-0100-L datasheet — TE Connectivity](https://www.te.com/commerce/DocumentDelivery/DDEController?Action=srchrtrv&DocNm=FC22&DocType=Data%20Sheet&DocLang=English&PartCntxt=FC2211-0000-0100-L&DocFormat=pdf)
- [FC2211-0000-0100-L product page — TE Connectivity](https://te.com/usa-en/product-FC2211-0000-0100-L.html)

- [LSB200 S-Beam Jr. — FUTEK](https://www.futek.com/lsb200sbeamoverview)
- [LCM300 Threaded In-Line Load Cell — FUTEK](https://www.futek.com/store/load-cells/threaded-in-line-load-cells/miniature-threaded-in-line-LCM300)
- [FUTEK LCM300 250 lbs, precio de segunda mano](https://www.dougdeals.com/futek-lcm300-mini-load-cell-250-lbs-tension-compression/)
- [Thru-Hole/Donut Load Cells — FUTEK](https://www.futek.com/store/custom-sensors-and-instruments/through-hole-load-cells)
- [Through Hole / Donut Load Cell — Transducer Techniques](https://www.transducertechniques.com/through-hole-donut-load-cell.aspx)
- [Compact Threaded Miniature Load Cell (XFTC301) — TE Connectivity](https://www.te.com/en/product-CAT-FLS0024.html)
- [SM S-Type Load Cell — Interface](https://www.interfaceforce.com/products/load-cells/tension-compression/sm-s-type-load-cell/)
- [Interface SMT2-1000N-38, listado con precio](https://www.ebay.de/itm/315142861364)
- [ATO.com — catálogo y precios de celdas de carga](https://www.ato.com/load-cell)
- [Honeywell Model 31 Series — datasheet](https://automation.honeywell.com/us/en/products/sensing-solutions/test-and-measurement/load-cells/model-31-series)
- [Honeywell Model 31, 25 lb — precio Newark](https://www.newark.com/honeywell/060-1430-04/load-cell/dp/27M1584)
- [Instrumented Pyramid Adapter for Amputee Gait Analysis (FM-PLS, sensado magnético) — NSF PAR](https://par.nsf.gov/servlets/purl/10482753)
- [iPecs Lab — RTC Electronics (celda de 6 ejes portátil)](https://rtcelectronicsinc.com/ipecs_tech.html)
