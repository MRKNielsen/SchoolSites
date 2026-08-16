#!/usr/bin/env node
/* ============================================================
   check-links.js — find broken internal references across the site

       node tools/check-links.js            # check everything
       node tools/check-links.js --all      # include marimo workbook exports

   Walks every .html page and resolves each <a href>, <link href>,
   <script src>, <img src>, <object data>, <source src>, <iframe src>,
   <embed src>, <video/audio src|poster> and SVG <use href> against the
   filesystem. Reports four kinds of problem:

     MISSING   the target does not exist on disk
     CASE      it exists, but with different capitalisation. This is the
               one that matters most: the repo is developed on Windows
               (case-insensitive) and served by GitHub Pages on Linux
               (case-sensitive), so a wrong-case link works locally and
               404s live.
     ABSOLUTE  a root-absolute path. The site is served from
               /SchoolSites/, so /year7-science/… 404s. Always relative.
     IGNORED   the target exists locally but is gitignored, so it is not
               on the published site. Catches links to *-payload.html.

   Exits 1 if anything was found, so it can gate a CI step later.

   Dependency-free by design, like the other tools here.
   ============================================================ */
"use strict";

const fs = require("fs");
const path = require("path");
const { execFileSync } = require("child_process");

const ROOT = path.resolve(__dirname, "..");
const ALL = process.argv.includes("--all");

const SKIP_DIRS = new Set([".git", ".github", "node_modules"]);
/* Third-party exports ship their own asset trees and are regenerated
   wholesale; they are not ours to fix. Same list as add-sitenav.js. */
