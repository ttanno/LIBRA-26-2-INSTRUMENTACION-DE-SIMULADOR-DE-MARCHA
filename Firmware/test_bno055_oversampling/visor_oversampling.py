"""
Visor en tiempo real para test_bno055_oversampling.ino.

Grafica raw_* (crudo, una muestra) contra avg_* (promedio de N muestras) para
roll y pitch, permitiendo ver visualmente la reduccion de ruido. Tambien
muestra un display numerico grande con el ultimo valor promediado.

Formato de linea esperado (CSV, la primera linea con encabezado se ignora):
    raw_heading,raw_roll,raw_pitch,avg_heading,avg_roll,avg_pitch,n,sys,gyro,accel,mag

Uso:
    python visor_oversampling.py --port COM7
    python visor_oversampling.py --port COM7 --baud 115200 --rango-euler 90

Requiere: pip install -r ../visor_python/requirements.txt   (pyserial, matplotlib)
"""

import argparse
import sys
import threading
import time
from collections import deque
from queue import Queue, Empty

import serial
import serial.tools.list_ports
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Button

MAX_PUNTOS = 200
CAMPOS = ["raw_heading", "raw_roll", "raw_pitch", "avg_heading", "avg_roll", "avg_pitch",
          "n", "sys", "gyro", "accel", "mag"]


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


def parsear_linea(linea: str):
    partes = linea.split(",")
    if len(partes) != len(CAMPOS):
        return None
    try:
        valores = [float(x) for x in partes]
    except ValueError:
        return None  # linea de arranque / encabezado, no CSV numerico
    return dict(zip(CAMPOS, valores))


def hilo_lectura_serial(ser: serial.Serial, cola: Queue, detener: threading.Event):
    while not detener.is_set():
        try:
            linea = ser.readline().decode("utf-8", errors="replace").strip()
        except serial.SerialException:
            break
        if not linea:
            continue
        dato = parsear_linea(linea)
        if dato is not None:
            cola.put(dato)


