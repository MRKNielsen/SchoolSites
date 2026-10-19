#!/usr/bin/env python3
"""Build year7-science/space/rubric.html from the bio-ecosystems rubric
engine plus the Space CAT 5 data.

The engine is data-driven (STRANDS / CRITERIA / PARTS / DEFAULT_BANDS), so
this swaps those blocks and the unit-specific copy, and leaves the marking,
comment, grouping and print code untouched. Every replacement asserts it
matched exactly once, so a change to the bio engine surfaces here rather
than producing a silently half-converted file.

**This page is NOT staff-gated** (Kodie's call, 19 Oct 2026). It was, for
about a day, and every content fix then cost a decrypt / edit / re-encrypt /
paste round that could not be checked until after it shipped — four of them,
three for defects that a look at the rendered page would have caught in
seconds. The marks and student names live in the teacher's browser, never in
the page; what the lock protected was the criteria and band descriptors.
bio-ecosystems/rubric.html is ungated too, since 8 Oct.

So this writes the finished page directly rather than a `*-payload.html` for
staff-crypt. If it is ever gated again, bring back the shell from git
(`rubric.html` at 62a193d) and have this emit the payload again — and read
the v2 note in CLAUDE.md first, because the shell that shipped on 19 Oct
used the older single-layer unlock and could not open a v2 blob.
"""
import os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from space_rubric_data import STRANDS, CRITERIA, PARTS

REPO = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    "year7-science")

# The page the tool is wrapped in. tokens.css carries the palette the tool's
# own style block maps onto; sitenav + favicon go on every page type per
# CLAUDE.md. No solutions.css — that was only ever there for the lockscreen.
PAGE_HEAD = '''<!DOCTYPE html>
<html lang="en-AU">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Astronomy Test &mdash; Rubric &amp; Report Generator | Year 7 Space</title>
<meta name="robots" content="noindex, nofollow">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Bitter:wght@500;700;800&family=Source+Sans+3:ital,wght@0,400;0,600;0,700;1,400&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../../assets/css/tokens.css">
<link rel="stylesheet" href="../../assets/css/sitenav.css">
<script src="../../assets/js/sitenav.js" defer></script>
<link rel="icon" href="../../assets/icons/favicon.svg" type="image/svg+xml">
<link rel="icon" href="../../assets/icons/favicon.ico" sizes="32x32">
<link rel="apple-touch-icon" href="../../assets/icons/apple-touch-icon.png">
<link rel="manifest" href="../../site.webmanifest">
<meta name="theme-color" content="#24576f">
</head>
<!-- data-nosearch keeps the tool out of assets/js/searchindex.js. Its visible
     text is the CAT 5 mark scheme in outline, and the grid is rebuilt by JS
     anyway, so what the indexer would capture is a static shell rather than
     what anyone actually sees — the same reason the orbit/season/binomial/
     lever widgets are excluded. Delete the attribute and rebuild the sitemap
     to make it searchable. -->
<body class="rubric-page theme-space" data-nosearch>
'''

PAGE_FOOT = '''
</body>
</html>
'''

# Sample class for the Demo button: six students across the band range, with a
# couple of not-attempted marks so the "worst part" and grouping logic have
# something to show. Band array is one value per strand, s1..s6, in order.
DEMO_FN = '''function demo(){
  state.meta = {cls:"7C", teacher:"Mr K Nielsen", task:"Astronomy Test (CAT 5)", date:"Term 4, 2026"};
  const rows = [
    ["Ava Chen","she",      [3,3,4,3,3,2]],
    ["Ben Novak","he",      [2,2,2,2,2,2]],
    ["Charlie Doust","they",[1,2,1,1,1,1]],
    ["Divya Rao","she",     [4,3,3,4,2,3]],
    ["Eli Marsh","he",      [2,1,3,2,3,1]],
    ["Frankie Hale","they", [3,4,3,3,3,3]]
  ];
  state.students = rows.map(r => {
    const st = newStudent(r[0], r[1]);
    /* a few questions left blank, so the completion line has something to say */
    if(r[0] === "Charlie Doust"){ st.q.Q11b = "x"; st.q.Q7dii = "x"; st.q.Q4d = "x"; }
    if(r[0] === "Eli Marsh"){ st.q.Q10 = "x"; }
    STRANDS.forEach((sd,i) => {
      const target = Math.min(r[2][i], maxBandOf(sd));
      for(let b=1;b<=target;b++) EV[sd.id][b].forEach(id => { if(st.q[id] !== "x") st.q[id] = true; });
    });
    recompute(st); regenerate(st,true);
    return st;
  });
}
'''
SRC  = os.path.join(REPO, "bio-ecosystems/rubric-payload.html")
DST  = os.path.join(REPO, "space/rubric.html")


