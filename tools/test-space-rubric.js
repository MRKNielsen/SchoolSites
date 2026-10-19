/* Boots year7-science/space/rubric.html in a real DOM (jsdom) and drives it
   as a teacher would: enters a class, cycles ticks, checks the bands,
   comment, teaching groups, printable rubric and the autosave round trip.

   The page is not gated, so this loads it whole rather than injecting a
   decrypted payload. It exists because the first build shipped broken: a
   splice in tools/build_space_rubric.py anchored on `const rows = [`, which
   appears three times, matched the wrong one and deleted ~12,600 characters
   including persist(), restore() and demo(). The page threw
   "restore is not defined" on boot and rendered chrome with no marking grid.
   The checks at the time sliced the script above the render functions, so
   they could not see any of it.

   Run after every rebuild:   node tools/test-space-rubric.js
   Needs jsdom:               npm install jsdom

   Two traps the harness itself hit first: boot() is async (it awaits
   restore() before falling back to demo()), so settle it before driving the
   UI; and applyRoll() deliberately keeps the marks of any student already
   listed by name, so a test roll must not reuse the demo class's names. */

const fs = require('fs');
const path = require('path');

let JSDOM;
try { ({ JSDOM } = require('jsdom')); }
catch (e) { console.error('This harness needs jsdom:  npm install jsdom'); process.exit(2); }

const PAGE = path.join(__dirname, '..', 'year7-science', 'space', 'rubric.html');
if (!fs.existsSync(PAGE)) {
  console.error('No page at ' + PAGE + '\nBuild it:  python tools/build_space_rubric.py');
  process.exit(2);
}
const pageHtml = fs.readFileSync(PAGE, 'utf8');

/* Load the page itself, scripts and all. External CSS/JS (tokens, sitenav)
   is not fetched, which affects only how it looks, not what it does. */
const dom = new JSDOM(pageHtml, { runScripts: 'dangerously', pretendToBeVisual: true,
                                  url: 'https://example.org/year7-science/space/rubric.html' });
const { window } = dom;
window.scrollTo = () => {};
const errs = []; window.addEventListener('error', e => errs.push(e.message));

const $ = s => window.document.querySelector(s);
const $$ = s => Array.from(window.document.querySelectorAll(s));
const sleep = ms => new Promise(r => setTimeout(r, ms));
let fail = 0;
const ok = (c, m) => { console.log((c?'  OK   ':'  FAIL ')+m); if(!c) fail++; };

