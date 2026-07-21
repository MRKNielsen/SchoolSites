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
   - "R" key reveals next step on current slide
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
  }

  /* Frag reveals: forward nav reveals remaining .frag fragments on the
     current slide before advancing; backward nav un-reveals first. */
  function syncFragBtns(s) {
    const left = s.querySelector(".frag:not(.on)");
    s.querySelectorAll(".reveal-btn[data-frag]").forEach(b => b.classList.toggle("done", !left));
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
  function next() { if (!revealNextFrag(slides[cur])) go(cur + 1); updateFade(); }
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

  /* Touch swipe */
  let x0 = null;
  document.addEventListener("touchstart", e => { x0 = e.touches[0].clientX; }, { passive: true });
  document.addEventListener("touchend", e => {
    if (x0 === null) return;
    const dx = e.changedTouches[0].clientX - x0;
    if (Math.abs(dx) > 60) (dx < 0 ? next() : prev());
    x0 = null;
  }, { passive: true });

  /* Step reveals: <button class="reveal-btn" data-target="#steps1">Show working</button> */
  function wireSteps(btn) {
    const target = btn.dataset.target
      ? document.querySelector(btn.dataset.target)
      : btn.closest(".slide").querySelector(".steps");
    if (!target) return;
    const items = Array.from(target.querySelectorAll("li"));
    const label = btn.textContent;
    let shown = 0;
    btn.addEventListener("click", () => {
      if (shown < items.length) {
        items[shown].classList.add("shown");
        shown++;
        if (shown === items.length) btn.textContent = "Reset ↺";
      } else {
        items.forEach(li => li.classList.remove("shown"));
        shown = 0;
        btn.textContent = label;
      }
    });
  }

  /* Answer toggles: <button class="reveal-btn" data-answer="#a1">Show answer</button>
     or a .reveal-btn inside a .qcard (toggles its .a) */
  function wireAnswer(btn) {
    const a = btn.dataset.answer
      ? document.querySelector(btn.dataset.answer)
      : btn.closest(".qcard") && btn.closest(".qcard").querySelector(".a");
    if (!a) return;
    const orig = btn.textContent;
    btn.addEventListener("click", () => {
      const open = a.classList.toggle("shown");
      btn.textContent = open ? "Hide ✕" : orig;
    });
  }

  document.querySelectorAll(".reveal-btn").forEach(btn => {
    if (btn.dataset.frag !== undefined)
      btn.addEventListener("click", () => revealNextFrag(btn.closest(".slide")));
    else if (btn.dataset.answer || btn.closest(".qcard")) wireAnswer(btn);
    else wireSteps(btn);
  });

  /* "R" key: reveal next unshown step / frag on the current slide */
  function revealNext(slide) {
    const next = slide.querySelector(".steps li:not(.shown), .frag:not(.on)");
    if (next) next.classList.add(next.classList.contains("frag") ? "on" : "shown");
  }

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
