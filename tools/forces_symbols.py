#!/usr/bin/env python3
"""Year 7 Forces & Motion lesson symbols (Lessons 1-18; 16-18 are the
trebuchet investigation).

Same system as tools/space_symbols.py: each symbol drawn once, every shape
carries a role, colour for the site and ink for the booklet. Force arrows
are always drawn in ink, so they read the same in both versions.

    python3 tools/forces_symbols.py [--sheet]

Writes year7-science/forces/img/symbols/lN.svg and
year7-science/forces/booklet/art/lN-ink.{svg,pdf}.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from unit_symbols_common import arrow, ground, poly, rect, stroke, write_all, ink  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UNIT = os.path.join(ROOT, "year7-science", "forces")
OUT = ' stroke="{}" stroke-width="2.4"'


def o(p):
    return OUT.format(ink(p))


def crate(p, x, y, w, h, role="mustard"):
    rect(p, x, y, w, h, role, o(p))
    stroke(p, f"M{x},{y} L{x + w},{y + h} M{x + w},{y} L{x},{y + h}", 1.6)


def ball(p, x, y, r, role="warm"):
    p.circle(x, y, r, role, o(p))


def trebuchet(p, x0=40, base=250, tilt=-35, role_arm="warm"):
    """Frame, pivot, a long arm with the counterweight on the short end."""
    px, py = x0 + 100, base - 120
    poly(p, [(x0 + 40, base), (px, py), (x0 + 160, base)], "dark", o(p))
    rect(p, x0, base, 200, 12, "deep", o(p))
    a = math.radians(tilt)
    lx, ly = px + 120 * math.cos(a), py + 120 * math.sin(a)   # long end
    sx, sy = px - 40 * math.cos(a), py - 40 * math.sin(a)     # short end
    p.line(sx, sy, lx, ly, 9, "ink")
    p.line(sx, sy, lx, ly, 5, role_arm)
    rect(p, sx - 20, sy + 4, 40, 34, "mustard", o(p))
    p.circle(px, py, 7, "ink")
    return lx, ly


# 1
def lesson1(p):
    """What is a force: a push and a pull, measured in newtons."""
    ground(p, 220)
    crate(p, 110, 140, 80, 80)
    arrow(p, 20, 180, 104, 180, 7, 20)
    stroke(p, "M190,170 L250,150", 3)
    arrow(p, 250, 150, 290, 136, 7, 20)


# 2
def lesson2(p):
    """Force diagrams & net force: four arrows on one object; the bigger
    sideways push wins."""
    crate(p, 115, 115, 70, 70, "cool")
    arrow(p, 150, 112, 150, 30, 6, 18)      # support
    arrow(p, 150, 188, 150, 270, 6, 18)     # weight
    arrow(p, 188, 150, 290, 150, 6, 18)     # big push
    arrow(p, 112, 150, 60, 150, 6, 18)      # small friction


# 3
def lesson3(p):
    """Experiment 1 — everyday forces: a magnet pulls a paperclip across
    the gap without touching it."""
    stroke(p, "M70,110 L70,200 A60,60 0 0 0 190,200 L190,110", 40, colour=p.P["warm"])
    stroke(p, "M50,110 L50,200 A80,80 0 0 0 210,200 L210,110 M90,110 L90,200 A40,40 0 0 0 170,200 L170,110", 2.4)
    rect(p, 50, 92, 40, 26, "pale", o(p))
    rect(p, 170, 92, 40, 26, "pale", o(p))
    stroke(p, "M70,86 C70,40 190,40 190,86", 2, dash="3 6")
    stroke(p, "M50,86 C44,10 216,10 210,86", 2, dash="3 6")
    # the paperclip, pulled up between the poles
    stroke(p, "M118,64 L118,40 C118,30 142,30 142,40 L142,70 C142,78 126,78 126,70 L126,48", 3.2)
    arrow(p, 130, 118 - 30, 130, 80, 3, 10)


# 4
def lesson4(p):
    """Newton's first & third laws: the rocket pushes gas down; the gas
    pushes the rocket up."""
    cx = 150
    p.path(f"M{cx},24 C{cx + 34},60 {cx + 34},120 {cx + 30},190 L{cx - 30},190 C{cx - 34},120 {cx - 34},60 {cx},24 Z", "pale", o(p))
    p.circle(cx, 90, 14, "cool")
    poly(p, [(cx - 30, 150), (cx - 58, 200), (cx - 30, 190)], "warm", o(p))
    poly(p, [(cx + 30, 150), (cx + 58, 200), (cx + 30, 190)], "warm", o(p))
    p.path(f"M{cx - 20},194 L{cx + 20},194 L{cx + 8},240 L{cx},270 L{cx - 8},240 Z", "sun")
    arrow(p, 250, 230, 250, 60, 6, 18)
    arrow(p, 50, 60, 50, 250, 6, 18)


# 5
def lesson5(p):
    """Newton's second law, F = ma: one force, a trolley speeding up."""
    ground(p, 230)
    rect(p, 110, 150, 110, 56, "cool", o(p))
    for x in (132, 198):
        ball(p, x, 214, 14, "dark")
    arrow(p, 18, 178, 104, 178, 7, 20)
    for i, y in enumerate((160, 178, 196)):
        p.line(232 + i * 6, y, 270 + i * 8, y, 3, "ink")


