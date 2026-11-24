#!/usr/bin/env python3
"""Build the 2027 A5 Forces and Motion lesson booklets from the A4 master.

    cd year7-science/forces/booklet/a5
    python3 make_a5.py                 # writes Forces_Lesson_Booklet_Yr7_A5_Book1.tex ... _Book3.tex
    python3 fill_a5.py Forces_Lesson_Booklet_Yr7_A5_Book1    (and Book2, Book3)

The master (../Forces_Motion_Lesson_Booklet_Yr7_8.tex) is read, never changed.
  * The nine theory lessons, whole and numbered as the planner numbers them:
    1, 2, 4, 5, 7, 9, 11 (optional), 12, 14 (optional). Lessons 3, 6, 8, 10
    and 13 are the five experiments (for the Forces Experiment Booklet);
    15-17 are the trebuchet investigation, which has its own booklet.
  * Three books: Lessons 1-4, 5-9 and 11-14.
  * Every keyed answer box (\\abox, \\wbox, \\rcqk ...) keeps its key, so a red
    teacher copy can later be made the same way as the A4 one.
  * A5 twoside, padded with notes pages to a multiple of 4 after a glossary
    built from the key vocabulary; the 2027 workbook style (a5-style.tex, the
    same file as the Particle Model and Separation books).
  * Figures and tables wider than the A5 text block are scaled to fit it.
Fails if a word of a kept lesson is lost or an environment is cut in half.
"""
import re, sys, os

HERE = os.path.dirname(os.path.abspath(__file__))
MASTER = os.path.join(HERE, '..', 'Forces_Motion_Lesson_Booklet_Yr7_8.tex')
OUT = os.path.join(HERE, 'Forces_Lesson_Booklet_Yr7_A5_Book%d.tex')
BOOKS = {1: [1, 2, 4], 2: [5, 7, 9], 3: [11, 12, 14]}
MOVED = {3: 'Experiment 1 --- Everyday Forces', 6: 'Experiment 2 --- Friction and Mass',
         8: 'Experiment 3 --- Bounce Efficiency', 10: 'Experiment 4 --- Lever Mechanical Advantage',
         13: 'Experiment 5 --- Measuring $g$'}
LATER = {15: 'Trebuchet investigation: planning', 16: 'Trebuchet investigation: launches',
         17: 'Trebuchet investigation: analysis and conclusion'}
TEXT_W = 11.8
COL_PAD = 0.42

src = open(MASTER, encoding='utf-8').read()
pre, rest = src.split('\n\\begin{document}', 1)
heads = [(m.start(), int(m.group(1))) for m in re.finditer(r'^% ═+\n%  LESSON (\d+) ', rest, re.M)]
blocks = {}
for i, (pos, n) in enumerate(heads):
    end = heads[i + 1][0] if i + 1 < len(heads) else rest.index('\\end{document}')
    blocks[n] = rest[pos:end]

pre = pre.replace('\\documentclass[11pt,a4paper]{article}',
                  '\\documentclass[11pt,a5paper,twoside]{article}\n\\newcommand{\\unitname}{Forces and Motion}\\newcommand{\\unitcaps}{FORCES AND MOTION}')
pre, n = re.subn(r'\\usepackage\[a4paper[^\]]*\]\{geometry\}',
                 r'\\usepackage[a5paper, inner=17mm, outer=13mm, top=19mm, bottom=17mm, headheight=14pt, headsep=4mm, footskip=8mm]{geometry}', pre)
assert n == 1, 'geometry'
pre = pre.replace('Path=./fonts/', 'Path=../fonts/')
# page-fill files are per book (a teacher wrapper would set \\abbase to the student book's name)
pre, n = re.subn(r'\\def\\abbase\{Forces_Motion_Lesson_Booklet_Yr7_8\}', lambda m: '\\providecommand\\abbase{\\jobname}', pre)
assert n == 1, 'abbase'
pre = pre.replace('\\usepackage{bookmark}', '\\usepackage{bookmark}\n\\makeatletter\\providecommand\\Hy@PageAnchorSlide{}\\makeatother', 1)
if '\\usepackage{graphicx}' not in pre:
    pre = pre.replace('\\usepackage{longtable}', '\\usepackage{longtable}\n\\usepackage{graphicx}')


