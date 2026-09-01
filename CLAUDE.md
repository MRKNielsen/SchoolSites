# KNISchoolSites — instructions for Claude sessions

This repo is a GitHub Pages site of class materials (slide decks, booklets,
landing pages) maintained by several educators, each working with Claude.
**All new and migrated content must use the shared design system. Do not
write per-page inline `<style>` blocks or invent new palettes.**

## Required reading

@ROADMAP.md

The file imported above is mandatory and is loaded into every session. It
carries the working rules (claim before starting, tick and date on
landing), the per-session checklist, the copyright and student-data
guardrails, and the list of decisions already settled. Follow it.

Its companion **`ROADMAP-DETAIL.md`** holds the full inventory, the
definition of done, and every outstanding job in effort order. It is
*not* auto-imported — **open it with Read before picking up, finishing or
adding any build-out work**, and edit it in place to record what landed.

In short: this file says *how* to build, `ROADMAP.md` says *how we work*,
and `ROADMAP-DETAIL.md` says *what is left*.

## Design system (mandatory)

Every slide deck links exactly these shared assets (adjust relative depth):

```html
<link rel="stylesheet" href="../../assets/css/tokens.css">
<link rel="stylesheet" href="../../assets/css/deck.css">
<link rel="stylesheet" href="../../assets/css/sitenav.css">
<script src="../../assets/js/deck.js" defer></script>
<script src="../../assets/js/sitenav.js" defer></script>
```

The last two lines are the site-wide nav drawer and go on **every** page
type, not just decks — see "Site-wide navigation" below.

