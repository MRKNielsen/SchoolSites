#!/usr/bin/env python3
"""Build the 2027 A5 Separation Technologies and Techniques lesson booklets.

The lessons come from the A4 Particle Model master (Lessons 16-27 moved to
this unit in 2027), which this script reads and never changes.

    cd year7-science/separation/booklet/a5
    python3 make_a5.py                                       # writes Book1 and Book2 .tex
    python3 fill_a5.py Separation_Lesson_Booklet_Yr7_A5_Book1 # builds, grows boxes to fill pages
    python3 fill_a5.py Separation_Lesson_Booklet_Yr7_A5_Book2

What this does to the master:
  * Master Lessons 16-21 and 25-27, in the 2027 teaching order, numbered by
    their slot in the unit (labs and CATs take the other slots; the labs are
    Experiments 1-9 in the Separation experiment booklet):
        Book 1: 1 Pure Substances (16), 2 Mixtures (17), 4 Classifying (18),
                5 Solute, Solvent and Solution (19), 7 Decanting, Filtration
                and Magnetic Separation (25)
        Book 2: 8 Evaporation and Crystallisation (26), 10 Solubility and
                Saturation (20), 12 Solubility Curves (21), 16 Distillation
                and Chromatography (27)
    Evaporation and Crystallisation now comes before Solubility and
    Saturation, so its two uses of "saturated" get a short gloss.
    Master Lessons 22-24 are the old experiments, now in the experiment booklet.
  * A5 twoside with mirrored margins (copier booklet mode), padded with notes
    pages to a multiple of 4, after a glossary built from the key vocabulary.
  * The 2027 workbook style (as in the Space A5 trial and the experiment
    booklets): colour cover from the unit's cover art, black-and-white inside,
    Outfit headings, a lesson opener band with the lesson's ink symbol
    (../art/lN-ink.pdf), and boxes told apart by frame and icon.
  * Any figure wider than the A5 text block is scaled down to fit it; any
    table wider than the text block has its column widths scaled to fit.
Fails if a word of a kept lesson is lost.
"""
from a5_fullwidth import full_width
import re, sys, os

HERE = os.path.dirname(os.path.abspath(__file__))
MASTER = os.path.join(HERE, '..', '..', '..', 'particle-model', 'booklet', 'Particle_Model_Lesson_Booklet_Yr7.tex')
OUT = os.path.join(HERE, 'Separation_Lesson_Booklet_Yr7_A5_Book%d.tex')
KEEP = [16, 17, 18, 19, 20, 21, 25, 26, 27]
# One A5 booklet of every lesson runs to ~170 pages, far more than a copier can
# fold and staple, so the lessons are printed as three books of 56-68 pages.
BOOKS = {1: [16, 17, 18, 19, 25], 2: [26, 20, 21, 27]}   # master lessons, in teaching order
# Lessons are numbered by their slot in the 2027 Separation unit (Term 2,
# Weeks 1-7, CATs not counted); the master's numbers (16-27) are kept only in
# labels and art file names.
PLANNUM = {16: 1, 17: 2, 18: 4, 19: 5, 25: 7, 26: 8, 20: 10, 21: 12, 27: 16}
MOVED = {3: 'Experiment 1 --- Solubility', 6: 'Experiment 2 --- Surface Area and Dissolving',
         9: 'Experiment 3 --- Fast and Slow Evaporation', 11: 'Experiment 4 --- Rates of Evaporation',
         13: 'Experiment 5 --- Solubility and Temperature', 14: 'Experiment 6 --- Growing Copper Sulfate Crystals (stretch)',
         15: 'Experiment 7 --- Filtration', 17: 'Experiment 8 --- Distillation', 18: 'Experiment 9 --- The Great Green Mix Up'}
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
pre = pre.replace('\\documentclass[11pt,a4paper]{article}', '\\documentclass[11pt,a5paper,twoside]{article}\n\\newcommand{\\unitname}{Separation Technologies and Techniques}\\newcommand{\\unitcaps}{SEPARATION}')
pre, n = re.subn(r'\\usepackage\[a4paper[^\]]*\]\{geometry\}',
                 r'\\usepackage[a5paper, inner=17mm, outer=13mm, top=19mm, bottom=17mm, headheight=14pt, headsep=4mm, footskip=8mm]{geometry}', pre)
