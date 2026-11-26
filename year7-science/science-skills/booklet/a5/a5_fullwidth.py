"""Full-width questions for the A5 lesson books (Kodie, 25 Nov 2026).

On an A5 page the A4 masters' side-by-side layouts leave each question about
5.7 cm wide, which is too narrow to write in. make_a5.py passes the finished
book through full_width() before writing it:

  * \\taskpair, \\ptpair and \\pqpair are redefined (after the master preamble,
    before \\begin{document}) to stack their two questions, each full width.
    The Particle-family masters pass a box height; the Forces-family masters
    pass a keyed \\abox/\\wbox call. Which one applies is read off the preamble.
  * A figure set beside its answer box (We do: spring scale, syringe, particle
    diagrams) becomes the figure centred above a full-width box.
  * Three drawing boxes in a row (Advanced Forces skydiver) are stacked.

The A4 masters are untouched. full_width() asserts nothing side by side is left.
"""
import re

STACK_PARTICLE = r"""
% ── A5: every question full page width (stacked, never side by side) ───────
\renewcommand{\taskpair}[4]{%
  \par\needspace{6\baselineskip}\vspace{2pt}%
  \task #1\par\vspace{2pt}\answerbox{#2}%
  \par\needspace{6\baselineskip}%
  \task #3\par\vspace{2pt}\answerbox{#4}\par\vspace{2pt}}
\renewcommand{\ptpair}[6]{%
  \pt{#1}#2\par\answerbox{#3}%
  \pt{#4}#5\par\answerbox{#6}}
"""

STACK_FORCES = r"""
% ── A5: every question full page width (stacked, never side by side) ───────
\renewcommand{\taskpair}[4]{%
  \par\needspace{6\baselineskip}\vspace{2pt}%
  \task #1\par\vspace{2pt}#2%
  \par\needspace{6\baselineskip}%
  \task #3\par\vspace{2pt}#4\par\vspace{2pt}}
\renewcommand{\ptpair}[6]{%
  \pt{#1}#2\par#3%
  \pt{#4}#5\par#6}
"""

STACK_PQ = r"""\renewcommand{\pqpair}[4]{%
  \needspace{4\baselineskip}\vspace{5pt}%
  \stepcounter{pqnum}\noindent\textbf{\thepqnum.}\quad #1\par\vspace{2pt}
  \begin{tcolorbox}[enhanced,arc=2mm,colback=Paper,colframe=Line,left=2mm,right=2mm,
    top=1mm,bottom=1mm,boxrule=1pt,height=#2]\end{tcolorbox}
  \stepcounter{pqnum}\noindent\textbf{\thepqnum.}\quad #3\par\vspace{2pt}
  \begin{tcolorbox}[enhanced,arc=2mm,colback=Paper,colframe=Line,left=2mm,right=2mm,
    top=1mm,bottom=1mm,boxrule=1pt,height=#4]\end{tcolorbox}}
"""

# Figure beside its answer: \noindent<mp fig>\hfill\n<mp box(es)>, closing a We do.
FIG_BOX = re.compile(
    r'\\par\\smallskip\\noindent\n'
    r'\\begin\{minipage\}\[c\]\{0\.\d+\\linewidth\}(?:\\centering)?(?P<fig>.*?)\\end\{minipage\}\\hfill\n'
    r'\\begin\{minipage\}\[c\]\{0\.\d+\\linewidth\}\n?(?P<box>.*?)\n?\\end\{minipage\}(?=\n\\end\{wedo\})',
    re.S)

# Three drawing boxes in a row, grouped so fill grows them together.
DRAW_ROW = re.compile(
    r'\\edef\\abgrp\{\\number\\numexpr\\value\{abox\}\+1\\relax\}%\n'
    r'\\noindent(?P<row>(?:\\begin\{minipage\}\[t\]\{0\.\d+\\linewidth\}\\drawk\{[^\n]*?\\end\{minipage\}(?:\\hfill)?\n?)+)'
    r'\\par\\gdef\\abgrp\{0\}')
DRAWK_IN = re.compile(r'\\begin\{minipage\}\[t\]\{0\.\d+\\linewidth\}(\\drawk\{.*?)\\end\{minipage\}')


def full_width(out):
    pre, sep, body = out.partition('\n\\begin{document}')
    assert sep, 'no \\begin{document}'
    add = ''
    if '\\newcommand{\\taskpair}' in pre:
        tp = pre.split('\\newcommand{\\taskpair}', 1)[1][:600]
        add += STACK_PARTICLE if '\\answerbox{#2}' in tp else STACK_FORCES
    if '\\newcommand{\\pqpair}' in pre:
        add += STACK_PQ
    body = FIG_BOX.sub(lambda m: '\\par\\smallskip\n\\begin{center}' + m['fig'].strip()
                       + '\\end{center}\n' + m['box'].strip(), body)
    body = DRAW_ROW.sub(lambda m: '\n'.join('\\par\\noindent' + d
                        for d in DRAWK_IN.findall(m['row'])) + '\\par', body)
    left = [l for l in body.split('\n')
            if re.search(r'\\begin\{minipage\}\[[ct]\]\{0\.\d+\\linewidth\}', l)]
    assert not left, 'side-by-side layout left in book:\n' + '\n'.join(left)
    return pre + add + sep + body
