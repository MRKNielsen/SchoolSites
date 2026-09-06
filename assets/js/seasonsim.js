/* ============================================================
   seasonsim.js — SEASONS VISUALISER (optional module)
   Pairs with assets/css/seasonsim.css. No dependencies, no build.

     <div class="seasonsim"></div>

   Optional attributes:
     data-hemisphere="south|north"   which hemisphere's season is named
                                     (default south — Melbourne)
     data-start="0".."1"             starting point in the year
     data-labels="off"               hide the scene text labels

   Teaching point the widget exists to make: THE AXIS NEVER MOVES.
   It stays tilted 23.5° in one fixed direction all the way round the
   orbit. Nothing about Earth changes through the year — only where
   Earth is. That is why the hemisphere leaning sunward swaps, and it
   is the whole mechanism of the seasons.

   Two deliberate choices, both anti-misconception:

   - The orbit is drawn as a CIRCLE. Earth's eccentricity is 0.017, so
     a circle is very nearly right, and an obviously elliptical orbit
     with the Sun at the centre is what makes students say "summer is
     when we're closest". The readout states the real distance figure
     instead, and it says outright that distance is not the cause.
   - The close-up keeps the axis at a FIXED screen angle and swings the
     lit half around it. Drawing it the other way — rotating Earth to
     keep the Sun on the left — is easier, and teaches the opposite of
     the truth.
   ============================================================ */
