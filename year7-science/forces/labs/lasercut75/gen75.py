"""Knock-down 75 % trebuchet -- laser-cut parts, 6 mm plywood, 900 x 600 bed.

Everything is a 2-layer (12 mm) laminate. Each SIDE UNIT (A-frame + rail + gussets + top cap)
is glued up once and never taken apart. Between sessions the machine comes apart into:
2 side units, 3 cross members, 2 braces, the arm unit (arm + axle + pillow blocks + sling).

Global axes:  X across (along the axle), Y fore-aft (+Y = throwing direction), Z up (0 = top of rails).
Run:  python3 gen75.py   ->  out/*.dxf, out/*.svg, out/*.png, out/*_preview.pdf
Cut = red (layer CUT), engrave = blue (layer ENGRAVE). Units mm.
"""
import os, math
import numpy as np
from shapely.geometry import Polygon, LineString, Point, box, MultiPolygon
from shapely.ops import unary_union
from shapely.prepared import prep
from shapely import affinity
import ezdxf
from matplotlib.textpath import TextPath
from matplotlib.font_manager import FontProperties

# ------------------------------------------------------------------ parameters
SHEET_W, SHEET_H = 900.0, 600.0
EDGE, GAP = 6.0, 6.0          # keep-clear at sheet edge; web between parts
T = 6.0                       # ply thickness; every structural part is 2 layers
TT = 2 * T                    # laminate thickness
FIT = 0.6                     # extra width on slots that take a 12 mm laminate (change after the fit test)

# trebuchet geometry (75 % of the 1 m oval build)
L_ARM = 750.0                 # pivot to release pin
A_ARM = 262.5                 # pivot to hang bolt
HANG = 210.0                  # hang bolt to the centre of the sand bag
AXLE_Z = 600.0                # axle centre above the rail tops
GAP_X = 270.0                 # inside faces of the two sides
SIDE_X0 = GAP_X / 2           # inner face of a side unit
SIDE_X1 = SIDE_X0 + TT        # outer face

# pillow block (UCP204, 20 mm bore) -- CHECK YOURS before cutting
PB_SHAFT_H = 33.3             # base to shaft centre
PB_BOLT_PITCH = 95.0          # bolt centres along the base
PB_LEN, PB_W = 127.0, 38.0
HEX_AF = 17.2                 # M10 hex head across flats (pocket in lower cap layer)
STUD_D = 10.5

# side panel
FOOT_Y = 217.5                # half width at the feet
LEG_W = 52.0
TOP_HALF = 72.0               # half width of the flat top
BAR_Z0, BAR_Z1 = 285.0, 330.0
CAP_Z = AXLE_Z - PB_SHAFT_H   # top of the cap
PANEL_TOP = CAP_Z - TT        # panel top edge (cap is 2 layers on top)
FOOT_TAB = (157.5, 197.5)     # |Y| range of the foot tabs that drop into the rail
FOOT_TAB_D = 20.0

# base
RAIL_Y = (-600.0, 525.0)      # back and front ends of the rails
RAIL_H = 90.0
XM_Y = {'BACK': -482.0, 'MIDDLE': 0.0, 'FRONT': 470.0}   # cross member positions
XM_HALF = {'BACK': 200.0, 'MIDDLE': 300.0, 'FRONT': 200.0}
XM_LOW = 57.5                 # height of the part of a cross member that passes under a rail
WEDGE_HOLE = (SIDE_X1 - 2.0, SIDE_X1 + 18.0)   # X range of the wedge hole
WEDGE_Z = -RAIL_H + XM_LOW / 2                 # wedge hole centre height
PIN_D = 8.5                   # 8 mm clevis pins
BRACE_Y = TT                  # braces sit beside the middle cross member, Y = 6..18
BRACE_TOP = (SIDE_X1, (BAR_Z0 + BAR_Z1) / 2)
BRACE_BOT = (280.0, WEDGE_Z)
BRACE_W = 40.0

