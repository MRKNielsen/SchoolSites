# pdfs/

Standalone question booklets that belong to **no unit**. Currently empty.

A booklet that belongs to a unit lives in that unit's own `booklet/`
folder, with the `.tex` beside the built PDF (and the `fonts/` the `.tex`
loads by relative path, if it loads any), so the booklet rebuilds from a
clean checkout. Embed it with an `<object type="application/pdf">` inside
a `.pdf-frame` — see `year7-science/bio-ecosystems/research-portfolio.html`.

The two booklets that used to sit here, `Ch6_Trigonometry_Question_Booklet`
and `Quadratics_Ch5_Ch7_Question_Booklet`, moved to
`year10-mathematics/10methods-primer/booklet/` in Aug 2026 — they belong
to the primer, and nothing on the site linked them while they were here.

Build artefacts (`.aux`, `.log`, `.toc`, `.synctex.gz`) are gitignored;
only the `.tex` and the `.pdf` are committed.
