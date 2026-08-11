# KNISchoolSites — instructions for Claude sessions

This repo is a GitHub Pages site of class materials (slide decks, booklets,
landing pages) maintained by several educators, each working with Claude.
**All new and migrated content must use the shared design system. Do not
write per-page inline `<style>` blocks or invent new palettes.**

## Design system (mandatory)

Every slide deck links exactly these shared assets (adjust relative depth):

```html
<link rel="stylesheet" href="../../assets/css/tokens.css">
<link rel="stylesheet" href="../../assets/css/deck.css">
<script src="../../assets/js/deck.js" defer></script>
```

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
  questions at random from earlier lessons and scores them. quiz.css also
  styles a standalone quiz page (`<body class="quizapp-page theme-X">`).
- Slide-jump menu — add `<button class="navbtn menubtn">` inside
  `.chrome` plus a `.slidemenu` overlay containing `.menugrid`, and give
  each slide a `data-menu="…"` title. deck.js builds the contents grid
  and binds `M`/Escape. Decks without the markup are unaffected.

Other page types: `assets/css/course.css` (unit landing),
`assets/css/hub.css` (term/unit hub), `assets/css/solutions.css`
(answer-key pages), `assets/css/worksheet.css` (printable student
worksheets), `assets/css/profile.css` (species / case-study reference
pages), `assets/css/site.css` (plain index pages).

**Living reference: open `styleguide/deck-demo.html` in a browser.** It
exercises every component and has a theme switcher. Start new decks from
`styleguide/deck-template.html`.

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
  margin styles.
- Gradual release tags: `<span class="phase-tag ido|wedo|youdo|cas">`.
- Maths: **typeset whole expressions with MathJax**, e.g.
  `\(\sin 30^\circ = \dfrac{1}{2}\)` — not half MathJax, half CSS. Mixing
  the two inside one expression is what breaks layout (a MathJax radical
  dropped into a CSS `.fr` collapses the fraction bar), and side-by-side
  CSS and MathJax fractions don't match.
- The CSS maths markup (`.m`, `.mu`, `.work`, `.bigeq`, `.eqbox`) is for
  light inline notation in prose. `.fr`/`.nu`/`.de` is now reserved for
  *styled word* fractions (e.g. colour-coded Opposite/Adjacent in
  trigonometry) — numeric fractions use `\dfrac`.
- Square roots are typeset with MathJax: `\(\sqrt{2}\)`. Never build a
  radical from a bare √ plus a CSS overbar — the bar will not meet the
  glyph. Copy `mathjax-tex-svg.js` into the deck's folder and add the
  standard config block (see any specialist or primer deck); its
  `pageReady` hook fires a `resize` so deck.js re-measures slide
  overflow after typesetting. Inside SVG, MathJax can't reach the text,
  and an overline `<tspan>` there reads as a detached bar — write a plain
  `√2` in diagram labels. A bare √ is also fine when referring to the
  symbol itself in prose.
- Reveals: `.steps` + `.reveal-btn data-target`, `.qcard` answers,
  `.ptab`/`.partpanel` part tabs — all wired automatically by deck.js.
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

Link `assets/css/site.css` (which layers on tokens.css). Follow the
existing card/list patterns in `index.html` and subject index pages.

## Course landing pages (subject home, immersive)

Use `assets/css/course.css` with `<body class="course-page theme-X">` —
full-bleed subject-colour gradient, glassy `.deck-card` grid, `.feature`
row cards. Reference implementation: `year12-specialist/index.html`
(pattern generalised from year7-science bio-ecosystems).

Once a unit has more than about four `.feature` cards, split them into
`.section-head` + `.section-sub` groups with one `.deck-grid` each rather
than one long row — see `year7-science/bio-ecosystems/index.html`, which
groups Student resources / Staff only / Lessons.

## Course hub pages (term/unit overviews)

Use `assets/css/hub.css` + `assets/js/hub.js` with
`<body class="hub-page theme-X">`. Reference implementation:
`year12-specialist/term-3/index.html`. Components: `.hub-head` header
band, `.timeline`/`.mile[data-date]` milestones, `#weeks` grid of
`.week[data-start]` cards, `.aos` chapter tags, `.milestone-chip`,
`.links`. hub.js auto-highlights the current week, marks past/next
milestones, and fills `.countdown[data-to]` elements.

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
blob decrypted in the browser with the staff password: `solutions.html`
(answer key) and `rubric.html` (the Ecosystem Investigation marking tool)
in year7-science/bio-ecosystems. The shell links tokens.css +
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

`.bookref` chips must be derived from the booklet's `.toc` after a
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
literal hex — those are content, not palette.
