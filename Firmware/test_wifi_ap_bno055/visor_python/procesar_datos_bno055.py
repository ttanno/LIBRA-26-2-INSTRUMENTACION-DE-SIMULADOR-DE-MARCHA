"""
Procesa los CSV del BNO055 que ya estan grabados en este directorio (los que
genera log_csv_bno055.py y comparar_filtro_ema.py) -- no requiere el sensor
ni el puerto serial conectado, solo lee los archivos.

Hace dos cosas:

1) Tandas de captura (bno055_<fecha>_<hora>[_repXdeN].csv):
   agrupa las repeticiones de cada tanda, calcula promedio y desviacion
   estandar de heading/roll/pitch/ax/ay/az por repeticion, y guarda todo en
   un solo CSV resumen. Tambien genera un grafico de la desviacion estandar
   promedio (roll/pitch) por tanda a lo largo del dia -- util para ver
   saltos de ruido entre tandas (p.ej. un conector que se aflojo a mitad de
   sesion, como paso el 15/09 -- ver Reportes-Semanales/S7).

2) Comparaciones crudo vs. filtrado (comparar_filtro_ema.py, p.ej.
   comparacion1.csv): genera los graficos de heading/pitch y de roll,
   crudo vs. filtrado, para revisar el comportamiento del filtro EMA
   (p.ej. el transitorio de arranque en 0 grados).

Uso:
    python procesar_datos_bno055.py
    python procesar_datos_bno055.py --dir . --salida procesado

Requiere: pip install -r requirements.txt (matplotlib)
"""

import argparse
import csv
import re
import statistics
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

CAMPOS_NUM = ["heading", "roll", "pitch", "ax", "ay", "az"]

REP_RE = re.compile(r"^(?P<base>bno055_.+?)_rep(?P<rep>\d+)de(?P<total>\d+)\.csv$")
FECHA_HORA_RE = re.compile(r"^bno055_(?P<fecha>\d{8})_(?P<hora>\d{6})")

COLUMNAS_COMPARACION = [
    "heading_crudo", "roll_crudo", "pitch_crudo",
    "heading_filtrado", "roll_filtrado", "pitch_filtrado",
]


# --------------------------------------------------------------------------
# 1) Tandas de captura (log_csv_bno055.py)
# --------------------------------------------------------------------------

def leer_captura(ruta: Path):
    """Lee un CSV de log_csv_bno055.py. Devuelve {campo: [valores]}."""
    datos = {c: [] for c in CAMPOS_NUM}
    with ruta.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for fila in reader:
            for c in CAMPOS_NUM:
                try:
                    datos[c].append(float(fila[c]))
                except (KeyError, ValueError, TypeError):
                    pass
    return datos


def agrupar_tandas(directorio: Path):
    """Agrupa los CSV de captura por tanda (misma corrida de
    log_csv_bno055.py). Devuelve {base: [(rep, total, ruta), ...]}, excluyendo
    los CSV de comparacion (que tienen otras columnas)."""
    tandas = defaultdict(list)
    for ruta in sorted(directorio.glob("bno055_*.csv")):
        m = REP_RE.match(ruta.name)
        if m:
            base, rep, total = m.group("base"), int(m.group("rep")), int(m.group("total"))
        else:
            base, rep, total = ruta.stem, 1, 1
        tandas[base].append((rep, total, ruta))
    for base in tandas:
        tandas[base].sort(key=lambda t: t[0])
    return tandas


def hora_de_base(base: str):
    """Devuelve un datetime si el nombre de la tanda trae fecha_hora
    (bno055_YYYYMMDD_HHMMSS...); si no (p.ej. 'bno055_quieto_reposo'),
    devuelve None."""
    m = FECHA_HORA_RE.match(base)
    if not m:
        return None
    return datetime.strptime(m.group("fecha") + m.group("hora"), "%Y%m%d%H%M%S")


