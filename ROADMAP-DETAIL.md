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
| year7-science | **Built** | `bio-ecosystems` (11 decks, 11 worksheets + collated booklet & gated answer copy, quiz, gated solutions + rubric + portfolio answer key, booklet, research portfolio, bandicoot profile) · `space` (10 decks, 10 worksheets + collated booklet, quiz, planner, booklet + single-lesson print, gated solutions) |
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

Totals: 70 decks, 21 worksheets, 3 hubs, 2 quizzes, 1 profile page,
6 gated pages.

### Landed — Year 10 exponential graphs redrawn (9 Oct 2026)

All ten figures in `10methods-primer/Ch3FL_ExponentialsLogs_Slides.html`
plus the compound-interest graph on slide 14 of
`Term4_RevisionExam_Slides.html`. The originals came out of the old JS
deck's graph helper: 310 px wide, no scale, curve labels written on top of
the curve, coordinate labels colliding with each other (`(3, ?)` sat
exactly on `V = 30000(0.88)ⁿ`), the `asymptote y = 0` label clipped off
the right edge, money curves drawn into negative years, and the
compound/simple graph with no x-axis at all.

What replaced them, so the next primer redraw can follow suit:

- Inline SVG in a `.graph-card` (`.narrow` on Key idea slides), 480×360
  viewBox, light grid, numbered axes, tokens only — `--accent` first
  curve, `--accent-warm` second curve or reference line, `--neg` dashed
  asymptote, `--accent-dark` points. Every label carries a
  `paint-order="stroke"` halo in `--card` so a gridline never cuts it.
- **Exponents are `<tspan>`s, not Unicode superscripts.** `⁰ ⁴ ⁵ ⁿ ⁻`
  (U+2070–207F) are in neither of Source Sans 3's latin subsets, so
  `10⁰` and `Aⁿ` were rendering in a fallback font mid-label while `10¹`
  `10²` `10³` (Latin-1) didn't. The same applies to deck prose, which
  still uses the Unicode forms.
- Worked-example and Your-turn slides now put the question and steps in
  the left column and the graph on the right, instead of a thumbnail
  beside the question with the steps full-width underneath. Reveal order
  is unchanged (checked with arrow presses). No slide overflows at
  1600×900, 1366×768 or 1280×720.
- Every label was checked in a browser against every stroke and every
  other label — zero collisions, at least ~5 px clearance throughout.
- Slide 21's formula chip was half MathJax, half text (`)ⁿ` floated
  outside the typeset fraction); now one MathJax expression.

### Landed — seasons visualiser (2 Sep 2026)

`assets/css/seasonsim.css` + `assets/js/seasonsim.js`, a third optional
module in the `orbit.js` / `binomsim.js` mould: one line of markup,
`<div class="seasonsim"></div>`, zero dependencies, colours from tokens,
controls hidden in print. Live on Space deck 2 slide 6 (full width, under
the existing two columns) and in `styleguide/deck-demo.html`.

Two things about it are load-bearing and should not be "tidied":

- **The close-up holds the axis at a fixed screen angle** and swings the
  lit half around it. Rotating Earth instead, so the Sun stays on the
  left, is easier to write and teaches the exact opposite of the
  mechanism — the whole point is that nothing about Earth changes.
- **The orbit is a circle.** Eccentricity is 0.017. A visibly elliptical
  orbit with the Sun in the middle is what produces "it's summer because
  we're closer", and deck 2 slide 7 had to be redrawn for exactly that.

Verified by running the module under a small DOM shim rather than
re-deriving its maths: polar night at the December solstice, midnight sun
in June, terminator through both poles at both equinoxes, sub-solar
latitude 23.4°S/N at the solstices, and the axis attributes byte-identical
at every point in the year.

### Landed — Space answer reveals, planet definition, recap sweep (8 Oct 2026)

Three jobs across all ten Space decks.

**On-click answers, 33 of them.** Every `.box.question` labelled Starter,
Think, Discuss, Check, Reflect or Predict now carries a reveal. Two
registers: a definite answer gets *Show answer* / **Answer**, an open
discussion gets *What to listen for* / **What we're listening for** —
because writing a single "correct" answer under a Discuss question would
quietly close down the discussion it exists to open. The one box left
without a reveal is deck 4's "Checking the rate against the rocks", which
is a You-do and already has its `ol.steps` working behind a button.

