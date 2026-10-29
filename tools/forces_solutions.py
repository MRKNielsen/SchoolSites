#!/usr/bin/env python3
"""Build the Forces gated answer key from the SAME answers as the teacher PDF.

    python3 tools/forces_solutions.py            # from the repo root

Reads   year7-science/forces/booklet/Forces_Motion_Lesson_Booklet_Yr7_8.tex  (questions, keys)
        .../booklet/Forces_Motion_Lesson_Booklet_Yr7_8.akp and .aux            (labels, pages, refs)
        .../booklet/Forces_Motion_Lesson_Booklet_Yr7_8_Teacher.akp and .log    (page check, drawing sizes)
        .../booklet/teacher-answers/*.tex                                      (every \\defans)
Writes  year7-science/forces/solutions-payload.html   (GITIGNORED plaintext)
        year7-science/forces/solutions.html           (gated shell; an existing BLOB line is kept)

Build the student copy, then the teacher copy (three passes each), then run
this. It refuses to write anything if the two .akp logs disagree on a single
page, if a key has no answer, or if an answer has no key: a stale key would
otherwise attach an answer to the wrong question with no warning. Needs
pandoc, xelatex and dvisvgm. Then encrypt the payload with
tools/staff-crypt.html and paste the BLOB line over the one in solutions.html.
"""
import re, os, sys, html, subprocess, tempfile, shutil, glob

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
UNIT = os.path.join(ROOT, 'year7-science', 'forces')
BK = os.path.join(UNIT, 'booklet')
BASE = 'Forces_Motion_Lesson_Booklet_Yr7_8'
if len(sys.argv) > 2:            # testing: forces_solutions.py <booklet dir> <output dir>
    BK, UNIT = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])

def die(msg):
    sys.exit('forces_solutions: ' + msg)

def read(p):
    return open(p, encoding='utf-8').read()

def group(s, i):
    """s[i] == '{' -> (content, index after the matching brace)"""
    if s[i] != '{':
        raise ValueError('expected { at %d: %r' % (i, s[i:i + 30]))
    d = 0; j = i
    while j < len(s):
        c = s[j]
        if c == '\\':
            j += 2; continue
        if c == '{': d += 1
        elif c == '}':
            d -= 1
            if d == 0: return s[i + 1:j], j + 1
        j += 1
    raise ValueError('unbalanced brace at %d' % i)

def args(s, i, n):
    out = []
    for _ in range(n):
        while s[i] in ' \t\n': i += 1
        a, i = group(s, i); out.append(a)
    return out, i

# ── inputs and the cross-checks ─────────────────────────────────────────────
tex = read(os.path.join(BK, BASE + '.tex'))
body = tex[tex.rindex('\\begin{document}'):]
labels = {m.group(1): (m.group(2), m.group(3)) for m in
          re.finditer(r'\\newlabel\{([^}]*)\}\{\{([^}]*)\}\{([^}]*)\}', read(os.path.join(BK, BASE + '.aux')))}
def akp(p):
    out = {}
    for line in read(p).splitlines():
        f = line.split(' ', 3)
        if len(f) >= 3: out[f[0]] = dict(page=f[1], label=f[3] if len(f) > 3 else '')
    return out
S = akp(os.path.join(BK, BASE + '.akp'))
T = akp(os.path.join(BK, BASE + '_Teacher.akp'))
bad = [k for k in S if T.get(k, {}).get('page') != S[k]['page']]
if bad:
    die('student and teacher copies disagree on the page of %d keys (e.g. %s): rebuild both' % (len(bad), bad[:5]))
dims = {m.group(1): (float(m.group(2)), float(m.group(3))) for m in
        re.finditer(r'ANSDIMS (\S+) ([\d.]+) ([\d.]+)', read(os.path.join(BK, BASE + '_Teacher.log')))}
ANS = {}; COMMON = ''
for f in sorted(glob.glob(os.path.join(BK, 'teacher-answers', '*.tex'))):
    s = re.sub(r'(?<!\\)%[^\n]*', '', read(f))      # comments out, escaped \% kept
    if os.path.basename(f) == 'common.tex':
        COMMON = s; continue
    for m in re.finditer(r'\\defans\{([^}]*)\}', s):
        a, _ = group(s, m.end())
        if m.group(1) in ANS: die('key answered twice: ' + m.group(1))
        ANS[m.group(1)] = a.strip()
missing = [k for k in S if not ANS.get(k)]
extra = [k for k in ANS if k not in S]
if missing: die('%d keys have no answer, e.g. %s' % (len(missing), missing[:8]))
if extra: die('%d answers have no key in the booklet, e.g. %s' % (len(extra), extra[:8]))

