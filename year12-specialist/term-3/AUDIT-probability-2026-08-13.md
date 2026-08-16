# Specialist 3&4 · Probability & Statistics content audit

**Date:** 13 August 2026
**Scope:** `slides/T3W00`, `T3W03`, `T3W04`, `T3W05`, `T3W06`, `T3W07`
**Reference text:** *Cambridge Specialist Mathematics VCE Units 3&4* (2nd ed., Evans et al. 2023),
Chapter 15 (§15A–15F) and Chapter 16 (§16A–16E), including every set exercise.

Two questions were asked of every slide:

1. **Is it right?** — every formula, worked example and numeric answer recomputed independently.
2. **Is it enough?** — can a student who has seen only these decks attempt *every* question
   in the matching exercise?

Question 1 turned up one hard error and a handful of stale cross-references. Question 2 turned
up more: five question types that appear repeatedly in the exercises had no coverage anywhere
in the deck set. Both are recorded below, with what was done.

---

## A · Errors found and corrected

| # | Deck | What was wrong | Fix |
|---|------|----------------|-----|
| A1 | T3W06, L1 Example 1 | "At \(\alpha = 0.02\) the one-tail test would reject and the two-tail wouldn't." **False** — the one-tail \(p\)-value is \(0.0228 > 0.02\), so *neither* rejects at 2%. The claim needs a level strictly between 0.0228 and 0.0455. | Changed to \(\alpha = 0.03\), with both \(p\)-values shown inline so the comparison is checkable on the slide. |
| A2 | T3W06, L2 | Lesson labelled **16D**, but its content (a two-tail test at level \(\alpha\) rejects exactly when \(\mu_0\) falls outside the \((1-\alpha)\) CI) is **§16C**. §16D is *Two-tail tests revisited* — the absolute-value material, which was absent. | Relabelled to 16C–16D; the CI↔test fact now reads "Fact (16C)". §16D content added (see B5). |
| A3 | T3W05, closing slide | "Type I and II errors (16D–E)". Errors are **§16E** only. | Corrected, and the sentence now previews §16D by name. |
| A4 | T3W04, title slide | Banner advertised *SAC 2 — Differential Equations, Mon 3–Tue 4 Aug (Week 4)*. T3W04 is a Week 5 deck; SAC 2 had already been sat, and its Week-5 partner T3W03 advertises SAC 3. | Banner now reads *SAC 3 (Probability & Statistics): Thu 27 Aug, Week 7*, matching T3W03. |
| A5 | T3W04, closing slide | "Problem Set 3 (Random Variables) covers Weeks 3–4" — Weeks 3–4 were Ch 13 and SAC 2, not random variables. | Now reads "covers Chapter 15". |
| A6 | T3W04, L3 | CLT guideline stated as \(n \ge 30\). The text's wording is "a sample size of 25 to 30 is sufficient" unless the distribution is very skewed. | Reworded to match, including the "improves as \(n\) grows" clause. |
| A7 | T3W05, Example 3 & Checkpoint 2 | Sample-size working compressed \(2z\sigma/w\) into an unexplained constant (e.g. "\(\sqrt{n} \ge 1.96 \times 6\)" when \(\sigma = 12\), \(w = 4\)). Arithmetically correct but unreproducible, and it hides exactly the step students get wrong. | Rewritten to show \(\dfrac{2z\sigma}{w}\) explicitly in each case. |

**Everything else checked out.** All other numeric answers across the six decks were recomputed
and are correct, including the diagram annotations: `X₁+X₂ ~ N(20, 8)` vs `2X ~ N(20, 16)`,
`D = T − S ~ N(2, 2.5²)` with `P(D < 0) ≈ 0.212`, the six-pack `P(Z < −2.449) ≈ 0.007`, the
Type II figures 0.20 → 0.0004, and the revision deck's `P(T > 205) ≈ 0.113` and `p ≈ 0.0139`.

---

## B · Coverage gaps — question types the decks did not prepare

These are the ones that matter. Each is a technique the exercises assume, that appeared nowhere
in the deck set.

### B1 · Continuous random variables and probability density functions — *the biggest gap*

The primer's Part 2 was titled "Discrete random variables" and the whole deck set worked only
from distribution tables and stated \(\mu\), \(\sigma\). But density functions run right through
both chapters:

- **Ex 15A Q3, Q4, Q5, Q8** — "\(X\) has probability density function \(f(x) = \ldots\); find
  \(\Pr(X < a)\); let \(Y = aX + b\), find \(\Pr(Y \le c)\)".
- **Ex 15B Q5** — \(E\), \(\text{Var}\), \(\text{sd}\) of \(X_1 + X_2 + X_3\) from a density.
- **Ex 15F Q1, Q4, Q5** — extract \(\mu\) and \(\sigma\) from a density, *then* apply the CLT.
  This is the text's own Example 15 and is the standard exam shape.

A student working only from the decks could not start any of these ten questions.

**Added:**

- **T3W00** — two new slides: *Continuous random variables: the density function*
  (\(f \ge 0\), \(\int f = 1\), probability as area, \(\Pr(X = c) = 0\)) and
  *\(E(X)\) and \(\text{Var}(X)\) by integration*, worked on \(f(x) = 1.5(1-x^2)\) on \([0,1]\)
  — the same three lines as the discrete case with \(\sum \to \int\), plus the CAS routine.
  Part 2 retitled; the formula card now carries both columns.
- **T3W03 L1** — new slide *When \(X\) is continuous: one extra step*, deriving
  \(\Pr(Y \le y) = \Pr\!\left(X \le \frac{y-b}{a}\right)\) and working it on \(f(x) = 2x\).
- **T3W04 L3** — new slide *The standard CLT question: a population given by a density
  function*, worked end to end on \(f(x) = x/8\) on \([0,4]\), \(n = 36\).

### B2 · Building a distribution, rather than just its mean and variance

Two separate omissions, both of which cost whole questions:

**Discrete transforms.** Ex 15A Q1, Q2 and Q11 ask "what is the probability distribution of
\(C\)?" and "what is the probability that the cost is more than \$2000?". The decks jumped
straight to \(E\) and \(\text{Var}\), which cannot answer either.
→ **T3W03 L1**, new slide *The distribution of \(Y = aX+b\), not just its mean* — transform the
values, keep the probabilities, read the probability off the new table.

**Sums from first principles.** Ex 15B Q1, Q2, Q6, Q7, Q8 require a two-way table:
"more than three children in the combined group", \(\Pr(X_1 - X_2 = 0)\),
\(\Pr(X_1 + 3X_2 = 6)\). The shortcut formulas are useless for all of them.
→ **T3W03 L2**, new slide *First principles: the distribution of a sum*, with the full 3×3
table for a spinner, the collected distribution, and the cross-check that the table's
\(E(S) = 3.4\) and \(\text{Var}(S) = 1.22\) agree with \(2\mu\) and \(2\sigma^2\).

### B3 · Inverse problems — solve for \(n\)

**Ex 15C Q7** (largest number of people in a lift, 99% confident) and **Q8** (20 batteries,
145 hours) fix the probability and ask for \(n\). Because both \(n\mu\) and \(\sqrt{n}\,\sigma\)
move — at different rates — this cannot be done by standardising once.
→ **T3W03 L3**, new slide *Running it backwards: "how many?"*, writing \(T_n \sim N(n\mu, n\sigma^2)\)
and testing integers (worked answer: 8 adults).

### B4 · Margin of error — *highest-risk gap*

The decks taught only **width**. But §16A defines **margin of error**, and
**Ex 16A Q15, Q16, Q17, Q18, Q19** are all phrased as margin of error — "within 20 of the
population mean", "within 0.5 grams of \(\mu\)", "the difference between the sample mean and
the true mean is not more than 10". A student applying the width formula to those gets
**\(n\) four times too large**, with no internal signal that anything is wrong.

Separately, **Ex 16A Q14 a–d** asks for the width↔\(n\) scaling as pure algebra
("by what factor must \(n\) increase to decrease the width by 80%?").

**Added — T3W05 L2:**

- New slide *Margin of error — and the factor-of-4 trap*: \(M = z\sigma/\sqrt{n}\),
  width \(= 2M\), and a table matching each phrasing to its condition on \(n\). Worked both
  ways on the same numbers (\(\sigma = 12\), target 3) to show 62 vs 246.
