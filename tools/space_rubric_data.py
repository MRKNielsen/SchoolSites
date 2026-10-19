# Data blocks for the Year 7 Space CAT 5 marking rubric.
# Spliced into a copy of the bio-ecosystems rubric engine by build_space_rubric.py.
#
# Strands are by unit topic (one per lesson taught), because the tool's job is
# forming reteaching groups. Weights are the actual CAT 5 marks for the
# questions behind each strand, so the overall level is weighted exactly as the
# paper is: 9 + 12 + 11 + 12 + 3 + 3 = 50.
#
# Every strand carries a complete band ladder up to its own maxBand — the
# engine's topCell() walks down from maxBand and missedBelow() penalises gaps,
# so a strand with a hole in the middle silently under-awards.

STRANDS = r'''[
{
  id:"s1", maxBand:4, weight:9,
  name:"Describes the structure and scale of the Earth–Moon–Sun system",
  sub:"Q1, Q6, Q10",
  start:"label the layers of Earth and the Sun on a diagram, working from the outside in",
  bands:[
    {q:"Q1 Earth", d:"Labels the crust and the mantle on the Earth diagram."},
    {q:"Q1 Sun + Q6a", d:"Labels all four remaining layers of the Sun, and finds how many times wider Earth is than the Moon."},
    {q:"Q6b", d:"Calculates the time sunlight takes to reach Earth, showing the working."},
    {q:"Q10", d:"Explains the Moon’s 300° temperature range from what the Moon lacks."}
  ],
  can:[
    "label the crust and mantle on a cross-section of Earth",
    "label all six layers of the Sun and compare the sizes of Earth and the Moon",
    "calculate how long sunlight takes to reach Earth, setting the working out clearly",
    "explain the Moon’s huge temperature range by reasoning from its lack of atmosphere and its month-long day"
  ],
  next:[
    "learn the Sun’s layers in order from the core outwards, then label them without the word list",
    "set calculations out as a formula, then the numbers, then the answer with its unit",
    "practise turning a comparison into an explanation — say what is missing and what that causes",
    "apply the same reasoning to another airless body, such as Mercury, and predict its temperature range"
  ]
},
{
  id:"s2", maxBand:4, weight:12,
  name:"Explains day, night and the seasons from Earth’s rotation and tilt",
  sub:"Q2, Q3, Q11",
  start:"read a day–night diagram: the half facing the Sun is lit, the other half is in darkness",
  bands:[
    {q:"Q2a, Q2c, Q3c", d:"Reads daylight and darkness off a diagram, and states the rotation period, the orbital period and the tilt angle."},
    {q:"Q2b, Q3a", d:"Uses the direction of the tilt to work out which hemisphere is in summer, and locates Melbourne’s winter on an orbit diagram."},
    {q:"Q3b, Q3d, Q11a", d:"Locates Melbourne’s autumn, rejects the “closest to the Sun” explanation, and draws a labelled diagram of the tilt at two points in the orbit."},
    {q:"Q11b", d:"Explains January and July using the tilt, referring to their own diagram."}
  ],
  can:[
    "read day and night off a diagram and recall the rotation period, the orbital period and the 23.5° tilt",
    "use the direction of the tilt to decide which hemisphere is having summer",
    "place all four seasons on an orbit diagram and reject the idea that distance from the Sun causes them",
    "explain the difference between January and July in Australia using a diagram {their} own work refers to"
  ],
  next:[
    "practise reading the tilt: find which end of the axis leans towards the Sun, and that hemisphere has summer",
    "work right around an orbit diagram naming all four seasons, not just summer and winter",
    "write the explanation out as well as drawing it — say what the tilt does to the angle and the hours of sunlight",
    "extend the explanation to the equator and the poles, where the same tilt gives a very different result"
  ]
},
{
  id:"s3", maxBand:4, weight:11,
  name:"Models the Moon’s phases and the tides from Earth–Moon–Sun geometry",
  sub:"Q4, Q5",
  start:"recall that the Moon reflects sunlight and takes about a month to orbit Earth",
  bands:[
    {q:"Q4a, Q4e", d:"States the Moon’s orbital period and explains that we see reflected sunlight."},
    {q:"Q4b, Q4c, Q5a", d:"Names the phase at a given orbital position, picks the matching Melbourne view, and identifies spring tides at the aligned position."},
    {q:"Q5b, Q5c", d:"Attributes two high tides a day to Earth’s rotation, and states what raises the bulge on the near side."},
    {q:"Q4d", d:"Works backwards from a pictured phase to the Moon’s position in its orbit, and names the phase in full."}
  ],
  can:[
    "state how long the Moon takes to orbit Earth and explain that moonlight is reflected sunlight",
    "go from a position in the Moon’s orbit to the phase we see, and draw it as it looks from Melbourne",
    "explain why there are two high tides a day and what causes the bulge nearest the Moon",
    "reverse the reasoning — start from a picture of the Moon and work out where it must be in its orbit"
  ],
  next:[
    "learn the eight phases in order, then match each one to a position in the orbit",
    "remember that from Melbourne a waxing Moon is lit on the left — the opposite of most textbook diagrams",
    "separate the two causes: the Moon raises the bulges, Earth’s spin carries us through them",
    "practise the reverse direction: given a phase, say where the Moon is and roughly how many days into the cycle"
  ]
},
{
  id:"s4", maxBand:4, weight:12,
  name:"Describes the solar system and works with astronomical units",
  sub:"Q7",
  start:"learn the eight planets in order outwards from the Sun",
  bands:[
    {q:"Q7a, Q7b", d:"Lists the eight planets in order from the Sun and names two gas giants."},
    {q:"Q7c (i), Q7d (i)", d:"Locates the asteroid belt between Mars and Jupiter, and states how many times farther from the Sun Uranus is than Earth."},
    {q:"Q7c (ii)", d:"Explains why the asteroid belt never formed into a planet."},
    {q:"Q7d (ii)", d:"Converts a distance in astronomical units into kilometres, showing the working."}
  ],
  can:[
    "name the eight planets in order and pick out the gas giants",
    "say where the asteroid belt sits and read a distance in astronomical units",
    "explain why the asteroid belt never became a planet",
    "convert astronomical units into kilometres and set the working out clearly"
  ],
  next:[
    "use a mnemonic for the order, then check it against the AU column in the booklet table",
    "learn what 1 AU means — the Earth–Sun distance — and use it to compare any two planets",
    "name the cause, not just the effect: it is Jupiter’s gravity that kept the material stirred up",
    "practise multiplying by 1.5 × 10⁸ km and writing the answer in a sensible form"
  ]
},
{
  id:"s5", maxBand:3, weight:3,
  name:"Recognises First Nations astronomy as science",
  sub:"Q8",
  start:"recall that dark constellations are made from the dark dust lanes between the stars",
  bands:[
    {q:"Q8a", d:"Contrasts dark constellations with western constellations."},
    {q:"Q8b part", d:"Names the season signalled by the Emu’s position at dusk."},
    {q:"Q8b part", d:"Links that position to what the emus are doing, as an ecological calendar."}
  ],
  can:[
    "explain that dark constellations are shapes made from the dust lanes, not from joining stars",
    "say what season the Emu in the Sky signals when its head sits near the horizon at dusk",
    "explain how the Emu works as a calendar by linking its position to the emus’ breeding season"
  ],
  next:[
    "put the two systems side by side — one joins bright points, the other reads the dark shapes between them",
    "learn how the Emu’s orientation changes through the year, not just where it is in autumn",
    "state the test that makes it science: the signal can be checked against what the animals actually do"
  ]
},
{
  id:"s6", maxBand:3, weight:3,
  name:"Evaluates the sustainability of our use of space",
  sub:"Q9",
  start:"recall what counts as space debris — dead satellites, spent rocket stages, fragments and lost equipment",
  bands:[
    {q:"Q9a", d:"Identifies what counts as space debris."},
    {q:"Q9b part", d:"Gives one reason a 1 cm fragment is dangerous to a spacecraft."},
    {q:"Q9b part", d:"Gives a second, genuinely different reason."}
  ],
  can:[
    "say what space debris is and give examples",
    "explain why even a tiny fragment is dangerous to a spacecraft",
    "give two separate reasons, rather than the same reason twice"
  ],
  next:[
    "learn the four kinds of debris so the examples come quickly",
    "bring the speed into the answer — about 7.8 km/s is what makes a 1 cm fragment dangerous",
    "check that {their} two reasons really differ: speed and energy are one reason, not two — the number of fragments, or the fact they cannot be tracked, is a second"
  ]
}
]'''

