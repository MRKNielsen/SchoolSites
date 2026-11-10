#!/usr/bin/env python3
"""Year 7 Space lesson symbols — one diagrammatic idea per lesson.

The workbook redesign's lesson art, in the manner of George Giusti's covers
for the Anchor Science Study Series: one idea, flat shapes, crisp lines, a
soft airbrush gradient only on light sources, lots of empty paper.

Each symbol is drawn ONCE. Every shape carries a ROLE; the role maps to a
flat cover colour (site, decks) or to a black-and-white ink treatment
(solid, hatch, stipple, or white with an outline) for the A5 booklet, so the
two versions can never drift apart.

    python3 tools/space_symbols.py            # write everything
    python3 tools/space_symbols.py --sheet    # also a preview sheet in the temp folder (needs rsvg-convert + Pillow)

Writes
    year7-science/space/img/symbols/lN.svg        colour, transparent ground (contents page, decks)
    year7-science/space/booklet/art/lN-ink.svg    black and white, for the booklet
    year7-science/space/booklet/art/lN-ink.pdf    the same as PDF for XeLaTeX (only if rsvg-convert exists)

Rules the drawings keep (CLAUDE.md):
  * Orbits are circles centred on the body they go round, and every orbiting
    thing sits exactly on its circle — asserted, not eyeballed.
  * The Moon waxes lit on the LEFT, as seen from Melbourne.
  * Lesson 7 shows the Milky Way and its dark dust lane over Country. It does
    not draw the Emu in the Sky or any other specific figure: those belong to
    particular peoples and their stories, and are taught in the lesson from
    their sources, not reinvented as decoration here.
"""
import math
import os
import random
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "year7-science", "space", "img", "symbols")
BOOK = os.path.join(ROOT, "year7-science", "space", "booklet", "art")
W = H = 300
TAU = math.tau

COLOUR = {
    "paper": "#efe6d2", "ink": "#1f2a33",
    "dark": "#1e4d78",      # navy
    "deep": "#1f6e6c",      # deep teal
    "warm": "#c8502a",      # rust
    "sun": "url(#sun)",     # mustard, airbrushed
    "lit": "url(#lit)",     # cream, airbrushed toward the terminator
    "cream": "#f2d79a",
    "pale": "#f7f0de",
    "cool": "#3d9aa1",      # teal
    "mustard": "#d9a12b",
    "night": "#1b2d45",     # Lesson 7's sky
}
INK = {
    "paper": "#ffffff", "ink": "#111111",
    "dark": "#111111",
    "deep": "url(#hd)",     # dense diagonal hatch
    "warm": "url(#hm)",     # medium cross-hatch
    "sun": "url(#dt)",      # stipple
    "lit": "#ffffff",
    "cream": "#ffffff",
    "pale": "#ffffff",
    "cool": "url(#hl)",     # light horizontal hatch
    "mustard": "url(#dt)",
    "night": "#111111",
}


def defs(mode):
    if mode == "colour":
        return """<defs>
  <radialGradient id="sun" cx="35%" cy="40%" r="75%">
    <stop offset="0" stop-color="#f0c45a"/><stop offset="1" stop-color="#d39a26"/></radialGradient>
  <linearGradient id="lit" x1="0" x2="1">
    <stop offset="0" stop-color="#f7e3ae"/><stop offset="1" stop-color="#e9c574"/></linearGradient>
</defs>"""
    return """<defs>
  <pattern id="hd" width="4" height="4" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
    <rect width="4" height="4" fill="#fff"/><line x1="0" y1="0" x2="0" y2="4" stroke="#111" stroke-width="2"/></pattern>
  <pattern id="hm" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
    <rect width="6" height="6" fill="#fff"/><line x1="0" y1="0" x2="0" y2="6" stroke="#111" stroke-width="1.3"/>
    <line x1="0" y1="0" x2="6" y2="0" stroke="#111" stroke-width="1.3"/></pattern>
  <pattern id="hl" width="6" height="6" patternUnits="userSpaceOnUse">
    <rect width="6" height="6" fill="#fff"/><line x1="0" y1="3" x2="6" y2="3" stroke="#111" stroke-width="1"/></pattern>
  <pattern id="dt" width="6" height="6" patternUnits="userSpaceOnUse">
    <rect width="6" height="6" fill="#fff"/><circle cx="1.5" cy="1.5" r="1" fill="#111"/>
    <circle cx="4.5" cy="4.5" r="1" fill="#111"/></pattern>
</defs>"""