# ── LaTeX clean-up before pandoc ────────────────────────────────────────────
def ref(m):
    lab = labels.get(m.group(2))
    if not lab: return '??'
    return lab[1] if m.group(1) == 'pageref' else lab[0]
CELLS = []                       # cell keys in placeholder order: QQC<n>QQ
def fix_tabular(t):
    """Drop the zero-width S column; custom column types become l or c."""
    spec, e = group(t, len('\\begin{tabular}'))
    cols = re.findall(r'(S|[WLCZpm]\{[^}]*\}|[lcr])', spec)
    hasS = bool(cols) and cols[0] == 'S'
    cols = [c for c in cols if c != 'S']
    newspec = '|' + '|'.join('c' if c[0] in 'ZC' else 'l' for c in cols) + '|'
    rows = t[e:t.rindex('\\end{tabular}')]
    if hasS:
        rows = re.sub(r'(^|\\\\[^\n]*\n)(\s*)(\\hd\s*)?&', r'\1\2', rows)
    return '\\begin{tabular}{%s}%s\\end{tabular}' % (newspec, rows)
def mkcell(m):
    CELLS.append(m.group(1))
    return 'QQC%dQQ' % (len(CELLS) - 1)
DROP = [r'\\needspace\{[^}]*\}', r'\\vspace\*?\{[^}]*\}', r'\\hspace\*?\{[^}]*\}', r'\\(med|small|big)skip\b',
        r'\\noindent\b', r'\\hfill\b', r'\\(new|clear)page\b', r'\\label\{[^}]*\}', r'\\edef\\abgrp\{[^\n]*?\\relax\}',
        r'\\gdef\\abgrp\{0\}', r'\\begin\{minipage\}(\[[^]]*\])?\{[^}]*\}', r'\\end\{minipage\}',
        r'\\(begin|end)\{ctab\}', r'\\talt\b', r'\\tmid\b', r'\\hd\b', r'\\anslabelset\{[^}]*\}',
        r'\\def\\wsname\{[^}]*\}', r'\\arrayrulecolor\{[^}]*\}', r'\\color\{[^}]*\}', r'\\tikz\{[^\n]*?\}\}?',
        r'\\(small|footnotesize|scriptsize|normalsize)\b', r'\\expfigcap\{[^}]*\}', r'\\textcolor\{[^}]*\}',
        r'\\wssafety\{[^}]*\}', r'\\(begin|end)\{yr[78]box\}']
FRAC = {('1', '2'): '½', ('1', '3'): '⅓', ('1', '4'): '¼', ('1', '6'): '⅙'}
def simple(x):
    return re.fullmatch(r'\s*[\w.]+\s*', x) is not None
def mathfix(m):
    """texmath's plain output cannot draw \\frac or \\sqrt: write them inline"""
    e = m.group(0).replace('\\tfrac', '\\frac').replace('\\dfrac', '\\frac')
    e = re.sub(r'\\frac(\d)(\d)', r'\\frac{\1}{\2}', e)
    while True:
        k = e.find('\\frac{')
        if k < 0: break
        a, j = group(e, k + 5); b, j2 = group(e, j)
        rep = FRAC.get((a.strip(), b.strip())) or '%s/%s' % (a if simple(a) else '(%s)' % a, b if simple(b) else '(%s)' % b)
        e = e[:k] + rep + e[j2:]
    while True:
        k = e.find('\\sqrt{')
        if k < 0: break
        a, j = group(e, k + 5)
        e = e[:k] + ('√' + a if simple(a) else '√(%s)' % a) + e[j:]
    return e
def clean(s):
    s = re.sub(r'(?<!\\)%[^\n]*', '', s)
    s = s.replace('$^\\circ$', '°').replace('\\,\\textdegree C', '\\,°C').replace('\\textdegree{}', '°').replace('\\textdegree', '°')
    s = re.sub(r'(?<!\\)\$[^$]+\$|\\\[.*?\\\]', mathfix, s, flags=re.S)
    s = re.sub(r'\\(pageref|ref)\{([^}]*)\}', ref, s)
    s = re.sub(r'\\begin\{tabular\}.*?\\end\{tabular\}', lambda m: fix_tabular(m.group(0)), s, flags=re.S)
    s = re.sub(r'\\cell\{([^}]*)\}', mkcell, s)
    for pat in DROP:
        s = re.sub(pat, '', s)
    s = re.sub(r'\\figcap(\[[^]]*\])?\{([^{}]|\{[^{}]*\})*\}', '', s)
    s = re.sub(r'\\diag[A-Za-z]+(\{[^}]*\})?', r'\\emph{(diagram in the booklet)}', s)
    s = re.sub(r'\\thead\{((?:[^{}]|\{[^{}]*\})*)\}', r'\1', s)
    s = s.replace('\\scaf{', '\\emph{').replace('\\tfrac', '\\frac').replace('\\textbullet', '•')
    s = s.replace('\\ansFBD', '%')
    s = re.sub(r'\\\\\[[^]]*\]', r'\\\\', s)
    return s.strip()

