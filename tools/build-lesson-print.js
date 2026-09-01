#!/usr/bin/env node
/* ============================================================
   build-lesson-print.js — single-lesson print booklets

     node tools/build-lesson-print.js 1
     node tools/build-lesson-print.js 1 3 4      (several at once)
     node tools/build-lesson-print.js --all

   Writes  booklet/Space_Lesson<N>_Print.tex  next to the master, then
   build it the usual way:

     xelatex -interaction=nonstopmode Space_Lesson1_Print.tex   (x3)

   WHY A GENERATOR AND NOT A SECOND .tex
   The obvious way to produce a one-lesson handout is to copy the
   preamble and the section body into a new file. That file then drifts:
   every correction to the master has to be made twice, and nothing
   tells you when it has not been. This script slices the master at
   build time instead, so the booklet .tex stays the single source of
   truth and the master file is never modified.

   HOW IT WORKS
   - Everything up to \begin{document} is the preamble, taken verbatim.
   - The titlepage and table of contents are replaced with a compact
     single-lesson cover; a 6-page handout does not want a contents page.
   - The chosen \section block is copied verbatim, from the decorative
     rule above it to the line before the next \section (or the glossary).
   - \setcounter{section}{N-1} before it, so \question keeps producing the
     SAME numbers as the master — Lesson 3's questions print as Q3.1…,
     not Q1.1…. This is the whole reason the counter is touched, and it
     is why the handout can be marked against the existing answer key.

   The section number is read from the order sections appear in the file,
   which is the same thing LaTeX counts, so the two cannot disagree.
   ============================================================ */

const fs = require('fs');
const path = require('path');

const BOOKLET = path.join(__dirname, '..', 'year7-science', 'space', 'booklet');
const MASTER = path.join(BOOKLET, 'Space_Unit_Booklet_Yr7_8.tex');

const SECTION_RE = /^\\section[[{]/;
const GLOSSARY_MARK = '% UNIT GLOSSARY';

function readMaster() {
  if (!fs.existsSync(MASTER)) {
    console.error('Cannot find the master booklet at ' + MASTER);
    process.exit(1);
  }
  return fs.readFileSync(MASTER, 'utf8').split('\n');
}

/* Pull the title out of \section{Foo} or \section[short]{Foo}, and drop the
   "(above level)" marker the TOC entries carry.
   Each \section also carries a trailing \label{sec:N} (the cover's contents
   table \pageref's it). Strip that first — a greedy match to the last brace
   otherwise swallows the label and leaves a stray "}" in the title. */
function sectionTitle(line) {
  const bare = line.replace(/\\label\{[^}]*\}\s*$/, '');
  const m = bare.match(/^\\section(?:\[[^\]]*\])?\{(.*)\}\s*$/);
  let t = m ? m[1] : bare;
  return t.replace(/\\textnormal\s*\{\(above level\)\}/g, '').trim();
}

function slice(lines) {
  const idx = [];
  lines.forEach((l, i) => { if (SECTION_RE.test(l)) idx.push(i); });
  const glossary = lines.findIndex(l => l.trim() === GLOSSARY_MARK);
  const end = glossary > 0 ? glossary - 1 : lines.length;

  const preambleEnd = lines.findIndex(l => l.trim() === '\\begin{document}');
  if (preambleEnd < 0) { console.error('No \\begin{document} found.'); process.exit(1); }

  const sections = idx.map((start, n) => {
    const stop = n + 1 < idx.length ? idx[n + 1] : end;
    let from = start;
    // take the "% ====" rule above the heading if there is one
    if (from > 0 && /^% ={5,}/.test(lines[from - 1])) from -= 1;
    let body = lines.slice(from, stop);
    while (body.length && (body[body.length - 1].trim() === '' ||
                           body[body.length - 1].trim() === '\\newpage')) body.pop();
    return { number: n + 1, title: sectionTitle(lines[start]), body };
  });

  return { preamble: lines.slice(0, preambleEnd), sections };
}

