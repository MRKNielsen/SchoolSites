/* ============================================================
   search-index.js — builds the full-text index behind the nav
   drawer's site-wide search. Not run on its own: build-sitemap.js
   requires it and writes assets/js/searchindex.js beside sitemap.js,
   so one command keeps the nav tree and the search index in step.

   The page set is exactly the nav tree's, which means everything the
   tree already excludes (the bare-name legacy folders, *-payload.html,
   404.html) is excluded here too. On top of that:

   - styleguide/ and tools/ are tooling, not class material;
   - the collated worksheets-all booklets repeat every worksheet word
     for word, so a hit there would only duplicate the single sheet;
   - PDFs and the marimo workbook exports have no text we can read;
   - gated pages (anything carrying `var BLOB`) contribute nothing —
     their content is ciphertext, and the plaintext payloads are never
     opened.

   Each page becomes a list of sections: one per slide on a deck (so a
   result can link straight to deck3.html#7), one per h1–h3 or
   worksheet part elsewhere. A section's text is split in two:

     text    what a student sees when the slide first appears
     hidden  unrevealed answers, working steps, .frag fragments and
             part panels — searchable, but the drawer never quotes it,
             so searching on the projector can't show an answer

   Typeset maths (\( … \), \[ … \]) is dropped: TeX source makes poor
   search terms and worse snippets.

   No dependencies: a small, tolerant tokenizer that is enough for the
   hand-written HTML in this repo. It is not a general HTML parser.
   ============================================================ */
"use strict";

const fs = require("fs");
const path = require("path");

const SKIP_PREFIX = ["styleguide/", "tools/"];
const SKIP_PAGE = /(^|\/)worksheets-all(-solutions)?\.html$/;

const VOID = new Set(["area", "base", "br", "col", "embed", "hr", "img", "input",
  "link", "meta", "param", "source", "track", "wbr"]);
/* Raw-text elements: their content is never markup. */
const RAW = new Set(["script", "style", "textarea", "title"]);
/* Subtrees never indexed. */
const SKIP_TAGS = new Set(["head", "button", "select", "textarea", "template", "noscript",
  "desc", "svg:title"]);
const SKIP_CLASSES = ["quiz-container", "start-hint", "orbitsim", "seasonsim", "binomsim", "leversim",
  "chrome", "keyhint", "slidemenu", "lockscreen", "toolbar", "namebar", "back-btn",
  "progress", "homebtn", "ws-bar", "marks", "wl-ico", "wl-marks"];
/* Inline elements that read as a label of their own (a question number,
   a callout label, a chip). Text either side gets a separator, so
   "1" + "The Moon produces…" doesn't index as "1The". Mirrors LABELS in
   sitenav.js. */
const LABELS = ["qn", "lnum", "lbl", "lbl-a", "n", "stepno", "part-label", "pill", "chip",
  "tag", "phase-tag", "bookref", "dc-num", "dc-kind", "wl-label"];
const INLINE = new Set(["a", "abbr", "b", "bdi", "bdo", "cite", "code", "data", "dfn", "em",
  "i", "kbd", "mark", "q", "s", "samp", "small", "span", "strong", "sub", "sup", "time",
  "u", "var", "tspan", "textpath"]);
const SEP = " · ";

const NAMED = {
  amp: "&", lt: "<", gt: ">", quot: '"', apos: "'", nbsp: " ", ensp: " ", emsp: " ", thinsp: " ",
  mdash: "—", ndash: "–", minus: "−", hellip: "…", middot: "·",
  bull: "•", rsquo: "’", lsquo: "‘", ldquo: "“", rdquo: "”",
  laquo: "«", raquo: "»", prime: "′", Prime: "″",
  deg: "°", times: "×", divide: "÷", plusmn: "±", le: "≤", ge: "≥",
  ne: "≠", asymp: "≈", infin: "∞", radic: "√", sum: "∑",
  frac12: "½", frac14: "¼", frac34: "¾", sup2: "²", sup3: "³",
  rarr: "→", larr: "←", harr: "↔", uarr: "↑", darr: "↓",
  rArr: "⇒", lArr: "⇐", hArr: "⇔", forall: "∀", exist: "∃",
  isin: "∈", notin: "∉", cap: "∩", cup: "∪", sub: "⊂", sube: "⊆",
  empty: "∅", and: "∧", or: "∨", not: "¬", there4: "∴",
  epsilon: "ε", alpha: "α", beta: "β", gamma: "γ", delta: "δ",
  Delta: "Δ", theta: "θ", Theta: "Θ", lambda: "λ", mu: "μ",
  pi: "π", sigma: "σ", Sigma: "Σ", phi: "φ", omega: "ω",
  Omega: "Ω", sect: "§", para: "¶", copy: "©", reg: "®",
  check: "✓", cross: "✗", star: "☆", eacute: "é", aacute: "á",
  iacute: "í", oacute: "ó", uacute: "ú", ntilde: "ñ", uuml: "ü",
  ouml: "ö", auml: "ä",
  sim: "∼", prop: "∝", hairsp: " ", rang: "⟩", lang: "⟨", perp: "⊥",
  ang: "∠", part: "∂",
};

