"""Page filling for the Trebuchet Investigation booklet.

Every writing box, graph grid and write-in table logs its page to
<base>.abp ("id group page [rows]"). This measures the empty space left at
the foot of each page of the built student PDF, shares it out among that
page's boxes (side-by-side boxes share one group; a table's share is split
across its rows) and writes <base>.abx (\abset{id}{extra}). It rebuilds and
backs off any page whose boxes moved, so nothing is pushed to a new page.
Run from booklet/:  python3 fill.py [jobname]   (needs xelatex, pdftoppm, Pillow)
The teacher copy reads the same .abx, so build it after this.
"""
import subprocess, os, re, sys
from collections import defaultdict
from PIL import Image

BASE = sys.argv[1] if len(sys.argv) > 1 else 'Trebuchet_Investigation_Yr7_8'
DPI = 100
TEXT_BOTTOM_MM = 277.0   # A4 297 mm minus the 2 cm bottom margin
TOP_SKIP_MM = 24.0       # below the running head
KEEP_MM = 8.0          # leave this much air at the foot: TeX versions differ by a few mm

def build():
    for _ in range(3):
        r = subprocess.run(['xelatex', '-interaction=nonstopmode', '-halt-on-error', BASE + '.tex'],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if r.returncode:
            sys.exit('xelatex failed, see ' + BASE + '.log')

def read_abp():
    boxes = {}
    for line in open(BASE + '.abp'):
        f = line.split()
        if len(f) >= 3:
            boxes[int(f[0])] = dict(grp=int(f[1]), page=int(f[2]), rows=int(f[3]) if len(f) > 3 else 0)
    return boxes

def free_space():
    subprocess.run(['pdftoppm', '-r', str(DPI), '-gray', BASE + '.pdf', '_fill'], check=True)
    out = {}
    for fn in sorted(os.listdir('.')):
        m = re.match(r'_fill-(\d+)\.pgm$', fn)
        if not m:
            continue
        im = Image.open(fn); w, h = im.size; px = im.load()
        mm = 297.0 / h
        lo, hi = int(TOP_SKIP_MM / mm), int(TEXT_BOTTOM_MM / mm)
        bottom = lo
        for y in range(hi, lo, -1):
            if any(px[x, y] < 245 for x in range(int(w * 0.08), int(w * 0.92), 2)):
                bottom = y; break
        out[int(m.group(1))] = TEXT_BOTTOM_MM - bottom * mm
        os.remove(fn)
    return out

def write_abx(extra):
    with open(BASE + '.abx', 'w') as f:
        for i in sorted(extra):
            if extra[i] > 0.005:
                f.write('\\abset{%d}{%.2fcm}\n' % (i, extra[i]))

def main():
    if os.path.exists(BASE + '.abx'):
        os.remove(BASE + '.abx')
    build()
    ref = read_abp(); npages = len(free_space())
    extra = defaultdict(float)
    damp = defaultdict(lambda: 0.92)
    for rnd in range(6):
        free = free_space()
        grew = False
        for p in sorted(free):
            ids = [i for i, b in ref.items() if b['page'] == p]
            if not ids or free[p] - KEEP_MM < 3.0:
                continue
            units = {}
            for i in ids:
                key = ref[i]['grp'] or i
                units.setdefault(key, []).append(i)
            share_cm = (free[p] - KEEP_MM) / 10.0 * damp[p] / len(units)
            for key, members in units.items():
                for i in members:
                    rows = ref[i]['rows']
                    extra[i] += share_cm / rows if rows else share_cm
            grew = True
        if not grew:
            break
        write_abx(extra); build()
        now = read_abp(); n = len(free_space())
        moved = {ref[i]['page'] for i in ref if now.get(i, {}).get('page') != ref[i]['page']}
        if n != npages or moved:
            # undo this round's growth on the offending pages and damp them
            bad = moved or set(free)
            for p in bad:
                for i, b in ref.items():
                    if b['page'] == p:
                        extra[i] *= 0.85
                damp[p] *= 0.6
            write_abx(extra); build()
        print('round', rnd + 1, 'free after:', {p: round(v) for p, v in free_space().items()})
    final = read_abp()
    assert all(final[i]['page'] == ref[i]['page'] for i in ref), 'a box moved page'
    print('pages', len(free_space()), '- boxes on the same pages as before')

main()
