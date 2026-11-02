"""Build assets/js/vc2-curriculum.js from VCAA's Victorian Curriculum F-10
Version 2.0 scope-and-sequence charts (Word), for tools/rubric-builder.html.

    python3 tools/build-curriculum.py                 # reads tools/vcaa/*.docx
    python3 tools/build-curriculum.py a.docx b.docx   # or the files given
    python3 tools/build-curriculum.py --check         # exit 1 if the .js is stale

The charts are VCAA's, licensed CC BY-NC 3.0 AU, and are NOT committed: put
fresh copies in tools/vcaa/ (gitignored) when VCAA updates them. Current
versions, from each learning area's "Scope and sequence" tab:

  Science Levels 7-10 (01-06-2024)
    https://f10.vcaa.vic.edu.au/sites/default/files/2025/Science%20Levels%207%E2%80%9310_01-06-2024.docx
  Mathematics Levels 7-10A (28-07-2023)
    https://f10.vcaa.vic.edu.au/sites/default/files/2025/Mathematics%20Levels%207%E2%80%9310A_28-07-2023.docx

To add a learning area or Foundation-6, download its chart into tools/vcaa/
and re-run; add its subject id/name to SUBJECTS if the code letter is new.

Read straight from word/document.xml with the standard library (no
python-docx, in keeping with the repo's dependency-free tools). Three things
in the charts that a plain text dump gets wrong, and this handles:

  - Equations. "describe the relationship between pi and the circumference"
    stores the pi as an Office Math object, which python-docx's .text drops
    silently, leaving "between  and". Math runs are rendered in place, and
    a math delimiter (m:d) gets its brackets back: y = cos(x), not y = cosx.
  - Merged cells. Columns are found by summing gridSpan, so a description in
    a merged Levels 7-8 cell is attributed once, and vertically merged
    continuation cells (which are empty) are skipped. Duplicate codes fail
    the build.
  - Layout differs by area: Science gives strand / sub-strand as full-width
    rows and the achievement standard above the content descriptions;
    Mathematics gives one table per strand under a "Strand:" heading, with
    each level's achievement standard split across the strand tables (the
    Number part under Number …), which are joined back in document order.
    Both are read by the row labels, not by position.
"""
import json, re, sys, zipfile, glob, os, math
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "js", "vc2-curriculum.js")
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
M = "{http://schemas.openxmlformats.org/officeDocument/2006/math}"
SUBJECTS = {"S": ("science", "Science"), "M": ("mathematics", "Mathematics")}
ATTRIBUTION = ("Victorian Curriculum F–10 Version 2.0 content elements are © VCAA, "
               "licensed CC BY-NC 3.0 AU. The curriculum can be accessed at https://f10.vcaa.vic.edu.au.")
MIN_LEVEL = 5   # Levels 5-6 are kept as the "towards" standard for Level 7 / Levels 7-8
CODE = re.compile(r"^VC2[A-Z]{1,2}\d{1,2}A?[A-Z]{1,3}\d{2}$")


def math_text(el):
    """Office Math -> plain text. m:d restores its brackets."""
    if el.tag == M + "t":
        return el.text or ""
    if el.tag == M + "d":
        pr = el.find(M + "dPr")
        beg = pr.find(M + "begChr").get(M + "val") if pr is not None and pr.find(M + "begChr") is not None else "("
        end = pr.find(M + "endChr").get(M + "val") if pr is not None and pr.find(M + "endChr") is not None else ")"
        inner = ", ".join(math_text(e) for e in el.findall(M + "e"))
        return beg + inner + end
    if el.tag.endswith("Pr"):
        return ""
    return "".join(math_text(c) for c in el)


def para_text(p):
    out = []
    def walk(el):
        for c in el:
            if c.tag == W + "t":
                out.append(c.text or "")
            elif c.tag in (W + "tab", W + "br"):
                out.append(" ")
            elif c.tag == M + "oMath" or c.tag == M + "oMathPara":
                out.append(math_text(c))
            elif c.tag == W + "pPr" or c.tag == W + "rPr":
                continue
            else:
                walk(c)
    walk(p)
    t = re.sub(r"\s+", " ", "".join(out)).strip()
    # an equation followed by a comma leaves "y=sin(x) , y=cos(x)"
    return re.sub(r" ([,;.])", r"\1", t)


