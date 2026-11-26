#!/usr/bin/env python3
"""Build the 2027 A5 Particle Model lesson booklet from the A4 master.

    cd year7-science/particle-model/booklet/a5
    python3 make_a5.py                                  # writes Particle_Model_Lesson_Booklet_Yr7_A5.tex
    python3 fill_a5.py Particle_Model_Lesson_Booklet_Yr7_A5   # builds, grows boxes to fill pages

The master (../Particle_Model_Lesson_Booklet_Yr7.tex) is read, never changed.
What this does to it:
  * Six lessons, one for each theory lesson of the 2027 unit plan (Term 1
    Weeks 4-6), numbered as the plan numbers them. Lessons 3, 6 and 9 are the
    labs, in the Particle Model experiment booklet.
        1 States of Matter                     <- master Lesson 1
        2 What is a Scientific Model?          <- master Lesson 2
        4 The Particle Model                   <- master Lessons 4 + 5
        5 Changes of State                     <- master Lessons 7 + 8
        7 Expansion, Contraction and Diffusion <- master Lessons 10 + 11
        8 Density                              <- master Lessons 13 + 14
    Where two master lessons make one plan lesson, the lesson keeps the first
    one's reading (Part A) and both theory sections (Part B, numbered on);
    Part C keeps the first PRACTICE_PER_SOURCE tasks of each and Part D the
    first EXT_KEEP extensions of the first. Master Lessons 6 (Limits of the
    Model) and 12 (Gas Pressure) are optional in the plan and left out.
    Lessons 16-27 belong to the Separation unit.
  * Two books: Lessons 1-4 and Lessons 5-8.
  * A5 twoside with mirrored margins (copier booklet mode), padded with notes
    pages to a multiple of 4, after a glossary built from the key vocabulary.
  * The 2027 workbook style (as in the Space A5 trial and the experiment
    booklets): colour cover from the unit's cover art, black-and-white inside,
    Outfit headings, a lesson opener band with the lesson's ink symbol
    (../art/lN-ink.pdf, N = the first master lesson), and boxes told apart by
    frame and icon.
  * Any figure wider than the A5 text block is scaled down to fit it; any
    table wider than the text block has its column widths scaled to fit.
Fails if a word of a kept part is lost or an environment is cut in half.
"""
from a5_fullwidth import full_width
import re, sys, os

HERE = os.path.dirname(os.path.abspath(__file__))
MASTER = os.path.join(HERE, '..', 'Particle_Model_Lesson_Booklet_Yr7.tex')
OUT = os.path.join(HERE, 'Particle_Model_Lesson_Booklet_Yr7_A5_Book%d.tex')
# (plan lesson, title, master lessons)
PLAN = [(1, None, [1]), (2, None, [2]), (4, 'The Particle Model', [4, 5]),
        (5, 'Changes of State', [7, 8]), (7, 'Expansion, Contraction and Diffusion', [10, 11]),
        (8, 'Density', [13, 14])]
BOOKS = {1: [1, 2, 4], 2: [5, 7, 8]}
MOVED = {3: 'Experiment 1 --- Matter Has Mass and Takes Up Space',
         6: 'Experiment 2 --- A Cooling Curve',
         9: 'Experiment 3 --- Density by Displacement'}
PRACTICE_PER_SOURCE = 3
EXT_KEEP = 2
TEXT_W = 11.8          # cm: A5 148 mm less inner 17 + outer 13
COL_PAD = 0.42         # cm of \tabcolsep padding per column

src = open(MASTER, encoding='utf-8').read()
pre, rest = src.split('\n\\begin{document}', 1)

# ---- lessons ----------------------------------------------------------------
heads = [(m.start(), int(m.group(1))) for m in
         re.finditer(r'^% ═+\n%  LESSON (\d+) ', rest, re.M)]
blocks = {}
for i, (pos, n) in enumerate(heads):
    end = heads[i + 1][0] if i + 1 < len(heads) else rest.index('\\end{document}')
    blocks[n] = rest[pos:end]

# ---- preamble ---------------------------------------------------------------
pre = pre.replace('\\documentclass[11pt,a4paper]{article}', '\\documentclass[11pt,a5paper,twoside]{article}')
pre, n = re.subn(r'\\usepackage\[a4paper[^\]]*\]\{geometry\}',
                 r'\\usepackage[a5paper, inner=17mm, outer=13mm, top=19mm, bottom=17mm, headheight=14pt, headsep=4mm, footskip=8mm]{geometry}', pre)
assert n == 1, 'geometry'
pre = pre.replace('Path=./fonts/', 'Path=../fonts/')
pre = pre.replace('{The Particle Model — Lesson Booklet}', '{The Particle Model — Lesson Booklet (A5)}')
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


def fit_pictures(t):
    t = t.replace('\\begin{tikzpicture}', '\\begin{fitbox}\\begin{tikzpicture}')
    return t.replace('\\end{tikzpicture}', '\\end{tikzpicture}\\end{fitbox}')


def tabspec(t):
    # balanced-brace column spec after \begin{tabular}
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


# diagrams are defined in the preamble: fit their pictures too
dpos = pre.index('%  DIAGRAM DEFINITIONS')
pre = pre[:dpos] + fit_pictures(tabspec(pre[dpos:]))

style = open(os.path.join(HERE, 'a5-style.tex'), encoding='utf-8').read()

def parts_of(b):
    pos = {m.group(1): m.start() for m in re.finditer(r'\\lessonpart\{(\w)\}', b)}
    assert sorted(pos) == ['A', 'B', 'C', 'D'], pos
    return {'head': b[:pos['A']], 'A': b[pos['A']:pos['B']], 'B': b[pos['B']:pos['C']],
            'C': b[pos['C']:pos['D']], 'D': b[pos['D']:]}