def fit_table(m):
    spec = m.group(1)
    widths = [float(w) for w in re.findall(r'[WZLCpm]\{([\d.]+)cm\}', spec)]
    if not widths:
        return m.group(0)
    total = sum(widths) + COL_PAD * len(widths)
    if total <= TEXT_W:
        return m.group(0)
    f = (TEXT_W - COL_PAD * len(widths)) / sum(widths)
    spec2 = re.sub(r'([WZLCpm])\{([\d.]+)cm\}', lambda k: '%s{%.2fcm}' % (k.group(1), float(k.group(2)) * f), spec)
    return '\\begin{tabular}{%s}' % spec2


def ink(t):
    # the master's few raw hues (red!55!black, brown!30 ...) become greys
    return re.sub(r'(?<![A-Za-z])(red|blue|green|orange|yellow|brown|purple|violet|teal)(?=!)', 'black', t)


def fit_pictures(t):
    t = ink(t)
    t = t.replace('\\begin{tikzpicture}', '\\begin{fitbox}\\begin{tikzpicture}')
    return t.replace('\\end{tikzpicture}', '\\end{tikzpicture}\\end{fitbox}')


def tabspec(t):
    out, i = [], 0
    while True:
        j = t.find('\\begin{tabular}{', i)
        if j < 0:
            out.append(t[i:]); break
        k = j + len('\\begin{tabular}{'); depth = 1
        while depth:
            depth += {'{': 1, '}': -1}.get(t[k], 0); k += 1
        out.append(t[i:j])
        out.append(re.sub(r'\\begin\{tabular\}\{(.*)\}$', fit_table, t[j:k], flags=re.S))
        i = k
    return ''.join(out)


dpos = pre.index('%  EMBEDDED DIAGRAM DEFINITIONS')
dend = pre.index('%  LESSON STRUCTURE')
pre = pre[:dpos] + fit_pictures(tabspec(pre[dpos:dend])) + pre[dend:]

style = open(os.path.join(HERE, 'a5-style.tex'), encoding='utf-8').read()
style = style.replace('{The Particle Model}', '{Forces and Motion}').replace('{THE PARTICLE MODEL}', '{FORCES AND MOTION}')


def balanced(t, what):
    for env in set(re.findall(r'\\begin\{(\w+)\}', t)) | set(re.findall(r'\\end\{(\w+)\}', t)):
        assert t.count('\\begin{%s}' % env) == t.count('\\end{%s}' % env), (what, env)
    return t


titles = {n: re.search(r'\\sectiondiv\{((?:[^{}]|\{[^{}]*\})*)\}', blocks[n]).group(1) for n in blocks}