def main():
    ap = argparse.ArgumentParser(description="Visor raw vs. promediado para test_bno055_oversampling.ino")
    ap.add_argument("--port", help="Puerto serial (ej. COM7). Si se omite, se pide interactivamente.")
    ap.add_argument("--baud", type=int, default=115200, help="Baudrate (default 115200)")
    ap.add_argument(
        "--rango-euler", type=float, default=100.0,
        help="Rango +/- del eje Y para roll/pitch en grados (default 100)"
    )
    args = ap.parse_args()

    puerto = args.port or elegir_puerto()

    try:
        ser = serial.Serial(puerto, args.baud, timeout=1)
    except serial.SerialException as e:
        print(f"No se pudo abrir {puerto}: {e}")
        sys.exit(1)

    print(f"Conectado a {puerto} @ {args.baud} baudios. Cierra la ventana del grafico para salir.")

    cola: Queue = Queue()
    detener = threading.Event()
    hilo = threading.Thread(target=hilo_lectura_serial, args=(ser, cola, detener), daemon=True)
    hilo.start()

    t = deque(maxlen=MAX_PUNTOS)
    raw_roll_d, avg_roll_d = deque(maxlen=MAX_PUNTOS), deque(maxlen=MAX_PUNTOS)
    raw_pitch_d, avg_pitch_d = deque(maxlen=MAX_PUNTOS), deque(maxlen=MAX_PUNTOS)

    estado = {
        "t0": time.time(),
        "offset_roll": 0.0,
        "offset_pitch": 0.0,
        "ultimo_raw": None,  # ultimo dato tal cual llego (avg_roll/avg_pitch sin offset), para el boton reset
    }

    fig, (ax_roll, ax_pitch) = plt.subplots(2, 1, figsize=(9, 8), sharex=True)
    fig.subplots_adjust(bottom=0.15, top=0.78, hspace=0.15)
    fig.suptitle("BNO055 oversampling - esperando datos...", y=0.99)

    caja = dict(boxstyle="round", facecolor="black", edgecolor="0.6")
    txt_roll = fig.text(
        0.27, 0.88, "ROLL (avg)\n---.--°", fontsize=20, ha="center", va="center",
        family="monospace", color="orange", bbox=caja,
    )
    txt_pitch = fig.text(
        0.73, 0.88, "PITCH (avg)\n---.--°", fontsize=20, ha="center", va="center",
        family="monospace", color="lime", bbox=caja,
    )

    (l_raw_roll,) = ax_roll.plot([], [], label="raw_roll", alpha=0.35, linewidth=1)
    (l_avg_roll,) = ax_roll.plot([], [], label="avg_roll", linewidth=2)
    ax_roll.set_ylabel("roll (grados)")
    ax_roll.set_ylim(-args.rango_euler, args.rango_euler)
    ax_roll.legend(loc="upper right")
    ax_roll.grid(True, alpha=0.3)

    (l_raw_pitch,) = ax_pitch.plot([], [], label="raw_pitch", alpha=0.35, linewidth=1)
    (l_avg_pitch,) = ax_pitch.plot([], [], label="avg_pitch", linewidth=2)
    ax_pitch.set_ylabel("pitch (grados)")
    ax_pitch.set_xlabel("tiempo (s desde el ultimo reset)")
    ax_pitch.set_ylim(-args.rango_euler, args.rango_euler)
    ax_pitch.legend(loc="upper right")
    ax_pitch.grid(True, alpha=0.3)

    ax_boton = fig.add_axes([0.4, 0.02, 0.2, 0.05])
    boton_reset = Button(ax_boton, "Zero / Reset")

    def on_reset(_event):
        ultimo = estado["ultimo_raw"]
        if ultimo is not None:
            estado["offset_roll"] = ultimo["avg_roll"]
            estado["offset_pitch"] = ultimo["avg_pitch"]
        t.clear()
        raw_roll_d.clear()
        avg_roll_d.clear()
        raw_pitch_d.clear()
        avg_pitch_d.clear()
        estado["t0"] = time.time()

    boton_reset.on_clicked(on_reset)

    def actualizar(_frame):
        actualizado = False
        try:
            while True:
                dato = cola.get_nowait()
                estado["ultimo_raw"] = dato

                ahora = time.time() - estado["t0"]
                t.append(ahora)
                raw_roll_d.append(dato["raw_roll"] - estado["offset_roll"])
                avg_roll_d.append(dato["avg_roll"] - estado["offset_roll"])
                raw_pitch_d.append(dato["raw_pitch"] - estado["offset_pitch"])
                avg_pitch_d.append(dato["avg_pitch"] - estado["offset_pitch"])

                fig.suptitle(
                    f"Calib sys={int(dato['sys'])} gyro={int(dato['gyro'])} "
                    f"accel={int(dato['accel'])} mag={int(dato['mag'])}   |   n={int(dato['n'])} muestras/bloque"
                )
                actualizado = True
        except Empty:
            pass

        if actualizado:
            l_raw_roll.set_data(t, raw_roll_d)
            l_avg_roll.set_data(t, avg_roll_d)
            l_raw_pitch.set_data(t, raw_pitch_d)
            l_avg_pitch.set_data(t, avg_pitch_d)
            txt_roll.set_text(f"ROLL (avg)\n{avg_roll_d[-1]:+.2f}°")
            txt_pitch.set_text(f"PITCH (avg)\n{avg_pitch_d[-1]:+.2f}°")
            if t:
                ax_roll.set_xlim(max(0, t[0]), max(t[-1], t[0] + 1))
                ax_pitch.set_xlim(max(0, t[0]), max(t[-1], t[0] + 1))

        return l_raw_roll, l_avg_roll, l_raw_pitch, l_avg_pitch

    anim = FuncAnimation(fig, actualizar, interval=100, cache_frame_data=False)

    try:
        plt.show()
    finally:
        detener.set()
        ser.close()


if __name__ == "__main__":
    main()