TRIG_PIN = 10.5
SCREW_D = 4.5
DOWEL_D = 6.2
PILOT = 3.0

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out')
os.makedirs(OUT, exist_ok=True)
FONT = FontProperties(family='DejaVu Sans', weight='bold')

# ------------------------------------------------------------------ helpers
def thick(p0, p1, w):
    return LineString([p0, p1]).buffer(w / 2, cap_style=2, join_style=2)

def fillet(g, r):
    return g.buffer(r, join_style=1).buffer(-r, join_style=1).buffer(-r / 2, join_style=1).buffer(r / 2, join_style=1)

def rect(x0, y0, x1, y1):
    return box(min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1))

def text(s, x, y, size, anchor='center', angle=0):
    tp = TextPath((0, 0), s, size=size, prop=FONT)
    polys = [np.array(p) for p in tp.to_polygons() if len(p) > 2]
    if not polys: return []
    allp = np.vstack(polys)
    w = allp[:, 0].max() - allp[:, 0].min(); h = size * 0.72
    dx = {'left': 0, 'center': -w / 2, 'right': -w}[anchor]
    out = []
    c, s_ = math.cos(math.radians(angle)), math.sin(math.radians(angle))
    for p in polys:
        q = p + np.array([dx, -h / 2])
        q = np.c_[c * q[:, 0] - s_ * q[:, 1], s_ * q[:, 0] + c * q[:, 1]] + np.array([x, y])
        out.append(q)
    return out

def circle_pts(x, y, r, n=48):
    t = np.linspace(0, 2 * np.pi, n + 1)
    return np.c_[x + r * np.cos(t), y + r * np.sin(t)]

def hexagon(x, y, af):
    r = af / math.sqrt(3)
    return Polygon([(x + r * math.cos(math.radians(30 + 60 * i)), y + r * math.sin(math.radians(30 + 60 * i))) for i in range(6)])

def cross(x, y, s=5):
    return [np.array([[x - s, y], [x + s, y]]), np.array([[x, y - s], [x, y + s]])]

class Part:
    def __init__(self, name, outline, holes=(), engrave=()):
        self.name, self.outline = name, outline
        self.holes = list(holes); self.engrave = list(engrave)
    def tf(self, angle=0.0, dx=0.0, dy=0.0, mirror=False):
        def tp(x, y):
            if mirror: x = -x
            c, s = math.cos(math.radians(angle)), math.sin(math.radians(angle))
            return (c * x - s * y + dx, s * x + c * y + dy)
        o = self.outline
        if mirror: o = affinity.scale(o, -1, 1, origin=(0, 0))
        o = affinity.translate(affinity.rotate(o, angle, origin=(0, 0)), dx, dy)
        return Part(self.name, o, [(*tp(x, y), d) for x, y, d in self.holes],
                    [np.array([tp(*q) for q in pl]) for pl in self.engrave])
    def solid(self):
        g = self.outline
        for x, y, d in self.holes:
            g = g.difference(Point(x, y).buffer(d / 2, 48))
        return g

