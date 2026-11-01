/* Tests for the shared rubric engine (assets/js/rubric.js) beyond the Space
   page itself — run alongside tools/test-space-rubric.js:

     node tools/test-rubric-marker.js

   1. validateRubric() passes the real rubrics (Space, the starter) and FAILS
      each defect it exists to catch. A check that has never been seen to fail
      is not evidence: the Space rubric once shipped with ~12,600 characters
      missing and a passing check. So every rule is broken on purpose here.
   2. A rubric that fails shows the problems panel, never a half-built marker.
   3. Rubric text is escaped: a rubric file is a document someone emailed, so
      markup in it must not become markup on the page.
   4. Another rubric works end to end: the starter marks, bands and totals.
   5. tools/rubric-marker.html: opens a rubric, saves a class that carries its
      rubric, and a page with a different rubric built in refuses that save.

   Needs jsdom (npm install jsdom — outside the repo root; see ROADMAP.md). */

const fs = require('fs');
const path = require('path');
let JSDOM;
try { ({ JSDOM } = require('jsdom')); }
catch (e) { console.error('This harness needs jsdom:  npm install jsdom'); process.exit(2); }

const ROOT = path.join(__dirname, '..');
const { ResourceLoader } = require('jsdom');
const ORIGIN = 'https://site.test/SchoolSites/';
/* jsdom gives file:// pages no localStorage, so the generic page is served
   from a pretend origin whose files are read straight off the disk */