Plus the fonts:

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Bitter:wght@500;700;800&family=Source+Sans+3:ital,wght@0,400;0,600;0,700;1,400&display=swap" rel="stylesheet">
```

- `assets/css/tokens.css` — global design tokens (colours, fonts, spacing).
  The only place raw colour values may be defined.
- `assets/css/deck.css` — the canonical slide system: layout, chrome,
  callout boxes, pedagogy tags, reveals, maths markup, tables, print rules.
- `assets/js/deck.js` — shared navigation (keys/buttons/swipe), progress,
  step reveals, answer toggles, part tabs, scroll-fade, slide-jump menu.
  Never copy nav JS into a deck.

Optional modules — link only when a deck uses them:

- `assets/css/quiz.css` + `assets/js/quiz.js` — multiple-choice retrieval
  quizzes. A unit-local `questions.js` sets
  `window.RETRIEVAL_QUESTIONS = [{deck, q, opts, ans}]`; a slide marked
  `class="slide quiz-slide" data-quiz-before="9" data-quiz-count="5"`
  containing `<div class="quiz-container"></div>` draws that many
  questions at random from earlier lessons and scores them. Add
  `data-quiz-exclude="4"` (comma-separated deck numbers) where a unit has
  an **optional** lesson inside an otherwise sequential run — without it a
  class that skipped that lesson gets cold-called on content it never saw.
  Year 7 Space uses it for Lesson 4. quiz.css also
  styles a standalone quiz page (`<body class="quizapp-page theme-X">`).
- `assets/css/orbit.css` + `assets/js/orbit.js` — the orbital phase
  visualiser. Markup is one line, `<div class="orbitsim"></div>`; the JS
  builds the SVG scene (Sun, Earth, orbiting Moon with its lit half
  always facing the Sun) plus a phase disc, slider, play button and
  hemisphere toggle. Attributes: `data-hemisphere="south|north"`
  (default south — a waxing Moon is lit on the **left** in Melbourne),
  `data-start="0..1"`, `data-labels="off"`. ~3.5 KB gzipped, no
  dependencies. Colours come from tokens so it follows the theme;
  controls are hidden in print. Live in `styleguide/deck-demo.html`.
- `assets/css/binomsim.css` + `assets/js/binomsim.js` — the binomial →
  normal visualiser for 15F. Markup is one line,
  `<div class="binomsim"></div>`; the JS builds the SVG (exact
  `Bi(n,p)` bars with the `N(np, np(1-p))` curve over them, mean line,
  auto-thinning axis), two sliders and a readout that states `np`,
  `n(1-p)` and a verdict on the `> 5` guideline. Attributes:
  `data-n`, `data-p`, `data-nmax` (default 200), `data-controls="off"`
  for a static figure. The window is ±4σ round the mean, clipped to
  `[0, n]`, widening to the full support when that would leave fewer
  than six bars. **The pmf is computed in log space via a Lanczos
  log-gamma** — `n!` overflows a double at 171 and the naive recurrence
  from `P(0) = (1-p)^n` underflows to zero for extreme `p`, so either
  shortcut draws an empty chart at exactly the settings the widget
  exists to demonstrate. Colours come from tokens; sliders are hidden
  in print. Live in `styleguide/deck-demo.html`.
- Slide-jump menu — add `<button class="navbtn menubtn">` inside
  `.chrome` plus a `.slidemenu` overlay containing `.menugrid`, and give
  each slide a `data-menu="…"` title. deck.js builds the contents grid
  and binds `M`/Escape. Decks without the markup are unaffected.

Other page types: `assets/css/course.css` (unit landing),
`assets/css/hub.css` (term/unit hub), `assets/css/solutions.css`
(answer-key pages), `assets/css/worksheet.css` (printable student
worksheets), `assets/css/profile.css` (species / case-study reference
pages), `assets/css/planner.css` (staff unit-planning documents — one
wide table, prints A4 landscape), `assets/css/site.css` (plain index
pages).

**Living reference: open `styleguide/deck-demo.html` in a browser.** It
exercises every component and has a theme switcher. Start new decks from
`styleguide/deck-template.html`.

## Site-wide navigation

`assets/css/sitenav.css` + `assets/js/sitenav.js` — a drawer that slides
in from the left edge with the whole site in it. Present on every page
type (decks, hubs, course landings, worksheets, quizzes, profiles,
solutions, plain index pages) so a student on any page can reach any
other without going back through the index.

- **Two lines per page**, before `</head>`, at the page's relative depth:
  the `sitenav.css` link and the `sitenav.js` script. tokens.css must be
  linked too (sitenav.css reads its palette and fonts) — the plain
  site.css index pages now link both.
- **Opening**: a slim tab pinned to the left edge, or the `N` key.
  Escape closes. There is no always-visible chrome, which is why decks
  can carry it without cluttering a projected slide.
- **Never edit `assets/js/sitemap.js`** — it is generated. After adding,
  renaming, moving or deleting a page, run:

  ```bash
  node tools/build-sitemap.js     # rebuild the tree
  node tools/add-sitenav.js       # dry run: which pages lack the tag
  node tools/add-sitenav.js --write
  ```

  `add-sitenav.js` is idempotent, so re-running it only touches pages
  that don't already link the drawer. Then check nothing broke:

  ```bash
  node tools/check-links.js       # exits 1 if it finds anything
  ```

  It resolves every `<a href>`, `<link>`, `<script src>`, `<img src>`,
  `<object data>`, `<source>`, `<iframe>`, `<embed>`, poster and SVG
  `<use>` against the filesystem and reports **MISSING**, **CASE**,
  **ABSOLUTE** and **IGNORED**. CASE is the one to care about — the repo
  is developed on Windows and served on Linux, so a wrong-case link
  works locally and 404s live. `--all` includes the marimo workbook
  exports, which have nine known-broken `manifest.json` links.
- Labels come from each page's `<title>`, with the surrounding context
  stripped ("Lesson 4 · Dichotomous Keys | Biodiversity & Ecosystems"
  becomes "Lesson 4 · Dichotomous Keys", because the tree already says
  which unit you're in). **A page with a vague `<title>` gets a vague nav
  entry** — fix the title rather than hand-editing sitemap.js. Where a
  title genuinely can't carry the label, add an entry to
  `LABEL_OVERRIDES` / `UNIT_OVERRIDES` / `FILE_LABEL_RULES` in
  `tools/build-sitemap.js`.
- Files are bucketed into **Lessons / Worksheets / Workbooks /
  Resources** by filename (`deck*.html`, `*_Slides.html` and anything in
  `slides/` are lessons; `worksheet*.html` are worksheets). A new naming
  convention needs a line in `GROUPS`.
- **Paths are relative, never root-absolute.** The site is served from
  `/SchoolSites/`, so `/year7-science/…` would 404. sitenav.js works the
  root prefix out from its own `<script src>`, which is why the two tags
  must carry the correct `../` depth. The single exception is
  `404.html`, which GitHub Pages renders *at the bad URL* — at any
  folder depth — so relative asset paths there would resolve against a
  path that doesn't exist. It carries `<base href="/SchoolSites/">` and
  is otherwise ordinary relative markup. If the site's served path ever
  changes, that one line changes with it. `check-links.js` honours a
  root-absolute `<base>`; `build-sitemap.js` keeps 404.html out of the
  nav tree via `SKIP_FILE`.
- **Keyboard**: the drawer's handler is registered in the *capture*
  phase and stops propagation while open, so arrows and space don't also
  advance the deck underneath. `M` still belongs to deck.js's slide-jump
  menu, and `N` stands down while that menu is up. If you add another
  global key anywhere, check it against both.
- Excluded from the nav: the four bare-name legacy folders
  (`algorithmics/`, `foundation/`, `methods/`, `specialist/` — pre-year-
  prefix duplicates of their `year12-*` equivalents), `*-payload.html`,
  and the marimo workbook exports, which are also skipped by the
  injector since a re-export would overwrite the edit. Those lists live
  at the top of both tools.
- Every selector in sitenav.css is scoped under `.sn-*` / `#sitenav`, and
  every property it needs is set explicitly rather than inherited —
  necessary because four of the page stylesheets ship a
  `* { margin:0; padding:0 }` reset and course.css sets `color:#fff` on
  `<body>`. Keep it that way.

## Site icon / installed app

One icon for the whole site, in `assets/icons/`, plus
`site.webmanifest` at the repo root. The mark is a treble clef inside an
electron-orbit atom, chalk on a chalk-blue board.

**`assets/icons/mark.svg` is the source of truth**, and it is
maintained by hand in Illustrator, not generated. One `<path>`,
`fill-rule="evenodd"`, `fill="currentColor"`, square viewBox, no
background. Everything else in `assets/icons/` is built from it:

```bash
node tools/build-icons.js --png   # mark.svg -> icons + logo-large*
```