- New slide *Scaling width against \(n\) — without any numbers*:
  \(\dfrac{n_2}{n_1} = \left(\dfrac{W_1}{W_2}\right)^2\), with all four parts of Q14 modelled,
  and the "decrease by 80% means \(W_2 = 0.2W_1\)" warning.
- Checkpoint 2 gained a part (c) contrasting a margin-of-error target with a width target.

### B5 · Section 16D in its entirety

**Every question in Exercise 16D (Q1–Q10) was unanswerable from the decks.** §16D recasts the
two-tail \(p\)-value in absolute-value form, and the exercise is built on it: \(\Pr(|Z| \ge a)\),
\(\Pr(|X - \mu| \ge d)\), \(\Pr(|\bar{X} - \mu| \ge |\bar{x} - \mu|\)), and "find the size of
difference that would lead you to reject".

**Added — T3W06 L2**, two new slides:

- *Section 16D: the two-tail \(p\)-value, written with \(|\;\;|\)* — the definition,
  \(\Pr(|Z| \ge a) = 2\Pr(Z \le -a)\) by symmetry, and the standardise-first warning
  (\(\Pr(|X-\mu| \ge d)\) uses \(\sigma\); \(\Pr(|\bar{X}-\mu| \ge d)\) uses \(\sigma/\sqrt{n}\) —
  which one depends on whether the question says "a value of \(X\)" or "the mean of a sample").
- *Worked example: "differs by at least …"* — all three parts of the Q10 shape, including the
  inverse part, on a deliberately borderline case (\(p = 0.0532\), do **not** reject) that ties
  back to the CI relationship on the previous slide.

### B6 · Strength of evidence

**Ex 16B Q5, Q6, Q7, Q8** ask students to *interpret* a \(p\)-value — "write a statement
interpreting each of the following p-values in terms of the strength of evidence". The text
supplies a fixed vocabulary (insufficient / good / strong / very strong at 0.05, 0.01, 0.001).
The decks only ever offered a binary reject-or-not at \(\alpha\), so four questions had no
usable answer.
→ **T3W05 L3**, new slide *Strength of evidence — the other way to answer*, with the table,
the distinction between "test at the 5% level" and "interpret this \(p\)-value", a model
sentence, and the standard caution that \(p\) is not \(\Pr(H_0 \text{ true})\).

### B7 · CAS procedures

The text teaches specific CAS routes that the decks never named. On a CAS-active SAC this is
not optional.

- **§16A / §16B / §16C** — `z Interval` and `z Test` (TI-Nspire), `One-Sample Z Int` and
  `One-Sample Z-Test` (ClassPad), and the **`ME`** output that *is* the margin of error.
  → **T3W05**, new slides *On CAS, and the exact \(z\) values* (L1) and *The \(z\)-test on CAS* (L3).
  The latter also introduces the term **\(z\)-test**, defined in the text and previously absent,
  and warns that the alternative-hypothesis dropdown silently halves or doubles the \(p\)-value.
- **§16A Q5, Q6, Q7, Q9** hand over a raw data list — one-variable statistics for \(\bar{x}\),
  but using the **given** \(\sigma\), not the CAS's \(s_x\). Noted on the same slide.
- **§15E Q1–Q3** require simulation with specific syntax. The decks described simulation
  conceptually with no commands.
  → **T3W04 L3** simulation slide now carries the TI-Nspire
  `approx(seq(mean(randnorm(…)),k,1,500))` and ClassPad `mean(randNorm(…))` + Fill Range
  procedures, for normal, uniform and binomial populations.

### B8 · Two smaller additions

- **General \(n\)-variable rule with *different* distributions** — §15B's final result and
  Ex 15B Q12b (two bags of apples, three bags of bananas). The deck stated only the iid case
  \(n\sigma^2\), inside a discussion box.
  → **T3W03 L2**, added as a `.box.defn` alongside the two-variable rule, with the
  \(2A_1 + 3B_1\) vs \(A_1 + A_2\) reading warning.
- **Reverse problems** — Ex 15B Q11 gives the mean and variance of \(aX + bY\) and asks for
  \(a, b \in \mathbb{N}\). One equation is quadratic, so the method is *substitute and test
  the integer candidates*, which is worth stating.
  → **T3W03**, Checkpoint 2 part (c) plus a hint box on the method.