def build(book, keep):
    words = []
    body = []
    for num in keep:
        b = balanced(blocks[num], num)
        b = fit_pictures(tabspec(b))
        # two narrow answer columns whose one-word heading is wider than the A5 column
        b = b.replace('\\thead{Acceleration}', '\\thead{\\scriptsize Acceleration}').replace('\\thead{Projectile?}', '\\thead{\\scriptsize Projectile?}')
        body.append('\\setcounter{section}{%d}\\renewcommand{\\lessonart}{%d}\n' % (num - 1, num) + b)

    def label_vocab(block):
        a = block.find('\\vocabhead'); bend = block.find('\\end{ctab}', a)
        if a < 0:
            return block
        v = block[a:bend]
        def lab(m):
            w = m.group(2); slug = re.sub(r'[^a-z0-9]+', '-', w.lower()).strip('-')
            if any(s == slug for _, s in words):
                return m.group(0)
            words.append((w, slug))
            return m.group(1) + '\\label{voc:%s}' % slug + m.group(3)
        v = re.sub(r'(\\textbf\{([^}\\]+)\})(\}?\s*&)', lab, v)
        return block[:a] + v + block[bend:]
    body = [label_vocab(b) for b in body]

    gloss = ['\\clearpage\\markboth{Glossary}{Glossary}\\hypertarget{glossary}{}\\pdfbookmark[1]{Glossary}{glossarybm}',
             '{\\headingfont\\bfseries\\LARGE Glossary}\\label{sec:glossary}\\par\\vspace{1mm}\\noindent\\rule{\\linewidth}{0.6pt}\\par',
             '{\\small Every key word in this booklet and the page it is introduced on.}\\par\\smallskip',
             '\\renewcommand{\\arraystretch}{1.3}',
             '\\begin{longtable}{|>{\\RaggedRight}p{34mm}|p{9mm}|p{\\dimexpr\\linewidth-43mm-6\\tabcolsep-4\\arrayrulewidth-1pt\\relax}|}',
             '\\hline \\rule{0pt}{4mm}\\headingfont\\bfseries Word & \\headingfont\\bfseries Page & \\headingfont\\bfseries In my own words \\\\ \\hline \\endhead']
    for w, s in sorted(words, key=lambda x: x[0].lower()):
        gloss.append('  %s & \\pageref{voc:%s} & \\\\ \\hline' % (w, s))
    gloss += ['\\end{longtable}', '\\padtofour']

    rows = []
    for n in range(1, 18):
        if n in MOVED:
            rows.append('  %d & \\textit{%s} & {\\footnotesize Experiment Booklet} \\\\ \\hline' % (n, MOVED[n]))
        elif n in LATER:
            rows.append('  %d & \\textit{%s} & {\\footnotesize Trebuchet booklet} \\\\ \\hline' % (n, LATER[n]))
        elif n in keep:
            rows.append('  %d & \\hyperlink{lesson.%d.1}{%s} & \\hyperlink{lesson.%d.1}{p.\\ \\pageref{sec:%d}} \\\\ \\hline' % (n, n, titles[n], n, n))
        else:
            other = [b for b, ls in BOOKS.items() if n in ls][0]
            rows.append('  %d & %s & Book %d \\\\ \\hline' % (n, titles[n], other))
    rng = 'Lessons %d--%d' % (min(keep), max(keep))
    front = (open(os.path.join(HERE, 'a5-front.tex'), encoding='utf-8').read()
             .replace('%%CONTENTS%%', '\n'.join(rows)).replace('%%BOOK%%', str(book)).replace('%%RANGE%%', rng)
             .replace('covers/particle-model.jpg', 'covers/forces.jpg')
             .replace('\\renewcommand{\\arraystretch}{1.45}', '\\renewcommand{\\arraystretch}{1.12}')
             .replace('The Particle Model}', 'Forces and Motion}')
             .replace('VC2S8U05 \\textbullet\\ VC2S8I01--I08 \\textbullet\\ VC2S8H01',
                      'VC2S8U13 \\textbullet\\ VC2S8U14 \\textbullet\\ VC2S8U15 \\textbullet\\ VC2S8I01--I08'))
    front = re.sub(r'\w+ lesson books?; experiments are in the \\textbf\{Experiment Booklet\}\.',
                   lambda m: 'Three lesson books. The five experiments are in the \\textbf{Experiment Booklet}; the trebuchet investigation has its own booklet.', front)
    assert '%%' not in front and 'particle-model.jpg' not in front

    out = pre + style + '\\begin{document}\n' + front + ''.join(body) + '\n'.join(gloss) + '\n\\end{document}\n'
    open(OUT % book, 'w', encoding='utf-8').write(out)

    def words_of(t):
        t = re.sub(r'%.*', '', t)
        return re.findall(r'[A-Za-z]{4,}', t)
    missing = set(w for num in keep for w in words_of(blocks[num])) - set(words_of(out))
    if missing:
        sys.exit('lost words: %s' % sorted(missing)[:20])
    print('wrote', os.path.basename(OUT % book), '-', len(keep), 'lessons,', len(words), 'glossary words')


for book, keep in BOOKS.items():
    build(book, keep)
