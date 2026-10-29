"""Assembly-step drawings for the 75 % knock-down trebuchet, built from the real part shapes in gen75.py."""
import math, os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from shapely.geometry import Point, box, Polygon
from shapely.ops import unary_union
from shapely import affinity
import gen75 as G
from iso import Solid, Cam, render, box_solid, cyl_x

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'steps')
os.makedirs(OUT, exist_ok=True)
WOOD, WOOD2, GUS, STEEL, ALU, SAND, NEW = '#E2CFA8', '#CDB48A', '#B8996A', '#7A8088', '#C9CED4', '#D8C08A', '#F2B36B'
X0, X1 = G.SIDE_X0, G.SIDE_X1

# ---------------------------------------------------------------- components (global coordinates)
def sx(side): return 1 if side == 'A' else -1

def panel(side, x=None, color=WOOD, layer=None):
    s = sx(side)
    p = G.side_panel(side, layer or 1).solid()
    t = G.T if layer else G.TT
    xin = X0 if x is None else x
    return Solid(p, (s * xin, 0, 0), (0, s, 0), (0, 0, 1), t, color, n=(s, 0, 0))

def rail(side, color=WOOD, layer=None, pieces=None, dx=0.0):
    s = sx(side)
    ps = [p for p in G.rail_pieces(side) if (layer is None and '1_' in p.name.split('_')[1] + '_') or
          (layer is not None and p.name.startswith(f'rail_{side}{layer}_'))]
    if layer is None:
        shape = unary_union([p.solid() for p in G.rail_pieces(side) if p.name.startswith(f'rail_{side}1_')])
        return [Solid(shape, (s * (X0 + dx), 0, 0), (0, s, 0), (0, 0, 1), G.TT, color, n=(s, 0, 0))]
    return [Solid(p.solid(), (s * (X0 + dx), 0, 0), (0, s, 0), (0, 0, 1), G.T, color, n=(s, 0, 0)) for p in ps]

def gussets(side, color=GUS, dx=0.0, dz=0.0):
    s = sx(side); g = G.gusset(0).solid(); out = []
    for y in (-177.5, 177.5):
        out.append(Solid(g, (s * (X1 + dx), y, dz), (0, 1, 0), (0, 0, 1), G.T, color, n=(s, 0, 0)))
        out.append(Solid(g, (s * (X0 - dx), y, dz), (0, 1, 0), (0, 0, 1), G.T, color, n=(-s, 0, 0)))
    return out

def cap(side, dz=0.0, color=GUS, split=0.0):
    s = sx(side); xc = s * (X0 + G.TT / 2)
    lo = Solid(G.cap('lower').solid(), (xc, 0, G.PANEL_TOP + dz), (0, 1, 0), (1, 0, 0), G.T, color, n=(0, 0, 1))
    up = Solid(G.cap('upper').solid(), (xc, 0, G.PANEL_TOP + G.T + dz + split), (0, 1, 0), (1, 0, 0), G.T, color, n=(0, 0, 1))
    return [lo, up]

def studs(side, dz=0.0, length=40.0):
    s = sx(side); xc = s * (X0 + G.TT / 2); out = []
    for y in (-G.PB_BOLT_PITCH / 2, G.PB_BOLT_PITCH / 2):
        out.append(Solid(Point(0, 0).buffer(5, 12), (xc, y, G.PANEL_TOP + dz), (1, 0, 0), (0, 1, 0), length, STEEL, n=(0, 0, 1)))
        out.append(Solid(Point(0, 0).buffer(9.9, 6), (xc, y, G.PANEL_TOP + dz), (1, 0, 0), (0, 1, 0), 6.4, STEEL, n=(0, 0, 1)))
    return out

def knobs(side, dz=0.0):
    s = sx(side); xc = s * (X0 + G.TT / 2); out = []
    for y in (-G.PB_BOLT_PITCH / 2, G.PB_BOLT_PITCH / 2):
        out.append(Solid(Point(0, 0).buffer(16, 5), (xc, y, G.CAP_Z + 14 + dz), (1, 0, 0), (0, 1, 0), 16, '#2B2B2B', n=(0, 0, 1)))
    return out

