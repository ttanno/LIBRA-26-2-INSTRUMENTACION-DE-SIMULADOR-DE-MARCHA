"""
Prueba de EXACTITUD y REPETIBILIDAD del BNO055 contra angulos conocidos,
usando el soporte de arco indexado (ver ../soporte_angulos_imu/).

A diferencia de log_csv_bno055.py (que solo mide RUIDO con el sensor quieto
en una posicion cualquiera), este script compara el angulo que reporta el
sensor contra el angulo REAL de cada agujero de indexado -- eso mide
exactitud (error = medido - real), ademas de precision (std) y
repetibilidad (volviendo a 0 grados entre cada angulo).

Uso tipico (fila A del soporte, 0/10/20/30 grados, 30 s por angulo):
    python prueba_angulos_conocidos.py --port COM7 --angulos 0,10,20,30

Con vuelta a 0 grados entre cada angulo, para ver repetibilidad del cero:
    python prueba_angulos_conocidos.py --port COM7 --angulos 0,10,20,30 --volver-a-cero

Por defecto usa el eje "roll" -- confirmado con datos reales el 29/09: con
el montaje actual del IMU en la plataforma, "pitch" se queda practicamente
plano (174-176 grados) sin importar el angulo real aplicado, mientras que
"roll" si responde (ver angulos_20260929_171116_resumen_roll.csv). Si
cambias el montaje del sensor sobre la plataforma, confirma de nuevo cual
eje responde antes de asumir que sigue siendo roll.

Flujo (--trigger auto, default): presionas Enter ANTES de mover el sensor
(marca "ahora lo muevo"), y recien ahi lo llevas al siguiente agujero de
indexado. El script espera a ver que el sensor realmente se movio (std alto)
y despues que volvio a quedar quieto (std bajo) para arrancar la grabacion
solo, sin que tengas que tocar la laptop de nuevo mientras lo sostienes.

OJO: si solo se espera quietud SIN antes confirmar que hubo movimiento, el
script puede disparar de inmediato con el sensor todavia en la posicion
anterior (paso pendiente) -- eso paso en la primera version de este script
(ver Reportes-Semanales/S9). Por eso ahora se exige ver el movimiento
primero.

Alternativas: --trigger boton (boton fisico BOOT del ESP32, ver
revisarBoton() en el sketch -- tambien antes de mover) o --trigger enter
(Enter justo cuando el sensor YA esta quieto en la posicion, sin deteccion
automatica -- el metodo mas simple si --trigger auto te da problemas).

Salida:
    - Un CSV crudo por angulo: angulos_<fecha>_<hora>_<angulo>deg.csv
    - Un resumen final en pantalla y en angulos_<fecha>_<hora>_resumen.csv
      con las columnas: angulo_real, promedio_medido, error, std, filas

Requiere: pip install -r requirements.txt (ya incluye pyserial)
"""

import argparse
import csv
import re
import statistics
import sys
import time
from collections import deque

import serial
import serial.tools.list_ports

LINE_RE = re.compile(
    r"Calib\[sys,gyro,accel,mag\]=(?P<sys>\d+),(?P<gyro>\d+),(?P<accel>\d+),(?P<mag>\d+)\s*\|\s*"
    r"Euler\[heading,roll,pitch\]=(?P<heading>-?\d+\.\d+),(?P<roll>-?\d+\.\d+),(?P<pitch>-?\d+\.\d+)\s*\|\s*"
    r"LinAccel\[x,y,z\]=(?P<ax>-?\d+\.\d+),(?P<ay>-?\d+\.\d+),(?P<az>-?\d+\.\d+)"
)

COLUMNAS = ["t_s", "calib_sys", "calib_gyro", "calib_accel", "calib_mag", "heading", "roll", "pitch"]


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


def esperar_boton(ser: serial.Serial):
    """Descarta lineas de datos hasta ver el marcador 'BTN' que manda el
    sketch al detectar el boton BOOT del ESP32. Bloquea sin timeout -- se
    puede cortar con Ctrl+C si hace falta volver al metodo de Enter."""
    ser.reset_input_buffer()
    while True:
        try:
            linea = ser.readline().decode("utf-8", errors="replace").strip()
        except serial.SerialException:
            print("Se perdio la conexion con el puerto serial mientras se esperaba el boton.")
            raise
        if linea == "BTN":
            return