# ------------------------------------------------------------------ parts
def side_panel(side, layer):
    """Y-Z plane. u = Y (fore-aft), v = Z (0 = top of rail)."""
    legs = [thick((s * (FOOT_Y - LEG_W / 2), 0), (s * (TOP_HALF - LEG_W / 2), PANEL_TOP), LEG_W) for s in (-1, 1)]
    pads = [rect(s * (FOOT_Y - 80), 0, s * FOOT_Y, 30) for s in (-1, 1)]
    top = rect(-TOP_HALF, PANEL_TOP - 50, TOP_HALF, PANEL_TOP)
    g = unary_union(legs + pads + [top])
    bar = rect(-FOOT_Y, BAR_Z0, FOOT_Y, BAR_Z1).intersection(unary_union(legs).convex_hull)
    g = unary_union([g, bar]).intersection(rect(-FOOT_Y, 0, FOOT_Y, PANEL_TOP))
    g = fillet(g, 14)
    # foot tabs (down into the rail) and top tabs (up into the cap)
    tabs = [rect(s * FOOT_TAB[0], -FOOT_TAB_D, s * FOOT_TAB[1], 0.5) for s in (-1, 1)]
    tabs += [rect(-30, PANEL_TOP - 0.5, -10, PANEL_TOP + TT), rect(10, PANEL_TOP - 0.5, 30, PANEL_TOP + TT)]
    g = unary_union([g] + tabs)
    # clearance notches for the stud heads under the cap
    for s in (-1, 1):
        g = g.difference(rect(s * PB_BOLT_PITCH / 2 - 11, PANEL_TOP - 3, s * PB_BOLT_PITCH / 2 + 11, PANEL_TOP + 1))
    # brace tab slot through the crossbar
    bz = (BAR_Z0 + BAR_Z1) / 2
    g = g.difference(rect(BRACE_Y - (TT + FIT) / 2, bz - 15.3, BRACE_Y + (TT + FIT) / 2, bz + 15.3))
    holes = []
    for s in (-1, 1):
        for t in (0.25, 0.72):
            p = (s * ((FOOT_Y - LEG_W / 2) + t * ((TOP_HALF - LEG_W / 2) - (FOOT_Y - LEG_W / 2))), t * PANEL_TOP)
            holes.append((*p, DOWEL_D))
    holes.append((0, PANEL_TOP - 25, DOWEL_D))
    fy = 1 if side == 'A' else -1      # side B is the mirror image of side A (engraving faces out on both)
    if fy < 0:
        g = affinity.scale(g, -1, 1, origin=(0, 0)); holes = [(-x, y, d) for x, y, d in holes]
    # labels sit on solid material: side/layer on the crossbar, front/back on the top block
    eng = text(f'{side}{layer}', -fy * 55, bz, 12) + text(f'SIDE {side}', -fy * 55, bz - 15, 5)
    eng += text('brace', fy * (BRACE_Y + 32), bz, 6)
    eng += text('FRONT >' if fy > 0 else '< FRONT', fy * 38, PANEL_TOP - 40, 6.5)
    eng += text('< BACK' if fy > 0 else 'BACK >', -fy * 38, PANEL_TOP - 40, 6.5)
    return Part(f'panel_{side}{layer}', g, holes, eng)

def cap(kind):
    """Horizontal, on top of a side panel. u = Y, w = X (centred on the panel)."""
    g = fillet(rect(-PB_LEN / 2 - 12, -26, PB_LEN / 2 + 12, 26), 4)
    for u0, u1 in ((-30, -10), (10, 30)):
        g = g.difference(rect(u0 - 0.3, -(TT + FIT) / 2, u1 + 0.3, (TT + FIT) / 2))
    holes, eng = [], []
    for s in (-1, 1):
        if kind == 'lower':
            g = g.difference(hexagon(s * PB_BOLT_PITCH / 2, 0, HEX_AF + 0.2))
        else:
            holes.append((s * PB_BOLT_PITCH / 2, 0, STUD_D))
    if kind == 'upper':
        eng.append(np.array([[-PB_LEN / 2, -PB_W / 2], [PB_LEN / 2, -PB_W / 2], [PB_LEN / 2, PB_W / 2],
                             [-PB_LEN / 2, PB_W / 2], [-PB_LEN / 2, -PB_W / 2]]))
        eng += text('bearing', 0, 13, 5)
    else:
        eng += text('CAP LOWER', 0, 15, 5)
    return Part('cap_' + kind, g, holes, eng)

def gusset(n):
    """Glued across a foot / rail joint, one each face. u = Y, v = Z."""
    g = fillet(rect(-60, -55, 60, 28), 4)
    holes = [(-40, -30, SCREW_D), (40, -30, SCREW_D), (-40, 14, SCREW_D), (40, 14, SCREW_D)]
    eng = [np.array([[-58, 0], [58, 0]])] + text('GUSSET', 0, -12, 6) + text('rail top', 0, -4, 4)
    return Part(f'gusset{n}', g, holes, eng)

