# Build-out roadmap — working rules

**Imported into every Claude session via `CLAUDE.md`. Read it before you
touch anything.** Kept deliberately short for that reason: the full
inventory and task list live in **`ROADMAP-DETAIL.md`**, which you should
open whenever you're picking up, finishing or adding work.

Last full audit: 16 Aug 2026.

## Working rules

1. **Check `ROADMAP-DETAIL.md` before starting.** The work is ordered by
   effort, cheapest first. Anything in its Tier 0–1 is small enough to
   sweep up whenever you're already in that part of the repo.
2. **Claim before you start** on anything Tier 2 or above — several
   educators work in this repo. Add `*(in progress — <name>, <date>)*`
   to the item. Claims older than a month can be taken over.
3. **Tick and date on landing:** `- [x] … *(done 2026-08-20)*`. An
   untouched item and an abandoned half-finished one look identical
   otherwise.
4. **Work you discover gets written down, not done silently.** Add it to
   the right tier in `ROADMAP-DETAIL.md`. The inventory is only useful
   while it's true.
5. **Finishing a half-built year level beats starting a new subject.**
   Year 7 Science, Year 12 Specialist and Year 12 Algorithmics are each
   one unit from complete.
6. **Kodie commits and pushes.** Leave the working tree clean and say
   what changed. Don't run `git commit` or `git push`.

## Standing per-session checklist

The checklist form of what `CLAUDE.md` explains in prose. Most breakage
this repo has seen came from skipping one of these.

- [ ] **Added, renamed, moved or deleted a page?**
      ```bash
      node tools/build-sitemap.js
      node tools/add-sitenav.js --write     # dry-run first without --write
      node tools/add-favicon.js --write     # dry-run first without --write
      node tools/check-links.js             # exits 1 on any finding
      ```
      Never hand-edit `assets/js/sitemap.js`.
- [ ] **Link checker clean?** `node tools/check-links.js`. The class to
      care about is **CASE** — a wrong-case link works on Windows and
      404s on GitHub Pages, so it will not show up in local testing.
- [ ] **New page `<title>`s specific enough to stand alone as nav labels?**
      Fix the title, not `sitemap.js`.
- [ ] **New theme?** The `tokens.css` block *and* the matching
      `.sn-t-<name>` dot in `sitenav.css`. A theme with no dot rule
      silently falls back to the generic accent.
- [ ] **Touched a booklet?** `xelatex` three times from a scratch copy of
      `booklet/`, then check the key hasn't drifted — question numbers
      are auto-generated but the answer key hardcodes them:
      ```bash
      pdftotext -layout booklet/*.pdf - | grep -o 'Q[0-9]*\.[0-9]* ([0-9]* marks\?)'
      ```
- [ ] **Touched a worksheet?** Marks totals agree across `.namebar
      .marks-total`, the toolbar hint, and the index `.wl-marks`.
- [ ] **Touched a gated page?** Round-trip through
      `tools/staff-crypt.html`. Never commit the `*-payload.html`.
- [ ] **New global keyboard shortcut?** Check against both `deck.js`
      (`M`, arrows, space) and `sitenav.js` (`N`, Escape).
- [ ] **Changed the icon?** Test the mark at 16px before shipping.

## Guardrails

**Copyright — never publish or commit.** Two source folders hold
third-party material: `ClaudeSPM/Specialist Maths Calc/Textbook
Chapters/` (scanned Specialist 3&4 textbook chapters) and
`Algorithmics/Authored/` (CLRS, Levitin, Shaffer, Guichard and others).
Derive from them for teaching; publish original material only. When
porting a unit that sits beside these, copy files deliberately rather
than sweeping a directory.

**Student data.** `.gitignore` blocks `*students*.csv` and
`*rooming*.csv`. The Algorithmics source folder also holds
`Assessment/Student Grades/` and `responses*.json` — keep those out. The
rubric tool autosaves to `localStorage`, so marks and names sit in the
browser profile: *Save file* then *Clear all marks* on a shared machine.

**Staff material.** SACs, marking schemes, teacher companions and answer
keys go behind the encrypted gate — never as a plain PDF link, even in
an unlinked folder.

## Deliberately not doing

Recorded so these don't get re-proposed by every session that reads the
repo fresh.

- **A build step or static site generator.** Hand-written HTML on GitHub
  Pages is a feature — any educator can open a file and read it. The two
  generated artefacts (`sitemap.js`, the icon set) have explicit tools
  and are committed.
- **Node dependencies in the repo root.** `node_modules/`,
  `package.json` and `package-lock.json` are gitignored — symlinks in
  `.bin` break git on this filesystem. The tools are dependency-free
  Node scripts by design.
- **KaTeX, Three.js, GSAP or similar.** MathJax is the only maths engine.
  Interactive widgets are inline SVG + vanilla JS as optional modules
  (`orbit.js` is the pattern).
- **Placeholder pages for unbuilt tools.** Twelve were deleted in
  Aug 2026. A card promising something that doesn't exist is worse than
  no card.
- **Per-page inline `<style>` blocks.** The only sanctioned exception is
  a `<style>` inside an inline SVG chart that references tokens.

---

**→ Full inventory, definition of done, and the tiered task list:
`ROADMAP-DETAIL.md`**
