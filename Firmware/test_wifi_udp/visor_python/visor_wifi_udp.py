"""
Visor en tiempo real para los datos que manda test_wifi_udp.ino por WiFi
(UDP), en vez de por el puerto serial.

Es el mismo formato CSV y el mismo grafico que visor_mpu6050.py -- lo unico
que cambia es como llegan los datos (socket UDP en vez de puerto serial).

Uso:
    python visor_wifi_udp.py                  -> escucha en el puerto 4210
    python visor_wifi_udp.py --port 4210

Al arrancar imprime tu IP local: copiala en PC_IP dentro de test_wifi_udp.ino
antes de cargar el sketch al ESP32.

Boton "Zero / Reset": igual que en visor_mpu6050.py, es solo un offset
visual -- no reinicia el drift real que sigue acumulandose en el ESP32.

Requiere: pip install -r requirements.txt
"""

import argparse
import re
import socket
import threading
import time
from collections import deque
from queue import Queue, Empty

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Button

LINE_RE = re.compile(
    r"(?P<ax>-?\d+\.\d+),(?P<ay>-?\d+\.\d+),(?P<az>-?\d+\.\d+),"
    r"(?P<gx>-?\d+\.\d+),(?P<gy>-?\d+\.\d+),(?P<gz>-?\d+\.\d+),"
    r"(?P<roll>-?\d+\.\d+),(?P<pitch>-?\d+\.\d+),(?P<yaw>-?\d+\.\d+),"
    r"(?P<temp>-?\d+\.\d+)"
)

MAX_PUNTOS = 200  # ~4 s de ventana a ~50 Hz (mismo criterio que visor_mpu6050.py)


def obtener_ip_local() -> str:
    """IP local de esta PC en la red actual (no envia trafico real, solo
    fuerza al sistema operativo a elegir la interfaz de salida)."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except OSError:
        return "127.0.0.1  (no se pudo detectar automaticamente -- revisa 'ipconfig' en la consola de Windows)"
    finally:
        s.close()


def hilo_lectura_udp(sock: socket.socket, cola: Queue, detener: threading.Event):
    while not detener.is_set():
        try:
            data, _addr = sock.recvfrom(2048)
        except socket.timeout:
            continue
        except OSError:
            break
        linea = data.decode("utf-8", errors="replace").strip()
        if not linea:
            continue
        m = LINE_RE.search(linea)
        if m:
            cola.put(m.groupdict())
        else:
            cola.put({"raw": linea})


def main():
    ap = argparse.ArgumentParser(description="Visor en tiempo real por WiFi UDP (test_wifi_udp.ino)")
    ap.add_argument("--port", type=int, default=4210, help="Puerto UDP a escuchar (debe ser igual a UDP_PORT en el .ino)")
    ap.add_argument(
        "--rango-angulo", type=float, default=100.0,
        help="Rango +/- del eje Y para roll/pitch/yaw en grados (default 100)"
    )
    args = ap.parse_args()

    print(f"Tu IP local es: {obtener_ip_local()}")
    print("Copia esa IP en PC_IP dentro de test_wifi_udp.ino antes de cargar el sketch.")
    print(f"Escuchando paquetes UDP en el puerto {args.port}... (Ctrl+C o cierra la ventana del grafico para salir)")

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", args.port))
    sock.settimeout(1.0)

    cola: Queue = Queue()
    detener = threading.Event()
    hilo = threading.Thread(target=hilo_lectura_udp, args=(sock, cola, detener), daemon=True)
    hilo.start()

    t = deque(maxlen=MAX_PUNTOS)
    roll_d, pitch_d, yaw_d = (deque(maxlen=MAX_PUNTOS) for _ in range(3))
    ax_d, ay_d, az_d = (deque(maxlen=MAX_PUNTOS) for _ in range(3))
    gx_d, gy_d, gz_d = (deque(maxlen=MAX_PUNTOS) for _ in range(3))

    estado = {
        "t0": time.time(),
        "offset_roll": 0.0,
        "offset_pitch": 0.0,
        "offset_yaw": 0.0,
        "ultimo_raw": None,
    }

    fig, (ax_ang, ax_accel, ax_gyro) = plt.subplots(3, 1, figsize=(9, 9), sharex=True)
    fig.subplots_adjust(bottom=0.13, top=0.82, hspace=0.15)
    fig.suptitle("MPU6050 (WiFi UDP) - esperando datos...", y=0.99)

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
                    continue

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

                fig.suptitle(f"MPU6050 (WiFi UDP)   |   Temp={dato['temp']} C")
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
        sock.close()


if __name__ == "__main__":
    main()
