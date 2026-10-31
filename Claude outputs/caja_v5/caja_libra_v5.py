"""
Caja de la galleta LIBRA — v5 (modelo paramétrico, CadQuery)

Sistema de coordenadas = el del STEP "Cuerpo" (mm):
  x : a lo ancho (lados cortos de la caja en x = ±49.5)
  y : vertical (cara superior de la placa base en y = 9.5; placa superior y = 79 .. 88.5)
  z : a lo largo (nervio central en z = ±4.75; la caja va de z = 27 a 109)

Piezas que genera:
  caja   : bandeja + paredes + rieles + marco trasero de anclaje
  tapa   : tapa deslizante (entra por +x, seguro por resalte elástico)
  clip_p : clip en C para el borde +x de la placa superior
  clip_n : clip en C para el borde -x de la placa superior

Tornillería: 2x M3x25 + 2 tuercas M3 (anclaje), tornillos M3 por debajo para la galleta
(avellanado Ø7 en los 4 standoffs), M3 + tuerca para la pestaña +x.
"""
import cadquery as cq

# ----------------------------------------------------------------- utilidades
def B(x0, x1, y0, y1, z0, z1):
    x0, x1 = sorted((x0, x1)); y0, y1 = sorted((y0, y1)); z0, z1 = sorted((z0, z1))
    return cq.Solid.makeBox(x1 - x0, y1 - y0, z1 - z0, cq.Vector(x0, y0, z0))

def cylY(x, z, y0, y1, r):
    return cq.Solid.makeCylinder(r, y1 - y0, cq.Vector(x, y0, z), cq.Vector(0, 1, 0))

def cylX(y, z, x0, x1, r):
    return cq.Solid.makeCylinder(r, x1 - x0, cq.Vector(x0, y, z), cq.Vector(1, 0, 0))

def prism_yz(x0, x1, pts):
    """Extruye en x un perfil dado en el plano (y, z)."""
    x0, x1 = sorted((x0, x1))
    return cq.Workplane("YZ", origin=(x0, 0, 0)).polyline(pts).close().extrude(x1 - x0).val()

def prism_xy(z0, z1, pts):
    """Extruye en z un perfil dado en el plano (x, y)."""
    return cq.Workplane("XY", origin=(0, 0, z0)).polyline(pts).close().extrude(z1 - z0).val()

# ----------------------------------------------------------------- parámetros
# entorno (cuerpo de metal, no se perfora)
Y_BASE   = 9.5          # cara superior de la placa base
Y_ROOF_B = 79.0         # cara inferior de la placa superior
Y_ROOF_T = 88.5         # cara superior de la placa superior
X_ROOF   = 40.0         # borde lateral de la placa superior
X_BLK_TOP = 33.5        # bloque superior trasero ocupa |x| <= 33.5

# caja
XO, ZF, ZB = 49.5, 27.0, 109.0          # exterior
XI, ZFI, ZBI = 46.0, 33.5, 105.5        # bolsillo (galleta 90x70)
Y_FLOOR = 12.5                          # piso de 3 mm
SO_X, SO_Z = 41.1, (39.35, 99.65)       # standoffs (82.2 x 60.3)
SO_R, SO_TOP = 4.75, 19.0
SO_HOLE_R, SO_CB_R, SO_CB_TOP = 1.75, 3.5, 14.5
CLEAR = 20.0                            # libre sobre los standoffs
T_LID, CL_LID, G_D = 2.0, 0.25, 1.5
Y_LID0 = SO_TOP + CLEAR                 # 39.0
G0, G1 = Y_LID0 - CL_LID, Y_LID0 + T_LID + CL_LID
Y_WALL = G1 + 1.5                       # 42.75
Y_WALL_PX = 32.5                        # pared +x baja: por ahí entra la tapa
OPEN_PX = 25.0                          # zona abierta arriba en +x (cables)
X_LID_END = XI - OPEN_PX                # 21
WIN = dict(y0=21.0, y1=37.0, z0=36.0, z1=103.0)   # ventana USB-C / borneras en -x
X_DET = 10.0                            # seguro de la tapa

# pestaña +x (2 agujeros horizontales) y desfase de cables en la esquina frontal +x
TAB_TOP, TAB_Z1, TAB_R = 36.0, 54.45, 1.5
TAB_HOLES_Z, TAB_HOLE_Y = (30.45, 50.45), 32.5
TAB_HOLE_R, TAB_BOSS_R, TAB_BOSS_X = 1.8, 3.05, 51.0
SLAB = dict(x0=37.5, z0=24.0, y0=19.0)               # refuerzo delantero (desfase)
NUT_SLOT = dict(x0=39.25, x1=43.75, y0=29.0, y1=36.0)
CABLE_NOTCH = dict(x0=34.5, z0=31.5, y0=36.0)

