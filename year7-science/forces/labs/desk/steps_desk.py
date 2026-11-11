"""Assembly drawings for the clip-together desk trebuchet (built from gen_desk.py geometry).

Conventions used in every drawing:
  orange   the parts this step adds or moves
  pale     what is already built
  red      arrows (which way to move it) and numbered badges (match the numbered text)
  circles  close-ups; the letter matches a dashed circle on the main view
Run:  python steps_desk.py      ->  steps/d01 ... d09 (.pdf for the guide, .png to look at)
"""
import os, sys, math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MP, Circle, FancyBboxPatch
from shapely.geometry import Point, box
from shapely import affinity
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'laser75'))
sys.path.insert(0, HERE)
import gen_desk as D
from iso import Solid, Cam, render, box_solid, cyl_x

OUT = os.path.join(HERE, 'steps'); os.makedirs(OUT, exist_ok=True)
T = D.T
WOOD = '#E2CFA8'                                   # neutral (parts list)
OLD, OLD_EC = '#F4EFE4', '#A39C8E'                 # already built
NEW, NEW_EC = '#F4A340', '#6B3F00'                 # added in this step
STEEL, DARK, MASS, RED, INK = '#8A9099', '#2B2B2B', '#B87333', '#C0392B', '#222222'
P = lambda *a: np.array([a], float)
ZC = sum(D.TIE_Z) / 2                              # height of the ties / keys

# ------------------------------------------------------------------ colouring
def tint(ss, fc, ec, lw=0.5):
    res = []
    for s in ss:
        q = Solid(s.shape, s.o, s.U, s.V, s.t, fc, s.n, ec, lw, s.alpha, s.label); q.layer = s.layer; res.append(q)
    return res
new = lambda ss: tint(ss, NEW, NEW_EC, 0.6)
old = lambda ss: tint(ss, OLD, OLD_EC, 0.45)
def shift(ss, d): return [s.moved(d) for s in ss]

# ------------------------------------------------------------------ parts in place (X across, Y to the front, Z up)
def base(crop=None):
    g = D.base().solid()
    if crop: g = g.intersection(box(*crop))
    b = Solid(g, (0, 0, -T), (1, 0, 0), (0, 1, 0), T); b.layer = -1      # the base is the ground: always drawn first
    return [b]
def guides(crop=None, which=(-1, 1)):
    g = D.guide(1).solid()
    if crop: g = g.intersection(box(crop[0], -10, crop[1], 30))
    return [Solid(g, (s * D.GUIDE_X - T / 2, 0, 0), (0, 1, 0), (0, 0, 1), T) for s in which]
def side(which, crop=None):
    s = 1 if which == 'L' else -1
    g = D.side(which).solid()
    if crop: g = g.intersection(box(*crop) if s > 0 else box(-crop[2], crop[1], -crop[0], crop[3]))
    return [Solid(g, (s * D.SX0, 0, 0), (0, s, 0), (0, 0, 1), T, n=(s, 0, 0))]
def ties(which=(-1, 1), crop=None):
    g = D.tie(1).solid()
    if crop: g = g.intersection(box(-crop[1], 0, -crop[0], 200))        # u runs along -X
    return [Solid(g, (0, sy * D.TIE_Y - T / 2, 0), (-1, 0, 0), (0, 0, 1), T) for sy in which]
def key_at(sx, sy, out=0.0):
    """One tie key, lying flat, straight edge against the outside of the side, pushed in from the front.
    out = how far it is still pulled back (mm); 0 = pushed home."""
    seat = (D.KEY_HOLE_W - 1.0 - D.KEY_W[0]) / (D.KEY_W[1] - D.KEY_W[0]) * D.KEY_LEN   # where the key jams
    y_tip = sy * D.TIE_Y - seat + out
    return Solid(D.key(0).solid(), (sx * D.SX1, y_tip, ZC - T / 2), (0, 1, 0), (sx, 0, 0), T, n=(0, 0, sx * -1.0) if False else None)
def keys(out=0.0, which=((1, 1), (1, -1), (-1, 1), (-1, -1))):
    res = []
    for sx, sy in which:
        k = key_at(sx, sy, out)
        # centre the 6 mm thickness on the hole whatever way the slab was extruded
        k.o = k.o + (ZC - (k.o[2] + k.t * k.n[2] / 2)) * np.array([0, 0, 1.0])
        res.append(k)
    return res
def plugs(which=((1, 1), (1, -1), (-1, 1), (-1, -1))):
    ys = {1: D.FOOT[1] + D.SLIDE / 2, -1: -D.FOOT[0] + D.SLIDE / 2}
    return [Solid(D.plug(0).solid(), (sx * (D.SX0 + T / 2) - T / 2, ys[sy], 0), (0, 1, 0), (0, 0, 1), T) for sx, sy in which]
def trig_post(): return [Solid(D.trigger_post().solid(), (D.POST_X - T / 2, D.POST_Y, 0), (0, 1, 0), (0, 0, 1), T)]
def trig_key(): return [Solid(D.trigger_key().solid(), (D.POST_X - 30, D.POST_Y, 30.2), (1, 0, 0), (0, 1, 0), T)]
def trig_plug(): return [Solid(D.plug(0).solid(), (D.POST_X - T / 2, D.POST_Y - 8 - D.HOOK / 2, 0), (0, 1, 0), (0, 0, 1), T)]