This needed a **new shared component**: `.box > .a` in deck.css, the
`.qcard .a` reveal generalised so it works inside a callout box without
wrapping the question in a second card. deck.js needed no change —
`data-answer="#id"` was already wired and had never been used in the repo.
Child selector, not descendant, so a `.qcard` nested in a box keeps its
own rule. `--ink` not `--muted`, because the box is already on a tinted
background. Print rule extended alongside it.

**The IAU definition of a planet** — new deck 5 slide 7, *What counts as a
planet?*: the three criteria, a table testing Pluto against each, and the
Pluto discussion moved onto it (it previously said "using the definition
above" on a slide where no definition existed).

Correcting it meant a four-file sweep, because **"dwarf planets are too
small" was wrong and was baked into an assessed question.** Size is not an
IAU criterion; Pluto passes the roundness test comfortably at 2,377 km and
fails criterion 3 and only criterion 3. Fixed in deck 5's bullet, the
booklet §5.2 bullet, booklet Q5.10 (which asked for "the two reasons", of
which there is one), worksheet 5 Q7, and both answers in
`solutions-payload.html`. The booklet gained a matching
`what counts as a planet` infobox at §5.2. Rebuilt ×3: still 48 pages,
every `\newlabel` page unchanged, all 67 deck `.bookref` chips still
correct, Q5.10 still Q5.10 at 3 marks.

**Recap slides.** Five of the ten — decks 1, 5, 8, 9 and 10 — claimed
First Nations content their deck does not teach. Left over from the
original 11-lesson shape, where the material was threaded through every
lesson; since the 31 Aug resequence it is all in Lesson 7. A recap that
summarises another lesson is simply wrong, so the bullets came out and
each deck gained one `.note` line pointing at the Lesson 7 slide that
actually covers it. Every pointer was checked against the slide map.
All ten recaps were then brought up to what the deck now contains —
mostly the Year 8 extension slides, which eight of the ten never
mentioned. Deck 8 had no exit question at all and now has one.

Two errors fixed in passing: deck 9 said JWST at L2 is "always in Earth's
shadow" (it is not, and must not be — it needs its solar panels lit; the
point of L2 is that Sun, Earth and Moon stay on one side so a single
shield covers all three), and the ISS gravity figure read 88% in the recap
against "about 90%" on two slides.

Also: deck.css line 561 carried a literal `</style>` inside a comment,
which silently truncated the file for anything inlining it into a `<style>`
block. Escaped. Harmless via `<link>`, which is why it survived this long.

### Landed — Space worksheets (2 Sep 2026)

Ten `worksheet.css` sheets for `year7-science/space`, one per lesson, 337
marks in total, plus `worksheets-all.html` collating them. Each is linked
under its lesson on the unit index via `.deck-item` + `.dc-wslink`, and the
answers went into the existing gated `solutions.html` rather than a second
gated page — a `.subhead` tagged `<span class="tag ws">Worksheet</span>` at
the end of each lesson's section.

Three things worth carrying forward:

- **Worksheet answers are referenced `W<sheet>.<q>`, not `Q<n>.<n>`.** The
  booklet's numbers are auto-generated and the reference sweep greps for
  that exact shape, so a worksheet answer numbered Q1.1 would be read as a
  booklet question and reported as drift.
- **The sheets were generated from a content table, not hand-written.** The
  marks total appears in three places per sheet (`.namebar`, the toolbar
  hint, the per-part `.marks`) and CLAUDE.md asks for them to agree; the
  cheapest way to guarantee that is to never type the number. Verified
  across all ten, and against the index `.wl-marks` and the answer key.
- **Only worksheet 7 carries a Country part.** All the unit's First Nations
  content sits in Lesson 7 by design — it was deliberately gathered there.
  Bio puts a Country question on every sheet because its content is spread
  that way; copying that pattern into Space would have meant inventing
  connections lesson by lesson.

`.drawbox[data-h="md"]` was documented but had no rule, working only by
falling through to the base height — now stated explicitly.

### Landed — pracs stripped from both unit planners (1 Sep 2026)