def esperar_estabilidad(ser: serial.Serial, eje: str, ventana: int, umbral_quieto: float, umbral_movimiento: float):
    """Arranca la grabacion sola, pero EXIGE ver primero que el sensor se
    movio (std_ventana > umbral_movimiento) antes de aceptar que quedo
    quieto (std_ventana < umbral_quieto). Sin este chequeo de movimiento
    previo, si el sensor ya estaba quieto en la posicion ANTERIOR cuando
    arranca la espera, dispara de inmediato sin que hayas alcanzado a
    moverlo -- ese fue el bug detectado en la primera version (angulo
    etiquetado mal, con el sensor todavia en la posicion vieja). Se puede
    cortar con Ctrl+C para pasar al siguiente angulo a mano."""
    buf = deque(maxlen=ventana)
    vio_movimiento = False
    ultimo_print = 0.0
    while True:
        try:
            linea = ser.readline().decode("utf-8", errors="replace").strip()
        except serial.SerialException:
            print("Se perdio la conexion con el puerto serial mientras se esperaba estabilidad.")
            raise
        if not linea:
            continue
        m = LINE_RE.search(linea)
        if not m:
            continue

        valor = float(m.groupdict()[eje])
        buf.append(valor)
        if len(buf) < ventana:
            continue

        std_actual = statistics.pstdev(buf)
        ahora = time.time()

        if not vio_movimiento:
            if std_actual > umbral_movimiento:
                vio_movimiento = True
                print(f"\n  Movimiento detectado ({eje} std={std_actual:.3f} > {umbral_movimiento}) -- esperando a que quede quieto en la nueva posicion...")
            elif ahora - ultimo_print > 0.5:
                ultimo_print = ahora
                print(f"  esperando que muevas el sensor... {eje}={valor:+.2f}  std_ventana={std_actual:.4f} (se considera movimiento si supera {umbral_movimiento})", end="\r")
        else:
            if std_actual < umbral_quieto:
                print(f"\n  Sensor quieto ({eje} std={std_actual:.4f} < {umbral_quieto}) -- arrancando grabacion.")
                return
            elif ahora - ultimo_print > 0.5:
                ultimo_print = ahora
                print(f"  esperando quietud... {eje}={valor:+.2f}  std_ventana={std_actual:.4f} (umbral {umbral_quieto})", end="\r")


