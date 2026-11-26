/* Demo question file for tools/test-demo.html — see assets/js/test.js for the format. */
window.TEST = {
  title: "Forces — Quick Check",
  subject: "Year 7 Science",
  backHref: "../index.html",
  /* Uncomment to give students a dropdown instead of typing the address:
  teachers: [
    { name: "Mr Nielsen", email: "your.name@school.example" }
  ],
  */
  teacherDomain: "",   // e.g. "education.vic.gov.au"
  studentDomain: "",
  reveal: "marks",     // "score" | "marks" | "answers"
  shuffleQuestions: false,
  shuffleOptions: true,
  clearOnLeave: true,  // leaving the page wipes answers (the count is emailed either way)
  questions: [
    { q: "A force is best described as…",
      opts: ["a push or a pull", "a type of energy", "the speed of an object", "the mass of an object"],
      ans: 0 },
    { q: "Which force slows a bike down when you stop pedalling on flat ground?",
      opts: ["Gravity", "Friction", "Magnetism", "Buoyancy"], ans: 1 },
    { type: "short", q: "What is the SI unit of force?", accept: ["newton", "newtons", "N"] },
    { type: "number", q: "A 2&nbsp;kg mass has a weight of about how many newtons on Earth? (use <em>g</em> = 9.8&nbsp;N/kg)",
      ans: 19.6, tol: 0.2, unit: "N", marks: 2 },
    { type: "written", q: "Explain why a heavy box is harder to start moving than to keep moving.",
      marks: 3, lines: 5 }
  ]
};