def pillow(side, dx=0.0, dz=0.0):
    s = sx(side); xc = s * (X0 + G.TT / 2) + s * dx
    base = box_solid(xc - 19, -G.PB_LEN / 2, G.CAP_Z + dz, xc + 19, G.PB_LEN / 2, G.CAP_Z + 14 + dz, STEEL)
    house = cyl_x(xc - 19, xc + 19, 0, G.AXLE_Z + dz, 31, STEEL)
    return [base, house]

def xmember(name, color=WOOD2, dz=0.0):
    y = G.XM_Y[name]
    return Solid(G.cross_member(name, 1).solid(), (0, y - G.T, dz), (1, 0, 0), (0, 0, 1), G.TT, color, n=(0, 1, 0))

def wedge(name, side, dy=0.0, color='#8B6B3E'):
    s = sx(side); y = G.XM_Y[name]
    xc = s * (G.WEDGE_HOLE[0] + G.WEDGE_HOLE[1]) / 2
    return Solid(G.wedge(0).solid(), (xc, y - 50 + dy, G.WEDGE_Z - 3), (0, 1, 0), (s, 0, 0), G.T, color, n=(0, 0, 1))

def brace(side, color=WOOD, dx=0.0, dz=0.0):
    s = sx(side)
    return Solid(G.brace(1).solid(), (s * dx, G.T, dz), (s, 0, 0), (0, 0, 1), G.TT, color, n=(0, 1, 0))

def pins(side):
    s = sx(side); out = []
    for (x, z) in ((X0 - 11, G.BRACE_TOP[1]), G.BRACE_BOT):
        out.append(Solid(Point(0, 0).buffer(4, 12), (s * x, -12, z), (1, 0, 0), (0, 0, 1), 42, STEEL, n=(0, 1, 0)))
    return out

def trigger(color=WOOD2, dz=0.0):
    yb = G.XM_Y['BACK']
    base = G.trigger_base().solid()
    out = [Solid(base, (0, yb, 0 + dz), (1, 0, 0), (0, 1, 0), G.T, color, n=(0, 0, 1))]
    for x, kind in ((-9, 'outer'), (-3, 'middle'), (3, 'outer')):
        out.append(Solid(G.trigger_layer(kind).solid(), (x, yb, G.T + dz), (0, 1, 0), (0, 0, 1), G.T, WOOD, n=(1, 0, 0)))
    return out

def arm_unit(angle=228.6, dz=0.0, with_bearings=True, explode=0.0, long=None):
    """Arm in the Y-Z plane at the given angle (degrees, 90 = long arm straight up)."""
    a = math.radians(angle); U = np.array([0, math.cos(a), math.sin(a)]); V = np.array([0, -math.sin(a), math.cos(a)])
    arm = Solid(box(-(G.A_ARM + 40), -20, long or G.L_ARM, 20), (-10, 0, G.AXLE_Z + dz), U, V, 20, ALU, n=(1, 0, 0))
    out = [arm, cyl_x(-178 - explode * 2, 178 + explode * 2, 0, G.AXLE_Z + dz, 10, STEEL)]
    for s in (-1, 1):
        out.append(cyl_x(s * 10 if s > 0 else -122 - explode, (122 + explode) if s > 0 else -10, 0, G.AXLE_Z + dz, 12.5, '#EDEDED'))
        if with_bearings:
            xc = s * (X0 + G.TT / 2) + s * explode
            out.append(box_solid(xc - 19, -G.PB_LEN / 2, G.CAP_Z + dz, xc + 19, G.PB_LEN / 2, G.CAP_Z + 14 + dz, STEEL))
            out.append(cyl_x(xc - 19, xc + 19, 0, G.AXLE_Z + dz, 31, STEEL))
            out.append(cyl_x(s * (160 + explode * 1.6) if s > 0 else -172 - explode * 1.6, (172 + explode * 1.6) if s > 0 else -160 - explode * 1.6, 0, G.AXLE_Z + dz, 17, '#555555'))
    return out, U

