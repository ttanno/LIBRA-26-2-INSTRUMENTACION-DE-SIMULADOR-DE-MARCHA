"""
Soporte del ToF2 para T-ToF4 (interferencia entre los dos VL53L1X).
Se fija con 2x M3 a los dos agujeros libres de la repisa de la caja
(CajaPCB v3: (72.7, -86.2) y (72.7, -96.2), bloque de 8 mm, y 9.5-17.5)
y copia EXACTA del asiento del ToF1 (orejas + rebaje del conector),
trasladada DX/DZ, con su cara inferior en y = 9.5: la placa del ToF2
queda en el mismo plano que la del ToF1.
Coordenadas = las del STEP de la caja (mm).
"""
import cadquery as cq

CAJA = "../cajaPCB_v3_snap/CajaPCB_v3_snap.step"
caja = cq.importers.importStep(CAJA).solids().vals()[0]

DX, DZ = 11.0, 28.3          # traslado del asiento respecto al del ToF1
Y_PLANO = 9.5                # cara inferior de la repisa = cara superior de la placa ToF
T_BASE = 3.0                 # placa bajo el bloque
Y_TOP = 14.5                 # tope de la escuadra
X_CARA_BLOQUE = 91.2         # cara exterior del bloque/pared
HOLGURA = 0.4
Z_BLOQ = (-104.0, -78.6)     # extension en z de la cara del bloque
D_M3 = 3.4

# 1) asiento del ToF1 copiado desde la caja (repisa de 2 mm)
recorte = cq.Solid.makeBox(96.5 - 82.5, 11.5 - Y_PLANO, 133.0 - 105.6,
                           pnt=cq.Vector(82.5, Y_PLANO, -133.0))
asiento = caja.intersect(recorte).translate(cq.Vector(DX, 0, DZ))

z0, z1 = Z_BLOQ
xr0 = X_CARA_BLOQUE + HOLGURA
xr1 = 82.5 + DX + 1.5          # escuadra solapa 1.5 mm con el asiento

# 2) placa bajo el bloque, con los 2 agujeros M3
base = cq.Solid.makeBox(xr1 - 66.0, T_BASE, z1 - z0,
                        pnt=cq.Vector(66.0, Y_PLANO - T_BASE, z0))
# 3) escuadra vertical contra la cara del bloque
riser = cq.Solid.makeBox(xr1 - xr0, Y_TOP - (Y_PLANO - T_BASE), z1 - z0,
                         pnt=cq.Vector(xr0, Y_PLANO - T_BASE, z0))
# 4) refuerzo sobre el asiento, entre la escuadra y el rebaje (no toca orejas ni conector)
x_rebaje = 87.4 + DX
refuerzo = cq.Solid.makeBox(x_rebaje - 1.0 - xr0, Y_TOP - 11.5, z1 - z0,
                            pnt=cq.Vector(xr0, 11.5, z0))

pieza = base.fuse(riser).fuse(asiento).fuse(refuerzo).clean()

# agujeros M3 pasantes en la placa base
for z in (-86.2, -96.2):
    cil = cq.Solid.makeCylinder(D_M3 / 2, 20, pnt=cq.Vector(72.7, Y_PLANO - T_BASE - 5, z),
                                dir=cq.Vector(0, 1, 0))
    pieza = pieza.cut(cil)


# chequeos
inter = pieza.intersect(caja).Volume()
print("volumen pieza mm3:", round(pieza.Volume(), 1), " interferencia con la caja:", round(inter, 3))
bb = pieza.BoundingBox()
print(f"bbox x[{bb.xmin:.1f},{bb.xmax:.1f}] y[{bb.ymin:.1f},{bb.ymax:.1f}] z[{bb.zmin:.1f},{bb.zmax:.1f}]")

cq.exporters.export(cq.Workplane().add(pieza), "Soporte_ToF2.step")
cq.exporters.export(cq.Workplane().add(pieza), "Soporte_ToF2.stl")
ens = cq.Assembly().add(caja, name="CajaPCB_v3", color=cq.Color(0.3, 0.6, 0.9)) \
                   .add(pieza, name="Soporte_ToF2", color=cq.Color(0.95, 0.55, 0.1))
ens.save("Ensamble_caja_soporte_ToF2.step")
