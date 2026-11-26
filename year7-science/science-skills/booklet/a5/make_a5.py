#!/usr/bin/env python3
"""Build the 2027 A5 Science Skills and Safety lesson booklet.

    cd year7-science/science-skills/booklet/a5
    python3 make_a5.py                                   # writes Science_Skills_Lesson_Booklet_Yr7_A5.tex
    python3 fill_a5.py Science_Skills_Lesson_Booklet_Yr7_A5

The lessons are written in sss-lessons.tex (Lessons 1, 4 and 5; Lessons 2, 3
and 6 are practicals in the Experiment Booklet). The preamble is taken from
the Particle Model lesson booklet, so both units share one set of macros, and
the 2027 A5 workbook style (a5-style.tex) is the same file the Particle Model
A5 books use.
"""
from a5_fullwidth import full_width
import re, os
HERE = os.path.dirname(os.path.abspath(__file__))
MASTER = os.path.join(HERE, '..', '..', '..', 'particle-model', 'booklet', 'Particle_Model_Lesson_Booklet_Yr7.tex')
OUT = os.path.join(HERE, 'Science_Skills_Lesson_Booklet_Yr7_A5.tex')
TITLES = {1: 'What is Science?', 4: 'The Scientific Method', 5: 'Safety'}
MOVED = {2: 'Experiment 1 --- Exploring the Lab', 3: 'Experiment 2 --- Measuring Mass and Volume',
         6: 'Experiment 3 --- Measuring Temperature and Time'}
TEXT_W, COL_PAD = 11.8, 0.42

pre = open(MASTER, encoding='utf-8').read().split('\n\\begin{document}', 1)[0]
pre = pre.replace('\\documentclass[11pt,a4paper]{article}',
    '\\documentclass[11pt,a5paper,twoside]{article}\n\\newcommand{\\unitname}{Science Skills and Safety}\\newcommand{\\unitcaps}{SCIENCE SKILLS AND SAFETY}')
pre, n = re.subn(r'\\usepackage\[a4paper[^\]]*\]\{geometry\}',
    r'\\usepackage[a5paper, inner=17mm, outer=13mm, top=19mm, bottom=17mm, headheight=14pt, headsep=4mm, footskip=8mm]{geometry}', pre)
assert n == 1
pre = pre.replace('Path=./fonts/', 'Path=../fonts/')
pre = pre.replace('{The Particle Model — Lesson Booklet}', '{Science Skills and Safety — Lesson Booklet}')
pre = pre.replace('\\usepackage{longtable}', '\\usepackage{longtable}\n\\usepackage{graphicx}\n\\usepackage{pifont}')
# the Particle Model's diagram macros are not needed here
pre = pre[:pre.index('% ══════════════════════════════════════════════════════════════════════════════\n%  SHARED DIAGRAMS')] + '\\usetikzlibrary{patterns}\n'
style = open(os.path.join(HERE, 'a5-style.tex'), encoding='utf-8').read()
body = open(os.path.join(HERE, 'sss-lessons.tex'), encoding='utf-8').read()
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
         .replace('covers/particle-model.jpg', 'covers/science-skills.jpg')
         .replace('Lesson Booklet %%BOOK%%\\\\[-1pt]{\\normalfont\\headingfont\\scriptsize %%RANGE%%}', 'Lesson Booklet\\\\[-1pt]{\\normalfont\\headingfont\\scriptsize Lessons 1, 4 and 5}')
         .replace('Lesson Booklet %%BOOK%% \\textbullet\\ %%RANGE%% \\textbullet\\ Year 7', 'Lesson Booklet \\textbullet\\ Year 7')
         .replace('The Particle Model}', 'Science Skills and Safety}')
         .replace('VC2S8U05 \\textbullet\\ VC2S8I01--I08', 'VC2S8I01--I08')
         .replace('Three lesson books; experiments are in the \\textbf{Experiment Booklet}.',
                  'Lessons 2, 3 and 6 are practicals: they are in the \\textbf{Experiment Booklet}.'))
assert '%%' not in front
out = pre + style + '\\begin{document}\n' + front + body + '\n'.join(gloss) + '\n\\end{document}\n'
open(OUT, 'w', encoding='utf-8').write(full_width(out))
print('wrote', os.path.basename(OUT), '-', len(words), 'glossary words')