Kodie's call: no practical or equipment-dependent activities in either
`planner.html`, or their Word twins. Removed the leaf-starch practical and its
write-up from Bio week 3, the quadrat survey, the classifying-plants prac, the
adaptation dice game, the sorting cards, the eutrophication demo; and from
Space the globe-and-torch and ball-and-lamp modelling, the shadow-stick
tracking, the solar-system scale model, the diffraction-grating spectroscope,
the night-sky viewing evening, and the specimen-handling framing of Lesson 4
(which now runs from the deck's photographs and the Elatina data table). Both
planners carry a note saying so.

**Scope: the planners only.** The decks, booklets and unit indexes still
describe these activities — Lesson 4's specimens are still in `deck4.html` and
on the Space index, and Bio §6 still carries its practical. If the pracs are
gone for good rather than "for now", those pages need the same pass.

### Landed — Space resequence: Lesson 3 to week 2, Lesson 4 optional (31 Aug 2026)

Kodie's call. Week 1 is now Lessons 1–2, week 2 is Lessons 3–5, and **Lesson 4
(Reading the Rocks) is an optional lesson** — badged on the unit index
(`.deck-card.is-ext` + `Optional · Specimens`), pilled on its own title slide,
and marked `optional` on the quiz page's topic chip.

Consequences that had to move with it:

- **The written assessment no longer covers §3.** It is drawn from §1, §2, §4,
  §5 and §6. You cannot assess content a class may not have been taught.
- **`quiz.js` gained `data-quiz-exclude`** — a comma-separated list of deck
  numbers to drop from the spaced-retrieval pool, applied after
  `data-quiz-before`. Decks 5–10 in Space carry `data-quiz-exclude="4"`, so a
  class that skipped Lesson 4 is never cold-called on rhythmites. The
  attribute is optional and absent markup behaves exactly as before.
- Index quiz chips reworded to match ("Quiz: Lessons 1–3, 5–6").

**Not done, deliberately:** the booklet still has §3 in sequence and unlabelled.
Adding an "optional" divider means a `.tex` edit and three `xelatex` passes, and
the answer key hardcodes `QN.M` question numbers — so it belongs in the same
pass as the outstanding booklet rebuild, not bolted on here. §3 keeps its
position, so nothing renumbered.

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

**Second use, 31 Aug 2026** — `year7-science/space/planner.html`, themed
`theme-space`. Four rows matching the week grouping the Space index already
declares (Week 4 is the above-level extension block), so the planner and the
index can never disagree. Word twin at
`7 Science/Space/Space_Unit_Planner_Yr7.docx`.

Other units can reuse the page type as-is: copy a `planner.html`, swap the rows
and the `theme-*` body class.

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
| `7 Science/Forces` — 6 decks, `experiments.html`, index, unit-local deck.css/js, booklet `.tex`/`.pdf`, 8 SVG figures, Ballista + Trebuchet lab tech sheets, 2 trebuchet investigation docx | `year7-science/forces` | Same unit-local shape bio and space had. Mostly a rename job. |
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
   `.aux` (never hand-numbered) — `node tools/check-bookrefs.js` verifies them.
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

- [ ] **`year7-science/bio-ecosystems/rubric.html` lost its body classes.**
      Noticed 8 Oct 2026 while rebuilding the sitemap for unrelated work.
      Commit `db7b36b` ("Update rubric.html", same day) left it with a bare
      `<body>` where every sibling gated page has
      `class="solutions-page theme-science"`. Three consequences: the
      `.lockscreen` loses its `.solutions-page` styling; the nav dot loses
      its colour, because `build-sitemap.js` reads the theme class off
      `<body>` into the tree's `k` field; and the unlock handler's
      documented swap of `body.solutions-page` → `body.rubric-page` has
      nothing to swap. **Not fixed here** — the page was being worked on
      the same day and this is someone else's in-flight edit. Its
      `<title>` also changed without a sitemap rebuild, so
      `node tools/build-sitemap.js` is owed either way; do both in one
      pass. **S**
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

- [ ] **Redraw the other primer figures from the old graph helper.**
      The 9 Oct pass covered exponentials only. The same helper drew
      the rest of the primer's figures and they show the same faults —
      seen in `Term4_RevisionExam_Slides.html` slides 9, 10, 34, 35
      (labels on the parabola, `x = 2` under `TP (2, −9)`, `√5 ≈ 2.236`
      on the curve) and the tree diagrams on 20 and 38 (branch labels
      overlapping). Ch1, Ch4, Ch6, Ch7 and Ch8 (~130 SVGs) not yet
      audited. Follow the conventions in the exponential-graphs Landed
      note. **M**
- [ ] **`&amp;amp;` in primer `data-topic` attributes.** The lesson tag
      reads "CAT 3 &AMP; WRAP-UP" on every topic slide —
      double-escaped in `Ch3A-E_4A-D_IndicesSurds_Slides.html` (46),
      `Ch4_2_MeasurementGeometry_Slides.html` (57) and
      `Term4_RevisionExam_Slides.html` (32). One replace each. **S**
- [ ] **Primer prose still mixes plain text and MathJax in one
      expression**, e.g. Ch3FL "x = log₂ 20 = \(\dfrac{\log 20}{\log
      2}\)" and Term4 "n = \(\dfrac{\log 2}{\log 1.05}\)". Sweep
      to whole-expression MathJax. **S–M**

