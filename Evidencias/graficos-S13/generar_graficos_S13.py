"""Gráficos de resultados de la S13 (P-19 a P-22 y verificación de distancia ToF).
Uso (desde la raíz del repo):  py Evidencias/graficos-S13/generar_graficos_S13.py
Solo lee las evidencias existentes; escribe los PNG en Evidencias/graficos-S13/."""
from pathlib import Path
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

RAIZ = Path(__file__).resolve().parents[2]
EV = RAIZ / "Evidencias"; INT = EV / "integracion-sensores-S13"; OUT = EV / "graficos-S13"
P19 = INT / "int2_20261110_161647"; P20 = INT / "integracion_20261110_165539"
C = {"cel": "#2a6f97", "t1": "#d1495b", "t2": "#edae49", "imu": "#00798c", "pit": "#6c757d", "err": "#000000"}
plt.rcParams.update({"figure.dpi": 150, "font.size": 9, "axes.grid": True, "grid.alpha": .3,
                     "axes.spines.top": False, "axes.spines.right": False})
COL_ERR = {"HX711": "cel", "ToF1": "t1", "ToF2": "t2", "BNO055": "imu"}

def leer(base):
    h = pd.read_csv(f"{base}_hx711.csv"); t = pd.read_csv(f"{base}_tof.csv")
    i = pd.read_csv(f"{base}_imu.csv"); e = pd.read_csv(f"{base}_errores.csv")
    t = t.assign(valida=(t.status == 0) & (t.dist_mm < 4000))  # 64351 mm = fuera de rango aunque status 0
    return h, t[t.sensor == 1], t[t.sensor == 2], i, e

def validas(t): return t[t.valida]

def marcar_errores(ax, e, sensor):
    for ts in e[e.sensor == sensor].t_s: ax.axvline(ts, color="k", lw=.6, ls=":", alpha=.7)

def series(base, titulo, archivo, mov=False):
    h, t1, t2, i, e = leer(base); ok = i[i.ok == 1]
    fig, ax = plt.subplots(4, 1, figsize=(8, 8.5), sharex=True)
    ax[0].plot(h.t_s, h.force_N - h.force_N.median(), color=C["cel"], lw=.6)
    ax[0].set_ylabel("Celda: F − mediana (N)")
    for a, t, k, nom in ((ax[1], t1, "t1", "ToF1"), (ax[2], t2, "t2", "ToF2")):
        v = validas(t); a.plot(v.t_s, v.dist_mm, color=C[k], lw=.7); a.set_ylabel(f"{nom} (mm)"); marcar_errores(a, e, nom)
        inv = t[~t.valida]
        for ts in inv.t_s: a.axvline(ts, color="#7b2cbf", lw=1, alpha=.6)
        if len(inv): a.text(.01, .04, f"{len(inv)} lecturas inválidas (líneas moradas: {(inv.status != 0).sum()} con status≠0, "
                             f"{((inv.status == 0) & (inv.dist_mm >= 4000)).sum()} de 64351 mm con status 0)",
                             transform=a.transAxes, fontsize=6.5, color="#7b2cbf")
    t1, t2 = validas(t1), validas(t2)
    marcar_errores(ax[3], e, "BNO055")
    if mov:
        ax[3].plot(ok.t_s, ok.roll, color=C["imu"], lw=.8); ax[3].set_ylabel("Roll (°)")
        a3 = ax[3].twinx(); a3.plot(ok.t_s, ok.pitch, color=C["pit"], lw=.8, ls="--"); a3.set_ylabel("Pitch (°, gris)")
        a3.spines["right"].set_visible(True); a3.grid(False)
    else:
        ax[3].plot(ok.t_s, ok.roll - ok.roll.iloc[0], color=C["imu"], lw=1.4, label=f"roll (inicio {ok.roll.iloc[0]:.2f}°)")
        ax[3].plot(ok.t_s, ok.pitch - ok.pitch.iloc[0], color=C["pit"], lw=1, ls="--", label=f"pitch (inicio {ok.pitch.iloc[0]:.2f}°)")
        ax[3].set_ylim(-.5, .5); ax[3].set_ylabel("Ángulo − inicial (°)"); ax[3].legend(fontsize=7, loc="upper left")
    if mov:
        for a, d, nom in ((ax[1], t1.dist_mm, "X"), (ax[2], t2.dist_mm, "Y")):
            lo, hi = d.min(), d.max()
            a.axhspan(lo, hi, color="grey", alpha=.08)
            a.set_title(f"Recorrido {nom}: {lo:.0f}–{hi:.0f} mm = {hi-lo:.0f} mm", fontsize=8, loc="right")
        lo, hi = ok.roll.min(), ok.roll.max()
        ax[3].set_title(f"Recorrido roll: {lo:.1f}° ↔ {hi:.1f}° = {hi-lo:.1f}°  (comandado 20°)", fontsize=8, loc="right")
    else:
        for a, d, u in ((ax[0], h.force_N, "N"), (ax[1], t1.dist_mm, "mm"), (ax[2], t2.dist_mm, "mm")):
            a.set_title(f"std = {d.std():.3f} {u}", fontsize=8, loc="right")
        ax[3].set_title(f"roll std = {ok.roll.std():.3f}°, pitch std = {ok.pitch.std():.3f}°", fontsize=8, loc="right")
    ax[3].set_xlabel("Tiempo (s, reloj del ESP32)")
    fig.suptitle(titulo + "\n(líneas punteadas: errores I2C/lectura registrados)", fontsize=10)
    fig.tight_layout(); fig.savefig(OUT / archivo); plt.close(fig)

