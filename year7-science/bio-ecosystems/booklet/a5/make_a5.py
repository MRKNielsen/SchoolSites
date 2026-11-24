#!/usr/bin/env python3
"""Build the 2027 A5 Biodiversity and Ecosystems lesson booklets (three books).

    cd year7-science/bio-ecosystems/booklet/a5
    python3 make_a5.py                 # writes Ecosystems_Lesson_Booklet_Yr7_A5_Book1..3.tex
    python3 fill_a5.py Ecosystems_Lesson_Booklet_Yr7_A5_Book1   (and 2, 3)

The lessons are written in eco-lessons-1/2/3.tex, in the 2027 lesson shape
(key vocabulary, Parts A-D). Their content is the A4 unit booklet's
(Bio_Ecosystems_Unit_Booklet_Yr7_8.tex), restructured; that master is not
read or changed. Lesson numbers follow the unit planner (planner-data.json):
the five labs share their theory lesson and are in the Experiment Booklet.

The preamble is the Particle Model lesson booklet's, so every Year 7 lesson
booklet shares one set of macros, and a5-style.tex is the same 2027 A5 style
the Particle Model and Separation books use. The cover art is placed by
../exp-cover.tex (covers/ecosystems.jpg).
"""
import re, os
HERE = os.path.dirname(os.path.abspath(__file__))
MASTER = os.path.join(HERE, '..', '..', '..', 'particle-model', 'booklet', 'Particle_Model_Lesson_Booklet_Yr7.tex')
OUT = os.path.join(HERE, 'Ecosystems_Lesson_Booklet_Yr7_A5_Book%d.tex')
TITLES = {1: 'Living or Non-living?', 2: 'Classification: Linnaean Levels', 3: 'Scientific Names and the Six Kingdoms',
          4: 'Dichotomous Keys', 5: 'Australian Ecosystems and Biodiversity', 6: 'Food Webs and Energy Flow',
          7: 'Ecosystem Services', 8: 'Adaptations', 9: 'Introduced Species', 10: 'Human Impacts on Ecosystems',
          11: 'Conservation and Action'}
LABS = {1: 'Is Yeast Alive?', 4: 'Key the Schoolyard', 5: 'Quadrat Survey', 8: 'Beaks and Food', 9: 'The Rabbit and Fox Model'}
BOOKS = {1: ([1, 2, 3, 4], 'eco-lessons-1.tex', 'Lessons 1--4 \\textbullet\\ Classifying life'),
         2: ([5, 6, 7, 8], 'eco-lessons-2.tex', 'Lessons 5--8 \\textbullet\\ How ecosystems work'),
         3: ([9, 10, 11], 'eco-lessons-3.tex', 'Lessons 9--11 \\textbullet\\ Threats and conservation')}

pre = open(MASTER, encoding='utf-8').read().split('\n\\begin{document}', 1)[0]
pre = pre.replace('\\documentclass[11pt,a4paper]{article}',
    '\\documentclass[11pt,a5paper,twoside]{article}\n\\newcommand{\\wrcoverfile}{../../../covers/ecosystems.jpg}'
    '\\newcommand{\\unitname}{Biodiversity and Ecosystems}\\newcommand{\\unitcaps}{BIODIVERSITY AND ECOSYSTEMS}')
pre, n = re.subn(r'\\usepackage\[a4paper[^\]]*\]\{geometry\}',
    r'\\usepackage[a5paper, inner=17mm, outer=13mm, top=19mm, bottom=17mm, headheight=14pt, headsep=4mm, footskip=8mm]{geometry}', pre)
assert n == 1
pre = pre.replace('Path=./fonts/', 'Path=../fonts/')
pre = pre.replace('{The Particle Model — Lesson Booklet}', '{Biodiversity and Ecosystems — Lesson Booklet}')
pre = pre.replace('\\usepackage{longtable}', '\\usepackage{longtable}\n\\usepackage{graphicx}\n\\usepackage{pifont}')
pre = pre[:pre.index('% ══════════════════════════════════════════════════════════════════════════════\n%  SHARED DIAGRAMS')] + '\\usetikzlibrary{patterns}\n'
style = open(os.path.join(HERE, 'a5-style.tex'), encoding='utf-8').read() + open(os.path.join(HERE, '..', 'exp-cover.tex'), encoding='utf-8').read()
style = style.replace('{The Particle Model}', '{Biodiversity and Ecosystems}').replace('{THE PARTICLE MODEL}', '{BIODIVERSITY AND ECOSYSTEMS}')


def build(book, lessons, src, rng):
    body = open(os.path.join(HERE, src), encoding='utf-8').read()
    body = body.replace('\\begin{tikzpicture}', '\\begin{fitbox}\\begin{tikzpicture}').replace('\\end{tikzpicture}', '\\end{tikzpicture}\\end{fitbox}')
    # glossary from the key vocabulary tables
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
    found = [int(x) for x in re.findall(r'\\label\{sec:(\d+)\}', body)]
    assert found == lessons, (book, found)

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
    for n in range(1, 12):
        lab_ = (' \\newline{\\footnotesize\\itshape + Lab: %s (Experiment Booklet)}' % LABS[n]) if n in LABS else ''
        if n in lessons:
            rows.append('  %d & \\hyperlink{lesson.%d.1}{%s}%s & \\hyperlink{lesson.%d.1}{p.\\ \\pageref{sec:%d}} \\\\ \\hline' % (n, n, TITLES[n], lab_, n, n))
        else:
            other = [b for b, v in BOOKS.items() if n in v[0]][0]
            rows.append('  %d & \\textit{%s}%s & Book %d \\\\ \\hline' % (n, TITLES[n], lab_, other))
    front = open(os.path.join(HERE, 'a5-front.tex'), encoding='utf-8').read()
    front = (front.replace('%%CONTENTS%%', '\n'.join(rows)).replace('%%BOOK%%', str(book)).replace('%%RANGE%%', rng.split(' \\textbullet')[0])
             .replace('covers/particle-model.jpg', 'covers/ecosystems.jpg')
             .replace('The Particle Model}', 'Biodiversity and Ecosystems}')
             .replace('VC2S8U05 \\textbullet\\ VC2S8I01--I08 \\textbullet\\ VC2S8H01',
                      'VC2S8U01 \\textbullet\\ VC2S8U04 \\textbullet\\ VC2S8I01--I08 \\textbullet\\ VC2S8H02--H04')
             )
    front = re.sub(r'\w+ lesson books?; experiments are in the \\textbf\{Experiment Booklet\}\.',
                   lambda m: 'Three lesson books. The five labs share a lesson and are in the \\textbf{Experiment Booklet}.', front)
    assert '%%' not in front and 'particle-model.jpg' not in front, front
    out = pre + style + '\\begin{document}\n' + front + body + '\n'.join(gloss) + '\n\\end{document}\n'
    open(OUT % book, 'w', encoding='utf-8').write(out)
    print('wrote', os.path.basename(OUT % book), '-', len(lessons), 'lessons,', len(words), 'glossary words')


for book, (lessons, src, rng) in BOOKS.items():
    if os.path.exists(os.path.join(HERE, src)):
        build(book, lessons, src, rng)
