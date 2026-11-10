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
  { deck: 1, q: "Something you can observe or measure about a material is called a…", opts: ["state", "property", "mixture", "model"], ans: 1 },

  /* ── LESSON 2: What is a Scientific Model? ──────────────────────────── */
  { deck: 2, q: "Something you notice with your senses or measure with an instrument is…", opts: ["an inference", "an observation", "a prediction", "a theory"], ans: 1 },
  { deck: 2, q: "Which of these is an inference?", opts: ["The grass is wet", "The box has a mass of 450 g", "It rained last night", "The thermometer reads 31 °C"], ans: 2 },
  { deck: 2, q: "Which of these is an observation?", opts: ["The dog is happy", "The milk smells sour", "The milk has gone off", "There is a book in the box"], ans: 1 },
  { deck: 2, q: "A scientific model is…", opts: ["an exact copy of the real thing", "a simpler version that helps us explain or predict", "a guess with no evidence", "always a physical object"], ans: 1 },
  { deck: 2, q: "A weather forecast is an example of which kind of model?", opts: ["Physical", "Diagram", "Mathematical or computer", "It is not a model"], ans: 2 },
  { deck: 2, q: "A globe is a good model of the Earth's shape. What does it leave out?", opts: ["That the Earth is round", "Where the continents are", "The Earth's real size", "Where the oceans are"], ans: 2 },
  { deck: 2, q: "A statement of what should happen if a model is right is a…", opts: ["prediction", "observation", "method", "conclusion"], ans: 0 },
  { deck: 2, q: "What should scientists do when new evidence doesn't fit their model?", opts: ["Ignore the evidence", "Change the model", "Stop doing science", "Keep the model anyway"], ans: 1 },
  { deck: 2, q: "Aristotle saw that the Earth's shadow on the Moon is always curved. This was evidence that the Earth is…", opts: ["flat", "a sphere", "very small", "moving"], ans: 1 },
  { deck: 2, q: "A sealed box rattles loudly and many small things seem to slide together when it's tilted. The best inference is…", opts: ["one large ball", "many small, hard objects", "nothing — it's empty", "a liquid"], ans: 1 },
  { deck: 2, q: "A model that has been tested many times and explains a huge range of evidence is called a…", opts: ["guess", "theory", "observation", "method"], ans: 1 },
  { deck: 2, q: "Democritus called the tiny pieces that make up everything atomos. What does the word mean?", opts: ["Invisible", "Uncuttable", "Moving", "Small"], ans: 1 },

  /* ── LESSON 3: Experiment 1 — Matter Has Mass and Takes Up Space ─────── */
  { deck: 3, q: "To tare a balance means to…", opts: ["clean the pan", "set it to zero with the empty container on it", "weigh something twice", "turn it off"], ans: 1 },
  { deck: 3, q: "An empty beaker is 52.40 g. With salt it is 67.15 g. What is the mass of the salt?", opts: ["14.75 g", "15.25 g", "119.55 g", "67.15 g"], ans: 0 },
  { deck: 3, q: "The curved surface of water in a measuring cylinder is called the…", opts: ["meniscus", "scale", "tare", "division"], ans: 0 },
  { deck: 3, q: "Where should your eye be when you read a measuring cylinder?", opts: ["Above the cylinder", "Level with the liquid surface", "Below the bench", "It doesn't matter"], ans: 1 },
  { deck: 3, q: "Which part of the meniscus do you read for water?", opts: ["The top of the curve", "The bottom of the curve", "The middle of the glass", "The highest mark"], ans: 1 },
  { deck: 3, q: "On a 100 mL cylinder with a small mark halfway between each 10 mL, one small division is worth…", opts: ["1 mL", "2 mL", "5 mL", "10 mL"], ans: 2 },
  { deck: 3, q: "A ball gets heavier when more air is pumped into it. This shows that air…", opts: ["has mass", "has no mass", "is a liquid", "keeps its own shape"], ans: 0 },
  { deck: 3, q: "An upside-down cup is pushed straight down into water, and the paper towel inside stays dry. Why?", opts: ["The towel is waterproof", "Trapped air takes up the space", "Water can't go into cups", "The water is too cold"], ans: 1 },
  { deck: 3, q: "What an experiment is trying to find out is its…", opts: ["method", "aim", "result", "equipment"], ans: 1 },
  { deck: 3, q: "Why repeat a test three times?", opts: ["To make it take longer", "To check the results are reliable", "Because the first one is always wrong", "To use more equipment"], ans: 1 },
  { deck: 3, q: "A ball goes from 410.50 g to 413.10 g after pumping. What mass of air was added?", opts: ["2.60 g", "3.60 g", "26.0 g", "823.60 g"], ans: 0 },
  { deck: 3, q: "Galileo's container got lighter when he let extra air out. This showed that…", opts: ["air has mass", "air has no mass", "containers lose mass over time", "air is a solid"], ans: 0 },

  /* ── LESSON 4: The Particle Model ────────────────────────────────────── */
  { deck: 4, q: "Which is NOT one of the four ideas of the particle model?", opts: ["Matter is made of tiny particles", "Particles are always moving", "Particles get bigger when heated", "There is empty space between particles"], ans: 2 },
  { deck: 4, q: "What is between the particles of a substance?", opts: ["Air", "Water", "Empty space", "Smaller particles"], ans: 2 },
  { deck: 4, q: "In a solid, the particles…", opts: ["move fast in all directions", "slide past each other", "vibrate in fixed places", "don't move at all"], ans: 2 },
  { deck: 4, q: "In a liquid, the particles are…", opts: ["far apart with no pattern", "close together with no pattern", "close together in a regular pattern", "not moving"], ans: 1 },
  { deck: 4, q: "In a gas, the particles are…", opts: ["far apart, moving fast in random directions", "close together, sliding past each other", "packed in a pattern", "touching but still"], ans: 0 },
  { deck: 4, q: "In which state is the attraction between particles strongest?", opts: ["Solid", "Liquid", "Gas", "It is the same in all three"], ans: 0 },
  { deck: 4, q: "A gas can be compressed because…", opts: ["its particles shrink", "there is lots of empty space between its particles", "its particles are touching", "its particles stop moving"], ans: 1 },
  { deck: 4, q: "A liquid flows because its particles…", opts: ["are far apart", "are held in fixed places", "can slide past each other", "are very small"], ans: 2 },
  { deck: 4, q: "To vibrate means to…", opts: ["move in a straight line", "jiggle backwards and forwards on the spot", "stop moving", "get bigger"], ans: 1 },
  { deck: 4, q: "In a particle diagram, the particles of one substance should be…", opts: ["different sizes in each state", "the same size in every state", "bigger in a gas", "smaller in a solid"], ans: 1 },
  { deck: 4, q: "Water can hardly be squashed because its particles…", opts: ["are far apart", "are close together with almost no space", "don't attract each other", "are moving too fast"], ans: 1 },
  { deck: 4, q: "A pull between particles that holds them together is called…", opts: ["attraction", "vibration", "pressure", "arrangement"], ans: 0 },

  /* ── LESSON 5: Particles Are Always Moving ───────────────────────────── */
  { deck: 5, q: "Kinetic energy is…", opts: ["stored energy", "the energy something has because it is moving", "heat in a solid", "the energy of light"], ans: 1 },
  { deck: 5, q: "When a substance is heated, its particles…", opts: ["get bigger", "move faster", "stop moving", "move more slowly"], ans: 1 },
  { deck: 5, q: "When a substance is cooled, its particles…", opts: ["stop moving completely", "move more slowly", "get smaller", "move faster"], ans: 1 },
  { deck: 5, q: "Temperature is a measure of…", opts: ["how big the particles are", "how fast the particles are moving on average", "how many particles there are", "how heavy a substance is"], ans: 1 },
  { deck: 5, q: "The particles in a block of ice are…", opts: ["not moving at all", "still vibrating", "moving fast in all directions", "melting"], ans: 1 },
  { deck: 5, q: "Who first saw tiny grains jiggling in water through a microscope, in 1827?", opts: ["Albert Einstein", "Robert Brown", "Galileo Galilei", "Democritus"], ans: 1 },
  { deck: 5, q: "What makes a grain jiggle in Brownian motion?", opts: ["The grain is alive", "Moving water particles hit it unevenly from every side", "Light pushes it", "The microscope shakes"], ans: 1 },
  { deck: 5, q: "Why does a grain in Brownian motion move in a zigzag?", opts: ["It is pulled by gravity", "The side hit hardest keeps changing", "It is following a current", "It is spinning"], ans: 1 },
  { deck: 5, q: "When the water is warmed, grains in Brownian motion jiggle…", opts: ["more slowly", "faster", "the same", "not at all"], ans: 1 },
  { deck: 5, q: "A smell spreads across a room because…", opts: ["smell particles are knocked about by moving air particles and spread out", "smell particles are pulled towards noses", "air particles stand still", "the smell is a type of light"], ans: 0 },
  { deck: 5, q: "Hot tea and cold tea are made of…", opts: ["different particles", "the same particles, moving at different speeds", "particles of different sizes", "heat particles and water particles"], ans: 1 },
  { deck: 5, q: "To crash into something is to…", opts: ["vibrate", "collide", "attract", "compress"], ans: 1 },

  /* ── LESSON 6: The Limits of the Model ───────────────────────────────── */
  { deck: 6, q: "An idea that many people believe but that is not correct is a…", opts: ["theory", "misconception", "prediction", "limitation"], ans: 1 },
  { deck: 6, q: "When ice melts, its particles…", opts: ["melt", "stay the same, but their arrangement and movement change", "get bigger", "turn into different particles"], ans: 1 },
  { deck: 6, q: "When a metal rod gets longer as it is heated, its particles…", opts: ["get bigger", "move further apart", "melt", "stop vibrating"], ans: 1 },
  { deck: 6, q: "A single particle of copper is…", opts: ["orange", "shiny", "not coloured", "hot"], ans: 2 },
  { deck: 6, q: "Which statement is TRUE?", opts: ["There is air between water particles", "Particles in a solid don't move", "Liquid particles are close together", "Particles get bigger when heated"], ans: 2 },
  { deck: 6, q: "Which is a rule for drawing particle diagrams?", opts: ["Draw gas particles bigger", "Particles of one substance are the same size in every state", "Leave gaps between liquid particles", "Draw solid particles with no pattern"], ans: 1 },
  { deck: 6, q: "A diagram of liquid water shows the particles far apart with big gaps. What is wrong?", opts: ["Nothing", "Liquid particles should be touching", "The particles should be bigger", "They should be in rows"], ans: 1 },
  { deck: 6, q: "Something a model can't show, or doesn't show accurately, is a…", opts: ["limitation", "property", "substance", "prediction"], ans: 0 },
  { deck: 6, q: "Which is a limitation of particle diagrams?", opts: ["They show the arrangement of particles", "They are flat and not to scale", "They show three states", "They use circles"], ans: 1 },
  { deck: 6, q: "Why can't a single particle of water be wet?", opts: ["It is too cold", "Wetness belongs to huge numbers of particles together", "It is a gas", "It has no mass"], ans: 1 },
  { deck: 6, q: "Rewrite correctly: 'The chocolate went hard because its particles froze.'", opts: ["The particles got smaller", "The particles lost energy, slowed down and became held in fixed places", "The particles turned into ice", "The particles stopped existing"], ans: 1 },
  { deck: 6, q: "How does the size of a drawing compare with the real thing? This is its…", opts: ["scale", "substance", "attraction", "mass"], ans: 0 }
];
