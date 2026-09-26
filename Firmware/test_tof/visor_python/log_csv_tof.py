"""
Registro a CSV por cable (COM) de los 2 sensores VL53L1X (test_tof.ino) --
sin graficos, pensado para juntar una sesion de mediciones (ej. comparar
contra una distancia patron conocida) y analizarla despues. Mismo patron
que log_csv_hx711.py, adaptado al formato de salida de test_tof.ino.

Uso:
    python log_csv_tof.py --port COM7
    python log_csv_tof.py --port COM7 --duracion 15
    python log_csv_tof.py --port COM7 --duracion 15 --salida prueba1.csv

Imprime en vivo cada lectura y, al terminar, un resumen (promedio y
desviacion estandar) de cada sensor -- util para comparar contra una
distancia patron (ej. 200 mm y 400 mm) y ver que tan preciso/repetible
sale.

Requiere: pip install -r requirements.txt (ya incluye pyserial)
"""

import argparse
import csv
import statistics
import re
import sys
import time

import serial
import serial.tools.list_ports

LINE_RE = re.compile(
    r"(?P<dist1_mm>\d+),"
    r"(?P<status1>\d+),"
    r"(?P<dist2_mm>\d+),"
    r"(?P<status2>\d+)"
)

COLUMNAS = ["t_s", "dist1_mm", "status1", "dist2_mm", "status2"]
STATUS_OK = 0


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


def imprimir_seguro(texto: str):
    try:
        print(texto)
    except UnicodeEncodeError:
        enc = sys.stdout.encoding or "utf-8"
        print(texto.encode(enc, errors="replace").decode(enc, errors="replace"))


def main():
    ap = argparse.ArgumentParser(description="Registro a CSV de 2x VL53L1X (test_tof.ino) por cable (COM)")
    ap.add_argument("--port", help="Puerto serial (ej. COM7). Si se omite, se pide interactivamente.")
    ap.add_argument("--baud", type=int, default=115200, help="Baudrate (default 115200)")
    ap.add_argument(
        "--duracion", type=float, default=None,
        help="Segundos a registrar. Si se omite, registra hasta Ctrl+C.",
    )
    ap.add_argument(
        "--salida", default=None,
        help="Nombre del archivo CSV de salida (default: tof_YYYYMMDD_HHMMSS.csv)",
    )
    args = ap.parse_args()

    puerto = args.port or elegir_puerto()

    try:
        ser = serial.Serial(puerto, args.baud, timeout=1)
    except serial.SerialException as e:
        print(f"No se pudo abrir {puerto}: {e}")
        sys.exit(1)

    time.sleep(2)  # dar tiempo a que el puerto se estabilice tras abrirlo (y al ESP32 a rearrancar por el DTR)
    ser.reset_input_buffer()  # descartar datos viejos que hayan quedado en el buffer antes de esta conexion
    print(f"Conectado a {puerto} @ {args.baud} baudios.")

    nombre_salida = args.salida or time.strftime("tof_%Y%m%d_%H%M%S.csv")
    if not nombre_salida.lower().endswith(".csv"):
        nombre_salida += ".csv"

    dist1_vals, dist2_vals = [], []
    filas = 0
    t0 = time.time()

    print(f"Registrando en '{nombre_salida}'.")
    if args.duracion:
        print(f"Se detendra automaticamente en {args.duracion:.0f} s. (Ctrl+C para detener antes)")
    else:
        print("Presiona Ctrl+C para detener el registro.")

    try:
        with open(nombre_salida, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(COLUMNAS)

            while True:
                if args.duracion is not None and (time.time() - t0) >= args.duracion:
                    break

                try:
                    linea = ser.readline().decode("utf-8", errors="replace").strip()
                except serial.SerialException:
                    print("Se perdio la conexion con el puerto serial.")
                    break

                if not linea:
                    continue

                m = LINE_RE.search(linea)
                if not m:
                    imprimir_seguro(f"[ESP32] {linea}")
                    continue

                d = m.groupdict()
                t = time.time() - t0
                dist1, status1 = int(d["dist1_mm"]), int(d["status1"])
                dist2, status2 = int(d["dist2_mm"]), int(d["status2"])

                writer.writerow([f"{t:.3f}", dist1, status1, dist2, status2])
                filas += 1

                if status1 == STATUS_OK:
                    dist1_vals.append(dist1)
                if status2 == STATUS_OK:
                    dist2_vals.append(dist2)

                marca1 = "OK" if status1 == STATUS_OK else f"status={status1}"
                marca2 = "OK" if status2 == STATUS_OK else f"status={status2}"
                print(f"  t={t:6.2f}s  ToF1={dist1:5d} mm ({marca1})   ToF2={dist2:5d} mm ({marca2})")

    except KeyboardInterrupt:
        print("\nRegistro detenido por el usuario.")
    finally:
        ser.close()

    print(f"\nListo. {filas} filas guardadas en '{nombre_salida}'.")

    for nombre, vals in (("ToF1", dist1_vals), ("ToF2", dist2_vals)):
        if len(vals) >= 2:
            print(
                f"  {nombre}: {len(vals)} lecturas validas -- "
                f"promedio={statistics.mean(vals):.1f} mm   desv.estandar={statistics.pstdev(vals):.1f} mm   "
                f"min={min(vals)} mm   max={max(vals)} mm"
            )
        elif len(vals) == 1:
            print(f"  {nombre}: solo 1 lectura valida ({vals[0]} mm) -- muy pocas para estadisticas")
        else:
            print(f"  {nombre}: 0 lecturas validas -- revisar status/timeout")


if __name__ == "__main__":
    main()
