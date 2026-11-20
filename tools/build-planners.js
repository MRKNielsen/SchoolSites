#!/usr/bin/env node
/* ============================================================
   build-planners.js — Year 7 unit plans, lesson by lesson

     node tools/build-planners.js                 (every unit, HTML only)
     node tools/build-planners.js forces          (one unit)
     node tools/build-planners.js --docx <dir>    (also write the Word copies into <dir>)

   ONE SOURCE, TWO COPIES
   Each unit's plan lives in  year7-science/<unit>/planner-data.json.
   This script writes the site page  year7-science/<unit>/planner.html
   and, with --docx, the faculty Word copy  <Unit>_Unit_Plan_Yr7.docx
   in the NHS unit-plan layout. Edit the JSON, never the outputs: the
   old planners had a Word twin that was edited by hand and drifted.

   --docx needs the `docx` package resolvable from wherever node runs it
   (it is NOT a dependency of this repo — don't npm install in the root).

   THE LAYOUT (from the Nov 2026 curriculum audit with the HoF)
     Header   unit description; achievement standard | content descriptors;
              prepare · review · DI/IEPs · extension; length; print links.
     Table    one row per lesson:
              Lesson | LIs & success criteria | Explicit instruction |
              Guided and independent learning (inc. practicals, in/excursions) |
              Review / formative assessment + CATs
     Practicals are never optional extras: each carries an inquiry LI and
     an understanding LI (shown in the LI column), its activity sheet,
     a RiskAssess link and the science skill it builds.

   INLINE MARKUP in any string
     **bold**  *italic*  [text](href)  \( maths \)  {{PH:placeholder}}
   Relative hrefs are relative to the unit folder; in Word they become
   absolute links to the GitHub Pages site. {{PH:…}} marks a link or item
   still to be filled in: yellow in Word, a highlighted chip on the site.
   ============================================================ */

const fs = require('fs');
const path = require('path');

const ROOT = path.join(__dirname, '..');
const Y7 = path.join(ROOT, 'year7-science');
const SITE = 'https://mrknielsen.github.io/SchoolSites/year7-science/';
const QUALITY_CRITERIA = '{{PH:faculty quality criteria link}}';

/* ---------- inline markup → runs ---------- */
const TOKEN = /(\*\*[^*]+\*\*|\*[^*]+\*|\[[^\]]+\]\([^)]+\)|\\\(.+?\\\)|\{\{PH:[^}]+\}\})/g;
function runs(str, inherit = {}) {
  const out = [];
  for (const part of String(str).split(TOKEN)) {
    if (!part) continue;
    let m;
    if ((m = part.match(/^\*\*([^*]+)\*\*$/))) out.push(...runs(m[1], { ...inherit, bold: true }));
    else if ((m = part.match(/^\*([^*]+)\*$/))) out.push(...runs(m[1], { ...inherit, italic: true }));
    else if ((m = part.match(/^\[([^\]]+)\]\(([^)]+)\)$/))) out.push(...runs(m[1], { ...inherit, href: m[2] }));
    else if ((m = part.match(/^\\\((.+)\\\)$/))) out.push({ ...inherit, text: m[1], math: true });
    else if ((m = part.match(/^\{\{PH:([^}]+)\}\}$/))) out.push({ ...inherit, text: m[1], ph: true });
    else out.push({ ...inherit, text: part });
  }
  return out;
}
const esc = s => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');

/* TeX → plain text for Word (the site keeps MathJax). */
function texPlain(t) {
  return t.replace(/\\text\{([^}]*)\}/g, '$1').replace(/\\tfrac\{1\}\{2\}/g, '½')
    .replace(/\\times/g, '×').replace(/\\omega/g, 'ω').replace(/\^2/g, '²')
    .replace(/\\,/g, ' ').replace(/\s+/g, ' ').trim();
}

