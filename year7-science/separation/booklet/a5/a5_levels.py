"""At-level and Advanced lesson books (faculty decision, 25 Nov 2026).

Every student completes the at-level lesson books; students who excel move on
to the Advanced book for the unit ("Advanced Ecosystems" ...), whose topics are
deeper elaborations of the at-level lessons, not more of the same work, and
which is never labelled optional. The A4 masters keep their Part D (above
level); this module takes it out of the A5 lesson books and hands it to the
Advanced book, where it becomes practice inside the topic that deepens that
lesson. Forces was the pilot (its make_a5.py does the same job its own way).

    at, parts = split_levels(out)          # after a unit's make_a5 has built a book
    build_advanced(...)                    # once per Advanced book

Used by the Particle Model, Separation, Ecosystems, Science Skills and Water
Resources make_a5.py, which share the Particle Model master's macros.
"""
import re, os, sys

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
%%BOOKS%% Finished your lesson work and want to go further? Ask your teacher about \textbf{%%ADV%%}.
\end{infobox}"""

HOW_ADV = r"""\begin{infobox}{How this booklet works}
\textbf{%%ADV%%} goes deeper into the ideas of the lesson books: more powerful models, the reasoning behind them, and harder problems that bring several ideas together. Each topic builds on the lessons named under its title. Each opens with its key vocabulary, then:\par\smallskip
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

BAD_AT = ('yr8box', 'exttask', 'Above level', 'above level', 'Year 8', 'optionalnote', 'lessonpart{D}')
BAD_ADV = ('yr8box', 'exttask', 'optionalnote', 'Year 8', 'above level', 'Above level')


def nocomment(t):
    return re.sub(r'(?<!\\)%.*', '', t)


def words_of(t):
    return re.findall(r'[A-Za-z]{4,}', nocomment(t))


def _end_of_part(out, i):
    ends = [out.find(s, i) for s in ('\n\\setcounter{section}', '\n% ═', '\\clearpage\\markboth{Glossary}')]
    return min(e for e in ends if e > 0)


def _lesson_at(out, i):
    sc = list(re.finditer(r'\\setcounter\{section\}\{(\d+)\}', out[:i]))
    if sc:
        return int(sc[-1].group(1)) + 1
    return int(re.findall(r'\\label\{sec:(\d+)\}', out[:i])[-1])


def d_tasks(d):
    """A Part D as plain practice: no banner, no Year 8 box, extensions as tasks."""
    d = re.sub(r'\\lessonpart\{D\}\{[^}]*\}\{[^}]*\}(\\label\{ext:\d+\})?\s*', '', d)
    d = re.sub(r'\\begin\{yr8box\}\s*.*?\n\s*\n(\\medskip\s*)?', '', d, count=1, flags=re.S)
    d = d.replace('\\end{yr8box}', '').replace('\\newpage', '').replace('\\clearpage', '').replace('\\exttask', '\\task')
    d = re.sub(r'(?m)^% ─+ PART D ─+\s*$', '', d)
    assert 'yr8box' not in d and 'lessonpart' not in d, d[:300]
    return d.strip() + '\n'


def split_levels(out, books_line, adv):
    """Take every Part D out of a built at-level book. Returns the book and
    {lesson number: its Part D as practice tasks}."""
    pre, sep, body = out.partition('\n\\begin{document}')
    parts = {}
    while True:
        i = body.find('\\lessonpart{D}')
        if i < 0:
            break
        # the Part D comment rule above it goes too
        head = body[:i].rstrip()
        last = head.rsplit('\n', 1)[-1]
        a = len(head) - len(last) if last.startswith('% ─') else i
        e = body.index('\\end{yr8box}', i) + len('\\end{yr8box}')
        tail = body[e:_end_of_part(body, e)]
        assert re.sub(r'\\(newpage|clearpage)|\s', '', nocomment(tail)) == '' or 'Final reflection' in tail, tail[:300]
        n = _lesson_at(body, i)
        assert n not in parts, n
        parts[n] = d_tasks(body[i:e])
        body = body[:a].rstrip() + '\n\\newpage\n' + body[e:]
    body = re.sub(r' \\textbullet\{\} VC2S\d+[A-Z]\d+(--[A-Z]?\d+)? \(above level\)', '', body)
    body = re.sub(r'\\textbullet\{\} *VC2S\d+[A-Z]\d+ *\(above level\) *\\textbullet\{\} ', r'\\textbullet{} ', body)
    a = body.index('\\begin{infobox}{How this booklet works}')
    b = body.index('\\end{infobox}', a) + len('\\end{infobox}')
    body = body[:a] + HOW_AT.replace('%%BOOKS%%', books_line).replace('%%ADV%%', adv) + body[b:]
    nc = nocomment(body)
    for bad in BAD_AT:
        assert bad not in nc, ('at-level book still has', bad, nc[nc.index(bad) - 200:nc.index(bad) + 100])
    return pre + sep + body, parts


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