class Pic:
    def __init__(self, mode, key):
        self.mode, self.key = mode, key
        self.P = COLOUR if mode == "colour" else INK
        self.out = []

    def edge(self, role):
        # In ink every filled shape gets an outline, so hatch has a boundary.
        if self.mode == "ink" and role not in ("ink", "paper", "night"):
            return ' stroke="#111" stroke-width="1.8"'
        return ""

    def circle(self, cx, cy, r, role, extra=""):
        self.out.append(f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r:.2f}" fill="{self.P[role]}"{self.edge(role)}{extra}/>')

    def ring(self, cx, cy, r, colour, w, extra=""):
        self.out.append(f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r:.2f}" fill="none" stroke="{colour}" stroke-width="{w}"{extra}/>')

    def orbit(self, cx, cy, r):
        self.ring(cx, cy, r, self.P["ink"], 1.4, ' stroke-dasharray="1 5" stroke-linecap="round"')

    def path(self, d, role, extra=""):
        self.out.append(f'<path d="{d}" fill="{self.P[role]}"{self.edge(role)}{extra}/>')

    def line(self, x1, y1, x2, y2, w=2, role="ink", extra=""):
        self.out.append(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" '
                        f'stroke="{self.P[role]}" stroke-width="{w}" stroke-linecap="round"{extra}/>')

    def raw(self, s):
        self.out.append(s)

    def uid(self, name):
        """Ids are unique per lesson and mode, so several symbols can share a page."""
        return f"{self.key}-{self.mode}-{name}"

    def svg(self, ground=True):
        body = "\n".join(self.out)
        d = defs(self.mode)
        # gradients/patterns are shared names; make them unique to this file too
        for name in ("sun", "lit", "hd", "hm", "hl", "dt"):
            d = d.replace(f'id="{name}"', f'id="{self.uid(name)}"')
            body = body.replace(f"url(#{name})", f"url(#{self.uid(name)})")
        g = f'<rect width="{W}" height="{H}" fill="{self.P["paper"]}"/>\n' if ground else ""
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}">\n{d}\n{g}{body}\n</svg>\n')


def polar(cx, cy, r, deg):
    """Point on a circle; 0 deg = east, counter-clockwise on screen."""
    return cx + r * math.cos(math.radians(deg)), cy - r * math.sin(math.radians(deg))


def on_circle(cx, cy, r, x, y):
    assert abs(math.hypot(x - cx, y - cy) - r) < 1e-6, "not on its orbit"


def sector(cx, cy, r, a0, a1):
    x0, y0 = polar(cx, cy, r, a0)
    x1, y1 = polar(cx, cy, r, a1)
    large = 1 if (a1 - a0) % 360 > 180 else 0
    return f"M{cx:.2f},{cy:.2f} L{x0:.2f},{y0:.2f} A{r},{r} 0 {large} 0 {x1:.2f},{y1:.2f} Z"


def annulus(cx, cy, r0, r1):
    """A ring between two radii (even-odd fill)."""
    def c(r):
        return (f"M{cx + r:.2f},{cy:.2f} A{r},{r} 0 1 0 {cx - r:.2f},{cy:.2f} "
                f"A{r},{r} 0 1 0 {cx + r:.2f},{cy:.2f} Z ")
    return c(r1) + c(r0)


