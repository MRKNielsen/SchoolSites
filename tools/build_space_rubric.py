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
  /* a few parts left blank, so the completion line has something to say */
  const skip = {"Charlie Doust":["Q11b","Q7dii","Q4d"], "Eli Marsh":["Q10"]};
  state.students = rows.map(r => {
    const st = newStudent(r[0], r[1]);
    STRANDS.forEach((sd,i) => {
      const target = Math.min(r[2][i], maxBandOf(sd));
      EVALL[sd.id].forEach(id => {
        if((skip[r[0]] || []).includes(id)) return;
        const mx = MAXOF[id], band = CRITERIA.find(c => c.id === id).band;
        /* full marks below the band reached, a pass at it, under half above it */
        st.q[id] = band < target ? mx : band === target ? Math.ceil(mx * PASS) : (mx >= 2 ? 0.5 : 0);
      });
    });
    return st;
  });
  refreshClass(); state.students.forEach(st => regenerate(st, true));
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
    """Replace, treating `rep` as a literal.

    A lambda, not a template string: re.sub parses backslashes in the
    replacement, so a `\\D` in injected JavaScript raised "bad escape \\D"
    rather than landing in the file.
    """
    out, n = re.subn(pat, lambda m: rep, text, flags=flags)
    assert n == expect, f"{what or pat!r} matched {n} times, expected {expect}"
    return out


# ===================================================================
# Marks instead of ticks (21 Oct 2026, Kodie's call)
# ===================================================================
# bio's grid takes a tick per criterion. Space's grid takes the MARK, out of
# the criterion's `max` from the paper:
#     blank  = not attempted      0 = attempted, nothing creditable
# The bands are still worked out from evidence: a criterion counts for its
# rubric cell once it earns at least PASS (half) of its marks.
#
# "Blank = not attempted" needs one guard, or a half-marked class reads as a
# class that skipped half the paper. A blank only counts as not attempted
# once the student has at least one mark AND somebody in the class has a mark
# in that column — so marking question-by-question down the class (Q1 for
# everyone, then Q2) and student-by-student both read correctly part way.
# That makes not-attempted a CLASS-level fact, so every edit recomputes every
# student (refreshClass); at 30 x 34 that is nothing.
#
# The grid's inputs are never re-rendered while a teacher types — only the
# Mark / Bands / Level cells and each input's colour are updated in place
# (refreshSummaries). Re-rendering the table on each keystroke or on blur
# destroys the input the teacher is tabbing into.

MARKS_SEMANTICS = r'''/* A mark is a number out of the criterion's `max` (from the paper), or blank.
     number — attempted; 0 is attempted with nothing creditable
     blank  — not attempted, once the student has a mark somewhere AND
              someone in the class has a mark in that column; until then it
              is simply not marked yet
   A criterion counts as demonstrated for its rubric cell once it earns at
   least PASS of its marks: 1/2 and 2/4 count, 1/3 does not. */
const PASS = 0.5;
const MAXOF = {}; CRITERIA.forEach(c => MAXOF[c.id] = c.max);
const MAX_TOTAL = CRITERIA.reduce((n,c) => n + c.max, 0);
const fmtMark = v => String(Math.round(v * 2) / 2);
const hasMark = (st, id) => typeof st.q[id] === "number";
const started = st => CRITERIA.some(c => hasMark(st, c.id));
let COLS_MARKED = new Set();
function refreshClass(){
  COLS_MARKED = new Set();
  state.students.forEach(st => CRITERIA.forEach(c => { if(hasMark(st, c.id)) COLS_MARKED.add(c.id); }));
  state.students.forEach(recompute);
}
const isDone   = (st, id) => hasMark(st, id) && st.q[id] > 0 && st.q[id] >= MAXOF[id] * PASS;
const isNotAtt = (st, id) => !hasMark(st, id) && COLS_MARKED.has(id) && started(st);
function rawTotal(st){ return CRITERIA.reduce((n,c) => n + (hasMark(st, c.id) ? st.q[c.id] : 0), 0); }
/* "", "1", "1.5", "1,5", "1½", "½" -> number | null (blank) | NaN (invalid) */
function parseMark(raw, max){
  let s = String(raw == null ? "" : raw).trim().replace(",", ".");
  if(s === "") return null;
  s = s.replace(/^½$/, "0.5").replace(/½$/, ".5");
  if(!/^(\d+(\.\d+)?|\.\d+)$/.test(s)) return NaN;
  const v = parseFloat(s);
  if(v < 0 || v > max || Math.abs(v * 2 - Math.round(v * 2)) > 1e-9) return NaN;
  return v;
}
'''

