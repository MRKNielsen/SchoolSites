"""Page filling for the A5 trial booklet (adapted from the Particle Model /
Trebuchet fill.py: same .abp/.abx protocol, A5 page geometry).

Every writing box logs its page to <base>.abp. This measures the empty
space left at the foot of each page of the built PDF, shares it out among
that page's boxes and writes <base>.abx, then rebuilds; a page whose boxes
moved is backed off. Run from a5-test/:  python3 fill_a5.py Space_Section1_A5
"""
import subprocess, os, re, sys
from collections import defaultdict
from PIL import Image

BASE = sys.argv[1] if len(sys.argv) > 1 else 'Space_Section1_A5'
DPI = 100
PAGE_MM = 210.0
TEXT_BOTTOM_MM = 193.0   # A5 210 mm minus the 17 mm bottom margin
TOP_SKIP_MM = 21.0       # below the running head
KEEP_MM = 6.0            # leave this much air at the foot


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
        mm = PAGE_MM / h
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
    good = {}
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
                units.setdefault(ref[i]['grp'] or i, []).append(i)
            share_cm = (free[p] - KEEP_MM) / 10.0 * damp[p] / len(units)
            for members in units.values():
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
            for p in (moved or set(free)):
                damp[p] *= 0.5
            extra = defaultdict(float, good)
            write_abx(extra); build()
        else:
            good = dict(extra)
        print('round', rnd + 1, 'free after:', {p: round(v) for p, v in free_space().items()})
    final = read_abp()
    assert all(final[i]['page'] == ref[i]['page'] for i in ref), 'a box moved page'
    print('pages', len(free_space()), '- boxes on the same pages as before')


main()