# marco trasero de anclaje
ZR0, ZR_PLATE, ZR1 = ZB, ZB + 3.0, ZB + 7.0     # placa trasera 3 mm, columnas hasta z = 116
XCOL = 42.0                                     # columnas en |x| = 42 .. 49.5
GAP_ROOF = 0.4
Y_TOP = Y_ROOF_B - GAP_ROOF                     # 78.6
BAR_H = 5.6                                     # travesaño bajo la placa
XS, ZS = (XCOL + XO) / 2, (ZR0 + ZR1) / 2       # tornillos: x = ±45.75, z = 112.5
NUT_AF, NUT_T = 5.8, 2.7

# clips
T_CLIP = 4.5
X_CLIP_IN = X_BLK_TOP + 1.0                     # 34.5: 1 mm del bloque superior

# ----------------------------------------------------------------- caja
def make_box():
    b = B(-XO, XO, Y_BASE, Y_WALL, ZF, ZB)
    # bolsillo
    b = b.cut(B(-XI, XI, Y_FLOOR, 99, ZFI, ZBI))
    # pared +x baja (salvo la pestaña)
    #   (las esquinas frontal y trasera quedan a altura completa, como en la v2)
    b = b.cut(B(XI - 0.01, XO + 1, Y_WALL_PX, 99, CABLE_NOTCH["z0"], ZBI))
    # standoffs de esquina
    for sx in (1, -1):
        for zc in SO_Z:
            sz = 1 if zc < 70 else -1
            zw = ZFI if sz > 0 else ZBI
            blk = cylY(sx * SO_X, zc, Y_FLOOR - 0.01, SO_TOP, SO_R)
            blk = blk.fuse(B(sx * (SO_X - SO_R), sx * XI, Y_FLOOR - 0.01, SO_TOP, zw, zc))
            blk = blk.fuse(B(sx * SO_X, sx * XI, Y_FLOOR - 0.01, SO_TOP, zw, zc + sz * SO_R))
            b = b.fuse(blk)
            b = b.cut(cylY(sx * SO_X, zc, SO_CB_TOP - 0.01, SO_TOP + 1, SO_HOLE_R))
            b = b.cut(cylY(sx * SO_X, zc, Y_BASE - 1, SO_CB_TOP, SO_CB_R))
    # pestaña +x
    tab = prism_yz(XI - 0.01, XO, [(Y_WALL_PX - 0.01, ZF), (Y_WALL_PX - 0.01, TAB_Z1), (TAB_TOP - TAB_R, TAB_Z1),
                                   (TAB_TOP, TAB_Z1 - TAB_R), (TAB_TOP, ZF)])
    b = b.fuse(tab)
    for zc in TAB_HOLES_Z:
        b = b.fuse(cylX(TAB_HOLE_Y, zc, XO - 0.01, TAB_BOSS_X, TAB_BOSS_R))
    # refuerzo delantero de la esquina +x (desfase)
    b = b.fuse(B(SLAB["x0"], XO, SLAB["y0"], Y_WALL, SLAB["z0"], ZF + 0.01))
    # agujeros de la pestaña: el delantero corre dentro de la pared frontal hasta x = 36.5
    b = b.cut(cylX(TAB_HOLE_Y, TAB_HOLES_Z[0], 36.5, TAB_BOSS_X + 1, TAB_HOLE_R))
    b = b.cut(cylX(TAB_HOLE_Y, TAB_HOLES_Z[1], XI - 1, TAB_BOSS_X + 1, TAB_HOLE_R))
    # trampa de tuerca del agujero delantero (abierta por delante)
    b = b.cut(B(NUT_SLOT["x0"], NUT_SLOT["x1"], NUT_SLOT["y0"], NUT_SLOT["y1"], SLAB["z0"] - 1, ZFI))
    # desfase para cables: rebaje interior en la esquina frontal +x
    b = b.cut(B(CABLE_NOTCH["x0"], XO + 1, CABLE_NOTCH["y0"], 99, CABLE_NOTCH["z0"], ZFI + 0.01))
    # rieles de la tapa (frontal, trasero y -x; abiertos en +x)
    b = b.cut(B(-XI - G_D, XO + 5, G0, G1, ZFI - G_D, ZBI + G_D))
    # hoyuelos del seguro
    b = b.cut(cylY(X_DET, ZFI - G_D, G0, G1, 0.9)).cut(cylY(X_DET, ZBI + G_D, G0, G1, 0.9))
    # ventana -x
    b = b.cut(B(-XO - 1, -XI + 0.5, WIN["y0"], WIN["y1"], WIN["z0"], WIN["z1"]))

    # ---- marco trasero de anclaje
    # placa trasera con ventana de alivio de techo a 45° (se imprime sin soportes)
    plate = B(-XO, XO, Y_BASE, Y_TOP, ZR0 - 0.01, ZR_PLATE)
    win_w, win_y0, win_y1 = 30.0, 24.0, 52.0
    plate = plate.cut(prism_xy(ZR0 - 1, ZR_PLATE + 1, [(-win_w, win_y0), (win_w, win_y0), (win_w, win_y1),
                                                         (0, win_y1 + win_w), (-win_w, win_y1)]))
    b = b.fuse(plate)
    # columnas de esquina (chaflán trasero inferior para librar los tetones al entrar)
    for s in (1, -1):
        col = prism_yz(s * XCOL, s * XO, [(Y_BASE + 12, ZR1), (Y_TOP, ZR1), (Y_TOP, ZR0), (Y_BASE, ZR0),
                                          (Y_BASE, ZR_PLATE), (Y_BASE + 12 - (ZR1 - ZR_PLATE), ZR1)])
        b = b.fuse(col)
    # travesaño bajo la placa superior, con chaflán a 45° por debajo
    bar = prism_yz(-XO, XO, [(Y_TOP, ZR0), (Y_TOP, ZR1), (Y_TOP - BAR_H, ZR1),
                            (Y_TOP - BAR_H - (ZR1 - ZR_PLATE), ZR_PLATE), (Y_TOP - BAR_H - (ZR1 - ZR_PLATE), ZR0)])
    b = b.fuse(bar)
    # tornillos M3 verticales + trampas de tuerca (entran por atrás)
    for s in (1, -1):
        b = b.cut(cylY(s * XS, ZS, Y_TOP - 18, Y_TOP + 1, 1.7))
        b = b.cut(B(s * XS - NUT_AF / 2, s * XS + NUT_AF / 2, Y_TOP - 7.0, Y_TOP - 7.0 + NUT_T, ZS - 3.2, ZR1 + 1))

    return b.clean()

