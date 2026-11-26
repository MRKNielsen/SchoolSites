#!/usr/bin/env python3
"""Build the 2027 A5 Forces and Motion books: the at-level lesson books and
Advanced Forces.

    cd year7-science/forces/booklet/a5
    python3 make_a5.py      # writes Forces_Lesson_Booklet_Yr7_A5_Book1/2.tex and Advanced_Forces_Yr7_A5_Book1/2.tex
    python3 fill_a5.py <jobname>     (once per book)

Faculty decision, Nov 2026: lesson books are split by curriculum level. Every
student completes the at-level books; students who excel move on to Advanced
Forces, whose topics are deeper elaborations, not extra work, and which is
never labelled optional.

The master (../Forces_Motion_Lesson_Booklet_Yr7_8.tex) is read, never changed.
  * At-level books: theory Lessons 1, 2, 4, 5, 7, 9 and 12, numbered as the
    planner numbers them, each with its Part D (above level) removed, and the
    "(above level)" curriculum codes dropped. Book 1 = 1, 2, 4, 5; Book 2 = 7,
    9, 12. Lessons 3, 6, 8, 10 and 13 are in the Forces Experiment Booklet;
    11 and 14 (the old optional lessons) and 15-17 (trebuchet investigation)
    are listed where they now live.
  * Advanced Forces, two books (Topics 1-4, 5-7): adv-forces.tex. Topics 1-5 are written there and pull in
    the old Part D questions of Lessons 1, 2, 4, 5 and 7 as practice
    (%%PARTD:N%%); Topics 6 and 7 are the old Lessons 11 and 14, whole
    (%%LESSON:N%%), with the Part D questions of Lessons 9 and 12 added to
    their practice.
  * Every keyed answer box keeps its key, so a red teacher copy can be made
    the A4 way. A5 twoside, glossary, padded to a multiple of 4; the 2027
    workbook style (a5-style.tex). Wide figures and tables scale to fit.
Fails if a word of a kept lesson or of a moved Part D is lost.
"""
from a5_fullwidth import full_width
import re, sys, os

HERE = os.path.dirname(os.path.abspath(__file__))
MASTER = os.path.join(HERE, '..', 'Forces_Motion_Lesson_Booklet_Yr7_8.tex')
OUT = os.path.join(HERE, 'Forces_Lesson_Booklet_Yr7_A5_Book%d.tex')
OUT_ADV = os.path.join(HERE, 'Advanced_Forces_Yr7_A5_Book%d.tex')
ADV_BOOKS = {1: [1, 2, 3, 4], 2: [5, 6, 7]}   # two books: one 108-page book is past the stapler
ADV_SRC = os.path.join(HERE, 'adv-forces.tex')
BOOKS = {1: [1, 2, 4, 5], 2: [7, 9, 12]}
MOVED = {3: 'Experiment 1 --- Everyday Forces', 6: 'Experiment 2 --- Friction and Mass',
         8: 'Experiment 3 --- Bounce Efficiency', 10: 'Experiment 4 --- Lever Mechanical Advantage',
         13: 'Experiment 5 --- Measuring $g$'}
LATER = {15: 'Trebuchet investigation: planning', 16: 'Trebuchet investigation: launches',
         17: 'Trebuchet investigation: analysis and conclusion'}
ADVANCED = {11: 'Turning Effects and the Trebuchet', 14: 'Optimising Range'}
# Advanced topics: (title, at-level lessons it deepens)
TOPICS = {1: ('Mass, Weight and Gravity Beyond Earth', '1'), 2: ('Net Force, Drag and Terminal Velocity', '2'),
          3: ('Force Pairs and Momentum', '4'), 4: ('$F = ma$: Acceleration and Impact', '5'),
          5: ('Calculating Energy', '7'), 6: ('Turning Effects and the Trebuchet', '9, 10'),
          7: ('Optimising Range', '12')}
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




def split_d(n):
    """Lesson n without its Part D, and its Part D questions as plain tasks."""
    b = blocks[n]
    i = b.index('\\lessonpart{D}')
    core = b[:i].rstrip() + '\n\\newpage\n'
    d = b[i:]
    d = re.sub(r'\\lessonpart\{D\}\{[^}]*\}\{[^}]*\}\\label\{ext:\d+\}\s*', '', d)
    d = re.sub(r'\\begin\{yr8box\}\s*.*?\n\s*\n(\\medskip\s*)?', '', d, count=1, flags=re.S)
    d = d.replace('\\end{yr8box}', '').replace('\\newpage', '').replace('\\exttask', '\\task')
    d = d.replace('The 2\\,kg ball in Worked Example~\\ref{we:7.3} starts with 98\\,J of GPE',
                  'A 2\\,kg ball dropped from 5\\,m starts with 98\\,J of GPE')
    assert 'yr8box' not in d and '\\ref{we:' not in d, n
    return core, d.strip() + '\n'


