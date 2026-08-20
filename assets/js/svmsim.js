/* ============================================================
   svmsim.js — SVM "WIDEST STREET" VISUALISER (optional module)
   Pairs with assets/css/svmsim.css. No dependencies, no build.

     <div class="svmsim"></div>

   Optional attributes:
     data-angle="34"      starting boundary angle in degrees
     data-width="20"      starting street width, in data units
     data-controls="off"  render the figure with no sliders

   What the widget exists to show: an SVM does not pick the
   boundary that looks tidiest — it picks the one with the most
   ROOM either side. Rotating changes how much room is
   available; widening eventually collides with a training
   point. The points it collides with are the support vectors,
   and the widest street over all angles is the SVM solution.

   Geometry. A boundary is the set of points p with p·n = c,
   where n = (cos t, sin t) is the unit normal. Projecting every
   point onto n turns the 2-D separation question into a 1-D
   one: the classes are separable at this angle exactly when
   max(proj of A) < min(proj of B), and the largest street that
   fits is that gap. The boundary is drawn at the midpoint of
   the gap, because an off-centre boundary is never optimal —
   so exposing an offset control would add a degree of freedom
   with only one right answer, and dilute the two that matter.

   The optimum is found by scanning t over a half-turn rather
   than by solving the quadratic program. The scan is over a
   FIXED, small point set and runs once per click, so the cost
   is irrelevant — and a student who steps the angle slider by
   hand is performing the same search, which is the point.

   All geometry is computed in DATA space (0..100 on both axes)
   and mapped to the viewBox only at draw time. Mixing the two
   is how sign errors creep in, because SVG's y axis runs the
   other way.
   ============================================================ */