- **Edit the mark in Illustrator, flatten to a single compound path,
  export, and replace mark.svg.** Then re-run build-icons.js. Do not
  hand-edit `favicon.svg`, `icon-*.svg` or `logo-large*` — they are
  generated and a rebuild silently overwrites them.
- Why one path matters: overlapping objects are invisible only while
  every piece is the same fully opaque colour. An assembled mark
  rendered with per-path `fill-opacity` shows the overlaps as visibly
  darker patches, and it breaks under strokes and boolean operations.
- **`mark-source.svg` is the archived assembled original** — the raw
  Illustrator export plus a hand-added connector bridging the clef's
  broken stem. Nothing builds from it; it is kept only as the record of
  where the artwork came from. The shipped mark supersedes it.
- Illustrator's path fitting is dramatically better than an
  auto-trace here: the same shape is ~2 KB of path data against ~24 KB
  from potrace, for a sub-pixel difference. A tracing step existed
  briefly and was removed once the Illustrator route proved better.
- It came from an Illustrator export that had an outer ring, a coloured
  nucleus and pale-yellow linework on white. All three were removed or
  changed: the ring and nucleus were most of what turned to mush in a
  browser tab, and yellow-on-white had too little contrast to survive
  downsampling. What's left is deliberately sparse. **Test any change at
  16px before shipping it** — the mark is right at the edge of what
  reads in a tab, and adding detail back will push it over.
- The clef's stem is broken in the original artwork — the coloured
  nucleus used to sit over the join and hide it. `mark-source.svg`
  therefore ends with a hand-added connector path bridging that gap. It
  sits in its own untransformed `<g>`, so its coordinates are in plain
  viewBox space, unlike the imported paths which carry a `translate()`.
  If the artwork is ever re-exported from Illustrator, that connector
  has to be re-added or the clef will read as two disconnected pieces.
- **Never draw the mark with `<text>`.** An SVG favicon cannot load a
  webfont, so a type-based mark falls back to whatever serif the OS has
  and renders differently per machine. Everything is vector shapes.
- **Colours are hardcoded, not tokens.** An icon file is fetched without
  the stylesheet, so it can't read a CSS variable. Board `#24576f`,
  chalk `#f6f4ef`. If those tokens change, update
  `tools/build-icons.js`, `site.webmanifest` and the `THEME` constant in
  `tools/add-favicon.js` together.
- The rasteriser's density is **computed from the viewBox**, not
  hardcoded: ImageMagick renders an SVG at `units / 72 * density` pixels,
  so a fixed high density against a ~1000-unit viewBox asks for a
  17000px bitmap and dies with "cache resources exhausted".
- **Corner rounding differs by target on purpose.** `favicon.svg` keeps
  its own `rx`; `apple-touch-icon.png` is square because iOS applies its
  own mask (a pre-rounded source shows dark corners inside the
  rounding); `icon-maskable-512.png` bleeds to every edge with the mark
  scaled to the middle 66% so it survives any Android mask shape.
- Regenerate with `node tools/build-icons.js --png` (needs ImageMagick).
  The three SVG sources are written first and committed, so the set is
  reproducible without the rasteriser.

**Large-format versions** come out of the same build, for print,
posters, slide titles or anything above about 256px:

- `logo-large.svg` — mark on a rounded board tile
- `logo-large-chalk.svg` — chalk mark alone, for dark backgrounds
- `logo-large-ink.svg` — board-coloured mark alone, for light and print

plus `logo-large-*-2048.png` rasters of each. Same geometry as the
icons, just without the icon framing.

`favicon.svg` is ~2.2 KB. If a change to the artwork sends that past
about 5 KB, the path wasn't flattened properly — check it's one compound
path and not a stack of overlapping objects.
- Inject the tags into new pages with the same dry-run/`--write` pattern
  as the nav drawer:

  ```bash
  node tools/add-favicon.js            # dry run
  node tools/add-favicon.js --write
  ```

  Idempotent, uses the same skip lists as `add-sitenav.js`, and writes
  paths at each page's relative depth — the site is served from
  `/SchoolSites/`, so root-absolute icon paths would 404. Note browsers
  also probe the *domain* root for `/favicon.ico`, which is outside this
  repo; the explicit `<link>` tags are what actually do the work.

## Deck rules

- `<body class="deck-page theme-X">` where X ∈ `theme-methods`,
  `theme-specialist` (pink), `theme-primer`, `theme-science`,
  `theme-space` (Year 7 Space — night indigo / starlight gold), or omit
  for the default chalk-blue.
- New subject → add a ~4-line theme block in tokens.css remapping only
  `--accent`, `--accent-dark`, `--accent-warm` (define new hexes as
  primitives in the same file first). Theme classes work on any page type
  (decks, hubs, landing pages). Do not override the pedagogy colours
  (`--ido/--wedo/--youdo`), answer-green, or error-red — these stay
  consistent across subjects.
- Slides are `<section class="slide">` inside `<main class="deck">`;
  variants: `title-slide`, `section-slide`, `exit-slide`.
- Callouts use the box system: `<div class="box key|defn|try|example|hint|answer|question|cas">`
  with a `<span class="lbl">Label</span>` first child.