def lit_part(cx, cy, r, k):
    """Lit region of a Moon disc, lit fraction k in (0,1), lit on the LEFT
    (waxing as seen from the southern hemisphere — Melbourne)."""
    top, bot = (cx, cy - r), (cx, cy + r)
    d = f"M{top[0]:.2f},{top[1]:.2f} A{r},{r} 0 0 0 {bot[0]:.2f},{bot[1]:.2f} "
    rx = r * abs(1 - 2 * k)
    if abs(k - 0.5) < 1e-9:
        return d + "Z"
    sweep = 1 if k < 0.5 else 0
    return d + f"A{rx:.2f},{r} 0 0 {sweep} {top[0]:.2f},{top[1]:.2f} Z"


# ---------------------------------------------------------------- 1
def lesson1(p):
    """Earth, Moon & Sun — scale and structure: the Sun is too big to fit;
    Earth, cut open, shows its layers; the Moon is 0.27 of Earth's width."""
    p.circle(372, 96, 170, "sun")
    ex, ey, er = 112, 188, 64
    p.circle(ex, ey, er, "deep")
    p.path(sector(ex, ey, er * 0.86, 0, 90), "warm")
    p.path(sector(ex, ey, er * 0.55, 0, 90), "mustard" if p.mode == "colour" else "cool")
    p.path(sector(ex, ey, er * 0.27, 0, 90), "cream")
    mr, mx, my = er * 0.27, 226, 252
    p.circle(mx, my, mr, "pale", f' stroke="{p.P["ink"]}" stroke-width="2"' if p.mode == "colour" else "")
    p.line(ex + er + 10, ey + 34, mx - mr - 8, my - 6, 1.6, extra=' stroke-dasharray="2 5"')


# ---------------------------------------------------------------- 2
def lesson2(p):
    """Day, night & seasons: parallel sunlight, the lit half, the tilted axis."""
    for i, y in enumerate([92, 122, 152, 182, 212]):
        p.line(18, y, 78 + (i % 2) * 14, y, 6, "mustard" if p.mode == "colour" else "ink")
    cx, cy, r = 186, 152, 86
    p.circle(cx, cy, r, "dark")
    p.path(f"M{cx},{cy - r} A{r},{r} 0 0 0 {cx},{cy + r} Z", "lit")
    if p.mode == "ink":
        p.ring(cx, cy, r, "#111", 2)
    tilt = math.radians(23.5)
    dx, dy = math.sin(tilt), -math.cos(tilt)
    a = r + 30
    p.line(cx - r * math.cos(tilt) * 0.98, cy - r * math.sin(tilt) * 0.98,
           cx + r * math.cos(tilt) * 0.98, cy + r * math.sin(tilt) * 0.98, 2.5,
           "cool" if p.mode == "colour" else "ink", ' stroke-dasharray="7 5"')
    p.line(cx - a * dx, cy - a * dy, cx + a * dx, cy + a * dy, 8, "paper")
    p.line(cx - a * dx, cy - a * dy, cx + a * dx, cy + a * dy, 3.5, "ink")
    p.circle(cx + a * dx, cy + a * dy, 5, "ink")
    p.circle(cx - a * dx, cy - a * dy, 5, "paper", f' stroke="{p.P["ink"]}" stroke-width="3"')


# ---------------------------------------------------------------- 3
def lesson3(p):
    """Phases & tides: the lit part grows from the left (southern sky), and
    the sea rises and falls in step."""
    r = 27
    for x, k in zip([48, 116, 184, 252], [0.22, 0.5, 0.78, 1.0]):
        p.circle(x, 96, r, "dark")
        if k >= 1:
            p.circle(x, 96, r, "lit")
        else:
            p.path(lit_part(x, 96, r, k), "lit")
        if p.mode == "ink":
            p.ring(x, 96, r, "#111", 2)
    for i, (y0, amp, role) in enumerate([(176, 16, "cool"), (212, 12, "deep"), (246, 8, "dark")]):
        pts = [f"{x:.1f},{y0 + amp * math.sin(x / 300 * TAU + i * 0.6):.1f}" for x in range(0, 301, 5)]
        p.path("M0,300 L" + " L".join(pts) + " L300,300 Z", role)