/* One pass, so "&amp;#8594;" decodes to the literal text "&#8594;"
   rather than being decoded twice into an arrow. */
function decode(s) {
  return s.replace(/&(#x[0-9a-f]+|#\d+|[a-z][a-z0-9]*);/gi, (m, e) =>
    e[0] !== "#" ? (e in NAMED ? NAMED[e] : m)
    : safeChar(e[1] === "x" || e[1] === "X" ? parseInt(e.slice(2), 16) : parseInt(e.slice(1), 10), m));
}
function safeChar(cp, fallback) {
  try { return String.fromCodePoint(cp); } catch (e) { return fallback; }
}

function stripMaths(s) {
  return s.replace(/\\\([\s\S]*?\\\)/g, " ").replace(/\\\[[\s\S]*?\\\]/g, " ");
}

function attrsOf(s) {
  const out = {};
  const re = /([^\s=\/"'>]+)(?:\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s>]+)))?/g;
  let m;
  while ((m = re.exec(s))) {
    const v = m[2] !== undefined ? m[2] : m[3] !== undefined ? m[3] : m[4] !== undefined ? m[4] : "";
    out[m[1].toLowerCase()] = v;
  }
  return out;
}

const squash = s => s.replace(/\s+/g, " ").trim();

/* ---------- One page → sections ------------------------------ */
function extract(html) {
  if (/var\s+BLOB\s*=/.test(html)) return [];                      /* gated */

  const isDeck = /class\s*=\s*"(?:[^"]*\s)?slide(?:\s[^"]*)?"/.test(html);
  const lower = html.toLowerCase();
  const TOKEN = /<!--[\s\S]*?-->|<!\[CDATA\[[\s\S]*?\]\]>|<![^>]*>|<(\/?)([a-zA-Z][\w:-]*)((?:[^>"']|"[^"]*"|'[^']*')*)>|[^<]+|</g;

  const root = { name: "#root", cls: [], skip: false, hidden: false, serial: 0, id: "" };
  const stack = [root];
  const sections = [];
  let serial = 0, slideNo = 0, cur = null, gap = false;

  /* Pages: everything before the first heading is an untitled section. */
  if (!isDeck) cur = newSection("", "");

  function newSection(anchor, title) {
    return { anchor, title, t: { s: "", last: -1 }, x: { s: "", last: -1 }, cap: null };
  }
  function close() {
    if (!cur) return;
    const title = squash(cur.title || "");
    const t = squash(cur.t.s), x = squash(cur.x.s);
    if (t || x || title) {
      const row = [cur.anchor, title, t];
      if (x) row.push(x);
      sections.push(row);
    }
    cur = null;
  }
  function top() { return stack[stack.length - 1]; }
  function blockSerial() {
    for (let i = stack.length - 1; i >= 0; i--)
      if (!INLINE.has(stack[i].name) || stack[i].label) return stack[i].serial;
    return 0;
  }
  function nearestId() {
    for (let i = stack.length - 1; i >= 0; i--) if (stack[i].id) return stack[i].id;
    return "";
  }

  function text(raw) {
    const t = top();
    if (t.skip || !cur) return;
    let v = decode(stripMaths(raw));
    if (cur.cap !== null && t.capturing) {                       /* heading -> title */
      cur.cap += (cur.cap && cur.capFrom !== t.serial ? " " : "") + v;
      cur.capFrom = t.serial;
      if (!isDeck) return;
    }
    if (!/\S/.test(v)) { gap = true; return; }
    const buf = t.hidden ? cur.x : cur.t;
    const b = blockSerial();
    if (buf.s) buf.s += b !== buf.last ? SEP : gap ? " " : "";
    buf.last = b; gap = false;
    buf.s += v;
  }

  function open(name, attrs, selfClose) {
    const parent = top();
    const cls = (attrs.class || "").split(/\s+/).filter(Boolean);
    const e = { name, cls, id: attrs.id || "", serial: ++serial };
    const has = c => cls.indexOf(c) !== -1;
    e.label = LABELS.some(has);

    e.skip = parent.skip || SKIP_TAGS.has(name) || "data-nosearch" in attrs ||
             SKIP_CLASSES.some(has) || (isDeck && name === "svg:title");

    let veiled = false;
    if (!has("shown") && !has("on")) {
      if (has("a") && (parent.cls.indexOf("box") !== -1 || stack.some(s => s.cls.indexOf("qcard") !== -1))) veiled = true;
      else if (name === "li" && parent.cls.indexOf("steps") !== -1) veiled = true;
      else if (has("frag") && !has("chooser")) veiled = true;
      else if (has("partpanel")) veiled = true;
    }
    if (parent.pendingAns) { veiled = true; parent.pendingAns = false; }   /* legacy decks */
    e.hidden = parent.hidden || veiled;
    e.dataAns = name === "button" && "data-ans" in attrs;
    e.capturing = parent.capturing || false;

    if (isDeck && has("slide")) {
      close();
      slideNo++;
      cur = newSection(slideNo, decode(attrs["data-menu"] || ""));
      e.slide = true;
    } else if (isDeck && cur && !cur.title && cur.cap === null && /^h[1-3]$/.test(name) && !e.skip) {
      cur.cap = ""; e.capturing = true; e.capOwner = true;          /* first heading = slide title */
    } else if (!isDeck && !e.skip && (/^h[1-3]$/.test(name) || has("part-head"))) {
      close();
      stack.push(e);                                                /* so nearestId sees it */
      cur = newSection(nearestId(), "");
      stack.pop();
      cur.cap = ""; e.capturing = true; e.capOwner = true;
    }

    if (name === "br") { gap = true; return; }
    if (VOID.has(name) || selfClose) return;
    stack.push(e);
  }

  function end(name) {
    let i = stack.length - 1;
    while (i > 0 && stack[i].name !== name) i--;
    if (i === 0) return;                                            /* stray end tag */
    while (stack.length > i) {
      const e = stack.pop();
      if (e.capOwner && cur) { cur.title = cur.title || cur.cap; cur.cap = null; }
      if (e.dataAns) top().pendingAns = true;
      if (e.slide) close();
    }
  }

  /* Text tokens stop at every "<", including the one in "\(a < b\)",
     so a run of them is gathered before maths is stripped from it. */
  let m, run = "";
  const flush = () => { if (run) { text(run); run = ""; } };
  while ((m = TOKEN.exec(html))) {
    if (m[2] || (m[0][0] === "<" && m[0].length > 1)) flush();
    if (m[2]) {
      let name = m[2].toLowerCase();
      if (name === "title" && stack.some(s => s.name === "svg")) name = "svg:title";
      if (m[1]) { end(name); continue; }
      const attrStr = m[3] || "";
      open(name, attrsOf(attrStr), /\/\s*$/.test(attrStr));
      if (RAW.has(name)) {
        const closeAt = lower.indexOf("</" + name, TOKEN.lastIndex);
        const stop = closeAt === -1 ? html.length : closeAt;
        if (name !== "script" && name !== "style") text(html.slice(TOKEN.lastIndex, stop));
        TOKEN.lastIndex = stop;
      }
    } else if (m[0][0] !== "<" || m[0] === "<") {
      run += m[0];
    }
  }
  flush();
  close();
  return sections;
}

/* ---------- Walk the nav tree -------------------------------- */
function buildSearchIndex(tree, ROOT) {
  const pages = [];

  function visit(nodes, ctx, theme) {
    for (const n of nodes) {
      const k = n.k || theme;
      if (n.h && !n.p && !n.x && !SKIP_PAGE.test(n.h) && !SKIP_PREFIX.some(p => n.h.startsWith(p))) {
        let html = "";
        try { html = fs.readFileSync(path.join(ROOT, n.h), "utf8"); } catch (e) { /* missing */ }
        const s = html ? extract(html) : [];
        if (s.length) {
          const fmt = !/class\s*=\s*"(?:[^"]*\s)?slide(?:\s[^"]*)?"/.test(html) ? "p"
                    : /assets\/js\/deck\.js/.test(html) ? "d" : "l";
          const page = { h: n.h, t: n.t, c: ctx.join(" · "), f: fmt, s };
          if (k) page.k = k;
          pages.push(page);
        }
      }
      if (n.c) visit(n.c, n.g || n.t === "Home" ? ctx : ctx.concat(n.t), k);
    }
  }
  visit(tree, [], "");
  return pages;
}

function render(pages) {
  return `/* ============================================================
   searchindex.js — GENERATED FILE, DO NOT EDIT BY HAND
   Regenerate with:  node tools/build-sitemap.js
   (it writes this file and sitemap.js together; see
   tools/search-index.js for what is and isn't indexed)

   Loaded by assets/js/sitenav.js only when someone types in the
   drawer's search box — never on page load.

   One page per line:
     h = href from repo root   t = nav label   c = context (year · subject · unit)
     k = theme   f = link format: d deck (#n), l legacy deck (#slide-n), p page (#id)
     s = sections: [anchor, title, text, hidden?]
         anchor is the slide number on a deck, an element id (or "") on a page;
         hidden is answer / working text that is searchable but never quoted
   ============================================================ */
window.SEARCHINDEX = {"v":1,"pages":[
${pages.map(p => JSON.stringify(p)).join(",\n")}
]};
`;
}

module.exports = { buildSearchIndex, render, extract };