def frecuencias():
    est = pd.read_csv(f"{P19}_estado.csv")
    fig, ax = plt.subplots(2, 1, figsize=(8, 5.5), sharex=True)
    for col, k, nom in (("cntH", "cel", "Celda"), ("cntT1", "t1", "ToF1"), ("cntT2", "t2", "ToF2"), ("cntI", "imu", "IMU")):
        f = est[col].diff() / est.t_s.diff()
        ax[0].plot(est.t_s, f.rolling(10, center=True).mean(), color=C[k], lw=1, label=f"{nom} ({f.mean():.2f} Hz)")
    ax[0].axhline(10, color="k", lw=.7, ls="--"); ax[0].set_ylabel("Frecuencia (Hz, media 10 s)")
    ax[0].legend(ncol=4, fontsize=7, loc="lower center"); ax[0].set_ylim(9, 12.5)
    ax[1].plot(est.t_s, est.loopMax_us / 1000, color="k", lw=.7)
    ax[1].set_ylabel("Loop máx. por segundo (ms)"); ax[1].set_xlabel("Tiempo (s)")
    m = est.loopMax_us.idxmax(); ax[1].annotate(f"{est.loopMax_us[m]/1000:.0f} ms (I2C colgado)", (est.t_s[m], est.loopMax_us[m]/1000),
                                                xytext=(-120, -10), textcoords="offset points", fontsize=7, arrowprops=dict(arrowstyle="->"))
    fig.suptitle("P-19 · T-INT2 en reposo: frecuencia real de cada sensor y duración del loop", fontsize=10)
    fig.tight_layout(); fig.savefig(OUT / "P19_frecuencias_loop.png"); plt.close(fig)

def errores_comparacion():
    filas = []
    for nom, base in (("P-19 reposo", P19), ("P-20 movimiento", P20)):
        h, t1, t2, i, e = leer(base); dur = max(h.t_s.max(), i.t_s.max()) / 60
        filas.append((nom, [(e.sensor == s).sum() / dur for s in ("HX711", "ToF1", "ToF2", "BNO055")], dur))
    x = np.arange(4); w = .38
    fig, ax = plt.subplots(figsize=(7, 3.8))
    for j, (nom, v, dur) in enumerate(filas):
        b = ax.bar(x + (j - .5) * w, v, w, label=f"{nom} ({dur:.1f} min)", color=["#adb5bd", "#495057"][j])
        ax.bar_label(b, fmt="%.1f", fontsize=7)
    ax.set_xticks(x, ["Celda", "ToF1", "ToF2", "IMU"]); ax.set_ylabel("Errores registrados por minuto")
    ax.set_title("Errores por sensor: reposo (P-19) vs movimiento (P-20)\nlíneas E del ESP32 (máx. una cada 500 ms por sensor)", fontsize=9)
    ax.legend(fontsize=8); fig.tight_layout(); fig.savefig(OUT / "P19_P20_errores_por_minuto.png"); plt.close(fig)

def p20_recorridos():
    _, t1, t2, i, _ = leer(P20); ok = i[i.ok == 1]; t1, t2 = validas(t1), validas(t2)
    med = [np.ptp(t1.dist_mm), np.ptp(t2.dist_mm), np.ptp(ok.roll)]
    ref = [100, 50, 20]; err = [100 * (m - r) / r for m, r in zip(med, ref)]
    fig, ax = plt.subplots(figsize=(6.5, 3.6)); x = np.arange(3)
    ax.bar(x - .2, ref, .4, color="#adb5bd", label="Comandado"); b = ax.bar(x + .2, med, .4, color=[C["t1"], C["t2"], C["imu"]], label="Medido")
    ax.bar_label(b, labels=[f"{m:.0f}\n({e:+.0f} %)" for m, e in zip(med, err)], fontsize=7)
    ax.set_xticks(x, ["ToF1 – X (mm)", "ToF2 – Y (mm)", "IMU – roll (°)"]); ax.set_ylim(0, 130)
    ax.set_title("P-20 · recorrido medido (mín–máx, lecturas válidas) vs comandado en el simulador", fontsize=9); ax.legend(fontsize=8)
    fig.tight_layout(); fig.savefig(OUT / "P20_recorrido_vs_comandado.png"); plt.close(fig)

