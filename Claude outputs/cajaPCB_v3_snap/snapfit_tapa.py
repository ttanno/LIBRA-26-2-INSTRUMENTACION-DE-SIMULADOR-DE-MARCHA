# Seguro snap-fit (estilo caja v5) + tapa deslizante para CajaPCB v3
import adsk.core, adsk.fusion, traceback, os
_out = r'C:\Users\aLESS\Documents\LIBRA\_claude_tmp'
_L = []
try:
    app = adsk.core.Application.get()
    des = adsk.fusion.Design.cast(app.activeProduct)
    root = des.rootComponent
    P3 = adsk.core.Point3D.create
    VI = adsk.core.ValueInput
    NB = adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    CUT = adsk.fusion.FeatureOperations.CutFeatureOperation
    JOIN = adsk.fusion.FeatureOperations.JoinFeatureOperation
    cm = lambda mm: mm / 10.0

    # ---- geometria de los rieles medida en Body1 (mm)
    GY0, GY1 = 54.85, 57.85          # alto de la ranura
    ZN, ZF = -145.8, -70.9           # fondo de la ranura: pared cercana / lejana
    XOPEN, XSTOP = -39.5, -3.8       # entrada (abierta) y tope
    # ---- tapa (mismos criterios que v5)
    CL = 0.25                        # holgura por lado
    T = (GY1 - GY0) - 2 * CL         # 2.5 mm
    LY0 = GY0 + CL                   # 55.10
    LZ0, LZ1 = ZN + CL, ZF - CL      # -145.55 .. -71.15
    LX0, LX1 = XOPEN, XSTOP - CL     # -39.5 .. -4.05
    XB = -29.0                       # posicion del seguro (cerca de la entrada)
    BEAM_W, SLOT_W, SLOT_L = 2.25, 1.0, 16.0
    R_BUMP, BUMP_IN, R_DIMPLE = 0.8, 0.2, 0.9

    box = root.bRepBodies.itemByName('Body1')
    for b in root.bRepBodies:
        if b.name == 'Tapa':
            raise Exception('Ya existe un cuerpo Tapa: no se vuelve a ejecutar')
    vol0 = box.volume

    def plane_at(y_mm, name):
        ci = root.constructionPlanes.createInput()
        ci.setByOffset(root.xZConstructionPlane, VI.createByReal(cm(y_mm)))
        p = root.constructionPlanes.add(ci); p.name = name
        return p

    def sketch_on(plane, name):
        sk = root.sketches.add(plane); sk.name = name
        return sk

    def sp(sk, x, y, z):
        return sk.modelToSketchSpace(P3(cm(x), cm(y), cm(z)))

    def rect(sk, y, x0, x1, z0, z1):
        sk.sketchCurves.sketchLines.addTwoPointRectangle(sp(sk, x0, y, z0), sp(sk, x1, y, z1))

    def circ(sk, y, x, z, r):
        sk.sketchCurves.sketchCircles.addByCenterRadius(sp(sk, x, y, z), cm(r))

    def ysign(sk):
        n = sk.xDirection.crossProduct(sk.yDirection)
        return 1.0 if n.y > 0 else -1.0

    def extrude(sk, h_mm, op, name, bodies=None):
        profs = adsk.core.ObjectCollection.create()
        for pr in sk.profiles: profs.add(pr)
        ei = root.features.extrudeFeatures.createInput(profs, op)
        ei.setDistanceExtent(False, VI.createByReal(cm(h_mm) * ysign(sk)))
        if bodies is not None:
            ei.participantBodies = bodies
        f = root.features.extrudeFeatures.add(ei); f.name = name
        return f

    # 1) hoyuelos en el fondo de los dos rieles (caja)
    pg = plane_at(GY0, 'Plano riel (snap)')
    sk = sketch_on(pg, 'Snap - hoyuelos riel')
    circ(sk, GY0, XB, ZN, R_DIMPLE); circ(sk, GY0, XB, ZF, R_DIMPLE)
    extrude(sk, GY1 - GY0, CUT, 'Snap - hoyuelos', [box])

    # 2) tapa deslizante
    pl = plane_at(LY0, 'Plano tapa')
    sk = sketch_on(pl, 'Tapa - contorno')
    rect(sk, LY0, LX0, LX1, LZ0, LZ1)
    f = extrude(sk, T, NB, 'Tapa')
    lid = f.bodies.item(0); lid.name = 'Tapa'

    # 3) ranuras que liberan las vigas flexibles
    sk = sketch_on(pl, 'Tapa - ranuras vigas')
    rect(sk, LY0, XB - SLOT_L/2, XB + SLOT_L/2, LZ0 + BEAM_W, LZ0 + BEAM_W + SLOT_W)
    rect(sk, LY0, XB - SLOT_L/2, XB + SLOT_L/2, LZ1 - BEAM_W - SLOT_W, LZ1 - BEAM_W)
    extrude(sk, T, CUT, 'Tapa - ranuras vigas', [lid])

    # 4) resaltes del seguro en el borde de cada viga
    sk = sketch_on(pl, 'Tapa - resaltes')
    circ(sk, LY0, XB, LZ0 + BUMP_IN, R_BUMP); circ(sk, LY0, XB, LZ1 - BUMP_IN, R_BUMP)
    extrude(sk, T, JOIN, 'Tapa - resaltes', [lid])

    # 5) agarre para deslizarla
    pt = plane_at(LY0 + T, 'Plano agarre tapa')
    sk = sketch_on(pt, 'Tapa - agarre')
    rect(sk, LY0 + T, LX0 + 1.5, LX0 + 4.5, LZ0 + 6, LZ1 - 6)
    extrude(sk, 2.0, JOIN, 'Tapa - agarre', [lid])

    for p in (pg, pl, pt): p.isLightBulbOn = False
    lid = root.bRepBodies.itemByName('Tapa')
    bb = lid.boundingBox
    _L.append('OK')
    _L.append('Body1 vol antes %.1f despues %.1f mm3' % (vol0*1000, box.volume*1000))
    _L.append('Tapa vol %.1f mm3 bb %s %s' % (lid.volume*1000,
        [round(v*10,2) for v in (bb.minPoint.x,bb.minPoint.y,bb.minPoint.z)],
        [round(v*10,2) for v in (bb.maxPoint.x,bb.maxPoint.y,bb.maxPoint.z)]))
    em = des.exportManager
    em.execute(em.createSTEPExportOptions(os.path.join(_out, 'CajaPCB_v3_snap.step'), root))
    _L.append('step exportado')
except:
    _L.append(traceback.format_exc())
open(os.path.join(_out, 'snap_out.txt'), 'w').write('\n'.join(_L))
