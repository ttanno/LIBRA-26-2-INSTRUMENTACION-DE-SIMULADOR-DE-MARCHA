# Antes/despues de la correccion preliminar del roll (ver correccion_preliminar_roll.md)
import pandas as pd, numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
M, B = 0.9694, -1.867
t = pd.read_csv("angulos_20260929_171116_std_roll_sin3.csv")
t["corr"] = (t.media - B) / M; t["std_c"] = t["std"] / M
t["e0"] = t.media - t.angulo_real; t["e1"] = t["corr"] - t.angulo_real
C0, C1, ink = "#e07b39", "#2a6fdb", "#333"
fig, (a, b) = plt.subplots(1, 2, figsize=(11.5, 4.8))
a.plot([-2, 32], [-2, 32], "--", color="#999", lw=1.2, label="Ideal")
n0 = (t.angulo_real == 0).sum(); off = iter(np.linspace(-0.9, 0.9, n0))
dx = [next(off) if k == 0 else 0 for k in t.angulo_real]
a.errorbar(t.angulo_real + dx, t.media, yerr=t["std"], fmt="o", ms=7, color=C0, ecolor=ink, capsize=4, label="Antes (medido)")
a.errorbar(t.angulo_real + dx, t["corr"], yerr=t.std_c, fmt="s", ms=7, color=C1, ecolor=ink, capsize=4, label="Después (corregido)")
a.set_xticks([0, 20, 30]); a.set_xlabel("Ángulo real (°)"); a.set_ylabel("Roll (°)")
a.set_title("Roll vs. ángulo conocido (media ± std)"); a.legend(frameon=False, loc="upper left"); a.grid(alpha=.25)
p = np.arange(len(t)); w = 0.38
b.bar(p - w/2, t.e0, w, color=C0, label="Antes"); b.bar(p + w/2, t.e1, w, color=C1, label="Después")
for i, r in t.iterrows():
    b.text(i - w/2, r.e0 - 0.08, f"{r.e0:+.2f}", ha="center", va="top", fontsize=8, color=ink)
    b.text(i + w/2, r.e1 + (0.05 if r.e1 >= 0 else -0.08), f"{r.e1:+.2f}", ha="center", va="bottom" if r.e1 >= 0 else "top", fontsize=8, color=ink)
b.axhline(0, color=ink, lw=0.8); b.set_ylim(-3.3, 0.9)
b.set_xticks(p); b.set_xticklabels([f"#{e}\n{k}°" for e, k in zip(t.ensayo, t.angulo_real)])
b.set_xlabel("Ensayo / ángulo real"); b.set_ylabel("Error (°)"); b.set_title("Error por ensayo"); b.legend(frameon=False, loc="upper center", ncol=2, bbox_to_anchor=(0.5, 1.0)); b.grid(axis="y", alpha=.25)
for ax in (a, b): [ax.spines[s].set_visible(False) for s in ("top", "right")]
fig.suptitle(f"BNO055 – corrección preliminar del roll: corregido = (medido + {-B:.3f}) / {M:.4f}\n"
             f"Sesión 29/09/2026, ensayo 3 excluido · RMSE {np.sqrt((t.e0**2).mean()):.2f}° → {np.sqrt((t.e1**2).mean()):.2f}°", fontweight="bold")
fig.tight_layout(); fig.savefig("angulos_20260929_171116_correccion_roll.png", dpi=160)
