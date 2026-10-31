# Registro de trazabilidad — LIBRA

**Responsable:** Alessandro Jesus Felix Tello · **Asesor:** Dr. Dante Elías
**Creado:** 28/09/2026 (S9), en respuesta a la observación del informe de la S7.

Este registro relaciona **cada cambio** de hardware, firmware, filtrado o calibración con **las pruebas** que se hicieron con ese cambio vigente y con **sus archivos de datos**. Sirve para responder a la pregunta: "¿con qué configuración exacta se obtuvo este dato?".

## Cómo usarlo

1. **Antes de probar**, anota el cambio en la Tabla A (si hubo alguno) con un ID `C-xx`.
2. **Al terminar cada prueba o tanda**, agrega una fila en la Tabla B con un ID `P-xx`. En la columna "Config. vigente", pon los `C-xx` que estaban activos.
3. En "Firmware", pon el sketch y el **commit de git** (`git log -1 --format=%h`). Si todavía no hiciste commit, pon "sin commit" y complétalo después.
4. Si una prueba sale mala (conector suelto, sensor sin detectar, datos en 0), **igual se registra**. Explica el motivo en "Resultado" y márcala como ❌ no válida.

Las filas de la S4 a la S8 se reconstruyeron a partir de los resúmenes semanales y de los archivos del repositorio. Lo que no se pudo confirmar está marcado como *(por confirmar)*.

---

## A. Registro de cambios

