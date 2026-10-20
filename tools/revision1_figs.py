#!/usr/bin/env python3
"""Lift the revision deck's figures for the printable worksheet.

The worksheet asks about the same diagrams the deck shows, so they come out
of revision1.html rather than being redrawn — one source, and they cannot
drift apart. worksheet.css wants print-safe figures: greyscale fills so a
black-and-white printer still shows the contrast, and ink in currentColor
(the .ws-fig wrapper sets that to --ink).
"""
import os, re, sys

DECK = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    'year7-science', 'space', 'revision1.html')

# illustrative hues -> greys that still separate on a mono printer
GREY = {
    '#f59e5b': '#bdbdbd',  # Sun
    '#f2e7c4': '#ffffff',  # lit Moon
    '#3a4a54': '#4a4a4a',  # unlit Moon
    '#5fa8d3': '#9a9a9a',  # Earth, lit half
    '#8ec5e0': '#c8c8c8',
    '#9fd0e6': '#d4d4d4',
    '#7fa7d9': '#b0b0b0',
    '#5d7a8a': '#6e6e6e',
    '#c9d6dc': '#dcdcdc',
    '#d9b38c': '#c4c4c4',
    '#3e5a6a': '#555555',
    '#f4f1e8': '#ffffff',
}


def greyscale(svg):
    def r(m):
        attr, hx = m.group(1), m.group(2).lower()
        return f'{attr}="{GREY.get(hx, hx)}"'
    svg = re.sub(r'(fill|stroke)="(#[0-9A-Fa-f]{6})"', r, svg)
    # tokens resolve to theme colours; on paper they must be ink
    svg = re.sub(r'style="fill:var\(--[a-z-]+\)"', 'fill="currentColor"', svg)
    svg = re.sub(r'style="stroke:var\(--[a-z-]+\)"', 'stroke="currentColor"', svg)

    # Figure labels were coloured for a dark slide — several are near-white,
    # which disappears on paper, and one is the Sun's orange. Every label
    # becomes ink with a white halo behind it (paint-order draws the stroke
    # first), so it reads whether it sits on blank paper or on a dark fill.
    def ink(m):
        tag = m.group(0)
        tag = re.sub(r'\s(?:fill|style)="[^"]*"', '', tag)
        return tag[:-1] + (' fill="currentColor" stroke="#fff" stroke-width="3"'
                           ' paint-order="stroke" stroke-linejoin="round">')
    svg = re.sub(r'<text[^>]*>', ink, svg)
    return svg


def figures():
    t = open(DECK, encoding='utf-8').read()
    secs = re.findall(r'<section class="slide.*?</section>', t, re.S)
    out = {}
    want = {'daynight': 8, 'orbit4': 10, 'moon6': 13, 'tides': 15}
    for name, n in want.items():
        svgs = re.findall(r'<svg.*?</svg>', secs[n - 1], flags=re.S)
        if not svgs:
            print(f'  !! no svg on slide {n} for {name}', file=sys.stderr)
            continue
        out[name] = [greyscale(s) for s in svgs]
        print(f'  {name:9s} slide {n:2d}: {len(svgs)} figure(s)')
    return out


if __name__ == '__main__':
    f = figures()
    import json
    json.dump({k: v for k, v in f.items()},
              open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'revision1_figs.json'),
                   'w', encoding='utf-8'), ensure_ascii=False)
    print('wrote figs.json')