def arm_parts(angle, tip=True, sensor=True, crop=None, tip_out=0.0):
    a = math.radians(angle)
    U = np.array([0, math.cos(a), math.sin(a)]); V = np.array([0, -math.sin(a), math.cos(a)])
    o = np.array([-T / 2, 0, D.AXLE_Z])
    shp = D.arm().solid()
    if crop:
        from shapely.ops import unary_union
        shp = shp.intersection(box(crop[0], -40, crop[1], 40))
        shp = unary_union([g for g in getattr(shp, 'geoms', [shp]) if g.geom_type == 'Polygon'])
    res = [Solid(shp, o, U, V, T)]
    if tip: res.append(Solid(D.release_tip(15).solid(), o + (D.L_ARM + tip_out) * U, U, V, T))
    if sensor: res.append(Solid(D.sensor_plate().solid(), np.array([T / 2, 0, D.AXLE_Z]) + 70 * U, U, V, 4, '#5A5F66'))
    return res, U, V

def washers(z, y, n, r, gap=0.0, x0=T / 2):
    res = []
    for s in (-1, 1):
        for i in range(n):
            a = x0 + gap + i * (T + gap * 0.25)
            res.append(cyl_x(a if s > 0 else -a - T, a + T if s > 0 else -a, y, z, r, '#EAD9B5'))
    return res
def bolt(x0, x1, y, z, r, head=1):
    """Bolt along X with its head at the +X end and a wing nut (drawn as a dark knob) at the other."""
    return [cyl_x(x0, x1, y, z, r, STEEL), cyl_x(x1 - 1, x1 + 6, y, z, r * 2.2, DARK), cyl_x(x0 - 2, x0 + 7, y, z, r * 2.6, '#55595F')]

def basket(pin, weights=0, ex=0.0, fl=0.0, wl=0.0):
    """pin = (y, z) of the hang bolt. ex / fl / wl explode the bails, floor and walls."""
    py, pz = pin
    fz = -D.LC - 34
    bails = [Solid(D.bail(1).solid(), (s * (D.BASKET / 2 + T / 2 + ex) - T / 2, py, pz), (0, 1, 0), (0, 0, 1), T) for s in (-1, 1)]
    floor = [Solid(D.floor_().solid(), (0, py, pz + fz - fl), (1, 0, 0), (0, 1, 0), T)]
    walls = [Solid(D.wall(1).solid(), (0, py + s * (D.BASKET / 2 + T / 2 + wl) - T / 2, pz), (-1, 0, 0), (0, 0, 1), T) for s in (-1, 1)]
    ws = [Solid(Point(0, 0).buffer(24, 24).difference(box(-3, 0, 3, 30)), (0, py, pz + fz + T + i * 9.5), (1, 0, 0), (0, 1, 0), 9, MASS)
          for i in range(weights)]
    return bails, floor, walls, ws

def seg(p0, p1, w, color):
    p0 = np.asarray(p0, float); p1 = np.asarray(p1, float)
    d = p1 - p0; L = np.linalg.norm(d); U = d / L
    V = np.cross([1.0, 0, 0], U)
    if np.linalg.norm(V) < 1e-6: V = np.array([0, 1.0, 0])
    V = V / np.linalg.norm(V)
    return Solid(box(0, -w / 2, L, w / 2), p0 - w / 2 * np.cross(U, V), U, V, w, color)

def frame(): return side('L') + side('R') + ties() + keys()

# ------------------------------------------------------------------ drawing helpers (all positions in mm)
def view(f, rect, solids, eye):
    ax = f.add_axes(rect); cam = Cam(eye); render(ax, solids, cam); return ax, cam
def arrow(ax, cam, a, b, lw=2.6, col=RED):
    ax.annotate('', xy=cam.p(b)[0], xytext=cam.p(a)[0], zorder=70,
                arrowprops=dict(arrowstyle='-|>', lw=lw, color=col, mutation_scale=17, shrinkA=0, shrinkB=0))
def badge(ax, cam, n, at, off=(0, 0), fs=11):
    p = cam.p(at)[0]; q = p + np.asarray(off, float)
    if np.hypot(*off) > 1:
        ax.plot([p[0], q[0]], [p[1], q[1]], color=INK, lw=0.9, zorder=71, solid_capstyle='round')
        ax.plot([p[0]], [p[1]], 'o', ms=3.2, color=INK, zorder=71)
    ax.text(q[0], q[1], str(n), fontsize=fs, fontweight='bold', color='white', ha='center', va='center', zorder=72,
            bbox=dict(boxstyle='circle,pad=0.28', fc=RED, ec='white', lw=1.0))
def note(ax, cam, text, at, off=(0, 0), fs=8.5, ha='center'):
    p = cam.p(at)[0]; q = p + np.asarray(off, float)
    if np.hypot(*off) > 1:
        ax.plot([p[0], q[0]], [p[1], q[1]], color='#666666', lw=0.6, zorder=65)
        ax.plot([p[0]], [p[1]], 'o', ms=2.4, color='#666666', zorder=65)
    ax.text(q[0], q[1], text, fontsize=fs, color=INK, ha=ha, va='center', zorder=66, linespacing=1.15,
            bbox=dict(boxstyle='round,pad=0.22', fc='white', ec='#888888', lw=0.5))
def mark(ax, cam, center, r, letter):
    c = cam.p(center)[0]
    ax.add_patch(Circle(c, r, fc='none', ec=INK, lw=1.0, ls=(0, (3, 2)), zorder=68))
    ax.text(c[0] + r * 0.78, c[1] + r * 0.78, letter, fontsize=9, fontweight='bold', color='white', ha='center', va='center', zorder=69,
            bbox=dict(boxstyle='round,pad=0.2', fc=INK, ec='white', lw=0.8))
