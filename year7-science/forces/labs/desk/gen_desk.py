"""Desk trebuchet -- clip-together, no glue. 6 mm plywood, 900 x 600 bed.

Every part is a single 6 mm layer. Joints are hooked tabs + lock plugs, tabs + tapered keys,
dovetails, and two bolts (axle M8, hang pin M6) with laser-cut spacer washers.
Global axes: X across (along the axle), Y fore-aft (+Y = throwing direction), Z up (0 = top of the base).
Needs: python -m pip install numpy shapely ezdxf matplotlib   (gen75.py must sit in the same folder)
Run:  python gen_desk.py            ->  out/      (slots drawn 6.4 mm)
      python gen_desk.py --cl 0     ->  out_CL0/  (slots drawn 6.0 mm)   takes 1-2 minutes
"""
import os, sys, math
try:
    import numpy, shapely, ezdxf, matplotlib
except ImportError as e:
    sys.exit(f"Missing Python package: {e.name}\nInstall the four it needs with:\n"
             "    python -m pip install numpy shapely ezdxf matplotlib\nthen run this script again.")
import numpy as np
from shapely.geometry import Polygon, Point
from shapely.ops import unary_union
from shapely import affinity
_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_here, '..', 'laser75'))
sys.path.insert(0, _here)          # gen75.py next to this file wins
import gen75 as K                      # shared helpers: Part, rect, fillet, text, thick, Sheet, nest, write, check
from gen75 import Part, rect, fillet, text, thick

# clearance can be set on the command line:  python3 gen_desk.py --cl 0   (files go to out_CL0)
_cl = float(sys.argv[sys.argv.index('--cl') + 1]) if '--cl' in sys.argv else 0.4
K.OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out' if '--cl' not in sys.argv else f'out_CL{_cl:g}')
os.makedirs(K.OUT, exist_ok=True)
K.EDGE = 25.0          # keep parts 25 mm in from every edge: they nest inside 850 x 550 on the 900 x 600 file

T = 6.0
CL = _cl               # slot width over the 6 mm sheet, as drawn (the laser's kerf adds about 0.2 more)
SW = T + CL             # slot width
L_ARM, A_ARM = 400.0, 130.0
AXLE_Z = 330.0
GAP = 120.0             # inside faces of the two sides
SX0, SX1 = GAP / 2, GAP / 2 + T
AXLE_D, HANG_D = 8.5, 6.5
FOOT = (108.0, 138.0)   # |Y| of a foot tab (final position)
HOOK, SLIDE = 10.0, 10.0
LEG_FOOT, LEG_TOP, LEG_W = 120.0, 22.0, 36.0
TIE_Z = (50.0, 80.0)    # tie tab height range
KEY_HOLE_W = 8.0        # key hole across (X); starts 1 mm inside the leg's outer face so the key draws the tie tight
KEY_HOLE_H = 6.5        # key hole height (Z): the key goes in flat, so this only has to clear the sheet thickness
KEY_LEN, KEY_W = 42.0, (4.4, 10.4)   # key: one straight edge (against the leg), taper on the other
BASE_Y = (-310.0, 250.0)
BASE_HALF = 100.0
GUIDE_X = 30.0          # trough guides at X = +-30 (inner faces +-27)
GUIDE_Y = (-300.0, 150.0)
POST_X, POST_Y = 51.0, -241.0
BASKET = 70.0           # inside size of the basket (X and Y)
BAIL_HALF = 50.0
LC = 75.0               # hang pin to basket centre

def leg_u(v):           # leg centre line, |Y| at height v
    return LEG_FOOT - (LEG_FOOT - LEG_TOP) * v / AXLE_Z
TIE_Y = leg_u(sum(TIE_Z) / 2)

# ------------------------------------------------------------------ parts
def hooked_tab(u0, u1, back=True):
    """Tab under a part edge (v = 0): drops through a slot, then the part slides back so the hook catches under the base."""
    tab = rect(u0, -T - 0.3, u1, 0.5)
    hook = rect(u0 - HOOK, -2 * T - 0.3, u1, -T - 0.3) if back else rect(u0, -2 * T - 0.3, u1 + HOOK, -T - 0.3)
    return unary_union([tab, hook])