# ── walk the booklet: lessons > parts > cards > parts ───────────────────────
TOK = re.compile(r'''\\sectiondiv\{|\\lessonpart\{|\\vocabhead|\\rcqk\{|\\begin\{wedo\}|\\end\{wedo\}|\\begin\{scaffold\}|
\\end\{scaffold\}|\\taskpair\{|\\ptpair\{|\\taskpart\{|\\task(?![a-zA-Z])(\[[a-z]\])?|\\exttask(?![a-zA-Z])|\\pt\{|
\\[aw]box\{|\\drawk\{|\\graphgrid\{|\\subsection\{Workstation|\\wsstep\{|\\subsubsection\*\{Results\}|\\begin\{tabular\}|
\\begin\{(workedex|readingbox|infobox|skillbox|expheader|enumerate|itemize)\}|\\optionalnote\{|\\subsection\{|\\subsubsection\*\{''', re.X)
SKIP = ('workedex', 'readingbox', 'infobox', 'skillbox', 'expheader', 'enumerate', 'itemize')
lessons = []; L = None; card = None; pend = ''
def new_card(kind):
    global card, pend
    keep = L['part'] in ('C', 'D') and len(pend) < 600
    card = dict(kind=kind, stem=pend if keep else '', parts=[], own=[], keys=[], part=None, closed=False, ext=(L['part'] == 'D'), caps={})
    pend = ''
    L['items'].append(card)
def add_part(name, text=''):
    card['part'] = dict(name=name, text=text, keys=[])
    card['parts'].append(card['part'])
def add_text(t):
    global pend
    if card is None or card['closed']:
        pend += t
    elif card['part'] is not None:
        card['part']['text'] += t
    else:
        card['stem'] += t
def add_key(k, kind):
    (card['part']['keys'] if card['part'] is not None else card['own']).append((k, kind))
    card['keys'].append(k)