const SKIP_PATH = ALL ? [] : [/\/workbooks\//];

/* attribute -> which elements it names a file on */
const REFS = [
  [/<a\b[^>]*?\bhref\s*=\s*("[^"]*"|'[^']*'|[^\s>]+)/gi, "a href"],
  [/<link\b[^>]*?\bhref\s*=\s*("[^"]*"|'[^']*'|[^\s>]+)/gi, "link href"],
  [/<(?:script|img|source|iframe|embed|audio|video|track|input)\b[^>]*?\bsrc\s*=\s*("[^"]*"|'[^']*'|[^\s>]+)/gi, "src"],
  [/<object\b[^>]*?\bdata\s*=\s*("[^"]*"|'[^']*'|[^\s>]+)/gi, "object data"],
  [/<(?:video|img)\b[^>]*?\bposter\s*=\s*("[^"]*"|'[^']*'|[^\s>]+)/gi, "poster"],
  [/<use\b[^>]*?\b(?:xlink:)?href\s*=\s*("[^"]*"|'[^']*'|[^\s>]+)/gi, "use href"],
];

const EXTERNAL = /^(?:https?:|mailto:|tel:|data:|javascript:|blob:|#|\/\/)/i;

/* Blank out anything that isn't live markup before matching:

     - comments, because the root index.html deliberately keeps the
       unpublished subject cards commented out and they must not be
       reported as breakage;
     - the *bodies* of <script> and <style> (the opening tags stay, so a
       <script src> is still checked), because JS that builds a download
       link reads as `a.href = url;` and matched as an <a href>.       */
const strip = html => html
  .replace(/<!--[\s\S]*?-->/g, "")
  .replace(/(<script\b[^>]*>)[\s\S]*?<\/script\s*>/gi, "$1</script>")
  .replace(/(<style\b[^>]*>)[\s\S]*?<\/style\s*>/gi, "$1</style>");

/* ---- filesystem helpers ---------------------------------------- */

function walk(dir, acc = []) {
  for (const e of fs.readdirSync(dir, { withFileTypes: true }).sort((a, b) => a.name.localeCompare(b.name))) {
    const abs = path.join(dir, e.name);
    if (e.isDirectory()) {
      if (SKIP_DIRS.has(e.name)) continue;
      walk(abs, acc);
    } else if (e.isFile() && e.name.toLowerCase().endsWith(".html")) {
      acc.push(rel(abs));
    }
  }
  return acc;
}

const rel = abs => path.relative(ROOT, abs).split(path.sep).join("/");

/* Directory listings, cached — used for the case-sensitive check. */
const listings = new Map();
function entries(absDir) {
  if (!listings.has(absDir)) {
    let names = [];
    try { names = fs.readdirSync(absDir); } catch { /* missing dir */ }
    listings.set(absDir, names);
  }
  return listings.get(absDir);
}

/* Resolve target/ -> target/index.html the way a static host would. */
function resolveTarget(absPath) {
  try {
    if (fs.statSync(absPath).isDirectory()) return path.join(absPath, "index.html");
  } catch { /* fall through */ }
  return absPath;
}

/* Walk the path segment by segment, comparing against the real
   directory listing. Returns "ok", "case" or "missing". */
function existsExact(absPath) {
  const parts = rel(absPath).split("/");
  let cur = ROOT;
  for (const part of parts) {
    if (part === "" || part === ".") continue;
    if (part === "..") { cur = path.dirname(cur); continue; }
    const names = entries(cur);
    if (names.includes(part)) { cur = path.join(cur, part); continue; }
    const hit = names.find(n => n.toLowerCase() === part.toLowerCase());
    return hit ? "case" : "missing";
  }
  return "ok";
}

/* ---- gitignore check ------------------------------------------- */

function gitIgnored(paths) {
  if (!paths.length) return new Set();
  try {
    const out = execFileSync("git", ["check-ignore", "--stdin"], {
      cwd: ROOT, input: paths.join("\n"), encoding: "utf8",
      stdio: ["pipe", "pipe", "pipe"],
    });
    return new Set(out.split("\n").filter(Boolean).map(s => s.replace(/\\/g, "/")));
  } catch (e) {
    /* exit 1 just means "nothing matched"; anything else means no git */
    if (e.status === 1) return new Set();
    return new Set();
  }
}

/* ---- main ------------------------------------------------------ */

const pages = walk(ROOT).filter(p => !SKIP_PATH.some(re => re.test("/" + p)));
const problems = [];
const candidates = new Set();   // existing targets, to test against gitignore
const pending = [];             // {page, kind, raw, target}

for (const page of pages) {
  const html = strip(fs.readFileSync(path.join(ROOT, page), "utf8"));

  /* 404.html carries <base href="/SchoolSites/"> because it renders at
     whatever bad URL was requested. Honour a root-absolute <base> by
     resolving that page's relative refs from the repo root. */
  const hasRootBase = /<base\b[^>]*\bhref\s*=\s*["']?\//i.test(html);
  const dir = hasRootBase ? ROOT : path.dirname(path.join(ROOT, page));

  for (const [re, kind] of REFS) {
    re.lastIndex = 0;
    let m;
    while ((m = re.exec(html))) {
      let raw = m[1].trim().replace(/^["']|["']$/g, "").trim();
      if (!raw || EXTERNAL.test(raw)) continue;

      if (raw.startsWith("/")) {
        problems.push({ page, kind, raw, type: "ABSOLUTE",
          note: "root-absolute — the site is served from /SchoolSites/" });
        continue;
      }

      const clean = raw.split("#")[0].split("?")[0];
      if (!clean) continue;

      let decoded;
      try { decoded = decodeURIComponent(clean); } catch { decoded = clean; }

      const abs = resolveTarget(path.resolve(dir, decoded));
      const state = existsExact(abs);

      if (state === "missing") {
        problems.push({ page, kind, raw, type: "MISSING", note: rel(abs) });
      } else if (state === "case") {
        problems.push({ page, kind, raw, type: "CASE",
          note: "wrong capitalisation — works on Windows, 404s on GitHub Pages" });
      } else {
        candidates.add(rel(abs));
        pending.push({ page, kind, raw, target: rel(abs) });
      }
    }
  }
}

const ignored = gitIgnored([...candidates]);
for (const p of pending) {
  if (ignored.has(p.target)) {
    problems.push({ page: p.page, kind: p.kind, raw: p.raw, type: "IGNORED",
      note: p.target + " is gitignored — not on the published site" });
  }
}

/* ---- report ---------------------------------------------------- */

const ORDER = ["MISSING", "CASE", "ABSOLUTE", "IGNORED"];
problems.sort((a, b) =>
  ORDER.indexOf(a.type) - ORDER.indexOf(b.type) ||
  a.page.localeCompare(b.page) || a.raw.localeCompare(b.raw));

let lastPage = null;
for (const p of problems) {
  const head = p.type + " · " + p.page;
  if (head !== lastPage) { console.log("\n" + head); lastPage = head; }
  console.log(`    ${p.kind}="${p.raw}"`);
  if (p.note) console.log(`      ${p.note}`);
}

const counts = ORDER.map(t => [t, problems.filter(p => p.type === t).length])
  .filter(([, n]) => n);

console.log("");
console.log(`${pages.length} page(s) checked · ${pending.length + problems.length} reference(s)`);
if (!problems.length) {
  console.log("No broken references.");
} else {
  console.log(counts.map(([t, n]) => `${n} ${t}`).join(" · "));
  if (!ALL) console.log("(marimo workbook exports skipped — pass --all to include them)");
}
process.exit(problems.length ? 1 : 0);