def cells(tr):
    """(grid column, colspan, [paragraph texts], vMerge-continue?) per cell"""
    col, out = 0, []
    for tc in tr.findall(W + "tc"):
        pr = tc.find(W + "tcPr")
        span = 1
        cont = False
        if pr is not None:
            gs = pr.find(W + "gridSpan")
            if gs is not None:
                span = int(gs.get(W + "val"))
            vm = pr.find(W + "vMerge")
            cont = vm is not None and vm.get(W + "val") in (None, "continue")
        paras = [t for t in (para_text(p) for p in tc.iter(W + "p")) if t]
        out.append((col, span, paras, cont))
        col += span
    return out


def level_key(label):
    """F, 1 … 10, 10A — and a band "7–8" sorts by its first level"""
    if label.startswith("F"):
        return (0, "")
    m = re.match(r"(\d+)(A?)", label)
    return (int(m.group(1)), m.group(2))


def level_label(t):
    t = t.strip()
    if t == "Foundation":
        return "F"
    m = re.match(r"Foundation to Level (\d+)$", t)
    if m:
        return "F–" + m.group(1)
    m = re.match(r"Levels? (\d+A?)(?: and (\d+A?))?$", t)
    if not m:
        return None
    return m.group(1) + ("–" + m.group(2) if m.group(2) else "")


def parse(path):
    with zipfile.ZipFile(path) as z:
        body = ET.fromstring(z.read("word/document.xml")).find(W + "body")
    subject = None
    levels = {}            # label -> {"achievement": str, "strands": {name: {sub: [cds]}}}
    order = []
    strand_heading = None  # Mathematics: "Strand: Number" paragraph before each table
    seen = set()

    def lev(label):
        if label not in levels:
            levels[label] = {"label": label, "achievement": "", "parts": [], "strands": {}}
            order.append(label)
        return levels[label]

    for block in body:
        if block.tag == W + "p":
            t = para_text(block)
            m = re.match(r"Strand:\s*(.+)$", t)
            if m:
                strand_heading = m.group(1).strip()
            continue
        if block.tag != W + "tbl":
            continue
        rows = block.findall(W + "tr")
        colmap = {}        # grid column -> level label; None = below MIN_LEVEL, skipped
        for col, span, paras, _ in cells(rows[0]):
            lab = level_label(paras[0]) if paras else None
            if lab:
                for k in range(col, col + span):
                    colmap[k] = lab if level_key(lab)[0] >= MIN_LEVEL else None
        if not colmap:
            raise SystemExit(f"{os.path.basename(path)}: a table has no level header row")
        section, strand, sub = None, strand_heading, None
        for tr in rows[1:]:
            cs = cells(tr)
            texts = [p for _, _, ps, _ in cs for p in ps]
            first = texts[0] if texts else ""
            distinct = set(" ".join(ps) for _, _, ps, _ in cs if ps)
            if len(distinct) == 1 and not any(CODE.match(p) for p in texts):
                label = first
                if re.match(r"Achievement standards?$", label):
                    section = "as"; continue
                if label == "Content descriptions":
                    section = "cd"; continue
                m = re.match(r"Strand:\s*(.+)$", label)
                if m:
                    strand, sub = m.group(1).strip(), None; continue
                m = re.match(r"Sub-strand:\s*(.+)$", label)
                if m:
                    sub = m.group(1).strip(); continue
                if re.match(r"Students learn (that|to):?$", label):
                    continue
            for col, span, paras, cont in cs:
                if cont or not paras:
                    continue
                if col not in colmap:
                    raise SystemExit(f"{os.path.basename(path)}: a cell at grid column {col} has no level")
                lab = colmap[col]
                if lab is None or paras[0].startswith("No content"):
                    continue
                if section == "as":
                    if re.match(r"Achievement standards?$", paras[0]) or paras[0].startswith("No achievement standard"):
                        continue
                    text = "\n\n".join(paras)
                    L = lev(lab)
                    # Mathematics splits each level's standard across its strand
                    # tables (Number's part under Number, and so on); joined in
                    # document order they are the whole standard
                    if text not in L["achievement"]:
                        L["achievement"] = (L["achievement"] + "\n\n" + text).strip()
                        # the strand is known for Mathematics (one table per
                        # strand); Science's standard sits above every strand
                        # row, so its paragraphs are placed by tag_standard()
                        for para in paras:
                            L["parts"].append((strand if section_strand_known(strand_heading) else None, para))
                elif section == "cd":
                    if re.match(r"Students learn (that|to):?$", paras[0]):
                        continue
                    pending = []
                    for p in paras:
                        if CODE.match(p):
                            if not pending:
                                raise SystemExit(f"{p}: code with no description before it")
                            if p in seen:
                                raise SystemExit(f"{p}: appears twice")
                            seen.add(p)
                            sid = SUBJECTS.get(p[3])
                            if not sid:
                                raise SystemExit(f"{p}: unknown learning area letter {p[3]!r} — add it to SUBJECTS")
                            if subject and subject != sid:
                                raise SystemExit(f"{os.path.basename(path)}: mixes {subject[1]} and {sid[1]}")
                            subject = sid
                            if not strand:
                                raise SystemExit(f"{p}: no strand above it")
                            lev(lab)["strands"].setdefault(strand, {}).setdefault(sub or strand, []).append(
                                {"code": p, "text": " ".join(pending)})
                            pending = []
                        else:
                            pending.append(p)
                    if pending:
                        raise SystemExit(f"{os.path.basename(path)} {lab}: text with no code after it: {pending[0][:60]!r}")
    if not subject:
        raise SystemExit(f"{os.path.basename(path)}: no content descriptions found")
    for lab in order:
        levels[lab]["standard"] = tag_standard(levels[lab])
    return {
        "id": subject[0], "name": subject[1], "source": os.path.basename(path),
        "levels": [{
            "level": lab,
            "achievement": levels[lab]["achievement"],
            "standard": levels[lab]["standard"],
            "strands": [{"name": st, "substrands": [{"name": ss, "cds": cds} for ss, cds in subs.items()]}
                        for st, subs in levels[lab]["strands"].items()],
        } for lab in sorted((l for l in order if levels[l]["strands"]), key=level_key)],
    }


