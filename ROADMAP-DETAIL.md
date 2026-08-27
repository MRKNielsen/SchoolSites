# Build-out roadmap — inventory and task list

**Companion to `ROADMAP.md`**, which carries the working rules, the
per-session checklist and the guardrails, and is imported into every
Claude session. This file holds the detail: where the site is, what
"done" means, and every outstanding job in effort order.

Open this whenever you are picking up, finishing or adding work. Claim
items before starting (Tier 2+), tick and date them on landing, and add
anything you discover.

Last full audit: 16 Aug 2026.

Effort key: **S** = under one session · **M** = one to three sessions ·
**L** = several sessions, worth splitting.

---

## Part 1 — Where the site actually is

Fourteen subject folders exist. Five carry content; nine are identical
35-line stub index pages, commented out of the root year picker.

| Subject | State | What's there |
|---|---|---|
| year7-science | **Built** | `bio-ecosystems` (11 decks, 11 worksheets + collated booklet & gated answer copy, quiz, gated solutions + rubric + portfolio answer key, booklet, research portfolio, bandicoot profile) · `space` (8 decks, quiz, booklet, gated solutions) |
| year12-algorithmics | **Built** | `unit-4` (13 slide decks, 9 marimo workbooks, hub, 7 problem sets, 7 revision PDFs, SAT brief, solutions) |
| year12-specialist | **Built** | `term-3` (11 decks, hub, 5 problem sets, SAC revision) |
| year10-mathematics | **Built** | `10methods-primer` (9 decks + hub) |
| year11-methods | **Built, on debt** | `chapter-9` (7 decks), `chapter-11` (2 decks) — still inline styles |
| year7-mathematics | Stub | — |
| year8-mathematics | Stub | — |
| year9-mathematics | Stub | — |
| year10-algorithmics | Stub | — |
| year11-algorithmics | Stub | — |
| year11-specialist | Stub | — |
| year11-foundation | Stub | — |
| year12-methods | Stub | — |
| year12-foundation | Stub | — |

Totals: 68 decks, 11 worksheets, 3 hubs, 2 quizzes, 1 profile page,
6 gated pages.

### Landed — unit planner page type (27 Aug 2026)

`assets/css/planner.css` — a new staff page type for unit planning documents:
one wide table, a week per row, `@page` A4 landscape with the column headings
repeated on every printed page. First use is
`year7-science/bio-ecosystems/planner.html`, a 7-week plan of the 11 lessons
in the faculty's existing column format (focus · learning intentions and
success criteria · core activities · support and extension · optional
activities · assessment), linked from a new *Planning* section on the unit
index. The same content also exists as a Word file for the faculty planning
folder — that copy lives outside the repo, in
`7 Science/Bio/Bio_Ecosystems_Unit_Planner_Yr7.docx`, and is **not** kept in
sync automatically. Whichever copy changes, change the other by hand.

Other units can reuse the page type as-is: copy `planner.html`, swap the rows.

### Landed — research portfolio answer key (25 Aug 2026)

`year7-science/bio-ecosystems/portfolio-solutions.html` — model answers and
marking criteria for all 11 stages of the Research Portfolio, plus the front
matter and the closing self-check. Linked from the unit index's *Staff only*
group and from a new *Staff only* section on `research-portfolio.html`.

Three things worth knowing before editing it:

- **The portfolio is unmarked and always was.** `\markscount` is a no-op in
  `Bio_Research_Portfolio_Yr7_8.tex` and the closing page asks students to
  judge themselves against the seven CAT criteria. So the key gives *model
  responses and criteria*, not a mark scheme, and there is no marks tally to
  keep in step — the check that matters is that the eleven stage titles still
  match the built PDF.
- **Every fact in it is traceable to `species-bandicoot.html`.** That is the
  point: the portfolio is a research task answered from the species profile,
  so an answer the profile can't support is a wrong answer even if it's true.
  Each stage's `.sh-meta` line links the profile section the answer lives in.
  If the profile changes, the key has to move with it.
