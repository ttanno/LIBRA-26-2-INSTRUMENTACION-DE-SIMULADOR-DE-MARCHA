"""
Visor en tiempo real para los datos que imprime test_bno055.ino por Serial.

Uso:
    python visor_imu.py                  -> lista los puertos disponibles y pide elegir uno
    python visor_imu.py --port COM5
    python visor_imu.py --port COM5 --baud 115200

Botones:
    "Zero grafico (local)"   -> offset solo en este script (RAM), para ver el
                                grafico centrado en 0. NO se guarda en el ESP32:
                                se pierde al cerrar el visor o reiniciar el sensor.
    "Cero absoluto (flash)"  -> envia el comando 'z' al ESP32: promedia la
                                orientacion actual (manten el sensor quieto ~1 s)
                                y la guarda en la memoria flash (NVS) del ESP32
                                como cero persistente, que sobrevive apagar/
                                encender el sistema.
    "Borrar cero (flash)"    -> envia el comando 'c' al ESP32 para borrar el
                                cero absoluto guardado en flash.

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

LINE_RE = re.compile(
    r"Calib\[sys,gyro,accel,mag\]=(?P<sys>\d+),(?P<gyro>\d+),(?P<accel>\d+),(?P<mag>\d+)\s*\|\s*"
    r"Euler\[heading,roll,pitch\]=(?P<heading>-?\d+\.\d+),(?P<roll>-?\d+\.\d+),(?P<pitch>-?\d+\.\d+)\s*\|\s*"
    r"LinAccel\[x,y,z\]=(?P<ax>-?\d+\.\d+),(?P<ay>-?\d+\.\d+),(?P<az>-?\d+\.\d+)\s*\|\s*"
    r"Temp=(?P<temp>-?\d+)"
)

MAX_PUNTOS = 200  # cuantas muestras se muestran en los graficos (a 200 ms/muestra ~ 40 s de ventana)


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
        m = LINE_RE.search(linea)
        if m:
            cola.put(m.groupdict())
        elif linea:
            cola.put({"raw": linea})


def main():
    ap = argparse.ArgumentParser(description="Visor en tiempo real para IMU BNO055 (test_bno055.ino)")
    ap.add_argument("--port", help="Puerto serial (ej. COM5). Si se omite, se pide interactivamente.")
    ap.add_argument("--baud", type=int, default=115200, help="Baudrate (default 115200)")
    ap.add_argument(
        "--rango-euler", type=float, default=100.0,
        help="Rango +/- del eje Y para heading/roll/pitch en grados (default 100, para mas resolucion cerca de 90 grados)"
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
    heading_d, roll_d, pitch_d = (deque(maxlen=MAX_PUNTOS) for _ in range(3))
    ax_d, ay_d, az_d = (deque(maxlen=MAX_PUNTOS) for _ in range(3))

    # Estado mutable compartido entre la actualizacion del grafico y el boton de reset.
    estado = {
        "t0": time.time(),
        "offset_heading": 0.0,
        "offset_roll": 0.0,
        "offset_pitch": 0.0,
        "ultimo_raw": None,  # ultima lectura de heading/roll/pitch tal cual llego (sin offset)
    }

    fig, (ax_euler, ax_accel) = plt.subplots(2, 1, figsize=(9, 8), sharex=True)
    fig.subplots_adjust(bottom=0.15, top=0.78, hspace=0.1)
    fig.suptitle("BNO055 - esperando datos...", y=0.99)

    caja = dict(boxstyle="round", facecolor="black", edgecolor="0.6")
    txt_roll = fig.text(
        0.27, 0.88, "ROLL\n---.--°", fontsize=22, ha="center", va="center",
        family="monospace", color="orange", bbox=caja,
    )
    txt_pitch = fig.text(
        0.73, 0.88, "PITCH\n---.--°", fontsize=22, ha="center", va="center",
        family="monospace", color="lime", bbox=caja,
    )

    (l_heading,) = ax_euler.plot([], [], label="heading")
    (l_roll,) = ax_euler.plot([], [], label="roll")
    (l_pitch,) = ax_euler.plot([], [], label="pitch")
    ax_euler.set_ylabel("grados (relativo al ultimo reset)")
    ax_euler.set_ylim(-args.rango_euler, args.rango_euler)
    ax_euler.legend(loc="upper right")
    ax_euler.grid(True, alpha=0.3)

    (l_ax,) = ax_accel.plot([], [], label="ax")
    (l_ay,) = ax_accel.plot([], [], label="ay")
    (l_az,) = ax_accel.plot([], [], label="az")
    ax_accel.set_ylabel("m/s^2")
    ax_accel.set_xlabel("tiempo (s desde el ultimo reset)")
    ax_accel.set_ylim(-20, 20)
    ax_accel.legend(loc="upper right")
    ax_accel.grid(True, alpha=0.3)

    ax_boton = fig.add_axes([0.13, 0.02, 0.24, 0.05])
    boton_reset = Button(ax_boton, "Zero grafico (local)")

    ax_boton_flash = fig.add_axes([0.39, 0.02, 0.24, 0.05])
    boton_flash = Button(ax_boton_flash, "Cero absoluto (flash)")

    ax_boton_borrar = fig.add_axes([0.65, 0.02, 0.24, 0.05])
    boton_borrar = Button(ax_boton_borrar, "Borrar cero (flash)")

    def on_reset(_event):
        # Offset solo local (en RAM de este script): NO se guarda en el ESP32
        # ni sobrevive a reiniciar el visor o el sensor. Sirve nada mas para
        # ver el grafico centrado en 0 durante esta sesion.
        ultimo = estado["ultimo_raw"]
        if ultimo is not None:
            estado["offset_heading"] = ultimo["heading"]
            estado["offset_roll"] = ultimo["roll"]
            estado["offset_pitch"] = ultimo["pitch"]
        t.clear()
        heading_d.clear()
        roll_d.clear()
        pitch_d.clear()
        ax_d.clear()
        ay_d.clear()
        az_d.clear()
        estado["t0"] = time.time()

    def on_set_flash(_event):
        # Envia el comando 'z' que test_bno055.ino interpreta como: promediar
        # la orientacion actual y guardarla en la memoria flash (NVS) del
        # ESP32 como cero absoluto persistente (sobrevive apagar/encender).
        print(">> Enviando 'z' (establecer cero absoluto en flash)... manten el sensor quieto.")
        ser.write(b"z\n")

    def on_clear_flash(_event):
        print(">> Enviando 'c' (borrar cero absoluto guardado en flash)...")
        ser.write(b"c\n")

    boton_reset.on_clicked(on_reset)
    boton_flash.on_clicked(on_set_flash)
    boton_borrar.on_clicked(on_clear_flash)

    def actualizar(_frame):
        actualizado = False
        try:
            while True:
                dato = cola.get_nowait()
                if "raw" in dato:
                    # Linea que no matcheo el formato numerico esperado: mensajes de
                    # arranque o confirmaciones de los comandos z/c. Se muestran en consola.
                    print(dato["raw"])
                    continue

                heading = float(dato["heading"])
                roll = float(dato["roll"])
                pitch = float(dato["pitch"])
                estado["ultimo_raw"] = {"heading": heading, "roll": roll, "pitch": pitch}

                ahora = time.time() - estado["t0"]
                t.append(ahora)
                heading_d.append(heading - estado["offset_heading"])
                roll_d.append(roll - estado["offset_roll"])
                pitch_d.append(pitch - estado["offset_pitch"])
                ax_d.append(float(dato["ax"]))
                ay_d.append(float(dato["ay"]))
                az_d.append(float(dato["az"]))

                sys_c, gyro_c, accel_c, mag_c = dato["sys"], dato["gyro"], dato["accel"], dato["mag"]
                fig.suptitle(
                    f"Calib sys={sys_c} gyro={gyro_c} accel={accel_c} mag={mag_c}   |   "
                    f"Temp={dato['temp']} C"
                )
                actualizado = True
        except Empty:
            pass

        if actualizado:
            l_heading.set_data(t, heading_d)
            l_roll.set_data(t, roll_d)
            l_pitch.set_data(t, pitch_d)
            l_ax.set_data(t, ax_d)
            l_ay.set_data(t, ay_d)
            l_az.set_data(t, az_d)
            txt_roll.set_text(f"ROLL\n{roll_d[-1]:+.2f}°")
            txt_pitch.set_text(f"PITCH\n{pitch_d[-1]:+.2f}°")
            if t:
                ax_euler.set_xlim(max(0, t[0]), max(t[-1], t[0] + 1))
                ax_accel.set_xlim(max(0, t[0]), max(t[-1], t[0] + 1))

        return l_heading, l_roll, l_pitch, l_ax, l_ay, l_az

    anim = FuncAnimation(fig, actualizar, interval=100, cache_frame_data=False)

    try:
        plt.show()
    finally:
        detener.set()
        ser.close()


if __name__ == "__main__":
    main()
