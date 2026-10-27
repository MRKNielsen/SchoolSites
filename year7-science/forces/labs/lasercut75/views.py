"""Assembled views drawn from the real part geometry in gen75.py (for the notes)."""
import math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MPoly, Rectangle, Circle
from shapely.geometry import MultiPolygon
import gen75 as G

WOOD, WOOD2, STEEL, ALU, SAND, STRAP = '#E2CFA8', '#C9AE80', '#6B7178', '#C9CED4', '#D8C08A', '#3E6C8C'
plt.rcParams.update({'font.size': 7, 'font.family': 'DejaVu Sans'})

def draw(ax, g, fc, ec='#1A1A1A', lw=0.6, alpha=1.0, z=1):
    for gg in (g.geoms if isinstance(g, MultiPolygon) else [g]):
        ax.add_patch(MPoly(list(gg.exterior.coords), closed=True, fc=fc, ec=ec, lw=lw, alpha=alpha, zorder=z))
        for r in gg.interiors:
            ax.add_patch(MPoly(list(r.coords), closed=True, fc='white', ec=ec, lw=lw, zorder=z + 0.1))

def lab(ax, text, xy, xytext, ha='left'):
    ax.annotate(text, xy=xy, xytext=xytext, ha=ha, va='center', fontsize=6.5,
                arrowprops=dict(arrowstyle='-', lw=0.5, color='#555555'))

def dim(ax, p0, p1, text, off=(0, 0), rot=0):
    ax.annotate('', xy=p1, xytext=p0, arrowprops=dict(arrowstyle='<->', lw=0.5, shrinkA=0, shrinkB=0))
    ax.text((p0[0] + p1[0]) / 2 + off[0], (p0[1] + p1[1]) / 2 + off[1], text, ha='center', va='center',
            fontsize=6.5, rotation=rot, bbox=dict(fc='white', ec='none', pad=0.6))

# ---------------------------------------------------------------- side unit
def side_unit(path):
    fig, ax = plt.subplots(figsize=(7.2, 4.6))
    for p in G.rail_pieces('A'):
        if '_A2_' in p.name: draw(ax, p.solid(), WOOD2, z=1)
    p = G.side_panel('A', 2); draw(ax, p.solid(), WOOD, z=2)
    for s in (-1, 1):
        gs = G.gusset(0).solid()
        from shapely import affinity
        draw(ax, affinity.translate(gs, s * 177.5, 0), '#B8996A', alpha=0.85, z=3)
    cap = G.rect(-G.PB_LEN / 2 - 12, G.PANEL_TOP, G.PB_LEN / 2 + 12, G.CAP_Z)
    draw(ax, cap, '#B8996A', z=3)
    ax.add_patch(Rectangle((-G.PB_LEN / 2, G.CAP_Z), G.PB_LEN, 14, fc=STEEL, ec='k', lw=0.5, zorder=4))
    ax.add_patch(Circle((0, G.AXLE_Z), 24, fc=STEEL, ec='k', lw=0.5, zorder=4))
    ax.add_patch(Circle((0, G.AXLE_Z), 10, fc='white', ec='k', lw=0.5, zorder=5))
    for s in (-1, 1):
        ax.add_patch(Rectangle((s * G.PB_BOLT_PITCH / 2 - 8, G.CAP_Z + 14), 16, 14, fc='#333', ec='k', lw=0.4, zorder=5))
    ax.plot([-650, 580], [-90, -90], color='#555', lw=0.8)
    for nm, y in G.XM_Y.items():
        ax.text(y, -100, {'BACK': 'back', 'MIDDLE': 'middle', 'FRONT': 'front'}[nm] + '\ncross member', ha='center', va='top', fontsize=6)
    lab(ax, 'pillow block on studs,\nheld by 2 star knobs', (40, G.CAP_Z + 20), (190, 640))
    lab(ax, 'top cap (2 layers):\nstud heads in hex pockets', (60, G.CAP_Z - 6), (190, 545))
    lab(ax, 'A-frame (2 layers)', (150, 200), (300, 260))
    lab(ax, 'gussets both faces,\nglued and screwed', (230, 10), (330, 120))
    lab(ax, 'rail (2 layers, joints\nstaggered); notches\nunderneath take the\ncross members', (420, -50), (600, 60))
    lab(ax, 'brace slot', (12, 307), (-260, 380), ha='right')
    dim(ax, (-560, 0), (-560, G.AXLE_Z), 'axle 600 above\nrail top', off=(-60, 0))
    dim(ax, (-600, -185), (525, -185), 'rail 1125 long', off=(0, -16))
    ax.text(-600, 700, 'Side unit A, outside face (glued up once, never taken apart). Side B is its mirror image.',
            fontsize=7.5, fontweight='bold', va='bottom')
    ax.set_xlim(-700, 760); ax.set_ylim(-230, 720); ax.set_aspect('equal'); ax.axis('off')
    fig.savefig(path, bbox_inches='tight'); plt.close(fig)

