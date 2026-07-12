# Class Materials

Static site for VCE & Foundation Mathematics resources, hosted on GitHub Pages.

## How it's laid out

```
/
├── index.html              ← landing page (the subject cards)
├── assets/css/site.css     ← shared styles — edit colours/fonts here once
├── specialist/
│   ├── index.html          ← subject page (list of resources)
│   └── slope-fields.html   ← a resource (placeholder — replace this)
├── methods/
│   ├── index.html
│   └── tangent-visualiser.html
├── algorithmics/
│   ├── index.html
│   └── complexity-suite.html
├── foundation/
│   ├── index.html
│   └── telling-time/
│       └── index.html      ← multi-file resources get their own folder
├── pdfs/                   ← drop compiled PDFs here
├── .gitignore             ← keeps LaTeX clutter + student CSVs out of git
└── .nojekyll              ← tells Pages to serve files as-is
```

## Replacing a placeholder, one at a time

1. **A single HTML tool** — overwrite the file (e.g. `specialist/slope-fields.html`)
   with your self-contained tool. It can keep or drop the shared stylesheet link;
   it works either way.
2. **A multi-file resource** — make a folder with an `index.html` inside it
   (like `foundation/telling-time/`). It's served at `/foundation/telling-time/`.
3. **A PDF** — put the file in `pdfs/`, then on the subject page point a list item at
   `../pdfs/yourfile.pdf` and set the `kind` label to "PDF".

Then edit the matching subject `index.html` so the link text and filename line up.

## Relative paths — the one thing to watch

Every link is **relative** so the site works whether it's a user site
(`you.github.io`) or a project site (`you.github.io/class-materials/`).
- Pages in a subject folder reach the stylesheet with `../assets/...`
- Pages one level deeper (like `telling-time/`) use `../../assets/...`
Keep it relative and nothing breaks.

## Going live

Settings → Pages → Source → *Deploy from a branch* → `main` / root → Save.
Every push redeploys automatically.
