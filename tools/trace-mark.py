#!/usr/bin/env python3
"""
trace-mark.py — flatten the assembled artwork into ONE outline.

    pip install potracer cairosvg pillow numpy
    python3 tools/trace-mark.py

Why this exists
---------------
assets/icons/mark-source.svg is *assembled*: the Illustrator export
(11 paths, carrying a translate) plus a hand-added connector bridging
the clef's broken stem. That connector is a separate overlapping object
— invisible only because every piece is the same opaque colour. Give
the mark any opacity or a stroke and the overlap shows as a seam.

This renders the source at 4x, traces the union back to bezier
outlines, and writes ONE continuous path with the connector baked in.
The trace is verified against the source by intersection-over-union
before anything is written — below 0.995 it aborts rather than
silently shipping a drifted mark.

Run this after ANY edit to mark-source.svg, then re-run
tools/build-icons.js. mark.svg is generated; don't hand-edit it.

Outputs (all in assets/icons/):
    mark.svg               single unified outline — source for the icon set
    logo-large.svg         mark on a rounded board tile
    logo-large-chalk.svg   chalk mark alone, for dark backgrounds
    logo-large-ink.svg     board-coloured mark alone, for light/print

Note on potracer: it treats ZERO as foreground, so the bitmap is
inverted before tracing. Passing it the obvious way round silently
traces the background instead, producing a filled square with the mark
knocked out of it.
"""
import io
import os
import re
import sys

import cairosvg
import numpy as np
import potrace
from PIL import Image

ICONS = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets', 'icons')
BOARD, CHALK = '#24576f', '#f6f4ef'
SUPERSAMPLE = 4
MIN_IOU = 0.995

src_path = os.path.join(ICONS, 'mark-source.svg')
src = open(src_path, encoding='utf-8').read()
VB = int(re.search(r'viewBox="0 0 (\d+)', src).group(1))
R = VB * SUPERSAMPLE


def rasterise(svg_text, n):
    """Render SVG text to a boolean ink mask at n x n."""
    tmp = os.path.join(ICONS, '_trace_tmp.svg')
    open(tmp, 'w', encoding='utf-8').write(svg_text.replace('currentColor', '#000000'))
    try:
        png = cairosvg.svg2png(url=tmp, output_width=n, output_height=n,
                               background_color='white')
    finally:
        os.remove(tmp)
    return np.array(Image.open(io.BytesIO(png)).convert('L')) < 128


def trace(ink, alphamax=1.0, opttolerance=0.2, turdsize=8):
    # alphamax 1.0 is potrace's own default corner threshold. Pushing it to
    # 1.34 with opttolerance 0.4 saves ~2 KB but drops IoU to 0.9954, which
    # sits on the acceptance threshold below — not worth the margin.
    # potracer's foreground is the ZERO value — invert.
    path = potrace.Bitmap(~ink).trace(turdsize=turdsize, alphamax=alphamax,
                                      opttolerance=opttolerance)
    s = VB / R
    f = lambda v: round(v * s, 2)
    parts = []
    for curve in path:
        st = curve.start_point
        d = 'M%s,%s' % (f(st.x), f(st.y))
        for seg in curve:
            if seg.is_corner:
                d += 'L%s,%s L%s,%s' % (f(seg.c.x), f(seg.c.y),
                                        f(seg.end_point.x), f(seg.end_point.y))
            else:
                d += 'C%s,%s %s,%s %s,%s' % (f(seg.c1.x), f(seg.c1.y),
                                             f(seg.c2.x), f(seg.c2.y),
                                             f(seg.end_point.x), f(seg.end_point.y))
        parts.append(d + 'Z')
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d">\n' % (VB, VB)
            + '<path fill-rule="evenodd" fill="currentColor" d="%s"/>\n</svg>\n'
            % ''.join(parts))


print('rendering mark.svg at %dpx…' % R)
smooth = trace(rasterise(src, R))

a, b = rasterise(src, 512), rasterise(smooth, 512)
iou = (a & b).sum() / (a | b).sum()
print('fidelity vs source: IoU %.4f' % iou)
if iou < MIN_IOU:
    sys.exit('trace drifted from the source (IoU %.4f < %.3f) — not written' % (iou, MIN_IOU))

inner = re.sub(r'^[\s\S]*?<svg[^>]*>', '', smooth).replace('</svg>', '').strip()
files = {
    'mark.svg': smooth,
    'logo-large.svg': ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d">' % (VB, VB)
                       + '<rect width="%d" height="%d" rx="%.1f" fill="%s"/>' % (VB, VB, VB * 0.22, BOARD)
                       + inner.replace('currentColor', CHALK) + '</svg>\n'),
    'logo-large-chalk.svg': smooth.replace('currentColor', CHALK),
    'logo-large-ink.svg': smooth.replace('currentColor', BOARD),
}
for name, text in files.items():
    open(os.path.join(ICONS, name), 'w', encoding='utf-8').write(text)
    print('wrote assets/icons/%-22s %5.1f KB' % (name, len(text) / 1024))

for name, bg in (('logo-large', None), ('logo-large-chalk', None), ('logo-large-ink', None)):
    out = os.path.join(ICONS, name + '-2048.png')
    cairosvg.svg2png(url=os.path.join(ICONS, name + '.svg'), write_to=out,
                     output_width=2048, output_height=2048)
    print('wrote assets/icons/%s-2048.png' % name)
