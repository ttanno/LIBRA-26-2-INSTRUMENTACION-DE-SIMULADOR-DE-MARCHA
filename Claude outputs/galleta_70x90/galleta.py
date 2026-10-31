"""Galleta (perfboard) 70x90 mm -- placa superior LIBRA (ESP32 + HX711 + Molex).
Genera: vista lado componentes, vista lado soldadura (espejada) y lista de cableado.
Grilla 24 columnas (A..X) x 30 filas (1..30), paso 2.54 mm.
"""
import string
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch, Circle, Polygon
from matplotlib.backends.backend_pdf import PdfPages

W, H, P = 70.0, 90.0, 2.54
NC, NR = 24, 30
X0 = (W - (NC - 1) * P) / 2
Y0 = (H - (NR - 1) * P) / 2
COLS = string.ascii_uppercase[:NC]

def xy(c, r):
    return X0 + (c - 1) * P, Y0 + (r - 1) * P

def name(c, r):
    return f"{COLS[c-1]}{r}"

# ---------------------------------------------------------------- componentes
ESP_L, ESP_R, ESP_R0 = 2, 12, 3     # columnas de headers, fila del pin superior
ESP_LEFT = ["3V3", "GND", "IO15", "IO2", "IO4", "IO16", "IO17", "IO5", "IO18",
            "IO19", "IO21", "RX0", "TX0", "IO22", "IO23"]
ESP_RIGHT = ["VIN", "GND", "IO13", "IO12", "IO14", "IO27", "IO26", "IO25",
             "IO33", "IO32", "IO35", "IO34", "VN", "VP", "EN"]
esp = {}
for i, n in enumerate(ESP_LEFT):
    esp["L" + n] = (ESP_L, ESP_R0 + i)
for i, n in enumerate(ESP_RIGHT):
    esp["R" + n] = (ESP_R, ESP_R0 + i)

HX6_ROW, HX4_ROW = 4, 14
HX6 = dict(zip(["E+", "E-", "A-", "A+", "B-", "B+"], [(c, HX6_ROW) for c in range(18, 24)]))
HX4 = dict(zip(["GND", "DT", "SCK", "VCC"], [(c, HX4_ROW) for c in range(19, 23)]))

J2 = {"+5V": (14, 1), "GND": (16, 1)}                                   # alimentación
J1 = {"E+": (18, 1), "E-": (20, 1), "A-": (22, 1), "A+": (24, 1)}       # celda de carga

MROW = 27
J3 = dict(zip(["3V3", "GND", "SDA2", "SCL2"], [(c, MROW) for c in range(2, 6)]))
J4 = dict(zip(["VCC", "GND", "SCL", "SDA", "INT", "SHUT"], [(c, MROW) for c in range(7, 13)]))
J5 = dict(zip(["VCC", "GND", "SCL", "SDA", "INT", "SHUT"], [(c, MROW) for c in range(14, 20)]))
J6 = dict(zip(["VCC", "GND", "OUT"], [(c, MROW) for c in range(21, 24)]))
R1 = [(20, 23), (24, 23)]

RAIL_3V3 = 25
RAIL_GND = 29

NET_COL = {
    "3V3": "#d62728", "GND": "#222222", "5V": "#ff7f0e",
    "SDA": "#1f77b4", "SCL": "#17becf", "SDA2": "#9467bd", "SCL2": "#e377c2",
    "SHUT1": "#2ca02c", "SHUT2": "#8c564b", "DT": "#bcbd22", "SCK": "#7f7f7f",
    "HALL": "#ff1493", "E+": "#d62728", "E-": "#111111", "A-": "#999999", "A+": "#2ca02c",
}

# ---------------------------------------------------------------- conexiones
# Puentes desnudos (estaño / alambre pelado) por la grilla: (net, [puntos])
bare = [
    ("3V3", [esp["L3V3"], (1, ESP_R0), (1, RAIL_3V3), (23, RAIL_3V3)]),
    ("GND", [(1, RAIL_GND), (24, RAIL_GND)]),
]
for J in (J3, J4, J5, J6):
    pins = list(J.values())
    c1, c2 = pins[0][0], pins[1][0]
    bare.append(("3V3", [(c1, MROW), (c1, RAIL_3V3)]))
    bare.append(("GND", [(c2, MROW), (c2, RAIL_GND)]))
