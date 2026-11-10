"""
T-INT2 -- Registro y analisis de la adquisicion simultanea
(test_integracion_sensores.ino: celda/HX711 + 2x VL53L1X + BNO055).

Registra por cable (COM) la salida del ESP32 durante la duracion pedida
(5 min por defecto) y al terminar:
  1. separa los datos por sensor en CSV,
  2. calcula la frecuencia real, los intervalos entre muestras, los huecos
     (muestras perdidas), los errores de cada sensor y las lineas perdidas
     en el Serial,
  3. escribe un resumen en Markdown con los criterios de aceptacion y una
     grafica de intervalos.

Uso:
    python log_integracion.py --port COM7                  # 5 min
    python log_integracion.py --port COM7 --duracion 60    # prueba corta
    python log_integracion.py --analizar int2_20261110_101500_raw.log

Archivos que genera (mismo prefijo, en la carpeta actual o en --carpeta):
    <prefijo>_raw.log        todo lo que llego por Serial, con hora del PC
    <prefijo>_hx711.csv      t_s, raw, force_N
    <prefijo>_tof.csv        t_s, sensor, dist_mm, status
    <prefijo>_imu.csv        t_s, dur_us, ok, roll, pitch, heading, sys, gyr, acc, mag
    <prefijo>_estado.csv     lineas S (contadores acumulados por segundo)
    <prefijo>_errores.csv    lineas E
    <prefijo>_resumen.md     resultados y criterios
    <prefijo>_intervalos.png grafica (si matplotlib esta instalado)

Requiere: pyserial y numpy (matplotlib opcional, solo para la grafica).
El modo --analizar no necesita pyserial.
"""

import argparse
import csv
import os
import re
import sys
import time
from collections import Counter
from datetime import datetime

import numpy as np

MARCA_INICIO_PC = "# PC INICIO_REGISTRO"
MARCA_INICIO_ESP = "# CONTADORES REINICIADOS"
MARCA_LISTO = "# LISTO"

# Criterios propuestos (no estan fijados en la tabla de T-INT2; se proponen
# aqui y se pueden ajustar)
TOL_FRECUENCIA = 0.05        # frecuencia real dentro de +-5 % de la nominal (IMU)
# El HX711 usa su oscilador interno (sin cristal): su tasa real no es
# exactamente 10 SPS (en la S12 se anoto ~11.5 Hz para la celda). Por eso su
# frecuencia se reporta como dato y lo que se evalua es que sea regular.
# Los VL53L1X igual: el periodo entre mediciones lo cuenta su oscilador
# interno, que en esta placa corre ~8 % rapido (100 ms -> 10.8 Hz, y con
# 50 ms + budget de 50 ms salian ~10.8 Hz = 21.6/2; medido el 2026-11-10).
SIN_CRITERIO_FRECUENCIA = {"H", "T1", "T2"}
MAX_PERDIDAS_PCT = 0.1       # muestras perdidas estimadas <= 0.1 %
FACTOR_HUECO = 1.5           # intervalo > 1.5 x mediana -> hueco
CONGELADO_S_DEFAULT = 10.0   # valores identicos seguidos por >= 10 s -> posible congelamiento

NOMBRES = {"H": "Celda (HX711)", "T1": "ToF1 (U3, 0x30)", "T2": "ToF2 (U2, 0x29)", "I": "IMU (BNO055)"}

STATUS_TOF = {
    0: "RangeValid", 1: "SigmaFail", 2: "SignalFail", 3: "RangeValidMinRangeClipped",
    4: "OutOfBoundsFail", 5: "HardwareFail", 6: "RangeValidNoWrapCheckFail",
    7: "WrapTargetFail", 8: "ProcessingFail", 9: "XtalkSignalFail",
    10: "SynchronizationInt", 11: "MergedPulse", 12: "TargetPresentLackOfSignal",
    13: "MinRangeFail", 14: "RangeInvalid", 254: "None",
}


def imprimir(texto: str):
    try:
        print(texto)
    except UnicodeEncodeError:
        enc = sys.stdout.encoding or "utf-8"
        print(texto.encode(enc, errors="replace").decode(enc, errors="replace"))


# =======================================================================
# Registro
# =======================================================================

