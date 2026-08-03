/* ============================================================
   quiz.js — SPACED RETRIEVAL QUIZ ENGINE (opt-in)
   Load with:  <script src="../../assets/js/quiz.js" defer></script>
   Styling:    assets/css/quiz.css

   Question bank — a unit-local questions.js sets:
     window.RETRIEVAL_QUESTIONS = [
       { deck: 3, q: "…", opts: ["A","B","C","D"], ans: 1 }   // ans = 0-based
     ];

   Slide markup:
     <section class="slide quiz-slide"
              data-quiz-before="9"     <!-- only questions from decks < 9 -->
              data-quiz-count="5">     <!-- how many to draw (default 5) -->
       <div class="quiz-container"></div>
     </section>

   Renders `count` questions drawn at random from the eligible pool,
   gives instant per-question feedback, and shows a tally once all
   have been answered. No markup → no-op, so this is safe to load
   anywhere.
   ============================================================ */
(function () {
  "use strict";

  function shuffle(arr) {
    const a = arr.slice();
    for (let i = a.length - 1; i > 0; i--) {          /* Fisher-Yates */
      const j = Math.floor(Math.random() * (i + 1));
      [a[i], a[j]] = [a[j], a[i]];
    }
    return a;
  }

  function build(container) {
    const slide = container.closest(".quiz-slide") || container;
    const bank = window.RETRIEVAL_QUESTIONS || [];
    const before = parseInt(slide.dataset.quizBefore, 10);
    const count = parseInt(slide.dataset.quizCount, 10) || 5;

    const pool = isNaN(before) ? bank : bank.filter(q => q.deck < before);
    if (pool.length < 2) {
      container.innerHTML = '<p class="quiz-none">This is the first lesson — no prior content to review yet. ' +
                            "Focus on today's learning intentions.</p>";
      return;
    }

    const chosen = shuffle(pool).slice(0, Math.min(count, pool.length));
    let answered = 0, correct = 0;

    chosen.forEach((q, qi) => {
      const card = document.createElement("div");
      card.className = "quiz-q";

      const text = document.createElement("p");
      text.className = "qq-text";
      text.innerHTML = '<span class="qq-num">Q' + (qi + 1) + ".</span> ";
      text.appendChild(document.createTextNode(q.q));
      card.appendChild(text);

      const opts = document.createElement("div");
      opts.className = "qq-opts";
      const fb = document.createElement("p");
      fb.className = "qq-feedback";

      q.opts.forEach((opt, oi) => {
        const btn = document.createElement("button");
        btn.className = "qq-opt";
        btn.type = "button";
        btn.textContent = opt;
        btn.addEventListener("click", e => {
          e.stopPropagation();
          if (card.dataset.answered) return;
          card.dataset.answered = "1";
          answered++;
          Array.from(opts.children).forEach((b, i) => {
            b.disabled = true;
            if (i === q.ans) b.classList.add("correct");
            else if (i === oi) b.classList.add("wrong");
          });
          if (oi === q.ans) {
            correct++;
            fb.textContent = "✓ Correct!";
            fb.className = "qq-feedback fb-correct";
          } else {
            fb.textContent = "✗ The correct answer was: " + q.opts[q.ans];
            fb.className = "qq-feedback fb-wrong";
          }
          if (answered === chosen.length) {
            tally.textContent = "Quiz complete: " + correct + " / " + chosen.length + " correct.";
            tally.classList.add("shown");
          }
          window.dispatchEvent(new Event("resize"));   /* deck.js re-measures overflow */
        });
        opts.appendChild(btn);
      });

      card.appendChild(opts);
      card.appendChild(fb);
      container.appendChild(card);
    });

    const tally = document.createElement("div");
    tally.className = "quiz-tally";
    container.appendChild(tally);
  }

  document.querySelectorAll(".quiz-container").forEach(build);
})();