def bag(angle, dz=0.0):
    a = math.radians(angle)
    hy = -G.A_ARM * math.cos(a); hz = G.AXLE_Z - G.A_ARM * math.sin(a) + dz
    c = hz - G.HANG
    return [box_solid(-65, hy - 65, c - 65, 65, hy + 65, c + 65, SAND)]

def trough():
    return [box_solid(-45, -560, 0, 45, 450, 22, '#F4F4F4')]

def side_unit(side, color=WOOD):
    return [panel(side, color=color)] + rail(side, color=color) + gussets(side) + cap(side) + studs(side)

# ---------------------------------------------------------------- figure helper
def fig(name, solids, eye=(1.0, 0.85, 0.75), guides=(), labels=(), ghost=(), size=(6.2, 4.6), xlim=None, ylim=None):
    f, ax = plt.subplots(figsize=size)
    cam = Cam(eye)
    render(ax, solids, cam, guides=guides, labels=labels, ghost=ghost)
    if xlim: ax.set_xlim(*xlim)
    if ylim: ax.set_ylim(*ylim)
    f.savefig(os.path.join(OUT, name + '.pdf'), bbox_inches='tight', pad_inches=0.05)
    f.savefig(os.path.join(OUT, name + '.png'), bbox_inches='tight', pad_inches=0.05, dpi=110)
    plt.close(f)

P = lambda *a: np.array([a], float)

# ---------------------------------------------------------------- BUILD (once)
def b_inventory():
    parts = [('A-frame layer', G.side_panel('A', 1), '4 (A1 A2 B1 B2)'), ('Rail pieces', G.rail_pieces('A')[0], '8'),
             ('Cross member layer', G.cross_member('MIDDLE', 1), '2 middle, 2 front, 2 back'),
             ('Brace layer', G.brace(1), '4'), ('Gusset', G.gusset(0), '8'), ('Top cap', G.cap('upper'), '2 upper, 2 lower'),
             ('Wedge', G.wedge(0), '8 (2 spare)'), ('Trigger layer', G.trigger_layer('middle'), '3 + base'),
             ('Sensor plate', G.sensor_plate(), '2'), ('Arm templates', G.arm_end_template(), 'end + tip'),
             ('Doubler templates', G.doubler_template('axle'), '2')]
    f, axs = plt.subplots(3, 4, figsize=(7.2, 5.4))
    for ax, (nm, p, q) in zip(axs.flat, parts):
        g = p.solid()
        for gg in (g.geoms if hasattr(g, 'geoms') else [g]):
            from matplotlib.patches import Polygon as MP
            ax.add_patch(MP(np.array(gg.exterior.coords), fc=WOOD, ec='#1A1A1A', lw=0.5))
            for r in gg.interiors: ax.add_patch(MP(np.array(r.coords), fc='white', ec='#1A1A1A', lw=0.4))
        for x, y, d in p.holes: ax.add_patch(plt.Circle((x, y), d / 2, fc='white', ec='#1A1A1A', lw=0.4))
        ax.set_aspect('equal'); ax.autoscale_view(); ax.axis('off')
        ax.set_title(f'{nm}\n× {q}', fontsize=10)
    axs.flat[-1].axis('off')
    f.tight_layout(); f.savefig(os.path.join(OUT, 'b01_inventory.pdf')); f.savefig(os.path.join(OUT, 'b01_inventory.png'), dpi=110); plt.close(f)

