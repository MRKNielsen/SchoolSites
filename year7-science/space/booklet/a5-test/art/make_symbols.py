"""Giusti-style lesson symbols for Year 7 Space — one diagrammatic idea each.

Writes, for every lesson, a colour SVG (site, decks) and an ink SVG (black
and white booklet). Both come from the same geometry: each shape is drawn
with a ROLE, and the role maps to a flat colour (with a soft airbrush
gradient on the light sources) or to a black-and-white ink treatment
(solid, hatch, stipple, or white with an outline).

    python3 make_symbols.py           -> l1-colour.svg, l1-ink.svg, ...
"""
import math
import os

OUT = os.path.dirname(os.path.abspath(__file__))
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
    def __init__(self, mode):
        self.mode, self.P, self.out = mode, (COLOUR if mode == "colour" else INK), []

    def edge(self, role):
        # In ink every filled shape gets an outline, so hatch has a boundary.
        if self.mode == "ink" and role not in ("ink", "paper"):
            return ' stroke="#111" stroke-width="1.8"'
        return ""

    def circle(self, cx, cy, r, role, extra=""):
        self.out.append(f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r:.2f}" fill="{self.P[role]}"{self.edge(role)}{extra}/>')

    def ring(self, cx, cy, r, colour, w):
        self.out.append(f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r:.2f}" fill="none" stroke="{colour}" stroke-width="{w}"/>')

    def path(self, d, role, extra=""):
        self.out.append(f'<path d="{d}" fill="{self.P[role]}"{self.edge(role)}{extra}/>')

    def line(self, x1, y1, x2, y2, w=2, role="ink", extra=""):
        self.out.append(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" '
                        f'stroke="{self.P[role]}" stroke-width="{w}" stroke-linecap="round"{extra}/>')

    def raw(self, s):
        self.out.append(s)

    def svg(self):
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}">\n{defs(self.mode)}\n'
                f'<rect width="{W}" height="{H}" fill="{self.P["paper"]}"/>\n'
                + "\n".join(self.out) + "\n</svg>\n")


def sector(cx, cy, r, a0, a1):
    """Pie slice from angle a0 to a1 (degrees, 0 = east, counter-clockwise on screen)."""
    x0, y0 = cx + r * math.cos(math.radians(a0)), cy - r * math.sin(math.radians(a0))
    x1, y1 = cx + r * math.cos(math.radians(a1)), cy - r * math.sin(math.radians(a1))
    large = 1 if (a1 - a0) % 360 > 180 else 0
    return f"M{cx:.2f},{cy:.2f} L{x0:.2f},{y0:.2f} A{r},{r} 0 {large} 0 {x1:.2f},{y1:.2f} Z"


def lit_part(cx, cy, r, k):
    """Lit region of a Moon disc, lit fraction k in (0,1), lit on the LEFT
    (waxing as seen from the southern hemisphere — Melbourne)."""
    top, bot = (cx, cy - r), (cx, cy + r)
    d = f"M{top[0]:.2f},{top[1]:.2f} A{r},{r} 0 0 0 {bot[0]:.2f},{bot[1]:.2f} "
    rx = r * abs(1 - 2 * k)
    if abs(k - 0.5) < 1e-9:
        return d + "Z"
    sweep = 1 if k < 0.5 else 0          # crescent: terminator bulges left
    return d + f"A{rx:.2f},{r} 0 0 {sweep} {top[0]:.2f},{top[1]:.2f} Z"


# ---------------------------------------------------------------- Lesson 1
def lesson1(mode):
    """Scale & structure: the Sun is too big to fit; Earth, cut open, shows
    its layers; the Moon is a quarter of Earth's width."""
    p = Pic(mode)
    p.circle(372, 96, 170, "sun")                        # the Sun runs off the page
    ex, ey, er = 112, 188, 64
    p.circle(ex, ey, er, "deep")                          # Earth, crust/surface
    # cut-away quarter showing the layers (mantle, outer core, inner core)
    p.path(sector(ex, ey, er * 0.86, 0, 90), "warm")
    p.path(sector(ex, ey, er * 0.55, 0, 90), "mustard" if mode == "colour" else "cool")
    p.path(sector(ex, ey, er * 0.27, 0, 90), "cream")
    mr = er * 0.27                                        # Moon = 0.27 x Earth
    mx, my = 226, 252
    p.circle(mx, my, mr, "pale", ' stroke="%s" stroke-width="2"' % p.P["ink"] if mode == "colour" else "")
    # a measured line from Earth to Moon: the diagram's one hard fact
    p.line(ex + er + 10, ey + 34, mx - mr - 8, my - 6, 1.6, extra=' stroke-dasharray="2 5"')
    return p.svg()