- **It ships with a placeholder blob** — `{v:2, iv:"", ct:"", keys:[]}` — so
  the page locks but cannot yet unlock. Encrypt `portfolio-solutions-payload.html`
  through `tools/staff-crypt.html` and paste the emitted line over it. Staff
  password only unless a student password is deliberately added: unlike the
  worksheet answers, this key is written to the teacher (what to send back,
  which error to expect) and it answers a task students are meant to research
  themselves.

One new shared component: `pre.calc` in `solutions.css` — the existing `.calc`
box with the element's own whitespace kept and `overflow-x: auto`, for a tree
or food-web trace whose meaning is its alignment. It scrolls rather than
wraps, so a diagram wider than a phone can't push the page sideways.

### Landed — collated worksheet booklets (18 Aug 2026)

`year7-science/bio-ecosystems/worksheets-all.html` collates all 11
worksheets into one printout, and `worksheets-all-solutions.html` is the
same booklet with model answers and marking guidance filled in in red,
staff-gated behind the usual encrypted blob. Both are plain
`worksheet.css` pages — a booklet is just many `.sheet` blocks in one
document, and the existing print rule already breaks a page after each
one, so no new pagination markup was needed.

Two things worth knowing before touching worksheet spacing again:

- **The print rhythm in `worksheet.css` is tuned, not arbitrary.** A
  block of print-only margin reductions (part, question, head, footer and
  the gaps around lines/tables/boxes) takes the set from 39 printed pages
  to 35, and the collated booklet from 42 to 36. Writing space itself is
  untouched — the 8 mm rule pitch, `data-lines` counts and box heights are
  all as authored. Loosening those margins puts the pages straight back.
- **`.ws-foot` carries `break-before: avoid`** so a footer can never be
  the only thing on a sheet; three worksheets did exactly that before.
  `.tick` stays `break-inside: avoid` — letting the self-check list split
  just strands one item instead of four.

Worksheets 4 and 9 still run to 4 pages. Both are genuinely long (770 mm
and 735 mm of content against 273 mm a page) and both fragment on a
single unbreakable block — a dichotomous-key table and a four-row
mechanism table. Shortening those questions is the only thing left that
would help, which is a content decision, not a CSS one.

The red overlay is generated, not hand-written: the answers are lifted
from `solutions.html` by matching its `W<n> Q<m>` qrefs onto each
worksheet's `.qn`, including the grouped multiple-choice blocks. If the
answer key changes, the booklet has to be regenerated and re-encrypted —
it does not update itself.

### Source material that exists but isn't ported

Everything below already exists on disk in the OneDrive teaching
folders. **Nothing here needs authoring from nothing** — that's what
makes it cheap relative to the stubs.

| Source | Target | Shape of the job |
|---|---|---|
| `7 Science/Forces` — 6 decks, `experiments.html`, index, unit-local deck.css/js, booklet `.tex`/`.pdf`, 8 SVG figures, Ballista + Trebuchet lab tech sheets, 2 trebuchet investigation docx | `year7-science/forces-motion` | Same unit-local shape bio and space had. Mostly a rename job. |
| `ClaudeSPM/Specialist Maths Calc` — beamer `.tex` for Ch8 Differentiation, Ch9 Integration, Ch10 Applications, Ch11 Differential Equations, Ch12 Kinematics, plus SAC materials | `year12-specialist/calculus` (or per-chapter units) | LaTeX → HTML deck conversion. No existing HTML to rename. |
| `Algorithmics` — `AOS1 - AlgoSlides.tex`, `AOS2 - Algorithm Design.tex`, problem sets AOS2PS1–5 + 2 graph extras, `AOS2 Notes W1.tex`, marimo workbooks, SAC1 materials | `year12-algorithmics/unit-3`, `year11-algorithmics` | LaTeX → HTML. Unit 4 is the template to copy. |
| `ClaudeSPM/SPM Term 3` — `TeacherCompanion-T3.tex`, `PracticeSAC3` + marking scheme, SAC 2 Task A/B solutions | `year12-specialist/term-3` (staff-gated additions) | Existing unit, missing its staff layer. |
| `7 Science/Handwriting Tasks` — 20 docx literacy tasks spanning bio, chem, physics, Caring for Country | worksheets across `year7-science` units | docx → `worksheet.css` pages. Repetitive but mechanical. |
| `7 Science/ChemStiles` — 6 Stile PDFs, 1 revision HTML | `year7-science/mixtures` | **Authoring, not porting.** No decks exist. |
| `pdfs/Ch6_Trigonometry`, `pdfs/Quadratics_Ch5_Ch7` | `year10-mathematics` | Booklets already built and committed, just orphaned — nothing links them. |