def elegir_puerto(serial_mod) -> str:
    import serial.tools.list_ports
    puertos = list(serial.tools.list_ports.comports())
    if not puertos:
        imprimir("No se detecto ningun puerto serial. Conecta el ESP32 y vuelve a intentar.")
        sys.exit(1)
    imprimir("Puertos disponibles:")
    for i, p in enumerate(puertos):
        imprimir(f"  [{i}] {p.device} - {p.description}")
    idx = input("Elige el numero de puerto: ").strip()
    try:
        return puertos[int(idx)].device
    except (ValueError, IndexError):
        imprimir("Seleccion invalida.")
        sys.exit(1)


def registrar(puerto, baud, duracion, descartar, ruta_raw):
    try:
        import serial
    except ImportError:
        imprimir("Falta pyserial: pip install pyserial")
        sys.exit(1)

    puerto = puerto or elegir_puerto(serial)
    imprimir(f"Abriendo {puerto} a {baud} baudios...")
    ser = serial.Serial(puerto, baud, timeout=0.2)

    with open(ruta_raw, "w", encoding="utf-8", newline="") as f:
        t_abre = time.time()

        def leer_linea():
            raw = ser.readline()
            if not raw:
                return None
            linea = raw.decode("utf-8", errors="replace").strip()
            if linea:
                f.write(f"{time.time() - t_abre:.3f}\t{linea}\n")
            return linea

        # 1) Esperar el reporte inicial (abrir el puerto suele reiniciar el ESP32)
        imprimir("Esperando el reporte inicial del ESP32...")
        listo = False
        pedido_i = False
        t0 = time.time()
        while time.time() - t0 < 15:
            linea = leer_linea()
            if linea is None:
                if not pedido_i and time.time() - t0 > 6:
                    ser.write(b"i\n")   # no se reinicio al abrir: pedir el reporte
                    pedido_i = True
                continue
            if linea.startswith("#"):
                imprimir(linea)
            if linea.startswith(MARCA_LISTO):
                listo = True
                break
        if not listo:
            imprimir("AVISO: no llego '# LISTO'. Se registra igual; revisa que el sketch cargado sea test_integracion_sensores.ino.")

        # 2) Asentamiento: se descartan los primeros segundos
        if descartar > 0:
            imprimir(f"Asentamiento: descartando {descartar:.0f} s...")
            t0 = time.time()
            while time.time() - t0 < descartar:
                linea = leer_linea()
                if linea and linea.startswith("E,"):
                    imprimir("  " + linea)

        # 3) Reiniciar contadores y registrar
        ser.write(b"r\n")
        f.write(f"{time.time() - t_abre:.3f}\t{MARCA_INICIO_PC}\n")
        imprimir(f"Registrando {duracion:.0f} s (Ctrl+C para cortar antes)...")
        t0 = time.time()
        proximo_aviso = 10.0
        ultima_s = None
        try:
            while time.time() - t0 < duracion:
                linea = leer_linea()
                if not linea:
                    continue
                if linea.startswith("S,"):
                    ultima_s = linea
                elif linea.startswith("E,"):
                    imprimir("  " + linea)
                transcurrido = time.time() - t0
                if transcurrido >= proximo_aviso:
                    proximo_aviso += 10.0
                    if ultima_s:
                        c = ultima_s.split(",")
                        imprimir(f"  {transcurrido:5.0f} s | H={c[3]} T1={c[4]} T2={c[5]} I={c[6]} | "
                                 f"err H={c[7]} T1={c[8]} T2={c[9]} I={c[10]} | loopMax={c[11]} us")
        except KeyboardInterrupt:
            imprimir("Registro cortado por el usuario.")
    ser.close()
    imprimir(f"Log guardado en {ruta_raw}")


# =======================================================================
# Lectura del log
# =======================================================================

RE_CONFIG = re.compile(r"(\w+)=(\d+)")