/* ---------- HTML ---------- */
function inlineHtml(str) {
  return runs(str).map(r => {
    let h = r.math ? `\\(${esc(r.text)}\\)` : esc(r.text);
    if (r.ph) return `<span class="ph">${h}</span>`;
    if (r.italic) h = `<em>${h}</em>`;
    if (r.bold) h = `<strong>${h}</strong>`;
    if (r.href) {
      const ext = /^https?:/.test(r.href);
      h = `<a href="${esc(r.href)}"${ext ? ' target="_blank" rel="noopener"' : ''}>${h}</a>`;
    }
    return h;
  }).join('');
}
const ul = items => items && items.length
  ? `<ul class="pl-list">\n${items.map(i => `        <li>${inlineHtml(i)}</li>`).join('\n')}\n      </ul>` : '';
const isAbove = (u, code) => (u.descriptors.find(d => d.code === code) || {}).above || /^VC2S10/.test(code);
const chips = (u, codes) => `<p class="vc-row">${codes.map(c => `<span class="vc${isAbove(u, c) ? ' above' : ''}">${esc(c)}</span>`).join(' ')}</p>`;

function lessonTag(l) {
  if (l.cat) return '<span class="ln-tag cat">CAT</span>';
  if (l.optional) return '<span class="ln-tag opt">Optional</span>';
  if (l.above) return '<span class="ln-tag above">Above level</span>';
  if (l.prac) return '<span class="ln-tag prac">Practical</span>';
  return '';
}

function rowHtml(u, l) {
  const li = [`<p class="lead">${inlineHtml(l.title)}</p>`, ul(l.li)];
  if (l.prac) {
    li.push(`<p class="prac-li"><span class="k">Inquiry</span> ${inlineHtml(l.prac.si)}</p>`);
    li.push(`<p class="prac-li"><span class="k">Understanding</span> ${inlineHtml(l.prac.su)}</p>`);
  }
  li.push(...(l.sc || []).map(s => `<p class="sc">${inlineHtml(s)}</p>`));
  li.push(chips(u, l.codes || []));

  const guided = [];
  if (l.prac) {
    const p = l.prac;
    guided.push(`<div class="prac">
        <p class="prac-h">Practical: ${inlineHtml(p.name)}</p>
        <ul class="pl-list">
          <li><strong>Activity sheet:</strong> ${inlineHtml(p.sheet)}</li>
          <li><strong>RiskAssess:</strong> ${inlineHtml(p.risk)}</li>
          <li><strong>Science skill:</strong> ${inlineHtml(p.skill)} — ${inlineHtml(QUALITY_CRITERIA)}</li>
        </ul>
      </div>`);
  }
  guided.push(ul(l.guided));

  const cls = [l.cat && 'is-cat', l.above && 'is-above', l.optional && 'is-opt'].filter(Boolean).join(' ');
  return `    <tr${cls ? ` class="${cls}"` : ''}>
      <td class="ln"><span class="ln-n">${esc(l.n)}</span>${lessonTag(l)}</td>
      <td>
      ${li.join('\n      ')}
      </td>
      <td>
      ${ul(l.explicit) || '<p class="sc">—</p>'}
      </td>
      <td>
      ${guided.join('\n      ')}
      </td>
      <td>
      ${ul(l.review)}
      </td>
    </tr>`;
}

