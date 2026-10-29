"""Assembly drawings for the clip-together desk trebuchet (built from gen_desk.py geometry)."""
import os, sys, math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from shapely.geometry import Point, box
from shapely import affinity
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'laser75'))
import gen_desk as D
from iso import Solid, Cam, render, box_solid, cyl_x

OUT = os.path.join(HERE, 'steps'); os.makedirs(OUT, exist_ok=True)
WOOD, WOOD2, STEEL, DARK, MASS = '#E2CFA8', '#CDB48A', '#7A8088', '#2B2B2B', '#B87333'
T = D.T
P = lambda *a: np.array([a], float)

def base(): return [Solid(D.base().solid(), (0, 0, -T), (1, 0, 0), (0, 1, 0), T, WOOD2, n=(0, 0, 1))]
def guides(dz=0.0):
    return [Solid(D.guide(1).solid(), (s * (D.GUIDE_X - T / 2), 0, dz), (0, 1, 0), (0, 0, 1), T, WOOD, n=(s, 0, 0)) for s in (-1, 1)]
def side(which, dy=0.0, dz=0.0):
    s = 1 if which == 'L' else -1
    return [Solid(D.side(which).solid(), (s * D.SX0, dy, dz), (0, s, 0), (0, 0, 1), T, WOOD, n=(s, 0, 0))]
def ties(dx=0.0):
    out = []
    for y in (-D.TIE_Y, D.TIE_Y):
        out.append(Solid(D.tie(1).solid(), (0, y - T / 2, 0), (1, 0, 0), (0, 0, 1), T, WOOD2, n=(0, 1, 0)))
    return out
def keys(dy=0.0):
    out = []
    for y in (-D.TIE_Y, D.TIE_Y):
        for s in (-1, 1):
            out.append(Solid(D.key(0).solid(), (s * (D.SX1 + 2.4), y - 22 + dy, sum(D.TIE_Z) / 2 - 3), (0, 1, 0), (s, 0, 0), T, '#8B6B3E', n=(0, 0, 1)))
    return out
def plugs(dz=0.0):
    out = []
    for s in (-1, 1):
        for y in (D.FOOT[1] + D.SLIDE / 2, -D.FOOT[0] + D.SLIDE / 2):
            out.append(Solid(D.plug(0).solid(), (s * D.SX0, y, dz), (0, 1, 0), (0, 0, 1), T, '#8B6B3E', n=(s, 0, 0)))
    return out
def trigger(dy=0.0, key_dx=0.0):
    post = Solid(D.trigger_post().solid(), (D.POST_X - T / 2, D.POST_Y + dy, 0), (0, 1, 0), (0, 0, 1), T, WOOD2, n=(1, 0, 0))
    key = Solid(D.trigger_key().solid(), (D.POST_X - 30 + key_dx, D.POST_Y + dy, 30.2), (1, 0, 0), (0, 1, 0), T, '#8B6B3E', n=(0, 0, 1))
    return [post, key]

def arm_parts(angle, tip=True, sensor=True, crop=None):
    a = math.radians(angle)
    U = np.array([0, math.cos(a), math.sin(a)]); V = np.array([0, -math.sin(a), math.cos(a)])
    o = np.array([-T / 2, 0, D.AXLE_Z])
    shp = D.arm().solid()
    if crop: shp = shp.intersection(box(crop[0], -40, crop[1], 40))
    out = [Solid(shp, o, U, V, T, '#D9C29A', n=(1, 0, 0))]
    if tip:
        out.append(Solid(D.release_tip(15).solid(), o + D.L_ARM * U, U, V, T, '#8B6B3E', n=(1, 0, 0)))
    if sensor:
        out.append(Solid(D.sensor_plate().solid(), np.array([T / 2, 0, D.AXLE_Z]) + 70 * U, U, V, 4, '#555555', n=(1, 0, 0)))
    return out, U, V

