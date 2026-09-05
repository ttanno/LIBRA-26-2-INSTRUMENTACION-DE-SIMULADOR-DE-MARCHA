# Comparativa — Celdas de carga y electrónica de lectura (Semana 5, Amazon)

**Fecha:** 31/08/2026
**Contexto:** seguimiento directo del pendiente heredado "Selección de sensor de fuerza del pylon" (`S4/Pendientes.md`) y de `Estado-del-arte/SENSORES DE FUERZA/PYLON/Comparativa-Sensores-Fuerza-Axial-Pylon.md` (19/08/2026). Esta nota compara 4 celdas de carga y 2 módulos de electrónica encontrados en Amazon durante la S5, contra los mismos requisitos ya fijados: **fuerza de prueba P5 = 2240 N**, **fuerza última P5 = 4480 N**, margen objetivo **~1.5–2× sobre la última**, interfaz mecánica real de **placa plana atornillada** (no pyramid adapter roscado), y electrónica ya decidida (ADS1256, salida cruda mV/V preferida sobre módulos con amplificador integrado).

Tipo de cambio usado para referencia: ~S/ 3.7 por US$ (aproximado, solo para comparar contra los US$ de la comparativa anterior).

---

## 1. Celdas de carga candidatas

| # | Producto (link) | Marca | Tipo / interfaz mecánica | Precisión | Rango de tamaños ofrecidos | Precio (todas las capacidades) | Envío a Perú |
|---|---|---|---|---|---|---|---|
| 1 | [Mini Célula de Carga, tipo fuelle](https://www.amazon.com/-/es/Tensión-Compresión-Presión-Precisión-Diámetro/dp/B0D78XJHKW) | QILICHUANGAN | Fuelle/pancake, acero aleado, disco con orificios en placas superior/inferior | 0.3% | 20, 50, 200, 300, 500, 1000, 2000 kg | PEN 164.35 | Sí (+ PEN 57.90 envío) |
| 2 | [Sensor de célula de carga, tipo varilla](https://www.amazon.com/-/es/compresión-inoxidable-precisión-industrial-medición/dp/B0D7C9ZHY5) | QILICHUANGAN | Varilla/tirante roscada en ambos extremos, acero inoxidable | 0.1% | 10, 20, 30, 50, 100, 200 kg | PEN 177.65 | Sí, gratis |
| 3 | [Celda de carga en línea miniatura 58mm](https://www.amazon.com/-/es/STCELLS-miniatura-medición-impacto-compresión/dp/B0CPSZQ3M2) | STCELLS | Fuelle/pancake, acero aleado, 58mm | No visible (bloqueado) | 30, 100, 200, 500, 1000, 2000, 5000 kg | No visible | **No** — "no puede enviarse a punto de entrega seleccionado" |
| 4 | [Sensor tipo fuelle, Ø2.283in, 3×M4](https://www.amazon.com/compresión-diámetro-exterior-precisión-0-0-44-1/dp/B0D66THCRR) | QILICHUANGAN | Fuelle/pancake, Ø58mm × 30mm, **patrón de pernos 3×M4 documentado**, acero aleado | 0.2% | 22, 44, 110, 220, 440, 1100, 2200, 4400, 6600, 11000 lb | PEN 181.12 | Sí, gratis (quedan 8 en stock) |

### 1.1 Capacidad en N, filtrada contra el requisito P5 (proof 2240 N / última 4480 N)

Solo se muestran las capacidades relevantes (cerca o por encima del margen objetivo 1.5–2×):

| Producto | Capacidad seleccionada | Fuerza (N) | Margen sobre última (4480 N) | Evaluación |
|---|---|---|---|---|
| #1 (fuelle, 0.3%) | 500 kg | 4 903 N | 1.09× | Insuficiente margen — operaría casi al límite |
| #1 (fuelle, 0.3%) | **1000 kg** | **9 807 N** | **2.19×** | **Cumple el margen objetivo** |
| #1 (fuelle, 0.3%) | 2000 kg | 19 613 N | 4.38× | Sobredimensionado — pierde resolución |
| #2 (varilla, 0.1%) | 200 kg (máximo disponible) | 1 961 N | 0.44× | **No cumple ni la fuerza de prueba** — descartado para el ensayo P5 |
| #4 (fuelle, 0.2%, M4) | 1100 lb | 4 893 N | 1.09× | Insuficiente margen — mismo problema que #1 a 500 kg |
| #4 (fuelle, 0.2%, M4) | **2200 lb** | **9 786 N** | **2.18×** | **Cumple el margen objetivo**, capacidad casi idéntica a #1 a 1000 kg |
| #4 (fuelle, 0.2%, M4) | 4400 lb | 19 572 N | 4.37× | Sobredimensionado |

**Producto #3 (STCELLS)** habría cubierto el rango igual de bien (500–2000 kg), pero Amazon no permite enviarlo al punto de entrega actual — queda descartado por disponibilidad, no por especificación. Como alternativa, Amazon sugiere en la misma página un "ATO Célula de carga de tensión y compresión" a PEN 595.38 (4.6★, envío Prime) — bastante más caro que las opciones QILICHUANGAN; no se investigó en detalle porque no era foco de esta semana.

---

## 2. Análisis frente a los criterios del proyecto

- **Interfaz mecánica (placa atornillada):** el producto **#4** es el único que documenta explícitamente el patrón de pernos (3×M4) en la ficha, lo que encaja directo con la placa superior del pylon (`parte-instrumentada.jpg`, ya referenciado en la comparativa anterior) sin necesitar adaptador. El producto **#1** tiene la misma forma física de disco con orificios (visible en las fotos), pero la ficha no confirma el patrón de pernos — habría que verificarlo con el vendedor o al recibir la pieza. El producto **#2** es tipo varilla roscada en línea, que la comparativa anterior ya identificó como menos compatible con esta interfaz real (favorece sensores pancake/donut sobre roscados en línea).
- **Salida eléctrica:** ninguna de las dos fichas de #1 o #2 especifica si la salida es mV/V cruda (puente de Wheatstone) compatible directo con el ADS1256 ya decidido. El producto **#4 sí especifica "Tipo de salida: Push-Pull"**, que normalmente describe una etapa digital/de conmutación y no un puente crudo — **esto es una señal de alerta a verificar antes de comprar**, porque podría no ser compatible con el ADS1256 sin conversión adicional (contradiría la razón por la que se descartó HX711 en la comparativa anterior). El producto #1 no menciona el tipo de salida en la ficha visible; solo indica voltaje de alimentación (10 V), consistente con excitación de puente pero sin confirmar el formato de la señal de vuelta.
- **No linealidad:** las tres opciones QILICHUANGAN (0.1–0.3%) están muy por debajo del objetivo del proyecto (<8%), así que la precisión no es un factor decisivo aquí — el diferenciador real es la interfaz mecánica y el tipo de salida.
- **Precio:** las tres opciones QILICHUANGAN cuestan prácticamente lo mismo (PEN 164–181, ≈ US$ 44–49) sin importar la capacidad elegida dentro del mismo listado — mucho más barato que las opciones de Nivel B/C de la comparativa anterior (Transducer Techniques, FUTEK, Interface, US$ 330–700). Esto es coherente con el enfoque de bajo costo ya usado en el proyecto, pero también significa menos garantía de calibración de fábrica que las opciones profesionales — habrá que calibrar con pesas conocidas de todas formas, como ya se documentó para el diseño propio tipo [16].

---

## 3. Electrónica de lectura (verificación del ADS1256 ya decidido)

| Producto | Función | Precio | Envío a Perú | Nota |
|---|---|---|---|---|
| [Teyleten Robot ADS1256, 24-bit, 8 canales](https://www.amazon.com/-/es/Teyleten-ADS1256-8-Channel-precisión-adquisición/dp/B0F4DPM9J1) | ADC dedicado — mismo chip ya decidido en la comparativa anterior | PEN 46.96 + PEN 54.72 envío ≈ PEN 101.68 total | Sí | Confirma que el ADS1256 decidido sí está disponible como módulo comprable en Amazon con envío a Perú, a un costo bajo (~US$ 27 total). Salida SPI, 30 ksps, no linealidad ±0.001%. |
| [SparkFun Amplificador HX711](https://www.amazon.com/-/es/SparkFun-Amplificador-célula-carga-Configuración/dp/B079LVMC6X) | Amplificador dedicado con salida digital integrada (alternativa al ADS1256) | PEN 38.61 + PEN 54.55 envío ≈ PEN 93.16 total | Sí | Es la opción que la comparativa anterior explícitamente descartó para no duplicar acondicionamiento (el ADS1256 ya lee la celda en paralelo con IMU/encoder). Se deja como referencia/respaldo, no como plan actual. |

---

## 4. Recomendación

1. **Celda de carga:** entre las opciones nuevas de esta semana, la mejor combinación costo/margen/interfaz es **#1 (QILICHUANGAN fuelle, variante 1000 kg, PEN 164.35)** como primera opción — capacidad casi idéntica a #4 en 2200 lb (~9.8 kN, margen 2.18–2.19× sobre la última P5) y sin la ambigüedad de salida "Push-Pull". **#4 (variante 2200 lb, PEN 181.12)** queda como segunda opción, mejor documentada mecánicamente (3×M4 confirmado) pero pendiente de aclarar si su salida es realmente compatible con el ADS1256.
2. **Antes de comprar cualquiera de las dos:** escribir al vendedor (QILICHUANGAN / QL Sensor) para confirmar (a) tipo de salida real (mV/V crudo vs. amplificado) y (b) patrón de pernos exacto de la variante elegida, ya que ninguna ficha lo confirma al 100% para la opción #1.
3. **Descartar #2 (varilla)** para el ensayo P5 completo — su capacidad máxima (200 kg ≈ 1961 N) no alcanza ni la fuerza de prueba (2240 N), y su interfaz roscada en línea es menos compatible con la placa atornillada real del pylon. Queda como referencia solo si se necesitara medir una carga puntual menor (ej. el caso de ~1200 N que sigue pendiente de simular en Fusion 360).
4. **Descartar #3 (STCELLS)** por ahora — no disponible para envío a Perú en este momento; no vale la pena investigar el precio hasta confirmar disponibilidad, o evaluar la alternativa ATO sugerida (PEN 595.38) si se necesita con urgencia.
5. **Electrónica:** el ADS1256 (Teyleten Robot, PEN ~101.68 con envío) confirma y cierra la parte de "verificar disponibilidad" del pendiente heredado — es comprable y barato. El HX711 (SparkFun) queda documentado solo como alternativa de respaldo, no como plan de compra.

---

## Pendiente para la próxima semana

- Confirmar con el vendedor el tipo de salida real de las opciones #1 y #4 antes de decidir cuál comprar.
- Cerrar la elección final entre #1 (1000 kg) y #4 (2200 lb) — o entre estas y la opción de fabricar la celda propia escalada (`Comparativa-Sensores-Fuerza-Axial-Pylon.md`, Nivel A) — y proceder con la compra/cotización.
- Actualizar `Estado-del-arte/SENSORES DE FUERZA/PYLON/Comparativa-Sensores-Fuerza-Axial-Pylon.md` con estas 4 opciones nuevas de Amazon como una fila adicional de "Nivel A" (bajo costo), ya que no estaban incluidas en la revisión del 19/08.

---

## Fuentes

- [Mini Célula de Carga, tipo fuelle (B0D78XJHKW)](https://www.amazon.com/-/es/Tensión-Compresión-Presión-Precisión-Diámetro/dp/B0D78XJHKW)
- [Sensor de célula de carga, tipo varilla (B0D7C9ZHY5)](https://www.amazon.com/-/es/compresión-inoxidable-precisión-industrial-medición/dp/B0D7C9ZHY5)
- [Celda de carga en línea miniatura STCELLS (B0CPSZQ3M2)](https://www.amazon.com/-/es/STCELLS-miniatura-medición-impacto-compresión/dp/B0CPSZQ3M2)
- [Sensor tipo fuelle Ø2.283in, 3×M4 (B0D66THCRR)](https://www.amazon.com/compresión-diámetro-exterior-precisión-0-0-44-1/dp/B0D66THCRR)
- [SparkFun Amplificador HX711 (B079LVMC6X)](https://www.amazon.com/-/es/SparkFun-Amplificador-célula-carga-Configuración/dp/B079LVMC6X)
- [Teyleten Robot ADS1256 (B0F4DPM9J1)](https://www.amazon.com/-/es/Teyleten-ADS1256-8-Channel-precisión-adquisición/dp/B0F4DPM9J1)
- `Estado-del-arte/SENSORES DE FUERZA/PYLON/Comparativa-Sensores-Fuerza-Axial-Pylon.md` — comparativa previa (19/08/2026), fuente de los requisitos P5 y de la interfaz mecánica.
- `Reportes-Semanales/S4/Pendientes.md` — pendiente heredado de selección de sensor de fuerza del pylon.
