#!/usr/bin/env python3
"""Exports the marimo workbooks to browser-runnable pages.

    python tools/build-workbooks-web.py year11-applied-computing/unit-1

Why a script rather than a bare `marimo export html-wasm`: the raw export is
self-contained, so every notebook ships its own 26 MB copy of the marimo
runtime. That is already the single heaviest thing in this repo (see the
repo-weight item in ROADMAP-DETAIL.md). This moves the runtime to one shared
assets/marimo/ at the repo root and rewrites each page to point at it, so N
workbooks cost 26 MB once rather than N times.

It also drops the <link rel="manifest"> that marimo emits but never exports —
the only broken reference `check-links.js --all` reports today.

Re-running overwrites the generated pages, so never hand-edit them: change
this script instead.
"""
import argparse
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

# Files marimo puts at the export root that are really part of the runtime,
# not of any one notebook. These move to the shared folder with assets/.
SHARED_EXTRAS = (
    "favicon.ico", "apple-touch-icon.png", "logo.png",
    "favicon-16x16.png", "favicon-32x32.png",
    "android-chrome-192x192.png", "android-chrome-512x512.png",
)


def export_one(notebook: pathlib.Path, out_dir: pathlib.Path, shared_rel: str,
               shared_dir: pathlib.Path) -> pathlib.Path:
    """Exports one notebook and repoints it at the shared runtime."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp = pathlib.Path(tmp) / "export"
        subprocess.run(
            ["marimo", "export", "html-wasm", notebook.name,
             "-o", str(tmp), "--mode", "edit"],
            cwd=notebook.parent, check=True,
            stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
        )

        # The runtime is byte-identical between notebooks of the same marimo
        # build, so the first export populates the shared folder and the rest
        # only confirm they agree.
        if not (shared_dir / "assets").is_dir():
            shared_dir.mkdir(parents=True, exist_ok=True)
            shutil.copytree(tmp / "assets", shared_dir / "assets")
            for extra in SHARED_EXTRAS:
                if (tmp / extra).is_file():
                    shutil.copy2(tmp / extra, shared_dir / extra)

        html = (tmp / "index.html").read_text(encoding="utf-8")
        for name in sorted(p.name for p in (tmp / "assets").iterdir()):
            if f"./assets/{name}" not in html:
                continue
            if not (shared_dir / "assets" / name).is_file():
                sys.exit(f"{notebook.name}: {name} is not in the shared runtime — "
                         f"the exports disagree. Delete {shared_dir} and rebuild all of them.")
        html = html.replace("./assets/", f"{shared_rel}/assets/")
        for extra in SHARED_EXTRAS:
            html = html.replace(f'"./{extra}"', f'"{shared_rel}/{extra}"')
        # marimo links a manifest it does not export. Harmless, but it is a
        # 404 and the link checker is right to say so.
        html = re.sub(r'\s*<link[^>]+rel="manifest"[^>]*>', "", html)

        page = out_dir / (notebook.stem.split("-")[0].lower() + ".html")
        out_dir.mkdir(parents=True, exist_ok=True)
        page.write_text(html, encoding="utf-8")

        # public/ carries the wheel marimo built from checks/, and anything
        # else the notebook fetches at runtime.
        if (tmp / "public").is_dir():
            if (out_dir / "public").exists():
                shutil.rmtree(out_dir / "public")
            shutil.copytree(tmp / "public", out_dir / "public")
        return page


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("unit", help="unit folder holding workbooks/, e.g. year11-applied-computing/unit-1")
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--shared", default="assets/marimo",
                    help="where the shared marimo runtime lives, relative to the repo root")
    args = ap.parse_args()

    root = pathlib.Path(args.repo_root).resolve()
    unit = (root / args.unit).resolve()
    notebooks = sorted((unit / "workbooks").glob("W*.py"))
    if not notebooks:
        sys.exit(f"No W*.py notebooks under {unit / 'workbooks'}")

    out_dir = unit / "workbooks-web"
    shared_dir = root / args.shared
    shared_rel = "/".join([".."] * len(out_dir.relative_to(root).parts)) + "/" + args.shared

    for nb in notebooks:
        page = export_one(nb, out_dir, shared_rel, shared_dir)
        print(f"  {nb.name} -> {page.relative_to(root)}")
    print(f"shared runtime: {shared_dir.relative_to(root)}  (referenced as {shared_rel})")


if __name__ == "__main__":
    main()