def rail_piece(side, layer, y0, y1):
    """Y-Z plane. Notches: top for the panel feet, bottom for the cross members."""
    g = rect(y0, -RAIL_H, y1, 0)
    for s in (-1, 1):
        g = g.difference(rect(s * FOOT_TAB[0] - 0.3, -FOOT_TAB_D - 0.3, s * FOOT_TAB[1] + 0.3, 1))
    marks = []
    for name, yc in XM_Y.items():
        g = g.difference(rect(yc - (TT + FIT) / 2, -RAIL_H - 1, yc + (TT + FIT) / 2, -RAIL_H + XM_LOW + 0.3))
        if y0 + 15 < yc < y1 - 15:
            marks.append((name[0], yc + 16))
    g = fillet(g, 1.0)
    holes = []
    for yd in np.arange(math.ceil((RAIL_Y[0] + 40) / 120) * 120, RAIL_Y[1] - 30, 120):
        if y0 + 20 < yd < y1 - 20 and all(abs(yd - c) > 30 for c in XM_Y.values()) and \
           all(abs(abs(yd) - (FOOT_TAB[0] + FOOT_TAB[1]) / 2) > 40 for _ in [0]):
            holes.append((yd, -RAIL_H / 2 + 15, DOWEL_D))
    fy = 1 if side == 'A' else -1
    if fy < 0:
        g = affinity.scale(g, -1, 1, origin=(0, 0)); holes = [(-x, y, d) for x, y, d in holes]
    eng = []
    for m, yc in marks: eng += text(m, fy * yc, -RAIL_H + 20, 9)
    eng += text(f'RAIL {side}{layer}', fy * (y0 + y1) / 2, -RAIL_H / 2 - 18, 8)
    if y1 >= RAIL_Y[1] - 1: eng += text('front >' if fy > 0 else '< front', fy * (y1 - 40), -12, 6)
    return Part(f'rail_{side}{layer}_{int(y0)}', g, holes, eng)

def rail_pieces(side):
    splits = {1: [RAIL_Y[0], -40.0, RAIL_Y[1]], 2: [RAIL_Y[0], 250.0, RAIL_Y[1]]}
    out = []
    for layer, sp in splits.items():
        for a, b in zip(sp[:-1], sp[1:]):
            out.append(rail_piece(side, layer, a, b))
    return out

def cross_member(name, layer):
    """X-Z plane. Full height between the rails, low through and beyond them."""
    h = XM_HALF[name]
    g = unary_union([rect(-SIDE_X0, -RAIL_H, SIDE_X0, 0), rect(-h, -RAIL_H, h, -RAIL_H + XM_LOW)])
    g = fillet(g, 3).union(rect(-SIDE_X0 + 0.5, -RAIL_H, SIDE_X0 - 0.5, -RAIL_H + 5))
    g = g.intersection(rect(-h, -RAIL_H, h, 0))
    for s in (-1, 1):
        g = g.difference(rect(s * WEDGE_HOLE[0], WEDGE_Z - 3.3, s * WEDGE_HOLE[1], WEDGE_Z + 3.3))
    holes = []
    if name == 'MIDDLE':
        holes += [(BRACE_BOT[0], BRACE_BOT[1], PIN_D), (-BRACE_BOT[0], BRACE_BOT[1], PIN_D)]
    if name == 'BACK':
        holes += [(-40, -3 - 0, 0)] if False else []
    eng = text(f'{name} - LAYER {layer}', 0, -RAIL_H / 2 - 8, 9)
    eng += text('wedge', WEDGE_HOLE[1] + 18, WEDGE_Z + 12, 5) + text('wedge', -WEDGE_HOLE[1] - 18, WEDGE_Z + 12, 5)
    if name == 'BACK':
        eng += text('trigger on top edge', 0, -14, 6)
    return Part(f'xm_{name}{layer}', g, holes, eng)

def wedge(n):
    """Flat taper, slides fore-aft through the hole in a cross member."""
    g = Polygon([(0, -7), (95, -13), (95, 13), (0, 7)])
    g = fillet(g, 1.5)
    return Part(f'wedge{n}', g, [(85, 0, 4.0)], text('W', 40, 0, 7))

