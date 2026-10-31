"""
Visor en tiempo real para los datos que imprime test_hx711.ino por Serial
(driver de la celda de carga sobre el HX711).

Igual que visor_ads1256.py: ademas de graficar, tiene una caja de texto para
mandar los comandos de calibracion (t, k<masa_kg>, r) sin ir y volver al
Monitor Serie del Arduino IDE.

Uso:
    python visor_hx711.py                  -> lista los puertos disponibles y pide elegir uno
    python visor_hx711.py --port COM5
    python visor_hx711.py --port COM5 --baud 115200

Caja de texto "Comando (t | k<masa_kg> | r)": escribe el comando y presiona
Enter para mandarlo al ESP32 -- mismo efecto que escribirlo en el Monitor
Serie.

Boton "Grabar" / "Detener": guarda las muestras en
grabaciones/hx711_<fecha>_<hora>.csv con columnas
pc_time_iso, pc_time_unix_s, t_rel_s, raw_code, force_N, tared, calibrated.
La hora de la PC se toma al llegar cada linea por el puerto, para poder
alinear despues con otro equipo grabando en paralelo (ej. plataforma AMTI).

Requiere: pip install -r requirements.txt
"""

import argparse
import csv
import re
import sys
import threading
import time
from collections import deque
from datetime import datetime
from pathlib import Path
from queue import Queue, Empty

import serial
import serial.tools.list_ports
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Button, TextBox

LINE_RE = re.compile(
    r"(?P<raw_code>-?\d+),"
    r"(?P<force_N>-?\d+\.\d+),"
    r"(?P<tared>[01]),"
    r"(?P<calibrated>[01])"
)

MAX_PUNTOS = 300  # a ~10 SPS (tasa fija del HX711 en la mayoria de los breakouts) ~ 30 s de ventana.


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
            # Marca de tiempo tomada aca, al llegar la linea, y no en el
            # redibujado (que agrupa muestras cada ~100 ms) -- es la que se
            # graba al CSV para sincronizar con otros equipos (ej. AMTI).
            cola.put((time.time(), m.groupdict()))
        else:
            # Lineas que no matchean el CSV (mensajes de arranque, errores de
            # timeout, confirmaciones de tara/calibracion, etc.) -- se
            # imprimen tal cual en consola en vez de intentar graficarlas.
            print(f"[ESP32] {linea}")


