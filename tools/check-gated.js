#!/usr/bin/env node
/* ============================================================
   check-gated.js — is each gated page's encrypted blob current?

     node tools/check-gated.js        # exits 1 if anything is stale

   THE FAILURE THIS EXISTS TO CATCH
   Gated pages ship their content as an encrypted `var BLOB = {...}`
   line. The plaintext lives beside them as `*-payload.html`, which is
   gitignored and never deployed. So editing the payload changes nothing
   on the site until someone re-encrypts it through tools/staff-crypt.html
   and pastes the new blob in.

   That is a silent failure. In Sep 2026 the Space answer key sat five
   days out of date across two whole-booklet renumberings — the site was
   still serving an 8-section key while the booklet had moved to 10, so
   every answer past §2 was attached to the wrong question number. Nothing
   warned anyone, because the payload was correct and the deployed page
   was syntactically fine.

   Two checks, both cheap:
     1. payload newer than its gated page  -> the blob was not refreshed
     2. payload's question set vs the built booklet PDF, where one exists
   ============================================================ */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const ROOT = path.join(__dirname, '..');
let problems = 0, checked = 0;

function walk(dir, out = []) {
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    if (e.name === '.git' || e.name === 'node_modules') continue;
    const p = path.join(dir, e.name);
    if (e.isDirectory()) walk(p, out);
    else if (e.name.endsWith('-payload.html')) out.push(p);
  }
  return out;
}

/* Questions the booklet actually asks, if there is a built PDF beside it. */
function bookletQuestions(unitDir) {
  const bk = path.join(unitDir, 'booklet');
  if (!fs.existsSync(bk)) return null;
  const pdf = fs.readdirSync(bk).find(f => /Unit_Booklet.*\.pdf$/.test(f));
  if (!pdf) return null;
  try {
    const txt = execSync(`pdftotext -layout ${JSON.stringify(path.join(bk, pdf))} -`,
                         { encoding: 'utf8', maxBuffer: 64 * 1024 * 1024 });
    return new Set((txt.match(/Q\d+\.\d+(?= \(\d+ marks?\))/g) || []));
  } catch { return null; }          // pdftotext not installed — skip quietly
}

for (const payload of walk(ROOT)) {
  const gated = payload.replace(/-payload\.html$/, '.html');
  const rel = path.relative(ROOT, gated);
  if (!fs.existsSync(gated)) { console.log(`  ?  ${rel} — payload has no gated page`); continue; }
  checked++;

  const gatedSrc = fs.readFileSync(gated, 'utf8');
  /* A shell that ships an empty ct locks but can never unlock. Worth its own
     message — it is a different problem from "the blob is out of date". */
  const blob = gatedSrc.match(/var BLOB\s*=\s*\{[^;]*\}/);
  if (blob && /"ct"\s*:\s*""/.test(blob[0])) {
    problems++;
    console.log(`  PLACEHOLDER  ${rel} — ships an empty blob, so the page locks but cannot unlock`);
    console.log(`         encrypt ${path.basename(payload)} through tools/staff-crypt.html.`);
    continue;
  }

  const pM = fs.statSync(payload).mtime, gM = fs.statSync(gated).mtime;
  /* Two minutes of slack: a re-encrypt touches the payload and the page
     moments apart, and a fresh clone gives everything the same checkout
     time. Only a real edit-and-forget shows up as minutes or days. */
  const stale = (pM - gM) > 120000;
  if (stale) {
    problems++;
    console.log(`  STALE  ${rel}`);
    console.log(`         payload edited ${pM.toISOString().slice(0, 16).replace('T', ' ')}, ` +
                `blob last touched ${gM.toISOString().slice(0, 16).replace('T', ' ')}`);
    console.log(`         re-encrypt ${path.basename(payload)} through tools/staff-crypt.html ` +
                `and paste the new "var BLOB" line in.`);
  }

  const bq = bookletQuestions(path.dirname(payload));
  if (bq && bq.size) {
    const src = fs.readFileSync(payload, 'utf8');
    const kq = new Set((src.match(/(?<=qref">)Q\d+\.\d+/g) || []));
    const missing = [...bq].filter(q => !kq.has(q));
    const extra = [...kq].filter(q => !bq.has(q));
    if (missing.length || extra.length) {
      problems++;
      console.log(`  MISMATCH  ${rel} — payload vs built booklet`);
      if (missing.length) console.log(`         in booklet, no answer: ${missing.slice(0, 8).join(', ')}${missing.length > 8 ? ` (+${missing.length - 8})` : ''}`);
      if (extra.length)   console.log(`         answered, not in booklet: ${extra.slice(0, 8).join(', ')}${extra.length > 8 ? ` (+${extra.length - 8})` : ''}`);
    } else if (!stale) {
      console.log(`  ok     ${rel} — ${kq.size} answers match the built booklet`);
    }
  } else if (!stale) {
    console.log(`  ok     ${rel}`);
  }
}

console.log(`\n${checked} gated page(s) checked · ${problems} problem(s)`);
process.exit(problems ? 1 : 0);
