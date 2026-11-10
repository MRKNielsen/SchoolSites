#!/usr/bin/env python3
"""Year 7 Particle Model lesson symbols (Lessons 1-15).

Same system as tools/space_symbols.py, and it borrows that file's drawing
kit: each symbol is drawn once, every shape carries a ROLE, and the role
maps to a flat cover colour (site) or a black-and-white ink treatment
(booklet). One diagrammatic idea per lesson, lots of empty paper.

    python3 tools/particle_symbols.py            # write everything
    python3 tools/particle_symbols.py --sheet    # also a preview sheet (needs rsvg-convert + Pillow)

Writes
    year7-science/particle-model/img/symbols/lN.svg       colour, transparent ground
    year7-science/particle-model/booklet/art/lN-ink.svg   black and white, for the booklet
    year7-science/particle-model/booklet/art/lN-ink.pdf   the same as PDF (only if rsvg-convert exists)

Lessons 16-30 (mixtures, solutions, separation) move to the Separation unit
in 2027; their symbols belong with that unit.

Rules the drawings keep:
  * Particles in one substance are all the same size.
  * Solids are packed in a regular pattern and touching; liquids touching
    but jumbled; gases far apart. Nothing is drawn that the particle model
    in Lesson 4 would call wrong (no particles that grow when heated).
"""
import math
import os
import random
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from space_symbols import Pic, W, H  # noqa: E402  (shared drawing kit)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "year7-science", "particle-model", "img", "symbols")
BOOK = os.path.join(ROOT, "year7-science", "particle-model", "booklet", "art")


def ink(p):
    return p.P["ink"]


def rect(p, x, y, w, h, role, extra=""):
    p.raw(f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" '
          f'fill="{p.P[role]}"{p.edge(role)}{extra}/>')


def outline(p, d, w=2.4):
    p.raw(f'<path d="{d}" fill="none" stroke="{ink(p)}" stroke-width="{w}" '
          f'stroke-linejoin="round" stroke-linecap="round"/>')


def jar(p, x, y, w, h, w_line=2.6):
    """An open-topped container: two sides and a base, drawn over its contents."""
    outline(p, f"M{x},{y} V{y + h} H{x + w} V{y}", w_line)


def particle(p, x, y, r, role):
    p.circle(x, y, r, role, f' stroke="{ink(p)}" stroke-width="1.4"' if p.mode == "colour" else "")


def lattice(p, x0, y0, cols, rows, r, role, jitter=0.0, rnd=None):
    d = 2 * r
    for j in range(rows):
        for i in range(cols):
            dx = dy = 0
            if jitter and rnd:
                dx, dy = rnd.uniform(-jitter, jitter), rnd.uniform(-jitter, jitter)
            particle(p, x0 + r + i * d + dx, y0 - r - j * d + dy, r, role)


