/* ============================================================
   The Particle Model — Year 7 Spaced Retrieval Question Bank
   Format: { deck: N, q: "question text", opts: ["A","B","C","D"], ans: 0-indexed-int }
   Deck 0 is Lesson 1's warm-up on primary-school ideas (states of
   matter and mixtures from Levels 5–6), so every later deck excludes it
   with data-quiz-exclude="0", as Year 7 Forces does. Later decks draw
   3 questions from the lesson before and 2 from older lessons
   (data-quiz-recent="3"). Content follows the Lesson Booklet.
   Add a lesson's questions here when its deck is built.
   ============================================================ */
window.RETRIEVAL_QUESTIONS = [

  /* ── LESSON 1 WARM-UP: what do you already know? (primary-school ideas) ─── */
  { deck: 0, q: "Which of these is a liquid at room temperature?", opts: ["Ice", "Milk", "Steam", "Sand"], ans: 1 },
  { deck: 0, q: "What happens to ice when it is left in a warm room?", opts: ["It melts into water", "It turns straight into a gas", "It gets heavier", "Nothing happens"], ans: 0 },
  { deck: 0, q: "Water turning into water vapour is called…", opts: ["melting", "freezing", "condensing", "evaporating"], ans: 3 },
  { deck: 0, q: "Drops of water form on the outside of a cold glass. This is called…", opts: ["melting", "condensation", "dissolving", "evaporation"], ans: 1 },
  { deck: 0, q: "Which of these is a gas?", opts: ["Honey", "A rock", "The air in a balloon", "Butter"], ans: 2 },
  { deck: 0, q: "Sugar stirred into water seems to disappear. What has it done?", opts: ["Melted", "Evaporated", "Dissolved", "Frozen"], ans: 2 },
  { deck: 0, q: "Which of these is a mixture?", opts: ["Pure water", "A fruit salad", "A gold ring", "Oxygen gas"], ans: 1 },
  { deck: 0, q: "Which is the best way to get sand out of water?", opts: ["Stir it", "Pour it through filter paper", "Freeze it", "Add more water"], ans: 1 },
  { deck: 0, q: "What happens to most materials when they are heated?", opts: ["They shrink", "They get heavier", "They expand a little", "They change colour"], ans: 2 },
  { deck: 0, q: "Water freezes at…", opts: ["0 °C", "10 °C", "50 °C", "100 °C"], ans: 0 },
  { deck: 0, q: "Water boils at…", opts: ["0 °C", "37 °C", "50 °C", "100 °C"], ans: 3 },
  { deck: 0, q: "A puddle dries up on a sunny day. Where has the water gone?", opts: ["It has soaked into nothing", "Into the air as water vapour", "It has turned into ice", "It has been destroyed"], ans: 1 },

  /* ── LESSON 1: States of Matter ─────────────────────────────────────── */
  { deck: 1, q: "Something is matter if it…", opts: ["can be seen", "has mass and takes up space", "is a solid", "gives off energy"], ans: 1 },
  { deck: 1, q: "Which of these is NOT matter?", opts: ["Air", "Water", "Light", "Sand"], ans: 2 },
  { deck: 1, q: "Which of these is matter?", opts: ["Sound", "Heat", "A shadow", "Helium in a balloon"], ans: 3 },
  { deck: 1, q: "Which state keeps its own shape and its own volume?", opts: ["Solid", "Liquid", "Gas", "All three"], ans: 0 },
  { deck: 1, q: "Which state keeps its volume but takes the shape of its container?", opts: ["Solid", "Liquid", "Gas", "None of them"], ans: 1 },
  { deck: 1, q: "Which state spreads out to fill its whole container?", opts: ["Solid", "Liquid", "Gas", "Solid and liquid"], ans: 2 },
  { deck: 1, q: "To compress something means to…", opts: ["heat it up", "squash it into a smaller volume", "pour it", "dissolve it"], ans: 1 },
  { deck: 1, q: "Which state can be compressed easily?", opts: ["Solid", "Liquid", "Gas", "None of them"], ans: 2 },
  { deck: 1, q: "The amount of space something takes up is its…", opts: ["mass", "weight", "volume", "state"], ans: 2 },
  { deck: 1, q: "250 mL of juice is poured into an empty 1 L jug. What volume of juice is in the jug?", opts: ["1 L", "250 mL", "500 mL", "It depends on the jug's shape"], ans: 1 },
  { deck: 1, q: "Sand pours, but scientists call it a solid. Why?", opts: ["Each grain keeps its own shape", "It is heavy", "It is found on beaches", "It can be compressed"], ans: 0 },
  { deck: 1, q: "Which is the best evidence that a material is a liquid?", opts: ["It looks wet", "It is see-through", "It flows and keeps the same volume in a new container", "It is cold"], ans: 2 },
  { deck: 1, q: "A sealed syringe of air is pushed from 50 mL to 30 mL. What does this show?", opts: ["Air has no mass", "Air can be compressed", "Air is a liquid", "Air keeps its own shape"], ans: 1 },
  { deck: 1, q: "Something you can observe or measure about a material is called a…", opts: ["state", "property", "mixture", "model"], ans: 1 }
];
