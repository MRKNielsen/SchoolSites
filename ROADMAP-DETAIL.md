# Build-out roadmap — inventory and task list

**Companion to `ROADMAP.md`**, which carries the working rules, the
per-session checklist and the guardrails, and is imported into every
Claude session. This file holds the detail: where the site is, what
"done" means, and every outstanding job in effort order.

Open this whenever you are picking up, finishing or adding work. Claim
items before starting (Tier 2+), tick and date them on landing, and add
anything you discover.

Last full audit: 16 Aug 2026. Last addition: 17 Oct 2026 (Applied Computing Unit 1 AOS 1 — dataset + all 16 decks).

Effort key: **S** = under one session · **M** = one to three sessions ·
**L** = several sessions, worth splitting.

---

## Part 1 — Where the site actually is

Fourteen subject folders exist. Five carry content; nine are identical
35-line stub index pages, commented out of the root year picker.

| Subject | State | What's there |
|---|---|---|
| year7-science | **Built** | `bio-ecosystems` (11 decks, 11 worksheets + collated booklet & gated answer copy, quiz, gated solutions + rubric, booklet, research portfolio, bandicoot profile) · `space` (8 decks, quiz, booklet) |
| year12-algorithmics | **Built** | `unit-4` (13 slide decks, 9 marimo workbooks, hub, 7 problem sets, 7 revision PDFs, SAT brief, solutions) |
| year12-specialist | **Built** | `term-3` (11 decks, hub, 5 problem sets, SAC revision) |
| year10-mathematics | **Built** | `10methods-primer` (9 decks + hub) |
| year11-methods | **Built, on debt** | `chapter-9` (7 decks), `chapter-11` (2 decks) — still inline styles |
| year11-applied-computing | **In build** | Subject landing, Unit 1 + Unit 2 hubs, Unit 1 + Unit 2 outlines, PSM reference, the Unit 1 AOS 1 dataset, and **all 16 AOS 1 decks** (154 slides). No workbooks, worksheets or assessments yet |
| year7-mathematics | Stub | — |
| year8-mathematics | Stub | — |
| year9-mathematics | Stub | — |
| year10-algorithmics | Stub | — |
| year11-algorithmics | Stub | — |
| year11-specialist | Stub | — |
| year11-foundation | Stub | — |
| year12-methods | Stub | — |
| year12-foundation | Stub | — |

Totals: 70 decks, 22 worksheets, 3 hubs, 2 quizzes, 1 profile page,
8 gated pages.

### Landed — Space rubric takes marks, not ticks (21 Oct 2026)

`year7-science/space/rubric.html` — each grid cell is now a number box for
that part's mark, out of the figure under its column heading. Blank = not
attempted, 0 = attempted and wrong, half marks allowed (`1.5`, `1½`). Enter
moves down the column. A new **Mark** column shows each student's total out
of 50, and the printed sheet's overall line gives the score.