# ---------------------------------------------------------------- Lesson 2
def lesson2(mode):
    """Day, night & seasons: parallel sunlight, the lit half, the tilted axis."""
    p = Pic(mode)
    for i, y in enumerate([92, 122, 152, 182, 212]):    # parallel rays from the left
        p.line(18, y, 78 + (i % 2) * 14, y, 6, "mustard" if mode == "colour" else "ink")
    cx, cy, r = 186, 152, 86
    p.circle(cx, cy, r, "dark")                          # night side
    p.path(f"M{cx},{cy - r} A{r},{r} 0 0 0 {cx},{cy + r} Z", "lit")   # day side faces the Sun
    if mode == "ink":
        p.ring(cx, cy, r, "#111", 2)
    tilt = math.radians(23.5)                            # axis, 23.5 degrees from upright
    dx, dy = math.sin(tilt), -math.cos(tilt)
    a, b = r + 30, r + 30
    eqc = "cool" if mode == "colour" else "ink"
    # equator: perpendicular to the axis, across the disc
    p.line(cx - r * math.cos(tilt) * 0.98, cy - r * math.sin(tilt) * 0.98,
           cx + r * math.cos(tilt) * 0.98, cy + r * math.sin(tilt) * 0.98, 2.5, eqc,
           ' stroke-dasharray="7 5"')
    # the axis carries a paper-coloured edge so it still reads over the night side
    p.line(cx - a * dx, cy - a * dy, cx + b * dx, cy + b * dy, 8, "paper")
    p.line(cx - a * dx, cy - a * dy, cx + b * dx, cy + b * dy, 3.5, "ink")
    p.circle(cx + b * dx, cy + b * dy, 5, "ink")       # south pole end (towards the viewer's south)
    p.circle(cx - a * dx, cy - a * dy, 5, "paper", f' stroke="{p.P["ink"]}" stroke-width="3"')
    return p.svg()


# ---------------------------------------------------------------- Lesson 3
def lesson3(mode):
    """Phases & tides: the lit part grows from the left (southern sky), and
    the sea rises and falls in step."""
    p = Pic(mode)
    r = 27
    for x, k in zip([48, 116, 184, 252], [0.22, 0.5, 0.78, 1.0]):
        p.circle(x, 96, r, "dark")
        if k >= 1:
            p.circle(x, 96, r, "lit")
        else:
            p.path(lit_part(x, 96, r, k), "lit")
        if mode == "ink":
            p.ring(x, 96, r, "#111", 2)
    # tides: three bands of sea, a high and a low swell
    for i, (y0, amp, role) in enumerate([(176, 16, "cool"), (212, 12, "deep"), (246, 8, "dark")]):
        pts = []
        for j in range(0, 61):
            x = j * 5
            pts.append(f"{x:.1f},{y0 + amp * math.sin(x / 300 * TAU * 1.0 + i * 0.6):.1f}")
        p.path("M0,300 L" + " L".join(pts) + " L300,300 Z", role)
    return p.svg()


# ---------------------------------------------------------------- Lesson 5
def lesson5(mode):
    """Our solar system: the Sun in the corner, circular orbits centred on it
    (see CLAUDE.md: never an ellipse with the Sun in the middle), planets of
    different sizes on their orbits."""
    p = Pic(mode)
    sx, sy = 0, 300
    orbits = [(104, 70, 5, "cool"), (140, 55, 7, "cream"), (178, 34, 8, "cool"),
              (222, 63, 21, "warm"), (268, 26, 15, "mustard")]
    for R, *_ in orbits:
        p.raw(f'<circle cx="{sx}" cy="{sy}" r="{R}" fill="none" stroke="{p.P["ink"]}" '
              f'stroke-width="1.4" stroke-dasharray="1 5" stroke-linecap="round"/>')
    p.circle(sx, sy, 70, "sun")
    for R, ang, pr, role in orbits:
        x, y = sx + R * math.cos(math.radians(ang)), sy - R * math.sin(math.radians(ang))
        assert abs(math.hypot(x - sx, y - sy) - R) < 1e-6      # on its orbit, exactly
        if R == 268:                                          # a ringed planet
            p.raw(f'<ellipse cx="{x:.2f}" cy="{y:.2f}" rx="{pr * 1.9:.2f}" ry="{pr * 0.45:.2f}" '
                  f'transform="rotate(-18 {x:.2f} {y:.2f})" fill="none" stroke="{p.P["ink"]}" stroke-width="2.4"/>')
        p.circle(x, y, pr, role)
        if R == 222 and mode == "colour":                     # banded giant
            p.raw(f'<clipPath id="jb"><circle cx="{x:.2f}" cy="{y:.2f}" r="{pr}"/></clipPath>'
                  f'<g clip-path="url(#jb)" fill="#f2d79a" opacity=".85">'
                  f'<rect x="{x - pr}" y="{y - 6}" width="{2 * pr}" height="4"/>'
                  f'<rect x="{x - pr}" y="{y + 4}" width="{2 * pr}" height="3"/></g>')
    if mode == "colour":
        p.ring(sx, sy, 70, "#efe6d2", 3)
    return p.svg()


LESSONS = {"l1": lesson1, "l2": lesson2, "l3": lesson3, "l5": lesson5}

if __name__ == "__main__":
    for key, fn in LESSONS.items():
        for mode in ("colour", "ink"):
            with open(os.path.join(OUT, f"{key}-{mode}.svg"), "w") as f:
                f.write(fn(mode))
    print("wrote", 2 * len(LESSONS), "SVGs to", OUT)