def fit(ax, pad=14):
    ax.relim(); ax.autoscale_view()
    x0, x1 = ax.get_xlim(); y0, y1 = ax.get_ylim()
    ax.set_xlim(x0 - pad, x1 + pad); ax.set_ylim(y0 - pad, y1 + pad)
def detail(f, rect, solids, eye, center, r, letter):
    """A round close-up. Returns (ax, cam); call seal() after adding arrows and notes."""
    ax, cam = view(f, rect, solids, eye)
    ax._c, ax._r, ax._letter = cam.p(center)[0], r, letter
    return ax, cam
def seal(ax):
    c, r = ax._c, ax._r
    clip = Circle(c, r, transform=ax.transData)
    for a in list(ax.patches) + list(ax.lines): a.set_clip_path(clip)
    ax.add_patch(Circle(c, r, fc='none', ec=INK, lw=1.5, zorder=90))
    ax.set_xlim(c[0] - r * 1.08, c[0] + r * 1.08); ax.set_ylim(c[1] - r * 1.08, c[1] + r * 1.08)
    ax.text(c[0] - r * 0.74, c[1] + r * 0.74, ax._letter, fontsize=10, fontweight='bold', color='white', ha='center', va='center', zorder=95,
            bbox=dict(boxstyle='round,pad=0.25', fc=INK, ec='white', lw=0.8))
def save(f, name):
    f.savefig(os.path.join(OUT, name + '.pdf')); f.savefig(os.path.join(OUT, name + '.png'), dpi=120); plt.close(f)
def flat(ax, shape, fc, ec=INK, lw=0.6, dx=0.0, dy=0.0, z=2, hatch=None):
    for g in (shape.geoms if hasattr(shape, 'geoms') else [shape]):
        ax.add_patch(MP(np.array(g.exterior.coords) + [dx, dy], fc=fc, ec=ec, lw=lw, zorder=z, hatch=hatch))
        for r in g.interiors: ax.add_patch(MP(np.array(r.coords) + [dx, dy], fc='white', ec=ec, lw=lw * 0.8, zorder=z))
def arrow2(ax, a, b, lw=2.4):
    ax.annotate('', xy=b, xytext=a, zorder=70, arrowprops=dict(arrowstyle='-|>', lw=lw, color=RED, mutation_scale=15, shrinkA=0, shrinkB=0))
def num2(ax, n, xy, fs=10):
    ax.text(xy[0], xy[1], str(n), fontsize=fs, fontweight='bold', color='white', ha='center', va='center', zorder=72,
            bbox=dict(boxstyle='circle,pad=0.28', fc=RED, ec='white', lw=1.0))

W, H = 7.0, 3.5      # every step figure is this size, so they line up in the guide
EYE = (1.0, 0.85, 0.7)

# ------------------------------------------------------------------ 1 parts
def inventory():
    items = [('Base', D.base(), '1'), ('Side L and side R', D.side('L'), '2'), ('Arm', D.arm(), '1'), ('Tie', D.tie(1), '2'),
             ('Trough guide', D.guide(1), '2'), ('Basket bail', D.bail(1), '2'), ('Basket floor', D.floor_(), '1'),
             ('Basket wall', D.wall(1), '2'), ('Trigger post', D.trigger_post(), '1'), ('Trigger key', D.trigger_key(), '1'),
             ('Release tips\n0 / 15 / 30', D.release_tip(15), '3'), ('Sling ring', D.ring(0), '3'), ('Lock plug', D.plug(0), '5'),
             ('Tie key', D.key(0), '8'), ('Axle washer\n(large)', D.washer('axle', 0), '20'), ('Hang washer\n(small)', D.washer('hang', 0), '12')]
    f, axs = plt.subplots(2, 8, figsize=(W, 3.3))
    for ax, (nm, p, q) in zip(axs.flat, items):
        flat(ax, p.solid(), WOOD, lw=0.5)
        ax.set_aspect('equal', adjustable='datalim'); ax.margins(0.16); ax.autoscale_view(); ax.axis('off')
        ax.set_title(nm, fontsize=7, pad=3)
        ax.text(0.98, 0.02, '× ' + q, transform=ax.transAxes, ha='right', va='bottom', fontsize=8, fontweight='bold', color='white',
                bbox=dict(boxstyle='round,pad=0.25', fc=RED, ec='none'))
    f.tight_layout(h_pad=1.0, w_pad=0.3); save(f, 'd01_inventory')

# ------------------------------------------------------------------ 2 trough guides
def step2():
    f = plt.figure(figsize=(W, H))
    ax, cam = view(f, [0.0, 0.0, 0.66, 1.0], old(base()) + new(shift(guides(), (0, 0, 55))), EYE)
    for yc in (-250.0, -60.0, 110.0):
        arrow(ax, cam, P(D.GUIDE_X + 9, yc, 46), P(D.GUIDE_X + 9, yc, 6), lw=2.0)
    badge(ax, cam, 1, P(D.GUIDE_X, -160, 70), (-10, 62))
    note(ax, cam, 'FRONT', P(0, 205, 0), (0, 0), fs=9)
    arrow(ax, cam, P(0, 262, 0), P(0, 330, 0), lw=2.0, col=INK)
    note(ax, cam, 'throws this way', P(0, 345, 0), (40, -16), fs=8)
    mark(ax, cam, P(D.GUIDE_X, 110, 22), 46, 'A'); fit(ax)
    ad, cd = detail(f, [0.66, 0.08, 0.33, 0.84], old(base(crop=(-20, 50, 100, 170))) + new(shift(guides(crop=(55, 165), which=(1,)), (0, 0, 16))),
                    (1.0, 0.75, 0.6), P(D.GUIDE_X, 110, 8), 52, 'A')
    arrow(ad, cd, P(D.GUIDE_X + 8, 110, 30), P(D.GUIDE_X + 8, 110, 4))
    note(ad, cd, 'tab', P(D.GUIDE_X + 3, 110, 13), (34, 26), fs=9)
    note(ad, cd, 'slot', P(D.GUIDE_X + 3, 124, 0), (30, -22), fs=9)
    seal(ad); save(f, 'd02_guides')