| ID | Fecha | Semana | Tipo | Componente | Qué cambió | Por qué | Archivo(s) / commit | Pruebas asociadas |
|---|---|---|---|---|---|---|---|---|
| C-01 | 22–28/08 | S4 | Firmware | BNO055 | Sobremuestreo: promedio de N lecturas crudas antes de reportar | Reducir el ruido aleatorio sin agregar hardware | `Firmware/test_bno055_oversampling/` · 4720b4e | P-01 |
| C-02 | 22–28/08 | S4 | Firmware | MPU6050 | Filtro complementario propio (`GYRO_WEIGHT`=0.98) y reporte de `yaw_solo_giro` sin corregir | Comparar con el BNO055 y mostrar la deriva | `Firmware/test_mpu6050/` · 4720b4e | — |
| C-03 | 22–28/08 | S4 | Firmware | Homing del pivote | Cero absoluto por acelerómetro (MPU6050), guardado en la flash | Referencia de posición absoluta | `Firmware/homing_absoluto/` · 4720b4e | P-02 |
| C-04 | 22–28/08 | S4 | Hardware | IMU | IMU montado en un soporte impreso en 3D sobre el pylon real | Pasar de la protoboard al montaje real | `Evidencias/pruebas-imu-S4/imu-montaje-*.png` | P-02 |
| C-05 | 22–28/08 | S4 | Firmware | Homing del husillo | Homing en dos etapas con sensor Hall + imán | Cero repetible del eje del motor | `Firmware/homing_husillo_hall/` · 4720b4e | (solo firmware, sin prueba en el motor) |
| C-06 | 29/08–04/09 | S5 | Hardware | Celda de carga | Compra de la celda tipo fuelle #4, 220 lb (~978 N), patrón 3×M4 | Cierre de la selección del sensor de fuerza | `Reportes-Semanales/S5/Comparativa-LoadCells-S5.md` · 4a1273b | P-12, P-13 |
| C-07 | 05–11/09 | S6 | Firmware | BNO055 (librería) | Corrección del bug de `DFRobot_BNO055`: `readReg` llamaba a `Wire.begin()` en cada lectura | Las lecturas quedaban en 0.00 después de unos segundos | `Firmware/test_wifi_ap_bno055/`, `test_wifi_udp_bno055/` · f30ae8e | P-04 → P-05 |
| C-08 | 05–11/09 | S6 | Firmware | BNO055 / comunicación | Envío por UDP en modo AP propio (`LIBRA_ESP32`, 192.168.4.1) | Transmisión inalámbrica | `Firmware/test_wifi_ap_bno055/` · f30ae8e | P-05 |
| C-09 | 05–11/09 | S6 | Firmware | Cero absoluto (`z`) | Promedio de 200 muestras (antes 100), reporte de std y rechazo si hay movimiento > 0.5° | Captura del cero más robusta | `test_wifi_ap_bno055.ino` · f30ae8e | *(sin prueba registrada)* |
| C-10 | 05–11/09 | S6 | Calibración | Acelerómetro del BNO055 | Calibración de 6 posiciones (`calibrar_acelerometro.py`) | `calib_accel` quedaba en 0/3 | `visor_python/calibrar_acelerometro.py` · f30ae8e | *(por confirmar si se corrió)* |
| C-11 | 05–11/09 | S6 | Filtrado | BNO055 | Filtro EMA en Python (alpha 0.15 / 0.05), en post-procesamiento | Suavizar microvariaciones | `Evidencias/pruebas-imu-S5/filtro-ema-comparacion-pitch-S5.png` | P-05 |
| C-12 | 12–18/09 | S7 | Calibración | Acelerómetro del BNO055 | Escritura de `ACC_RADIUS` (~1000 mg) con `escribirAccRadiusCrudo()` — **experimental** | La librería solo expone `setAxisOffset()` | `test_wifi_ap_bno055.ino` · 5e4bdd7 | P-06 a P-09 *(por confirmar)* |
| C-13 | 12–18/09 | S7 | Filtrado / firmware | BNO055 | EMA embebido en el ESP32 (`actualizarFiltroEMA()`, alpha=0.10, corrección 0°/360°) | Filtrar en el origen | `test_wifi_ap_bno055.ino` · 5e4bdd7 | P-06 a P-10 |
| C-14 | 12–18/09 | S7 | Firmware | BNO055 | `chequearSaludConexion()`: alerta si la std de roll/pitch > 0.10° en ~5 s | Detectar problemas de conexión | `test_wifi_ap_bno055.ino` · 5e4bdd7 | P-06 a P-10 |
| C-15 | 12–18/09 | S7 | Software | Registro de CSV | `log_csv_bno055.py --pausa` (repeticiones encadenadas) y detección de captura en 0.0 | Tandas de 5 y 10 repeticiones | `visor_python/log_csv_bno055.py` · 5e4bdd7 | P-06 a P-09 |
| C-16 | 12–18/09 | S7 | Hardware | Lectura de la celda | Prueba con HX711 a 3.3 V en paralelo al ADS1256 | Aislar el "diente de sierra" del ADS1256 | `Firmware/test_hx711/` · 5e4bdd7 | P-12 |
| C-17 | 19–25/09 | S8 | Firmware | ToF | Sketch para 2× VL53L1X con reasignación I2C (ToF1→0x30, ToF2=0x29), SHUT en GPIO25/26 | Prueba pendiente desde la S7 | `Firmware/test_tof/` · 2d9b352 | P-14 |
| C-18 | 19–25/09 | S8 | Software | Visores de ToF | `reset_input_buffer()` y corrección de `UnicodeEncodeError` | Filas viejas del buffer y caídas del hilo de lectura | `Firmware/test_tof/visor_python/` · 2d9b352 | P-14 |
| C-19 | 19–25/09 | S8 | Hardware (diseño) | PCB | Diseño de la placa superior (ESP32) y del breakout del BNO055 con 3 conectores XH de 4 pines | Integración; los XH con traba atacan el falso contacto | `Evidencias/pcb-S8/` · 2d9b352 | *(sin fabricar)* |
| **C-20** | S9 | S9 | Firmware | BNO055 | **Arreglo de la inicialización del EMA** (sembrar con la primera lectura válida, no con 0°) | Bug de la S7 (P-10) | `test_wifi_ap_bno055.ino` · _(commit)_ | _(completar)_ |
| **C-21** | S9 | S9 | Hardware | Conexión del BNO055 | _(describir: cable/conector usado, cómo quedó fijado)_ | Falso contacto de la S7 (P-09) | _(foto en Evidencias/pruebas-imu-S9/)_ | _(completar)_ |
| **C-22** | 28/09 | S9 | Firmware / hardware | Bus I2C del BNO055 | SDA/SCL de GPIO21/22 (`Wire`) a **GPIO17/16 (`Wire1`)**, incluida la escritura de `ACC_RADIUS` | Pasar al pinout final de la PCB; GPIO21/22 quedan para los ToF | `Firmware/test_wifi_ap_bno055/test_wifi_ap_bno055.ino` · _(commit)_ | _(completar)_ |
| C-23 | 22/10 | S10 | Hardware (diseño) | Caja de la PCB (Component1) | Fijación de la caja al nervio central del cuerpo: se reemplaza el brazo lateral por 2 muñones con topes frontales y trampas de tuerca M3, más una contrabrida en U detrás del nervio (2× M3x25 + 2 tuercas M3). Restricción vertical: pestaña bajo el bloque colgante (atrapada entre placa base y bloque) con 3 costillas de aplastamiento de 0.3 mm. Interior de la caja sin cambios. Para imprimir en 3D (PLA/PETG) | Sujetar la caja sin perforar el cuerpo | `Claude outputs/caja_abrazadera_nervio/` | *(sin imprimir)* |
| C-24 | 22/10 | S10 | Hardware (diseño) | Caja de la PCB (Component1) | Tapa deslizante en rieles (entra por +x). Paredes elevadas para dejar 20 mm libres sobre los standoffs. USB-C y borneras hacia −x, con ventana de 16 mm de alto en esa pared. 25 mm abiertos por arriba en el lado +x (conector XH y headers). Seguro por resalte elástico en la tapa | Cerrar la caja dejando salida de cables | `Claude outputs/caja_abrazadera_nervio/Tapa_deslizante.*` | *(sin imprimir)* |
| C-25 | 23/10 | S10 | Hardware (diseño) | Caja de la PCB (Component1_v3) | Cambio de anclaje: se elimina la abrazadera al nervio (muñones, topes, pestaña bajo el bloque y contrabrida). La caja se ancla a la placa superior **sin perforarla** (el cuerpo es de metal): 2 columnas en las esquinas frontales con ménsula bajo la placa y orejas fuera de su borde, más una brida en U impresa que se baja en el hueco entre los bloques superiores y abraza los bordes de la placa; 2× M3x25 verticales en x=±44, z=45 prensan la placa entre ménsula y brida. Parte de la v2 del usuario (avellanados bajo standoffs y trampa de tuerca de la pestaña) | El cuerpo tiene partes soldadas no consideradas en C-23 que interfieren con la abrazadera al nervio; se ancla arriba | `Claude outputs/caja_anclaje_superior/` | *(sin imprimir)* |
| C-26 | 23/10 | S10 | Hardware (diseño) | Caja de la PCB (Component1_v4) | Reemplaza a C-25: el anclaje pasa a las esquinas traseras (columnas por fuera de la pared trasera, z 109–117) para dejar libre el paso de cables de la esquina frontal +x. Sin perforar el cuerpo: 2 clips en C impresos sobre los bordes de la placa superior + 2× M3x25 verticales en x=±45.75, z=113. La tapa se puede sacar con la caja montada | Liberar el paso de cables de la esquina frontal +x | `Claude outputs/caja_anclaje_superior/` | *(sin imprimir)* |
| C-27 | 23/10 | S10 | Hardware (diseño) | Caja de la PCB (Caja_v5) | Rediseño completo y paramétrico (reemplaza a C-23 a C-26). Conserva todo lo esencial de la v2 del usuario: bolsillo 92×72, 4 standoffs 82.2×60.3 con avellanado Ø7, 20 mm libres, pestaña +x con 2 agujeros y trampa de tuerca, desfase de cables en la esquina frontal +x, ventana −x de 16 mm y 25 mm abiertos arriba en +x. Tapa deslizante con seguro. Anclaje arriba sin perforar: marco trasero rígido (placa + columnas + travesaño bajo la placa superior), 2 clips en C y 2× M3x25 | Unificar el diseño en un modelo limpio y más rígido | `Claude outputs/caja_v5/` (incluye `caja_libra_v5.py`) | *(sin imprimir)* |
| C-28 | 23/10 | S10 | Hardware (diseño y fabricación) | Caja de la PCB (CAJAPCB, versión final) | Versión final elegida (reemplaza a C-23 a C-27): bandeja con 4 standoffs 82.2×60.3 y 20 mm libres, ventanas laterales para USB/borneras/cables, marco de 2 columnas con cartelas y brida superior (99×20×13.5 mm) que prensa la placa superior del cuerpo con 2 pernos M3 verticales, sin perforar. Soporte integrado para un VL53L1X en la pared exterior. **Impresa en 3D** | Fijar la placa al cuerpo metálico sin perforarlo e integrar un ToF | `Evidencias/caja-pcb-S10/CAJAPCB.step`, `caja-pcb-*.png` | *(montaje pendiente)* |
| C-29 | 17–23/10 | S10 | Hardware | Placa superior (galleta 70×90) | Placa provisional terminada: ESP32 DevKit + HX711 sobre headers hembra, borneras KF301 (celda J1, 5 V J2), Molex KK con traba para BNO055 (J3, `Wire1` GPIO17/16), ToF1/ToF2 (J4/J5, GPIO21/22, SHUT 25/26) y Hall (J6, GPIO34 + pull-up 10k). Mismo pinout que la PCB final | La PCB principal no se puede fabricar por ahora; conectores con traba contra el falso contacto | `Evidencias/pcb-S10/galleta-70x90-S10.png` · `Firmware/PCB_placa_superior_PINOUT.md` | *(verificación eléctrica pendiente)* |
| C-30 | 27/10 | S11 | Software | Visor de la celda (`visor_hx711.py`) | Botón Grabar/Detener: guarda cada muestra en `grabaciones/hx711_<fecha>_<hora>.csv` con la hora de la PC tomada al llegar la línea por el puerto (`pc_time_iso, pc_time_unix_s, t_rel_s, raw_code, force_N, tared, calibrated`) | Alinear la celda con la AMTI grabando en paralelo | `Firmware/test_hx711/visor_python/visor_hx711.py` · sin commit | P-18 |
| C-31 | 30/10 | S11 | Hardware (diseño) | Caja de la PCB (nuevoPCB, reemplaza a C-28) | Caja más baja apoyada en la placa base del cuerpo: bandeja abierta para la placa 90×70 con rieles para tapa deslizante, ala lateral con canal de salida de cables y 2 orejas con agujero; 2 ganchos en C (Body5/Body6, ~102×30×15 mm) que entran por ranuras en T de la base y abrazan el borde de la placa base. Sin pernos al cuerpo ni perforaciones | Fijación más simple, con menos piezas y sin brida superior | `Evidencias/caja-pcb-S11/nuevoPCB.step`, `nuevoPCB-*.png` | *(sin imprimir)* |

