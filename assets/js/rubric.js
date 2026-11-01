/* =========================================================================
   rubric.js — the rubric marker engine.

   Marks a class against any rubric: a marking grid of question marks, bands
   worked out per strand, written comments, teaching groups, class analysis
   and printable rubrics. Everything specific to one assessment lives in a
   rubric file that sets window.RUBRIC before this script runs:

     year7-science/space/rubric-data.js   the Astronomy Test (CAT 5)

   Pages that use it:
     year7-science/space/rubric.html      Space, with its rubric built in
     tools/rubric-marker.html             any rubric a teacher opens

   The page supplies <body class="rubric-page theme-X"> and an empty
   <div id="rubric-app"></div>; this script builds everything inside it.
   It is a classic script on purpose: tools/test-space-rubric.js drives the
   page through its globals (state, setMark, CRITERIA ...).

   Nothing is sent anywhere. Marks autosave to localStorage in this browser
   under the rubric's storageKey; Save file / Open file move them between
   machines, and a saved file carries the rubric with it.

   Started life as the Space page's inline script (itself built from bio's
   rubric by the now-retired tools/build_space_rubric.py). The engine is
   unchanged in behaviour; what was Space-specific now comes from the rubric.
   ========================================================================= */
"use strict";

/* ============================ RUBRIC ============================ */
const RUBRIC_FORMAT = "rubric-marker/1";
const RUBRIC = window.RUBRIC || null;
const ID_RE = /^[A-Za-z0-9_-]{1,40}$/;

/* Check a rubric before anything is built from it. Returns {errors, warnings}.
   An error means the marker would misbehave silently (a strand capped by an
   empty band, a weight that disagrees with the paper), so the page shows the
   list instead of the marker. Every rule here was learnt the hard way on the
   Space and bio rubrics — see CLAUDE.md "A unit's rubric is generated". */
function validateRubric(R){
  const errors = [], warnings = [];
  const E = m => errors.push(m), W = m => warnings.push(m);
  if(!R || typeof R !== "object" || Array.isArray(R)){ E("The file does not contain a rubric."); return {errors, warnings}; }
  if(R.format !== RUBRIC_FORMAT) E("format must be \"" + RUBRIC_FORMAT + "\" (found " + JSON.stringify(R.format) + ").");
  if(typeof R.id !== "string" || !ID_RE.test(R.id)) E("id must be 1–40 letters, digits, - or _ (found " + JSON.stringify(R.id) + ").");
  if(typeof R.title !== "string" || !R.title.trim()) E("title is missing.");
  if(R.theme != null && !/^[a-z0-9-]{1,30}$/.test(String(R.theme))) E("theme must be a plain theme name such as \"space\".");
  if(R.storageKey != null && (typeof R.storageKey !== "string" || !R.storageKey)) E("storageKey must be a non-empty string.");
  if(R.columnOrder != null && !["listed","question"].includes(R.columnOrder)) E("columnOrder must be \"listed\" or \"question\".");
  if(R.pass != null && !(typeof R.pass === "number" && R.pass > 0 && R.pass <= 1)) E("pass must be a number above 0 and at most 1.");
  if(!Array.isArray(R.bands) || R.bands.length !== 4 || !R.bands.every(b => typeof b === "string" && b.trim()))
    E("bands must list exactly four band labels (bands 1–4; band 0 is band0).");
  ["parts","strands","criteria"].forEach(k => { if(!Array.isArray(R[k]) || !R[k].length) E(k + " must be a non-empty list."); });
  if(errors.length) return {errors, warnings};

  const uniq = (list, what) => {
    const seen = new Set();
    list.forEach((x, i) => {
      if(!x || typeof x !== "object"){ E(what + " " + (i+1) + " is not an object."); return; }
      if(typeof x.id !== "string" || !ID_RE.test(x.id)) E(what + " " + (i+1) + ": id " + JSON.stringify(x.id) + " must be 1–40 letters, digits, - or _.");
      else if(seen.has(x.id)) E(what + " id \"" + x.id + "\" is used twice.");
      else seen.add(x.id);
    });
    return seen;
  };
  const partIds = uniq(R.parts, "Part"), strandIds = uniq(R.strands, "Strand"), critIds = uniq(R.criteria, "Criterion");
  if(errors.length) return {errors, warnings};

  R.parts.forEach(p => { if(typeof p.name !== "string" || !p.name.trim()) E("Part " + p.id + " has no name."); });
  const str = v => typeof v === "string" && v.trim() !== "";
  R.strands.forEach(s => {
    const where = "Strand " + s.id;
    if(!str(s.name)) E(where + " has no name.");
    const mb = s.maxBand == null ? 4 : s.maxBand;
    if(!Number.isInteger(mb) || mb < 1 || mb > 4){ E(where + ": maxBand must be a whole number from 1 to 4."); return; }
    if(!Array.isArray(s.bands) || s.bands.length < mb) E(where + ": needs a descriptor for each of bands 1–" + mb + ".");
    else s.bands.slice(0, mb).forEach((b, i) => { if(!b || !str(b.d)) E(where + ", band " + (i+1) + ": descriptor (d) is empty."); });
    if(!Array.isArray(s.can) || s.can.length < mb || !s.can.slice(0, mb).every(str)) E(where + ": can needs one phrase for each of bands 1–" + mb + ".");
    if(!Array.isArray(s.next) || s.next.length < mb || !s.next.slice(0, mb).every(str)) E(where + ": next needs one phrase for each of bands 1–" + mb + ".");
    if(!str(s.start)) E(where + ": start (the next step for band 0) is empty.");
    if(s.weight != null && !(typeof s.weight === "number" && s.weight > 0)) E(where + ": weight must be a positive number.");
    if(s.code != null && typeof s.code !== "string") E(where + ": code must be text.");
  });
  R.criteria.forEach(c => {
    const where = "Criterion " + c.id;
    if(!str(c.q)) E(where + ": q (the question number shown on the grid) is empty.");
    if(!partIds.has(c.part)) E(where + ": part \"" + c.part + "\" is not one of the parts.");
    if(!(typeof c.max === "number" && c.max > 0 && Math.abs(c.max * 2 - Math.round(c.max * 2)) < 1e-9))
      E(where + ": max must be a positive whole or half mark.");
    if(c.strand == null) return;     /* recorded, but outside the rubric */
    if(!strandIds.has(c.strand)){ E(where + ": strand \"" + c.strand + "\" does not exist."); return; }
    const s = R.strands.find(x => x.id === c.strand), mb = s.maxBand == null ? 4 : s.maxBand;
    if(!Number.isInteger(c.band) || c.band < 1 || c.band > mb) E(where + ": band must be from 1 to " + mb + " (strand " + s.id + "'s maxBand).");
  });
  if(errors.length) return {errors, warnings};

  /* The band ladder must be complete. topCell() walks down from maxBand and
     missedBelow() penalises gaps, so a band with no question behind it
     silently caps the strand below it. */
  R.strands.forEach(s => {
    const mb = s.maxBand == null ? 4 : s.maxBand;
    for(let b = 1; b <= mb; b++)
      if(!R.criteria.some(c => c.strand === s.id && c.band === b))
        E("Strand " + s.id + " has no question for band " + b + ", so nobody could be awarded above band " + (b-1) + ". Add a question for it, or lower maxBand.");
  });
  /* A strand's weight is its marks on the paper, so the overall level is
     weighted exactly as the paper is. Leave weight out to have it summed. */
  const sumOf = id => R.criteria.filter(c => c.strand === id).reduce((n, c) => n + c.max, 0);
  R.strands.forEach(s => {
    if(s.weight != null && Math.abs(s.weight - sumOf(s.id)) > 1e-9)
      E("Strand " + s.id + ": weight is " + s.weight + " but its questions are worth " + sumOf(s.id) + " marks. Fix one, or leave weight out.");
  });
  const total = R.criteria.reduce((n, c) => n + c.max, 0);
  if(R.total != null && Math.abs(R.total - total) > 1e-9) E("total is " + R.total + " but the questions add up to " + total + ".");
  R.parts.forEach(p => { if(!R.criteria.some(c => c.part === p.id)) W("Part " + p.id + " has no questions, so it will not appear on the grid."); });
  const off = R.criteria.filter(c => c.strand == null).length;
  if(off) W(off + " question" + (off === 1 ? " is" : "s are") + " outside the rubric (no strand): marked and totalled, but evidence for no band.");
  if(R.parts.length > 5) W("More than five parts: part colours repeat after the fifth.");
  if(R.attribution != null && typeof R.attribution !== "string") E("attribution must be text.");
  ["levels","gloss"].forEach(k => {
    if(R[k] != null && !(Array.isArray(R[k]) && R[k].length === 5 && R[k].every(t => typeof t === "string" && t.trim())))
      E(k + " must list five phrases, for overall levels 0–4.");
  });
  if(R.save && R.save.version != null && !(Number.isInteger(R.save.version) && R.save.version >= 1)) E("save.version must be a whole number from 1.");
  return {errors, warnings};
}

/* Fill in everything a rubric may leave out. Only called on a valid rubric. */
function normaliseRubric(src){
  const R = JSON.parse(JSON.stringify(src));
  R.task = R.task || R.title;
  R.eyebrow = R.eyebrow || R.context || "Assessment";
  R.subtitle = R.subtitle || "rubric & report generator";
  R.band0 = R.band0 || "Not demonstrated";
  /* the overall level's name (printed rubric, analysis) and the phrase the
     comment opens with ("Across this test Ava is …"), for levels 0–4 */
  R.levels = R.levels || ["Not demonstrated","Working towards the expected standard","At the expected standard",
                          "At the expected standard","Above the expected standard"];
  R.gloss = R.gloss || ["not yet demonstrating the expected standard","working towards the expected standard",
                        "at the expected standard","working securely at the expected standard","working above the expected standard"];
  R.pass = R.pass || 0.5;
  R.columnOrder = R.columnOrder || "listed";
  R.storageKey = R.storageKey || ("rubric-marker:" + R.id);
  R.fileStem = String(R.fileStem || R.id).toLowerCase().replace(/[^a-z0-9-]+/g, "-").replace(/^-+|-+$/g, "") || "rubric";
  const n = R.noun || {};
  R.noun = {task: n.task || "task", item: n.item || "question"};
  R.noun.items = n.items || R.noun.item + "s";
  R.save = Object.assign({version:1, marksSince:1, migrations:{}}, R.save || {});
  R.strands.forEach(s => {
    s.maxBand = s.maxBand == null ? 4 : s.maxBand;
    if(s.weight == null) s.weight = R.criteria.filter(c => c.strand === s.id).reduce((t, c) => t + c.max, 0);
    if(!s.sub){
      const qs = [];
      R.criteria.forEach(c => { if(c.strand === s.id && !qs.includes(c.q)) qs.push(c.q); });
      s.sub = qs.join(", ");
    }
    s.bands = s.bands.map(b => ({q: (b && b.q) || "", d: b.d}));
  });
  R.criteria.forEach(c => { c.sub = c.sub || ""; c.label = c.label || ""; if(c.strand === undefined) c.strand = null; });
  return R;
}

const RUBRIC_CHECK = RUBRIC ? validateRubric(RUBRIC) : {errors:["No rubric was loaded on this page."], warnings:[]};
const RUBRIC_OK = RUBRIC_CHECK.errors.length === 0;
const R = RUBRIC_OK ? normaliseRubric(RUBRIC) : null;

const STRANDS  = R ? R.strands  : [];
const CRITERIA = R ? R.criteria : [];
const PARTS    = R ? R.parts    : [];
const NOUN     = R ? R.noun     : {task:"task", item:"question", items:"questions"};
const DEFAULT_BANDS = R ? [...R.bands] : ["","","",""];
const DEFAULT_BAND0 = R ? R.band0 : "Not demonstrated";

/* part ids are the rubric's own; classes are by position so the CSS can
   colour any task's parts (pA..pE, wrapping after five) */
const PART_CLS = {};
PARTS.forEach((p, i) => PART_CLS[p.id] = "p" + "ABCDE"[i % 5]);
const partCls = id => PART_CLS[id] || "pA";

/* label a criterion the way the task numbers it: "Q4 (b)", "Q7 (ci)" */
const qLabel = c => c.q + (c.sub ? " (" + c.sub + ")" : "");

/* Column order for the marking grid only — CRITERIA itself stays in strand
   order, because the bands, printed rubric and reference read it that way.
   "question": sort by question number, then by criterion id; Space's ids were
   written to run in paper order within each question, which
   tools/test-space-rubric.js asserts. "listed" (the default): the order the
   rubric lists them in. */
const qNum = c => parseInt(String(c.q).replace(/^\D+/, ""), 10) || 0;
const MARK_COLS = (R && R.columnOrder === "question")
  ? CRITERIA.map((c, i) => i).sort((a, b) =>
      qNum(CRITERIA[a]) - qNum(CRITERIA[b]) ||
      (CRITERIA[a].id < CRITERIA[b].id ? -1 : CRITERIA[a].id > CRITERIA[b].id ? 1 : 0))
  : CRITERIA.map((c, i) => i);

/* Saved files carry a version. When a rubric renames criteria, it bumps
   save.version and adds a migration: save.migrations[v] maps version v's ids
   to version v+1's. Files from before save.marksSince stored ticks, which
   open as full marks (tick) or blank. */
