"""
Registro a CSV por cable (COM) de la celda de carga (test_hx711.ino) --
sin graficos, pensado para juntar datos de una sesion de pesaje y
analizarlos despues en Excel/pandas. Mismo patron que log_csv_ads1256.py,
adaptado al formato de salida del HX711 (sin columna voltage_V, ver
test_hx711.ino).

Uso:
    python log_csv_hx711.py --port COM7
    python log_csv_hx711.py --port COM7 --duracion 30
    python log_csv_hx711.py --port COM7 --duracion 30 --salida prueba1.csv

Para grabar varias veces seguidas sin reescribir el comando cada vez (util
para repetir la prueba con distintos pesos):
    python log_csv_hx711.py --port COM7 --duracion 15 --repeticiones 5

Con --repeticiones > 1, el script pausa entre cada grabacion para que
cambies el peso sobre la celda -- presiona Enter cuando estes listo para
la siguiente. Cada repeticion se guarda en su propio archivo
(hx711_<fecha>_<hora>_repNdeM.csv) y al final se imprime una tabla
comparando el promedio y la desviacion estandar de la fuerza de cada una
(util para ver que tan repetible/ruidosa es la medicion con cada peso).

Si no se indica --duracion, cada grabacion registra hasta que presiones
Ctrl+C (con --repeticiones > 1 y sin --duracion, Ctrl+C solo corta la
grabacion actual y pasa a la pausa de la siguiente).

Este script NO tara ni calibra por vos -- antes de grabar, asegurate de
haber hecho 't' y 'k<masa>' en el Monitor Serie (o en visor_hx711.py) al
menos una vez, porque el ESP32 ya se acuerda de esa calibracion (queda en
flash). Si arranca a grabar y ve que todavia no esta calibrado
(columna "calibrated"=0), avisa por consola pero igual registra los datos
crudos (raw_code sigue siendo valido aunque force_N no lo sea).

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
    r"(?P<raw_code>-?\d+),"
    r"(?P<force_N>-?\d+\.\d+),"
    r"(?P<tared>[01]),"
    r"(?P<calibrated>[01])"
)

COLUMNAS = ["t_s", "raw_code", "force_N", "tared", "calibrated"]


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


def grabar_una_vez(ser: serial.Serial, nombre_salida: str, duracion):
    """Graba una sola sesion a un CSV. Devuelve un dict con la lista de
    fuerzas registradas (para el resumen final) y la cantidad de filas."""
    force_vals = []
    aviso_no_calibrado_mostrado = False

    t0 = time.time()
    filas = 0

    print(f"Registrando en '{nombre_salida}'.")
    if duracion:
        print(f"Se detendra automaticamente en {duracion:.0f} s. (Ctrl+C para detener antes)")
    else:
        print("Presiona Ctrl+C para detener el registro.")

    try:
        with open(nombre_salida, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(COLUMNAS)

            while True:
                if duracion is not None and (time.time() - t0) >= duracion:
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
                    continue  # mensajes de arranque, confirmaciones de tara/calibracion, errores de timeout, etc.

                d = m.groupdict()

                if d["calibrated"] == "0" and not aviso_no_calibrado_mostrado:
                    print(
                        "  AVISO: 'calibrated=0' -- todavia no se hizo 't'+'k<masa>' en este ESP32. "
                        "Se sigue registrando raw_code, pero force_N no es valido."
                    )
                    aviso_no_calibrado_mostrado = True

                t = time.time() - t0
                force_n = float(d["force_N"])

                writer.writerow([
                    f"{t:.3f}", d["raw_code"], force_n,
                    d["tared"], d["calibrated"],
                ])
                filas += 1
                force_vals.append(force_n)

                if filas % 10 == 0:
                    print(f"  {filas} filas registradas... (t={t:.1f}s, fuerza actual={force_n:+.3f} N)", end="\r")

    except KeyboardInterrupt:
        print("\nGrabacion detenida por el usuario.")

    print(f"\nListo. {filas} filas guardadas en '{nombre_salida}'.")

    resultado = {"archivo": nombre_salida, "filas": filas, "force_N": force_vals}

    if filas >= 2:
        print(
            f"  Resumen: promedio={statistics.mean(force_vals):+.4f} N   "
            f"desv.estandar={statistics.pstdev(force_vals):.4f} N"
        )
    else:
        print("Muy pocas filas para calcular estadisticas -- revisa que el HX711 este enviando datos.")

    return resultado


def main():
    ap = argparse.ArgumentParser(description="Registro a CSV de la celda de carga (test_hx711.ino) por cable (COM)")
    ap.add_argument("--port", help="Puerto serial (ej. COM7). Si se omite, se pide interactivamente.")
    ap.add_argument("--baud", type=int, default=115200, help="Baudrate (default 115200)")
    ap.add_argument(
        "--duracion", type=float, default=None,
        help="Segundos a registrar por repeticion. Si se omite, cada una registra hasta Ctrl+C.",
    )
    ap.add_argument(
        "--salida", default=None,
        help="Nombre base del archivo CSV de salida (default: hx711_YYYYMMDD_HHMMSS.csv)",
    )
    ap.add_argument(
        "--repeticiones", type=int, default=1,
        help="Cuantas grabaciones seguidas hacer (con pausa entre cada una para cambiar el peso). Default 1.",
    )
    args = ap.parse_args()

    puerto = args.port or elegir_puerto()

    try:
        ser = serial.Serial(puerto, args.baud, timeout=1)
    except serial.SerialException as e:
        print(f"No se pudo abrir {puerto}: {e}")
        sys.exit(1)

    time.sleep(2)  # dar tiempo a que el puerto se estabilice tras abrirlo
    print(f"Conectado a {puerto} @ {args.baud} baudios.")

    base = args.salida or time.strftime("hx711_%Y%m%d_%H%M%S")
    if base.lower().endswith(".csv"):
        base = base[:-4]

    resultados = []

    try:
        for i in range(1, args.repeticiones + 1):
            if args.repeticiones > 1:
                print(f"\n=== Repeticion {i} de {args.repeticiones} ===")
                input("Acomoda el peso sobre la celda y presiona Enter para empezar a grabar...")
                nombre_salida = f"{base}_rep{i}de{args.repeticiones}.csv"
            else:
                nombre_salida = f"{base}.csv"

            resultado = grabar_una_vez(ser, nombre_salida, args.duracion)
            resultados.append(resultado)
    finally:
        ser.close()

    if len(resultados) > 1:
        print("\n=== Resumen de todas las repeticiones ===")
        print(f"{'archivo':40s} {'filas':>6s} {'fuerza prom (N)':>16s} {'fuerza std (N)':>15s}")
        for r in resultados:
            if r["filas"] < 2:
                print(f"{r['archivo']:40s} {r['filas']:6d}   (muy pocas filas)")
                continue
            print(
                f"{r['archivo']:40s} {r['filas']:6d} "
                f"{statistics.mean(r['force_N']):16.4f} "
                f"{statistics.pstdev(r['force_N']):15.4f}"
            )


if __name__ == "__main__":
    main()