def brace(layer):
    """X-Z plane. Tab through the panel crossbar, pinned inside; pinned to the middle cross member below."""
    tx, tz = BRACE_TOP
    bx, bz = BRACE_BOT
    body = thick((tx + 4, tz), (bx, bz), BRACE_W)
    foot = Point(bx, bz).buffer(BRACE_W / 2, 32)
    tab = rect(SIDE_X0 - 22, tz - 15, tx + 6, tz + 15)
    g = fillet(unary_union([body, foot, tab]), 3)
    holes = [(SIDE_X0 - 11, tz, PIN_D), (bx, bz, PIN_D)]
    eng = text(f'BRACE {layer}', (tx + bx) / 2 + 6, (tz + bz) / 2, 7,
               angle=math.degrees(math.atan2(tz - bz, tx - bx)) + 180)
    return Part(f'brace{layer}', g, holes, eng)

def trigger_layer(kind):
    w, h, tab_w = 120.0, 70.0, 30.0
    g = unary_union([rect(-w / 2, 0, w / 2, h)] + [rect(x - tab_w / 2, -T, x + tab_w / 2, 0.5) for x in (-35, 35)])
    if kind == 'middle':
        g = g.difference(rect(-11, 25, 11, h + 1))
    g = fillet(g, 1.5)
    return Part('trigger_' + kind, g, [(0, 45, TRIG_PIN)],
                text('TRIGGER ' + ('MID' if kind == 'middle' else 'OUTER'), 0, 10, 6))

def trigger_base():
    """Glued and screwed onto the top edge of the BACK cross member (screws along the centre line)."""
    g = fillet(rect(-55, -80, 55, 80), 4)
    for v in (-35, 35):
        g = g.difference(rect(-9.3, v - 15.3, 9.3, v + 15.3))
    holes = [(-30, 0, SCREW_D), (30, 0, SCREW_D)]
    eng = [np.array([[-50, 0], [50, 0]])] + text('over the cross member', 0, -8, 4.5) + text('TRIGGER BASE', 0, 62, 6)
    return Part('trigger_base', g, holes, eng)

def sensor_plate():
    g = fillet(rect(-55, -28, 55, 28), 5)
    for x in (-45, 45): g = g.difference(rect(x - 2.2, -14, x + 2.2, 14))
    for y in (-20, 20): g = g.difference(rect(-28, y - 2.2, 28, y + 2.2))
    return Part('sensor_plate', g, [], text('SENSOR', 0, -1, 6))

def arm_end_template():
    hang, axle = 40.0, 40.0 + A_ARM
    g = fillet(rect(0, -20, axle + 40, 20), 2)
    eng = [np.array([[2.0, -17.5], [2.0, 17.5]]), circle_pts(hang, 0, 6.25), circle_pts(axle, 0, 10.25)]
    eng += text('END', 14, 9, 6) + text('hang M12', hang + 30, 10, 5) + text('axle 20', axle - 28, 10, 5)
    eng += text('ARM END TEMPLATE - flush with end', axle / 2 + 20, -11, 5)
    return Part('arm_end_template', g, [(hang, 0, PILOT), (axle, 0, PILOT)], eng)

def arm_tip_template():
    g = fillet(rect(-110, -10, 0, 10), 2)
    eng = [np.array([[-2.0, -7.5], [-2.0, 7.5]])] + text('TIP', -14, 0, 5) + text('sling eye', -45, 0, 4.5) + \
          text('trigger', -98, 0, 4.5)
    return Part('arm_tip_template', g, [(-22.5, 0, PILOT), (-75.0, 0, PILOT)], eng)

def doubler_template(kind):
    g = fillet(rect(-50, -20, 50, 20), 3)
    c = 20.5 if kind == 'axle' else 12.5
    eng = [circle_pts(0, 0, c / 2)] + text(('AXLE' if kind == 'axle' else 'HANG') + ' DOUBLER x2', 0, 13, 4.5)
    eng += text('M5', 35, -13, 4) + text('M5', -35, -13, 4)
    return Part('doubler_' + kind, g, [(0, 0, PILOT), (35, 0, PILOT), (-35, 0, PILOT)], eng)