const SAVE_VERSION = R ? R.save.version : 1;
const MARKS_SINCE  = R ? R.save.marksSince : 1;
const MIGRATIONS   = R ? R.save.migrations : {};
/* rename every key in one pass, so swaps like A3i→A2i and A4i→A3i cannot collide */
function migrateTicks(q, fromVersion){
  let cur = q || {};
  for(let v = Math.max(1, fromVersion || 1); v < SAVE_VERSION; v++){
    const map = MIGRATIONS[v] || {};
    const next = {};
    Object.keys(cur).forEach(k => {
      const id = map[k] || k;
      if(next[id] === true) return;   // a merge keeps the stronger mark
      next[id] = cur[k];
    });
    cur = next;
  }
  return cur;
}

/* evidence index: EV[strandId][band] = [criterion ids], EVALL = every id in the strand */
const EV = {}, EVALL = {};
STRANDS.forEach(s => { EV[s.id] = {1:[],2:[],3:[],4:[]}; EVALL[s.id] = []; });
CRITERIA.forEach(c => { if(c.strand){ EV[c.strand][c.band].push(c.id); EVALL[c.strand].push(c.id); } });

/* A mark is a number out of the criterion's `max` (from the paper), or blank.
     number — attempted; 0 is attempted with nothing creditable
     blank  — not attempted, once the student has a mark somewhere AND
              someone in the class has a mark in that column; until then it
              is simply not marked yet
   A criterion counts as demonstrated for its rubric cell once it earns at
   least PASS of its marks: 1/2 and 2/4 count, 1/3 does not. */
const PASS = R ? R.pass : 0.5;
const MAXOF = {}; CRITERIA.forEach(c => MAXOF[c.id] = c.max);
const MAX_TOTAL = CRITERIA.reduce((n,c) => n + c.max, 0);
const fmtMark = v => String(Math.round(v * 2) / 2);
const hasMark = (st, id) => typeof st.q[id] === "number";
const started = st => CRITERIA.some(c => hasMark(st, c.id));
let COLS_MARKED = new Set();
function refreshClass(){
  COLS_MARKED = new Set();
  state.students.forEach(st => CRITERIA.forEach(c => { if(hasMark(st, c.id)) COLS_MARKED.add(c.id); }));
  state.students.forEach(recompute);
}
const isDone   = (st, id) => hasMark(st, id) && st.q[id] > 0 && st.q[id] >= MAXOF[id] * PASS;
const isNotAtt = (st, id) => !hasMark(st, id) && COLS_MARKED.has(id) && started(st);
function rawTotal(st){ return CRITERIA.reduce((n,c) => n + (hasMark(st, c.id) ? st.q[c.id] : 0), 0); }
/* "", "1", "1.5", "1,5", "1½", "½" -> number | null (blank) | NaN (invalid) */
function parseMark(raw, max){
  let s = String(raw == null ? "" : raw).trim().replace(",", ".");
  if(s === "") return null;
  s = s.replace(/^½$/, "0.5").replace(/½$/, ".5");
  if(!/^(\d+(\.\d+)?|\.\d+)$/.test(s)) return NaN;
  const v = parseFloat(s);
  if(v < 0 || v > max || Math.abs(v * 2 - Math.round(v * 2)) > 1e-9) return NaN;
  return v;
}

/* A rubric cell is met when every criterion behind it is done. */
function cellMet(st, s, b){
  const need = EV[s.id][b];
  return need.length > 0 && need.every(id => isDone(st, id));
}
/* Highest cell met outright, ignoring whatever sits below it. 0 = none. */
function topCell(st, s){
  for(let b = maxBandOf(s); b >= 1; b--) if(cellMet(st, s, b)) return b;
  return 0;
}
/* Developmental penalty: every question below the top cell that is not done
   pulls the award down one band. Reaching band 4 while skipping the
   groundwork therefore does not award band 4. */
function missedBelow(st, s, top){
  let n = 0;
  for(let b = 1; b < top; b++) EV[s.id][b].forEach(id => { if(!isDone(st, id)) n++; });
  return n;
}
function strandTouched(st, s){
  return EVALL[s.id].some(id => hasMark(st, id))
      || (started(st) && EVALL[s.id].some(id => COLS_MARKED.has(id)));
}

/* Everything known about one strand. band 0 = not demonstrated. */
function strandResult(st, s){
  const top = topCell(st, s);
  const missed = missedBelow(st, s, top);
  const derived = Math.max(0, top - missed);
  const o = st.override[s.id];
  const overridden = Number.isInteger(o) && o >= 0 && o <= maxBandOf(s);
  return {top, missed, derived, band: overridden ? o : derived, overridden,
          assessed: strandTouched(st, s) || overridden};
}
function deriveBand(st, s){ const r = strandResult(st, s); return r.assessed ? r.derived : null; }

/* st.marks is the cache everything downstream reads. */
function recompute(st){
  if(!st.q) st.q = {};
  if(!st.override) st.override = {};
  st.res = {};
  STRANDS.forEach(s => {
    const r = strandResult(st, s);
    st.res[s.id] = r;
    st.marks[s.id] = r.assessed ? r.band : null;
  });
}
function newStudent(name, pron){
  const st = {id:uid(), name:name||"", pron:pron||"they",
              q:{}, override:{}, marks:{}, res:{}, comment:"", edited:false};
  recompute(st);
  return st;
}

/* completion picture across the whole test */
function tally(st){
  const done = CRITERIA.filter(c => isDone(st, c.id)).length;
  const notAtt = CRITERIA.filter(c => isNotAtt(st, c.id)).length;
  const byPart = {};
  PARTS.forEach(pt => byPart[pt.id] = CRITERIA.filter(c => c.part === pt.id && isNotAtt(st, c.id)).length);
  let worst = null;
  PARTS.forEach(pt => { if(byPart[pt.id] > 0 && (!worst || byPart[pt.id] > byPart[worst])) worst = pt.id; });
  return {done, notAtt, total: CRITERIA.length, worstPart: worst, byPart,
          score: rawTotal(st), outOf: MAX_TOTAL};
}

/* ---- overall level. mean sits on 0..4: 0 is nothing demonstrated,
   4 is the top band everywhere. Boundaries at the half-bands. ---- */
function overallLevel(pct){
  if(pct === null) return {name:"Not yet assessed", key:-1, mean:null};
  const mean = pct * 4;
  const key = mean < 0.5 ? 0 : mean < 1.5 ? 1 : mean < 2.5 ? 2 : mean < 3.5 ? 3 : 4;
  return {name:R.levels[key], key, mean};
}
const GLOSS = R ? R.gloss : [];

/* ============================ STATE ============================ */
const state = {
  meta:{cls:"", teacher:"", task: R ? R.task : "", date:""},
  band0:DEFAULT_BAND0,
  bandLabels:[...DEFAULT_BANDS],
  students:[],           // {id,name,pron,q:{critId:mark},override:{strandId:band},marks:{strandId:0-4|null},comment,edited}
  opts:{length:"standard", person:"third", steps:2},
  ui:{tab:"setup", cmtSel:null, groupStrand: STRANDS.length ? STRANDS[0].id : ""}
};
let seq = 1;
const uid = () => "st" + (seq++) + "_" + Math.random().toString(36).slice(2,7);

/* ============================ HELPERS ============================ */
const $  = s => document.querySelector(s);
const $$ = s => Array.from(document.querySelectorAll(s));
function esc(t){ return String(t==null?"":t).replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c])); }
function toast(msg){ const s=$("#status"); s.textContent=msg; s.classList.add("show"); clearTimeout(s._t); s._t=setTimeout(()=>s.classList.remove("show"),2200); }
const strandById = id => STRANDS.find(s => s.id === id);
const maxBandOf = s => s.maxBand || 4;

function firstName(n){ return String(n||"").trim().split(/\s+/)[0] || "The student"; }
function pronoun(p){
  if(p === "he")  return {sub:"he",  Sub:"He",  obj:"him", pos:"his"};
  if(p === "she") return {sub:"she", Sub:"She", obj:"her", pos:"her"};
  return {sub:"they", Sub:"They", obj:"them", pos:"their"};
}
/* stable per-student variation so wording differs between students but not between rebuilds */
function seedOf(str){ let h = 2166136261; for(let i=0;i<str.length;i++){ h ^= str.charCodeAt(i); h = Math.imul(h,16777619); } return Math.abs(h); }
const pick = (arr, seed, salt=0) => arr[(seed + salt*7919) % arr.length];

function assessed(st){ return STRANDS.filter(s => Number.isInteger(st.marks[s.id])); }
/* Weighted position on the 0-to-top band scale, across EVERY strand.
   An unmarked strand counts as 0, so a student cannot read "at the
   expected standard" overall on the strength of one strand while the
   other six are blank. While marking is incomplete the figure is
   provisional, and the interface says so rather than hiding it. */
function pctOf(st){
  if(!assessed(st).length) return null;
  let got = 0, max = 0;
  STRANDS.forEach(s => {
    const w = s.weight || 1;
    const b = Number.isInteger(st.marks[s.id]) ? st.marks[s.id] : 0;
    got += (b / maxBandOf(s)) * w;
    max += w;
  });
  return max === 0 ? null : got / max;
}
function plain(t){ return String(t||"").replace(/\{their\}/g,"their"); }
function joinList(items){
  if(items.length <= 1) return items[0] || "";
  if(items.length === 2) return items[0] + " and " + items[1];
  return items.slice(0,-1).join(", ") + " and " + items[items.length-1];
}

/* ============================ COMMENT ENGINE ============================ */
function buildComment(st){
  const a = assessed(st);
  const fn = firstName(st.name);
  const second = state.opts.person === "second";
  const P = pronoun(st.pron);
  const S  = second ? "you"  : P.sub;
  const Sc = second ? "You"  : P.Sub;
  const NAME = second ? "You" : fn;
  const POS = second ? "your" : P.pos;
  const seed = seedOf(st.name);

  if(!a.length){
    return NAME + (second ? " have not yet been assessed on this task." : " has not yet been assessed on this task.");
  }

  const pct = pctOf(st);
  const lvl = overallLevel(pct);

  // rank strands: strengths high-first, next steps low-first (Part D weighted forward)
  const norm = s => st.marks[s.id] / maxBandOf(s);
  const scored = a.filter(s => st.marks[s.id] >= 1);
  const wnorm = s => norm(s) * Math.sqrt(s.weight || 1);
  /* next steps rank on what is left to gain, not on the same scale as
     strengths — otherwise a strand with a low maxBand is always both. */
  const wgap  = s => (1 - norm(s)) * Math.sqrt(s.weight || 1);
  const byHigh = [...scored].sort((x,y) => wnorm(y)-wnorm(x) || (y.weight||1)-(x.weight||1));
  const byLow  = [...a].sort((x,y) => wgap(y)-wgap(x) || (y.weight||1)-(x.weight||1));

  const poss = second ? "your" : P.pos;
  const fix = t => String(t||"").replace(/\{their\}/g, poss);
  const canOf  = s => fix(s.can[st.marks[s.id]-1]);
  /* at band 0 the next step is the way in, not the next rung up */
  const nextOf = s => { const b = st.marks[s.id];
    return fix(b <= 0 ? s.start : s.next[Math.min(b-1, s.next.length-1)]); };

  const isAre = second ? "are" : "is";
  const g = GLOSS[lvl.key];
  const OPEN = second ? ["Across this "+NOUN.task+" you are "+g+"."]
                      : ["Across this "+NOUN.task+" "+fn+" is "+g+"."];
  const opening = pick(OPEN, seed, 0);

  const strengthLead = pick(
    second ? ["You can now ", "You have shown that you can ", "Your work shows that you can "]
           : [fn+" can now ", fn+" has shown that "+P.sub+" can ", POS.charAt(0).toUpperCase()+POS.slice(1)+" work shows that "+P.sub+" can "],
    seed, 1);
  const alsoLead = pick(
    second ? ["You can also ", "You can also now "] : [Sc+" can also ", fn+" can also "],
    seed, 2);
  const noStrength = second ? "To make a start, you should " : "To make a start, "+fn+" should ";
  const stepLead0 = pick(
    second ? ["To build on this, you should ", "The next step is to ", "To improve, you should "]
           : ["To build on this, "+fn+" should ", "The next step for "+fn+" is to ", "To improve, "+fn+" should "],
    seed, 3);
  const stepLead = scored.length ? stepLead0 : noStrength;
  const alsoStep = second ? "It would also help to " : "It would also help "+P.obj+" to ";
  const thirdStep = "Beyond that, the aim is to ";

  /* How much of the task was actually attempted. Name only the parts that
     really hold unattempted questions — attributing the whole count to the
     single worst part misreports the student's work. */
  const tl = tally(st);
  const shortPart = id => ((PARTS.find(pt => pt.id === id) || {}).name || "").split(" · ")[0];
  const hitParts = PARTS.filter(pt => tl.byPart[pt.id] > 0).map(pt => pt.id);
  const whereList = hitParts.length
    ? (hitParts.length === 1 ? shortPart(hitParts[0])
       : "Parts " + joinList(hitParts.map(id => shortPart(id).replace(/^Part /, ""))))
    : "";
  let completion = "";
  if(tl.notAtt === 0){
    completion = second ? "You attempted every "+NOUN.item+" on the "+NOUN.task+"."
                        : fn + " attempted every "+NOUN.item+" on the "+NOUN.task+".";
  } else if(tl.notAtt <= 3){
    completion = (second ? "You left " : fn + " left ") + tl.notAtt + " "
      + (tl.notAtt===1 ? NOUN.item : NOUN.items) + " unattempted"
      + (whereList ? (hitParts.length === 1 ? " in " : " across ") + whereList : "")
      + ", so there is little evidence to mark there.";
  } else {
    const share = Math.round(tl.notAtt / tl.total * 100);
    const dominant = hitParts.length > 1 && tl.worstPart && tl.byPart[tl.worstPart] * 2 > tl.notAtt;
    const where = hitParts.length === 1 ? ", all of them in " + whereList
                : dominant ? ", most of them in " + shortPart(tl.worstPart)
                : whereList ? ", spread across " + whereList : "";
    completion = tl.notAtt + " of the " + tl.total + " " + NOUN.items + " were left unattempted"
      + where + " — about " + share + "% of the " + NOUN.task + ". "
      + "Attempting those " + NOUN.items + " is the single quickest way to lift this result, because an unanswered "
      + NOUN.item + " cannot show what " + (second ? "you know." : fn + " knows.");
  }

  const nSteps = Math.min(parseInt(state.opts.steps,10) || 2, byLow.length);
  const steps = byLow.slice(0, nSteps).map(nextOf).filter(Boolean);
  const stepPara = () => {
    if(!steps.length) return "";
    let t = stepLead + steps[0] + ".";
    if(steps[1]) t += " " + alsoStep + steps[1] + ".";
    if(steps[2]) t += " " + thirdStep + steps[2] + ".";
    return t;
  };

  const out = [];

  if(state.opts.length === "brief"){
    out.push(opening + (tl.notAtt > 3 ? " " + completion : ""));
    out.push((byHigh.length ? strengthLead + canOf(byHigh[0]) + ". " : "")
             + stepLead + (steps[0] || "") + ".");
  }
  else if(state.opts.length === "detailed"){
    out.push(opening);
    const lines = STRANDS.filter(s => Number.isInteger(st.marks[s.id])).map(s => {
      const b = st.marks[s.id];
      const label = b === 0 ? state.band0 : state.bandLabels[b-1];
      return "• " + s.name + " — " + label
        + (b === 0 ? ": the next thing to do is " + nextOf(s) + "."
                   : ": " + (second ? "you can " : P.sub+" can ") + canOf(s) + ".");
    });
    out.push(lines.join("\n"));
    out.push(completion);
    const sp2 = stepPara(); if(sp2) out.push(sp2);
  }
  else { // standard
    out.push(opening);
    const a1 = byHigh[0], a2 = byHigh[1];
    if(a1){
      let strengths = strengthLead + canOf(a1) + ".";
      if(a2 && norm(a2) >= 0.34) strengths += " " + alsoLead + canOf(a2) + ".";
      out.push(strengths);
    }
    out.push(completion);
    const sp3 = stepPara(); if(sp3) out.push(sp3);
  }
  return out.join("\n\n");
}