def b_aframe():
    s = [panel('A', x=X0 + 160, layer=1, color=WOOD), panel('A', x=X0, layer=2, color=WOOD2)]
    dow = [Solid(Point(0, 0).buffer(3, 10), (X0 - 10, y, z), (0, 1, 0), (0, 0, 1), 200, '#B5651D', n=(1, 0, 0))
           for (y, z, d) in G.side_panel('A', 1).holes if d == G.DOWEL_D]
    fig('b02_aframe', s + dow, eye=(1.0, 0.55, 0.45),
        guides=[(P(X0 + 160, 0, 300), P(X0 + 20, 0, 300))],
        labels=[('layer 1 (engraving out)', P(X0 + 166, 150, 470), (60, 40)), ('layer 2', P(X0 + 6, -150, 470), (-50, 40)),
                ('6 mm dowels', P(X0 + 190, -100, 190), (50, -45))])

def b_rail():
    pcs = G.rail_pieces('A'); out = []
    for p in pcs:
        lay = 2 if p.name.startswith('rail_A2') else 1
        out.append(Solid(p.solid(), (X0 + (110 if lay == 2 else 0), 0, 0), (0, 1, 0), (0, 0, 1), G.T, WOOD2 if lay == 2 else WOOD, n=(1, 0, 0)))
    fig('b03_rail', out, eye=(1.0, 0.45, 0.5), guides=[(P(X0 + 110, 0, -45), P(X0 + 10, 0, -45))],
        labels=[('layer 1: back + front pieces', P(X0, -350, 0), (-40, 40)), ('layer 2: joints fall\nin different places', P(X0 + 116, 300, 0), (50, 45)),
                ('notches line up', P(X0, G.XM_Y['FRONT'], -90), (40, -40))])

def b_pairs():
    out = [Solid(G.cross_member('MIDDLE', 1).solid(), (0, 0, 0), (1, 0, 0), (0, 0, 1), G.T, WOOD, n=(0, 1, 0)),
           Solid(G.cross_member('MIDDLE', 2).solid(), (0, 90, 0), (1, 0, 0), (0, 0, 1), G.T, WOOD2, n=(0, 1, 0)),
           Solid(G.brace(1).solid(), (0, 300, 120), (1, 0, 0), (0, 0, 1), G.T, WOOD, n=(0, 1, 0)),
           Solid(G.brace(2).solid(), (0, 390, 120), (1, 0, 0), (0, 0, 1), G.T, WOOD2, n=(0, 1, 0))]
    fig('b04_pairs', out, eye=(0.35, 1.0, 0.5), guides=[(P(0, 90, -45), P(0, 10, -45)), (P(220, 390, 250), P(220, 310, 250))],
        labels=[('cross member: 2 layers', P(-250, 0, -40), (-40, 35)), ('brace: 2 layers', P(220, 390, 290), (60, 30))])

def b_caps():
    out = cap('A', dz=0, split=110) + [s.moved((0, 0, -60)) for s in studs('A')]
    fig('b05_caps', out, eye=(1.0, 0.8, 0.9),
        guides=[(P(X0 + 6, -47.5, G.PANEL_TOP - 60), P(X0 + 6, -47.5, G.PANEL_TOP - 5)),
                (P(X0 + 6, 0, G.PANEL_TOP + 120), P(X0 + 6, 0, G.PANEL_TOP + 12))],
        labels=[('M10 × 40 bolts up\nthrough the hex pockets', P(X0 + 6, 47.5, G.PANEL_TOP - 40), (70, -25)),
                ('lower cap', P(X0 + 6, -70, G.PANEL_TOP + 3), (-70, -20)), ('upper cap: glue on', P(X0 + 6, -70, G.PANEL_TOP + 116), (-60, 25))])

def b_frame_rail():
    out = [panel('A').moved((0, 0, 150))] + rail('A')
    fig('b06_frame_on_rail', out, eye=(1.0, 0.6, 0.55),
        guides=[(P(X1, -177.5, 140), P(X1, -177.5, 5)), (P(X1, 177.5, 140), P(X1, 177.5, 5))],
        labels=[('foot tabs drop into\nthe notches in the rail', P(X1, 177.5, 40), (70, 30)),
                ('glue in the notches', P(X1, -177.5, -10), (-60, -30))])