# ---------------------------------------------------------------- front view at the pivot line
def front(path):
    fig, ax = plt.subplots(figsize=(7.2, 5.6))
    xm = G.cross_member('MIDDLE', 1).solid(); draw(ax, xm, WOOD2, z=1)
    for s in (-1, 1):
        x0 = s * G.SIDE_X0; x1 = s * G.SIDE_X1
        draw(ax, G.rect(x0, -G.RAIL_H, x1, 0), WOOD, z=2)                        # rail end-on
        draw(ax, G.rect(x0, 0, x1, G.PANEL_TOP), WOOD, z=2)                       # panel edge-on
        draw(ax, G.rect(s * (G.SIDE_X0 + G.TT / 2) - 26, G.PANEL_TOP, s * (G.SIDE_X0 + G.TT / 2) + 26, G.CAP_Z), '#B8996A', z=3)
        cx = s * (G.SIDE_X0 + G.TT / 2)
        ax.add_patch(Rectangle((cx - 19, G.CAP_Z), 38, 64, fc=STEEL, ec='k', lw=0.5, zorder=4))
        # wedge in its hole (seen end-on)
        draw(ax, G.rect(s * (G.SIDE_X1), G.WEDGE_Z - 3, s * (G.SIDE_X1 + 17), G.WEDGE_Z + 3), '#8B6B3E', z=4)
        # brace (in front of the cross member)
        b = G.brace(1).solid()
        from shapely import affinity
        b = b if s > 0 else affinity.scale(b, -1, 1, origin=(0, 0))
        draw(ax, b, WOOD, alpha=0.9, z=5)
    ax.add_patch(Rectangle((-205, G.AXLE_Z - 10), 410, 20, fc=STEEL, ec='k', lw=0.5, zorder=6))
    for s in (-1, 1):
        ax.add_patch(Rectangle((s * 10 if s > 0 else -G.SIDE_X0, G.AXLE_Z - 14), G.SIDE_X0 - 10, 28, fc='#EEEEEE', ec='k', lw=0.4, zorder=6))
    hang_z = G.AXLE_Z - G.A_ARM
    ax.add_patch(Rectangle((-10, hang_z - 40), 20, 450, fc=ALU, ec='k', lw=0.5, zorder=7))
    ax.add_patch(Rectangle((-32, hang_z - 6), 64, 12, fc=STEEL, ec='k', lw=0.4, zorder=8))
    bag_c = hang_z - G.HANG
    ax.plot([-26, 0, 26], [hang_z, bag_c + 95, hang_z], color=STRAP, lw=1.4, zorder=8)
    ax.add_patch(Rectangle((-65, bag_c - 65), 130, 130, fc=SAND, ec='k', lw=0.5, zorder=8, joinstyle='round'))
    ax.plot([0, -55, -55, 55, 55, 0], [bag_c + 95, bag_c + 65, bag_c - 65, bag_c - 65, bag_c + 65, bag_c + 95], color=STRAP, lw=1.2, zorder=9)
    ax.add_patch(Rectangle((-45, 0), 90, 30, fc='#F0F0F0', ec='k', lw=0.4, zorder=3))
    ax.plot([-360, 360], [-90, -90], color='#555', lw=0.8)
    dim(ax, (-G.SIDE_X0, 720), (-15, 720), 'gap 270', off=(0, 22))
    ax.annotate('', xy=(G.SIDE_X0, 720), xytext=(15, 720), arrowprops=dict(arrowstyle='->', lw=0.5, shrinkA=0, shrinkB=0))
    dim(ax, (-300, -125), (300, -125), 'middle cross member 600', off=(0, -14))
    dim(ax, (610, 0), (610, G.AXLE_Z), 'axle 600 above the rail tops', off=(0, 0), rot=90)
    ax.plot([215, 620], [G.AXLE_Z, G.AXLE_Z], color='#888', lw=0.4); ax.plot([500, 620], [0, 0], color='#888', lw=0.4)
    lab(ax, 'pillow block\n(arm unit lifts off)', (-150, G.CAP_Z + 50), (-330, 690), ha='right')
    lab(ax, 'side unit\n(panel on rail)', (-141, 450), (-330, 470), ha='right')
    lab(ax, 'brace: tab through\nthe crossbar, R-clip\npin inside', (-130, 308), (-330, 330), ha='right')
    lab(ax, 'wedge locks the cross\nmember outside the rail', (-160, G.WEDGE_Z), (-330, 120), ha='right')
    lab(ax, 'brace pinned to the\ncross member end', (-280, G.WEDGE_Z), (-330, -40), ha='right')
    lab(ax, '4 kg bag, 210 below\nthe hang bolt', (65, bag_c + 30), (345, 250))
    lab(ax, 'trough on the\ncross members', (45, 20), (345, 60))
    ax.text(-540, 800, 'From the front, at the pivot line (arm hanging at rest, sizes in mm)', fontsize=7.5, fontweight='bold')
    ax.set_xlim(-560, 640); ax.set_ylim(-180, 830); ax.set_aspect('equal'); ax.axis('off')
    fig.savefig(path, bbox_inches='tight'); plt.close(fig)