function regenerate(st, force){
  if(st.edited && !force) return;
  st.comment = buildComment(st);
  st.edited = false;
}
function regenerateAll(force){ state.students.forEach(s => regenerate(s, force)); }

/* ============================ RENDER: setup ============================ */
function renderSetup(){
  $("#f-class").value   = state.meta.cls;
  $("#f-teacher").value = state.meta.teacher;
  $("#f-task").value    = state.meta.task;
  $("#f-date").value    = state.meta.date;
  const bf = $("#bandFields");
  bf.innerHTML = '<label class="field"><span>Band 0</span><input data-band="0" value="'+esc(state.band0)+'"></label>'
    + state.bandLabels.map((l,i) =>
      '<label class="field"><span>Band '+(i+1)+'</span><input data-band="'+(i+1)+'" value="'+esc(l)+'"></label>').join("");
  bf.querySelectorAll("input").forEach(inp => inp.oninput = e => {
    const i = +e.target.dataset.band;
    if(i === 0) state.band0 = e.target.value; else state.bandLabels[i-1] = e.target.value;
    renderGroups(); renderPrint(); renderRef(); renderAnalysis(); persist();   // not renderSetup — that would steal focus
  });
  if(document.activeElement !== $("#f-roll")){
    $("#f-roll").value = state.students.map(s =>
      [s.name, s.pron].filter(Boolean).join(", ")).join("\n");
  }
}

/* "she", "her", "She/her" -> she; "he", "him", "his" -> he; anything else -> they */
function pronOf(v){
  const w = String(v || "").trim().toLowerCase().split(/[^a-z]+/)[0];
  return ["she","her","hers"].includes(w) ? "she" : ["he","him","his"].includes(w) ? "he" : "they";
}
function applyRoll(){
  const lines = $("#f-roll").value.split("\n").map(l => l.trim()).filter(Boolean);
  const old = new Map(state.students.map(s => [s.name.toLowerCase(), s]));
  const next = [];
  lines.forEach(line => {
    const parts = line.split(",").map(p => p.trim());
    const name = parts[0];
    if(!name) return;
    const prev = old.get(name.toLowerCase());
    const st = prev || newStudent(name);
    st.name = name;
    if(parts[1]) st.pron = pronOf(parts[1]);
    recompute(st);
    next.push(st);
  });
  state.students = next;
  regenerateAll(false);
  renderAll(); persist();
  toast(next.length + " student" + (next.length===1?"":"s") + " in the class list");
}

/* ============================ RENDER: mark grid ============================ */
function markedCount(){
  return state.students.reduce((n,st) => n + CRITERIA.filter(c => st.q && st.q[c.id] !== undefined).length, 0);
}
const HEADER_EVERY = 12;   // repeat the column headers every N students

function headRowHTML(){
  // row 1: one cell per booklet question, spanning its sub-parts
  let h = "<tr class='hrow'><th class='stu'>Student</th>";
  let i = 0;
  while(i < MARK_COLS.length){
    const c = CRITERIA[MARK_COLS[i]];
    let n = 1;
    while(i + n < MARK_COLS.length && CRITERIA[MARK_COLS[i+n]].q === c.q) n++;
    const first = i === 0 || CRITERIA[MARK_COLS[i-1]].part !== c.part;
    h += "<th class='q "+partCls(c.part)+(first?" pstart":"")+"' colspan='"+n+"'>"+esc(c.q)+"</th>";
    i += n;
  }
  h += "<th class='totcol' rowspan='2'>Mark</th><th class='bandcol' rowspan='2'>Bands</th><th class='lvlcol' rowspan='2'>Level</th></tr>";
  // row 2: the sub-part, for the questions the rubric splits across bands
  h += "<tr class='srow'><th class='stu'></th>";
  MARK_COLS.forEach((ci,k) => {
    const c = CRITERIA[ci];
    const first = k===0 || CRITERIA[MARK_COLS[k-1]].part !== c.part;
    h += "<th class='qsub "+partCls(c.part)+(first?" pstart":"")+"' title='"+esc(qLabel(c)+" — "+c.label)+"'>"
       + (c.sub ? esc(c.sub) : "<span class='dot'>&middot;</span>")
       + "<span class='qmax'>/"+fmtMark(c.max)+"</span></th>";
  });
  h += "</tr>";
  return h;
}
function partRowHTML(){
  let h = "<tr class='prow'><th class='stu'></th>";
  let i = 0;
  while(i < MARK_COLS.length){
    const pid = CRITERIA[MARK_COLS[i]].part;
    let n = 1;
    while(i + n < MARK_COLS.length && CRITERIA[MARK_COLS[i+n]].part === pid) n++;
    const pt = PARTS.find(p => p.id === pid) || {id:pid, name:pid};
    h += "<th class='pgroup "+partCls(pid)+"' colspan='"+n+"' title='"+esc(pt.name)+"'>"
       + esc(n < 4 ? pt.id : pt.name) + "</th>";
    i += n;
  }
  h += "<th colspan='3'></th></tr>";
  return h;
}

function qinClass(st, c){
  return hasMark(st, c.id) ? (isDone(st, c.id) ? "on" : "low") : (isNotAtt(st, c.id) ? "no" : "");
}
function totHTML(st){
  return started(st) ? "<b>"+fmtMark(rawTotal(st))+"</b><span>/"+MAX_TOTAL+"</span>" : "<span>&middot;</span>";
}
function bandsHTML(st){
  return STRANDS.map(s => {
    const m = st.marks[s.id], r = st.res[s.id] || {};
    const ov = r.overridden;
    const tip = s.name + " — band " + (m===null ? 0 : m)
      + (r.missed ? " (top cell " + r.top + ", " + r.missed + " developing question" + (r.missed===1?"":"s") + " missing)" : "")
      + (ov ? " — overridden" : "");
    return "<span class='bnum b"+(m===null?"nil":m)+(ov?" ov":"")+(r.missed?" pen":"")+"' title='"+esc(tip)+"'>"
           +(m===null?"·":m)+"</span>";
  }).join("");
}
function lvlHTML(st){
  const pct = pctOf(st), lv = overallLevel(pct);
  return "<span class='chip b"+lv.key+"' title='"+esc(lv.name)+"'>"
       + (pct===null?"—":lv.mean.toFixed(1)) + "</span>";
}
/* update everything in the grid that a mark can change, without touching the
   inputs themselves (so focus and the caret survive) */
function refreshSummaries(){
  const t = $("#markTable");
  if(!t) return;
  state.students.forEach((st, ri) => {
    const a = t.querySelector("#tot-"+ri), b = t.querySelector("#bc-"+ri), l = t.querySelector("#lv-"+ri);
    if(a) a.innerHTML = totHTML(st);
    if(b) b.innerHTML = bandsHTML(st);
    if(l) l.innerHTML = lvlHTML(st);
  });
  t.querySelectorAll(".qcell .qin").forEach(inp => {
    const st = state.students[+inp.dataset.r], c = CRITERIA[+inp.dataset.c];
    if(!st || !c || inp.classList.contains("bad")) return;
    inp.className = "qin " + qinClass(st, c);
  });
  updateMarkTally();
}
function updateMarkTally(){
  const n = markedCount();
  const el = $("#tallyMark");
  if(el) el.textContent = state.students.length ? n + "/" + (state.students.length * CRITERIA.length) : "";
}
function renderMast(){
  $("#mastMeta").innerHTML = [
    esc([state.meta.cls, state.meta.teacher].filter(Boolean).join(" · ")) || "Set your class on the Class tab",
    esc(state.meta.date || ""),
    state.students.length ? state.students.length + " students · " + markedCount() + " marks entered" : ""
  ].filter(Boolean).join("<br>");
}

function renderMark(){
  const t = $("#markTable");
  if(!state.students.length){
    t.innerHTML = "";
    $("#markEmpty").innerHTML = '<div class="empty"><strong>No students yet</strong>Add your class list on the Class tab, then come back here to mark.</div>';
    $("#tallyMark").textContent = "";
    renderCritKey();
    return;
  }
  $("#markEmpty").innerHTML = "";

  let h = "<thead>" + partRowHTML() + headRowHTML() + "</thead><tbody>";

  state.students.forEach((st, ri) => {
    if(ri > 0 && ri % HEADER_EVERY === 0) h += headRowHTML().replace("class='hrow'", "class='hrow repeat'");
    h += "<tr class='row'><td class='stu'><span class='nm'>"+esc(st.name)+"</span></td>";
    MARK_COLS.forEach((ci,k) => {
      const c = CRITERIA[ci];
      const first = k===0 || CRITERIA[MARK_COLS[k-1]].part !== c.part;
      const v = hasMark(st, c.id) ? fmtMark(st.q[c.id]) : "";
      h += "<td class='qcell "+partCls(c.part)+(first?" pstart":"")+"'>"
         + "<input type='text' inputmode='decimal' autocomplete='off' spellcheck='false' maxlength='4'"
         + " class='qin "+qinClass(st, c)+"' data-r='"+ri+"' data-c='"+ci+"' value='"+v+"'"
         + " aria-label='"+esc(st.name+" — "+qLabel(c)+" "+c.label+" — out of "+fmtMark(c.max))+"'></td>";
    });
    h += "<td class='totcol' id='tot-"+ri+"'>"+totHTML(st)+"</td>";
    h += "<td class='bandcol' id='bc-"+ri+"'>"+bandsHTML(st)+"</td>";
    h += "<td class='lvlcol' id='lv-"+ri+"'>"+lvlHTML(st)+"</td></tr>";
  });
  h += "</tbody>";
  t.innerHTML = h;

  t.querySelectorAll(".qcell .qin").forEach(inp => {
    inp.oninput = () => enterMark(inp);
    inp.onblur = () => leaveMark(inp);
    inp.onfocus = () => inp.select();
    inp.onkeydown = e => gridKey(e, +inp.dataset.r, +inp.dataset.c);
  });
  updateMarkTally();
  renderCritKey();
}