def grabar_angulo(ser: serial.Serial, nombre_salida: str, duracion: float, eje: str):
    heading_vals, roll_vals, pitch_vals = [], [], []
    t0 = time.time()
    filas = 0

    print(f"Grabando {duracion:.0f} s en '{nombre_salida}' (Ctrl+C para cortar antes)...")

    try:
        with open(nombre_salida, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(COLUMNAS)

            while (time.time() - t0) < duracion:
                try:
                    linea = ser.readline().decode("utf-8", errors="replace").strip()
                except serial.SerialException:
                    print("Se perdio la conexion con el puerto serial.")
                    break

                if not linea:
                    continue
                m = LINE_RE.search(linea)
                if not m:
                    continue

                d = m.groupdict()
                t = time.time() - t0
                heading, roll, pitch = float(d["heading"]), float(d["roll"]), float(d["pitch"])
                writer.writerow([f"{t:.3f}", d["sys"], d["gyro"], d["accel"], d["mag"], heading, roll, pitch])
                filas += 1
                heading_vals.append(heading)
                roll_vals.append(roll)
                pitch_vals.append(pitch)

                if filas % 20 == 0:
                    print(f"  {filas} filas... (t={t:.1f}s)", end="\r")
    except KeyboardInterrupt:
        print("\nGrabacion detenida por el usuario.")

    print(f"\n{filas} filas guardadas en '{nombre_salida}'.")

    valores = {"heading": heading_vals, "roll": roll_vals, "pitch": pitch_vals}[eje]
    if filas < 2:
        print("Muy pocas filas para calcular estadisticas -- revisa que el sensor este enviando datos.")
        return None, None, filas

    promedio = statistics.mean(valores)
    std = statistics.pstdev(valores)
    print(f"  {eje}: promedio={promedio:+.3f}  std={std:.4f}")

    if filas >= 1 and all(v == 0.0 for v in heading_vals + roll_vals + pitch_vals):
        print("ATENCION: todos los valores salieron en 0.0 -- el BNO055 puede no haberse detectado bien al arrancar (revisar cableado/alimentacion antes de seguir).")

    return promedio, std, filas


def main():
    ap = argparse.ArgumentParser(description="Prueba de exactitud del BNO055 contra angulos conocidos (soporte indexado)")
    ap.add_argument("--port", help="Puerto serial (ej. COM7). Si se omite, se pide interactivamente.")
    ap.add_argument("--baud", type=int, default=115200, help="Baudrate (default 115200)")
    ap.add_argument("--angulos", required=True, help="Lista de angulos reales separados por coma, en el orden a probar. Ej: 0,10,20,30")
    ap.add_argument("--duracion", type=float, default=30.0, help="Segundos a grabar por angulo (default 30)")
    ap.add_argument("--eje", choices=["roll", "pitch", "heading"], default="roll", help="Eje del BNO055 a comparar contra el angulo real (default roll -- confirmado con el montaje actual, ver docstring)")
    ap.add_argument("--trigger", choices=["auto", "boton", "enter"], default="auto", help="Como arrancar cada grabacion: 'auto' (detecta quietud del sensor solo, default), 'boton' (boton BOOT del ESP32) o 'enter' (Enter en la laptop)")
    ap.add_argument("--ventana-estable", type=int, default=15, help="Muestras seguidas usadas para medir quietud/movimiento en --trigger auto (default 15, ~1.5 s a 10 Hz)")
    ap.add_argument("--umbral-estable", type=float, default=0.05, help="Std maxima (grados) para considerar el sensor quieto en --trigger auto (default 0.05)")
    ap.add_argument("--umbral-movimiento", type=float, default=1.5, help="Std minima (grados) para considerar que el sensor se esta moviendo en --trigger auto, antes de esperar quietud (default 1.5)")
    ap.add_argument("--volver-a-cero", action="store_true", help="Intercala una pasada extra por 0 grados entre cada angulo de la lista, para medir repetibilidad del cero")
    ap.add_argument("--salida", default=None, help="Prefijo de los archivos de salida (default: angulos_YYYYMMDD_HHMMSS)")
    args = ap.parse_args()

    angulos = [float(a.strip()) for a in args.angulos.split(",") if a.strip()]
    if args.volver_a_cero:
        secuencia = []
        for i, a in enumerate(angulos):
            if i > 0:
                secuencia.append(0.0)
            secuencia.append(a)
        angulos = secuencia

    puerto = args.port or elegir_puerto()
    try:
        ser = serial.Serial(puerto, args.baud, timeout=1)
    except serial.SerialException as e:
        print(f"No se pudo abrir {puerto}: {e}")
        sys.exit(1)
    time.sleep(2)
    print(f"Conectado a {puerto} @ {args.baud} baudios. Comparando contra eje '{args.eje}'.")

    base = args.salida or time.strftime("angulos_%Y%m%d_%H%M%S")

    filas_resumen = []
    try:
        for i, angulo_real in enumerate(angulos, 1):
            print(f"\n=== Posicion {i} de {len(angulos)}: {angulo_real:.0f} grados ===")
            if args.trigger == "auto":
                input(
                    f"Presiona Enter cuando vayas a EMPEZAR A MOVER el sensor hacia "
                    f"{angulo_real:.0f} grados (recien ahi muevelo hasta el agujero de "
                    f"indexado correspondiente)..."
                )
                esperar_estabilidad(ser, args.eje, args.ventana_estable, args.umbral_estable, args.umbral_movimiento)
            elif args.trigger == "boton":
                print(
                    f"Presiona el boton BOOT del ESP32 cuando vayas a EMPEZAR A MOVER el "
                    f"sensor hacia {angulo_real:.0f} grados (recien ahi muevelo)..."
                )
                esperar_boton(ser)
                esperar_estabilidad(ser, args.eje, args.ventana_estable, args.umbral_estable, args.umbral_movimiento)
            else:
                input(
                    f"Acomoda el IMU en el agujero de indexado de {angulo_real:.0f} grados "
                    f"(perno de pivote + perno de indexado puestos, plataforma quieta) y presiona Enter..."
                )
            nombre_salida = f"{base}_{angulo_real:.0f}deg_{i:02d}.csv"
            promedio, std, filas = grabar_angulo(ser, nombre_salida, args.duracion, args.eje)
            if promedio is None:
                continue
            error = promedio - angulo_real
            filas_resumen.append({
                "angulo_real": angulo_real, "promedio_medido": promedio,
                "error": error, "std": std, "filas": filas, "archivo": nombre_salida,
            })
    finally:
        ser.close()

    if not filas_resumen:
        print("\nNo se junto ningun resultado valido.")
        return

    resumen_csv = f"{base}_resumen.csv"
    with open(resumen_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["angulo_real", "promedio_medido", "error", "std", "filas", "archivo"])
        for r in filas_resumen:
            writer.writerow([r["angulo_real"], f"{r['promedio_medido']:.3f}", f"{r['error']:+.3f}", f"{r['std']:.4f}", r["filas"], r["archivo"]])

    print(f"\n=== Resumen (eje={args.eje}) -- guardado en '{resumen_csv}' ===")
    print(f"{'Angulo real':>12s} {'Promedio medido':>17s} {'Error':>8s} {'std':>8s}")
    for r in filas_resumen:
        print(f"{r['angulo_real']:12.1f} {r['promedio_medido']:17.3f} {r['error']:+8.3f} {r['std']:8.4f}")

    print(
        "\nError = promedio_medido - angulo_real. Si vuelves al mismo angulo mas de "
        "una vez (--volver-a-cero, o repitiendo un angulo en --angulos), compara esas "
        "filas entre si para ver la repetibilidad."
    )


if __name__ == "__main__":
    main()