- **\(P(\text{Type I})\) from a stated critical value** — Ex 16E Q7a gives the researcher's
  rule rather than \(\alpha\). The deck only computed Type II from \(\alpha\).
  → **T3W06 L4**, new slide *When the critical value is handed to you*, doing both errors from
  the same critical value with the "same \(c\), same \(\text{sd}(\bar{X})\), different \(\mu\)"
  framing.

---

## C · Coverage after the changes

| Exercise | Status |
|----------|--------|
| 15A | ✅ all question types covered (was: Q1, Q2, Q3, Q4, Q5, Q8, Q11 uncovered) |
| 15B | ✅ (was: Q1, Q2, Q5, Q6, Q7, Q8, Q11, Q12b uncovered) |
| 15C | ✅ (was: Q7, Q8 uncovered) |
| 15D | ✅ — was already complete |
| 15E | ✅ (was: no CAS syntax for Q1–Q3) |
| 15F | ✅ (was: Q1, Q4, Q5 uncovered) |
| 16A | ✅ (was: Q5–Q7, Q9, Q14–Q19 uncovered) |
| 16B | ✅ (was: Q5, Q6, Q7, Q8 uncovered) |
| 16C | ✅ — was already complete |
| 16D | ✅ (was: **Q1–Q10, the entire exercise**, uncovered) |
| 16E | ✅ (was: Q7a uncovered) |

One item is left deliberately uncovered: **Ex 16A Q12** (the probability that both, or at least
one, of two independent confidence intervals contain \(\mu\)). It needs only \(0.95^2\) and
\(1 - 0.05^2\) from the primer's Part 1, so it is a legitimate synthesis question rather than a
gap.

---

## D · Flagged for a teaching decision — not changed

1. **T3W07 week placement.** The deck is titled *SAC 3 Revision* and its subtitle says
   "Week 7", with Lesson 4 describing "revision Monday, timed practice SAC mid-week, SAC 3 on
   the scheduled day". But `index.html` links it only from **Week 9** (REVISION), while Week 7
   links T3W06. Either the deck is being reused as a general Ch 15–16 revision deck in Week 9
   (in which case the Lesson 4 logistics slide and the "Week 7" subtitle should be softened),
   or the index should link it from Week 7 as well. Left alone — it is a scheduling call.
2. **Inline style hacks.** All six decks carry `style="margin-top:12px"`-type spacing on reveal
   lists and centred display maths, which `CLAUDE.md` asks new work to avoid (deck.css already
   supplies the spacing). New slides added in this pass use no inline margins; the pre-existing
   ones were left in place rather than churn every slide. Worth a separate tidy pass.
3. **Inert classes.** `goals`, `col` and `narrow` appear in the markup but are defined in
   neither `deck.css` nor `tokens.css`. They are harmless — `.section-slide ul` and the
   `.cols` grid do the work — but `narrow` in particular looks like it was meant to do
   something. Pre-existing; not introduced here.
4. **Slide-jump menu.** Only T3W00 has the `.menubtn` / `.slidemenu` markup. T3W03–T3W07 now
   run to 21–25 slides each, which is where a contents grid starts to earn its keep.

---

## E · Follow-up: live CLT simulation added to T3W04 Lesson 3

§15E is *"Investigating the distribution of the sample mean **using simulation**"*, and the
pass above had only added the CAS commands for it — the deck still asserted what a simulation
would show rather than showing it. A live simulation now sits between the CAS-syntax slide and
the formal statement of the theorem, so the theorem is stated *after* the class has watched it
happen.

**What it does.** Two panels on a shared x-scale: the population on the left, a histogram of
simulated sample means on the right with the predicted \(N(\mu, \sigma^2/n)\) curve overlaid.
Four population shapes on \(\{1,\dots,6\}\) — all four exact, so every number on screen can be
checked by hand:

| shape | \(\mu\) | \(\sigma\) |
|-------|--------|-----------|
| Uniform (fair die) | 3.5 | 1.7078 |
| Strongly skewed | 2.02 | 1.3113 |
| Two peaks | 3.5 | 2.2023 |
| Already bell-ish | 3.5 | 1.2042 |

