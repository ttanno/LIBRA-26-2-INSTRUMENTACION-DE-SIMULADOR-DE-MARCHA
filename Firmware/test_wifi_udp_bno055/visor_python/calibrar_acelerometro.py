"""
Calibracion del acelerometro del BNO055 por "6 posiciones" -- sin necesidad
de hacer la figura de 8 / movimiento continuo que pide la auto-calibracion
del propio chip (que es la que se ve trabada en calib.accel=0 en tus
pruebas). Esto SI queda guardado en el chip (via registros de offset) y
persiste en la flash del ESP32 entre reinicios -- una vez que lo corres,
no hace falta repetirlo cada vez que enciendes el ESP32.

Por que funciona / por que no hay atajo de IA que lo reemplace:
El acelerometro tiene un sesgo (offset) fijo por eje que hay que restar
para que la lectura en reposo de cada eje sea exactamente 0 g (excepto el
eje que apunta a la gravedad, que debe leer +-1 g). Para separar "sesgo
del sensor" de "direccion de la gravedad" es matematicamente necesario ver
el sensor quieto en al menos un par de orientaciones opuestas por eje (6
en total) -- con el sensor en UNA sola posicion, esa informacion
simplemente no esta en los datos, entonces ningun algoritmo (con o sin IA)
puede inventarla. Lo que SI se puede hacer con procesamiento es evitar la
danza de "muevelo despacio en el aire" del chip: basta con apoyarlo quieto
en 6 orientaciones distintas (las 6 caras de un cubo, en cualquier orden,
sin que importe cual llames X/Y/Z) y este script hace el resto.

Uso:
    python calibrar_acelerometro.py --port COM7

Requiere que el sketch cargado en el ESP32 ya incluya el campo
"AccRaw[x,y,z]=..." en la linea que imprime (ver test_wifi_ap_bno055.ino /
test_wifi_udp_bno055.ino actualizados) y el comando 'a<x>,<y>,<z>' para
aplicar la calibracion.

Requiere: pip install -r requirements.txt (pyserial)
"""

import argparse
import re
import sys
import time

import serial
import serial.tools.list_ports

LINE_RE = re.compile(
    r"Calib\[sys,gyro,accel,mag\]=(?P<sys>\d+),(?P<gyro>\d+),(?P<accel>\d+),(?P<mag>\d+).*"
    r"AccRaw\[x,y,z\]=(?P<ax>-?\d+\.\d+),(?P<ay>-?\d+\.\d+),(?P<az>-?\d+\.\d+)"
)

GRAVEDAD_MG = 1000.0  # 1 g en mg -- lo que deberia leer el eje que apunta hacia arriba/abajo
DURACION_POR_POSE_S = 2.0

# las 6 combinaciones que necesitamos: eje dominante ('X'/'Y'/'Z') + signo ('+'/'-')
POSES_NECESARIAS = [
    ("X", "+"), ("X", "-"),
    ("Y", "+"), ("Y", "-"),
    ("Z", "+"), ("Z", "-"),
]


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


def leer_accraw_promedio(ser: serial.Serial, duracion: float):
    """Lee lineas por `duracion` segundos y devuelve el promedio de AccRaw x,y,z."""
    xs, ys, zs = [], [], []
    t0 = time.time()
    while time.time() - t0 < duracion:
        try:
            linea = ser.readline().decode("utf-8", errors="replace").strip()
        except serial.SerialException:
            print("Se perdio la conexion con el puerto serial.")
            sys.exit(1)
        if not linea:
            continue
        m = LINE_RE.search(linea)
        if not m:
            continue
        xs.append(float(m.group("ax")))
        ys.append(float(m.group("ay")))
        zs.append(float(m.group("az")))

    if len(xs) < 3:
        return None
    return (sum(xs) / len(xs), sum(ys) / len(ys), sum(zs) / len(zs))


def eje_dominante(vec):
    x, y, z = vec
    ejes = {"X": x, "Y": y, "Z": z}
    nombre = max(ejes, key=lambda k: abs(ejes[k]))
    valor = ejes[nombre]
    signo = "+" if valor >= 0 else "-"
    return nombre, signo, valor