def at_level(b):
    b = re.sub(r' \\textbullet\{\} VC2S10U\d+ \(above level\)', '', b)
    return b


def label_vocab_all(body, words):
    def one(block):
        out, pos = [], 0
        for m in re.finditer(r'\\vocabhead', block):
            bend = block.find('\\end{ctab}', m.start())
            v = block[m.start():bend]
            def lab(mm):
                w = mm.group(2); slug = re.sub(r'[^a-z0-9]+', '-', w.lower()).strip('-')
                if any(s_ == slug for _, s_ in words):
                    return mm.group(0)
                words.append((w, slug))
                return mm.group(1) + '\\label{voc:%s}' % slug + mm.group(3)
            out.append(block[pos:m.start()]); out.append(re.sub(r'(\\textbf\{([^}\\]+)\})(\}?\s*&)', lab, v)); pos = bend
        out.append(block[pos:])
        return ''.join(out)
    return one(body)


def glossary(words):
    g = ['\\clearpage\\markboth{Glossary}{Glossary}\\hypertarget{glossary}{}\\pdfbookmark[1]{Glossary}{glossarybm}',
         '{\\headingfont\\bfseries\\LARGE Glossary}\\label{sec:glossary}\\par\\vspace{1mm}\\noindent\\rule{\\linewidth}{0.6pt}\\par',
         '{\\small Every key word in this booklet and the page it is introduced on.}\\par\\smallskip',
         '\\renewcommand{\\arraystretch}{1.3}',
         '\\begin{longtable}{|>{\\RaggedRight}p{34mm}|p{9mm}|p{\\dimexpr\\linewidth-43mm-6\\tabcolsep-4\\arrayrulewidth-1pt\\relax}|}',
         '\\hline \\rule{0pt}{4mm}\\headingfont\\bfseries Word & \\headingfont\\bfseries Page & \\headingfont\\bfseries In my own words \\\\ \\hline \\endhead']
    for w, s_ in sorted(words, key=lambda x: x[0].lower()):
        g.append('  %s & \\pageref{voc:%s} & \\\\ \\hline' % (w, s_))
    return '\n'.join(g + ['\\end{longtable}', '\\padtofour'])


def front_common(rows, book_tag, rng, title, how, vc):
    f = (open(os.path.join(HERE, 'a5-front.tex'), encoding='utf-8').read()
         .replace('%%CONTENTS%%', '\n'.join(rows))
         .replace('Lesson Booklet %%BOOK%%\\\\[-1pt]{\\normalfont\\headingfont\\scriptsize %%RANGE%%}', book_tag)
         .replace('Lesson Booklet %%BOOK%% \\textbullet\\ %%RANGE%% \\textbullet\\ Year 7', rng)
         .replace('covers/particle-model.jpg', 'covers/forces.jpg')
         .replace('\\renewcommand{\\arraystretch}{1.45}', '\\renewcommand{\\arraystretch}{1.12}')
         .replace('The Particle Model}', '%s}' % title)
         .replace('VC2S8U05 \\textbullet\\ VC2S8I01--I08 \\textbullet\\ VC2S8H01', vc))
    a = f.index('\\begin{infobox}{How this booklet works}'); b = f.index('\\end{infobox}', a) + len('\\end{infobox}')
    f = f[:a] + how + f[b:]
    assert '%%' not in f and 'particle-model.jpg' not in f and 'Particle' not in f, f[:400]
    return f


def words_of(t):
    t = re.sub(r'%.*', '', t)
    return re.findall(r'[A-Za-z]{4,}', t)


def prep(b):
    b = fit_pictures(tabspec(b))
    return b.replace('\\thead{Acceleration}', '\\thead{\\scriptsize Acceleration}').replace('\\thead{Projectile?}', '\\thead{\\scriptsize Projectile?}')


HOW_AT = r"""\begin{infobox}{How this booklet works}
One section for each lesson. Each opens with its key vocabulary, then:\par\smallskip
\renewcommand{\arraystretch}{1.25}
\begin{tabular}{@{}p{24mm}p{70mm}@{}}
\textbf{Part A} & a reading with comprehension questions \\
\textbf{Part B} & the ideas, worked through \\
\textbf{Part C} & practice on your own \\
\end{tabular}

\smallskip
\begin{tabular}{@{}p{24mm}p{70mm}@{}}
\textbf{I do} \tagicon{\icodots{1}} & your teacher works an example (solid frame) \\
\textbf{We do} \tagicon{\icodots{2}} & you try one together (dashed frame) \\
\textbf{Reading} \tagicon{\icoread} & a passage to read (thin frame) \\
\end{tabular}

\smallskip
Two lesson books. The five experiments are in the \textbf{Experiment Booklet}, and the trebuchet investigation has its own booklet. Finished your lesson work and want to go further? Ask your teacher about \textbf{Advanced Forces}.
\end{infobox}"""

