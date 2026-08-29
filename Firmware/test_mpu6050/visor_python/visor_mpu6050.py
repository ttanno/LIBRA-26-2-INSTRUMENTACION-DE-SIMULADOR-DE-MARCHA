"""
Visor en tiempo real para los datos que imprime test_mpu6050.ino por Serial.

A diferencia de visor_imu.py (BNO055), aca no hay heading absoluto ni estado
de calibracion -- en su lugar se grafica "yaw_solo_giro", que es la
integracion pura del giroscopio SIN corregir. Es normal (y esperado) verlo
alejarse de 0 con el tiempo aunque el sensor este quieto: eso es el drift.
roll/pitch si estan corregidos por el filtro complementario del sketch.

Uso:
    python visor_mpu6050.py                  -> lista los puertos disponibles y pide elegir uno
    python visor_mpu6050.py --port COM5
    python visor_mpu6050.py --port COM5 --baud 115200

Boton "Zero / Reset": toma la ultima lectura de roll/pitch/yaw_solo_giro
como nuevo origen (0,0,0) SOLO para la vista (offset visual) y limpia los
graficos -- no reinicia el drift acumulado real dentro del ESP32, que sigue
corriendo en el sketch.

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
    r"(?P<ax>-?\d+\.\d+),(?P<ay>-?\d+\.\d+),(?P<az>-?\d+\.\d+),"
    r"(?P<gx>-?\d+\.\d+),(?P<gy>-?\d+\.\d+),(?P<gz>-?\d+\.\d+),"
    r"(?P<roll>-?\d+\.\d+),(?P<pitch>-?\d+\.\d+),(?P<yaw>-?\d+\.\d+),"
    r"(?P<temp>-?\d+\.\d+)"
)

MAX_PUNTOS = 200  # cuantas muestras se muestran en los graficos (a ~20 ms/muestra ~ 4 s de ventana... ver nota abajo)
# El sketch manda datos a ~50 Hz (delay(20) en el .ino), asi que 200 puntos ~ 4 s de ventana.
# Si quieres ver mas historial, sube MAX_PUNTOS (consume mas memoria/CPU de graficado).


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
    ap = argparse.ArgumentParser(description="Visor en tiempo real para IMU MPU6050 (test_mpu6050.ino)")
    ap.add_argument("--port", help="Puerto serial (ej. COM5). Si se omite, se pide interactivamente.")
    ap.add_argument("--baud", type=int, default=115200, help="Baudrate (default 115200)")
    ap.add_argument(
        "--rango-angulo", type=float, default=100.0,
        help="Rango +/- del eje Y para roll/pitch/yaw en grados (default 100)"
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
    roll_d, pitch_d, yaw_d = (deque(maxlen=MAX_PUNTOS) for _ in range(3))
    ax_d, ay_d, az_d = (deque(maxlen=MAX_PUNTOS) for _ in range(3))
    gx_d, gy_d, gz_d = (deque(maxlen=MAX_PUNTOS) for _ in range(3))

    # Estado mutable compartido entre la actualizacion del grafico y el boton de reset.
    estado = {
        "t0": time.time(),
        "offset_roll": 0.0,
        "offset_pitch": 0.0,
        "offset_yaw": 0.0,
        "ultimo_raw": None,  # ultima lectura de roll/pitch/yaw tal cual llego (sin offset)
    }

    fig, (ax_ang, ax_accel, ax_gyro) = plt.subplots(3, 1, figsize=(9, 9), sharex=True)
    fig.subplots_adjust(bottom=0.13, top=0.82, hspace=0.15)
    fig.suptitle("MPU6050 - esperando datos...", y=0.99)

    caja = dict(boxstyle="round", facecolor="black", edgecolor="0.6")
    txt_roll = fig.text(
        0.27, 0.90, "ROLL\n---.--°", fontsize=20, ha="center", va="center",
        family="monospace", color="orange", bbox=caja,
    )
    txt_pitch = fig.text(
        0.73, 0.90, "PITCH\n---.--°", fontsize=20, ha="center", va="center",
        family="monospace", color="lime", bbox=caja,
    )

    (l_roll,) = ax_ang.plot([], [], label="roll (filtrado)")
    (l_pitch,) = ax_ang.plot([], [], label="pitch (filtrado)")
    (l_yaw,) = ax_ang.plot([], [], "--", label="yaw (solo giro, DERIVA)", color="red")
    ax_ang.set_ylabel("grados (relativo al ultimo reset)")
    ax_ang.set_ylim(-args.rango_angulo, args.rango_angulo)
    ax_ang.legend(loc="upper right", fontsize=8)
    ax_ang.grid(True, alpha=0.3)

    (l_ax,) = ax_accel.plot([], [], label="ax")
    (l_ay,) = ax_accel.plot([], [], label="ay")
    (l_az,) = ax_accel.plot([], [], label="az")
    ax_accel.set_ylabel("accel (m/s^2)")
    ax_accel.set_ylim(-20, 20)
    ax_accel.legend(loc="upper right", fontsize=8)
    ax_accel.grid(True, alpha=0.3)

    (l_gx,) = ax_gyro.plot([], [], label="gx")
    (l_gy,) = ax_gyro.plot([], [], label="gy")
    (l_gz,) = ax_gyro.plot([], [], label="gz")
    ax_gyro.set_ylabel("giro (rad/s)")
    ax_gyro.set_xlabel("tiempo (s desde el ultimo reset)")
    ax_gyro.set_ylim(-2, 2)
    ax_gyro.legend(loc="upper right", fontsize=8)
    ax_gyro.grid(True, alpha=0.3)

    ax_boton = fig.add_axes([0.4, 0.01, 0.2, 0.045])
    boton_reset = Button(ax_boton, "Zero / Reset (solo vista)")

    def on_reset(_event):
        ultimo = estado["ultimo_raw"]
        if ultimo is not None:
            estado["offset_roll"] = ultimo["roll"]
            estado["offset_pitch"] = ultimo["pitch"]
            estado["offset_yaw"] = ultimo["yaw"]
        t.clear()
        roll_d.clear(); pitch_d.clear(); yaw_d.clear()
        ax_d.clear(); ay_d.clear(); az_d.clear()
        gx_d.clear(); gy_d.clear(); gz_d.clear()
        estado["t0"] = time.time()

    boton_reset.on_clicked(on_reset)

    def actualizar(_frame):
        actualizado = False
        try:
            while True:
                dato = cola.get_nowait()
                if "raw" in dato:
                    continue  # linea que no matcheo el formato esperado (ej. mensajes de arranque/calibracion)

                roll = float(dato["roll"])
                pitch = float(dato["pitch"])
                yaw = float(dato["yaw"])
                estado["ultimo_raw"] = {"roll": roll, "pitch": pitch, "yaw": yaw}

                ahora = time.time() - estado["t0"]
                t.append(ahora)
                roll_d.append(roll - estado["offset_roll"])
                pitch_d.append(pitch - estado["offset_pitch"])
                yaw_d.append(yaw - estado["offset_yaw"])
                ax_d.append(float(dato["ax"]))
                ay_d.append(float(dato["ay"]))
                az_d.append(float(dato["az"]))
                gx_d.append(float(dato["gx"]))
                gy_d.append(float(dato["gy"]))
                gz_d.append(float(dato["gz"]))

                fig.suptitle(f"MPU6050   |   Temp={dato['temp']} C")
                actualizado = True
        except Empty:
            pass

        if actualizado:
            l_roll.set_data(t, roll_d)
            l_pitch.set_data(t, pitch_d)
            l_yaw.set_data(t, yaw_d)
            l_ax.set_data(t, ax_d)
            l_ay.set_data(t, ay_d)
            l_az.set_data(t, az_d)
            l_gx.set_data(t, gx_d)
            l_gy.set_data(t, gy_d)
            l_gz.set_data(t, gz_d)
            txt_roll.set_text(f"ROLL\n{roll_d[-1]:+.2f}°")
            txt_pitch.set_text(f"PITCH\n{pitch_d[-1]:+.2f}°")
            if t:
                for a in (ax_ang, ax_accel, ax_gyro):
                    a.set_xlim(max(0, t[0]), max(t[-1], t[0] + 1))

        return l_roll, l_pitch, l_yaw, l_ax, l_ay, l_az, l_gx, l_gy, l_gz

    anim = FuncAnimation(fig, actualizar, interval=100, cache_frame_data=False)

    try:
        plt.show()
    finally:
        detener.set()
        ser.close()


if __name__ == "__main__":
    main()