---

## Part 2 — Definition of done

A subject is **complete** when its index page lists real units and it's
uncommented in the root year picker. A *unit* is complete when it has
the rungs below. Not every unit needs every rung — but decide
deliberately and note the decision, rather than leaving a gap that reads
as unfinished.

**The completeness ladder** (bio-ecosystems is the reference for all of it):

1. **Unit landing page** — `course.css`, themed, grouped into
   `.section-head` sections once past ~4 cards.
2. **Decks** — shared assets only, no inline `<style>`, correct theme
   class, MathJax config block with the `pageReady` hook if there's maths.
3. **Booklet** — `.tex` source + built PDF in the unit's `booklet/`,
   embedded via `.pdf-frame`, `.bookref` chips derived from the built
   `.toc` (never hand-numbered).
4. **Worksheets** — `worksheet.css`, marks totals agreeing across
   `.namebar`, toolbar hint and the index `.wl-marks`.
5. **Retrieval quiz** — unit-local `questions.js` + `quiz.html`, plus
   `.quiz-slide` insertions in later decks.
6. **Solutions** — staff-gated, encrypted through `tools/staff-crypt.html`.
7. **Hub** — `hub.css`, week grid and milestones, for units taught to a
   fixed calendar.
8. **Profile / reference pages** — where a unit has a case study worth
   reading alongside the decks.

**Every page, every time:** links tokens.css, carries the sitenav two-liner
and the favicon block, and has a `<title>` specific enough to be a nav
label on its own.

---

## Part 3 — The work, in effort order

### Tier 0 — Housekeeping (minutes each)

- [x] **`.gitignore` has a stray trailing quote.** Stripped; confirmed
      with `git check-ignore -v` that
      `year12-algorithmics/unit-4/sat/Memo03_brief.pdf` now matches.
      **S** *(done 2026-08-16)*
- [x] **Link the two orphaned booklets in `pdfs/`.** Both moved into
      `year10-mathematics/10methods-primer/booklet/` with their `.tex`,
      and given `.pdf-frame` pages — `booklet-trigonometry.html` (39 pp,
      6A–6K) and `booklet-quadratics.html` (56 pp, 5A–5J + 7A–7I). Each
      lists its sections linked to the matching deck slide, and the
      primer hub now shows a "Question booklet" chip beside "Open deck"
      on the Ch5, Ch6 and Ch7 chapters. `pdfs/` is left in place, empty,
      with its README updated to say what it's for.
      **S** *(done 2026-08-16)*
- [x] **Add a `404.html`.** `course.css` page with the drawer, listing
      the six units that have material. It is the one page in the repo
      carrying a root-absolute path: a 404 renders at the *bad* URL, at
      any depth, so relative asset paths would 404 in turn — it uses
      `<base href="/SchoolSites/">` and everything else on the page is
      relative to that. Excluded from the nav tree via `SKIP_FILE` in
      `build-sitemap.js`. **S** *(done 2026-08-16)*

- [x] **`10methods-primer/index.html` still has an inline `<style>`
      block.** Lifted into hub.css as a named **chapter group**
      component — `.chapter`, `.ch-head`, `.ch-meta`, `.ch-links`,
      `.ch-open` — rather than accepted, because the multi-chapter shape
      recurs (year11-methods ch9/11, and Specialist calculus will want it
      if that lands as one unit with chapter sections). Two of the
      lifted rules weren't chapter-specific at all and went into the
      existing `ul.periods` block instead: `ul.periods a` (a period line
      linking straight to its slide, white not UA blue) and
      `ul.periods li b` (the lead-in section code or day, in the hub
      amber). **That second one is a deliberate visual change to
      `year12-algorithmics/unit-4/index.html`** — its `<b>Tue</b>` day
      labels were previously unstyled and now match the primer's. The
      three hub pages now carry no inline `<style>` between them;
      `check-links.js` clean at 132 pages / 1683 refs. **S**
      *(done 2026-08-16)*