def test_coupon():
    g = fillet(rect(0, 0, 180, 92), 3)
    holes, eng = [], []
    for i, w in enumerate([12.2, 12.6, 13.0]):          # slots for a 12 mm laminate
        x0 = 10 + i * 24
        g = g.difference(rect(x0, 10, x0 + w, 40))
        eng += text(f'{w}', x0 + w / 2, 46, 4.5)
    for i, d in enumerate([8.3, 8.6, 10.3, 10.6]):     # clevis pin and trigger pin
        x = 96 + i * 22
        holes.append((x, 25, d))
        eng += text(f'{d}', x, 38, 4.5)
    for i, af in enumerate([17.0, 17.4]):              # hex pocket for M10 heads
        g = g.difference(hexagon(20 + i * 30, 67, af))
        eng += text(f'{af}', 20 + i * 30, 84, 4.5)
    g = g.difference(rect(78, 63.7, 98, 70.3))          # wedge hole (6 mm wedge, 20 wide)
    eng += text('wedge', 88, 77, 4.5) + text('FIT TEST', 140, 72, 6) + text('cut first', 140, 62, 4.5)
    return Part('test_coupon', g, holes, eng)

def pouch():
    a, b = 60.0, 38.0
    t = np.linspace(0, 2 * np.pi, 120)
    g = unary_union([Polygon(np.c_[a * np.cos(t), b * np.sin(t)]), rect(-a - 14, -9, -a + 4, 9), rect(a - 4, -9, a + 14, 9)])
    return Part('pouch', fillet(g, 4), [(-a - 5, 0, 6.0), (a + 5, 0, 6.0), (0, 0, 8.0)], [])

# ------------------------------------------------------------------ nesting
class Sheet:
    def __init__(self, n, title, w=SHEET_W, h=SHEET_H):
        self.n, self.title, self.w, self.h, self.parts = n, title, w, h, []
    def free(self):
        s = rect(EDGE, EDGE, self.w - EDGE, self.h - EDGE)
        if self.parts:
            s = s.difference(unary_union([p.solid().buffer(GAP, 16) for p in self.parts]))
        return s
    def try_place(self, part, angles=(0, 90, 180, 270), step=5.0):
        region = prep(self.free())
        best = None
        for ang in angles:
            q = part.tf(ang)
            minx, miny, maxx, maxy = q.outline.bounds
            if maxx - minx > self.w - 2 * EDGE or maxy - miny > self.h - 2 * EDGE: continue
            for yy in np.arange(EDGE - miny, self.h - EDGE - maxy + 1e-6, step):
                if best is not None and yy + 0 > best[0]: break
                for xx in np.arange(EDGE - minx, self.w - EDGE - maxx + 1e-6, step):
                    if region.contains(affinity.translate(q.outline, xx, yy)):
                        sc = yy + xx * 0.02
                        if best is None or sc < best[0]: best = (sc, ang, xx, yy)
                        break
        if best is None: return False
        _, ang, xx, yy = best
        self.parts.append(part.tf(ang, xx, yy))
        return True

def nest(parts, sheets, first_new=None):
    for p in sorted(parts, key=lambda p: -p.outline.area):
        for sh in sheets:
            if sh.try_place(p): break
        else:
            sh = Sheet(len(sheets) + 1, f'sheet {len(sheets) + 1}')
            sheets.append(sh)
            assert sh.try_place(p), f'{p.name} does not fit an empty sheet'
    return sheets

