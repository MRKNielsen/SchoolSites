/* ============================================================
   teachtools.js — the teacher's toolbox for slide decks (opt-in).
   Load after deck.js, with teachtools.css:

     <link rel="stylesheet" href="../../../assets/css/teachtools.css">
     <script src="../../../assets/js/teachtools.js" defer></script>

   A tab on the right edge opens the toolbox:
   - Pen / highlighter / eraser: write on the slide itself. Writing is
     stored per slide in this browser (localStorage) until deleted, and
     is anchored to the slide's content so it stays with the question
     when working is revealed underneath it.
   - Whiteboard: a pop-out board with pages; "Save image" downloads a PNG.
   - Timer: a countdown card that can be dragged anywhere.
   - Ruler (the pen draws straight lines along its edge), Measure
     (drag between two points for length and angle), Protractor.
   - Lesson PDF: the slides taught this session, fully revealed, with
     their writing and the whiteboard pages, sent to the print dialog.
   - Delete: this slide's writing, or everything for this deck.
   No dependencies. A stylus draws; once a stylus has been seen, fingers
   are ignored on the writing surface (palm rejection).
   ============================================================ */
(function () {
  "use strict";
  const slides = Array.from(document.querySelectorAll(".deck .slide"));
  if (!slides.length || document.querySelector(".tt-layer")) return;

  /* ---------------- storage ---------------- */
  const KEY = "teachtools:" + location.pathname.replace(/index\.html$/, "");
  let data = { ink: {}, wb: [{ bg: "plain", s: [] }] };
  try {
    const raw = JSON.parse(localStorage.getItem(KEY) || "null");
    if (raw && raw.ink && raw.wb && raw.wb.length) data = raw;
  } catch (e) { /* unreadable: start clean */ }
  let saveT = null;
  function save() {
    clearTimeout(saveT);
    saveT = setTimeout(() => {
      Object.keys(data.ink).forEach(k => { if (!data.ink[k].length) delete data.ink[k]; });   /* reading a slide makes an empty list */
      try { localStorage.setItem(KEY, JSON.stringify(data)); }
      catch (e) { toast("Browser storage is full: writing on this deck is no longer being saved"); }
    }, 400);
  }

  /* ---------------- small helpers ---------------- */
  const el = (tag, cls, html) => { const n = document.createElement(tag); if (cls) n.className = cls; if (html != null) n.innerHTML = html; return n; };
  const SVGNS = "http://www.w3.org/2000/svg";
  const svg = (tag, attrs) => { const n = document.createElementNS(SVGNS, tag); for (const k in attrs) n.setAttribute(k, attrs[k]); return n; };
  const ICON = {
    tools: '<path d="M4 20l4-1 11-11-3-3L5 16l-1 4z"/><path d="M14 6l3 3"/>',
    pen: '<path d="M4 20l4-1 11-11-3-3L5 16l-1 4z"/><path d="M14 6l3 3"/>',
    hi: '<path d="M6 15l8-10 5 4-8 10H7l-1-4z"/><path d="M4 21h8"/>',
    erase: '<path d="M4 15l8-9 8 6-6 8H9l-5-5z"/><path d="M9 20h11"/>',
    timer: '<circle cx="12" cy="13" r="8"/><path d="M12 13V9M9 3h6M12 3v2"/>',
    board: '<rect x="3" y="4" width="18" height="13" rx="1.5"/><path d="M8 21l4-4 4 4"/>',
    ruler: '<rect x="2" y="9" width="20" height="6" rx="1"/><path d="M6 9v3M10 9v2M14 9v3M18 9v2"/>',
    measure: '<path d="M4 20L20 4"/><circle cx="4" cy="20" r="1.6"/><circle cx="20" cy="4" r="1.6"/>',
    pro: '<path d="M2 17a10 10 0 0120 0z"/><path d="M12 17V9M12 17l6-5"/>',
    undo: '<path d="M8 8H4V4"/><path d="M4 8a9 9 0 111 9"/>',
    pdf: '<path d="M6 3h8l4 4v14H6z"/><path d="M14 3v4h4M9 13h6M9 17h6"/>',
    img: '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 16l5-5 4 4 3-3 6 6"/><circle cx="15.5" cy="9.5" r="1.5"/>',
    bin: '<path d="M5 7h14M9 7V4h6v3M7 7l1 13h8l1-13"/>'
  };
  const icon = k => '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' + ICON[k] + "</svg>";

  const layer = el("div", "tt-layer");
  layer.setAttribute("data-noswipe", "");
  document.body.appendChild(layer);
  const toastEl = el("div", "tt-toast"); layer.appendChild(toastEl);
  let toastT = null;
  function toast(msg) { toastEl.textContent = msg; toastEl.classList.add("show"); clearTimeout(toastT); toastT = setTimeout(() => toastEl.classList.remove("show"), 2600); }

  /* Drag anything by pointer; returns nothing, calls move(dx, dy, e) with deltas since the last event. */
  function drag(handle, move, start, end) {
    handle.addEventListener("pointerdown", e => {
      if (e.button > 0) return;
      e.preventDefault(); e.stopPropagation();
      handle.setPointerCapture(e.pointerId);
      let px = e.clientX, py = e.clientY;
      if (start) start(e);
      const mv = ev => { move(ev.clientX - px, ev.clientY - py, ev); px = ev.clientX; py = ev.clientY; };
      const up = ev => { handle.removeEventListener("pointermove", mv); handle.removeEventListener("pointerup", up); handle.removeEventListener("pointercancel", up); if (end) end(ev); };
      handle.addEventListener("pointermove", mv);
      handle.addEventListener("pointerup", up);
      handle.addEventListener("pointercancel", up);
    });
  }
  function download(canvas, name) {
    canvas.toBlob(b => {
      const a = el("a"); a.href = URL.createObjectURL(b); a.download = name;
      document.body.appendChild(a); a.click(); a.remove();
      setTimeout(() => URL.revokeObjectURL(a.href), 4000);
    }, "image/png");
  }
  const deckName = (document.title || "deck").replace(/[^\w]+/g, "-").replace(/^-|-$/g, "").slice(0, 40);

  /* ---------------- pen state ---------------- */
  const COLOURS = [["ink", "Ink"], ["#d93025", "Red"], ["#1a66d6", "Blue"], ["#1e8a3c", "Green"], ["#e07b00", "Orange"], ["#8e24aa", "Purple"]];
  const WIDTHS = [2.5, 4.5, 8];
  const pen = { tool: null, colour: "#d93025", width: 2.5 };   /* tool: null | pen | hi | erase */
  const inkColour = () => (getComputedStyle(document.body).getPropertyValue("--ink") || "#222").trim() || "#222";
  const paint = c => (c === "ink" ? inkColour() : c);
  let penSeen = false;

  /* A stroke: { c, w, a (alpha), sw (surface width when drawn), p: [x, y, pressure, ...] }.
     On a slide, y is measured from the top of the slide's first element (the anchor), so the
     writing follows the content when the slide re-centres after a reveal. */
  function drawStroke(ctx, s, k, ox, oy, inkCol) {
    const p = s.p, n = p.length / 3;
    if (!n) return;
    ctx.strokeStyle = ctx.fillStyle = (s.c === "ink" && inkCol) ? inkCol : paint(s.c);
    ctx.lineCap = ctx.lineJoin = "round";
    ctx.globalAlpha = s.a || 1;
    const X = i => p[i * 3] * k + ox, Y = i => p[i * 3 + 1] * k + oy;
    if (n === 1) { ctx.beginPath(); ctx.arc(X(0), Y(0), s.w * k * 0.6, 0, 6.3); ctx.fill(); ctx.globalAlpha = 1; return; }
    if (s.a) {                                   /* highlighter: one path, so overlaps don't darken */
      ctx.lineWidth = s.w * k; ctx.beginPath(); ctx.moveTo(X(0), Y(0));
      for (let i = 1; i < n; i++) ctx.lineTo(X(i), Y(i));
      ctx.stroke(); ctx.globalAlpha = 1; return;
    }
    for (let i = 1; i < n; i++) {                /* pen: width follows pressure */
      ctx.lineWidth = Math.max(0.6, s.w * k * (0.45 + 1.1 * (p[i * 3 + 2] / 100)));
      ctx.beginPath(); ctx.moveTo(X(i - 1), Y(i - 1)); ctx.lineTo(X(i), Y(i)); ctx.stroke();
    }
    ctx.globalAlpha = 1;
  }
  function hit(s, x, y, k, ox, oy, r) {
    const p = s.p;
    for (let i = 0; i < p.length; i += 3) {
      const dx = p[i] * k + ox - x, dy = p[i + 1] * k + oy - y;
      if (dx * dx + dy * dy < r * r) return true;
    }
    return false;
  }

  /* A writing surface: a canvas plus the list of strokes it shows.
     opts: list() -> strokes array, geom() -> { w, k(stroke), ox, oy } in CSS px, toLocal(e) -> [x, y],
           changed() after any edit, snap(x, y, first) optional straight-edge. */
  function surface(canvas, opts) {
    const ctx = canvas.getContext("2d");
    const undo = [];
    let cur = null, erased = null;
    function redraw() {
      const dpr = window.devicePixelRatio || 1;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      const g = opts.geom();
      opts.list().forEach(s => drawStroke(ctx, s, g.w / s.sw, g.ox, g.oy, opts.ink));
    }
    canvas.addEventListener("pointerdown", e => {
      if (!pen.tool || e.button > 0) return;
      if (e.pointerType === "pen") penSeen = true;
      if (e.pointerType === "touch" && penSeen) return;       /* palm rejection */
      e.preventDefault();
      canvas.setPointerCapture(e.pointerId);
      closeBox();
      const g = opts.geom();
      if (pen.tool === "erase") { erased = []; rub(e, g); return; }
      const hi = pen.tool === "hi";
      cur = { c: pen.colour, w: hi ? pen.width * 5 : pen.width, sw: Math.round(g.w), p: [], id: e.pointerId, lock: null };
      if (hi) cur.a = 0.32;
      add(e, g, true);
    });
    function add(e, g, first) {
      const evs = (!first && e.getCoalescedEvents) ? e.getCoalescedEvents() : [e];
      (evs.length ? evs : [e]).forEach(ev => {
        let [x, y] = opts.toLocal(ev);
        if (opts.snap) { const q = opts.snap(x, y, first, cur); if (q) { x = q[0]; y = q[1]; } }
        const pr = ev.pointerType === "pen" ? Math.round((ev.pressure || 0.5) * 100) : 50;
        cur.p.push(Math.round((x - g.ox) * 10) / 10, Math.round((y - g.oy) * 10) / 10, cur.lock ? 50 : pr);
        first = false;
      });
      const dpr = window.devicePixelRatio || 1;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      if (cur.a) { redraw(); drawStroke(ctx, cur, 1, g.ox, g.oy, opts.ink); }
      else {
        const n = cur.p.length / 3, from = Math.max(0, n - evs.length - 1);
        drawStroke(ctx, { c: cur.c, w: cur.w, p: cur.p.slice(from * 3) }, 1, g.ox, g.oy, opts.ink);
      }
    }
    function rub(e, g) {
      const [x, y] = opts.toLocal(e), list = opts.list();
      for (let i = list.length - 1; i >= 0; i--) {
        if (hit(list[i], x, y, g.w / list[i].sw, g.ox, g.oy, 14)) erased.push({ i: i, s: list.splice(i, 1)[0] });
      }
      redraw();
    }
    canvas.addEventListener("pointermove", e => {
      if (cur && e.pointerId === cur.id) add(e, opts.geom(), false);
      else if (erased && e.buttons) rub(e, opts.geom());
    });
    function finish(e) {
      if (cur && e.pointerId === cur.id) {
        const s = { c: cur.c, w: cur.w, sw: cur.sw, p: cur.p }; if (cur.a) s.a = cur.a;
        opts.list().push(s); undo.push({ add: s }); cur = null; redraw(); opts.changed();
      } else if (erased) {
        if (erased.length) { undo.push({ del: erased }); opts.changed(); }
        erased = null;
      }
    }
    canvas.addEventListener("pointerup", finish);
    canvas.addEventListener("pointercancel", finish);
    return {
      redraw: redraw,
      undo: function () {
        const u = undo.pop(), list = opts.list();
        if (!u) return false;
        if (u.add) { const i = list.indexOf(u.add); if (i >= 0) list.splice(i, 1); }
        else u.del.slice().reverse().forEach(d => list.splice(Math.min(d.i, list.length), 0, d.s));
        redraw(); opts.changed(); return true;
      },
      forget: function () { undo.length = 0; }
    };
  }

  /* ---------------- ink on the active slide ---------------- */
  const ink = el("canvas", "tt-ink"); ink.setAttribute("data-noswipe", "");
  let active = -1;
  const visited = new Set();
  let dwellT = null;
  const strokes = i => (data.ink[i] || (data.ink[i] = []));
  function anchor(slide) {
    for (const c of slide.children) {
      if (c === ink || c.classList.contains("tt-inkimg")) continue;
      if (c.offsetParent !== null) return c.offsetTop;
    }
    return 0;
  }
  function fitInk() {
    const s = slides[active]; if (!s) return;
    ink.style.height = "0px";
    const w = s.clientWidth, h = Math.max(s.scrollHeight, s.clientHeight), dpr = window.devicePixelRatio || 1;
    ink.style.height = h + "px";
    if (ink.width !== Math.round(w * dpr) || ink.height !== Math.round(h * dpr)) { ink.width = Math.round(w * dpr); ink.height = Math.round(h * dpr); }
    inkSurf.redraw();
  }
  const inkSurf = surface(ink, {
    list: () => strokes(active),
    geom: () => { const s = slides[active]; return { w: s.clientWidth, ox: 0, oy: anchor(s) }; },
    toLocal: e => { const s = slides[active], r = s.getBoundingClientRect(); return [e.clientX - r.left, e.clientY - r.top + s.scrollTop]; },
    changed: () => { if (!strokes(active).length) delete data.ink[active]; save(); },
    snap: (x, y, first, cur) => rulerSnap(x, y, first, cur)
  });
  function activate() {
    const i = slides.findIndex(s => s.classList.contains("active"));
    if (i < 0 || document.body.classList.contains("tt-exporting")) return;
    if (i !== active) {
      active = i; inkSurf.forget(); slides[i].appendChild(ink);
      clearTimeout(dwellT); dwellT = setTimeout(() => visited.add(i), 1500);
    }
    requestAnimationFrame(fitInk);
  }
  new MutationObserver(activate).observe(document.querySelector(".deck"), { attributes: true, attributeFilter: ["class"], subtree: true });
  window.addEventListener("resize", () => requestAnimationFrame(fitInk));
  document.addEventListener("click", () => requestAnimationFrame(fitInk));
  document.addEventListener("keyup", () => requestAnimationFrame(fitInk));
  window.addEventListener("load", () => requestAnimationFrame(fitInk));

  /* ---------------- toolbox ---------------- */
  const tab = el("button", "tt-tab", icon("tools") + '<i class="tt-dot"></i>');
  tab.setAttribute("aria-label", "Open the teaching toolbox"); tab.title = "Teaching toolbox";
  const box = el("div", "tt-box");
  layer.append(tab, box);
  let hideT = null;
  function openBox() { layer.classList.add("tt-open"); armHide(); }
  function closeBox() { layer.classList.remove("tt-open"); clearTimeout(hideT); confirmEl.classList.remove("show"); }
  function armHide() { clearTimeout(hideT); hideT = setTimeout(closeBox, 6000); }
  tab.addEventListener("click", () => { tab.blur(); openBox(); });
  box.addEventListener("pointerdown", armHide);
  box.addEventListener("pointermove", armHide);
  document.addEventListener("pointerdown", e => { if (layer.classList.contains("tt-open") && !box.contains(e.target) && e.target !== tab) closeBox(); }, true);

  const btns = {};
  function button(parent, key, label, ic, fn, cls) {
    const b = el("button", "tt-btn" + (cls ? " " + cls : ""), icon(ic) + "<span>" + label + "</span>");
    b.type = "button";
    b.addEventListener("click", e => { e.stopPropagation(); b.blur(); fn(); });
    parent.appendChild(b); btns[key] = b; return b;
  }
  function head(t) { box.appendChild(el("h4", "", t)); }
  function grid() { const g = el("div", "tt-grid"); box.appendChild(g); return g; }

  head("Write on the slide");
  let g = grid();
  button(g, "pen", "Pen", "pen", () => setTool("pen"));
  button(g, "hi", "Highlighter", "hi", () => setTool("hi"));
  button(g, "erase", "Eraser", "erase", () => setTool("erase"));
  button(g, "undo", "Undo", "undo", () => { if (!inkSurf.undo()) toast("Nothing to undo on this slide"); });
  const swRow = el("div", "tt-row"); box.appendChild(swRow);
  const swatches = COLOURS.map(([c, name]) => {
    const b = el("button", "tt-sw"); b.type = "button"; b.title = name; b.setAttribute("aria-label", name + " pen");
    b.dataset.c = c;
    b.addEventListener("click", e => { e.stopPropagation(); b.blur(); pen.colour = c; if (!pen.tool || pen.tool === "erase") setTool("pen", true); syncPen(); });
    swRow.appendChild(b); return b;
  });
  const wdRow = el("div", "tt-row"); box.appendChild(wdRow);
  const widths = WIDTHS.map((w, i) => {
    const b = el("button", "tt-wd", '<i style="height:' + (2 + i * 3) + 'px"></i>'); b.type = "button";
    b.setAttribute("aria-label", ["Fine", "Medium", "Thick"][i] + " line");
    b.addEventListener("click", e => { e.stopPropagation(); b.blur(); pen.width = w; syncPen(); });
    wdRow.appendChild(b); return b;
  });

  head("Tools");
  g = grid();
  button(g, "timer", "Timer", "timer", toggleTimer);
  button(g, "wb", "Whiteboard", "board", toggleWb);
  button(g, "ruler", "Ruler", "ruler", toggleRuler);
  button(g, "measure", "Measure", "measure", toggleMeasure);
  button(g, "pro", "Protractor", "pro", togglePro, "wide");

  head("Save and clear");
  g = grid();
  button(g, "pdf", "Lesson PDF", "pdf", exportLesson);
  button(g, "img", "Save writing", "img", saveInkImage);
  button(g, "bin", "Delete writing", "bin", () => { confirmEl.classList.toggle("show"); armHide(); }, "wide warn");
  const confirmEl = el("div", "tt-confirm", "<b>Delete which writing?</b>");
  box.appendChild(confirmEl);
  [["This slide", () => { delete data.ink[active]; inkSurf.forget(); inkSurf.redraw(); save(); toast("Writing on this slide deleted"); }],
   ["Whole deck and whiteboard", () => { data = { ink: {}, wb: [{ bg: "plain", s: [] }] }; inkSurf.forget(); inkSurf.redraw(); wbPage = 0; if (wb) wbSync(); save(); toast("All writing for this deck deleted"); }],
   ["Cancel", null]].forEach(([label, fn], i) => {
    const b = el("button", i === 2 ? "plain" : "", label); b.type = "button";
    b.addEventListener("click", e => { e.stopPropagation(); confirmEl.classList.remove("show"); if (fn) fn(); });
    confirmEl.appendChild(b);
  });

  function setTool(t, keep) {
    pen.tool = (pen.tool === t && !keep) ? null : t;
    document.body.classList.toggle("tt-drawing", !!pen.tool);
    if (pen.tool && measureOn) toggleMeasure();
    syncPen();
  }
  function syncPen() {
    ["pen", "hi", "erase"].forEach(k => btns[k].classList.toggle("on", pen.tool === k));
    swatches.forEach(b => { b.style.background = paint(b.dataset.c); b.classList.toggle("on", b.dataset.c === pen.colour); });
    widths.forEach((b, i) => b.classList.toggle("on", WIDTHS[i] === pen.width));
    tab.classList.toggle("live", !!pen.tool);
    tab.querySelector(".tt-dot").style.background = pen.tool === "erase" ? "#fff" : paint(pen.colour);
    if (wb) wbSyncTools();
  }
  document.addEventListener("keydown", e => {
    if (e.key === "Escape" && pen.tool && !document.body.classList.contains("tt-exporting")) setTool(pen.tool);
  });

  function saveInkImage() {
    if (!strokes(active).length) { delete data.ink[active]; toast("No writing on this slide to save"); return; }
    const c = el("canvas"); c.width = ink.width; c.height = ink.height;
    const x = c.getContext("2d");
    x.fillStyle = getComputedStyle(document.body).backgroundColor || "#fff"; x.fillRect(0, 0, c.width, c.height);
    x.drawImage(ink, 0, 0);
    download(c, deckName + "-slide" + (active + 1) + "-writing.png");
    toast("Saved this slide's writing as an image. Lesson PDF keeps the slide with it.");
  }

  /* ---------------- timer ---------------- */
  let timer = null;
  function toggleTimer() {
    if (timer) { timer.close(); return; }
    const card = el("div", "tt-card tt-timer");
    card.innerHTML = '<div class="tt-bar"><span class="grow">Timer</span><button class="tt-x" data-a="size" aria-label="Bigger or smaller">⤢</button><button class="tt-x" data-a="close" aria-label="Close timer">✕</button></div>' +
      '<div class="tt-time" aria-live="polite"></div>' +
      '<div class="tt-row"><button class="tt-pill" data-a="-">−1</button><button class="tt-pill go" data-a="go">Start</button><button class="tt-pill" data-a="+">+1</button></div>' +
      '<div class="tt-row">' + [1, 2, 5, 10, 15].map(m => '<button class="tt-pill" data-m="' + m + '">' + m + "</button>").join("") + '<button class="tt-pill" data-a="reset">Reset</button></div>';
    layer.appendChild(card);
    let total = 300, left = 300, tick = null;
    const shown = card.querySelector(".tt-time"), go = card.querySelector('[data-a="go"]');
    const draw = () => { shown.textContent = Math.floor(left / 60) + ":" + String(left % 60).padStart(2, "0"); };
    function beep() {
      try {
        const A = window.AudioContext || window.webkitAudioContext, ctx = new A();
        [0, 0.35, 0.7, 1.05].forEach(t => {
          const o = ctx.createOscillator(), gn = ctx.createGain();
          o.frequency.value = 880; o.connect(gn); gn.connect(ctx.destination);
          gn.gain.setValueAtTime(0.25, ctx.currentTime + t);
          gn.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + t + 0.3);
          o.start(ctx.currentTime + t); o.stop(ctx.currentTime + t + 0.3);
        });
      } catch (e) { /* no audio: the flash is enough */ }
    }
    function stop() { clearInterval(tick); tick = null; go.textContent = left ? "Start" : "Done"; }
    function start() {
      if (!left) return;
      card.classList.remove("up"); go.textContent = "Pause";
      const endAt = Date.now() + left * 1000;                 /* wall clock, so a sleeping tab can't drift */
      tick = setInterval(() => {
        left = Math.max(0, Math.round((endAt - Date.now()) / 1000)); draw();
        if (!left) { stop(); card.classList.add("up"); beep(); }
      }, 250);
    }
    card.addEventListener("click", e => {
      const b = e.target.closest("button"); if (!b) return;
      e.stopPropagation(); b.blur();
      const a = b.dataset.a;
      if (b.dataset.m) { stop(); total = left = +b.dataset.m * 60; card.classList.remove("up"); go.textContent = "Start"; }
      else if (a === "go") { tick ? stop() : start(); }
      else if (a === "reset") { stop(); left = total; card.classList.remove("up"); go.textContent = "Start"; }
      else if (a === "size") card.classList.toggle("big");
      else if (a === "close") timer.close();
      else if (a === "+" || a === "-") {
        const d = a === "+" ? 60 : -60, was = !!tick;
        if (was) stop();
        left = Math.min(99 * 60, Math.max(was ? 1 : 60, left + d)); if (!was) total = left;
        card.classList.remove("up"); if (was) start(); else go.textContent = "Start";
      }
      draw();
    });
    let x = 0, y = 0;
    drag(card.querySelector(".tt-bar"), (dx, dy) => { x += dx; y += dy; card.style.transform = "translate(" + x + "px," + y + "px)"; });
    draw();
    timer = { close: () => { clearInterval(tick); card.remove(); timer = null; btns.timer.classList.remove("on"); } };
    btns.timer.classList.add("on"); closeBox();
  }

  /* ---------------- whiteboard ---------------- */
  let wb = null, wbPage = 0, wbSync = null, wbSyncTools = null;
  const BGS = ["plain", "grid", "dots"];
  function paintBg(ctx, w, h, bg) {
    ctx.fillStyle = "#fff"; ctx.fillRect(0, 0, w, h);
    if (bg === "plain") return;
    const step = w / 32;
    ctx.strokeStyle = "#d5dbe3"; ctx.fillStyle = "#b9c2cd"; ctx.lineWidth = Math.max(1, w / 1400);
    if (bg === "grid") {
      ctx.beginPath();
      for (let x = step; x < w; x += step) { ctx.moveTo(x, 0); ctx.lineTo(x, h); }
      for (let y = step; y < h; y += step) { ctx.moveTo(0, y); ctx.lineTo(w, y); }
      ctx.stroke();
    } else for (let x = step; x < w; x += step) for (let y = step; y < h; y += step) { ctx.beginPath(); ctx.arc(x, y, Math.max(1, w / 900), 0, 6.3); ctx.fill(); }
  }
  function toggleWb() {
    if (wb) { wb.close(); return; }
    const card = el("div", "tt-card tt-wb");
    card.innerHTML = '<div class="tt-bar"><span class="grow">Whiteboard</span><button class="tt-x" data-a="max" aria-label="Full screen board">⤢</button><button class="tt-x" data-a="close" aria-label="Close whiteboard">✕</button></div>' +
      '<div class="tt-tools"></div><div class="tt-surface"><canvas class="bg"></canvas><canvas class="fg" data-noswipe></canvas></div><div class="tt-grip"></div>';
    layer.appendChild(card);
    const tools = card.querySelector(".tt-tools"), bgC = card.querySelector(".bg"), fgC = card.querySelector(".fg"), surf = card.querySelector(".tt-surface");
    const mini = (label, fn, title) => { const b = el("button", "tt-mini", label); b.type = "button"; if (title) { b.title = title; b.setAttribute("aria-label", title); } b.addEventListener("click", e => { e.stopPropagation(); b.blur(); fn(); }); tools.appendChild(b); return b; };
    const sep = () => tools.appendChild(el("span", "sep"));
    const bPen = mini("Pen", () => setTool("pen", true)), bHi = mini("Highlight", () => setTool("hi", true)), bEr = mini("Eraser", () => setTool("erase", true));
    sep();
    const sws = COLOURS.map(([c, name]) => { const b = el("button", "tt-sw"); b.type = "button"; b.title = name; b.dataset.c = c; b.addEventListener("click", e => { e.stopPropagation(); b.blur(); pen.colour = c; if (!pen.tool || pen.tool === "erase") setTool("pen", true); syncPen(); }); tools.appendChild(b); return b; });
    sep();
    mini("Undo", () => s.undo());
    mini("Paper", () => { const p = page(); p.bg = BGS[(BGS.indexOf(p.bg) + 1) % BGS.length]; fit(); save(); }, "Plain, grid or dotted paper");
    sep();
    mini("◀", () => { if (wbPage > 0) { wbPage--; s.forget(); sync(); } }, "Previous page");
    const pageLbl = el("span", "", ""); pageLbl.style.cssText = "font-size:13px;font-weight:700;min-width:3.2em;text-align:center"; tools.appendChild(pageLbl);
    mini("▶", () => { if (wbPage < data.wb.length - 1) { wbPage++; s.forget(); sync(); } }, "Next page");
    mini("+ Page", () => { data.wb.splice(wbPage + 1, 0, { bg: page().bg, s: [] }); wbPage++; s.forget(); sync(); save(); });
    sep();
    mini("Clear", () => { page().s.length = 0; s.forget(); s.redraw(); save(); }, "Clear this page");
    mini("Save image", () => {
      const W = 2000, H = Math.round(W * fgC.clientHeight / fgC.clientWidth), c = el("canvas"); c.width = W; c.height = H;
      const x = c.getContext("2d"); paintBg(x, W, H, page().bg);
      page().s.forEach(st => drawStroke(x, st, W / st.sw, 0, 0, "#1d1d1f"));
      download(c, deckName + "-whiteboard-" + (wbPage + 1) + ".png"); toast("Whiteboard page saved as an image");
    });
    const page = () => data.wb[wbPage] || (wbPage = 0, data.wb[0]);
    const s = surface(fgC, {
      list: () => page().s,
      geom: () => ({ w: fgC.clientWidth, ox: 0, oy: 0 }),
      toLocal: e => { const r = fgC.getBoundingClientRect(); return [e.clientX - r.left, e.clientY - r.top]; },
      changed: save, ink: "#1d1d1f"
    });
    function fit() {
      const dpr = window.devicePixelRatio || 1, w = surf.clientWidth, h = surf.clientHeight;
      [bgC, fgC].forEach(c => { c.width = Math.round(w * dpr); c.height = Math.round(h * dpr); });
      const x = bgC.getContext("2d"); x.setTransform(dpr, 0, 0, dpr, 0, 0); paintBg(x, w, h, page().bg);
      s.redraw();
    }
    function sync() { pageLbl.textContent = (wbPage + 1) + " / " + data.wb.length; fit(); }
    function syncTools() {
      bPen.classList.toggle("on", pen.tool === "pen"); bHi.classList.toggle("on", pen.tool === "hi"); bEr.classList.toggle("on", pen.tool === "erase");
      sws.forEach(b => { b.style.background = b.dataset.c === "ink" ? "#1d1d1f" : b.dataset.c; b.classList.toggle("on", b.dataset.c === pen.colour); });
    }
    card.querySelector(".tt-bar").addEventListener("click", e => {
      const b = e.target.closest("button"); if (!b) return; e.stopPropagation(); b.blur();
      if (b.dataset.a === "close") wb.close(); else { card.classList.toggle("max"); requestAnimationFrame(fit); }
    });
    let x = 0, y = 0;
    drag(card.querySelector(".tt-bar"), (dx, dy) => { if (card.classList.contains("max")) return; x += dx; y += dy; card.style.transform = "translate(" + x + "px," + y + "px)"; });
    drag(card.querySelector(".tt-grip"), (dx, dy) => { card.style.width = Math.max(320, card.offsetWidth + dx) + "px"; card.style.height = Math.max(240, card.offsetHeight + dy) + "px"; fit(); });
    const onResize = () => requestAnimationFrame(fit);
    window.addEventListener("resize", onResize);
    wbSync = sync; wbSyncTools = syncTools;
    wb = { close: () => { window.removeEventListener("resize", onResize); card.remove(); wb = null; btns.wb.classList.remove("on"); } };
    btns.wb.classList.add("on"); closeBox();
    if (!pen.tool) setTool("pen", true);
    sync(); syncTools();
  }

  /* ---------------- ruler ---------------- */
  const UNIT = 50;                       /* px per numbered ruler unit; Measure reports in the same units */
  let ruler = null;
  function toggleRuler() {
    if (ruler) { ruler.node.remove(); ruler = null; btns.ruler.classList.remove("on"); return; }
    const L = Math.min(700, Math.round(window.innerWidth * 0.55 / UNIT) * UNIT), H = 62;
    const node = el("div", "tt-ruler");
    const s = svg("svg", { width: L, height: H, viewBox: "0 0 " + L + " " + H });
    s.appendChild(svg("rect", { class: "body", x: 0, y: 0, width: L, height: H, rx: 4 }));
    for (let i = 0; i <= L / 10; i++) {
      const big = i % 5 === 0, x = i * 10;
      s.appendChild(svg("line", { class: "tick", x1: x, y1: 0, x2: x, y2: big ? 14 : 8 }));
      s.appendChild(svg("line", { class: "tick", x1: x, y1: H, x2: x, y2: H - (big ? 14 : 8) }));
      if (big && i && x < L) { const t = svg("text", { x: x, y: 27 }); t.textContent = i / 5; s.appendChild(t); }
    }
    const read = svg("text", { class: "tt-read", x: L / 2, y: 46 }); s.appendChild(read);
    const hA = svg("circle", { class: "tt-handle", cx: L - 16, cy: H / 2 + 6, r: 11 }), hB = svg("circle", { class: "tt-handle", cx: 16, cy: H / 2 + 6, r: 11 });
    const tA = svg("text", { x: L - 16, y: H / 2 + 11, style: "pointer-events:none;font-size:13px" }); tA.textContent = "↻";
    const tB = svg("text", { x: 16, y: H / 2 + 11, style: "pointer-events:none;font-size:13px" }); tB.textContent = "↻";
    s.append(hA, hB, tA, tB);
    node.appendChild(s); layer.appendChild(node);
    const st = { cx: window.innerWidth / 2, cy: window.innerHeight / 2, ang: 0, L: L, H: H };
    function place() {
      node.style.transform = "translate(" + st.cx + "px," + st.cy + "px) rotate(" + st.ang + "deg) translate(" + (-L / 2) + "px," + (-H / 2) + "px)";
      let shown = ((-st.ang % 180) + 180) % 180; shown = Math.round(shown * 10) / 10;
      read.textContent = shown + "°";
    }
    drag(node, (dx, dy) => { st.cx += dx; st.cy += dy; place(); });
    [hA, hB].forEach(h => drag(h, (dx, dy, e) => {
      let a = Math.atan2(e.clientY - st.cy, e.clientX - st.cx) * 180 / Math.PI; if (h === hB) a += 180;
      const snap = Math.round(a / 15) * 15; st.ang = Math.abs(a - snap) < 2 ? snap : Math.round(a * 2) / 2; place();
    }));
    place();
    ruler = { node: node, st: st }; btns.ruler.classList.add("on"); closeBox();
    if (!pen.tool) toast("Pick the pen, then draw along either long edge of the ruler");
  }
  /* If a stroke starts close to a long edge of the ruler, keep it on that edge. Slide coordinates in and out. */
  function rulerSnap(x, y, first, cur) {
    if (!ruler) return null;
    const s = slides[active], r = s.getBoundingClientRect();
    const vx = x + r.left, vy = y + r.top - s.scrollTop, st = ruler.st, a = st.ang * Math.PI / 180;
    const ux = Math.cos(a), uy = Math.sin(a), nx = -uy, ny = ux;
    const d = (vx - st.cx) * nx + (vy - st.cy) * ny;                 /* signed distance from the ruler's centre line */
    if (first) {
      const along = (vx - st.cx) * ux + (vy - st.cy) * uy, side = d < 0 ? -1 : 1;
      cur.lock = (Math.abs(Math.abs(d) - st.H / 2) < 26 && Math.abs(along) < st.L / 2 + 40) ? side : null;
    }
    if (!cur.lock) return null;
    const off = cur.lock * (st.H / 2 + cur.w / 2 + 0.5) - d;
    return [x + nx * off, y + ny * off];
  }

  /* ---------------- protractor ---------------- */
  let pro = null;
  function togglePro() {
    if (pro) { pro.remove(); pro = null; btns.pro.classList.remove("on"); return; }
    const R = Math.min(260, Math.round(window.innerHeight * 0.3)), pad = 26;
    const node = el("div", "tt-pro");
    const s = svg("svg", { width: 2 * R + 2 * pad, height: R + 2 * pad, viewBox: (-R - pad) + " " + (-R - pad) + " " + (2 * R + 2 * pad) + " " + (R + 2 * pad) });
    s.appendChild(svg("path", { class: "body", d: "M" + (-R) + " 0A" + R + " " + R + " 0 0 1 " + R + " 0L" + R + " " + (pad - 6) + "L" + (-R) + " " + (pad - 6) + "Z" }));
    for (let d = 0; d <= 180; d++) {
      const a = d * Math.PI / 180, len = d % 10 === 0 ? 16 : d % 5 === 0 ? 11 : 6, c = Math.cos(a), sn = Math.sin(a);
      s.appendChild(svg("line", { class: "tick", x1: R * c, y1: -R * sn, x2: (R - len) * c, y2: -(R - len) * sn }));
      if (d % 10 === 0) { const t = svg("text", { x: (R - 28) * c, y: -(R - 28) * sn + 4 }); t.textContent = d; s.appendChild(t); }
    }
    s.appendChild(svg("line", { class: "tick", x1: -R, y1: 0, x2: R, y2: 0 }));
    s.appendChild(svg("line", { class: "tick", x1: 0, y1: -10, x2: 0, y2: 6 }));
    const arm = svg("line", { class: "arm", x1: 0, y1: 0 }), knob = svg("circle", { class: "armknob", r: 11 });
    const read = svg("text", { class: "tt-read", x: 0, y: -R * 0.42 });
    const rot = svg("circle", { class: "tt-handle", cx: R - 14, cy: pad / 2 - 2, r: 11 }), rotT = svg("text", { x: R - 14, y: pad / 2 + 3, style: "pointer-events:none;font-size:13px" }); rotT.textContent = "↻";
    const cls = svg("circle", { class: "tt-handle", cx: -R + 14, cy: pad / 2 - 2, r: 11 }), clsT = svg("text", { x: -R + 14, y: pad / 2 + 3, style: "pointer-events:none;font-size:13px" }); clsT.textContent = "✕";
    s.append(arm, knob, read, rot, rotT, cls, clsT);
    node.appendChild(s); layer.appendChild(node);
    const st = { cx: window.innerWidth / 2, cy: window.innerHeight * 0.6, ang: 0, arm: 60 };
    function place() {
      node.style.transform = "translate(" + st.cx + "px," + st.cy + "px) rotate(" + st.ang + "deg) translate(" + (-R - pad) + "px," + (-R - pad) + "px)";
      const a = st.arm * Math.PI / 180, x = (R + 12) * Math.cos(a), y = -(R + 12) * Math.sin(a);
      arm.setAttribute("x2", x); arm.setAttribute("y2", y); knob.setAttribute("cx", x); knob.setAttribute("cy", y);
      read.textContent = (Math.round(st.arm * 2) / 2) + "°";
    }
    drag(node, (dx, dy) => { st.cx += dx; st.cy += dy; place(); });
    drag(rot, (dx, dy, e) => { const a = Math.atan2(e.clientY - st.cy, e.clientX - st.cx) * 180 / Math.PI, sn = Math.round(a / 15) * 15; st.ang = Math.abs(a - sn) < 2 ? sn : Math.round(a); place(); });
    drag(knob, (dx, dy, e) => {
      let a = -Math.atan2(e.clientY - st.cy, e.clientX - st.cx) * 180 / Math.PI + st.ang;
      a = ((a % 360) + 360) % 360; if (a > 270) a = 0; else if (a > 180) a = 180;
      const sn = Math.round(a / 5) * 5; st.arm = Math.abs(a - sn) < 0.8 ? sn : Math.round(a * 2) / 2; place();
    });
    cls.addEventListener("pointerdown", e => { e.stopPropagation(); togglePro(); });
    place();
    pro = node; btns.pro.classList.add("on"); closeBox();
  }

  /* ---------------- measure ---------------- */
  let measureOn = false, measureEl = null;
  function toggleMeasure() {
    measureOn = !measureOn; btns.measure.classList.toggle("on", measureOn);
    if (!measureOn) { if (measureEl) measureEl.remove(); measureEl = null; return; }
    if (pen.tool) setTool(pen.tool);
    measureEl = el("div", "tt-measure");
    const s = svg("svg", {}); measureEl.appendChild(s);
    layer.insertBefore(measureEl, layer.firstChild);
    let cur = null;
    measureEl.addEventListener("pointerdown", e => {
      if (e.button > 0) return; e.preventDefault(); measureEl.setPointerCapture(e.pointerId);
      if (s.childNodes.length > 15) { for (let i = 0; i < 5; i++) s.removeChild(s.firstChild); }
      const gq = svg("g", {}), ln = svg("line", {}), c1 = svg("circle", { r: 4 }), c2 = svg("circle", { r: 4 }), bx = svg("rect", { height: 24 }), tx = svg("text", {});
      gq.append(ln, c1, c2, bx, tx); s.appendChild(gq);
      cur = { x: e.clientX, y: e.clientY, ln: ln, c1: c1, c2: c2, bx: bx, tx: tx }; upd(e);
    });
    function upd(e) {
      const dx = e.clientX - cur.x, dy = e.clientY - cur.y, len = Math.hypot(dx, dy);
      let ang = Math.atan2(-dy, dx) * 180 / Math.PI; if (ang < 0) ang += 180; if (ang >= 179.95) ang = 0;
      cur.ln.setAttribute("x1", cur.x); cur.ln.setAttribute("y1", cur.y); cur.ln.setAttribute("x2", e.clientX); cur.ln.setAttribute("y2", e.clientY);
      cur.c1.setAttribute("cx", cur.x); cur.c1.setAttribute("cy", cur.y); cur.c2.setAttribute("cx", e.clientX); cur.c2.setAttribute("cy", e.clientY);
      const label = (len / UNIT).toFixed(2) + " units   " + ang.toFixed(1) + "°", w = label.length * 7.6 + 14;
      const mx = (cur.x + e.clientX) / 2, my = (cur.y + e.clientY) / 2 - 22;
      cur.bx.setAttribute("x", mx - w / 2); cur.bx.setAttribute("y", my - 16); cur.bx.setAttribute("width", w);
      cur.tx.setAttribute("x", mx); cur.tx.setAttribute("y", my + 1); cur.tx.textContent = label;
    }
    measureEl.addEventListener("pointermove", e => { if (cur) upd(e); });
    const end = () => { cur = null; };
    measureEl.addEventListener("pointerup", end); measureEl.addEventListener("pointercancel", end);
    closeBox(); toast("Drag between two points. Lengths use the ruler's units.");
  }

  /* ---------------- lesson PDF ---------------- */
  let exportBar = null, pageStyle = null;
  function exportLesson() {
    closeBox();
    const body = document.body, W = window.innerWidth, H = window.innerHeight;
    visited.add(active);
    Object.keys(data.ink).forEach(k => { if (data.ink[k].length) visited.add(+k); });
    let all = false;
    exportBar = el("div", "tt-exportbar");
    const info = el("span"), bAll = el("button", "", ""), bPrint = el("button", "pri", "Save as PDF"), bClose = el("button", "", "Back to the deck");
    exportBar.append(info, bAll, bPrint, bClose); body.appendChild(exportBar);
    const wbPages = [];
    data.wb.forEach((p, i) => {
      if (!p.s.length) return;
      let maxY = 0;
      p.s.forEach(st => { for (let j = 1; j < st.p.length; j += 3) maxY = Math.max(maxY, st.p[j] * 2000 / st.sw); });
      const c = el("canvas"); c.width = 2000; c.height = Math.max(1250, Math.ceil(maxY + 60));
      const x = c.getContext("2d"); paintBg(x, c.width, c.height, p.bg);
      p.s.forEach(st => drawStroke(x, st, 2000 / st.sw, 0, 0, "#1d1d1f"));
      const sec = el("section", "tt-wbpage", "<h3>Whiteboard page " + (i + 1) + "</h3>"), im = el("img"); im.src = c.toDataURL("image/png"); im.alt = "Whiteboard page " + (i + 1);
      sec.appendChild(im); document.querySelector(".deck").appendChild(sec); wbPages.push(sec);
    });
    body.classList.add("tt-exporting"); document.documentElement.classList.add("tt-exporting");
    pageStyle = el("style"); pageStyle.textContent = "@page { size: " + W + "px " + H + "px; margin: 0; }"; document.head.appendChild(pageStyle);
    function layout() {
      slides.forEach((s, i) => {
        s.classList.toggle("tt-skip", !all && !visited.has(i));
        const old = s.querySelector(":scope > img.tt-inkimg"); if (old) old.remove();
      });
      const n = slides.filter(s => !s.classList.contains("tt-skip")).length;
      info.textContent = "Lesson PDF: " + n + " slide" + (n === 1 ? "" : "s") + (wbPages.length ? " + " + wbPages.length + " whiteboard page" + (wbPages.length === 1 ? "" : "s") : "") + ", with your writing";
      bAll.textContent = all ? "Only slides taught" : "Include every slide";
      requestAnimationFrame(() => requestAnimationFrame(() => {
        slides.forEach((s, i) => {
          const list = data.ink[i];
          if (s.classList.contains("tt-skip") || !list || !list.length) return;
          const w = s.offsetWidth, h = s.offsetHeight, c = el("canvas"), k = 2;
          c.width = w * k; c.height = h * k;
          const x = c.getContext("2d"); x.setTransform(k, 0, 0, k, 0, 0);
          const oy = anchor(s);
          list.forEach(st => drawStroke(x, st, w / st.sw, 0, oy));
          const im = el("img", "tt-inkimg"); im.alt = ""; im.src = c.toDataURL("image/png"); s.appendChild(im);
        });
        window.scrollTo(0, 0);
      }));
    }
    const block = e => { if (!e.target.closest(".tt-exportbar")) { e.stopPropagation(); if (e.type === "keydown" && e.key === "Escape") leave(); } };
    ["keydown", "keyup", "touchstart", "touchend"].forEach(t => window.addEventListener(t, block, true));
    function leave() {
      ["keydown", "keyup", "touchstart", "touchend"].forEach(t => window.removeEventListener(t, block, true));
      body.classList.remove("tt-exporting"); document.documentElement.classList.remove("tt-exporting");
      slides.forEach(s => { s.classList.remove("tt-skip"); const im = s.querySelector(":scope > img.tt-inkimg"); if (im) im.remove(); });
      wbPages.forEach(p => p.remove()); exportBar.remove(); pageStyle.remove(); exportBar = null;
      window.scrollTo(0, 0); requestAnimationFrame(fitInk);
    }
    bAll.addEventListener("click", () => { all = !all; layout(); });
    bPrint.addEventListener("click", () => window.print());
    bClose.addEventListener("click", leave);
    layout();
    toast("Check the pages, then choose Save as PDF and pick 'Save as PDF' as the printer");
  }

  syncPen();
  activate();
})();