Controls: shape tabs, an \(n\) slider (1–50), and *Draw 1 sample* / *Draw 200* / *Clear*.
A readout table puts predicted \(\mu\) and \(\sigma/\sqrt{n}\) beside the simulated mean and sd
of the \(\bar{x}\) values, so the CLT's two quantitative claims are checkable live rather than
taken on trust.

**Three design decisions worth recording:**

- **Shared x-scale across both panels.** The narrowing of \(\bar{X}\) is then a direct visual
  comparison against the population it came from, rather than two separately-scaled charts.
- **Bin width tracks \(1/n\)** until that becomes finer than 0.1. Sample means from a discrete
  population *are* discrete, and fixed bins turn that into a misleading comb. A consequence
  worth using in class: at \(n = 1\) the right panel reproduces the left panel exactly.
- **Draw 1 sample** marks the \(n\) individual values on the population panel and the single
  \(\bar{x}\) they produce on the mean panel — the step students most often lose, since the
  right-hand histogram is a distribution of *summaries*, not of observations.

The skewed population is the one to dwell on: it is the only shape still visibly asymmetric at
\(n = 5\), which is what the text's "unless the distribution is very skewed" caveat means.

**Sizing.** The chart is deliberately modest: a `960 × 252` viewBox capped at `max-width: 880px`
and centred, so it renders about `880 × 231` px rather than filling the slide width. That matches
how the static figures in T3W03 are constrained, and it leaves the slide's tabs, controls,
readout table and closing note comfortably above the fold on a 1080p projector — the chart is a
demonstration inside the lesson, not the whole slide.

**Implementation notes.** One slide-local `<script>` at the end of T3W04, after deck.js — no
navigation logic, no new CSS, no new palette. Every colour is a token
(`--accent`, `--accent-warm`, `--ink-soft`, `--neg`, `--muted`); every layout class already
exists in deck.css (`.graph-card`, `.ctrl`, `.parts`, `.ptab`, `.legend`, `.tbl`, `.reveal-btn`).
Two interactions with shared code were handled explicitly:

- SVG text is written in words, not MathJax — MathJax cannot reach inside `<svg>`
  (see CLAUDE.md). Symbols appear in the surrounding HTML instead.
- deck.js also listens on `.ptab` and marks the outgoing tab `.done` (a ✓, correct for
  worked-example parts, wrong for a shape selector). Its listener is registered *after* the
  inline script's — deck.js is deferred, the inline script is not — so the class is cleared on
  a zero-delay timeout, once the synchronous handler queue has drained.
- The chart and controls carry `data-noswipe`, and deck.js's keyboard handler already ignores
  `input` elements, so dragging the slider on a touchscreen or whiteboard cannot advance the
  deck.

**Verified** by loading the real page (with the real deck.js) in jsdom and driving it: no
console errors; axis, bars and curve all render; every button and the slider behave; tab state
ends with exactly one `.active` and no stray `.done`; arrow keys do not steal focus from the
slider; and nothing — bar, curve, μ label or sample dot — falls outside its panel across all
four shapes at \(n = 1, 2, 3, 5, 10, 11, 30, 50\), including the worst-case dot stack (skewed
population, \(n = 50\), most values landing on \(x = 1\)). The simulated sd
of \(\bar{x}\) matched \(\sigma/\sqrt{n}\) at every \(n\) tested (e.g. skewed population:
0.398 vs 0.415 at \(n=10\), 0.230 vs 0.239 at \(n=30\), 0.175 vs 0.185 at \(n=50\)).

T3W04 is now 22 slides.

---

## F · Follow-up: explanations expanded across all six decks

The decks were written to be projected, so most points were single-clause assertions — correct,
but stating *what* is true without saying *why*. Since these pages are also the version a
student reads alone on the site, every explanatory bullet has been rewritten as a short bold
lead followed by full reasoning.

**The pattern used throughout**, so the decks still work on a screen at the back of a room:

> **Variances add even when you subtract.** Mechanically this is the rule with \(b = -1\):
> the coefficient is squared and the minus sign disappears. But it is the *right* answer, not
> an accident of the algebra — uncertainty in \(Y\) makes \(X - Y\) uncertain in exactly the
> way uncertainty in \(X\) does. Errors accumulate; they do not cancel…