# ---------------------------------------------------------------- criteria
# One tickable row per observable. band must exist for every level up to the
# strand's maxBand, or that strand can never award the levels above the hole.
#
# `q` is the question number ALONE and `sub` is the sub-part, because the mark
# grid groups columns by `q` into a "Q1 ... Q11" header row with the sub-parts
# beneath. Putting the sub-part in `q` (as "Q2a") splits that header into one
# cell per criterion and the row stops reading like the paper.
#
# `sub` shows in a 30px column, so keep it to three characters; the full label
# is in the cell's tooltip and in the Rubric reference tab. Where two criteria
# come from one sub-part they take a digit (a1/a2, b1/b2).
#
# Rows are listed in PAPER order, which also puts the CSV export in paper
# order so it matches the grid. Nothing depends on this order: the band logic
# groups by strand (EV/EVALL), and the reference tab and printed rubric filter
# by part. MARK_COLS re-sorts into paper order anyway, so the grid stays right
# even if these rows are later regrouped.
CRITERIA = r'''[
 {id:"Q1a",   q:"Q1",  sub:"ear", part:"A", label:"Labels the crust and the mantle",                            strand:"s1", band:1},
 {id:"Q1b",   q:"Q1",  sub:"sun", part:"A", label:"Labels the Sun’s four unlabelled layers",                     strand:"s1", band:2},
 {id:"Q2a",   q:"Q2",  sub:"a",   part:"B", label:"Reads daylight and darkness off the diagram",                strand:"s2", band:1},
 {id:"Q2b",   q:"Q2",  sub:"b",   part:"B", label:"Uses the tilt to say which country is in summer",            strand:"s2", band:2},
 {id:"Q2c",   q:"Q2",  sub:"c",   part:"B", label:"States the time for one rotation on the axis",               strand:"s2", band:1},
 {id:"Q3a",   q:"Q3",  sub:"a1",  part:"B", label:"Locates Melbourne’s winter on the orbit",                     strand:"s2", band:2},
 {id:"Q3b",   q:"Q3",  sub:"a2",  part:"B", label:"Locates Melbourne’s autumn on the orbit",                     strand:"s2", band:3},
 {id:"Q3c",   q:"Q3",  sub:"bc",  part:"B", label:"States the orbital period and the tilt angle",               strand:"s2", band:1},
 {id:"Q3d",   q:"Q3",  sub:"d",   part:"B", label:"Rejects the “closest to the Sun” explanation",                strand:"s2", band:3},
 {id:"Q4a",   q:"Q4",  sub:"a",   part:"C", label:"States the Moon’s orbital period",                            strand:"s3", band:1},
 {id:"Q4b",   q:"Q4",  sub:"b",   part:"C", label:"Phase at position X, and its Melbourne view",                strand:"s3", band:2},
 {id:"Q4c",   q:"Q4",  sub:"c",   part:"C", label:"Phase at position Y, and its Melbourne view",                strand:"s3", band:2},
 {id:"Q4d",   q:"Q4",  sub:"d",   part:"C", label:"Works back from a pictured phase to its orbital position",   strand:"s3", band:4},
 {id:"Q4e",   q:"Q4",  sub:"e",   part:"C", label:"Explains that we see reflected sunlight",                    strand:"s3", band:1},
 {id:"Q5a",   q:"Q5",  sub:"a",   part:"C", label:"Identifies spring tides at the aligned position",            strand:"s3", band:2},
 {id:"Q5b",   q:"Q5",  sub:"b",   part:"C", label:"Two high tides a day come from Earth’s rotation",            strand:"s3", band:3},
 {id:"Q5c",   q:"Q5",  sub:"c",   part:"C", label:"States what raises the near-side tidal bulge",               strand:"s3", band:3},
 {id:"Q6a",   q:"Q6",  sub:"a",   part:"A", label:"Finds how many times wider Earth is than the Moon",          strand:"s1", band:2},
 {id:"Q6b",   q:"Q6",  sub:"b",   part:"A", label:"Calculates the light travel time from the Sun, with working",strand:"s1", band:3},
 {id:"Q7a",   q:"Q7",  sub:"a",   part:"D", label:"Lists the eight planets in order from the Sun",              strand:"s4", band:1},
 {id:"Q7b",   q:"Q7",  sub:"b",   part:"D", label:"Names two gas giants",                                       strand:"s4", band:1},
 {id:"Q7ci",  q:"Q7",  sub:"ci",  part:"D", label:"Locates the asteroid belt",                                  strand:"s4", band:2},
 {id:"Q7cii", q:"Q7",  sub:"cii", part:"D", label:"Explains why the belt never formed a planet",                strand:"s4", band:3},
 {id:"Q7di",  q:"Q7",  sub:"di",  part:"D", label:"States how many times farther out Uranus is",                strand:"s4", band:2},
 {id:"Q7dii", q:"Q7",  sub:"dii", part:"D", label:"Converts AU to kilometres, with working",                    strand:"s4", band:4},
 {id:"Q8a",   q:"Q8",  sub:"a",   part:"E", label:"Contrasts dark and western constellations",                  strand:"s5", band:1},
 {id:"Q8bi",  q:"Q8",  sub:"b1",  part:"E", label:"Names the season the Emu’s position signals",                 strand:"s5", band:2},
 {id:"Q8bii", q:"Q8",  sub:"b2",  part:"E", label:"Links it to the emus’ breeding cycle",                       strand:"s5", band:3},
 {id:"Q9a",   q:"Q9",  sub:"a",   part:"E", label:"Identifies what counts as space debris",                     strand:"s6", band:1},
 {id:"Q9bi",  q:"Q9",  sub:"b1",  part:"E", label:"One reason a 1 cm fragment is dangerous",                    strand:"s6", band:2},
 {id:"Q9bii", q:"Q9",  sub:"b2",  part:"E", label:"A second, genuinely different reason",                       strand:"s6", band:3},
 {id:"Q10",   q:"Q10", sub:"",    part:"A", label:"Explains the Moon’s 300° temperature range",                  strand:"s1", band:4},
 {id:"Q11a",  q:"Q11", sub:"dia", part:"B", label:"Draws a labelled diagram of the tilt at two orbital points", strand:"s2", band:3},
 {id:"Q11b",  q:"Q11", sub:"exp", part:"B", label:"Explains January and July, referring to the diagram",        strand:"s2", band:4}
]'''

PARTS = r'''[
  {id:"A", name:"Part A · Earth, Moon and Sun"},
  {id:"B", name:"Part B · Day, night and seasons"},
  {id:"C", name:"Part C · Moon phases and tides"},
  {id:"D", name:"Part D · The solar system"},
  {id:"E", name:"Part E · Science in society"}
]'''