def axle(washers=True, explode=0.0):
    out = [cyl_x(-D.SX1 - 12 - explode * 2, D.SX1 + 14 + explode * 2, 0, D.AXLE_Z, 4, STEEL),
           cyl_x(D.SX1 + 6 + explode * 2, D.SX1 + 16 + explode * 2, 0, D.AXLE_Z, 9, DARK)]
    if washers:
        for s in (-1, 1):
            for i in range(9):
                x0 = 3 + i * 6 + explode * (0.2 + i * 0.12)
                out.append(cyl_x(s * x0 if s > 0 else -x0 - 6, (x0 + 6) if s > 0 else -x0, 0, D.AXLE_Z, 12, '#E8D9B8'))
    return out

def basket(pin, weights=0, explode=0.0):
    py, pz = pin
    out = []
    for s in (-1, 1):
        out.append(Solid(D.bail(1).solid(), (s * (D.BASKET / 2 + explode), py, pz), (0, 1, 0), (0, 0, 1), T, WOOD, n=(s, 0, 0)))
    fz = -D.LC - 34
    out.append(Solid(D.floor_().solid(), (0, py, pz + fz - explode * 0.8), (1, 0, 0), (0, 1, 0), T, WOOD2, n=(0, 0, 1)))
    for s in (-1, 1):
        out.append(Solid(D.wall(1).solid(), (0, py + s * (D.BASKET / 2 + explode * 0.6) + (0 if s > 0 else -T), pz), (1, 0, 0), (0, 0, 1), T, WOOD2, n=(0, 1, 0)))
    for i in range(weights):
        out.append(Solid(Point(0, 0).buffer(24, 24).difference(box(-3, 0, 3, 30)), (0, py, pz + fz + T + i * 9.5), (1, 0, 0), (0, 1, 0), 9, MASS, n=(0, 0, 1)))
    hb = [cyl_x(-D.BASKET / 2 - T - 8, D.BASKET / 2 + T + 8, py, pz, 3, STEEL)]
    return out + hb

def seg(p0, p1, w, color):
    p0 = np.asarray(p0, float); p1 = np.asarray(p1, float)
    d = p1 - p0; L = np.linalg.norm(d); U = d / L
    V = np.cross([1.0, 0, 0], U); V = V / np.linalg.norm(V)
    return Solid(box(0, -w / 2, L, w / 2), p0 - np.array([w / 2, 0, 0]), U, V, w, color, n=(1, 0, 0))

def frame():
    return base() + guides() + side('L') + side('R') + ties() + keys() + plugs() + trigger()

def fig(name, solids, eye=(1.0, 0.85, 0.7), guides_=(), labels=(), size=(6.0, 4.4)):
    f, ax = plt.subplots(figsize=size)
    render(ax, solids, Cam(eye), guides=guides_, labels=labels)
    f.savefig(os.path.join(OUT, name + '.pdf'), bbox_inches='tight', pad_inches=0.04)
    f.savefig(os.path.join(OUT, name + '.png'), bbox_inches='tight', pad_inches=0.04, dpi=110)
    plt.close(f)

def inventory():
    items = [('Base', D.base(), 1), ('Side L / R', D.side('L'), 2), ('Arm', D.arm(), 1), ('Tie', D.tie(1), 2),
             ('Trough guide', D.guide(1), 2), ('Basket side (bail)', D.bail(1), 2), ('Basket floor', D.floor_(), 1),
             ('Basket wall', D.wall(1), 2), ('Trigger post + key', D.trigger_post(), '1 + 1'), ('Release tips 0/15/30', D.release_tip(15), 3),
             ('Sling ring', D.ring(0), 3), ('Lock plug', D.plug(0), 5), ('Tie key', D.key(0), 6),
             ('Axle washer', D.washer('axle', 0), 20), ('Hang washer', D.washer('hang', 0), 12), ('Sensor plate', D.sensor_plate(), 1)]
    f, axs = plt.subplots(4, 4, figsize=(7.2, 6.0))
    from matplotlib.patches import Polygon as MP
    for ax, (nm, p, q) in zip(axs.flat, items):
        g = p.solid()
        for gg in (g.geoms if hasattr(g, 'geoms') else [g]):
            ax.add_patch(MP(np.array(gg.exterior.coords), fc=WOOD, ec='#1A1A1A', lw=0.5))
            for r in gg.interiors: ax.add_patch(MP(np.array(r.coords), fc='white', ec='#1A1A1A', lw=0.4))
        ax.set_aspect('equal'); ax.autoscale_view(); ax.axis('off'); ax.set_title(f'{nm}\n× {q}', fontsize=9)
    f.tight_layout(); f.savefig(os.path.join(OUT, 'd01_inventory.pdf')); f.savefig(os.path.join(OUT, 'd01_inventory.png'), dpi=110); plt.close(f)

