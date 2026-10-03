"""
Soporte inclinable con arco indexado para pruebas del IMU (BNO055) a angulos conocidos.
LIBRA - S9. Genera STEP/STL con CadQuery.

Concepto (como una "tilt table" / placa de indexado de taller):
  - BASE + 2 MEJILLAS (una sola pieza): cada mejilla tiene un agujero de pivote y
    un arco de agujeros alrededor de el.
      Fila A (R = 80 mm): 0, 10, 20, 30, 40, 50, 60 grados
      Fila B (R = 66 mm): 5, 15, 25, 35, 45, 55 grados
  - PLATAFORMA (pieza unica): placa superior con alojamiento para el IMU y dos
    alas laterales con el agujero de pivote y dos agujeros de indexado (R=66 y R=80).
  - Pivote e indexado: tornillo M4 x 60 + tuerca (o varilla de 4 mm).

Error angular por holgura ~ holgura / R. Con agujero 4.3 mm y perno 4.0 mm,
el peor caso es ~0.3-0.4 grados, pero es SISTEMATICO (la gravedad apoya siempre
la plataforma sobre el perno del mismo lado), asi que es repetible. Verificar cada
posicion una vez con un inclinometro digital o el del celular y anotar el angulo real.
"""
import math
import cadquery as cq

# ---------------- parametros ----------------
H       = 25.0    # altura del eje de pivote sobre el piso
HOLE    = 4.3     # agujero para perno M4 (impresion)
RA, RB  = 80.0, 66.0
ANG_A   = [0, 10, 20, 30, 40, 50, 60]
ANG_B   = [5, 15, 25, 35, 45, 55]
WP      = 40.0    # ancho de la plataforma (exterior de las alas)
TF      = 5.0     # espesor de cada ala de la plataforma
TP      = 5.0     # espesor de la placa superior
GAP     = 0.5     # juego lateral plataforma-mejilla
TC      = 6.0     # espesor de cada mejilla
RC      = 90.0    # radio exterior del arco de la mejilla
TB      = 6.0     # espesor de la base
LP0, LP1 = -8.0, 95.0          # extension de la plataforma (coord. local x)
ZF0, ZF1 = -8.0, 6.0           # ala: desde z=-8 hasta z=6 (local)
IMU_W, IMU_L, IMU_D = 19.6, 21.6, 1.5   # SEN0374: 19 x 21 mm (+0.6 de juego)
IMU_X   = 50.0    # centro del alojamiento del IMU (coord. local x)
TXT, TXT_D = 4.0, 0.6

Y_IN  = WP / 2 + GAP          # cara interior de la mejilla
Y_OUT = Y_IN + TC             # cara exterior
W_TOT = 2 * Y_OUT

# ---------------- plataforma (en su marco local: pivote en el origen) ----------------
def plataforma():
    # alas: perfil XZ extruido en Y
    ala_prof = (cq.Workplane("XZ").center(0, 0)
                .moveTo(0, ZF0).lineTo(LP1, ZF0).lineTo(LP1, ZF1).lineTo(0, ZF1).close()
                .extrude(-TF))                          # XZ normal es -Y -> extrude(-TF) va a +Y
    disco = cq.Workplane("XZ").circle(8.0).extrude(-TF)
    ala = ala_prof.union(disco)
    ala_izq = ala.translate((0, -WP / 2, 0))
    ala_der = ala.translate((0, WP / 2 - TF, 0))
    placa = (cq.Workplane("XY").box(LP1 - LP0, WP, TP, centered=(False, True, False))
             .translate((LP0, 0, ZF1)))
    p = placa.union(ala_izq).union(ala_der)
    # agujeros transversales (eje Y): pivote + indexado
    for x in (0.0, RB, RA):
        cil = (cq.Workplane("XZ").center(x, 0).circle(HOLE / 2).extrude(WP, both=True))
        p = p.cut(cil)
    # alojamiento del IMU
    zt = ZF1 + TP
    p = p.cut(cq.Workplane("XY").box(IMU_L, IMU_W, IMU_D * 2).translate((IMU_X, 0, zt)))
    # flecha grabada indicando el sentido de inclinacion (+ angulo)
    flecha = (cq.Workplane("XY").workplane(offset=zt)
              .center(IMU_X + 20, 0)
              .polyline([(-6, -1.5), (2, -1.5), (2, -4), (7, 0), (2, 4), (2, 1.5), (-6, 1.5)]).close()
              .extrude(-TXT_D))
    p = p.cut(flecha)
    p = p.cut(cq.Workplane("XY").workplane(offset=zt).center(IMU_X - 20, 0)
              .text("LIBRA", 5, -TXT_D, kind="bold").rotate((0, 0, 0), (0, 0, 1), 0))
    return p