bare.append(("3V3", [R1[0], (R1[0][0], RAIL_3V3)]))
bare.append(("HALL", [J6["OUT"], (24, MROW), R1[1]]))

# Cables aislados punto a punto: (net, desde, hasta, etiqueta desde, etiqueta hasta, ruta opcional)
wires = [
    ("GND", esp["LGND"], (3, RAIL_GND), "ESP GND", "riel GND", [(3, ESP_R0 + 1)]),
    ("GND", esp["RGND"], J2["GND"], "ESP GND", "J2 GND", [(16, ESP_R0 + 1)]),
    ("5V", J2["+5V"], esp["RVIN"], "J2 +5V", "ESP VIN", [(14, ESP_R0)]),
    ("E+", HX6["E+"], J1["E+"], "HX E+", "J1 E+ (rojo)", None),
    ("E-", HX6["E-"], J1["E-"], "HX E-", "J1 E- (negro)", [(19, 2), (20, 2)]),
    ("A-", HX6["A-"], J1["A-"], "HX A-", "J1 A- (blanco)", [(20, 3), (22, 3)]),
    ("A+", HX6["A+"], J1["A+"], "HX A+", "J1 A+ (verde)", [(21, 5), (24, 5)]),
    ("GND", HX4["GND"], (19, RAIL_GND), "HX GND", "riel GND", None),
    ("3V3", HX4["VCC"], (22, RAIL_3V3), "HX VCC", "riel 3V3", None),
    ("DT", esp["RIO32"], HX4["DT"], "IO32", "HX DT", [(14, 12), (14, 16), (20, 16)]),
    ("SCK", esp["RIO33"], HX4["SCK"], "IO33", "HX SCK", [(15, 11), (15, 17), (21, 17)]),
    ("SHUT1", esp["RIO25"], J4["SHUT"], "IO25", "J4 SHUT", [(13, 10), (13, 22), (12, 22)]),
    ("SHUT2", esp["RIO26"], J5["SHUT"], "IO26", "J5 SHUT", [(16, 9), (16, 20), (19, 20)]),
    ("HALL", esp["RIO34"], R1[1], "IO34", "R1 / J6 OUT", [(17, 14), (17, 19), (24, 19)]),
    ("SDA2", esp["LIO17"], J3["SDA2"], "IO17", "J3 SDA2", [(4, 9)]),
    ("SCL2", esp["LIO16"], J3["SCL2"], "IO16", "J3 SCL2", [(5, 8)]),
    ("SDA", esp["LIO21"], J4["SDA"], "IO21", "J4 SDA", [(10, 13)]),
    ("SCL", esp["LIO22"], J4["SCL"], "IO22", "J4 SCL", [(9, 16)]),
    ("SDA", J4["SDA"], J5["SDA"], "J4 SDA", "J5 SDA", [(10, 24), (17, 24)]),
    ("SCL", J4["SCL"], J5["SCL"], "J4 SCL", "J5 SCL", [(9, 23), (16, 23)]),
]

# ---------------------------------------------------------------- verificación
def path_points(pts):
    out = []
    for a, b in zip(pts, pts[1:]):
        (c1, r1), (c2, r2) = a, b
        assert c1 == c2 or r1 == r2, (a, b)
        if c1 == c2:
            step = 1 if r2 >= r1 else -1
            seg = [(c1, r) for r in range(r1, r2 + step, step)]
        else:
            step = 1 if c2 >= c1 else -1
            seg = [(c, r1) for c in range(c1, c2 + step, step)]
        out += seg if not out else seg[1:]
    return out