# 6
def lesson6(p):
    """Experiment 2 — friction and mass: add masses to the block and
    friction grows against the pull."""
    rect(p, 0, 222, 300, 30, "warm", o(p))
    rect(p, 96, 162, 100, 60, "mustard", o(p))
    for i in range(3):
        rect(p, 114, 140 - i * 22, 64, 20, "dark", o(p))
    arrow(p, 200, 192, 290, 192, 6, 18)
    arrow(p, 96, 214, 26, 214, 6, 18)


# 7
def lesson7(p):
    """Energy & transformation: a pendulum trades height for speed and back."""
    px, py, L = 150, 30, 190
    for ang, role, alpha in ((-40, "warm", 1), (0, "mustard", 1), (40, "warm", 1)):
        a = math.radians(ang)
        x, y = px + L * math.sin(a), py + L * math.cos(a)
        p.line(px, py, x, y, 2 if ang else 3, "ink", "" if ang == 0 else ' stroke-dasharray="5 5"')
        ball(p, x, y, 18, role)
    stroke(p, f"M{px + L * math.sin(math.radians(-40)):.1f},{py + L * math.cos(math.radians(-40)) + 26:.1f} "
              f"A{L + 26},{L + 26} 0 0 0 {px + L * math.sin(math.radians(40)):.1f},{py + L * math.cos(math.radians(40)) + 26:.1f}",
           2, dash="3 6")
    rect(p, 110, 20, 80, 10, "dark", o(p))


# 8
def lesson8(p):
    """Experiment 3 — bounce efficiency: each bounce is lower than the drop
    before it."""
    ground(p, 250)
    x, h, d = 30, 200, 0
    path = f"M{x},50"
    pts = []
    for k in range(4):
        w = 70 - k * 12
        path += f" Q{x + w / 2},{250 - h * 2 + 250 if False else 250 - h} {x + w},250" if k else f" L{x},250"
        if k:
            pass
        pts.append(x)
        x += w if k else 0
        h *= 0.6
    # simpler, explicit arcs
    stroke(p, "M40,40 L40,236 Q80,90 120,236 Q148,140 176,236 Q196,180 216,236 Q228,210 240,236", 2.6, dash="5 5")
    ball(p, 40, 40, 14, "warm")
    ball(p, 240, 236, 14, "warm")
    for x, top in ((80, 163), (148, 188), (196, 208)):
        p.line(x + 46, top - 2, x + 46, 250, 1.4, "ink", ' stroke-dasharray="2 4"')
    del path, pts, d


# 9
def lesson9(p):
    """Simple machines & levers: a small effort far from the fulcrum lifts
    a big load close to it."""
    poly(p, [(120, 230), (150, 180), (180, 230)], "dark", o(p))
    ground(p, 232)
    p.line(20, 186, 280, 168, 8, "ink")
    p.line(20, 186, 280, 168, 4, "mustard")
    crate(p, 64, 128, 64, 54, "warm")
    arrow(p, 262, 90, 262, 160, 6, 16)


# 10
def lesson10(p):
    """Experiment 4 — mechanical advantage: a light mass far out balances a
    heavy one close in."""
    poly(p, [(130, 230), (150, 160), (170, 230)], "dark", o(p))
    ground(p, 232)
    p.line(20, 158, 280, 158, 8, "ink")
    p.line(20, 158, 280, 158, 4, "cool")
    for x, w, h in ((96, 50, 70), (250, 24, 30)):
        p.line(x, 158, x, 168, 2, "ink")
        rect(p, x - w / 2, 168, w, h, "warm" if w > 30 else "mustard", o(p))
    for x0, x1 in ((96, 150), (150, 250)):
        stroke(p, f"M{x0},132 L{x1},132", 1.8)
        stroke(p, f"M{x0},124 L{x0},140 M{x1},124 L{x1},140", 1.8)