# ---------------- base + mejillas (marco global: pivote en (0, 0, H)) ----------------
def mejilla_perfil():
    pts = [(0, H)]
    for a in range(-12, 73, 2):
        r = math.radians(a)
        pts.append((RC * math.cos(r), H + RC * math.sin(r)))
    sector = cq.Workplane("XZ").polyline(pts).close().extrude(-TC)
    rect = cq.Workplane("XZ").moveTo(-15, 0).lineTo(95, 0).lineTo(95, H).lineTo(-15, H).close().extrude(-TC)
    circ = cq.Workplane("XZ").center(0, H).circle(13).extrude(-TC)
    return sector.union(rect).union(circ)

def base_mejillas():
    base = (cq.Workplane("XY").box(125, W_TOT + 20, TB, centered=(False, True, False))
            .translate((-22, 0, 0)))
    m = mejilla_perfil()
    b = base.union(m.translate((0, Y_IN, 0))).union(m.translate((0, -Y_OUT, 0)))
    # agujeros
    def cil(x, z):
        return cq.Workplane("XZ").center(x, z).circle(HOLE / 2).extrude(W_TOT + 10, both=True)
    b = b.cut(cil(0, H))
    for R, angs in ((RA, ANG_A), (RB, ANG_B)):
        for a in angs:
            r = math.radians(a)
            b = b.cut(cil(R * math.cos(r), H + R * math.sin(r)))
    # etiquetas grabadas en ambas caras exteriores
    for R, angs in ((RA, ANG_A), (RB, ANG_B)):
        rl = R - 7.0
        for a in angs:
            r = math.radians(a)
            x, z = rl * math.cos(r), H + rl * math.sin(r)
            # cara +Y (xDir = -X para que se lea desde afuera)
            plP = cq.Plane(origin=(0, Y_OUT, 0), xDir=(-1, 0, 0), normal=(0, 1, 0))
            b = b.cut(cq.Workplane(plP).center(-x, z).text(str(a), TXT, -TXT_D))
            plN = cq.Plane(origin=(0, -Y_OUT, 0), xDir=(1, 0, 0), normal=(0, -1, 0))
            b = b.cut(cq.Workplane(plN).center(x, z).text(str(a), TXT, -TXT_D))
    return b

def perno(x, z):
    return (cq.Workplane("XZ").center(x, z).circle(2.0).extrude(W_TOT / 2 + 4, both=True))

if __name__ == "__main__":
    import sys
    ang = float(sys.argv[1]) if len(sys.argv) > 1 else 30.0
    P = plataforma()
    B = base_mejillas()
    cq.exporters.export(P, "plataforma_imu.step")
    cq.exporters.export(P, "plataforma_imu.stl", tolerance=0.02, angularTolerance=0.1)
    cq.exporters.export(B, "base_arco_indexado.step")
    cq.exporters.export(B, "base_arco_indexado.stl", tolerance=0.02, angularTolerance=0.1)
    # ensamble de referencia a 'ang' grados
    R = RA if ang in ANG_A else RB
    Pm = P.rotate((0, 0, 0), (0, 1, 0), -ang).translate((0, 0, H))
    a = math.radians(ang)
    asm = (cq.Assembly(name="soporte_angulos_imu")
           .add(B, name="base_arco_indexado", color=cq.Color(0.75, 0.75, 0.78))
           .add(Pm, name="plataforma_imu", color=cq.Color(0.2, 0.45, 0.8))
           .add(perno(0, H), name="perno_pivote_M4", color=cq.Color(0.3, 0.3, 0.3))
           .add(perno(R * math.cos(a), H + R * math.sin(a)), name="perno_indexado_M4",
                color=cq.Color(0.3, 0.3, 0.3)))
    asm.save(f"ensamble_soporte_{int(ang)}grados.step")
    print("ok")
