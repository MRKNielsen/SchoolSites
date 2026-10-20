#!/usr/bin/env python3
"""Build year7-science/space/worksheet-revision1.html — the fill-in sheet
that goes with revision1.html.

Rebuilt from the supplied PDF rather than embedded, so it matches the
unit's other eleven worksheets: worksheet.css, A4 print rules, the shared
question furniture, a nav entry and a Print button. The PDF stays beside
it as a download for anyone who wants the original file.

Figures come out of the deck (see figs.py) rather than being redrawn, so
the sheet and the slides can never show different diagrams.

Marks: the PDF marks some tasks and not others, because the unmarked ones
are practice rather than assessment. That is kept — `.marks` appears only
where the CAT would actually award them, and there is no sheet total,
since a total over a mixed sheet would mean nothing. The other worksheets
in this unit do carry totals; this one is deliberately different.
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
DST = os.path.join(os.path.dirname(HERE), 'year7-science', 'space',
                   'worksheet-revision1.html')
FIG = json.load(open(os.path.join(HERE, 'revision1_figs.json'), encoding='utf-8'))


def fig(name, i=0, h='md', label=''):
    return (f'<figure class="ws-fig" data-h="{h}">{FIG[name][i]}'
            + (f'<figcaption>{label}</figcaption>' if label else '')
            + '</figure>')


def lines(n):
    return f'<div class="lines" data-lines="{n}"></div>'


def q(num, body, marks=None):
    m = f'<span class="marks">{marks}</span>' if marks else ''
    return (f'    <div class="q"><span class="qn">{num}</span>\n'
            f'      <div class="qbody">{m}{body}</div>\n    </div>')


def part(label, title, body, marks=None):
    m = f'<span class="marks">{marks}</span>' if marks else ''
    return ('  <section class="part">\n'
            f'    <div class="part-head"><span class="part-label">{label}</span>'
            f'<span class="part-title">{title}</span>{m}</div>\n'
            + body + '\n  </section>\n')


PARTS = []

# 1 ---------------------------------------------------------------------
PARTS.append(part('1', 'Quick-fire eight <span class="pt-meta">Starter &middot; from memory, no booklet</span>',
    '\n'.join(q(i + 1, text + '<span class="blank lg"></span>') for i, text in enumerate([
        'How long does Earth take to spin once on its axis?',
        'How many days for Earth to travel once around the Sun?',
        'By how many degrees is Earth&rsquo;s axis tilted?',
        'How many days from one full Moon to the next?',
        'One astronomical unit (1&nbsp;AU) is how many kilometres?',
        'How far does light travel in one second?',
        'Which layer of the Sun do we see as its &ldquo;surface&rdquo;?',
        'Is Neptune a terrestrial planet, a gas giant or an ice giant?',
    ])) + '\n    <div class="infobox"><span class="lbl">Score</span><p>&nbsp;&nbsp;&nbsp;&nbsp;/ 8 &mdash; circle any you missed and come back to them.</p></div>'))

# 2 ---------------------------------------------------------------------
L2 = ('    <div class="chips"><span class="cl">Part A &middot; Earth</span>'
      '<span class="chip">Inner core</span><span class="chip">Outer core</span>'
      '<span class="chip">Mantle</span><span class="chip">Crust</span></div>\n'
      + '\n'.join(q(f'A{i+1}', text + '<span class="blank lg"></span>') for i, text in enumerate([
          'I&rsquo;m liquid iron and nickel, and my movement makes Earth&rsquo;s magnetic field.',
          'I&rsquo;m only 5&ndash;70&nbsp;km thick and I&rsquo;m broken into tectonic plates.',
          'I&rsquo;m solid iron and nickel at the very centre of the planet.',
          'I&rsquo;m semi-solid rock about 2,900&nbsp;km thick.']))
      + '\n    <div class="chips"><span class="cl">Part B &middot; The Sun</span>'
        '<span class="chip">Core</span><span class="chip">Radiative zone</span>'
        '<span class="chip">Convective zone</span><span class="chip">Photosphere</span>'
        '<span class="chip">Chromosphere</span><span class="chip">Corona</span></div>\n'
      + '\n'.join(q(f'B{i+1}', text + '<span class="blank lg"></span>') for i, text in enumerate([
          'I&rsquo;m the Sun&rsquo;s visible surface, where sunspots form.',
          'Nuclear fusion happens in me, at about 15 million&nbsp;&deg;C.',
          'I&rsquo;m the outermost layer, at over 1 million&nbsp;&deg;C.',
          'Energy takes about 100,000 years to cross me as light.',
          'I&rsquo;m the thin layer of atmosphere just above the visible surface.',
          'Hot plasma rises and sinks through me, carrying energy outward.']))
      + '\n    <div class="y8box"><span class="lbl">Challenge</span>'
        '<p>Write each set of layers in order, from the centre out.</p>'
        '<p><b>Earth</b>' + lines(1) + '</p><p><b>Sun</b>' + lines(1) + '</p></div>')
PARTS.append(part('2', 'Which layer am I? <span class="pt-meta">Layers &middot; pairs</span>', L2))

# 3 ---------------------------------------------------------------------
L3 = (f'    {fig("daynight", 0, "md", "Sunlight arrives from the right. P and Q are marked on Earth.")}\n'
      + '\n'.join([
          q(1, 'Which place, P or Q, is in daylight right now?<span class="blank lg"></span>', 1),
          q(2, 'Which place is having summer? Use the tilt of the axis to explain.' + lines(3), 2),
          q(3, 'Roughly which month of the year could this be?<span class="blank lg"></span>', 1),
          q(4, 'Fix this sentence: &ldquo;Earth revolves on its axis once every 24 hours.&rdquo;' + lines(2), 1),
      ]))
PARTS.append(part('3', 'Read the diagram: places P and Q <span class="pt-meta">Day, night and seasons &middot; on your own</span>', L3, '5 marks'))

# 4 ---------------------------------------------------------------------
L4 = (f'    {fig("orbit4", 0, "md", "Earth at four positions around the Sun. &bull; marks the North Pole.")}\n'
      + '\n'.join([
          q('a', 'At which position is Melbourne having summer?<span class="blank"></span>'),
          q('b', 'Follow the arrows. At which position is Melbourne having spring?<span class="blank"></span>'),
          q('c', 'At which two positions are day and night equal everywhere?<span class="blank"></span>'),
          q('d', 'Japan is in the Northern Hemisphere. At which position is Japan having winter?<span class="blank"></span>'),
          q('e', '&ldquo;Melbourne is cold in July because Earth is furthest from the Sun then.&rdquo; '
                 'Earth really <i>is</i> furthest in July. So what is wrong with this reasoning?' + lines(3)),
      ]))
PARTS.append(part('4', 'Earth&rsquo;s year in four positions <span class="pt-meta">Day, night and seasons &middot; pairs</span>', L4))

# 5 ---------------------------------------------------------------------
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
          q('a', 'Name the phase seen from Earth at: position 2<span class="blank"></span> '
                 'position 5<span class="blank"></span>'),
          q('b', 'Which drawing, (i) to (iv), shows the Moon at position 3 as seen from Melbourne?<span class="blank"></span>'),
          q('c', 'Which drawing shows the Moon at position 6 as seen from Melbourne?<span class="blank"></span>'),
          q('d', 'Name the phase seen from Earth at: position 1<span class="blank"></span> '
                 'position 4<span class="blank"></span>'),
          q('e', '&ldquo;The dark part of a crescent Moon is Earth&rsquo;s shadow.&rdquo; Correct this statement.' + lines(3)),
      ]))
PARTS.append(part('5', 'The Moon at positions 1 to 6 <span class="pt-meta">Moon phases &middot; on your own, then check</span>', L5))

# 6 ---------------------------------------------------------------------
L6 = ('    <figure class="ws-fig" data-h="sm">' + ''.join(FIG['tides'])
      + '<figcaption>(i) Sun &middot; Moon &middot; Earth &ensp; (ii) Moon at right angles &ensp; '
        '(iii) Sun &middot; Earth &middot; Moon &mdash; not to scale</figcaption></figure>\n'
      + '\n'.join([
          q(1, 'Which line-up(s) cause spring tides? Name the Moon&rsquo;s phase in each.' + lines(2), 2),
          q(2, 'Which causes neap tides? Why are neap tides smaller?' + lines(2), 2),
          q(3, 'There is a new Moon on 2 November. About when are the next neap tides?' + lines(1), 1),
          q(4, 'High tide at a beach is at 6&nbsp;am. When is the next high tide, and which motion causes it?' + lines(2), 2),
          q(5, 'If the Moon vanished, would the oceans stop having tides? Explain.' + lines(2), 2),
      ]))
PARTS.append(part('6', 'Three line-ups: spring or neap? <span class="pt-meta">Tides &middot; pairs</span>', L6, '9 marks'))

# 7 ---------------------------------------------------------------------
CALC = [
    ('How many times wider is the Sun than the Moon? Nearest whole number.', 2),
    ('Saturn is 9.54&nbsp;AU from the Sun. Calculate this distance in km.', 2),
    ('How long does sunlight take to reach Mars? Give your answer in seconds, then in minutes and seconds.', 2),
    ('How many times farther from the Sun is Neptune than Mars? Nearest whole number.', 2),
    ('<b>Challenge:</b> mission control radios an astronaut on the Moon, who replies instantly. '
     'What is the shortest wait between sending and hearing the reply?', 2),
]
L7 = ('    <div class="infobox"><span class="lbl">Data</span><p>Sun diameter 1,392,000&nbsp;km &middot; '
      'Moon diameter 3,474&nbsp;km &middot; Earth to Moon 384,400&nbsp;km &middot; '
      'Mars to Sun 228,000,000&nbsp;km &middot; Mars 1.52&nbsp;AU &middot; Saturn 9.54&nbsp;AU &middot; '
      'Neptune 30.1&nbsp;AU &middot; 1&nbsp;AU = 150,000,000&nbsp;km &middot; speed of light = 300,000&nbsp;km/s</p>'
      '<p><b>Every time:</b> write the rule &rarr; put the numbers in &rarr; calculate &rarr; '
      'answer with units, rounded as asked.</p></div>\n'
      + '\n'.join(q(i + 1, text + '<table class="wtbl"><tr><th>Rule and working</th>'
                                  '<th>Answer (with units)</th></tr>'
                                  '<tr><td class="fill"></td><td class="fill"></td></tr></table>', m)
                  for i, (text, m) in enumerate(CALC)))
PARTS.append(part('7', 'Your turn: five calculations <span class="pt-meta">Calculations &middot; show all working</span>', L7, '10 marks'))

# 8 ---------------------------------------------------------------------
L8 = '\n'.join([
    q(1, 'Put them in order from the Sun: Uranus &middot; Mars &middot; Saturn &middot; Mercury &middot; '
         'Neptune &middot; Earth &middot; Jupiter &middot; Venus'
         '<table class="wtbl"><tr>' + ''.join(f'<th>{i}</th>' for i in range(1, 9)) + '</tr>'
         '<tr>' + '<td class="fill"></td>' * 8 + '</tr></table>'
         '<p>My own mnemonic:</p>' + lines(1)),
    q(2, 'Odd one out: Mercury, Venus, Saturn, Mars. Which, and why?' + lines(2)),
    q(3, 'Who am I?<br>a) The first planet beyond the asteroid belt.<span class="blank lg"></span>'
         '<br>b) An ice giant, 7th from the Sun, spinning on my side.<span class="blank lg"></span>'
         '<br>c) The hottest planet, though not the closest to the Sun.<span class="blank lg"></span>'),
    q(4, '&ldquo;The asteroid belt is what&rsquo;s left of a planet that exploded.&rdquo; '
         'Give the scientific explanation instead.' + lines(3)),
    q(5, 'Where is the Kuiper Belt? Name a dwarf planet found there.' + lines(2)),
])
PARTS.append(part('8', 'Sort, classify, explain <span class="pt-meta">Solar system &middot; pairs</span>', L8))

# 9 ---------------------------------------------------------------------
L9 = ('    <div class="infobox"><span class="lbl">Sentence frame</span>'
      '<p>&ldquo;This happens because &hellip; This means that &hellip;&rdquo;</p></div>\n'
      + '\n'.join([
          q('A', '<b>Planet temperatures.</b> Mercury is closer to the Sun than Venus. Yet Mercury&rsquo;s '
                 'night side drops to &minus;180&nbsp;&deg;C, while Venus stays at about 465&nbsp;&deg;C '
                 'day and night. Explain why.' + lines(4), 2),
          q('B', '<b>Space debris.</b> A fleck of paint once chipped a window on the International Space '
                 'Station. Explain how something so tiny could do damage, and why the crew could not '
                 'steer around it.' + lines(4), 2),
          q('C', '<b>Sky knowledge.</b> A friend says the dark patches along the Milky Way are &ldquo;just '
                 'empty gaps&rdquo;. Correct them, and explain how Aboriginal astronomers use these dark '
                 'shapes as a calendar.' + lines(4), 2),
      ]))
PARTS.append(part('9', 'Explain it: two marks, two points, joined by &ldquo;because&rdquo; '
                       '<span class="pt-meta">Explain it &middot; on your own</span>', L9, '6 marks'))

# 10 --------------------------------------------------------------------
L10 = q(1, 'Japan is in the Northern Hemisphere. Using a labelled diagram, explain why Japan has its '
           'summer in June while Melbourne has its summer in December.'
           '<div class="drawbox" data-h="lg"></div>' + lines(4), 4)
PARTS.append(part('10', 'A four-mark diagram answer <span class="pt-meta">Draw and explain &middot; on your own</span>', L10, '4 marks'))

# exit ------------------------------------------------------------------
RATE = [('Layers of Earth and Sun', '&sect;1.2, &sect;1.4 &middot; p.3&ndash;5', 'name and order all 4 + 6 layers'),
        ('Day, night and seasons', '&sect;2 &middot; p.8&ndash;10', 'read an orbit diagram; explain tilt'),
        ('Moon phases', '&sect;3.1 &middot; p.11', 'name a phase; pick the Melbourne view'),
        ('Tides', '&sect;3.2 &middot; p.12&ndash;13', 'explain spring vs neap; two tides a day'),
        ('Calculations', '&sect;1.1, &sect;1.4, &sect;5.1', 'ratios, AU to km, light time, with working'),
        ('Solar system', '&sect;5 &middot; p.20&ndash;22', 'order and classify; explain the asteroid belt'),
        ('Moon, debris, sky knowledge', '&sect;1.3, &sect;6.3, &sect;7', 'explain each in two linked sentences')]
EXIT = ('    <p>Write <b>Confident</b>, <b>Shaky</b> or <b>Need help</b> next to each, then revise your two weakest.</p>\n'
        '    <table class="wtbl"><tr><th>Topic</th><th>Booklet</th><th>I can&hellip;</th><th>How I feel</th></tr>'
        + ''.join(f'<tr><td>{a}</td><td>{b}</td><td>{c}</td><td class="fill"></td></tr>' for a, b, c in RATE)
        + '</table>\n    <div class="infobox"><span class="lbl">Best practice before the CAT</span>'
          '<p>The booklet&rsquo;s &ldquo;Check your understanding&rdquo; questions for each topic above.</p></div>')
PARTS.append(part('!Exit', 'Rate yourself, then revise your two weakest', EXIT))

PAGE = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Revision Worksheet 1 &middot; Ready for the CAT | Space</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Bitter:wght@500;700;800&family=Source+Sans+3:ital,wght@0,400;0,600;0,700;1,400&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../../assets/css/tokens.css">
<link rel="stylesheet" href="../../assets/css/worksheet.css">
<link rel="stylesheet" href="../../assets/css/sitenav.css">
<script src="../../assets/js/sitenav.js" defer></script>
<link rel="icon" href="../../assets/icons/favicon.svg" type="image/svg+xml">
<link rel="icon" href="../../assets/icons/favicon.ico" sizes="32x32">
<link rel="apple-touch-icon" href="../../assets/icons/apple-touch-icon.png">
<link rel="manifest" href="../../site.webmanifest">
<meta name="theme-color" content="#24576f">
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

''' + '\n'.join(PARTS) + '''
  <div class="ws-foot">Year 7 Science &middot; Space &middot; Revision worksheet 1 &mdash; companion to the Revision 1 slides.</div>
</div>

</body>
</html>
'''

if __name__ == '__main__':
    open(DST, 'w', encoding='utf-8', newline='').write(PAGE)
    print(f'wrote {DST}\n  {len(PAGE):,} chars, {len(PARTS)} parts')
