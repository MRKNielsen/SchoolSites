#!/usr/bin/env python3
"""Port the CAT revision deck onto the shared design system.

Source: a slide export with 26 sections, 688 inline style= attributes, 53
hardcoded hexes and its own 1920x1080 scaling script. Only `.slide` is a
class, so this maps by the *role* the inline style encodes.

deck.css already handles vertical centring, overflow, the type scale and
print, so most of the work is deleting styling rather than translating it.
The care goes into three places: which card becomes which `.box` variant,
the 24 inline SVGs (theme hexes -> tokens, illustrative hues left alone),
and not losing text. The run fails if any visible string from the source is
missing from the output.
"""
import html, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = '/sessions/vibrant-wizardly-cannon/mnt/uploads/Space_CAT_Revision_Lesson 1.html'
DST = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'year7-science', 'space', 'revision1.html')

# theme colours -> tokens; illustrative hues stay literal (CLAUDE.md)
TOKEN = {
    '#13232e': 'var(--accent-dark)', '#1b2a33': 'var(--ink)',
    '#1f3a4d': 'var(--accent-dark)', '#24576f': 'var(--accent)',
    '#2e4757': 'var(--accent-dark)', '#33434d': 'var(--ink)',
    '#35505f': 'var(--accent-dark)', '#3a4a54': 'var(--ink-soft)',
    '#0f1d26': 'var(--accent-dark)', '#0b141a': 'var(--accent-dark)',
    '#26343c': 'var(--ink)', '#c2410c': 'var(--accent-warm)',
    '#f7f5ef': 'var(--card)', '#fffdf8': 'var(--card)',
    '#f7fafa': 'var(--card)', '#e7eef0': 'var(--card)',
}
KEEP = {'#dce6f5', '#2e3350', '#f4f1e8', '#ffffff', '#fff', '#eef3f5'}


def svg_tokens(s):
    def r(m):
        attr, hx = m.group(1), m.group(2).lower()
        if hx in KEEP or hx not in TOKEN:
            return m.group(0)
        return f'style="{attr}:{TOKEN[hx]}"'
    s = re.sub(r'(fill|stroke)="(#[0-9A-Fa-f]{3,6})"', r, s)
    # the export positions some figures absolutely; deck.css lays them out
    s = re.sub(r'\sstyle="position:absolute[^"]*"', '', s)
    # every figure carries a viewBox, so drop the 1920-canvas pixel sizes and
    # let .graph-card scale them — a fixed height on a slide clips under the
    # overflow fade instead of shrinking
    s = re.sub(r'\s(width|height)="\d+"', '', s)
    s = re.sub(r'\sstyle="(?:width|height):[^"]*"', '', s)
    return s



LABEL = re.compile(
    r'<p style="position:absolute;left:(-?\d+)px;top:(-?\d+)px;width:(\d+)px;'
    r'font-size:(\d+)px;([^"]*)">(.*?)</p>', re.S)


def inline_labels(body):
    """Move figure labels into their SVG as <text>.

    The export overlays labels on a figure with position:absolute, in the
    1920-canvas coordinate space. Stripping that positioning (as the rest of
    this port does) drops them out of the picture and stacks them underneath
    it as loose sentences. The container is width:Wpx;height:Hpx and the
    figure's viewBox is "0 0 W H", so the pixel coordinates are already SVG
    user units and transfer straight across — which also makes them scale
    with the figure instead of needing a positioned wrapper.
    """
    def fix(m):
        box, inner = m.group(0), m.group(2)
        w, h = m.group(1).split('x')
        svg = re.search(r'<svg[^>]*viewBox="0 0 ' + w + r' ' + h + r'"[^>]*>', inner)
        if not svg:
            return box
        texts = []
        for lb in LABEL.finditer(inner):
            left, top, wid, fs = (int(lb.group(i)) for i in (1, 2, 3, 4))
            rest, txt = lb.group(5), re.sub(r'<[^>]+>', '', lb.group(6)).strip()
            align = (re.search(r'text-align:(\w+)', rest) or [None, 'left'])[1]
            col = (re.search(r'color:(#[0-9A-Fa-f]{6})', rest) or [None, ''])[1].lower()
            x = left + wid // 2 if align == 'center' else (left + wid if align == 'right' else left)
            anchor = {'center': 'middle', 'right': 'end'}.get(align, 'start')
            fill = TOKEN.get(col, col or 'var(--ink)')
            if col in KEEP:
                fill = col
            texts.append(f'<text x="{x}" y="{top + int(fs * 0.8)}" text-anchor="{anchor}" '
                         f'font-size="{fs}" font-weight="700" style="fill:{fill}">{txt}</text>')
        if not texts:
            return box
        inner = LABEL.sub('', inner)
        inner = inner.replace('</svg>', '\n' + '\n'.join(texts) + '\n</svg>', 1)
        return inner
    return re.sub(
        r'<div style="position:relative;width:(\d+)px;height:(\d+)px">(.*?)</div>',
        lambda m: fix(type('M', (), {
            'group': lambda s, i: (f'{m.group(1)}x{m.group(2)}' if i == 1
                                   else m.group(3) if i == 2 else m.group(0))})()),
        body, flags=re.S)


