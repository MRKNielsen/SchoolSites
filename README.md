# Class Materials

Static site for Years 7–12 class resources, hosted on GitHub Pages.
Live at: https://mrknielsen.github.io/SchoolSites/

## How it's laid out

The landing page groups everything by **year level**. On disk, each subject has
its own **per-year folder** named `yearNN-subject`:

```
/
├── index.html                    ← landing page (grouped by year 7–12)
├── assets/css/site.css           ← shared styles — edit colours/fonts here once
├── year7-mathematics/
│   ├── index.html                ← subject page (list of resources)
│   └── number-sense-games.html   ← a resource (placeholder — replace this)
├── year7-science/
├── year8-mathematics/
├── year9-mathematics/
├── year10-mathematics/
├── year10-algorithmics/
├── year11-methods/
├── year11-specialist/
├── year11-foundation/
├── year11-algorithmics/
├── year12-methods/
├── year12-specialist/
├── year12-foundation/
├── year12-algorithmics/
├── pdfs/                         ← drop compiled PDFs here
├── .gitignore
└── .nojekyll
```

## Replacing a placeholder, one at a time

1. **Single HTML tool** — overwrite the placeholder file in the subject folder
   (e.g. `year12-specialist/slope-fields.html`).
2. **Multi-file resource** — make a sub-folder with an `index.html` inside the
   subject folder (e.g. `year7-science/electricity/index.html`). Note: a page one
   level deeper needs `../../assets/...` for the stylesheet.
3. **PDF** — put it in `pdfs/`, then link to `../pdfs/yourfile.pdf` from the
   subject page and set the `kind` label to "PDF".

Then edit the subject `index.html` so the link text and filename match.

## Adding a new subject to a year

1. Make the folder: `yearNN-subject/`
2. Copy an existing subject's `index.html` into it and edit the titles/labels.
3. Add a matching `<a class="card">` inside that year's `<section class="year-block">`
   on the root `index.html`.

## Relative paths

All links are relative so the site works under the `/SchoolSites/` project path.
- Subject pages reach the stylesheet with `../assets/...`
- Pages one level deeper use `../../assets/...`

## Going live

Already configured. Each push auto-redeploys. Hard-refresh (Ctrl+F5) to bust cache.
