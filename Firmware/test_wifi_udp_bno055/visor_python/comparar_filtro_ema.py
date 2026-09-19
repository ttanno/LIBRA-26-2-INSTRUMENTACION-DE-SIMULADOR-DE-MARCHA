"""
Compara el dato CRUDO vs el FILTRADO (EMA) del BNO055, leyendo ambos de la
MISMA linea que ya manda el ESP32 (Euler[...] = filtrado, EulerCrudo[...] =
crudo) -- no hace falta grabar dos veces ni tocar el firmware para esto.

Uso:
    python comparar_filtro_ema.py --port COM7
    python comparar_filtro_ema.py --port COM7 --muestras 30
    python comparar_filtro_ema.py --port COM7 --muestras 30 --salida comparacion1.csv

Requiere que el ESP32 ya tenga cargado el sketch con el filtro EMA
(test_wifi_ap_bno055.ino o test_wifi_udp_bno055.ino, version con
EulerCrudo[...]) -- si no aparece ese campo en la linea, este script no va
a encontrar nada que comparar.
"""

import argparse
import csv
import re
import statistics
import sys
import time

import serial
import serial.tools.list_ports

LINE_RE = re.compile(
    r"Calib\[sys,gyro,accel,mag\]=(?P<sys>\d+),(?P<gyro>\d+),(?P<accel>\d+),(?P<mag>\d+)\s*\|\s*"
    r"Euler\[heading,roll,pitch\]=(?P<heading>-?\d+\.\d+),(?P<roll>-?\d+\.\d+),(?P<pitch>-?\d+\.\d+)\s*\|\s*"
    r"LinAccel\[x,y,z\]=(?P<ax>-?\d+\.\d+),(?P<ay>-?\d+\.\d+),(?P<az>-?\d+\.\d+).*"
    r"EulerCrudo\[heading,roll,pitch\]=(?P<headingC>-?\d+\.\d+),(?P<rollC>-?\d+\.\d+),(?P<pitchC>-?\d+\.\d+)"
)


def elegir_puerto() -> str:
    puertos = list(serial.tools.list_ports.comports())
    if not puertos:
        print("No se detecto ningun puerto serial. Conecta el ESP32 y vuelve a intentar.")
        sys.exit(1)
    print("Puertos disponibles:")
    for i, p in enumerate(puertos):
        print(f"  [{i}] {p.device} - {p.description}")
    idx = input("Elige el numero de puerto: ").strip()
    try:
        return puertos[int(idx)].device
    except (ValueError, IndexError):
        print("Seleccion invalida.")
        sys.exit(1)


def main():
    ap = argparse.ArgumentParser(description="Compara BNO055 crudo vs filtrado (EMA) en vivo")
    ap.add_argument("--port", help="Puerto serial (ej. COM7). Si se omite, se pide interactivamente.")
    ap.add_argument("--baud", type=int, default=115200)
    ap.add_argument("--muestras", type=int, default=30, help="Cuantas lineas leer (default 30)")
    ap.add_argument("--salida", default=None, help="Si se indica, guarda un CSV con crudo y filtrado lado a lado")
    args = ap.parse_args()

    puerto = args.port or elegir_puerto()

    try:
        ser = serial.Serial(puerto, args.baud, timeout=1)
    except serial.SerialException as e:
        print(f"No se pudo abrir {puerto}: {e}")
        sys.exit(1)

    time.sleep(2)
    print(f"Conectado a {puerto} @ {args.baud} baudios.")
    print(f"Leyendo {args.muestras} muestras (crudo + filtrado en la misma linea)...")

    filas = []
    while len(filas) < args.muestras:
        try:
            linea = ser.readline().decode("utf-8", errors="replace").strip()
        except serial.SerialException:
            print("Se perdio la conexion con el puerto serial.")
            break
        if not linea:
            continue
        m = LINE_RE.search(linea)
        if not m:
            # Puede ser una linea de ALERTA[conexion] u otra cosa -- se ignora.
            continue
        d = m.groupdict()
        filas.append(d)
        print(f"  [{len(filas)}/{args.muestras}] "
              f"crudo(roll={d['rollC']}, pitch={d['pitchC']})  "
              f"filtrado(roll={d['roll']}, pitch={d['pitch']})", end="\r")

    ser.close()
    print()

    if len(filas) < 2:
        print("Muy pocas muestras validas -- revisa que el sketch cargado ya tenga el campo EulerCrudo[...].")
        sys.exit(1)

    def col(nombre):
        return [float(f[nombre]) for f in filas]

    pares = [
        ("heading", "headingC"),
        ("roll", "rollC"),
        ("pitch", "pitchC"),
    ]

    print(f"\n=== Comparacion crudo vs filtrado (EMA) -- {len(filas)} muestras ===")
    print(f"{'variable':<10} {'std crudo':>10} {'std filtrado':>13} {'reduccion':>10}")
    resumen = {}
    for filtrado, crudo in pares:
        c = col(crudo)
        f = col(filtrado)
        std_c = statistics.pstdev(c)
        std_f = statistics.pstdev(f)
        reduccion = (1 - std_f / std_c) * 100 if std_c > 0 else float("nan")
        resumen[filtrado] = (std_c, std_f, reduccion)
        print(f"{filtrado:<10} {std_c:>10.4f} {std_f:>13.4f} {reduccion:>9.1f}%")

    print(
        "\nSi 'reduccion' sale alta (varias decenas %), el filtro esta suavizando ruido real.\n"
        "Si sale baja o negativa, o si el std crudo YA era muy chico (sensor muy estable/conexion\n"
        "buena), no hay mucho que reducir -- eso tambien es un resultado valido, no un error."
    )

    if args.salida:
        with open(args.salida, "w", newline="", encoding="utf-8") as fcsv:
            writer = csv.writer(fcsv)
            writer.writerow([
                "heading_crudo", "roll_crudo", "pitch_crudo",
                "heading_filtrado", "roll_filtrado", "pitch_filtrado",
            ])
            for d in filas:
                writer.writerow([
                    d["headingC"], d["rollC"], d["pitchC"],
                    d["heading"], d["roll"], d["pitch"],
                ])
        print(f"\nGuardado: {args.salida}")


if __name__ == "__main__":
    main()
