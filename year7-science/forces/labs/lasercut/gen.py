"""Laser-cut parts for the 4 kg oval trebuchet (6 mm plywood, 900 x 600 bed).

Every size is a parameter below. Run:  python3 gen.py  -> out/*.svg, out/*.dxf, out/*.png
Cut = red hairline (layer CUT). Engrave/score = blue (layer ENGRAVE).
Units: millimetres. Sheet origin bottom-left in the DXF; SVG is y-down as usual.
"""
import os, math
import numpy as np
from shapely.geometry import Polygon, LineString, Point, box, MultiPolygon
from shapely.ops import unary_union
from shapely import affinity
import ezdxf
from matplotlib.textpath import TextPath
from matplotlib.font_manager import FontProperties

# ---------------------------------------------------------------- parameters
SHEET_W, SHEET_H = 900.0, 600.0     # laser bed
EDGE = 6.0                          # keep-clear margin at the sheet edge
GAP = 6.0                           # minimum web between parts
T = 6.0                             # plywood thickness

AXLE_H = 800.0       # axle centre above the panel's bottom edge (= top of base rails)
BOSS_R = 60.0        # radius of the boss round the bearing
FOOT_X = 290.0       # half-width of the panel at the feet
LEG_W = 70.0         # leg width
BAR_Y0, BAR_Y1 = 380.0, 440.0   # crossbar
FOOT_H = 40.0        # foot pad height
FOOT_L = 120.0       # foot pad length
BEARING_CLEAR = 42.0 # clearance hole for the bearing housing boss
BEARING_BOLT_D = 10.5   # M10
BEARING_BOLT_PITCH = 90.0  # 2-bolt flange bearing (UCFL204 pattern) -- CHECK YOURS
DOWEL_D = 6.2        # alignment dowels for gluing the two layers

PIN_D = 10.5         # trigger pin (10 mm rod or bolt)
SCREW_D = 4.5        # wood screws
HANG_BOLT_D = 12.5   # M12 hang bolt through the arm
AXLE_D = 20.5        # 20 mm axle
EYE_D = 6.5          # M6 eye bolts
PILOT_D = 3.0        # pilot holes in drilling templates

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out')
os.makedirs(OUT, exist_ok=True)
FONT = FontProperties(family='DejaVu Sans', weight='bold')

# ---------------------------------------------------------------- helpers
def thick(p0, p1, w):
    return LineString([p0, p1]).buffer(w / 2, cap_style=2, join_style=2)

def fillet(poly, r):          # round inside corners, then outside corners
    return poly.buffer(r, join_style=1).buffer(-r, join_style=1).buffer(-r / 2, join_style=1).buffer(r / 2, join_style=1)

def text_polys(s, x, y, size, anchor='left'):
    tp = TextPath((0, 0), s, size=size, prop=FONT)
    polys = [np.array(p) for p in tp.to_polygons() if len(p) > 2]
    if not polys: return []
    allp = np.vstack(polys)
    w = allp[:, 0].max() - allp[:, 0].min()
    dx = {'left': 0, 'center': -w / 2, 'right': -w}[anchor]
    return [p + np.array([x + dx, y]) for p in polys]

class Part:
    """outline: shapely Polygon (cut). holes: list of (x, y, d) circles (cut).
    cuts: extra closed polylines to cut. engrave: list of polylines (closed or open)."""
    def __init__(self, name, outline, holes=(), engrave=(), cuts=()):
        self.name, self.outline = name, outline
        self.holes = list(holes); self.engrave = list(engrave); self.cuts = list(cuts)
    def transformed(self, angle=0.0, dx=0.0, dy=0.0):
        def tp(x, y):
            c, s = math.cos(math.radians(angle)), math.sin(math.radians(angle))
            return (c * x - s * y + dx, s * x + c * y + dy)
        o = affinity.translate(affinity.rotate(self.outline, angle, origin=(0, 0)), dx, dy)
        h = [(*tp(x, y), d) for x, y, d in self.holes]
        e = [np.array([tp(*q) for q in pl]) for pl in self.engrave]
        c = [np.array([tp(*q) for q in pl]) for pl in self.cuts]
        return Part(self.name, o, h, e, c)
    def solid(self):
        g = self.outline
        for x, y, d in self.holes:
            g = g.difference(Point(x, y).buffer(d / 2, 64))
        return g