def main():
    ap = argparse.ArgumentParser(description="Visor en tiempo real para la celda de carga (test_hx711.ino)")
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
    raw_d = deque(maxlen=MAX_PUNTOS)
    force_d = deque(maxlen=MAX_PUNTOS)

    estado = {
        "t0": time.time(),
        "tared": False,
        "calibrated": False,
    }

    fig, (ax_r, ax_f) = plt.subplots(2, 1, figsize=(9, 7), sharex=True)
    fig.subplots_adjust(bottom=0.2, top=0.85, hspace=0.2)
    fig.suptitle("HX711 (celda de carga) - esperando datos...", y=0.98)

    caja = dict(boxstyle="round", facecolor="black", edgecolor="0.6")
    txt_estado = fig.text(
        0.5, 0.90, "tara: -- | calibracion: --", fontsize=11, ha="center", va="center",
        family="monospace", color="white", bbox=caja,
    )

    (l_r,) = ax_r.plot([], [], color="tab:blue", label="raw_code (cuentas crudas, sin tara)")
    ax_r.set_ylabel("Cuentas")
    ax_r.legend(loc="upper right", fontsize=8)
    ax_r.grid(True, alpha=0.3)

    (l_f,) = ax_f.plot([], [], color="tab:orange", label="force_N (calibrado)")
    ax_f.set_ylabel("Newtons")
    ax_f.set_xlabel("tiempo (s desde que se abrio el visor)")
    ax_f.set_ylim(-args.rango_fuerza, args.rango_fuerza)
    ax_f.legend(loc="upper right", fontsize=8)
    ax_f.grid(True, alpha=0.3)

    ax_cmd = fig.add_axes([0.25, 0.03, 0.42, 0.05])
    caja_comando = TextBox(ax_cmd, "Comando (t | k<masa_kg> | r): ")

    # ---------------- Grabacion a CSV (boton Grabar / Detener) ----------------
    ax_btn = fig.add_axes([0.72, 0.03, 0.2, 0.05])
    boton_grabar = Button(ax_btn, "Grabar", color="0.85", hovercolor="0.95")
    grabacion = {"archivo": None, "writer": None, "t_ini": 0.0, "n": 0, "ruta": None}

    def iniciar_grabacion():
        carpeta = Path(__file__).resolve().parent / "grabaciones"
        carpeta.mkdir(exist_ok=True)
        ruta = carpeta / f"hx711_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        f = open(ruta, "w", newline="", encoding="utf-8")
        w = csv.writer(f)
        w.writerow(["pc_time_iso", "pc_time_unix_s", "t_rel_s", "raw_code", "force_N", "tared", "calibrated"])
        grabacion.update(archivo=f, writer=w, t_ini=time.time(), n=0, ruta=ruta)
        boton_grabar.label.set_text("Detener")
        ax_btn.set_facecolor("tomato")
        boton_grabar.color = "tomato"
        print(f"[visor] GRABANDO -> {ruta}  (inicio {datetime.now().isoformat(timespec='milliseconds')})")

    def detener_grabacion():
        if grabacion["archivo"] is None:
            return
        grabacion["archivo"].close()
        dur = time.time() - grabacion["t_ini"]
        print(f"[visor] Grabacion detenida: {grabacion['n']} muestras en {dur:.1f} s -> {grabacion['ruta']}")
        grabacion.update(archivo=None, writer=None)
        boton_grabar.label.set_text("Grabar")
        ax_btn.set_facecolor("0.85")
        boton_grabar.color = "0.85"

    def on_grabar(_evento):
        if grabacion["archivo"] is None:
            iniciar_grabacion()
        else:
            detener_grabacion()
        fig.canvas.draw_idle()

    boton_grabar.on_clicked(on_grabar)

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
                t_pc, dato = cola.get_nowait()
                ahora = t_pc - estado["t0"]
                if grabacion["writer"] is not None:
                    grabacion["writer"].writerow([
                        datetime.fromtimestamp(t_pc).isoformat(timespec="milliseconds"),
                        f"{t_pc:.3f}", f"{t_pc - grabacion['t_ini']:.3f}",
                        dato["raw_code"], dato["force_N"], dato["tared"], dato["calibrated"],
                    ])
                    grabacion["n"] += 1
                t.append(ahora)
                raw_d.append(float(dato["raw_code"]))
                force_d.append(float(dato["force_N"]))
                estado["tared"] = dato["tared"] == "1"
                estado["calibrated"] = dato["calibrated"] == "1"
                actualizado = True
        except Empty:
            pass

        if actualizado:
            l_r.set_data(t, raw_d)
            l_f.set_data(t, force_d)
            if t:
                ax_r.set_xlim(max(0, t[0]), max(t[-1], t[0] + 1))
                ax_r.relim()
                ax_r.autoscale_view(scalex=False, scaley=True)

            estado_txt = (
                f"tara: {'OK' if estado['tared'] else 'sin tarar'}   |   "
                f"calibracion: {'OK' if estado['calibrated'] else 'sin calibrar (force_N no valido)'}"
            )
            txt_estado.set_text(estado_txt)
            txt_estado.set_color("lime" if estado["calibrated"] else "orange")
            titulo = f"HX711 (celda de carga)   |   ultima fuerza: {force_d[-1]:+.2f} N"
            if grabacion["writer"] is not None:
                titulo += f"   |   ● GRABANDO {time.time() - grabacion['t_ini']:.1f} s"
                grabacion["archivo"].flush()
            fig.suptitle(titulo, y=0.98, color="red" if grabacion["writer"] is not None else "black")

        return l_r, l_f

    anim = FuncAnimation(fig, actualizar, interval=100, cache_frame_data=False)

    try:
        plt.show()
    finally:
        detener_grabacion()  # si se cierra la ventana grabando, no se pierde el archivo
        detener.set()
        ser.close()


if __name__ == "__main__":
    main()