def check():
    occ = {}
    def put(p, who):
        occ.setdefault(p, set()).add(who)
    for k, v in esp.items(): put(v, "ESP:" + k)
    for nm, J in [("HX6", HX6), ("HX4", HX4), ("J1", J1), ("J2", J2), ("J3", J3),
                  ("J4", J4), ("J5", J5), ("J6", J6)]:
        for k, v in J.items(): put(v, f"{nm}:{k}")
    pin_net = {}
    for net, pts in bare:
        for p in path_points(pts):
            pin_net.setdefault(p, set()).add(net)
    bad = {p: n for p, n in pin_net.items() if len(n) > 1}
    assert not bad, bad
    # un puente desnudo no puede pasar por un pin de otro componente salvo sus extremos
    for net, pts in bare:
        pp = path_points(pts)
        for p in pp[1:-1]:
            if p in occ and p not in pts:
                raise SystemExit(f"puente {net} pasa por pin {occ[p]} en {name(*p)}")
    for p in [x for J in (esp, HX6, HX4, J1, J2, J3, J4, J5, J6) for x in J.values()]:
        assert 1 <= p[0] <= NC and 1 <= p[1] <= NR, p
    print("OK: sin cortos entre puentes desnudos")

check()

# ---------------------------------------------------------------- dibujo
def draw_board(ax, mirror, title):
    tx = (lambda x: W - x) if mirror else (lambda x: x)
    ax.set_xlim(-9, W + 4); ax.set_ylim(H + 4, -9); ax.set_aspect("equal"); ax.axis("off")
    ax.add_patch(FancyBboxPatch((0, 0), W, H, boxstyle="round,pad=0,rounding_size=1.5",
                                fc="#e9d9a8" if not mirror else "#d8c38c", ec="#6b5a2b", lw=1.2, zorder=0))
    for (mx, my) in [(2.8, 2.8), (W - 2.8, 2.8), (2.8, H - 2.8), (W - 2.8, H - 2.8)]:
        ax.add_patch(Circle((tx(mx), my), 1.5, fc="white", ec="#6b5a2b", lw=0.8, zorder=1))
    for c in range(1, NC + 1):
        for r in range(1, NR + 1):
            x, y = xy(c, r)
            ax.add_patch(Circle((tx(x), y), 0.85, fc="#c98b3d" if mirror else "#d9a35a", ec="none", zorder=1))
            ax.add_patch(Circle((tx(x), y), 0.45, fc="white", ec="none", zorder=1))
    for c in range(1, NC + 1):
        x, _ = xy(c, 1)
        ax.text(tx(x), -2.0, COLS[c-1], ha="center", va="center", fontsize=4.6, color="#333")
        ax.text(tx(x), H + 2.0, COLS[c-1], ha="center", va="center", fontsize=4.6, color="#333")
    for r in range(1, NR + 1):
        _, y = xy(1, r)
        ax.text(-2.2 if not mirror else -2.2, y, str(r), ha="center", va="center", fontsize=4.6, color="#333")
        ax.text(W + 2.2, y, str(r), ha="center", va="center", fontsize=4.6, color="#333")
    ax.text(W / 2, -6.5, title, ha="center", va="center", fontsize=8.5, weight="bold")
    return tx

def rect(ax, tx, x1, y1, x2, y2, **kw):
    a, b = sorted([tx(x1), tx(x2)])
    ax.add_patch(Rectangle((a, y1), b - a, y2 - y1, **kw))

def pin_sq(ax, tx, c, r, color="#444", z=4):
    x, y = xy(c, r)
    ax.add_patch(Rectangle((tx(x) - 0.75, y - 0.75), 1.5, 1.5, fc=color, ec="none", zorder=z))

