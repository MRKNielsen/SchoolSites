/* ============================================================
   binomsim.js — BINOMIAL → NORMAL VISUALISER (optional module)
   Pairs with assets/css/binomsim.css. No dependencies, no build.

     <div class="binomsim"></div>

   Optional attributes:
     data-n="30"          starting number of trials
     data-p="0.5"         starting probability of success
     data-nmax="200"      top of the n slider (default 200)
     data-controls="off"  render the figure with no sliders

   What the widget exists to show: the bars are the EXACT
   binomial Bi(n, p); the curve is the normal N(np, np(1-p))
   that 15F proposes in its place. The two parameters are not
   chosen to make the picture look good — they are the
   binomial's own mean and variance, which is why the curve
   always sits in the right place and only ever fails on SHAPE.

   Drag p towards 0 or 1 with n small and the bars pile against
   an end: skewed, and no symmetric bell can follow them. That
   is the whole content of the np > 5, n(1-p) > 5 guideline, and
   the verdict chip says so in words rather than leaving the
   student to read a rule off a page.

   Numerics: the pmf is computed in log space via a Lanczos
   log-gamma, not by the product formula. n! overflows a double
   at n = 171 and the naive recurrence from P(0) = (1-p)^n
   underflows to zero for extreme p — either would silently draw
   an empty chart at exactly the settings the widget exists to
   demonstrate.
   ============================================================ */