i = 0
while True:
    m = TOK.search(body, i)
    if not m: break
    if L is not None: add_text(body[i:m.start()])
    tok = m.group(0); j = m.end()
    if tok == '\\sectiondiv{':
        (t, sub), e = args(body, j - 1, 2)
        L = dict(n=len(lessons) + 1, title=t, sub=sub, items=[], part=''); lessons.append(L)
        card = None; pend = ''; i = e; continue
    if L is None:
        i = j; continue
    if tok == '\\lessonpart{':
        (p, t, _), e = args(body, j - 1, 3)
        L['part'] = p; L['items'].append(dict(kind='part', letter=p, title=t)); card = None; pend = ''; i = e; continue
    if tok.startswith('\\begin{') and m.group(2) in SKIP:
        env = m.group(2); e = body.index('\\end{%s}' % env, j) + len('\\end{%s}' % env)
        if '\\cell{' in body[m.start():e] or re.search(r'\\[aw]box\{', body[m.start():e]):
            die('answer furniture inside a skipped %s environment' % env)
        i = e; continue
    if tok == '\\optionalnote{':
        _, e = group(body, j - 1); i = e; continue
    if tok == '\\vocabhead':
        new_card('vocab'); card['label'] = 'Key vocabulary'; i = j; continue
    if tok == '\\subsubsection*{Results}':
        new_card('results'); card['label'] = 'Results'; i = j; continue
    if tok == '\\subsection{Workstation':
        t, e = group(body, m.start() + len('\\subsection'))
        L['items'].append(dict(kind='sub', title='Workstation' + t[len('Workstation'):] if t.startswith('Workstation') else t))
        card = None; pend = ''; i = e; continue
    if tok in ('\\subsection{', '\\subsubsection*{'):
        _, e = group(body, j - 1)
        if card is not None and card['kind'] != 'results': card['closed'] = True
        pend = ''; i = e; continue
    if tok == '\\wsstep{':
        _, e = group(body, j - 1); new_card('q'); i = e; continue
    if tok == '\\rcqk{':
        (k, q, _), e = args(body, j - 1, 3)
        new_card('q'); card['stem'] = q; add_key(k, 'a'); card['closed'] = True; i = e; continue
    if tok in ('\\begin{wedo}', '\\begin{scaffold}'):
        _, e = group(body, j); new_card('q'); i = e; continue
    if tok in ('\\end{wedo}', '\\end{scaffold}'):
        if card is not None: card['closed'] = True
        i = j; continue
    if tok == '\\taskpart{':
        p, e = group(body, j - 1); add_part(p); i = e; continue
    if tok.startswith('\\task') and not tok.startswith('\\taskpair'):
        new_card('q')
        if m.group(1): add_part(m.group(1)[1])
        i = j; continue
    if tok.startswith('\\exttask'):
        new_card('q'); i = j; continue
    if tok == '\\pt{':
        p, e = group(body, j - 1); add_part(p); i = e; continue
    if tok == '\\taskpair{':
        a4, e = args(body, j - 1, 4)
        for t, bx in ((a4[0], a4[1]), (a4[2], a4[3])):
            new_card('q'); card['stem'] += t
            add_key(re.match(r'\\[aw]box\{([^}]*)\}', bx).group(1), 'a'); card['closed'] = True
        i = e; continue
    if tok == '\\ptpair{':
        a6, e = args(body, j - 1, 6)
        for p, t, bx in ((a6[0], a6[1], a6[2]), (a6[3], a6[4], a6[5])):
            add_part(p, t); add_key(re.match(r'\\[aw]box\{([^}]*)\}', bx).group(1), 'a')
        i = e; continue
    if tok in ('\\abox{', '\\wbox{'):
        (k, _), e = args(body, j - 1, 2); add_key(k, 'a'); i = e; continue
    if tok == '\\drawk{':
        (k, _, cap), e = args(body, j - 1, 3); add_key(k, 'draw'); card['caps'][k] = cap; i = e; continue
    if tok == '\\graphgrid{':
        (k, _), e = args(body, j - 1, 2); add_key(k, 'graph'); i = e; continue
    if tok == '\\begin{tabular}':
        e = body.index('\\end{tabular}', j) + len('\\end{tabular}')
        t = body[m.start():e]
        if card is not None and not card['closed']:
            card['keys'] += re.findall(r'\\cell\{([^}]*)\}', t)
        elif '\\cell{' in t:
            die('a write-in table outside any question, near ' + t[:60])
        add_text(t); i = e; continue
    raise SystemExit('unhandled ' + tok)

seen = {k for L_ in lessons for it in L_['items'] for k in it.get('keys', [])}
lost = [k for k in S if k not in seen]
if lost: die('the walker missed %d keys, e.g. %s' % (len(lost), lost[:8]))
def boxkeys(it):
    """(key, kind) for every box, drawing and graph in a card, own then parts"""
    return list(it.get('own', [])) + [x for p in it.get('parts', []) for x in p['keys']]
DRAWN = {k for L_ in lessons for it in L_['items'] for k, kind in boxkeys(it) if kind in ('draw', 'graph')}
GRAPHS = {k for L_ in lessons for it in L_['items'] for k, kind in boxkeys(it) if kind == 'graph'}
nodim = [k for k in DRAWN if k not in dims]
if nodim: die('no ANSDIMS line in the teacher log for %s: rebuild the teacher copy' % nodim)

# ── pandoc, once for everything ─────────────────────────────────────────────
chunks = []
def chunk(latex):
    chunks.append(latex); return len(chunks) - 1
INTRO = re.compile(r'^\s*(Work through every task|Every question in this lesson goes beyond|These questions go beyond|The hardest questions in this extension)[^\n]*', re.M)
for L_ in lessons:
    for it in L_['items']:
        if it['kind'] not in ('q', 'vocab', 'results'): continue
        it['stem_c'] = chunk(clean(INTRO.sub('', it['stem'])))
        for p in it['parts']:
            p['text_c'] = chunk(clean(p['text']))