function pageHtml(u) {
  const mathjax = JSON.stringify(u).includes('\\\\(');
  const cell = (h, items) => `      <div class="pl-grid2-cell">
        <h3>${h}</h3>
        ${ul(items)}
      </div>`;
  return `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<!-- GENERATED by tools/build-planners.js from planner-data.json — edit the JSON, not this file. -->
${mathjax ? `<script>
  window.MathJax = {
    tex: { inlineMath: [['\\\\(', '\\\\)']], displayMath: [['\\\\[', '\\\\]']] },
    svg: { fontCache: 'global' },
    options: { skipHtmlTags: ['script','noscript','style','textarea','pre','code'] }
  };
</script>
<script src="../../assets/vendor/mathjax/tex-svg.js" async></script>
` : ''}<title>Unit Plan &middot; ${esc(u.unit)} | Year 7 Science</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Bitter:wght@500;700;800&family=Source+Sans+3:ital,wght@0,400;0,600;0,700;1,400&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../../assets/css/tokens.css">
<link rel="stylesheet" href="../../assets/css/planner.css">
<link rel="stylesheet" href="../../assets/css/sitenav.css">
<script src="../../assets/js/sitenav.js" defer></script>
<link rel="icon" href="../../assets/icons/favicon.svg" type="image/svg+xml">
<link rel="icon" href="../../assets/icons/favicon.ico" sizes="32x32">
<link rel="apple-touch-icon" href="../../assets/icons/apple-touch-icon.png">
<link rel="manifest" href="../../site.webmanifest">
<meta name="theme-color" content="#${u.accent}">
</head>
<body class="planner-page ${u.theme}">

<div class="pl-bar">
  <a href="./">&#8592; Back to unit</a>
  <button type="button" onclick="window.print()">Print / PDF</button>
  <span class="spacer"></span>
  <span class="hint">Prints A4 landscape &middot; column headings repeat on every page</span>
</div>

<div class="sheet">

  <header class="pl-head">
    <div class="pl-tag">Year 7 Science · Unit plan</div>
    <h1>Unit: ${esc(u.unit)}</h1>
    <p class="pl-meta">${esc(u.length)} · Victorian Curriculum F–10 v2.0</p>
    <p class="pl-desc">${inlineHtml(u.description)}</p>

    <section class="pl-as">
      <div class="pl-as-col">
        <h2>Achievement standard &#183; Levels 7&#8211;8</h2>
        <ul class="pl-list">
${u.achievement.map(a => `          <li><strong>${esc(a.strand)}.</strong> ${inlineHtml(a.text)}</li>`).join('\n')}
        </ul>
      </div>
      <div class="pl-as-col">
        <h2>Content descriptors</h2>
        <dl class="pl-codes pl-codes--stacked">
${u.descriptors.map(d => `          <div><dt><span class="vc${d.above ? ' above' : ''}">${esc(d.code)}</span></dt><dd>${inlineHtml(d.text)}</dd></div>`).join('\n')}
        </dl>
      </div>
    </section>

    <div class="pl-grid2">
${cell('Prepare for learning', u.prepare)}
${cell('Review and reflect', u.review)}
${cell('Modifications for DI and IEPs', u.diff)}
${cell('Extension', u.extension)}
    </div>

    <div class="pl-print">
      <h3>Print the whole thing</h3>
      ${ul(u.print.map(p => `[${p.text}](${p.href})`))}
      <p class="sc">Each lesson row links its own booklet pages for printing one section at a time.</p>
    </div>
    ${ul(u.notes).replace('pl-list', 'pl-list pl-notes')}
  </header>

  <div class="pl-scroll">
  <table class="planner planner--lessons">
    <colgroup>
      <col class="c-ln"><col class="c-lisc"><col class="c-ex"><col class="c-gi"><col class="c-rv">
    </colgroup>
    <thead>
      <tr>
        <th>Lesson</th>
        <th>Learning intentions and success criteria</th>
        <th>Explicit instruction</th>
        <th>Guided and independent learning <span class="th-sub">(inc. practicals, in/excursions)</span></th>
        <th>Review / formative assessment + CATs</th>
      </tr>
    </thead>
    <tbody>
${u.lessons.map(l => rowHtml(u, l)).join('\n')}
    </tbody>
  </table>
  </div>

  <p class="pl-foot">Generated from planner-data.json by tools/build-planners.js — the Word copy comes from the same file. ${esc(u.unit)} &middot; Year 7 Science &middot; Victorian Curriculum 2.0</p>

</div>

</body>
</html>
`;
}