# ---------------------------------------------------------------- wedge joint, plan view
def wedge_plan(path):
    fig, ax = plt.subplots(figsize=(3.4, 2.6))
    ax.add_patch(Rectangle((G.SIDE_X0, -90), G.TT, 180, fc=WOOD, ec='k', lw=0.5, zorder=2))
    ax.add_patch(Rectangle((60, -6), G.XM_HALF['FRONT'] - 60, 12, fc=WOOD2, ec='k', lw=0.5, zorder=1))
    ax.add_patch(Rectangle((G.WEDGE_HOLE[0], -6), G.WEDGE_HOLE[1] - G.WEDGE_HOLE[0], 12, fc='white', ec='k', lw=0.4, zorder=3))
    xs = G.SIDE_X1
    ax.add_patch(MPoly([(xs, -70), (xs + 14, -70), (xs + 20, 25), (xs, 25)], closed=True, fc='#8B6B3E', ec='k', lw=0.5, zorder=4))
    ax.annotate('', xy=(xs + 30, 25), xytext=(xs + 30, -60), arrowprops=dict(arrowstyle='->', lw=0.6))
    ax.text(xs + 38, -40, 'tap the wedge\nthrough: it pulls\nthe shoulder tight\nagainst the rail', fontsize=6, va='center')
    ax.text(G.SIDE_X0 - 4, 70, 'rail', ha='right', fontsize=6.5)
    ax.text(62, 16, 'cross member', fontsize=6.5)
    ax.text(G.SIDE_X0 - 6, -40, 'shoulder bears on\nthe inside face', ha='right', fontsize=6)
    ax.text(40, 100, 'Wedge joint, from above', fontsize=7.5, fontweight='bold')
    ax.set_xlim(20, 280); ax.set_ylim(-95, 110); ax.set_aspect('equal'); ax.axis('off')
    fig.savefig(path, bbox_inches='tight'); plt.close(fig)

if __name__ == '__main__':
    side_unit('view_side_unit.pdf'); front('view_front.pdf'); wedge_plan('view_wedge.pdf')
    for n in ('view_side_unit', 'view_front', 'view_wedge'):
        import subprocess
        subprocess.run(['pdftoppm', '-r', '90', '-png', '-singlefile', n + '.pdf', n])
    print('ok')
