#!/usr/bin/env node
/* ============================================================
   build-sitemap.js — regenerate assets/js/sitemap.js
   Run from the repo root, no dependencies:

       node tools/build-sitemap.js

   Walks the repo for .html pages, reads each page's <title> and
   <body class>, and writes a grouped tree that assets/js/sitenav.js
   renders into the site-wide navigation drawer.

   Re-run this after adding, renaming or removing a page. Nothing else
   needs editing — sitenav.js loads sitemap.js itself.
   ============================================================ */
"use strict";

const fs = require("fs");
const path = require("path");

const ROOT = path.resolve(__dirname, "..");
const OUT = path.join(ROOT, "assets", "js", "sitemap.js");

/* ---------- Configuration ----------------------------------- */

/* Directories never walked. */
const SKIP_DIRS = new Set([
  ".git", ".github", "node_modules", "assets", "img", "images", "fonts",
  "booklet", "problemsets", "revision", "sat", "data",
]);

/* Top-level folders left out of the nav. The four bare-name subject
   folders are pre-year-prefix duplicates of their year12-* equivalents
   and are linked from nowhere; listing them would give students two
   doors to the same room. Delete a line here to surface one again. */
const SKIP_TOP = new Set(["algorithmics", "foundation", "methods", "specialist"]);

/* Individual pages left out: gated plaintext (gitignored anyway),
   fragments that are not standalone pages, and 404.html — GitHub Pages
   serves that one automatically and it is a destination you arrive at by
   accident, not one to offer in a contents list. */
const SKIP_FILE = /(-payload\.html$)|^404\.html$/;

/* Third-party exports we link to but never inject into (marimo apps). */
const OPAQUE_DIRS = new Set(["workbooks"]);

/* Pages whose <title> is useless (third-party exports name themselves
   after their build slug). Matched against the path from the repo root,
   so a rule can be scoped to one folder — necessary here because the
   slide decks share the workbooks' U4Wnn stem. */
const FILE_LABEL_RULES = [
  { test: /\/workbooks\/u4w(\d+)\.html$/i, label: m => "Workbook " + Number(m[1]) },
];

/* Titles that read badly when derived mechanically. Keyed by path from
   the repo root. */
const LABEL_OVERRIDES = {
  "index.html": "All year levels",
  "year12-specialist/term-3/index.html": "Term 3 — course hub",
  "year12-algorithmics/unit-4/index.html": "Unit 4 — course hub",
  "year10-mathematics/10methods-primer/index.html": "Course home",
  "styleguide/deck-demo.html": "Deck system demo",
  "styleguide/deck-template.html": "Deck starter template",
  "tools/staff-crypt.html": "Staff blob tool (encrypt / decrypt)",
  "tools/page-builder.html": "Page builder (slides & worksheets)",
};

/* Unit folder names → the label used for the unit itself. Derived from
   the unit index <title> when absent here. */
const UNIT_OVERRIDES = {
  "year12-specialist/term-3": "Term 3",
  "year12-algorithmics/unit-4": "Unit 4",
  "year10-mathematics/10methods-primer": "10 Methods Primer",
};

const SUBJECT_LABELS = {
  mathematics: "Mathematics",
  science: "Science",
  methods: "Mathematical Methods",
  specialist: "Specialist Mathematics",
  foundation: "Foundation Mathematics",
  algorithmics: "Algorithmics",
};

const YEAR_BANDS = {
  7: "Junior", 8: "Junior", 9: "Middle", 10: "Middle",
  11: "VCE Units 1 & 2", 12: "VCE Units 3 & 4",
};

