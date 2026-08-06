/* ============================================================
   profile.js — SPECIES / CASE-STUDY PROFILE PAGES
   Companion to profile.css. One job only: highlight the sticky
   .toc chip for the section currently in view.

   Requires nothing. Pages without a .toc or without section.pf
   elements are left alone.
   ============================================================ */
(function () {
  'use strict';

  function init() {
    var toc = document.querySelector('.profile-page .toc');
    if (!toc) return;

    var links = Array.prototype.slice.call(toc.querySelectorAll('a[href^="#"]'));
    if (!links.length) return;

    var map = {};
    var sections = [];
    links.forEach(function (a) {
      var id = a.getAttribute('href').slice(1);
      var sec = document.getElementById(id);
      if (!sec) return;
      map[id] = a;
      sections.push(sec);
    });
    if (!sections.length) return;

    var current = null;
    function setCurrent(id) {
      if (id === current) return;
      current = id;
      links.forEach(function (a) { a.classList.remove('is-current'); });
      if (map[id]) map[id].classList.add('is-current');
    }

    if ('IntersectionObserver' in window) {
      var visible = Object.create(null);
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
          if (e.isIntersecting) visible[e.target.id] = true;
          else delete visible[e.target.id];
        });
        // Topmost visible section wins.
        for (var i = 0; i < sections.length; i++) {
          if (visible[sections[i].id]) { setCurrent(sections[i].id); return; }
        }
      }, { rootMargin: '-80px 0px -65% 0px', threshold: 0 });
      sections.forEach(function (s) { io.observe(s); });
    } else {
      window.addEventListener('scroll', function () {
        var y = window.pageYOffset + 100, pick = sections[0].id;
        sections.forEach(function (s) { if (s.offsetTop <= y) pick = s.id; });
        setCurrent(pick);
      }, { passive: true });
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