function renderCritKey(){
  const el = $("#critKey");
  if(!el) return;
  let h = "";
  PARTS.forEach(pt => {
    h += "<div class='ckpart'><h4 class='"+partCls(pt.id)+"'>"+esc(pt.name)+"</h4><ul>";
    CRITERIA.filter(c => c.part === pt.id).forEach(c => {
      const s = c.strand ? strandById(c.strand) : null;
      h += "<li><span class='ckcode'>"+esc(qLabel(c))+"</span> "+esc(c.label)
         + " <span class='ckmax'>("+fmtMark(c.max)+" mark"+(c.max===1?"":"s")+")</span>"
         + (s ? "<span class='ckmap'>&rarr; "+esc(s.code ? s.code + " · " + s.sub : s.sub)+", band "+c.band+"</span>"
              : "<span class='ckmap ckoff'>&rarr; not in the rubric</span>")
         + "</li>";
    });
    h += "</ul></div>";
  });
  el.innerHTML = h;
}

/* Store one mark. value: number, or null / "" for blank. Returns false (and
   stores nothing) when the value is not a half-mark step from 0 to max. */
function setMark(ri, ci, value){
  const st = state.students[ri], c = CRITERIA[ci];
  if(!st || !c) return false;
  const v = (value === null || value === "") ? null
          : typeof value === "number" ? value : parseMark(value, c.max);
  if(Number.isNaN(v) || (typeof v === "number" && Number.isNaN(parseMark(String(v), c.max)))) return false;
  if(v === null) delete st.q[c.id]; else st.q[c.id] = v;
  refreshClass();
  refreshSummaries();
  scheduleHeavy();
  return true;
}
/* typing in a cell: store as soon as it is valid, flag it while it is not */
function enterMark(inp){
  const ri = +inp.dataset.r, ci = +inp.dataset.c, c = CRITERIA[ci];
  const v = parseMark(inp.value, c.max);
  if(Number.isNaN(v)){
    inp.classList.add("bad");
    inp.title = qLabel(c) + " is out of " + fmtMark(c.max) + " — enter 0 to " + fmtMark(c.max) + " in half marks, or leave blank";
    return;
  }
  inp.classList.remove("bad"); inp.title = "";
  setMark(ri, ci, v);
}
/* leaving a cell that still holds an invalid entry puts the stored mark back */
function leaveMark(inp){
  if(!inp.classList.contains("bad")) return;
  const st = state.students[+inp.dataset.r], c = CRITERIA[+inp.dataset.c];
  toast(qLabel(c) + " is out of " + fmtMark(c.max) + " — that entry was not kept");
  inp.value = st && hasMark(st, c.id) ? fmtMark(st.q[c.id]) : "";
  inp.classList.remove("bad"); inp.title = "";
}
let heavyTimer = null;
function scheduleHeavy(){
  clearTimeout(heavyTimer);
  heavyTimer = setTimeout(() => {
    regenerateAll(false);
    renderComments(); renderGroups(); renderPrint(); persist(); renderMast(); renderAnalysis();
  }, 350);
}
function gridKey(e, ri, ci){
  const k = e.key;
  let nr = ri, nc = ci;
  if(k === "ArrowDown") nr = Math.min(ri+1, state.students.length-1);
  else if(k === "ArrowUp") nr = Math.max(ri-1, 0);
  else if(k === "ArrowRight") nc = MARK_COLS[Math.min(MARK_COLS.indexOf(ci)+1, MARK_COLS.length-1)];
  else if(k === "ArrowLeft")  nc = MARK_COLS[Math.max(MARK_COLS.indexOf(ci)-1, 0)];
  else if(k === "Enter") nr = e.shiftKey ? Math.max(ri-1, 0) : Math.min(ri+1, state.students.length-1);
  else return;
  e.preventDefault();
  const el = $("#markTable").querySelector("[data-r='"+nr+"'][data-c='"+nc+"']");
  if(el){ el.focus(); el.scrollIntoView({block:"nearest", inline:"nearest"}); }
}

/* ============================ RENDER: comments ============================ */
function renderComments(){
  const list = $("#cmtList"), pane = $("#cmtPane");
  if(!state.students.length){
    list.innerHTML = "";
    pane.innerHTML = '<div class="empty"><strong>No students yet</strong>Add your class list on the Class tab.</div>';
    return;
  }
  if(!state.students.find(s => s.id === state.ui.cmtSel)) state.ui.cmtSel = state.students[0].id;
  list.innerHTML = state.students.map(s =>
    '<button type="button" data-id="'+s.id+'" aria-pressed="'+(s.id===state.ui.cmtSel)+'">'+esc(firstName(s.name))+(s.edited?" ✎":"")+'</button>').join("");
  list.querySelectorAll("button").forEach(b => b.onclick = () => { state.ui.cmtSel = b.dataset.id; renderComments(); });

  const st = state.students.find(s => s.id === state.ui.cmtSel);
  if(!st.comment) regenerate(st, true);
  pane.innerHTML =
    '<div class="grid2">'
    + '<label class="field"><span>Pronoun</span><select id="c-pron">'
      + ['they','she','he'].map(p => '<option value="'+p+'"'+(p===st.pron?" selected":"")+'>'+p+'</option>').join("")
      + '</select></label>'
    + '</div>'
    + '<div class="field"><span>Bands — worked out from the marks and the developmental penalty; change one only if you disagree</span>'
    + '<div class="ovrow">' + STRANDS.map(sd => {
        const rr = st.res[sd.id] || {}, der = rr.derived, ov = st.override[sd.id];
        const isov = Number.isInteger(ov);
        return '<div class="ovcell'+(isov?' isov':'')+'"><span class="ovname">'+esc(sd.sub)+'</span>'
          + '<select data-ov="'+sd.id+'"><option value="">Auto — '+(rr.assessed ? ('band '+der + (rr.missed ? ' (top '+rr.top+', −'+rr.missed+')' : '')) : 'not assessed')+'</option>'
          + [0,1,2,3,4].filter(b => b <= maxBandOf(sd)).map(b => '<option value="'+b+'"'+(ov===b?' selected':'')+'>Band '+b+(b===0?' — '+state.band0:'')+'</option>').join("")
          + '</select></div>';
      }).join("") + '</div></div>'
    + '<label class="field"><span>Comment for '+esc(st.name)+' '+(st.edited?'<span class="edited-flag">edited by hand</span>':'')+'</span>'
    + '<textarea id="c-text" rows="9">'+esc(st.comment)+'</textarea></label>'
    + '<div class="iobar"><button class="btn ghost small" id="c-regen">Rebuild from marks</button>'
    + '<button class="btn ghost small" id="c-copy">Copy</button></div>';

  pane.querySelectorAll("[data-ov]").forEach(sel => sel.onchange = e => {
    const id = e.target.dataset.ov, v = parseInt(e.target.value,10);
    if(Number.isInteger(v)) st.override[id] = v; else delete st.override[id];
    recompute(st); regenerate(st,false);
    renderMark(); renderComments(); renderGroups(); renderPrint(); persist();
  });
  $("#c-pron").onchange    = e => { st.pron = e.target.value; regenerate(st,false); renderComments(); renderPrint(); persist(); };
  $("#c-text").oninput     = e => { st.comment = e.target.value; st.edited = true; renderPrint(); persist(); };
  $("#c-regen").onclick    = () => { regenerate(st,true); renderComments(); renderPrint(); persist(); toast("Comment rebuilt"); };
  $("#c-copy").onclick     = () => { navigator.clipboard.writeText(st.comment).then(()=>toast("Comment copied")); };
}

/* ============================ RENDER: groups ============================ */
function renderGroups(){
  const sel = $("#f-groupstrand");
  if(sel.options.length !== STRANDS.length){
    sel.innerHTML = STRANDS.map(s => '<option value="'+s.id+'">'+esc(s.name)+'</option>').join("");
  }
  sel.value = state.ui.groupStrand;
  const s = strandById(state.ui.groupStrand);
  const pane = $("#groupPane");
  if(!state.students.length){ pane.innerHTML = '<div class="empty"><strong>No students yet</strong>Add your class list on the Class tab.</div>'; return; }

  const buckets = {0:[],1:[],2:[],3:[],4:[]}, unassessed = [];
  state.students.forEach(st => { const m = st.marks[s.id];
    if(Number.isInteger(m)) buckets[m].push(st.name); else unassessed.push(st.name); });

  let h = '<div class="groupgrid">';
  h += '<div class="groupbox g0"><h4>0 · '+esc(state.band0)+' <span style="font-weight:400">('+buckets[0].length+')</span></h4>';
  h += buckets[0].length ? '<ul>'+buckets[0].map(n=>'<li>'+esc(n)+'</li>').join("")+'</ul>' : '<div class="none">Nobody here</div>';
  h += '<div class="nextline"><strong>Teach next:</strong> '+esc(plain(s.start).charAt(0).toUpperCase()+plain(s.start).slice(1))+'.</div></div>';
  for(let b=1;b<=maxBandOf(s);b++){
    if(!EV[s.id][b].length) continue;
    h += '<div class="groupbox g'+b+'"><h4>'+b+' · '+esc(state.bandLabels[b-1])+' <span style="font-weight:400">('+buckets[b].length+')</span></h4>';
    h += buckets[b].length ? '<ul>'+buckets[b].map(n=>'<li>'+esc(n)+'</li>').join("")+'</ul>' : '<div class="none">Nobody here</div>';
    const nx = plain(s.next[b-1]);
    h += '<div class="nextline"><strong>Teach next:</strong> '+esc(nx ? nx.charAt(0).toUpperCase()+nx.slice(1)+"." : "—")+'</div></div>';
  }
  if(unassessed.length){
    h += '<div class="groupbox gnil"><h4>Not assessed ('+unassessed.length+')</h4><ul>'+unassessed.map(n=>'<li>'+esc(n)+'</li>').join("")+'</ul></div>';
  }
  h += '</div>';
  pane.innerHTML = h;
}

/* ============================ RENDER: print ============================ */
function pips(b, max){
  let out = "";
  for(let i=1;i<=max;i++) out += '<span class="pip'+(i<=b?" on":"")+'" aria-hidden="true"></span>';
  return out + '<span class="sr">band '+b+' of '+max+'</span>';
}
function renderPrint(){
  const who = $("#f-printwho");
  const cur = who.value;
  who.innerHTML = '<option value="all">All students</option>' + state.students.map(s => '<option value="'+s.id+'">'+esc(s.name)+'</option>').join("");
  who.value = [...who.options].some(o=>o.value===cur) ? cur : "all";

  const pane = $("#printPane");
  const what = $("#f-printwhat").value;
  const scale = parseFloat($("#f-printsize").value) || 1;

  if(what === "groups"){ pane.innerHTML = groupSheetHTML(scale); return; }
  if(!state.students.length){ pane.innerHTML = '<div class="empty"><strong>Nothing to print yet</strong>Add students and mark them first.</div>'; return; }

  const list = who.value === "all" ? state.students : state.students.filter(s => s.id === who.value);
  pane.innerHTML = list.map(st => sheetHTML(st, what !== "rubriconly", scale)).join("");
}

