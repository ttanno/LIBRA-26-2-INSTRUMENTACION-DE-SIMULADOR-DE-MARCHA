"""
Procesa las corridas de prueba_angulos_conocidos.py (subida 0->60 y bajada
60->0, 3 repeticiones por angulo) para evaluar linealidad, exactitud,
repetibilidad e histeresis del BNO055 (eje roll) contra el soporte de arco
indexado. Ver Reportes-Semanales/S9 para el contexto completo.

No requiere argumentos -- el mapeo de archivos esta fijado a mano abajo
porque varias posiciones se tuvieron que repetir por desconexiones durante
la toma de datos (ver MAPA mas abajo, con comentarios de que se descarto y
por que).

Uso:
    python analizar_linealidad.py
"""
import csv
import statistics

import matplotlib.pyplot as plt

# Paleta validada del proyecto (ver dataviz skill) -- slot 1 azul, slot 2
# naranja, pasan el chequeo de separacion CVD como par adyacente.
COLOR_SUBIDA = "#2a78d6"
COLOR_BAJADA = "#eb6834"
COLOR_IDEAL = "#898781"   # muted/axis
COLOR_GRID = "#e1e0d9"
COLOR_AXIS = "#c3c2b7"
COLOR_TEXT = "#0b0b0b"
COLOR_TEXT_SEC = "#52514e"

OUT_DIR = "../../../Evidencias/pruebas-imu-S9"


def _estilo_ejes(ax):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(COLOR_AXIS)
    ax.spines["bottom"].set_color(COLOR_AXIS)
    ax.grid(True, color=COLOR_GRID, linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)
    ax.tick_params(colors=COLOR_TEXT_SEC, labelsize=9)
    ax.xaxis.label.set_color(COLOR_TEXT)
    ax.yaxis.label.set_color(COLOR_TEXT)

EJE = "roll"

# direccion -> angulo_real -> lista de archivos CSV (cada uno 1 repeticion)
# Comentarios indican por que se eligio esa version cuando hubo repeticiones.
MAPA = {
    "subida": {
        0:  ["angulos_subida_0deg_01.csv", "angulos_subida_0deg_02.csv", "angulos_subida_0deg_03.csv"],
        5:  ["angulos_subida_5deg_04.csv", "angulos_subida_5deg_05.csv", "angulos_subida_5deg_06.csv"],
        10: ["angulos_subida_10deg_07.csv", "angulos_subida_10deg_08.csv", "angulos_subida_10deg_09.csv"],
        15: ["angulos_subida_15deg_10.csv", "angulos_subida_15deg_11.csv", "angulos_subida_15deg_12.csv"],
        20: ["angulos_subida_20deg_13.csv", "angulos_subida_20deg_14.csv", "angulos_subida_20deg_15.csv"],
        25: ["angulos_subida_25deg_16.csv", "angulos_subida_25deg_17.csv", "angulos_subida_25deg_18.csv"],
        30: ["angulos_subida_30deg_19.csv", "angulos_subida_30deg_20.csv", "angulos_subida_30deg_21.csv"],
        35: ["angulos_subida_35deg_22.csv", "angulos_subida_35deg_23.csv", "angulos_subida_35deg_24.csv"],
        40: ["angulos_subida_40deg_25.csv", "angulos_subida_40deg_26.csv", "angulos_subida_40deg_27.csv"],
        45: ["angulos_subida_45deg_28.csv", "angulos_subida_45deg_29.csv", "angulos_subida_45deg_30.csv"],
        50: ["angulos_subida_50deg_31.csv", "angulos_subida_50deg_32.csv", "angulos_subida_50deg_33.csv"],
        55: ["angulos_subida_55deg_34.csv", "angulos_subida_55deg_35.csv", "angulos_subida_55deg_36.csv"],
        60: ["angulos_subida_60deg_37.csv", "angulos_subida_60deg_38.csv", "angulos_subida_60deg_39.csv"],
    },
    "bajada": {
        # 0deg: se descarta angulos_bajada_final_0deg_05.csv (quedo cerca del
        # corte de conexion) -- se repitieron las 3 limpias en bajada_0_final.
        0:  ["angulos_bajada_0_final_0deg_01.csv", "angulos_bajada_0_final_0deg_02.csv", "angulos_bajada_0_final_0deg_03.csv"],
        5:  ["angulos_bajada_final_5deg_02.csv", "angulos_bajada_final_5deg_03.csv", "angulos_bajada_final_5deg_04.csv"],
        # 10deg: 2 repeticiones de bajada_resto (13,14) + 1 de bajada_final
        # (01) -- se descarta bajada_resto_10deg_15.csv (archivo cortado,
        # 7898 bytes vs ~9000-9500 de las completas).
        10: ["angulos_bajada_resto_10deg_13.csv", "angulos_bajada_resto_10deg_14.csv", "angulos_bajada_final_10deg_01.csv"],
        15: ["angulos_bajada_resto_15deg_10.csv", "angulos_bajada_resto_15deg_11.csv", "angulos_bajada_resto_15deg_12.csv"],
        20: ["angulos_bajada_resto_20deg_07.csv", "angulos_bajada_resto_20deg_08.csv", "angulos_bajada_resto_20deg_09.csv"],
        25: ["angulos_bajada_resto_25deg_04.csv", "angulos_bajada_resto_25deg_05.csv", "angulos_bajada_resto_25deg_06.csv"],
        # 30deg: se descartan angulos_bajada_30deg_19.csv (completo pero
        # sospechoso, 13090 bytes vs ~9450 tipico) y 30deg_20.csv (cortado,
        # 7410 bytes) -- se repitieron las 3 limpias en bajada_resto.
        30: ["angulos_bajada_resto_30deg_01.csv", "angulos_bajada_resto_30deg_02.csv", "angulos_bajada_resto_30deg_03.csv"],
        35: ["angulos_bajada_35deg_16.csv", "angulos_bajada_35deg_17.csv", "angulos_bajada_35deg_18.csv"],
        40: ["angulos_bajada_40deg_13.csv", "angulos_bajada_40deg_14.csv", "angulos_bajada_40deg_15.csv"],
        45: ["angulos_bajada_45deg_10.csv", "angulos_bajada_45deg_11.csv", "angulos_bajada_45deg_12.csv"],
        50: ["angulos_bajada_50deg_07.csv", "angulos_bajada_50deg_08.csv", "angulos_bajada_50deg_09.csv"],
        55: ["angulos_bajada_55deg_04.csv", "angulos_bajada_55deg_05.csv", "angulos_bajada_55deg_06.csv"],
        60: ["angulos_bajada_60deg_01.csv", "angulos_bajada_60deg_02.csv", "angulos_bajada_60deg_03.csv"],
    },
}