# ---------------------------------------------------------------- 4
def lesson4(p):
    """Reading the rocks: layers that thicken and thin with the tides
    (rhythmites — the record of a 21.9-hour day), and the Acraman impact
    falling on them."""
    x0, x1, top, bot = 34, 266, 132, 274
    cx, cr = 186, 30                               # the crater, cut into the top layer
    clip = p.uid("rock")
    p.raw(f'<clipPath id="{clip}"><path clip-rule="evenodd" d="M{x0},{top} H{x1} V{bot} H{x0} Z '
          f'M{cx - cr},{top} A{cr},{cr} 0 0 0 {cx + cr},{top} Z"/></clipPath>')
    p.raw(f'<g clip-path="url(#{clip})">')
    y, i = bot, 0
    while y > top - 20:                           # thick/thin bands on a tidal rhythm
        h = 5 + 9 * (0.5 + 0.5 * math.sin(i * TAU / 7))
        p.raw(f'<rect x="{x0}" y="{y - h:.2f}" width="{x1 - x0}" height="{h:.2f}" '
              f'fill="{p.P["warm" if i % 2 == 0 else "cream"]}"/>')
        y -= h
        i += 1
    p.raw("</g>")
    # the block's outline and the crater's rim, in ink
    p.raw(f'<path d="M{x0},{top} H{cx - cr} A{cr},{cr} 0 0 0 {cx + cr},{top} H{x1} V{bot} H{x0} Z" '
          f'fill="none" stroke="{p.P["ink"]}" stroke-width="2.2"/>')
    # the incoming asteroid and its trail, aimed at the crater
    ax, ay = 252, 46
    for k, w in enumerate((5, 3.2, 1.8)):
        off = (k - 1) * 9
        p.line(ax + 14 + off * 0.4, ay - 12 + off, ax + 62 + off * 0.4, ay - 50 + off, w,
               "mustard" if p.mode == "colour" else "ink")
    p.circle(ax, ay, 12, "dark")
    p.line(ax - 16, ay + 16, cx + 10, top - 30, 1.6, extra=' stroke-dasharray="2 6"')


# ---------------------------------------------------------------- 6
def lesson6(p):
    """Space technology & sustainability: a satellite on its orbit, and the
    debris that crowds the orbit above it."""
    ex, ey, er = 40, 330, 150
    p.circle(ex, ey, er, "deep")
    p.ring(ex, ey, er + 9, p.P["cool"] if p.mode == "colour" else "#111", 5 if p.mode == "colour" else 1.2,
           '' if p.mode == "colour" else ' stroke-dasharray="3 4"')             # the thin atmosphere
    R1, R2 = 205, 250
    p.orbit(ex, ey, R1)
    p.orbit(ex, ey, R2)
    sx, sy = polar(ex, ey, R1, 52)
    on_circle(ex, ey, R1, sx, sy)
    ang = -(52 - 90)                               # panels lie along the orbit's tangent
    p.raw(f'<g transform="translate({sx:.2f} {sy:.2f}) rotate({ang:.2f})">')
    for side in (-1, 1):
        x = 13 if side > 0 else -45
        p.raw(f'<rect x="{x}" y="-9" width="32" height="18" fill="{p.P["cool"]}" '
              f'stroke="{p.P["ink"]}" stroke-width="1.6"/>')
        for k in (1, 2, 3):
            xx = x + 8 * k
            p.raw(f'<line x1="{xx}" y1="-9" x2="{xx}" y2="9" stroke="{p.P["ink"]}" stroke-width="1"/>')
    p.raw(f'<rect x="-11" y="-11" width="22" height="22" fill="{p.P["mustard"] if p.mode == "colour" else "#fff"}" '
          f'stroke="{p.P["ink"]}" stroke-width="2"/></g>')
    rnd = random.Random(6)                         # debris: small shards on the outer orbit
    for deg in (28, 36, 41, 58, 64, 71, 79):
        x, y = polar(ex, ey, R2, deg)
        on_circle(ex, ey, R2, x, y)
        s = rnd.uniform(3.5, 6.5)
        rot = rnd.uniform(0, 360)
        p.raw(f'<path transform="translate({x:.2f} {y:.2f}) rotate({rot:.1f})" '
              f'd="M{-s},{-s * 0.6} L{s},{-s * 0.2} L{-s * 0.2},{s} Z" fill="{p.P["warm"]}"'
              f'{p.edge("warm")}/>')


