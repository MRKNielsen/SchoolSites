/* ============================================================
   test.js — EMAILED TEST ENGINE (opt-in)
   A one-sitting test: the student enters their name, their email
   and their teacher's email, answers every question, submits, and
   the page marks it and opens the student's email app with the
   results addressed to the teacher (student cc'd).

   NOTHING IS STORED. No localStorage, no cookies, no server — the
   answers live only in this tab until it closes. The only copy
   that survives is the email the student sends.

   Page markup (see tools/test-demo.html for a full page):
     <link rel="stylesheet" href="../../assets/css/quiz.css">
     <link rel="stylesheet" href="../../assets/css/test.css">
     <body class="quizapp-page testapp-page theme-science">
       <div id="test-app"></div>
       <script src="test-questions.js"></script>
       <script src="../../assets/js/test.js" defer></script>

   test-questions.js sets window.TEST:
     window.TEST = {
       title:   "Space — Topic Test",
       subject: "Year 7 Science",            // shown above the title
       backHref: "index.html",                // optional back link
       teachers: [                            // optional: a dropdown instead of a typed address
         { name: "Mr Nielsen", email: "teacher@example.edu.au" }
       ],
       teacherDomain: "",                     // optional: only accept teacher emails @this domain
       studentDomain: "",                     // optional: only accept student emails @this domain
       reveal: "marks",                       // after submitting the student sees:
                                              //   "score"   — total only
                                              //   "marks"   — total + ✓/✗ per question (default)
                                              //   "answers" — the above + the correct answers
       shuffleQuestions: false,
       shuffleOptions:   false,
       questions: [
         { q: "…", opts: ["A","B","C","D"], ans: 1, marks: 1 },        // multiple choice, ans 0-based
         { type: "short",  q: "…", accept: ["gravity"], marks: 1 },     // typed, any accepted answer
         { type: "number", q: "…", ans: 9.8, tol: 0.1, unit: "m/s²" },  // numeric, ± tol
         { type: "written", q: "…", marks: 3, lines: 5 }                // teacher marks it
       ]
     };

   Question and option text is HTML (so <em>, <sub>, MathJax \( \)
   all work); the email gets the plain-text version.

   The student is cc'd, so the email only includes correct answers
   when reveal is "answers".

   The answer key is in test-questions.js, so a determined student
   can read it — this is for low-stakes checks, not SACs/CATs.
   ============================================================ */
