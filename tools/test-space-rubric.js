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
  ok($$('#p-mark td.qcell input.qin').length === 3*34, `grid is ${3*34} cells (3 students x 34 criteria)`);

  console.log('\n=== entering marks ===');
  ok(window.eval('setMark(0,0,1)') === true && window.eval('state.students[0].q.Q1a') === 1, 'a mark in range is stored');
  ok(window.eval('setMark(0,0,"")') === true && window.eval('state.students[0].q.Q1a') === undefined, 'blank clears it');
  const q1b = window.eval('CRITERIA.findIndex(c => c.id === "Q1b")');
  ok(window.eval(`setMark(0,${q1b},"1.5")`) === true && window.eval('state.students[0].q.Q1b') === 1.5, 'half marks accepted (1.5 / 2)');
  ok(window.eval(`setMark(0,${q1b},"1½")`) === true && window.eval('state.students[0].q.Q1b') === 1.5, '"1½" reads as 1.5');
  ok(window.eval(`setMark(0,${q1b},3)`) === false && window.eval('state.students[0].q.Q1b') === 1.5, 'over the max is refused and the old mark kept');
  ok(window.eval(`setMark(0,${q1b},"1.25")`) === false, 'quarter marks refused');
  ok(window.eval(`setMark(0,${q1b},"abc")`) === false, 'text refused');
  window.eval(`setMark(0,${q1b},"")`);

  console.log('\n=== half the marks or more counts as demonstrated ===');
  const ix = id => window.eval(`CRITERIA.findIndex(c => c.id === "${id}")`);
  const done = id => window.eval(`isDone(state.students[0], "${id}")`);
  window.eval(`setMark(0,${ix('Q7a')},2)`);   ok(done('Q7a') === true,  'Q7a 2/4 counts');
  window.eval(`setMark(0,${ix('Q7a')},1.5)`); ok(done('Q7a') === false, 'Q7a 1.5/4 does not');
  window.eval(`setMark(0,${ix('Q6a')},1)`);   ok(done('Q6a') === true,  'Q6a 1/2 counts');
  window.eval(`setMark(0,${ix('Q2a')},0.5)`); ok(done('Q2a') === true,  'Q2a ½/1 counts (half)');
  window.eval(`setMark(0,${ix('Q4a')},0)`);   ok(done('Q4a') === false, 'a 0 does not');

  console.log('\n=== blank is "not attempted" only once marking has reached it ===');
  const na = (r, id) => window.eval(`isNotAtt(state.students[${r}], "${id}")`);
  ok(na(0,'Q10') === false, 'blank Q10, nobody has a Q10 mark yet -> not marked, not "not attempted"');
  ok(na(1,'Q7a') === false, 'student with no marks at all -> not marked');
  window.eval(`setMark(1,${ix('Q10')},2)`);
  ok(na(0,'Q10') === true, 'once someone has a Q10 mark, a started student\'s blank Q10 is not attempted');
  ok(na(2,'Q10') === false, '...but a student not yet started still reads as not marked');
  ok(window.eval('state.students[2].marks.s1') === null, 'an unstarted student has no band, not band 0');
  ok(window.eval('state.students[1].marks.s4') === 0, 'a started student\'s untouched strand in a marked column is band 0');

  console.log('\n=== typing in the grid keeps the input (no re-render under the caret) ===');
  window.eval('renderAll();');
  const inpQ2b = $$('#markTable tr.row')[2].querySelector(`input[data-c="${ix('Q2b')}"]`);
  inpQ2b.value = '1'; inpQ2b.dispatchEvent(new window.Event('input'));
  const same = $$('#markTable tr.row')[2].querySelector(`input[data-c="${ix('Q2b')}"]`) === inpQ2b;
  ok(same && window.eval('state.students[2].q.Q2b') === 1, 'input event stores the mark and the same input element survives');
  ok(/1<\/b><span>\/50/.test($('#tot-2').innerHTML), 'Mark column updated in place: ' + $('#tot-2').textContent);
  inpQ2b.value = '7'; inpQ2b.dispatchEvent(new window.Event('input'));
  ok(inpQ2b.classList.contains('bad') && window.eval('state.students[2].q.Q2b') === 1, 'an out-of-range entry is flagged and not stored');
  inpQ2b.dispatchEvent(new window.Event('blur'));
  ok(inpQ2b.value === '1' && !inpQ2b.classList.contains('bad'), 'leaving the cell puts the stored mark back');
  ok($$('#p-mark th.qsub .qmax').map(e=>e.textContent).join('') .startsWith('/1/2/1/1/1'), 'column heads show what each part is out of');

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
  const col5 = $$('#markTable tr.row')[0].querySelectorAll('td.qcell input')[5];
  const trueIdx = +col5.dataset.c;
  ok(window.eval(`CRITERIA[${trueIdx}].id`) === 'Q3a',
     'the 6th column on screen maps to Q3a');
  window.eval(`setMark(0, ${trueIdx}, 1);`);
  ok(window.eval('state.students[0].q.Q3a') === 1, 'marking it marks Q3a, not something else');
  window.eval(`setMark(0, ${trueIdx}, "");`);

  console.log('\n=== marks drive bands, comments, groups, print ===');
  window.eval('const s=state.students[0]; CRITERIA.forEach(c=>s.q[c.id]=c.max); refreshClass(); regenerate(s,true); renderAll();');
  ok(window.eval('JSON.stringify(STRANDS.map(x=>state.students[0].marks[x.id]))') === '[4,4,4,4,3,3]',
     'full marks -> top band on every strand');
  const cmt = window.eval('state.students[0].comment');
  ok(cmt.length > 80 && !/undefined|\{their\}|NaN/.test(cmt), `comment ${cmt.length} chars, clean`);
  window.eval('renderPrint(); renderGroups();');
  ok(/Priya/.test($('#p-print').textContent), 'printable rubric names the student');
  ok(window.eval('rawTotal(state.students[0])') === 50 && /50 \/ 50 marks/.test($('#p-print').textContent), 'full marks total 50 / 50 on the print');
  ok($('#p-groups').textContent.trim().length > 40, 'teaching groups populated');

  console.log('\n=== autosave round-trips (700ms debounce) ===');
  window.eval('persist();');
  await sleep(1100);
  const saved = JSON.parse((await window.storage.get('astronomy-rubric:v1')).value);
  ok(saved.students.length === 3, `autosave holds ${saved.students.length} students`);
  ok(saved.version === 2, `save format v${saved.version}`);

  window.eval('state.students = []; renderAll();');
  const got = await window.eval('restore()');
  window.eval('renderAll();');
  ok(got === true && window.eval('state.students.length') === 3, 'restored 3 students');
  ok(window.eval('Object.keys(state.students[0].q).length') === 34, 'all 34 marks came back');
  ok(window.eval('state.students[0].q.Q7a') === 4, 'as numbers (Q7a = 4)');

  console.log('\n=== a tick-era (v1) save still opens ===');
  window.eval(`importJSON(JSON.stringify({version:1, meta:{}, students:[
    {name:"Old Tick", pron:"they", q:{Q1a:true, Q7a:true, Q10:"x"}, override:{}, comment:"", edited:false}]}))`);
  ok(window.eval('JSON.stringify(state.students[0].q.Q1a)+","+state.students[0].q.Q7a') === '1,4', 'ticks become full marks (Q1a 1, Q7a 4)');
  ok(window.eval('"Q10" in state.students[0].q') === false, '"x" becomes blank (not attempted)');
  ok(window.eval('state.students[0].q.Q2a') === 0, 'an empty tick-era cell (attempted, not successful) becomes 0');

  console.log('\n=== CSV round trip ===');
  window.eval(`importCSV("Name,Pronoun,Q1 (ear) /1,Q7 (a) /4,Q10\\nAva,she,1,2.5,\\nBen,he,y,9,0")`);
  ok(window.eval('state.students.length') === 2, 'two students imported');
  ok(window.eval('state.students[0].q.Q7a') === 2.5 && window.eval('"Q10" in state.students[0].q') === false, 'numbers read, blank stays blank');
  ok(window.eval('state.students[1].q.Q1a') === 1 && window.eval('state.students[1].q.Q10') === 0, 'a "y" is full marks, 0 is 0');
  ok(window.eval('"Q7a" in state.students[1].q') === false, 'an out-of-range 9/4 is left blank, not stored');

  console.log('\n=== the key is namespaced away from bio ===');
  ok(!pageHtml.includes('ecosystem-rubric'), 'no "ecosystem-rubric" key left in the payload');

  console.log('\n' + (fail ? fail + ' CHECK(S) FAILED' : 'ALL CHECKS PASSED'));
  process.exit(fail ? 1 : 0);
})();