# ---------------------------------------------------------------- 7
def lesson7(p):
    """Aboriginal & Torres Strait Islander astronomy: the Milky Way over
    Country, with the dark dust lane that many peoples read as well as the
    stars. No specific figure is drawn (see the module docstring)."""
    sky = p.uid("sky")                             # a round sky, not a square tile
    p.raw(f'<clipPath id="{sky}"><circle cx="150" cy="150" r="146"/></clipPath>')
    p.raw(f'<g clip-path="url(#{sky})">')
    p.raw(f'<rect x="0" y="0" width="{W}" height="{H}" fill="{p.P["night"]}"/>')
    # the Milky Way: a band of stars from lower left to upper right
    rnd = random.Random(7)
    band = p.uid("band")
    p.raw(f'<clipPath id="{band}"><path d="M-40,250 L210,-40 L330,30 L80,320 Z"/></clipPath>')
    p.raw(f'<g clip-path="url(#{band})">')
    if p.mode == "colour":                         # the band's glow, so the dark lane reads
        p.raw('<path d="M-20,262 C60,170 150,90 230,-10 L300,40 C230,120 140,210 70,300 Z" '
              'fill="#2c5a86" opacity=".75"/>')
    star ="#f2d79a" if p.mode == "colour" else "#ffffff"
    for _ in range(520):
        t, u = rnd.random(), rnd.gauss(0, 0.33)
        x = -40 + 250 * t + 120 * (u + 0.5)
        y = 250 - 290 * t + 70 * (u + 0.5)
        p.raw(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rnd.uniform(0.6, 1.6):.2f}" fill="{star}" '
              f'opacity="{rnd.uniform(0.45, 1):.2f}"/>')
    p.raw("</g>")
    # the dark lane down the middle of the band
    lane = "M30,250 C70,205 95,190 112,150 C126,118 150,110 168,82 C180,62 196,50 214,22 " \
           "L226,30 C210,58 196,74 184,96 C166,126 146,136 132,166 C116,200 92,224 52,262 Z"
    p.path(lane, "night")
    # a few bright stars outside the band
    for x, y, r in [(72, 66, 2.6), (258, 150, 2.2), (232, 206, 1.8), (86, 120, 1.6), (240, 92, 1.8)]:
        p.circle(x, y, r, "pale")
    # Country: the land under the sky
    hills = "M0,246 C40,230 70,234 104,224 C140,214 170,228 206,220 C240,212 270,224 300,216 L300,300 L0,300 Z"
    p.path(hills, "warm")
    p.raw("</g>")
    if p.mode == "ink":
        p.ring(150, 150, 146, "#111", 2)


