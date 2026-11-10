"""Shared helpers for the Year 7 lesson-symbol generators.

Each unit's generator (tools/<unit>_symbols.py) draws its lessons with the
Pic kit from tools/space_symbols.py and calls write_all() to produce the
colour SVGs for the site and the ink SVG + PDF for the booklet.
"""
import math
import os
import re
import shutil
import subprocess
import tempfile

from space_symbols import Pic, W, H  # noqa: F401  (re-exported)


def ink(p):
    return p.P["ink"]


def rect(p, x, y, w, h, role, extra=""):
    p.raw(f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" fill="{p.P[role]}"{p.edge(role)}{extra}/>')


def poly(p, pts, role, extra=""):
    p.path("M" + " L".join(f"{x:.2f},{y:.2f}" for x, y in pts) + " Z", role, extra)


def stroke(p, d, w=2.4, dash=None, colour=None):
    da = f' stroke-dasharray="{dash}"' if dash else ""
    p.raw(f'<path d="{d}" fill="none" stroke="{colour or ink(p)}" stroke-width="{w}" '
          f'stroke-linecap="round" stroke-linejoin="round"{da}/>')


def arrow(p, x1, y1, x2, y2, w=4, head=13, role="ink"):
    a = math.atan2(y2 - y1, x2 - x1)
    bx, by = x2 - head * math.cos(a), y2 - head * math.sin(a)
    p.line(x1, y1, bx, by, w, role)
    l = (bx + head * 0.6 * math.sin(a), by - head * 0.6 * math.cos(a))
    r = (bx - head * 0.6 * math.sin(a), by + head * 0.6 * math.cos(a))
    p.raw(f'<path d="M{x2:.2f},{y2:.2f} L{l[0]:.2f},{l[1]:.2f} L{r[0]:.2f},{r[1]:.2f} Z" fill="{p.P[role]}"/>')


def ground(p, y, x0=12, x1=288):
    p.line(x0, y, x1, y, 4, "ink")


_TAG = re.compile(r"<([a-zA-Z]+)((?:\s+[a-zA-Z:-]+=\"[^\"]*\")+)\s*(/?)>")
_ATTR = re.compile(r'\s+([a-zA-Z:-]+)="([^"]*)"')


def dedupe(svg):
    """A shape may be given an outline by both Pic.edge() and its caller;
    keep the caller's (the later one), so every tag is valid XML."""
    def fix(m):
        attrs = {}
        for k, v in _ATTR.findall(m.group(2)):
            attrs.pop(k, None)
            attrs[k] = v
        return "<" + m.group(1) + "".join(f' {k}="{v}"' for k, v in attrs.items()) + (" /" if m.group(3) else "") + ">"
    return _TAG.sub(fix, svg)


def write_all(lessons, key, site_dir, book_dir, argv):
    os.makedirs(site_dir, exist_ok=True)
    os.makedirs(book_dir, exist_ok=True)
    rsvg = shutil.which("rsvg-convert")

    def render(n, mode, ground_):
        p = Pic(mode, f"{key}{n}")
        lessons[n](p)
        return dedupe(p.svg(ground=ground_))

    for n in lessons:
        with open(os.path.join(site_dir, f"l{n}.svg"), "w", encoding="utf-8", newline="\n") as f:
            f.write(render(n, "colour", False))
        inkf = os.path.join(book_dir, f"l{n}-ink.svg")
        with open(inkf, "w", encoding="utf-8", newline="\n") as f:
            f.write(render(n, "ink", False))
        if rsvg:
            subprocess.run([rsvg, "-f", "pdf", inkf, "-o", inkf[:-4] + ".pdf"], check=True)
    print(f"wrote {len(lessons)} colour + ink symbols" + ("" if rsvg else " (no rsvg-convert: ink PDFs not rebuilt)"))
    if "--sheet" in argv:
        from PIL import Image
        tiles = []
        with tempfile.TemporaryDirectory() as tmp:
            for mode in ("colour", "ink"):
                for n in lessons:
                    svg = os.path.join(tmp, f"{n}-{mode}.svg")
                    open(svg, "w").write(render(n, mode, True))
                    subprocess.run([rsvg, "-w", "180", svg, "-o", svg[:-4] + ".png"], check=True)
                    tiles.append(Image.open(svg[:-4] + ".png").convert("RGB"))
        cols = 9
        rows = math.ceil(len(tiles) / cols)
        sheet = Image.new("RGB", (cols * 190 + 10, rows * 190 + 10), "#888")
        for i, t in enumerate(tiles):
            sheet.paste(t, (10 + (i % cols) * 190, 10 + (i // cols) * 190))
        out = argv[argv.index("--sheet-out") + 1] if "--sheet-out" in argv else os.path.join(tempfile.gettempdir(), f"{key}-sheet.png")
        sheet.save(out)
        print("preview sheet:", out)
