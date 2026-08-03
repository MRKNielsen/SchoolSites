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
(answer-key pages), `assets/css/site.css` (plain index pages).

**Living reference: open `styleguide/deck-demo.html` in a browser.** It
exercises every component and has a theme switcher. Start new decks from
`styleguide/deck-template.html`.

## Deck rules

- `<body class="deck-page theme-X">` where X ∈ `theme-methods`,
  `theme-specialist` (pink), `theme-primer`, `theme-science`, or omit for
  the default chalk-blue.
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

## Course hub pages (term/unit overviews)

Use `assets/css/hub.css` + `assets/js/hub.js` with
`<body class="hub-page theme-X">`. Reference implementation:
`year12-specialist/term-3/index.html`. Components: `.hub-head` header
band, `.timeline`/`.mile[data-date]` milestones, `#weeks` grid of
`.week[data-start]` cards, `.aos` chapter tags, `.milestone-chip`,
`.links`. hub.js auto-highlights the current week, marks past/next
milestones, and fills `.countdown[data-to]` elements.

## PDFs

Decision on file: embed with native `<object type="application/pdf">` +
fallback download link, styled by a `.pdf-frame` rule in site.css.
(Not yet implemented — implement the .pdf-frame rule if you're the first
to need it, full width, ~80vh, card-style border.)

## Legacy content

Ported already: year12-specialist (term-3 decks, hub, landing),
year10-mathematics/10methods-primer (9 decks + hub), and year7-science
bio-ecosystems (11 decks, landing, quiz, solutions — its unit-local
deck.css/deck.js are gone).

Still on inline styles: year11-methods ch9/11. When touching one, port it
to the shared assets rather than extending its inline styles.

Note on SVG diagrams: convert *theme* colours in figures to tokens, but
leave genuinely illustrative hues (a fox is orange, water is blue) as
literal hex — those are content, not palette.