- Other content components: `.step`/`.n` numbered working cards
  (`.step.substep` + `.n-blank` continues the step above without a new
  number), `.formula` inline chip, `table.tbl.vocab` word/say-it/meaning
  tables, `.say` and `.note` asides, `.bookref` booklet-page chip,
  `.chooser`/`.opts`/`.opt.correct` "pick the one that fits" cards,
  `.textflow`/`.figure-right` for prose wrapping a figure. `.key` on its
  own is a *keyboard cap* — a key-idea callout is `.box.key`.
- `.box.country` is the First Nations / Caring for Country callout. Like
  the pedagogy colours it keeps one earth tone across every subject and
  does not follow the theme accent.
- Bare `<p>` and `<ul>`/`<ol>` directly inside a slide get their spacing
  and indent from the prose defaults in deck.css — don't add per-slide
  margin styles. A centred caption under a figure is `.figcap`; the
  course/assessment line at the foot of a title or section slide is
  `.slide-foot`. Both exist because the Specialist Term 3 decks were
  carrying 27 `style="font-size:21px; text-align:center"` attributes
  between them.
- Gradual release tags: `<span class="phase-tag ido|wedo|youdo|cas">`.
- Maths: **typeset whole expressions with MathJax**, e.g.
  `\(\sin 30^\circ = \dfrac{1}{2}\)` — not half MathJax, half CSS. Mixing
  the two inside one expression is what breaks layout (a MathJax radical
  dropped into a CSS `.fr` collapses the fraction bar), and side-by-side
  CSS and MathJax fractions don't match. MathJax is the only maths engine
  in this repo — don't add KaTeX alongside it.
- Lines of working go in `.working`, not a column of `.formula` chips.
  `.formula` is a *boxed* chip for a standalone stated rule; stacking
  several reads as unrelated boxes rather than one calculation. Combine
  with `.steps` (`<ol class="steps working">`) to keep the step reveal.
  `.working` shrink-wraps and centres the block while leaving its lines
  left-aligned; the `=` alignment itself comes from `\phantom{…}` padding
  on continuation lines, because each line is typeset separately and
  MathJax cannot align across them. `.lbl-step` labels a line.