def b_gussets():
    out = [panel('A')] + rail('A') + [g.moved((60 if g.n[0] > 0 else -60, 0, 0)) for g in gussets('A')]
    fig('b07_gussets', out, eye=(1.0, 0.6, 0.5),
        guides=[(P(X1 + 60, 177.5, 0), P(X1 + 8, 177.5, 0)), (P(X1 + 60, -177.5, 0), P(X1 + 8, -177.5, 0))],
        labels=[('gusset each face of each foot\nglue + 4 screws', P(X1 + 66, 177.5, 28), (60, 35)),
                ('line on the gusset = rail top', P(X1 + 66, -177.5, -2), (-60, -35))])

def b_cap_on():
    out = [panel('A')] + rail('A') + gussets('A') + [s.moved((0, 0, 90)) for s in cap('A') + studs('A')]
    fig('b08_cap_on', out, eye=(1.0, 0.7, 0.6),
        guides=[(P(X0 + 6, 0, G.PANEL_TOP + 85), P(X0 + 6, 0, G.PANEL_TOP + 18))],
        labels=[('cap over the two top tabs,\nstud heads down; glue', P(X0 + 6, 60, G.PANEL_TOP + 100), (80, 25)),
                ('SIDE UNIT A finished.\nMake side B the same\n(it is the mirror image)', P(X0, 300, 0), (95, 60))])

def b_trigger():
    out = [xmember('BACK')] + trigger(dz=80)
    fig('b09_trigger', out, eye=(0.9, 1.0, 0.7),
        guides=[(P(0, G.XM_Y['BACK'], 75), P(0, G.XM_Y['BACK'], 10))],
        labels=[('3 trigger layers glued,\nslotted one in the middle', P(9, G.XM_Y['BACK'], 150), (70, 30)),
                ('base: glue + 2 screws\ninto the top edge', P(40, G.XM_Y['BACK'], 84), (75, -25)),
                ('BACK cross member', P(-150, G.XM_Y['BACK'], -50), (-50, -30))])

def b_arm_unit():
    out, U = arm_unit(angle=90, explode=90)
    arm = Solid(box(-(G.A_ARM + 40), -20, 260, 20), (-10, 0, G.AXLE_Z), (0, 0, 1), (0, -1, 0), 20, ALU, n=(1, 0, 0))
    out = [arm] + out[1:]
    fig('b11_arm_unit', out, eye=(0.35, 1.0, 0.3), size=(6.6, 4.4),
        guides=[(P(320, 0, G.AXLE_Z + 60), P(240, 0, G.AXLE_Z + 60)), (P(-320, 0, G.AXLE_Z + 60), P(-240, 0, G.AXLE_Z + 60))],
        labels=[('arm (drilled, doublers on;\nsling + release pin fitted)', P(0, 0, G.AXLE_Z + 240), (90, 10)),
                ('spacer', P(70, 0, G.AXLE_Z), (10, -45)), ('pillow block', P(245, 0, G.AXLE_Z - 31), (20, -45)),
                ('collar', P(330, 0, G.AXLE_Z + 17), (35, 30)), ('20 mm axle', P(-300, 0, G.AXLE_Z), (-30, -40)),
                ('hang bolt', P(0, 0, G.AXLE_Z - G.A_ARM), (-70, 0))])

