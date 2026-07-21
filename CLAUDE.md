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
  step reveals, answer toggles, part tabs, scroll-fade. Never copy nav JS
  into a deck.

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
- Gradual release tags: `<span class="phase-tag ido|wedo|youdo|cas">`.
- Maths: prefer the CSS markup (`.m`, `.mu`, `.fr`/`.nu`/`.de`, `.work`,
  `.bigeq`, `.eqbox`) over MathJax; MathJax is permitted where notation
  demands it (mjx sizing is already handled).
- Reveals: `.steps` + `.reveal-btn data-target`, `.qcard` answers,
  `.ptab`/`.partpanel` part tabs — all wired automatically by deck.js.
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

Old decks (year11-methods ch9/11, year12-specialist term-3,
10methods-primer, year7-science bio-ecosystems) still carry inline styles.
They are being rebuilt onto the canonical system — when touching one,
port it to the shared assets rather than extending its inline styles.