# ------------------------------------------------------------------ 3 frame: ties through both sides, keys
def step3():
    f = plt.figure(figsize=(W, H))
    ex = 62
    solids = new(shift(side('L'), (ex, 0, 0)) + shift(side('R'), (-ex, 0, 0)) + ties())
    ax, cam = view(f, [0.0, 0.0, 0.60, 1.0], solids, (1.0, 0.8, 0.55))
    for sy in (1, -1):
        arrow(ax, cam, P(D.SX1 + ex + 40, sy * D.TIE_Y, ZC + 26), P(D.SX1 + 22, sy * D.TIE_Y, ZC + 26), lw=2.2)
        arrow(ax, cam, P(-D.SX1 - ex - 40, sy * D.TIE_Y, ZC + 26), P(-D.SX1 - 22, sy * D.TIE_Y, ZC + 26), lw=2.2)
    badge(ax, cam, 1, P(0, D.TIE_Y, ZC + 17), (-6, 78))
    badge(ax, cam, 2, P(D.SX1 + ex + 20, D.TIE_Y, ZC + 26), (40, 50))
    note(ax, cam, 'SIDE L', P(D.SX1 + ex, 0, D.AXLE_Z + 26), (36, 26), fs=8)
    note(ax, cam, 'SIDE R', P(-D.SX1 - ex, 0, D.AXLE_Z + 26), (-36, 26), fs=8)
    note(ax, cam, 'tie', P(0, -D.TIE_Y, ZC), (-70, -52), fs=8)
    fit(ax)
    # close-up: the key, seen from outside the frame
    sol = old(side('L', crop=(D.TIE_Y - 70, 0, D.TIE_Y + 70, 140))) + old(ties(which=(1,), crop=(40, 100))) + new(keys(out=34, which=((1, 1),)))
    ad, cd = detail(f, [0.60, 0.04, 0.40, 0.92], sol, (1.0, 0.62, 0.55), P(D.SX1 + 6, D.TIE_Y + 22, ZC), 52, 'B')
    arrow(ad, cd, P(D.SX1 + 24, D.TIE_Y + 78, ZC + 3), P(D.SX1 + 24, D.TIE_Y + 46, ZC + 3))
    badge(ad, cd, 3, P(D.SX1 + 8, D.TIE_Y + 56, ZC + 3), (-2, 32))
    note(ad, cd, 'straight edge\nagainst the side', P(D.SX1 + 0.5, D.TIE_Y + 46, ZC + 3), (-10, -28), fs=7.6)
    note(ad, cd, 'flat, thin\nend first', P(D.SX1 + 6, D.TIE_Y + 23, ZC + 3), (-27, -24), fs=7.6)
    note(ad, cd, 'tie end', P(D.SX1 + 16, D.TIE_Y, ZC + 13), (6, 26), fs=7.6)
    seal(ad); save(f, 'd03_frame')

# ------------------------------------------------------------------ 4 frame onto the base: drop, slide back, plug
def hook_section(ax, stage, kind='foot'):
    """Side elevation of one hooked joint, front to the right (u = Y, v = Z).
    foot: drops in 10 mm forward, slides BACK.  post: drops in 10 mm back, slides FORWARD."""
    if kind == 'foot':
        y0, y1 = D.FOOT[0], D.FOOT[1] + D.SLIDE                   # the slot in the base
        part = D.side('L').solid().intersection(box(88, -14, 170, 24)); start = D.SLIDE
        plug_y = D.FOOT[1] + D.SLIDE / 2; lo, hi = 70, 186
        words = {1: 'drop in', 2: 'slide BACK 10 mm', 3: 'lock plug in front'}
    else:
        y0, y1 = -8 - D.HOOK, 8
        part = D.trigger_post().solid(); start = -D.HOOK
        plug_y = -8 - D.HOOK / 2; lo, hi = -66, 50
        words = {1: 'drop in', 2: 'slide FORWARD 10 mm', 3: 'lock plug behind'}
    for a, b in ((lo, y0 - 0.2), (y1 + 0.2, hi)):
        ax.add_patch(MP([(a, -T), (b, -T), (b, 0), (a, 0)], fc='#D8CFBD', ec=INK, lw=0.7, zorder=3))
    lift = 16 if kind == 'foot' else 20
    dy, dz = {1: (start, lift), 2: (0, 0), 3: (0, 0)}[stage]
    if stage == 2: flat(ax, part, 'none', ec='#999999', lw=0.6, dx=start, z=4)
    flat(ax, part, NEW if stage < 3 else OLD, ec=NEW_EC if stage < 3 else OLD_EC, lw=0.8, dx=dy, dy=dz, z=5)
    top = part.bounds[3]; sgn = 1 if kind == 'foot' else -1
    xa = (part.bounds[2] + start + 9) if kind == 'foot' else (part.bounds[0] + start - 9)
    if stage == 1: arrow2(ax, (xa, top + lift + 2), (xa, top - 6))
    if stage == 2: arrow2(ax, (xa + sgn * 14, top * 0.55), (xa - sgn * 8, top * 0.55))
    if stage == 3:
        flat(ax, D.plug(0).solid(), NEW, ec=NEW_EC, lw=0.8, dx=plug_y, dy=13, z=6)
        arrow2(ax, (plug_y + sgn * 19, 30), (plug_y + sgn * 19, 8))
    yt = max(top + lift, 40) + 13
    num2(ax, stage, (lo + 9, yt), fs=9); ax.text(lo + 9 + (hi - lo) * 0.10, yt, words[stage], fontsize=8.2, va='center', ha='left')
    ax.text(lo + 2, -11.5, 'base', fontsize=6.5, color='#555555', va='center')
    ax.set_xlim(lo - 4, hi + 4); ax.set_ylim(-17, yt + 9); ax.set_aspect('equal'); ax.axis('off')

