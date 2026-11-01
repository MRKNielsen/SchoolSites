/* =========================================================================
   rubric-open.js — the "open a rubric" screen for tools/rubric-marker.html.

   Decides which rubric the marker runs, then loads the engine
   (assets/js/rubric.js) with window.RUBRIC set. The engine never changes
   rubric while running — its constants are built once from window.RUBRIC —
   so switching rubric goes through a page reload with the choice parked in
   sessionStorage.

   Accepts, by file picker or drag and drop:
     • a rubric file (.json, or a unit's rubric-data.js — the
       `window.RUBRIC = …;` wrapper is stripped, never executed)
     • a class saved from any marker page: saves carry their rubric, so the
       class opens with the rubric it was marked against
   Remembers the last rubric opened, and lists classes autosaved in this
   browser under the generic "rubric-marker:" keys.

   Usage: <div id="rubric-app"></div>
          <script src="../assets/js/rubric-open.js"
                  data-engine="../assets/js/rubric.js"></script>
   ========================================================================= */
(function(){
  "use strict";
  const FORMAT = "rubric-marker/1";
  const LAST = "rubric-marker:last";
  const PENDING = "rubric-marker:pending";
  const me = document.currentScript;
  const ENGINE = (me && me.getAttribute("data-engine")) || "../assets/js/rubric.js";
  const STARTER = me && me.getAttribute("data-starter");
  const BUILDER = me && me.getAttribute("data-builder");
  const EXAMPLES = (me && me.getAttribute("data-examples") || "").split(";").map(s => s.trim()).filter(Boolean)
    .map(s => { const i = s.indexOf("|"); return {label: s.slice(0, i), src: s.slice(i + 1)}; });
  const app = document.getElementById("rubric-app");
  const esc = t => String(t == null ? "" : t).replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));

  const store = {
    get(area, k){ try{ return window[area].getItem(k); }catch(e){ return null; } },
    set(area, k, v){ try{ window[area].setItem(k, v); return true; }catch(e){ return false; } },
    del(area, k){ try{ window[area].removeItem(k); }catch(e){} }
  };

  /* Text -> {rubric, save} or throws with a message a teacher can act on. */
  function parse(text){
    let t = String(text).replace(/^﻿/, "").trim();
    /* a unit's rubric-data.js: comment header, then window.RUBRIC = {...}; */
    const m = t.match(/window\.RUBRIC\s*=\s*([\s\S]*?);?\s*$/);
    if(m && !/^[\[{]/.test(t)) t = m[1];
    let d;
    try{ d = JSON.parse(t); }
    catch(e){ throw new Error("That file isn’t valid JSON, so it can’t be a rubric or a saved class."); }
    if(d && d.format === FORMAT) return {rubric: d, save: null};
    if(d && d.rubric && d.rubric.format === FORMAT) return {rubric: d.rubric, save: text};
    if(d && Array.isArray(d.students))
      throw new Error("That saved class has no rubric inside it — it was saved before saves carried one. Open it from the page it was marked on, then Save file again.");
    throw new Error("That file isn’t a rubric or a class saved from the marker.");
  }

  function start(rubric, saveText){
    window.RUBRIC = rubric;
    if(saveText) window.RUBRIC_OPEN_SAVE = saveText;
    store.set("localStorage", LAST, JSON.stringify(rubric));
    /* the engine can hand back a file from another rubric: park it and reload */
    window.rubricSwitch = (r, save) => {
      const parked = JSON.stringify({rubric: r, save: save || null});
      if(!store.set("sessionStorage", PENDING, parked)) store.set("localStorage", PENDING, parked);
      store.set("localStorage", LAST, JSON.stringify(r));
      location.reload();
    };
    const s = document.createElement("script");
    s.src = ENGINE;
    s.onerror = () => { app.innerHTML = '<div class="rb-open"><p class="err">The marking engine didn’t load (' + esc(ENGINE) + ').</p></div>'; };
    document.body.appendChild(s);
  }

  function another(){
    store.del("localStorage", LAST);
    location.reload();
  }
  document.addEventListener("rubric:ready", () => {
    const side = document.querySelector(".masthead-side");
    if(!side) return;
    const b = document.createElement("button");
    b.type = "button"; b.className = "unit-back"; b.textContent = "Open another rubric";
    b.onclick = another;
    side.insertBefore(b, side.firstChild);
    /* hand the rubric to the builder, which picks it up from INCOMING */
    if(BUILDER && window.RUBRIC){
      const e = document.createElement("button");
      e.type = "button"; e.className = "unit-back"; e.textContent = "Edit in builder";
      e.onclick = () => { store.set("localStorage", "rubric-builder:incoming", JSON.stringify(window.RUBRIC)); location.href = BUILDER; };
      side.insertBefore(e, b.nextSibling);
    }
  });
  document.addEventListener("rubric:problems", () => {
    const panel = document.querySelector(".rb-problems .card-body");
    if(!panel) return;
    const b = document.createElement("button");
    b.type = "button"; b.className = "btn"; b.textContent = "Choose a different file";
    b.onclick = another;
    panel.appendChild(b);
  });

  /* classes autosaved in this browser by the generic marker */
  function recent(){
    const out = [];
    try{
      for(let i = 0; i < localStorage.length; i++){
        const k = localStorage.key(i);
        if(!k || k.indexOf("rubric-marker:") !== 0 || k === LAST || k === PENDING) continue;
        try{
          const d = JSON.parse(localStorage.getItem(k));
          if(d && d.rubric && d.rubric.format === FORMAT)
            out.push({key: k, title: d.rubric.title, cls: d.meta && d.meta.cls, n: (d.students || []).length});
        }catch(e){}
      }
    }catch(e){}
    return out;
  }

  function loadExample(src){
    const s = document.createElement("script");
    s.src = src;
    s.onload = () => { const r = window.RUBRIC; if(r) start(r, null); else showError("That example didn’t set a rubric."); };
    s.onerror = () => showError("Couldn’t load " + src + ".");
    document.head.appendChild(s);
  }

  function showError(msg){
    const el = document.getElementById("rbErr");
    if(el) el.textContent = msg;
  }

  function readFile(f){
    const r = new FileReader();
    r.onload = () => {
      try{ const got = parse(r.result); start(got.rubric, got.save); }
      catch(e){ showError(e.message); }
    };
    r.onerror = () => showError("Couldn’t read that file.");
    r.readAsText(f);
  }

  function picker(){
    const rec = recent();
    app.innerHTML = `
<header class="masthead">
  <div class="masthead-inner">
    <div>
      <div class="eyebrow">Staff tool</div>
      <h1>Rubric marker <em>— mark any assessment against its rubric</em></h1>
    </div>
  </div>
</header>
<div class="rb-open">
  <div class="note">Open a <strong>rubric file</strong> to start marking a class, or a <strong>class you saved</strong> from any marker to carry on — saved classes carry their rubric with them. Nothing is uploaded: files are read in this browser, and marks autosave here only.</div>
  <div class="card">
    <div class="card-head"><div><h2>Open a file</h2><p>A rubric (<code>.json</code>, or a unit’s <code>rubric-data.js</code>) or a saved class (<code>.json</code>).</p></div></div>
    <div class="card-body">
      <div class="rb-drop" id="rbDrop">
        <button class="btn" id="rbPick" type="button">Choose a file…</button>
        <p>or drop it here</p>
        <input type="file" id="rbFile" accept=".json,.js,application/json" hidden>
      </div>
      <div class="err" id="rbErr" role="alert"></div>
    </div>
  </div>
  ${rec.length ? `<div class="card">
    <div class="card-head"><div><h2>Carry on marking</h2><p>Classes autosaved in this browser.</p></div></div>
    <div class="card-body"><ul class="rb-recent">${rec.map((r, i) =>
      `<li><span><span class="t">${esc(r.title)}</span> <span class="m">${esc(r.cls || "no class name")} · ${r.n} student${r.n === 1 ? "" : "s"}</span></span>`
      + `<button class="btn ghost small" type="button" data-recent="${i}">Open</button></li>`).join("")}</ul></div>
  </div>` : ""}
  ${EXAMPLES.length ? `<div class="card">
    <div class="card-head"><div><h2>Rubrics on this site</h2><p>Open one to see how a finished rubric marks, or download it from the Class tab as a starting point for your own.</p></div></div>
    <div class="card-body"><ul class="rb-recent">${EXAMPLES.map((x, i) =>
      `<li><span class="t">${esc(x.label)}</span><button class="btn ghost small" type="button" data-example="${i}">Open</button></li>`).join("")}</ul></div>
  </div>` : ""}
  ${STARTER ? `<div class="card">
    <div class="card-head"><div><h2>Make your own</h2><p>The rubric builder walks through it: the task, the strands with a descriptor and comment wording for each band — starting from Victorian Curriculum content descriptions if you like — and every question with its marks, strand and band. It checks the rubric as you go and opens it here when it’s ready.</p></div>
    <span class="iobar flush">${BUILDER ? `<a class="btn small" href="${esc(BUILDER)}">Open the rubric builder</a>` : ""}<a class="btn ghost small" href="${esc(STARTER)}" download>Download the starter rubric</a></span></div>
  </div>` : ""}
</div>`;
    const input = document.getElementById("rbFile");
    document.getElementById("rbPick").onclick = () => input.click();
    input.onchange = e => { const f = e.target.files[0]; if(f) readFile(f); e.target.value = ""; };
    const drop = document.getElementById("rbDrop");
    drop.addEventListener("dragover", e => { e.preventDefault(); drop.classList.add("over"); });
    drop.addEventListener("dragleave", () => drop.classList.remove("over"));
    drop.addEventListener("drop", e => {
      e.preventDefault(); drop.classList.remove("over");
      const f = e.dataTransfer && e.dataTransfer.files[0]; if(f) readFile(f);
    });
    app.querySelectorAll("[data-recent]").forEach(b => b.onclick = () => {
      const r = rec[+b.dataset.recent];
      try{ const d = JSON.parse(localStorage.getItem(r.key)); start(d.rubric, null); }   /* the engine restores the autosave itself */
      catch(e){ showError("That autosave couldn’t be read."); }
    });
    app.querySelectorAll("[data-example]").forEach(b => b.onclick = () => loadExample(EXAMPLES[+b.dataset.example].src));
  }

  /* 1. a switch parked by the engine before a reload */
  const parked = store.get("sessionStorage", PENDING) || store.get("localStorage", PENDING);
  store.del("sessionStorage", PENDING); store.del("localStorage", PENDING);
  if(parked){
    try{ const p = JSON.parse(parked); if(p && p.rubric){ start(p.rubric, p.save); return; } }catch(e){}
  }
  /* 2. the rubric open last time */
  const last = store.get("localStorage", LAST);
  if(last){
    try{ const r = JSON.parse(last); if(r && r.format === FORMAT){ start(r, null); return; } }catch(e){}
  }
  /* 3. choose one */
  picker();
})();
