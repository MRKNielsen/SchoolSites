/* Tests for tools/rubric-builder.html — run with the other rubric tests:

     node tools/test-rubric-builder.js

   1. Round trip: opening an existing rubric and exporting it gives back the
      same rubric, byte for byte as JSON (Space, the starter). Anything the
      builder has no form for must survive untouched.
   2. A rubric built from nothing through the form — typing, the booklet
      paste, tagging — passes the marker's own validateRubric() and boots
      the marker with no problems.
   3. The booklet paste reads the formats booklets actually print.
   4. Problems are named the way a teacher thinks (strand number and name,
      question number), not by internal id.
   5. Typing never rebuilds the box being typed in.
   6. The curriculum picker links codes, offers the achievement standard as
      snippets, and puts VCAA's CC BY-NC line on the exported rubric.
   7. The real curriculum data, when present: unique well-formed codes,
      every level has an achievement standard.

   Needs jsdom (outside the repo root — see CLAUDE.md "Rubric marker"). */

const fs = require('fs');
const path = require('path');
let JSDOM, ResourceLoader, VirtualConsole;
try { ({ JSDOM, ResourceLoader, VirtualConsole } = require('jsdom')); }
catch (e) { console.error('This harness needs jsdom:  npm install jsdom'); process.exit(2); }

const ROOT = path.join(__dirname, '..');
const ORIGIN = 'https://site.test/SchoolSites/';
const SPACE_JS = fs.readFileSync(path.join(ROOT, 'year7-science/space/rubric-data.js'), 'utf8');
const SPACE = JSON.parse(SPACE_JS.slice(SPACE_JS.indexOf('window.RUBRIC =') + 15).trim().replace(/;\s*$/, ''));
const STARTER = JSON.parse(fs.readFileSync(path.join(ROOT, 'tools/rubric-starter.json'), 'utf8'));
const VC_FILE = path.join(ROOT, 'assets/js/vc2-curriculum.js');

/* the site served from disk; a missing file (no curriculum yet) is a 404,
   which the page must survive */