HOW_ADV = r"""\begin{infobox}{How this booklet works}
\textbf{Advanced Forces} goes deeper into the ideas of the lesson books: more powerful models, the mathematics behind them, and harder problems that bring several ideas together. Each topic builds on the lessons named under its title. Each opens with its key vocabulary, then:\par\smallskip
\renewcommand{\arraystretch}{1.25}
\begin{tabular}{@{}p{24mm}p{70mm}@{}}
\textbf{Part A} & a reading with comprehension questions \\
\textbf{Part B} & the deeper idea, worked through \\
\textbf{Part C} & practice on your own \\
\textbf{Part D} & a challenge that pulls the ideas together \\
\end{tabular}

\smallskip
\begin{tabular}{@{}p{24mm}p{70mm}@{}}
\textbf{I do} \tagicon{\icodots{1}} & a worked example (solid frame) \\
\textbf{We do} \tagicon{\icodots{2}} & you try one with help (dashed frame) \\
\textbf{Reading} \tagicon{\icoread} & a passage to read (thin frame) \\
\end{tabular}
\end{infobox}"""


def build(book, keep):
    words = []
    body = ''
    for num in keep:
        core, _ = split_d(num)
        b = at_level(prep(balanced(core, num)))
        body += '\\setcounter{section}{%d}\\renewcommand{\\lessonart}{%d}\n' % (num - 1, num) + b
    body = label_vocab_all(body, words)
    rows = []
    for n in range(1, 18):
        if n in MOVED:
            rows.append('  %d & \\textit{%s} & {\\footnotesize Experiment Booklet} \\\\ \\hline' % (n, MOVED[n]))
        elif n in LATER:
            rows.append('  %d & \\textit{%s} & {\\footnotesize Trebuchet booklet} \\\\ \\hline' % (n, LATER[n]))
        elif n in ADVANCED:
            rows.append('  %d & \\textit{%s} & {\\footnotesize Advanced Forces} \\\\ \\hline' % (n, ADVANCED[n]))
        elif n in keep:
            rows.append('  %d & \\hyperlink{lesson.%d.1}{%s} & \\hyperlink{lesson.%d.1}{p.\\ \\pageref{sec:%d}} \\\\ \\hline' % (n, n, titles[n], n, n))
        else:
            other = [b for b, ls in BOOKS.items() if n in ls][0]
            rows.append('  %d & %s & Book %d \\\\ \\hline' % (n, titles[n], other))
    rng = 'Lessons %s' % ', '.join(map(str, keep))
    front = front_common(rows, 'Lesson Booklet %d\\\\[-1pt]{\\normalfont\\headingfont\\scriptsize %s}' % (book, rng),
                         'Lesson Booklet %d \\textbullet\\ %s \\textbullet\\ Year 7' % (book, rng), 'Forces and Motion', HOW_AT,
                         'VC2S8U13 \\textbullet\\ VC2S8U14 \\textbullet\\ VC2S8U15 \\textbullet\\ VC2S8I01--I08')
    out = pre + style + '\\begin{document}\n' + front + body + glossary(words) + '\n\\end{document}\n'
    nocomment = re.sub(r'(?<!\\)%.*', '', body)
    for bad in ('yr8box', 'exttask', 'Above level', 'above level', 'Year 8', 'ptional'):
        assert bad not in nocomment, (book, bad)
    open(OUT % book, 'w', encoding='utf-8').write(full_width(out))
    missing = set(w for num in keep for w in words_of(split_d(num)[0])) - set(words_of(out))
    if missing:
        sys.exit('lost words: %s' % sorted(missing)[:20])
    print('wrote', os.path.basename(OUT % book), '-', len(keep), 'lessons,', len(words), 'glossary words')


def whole_lesson(n, topic, extra_from):
    """An old optional lesson as an Advanced topic: drop its own banner, codes and
    optional note; add the Part D questions of lesson extra_from to its practice."""
    b = blocks[n]
    b = b[b.index('\\vocabhead'):]
    b = re.sub(r'\\optionalnote\{[^\n]*\}\n', '', b)
    i = b.index('\\lessonpart{D}')
    core, dpart = b[:i], b[i:]
    dpart = re.sub(r'\\lessonpart\{D\}\{[^}]*\}', '\\\\lessonpart{D}{Challenge}', dpart, count=1)
    dpart = re.sub(r'\\begin\{yr8box\}\s*.*?\n\s*\n(\\medskip\s*)?', '', dpart, count=1, flags=re.S)
    dpart = dpart.replace('\\end{yr8box}', '').replace('\\exttask', '\\task')
    _, extra = split_d(extra_from)
    more = ('\\needspace{6\\baselineskip}\\par\\medskip{\\headingfont\\bfseries\\large More practice}\\par\\smallskip\n' + extra + '\n')
    b = core + more + dpart
    b = re.sub(r'\\ref\{task:%d\.(\d+)\}' % n, lambda m: '\\ref{task:%d.%s}' % (topic, m.group(1)), b)
    assert 'yr8box' not in b and 'ptional' not in b, n
    return b