def b_arm_drill():
    f, ax = plt.subplots(figsize=(9.0, 2.6))
    from matplotlib.patches import Rectangle, Circle, Polygon as MP
    Ltot = 40 + G.A_ARM + G.L_ARM
    ax.add_patch(Rectangle((0, -20), Ltot, 40, fc=ALU, ec='k', lw=0.6))
    for x, d, t in ((40, 12.5, 'hang bolt M12'), (40 + G.A_ARM, 20.5, 'axle 20 mm')):
        ax.add_patch(Rectangle((x - 50, -20), 100, 40, fc='#9AA0A6', ec='k', lw=0.5, alpha=0.7))
        ax.add_patch(Circle((x, 0), d / 2, fc='white', ec='k', lw=0.6))
        ax.text(x, 30, t, ha='center', fontsize=9)
        for dxh in (-35, 35): ax.add_patch(Circle((x + dxh, 0), 2.5, fc='white', ec='k', lw=0.4))
    ax.add_patch(Rectangle((Ltot, -3), 30, 6, fc='#555', ec='k', lw=0.4))
    ax.text(Ltot + 15, 30, 'release pin', ha='center', fontsize=9)
    for x, t, y in ((Ltot - 22.5, 'sling eye', 26), (Ltot - 75, 'trigger eye', -30)):
        ax.plot([x, x], [-20, 20], color='k', lw=0.4, ls=':'); ax.text(x - 10, y, t, ha='right', fontsize=9)
    ax.add_patch(Rectangle((40 + G.A_ARM + 100, -12), 60, 24, fc='#F0F0F0', ec='k', lw=0.5)); ax.text(40 + G.A_ARM + 130, 0, 'sensor', ha='center', va='center', fontsize=6.5)
    def d(x0, x1, y, t):
        ax.annotate('', xy=(x1, y), xytext=(x0, y), arrowprops=dict(arrowstyle='<->', lw=0.5))
        ax.text((x0 + x1) / 2, y - 9, t, ha='center', va='top', fontsize=9)
    d(0, 40, -45, '40'); d(40, 40 + G.A_ARM, -45, '262.5'); d(40 + G.A_ARM, Ltot, -45, '750 (axle to pin)')
    d(0, Ltot, -80, f'tube {Ltot:.0f} long')
    ax.text(40 + G.A_ARM - 50, 52, 'grey: 6 mm aluminium doubler each side, 3 × M5 bolts', fontsize=8.5, ha='left')
    ax.set_xlim(-20, Ltot + 70); ax.set_ylim(-115, 70); ax.set_aspect('equal'); ax.axis('off')
    f.savefig(os.path.join(OUT, 'b10_arm_drill.pdf'), bbox_inches='tight'); f.savefig(os.path.join(OUT, 'b10_arm_drill.png'), bbox_inches='tight', dpi=110); plt.close(f)

# ---------------------------------------------------------------- SETUP (each session)
def s_layout():
    out = [xmember(n) for n in ('BACK', 'MIDDLE', 'FRONT')] + trigger()
    fig('s01_crossmembers', out, labels=[('BACK (trigger)', P(-120, G.XM_Y['BACK'], 0), (-30, 30)),
                                        ('MIDDLE (longest)', P(-250, 0, -40), (-40, 25)), ('FRONT', P(-120, G.XM_Y['FRONT'], 0), (-25, 25)),
                                        ('throwing direction', P(320, 520, -90), (30, -20))],
        guides=[(P(320, -100, -90), P(320, 520, -90))])

def s_side(which):
    base = [xmember(n) for n in ('BACK', 'MIDDLE', 'FRONT')] + trigger()
    if which == 'A':
        out = base + [s.moved((0, 0, 220)) for s in side_unit('A')]
        lab = [('side unit A, engraving out', P(X1, 250, 520), (70, 25)), ('notches under the rail\ndrop over each cross member', P(X1, G.XM_Y['FRONT'], 150), (75, -20))]
        gd = [(P(X1, -300, 200), P(X1, -300, 30)), (P(X1, 300, 200), P(X1, 300, 30))]
        fig('s02_side_A', out, guides=gd, labels=lab)
    else:
        out = base + side_unit('A') + [s.moved((0, 0, 220)) for s in side_unit('B')]
        lab = [('side unit B', P(-X1, -250, 560), (-60, 25))]
        gd = [(P(-X1, -300, 200), P(-X1, -300, 30)), (P(-X1, 300, 200), P(-X1, 300, 30))]
        fig('s03_side_B', out, guides=gd, labels=lab)

