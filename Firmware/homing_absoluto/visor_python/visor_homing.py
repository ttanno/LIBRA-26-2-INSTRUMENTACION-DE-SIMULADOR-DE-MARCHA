"""
Visor + control en tiempo real para homing_absoluto.ino.

A diferencia de los otros visores (visor_imu.py, visor_mpu6050.py), aca el
boton "Zero/Reset" NO es solo un offset visual -- envia de verdad el
comando 'z' por Serial, que le pide al ESP32 que promedie el angulo actual
del acelerometro y lo guarde en su memoria flash (persistente entre
reinicios). Es decir: el boton dispara el mismo homing fisico que harias
escribiendo 'z' a mano en el Monitor Serie de Arduino.

Uso:
    python visor_homing.py                  -> lista los puertos disponibles y pide elegir uno
    python visor_homing.py --port COM5
    python visor_homing.py --port COM5 --baud 115200

Botones:
    "Establecer cero (z)"  -> manda 'z' -> el ESP32 promedia ~1 s del
                               acelerometro y guarda ese angulo como cero
                               absoluto en flash. MANTEN EL PIVOTE QUIETO
                               en la posicion de referencia antes de pulsarlo.
    "Borrar cero (c)"      -> manda 'c' -> borra el cero guardado en flash.

Requiere: pip install -r requirements.txt
"""

import argparse
import re
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

# Formato esperado (ver homing_absoluto.ino): roll,pitch,roll_abs,pitch_abs,zero_set
LINE_RE = re.compile(
    r"^(?P<roll>-?\d+\.\d+),(?P<pitch>-?\d+\.\d+),"
    r"(?P<roll_abs>-?\d+\.\d+),(?P<pitch_abs>-?\d+\.\d+),"
    r"(?P<zero_set>[01])$"
)

MAX_PUNTOS = 200  # ~50 Hz de muestreo en el sketch -> ~4 s de ventana


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


def hilo_lectura_serial(ser: serial.Serial, cola: Queue, detener: threading.Event):
    while not detener.is_set():
        try:
            linea = ser.readline().decode("utf-8", errors="replace").strip()
        except serial.SerialException:
            break
        if not linea:
            continue
        m = LINE_RE.match(linea)
        if m:
            cola.put(m.groupdict())
        else:
            # Mensajes de arranque/calibracion/homing del ESP32 (no son datos CSV) -- se muestran por consola.
            print(f"[ESP32] {linea}")


def main():
    ap = argparse.ArgumentParser(description="Visor + control para homing_absoluto.ino")
    ap.add_argument("--port", help="Puerto serial (ej. COM5). Si se omite, se pide interactivamente.")
    ap.add_argument("--baud", type=int, default=115200, help="Baudrate (default 115200)")
    ap.add_argument(
        "--rango-angulo", type=float, default=100.0,
        help="Rango +/- del eje Y en grados (default 100)"
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
    roll_d, pitch_d = (deque(maxlen=MAX_PUNTOS) for _ in range(2))
    roll_abs_d, pitch_abs_d = (deque(maxlen=MAX_PUNTOS) for _ in range(2))

    estado = {"t0": time.time(), "zero_set": False}

    fig, (ax_abs, ax_raw) = plt.subplots(2, 1, figsize=(9, 8), sharex=True)
    fig.subplots_adjust(bottom=0.2, top=0.8, hspace=0.15)
    fig.suptitle("Homing absoluto - esperando datos...", y=0.99)

    caja = dict(boxstyle="round", facecolor="black", edgecolor="0.6")
    txt_roll_abs = fig.text(
        0.27, 0.88, "ROLL_ABS\n---.--°", fontsize=18, ha="center", va="center",
        family="monospace", color="orange", bbox=caja,
    )
    txt_pitch_abs = fig.text(
        0.73, 0.88, "PITCH_ABS\n---.--°", fontsize=18, ha="center", va="center",
        family="monospace", color="lime", bbox=caja,
    )

    (l_roll_abs,) = ax_abs.plot([], [], label="roll_abs (rel. al cero guardado)")
    (l_pitch_abs,) = ax_abs.plot([], [], label="pitch_abs (rel. al cero guardado)")
    ax_abs.axhline(0, color="gray", linewidth=1, linestyle=":")
    ax_abs.set_ylabel("grados (cero absoluto)")
    ax_abs.set_ylim(-args.rango_angulo, args.rango_angulo)
    ax_abs.legend(loc="upper right", fontsize=8)
    ax_abs.grid(True, alpha=0.3)

    (l_roll,) = ax_raw.plot([], [], "--", label="roll (crudo del filtro)", alpha=0.6)
    (l_pitch,) = ax_raw.plot([], [], "--", label="pitch (crudo del filtro)", alpha=0.6)
    ax_raw.set_ylabel("grados (crudo)")
    ax_raw.set_xlabel("tiempo (s)")
    ax_raw.set_ylim(-180, 180)
    ax_raw.legend(loc="upper right", fontsize=8)
    ax_raw.grid(True, alpha=0.3)

    ax_boton_z = fig.add_axes([0.15, 0.03, 0.32, 0.06])
    boton_z = Button(ax_boton_z, "Establecer cero (z)")

    ax_boton_c = fig.add_axes([0.53, 0.03, 0.32, 0.06])
    boton_c = Button(ax_boton_c, "Borrar cero (c)")

    def on_zero(_event):
        print(">> Enviando 'z' (establecer cero) -- manten el pivote quieto en la posicion de referencia...")
        ser.write(b"z")

    def on_clear(_event):
        print(">> Enviando 'c' (borrar cero)...")
        ser.write(b"c")

    boton_z.on_clicked(on_zero)
    boton_c.on_clicked(on_clear)

    def actualizar(_frame):
        actualizado = False
        try:
            while True:
                dato = cola.get_nowait()
                ahora = time.time() - estado["t0"]
                t.append(ahora)
                roll_d.append(float(dato["roll"]))
                pitch_d.append(float(dato["pitch"]))
                roll_abs_d.append(float(dato["roll_abs"]))
                pitch_abs_d.append(float(dato["pitch_abs"]))
                estado["zero_set"] = dato["zero_set"] == "1"
                actualizado = True
        except Empty:
            pass

        if actualizado:
            l_roll_abs.set_data(t, roll_abs_d)
            l_pitch_abs.set_data(t, pitch_abs_d)
            l_roll.set_data(t, roll_d)
            l_pitch.set_data(t, pitch_d)
            txt_roll_abs.set_text(f"ROLL_ABS\n{roll_abs_d[-1]:+.2f}°")
            txt_pitch_abs.set_text(f"PITCH_ABS\n{pitch_abs_d[-1]:+.2f}°")

            estado_txt = "CERO ABSOLUTO: SI (guardado en flash)" if estado["zero_set"] else "CERO ABSOLUTO: NO establecido aun"
            fig.suptitle(f"Homing absoluto (MPU6050)   |   {estado_txt}")

            if t:
                ax_abs.set_xlim(max(0, t[0]), max(t[-1], t[0] + 1))
                ax_raw.set_xlim(max(0, t[0]), max(t[-1], t[0] + 1))

        return l_roll_abs, l_pitch_abs, l_roll, l_pitch

    anim = FuncAnimation(fig, actualizar, interval=100, cache_frame_data=False)

    try:
        plt.show()
    finally:
        detener.set()
        ser.close()


if __name__ == "__main__":
    main()
