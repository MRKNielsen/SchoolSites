/* ============================================================
   Biodiversity & Ecosystems — Teacher Slide Decks
   Navigation, step-reveal, menu logic + spaced retrieval quiz.
   ============================================================ */
(function () {
  /* ---- Core slide navigation (same as Forces) ---- */
  const deck = document.querySelector('.deck');
  const slides = Array.from(document.querySelectorAll('.slide'));
  const progress = document.querySelector('.progress');
  const counter = document.querySelector('.counter');
  const prevBtn = document.querySelector('.nav-prev');
  const nextBtn = document.querySelector('.nav-next');
  const menuBtn = document.querySelector('.menu-btn');
  const menuOverlay = document.querySelector('.menu-overlay');
  const menuClose = document.querySelector('.menu-close');
  const menuGrid = document.querySelector('.menu-grid');

  let current = 0;

  slides.forEach((s, i) => {
    const title = s.getAttribute('data-menu') || ('Slide ' + (i + 1));
    const item = document.createElement('div');
    item.className = 'menu-item';
    item.innerHTML = '<div class="mi-num">' + String(i + 1).padStart(2, '0') + '</div>' +
                     '<div class="mi-title">' + title + '</div>';
    item.addEventListener('click', () => { goTo(i); closeMenu(); });
    menuGrid.appendChild(item);
  });
  const menuItems = Array.from(menuGrid.children);

  function stepsOf(slide) {
    return Array.from(slide.querySelectorAll('.we-step'));
  }
  function revealedCount(slide) {
    return stepsOf(slide).filter(s => s.classList.contains('revealed')).length;
  }

  function show(index) {
    slides.forEach((s, i) => s.classList.toggle('active', i === index));
    current = index;
    progress.style.width = ((index + 1) / slides.length * 100) + '%';
    counter.textContent = (index + 1) + ' / ' + slides.length;
    prevBtn.disabled = index === 0;
    nextBtn.disabled = false;
    menuItems.forEach((m, i) => m.classList.toggle('active', i === index));
  }

  function goTo(index) {
    if (index < 0) index = 0;
    if (index > slides.length - 1) index = slides.length - 1;
    show(index);
  }

  function advance() {
    const slide = slides[current];
    const steps = stepsOf(slide);
    const shown = revealedCount(slide);
    if (steps.length && shown < steps.length) {
      steps[shown].classList.add('revealed');
      return;
    }
    if (current < slides.length - 1) goTo(current + 1);
  }

  function retreat() {
    const slide = slides[current];
    const steps = stepsOf(slide);
    const shown = revealedCount(slide);
    if (steps.length && shown > 0) {
      steps[shown - 1].classList.remove('revealed');
      return;
    }
    if (current > 0) {
      goTo(current - 1);
      const prev = slides[current];
      stepsOf(prev).forEach(s => s.classList.add('revealed'));
    }
  }

  nextBtn.addEventListener('click', advance);
  prevBtn.addEventListener('click', retreat);

  deck.addEventListener('click', (e) => {
    if (e.target.closest('a, button, .menu-item, .qq-opt')) return;
    advance();
  });

  document.addEventListener('keydown', (e) => {
    if (menuOverlay.classList.contains('open')) {
      if (e.key === 'Escape') closeMenu();
      return;
    }
    switch (e.key) {
      case 'ArrowRight':
      case ' ':
      case 'PageDown':
        e.preventDefault(); advance(); break;
      case 'ArrowLeft':
      case 'PageUp':
        e.preventDefault(); retreat(); break;
      case 'Home':
        e.preventDefault(); goTo(0); break;
      case 'End':
        e.preventDefault(); goTo(slides.length - 1); break;
      case 'm': case 'M':
        toggleMenu(); break;
    }
  });

  function openMenu()  { menuOverlay.classList.add('open'); }
  function closeMenu() { menuOverlay.classList.remove('open'); }
  function toggleMenu() { menuOverlay.classList.toggle('open'); }
  menuBtn.addEventListener('click', toggleMenu);
  menuClose.addEventListener('click', closeMenu);

  window.deckGoTo = goTo;

  document.querySelectorAll('[data-goto]').forEach(t => {
    t.addEventListener('click', (e) => {
      e.stopPropagation();
      goTo(parseInt(t.getAttribute('data-goto'), 10));
    });
  });

  function jumpToHash() {
    const h = location.hash.replace('#', '');
    if (!h) return;
    const el = document.querySelector('[data-anchor="' + h + '"]');
    if (el) {
      const idx = slides.indexOf(el);
      if (idx >= 0) goTo(idx);
    }
  }

  show(0);
  jumpToHash();
  window.addEventListener('hashchange', jumpToHash);

  /* ============================================================
     SPACED RETRIEVAL QUIZ ENGINE
     Each deck HTML sets:  window.BIO_DECK_NUM = N;   (before this script)
     questions.js sets:    window.BIO_QUESTIONS = [...];
     The quiz slide has class "quiz-slide" and a child ".quiz-container".
     On load, we filter questions to deck < N, pick 5 at random,
     render interactive MC, and show a tally when all are answered.
     ============================================================ */
  function shuffle(arr) {
    return [...arr].sort(() => Math.random() - 0.5);
  }

  function initQuiz() {
    const quizSlide = document.querySelector('.quiz-slide');
    if (!quizSlide) return;

    const deckNum = window.BIO_DECK_NUM || 1;
    const allQ = window.BIO_QUESTIONS || [];
    const pool = allQ.filter(function(q) { return q.deck < deckNum; });
    const container = quizSlide.querySelector('.quiz-container');
    if (!container) return;

    if (pool.length < 2) {
      container.innerHTML = '<p class="quiz-none">This is your first lesson — no prior content to review yet! Focus on today\'s learning intentions below.</p>';
      return;
    }

    const chosen = shuffle(pool).slice(0, Math.min(5, pool.length));
    let answered = 0;
    let correct = 0;

    const tally = document.createElement('div');
    tally.className = 'quiz-tally';
    container.parentNode.appendChild(tally);

    container.innerHTML = chosen.map(function(q, qi) {
      return '<div class="quiz-q" data-qi="' + qi + '" data-ans="' + q.ans + '">' +
        '<div class="qq-text"><span class="qq-num">Q' + (qi + 1) + '.</span> ' + q.q + '</div>' +
        '<div class="qq-opts">' +
          q.opts.map(function(opt, oi) {
            return '<button class="qq-opt" data-oi="' + oi + '">' + opt + '</button>';
          }).join('') +
        '</div>' +
        '<div class="qq-feedback"></div>' +
      '</div>';
    }).join('');

    container.querySelectorAll('.quiz-q').forEach(function(qDiv, qi) {
      const correctIdx = parseInt(qDiv.dataset.ans, 10);
      const q = chosen[qi];
      qDiv.querySelectorAll('.qq-opt').forEach(function(btn) {
        btn.addEventListener('click', function(e) {
          e.stopPropagation();
          if (qDiv.dataset.answered) return;
          qDiv.dataset.answered = '1';
          answered++;
          const chosenIdx = parseInt(btn.dataset.oi, 10);
          qDiv.querySelectorAll('.qq-opt').forEach(function(b, i) {
            b.disabled = true;
            if (i === correctIdx) b.classList.add('correct');
            else if (i === chosenIdx) b.classList.add('wrong');
          });
          const fb = qDiv.querySelector('.qq-feedback');
          if (chosenIdx === correctIdx) {
            correct++;
            fb.textContent = '✓ Correct!';
            fb.className = 'qq-feedback fb-correct';
          } else {
            fb.textContent = '✗ The correct answer was: ' + q.opts[correctIdx];
            fb.className = 'qq-feedback fb-wrong';
          }
          if (answered === chosen.length) {
            tally.style.display = 'block';
            tally.textContent = 'Quiz complete: ' + correct + ' / ' + chosen.length + ' correct. Well done!';
          }
        });
      });
    });
  }

  initQuiz();
})();