/* Which group a file inside a unit belongs to, in display order. */
const GROUPS = [
  { key: "lessons",    label: "Lessons",
    test: (rel, file) => /\/slides\//.test(rel) || /^deck\d+\.html$/i.test(file) || /_Slides\.html$/i.test(file) },
  { key: "worksheets", label: "Worksheets",
    test: (rel, file) => /^worksheet\d+/i.test(file) },
  { key: "workbooks",  label: "Workbooks",
    test: (rel) => /\/workbooks\//.test(rel) },
  { key: "resources",  label: "Resources", test: () => true },
];

/* ---------- Small helpers ----------------------------------- */

const NAMED = {
  amp: "&", lt: "<", gt: ">", quot: '"', apos: "'", nbsp: " ",
  mdash: "\u2014", ndash: "\u2013", middot: "\u00b7", hellip: "\u2026",
  rsquo: "\u2019", lsquo: "\u2018", ldquo: "\u201c", rdquo: "\u201d",
  deg: "\u00b0", times: "\u00d7", theta: "\u03b8", Theta: "\u0398",
  Omega: "\u03a9", minus: "\u2212", bull: "\u2022",
};

function decode(s) {
  return s
    .replace(/&#x([0-9a-f]+);/gi, (_, h) => String.fromCodePoint(parseInt(h, 16)))
    .replace(/&#(\d+);/g, (_, d) => String.fromCodePoint(parseInt(d, 10)))
    .replace(/&([a-z]+);/gi, (m, n) => (n in NAMED ? NAMED[n] : m))
    .replace(/\s+/g, " ")
    .trim();
}

function read(file) {
  try { return fs.readFileSync(file, "utf8"); } catch { return ""; }
}

function titleOf(html) {
  const m = html.match(/<title[^>]*>([\s\S]*?)<\/title>/i);
  return m ? decode(m[1]) : "";
}

function themeOf(html) {
  const m = html.match(/<body[^>]*\sclass="([^"]*)"/i);
  if (!m) return "";
  const t = m[1].match(/theme-([a-z0-9-]+)/i);
  return t ? t[1] : "";
}

/* Remove a trailing " · Context" / " — Context" / " | Context" when the
   context is something the tree already tells you (the unit, subject or
   year you are sitting inside). Applied repeatedly so a title carrying
   two of them loses both. */
function stripContext(title, contexts) {
  let out = title, changed = true;
  while (changed) {
    changed = false;
    for (const c of contexts) {
      if (!c) continue;
      const re = new RegExp("\\s*[|\u00b7\u2014\u2013-]\\s*" + esc(c) + "\\s*$", "i");
      if (re.test(out)) { out = out.replace(re, ""); changed = true; }
    }
  }
  return out.trim() || title;
}

const esc = s => s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");

/* Second pass: drop a whole trailing segment that merely *mentions* the
   subject or unit ("… — VCE Algorithmics Unit 4"). Only fires when the
   remaining text is still substantial, so a title that is nothing but
   its context survives. */
function stripLooseContext(title, keys) {
  for (const k of keys) {
    if (!k) continue;
    const re = new RegExp("\\s*[|\u00b7\u2014\u2013]\\s*[^|\u00b7\u2014\u2013]*\\b" + esc(k) + "\\b[^|\u00b7\u2014\u2013]*$", "i");
    const cut = title.replace(re, "").trim();
    if (cut && cut.length >= 4) return cut;
  }
  return title;
}

/* deck2 sorts before deck10. */
function natcmp(a, b) {
  return String(a).localeCompare(String(b), "en", { numeric: true, sensitivity: "base" });
}

function walk(dir, acc = []) {
  for (const e of fs.readdirSync(dir, { withFileTypes: true }).sort((x, y) => natcmp(x.name, y.name))) {
    const full = path.join(dir, e.name);
    if (e.isDirectory()) {
      if (SKIP_DIRS.has(e.name)) continue;
      walk(full, acc);
    } else if (e.isFile() && e.name.toLowerCase().endsWith(".html")) {
      if (SKIP_FILE.test(e.name)) continue;
      acc.push(path.relative(ROOT, full).split(path.sep).join("/"));
    }
  }
  return acc;
}

function pageInfo(rel) {
  const html = read(path.join(ROOT, rel));
  return { rel, title: titleOf(html), theme: themeOf(html) };
}

/* ---------- Build the tree ---------------------------------- */

const all = walk(ROOT).filter(rel => !SKIP_TOP.has(rel.split("/")[0]));
const info = new Map(all.map(rel => [rel, pageInfo(rel)]));
const used = new Set();

function label(rel, contexts, loose) {
  if (LABEL_OVERRIDES[rel]) return LABEL_OVERRIDES[rel];
  for (const r of FILE_LABEL_RULES) {
    const m = ("/" + rel).match(r.test);
    if (m) return r.label(m);
  }
  const t = info.get(rel).title;
  if (!t) return path.basename(rel, ".html");
  return stripLooseContext(stripContext(t, contexts), loose || []);
}

function node(rel, contexts, loose) {
  used.add(rel);
  const n = { t: label(rel, contexts, loose), h: rel };
  const th = info.get(rel).theme;
  if (th) n.k = th;
  if (OPAQUE_DIRS.has(rel.split("/").slice(-2)[0])) n.x = 1;
  return n;
}

/* Files that live under `dir` (at any depth) and are not `dir/index.html`. */
function childrenOf(dir) {
  return all.filter(r => r.startsWith(dir + "/") && r !== dir + "/index.html" && !used.has(r));
}

function groupFiles(dir, files, contexts, loose) {
  const buckets = new Map(GROUPS.map(g => [g.key, []]));
  for (const rel of files.sort(natcmp)) {
    const file = rel.split("/").pop();
    const g = GROUPS.find(g => g.test("/" + rel, file));
    buckets.get(g.key).push(node(rel, contexts, loose));
  }
  return GROUPS
    .filter(g => buckets.get(g.key).length)
    .map(g => ({ t: g.label, g: 1, c: buckets.get(g.key) }));
}

const tree = [];

/* --- Home ---------------------------------------------------- */
if (info.has("index.html")) {
  tree.push({ t: "Home", h: "index.html" });
  used.add("index.html");
}

/* --- Year levels --------------------------------------------- */
const yearDirs = fs.readdirSync(ROOT, { withFileTypes: true })
  .filter(e => e.isDirectory() && /^year\d+-/.test(e.name) && !SKIP_TOP.has(e.name))
  .map(e => e.name);

const byYear = new Map();
for (const d of yearDirs) {
  const [, yr, subj] = d.match(/^year(\d+)-(.+)$/);
  if (!byYear.has(yr)) byYear.set(yr, []);
  byYear.get(yr).push({ dir: d, subj });
}

for (const yr of [...byYear.keys()].sort((a, b) => a - b)) {
  const yearNode = { t: "Year " + yr, s: YEAR_BANDS[yr] || "", c: [] };

  for (const { dir, subj } of byYear.get(yr).sort((a, b) => natcmp(a.subj, b.subj))) {
    const subjIndex = dir + "/index.html";
    const subjLabel = SUBJECT_LABELS[subj] ||
      (info.has(subjIndex) ? label(subjIndex, ["Class Materials", "Year " + yr]) : subj);
    const contexts = [subjLabel, "Class Materials", "Year " + yr,
                      "Year " + yr + " " + subjLabel, subjLabel + " " + yr];
    /* Words that, if they turn up in a trailing segment, mean that whole
       segment is context rather than title. */
    const loose = [subjLabel, "Class Materials"];

    const subjNode = { t: subjLabel, c: [] };
    if (info.has(subjIndex)) {
      subjNode.h = subjIndex;
      const th = info.get(subjIndex).theme;
      if (th) subjNode.k = th;
      used.add(subjIndex);
    }

    /* Units = subfolders that carry their own index.html. */
    const unitDirs = [...new Set(
      all.filter(r => r.startsWith(dir + "/") && r.endsWith("/index.html"))
         .map(r => r.slice(0, r.lastIndexOf("/")))
         .filter(d => d !== dir)
    )].sort(natcmp);

    for (const ud of unitDirs) {
      const uIndex = ud + "/index.html";
      const uLabel = UNIT_OVERRIDES[ud] ||
        stripContext(info.get(uIndex).title, [...contexts, "Course Home", "Course Hub"]);
      const uTheme = info.get(uIndex).theme;
      const uContexts = [...contexts, uLabel, "Course Home", "Course Hub"];

      const unitNode = { t: uLabel, h: uIndex, u: 1, c: [] };
      if (uTheme) unitNode.k = uTheme;
      used.add(uIndex);
      unitNode.c = groupFiles(ud, childrenOf(ud), uContexts, loose);
      subjNode.c.push(unitNode);
    }

    /* Loose pages sitting directly in the subject folder. */
    const looseFiles = all.filter(r =>
      r.startsWith(dir + "/") && !used.has(r) &&
      r.slice(dir.length + 1).indexOf("/") === -1);
    for (const rel of looseFiles.sort(natcmp)) subjNode.c.push(node(rel, contexts, loose));

    yearNode.c.push(subjNode);
  }
  tree.push(yearNode);
}

/* --- Reference & tools --------------------------------------- */
const refNode = { t: "Reference & tools", s: "Style guide, staff utilities", c: [] };

const styleguide = all.filter(r => r.startsWith("styleguide/") && !used.has(r));
if (styleguide.length) {
  refNode.c.push({ t: "Style guide", c: styleguide.sort(natcmp).map(r => node(r, ["Class Materials"])) });
}
const toolPages = all.filter(r => r.startsWith("tools/") && !used.has(r));
if (toolPages.length) {
  refNode.c.push({ t: "Staff tools", c: toolPages.sort(natcmp).map(r => node(r, ["Class Materials"])) });
}

/* Standalone question booklets — PDFs belonging to no unit, linked from
   nowhere else on the site. */
const pdfDir = path.join(ROOT, "pdfs");
if (fs.existsSync(pdfDir)) {
  const pdfs = fs.readdirSync(pdfDir).filter(f => f.toLowerCase().endsWith(".pdf")).sort(natcmp);
  if (pdfs.length) {
    refNode.c.push({
      t: "Question booklets",
      c: pdfs.map(f => ({
        t: f.replace(/\.pdf$/i, "").replace(/[_-]+/g, " ").replace(/\s*Question Booklet$/i, ""),
        h: "pdfs/" + f, p: 1,
      })),
    });
  }
}
if (refNode.c.length) tree.push(refNode);

/* --- Anything the rules missed ------------------------------- */
const orphans = all.filter(r => !used.has(r));
if (orphans.length) {
  tree.push({ t: "Other pages", c: orphans.sort(natcmp).map(r => node(r, ["Class Materials"])) });
}

/* ---------- Emit --------------------------------------------- */

function count(nodes) {
  return nodes.reduce((n, x) => n + (x.h ? 1 : 0) + (x.c ? count(x.c) : 0), 0);
}

const out =
`/* ============================================================
   sitemap.js — GENERATED FILE, DO NOT EDIT BY HAND
   Regenerate with:  node tools/build-sitemap.js
   Consumed by assets/js/sitenav.js (the site-wide nav drawer).

   Node keys are short because this ships to every page:
     t = title   h = href (from repo root)   c = children
     s = subtitle   k = theme   u = unit      g = group heading
     x = opaque page (third-party export, no nav injected)
     p = PDF
   ============================================================ */
window.SITEMAP = ${JSON.stringify({ generated: new Date().toISOString().slice(0, 10), tree }, null, 1)};
`;

fs.mkdirSync(path.dirname(OUT), { recursive: true });
fs.writeFileSync(OUT, out, "utf8");

console.log("Wrote " + path.relative(ROOT, OUT));
console.log("  " + count(tree) + " links across " + tree.length + " top-level sections");
if (orphans.length) console.log("  " + orphans.length + " page(s) fell through to 'Other pages': " + orphans.join(", "));