def vis(frag):
    frag = re.sub(r'<svg.*?</svg>', ' ', frag, flags=re.S)
    frag = re.sub(r'<[^>]+>', ' ', frag)
    return re.sub(r'\s+', ' ', html.unescape(frag)).strip()


def strip_styles(frag):
    return re.sub(r'\sstyle="[^"]*"', '', frag)


def convert(tag, body, n, total):
    """One section -> design-system slide."""
    bg = (re.search(r'background:(#[0-9A-Fa-f]{6})', tag) or [None, ''])[1].lower()
    notes = re.search(r'data-notes="(.*?)"\s+class=', tag, re.S)
    sid = (re.search(r'id="([^"]+)"', tag) or [None, f's{n}'])[1]

    # the source body already ends with its own </section>; the writer below
    # adds one, and two closers per slide collapse <main> and flatten the deck
    body = re.sub(r'</section>\s*$', '', body)

    body = inline_labels(body)

    svgs = re.findall(r'<svg.*?</svg>', body, flags=re.S)
    holder = body
    for i, s in enumerate(svgs):
        holder = holder.replace(s, f'@@SVG{i}@@', 1)

    kick = re.search(r'<p[^>]*text-transform:uppercase[^>]*>(.*?)</p>', holder, re.S)
    head = re.search(r'<h([12])[^>]*>(.*?)</h\1>', holder, re.S)
    kicker = vis(kick.group(1)) if kick else ''
    heading = vis(head.group(2)) if head else ''

    rest = holder
    if kick:
        rest = rest.replace(kick.group(0), '', 1)
    if head:
        rest = rest.replace(head.group(0), '', 1)

    # trailing paragraph: a booklet reference, or a closing instruction
    foot = ''
    tail = list(re.finditer(r'<p[^>]*>((?:(?!</p>).)*)</p>\s*$', rest, re.S))
    if tail:
        txt = vis(tail[-1].group(1))
        cls = 'bookref book' if txt.lower().startswith('booklet') else 'note'
        foot = f'<p class="{cls}">{tail[-1].group(1).strip()}</p>'
        rest = rest[:tail[-1].start()] + rest[tail[-1].end():]

    # structural mapping
    rest = re.sub(r'<div[^>]*grid-template-columns:1fr 1fr[^>]*>',
                  '<div class="cols even">', rest)
    rest = re.sub(r'<table[^>]*>', '<table class="tbl">', rest)
    # cards: a div with its own background becomes a box
    # a card whose first child is just a number is a numbered working card
    rest = re.sub(
        r'<div[^>]*background:#(?:FFFDF8|fffdf8)[^>]*>\s*<p[^>]*>(\d+)</p>\s*<p[^>]*>',
        lambda m: f'<div class="step"><span class="n">{m.group(1)}</span><p>', rest)
    rest = re.sub(r'<div[^>]*background:#(?:FFFDF8|fffdf8)[^>]*>', '<div class="box">', rest)
    rest = re.sub(r'<div[^>]*background:#(?:F7FAFA|f7fafa)[^>]*>', '<div class="box key">', rest)
    rest = re.sub(r'<p[^>]*background:#(?:EEF3F5|eef3f5)[^>]*>', '<p class="result">', rest)
    # figure wrappers carry the same canvas sizes
    rest = re.sub(r'\sstyle="(?:width|height):\d+px;?(?:(?:width|height):\d+px;?)*"', '', rest)
    rest = strip_styles(rest)
    rest = re.sub(r'<div>\s*</div>', '', rest)
    rest = re.sub(r'\n{3,}', '\n\n', rest).strip()

    for i, s in enumerate(svgs):
        rest = rest.replace(f'@@SVG{i}@@',
                            '<div class="graph-card">' + svg_tokens(s) + '</div>')

    # slide variant
    cls = 'slide'
    if bg == '#13232e':
        cls += ' title-slide' if n == 1 else ' exit-slide'
    if n == 1:
        cls += ' active'

    menu = heading or kicker or sid
    h = [f'  <section class="{cls}" data-menu="{html.escape(menu[:48], quote=True)}">']
    if foot.startswith('<p class="bookref'):
        h.append('    ' + foot)
        foot = ''
    if kicker:
        h.append(f'    <p class="eyebrow">{kicker}</p>')
    if heading:
        h.append(f'    <h{1 if n == 1 else 2}>{heading}</h{1 if n == 1 else 2}>')
    if rest:
        h.append('    ' + rest.replace('\n', '\n    '))
    if foot:
        h.append('    ' + foot)
    if notes:
        txt = html.unescape(notes.group(1))
        h.append('    <details class="teacher"><summary>Teacher notes</summary>')
        h.append(f'      <div class="inner-d"><p>{html.escape(txt)}</p></div></details>')
    h.append('  </section>')
    return '\n'.join(h)