assert n == 1, 'geometry'
pre = pre.replace('Path=./fonts/', 'Path=../fonts/')
pre = pre.replace('{The Particle Model — Lesson Booklet}', '{Separation Technologies and Techniques — Lesson Booklet}')
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

def build(book, keep):
  global words
  words = []
  body = []
  for n in keep:
      b = blocks[n]
      if n == 26:
          b = b.replace('A saturated solution left in a dish', 'A saturated solution (one holding as much solute as it can) left in a dish', 1)
      b = fit_pictures(tabspec(b))
      body.append('\\setcounter{section}{%d}\\renewcommand{\\lessonart}{%d}\n' % (PLANNUM[n] - 1, n) + b)

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
  titles = {n: re.search(r'\\sectiondiv\{([^}]*)\}', blocks[n]).group(1) for n in blocks}
  rows = []
  slot = {v: k for k, v in PLANNUM.items()}
  for p in range(1, 19):
      if p in MOVED:
          rows.append('  %d & \\textit{%s} & Experiment Booklet \\\\ \\hline' % (p, MOVED[p]))
          continue
      n = slot[p]
      if n in keep:
          rows.append('  %d & \\hyperlink{lesson.%d.1}{%s} & \\hyperlink{lesson.%d.1}{p.\\ \\pageref{sec:%d}} \\\\ \\hline' % (p, p, titles[n], p, n))
      else:
          other = [b for b, ls in BOOKS.items() if n in ls][0]
          rows.append('  %d & %s & Book %d \\\\ \\hline' % (p, titles[n], other))
  rng = 'Lessons 1--7' if book == 1 else 'Lessons 8--16'
  front = (open(os.path.join(HERE, 'a5-front.tex'), encoding='utf-8').read()
           .replace('%%CONTENTS%%', '\n'.join(rows)).replace('%%BOOK%%', str(book)).replace('%%RANGE%%', rng)
           .replace('covers/particle-model.jpg', 'covers/separation.jpg')
           .replace('{\\headingfont\\bfseries\\fontsize{22}{26}\\selectfont The Particle Model}', '{\\headingfont\\bfseries\\fontsize{16}{20}\\selectfont Separation Technologies and Techniques}')
           .replace('VC2S8U05 \\textbullet\\ VC2S8I01--I08 \\textbullet\\ VC2S8H01', 'VC2S8U05 \\textbullet\\ VC2S8U06 \\textbullet\\ VC2S8U07 \\textbullet\\ VC2S8I01--I08 \\textbullet\\ VC2S8H02')
           .replace('Three lesson books;', 'Two lesson books;'))
  front = front.replace('Two lesson books;', 'Two lesson books;')
  assert '%%' not in front and 'particle-model.jpg' not in front

  out = pre + style + '\\begin{document}\n' + front + ''.join(body) + '\n'.join(gloss) + '\n\\end{document}\n'
  open(OUT % book, 'w', encoding='utf-8').write(full_width(out))

  # ---- no word lost: every word of every kept lesson is still in the output ----
  def words_of(t):
      t = re.sub(r'%.*', '', t)
      return re.findall(r'[A-Za-z]{4,}', t)
  missing = set(w for n in keep for w in words_of(blocks[n])) - set(words_of(out))
  if missing:
      sys.exit('lost words: %s' % sorted(missing)[:20])
  print('wrote', os.path.basename(OUT % book), '-', len(keep), 'lessons,', len(words), 'glossary words')


for book, keep in BOOKS.items():
    build(book, keep)