def block(text, name, opener):
    """Span of `const NAME = [ ... ]`, brace-balanced."""
    m = re.search(r"const\s+" + name + r"\s*=\s*" + re.escape(opener), text)
    assert m, f"{name} not found"
    close = {"[": "]", "{": "}"}[opener]
    i = m.end() - 1
    d = 0
    instr = None
    j = i
    while j < len(text):
        ch = text[j]
        if instr:
            if ch == "\\":
                j += 2
                continue
            if ch == instr:
                instr = None
        elif ch in "\"'":
            instr = ch
        elif ch == opener:
            d += 1
        elif ch == close:
            d -= 1
            if d == 0:
                return m.start(), j + 1
        j += 1
    raise AssertionError(f"{name} unbalanced")


def swap_const(text, name, opener, new_literal):
    a, b = block(text, name, opener)
    return text[:a] + f"const {name} = " + new_literal + text[b:]


def span_of(text, start_literal, end_literal):
    """[start, end) of a run from a literal to the first end-literal after it.

    The start literal MUST be unique. It was not, once: `const rows = [`
    appears three times in bio's payload, this matched the first (inside
    exportCSV) and the splice deleted ~12,600 characters through to the end
    of demo() — persist, restore, demo, the CSV import/export and the file
    handling all went with it. The page then threw "restore is not defined"
    on boot and rendered chrome with no marking grid.
    """
    n = text.count(start_literal)
    assert n == 1, (f"start literal matched {n} times, expected 1 — pick a "
                    f"unique anchor: {start_literal[:60]!r}")
    a = text.index(start_literal)
    b = text.find(end_literal, a)
    assert b != -1, f"end not found after {start_literal[:50]}"
    return a, b + len(end_literal)


def function_span(text, name):
    """[start, end) of `function NAME(...){ ... }`, by brace balance.

    Safer than matching the closing literal, which depends on indentation
    that is not unique anywhere in this file.
    """
    m = re.search(r"\nfunction\s+" + re.escape(name) + r"\s*\(", text)
    assert m, f"function {name} not found"
    i = text.index("{", m.end() - 1)
    d, j, instr = 0, i, None
    while j < len(text):
        ch = text[j]
        if instr:
            if ch == "\\":
                j += 2
                continue
            if ch == instr:
                instr = None
        elif ch in "\"'`":
            instr = ch
        elif ch == "{":
            d += 1
        elif ch == "}":
            d -= 1
            if d == 0:
                return m.start() + 1, j + 1
        j += 1
    raise AssertionError(f"function {name} unbalanced")


def sub1(text, pat, rep, flags=0, what="", expect=1):
    out, n = re.subn(pat, rep, text, flags=flags)
    assert n == expect, f"{what or pat!r} matched {n} times, expected {expect}"
    return out


