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
let baseline = null;       // the rubric as it was opened, to compare edits against
const BASELINE = "rubric-builder:baseline";

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
  d.strands.forEach(s => { if(Array.isArray(s.focus) && !s.focus.length) delete s.focus; });
  if(d.strands.some(s => s.code && /^VC2/.test(s.code)) && !d.attribution) d.attribution = ATTRIBUTION;
  /* a change that alters what entered marks mean gets a new version number,
     so a class marked on the old one can be told what changed */
  if(baseline && typeof rubricDiff === "function"
     && rubricDiff(baseline, d).some(x => x.kind !== "id" && MARK_CHANGES.includes(x.kind)))
    d.version = (Number(baseline.version) || 1) + 1;
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
  }).replace(/^total is/, "The paper total is").replace(/^[a-z]/, c => c.toUpperCase());
}
function check(){
  const d = exportRubric();
  const r = (typeof validateRubric === "function") ? validateRubric(d) : {errors: ["The marking engine didn’t load, so the rubric can’t be checked."], warnings: []};
  return {errors: r.errors.map(e => friendly(e, d)), warnings: r.warnings.map(e => friendly(e, d)).concat(defaultWarnings()), d};
}

/* ============================ RUBRICS IN USE ============================
   A class marked on this rubric in this browser: the marker autosaves under
   the rubric's storageKey on the same site, so the builder can see it. Looked
   up under both the opened rubric's key and the edited one's. */
const keyOf = r => r && (r.storageKey || (r.id ? "rubric-marker:" + r.id : ""));
const hasMark = (s, id) => s && s.q && (typeof s.q[id] === "number" || s.q[id] === true);
function classInUse(){
  const keys = [...new Set([keyOf(baseline), keyOf(doc)].filter(Boolean))];
  for(const k of keys){
    const raw = store.get(k);
    if(!raw) continue;
    try{
      const d = JSON.parse(raw), students = Array.isArray(d.students) ? d.students : [];
      const marked = students.filter(s => Object.keys(s.q || {}).length || (s.parked || []).length);
      if(marked.length) return {key: k, cls: (d.meta || {}).cls || "", students, marked: marked.length,
        marks: students.reduce((n, s) => n + Object.keys(s.q || {}).length, 0), rubric: d.rubric || null};
    }catch(e){}
  }
  return null;
}
const sName = sid => { const i = doc.strands.findIndex(x => x.id === sid);
  return i < 0 ? "a removed strand" : "strand " + (i + 1) + (doc.strands[i].name ? " (“" + doc.strands[i].name.slice(0, 40) + (doc.strands[i].name.length > 40 ? "…" : "") + "”)" : ""); };
/* each change since the rubric was opened (or since the class was marked),
   with what it does to the marks in this browser */