def steps():
    inventory()
    # 2 guides into base
    fig('d02_guides', base() + guides(dz=60), guides_=[(P(D.GUIDE_X, -60, 55), P(D.GUIDE_X, -60, 8))],
        labels=[('trough guides: press the tabs\ninto the slots', P(D.GUIDE_X, 100, 78), (160, 60)), ('BASE, FRONT end away from you', P(0, 200, 0), (150, -60))])
    # 3 sides: drop in, slide back, plug
    fig('d03_sides', base() + guides() + side('L', dy=D.SLIDE, dz=50) + side('R') + plugs(dz=40)[2:],
        guides_=[(P(D.SX1, 140, 45), P(D.SX1, 140, 5)), (P(D.SX1 + 20, 200, 20), P(D.SX1 + 20, 170, 20))],
        labels=[('1  drop the foot hooks\n    through the slots', P(D.SX1, 150, 60), (180, 40)),
                ('2  slide the side back\n    10 mm (towards BACK)', P(D.SX1 + 20, 185, 20), (200, -40)),
                ('3  push a lock plug into\n    each gap left in front', P(-D.SX1, 143, 10), (-200, -50))])
    # 4 ties + keys
    fig('d04_ties', base() + guides() + side('L') + side('R') + plugs() + ties() + keys(dy=-60),
        guides_=[(P(D.SX1 + 4, D.TIE_Y - 90, 70), P(D.SX1 + 4, D.TIE_Y - 30, 70))],
        labels=[('tie through both sides', P(0, D.TIE_Y, 82), (-170, 120)), ('key outside each side:\npush in, thin end first', P(D.SX1 + 4, D.TIE_Y - 70, 62), (200, -30))])
    # 5 trigger
    bcrop = [Solid(D.base().solid().intersection(box(-60, D.POST_Y - 70, 100, D.POST_Y + 70)), (0, 0, -T), (1, 0, 0), (0, 1, 0), T, WOOD2, n=(0, 0, 1))]
    gcrop = [Solid(D.guide(1).solid().intersection(box(D.POST_Y - 70, -10, D.POST_Y + 70, 30)), (D.GUIDE_X - T / 2, 0, 0), (0, 1, 0), (0, 0, 1), T, WOOD, n=(1, 0, 0))]
    fig('d05_trigger', bcrop + gcrop + trigger(dy=-D.HOOK, key_dx=60), eye=(1.0, -0.5, 0.7), size=(5.0, 3.6),
        guides_=[(P(D.POST_X + 60, D.POST_Y, 33), P(D.POST_X + 10, D.POST_Y, 33))],
        labels=[('post: hook through,\nslide FORWARD, lock plug', P(D.POST_X, D.POST_Y - 10, 45), (-60, 40)),
                ('trigger key slides\nthrough the post', P(D.POST_X + 70, D.POST_Y, 33), (60, 30))])
    # 6 arm: tip, sling, sensor
    arm, U, V = arm_parts(0.0)
    tipd = arm[1].moved(60 * U)
    fig('d06_arm', [arm[0], tipd, arm[2]] + [Solid(D.ring(0).solid(), (T / 2 + 2, 470, D.AXLE_Z + 20), (0, 1, 0), (0, 0, 1), T, '#8B6B3E', n=(1, 0, 0))],
        eye=(1.0, 0.2, 0.25), size=(6.6, 2.6),
        guides_=[(P(0, D.L_ARM + 60, D.AXLE_Z), P(0, D.L_ARM + 8, D.AXLE_Z))],
        labels=[('release tip: dovetail slides in\n(start with 15; 0 and 30 to tune)', P(0, D.L_ARM + 70, D.AXLE_Z - 10), (60, -90)),
                ('sling ring', P(0, 470, D.AXLE_Z + 20), (90, 60)), ('sensor plate', P(0, 70, D.AXLE_Z), (-40, -80)),
                ('hang hole', P(0, -D.A_ARM, D.AXLE_Z), (0, 70))])
    # 7 basket onto the arm
    arm, U, V = arm_parts(90.0, tip=False, sensor=False, crop=(-170, 60))
    pin = (0.0, D.AXLE_Z - D.A_ARM)
    hw = [cyl_x(s * (3 + i * 6) if s > 0 else -(3 + i * 6) - 6, (3 + i * 6 + 6) if s > 0 else -(3 + i * 6), 0, pin[1], 10, '#E8D9B8') for s in (-1, 1) for i in range(5)]
    fig('d07_basket', arm + hw + basket(pin, explode=25), eye=(1.0, 0.7, 0.35), size=(5.2, 4.4),
        labels=[('bails on the M6 hang bolt,\n5 washers each side of the arm', P(D.BASKET / 2 + 25, 0, pin[1] + 5), (110, 50)),
                ('floor and walls: tabs drop\ninto the slots in the bails', P(0, 0, pin[1] - 105), (120, -40))])
    # 8 arm onto the frame
    arm, U, V = arm_parts(90.0)
    fig('d08_axle', frame() + [s.moved((0, 0, 0)) for s in arm] + axle(explode=10) + basket(pin), eye=(1.0, 0.8, 0.45), size=(6.0, 5.0),
        labels=[('M8 axle bolt: side, 9 washers,\narm, 9 washers, side, wing nut', P(D.SX1 + 30, 0, D.AXLE_Z), (330, -120)),
                ('nut snug, then back a little:\nthe arm must swing freely', P(-D.SX1 - 10, 0, D.AXLE_Z), (-300, 160))])
    # 9 loaded and cocked
    ang = 180 + math.degrees(math.asin((D.AXLE_Z - 40) / D.L_ARM))
    arm, U, V = arm_parts(ang)
    a = math.radians(ang)
    pin = (-D.A_ARM * math.cos(a), D.AXLE_Z - D.A_ARM * math.sin(a))
    tip = np.array([0, D.L_ARM * math.cos(a), D.AXLE_Z + D.L_ARM * math.sin(a)])
    teye = np.array([0, (D.L_ARM - 50) * math.cos(a), D.AXLE_Z + (D.L_ARM - 50) * math.sin(a)])
    pouch = np.array([0, tip[1] + 0.95 * 360, 14])
    extra = [seg(tip, pouch, 2.5, '#8E5B2E'), box_solid(-14, pouch[1] - 4, 3, 14, pouch[1] + 26, 27, '#C0392B'),
             seg(teye, (D.POST_X - 20, D.POST_Y, 36), 2.5, DARK)]
    fig('d09_cocked', frame() + arm + axle() + basket(pin, weights=7) + extra, eye=(1.0, 0.55, 0.5), size=(6.4, 4.8),
        labels=[('weights in the basket', P(0, pin[0], pin[1] - 60), (220, 80)),
                ('loop from the arm over the\ntrigger key, inside the post', P(D.POST_X - 20, D.POST_Y, 36), (-200, -60)),
                ('ring over the release tip;\nbeanbag in the pouch', P(0, pouch[1], 20), (200, -60))])

if __name__ == '__main__':
    steps(); print(sorted(os.listdir(OUT)))