# ------------------------------------------------------------------ output
def write(name, parts, title, w=SHEET_W, h=SHEET_H):
    doc = ezdxf.new('R2010', setup=True); doc.units = ezdxf.units.MM
    doc.layers.add('CUT', color=1); doc.layers.add('ENGRAVE', color=5)
    msp = doc.modelspace()
    def rings(g):
        for gg in (g.geoms if isinstance(g, MultiPolygon) else [g]):
            yield list(gg.exterior.coords)
            for r in gg.interiors: yield list(r.coords)
    for p in parts:
        for r in rings(p.outline): msp.add_lwpolyline(r, close=True, dxfattribs={'layer': 'CUT'})
        for x, y, d in p.holes: msp.add_circle((x, y), d / 2, dxfattribs={'layer': 'CUT'})
        for pl in p.engrave:
            msp.add_lwpolyline(pl.tolist(), close=bool(len(pl) > 8), dxfattribs={'layer': 'ENGRAVE'})
    doc.saveas(os.path.join(OUT, name + '.dxf'))
    P = lambda x, y: f'{x:.3f},{h - y:.3f}'
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}mm" height="{h}mm" viewBox="0 0 {w} {h}">',
           f'<title>{title}</title>', '<g id="CUT" fill="none" stroke="#FF0000" stroke-width="0.1">']
    for p in parts:
        for r in rings(p.outline): svg.append('<path d="M' + ' L'.join(P(*c) for c in r) + ' Z"/>')
        for x, y, d in p.holes: svg.append(f'<circle cx="{x:.3f}" cy="{h - y:.3f}" r="{d / 2:.3f}"/>')
    svg.append('</g><g id="ENGRAVE" fill="none" stroke="#0000FF" stroke-width="0.1">')
    for p in parts:
        for pl in p.engrave: svg.append('<path d="M' + ' L'.join(P(*c) for c in pl) + '"/>')
    svg.append('</g></svg>')
    open(os.path.join(OUT, name + '.svg'), 'w').write('\n'.join(svg))
    prev = list(svg)
    prev.insert(2, f'<rect x="0" y="0" width="{w}" height="{h}" fill="#F3EBDD" stroke="#888" stroke-width="1"/>')
    prev = [l.replace('stroke-width="0.1"', 'stroke-width="0.8"') for l in prev]
    import cairosvg
    cairosvg.svg2png(bytestring='\n'.join(prev).encode(), write_to=os.path.join(OUT, name + '.png'), output_width=1350)
    cairosvg.svg2pdf(bytestring='\n'.join(prev).encode(), write_to=os.path.join(OUT, name + '_preview.pdf'))

def check(parts, w=SHEET_W, h=SHEET_H):
    sheet = rect(0, 0, w, h)
    for p in parts:
        assert sheet.contains(p.outline), f'{p.name} off the sheet'
        inner = prep(p.solid().buffer(-1.5))
        for pl in p.engrave:
            for x, y in pl:
                assert inner.contains(Point(x, y)), f'engraving on {p.name} falls off the part at ({x:.0f}, {y:.0f})'
    for i in range(len(parts)):
        for j in range(i + 1, len(parts)):
            d = parts[i].solid().distance(parts[j].solid())
            assert d >= GAP - 0.05, f'{parts[i].name} and {parts[j].name} only {d:.2f} mm apart'

def check_joints():
    """Mating dimensions agree between parts."""
    # panel foot tabs fit the rail top notches
    assert FOOT_TAB_D <= RAIL_H - XM_LOW - 5
    # cross member low section fits the rail bottom notch, wedge hole sits outside the rail face
    assert WEDGE_HOLE[0] < SIDE_X1 < WEDGE_HOLE[1]
    assert XM_HALF['BACK'] > WEDGE_HOLE[1] + 10 and XM_HALF['MIDDLE'] > BRACE_BOT[0] + 10
    # bag clears the trough: bag centre lowest point is AXLE_Z - A_ARM - HANG
    low = AXLE_Z - A_ARM - HANG
    assert low > 100, low
    # stud heads sit inside the cap footprint, clear of the panel top tabs
    assert PB_BOLT_PITCH / 2 - HEX_AF / 2 > 30
    return low