def draw_components(ax, tx, ghost=False):
    a = 0.25 if ghost else 1.0
    ls = "--" if ghost else "-"
    z = 2 if ghost else 3
    # ESP32
    xl, _ = xy(ESP_L, 1); xr, _ = xy(ESP_R, 1)
    _, yc = xy(1, ESP_R0 + 7)
    bw, bl = 28.33, 51.45
    x1 = (xl + xr) / 2 - bw / 2
    rect(ax, tx, x1, yc - bl / 2, x1 + bw, yc + bl / 2, fc="#1b3d6e" if not ghost else "none",
         ec="#1b3d6e", lw=0.8, ls=ls, alpha=a, zorder=z)
    if not ghost:
        rect(ax, tx, (xl + xr) / 2 - 4, yc - bl / 2 - 1.2, (xl + xr) / 2 + 4, yc - bl / 2 + 4.5,
             fc="#b8b8b8", ec="#666", lw=0.6, zorder=z + 0.1)
        ax.text(tx((xl + xr) / 2), yc - bl / 2 + 1.7, "USB", ha="center", va="center", fontsize=4.5, zorder=6)
        ax.text(tx((xl + xr) / 2), yc + bl / 2 - 4.5, "ESP32-WROOM-32U\nDevKit 30 pines\n(U.FL abajo)",
                ha="center", va="center", fontsize=4.6, color="white", zorder=6)
        for k, (c, r) in esp.items():
            pin_sq(ax, tx, c, r, "#f2c94c")
            x, y = xy(c, r)
            inward = 1 if k[0] == "L" else -1
            ax.text(tx(x + inward * 1.6), y, k[1:], ha="left" if inward == 1 else "right", va="center",
                    fontsize=3.9, color="white", zorder=6)
    # HX711
    hx1, _ = xy(18, 1); hx2, _ = xy(23, 1)
    _, hy1 = xy(1, HX6_ROW); _, hy2 = xy(1, HX4_ROW)
    cx = (hx1 + hx2) / 2
    rect(ax, tx, cx - 10.5, hy1 - 2.6, cx + 10.5, hy2 + 2.6, fc="#2e7d32" if not ghost else "none",
         ec="#2e7d32", lw=0.8, ls=ls, alpha=a, zorder=z)
    if not ghost:
        ax.text(tx(cx), (hy1 + hy2) / 2, "HX711\n(XFW-HX711)", ha="center", va="center", fontsize=5.5,
                color="white", zorder=6)
        for dct, dy in ((HX6, 1.7), (HX4, -1.7)):
            for k, (c, r) in dct.items():
                pin_sq(ax, tx, c, r, "#f2c94c")
                x, y = xy(c, r)
                ax.text(tx(x), y + dy, k, ha="center", va="center", fontsize=3.6, color="white", zorder=6,
                        rotation=90)
    # Borneras KF301 (paso 5.08)
    def bornera(pins, label, labels):
        xs = [xy(c, r)[0] for c, r in pins]; y = xy(*pins[0])[1]
        for i in range(0, len(xs), 2):
            rect(ax, tx, xs[i] - 2.5, y - 4.4, xs[i + 1] + 2.5, y + 3.2,
                 fc="#1565c0" if not ghost else "none", ec="#0d3c7a", lw=0.7, ls=ls, alpha=a, zorder=z)
        if not ghost:
            for (c, r), t in zip(pins, labels):
                pin_sq(ax, tx, c, r, "#cfd8dc")
                x, yy = xy(c, r)
                ax.text(tx(x), yy + 2.0, t, ha="center", va="center", fontsize=3.8, color="white", zorder=6)
            ax.text(tx((xs[0] + xs[-1]) / 2), y - 2.7, label, ha="center", va="center", fontsize=4.3,
                    color="white", zorder=6, weight="bold")
    bornera(list(J2.values()), "J2 5V", ["+5V", "GND"])
    bornera(list(J1.values()), "J1 CELDA", ["E+", "E-", "A-", "A+"])
    # Molex KK 2.54
    def molex(J, label):
        pins = list(J.values())
        xa = xy(*pins[0])[0]; xb = xy(*pins[-1])[0]; y = xy(*pins[0])[1]
        rect(ax, tx, xa - 1.27, y - 2.4, xb + 1.27, y + 3.4, fc="#f5f5f5" if not ghost else "none",
             ec="#555", lw=0.7, ls=ls, alpha=a, zorder=z)
        if not ghost:
            rect(ax, tx, xa - 0.5, y + 2.5, xb + 0.5, y + 3.4, fc="#bbb", ec="none", zorder=z + 0.1)
            for i, (k, (c, r)) in enumerate(J.items()):
                pin_sq(ax, tx, c, r, "#f2c94c")
                x, yy = xy(c, r)
                ax.text(tx(x), yy - 1.55, k, ha="center", va="bottom", fontsize=3.3, rotation=90, zorder=6)
            ax.add_patch(Polygon([(tx(xa) - 0.9, y + 1.3), (tx(xa) + 0.9, y + 1.3), (tx(xa), y + 2.3)],
                                 fc="#d62728", zorder=6))
            ax.text(tx((xa + xb) / 2), y + 5.0, label, ha="center", va="center", fontsize=4.6, weight="bold")
    molex(J3, "J3 IMU (BNO055)")
    molex(J4, "J4 ToF1")
    molex(J5, "J5 ToF2")
    molex(J6, "J6 HALL")
    # R1
    (c1, r1), (c2, r2) = R1
    xa, ya = xy(c1, r1); xb, _ = xy(c2, r2)
    if not ghost:
        ax.plot([tx(xa), tx(xb)], [ya, ya], color="#777", lw=0.8, zorder=3)
        rect(ax, tx, xa + 2.0, ya - 0.9, xb - 2.0, ya + 0.9, fc="#e8c39e", ec="#8d6e63", lw=0.6, zorder=4)
        ax.text(tx((xa + xb) / 2), ya - 1.9, "R1 10k", ha="center", va="center", fontsize=4.3, zorder=6)
        pin_sq(ax, tx, c1, r1); pin_sq(ax, tx, c2, r2)

