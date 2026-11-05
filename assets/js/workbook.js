/* ============================================================
   workbook.js — book navigation for the Year 7 workbook look
   Zero dependencies. Load it in <head> WITHOUT defer, after
   workbook.css, so the opening class is set before first paint:

     <script src="../../assets/js/workbook.js"></script>

   Three behaviours, all skipped under prefers-reduced-motion:

   1. Shelf → unit. Clicking a .cover-card gives that cover the
      view-transition-name "book-cover" and remembers the target
      URL in sessionStorage. Pages that link workbook.css opt into
      cross-document View Transitions, so the cover glides from the
      shelf to the middle of the unit page (Chrome/Edge/Safari;
      Firefox just loads the page).
   2. On the unit page, if we arrived from that cover, <html> gets
      .wb-opening: the .book-opener (the same cover) swings open on
      its left edge to reveal the contents, then removes itself.
      A direct visit, a reload or Back never plays it.
   3. Contents → lesson. Clicking a .lesson-page plays a short
      page-flick (~0.7 s): one page fills the window, bound by a spine
      on its left edge, and leaves lift off it from that hinge. Then
      it follows the link.
      Modified clicks (new tab etc.) are left alone.
   ============================================================ */
(function () {
  "use strict";
  var KEY = "wb-open";
  var reduce = window.matchMedia &&
    window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var root = document.documentElement;

  function norm(u) {             // ".../space/index.html#x" -> ".../space/"
    try {
      var url = new URL(u, location.href);
      return url.origin + url.pathname.replace(/index\.html$/, "");
    } catch (e) { return String(u); }
  }

  /* ---- 2. Arrival: decide before first paint ---- */
  try {
    var want = sessionStorage.getItem(KEY);
    sessionStorage.removeItem(KEY);
    if (want && !reduce && norm(want) === norm(location.href)) {
      root.classList.add("wb-opening");
    }
  } catch (e) { /* storage blocked: no animation, page still works */ }

  function endOpening() { root.classList.remove("wb-opening", "wb-swinging"); }

  function plainClick(e) {
    return e.button === 0 && !e.defaultPrevented &&
      !(e.metaKey || e.ctrlKey || e.shiftKey || e.altKey);
  }

  /* ---- 3. Page flick ---- */
  function flick(link) {
    var page = (link.querySelector(".bk-page") || {}).textContent || "";
    var o = document.createElement("div");
    o.className = "wb-flip";
    o.setAttribute("aria-hidden", "true");
    var html = '<div class="wf-book"><div class="wf-page">' +
      (page ? '<span class="wf-turn">p.&nbsp;' + page.trim() + "</span>" : "") +
      "</div>";
    for (var i = 0; i < 5; i++) {
      html += '<div class="wf-leaf" style="--i:' + i + '"></div>';
    }
    o.innerHTML = html + "</div>";
    document.body.appendChild(o);
    root.classList.add("wb-flipping");
    window.setTimeout(function () { location.href = link.href; }, 720);
  }

  document.addEventListener("click", function (e) {
    if (!e.target.closest || !plainClick(e)) return;

    var cover = e.target.closest("a.cover-card");
    if (cover) {                                   /* 1. shelf -> unit */
      if (reduce) return;
      var img = cover.querySelector("img");
      if (img) img.style.viewTransitionName = "book-cover";
      try { sessionStorage.setItem(KEY, cover.href); } catch (err) {}
      return;
    }

    var lesson = e.target.closest("a.lesson-page");
    if (lesson && !reduce) {                       /* 3. contents -> lesson */
      e.preventDefault();
      if (!root.classList.contains("wb-flipping")) flick(lesson);
    }
  });

  /* The swing starts only once the view transition has finished —
     during the transition the cover is a captured snapshot, so a swing
     run then is never seen. Browsers without `pagereveal` (Firefox)
     have no transition either, so they start straight away. */
  var swung = false;
  function swing() {
    if (swung || !root.classList.contains("wb-opening")) return;
    swung = true;
    root.classList.add("wb-swinging");
    var frame = document.querySelector(".book-opener .bo-frame");
    if (frame) {
      frame.addEventListener("animationend", function (e) {
        if (e.target === frame) endOpening();     // the frame fades last
      });
    }
    window.setTimeout(endOpening, 2200);          // safety net
  }
  window.addEventListener("pagereveal", function (e) {
    if (!root.classList.contains("wb-opening")) return;
    if (e.viewTransition) e.viewTransition.finished.then(swing, swing);
    else swing();
  });
  document.addEventListener("DOMContentLoaded", function () {
    if (!document.querySelector(".book-opener")) { endOpening(); return; }
    if (!("onpagereveal" in window)) window.setTimeout(swing, 60);
    window.setTimeout(swing, 1500);               // transition never ended
  });

  /* Back/forward cache restores the page mid-animation: reset it. */
  window.addEventListener("pageshow", function (e) {
    if (!e.persisted) return;
    endOpening();
    root.classList.remove("wb-flipping");
    var f = document.querySelector(".wb-flip");
    if (f) f.remove();
    var imgs = document.querySelectorAll(".cover-card img");
    for (var i = 0; i < imgs.length; i++) imgs[i].style.viewTransitionName = "";
  });
})();
