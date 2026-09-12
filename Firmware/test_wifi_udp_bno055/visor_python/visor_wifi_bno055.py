"""
Visor en tiempo real para los datos que manda test_wifi_udp_bno055.ino por
WiFi (UDP) -- version BNO055 (DFRobot) de visor_wifi_udp.py (esa era para
el MPU6050).

Mismo formato de linea y mismo grafico que visor_imu.py (el de Serial para
test_bno055.ino), pero:
  - Los datos llegan por un socket UDP en vez de un puerto serial.
  - Los botones que mandaban comandos por Serial ("Cero absoluto (flash)" /
    "Borrar cero (flash)") ahora mandan el mismo comando 'z'/'c' como
    paquete UDP directo al ESP32 -- para eso, el visor necesita conocer la
    IP del ESP32, que descubre solo del primer paquete que reciba (no hace
    falta configurarla a mano).

Uso:
    python visor_wifi_bno055.py                  -> escucha en el puerto 4211
    python visor_wifi_bno055.py --port 4211

Al arrancar imprime tu IP local: copiala en PC_IP dentro de
test_wifi_udp_bno055.ino antes de cargar el sketch.

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
    r"Calib\[sys,gyro,accel,mag\]=(?P<sys>\d+),(?P<gyro>\d+),(?P<accel>\d+),(?P<mag>\d+)\s*\|\s*"
    r"Euler\[heading,roll,pitch\]=(?P<heading>-?\d+\.\d+),(?P<roll>-?\d+\.\d+),(?P<pitch>-?\d+\.\d+)\s*\|\s*"
    r"LinAccel\[x,y,z\]=(?P<ax>-?\d+\.\d+),(?P<ay>-?\d+\.\d+),(?P<az>-?\d+\.\d+)"
)

MAX_PUNTOS = 200  # ~20 s de ventana a ~10 Hz (el sketch manda cada 100 ms)


def obtener_ip_local() -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except OSError:
        return "127.0.0.1  (no se pudo detectar automaticamente -- revisa 'ipconfig' en la consola de Windows)"
    finally:
        s.close()


def hilo_lectura_udp(sock: socket.socket, cola: Queue, detener: threading.Event, estado: dict):
    while not detener.is_set():
        try:
            data, addr = sock.recvfrom(2048)
        except socket.timeout:
            continue
        except OSError:
            break
        estado["esp32_addr"] = addr  # se actualiza con cada paquete: asi sabemos donde mandar 'z'/'c'
        linea = data.decode("utf-8", errors="replace").strip()
        if not linea:
            continue
        m = LINE_RE.search(linea)
        if m:
            cola.put(m.groupdict())
        else:
            cola.put({"raw": linea})


def main():
    ap = argparse.ArgumentParser(description="Visor en tiempo real por WiFi UDP para BNO055 (test_wifi_udp_bno055.ino)")
    ap.add_argument("--port", type=int, default=4211, help="Puerto UDP a escuchar (debe ser igual a UDP_PORT en el .ino)")
    ap.add_argument(
        "--rango-euler", type=float, default=100.0,
        help="Rango +/- del eje Y para heading/roll/pitch en grados (default 100)"
    )
    args = ap.parse_args()

    print(f"Tu IP local es: {obtener_ip_local()}")
    print("Copia esa IP en PC_IP dentro de test_wifi_udp_bno055.ino antes de cargar el sketch.")
    print(f"Escuchando paquetes UDP en el puerto {args.port}...")
    print("Los botones de cero absoluto/borrar solo funcionan despues de recibir el primer paquete del ESP32 (para saber su IP).")

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", args.port))
    sock.settimeout(1.0)

    cola: Queue = Queue()
    detener = threading.Event()
    estado_red = {"esp32_addr": None}
    hilo = threading.Thread(target=hilo_lectura_udp, args=(sock, cola, detener, estado_red), daemon=True)
    hilo.start()

    t = deque(maxlen=MAX_PUNTOS)
    heading_d, roll_d, pitch_d = (deque(maxlen=MAX_PUNTOS) for _ in range(3))
    ax_d, ay_d, az_d = (deque(maxlen=MAX_PUNTOS) for _ in range(3))

    estado = {
        "t0": time.time(),
        "offset_heading": 0.0,
        "offset_roll": 0.0,
        "offset_pitch": 0.0,
        "ultimo_raw": None,
    }

    fig, (ax_euler, ax_accel) = plt.subplots(2, 1, figsize=(9, 8), sharex=True)
    fig.subplots_adjust(bottom=0.15, top=0.78, hspace=0.1)
    fig.suptitle("BNO055 (WiFi UDP) - esperando datos...", y=0.99)

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
        ultimo = estado["ultimo_raw"]
        if ultimo is not None:
            estado["offset_heading"] = ultimo["heading"]
            estado["offset_roll"] = ultimo["roll"]
            estado["offset_pitch"] = ultimo["pitch"]
        t.clear()
        heading_d.clear(); roll_d.clear(); pitch_d.clear()
        ax_d.clear(); ay_d.clear(); az_d.clear()
        estado["t0"] = time.time()

    def _enviar_comando(cmd: bytes, etiqueta: str):
        addr = estado_red["esp32_addr"]
        if addr is None:
            print(f">> No se puede mandar '{etiqueta}' todavia: no se ha recibido ningun paquete del ESP32 (no se conoce su IP).")
            return
        print(f">> Enviando '{etiqueta}' a {addr[0]}:{addr[1]}...")
        sock.sendto(cmd, addr)

    def on_set_flash(_event):
        _enviar_comando(b"z", "z (fijar cero absoluto)")

    def on_clear_flash(_event):
        _enviar_comando(b"c", "c (borrar cero absoluto)")

    boton_reset.on_clicked(on_reset)
    boton_flash.on_clicked(on_set_flash)
    boton_borrar.on_clicked(on_clear_flash)

    def actualizar(_frame):
        actualizado = False
        try:
            while True:
                dato = cola.get_nowait()
                if "raw" in dato:
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
                fig.suptitle(f"BNO055 (WiFi UDP)   |   Calib sys={sys_c} gyro={gyro_c} accel={accel_c} mag={mag_c}")
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
        sock.close()


if __name__ == "__main__":
    main()
