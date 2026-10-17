/* ============================================================
   leversim.js — LEVER BALANCE (optional module)
   Pairs with assets/css/leversim.css. No dependencies, no build.

     <div class="leversim"></div>

   Optional attributes:
     data-load="100"        load mass in grams
     data-loadarm="20"      load arm in cm (the load sits left of the fulcrum)
     data-effort="50"       starting effort mass in grams
     data-arm="30"          starting effort arm in cm (right of the fulcrum)
     data-masses="50,100,150,200"   the effort masses offered as buttons
     data-moveload="on"     add a slider for the load arm too
     data-hold="off"        start with the stick free (default: held level)

   The set-up is Experiment 4 in the Forces lesson booklet: a metre
   stick resting on a fulcrum at its 50 cm mark, a load on the left,
   slotted effort masses on the right. Drag the effort (or use the
   slider), then "Let go" and the stick tips towards whichever side
   has the bigger turning effect, mass × arm.

   Two things are deliberate:
   - The stick's own weight acts at its centre, on the fulcrum, so it
     has no turning effect and is left out. That is why the booklet's
     method keeps the fulcrum at 50 cm.
   - "Balanced" means the effort is within half a centimetre of the
     exact balance point. Positions move in whole centimetres (as a
     student reads a metre stick), so a 150 g effort, whose exact
     point is 13.3 cm, balances at 13 cm. An exact-equality test
     would never call it balanced.
   An unbalanced stick does not hang at an angle that depends on how
   unbalanced it is: it tips until its end meets the bench. The arm
   dimensions and labels are drawn level, at the tipped positions.
   ============================================================ */