class DiskLoader extends ResourceLoader {
  fetch(url) {
    if (!url.startsWith(ORIGIN)) return null;
    const file = path.join(ROOT, decodeURIComponent(url.slice(ORIGIN.length).split(/[?#]/)[0]));
    if (/vc2-curriculum\.js$/.test(file) && this.noCurriculum) return Promise.resolve(Buffer.from('/* withheld by the test */'));
    return fs.existsSync(file) ? Promise.resolve(fs.readFileSync(file)) : Promise.reject(new Error('404 ' + url));
  }
}
const sleep = ms => new Promise(r => setTimeout(r, ms));
let fail = 0;
const ok = (c, m) => { console.log((c ? '  OK   ' : '  FAIL ') + m); if (!c) fail++; };
const same = (a, b) => JSON.stringify(a) === JSON.stringify(b);

async function open({ storage = {}, vc = null, noCurriculum = false } = {}) {
  const html = fs.readFileSync(path.join(ROOT, 'tools/rubric-builder.html'), 'utf8')
    .replace(/<script src="[^"]*sitenav\.js"[^>]*><\/script>/, '').replace(/<link [^>]*>/g, '');
  const loader = new DiskLoader(); loader.noCurriculum = noCurriculum || !!vc;
  /* downloads click a blob: link, which jsdom reports as unimplemented navigation */
  const vcons = new VirtualConsole();
  vcons.on('jsdomError', e => { if (!/navigation/.test(e.message)) console.error(e.message); });
  const dom = new JSDOM(html, { runScripts: 'dangerously', resources: loader, pretendToBeVisual: true, virtualConsole: vcons,
    url: ORIGIN + 'tools/rubric-builder.html',
    beforeParse(w) {
      w.scrollTo = () => {}; w.open = () => ({});   /* jsdom: no navigation, no scrollIntoView */
      w.Element.prototype.scrollIntoView = () => {};
      Object.keys(storage).forEach(k => w.localStorage.setItem(k, storage[k]));
      if (vc) w.VC2 = vc;
      w.navigator.clipboard = { writeText: async () => {} };
    } });
  const w = dom.window;
  const errs = []; w.addEventListener('error', e => errs.push(e.message));
  await sleep(500);
  if (vc) w.VC2 = vc;
  return { w, errs, B: w.rubricBuilder, $: s => w.document.querySelector(s), $$: s => [...w.document.querySelectorAll(s)] };
}
function type(w, el, value) { el.value = value; el.dispatchEvent(new w.Event('input', { bubbles: true })); }
function choose(w, el, value) { el.value = value; el.dispatchEvent(new w.Event('input', { bubbles: true })); el.dispatchEvent(new w.Event('change', { bubbles: true })); }
const click = (w, el) => el.dispatchEvent(new w.MouseEvent('click', { bubbles: true }));

(async () => {
  console.log('\n=== first visit ===');
  {
    const { w, errs, B, $ } = await open({ noCurriculum: true });
    ok(errs.length === 0, errs.length ? 'errors: ' + errs.join(' | ') : 'boots clean, even with no curriculum data');
    ok(B && B.doc && B.doc.format === 'rubric-marker/1' && B.doc.strands.length === 1, 'starts a blank rubric with one strand');
    ok(/Year 7 Space/.test($('#bNotice').textContent), 'offers to start from a rubric on the site');
    ok(typeof w.validateRubric === 'function' && !w.document.querySelector('#rubric-app'), 'loads the marker\'s validateRubric without booting a marker');
  }

  console.log('\n=== round trip: open, export, nothing lost ===');
  {
    const { B } = await open({ noCurriculum: true });
    B.adopt(SPACE);
    const out = B.exportRubric();
    ok(same(out, SPACE), 'Space rubric exports identical (migrations, demo, storageKey, weights all kept)');
    if (!same(out, SPACE)) {
      const a = JSON.stringify(out, null, 1).split('\n'), b = JSON.stringify(SPACE, null, 1).split('\n');
      for (let i = 0; i < Math.max(a.length, b.length); i++) if (a[i] !== b[i]) { console.log('        first difference: ' + b[i] + '  ->  ' + a[i]); break; }
    }
    ok(B.check().errors.length === 0, 'and the builder reports it ready');
    B.adopt(STARTER);
    ok(same(B.exportRubric(), STARTER), 'starter rubric exports identical (including its _about note)');
  }

  console.log('\n=== build a rubric from nothing, through the form ===');
  {
    const { w, B, $, $$, errs } = await open({ noCurriculum: true });
    type(w, $('[data-f="title"]'), 'Forces Test');
    type(w, $('[data-f="noun.task"]'), 'test');
    ok(B.doc.title === 'Forces Test', 'typing the title sets it');
    /* strand 1 */
    click(w, $('[data-tab="strands"]'));
    const nameBox = $('[data-f="strands.0.name"]');
    type(w, nameBox, 'Describes balanced and unbalanced forces');
    ok($('[data-f="strands.0.name"]') === nameBox, 'typing does not rebuild the box being typed in');
    choose(w, $('[data-f="strands.0.maxBand"]'), '2');
    ok(B.doc.strands[0].maxBand === 2 && $$('.bband').length === 2, 'lowering the top band to 2 shows two band panels');
    for (let b = 0; b < 2; b++) {
      type(w, $(`[data-f="strands.0.bands.${b}.d"]`), 'Descriptor ' + (b + 1) + '.');
      type(w, $(`[data-f="strands.0.can.${b}"]`), 'do thing ' + (b + 1));
      type(w, $(`[data-f="strands.0.next.${b}"]`), 'practise thing ' + (b + 1));
    }
    type(w, $('[data-f="strands.0.start"]'), 'name the forces on an object');
    /* strand 2, from the button */
    click(w, w.document.querySelector('[data-act="s-add"]'));
    ok(B.doc.strands.length === 2 && B.doc.strands[1].id === 's2', 'Add a strand gives a second strand (s2)');
    type(w, $('[data-f="strands.1.name"]'), 'Uses a lever to balance a load');
    choose(w, $('[data-f="strands.1.maxBand"]'), '1');
    type(w, $('[data-f="strands.1.bands.0.d"]'), 'Balances the lever.');
    type(w, $('[data-f="strands.1.can.0"]'), 'balance a lever');
    type(w, $('[data-f="strands.1.next.0"]'), 'predict the balance point');
    type(w, $('[data-f="strands.1.start"]'), 'find the fulcrum');
    /* questions from a booklet paste */
    click(w, $('[data-tab="questions"]'));
    click(w, $('[data-act="paste"]'));
    type(w, $('#bPasteText'), 'Q1.1 (1 mark)\n   Q1.2 (2 marks)  \nQ1.3 (1 mark)\nnoise line\nQ1.2 (2 marks)');
    ok($('#bPasteN').textContent === '3', 'paste recognises 3 questions (the repeat is dropped)');
    click(w, $('[data-act="paste-add"]'));
    ok(B.doc.criteria.length === 3 && B.doc.criteria.map(c => c.q + '/' + c.max).join(' ') === 'Q1.1/1 Q1.2/2 Q1.3/1', 'and adds them with their marks');
    let r = B.check();
    ok(r.errors.length > 0, 'untagged, the rubric is not ready (' + r.errors.length + ' problems)');
    ok(r.errors.some(e => /Strand 1 \(“Describes balanced/.test(e) && /no question for band 1/.test(e)),
       'a missing band is named by strand number and name: "' + (r.errors.find(e => /no question for band/.test(e)) || '').slice(0, 80) + '…"');
    const tag = (i, strand, band) => {
      choose(w, $(`[data-f="criteria.${i}.strand"]`), strand);
      if (band) choose(w, $(`[data-f="criteria.${i}.band"]`), String(band));
    };
    tag(0, 's1', 1); tag(1, 's1', 2); tag(2, 's2', 1);
    ok($$('[data-f="criteria.0.band"] option').length === 2, 'a question on strand 1 offers bands 1–2 only');
    r = B.check();
    ok(r.errors.length === 0, 'tagged, the rubric is ready' + (r.errors.length ? ': ' + r.errors.join(' | ') : ''));
    const out = r.d;
    ok(out.id === 'forces-test' && out.criteria.map(c => c.id).join() === 'Q1_1,Q1_2,Q1_3',
       'ids made from the title and the question numbers: ' + out.id + ' / ' + out.criteria.map(c => c.id).join(','));
    ok(out.strands[0].bands.map(b => b.q).join('|') === 'Q1.1|Q1.2', 'blank evidence labels are filled from the tagged questions');
    ok(out.strands[0].bands.length === 2 && out.strands[0].can.length === 2, 'band arrays trimmed to the strand\'s top band');
    ok(!out.criteria.some(c => '_new' in c), 'no builder scratch fields in the file');
    ok(/Q1\.1/.test($('#bCov').textContent) && !/missing/.test($('#bCov').textContent), 'evidence grid shows every band covered');
    /* lowering a ceiling clamps tagged questions */
    click(w, $('[data-tab="strands"]'));
    choose(w, $('[data-f="strands.0.maxBand"]'), '1');
    ok(B.doc.criteria[1].band === 1, 'lowering a strand\'s top band moves its band-2 question down to band 1');
    choose(w, $('[data-f="strands.0.maxBand"]'), '2');
    click(w, $('[data-tab="questions"]'));
    choose(w, $('[data-f="criteria.1.band"]'), '2');
    /* hand it to the marker */
    const final = B.check().d;
    const ENGINE = fs.readFileSync(path.join(ROOT, 'assets/js/rubric.js'), 'utf8');
    const m = new JSDOM('<body class="rubric-page"><div id="rubric-app"></div><script>window.RUBRIC=' + JSON.stringify(final) + '</script><script>' + ENGINE + '</script>',
      { runScripts: 'dangerously', pretendToBeVisual: true, url: 'https://e.test/m.html' });
    m.window.scrollTo = () => {}; await sleep(200);
    ok(m.window.document.querySelector('#markTable') && !m.window.document.querySelector('.rb-problems'), 'the marker boots on the built rubric');
    ok(/Across this test/.test(m.window.eval('state.students[0].comment')), 'and writes comments with its nouns');
    /* "Open in marker" hands it over through the marker's last-rubric slot */
    click(w, $('[data-act="marker"]'));
    ok(JSON.parse(w.localStorage.getItem('rubric-marker:last')).id === 'forces-test', '"Open in marker" leaves it where the marker looks first');
    /* the draft autosaves */
    await sleep(500);
    ok(JSON.parse(w.localStorage.getItem('rubric-builder:draft')).title === 'Forces Test', 'the draft autosaves in this browser');
    /* rubric-data.js wrapper parses back */
    let js = ''; w.eval('URL.createObjectURL = b => { window.__blob = b; return "blob:x"; }; URL.revokeObjectURL = () => {};');
    click(w, $('[data-tab="check"]')); click(w, $('[data-act="dl-js"]'));
    js = await new Promise(res => { const fr = new w.FileReader(); fr.onload = () => res(fr.result); fr.readAsText(w.__blob); });
    ok(same(JSON.parse(js.slice(js.indexOf('window.RUBRIC =') + 15).trim().replace(/;\s*$/, '')), final), 'Download for the site gives a rubric-data.js that parses back to the same rubric');
    ok(errs.length === 0, errs.length ? 'errors: ' + errs.join(' | ') : 'no script errors along the way');
  }

  console.log('\n=== the draft comes back, and editing keeps existing ids ===');
  {
    const { w, B, $ } = await open({ noCurriculum: true, storage: { 'rubric-builder:draft': JSON.stringify(SPACE) } });
    ok(B.doc.title === 'Astronomy Test' && /draft saved in this browser/.test($('#bNotice').textContent), 'a saved draft reopens');
    click(w, $('[data-tab="questions"]'));
    type(w, $('[data-f="criteria.0.q"]'), 'Q12');
    type(w, $('[data-f="criteria.0.max"]'), '2');
    const out = B.check();
    ok(out.d.criteria[0].id === 'Q1a', 'renumbering a question keeps its id (saved classes are keyed on it)');
    ok(out.d.strands[0].weight === 10, 'a strand\'s weight follows its marks (9 -> 10) instead of failing validation');
    ok(out.errors.length === 1 && /total is 50 but the questions add up to 51/.test(out.errors[0]),
       '...while the paper total still catches the extra mark: "' + (out.errors[0] || 'no error') + '"');
  }

  console.log('\n=== "Edit in builder" from the marker ===');
  {
    const { w, B, $ } = await open({ noCurriculum: true, storage: {
      'rubric-builder:draft': JSON.stringify(STARTER), 'rubric-builder:incoming': JSON.stringify(SPACE) } });
    ok(B.doc.id === 'y7-space-cat5' && /from the marker/.test($('#bNotice').textContent), 'a rubric handed over by the marker opens');
    ok(!w.localStorage.getItem('rubric-builder:incoming'), 'the hand-over is used once');
    click(w, $('[data-act="restore-prev"]'));
    ok(B.doc.id === 'starter-investigation', 'and the draft it replaced is one click away');
  }

  console.log('\n=== booklet paste formats ===');
  {
    const { B } = await open({ noCurriculum: true });
    const p = t => B.parseBooklet(t).map(r => r.q + (r.sub ? '(' + r.sub + ')' : '') + '/' + r.max).join(' ');
    ok(p('Q3.2 (2 marks)  Q3.3 (1 mark)') === 'Q3.2/2 Q3.3/1', 'pdftotext form: Q3.2 (2 marks)');
    ok(p('Question 4b [3 marks]') === 'Q4(b)/3', 'Question 4b [3 marks]');
    ok(p('5(a) (1 mark)\n5(b) (2 marks)') === 'Q5(a)/1 Q5(b)/2', '5(a) (1 mark)');
    ok(p('Q7 (ii) (1.5 marks)') === 'Q7(ii)/1.5', 'roman sub-parts and half marks');
    ok(p('Total (50 marks) page 3') === '', 'a total line is not a question');
    ok(p('see Q2 for details') === '', 'a mention without marks is not a question');
  }

  console.log('\n=== escaping ===');
  {
    const bad = '<img src=x onerror=alert(1)>';
    const r = JSON.parse(JSON.stringify(STARTER));
    r.title = bad; r.parts[0].name = bad; r.strands[0].name = bad; r.criteria[0].label = bad; r.criteria[0].q = bad; r.strands[0].code = bad;
    const { w, B } = await open({ noCurriculum: true });
    B.adopt(r);
    for (const t of ['task', 'strands', 'questions', 'check']) B.showTab(t);
    await sleep(200);
    ok(w.document.querySelectorAll('img').length === 0, 'markup in a rubric file stays text on every tab');
  }

  console.log('\n=== curriculum picker (fixture) ===');
  {
    const VC = { attribution: 'fixture © VCAA, CC BY-NC', subjects: [{ id: 'science', name: 'Science', levels: [
      { level: '7–8', achievement: 'By the end of Level 8, students explain how forces act. They describe models. They plan investigations.',
        strands: [{ name: 'Science understanding', substrands: [{ name: 'Physical sciences', cds: [
          { code: 'VC2S8U07', text: 'investigate the effects of forces on objects' },
          { code: 'VC2S8U08', text: 'describe energy transfers' }] }] }] }] }] };
    const { w, B, $, $$ } = await open({ vc: VC });
    click(w, $('[data-tab="strands"]'));
    click(w, $('[data-act="pick"][data-i="new"]'));
    ok(!$('#bPick').hidden && $$('.bpick-row').length === 2, 'Add from the curriculum lists the content descriptions');
    type(w, $('#pkQ'), 'forces');
    ok($$('.bpick-row').length === 1, 'search narrows to the match');
    click(w, $('.bpick-row [data-pick]'));
    ok(B.doc.strands.length === 2 && B.doc.strands[1].code === 'VC2S8U07', 'picking makes a new strand linked to VC2S8U07');
    ok(/investigate the effects of forces/.test($('.bstrand[data-strand="1"] .bcur').textContent), 'the strand shows the content description');
    const snips = $$('.bstrand[data-strand="1"] .bladder .bcol.at .chipbtn');
    ok(snips.length === 3, 'the level\'s achievement standard is offered a sentence at a time under At (' + snips.length + ')');
    ok(/No lower level/.test($('.bstrand[data-strand="1"] .bcol.towards').textContent)
       && /top of the F–10 curriculum/.test($('.bstrand[data-strand="1"] .bcol.above').textContent),
       'with only one level in the data, Towards and Above say why they are empty');
    ok(/^Can explain how forces act/.test(B.doc.strands[1].bands[2].d), 'a strand started from the curriculum arrives with default descriptors');
    const box = $('[data-f="strands.1.bands.2.d"]');
    type(w, box, '');      /* clear the default, then write into it */
    box.dispatchEvent(new w.FocusEvent('focusin', { bubbles: true }));
    click(w, snips[1]);
    ok(B.doc.strands[1].bands[2].d === 'They describe models.', 'clicking a sentence puts it in the last box written in');
    const out = B.exportRubric();
    ok(/© VCAA, licensed CC BY-NC/.test(out.attribution || ''), 'a rubric using VC2 codes carries VCAA\'s attribution line');
  }

  console.log('\n=== curriculum data ===');
  if (!fs.existsSync(VC_FILE)) { console.log('  --   assets/js/vc2-curriculum.js not built yet; skipped'); }
  else {
    const w = new JSDOM('<script>' + fs.readFileSync(VC_FILE, 'utf8') + '</script>', { runScripts: 'dangerously' }).window;
    const V = w.VC2, cds = [];
    V.subjects.forEach(s => s.levels.forEach(l => l.strands.forEach(st => st.substrands.forEach(ss => ss.cds.forEach(c => cds.push(Object.assign({ s: s.id, l: l.level }, c)))))));
    ok(/© VCAA/.test(V.attribution) && /CC BY-NC/.test(V.attribution), 'carries the VCAA attribution');
    ok(cds.length > 100, cds.length + ' content descriptions');
    ok(new Set(cds.map(c => c.code)).size === cds.length, 'codes are unique');
    ok(cds.every(c => /^VC2[A-Z]{1,3}\d{1,2}[A-Z]{1,3}\d{2}$/.test(c.code)), 'every code is well formed (VC2…)' + (cds.find(c => !/^VC2[A-Z]{1,3}\d{1,2}[A-Z]{1,3}\d{2}$/.test(c.code)) ? ' — e.g. ' + cds.find(c => !/^VC2[A-Z]{1,3}\d{1,2}[A-Z]{1,3}\d{2}$/.test(c.code)).code : ''));
    ok(cds.every(c => c.text && c.text.length > 15 && !/\s{2}/.test(c.text)), 'every description has clean text');
    /* VCAA sets no standard for Level 10A ("No achievement standard for Level 10A") */
    ok(V.subjects.every(s => s.levels.every(l => l.level === '10A' ? l.achievement === '' : l.achievement.length > 200)),
       'every level has its achievement standard (10A has none, as in the chart)');
    ok(V.subjects.find(s => s.id === 'mathematics').levels.map(l => l.level).join() === '5,6,7,8,9,10,10A'
       && V.subjects.find(s => s.id === 'science').levels.map(l => l.level).join() === '5–6,7–8,9–10',
       'levels in order: 5 … 10, 10A and 5–6, 7–8, 9–10 (Levels 5–6 are the "towards" standard for 7 and 7–8)');
    /* every sentence tagged, and the tags are real strands / sub-strands of its level */
    const tagsOk = V.subjects.every(s => s.levels.every(l => (l.standard || []).every(x =>
      l.strands.some(st => st.name === x.strand && st.substrands.some(ss => ss.name === x.sub)))));
    ok(tagsOk, 'every achievement-standard sentence is tagged with a strand and sub-strand of its own level');
    ok(V.subjects.every(s => s.levels.every(l => (l.standard || []).map(x => x.text).join(' ').replace(/\s+/g, ' ')
       === l.achievement.replace(/\s+/g, ' '))), 'the tagged sentences are the whole standard, in order, nothing lost');
    /* anchors from reading every Science sentence by hand */
    const tagOf = (lev, start) => { const l = V.subjects.find(s => s.id === 'science').levels.find(x => x.level === lev);
      const x = l.standard.find(y => y.text.startsWith(start)); return x && x.sub; };
    const anchors = [
      ['5–6', 'They identify sources of light', 'Physical sciences'],
      ['5–6', 'They discuss examples that illustrate', 'Use and influence of science'],
      ['7–8', 'They use the particle and kinetic theories', 'Chemical sciences'],
      ['7–8', 'They distinguish between renewable and non-renewable', 'Earth and space sciences'],
      ['7–8', 'They represent and explain the effects of forces', 'Physical sciences'],
      ['7–8', 'They identify assumptions and sources of error', 'Evaluating'],
      ['9–10', 'They predict the products of reactions', 'Chemical sciences'],
      ['9–10', 'They describe trends in patterns of global climate change', 'Earth and space sciences'],
      ['9–10', 'They use Newton’s laws', 'Physical sciences'],
    ];
    ok(anchors.every(([l, t, sub]) => tagOf(l, t) === sub),
       'hand-checked sentences carry the right sub-strand (' + anchors.filter(([l, t, sub]) => tagOf(l, t) !== sub).map(a => a[0] + ' ' + a[1]).join('; ') + ')');
    const pi = cds.find(c => c.code === 'VC2M7M03'), trig = cds.find(c => c.code === 'VC2M10ASP03');
    ok(pi && /between π and the circumference/.test(pi.text), 'equations survive: "between π and the circumference"');
    ok(trig && /y=sin\(x\), y=cos\(x\) and y=tan\(x\)/.test(trig.text), '...and "y=sin(x), y=cos(x) and y=tan(x)" (brackets from the equation delimiter)');
  }

  console.log('\n=== default statements, real data ===');
  if (fs.existsSync(VC_FILE)) {
    const { w, B, $ } = await open();
    B.doc = { format: 'rubric-marker/1', id: 'd', title: 'D', bands: ['Towards', 'At', 'At', 'Above'], parts: [{ id: 'A', name: 'A' }], strands: [], criteria: [] };
    B.showTab('strands');
    click(w, $('[data-act="pick"][data-i="new"]'));
    choose(w, w.document.querySelector('#pkSub'), 'science');
    type(w, w.document.querySelector('#pkQ'), 'VC2S8U14');
    click(w, w.document.querySelector('.bpick-row [data-pick]'));
    const s = B.doc.strands[0];
    ok(s.code === 'VC2S8U14' && /^Balanced and unbalanced forces/.test(s.name), 'a strand from the picker takes the content description as its draft heading');
    ok(/^Can identify sources of light/.test(s.bands[0].d), 'band 1 (Towards) is drafted from Level 5–6: "' + s.bands[0].d.slice(0, 50) + '…"');
    ok(/^Can demonstrate how simple machines/.test(s.bands[1].d) && /represent and explain the effects of forces/.test(s.bands[1].d), 'band 2 (At) from Level 7–8, every Physical sciences sentence');
    ok(/use Newton’s laws/.test(s.bands[3].d), 'band 4 (Above) from Level 9–10');
    ok(!/They |Students |By the end/.test(s.bands.map(b => b.d).join(' ')), 'VCAA’s “They …” becomes “Can …” — no stray “They” or “By the end of”');
    ok(s.can[1] === 'demonstrate how simple machines can be used for a purpose', '“Ava can now …” takes the base form, lower-case, no full stop');
    ok(s.next[0] === s.can[1] && /\{their\}/.test(s.next[3]), 'a band’s next step is the band above’s “can now”; the top band gets an extension step');
    ok(/^identify sources of light/.test(s.start), 'band 0’s first step comes from the Towards sentences');
    let r = B.check();
    ok(r.warnings.some(x => /Strand 1 still has default wording in 14 boxes \(row heading/.test(x)), 'Check lists boxes still holding defaults: "' + (r.warnings.find(x => /default wording/.test(x)) || '').slice(0, 70) + '…"');
    ok(r.warnings.some(x => /bands 2 and 3 have the same descriptor/.test(x)), 'and says when two At bands share one descriptor');
    type(w, $('[data-f="strands.0.bands.2.d"]'), 'Represents a force diagram and predicts the motion of an object from it.');
    r = B.check();
    ok(!r.warnings.some(x => /same descriptor/.test(x)) && r.warnings.some(x => /default wording in 13 boxes/.test(x)), 'editing band 3 clears that warning and the count drops');
    /* Fill never overwrites */
    type(w, $('[data-f="strands.0.name"]'), 'Explains motion with forces');
    type(w, $('[data-f="strands.0.bands.0.d"]'), '');
    click(w, $('[data-act="defaults"][data-i="0"]'));
    ok(B.doc.strands[0].name === 'Explains motion with forces' && /^Can identify sources of light/.test(B.doc.strands[0].bands[0].d)
       && /^Represents a force diagram/.test(B.doc.strands[0].bands[2].d), 'Fill puts back only the emptied box and leaves typed text alone');
    /* 10A: no standard, its content descriptions stand in */
    B.doc.strands.push({ id: 's2', name: '', code: 'VC2M10AA01', start: '', bands: [1, 2, 3, 4].map(() => ({ q: '', d: '' })), can: ['', '', '', ''], next: ['', '', '', ''] });
    B.render(); click(w, $('[data-act="defaults"][data-i="1"]'));
    const t = B.doc.strands[1];
    ok(/^Can /.test(t.bands[1].d) && t.bands[1].d.length > 30 && /^Can /.test(t.bands[0].d), 'a Level 10A code still gets drafts (At from 10A content descriptions, Towards from Level 10)');
  }

  console.log('\n=== statement bank ===');
  {
    const { w, B, $ } = await open({ noCurriculum: true, storage: { 'rubric-builder:draft': JSON.stringify(STARTER) } });
    B.showTab('strands');
    click(w, $('[data-act="bank"]'));
    ok(!$('#bPick').hidden && /bank is empty/.test($('#bkList').textContent), 'the bank opens, empty at first, saying what it is for');
    $('#bkText').value = 'identify the independent, dependent and controlled variables'; $('#bkTag').value = 'Inquiry';
    click(w, $('[data-bank="add"]'));
    $('#bkText').value = 'communicate findings using scientific vocabulary'; $('#bkTag').value = 'Communicating';
    click(w, $('[data-bank="add"]'));
    const saved = JSON.parse(w.localStorage.getItem('rubric-builder:bank'));
    ok(saved.length === 2 && saved[0].tag === 'Communicating', 'statements are saved in this browser, newest first');
    type(w, $('#bkQ'), 'inquiry');
    ok(w.document.querySelectorAll('#bkList .bpick-row').length === 1, 'search finds by tag');
    click(w, $('[data-bank="close"]'));
    const can = $('[data-f="strands.0.can.1"]');
    type(w, can, '');
    can.dispatchEvent(new w.FocusEvent('focusin', { bubbles: true }));
    click(w, $('[data-act="bank"]'));
    type(w, $('#bkQ'), 'variables');
    click(w, $('[data-bank="use"]'));
    ok(B.doc.strands[0].can[1] === 'identify the independent, dependent and controlled variables', 'Insert puts it in the box last written in');
    click(w, $('[data-act="bank"]'));
    ok(/variables you were last/.test($('#bPick').textContent) === false && $('#bkText').value === 'identify the independent, dependent and controlled variables',
       'opening the bank offers the box you were writing in as a new statement');
    w.eval('URL.createObjectURL = b => { window.__blob = b; return "blob:x"; }; URL.revokeObjectURL = () => {};');
    type(w, $('#bkQ'), '');
    click(w, $('[data-bank="export"]'));
    const exp = JSON.parse(await new Promise(res => { const fr = new w.FileReader(); fr.onload = () => res(fr.result); fr.readAsText(w.__blob); }));
    ok(exp.format === 'rubric-statement-bank/1' && exp.statements.length === 2, 'Export gives a bank file of 2 statements');
    /* import into a fresh browser */
    const { w: w2, $: $2 } = await open({ noCurriculum: true });
    click(w2, $2('[data-act="bank"]'));
    const fi = $2('#bkFile');
    Object.defineProperty(fi, 'files', { value: [new w2.File([JSON.stringify(exp)], 'bank.json')] });
    fi.dispatchEvent(new w2.Event('change'));
    await sleep(200);
    ok(JSON.parse(w2.localStorage.getItem('rubric-builder:bank') || '[]').length === 2, 'Import adds a colleague’s bank');
    fi.dispatchEvent(new w2.Event('change')); await sleep(200);
    ok(JSON.parse(w2.localStorage.getItem('rubric-builder:bank')).length === 2, 'importing the same bank twice adds no duplicates');
    click(w2, $2('[data-bank="del"]'));
    ok(JSON.parse(w2.localStorage.getItem('rubric-builder:bank')).length === 1, 'a statement can be deleted');
  }

  console.log('\n=== Towards / At / Above, real data ===');
  if (fs.existsSync(VC_FILE)) {
    const { w, B, $, $$ } = await open();
    B.doc = { format: 'rubric-marker/1', id: 't', title: 'T', bands: ['Towards', 'At', 'At', 'Above'], parts: [{ id: 'A', name: 'A' }],
      strands: [{ id: 's1', name: 'Forces', code: 'VC2S8U14', start: '', bands: [{ q: '', d: '' }, { q: '', d: '' }, { q: '', d: '' }, { q: '', d: '' }], can: ['', '', '', ''], next: ['', '', '', ''] }],
      criteria: [] };
    B.showTab('strands');
    const col = r => $('.bstrand[data-strand="0"] .bcol.' + r), txt = r => col(r).textContent;
    ok(/Level 5–6/.test(txt('towards')) && /Level 7–8/.test(txt('at')) && /Level 9–10/.test(txt('above')),
       'VC2S8U14 (forces, 7–8): Towards is Level 5–6, At 7–8, Above 9–10');
    ok(/sources of light/.test(txt('towards')) && !/particles/.test(txt('towards')), 'Towards holds Level 5–6 Physical sciences sentences only');
    ok(/effects of forces/.test(txt('at')) && !/plate tectonics/.test(txt('at')), 'At holds Level 7–8 Physical sciences sentences only');
    ok(/Newton’s laws/.test(txt('above')), 'Above holds Level 9–10 Physical sciences (Newton’s laws)');
    ok(/→ band 1/.test(txt('towards')) && /→ band 2/.test(txt('at')) && /→ band 4/.test(txt('above')),
       'with bands Towards / At / At / Above, the columns go to bands 1, 2 and 4');
    click(w, [...col('towards').querySelectorAll('.chipbtn')].find(b => /sources of light/.test(b.textContent)));
    ok(/^They identify sources of light/.test(B.doc.strands[0].bands[0].d), 'clicking a Towards sentence, with no box in use, fills band 1’s descriptor');
    click(w, $('[data-act="std-whole"]'));
    ok(/plate tectonics/.test(txt('at')), 'the toggle shows whole standards');
    click(w, $('[data-act="std-whole"]'));
    /* Mathematics: strand-split standards, and 10A's missing standard */
    B.doc.strands[0].code = 'VC2M10A04'; B.render();
    ok(/Level 9/.test(txt('towards')) && /Level 10\b/.test(txt('at')) && /Level 10A/.test(txt('above')), 'VC2M10A04 (Algebra, Level 10): Towards 9, At 10, Above 10A');
    ok(/no achievement standard for Level 10A/.test(txt('above')) && /polynomial/.test(txt('above')),
       'Above says 10A has no standard and offers its Algebra content descriptions instead');
    ok(!/statistical/.test(txt('at')), 'At holds Level 10 Algebra sentences, not Statistics');
    B.doc.strands[0].code = 'VC2M7N01'; B.render();
    ok(/Level 6/.test(txt('towards')) && $$('.bstrand[data-strand="0"] .bcol.towards .chipbtn').length > 0, 'VC2M7N01: Towards is the Level 6 Number standard');
  }

  console.log('\n' + (fail ? fail + ' CHECK(S) FAILED' : 'ALL CHECKS PASSED'));
  process.exit(fail ? 1 : 0);
})();