### Tier 2 — Ports with HTML source (one to three sessions each)

These follow a known recipe. Read the "Legacy content" section of
CLAUDE.md before starting one — the class-rename vocabulary and the two
traps (strip inline `style=` *before* renaming classes; don't promote a
Recap slide to `.exit-slide`) are written down there.

- [ ] **Port `7 Science/Forces` → `year7-science/forces`. M** *(in progress — Kodie, 2026-10-06)*
      The cheapest real content win in the repo, and it completes Year 7
      Science's third unit.
  - [x] 6 decks off the unit-local `deck.css`/`deck.js` onto shared assets
        *(deck1 2026-10-06, decks 2–6 2026-10-07 — awaiting Kodie's review)*.
        Lab slides link the booklet PDF page until `experiments.html` is
        ported; repoint them then. Chips with no booklet content behind them
        (the "§N · Extension" slides) were dropped, not re-pointed. Shared
        `deck.css` gained `.cols.three`.
  - [ ] `experiments.html` — decide its page type (likely `course.css`
        section on the landing page, or a `profile.css` reference page)
  - [x] Unit landing page, `theme-science` *(done 2026-10-06 — lists only what is published; add cards as decks land)*
  - [ ] `booklet/` — `.tex` + PDF + `fonts/`, embedded via `.pdf-frame`
        — files copied 2026-10-06, linked from the landing page; not yet
        in a `.pdf-frame` page
  - [x] **Booklet numbering fixed** *(2026-10-06)*. `\sectiondiv{title}{summary}`
        now steps the real section counter and is followed by `\label{sec:N}`;
        every subsection has `\label{sub:N.M}`. Tasks (`\task`, `\task[a]`,
        `\taskpart{b}`, `\exttask`), questions (`\question{marks}{text}`) and
        figures (`\figcap`, `\expfigcap` → E-numbered) are all auto-numbered
        per section and auto-labelled `task:`/`q:`/`fig:`; experiments carry
        `\label{exp:N}`. Never type a number by hand. The beginner-skills
        block is §1.1–1.7, so the original Task 1.1/1.2a–c/Extension 1.3 are
        now Task 1.6/1.7a–c/Extension 1.8; questions were hand-numbered out of
        order (Q4 before Q3 in §2) and now run Q2.1–2.6 etc. Cover contents
        table gained a `\pageref` page column; stray `\label{LastPage}`
        removed (the `lastpage` package already defines it). 52 pp.
        Deck 1 chips re-derived from the `.aux`.
  - [ ] 8 SVG figures — theme colours to tokens, illustrative hues left alone
  - [x] Ballista + Trebuchet lab tech sheets as linked PDFs *(in `labs/`, Planning section of the index)*
  - [x] `.bookref` chips derived from the built `.aux` — 61 refs, all decks ✓
        (`node tools/check-bookrefs.js year7-science/forces`)
  - [x] Unit planner `planner.html`, 5 weeks; index grouped by the same weeks *(2026-10-07)*
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