def side(which):
    """Y-Z plane. u = Y, v = Z. Side R is the mirror image of side L, so both hook backwards."""
    legs = [thick((s * LEG_FOOT, 0), (s * LEG_TOP, AXLE_Z), LEG_W) for s in (-1, 1)]
    pads = [rect(s * (FOOT[0] - 6), 0, s * (FOOT[1] + 4), 14) for s in (-1, 1)]
    boss = Point(0, AXLE_Z).buffer(26, 48)
    g = unary_union(legs + pads + [boss]).intersection(rect(-200, 0, 200, AXLE_Z + 30))
    g = fillet(g, 10)
    tabs = [hooked_tab(FOOT[0], FOOT[1]), hooked_tab(-FOOT[1], -FOOT[0])]
    g = unary_union([g] + tabs)
    for s in (-1, 1):       # tie slots
        g = g.difference(rect(s * TIE_Y - SW / 2, TIE_Z[0] - 0.2, s * TIE_Y + SW / 2, TIE_Z[1] + 0.2))
    holes = [(0, AXLE_Z, AXLE_D)]
    fy = 1 if which == 'L' else -1
    if fy < 0:
        g = affinity.scale(g, -1, 1, origin=(0, 0)); holes = [(-x, y, d) for x, y, d in holes]
    eng = text(f'SIDE {which}', 0, AXLE_Z + 15, 5) + text('FRONT>' if fy > 0 else '<FRONT', fy * 121, 7, 4.2)
    return Part(f'side_{which}', g, holes, eng)

def base():
    """X-Y plane. u = X, v = Y."""
    g = fillet(rect(-BASE_HALF, BASE_Y[0], BASE_HALF, BASE_Y[1]), 8)
    def slot(x0, x1, y0, y1): return rect(x0, y0, x1, y1)
    cuts = []
    for s in (-1, 1):
        xa, xb = s * (SX0 - CL / 2), s * (SX1 + CL / 2)
        for y0, y1 in ((FOOT[0] - HOOK, FOOT[1] + SLIDE), (-FOOT[1] - HOOK, -FOOT[0] + SLIDE)):
            cuts.append(slot(min(xa, xb), max(xa, xb), y0 - 0.2, y1 + 0.2))
    for s in (-1, 1):           # trough guide tabs
        for yc in (-250.0, -60.0, 110.0):
            cuts.append(slot(s * GUIDE_X - SW / 2, s * GUIDE_X + SW / 2, yc - 10.2, yc + 10.2))
    # trigger post (hooked, slides towards the front)
    cuts.append(slot(POST_X - SW / 2, POST_X + SW / 2, POST_Y - 8 - 0.2, POST_Y + 8 + HOOK + 0.2))
    for c in cuts: g = g.difference(c)
    eng = text('BASE', 0, -180, 9) + text('FRONT', 0, 200, 7) + text('throwing direction ^', 0, 186, 4.5)
    eng += text('trigger', POST_X + 22, POST_Y, 4.5, angle=90)
    return Part('base', g, [], eng)

def plug(n):
    """Lock plug: fills the gap left in a foot slot after the side slides back."""
    g = unary_union([rect(-SLIDE / 2 + CL / 2, -T, SLIDE / 2 - CL / 2, 0.5), rect(-11, 0, 11, 9)])
    return Part(f'plug{n}', fillet(g, 1), [], text('P', 0, 4.5, 5))

def tie(n):
    """X-Z plane: between the sides, keyed outside each one."""
    body = rect(-SX0, TIE_Z[0] - 2, SX0, TIE_Z[1] + 2)
    tabs = rect(-(SX1 + 20), TIE_Z[0] + 0.2, SX1 + 20, TIE_Z[1] - 0.2)
    g = fillet(unary_union([body, tabs]), 1.5)
    for s in (-1, 1):
        zc = sum(TIE_Z) / 2
        x0, x1 = s * (SX1 - 1.0), s * (SX1 - 1.0 + KEY_HOLE_W)
        g = g.difference(rect(min(x0, x1), zc - KEY_HOLE_H / 2, max(x0, x1), zc + KEY_HOLE_H / 2))
    return Part(f'tie{n}', g, [], text(f'TIE', 0, sum(TIE_Z) / 2, 7))

def key(n, length=KEY_LEN):
    """Flat along y = 0 (this edge goes against the leg); all the taper is on the other edge.
    An engraved line runs beside the flat edge so students can tell which edge it is."""
    g = Polygon([(0, 0), (length, 0), (length, KEY_W[1]), (0, KEY_W[0])])
    eng = text('K', length - 8, KEY_W[1] / 2 + 0.4, 4.2) + [np.array([[5.0, 2.0], [24.0, 2.0]])]
    return Part(f'key{n}', fillet(g, 0.8), [], eng)