- `.result` is a short stated answer *in prose* — bold accent text, no
  box. Use it where a "formula" chip was really carrying words ("Full
  Moon", "radio telescope"), which is most of them in practice.
- The CSS maths markup (`.m`, `.mu`, `.work`, `.bigeq`, `.eqbox`) is for
  light inline notation in prose. `.fr`/`.nu`/`.de` is now reserved for
  *styled word* fractions (e.g. colour-coded Opposite/Adjacent in
  trigonometry) — numeric fractions use `\dfrac`.
- Square roots are typeset with MathJax: `\(\sqrt{2}\)`. Never build a
  radical from a bare √ plus a CSS overbar — the bar will not meet the
  glyph. **MathJax is vendored once**, at
  `assets/vendor/mathjax/tex-svg.js` — link it at the deck's relative
  depth, do *not* copy the 2 MB file into the unit folder. (It used to
  be duplicated per folder; four identical copies meant a student who
  had already opened a Specialist deck still re-downloaded the whole
  thing for a primer deck.) Add the standard config block beside it —
  every deck must include the `startup.pageReady` hook, which fires a
  `resize` so deck.js re-measures slide overflow after typesetting.
  Twenty decks were missing it and mis-measured maths-heavy slides. Inside SVG, MathJax can't reach the text,
  and an overline `<tspan>` there reads as a detached bar — write a plain
  `√2` in diagram labels. A bare √ is also fine when referring to the
  symbol itself in prose.
- Reveals: `.steps` + `.reveal-btn data-target`, `.qcard` answers,
  `.ptab`/`.partpanel` part tabs — all wired automatically by deck.js.
  **Forward nav (→ / space / next) reveals the next hidden thing on the
  slide before advancing** — a `.steps` line, a `.frag`, or a `.qcard`
  answer, in document order — so a worked example can be walked through
  from the presenter remote without touching a button. Reveals inside a
  `.partpanel` that isn't on screen are skipped, so an arrow press never
  looks like a no-op. Buttons and keys read the same DOM state, so the
  two can be mixed freely; `R` reveals without any chance of advancing.
  Backward nav un-reveals fragments only — steps and answers stay up, so
  `←` backs out of a long worked example in one press.
  `.frag` reveals on forward navigation and works on SVG groups too, so
  a `<g class="frag">` is a diagram layer. `<g class="vanish">` fades out
  once a later `.frag` appears. Where a diagram layer must pair with
  prose in the *other* column (document order can't express that), mark
  it `.keylayer` and mirror `.on` across with a short per-deck script —
  see the dichotomous-key slide in year7-science deck4.
- Vertical centring and overflow (15% top buffer, 15% bottom scroll fade)
  are automatic — do not add per-slide spacing hacks.
- Chrome (nav buttons, counter, hints) is sized in viewport units on
  purpose (constant size under zoom) — don't convert those to px.

## Landing/index pages

**Every index page is a course-page now** — the root landing page, all
15 subject index pages and the two year11-methods chapter indexes were
ported off site.css in Aug 2026. A new index page starts from
`year7-science/index.html`, not from site.css.

`assets/css/site.css` survives only for the four bare-name legacy
folders and `tools/staff-crypt.html`. It still carries its own `:root`
palette because those pages don't link tokens.css — leave that alone.

The twelve placeholder tool pages it used to serve were **deleted** in
Aug 2026, along with their index cards: seven `sample-resource.html`
stubs plus `tangent-visualiser`, `slope-fields`, `complexity-suite`,
`telling-time` and `number-sense-games`. Despite the specific names,
every one was the same 2 KB shell reading "this is where your tool
goes" — a card promising a tool that doesn't exist is worse than no
card. An index left with nothing gets
`<p class="section-sub">No resources published for this subject yet.</p>`
in place of its `.deck-grid`; nine of the fourteen subject pages are in
that state, which is the honest picture of what's published.

## Course landing pages (subject home, immersive)

Use `assets/css/course.css` with `<body class="course-page theme-X">` —
full-bleed subject-colour gradient, glassy `.deck-card` grid, `.feature`
row cards. Reference implementation: `year12-specialist/index.html`
(pattern generalised from year7-science bio-ecosystems).

Once a unit has more than about four `.feature` cards, split them into
`.section-head` + `.section-sub` groups with one `.deck-grid` each rather
than one long row — see `year7-science/bio-ecosystems/index.html`, which
groups Student resources / Staff only / Lessons.

Three components exist for index pages specifically:

- `.dc-kind` — the resource-type chip on the right of a card ("Unit",
  "Hub", "Chapter", "HTML tool"). It sits where `.go` would, so use one
  or the other, never both. Subject index pages use `.feature` rows +
  `.dc-kind`; a chapter index with many lessons reads better as plain
  `.deck-card`s with `.dc-num` (`year11-methods/chapter-9`).
- `.yeartabs`/`.ytab`/`.ypanel` — the root index year picker. Panels
  toggle with `[hidden]`, and the first visible panel ships un-hidden so
  a no-JS visitor still sees something. The tab script lives inline on
  `index.html`, reads whatever tabs are present, and mirrors the
  selection into a `#year-N` hash.
  **Subjects with nothing published are commented out, not deleted** —
  nine of them as of Aug 2026, which also empties the Year 8 and Year 9
  tabs, so those tab buttons and panels are commented out too. Uncomment
  a card (and its tab/panel if the whole year is hidden) when the
  subject gets content. A header comment at the top of the tab strip
  lists what's currently hidden; keep it in step. The folders and their
  index pages still exist and are still listed in the nav drawer — the
  root page is curated, the drawer is the full map.
- `.band-label` — eyebrow above a panel's cards ("Junior", "VCE Units
  3 & 4").

**A subject index carries its subject's theme class**, so the colour a
student sees on the year-level card carries through to the unit. Every
subject therefore needs a theme: `theme-foundation` (rust) and
`theme-maths` (the Methods blue, for Years 7–10 Mathematics) were added
for this. When you add a theme, also add a matching `.sn-t-<name>` dot
colour in sitenav.css — `build-sitemap.js` reads the theme class off
`<body>` into the tree's `k` field and the drawer paints a dot with it,
so a theme with no `.sn-t-` rule silently falls back to the generic
accent.

## Course hub pages (term/unit overviews)

Use `assets/css/hub.css` + `assets/js/hub.js` with
`<body class="hub-page theme-X">`. Reference implementation:
`year12-specialist/term-3/index.html`. Components: `.hub-head` header
band, `.timeline`/`.mile[data-date]` milestones, `#weeks` grid of
`.week[data-start]` cards, `.aos` chapter tags, `.milestone-chip`,
`.links`. hub.js auto-highlights the current week, marks past/next
milestones, and fills `.countdown[data-to]` elements.

A unit long enough to need **several week grids stacked** wraps each in a
`.chapter` opening with a `.ch-head` (`h2` + `.ch-meta`, then a `.ch-open`
pill on the right, or a `.ch-links` span when a chapter has more than one
destination — e.g. a question booklet beside the deck). Reference
implementation: `year10-mathematics/10methods-primer/index.html`, nine
chapters across a full year. A hub with a single grid goes straight from
`h2` to `.grid` and needs none of it. Period lines carry their own link
and label styling (`ul.periods a`, `ul.periods li b` — the lead-in code
or day, in the hub's amber), so don't restate those per page.

## Species / case-study profile pages

Use `assets/css/profile.css` + `assets/js/profile.js` with
`<body class="profile-page theme-X">`. A long-form reference page a
student reads *alongside* a unit — not a deck and not a worksheet.
Reference implementation:
`year7-science/bio-ecosystems/species-bandicoot.html` (ported from the
Eastern Barred Bandicoot species booklet docx).

- Structure: `.hero` (`.back-btn`, `.unit-tag`, `h1`, `.binomial`,
  `.sub`, `.meta-row` of chips) → sticky `.toc` chip nav → `<main>` of
  `section.pf`, each opening with `.pf-head` (`.pf-eyebrow` + `h2`).
  profile.js does one thing: marks the `.toc` chip for the section in
  view `.is-current`. Nothing else is scripted.
- Layout: `.cols`, `.cols.wide-left` (5:7), `.cols.thirds` — all collapse
  to one column under 760 px.
- Content components: `.panel` (+ `.panel-lbl`, `h4` subheads;
  `.panel.flush` when the panel's body *is* a table), `table.pf-tbl`
  (`.ladder` for a two-column classification ladder, `.plain` to drop the
  bold first column), `.figure` > img + figcaption, `.pill`
  (`.biotic`/`.abiotic`/`.up`/`.down`), `.taglist` > `.t`,
  `.strategy` (`.st-num`, `.st-how`, `.ad-grid` of `.ad`/`.dis`,
  `.status`), and `.ok`/`.no` for correct/incorrect examples.
- Callouts mirror deck.css: `.box`, `.box.key`, `.box.defn`,
  `.box.country`, each with a `<span class="lbl">` first child.
  `.box.country` keeps the earth tone across every subject, same as in
  decks and worksheets.
- Prose spacing comes from the section defaults (`section.pf > * + *`,
  `h3 + *`). Don't add per-section margins.
- Charts are inline SVG with a `<style>` block referencing tokens
  (`var(--accent)`, `var(--ink-soft)`) so they follow the theme — see the
  population graph in the bandicoot profile. Don't ship a matplotlib PNG
  where an SVG will do; photos stay as images under the unit's `img/`.
- Print rules are in profile.css: hero flattens to ink-on-white, the toc
  and back button are dropped, and each `section.pf` starts a new page.

## Printable worksheets

Use `assets/css/worksheet.css` with
`<body class="worksheet-page theme-X">`. Print-first: `@page` is A4 and
the on-screen `.sheet` is a paper preview at 210×297 mm. No JS module —
the only script is the inline `window.print()` on the toolbar button.
Reference implementation: `year7-science/bio-ecosystems/worksheet1.html`.

- One `.sheet` holds the whole worksheet and flows across printed pages;
  it opens with `.ws-head` (`.ws-tag`, `h1` with `.lnum`, `.ws-sub`,
  `.namebar`) and closes with `.ws-foot`. Don't split a worksheet into
  several `.sheet`s and don't add `.ws-runhead` (an optional hard page
  break) without measuring — the bio worksheets fill 90%+ of each sheet
  flowing, and a mid-part forced break dropped that to ~76% and added a
  whole page to five of the eleven. Pagination is safe because
  `break-inside: avoid` is set on questions, tables, sort columns and
  callouts, and no single block exceeds a page (tallest is ~190 mm
  against 273 mm of usable height).
- `.namebar` auto-draws its rules — the `span::after` fills the
  remaining width, so don't type underscores.
- Content: `section.part` + `.part-head` (`.part-label`, `.part-title`,
  `.marks`), `.q` with `.qn` + `.qbody`, `.sub-q` with `.sl`.
  A `.part-label` beginning `!` drops the "Part " prefix (used by the
  closing self-check block).
- Writing space is `.lines` with `data-lines="1".."10"` (8 mm rule),
  `.blank`/`.blank.sm`/`.blank.lg` inline, and `.drawbox`
  (`data-h="sm|md|lg"`) for diagrams. Never hand-draw rules with
  underscores or borders.
- Question furniture: `.opts`/`.opt` multiple choice, `.tick` checkbox
  list, `table.wtbl` with `td.fill` blank cells, `.sortcols[data-cols]`
  of `.sortcol`, `.chips`/`.chip` word bank.
- Callouts: `.infobox` (accent), `.fnbox` (First Nations — earth tone,
  theme-independent like `.box.country` in decks), `.y8box` plus the
  inline `.y8` marker for Year 8 extension. Each takes a `.lbl` first
  child.
- Marks totals in `.namebar .marks-total`, the toolbar hint and the unit
  index `.wl-marks` must agree with the sum of the `.part-head` marks.
- Answers go in the unit's `solutions.css` page, tagged
  `<span class="tag ws">Worksheet</span>`, under a `.subhead` divider at
  the end of that lesson's section. Note that bio-ecosystems'
  `solutions.html` ships its answers as an encrypted blob — adding to it
  means decrypting, splicing, and re-encrypting via
  `tools/staff-crypt.html` (see "Staff-gated pages").

On the unit landing page each worksheet is linked directly under its
lesson: wrap the `.deck-card` and a `.dc-wslink` in a `.deck-item`
(course.css). The wrapper is required because `.deck-card` is itself an
`<a>` and a link cannot be nested inside one — cards without a wrapper
are unaffected. course.css also has `.ws-strip` / `.ws-link` (`.wl-num`,
`.wl-title`, `.wl-marks`) under a `.section-head` + `.section-sub` for a
standalone all-worksheets list, if a unit wants one instead.

## Staff-gated pages

Some pages are for teachers only and ship their content as an encrypted
blob decrypted in the browser with the staff password. In
year7-science/bio-ecosystems: `solutions.html` (answer key),
`worksheets-all-solutions.html` (the collated worksheet booklet with
answers), `portfolio-solutions.html` (the Research Portfolio key) and
`rubric.html` (the Ecosystem Investigation marking tool). In
year7-science/space: `solutions.html`.

**`portfolio-solutions.html` is not yet encrypted** — it ships the shell
with a placeholder `var BLOB = {v:2, iv:"", ct:"", keys:[]};`, so it
locks but cannot unlock. Encrypt `portfolio-solutions-payload.html`
through `tools/staff-crypt.html` and paste the emitted line over the
placeholder. Staff password only unless a student one is deliberately
added — that key answers a task students are meant to research
themselves. The shell links tokens.css +
solutions.css and uses the shared `.lockscreen` component; the payload
lives in a single `var BLOB = {salt, iv, iter, ct};` line
(PBKDF2-SHA256 → AES-GCM).

- **`tools/staff-crypt.html`** does the encrypting and decrypting —
  open it locally, it never sends the password anywhere. Editing a gated
  page means: decrypt → edit the payload → re-encrypt → paste the new
  `var BLOB` line. A *fresh* salt and iteration count each time is fine;
  the page reads both out of the blob. (Earlier notes here claimed they
  had to be reused — they don't.)
- Plaintext payloads are `*-payload.html` and are **gitignored**.
  Committing one defeats the lock. The encrypted page is the source of
  truth; round-trip through staff-crypt to make changes.
- `rubric.html` differs from `solutions.html` in that its payload is an
  *application*, not static markup. `innerHTML` never executes injected
  `<script>` elements, so the unlock handler re-creates each one as a
  fresh node. It also swaps `body.solutions-page` for
  `body.rubric-page` on unlock — otherwise the solutions-page rules
  out-specify the tool's own.
- The marking tool autosaves to `localStorage` so a refresh doesn't lose
  a class's marks. That means student names and marks sit in the
  browser profile: use *Save file* then *Clear all marks* on a shared
  machine.
- Its palette is mapped onto tokens in one `body.rubric-page` block —
  band ramp (`--c-band-0..4`) and rubric part hues (`--c-part-b/c/d`)
  are primitives in tokens.css. Like the pedagogy colours these stay
  constant across subjects so a printed rubric reads the same whichever
  subject issued it; Part A follows the theme accent.

## PDFs

Implemented. Embed with a native `<object type="application/pdf">` so the
browser's own viewer supplies search/zoom/print — no JS, no pdf.js.
Components live in **course.css**, not site.css as the original note
guessed: the pages that embed unit PDFs are course-pages. Lift them into
a shared file if a plain site.css index page ever needs one.

```html
<div class="pdf-frame">
  <object data="booklet/….pdf" type="application/pdf">
    <div class="pdf-fallback">…<a class="pdf-btn" href="…">Open</a></div>
  </object>
</div>
<div class="pdf-actions"><a class="pdf-btn" …>…</a></div>
```

- Full width, 80vh (60vh on phones and short viewports), card border.
- Mobile Safari and most Android browsers refuse to render a PDF in an
  `<object>`, so the fallback content is a real download card and
  `.pdf-actions` sits outside the frame where it always shows. Don't
  replace this with an `<iframe>` — the fallback stops working.
- Reference implementation:
  `year7-science/bio-ecosystems/research-portfolio.html` (the 27-page
  Research Portfolio question booklet, built from
  `booklet/Bio_Research_Portfolio_Yr7_8.tex` — the LaTeX stays the source
  of truth, the PDF beside it is the build output).

A unit's PDFs live in its own `booklet/` folder with the `.tex` beside
them, plus the `fonts/` the `.tex` loads by relative path (Lato +
Poppins) so the booklet builds from a clean checkout. `pdfs/` at the
repo root is for standalone question booklets that belong to no unit.

Build a booklet with `xelatex` run **three times** (TOC, then
`\LastPage`), from a scratch copy of `booklet/` — the `.aux`/`.log`/
`.toc` build artefacts are not committed, only the `.tex` and `.pdf`.

**Single-lesson handouts are generated, never hand-copied.**

```bash
node tools/build-lesson-print.js          # list the sections
node tools/build-lesson-print.js 1        # write Space_Lesson1_Print.tex
node tools/build-lesson-print.js --all
```

It slices the master `.tex` — preamble verbatim, a compact cover in
place of the titlepage and TOC, then the chosen `\section` block — and
never modifies the master. A hand-made second `.tex` would drift the
first time a question was corrected, with nothing to signal it; this
keeps one source of truth. The emitted file carries a "GENERATED —
do not edit" header, and is safe to commit alongside its PDF.

The one subtlety: it emits `\setcounter{section}{N-1}` before the body,
because `\question` numbers off `\thesection`. Without it Lesson 3's
handout would print Q1.1… instead of Q3.1… and could not be marked
against the existing answer key.

Booklets have a question apparatus already defined in the preamble —
`\question{marks}{text}`, `\anslines{n}` (ruled writing lines),
`\answerbox{height}`, `\markscount{n}`, and the `yr7box` (at the level)
/ `yr8box` (above the level) containers. Use these rather than inventing
new markup.

**Question numbers are automatic — never write one by hand.** `\question`
steps a `qnum` counter that resets at each `\section`, printing
`Q<section>.<n>`, so inserting, deleting or reordering content renumbers
everything for free. (Space originally took the number as a literal
first argument; adding a subsection then meant hand-renumbering the rest
of the section *and* the answer key, which is exactly the failure this
avoids.) Two consequences: the numbers exist only in the built PDF, not
the `.tex`, so grepping the source for `Q1.9` finds nothing — extract
from the PDF with `pdftotext` instead; and because `\question` uses
`\refstepcounter`, a `\label` placed straight after one can be `\ref`'d.

The answer key still hardcodes `Q<n>.<n>` references, so it can drift
silently from an auto-numbered booklet. After changing question content,
diff the built PDF against the key:

```bash
pdftotext -layout booklet/*.pdf - | grep -o 'Q[0-9]*\.[0-9]* ([0-9]* marks\?)'
```

and check every number and mark allocation still matches
`solutions-payload.html`. Space's pattern: a `yr7box` headed "Check your
understanding" at the end of each subsection, questions numbered
`Q<lesson>.<n>` running continuously through the lesson, with the Year 8
box kept last. Don't number the "Your turn" `scaffold` blocks — they
drift out of sync when sections are reordered.

**Every `\section` and `\subsection` in the Space booklet carries a
`\label{sec:N}` / `\label{sub:N.M}`**, and the cover's contents table
`\pageref`s them. That serves two purposes: the contents table can never
list a stale page, and a reference sweep reads exact page numbers out of
the `.aux` —

```bash
grep -o '\\newlabel{su\?[bc]:[0-9.]*}{{[^}]*}{[0-9]*}' booklet/*.aux
```

— rather than scraping headings out of `pdftotext` output, which breaks
on whitespace and on any heading that wraps. Add the same labels to any
booklet that needs a sweep. Note the `.toc` file only exists when
`\tableofcontents` is present; the `.aux` is always written.

`.bookref` chips must be derived from the booklet's labels after a
build, never hand-written. Space's original chips cited pages 38–71 of a
22-page booklet — the numbers followed a synthetic `(N-1)*6+3` pattern —
and their `QX.Y` references pointed at numbered questions the booklet
never had (the only question labels in the `.tex` are five "Your turn"
scaffolds). Match old subsections to new ones by **title**, not number.

## Legacy content

Ported already: year12-specialist (term-3 decks, hub, landing),
year10-mathematics/10methods-primer (9 decks + hub), year7-science
bio-ecosystems (11 decks, landing, quiz, solutions, 11 worksheets — its
unit-local deck.css/deck.js are gone), and year7-science/space (8 decks,
landing, quiz, booklet — ported from the OneDrive `7 Science/Space`
folder, same unit-local shape bio-ecosystems had, then consolidated from
11 lessons to an 8-lesson 4-week program).

Space's consolidation is the reference for compressing a unit. Lessons
merge in pairs (old 2+3, 5+8, 6+10) chosen to sit inside one VC 2.0
content description; nothing was deleted, so merged decks run 21–22
slides and open each half with a `.section-slide` divider carrying that
part's learning intentions. Each merged content slide keeps a
`data-src-section` attribute recording the booklet section it came from
— that's what makes the `.bookref` chips re-pointable afterwards. The
booklet merges the same way: the second partner's `\section` becomes an
unnumbered "Part B" heading so `\subsection` numbering just continues
(2.1…2.5) rather than being demoted, which would have pushed a
`\subsubsection` down to `\paragraph` and broken its styling.

Still on inline styles: year11-methods ch9/11. When touching one, port it
to the shared assets rather than extending its inline styles.

Porting a unit-local deck set is mostly a rename job, and the vocabulary
repeats across units: `.kicker`→`.eyebrow`, `h1.slide-title`→`h2`,
`.body-text`/`.bullets`→ bare `<p>`/`<ul>`, `.callout`→`.box.key`,
`.discuss`→`.box.question`, `.fn-callout`→`.box.country`,
`.booklet-ref`→`.bookref`, `.diagram`→`.graph-card`, `.math`→`.formula`,
and the `.worked`/`.we-steps` block → `.box.question` + `ol.steps` +
`.reveal-btn`. Two things that bite: strip the inline `style=` spacing
hacks *before* the class renames (otherwise `<ul class="bullets"
style="…">` slips past an exact-match pattern), and don't promote a
"Recap" slide to `.exit-slide` — that variant centres its content, which
reads badly on a long summary list.

Themed colours inside SVG diagrams can't use `var()` in a presentation
attribute. Convert `fill="#hex"` to `style="fill:var(--accent)"` on the
element rather than leaving the hex or trying `fill="var(--accent)"`.

Note on SVG diagrams: convert *theme* colours in figures to tokens, but
leave genuinely illustrative hues (a fox is orange, water is blue) as
literal hex — those are content, not palette. The line falls in an
awkward place when the same hex does both jobs: in the Specialist Term 3
figures `#90A4AE` drew both dashed guide lines (chrome → `--ink-faint`)
and a second plotted curve (a data series that must stay distinguishable
from the accent → left as hex). Judge per element, not per colour.

Don't put a `<style>text{font-family:…}</style>` inside a figure. An SVG
has no inherited font, so a diagram with no rule falls back to the UA
serif — deck.css now handles that globally with
`.deck svg text:not([font-family])`. The `:not()` matters: a CSS
declaration beats an SVG presentation attribute at *any* specificity, so
without it the rule would silently override deliberate
`font-family="Bitter…"` display labels (there are 87 in bio-ecosystems).
Set the attribute on a `<text>` to opt it out.