ans_c = {k: chunk(clean(a)) for k, a in ANS.items() if k not in DRAWN}
PRE = '\\newcommand{\\pt}[1]{(#1) }\n'
src = PRE + '\n\n'.join('ZQZITEM%dZQZ\n\n%s' % (n, c) for n, c in enumerate(chunks))
r = subprocess.run(['pandoc', '-f', 'latex', '-t', 'html', '--wrap=none'], input=src, capture_output=True, text=True)
if r.returncode: die('pandoc failed: ' + r.stderr[:2000])
pieces = re.split(r'<p>ZQZITEM(\d+)ZQZ</p>', r.stdout)
HT = {int(pieces[n]): pieces[n + 1].strip() for n in range(1, len(pieces), 2)}
if len(HT) != len(chunks): die('pandoc lost items: %d of %d came back' % (len(HT), len(chunks)))
leak = [n for n, h in HT.items() if re.search(r'\\[a-zA-Z]{2,}', h)]
if leak: print('warning: raw LaTeX left in %d items, e.g. %r' % (len(leak), HT[leak[0]][:160]))
def inline(h):
    h = h.strip()
    if h.startswith('<p>') and h.endswith('</p>') and h.count('<p>') == 1: h = h[3:-4]
    return h
def fill_cells(h):
    h = re.sub(r'QQC(\d+)QQ', lambda m: '<span class="cellans">%s</span>' % inline(HT[ans_c[CELLS[int(m.group(1))]]]), h)
    return h.replace('<table>', '<table class="ans">')

# ── drawings and graphs: the same TikZ, compiled standalone, as SVG ─────────
pre = tex[:tex.rindex('\\begin{document}')]
colours = '\n'.join(re.findall(r'^\\definecolor\{[^\n]*$', pre, re.M))
caps = {k: c for L_ in lessons for it in L_['items'] for k, c in it.get('caps', {}).items()}
order = [k for k in S if k in DRAWN]
svg = {}
tmp = tempfile.mkdtemp()
try:
    shutil.copytree(os.path.join(BK, 'fonts'), os.path.join(tmp, 'fonts'))
    doc = [r'\def\pgfsysdriver{pgfsys-dvisvgm.def}', r'\documentclass[tikz,border=1pt]{standalone}', r'\usepackage{fontspec}',
           r'\setmainfont{Lato}[Path=./fonts/, Extension=.ttf, UprightFont=Lato-Regular, ItalicFont=Lato-Italic, BoldFont=Lato-Bold, BoldItalicFont=Lato-BoldItalic]',
           r'\usepackage{amsmath}', r'\usetikzlibrary{arrows.meta,calc,positioning,patterns,decorations.pathreplacing}',
           colours, COMMON, r'\begin{document}']
    for k in order:
        w, h = dims[k]
        doc.append(r'\begin{tikzpicture}[x=1cm,y=1cm]\def\AW{%.5f}\def\AH{%.5f}' % (w, h))
        doc.append(r'\fill[white] (0,0) rectangle (\AW,\AH);')
        if k in GRAPHS: doc.append(r'\draw[step=5mm, Line, very thin] (0,0) grid (\AW,\AH);')
        doc.append(r'\draw[MidGrey, line width=0.5pt] (0,0) rectangle (\AW,\AH);')
        if caps.get(k, '').strip():
            doc.append(r'\node[anchor=north west, inner sep=0pt, text width=%.3fcm, font=\small, text=DarkGrey] at (0.5,{\AH-0.3}) {%s};' % (w - 1.0, caps[k]))
        doc += [ANS[k], r'\end{tikzpicture}']
    doc.append(r'\end{document}')
    open(os.path.join(tmp, 'd.tex'), 'w', encoding='utf-8').write('\n'.join(doc))
    # dvisvgm keeps labels as real text with a small WOFF2 subset of Lato,
    # about a twentieth of the size of pdftocairo's glyph paths
    r = subprocess.run(['xelatex', '-no-pdf', '-interaction=nonstopmode', '-halt-on-error', 'd.tex'], cwd=tmp, capture_output=True, text=True)
    if r.returncode: die('the drawing build failed:\n' + r.stdout[-1500:])
    r = subprocess.run(['dvisvgm', '--font-format=woff2', '--precision=3', '--bbox=papersize', '--page=1-', '-o', 'd-%p.svg', 'd.xdv'],
                       cwd=tmp, capture_output=True, text=True)
    if r.returncode: die('dvisvgm failed: ' + r.stderr[-800:])
    files = sorted(glob.glob(os.path.join(tmp, 'd-*.svg')), key=lambda f: int(re.findall(r'(\d+)\.svg$', f)[0]))
    if len(files) != len(order): die('dvisvgm made %d drawings, expected %d' % (len(files), len(order)))
    for f, k in zip(files, order):
        s = read(f); s = s[s.index('<svg'):]
        p = 'f%s' % re.sub(r'[^a-z0-9]', '', k.lower())    # ids, fonts and classes must be unique across the page
        s = re.sub(r"\bid='([^']+)'", lambda m: "id='%s-%s'" % (p, m.group(1)), s)
        s = re.sub(r"(xlink:href|href)='#([^']+)'", lambda m: "%s='#%s-%s'" % (m.group(1), p, m.group(2)), s)
        s = re.sub(r'url\(#([^)]+)\)', lambda m: 'url(#%s-%s)' % (p, m.group(1)), s)
        s = re.sub(r'\bnf(\d+)\b', lambda m: '%snf%s' % (p, m.group(1)), s)
        s = re.sub(r"class='f(\d+)'", lambda m: "class='%sf%s'" % (p, m.group(1)), s)
        s = re.sub(r'(?<![\w-])\.f(\d+)\b', lambda m: '.%sf%s' % (p, m.group(1)), s)
        s = re.sub(r"^<svg([^>]*?) width='[^']*' height='[^']*'", r'<svg\1', s, count=1)
        s = s.replace('<svg', '<svg role="img" aria-label="Model answer: %s" style="width:100%%;max-width:%dpx;height:auto"'
                      % (html.escape(S[k]['label']), int(dims[k][0] * 38)), 1)
        svg[k] = re.sub(r'>\s+<', '><', s)