### Tier 1 — Small fixes (under a session each)

- [x] **Encrypt `year7-science/space/solutions.html`.** Already done and
      the item had gone stale — the page now carries a real v2 blob with
      both a staff and a student wrapper, and unlocks. Confirmed by
      parsing the blob, not by reading this file. **S**
      *(found already landed 2026-08-25)*
- [x] **Detheme the SVG figures in `year12-specialist/term-3/slides/`.**
      All eleven decks, not just T3W01–05: 576 elements rethemed, 21
      per-figure `<style>` blocks removed, 27 `style="font-size:…"`
      prose hacks replaced. Mapping used — `#d02670`→`--accent`,
      `#9d174d`/`#9d144d`→`--accent-dark`, `#475569`→`--ink-soft`,
      `#e2e8f0`→`--line`, `#1e293b`→`--ink`, `#b45309`→`--accent-warm`
      (exactly `--c-rust-600`), `#c0392b`→`--neg`. Left literal on
      purpose: `#fff`, `#eff2fb` (neutral card wash), and `#90A4AE`
      where it draws a *second plotted curve* — that one is a data
      series, not palette. Where the same hex drew a dashed guide line
      it became `--ink-faint`. Three new deck.css components carry what
      the inline styles were doing: `.deck svg text:not([font-family])`,
      `.figcap`, `.slide-foot`. **S** *(done 2026-08-16)*
- [ ] **Decide the fate of the four bare-name legacy folders.**
      `algorithmics/`, `foundation/`, `methods/`, `specialist/` hold 8
      files between them, still on `site.css`, excluded from the nav
      drawer. Note they are *not* pure duplicates: `complexity-suite`,
      `telling-time`, `tangent-visualiser` and `slope-fields` survive
      here even though the year-prefixed copies of those placeholders
      were deleted in Aug 2026. Check whether any is a real tool worth
      keeping; if not, delete all four folders and retire `site.css`
      down to `tools/staff-crypt.html` only. **S**
- [x] **Audit the nine stub index pages.** All clean — every one carries
      the "No resources published for this subject yet" line with no
      empty `.deck-grid`, the right theme class, and a `<title>` that
      reduces to a sensible nav label ("Mathematics", "Algorithmics",
      "Foundation Mathematics"…) under its Year N section. Also
      confirmed all eight themes in tokens.css have a matching
      `.sn-t-<name>` dot rule in sitenav.css, so none is falling back to
      the generic accent. Nothing to change. **S** *(done 2026-08-16)*