def main():
    ap = argparse.ArgumentParser(description="Calibracion de 6 posiciones del acelerometro del BNO055")
    ap.add_argument("--port", help="Puerto serial (ej. COM7). Si se omite, se pide interactivamente.")
    ap.add_argument("--baud", type=int, default=115200, help="Baudrate (default 115200)")
    args = ap.parse_args()

    puerto = args.port or elegir_puerto()

    try:
        ser = serial.Serial(puerto, args.baud, timeout=1)
    except serial.SerialException as e:
        print(f"No se pudo abrir {puerto}: {e}")
        sys.exit(1)

    time.sleep(2)
    print(f"Conectado a {puerto} @ {args.baud} baudios.\n")

    print("=" * 70)
    print("CALIBRACION DE ACELEROMETRO (6 posiciones)")
    print("=" * 70)
    print(
        "Vas a apoyar el sensor QUIETO sobre una superficie plana, en 6\n"
        "orientaciones distintas -- una por cada cara de un cubo imaginario\n"
        "(por ejemplo: normal, boca abajo, de canto hacia la izquierda, de\n"
        "canto hacia la derecha, parado en un extremo, parado en el otro).\n"
        "No importa que cara llames 'arriba' -- el script detecta solo cual\n"
        "eje quedo apuntando a la gravedad en cada pose.\n"
    )

    lecturas = {}  # (eje, signo) -> valor promedio en ese eje para esa pose

    intento = 0
    while len(lecturas) < 6:
        intento += 1
        faltantes = [p for p in POSES_NECESARIAS if p not in lecturas]
        print(f"\n--- Pose {intento} -- van {len(lecturas)}/6. Faltan: {faltantes} ---")
        input("Acomoda el sensor en una orientacion NUEVA, dejalo quieto, y presiona Enter...")

        promedio = leer_accraw_promedio(ser, DURACION_POR_POSE_S)
        if promedio is None:
            print("No se recibieron datos validos (revisa que el sketch tenga el campo AccRaw). Reintenta esta pose.")
            intento -= 1
            continue

        eje, signo, valor = eje_dominante(promedio)
        clave = (eje, signo)
        print(f"  Detectado: eje {eje}{signo}  (valor={valor:+.1f} mg, vector completo={tuple(round(v,1) for v in promedio)})")

        if abs(valor) < 700:
            print("  AVISO: la lectura del eje dominante es baja para ser 1g (~1000 mg) -- "
                  "revisa que el sensor este realmente quieto y bien apoyado (no inclinado a la mitad). Reintenta esta pose.")
            continue

        if clave in lecturas:
            print(f"  Esa cara (eje {eje}{signo}) ya la habias hecho antes -- prueba una orientacion distinta.")
            continue

        lecturas[clave] = promedio

    # bias por eje = promedio de la lectura EN ESE EJE cuando aparece como +dominante y como -dominante
    bias = {}
    for eje in ("X", "Y", "Z"):
        idx = {"X": 0, "Y": 1, "Z": 2}[eje]
        val_pos = lecturas[(eje, "+")][idx]
        val_neg = lecturas[(eje, "-")][idx]
        bias[eje] = (val_pos + val_neg) / 2.0
        print(f"\nEje {eje}: lectura en pose '+' = {val_pos:+.1f} mg, en pose '-' = {val_neg:+.1f} mg "
              f"-> sesgo (offset) = {bias[eje]:+.1f} mg")

    print("\nOffsets calculados (mg): "
          f"X={bias['X']:+.1f}  Y={bias['Y']:+.1f}  Z={bias['Z']:+.1f}")

    comando = f"a{bias['X']:.1f},{bias['Y']:.1f},{bias['Z']:.1f}\n"
    print(f"\nEnviando al ESP32: {comando.strip()}")
    ser.write(comando.encode("utf-8"))
    time.sleep(1.0)

    print("\nRespuesta del ESP32:")
    t0 = time.time()
    while time.time() - t0 < 2.0:
        linea = ser.readline().decode("utf-8", errors="replace").strip()
        if linea:
            print(f"  {linea}")

    print(
        "\nListo. La calibracion quedo guardada en la flash del ESP32 -- no hace\n"
        "falta repetir esto cada vez que lo enciendas. Corre log_csv_bno055.py\n"
        "de nuevo con el sensor quieto y compara la desviacion estandar de\n"
        "roll/pitch contra tus pruebas anteriores para confirmar la mejora."
    )

    ser.close()


if __name__ == "__main__":
    main()