def cross(x, y, s=6):
    return [np.array([[x - s, y], [x + s, y]]), np.array([[x, y - s], [x, y + s]])]

# ---------------------------------------------------------------- parts
def side_panel(label):
    axle = (0.0, AXLE_H)
    legs = [thick((sx * (FOOT_X - LEG_W / 2), 0.0), axle, LEG_W) for sx in (-1, 1)]
    feet = [box(sx * FOOT_X - (FOOT_L if sx > 0 else 0), 0, sx * FOOT_X + (0 if sx > 0 else FOOT_L), FOOT_H) for sx in (-1, 1)]
    bar = box(-FOOT_X, BAR_Y0, FOOT_X, BAR_Y1)
    boss = Point(axle).buffer(BOSS_R, 64)
    g = unary_union(legs + feet + [boss])
    # crossbar only between the legs' outer edges
    g = unary_union([g, bar.intersection(unary_union(legs).convex_hull)])
    g = g.intersection(box(-FOOT_X, 0, FOOT_X, AXLE_H + BOSS_R))
    g = fillet(g, 18)
    holes = [(0, AXLE_H, BEARING_CLEAR),
             (-BEARING_BOLT_PITCH / 2, AXLE_H, BEARING_BOLT_D),
             (BEARING_BOLT_PITCH / 2, AXLE_H, BEARING_BOLT_D)]
    # dowels: one per leg, two on the crossbar ends
    for sx in (-1, 1):
        t = 0.30
        holes.append((sx * (FOOT_X - LEG_W / 2) * (1 - t), AXLE_H * t, DOWEL_D))
        t = 0.75
        holes.append((sx * (FOOT_X - LEG_W / 2) * (1 - t), AXLE_H * t, DOWEL_D))
    eng = []
    for sx in (-1, 1):          # foot bracket marks
        fx = sx * (FOOT_X - FOOT_L / 2)
        eng += cross(fx - 30, FOOT_H / 2) + cross(fx + 30, FOOT_H / 2)
    bx = 0.0                    # brace bracket mark on the crossbar centre (outer face)
    eng += cross(bx - 20, (BAR_Y0 + BAR_Y1) / 2) + cross(bx + 20, (BAR_Y0 + BAR_Y1) / 2)
    eng += text_polys(label, 0, BAR_Y0 + 12, 13, 'center')
    eng += text_polys('axle', 0, AXLE_H - BOSS_R + 6, 8, 'center')
    return Part('side_panel', g, holes, eng)

def trigger_layer(kind):
    """3 layers glued face to face; tabs into the base plate. kind: 'outer' | 'middle'"""
    w, h, tab_w, tab_d = 120.0, 70.0, 30.0, T
    body = box(-w / 2, 0, w / 2, h)
    tabs = [box(x - tab_w / 2, -tab_d, x + tab_w / 2, 0) for x in (-35, 35)]
    g = unary_union([body] + tabs)
    if kind == 'middle':
        g = g.difference(box(-11, 25, 11, h + 1))      # slot for the cord loop
    g = fillet(g, 2)
    eng = text_polys('TRIGGER ' + ('MID' if kind == 'middle' else 'OUTER'), 0, 8, 7, 'center')
    return Part('trigger_' + kind, g, [(0, 45, PIN_D)], eng)

def trigger_base():
    w, h = 170.0, 90.0
    g = fillet(box(-w / 2, -h / 2, w / 2, h / 2), 4)
    slots = [box(x - 15.2, -9.3, x + 15.2, 9.3) for x in (-35, 35)]   # 3 layers = 18 mm + clearance
    for s in slots: g = g.difference(s)
    holes = [(sx * 70, sy * 32, SCREW_D) for sx in (-1, 1) for sy in (-1, 1)]
    eng = text_polys('TRIGGER BASE', 0, 26, 7, 'center')
    return Part('trigger_base', g, holes, eng)