def step4():
    f = plt.figure(figsize=(W, H))
    lift = (0, D.SLIDE, 60)
    ax, cam = view(f, [0.0, 0.0, 0.60, 1.0], old(base() + guides()) + new(shift(frame(), lift)), EYE)
    arrow(ax, cam, P(D.SX1 + 14, D.FOOT[1] + 30, 62), P(D.SX1 + 14, D.FOOT[1] + 30, 10))
    arrow(ax, cam, P(D.SX1 + 14, -D.FOOT[0] + 30, 62), P(D.SX1 + 14, -D.FOOT[0] + 30, 10))
    badge(ax, cam, 1, P(D.SX1 + 14, D.FOOT[1] + 30, 40), (52, 30))
    arrow(ax, cam, P(D.SX1 + 40, 215, 0), P(D.SX1 + 40, 160, 0))
    badge(ax, cam, 2, P(D.SX1 + 40, 190, 0), (44, -26))
    note(ax, cam, 'FRONT', P(-72, 236, 0), (0, 0), fs=8)
    note(ax, cam, 'BACK', P(-95, -292, 0), (-22, 10), fs=8)
    fit(ax)
    for i, st in enumerate((1, 2, 3)):
        a2 = f.add_axes([0.60, 0.69 - i * 0.31, 0.40, 0.30]); hook_section(a2, st)
    f.text(0.80, 0.012, 'side view of one foot:   BACK ←    → FRONT', fontsize=6.8, color='#555555', ha='center', va='bottom')
    save(f, 'd04_clip')

# ------------------------------------------------------------------ 5 trigger
def step5():
    f = plt.figure(figsize=(W, H))
    crop = (-10, D.POST_Y - 66, 112, D.POST_Y + 84)
    sol = old(base(crop=crop) + guides(crop=(D.POST_Y - 66, D.POST_Y + 84), which=(1,)))
    sol += new(trig_post() + trig_plug() + shift(trig_key(), (62, 0, 0)))
    ax, cam = view(f, [0.0, 0.0, 0.46, 1.0], sol, (1.0, -0.55, 0.6))
    arrow(ax, cam, P(D.POST_X + 132, D.POST_Y - 20, 36), P(D.POST_X + 78, D.POST_Y - 20, 36))
    badge(ax, cam, 4, P(D.POST_X + 104, D.POST_Y - 20, 36), (-30, -34))
    note(ax, cam, 'trigger key', P(D.POST_X + 110, D.POST_Y + 6, 36), (34, 34), fs=8)
    note(ax, cam, 'post', P(D.POST_X + 3, D.POST_Y + 10, 48), (44, 40), fs=8)
    note(ax, cam, 'lock plug', P(D.POST_X + 3, D.POST_Y - 20, 9), (-52, -30), fs=8)
    note(ax, cam, 'trough guide', P(D.GUIDE_X, D.POST_Y - 40, 18), (-40, 44), fs=8)
    fit(ax)
    for i, st in enumerate((1, 2, 3)):
        a2 = f.add_axes([0.47, 0.69 - i * 0.31, 0.33, 0.30]); hook_section(a2, st, 'post')
    f.text(0.635, 0.012, 'side view of the post:   BACK ←    → FRONT', fontsize=6.8, color='#555555', ha='center', va='bottom')
    a2 = f.add_axes([0.82, 0.10, 0.17, 0.84])                       # where on the base
    flat(a2, D.base().solid(), OLD, ec=OLD_EC, lw=0.6)
    a2.add_patch(Circle((D.POST_X, D.POST_Y), 34, fc='none', ec=RED, lw=1.8, zorder=5))
    a2.text(0, 222, 'FRONT', fontsize=7, ha='center', va='center')
    a2.text(0, -332, 'trigger slot:\nat the BACK,\nbeside the trough', fontsize=7, ha='center', va='top', linespacing=1.15)
    a2.set_xlim(-135, 135); a2.set_ylim(-440, 262); a2.set_aspect('equal'); a2.axis('off')
    save(f, 'd05_trigger')