# 11
def lesson11(p):
    """Levers extension: the tip of a long arm sweeps a much bigger arc than
    the short end in the same turn — that is the trebuchet's speed."""
    px, py = 150, 170
    for r, w in ((120, 3), (40, 3)):
        stroke(p, f"M{px - r * math.cos(math.radians(30)):.1f},{py - r * math.sin(math.radians(30)):.1f} "
                  f"A{r},{r} 0 0 1 {px + r * math.cos(math.radians(30)):.1f},{py - r * math.sin(math.radians(30)):.1f}",
               w, dash="6 6")
    p.line(px - 40, py, px + 120, py, 9, "ink")
    p.line(px - 40, py, px + 120, py, 5, "warm")
    p.circle(px, py, 8, "ink")
    arrow(p, px + 104 * math.cos(math.radians(30)), py - 104 * math.sin(math.radians(30)) - 22,
          px + 70, py - 104 - 16, 3, 12)
    rect(p, px - 60, py + 4, 40, 34, "mustard", o(p))


# 12
def lesson12(p):
    """Projectile motion: across at a steady speed, down faster and faster
    — together, a curve."""
    ground(p, 250)
    rect(p, 14, 60, 60, 190, "dark", o(p))
    xs = [74 + 36 * i for i in range(6)]
    ys = [60 + 7.2 * i * i for i in range(6)]
    stroke(p, "M74,60 " + " ".join(f"L{x:.0f},{y:.0f}" for x, y in zip(xs, ys)), 2, dash="4 6")
    for x, y in zip(xs, ys):
        ball(p, x, y - 0, 9, "warm")
    arrow(p, 80, 34, 140, 34, 3, 12)


# 13
def lesson13(p):
    """Experiment 5 — measuring g: a falling ball under a motion sensor
    covers more ground in each equal time."""
    rect(p, 110, 20, 80, 30, "dark", o(p))
    p.line(150, 50, 150, 64, 3, "ink")
    y, gap = 76, 26
    for k in range(5):
        ball(p, 150, y, 11, "warm" if k == 4 else "pale")
        p.line(196, y, 214, y, 1.6, "ink")
        y += gap
        gap += 13
    stroke(p, "M214,76 L214,248", 1.6)
    ground(p, 276)


# 14
def lesson14(p):
    """Optimising range: launched at 45°, the shot goes furthest; 30° and
    60° land together, short of it."""
    ground(p, 250)
    def arc(deg, role):
        r = 230 * math.sin(math.radians(2 * deg))
        h = r * math.tan(math.radians(deg)) / 4
        stroke(p, f"M24,250 Q{24 + r / 2:.1f},{250 - 2 * h:.1f} {24 + r:.1f},250", 4 if deg == 45 else 2.4,
               colour=p.P[role] if p.mode == "colour" else "#111", dash=None if deg == 45 else "6 5")
    arc(30, "cool")
    arc(60, "cool")
    arc(45, "warm")
    p.circle(254, 250, 8, "ink")


# 15
def lesson15(p):
    """Planning the investigation: the trebuchet itself."""
    lx, ly = trebuchet(p)
    stroke(p, f"M{lx},{ly} L{lx + 18},{ly + 34}", 2)
    ball(p, lx + 18, ly + 42, 10, "cream")


# 16
def lesson16(p):
    """Trebuchet launches: the throw, and the tape along the ground."""
    lx, ly = trebuchet(p, 10, 240, -70)
    stroke(p, f"M{lx},{ly} Q220,0 286,236", 2.4, dash="5 6")
    ball(p, 286, 228, 9, "cream")
    rect(p, 120, 262, 176, 12, "mustard", o(p))
    for x in range(130, 296, 16):
        p.line(x, 262, x, 268, 1.4, "ink")


# 17
def lesson17(p):
    """Analysis & conclusion: range against counterweight — a line graph."""
    stroke(p, "M50,30 L50,250 L280,250", 3)
    pts = [(80, 216), (122, 180), (166, 150), (208, 116), (250, 92)]
    stroke(p, "M70,224 L262,84", 2.4, colour=p.P["warm"] if p.mode == "colour" else "#111")
    for x, y in pts:
        p.circle(x, y, 7, "dark")
    for x in (80, 122, 166, 208, 250):
        p.line(x, 250, x, 258, 2, "ink")


# 18
def lesson18(p):
    """Investigation test: open booklet, pencil in hand."""
    poly(p, [(40, 70), (150, 90), (150, 260), (40, 240)], "pale", o(p))
    poly(p, [(260, 70), (150, 90), (150, 260), (260, 240)], "pale", o(p))
    for k in range(5):
        y = 120 + k * 24
        p.line(60, y - 2 + k * 0, 136, y + 10, 1.6, "ink")
        p.line(164, y + 10, 240, y - 2, 1.6, "ink")
    p.raw(f'<g transform="rotate(35 220 120)">')
    rect(p, 208, 20, 18, 120, "mustard", o(p))
    poly(p, [(208, 140), (226, 140), (217, 160)], "cream", o(p))
    p.raw("</g>")


LESSONS = {n: globals()[f"lesson{n}"] for n in range(1, 19)}

if __name__ == "__main__":
    write_all(LESSONS, "frc", os.path.join(UNIT, "img", "symbols"), os.path.join(UNIT, "booklet", "art"), sys.argv)
