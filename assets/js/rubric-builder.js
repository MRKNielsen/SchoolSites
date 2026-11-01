/* =========================================================================
   rubric-builder.js — tools/rubric-builder.html: write a rubric file for
   the rubric marker without hand-editing JSON.

   The state IS a rubric file (format rubric-marker/1). Fields the builder
   has no form for (save migrations, demo class, levels/gloss, back link …)
   ride along untouched, so opening the Space rubric and exporting it gives
   back the same rubric — tools/test-rubric-builder.js asserts exactly that.

   Validation is the marker's own: the page loads assets/js/rubric.js with
   window.RUBRIC_NO_BOOT and calls validateRubric() on what would be
   exported, so the builder and the marker cannot disagree about what a
   valid rubric is.

   Curriculum: window.VC2 from assets/js/vc2-curriculum.js (generated from
   VCAA's scope-and-sequence charts by tools/build-curriculum.py). Without it
   the builder still works; codes are typed by hand.

   Inputs carry data-f="path.to.field" and are bound by one delegated
   listener. Typing never re-renders the input being typed in — the marking
   grid learnt that a re-render under the caret loses the cell — so a tab is
   rebuilt only for structural changes, with focus put back afterwards.
   ========================================================================= */
"use strict";
(function(){

const FORMAT = "rubric-marker/1";
const DRAFT = "rubric-builder:draft";
const INCOMING = "rubric-builder:incoming";
const PREVIOUS = "rubric-builder:previous";
const THEMES = ["science","space","maths","methods","specialist","primer","foundation","algorithmics","computing"];
const ATTRIBUTION = "Victorian Curriculum F–10 Version 2.0 content elements are © VCAA, licensed CC BY-NC 3.0 AU. The curriculum can be accessed at https://f10.vcaa.vic.edu.au.";
const ME = document.currentScript;
const MARKER = (ME && ME.getAttribute("data-marker")) || "rubric-marker.html";
const STARTER = (ME && ME.getAttribute("data-starter")) || "rubric-starter.json";
const EXAMPLES = (ME && ME.getAttribute("data-examples") || "").split(";").map(s => s.trim()).filter(Boolean)
  .map(s => { const i = s.indexOf("|"); return {label: s.slice(0, i), src: s.slice(i + 1)}; });

const app = document.getElementById("builder-app");
const $ = s => app.querySelector(s);
const $$ = s => Array.from(app.querySelectorAll(s));
const esc = t => String(t == null ? "" : t).replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const clone = o => JSON.parse(JSON.stringify(o));
const cap = t => t ? t.charAt(0).toUpperCase() + t.slice(1) : t;
const store = {
  get(k){ try{ return localStorage.getItem(k); }catch(e){ return null; } },
  set(k, v){ try{ localStorage.setItem(k, v); return true; }catch(e){ return false; } },
  del(k){ try{ localStorage.removeItem(k); }catch(e){} }
};

/* ============================ STATE ============================ */
let doc = null;            // the rubric being edited
let tab = "task";
let notice = "";           // a line shown above the tabs (restored draft etc.)
let pickFor = null;        // strand index the curriculum picker attaches to, or "new"
let lastText = null;       // last descriptor/phrase field focused, for snippet inserts
let paste = null;          // booklet paste panel: {text, rows}

function blank(){
  return {
    format: FORMAT, id: "", title: "", task: "", context: "", eyebrow: "",
    noun: {task: "task", item: "question"},
    columnOrder: "listed",
    bands: ["Working towards the standard","Approaching the standard","At the standard","Above the standard"],
    band0: "Not demonstrated",
    parts: [{id: "A", name: "Part A"}],
    strands: [newStrand([])],
    criteria: []
  };
}
function newStrand(existing){
  const ids = new Set(existing.map(s => s.id));
  let n = existing.length + 1; while(ids.has("s" + n)) n++;
  return {id: "s" + n, name: "", maxBand: 4, start: "",
          bands: [1,2,3,4].map(() => ({q: "", d: ""})), can: ["","","",""], next: ["","","",""]};
}
function nextPartId(){
  const used = new Set(doc.parts.map(p => p.id));
  for(const L of "ABCDEFGHIJKLMNOPQRSTUVWXYZ") if(!used.has(L)) return L;
  let n = 1; while(used.has("P" + n)) n++; return "P" + n;
}
const slug = t => String(t || "").toLowerCase().normalize("NFKD").replace(/[^\w\s-]/g, "").trim()
  .replace(/[\s_]+/g, "-").replace(/-+/g, "-").slice(0, 40).replace(/-+$/, "");

/* Give strand/criterion/part entries the arrays and fields the form reads. */
function tidy(d){
  d.noun = Object.assign({task: "task", item: "question"}, d.noun || {});
  if(!Array.isArray(d.bands) || d.bands.length !== 4) d.bands = blank().bands;
  d.parts = Array.isArray(d.parts) && d.parts.length ? d.parts : [{id: "A", name: "Part A"}];
  d.strands = Array.isArray(d.strands) ? d.strands : [];
  d.criteria = Array.isArray(d.criteria) ? d.criteria : [];
  d.strands.forEach(s => {
    ["bands","can","next"].forEach(k => { if(!Array.isArray(s[k])) s[k] = []; });
    for(let i = 0; i < 4; i++){
      if(!s.bands[i]) s.bands[i] = {q: "", d: ""};
      if(s.can[i] == null) s.can[i] = "";
      if(s.next[i] == null) s.next[i] = "";
    }
    if(s.start == null) s.start = "";
  });
  return d;
}

/* ============================ EXPORT ============================ */
/* the rubric as a file: arrays trimmed to each strand's maxBand, evidence
   labels filled where left blank, weights kept equal to the marks, ids
   given to anything new, and builder-only scratch removed */
const qTag = c => c.q + (c.sub ? (/^([a-z]|[ivx]+|[a-z][ivx]+|\d+)$/i.test(c.sub) ? c.sub : " " + c.sub) : "");
function autoEvidence(d, sid, b){
  return d.criteria.filter(c => c.strand === sid && +c.band === b).map(qTag).join(", ");
}
function exportRubric(src){
  const d = clone(src || doc);
  if(!d.id) d.id = slug(d.title) || "rubric";
  if(!d.task) delete d.task;
  ["context","eyebrow","subtitle","fileStem","storageKey","attribution"].forEach(k => { if(d[k] === "") delete d[k]; });
  if(d.total === "" || d.total == null) delete d.total;
  /* criterion ids: keep any the rubric already had (saved classes are keyed
     on them); mint one from the question label for a new one */
  const used = new Set(d.criteria.filter(c => !c._new && c.id).map(c => c.id));
  d.criteria.forEach(c => {
    if(c._new || !c.id){
      /* "Q1.1" -> "Q1_1", never "Q11", which is question eleven */
      const base = (String(c.q || "") + String(c.sub || "")).replace(/\./g, "_").replace(/[^A-Za-z0-9_-]/g, "").slice(0, 34) || "c";
      let id = base, n = 2; while(used.has(id)) id = base + "-" + n++;
      c.id = id; used.add(id);
    }
    delete c._new;
    if(c.strand === "" || c.strand == null) c.strand = null;
    if(c.strand === null) delete c.band;
    c.max = Number(c.max);
    if(c.strand) c.band = Number(c.band);
  });
  d.strands.forEach(s => {
    const mb = Number(s.maxBand) || 4;
    if("maxBand" in s) s.maxBand = mb;   /* left out means 4; keep it that way */
    s.bands = s.bands.slice(0, mb).map((b, i) => ({q: (b.q || "").trim() || autoEvidence(d, s.id, i + 1), d: b.d}));
    s.can = s.can.slice(0, mb); s.next = s.next.slice(0, mb);
    const marks = d.criteria.filter(c => c.strand === s.id).reduce((t, c) => t + c.max, 0);
    if("weight" in s) s.weight = marks;
  });
  if(d.strands.some(s => s.code && /^VC2/.test(s.code)) && !d.attribution) d.attribution = ATTRIBUTION;
  return d;
}
/* the marker's messages name ids; a teacher thinks in strand names and question numbers */
function friendly(msg, d){
  return msg.replace(/Strand (\S+?)(?=[ :,.]|'s|$)/g, (m, id) => {
    const i = d.strands.findIndex(s => s.id === id);
    return i < 0 ? m : "Strand " + (i + 1) + (d.strands[i].name ? " (“" + d.strands[i].name.slice(0, 40) + (d.strands[i].name.length > 40 ? "…" : "") + "”)" : "");
  }).replace(/Criterion (\S+?)(?=[ :,.]|$)/g, (m, id) => {
    const c = d.criteria.find(x => x.id === id);
    return c ? "Question " + (qTag(c) || "(unnumbered)") : m;
  }).replace(/strand (s\d+)'s maxBand/g, (m, id) => {
    const i = d.strands.findIndex(s => s.id === id); return i < 0 ? m : "strand " + (i + 1) + "'s top band";
  }).replace(/^total is/, "The paper total is");
}
function check(){
  const d = exportRubric();
  const r = (typeof validateRubric === "function") ? validateRubric(d) : {errors: ["The marking engine didn’t load, so the rubric can’t be checked."], warnings: []};
  return {errors: r.errors.map(e => friendly(e, d)), warnings: r.warnings.map(e => friendly(e, d)), d};
}

/* ============================ CURRICULUM ============================ */
const VC = window.VC2 || null;
const CD = [];           // flat list: {code, text, subject, level, strand, substrand, std}
if(VC) VC.subjects.forEach(sub => sub.levels.forEach(lv => (lv.strands || []).forEach(st => (st.substrands || []).forEach(ss =>
  (ss.cds || []).forEach(cd => CD.push({code: cd.code, text: cd.text, subject: sub.name, subjectId: sub.id,
    level: lv.level, strand: st.name, substrand: ss.name, std: lv.achievement || ""}))))));
const byCode = code => CD.find(c => c.code === code);
const codesOf = s => String(s.code || "").split(/[\s,;]+/).filter(Boolean);
/* the achievement standard, a sentence at a time, as insertable snippets */
const sentences = t => String(t || "").replace(/\s+/g, " ").match(/[^.!?]+[.!?]+(\s|$)/g) || (t ? [t] : []);

/* ============================ RENDER ============================ */
function shell(){
  app.innerHTML = `
<header class="masthead">
  <div class="masthead-inner">
    <div>
      <div class="eyebrow">Staff tool</div>
      <h1>Rubric builder <em>— write a rubric for the rubric marker</em></h1>
    </div>
    <div class="masthead-side">
      <a class="unit-back" href="${esc(MARKER)}">Rubric marker &#8594;</a>
      <div class="masthead-meta" id="bMeta"></div>
    </div>
  </div>
</header>
<nav class="tabbar">
  <div class="tabbar-inner" role="tablist" aria-label="Sections">
    <button class="tab" role="tab" data-tab="task" id="btab-task" aria-selected="false">1 · Task</button>
    <button class="tab" role="tab" data-tab="strands" id="btab-strands" aria-selected="false">2 · Strands <span class="tally" id="tStrands"></span></button>
    <button class="tab" role="tab" data-tab="questions" id="btab-questions" aria-selected="false">3 · Questions <span class="tally" id="tQuestions"></span></button>
    <button class="tab" role="tab" data-tab="check" id="btab-check" aria-selected="false">4 · Check &amp; export <span class="tally" id="tCheck"></span></button>
    <span class="tabbar-spacer"></span>
    <span class="iobar">
      <button class="btn ghost small" data-act="new">New</button>
      <button class="btn ghost small" data-act="open">Open…</button>
      <button class="btn small" data-act="marker">Open in marker</button>
      <input type="file" id="bFile" accept=".json,.js,application/json" hidden>
    </span>
  </div>
</nav>
<main>
  <div id="bNotice"></div>
  <div id="bPanel"></div>
</main>
<div class="bpick" id="bPick" hidden></div>
<div class="status" id="status" role="status" aria-live="polite"></div>`;
}

function toast(msg){ const s = document.getElementById("status"); s.textContent = msg; s.classList.add("show"); clearTimeout(s._t); s._t = setTimeout(() => s.classList.remove("show"), 2600); }

const field = (label, path, value, opts = {}) => {
  const id = "f_" + path.replace(/\W/g, "_");
  const attrs = `id="${id}" data-f="${esc(path)}"${opts.num ? ' data-num="1"' : ""}${opts.placeholder ? ` placeholder="${esc(opts.placeholder)}"` : ""}${opts.rerender ? ' data-rerender="1"' : ""}${opts.text ? ' data-text="1"' : ""}`;
  const input = opts.area
    ? `<textarea ${attrs} rows="${opts.rows || 2}">${esc(value)}</textarea>`
    : `<input ${attrs} value="${esc(value)}"${opts.num ? ' inputmode="decimal"' : ""}>`;
  return `<label class="field" for="${id}"><span>${label}${opts.hint ? ` <em class="fieldnote">${opts.hint}</em>` : ""}</span>${input}</label>`;
};
const select = (label, path, value, options, opts = {}) => {
  const id = "f_" + path.replace(/\W/g, "_");
  return `<label class="field" for="${id}"><span>${label}</span><select id="${id}" data-f="${esc(path)}"${opts.num ? ' data-num="1"' : ""}${opts.rerender ? ' data-rerender="1"' : ""}>`
    + options.map(o => `<option value="${esc(o[0])}"${String(o[0]) === String(value) ? " selected" : ""}>${esc(o[1])}</option>`).join("")
    + `</select></label>`;
};

function renderTask(){
  const d = doc;
  return `
<div class="card"><div class="card-head"><div><h2>The task</h2><p>What the marker, the printed rubrics and the comments call this assessment.</p></div></div>
<div class="card-body"><div class="grid2">
  ${field("Title", "title", d.title, {placeholder: "e.g. Chemical Reactions Test", rerender: false})}
  ${field("Name on reports", "task", d.task || "", {placeholder: d.title || "the title", hint: "if different, e.g. with a CAT number"})}
  ${field("Context", "context", d.context || "", {placeholder: "e.g. Year 8 Science · Chemistry"})}
  ${field("Eyebrow", "eyebrow", d.eyebrow || "", {placeholder: d.context || "e.g. Year 8 Science · Common Assessment Task", hint: "small line above the title"})}
  ${field("The task is a…", "noun.task", d.noun.task, {hint: "“Across this <b>test</b> Ava is…”"})}
  ${field("Each part to mark is a…", "noun.item", d.noun.item, {hint: "question, task, criterion"})}
  ${select("Colour theme", "theme", d.theme || "", [["", "Site default (chalk blue)"], ...THEMES.map(t => [t, cap(t)])], {rerender: true})}
  ${field("Paper total", "total", d.total == null ? "" : d.total, {num: true, placeholder: "optional", hint: "checked against the questions’ marks"})}
</div></div></div>

<div class="card"><div class="card-head"><div><h2>Band labels</h2><p>Four bands, plus band 0 for “not yet demonstrated”. Strands can stop short of band 4 if this task can’t show evidence that high.</p></div></div>
<div class="card-body"><div class="grid2">
  ${field("Band 0", "band0", d.band0 || "")}
  ${d.bands.map((b, i) => field("Band " + (i + 1), "bands." + i, b)).join("")}
</div></div></div>

<div class="card"><div class="card-head"><div><h2>Marking rules</h2></div></div>
<div class="card-body"><div class="grid2">
  ${select("A question counts towards its band at…", "pass", d.pass == null ? 0.5 : d.pass, [[0.5, "half its marks or more"], [1, "full marks only"], [0.75, "three-quarters of its marks"], [0.25, "a quarter of its marks"]], {num: true})}
  ${select("Marking grid columns", "columnOrder", d.columnOrder || "listed", [["listed", "in the order of the Questions tab"], ["question", "sorted by question number"]])}
</div>
<details class="badv"><summary>Advanced</summary>
  <p class="hint">The id names this rubric’s autosave slot in the marker. Leave it once a class has been marked: changing it starts a fresh slot, and saved classes from the old id will be refused.</p>
  <div class="grid2">
    ${field("Rubric id", "id", d.id || "", {placeholder: slug(d.title) || "made from the title"})}
    ${field("File name stem", "fileStem", d.fileStem || "", {placeholder: d.id || slug(d.title) || "the id"})}
  </div>
  ${d.storageKey || d.save || d.demo ? `<p class="hint">This rubric also carries ${[d.storageKey && "its own autosave key (" + esc(d.storageKey) + ")", d.save && "save-file migrations", d.demo && "a demo class"].filter(Boolean).join(", ")}. They are kept as they are.</p>
  <button class="btn ghost small" data-act="fork">Make this a new rubric</button> <span class="hint">— a copy with a new id, ready to adapt for another task.</span>` : ""}
</details>
</div></div>`;
}

function strandCard(s, i){
  const mb = +s.maxBand || 4;
  const marks = doc.criteria.filter(c => c.strand === s.id).reduce((t, c) => t + (+c.max || 0), 0);
  const nq = doc.criteria.filter(c => c.strand === s.id).length;
  const codes = codesOf(s), known = codes.map(byCode).filter(Boolean);
  let h = `<div class="card bstrand" data-strand="${i}">
<div class="card-head">
  <div><h2>Strand ${i + 1}</h2><p id="sMarks${i}">${nq} question${nq === 1 ? "" : "s"} · ${marks} mark${marks === 1 ? "" : "s"}</p></div>
  <span class="iobar flush">
    <button class="btn ghost small" data-act="s-up" data-i="${i}" ${i === 0 ? "disabled" : ""} aria-label="Move strand up">&#8593;</button>
    <button class="btn ghost small" data-act="s-down" data-i="${i}" ${i === doc.strands.length - 1 ? "disabled" : ""} aria-label="Move strand down">&#8595;</button>
    <button class="btn danger small" data-act="s-del" data-i="${i}">Remove</button>
  </span>
</div>
<div class="card-body">
  ${field("What students do — the row heading", `strands.${i}.name`, s.name, {area: true, rows: 2, text: true, placeholder: "e.g. Explains day, night and the seasons from Earth’s rotation and tilt"})}
  <div class="grid3">
    <div class="field"><span>Curriculum</span>
      <div class="bcode">${field("", `strands.${i}.code`, s.code || "", {placeholder: VC ? "pick or type a code" : "e.g. VC2S8U03", rerender: true}).replace('<label class="field"', '<label class="field bare"')}
      <button class="btn ghost small" data-act="pick" data-i="${i}">${VC ? "Find…" : "Codes?"}</button></div>
    </div>
    ${select("Highest band this task can show", `strands.${i}.maxBand`, mb, [[4,"Band 4"],[3,"Band 3"],[2,"Band 2"],[1,"Band 1"]], {num: true, rerender: true})}
    ${field("Short label", `strands.${i}.sub`, s.sub || "", {placeholder: "the question numbers", hint: "under the strand on reports"})}
  </div>`;
  if(known.length){
    h += `<div class="bcur">` + known.map(k => `<div class="bcd"><span class="ckcode cur">${esc(k.code)}</span> ${esc(k.text)} <span class="hint">${esc(k.subject)} · Level ${esc(k.level)} · ${esc(k.substrand || k.strand)}</span>
      <button class="chipbtn" data-act="snip" data-t="${esc(k.text)}">use text</button></div>`).join("");
    const std = known[0].std;
    if(std) h += `<details class="bstd"><summary>Achievement standard, Level ${esc(known[0].level)} — click a sentence to put it in the last box you were writing in</summary><div class="bsnips">`
      + sentences(std).map(t => `<button class="chipbtn" data-act="snip" data-t="${esc(t.trim())}">${esc(t.trim())}</button>`).join("") + `</div></details>`;
    h += `</div>`;
  } else if(codes.length && VC){
    h += `<p class="hint">${esc(codes.join(", "))} isn’t in the curriculum data here (Science 7–10, Mathematics 7–10A). It will still be shown on the rubric.</p>`;
  }
  h += `<div class="bbands">`;
  for(let b = 1; b <= mb; b++){
    const auto = autoEvidence(doc, s.id, b);
    h += `<div class="bband">
      <div class="bband-h"><span class="bnum b${b}">${b}</span> ${esc(doc.bands[b-1] || "")}
        <span class="bev ${auto ? "" : "none"}" id="ev${i}_${b}">${auto ? "evidence: " + esc(auto) : "no question tagged to this band yet"}</span></div>
      ${field("Descriptor — what work at this band looks like", `strands.${i}.bands.${b-1}.d`, s.bands[b-1].d, {area: true, rows: 2, text: true})}
      <div class="grid2">
        ${field("Comment: “Ava can now …”", `strands.${i}.can.${b-1}`, s.can[b-1], {text: true, placeholder: "label the layers of the Sun"})}
        ${field("Comment: “To improve, Ava should …”", `strands.${i}.next.${b-1}`, s.next[b-1], {text: true, placeholder: b === mb ? "how to extend beyond the task" : "what lifts work to the next band"})}
      </div>
      ${field("Evidence label on the rubric", `strands.${i}.bands.${b-1}.q`, s.bands[b-1].q, {placeholder: auto || "filled from the questions tagged to this band", hint: "leave blank to use the questions"})}
    </div>`;
  }
  h += `</div>
  ${field("Band 0 next step: “To make a start, Ava should …”", `strands.${i}.start`, s.start, {text: true, placeholder: "the way in for a student who showed nothing yet"})}
  <p class="hint">Write the comment phrases to follow on from the quoted words, starting lower-case, with no full stop. <code>{their}</code> becomes his, her, their or your.</p>
</div></div>`;
  return h;
}
function renderStrands(){
  return `<div class="note">A strand is one row of the rubric. Each band needs a descriptor, the phrases the marker writes comments with, and at least one question behind it (tag questions on the next tab). ${VC ? "Start a strand from a Victorian Curriculum content description with <b>Add from the curriculum</b>." : ""}</div>`
    + doc.strands.map(strandCard).join("")
    + `<div class="iobar"><button class="btn" data-act="s-add">Add a strand</button>${VC ? '<button class="btn ghost" data-act="pick" data-i="new">Add from the curriculum…</button>' : ""}</div>`;
}

function coverageHTML(){
  const d = doc;
  if(!d.strands.length) return '<p class="hint">No strands yet.</p>';
  let h = '<table class="an-t bcov"><thead><tr><th>Strand</th>' + [1,2,3,4].map(b => '<th>Band ' + b + '</th>').join("") + '<th class="n">Marks</th></tr></thead><tbody>';
  d.strands.forEach((s, i) => {
    const mb = +s.maxBand || 4;
    h += '<tr><td>' + (i + 1) + '. ' + esc((s.name || "(no name yet)").slice(0, 60)) + '</td>';
    for(let b = 1; b <= 4; b++){
      if(b > mb){ h += '<td class="na">—</td>'; continue; }
      const cs = d.criteria.filter(c => c.strand === s.id && +c.band === b);
      h += cs.length ? '<td>' + esc(cs.map(qTag).join(", ")) + ' <span class="hint">' + cs.reduce((t, c) => t + (+c.max || 0), 0) + 'm</span></td>'
                     : '<td class="gap">missing</td>';
    }
    h += '<td class="n">' + d.criteria.filter(c => c.strand === s.id).reduce((t, c) => t + (+c.max || 0), 0) + '</td></tr>';
  });
  const off = d.criteria.filter(c => !c.strand);
  const total = d.criteria.reduce((t, c) => t + (+c.max || 0), 0);
  h += '</tbody><tfoot><tr><td colspan="5">' + (off.length ? esc(off.length + " outside the rubric: " + off.map(qTag).join(", ")) : "") + '</td><td class="n"><b>' + total + '</b></td></tr></tfoot></table>';
  return h;
}

function renderQuestions(){
  const d = doc;
  const partOpts = d.parts.map(p => [p.id, p.name]);
  const strandOpts = [["", "— not in the rubric —"], ...d.strands.map((s, i) => [s.id, (i + 1) + ". " + (s.name || "(unnamed strand)").slice(0, 48)])];
  let h = `<div class="card"><div class="card-head"><div><h2>Parts of the task</h2><p>Sections of the paper. They group the columns of the marking grid.</p></div>
    <button class="btn ghost small" data-act="p-add">Add a part</button></div><div class="card-body"><div class="grid3">`
    + d.parts.map((p, i) => `<div class="bpart">${field("Part " + esc(p.id), `parts.${i}.name`, p.name, {rerender: false})}${d.parts.length > 1 ? `<button class="btn danger small" data-act="p-del" data-i="${i}">Remove</button>` : ""}</div>`).join("")
    + `</div></div></div>`;

  h += `<div class="card"><div class="card-head"><div><h2>Questions</h2><p>One row for every mark-bearing ${esc(d.noun.item)} or part of one. Tag each to the strand and band it gives evidence for. A question can count for only one band; split it into parts (a), (b) if it evidences two.</p></div>
    <span class="iobar flush"><button class="btn ghost small" data-act="paste">Paste from a booklet…</button><button class="btn ghost small" data-act="q-sort">Sort by number</button><button class="btn small" data-act="q-add">Add a question</button></span></div>
  <div class="card-body">`;
  if(paste){
    h += `<div class="bpaste"><p class="hint">Paste the question list from a booklet, e.g. the output of <code>pdftotext -layout booklet.pdf - | grep -o 'Q[0-9]*\\.[0-9]* ([0-9]* marks\\?)'</code>. Anything like <code>Q3.2 (2 marks)</code>, <code>Question 4b [3 marks]</code> or <code>5(a) (1 mark)</code> is read.</p>
      <textarea id="bPasteText" rows="6">${esc(paste.text)}</textarea>
      <div class="iobar"><label class="field bare inline"><span>Into part</span><select id="bPastePart">${partOpts.map(o => `<option value="${esc(o[0])}">${esc(o[1])}</option>`).join("")}</select></label>
      <button class="btn small" data-act="paste-add">Add <span id="bPasteN">${paste.rows.length}</span> question${paste.rows.length === 1 ? "" : "s"}</button><button class="btn ghost small" data-act="paste-close">Close</button></div>
      <div id="bPastePrev">${pastePreview()}</div></div>`;
  }
  if(!d.criteria.length) h += '<div class="empty"><strong>No questions yet</strong>Add them one at a time, or paste the list from a booklet.</div>';
  else {
    h += `<div class="an-tablewrap"><table class="bq"><thead><tr><th>${esc(cap(d.noun.item))}</th><th>Part (a, b…)</th><th>What it asks for</th><th>Section</th><th class="n">Marks</th><th>Strand</th><th>Band</th><th></th></tr></thead><tbody>`;
    d.criteria.forEach((c, i) => {
      const s = d.strands.find(x => x.id === c.strand);
      const mb = s ? (+s.maxBand || 4) : 0;
      h += `<tr${s ? "" : ' class="off"'}>
        <td><input data-f="criteria.${i}.q" value="${esc(c.q)}" class="w-q" aria-label="Question number"></td>
        <td><input data-f="criteria.${i}.sub" value="${esc(c.sub || "")}" class="w-sub" aria-label="Sub-part"></td>
        <td><input data-f="criteria.${i}.label" value="${esc(c.label || "")}" class="w-lab" placeholder="e.g. Labels the layers of the Sun" aria-label="What it asks for"></td>
        <td><select data-f="criteria.${i}.part" aria-label="Section">${partOpts.map(o => `<option value="${esc(o[0])}"${o[0] === c.part ? " selected" : ""}>${esc(o[0])}</option>`).join("")}</select></td>
        <td><input data-f="criteria.${i}.max" data-num="1" value="${esc(c.max)}" class="w-max" inputmode="decimal" aria-label="Marks"></td>
        <td><select data-f="criteria.${i}.strand" data-rerender="1" aria-label="Strand">${strandOpts.map(o => `<option value="${esc(o[0])}"${o[0] === (c.strand || "") ? " selected" : ""}>${esc(o[1])}</option>`).join("")}</select></td>
        <td>${s ? `<select data-f="criteria.${i}.band" data-num="1" data-rerender="1" aria-label="Band">${Array.from({length: mb}, (_, k) => k + 1).map(b => `<option value="${b}"${+c.band === b ? " selected" : ""}>${b}</option>`).join("")}</select>` : ""}</td>
        <td class="bq-act"><button class="btn ghost small" data-act="q-up" data-i="${i}" aria-label="Move up" ${i ? "" : "disabled"}>&#8593;</button><button class="btn ghost small" data-act="q-dup" data-i="${i}" aria-label="Duplicate">&#10697;</button><button class="btn danger small" data-act="q-del" data-i="${i}" aria-label="Remove">&#10005;</button></td>
      </tr>`;
    });
    h += `</tbody></table></div>`;
  }
  h += `</div></div><div class="card"><div class="card-head"><div><h2>Evidence by band</h2><p>Every band up to a strand’s highest needs a question behind it — an empty one would stop anyone being awarded above it.</p></div></div><div class="card-body" id="bCov">${coverageHTML()}</div></div>`;
  return h;
}

function checkListHTML(r){
  if(!r.errors.length && !r.warnings.length) return '<p class="bok">Ready — the marker will accept this rubric.</p>';
  return (r.errors.length ? '<p><b>' + r.errors.length + ' to fix before the marker will use it</b></p><ul class="bchk">' + r.errors.map(e => '<li>' + esc(e) + '</li>').join("") + '</ul>' : '<p class="bok">Ready — the marker will accept this rubric.</p>')
    + (r.warnings.length ? '<ul class="bchk">' + r.warnings.map(e => '<li class="warn">' + esc(e) + '</li>').join("") + '</ul>' : "");
}
function renderCheck(){
  const r = check(), d = r.d;
  const total = d.criteria.reduce((t, c) => t + (+c.max || 0), 0);
  return `<div class="card"><div class="card-head"><div><h2>${esc(d.title || "Untitled rubric")}</h2><p>${d.strands.length} strand${d.strands.length === 1 ? "" : "s"} · ${d.criteria.length} ${esc(d.criteria.length === 1 ? d.noun.item : (d.noun.items || d.noun.item + "s"))} · ${total} marks</p></div>
    <span class="iobar flush"><button class="btn" data-act="marker">Open in marker</button></span></div>
  <div class="card-body" id="bCheckList">${checkListHTML(r)}</div></div>
  <div class="card"><div class="card-head"><div><h2>Evidence by band</h2></div></div><div class="card-body" id="bCov">${coverageHTML()}</div></div>
  <div class="card"><div class="card-head"><div><h2>Save the rubric</h2><p>The builder keeps a draft in this browser as you go. To keep the rubric, share it, or open it on another computer, download it.</p></div></div>
  <div class="card-body"><div class="iobar" style="flex-wrap:wrap">
    <button class="btn" data-act="dl-json">Download rubric (.json)</button>
    <button class="btn ghost" data-act="dl-js">Download for the site (rubric-data.js)</button>
    <button class="btn ghost" data-act="copy">Copy as JSON</button>
  </div>
  <p class="hint">The <code>.json</code> opens in the rubric marker from any computer. <code>rubric-data.js</code> is the same rubric wrapped to sit beside a unit page on this site, like <code>year7-science/space/rubric-data.js</code>.</p>
  ${d.attribution ? '<p class="hint">' + esc(d.attribution) + ' This line is saved with the rubric and shown on its Rubric reference tab.</p>' : ""}
  </div></div>`;
}

const RENDER = {task: renderTask, strands: renderStrands, questions: renderQuestions, check: renderCheck};
function render(){
  /* keep focus and caret across a rebuild */
  const a = document.activeElement, f = a && a.dataset && a.dataset.f;
  const sel = f && "selectionStart" in a ? [a.selectionStart, a.selectionEnd] : null;
  const y = window.scrollY;
  $("#bPanel").innerHTML = RENDER[tab]();
  $("#bNotice").innerHTML = notice ? '<div class="note bnote">' + notice + '</div>' : "";
  $$(".tab").forEach(t => t.setAttribute("aria-selected", String(t.dataset.tab === tab)));
  document.body.className = document.body.className.replace(/\btheme-\S+/g, "").trim() + (doc.theme ? " theme-" + doc.theme : "");
  if(f){
    const el = app.querySelector('[data-f="' + f + '"]');
    if(el){ el.focus({preventScroll: true}); if(sel) try{ el.setSelectionRange(sel[0], sel[1]); }catch(e){} }
  }
  window.scrollTo(0, y);
  derived();
}
/* everything computed from the rubric that can change while typing,
   updated without touching any input */
let derivedTimer = null;
function derived(){
  clearTimeout(derivedTimer);
  derivedTimer = setTimeout(() => {
    const r = check();
    const ts = $("#tStrands"), tq = $("#tQuestions"), tc = $("#tCheck");
    if(ts) ts.textContent = doc.strands.length || "";
    if(tq) tq.textContent = doc.criteria.length || "";
    if(tc){ tc.textContent = r.errors.length ? r.errors.length + " to fix" : "ready"; tc.classList.toggle("bad", !!r.errors.length); }
    const cl = $("#bCheckList"); if(cl) cl.innerHTML = checkListHTML(r);
    const cv = $("#bCov"); if(cv) cv.innerHTML = coverageHTML();
    const meta = $("#bMeta");
    if(meta){ const t = doc.criteria.reduce((n, c) => n + (+c.max || 0), 0); meta.textContent = (doc.title || "Untitled") + " · " + t + " marks"; }
    doc.strands.forEach((s, i) => {
      const n = doc.criteria.filter(c => c.strand === s.id), m = n.reduce((t, c) => t + (+c.max || 0), 0);
      const el = $("#sMarks" + i); if(el) el.textContent = n.length + " question" + (n.length === 1 ? "" : "s") + " · " + m + " mark" + (m === 1 ? "" : "s");
      for(let b = 1; b <= 4; b++){
        const ev = $("#ev" + i + "_" + b); if(!ev) continue;
        const auto = autoEvidence(doc, s.id, b);
        ev.textContent = auto ? "evidence: " + auto : "no question tagged to this band yet";
        ev.classList.toggle("none", !auto);
        const qi = app.querySelector(`[data-f="strands.${i}.bands.${b-1}.q"]`);
        if(qi) qi.placeholder = auto || "filled from the questions tagged to this band";
      }
    });
    save();
  }, 120);
}

/* ============================ EDITING ============================ */
function setPath(obj, path, val){
  const ks = path.split(".");
  let o = obj;
  for(let i = 0; i < ks.length - 1; i++){
    const k = /^\d+$/.test(ks[i]) ? +ks[i] : ks[i];
    if(o[k] == null) o[k] = /^\d+$/.test(ks[i+1]) ? [] : {};
    o = o[k];
  }
  o[ks[ks.length - 1]] = val;
}
function onInput(e){
  const el = e.target, f = el.dataset && el.dataset.f;
  if(!f) return;
  let v = el.value;
  if(el.dataset.num){
    const t = String(v).trim().replace(",", ".");
    v = t === "" ? (f === "total" ? "" : 0) : (isNaN(+t) ? t : +t);
  }
  if(f === "theme" && v === "") delete doc.theme;
  else setPath(doc, f, v);
  /* a strand's criteria lose their band when the strand's ceiling drops */
  const m = f.match(/^strands\.(\d+)\.maxBand$/);
  if(m){ const s = doc.strands[+m[1]]; doc.criteria.forEach(c => { if(c.strand === s.id && +c.band > +s.maxBand) c.band = +s.maxBand; }); }
  const cm = f.match(/^criteria\.(\d+)\.strand$/);
  if(cm){ const c = doc.criteria[+cm[1]], s = doc.strands.find(x => x.id === c.strand);
    if(!s) c.strand = null; else if(!(+c.band >= 1 && +c.band <= (+s.maxBand || 4))) c.band = 1; }
  if(el.dataset.rerender && e.type === "change") render(); else derived();
}
function insertSnippet(t){
  const el = lastText && document.contains(lastText) ? lastText : null;
  if(!el){ try{ navigator.clipboard.writeText(t); }catch(e){} toast("Click in a descriptor or comment box first — copied instead"); return; }
  const a = el.selectionStart != null ? el.selectionStart : el.value.length, b = el.selectionEnd != null ? el.selectionEnd : a;
  const before = el.value.slice(0, a), sp = before && !/\s$/.test(before) ? " " : "";
  el.value = before + sp + t + el.value.slice(b);
  el.focus(); const p = (before + sp + t).length; el.setSelectionRange(p, p);
  onInput({target: el, type: "input"});
}

/* booklet paste: "Q3.2 (2 marks)", "Question 4b [3 marks]", "5(a) (1 mark)" */
function parseBooklet(text){
  const out = [], seen = new Set();
  const re = /(?:^|[^\w.])(?:Q(?:uestion)?\s*)?(\d+(?:\.\d+)?)\s*(?:\(?\s*([a-h]|[ivx]{1,4}|[a-h][ivx]{1,4})\s*\)?)?\s*[(\[]\s*(\d+(?:\.5)?)\s*(?:marks?|m)\s*[)\]]/gi;
  let m;
  while((m = re.exec(String(text)))){
    const q = "Q" + m[1], sub = (m[2] || "").toLowerCase(), max = +m[3];
    const key = q + "|" + sub;
    if(seen.has(key) || !(max > 0)) continue;
    seen.add(key); out.push({q, sub, max});
  }
  return out;
}
function pastePreview(){
  if(!paste.rows.length) return '<p class="hint">Nothing recognised yet.</p>';
  return '<p class="hint">' + esc(paste.rows.map(r => r.q + (r.sub ? "(" + r.sub + ")" : "") + " · " + r.max + "m").join("   ")) + '</p>';
}
function addCriterion(c, at){
  const row = Object.assign({id: "", q: "", sub: "", label: "", part: doc.parts[doc.parts.length - 1].id, strand: null, band: 1, max: 1, _new: true}, c);
  if(at == null) doc.criteria.push(row); else doc.criteria.splice(at, 0, row);
  return row;
}
function nextQ(){
  const ns = doc.criteria.map(c => parseFloat(String(c.q).replace(/^\D+/, ""))).filter(n => !isNaN(n));
  return "Q" + (ns.length ? Math.floor(Math.max(...ns)) + 1 : 1);
}
const qSortKey = c => [parseFloat(String(c.q).replace(/^\D+/, "")) || 0, String(c.sub || "")];

const ACT = {
  "s-add"(){ doc.strands.push(newStrand(doc.strands)); render(); scrollToLast(".bstrand"); },
  "s-del"(i){
    const s = doc.strands[i], n = doc.criteria.filter(c => c.strand === s.id).length;
    if(!confirm("Remove strand " + (i + 1) + (s.name ? " (" + s.name.slice(0, 50) + ")" : "") + "?" + (n ? " Its " + n + " question" + (n === 1 ? "" : "s") + " will be left outside the rubric." : ""))) return;
    doc.criteria.forEach(c => { if(c.strand === s.id) c.strand = null; });
    doc.strands.splice(i, 1); render();
  },
  "s-up"(i){ if(i > 0){ [doc.strands[i-1], doc.strands[i]] = [doc.strands[i], doc.strands[i-1]]; render(); } },
  "s-down"(i){ if(i < doc.strands.length - 1){ [doc.strands[i+1], doc.strands[i]] = [doc.strands[i], doc.strands[i+1]]; render(); } },
  "p-add"(){ const id = nextPartId(); doc.parts.push({id, name: "Part " + id}); render(); },
  "p-del"(i){
    const p = doc.parts[i], n = doc.criteria.filter(c => c.part === p.id).length;
    if(n && !confirm(n + " question" + (n === 1 ? " is" : "s are") + " in " + p.name + ". Move " + (n === 1 ? "it" : "them") + " to " + doc.parts[i ? 0 : 1].name + " and remove the part?")) return;
    const to = doc.parts[i ? 0 : 1].id; doc.criteria.forEach(c => { if(c.part === p.id) c.part = to; });
    doc.parts.splice(i, 1); render();
  },
  "q-add"(){ const prev = doc.criteria[doc.criteria.length - 1];
    addCriterion({q: nextQ(), part: prev ? prev.part : doc.parts[0].id, strand: prev ? prev.strand : null}); render(); focusLast('[data-f$=".label"]'); },
  "q-dup"(i){ const c = clone(doc.criteria[i]); delete c.id; c._new = true;
    c.sub = c.sub ? (/^[a-h]$/.test(c.sub) ? String.fromCharCode(c.sub.charCodeAt(0) + 1) : c.sub + "2") : "b";
    if(!doc.criteria[i].sub) doc.criteria[i].sub = "a";
    doc.criteria.splice(i + 1, 0, c); render(); },
  "q-del"(i){ doc.criteria.splice(i, 1); render(); },
  "q-up"(i){ if(i > 0){ [doc.criteria[i-1], doc.criteria[i]] = [doc.criteria[i], doc.criteria[i-1]]; render(); } },
  "q-sort"(){ doc.criteria.sort((a, b) => { const x = qSortKey(a), y = qSortKey(b); return x[0] - y[0] || (x[1] < y[1] ? -1 : x[1] > y[1] ? 1 : 0); }); render(); toast("Sorted by question number"); },
  "paste"(){ paste = paste || {text: "", rows: []}; render(); const t = $("#bPasteText"); if(t) t.focus(); },
  "paste-close"(){ paste = null; render(); },
  "paste-add"(){
    if(!paste || !paste.rows.length){ toast("Nothing recognised to add"); return; }
    const part = ($("#bPastePart") || {}).value || doc.parts[0].id;
    const have = new Set(doc.criteria.map(c => c.q + "|" + (c.sub || "")));
    let n = 0;
    paste.rows.forEach(r => { if(have.has(r.q + "|" + r.sub)) return; addCriterion({q: r.q, sub: r.sub, max: r.max, part}); n++; });
    paste = null; render(); toast(n + " question" + (n === 1 ? "" : "s") + " added — now tag each to a strand and band");
  },
  "pick"(i){ pickFor = i === "new" ? "new" : +i; openPicker(); },
  "snip"(i, el){ insertSnippet(el.dataset.t); },
  "new"(){ if(!confirm("Start a new, empty rubric? Download this one first if you want to keep it.")) return;
    doc = blank(); notice = ""; tab = "task"; render(); toast("New rubric"); },
  "open"(){ $("#bFile").click(); },
  "fork"(){
    if(!confirm("Make a copy of this rubric with a new id? Classes saved against the original will not open in the copy.")) return;
    ["storageKey","save","demo","fileStem","back"].forEach(k => delete doc[k]);
    doc.id = ""; doc.title = (doc.title || "") + " (copy)"; notice = "This is now a new rubric, separate from the one it was copied from."; render();
  },
  "marker"(){
    const r = check();
    if(r.errors.length){ tab = "check"; render(); toast("Fix the problems listed first — the marker would refuse it"); return; }
    store.set("rubric-marker:last", JSON.stringify(r.d));
    const w = window.open(MARKER, "_blank");
    if(!w) location.href = MARKER;
  },
  "dl-json"(){ const r = check(); download((r.d.fileStem || r.d.id) + "-rubric-definition.json", JSON.stringify(r.d, null, 2), "application/json");
    if(r.errors.length) toast("Downloaded — but it has " + r.errors.length + " problem" + (r.errors.length === 1 ? "" : "s") + " to fix before the marker will use it"); },
  "dl-js"(){ const r = check(); download("rubric-data.js", dataJS(r.d), "text/javascript"); },
  "copy"(){ const r = check(); try{ navigator.clipboard.writeText(JSON.stringify(r.d, null, 2)).then(() => toast("Copied")); }catch(e){ toast("Couldn’t copy"); } },
  "restore-prev"(){ const p = store.get(PREVIOUS); if(p){ try{ doc = tidy(JSON.parse(p)); }catch(e){} } store.del(PREVIOUS); notice = ""; render(); toast("Back to your previous draft"); },
  "dismiss"(){ notice = ""; render(); },
  "example"(i){ loadScriptRubric(EXAMPLES[+i].src); }
};
function scrollToLast(sel){ const all = $$(sel); if(all.length) all[all.length - 1].scrollIntoView({block: "start"}); }
function focusLast(sel){ const all = $$(sel); if(all.length) all[all.length - 1].focus(); }

function dataJS(d){
  return "/* " + (d.title || "Rubric") + " — rubric for the rubric marker (assets/js/rubric.js).\n"
    + "   Written by tools/rubric-builder.html; open it there to edit, or edit the JSON\n"
    + "   below by hand and keep it valid JSON. After editing on the site, run\n"
    + "   node tools/test-rubric-marker.js. */\nwindow.RUBRIC = " + JSON.stringify(d, null, 2) + ";\n";
}
function download(name, text, type){
  const b = new Blob([text], {type}); const u = URL.createObjectURL(b);
  const a = document.createElement("a"); a.href = u; a.download = name; document.body.appendChild(a); a.click(); a.remove();
  setTimeout(() => URL.revokeObjectURL(u), 1500);
}

/* ============================ CURRICULUM PICKER ============================ */
function openPicker(){
  const p = document.getElementById("bPick");
  if(!VC){
    p.innerHTML = `<div class="bpick-in card"><div class="card-head"><div><h2>Curriculum codes</h2></div><button class="btn ghost small" data-pick="close">Close</button></div>
      <div class="card-body"><p>The curriculum data isn’t on this site yet. Type the code into the strand (e.g. <code>VC2S8U03</code>) — it is shown on the rubric just the same.</p></div></div>`;
    p.hidden = false; return;
  }
  const subjects = VC.subjects.map(s => [s.id, s.name]);
  const s0 = (pickFor !== "new" && byCode(codesOf(doc.strands[pickFor] || {})[0] || "")) || null;
  p.innerHTML = `<div class="bpick-in card" role="dialog" aria-modal="true" aria-label="Victorian Curriculum content descriptions">
  <div class="card-head"><div><h2>${pickFor === "new" ? "Start a strand from the curriculum" : "Link strand " + (pickFor + 1) + " to the curriculum"}</h2>
    <p>Victorian Curriculum F–10 Version 2.0 · content descriptions</p></div><button class="btn ghost small" data-pick="close">Close</button></div>
  <div class="card-body">
    <div class="grid3">
      <label class="field"><span>Learning area</span><select id="pkSub">${subjects.map(o => `<option value="${esc(o[0])}"${s0 && s0.subjectId === o[0] ? " selected" : ""}>${esc(o[1])}</option>`).join("")}</select></label>
      <label class="field"><span>Level</span><select id="pkLev"></select></label>
      <label class="field"><span>Search</span><input id="pkQ" placeholder="word or code"></label>
    </div>
    <div class="bpick-list" id="pkList"></div>
    <p class="hint">${esc(VC.attribution || ATTRIBUTION)}</p>
  </div></div>`;
  p.hidden = false;
  const lev = () => { const sub = VC.subjects.find(s => s.id === document.getElementById("pkSub").value);
    document.getElementById("pkLev").innerHTML = '<option value="">All levels</option>' + sub.levels.map(l => `<option${s0 && s0.level === l.level ? " selected" : ""}>${esc(l.level)}</option>`).join(""); };
  lev();
  document.getElementById("pkSub").onchange = () => { lev(); list(); };
  document.getElementById("pkLev").onchange = list;
  document.getElementById("pkQ").oninput = list;
  list();
  document.getElementById("pkQ").focus();
}
function list(){
  const sub = document.getElementById("pkSub").value, lev = document.getElementById("pkLev").value;
  const words = document.getElementById("pkQ").value.toLowerCase().split(/\s+/).filter(Boolean);
  const hits = CD.filter(c => c.subjectId === sub && (!lev || c.level === lev)
    && words.every(w => (c.code + " " + c.text + " " + c.substrand).toLowerCase().includes(w)));
  const cur = pickFor !== "new" && doc.strands[pickFor] ? codesOf(doc.strands[pickFor]) : [];
  let h = "", last = "";
  hits.slice(0, 120).forEach(c => {
    const head = "Level " + c.level + " · " + c.strand + (c.substrand && c.substrand !== c.strand ? " · " + c.substrand : "");
    if(head !== last){ h += '<h4>' + esc(head) + '</h4>'; last = head; }
    const on = cur.includes(c.code);
    h += `<div class="bpick-row"><span class="ckcode cur">${esc(c.code)}</span><span class="t">${esc(c.text)}</span>
      <button class="btn ${on ? "ghost" : ""} small" data-pick="${on ? "unlink" : "use"}" data-code="${esc(c.code)}">${pickFor === "new" ? "New strand" : on ? "Unlink" : "Link"}</button></div>`;
  });
  document.getElementById("pkList").innerHTML = h || '<p class="hint">No content descriptions match.</p>';
}
function onPick(e){
  const b = e.target.closest("[data-pick]"), p = document.getElementById("bPick");
  if(!b){ if(e.target === p) closePicker(); return; }
  const what = b.dataset.pick;
  if(what === "close"){ closePicker(); return; }
  const c = byCode(b.dataset.code);
  if(pickFor === "new"){
    const s = newStrand(doc.strands); s.code = c.code;
    doc.strands.push(s); closePicker(); tab = "strands"; render(); scrollToLast(".bstrand");
    const nm = $$('[data-f$=".name"]').pop(); if(nm) nm.focus();
    toast(c.code + " linked — write the row heading in your own words, then the bands");
    return;
  }
  const s = doc.strands[pickFor], codes = codesOf(s);
  s.code = (what === "use" ? [...codes, c.code] : codes.filter(x => x !== c.code)).join(", ");
  render(); list();
}
function closePicker(){ const p = document.getElementById("bPick"); p.hidden = true; p.innerHTML = ""; }

/* ============================ OPEN / SAVE ============================ */
function fromText(text){
  let t = String(text).replace(/^﻿/, "").trim();
  const m = t.match(/window\.RUBRIC\s*=\s*([\s\S]*?);?\s*$/);
  if(m && !/^[\[{]/.test(t)) t = m[1];
  const d = JSON.parse(t);
  if(d && d.format === FORMAT) return d;
  if(d && d.rubric && d.rubric.format === FORMAT) return d.rubric;
  throw new Error("not a rubric");
}
function adopt(d, msg){
  const cur = store.get(DRAFT);
  doc = tidy(clone(d));
  notice = msg || "";
  tab = "task"; render();
  if(cur && cur !== JSON.stringify(doc)) store.set(PREVIOUS, cur);
}
function loadScriptRubric(src){
  const had = window.RUBRIC; window.RUBRIC = undefined;
  const s = document.createElement("script"); s.src = src;
  s.onload = () => { const r = window.RUBRIC; window.RUBRIC = had; if(r) adopt(r, "Opened “" + esc(r.title) + "”. Edits change this rubric; use <b>Make this a new rubric</b> (Task · Advanced) to adapt a copy for another task."); };
  s.onerror = () => toast("Couldn’t load " + src);
  document.head.appendChild(s);
}
let saveTimer = null;
function save(){ clearTimeout(saveTimer); saveTimer = setTimeout(() => store.set(DRAFT, JSON.stringify(doc)), 300); }

/* ============================ WIRE ============================ */
function wire(){
  app.addEventListener("input", e => {
    if(e.target.id === "bPasteText"){ paste.text = e.target.value; paste.rows = parseBooklet(paste.text);
      $("#bPasteN").textContent = paste.rows.length; $("#bPastePrev").innerHTML = pastePreview(); return; }
    onInput(e);
  });
  app.addEventListener("change", e => { if(e.target.dataset && e.target.dataset.rerender) onInput(e); });
  app.addEventListener("focusin", e => { if(e.target.dataset && e.target.dataset.text) lastText = e.target; });
  app.addEventListener("click", e => {
    const t = e.target.closest(".tab[data-tab]");
    if(t){ tab = t.dataset.tab; render(); window.scrollTo(0, 0); return; }
    if(e.target.closest("#bPick")){ onPick(e); return; }
    const b = e.target.closest("[data-act]");
    if(b && ACT[b.dataset.act]){ e.preventDefault(); const i = b.dataset.i; ACT[b.dataset.act](/^\d+$/.test(i || "") ? +i : i, b); }
  });
  document.addEventListener("keydown", e => { if(e.key === "Escape" && !document.getElementById("bPick").hidden) closePicker(); });
  $("#bFile").onchange = e => {
    const f = e.target.files[0]; e.target.value = "";
    if(!f) return;
    const r = new FileReader();
    r.onload = () => { try{ const d = fromText(r.result); adopt(d, "Opened “" + esc(d.title) + "” from " + esc(f.name) + "."); }
      catch(err){ toast("That file isn’t a rubric or a class saved from the marker"); } };
    r.readAsText(f);
  };
}

/* expose for tests and the console */
window.rubricBuilder = {
  get doc(){ return doc; }, set doc(d){ doc = tidy(d); render(); },
  exportRubric, check, parseBooklet, autoEvidence: (sid, b) => autoEvidence(doc, sid, b), render, act: (n, i) => ACT[n](i),
  showTab: t => { tab = t; render(); }, adopt
};

/* ============================ BOOT ============================ */
shell();
wire();
const incoming = store.get(INCOMING);
store.del(INCOMING);
const draft = store.get(DRAFT);
if(incoming){
  try{ const d = JSON.parse(incoming); doc = tidy(d);
    if(draft && draft !== incoming){ store.set(PREVIOUS, draft);
      notice = "Opened “" + esc(d.title) + "” from the marker. <button class=\"btn ghost small\" data-act=\"restore-prev\">Back to the draft you had before</button>"; }
    else notice = "Opened “" + esc(d.title) + "” from the marker.";
  }catch(e){ doc = null; }
}
if(!doc && draft){
  try{ doc = tidy(JSON.parse(draft)); notice = "Carrying on with the draft saved in this browser. <button class=\"btn ghost small\" data-act=\"new\">Start a new rubric</button>"; }catch(e){ doc = null; }
}
if(!doc){
  doc = blank();
  notice = "Build a rubric step by step, or start from one that already exists: "
    + "<button class=\"btn ghost small\" data-act=\"open\">Open a rubric file…</button>"
    + EXAMPLES.map((x, i) => " <button class=\"btn ghost small\" data-act=\"example\" data-i=\"" + i + "\">" + esc(x.label) + "</button>").join("")
    + (STARTER ? " or download the <a href=\"" + esc(STARTER) + "\" download>starter rubric</a> and open it." : "");
}
render();
})();