def procesar_tandas(directorio: Path, salida_dir: Path):
    tandas = agrupar_tandas(directorio)
    if not tandas:
        print("No se encontraron CSV de captura (bno055_*.csv) en", directorio)
        return

    filas_resumen = []
    puntos_tendencia = []  # (hora, base, roll_std_prom, pitch_std_prom)

    print("=== Tandas de captura encontradas ===")
    for base in sorted(tandas, key=lambda b: (hora_de_base(b) or datetime.min, b)):
        reps = tandas[base]
        print(f"\n{base}  ({len(reps)} repeticion(es) encontradas)")
        roll_stds, pitch_stds = [], []

        for rep, total, ruta in reps:
            datos = leer_captura(ruta)
            filas = len(datos["heading"])
            fila = {"tanda": base, "rep": rep, "total": total, "archivo": ruta.name, "filas": filas}

            if filas >= 2:
                for c in CAMPOS_NUM:
                    fila[f"{c}_prom"] = round(statistics.mean(datos[c]), 4)
                    fila[f"{c}_std"] = round(statistics.pstdev(datos[c]), 4)
                roll_stds.append(fila["roll_std"])
                pitch_stds.append(fila["pitch_std"])
                print(
                    f"  rep{rep}de{total}: {filas:4d} filas  "
                    f"roll_std={fila['roll_std']:.4f}  pitch_std={fila['pitch_std']:.4f}  "
                    f"ax_std={fila['ax_std']:.4f}  ay_std={fila['ay_std']:.4f}  az_std={fila['az_std']:.4f}"
                )
            else:
                for c in CAMPOS_NUM:
                    fila[f"{c}_prom"] = ""
                    fila[f"{c}_std"] = ""
                print(f"  rep{rep}de{total}: {filas:4d} filas (muy pocas para estadisticas)")

            filas_resumen.append(fila)

        hora = hora_de_base(base)
        if hora is not None and roll_stds and pitch_stds:
            puntos_tendencia.append((hora, base, statistics.mean(roll_stds), statistics.mean(pitch_stds)))

    salida_dir.mkdir(parents=True, exist_ok=True)

    ruta_resumen = salida_dir / "resumen_tandas.csv"
    columnas = ["tanda", "rep", "total", "archivo", "filas"]
    for c in CAMPOS_NUM:
        columnas += [f"{c}_prom", f"{c}_std"]
    with ruta_resumen.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columnas)
        writer.writeheader()
        writer.writerows(filas_resumen)
    print(f"\nResumen guardado: {ruta_resumen}")

    if len(puntos_tendencia) >= 2:
        puntos_tendencia.sort(key=lambda p: p[0])
        fechas_distintas = len({p[0].date() for p in puntos_tendencia}) > 1
        fmt = "%d/%m %H:%M" if fechas_distintas else "%H:%M"
        etiquetas = [p[0].strftime(fmt) for p in puntos_tendencia]
        roll_prom = [p[2] for p in puntos_tendencia]
        pitch_prom = [p[3] for p in puntos_tendencia]

        fig, ax1 = plt.subplots(figsize=(10, 5))
        ax1.plot(etiquetas, roll_prom, marker="o", color="#3B82F6", label="roll (std promedio)")
        ax1.plot(etiquetas, pitch_prom, marker="o", color="#F97316", label="pitch (std promedio)")
        ax1.set_xlabel("Hora de la tanda")
        ax1.set_ylabel("Desviacion estandar (grados)")
        ax1.set_title("Ruido (std) promedio de roll/pitch por tanda de captura")
        ax1.grid(True, alpha=0.3)
        ax1.legend()
        plt.setp(ax1.get_xticklabels(), rotation=45, ha="right")
        fig.tight_layout()
        ruta_png = salida_dir / "tendencia_ruido.png"
        fig.savefig(ruta_png, dpi=150)
        plt.close(fig)
        print(f"Grafico guardado: {ruta_png}")
    else:
        print("\nNo hay suficientes tandas con fecha/hora en el nombre para graficar la tendencia de ruido.")


# --------------------------------------------------------------------------
# 2) Comparaciones crudo vs. filtrado (comparar_filtro_ema.py)
# --------------------------------------------------------------------------