def draw_wiring(ax, tx):
    for net, pts in bare:
        pp = [xy(*p) for p in pts]
        ax.plot([tx(x) for x, _ in pp], [y for _, y in pp], color="#9e9e9e", lw=3.2,
                solid_capstyle="round", zorder=5)
        ax.plot([tx(x) for x, _ in pp], [y for _, y in pp], color=NET_COL.get(net, "#555"), lw=1.0,
                solid_capstyle="round", zorder=5.1)
    for i, (net, a, b, la, lb, via) in enumerate(wires, 1):
        pts = [a] + (via or []) + [b]
        pp = [xy(*p) for p in pts]
        off = ((i % 5) - 2) * 0.12
        ax.plot([tx(x) + off for x, _ in pp], [y + off for _, y in pp], color=NET_COL[net], lw=1.1,
                alpha=0.95, zorder=6, solid_joinstyle="round")
        for p in (a, b):
            x, y = xy(*p)
            ax.add_patch(Circle((tx(x), y), 0.7, fc=NET_COL[net], ec="white", lw=0.4, zorder=7))
        # número del cable en el punto medio de su tramo más largo
        segs = list(zip(pp, pp[1:]))
        (sa, sb) = max(segs, key=lambda s: abs(s[0][0] - s[1][0]) + abs(s[0][1] - s[1][1]))
        mx, my = (sa[0] + sb[0]) / 2, (sa[1] + sb[1]) / 2
        ax.text(tx(mx), my, str(i), fontsize=4.2, ha="center", va="center", zorder=8,
                bbox=dict(boxstyle="circle,pad=0.12", fc="white", ec=NET_COL[net], lw=0.6))
    ax.text(tx(xy(1, RAIL_3V3)[0]) , xy(1, RAIL_3V3)[1] - 1.6, "riel 3V3", fontsize=4.2, color=NET_COL["3V3"],
            ha="left" if tx(0) == 0 else "right", zorder=8)
    ax.text(tx(xy(1, RAIL_GND)[0]), xy(1, RAIL_GND)[1] + 2.0, "riel GND", fontsize=4.2, color="#222",
            ha="left" if tx(0) == 0 else "right", zorder=8)

def wire_table():
    rows = []
    for i, (net, a, b, la, lb, via) in enumerate(wires, 1):
        rows.append((str(i), net, f"{la} ({name(*a)})", f"{lb} ({name(*b)})"))
    return rows