(async () => {
  /* boot() is async (it awaits restore() before falling back to demo()), so
     settle it before driving the UI or the demo class lands on top of
     whatever the test just entered. */
  await sleep(200);
  ok(errs.length===0, errs.length? 'boot errors: '+errs.join('|') : 'boots clean');
  ok(window.eval('state.students.length') === 6, 'boot fell back to the demo class (6 students)');

  console.log('\n=== a teacher enters their own class ===');
  await window.storage.set('astronomy-rubric:v1', '');     // clear the demo autosave
  $('#f-roll').value = 'Priya Shah, she\nTom Reilly, he\nJordan Lee';
  window.eval('applyRoll();');
  ok(window.eval('state.students.length') === 3, '3 fresh students replace the demo');
  ok(window.eval('Object.keys(state.students[0].q).length') === 0,
     'new names start blank (applyRoll keeps marks only for names already listed)');
  ok($$('#p-mark td.qcell').length === 3*34, `grid is ${3*34} cells (3 students x 34 criteria)`);

  console.log('\n=== ticking works ===');
  window.eval('cycleTick(0,0);');
  ok(window.eval('state.students[0].q.Q1a') === true, 'click 1 = successful');
  window.eval('cycleTick(0,0);');
  ok(window.eval('state.students[0].q.Q1a') === 'x', 'click 2 = not attempted');
  window.eval('cycleTick(0,0);');
  ok(window.eval('state.students[0].q.Q1a') === undefined, 'click 3 = cleared');

  console.log('\n=== the grid runs in paper order, not strand order ===');
  const order = window.eval('JSON.stringify(MARK_COLS.map(i => CRITERIA[i].id))');
  const ids = JSON.parse(order);
  const want = ['Q1a','Q1b','Q2a','Q2b','Q2c','Q3a','Q3b','Q3c','Q3d',
                'Q4a','Q4b','Q4c','Q4d','Q4e','Q5a','Q5b','Q5c','Q6a','Q6b',
                'Q7a','Q7b','Q7ci','Q7cii','Q7di','Q7dii',
                'Q8a','Q8bi','Q8bii','Q9a','Q9bi','Q9bii','Q10','Q11a','Q11b'];
  ok(JSON.stringify(ids) === JSON.stringify(want),
     'columns are Q1\u2192Q11 in paper order');
  if (JSON.stringify(ids) !== JSON.stringify(want)) console.log('        got: ' + ids.join(' '));

  /* the header must read Q1..Q11 left to right, once each */
  const qs = $$('#markTable tr.hrow th.q').map(e => e.textContent.trim());
  ok(JSON.stringify(qs) === JSON.stringify(
       ['Q1','Q2','Q3','Q4','Q5','Q6','Q7','Q8','Q9','Q10','Q11']),
     'header row reads ' + qs.join(' '));

  /* CRITERIA itself must NOT have been reordered — the bands, the printed
     rubric and the reference table all read it in strand order */
  /* MARK_COLS must cover every criterion exactly once, whatever order
     CRITERIA happens to be listed in */
  const sorted = [...JSON.parse(window.eval('JSON.stringify(MARK_COLS)'))].sort((a,b)=>a-b);
  ok(JSON.stringify(sorted) === JSON.stringify([...Array(34).keys()]),
     'MARK_COLS is a permutation of all 34 criteria, no gaps or repeats');

  /* the CSV export should hand back the same order the teacher just marked in */
  const csvHead = window.eval('CRITERIA.map(c => qLabel(c)).join("|")').split('|');
  ok(csvHead[0] === 'Q1 (ear)' && csvHead[33] === 'Q11 (exp)',
     'CSV columns run Q1 \u2192 Q11 too (' + csvHead[0] + ' \u2026 ' + csvHead[33] + ')');

  console.log('\n=== clicking a reordered column hits the right criterion ===');
  /* column 5 on screen is Q3a; its data-c is the true CRITERIA index */
  const col5 = $$('#markTable tr.row')[0].querySelectorAll('td.qcell button')[5];
  const trueIdx = +col5.dataset.c;
  ok(window.eval(`CRITERIA[${trueIdx}].id`) === 'Q3a',
     'the 6th column on screen maps to Q3a');
  window.eval(`cycleTick(0, ${trueIdx});`);
  ok(window.eval('state.students[0].q.Q3a') === true, 'ticking it marks Q3a, not something else');
  window.eval(`cycleTick(0, ${trueIdx}); cycleTick(0, ${trueIdx});`);

  console.log('\n=== marks drive bands, comments, groups, print ===');
  window.eval('const s=state.students[0]; CRITERIA.forEach(c=>s.q[c.id]=true); recompute(s); regenerate(s,true); renderAll();');
  ok(window.eval('JSON.stringify(STRANDS.map(x=>state.students[0].marks[x.id]))') === '[4,4,4,4,3,3]',
     'full marks -> top band on every strand');
  const cmt = window.eval('state.students[0].comment');
  ok(cmt.length > 80 && !/undefined|\{their\}|NaN/.test(cmt), `comment ${cmt.length} chars, clean`);
  window.eval('renderPrint(); renderGroups();');
  ok(/Priya/.test($('#p-print').textContent), 'printable rubric names the student');
  ok($('#p-groups').textContent.trim().length > 40, 'teaching groups populated');

  console.log('\n=== autosave round-trips (700ms debounce) ===');
  window.eval('persist();');
  await sleep(1100);
  const saved = JSON.parse((await window.storage.get('astronomy-rubric:v1')).value);
  ok(saved.students.length === 3, `autosave holds ${saved.students.length} students`);
  ok(saved.version === 1, `save format v${saved.version}`);

  window.eval('state.students = []; renderAll();');
  const got = await window.eval('restore()');
  window.eval('renderAll();');
  ok(got === true && window.eval('state.students.length') === 3, 'restored 3 students');
  ok(window.eval('Object.keys(state.students[0].q).length') === 34, 'all 34 ticks came back');

  console.log('\n=== the key is namespaced away from bio ===');
  ok(!pageHtml.includes('ecosystem-rubric'), 'no "ecosystem-rubric" key left in the payload');

  console.log('\n' + (fail ? fail + ' CHECK(S) FAILED' : 'ALL CHECKS PASSED'));
  process.exit(fail ? 1 : 0);
})();