if __name__ == '__main__':
    print('bag centre lowest point above rails:', check_joints())
    # sheets 1-2: two side-panel layers each
    sheets = []
    for n, pair in ((1, [('A', 1), ('A', 2)]), (2, [('B', 1), ('B', 2)])):
        sh = Sheet(n, f'Sheet {n}: side {pair[0][0]} panels')
        for k, (side, layer) in enumerate(pair):
            p = side_panel(side, layer)
            minx, miny, maxx, maxy = p.outline.bounds
            pw = maxx - minx
            x0 = EDGE + (SHEET_W - 2 * EDGE - 2 * pw - GAP) / 2 + k * (pw + GAP) - minx
            y0 = EDGE + ((SHEET_H - 2 * EDGE) - (maxy - miny)) / 2 - miny
            sh.parts.append(p.tf(0, x0, y0))
        sheets.append(sh)
    # sheet 3: rails, packed in rows (8 pieces, 90 tall)
    sh3 = Sheet(3, 'Sheet 3: rails')
    pcs = {p.name: p for p in rail_pieces('A') + rail_pieces('B')}
    rows = [['rail_A2_-600'], ['rail_B2_-600'], ['rail_A1_-40', 'rail_A2_250'], ['rail_B1_-40', 'rail_B2_250'],
            ['rail_A1_-600'], ['rail_B1_-600']]
    def row_pack(sh, rows, h_row):
        for r, names in enumerate(rows):
            x = EDGE
            for nm in names:
                q = pcs[nm]; minx, miny, maxx, maxy = q.outline.bounds
                sh.parts.append(q.tf(0, x - minx, EDGE + r * (h_row + GAP) - miny))
                x += (maxx - minx) + GAP
    row_pack(sh3, rows, RAIL_H)
    # sheet 4: cross members in rows, braces in the band above
    sh4 = Sheet(4, 'Sheet 4: cross members and braces')
    pcs = {p.name: p for p in [cross_member(nm, l) for nm in ('MIDDLE', 'FRONT', 'BACK') for l in (1, 2)]}
    row_pack(sh4, [['xm_MIDDLE1'], ['xm_MIDDLE2'], ['xm_FRONT1', 'xm_BACK1'], ['xm_FRONT2', 'xm_BACK2']], RAIL_H)
    a = -math.degrees(math.atan2(BRACE_TOP[1] - BRACE_BOT[1], BRACE_TOP[0] - BRACE_BOT[0]))
    for l in (1, 2, 3, 4):
        assert sh4.try_place(brace(l), angles=(a, a + 180), step=2.0), 'brace does not fit'
    sheets += [sh3, sh4]
    small = [gusset(i) for i in range(8)] + [cap('lower'), cap('lower'), cap('upper'), cap('upper')]
    small += [wedge(i) for i in range(8)]
    small += [trigger_layer('outer'), trigger_layer('middle'), trigger_layer('outer'), trigger_base()]
    small += [sensor_plate(), sensor_plate(), arm_end_template(), arm_tip_template(),
              doubler_template('axle'), doubler_template('hang')]
    nest(small, sheets)
    names = {1: '01_Sheet_SIDE_A_panels', 2: '02_Sheet_SIDE_B_panels', 3: '03_Sheet_rails', 4: '04_Sheet_cross_members_braces'}
    for sh in sheets:
        check(sh.parts)
        nm = names.get(sh.n, f'0{sh.n}_Sheet_base_and_parts')
        write(nm, sh.parts, f'Trebuchet 75% knock-down - sheet {sh.n} of {len(sheets)} - 6 mm ply')
        print(nm, len(sh.parts), sorted(p.name for p in sh.parts))
    c = test_coupon().tf(0, 5, 5); check([c], 190, 102)
    write('00_Test_coupon_cut_first', [c], 'Fit test coupon - cut first', 190, 102)
    pts = [pouch().tf(0, 80 + (i % 3) * 160, 55 + (i // 3) * 100) for i in range(6)]
    check(pts, 480, 210); write(f'0{len(sheets) + 1}_Fabric_sling_pouches', pts, 'Sling pouches - canvas or leather', 480, 210)
    print('sheets:', len(sheets))