def page(fig, scale_1to1):
    # Dos vistas a escala real arriba, tabla abajo
    axw = (W + 13) / 210; axh = (H + 13) / 297
    ax1 = fig.add_axes([12 / 210, 1 - (H + 30) / 297, axw, axh])
    ax2 = fig.add_axes([(12 + W + 22) / 210, 1 - (H + 30) / 297, axw, axh])
    t1 = draw_board(ax1, False, "LADO COMPONENTES (vista superior)")
    draw_components(ax1, t1)
    t2 = draw_board(ax2, True, "LADO SOLDADURA (espejado) — cableado")
    draw_components(ax2, t2, ghost=True)
    draw_wiring(ax2, t2)
    fig.text(0.5, 1 - 7 / 297, "LIBRA — Galleta 70×90 mm (placa superior: ESP32 + HX711 + Molex)",
             ha="center", fontsize=11, weight="bold")
    fig.text(0.5, 1 - 12 / 297, "Grilla 24×30 agujeros, paso 2.54 mm · columnas A–X, filas 1–30 · "
             "imprimir al 100 % (sin 'ajustar a página') para usar como plantilla",
             ha="center", fontsize=6.5, color="#444")
    fig.text(0.5, 0.03, "LIBRA · placa superior provisional en galleta · v1 · 2026-10-05 · "
             "pinout según Firmware/PCB_placa_superior_PINOUT.md", ha="center", fontsize=5.5, color="#666")
    # cuadro de verificación de escala
    fig.add_artist(Rectangle(((210 - 22) / 210, 1 - 14 / 297), 10 / 210, 10 / 297, transform=fig.transFigure,
                             fc="none", ec="black", lw=0.6))
    fig.text((210 - 17) / 210, 1 - 16.5 / 297, "10 mm", ha="center", fontsize=5)
    # tabla
    rows = wire_table()
    axt = fig.add_axes([10 / 210, 0.17, 120 / 210, 0.40]); axt.axis("off")
    tb = axt.table(cellText=rows, colLabels=["#", "Red", "Desde", "Hasta"], loc="upper left",
                   colWidths=[0.06, 0.12, 0.41, 0.41], cellLoc="left")
    tb.auto_set_font_size(False); tb.set_fontsize(6.2); tb.scale(1, 0.95)
    for (r, c), cell in tb.get_celld().items():
        cell.set_linewidth(0.3)
        if r == 0:
            cell.set_facecolor("#eeeeee"); cell.set_text_props(weight="bold")
        elif c == 1:
            cell.set_text_props(color=NET_COL[rows[r - 1][1]], weight="bold")
    notes = (
        "CABLES AISLADOS (tabla): alambre AWG 26–30, lado soldadura.\n"
        "PUENTES DESNUDOS (gris): estaño o alambre pelado por la grilla:\n"
        " • 3V3: ESP 3V3 (B3)→A3→A25, riel fila 25 (A–W)\n"
        " • GND: riel fila 29 (A–X)\n"
        " • Pin 1 de cada Molex sube al riel 3V3,\n"
        "   pin 2 baja al riel GND (2 agujeros)\n"
        " • R1 izq. (T23)→T25 · J6 OUT (W27)→X27→X23\n\n"
        "ANTES DE SOLDAR — medir y ajustar:\n"
        " • ESP32: separación entre headers. Dibujado a\n"
        "   10 pasos (25.4 mm, B↔L). Si tu placa es de\n"
        "   9 pasos (22.86 mm) el header derecho va en K.\n"
        " • HX711: dibujado con 10 pasos entre header de\n"
        "   6 y de 4 pines (filas 4 y 14). Mueve el de 4\n"
        "   pines a la fila que caiga; los cables 8–11 sólo\n"
        "   cambian de largo.\n"
        " • Orden de pines del ESP32/HX711: confirmar con\n"
        "   la serigrafía de tus módulos.\n"
        " • Montar ESP32 y HX711 sobre headers hembra\n"
        "   (removibles, y deja pasar cables por debajo).\n\n"
        "NOTAS\n"
        " • R1 10k = pull-up del Hall: GPIO34 NO tiene\n"
        "   pull-up interno (INPUT_PULLUP no hace nada).\n"
        " • INT de los ToF y B± del HX711: sin conectar.\n"
        " • Molex KK 2.54 mm; ▼ rojo = pin 1.\n"
        " • J1 queda pegado al agujero de montaje sup.\n"
        "   derecho: tornillo de cabeza chica o no usarlo.\n"
        " • GPIO25/26 = SHUT de los ToF; el sketch de\n"
        "   homing usa 25/26/27 para el driver: reasignar\n"
        "   si ambos van en esta placa."
    )
    fig.text(134 / 210, 0.57, notes, ha="left", va="top", fontsize=5.6, family="DejaVu Sans",
             linespacing=1.35)

if __name__ == "__main__":
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else "."
    fig = plt.figure(figsize=(210 / 25.4, 297 / 25.4))
    page(fig, True)
    with PdfPages(f"{out}/galleta_70x90_LIBRA.pdf") as pdf:
        pdf.savefig(fig)
    fig.savefig(f"{out}/galleta_70x90_LIBRA.png", dpi=300)
    print("listo")