# ---------------------------------------------------------------- 5
def lesson5(p):
    """Our solar system: the Sun in the corner, circular orbits centred on
    it, planets of different sizes on their orbits."""
    sx, sy = 0, 300
    orbits = [(104, 70, 5, "cool"), (140, 55, 7, "cream"), (178, 34, 8, "cool"),
              (222, 63, 21, "warm"), (268, 26, 15, "mustard")]
    for R, *_ in orbits:
        p.orbit(sx, sy, R)
    p.circle(sx, sy, 70, "sun")
    for R, ang, pr, role in orbits:
        x, y = polar(sx, sy, R, ang)
        on_circle(sx, sy, R, x, y)
        if R == 268:
            p.raw(f'<ellipse cx="{x:.2f}" cy="{y:.2f}" rx="{pr * 1.9:.2f}" ry="{pr * 0.45:.2f}" '
                  f'transform="rotate(-18 {x:.2f} {y:.2f})" fill="none" stroke="{p.P["ink"]}" stroke-width="2.4"/>')
        p.circle(x, y, pr, role)
        if R == 222 and p.mode == "colour":
            cid = p.uid("bands")
            p.raw(f'<clipPath id="{cid}"><circle cx="{x:.2f}" cy="{y:.2f}" r="{pr}"/></clipPath>'
                  f'<g clip-path="url(#{cid})" fill="#f2d79a" opacity=".85">'
                  f'<rect x="{x - pr}" y="{y - 6}" width="{2 * pr}" height="4"/>'
                  f'<rect x="{x - pr}" y="{y + 4}" width="{2 * pr}" height="3"/></g>')
    if p.mode == "colour":
        p.ring(sx, sy, 70, "#efe6d2", 3)


# ---------------------------------------------------------------- 8
def lesson8(p):
    """The search for life: a star's habitable zone — the band of orbits
    where water could stay liquid — with one planet inside it, one too
    hot and one too cold."""
    sx, sy = -10, 150
    zone = annulus(sx, sy, 150, 205)
    p.path(zone, "cool", ' fill-rule="evenodd"')
    for R in (100, 175, 255):
        p.orbit(sx, sy, R)
    p.circle(sx, sy, 58, "sun")
    for R, deg, pr, role in [(100, 24, 8, "warm"), (175, -12, 13, "deep"), (255, 18, 10, "pale")]:
        x, y = polar(sx, sy, R, deg)
        on_circle(sx, sy, R, x, y)
        p.circle(x, y, pr, role, f' stroke="{p.P["ink"]}" stroke-width="2"' if role == "pale" and p.mode == "colour" else "")
    if p.mode == "colour":
        p.ring(sx, sy, 58, "#efe6d2", 3)


# ---------------------------------------------------------------- 9
def lesson9(p):
    """Gravity & orbits: Newton's cannonball. Fired from a mountain top,
    slow shots fall back to the ground; fast enough, the shot keeps
    falling round the planet — a circular orbit."""
    cx, cy, r = 150, 196, 78
    R = r + 26                                      # launch height = the orbit's radius
    p.orbit(cx, cy, R)
    p.circle(cx, cy, r, "deep")
    # the mountain, its peak exactly on the orbit
    peak = (cx, cy - R)
    on_circle(cx, cy, R, *peak)
    p.path(f"M{cx - 20},{cy - r + 4} L{peak[0]},{peak[1] + 2} L{cx + 20},{cy - r + 4} Z", "warm")
    # two shots that fall short: curves from the peak to the ground
    for land, bend in ((52, 0.55), (22, 0.75)):
        lx, ly = polar(cx, cy, r, land)
        c1x, c1y = peak[0] + (lx - peak[0]) * bend, peak[1] - 2
        p.raw(f'<path d="M{peak[0]:.2f},{peak[1]:.2f} Q{c1x:.2f},{c1y:.2f} {lx:.2f},{ly:.2f}" fill="none" '
              f'stroke="{p.P["ink"]}" stroke-width="2.2" stroke-dasharray="6 5"/>')
        p.circle(lx, ly, 4, "ink")
    # the shot in orbit
    bx, by = polar(cx, cy, R, -30)
    on_circle(cx, cy, R, bx, by)
    p.circle(bx, by, 9, "dark")
    # the cannon's direction: level, along the orbit
    p.line(peak[0] + 4, peak[1] - 1, peak[0] + 34, peak[1] - 1, 4, "ink")
    p.raw(f'<path d="M{peak[0] + 38},{peak[1] - 1} l-9,-6 v12 Z" fill="{p.P["ink"]}"/>')


