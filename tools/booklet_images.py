#!/usr/bin/env python3
"""Render every page of a booklet PDF to an image for the site.

Workbook decks show a small view of the booklet page a task is on
(.bookview), and the unit's flip-book will turn through the same images.
They are build output from the PDF, never edited by hand:

    python3 tools/booklet_images.py year7-science/space/booklet/Space_Unit_Booklet_Yr7_8.pdf
    python3 tools/booklet_images.py year7-science/space/booklet/Space_Unit_Booklet_Yr7_8.pdf --check

writes booklet/pages/p01.jpg, p02.jpg ... (700 px wide, JPEG) beside the
PDF. --check changes nothing and exits 1 if any page image is missing,
older than the PDF, or left over from a longer booklet. Re-run after
every booklet rebuild. Needs pdftoppm (poppler).
"""
import glob
import os
import re
import shutil
import subprocess
import sys
import tempfile

WIDTH = 700


def pages_of(pdf):
    out = subprocess.run(["pdfinfo", pdf], stdout=subprocess.PIPE, check=True).stdout.decode()
    return int(re.search(r"^Pages:\s+(\d+)", out, re.M).group(1))


def name(n, total):
    return "p%0*d.jpg" % (max(2, len(str(total))), n)


def main(argv):
    if len(argv) < 2 or argv[1] in ("-h", "--help"):
        sys.exit(__doc__)
    pdf = argv[1]
    check = "--check" in argv[2:]
    outdir = os.path.join(os.path.dirname(pdf), "pages")
    total = pages_of(pdf)
    want = {name(n, total) for n in range(1, total + 1)}
    have = {os.path.basename(f) for f in glob.glob(os.path.join(outdir, "p*.jpg"))}

    if check:
        pdf_t = os.path.getmtime(pdf)
        problems = ["missing " + f for f in sorted(want - have)]
        problems += ["left over " + f for f in sorted(have - want)]
        problems += ["older than the PDF: " + f for f in sorted(want & have)
                     if os.path.getmtime(os.path.join(outdir, f)) < pdf_t]
        if problems:
            print("%s: page images are stale (%d issues)" % (pdf, len(problems)))
            for p in problems[:12]:
                print("  " + p)
            return 1
        print("%s: %d page images, all current." % (pdf, total))
        return 0

    os.makedirs(outdir, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(["pdftoppm", "-jpeg", "-jpegopt", "quality=74,progressive=y",
                        "-scale-to-x", str(WIDTH), "-scale-to-y", "-1",
                        pdf, os.path.join(tmp, "pg")], check=True)
        made = sorted(glob.glob(os.path.join(tmp, "pg-*.jpg")),
                      key=lambda f: int(re.search(r"-(\d+)\.jpg$", f).group(1)))
        if len(made) != total:
            sys.exit("pdftoppm made %d images for %d pages" % (len(made), total))
        for n, f in enumerate(made, 1):
            shutil.copyfile(f, os.path.join(outdir, name(n, total)))
    for extra in sorted(have - want):
        print("note: %s is left over from a longer booklet — delete it" % extra)
    print("%s: wrote %d page images to %s" % (pdf, total, outdir))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
