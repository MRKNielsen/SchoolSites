/* Boots year7-science/space/rubric-payload.html in a real DOM (jsdom) the
   same way rubric.html does after unlocking — inject into #content, then
   re-create each <script> so it runs — and drives it as a teacher would.

   This exists because the first build of the payload shipped broken: a
   splice in tools/build_space_rubric.py anchored on `const rows = [`, which
   appears three times, matched the wrong one and deleted ~12,600 characters
   including persist(), restore() and demo(). The page then threw
   "restore is not defined" on boot and rendered chrome with no marking grid.
   The checks that existed at the time sliced the script above the render
   functions, so they could not see any of it.

   Run after every rebuild:   node tools/test-space-rubric.js
   Needs jsdom:               npm install jsdom

   Two things the harness itself got wrong first, worth knowing if it fails:
   boot() is async (it awaits restore() before falling back to demo()), so
   settle it before driving the UI; and applyRoll() deliberately keeps the
   marks of any student already listed by name, so a test roll must not
   reuse the demo class's names. */
const fs = require('fs');
const path = require('path');

let JSDOM;
try { ({ JSDOM } = require('jsdom')); }
catch (e) {
  console.error('This harness needs jsdom:  npm install jsdom');
  process.exit(2);
}

/* resolved from this file, so it runs from anywhere and on Windows */
const PAYLOAD = path.join(__dirname, '..', 'year7-science', 'space', 'rubric-payload.html');
if (!fs.existsSync(PAYLOAD)) {
  console.error('No payload at ' + PAYLOAD + '\n'
    + 'It is gitignored — rebuild it:  python tools/build_space_rubric.py');
  process.exit(2);
}
const payload = fs.readFileSync(PAYLOAD, 'utf8');

const dom = new JSDOM(`<!DOCTYPE html><html><body class="rubric-page theme-space"><div id="content"></div></body></html>`,
  { runScripts: 'dangerously', pretendToBeVisual: true, url: 'https://example.org/' });
const { window } = dom;
window.scrollTo = () => {};
const errs = []; window.addEventListener('error', e => errs.push(e.message));

const content = window.document.getElementById('content');
content.innerHTML = payload;
Array.from(content.querySelectorAll('script')).forEach(old => {
  const s = window.document.createElement('script');
  for (const a of old.attributes) s.setAttribute(a.name, a.value);
  s.textContent = old.textContent; old.parentNode.replaceChild(s, old);
});

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
  ok(!payload.includes('ecosystem-rubric'), 'no "ecosystem-rubric" key left in the payload');

  console.log('\n' + (fail ? fail + ' CHECK(S) FAILED' : 'ALL CHECKS PASSED'));
  process.exit(fail ? 1 : 0);
})();