def label_vocab(body, words):
    out, pos = [], 0
    for m in re.finditer(r'\\vocabhead', body):
        bend = body.find('\\end{ctab}', m.start())
        v = body[m.start():bend]
        def lab(mm):
            w = mm.group(2); slug = re.sub(r'[^a-z0-9]+', '-', w.lower()).strip('-')
            if any(s_ == slug for _, s_ in words):
                return mm.group(0)
            words.append((w, slug))
            return mm.group(1) + '\\label{voc:%s}' % slug + mm.group(3)
        out.append(body[pos:m.start()]); out.append(re.sub(r'(\\textbf\{([^}\\]+)\})(\}?\s*&)', lab, v)); pos = bend
    out.append(body[pos:])
    return ''.join(out)


def balanced(t, what):
    for env in set(re.findall(r'\\begin\{(\w+)\}', t)) | set(re.findall(r'\\end\{(\w+)\}', t)):
        assert t.count('\\begin{%s}' % env) == t.count('\\end{%s}' % env), (what, env)
    return t


def topic_chunks(src):
    starts = [m.start() for m in re.finditer(r'^\\setcounter\{section\}\{(\d+)\}', src, re.M)]
    return {i + 1: src[a:(starts[i + 1] if i + 1 < len(starts) else len(src))] for i, a in enumerate(starts)}