def leer_promedio(archivo, eje):
    with open(archivo, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    vals = [float(r[eje]) for r in rows]
    return statistics.mean(vals), statistics.pstdev(vals), len(vals)


def regresion_lineal(xs, ys):
    n = len(xs)
    mx, my = statistics.mean(xs), statistics.mean(ys)
    sxx = sum((x - mx) ** 2 for x in xs)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    syy = sum((y - my) ** 2 for y in ys)
    pendiente = sxy / sxx
    intercepto = my - pendiente * mx
    pred = [pendiente * x + intercepto for x in xs]
    ss_res = sum((y - p) ** 2 for y, p in zip(ys, pred))
    ss_tot = syy
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else float("nan")
    return pendiente, intercepto, r2


def main():
    resultados = {"subida": {}, "bajada": {}}

    for direccion, por_angulo in MAPA.items():
        print(f"\n{'='*70}\n{direccion.upper()}\n{'='*70}")
        print(f"{'Angulo real':>12s} {'Promedio '+EJE:>14s} {'Error':>8s} {'std inter-rep':>14s} {'reps':>5s}")
        for angulo in sorted(por_angulo):
            archivos = por_angulo[angulo]
            promedios_rep = []
            for a in archivos:
                prom, std_intra, n = leer_promedio(a, EJE)
                promedios_rep.append(prom)
            prom_angulo = statistics.mean(promedios_rep)
            std_entre_reps = statistics.pstdev(promedios_rep) if len(promedios_rep) > 1 else 0.0
            error = prom_angulo - angulo
            resultados[direccion][angulo] = {
                "promedio": prom_angulo, "error": error,
                "std_entre_reps": std_entre_reps, "promedios_rep": promedios_rep,
            }
            print(f"{angulo:12.1f} {prom_angulo:14.3f} {error:+8.3f} {std_entre_reps:14.4f} {len(archivos):5d}")

    # --- regresion lineal por direccion ---
    print(f"\n{'='*70}\nLINEALIDAD (regresion lineal: {EJE}_medido = pendiente * angulo_real + intercepto)\n{'='*70}")
    for direccion in ("subida", "bajada"):
        angulos = sorted(resultados[direccion])
        xs = angulos
        ys = [resultados[direccion][a]["promedio"] for a in angulos]
        pendiente, intercepto, r2 = regresion_lineal(xs, ys)
        print(f"{direccion:10s}: pendiente={pendiente:.4f}  intercepto={intercepto:+.3f}  R²={r2:.6f}")

    # --- comparacion subida vs bajada (histeresis) ---
    print(f"\n{'='*70}\nHISTERESIS (subida vs bajada, mismo angulo real)\n{'='*70}")
    print(f"{'Angulo real':>12s} {'Subida':>10s} {'Bajada':>10s} {'Diferencia':>12s}")
    diffs = []
    for angulo in sorted(resultados["subida"]):
        if angulo not in resultados["bajada"]:
            continue
        s = resultados["subida"][angulo]["promedio"]
        b = resultados["bajada"][angulo]["promedio"]
        diff = s - b
        diffs.append(diff)
        print(f"{angulo:12.1f} {s:10.3f} {b:10.3f} {diff:+12.3f}")
    if diffs:
        print(f"\nDiferencia media subida-bajada: {statistics.mean(diffs):+.3f}  (std: {statistics.pstdev(diffs):.3f})")

    # --- regresion combinada (subida+bajada) para el filtro de correccion ---
    xs_todos, ys_todos = [], []
    for direccion in ("subida", "bajada"):
        for angulo, r in resultados[direccion].items():
            xs_todos.append(angulo)
            ys_todos.append(r["promedio"])
    pendiente_c, intercepto_c, r2_c = regresion_lineal(xs_todos, ys_todos)
    print(f"\nFiltro de correccion (pool subida+bajada, {len(xs_todos)} puntos): "
          f"pendiente={pendiente_c:.4f}  intercepto={intercepto_c:+.3f}  R²={r2_c:.6f}")
    print(f"angulo_corregido = (roll_medido - ({intercepto_c:+.3f})) / {pendiente_c:.4f}")

    # --- grafico 1: medido vs real, con recta ideal ---
    fig, ax = plt.subplots(figsize=(7, 5.5), dpi=150)
    fig.patch.set_facecolor("#fcfcfb")
    ax.set_facecolor("#fcfcfb")
    rango = [0, 60]
    ax.plot(rango, rango, "--", color=COLOR_IDEAL, linewidth=1.5, label="Ideal (medido = real)", zorder=1)
    for direccion, color in (("subida", COLOR_SUBIDA), ("bajada", COLOR_BAJADA)):
        angulos = sorted(resultados[direccion])
        ys = [resultados[direccion][a]["promedio"] for a in angulos]
        ax.plot(angulos, ys, "o-", color=color, linewidth=2, markersize=8,
                 label=f"{direccion.capitalize()} (R²={regresion_lineal(angulos, ys)[2]:.4f})", zorder=3)
    _estilo_ejes(ax)
    ax.set_xlabel("Ángulo real (grados)")
    ax.set_ylabel("Roll medido, BNO055 (grados)")
    ax.set_title("Linealidad del BNO055 vs. soporte de arco indexado (0-60°)", color=COLOR_TEXT, fontsize=12, pad=12)
    ax.legend(frameon=False, fontsize=9, loc="upper left")
    fig.tight_layout()
    fig.savefig(f"{OUT_DIR}/linealidad-medido-vs-real-S9.png", facecolor=fig.get_facecolor())
    plt.close(fig)

    # --- grafico 2: error antes/despues del filtro de correccion (2 paneles) ---
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 5), dpi=150, sharey=True)
    fig.patch.set_facecolor("#fcfcfb")
    for ax in (ax1, ax2):
        ax.set_facecolor("#fcfcfb")
        ax.axhline(0, color=COLOR_IDEAL, linewidth=1.2, zorder=1)

    for direccion, color in (("subida", COLOR_SUBIDA), ("bajada", COLOR_BAJADA)):
        angulos = sorted(resultados[direccion])
        errores_crudos = [resultados[direccion][a]["error"] for a in angulos]
        ax1.plot(angulos, errores_crudos, "o-", color=color, linewidth=2, markersize=7,
                  label=direccion.capitalize(), zorder=3)

        errores_corregidos = []
        for a in angulos:
            medido = resultados[direccion][a]["promedio"]
            corregido = (medido - intercepto_c) / pendiente_c
            errores_corregidos.append(corregido - a)
        ax2.plot(angulos, errores_corregidos, "o-", color=color, linewidth=2, markersize=7,
                  label=direccion.capitalize(), zorder=3)

    for ax, titulo in ((ax1, "Antes (lectura cruda del BNO055)"), (ax2, "Después (filtro lineal de corrección)")):
        _estilo_ejes(ax)
        ax.set_xlabel("Ángulo real (grados)")
        ax.set_title(titulo, color=COLOR_TEXT, fontsize=11, pad=10)
    ax1.set_ylabel("Error = medido − real (grados)")
    ax1.legend(frameon=False, fontsize=9, loc="lower left")
    fig.suptitle("Efecto de un filtro de corrección lineal sobre el error del BNO055", color=COLOR_TEXT, fontsize=12, y=1.02)
    fig.tight_layout()
    fig.savefig(f"{OUT_DIR}/linealidad-filtro-correccion-S9.png", facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close(fig)
    print(f"\nGraficos guardados en {OUT_DIR}/")

    # --- resumen final combinado a CSV ---
    with open("resumen_linealidad_S9.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["direccion", "angulo_real", "promedio_medido", "error", "std_entre_repeticiones", "repeticiones"])
        for direccion in ("subida", "bajada"):
            for angulo in sorted(resultados[direccion]):
                r = resultados[direccion][angulo]
                w.writerow([direccion, angulo, f"{r['promedio']:.3f}", f"{r['error']:+.3f}", f"{r['std_entre_reps']:.4f}", len(r["promedios_rep"])])
    print(f"\nGuardado: resumen_linealidad_S9.csv")


if __name__ == "__main__":
    main()
