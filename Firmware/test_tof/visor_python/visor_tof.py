"""
Visor en tiempo real para los datos que imprime test_tof.ino por Serial
(2x VL53L1X, sensores de distancia ToF).

Mismo patron que visor_hx711.py: grafica la distancia de cada sensor en
vivo, sin caja de comandos porque este sketch no tiene comandos de
calibracion por Serial (el VL53L1X no lo necesita, ver test_tof.ino).

Uso:
    python visor_tof.py                  -> lista los puertos disponibles y pide elegir uno
    python visor_tof.py --port COM5
    python visor_tof.py --port COM5 --baud 115200

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

LINE_RE = re.compile(
    r"(?P<dist1_mm>\d+),"
    r"(?P<status1>\d+),"
    r"(?P<dist2_mm>\d+),"
    r"(?P<status2>\d+)"
)

MAX_PUNTOS = 300  # a ~50 ms/muestra (timing budget del sketch) ~ 15 s de ventana.

# Codigo de estado 0 = "RangeValid" en la libreria VL53L1X de Pololu; cualquier
# otro valor indica una lectura no confiable (fuera de rango, poca senal, etc.).
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
            # Lineas que no matchean el CSV (mensajes de arranque, escaneo
            # I2C, errores de timeout, etc.) -- se imprimen tal cual en
            # consola en vez de intentar graficarlas. El bootloader del
            # ESP32 imprime sus mensajes de arranque a 74880 baudios; leidos
            # a 115200 pueden salir bytes que la consola de Windows (cp1252)
            # no sabe representar, asi que se reemplazan en vez de crashear
            # el hilo de lectura.
            try:
                print(f"[ESP32] {linea}")
            except UnicodeEncodeError:
                enc = sys.stdout.encoding or "utf-8"
                print(f"[ESP32] {linea}".encode(enc, errors="replace").decode(enc, errors="replace"))


def main():
    ap = argparse.ArgumentParser(description="Visor en tiempo real para 2x VL53L1X (test_tof.ino)")
    ap.add_argument("--port", help="Puerto serial (ej. COM5). Si se omite, se pide interactivamente.")
    ap.add_argument("--baud", type=int, default=115200, help="Baudrate (default 115200)")
    ap.add_argument(
        "--rango-mm", type=float, default=4000.0,
        help="Rango maximo del eje Y para la distancia en mm (default 4000, alcance tipico en modo Long)"
    )
    args = ap.parse_args()

    puerto = args.port or elegir_puerto()

    try:
        ser = serial.Serial(puerto, args.baud, timeout=1)
    except serial.SerialException as e:
        print(f"No se pudo abrir {puerto}: {e}")
        sys.exit(1)

    ser.reset_input_buffer()  # descartar datos viejos que hayan quedado en el buffer antes de esta conexion
    print(f"Conectado a {puerto} @ {args.baud} baudios. Cierra la ventana del grafico para salir.")

    cola: Queue = Queue()
    detener = threading.Event()
    hilo = threading.Thread(target=hilo_lectura_serial, args=(ser, cola, detener), daemon=True)
    hilo.start()

    t = deque(maxlen=MAX_PUNTOS)
    dist1_d = deque(maxlen=MAX_PUNTOS)
    dist2_d = deque(maxlen=MAX_PUNTOS)

    estado = {"t0": time.time(), "status1": None, "status2": None}

    fig, ax = plt.subplots(figsize=(9, 6))
    fig.subplots_adjust(top=0.85)
    fig.suptitle("VL53L1X x2 (ToF) - esperando datos...", y=0.97)

    caja = dict(boxstyle="round", facecolor="black", edgecolor="0.6")
    txt_estado = fig.text(
        0.5, 0.90, "ToF1: -- | ToF2: --", fontsize=11, ha="center", va="center",
        family="monospace", color="white", bbox=caja,
    )

    (l_1,) = ax.plot([], [], color="tab:blue", label="ToF1 (U3, 0x30)")
    (l_2,) = ax.plot([], [], color="tab:orange", label="ToF2 (U2, 0x29)")
    ax.set_ylabel("Distancia (mm)")
    ax.set_xlabel("tiempo (s desde que se abrio el visor)")
    ax.set_ylim(0, args.rango_mm)
    ax.legend(loc="upper right", fontsize=8)
    ax.grid(True, alpha=0.3)

    def actualizar(_frame):
        actualizado = False
        try:
            while True:
                dato = cola.get_nowait()
                ahora = time.time() - estado["t0"]
                t.append(ahora)
                dist1_d.append(float(dato["dist1_mm"]))
                dist2_d.append(float(dato["dist2_mm"]))
                estado["status1"] = int(dato["status1"])
                estado["status2"] = int(dato["status2"])
                actualizado = True
        except Empty:
            pass

        if actualizado:
            l_1.set_data(t, dist1_d)
            l_2.set_data(t, dist2_d)
            if t:
                ax.set_xlim(max(0, t[0]), max(t[-1], t[0] + 1))

            def texto_estado(nombre, status):
                if status == STATUS_OK:
                    return f"{nombre}: OK"
                return f"{nombre}: status={status} (no valido)"

            estado_txt = (
                f"{texto_estado('ToF1', estado['status1'])}   |   "
                f"{texto_estado('ToF2', estado['status2'])}"
            )
            txt_estado.set_text(estado_txt)
            ambos_ok = estado["status1"] == STATUS_OK and estado["status2"] == STATUS_OK
            txt_estado.set_color("lime" if ambos_ok else "orange")
            fig.suptitle(
                f"VL53L1X x2 (ToF)   |   ToF1={dist1_d[-1]:.0f} mm   ToF2={dist2_d[-1]:.0f} mm", y=0.97
            )

        return l_1, l_2

    anim = FuncAnimation(fig, actualizar, interval=100, cache_frame_data=False)

    try:
        plt.show()
    finally:
        detener.set()
        ser.close()


if __name__ == "__main__":
    main()
