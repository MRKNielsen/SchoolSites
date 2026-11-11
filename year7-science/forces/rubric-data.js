/* Year 7 Forces & Motion — Trebuchet Investigation Test (Lesson 18) rubric.

   The rubric itself: strands, band descriptors, the questions that evidence
   each band, and the comment wording. The engine that reads it is shared —
   assets/js/rubric.js — and this page's shell is year7-science/forces/rubric.html.

   Built from the staff-only test paper and its marking key (7 Science/Forces/
   Trebuchet_Test, kept out of this repo): 14 questions, Section A /12,
   Section B /20, Section C /9 = 41. Section C questions sit only in band 4
   ("Above"); strands 2 and 4 have no above-level question, so they stop at
   band 3. Descriptors name the skill, never the answer.

   Everything between the outer braces is plain JSON, so the same text can be
   saved as a .json file and opened in tools/rubric-marker.html or
   tools/rubric-builder.html. Keep it JSON: double-quoted keys, no comments
   inside, no trailing commas.

   storageKey and save.version must not change while a class is mid-marking. */
window.RUBRIC = {
  "format": "rubric-marker/1",
  "id": "y7-forces-trebuchet-test",
  "version": 1,
  "title": "Trebuchet Investigation Test",
  "task": "Trebuchet Investigation Test",
  "context": "Year 7 Science · Forces & Motion",
  "eyebrow": "Year 7 Science · Open-booklet test",
  "subtitle": "rubric & report generator",
  "back": {
    "href": "index.html",
    "label": "Forces & Motion"
  },
  "theme": "science",
  "noun": {
    "task": "test",
    "item": "question"
  },
  "fileStem": "trebuchet-test",
  "storageKey": "trebuchet-test-rubric:v1",
  "columnOrder": "question",
  "total": 41,
  "pass": 0.5,
  "band0": "Not demonstrated",
  "bands": [
    "Towards expected standard",
    "At expected standard",
    "At expected standard",
    "Above expected standard"
  ],
  "save": {
    "version": 1
  },
  "demo": {
    "meta": {
      "cls": "7C",
      "teacher": "Mr K Nielsen",
      "date": "Term 4"
    },
    "students": [
      [
        "Ava Chen",
        "she",
        [
          3,
          3,
          4,
          3,
          3
        ]
      ],
      [
        "Ben Novak",
        "he",
        [
          2,
          2,
          2,
          2,
          2
        ]
      ],
      [
        "Charlie Doust",
        "they",
        [
          1,
          2,
          1,
          1,
          1
        ]
      ],
      [
        "Divya Rao",
        "she",
        [
          4,
          3,
          3,
          3,
          4
        ]
      ],
      [
        "Eli Marsh",
        "he",
        [
          2,
          1,
          3,
          2,
          3
        ]
      ],
      [
        "Frankie Hale",
        "they",
        [
          3,
          3,
          3,
          3,
          2
        ]
      ]
    ],
    "skip": {
      "Charlie Doust": [
        "Q11",
        "Q9b"
      ],
      "Eli Marsh": [
        "Q14"
      ]
    }
  },
  "parts": [
    {
      "id": "A",
      "name": "Section A · Your investigation"
    },
    {
      "id": "B",
      "name": "Section B · A new investigation"
    },
    {
      "id": "C",
      "name": "Section C · Going further (above level)"
    }
  ],
  "strands": [
    {
      "id": "s1",
      "code": "VC2S8U15",
      "maxBand": 4,
      "name": "Explains the launch with forces, levers and energy",
      "sub": "Q1a–c, Q11, Q13",
      "start": "name the energy store of a raised counterweight and the forces acting on a projectile once it is launched",
      "bands": [
        {
          "q": "Q1a, Q1b",
          "d": "Names the energy store of a raised counterweight and the forces acting on a projectile in flight."
        },
        {
          "q": "Q1c",
          "d": "Explains why a trebuchet’s arm is a Class 1 lever."
        },
        {
          "q": "Q11",
          "d": "Explains why a heavier projectile lands shorter, linking its mass to its launch speed or energy."
        },
        {
          "q": "Q13",
          "d": "Calculates and compares the kinetic energy of two projectiles, and accounts for the energy that did not reach the heavier one."
        }
      ],
      "can": [
        "name the energy store of a raised counterweight and the forces acting on a projectile in flight",
        "explain why a trebuchet’s arm is a Class 1 lever, with the pivot between the effort and the load",
        "explain why a heavier projectile lands shorter by linking its mass to its launch speed",
        "calculate the kinetic energy of a projectile and account for the energy that does not reach it"
      ],
      "next": [
        "practise placing the pivot, effort and load on lever diagrams and naming the class of each lever",
        "build explanations as a chain of linked ideas — same energy, more mass, less speed, shorter range",
        "use KE = ½mv² to put numbers on an explanation of how the counterweight’s energy is shared out",
        "investigate where the wasted energy goes in other machines, and how engineers reduce it"
      ],
      "weight": 10
    },
    {
      "id": "s2",
      "code": "VC2S8I02",
      "maxBand": 3,
      "name": "Identifies the variables in a fair test",
      "sub": "Q2, Q5",
      "start": "practise picking out what was changed and what was measured in a short description of an experiment",
      "bands": [
        {
          "q": "Q5a, Q5b",
          "d": "Identifies the independent and dependent variables in an investigation described to them."
        },
        {
          "q": "Q2 IV + DV",
          "d": "Names the independent and dependent variables in their own investigation, and says how each was changed or measured."
        },
        {
          "q": "Q2 CV, Q5c",
          "d": "Identifies a controlled variable and explains how it was kept the same."
        }
      ],
      "can": [
        "pick out the variable that was changed and the one that was measured in an investigation",
        "name the variables in {their} own investigation and describe how each was changed or measured",
        "identify a controlled variable and explain how it was kept the same"
      ],
      "next": [
        "describe how each variable is changed or measured, not just name it",
        "list the things that must stay the same in a fair test, and say how each one is kept the same",
        "plan a fair test of {their} own, writing the controlled variables into the method"
      ],
      "weight": 6
    },
    {
      "id": "s3",
      "code": "VC2S8I04",
      "maxBand": 4,
      "name": "Processes data: means, odd results and calculations",
      "sub": "Q6a, Q6c, Q7, Q12",
      "start": "practise calculating a mean: add the trials, then divide by how many there are",
      "bands": [
        {
          "q": "Q7a",
          "d": "Calculates the mean of three trials."
        },
        {
          "q": "Q6a, Q6c",
          "d": "Identifies an odd result and calculates the mean without it."
        },
        {
          "q": "Q7b, Q7c",
          "d": "Substitutes into v = ω × L to calculate the speed of the arm’s tip, with the unit."
        },
        {
          "q": "Q12",
          "d": "Calculates the gravitational potential energy, the kinetic energy and the efficiency of a launch."
        }
      ],
      "can": [
        "calculate the mean of repeated trials",
        "spot an odd result and leave it out of the mean",
        "use a formula to calculate a speed, showing the working and the unit",
        "calculate the energy going into and out of a launch, and its efficiency"
      ],
      "next": [
        "check each set of trials for a result that does not fit before working out the mean",
        "practise substituting into a formula: write it, put the numbers in, then give the answer with its unit",
        "convert grams to kilograms and use GPE = mgh and KE = ½mv² to compare the energy in and out",
        "use efficiency to compare two designs and suggest how to make a launch more efficient"
      ],
      "weight": 8
    },
    {
      "id": "s4",
      "code": "VC2S8I05",
      "maxBand": 3,
      "name": "Graphs data and describes patterns",
      "sub": "Q3, Q8–Q10",
      "start": "practise reading values from a results table and saying whether one goes up or down as the other changes",
      "bands": [
        {
          "q": "Q3, Q10a, Q10c",
          "d": "Reads results from a table and describes how one variable changed with another, using numbers."
        },
        {
          "q": "Q8 points + curve, Q10b",
          "d": "Plots data and draws a smooth curve of best fit, recognising when a pattern is a curve."
        },
        {
          "q": "Q8 odd result, Q9",
          "d": "Leaves the odd result out of the line of best fit and reads a prediction from it."
        }
      ],
      "can": [
        "describe how one variable changed as another changed, quoting numbers from a table",
        "plot data and draw a smooth curve of best fit",
        "use a line of best fit, drawn without the odd result, to make a prediction"
      ],
      "next": [
        "plot the data on a grid and draw a smooth line of best fit rather than joining the dots",
        "leave odd results out of the line of best fit, and use the line to read off a prediction",
        "explain why a prediction outside the tested range is less reliable than one inside it"
      ],
      "weight": 11
    },
    {
      "id": "s5",
      "code": "VC2S8I06",
      "maxBand": 4,
      "name": "Evaluates the method and its conclusions",
      "sub": "Q1d, Q4, Q6b, Q14",
      "start": "explain why scientists repeat each trial rather than relying on one result",
      "bands": [
        {
          "q": "Q1d",
          "d": "Gives the reason for repeating each trial."
        },
        {
          "q": "Q4a, Q6b",
          "d": "Identifies a specific source of error, and a likely cause of an odd result."
        },
        {
          "q": "Q4b",
          "d": "Suggests an improvement that reduces the error they identified."
        },
        {
          "q": "Q14",
          "d": "Judges whether a conclusion is justified, recognising that the data does not reach beyond the values tested."
        }
      ],
      "can": [
        "explain why each trial is repeated",
        "name specific sources of error, including what might cause an odd result",
        "suggest an improvement that reduces a specific error",
        "judge whether a conclusion goes further than the evidence supports"
      ],
      "next": [
        "name a specific source of error in an investigation, rather than “human error”",
        "for each source of error, suggest a change to the method that would reduce it",
        "check whether a conclusion stays inside the range of values that was actually tested",
        "design a follow-up test that would check a claim beyond the tested range"
      ],
      "weight": 6
    }
  ],
  "criteria": [
    {
      "id": "Q1a",
      "q": "Q1",
      "sub": "a",
      "part": "A",
      "label": "Names the energy store of a raised counterweight",
      "strand": "s1",
      "band": 1,
      "max": 1
    },
    {
      "id": "Q1b",
      "q": "Q1",
      "sub": "b",
      "part": "A",
      "label": "Names the forces on the projectile in flight",
      "strand": "s1",
      "band": 1,
      "max": 1
    },
    {
      "id": "Q1c",
      "q": "Q1",
      "sub": "c",
      "part": "A",
      "label": "Says why the arm is a Class 1 lever",
      "strand": "s1",
      "band": 2,
      "max": 1
    },
    {
      "id": "Q1d",
      "q": "Q1",
      "sub": "d",
      "part": "A",
      "label": "Gives the reason for three launches",
      "strand": "s5",
      "band": 1,
      "max": 1
    },
    {
      "id": "Q2iv",
      "q": "Q2",
      "sub": "iv",
      "part": "A",
      "label": "Independent variable and how it was changed",
      "strand": "s2",
      "band": 2,
      "max": 1
    },
    {
      "id": "Q2dv",
      "q": "Q2",
      "sub": "dv",
      "part": "A",
      "label": "Dependent variable and how it was measured",
      "strand": "s2",
      "band": 2,
      "max": 1
    },
    {
      "id": "Q2cv",
      "q": "Q2",
      "sub": "cv",
      "part": "A",
      "label": "A controlled variable and how it was kept the same",
      "strand": "s2",
      "band": 3,
      "max": 1
    },
    {
      "id": "Q3a",
      "q": "Q3",
      "sub": "a",
      "part": "A",
      "label": "Lightest counterweight and its mean range, from the booklet",
      "strand": "s4",
      "band": 1,
      "max": 1
    },
    {
      "id": "Q3b",
      "q": "Q3",
      "sub": "b",
      "part": "A",
      "label": "Heaviest counterweight and its mean range, from the booklet",
      "strand": "s4",
      "band": 1,
      "max": 1
    },
    {
      "id": "Q3c",
      "q": "Q3",
      "sub": "c",
      "part": "A",
      "label": "Describes the pattern in their own results",
      "strand": "s4",
      "band": 1,
      "max": 1
    },
    {
      "id": "Q4a",
      "q": "Q4",
      "sub": "a",
      "part": "A",
      "label": "A specific source of error",
      "strand": "s5",
      "band": 2,
      "max": 1
    },
    {
      "id": "Q4b",
      "q": "Q4",
      "sub": "b",
      "part": "A",
      "label": "An improvement that matches the error",
      "strand": "s5",
      "band": 3,
      "max": 1
    },
    {
      "id": "Q5a",
      "q": "Q5",
      "sub": "a",
      "part": "B",
      "label": "Picks out the independent variable",
      "strand": "s2",
      "band": 1,
      "max": 1
    },
    {
      "id": "Q5b",
      "q": "Q5",
      "sub": "b",
      "part": "B",
      "label": "Picks out the dependent variable",
      "strand": "s2",
      "band": 1,
      "max": 1
    },
    {
      "id": "Q5c",
      "q": "Q5",
      "sub": "c",
      "part": "B",
      "label": "Picks out a controlled variable",
      "strand": "s2",
      "band": 3,
      "max": 1
    },
    {
      "id": "Q6a",
      "q": "Q6",
      "sub": "a",
      "part": "B",
      "label": "Identifies the odd result",
      "strand": "s3",
      "band": 2,
      "max": 1
    },
    {
      "id": "Q6b",
      "q": "Q6",
      "sub": "b",
      "part": "B",
      "label": "Suggests a cause for the odd result",
      "strand": "s5",
      "band": 2,
      "max": 1
    },
    {
      "id": "Q6c",
      "q": "Q6",
      "sub": "c",
      "part": "B",
      "label": "Mean range without the odd result, with working",
      "strand": "s3",
      "band": 2,
      "max": 1
    },
    {
      "id": "Q7a",
      "q": "Q7",
      "sub": "a",
      "part": "B",
      "label": "Mean of three trials, with working",
      "strand": "s3",
      "band": 1,
      "max": 1
    },
    {
      "id": "Q7b",
      "q": "Q7",
      "sub": "b",
      "part": "B",
      "label": "Tip speed from v = ω × L",
      "strand": "s3",
      "band": 3,
      "max": 1
    },
    {
      "id": "Q7c",
      "q": "Q7",
      "sub": "c",
      "part": "B",
      "label": "Second tip speed from v = ω × L",
      "strand": "s3",
      "band": 3,
      "max": 1
    },
    {
      "id": "Q8a",
      "q": "Q8",
      "sub": "pts",
      "part": "B",
      "label": "Plots all five points accurately",
      "strand": "s4",
      "band": 2,
      "max": 1
    },
    {
      "id": "Q8b",
      "q": "Q8",
      "sub": "curve",
      "part": "B",
      "label": "Draws a smooth curve of best fit",
      "strand": "s4",
      "band": 2,
      "max": 1
    },
    {
      "id": "Q8c",
      "q": "Q8",
      "sub": "odd",
      "part": "B",
      "label": "Leaves the odd result out of the line",
      "strand": "s4",
      "band": 3,
      "max": 1
    },
    {
      "id": "Q9a",
      "q": "Q9",
      "sub": "a",
      "part": "B",
      "label": "Reads a prediction from the curve",
      "strand": "s4",
      "band": 3,
      "max": 1
    },
    {
      "id": "Q9b",
      "q": "Q9",
      "sub": "b",
      "part": "B",
      "label": "Shows how the prediction was read",
      "strand": "s4",
      "band": 3,
      "max": 1
    },
    {
      "id": "Q10a",
      "q": "Q10",
      "sub": "a",
      "part": "B",
      "label": "Describes the trend in range, with numbers",
      "strand": "s4",
      "band": 1,
      "max": 1
    },
    {
      "id": "Q10b",
      "q": "Q10",
      "sub": "b",
      "part": "B",
      "label": "Recognises a curve and says how",
      "strand": "s4",
      "band": 2,
      "max": 1
    },
    {
      "id": "Q10c",
      "q": "Q10",
      "sub": "c",
      "part": "B",
      "label": "Describes the change in peak spin, with numbers",
      "strand": "s4",
      "band": 1,
      "max": 1
    },
    {
      "id": "Q11",
      "q": "Q11",
      "sub": "",
      "part": "B",
      "label": "Explains why a heavier beanbag lands shorter",
      "strand": "s1",
      "band": 3,
      "max": 3
    },
    {
      "id": "Q12a",
      "q": "Q12",
      "sub": "a",
      "part": "C",
      "label": "Gravitational potential energy given up",
      "strand": "s3",
      "band": 4,
      "max": 1
    },
    {
      "id": "Q12b",
      "q": "Q12",
      "sub": "b",
      "part": "C",
      "label": "Kinetic energy of the beanbag",
      "strand": "s3",
      "band": 4,
      "max": 1
    },
    {
      "id": "Q12c",
      "q": "Q12",
      "sub": "c",
      "part": "C",
      "label": "Efficiency of the launch",
      "strand": "s3",
      "band": 4,
      "max": 1
    },
    {
      "id": "Q13a",
      "q": "Q13",
      "sub": "a",
      "part": "C",
      "label": "Kinetic energy of the light beanbag",
      "strand": "s1",
      "band": 4,
      "max": 1
    },
    {
      "id": "Q13b",
      "q": "Q13",
      "sub": "b",
      "part": "C",
      "label": "Kinetic energy of the heavy beanbag",
      "strand": "s1",
      "band": 4,
      "max": 1
    },
    {
      "id": "Q13c",
      "q": "Q13",
      "sub": "c",
      "part": "C",
      "label": "Which received more, and where the rest went",
      "strand": "s1",
      "band": 4,
      "max": 2
    },
    {
      "id": "Q14",
      "q": "Q14",
      "sub": "",
      "part": "C",
      "label": "Judges whether the conclusion is justified",
      "strand": "s5",
      "band": 4,
      "max": 2
    }
  ]
};