def section_strand_known(strand_heading):
    """Mathematics names the strand above each table; Science does not"""
    return bool(strand_heading)


# Hand corrections to tag_standard(), after reading every Science sentence
# (Nov 2026). Keyed on (level, start of the sentence); each must match exactly
# one sentence or the build stops, so a reworded chart cannot slip past.
SUB_OVERRIDES = {
    # shares "reactions"/"products" with the carbon-cycle descriptions, but it
    # is the chemistry of VC2S10U08/U09
    ("9–10", "They predict the products of reactions"): "Chemical sciences",
}


STOP = set("""the and for with that this from into their them they students student use using
including include includes level end by of to in on a an as is are be can or its it at
how what when which why who between different other such these those than through about
also both more most each them ways way""".split())


def stems(text):
    return {w[:6] for w in re.findall(r"[a-z]+", text.lower()) if len(w) > 2 and w not in STOP}


def sentences(text):
    return [t.strip() for t in re.split(r"(?<=[.!?])\s+(?=[A-Z‘“(])", text) if t.strip()]


def scores(sentence_stems, groups):
    """how much each group's content descriptions share with the sentence:
    each shared stem counts log(n/df) over the groups, so words every group
    uses ('scientific', 'data') count for next to nothing"""
    n = len(groups)
    df = {}
    for g in groups.values():
        for w in g:
            df[w] = df.get(w, 0) + 1
    return {k: sum(math.log((n + 1) / df[w]) for w in sentence_stems & g) for k, g in groups.items()}


def best(sentence_stems, groups):
    sc = scores(sentence_stems, groups)
    top = max(sc, key=lambda k: sc[k])
    return top, sc[top]


def in_order(sents, groups):
    """Assign each sentence a group, never going back to an earlier group
    (VCAA's standards run through the sub-strands in table order), choosing
    the assignment with the highest total score. A sentence with nothing in
    common with any group stays with the one before it."""
    keys = list(groups)
    S = [scores(stems(t), groups) for t in sents]
    m = len(keys)
    dp = [[0.0] * m for _ in sents]
    back = [[0] * m for _ in sents]
    for i, sc in enumerate(S):
        for j, k in enumerate(keys):
            if i == 0:
                dp[i][j] = sc[k] - j * 1e-6          # tie: the earliest group
            else:
                # tie: the latest earlier group, i.e. stay with the sentence before
                kk = max(range(j + 1), key=lambda q: (dp[i - 1][q], q))
                back[i][j] = kk
                dp[i][j] = dp[i - 1][kk] + sc[k]
    j = max(range(m), key=lambda q: (dp[-1][q], -q))
    out = []
    for i in range(len(sents) - 1, -1, -1):
        out.append(keys[j])
        j = back[i][j]
    return out[::-1]


