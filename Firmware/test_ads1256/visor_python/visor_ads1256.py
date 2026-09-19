"""
Visor en tiempo real para los datos que imprime test_ads1256.ino por Serial
(driver de la celda de carga sobre el ADS1256).

A diferencia de los visores de IMU (BNO055/MPU6050), acá lo importante no es
solo graficar sino también poder CALIBRAR sin tener que ir y volver al
Monitor Serie del Arduino IDE: hay una caja de texto para mandar los mismos
comandos que entiende el sketch (t, k<masa_kg>, r).

Uso:
    python visor_ads1256.py                  -> lista los puertos disponibles y pide elegir uno
    python visor_ads1256.py --port COM5
    python visor_ads1256.py --port COM5 --baud 115200

Caja de texto "Comando (t | k<masa_kg> | r)": escribe el comando y presiona
Enter para mandarlo al ESP32 -- mismo efecto que escribirlo en el Monitor
Serie.

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
from matplotlib.widgets import TextBox

LINE_RE = re.compile(
    r"(?P<raw_code>-?\d+),"
    r"(?P<voltage_V>-?\d+\.\d+),"
    r"(?P<force_N>-?\d+\.\d+),"
    r"(?P<tared>[01]),"
    r"(?P<calibrated>[01])"
)

MAX_PUNTOS = 300  # a ~100 SPS (DRATE por defecto del sketch) ~ 3 s de ventana.
# Si el sketch se reconfigura a otra tasa de datos, ajustar acá si se quiere
# mantener la misma ventana de tiempo visible.


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
        else:
            # Lineas que no matchean el CSV (mensajes de arranque, errores de
            # DRDY, confirmaciones de tara/calibracion, etc.) -- se imprimen
            # tal cual en consola en vez de intentar graficarlas.
            print(f"[ESP32] {linea}")


def main():
    ap = argparse.ArgumentParser(description="Visor en tiempo real para la celda de carga (test_ads1256.ino)")
    ap.add_argument("--port", help="Puerto serial (ej. COM5). Si se omite, se pide interactivamente.")
    ap.add_argument("--baud", type=int, default=115200, help="Baudrate (default 115200)")
    ap.add_argument(
        "--rango-fuerza", type=float, default=500.0,
        help="Rango +/- del eje Y para la fuerza en Newtons (default 500)"
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
    voltage_d = deque(maxlen=MAX_PUNTOS)
    force_d = deque(maxlen=MAX_PUNTOS)

    estado = {
        "t0": time.time(),
        "tared": False,
        "calibrated": False,
    }

    fig, (ax_v, ax_f) = plt.subplots(2, 1, figsize=(9, 7), sharex=True)
    fig.subplots_adjust(bottom=0.2, top=0.85, hspace=0.2)
    fig.suptitle("ADS1256 (celda de carga) - esperando datos...", y=0.98)

    caja = dict(boxstyle="round", facecolor="black", edgecolor="0.6")
    txt_estado = fig.text(
        0.5, 0.90, "tara: -- | calibracion: --", fontsize=11, ha="center", va="center",
        family="monospace", color="white", bbox=caja,
    )

    (l_v,) = ax_v.plot([], [], color="tab:blue", label="voltage_V (crudo, sin tara)")
    ax_v.set_ylabel("Voltios")
    ax_v.legend(loc="upper right", fontsize=8)
    ax_v.grid(True, alpha=0.3)

    (l_f,) = ax_f.plot([], [], color="tab:orange", label="force_N (calibrado)")
    ax_f.set_ylabel("Newtons")
    ax_f.set_xlabel("tiempo (s desde que se abrio el visor)")
    ax_f.set_ylim(-args.rango_fuerza, args.rango_fuerza)
    ax_f.legend(loc="upper right", fontsize=8)
    ax_f.grid(True, alpha=0.3)

    ax_cmd = fig.add_axes([0.25, 0.03, 0.5, 0.05])
    caja_comando = TextBox(ax_cmd, "Comando (t | k<masa_kg> | r): ")

    def on_submit(texto):
        cmd = texto.strip()
        if not cmd:
            return
        ser.write((cmd + "\n").encode("utf-8"))
        print(f"[visor] Comando enviado: {cmd}")
        caja_comando.set_val("")

    caja_comando.on_submit(on_submit)

    def actualizar(_frame):
        actualizado = False
        try:
            while True:
                dato = cola.get_nowait()
                ahora = time.time() - estado["t0"]
                t.append(ahora)
                voltage_d.append(float(dato["voltage_V"]))
                force_d.append(float(dato["force_N"]))
                estado["tared"] = dato["tared"] == "1"
                estado["calibrated"] = dato["calibrated"] == "1"
                actualizado = True
        except Empty:
            pass

        if actualizado:
            l_v.set_data(t, voltage_d)
            l_f.set_data(t, force_d)
            if t:
                ax_v.set_xlim(max(0, t[0]), max(t[-1], t[0] + 1))
                ax_v.relim()
                ax_v.autoscale_view(scalex=False, scaley=True)

            estado_txt = (
                f"tara: {'OK' if estado['tared'] else 'sin tarar'}   |   "
                f"calibracion: {'OK' if estado['calibrated'] else 'sin calibrar (force_N no valido)'}"
            )
            txt_estado.set_text(estado_txt)
            txt_estado.set_color("lime" if estado["calibrated"] else "orange")
            fig.suptitle(f"ADS1256 (celda de carga)   |   ultima fuerza: {force_d[-1]:+.2f} N", y=0.98)

        return l_v, l_f

    anim = FuncAnimation(fig, actualizar, interval=100, cache_frame_data=False)

    try:
        plt.show()
    finally:
        detener.set()
        ser.close()


if __name__ == "__main__":
    main()