(function () {
  'use strict';

  var SVGNS = 'http://www.w3.org/2000/svg';

  /* Plot geometry, in viewBox units. */
  var VB_W = 960, VB_H = 300;
  var L = 62, R = 936, YTOP = 30, YBASE = 232;

  /* ---------- numerics ---------- */

  /* Lanczos approximation to ln Γ(z), g = 7, n = 9. Accurate to
     ~15 significant figures over the range we need. */
  var LANCZOS = [
    0.99999999999980993, 676.5203681218851, -1259.1392167224028,
    771.32342877765313, -176.61502916214059, 12.507343278686905,
    -0.13857109526572012, 9.9843695780195716e-6, 1.5056327351493116e-7
  ];
  function lgamma(z) {
    if (z < 0.5) {  /* reflection, not needed here but keeps the fn total */
      return Math.log(Math.PI / Math.sin(Math.PI * z)) - lgamma(1 - z);
    }
    z -= 1;
    var x = LANCZOS[0];
    for (var i = 1; i < 9; i++) x += LANCZOS[i] / (z + i);
    var t = z + 7.5;
    return 0.5 * Math.log(2 * Math.PI) + (z + 0.5) * Math.log(t) - t + Math.log(x);
  }
  function lnChoose(n, k) {
    return lgamma(n + 1) - lgamma(k + 1) - lgamma(n - k + 1);
  }
  function binomPmf(n, k, p) {
    if (k < 0 || k > n) return 0;
    return Math.exp(lnChoose(n, k) + k * Math.log(p) + (n - k) * Math.log(1 - p));
  }
  function normalPdf(x, mu, sd) {
    var z = (x - mu) / sd;
    return Math.exp(-0.5 * z * z) / (sd * Math.sqrt(2 * Math.PI));
  }

  /* ---------- dom helpers ---------- */

  function el(tag, attrs, cls) {
    var e = document.createElementNS(SVGNS, tag);
    for (var k in attrs) e.setAttribute(k, attrs[k]);
    if (cls) e.setAttribute('class', cls);
    return e;
  }
  function html(tag, cls, text) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text != null) e.textContent = text;
    return e;
  }

  /* Axis labels thin out as the window widens, so the ticks never
     collide however far n is dragged. */
  function tickStep(span) {
    var raw = span / 12;
    var pow = Math.pow(10, Math.floor(Math.log(raw) / Math.LN10));
    var mult = raw / pow;
    var nice = mult <= 1 ? 1 : mult <= 2 ? 2 : mult <= 5 ? 5 : 10;
    return Math.max(1, nice * pow);
  }

  /* ---------- build one widget ---------- */

  function build(host) {
    var nMax = parseInt(host.dataset.nmax || '200', 10);
    var n = Math.min(nMax, parseInt(host.dataset.n || '30', 10));
    var p = parseFloat(host.dataset.p || '0.5');
    var showControls = host.dataset.controls !== 'off';

    var svg = el('svg', {
      viewBox: '0 0 ' + VB_W + ' ' + VB_H,
      xmlns: SVGNS, role: 'img',
      'aria-label': 'Bar chart of the exact binomial distribution with the ' +
                    'normal approximation N(np, np(1-p)) drawn over it.'
    });
    var gBars = el('g'), gCurve = el('g'), gAxis = el('g');
    svg.appendChild(gBars);
    svg.appendChild(gCurve);
    svg.appendChild(el('line', { x1: L, y1: YBASE, x2: R, y2: YBASE }, 'bs-axis'));
    svg.appendChild(gAxis);
    var xlab = el('text', { x: (L + R) / 2, y: VB_H - 8 }, 'bs-axislab');
    xlab.textContent = 'number of successes, x';
    svg.appendChild(xlab);
    host.appendChild(svg);

    /* readout */
    var read = html('div', 'bs-readout');
    var rDist = html('span', 'bs-stat');
    var rNp = html('span', 'bs-stat');
    var rSd = html('span', 'bs-stat');
    var rVerdict = html('span', 'bs-verdict');
    read.appendChild(rDist); read.appendChild(rNp);
    read.appendChild(rSd); read.appendChild(rVerdict);
    host.appendChild(read);

    /* controls */
    var nIn, pIn, nOut, pOut;
    if (showControls) {
      var ctrls = html('div', 'bs-controls');
      ctrls.setAttribute('data-noswipe', '');

      var c1 = html('div', 'ctrl');
      var l1 = html('label'); l1.appendChild(document.createTextNode('Trials n '));
      nOut = html('output', null, String(n)); l1.appendChild(nOut);
      nIn = document.createElement('input');
      nIn.type = 'range'; nIn.min = '1'; nIn.max = String(nMax);
      nIn.step = '1'; nIn.value = String(n);
      c1.appendChild(l1); c1.appendChild(nIn);

      var c2 = html('div', 'ctrl');
      var l2 = html('label'); l2.appendChild(document.createTextNode('Success probability p '));
      pOut = html('output', null, p.toFixed(2)); l2.appendChild(pOut);
      pIn = document.createElement('input');
      pIn.type = 'range'; pIn.min = '0.01'; pIn.max = '0.99';
      pIn.step = '0.01'; pIn.value = String(p);
      c2.appendChild(l2); c2.appendChild(pIn);

      ctrls.appendChild(c1); ctrls.appendChild(c2);
      host.appendChild(ctrls);

      nIn.addEventListener('input', function () {
        n = parseInt(nIn.value, 10); nOut.textContent = n; render();
      });
      pIn.addEventListener('input', function () {
        p = parseFloat(pIn.value); pOut.textContent = p.toFixed(2); render();
      });
    }

    function render() {
      var mu = n * p, varr = n * p * (1 - p), sd = Math.sqrt(varr);

      /* Window: four standard deviations either side of the mean,
         clipped to [0, n]. For small n that window is wider than
         the support, so fall back to the whole of it — otherwise a
         one-bar chart appears and the shape is impossible to read. */
      var lo = Math.max(0, Math.floor(mu - 4 * sd));
      var hi = Math.min(n, Math.ceil(mu + 4 * sd));
      if (hi - lo < 6) { lo = 0; hi = n; }
      var bins = hi - lo + 1;

      /* scales */
      var bw = (R - L) / bins;                     /* pixels per unit of x */
      function sx(x) { return L + (x - lo + 0.5) * bw; }

      var pmf = [], ymax = 0;
      for (var k = lo; k <= hi; k++) {
        var v = binomPmf(n, k, p);
        pmf.push(v);
        if (v > ymax) ymax = v;
      }
      var peak = normalPdf(mu, mu, sd);            /* curve can out-top the bars */
      ymax = Math.max(ymax, peak) * 1.12;
      function sy(v) { return YBASE - (v / ymax) * (YBASE - YTOP); }

      /* bars */
      while (gBars.firstChild) gBars.removeChild(gBars.firstChild);
      var half = Math.max(0.5, bw * 0.44);
      for (var i = 0; i < pmf.length; i++) {
        var y = sy(pmf[i]);
        if (YBASE - y < 0.4) continue;             /* skip invisible slivers */
        gBars.appendChild(el('rect', {
          x: sx(lo + i) - half, y: y, width: half * 2, height: YBASE - y,
          rx: Math.min(3, half)
        }, 'bs-bar'));
      }

      /* normal curve, sampled across the window */
      while (gCurve.firstChild) gCurve.removeChild(gCurve.firstChild);
      var d = '', steps = 240;
      for (var s = 0; s <= steps; s++) {
        var x = lo - 0.5 + (hi - lo + 1) * (s / steps);
        var yy = sy(normalPdf(x, mu, sd));
        d += (s ? ' L' : 'M') + sx(x).toFixed(1) + ',' + Math.max(YTOP - 12, yy).toFixed(1);
      }
      gCurve.appendChild(el('path', { d: d }, 'bs-curve'));
      gCurve.appendChild(el('line', {
        x1: sx(mu), y1: YTOP - 12, x2: sx(mu), y2: YBASE
      }, 'bs-mean'));
      var ml = el('text', { x: sx(mu), y: YTOP - 17 }, 'bs-meanlab');
      ml.textContent = 'np = ' + (Math.round(mu * 100) / 100);
      gCurve.appendChild(ml);

      /* axis ticks */
      while (gAxis.firstChild) gAxis.removeChild(gAxis.firstChild);
      var step = tickStep(hi - lo + 1);
      var first = Math.ceil(lo / step) * step;
      for (var t = first; t <= hi; t += step) {
        gAxis.appendChild(el('line', {
          x1: sx(t), y1: YBASE, x2: sx(t), y2: YBASE + 6
        }, 'bs-tick'));
        var tl = el('text', { x: sx(t), y: YBASE + 24 }, 'bs-ticklab');
        tl.textContent = t;
        gAxis.appendChild(tl);
      }

      /* readout + verdict */
      var nq = n * (1 - p), worst = Math.min(mu, nq);
      rDist.innerHTML = '<b>Bi(' + n + ', ' + p.toFixed(2) + ')</b> ≈ ' +
                        '<b>N(' + round2(mu) + ', ' + round2(varr) + ')</b>';
      rNp.innerHTML = 'np = <b>' + round2(mu) + '</b> · n(1−p) = <b>' + round2(nq) + '</b>';
      rSd.innerHTML = 'sd = <b>' + round2(sd) + '</b>';

      /* Two distinct ways the guideline can fail, and they need
         different words. A binomial at p = 0.5 with small n is
         perfectly symmetric — it just has too few bars for a smooth
         curve to mean anything. Calling that "too skewed" would
         teach the wrong diagnosis, so split on the actual skewness,
         (1-2p)/sqrt(np(1-p)). */
      var skew = Math.abs((1 - 2 * p) / sd);
      rVerdict.className = 'bs-verdict ' + (worst >= 10 ? 'ok' : worst >= 5 ? 'edge' : 'bad');
      rVerdict.textContent =
        worst >= 10  ? 'Safe — both comfortably above 5, the fit is close'
      : worst >= 5   ? 'Borderline — the guideline is only just met'
      : skew >= 0.5  ? 'Too skewed — the bars pile against an end, no bell fits'
      :                'Too few trials — the bars are too coarse for a curve';
    }

    function round2(v) { return Math.round(v * 100) / 100; }

    render();
  }

  function init() {
    var hosts = document.querySelectorAll('.binomsim');
    for (var i = 0; i < hosts.length; i++) {
      if (!hosts[i].dataset.bsReady) { hosts[i].dataset.bsReady = '1'; build(hosts[i]); }
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else { init(); }
})();