finally:
    shutil.rmtree(tmp)

# ── the unlock script, from year7-science/space/worksheet-revision-solutions.html (v2 blob);
# its submit handler is the solutions-page one, with a guard for a placeholder blob ──
SCRIPT_PRE = '<script>\n(function(){\n'
SCRIPT_POST = '\n  var b64 = function(s){var bin=atob(s);var a=new Uint8Array(bin.length);for(var i=0;i<bin.length;i++)a[i]=bin.charCodeAt(i);return a;};\n  /* The payload is encrypted once under a random content key; that key is\n     wrapped separately under each password the page accepts. Try each\n     wrapper, and the first that opens tells us both the content key and\n     which audience just unlocked. */\n  async function derive(pw, salt, iter){\n    var baseKey = await crypto.subtle.importKey("raw", new TextEncoder().encode(pw),\n      {name:"PBKDF2"}, false, ["deriveKey"]);\n    return crypto.subtle.deriveKey(\n      {name:"PBKDF2", salt:b64(salt), iterations:iter, hash:"SHA-256"},\n      baseKey, {name:"AES-GCM", length:256}, false, ["decrypt"]);\n  }\n  async function unlock(pw){\n    for (var i = 0; i < BLOB.keys.length; i++){\n      var k = BLOB.keys[i], raw;\n      try {\n        raw = await crypto.subtle.decrypt({name:"AES-GCM", iv:b64(k.iv)},\n                                          await derive(pw, k.salt, k.iter), b64(k.ct));\n      } catch (e) { continue; }\n      var ckey = await crypto.subtle.importKey("raw", raw, {name:"AES-GCM"},\n                                               false, ["decrypt"]);\n      var pt = await crypto.subtle.decrypt({name:"AES-GCM", iv:b64(BLOB.iv)},\n                                           ckey, b64(BLOB.ct));\n      return { role: k.role, html: new TextDecoder().decode(pt) };\n    }\n    throw new Error("bad password");\n  }\n\n  /* Unlocked with the student password: this is a revision resource, not a\n     confidential teacher document, so drop the staff framing. The content\n     is identical — only the labelling changes. */\n  function softenForStudents(){\n    var tag = document.querySelector(".unit-tag");\n    if (tag) tag.textContent = "Answer key";\n    var note = document.querySelector(".teacher-note strong");\n    if (note && /How to use/i.test(note.textContent)) return;\n  }\n\n  var form=document.getElementById("unlockForm");\n  form.addEventListener("submit",async function(e){\n    e.preventDefault();\n    var err=document.getElementById("err");\n    err.textContent="";\n    /* a placeholder blob is a truthy object, so test its ciphertext */\n    if(!BLOB.ct){\n      err.textContent="This answer key has not been encrypted yet (tools/staff-crypt.html).";\n      return;\n    }\n    try{\n      var res=await unlock(document.getElementById("pw").value);\n      document.body.dataset.role=res.role;\n      if(res.role==="student") softenForStudents();\n      document.getElementById("content").innerHTML=res.html;\n      document.getElementById("lock").style.display="none";\n      window.scrollTo(0,0);\n    }catch(ex){\n      err.textContent="Incorrect password. Try again.";\n      document.getElementById("pw").value="";\n      document.getElementById("pw").focus();\n    }\n  });\n})();\n</script>\n</body>\n</html>\n'

