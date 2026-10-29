"""Tiny 3D renderer for assembly drawings: extrudes flat parts, projects them, draws with the painter's algorithm."""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.path import Path
from matplotlib.patches import PathPatch
from shapely.geometry import Polygon, MultiPolygon, Point, box
from shapely.ops import unary_union

EYE = np.array([1.0, 0.85, 0.75])

class Cam:
    def __init__(self, eye=EYE):
        e = np.asarray(eye, float); self.e = e / np.linalg.norm(e)
        f = -self.e
        r = np.cross(f, [0, 0, 1.0]); self.r = r / np.linalg.norm(r)
        self.u = np.cross(self.r, f)
    def p(self, P):
        P = np.atleast_2d(P)
        return np.c_[P @ self.r, P @ self.u]
    def depth(self, P):
        return np.atleast_2d(P) @ self.e

def shade(hexcol, k):
    c = np.array(matplotlib.colors.to_rgb(hexcol))
    return tuple(np.clip(c * k + (1 - k) * 0.0 if k < 1 else c + (1 - c) * (k - 1), 0, 1))

LIGHT = np.array([0.4, 0.7, 1.0]); LIGHT /= np.linalg.norm(LIGHT)

class Solid:
    """A flat shape (shapely, local u/v) extruded along n by thickness t, placed at origin o with axes U, V."""
    def __init__(self, shape, o, U, V, t, color='#E2CFA8', n=None, ec='#1A1A1A', lw=0.5, alpha=1.0, label=None):
        self.shape = shape
        self.o = np.asarray(o, float); self.U = np.asarray(U, float); self.V = np.asarray(V, float)
        self.n = np.asarray(n, float) if n is not None else np.cross(self.U, self.V)
        self.t, self.color, self.ec, self.lw, self.alpha, self.label = t, color, ec, lw, alpha, label
    def moved(self, d):
        s = Solid(self.shape, self.o + np.asarray(d, float), self.U, self.V, self.t, self.color, self.n, self.ec, self.lw, self.alpha, self.label)
        return s
    def to3(self, uv, off=0.0):
        uv = np.asarray(uv, float)
        return self.o + np.outer(uv[:, 0], self.U) + np.outer(uv[:, 1], self.V) + off * self.n
    def faces(self):
        out = []
        geoms = self.shape.geoms if isinstance(self.shape, MultiPolygon) else [self.shape]
        for g in geoms:
            g = g.simplify(0.4)
            for off, sgn in ((0.0, -1), (self.t, 1)):
                rings = [self.to3(np.array(g.exterior.coords), off)] + [self.to3(np.array(r.coords), off) for r in g.interiors]
                out.append(('cap', rings, sgn * self.n))
            ext = np.array(g.exterior.coords)
            for a, b in zip(ext[:-1], ext[1:]):
                q = np.array([a, b])
                p0 = self.to3(q, 0.0); p1 = self.to3(q, self.t)
                quad = np.array([p0[0], p0[1], p1[1], p1[0]])
                edge = p0[1] - p0[0]
                nn = np.cross(edge, self.n); nrm = np.linalg.norm(nn)
                if nrm < 1e-9: continue
                out.append(('side', [quad], nn / nrm))
        return out

def box_solid(x0, y0, z0, x1, y1, z1, color, **kw):
    return Solid(box(x0, y0, x1, y1), (0, 0, z0), (1, 0, 0), (0, 1, 0), z1 - z0, color, n=(0, 0, 1), **kw)

def cyl_x(xc0, xc1, y, z, r, color, **kw):
    """Cylinder along X (axle, collars)."""
    return Solid(Point(0, 0).buffer(r, 24), (xc0, y, z), (0, 1, 0), (0, 0, 1), xc1 - xc0, color, n=(1, 0, 0), **kw)

def render(ax, solids, cam, guides=(), labels=(), ghost=()):
    items = []
    for s in list(ghost) + list(solids):
        is_ghost = s in ghost
        for kind, rings, nrm in s.faces():
            facing = np.dot(nrm, cam.e)
            if kind == 'side' and facing <= 0: continue
            if kind == 'cap' and facing <= 0: continue
            pts = np.vstack(rings)
            d = cam.depth(pts).mean()
            if kind == 'side':
                d = cam.depth(pts).max() - 0.01
            k = 0.78 + 0.35 * max(0.0, float(np.dot(nrm, LIGHT)))
            items.append((d, rings, s, k, is_ghost, kind))
    items.sort(key=lambda it: it[0])
    for d, rings, s, k, g, kind in items:
        verts, codes = [], []
        for r in rings:
            p = cam.p(r)
            verts += list(p) + [p[0]]
            codes += [Path.MOVETO] + [Path.LINETO] * (len(p) - 1) + [Path.CLOSEPOLY]
        col = shade(s.color, k)
        if g:
            ax.add_patch(PathPatch(Path(verts, codes), fc=(0.93, 0.93, 0.93), ec='#AAAAAA', lw=0.3, alpha=0.9))
        else:
            ax.add_patch(PathPatch(Path(verts, codes), fc=col, ec=s.ec, lw=(s.lw if kind == 'cap' else s.lw * 0.6),
                                   alpha=s.alpha, joinstyle='round'))
    for a, b in guides:
        pa, pb = cam.p(a)[0], cam.p(b)[0]
        ax.annotate('', xy=pb, xytext=pa, arrowprops=dict(arrowstyle='-|>', lw=0.8, ls=(0, (4, 2)), color='#C0392B',
                                                          shrinkA=0, shrinkB=0, mutation_scale=9))
    for text, at, off in labels:
        p = cam.p(at)[0]
        ax.annotate(text, xy=p, xytext=(p[0] + off[0], p[1] + off[1]), fontsize=11, ha='center', va='center',
                    bbox=dict(boxstyle='round,pad=0.25', fc='white', ec='#555555', lw=0.5),
                    arrowprops=dict(arrowstyle='-', lw=0.5, color='#555555', shrinkA=0, shrinkB=2))
    ax.set_aspect('equal'); ax.axis('off'); ax.autoscale_view()

def badge(ax, text, xy, col='#C0392B'):
    ax.text(*xy, text, fontsize=8, fontweight='bold', color='white', ha='center', va='center',
            bbox=dict(boxstyle='circle,pad=0.3', fc=col, ec='none'), transform=ax.transAxes)