function sheetHTML(st, withComment, scale){
  const pct = pctOf(st), lv = overallLevel(pct);
  const m = state.meta;
  let h = '<div class="sheet" style="font-size:'+(9.2*scale).toFixed(2)+'pt">';

  h += '<div class="sheet-head"><div>'
     + '<div class="t-eyebrow">'+esc(R.eyebrow)+'</div>'
     + '<h2>'+esc(m.task || R.task)+'</h2>'
     + '<div class="t-sub">Marking rubric &amp; feedback</div>'
     + '</div><div class="who"><span class="nm">'+esc(st.name)+'</span>'

     + esc([m.cls, m.teacher].filter(Boolean).join(" · "))
     + (m.date ? '<br>'+esc(m.date) : '')
     + '</div></div>';

  h += '<table class="rub"><thead><tr><th class="hstrand">Strand</th>'
     + '<th class="hzero">0 &middot; '+esc(state.band0)+'</th>'
     + state.bandLabels.map((l,i) => '<th>'+(i+1)+' &middot; '+esc(l)+'</th>').join("")
     + '</tr></thead><tbody>';

  STRANDS.forEach(s => {
    const r = st.res[s.id] || {};
    /* On a printed report there is no such thing as an unmarked strand:
       teachers tick what was achieved and leave the rest blank, so blank
       is band 0 — not demonstrated. */
    const awarded = Number.isInteger(st.marks[s.id]) ? st.marks[s.id] : 0;
    h += '<tr><td class="strand">'+esc(s.name)+'<span class="sub">'+esc(s.sub)+'</span>'
       + (r.missed ? '<span class="pen">&minus;'+r.missed+' band'+(r.missed===1?'':'s')+' for missing developing skills</span>' : '')
       + '</td>';

    // band 0 column
    const zeroHit = awarded === 0;
    h += '<td class="'+(zeroHit ? 'hit b0 awarded' : 'off')+'">Has not yet demonstrated the skills in this row.'
       + (zeroHit ? '<span class="award">Awarded</span>' : '')
       + '</td>';

    for(let bd=1;bd<=4;bd++){
      const band = s.bands[bd-1];
      if(bd > maxBandOf(s) || !EV[s.id][bd].length){ h += '<td class="na">No '+esc(NOUN.item)+' in this '+esc(NOUN.task)+'.</td>'; continue; }
      const met = cellMet(st, s, bd);
      const isAward = awarded === bd;
      const cls = (met ? 'hit b'+bd : 'off') + (isAward ? ' awarded' : '');
      h += '<td class="'+cls+'">'
         + '<span class="qc">'+esc(band.q)+'</span> ' + esc(band.d)
         + '<span class="cellfoot">'
         +   '<span class="cbx '+(met ? 'on' : 'no')+'"></span>'
         +   '<span class="cbxlab">'+(met ? 'demonstrated' : 'not demonstrated')+'</span>'
         +   (isAward ? '<span class="award">Awarded</span>' : '')
         + '</span></td>';
    }
    h += '</tr>';
  });
  h += '</tbody></table>';
  h += '<div class="rubkey">A shaded cell has been demonstrated. A red cross marks a developing skill that has not been, and each missing question below the highest shaded cell lowers the awarded band by one.</div>';

  // questions completed / attempted but not successful / not attempted
  const codes = [];
  CRITERIA.forEach(c => {
    let e = codes.find(x => x.code === c.q);
    if(!e){ e = {code:c.q, ids:[]}; codes.push(e); }
    e.ids.push(c.id);
  });
  const gDone = [], gPart = [], gNot = [];
  codes.forEach(c => {
    if(c.ids.some(id => isNotAtt(st,id))) gNot.push(c.code);
    else if(c.ids.every(id => isDone(st,id))) gDone.push(c.code);
    else gPart.push(c.code);
  });
  const grp = (lab, arr, cls) => arr.length
    ? '<span class="evgrp"><span class="evlab">'+lab+'</span>'
      + arr.map(c => '<span class="ev '+cls+'">'+esc(c)+'</span>').join("") + '</span>' : "";
  h += '<div class="evbar">'
     + grp("Questions completed", gDone, "all")
     + grp("Attempted, not yet successful", gPart, "part")
     + grp("Not attempted", gNot, "no")
     + '</div>';

  const cmt = (st.comment || "").split(/\n{2,}/).filter(Boolean);
  h += '<div class="cbox keep"><h3>Feedback</h3>'
     + (withComment && cmt.length ? cmt.map(pp => '<p>'+esc(pp).replace(/\n/g,"<br>")+'</p>').join("")
        : '<p class="wline">&nbsp;</p><p class="wline">&nbsp;</p><p class="wline">&nbsp;</p><p class="wline">&nbsp;</p>')
     + '</div>';

  const tl = tally(st);
  h += '<div class="overallbar">'
     + '<span class="olab">Overall</span>'
     + '<span class="olvl b'+(lv.key < 0 ? "nil" : lv.key)+'">'+esc(lv.name)+'</span>'
     + (pct===null ? '' : '<span class="omean">mean band '+lv.mean.toFixed(1)+' of 4</span>')
     + '<span class="omean">'+fmtMark(tl.score)+' / '+tl.outOf+' marks'
     + (tl.notAtt ? ' &middot; '+tl.notAtt+' not attempted' : '')+'</span>'
     + '<span class="ofoot">'+esc([m.cls, m.teacher].filter(Boolean).join(" · "))+'</span>'
     + '</div>';

  h += '</div>';
  return h;
}

function groupSheetHTML(scale){
  if(!state.students.length) return '<div class="empty"><strong>Nothing to print yet</strong>Add students and mark them first.</div>';
  const m = state.meta;
  let h = '<div class="sheet groupsheet" style="font-size:'+(9.2*scale).toFixed(2)+'pt">';
  h += '<div class="sheet-head"><div><div class="t-eyebrow">'+esc((R.context ? R.context + " · " : "") + (m.task || R.task))+'</div>'
     + '<h2>Teaching groups</h2><div class="t-sub">Who sits where, and what each group needs next</div></div>'
     + '<div class="who"><span class="nm">'+esc(m.cls||"Class")+'</span>'+esc(m.teacher||"")+(m.date?'<br>'+esc(m.date):'')+'</div></div>';

  STRANDS.forEach(s => {
    const buckets = {0:[],1:[],2:[],3:[],4:[]};
    state.students.forEach(st => { const b = st.marks[s.id];
      buckets[Number.isInteger(b) ? b : 0].push(firstName(st.name)); });
    h += '<div class="gs-strand"><h3>'+esc(s.name)+'</h3><div class="gs-bands">';
    h += '<div class="gs-band b0"><span class="bh">0 · '+esc(state.band0)+'</span>'
       + (buckets[0].length ? esc(buckets[0].join(", ")) : '<span style="opacity:.5">—</span>')
       + '<span class="teach">Next: '+esc(plain(s.start))+'</span></div>';
    for(let b=1;b<=4;b++){
      if(b > maxBandOf(s) || !EV[s.id][b].length){ h += '<div class="gs-band na">No '+esc(NOUN.item)+' in this '+esc(NOUN.task)+'.</div>'; continue; }
      h += '<div class="gs-band b'+b+'"><span class="bh">'+b+' · '+esc(state.bandLabels[b-1])+'</span>'
         + (buckets[b].length ? esc(buckets[b].join(", ")) : '<span style="opacity:.5">—</span>')
         + '<span class="teach">Next: '+esc(plain(s.next[b-1])||"—")+'</span></div>';
    }
    h += '</div></div>';
  });
  h += '</div>';
  return h;
}

/* ============================ RENDER: reference ============================ */
function renderRef(){
  let h = '<thead><tr><th>Strand</th><th>0 · '+esc(state.band0)+'</th>'
        + state.bandLabels.map((l,i)=>'<th>'+(i+1)+' · '+esc(l)+'</th>').join("") + '</tr></thead><tbody>';
  STRANDS.forEach(s => {
    h += '<tr><td class="sname">'+esc(s.name)+(s.code ? '<span class="code">'+esc(s.code)+'</span>' : '')+'</td>'
       + '<td class="b0cell">Has not yet demonstrated the skills in this row.'
       + '<span class="startby">Start by: '+esc(plain(s.start))+'</span></td>';
    for(let b=1;b<=4;b++){
      const band = s.bands[b-1];
      if(b > maxBandOf(s) || !EV[s.id][b].length){ h += '<td class="na">No '+esc(NOUN.item)+' in this '+esc(NOUN.task)+'.</td>'; continue; }
      h += '<td><span class="qc">'+esc(band.q)+'</span>'+esc(band.d)+'</td>';
    }
    h += '</tr>';
  });
  h += '</tbody>';
  $("#refTable").innerHTML = h;
  /* curriculum credit, e.g. VCAA's CC BY-NC line when strands quote the
     Victorian Curriculum (tools/rubric-builder.html adds it) */
  const at = $("#refAttribution");
  if(at) at.textContent = R.attribution || "";
}

/* ============================ RENDER: all ============================ */
/* ============================ RENDER: analysis ============================ */
let anSort = "paper";
const pct = (n, d) => d ? Math.round(100 * n / d) : 0;
const median = a => { if(!a.length) return null; const s = [...a].sort((x,y)=>x-y), m = s.length >> 1;
  return s.length % 2 ? s[m] : (s[m-1] + s[m]) / 2; };
const round1 = v => Math.round(v * 10) / 10;

/* one row per criterion, over the students who have been marked */
function questionStats(marked){
  return CRITERIA.map((c, ci) => {
    const colOn = COLS_MARKED.has(c.id);
    let sum = 0, done = 0, na = 0, entered = 0;
    marked.forEach(st => {
      if(hasMark(st, c.id)){ sum += st.q[c.id]; entered++; }
      if(isDone(st, c.id)) done++;
      if(isNotAtt(st, c.id)) na++;
    });
    const n = marked.length;
    return {c, ci, colOn, n, entered, na, mean: n ? sum / n : 0,
            fac: colOn && n ? sum / (n * c.max) : null,
            donePct: colOn ? pct(done, n) : null, naPct: colOn ? pct(na, n) : null};
  });
}

function anTile(k, v, s){
  return '<div class="an-tile"><div class="k">'+k+'</div><div class="v">'+v+'</div>'+(s ? '<div class="s">'+s+'</div>' : '')+'</div>';
}

/* Spread of totals in ten bins (fewer for a short task). Bin width is a whole
   number of marks; the last bin is closed so a full-marks total has a home.
   Space: 50 marks -> ten bins of five, 0–4 ... 45–50. */
const HIST_W = Math.max(1, Math.ceil(MAX_TOTAL / 10));
const HIST_N = Math.max(1, Math.ceil(MAX_TOTAL / HIST_W));
function histSVG(totals){
  const bins = Array.from({length:HIST_N}, (_, i) => ({lo:i*HIST_W, names:[]}));
  totals.forEach(t => bins[Math.min(HIST_N-1, Math.floor(t.v / HIST_W))].names.push(t.name + " (" + fmtMark(t.v) + ")"));
  const W = 720, H = 230, L = 14, R = 14, T = 26, B = 34;
  const bw = (W - L - R) / HIST_N, max = Math.max(1, ...bins.map(b => b.names.length));
  const y = v => T + (H - T - B) * (1 - v / max);
  let h = '<svg class="an-hist" viewBox="0 0 '+W+' '+H+'" role="img" aria-label="Number of students in each '+HIST_W+'-mark band of the total score">';
  bins.forEach((b, i) => {
    const x = L + i * bw + 1, w = bw - 2, n = b.names.length, y0 = H - B;
    const hi = i === HIST_N-1 ? MAX_TOTAL : b.lo + HIST_W - 1;
    const lab = hi > b.lo ? b.lo + "–" + fmtMark(hi) : String(b.lo);
    const tip = '<b>' + lab + ' marks · ' + n + ' student' + (n===1?'':'s') + '</b>' + esc(b.names.join(", "));
    if(n){
      const yt = y(n), r = Math.min(4, (y0 - yt) / 2);
      /* rounded data-end at the top, square at the baseline */
      h += '<path class="bar" d="M'+x+','+y0+' V'+(yt+r)+' Q'+x+','+yt+' '+(x+r)+','+yt+' H'+(x+w-r)+' Q'+(x+w)+','+yt+' '+(x+w)+','+(yt+r)+' V'+y0+' Z"/>';
      h += '<text class="cnt" x="'+(x+w/2)+'" y="'+(yt-6)+'" text-anchor="middle">'+n+'</text>';
    }
    h += '<rect class="hit" x="'+(x-1)+'" y="'+T+'" width="'+(w+2)+'" height="'+(H-T-B)+'" data-tip="'+esc(tip)+'" tabindex="0" aria-label="'+esc(lab+" marks: "+n+" students")+'"/>';
    h += '<text x="'+(x+w/2)+'" y="'+(H-B+16)+'" text-anchor="middle">'+lab+'</text>';
  });
  h += '<line class="base" x1="'+L+'" x2="'+(W-R)+'" y1="'+(H-B)+'" y2="'+(H-B)+'"/>';
  if(totals.length){
    const mean = totals.reduce((a,t) => a + t.v, 0) / totals.length;
    const mx = L + (W - L - R) * Math.min(mean, MAX_TOTAL) / MAX_TOTAL;
    h += '<line class="mean" x1="'+mx+'" x2="'+mx+'" y1="'+(T-12)+'" y2="'+(H-B)+'"/>';
    const anchor = mx > W - 120 ? "end" : "start", dx = anchor === "end" ? -5 : 5;
    h += '<text class="meanlab" x="'+(mx+dx)+'" y="'+(T-4)+'" text-anchor="'+anchor+'">class mean '+round1(mean)+'</text>';
  }
  h += '<text x="'+(W/2)+'" y="'+(H-2)+'" text-anchor="middle">Total mark out of '+fmtMark(MAX_TOTAL)+'</text>';
  return h + '</svg>';
}

function bandLabel(b){ return b === 0 ? state.band0 : state.bandLabels[b-1]; }

function stackRow(name, sub, counts, names, maxB, meanTxt){
  const n = counts.reduce((a,b) => a + b, 0);
  let bar = '<div class="an-stack">';
  counts.forEach((k, b) => {
    if(b > maxB || !k) return;
    const tip = '<b>Band ' + b + ' · ' + esc(bandLabel(b)) + ' — ' + k + ' of ' + n + '</b>' + esc(names[b].join(", "));
    bar += '<div class="seg c'+b+'" style="flex:'+k+' 1 0" data-tip="'+esc(tip)+'" tabindex="0" aria-label="'
         + esc(name+", band "+b+": "+k+" students")+'">'+k+'</div>';
  });
  bar += '</div>';
  return '<div class="nm">'+esc(name)+(sub ? '<small>'+esc(sub)+'</small>' : '')+'</div>'+bar
       + '<div class="mb">'+meanTxt+'</div>';
}