def sensor_plate():
    w, h = 110.0, 56.0
    g = fillet(box(-w / 2, -h / 2, w / 2, h / 2), 5)
    for x in (-45, 45):        # strap slots round the arm
        g = g.difference(box(x - 2.2, -14, x + 2.2, 14))
    for y in (-20, 20):        # strap slots round the sensor
        g = g.difference(box(-28, y - 2.2, 28, y + 2.2))
    eng = text_polys('SENSOR', 0, -4, 7, 'center')
    return Part('sensor_plate', g, [], eng)

def arm_end_template():
    """Lies on the 40 mm side face of the arm, flush with the counterweight end."""
    L0, w = 470.0, 40.0
    g = fillet(box(0, -w / 2, L0, w / 2), 2)
    holes = [(50.0, 0, PILOT_D), (400.0, 0, PILOT_D)]
    eng = [np.array([[0.8, -w / 2 + 1], [0.8, w / 2 - 1]])]
    for x, d in ((50.0, HANG_BOLT_D), (400.0, AXLE_D)):
        t = np.linspace(0, 2 * np.pi, 60)
        eng.append(np.c_[x + d / 2 * np.cos(t), d / 2 * np.sin(t)])
    eng += text_polys('END', 6, -4, 7) + text_polys('hang bolt M12', 70, 6, 6) + text_polys('axle 20', 420, 6, 6)
    eng += text_polys('ARM END TEMPLATE - flush with end', 120, -14, 6)
    return Part('arm_end_template', g, holes, eng)

def arm_tip_template():
    """Lies on the 20 mm sling-side face, flush with the tip end. Flip for the trigger eye."""
    L0, w = 140.0, 20.0
    g = fillet(box(-L0, -w / 2, 0, w / 2), 2)
    holes = [(-30.0, 0, PILOT_D), (-100.0, 0, PILOT_D)]
    eng = [np.array([[-0.8, -w / 2 + 1], [-0.8, w / 2 - 1]])]
    eng += text_polys('TIP', -22, -3.5, 6) + text_polys('sling eye', -82, -3.5, 5)
    eng += text_polys('trigger', -136, -3.5, 5)
    return Part('arm_tip_template', g, holes, eng)

def doubler_template(kind):
    """Marking/drilling template for the 6 mm ALUMINIUM doubler plates (not cut on this laser)."""
    w, h = 120.0, 40.0
    g = fillet(box(-w / 2, -h / 2, w / 2, h / 2), 3)
    centre = AXLE_D if kind == 'axle' else HANG_BOLT_D
    holes = [(0, 0, PILOT_D)] + [(sx * 45, 0, PILOT_D) for sx in (-1, 1)]
    t = np.linspace(0, 2 * np.pi, 60)
    eng = [np.c_[centre / 2 * np.cos(t), centre / 2 * np.sin(t)]]
    eng += text_polys(('AXLE' if kind == 'axle' else 'HANG') + ' DOUBLER x2', 0, 10, 5.5, 'center')
    eng += text_polys('M5 bolts', 45, -16, 4.5, 'center') + text_polys('M5 bolts', -45, -16, 4.5, 'center')
    return Part('doubler_' + kind, g, holes, eng)

