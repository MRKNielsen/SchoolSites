/* ============================================================
   deck.js — shared slide-deck navigation & interactions
   Load with:  <script src="../../assets/js/deck.js" defer></script>

   Provides:
   - Arrow-key / button / swipe navigation between .slide elements
   - Progress bar (.progress) and counter (.counter) updates
   - #hash deep-linking to slide numbers
   - .reveal-btn → shows .steps li in sequence (data-target="#id")
   - .qcard answer toggles (button.reveal-btn inside .qcard, or data-answer)
   - .ptab / .partpanel part-by-part worked examples
   - Forward nav (→ / space / next) reveals the next hidden step,
     fragment or answer on the slide before advancing
   - "R" key does the same reveal without any chance of advancing
   ============================================================ */
(function () {
  "use strict";

  const slides = Array.from(document.querySelectorAll(".slide"));
  if (!slides.length) return;
  const progress = document.querySelector(".progress");
  const counter = document.querySelector(".counter");
  let cur = Math.max(0, slides.findIndex(s => s.classList.contains("active")));

  /* Layout state for the active slide:
     - .overflowing → content taller than viewport: 15% top buffer applies
       (measured against the base 5vh padding so the buffer itself
       doesn't flip the result back and forth)
     - body.has-more → bottom fade zone while unscrolled content remains */
  function updateFade() {
    const s = slides[cur];
    const extra = s.classList.contains("overflowing") ? window.innerHeight * 0.10 : 0;
    s.classList.toggle("overflowing", s.scrollHeight - extra > s.clientHeight + 1);
    const more = s.scrollHeight - s.scrollTop - s.clientHeight > 8;
    document.body.classList.toggle("has-more", more);
  }
  slides.forEach(s => s.addEventListener("scroll", updateFade, { passive: true }));
  window.addEventListener("resize", updateFade);
  window.addEventListener("load", updateFade); /* re-check once fonts/images are in */
  /* reveals/tabs change slide height — re-check after any click */
  document.addEventListener("click", () => requestAnimationFrame(updateFade));

  function go(i) {
    if (i < 0 || i >= slides.length) return;
    slides[cur].classList.remove("active");
    cur = i;
    slides[cur].classList.add("active");
    if (progress) progress.style.width = ((cur + 1) / slides.length * 100) + "%";
    if (counter) counter.textContent = (cur + 1) + " / " + slides.length;
    history.replaceState(null, "", "#" + (cur + 1));
    updateTag();
    updateFade();
    markMenu();
  }

  /* ---- Reveals ------------------------------------------------------
     Everything still hidden on a slide - .steps items, .frag fragments
     and .qcard answers - is revealed one piece at a time, in document
     order, by the right arrow / space / "next" button, before the deck
     moves on. Buttons and keys share one source of truth (the DOM), so
     a step revealed by the arrow still leaves its button on the right
     label. Backward nav un-reveals fragments only: steps and answers
     stay up, so backing out of a worked example is a single press. */

  const HIDDEN = ".steps > li:not(.shown), .frag:not(.on), [data-answer-for]:not(.shown)";
  const stepBtns = new Map();   /* <ul|ol class="steps">  -> { btn, label } */
  const ansBtns = new Map();    /* answer element         -> { btn, label } */

  function syncFragBtns(s) {
    const left = s.querySelector(".frag:not(.on)");
    s.querySelectorAll(".reveal-btn[data-frag]").forEach(b => b.classList.toggle("done", !left));
  }
  function syncStepBtn(list) {
    const rec = list && stepBtns.get(list);
    if (!rec) return;
    const done = list.querySelector(":scope > li") && !list.querySelector(":scope > li:not(.shown)");
    rec.btn.textContent = done ? "Reset \u21ba" : rec.label;
  }
  function syncAnsBtn(a) {
    const rec = ansBtns.get(a);
    if (rec) rec.btn.textContent = a.classList.contains("shown") ? "Hide \u2715" : rec.label;
  }

  /* A reveal sitting in a part-panel that isn't on screen must not eat
     an arrow press - the room would see nothing happen. */
  function onScreen(el) {
    const p = el.closest(".partpanel");
    return !p || p.classList.contains("shown");
  }
  /* Reveal the next hidden thing on this slide; false when none is left. */
  function revealNext(s) {
    const el = Array.from(s.querySelectorAll(HIDDEN)).find(onScreen);
    if (!el) return false;
    if (el.matches(".steps > li")) { el.classList.add("shown"); syncStepBtn(el.parentElement); }
    else if (el.classList.contains("frag")) { el.classList.add("on"); syncFragBtns(s); }
    else { el.classList.add("shown"); syncAnsBtn(el); }
    return true;
  }
  function revealNextFrag(s) {
    const f = s.querySelector(".frag:not(.on)");
    if (f) { f.classList.add("on"); syncFragBtns(s); return true; }
    return false;
  }
  function unrevealLastFrag(s) {
    const on = s.querySelectorAll(".frag.on");
    if (on.length) { on[on.length - 1].classList.remove("on"); syncFragBtns(s); return true; }
    return false;
  }
  function next() { if (!revealNext(slides[cur])) go(cur + 1); updateFade(); }
  function prev() { if (!unrevealLastFrag(slides[cur])) go(cur - 1); updateFade(); }

  /* Buttons: <button data-nav="prev|next|first|last"> */
  document.querySelectorAll("[data-nav]").forEach(btn => {
    btn.addEventListener("click", () => {
      const d = btn.dataset.nav;
      if (d === "prev") prev();
      else if (d === "next") next();
      else if (d === "first") go(0);
      else if (d === "last") go(slides.length - 1);
    });
  });

  /* Keyboard */
  document.addEventListener("keydown", e => {
    if (e.target.matches("input, textarea, select")) return;
    const m = document.querySelector(".slidemenu");
    if (m && !m.hidden) return;           /* menu open: let it own the keyboard */
    if (/^[1-9]$/.test(e.key)) {          /* jump to <section data-lesson="n"> */
      const t = slides.findIndex(s => s.dataset.lesson === e.key);
      if (t >= 0) { go(t); return; }
    }
    switch (e.key) {
      case "ArrowRight": case "PageDown": case " ": next(); e.preventDefault(); break;
      case "ArrowLeft": case "PageUp": prev(); e.preventDefault(); break;
      case "Home": go(0); break;
      case "End": go(slides.length - 1); break;
      case "r": case "R": revealNext(slides[cur]); break;
      case "f": case "F":
        document.fullscreenElement ? document.exitFullscreen() : document.documentElement.requestFullscreen();
        break;
    }
  });

  /* Per-slide topic in the lesson tag: <section data-topic="Lesson 2 · …"> */
  const tagEl = document.querySelector(".lessontag");
  const tagDefault = tagEl ? tagEl.textContent : "";
  function updateTag() {
    if (tagEl) tagEl.textContent = slides[cur].dataset.topic || tagDefault;
  }

  /* Touch swipe.
     Dragging a range slider is a horizontal gesture too, so a swipe that
     starts on a control must not also advance the slide — on a touchscreen
     (interactive whiteboard, iPad) that made sliders look broken: the deck
     jumped away mid-drag. Opt anything else out with [data-noswipe]. */
  const NOSWIPE = "input, textarea, select, [data-noswipe]";
  let x0 = null;
  document.addEventListener("touchstart", e => {
    const t = e.target;
    x0 = (t && t.closest && t.closest(NOSWIPE)) ? null : e.touches[0].clientX;
  }, { passive: true });
  document.addEventListener("touchend", e => {
    if (x0 === null) return;
    const dx = e.changedTouches[0].clientX - x0;
    if (Math.abs(dx) > 60) (dx < 0 ? next() : prev());
    x0 = null;
  }, { passive: true });

  /* Step reveals: <button class="reveal-btn" data-target="#steps1">Show working</button>
     (data-steps="steps1" is the legacy spelling and is accepted too).
     State lives in the DOM so the arrow keys and the button agree. */
  function wireSteps(btn) {
    const list = btn.dataset.target ? document.querySelector(btn.dataset.target)
      : btn.dataset.steps ? document.getElementById(btn.dataset.steps)
      : btn.closest(".slide") && btn.closest(".slide").querySelector(".steps");
    if (!list) return;
    stepBtns.set(list, { btn: btn, label: btn.textContent });
    btn.addEventListener("click", () => {
      const li = list.querySelector(":scope > li:not(.shown)");
      if (li) li.classList.add("shown");
      else list.querySelectorAll(":scope > li").forEach(x => x.classList.remove("shown"));
      syncStepBtn(list);
    });
  }

  /* Answer toggles: <button class="reveal-btn" data-answer="#a1">Show answer</button>
     or a .reveal-btn inside a .qcard (toggles its .a) */
  function wireAnswer(btn) {
    const a = btn.dataset.answer
      ? document.querySelector(btn.dataset.answer)
      : btn.closest(".qcard") && btn.closest(".qcard").querySelector(".a");
    if (!a) return;
    a.setAttribute("data-answer-for", "");   /* marks it for arrow-key reveal */
    ansBtns.set(a, { btn: btn, label: btn.textContent });
    btn.addEventListener("click", () => { a.classList.toggle("shown"); syncAnsBtn(a); });
  }

  document.querySelectorAll(".reveal-btn").forEach(btn => {
    if (btn.dataset.frag !== undefined)
      btn.addEventListener("click", () => revealNextFrag(btn.closest(".slide")));
    else if (btn.dataset.answer || btn.closest(".qcard")) wireAnswer(btn);
    else wireSteps(btn);
  });

  /* Part tabs: <button class="ptab" data-part="#p1"> + <div class="partpanel" id="p1"> */
  document.querySelectorAll(".ptab").forEach(tab => {
    tab.addEventListener("click", () => {
      const scope = tab.closest(".slide");
      scope.querySelectorAll(".ptab").forEach(t => {
        if (t.classList.contains("active")) t.classList.replace("active", "done");
      });
      tab.classList.add("active");
      tab.classList.remove("done");
      scope.querySelectorAll(".partpanel").forEach(p => p.classList.remove("shown"));
      const panel = document.querySelector(tab.dataset.part);
      if (panel) panel.classList.add("shown");
    });
  });

  /* Slide-jump menu (opt-in): needs a .slidemenu overlay containing
     .menugrid, plus a .menubtn to open it. Entries are built from every
     slide carrying data-menu. Absent markup → nothing happens. */
  const menu = document.querySelector(".slidemenu");
  const menuGrid = menu && menu.querySelector(".menugrid");
  let menuItems = [];
  if (menuGrid) {
    slides.forEach((s, i) => {
      const item = document.createElement("button");
      item.className = "menuitem";
      item.innerHTML = '<span class="mi-num">' + String(i + 1).padStart(2, "0") + "</span>" +
                       '<div class="mi-title"></div>';
      item.querySelector(".mi-title").textContent = s.dataset.menu || "Slide " + (i + 1);
      item.addEventListener("click", () => { go(i); closeMenu(); });
      menuGrid.appendChild(item);
    });
    menuItems = Array.from(menuGrid.children);
  }
  function markMenu() {
    menuItems.forEach((m, i) => m.classList.toggle("active", i === cur));
  }
  function openMenu() { if (!menu) return; markMenu(); menu.hidden = false; }
  function closeMenu() { if (menu) menu.hidden = true; }
  function toggleMenu() { if (menu) (menu.hidden ? openMenu() : closeMenu()); }
  document.querySelectorAll(".menubtn").forEach(b => b.addEventListener("click", toggleMenu));
  document.querySelectorAll(".menuclose").forEach(b => b.addEventListener("click", closeMenu));
  if (menu) {
    document.addEventListener("keydown", e => {
      if (e.key === "Escape") closeMenu();
      else if ((e.key === "m" || e.key === "M") && !e.target.matches("input, textarea, select")) toggleMenu();
    });
  }

  /* Init: honour #n in URL, set chrome */
  const fromHash = parseInt(location.hash.slice(1), 10);
  slides.forEach(s => s.classList.remove("active"));
  cur = (!isNaN(fromHash) && fromHash >= 1 && fromHash <= slides.length) ? fromHash - 1 : 0;
  slides[cur].classList.add("active");
  if (progress) progress.style.width = ((cur + 1) / slides.length * 100) + "%";
  if (counter) counter.textContent = (cur + 1) + " / " + slides.length;
  updateTag();
  updateFade();
})();