function cover(sec) {
  return [
    '\\begin{document}',
    '',
    '% Compact single-lesson cover. The master booklet uses a full-bleed',
    '% Navy titlepage; a handful of stapled sheets does not need one, and a',
    '% full-page ink flood is unkind to a school printer.',
    '\\thispagestyle{fancy}',
    '\\begin{center}',
    '  {\\headingfont\\small\\color{Gold}NORTHCOTE HIGH SCHOOL\\ \\textbullet\\ YEAR 7/8 SCIENCE\\ \\textbullet\\ VICTORIAN CURRICULUM 2.0}\\\\[0.5em]',
    '  {\\headingfont\\fontsize{26pt}{30pt}\\selectfont\\bfseries\\color{Space}Space}\\\\[0.35em]',
    '  {\\headingfont\\large\\color{SpaceMid}Lesson ' + sec.number + ' \\textbullet\\ ' + sec.title + '}\\\\[0.7em]',
    '  {\\color{Gold}\\rule{0.5\\linewidth}{1.2pt}}\\\\[0.7em]',
    '  \\begin{minipage}{0.8\\linewidth}\\centering\\small',
    '    \\textcolor{DarkGrey}{This is Section~' + sec.number + ' of the Space unit booklet, printed on its own.',
    '    Question numbers match the full booklet, so answers can be marked against the same key.}',
    '  \\end{minipage}\\\\[1.2em]',
    '  \\begin{minipage}{0.8\\linewidth}',
    '    \\small\\textbf{Name:}\\ \\rule{5cm}{0.4pt}\\hfill\\textbf{Class:}\\ \\rule{3cm}{0.4pt}',
    '  \\end{minipage}',
    '\\end{center}',
    '\\vspace{1.2em}',
    '',
    // \question numbers off \thesection, so the counter has to be set for the
    // handout to agree with the master and with the answer key.
    '\\setcounter{section}{' + (sec.number - 1) + '}',
    ''
  ];
}

function build(n, parsed) {
  const sec = parsed.sections[n - 1];
  if (!sec) {
    console.error('There is no section ' + n + ' — the booklet has ' + parsed.sections.length + '.');
    return false;
  }
  const out = []
    .concat(['% ============================================================',
             '% GENERATED FILE — do not edit.',
             '% Produced by tools/build-lesson-print.js from',
             '% Space_Unit_Booklet_Yr7_8.tex. Edit the master and re-run:',
             '%   node tools/build-lesson-print.js ' + n,
             '% ============================================================'])
    .concat(parsed.preamble)
    .concat(cover(sec))
    .concat(sec.body)
    .concat(['', '\\end{document}', '']);

  const file = path.join(BOOKLET, 'Space_Lesson' + n + '_Print.tex');
  fs.writeFileSync(file, out.join('\n'), 'utf8');
  const questions = sec.body.filter(l => /\\question\{/.test(l)).length;
  const marks = sec.body.reduce((t, l) => {
    const m = l.match(/\\question\{(\d+)\}/); return t + (m ? Number(m[1]) : 0);
  }, 0);
  console.log('  Lesson ' + n + '  ' + sec.title.slice(0, 44).padEnd(46) +
    String(questions).padStart(2) + ' questions · ' + String(marks).padStart(3) +
    ' marks · ' + path.basename(file));
  return true;
}

const parsed = slice(readMaster());
let args = process.argv.slice(2);
if (args.includes('--all')) args = parsed.sections.map(s => String(s.number));
if (!args.length) {
  console.log('Sections in the booklet:');
  parsed.sections.forEach(s => console.log('  %d  %s', s.number, s.title));
  console.log('\nUsage: node tools/build-lesson-print.js <n> [n...]   |   --all');
  process.exit(0);
}
console.log('Writing single-lesson print files:');
let ok = true;
args.forEach(a => { if (!build(Number(a), parsed)) ok = false; });
console.log('\nBuild with:  xelatex -interaction=nonstopmode <file>   (run it three times)');
process.exit(ok ? 0 : 1);