function renderAnalysis(){
  const pane = $("#anPane");
  if(!pane) return;
  const all = state.students, marked = all.filter(started);
  if(!marked.length){
    pane.innerHTML = '<div class="empty"><strong>Nothing to analyse yet</strong>Enter marks on the Mark tab and the class picture builds here as you go.</div>';
    return;
  }
  const qs = questionStats(marked);
  const live = qs.filter(r => r.colOn);
  const unmarkedCols = qs.length - live.length;
  const totals = marked.map(st => ({name: st.name, v: rawTotal(st)}));
  const vals = totals.map(t => t.v);
  const mean = vals.reduce((a,b) => a + b, 0) / vals.length;
  const naCells = live.reduce((a, r) => a + r.na, 0);
  const naOf = live.length * marked.length;

  let h = '<div class="an-print-title">'+esc(state.meta.task || R.task)+' — class analysis'
        + (state.meta.cls ? ' · '+esc(state.meta.cls) : '')+'</div>';
  if(marked.length < all.length || unmarkedCols){
    h += '<div class="an-note">'
       + (marked.length < all.length ? (all.length - marked.length) + ' of ' + all.length + ' students have no marks yet and are left out. ' : '')
       + (unmarkedCols ? unmarkedCols + ' of ' + qs.length + ' columns have no marks for anyone yet, so totals are not final.' : '')
       + '</div>';
  }
  h += '<div class="an-tiles">'
     + anTile("Students marked", marked.length, "of " + all.length + " in the class")
     + anTile("Class mean", round1(mean) + "<span style='font-size:14px;color:var(--ink-faint)'> / "+MAX_TOTAL+"</span>", pct(mean, MAX_TOTAL) + "% of the marks")
     + anTile("Median", fmtMark(median(vals)), "half the class at or above this")
     + anTile("Range", fmtMark(Math.min(...vals)) + "–" + fmtMark(Math.max(...vals)), "lowest to highest total")
     + anTile("Not attempted", pct(naCells, naOf) + "%", naCells + " part" + (naCells===1?"":"s") + " left blank across the class")
     + '</div>';

  h += '<div class="an-sec"><h3>Spread of total marks</h3>'
     + '<p class="an-sub">How many students landed in each '+(HIST_W===1 ? 'mark' : HIST_W+'-mark band')+'. Hover or focus a bar to see who is in it.</p>'
     + histSVG(totals) + '</div>';

  /* ---- strands ---- */
  h += '<div class="an-sec"><h3>Bands by strand</h3>'
     + '<p class="an-sub">Where the class sits on each strand of the rubric, after the developmental penalty. Strands with a weak first band are the ones to reteach from the start.</p>'
     + '<div class="an-legend">' + [0,1,2,3,4].map(b => '<span><i class="c'+b+'"></i>'+b+' · '+esc(bandLabel(b))+'</span>').join("") + '</div>'
     + '<div class="an-rows">';
  const tableRows = [];
  STRANDS.forEach(s => {
    const counts = [0,0,0,0,0], names = [[],[],[],[],[]];
    let sum = 0, n = 0;
    marked.forEach(st => { const m = st.marks[s.id]; if(Number.isInteger(m)){ counts[m]++; names[m].push(st.name); sum += m; n++; } });
    const meanB = n ? round1(sum / n) : null;
    h += stackRow(s.name, s.sub + " · " + s.weight + " marks", counts, names, maxBandOf(s),
                  meanB === null ? "—" : "<b>" + meanB + "</b> / " + maxBandOf(s));
    tableRows.push([s.name, counts, maxBandOf(s), meanB]);
  });
  /* overall level, on the same 0–4 scale */
  const oc = [0,0,0,0,0], on = [[],[],[],[],[]];
  marked.forEach(st => { const lv = overallLevel(pctOf(st)); if(lv.key >= 0){ oc[lv.key]++; on[lv.key].push(st.name); } });
  h += '<div class="sep"></div>' + stackRow("Overall level", "weighted by each strand's marks", oc, on, 4, "");
  tableRows.push(["Overall level", oc, 4, null]);
  h += '</div>';
  h += '<details class="an-table"><summary>Show as a table</summary><table class="an-t"><thead><tr><th>Strand</th>'
     + [0,1,2,3,4].map(b => '<th class="n">Band '+b+'</th>').join("") + '<th class="n">Mean</th></tr></thead><tbody>'
     + tableRows.map(r => '<tr><td>'+esc(r[0])+'</td>' + r[1].map((k,b) => '<td class="n">'+(b > r[2] ? '—' : k)+'</td>').join("")
       + '<td class="n">'+(r[3] === null ? '' : r[3] + ' / ' + r[2])+'</td></tr>').join("")
     + '</tbody></table></details></div>';

  /* ---- questions ---- */
  const rows = anSort === "low"
    ? [...qs].sort((a,b) => (a.fac === null) - (b.fac === null) || (a.fac||0) - (b.fac||0))
    : MARK_COLS.map(ci => qs[ci]);
  h += '<div class="an-sec"><h3>'+esc(NOUN.item.charAt(0).toUpperCase()+NOUN.item.slice(1))+' by '+esc(NOUN.item)+'</h3>'
     + '<p class="an-sub"><b>Facility</b> is the share of the available marks the class earned (a blank counts as 0); the dashed line is half. '
     + '<b>Demonstrated</b> is how many scored at least half, which is what counts towards a band. '
     + 'Parts under 50% facility are flagged to reteach; parts a quarter or more of the class skipped are flagged as skipped.</p>'
     + '<div class="an-sort" role="group" aria-label="Sort questions">'
     + '<button type="button" data-sort="paper" aria-pressed="'+(anSort==="paper")+'">'+esc(NOUN.task.charAt(0).toUpperCase()+NOUN.task.slice(1))+' order</button>'
     + '<button type="button" data-sort="low" aria-pressed="'+(anSort==="low")+'">Lowest facility first</button></div>'
     + '<div class="an-tablewrap"><table class="an-t"><thead><tr><th>Part</th><th>Question</th><th>What it asks for</th>'
     + '<th class="n">Out of</th><th class="n">Mean</th><th>Facility</th><th class="n">Demonstrated</th><th class="n">Not attempted</th><th>Flag</th></tr></thead><tbody>';
  let prevPart = null;
  rows.forEach(r => {
    const c = r.c, brk = anSort === "paper" && prevPart !== null && prevPart !== c.part;
    prevPart = c.part;
    if(!r.colOn){
      h += '<tr'+(brk?' class="pstart"':'')+'><td>'+esc(c.part)+'</td><td class="q">'+esc(qLabel(c))+'</td><td class="lab">'+esc(c.label)+'</td>'
         + '<td class="n">'+fmtMark(c.max)+'</td><td colspan="5" style="color:var(--ink-faint)">Not marked yet</td></tr>';
      return;
    }
    const f = Math.round(r.fac * 100);
    const flags = (f < 50 ? '<span class="an-flag re">Reteach</span>' : '') + (r.naPct >= 25 ? '<span class="an-flag sk">Often skipped</span>' : '');
    h += '<tr'+(brk?' class="pstart"':'')+'><td>'+esc(c.part)+'</td><td class="q">'+esc(qLabel(c))+'</td><td class="lab">'+esc(c.label)+'</td>'
       + '<td class="n">'+fmtMark(c.max)+'</td><td class="n">'+round1(r.mean)+'</td>'
       + '<td><div class="an-fac" data-tip="'+esc('<b>'+qLabel(c)+' · '+f+'% facility</b>Mean '+round1(r.mean)+' of '+fmtMark(c.max)+' across '+r.n+' students')+'">'
       + '<span class="track"><span class="fill" style="width:'+f+'%"></span><span class="half"></span></span><b>'+f+'%</b></div></td>'
       + '<td class="n">'+r.donePct+'%</td><td class="n">'+r.naPct+'%</td><td>'+flags+'</td></tr>';
  });
  h += '</tbody></table></div></div>';

  pane.innerHTML = h;
  pane.querySelectorAll(".an-sort button").forEach(b => b.onclick = () => { anSort = b.dataset.sort; renderAnalysis(); });
}

function exportAnalysisCSV(){
  const marked = state.students.filter(started);
  const qs = questionStats(marked);
  const head = ["Question","Part","What it asks for","Out of","Students marked","Mean","Facility %","Demonstrated %","Not attempted %"];
  const lines = [head.map(csvCell).join(",")];
  MARK_COLS.forEach(ci => { const r = qs[ci], c = r.c;
    lines.push([qLabel(c), c.part, c.label, fmtMark(c.max), r.n,
      r.colOn ? round1(r.mean) : "", r.colOn ? Math.round(r.fac*100) : "", r.colOn ? r.donePct : "", r.colOn ? r.naPct : ""].map(csvCell).join(","));
  });
  download((state.meta.cls||"class")+"-"+R.fileStem+"-analysis-"+stamp()+".csv", lines.join("\n"), "text/csv;charset=utf-8");
  toast("Question analysis downloaded");
}

/* one floating tooltip for every [data-tip] in the analysis tab, on hover and on focus */
function wireAnalysisTip(){
  const tip = document.createElement("div"); tip.id = "anTip"; tip.setAttribute("role", "tooltip");
  document.body.appendChild(tip);
  const show = (el, x, y) => { tip.innerHTML = el.getAttribute("data-tip"); tip.style.display = "block";
    const r = tip.getBoundingClientRect();
    tip.style.left = Math.max(8, Math.min(window.innerWidth - r.width - 8, x + 12)) + "px";
    tip.style.top  = Math.max(8, (y + 16 + r.height > window.innerHeight ? y - r.height - 12 : y + 16)) + "px"; };
  const hide = () => { tip.style.display = "none"; };
  document.addEventListener("mousemove", e => {
    const el = e.target.closest && e.target.closest("#anPane [data-tip]");
    if(el) show(el, e.clientX, e.clientY); else hide();
  });
  document.addEventListener("focusin", e => {
    const el = e.target.closest && e.target.closest("#anPane [data-tip]");
    if(el){ const r = el.getBoundingClientRect(); show(el, r.left + r.width/2, r.bottom); } else hide();
  });
  document.addEventListener("scroll", hide, true);
}

function renderAll(){
  refreshClass();
  renderMast();
  renderSetup(); renderMark(); renderComments(); renderGroups(); renderPrint(); renderRef(); renderAnalysis();
}

/* ============================ TABS ============================ */
function showTab(id){
  state.ui.tab = id;
  $$(".tab").forEach(t => t.setAttribute("aria-selected", String(t.dataset.panel === id)));
  $$(".panel").forEach(p => p.classList.toggle("on", p.id === "p-"+id));
  window.scrollTo({top:0, behavior:"instant"});
}