# ---------------------------------------------------------------- 10
def lesson10(p):
    """Stars, galaxies & starlight: starlight through a prism spreads into a
    spectrum, and the dark lines in it tell us what the star is made of."""
    p.circle(30, 150, 46, "sun")
    p.raw(f'<path d="M66,140 L128,146 L128,154 L66,160 Z" fill="{p.P["pale"]}" '
          f'stroke="{p.P["ink"]}" stroke-width="1.2"/>')                      # the beam
    tri = (150, 92), (106, 206), (194, 206)
    # the fan of light from the prism to the spectrum
    p.raw(f'<path d="M168,152 L232,62 L232,238 Z" fill="{p.P["pale"]}" '
          f'stroke="{p.P["ink"]}" stroke-width="1.2" stroke-linejoin="round"/>')
    p.raw('<path d="M{},{} L{},{} L{},{} Z" fill="{}" stroke="{}" stroke-width="2.6" '
          'stroke-linejoin="round"/>'.format(*tri[0], *tri[1], *tri[2], p.P["pale"], p.P["ink"]))
    roles = ["warm", "mustard", "cream", "cool", "deep", "dark"]
    y = 62
    for role in roles:
        p.raw(f'<rect x="232" y="{y}" width="50" height="29.4" fill="{p.P[role]}"{p.edge(role)}/>')
        y += 29.4
    for ly in (84, 131, 170, 214):                 # absorption lines
        p.line(228, ly, 286, ly, 3.4 if p.mode == "colour" else 4.2,
               "ink" if p.mode == "colour" else "paper")
        if p.mode == "ink":
            p.line(228, ly, 286, ly, 1.6, "ink")


LESSONS = {1: lesson1, 2: lesson2, 3: lesson3, 4: lesson4, 5: lesson5,
           6: lesson6, 7: lesson7, 8: lesson8, 9: lesson9, 10: lesson10}


def render(n, mode, ground):
    p = Pic(mode, f"l{n}")
    LESSONS[n](p)
    return p.svg(ground=ground)


def main(argv):
    os.makedirs(SITE, exist_ok=True)
    os.makedirs(BOOK, exist_ok=True)
    rsvg = shutil.which("rsvg-convert")
    for n in LESSONS:
        with open(os.path.join(SITE, f"l{n}.svg"), "w", encoding="utf-8", newline="\n") as f:
            f.write(render(n, "colour", ground=False))
        ink = os.path.join(BOOK, f"l{n}-ink.svg")
        with open(ink, "w", encoding="utf-8", newline="\n") as f:
            f.write(render(n, "ink", ground=False))
        if rsvg:
            subprocess.run([rsvg, "-f", "pdf", ink, "-o", ink[:-4] + ".pdf"], check=True)
    print(f"wrote {len(LESSONS)} colour symbols to {os.path.relpath(SITE, ROOT)}"
          f" and {len(LESSONS)} ink symbols to {os.path.relpath(BOOK, ROOT)}"
          + ("" if rsvg else " (no rsvg-convert: ink PDFs not rebuilt)"))
    if "--sheet" in argv:
        from PIL import Image
        import tempfile
        tiles = []
        with tempfile.TemporaryDirectory() as tmp:
            for mode in ("colour", "ink"):
                for n in LESSONS:
                    svg = os.path.join(tmp, f"{n}-{mode}.svg")
                    with open(svg, "w") as f:
                        f.write(render(n, mode, ground=True))
                    png = svg[:-4] + ".png"
                    subprocess.run([rsvg, "-w", "240", svg, "-o", png], check=True)
                    tiles.append(Image.open(png).convert("RGB"))
        cols = len(LESSONS)
        sheet = Image.new("RGB", (cols * 250 + 10, 2 * 250 + 10), "#888")
        for i, t in enumerate(tiles):
            sheet.paste(t, (10 + (i % cols) * 250, 10 + (i // cols) * 250))
        out = (argv[argv.index("--sheet-out") + 1] if "--sheet-out" in argv
               else os.path.join(tempfile.gettempdir(), "space-symbols-sheet.png"))
        sheet.save(out)
        print(f"preview sheet: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