# ----------------------------------------------------------------- tapa
def make_lid():
    z0, z1 = ZFI - G_D + CL_LID, ZBI + G_D - CL_LID
    x0 = -XI - G_D + CL_LID
    lid = B(x0, X_LID_END, Y_LID0, Y_LID0 + T_LID, z0, z1)
    for zs in (z0 + 2.25, z1 - 2.25 - 1.0):            # vigas flexibles
        lid = lid.cut(B(X_DET - 8, X_DET + 8, Y_LID0 - 1, Y_LID0 + T_LID + 1, zs, zs + 1.0))
    lid = lid.fuse(cylY(X_DET, z0 + 0.2, Y_LID0, Y_LID0 + T_LID, 0.8))     # resaltes del seguro
    lid = lid.fuse(cylY(X_DET, z1 - 0.2, Y_LID0, Y_LID0 + T_LID, 0.8))
    lid = lid.fuse(B(X_LID_END - 5, X_LID_END - 2, Y_LID0 + T_LID, Y_LID0 + T_LID + 2, ZFI + 6, ZBI - 6))  # agarre
    return lid.clean()

# ----------------------------------------------------------------- clips
def make_clip(s):
    cz0, cz1 = ZR0 - 1.0, ZR1 + 1.0
    c = B(s * X_CLIP_IN, s * XO, Y_ROOF_T, Y_ROOF_T + T_CLIP, cz0, cz1)
    c = c.fuse(B(s * (X_ROOF + 0.3), s * XO, Y_ROOF_B + 0.5, Y_ROOF_T + 0.01, cz0, cz1))
    c = c.cut(cylY(s * XS, ZS, Y_ROOF_B, Y_ROOF_T + T_CLIP + 1, 1.7))
    try:
        c = cq.Workplane().add(c).edges("|Z").edges(">Y").chamfer(0.8).val()
    except Exception:
        pass
    return c.clean()

if __name__ == "__main__":
    caja, tapa = make_box(), make_lid()
    clip_p, clip_n = make_clip(1), make_clip(-1)
    for n, p in (("caja", caja), ("tapa", tapa), ("clip_p", clip_p), ("clip_n", clip_n)):
        cq.exporters.export(cq.Workplane().add(p), f"v5_{n}.step")
        print(n, "válido:", p.isValid(), "vol:", round(p.Volume(), 1))
