/* ============================================================
   orbit.js — ORBITAL PHASE VISUALISER (optional module)
   Pairs with assets/css/orbit.css. No dependencies, no build.

     <div class="orbitsim" data-hemisphere="south"></div>

   Optional attributes:
     data-hemisphere="south|north"   default south (Melbourne)
     data-start="0".."1"             starting point in the cycle
     data-labels="off"               hide the scene text labels

   Teaching point the widget exists to make: the Moon's lit half
   ALWAYS faces the Sun. The phase is just how much of that lit
   half we can see from Earth. Nothing here casts Earth's shadow
   on the Moon — that's an eclipse, and it's the misconception
   the slide beside this is trying to kill.

   Southern hemisphere is the default because an observer in
   Melbourne sees the disc rotated 180° from the northern
   textbook picture: a waxing Moon is lit on the LEFT here.
   ============================================================ */
(function () {
  'use strict';

  var SYNODIC = 29.5;           // days, new Moon to new Moon
  var TWO_PI = Math.PI * 2;

  var PHASES = [
    [0.000, 'New Moon'],        [0.030, 'Waxing crescent'],
    [0.220, 'First quarter'],   [0.280, 'Waxing gibbous'],
    [0.470, 'Full Moon'],       [0.530, 'Waning gibbous'],
    [0.720, 'Third quarter'],   [0.780, 'Waning crescent'],
    [0.970, 'New Moon']
  ];

  function phaseName(f) {
    for (var i = PHASES.length - 1; i >= 0; i--) {
      if (f >= PHASES[i][0]) return PHASES[i][1];
    }
    return 'New Moon';
  }

  function svgEl(name, attrs) {
    var e = document.createElementNS('http://www.w3.org/2000/svg', name);
    for (var k in attrs) if (attrs.hasOwnProperty(k)) e.setAttribute(k, attrs[k]);
    return e;
  }

  /* The lit shape of the disc as seen from Earth.
     Limb is a semicircle; the terminator is a semi-ellipse whose
     x-radius shrinks to zero at the quarters and grows again — which
     is exactly why a quarter Moon's edge is a straight line. */
  function phasePath(r, f) {
    var k = Math.cos(TWO_PI * f);        //  1 at new, -1 at full
    var rx = Math.abs(k) * r;
    var waxing = f < 0.5;
    var limbSweep = waxing ? 1 : 0;
    // Reversing the sweep carves the terminator out of the lit side (crescent);
    // keeping it adds the far semi-ellipse on (gibbous).
    var termSweep = waxing ? (f < 0.25 ? 0 : 1) : (f > 0.75 ? 1 : 0);
    return 'M 0,' + (-r) +
           ' A ' + r + ',' + r + ' 0 0,' + limbSweep + ' 0,' + r +
           ' A ' + rx.toFixed(2) + ',' + r + ' 0 0,' + termSweep + ' 0,' + (-r);
  }

  function build(host) {
    var south = (host.dataset.hemisphere || 'south') !== 'north';
    var showLabels = host.dataset.labels !== 'off';
    var f = parseFloat(host.dataset.start || '0.16');

    // ---- geometry ----
    var W = 460, H = 250;
    var EX = 250, EY = 132, ORB = 88;      // Earth centre, orbit radius
    var SX = 34,  SY = 132;                // Sun centre
    var DX = 408, DY = 60,  DR = 34;       // phase disc centre + radius

    var svg = svgEl('svg', {
      viewBox: '0 0 ' + W + ' ' + H,
      role: 'img',
      'aria-label': 'Diagram of the Moon orbiting Earth, showing why we see phases'
    });

    // Sun
    svg.appendChild(svgEl('circle', { class: 'os-sun-halo', cx: SX, cy: SY, r: 34 }));
    svg.appendChild(svgEl('circle', { class: 'os-sun', cx: SX, cy: SY, r: 19 }));
    [-30, -15, 0, 15, 30].forEach(function (dy) {
      svg.appendChild(svgEl('line', {
        class: 'os-ray', x1: SX + 24, y1: SY + dy * 0.75, x2: SX + 74, y2: SY + dy * 0.9
      }));
    });

    // Orbit path + Earth
    svg.appendChild(svgEl('circle', { class: 'os-orbit', cx: EX, cy: EY, r: ORB }));
    var sight = svgEl('line', { class: 'os-sight', x1: EX, y1: EY, x2: EX, y2: EY });
    svg.appendChild(sight);
    svg.appendChild(svgEl('circle', { class: 'os-earth', cx: EX, cy: EY, r: 19 }));
    // Earth's own night side — reinforces that the Sun lights one half of everything
    svg.appendChild(svgEl('path', {
      class: 'os-earth-nightside',
      d: 'M ' + EX + ',' + (EY - 19) + ' A 19,19 0 0,1 ' + EX + ',' + (EY + 19) + ' Z'
    }));

    // Moon: dark disc + lit half, rotated so the lit half faces the Sun
    var moon = svgEl('g', {});
    moon.appendChild(svgEl('circle', { class: 'os-moon-dark', cx: 0, cy: 0, r: 11 }));
    var moonLit = svgEl('path', {
      class: 'os-moon-lit',
      d: 'M 0,-11 A 11,11 0 0,1 0,11 Z'
    });
    moon.appendChild(moonLit);
    moon.appendChild(svgEl('circle', { class: 'os-moon-ring', cx: 0, cy: 0, r: 11 }));
    svg.appendChild(moon);

    // Phase disc — what an observer on Earth actually sees
    var discG = svgEl('g', { transform: 'translate(' + DX + ',' + DY + ')' });
    discG.appendChild(svgEl('circle', { class: 'os-disc-bg', cx: 0, cy: 0, r: DR }));
    var discInner = svgEl('g', south ? { transform: 'rotate(180)' } : {});
    var discLit = svgEl('path', { class: 'os-disc-lit', d: '' });
    discInner.appendChild(discLit);
    discG.appendChild(discInner);
    discG.appendChild(svgEl('circle', { class: 'os-disc-ring', cx: 0, cy: 0, r: DR }));
    svg.appendChild(discG);

    if (showLabels) {
      var lbl = function (x, y, t, key) {
        var e = svgEl('text', { class: 'os-label' + (key ? ' is-key' : ''), x: x, y: y, 'text-anchor': 'middle' });
        e.textContent = t; svg.appendChild(e);
      };
      lbl(SX, SY + 40, 'Sun');
      lbl(EX, EY + 36, 'Earth');
      lbl(DX, DY + DR + 18, 'What you see', true);
      var hemi = svgEl('text', { class: 'os-label', x: DX, y: DY + DR + 32, 'text-anchor': 'middle' });
      hemi.textContent = south ? '(southern sky)' : '(northern sky)';
      svg.appendChild(hemi);
    }

    // ---- controls ----
    var readout = document.createElement('div');
    readout.className = 'os-readout';
    var nameEl = document.createElement('span'); nameEl.className = 'os-phase';
    var dayEl = document.createElement('span'); dayEl.className = 'os-day';
    readout.appendChild(nameEl); readout.appendChild(dayEl);

    var controls = document.createElement('div');
    controls.className = 'os-controls';

    var play = document.createElement('button');
    play.type = 'button';
    play.className = 'os-btn os-play';
    play.textContent = 'Play';
    play.setAttribute('aria-label', 'Animate the Moon through one orbit');

    var range = document.createElement('input');
    range.type = 'range';
    range.min = '0'; range.max = '1000'; range.step = '1';
    range.setAttribute('aria-label', 'Position in the 29.5 day cycle');

    var hemiWrap = document.createElement('label');
    hemiWrap.className = 'os-hemi';
    var hemiBox = document.createElement('input');
    hemiBox.type = 'checkbox'; hemiBox.checked = south;
    hemiWrap.appendChild(hemiBox);
    hemiWrap.appendChild(document.createTextNode('Southern view'));

    controls.appendChild(play);
    controls.appendChild(range);
    controls.appendChild(hemiWrap);

    host.appendChild(svg);
    host.appendChild(readout);
    host.appendChild(controls);

    // ---- render ----
    function render() {
      // f = 0 → Moon between Earth and Sun (new). f = 0.5 → Earth in the middle (full).
      var a = Math.PI + TWO_PI * f;
      var mx = EX + ORB * Math.cos(a);
      var my = EY + ORB * Math.sin(a);
      // Lit half faces the Sun. The lit path is the +x semicircle in local
      // coords, and rotate(θ) maps +x onto θ — so the angle IS the bearing to
      // the Sun, with no offset.
      var toSun = Math.atan2(SY - my, SX - mx) * 180 / Math.PI;
      moon.setAttribute('transform', 'translate(' + mx.toFixed(1) + ',' + my.toFixed(1) + ') rotate(' + toSun.toFixed(1) + ')');
      sight.setAttribute('x2', mx.toFixed(1));
      sight.setAttribute('y2', my.toFixed(1));

      discLit.setAttribute('d', phasePath(DR, f));

      nameEl.textContent = phaseName(f);
      dayEl.textContent = 'Day ' + (f * SYNODIC).toFixed(1) + ' of ' + SYNODIC;
      if (range.value !== String(Math.round(f * 1000))) range.value = Math.round(f * 1000);
    }

    // ---- interaction ----
    range.addEventListener('input', function () {
      stop();
      f = parseInt(range.value, 10) / 1000;
      render();
    });
    // deck.js and sitenav.js both already ignore keydown on form controls, so
    // this only has to cover the arrows the slider itself consumes — stopping
    // everything would also swallow Escape and N, which belong to the drawer.
    range.addEventListener('keydown', function (e) {
      if (e.key.indexOf('Arrow') === 0 || e.key === 'Home' || e.key === 'End') {
        e.stopPropagation();
      }
    });

    hemiBox.addEventListener('change', function () {
      south = hemiBox.checked;
      discInner.setAttribute('transform', south ? 'rotate(180)' : '');
      if (showLabels) hemi.textContent = south ? '(southern sky)' : '(northern sky)';
    });

    var raf = null, last = 0;
    function frame(t) {
      if (!last) last = t;
      f = (f + (t - last) / 12000) % 1;     // one orbit ≈ 12 s
      last = t;
      render();
      raf = requestAnimationFrame(frame);
    }
    function stop() {
      if (raf) { cancelAnimationFrame(raf); raf = null; }
      last = 0; play.textContent = 'Play';
    }
    play.addEventListener('click', function () {
      if (raf) { stop(); return; }
      play.textContent = 'Pause';
      raf = requestAnimationFrame(frame);
    });
    // Never leave an animation running on a slide the class has left.
    document.addEventListener('visibilitychange', function () {
      if (document.hidden) stop();
    });

    render();
  }

  function init() {
    var hosts = document.querySelectorAll('.orbitsim');
    for (var i = 0; i < hosts.length; i++) {
      if (!hosts[i].dataset.osReady) { hosts[i].dataset.osReady = '1'; build(hosts[i]); }
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else { init(); }
})();