def build_advanced(*, here, pre, style, front_tpl, adv_src, topics, books, out_pattern, parts,
                   unit, adv, cover, vc, fit, full_width, extra=None, front_fix=None):
    """topics = {t: (title, 'lessons it deepens')}; books = {book: [topics]};
    parts = {lesson: Part D practice}; extra = {placeholder: text}.
    Every Part D must land in some Advanced book; fails if a word of one is lost."""
    src_all = open(os.path.join(here, adv_src), encoding='utf-8').read()
    for k, v in (extra or {}).items():
        assert k in src_all, k
        src_all = src_all.replace(k, v)
    chunks = topic_chunks(src_all)
    assert sorted(chunks) == sorted(topics), (sorted(chunks), sorted(topics))
    used = set(int(n) for n in re.findall(r'%%PARTD:(\d+)%%', src_all))
    assert used == set(parts), ('Part D placed', sorted(used), 'Part D found', sorted(parts))
    sty = style
    for a, b in ((unit, adv), (unit.upper(), adv.upper())):
        sty = sty.replace('{%s}' % a, '{%s}' % b)
    sty = sty.replace('LESSON', 'TOPIC')
    pre2 = pre
    for a, b in ((unit, adv), (unit.upper(), adv.upper())):
        pre2 = pre2.replace('\\newcommand{\\unitname}{%s}' % a, '\\newcommand{\\unitname}{%s}' % b)
        pre2 = pre2.replace('\\newcommand{\\unitcaps}{%s}' % a, '\\newcommand{\\unitcaps}{%s}' % b)
        pre2 = pre2.replace('{%s — Lesson Booklet}' % a, '{%s}' % b)
    outs = []
    for abook, tlist in books.items():
        src = ''.join(chunks[t] for t in tlist)
        src = re.sub(r'%%PARTD:(\d+)%%', lambda m: parts[int(m.group(1))], src)
        assert not re.search(r'%%[A-Z]+(:\d+)?%%', src), re.search(r'%%[A-Z]+(:\d+)?%%', src).group(0)
        body = fit(balanced(src, adv))
        words = []
        body = label_vocab(body, words)
        rows = []
        for t, (ti, dl) in topics.items():
            if t in tlist:
                rows.append('  %d & \\hyperlink{lesson.%d.1}{%s} & %s & \\hyperlink{lesson.%d.1}{p.\\ \\pageref{sec:%d}} \\\\ \\hline' % (t, t, ti, dl, t, t))
            else:
                other = [b for b, v in books.items() if t in v][0]
                rows.append('  %d & \\textit{%s} & %s & Book %d \\\\ \\hline' % (t, ti, dl, other))
        rng = 'Topics %d--%d' % (min(tlist), max(tlist)) if len(tlist) > 1 else 'Topic %d' % tlist[0]
        tag = ('%s %d' % (adv, abook)) if len(books) > 1 else adv
        f = (front_fix or (lambda x: x))(front_tpl)
        f = (f.replace('%%CONTENTS%%', '\n'.join(rows))
             .replace('Lesson Booklet %%BOOK%%\\\\[-1pt]{\\normalfont\\headingfont\\scriptsize %%RANGE%%}',
                      '%s\\\\[-1pt]{\\normalfont\\headingfont\\scriptsize %s}' % (tag, rng))
             .replace('Lesson Booklet %%BOOK%% \\textbullet\\ %%RANGE%% \\textbullet\\ Year 7',
                      ('Book %d \\textbullet\\ ' % abook if len(books) > 1 else '') + '%s \\textbullet\\ Above the Year 7 level' % rng)
             .replace('covers/particle-model.jpg', cover)
             .replace('The Particle Model}', '%s}' % adv)
             .replace('VC2S8U05 \\textbullet\\ VC2S8I01--I08 \\textbullet\\ VC2S8H01', vc))
        a = f.index('\\begin{infobox}{How this booklet works}'); b = f.index('\\end{infobox}', a) + len('\\end{infobox}')
        f = f[:a] + HOW_ADV.replace('%%ADV%%', adv) + f[b:]
        f = f.replace('\\begin{tabular}{|C{1.1cm}|L{6.0cm}|C{2.4cm}|}\n  \\hline\\thead{Lesson} & \\thead{Title} & \\thead{Page} \\\\ \\hline',
                      '\\begin{tabular}{|C{1.1cm}|L{5.2cm}|C{1.7cm}|C{1.4cm}|}\n  \\hline\\thead{Topic} & \\thead{Title} & \\thead{Deepens lesson} & \\thead{Page} \\\\ \\hline')
        f = f.replace('  --- & \\hyperlink{glossary}{Glossary} & \\hyperlink{glossary}{\\pageref{sec:glossary}} \\\\ \\hline',
                      '  --- & \\hyperlink{glossary}{Glossary} & & \\hyperlink{glossary}{\\pageref{sec:glossary}} \\\\ \\hline')
        assert 'Deepens lesson' in f and '%%' not in f and cover in f, f[:500]
        out = pre2 + sty + '\\begin{document}\n' + f + body + '\n' + glossary(words) + '\n\\end{document}\n'
        nc = nocomment(body)
        for bad in BAD_ADV:
            assert bad not in nc, (adv, bad, nc[nc.index(bad) - 200:nc.index(bad) + 100])
        path = out_pattern % abook if '%d' in out_pattern else out_pattern
        open(path, 'w', encoding='utf-8').write(full_width(out))
        print('wrote', os.path.basename(path), '-', len(tlist), 'topics,', len(words), 'glossary words')
        outs.append(out)
    every = set(words_of(''.join(outs)))
    missing = set(w for d in parts.values() for w in words_of(d)) - every
    if missing:
        sys.exit('%s lost words: %s' % (adv, sorted(missing)[:20]))
    return outs
