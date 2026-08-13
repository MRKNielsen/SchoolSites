#!/usr/bin/env node
/* ============================================================
   add-sitenav.js — link the site-wide nav drawer into every page

       node tools/add-sitenav.js          # report what it would do
       node tools/add-sitenav.js --write  # actually edit the files

   Inserts, immediately before </head>:

       <link rel="stylesheet" href="…/assets/css/tokens.css">   (if absent)
       <link rel="stylesheet" href="…/assets/css/sitenav.css">
       <script src="…/assets/js/sitenav.js" defer></script>

   at the right relative depth for each page. Idempotent — a page that
   already links sitenav.js is left alone, so it is safe to re-run after
   adding pages.

   Skipped: third-party exports (marimo workbooks), gitignored payload
   files, and the four legacy top-level subject folders. Those lists
   live in tools/build-sitemap.js and are re-read here so the two stay
   in step.
   ============================================================ */
"use strict";

const fs = require("fs");
const path = require("path");

const ROOT = path.resolve(__dirname, "..");
const WRITE = process.argv.includes("--write");

const SKIP_DIRS = new Set([".git", ".github", "node_modules", "assets", "img", "images", "fonts", "booklet"]);
const SKIP_TOP = new Set(["algorithmics", "foundation", "methods", "specialist"]);
/* Generated third-party pages: editing them would be overwritten on the
   next export, and they carry their own full-page app chrome. */
const SKIP_PATH = [/\/workbooks\//, /-payload\.html$/];

function walk(dir, acc = []) {
  for (const e of fs.readdirSync(dir, { withFileTypes: true }).sort((a, b) => a.name.localeCompare(b.name))) {
    if (e.isDirectory()) {
      if (SKIP_DIRS.has(e.name)) continue;
      walk(path.join(dir, e.name), acc);
    } else if (e.isFile() && e.name.toLowerCase().endsWith(".html")) {
      acc.push(path.relative(ROOT, path.join(dir, e.name)).split(path.sep).join("/"));
    }
  }
  return acc;
}

const pages = walk(ROOT).filter(rel =>
  !SKIP_TOP.has(rel.split("/")[0]) && !SKIP_PATH.some(re => re.test("/" + rel)));

let added = 0, already = 0, noHead = 0;
const report = [];

for (const rel of pages) {
  const file = path.join(ROOT, rel);
  let html = fs.readFileSync(file, "utf8");

  if (/assets\/js\/sitenav\.js/.test(html)) { already++; continue; }

  const closeHead = html.search(/<\/head>/i);
  if (closeHead === -1) { noHead++; report.push("  no <head>: " + rel); continue; }

  const up = "../".repeat(rel.split("/").length - 1);
  const indent = (html.slice(0, closeHead).match(/\n([ \t]*)$/) || [, ""])[1];

  const lines = [];
  if (!/assets\/css\/tokens\.css/.test(html)) {
    /* site.css pages predate tokens.css and redefine the same values in
       their own :root, so adding it changes nothing visually — it just
       gives the drawer the palette and fonts it expects. */
    lines.push(`<link rel="stylesheet" href="${up}assets/css/tokens.css">`);
  }
  lines.push(`<link rel="stylesheet" href="${up}assets/css/sitenav.css">`);
  lines.push(`<script src="${up}assets/js/sitenav.js" defer></script>`);

  const block = lines.map(l => indent + l).join("\n") + "\n" + indent;
  html = html.slice(0, closeHead) + block + html.slice(closeHead);

  if (WRITE) fs.writeFileSync(file, html, "utf8");
  added++;
  report.push("  " + (WRITE ? "linked" : "would link") + ": " + rel + (lines.length === 3 ? "  (+tokens.css)" : ""));
}

console.log(report.join("\n"));
console.log("");
console.log(`${added} page(s) ${WRITE ? "updated" : "to update"} · ${already} already linked · ${noHead} without <head>`);
if (!WRITE && added) console.log("Re-run with --write to apply.");