(function () {
  'use strict';

  var TWO_PI = Math.PI * 2;
  var TILT = 23.44;                       // degrees
  var TILT_RAD = TILT * Math.PI / 180;

  /* t = 0 at the December solstice, running forward through the year. */
  var MARKERS = [
    [0.00, '21 December', 'solstice'],
    [0.25, '20 March',    'equinox'],
    [0.50, '21 June',     'solstice'],
    [0.75, '22 September','equinox']
  ];
  var SEASON_S = ['Summer', 'Autumn', 'Winter', 'Spring'];
  var MONTHS = ['January','February','March','April','May','June',
                'July','August','September','October','November','December'];
  var CUM = [0,31,59,90,120,151,181,212,243,273,304,334];   // non-leap

  function svgEl(name, attrs) {
    var e = document.createElementNS('http://www.w3.org/2000/svg', name);
    for (var k in attrs) if (attrs.hasOwnProperty(k)) e.setAttribute(k, attrs[k]);
    return e;
  }

  /* Day-of-year for a fraction through the year measured from 21 December. */
  function dayOfYear(t) { return (t * 365 + 355) % 365; }

  function dateLabel(t) {
    var d = dayOfYear(t), m = 11;
    for (var i = 11; i >= 0; i--) { if (d >= CUM[i]) { m = i; break; } }
    return (Math.floor(d - CUM[m]) + 1) + ' ' + MONTHS[m];
  }

  /* Latitude at which the Sun is directly overhead. -23.44° at the
     December solstice, 0 at an equinox, +23.44° in June. */
  function subsolar(t) { return -TILT * Math.cos(TWO_PI * t); }

  function nearestMarker(t) {
    for (var i = 0; i < MARKERS.length; i++) {
      var d = Math.abs(((t - MARKERS[i][0] + 0.5) % 1) - 0.5);
      if (d < 0.012) return MARKERS[i];
    }
    return null;
  }

  function build(host) {
    var south = (host.dataset.hemisphere || 'south') !== 'north';
    var showLabels = host.dataset.labels !== 'off';
    var t = parseFloat(host.dataset.start || '0');

    var W = 560, H = 250;
    var SX = 176, SY = 126, ORB = 96;      // Sun centre, orbit radius
    var CX = 438, CY = 116, CR = 62;       // close-up Earth centre + radius

    var svg = svgEl('svg', {
      viewBox: '0 0 ' + W + ' ' + H, role: 'img',
      'aria-label': 'Earth orbiting the Sun with a fixed axial tilt, showing how the seasons arise'
    });

    // ---- Sun ----
    svg.appendChild(svgEl('circle', { class: 'ss-sun-halo', cx: SX, cy: SY, r: 30 }));
    svg.appendChild(svgEl('circle', { class: 'ss-sun', cx: SX, cy: SY, r: 17 }));

    // ---- Orbit (circular, on purpose) + the four station points ----
    svg.appendChild(svgEl('circle', { class: 'ss-orbit', cx: SX, cy: SY, r: ORB }));
    MARKERS.forEach(function (m) {
      var a = TWO_PI * m[0];
      svg.appendChild(svgEl('circle', {
        class: 'ss-station', cx: SX + ORB * Math.cos(a), cy: SY + ORB * Math.sin(a), r: 2.6
      }));
    });

    // ---- Earth on the orbit: dark disc, lit half, fixed axis ----
    var mini = svgEl('g', {});
    mini.appendChild(svgEl('circle', { class: 'ss-mini-dark', cx: 0, cy: 0, r: 13 }));
    var miniLit = svgEl('path', { class: 'ss-mini-lit', d: 'M 0,-13 A 13,13 0 0,1 0,13 Z' });
    mini.appendChild(miniLit);
    mini.appendChild(svgEl('circle', { class: 'ss-mini-ring', cx: 0, cy: 0, r: 13 }));
    // axis drawn in the group's own frame, never rotated — that is the point
    mini.appendChild(svgEl('line', {
      class: 'ss-mini-axis',
      x1: 18 * Math.sin(TILT_RAD), y1: -18 * Math.cos(TILT_RAD),
      x2: -18 * Math.sin(TILT_RAD), y2: 18 * Math.cos(TILT_RAD)
    }));
    svg.appendChild(mini);

    // ---- Close-up ----
    var closeG = svgEl('g', { transform: 'translate(' + CX + ',' + CY + ')' });
    closeG.appendChild(svgEl('circle', { class: 'ss-earth-dark', cx: 0, cy: 0, r: CR }));
    var litG = svgEl('g', {});
    litG.appendChild(svgEl('path', { class: 'ss-earth-lit', d: 'M 0,' + (-CR) + ' A ' + CR + ',' + CR + ' 0 0,1 0,' + CR + ' Z' }));
    closeG.appendChild(litG);

    // Sunlight arriving from whichever side the Sun is on. Rotated by the same
    // bearing as the lit half, so the rays always strike the lit face — without
    // them the close-up gives no clue where the Sun is.
    var raysG = svgEl('g', {});
    [-30, 0, 30].forEach(function (dy) {
      raysG.appendChild(svgEl('line', {
        class: 'ss-ray', x1: CR + 34, y1: dy, x2: CR + 9, y2: dy
      }));
      raysG.appendChild(svgEl('path', {
        class: 'ss-ray-head',
        d: 'M ' + (CR + 9) + ',' + dy + ' l 7,-3.5 l 0,7 z'
      }));
    });
    closeG.appendChild(raysG);

    // latitude furniture, fixed to the axis
    var tiltG = svgEl('g', { transform: 'rotate(' + TILT + ')' });
    tiltG.appendChild(svgEl('line', { class: 'ss-equator', x1: -CR, y1: 0, x2: CR, y2: 0 }));
    [-1, 1].forEach(function (s) {
      var y = s * CR * Math.sin(TILT_RAD);
      var half = CR * Math.cos(TILT_RAD);
      tiltG.appendChild(svgEl('line', { class: 'ss-tropic', x1: -half, y1: y, x2: half, y2: y }));
    });
    tiltG.appendChild(svgEl('line', { class: 'ss-axis', x1: 0, y1: -(CR + 16), x2: 0, y2: CR + 16 }));
    var nCap = svgEl('circle', { class: 'ss-pole', cx: 0, cy: -(CR + 16), r: 3 });
    var sCap = svgEl('circle', { class: 'ss-pole', cx: 0, cy: CR + 16, r: 3 });
    tiltG.appendChild(nCap); tiltG.appendChild(sCap);
    var nTxt = svgEl('text', { class: 'ss-pole-lbl', x: 0, y: -(CR + 24), 'text-anchor': 'middle' });
    nTxt.textContent = 'N';
    var sTxt = svgEl('text', { class: 'ss-pole-lbl', x: 0, y: CR + 32, 'text-anchor': 'middle' });
    sTxt.textContent = 'S';
    tiltG.appendChild(nTxt); tiltG.appendChild(sTxt);
    closeG.appendChild(tiltG);
    closeG.appendChild(svgEl('circle', { class: 'ss-earth-ring', cx: 0, cy: 0, r: CR }));
    svg.appendChild(closeG);

    if (showLabels) {
      var lbl = function (x, y, txt, key) {
        var e = svgEl('text', { class: 'ss-label' + (key ? ' is-key' : ''), x: x, y: y, 'text-anchor': 'middle' });
        e.textContent = txt; svg.appendChild(e);
      };
      lbl(SX, SY + 38, 'Sun');
      lbl(CX, CY + CR + 52, 'The axis never moves', true);
      lbl(CX, CY + CR + 66, 'only Earth does');
    }

    // ---- readout + controls ----
    var readout = document.createElement('div');
    readout.className = 'ss-readout';
    var seasonEl = document.createElement('span'); seasonEl.className = 'ss-season';
    var dateEl   = document.createElement('span'); dateEl.className = 'ss-date';
    var tiltEl   = document.createElement('span'); tiltEl.className = 'ss-tiltnote';
    readout.appendChild(seasonEl); readout.appendChild(dateEl); readout.appendChild(tiltEl);

    var controls = document.createElement('div');
    controls.className = 'ss-controls';

    var play = document.createElement('button');
    play.type = 'button'; play.className = 'ss-btn ss-play';
    play.textContent = 'Play';
    play.setAttribute('aria-label', 'Animate Earth through one year');

    var range = document.createElement('input');
    range.type = 'range'; range.min = '0'; range.max = '1000'; range.step = '1';
    range.setAttribute('aria-label', 'Position in the year, starting at the December solstice');

    var hemiWrap = document.createElement('label');
    hemiWrap.className = 'ss-hemi';
    var hemiBox = document.createElement('input');
    hemiBox.type = 'checkbox'; hemiBox.checked = south;
    hemiWrap.appendChild(hemiBox);
    hemiWrap.appendChild(document.createTextNode('Australian seasons'));

    controls.appendChild(play); controls.appendChild(range); controls.appendChild(hemiWrap);

    // deck.js reads this: dragging inside the widget is scrubbing the year,
    // not a swipe to the next slide.
    host.setAttribute('data-noswipe', '');

    host.appendChild(svg);
    host.appendChild(readout);
    host.appendChild(controls);

    // ---- render ----
    function render() {
      var a = TWO_PI * t;
      var ex = SX + ORB * Math.cos(a);
      var ey = SY + ORB * Math.sin(a);

      // The lit path is the +x semicircle, and rotate(θ) maps +x onto θ, so
      // the rotation angle IS the bearing to the Sun.
      var toSun = Math.atan2(SY - ey, SX - ex) * 180 / Math.PI;
      mini.setAttribute('transform', 'translate(' + ex.toFixed(1) + ',' + ey.toFixed(1) + ')');
      miniLit.setAttribute('transform', 'rotate(' + toSun.toFixed(1) + ')');
      litG.setAttribute('transform', 'rotate(' + toSun.toFixed(1) + ')');
      raysG.setAttribute('transform', 'rotate(' + toSun.toFixed(1) + ')');

      var d = subsolar(t);
      var southward = d < 0;                     // Sun overhead south of the equator
      var favoured = southward ? 'Southern' : 'Northern';
      var quarter = Math.floor(((t % 1) + 1) % 1 * 4) % 4;
      var season = south ? SEASON_S[quarter] : SEASON_S[(quarter + 2) % 4];

      var mk = nearestMarker(t);
      seasonEl.textContent = season + (south ? ' in Australia' : ' in the north');
      dateEl.textContent = mk ? (mk[1] + ' — ' + mk[2]) : dateLabel(t);
      dateEl.classList.toggle('is-marker', !!mk);

      if (Math.abs(d) < 0.4) {
        tiltEl.textContent = 'Neither hemisphere tilted toward the Sun — day and night equal everywhere';
      } else {
        tiltEl.textContent = favoured + ' Hemisphere tilted toward the Sun · Sun overhead at '
          + Math.abs(d).toFixed(1) + '°' + (southward ? 'S' : 'N');
      }

      if (range.value !== String(Math.round(t * 1000))) range.value = Math.round(t * 1000);
    }

    // ---- interaction ----
    range.addEventListener('input', function () {
      stop(); t = parseInt(range.value, 10) / 1000; render();
    });
    // deck.js and sitenav.js already ignore keydown on form controls; this only
    // has to swallow the arrows the slider itself consumes, so Escape and N
    // still reach the drawer.
    range.addEventListener('keydown', function (e) {
      if (e.key.indexOf('Arrow') === 0 || e.key === 'Home' || e.key === 'End') e.stopPropagation();
    });
    hemiBox.addEventListener('change', function () { south = hemiBox.checked; render(); });

    var raf = null, last = 0;
    function frame(ts) {
      if (!last) last = ts;
      t = (t + (ts - last) / 16000) % 1;      // one year ≈ 16 s
      last = ts; render();
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
    document.addEventListener('visibilitychange', function () { if (document.hidden) stop(); });

    render();
  }

  function init() {
    var hosts = document.querySelectorAll('.seasonsim');
    for (var i = 0; i < hosts.length; i++) {
      if (!hosts[i].dataset.ssReady) { hosts[i].dataset.ssReady = '1'; build(hosts[i]); }
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else { init(); }
})();