# the model-results notes are teacher material too, so they live in teacher-answers/
NOTES = read(os.path.join(BK, 'teacher-answers', 'web-notes.html'))

# ── assemble the payload ────────────────────────────────────────────────────
def esc(s):
    return html.escape(s, quote=False)
def plain(t):
    t = re.sub(r'\\texorpdfstring\{((?:[^{}]|\{[^{}]*\})*)\}\{[^}]*\}', r'\1', t)
    t = re.sub(r'\$([^$]*)\$', r'\1', t)
    return t.replace('\\textbullet{}', '•').replace('---', '—').replace('--', '–').replace('\\', '')
def card_label(it):
    if it['kind'] in ('vocab', 'results'): return it['label']
    lab = S[it['keys'][0]]['label']
    return re.sub(r' \([^)]*\)$', '', lab)
def ans_html(k, kind):
    if kind in ('draw', 'graph'): return '<div class="draw">%s</div>' % svg[k]
    return HT[ans_c[k]]
STYLE = ('<style>'
  '.solutions-page .cellans{color:var(--neg);font-weight:600}'
  '.solutions-page .q{flex-direction:column;align-items:stretch;gap:.3em}'
  '.solutions-page .qhead{display:flex;gap:.6em;align-items:baseline;flex-wrap:wrap}'
  '.solutions-page .qhead .pg{margin-left:auto;font-size:.78rem;font-weight:600;color:var(--muted);white-space:nowrap}'
  '.solutions-page .qtext{font-weight:400;color:var(--ink)}.solutions-page .qtext p{margin:.25em 0}'
  '.solutions-page .a .part{margin-top:.8em}.solutions-page .a .part:first-child{margin-top:0}'
  '.solutions-page .a .pq{color:var(--muted);font-size:.93rem;margin-bottom:.2em}'
  '.solutions-page .a .pl{font-weight:700;color:var(--accent-dark);margin-right:.35em}'
  '.solutions-page .draw{margin:.4em 0;overflow-x:auto}'
  '.solutions-page table.ans td p,.solutions-page table.ans th p{margin:0}'
  '.solutions-page .a table.ans{display:block;overflow-x:auto}'
  '</style>')
H = [STYLE, '<nav class="toc">' + ''.join('<a href="#l%d">%d &middot; %s</a>' % (L_['n'], L_['n'], esc(plain(L_['title']).split(' (')[0]))
                                       for L_ in lessons) + '<a class="review" href="#notes">Model results</a></nav>', '<main>']
H.append('<section class="lesson" id="notes"><div class="lesson-head"><span class="lesson-num">&#9888;</span>'
         '<span class="lesson-title">About the experiment answers</span></div><div class="note">' + NOTES + '</div></section>')
ncards = 0
for L_ in lessons:
    opt = 'Optional' in L_['title']
    H.append('<section class="lesson" id="l%d"><div class="lesson-head"><span class="lesson-num">%d</span>'
             '<span class="lesson-title">%s</span>%s</div>' % (L_['n'], L_['n'], esc(plain(L_['title'])),
             ' <span class="tag y8">Year 8 extension</span>' if opt else ''))
    for it in L_['items']:
        if it['kind'] == 'part':
            H.append('<div class="subhead"><h3>Part %s &middot; %s</h3></div>' % (it['letter'], esc(it['title']))); continue
        if it['kind'] == 'sub':
            H.append('<div class="subhead"><h3>%s</h3></div>' % esc(plain(it['title']))); continue
        if not it['keys']: continue
        ncards += 1
        page = S[it['keys'][0]]['page']
        tag = '<span class="tag y8">Above level</span>' if it['ext'] and not opt else ''
        head = '<div class="qhead"><span class="qref">%s</span>%s<span class="pg">Booklet p.&nbsp;%s</span></div>' % (esc(card_label(it)), tag, page)
        stem = fill_cells(HT[it['stem_c']])
        if it['kind'] in ('vocab', 'results'):
            H.append('<div class="qa"><div class="q">%s</div><div class="a">%s</div></div>' % (head, stem)); continue
        a = ''.join(ans_html(k, kd) for k, kd in it['own'])
        for p in it['parts']:
            a += '<div class="part"><div class="pq"><span class="pl">(%s)</span>%s</div>%s</div>' % (
                esc(p['name']), inline(fill_cells(HT[p['text_c']])), ''.join(ans_html(k, kd) for k, kd in p['keys']))
        H.append('<div class="qa"><div class="q">%s<div class="qtext">%s</div></div><div class="a">%s</div></div>' % (head, stem, a))
    H.append('</section>')
