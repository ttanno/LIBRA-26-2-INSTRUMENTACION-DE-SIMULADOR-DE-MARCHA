"""
Visor en tiempo real de los cuatro sensores de la galleta (celda HX711,
ToF1, ToF2 y BNO055) con el sketch test_integracion_sensores.ino.

Grafica:
  - Fuerza de la celda (N; si no hay calibracion, cuentas crudas)
  - Distancia de ToF1 y ToF2 (mm; solo lecturas con estado valido = 0)
  - Roll, pitch y heading del BNO055 (grados; solo muestras con ok=1)
  - Barra de estado: frecuencia real de cada sensor en los ultimos 5 s,
    errores acumulados (contadores del ESP32) y duracion maxima del loop

Uso:
    python visor_integracion.py                 -> pide elegir el puerto
    python visor_integracion.py --port COM7

Caja "Comando (i | r)": i = reimprime el reporte inicial (escaneo guardado),
r = reinicia los contadores del ESP32.

Boton "Grabar" / "Detener": al empezar manda 'i' y 'r' al ESP32 (reporte
inicial dentro del archivo y contadores en cero) y guarda todas las lineas
tal como llegan, con la hora del PC, en
grabaciones/integracion_<fecha>_<hora>_raw.log. Ese
archivo se puede analizar despues con
    python log_integracion.py --analizar grabaciones/<archivo>_raw.log

No usar al mismo tiempo que log_integracion.py: solo un programa puede tener
abierto el puerto.

Requiere: pip install -r requirements.txt
"""

import argparse
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

VENTANA_S = 30.0         # segundos visibles en el grafico
VENTANA_FREC_S = 5.0     # ventana para calcular la frecuencia real
MAX_PUNTOS = 2000        # por serie (a ~11 Hz alcanza para ~3 min)


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
        if linea:
            # Hora del PC tomada al llegar la linea (para grabar y para la
            # frecuencia mostrada; el analisis fino usa t_us del ESP32).
            cola.put((time.time(), linea))