def test_coupon():
    w, h = 150.0, 60.0
    g = fillet(box(0, 0, w, h), 3)
    holes, eng = [], []
    for i, d in enumerate([19.8, 20.2, 20.6, 21.0]):
        holes.append((18 + i * 30, 40, d))
        eng += text_polys(f'{d:.1f}', 18 + i * 30, 22, 5, 'center')
    # three slot widths for the trigger tabs (18 mm stack) and one tab
    for i, sw in enumerate([18.2, 18.6, 19.0]):
        s = box(12 + i * 30 - 2, 4, 12 + i * 30 + sw - 2, 14)
        g = g.difference(s)
    for i, d in enumerate([10.3, 10.5, 10.8]):
        holes.append((120 + 0 * i, 0, 0)) if False else None
    for i, d in enumerate([10.3, 10.6]):
        holes.append((132, 15 + i * 26, d))
        eng += text_polys(f'{d:.1f}', 132, 5 + i * 26 + (0 if i == 0 else 16), 4, 'center')
    eng += text_polys('FIT TEST', 75, 52, 6, 'center')
    return Part('test_coupon', g, holes, eng)

def pouch():
    """Sling pouch, cut from canvas or leather (separate fabric file)."""
    a, b = 60.0, 38.0
    t = np.linspace(0, 2 * np.pi, 120)
    g = Polygon(np.c_[a * np.cos(t), b * np.sin(t)])
    g = unary_union([g, box(-a - 14, -9, -a + 4, 9), box(a - 4, -9, a + 14, 9)])
    g = fillet(g, 4)
    holes = [(-a - 5, 0, 6.0), (a + 5, 0, 6.0), (0, 0, 8.0)]
    return Part('pouch', g, holes, [])

# ---------------------------------------------------------------- nesting
def free_region(placed):
    sheet = box(EDGE, EDGE, SHEET_W - EDGE, SHEET_H - EDGE)
    used = unary_union([p.solid().buffer(GAP) for p in placed]) if placed else Polygon()
    return sheet.difference(used)

def place(part, placed, angles=(0, 90, 180, 270), step=4.0, prefer='bl'):
    region = free_region(placed)
    best = None
    for ang in angles:
        q = part.transformed(ang)
        minx, miny, maxx, maxy = q.outline.bounds
        for yy in np.arange(EDGE - miny, SHEET_H - EDGE - maxy + 1e-6, step):
            for xx in np.arange(EDGE - minx, SHEET_W - EDGE - maxx + 1e-6, step):
                shape = affinity.translate(q.outline, xx, yy)
                if region.contains(shape):
                    score = (yy + xx * 0.25) if prefer == 'bl' else (-yy + xx * 0.25)
                    if best is None or score < best[0]:
                        best = (score, ang, xx, yy)
                    break
    if best is None:
        raise RuntimeError(f'could not place {part.name}')
    _, ang, xx, yy = best
    return part.transformed(ang, xx, yy)

def panel_on_sheet(label):
    p = side_panel(label)
    # panel height runs along the 900 mm direction, centred on the 600 mm direction
    q = p.transformed(-90)
    minx, miny, maxx, maxy = q.outline.bounds
    dx = EDGE - minx + ((SHEET_W - 2 * EDGE) - (maxx - minx)) / 2
    dy = EDGE - miny + ((SHEET_H - 2 * EDGE) - (maxy - miny)) / 2
    return q.transformed(0, dx, dy)

