#!/usr/bin/env node
// check-bookrefs.js — verify booklet chips against the booklet's .aux
//
//   node tools/check-bookrefs.js [unitDir ...]
//
// With no arguments, checks every folder that has booklet/*.aux.
// The .aux is the source of truth: build the booklet first (xelatex ×3).
//
// Checks, in every *.html in the unit folder:
//   <p class="bookref book">Booklet p.N · §1.2 | Task 1.7b | Extension 1.8 | Q2.3 | Worked Example 2.1</p>
//   <a href="booklet/X.pdf#page=N">… Experiment N …</a>
// Each reference must exist as a label (sec:, sub:, task:, q:, exp:, we:) and its
// page must be p.N, or inside pp.N–M. A reference kind the booklet has no
// labels for at all is reported as unchecked, not as an error.
'use strict';
const fs = require('fs'), path = require('path');
const root = path.resolve(__dirname, '..');

function decode(t) {
  return t.replace(/&#(\d+);/g, (_, n) => String.fromCodePoint(+n))
          .replace(/&amp;/g, '&').replace(/&nbsp;/g, ' ').replace(/<[^>]+>/g, '');
}
function readAux(file) {
  const labels = {};
  const re = /\\newlabel\{([^}]+)\}\{\{([^}]*)\}\{(\d+)\}/g;
  let m; const s = fs.readFileSync(file, 'utf8');
  while ((m = re.exec(s))) labels[m[1]] = +m[3];
  return labels;
}
function refsIn(text) {
  const out = [];
  let m;
  const sec = /§\s*(\d+(?:\.\d+)?)(?:\s*[–-]\s*(\d+(?:\.\d+)?))?/g;
  while ((m = sec.exec(text))) for (const r of [m[1], m[2]]) if (r)
    out.push((r.includes('.') ? 'sub:' : 'sec:') + r);
  const pats = [[/\bTask\s+(\d+\.\d+[a-z]?)/g, 'task:'], [/\bExtension\s+(\d+\.\d+)/g, 'task:'],
                [/\bQ\s?(\d+\.\d+)/g, 'q:'], [/\bExperiment\s+(\d+)/g, 'exp:'],
                [/\bWorked Example\s+(\d+\.\d+)/g, 'we:']];
  for (const [re, kind] of pats) while ((m = re.exec(text))) out.push(kind + m[1]);
  return out;
}
function checkUnit(dir) {
  const bdir = path.join(dir, 'booklet');
  const aux = fs.existsSync(bdir) && fs.readdirSync(bdir).filter(f => f.endsWith('.aux') && !/_Lesson\d+_Print/.test(f));
  if (!aux || !aux.length) return { errors: 0, checked: 0, skipped: true };
  const labels = Object.assign({}, ...aux.map(f => readAux(path.join(bdir, f))));
  const kinds = new Set(Object.keys(labels).map(k => k.split(':')[0] + ':'));
  let errors = 0, checked = 0, unchecked = 0;
  const rel = p => path.relative(root, p).split(path.sep).join('/');
  for (const f of fs.readdirSync(dir).filter(f => f.endsWith('.html')).sort()) {
    const html = fs.readFileSync(path.join(dir, f), 'utf8');
    const lines = html.split('\n');
    lines.forEach((line, i) => {
      const items = [];
      let m;
      const chip = /<p class="bookref[^"]*\bbook\b[^"]*"[^>]*>([\s\S]*?)<\/p>/g;
      while ((m = chip.exec(line))) {
        const t = decode(m[1]);
        const pg = /pp?\.\s*(\d+)(?:\s*[–-]\s*(\d+))?/.exec(t);
        items.push({ t, lo: pg && +pg[1], hi: pg && +(pg[2] || pg[1]) });
      }
      const link = /href="booklet\/[^"#]+\.pdf#page=(\d+)"[^>]*>([\s\S]*?)<\/a>/g;
      while ((m = link.exec(line))) items.push({ t: decode(m[2]), lo: +m[1], hi: +m[1] });
      for (const it of items) {
        const where = `${rel(path.join(dir, f))}:${i + 1}`;
        if (it.lo == null) { console.log(`ERROR ${where}  no page in "${it.t}"`); errors++; continue; }
        for (const r of refsIn(it.t)) {
          const kind = r.split(':')[0] + ':';
          if (!(r in labels)) {
            if (kinds.has(kind)) { console.log(`ERROR ${where}  ${r} does not exist  "${it.t}"`); errors++; }
            else unchecked++;
            continue;
          }
          checked++;
          const p = labels[r];
          if (p < it.lo || p > it.hi)
            { console.log(`ERROR ${where}  ${r} is on p.${p}  "${it.t}"`); errors++; }
        }
      }
    });
  }
  console.log(`${rel(dir)}: ${checked} refs checked, ${errors} wrong` + (unchecked ? `, ${unchecked} unchecked (no labels of that kind)` : ''));
  return { errors, checked };
}
let dirs = process.argv.slice(2).map(d => path.resolve(d));
if (!dirs.length) {
  const walk = d => { for (const e of fs.readdirSync(d, { withFileTypes: true })) {
    if (!e.isDirectory() || e.name.startsWith('.') || e.name === 'node_modules') continue;
    const p = path.join(d, e.name);
    if (e.name === 'booklet') dirs.push(d); else walk(p);
  } };
  walk(root);
}
let bad = 0;
for (const d of dirs) bad += checkUnit(d).errors;
process.exit(bad ? 1 : 0);