def p21_celda():
    reps = [pd.read_csv(EV / "pruebas-fuerza-S13" / f"tcel1_20261110_172035_rep{k}de3.csv") for k in (1, 2, 3)]
    fig, ax = plt.subplots(1, 2, figsize=(9, 3.8), gridspec_kw={"width_ratios": [2, 1]})
    for k, d in enumerate(reps, 1):
        tt = np.arange(len(d)) / 11.5 if d.t_s.diff().max() < .05 else d.t_s - d.t_s.iloc[0]
        ax[0].plot(tt, d.force_N, lw=.6, label=f"Toma {k}")
        s = d.force_N[tt >= 20] if k == 3 else d.force_N
        ax[1].hist(s - s.mean(), bins=40, histtype="step", lw=1.2,
                   label=f"Toma {k}: std {s.std():.3f} N" + (" (t≥20 s)" if k == 3 else ""))
    ax[0].axvline(20, color="k", ls=":", lw=.7); ax[0].text(20.5, ax[0].get_ylim()[1]*.9, "fin del transitorio\n(toma 3)", fontsize=7)
    ax[0].set_xlabel("Tiempo (s)"); ax[0].set_ylabel("Fuerza (N)"); ax[0].legend(fontsize=7)
    ax[1].set_xlabel("F − media (N)"); ax[1].set_ylabel("Muestras"); ax[1].legend(fontsize=6.5)
    fig.suptitle("P-21 · T-CEL1: ruido de la celda en reposo (factor 0.00024704 N/cuenta, por verificar con masa patrón)", fontsize=9)
    fig.tight_layout(); fig.savefig(OUT / "P21_ruido_celda.png"); plt.close(fig)

def p22_imu():
    reps = [pd.read_csv(EV / "pruebas-imu-S13" / f"timu1_20261110_173304_rep{k}de3.csv") for k in (1, 2, 3)]
    fig, ax = plt.subplots(3, 1, figsize=(8, 6.5), sharex=True)
    for k, d in enumerate(reps, 1):
        tt = d.t_s - d.t_s.iloc[0]
        ax[0].plot(tt, d.roll, lw=1, label=f"Toma {k} (std {d.roll.std():.4f}°)")
        ax[1].plot(tt, d.pitch, lw=1, label=f"Toma {k} (std {d.pitch.std():.4f}°)")
        ax[2].plot(tt, np.sqrt(d.ax**2 + d.ay**2 + d.az**2), lw=.6, label=f"Toma {k}")
    for a, v in ((ax[0], reps[0].roll.mean()), (ax[1], reps[0].pitch.mean())):
        a.set_ylim(v - .3, v + .3); a.axhspan(v - .0625/2, v + .0625/2, color="grey", alpha=.15)
    ax[0].set_ylabel("Roll (°)"); ax[1].set_ylabel("Pitch (°)"); ax[2].set_ylabel("|a lineal| (m/s²)")
    ax[0].legend(fontsize=7); ax[1].legend(fontsize=7); ax[2].set_xlabel("Tiempo (s)")
    ax[0].set_title("Franja gris: resolución del BNO055 (0.0625°); la aceleración sí varía → el sensor no está congelado", fontsize=8)
    fig.suptitle("P-22 · T-IMU1: ruido del IMU en reposo (calibración 1,3,3,0)", fontsize=10)
    fig.tight_layout(); fig.savefig(OUT / "P22_ruido_imu.png"); plt.close(fig)

def verif_tof():
    # Valores de la verificación de distancia del 10/11 (aún sin fila P-23 en el registro)
    nom = ["ToF1", "ToF2"]; med = [348.2, 746.2]; std = [1.5, 2.3]; ref = [368.3, 760.0]
    fig, ax = plt.subplots(figsize=(6, 3.6)); x = np.arange(2)
    ax.bar(x - .2, ref, .4, color="#adb5bd", label="Referencia (cinta)")
    b = ax.bar(x + .2, med, .4, yerr=std, capsize=3, color=[C["t1"], C["t2"]], label="Medido (media ± std)")
    ax.bar_label(b, labels=[f"{m-r:+.1f} mm" for m, r in zip(med, ref)], padding=6, fontsize=8)
    ax.set_xticks(x, nom); ax.set_ylabel("Distancia (mm)"); ax.set_ylim(0, 880); ax.legend(fontsize=8, loc="upper left")
    ax.set_title("Verificación de distancia de los ToF (preliminar, por registrar como P-23)\nambos miden de menos → probable offset / punto de referencia", fontsize=9)
    fig.tight_layout(); fig.savefig(OUT / "verificacion_distancia_ToF.png"); plt.close(fig)

if __name__ == "__main__":
    series(P19, "P-19 · T-INT2: adquisición simultánea en reposo (5 min)", "P19_series_reposo.png")
    frecuencias(); errores_comparacion()
    series(P20, "P-20 · adquisición simultánea en movimiento (X 10 cm, Y 5 cm, roll −20°↔0°)", "P20_series_movimiento.png", mov=True)
    p20_recorridos(); p21_celda(); p22_imu(); verif_tof()
    print("\n".join(sorted(p.name for p in OUT.glob("*.png"))))