# ---------------------------------------------------------------- output
def write(name, parts, title, w=SHEET_W, h=SHEET_H):
    # DXF
    doc = ezdxf.new('R2010', setup=True); doc.units = ezdxf.units.MM
    doc.layers.add('CUT', color=1); doc.layers.add('ENGRAVE', color=5)
    msp = doc.modelspace()
    def poly_rings(g):
        geoms = g.geoms if isinstance(g, MultiPolygon) else [g]
        for gg in geoms:
            yield list(gg.exterior.coords)
            for r in gg.interiors: yield list(r.coords)
    for p in parts:
        for ring in poly_rings(p.outline):
            msp.add_lwpolyline(ring, close=True, dxfattribs={'layer': 'CUT'})
        for x, y, d in p.holes:
            msp.add_circle((x, y), d / 2, dxfattribs={'layer': 'CUT'})
        for pl in p.cuts:
            msp.add_lwpolyline(pl.tolist(), close=True, dxfattribs={'layer': 'CUT'})
        for pl in p.engrave:
            closed = np.allclose(pl[0], pl[-1]) or len(pl) > 8
            msp.add_lwpolyline(pl.tolist(), close=bool(closed), dxfattribs={'layer': 'ENGRAVE'})
    doc.saveas(os.path.join(OUT, name + '.dxf'))
    # SVG (y flipped so it matches the DXF)
    def P(x, y): return f'{x:.3f},{h - y:.3f}'
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}mm" height="{h}mm" viewBox="0 0 {w} {h}">',
           f'<title>{title}</title>',
           '<g id="CUT" fill="none" stroke="#FF0000" stroke-width="0.1">']
    for p in parts:
        for ring in poly_rings(p.outline):
            out.append('<path d="M' + ' L'.join(P(*c) for c in ring) + ' Z"/>')
        for x, y, d in p.holes:
            out.append(f'<circle cx="{x:.3f}" cy="{h - y:.3f}" r="{d / 2:.3f}"/>')
        for pl in p.cuts:
            out.append('<path d="M' + ' L'.join(P(*c) for c in pl) + ' Z"/>')
    out.append('</g><g id="ENGRAVE" fill="none" stroke="#0000FF" stroke-width="0.1">')
    for p in parts:
        for pl in p.engrave:
            out.append('<path d="M' + ' L'.join(P(*c) for c in pl) + '"/>')
    out.append('</g></svg>')
    with open(os.path.join(OUT, name + '.svg'), 'w') as f:
        f.write('\n'.join(out))
    # preview with sheet outline
    prev = list(out)
    prev.insert(2, f'<rect x="0" y="0" width="{w}" height="{h}" fill="#F3EBDD" stroke="#888" stroke-width="1"/>')
    prev = [l.replace('stroke-width="0.1"', 'stroke-width="0.8"') for l in prev]
    import cairosvg
    cairosvg.svg2png(bytestring='\n'.join(prev).encode(), write_to=os.path.join(OUT, name + '.png'),
                     output_width=1350)
    cairosvg.svg2pdf(bytestring='\n'.join(prev).encode(), write_to=os.path.join(OUT, name + '_preview.pdf'))

def check(parts, w=SHEET_W, h=SHEET_H):
    sheet = box(0, 0, w, h)
    for p in parts:
        assert sheet.contains(p.outline), f'{p.name} off the sheet'
    for i in range(len(parts)):
        for j in range(i + 1, len(parts)):
            a, b = parts[i].solid(), parts[j].solid()
            assert a.distance(b) >= GAP - 0.01, f'{parts[i].name} too close to {parts[j].name}'

if __name__ == '__main__':
    small = {
        1: [trigger_layer('outer'), trigger_layer('middle'), trigger_layer('outer'), trigger_base()],
        2: [arm_end_template(), arm_tip_template()],
        3: [sensor_plate(), sensor_plate()],
        4: [doubler_template('axle'), doubler_template('hang')],
    }
    labels = {1: 'SIDE A - LAYER 1', 2: 'SIDE A - LAYER 2', 3: 'SIDE B - LAYER 1', 4: 'SIDE B - LAYER 2'}
    for n in (1, 2, 3, 4):
        parts = [panel_on_sheet(labels[n])]
        for sp in small[n]:
            parts.append(place(sp, parts))
        check(parts)
        write(f'0{n}_Sheet_{labels[n].replace(" - ", "_").replace(" ", "_")}', parts,
              f'Trebuchet laser parts - sheet {n} of 4 - 6 mm ply - {labels[n]}')
        print('sheet', n, [p.name for p in parts])
    c = test_coupon().transformed(0, 5, 5)
    check([c], 160, 70)
    write('00_Test_coupon_cut_first', [c], 'Fit test coupon - cut first', 160, 70)
    pts = []
    for i in range(6):
        pts.append(pouch().transformed(0, 80 + (i % 3) * 160, 55 + (i // 3) * 100))
    check(pts, 480, 210)
    write('05_Fabric_sling_pouches', pts, 'Sling pouches - canvas or leather', 480, 210)
    print('done')