def main():
    ap = argparse.ArgumentParser(description="Visor en tiempo real de test_integracion_sensores.ino")
    ap.add_argument("--port", help="Puerto serial (ej. COM7). Si se omite, se pide interactivamente.")
    ap.add_argument("--baud", type=int, default=115200)
    args = ap.parse_args()

    puerto = args.port or elegir_puerto()
    try:
        ser = serial.Serial(puerto, args.baud, timeout=1)
    except serial.SerialException as e:
        print(f"No se pudo abrir {puerto}: {e}")
        sys.exit(1)
    print(f"Conectado a {puerto} @ {args.baud} baudios. Cierra la ventana para salir.")

    cola: Queue = Queue()
    detener = threading.Event()
    threading.Thread(target=hilo_lectura_serial, args=(ser, cola, detener), daemon=True).start()

    t0 = time.time()
    serie = {k: (deque(maxlen=MAX_PUNTOS), deque(maxlen=MAX_PUNTOS))
             for k in ("H", "T1", "T2", "roll", "pitch", "heading")}
    llegadas = {k: deque(maxlen=200) for k in ("H", "T1", "T2", "I")}
    estado = {"S": None, "init": "", "calibrado": None, "imu_malas": 0, "tof_invalidas": 0}

    fig, (ax_f, ax_d, ax_a) = plt.subplots(3, 1, figsize=(10, 8.5), sharex=True)
    fig.subplots_adjust(bottom=0.13, top=0.84, hspace=0.25)
    fig.suptitle("Galleta LIBRA - celda + 2x ToF + BNO055 (esperando datos...)", y=0.985)
    txt_estado = fig.text(0.5, 0.905, "", fontsize=9, ha="center", va="center", family="monospace",
                          bbox=dict(boxstyle="round", facecolor="#f4f4f4", edgecolor="0.7"))

    (l_f,) = ax_f.plot([], [], color="tab:orange", lw=1.2)
    ax_f.set_ylabel("Fuerza (N)")
    ax_f.grid(True, alpha=0.3)

    (l_t1,) = ax_d.plot([], [], color="tab:blue", lw=1.2, label="ToF1 (0x30)")
    (l_t2,) = ax_d.plot([], [], color="tab:green", lw=1.2, label="ToF2 (0x29)")
    ax_d.set_ylabel("Distancia (mm)")
    ax_d.legend(loc="upper left", fontsize=8)
    ax_d.grid(True, alpha=0.3)

    (l_r,) = ax_a.plot([], [], color="tab:red", lw=1.2, label="roll")
    (l_p,) = ax_a.plot([], [], color="tab:purple", lw=1.2, label="pitch")
    ax_h = ax_a.twinx()
    (l_h,) = ax_h.plot([], [], color="0.6", lw=0.8, ls="--", label="heading (eje der.)")
    ax_a.set_ylabel("Roll / pitch (°)")
    ax_h.set_ylabel("Heading (°)", color="0.4")
    ax_a.set_xlabel("tiempo (s desde que se abrio el visor)")
    ax_a.legend(handles=[l_r, l_p, l_h], loc="upper left", fontsize=8)
    ax_a.grid(True, alpha=0.3)

    # ---------------- Comandos ----------------
    ax_cmd = fig.add_axes([0.22, 0.03, 0.4, 0.045])
    caja = TextBox(ax_cmd, "Comando (i | r): ")

    def on_submit(texto):
        cmd = texto.strip()
        if cmd:
            ser.write((cmd + "\n").encode("utf-8"))
            print(f"[visor] Comando enviado: {cmd}")
            caja.set_val("")

    caja.on_submit(on_submit)

    # ---------------- Grabacion ----------------
    ax_btn = fig.add_axes([0.7, 0.03, 0.2, 0.045])
    boton = Button(ax_btn, "Grabar", color="0.85", hovercolor="0.95")
    grab = {"f": None, "t_ini": 0.0, "n": 0, "ruta": None}

    def iniciar():
        carpeta = Path(__file__).resolve().parent / "grabaciones"
        carpeta.mkdir(exist_ok=True)
        ruta = carpeta / f"integracion_{datetime.now():%Y%m%d_%H%M%S}_raw.log"
        grab.update(f=open(ruta, "w", encoding="utf-8"), t_ini=time.time(), n=0, ruta=ruta)
        # Marca que log_integracion.py --analizar usa como inicio del registro.
        # 'i' reimprime el reporte (CONFIG, escaneo guardado, INIT) dentro del
        # archivo y 'r' reinicia los contadores, igual que hace log_integracion.py.
        grab["f"].write(f"{0.0:.3f}\t# PC INICIO_REGISTRO\n")
        ser.write(b"i\n")
        ser.write(b"r\n")
        boton.label.set_text("Detener")
        boton.color = "tomato"
        ax_btn.set_facecolor("tomato")
        print(f"[visor] GRABANDO -> {ruta}")

    def parar():
        if grab["f"] is None:
            return
        grab["f"].close()
        print(f"[visor] Grabacion detenida: {grab['n']} lineas en {time.time() - grab['t_ini']:.1f} s -> {grab['ruta']}")
        grab["f"] = None
        boton.label.set_text("Grabar")
        boton.color = "0.85"
        ax_btn.set_facecolor("0.85")

    def on_grabar(_):
        parar() if grab["f"] else iniciar()
        fig.canvas.draw_idle()

    boton.on_clicked(on_grabar)

    # ---------------- Procesamiento de lineas ----------------
    def procesar(t_pc: float, linea: str):
        t = t_pc - t0
        if grab["f"] is not None:
            grab["f"].write(f"{t_pc - grab['t_ini']:.3f}\t{linea}\n")
            grab["n"] += 1
        if linea.startswith("#"):
            print(f"[ESP32] {linea}")
            if linea.startswith("# INIT"):
                estado["init"] = linea[2:]
            elif linea.startswith("# CAL"):
                estado["calibrado"] = "calibrado=1" in linea
            return
        c = linea.split(",")
        try:
            tipo = c[0]
            if tipo == "H" and len(c) == 5:
                raw, fuerza = int(c[3]), float(c[4])
                # Sin calibracion el ESP32 manda force_N = 0 -> mostrar cuentas
                v = raw if estado["calibrado"] is False else fuerza
                serie["H"][0].append(t); serie["H"][1].append(v)
                llegadas["H"].append(t)
            elif tipo == "T" and len(c) == 6:
                k = "T1" if c[3] == "1" else "T2"
                llegadas[k].append(t)
                if c[5] == "0":
                    serie[k][0].append(t); serie[k][1].append(int(c[4]))
                else:
                    estado["tof_invalidas"] += 1
            elif tipo == "I" and len(c) == 12:
                llegadas["I"].append(t)
                if c[4] == "1":
                    for k, idx in (("roll", 5), ("pitch", 6), ("heading", 7)):
                        serie[k][0].append(t); serie[k][1].append(float(c[idx]))
                else:
                    estado["imu_malas"] += 1
            elif tipo == "S" and len(c) == 13:
                estado["S"] = [int(x) for x in c[3:]]
            elif tipo == "E":
                print(f"[ESP32] {linea}")
        except ValueError:
            print(f"[visor] linea malformada: {linea!r}")

    def frec(k, ahora):
        n = sum(1 for x in llegadas[k] if ahora - x <= VENTANA_FREC_S)
        return n / VENTANA_FREC_S

    def actualizar(_frame):
        try:
            while True:
                procesar(*cola.get_nowait())
        except Empty:
            pass

        ahora = time.time() - t0
        for linea_plot, k in ((l_f, "H"), (l_t1, "T1"), (l_t2, "T2"), (l_r, "roll"), (l_p, "pitch"), (l_h, "heading")):
            linea_plot.set_data(serie[k][0], serie[k][1])
        ax_a.set_xlim(max(0.0, ahora - VENTANA_S), max(ahora, VENTANA_S))
        for ax in (ax_f, ax_d, ax_a):
            ax.relim()
            ax.autoscale_view(scalex=False, scaley=True)
        ax_h.set_ylim(0, 360)
        ax_f.set_ylabel("Celda (cuentas)" if estado["calibrado"] is False else "Fuerza (N)")

        s = estado["S"]
        errores = (f"err H={s[4]} T1={s[5]} T2={s[6]} I={s[7]} | loop max {s[8] / 1000:.1f} ms"
                   if s else "err: esperando linea S")
        txt_estado.set_text(
            f"Hz (ult. {VENTANA_FREC_S:.0f} s)  celda {frec('H', ahora):5.1f} | ToF1 {frec('T1', ahora):5.1f} | "
            f"ToF2 {frec('T2', ahora):5.1f} | IMU {frec('I', ahora):5.1f}\n"
            f"{errores} | IMU descartadas {estado['imu_malas']} | ToF invalidas {estado['tof_invalidas']}"
        )

        partes = []
        if serie["H"][1]:
            partes.append(f"F {serie['H'][1][-1]:+.1f} {'cts' if estado['calibrado'] is False else 'N'}")
        if serie["T1"][1]:
            partes.append(f"ToF1 {serie['T1'][1][-1]} mm")
        if serie["T2"][1]:
            partes.append(f"ToF2 {serie['T2'][1][-1]} mm")
        if serie["roll"][1]:
            partes.append(f"roll {serie['roll'][1][-1]:+.2f}°  pitch {serie['pitch'][1][-1]:+.2f}°")
        titulo = "   |   ".join(partes) if partes else "esperando datos..."
        if grab["f"] is not None:
            titulo = f"● GRABANDO {time.time() - grab['t_ini']:.0f} s   |   " + titulo
            grab["f"].flush()
        fig.suptitle(titulo, y=0.985, color="red" if grab["f"] is not None else "black", fontsize=11)
        return ()

    anim = FuncAnimation(fig, actualizar, interval=150, cache_frame_data=False)  # noqa: F841

    try:
        plt.show()
    finally:
        parar()
        detener.set()
        ser.close()


if __name__ == "__main__":
    main()