def jumble(p, x0, y0, w, rows, r, role, seed):
    """Liquid: touching but not in rows. Each particle drops into the lowest
    free spot at a random x, so they touch without overlapping."""
    rnd = random.Random(seed)
    placed = []
    for _ in range(rows * int(w // (2 * r))):
        best = None
        for _try in range(40):
            x = rnd.uniform(x0 + r, x0 + w - r)
            y = y0 - r
            for a, b in placed:                    # rest on whatever is below
                dx = abs(x - a)
                if dx < 2 * r:
                    y = min(y, b - math.sqrt(4 * r * r - dx * dx))
            if best is None or y > best[1]:
                best = (x, y)
        placed.append(best)
    for x, y in placed:
        particle(p, x, y, r, role)


def spread(p, x0, y0, w, h, r, role, n, seed, gap=5.2):
    """Gas: far apart. Rejection-sample points a few diameters apart."""
    rnd = random.Random(seed)
    pts = []
    tries = 0
    while len(pts) < n and tries < 5000:
        tries += 1
        x, y = rnd.uniform(x0 + r + 3, x0 + w - r - 3), rnd.uniform(y0 + r + 3, y0 + h - r - 3)
        if all(math.hypot(x - a, y - b) > gap * r for a, b in pts):
            pts.append((x, y))
    for x, y in pts:
        particle(p, x, y, r, role)
    return pts


def arrow(p, x1, y1, x2, y2, w=2.4, head=9):
    a = math.atan2(y2 - y1, x2 - x1)
    bx, by = x2 - head * math.cos(a), y2 - head * math.sin(a)
    p.line(x1, y1, bx, by, w)
    l = (bx + head * 0.55 * math.sin(a), by - head * 0.55 * math.cos(a))
    r = (bx - head * 0.55 * math.sin(a), by + head * 0.55 * math.cos(a))
    p.raw(f'<path d="M{x2:.2f},{y2:.2f} L{l[0]:.2f},{l[1]:.2f} L{r[0]:.2f},{r[1]:.2f} Z" fill="{ink(p)}"/>')


def flame(p, cx, base, s=1.0):
    p.path(f"M{cx},{base} C{cx - 22 * s},{base - 6 * s} {cx - 14 * s},{base - 30 * s} {cx},{base - 50 * s} "
           f"C{cx + 14 * s},{base - 30 * s} {cx + 22 * s},{base - 6 * s} {cx},{base} Z", "warm")
    p.path(f"M{cx},{base} C{cx - 10 * s},{base - 4 * s} {cx - 7 * s},{base - 16 * s} {cx},{base - 28 * s} "
           f"C{cx + 7 * s},{base - 16 * s} {cx + 10 * s},{base - 4 * s} {cx},{base} Z", "sun")


# ---------------------------------------------------------------- 1
def lesson1(p):
    """States of matter: the same three jars. A solid keeps its own shape,
    a liquid takes the jar's shape at the bottom, a gas fills it all."""
    y, h, w = 236, 120, 72
    xs = (24, 114, 204)
    rect(p, xs[0] + 14, y - 58, 44, 58, "deep")                         # solid: its own shape
    rect(p, xs[1], y - 46, w, 46, "cool")                              # liquid: the jar's shape
    p.line(xs[1] + 2, y - 46, xs[1] + w - 2, y - 46, 2, "ink")
    rect(p, xs[2], y - h, w, h, "cream" if p.mode == "colour" else "sun")  # gas: everywhere
    for x in xs:
        jar(p, x, y - h, w, h)
    p.line(10, y + 1.5, 290, y + 1.5, 3, "ink")


# ---------------------------------------------------------------- 2
def lesson2(p):
    """What is a scientific model: the mystery box. We can't see inside,
    so we probe it and infer a shape — the dashed guess."""
    x, y, s = 70, 80, 160
    rect(p, x, y, s, s, "dark" if p.mode == "colour" else "deep")
    p.raw(f'<rect x="{x}" y="{y}" width="{s}" height="{s}" fill="none" stroke="{ink(p)}" stroke-width="2.6"/>')
    # the inferred shape: drawn as a guess, light dashed line
    guess = "#f2d79a" if p.mode == "colour" else "#ffffff"
    p.raw(f'<path d="M{x + 52},{y + 112} C{x + 40},{y + 60} {x + 96},{y + 40} {x + 112},{y + 74} '
          f'C{x + 128},{y + 108} {x + 92},{y + 130} {x + 52},{y + 112} Z" fill="none" stroke="{guess}" '
          f'stroke-width="3" stroke-dasharray="7 6" stroke-linecap="round"/>')
    # probes: rods pushed in through the walls until they touch something
    for x1, y1, x2, y2 in [(x - 44, y + 86, x + 48, y + 86), (x + 92, y - 44, x + 92, y + 52),
                           (x + s + 44, y + 98, x + 117, y + 98)]:
        p.line(x1, y1, x2, y2, 8, "paper")
        p.line(x1, y1, x2, y2, 4.5, "mustard" if p.mode == "colour" else "ink")
        p.circle(x2, y2, 4, "ink")


# ---------------------------------------------------------------- 3
def lesson3(p):
    """Experiment 1, matter has mass: a beam balance tips toward the
    blown-up balloon — air has mass."""
    cx, py = 150, 110
    tilt = math.radians(8)
    L = 104
    lx, ly = cx - L * math.cos(tilt), py - L * math.sin(tilt)   # light side (left) up
    rx, ry = cx + L * math.cos(tilt), py + L * math.sin(tilt)   # heavy side (right) down
    p.path(f"M{cx - 34},262 L{cx + 34},262 L{cx + 8},{py + 6} L{cx - 8},{py + 6} Z", "deep")  # stand
    p.line(cx - 60, 264, cx + 60, 264, 5, "ink")
    p.line(lx, ly, rx, ry, 5, "ink")
    p.circle(cx, py, 6, "ink")
    for (ex, ey), full in (((lx, ly), False), ((rx, ry), True)):
        p.line(ex, ey, ex, ey + 30, 1.8, "ink")
        if full:
            bx, by = ex, ey + 30 + 38
            p.raw(f'<ellipse cx="{bx:.2f}" cy="{by:.2f}" rx="31" ry="37" fill="{p.P["warm"]}"{p.edge("warm")}/>')
            p.path(f"M{bx - 5},{by - 36} L{bx + 5},{by - 36} L{bx},{by - 42} Z", "warm")
        else:
            bx, by = ex, ey + 30 + 16
            p.raw(f'<path d="M{bx - 6},{by - 16} C{bx - 16},{by - 4} {bx - 10},{by + 14} {bx},{by + 16} '
                  f'C{bx + 10},{by + 14} {bx + 16},{by - 4} {bx + 6},{by - 16} Z" fill="{p.P["warm"]}"{p.edge("warm")}/>')


# ---------------------------------------------------------------- 4
def lesson4(p):
    """The particle model: solid, liquid and gas as particles — packed in
    rows, touching but jumbled, far apart."""
    r = 9.5
    w, h, y = 80, 92, 210
    xs = (16, 110, 204)
    lattice(p, xs[0] + 2, y - 1, 4, 3, r, "deep")
    jumble(p, xs[1] + 1, y - 1, w - 2, 2, r, "cool", 4)
    spread(p, xs[2], y - h, w, h, r, "mustard", 4, 41, gap=3.4)
    for x in xs:
        jar(p, x, y - h, w, h)


# ---------------------------------------------------------------- 5
def lesson5(p):
    """Particles are always moving: Brownian motion. A grain of pollen
    jiggles on a random zigzag path, knocked by water particles too small
    to see."""
    rnd = random.Random(5)
    x, y = 70, 210
    pts = [(x, y)]
    for _ in range(16):
        a = rnd.uniform(-1.3, 0.5) * math.pi / 2 + rnd.choice((0, 0, math.pi / 3))
        d = rnd.uniform(14, 30)
        x = min(260, max(40, x + d * math.cos(a)))
        y = min(250, max(50, y - abs(d * math.sin(a)) * rnd.choice((1, 1, -0.6))))
        pts.append((x, y))
    d = "M" + " L".join(f"{a:.1f},{b:.1f}" for a, b in pts)
    p.raw(f'<path d="{d}" fill="none" stroke="{ink(p)}" stroke-width="2" stroke-dasharray="3 5" '
          f'stroke-linecap="round" stroke-linejoin="round"/>')
    for a, b in pts[:-1]:
        p.circle(a, b, 2.6, "ink")
    gx, gy = pts[-1]
    p.circle(gx, gy, 22, "sun")
    # small water particles around the grain
    for k in range(9):
        ang = k * 40 + 12
        qx, qy = gx + 33 * math.cos(math.radians(ang)), gy + 33 * math.sin(math.radians(ang))
        particle(p, qx, qy, 5.5, "cool")


# ---------------------------------------------------------------- 6
def lesson6(p):
    """The limits of the model: under the lens a copper bar is particles
    with empty space between them — but each particle is not a tiny bit of
    copper-coloured solid. The model leaves things out."""
    rect(p, 18, 186, 264, 40, "warm")                     # the bar as we see it
    lx, ly, lr = 150, 112, 70
    p.line(lx + lr * 0.72, ly + lr * 0.72, lx + lr * 1.25, ly + lr * 1.25, 12, "ink")  # handle
    clip = p.uid("lens")
    p.raw(f'<clipPath id="{clip}"><circle cx="{lx}" cy="{ly}" r="{lr}"/></clipPath>')
    p.circle(lx, ly, lr, "pale")
    p.raw(f'<g clip-path="url(#{clip})">')
    r = 12
    for j in range(-4, 5):
        for i in range(-4, 5):
            x = lx + i * 2 * r * 1.12 + (j % 2) * r * 1.12
            y = ly + j * 2 * r * 0.98
            particle(p, x, y, r, "warm")
    p.raw("</g>")
    p.ring(lx, ly, lr, ink(p), 5)
    p.line(lx - lr * 0.5, ly + lr * 0.86, 120, 186, 1.6, extra=' stroke-dasharray="2 5"')
    p.line(lx + lr * 0.5, ly + lr * 0.86, 180, 186, 1.6, extra=' stroke-dasharray="2 5"')


# ---------------------------------------------------------------- 7
def lesson7(p):
    """Melting and freezing: a heating curve. Temperature rises, stays
    flat while the solid melts, then rises again."""
    x0, y0, x1, y1 = 46, 258, 276, 40
    plateau = 150
    band = p.uid("band")
    # the melting stretch, shaded
    rect(p, 112, y1 + 6, 88, y0 - y1 - 6, "cream" if p.mode == "colour" else "cool")
    arrow(p, x0, y0, x0, y1, 3)
    arrow(p, x0, y0, x1, y0, 3)
    d = f"M{x0 + 6},{y0 - 26} L112,{plateau} L200,{plateau} L262,{y1 + 34}"
    p.raw(f'<path d="{d}" fill="none" stroke="{p.P["warm"] if p.mode == "colour" else ink(p)}" '
          f'stroke-width="6" stroke-linejoin="round" stroke-linecap="round"/>')
    # a little ice cube melting on the plateau
    rect(p, 136, plateau - 46, 26, 26, "cool")
    p.raw(f'<path d="M132,{plateau - 18} C142,{plateau - 12} 162,{plateau - 12} 170,{plateau - 18}" '
          f'fill="none" stroke="{ink(p)}" stroke-width="2"/>')
    del band


# ---------------------------------------------------------------- 8
def lesson8(p):
    """Boiling, evaporation and condensation: a beaker boils; the gas meets
    a cold plate above and condenses back into drops."""
    bx, by, bw, bh = 92, 214, 116, 92
    rect(p, bx, by - 64, bw, 64, "cool")
    for cx, cy, r in [(118, 196, 7), (150, 178, 9), (184, 192, 6), (136, 164, 5), (172, 160, 6)]:
        p.circle(cx, cy, r, "paper", f' stroke="{ink(p)}" stroke-width="2"')
    jar(p, bx, by - bh, bw, bh)
    p.line(bx - 6, by, bx + bw + 6, by, 4, "ink")
    flame(p, 150, 262, 0.9)
    # rising gas particles
    for x, y in [(126, 100), (162, 92), (146, 70), (180, 112), (114, 78)]:
        particle(p, x, y, 6, "cool")
    # the cold plate, and drops forming underneath it
    rect(p, 66, 30, 168, 14, "deep")
    for x in range(84, 230, 24):
        p.path(f"M{x - 6},44 C{x - 6},52 {x - 3},58 {x},60 C{x + 3},58 {x + 6},52 {x + 6},44 Z", "cool")


# ---------------------------------------------------------------- 9
def lesson9(p):
    """Experiment 2, a cooling curve: a thermometer stands in a test tube
    of cooling liquid, read again and again over time."""
    tx, ttop, tw, tbot = 122, 70, 56, 250
    rect(p, tx, 176, tw, tbot - 176, "cool")
    p.raw(f'<path d="M{tx + tw},{tbot - tw / 2} A{tw / 2},{tw / 2} 0 0 1 {tx},{tbot - tw / 2}" '
          f'fill="{p.P["cool"]}"/>')
    outline(p, f"M{tx},{ttop} V{tbot - tw / 2} A{tw / 2},{tw / 2} 0 0 0 {tx + tw},{tbot - tw / 2} V{ttop}")
    # thermometer
    cx = tx + tw / 2
    rect(p, cx - 7, 30, 14, 196, "pale", f' stroke="{ink(p)}" stroke-width="2"' if p.mode == "colour" else "")
    p.raw(f'<rect x="{cx - 7}" y="30" width="14" height="196" rx="7" fill="none" stroke="{ink(p)}" stroke-width="2.4"/>')
    p.line(cx, 120, cx, 226, 6, "warm" if p.mode == "colour" else "ink")
    p.circle(cx, 228, 12, "warm")
    for k in range(7):
        y = 50 + k * 14
        p.line(cx + 7, y, cx + (16 if k % 2 == 0 else 12), y, 1.6, "ink")
    # time: a stopwatch beside it
    sx, sy = 236, 96
    p.circle(sx, sy, 30, "pale", f' stroke="{ink(p)}" stroke-width="3"' if p.mode == "colour" else "")
    p.raw(f'<rect x="{sx - 6}" y="{sy - 42}" width="12" height="9" fill="{ink(p)}"/>')
    p.line(sx, sy, sx, sy - 22, 3, "ink")
    p.line(sx, sy, sx + 15, sy + 6, 3, "ink")


# ---------------------------------------------------------------- 10
def lesson10(p):
    """Diffusion: a drop of colour spreads through still water, crowded at
    the middle and thinning out — no stirring needed."""
    bx, by, bw, bh = 46, 262, 208, 196
    rect(p, bx, by - 170, bw, 170, "pale" if p.mode == "colour" else "paper")
    p.line(bx + 2, by - 170, bx + bw - 2, by - 170, 2, "ink")
    rnd = random.Random(10)
    cx, cy = 150, 180
    for _ in range(170):
        rr = abs(rnd.gauss(0, 34))
        a = rnd.uniform(0, math.tau)
        x, y = cx + rr * math.cos(a) * 1.25, cy + rr * math.sin(a)
        if bx + 8 < x < bx + bw - 8 and by - 166 < y < by - 6:
            p.circle(x, y, 4.2, "warm" if p.mode == "colour" else "ink")
    jar(p, bx, by - bh, bw, bh)


# ---------------------------------------------------------------- 11
def lesson11(p):
    """Expansion and contraction: the ball and ring. Heated, the ball sits
    on the ring and won't pass through — its particles move more and take
    up more room (the particles themselves don't grow)."""
    rx, ry, rr = 150, 206, 50                     # the ring, seen edge-on
    br = 56
    by = ry - math.sqrt(br * br - (rr - 4) ** 2)   # the ball resting on the ring's rim
    # ring: back half, ball, front half
    p.raw(f'<path d="M{rx - rr},{ry} A{rr},14 0 0 1 {rx + rr},{ry}" fill="none" stroke="{ink(p)}" stroke-width="9"/>')
    p.line(rx + rr, ry, 278, ry + 30, 6, "ink")                              # handle
    p.circle(rx, by, br, "warm")
    p.raw(f'<path d="M{rx - rr},{ry} A{rr},14 0 0 0 {rx + rr},{ry}" fill="none" stroke="{ink(p)}" stroke-width="9"/>')
    p.raw(f'<path d="M{rx - rr},{ry} A{rr},14 0 0 0 {rx + rr},{ry}" fill="none" '
          f'stroke="{p.P["deep"] if p.mode == "colour" else "#fff"}" stroke-width="4"/>')
    # heat shimmer
    for dx in (-86, 86):
        x = rx + dx
        p.raw(f'<path d="M{x},{by + 34} C{x - 8},{by + 18} {x + 8},{by + 6} {x},{by - 10} '
              f'C{x - 8},{by - 26} {x + 8},{by - 36} {x},{by - 50}" fill="none" stroke="{ink(p)}" '
              f'stroke-width="2.4" stroke-linecap="round"/>')


# ---------------------------------------------------------------- 12
def lesson12(p):
    """Gas pressure: gas particles in a syringe hit the walls; push the
    plunger in and they hit more often."""
    x0, y0, x1, y1 = 34, 106, 226, 206
    plunger = 92
    rect(p, x0 + plunger, y0, x1 - x0 - plunger, y1 - y0, "pale" if p.mode == "colour" else "paper")
    outline(p, f"M{x0},{y0} H{x1} V{y0 + 34} H{x1 + 30} V{y1 - 34} H{x1} V{y1} H{x0}", 3)
    rect(p, x0 + plunger - 10, y0 + 2, 10, y1 - y0 - 4, "deep")
    rect(p, x0 - 26, y0 + 40, x0 + plunger - 10 - (x0 - 26), 20, "deep")
    rect(p, x0 - 36, y0 + 18, 10, 64, "deep")
    arrow(p, 6, 50, 64, 50, 3)
    pts = spread(p, x0 + plunger + 2, y0 + 2, x1 - x0 - plunger - 4, y1 - y0 - 4, 8, "mustard", 8, 12)
    # each particle's next move, toward a wall
    rnd = random.Random(12)
    for x, y in pts:
        a = rnd.uniform(0, math.tau)
        p.line(x + 11 * math.cos(a), y + 11 * math.sin(a), x + 24 * math.cos(a), y + 24 * math.sin(a), 2, "ink")


# ---------------------------------------------------------------- 13
def lesson13(p):
    """What density means: in the same water, a cork floats and a stone of
    the same size sinks — heavy for its size."""
    bx, by, bw, bh = 40, 262, 220, 190
    wl = by - 140
    rect(p, bx, wl, bw, by - wl, "cool")
    p.line(bx + 2, wl, bx + bw - 2, wl, 2, "ink")
    s = 46
    rect(p, 80, wl - s * 0.3, s, s, "cream" if p.mode == "colour" else "sun")      # floats, mostly above? no: 30% above
    rect(p, 172, by - s - 2, s, s, "dark" if p.mode == "colour" else "deep")        # sinks
    jar(p, bx, by - bh, bw, bh)


# ---------------------------------------------------------------- 14
def lesson14(p):
    """Calculating density: a block's length, width and height give its
    volume; with its mass, the density."""
    # isometric block
    ox, oy = 92, 214
    a, b, c = 120, 70, 76                      # length, depth, height
    cx, sx = math.cos(math.radians(30)), math.sin(math.radians(30))
    P0 = (ox, oy)
    P1 = (ox + a * cx, oy - a * sx)
    P3 = (ox - b * cx, oy - b * sx)
    P2 = (P1[0] - b * cx, P1[1] - b * sx)

    def up(pt):
        return (pt[0], pt[1] - c)

    def poly(pts, role):
        p.path("M" + " L".join(f"{x:.2f},{y:.2f}" for x, y in pts) + " Z", role,
               f' stroke="{ink(p)}" stroke-width="2.4" stroke-linejoin="round"' if p.mode == "colour" else "")

    poly([P0, P1, up(P1), up(P0)], "deep")
    poly([P0, P3, up(P3), up(P0)], "cool")
    poly([up(P0), up(P1), up(P2), up(P3)], "pale")
    # dimension ticks
    def dim(pa, pb, off):
        (x1, y1), (x2, y2) = pa, pb
        x1, y1, x2, y2 = x1 + off[0], y1 + off[1], x2 + off[0], y2 + off[1]
        p.line(x1, y1, x2, y2, 1.8, "ink")
        for x, y in ((x1, y1), (x2, y2)):
            p.line(x - 5, y - 5, x + 5, y + 5, 1.8, "ink")
    dim(P0, P1, (6, 14))
    dim(P0, P3, (-8, 14))
    dim(up(P1), P1, (16, 0))


# ---------------------------------------------------------------- 15
def lesson15(p):
    """Experiment 3, density by displacement: drop the object into a
    measuring cylinder and the water rises by its volume."""
    cx, cw, top, bot = 150, 76, 30, 262
    x0 = cx - cw / 2
    before, after = 186, 140
    rect(p, x0, after, cw, bot - after, "cool")
    rect(p, x0, before, cw, after - before if after > before else 0, "cool")
    p.line(x0 + 2, after, x0 + cw - 2, after, 2.4, "ink")
    # the first level, dashed
    p.line(x0 - 26, before, x0 + cw + 26, before, 2.2, extra=' stroke-dasharray="6 5"')
    p.line(x0 - 26, after, x0 - 2, after, 2.2)
    # the object at the bottom
    p.path(f"M{cx - 22},{bot - 4} L{cx - 26},{bot - 26} L{cx - 8},{bot - 44} L{cx + 18},{bot - 38} "
           f"L{cx + 24},{bot - 12} L{cx + 6},{bot - 4} Z", "warm")
    # scale marks
    for k in range(13):
        y = top + 26 + k * 16
        p.line(x0 + cw, y, x0 + cw - (14 if k % 2 == 0 else 8), y, 1.6, "ink")
    outline(p, f"M{x0},{top} V{bot} H{x0 + cw} V{top}", 3)
    p.line(x0 - 26, bot + 2, x0 + cw + 26, bot + 2, 5, "ink")
    # the rise
    arrow(p, x0 + cw + 18, before - 4, x0 + cw + 18, after + 4, 2.2, 7)


LESSONS = {n: globals()[f"lesson{n}"] for n in range(1, 16)}


def render(n, mode, ground):
    p = Pic(mode, f"pm{n}")
    LESSONS[n](p)
    return p.svg(ground=ground)


def main(argv):
    os.makedirs(SITE, exist_ok=True)
    os.makedirs(BOOK, exist_ok=True)
    rsvg = shutil.which("rsvg-convert")
    for n in LESSONS:
        with open(os.path.join(SITE, f"l{n}.svg"), "w", encoding="utf-8", newline="\n") as f:
            f.write(render(n, "colour", ground=False))
        inkf = os.path.join(BOOK, f"l{n}-ink.svg")
        with open(inkf, "w", encoding="utf-8", newline="\n") as f:
            f.write(render(n, "ink", ground=False))
        if rsvg:
            subprocess.run([rsvg, "-f", "pdf", inkf, "-o", inkf[:-4] + ".pdf"], check=True)
    print(f"wrote {len(LESSONS)} colour symbols to {os.path.relpath(SITE, ROOT)}"
          f" and {len(LESSONS)} ink symbols to {os.path.relpath(BOOK, ROOT)}"
          + ("" if rsvg else " (no rsvg-convert: ink PDFs not rebuilt)"))
    if "--sheet" in argv:
        from PIL import Image
        tiles = []
        with tempfile.TemporaryDirectory() as tmp:
            for mode in ("colour", "ink"):
                for n in LESSONS:
                    svg = os.path.join(tmp, f"{n}-{mode}.svg")
                    with open(svg, "w") as f:
                        f.write(render(n, mode, ground=True))
                    png = svg[:-4] + ".png"
                    subprocess.run([rsvg, "-w", "200", svg, "-o", png], check=True)
                    tiles.append(Image.open(png).convert("RGB"))
        cols = 8
        rows = math.ceil(len(tiles) / cols)
        sheet = Image.new("RGB", (cols * 210 + 10, rows * 210 + 10), "#888")
        for i, t in enumerate(tiles):
            sheet.paste(t, (10 + (i % cols) * 210, 10 + (i // cols) * 210))
        out = (argv[argv.index("--sheet-out") + 1] if "--sheet-out" in argv
               else os.path.join(tempfile.gettempdir(), "particle-symbols-sheet.png"))
        sheet.save(out)
        print(f"preview sheet: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