---

## B. Registro de pruebas

**Resultado:** ✅ válida · ⚠️ válida con reservas · ❌ no válida

| ID | Fecha | Sensor | Objetivo | Config. vigente | Condiciones (montaje · conexión · duración) | Resultado | Datos / evidencia |
|---|---|---|---|---|---|---|---|
| P-01 | 22–28/08 | BNO055 | Verificación cualitativa del sobremuestreo | C-01 | Protoboard, inclinación a mano contra una regla | ⚠️ Solo cualitativa: sigue la inclinación (p. ej. +39.57° / −1.08°). Falta la prueba de std crudo vs. promediado | `Evidencias/pruebas-imu-S4/bno055-oversampling-banco-*.png` |
| P-02 | 29/08–04/09 | MPU6050 | Repetibilidad del homing del pivote | C-03, C-04 | Montado en el pylon real | ⚠️ Al volver a la posición de cero, el ángulo no coincide con el cero guardado. Motivó la comparativa de IMU de bajo drift | *(sin CSV)* · `Estado-del-arte/.../Comparativa-IMU-Bajo-Drift.md` |
| P-03 | 10/09 16:14 | BNO055 | Sensor quieto, ruido | C-08 | Por cable (log CSV), 30 s | ❌ `calib`=0,0,0,0; heading con salto 0°/360° | `Evidencias/pruebas-imu-S5/bno055_20260910_161442.csv` |
| P-04 | 10/09 16:20–16:51 | BNO055 | Sensor quieto, ruido | antes de C-07 | Por cable, 30 s por captura | ❌ Todo en 0.000 → llevó a encontrar el bug de la librería | `bno055_20260910_162052.csv`, `_163353`, `_164347`, `_164432`, `_165122_rep1de5` |
| P-05 | 10/09 16:48–16:54 | BNO055 | Sensor quieto, ruido (5 reps.) | C-07, C-08, C-11 | Por cable, 5 × 30 s | ⚠️ std roll 0.06–0.50°, pitch 0.29–0.54°; `calib`=0,3,0,0 (acc/mag sin calibrar); heading inútil | `bno055_20260910_164804.csv`, `_165400_rep1–5de5.csv` · `Evidencias/pruebas-imu-S5/Analisis-Prueba-Quieto-S5.md` |
| P-06 | 15/09 14:49 | BNO055 | Tanda de ruido (5 reps.) | C-12 a C-15 | *(montaje por confirmar)* | ✅ Conector bien puesto | `Firmware/test_wifi_ap_bno055/visor_python/bno055_20260915_144911_rep1–5de5.csv` |
| P-07 | 15/09 16:09–16:10 | BNO055 | Tanda de ruido (1 + 5 reps.) | C-12 a C-15 | *(por confirmar)* | ✅ | `bno055_20260915_160934_*.csv`, `_161043_rep1–5de5.csv` |
| P-08 | 15/09 16:49 | BNO055 | Tanda de ruido (5 reps.) | C-12 a C-15 | *(por confirmar)* | ⚠️/❌ Una de las dos tandas con salto de ruido (~16:50) *(por confirmar cuál)* | `bno055_20260915_164937_rep1–5de5.csv` |
| P-09 | 15/09 16:56–17:05 | BNO055 | Tandas de ruido (2 × 10 reps.) | C-12 a C-15 | Conector flojo *(cable exacto sin identificar)* | ❌ std 0.35–0.63° frente a 0.0000–0.0007° con el conector bien puesto (~500×) → **falso contacto** | `bno055_20260915_165625_rep1–10de10.csv`, `_170516_rep1–10de10.csv` · `Evidencias/pruebas-imu-S7/tendencia-ruido-conexion-S7.png` |
| P-10 | 15–16/09 | BNO055 | Crudo vs. EMA embebido | C-13 | Misma línea serial (crudo + filtrado) | ❌ Bug: el EMA arranca en 0° y tarda ~30 muestras en converger | `Evidencias/pruebas-imu-S7/comparacion1.csv`, `bug-inicializacion-ema-*.png` |
| P-11 | *(sin fecha)* | BNO055 | Sensor quieto en reposo (10 reps.) | *(por confirmar)* | *(por confirmar)* | ⚠️ Rep. 8 anómala (heading std 67°, pitch std 83°); el resto con roll std 0.19–0.58° | `visor_python/bno055_quieto_reposo_rep1–10de10.csv` · `procesado/resumen_tandas.csv` |
| P-12 | 12–18/09 | Celda + HX711 | Calibración con masa patrón | C-06, C-16 | HX711 a 3.3 V, masa patrón de 2.000 kg | ✅ 0.001098 N/cuenta; 2 kg → 19.61 N; vacío → 0.016 N; verificación → 9.84 N (≈1.004 kg) | `Evidencias/pruebas-fuerza-S7/entendiendo-cuentas-hx711-S7.csv` · `Evidencias/graficos-fuerza-S8/hx711-calibracion-S7.png` |
| P-13 | 16/09 09:45–09:47 | Celda + ADS1256 | Diagnóstico del "diente de sierra" | C-06 | *(por confirmar)* | ⚠️ Ruido tipo diente de sierra sin aislar | `Firmware/test_ads1256/visor_python/ads1256_20260916_094507.csv`, `_094700.csv` |
| P-14 | 21/09 | 2× VL53L1X | Distancia conocida (20 y 40 cm) | C-17, C-18 | ~20 s, 213 muestras válidas por sensor, ~10.8 Hz | ✅ ToF1: 408.4 mm (esperado 400, +2.1 %); ToF2: 219.5 mm (esperado 200, +9.75 %) | `Evidencias/pruebas-tof-S8/tof_20cm_40cm_prueba1.csv`, `montaje-tof-20cm-40cm-S8.jpg` |
| **P-15** | S9 | BNO055 | **Confirmar el arreglo del EMA** (el filtrado arranca en el valor real) | C-20, C-22 | _(montaje fijo · conexión · alpha · duración)_ | _(completar)_ | _(CSV + gráfico crudo vs. filtrado)_ |
| **P-16** | S9 | BNO055 | **Ruido en condiciones controladas**, sin salto entre tandas | C-20, C-21, C-22 | _(misma posición, mismo cable, sin tocar, mismo tiempo de estabilización)_ | _(completar)_ | _(CSVs de la tanda)_ |
| **P-17** | S9 | Celda + ADS1256 | **Comparación HX711 vs. ADS1256** (misma celda, misma masa) | C-06 | _(completar)_ | _(completar)_ | _(completar)_ |
| P-18 | 27/10 14:42–14:46 | Celda + HX711 vs. AMTI | Comparar la celda contra la plataforma de fuerza de referencia | C-06, C-16, C-30 | Celda sobre la AMTI, carga axial en escalones; HX711 ~11.5 Hz, AMTI 1000 Hz; desfase corregido a mano (−2.04 s / +1.28 s) | ⚠️ Lineal y repetible: F = 5.15·Fz − 26 y F = 5.03·Fz − 20, R² = 0.999, RMSE ≈ 5 N. AMTI saturada desde ~580 N; celda cargada hasta ~1270 N (sobre su nominal); unidad de Fz sin confirmar | `Firmware/test_hx711/visor_python/grabaciones/hx711_20261027_144216.csv` (Trial00530), `_144423.csv` (Trial00533) · `Evidencias/pruebas-fuerza-amti-S11/` |

---

## Pendientes de este registro

- Confirmar qué tanda del 15/09 (16:49 o 16:56) tuvo el primer salto de ruido y qué cable/conector era.
- Confirmar si se corrió la calibración de 6 posiciones (C-10) y con qué resultado.
- Fechar la tanda `bno055_quieto_reposo` (P-11) y anotar su configuración.
- Desde la S9: hacer un commit antes de cada tanda para que el hash identifique el firmware exacto.