def leer_log(ruta_raw):
    """Devuelve (info, datos, malformadas). datos: lista de (tipo, campos) en
    orden de llegada, solo despues de la marca de inicio."""
    info = {"config": {}, "scan": [], "init": "", "cal": "", "otros": []}
    lineas = []
    with open(ruta_raw, encoding="utf-8", errors="replace") as f:
        for fila in f:
            fila = fila.rstrip("\n")
            linea = fila.split("\t", 1)[1] if "\t" in fila else fila
            lineas.append(linea.strip())

    # Inicio: preferir la confirmacion del ESP32 tras la marca del PC
    idx_inicio = 0
    if MARCA_INICIO_PC in lineas:
        idx_inicio = lineas.index(MARCA_INICIO_PC)
        for k in range(idx_inicio, min(idx_inicio + 200, len(lineas))):
            if lineas[k].startswith(MARCA_INICIO_ESP):
                idx_inicio = k
                break

    datos = []
    malformadas = 0
    largos = {"H": 5, "T": 6, "I": 12, "S": 13, "E": 6}
    for k, linea in enumerate(lineas):
        if linea.startswith("#"):
            if linea.startswith("# CONFIG"):
                info["config"] = {a: int(b) for a, b in RE_CONFIG.findall(linea)}
            elif linea.startswith("# SCAN"):
                if linea not in info["scan"]:
                    info["scan"].append(linea)
            elif linea.startswith("# INIT"):
                info["init"] = linea
            elif linea.startswith("# CAL"):
                info["cal"] = linea
            continue
        if k <= idx_inicio:
            continue
        campos = linea.split(",")
        tipo = campos[0]
        if tipo not in largos or len(campos) != largos[tipo]:
            malformadas += 1
            continue
        datos.append((tipo, campos))
    return info, datos, malformadas


def desenvolver_micros(t_us):
    """micros() del ESP32 es uint32 y da la vuelta cada ~71.6 min."""
    t = np.asarray(t_us, dtype=np.float64)
    if len(t) < 2:
        return t
    saltos = np.diff(t) < -(2 ** 31)
    return t + np.concatenate([[0], np.cumsum(saltos)]) * 2 ** 32


# =======================================================================
# Analisis
# =======================================================================

def analizar_intervalos(t_s, nominal_hz):
    r = {"n": int(len(t_s))}
    if len(t_s) < 3:
        return r
    dt_ms = np.diff(t_s) * 1000.0
    med = float(np.median(dt_ms))
    span = float(t_s[-1] - t_s[0])
    huecos = dt_ms > FACTOR_HUECO * med
    perdidas = int(np.sum(np.maximum(np.round(dt_ms[huecos] / med) - 1, 0)))
    r.update({
        "duracion_s": span,
        "f_real_hz": (len(t_s) - 1) / span if span > 0 else float("nan"),
        "f_nominal_hz": nominal_hz,
        "dt_med_ms": med,
        "dt_media_ms": float(np.mean(dt_ms)),
        "dt_std_ms": float(np.std(dt_ms)),
        "dt_min_ms": float(np.min(dt_ms)),
        "dt_p99_ms": float(np.percentile(dt_ms, 99)),
        "dt_max_ms": float(np.max(dt_ms)),
        "n_huecos": int(np.sum(huecos)),
        "perdidas_est": perdidas,
        "perdidas_pct": 100.0 * perdidas / (len(t_s) + perdidas),
        "huecos_top": sorted(
            [(float(t_s[i]), float(dt_ms[i])) for i in np.nonzero(huecos)[0]],
            key=lambda x: -x[1])[:5],
        "dt_ms": dt_ms,
    })
    return r


def racha_identica_s(t_s, valores):
    """Duracion (s) de la racha mas larga de valores identicos consecutivos."""
    if len(valores) < 2:
        return 0.0, None
    v = np.asarray(valores)
    iguales = np.all(v[1:] == v[:-1], axis=1) if v.ndim > 1 else (v[1:] == v[:-1])
    mejor, inicio, mejor_ini = 0.0, None, None
    for i, eq in enumerate(iguales):
        if eq:
            if inicio is None:
                inicio = i
            dur = t_s[i + 1] - t_s[inicio]
            if dur > mejor:
                mejor, mejor_ini = dur, t_s[inicio]
        else:
            inicio = None
    return float(mejor), mejor_ini