# ------------------------------------------------------------------ 6 arm: release tip, cords, sensor
def step6():
    f = plt.figure(figsize=(W, H))
    side_on = (1.0, 0.0, 0.0)
    arm, U, V = arm_parts(0.0)
    ax, cam = view(f, [0.0, 0.52, 1.0, 0.48], old([arm[0]]) + new([arm[1]]) + [arm[2]], side_on)
    Z0 = D.AXLE_Z
    # sling laid out under the arm, to scale: 360 mm from the tip to the middle of the pouch
    hole = np.array([D.L_ARM - 27, Z0 - 4]); pc = np.array([D.L_ARM - 360, Z0 - 54]); rg = np.array([pc[0] - 92, Z0 - 54])
    ax.plot([hole[0], hole[0] - 16, pc[0] + 30], [hole[1], Z0 - 54, Z0 - 54], color='#8E5B2E', lw=1.4, zorder=40)
    ax.add_patch(FancyBboxPatch((pc[0] - 30, pc[1] - 9), 60, 18, boxstyle='round,pad=0,rounding_size=8', fc=RED, ec='#7B241C', lw=0.8, zorder=41))
    ax.plot([pc[0] - 30, rg[0] + 16], [pc[1], rg[1]], color='#8E5B2E', lw=1.4, zorder=40)
    flat(ax, D.ring(0).solid(), NEW, ec=NEW_EC, dx=rg[0], dy=rg[1], z=42)
    tr = np.array([D.L_ARM - 50, Z0])
    ax.add_patch(matplotlib.patches.Ellipse((tr[0], tr[1] + 16), 13, 34, fc='none', ec=DARK, lw=1.4, zorder=40))
    ax.annotate('', xy=(pc[0], Z0 - 76), xytext=(D.L_ARM, Z0 - 76), arrowprops=dict(arrowstyle='<->', lw=0.8, color=INK))
    ax.text((pc[0] + D.L_ARM) / 2 - 40, Z0 - 76, '360 mm', fontsize=8, ha='center', va='center', bbox=dict(fc='white', ec='none', pad=1.5))
    note(ax, cam, 'pouch', P(0, pc[0] + 30, pc[1]), (30, 0), fs=7.8)
    note(ax, cam, 'sling ring', P(0, rg[0] - 4, rg[1] - 10), (-10, -18), fs=7.8)
    note(ax, cam, 'sensor plate', P(0, 70, Z0 + 22), (0, 18), fs=7.8)
    note(ax, cam, 'hang hole', P(0, -D.A_ARM, Z0), (-4, 34), fs=7.8)
    note(ax, cam, 'axle hole', P(0, 0, Z0), (-26, 38), fs=7.8)
    badge(ax, cam, 1, P(0, D.L_ARM + 22, Z0 + 4), (14, 32))
    badge(ax, cam, 2, P(0, 250, Z0 - 54), (0, 0), fs=9)
    badge(ax, cam, 3, P(0, tr[0] - 6, Z0 + 26), (-24, 14), fs=9)
    badge(ax, cam, 4, P(0, 108, Z0 - 6), (0, 0), fs=9)
    mark(ax, cam, P(0, D.L_ARM - 6, Z0), 46, 'C'); fit(ax, pad=10)
    # close-up of the tip
    arm2, U, V = arm_parts(0.0, sensor=False, crop=(D.L_ARM - 100, D.L_ARM + 5), tip_out=12)
    ad, cd = detail(f, [0.29, 0.0, 0.42, 0.55], old([arm2[0]]) + new([arm2[1]]), side_on, P(0, D.L_ARM - 8, Z0 - 2), 58, 'C')
    arrow2(ad, (D.L_ARM + 30, Z0 + 22), (D.L_ARM + 4, Z0 + 22))
    note(ad, cd, 'trigger loop', P(0, D.L_ARM - 50, Z0), (26, 30), fs=7.6)
    note(ad, cd, 'sling cord', P(0, D.L_ARM - 27, Z0 - 4), (-8, -30), fs=7.6)
    note(ad, cd, 'prong: towards\nthe sling side', P(0, D.L_ARM + 38, Z0 - 5), (-24, -25), fs=7.6)
    seal(ad)
    f.text(0.02, 0.36, 'The three release tips are\nengraved 0, 15 and 30.\nStart with 15. Its dovetail\nslides into the end of the arm.', fontsize=8, va='top', linespacing=1.3)
    f.text(0.73, 0.36, 'The sling side of the arm\nis the side nearest the\nengraved word "sling".', fontsize=8, va='top', linespacing=1.3)
    save(f, 'd06_arm')

# ------------------------------------------------------------------ stack diagram for a bolt
def stack(ax, items, title):
    """items: (label, width, height, colour, edge). Drawn left to right along the bolt."""
    x = 0; mids = []
    tot = sum(i[1] for i in items) + 3 * (len(items) - 1)
    ax.plot([-10, tot + 10], [0, 0], color=STEEL, lw=3.2, zorder=1, solid_capstyle='butt')
    for k, (lab, w, h, fc, ec) in enumerate(items):
        ax.add_patch(MP([(x, -h / 2), (x + w, -h / 2), (x + w, h / 2), (x, h / 2)], fc=fc, ec=ec, lw=0.7, zorder=3))
        up = k % 2 == 0; far = 52 if lab == 'washer' else 30
        ax.plot([x + w / 2, x + w / 2], [h / 2 if up else -h / 2, far if up else -far], color='#666666', lw=0.5, zorder=2)
        ax.text(x + w / 2, far + 2 if up else -far - 2, lab, fontsize=7.3, ha='center', va='bottom' if up else 'top', linespacing=1.1)
        x += w + 3
    ax.text(tot / 2, 62, title, fontsize=8, fontweight='bold', ha='center', va='bottom')
    ax.set_xlim(-22, tot + 22); ax.set_ylim(-70, 76); ax.set_aspect('equal'); ax.axis('off')