def main():
    t = open(SRC, encoding="utf-8").read()
    orig_len = len(t)

    # NB: the Space data blocks are spliced in LAST, after the blanket
    # booklet/investigation wording replacements below. Doing it the other way
    # round rewrote a legitimate reference in the Space feedback text ("the AU
    # column in the booklet table" became "on the test table") — the booklet is
    # a real thing a student can open, and that line was already correct.

    # ---- drop the per-student species, which Space has no equivalent of
    a, b = block(t, "SPECIES", "[")
    t = t[:a] + 'const SPECIES = [];   /* Space has no per-student artefact */' + t[b:]
    t = sub1(t, r'\n *if\(parts\[1\]\) st\.species = matchSpecies\(parts\[1\]\);',
             '', what="roll species column")
    t = sub1(t, r'if\(parts\[2\]\) st\.pron =', 'if(parts[1]) st.pron =',
             what="roll pronoun column")

    # ---- save format: this is a new tool, so start its versioning clean
    t = sub1(t, r'const SAVE_VERSION = \d+;', 'const SAVE_VERSION = 1;',
             what="SAVE_VERSION")

    # ---- namespace the autosave key -----------------------------------
    # bio's key is "ecosystem-rubric:v1". Left as-is, a teacher with both
    # rubrics open in one browser has them share a single localStorage slot
    # and silently overwrite each other's marks — the autosave is keyed by
    # tool, not by page, so same key means same data.
    t = sub1(t, re.escape('"ecosystem-rubric:v1"'), '"astronomy-rubric:v1"',
             what="autosave key", expect=2)
    a, b = block(t, "MIGRATIONS", "{")
    t = t[:a] + ('const MIGRATIONS = {};   /* v1 — no prior save format to migrate from */') + t[b:]

    # ---- unit-specific copy -----------------------------------------
    # task name appears in the default state, the loader default and the demo
    t = sub1(t, re.escape('task:"Ecosystem Investigation"'),
             'task:"Astronomy Test (CAT 5)"', what="meta task", expect=3)
    t = sub1(t, re.escape('teacher:"Mr K Nielsen", task:"Astronomy Test (CAT 5)", date:"Term 3, 2026"'),
             'teacher:"Mr K Nielsen", task:"Astronomy Test (CAT 5)", date:"Term 4, 2026"',
             what="demo term")

    reps = [
        (r'Ecosystem Investigation — rubric & report generator',
         'Astronomy Test (CAT 5) — rubric & report generator', 'doc comment'),
        (r'<h1>Ecosystem Investigation <em>— rubric &amp; report generator</em></h1>',
         '<h1>Astronomy Test <em>— CAT 5 rubric &amp; report generator</em></h1>', 'h1'),
        (r'<input id="f-task" value="Ecosystem Investigation">',
         '<input id="f-task" value="Astronomy Test (CAT 5)">', 'task field'),
        ('One per line. Add a species and pronoun after commas if you want them: <code>Ava Chen, Regent Honeyeater, she</code>',
         'One per line. Add a pronoun after a comma if you want one: <code>Ava Chen, she</code>',
         'roll help'),
        ('one column per booklet question, in booklet order',
         'one column per criterion, in test order', 'csv help'),
        ('CRITERIA — what the teacher actually ticks, in booklet order.',
         'CRITERIA — what the teacher actually ticks, in test order.', 'criteria comment'),
        # the masthead back-link still pointed at bio's unit by name
        ('&#8592; Biodiversity &amp; Ecosystems', '&#8592; Space', 'unit back link'),
        # the grid's own help text describes where the columns come from
        ('Columns follow the Student Booklet question by question. Where the '
         'rubric splits one question across two bands it appears as (i) and (ii) '
         'under that question number.',
         'Columns follow the Astronomy Test question by question. Where the '
         'rubric splits one question across two bands it appears as (i) and (ii) '
         'under that question number.', 'grid help text'),
        ('/* label a criterion the way the Student Booklet numbers it: "A3 (i)", "A4a" */',
         '/* label a criterion the way the test numbers it: "Q4b (i)", "Q7c (ii)" */',
         'qLabel comment'),
        ('the Year 7/8 Biodiversity & Ecosystems unit.', 'the Year 7 Space unit.', 'header blurb'),
    ]
    for pat, rep, what in reps:
        t = sub1(t, re.escape(pat), rep.replace("\\", "\\\\"), what=what)

    # ---- remaining unit wording, all plain substring work -------------
    for a, b in [("the whole booklet", "the whole test"),
                 ("in the booklet", "on the test"),
                 ("the booklet", "the test"),
                 ("this investigation", "this test"),
                 ("Across this investigation", "Across this test"),
                 # downloaded filenames: "7C-ecosystem-rubric-<date>.json"
                 # and "7C-ecosystem-marks-<date>.csv"
                 ("-ecosystem-rubric-", "-astronomy-rubric-"),
                 ("-ecosystem-marks", "-astronomy-marks")]:
        t = t.replace(a, b)

    # ---- strip the per-student species, UI and all -------------------
    # The field stays in the student object so save/load/CSV keep working
    # unchanged, but nothing writes to it and nothing shows it.
    t = sub1(t, re.escape('placeholder="Ava Chen, Regent Honeyeater, she&#10;Ben Novak, Greater Bilby, he&#10;Charlie Doust"'),
             'placeholder="Ava Chen, she&#10;Ben Novak, he&#10;Charlie Doust"',
             what="roll placeholder")
    t = sub1(t, re.escape('const seed = seedOf(st.name + "|" + st.species);'),
             'const seed = seedOf(st.name);', what="comment seed")
    t = sub1(t, re.escape('const sp = st.species ? "the " + st.species : "";'),
             'const sp = "";   /* no per-student artefact on a written test */',
             what="comment species lead")
    t = sub1(t, re.escape('''[s.name, s.species, s.pron].filter(Boolean).join(", ")'''),
             '[s.name, s.pron].filter(Boolean).join(", ")', what="roll serialise")
    # newStudent loses its species parameter, so every call site moves along one
    t = sub1(t, re.escape('function newStudent(name, species, pron){\n  const st = {id:uid(), name:name||"", species:species||"", pron:pron||"they",'),
             'function newStudent(name, pron){\n  const st = {id:uid(), name:name||"", species:"", pron:pron||"they",',
             what="newStudent signature")
    t = sub1(t, re.escape('newStudent(o.name||"", o.species||"", o.pron||"they")'),
             'newStudent(o.name||"", o.pron||"they")', what="newStudent load call")
    t = sub1(t, re.escape('''+"</span><br><span class='sp'>"+esc(st.species || "— no species —")+"</span></td>"'''),
             '+"</span></td>"', what="mark grid species line")
    t = sub1(t, re.escape("""     + (st.species ? '<span class="sp">'+esc(st.species)+'</span><br>' : '')"""),
             '', what="print sheet species")

    # the Species <select> on the Comments tab, and its handler
    a, b = span_of(t, "+ '<label class=\"field\"><span>Species</span><select id=\"c-species\">'", "join(\"\")")
    t = t[:a] + t[b:]
    t = sub1(t, r"\n *\+ \(st\.species && !SPECIES\.includes\(st\.species\).*?\n", "\n",
             flags=re.S, what="species select fallback")
    t = sub1(t, r'\n *\$\("#c-species"\)\.onchange[^\n]*\n', "\n", what="species select handler")

    # ---- print headings -----------------------------------------------
    t = sub1(t, re.escape('esc(m.task || "Ecosystem Investigation")'),
             'esc(m.task || "Astronomy Test (CAT 5)")', what="print task fallback")
    t = sub1(t, re.escape('Year 7 Science &middot; Ecosystem Investigation'),
             'Year 7 Science &middot; Space &middot; Astronomy Test (CAT 5)',
             what="sheet eyebrow")

    # ---- demo class: bio's rows carry species, 7 bands and bio criterion
    # ids, none of which exist here. Rewrite for Space's 6 strands.
    # Anchored on the function itself, not on `const rows = [` — see span_of.
    a, b = function_span(t, "demo")
    t = t[:a] + DEMO_FN + t[b:]

    # ---- rank strengths and next steps by weight as well as by band ----
    # bio ranks on band/maxBand alone, which is fine when every strand has the
    # same maxBand. Here s5 and s6 top out at 3, so band 2 scores 0.67 against
    # 0.50 for the four-band strands, and a student at band 2 across the board
    # is told their strengths are the two 3-mark questions. Scaling by the
    # square root of the strand weight restores the marks to the ranking
    # without letting the big strands swamp a genuinely strong small one.
    t = sub1(t, re.escape(
        '  const byHigh = [...scored].sort((x,y) => norm(y)-norm(x) || (y.weight||1)-(x.weight||1));\n'
        '  const byLow  = [...a].sort((x,y) => norm(x)-norm(y) || (y.weight||1)-(x.weight||1));'),
        '  const wnorm = s => norm(s) * Math.sqrt(s.weight || 1);\n'
        '  /* next steps rank on what is left to gain, not on the same scale as\n'
        '     strengths — otherwise a strand with a low maxBand is always both. */\n'
        '  const wgap  = s => (1 - norm(s)) * Math.sqrt(s.weight || 1);\n'
        '  const byHigh = [...scored].sort((x,y) => wnorm(y)-wnorm(x) || (y.weight||1)-(x.weight||1));\n'
        '  const byLow  = [...a].sort((x,y) => wgap(y)-wgap(x) || (y.weight||1)-(x.weight||1));',
        what="weighted strand ranking")

    # bio's Part D closer is keyed on strand s7, which Space has no equivalent
    # of — it would be dead code carrying bio's wording into an astronomy tool.
    a = t.index("    // Part D closer")
    b = t.index("      if(closers[b]) out.push(closers[b]);\n    }\n", a) + len("      if(closers[b]) out.push(closers[b]);\n    }\n")
    t = t[:a] + "    /* bio's Part D closer removed: CAT 5 has no single weighted part. */\n" + t[b:]

    # ---- data blocks, last (see the note at the top of main) ----------
    t = swap_const(t, "STRANDS", "[", STRANDS)
    t = swap_const(t, "CRITERIA", "[", CRITERIA)
    t = swap_const(t, "PARTS", "[", PARTS)

    hdr = ("<!-- GENERATED — do not edit this file.\n"
           "     Built from bio-ecosystems/rubric-payload.html by\n"
           "     tools/build_space_rubric.py; the data lives in\n"
           "     tools/space_rubric_data.py. The marking, comment, grouping and\n"
           "     print engine is shared with bio; only STRANDS, CRITERIA, PARTS\n"
           "     and the unit copy differ. Edit the data or the builder and\n"
           "     re-run it, then: node tools/test-space-rubric.js -->\n")
    tool = hdr + t
    page = PAGE_HEAD + tool + PAGE_FOOT

    os.makedirs(os.path.dirname(DST), exist_ok=True)
    open(DST, "w", encoding="utf-8", newline="").write(page)
    print(f"wrote {DST}")
    print(f"  tool {orig_len:,} -> {len(tool):,} chars, page {len(page.encode()):,} bytes")

    # the gated pair is retired — leave no stale payload for check-gated to
    # chase, and no stale encrypted page pretending to be the real one
    stale = os.path.join(REPO, "space/rubric-payload.html")
    if os.path.exists(stale):
        os.remove(stale)
        print("  removed the old rubric-payload.html (page is no longer gated)")

    t = page

    # ---- sanity checks ------------------------------------------------
    # Sweep for bio wording anywhere outside this builder's own header
    # comment. The back-link in the masthead read "← Biodiversity &
    # Ecosystems" in the first two builds — visible on screen, and missed
    # because the checks only looked for a handful of named strings.
    # slice past the generated header, whose own text names bio as the source
    MARK = "node tools/test-space-rubric.js -->"
    body = t[t.index(MARK) + len(MARK):]
    for word in ("Regent Honeyeater", "Ecosystem Investigation", "matchSpecies(parts",
                 "Biodiversity", "bio-ecosystems", "Student Booklet", "ecosystem"):
        assert word not in body, f"bio leftover in the payload body: {word!r}"
    assert "Astronomy Test" in body
    print("  no bio leftovers")

    # Every top-level function bio defines must survive, except the ones this
    # builder removes on purpose. Without this check a splice that swallows
    # neighbouring code is invisible until the page throws in front of a
    # class — which is exactly what happened on 19 Oct with `const rows = [`.
    def top_level_fns(src):
        js = src[src.index("<script>"):]
        return set(re.findall(r"\n\s*(?:async\s+)?function\s+([A-Za-z_$][\w$]*)", js))

    INTENTIONALLY_REMOVED = {"matchSpecies"}
    lost = (top_level_fns(open(SRC, encoding="utf-8").read())
            - top_level_fns(t) - INTENTIONALLY_REMOVED)
    assert not lost, ("a splice swallowed code — these functions vanished: "
                      + ", ".join(sorted(lost)))
    print(f"  all {len(top_level_fns(t))} engine functions intact")

    # The boot path must be able to find what it calls.
    for name in ("restore", "persist", "demo", "renderAll", "boot"):
        assert re.search(r"function\s+" + name + r"\s*\(", t), f"missing {name}()"
    print("  boot path intact (restore, persist, demo, renderAll, boot)")


if __name__ == "__main__":
    main()