def s_wedges():
    base = [xmember(n) for n in ('BACK', 'MIDDLE', 'FRONT')] + trigger() + side_unit('A') + side_unit('B')
    w = [wedge(n, 'A', dy=-80) for n in ('BACK', 'MIDDLE', 'FRONT')] + [wedge(n, 'B', dy=0) for n in ('BACK', 'MIDDLE', 'FRONT')]
    fig('s04_wedges', base + w, eye=(1.0, 0.75, 0.55),
        guides=[(P(155, G.XM_Y['FRONT'] - 150, G.WEDGE_Z + 10), P(155, G.XM_Y['FRONT'] - 60, G.WEDGE_Z + 10))],
        labels=[('wedge: thin end first,\ntap firm by hand (×6)', P(155, G.XM_Y['FRONT'] - 120, G.WEDGE_Z), (70, -30))])
    return
    cu = [Solid(G.cross_member('FRONT', 1).solid().intersection(box(60, -100, 210, 10)), (0, G.XM_Y['FRONT'] - G.T, 0), (1, 0, 0), (0, 0, 1), G.TT, WOOD2, n=(0, 1, 0)),
          Solid(unary_union([p.solid() for p in G.rail_pieces('A') if p.name.startswith('rail_A1_')]).intersection(box(G.XM_Y['FRONT'] - 90, -95, G.XM_Y['FRONT'] + 60, 5)),
                (X0, 0, 0), (0, 1, 0), (0, 0, 1), G.TT, WOOD, n=(1, 0, 0)),
          wedge('FRONT', 'A', dy=-30)]
    fig('s04b_wedge_closeup', cu, eye=(1.0, 0.9, 1.1), size=(3.4, 3.0),
        guides=[(P(155, G.XM_Y['FRONT'] - 120, G.WEDGE_Z + 5), P(155, G.XM_Y['FRONT'] - 70, G.WEDGE_Z + 5))],
        labels=[('rail', P(X1, G.XM_Y['FRONT'] + 40, -10), (40, 25)), ('cross member', P(200, G.XM_Y['FRONT'], -60), (20, -35))])

def s_braces():
    base = [xmember(n) for n in ('BACK', 'MIDDLE', 'FRONT')] + trigger() + side_unit('A') + side_unit('B') + \
           [wedge(n, s) for n in ('BACK', 'MIDDLE', 'FRONT') for s in 'AB']
    out = base + [brace('A', dx=120), brace('B')] + pins('B')
    fig('s05_braces', out, eye=(1.0, 0.9, 0.55),
        guides=[(P(X1 + 120, 12, G.BRACE_TOP[1]), P(X1 + 20, 12, G.BRACE_TOP[1]))],
        labels=[('tab through the slot\nin the crossbar', P(X1 + 120, 12, G.BRACE_TOP[1] + 20), (60, 35)),
                ('pin + R-clip at\nboth ends', P(-G.BRACE_BOT[0], 20, G.BRACE_BOT[1]), (-60, -30))])

def s_arm():
    base = [xmember(n) for n in ('BACK', 'MIDDLE', 'FRONT')] + trigger() + side_unit('A') + side_unit('B') + \
           [wedge(n, s) for n in ('BACK', 'MIDDLE', 'FRONT') for s in 'AB'] + [brace('A'), brace('B')]
    arm, U = arm_unit(angle=90, dz=260, long=280)
    out = base + arm + [k.moved((0, 0, 330)) for k in knobs('A') + knobs('B')]
    fig('s06_arm', out, eye=(1.0, 0.8, 0.6),
        guides=[(P(X0 + 6, -47.5, G.CAP_Z + 250), P(X0 + 6, -47.5, G.CAP_Z + 40)), (P(-X0 - 6, 47.5, G.CAP_Z + 250), P(-X0 - 6, 47.5, G.CAP_Z + 40))],
        labels=[('arm unit: lift on,\npillow blocks over the studs', P(0, 0, G.AXLE_Z + 520), (330, 60)),
                ('4 star knobs: finger tight\n+ a quarter turn', P(-X0 - 6, -47.5, G.CAP_Z + 346), (-330, -120))], size=(6.2, 5.6))