def balanced(t, what):
    for env in set(re.findall(r'\\begin\{(\w+)\}', t)) | set(re.findall(r'\\end\{(\w+)\}', t)):
        assert t.count('\\begin{%s}' % env) == t.count('\\end{%s}' % env), (what, env)
    return t


def tasks(c, k):
    # intro + the first k tasks of a Part C
    starts = [m.start() for m in re.finditer(r'^(?:\\needspace\{[^}]*\}\n)?\\(?:task|taskpair)\b', c, re.M)]
    if len(starts) <= k:
        return c[:starts[0]], c[starts[0]:]
    return c[:starts[0]], balanced(c[starts[0]:starts[k]], 'tasks')


def exts(d, k):
    ends = [m.end() for m in re.finditer(r'\\end\{keepext\}', d)]
    if len(ends) <= k:
        return d
    return balanced(d[:ends[k - 1]] + '\n\n\\end{yr8box}\n\\newpage\n', 'ext')


def plan_lesson(num, title, srcs):
    if len(srcs) == 1:
        return blocks[srcs[0]], [blocks[srcs[0]]]
    p1, p2 = parts_of(blocks[srcs[0]]), parts_of(blocks[srcs[1]])
    head = p1['head']
    # one opener: the plan's title, both summaries
    m1 = re.search(r'\\sectiondiv\{([^}]*)\}\{(.*)\}\\label', p1['head'])
    m2 = re.search(r'\\sectiondiv\{([^}]*)\}\{(.*)\}\\label', p2['head'])
    bul = lambda t: t.split(' \\textbullet{} ')
    summary = ' \\textbullet{} '.join(bul(m1.group(2))[:2] + bul(m2.group(2))[:2])
    head = head.replace(m1.group(0), '\\sectiondiv{%s}{%s}\\label' % (title, summary))
    # both vocabulary lists in one table (the second's example row left blank)
    v2 = p2['head'][p2['head'].index('\\vocabhead'):]
    rows = re.findall(r'^  & .*\\\\ \\hline$', v2, re.M)
    rows = [re.sub(r'\\scaf\{(\\textbf\{[^}]*\})\} & \\scaf\{.*\} (\\\\ \\hline)$', r'\1 & \2', r) for r in rows]
    vend = head.index('\\end{tabular}', head.index('\\vocabhead'))
    head = head[:vend] + '\n'.join(rows) + '\n' + head[vend:]
    i1, t1 = tasks(p1['C'], PRACTICE_PER_SOURCE)
    _, t2 = tasks(p2['C'], PRACTICE_PER_SOURCE)
    b2 = p2['B'][p2['B'].index('\n') + 1:]       # theory without its Part B heading
    d1 = exts(p1['D'], EXT_KEEP)
    out = head + p1['A'] + p1['B'] + b2 + i1 + t1 + t2 + d1
    # cross-references between the two master lessons now point inside one lesson
    out = out.replace('This lesson is about melting and freezing; Lesson 8 covers the rest.', 'Melting and freezing come first; the rest follow.')
    return balanced(out, num), [p1['A'], p1['B'], b2, t1, t2, d1]


def build(book, keep):
  global words
  words = []
  body = []
  kept = []
  for num, title, srcs in PLAN:
      if num not in keep:
          continue
      b, pieces = plan_lesson(num, title, srcs)
      kept += pieces
      b = fit_pictures(tabspec(b))
      body.append('\\setcounter{section}{%d}\\renewcommand{\\lessonart}{%d}\n' % (num - 1, srcs[0]) + b)

  # ---- glossary from the key vocabulary tables -------------------------------
  words = []
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

  # ---- front matter ------------------------------------------------------------
  titles = {}
  for num, title, srcs in PLAN:
      titles[num] = (title or re.search(r'\\sectiondiv\{([^}]*)\}', blocks[srcs[0]]).group(1), srcs[0])
  rows = []
  for n in range(1, 10):
      if n in MOVED:
          rows.append('  %d & \\textit{%s} & Experiment Booklet \\\\ \\hline' % (n, MOVED[n]))
      elif n in keep:
          t, s0 = titles[n]
          rows.append('  %d & \\hyperlink{lesson.%d.1}{%s} & \\hyperlink{lesson.%d.1}{p.\\ \\pageref{sec:%d}} \\\\ \\hline' % (n, n, t, n, s0))
      else:
          other = [b for b, ls in BOOKS.items() if n in ls][0]
          rows.append('  %d & %s & Book %d \\\\ \\hline' % (n, titles[n][0], other))
  rng = 'Lessons %d--%d' % (min(keep), max(keep))
  front = (open(os.path.join(HERE, 'a5-front.tex'), encoding='utf-8').read()
           .replace('%%CONTENTS%%', '\n'.join(rows)).replace('%%BOOK%%', str(book)).replace('%%RANGE%%', rng))

  out = pre + style + '\\begin{document}\n' + front + ''.join(body) + '\n'.join(gloss) + '\n\\end{document}\n'
  open(OUT % book, 'w', encoding='utf-8').write(full_width(out))

  # ---- no word lost: every word of every kept lesson is still in the output ----
  def words_of(t):
      t = re.sub(r'%.*', '', t)
      return re.findall(r'[A-Za-z]{4,}', t)
  missing = set(w for p in kept for w in words_of(p)) - set(words_of(out))
  if missing:
      sys.exit('lost words: %s' % sorted(missing)[:20])
  print('wrote', os.path.basename(OUT % book), '-', len(keep), 'lessons,', len(words), 'glossary words')


for book, keep in BOOKS.items():
    build(book, keep)