def detectar_comparaciones(directorio: Path):
    """Devuelve la lista de CSV cuyo encabezado coincide con el de
    comparar_filtro_ema.py (crudo vs. filtrado)."""
    encontrados = []
    for ruta in sorted(directorio.glob("*.csv")):
        try:
            with ruta.open(newline="", encoding="utf-8") as f:
                encabezado = next(csv.reader(f), None)
        except (OSError, UnicodeDecodeError):
            continue
        if encabezado == COLUMNAS_COMPARACION:
            encontrados.append(ruta)
    return encontrados


def procesar_comparaciones(directorio: Path, salida_dir: Path):
    archivos = detectar_comparaciones(directorio)
    if not archivos:
        print("\nNo se encontraron CSV de comparacion crudo/filtrado (formato de comparar_filtro_ema.py).")
        return

    salida_dir.mkdir(parents=True, exist_ok=True)
    print("\n=== Comparaciones crudo vs. filtrado (EMA) encontradas ===")

    for ruta in archivos:
        with ruta.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            filas = [
                {k: float(v) for k, v in fila.items()}
                for fila in reader
            ]
        if len(filas) < 2:
            print(f"{ruta.name}: muy pocas filas, se omite.")
            continue

        muestras = list(range(1, len(filas) + 1))

        def col(nombre):
            return [f[nombre] for f in filas]

        print(f"\n{ruta.name} ({len(filas)} muestras)")
        for filtrado, crudo in (("heading", "heading_crudo"), ("roll", "roll_crudo"), ("pitch", "pitch_crudo")):
            c, fdat = col(crudo), col(f"{filtrado}_filtrado")
            std_c, std_f = statistics.pstdev(c), statistics.pstdev(fdat)
            print(f"  {filtrado:<8} std crudo={std_c:.4f}  std filtrado={std_f:.4f}")

        prefijo = ruta.stem

        fig, (axp, axh) = plt.subplots(2, 1, figsize=(9, 7), sharex=True)
        for ax, campo, titulo in ((axp, "pitch", "Pitch"), (axh, "heading", "Heading")):
            ax.plot(muestras, col(f"{campo}_crudo"), color="#16A34A", label="crudo")
            ax.plot(muestras, col(f"{campo}_filtrado"), color="#DC2626", label="filtrado (EMA)")
            ax.set_ylabel(f"{titulo} (grados)")
            ax.set_title(f"{titulo}: crudo vs. filtrado")
            ax.grid(True, alpha=0.3)
            ax.legend()
        axh.set_xlabel("Muestra")
        fig.tight_layout()
        ruta_png = salida_dir / f"{prefijo}_pitch_heading.png"
        fig.savefig(ruta_png, dpi=150)
        plt.close(fig)
        print(f"  Grafico guardado: {ruta_png}")

        fig, ax = plt.subplots(figsize=(9, 4))
        ax.plot(muestras, col("roll_crudo"), color="#16A34A", label="crudo")
        ax.plot(muestras, col("roll_filtrado"), color="#DC2626", label="filtrado (EMA)")
        ax.set_xlabel("Muestra")
        ax.set_ylabel("Roll (grados)")
        ax.set_title("Roll: crudo vs. filtrado")
        ax.grid(True, alpha=0.3)
        ax.legend()
        fig.tight_layout()
        ruta_png = salida_dir / f"{prefijo}_roll.png"
        fig.savefig(ruta_png, dpi=150)
        plt.close(fig)
        print(f"  Grafico guardado: {ruta_png}")


# --------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description="Procesa los CSV del BNO055 ya grabados (sin necesitar el sensor)")
    ap.add_argument("--dir", default=".", help="Directorio con los CSV (default: directorio actual)")
    ap.add_argument("--salida", default="procesado", help="Directorio de salida para el resumen y los graficos (default: procesado)")
    args = ap.parse_args()

    directorio = Path(args.dir)
    if not directorio.is_dir():
        print(f"No existe el directorio: {directorio}")
        sys.exit(1)
    salida_dir = directorio / args.salida

    procesar_tandas(directorio, salida_dir)
    procesar_comparaciones(directorio, salida_dir)

    print(f"\nListo. Resultados en: {salida_dir}")


if __name__ == "__main__":
    main()
