#!/usr/bin/env python3
"""Write real booklet page numbers into a workbook unit page.

A unit's contents page captions each lesson "Turn to page N". N must be
the page that lesson starts on in the printed booklet, so it is never
typed by hand: the page marks each number with the booklet label it
stands for,

    <section class="contents" data-booklet="booklet/Space_Unit_Booklet_Yr7_8.tex">
      ... <span class="bk-page" data-label="sec:2">8</span> ...

and this tool builds that booklet in a scratch folder (xelatex, twice,
so \\pageref is settled), reads every \\newlabel from the .aux and
rewrites the numbers. The booklet folder itself is never touched.

    python3 tools/booklet_pages.py year7-science/space/index.html
    python3 tools/booklet_pages.py year7-science/space/index.html --check

--check changes nothing and exits 1 if any number is stale or any label
is missing from the booklet. Re-run after changing the booklet (the A5
rebuild will move every page). Needs xelatex on PATH.
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile

SPAN = re.compile(r'(<span class="bk-page" data-label="([^"]+)">)([^<]*)(</span>)')
BOOKLET = re.compile(r'data-booklet="([^"]+)"')
NEWLABEL = re.compile(r'\\newlabel\{([^}]+)\}\{\{[^}]*\}\{([^}]*)\}')


def build_labels(tex_path):
    src_dir = os.path.dirname(os.path.abspath(tex_path))
    name = os.path.basename(tex_path)
    with tempfile.TemporaryDirectory() as tmp:
        work = os.path.join(tmp, "booklet")
        shutil.copytree(src_dir, work)
        for _ in range(2):
            r = subprocess.run(["xelatex", "-interaction=nonstopmode", "-halt-on-error", name],
                               cwd=work, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            if r.returncode != 0:
                tail = r.stdout.decode("utf-8", "replace")[-1500:]
                sys.exit("xelatex failed on %s:\n%s" % (name, tail))
        aux = open(os.path.join(work, name[:-4] + ".aux"), encoding="utf-8", errors="replace").read()
    return {m.group(1): m.group(2) for m in NEWLABEL.finditer(aux)}


def main(argv):
    if len(argv) < 2 or argv[1] in ("-h", "--help"):
        sys.exit(__doc__)
    page = argv[1]
    check = "--check" in argv[2:]
    html = open(page, encoding="utf-8").read()
    m = BOOKLET.search(html)
    if not m:
        sys.exit("%s has no data-booklet=\"…\" attribute" % page)
    tex = os.path.join(os.path.dirname(page), m.group(1))
    labels = build_labels(tex)

    problems, changed = [], 0

    def fix(mm):
        nonlocal changed
        label, old = mm.group(2), mm.group(3)
        if label not in labels:
            problems.append("label %s is not in %s" % (label, os.path.basename(tex)))
            return mm.group(0)
        new = labels[label]
        if new != old:
            changed += 1
            problems.append("%s: page %s -> %s" % (label, old or "(blank)", new))
        return mm.group(1) + new + mm.group(4)

    out = SPAN.sub(fix, html)
    count = len(SPAN.findall(html))
    if count == 0:
        sys.exit("%s has no <span class=\"bk-page\" data-label=…> numbers" % page)

    if check:
        if problems:
            print("%s is stale:" % page)
            for p in problems:
                print("  " + p)
            return 1
        print("%s: all %d page numbers match the booklet." % (page, count))
        return 0

    missing = [p for p in problems if "is not in" in p]
    if missing:
        print("\n".join(missing))
        return 1
    if out != html:
        with open(page, "w", encoding="utf-8", newline="\n") as f:
            f.write(out)
    print("%s: %d page numbers, %d updated." % (page, count, changed))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
