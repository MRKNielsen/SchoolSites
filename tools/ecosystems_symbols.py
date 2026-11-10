#!/usr/bin/env python3
"""Year 7 Biodiversity & Ecosystems lesson symbols (Lessons 1-11).

Same system as tools/space_symbols.py: each symbol drawn once, every shape
carries a role, colour for the site and ink for the booklet.

    python3 tools/ecosystems_symbols.py [--sheet]

Writes year7-science/bio-ecosystems/img/symbols/lN.svg and
year7-science/bio-ecosystems/booklet/art/lN-ink.{svg,pdf}.
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from unit_symbols_common import arrow, ground, poly, rect, stroke, write_all, ink  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UNIT = os.path.join(ROOT, "year7-science", "bio-ecosystems")


def leaf(p, x, y, ang, L=34, w=11, role="deep"):
    """A eucalypt-style leaf from (x, y) pointing at angle ang (degrees)."""
    a = math.radians(ang)
    tx, ty = x + L * math.cos(a), y + L * math.sin(a)
    nx, ny = -math.sin(a) * w, math.cos(a) * w
    mx, my = (x + tx) / 2, (y + ty) / 2
    p.path(f"M{x:.1f},{y:.1f} Q{mx + nx:.1f},{my + ny:.1f} {tx:.1f},{ty:.1f} Q{mx - nx:.1f},{my - ny:.1f} {x:.1f},{y:.1f} Z", role)


# 1 ------------------------------------------------------------------
def lesson1(p):
    """Living or non-living: a seed has sent up a shoot; a pebble beside it
    has not. Same soil, only one grows."""
    rect(p, 0, 220, 300, 80, "warm")
    ground(p, 220)
    # seedling
    stroke(p, "M100,220 C100,180 96,150 104,112", 5, colour=p.P["deep"] if p.mode == "colour" else "#111")
    leaf(p, 104, 118, -150, 42, 14)
    leaf(p, 104, 118, -30, 46, 15)
    p.raw(f'<ellipse cx="100" cy="232" rx="16" ry="10" fill="{p.P["cream"]}"{p.edge("cream")}'
          + (f' stroke="{ink(p)}" stroke-width="1.8"' if p.mode == "colour" else "") + '/>')
    # roots
    stroke(p, "M100,240 C96,252 92,258 86,266 M100,240 C104,254 110,260 116,270", 2.2)
    # pebble
    p.raw(f'<path d="M180,220 C176,198 196,186 220,188 C246,190 258,204 252,220 Z" fill="{p.P["dark"] if p.mode == "colour" else "url(#hd)"}"'
          + (' stroke="#111" stroke-width="1.8"' if p.mode == "ink" else "") + '/>')


# 2 ------------------------------------------------------------------
def lesson2(p):
    """Classification levels: groups inside groups, narrowing from kingdom
    to one species."""
    roles = ["cream", "mustard", "cool", "deep", "warm"]
    for i, role in enumerate(roles):
        inset = i * 24
        p.raw(f'<rect x="{30 + inset}" y="{30 + inset}" width="{240 - 2 * inset}" height="{240 - 2 * inset}" rx="{18 - i * 2}" '
              f'fill="{p.P[role]}" stroke="{ink(p)}" stroke-width="2.2"/>')
    p.circle(150, 150, 12, "ink")


# 3 ------------------------------------------------------------------
def lesson3(p):
    """Scientific names & the six kingdoms: life divided six ways."""
    roles = ["deep", "mustard", "warm", "cool", "dark", "cream"]
    cx, cy, r = 150, 150, 118
    for i, role in enumerate(roles):
        a0, a1 = math.radians(90 + i * 60), math.radians(90 + (i + 1) * 60)
        x0, y0 = cx + r * math.cos(a0), cy - r * math.sin(a0)
        x1, y1 = cx + r * math.cos(a1), cy - r * math.sin(a1)
        p.raw(f'<path d="M{cx},{cy} L{x0:.1f},{y0:.1f} A{r},{r} 0 0 0 {x1:.1f},{y1:.1f} Z" fill="{p.P[role]}" '
              f'stroke="{p.P["paper"] if p.mode == "colour" else "#111"}" stroke-width="{4 if p.mode == "colour" else 2}"/>')
    p.circle(cx, cy, 26, "paper", f' stroke="{ink(p)}" stroke-width="2.4"')


# 4 ------------------------------------------------------------------
def lesson4(p):
    """Dichotomous keys: every question splits the group in two, until one
    organism is left at each tip."""
    nodes = {"a": (150, 40), "b": (84, 120), "c": (216, 120)}
    tips = [(46, 214), (122, 214), (178, 214), (254, 214)]
    stroke(p, "M150,40 L84,120 M150,40 L216,120 M84,120 L46,214 M84,120 L122,214 M216,120 L178,214 M216,120 L254,214", 4)
    for x, y in nodes.values():
        p.circle(x, y, 13, "paper", f' stroke="{ink(p)}" stroke-width="3"')
    for (x, y), role in zip(tips, ["deep", "mustard", "warm", "cool"]):
        p.circle(x, y + 18, 24, role)


# 5 ------------------------------------------------------------------
def lesson5(p):
    """Australian ecosystems & biodiversity: the living (tree, bird) and the
    non-living (sun, water, rock) together."""
    p.circle(238, 64, 34, "sun")
    rect(p, 0, 228, 300, 72, "cool")
    for x in range(0, 300, 40):
        stroke(p, f"M{x},240 q10,-6 20,0 q10,6 20,0", 2, colour=p.P["paper"] if p.mode == "colour" else "#111")
    p.path("M0,228 L0,200 C40,190 80,196 110,206 C130,214 150,222 170,228 Z", "warm")
    # gum tree
    rect(p, 66, 120, 12, 90, "dark")
    for cx, cy, r in [(52, 112, 30), (90, 96, 34), (72, 72, 28)]:
        p.circle(cx, cy, r, "deep")
    # bird
    stroke(p, "M150,110 q12,-12 24,0 q12,-12 24,0", 4)


# 6 ------------------------------------------------------------------
def lesson6(p):
    """Food webs & energy flow: a lot of producer supports less consumer —
    energy is lost at every step up."""
    tiers = [("deep", 240, 64), ("mustard", 170, 138), ("warm", 100, 210)]
    for role, w, y in [("warm", 84, 70), ("mustard", 164, 140), ("deep", 244, 210)]:
        x = 150 - w / 2
        poly(p, [(x, y + 60), (x + w, y + 60), (x + w - 22, y), (x + 22, y)], role,
             f' stroke="{ink(p)}" stroke-width="2.2"' if p.mode == "colour" else "")
    del tiers
    arrow(p, 270, 250, 270, 70, 4, 14)


# 7 ------------------------------------------------------------------
def lesson7(p):
    """Ecosystem services: a native bee pollinating a flower."""
    cx, cy = 118, 178
    stroke(p, f"M{cx},{cy} L{cx},286", 5, colour=p.P["deep"] if p.mode == "colour" else "#111")
    for k in range(6):
        a = math.radians(k * 60)
        p.raw(f'<ellipse cx="{cx + 34 * math.cos(a):.1f}" cy="{cy + 34 * math.sin(a):.1f}" rx="26" ry="15" '
              f'transform="rotate({k * 60} {cx + 34 * math.cos(a):.1f} {cy + 34 * math.sin(a):.1f})" fill="{p.P["cream"]}" '
              f'stroke="{ink(p)}" stroke-width="2"/>')
    p.circle(cx, cy, 18, "mustard")
    # bee
    bx, by = 214, 92
    for dx in (-10, 10):
        p.raw(f'<ellipse cx="{bx + dx}" cy="{by - 24}" rx="12" ry="20" transform="rotate({dx * 2} {bx + dx} {by - 24})" '
              f'fill="{p.P["pale"]}" stroke="{ink(p)}" stroke-width="2"/>')
    p.raw(f'<ellipse cx="{bx}" cy="{by}" rx="30" ry="19" fill="{p.P["mustard"]}" stroke="{ink(p)}" stroke-width="2.2"/>')
    for dx in (-8, 8):
        p.line(bx + dx, by - 18, bx + dx, by + 18, 5, "ink")
    stroke(p, f"M{bx - 32},{by + 8} C170,140 150,150 {cx + 16},{cy - 22}", 2, dash="3 6")


# 8 ------------------------------------------------------------------
def lesson8(p):
    """Adaptations: eucalypt leaves hang edge-on to the midday sun, so less
    of each leaf is baked."""
    p.circle(150, 40, 30, "sun")
    for x in (60, 120, 180, 240):
        p.line(x, 76, x, 92, 3, "mustard" if p.mode == "colour" else "ink")
    stroke(p, "M20,112 C90,100 210,100 280,112", 6, colour=p.P["dark"] if p.mode == "colour" else "#111")
    for x in (52, 98, 150, 202, 248):
        leaf(p, x, 108, 90 + (x % 3 - 1) * 6, 120, 13)


# 9 ------------------------------------------------------------------
def lesson9(p):
    """Introduced species: a large carp takes over the river; the small
    native fish are pushed out."""
    rect(p, 0, 40, 300, 230, "cool")
    def fish(x, y, s, role, flip=False):
        d = -1 if flip else 1
        p.path(f"M{x},{y} C{x + d * 40 * s},{y - 34 * s} {x + d * 100 * s},{y - 30 * s} {x + d * 130 * s},{y} "
               f"C{x + d * 100 * s},{y + 30 * s} {x + d * 40 * s},{y + 34 * s} {x},{y} Z", role,
               f' stroke="{ink(p)}" stroke-width="2.2"')
        poly(p, [(x, y), (x - d * 30 * s, y - 24 * s), (x - d * 30 * s, y + 24 * s)], role,
             f' stroke="{ink(p)}" stroke-width="2.2"')
        p.circle(x + d * 104 * s, y - 6 * s, 5 * s, "ink")
    fish(70, 170, 1.3, "warm")
    for x, y in [(56, 76), (110, 66), (82, 104)]:
        fish(x, y, 0.32, "pale", flip=True)


# 10 -----------------------------------------------------------------
def lesson10(p):
    """Human impacts: one forest cut into islands by a road and clearing —
    habitat fragmentation."""
    rect(p, 20, 20, 260, 260, "cream")
    for x, y, w, h in [(30, 30, 110, 96), (164, 30, 106, 70), (30, 160, 70, 110), (190, 150, 80, 120)]:
        p.raw(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="{p.P["deep"]}"{p.edge("deep")}/>')
    rect(p, 20, 128, 260, 22, "dark")
    for x in range(30, 280, 30):
        p.line(x, 139, x + 14, 139, 3, "paper")
    p.raw(f'<rect x="20" y="20" width="260" height="260" fill="none" stroke="{ink(p)}" stroke-width="2.6"/>')


# 11 -----------------------------------------------------------------
def lesson11(p):
    """Conservation & action: a corridor of planted bush joins two patches,
    so animals can move between them again."""
    rect(p, 20, 20, 260, 260, "cream")
    p.raw(f'<rect x="30" y="40" width="90" height="220" rx="16" fill="{p.P["deep"]}"{p.edge("deep")}/>')
    p.raw(f'<rect x="180" y="40" width="90" height="220" rx="16" fill="{p.P["deep"]}"{p.edge("deep")}/>')
    p.raw(f'<rect x="112" y="128" width="76" height="44" fill="{p.P["cool"]}"{p.edge("cool")}/>')
    for x in (128, 150, 172):
        p.circle(x, 150, 9, "deep")
    stroke(p, "M76,150 C110,110 190,110 224,150", 2.4, dash="4 7")
    arrow(p, 206, 133, 224, 150, 2.4, 10)
    p.raw(f'<rect x="20" y="20" width="260" height="260" fill="none" stroke="{ink(p)}" stroke-width="2.6"/>')


LESSONS = {n: globals()[f"lesson{n}"] for n in range(1, 12)}

if __name__ == "__main__":
    random.seed(0)
    write_all(LESSONS, "eco", os.path.join(UNIT, "img", "symbols"), os.path.join(UNIT, "booklet", "art"), sys.argv)