def tag_standard(L):
    """[{strand, sub, text}] — the achievement standard a sentence at a time,
    each tagged with the strand (and sub-strand) it speaks to, so the builder
    can show only the sentences for the strand a rubric row is linked to.

    Mathematics: the chart already splits the standard by strand; sub-strand
    is the strand. Science: each paragraph is placed in the strand whose
    content descriptions (same level) it shares most words with, then each
    sentence in a sub-strand by in_order(): the standard runs through the
    sub-strands in table order, so a sentence never goes back to an earlier
    one. Without that rule, Level 9-10's "predict the products of reactions"
    went to Biological and "trends in patterns of global climate change" to
    Chemical. The result was read in full by hand (Nov 2026) and is anchored
    by tools/test-rubric-builder.js."""
    strands = L["strands"]
    out = []
    for strand, para in L["parts"]:
        if strand is None:
            strand, _ = best(stems(para), {st: set().union(*(stems(c["text"]) for subs in strands[st].values() for c in subs))
                                            for st in strands})
        subs = strands.get(strand, {})
        groups = {ss: set().union(*(stems(c["text"]) for c in cds)) for ss, cds in subs.items()}
        sents = sentences(para)
        tags = in_order(sents, groups) if len(groups) > 1 else [next(iter(groups), strand)] * len(sents)
        out += [{"strand": strand, "sub": sub, "text": t} for t, sub in zip(sents, tags)]
    for (lev, start), sub in SUB_OVERRIDES.items():
        if lev != L["label"]:
            continue
        hits = [x for x in out if x["text"].startswith(start)]
        if len(hits) != 1 or sub not in strands.get(hits[0]["strand"], {}):
            raise SystemExit(f"SUB_OVERRIDES: {lev} {start!r} matched {len(hits)} sentences (or {sub!r} is not a sub-strand of its strand)")
        hits[0]["sub"] = sub
    return out


def build(paths):
    parsed = [parse(p) for p in paths]
    sources = sorted(s.pop("source") for s in parsed)
    # one learning area can come in two charts (Foundation-6 and 7-10)
    merged = {}
    for s in parsed:
        m = merged.setdefault(s["id"], {"id": s["id"], "name": s["name"], "levels": []})
        have = {l["level"] for l in m["levels"]}
        dup = have & {l["level"] for l in s["levels"]}
        if dup:
            raise SystemExit(f"{s['name']}: level {sorted(dup)[0]} is in two charts")
        m["levels"] += s["levels"]
    subjects = sorted(merged.values(), key=lambda s: s["name"])
    for s in subjects:
        s["levels"].sort(key=lambda l: level_key(l["level"]))
    data = {"version": "Victorian Curriculum F–10 Version 2.0", "attribution": ATTRIBUTION,
            "sources": sources, "subjects": subjects}
    n = sum(len(ss["cds"]) for s in subjects for l in s["levels"] for st in l["strands"] for ss in st["substrands"])
    head = ("/* GENERATED by tools/build-curriculum.py — do not edit.\n"
            "   Victorian Curriculum F–10 Version 2.0 content descriptions and achievement\n"
            "   standards, for the curriculum picker in tools/rubric-builder.html.\n"
            "   " + ATTRIBUTION + "\n"
            "   Sources: " + "; ".join(data["sources"]) + ". */\n")
    return head + "window.VC2 = " + json.dumps(data, ensure_ascii=False, indent=1) + ";\n", n, subjects


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    paths = args or sorted(glob.glob(os.path.join(ROOT, "tools", "vcaa", "*.docx")))
    if not paths:
        raise SystemExit("No charts found. Download them into tools/vcaa/ (see the top of this file).")
    js, n, subjects = build(paths)
    if "--check" in sys.argv:
        cur = open(OUT, encoding="utf-8").read() if os.path.exists(OUT) else ""
        if cur != js:
            print("assets/js/vc2-curriculum.js is stale — run python3 tools/build-curriculum.py"); sys.exit(1)
        print("vc2-curriculum.js is current."); sys.exit(0)
    open(OUT, "w", encoding="utf-8", newline="\n").write(js)
    for s in subjects:
        print(f"{s['name']}: " + ", ".join(
            f"Level {l['level']} ({sum(len(ss['cds']) for st in l['strands'] for ss in st['substrands'])})" for l in s["levels"]))
    print(f"Wrote assets/js/vc2-curriculum.js — {n} content descriptions, {len(js) // 1024} KB")