SET_MARK = r'''/* Store one mark. value: number, or null / "" for blank. Returns false (and
   stores nothing) when the value is not a half-mark step from 0 to max. */
function setMark(ri, ci, value){
  const st = state.students[ri], c = CRITERIA[ci];
  if(!st || !c) return false;
  const v = (value === null || value === "") ? null
          : typeof value === "number" ? value : parseMark(value, c.max);
  if(Number.isNaN(v) || (typeof v === "number" && Number.isNaN(parseMark(String(v), c.max)))) return false;
  if(v === null) delete st.q[c.id]; else st.q[c.id] = v;
  refreshClass();
  refreshSummaries();
  scheduleHeavy();
  return true;
}
/* typing in a cell: store as soon as it is valid, flag it while it is not */
function enterMark(inp){
  const ri = +inp.dataset.r, ci = +inp.dataset.c, c = CRITERIA[ci];
  const v = parseMark(inp.value, c.max);
  if(Number.isNaN(v)){
    inp.classList.add("bad");
    inp.title = qLabel(c) + " is out of " + fmtMark(c.max) + " — enter 0 to " + fmtMark(c.max) + " in half marks, or leave blank";
    return;
  }
  inp.classList.remove("bad"); inp.title = "";
  setMark(ri, ci, v);
}
/* leaving a cell that still holds an invalid entry puts the stored mark back */
function leaveMark(inp){
  if(!inp.classList.contains("bad")) return;
  const st = state.students[+inp.dataset.r], c = CRITERIA[+inp.dataset.c];
  toast(qLabel(c) + " is out of " + fmtMark(c.max) + " — that entry was not kept");
  inp.value = st && hasMark(st, c.id) ? fmtMark(st.q[c.id]) : "";
  inp.classList.remove("bad"); inp.title = "";
}
let heavyTimer = null;
function scheduleHeavy(){
  clearTimeout(heavyTimer);
  heavyTimer = setTimeout(() => {
    regenerateAll(false);
    renderComments(); renderGroups(); renderPrint(); persist(); renderMast();
  }, 350);
}'''

CELL_FNS = r'''function qinClass(st, c){
  return hasMark(st, c.id) ? (isDone(st, c.id) ? "on" : "low") : (isNotAtt(st, c.id) ? "no" : "");
}
function totHTML(st){
  return started(st) ? "<b>"+fmtMark(rawTotal(st))+"</b><span>/"+MAX_TOTAL+"</span>" : "<span>&middot;</span>";
}
function bandsHTML(st){
  return STRANDS.map(s => {
    const m = st.marks[s.id], r = st.res[s.id] || {};
    const ov = r.overridden;
    const tip = s.name + " — band " + (m===null ? 0 : m)
      + (r.missed ? " (top cell " + r.top + ", " + r.missed + " developing question" + (r.missed===1?"":"s") + " missing)" : "")
      + (ov ? " — overridden" : "");
    return "<span class='bnum b"+(m===null?"nil":m)+(ov?" ov":"")+(r.missed?" pen":"")+"' title='"+esc(tip)+"'>"
           +(m===null?"·":m)+"</span>";
  }).join("");
}
function lvlHTML(st){
  const pct = pctOf(st), lv = overallLevel(pct);
  return "<span class='chip b"+lv.key+"' title='"+esc(lv.name)+"'>"
       + (pct===null?"—":lv.mean.toFixed(1)) + "</span>";
}
/* update everything in the grid that a mark can change, without touching the
   inputs themselves (so focus and the caret survive) */
function refreshSummaries(){
  const t = $("#markTable");
  if(!t) return;
  state.students.forEach((st, ri) => {
    const a = t.querySelector("#tot-"+ri), b = t.querySelector("#bc-"+ri), l = t.querySelector("#lv-"+ri);
    if(a) a.innerHTML = totHTML(st);
    if(b) b.innerHTML = bandsHTML(st);
    if(l) l.innerHTML = lvlHTML(st);
  });
  t.querySelectorAll(".qcell .qin").forEach(inp => {
    const st = state.students[+inp.dataset.r], c = CRITERIA[+inp.dataset.c];
    if(!st || !c || inp.classList.contains("bad")) return;
    inp.className = "qin " + qinClass(st, c);
  });
  updateMarkTally();
}
function updateMarkTally(){
  const n = markedCount();
  const el = $("#tallyMark");
  if(el) el.textContent = state.students.length ? n + "/" + (state.students.length * CRITERIA.length) : "";
}
function renderMast(){
  $("#mastMeta").innerHTML = [
    esc([state.meta.cls, state.meta.teacher].filter(Boolean).join(" · ")) || "Set your class on the Class tab",
    esc(state.meta.date || ""),
    state.students.length ? state.students.length + " students · " + markedCount() + " marks entered" : ""
  ].filter(Boolean).join("<br>");
}

function renderMark(){'''

