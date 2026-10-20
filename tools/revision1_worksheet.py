#!/usr/bin/env python3
"""Build the Revision 1 worksheet for year7-science/space — both copies.

    python3 tools/revision1_worksheet.py            # student sheet
    python3 tools/revision1_worksheet.py --answers  # red answer copy
    python3 tools/revision1_worksheet.py --both

Rebuilt from the supplied PDF rather than embedded, so it matches the
unit's other eleven worksheets: worksheet.css, A4 print rules, the shared
question furniture, a nav entry and a Print button. The PDF stays beside
it as a download for anyone who wants the original file.

Figures come out of the deck (see revision1_figs.py) rather than being
redrawn, so the sheet and the slides can never show different diagrams.

Marks: the PDF marks some tasks and not others, because the unmarked ones
are practice rather than assessment. That is kept — `.marks` appears only
where the CAT would actually award them, and there is no sheet total,
since a total over a mixed sheet would mean nothing. The other worksheets
in this unit do carry totals; this one is deliberately different.

WHY BOTH COPIES COME OUT OF THIS ONE FILE
-----------------------------------------
The answer copy is the student sheet with answers written into its own
furniture — blanks filled, ruled lines written on, table cells completed
— exactly as worksheet.css's "red answer overlay" block describes. The
question wording therefore exists once, here, and cannot drift between
the two copies the way a hand-copied key does. Running with no flag must
leave worksheet-revision1.html byte-identical; the build checks that the
answer text never leaks into the student copy.

Answers are the deck's own. Every one is lifted from the matching answer
slide in revision1.html (slides 4, 7, 9, 11, 14, 16, 19, 21, 23, 25), so
the key agrees with what the class is actually shown. Where the deck
gives a rider ("one rotation = one day"), it becomes marking guidance.

The answer copy is staff-gated, same shell as
worksheet-revision-solutions.html: this script writes the plaintext
payload (gitignored) and the lock shell, and keeps any `var BLOB` line
already in the shell so re-running after encryption does not wipe it.
Encrypt the payload through tools/staff-crypt.html and paste the emitted
line over the placeholder.
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
UNIT = os.path.join(ROOT, 'year7-science', 'space')
DST = os.path.join(UNIT, 'worksheet-revision1.html')
SHELL = os.path.join(UNIT, 'worksheet-revision1-solutions.html')
PAYLOAD = os.path.join(UNIT, 'worksheet-revision1-solutions-payload.html')
FIG = json.load(open(os.path.join(HERE, 'revision1_figs.json'), encoding='utf-8'))

ANSWERS = False          # flipped by build(); every helper below reads it

# The exit self-rating rows. Module level because verify() counts them: they
# are the cells deliberately left blank on the answer copy.
RATE_ROWS = [
    ('Layers of Earth and Sun', '&sect;1.2, &sect;1.4 &middot; p.3&ndash;5', 'name and order all 4 + 6 layers'),
    ('Day, night and seasons', '&sect;2 &middot; p.8&ndash;10', 'read an orbit diagram; explain tilt'),
    ('Moon phases', '&sect;3.1 &middot; p.11', 'name a phase; pick the Melbourne view'),
    ('Tides', '&sect;3.2 &middot; p.12&ndash;13', 'explain spring vs neap; two tides a day'),
    ('Calculations', '&sect;1.1, &sect;1.4, &sect;5.1', 'ratios, AU to km, light time, with working'),
    ('Solar system', '&sect;5 &middot; p.20&ndash;22', 'order and classify; explain the asteroid belt'),
    ('Moon, debris, sky knowledge', '&sect;1.3, &sect;6.3, &sect;7', 'explain each in two linked sentences'),
]


# ---------------------------------------------------------------- helpers

def fig(name, i=0, h='md', label=''):
    return (f'<figure class="ws-fig" data-h="{h}">{FIG[name][i]}'
            + (f'<figcaption>{label}</figcaption>' if label else '')
            + '</figure>')


def blank(ans='', lg=True):
    """An inline rule. In the answer copy the answer is written on it."""
    cls = 'blank lg' if lg else 'blank'
    inner = f'<span class="wsa-in">{ans}</span>' if ANSWERS and ans else ''
    return f'<span class="{cls}">{inner}</span>'


def lines(n, ans=None):
    """Ruled writing space. In the answer copy, written on.

    .lines.filled keeps data-lines so --n still sets the minimum height,
    and goes to height:auto so a long model answer grows the block rather
    than spilling out of it."""
    if ANSWERS and ans:
        return f'<div class="lines filled" data-lines="{n}">{ans}</div>'
    return f'<div class="lines" data-lines="{n}"></div>'


def cell(ans=''):
    inner = f'<span class="wsa-in">{ans}</span>' if ANSWERS and ans else ''
    return f'<td class="fill">{inner}</td>'


def note(txt):
    """Marking guidance. The one thing that sits outside the student's own
    furniture, because a student never wrote it."""
    return f'<span class="wsa-note">{txt}</span>' if ANSWERS and txt else ''


def drawbox(h, ans_fig=None, label=''):
    """Empty space to draw in — replaced on the answer copy by the deck's
    own model diagram, since the marking copy wants the diagram shown
    rather than a second drawing of it."""
    if ANSWERS and ans_fig:
        return fig(ans_fig, 0, h, label)
    return f'<div class="drawbox" data-h="{h}"></div>'


def q(num, body, marks=None, nt=None):
    m = f'<span class="marks">{marks}</span>' if marks else ''
    return (f'    <div class="q"><span class="qn">{num}</span>\n'
            f'      <div class="qbody">{m}{body}{note(nt)}</div>\n    </div>')


def part(label, title, body, marks=None):
    m = f'<span class="marks">{marks}</span>' if marks else ''
    return ('  <section class="part">\n'
            f'    <div class="part-head"><span class="part-label">{label}</span>'
            f'<span class="part-title">{title}</span>{m}</div>\n'
            + body + '\n  </section>\n')


# ------------------------------------------------------------------ parts

def parts():
    """Build every part. Called after ANSWERS is set."""
    P = []

    # 1 — answers from slide 4 -------------------------------------------
    QUICK = [
        ('How long does Earth take to spin once on its axis?', '24 hours',
         'One rotation = one day. Accept &ldquo;one day&rdquo;, or 23&nbsp;h 56&nbsp;min if they name the sidereal day.'),
        ('How many days for Earth to travel once around the Sun?', '365.25 days',
         'One revolution = one year. Accept 365, 365&frac14; or 365.25.'),
        ('By how many degrees is Earth&rsquo;s axis tilted?', '23.5&deg;',
         'Accept 23.4&deg;. The axis always points the same way.'),
        ('How many days from one full Moon to the next?', '29.5 days',
         'One full cycle of phases. Accept 29 or 30.'),
        ('One astronomical unit (1&nbsp;AU) is how many kilometres?', '150,000,000 km', None),
        ('How far does light travel in one second?', '300,000 km',
         'So the speed of light is 300,000&nbsp;km/s.'),
        ('Which layer of the Sun do we see as its &ldquo;surface&rdquo;?', 'Photosphere',
         'About 5,500&nbsp;&deg;C.'),
        ('Is Neptune a terrestrial planet, a gas giant or an ice giant?', 'Ice giant',
         'Not a gas giant &mdash; Uranus and Neptune are the two ice giants.'),
    ]
    P.append(part('1', 'Quick-fire eight <span class="pt-meta">Starter &middot; from memory, no booklet</span>',
        '\n'.join(q(i + 1, text + blank(ans), nt=nt)
                  for i, (text, ans, nt) in enumerate(QUICK))
        + '\n    <div class="infobox"><span class="lbl">Score</span><p>&nbsp;&nbsp;&nbsp;&nbsp;/ 8 &mdash; circle any you missed and come back to them.</p></div>'))

    # 2 — answers from slide 7 ------------------------------------------
    EARTH = [('I&rsquo;m liquid iron and nickel, and my movement makes Earth&rsquo;s magnetic field.', 'Outer core'),
             ('I&rsquo;m only 5&ndash;70&nbsp;km thick and I&rsquo;m broken into tectonic plates.', 'Crust'),
             ('I&rsquo;m solid iron and nickel at the very centre of the planet.', 'Inner core'),
             ('I&rsquo;m semi-solid rock about 2,900&nbsp;km thick.', 'Mantle')]
    SUN = [('I&rsquo;m the Sun&rsquo;s visible surface, where sunspots form.', 'Photosphere'),
           ('Nuclear fusion happens in me, at about 15 million&nbsp;&deg;C.', 'Core'),
           ('I&rsquo;m the outermost layer, at over 1 million&nbsp;&deg;C.', 'Corona'),
           ('Energy takes about 100,000 years to cross me as light.', 'Radiative zone'),
           ('I&rsquo;m the thin layer of atmosphere just above the visible surface.', 'Chromosphere'),
           ('Hot plasma rises and sinks through me, carrying energy outward.', 'Convective zone')]
    L2 = ('    <div class="chips"><span class="cl">Part A &middot; Earth</span>'
          '<span class="chip">Inner core</span><span class="chip">Outer core</span>'
          '<span class="chip">Mantle</span><span class="chip">Crust</span></div>\n'
          + '\n'.join(q(f'A{i+1}', text + blank(ans)) for i, (text, ans) in enumerate(EARTH))
          + '\n    <div class="chips"><span class="cl">Part B &middot; The Sun</span>'
            '<span class="chip">Core</span><span class="chip">Radiative zone</span>'
            '<span class="chip">Convective zone</span><span class="chip">Photosphere</span>'
            '<span class="chip">Chromosphere</span><span class="chip">Corona</span></div>\n'
          + '\n'.join(q(f'B{i+1}', text + blank(ans)) for i, (text, ans) in enumerate(SUN))
          + '\n    <div class="y8box"><span class="lbl">Challenge</span>'
            '<p>Write each set of layers in order, from the centre out.</p>'
            '<p><b>Earth</b>' + lines(1, 'Inner core &rarr; outer core &rarr; mantle &rarr; crust')
          + '</p><p><b>Sun</b>' + lines(1, 'Core &rarr; radiative zone &rarr; convective zone &rarr; photosphere &rarr; chromosphere &rarr; corona')
          + '</p>' + note('Memory hook for the Sun: <b>C</b>an <b>R</b>eally <b>C</b>ool '
                          '<b>P</b>eople <b>C</b>hase <b>C</b>omets?') + '</div>')
    P.append(part('2', 'Which layer am I? <span class="pt-meta">Layers &middot; pairs</span>', L2))

    # 3 — answers from slide 9 ------------------------------------------
    L3 = (f'    {fig("daynight", 0, "md", "Sunlight arrives from the right. P and Q are marked on Earth.")}\n'
          + '\n'.join([
              q(1, 'Which place, P or Q, is in daylight right now?' + blank('P'), 1,
                'Sunlight arrives from the right, so the right-hand half is day. Q is on the night side.'),
              q(2, 'Which place is having summer? Use the tilt of the axis to explain.'
                   + lines(3, 'P is having summer. The South Pole end leans toward the Sun, so the '
                              'Southern Hemisphere &mdash; where P is &mdash; gets more direct sunlight '
                              'and longer days.'), 2,
                '1 mark for P / the Southern Hemisphere, 1 mark for the tilt toward the Sun. '
                'No mark for an answer about distance from the Sun.'),
              q(3, 'Roughly which month of the year could this be?' + blank('Around December'), 1,
                'Accept any southern summer month, December to February.'),
              q(4, 'Fix this sentence: &ldquo;Earth revolves on its axis once every 24 hours.&rdquo;'
                   + lines(2, '&ldquo;Earth <b>rotates</b> on its axis once every 24 hours.&rdquo;'), 1,
                'Rotate = spin on the axis. Revolve = orbit the Sun, which takes 365.25 days. '
                'The mark is for the word, not for rewriting the sentence.'),
          ]))
    P.append(part('3', 'Read the diagram: places P and Q <span class="pt-meta">Day, night and seasons &middot; on your own</span>', L3, '5 marks'))

    # 4 — answers from slide 11 -----------------------------------------
    L4 = (f'    {fig("orbit4", 0, "md", "Earth at four positions around the Sun. &bull; marks the North Pole.")}\n'
          + '\n'.join([
              q('a', 'At which position is Melbourne having summer?' + blank('Position 2', lg=False), None,
                'The South Pole end leans toward the Sun.'),
              q('b', 'Follow the arrows. At which position is Melbourne having spring?'
                   + blank('Position 3', lg=False), None,
                'Along the arrows: 2 summer, 4 autumn, 1 winter, 3 spring.'),
              q('c', 'At which two positions are day and night equal everywhere?'
                   + blank('Positions 3 and 4', lg=False), None,
                'The equinoxes &mdash; neither pole leans toward the Sun.'),
              q('d', 'Japan is in the Northern Hemisphere. At which position is Japan having winter?'
                   + blank('Position 2', lg=False), None,
                'When the south leans in, the north leans away. The two hemispheres always have '
                'opposite seasons.'),
              q('e', '&ldquo;Melbourne is cold in July because Earth is furthest from the Sun then.&rdquo; '
                     'Earth really <i>is</i> furthest in July. So what is wrong with this reasoning?'
                   + lines(3, '<p>The fact is true, but it is the wrong cause. Earth is only about 3% '
                              'further from the Sun in July, which makes very little difference.</p>'
                              '<p>Melbourne is cold because the Southern Hemisphere is tilted away from '
                              'the Sun: the Sun sits lower, its rays are spread over more ground, and the '
                              'days are shorter. The proof &mdash; in July the Northern Hemisphere is '
                              'having summer, at exactly the same distance.</p>'), None,
                'The point to listen for is that distance is the same for both hemispheres, so it '
                'cannot explain opposite seasons.'),
          ]))
    P.append(part('4', 'Earth&rsquo;s year in four positions <span class="pt-meta">Day, night and seasons &middot; pairs</span>', L4))

    # 5 — answers from slide 14 -----------------------------------------
    L5 = (f'    {fig("moon6", 0, "md", "The Moon at six positions, with sunlight from the right.")}\n'
          '    <div class="chips"><span class="cl">Word bank</span>'
          '<span class="chip">New</span><span class="chip">Waxing crescent</span>'
          '<span class="chip">First quarter</span><span class="chip">Waxing gibbous</span>'
          '<span class="chip">Full</span><span class="chip">Waning gibbous</span>'
          '<span class="chip">Third quarter</span><span class="chip">Waning crescent</span></div>\n'
          + '    <figure class="ws-fig" data-h="xs">'
          + ''.join(FIG['moon6'][1:5])
          + '<figcaption>(i)&ensp;&ensp;(ii)&ensp;&ensp;(iii)&ensp;&ensp;(iv) &mdash; as seen from Melbourne</figcaption></figure>\n'
          + '\n'.join([
              q('a', 'Name the phase seen from Earth at: position 2' + blank('Waxing crescent', lg=False)
                   + ' position 5' + blank('Waning gibbous', lg=False), None,
                'Position 2 is just after new; position 5 is just after full.'),
              q('b', 'Which drawing, (i) to (iv), shows the Moon at position 3 as seen from Melbourne?'
                   + blank('(iii)', lg=False), None,
                'Position 3 is a waxing gibbous, and from Melbourne a waxing Moon is lit on the '
                '<b>left</b>.'),
              q('c', 'Which drawing shows the Moon at position 6 as seen from Melbourne?'
                   + blank('(iv)', lg=False), None,
                'Position 6 is a waning crescent, lit on the right from Melbourne.'),
              q('d', 'Name the phase seen from Earth at: position 1' + blank('New Moon', lg=False)
                   + ' position 4' + blank('Full Moon', lg=False), None,
                'At 1 the Moon sits between Earth and the Sun, so its lit half faces away from us. '
                'At 4 Earth is between the Sun and the Moon.'),
              q('e', '&ldquo;The dark part of a crescent Moon is Earth&rsquo;s shadow.&rdquo; Correct this statement.'
                   + lines(3, 'The Moon makes no light of its own &mdash; we see sunlight reflected off '
                              'it, and half of it is always lit. The dark part of a crescent is the '
                              'unlit half turned toward us, not Earth&rsquo;s shadow. Earth&rsquo;s '
                              'shadow falling on the Moon is a lunar eclipse, which is rare.'), None,
                'Listen for &ldquo;the unlit half turned toward us&rdquo;. Naming the eclipse is a '
                'bonus, not required.'),
          ]))
    P.append(part('5', 'The Moon at positions 1 to 6 <span class="pt-meta">Moon phases &middot; on your own, then check</span>', L5))

    # 6 — answers from slide 16 -----------------------------------------
    L6 = ('    <figure class="ws-fig" data-h="sm">' + ''.join(FIG['tides'])
          + '<figcaption>(i) Sun &middot; Moon &middot; Earth &ensp; (ii) Moon at right angles &ensp; '
            '(iii) Sun &middot; Earth &middot; Moon &mdash; not to scale</figcaption></figure>\n'
          + '\n'.join([
              q(1, 'Which line-up(s) cause spring tides? Name the Moon&rsquo;s phase in each.'
                   + lines(2, '(i) and (iii). (i) is a new Moon, (iii) a full Moon. The Sun and Moon '
                              'pull along the same line, so their effects add: the highest highs and '
                              'the lowest lows.'), 2,
                '1 mark for both line-ups, 1 mark for both phases.'),
              q(2, 'Which causes neap tides? Why are neap tides smaller?'
                   + lines(2, '(ii) &mdash; a first or third quarter Moon. The Sun&rsquo;s pull is at '
                              'right angles to the Moon&rsquo;s, so they partly cancel and the tidal '
                              'range is smaller.'), 2,
                '1 mark for (ii), 1 mark for the two pulls partly cancelling.'),
              q(3, 'There is a new Moon on 2 November. About when are the next neap tides?'
                   + lines(1, 'About 9 November &mdash; a quarter of the 29.5-day cycle later, at first quarter.'), 1,
                'Accept 8&ndash;10 November.'),
              q(4, 'High tide at a beach is at 6&nbsp;am. When is the next high tide, and which motion causes it?'
                   + lines(2, 'About 6:25&nbsp;pm. Earth spinning on its axis carries the beach through '
                              'the second bulge, on the side away from the Moon. Two bulges means two '
                              'high tides a day.'), 2,
                '1 mark for about 12&nbsp;h 25&nbsp;min later (accept &ldquo;about 6:30&nbsp;pm&rdquo; '
                'or &ldquo;about 12 hours later&rdquo;), 1 mark for Earth&rsquo;s rotation.'),
              q(5, 'If the Moon vanished, would the oceans stop having tides? Explain.'
                   + lines(2, 'No, but the tides would be much smaller. The Moon&rsquo;s gravity makes '
                              'the main bulge, but the Sun&rsquo;s gravity also pulls on the oceans, so '
                              'there would still be small tides.'), 2,
                '1 mark for &ldquo;no&rdquo;, 1 mark for the Sun still pulling on the oceans.'),
          ]))
    P.append(part('6', 'Three line-ups: spring or neap? <span class="pt-meta">Tides &middot; pairs</span>', L6, '9 marks'))

    # 7 — answers from slide 19 -----------------------------------------
    CALC = [
        ('How many times wider is the Sun than the Moon? Nearest whole number.', 2,
         'times wider = bigger &divide; smaller<br>= 1,392,000 &divide; 3,474<br>= 400.69&hellip;',
         '401 times',
         '1 mark for the rule and working, 1 mark for the answer. Accept 400 if they round down.'),
        ('Saturn is 9.54&nbsp;AU from the Sun. Calculate this distance in km.', 2,
         'km = AU &times; 150,000,000<br>= 9.54 &times; 150,000,000',
         '1,431,000,000 km',
         'The unit is needed for the second mark.'),
        ('How long does sunlight take to reach Mars? Give your answer in seconds, then in minutes and seconds.', 2,
         'time = distance &divide; speed<br>= 228,000,000 &divide; 300,000 = 760&nbsp;s<br>760 &divide; 60 = 12 rem 40',
         '760 s = 12 min 40 s',
         'Both forms are needed for the second mark.'),
        ('How many times farther from the Sun is Neptune than Mars? Nearest whole number.', 2,
         'bigger &divide; smaller<br>= 30.1 &divide; 1.52<br>= 19.8&hellip;',
         '20 times',
         'No kilometres needed &mdash; both distances are already in AU, so divide one by the other. '
         'Converting first and then dividing is still correct.'),
        ('<b>Challenge:</b> mission control radios an astronaut on the Moon, who replies instantly. '
         'What is the shortest wait between sending and hearing the reply?', 2,
         'distance &divide; speed, there and back<br>= 384,400 &divide; 300,000 = 1.28&nbsp;s each way<br>&times; 2',
         '2.56 s',
         'The signal travels there <i>and</i> back, so the one-way time is doubled. 1.28&nbsp;s alone '
         'earns the working mark only.'),
    ]
    L7 = ('    <div class="infobox"><span class="lbl">Data</span><p>Sun diameter 1,392,000&nbsp;km &middot; '
          'Moon diameter 3,474&nbsp;km &middot; Earth to Moon 384,400&nbsp;km &middot; '
          'Mars to Sun 228,000,000&nbsp;km &middot; Mars 1.52&nbsp;AU &middot; Saturn 9.54&nbsp;AU &middot; '
          'Neptune 30.1&nbsp;AU &middot; 1&nbsp;AU = 150,000,000&nbsp;km &middot; speed of light = 300,000&nbsp;km/s</p>'
          '<p><b>Every time:</b> write the rule &rarr; put the numbers in &rarr; calculate &rarr; '
          'answer with units, rounded as asked.</p></div>\n'
          + '\n'.join(q(i + 1, text + '<table class="wtbl"><tr><th>Rule and working</th>'
                                      '<th>Answer (with units)</th></tr><tr>'
                                      + cell(work) + cell(ans) + '</tr></table>', m, nt)
                      for i, (text, m, work, ans, nt) in enumerate(CALC)))
    P.append(part('7', 'Your turn: five calculations <span class="pt-meta">Calculations &middot; show all working</span>', L7, '10 marks'))

    # 8 — answers from slide 21 -----------------------------------------
    ORDER = ['Mercury', 'Venus', 'Earth', 'Mars', 'Jupiter', 'Saturn', 'Uranus', 'Neptune']
    L8 = '\n'.join([
        q(1, 'Put them in order from the Sun: Uranus &middot; Mars &middot; Saturn &middot; Mercury &middot; '
             'Neptune &middot; Earth &middot; Jupiter &middot; Venus'
             '<table class="wtbl"><tr>' + ''.join(f'<th>{i}</th>' for i in range(1, 9)) + '</tr>'
             '<tr>' + ''.join(cell(p) for p in ORDER) + '</tr></table>'
             '<p>My own mnemonic:</p>'
             + lines(1, 'e.g. <i>My Very Easy Method Just Speeds Up Naming</i>'), None,
          'Four rocky, two gas giants, two ice giants, with the asteroid belt between Mars and '
          'Jupiter. Any mnemonic giving the right order earns it &mdash; their own silly one sticks '
          'better than a borrowed one.'),
        q(2, 'Odd one out: Mercury, Venus, Saturn, Mars. Which, and why?'
             + lines(2, 'Saturn. It is a gas giant; Mercury, Venus and Mars are all small, rocky '
                        'terrestrial planets.'), None,
          'The reason matters more than the name &mdash; &ldquo;Saturn&rdquo; alone is half an answer.'),
        q(3, 'Who am I?<br>a) The first planet beyond the asteroid belt.' + blank('Jupiter')
             + '<br>b) An ice giant, 7th from the Sun, spinning on my side.' + blank('Uranus')
             + '<br>c) The hottest planet, though not the closest to the Sun.' + blank('Venus'), None,
          'c) Venus &mdash; its thick atmosphere traps the heat.'),
        q(4, '&ldquo;The asteroid belt is what&rsquo;s left of a planet that exploded.&rdquo; '
             'Give the scientific explanation instead.'
             + lines(3, 'It never was a planet. Jupiter&rsquo;s strong gravity kept stirring up the '
                        'rocky and metal pieces in that region, so they could never clump together '
                        'into a single planet.'), None,
          'Do not accept &ldquo;a planet exploded&rdquo; in any wording. The point is that the '
          'material never came together in the first place.'),
        q(5, 'Where is the Kuiper Belt? Name a dwarf planet found there.'
             + lines(2, 'Beyond Neptune, about 30&ndash;50&nbsp;AU from the Sun. Pluto is there '
                        '(also Eris, Haumea or Makemake).'), None,
          'Accept any of the four dwarf planets.'),
    ])
    P.append(part('8', 'Sort, classify, explain <span class="pt-meta">Solar system &middot; pairs</span>', L8))

    # 9 — answers from slide 23 -----------------------------------------
    L9 = ('    <div class="infobox"><span class="lbl">Sentence frame</span>'
          '<p>&ldquo;This happens because &hellip; This means that &hellip;&rdquo;</p></div>\n'
          + '\n'.join([
              q('A', '<b>Planet temperatures.</b> Mercury is closer to the Sun than Venus. Yet Mercury&rsquo;s '
                     'night side drops to &minus;180&nbsp;&deg;C, while Venus stays at about 465&nbsp;&deg;C '
                     'day and night. Explain why.'
                   + lines(4, 'Venus has a very thick carbon dioxide atmosphere that traps heat and '
                              'carries it right around the planet, so its night side stays hot. '
                              'Mercury has almost no atmosphere, so heat escapes to space as soon as '
                              'the Sun sets. Distance decides how much energy arrives; the atmosphere '
                              'decides how much stays.'), 2,
                '1 mark for Venus&rsquo;s thick atmosphere trapping heat, 1 mark for Mercury having '
                'almost none. Both points are needed for 2.'),
              q('B', '<b>Space debris.</b> A fleck of paint once chipped a window on the International Space '
                     'Station. Explain how something so tiny could do damage, and why the crew could not '
                     'steer around it.'
                   + lines(4, 'Objects in orbit move at about 7.8&nbsp;km/s &mdash; up to 15&nbsp;km/s '
                              'in a head-on meeting &mdash; so even a tiny mass arrives with huge '
                              'energy. Pieces that small cannot be tracked from the ground, so there is '
                              'no warning in time to move out of the way.'), 2,
                '1 mark for the orbital speed and the energy that comes with it, 1 mark for being too '
                'small to track. Kessler syndrome is a bonus, not required.'),
              q('C', '<b>Sky knowledge.</b> A friend says the dark patches along the Milky Way are &ldquo;just '
                     'empty gaps&rdquo;. Correct them, and explain how Aboriginal astronomers use these dark '
                     'shapes as a calendar.'
                   + lines(4, 'The dark patches are real clouds of gas and dust blocking the light of '
                              'the stars behind them, not gaps. Aboriginal astronomers read the dark '
                              'shapes themselves as constellations &mdash; the Emu in the Sky &mdash; '
                              'and its position at dusk changes through the year, signalling events on '
                              'Country such as when emus lay their eggs.'), 2,
                '1 mark for dust clouds blocking starlight, 1 mark for the Emu in the Sky marking the '
                'time of year. Western constellations join bright stars; dark constellations are made '
                'of the clouds.'),
          ]))
    P.append(part('9', 'Explain it: two marks, two points, joined by &ldquo;because&rdquo; '
                       '<span class="pt-meta">Explain it &middot; on your own</span>', L9, '6 marks'))

    # 10 — answers from slides 24 and 25 --------------------------------
    L10 = q(1, 'Japan is in the Northern Hemisphere. Using a labelled diagram, explain why Japan has its '
               'summer in June while Melbourne has its summer in December.'
               + drawbox('lg', 'model',
                         'Model diagram &mdash; Sun in the middle, Earth drawn twice with the axis '
                         'tilted the same way in both. A is June&ndash;July, B is December&ndash;January.')
               + lines(4, 'In my diagram, at position A (June) Earth&rsquo;s axis leans so the Northern '
                          'Hemisphere tilts toward the Sun. Japan gets the Sun high in the sky, its '
                          'rays strike more directly so the energy is concentrated, and its days are '
                          'long: summer. At the same time the Southern Hemisphere tilts away, so '
                          'Melbourne gets low, spread-out sunlight and short days: winter. At position '
                          'B (December) the axis still points the same way, but Earth is on the other '
                          'side of the Sun, so the seasons swap. It is not distance &mdash; Earth is '
                          'actually closest to the Sun in January.'), 4,
            '<b>1</b> Sun in the middle, Earth drawn twice, axis tilted the same way in both with N '
            'and S labelled. <b>2</b> June: north tilted toward the Sun, so Japan has summer. '
            '<b>3</b> December: south tilted toward the Sun, so Melbourne has summer. <b>4</b> Why '
            'leaning toward matters &mdash; Sun higher, rays more direct, days longer &mdash; and '
            'says explicitly that it is <i>not</i> caused by distance. '
            'The explanation must refer to the diagram to earn marks 2 and 3.')
    P.append(part('10', 'A four-mark diagram answer <span class="pt-meta">Draw and explain &middot; on your own</span>', L10, '4 marks'))

    # exit --------------------------------------------------------------
    RATE = RATE_ROWS
    # The self-rating column stays blank on the answer copy too: it is the
    # student's own judgement, not a question with a right answer.
    EXIT = ('    <p>Write <b>Confident</b>, <b>Shaky</b> or <b>Need help</b> next to each, then revise your two weakest.</p>\n'
            '    <table class="wtbl"><tr><th>Topic</th><th>Booklet</th><th>I can&hellip;</th><th>How I feel</th></tr>'
            + ''.join(f'<tr><td>{a}</td><td>{b}</td><td>{c}</td><td class="fill"></td></tr>' for a, b, c in RATE)
            + '</table>\n    <div class="infobox"><span class="lbl">Best practice before the CAT</span>'
              '<p>The booklet&rsquo;s &ldquo;Check your understanding&rdquo; questions for each topic above.</p>'
            + note('Nothing to mark here &mdash; it is the student&rsquo;s own rating. Collect the '
                   'sheets and it tells you which booklet sections to reteach on Monday.') + '</div>')
    P.append(part('!Exit', 'Rate yourself, then revise your two weakest', EXIT))

    return P


# ------------------------------------------------------------------ pages

HEAD = '''<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Bitter:wght@500;700;800&{caveat}family=Source+Sans+3:ital,wght@0,400;0,600;0,700;1,400&display=swap" rel="stylesheet">
{css}<link rel="stylesheet" href="../../assets/css/sitenav.css">
<script src="../../assets/js/sitenav.js" defer></script>
<link rel="icon" href="../../assets/icons/favicon.svg" type="image/svg+xml">
<link rel="icon" href="../../assets/icons/favicon.ico" sizes="32x32">
<link rel="apple-touch-icon" href="../../assets/icons/apple-touch-icon.png">
<link rel="manifest" href="../../site.webmanifest">
<meta name="theme-color" content="#24576f">'''


def student_page(body_parts):
    return '''<!DOCTYPE html>
<html lang="en">
<head>
''' + HEAD.format(title='Revision Worksheet 1 &middot; Ready for the CAT | Space',
                  caveat='',
                  css='<link rel="stylesheet" href="../../assets/css/tokens.css">\n'
                      '<link rel="stylesheet" href="../../assets/css/worksheet.css">\n') + '''
</head>
<body class="worksheet-page theme-space">

<div class="ws-bar">
  <a href="index.html">&#8592; Unit home</a>
  <a href="revision1.html">Revision 1 slides</a>
  <a href="Space_CAT_Revision_Worksheet.pdf">Original PDF</a>
  <span class="spacer"></span>
  <span class="hint">Fill in as the slides go</span>
  <button type="button" onclick="window.print()">Print / Save as PDF</button>
</div>

<div class="sheet">
  <div class="ws-head">
    <div class="ws-tag">Year 7&ndash;8 Science &middot; Space</div>
    <h1><span class="lnum">Revision 1</span>Ready for the CAT</h1>
    <p class="ws-sub">Fill in the boxes as we go through the slides. Answers are shown on the slide after each task &mdash; tick or fix yours in a different colour.</p>
    <div class="namebar">
      <span>Name</span><span>Class</span><span>Date</span>
    </div>
  </div>

''' + '\n'.join(body_parts) + '''
  <div class="ws-foot">Year 7 Science &middot; Space &middot; Revision worksheet 1 &mdash; companion to the Revision 1 slides.</div>
</div>

</body>
</html>
'''


def answer_payload(body_parts):
    """Everything that goes inside #content once the page is unlocked.

    It is the student sheet with the answer overlay switched on, so the
    marking copy reads as a completed worksheet. Inline onclick survives
    innerHTML, so the Print button still works from the payload."""
    return '''<div class="ws-bar">
  <a href="index.html">&#8592; Unit home</a>
  <a href="worksheet-revision1.html">Blank student copy</a>
  <a href="revision1.html">Revision 1 slides</a>
  <span class="spacer"></span>
  <span class="hint">Red = answer &middot; red italics = marking guidance</span>
  <button type="button" onclick="window.print()">Print / Save as PDF</button>
</div>

<div class="sheet staff">
  <div class="ws-head">
    <div class="ws-tag">Year 7&ndash;8 Science &middot; Space &middot; Teacher copy</div>
    <h1><span class="lnum">Revision 1</span>Ready for the CAT<span class="staff-flag">Answers</span></h1>
    <p class="ws-sub">The student sheet with model answers written in. Answers are the ones the Revision 1 slides show, so marking matches what the class was taught. Model wording is not the only acceptable wording &mdash; award the mark for any response carrying the same point.</p>
    <div class="namebar">
      <span>Name</span><span>Class</span><span>Date</span>
    </div>
  </div>

''' + '\n'.join(body_parts) + '''
  <div class="ws-foot">Year 7 Science &middot; Space &middot; Revision worksheet 1, answer copy &mdash; companion to the Revision 1 slides.</div>
</div>
'''


PLACEHOLDER = 'var BLOB = {v:2, iv:"", ct:"", keys:[]};'


def answer_shell():
    """The lock page. Any `var BLOB` line already present is kept, so a
    rebuild after encryption does not throw the blob away."""
    blob = PLACEHOLDER
    if os.path.exists(SHELL):
        old = open(SHELL, encoding='utf-8').read()
        m = re.search(r'^var BLOB = .*$', old, re.M)
        if m and '"ct":""' not in m.group(0) and 'ct:""' not in m.group(0):
            blob = m.group(0)
            print('  kept the existing encrypted blob')
    return '''<!DOCTYPE html>
<html lang="en">
<head>
''' + HEAD.format(title='Revision Worksheet 1 &middot; Ready for the CAT &mdash; Answers | Space',
                  caveat='family=Caveat:wght@500;700&',
                  css='<link rel="stylesheet" href="../../assets/css/tokens.css">\n'
                      '<link rel="stylesheet" href="../../assets/css/solutions.css">\n'
                      '<link rel="stylesheet" href="../../assets/css/worksheet.css">\n') + '''
</head>
<body class="solutions-page theme-space">

<div class="hero" id="hero">
  <a class="back-btn" href="index.html">&#8592; Back to unit</a>
  <div class="unit-tag">Teacher Copy &middot; Confidential</div>
  <h1>Revision Worksheet 1 &mdash; Answers</h1>
  <p class="sub">The Revision 1 worksheet with model answers and marking guidance written into it, ready to print as a marking copy.</p>
  <div class="meta-row">
    <span>Revision 1</span><span>&middot;</span>
    <span>11 parts</span><span>&middot;</span>
    <span>34 marks where the CAT awards them</span><span>&middot;</span>
    <span>Victorian Curriculum F&ndash;10 v2.0</span>
  </div>
  <div class="teacher-note">
    <strong>How to use:</strong> answers come from the Revision 1 slides, so this copy marks what the class was actually shown. Model wording is not the only acceptable wording &mdash; award marks for any response carrying the same point. Red italic notes give the mark split and the common errors. The blank student copy is at <em>worksheet-revision1.html</em>.
  </div>
</div>

<div class="lockscreen" id="lock">
  <div class="lock-icon">&#128273;</div>
  <h2>Staff access only</h2>
  <p>This page contains the answers. Enter the staff password to view it.</p>
  <form id="unlockForm">
    <input id="pw" type="password" autocomplete="off" placeholder="Password" autofocus />
    <button type="submit">Unlock</button>
  </form>
  <p class="err" id="err"></p>
</div>
<div id="content"></div>

<script>
''' + blob + '''
(function(){
  var b64 = function(s){var bin=atob(s);var a=new Uint8Array(bin.length);for(var i=0;i<bin.length;i++)a[i]=bin.charCodeAt(i);return a;};
  /* v2 blob: the payload is encrypted once under a random content key, and
     that key is wrapped separately under each password the page accepts.
     Try each wrapper; the first that opens gives us both the content key
     and which audience just unlocked. Reading BLOB.salt/BLOB.iter here --
     the old single-layer shape -- answers "Incorrect password" to every
     password, because neither exists on a v2 blob. */
  async function derive(pw, salt, iter){
    var baseKey = await crypto.subtle.importKey("raw", new TextEncoder().encode(pw),
      {name:"PBKDF2"}, false, ["deriveKey"]);
    return crypto.subtle.deriveKey(
      {name:"PBKDF2", salt:b64(salt), iterations:iter, hash:"SHA-256"},
      baseKey, {name:"AES-GCM", length:256}, false, ["decrypt"]);
  }
  async function unlock(pw){
    if(!BLOB.ct) throw new Error("no payload");
    for (var i = 0; i < BLOB.keys.length; i++){
      var k = BLOB.keys[i], raw;
      try {
        raw = await crypto.subtle.decrypt({name:"AES-GCM", iv:b64(k.iv)},
                                          await derive(pw, k.salt, k.iter), b64(k.ct));
      } catch (e) { continue; }
      var ckey = await crypto.subtle.importKey("raw", raw, {name:"AES-GCM"},
                                               false, ["decrypt"]);
      var pt = await crypto.subtle.decrypt({name:"AES-GCM", iv:b64(BLOB.iv)},
                                           ckey, b64(BLOB.ct));
      return { role: k.role, html: new TextDecoder().decode(pt) };
    }
    throw new Error("bad password");
  }

  /* Unlocked with the student password: this is revision material, not a
     confidential teacher document, so drop the staff framing. The content
     is identical -- only the labelling changes. */
  function softenForStudents(){
    var tag = document.querySelector(".unit-tag");
    if (tag) tag.textContent = "Answer key";
    document.querySelectorAll(".ws-tag").forEach(function(t){
      t.textContent = "Year 7\\u20138 Science \\u00b7 Space \\u00b7 Answer key";
    });
  }

  var form=document.getElementById("unlockForm");
  form.addEventListener("submit",async function(e){
    e.preventDefault();
    var err=document.getElementById("err");
    err.textContent="";
    try{
      var res=await unlock(document.getElementById("pw").value);
      document.getElementById("content").innerHTML=res.html;
      document.body.dataset.role=res.role;
      if(res.role==="student") softenForStudents();
      document.getElementById("lock").style.display="none";
      document.getElementById("hero").style.display="none";
      /* the payload is worksheet markup, so hand the page over to
         worksheet.css -- solutions.css ships a * reset that would
         otherwise out-specify the sheet layout (same trick as rubric.html) */
      document.body.className="worksheet-page theme-space";
      window.scrollTo(0,0);
    }catch(ex){
      err.textContent = BLOB.ct
        ? "Incorrect password. Try again."
        : "This page has no answers in it yet \\u2014 the payload has not been encrypted.";
      document.getElementById("pw").value="";
      document.getElementById("pw").focus();
    }
  });
})();
</script>
</body>
</html>
'''


# --------------------------------------------------------- verification

def unfill(payload):
    """Strip the answer overlay back off, mechanically.

    The result must be the student sheet's question markup exactly. That
    is the check worth having: it catches an answer that silently replaced
    question wording, a question dropped from one copy, and a `.lines`
    block whose data-lines changed — none of which a count would see."""
    s = payload
    # written-in answers and marking notes come straight out
    s = re.sub(r'<span class="wsa-in">.*?</span>', '', s)
    s = re.sub(r'<span class="wsa-note">.*?</span>', '', s)
    # a written-on block goes back to empty ruled space
    s = re.sub(r'<div class="lines filled" data-lines="(\d+)">.*?</div>',
               lambda m: f'<div class="lines" data-lines="{m.group(1)}"></div>', s)
    # the model diagram goes back to the box the student draws in
    s = re.sub(r'<figure class="ws-fig" data-h="lg">'
               + re.escape(FIG['model'][0])
               + r'<figcaption>Model diagram.*?</figcaption></figure>',
               '<div class="drawbox" data-h="lg"></div>', s, flags=re.S)
    return s


def verify(student, payload):
    def body(page):
        return '\n'.join(re.findall(r'  <section class="part">.*?\n  </section>',
                                    page, re.S))

    want, got = body(student), unfill(body(payload))
    if want != got:
        import difflib
        d = list(difflib.unified_diff(want.split('\n'), got.split('\n'),
                                      'student', 'answers-unfilled', n=1, lineterm=''))
        raise AssertionError('stripping the overlay off the answer copy does not '
                             'give the student sheet back:\n' + '\n'.join(d[:40]))

    # Every slot the student writes in is filled, with two deliberate
    # exceptions: the exit self-rating column (their own judgement) and
    # the Score box (they mark it themselves).
    pb = body(payload)
    slots = {
        'inline blanks':  (len(re.findall(r'<span class="blank', body(student))),
                           len(re.findall(r'<span class="blank[^>]*><span class="wsa-in">', pb))),
        'ruled blocks':   (len(re.findall(r'<div class="lines"', body(student))),
                           len(re.findall(r'<div class="lines filled"', pb))),
        'drawbox':        (len(re.findall(r'<div class="drawbox"', body(student))),
                           len(re.findall(r'class="ws-fig" data-h="lg"', pb))),
    }
    for what, (n_student, n_filled) in slots.items():
        assert n_student == n_filled, \
            f'{what}: student sheet has {n_student}, answer copy fills {n_filled}'

    cells_student = len(re.findall(r'<td class="fill">', body(student)))
    cells_filled = len(re.findall(r'<td class="fill"><span class="wsa-in">', pb))
    exit_cells = len(RATE_ROWS)
    assert cells_student - cells_filled == exit_cells, (
        f'table cells: {cells_student} on the student sheet, {cells_filled} filled, '
        f'expected exactly {exit_cells} left blank (the exit self-rating column)')

    print(f'  verified: overlay strips back to the student sheet exactly; '
          f'{sum(v[1] for v in slots.values()) + cells_filled} answer slots filled, '
          f'{exit_cells} left blank on purpose')


# ------------------------------------------------------------------- main

def build(answers):
    global ANSWERS
    ANSWERS = answers
    return parts()


def main(argv):
    want = set(a.lstrip('-') for a in argv[1:]) or {'student'}
    if 'both' in want:
        want = {'student', 'answers'}

    if 'student' in want:
        page = student_page(build(False))
        open(DST, 'w', encoding='utf-8', newline='').write(page)
        print(f'wrote {DST}\n  {len(page):,} chars')
        # The overlay must never reach the student copy: a leak here puts
        # the answers on the page every class prints from.
        for leak in ('wsa-in', 'wsa-note', 'lines filled', 'sheet staff', 'staff-flag'):
            assert leak not in page, f'answer overlay leaked into the student copy: {leak}'

    if 'answers' in want:
        pay = answer_payload(build(True))
        verify(student_page(build(False)), pay)
        open(PAYLOAD, 'w', encoding='utf-8', newline='').write(pay)
        shell = answer_shell()
        open(SHELL, 'w', encoding='utf-8', newline='').write(shell)
        print(f'wrote {PAYLOAD}\n  {len(pay):,} chars, '
              f'{pay.count("wsa-in")} written-in answers, '
              f'{pay.count("lines filled")} written-on line blocks, '
              f'{pay.count("wsa-note")} marking notes')
        print(f'wrote {SHELL}\n  {len(shell):,} chars'
              + ('  [PLACEHOLDER BLOB — encrypt the payload through '
                 'tools/staff-crypt.html]' if PLACEHOLDER in shell else ''))


if __name__ == '__main__':
    main(sys.argv)
