#!/usr/bin/env python3
"""Build the 2027 A5 Water Cycle and Resources lesson booklet.

    cd year7-science/science-skills/booklet/a5
    python3 make_a5.py                                   # writes Water_Resources_Lesson_Booklet_Yr7_A5.tex
    python3 fill_a5.py Water_Resources_Lesson_Booklet_Yr7_A5

The lessons are written in wr-lessons.tex (Lessons 1, 3, 4 and 5; Lessons 2
and 6 are practicals in the Experiment Booklet). The cover art is placed
by ../wr-cover.tex (covers/water-resources.jpg). The preamble is taken from
the Particle Model lesson booklet, so both units share one set of macros, and
the 2027 A5 workbook style (a5-style.tex) is the same file the Particle Model
A5 books use.
"""
from a5_fullwidth import full_width
import re, os
HERE = os.path.dirname(os.path.abspath(__file__))
MASTER = os.path.join(HERE, '..', '..', '..', 'particle-model', 'booklet', 'Particle_Model_Lesson_Booklet_Yr7.tex')
OUT = os.path.join(HERE, 'Water_Resources_Lesson_Booklet_Yr7_A5.tex')
TITLES = {1: 'What is the Water Cycle?', 3: 'Resources', 4: 'Renewability and Sustainability', 5: 'Energy and Renewable Energy'}
MOVED = {2: 'Experiment 1 --- Water Cycle in a Bag', 6: 'Experiment 2 --- Household Energy Audit'}
TEXT_W, COL_PAD = 11.8, 0.42

pre = open(MASTER, encoding='utf-8').read().split('\n\\begin{document}', 1)[0]
pre = pre.replace('\\documentclass[11pt,a4paper]{article}',
    '\\documentclass[11pt,a5paper,twoside]{article}\n\\newcommand{\\wrcoverfile}{../../../covers/water-resources.jpg}\\newcommand{\\unitname}{Water Cycle and Resources}\\newcommand{\\unitcaps}{WATER CYCLE AND RESOURCES}')
pre, n = re.subn(r'\\usepackage\[a4paper[^\]]*\]\{geometry\}',
    r'\\usepackage[a5paper, inner=17mm, outer=13mm, top=19mm, bottom=17mm, headheight=14pt, headsep=4mm, footskip=8mm]{geometry}', pre)
assert n == 1
pre = pre.replace('Path=./fonts/', 'Path=../fonts/')
pre = pre.replace('{The Particle Model — Lesson Booklet}', '{Water Cycle and Resources — Lesson Booklet}')
pre = pre.replace('\\usepackage{longtable}', '\\usepackage{longtable}\n\\usepackage{graphicx}\n\\usepackage{pifont}')
# the Particle Model's diagram macros are not needed here
pre = pre[:pre.index('% ══════════════════════════════════════════════════════════════════════════════\n%  SHARED DIAGRAMS')] + '\\usetikzlibrary{patterns}\n'
style = open(os.path.join(HERE, 'a5-style.tex'), encoding='utf-8').read() + open(os.path.join(HERE, '..', 'wr-cover.tex'), encoding='utf-8').read()
body = open(os.path.join(HERE, 'wr-lessons.tex'), encoding='utf-8').read()
body = body.replace('\\begin{tikzpicture}', '\\begin{fitbox}\\begin{tikzpicture}').replace('\\end{tikzpicture}', '\\end{tikzpicture}\\end{fitbox}')

words = []
def lab(m):
    w = m.group(2); slug = re.sub(r'[^a-z0-9]+', '-', w.lower()).strip('-')
    if any(s == slug for _, s in words):
        return m.group(0)
    words.append((w, slug))
    return m.group(1) + '\\label{voc:%s}' % slug + m.group(3)
parts = body.split('\\vocabhead')
for i in range(1, len(parts)):
    e = parts[i].find('\\end{ctab}')
    parts[i] = re.sub(r'(\\textbf\{([^}\\]+)\})(\}?\s*&)', lab, parts[i][:e]) + parts[i][e:]
body = '\\vocabhead'.join(parts)

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
for n in range(1, 7):
    if n in MOVED:
        rows.append('  %d & \\textit{%s} & Experiment Booklet \\\\ \\hline' % (n, MOVED[n]))
    else:
        rows.append('  %d & \\hyperlink{lesson.%d.1}{%s} & \\hyperlink{lesson.%d.1}{p.\\ \\pageref{sec:%d}} \\\\ \\hline' % (n, n, TITLES[n], n, n))
front = open(os.path.join(HERE, 'a5-front.tex'), encoding='utf-8').read()
front = (front.replace('%%CONTENTS%%', '\n'.join(rows))
         .replace('\\node[anchor=north] at (current page.north) {\\includegraphics[width=\\paperwidth]{../../../covers/particle-model.jpg}};', '')
         .replace('\\thispagestyle{empty}\n', '\\thispagestyle{empty}\n\\wrcover\n', 1)
         .replace('Lesson Booklet %%BOOK%%\\\\[-1pt]{\\normalfont\\headingfont\\scriptsize %%RANGE%%}', 'Lesson Booklet\\\\[-1pt]{\\normalfont\\headingfont\\scriptsize Lessons 1, 3, 4 and 5}')
         .replace('Lesson Booklet %%BOOK%% \\textbullet\\ %%RANGE%% \\textbullet\\ Year 7', 'Lesson Booklet \\textbullet\\ Year 7')
         .replace('The Particle Model}', 'Water Cycle and Resources}')
         .replace('VC2S8U05 \\textbullet\\ VC2S8I01--I08 \\textbullet\\ VC2S8H01', 'VC2S8U09 \\textbullet\\ VC2S8U15 \\textbullet\\ VC2S8U16 \\textbullet\\ VC2S8H03')
         .replace('Three lesson books; experiments are in the \\textbf{Experiment Booklet}.',
                  'Lessons 2 and 6 are practicals: they are in the \\textbf{Experiment Booklet}.'))
assert '%%' not in front
out = pre + style + '\\begin{document}\n' + front + body + '\n'.join(gloss) + '\n\\end{document}\n'
open(OUT, 'w', encoding='utf-8').write(full_width(out))
print('wrote', os.path.basename(OUT), '-', len(words), 'glossary words')