- [x] **Add a link checker to `tools/`.** `tools/check-links.js` —
      dependency-free, walks every `<a href>`, `<link>`, `<script src>`,
      `<img src>`, `<object data>`, `<source>`, `<iframe>`, `<embed>`,
      poster and SVG `<use>`. Reports four classes: **MISSING**,
      **CASE** (exists with different capitalisation — works on Windows,
      404s on GitHub Pages, the one this repo is most exposed to),
      **ABSOLUTE** (root-absolute path under `/SchoolSites/`) and
      **IGNORED** (target is gitignored, so it isn't on the published
      site — catches links to `*-payload.html`). Exits 1 on any finding,
      ready for the CI item in Tier 5. Skips marimo workbook exports
      unless `--all`. It found one real break on first run (the
      styleguide deck template's home button pointed at a
      `styleguide/index.html` that doesn't exist) — now fixed. **S**
      *(done 2026-08-16)*

      Two false-positive traps it already handles, worth knowing before
      extending it: `<script>` and `<style>` *bodies* are blanked before
      matching, because JS that builds a download link reads as
      `a.href = url;` and matched as an `<a href>`; and HTML comments are
      blanked, because the root index.html deliberately keeps the
      unpublished subject cards commented out.

### Tier 2 — Ports with HTML source (one to three sessions each)

These follow a known recipe. Read the "Legacy content" section of
CLAUDE.md before starting one — the class-rename vocabulary and the two
traps (strip inline `style=` *before* renaming classes; don't promote a
Recap slide to `.exit-slide`) are written down there.

- [ ] **Port `7 Science/Forces` → `year7-science/forces-motion`. M**
      The cheapest real content win in the repo, and it completes Year 7
      Science's third unit.
  - [ ] 6 decks off the unit-local `deck.css`/`deck.js` onto shared assets
  - [ ] `experiments.html` — decide its page type (likely `course.css`
        section on the landing page, or a `profile.css` reference page)
  - [ ] Unit landing page, `theme-science`
  - [ ] `booklet/` — `.tex` + PDF + `fonts/`, embedded via `.pdf-frame`
  - [ ] 8 SVG figures — theme colours to tokens, illustrative hues left alone
  - [ ] Ballista + Trebuchet lab tech sheets as linked PDFs
  - [ ] `.bookref` chips derived from the built `.toc`
  - [ ] Trebuchet investigation docx → worksheet pages *(can defer)*
  - [ ] Quiz + gated solutions *(can defer to a second pass)*

- [ ] **Port `year11-methods` chapter-9 and chapter-11 off inline
      styles. M** Nine decks, the last inline-styled content in the repo.
      Both chapter indexes were already ported to `course.css`, so it's
      the decks only. Same recipe as Forces, plus: these are maths decks,
      so check every MathJax config block has the `startup.pageReady`
      hook and that no deck carries its own copy of `tex-svg.js` instead
      of the vendored one.

- [ ] **Handwriting Tasks → worksheets. M**
      20 docx literacy tasks. Nine map onto bio-ecosystems topics
      (classification, food webs, ecosystems, adaptations, biodiversity,
      Caring for Country), six onto a future mixtures unit, three onto
      forces. Do them in unit batches as each unit lands, not as one
      20-file push. Note task 20 (Caring for Country) uses `.fnbox`.

### Tier 3 — LaTeX → HTML conversions (several sessions each)

No HTML to rename — the beamer source has to be re-authored as decks.
Budget more than the page count suggests: the maths and diagrams are the
slow part, not the structure.

- [ ] **Algorithmics Unit 3 → `year12-algorithmics/unit-3`. L**
      Unit 4 is built and is the template — copy its folder shape
      (`slides/`, `problemsets/`, `revision/`, `workbooks/`, hub
      `index.html`, gated `solutions.html`) exactly.
  - [ ] `AOS1 - AlgoSlides.tex` → decks
  - [ ] `AOS2 - Algorithm Design.tex` → decks
  - [ ] Problem sets AOS2PS1–5 + the two graph extras → `problemsets/`
  - [ ] SAC1 materials → staff-gated
  - [ ] Marimo workbooks — **note** the injector skips marimo exports
        because a re-export overwrites the edit; follow Unit 4's pattern
  - [ ] Hub page with the unit calendar
  - [ ] Then uncomment year12-algorithmics's Unit 3 card

- [ ] **Year 11 Algorithmics → `year11-algorithmics`. L**
      Depends on how much Unit 1/2 material exists — the `Algorithmics`
      folder is mostly Units 3&4. **Audit the source before committing to
      this one**; it may turn out to be a Tier 4 authoring job.

- [ ] **Specialist calculus → `year12-specialist`. L**
      Five beamer chapters: Ch8 Differentiation, Ch9 Integration,
      Ch10 Applications, Ch11 Differential Equations, Ch12 Kinematics.
      Decide the folder shape first — per-chapter units, or one
      `calculus/` unit with chapter sections. `term-3` already covers
      kinematics from the calendar side, so **check for overlap with
      Ch12 before duplicating it**.
      There's a partial `website/ch12.html` in the source folder worth
      looking at as a starting point.
      Heavy maths: every expression whole-typeset in MathJax, `.working`
      for lines of working, `\phantom{}` for `=` alignment.

- [ ] **Term 3 staff layer. M**
      `TeacherCompanion-T3.tex`, `PracticeSAC3` + marking scheme, and the
      SAC 2 Task A/B solutions all exist unported. This is the gated-page
      recipe, and term-3 currently has no `solutions.html` at all.

### Tier 4 — Authoring from scratch (large, open-ended)

Eight of the nine stub subjects have **no source material at all**. Be
honest about that: a stub with a truthful "nothing published yet" line
is better than a card promising a tool that doesn't exist — that
principle already cost twelve placeholder pages in Aug 2026, don't
re-earn it.

- [ ] **Year 7 Chemistry (Mixtures) → `year7-science/mixtures`. L**
      Six Stile PDFs and one revision page to work from — enough to
      scaffold a unit outline, not enough to port. Would complete Year 7
      Science as a full-year program (Bio · Space · Forces · Mixtures)
      and absorbs six of the Handwriting Tasks.
- [ ] **year7/8/9-mathematics. L each** Nothing exists. Three full
      junior maths programs is the largest single commitment in this
      file — treat each as its own project, and probably don't start one
      until Tiers 0–3 are clear.
- [ ] **year12-methods, year11-specialist, year11-foundation,
      year12-foundation, year10-algorithmics. L each** Nothing exists.

**Ordering note:** don't take a Tier 4 subject purely because it's next
alphabetically. Prefer whichever you're actually teaching, or whichever
completes a year level that's already half-built (Year 7 Science is one
unit from complete; Year 12 Specialist and Algorithmics are each one unit
from complete). Finishing a year level is worth more to a student than
starting a new one.