(function () {
  'use strict';

  var SVGNS = 'http://www.w3.org/2000/svg';

  /* Plot geometry, in viewBox units. */
  var VB_W = 620, VB_H = 400;
  var L = 58, R = 566, TOP = 26, BOT = 330;

  /* Data space is 0..100 on both axes. */
  var DMAX = 100;

  /* A fixed, linearly separable training set. Chosen so the
     widest street sits at an angle the student has to hunt
     for — not at 0 or 45 degrees, where they would land by
     accident and learn nothing. */
  var CLASS_A = [[18, 26], [26, 42], [34, 20], [12, 48], [30, 58], [42, 34]];
  var CLASS_B = [[68, 74], [80, 58], [74, 90], [88, 76], [60, 86], [90, 94]];

  function sx(x) { return L + (x / DMAX) * (R - L); }
  function sy(y) { return BOT - (y / DMAX) * (BOT - TOP); }

  function svg(tag, cls) {
    var e = document.createElementNS(SVGNS, tag);
    if (cls) e.setAttribute('class', cls);
    return e;
  }
  function html(tag, cls, text) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text != null) e.textContent = text;
    return e;
  }
  function attrs(e, o) { for (var k in o) e.setAttribute(k, o[k]); return e; }

  /* ---- geometry, all in data space ---- */

  function normal(deg) {
    var t = deg * Math.PI / 180;
    return [Math.cos(t), Math.sin(t)];
  }
  function proj(p, n) { return p[0] * n[0] + p[1] * n[1]; }

  /* For a given angle: how far apart are the classes along the
     normal, and where is the midpoint between them? */
  function analyse(deg) {
    var n = normal(deg), i;
    var aMax = -Infinity, aArg = null, bMin = Infinity, bArg = null;
    for (i = 0; i < CLASS_A.length; i++) {
      var va = proj(CLASS_A[i], n);
      if (va > aMax) { aMax = va; aArg = CLASS_A[i]; }
    }
    for (i = 0; i < CLASS_B.length; i++) {
      var vb = proj(CLASS_B[i], n);
      if (vb < bMin) { bMin = vb; bArg = CLASS_B[i]; }
    }
    return {
      n: n,
      gap: bMin - aMax,          /* widest street that fits at this angle */
      centre: (aMax + bMin) / 2, /* offset c of the boundary */
      svA: aArg, svB: bArg
    };
  }

  /* Clip the line p·n = c to the data box, returning the two
     endpoints, or null when the line misses the box entirely. */
  function clip(n, c) {
    var d = [-n[1], n[0]];          /* direction along the line */
    var p0 = [c * n[0], c * n[1]];  /* the point on it nearest the origin */
    var lo = -Infinity, hi = Infinity;
    for (var ax = 0; ax < 2; ax++) {
      if (Math.abs(d[ax]) < 1e-12) {
        if (p0[ax] < 0 || p0[ax] > DMAX) return null;
      } else {
        var t1 = (0 - p0[ax]) / d[ax], t2 = (DMAX - p0[ax]) / d[ax];
        if (t1 > t2) { var s = t1; t1 = t2; t2 = s; }
        if (t1 > lo) lo = t1;
        if (t2 < hi) hi = t2;
      }
    }
    if (lo > hi) return null;
    return [[p0[0] + lo * d[0], p0[1] + lo * d[1]],
            [p0[0] + hi * d[0], p0[1] + hi * d[1]]];
  }

  /* Training points strictly inside the street. */
  function inside(n, c, w) {
    var hits = [], i, half = w / 2;
    for (i = 0; i < CLASS_A.length; i++)
      if (Math.abs(proj(CLASS_A[i], n) - c) < half - 1e-9) hits.push(CLASS_A[i]);
    for (i = 0; i < CLASS_B.length; i++)
      if (Math.abs(proj(CLASS_B[i], n) - c) < half - 1e-9) hits.push(CLASS_B[i]);
    return hits;
  }

  /* The widest street over all angles — the SVM solution. */
  function best() {
    var bd = 0, bg = -Infinity;
    /* Step by 1 degree, matching the slider: snapping to an angle the
       slider cannot represent would leave the readout and the picture
       disagreeing by a fraction of a degree. */
    for (var deg = 0; deg < 180; deg += 1) {
      var g = analyse(deg).gap;
      if (g > bg) { bg = g; bd = deg; }
    }
    return { deg: bd, gap: bg };
  }

  function build(host) {
    var angle = parseFloat(host.dataset.angle);
    var width = parseFloat(host.dataset.width);
    if (!isFinite(angle)) angle = 0;
    if (!isFinite(width)) width = 12;
    var showCtrls = host.dataset.controls !== 'off';

    var OPT = best();

    var s = svg('svg');
    s.setAttribute('viewBox', '0 0 ' + VB_W + ' ' + VB_H);
    s.setAttribute('role', 'img');
    s.setAttribute('aria-label', 'Support vector machine margin visualiser');

    var road = svg('polygon', 'sv-road');
    var e1 = svg('line', 'sv-edge'), e2 = svg('line', 'sv-edge');
    var line = svg('line', 'sv-line');
    var frame = attrs(svg('rect', 'sv-frame'),
      { x: sx(0), y: sy(DMAX), width: sx(DMAX) - sx(0), height: sy(0) - sy(DMAX) });

    s.appendChild(frame);
    s.appendChild(road);
    s.appendChild(e1); s.appendChild(e2);
    s.appendChild(line);

    /* points, drawn once; the highlight rings move each update */
    var ringA = attrs(svg('circle', 'sv-sv'), { r: 10 });
    var ringB = attrs(svg('circle', 'sv-sv'), { r: 10 });
    s.appendChild(ringA); s.appendChild(ringB);

    var hitLayer = svg('g');
    s.appendChild(hitLayer);

    function dot(p, cls) {
      var c = attrs(svg('circle', cls), { cx: sx(p[0]), cy: sy(p[1]), r: 6 });
      s.appendChild(c);
    }
    CLASS_A.forEach(function (p) { dot(p, 'sv-a'); });
    CLASS_B.forEach(function (p) { dot(p, 'sv-b'); });

    /* key + axis labels */
    var kA = attrs(svg('circle', 'sv-a'), { cx: L + 8, cy: BOT + 34, r: 6 });
    var kAt = attrs(svg('text', 'sv-keylab'), { x: L + 20, y: BOT + 39 });
    kAt.textContent = 'class A'; kAt.setAttribute('fill', 'var(--accent)');
    var kB = attrs(svg('circle', 'sv-b'), { cx: L + 104, cy: BOT + 34, r: 6 });
    var kBt = attrs(svg('text', 'sv-keylab'), { x: L + 116, y: BOT + 39 });
    kBt.textContent = 'class B'; kBt.setAttribute('fill', 'var(--accent-warm)');
    var kS = attrs(svg('circle', 'sv-sv'), { cx: L + 216, cy: BOT + 34, r: 8 });
    var kSt = attrs(svg('text', 'sv-keylab'), { x: L + 230, y: BOT + 39 });
    kSt.textContent = 'nearest point each side'; kSt.setAttribute('fill', 'var(--neg)');
    [kA, kAt, kB, kBt, kS, kSt].forEach(function (n) { s.appendChild(n); });

    var xlab = attrs(svg('text', 'sv-axlab'), { x: (sx(0) + sx(DMAX)) / 2, y: BOT + 66 });
    xlab.textContent = 'feature 1';
    s.appendChild(xlab);

    host.appendChild(s);

    /* ---- readout ---- */
    var read = html('div', 'sv-readout');
    var statW = html('span', 'sv-stat');
    var statM = html('span', 'sv-stat');
    var verdict = html('span', 'sv-verdict');
    read.appendChild(statW); read.appendChild(statM); read.appendChild(verdict);
    host.appendChild(read);

    /* ---- controls ---- */
    var aIn, wIn, aOut, wOut;
    if (showCtrls) {
      var ctrls = html('div', 'sv-controls');
      ctrls.setAttribute('data-noswipe', '');

      var c1 = html('div', 'ctrl');
      var l1 = html('label');
      l1.appendChild(document.createTextNode('Boundary angle '));
      aOut = html('output', null, angle.toFixed(0) + '°');
      l1.appendChild(aOut);
      aIn = document.createElement('input');
      attrs(aIn, { type: 'range', min: '0', max: '179', step: '1' });
      aIn.value = String(angle);
      c1.appendChild(l1); c1.appendChild(aIn);

      var c2 = html('div', 'ctrl');
      var l2 = html('label');
      l2.appendChild(document.createTextNode('Street width '));
      wOut = html('output', null, width.toFixed(1));
      l2.appendChild(wOut);
      wIn = document.createElement('input');
      attrs(wIn, { type: 'range', min: '0', max: '60', step: '0.5' });
      wIn.value = String(width);
      c2.appendChild(l2); c2.appendChild(wIn);

      var snap = html('button', 'sv-snap', 'Snap to the widest street');
      snap.type = 'button';

      ctrls.appendChild(c1); ctrls.appendChild(c2); ctrls.appendChild(snap);
      host.appendChild(ctrls);

      aIn.addEventListener('input', function () {
        angle = parseFloat(aIn.value); draw();
      });
      wIn.addEventListener('input', function () {
        width = parseFloat(wIn.value); draw();
      });
      snap.addEventListener('click', function () {
        /* Floor, not round: rounding up would push the street a hair
           wider than the gap and report its own answer as invalid. */
        angle = OPT.deg; width = Math.floor(OPT.gap * 2) / 2;
        aIn.value = String(angle); wIn.value = String(width);
        draw();
      });
    }

    function segment(el, seg) {
      if (!seg) { el.setAttribute('x1', 0); el.setAttribute('y1', 0);
                  el.setAttribute('x2', 0); el.setAttribute('y2', 0); return; }
      attrs(el, { x1: sx(seg[0][0]), y1: sy(seg[0][1]),
                  x2: sx(seg[1][0]), y2: sy(seg[1][1]) });
    }

    function draw() {
      var a = analyse(angle);
      var n = a.n, c = a.centre, half = width / 2;

      var mid = clip(n, c);
      var s1 = clip(n, c - half);
      var s2 = clip(n, c + half);

      var hits = inside(n, c, width);
      var separable = a.gap > 0;
      var tooWide = hits.length > 0;
      var atOptimum = separable && Math.abs(width - a.gap) < 0.6 &&
                      Math.abs(a.gap - OPT.gap) < 0.6;

      segment(line, mid);
      segment(e1, s1); segment(e2, s2);

      if (s1 && s2) {
        road.setAttribute('points',
          [sx(s1[0][0]) + ',' + sy(s1[0][1]),
           sx(s1[1][0]) + ',' + sy(s1[1][1]),
           sx(s2[1][0]) + ',' + sy(s2[1][1]),
           sx(s2[0][0]) + ',' + sy(s2[0][1])].join(' '));
      } else {
        road.setAttribute('points', '');
      }

      [road, e1, e2, line].forEach(function (el) {
        el.classList.toggle('bad', tooWide || !separable);
      });

      attrs(ringA, { cx: sx(a.svA[0]), cy: sy(a.svA[1]) });
      attrs(ringB, { cx: sx(a.svB[0]), cy: sy(a.svB[1]) });
      var showRings = separable ? 1 : 0;
      ringA.setAttribute('opacity', showRings);
      ringB.setAttribute('opacity', showRings);

      while (hitLayer.firstChild) hitLayer.removeChild(hitLayer.firstChild);
      hits.forEach(function (p) {
        hitLayer.appendChild(attrs(svg('circle', 'sv-hit'),
          { cx: sx(p[0]), cy: sy(p[1]), r: 10 }));
      });

      statW.innerHTML = 'Street width <b>' + width.toFixed(1) + '</b>';
      statM.innerHTML = separable
        ? 'widest that fits at ' + angle.toFixed(0) + '°: <b>' + a.gap.toFixed(1) + '</b>'
        : 'the classes overlap at this angle';

      verdict.className = 'sv-verdict';
      if (!separable) {
        verdict.classList.add('bad');
        verdict.textContent = 'No boundary at this angle separates the classes';
      } else if (tooWide) {
        verdict.classList.add('bad');
        verdict.textContent = hits.length + ' point' + (hits.length > 1 ? 's' : '') +
                              ' inside the street — too wide';
      } else if (atOptimum) {
        verdict.classList.add('best');
        verdict.textContent = 'This is the widest street of all — the SVM solution';
      } else {
        verdict.classList.add('ok');
        verdict.textContent = 'Valid street — but is there a wider one?';
      }

      if (aOut) aOut.textContent = angle.toFixed(0) + '°';
      if (wOut) wOut.textContent = width.toFixed(1);
    }

    draw();
  }

  function init() {
    var nodes = document.querySelectorAll('.svmsim');
    for (var i = 0; i < nodes.length; i++) build(nodes[i]);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