Bands still come from the evidence: a part counts towards its rubric cell at
half its marks or more (Kodie's call). Allocations are read off
`CAT_5_Astronomy_Test_2026_FINAL.pdf` and recorded, with the reasoning for
each split, above `CRITERIA` in `tools/space_rubric_data.py`.

- **The paper's Q7 header says "(11 marks)"** but its parts sum to
  4+1+1+1+1+1+1+2 = 12, and 12 is what makes the paper total 50. The tool
  uses 12. Fix the header on the paper.
- **Q11's diagram/explanation split isn't on the paper**; 2 + 2 is assumed.
  Change `max` on Q11a/Q11b if the marking key says otherwise.

Save format v2; v1 tick files and autosaves convert on open. CSV columns
hold the mark (headings now read e.g. `Q7 (a) /4`); a `y` reads as full
marks. 58 checks in `tools/test-space-rubric.js`, all passing, and the grid
and print view checked rendered in Chromium. bio's rubric is unchanged.

**Fixed 22 Oct — pronouns.** Both ways in dropped every pronoun to "they":
the class-list roll still read bio's third column, and the CSV import still
passed bio's species argument into Space's `newStudent(name, pron)`. Both now
go through `pronOf()` (whole-word: "her" no longer reads as "he"). The CSV
template and export lose the Species column; an old file that has one still
imports. Four new checks in `test-space-rubric.js`, confirmed to fail against
the old code. bio's own roll has the same "her" → "he" quirk (bio unchanged).

### Landed — red answer copy for Revision Worksheet 1 (21 Oct 2026)

`year7-science/space/worksheet-revision1-solutions.html` — the Revision 1
sheet with answers written into its own furniture, in the same red overlay
as the other Space answer copies. 51 written-in answers, 19 written-on line
blocks, 42 marking notes carrying the mark split and the common errors.
Linked from **Staff only** on the unit index.

**Both copies come out of one file now.** `tools/revision1_worksheet.py`
grew an `ANSWERS` flag and `--student` / `--answers` / `--both`; the
question wording exists once, so the key cannot drift from the sheet the
way a hand-copied one does. The student copy rebuilds byte-identical,
which the build asserts, along with the overlay never leaking into it.

Answers are the deck's own — every one lifted from the matching answer
slide (4, 7, 9, 11, 14, 16, 19, 21, 23, 25) and the source slide named in a
comment — so the key marks what the class was actually shown rather than a
second derivation of it.

Two checks, because one of them is the one that failed last time:

- `verify()` **strips the overlay back off and requires the student
  sheet's markup exactly.** Counting filled slots would not catch an
  answer that ate a question, a question missing from one copy, or a
  `data-lines` changed under an answer. It also names the deliberate
  blanks: the exit self-rating column is the student's own judgement.
- `tools/test-revision1-worksheet.py` breaks each defect class in turn and
  **requires `verify()` to raise** — 7 of 7 caught. A check nobody has
  seen fail is not evidence; that is exactly how the rubric shipped with
  12,600 characters missing and a green build.

**Fixed while building it: `revision1.html` slide 25 drew the orbit as a
3:1 ellipse with the Sun at its centre** — on the model-answer slide whose
fourth mark is *"says explicitly that it is not caused by distance"*. It is
now a circle (r=155) with both Earth positions exactly on it, asserted by
computing each Earth's distance to the Sun. This is the second time this
figure has been drawn that way in this repo (Space deck 2 slide 7 was the
first), so CLAUDE.md's circular-orbit rule now says plainly that it covers
every hand-drawn orbit, not just `seasonsim`. The figure also gained
per-position captions, lost a duplicated loose caption in favour of a
`.figcap`, and took `.graph-card.narrow` so the squarer aspect does not
make the slide taller than it was.

Also fixed: the one `style="color:#C2410C"` the port left behind, now
`var(--cas)` — the system's Year 8 / extension colour, matching `.y8box`.

`check-gated.js` flags the new page as **PLACEHOLDER** until Kodie encrypts
`worksheet-revision1-solutions-payload.html` through `tools/staff-crypt.html`
and pastes the emitted line over the placeholder. The shell keeps any real
`var BLOB` already present, so rebuilding afterwards does not wipe it.

Rebuild with `python tools/revision1_figs.py && python
tools/revision1_worksheet.py --both && python
tools/test-revision1-worksheet.py`.

**Not verified:** parts 1, 3, 7, 8 and 10 of the answer copy have been
looked at rendered. Parts 2, 4, 5, 6, 9 are built by the same helpers and
the round trip proves their wording, but nobody has seen them on paper.

### Landed — CAT revision lesson 1 + its worksheet (20 Oct 2026)

`year7-science/space/revision1.html` (26 slides) and
`worksheet-revision1.html`, the fill-in sheet that goes with them, plus the
original `Space_CAT_Revision_Worksheet.pdf` kept beside it as a download.
Both linked from a new **Revision** section on the unit index, placed so a
second revision lesson drops in beside the first.

**The deck was a port, not a drop-in.** The source was a slide export: 688
inline `style=` attributes, 53 hardcoded hexes, 24 inline SVGs, its own
1920x1080 scaling script, and `.slide` as the only class — everything else
styled by element. `tools/revision1_build.py` maps by the *role* the inline
style encodes rather than renaming classes, because there were no classes to
rename. Result: 0 inline styles, 0 per-page `<style>`, and the only hexes
left are illustrative (Sun gold, lit/unlit Moon, planet hues), which is what
CLAUDE.md asks for.

Three things the port had to get right, each of which broke first:

- **The source bodies already ended with `</section>`.** Adding another
  closed `<main>` early and flattened all 26 slides into one scrolling
  column — every slide's teacher notes stacked on top of each other. Caught
  by counting openers against closers: 26 against 51.
- **Figure labels were absolutely positioned over the SVGs** in canvas
  coordinates. Stripping that positioning — which the rest of the port does
  — dropped them out of the pictures and left them as loose sentences
  underneath. The container is `width:Wpx;height:Hpx` and the figure's
  viewBox is `0 0 W H`, so the coordinates transfer straight into the SVG as
  `<text>`, which also makes them scale with the figure.
- **Labels coloured for a dark slide vanish on paper.** In the worksheet
  every figure label is ink with a white halo (`paint-order="stroke"`), so
  it reads on blank paper and on a dark fill alike.

A text-coverage check fails the build if any visible string from the source
is missing from the output — the lesson from the rubric, where a splice
quietly deleted 12,600 characters and the checks could not see it. The one
deliberate exception is the cover, hand-authored to the house title-slide
pattern (`.eyebrow`, `h1`, `.subtitle`, `.head-meta` pills, `.start-hint`).

The worksheet reuses the deck's figures rather than redrawing them
(`tools/revision1_figs.py` lifts and greyscales them), so sheet and slides
cannot drift apart. It deliberately carries **no sheet total**: the source
marks some tasks and not others, because the unmarked ones are practice, and
a total over a mixed sheet would mean nothing. Every other worksheet in this
unit does carry one.

Checked: the Moon phase figure is **southern hemisphere** — the lit arc
sweep flags put waxing on the left — matching the booklet figure corrected
on 15 Oct and the `orbit.js` default.

New shared component: `.part-title .pt-meta` in worksheet.css, the quiet
note after a task title saying how the task is done ("pairs", "on your own",
"show all working").

Rebuild with:

```bash
python tools/revision1_build.py       # the deck
python tools/revision1_figs.py        # lift + greyscale its figures
python tools/revision1_worksheet.py   # the worksheet
node tools/build-sitemap.js && node tools/check-links.js
```

**Not verified:** I have looked at the title slide, slides 2–5, 12–13 and the
worksheet's first four tasks rendered. The remaining slides are built by the
same mapping and the text check proves nothing was lost, but nobody has seen
them on a projector yet.

### Landed — Space rubric ungated (19 Oct 2026)

`space/rubric.html` is now a plain page: no `var BLOB`, no lockscreen, the
tool inline. `tools/build_space_rubric.py` writes the finished page rather
than a payload for staff-crypt, and deletes the old `rubric-payload.html`.

**Why.** Gated, every content fix cost a decrypt / edit / re-encrypt / paste
round that could not be checked until after it shipped. Four of those in a
day, three for defects a glance at the rendered page would have caught: a
broken build that threw on boot, a back link reading "Biodiversity &
Ecosystems", and a CSV exporting as `-ecosystem-marks.csv`. The marks and
student names live in `localStorage`, never in the page, so the lock only
ever covered the criteria and band descriptors — which a student arguably
benefits from reading. bio's rubric has been ungated since 8 Oct anyway.

Consequences handled:

- `data-nosearch` on `<body>` keeps it out of `searchindex.js`. Its visible
  text is the CAT 5 mark scheme in outline, and the grid is rebuilt by JS so
  the indexer would only capture a static shell — the same reasoning that
  excludes the orbit/season/binomial/lever widgets. Still in the nav tree,
  still reachable by anyone with the link. Drop the attribute and rebuild
  the sitemap to make it searchable.
- The index card moved out of *Staff only* (whose subtitle promises a
  password) into *Planning & marking*, renamed from *Planning*, with the
  note that marks stay in your own browser.
- `check-gated.js` keys off `*-payload.html`, so deleting the payload
  retires the page from its checks with no change to the tool.
- `tools/test-space-rubric.js` now loads `rubric.html` whole instead of
  injecting a decrypted payload — closer to what actually ships.

If it is ever gated again: the shell is at `rubric.html` in `62a193d`, and
**it will not work as-is** — it used the single-layer `{salt, iv, iter, ct}`
unlock and cannot open a v2 blob. Take the v2 implementation from
`worksheet-revision-solutions.html`.

Also fixed in this pass, all found by looking at it rendered rather than
testing it: the masthead back link said "Biodiversity & Ecosystems"; the CSV
downloaded as `<class>-ecosystem-marks-<date>.csv`; and a replacement of
mine had produced "the Year 7/8 Year 7 Space unit". The builder now sweeps
the whole page body for bio wording instead of checking a handful of named
strings.

### Fixed — Space rubric shipped broken, and why the checks missed it (19 Oct 2026)

The first build of `space/rubric-payload.html` was **missing ~12,600
characters** and threw `ReferenceError: restore is not defined` on boot. The
page unlocked, drew its tab bar and panel headings, and then stopped — so it
looked like a rubric with no rubric in it. Kodie found it by opening it.

Cause: a splice in `tools/build_space_rubric.py` anchored on
`const rows = [`, which occurs **three times** in bio's payload. It matched
the first (inside `exportCSV`) and deleted everything from there to the end
of `demo()`, taking `persist`, `restore`, `demo`, `importCSV`, `importJSON`,
`parseCSV` and `handleFile` with it. `span_of()` asserted that its *end*
literal was findable but never that its *start* was unique — unlike
`sub1()`, which did check.

**The checks could not have caught it.** They extracted the script and cut
it at the render functions to get a DOM-free slice to run under node. Every
deleted function lived below that cut. The slice passed, and passed
honestly — it just could not see the half of the file that was gone. A test
that only exercises the part you kept proves nothing about the part you
spliced.

Three things now stand between this and a repeat:

- `span_of()` asserts its start literal is unique, and the demo splice is
  anchored with a new `function_span()` that finds `function demo(` and
  walks braces instead of matching indentation.
- The builder diffs the set of top-level functions against bio's and fails
  if any vanished that it did not mean to remove, then explicitly confirms
  `restore`, `persist`, `demo`, `renderAll` and `boot` all still exist.
- **`node tools/test-space-rubric.js`** boots the payload in jsdom exactly
  as `rubric.html` does after unlocking, then drives it: enters a class,
  cycles ticks through successful / not-attempted / clear, marks a student
  out and checks the bands, comment, teaching groups and printable rubric,
  and round-trips the autosave. Run it after every rebuild. Needs
  `npm install jsdom`.

Found while fixing it: the autosave key was still bio's
`"ecosystem-rubric:v1"`, so a teacher with both rubrics open in one browser
would have had them share a single localStorage slot and silently overwrite
each other's marks. Now `"astronomy-rubric:v1"`.

Two traps the harness itself hit, noted in its header: `boot()` is async, so
it must be settled before the UI is driven or `demo()` lands on top of the
test's class; and `applyRoll()` deliberately keeps the marks of any student
already listed by name, so a test roll must not reuse the demo's names.

**Kodie must re-encrypt**: the blob pasted in on 19 Oct was made from the
broken payload. Re-run `tools/staff-crypt.html` against the rebuilt one.

### Landed — Space CAT 5 rubric & report generator (19 Oct 2026)

`year7-science/space/rubric.html` — the Astronomy Test marking tool, built
on bio's rubric engine. Staff-gated, on the design system
(`tokens.css` + `solutions.css`, `theme-space`, shared `.lockscreen`),
linked from the unit index under *Staff only*.

**The engine is shared; only the data differs**, so
`space/rubric-payload.html` is generated by `tools/build_space_rubric.py`
rather than hand-written. Every splice asserts it matched exactly once, so
a future change to bio's engine surfaces as a build failure instead of a
quietly half-converted file. The builder also strips bio's per-student
species (name + optional pronoun is all a written test needs) and bio's
Part D closer, which keyed on a strand `s7` that Space has no equivalent of
and would otherwise have sat there as dead bio prose.

**Six strands, one per topic taught**, weighted by the test's own marks —
9 + 12 + 11 + 12 + 3 + 3 = 50 — so the overall level is weighted exactly as
the paper is. 34 tickable criteria across the 11 questions. The two
3-mark strands (First Nations astronomy, space sustainability) use
`maxBand: 3` rather than being padded to four levels on three marks.

Three things learned that apply to any future rubric:

- A strand needs a **complete band ladder to its own `maxBand`**.
  `topCell()` walks down from `maxBand` and `missedBelow()` penalises
  gaps, so one empty band in the middle silently caps that strand. There
  is now a test for it.
- bio ranks strengths on `band/maxBand`, which only works when every
  strand shares a `maxBand`. Here band 2 of 3 (0.67) beat band 2 of 4
  (0.50), so a student at band 2 across the board was told their
  strengths were the two 3-mark questions. Strengths now scale by
  `√weight`, and next steps rank on the **gap** rather than the same
  figure — using one figure for both makes a low-`maxBand` strand come
  out as a strength and a next step at once.
- The unlock guard has to test `BLOB.ct`, not `BLOB`. A placeholder blob
  is a truthy object, so bio's `!BLOB` check reports "Incorrect password"
  when the real fault is an unencrypted payload.

Verified by running the engine under node with a DOM shim: band ladders
complete, weights summing to 50, full marks giving top band on every
strand, the developmental penalty still biting (band 4 alone awards 0),
the unassessed case handled, and generated comments free of
`{their}`/undefined. Also checked statically that every id the script
reaches for exists in the markup and no strand or criterion reference
dangles. **Not yet seen rendered in a browser** — the preview panel
would not open it, so give it a look before using it with a class.

**Needs Kodie:** encrypt `rubric-payload.html` through
`tools/staff-crypt.html` and paste the `var BLOB` line in. It ships as a
placeholder, so the page locks but cannot unlock; `check-gated.js` reports
it until then.

### Landed — Space booklet Moon phases flipped to southern (15 Oct 2026)

The eight-phase row in booklet §3.1 was drawn for the **Northern
Hemisphere** — waxing lit on the right. Everything else in the unit was
already southern and explicit about it: deck 3 uses `orbit.js`, which
defaults to `data-hemisphere="south"`; worksheet 3 asks for a waxing
crescent "seen from Melbourne"; the revision worksheet's self-check says
"waxing = lit on the left"; and the key for W3.6 spells out that a waxing
Moon is lit on the left here and calls it worth naming explicitly. So the
one static figure in the unit contradicted the widget, both worksheets and
the answer key — a student shading from the booklet picture would have
been marked wrong by the key.

Cause worth recording: `\\moonphase`'s second argument was documented as
`{mirror: 1=waxing, -1=waning}`. Waxing and lit-side are opposite in the
two hemispheres, so a macro keyed on *waxing* silently bakes in a
hemisphere. It now takes `{lit side: -1 = left, +1 = right}` and the
hemisphere is stated once, in the comment above it. Same trap as the
seasons widget: the parameter that looks like the physics isn't.

Also added a *Which side is lit depends on where you are standing*
infobox beside the existing misconception box, and the subsection heading
now reads "as seen from Melbourne".

Rebuilt ×3: still 48 pages, every `\\newlabel` page unchanged, all 67 deck
`.bookref` chips still correct. `Space_Lesson1_Print.tex` was regenerated
because it carries the preamble verbatim — it never calls `\\moonphase`,
so its committed PDF is byte-identical in rendered text and did not need
rebuilding. **The unit booklet PDF does, and has not been.**

One accessibility fix in passing: the shading question on
`worksheet-revision.html` had an `aria-label` reading "(a) waxing crescent
and (b) waning gibbous" against printed labels of "(a) Waxing gibbous" and
"(b) Waning crescent" — crescent and gibbous swapped, so a screen-reader
user got a different question. Label corrected to match what is printed.

### Landed — Trebuchet Investigation booklet + teacher copy (14 Oct 2026)

`year7-science/forces/booklet/Trebuchet_Investigation_Yr7_8.tex` + `.pdf` —
the culminating investigation (Lessons 15–18) rebuilt as its own 18-page
booklet, embedded on `forces/trebuchet-investigation.html` and linked from
the unit index (*Student resources*, and lesson cards 15–18). Same look and
four-part shape as the Lesson Booklet's experiment lessons, preamble copied
from it: A Reading (*Warwolf*), B Planning, C Results and analysis, D Above
level. Kodie's booklet rules apply (no marks, red first rows, 1.5 cm rows).

- **Why it changed.** The old task measured *g* with g = 2h/t² from the
  release height and the whole flight time. That only holds with zero
  initial vertical velocity; a trebuchet releases upwards (about 40–50°),
  so a typical desktop launch (h 0.81 m, t 1.09 s) gives 1.4 m/s² however
  carefully students work. It also had no real independent variable. Now
  the IV is counterweight mass (5 levels × 3 launches), DV1 is range, and
  DV2 is the arm's peak spin from a **PASCO PS-3223** gyroscope strapped
  to the long arm near the pivot; tip speed v = ω × L ties it to the lever
  lesson. Measuring g survives only as a Part D drop test of the sensor
  (`ext:drop`), where the formula does apply because it starts from rest.
  The old-method critique and a release-pin design task were cut at
  Kodie's request (14 Oct).
- **Assessed by an open-booklet test (15 Oct).** Lesson 17 is now the core
  analysis lesson (no longer an optional launch buffer) and Lesson 18 is
  the *Trebuchet Investigation Test*: Section A on the student's own
  results (towards), Section B a common unseen data set — beanbag mass
  changed, one answer key (at), Section C above level. Level is read off
  Section B, with C for above. **The paper is staff material and is not in
  this repo**: `.tex`, teacher wrapper and PDFs live in OneDrive at
  `7 Science/Forces/Trebuchet_Test/`, building against `../fonts/`. The
  unit is now 18 lessons with 2 optional (11, 14).
- **Teacher copy** — `Trebuchet_Investigation_Yr7_8_Teacher.tex` + PDF,
  **gitignored**, using the Ch3G–3L one-source/two-builds pattern: every
  box, cell, blank and graph filled in red, then three pages of teacher
  notes (why it changed, prep, SPARKvue, lesson timing, expected results,
  an assessment guide by inquiry-skill criterion, misconceptions). There is
  no gated HTML page for it. Build the student copy first — the teacher
  build reads its `.abx`, so both paginate identically.
- **The sample answers are modelled, not measured** — a rigid-arm + sling
  simulation with pivot friction and drag (0.40/0.10 m arm, 25 g beanbag,
  600–1000 g). The shape to expect: range close to linear (about 0.8 m per
  100 g); peak spin up only about 16% and levelling off (the counterweight
  can't beat free fall, about 19 rad/s on that arm); the projectile leaves
  at 1.5–2× the tip speed because of the sling. Swap in a real class set
  once one exists.
- **Page filling** — `booklet/fill.py` (Python + Pillow + pdftoppm) writes
  the `.abx` the booklet reads. It leaves 8 mm at every page foot: TeX Live
  2022 and 2023 set this booklet a few mm apart, and with less slack a box
  changed page on 2022. Re-run it after any content change.
- `labs/Trebuchet_Lab_Tech_Sheet` rewritten for the new kit (slotted masses,
  beanbags, sensors; no cameras or plumb line). `planner.html` weeks 5–6
  follow the booklet; the summative is judged against the teacher copy's
  assessment guide, not the old /137 rubric.

### Landed — Ch8 Probability question booklet (14 Oct 2026)

`10methods-primer/booklet/Ch8_Probability_Question_Booklet.tex` + `.pdf`
(44 pp, sections 8A–8J; 8K is not taught) — the fourth primer booklet,
in the Ch3F–3L format: per section a refbox of textbook example numbers
and question sets with pages, two original worked examples, then five
hurdle questions on a new page. Diagrams are TikZ macros in the preamble
(spinner, Venn with shaded-region variant, two-stage tree with an
outcome/probability column, three-stage coin tree, outcome array with a
crossed-out diagonal for "without replacement", counting boxes). Gaps
are filled rather than left bare: each worked example and hurdle is
measured and placed whole, and leftover space becomes Notes lines or
working lines. All worked and hurdle answers were checked by script.
Linked as `booklet-probability.html` (built like `booklet-exponentials.html`;
8B links to the 8B+ lesson, slide #8), with a "Question booklet" chip on
`unit8-probability.html` and on the Unit 8 topic button. No answer copy
yet.

### Landed — Space revision worksheet + answer copy (13–14 Oct 2026)

`year7-science/space/worksheet-revision.html` — two 50-minute lessons of
revision for the written Astronomy Test (CAT 5), covering Lessons 1–7:
Session 1 is Parts A–E (41 marks), Session 2 Parts F–J (42), 83 in all,
10 printed pages with each session starting on a fresh page. Linked from
the Space index under *Student resources*.

- **It deliberately shares no question or question format with the
  test.** It revises the same content, but in different question types.
  If the test changes, re-check the revision sheet against it rather than
  copying test items in. Keep test details out of this repo — it is
  public, and the answer copy also opens with the student password.
- The answer copy is `worksheet-revision-solutions.html`, a gated shell
  copied from bio's `worksheets-all-solutions.html`, linked under *Staff
  only*. It accepts the staff and the student password.
- Lesson 4 is optional and not assessed, so it appears only in a
  fast-finisher box.
- New shared component: `.ws-fig` in `worksheet.css` (see CLAUDE.md).
- `tools/check-gated.js`, two fixes: the placeholder test now matches the
  unquoted `{v:2, iv:"", ct:"", keys:[]}` form CLAUDE.md documents (it only
  caught `"ct":""`, so `portfolio-solutions.html` was never flagged), and the
  booklet diff is skipped for payloads with no `qref` Q-numbers, so a
  worksheet answer copy is no longer reported as missing every question.

### Landed — primer course home split into topic pages (14 Oct 2026)

`10methods-primer/index.html` was nine stacked chapter sections (34 week
cards, ~4550 px tall). It is now the header and milestone timeline plus a
3×3 grid of topic buttons that fits one 1080p window (and 1366×768).
Each button opens a topic page — `unit1-linear-relations.html` …
`unit8-probability.html`, `wrapup-revision-cat3.html` — carrying that
chapter's week cards verbatim (all 132 lesson links checked against the
old page), its deck / booklet pills, and previous / next topic links.
New components at the end of `hub.css` ("Topic buttons"); see CLAUDE.md,
Course hub pages. A one-screen nine-column "year grid" was tried first
the same day and dropped — too dense to read comfortably.

### Landed — Ch3F–3L question booklet linked (14 Oct 2026)

`booklet/Ch3FL_ExponentialsLogs_Question_Booklet.pdf` (24 pp, 3F–3L) now
has a page, `10methods-primer/booklet-exponentials.html`, built the same
way as `booklet-trigonometry.html`: `.pdf-frame` embed, open/download
buttons, and a section strip linking each section to its deck slide. The
primer hub's 3F–3L chapter carries a "Question booklet" chip beside
"Open deck". The Ch3G–3L example set below is deliberately **not**
linked.

### Landed — Ch3G–3L worked example set, print booklet (14 Oct 2026)

`10methods-primer/booklet/Ch3G-L_Example_Set.tex` + `.pdf` — a 25-page
A4 booklet of original worked examples for 3G–3L (27 examples, 6 key-idea
panels, 6 fix-the-error tasks, 30 practice questions + 6 mixed). Each
section: Key ideas → I do (fully worked) → We do (write-in blanks and
1.5 cm tables, first row in red) → Fix it → You do. Not yet linked from
the site — it was asked for as a print document.

New pattern, reusable for any booklet that needs a teacher copy:

- **One source, two builds.** The student `.tex` holds no answers; every
  blank is `\\blank{width}{key}`, `\\cell{key}` or `\\tans{key}`.
  `Ch3G-L_Example_Set_Teacher.tex` defines every key with `\\defans`
  inside `\\teacheranswers` and `\\input`s the student file, which prints
  them in red. The wrapper and its PDF are **gitignored** by path (staff
  material). A missing key prints `??key??` — grep the teacher PDF.
- **Both copies paginate identically** (teacher answers are `\\smash`ed
  or zero-height), so "page 14" means the same page in both.
- **No bare gaps.** Example boxes are typeset, measured, then placed
  whole; if one won't fit, the rest of the page becomes ruled *Notes*
  lines (`\\placeorfill`). Questions do the same with plain lines, and
  each section ends with lines to the foot of the page. Writing lines are
  8 mm everywhere (`\\rulepitch`), which is what lets `\\tans` sit on them.

### Landed — Year 10 exponential graphs redrawn (9 Oct 2026)

All ten figures in `10methods-primer/Ch3FL_ExponentialsLogs_Slides.html`
plus the compound-interest graph on slide 14 of
`Term4_RevisionExam_Slides.html`. The originals came out of the old JS
deck's graph helper: 310 px wide, no scale, curve labels written on top
of the curve, coordinate labels colliding with each other (`(3, ?)` sat
exactly on `V = 30000(0.88)ⁿ`), the `asymptote y = 0` label clipped off the
right edge, money curves drawn into negative years, and the compound/simple
graph with no x-axis at all.

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
every `\\newlabel` page unchanged, all 67 deck `.bookref` chips still
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
shield covers all three), and the ISS gravity figure read 88% in the
recap against "about 90%" on two slides.

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

Kodies call: no practical or equipment-dependent activities in either
`planner.html`, or their Word twins. Removed the leaf-starch practical and its
write-up from Bio week 3, the quadrat survey, the classifying-plants prac,
the adaptation dice game, the sorting cards, the eutrophication demo; and from
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

Kodies call. Week 1 is now Lessons 1–2, week 2 is Lessons 3–5, and **Lesson 4
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
declares (Week 4 is the above-level extension block), so the planner and
the index can never disagree. Word twin at
`7 Science/Space/Space_Unit_Planner_Yr7.docx`.

Other units can reuse the page type as-is: copy a `planner.html`, swap the rows
and the `theme-*` body class.

### Landed — research portfolio answer key (25 Aug 2026)

`year7-science/bio-ecosystems/portfolio-solutions.html` — model answers and
marking criteria for all 11 stages of the Research Portfolio, plus the front
matter and the closing self-check. Linked from the unit index's *Staff only*
group and from a new *Staff only* section on `research-portfolio.html`.

Three things worth knowing before editing it:

- **The portfolio is unmarked and always was.** `\\markscount` is a no-op in
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

### Landed — Year 11 Applied Computing scaffold (3 Sep 2026)

`year11-applied-computing` is a new VCE subject built against the
**Applied Computing Study Design 2025–**, for first teaching in 2027.
What exists is the frame, not the content:

- Subject landing (`course.css`), Unit 1 and Unit 2 hubs (`hub.css`,
  16-week grids on the 2027 Victorian term calendar), Unit 1 and Unit 2
  outlines and a shared problem-solving methodology reference (all
  `profile.css`).
- New `theme-computing` in tokens.css (deep cyan-blue `--c-cyber-700`
  `#0369a1`) plus its `.sn-t-computing` dot in sitenav.css. It is
  deliberately *not* the Algorithmics teal — the two computing subjects
  sit next to each other in the Year 11/12 tabs and in the nav drawer,
  and a near-identical dot makes them unreadable.
- Uncommented in the root year picker (Year 11 panel).

Two things worth knowing before adding content:

- **The outlines and the PSM page are generated from the study design
  `.docx`, not typed.** The PSM page's Unit 1 / Unit 2 applicability
  columns come from the `·` marks in the study design's own
  specification tables (columns 3 and 4 of a 9-column grid; the activity
  names sit in vertically-merged cells, so a naive `python-docx` read
  mis-groups them). If the study design is amended, regenerate rather
  than hand-patch.
- **The PSM specification and the key knowledge lists disagree by
  design.** Ideation is unticked for both Applied Computing units in the
  specification table but is explicitly listed in Unit 2 AOS 1 key
  knowledge. That is not an extraction error — don't "fix" it.

Course design decisions recorded: Python as the OOP language (so the
marimo workbooks and the assessed language are the same), SQL against a
relational database for Unit 1 AOS 1. Unit 1 = Semester 1, Unit 2 =
Semester 2.

### Landed — Year 11 Applied Computing, Unit 1 AOS 1 dataset and first decks (17 Oct 2026)

**The teaching dataset is built** at `year11-applied-computing/unit-1/data/`.
Victorian climate observations, calendar year 2025: 4 regions, 6 stations, 2190
daily observations across three normalised tables.

It is **synthetic**, and deliberately so. Structure mirrors the Bureau of
Meteorology's daily observations and each station's annual mean maximum, mean
minimum and rainfall are calibrated to that station's published climate normals,
so the figures behave realistically — but it is not a Bureau extract and the
data dictionary says so in its first paragraph. Synthetic was chosen because
every fault in the dirty extract is then *engineered and documented*, which gives
the cleaning task a known correct answer and makes it auto-checkable. Real data
has whatever faults it happens to have.

Ships as: the dirty extract (`observations_raw.csv`, 2208 rows, nine fault
classes), the same data as a staging table (`climate-raw.db`), the clean
normalised CSVs, a SQLite database with keys and CHECK constraints
(`climate.db`), an XLSX for the spreadsheet weeks, and a generated data
dictionary.

**Two things are deliberately NOT in this repo**, because it is public: the
cleaning answer key, and the four generator scripts — they reveal every
injected fault. They live with the staff material and should go into the private
autograder repo when it exists.

**Decks T1 and T2 are built** (`unit-1/slides/`), on shared assets, theme-computing,
no inline styles, verified rendering with no slide overflow. A deck template file
was deliberately not created: the first real deck is the reference, which avoids
a placeholder file in a repo whose rules forbid them.

Remaining in Unit 1 AOS 1: decks T3–T16, eight marimo workbooks, eight
worksheets, the booklet and the Outcome 1 task.

### Landed — Unit 1 AOS 1 decks complete (17 Oct 2026)

All sixteen Area of Study 1 decks are built and wired into the hub week
cards, 154 slides in total. Every key-knowledge dot-point in Outcome 1 is
covered by exactly one deck.

Built to Kodie's house style throughout: a key-vocabulary starter slide
opens every lesson, every **I do** worked example is followed by a **We do**
question, and there are no *You do* blocks. Current chrome on all of them
(slide-jump menu, "reveals then advances" keyhint, empty `.counter`).

**The decks are generated, not hand-typed.** A small generator held the
boilerplate so house style is byte-identical across all sixteen; the content
is authored per deck. The generator lives with the staff material, not in
this repo — it is a one-off, not a tool anyone needs to maintain.

Two verification steps worth repeating for any later deck set:

- **Every SQL query in T12–T14 was run against `climate.db` before shipping.**
  Thirteen queries, all returning the rows the slide implies. A deck that
  teaches a query which does not run is worse than no deck.
- **Every quoted statistic was recomputed from the dataset.** This caught one
  error — T15 claimed Mildura had 56 rain days, a figure from before the
  dataset was recalibrated against Bureau normals. It has 76.

One honesty fix: T4's worked example shows a row carrying six faults at once.
No real row in the extract is that bad (checked — none carries even three),
so the slide now says plainly that the row is constructed from six faults
that are genuinely in the file.

Remaining in Unit 1 AOS 1: eight marimo workbooks, eight worksheets, the
booklet and the Outcome 1 task.

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

- [ ] **Encrypt `year7-science/space/worksheet-revision-solutions.html`.**
      Ships with a placeholder blob until the staff password is applied:
      run `worksheet-revision-solutions-payload.html` through
      `tools/staff-crypt.html`, paste the line over `var BLOB`, then
      `node tools/check-gated.js`. **S**
- [ ] **Space deck 6 understates the debris energy by 100×.** The "We do"
      slide says a 10 g bolt at 7,800 m/s has "20× more kinetic energy than
      a cricket ball", but its own figures are 304,200 J against 152 J,
      which is about 2,000×. Found 13 Oct 2026 while writing the revision
      sheet; not changed, because it is someone else's deck. **S**
- [ ] **`check-gated.js` reports a page with no blob at all as "ok".** Its
      placeholder test fires on a blob with an empty `ct`, so a gated page
      that has lost its `var BLOB` line entirely passes silently —
      `bio-ecosystems/rubric.html` does exactly this today. One extra
      branch: payload exists, page has no `var BLOB` → report it. **S**
      *(found 19 Oct 2026 while building the Space rubric)*
- [ ] **`year7-science/bio-ecosystems/rubric.html` lost its body classes
      — and its lock.** Revisited 19 Oct: as well as the bare `<body>`
      below, the page now has **no `var BLOB` and no lockscreen**, so the
      marking tool and its band descriptors are publicly readable, and it
      no longer links `tokens.css`/`solutions.css` (own palette and
      fonts). Possibly deliberate; flagging rather than reverting, since
      four commits that day were clearly intentional work. If it should be
      gated again, `space/rubric.html` is now the clean example, or
      `git show e8d6086:year7-science/bio-ecosystems/rubric.html`.
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

- [ ] **Encrypt `year7-science/space/solutions.html`.** It ships
      `var BLOB = {salt:"", iv:"", iter:0, ct:""}` — the page locks but
      can never unlock, which is worse than not shipping it. The
      plaintext `solutions-payload.html` is right there (and correctly
      gitignored). Run it through `tools/staff-crypt.html`, paste the
      emitted line over the placeholder. **S**
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
- [ ] **Year 11 Applied Computing content → `year11-applied-computing`.
      L** Scaffold landed 3 Sep 2026 (see Part 1); the frame, outlines
      and PSM reference are done. Outstanding, in teaching order:
      Unit 1 AOS 1 decks (weeks 1–8) and the database/SQL folio;
      Unit 1 AOS 2 Python decks (weeks 9–16) and folio; marimo workbooks
      for both; LaTeX assessment booklets under each unit's `booklet/`;
      Unit 2 AOS 1 project scaffolding and AOS 2 cyber security decks
      plus the teacher-provided case study. Unit 1 is the half to build
      first — it is taught in Semester 1. *(in progress — Kodie, 17 Oct 2026)*
      Dataset and all 16 AOS 1 decks landed 17 Oct 2026; see Part 1.

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