/* ---------- Word ---------- */
async function writeDocx(u, outDir) {
  const D = require('docx');
  const { Document, Packer, Paragraph, TextRun, ExternalHyperlink, Table, TableRow, TableCell,
    WidthType, ShadingType, BorderStyle, PageOrientation, AlignmentType, LevelFormat,
    VerticalAlign, HeadingLevel, Footer, PageNumber } = D;

  const FONT = 'Calibri';
  const ACC = u.accent;
  const abs = h => /^https?:/.test(h) ? h : SITE + u.slug + '/' + h;

  const toRuns = (str, base = {}) => runs(str).map(r => {
    const o = { text: r.math ? texPlain(r.text) : r.text, font: FONT, size: base.size || 18,
      bold: r.bold || base.bold, italics: r.italic || base.italics, color: base.color };
    if (r.ph) return new TextRun({ ...o, text: `[${r.text}]`, bold: true, highlight: 'yellow' });
    if (r.href) return new ExternalHyperlink({ link: abs(r.href), children: [new TextRun({ ...o, style: 'Hyperlink', color: '0563C1', underline: {} })] });
    return new TextRun(o);
  });
  const P = (str, opt = {}) => new Paragraph({ children: toRuns(str, opt), spacing: { after: opt.after ?? 40 }, keepLines: true });
  const B = (str, opt = {}) => new Paragraph({ children: toRuns(str, opt), numbering: { reference: 'dots', level: 0 }, spacing: { after: 30 } });
  const H = (str, size = 20) => new Paragraph({ children: toRuns(str, { bold: true, size, color: ACC }), spacing: { after: 60 }, keepNext: true });

  const border = { style: BorderStyle.SINGLE, size: 4, color: '8A8A8A' };
  const borders = { top: border, bottom: border, left: border, right: border };
  const W = 15398; // A4 landscape, 0.5" margins
  const cell = (children, width, opt = {}) => new TableCell({
    children: children.length ? children : [new Paragraph('')],
    width: { size: width, type: WidthType.DXA }, borders,
    margins: { top: 80, bottom: 80, left: 100, right: 100 },
    shading: opt.fill ? { fill: opt.fill, type: ShadingType.CLEAR, color: 'auto' } : undefined,
    verticalAlign: opt.vAlign, columnSpan: opt.span,
  });
  const table = (widths, rows) => new Table({ width: { size: W, type: WidthType.DXA }, columnWidths: widths, rows });
  const tint = 'EEF3F6';

  const header = [
    new Paragraph({ children: [new TextRun({ text: `Unit – ${u.unit} (Year 7 Science)`, font: FONT, size: 36, bold: true, color: ACC })], heading: HeadingLevel.TITLE, spacing: { after: 60 } }),
    P(`${u.length} · Victorian Curriculum F–10 v2.0 · generated ${new Date().toLocaleDateString('en-AU', { day: 'numeric', month: 'long', year: 'numeric' })}`, { color: '666666', after: 160 }),
    table([W], [new TableRow({ children: [cell([H('Unit description:'), P(u.description)], W, { fill: tint })] })]),
    new Paragraph({ text: '', spacing: { after: 80 } }),
    table([W / 2, W / 2], [new TableRow({ children: [
      cell([H('Sections of achievement standard covered in unit:'), ...u.achievement.map(a => B(`**${a.strand}.** ${a.text}`))], W / 2, { fill: tint }),
      cell([H('Content descriptors covered in unit:'), ...u.descriptors.map(d => B(`${d.text} **${d.code}**${d.above ? ' *(above level)*' : ''}`))], W / 2, { fill: tint }),
    ] })]),
    new Paragraph({ text: '', spacing: { after: 80 } }),
    table([W / 2, W / 2], [
      new TableRow({ children: [
        cell([H('Suggested tasks to prepare students for learning:'), ...u.prepare.map(t => B(t))], W / 2),
        cell([H('Suggested tasks to review and reflect on learning:'), ...u.review.map(t => B(t))], W / 2),
      ] }),
      new TableRow({ children: [
        cell([H('Suggested modifications for DI and students with IEPs:'), ...u.diff.map(t => B(t))], W / 2),
        cell([H('Suggested extension tasks:'), ...u.extension.map(t => B(t))], W / 2),
      ] }),
    ]),
    new Paragraph({ text: '', spacing: { after: 80 } }),
    H('Print the whole thing:'),
    ...u.print.map(p => B(`[${p.text}](${p.href})`)),
    P('*Each lesson row links its own booklet pages so one section can be printed at a time.*', { after: 100 }),
    ...u.notes.map(n => B(n)),
    new Paragraph({ children: [new TextRun({ text: u.length, font: FONT, size: 22, bold: true, highlight: 'yellow' })], spacing: { before: 160, after: 120 } }),
  ];

  const cw = [900, 3900, 2900, 4900, 2798];
  const headCells = ['Lesson', 'Learning Intentions and Success Criteria', 'Explicit instruction',
    'Guided and independent learning (inc. practicals, in/excursions)', 'Review / Formative assessment + CATs']
    .map((t, i) => cell([new Paragraph({ children: [new TextRun({ text: t, font: FONT, size: 18, bold: true, color: 'FFFFFF' })] })], cw[i], { fill: ACC }));

  const rows = [new TableRow({ tableHeader: true, cantSplit: true, children: headCells })];
  for (const l of u.lessons) {
    const tag = l.cat ? 'CAT' : l.optional ? 'Optional' : l.above ? 'Above level' : l.prac ? 'Practical' : '';
    const c0 = [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: l.n, font: FONT, size: 26, bold: true, color: ACC })] })];
    if (tag) c0.push(new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: tag, font: FONT, size: 14, bold: true, color: l.cat ? 'B00020' : '666666' })] }));

    const c1 = [P(`**${l.title}**`), ...(l.li || []).map(t => B(t))];
    if (l.prac) { c1.push(B(`**Inquiry:** ${l.prac.si}`)); c1.push(B(`**Understanding:** ${l.prac.su}`)); }
    c1.push(...(l.sc || []).map(s => P(`*${s}*`, { color: '555555' })));
    if (l.codes && l.codes.length) c1.push(P(l.codes.join(' · '), { size: 14, color: ACC }));

    const c2 = (l.explicit || []).map(t => P(t));
    const c3 = [];
    if (l.prac) {
      const p = l.prac;
      c3.push(P(`**Practical:** ${p.name}`));
      c3.push(B(`**Activity sheet:** ${p.sheet}`));
      c3.push(B(`**RiskAssess:** ${p.risk}`));
      c3.push(B(`**Science skill:** ${p.skill} — ${QUALITY_CRITERIA}`));
    }
    c3.push(...(l.guided || []).map(t => B(t)));
    const c4 = (l.review || []).map(t => P(t));

    rows.push(new TableRow({ cantSplit: true, children: [
      cell(c0, cw[0], { fill: l.cat ? 'FBEAEA' : tint }), cell(c1, cw[1]), cell(c2, cw[2]), cell(c3, cw[3]), cell(c4, cw[4]),
    ] }));
  }

  const doc = new Document({
    creator: 'Year 7 Science', title: `Unit – ${u.unit}`,
    styles: { default: { document: { run: { font: FONT, size: 18 } } },
      paragraphStyles: [{ id: 'Title', name: 'Title', basedOn: 'Normal', run: { font: FONT, size: 36, bold: true }, paragraph: { spacing: { before: 0, after: 60 }, keepNext: true } }] },
    numbering: { config: [{ reference: 'dots', levels: [{ level: 0, format: LevelFormat.BULLET, text: '•', alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 260, hanging: 200 } } } }] }] },
    sections: [{
      properties: { page: { size: { width: 11906, height: 16838, orientation: PageOrientation.LANDSCAPE }, margin: { top: 720, bottom: 720, left: 720, right: 720 } } },
      footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [
        new TextRun({ text: `${u.unit} · Year 7 Science unit plan · page `, font: FONT, size: 14, color: '888888' }),
        new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: 14, color: '888888' }),
      ] })] }) },
      children: [...header, table(cw, rows)],
    }],
  });
  const name = u.unit.replace(/&/g, 'and').replace(/[^A-Za-z0-9]+/g, '_').replace(/^_|_$/g, '');
  const file = path.join(outDir, `${name}_Unit_Plan_Yr7.docx`);
  fs.writeFileSync(file, await Packer.toBuffer(doc));
  return file;
}

/* ---------- main ---------- */
(async () => {
  const args = process.argv.slice(2);
  let docxDir = null;
  const i = args.indexOf('--docx');
  if (i >= 0) { docxDir = path.resolve(args[i + 1]); args.splice(i, 2); }
  const units = args.length ? args : fs.readdirSync(Y7).filter(d => fs.existsSync(path.join(Y7, d, 'planner-data.json')));
  for (const slug of units) {
    const u = JSON.parse(fs.readFileSync(path.join(Y7, slug, 'planner-data.json'), 'utf8'));
    fs.writeFileSync(path.join(Y7, slug, 'planner.html'), pageHtml(u));
    console.log(`wrote year7-science/${slug}/planner.html`);
    if (docxDir) console.log(`wrote ${await writeDocx(u, docxDir)}`);
  }
})().catch(e => { console.error(e); process.exit(1); });