(function () {
  "use strict";

  const T = window.TEST;
  const app = document.getElementById("test-app");
  if (!app || !T || !Array.isArray(T.questions)) return;

  const MAILTO_LIMIT = 1900;          /* Outlook/Windows truncate mailto URLs near 2,000 chars */
  const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

  /* ---------- helpers ---------- */
  function el(tag, cls, html) {
    const e = document.createElement(tag);
    if (cls) e.className = cls;
    if (html != null) e.innerHTML = html;
    return e;
  }
  function plain(html) {
    const d = document.createElement("div");
    d.innerHTML = html;
    return (d.textContent || "").replace(/\s+/g, " ").trim();
  }
  function shuffle(arr) {
    const a = arr.slice();
    for (let i = a.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [a[i], a[j]] = [a[j], a[i]];
    }
    return a;
  }
  function esc(s) {
    return String(s).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);
  }
  function norm(s) { return String(s).toLowerCase().replace(/\s+/g, " ").trim(); }
  function typeOf(q) { return q.type || (q.opts ? "mc" : "short"); }
  function marksOf(q) { return q.marks == null ? 1 : q.marks; }
  function letter(i) { return String.fromCharCode(65 + i); }
  function typeset(node) {
    if (window.MathJax && MathJax.typesetPromise) MathJax.typesetPromise([node]).catch(() => {});
  }
  function domainOk(email, domain) {
    return !domain || email.toLowerCase().endsWith("@" + domain.toLowerCase().replace(/^@/, ""));
  }
  function fmtTime(d) {
    return d.toLocaleString("en-AU", { weekday: "short", day: "numeric", month: "short",
      year: "numeric", hour: "numeric", minute: "2-digit" });
  }

  /* ---------- build the question list (fixed for this sitting) ---------- */
  let qs = T.questions.map((q, i) => {
    const c = Object.assign({ orig: i }, q);
    if (typeOf(q) === "mc") {
      c.order = q.opts.map((_, k) => k);
      if (T.shuffleOptions) c.order = shuffle(c.order);
    }
    return c;
  });
  if (T.shuffleQuestions) qs = shuffle(qs);
  const autoTotal = qs.filter(q => typeOf(q) !== "written").reduce((s, q) => s + marksOf(q), 0);
  const writtenTotal = qs.filter(q => typeOf(q) === "written").reduce((s, q) => s + marksOf(q), 0);

  let student = null, startedAt = null, inProgress = false;

  window.addEventListener("beforeunload", e => {
    if (inProgress) { e.preventDefault(); e.returnValue = ""; }
  });

  /* ---------- header ---------- */
  const header = el("div", "page-header");
  if (T.backHref) header.appendChild(el("a", "back-link", "&#8592; Back")).href = T.backHref;
  if (T.subject) header.appendChild(el("p", "test-eyebrow", T.subject));
  header.appendChild(el("h1", null, T.title || "Test"));
  header.appendChild(el("p", "sub",
    qs.length + " questions &middot; " + (autoTotal + writtenTotal) + " marks"));
  app.appendChild(header);

  /* ---------- 1. details ---------- */
  const details = el("form", "test-details");
  details.noValidate = true;
  details.innerHTML =
    '<p class="test-note">Your results are emailed to your teacher when you finish. ' +
    'Nothing is saved on this website &mdash; if you close or refresh this tab, your answers are lost.</p>' +
    '<label class="test-field"><span>Your full name</span>' +
      '<input name="name" autocomplete="name" required></label>' +
    '<label class="test-field"><span>Your school email</span>' +
      '<input name="email" type="email" autocomplete="email" required></label>' +
    '<label class="test-field"><span>Your teacher</span>' +
      (Array.isArray(T.teachers) && T.teachers.length
        ? '<select name="teacher" required><option value="">Choose your teacher…</option>' +
          T.teachers.map(t => '<option value="' + esc(t.email) + '">' + esc(t.name) + "</option>").join("") +
          "</select>"
        : '<input name="teacher" type="email" placeholder="teacher’s email address" required>') +
    "</label>" +
    '<p class="test-error" role="alert"></p>' +
    '<button class="start-btn" type="submit">Start test &#8594;</button>';
  app.appendChild(details);

  details.addEventListener("submit", e => {
    e.preventDefault();
    const f = details.elements;
    const name = f.name.value.trim();
    const email = f.email.value.trim();
    const teacher = f.teacher.value.trim();
    const err = details.querySelector(".test-error");
    let msg = "";
    if (!name) msg = "Enter your name.";
    else if (!EMAIL_RE.test(email)) msg = "Check your email address.";
    else if (!domainOk(email, T.studentDomain)) msg = "Use your school email (@" + T.studentDomain + ").";
    else if (!EMAIL_RE.test(teacher)) msg = "Check your teacher’s email address.";
    else if (!domainOk(teacher, T.teacherDomain)) msg = "Your teacher’s email should end in @" + T.teacherDomain + ".";
    else if (teacher.toLowerCase() === email.toLowerCase()) msg = "That’s your email — enter your teacher’s.";
    err.textContent = msg;
    if (msg) return;

    student = { name, email, teacher };
    startedAt = new Date();
    inProgress = true;
    details.hidden = true;
    paper.hidden = false;
    paper.querySelector(".test-who").textContent = name + " · " + email;
    window.scrollTo(0, 0);
  });

  /* ---------- 2. the paper ---------- */
  const paper = el("form", "test-paper");
  paper.hidden = true;
  paper.noValidate = true;
  paper.appendChild(el("p", "test-who"));

  qs.forEach((q, i) => {
    const card = el("fieldset", "q-card test-q");
    q.card = card;
    const kind = typeOf(q);
    const m = marksOf(q);
    card.appendChild(el("legend", "q-deck-tag",
      "Question " + (i + 1) + " &middot; " + m + " mark" + (m === 1 ? "" : "s")));
    card.appendChild(el("div", "q-text", q.q));
    const nm = "q" + i;

    if (kind === "mc") {
      const opts = el("div", "test-opts");
      q.order.forEach((k, pos) => {
        const lab = el("label", "test-opt");
        const r = el("input"); r.type = "radio"; r.name = nm; r.value = k;
        lab.appendChild(r);
        lab.appendChild(el("span", "test-opt-letter", letter(pos)));
        lab.appendChild(el("span", "test-opt-text", q.opts[k]));
        opts.appendChild(lab);
      });
      card.appendChild(opts);
    } else if (kind === "written") {
      const ta = el("textarea", "test-input"); ta.name = nm; ta.rows = q.lines || 5;
      card.appendChild(ta);
    } else {
      const wrap = el("div", "test-inline");
      const inp = el("input", "test-input"); inp.name = nm; inp.autocomplete = "off";
      if (kind === "number") inp.inputMode = "decimal";
      wrap.appendChild(inp);
      if (q.unit) wrap.appendChild(el("span", "test-unit", q.unit));
      card.appendChild(wrap);
    }
    card.appendChild(el("p", "test-mark"));
    paper.appendChild(card);
  });

  const submitRow = el("div", "test-submit");
  submitRow.appendChild(el("p", "test-error", ""));
  submitRow.appendChild(el("button", "start-btn", "Submit &amp; email results")).type = "submit";
  paper.appendChild(submitRow);
  app.appendChild(paper);
  typeset(paper);

  /* ---------- marking ---------- */
  function responseOf(q, i) {
    const f = paper.elements["q" + i];
    if (typeOf(q) === "mc") {
      const r = paper.querySelector('input[name="q' + i + '"]:checked');
      return r ? parseInt(r.value, 10) : null;
    }
    const v = f.value.trim();
    return v === "" ? null : v;
  }
  function mark(q, resp) {
    const kind = typeOf(q);
    if (resp == null) return kind === "written" ? null : 0;
    if (kind === "mc") return resp === q.ans ? marksOf(q) : 0;
    if (kind === "written") return null;
    if (kind === "number") {
      const n = parseFloat(String(resp).replace(/[^\d.eE+\-]/g, ""));
      return !isNaN(n) && Math.abs(n - q.ans) <= (q.tol || 0) + 1e-12 ? marksOf(q) : 0;
    }
    return (q.accept || []).some(a => norm(a) === norm(resp)) ? marksOf(q) : 0;
  }
  function keyText(q) {
    const kind = typeOf(q);
    if (kind === "mc") return letter(q.order.indexOf(q.ans)) + ") " + plain(q.opts[q.ans]);
    if (kind === "number") return q.ans + (q.tol ? " (± " + q.tol + ")" : "") + (q.unit ? " " + q.unit : "");
    if (kind === "short") return (q.accept || [])[0] || "";
    return "";
  }
  function respText(q, resp) {
    if (resp == null) return "(no answer)";
    if (typeOf(q) === "mc") return letter(q.order.indexOf(resp)) + ") " + plain(q.opts[resp]);
    return resp + (typeOf(q) === "number" && q.unit ? " " + q.unit : "");
  }

  /* ---------- 3. submit ---------- */
  paper.addEventListener("submit", e => {
    e.preventDefault();
    const blanks = qs.map((q, i) => responseOf(q, i) == null ? i + 1 : 0).filter(Boolean);
    if (blanks.length && !confirm("You haven’t answered question" + (blanks.length > 1 ? "s " : " ") +
        blanks.join(", ") + ". Submit anyway?")) return;

    const finishedAt = new Date();
    const mins = Math.max(1, Math.round((finishedAt - startedAt) / 60000));
    let got = 0;
    const lines = [];
    qs.forEach((q, i) => {
      const resp = responseOf(q, i);
      const m = mark(q, resp);
      const out = marksOf(q);
      const kind = typeOf(q);
      if (m != null) got += m;

      /* lock the paper and show per-question feedback if allowed */
      q.card.disabled = true;
      const tag = q.card.querySelector(".test-mark");
      if (kind === "written") {
        tag.textContent = "Marked by your teacher";
        tag.className = "test-mark pending";
      } else if (T.reveal !== "score") {
        tag.textContent = (m === out ? "✓ " : "✗ ") + m + " / " + out +
          (T.reveal === "answers" && m !== out ? "  —  answer: " + keyText(q) : "");
        tag.className = "test-mark " + (m === out ? "right" : "wrong");
      }

      const head = "Q" + (i + 1) + " " + (kind === "written" ? "[to mark, " + out + "]"
                     : (m === out ? "✓" : "✗") + " " + m + "/" + out);
      if (kind === "written") {
        lines.push(head + "\n" + plain(q.q) + "\n> " + respText(q, resp).replace(/\n/g, "\n> "));
      } else {
        lines.push(head + "  " + respText(q, resp) +
          (m !== out && T.reveal === "answers" ? "   [key: " + keyText(q) + "]" : ""));
      }
    });
    inProgress = false;
    submitRow.hidden = true;

    const scoreLine = "Auto-marked: " + got + " / " + autoTotal +
      (writtenTotal ? "  (+ " + writtenTotal + " marks of written answers to mark)" : "");
    const body =
      (T.subject ? T.subject + " — " : "") + (T.title || "Test") + "\n" +
      "Student: " + student.name + " <" + student.email + ">\n" +
      "Started: " + fmtTime(startedAt) + "\n" +
      "Submitted: " + fmtTime(finishedAt) + " (" + mins + " min)\n" +
      scoreLine + "\n\n" + lines.join("\n\n") + "\n";
    const subject = (T.title || "Test") + " — " + student.name + " — " + got + "/" + autoTotal;

    showResults(got, body, subject);
  });

  /* ---------- 4. results + email ---------- */
  function mailtoFor(body, subject) {
    const base = "mailto:" + encodeURIComponent(student.teacher) +
      "?cc=" + encodeURIComponent(student.email) +
      "&subject=" + encodeURIComponent(subject) + "&body=";
    const full = base + encodeURIComponent(body);
    if (full.length <= MAILTO_LIMIT) return { href: full, short: false };
    const stub = "My full results are copied to the clipboard — paste them here (Ctrl+V / Cmd+V) before sending.\n\n";
    return { href: base + encodeURIComponent(stub + body.split("\n\n")[0] + "\n"), short: true };
  }
  function copy(text) {
    if (navigator.clipboard && navigator.clipboard.writeText) return navigator.clipboard.writeText(text);
    const ta = document.createElement("textarea");
    ta.value = text; document.body.appendChild(ta); ta.select();
    try { document.execCommand("copy"); } finally { ta.remove(); }
    return Promise.resolve();
  }

  function showResults(got, body, subject) {
    const mail = mailtoFor(body, subject);
    const res = el("section", "test-results");
    res.innerHTML =
      '<div class="score-ring"><div class="score-num">' + got + '</div>' +
      '<div class="score-denom">out of ' + autoTotal + "</div></div>" +
      (writtenTotal ? '<p class="result-sub">Plus ' + writtenTotal +
        " marks of written answers for your teacher to mark.</p>" : "") +
      '<p class="result-msg">Now send it to your teacher</p>' +
      '<p class="result-sub">Your email app should have opened with your results. ' +
      (mail.short ? "Your results are long, so they’ve been copied — <strong>paste them into the email</strong>, then " : "") +
      "Press <strong>Send</strong>. Your test isn’t handed in until you do.</p>" +
      '<div class="result-btns"><a class="btn-primary test-btn" href="' + mail.href + '">&#9993; Open email again</a>' +
      '<button class="btn-secondary" type="button" data-copy>Copy results</button></div>' +
      '<details class="test-fallback"><summary>Email app didn’t open?</summary>' +
      "<p>Copy your results, open your school email in the browser, and send them to <strong>" +
      esc(student.teacher) + "</strong> with the subject <em>" + esc(subject) + "</em>.</p>" +
      '<textarea class="test-input" readonly rows="10"></textarea></details>';
    res.querySelector("textarea").value = body;
    const btn = res.querySelector("[data-copy]");
    btn.addEventListener("click", () => copy(body).then(() => {
      btn.textContent = "Copied ✓";
      setTimeout(() => { btn.textContent = "Copy results"; }, 2000);
    }));
    app.insertBefore(res, paper);
    window.scrollTo(0, 0);

    if (mail.short) copy(body).catch(() => {});
    window.location.href = mail.href;            /* still inside the Submit click */
  }
})();