def bolt_stack(ax, part, n, wr, title):
    wash = ('washer', 2.5, wr * 2, '#B9BEC5', INK)
    ply = lambda lab, h, fc=NEW, ec=NEW_EC: (lab, 9, h, fc, ec)
    many = (f'{n} wooden\nwashers', 9 * 2.4, wr * 2 + 6, '#EAD9B5', INK)
    stack(ax, [('bolt\nhead', 7, 13, DARK, DARK), wash, ply(part, 40), many, ply('ARM', 34, OLD, OLD_EC), many, ply(part, 40), wash,
               ('wing\nnut', 9, 22, '#55595F', DARK)], title)

# ------------------------------------------------------------------ 7 basket
def step7():
    f = plt.figure(figsize=(W, H))
    pin = (0.0, D.AXLE_Z - D.A_ARM)
    arm, U, V = arm_parts(90.0, tip=False, sensor=False, crop=(-170, -60))
    bails, floor, walls, _ = basket(pin, ex=36, fl=46, wl=44)
    hw = washers(pin[1], 0, 5, 10, gap=3.0)
    bl = bolt(-D.BASKET / 2 - 36 - 22, D.BASKET / 2 + 36 + 22, 0, pin[1], 3)
    ax, cam = view(f, [0.0, 0.0, 0.50, 1.0], old(arm) + new(bails + floor + walls) + hw + bl, (1.0, 0.75, 0.42))
    fzc = pin[1] - D.LC - 34
    arrow(ax, cam, P(D.BASKET / 2 + 64, 0, pin[1] + 22), P(D.BASKET / 2 + 26, 0, pin[1] + 22), lw=2.0)
    badge(ax, cam, 1, P(D.BASKET / 2 + 40, 0, pin[1] + 22), (34, 36))
    arrow(ax, cam, P(0, 0, fzc - 40), P(0, 0, fzc - 8), lw=2.0)
    badge(ax, cam, 2, P(0, 0, fzc - 26), (-46, -6))
    arrow(ax, cam, P(0, D.BASKET / 2 + 62, pin[1] - D.LC), P(0, D.BASKET / 2 + 26, pin[1] - D.LC), lw=2.0)
    badge(ax, cam, 3, P(0, D.BASKET / 2 + 44, pin[1] - D.LC), (40, -34))
    note(ax, cam, 'bail', P(D.BASKET / 2 + 39, -30, pin[1] - D.LC + 10), (-56, 30), fs=8)
    note(ax, cam, 'floor', P(20, 20, fzc - 46), (52, -20), fs=8)
    note(ax, cam, 'wall', P(-10, D.BASKET / 2 + 47, pin[1] - D.LC + 22), (62, 30), fs=8)
    note(ax, cam, 'short end\nof the arm', P(0, 0, pin[1] + 62), (70, 6), fs=8)
    fit(ax)
    a2 = f.add_axes([0.50, 0.30, 0.50, 0.62]); bolt_stack(a2, 'bail', 5, 10, 'Order on the M6 hang bolt')
    f.text(0.52, 0.24, 'Tighten the wing nut until the bails just hold the floor\nand walls. The basket must still swing on the bolt.',
           fontsize=8, va='top', linespacing=1.3)
    save(f, 'd07_basket')

# ------------------------------------------------------------------ 8 arm onto the frame
def built(short=False):
    if short: return base(crop=(-100, -200, 100, 200)) + guides(crop=(-200, 200)) + frame() + plugs()
    return base() + guides() + frame() + plugs() + trig_post() + trig_key() + trig_plug()

def step8():
    f = plt.figure(figsize=(W, 4.3))
    pin = (0.0, D.AXLE_Z - D.A_ARM)
    arm, U, V = arm_parts(90.0)
    bails, floor, walls, _ = basket(pin)
    hang = washers(pin[1], 0, 5, 10) + [cyl_x(-D.BASKET / 2 - T - 8, D.BASKET / 2 + T + 8, 0, pin[1], 3, STEEL)]
    axw = washers(D.AXLE_Z, 0, 9, 12)
    ab = shift(bolt(-D.SX1 - 14, D.SX1 + 12, 0, D.AXLE_Z, 4), (70, 0, 0))
    ax, cam = view(f, [0.0, 0.0, 0.46, 1.0], old(built(short=True)) + new(arm[:2]) + [arm[2]] + new(bails + floor + walls) + hang + axw + ab, (1.0, 0.8, 0.42))
    arrow(ax, cam, P(D.SX1 + 150, 0, D.AXLE_Z + 14), P(D.SX1 + 96, 0, D.AXLE_Z + 14), lw=2.2)
    badge(ax, cam, 2, P(D.SX1 + 120, 0, D.AXLE_Z + 14), (-44, 30))
    badge(ax, cam, 1, P(0, 0, D.AXLE_Z + 190), (60, 10))
    note(ax, cam, 'long end up', P(0, 0, D.AXLE_Z + 330), (76, -6), fs=8)
    note(ax, cam, 'basket hangs\nbetween the sides', P(D.BASKET / 2 + T, 30, pin[1] - D.LC), (150, 40), fs=8)
    mark(ax, cam, P(0, 0, D.AXLE_Z), 62, 'D'); fit(ax)
    a2 = f.add_axes([0.46, 0.30, 0.54, 0.62]); bolt_stack(a2, 'SIDE', 9, 12, 'D   Order on the M8 axle bolt')
    f.text(0.48, 0.24, 'Tighten the wing nut until it is snug, then back it off a\nlittle. The arm must swing freely.', fontsize=8, va='top', linespacing=1.3)
    save(f, 'd08_axle')