H.append('</main>')
payload = '\n'.join(H) + '\n'

# ── write the payload and the gated shell ───────────────────────────────────
nkeys = len(S)
shell_head = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Solution Set &mdash; Forces and Motion | Year 7 Science</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Bitter:wght@500;700;800&family=Source+Sans+3:ital,wght@0,400;0,600;0,700;1,400&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../../assets/css/tokens.css">
<link rel="stylesheet" href="../../assets/css/solutions.css">
<link rel="stylesheet" href="../../assets/css/sitenav.css">
<script src="../../assets/js/sitenav.js" defer></script>
<link rel="icon" href="../../assets/icons/favicon.svg" type="image/svg+xml">
<link rel="icon" href="../../assets/icons/favicon.ico" sizes="32x32">
<link rel="apple-touch-icon" href="../../assets/icons/apple-touch-icon.png">
<link rel="manifest" href="../../site.webmanifest">
<meta name="theme-color" content="#24576f">
</head>
<body class="solutions-page theme-science">
<!-- GENERATED by tools/forces_solutions.py from the booklet and teacher-answers/ -- do not edit by hand.
     The answers are the ones printed in red in the (gitignored) teacher PDF. -->

<div class="hero">
  <a class="back-btn" href="index.html">&#8592; Back to unit</a>
  <div class="unit-tag">Teacher Answer Key &middot; Confidential</div>
  <h1>Solution Set &mdash; Forces and Motion</h1>
  <p class="sub">Model answers for every box, table, drawing and graph in the Year 7/8 Forces and Motion lesson booklet &mdash; the same answers as the red teacher copy.</p>
  <div class="meta-row">
    <span>14 lessons</span><span>&middot;</span>
    <span>%(cards)d questions</span><span>&middot;</span>
    <span>%(keys)d answers</span><span>&middot;</span>
    <span>Year 7 core + Year 8 extension</span><span>&middot;</span>
    <span>Victorian Curriculum F&ndash;10 v2.0</span>
  </div>
  <div class="teacher-note">
    <strong>How to use:</strong> These are model responses, not the only acceptable wording &mdash; accept any answer that shows the same understanding. Question numbers and page references match the current booklet (Task <em>lesson</em>.<em>n</em>, Extension <em>lesson</em>.<em>n</em>, C<em>n</em> for comprehension). Purple &ldquo;Above level&rdquo; tags mark Part D; Lessons 11 and 14 are optional Year 8 extension lessons. The experiment results are <strong>modelled</strong> &mdash; see &ldquo;Model results&rdquo; before marking students&rsquo; own data.
  </div>
</div>

<div class="lockscreen" id="lock">
  <div class="lock-icon">&#128273;</div>
  <h2>Staff access only</h2>
  <p>This solution set is password protected. Enter the staff password to view the answers.</p>
  <form id="unlockForm">
    <input id="pw" type="password" autocomplete="off" placeholder="Password" autofocus />
    <button type="submit">Unlock</button>
  </form>
  <p class="err" id="err"></p>
</div>
<div id="content"></div>

<footer>
  Forces and Motion &middot; Teacher Solution Set &middot; Year 7 Science &middot; Victorian Curriculum F&ndash;10 v2.0<br>
  Generated to accompany <em>Forces_Motion_Lesson_Booklet_Yr7_8.pdf</em>. For staff use.
</footer>

''' % dict(cards=ncards, keys=nkeys)
PLACEHOLDER = 'var BLOB = {"v":2,"iv":"","ct":"","keys":[]};'
gated = os.path.join(UNIT, 'solutions.html')
blob = PLACEHOLDER
if os.path.exists(gated):
    m = re.search(r'^var BLOB = \{.*?\};', read(gated), re.M)
    if m: blob = m.group(0)
open(os.path.join(UNIT, 'solutions-payload.html'), 'w', encoding='utf-8').write(payload)
open(gated, 'w', encoding='utf-8').write(shell_head + SCRIPT_PRE + blob + SCRIPT_POST)
print('payload %d KB: %d cards, %d answers (%d drawings and graphs) -> %s' % (
    len(payload) // 1024, ncards, nkeys, len(svg), os.path.relpath(os.path.join(UNIT, 'solutions-payload.html'), ROOT)))
if blob == PLACEHOLDER:
    print('solutions.html has a PLACEHOLDER blob: encrypt solutions-payload.html with tools/staff-crypt.html and paste the BLOB line in')
else:
    print('solutions.html kept its existing BLOB line: it is now STALE until you re-encrypt the new payload')