function impact(){
  const cls = classInUse(), ref = (cls && cls.rubric) || baseline;
  if(!ref || typeof rubricDiff !== "function") return {cls, items: []};
  const st = cls ? cls.students : [];
  const n = (pred) => st.filter(pred).length;
  const pl = (k, w) => k + " " + w + (k === 1 ? "" : "s");
  const items = rubricDiff(ref, exportRubric()).filter(x => MARK_CHANGES.includes(x.kind)).map(x => {
    let text = describeChange(x, sName), level = "info";
    if(x.kind === "removed"){
      const k = n(s => hasMark(s, x.id));
      if(k){ level = "warn"; text += " " + pl(k, "student") + " in " + (cls.cls || "the class") + " have a mark for it; the marker will set " + (k === 1 ? "it" : "them") + " aside, not delete " + (k === 1 ? "it" : "them") + "."; }
    } else if(x.kind === "max"){
      const over = n(s => typeof (s.q || {})[x.id] === "number" && s.q[x.id] > x.to);
      const k = n(s => hasMark(s, x.id));
      if(over){ level = "warn"; text += " " + pl(over, "mark") + " already entered " + (over === 1 ? "is" : "are") + " over " + x.to + " and will be set aside."; }
      if(k - over > 0){ if(level !== "warn") level = "caution"; text += " " + pl(k - over, "mark") + " entered out of " + x.from + " will now be read as out of " + x.to + " — check " + (k - over === 1 ? "it" : "them") + "."; }
    } else if(x.kind === "moved"){
      const k = n(s => hasMark(s, x.id));
      if(k){ level = "caution"; text += " " + pl(k, "mark") + " already entered will count towards the new band."; }
    } else if(x.kind === "strand-removed"){
      const k = n(s => s.override && Number.isInteger(s.override[x.id]));
      if(k){ level = "warn"; text += " " + pl(k, "band override") + " for it will be set aside."; }
    } else if(x.kind === "maxband"){
      const k = x.to < x.from ? n(s => s.override && Number.isInteger(s.override[x.id]) && s.override[x.id] > x.to) : 0;
      if(k){ level = "warn"; text += " " + pl(k, "band override") + " above band " + x.to + " will be set aside."; }
    } else if(x.kind === "id"){
      level = cls ? "warn" : "caution";
      text += cls ? " " + (cls.cls || "The class") + "’s marks stay saved under the old id; this version starts empty." : "";
    }
    return {kind: x.kind, id: x.id, level, text};
  });
  return {cls, items};
}
function impactHTML(){
  const {cls, items} = impact();
  if(!cls && !items.length) return "";
  const head = cls
    ? "<b>" + esc(cls.cls || "A class") + "</b> has " + cls.marks + " mark" + (cls.marks === 1 ? "" : "s") + " for " + cls.marked + " student" + (cls.marked === 1 ? "" : "s") + " on this rubric, saved in this browser."
    : "Compared with the rubric as you opened it — for any class already marked on it:";
  const body = items.length
    ? '<ul class="bchk bimpact">' + items.map(x => '<li class="' + x.level + '">' + esc(x.text) + '</li>').join("") + '</ul>'
      + '<p class="hint">Nothing is lost: the marker sets aside any mark this version can’t hold, keeps it in every save, and puts it back if the question returns. Renumbering a question is always safe — marks follow the question, not its number.</p>'
    : '<p class="bok">Nothing you’ve changed affects those marks.</p>';
  return '<div class="card bimpact-card"><div class="card-head"><div><h2>Marks already entered</h2><p>' + head + '</p></div></div><div class="card-body" id="bImpact">' + body + '</div></div>';
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
let stdWhole = false;      // show whole standards, not just the linked strand's sentences

/* Towards / At / Above, from the continuum. VCAA writes one achievement
   standard per level (or pair of levels) and nothing graded inside it, so
   the honest "towards" is the standard of the level below and "above" the
   standard of the level above. Each column is narrowed to the linked code's
   sub-strand (Science) or strand (Mathematics), using the tags
   tools/build-curriculum.py gives each sentence. */
/* How closely a sentence matches the linked content description(s): the
   distinctive words they share, each weighted by how few of the column's
   sentences use it. Common curriculum verbs (explain, describe …) don't
   count — every sentence has them. Score 0 = nothing in common. */
const STOPW = new Set(("the and for with that this from into their them they students student use using uses used including include includes "
  + "level end by of to in on a an as is are be can or its it at how what when which why who between different other such these those than "
  + "through about also both more most each ways way may will within range variety selected select appropriate "
  + "explain explains describe identify represent represented investigate investigated model models analyse apply compare "
  + "demonstrate predict design construct relate related observe solve problem problems simple key processes process").split(" "));
const stemsOf = t => new Set((String(t || "").toLowerCase().match(/[a-z]+/g) || [])
  .filter(w => w.length > 2 && !STOPW.has(w)).map(w => w.replace(/s$/, "").slice(0, 6)).filter(w => !STOPW.has(w)));
/* ---- discrete skills ----
   VCAA writes several skills into one sentence ("substitute into formulas,
   find unknown values, …, expand binomial expressions and factorise …").
   A band is awarded only when every question behind it is done, so a
   descriptor has to name what its questions show: one skill, usually. Split
   at a comma, semicolon or "and" ONLY where the next word starts a new verb
   phrase, and only once the piece before it has an object — so "prime,
   composite, square and triangular numbers" stays whole, and so do paired
   verbs on one object ("add and subtract fractions", "represent and explain
   the effects of forces"). Participles ("giving reasons", "justifying
   choices") qualify the skill before them and stay attached. */
const VERBS = new Set(("use apply solve find order add subtract multiply divide connect round convert compare represent describe explain "
  + "identify recognise interpret investigate calculate estimate measure locate list sketch graph plot factorise expand manipulate "
  + "substitute simplify establish determine design construct create conduct plan analyse evaluate discuss examine distinguish "
  + "classify model relate provide demonstrate undertake observe make propose predict select document communicate write sequence "
  + "formulate refine justify verify choose name state label read assign record collect generate organise process summarise "
  + "transform reflect translate rotate prove define perform implement explore experiment test describe sort continue extend "
  + "count partition share approximate interpret pose plan report state rearrange inform decide critique develop express judge "
  + "illustrate assess build draw").split(/\s+/));
/* "states", "labels" (a teacher's descriptor: "…, and states the period")
   count as verbs only after "and" — after a bare comma, "measures of
   central tendency" is a noun */
const isBase = w => VERBS.has(w);
const isVerb = (w, andJoin) => isBase(w) || (andJoin && w.length > 3 && ((/s$/.test(w) && VERBS.has(w.slice(0, -1))) || (/es$/.test(w) && VERBS.has(w.slice(0, -2)))));
function splitSkills(text){
  let t = String(text || "").trim()
    .replace(/^By the end of Levels? [^,]+,\s*students\s+/i, "").replace(/^(They|Students|Can)\s+/i, "").replace(/[.;:\s]+$/, "");
  const out = [];
  t.split(/\s*;\s*/).forEach(part => {
    const re = /(,\s+and\s+|,\s+|\s+and\s+)([A-Za-z]+)/g;
    let start = 0, m;
    while((m = re.exec(part))){
      const next = m[2].toLowerCase(), andJoin = /and/.test(m[1]);
      if(!isVerb(next, andJoin)) continue;
      const left = part.slice(start, m.index);
      const words = (left.toLowerCase().match(/[a-z]+/g) || []);
      if(!words.some(w => !isBase(w) && w !== "and")) continue;         // no object yet: "add and subtract"
      /* shared object: "write and order decimals". Base forms only — a plural
         noun ("experiments", "graphs") is not a verb waiting for an object */
      if(isBase(words[words.length - 1])) continue;
      /* "use them to model situations and solve problems": after "to <verb>",
         a plain "and" carries on the same purpose */
      if(m[1].trim() === "and" && /\bto ([a-z]+)/.test(left.toLowerCase()) && isBase(left.toLowerCase().match(/\bto ([a-z]+)/)[1])) continue;
      out.push(left); start = m.index + m[1].length;
    }
    out.push(part.slice(start));
  });
  return out.map(x => x.replace(/^[\s,]+|[\s,]+$/g, "").replace(/^and\s+/i, "").replace(/^(they|students)\s+/i, "").replace(/^./, c => c.toLowerCase())).filter(x => x.length > 2);
}

function rankItems(texts, ref){
  const R = stemsOf(ref), S = texts.map(stemsOf), n = texts.length, df = {};
  S.forEach(set => set.forEach(w => df[w] = (df[w] || 0) + 1));
  /* divided by √(the skill's own word count), so a long skill doesn't win
     just by sharing more words than a short, exact one */
  return texts.map((text, j) => ({text, score: [...S[j]].filter(w => R.has(w)).reduce((t, w) => t + Math.log((n + 1) / df[w]), 0) / Math.sqrt(Math.max(1, S[j].size))}));
}

/* A content description can bundle several skills too (VC2M8A02: graph
   linear relations; solve linear equations and inequalities; verify
   solutions by substitution). strand.focus lists the ones this strand
   assesses; empty means the whole description. */
const codeSkills = known => [].concat(...known.map(k => splitSkills(k.text)));
function strandRef(s, known){
  const f = Array.isArray(s.focus) ? s.focus.filter(Boolean) : [];
  return f.length ? f.join(" ") : known.map(x => x.text).join(" ");
}

function ladder(k, whole = stdWhole){
  const subj = VC.subjects.find(x => x.id === k.subjectId);
  const i = subj.levels.findIndex(l => l.level === k.level);
  const col = (lv, role) => {
    if(!lv) return {role, level: null, items: [], note: role === "towards" ? "No lower level in the curriculum data here." : "Level " + k.level + " is the top of the F–10 curriculum."};
    const tagged = Array.isArray(lv.standard) && lv.standard.length ? lv.standard : null;
    if(!tagged && !lv.achievement){
      /* Level 10A: no achievement standard, so its content descriptions for the strand stand in */
      const cds = CD.filter(c => c.subjectId === k.subjectId && c.level === lv.level && (whole || c.strand === k.strand));
      return {role, level: lv.level, items: rankItems([].concat(...cds.map(c => splitSkills(c.text))), ref),
              note: "VCAA sets no achievement standard for Level " + lv.level + "; these are its content descriptions" + (whole ? "." : " for " + k.strand + ".")};
    }
    let items = tagged ? tagged : sentences(lv.achievement).map(t => ({text: t.trim()}));
    let note = "";
    if(tagged && !whole){
      const bySub = items.filter(x => x.strand === k.strand && x.sub === k.substrand);
      const byStrand = items.filter(x => x.strand === k.strand);
      if(bySub.length) items = bySub;
      else if(byStrand.length){ items = byStrand; note = "Nothing at this level for " + k.substrand + " alone; showing all of " + k.strand + "."; }
      else note = "Nothing at this level for " + k.strand + "; showing the whole standard.";
    }
    return {role, level: lv.level, items: rankItems([].concat(...items.map(x => splitSkills(x.text))), ref), note};
  };
  /* rank against every linked code the strand carries (k is the first) */
  const ref = (k.ref || k.text);
  return [col(subj.levels[i - 1], "towards"), col(subj.levels[i], "at"), col(subj.levels[i + 1], "above")];
}
/* ============================ DEFAULT STATEMENTS ============================
   Drafts for an empty strand, from its curriculum code's Towards / At /
   Above sentences. They are starting points: every one is flagged on the
   Check tab until it has been edited, and "Fill" never touches a box that
   already has text. The wording stays VCAA's — "They represent and explain …"
   becomes "Can represent and explain …" for a descriptor and "represent and
   explain …" for "Ava can now …" — so no verb has to be conjugated by rule. */
const TOP_NEXT = "apply this in less familiar contexts, explaining {their} reasoning fully";
function baseForm(t){
  return String(t || "").trim()
    .replace(/^By the end of Levels? [^,]+,\s*students\s+/i, "")
    .replace(/^(They|Students)\s+/, "")
    .replace(/[.;:\s]+$/, "")
    .replace(/^./, c => c.toLowerCase());
}
/* which column feeds each band: 1 Towards, top Above, the rest At */
function roleOfBand(b, mb){
  if(mb === 1) return "at";
  if(b === 1) return "towards";
  if(b === mb && mb >= 3) return "above";
  return "at";
}
/* One skill per band: each band's default is the single sentence in its
   column that best matches the linked content description. A level with
   nothing relevant (Levels 5–6 have no forces; nothing sits above 9–10)
   leaves the band blank for the teacher, rather than filling it with a
   sentence about something else. Earlier versions put the whole sub-strand
   into every band — five skills in one descriptor, which no single band of
   questions can evidence. */
function defaultsFor(s){
  if(!VC) return null;
  const known = codesOf(s).map(byCode).filter(Boolean);
  if(!known.length) return null;
  const k = Object.assign({}, known[0], {ref: strandRef(s, known)});
  const cols = ladder(k, false), by = {}, lvl = {};
  cols.forEach(c => { by[c.role] = c.items; lvl[c.role] = c.level; });
  /* the n closest skills in a column, back in curriculum order */
  /* a second pick has to be at least half as close as the first, or the
     band is left for the teacher rather than filled with a near-miss */
  const top = (role, n) => {
    const r = (by[role] || []).map((x, j) => Object.assign({j}, x)).filter(x => x.score > 0).sort((a, b) => b.score - a.score);
    return r.filter((x, q) => q === 0 || x.score >= r[0].score / 2).slice(0, n).sort((a, b) => a.j - b.j).map(x => x.text);
  };
  const best = role => top(role, 1)[0] || "";
  const mb = +s.maxBand || 4;
  /* one chosen skill makes a proper row heading; otherwise the description, flagged on Check */
  const focus = Array.isArray(s.focus) ? s.focus.filter(Boolean) : [];
  const head = focus.length === 1 ? focus[0] : k.text;
  const out = {name: head.charAt(0).toUpperCase() + head.slice(1), bands: [], can: [], next: [], start: "", gaps: [], picks: {}};
  const roles = Array.from({length: mb}, (_, j) => roleOfBand(j + 1, mb));
  /* two At bands take the two closest At skills, so they progress rather than repeat */
  const atBands = roles.map((r, j) => r === "at" ? j + 1 : 0).filter(Boolean), atPicks = top("at", atBands.length);
  for(let b = 1; b <= mb; b++){
    const role = roles[b-1];
    const t = role === "at" ? (atPicks[atBands.indexOf(b)] || "") : best(role);
    out.bands[b-1] = t ? "Can " + t + "." : "";
    out.can[b-1] = t;
    if(t) out.picks[t] = (out.picks[t] ? out.picks[t] + ", " : "band ") + b;
    else out.gaps.push("band " + b + (role === "at" && atPicks.length ? " (only " + atPicks.length + " At skill" + (atPicks.length === 1 ? "" : "s") + " match" + (atPicks.length === 1 ? "es" : "") + ")"
      : lvl[role] ? " (nothing at Level " + lvl[role] + " matches)" : " (no level " + (role === "towards" ? "below" : "above") + ")"));
  }
  /* a band's next step is the next band up that has something in it — an
     empty band is skipped, as it can't be awarded */
  for(let b = 1; b <= mb; b++){
    if(!out.can[b-1]) continue;
    const up = out.can.slice(b).find(Boolean);
    out.next[b-1] = up || TOP_NEXT;
  }
  out.start = best("towards") || best("at");
  return out;
}
/* fill the empty boxes of strand i; returns how many were filled */
function fillDefaults(i){
  const s = doc.strands[i], d = defaultsFor(s);
  if(!d) return 0;
  fillDefaults.gaps = d.gaps;
  let n = 0;
  const put = (get, set, v) => { if(v && !String(get() || "").trim()){ set(v); n++; } };
  put(() => s.name, v => s.name = v, d.name);
  d.bands.forEach((v, j) => put(() => s.bands[j].d, x => s.bands[j].d = x, v));
  d.can.forEach((v, j) => put(() => s.can[j], x => s.can[j] = x, v));
  d.next.forEach((v, j) => put(() => s.next[j], x => s.next[j] = x, v));
  put(() => s.start, v => s.start = v, d.start);
  return n;
}
/* reminders for the Check tab: defaults left as they were, and two bands
   saying the same thing (the curriculum has one At standard; what lifts work
   from one At band to the next is the teacher's call) */
function defaultWarnings(){
  const w = [];
  doc.strands.forEach((s, i) => {
    const mb = +s.maxBand || 4, name = "Strand " + (i + 1);
    const d = defaultsFor(s);
    if(d){
      const left = [];
      if(s.name && s.name === d.name) left.push("row heading — the whole content description; shorten it to what students do");
      for(let b = 1; b <= mb; b++){
        if(s.bands[b-1].d && s.bands[b-1].d === d.bands[b-1]) left.push("band " + b + " descriptor");
        if(s.can[b-1] && s.can[b-1] === d.can[b-1]) left.push("band " + b + " “can now”");
        if(s.next[b-1] && s.next[b-1] === d.next[b-1]) left.push("band " + b + " next step");
      }
      if(s.start && s.start === d.start) left.push("band 0 first step");
      if(left.length) w.push(name + " still has default wording in " + left.length + " box" + (left.length === 1 ? "" : "es") + " (" + left.slice(0, 4).join(", ") + (left.length > 4 ? "…" : "") + "). Make it specific to this task.");
    }
    /* a band is awarded only when every question behind it is done, so a
       descriptor listing several separate skills can't match its evidence */
    for(let b = 1; b <= mb; b++){
      const k = splitSkills(s.bands[b-1].d).length;
      const q = doc.criteria.filter(c => c.strand === s.id && +c.band === b).length;
      if(k > 1 && k > q)
        w.push(name + ", band " + b + ": the descriptor names " + k + " separate skills, but " + (q ? "only " + q + " question" + (q === 1 ? " gives" : "s give") : "no question gives yet") + " evidence for it. Every question behind a band must be done for it to be awarded, so the descriptor should say what those questions show — trim it, or split the skills across bands or strands.");
    }
    for(let b = 1; b < mb; b++){
      const a = (s.bands[b-1].d || "").trim();
      if(a && a === (s.bands[b].d || "").trim())
        w.push(name + ": bands " + b + " and " + (b + 1) + " have the same descriptor. Say what lifts work from one to the other.");
    }
  });
  return w;
}

/* the band a column's sentences go to by default */
function bandFor(role, s){
  const mb = +s.maxBand || 4;
  if(role === "towards") return 1;
  if(role === "above") return mb;
  const at = doc.bands.findIndex((b, j) => j < mb && /\bat\b/i.test(b));
  return at >= 0 ? at + 1 : Math.max(1, mb - 1);
}

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
      <button class="btn ghost small" data-act="bank">Statement bank</button>
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
    const cs = codeSkills(known), focus = Array.isArray(s.focus) ? s.focus : [];
    if(cs.length > 1){
      h += `<div class="bfocus"><span class="bfocus-h">${cs.length} skills in ${esc(known.map(x => x.code).join(", "))} — which does this strand assess?</span>`
        + cs.map(t => `<button class="chipbtn" data-act="focus" data-i="${i}" data-t="${esc(t)}" aria-pressed="${focus.includes(t)}">${esc(cap(t))}</button>`).join("")
        + `<span class="hint">${focus.length ? "The standards below are ranked against the chosen skill" + (focus.length === 1 ? "" : "s") + "." : "None chosen: ranked against the whole description."}</span>`
        + `<button class="btn ghost small" data-act="split-strand" data-i="${i}">One strand per skill (${cs.length} strands)</button></div>`;
    }
    const k = Object.assign({}, known[0], {ref: strandRef(s, known)}), cols = ladder(k), picks = (defaultsFor(s) || {}).picks || {};
    const name = {towards: "Towards", at: "At", above: "Above"};
    h += `<div class="bladder"><div class="bladder-h"><b>Achievement standards</b>
        <span class="iobar flush"><button class="btn ghost small" data-act="defaults" data-i="${i}" title="Drafts from the Towards / At / Above sentences; boxes with text are left alone">Fill empty boxes with defaults</button>
        <button class="chipbtn" data-act="std-whole" aria-pressed="${stdWhole}">${stdWhole ? "Showing whole standards — show just " + esc(k.substrand) : "Showing " + esc(k.substrand) + " — show whole standards"}</button></span></div>
      <div class="bladder-cols">` + cols.map(c => {
        const b = bandFor(c.role, s);
        const top = Math.max(0, ...c.items.map(x => x.score));
        return `<div class="bcol ${c.role}"><h4>${name[c.role]}${c.level ? ` <span>Level ${esc(c.level)}</span>` : ""}${c.items.length ? ` <em>→ band ${b}</em>` : ""}</h4>`
          + (c.note ? `<p class="hint">${esc(c.note)}</p>` : "")
          + (c.items.length && !top ? `<p class="hint bnomatch">Nothing at this level matches ${esc(known.map(x => x.code).join(", "))} — the default leaves band ${b} for you to write.</p>` : "")
          + c.items.map(x => { const pk = !stdWhole && picks[x.text];
              return `<button class="chipbtn${pk ? " best" : ""}" data-act="snip" data-i="${i}" data-b="${b}" data-t="${esc(x.text)}"${pk ? ' title="Closest to the linked content description"' : ""}>${esc(cap(x.text))}${pk ? ` <span class="bpick-tag">default · ${esc(pk)}</span>` : ""}</button>`; }).join("")
          + `</div>`;
      }).join("") + `</div>
      <p class="hint">VCAA writes one achievement standard per level, so <b>Towards</b> and <b>Above</b> are the standards for the levels either side of ${esc(k.code)}’s. Each sentence is broken into its separate skills, because a band can only be awarded for what its questions show. Click a skill to add it to that band’s descriptor — or to the box you’re writing in, if it’s on this strand — then make it specific to the task.</p></div>`;
    h += `</div>`;
  } else if(codes.length && VC){
    h += `<p class="hint">${esc(codes.join(", "))} isn’t in the curriculum data here (Science 7–10, Mathematics 7–10A). It will still be shown on the rubric.</p>`;
  }
  h += `<div class="bbands">`;
  for(let b = 1; b <= mb; b++){
    const auto = autoEvidence(doc, s.id, b);
    h += `<div class="bband${auto ? "" : " bempty"}" id="bb${i}_${b}">
      <div class="bband-h"><span class="bnum b${b}">${b}</span> ${esc(doc.bands[b-1] || "")}
        <span class="bev ${auto ? "" : "none"}" id="ev${i}_${b}">${auto ? "evidence: " + esc(auto) : "no question — greyed out on the rubric, can’t be awarded"}</span></div>
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
                     : '<td class="bempty">empty — greyed out</td>';
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
  h += `</div></div><div class="card"><div class="card-head"><div><h2>Evidence by band</h2><p>A band with no question behind it is allowed: it is greyed out on the rubric and can’t be awarded, and a student who reaches the band above simply skips it.</p></div></div><div class="card-body" id="bCov">${coverageHTML()}</div></div>`;
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
  <div id="bImpactWrap">${impactHTML()}</div>
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
  $("#bNotice").innerHTML = (notice ? '<div class="note bnote">' + notice + '</div>' : "") + '<div id="bUse"></div>';
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
    const iw = $("#bImpactWrap"); if(iw) iw.innerHTML = impactHTML();
    /* off the Check tab, a one-line reminder while edits would touch entered marks */
    const use = $("#bUse");
    if(use){
      const im = tab === "check" ? null : impact();
      const warn = im ? im.items.filter(x => x.level !== "info").length : 0;
      use.innerHTML = im && im.cls ? '<div class="note bnote buse">' + esc(im.cls.cls || "A class") + ' has marks on this rubric in this browser. '
        + (warn ? '<b>' + warn + ' of your changes affect them</b> — see <button class="btn ghost small" data-act="goto-check">Check &amp; export</button>.' : 'Nothing you’ve changed affects them yet.') + '</div>' : "";
    }
    const cv = $("#bCov"); if(cv) cv.innerHTML = coverageHTML();
    const meta = $("#bMeta");
    if(meta){ const t = doc.criteria.reduce((n, c) => n + (+c.max || 0), 0); meta.textContent = (doc.title || "Untitled") + " · " + t + " marks"; }
    doc.strands.forEach((s, i) => {
      const n = doc.criteria.filter(c => c.strand === s.id), m = n.reduce((t, c) => t + (+c.max || 0), 0);
      const el = $("#sMarks" + i); if(el) el.textContent = n.length + " question" + (n.length === 1 ? "" : "s") + " · " + m + " mark" + (m === 1 ? "" : "s");
      for(let b = 1; b <= 4; b++){
        const ev = $("#ev" + i + "_" + b); if(!ev) continue;
        const auto = autoEvidence(doc, s.id, b);
        ev.textContent = auto ? "evidence: " + auto : "no question — greyed out on the rubric, can’t be awarded";
        const bb = $("#bb" + i + "_" + b); if(bb) bb.classList.toggle("bempty", !auto);
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
function insertSnippet(t, si, band){
  /* the box being written in, if it is on this strand; else the band's descriptor */
  const own = lastText && document.contains(lastText) && (si == null || (lastText.closest(".bstrand") || {dataset: {}}).dataset.strand === String(si));
  const el = own ? lastText : (si != null && band ? app.querySelector(`[data-f="strands.${si}.bands.${band - 1}.d"]`) : null);
  /* a skill dropped into an empty descriptor reads as one: "Can … ." */
  if(el && /\.d$/.test(el.dataset.f || "") && !el.value.trim() && /^[a-z]/.test(t)) t = "Can " + t + ".";
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

/* ============================ STATEMENT BANK ============================
   A teacher's own saved statements, for any rubric: kept in this browser
   (rubric-builder:bank) and moved between people and machines as a .json
   file. Each is {text, tag}; tag is free text ("Inquiry", "Year 8 forces"). */
const BANK = "rubric-builder:bank";
let bank = [];
try{ bank = JSON.parse(store.get(BANK) || "[]"); if(!Array.isArray(bank)) bank = []; }catch(e){ bank = []; }
bank = bank.filter(x => x && typeof x.text === "string" && x.text.trim());
const saveBank = () => store.set(BANK, JSON.stringify(bank));
let bankQ = "";
function bankAdd(text, tag){
  text = String(text || "").trim(); tag = String(tag || "").trim();
  if(!text) return false;
  if(bank.some(x => x.text === text)){ toast("Already in the bank"); return false; }
  bank.unshift({text, tag}); saveBank(); return true;
}
function openBank(){
  const p = document.getElementById("bPick");
  const cur = lastText && document.contains(lastText) ? lastText.value.trim() : "";
  const q = bankQ.toLowerCase().split(/\s+/).filter(Boolean);
  const list = bank.map((x, j) => [x, j]).filter(([x]) => q.every(w => (x.text + " " + x.tag).toLowerCase().includes(w)));
  p.innerHTML = `<div class="bpick-in card" role="dialog" aria-modal="true" aria-label="Statement bank">
  <div class="card-head"><div><h2>Statement bank</h2><p>Your own statements, for any rubric. Kept in this browser; export to share or move them.</p></div><button class="btn ghost small" data-bank="close">Close</button></div>
  <div class="card-body">
    <div class="bbank-add">
      <label class="field"><span>New statement</span><textarea id="bkText" rows="2" placeholder="e.g. identify the independent, dependent and controlled variables in an investigation">${esc(cur)}</textarea></label>
      <div class="iobar"><label class="field bare inline"><span>Tag</span><input id="bkTag" placeholder="e.g. Inquiry"></label>
      <button class="btn small" data-bank="add">Add to bank</button></div>
      ${cur ? '<p class="hint">Filled in from the box you were last writing in.</p>' : ""}
    </div>
    <div class="grid3"><label class="field"><span>Search</span><input id="bkQ" value="${esc(bankQ)}" placeholder="word or tag"></label></div>
    <div class="bpick-list" id="bkList">${list.length ? list.map(([x, j]) =>
      `<div class="bpick-row"><span class="t">${esc(x.text)}${x.tag ? ` <span class="ckcode cur">${esc(x.tag)}</span>` : ""}</span>
       <button class="btn small" data-bank="use" data-j="${j}">Insert</button><button class="btn danger small" data-bank="del" data-j="${j}" aria-label="Delete">&#10005;</button></div>`).join("")
      : `<p class="hint">${bank.length ? "Nothing matches." : "The bank is empty. Add statements you reuse — inquiry skills, communication, working mathematically — and insert them into any rubric."}</p>`}</div>
    <div class="iobar"><button class="btn ghost small" data-bank="export" ${bank.length ? "" : "disabled"}>Export bank (.json)</button>
      <button class="btn ghost small" data-bank="import">Import a bank…</button><input type="file" id="bkFile" accept=".json,application/json" hidden></div>
    <p class="hint">Insert puts a statement into the box you were last writing in. Comment boxes read best without a full stop or capital.</p>
  </div></div>`;
  p.hidden = false;
  const qi = document.getElementById("bkQ");
  qi.oninput = () => { bankQ = qi.value; const pos = qi.selectionStart; openBank(); const n = document.getElementById("bkQ"); n.focus(); n.setSelectionRange(pos, pos); };
  document.getElementById("bkFile").onchange = e => {
    const f = e.target.files[0]; e.target.value = ""; if(!f) return;
    const r = new FileReader();
    r.onload = () => {
      try{
        const d = JSON.parse(r.result), items = Array.isArray(d) ? d : d.statements;
        if(!Array.isArray(items)) throw 0;
        let n = 0; items.slice().reverse().forEach(x => { if(x && typeof x.text === "string" && !bank.some(y => y.text === x.text.trim())){ bank.unshift({text: x.text.trim(), tag: String(x.tag || "")}); n++; } });
        saveBank(); openBank(); toast(n + " statement" + (n === 1 ? "" : "s") + " added");
      }catch(err){ toast("That isn’t a statement bank file"); }
    };
    r.readAsText(f);
  };
}
function onBank(e){
  const b = e.target.closest("[data-bank]");
  if(!b) return false;
  const what = b.dataset.bank, j = +b.dataset.j;
  if(what === "close"){ closePicker(); return true; }
  if(what === "add"){ if(bankAdd(document.getElementById("bkText").value, document.getElementById("bkTag").value)){ openBank(); toast("Added to the bank"); } return true; }
  if(what === "del"){ bank.splice(j, 1); saveBank(); openBank(); return true; }
  if(what === "use"){
    const t = bank[j].text;
    if(!(lastText && document.contains(lastText))){ toast("Click in a box on the Strands tab first, then insert"); return true; }
    closePicker(); insertSnippet(t, null, null); toast("Inserted"); return true;
  }
  if(what === "export"){ download("statement-bank.json", JSON.stringify({format: "rubric-statement-bank/1", statements: bank}, null, 2), "application/json"); return true; }
  if(what === "import"){ document.getElementById("bkFile").click(); return true; }
  return true;
}

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
  "q-del"(i){
    const c = doc.criteria[i], cls = c.id && !c._new ? classInUse() : null;
    const k = cls ? cls.students.filter(s => hasMark(s, c.id)).length : 0;
    if(k && !confirm(qTag(c) + " has marks for " + k + " student" + (k === 1 ? "" : "s") + " in " + (cls.cls || "a class") + " saved in this browser. Remove it? The marker will set those marks aside, not delete them.")) return;
    doc.criteria.splice(i, 1); render();
  },
  "goto-check"(){ tab = "check"; render(); window.scrollTo(0, 0); },
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
  "snip"(i, el){ insertSnippet(el.dataset.t, i, el.dataset.b ? +el.dataset.b : null); },
  "std-whole"(){ stdWhole = !stdWhole; render(); },
  "focus"(i, el){
    const s = doc.strands[i], t = el.dataset.t, f = Array.isArray(s.focus) ? s.focus : [];
    s.focus = f.includes(t) ? f.filter(x => x !== t) : [...f, t];
    if(!s.focus.length) delete s.focus;
    render();
  },
  /* a strand per skill of its code: the first keeps this strand, the rest
     are new strands straight after it, each drafted from its own skill */
  "split-strand"(i){
    const s = doc.strands[i], cs = codeSkills(codesOf(s).map(byCode).filter(Boolean));
    if(cs.length < 2) return;
    if(!confirm("Make " + cs.length + " strands from " + s.code + ", one per skill? This strand keeps the first skill; " + (cs.length - 1) + " new strand" + (cs.length === 2 ? "" : "s") + " follow it.")) return;
    s.focus = [cs[0]];
    const added = [];
    const add = cs.slice(1).map(t => { const n = newStrand(doc.strands.concat(added)); n.code = s.code; n.focus = [t]; added.push(n); return n; });
    doc.strands.splice(i + 1, 0, ...add);
    let filled = 0; for(let j = i; j <= i + add.length; j++) filled += fillDefaults(j);
    render(); toast(cs.length + " strands, one skill each" + (filled ? " — " + filled + " empty boxes drafted" : "") + ". Tag each strand’s questions on the Questions tab.");
  },
  "defaults"(i){
    const n = fillDefaults(i); render();
    toast(n ? n + " empty box" + (n === 1 ? "" : "es") + " filled from the curriculum — each needs editing to fit the task." + (fillDefaults.gaps && fillDefaults.gaps.length ? " Left for you: " + fillDefaults.gaps.join(", ") + "." : "") : "Nothing to fill — every box already has text");
  },
  "bank"(){ openBank(); },
  "new"(){ if(!confirm("Start a new, empty rubric? Download this one first if you want to keep it.")) return;
    doc = blank(); baseline = null; store.del(BASELINE); notice = ""; tab = "task"; render(); toast("New rubric"); },
  "open"(){ $("#bFile").click(); },
  "fork"(){
    if(!confirm("Make a copy of this rubric with a new id? Classes saved against the original will not open in the copy.")) return;
    ["storageKey","save","demo","fileStem","back"].forEach(k => delete doc[k]);
    doc.id = ""; doc.title = (doc.title || "") + " (copy)"; baseline = null; store.del(BASELINE);
    notice = "This is now a new rubric, separate from the one it was copied from."; render();
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
  "restore-prev"(){
    const p = store.get(PREVIOUS); if(p){ try{ doc = tidy(JSON.parse(p)); }catch(e){} }
    const pb = store.get(PREVIOUS + "-baseline"); baseline = null; try{ baseline = pb ? JSON.parse(pb) : null; }catch(e){}
    baseline ? store.set(BASELINE, JSON.stringify(baseline)) : store.del(BASELINE);
    store.del(PREVIOUS); store.del(PREVIOUS + "-baseline"); notice = ""; render(); toast("Back to your previous draft"); },
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
  if(onBank(e)) return;
  const b = e.target.closest("[data-pick]"), p = document.getElementById("bPick");
  if(!b){ if(e.target === p) closePicker(); return; }
  const what = b.dataset.pick;
  if(what === "close"){ closePicker(); return; }
  const c = byCode(b.dataset.code);
  if(pickFor === "new"){
    const s = newStrand(doc.strands); s.code = c.code;
    doc.strands.push(s);
    const filled = fillDefaults(doc.strands.length - 1);
    closePicker(); tab = "strands"; render(); scrollToLast(".bstrand");
    const nm = $$('[data-f$=".name"]').pop(); if(nm) nm.focus();
    toast(c.code + " linked, " + filled + " boxes drafted from the curriculum — now make each one fit the task." + (fillDefaults.gaps && fillDefaults.gaps.length ? " Left for you: " + fillDefaults.gaps.join(", ") + "." : ""));
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
  const cur = store.get(DRAFT), curBase = store.get(BASELINE);
  baseline = clone(d); store.set(BASELINE, JSON.stringify(baseline));
  if(cur) curBase ? store.set(PREVIOUS + "-baseline", curBase) : store.del(PREVIOUS + "-baseline");
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
window.rubricBuilder = {splitSkills, defaultsFor: i => defaultsFor(doc.strands[i]),
  get doc(){ return doc; }, set doc(d){ doc = tidy(d); render(); },
  exportRubric, check, parseBooklet, autoEvidence: (sid, b) => autoEvidence(doc, sid, b), render, act: (n, i) => ACT[n](i),
  showTab: t => { tab = t; render(); }, adopt, impact, classInUse, get baseline(){ return baseline; }
};

/* ============================ BOOT ============================ */
shell();
wire();
const incoming = store.get(INCOMING);
store.del(INCOMING);
const draft = store.get(DRAFT);
if(incoming){
  try{ const d = JSON.parse(incoming); doc = tidy(d);
    const curBase = store.get(BASELINE);
    curBase ? store.set(PREVIOUS + "-baseline", curBase) : store.del(PREVIOUS + "-baseline");
    baseline = JSON.parse(incoming); store.set(BASELINE, incoming);
    if(draft && draft !== incoming){ store.set(PREVIOUS, draft);
      notice = "Opened “" + esc(d.title) + "” from the marker. <button class=\"btn ghost small\" data-act=\"restore-prev\">Back to the draft you had before</button>"; }
    else notice = "Opened “" + esc(d.title) + "” from the marker.";
  }catch(e){ doc = null; }
}
if(!doc && draft){
  try{ const b = store.get(BASELINE); baseline = b ? JSON.parse(b) : null; }catch(e){ baseline = null; }
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