# ------------------------------------------------------------------ 9 loaded and cocked
def step9():
    f = plt.figure(figsize=(W, 4.2))
    ang = 180 + math.degrees(math.asin((D.AXLE_Z - 40) / D.L_ARM))
    arm, U, V = arm_parts(ang)
    a = math.radians(ang)
    pin = (-D.A_ARM * math.cos(a), D.AXLE_Z - D.A_ARM * math.sin(a))
    tip = np.array([0, D.L_ARM * math.cos(a), D.AXLE_Z + D.L_ARM * math.sin(a)])
    teye = np.array([0, (D.L_ARM - 50) * math.cos(a), D.AXLE_Z + (D.L_ARM - 50) * math.sin(a)])
    pouch = np.array([0, tip[1] + 0.95 * 360, 14])
    kx = D.POST_X - 14
    bails, floor, walls, ws = basket(pin, weights=6)
    hang = [cyl_x(-D.BASKET / 2 - T - 8, D.BASKET / 2 + T + 8, pin[0], pin[1], 3, STEEL)]
    cords = [seg(tip, pouch, 2.5, '#8E5B2E'), seg(teye, (kx, D.POST_Y, 37), 2.5, DARK),
             seg((D.POST_X + 48, D.POST_Y, 33), (D.POST_X + 150, D.POST_Y - 40, 6), 2.2, '#3465A4')]
    bag = [box_solid(-14, pouch[1] - 14, 3, 14, pouch[1] + 16, 26, RED)]
    scene = tint(built(), WOOD, INK, 0.45) + tint(arm[:2], '#D9C29A', INK, 0.45) + [arm[2]] + tint(bails + floor + walls, WOOD, INK, 0.45) \
        + ws + hang + washers(D.AXLE_Z, 0, 9, 12) + bolt(-D.SX1 - 14, D.SX1 + 12, 0, D.AXLE_Z, 4) + cords + bag
    ax, cam = view(f, [0.0, 0.0, 0.70, 1.0], scene, (1.0, 0.55, 0.48))
    badge(ax, cam, 1, P(0, pin[0], pin[1] - D.LC), (120, 60))
    badge(ax, cam, 2, P(kx, D.POST_Y, 40), (-86, 46))
    badge(ax, cam, 3, P(0, pouch[1], 28), (90, 54))
    arrow(ax, cam, P(D.POST_X + 150, D.POST_Y - 40, 6), P(D.POST_X + 235, D.POST_Y - 74, 6), lw=2.2)
    badge(ax, cam, 5, P(D.POST_X + 195, D.POST_Y - 58, 6), (0, -34))
    note(ax, cam, 'pull cord', P(D.POST_X + 110, D.POST_Y - 24, 16), (36, -44), fs=8)
    arrow(ax, cam, P(0, 262, 0), P(0, 345, 0), lw=2.2, col=INK)
    note(ax, cam, 'throws this way', P(0, 350, 0), (-60, -30), fs=8)
    mark(ax, cam, P(kx, D.POST_Y, 36), 44, 'E'); fit(ax)
    # close-up: loop over the trigger key
    crop = (-10, D.POST_Y - 60, 110, D.POST_Y + 70)
    sol = old(base(crop=crop) + guides(crop=(D.POST_Y - 60, D.POST_Y + 70), which=(1,))) + tint(trig_post() + trig_plug(), WOOD, INK) \
        + tint(trig_key(), NEW, NEW_EC) + [seg((kx, D.POST_Y, 37), (kx - 8, D.POST_Y - 6, 120), 2.5, DARK), seg((kx, D.POST_Y - 5, 31), (kx, D.POST_Y + 5, 31), 2.5, DARK)]
    ad, cd = detail(f, [0.70, 0.30, 0.30, 0.66], sol, (1.0, -0.62, 0.62), P(D.POST_X - 4, D.POST_Y, 40), 60, 'E')
    note(ad, cd, 'loop over\nthe key', P(kx, D.POST_Y, 66), (22, 6), fs=7.6)
    note(ad, cd, 'post', P(D.POST_X + 3, D.POST_Y - 8, 46), (-40, -4), fs=7.6)
    arrow(ad, cd, P(D.POST_X + 50, D.POST_Y - 18, 42), P(D.POST_X + 88, D.POST_Y - 18, 42), lw=2.0)
    seal(ad)
    f.text(0.71, 0.24, 'Pulling the cord slides the\nkey out from under the loop.', fontsize=8, va='top', linespacing=1.3)
    save(f, 'd09_cocked')

def steps():
    inventory(); step2(); step3(); step4(); step5(); step6(); step7(); step8(); step9()
    for old_name in ('d03_sides', 'd04_ties'):
        for ext in ('.pdf', '.png'):
            p = os.path.join(OUT, old_name + ext)
            if os.path.exists(p): os.replace(p, os.path.join(OUT, '_old_' + old_name + ext))

if __name__ == '__main__':
    only = [a for a in sys.argv[1:] if not a.startswith('-')]
    if only:
        for n in only: globals()[n]()
    else: steps()
    print(sorted(x for x in os.listdir(OUT) if not x.startswith('_')))