MARKS_CSS = '''
/* mark entry (Space): a number box per criterion, coloured by what it earns */
.qin{width:28px;height:24px;margin:4px auto;display:block;padding:0;box-sizing:border-box;
  text-align:center;font:inherit;font-size:13px;font-variant-numeric:tabular-nums;
  border:1px solid var(--rule-strong);border-radius:4px;background:var(--surface);color:var(--ink)}
.qin:hover{border-color:var(--myrtle)}
.qin:focus{outline:2px solid var(--myrtle);outline-offset:0;border-color:var(--myrtle)}
.qin.on{background:color-mix(in srgb, var(--myrtle) 18%, var(--surface));border-color:var(--myrtle);font-weight:700}
.qin.low{background:var(--surface);border-color:var(--ink-faint)}
.qin.no{background:var(--red-soft);border-color:var(--red)}
.qin.bad{outline:2px solid var(--red);outline-offset:0;background:var(--red-soft);color:var(--red)}
.legend .qin{display:inline-block;margin:0;width:22px;height:18px;font-size:11px;line-height:16px;vertical-align:middle}
th.qsub .qmax{display:block;font-style:normal;font-weight:400;font-size:10px;color:var(--ink-faint);margin-top:1px}
td.totcol,th.totcol{padding:6px 10px 6px 8px;min-width:66px;white-space:nowrap;text-align:right;border-left:2px solid var(--rule-strong);font-variant-numeric:tabular-nums}
th.totcol{font-size:10px;letter-spacing:.07em;text-transform:uppercase;color:var(--ink-soft)}
tr.hrow th.totcol{border-bottom:2px solid var(--rule-strong);vertical-align:bottom}
td.totcol b{font-size:13px} td.totcol span{font-size:11px;color:var(--ink-faint)}
td.bandcol{border-left:1px solid var(--rule)}
.ckmax{color:var(--ink-faint);font-size:.92em;white-space:nowrap}
'''


def check_marks():
    """Every criterion has a `max`; each strand's maxes sum to its weight;
    the paper sums to 50. Read from the data literals, so a typo in
    space_rubric_data.py fails the build rather than mis-weighting a strand."""
    crit = re.findall(r'\{id:"(\w+)".*?strand:"(s\d)".*?max:([\d.]+)\}', CRITERIA)
    n_rows = len(re.findall(r'\{id:"', CRITERIA))
    assert len(crit) == n_rows, f"{n_rows - len(crit)} criteria have no max"
    weights = dict(re.findall(r'id:"(s\d)", maxBand:\d, weight:(\d+)', STRANDS))
    tot = {}
    for _, s_id, mx in crit:
        tot[s_id] = tot.get(s_id, 0) + float(mx)
    for s_id, w in weights.items():
        assert tot.get(s_id) == float(w), f"strand {s_id}: criteria sum to {tot.get(s_id)}, weight is {w}"
    assert sum(tot.values()) == 50, f"paper sums to {sum(tot.values())}, not 50"
    print(f"  marks: {len(crit)} criteria, strands {'+'.join(str(int(tot[k])) for k in sorted(tot))} = 50")