def main():
    src = open(SRC, encoding='utf-8', errors='replace').read()
    spans = [(m.start(), m.end()) for m in re.finditer(r'<section[^>]*>', src)]
    secs = []
    for i, (a, b) in enumerate(spans):
        end = spans[i + 1][0] if i + 1 < len(spans) else src.rindex('</section>')
        secs.append((src[a:b], src[b:end]))

    slides = [convert(t, b, i + 1, len(secs)) for i, (t, b) in enumerate(secs)]
    slides[0] = COVER                      # the cover is hand-authored, above
    page = PAGE_HEAD + '\n\n'.join(slides) + PAGE_FOOT
    open(DST, 'w', encoding='utf-8', newline='').write(page)
    print(f'wrote {DST}\n  {len(secs)} slides, {len(page):,} chars')

    # ---- nothing lost -------------------------------------------------
    missing = []
    for i, (t, b) in enumerate(secs):
        if i == 0:
            continue   # the cover is hand-authored above, deliberately reworded
        for chunk in re.findall(r'>([^<>]{6,})<', b):
            s = html.unescape(chunk).strip()
            if s and s not in page and html.escape(s) not in page:
                missing.append((i + 1, s[:70]))
    print(f'  text check: {len(missing)} missing fragment(s)')
    for n, s in missing[:12]:
        print(f'    slide {n}: {s!r}')
    if missing:
        sys.exit(1)

    left = re.findall(r'style="(?!fill:|stroke:)[^"]*"', page)
    print(f'  inline style= left: {len(left)}')
    hexes = set(h.lower() for h in re.findall(r'#[0-9A-Fa-f]{6}', page))
    print(f'  hex colours left: {len(hexes)} (illustrative only if small)')
    print('   ', sorted(hexes)[:14])



COVER = """  <section class="slide title-slide active" data-menu="Title">
    <p class="eyebrow">Year 7 Science <b>&#183;</b> Space <b>&#183;</b> Revision 1 of 2</p>
    <h1>Ready for the CAT</h1>
    <p class="subtitle">A 50-minute revision lesson. Every skill the test checks, practised with brand-new questions.</p>
    <div class="head-meta">
      <span class="pill">50 minutes</span>
      <span class="pill">Booklet &#167;1&#8211;3, &#167;5&#8211;7</span>
      <span class="pill">Answers follow each task</span>
    </div>
    <p class="start-hint">Press <span class="key">&#8594;</span> to begin.</p>
  </section>"""

PAGE_HEAD = '''<!DOCTYPE html>
<html lang="en-AU">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Revision 1 &#8212; Ready for the CAT | Space</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Bitter:wght@500;700;800&family=Source+Sans+3:ital,wght@0,400;0,600;0,700;1,400&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../../assets/css/tokens.css">
<link rel="stylesheet" href="../../assets/css/deck.css">
<link rel="stylesheet" href="../../assets/css/sitenav.css">
<script src="../../assets/js/deck.js" defer></script>
<script src="../../assets/js/sitenav.js" defer></script>
<link rel="icon" href="../../assets/icons/favicon.svg" type="image/svg+xml">
<link rel="icon" href="../../assets/icons/favicon.ico" sizes="32x32">
<link rel="apple-touch-icon" href="../../assets/icons/apple-touch-icon.png">
<link rel="manifest" href="../../site.webmanifest">
<meta name="theme-color" content="#24576f">
</head>
<body class="deck-page theme-space">

<div class="progress"></div>
<div class="lessontag">Revision 1 &#183; Ready for the CAT</div>
<a class="homebtn" href="index.html" title="Back to the unit">&#8962;</a>

<main class="deck">

'''

PAGE_FOOT = '''

</main>

<div class="keyhint"><span class="key">&#8594;</span> reveals then advances &#183; <span class="key">&#8592;</span> back &#183; <span class="key">R</span> reveal &#183; <span class="key">M</span> menu</div>
<div class="chrome">
  <button class="navbtn" data-nav="prev">&#8592;</button>
  <span class="counter">1 / 26</span>
  <button class="navbtn" data-nav="next">&#8594;</button>
  <button class="navbtn menubtn" title="Contents (M)">&#9776;</button>
</div>
<div class="slidemenu" hidden>
  <button class="menuclose" aria-label="Close menu">&times;</button>
  <h2>Revision 1 &#8212; slide overview</h2>
  <div class="menugrid"></div>
</div>

</body>
</html>
'''

if __name__ == '__main__':
    main()