### Tier 5 — Platform work (ongoing, do between content pushes)

- [ ] **Repo weight.** `year12-algorithmics/unit-4/workbooks` is 27 MB —
      the largest thing in the repo by a wide margin — because each
      marimo export ships its own copy of the favicon set and an
      `assets/` folder. Investigate whether the exports can share the
      site's assets, or whether the workbooks belong as downloads rather
      than committed pages. Weigh against CLAUDE.md's warning that
      re-exporting overwrites edits. **M**
- [ ] **Site search.** 68 decks and growing. The nav drawer maps the site
      but doesn't search it. `sitemap.js` is already a generated tree —
      a client-side title/heading index built by the same tool would be a
      small extension. **M**
- [ ] **Hub pages for the remaining built units.** Only 3 of the built
      units have one. Not every unit needs a week grid, but the ones
      taught to a fixed calendar do. **S each**
- [ ] **Accessibility pass.** Never audited. Contrast on themed
      backgrounds, keyboard reachability of the deck chrome and part
      tabs, alt text on the SVG figures, focus visibility in the drawer.
      Do it once properly and write the findings into CLAUDE.md so it
      doesn't have to be rediscovered. **M**
- [ ] **A contributor README.** `CLAUDE.md` is the design contract but
      reads as instructions to Claude. A short human-facing README —
      how to run the tools, what the folder conventions are, how to start
      a new unit — would help another educator start cold. **S**
- [ ] **The marimo workbook exports have nine broken `manifest.json`
      links.** `node tools/check-links.js --all` reports every
      `unit-4/workbooks/u4w0*.html` linking a `./manifest.json` that was
      never exported. Harmless in practice — it's a preload hint — but
      it is the only breakage left in the repo, and it argues for the
      "workbooks as downloads rather than committed pages" option in the
      repo-weight item below. Do not hand-edit the exports; a re-export
      overwrites. **S** *(found 2026-08-16)*
- [ ] **Consider CI.** A GitHub Action running the link checker and
      confirming `sitemap.js` is current on every push would catch the
      two things most likely to silently rot. The checker now exists and
      exits 1 on any finding, so the action is a handful of lines —
      just gate it on `check-links.js` (not `--all`, until the workbook
      manifests above are dealt with). **S**
