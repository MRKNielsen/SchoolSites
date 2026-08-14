#!/usr/bin/env node
/* ============================================================
   add-favicon.js — link the site icon set into every page

       node tools/add-favicon.js          # report what it would do
       node tools/add-favicon.js --write  # actually edit the files

   Inserts, immediately before </head>:

       <link rel="icon" href="…/assets/icons/favicon.svg" type="image/svg+xml">
       <link rel="icon" href="…/assets/icons/favicon.ico" sizes="32x32">
       <link rel="apple-touch-icon" href="…/assets/icons/apple-touch-icon.png">
       <link rel="manifest" href="…/site.webmanifest">
       <meta name="theme-color" content="#24576f">

   at the right relative depth for each page. Idempotent — a page that
   already links favicon.svg is left alone, so it is safe to re-run.

   Order matters: the SVG comes first because browsers take the last
   format they understand, and every modern browser understands SVG.
   The .ico stays for older ones and for Windows pinned tiles.

   Paths are relative, never root-absolute: the site is served from
   /SchoolSites/, so /assets/icons/… would 404.

   Same skip lists as add-sitenav.js — third-party marimo exports,
   gitignored payloads, and the four legacy top-level folders.
   ============================================================ */
"use strict";

const fs = require("fs");
const path = require("path");

const ROOT = path.resolve(__dirname, "..");
const WRITE = process.argv.includes("--write");

const SKIP_DIRS = new Set([".git", ".github", "node_modules", "assets", "img", "images", "fonts", "booklet"]);
const SKIP_TOP = new Set(["algorithmics", "foundation", "methods", "specialist"]);
const SKIP_PATH = [/\/workbooks\//, /-payload\.html$/];

const THEME = "#24576f";   /* keep in step with site.webmanifest + build-icons.js */

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

  if (/assets\/icons\/favicon\.svg/.test(html)) { already++; continue; }

  const closeHead = html.search(/<\/head>/i);
  if (closeHead === -1) { noHead++; report.push("  no <head>: " + rel); continue; }

  const up = "../".repeat(rel.split("/").length - 1);
  const indent = (html.slice(0, closeHead).match(/\n([ \t]*)$/) || [, ""])[1];

  const lines = [
    `<link rel="icon" href="${up}assets/icons/favicon.svg" type="image/svg+xml">`,
    `<link rel="icon" href="${up}assets/icons/favicon.ico" sizes="32x32">`,
    `<link rel="apple-touch-icon" href="${up}assets/icons/apple-touch-icon.png">`,
    `<link rel="manifest" href="${up}site.webmanifest">`
  ];
  /* Don't add a second theme-color if the page already sets one. */
  if (!/name=["']theme-color["']/i.test(html)) {
    lines.push(`<meta name="theme-color" content="${THEME}">`);
  }

  const block = lines.map(l => indent + l).join("\n") + "\n" + indent;
  html = html.slice(0, closeHead) + block + html.slice(closeHead);

  if (WRITE) fs.writeFileSync(file, html, "utf8");
  added++;
  report.push("  " + (WRITE ? "linked" : "would link") + ": " + rel);
}

console.log(report.join("\n"));
console.log("");
console.log(`${added} page(s) ${WRITE ? "updated" : "to update"} · ${already} already linked · ${noHead} without <head>`);
if (!WRITE && added) console.log("Re-run with --write to apply.");