The eye still lands on the bold claim; the reasoning is there for anyone who stops.

**What the expansions consistently cover** — each point now answers three questions rather
than one: *what is true*, *why it is true*, and *why the wrong answer is tempting*. So the
variance rules are traced back to the square in the definition of variance; the \(2X\) versus
\(X_1 + X_2\) distinction is explained through cancellation rather than asserted; "do not
reject" is separated from "accept" via the jury analogy the text itself uses; and the
confidence-interval interpretation is grounded in *the interval is random, \(\mu\) is fixed*.
Several additions quantify the cost of the standard error — taking the wrong variance route in
the swimming example gives \(p \approx 0.065\) instead of \(0.212\), and the lift example
gives a 31% overload risk instead of 2.3% — because a wrong answer that looks plausible is
exactly the kind students do not catch.

| deck | slides | words before | words after | growth |
|------|-------:|-------------:|------------:|-------:|
| T3W00 | 23 | 2 420 | 4 303 | +78% |
| T3W03 | 25 | 2 723 | 3 863 | +42% |
| T3W04 | 22 | 1 866 | 3 434 | +84% |
| T3W05 | 25 | 2 564 | 3 608 | +41% |
| T3W06 | 23 | 2 338 | 3 311 | +42% |
| T3W07 | 15 | 1 108 | 1 647 | +49% |
| **total** | **133** | **13 019** | **20 166** | **+55%** |

**Left deliberately terse:** the learning-intention lists on section dividers, the week-map
tables, the numbered reveal steps inside worked examples (prose there would break the pacing of
the reveal), and the rapid-fire drill in T3W07. Those are scaffolding, not explanation.

**Fit.** No slide splitting was needed. Estimating rendered height against the deck's own
typography — 16.5 px body text at line-height 1.5, 90 vw content width, on a 1080p projector
with about 918 px of usable height — the tallest slide in the set is the T3W04 simulation at
roughly 908 px, and every other slide sits comfortably below. Note that `.frag` uses
`visibility: hidden`, not `display: none`, so hidden reveal content occupies its space at all
times and is included in those figures. Slides that do overflow are handled gracefully anyway
by deck.css's scroll-and-fade, so the risk here is aesthetic rather than functional.

**One typographic consequence worth a decision.** At 90 vw with no measure constraint, a
full-width line of body text runs to roughly 200 characters on a 1080p display — well beyond
the 45–75 that reads comfortably. This was already true of the decks before this pass; longer
paragraphs simply make it visible. deck.css already contains the fix in miniature
(`.lede { max-width: 66ch }`), but `.lede` also greys its text, so it is wrong for primary
content. Adding a measure cap to `.slide > p` and `.slide > ul` in deck.css would improve every
deck in the repo at once — including other educators' — so it is left as a proposal rather than
done unilaterally.

---

## G · Verification performed

- **Numeric.** Every figure in every slide added or edited was recomputed in Python
  (`scipy.stats.norm` for tail areas, `sympy` for the density-function integrals) and matched
  to the printed value. All 60+ checks pass, including the two-way spinner table enumerated
  from first principles and cross-checked against \(2\mu\) and \(2\sigma^2\).
- **Interactive.** The T3W04 simulation was driven headlessly in jsdom against the real page
  and the real deck.js — see section E for what was exercised and the predicted-vs-simulated
  figures.
- **Structural.** All six decks parse with balanced tags and no unclosed elements.
  Example numbering is sequential and gap-free in each deck after the insertions
  (T3W03: 1–9, T3W04: 1–4, T3W05: 1–6, T3W06: 1–6).
- **Design system.** No new CSS, no new inline colours, no per-slide margin hacks. New slides
  use only existing components — `.box.key/.defn/.example/.hint/.try/.cas`, `.tbl`, `.steps`,
  `.frag`, `.result`, `.cols`. Reveal buttons audited for correct wiring: `data-frag` buttons
  all have `.frag` targets, and the new step-reveal buttons all have an `ol.steps` in the same
  slide (deck.js falls back to `.steps` only when `data-frag` is absent).
- **Sitemap.** No pages added, renamed, moved or deleted, and no `<title>` changed, so
  `assets/js/sitemap.js` does not need rebuilding.