def arm():
    """Arm in its own plane. s along the arm (0 = axle), d across. Sling side = -d."""
    h = lambda s: 18.0 - 5.0 * s / L_ARM
    longp = Polygon([(0, -h(0)), (L_ARM, -h(L_ARM)), (L_ARM, h(L_ARM)), (0, h(0))])
    short = rect(-A_ARM, -15, 0, 15)
    g = unary_union([longp, short, Point(0, 0).buffer(24, 48), Point(-A_ARM, 0).buffer(15, 32)])
    g = fillet(g, 6)
    # dovetail socket for the release tip
    g = g.difference(Polygon([(L_ARM - 14, -7), (L_ARM + 1, -5), (L_ARM + 1, 5), (L_ARM - 14, 7)]))
    # lightening slots
    for s0 in (110.0, 175.0, 240.0, 300.0):
        s1 = s0 + 52 if s0 < 300 else s0 + 35
        g = g.difference(fillet(Polygon([(s0, -(h(s0) - 6.5)), (s1, -(h(s1) - 6.5)), (s1, h(s1) - 6.5), (s0, h(s0) - 6.5)]), 2.5))
    holes = [(0, 0, AXLE_D), (-A_ARM, 0, HANG_D), (L_ARM - 50, 0, 4.0), (L_ARM - 27, -4, 4.0)]
    eng = text('ARM', 60, 5, 7) + text('sensor here', 60, -8, 4.2)
    eng += text('trigger', L_ARM - 50, 8.0, 3.2) + text('sling', L_ARM - 27, 5.5, 3.2)
    return Part('arm', g, holes, eng)

def release_tip(angle):
    """Dovetail tab into the arm tip; prong angled towards the sling side (-d) by `angle` degrees."""
    c = CL / 2
    tab = Polygon([(-14 + c, -7 + c), (0.5, -5 + c), (0.5, 5 - c), (-14 + c, 7 - c)])
    block = rect(0, -9, 12, 9)
    prong = rect(0, -3, 24, 3)
    prong = affinity.rotate(prong, -angle, origin=(0, 0)).buffer(0)
    prong = affinity.translate(prong, 10, 0)
    tip = Point(10 + 24 * math.cos(math.radians(-angle)), 24 * math.sin(math.radians(-angle))).buffer(3, 16)
    g = fillet(unary_union([tab, block, prong, tip]), 0.8)
    return Part(f'tip{int(angle)}', g, [], text(f'{int(angle)}', 5, 4.5 if angle else 0, 4.5))

def ring(n):
    """Sling release ring: drops over the release prong; the sling cord ties through the ear."""
    g = fillet(unary_union([Point(0, 0).buffer(10, 48), Point(15, 0).buffer(5.5, 32), rect(0, -4, 15, 4)]), 1)
    return Part(f'ring{n}', g, [(0, 0, 9.0), (15.5, 0, 3.0)], [])

def washer(kind, n):
    r, d = (12.0, AXLE_D) if kind == 'axle' else (10.0, HANG_D)
    return Part(f'washer_{kind}{n}', Point(0, 0).buffer(r, 48), [(0, 0, d)], [])

def bail(n):
    """Y-Z plane, hangs on the hang pin (v = 0). Floor and both walls hook into it."""
    neck = unary_union([Point(0, 0).buffer(12, 32), rect(-11, -40, 11, 0)])
    plate = rect(-BAIL_HALF, -LC - 40, BAIL_HALF, -LC + 38)
    g = fillet(unary_union([neck, plate]), 4)
    fz = -LC - 34                                       # floor (6 mm) sits at fz .. fz + 6
    for u0, u1 in ((-25, -5), (5, 25)):
        g = g.difference(rect(u0 - 0.2, fz - CL / 2, u1 + 0.2, fz + T + CL / 2))
    for s in (-1, 1):                                   # wall tabs
        uc = s * (BASKET / 2 + T / 2)
        g = g.difference(rect(uc - SW / 2, -LC - 20.2, uc + SW / 2, -LC + 20.2))
    return Part(f'bail{n}', g, [(0, 0, HANG_D)], text('BAIL', 0, -LC + 22, 6) + text('basket', 0, -LC + 2, 4.5))

def floor_():
    g = rect(-BASKET / 2, -BASKET / 2, BASKET / 2, BASKET / 2)
    for s in (-1, 1):
        for v0, v1 in ((-25, -5), (5, 25)):
            g = g.union(rect(s * BASKET / 2, v0, s * (BASKET / 2 + T + 3), v1))
    return Part('floor', fillet(g, 1), [], text('FLOOR', 0, 0, 6))

def wall(n):
    fz = -LC - 34
    g = rect(-BASKET / 2, fz, BASKET / 2, -LC + 36)
    for s in (-1, 1):
        g = g.union(rect(s * BASKET / 2, -LC - 19.8, s * (BASKET / 2 + T + 3), -LC + 19.8))
    return Part(f'wall{n}', fillet(g, 1), [], text('WALL', 0, -LC + 20, 6))