(function () {
  'use strict';

  var SVGNS = 'http://www.w3.org/2000/svg';

  /* Geometry, in viewBox units. 8 units per centimetre of stick.
     The fulcrum is a low prism, so a tipped stick rests at about 4°
     with its end on the bench — enough to read at a glance without
     swinging the masses' labels out of the picture. */
  var PX = 8, FX = 480, FY = 242;                 /* fulcrum apex */
  var SX0 = FX - 50 * PX, SX1 = FX + 50 * PX;     /* 0 cm and 100 cm ends */
  var STICK_H = 24, BENCH_Y = 272, TOP = FY - STICK_H;
  var MAX_TILT = Math.asin((BENCH_Y - FY) / (50 * PX)) * 180 / Math.PI;
  var LOAD_W = 56, LOAD_H = 56, DISC_W = 52, DISC_H = 13;
  var DIM_Y = 104;                                /* the arm dimensions, always level */

  var reduceMotion = window.matchMedia &&
    window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function el(tag, attrs, cls, text) {
    var e = document.createElementNS(SVGNS, tag);
    for (var k in attrs) e.setAttribute(k, attrs[k]);
    if (cls) e.setAttribute('class', cls);
    if (text != null) e.textContent = text;
    return e;
  }
  function html(tag, cls, text) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text != null) e.textContent = text;
    return e;
  }
  function clear(g) { while (g.firstChild) g.removeChild(g.firstChild); }
  function fmt(v) { return String(Math.round(v * 100) / 100); }
  function int(v, d) { var n = parseInt(v, 10); return isNaN(n) ? d : n; }

  /* Dimension arrow between x1 and x2. The label sits centred above
     the arrow when it fits; otherwise just outside it, on the side
     given by `out` (-1 left, 1 right), so two short arms never print
     their labels on top of each other. */
  function dim(g, x1, x2, y, text, cls, out) {
    if (Math.abs(x2 - x1) < 2) return;
    var a = Math.min(x1, x2), b = Math.max(x1, x2), h = Math.min(10, (b - a) / 2);
    g.appendChild(el('line', { x1: a + h, y1: y, x2: b - h, y2: y }, 'ls-dim ' + cls));
    g.appendChild(el('polygon', { points: a + ',' + y + ' ' + (a + h) + ',' + (y - 5) + ' ' + (a + h) + ',' + (y + 5) }, 'ls-dimhead ' + cls));
    g.appendChild(el('polygon', { points: b + ',' + y + ' ' + (b - h) + ',' + (y - 5) + ' ' + (b - h) + ',' + (y + 5) }, 'ls-dimhead ' + cls));
    var t = el('text', { x: (a + b) / 2, y: y - 9 }, 'ls-dimlab ' + cls, text);
    g.appendChild(t);
    var w = t.getComputedTextLength ? t.getComputedTextLength() : 0;
    if (w + 16 > b - a) {
      t.setAttribute('y', y + 6);
      if (out < 0) { t.setAttribute('x', a - 8); t.style.textAnchor = 'end'; }
      else { t.setAttribute('x', b + 8); t.style.textAnchor = 'start'; }
    }
  }

  function build(host) {
    var load = int(host.dataset.load, 100);
    var loadArm = int(host.dataset.loadarm, 20);
    var masses = (host.dataset.masses || '50,100,150,200').split(',')
      .map(function (m) { return int(m, 0); }).filter(function (m) { return m > 0; });
    var effort = int(host.dataset.effort, masses[0]);
    var arm = int(host.dataset.arm, 30);
    var moveLoad = host.dataset.moveload === 'on';
    var held = host.dataset.hold !== 'off';
    var angle = 0, target = 0, raf = null;

    /* ---------- scene ---------- */
    var svg = el('svg', { viewBox: '0 76 960 222', xmlns: SVGNS, role: 'img' });
    svg.appendChild(el('rect', { x: 20, y: BENCH_Y, width: 920, height: 24 }, 'ls-bench'));
    svg.appendChild(el('line', { x1: 20, y1: BENCH_Y, x2: 940, y2: BENCH_Y }, 'ls-benchline'));
    svg.appendChild(el('text', { x: 28, y: BENCH_Y + 17 }, 'ls-small', 'bench'));
    var gSupports = el('g');
    svg.appendChild(gSupports);
    svg.appendChild(el('polygon', {
      points: FX + ',' + FY + ' ' + (FX - 30) + ',' + BENCH_Y + ' ' + (FX + 30) + ',' + BENCH_Y
    }, 'ls-fulcrum'));
    svg.appendChild(el('text', { x: FX + 40, y: BENCH_Y + 18 }, 'ls-fulcrumlab', 'fulcrum at 50 cm'));

    /* gTurn tips with the stick; gOver holds the words and the arm
       dimensions, drawn level at the tipped positions so they stay
       readable and never rotate out of the picture. */
    var gTurn = el('g'), gOver = el('g');
    svg.appendChild(gTurn);
    svg.appendChild(gOver);
    gTurn.appendChild(el('rect', { x: SX0, y: TOP, width: SX1 - SX0, height: STICK_H, rx: 2 }, 'ls-stick'));
    for (var c = 0; c <= 100; c += 5) {
      var x = SX0 + c * PX, major = c % 10 === 0;
      gTurn.appendChild(el('line', { x1: x, y1: TOP, x2: x, y2: TOP + (major ? 9 : 5) }, 'ls-tick'));
      if (major && c > 0 && c < 100) {
        gTurn.appendChild(el('text', { x: x, y: FY - 3 }, 'ls-ticklab', String(c)));
      }
    }
    var gLoad = el('g', {}, 'ls-loadgrp'), gEffort = el('g', {}, 'ls-effortgrp');
    gTurn.appendChild(gLoad);
    gTurn.appendChild(gEffort);
    host.appendChild(svg);

    /* ---------- readout ---------- */
    var read = html('div', 'ls-readout');
    read.setAttribute('aria-live', 'polite');
    var rLoad = html('span', 'ls-stat'), rEff = html('span', 'ls-stat'), rVerdict = html('span', 'ls-verdict');
    read.appendChild(rLoad); read.appendChild(rEff); read.appendChild(rVerdict);
    host.appendChild(read);

    /* ---------- controls ---------- */
    var ctrls = html('div', 'ls-controls');
    ctrls.setAttribute('data-noswipe', '');

    var massBox = html('div', 'ls-masses');
    massBox.appendChild(html('span', 'ls-ctrl-lab', 'Effort mass'));
    var massBtns = masses.map(function (m) {
      var b = html('button', 'ls-btn ls-mass', m + ' g');
      b.type = 'button';
      b.addEventListener('click', function () { effort = m; render(); });
      massBox.appendChild(b);
      return b;
    });
    ctrls.appendChild(massBox);

    var sliders = html('div', 'ls-sliders');
    function slider(label, value, onInput) {
      var box = html('div', 'ctrl');
      var lab = html('label');
      lab.appendChild(document.createTextNode(label + ' '));
      var out = html('output', null, value + ' cm');
      lab.appendChild(out);
      var inp = document.createElement('input');
      inp.type = 'range'; inp.min = '1'; inp.max = '49'; inp.step = '1'; inp.value = String(value);
      inp.setAttribute('aria-label', label + ' in centimetres');
      inp.addEventListener('input', function () { onInput(parseInt(inp.value, 10)); render(); });
      box.appendChild(lab); box.appendChild(inp);
      sliders.appendChild(box);
      return { inp: inp, out: out };
    }
    var sArm = slider('Effort arm', arm, function (v) { arm = v; });
    var sLoad = moveLoad ? slider('Load arm', loadArm, function (v) { loadArm = v; }) : null;
    ctrls.appendChild(sliders);

    var holdBtn = html('button', 'ls-btn ls-hold');
    holdBtn.type = 'button';
    holdBtn.addEventListener('click', function () { held = !held; render(); });
    ctrls.appendChild(holdBtn);
    host.appendChild(ctrls);

    /* ---------- dragging ---------- */
    function armFromPointer(e, side) {
      var pt = svg.createSVGPoint();
      pt.x = e.clientX; pt.y = e.clientY;
      var p = pt.matrixTransform(svg.getScreenCTM().inverse());
      var a = angle * Math.PI / 180;
      var along = (p.x - FX) * Math.cos(a) + (p.y - FY) * Math.sin(a);   /* distance along the tilted stick */
      return Math.max(1, Math.min(49, Math.round(side * along / PX)));
    }
    function draggable(g, side, set) {
      g.addEventListener('pointerdown', function (e) {
        e.preventDefault();
        g.setPointerCapture(e.pointerId);
        g.classList.add('is-dragging');
        function move(ev) { set(armFromPointer(ev, side)); render(); }
        function up() {
          g.classList.remove('is-dragging');
          g.removeEventListener('pointermove', move);
          g.removeEventListener('pointerup', up);
          g.removeEventListener('pointercancel', up);
        }
        g.addEventListener('pointermove', move);
        g.addEventListener('pointerup', up);
        g.addEventListener('pointercancel', up);
      });
    }
    draggable(gEffort, 1, function (v) { arm = v; });
    if (moveLoad) draggable(gLoad, -1, function (v) { loadArm = v; });
    gEffort.classList.add('is-draggable');
    if (moveLoad) gLoad.classList.add('is-draggable');

    /* ---------- tipping animation ---------- */
    var lx, ex, stackTop;                           /* set by render() */
    function rot(x, y) {                            /* a point on the stick, after tipping */
      var a = angle * Math.PI / 180, dx = x - FX, dy = y - FY;
      return { x: FX + dx * Math.cos(a) - dy * Math.sin(a), y: FY + dx * Math.sin(a) + dy * Math.cos(a) };
    }
    function applyAngle() {
      gTurn.setAttribute('transform', 'rotate(' + angle.toFixed(3) + ' ' + FX + ' ' + FY + ')');
      clear(gOver);
      var pL = rot(lx, TOP), pE = rot(ex, TOP);
      var lIn = rot(lx, TOP - LOAD_H / 2 + 6), lName = rot(lx, TOP - LOAD_H - 9);
      var eMass = rot(ex, stackTop - 8), eName = rot(ex, stackTop - 30);
      gOver.appendChild(el('text', { x: lIn.x, y: lIn.y }, 'ls-masslab ls-loadtxt', load + ' g'));
      gOver.appendChild(el('text', { x: lName.x, y: lName.y }, 'ls-name ls-loadtxt', 'Load'));
      gOver.appendChild(el('text', { x: eMass.x, y: eMass.y }, 'ls-masslab ls-efftxt', effort + ' g'));
      gOver.appendChild(el('text', { x: eName.x, y: eName.y }, 'ls-name ls-efftxt', 'Effort'));
      gOver.appendChild(el('line', { x1: FX, y1: DIM_Y - 10, x2: FX, y2: TOP }, 'ls-guide'));
      gOver.appendChild(el('line', { x1: pL.x, y1: DIM_Y - 10, x2: pL.x, y2: lName.y - 20 }, 'ls-guide'));
      gOver.appendChild(el('line', { x1: pE.x, y1: DIM_Y - 10, x2: pE.x, y2: eName.y - 20 }, 'ls-guide'));
      dim(gOver, pL.x, FX, DIM_Y, 'load arm = ' + loadArm + ' cm', 'is-load', -1);
      dim(gOver, FX, pE.x, DIM_Y, 'effort arm = ' + arm + ' cm', 'is-effort', 1);
    }
    function animate() {
      if (reduceMotion) { angle = target; applyAngle(); return; }
      applyAngle();
      if (raf) return;
      (function step() {
        angle += (target - angle) * 0.18;
        if (Math.abs(target - angle) < 0.02) { angle = target; raf = null; applyAngle(); return; }
        applyAngle();
        raf = requestAnimationFrame(step);
      })();
    }

    /* ---------- draw ---------- */
    function render() {
      lx = FX - loadArm * PX; ex = FX + arm * PX;

      clear(gLoad);
      gLoad.appendChild(el('rect', { x: lx - LOAD_W / 2, y: TOP - LOAD_H, width: LOAD_W, height: LOAD_H, rx: 5 }, 'ls-load'));

      clear(gEffort);
      var n = Math.max(1, Math.round(effort / 50));
      stackTop = TOP - n * DISC_H;
      for (var i = 0; i < n; i++) {
        var y = TOP - (i + 1) * DISC_H;
        gEffort.appendChild(el('rect', { x: ex - DISC_W / 2, y: y, width: DISC_W, height: DISC_H - 1, rx: 3 }, 'ls-disc'));
        gEffort.appendChild(el('line', { x1: ex, y1: y + 2, x2: ex + DISC_W / 2 - 3, y2: y + 2 }, 'ls-slot'));
      }
      /* generous invisible hit areas, so the masses are easy to grab on a touchscreen */
      gEffort.appendChild(el('rect', { x: ex - 36, y: stackTop - 50, width: 72, height: TOP - stackTop + 58 }, 'ls-hit'));
      if (moveLoad) gLoad.appendChild(el('rect', { x: lx - 36, y: TOP - LOAD_H - 30, width: 72, height: LOAD_H + 38 }, 'ls-hit'));

      clear(gSupports);
      if (held) {
        [SX0 + 20, SX1 - 20].forEach(function (sx) {
          gSupports.appendChild(el('rect', { x: sx - 18, y: FY, width: 36, height: BENCH_Y - FY }, 'ls-support'));
          gSupports.appendChild(el('text', { x: sx, y: FY + 21 }, 'ls-supportlab', 'held'));
        });
      }

      /* physics */
      var tl = load * loadArm, te = effort * arm;
      var exact = tl / effort;                       /* effort arm that balances exactly */
      var balanced = Math.abs(arm - exact) <= 0.5;
      var side = balanced ? 0 : (tl > te ? -1 : 1); /* -1: load side down */
      target = held ? 0 : side * MAX_TILT;
      animate();

      /* readout */
      rLoad.innerHTML = 'Load side: <b>' + load + ' g</b> × <b>' + loadArm + ' cm</b>' +
                        (held ? '' : ' = <b>' + tl + '</b>');
      rEff.innerHTML = 'Effort side: <b>' + effort + ' g</b> × <b>' + arm + ' cm</b>' +
                       (held ? '' : ' = <b>' + te + '</b>');
      if (held) {
        rVerdict.className = 'ls-verdict is-held';
        rVerdict.textContent = 'Held level. Predict, then let go';
      } else if (balanced) {
        rVerdict.className = 'ls-verdict is-ok';
        rVerdict.textContent = 'Balanced! MA = ' + arm + ' ÷ ' + loadArm + ' = ' + fmt(arm / loadArm) +
                               ' · or ' + load + ' ÷ ' + effort + ' = ' + fmt(load / effort);
      } else {
        rVerdict.className = 'ls-verdict is-tip';
        rVerdict.textContent = side < 0 ? 'Tips down on the load side' : 'Tips down on the effort side';
      }

      /* controls */
      massBtns.forEach(function (b, i) { b.setAttribute('aria-pressed', masses[i] === effort ? 'true' : 'false'); });
      sArm.inp.value = String(arm); sArm.out.textContent = arm + ' cm';
      if (sLoad) { sLoad.inp.value = String(loadArm); sLoad.out.textContent = loadArm + ' cm'; }
      holdBtn.textContent = held ? 'Let go' : 'Hold it level';
      holdBtn.classList.toggle('is-go', held);

      svg.setAttribute('aria-label', 'A metre stick on a fulcrum at its 50 centimetre mark. A ' + load +
        ' gram load sits ' + loadArm + ' centimetres left of the fulcrum and a ' + effort +
        ' gram effort sits ' + arm + ' centimetres right of it. ' +
        (held ? 'The stick is being held level.' : balanced ? 'The stick balances.' :
         side < 0 ? 'The stick tips down on the load side.' : 'The stick tips down on the effort side.'));
    }

    render();
  }

  function init() {
    var hosts = document.querySelectorAll('.leversim');
    for (var i = 0; i < hosts.length; i++) {
      if (!hosts[i].dataset.lsReady) { hosts[i].dataset.lsReady = '1'; build(hosts[i]); }
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else { init(); }
})();