def analizar(ruta_raw, congelado_s=CONGELADO_S_DEFAULT):
    prefijo = ruta_raw[:-len("_raw.log")] if ruta_raw.endswith("_raw.log") else os.path.splitext(ruta_raw)[0]
    info, datos, malformadas = leer_log(ruta_raw)
    if not datos:
        imprimir("No hay datos despues de la marca de inicio en el log.")
        sys.exit(1)

    # Tiempo unico del ESP32 en orden de llegada
    t_all = desenvolver_micros([int(c[2]) for _, c in datos])
    t_ref = t_all[0]
    t_all = (t_all - t_ref) / 1e6

    n_vals = np.array([int(c[1]) for _, c in datos], dtype=np.int64)
    dn = np.diff(n_vals)
    lineas_perdidas = int(np.sum(dn[dn > 1] - 1))
    saltos_raros = int(np.sum(dn < 1))  # reinicio del ESP32 o desorden

    H, T, I, S, E = [], [], [], [], []
    for (tipo, c), t in zip(datos, t_all):
        if tipo == "H":
            H.append((t, int(c[3]), float(c[4])))
        elif tipo == "T":
            T.append((t, int(c[3]), int(c[4]), int(c[5])))
        elif tipo == "I":
            I.append((t, int(c[3]), int(c[4]), float(c[5]), float(c[6]), float(c[7]),
                      int(c[8]), int(c[9]), int(c[10]), int(c[11])))
        elif tipo == "S":
            S.append((t, *[int(x) for x in c[3:13]]))
        elif tipo == "E":
            E.append((t, c[3], c[4], c[5]))

    # ---- CSV por sensor ----
    def guardar(sufijo, cabecera, filas):
        with open(f"{prefijo}_{sufijo}.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(cabecera)
            for fila in filas:
                w.writerow([f"{x:.6f}" if isinstance(x, float) else x for x in fila])

    guardar("hx711", ["t_s", "raw", "force_N"], H)
    guardar("tof", ["t_s", "sensor", "dist_mm", "status"], T)
    guardar("imu", ["t_s", "dur_us", "ok", "roll", "pitch", "heading", "sys", "gyr", "acc", "mag"], I)
    guardar("estado", ["t_s", "cntH", "cntT1", "cntT2", "cntI", "errH", "errT1", "errT2",
                       "errI", "loopMax_us", "serialBloq"], S)
    guardar("errores", ["t_s", "sensor", "motivo", "detalle"], E)

    # ---- Frecuencias e intervalos ----
    cfg = info["config"]
    nominal = {
        "H": float(cfg.get("hx711_sps_esperado", 10)),
        "T1": 1000.0 / cfg.get("tof_periodo_ms", 50),
        "T2": 1000.0 / cfg.get("tof_periodo_ms", 50),
        "I": 1000.0 / cfg.get("imu_periodo_ms", 100),
    }
    t_por = {
        "H": np.array([x[0] for x in H]),
        "T1": np.array([x[0] for x in T if x[1] == 1]),
        "T2": np.array([x[0] for x in T if x[1] == 2]),
        "I": np.array([x[0] for x in I]),
    }
    res = {k: analizar_intervalos(t_por[k], nominal[k]) for k in t_por}

    # ---- Contadores del ESP32 (S): muestras generadas vs. recibidas ----
    cnt_esp = {}
    err_esp = {"H": 0, "T1": 0, "T2": 0, "I": 0}
    loop_max = []
    serial_bloq = 0
    if S:
        primero, ultimo = S[0], S[-1]
        for j, k in enumerate(["H", "T1", "T2", "I"]):
            cnt_esp[k] = ultimo[1 + j]
            err_esp[k] = ultimo[5 + j]
        loop_max = [s[9] for s in S]
        serial_bloq = ultimo[10]

    errores_por = Counter((e[1], e[2]) for e in E)

    # ---- ToF: estados ----
    st_tof = {s: Counter(x[3] for x in T if x[1] == s) for s in (1, 2)}

    # ---- IMU: duracion de lectura, fallas, calibracion, congelamiento ----
    imu_dur = np.array([x[1] for x in I], dtype=float)
    imu_fallas = int(sum(1 for x in I if x[2] == 0))
    imu_cong_s, imu_cong_t = racha_identica_s(t_por["I"], np.array([x[3:6] for x in I])) if I else (0.0, None)
    calib_final = I[-1][6:10] if I else None
    calib_min = tuple(min(x[6 + j] for x in I) for j in range(4)) if I else None

    # ---- HX711: congelamiento / saturacion ----
    hx_raw = np.array([x[1] for x in H])
    hx_cong_s, hx_cong_t = racha_identica_s(t_por["H"], hx_raw) if H else (0.0, None)
    hx_sat = int(np.sum((hx_raw >= 8388607) | (hx_raw <= -8388608))) if H else 0

    # ---- Criterios ----
    criterios = []

    def criterio(nombre, cumple, detalle, si_falla="NO CUMPLE"):
        criterios.append((nombre, "CUMPLE" if cumple else si_falla, detalle))

    criterio("Lineas perdidas en el Serial = 0", lineas_perdidas == 0 and malformadas == 0,
             f"{lineas_perdidas} perdidas, {malformadas} malformadas")
    criterio("Buffer del Serial sin bloqueos", serial_bloq == 0, f"serialBloq = {serial_bloq}")
    for k in ["H", "T1", "T2", "I"]:
        r = res[k]
        if r["n"] < 3:
            criterio(f"{NOMBRES[k]}: entrega datos", False, f"{r['n']} muestras")
            continue
        dev = (r["f_real_hz"] - r["f_nominal_hz"]) / r["f_nominal_hz"]
        if k in SIN_CRITERIO_FRECUENCIA:
            criterios.append((f"{NOMBRES[k]}: frecuencia real (informativo)", "INFO",
                              f"{r['f_real_hz']:.2f} Hz (nominal del modulo {r['f_nominal_hz']:.0f} Hz); "
                              f"dt std {r['dt_std_ms']:.2f} ms"))
        else:
            criterio(f"{NOMBRES[k]}: frecuencia dentro de +-{TOL_FRECUENCIA * 100:.0f} % de la nominal",
                 abs(dev) <= TOL_FRECUENCIA,
                     f"{r['f_real_hz']:.2f} Hz vs {r['f_nominal_hz']:.2f} Hz ({dev * 100:+.1f} %)")
        criterio(f"{NOMBRES[k]}: muestras perdidas <= {MAX_PERDIDAS_PCT} %",
                 r["perdidas_pct"] <= MAX_PERDIDAS_PCT,
                 f"{r['perdidas_est']} ({r['perdidas_pct']:.3f} %) en {r['n_huecos']} huecos")
        criterio(f"{NOMBRES[k]}: sin errores", err_esp[k] == 0, f"{err_esp[k]} errores")
    if I:
        criterio(f"IMU sin congelamientos (>= {congelado_s:.0f} s identico)", imu_cong_s < congelado_s,
                 f"racha mas larga {imu_cong_s:.1f} s (un IMU muy quieto puede repetir valores: "
                 f"si sale REVISAR, mover levemente la plataforma y ver si responde)", si_falla="REVISAR")
    if H:
        criterio("Celda sin congelamiento ni saturacion", hx_cong_s < congelado_s and hx_sat == 0,
                 f"racha identica {hx_cong_s:.1f} s, {hx_sat} muestras saturadas")

    evaluados = [c for c in criterios if c[1] != "INFO"]
    n_ok = sum(1 for c in evaluados if c[1] == "CUMPLE")

    # ---- Resumen Markdown ----
    nombre_base = os.path.basename(prefijo)
    md = []
    md.append(f"# T-INT2 – Adquisición simultánea ({nombre_base})\n")
    md.append(f"Análisis generado el {datetime.now():%d/%m/%Y %H:%M}. "
              f"Duración registrada: {t_all[-1]:.1f} s (reloj del ESP32).\n")
    md.append("## Configuración e inicio\n")
    if cfg:
        md.append("- " + ", ".join(f"`{a}={b}`" for a, b in cfg.items()))
    for s in info["scan"]:
        md.append(f"- `{s[2:]}`")
    if info["init"]:
        md.append(f"- `{info['init'][2:]}`")
    if info["cal"]:
        md.append(f"- `{info['cal'][2:]}`")
    md.append("")

    md.append(f"## Criterios ({n_ok}/{len(evaluados)} cumplen)\n")
    md.append("Criterios propuestos para T-INT2 (ajustables en el script).\n")
    md.append("| Criterio | Resultado | Detalle |")
    md.append("|---|---|---|")
    for c in criterios:
        md.append(f"| {c[0]} | **{c[1]}** | {c[2]} |")
    md.append("")

    md.append("## Frecuencia real e intervalos\n")
    md.append("| Sensor | Muestras | Generadas (ESP32) | f real (Hz) | f nominal (Hz) | Δt mediana (ms) | Δt std (ms) | Δt mín / p99 / máx (ms) | Huecos | Perdidas est. |")
    md.append("|---|---|---|---|---|---|---|---|---|---|")
    for k in ["H", "T1", "T2", "I"]:
        r = res[k]
        gen = cnt_esp.get(k, "–")
        if r["n"] < 3:
            md.append(f"| {NOMBRES[k]} | {r['n']} | {gen} | – | {nominal[k]:.2f} | – | – | – | – | – |")
            continue
        md.append(f"| {NOMBRES[k]} | {r['n']} | {gen} | {r['f_real_hz']:.3f} | {r['f_nominal_hz']:.2f} | "
                  f"{r['dt_med_ms']:.2f} | {r['dt_std_ms']:.2f} | "
                  f"{r['dt_min_ms']:.1f} / {r['dt_p99_ms']:.1f} / {r['dt_max_ms']:.1f} | "
                  f"{r['n_huecos']} | {r['perdidas_est']} ({r['perdidas_pct']:.3f} %) |")
    md.append("")
    md.append(f"Un hueco es un intervalo mayor que {FACTOR_HUECO}× la mediana; las muestras perdidas "
              "se estiman como round(Δt / mediana) − 1 en cada hueco. Si «Generadas» supera a «Muestras», "
              "la diferencia se perdió en el enlace Serial y no en el sensor.\n")

    huecos_txt = []
    for k in ["H", "T1", "T2", "I"]:
        for t, d in res[k].get("huecos_top", []):
            huecos_txt.append(f"- {NOMBRES[k]}: t = {t:.2f} s, Δt = {d:.1f} ms")
    if huecos_txt:
        md.append("Huecos más largos:\n")
        md.extend(huecos_txt)
        md.append("")

    md.append("## Errores y conflictos en el bus\n")
    md.append(f"- Líneas perdidas en el Serial (saltos del contador n): {lineas_perdidas}; "
              f"líneas malformadas: {malformadas}; reinicios/desorden del contador: {saltos_raros}")
    md.append(f"- Bloqueos del buffer del Serial (serialBloq): {serial_bloq}")
    if loop_max:
        lm = np.array(loop_max)
        md.append(f"- Duración máxima del loop por segundo: mediana {np.median(lm):.0f} µs, "
                  f"p99 {np.percentile(lm, 99):.0f} µs, máx {lm.max():.0f} µs")
    md.append(f"- Errores acumulados en el ESP32: HX711 {err_esp['H']}, ToF1 {err_esp['T1']}, "
              f"ToF2 {err_esp['T2']}, BNO055 {err_esp['I']}")
    if errores_por:
        for (sensor, motivo), n in sorted(errores_por.items()):
            md.append(f"  - {sensor} / {motivo}: {n} línea(s) E (se imprime como máximo una cada 500 ms por sensor)")
    md.append("")

    md.append("## Detalle por sensor\n")
    for s in (1, 2):
        tot = sum(st_tof[s].values())
        if tot == 0:
            continue
        partes = ", ".join(f"{STATUS_TOF.get(k, k)} {100 * v / tot:.1f} %" for k, v in st_tof[s].most_common())
        md.append(f"- ToF{s} – estado de rango: {partes}")
    if I:
        md.append(f"- BNO055 – duración de cada lectura (calib + Euler, Wire1): media {imu_dur.mean():.0f} µs, "
                  f"p99 {np.percentile(imu_dur, 99):.0f} µs, máx {imu_dur.max():.0f} µs; lecturas fallidas: {imu_fallas}")
        md.append(f"- BNO055 – calibración [sys,gyr,acc,mag] final {list(calib_final)}, mínima durante el registro {list(calib_min)}")
        md.append(f"- BNO055 – racha más larga de roll/pitch/heading idénticos: {imu_cong_s:.1f} s"
                  + (f" (desde t = {imu_cong_t:.1f} s)" if imu_cong_t is not None and imu_cong_s > 0 else ""))
    if H:
        md.append(f"- HX711 – racha más larga de cuentas idénticas: {hx_cong_s:.1f} s; muestras saturadas: {hx_sat}")
    md.append("")

    ruta_png = f"{prefijo}_intervalos.png"
    if graficar(res, t_por, I, imu_dur, ruta_png):
        md.append(f"![Intervalos entre muestras]({os.path.basename(ruta_png)})\n")

    with open(f"{prefijo}_resumen.md", "w", encoding="utf-8") as f:
        f.write("\n".join(md))

    # ---- Consola ----
    imprimir("")
    imprimir(f"=== T-INT2: {n_ok}/{len(evaluados)} criterios cumplen ===")
    for c in criterios:
        imprimir(f"  [{c[1]:9}] {c[0]} -> {c[2]}")
    imprimir(f"Resumen: {prefijo}_resumen.md")


def graficar(res, t_por, I, imu_dur, ruta_png):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        imprimir("(matplotlib no instalado: se omite la grafica)")
        return False
    filas = [k for k in ["H", "T1", "T2", "I"] if res[k]["n"] >= 3]
    n = len(filas) + (1 if I else 0)
    if n == 0:
        return False
    fig, ejes = plt.subplots(n, 1, figsize=(10, 2.1 * n), sharex=True)
    ejes = np.atleast_1d(ejes)
    for ax, k in zip(ejes, filas):
        r = res[k]
        ax.plot(t_por[k][1:], r["dt_ms"], lw=0.6, color="#3a6ea5")
        ax.axhline(1000.0 / r["f_nominal_hz"], color="#999999", lw=0.8, ls="--")
        ax.set_ylabel("Δt (ms)")
        ax.set_ylim(bottom=0, top=max(r["dt_max_ms"] * 1.1, 2000.0 / r["f_nominal_hz"]))
        ax.ticklabel_format(axis="y", useOffset=False)
        ax.set_title(f"{NOMBRES[k]} – {r['f_real_hz']:.2f} Hz, {r['perdidas_est']} perdidas", fontsize=9, loc="left")
    if I:
        ax = ejes[-1]
        ax.plot(t_por["I"], imu_dur / 1000.0, lw=0.6, color="#b5523b")
        ax.set_ylabel("lectura (ms)")
        ax.set_ylim(bottom=0)
        ax.ticklabel_format(axis="y", useOffset=False)
        ax.set_title("BNO055 – duración de cada lectura en Wire1", fontsize=9, loc="left")
    ejes[-1].set_xlabel("t (s)")
    fig.tight_layout()
    fig.savefig(ruta_png, dpi=130)
    plt.close(fig)
    return True


# =======================================================================

def main():
    ap = argparse.ArgumentParser(description="T-INT2: registro y analisis de adquisicion simultanea")
    ap.add_argument("--port", help="Puerto serial (ej. COM7). Si se omite, se pide interactivamente.")
    ap.add_argument("--baud", type=int, default=115200)
    ap.add_argument("--duracion", type=float, default=300.0, help="Segundos a registrar (default 300 = 5 min)")
    ap.add_argument("--descartar", type=float, default=10.0, help="Segundos de asentamiento descartados (default 10)")
    ap.add_argument("--carpeta", default=".", help="Carpeta de salida")
    ap.add_argument("--congelado", type=float, default=CONGELADO_S_DEFAULT,
                    help="Segundos de valores identicos para marcar congelamiento (default 10)")
    ap.add_argument("--analizar", metavar="RAW_LOG", help="Solo analizar un _raw.log ya registrado")
    args = ap.parse_args()

    if args.analizar:
        analizar(args.analizar, args.congelado)
        return

    os.makedirs(args.carpeta, exist_ok=True)
    ruta_raw = os.path.join(args.carpeta, f"int2_{datetime.now():%Y%m%d_%H%M%S}_raw.log")
    registrar(args.port, args.baud, args.duracion, args.descartar, ruta_raw)
    analizar(ruta_raw, args.congelado)


if __name__ == "__main__":
    main()