/* ============================ FILE IO ============================ */
function download(name, text, type){
  const b = new Blob([text], {type: type || "text/plain;charset=utf-8"});
  const u = URL.createObjectURL(b);
  const a = document.createElement("a"); a.href = u; a.download = name; a.click();
  setTimeout(()=>URL.revokeObjectURL(u), 1500);
}
function stamp(){
  const d = new Date();
  return d.getFullYear()+"-"+String(d.getMonth()+1).padStart(2,"0")+"-"+String(d.getDate()).padStart(2,"0");
}
function saveJSON(){
  const payload = saveData();
  payload.criteria = CRITERIA.map(c => qLabel(c));
  download((state.meta.cls||"class")+"-"+R.fileStem+"-rubric-"+stamp()+".json", JSON.stringify(payload,null,2), "application/json");
  toast("File saved to your downloads");
}
function csvCell(v){ const s = String(v==null?"":v); return /[",\n]/.test(s) ? '"'+s.replace(/"/g,'""')+'"' : s; }
function exportCSV(blank){
  const head = ["Name","Pronoun",
    ...CRITERIA.map(c => qLabel(c) + " /" + fmtMark(c.max)),
    ...STRANDS.map(s => "Override " + s.id),
    "Comment"];
  const rows = [head.map(csvCell).join(",")];
  const src = state.students.length ? state.students : [newStudent("")];
  src.forEach(st => rows.push([
    csvCell(st.name), csvCell(st.pron),
    ...CRITERIA.map(c => blank || !hasMark(st,c.id) ? "" : fmtMark(st.q[c.id])),
    ...STRANDS.map(s => blank ? "" : (Number.isInteger(st.override[s.id]) ? st.override[s.id] : "")),
    csvCell(blank ? "" : st.comment)
  ].join(",")));
  download((state.meta.cls||"class")+"-"+R.fileStem+"-marks"+(blank?"-template":"")+"-"+stamp()+".csv", rows.join("\n"), "text/csv;charset=utf-8");
  toast(blank ? "Template downloaded" : "CSV exported");
}
const TRUEY = v => /^(1|y|yes|t|true|✓|✔|done|p)$/i.test(String(v||"").trim());
function parseCSV(text){
  const rows = []; let row = [], cell = "", q = false;
  for(let i=0;i<text.length;i++){
    const c = text[i];
    if(q){
      if(c === '"' && text[i+1] === '"'){ cell += '"'; i++; }
      else if(c === '"') q = false;
      else cell += c;
    } else {
      if(c === '"') q = true;
      else if(c === ","){ row.push(cell); cell = ""; }
      else if(c === "\n"){ row.push(cell); rows.push(row); row = []; cell = ""; }
      else if(c !== "\r") cell += c;
    }
  }
  row.push(cell); if(row.length > 1 || row[0] !== "") rows.push(row);
  return rows;
}
function importCSV(text){
  const rows = parseCSV(text).filter(r => r.some(c => c.trim() !== ""));
  if(!rows.length){ toast("That file has no rows"); return; }
  const head = rows[0].map(h => h.trim().toLowerCase());
  const find = pred => head.findIndex(pred);
  const idxName = find(h => h.startsWith("name"));
  const idxPr   = find(h => h.startsWith("pronoun"));
  const idxCm   = find(h => h.startsWith("comment"));
  const norm = t => String(t||"").toLowerCase().replace(/[^a-z0-9]/g,"");
  const headN = head.map(norm);
  /* A column headed with an id from an older numbering still lands on the
     criterion it was renamed to (save.migrations). */
  const backMap = {};
  Object.keys(MIGRATIONS).forEach(v => Object.keys(MIGRATIONS[v]).forEach(old => {
    const now = migrateTicks({[old]: 1}, +v);
    Object.keys(now).forEach(id => { (backMap[id] = backMap[id] || []).push(old); });
  }));
  const idxQ = CRITERIA.map(c => {
    const want = [norm(qLabel(c) + " /" + fmtMark(c.max)), norm(qLabel(c)), norm(c.id)];
    (backMap[c.id] || []).forEach(o => want.push(norm(o)));
    for(const w of want){ const i = headN.indexOf(w); if(i >= 0) return i; }
    return -1;
  });
  const idxOv   = STRANDS.map(s => find(h => h === "override "+s.id || h.startsWith(s.id+" ") || h === s.id));
  if(idxName < 0){ toast("The file needs a Name column"); return; }
  const anyQ = idxQ.some(i => i >= 0);
  const out = [], badCells = [];
  rows.slice(1).forEach(r => {
    const name = (r[idxName]||"").trim(); if(!name) return;
    const st = newStudent(name, idxPr >= 0 ? pronOf(r[idxPr]) : "they");
    CRITERIA.forEach((c,i) => {
      if(idxQ[i] < 0) return;
      const raw = String(r[idxQ[i]]||"").trim();
      if(/^(x|n|no|na|blank|not attempted|-)$/i.test(raw)) return;
      const v = parseMark(raw, c.max);
      if(typeof v === "number" && !Number.isNaN(v)) st.q[c.id] = v;   /* NaN is a number too */
      else if(TRUEY(raw)) st.q[c.id] = c.max;
      else if(Number.isNaN(v)) badCells.push(name + " " + qLabel(c) + " (" + raw + ")");
    });
    STRANDS.forEach((sd,i) => {
      const v = idxOv[i] >= 0 ? parseInt((r[idxOv[i]]||"").trim(),10) : NaN;
      if(v >= 0 && v <= maxBandOf(sd)) st.override[sd.id] = v;
    });
    recompute(st);
    const c = idxCm >= 0 ? (r[idxCm]||"").trim() : "";
    if(c){ st.comment = c; st.edited = true; } else regenerate(st,true);
    out.push(st);
  });
  state.students = out;
  refreshClass(); state.students.forEach(s => regenerate(s, false));
  renderAll(); persist();
  if(badCells.length) setTimeout(() => toast(badCells.length + " cell" + (badCells.length===1?"":"s")
    + " out of range and left blank: " + badCells.slice(0,3).join(", ") + (badCells.length > 3 ? "…" : "")), 2400);
  toast("Imported "+out.length+" student"+(out.length===1?"":"s")+(anyQ?"":" — no question columns found, so no marks were set"));
}
function importJSON(text){
  const d = JSON.parse(text);
  /* A bare rubric, or a class marked against a different rubric. The generic
     marker page can switch to it (window.rubricSwitch); a page with its rubric
     built in refuses, rather than dropping every mark whose id it lacks. */
  const fileRubric = d && d.format === RUBRIC_FORMAT ? d : (d && d.rubric) || null;
  const fileRubricId = fileRubric ? fileRubric.id : d && d.rubricId;
  const bare = d && d.format === RUBRIC_FORMAT;
  if(bare || (fileRubricId && fileRubricId !== R.id)){
    if(typeof window.rubricSwitch === "function" && fileRubric){ window.rubricSwitch(fileRubric, bare ? null : text); return false; }
    toast(bare ? "That is a rubric, not a class — open it in the rubric marker"
               : "That file was marked against a different rubric (" + (fileRubric && fileRubric.title || fileRubricId) + ")");
    return false;
  }
  const fileVersion = Number(d.version) || 1;
  state.meta = Object.assign({cls:"",teacher:"",task:R.task,date:""}, d.meta||{});
  if(typeof d.band0 === "string" && d.band0) state.band0 = d.band0;
  if(Array.isArray(d.bandLabels) && d.bandLabels.length === 4) state.bandLabels = d.bandLabels;
  if(d.opts) state.opts = Object.assign(state.opts, d.opts);
  state.students = (d.students||[]).map(o => {
    const st = newStudent(o.name||"", o.pron||"they");
    const mq = migrateTicks(o.q, fileVersion);
    Object.keys(mq).forEach(id => {
      if(!(id in MAXOF)) return;
      const v = mq[id];
      if(typeof v === "number"){ if(!Number.isNaN(parseMark(String(v), MAXOF[id]))) st.q[id] = v; }
      else if(v === true) st.q[id] = MAXOF[id];
    });
    if(fileVersion < MARKS_SINCE && Object.keys(mq).some(id => id in MAXOF))
      CRITERIA.forEach(c => { if(mq[c.id] === undefined) st.q[c.id] = 0; });
    if(o.override) STRANDS.forEach(sd => {
      const v = o.override[sd.id];
      if(Number.isInteger(v) && v >= 0 && v <= maxBandOf(sd)) st.override[sd.id] = v;
    });
    /* files saved before ticks existed stored a band per strand — keep them as overrides */
    if(!o.q && o.marks) STRANDS.forEach(sd => {
      const v = o.marks[sd.id];
      if(Number.isInteger(v) && v >= 1 && v <= maxBandOf(sd)) st.override[sd.id] = v;
    });
    recompute(st);
    st.comment = o.comment || ""; st.edited = !!o.edited;
    return st;
  });
  refreshClass(); state.students.forEach(s => { if(!s.comment) regenerate(s, true); });
  $("#f-length").value = state.opts.length; $("#f-person").value = state.opts.person; $("#f-steps").value = String(state.opts.steps);
  renderAll(); persist();
  toast("Opened "+state.students.length+" student"+(state.students.length===1?"":"s"));
  return true;
}
function handleFile(file){
  const r = new FileReader();
  r.onload = () => {
    try{
      if(/\.csv$/i.test(file.name)) importCSV(r.result);
      else importJSON(r.result);
    }catch(err){ toast("Could not read that file — check it is a CSV or a saved JSON"); }
  };
  r.readAsText(file);
}

/* ---- optional autosave where the host provides it; never required ---- */
let persistTimer = null;
/* What a save holds: the class, and the rubric it was marked against, so the
   file can be reopened anywhere — including tools/rubric-marker.html with
   nothing else to hand. */
function saveData(){
  return {version:SAVE_VERSION, rubricId:R.id,
    meta:state.meta, band0:state.band0, bandLabels:state.bandLabels, opts:state.opts,
    students: state.students.map(s => ({name:s.name, pron:s.pron,
      q:s.q, override:s.override, comment:s.comment, edited:s.edited})),
    rubric: RUBRIC};
}
function persist(){
  if(typeof window.storage === "undefined" || !window.storage) return;
  clearTimeout(persistTimer);
  persistTimer = setTimeout(async () => {
    try{
      await window.storage.set(R.storageKey, JSON.stringify(saveData()));
    }catch(e){ /* no autosave available — Save file is the fallback */ }
  }, 700);
}
async function restore(){
  if(typeof window.storage === "undefined" || !window.storage) return false;
  try{
    const r = await window.storage.get(R.storageKey);
    if(r && r.value) return importJSON(r.value) !== false;
  }catch(e){}
  return false;
}

/* ============================ DEMO ============================ */
/* The class a first-time visitor sees, so every tab has something in it.
   A rubric can name its own (rubric.demo); otherwise six students spread
   across the bands. Replaced by the teacher's own class from the Class tab. */
const GENERIC_DEMO = {
  meta:{cls:"", teacher:"", date:""},
  students:[
    ["Ava Chen","she",[3,3,4,3,3,2]],
    ["Ben Novak","he",[2,2,2,2,2,2]],
    ["Charlie Doust","they",[1,2,1,1,1,1]],
    ["Divya Rao","she",[4,3,3,4,2,3]],
    ["Eli Marsh","he",[2,1,3,2,3,1]],
    ["Frankie Hale","they",[3,4,3,3,3,3]]
  ],
  skip:{}
};
function demo(){
  const D = R.demo || GENERIC_DEMO;
  state.meta = Object.assign({cls:"", teacher:"", date:""}, D.meta || {}, {task:R.task});
  const skip = D.skip || {};
  state.students = (D.students || []).map(r => {
    const st = newStudent(r[0], r[1]);
    const targets = r[2] || [];
    STRANDS.forEach((sd,i) => {
      const target = Math.min(targets.length ? targets[i % targets.length] : 2, maxBandOf(sd));
      EVALL[sd.id].forEach(id => {
        if((skip[r[0]] || []).includes(id)) return;
        const mx = MAXOF[id], band = CRITERIA.find(c => c.id === id).band;
        /* full marks below the band reached, a pass at it, under half above it */
        st.q[id] = band < target ? mx : band === target ? Math.ceil(mx * PASS) : (mx >= 2 ? 0.5 : 0);
      });
    });
    return st;
  });
  refreshClass(); state.students.forEach(st => regenerate(st, true));
}

/* ============================ SHELL ============================ */
const cap = t => t.charAt(0).toUpperCase() + t.slice(1);
function shellHTML(){
  const bandsRepeat = DEFAULT_BANDS.some((b, i) => DEFAULT_BANDS.indexOf(b) !== i);
  const back = R.back && R.back.href && !/^\s*javascript:/i.test(R.back.href)
    ? '<a class="unit-back" href="'+esc(R.back.href)+'">&#8592; '+esc(R.back.label || "Back")+'</a>' : '';
  return `
<header class="masthead">
  <div class="masthead-inner">
    <div>
      <div class="eyebrow">${esc(R.eyebrow)}</div>
      <h1>${esc(R.title)} <em>— ${esc(R.subtitle)}</em></h1>
    </div>
    <div class="masthead-side">
      ${back}
      <div class="masthead-meta" id="mastMeta"></div>
    </div>
  </div>
</header>

<nav class="tabbar">
  <div class="tabbar-inner" role="tablist" aria-label="Sections">
    <button class="tab" role="tab" data-panel="setup" id="tab-setup" aria-controls="p-setup" aria-selected="false">Class</button>
    <button class="tab" role="tab" data-panel="mark" id="tab-mark" aria-controls="p-mark" aria-selected="false">Mark <span class="tally" id="tallyMark"></span></button>
    <button class="tab" role="tab" data-panel="comments" id="tab-comments" aria-controls="p-comments" aria-selected="false">Comments</button>
    <button class="tab" role="tab" data-panel="groups" id="tab-groups" aria-controls="p-groups" aria-selected="false">Teaching groups</button>
    <button class="tab" role="tab" data-panel="analysis" id="tab-analysis" aria-controls="p-analysis" aria-selected="false">Analysis</button>
    <button class="tab" role="tab" data-panel="print" id="tab-print" aria-controls="p-print" aria-selected="false">Print rubrics</button>
    <button class="tab" role="tab" data-panel="ref" id="tab-ref" aria-controls="p-ref" aria-selected="false">Rubric reference</button>
    <span class="tabbar-spacer"></span>
    <span class="iobar">
      <button class="btn ghost small" id="btnSave">Save file</button>
      <button class="btn ghost small" id="btnLoad">Open file</button>
      <input type="file" id="fileIn" accept=".json,.csv" hidden>
    </span>
  </div>
</nav>

<main>

<!-- ============ CLASS ============ -->
<section class="panel" id="p-setup" role="tabpanel" aria-labelledby="tab-setup" tabindex="0">
  <div class="note">
    Nothing is sent anywhere and nothing is stored on a server. Use <strong>Save file</strong> before you close the tab, then <strong>Open file</strong> to pick up where you left off.
  </div>

  <div class="card">
    <div class="card-head">
      <div><h2>Task details</h2><p>These appear in the header of every printed rubric.</p></div>
    </div>
    <div class="card-body">
      <div class="grid2">
        <label class="field"><span>Class</span><input id="f-class" placeholder="7C"></label>
        <label class="field"><span>Teacher</span><input id="f-teacher" placeholder="Your name"></label>
        <label class="field"><span>Task</span><input id="f-task"></label>
        <label class="field"><span>Semester / date</span><input id="f-date" placeholder="Term 3, 2026"></label>
      </div>
    </div>
  </div>

  <div class="card">
    <div class="card-head">
      <div><h2>Band labels</h2><p>Band 0 is the “not demonstrated” column added to the printed rubric.${bandsRepeat ? " The rubric as issued has two columns with the same label — rename them here if you want the printed sheet and the comments to distinguish the two." : ""}</p></div>
      <button class="btn ghost small" id="btnResetBands">Restore rubric wording</button>
    </div>
    <div class="card-body">
      <div class="grid2" id="bandFields"></div>
    </div>
  </div>

  <div class="card">
    <div class="card-head">
      <div><h2>Students</h2><p>One per line. Add a pronoun after a comma if you want one: <code>Ava Chen, she</code></p></div>
      <span class="iobar flush"><button class="btn ghost small" id="btnEmpty">Start an empty class</button><button class="btn" id="btnApplyRoll">Update class list</button></span>
    </div>
    <div class="card-body">
      <label class="field"><span>Class roll</span><textarea id="f-roll" rows="9" placeholder="Ava Chen, she&#10;Ben Novak, he&#10;Charlie Doust"></textarea></label>
      <p class="hint">Marks already entered are kept for any student whose name is unchanged. Removing a name removes that student's marks.</p>
    </div>
  </div>

  <div class="card">
    <div class="card-head"><div><h2>Data</h2><p>CSV opens in Excel or Google Sheets — one row per student, one column per criterion, in ${esc(NOUN.task)} order. Each ${esc(NOUN.item)} column holds the mark, out of the figure in its heading; leave it blank where the part was not attempted. The Override columns are optional and accept 0–4.</p></div></div>
    <div class="card-body">
      <div class="iobar" style="flex-wrap:wrap">
        <button class="btn ghost small" id="btnCsvOut">Export marks as CSV</button>
        <button class="btn ghost small" id="btnCsvTemplate">Download blank CSV template</button>
        <button class="btn ghost small" id="btnLoad2">Import CSV or JSON</button>
        <button class="btn ghost small" id="btnRubricOut">Download this rubric</button>
        <button class="btn danger small" id="btnClearMarks">Clear all marks</button>
      </div>
    </div>
  </div>
</section>

<!-- ============ MARK ============ -->
<section class="panel" id="p-mark" role="tabpanel" aria-labelledby="tab-mark" tabindex="0">
  <div class="card">
    <div class="card-head">
      <div><h2>Marking grid</h2><p>Columns follow the ${esc(R.title)} ${esc(NOUN.item)} by ${esc(NOUN.item)}. Where the rubric splits one ${esc(NOUN.item)} across bands, each part has its own column under that ${esc(NOUN.item)} number. Type the mark for each part &mdash; the figure under each column is what it is out of, and half marks are fine (<code>1.5</code>). Enter <b>0</b> when a part was attempted but earned nothing, and leave it <b>blank</b> when it was not attempted. Enter moves down the column, the arrow keys move between cells. Bands are worked out from the marks: a part counts towards its rubric cell at ${R.pass === 0.5 ? "half its marks" : Math.round(R.pass * 100) + "% of its marks"} or more, a cell counts only when every part behind it does, and each missing part below the top cell pulls the award down a band.</p></div>
      <div class="legend">
        <div><span class="qin on">2</span> ${R.pass === 0.5 ? "half marks" : Math.round(R.pass * 100) + "% of the marks"} or more</div>
        <div><span class="qin low">0</span> under ${R.pass === 0.5 ? "half" : Math.round(R.pass * 100) + "%"}</div>
        <div><span class="qin no"></span> blank &middot; not attempted</div>
        <div><span class="sw" style="background:var(--band0)"></span>0</div>
        <div><span class="sw" style="background:var(--band1)"></span>1</div>
        <div><span class="sw" style="background:var(--band2)"></span>2</div>
        <div><span class="sw" style="background:var(--band3)"></span>3</div>
        <div><span class="sw" style="background:var(--band4)"></span>4</div>
      </div>
    </div>
    <div class="card-body">
      <div class="gridwrap"><table class="mark" id="markTable"></table></div>
      <div id="markEmpty"></div>
      <details class="critkey"><summary>What each column means</summary><div class="ckgrid" id="critKey"></div></details>
    </div>
  </div>
</section>

<!-- ============ COMMENTS ============ -->
<section class="panel" id="p-comments" role="tabpanel" aria-labelledby="tab-comments" tabindex="0">
  <div class="card">
    <div class="card-head">
      <div><h2>Comments</h2><p>Written from the marks. Edit any comment and it stays edited — the printed rubric uses whatever is in the box.</p></div>
      <div class="iobar">
        <button class="btn ghost small" id="btnRegenAll">Rebuild all unedited</button>
        <button class="btn ghost small" id="btnCopyAll">Copy all comments</button>
      </div>
    </div>
    <div class="card-body">
      <div class="cmt-tools">
        <label class="field" style="min-width:150px"><span>Length</span>
          <select id="f-length"><option value="brief">Brief — 2 sentences</option><option value="standard" selected>Standard — report length</option><option value="detailed">Detailed — every strand</option></select>
        </label>
        <label class="field" style="min-width:150px"><span>Address the student as</span>
          <select id="f-person"><option value="third" selected>Third person (Ava has…)</option><option value="second">Second person (You have…)</option></select>
        </label>
        <label class="field" style="min-width:160px"><span>Next steps shown</span>
          <select id="f-steps"><option value="2" selected>Two</option><option value="1">One</option><option value="3">Three</option></select>
        </label>
      </div>
      <div class="stulist" id="cmtList"></div>
      <div id="cmtPane"></div>
    </div>
  </div>
</section>

<!-- ============ GROUPS ============ -->
<section class="panel" id="p-groups" role="tabpanel" aria-labelledby="tab-groups" tabindex="0">
  <div class="card">
    <div class="card-head">
      <div><h2>Teaching groups</h2><p>Read down a strand to see who sits where, and what to teach each group next.</p></div>
      <label class="field" style="margin:0;min-width:230px"><span>Strand</span><select id="f-groupstrand"></select></label>
    </div>
    <div class="card-body"><div id="groupPane"></div></div>
  </div>
</section>

<!-- ============ ANALYSIS ============ -->
<section class="panel" id="p-analysis" role="tabpanel" aria-labelledby="tab-analysis" tabindex="0">
  <div class="card">
    <div class="card-head">
      <div><h2>Class analysis</h2><p>How the class went on the ${esc(NOUN.task)}, worked out from the marks in the grid. It updates as you mark, and only counts students with at least one mark entered.</p></div>
      <div class="an-actions">
        <button class="btn ghost small" id="btnAnCsv">Download ${esc(NOUN.item)} analysis (CSV)</button>
        <button class="btn small" id="btnAnPrint">Print analysis</button>
      </div>
    </div>
    <div class="card-body"><div id="anPane"></div></div>
  </div>
</section>

<!-- ============ PRINT ============ -->
<section class="panel" id="p-print" role="tabpanel" aria-labelledby="tab-print" tabindex="0">
  <div class="printbar">
    <label class="field" style="margin:0;min-width:200px"><span>Print</span>
      <select id="f-printwho"><option value="all">All students</option></select>
    </label>
    <label class="field" style="margin:0;min-width:170px"><span>Include</span>
      <select id="f-printwhat"><option value="rubric" selected>Rubric + comment</option><option value="rubriconly">Rubric only</option><option value="groups">Teaching group summary</option></select>
    </label>
    <label class="field" style="margin:0;min-width:130px"><span>Text size</span>
      <select id="f-printsize"><option value="0.92">Smaller</option><option value="1" selected>Normal</option><option value="1.07">Larger</option></select>
    </label>
    <button class="btn" id="btnPrint">Print</button>
  </div>
  <div id="printPane"></div>
</section>

<!-- ============ REFERENCE ============ -->
<section class="panel" id="p-ref" role="tabpanel" aria-labelledby="tab-ref" tabindex="0">
  <div class="card">
    <div class="card-head"><div><h2>Rubric reference</h2><p>The rubric exactly as issued, with the ${esc(NOUN.item)} that gives the evidence for each cell.</p></div></div>
    <div class="card-body"><div style="overflow-x:auto"><table class="ref" id="refTable"></table></div><p class="hint" id="refAttribution"></p></div>
  </div>
</section>

</main>

<div class="status" id="status" role="status" aria-live="polite"></div>`;
}

/* A rubric that fails validateRubric() gets this instead of the marker. */
function problemsHTML(){
  const c = RUBRIC_CHECK;
  return '<div class="rb-problems"><div class="card"><div class="card-head"><div><h2>This rubric can’t be used yet</h2>'
    + '<p>'+(RUBRIC ? 'The marker checks a rubric before building anything from it, so that nothing is marked against a rubric that would band students wrongly.' : 'No rubric was loaded.')+'</p></div></div>'
    + '<div class="card-body"><strong>'+c.errors.length+' problem'+(c.errors.length===1?'':'s')+' to fix</strong><ul>'
    + c.errors.map(e => '<li>'+esc(e)+'</li>').join("")
    + c.warnings.map(e => '<li class="warn">'+esc(e)+'</li>').join("")
    + '</ul></div></div></div>';
}

/* ============================ WIRE UP ============================ */
function downloadRubric(){
  download(R.fileStem + "-rubric-definition.json", JSON.stringify(RUBRIC, null, 2), "application/json");
  toast("Rubric downloaded — open it in the rubric marker, or share it");
}
function wireUp(){
  $$(".tab").forEach(t => t.onclick = () => showTab(t.dataset.panel));
  wireAnalysisTip();
  ["cls","teacher","task","date"].forEach(k => {
    const el = $("#f-"+(k==="cls"?"class":k));
    el.oninput = () => { state.meta[k] = el.value; renderPrint(); persist();
      renderMast(); };
  });
  $("#btnApplyRoll").onclick = applyRoll;
  $("#btnEmpty").onclick = () => {
    if(state.students.length && !confirm("Remove all students and their marks, and start with an empty class?")) return;
    state.students = []; $("#f-roll").value = ""; renderAll(); persist(); toast("Empty class ready");
  };
  $("#btnResetBands").onclick = () => { state.bandLabels = [...DEFAULT_BANDS]; state.band0 = DEFAULT_BAND0; renderAll(); persist(); toast("Band labels restored"); };
  $("#btnSave").onclick = saveJSON;
  $("#btnLoad").onclick = () => $("#fileIn").click();
  $("#btnLoad2").onclick = () => $("#fileIn").click();
  $("#fileIn").onchange = e => { const f = e.target.files[0]; if(f) handleFile(f); e.target.value = ""; };
  $("#btnCsvOut").onclick = () => exportCSV(false);
  $("#btnCsvTemplate").onclick = () => exportCSV(true);
  $("#btnClearMarks").onclick = () => {
    if(!confirm("Clear every mark and override for all students? Comments will be rebuilt as blank.")) return;
    state.students.forEach(s => { s.q = {}; s.override = {}; recompute(s); s.edited = false; regenerate(s,true); });
    renderAll(); persist(); toast("Marks cleared");
  };
  $("#f-length").onchange = e => { state.opts.length = e.target.value; regenerateAll(false); renderComments(); renderPrint(); persist(); };
  $("#f-person").onchange = e => { state.opts.person = e.target.value; regenerateAll(false); renderComments(); renderPrint(); persist(); };
  $("#f-steps").onchange  = e => { state.opts.steps = parseInt(e.target.value,10); regenerateAll(false); renderComments(); renderPrint(); persist(); };
  $("#btnRegenAll").onclick = () => { regenerateAll(false); renderComments(); renderPrint(); persist(); toast("Rebuilt every comment you have not edited"); };
  $("#btnCopyAll").onclick = () => {
    const txt = state.students.map(s => s.name + "\n" + s.comment).join("\n\n———\n\n");
    navigator.clipboard.writeText(txt).then(()=>toast("All comments copied"));
  };
  $("#f-groupstrand").onchange = e => { state.ui.groupStrand = e.target.value; renderGroups(); };
  ["#f-printwho","#f-printwhat","#f-printsize"].forEach(s => $(s).onchange = renderPrint);
  $("#btnPrint").onclick = () => window.print();
  $("#btnAnPrint").onclick = () => { showTab("analysis"); window.print(); };
  $("#btnAnCsv").onclick = exportAnalysisCSV;
  $("#btnRubricOut").onclick = downloadRubric;
}

/* ============================ BOOT ============================ */
/* Autosave. window.storage is provided by the authoring environment; on the
   live site fall back to localStorage so a refresh doesn't lose the marks.
   Data stays in this browser only — nothing is sent anywhere. Use
   "Clear all marks" (or Save file, then clear) on a shared machine. */
if(!window.RUBRIC_NO_BOOT && (typeof window.storage === "undefined" || !window.storage)){
  try{
    localStorage.setItem("__probe","1"); localStorage.removeItem("__probe");
    window.storage = {
      get: async k => { const v = localStorage.getItem(k); return v === null ? null : {value:v}; },
      set: async (k,v) => { localStorage.setItem(k,v); }
    };
  }catch(e){ /* storage blocked — Save file is the fallback */ }
}

/* window.RUBRIC_OPEN_SAVE: the text of a saved class to open on boot, set by
   tools/rubric-marker.html when the teacher picked a save file rather than a
   bare rubric. It wins over the autosave. */
/* window.RUBRIC_NO_BOOT: load the engine's functions without building a
   marker — tools/rubric-builder.html uses validateRubric() and
   normaliseRubric() this way, so the builder and the marker can never
   disagree about what a valid rubric is. */
async function boot(){
  if(window.RUBRIC_NO_BOOT) return;
  const app = document.getElementById("rubric-app") || document.body;
  if(!RUBRIC_OK){
    app.innerHTML = problemsHTML();
    document.dispatchEvent(new CustomEvent("rubric:problems", {detail: RUBRIC_CHECK}));
    return;
  }
  if(R.theme && !document.body.className.split(/\s+/).some(c => c.indexOf("theme-") === 0))
    document.body.classList.add("theme-" + R.theme);
  document.body.classList.add("rubric-page");
  app.innerHTML = shellHTML();
  wireUp();
  let opened = false;
  if(typeof window.RUBRIC_OPEN_SAVE === "string"){
    try{ opened = importJSON(window.RUBRIC_OPEN_SAVE) !== false; }catch(e){ toast("Could not read that saved file"); }
  }
  if(!opened && !(await restore())) demo();
  renderAll();
  showTab("setup");
  document.dispatchEvent(new CustomEvent("rubric:ready", {detail: {id: R.id, title: R.title}}));
}
boot();