def s_ready():
    base = [xmember(n) for n in ('BACK', 'MIDDLE', 'FRONT')] + trigger() + side_unit('A') + side_unit('B') + \
           [wedge(n, s) for n in ('BACK', 'MIDDLE', 'FRONT') for s in 'AB'] + [brace('A'), brace('B')] + trough()
    arm, U = arm_unit(angle=90, long=280)
    out = base + arm + knobs('A') + knobs('B') + bag(90)
    fig('s07_ready', out, eye=(0.45, 1.0, 0.32), size=(6.2, 5.0),
        labels=[('trough', P(30, 440, 22), (260, -60)),
                ('4 kg bag hangs at rest;\nsafety strap on', P(65, 65, G.AXLE_Z - G.A_ARM - G.HANG + 40), (380, 260)),
                ('peg or sandbag\nthe base', P(-300, -300, -60), (-330, -40))])


def seg(p0, p1, w, color):
    """Thin rod/cord between two points in the Y-Z plane at X = 0."""
    p0 = np.asarray(p0, float); p1 = np.asarray(p1, float)
    d = p1 - p0; L = np.linalg.norm(d); U = d / L
    V = np.cross([1.0, 0, 0], U); V = V / np.linalg.norm(V)
    return Solid(box(0, -w / 2, L, w / 2), p0 - np.array([w / 2, 0, 0]), U, V, w, color, n=(1, 0, 0))

def s_cocked():
    ang = 180 + math.degrees(math.asin((G.AXLE_Z - 0.10 * G.L_ARM) / G.L_ARM))
    base = [xmember(n) for n in ('BACK', 'MIDDLE', 'FRONT')] + trigger() + side_unit('A') + side_unit('B') + \
           [wedge(n, s) for n in ('BACK', 'MIDDLE', 'FRONT') for s in 'AB'] + [brace('A'), brace('B')] + trough()
    arm, U = arm_unit(angle=ang)
    a = math.radians(ang)
    tip = np.array([0, G.L_ARM * math.cos(a), G.AXLE_Z + G.L_ARM * math.sin(a)])
    teye = np.array([0, (G.L_ARM - 75) * math.cos(a), G.AXLE_Z + (G.L_ARM - 75) * math.sin(a)])
    pouch = np.array([0, tip[1] + 0.98 * G.L_ARM, 30])
    sling = [seg(tip, pouch, 4, '#8E5B2E'), box_solid(-22, pouch[1] - 5, 22, 22, pouch[1] + 40, 52, '#C0392B')]
    loop = [seg(teye, (0, G.XM_Y['BACK'], 60), 5, '#2B2B2B')]
    out = base + arm + knobs('A') + knobs('B') + bag(ang) + sling + loop
    fig('s08_cocked', out, eye=(1.0, 0.55, 0.5), size=(6.6, 4.8),
        labels=[('trigger loop round the\npin in the trigger block', P(0, G.XM_Y['BACK'], 60), (-300, -120)),
                ('sling + beanbag\nin the trough', P(0, pouch[1], 40), (320, -60)),
                ('ring over the\nrelease pin', P(0, tip[1], tip[2]), (-330, 120)),
                ('4 kg bag raised:\nstand clear of it', P(65, 187, 574), (300, 200))])

if __name__ == '__main__':
    b_inventory(); b_aframe(); b_rail(); b_pairs(); b_caps(); b_frame_rail(); b_gussets(); b_cap_on(); b_trigger()
    b_arm_drill(); b_arm_unit()
    s_layout(); s_side('A'); s_side('B'); s_wedges(); s_braces(); s_arm(); s_ready(); s_cocked()
    print('done', sorted(os.listdir(OUT)))