def build_advanced(abook, topics):
    src = open(ADV_SRC, encoding='utf-8').read()
    # one chunk per topic, each starting at its \setcounter{section}
    starts = [m.start() for m in re.finditer(r'^\\setcounter\{section\}\{(\d+)\}', src, re.M)]
    chunks = {i + 1: src[a:(starts[i + 1] if i + 1 < len(starts) else len(src))] for i, a in enumerate(starts)}
    assert sorted(chunks) == sorted(TOPICS), sorted(chunks)
    src = ''.join(chunks[t] for t in topics)
    src = re.sub(r'%%PARTD:(\d+)%%', lambda m: split_d(int(m.group(1)))[1], src)
    src = src.replace('%%LESSON:11%%', whole_lesson(11, 6, 9)).replace('%%LESSON:14%%', whole_lesson(14, 7, 12))
    assert not re.search(r'%%[A-Z]+:\d+%%', src)
    body = prep(balanced(src, 'advanced'))
    words = []
    body = label_vocab_all(body, words)
    rows = []
    for t, (ti, dl) in TOPICS.items():
        if t in topics:
            rows.append('  %d & \\hyperlink{lesson.%d.1}{%s} & %s & \\hyperlink{lesson.%d.1}{p.\\ \\pageref{sec:%d}} \\\\ \\hline' % (t, t, ti, dl, t, t))
        else:
            other = [b for b, v in ADV_BOOKS.items() if t in v][0]
            rows.append('  %d & \\textit{%s} & %s & Book %d \\\\ \\hline' % (t, ti, dl, other))
    rng = 'Topics %d--%d' % (min(topics), max(topics))
    front = front_common(rows, 'Advanced Forces %d\\\\[-1pt]{\\normalfont\\headingfont\\scriptsize %s}' % (abook, rng),
                         'Book %d \\textbullet\\ %s \\textbullet\\ Above the Year 7 level' % (abook, rng), 'Advanced Forces', HOW_ADV,
                         'VC2S8U13--U15 \\textbullet\\ VC2S10U15 \\textbullet\\ VC2S10U17')
    front = front.replace('\\begin{tabular}{|C{1.1cm}|L{6.0cm}|C{2.4cm}|}\n  \\hline\\thead{Lesson} & \\thead{Title} & \\thead{Page} \\\\ \\hline',
                          '\\begin{tabular}{|C{1.1cm}|L{5.2cm}|C{1.7cm}|C{1.4cm}|}\n  \\hline\\thead{Topic} & \\thead{Title} & \\thead{Deepens lesson} & \\thead{Page} \\\\ \\hline')
    front = front.replace('  --- & \\hyperlink{glossary}{Glossary} & \\hyperlink{glossary}{\\pageref{sec:glossary}} \\\\ \\hline',
                          '  --- & \\hyperlink{glossary}{Glossary} & & \\hyperlink{glossary}{\\pageref{sec:glossary}} \\\\ \\hline')
    assert 'Deepens lesson' in front
    sty = style.replace('{FORCES AND MOTION}', '{ADVANCED FORCES}').replace('{Forces and Motion}', '{Advanced Forces}').replace('LESSON', 'TOPIC')
    out = (pre.replace('{FORCES AND MOTION}', '{ADVANCED FORCES}').replace('\\newcommand{\\unitname}{Forces and Motion}', '\\newcommand{\\unitname}{Advanced Forces}')
           + sty + '\\begin{document}\n' + front + body + '\n' + glossary(words) + '\n\\end{document}\n')
    nocomment = re.sub(r'(?<!\\)%.*', '', body)
    for bad in ('yr8box', 'exttask', 'ptional', 'Year 8 extension'):
        assert bad not in nocomment, bad
    open(OUT_ADV % abook, 'w', encoding='utf-8').write(full_width(out))
    print('wrote', os.path.basename(OUT_ADV % abook), '-', len(topics), 'topics,', len(words), 'glossary words')
    return out


def check_advanced(outs):
    every = ''.join(outs)
    moved = [split_d(n)[1] for n in (1, 2, 4, 5, 7, 9, 12)] + [whole_lesson(11, 6, 9), whole_lesson(14, 7, 12)]
    missing = set(w for t in moved for w in words_of(t)) - set(words_of(every))
    if missing:
        sys.exit('advanced lost words: %s' % sorted(missing)[:20])

for book, keep in BOOKS.items():
    build(book, keep)
check_advanced([build_advanced(b, t) for b, t in ADV_BOOKS.items()])