def to_marks(t):
    """Swap the tick engine for mark entry. Every splice asserts it matched."""
    t = sub1(t, r"/\* A tick is one of three things:.*?const isNotAtt = \(st, id\) => st\.q\[id\] === \"x\";",
             MARKS_SEMANTICS.rstrip("\n"), flags=re.S, what="tick semantics")
    t = sub1(t, re.escape('function strandTouched(st, s){ return EVALL[s.id].some(id => st.q[id] !== undefined); }'),
             'function strandTouched(st, s){\n'
             '  return EVALL[s.id].some(id => hasMark(st, id))\n'
             '      || (started(st) && EVALL[s.id].some(id => COLS_MARKED.has(id)));\n}',
             what="strandTouched")
    t = sub1(t, re.escape("  return {done, notAtt, total: CRITERIA.length, worstPart: worst, byPart};"),
             "  return {done, notAtt, total: CRITERIA.length, worstPart: worst, byPart,\n"
             "          score: rawTotal(st), outOf: MAX_TOTAL};", what="tally score")

    # save format v2: values are numbers. v1 files held true / "x".
    t = sub1(t, r'const SAVE_VERSION = 1;', 'const SAVE_VERSION = 2;', what="SAVE_VERSION 2")
    t = sub1(t, re.escape('const MIGRATIONS = {};   /* v1 — no prior save format to migrate from */'),
             'const MIGRATIONS = {1:{}};   /* 1 → 2  ticks became marks: same ids, values converted in importJSON */',
             what="MIGRATIONS v1")

    # ---- grid ----------------------------------------------------------
    t = sub1(t, re.escape('''  h += "<th class='bandcol' rowspan='2'>Bands</th><th class='lvlcol' rowspan='2'>Level</th></tr>";'''),
             '''  h += "<th class='totcol' rowspan='2'>Mark</th><th class='bandcol' rowspan='2'>Bands</th><th class='lvlcol' rowspan='2'>Level</th></tr>";''',
             what="head totcol")
    t = sub1(t, re.escape('''       + (c.sub ? esc(c.sub) : "<span class='dot'>&middot;</span>") + "</th>";'''),
             '''       + (c.sub ? esc(c.sub) : "<span class='dot'>&middot;</span>")
       + "<span class='qmax'>/"+fmtMark(c.max)+"</span></th>";''', what="head max")
    t = sub1(t, re.escape('''  h += "<th colspan='2'></th></tr>";'''),
             '''  h += "<th colspan='3'></th></tr>";''', what="part row span")
    t = sub1(t, re.escape("\nfunction renderMark(){"), "\n" + CELL_FNS, what="cell helpers")
    t = sub1(t, re.escape('''      const v = st.q[c.id];
      const cls = v === true ? "on" : v === "x" ? "no" : "";
      const word = v === true ? "successful" : v === "x" ? "not attempted" : "not marked";
      h += "<td class='qcell p"+c.part+(first?" pstart":"")+"'>"
         + "<button type='button' class='qbtn "+cls+"' data-r='"+ri+"' data-c='"+ci+"'"
         + " aria-label='"+esc(st.name+" — "+qLabel(c)+" "+c.label+" — "+word)+"'></button></td>";'''),
             '''      const v = hasMark(st, c.id) ? fmtMark(st.q[c.id]) : "";
      h += "<td class='qcell p"+c.part+(first?" pstart":"")+"'>"
         + "<input type='text' inputmode='decimal' autocomplete='off' spellcheck='false' maxlength='4'"
         + " class='qin "+qinClass(st, c)+"' data-r='"+ri+"' data-c='"+ci+"' value='"+v+"'"
         + " aria-label='"+esc(st.name+" — "+qLabel(c)+" "+c.label+" — out of "+fmtMark(c.max))+"'></td>";''',
             what="cell input")
    a, b = span_of(t, "    const bands = STRANDS.map(s => {\n      const m = st.marks[s.id], r = st.res[s.id] || {};",
                   '''+ (pct===null?"—":lv.mean.toFixed(1)) + "</span></td></tr>";''')
    t = t[:a] + '''    h += "<td class='totcol' id='tot-"+ri+"'>"+totHTML(st)+"</td>";
    h += "<td class='bandcol' id='bc-"+ri+"'>"+bandsHTML(st)+"</td>";
    h += "<td class='lvlcol' id='lv-"+ri+"'>"+lvlHTML(st)+"</td></tr>";''' + t[b:]
    t = sub1(t, re.escape('''  t.querySelectorAll(".qcell .qbtn").forEach(btn => {
    btn.onclick = () => cycleTick(+btn.dataset.r, +btn.dataset.c);
    btn.onkeydown = e => gridKey(e, +btn.dataset.r, +btn.dataset.c);
  });

  const done = state.students.reduce((n,st) => n + CRITERIA.filter(c => isDone(st,c.id)).length, 0);
  $("#tallyMark").textContent = done + "/" + (state.students.length * CRITERIA.length);'''),
             '''  t.querySelectorAll(".qcell .qin").forEach(inp => {
    inp.oninput = () => enterMark(inp);
    inp.onblur = () => leaveMark(inp);
    inp.onfocus = () => inp.select();
    inp.onkeydown = e => gridKey(e, +inp.dataset.r, +inp.dataset.c);
  });
  updateMarkTally();''', what="grid wiring")
    a, b = function_span(t, "cycleTick")
    t = t[:a] + SET_MARK + t[b:]
    t = sub1(t, re.escape("/* click once = successful, twice = not attempted, three times = clear */\n"),
             "", what="cycleTick comment")
    # Enter goes down the column (marking one question for the whole class),
    # Shift+Enter back up. Arrows move between cells, as before.
    t = sub1(t, re.escape('''  else if(k === "ArrowLeft")  nc = MARK_COLS[Math.max(MARK_COLS.indexOf(ci)-1, 0)];
  else return;'''),
             '''  else if(k === "ArrowLeft")  nc = MARK_COLS[Math.max(MARK_COLS.indexOf(ci)-1, 0)];
  else if(k === "Enter") nr = e.shiftKey ? Math.max(ri-1, 0) : Math.min(ri+1, state.students.length-1);
  else return;''', what="Enter key")

    t = sub1(t, re.escape('''        <div><span class="qbtn on lg"></span> successful</div>
        <div><span class="qbtn no lg"></span> not attempted</div>
        <div><span class="qbtn lg"></span> not marked</div>'''),
             '''        <div><span class="qin on">2</span> half marks or more</div>
        <div><span class="qin low">0</span> under half</div>
        <div><span class="qin no"></span> blank &middot; not attempted</div>''', what="legend")
    t = sub1(t, re.escape('Click once for a successful answer, twice for not attempted, three times to clear. '
                          'Bands are worked out from the ticks: a cell counts only when every question behind it is done, '
                          'and each missing question below the top cell pulls the award down a band.'),
             'Type the mark for each part &mdash; the figure under each column is what it is out of, and half marks are fine '
             '(<code>1.5</code>). Enter <b>0</b> when a part was attempted but earned nothing, and leave it <b>blank</b> when it '
             'was not attempted. Enter moves down the column, the arrow keys move between cells. Bands are worked out from the '
             'marks: a part counts towards its rubric cell at half its marks or more, a cell counts only when every part behind '
             'it does, and each missing part below the top cell pulls the award down a band.', what="grid help")

    # ---- reference tab: say what each criterion is out of
    t = sub1(t, re.escape('''      h += "<li><span class='ckcode'>"+esc(qLabel(c))+"</span> "+esc(c.label)'''),
             '''      h += "<li><span class='ckcode'>"+esc(qLabel(c))+"</span> "+esc(c.label)
         + " <span class='ckmax'>("+fmtMark(c.max)+" mark"+(c.max===1?"":"s")+")</span>"''', what="crit key max")

    # ---- print sheet: the score, not a count of ticks
    t = sub1(t, re.escape('''     + '<span class="omean">'+tl.done+' of '+tl.total+' questions successful\''''),
             '''     + '<span class="omean">'+fmtMark(tl.score)+' / '+tl.outOf+' marks\'''', what="overall score")

    # ---- mast / tallies / copy
    t = sub1(t, re.escape('''function renderAll(){
  $("#mastMeta").innerHTML = [
    esc([state.meta.cls, state.meta.teacher].filter(Boolean).join(" · ")) || "Set your class on the Class tab",
    esc(state.meta.date || ""),
    state.students.length ? state.students.length + " students · " + markedCount() + " ticks" : ""
  ].filter(Boolean).join("<br>");'''),
             '''function renderAll(){
  refreshClass();
  renderMast();''', what="renderAll")
    t = sub1(t, re.escape('''    $("#mastMeta").innerHTML = [esc([state.meta.cls,state.meta.teacher].filter(Boolean).join(" · ")) || "Set your class on the Class tab",
      esc(state.meta.date||""), state.students.length ? state.students.length+" students · "+markedCount()+" ticks" : ""].filter(Boolean).join("<br>"); };'''),
             '''    renderMast(); };''', what="meta mast")
    for a, b2, what in [
        ('Export ticks as CSV', 'Export marks as CSV', 'csv button'),
        ('Clear every tick and override', 'Clear every mark and override', 'clear confirm'),
        ('so no ticks were set', 'so no marks were set', 'import toast'),
        ('Bands — worked out from the ticks and', 'Bands — worked out from the marks and', 'override label'),
        ('Put a 1 (or y) where the student was successful and an x where the question was not attempted.',
         'Each question column holds the mark, out of the figure in its heading; leave it blank where the part was not attempted.',
         'csv help'),
    ]:
        t = sub1(t, re.escape(a), b2, what=what)

    # ---- CSV out: the mark itself; headings carry the "out of"
    t = sub1(t, re.escape('    ...CRITERIA.map(c => qLabel(c)),\n'),
             '    ...CRITERIA.map(c => qLabel(c) + " /" + fmtMark(c.max)),\n', what="csv head")
    t = sub1(t, re.escape('''    ...CRITERIA.map(c => blank ? "" : (isDone(st,c.id) ? "1" : isNotAtt(st,c.id) ? "x" : "")),'''),
             '''    ...CRITERIA.map(c => blank || !hasMark(st,c.id) ? "" : fmtMark(st.q[c.id])),''', what="csv cells")
    # CSV in: numbers; y/✓ (a tick-era sheet) is full marks; x is blank
    t = sub1(t, re.escape('    const want = [norm(qLabel(c)), norm(c.id)];'),
             '    const want = [norm(qLabel(c) + " /" + fmtMark(c.max)), norm(qLabel(c)), norm(c.id)];', what="csv match")
    t = sub1(t, re.escape('''      if(/^(x|n|no|na|blank|not attempted|-)$/i.test(raw)) st.q[c.id] = "x";
      else if(TRUEY(raw)) st.q[c.id] = true;'''),
             '''      if(/^(x|n|no|na|blank|not attempted|-)$/i.test(raw)) return;
      const v = parseMark(raw, c.max);
      if(typeof v === "number" && !Number.isNaN(v)) st.q[c.id] = v;   /* NaN is a number too */
      else if(TRUEY(raw)) st.q[c.id] = c.max;
      else if(Number.isNaN(v)) badCells.push(name + " " + qLabel(c) + " (" + raw + ")");''', what="csv parse")
    t = sub1(t, re.escape('''  const anyQ = idxQ.some(i => i >= 0);
  const out = [];'''),
             '''  const anyQ = idxQ.some(i => i >= 0);
  const out = [], badCells = [];''', what="csv badCells")
    t = sub1(t, re.escape('''  state.students = out;
  renderAll(); persist();
  toast("Imported "+out.length'''),
             '''  state.students = out;
  refreshClass(); state.students.forEach(s => regenerate(s, false));
  renderAll(); persist();
  if(badCells.length) setTimeout(() => toast(badCells.length + " cell" + (badCells.length===1?"":"s")
    + " out of range and left blank: " + badCells.slice(0,3).join(", ") + (badCells.length > 3 ? "…" : "")), 2400);
  toast("Imported "+out.length''', what="csv refresh")

    # JSON in: v2 numbers as-is; v1 ticks -> true is full marks, "x" blank,
    # and a criterion left empty on a student who had any tick becomes 0 —
    # in the tick era an empty cell meant "attempted, not successful".
    t = sub1(t, re.escape('''    const mq = migrateTicks(o.q, fileVersion);
    Object.keys(mq).forEach(id => {
      if(!CRITERIA.some(c => c.id === id)) return;
      const v = mq[id];
      if(v === "x"){ if(st.q[id] !== true) st.q[id] = "x"; }
      else if(v) st.q[id] = true;
    });'''),
             '''    const mq = migrateTicks(o.q, fileVersion);
    Object.keys(mq).forEach(id => {
      if(!(id in MAXOF)) return;
      const v = mq[id];
      if(typeof v === "number"){ if(!Number.isNaN(parseMark(String(v), MAXOF[id]))) st.q[id] = v; }
      else if(v === true) st.q[id] = MAXOF[id];
    });
    if(fileVersion < 2 && Object.keys(mq).some(id => id in MAXOF))
      CRITERIA.forEach(c => { if(mq[c.id] === undefined) st.q[c.id] = 0; });''', what="json values")
    t = sub1(t, re.escape('''    if(!st.comment) regenerate(st,true);
    return st;
  });'''),
             '''    return st;
  });
  refreshClass(); state.students.forEach(s => { if(!s.comment) regenerate(s, true); });''', what="json refresh")

    t = sub1(t, re.escape("\ntd.qcell{width:30px;"), MARKS_CSS + "\ntd.qcell{width:30px;", what="marks css")
    return t


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
    # The pronoun moves from column 3 to column 2. The WHOLE line is replaced:
    # an earlier build swapped only the `if(parts[2])` guard and left the two
    # tests reading parts[2], so every pronoun typed into the roll came out
    # "they". bio's prefix tests also read "her" as "he" (/^(he|him)/ matches
    # "her"), so Space normalises through pronOf() with whole-word matches.
    t = sub1(t, re.escape('    if(parts[2]) st.pron = /^(he|him)/i.test(parts[2]) ? "he" : '
                          '/^(she|her)/i.test(parts[2]) ? "she" : "they";'),
             '    if(parts[1]) st.pron = pronOf(parts[1]);', what="roll pronoun column")
    t = sub1(t, re.escape("\nfunction applyRoll(){"),
             '\n/* "she", "her", "She/her" -> she; "he", "him", "his" -> he; anything else -> they */\n'
             'function pronOf(v){\n'
             '  const w = String(v || "").trim().toLowerCase().split(/[^a-z]+/)[0];\n'
             '  return ["she","her","hers"].includes(w) ? "she" : ["he","him","his"].includes(w) ? "he" : "they";\n'
             '}\nfunction applyRoll(){', what="pronOf helper")

    # ---- CSV: no Species column; pronouns land in the pronoun parameter --
    # bio's import called newStudent(name, species, pron). Space's newStudent
    # is (name, pron), so the species argument ("") was read as the pronoun
    # and every imported student became "they". An old file that still has a
    # Species column is fine: the column is simply ignored.
    t = sub1(t, re.escape('  const head = ["Name","Species","Pronoun",'),
             '  const head = ["Name","Pronoun",', what="csv head species")
    t = sub1(t, re.escape('    csvCell(st.name), csvCell(st.species), csvCell(st.pron),'),
             '    csvCell(st.name), csvCell(st.pron),', what="csv row species")
    t = sub1(t, re.escape('''    const st = newStudent(name,
      idxSp >= 0 ? matchSpecies((r[idxSp]||"").trim()) : "",
      idxPr >= 0 ? (r[idxPr]||"they").trim().toLowerCase() : "they");
    if(!["he","she","they"].includes(st.pron)) st.pron = "they";'''),
             '    const st = newStudent(name, idxPr >= 0 ? pronOf(r[idxPr]) : "they");',
             what="csv newStudent pronoun")
    t = sub1(t, re.escape('  const idxSp   = find(h => h.startsWith("species"));\n'), '', what="csv idxSp")

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
        t = sub1(t, re.escape(pat), rep, what=what)

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

    # ---- mark grid in paper order -------------------------------------
    # CRITERIA stays grouped by strand — that is what the printed rubric and
    # the reference table want, and what the band logic reads. The marking
    # grid alone is re-ordered to the paper's own sequence, Q1 to Q11, so
    # entering marks runs front to back through the script instead of
    # hopping between questions. data-c stays the true CRITERIA index, so
    # cycleTick() is untouched; only the headers and arrow-key movement
    # follow the display order.
    t = sub1(t, re.escape('const qLabel = c => c.q + (c.sub ? " (" + c.sub + ")" : "");'),
             '''const qLabel = c => c.q + (c.sub ? " (" + c.sub + ")" : "");

/* Column order for the marking grid only. Sorting by question number and
   then by criterion id reproduces the paper's order exactly, because the
   ids were written to run in paper order within each question — asserted
   in tools/test-space-rubric.js so a future renaming cannot break it
   silently. */
const qNum = c => parseInt(String(c.q).replace(/^\\D+/, ""), 10) || 0;
const MARK_COLS = CRITERIA.map((c, i) => i).sort((a, b) =>
  qNum(CRITERIA[a]) - qNum(CRITERIA[b]) ||
  (CRITERIA[a].id < CRITERIA[b].id ? -1 : CRITERIA[a].id > CRITERIA[b].id ? 1 : 0));''',
             what="MARK_COLS")

    # header row 1: question numbers, grouped over their sub-parts
    t = sub1(t, re.escape('''  let i = 0;
  while(i < CRITERIA.length){
    const c = CRITERIA[i];
    let n = 1;
    while(i + n < CRITERIA.length && CRITERIA[i+n].q === c.q) n++;
    const first = i === 0 || CRITERIA[i-1].part !== c.part;'''),
             '''  let i = 0;
  while(i < MARK_COLS.length){
    const c = CRITERIA[MARK_COLS[i]];
    let n = 1;
    while(i + n < MARK_COLS.length && CRITERIA[MARK_COLS[i+n]].q === c.q) n++;
    const first = i === 0 || CRITERIA[MARK_COLS[i-1]].part !== c.part;''',
             what="head row 1")

    # header row 2: the sub-part letters
    t = sub1(t, re.escape('''  CRITERIA.forEach((c,ci) => {
    const first = ci===0 || CRITERIA[ci-1].part !== c.part;
    h += "<th class='qsub p"'''),
             '''  MARK_COLS.forEach((ci,k) => {
    const c = CRITERIA[ci];
    const first = k===0 || CRITERIA[MARK_COLS[k-1]].part !== c.part;
    h += "<th class='qsub p"''',
             what="head row 2")

    # part row: parts are no longer contiguous in paper order, so emit one
    # group per run. Narrow runs show the letter, with the full name on hover.
    t = sub1(t, re.escape('''  PARTS.forEach(pt => {
    const n = CRITERIA.filter(c => c.part === pt.id).length;
    h += "<th class='pgroup p"+pt.id+"' colspan='"+n+"'>"+esc(pt.name)+"</th>";
  });'''),
             '''  let i = 0;
  while(i < MARK_COLS.length){
    const pid = CRITERIA[MARK_COLS[i]].part;
    let n = 1;
    while(i + n < MARK_COLS.length && CRITERIA[MARK_COLS[i+n]].part === pid) n++;
    const pt = PARTS.find(p => p.id === pid) || {id:pid, name:pid};
    h += "<th class='pgroup p"+pid+"' colspan='"+n+"' title='"+esc(pt.name)+"'>"
       + esc(n < 4 ? pt.id : pt.name) + "</th>";
    i += n;
  }''',
             what="part row runs")

    # the cell loop
    t = sub1(t, re.escape('''    CRITERIA.forEach((c,ci) => {
      const first = ci===0 || CRITERIA[ci-1].part !== c.part;
      const v = st.q[c.id];'''),
             '''    MARK_COLS.forEach((ci,k) => {
      const c = CRITERIA[ci];
      const first = k===0 || CRITERIA[MARK_COLS[k-1]].part !== c.part;
      const v = st.q[c.id];''',
             what="cell loop")

    # arrow keys follow the paper, not the strand grouping
    t = sub1(t, re.escape('''  else if(k === "ArrowRight") nc = Math.min(ci+1, CRITERIA.length-1);
  else if(k === "ArrowLeft") nc = Math.max(ci-1, 0);'''),
             '''  else if(k === "ArrowRight") nc = MARK_COLS[Math.min(MARK_COLS.indexOf(ci)+1, MARK_COLS.length-1)];
  else if(k === "ArrowLeft")  nc = MARK_COLS[Math.max(MARK_COLS.indexOf(ci)-1, 0)];''',
             what="arrow keys")

    # bio had four parts, so Part E inherited no colour
    t = sub1(t, re.escape('th.pgroup.pD{background:var(--part-d-bg);color:var(--part-d)}'),
             'th.pgroup.pD{background:var(--part-d-bg);color:var(--part-d)}\n'
             'th.pgroup.pE{background:var(--tint-soft);color:var(--ink-soft)}',
             what="part E colour")

    # ---- data blocks, last (see the note at the top of main) ----------
    t = swap_const(t, "STRANDS", "[", STRANDS)
    t = swap_const(t, "CRITERIA", "[", CRITERIA)
    t = swap_const(t, "PARTS", "[", PARTS)

    # ---- marks, not ticks (after the data, which carries each `max`) --
    check_marks()
    t = to_marks(t)

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

    INTENTIONALLY_REMOVED = {"matchSpecies", "cycleTick"}   # cycleTick -> setMark (marks, not ticks)
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