def guide(n):
    """Trough guide, Y-Z plane, friction tabs into the base."""
    g = rect(GUIDE_Y[0], 0, GUIDE_Y[1], 18)
    for yc in (-250.0, -60.0, 110.0):
        g = g.union(rect(yc - 9.9, -T, yc + 9.9, 0.5))
    return Part(f'guide{n}', fillet(g, 1), [], text('TROUGH GUIDE', -100, 9, 6))

def trigger_post():
    body = rect(-14, 0, 14, 48)
    g = unary_union([body, hooked_tab(-8, 8, back=False)])
    g = fillet(g, 1.5).difference(rect(-6 - CL / 2, 30, 6 + CL / 2, 30 + SW))
    return Part('trigger_post', g, [], text('TRIGGER', 0, 16, 4.2))

def trigger_key():
    g = unary_union([rect(0, -6, 70, 6), Point(76, 0).buffer(10, 32)])
    return Part('trigger_key', fillet(g, 1), [(78, 0, 5.0)], text('PULL', 34, 0, 5))

def sensor_plate():
    g = fillet(rect(-40, -22, 40, 22), 4)
    for x in (-32, 32): g = g.difference(rect(x - 2.2, -12, x + 2.2, 12))
    for y in (-15, 15): g = g.difference(rect(-20, y - 2.2, 20, y + 2.2))
    return Part('sensor_plate', g, [], text('SENSOR', 0, 0, 5))

def test_coupon():
    g = fillet(rect(0, 0, 120, 60), 3)
    holes, eng = [], []
    for i, w in enumerate([round(SW - 0.2, 2), round(SW, 2), round(SW + 0.2, 2)]):
        g = g.difference(rect(10 + i * 20, 10, 10 + i * 20 + w, 34)); eng += text(f'{w}', 13 + i * 20, 41, 4)
    for i, d in enumerate([8.3, 8.6, 6.3, 6.6]):
        holes.append((76 + (i % 2) * 22, 16 + (i // 2) * 24, d)); eng += text(f'{d}', 76 + (i % 2) * 22, 26 + (i // 2) * 24, 3.8)
    eng += text('FIT TEST', 40, 52, 5)
    return Part('test_coupon', g, holes, eng)

def kit():
    p = [base(), side('L'), side('R'), arm(), tie(1), tie(2), guide(1), guide(2),
         bail(1), bail(2), floor_(), wall(1), wall(2), trigger_post(), trigger_key(), sensor_plate()]
    p += [plug(i) for i in range(5)] + [key(i) for i in range(8)]
    p += [release_tip(a) for a in (0, 15, 30)] + [ring(i) for i in range(3)]
    p += [washer('axle', i) for i in range(20)] + [washer('hang', i) for i in range(12)]
    return p

def precheck(parts):
    from shapely.prepared import prep
    bad = []
    for p in parts:
        inner = prep(p.solid().buffer(-1.5))
        n = sum(1 for pl in p.engrave for x, y in pl if not inner.contains(Point(x, y)))
        if n: bad.append((p.name, n))
    assert not bad, bad

if __name__ == '__main__':
    precheck(kit() + [test_coupon()])
    sheets = K.nest(kit(), [K.Sheet(1, 'desk trebuchet')])
    for sh in sheets:
        K.check(sh.parts)
        for q in sh.parts:      # everything inside the 850 x 550 area
            x0, y0, x1, y1 = q.outline.bounds
            assert x0 >= 25 - 1e-6 and y0 >= 25 - 1e-6 and x1 <= 875 + 1e-6 and y1 <= 575 + 1e-6, q.name
        K.write(f'0{sh.n}_Desk_trebuchet_sheet{sh.n}', sh.parts, f'Desk trebuchet - sheet {sh.n} of {len(sheets)} - 6 mm ply')
        print('sheet', sh.n, len(sh.parts))
    c = test_coupon().tf(0, 5, 5); K.check([c], 130, 70)
    K.write('00_Test_coupon_cut_first', [c], 'Desk trebuchet fit test', 130, 70)
    pts = [K.pouch().tf(0, 0, 0) for _ in range(1)]
    pp = []
    for i in range(6):
        q = Part('pouch', affinity.scale(K.pouch().outline, 0.6, 0.6, origin=(0, 0)), [(-a, 0, 4.0) for a in (-39.0, 39.0)] + [(0, 0, 5.0)], [])
        pp.append(q.tf(0, 55 + (i % 3) * 100, 35 + (i // 3) * 65))
    K.check(pp, 320, 140); K.write(f'0{len(sheets) + 1}_Fabric_pouches', pp, 'Desk trebuchet sling pouches - felt or canvas', 320, 140)
    print('sheets', len(sheets))
