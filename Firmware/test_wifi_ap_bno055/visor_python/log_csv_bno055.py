"""
Registro a CSV por cable (COM) del BNO055 -- sin graficos, pensado para
pruebas cortas (ej. "dejar el sensor quieto") y analizar despues en
Excel/pandas. Funciona con cualquiera de los sketches de WiFi ya cargados
(AP o STA), porque ambos imprimen la misma linea por Serial. No hace falta
tocar el sketch ni el WiFi para usar esto -- es exactamente lo mismo que
lee visor_serial_bno055.py, pero en vez de graficar, guarda a un archivo.

Uso:
    python log_csv_bno055.py --port COM7
    python log_csv_bno055.py --port COM7 --duracion 30
    python log_csv_bno055.py --port COM7 --duracion 30 --salida quieto1.csv

Para grabar varias veces seguidas sin tener que volver a escribir el
comando cada vez (util para juntar mas datos / repetir en distintas
posiciones):
    python log_csv_bno055.py --port COM7 --duracion 30 --repeticiones 5

Con --repeticiones > 1, el script pausa entre cada grabacion y te deja
reacomodar el sensor (o dejarlo igual, para ver que tan repetible es) --
presiona Enter cuando estes listo para la siguiente. Cada repeticion se
guarda en su propio archivo (bno055_<fecha>_<hora>_repNdeM.csv) y al final
se imprime una tabla comparando el ruido (desviacion estandar) de todas
las repeticiones juntas.

Si en vez de pausa manual (Enter) quieres que la pausa entre repeticiones
sea automatica de N segundos (util para dejar el sensor quieto en la misma
posicion y correr todo sin intervencion), usa --pausa:
    python log_csv_bno055.py --port COM7 --duracion 30 --repeticiones 10 --pausa 30

Si no se indica --duracion, cada grabacion registra hasta que presiones
Ctrl+C (con --repeticiones > 1 y sin --duracion, Ctrl+C solo corta la
grabacion actual y pasa a la pausa de la siguiente).

Por defecto, ANTES de cada grabacion, borra el "cero absoluto" guardado
en la flash del ESP32 (el mismo que se guarda con el boton "Cero absoluto
(flash)" o el comando 'z') -- asi cada prueba arranca limpia, sin un cero
de una prueba anterior de por medio. Si por algun motivo no quieres que
lo borre, usa --sin-borrar-cero.

Al terminar cada grabacion, imprime promedio y desviacion estandar de
heading/roll/pitch y de la aceleracion lineal (ax, ay, az) -- justo lo que
hace falta para la prueba de "dejarlo quieto": mientras mas chica la
desviacion estandar, mas estable/menos ruidoso es el sensor en esa
condicion.

Requiere: pip install -r requirements.txt (ya incluye pyserial)
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
    r"LinAccel\[x,y,z\]=(?P<ax>-?\d+\.\d+),(?P<ay>-?\d+\.\d+),(?P<az>-?\d+\.\d+)"
)

COLUMNAS = [
    "t_s", "calib_sys", "calib_gyro", "calib_accel", "calib_mag",
    "heading", "roll", "pitch", "ax", "ay", "az",
]


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


def borrar_cero(ser: serial.Serial):
    print("Borrando el cero absoluto guardado en flash (comando 'c') antes de grabar...")
    ser.write(b"c\n")
    time.sleep(1.5)
    while ser.in_waiting:
        resp = ser.readline().decode("utf-8", errors="replace").strip()
        if resp:
            print(f"  ESP32: {resp}")


def grabar_una_vez(ser: serial.Serial, nombre_salida: str, duracion):
    """Graba una sola sesion a un CSV. Devuelve un dict con las listas de
    valores registrados (para el resumen final) y la cantidad de filas."""
    heading_vals, roll_vals, pitch_vals = [], [], []
    ax_vals, ay_vals, az_vals = [], [], []

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
                    continue

                d = m.groupdict()
                t = time.time() - t0
                heading, roll, pitch = float(d["heading"]), float(d["roll"]), float(d["pitch"])
                ax, ay, az = float(d["ax"]), float(d["ay"]), float(d["az"])

                writer.writerow([
                    f"{t:.3f}", d["sys"], d["gyro"], d["accel"], d["mag"],
                    heading, roll, pitch, ax, ay, az,
                ])
                filas += 1

                heading_vals.append(heading)
                roll_vals.append(roll)
                pitch_vals.append(pitch)
                ax_vals.append(ax)
                ay_vals.append(ay)
                az_vals.append(az)

                if filas % 20 == 0:
                    print(f"  {filas} filas registradas... (t={t:.1f}s)", end="\r")

    except KeyboardInterrupt:
        print("\nGrabacion detenida por el usuario.")

    print(f"\nListo. {filas} filas guardadas en '{nombre_salida}'.")

    resultado = {
        "archivo": nombre_salida,
        "filas": filas,
        "heading": heading_vals, "roll": roll_vals, "pitch": pitch_vals,
        "ax": ax_vals, "ay": ay_vals, "az": az_vals,
    }

    if filas >= 2:
        def resumen(nombre, valores):
            return (
                f"  {nombre}: promedio={statistics.mean(valores):+.4f}  "
                f"desv.estandar={statistics.pstdev(valores):.4f}"
            )

        print("Resumen (util para la prueba de 'dejarlo quieto' -- cuanto ruido tiene el sensor):")
        print(resumen("heading", heading_vals))
        print(resumen("roll   ", roll_vals))
        print(resumen("pitch  ", pitch_vals))
        print(resumen("ax     ", ax_vals))
        print(resumen("ay     ", ay_vals))
        print(resumen("az     ", az_vals))
    else:
        print("Muy pocas filas para calcular estadisticas -- revisa que el sensor este enviando datos.")

    return resultado


def todos_en_cero(resultado) -> bool:
    """True si la repeticion tiene datos pero todos los valores son 0.0
    (senal de que el BNO055 no se detecto bien al arrancar)."""
    if resultado["filas"] < 1:
        return False
    campos = ("heading", "roll", "pitch", "ax", "ay", "az")
    return all(v == 0.0 for campo in campos for v in resultado[campo])


def main():
    ap = argparse.ArgumentParser(description="Registro a CSV del BNO055 por cable (COM)")
    ap.add_argument("--port", help="Puerto serial (ej. COM7). Si se omite, se pide interactivamente.")
    ap.add_argument("--baud", type=int, default=115200, help="Baudrate (default 115200)")
    ap.add_argument(
        "--duracion", type=float, default=None,
        help="Segundos a registrar por repeticion. Si se omite, cada una registra hasta Ctrl+C.",
    )
    ap.add_argument(
        "--salida", default=None,
        help="Nombre base del archivo CSV de salida (default: bno055_YYYYMMDD_HHMMSS.csv)",
    )
    ap.add_argument(
        "--repeticiones", type=int, default=1,
        help="Cuantas grabaciones seguidas hacer (con pausa entre cada una para reacomodar el sensor). Default 1.",
    )
    ap.add_argument(
        "--sin-borrar-cero", action="store_true",
        help="No borrar el cero absoluto guardado en flash antes de cada grabacion (por defecto SI se borra).",
    )
    ap.add_argument(
        "--pausa", type=float, default=None,
        help="Segundos de pausa automatica entre repeticiones (sin esperar Enter). Si se omite, se espera Enter.",
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

    base = args.salida or time.strftime("bno055_%Y%m%d_%H%M%S")
    if base.lower().endswith(".csv"):
        base = base[:-4]

    resultados = []

    try:
        for i in range(1, args.repeticiones + 1):
            if args.repeticiones > 1:
                print(f"\n=== Repeticion {i} de {args.repeticiones} ===")
                if i > 1 and args.pausa is not None:
                    print(f"Pausa automatica de {args.pausa:.0f} s antes de la siguiente grabacion...")
                    time.sleep(args.pausa)
                elif args.pausa is None:
                    input("Acomoda el sensor (mismo lugar u otro) y presiona Enter para empezar a grabar...")
                nombre_salida = f"{base}_rep{i}de{args.repeticiones}.csv"
            else:
                nombre_salida = f"{base}.csv"

            if not args.sin_borrar_cero:
                borrar_cero(ser)

            resultado = grabar_una_vez(ser, nombre_salida, args.duracion)
            resultados.append(resultado)

            if i == 1 and args.repeticiones > 1 and todos_en_cero(resultado):
                print(
                    "\nATENCION: la repeticion 1 registro todos los valores en 0.0 "
                    "-- el BNO055 puede no haberse detectado bien al arrancar."
                )
                resp = input(
                    "¿Deseas continuar con las siguientes repeticiones de todas formas? (s/n): "
                ).strip().lower()
                if resp != "s":
                    print("Deteniendo antes de las siguientes repeticiones.")
                    break
    finally:
        ser.close()

    if len(resultados) > 1:
        print("\n=== Resumen de todas las repeticiones (comparar repetibilidad) ===")
        print(f"{'archivo':40s} {'filas':>6s} {'roll std':>10s} {'pitch std':>10s} {'ax std':>8s} {'ay std':>8s} {'az std':>8s}")
        for r in resultados:
            if r["filas"] < 2:
                print(f"{r['archivo']:40s} {r['filas']:6d}   (muy pocas filas)")
                continue
            print(
                f"{r['archivo']:40s} {r['filas']:6d} "
                f"{statistics.pstdev(r['roll']):10.4f} "
                f"{statistics.pstdev(r['pitch']):10.4f} "
                f"{statistics.pstdev(r['ax']):8.4f} "
                f"{statistics.pstdev(r['ay']):8.4f} "
                f"{statistics.pstdev(r['az']):8.4f}"
            )
        print("\nSi la desviacion estandar sale parecida entre repeticiones, el sensor es repetible/estable.")
        print("Si varia mucho de una repeticion a otra, puede ser calibracion inconsistente o vibracion externa.")


if __name__ == "__main__":
    main()