class DiskLoader extends ResourceLoader {
  fetch(url, opts) {
    if (!url.startsWith(ORIGIN)) return null;
    const file = path.join(ROOT, decodeURIComponent(url.slice(ORIGIN.length).split(/[?#]/)[0]));
    return Promise.resolve(fs.readFileSync(file));
  }
}
const ENGINE = fs.readFileSync(path.join(ROOT, 'assets/js/rubric.js'), 'utf8');
const SPACE_JS = fs.readFileSync(path.join(ROOT, 'year7-science/space/rubric-data.js'), 'utf8');
const SPACE = JSON.parse(SPACE_JS.slice(SPACE_JS.indexOf('window.RUBRIC =') + 15).trim().replace(/;\s*$/, ''));
const STARTER = JSON.parse(fs.readFileSync(path.join(ROOT, 'tools/rubric-starter.json'), 'utf8'));
const clone = o => JSON.parse(JSON.stringify(o));

const sleep = ms => new Promise(r => setTimeout(r, ms));
let fail = 0;
const ok = (c, m) => { console.log((c ? '  OK   ' : '  FAIL ') + m); if (!c) fail++; };

/* a bare page running the engine on a given rubric (and optionally a save) */
async function boot(rubric, extra) {
  const html = '<!DOCTYPE html><html><body class="rubric-page"><div id="rubric-app"></div>'
    + '<script>window.RUBRIC = ' + JSON.stringify(rubric).replace(/</g, '\\u003c') + ';'
    + (extra || '') + '</script><script>' + ENGINE + '</script></body></html>';
  const dom = new JSDOM(html, { runScripts: 'dangerously', pretendToBeVisual: true,
                                url: 'https://example.org/t/' + Math.random().toString(36).slice(2) + '.html' });
  const w = dom.window;
  w.scrollTo = () => {};
  const errs = []; w.addEventListener('error', e => errs.push(e.message));
  await sleep(150);
  return { w, errs, $: s => w.document.querySelector(s) };
}

(async () => {
  console.log('\n=== real rubrics validate clean ===');
  {
    const { w, errs } = await boot(SPACE);
    const chk = JSON.parse(w.eval('JSON.stringify(RUBRIC_CHECK)'));
    ok(chk.errors.length === 0, 'Space rubric: no errors' + (chk.errors.length ? ' — ' + chk.errors.join(' | ') : ''));
    ok(errs.length === 0, 'Space rubric boots without script errors');
    const { w: w2 } = await boot(STARTER);
    const c2 = JSON.parse(w2.eval('JSON.stringify(RUBRIC_CHECK)'));
    ok(c2.errors.length === 0, 'starter rubric: no errors' + (c2.errors.length ? ' — ' + c2.errors.join(' | ') : ''));
  }

  console.log('\n=== every rule fails when broken ===');
  /* [description, how to break the Space rubric, text the error must contain] */
  const breaks = [
    ['wrong format',                 r => { r.format = 'rubric/0'; },                                       'format must be'],
    ['id with markup in it',         r => { r.id = '"><img src=x>'; },                                      'id must be'],
    ['three band labels',            r => { r.bands.pop(); },                                               'exactly four band labels'],
    ['duplicate criterion id',       r => { r.criteria[1].id = r.criteria[0].id; },                         'used twice'],
    ['criterion in a missing part',  r => { r.criteria[0].part = 'Z'; },                                     'is not one of the parts'],
    ['criterion in a missing strand',r => { r.criteria[0].strand = 's9'; },                                  'does not exist'],
    ['band above the strand maxBand',r => { r.criteria.find(c => c.strand === 's5').band = 4; },             "maxBand"],
    ['quarter-mark max',             r => { r.criteria[0].max = 0.25; },                                     'whole or half mark'],
    ['missing can phrase',           r => { r.strands[0].can.length = 3; },                                  'can needs one phrase'],
    ['missing next phrase',          r => { r.strands[0].next.length = 2; },                                 'next needs one phrase'],
    ['empty band descriptor',        r => { r.strands[0].bands[1].d = ''; },                                 'descriptor (d) is empty'],
    ['no start step',                r => { delete r.strands[0].start; },                                    'start'],
    ['an empty band in the ladder',  r => { r.criteria.filter(c => c.strand === 's1' && c.band === 2).forEach(c => c.band = 1); }, 'has no question for band 2'],
    ['weight disagrees with marks',  r => { r.strands[0].weight = 10; },                                     'weight is 10'],
    ['total disagrees with marks',   r => { r.total = 51; },                                                 'total is 51'],
    ['theme that is not a name',     r => { r.theme = 'space" onload="x'; },                                 'theme must be'],
    ['bad columnOrder',              r => { r.columnOrder = 'random'; },                                     'columnOrder'],
    ['pass above 1',                 r => { r.pass = 2; },                                                   'pass must be'],
    ['no criteria',                  r => { r.criteria = []; },                                              'criteria must be a non-empty list'],
  ];
  for (const [what, brk, want] of breaks) {
    const r = clone(SPACE); brk(r);
    const { w } = await boot(r);
    const errs = JSON.parse(w.eval('JSON.stringify(RUBRIC_CHECK.errors)'));
    ok(errs.some(e => e.includes(want)), what + ' -> "' + (errs.find(e => e.includes(want)) || errs[0] || 'no error').slice(0, 90) + '"');
  }
  {
    const r = clone(SPACE); r.strands.forEach(s => delete s.weight); delete r.total;
    const { w } = await boot(r);
    ok(w.eval('RUBRIC_OK') && w.eval('JSON.stringify(STRANDS.map(s => s.weight))') === '[9,12,11,12,3,3]',
       'weight left out is summed from the questions (9,12,11,12,3,3)');
  }

  console.log('\n=== a broken rubric shows its problems, not a marker ===');
  {
    const r = clone(SPACE); r.strands[0].weight = 10;
    const { w, $, errs } = await boot(r);
    ok($('.rb-problems') && /weight is 10/.test($('.rb-problems').textContent), 'problems panel lists the fault');
    ok(!$('#markTable') && !$('.tabbar'), 'no marking grid or tabs are built');
    ok(errs.length === 0, 'and nothing throws');
    const { $: $2 } = await boot(null);
    ok($2('.rb-problems') && /No rubric was loaded/.test($2('.rb-problems').textContent), 'no rubric at all says so');
  }

  console.log('\n=== rubric text is escaped everywhere it is shown ===');
  {
    const r = clone(STARTER);
    const bad = '<img src=x onerror=alert(1)>';
    r.title = 'T' + bad; r.eyebrow = 'E' + bad; r.parts[0].name = 'P' + bad;
    r.strands[0].name = 'S' + bad; r.strands[0].code = 'C' + bad; r.strands[0].bands[0].d = 'D' + bad;
    r.strands[0].bands[0].q = 'Q' + bad; r.strands[0].can[0] = 'can' + bad; r.strands[0].next[0] = 'next' + bad;
    r.strands[0].start = 'start' + bad; r.criteria[0].label = 'L' + bad; r.criteria[0].q = 'Q1' + bad;
    r.noun = { task: 'task' + bad, item: 'item' + bad };
    r.back = { href: 'javascript:alert(1)', label: 'B' + bad };
    const { w, $ } = await boot(r);
    w.eval('renderAll(); ["mark","comments","groups","analysis","print","ref"].forEach(showTab);');
    w.document.getElementById('f-printwhat').value = 'groups'; w.eval('renderPrint()');
    const groupsImgs = w.document.querySelectorAll('#printPane img').length;
    w.document.getElementById('f-printwhat').value = 'rubric'; w.eval('renderPrint()');
    ok(w.document.querySelectorAll('img').length === 0 && groupsImgs === 0, 'no <img> injected on any tab or print view');
    ok(/<img src=x/.test($('#rubric-app').textContent), '...the text is shown literally instead');
    ok(!$('a.unit-back'), 'a javascript: back link is dropped');
  }

  console.log('\n=== another rubric marks end to end (the starter) ===');
  {
    const { w, $ } = await boot(STARTER);
    ok(w.eval('state.students.length') === 6, 'generic demo class of 6');
    ok(w.eval('MAX_TOTAL') === 20 && w.eval('HIST_W') === 2 && w.eval('HIST_N') === 10, 'total 20 -> ten 2-mark histogram bins');
    ok(w.eval('JSON.stringify(MARK_COLS)') === JSON.stringify([...Array(11).keys()]), 'columnOrder "listed" keeps the rubric order');
    ok(w.eval('R.storageKey') === 'rubric-marker:starter-investigation', 'own autosave key, derived from the id');
    $('#f-roll').value = 'Pat Kim, she\nLee Ray';
    w.eval('applyRoll(); CRITERIA.forEach((c,i) => setMark(0, i, c.max)); refreshClass(); regenerate(state.students[0], true); renderAll();');
    ok(w.eval('JSON.stringify(STRANDS.map(s => state.students[0].marks[s.id]))') === '[4,4,3]', 'full marks -> top band on each strand (4,4,3)');
    ok(/20 \/ 20 marks/.test($('#p-print').textContent), 'print shows 20 / 20');
    const cmt = w.eval('state.students[0].comment');
    ok(/Across this report Pat/.test(cmt) && !/undefined|\{their\}|NaN|(this|the) test\b/.test(cmt), 'comment uses the rubric\'s nouns ("this report"), clean');
    ok($$count(w, '#markTable th.pgroup') === 3 && w.document.querySelector('#markTable th.pgroup.pC'), 'three part groups, coloured pA..pC by position');
    ok(/Practical Investigation Report/.test($('.masthead').textContent), 'masthead comes from the rubric');
    w.eval('download = (n, t) => { window.__save = t; window.__name = n; }; saveJSON();');
    const save = JSON.parse(w.eval('window.__save'));
    ok(save.rubric && save.rubric.id === 'starter-investigation' && save.rubricId === 'starter-investigation', 'a saved class carries its rubric');
    ok(/^class-starter-investigation-rubric-\d{4}-\d\d-\d\d\.json$/.test(w.eval('window.__name')), 'file named from fileStem: ' + w.eval('window.__name'));
    w.eval('download = (n, t) => { window.__def = t; }; downloadRubric();');
    ok(JSON.stringify(JSON.parse(w.eval('window.__def'))) === JSON.stringify(STARTER), '"Download this rubric" gives back the rubric exactly');
    fs.writeFileSync(path.join(require('os').tmpdir(), 'rubric-test-starter-save.json'), w.eval('window.__save'));
  }

  console.log('\n=== a save from one rubric is refused by another ===');
  {
    const starterSave = fs.readFileSync(path.join(require('os').tmpdir(), 'rubric-test-starter-save.json'), 'utf8');
    const { w } = await boot(SPACE);
    const before = w.eval('state.students.map(s => s.name).join()');
    ok(w.eval('importJSON(' + JSON.stringify(starterSave) + ')') === false, 'Space refuses a class marked on the starter');
    ok(w.eval('state.students.map(s => s.name).join()') === before, '...and keeps its own class untouched');
    ok(w.eval('importJSON(' + JSON.stringify(JSON.stringify(STARTER)) + ')') === false, 'a bare rubric file is not taken for a class');
    /* an old Space save, from before saves carried a rubric, still opens */
    ok(w.eval('importJSON(JSON.stringify({version:2, meta:{cls:"7X"}, students:[{name:"Old Save", pron:"he", q:{Q1a:1}}]}))') === true
       && w.eval('state.students[0].name') === 'Old Save', 'an old Space save (no rubric inside) still opens on the Space page');
    /* its own save round-trips */
    w.eval('download = (n, t) => { window.__s = t; }; saveJSON();');
    ok(w.eval('importJSON(window.__s)') === true, 'Space opens its own new-format save');
  }

  console.log('\n=== tools/rubric-marker.html ===');
  {
    const page = path.join(ROOT, 'tools/rubric-marker.html');
    /* sitenav and the stylesheets are chrome; leave them out so jsdom loads
       only the opener, the engine and the example rubric, all from disk */
    const html = fs.readFileSync(page, 'utf8')
      .replace(/<script src="[^"]*sitenav\.js"[^>]*><\/script>/, '')
      .replace(/<link [^>]*>/g, '');
    const open = async (prep) => {
      const dom = new JSDOM(html, { runScripts: 'dangerously', resources: new DiskLoader(), pretendToBeVisual: true,
                                    url: ORIGIN + 'tools/rubric-marker.html',
                                    beforeParse(win){ win.scrollTo = () => {}; if (prep) prep(win); } });
      await sleep(600);
      return dom.window;
    };
    let w = await open();
    ok(w.document.querySelector('#rbPick') && !w.document.querySelector('#markTable'), 'first visit shows the open-a-rubric screen');
    ok(/Year 7 Space/.test(w.document.querySelector('.rb-open').textContent), 'lists the site\'s rubrics');
    ok(w.document.querySelector('a[download][href="rubric-starter.json"]'), 'offers the starter rubric');

    /* open the starter as a file */
    const file = new w.File([JSON.stringify(STARTER)], 'starter.json', { type: 'application/json' });
    const input = w.document.querySelector('#rbFile');
    Object.defineProperty(input, 'files', { value: [file] });
    input.dispatchEvent(new w.Event('change'));
    await sleep(700);
    ok(w.document.querySelector('#markTable') && /Practical Investigation/.test(w.document.querySelector('.masthead').textContent), 'opening the starter file boots the marker on it');
    ok([...w.document.querySelectorAll('.masthead-side button.unit-back')].some(b => /Open another rubric/.test(b.textContent)), 'with an "Open another rubric" button');
    const last = w.localStorage.getItem('rubric-marker:last');
    ok(last && JSON.parse(last).id === 'starter-investigation', 'remembers the rubric for next time');

    /* a rubric-data.js file is read as data, never run */
    const jsText = '/* hi */\nwindow.RUBRIC = ' + JSON.stringify(STARTER) + ';\n';
    w = await open(win => win.localStorage.clear());
    const in2 = w.document.querySelector('#rbFile');
    Object.defineProperty(in2, 'files', { value: [new w.File([jsText], 'rubric-data.js')] });
    in2.dispatchEvent(new w.Event('change'));
    await sleep(700);
    ok(w.document.querySelector('#markTable'), 'a unit\'s rubric-data.js opens too (wrapper stripped)');

    /* an old save without a rubric is explained, not crashed on */
    w = await open(win => win.localStorage.clear());
    const in3 = w.document.querySelector('#rbFile');
    Object.defineProperty(in3, 'files', { value: [new w.File([JSON.stringify({version: 2, students: []})], 'old.json')] });
    in3.dispatchEvent(new w.Event('change'));
    await sleep(300);
    ok(/has no rubric inside it/.test(w.document.querySelector('#rbErr').textContent), 'an old rubric-less save gets an explanation');

    /* a saved class opens with its own rubric and its own students */
    const starterSave = fs.readFileSync(path.join(require('os').tmpdir(), 'rubric-test-starter-save.json'), 'utf8');
    w = await open(win => win.localStorage.clear());
    const in4 = w.document.querySelector('#rbFile');
    Object.defineProperty(in4, 'files', { value: [new w.File([starterSave], 'class.json')] });
    in4.dispatchEvent(new w.Event('change'));
    await sleep(700);
    ok(w.eval('state.students.map(s => s.name).join()') === 'Pat Kim,Lee Ray', 'a saved class opens with its students (not the demo)');
    ok(w.eval('state.students[0].marks.eval') === 3, '...and their marks');
  }

  console.log('\n' + (fail ? fail + ' CHECK(S) FAILED' : 'ALL CHECKS PASSED'));
  process.exit(fail ? 1 : 0);
})();

function $$count(w, sel) { return w.document.querySelectorAll(sel).length; }
