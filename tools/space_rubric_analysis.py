# Analysis tab for the Year 7 Space CAT 5 rubric.
# Spliced in by build_space_rubric.py (add_analysis), after to_marks().
#
# Reads only what the marking grid already holds — nothing is stored. A
# student counts as "marked" once they have one mark (started()), and a part
# counts once anyone has a mark in it (COLS_MARKED), the same rules the grid
# uses for "not attempted". Facility counts a blank as 0: a skipped part is a
# part the class didn't get, and the not-attempted column says how much of
# the gap is skipping.
#
# Colour: the band charts use --chart-band-0..4, a chart-only version of the
# band scale (tokens.css). The cell tints --band0..4 are pale backgrounds and
# fail as fills: bands 0–2 sit within dE 3.3 of each other. The chart ramp is
# one hue stepping evenly in lightness (band 0 a warm near-white), validated
# with the dataviz skill's validator: adjacent dE >= 15.5 normal vision,
# >= 12.9 under CVD. Bands 0 and 1 are under 3:1 against the page, so every
# segment carries its count and a table view sits underneath.

ANALYSIS_TAB = ('    <button class="tab" role="tab" data-panel="analysis" id="tab-analysis" '
                'aria-controls="p-analysis" aria-selected="false">Analysis</button>\n')

ANALYSIS_PANEL = '''<!-- ============ ANALYSIS ============ -->
<section class="panel" id="p-analysis" role="tabpanel" aria-labelledby="tab-analysis" tabindex="0">
  <div class="card">
    <div class="card-head">
      <div><h2>Class analysis</h2><p>How the class went on the test, worked out from the marks in the grid. It updates as you mark, and only counts students with at least one mark entered.</p></div>
      <div class="an-actions">
        <button class="btn ghost small" id="btnAnCsv">Download question analysis (CSV)</button>
        <button class="btn small" id="btnAnPrint">Print analysis</button>
      </div>
    </div>
    <div class="card-body"><div id="anPane"></div></div>
  </div>
</section>

'''

ANALYSIS_CSS = '''
/* ---- analysis tab ---- */
body.rubric-page{
  --cb0: var(--c-chart-band-0); --cb1: var(--c-chart-band-1); --cb2: var(--c-chart-band-2);
  --cb3: var(--c-chart-band-3); --cb4: var(--c-chart-band-4);
}
.an-actions{display:flex;gap:8px;flex-wrap:wrap;align-items:flex-start}
.an-print-title{display:none}
.an-tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin-bottom:22px}
.an-tile{border:1px solid var(--rule);border-radius:8px;padding:10px 12px;background:var(--surface)}
.an-tile .k{font-size:10.5px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--ink-faint)}
.an-tile .v{font-family:var(--display);font-size:24px;font-weight:700;line-height:1.15;margin-top:4px;color:var(--ink);font-variant-numeric:tabular-nums}
.an-tile .s{font-size:12px;color:var(--ink-soft);margin-top:2px}
.an-sec{margin:0 0 26px;break-inside:avoid}
.an-sec h3{font-family:var(--display);font-size:17px;margin:0 0 2px;color:var(--ink)}
.an-sec .an-sub{font-size:12.5px;color:var(--ink-faint);margin:0 0 10px;max-width:75ch}
.an-note{font-size:12.5px;color:var(--ink-soft);background:var(--tint-soft);border:1px solid var(--rule);border-radius:6px;padding:8px 10px;margin:0 0 16px}
.an-hist{width:100%;max-width:720px;height:auto;display:block}
.an-hist .bar{fill:var(--myrtle)}
.an-hist .hit{fill:transparent;cursor:default}
.an-hist text{font-family:var(--body);fill:var(--ink-soft);font-size:11px}
.an-hist text.cnt{fill:var(--ink);font-weight:700;font-size:12px}
.an-hist .base{stroke:var(--rule-strong);stroke-width:1}
.an-hist .mean{stroke:var(--ink);stroke-width:1.5;stroke-dasharray:4 3}
.an-hist text.meanlab{fill:var(--ink);font-weight:700}
/* strand bands: 100% stacked rows */
.an-legend{display:flex;flex-wrap:wrap;gap:6px 14px;font-size:12px;color:var(--ink-soft);margin:0 0 10px}
.an-legend span{display:inline-flex;align-items:center;gap:6px}
.an-legend i{width:14px;height:14px;border-radius:3px;display:inline-block;border:1px solid var(--rule-strong)}
.an-rows{display:grid;grid-template-columns:minmax(180px,300px) 1fr 70px;gap:8px 14px;align-items:center}
.an-rows .nm{font-size:12.5px;line-height:1.3;color:var(--ink)}
.an-rows .nm small{display:block;color:var(--ink-faint);font-size:11px}
.an-rows .mb{font-size:12px;color:var(--ink-soft);text-align:right;font-variant-numeric:tabular-nums}
.an-rows .mb b{color:var(--ink);font-size:13px}
.an-rows .sep{grid-column:1/-1;border-top:1px solid var(--rule);margin:2px 0}
.an-stack{display:flex;height:26px;gap:2px}
.an-stack .seg{display:flex;align-items:center;justify-content:center;font-size:11.5px;font-weight:700;min-width:0;
  border-radius:0;box-shadow:inset 0 0 0 1px color-mix(in srgb, var(--ink) 14%, transparent);overflow:hidden;white-space:nowrap;outline-offset:1px}
.an-stack .seg:first-child{border-radius:4px 0 0 4px} .an-stack .seg:last-child{border-radius:0 4px 4px 0}
.an-stack .seg:only-child{border-radius:4px}
.an-stack .seg.c0{background:var(--cb0);color:var(--ink)} .an-stack .seg.c1{background:var(--cb1);color:var(--ink)}
.an-stack .seg.c2{background:var(--cb2);color:var(--ink)} .an-stack .seg.c3{background:var(--cb3);color:var(--c-white)}
.an-stack .seg.c4{background:var(--cb4);color:var(--c-white)}
.an-stack .seg:hover,.an-stack .seg:focus{filter:brightness(.93);outline:2px solid var(--ink)}
.an-legend i.c0{background:var(--cb0)} .an-legend i.c1{background:var(--cb1)} .an-legend i.c2{background:var(--cb2)}
.an-legend i.c3{background:var(--cb3)} .an-legend i.c4{background:var(--cb4)}
details.an-table{margin-top:10px;font-size:12.5px}
details.an-table summary{cursor:pointer;color:var(--myrtle-dark);font-weight:600}
table.an-t{border-collapse:collapse;width:100%;margin-top:8px;font-size:12.5px;font-variant-numeric:tabular-nums}
table.an-t th,table.an-t td{border-bottom:1px solid var(--rule);padding:6px 8px;text-align:left;vertical-align:middle}
table.an-t th{font-size:10.5px;letter-spacing:.07em;text-transform:uppercase;color:var(--ink-soft);background:var(--tint-soft);font-weight:700}
table.an-t td.n,table.an-t th.n{text-align:right}
table.an-t tr.pstart td{border-top:2px solid var(--rule-strong)}
table.an-t td.q{font-family:var(--mono);font-size:12px;white-space:nowrap}
table.an-t td.lab{color:var(--ink);min-width:220px}
.an-fac{display:flex;align-items:center;gap:8px;min-width:170px}
.an-fac .track{flex:1;height:10px;background:var(--tint-soft);border-radius:0 4px 4px 0;position:relative;box-shadow:inset 0 0 0 1px var(--rule)}
.an-fac .fill{position:absolute;left:0;top:0;bottom:0;background:var(--myrtle);border-radius:0 4px 4px 0}
.an-fac .half{position:absolute;left:50%;top:-3px;bottom:-3px;border-left:1px dashed var(--ink-faint)}
.an-fac b{width:38px;text-align:right;font-size:12.5px;color:var(--ink)}
.an-flag{display:inline-block;font-size:10.5px;font-weight:700;letter-spacing:.04em;padding:2px 7px;border-radius:10px;white-space:nowrap;margin:1px 4px 1px 0}
.an-flag.re{background:var(--red-soft);color:var(--red);border:1px solid color-mix(in srgb, var(--red) 40%, transparent)}
.an-flag.sk{background:var(--tint-soft);color:var(--ink-soft);border:1px solid var(--rule-strong)}
.an-sort{display:inline-flex;border:1px solid var(--rule-strong);border-radius:6px;overflow:hidden;margin:0 0 8px}
.an-sort button{border:0;background:var(--surface);padding:5px 10px;font:inherit;font-size:12px;color:var(--ink-soft);cursor:pointer}
.an-sort button[aria-pressed="true"]{background:var(--myrtle);color:var(--c-white)}
.an-tablewrap{overflow-x:auto}
#anTip{position:fixed;z-index:80;pointer-events:none;background:var(--ink);color:var(--c-white);font-size:12px;line-height:1.35;
  padding:7px 9px;border-radius:6px;max-width:300px;box-shadow:0 4px 14px rgba(0,0,0,.18);display:none}
#anTip b{display:block;margin-bottom:2px}
@media (max-width:700px){.an-rows{grid-template-columns:1fr 54px}.an-rows .nm{grid-column:1/-1}}
@media print{
  .an-actions,.an-sort,#anTip{display:none!important}
  .an-print-title{display:block;font-family:var(--display);font-size:18px;margin:0 0 4px}
  details.an-table{display:none}
  /* sections may break (the question table is two pages); their parts may not */
  .an-sec{break-inside:auto}
  .an-sec h3,.an-sub,.an-tiles,.an-hist,.an-legend,.an-rows{break-inside:avoid;page-break-inside:avoid}
  .an-sec h3{break-after:avoid}
  /* the screen wrapper scrolls; on paper it would clip the right-hand columns */
  .an-tablewrap{overflow:visible}
  table.an-t{font-size:9px}
  table.an-t th,table.an-t td{padding:3px 5px}
  table.an-t td.lab{min-width:0}
  .an-fac{min-width:90px}
  .an-fac b{width:30px;font-size:9px}
  table.an-t tr{break-inside:avoid}
}
'''

ANALYSIS_JS = r'''
/* ============================ RENDER: analysis ============================ */
let anSort = "paper";
const pct = (n, d) => d ? Math.round(100 * n / d) : 0;
const median = a => { if(!a.length) return null; const s = [...a].sort((x,y)=>x-y), m = s.length >> 1;
  return s.length % 2 ? s[m] : (s[m-1] + s[m]) / 2; };
const round1 = v => Math.round(v * 10) / 10;

/* one row per criterion, over the students who have been marked */
function questionStats(marked){
  return CRITERIA.map((c, ci) => {
    const colOn = COLS_MARKED.has(c.id);
    let sum = 0, done = 0, na = 0, entered = 0;
    marked.forEach(st => {
      if(hasMark(st, c.id)){ sum += st.q[c.id]; entered++; }
      if(isDone(st, c.id)) done++;
      if(isNotAtt(st, c.id)) na++;
    });
    const n = marked.length;
    return {c, ci, colOn, n, entered, na, mean: n ? sum / n : 0,
            fac: colOn && n ? sum / (n * c.max) : null,
            donePct: colOn ? pct(done, n) : null, naPct: colOn ? pct(na, n) : null};
  });
}

function anTile(k, v, s){
  return '<div class="an-tile"><div class="k">'+k+'</div><div class="v">'+v+'</div>'+(s ? '<div class="s">'+s+'</div>' : '')+'</div>';
}

function histSVG(totals){
  /* ten bins of five marks; the last (45–50) is closed so 50 has a home */
  const bins = Array.from({length:10}, (_, i) => ({lo:i*5, hi:i===9 ? 50 : i*5+4.5, names:[]}));
  totals.forEach(t => bins[Math.min(9, Math.floor(t.v / 5))].names.push(t.name + " (" + fmtMark(t.v) + ")"));
  const W = 720, H = 230, L = 14, R = 14, T = 26, B = 34;
  const bw = (W - L - R) / 10, max = Math.max(1, ...bins.map(b => b.names.length));
  const y = v => T + (H - T - B) * (1 - v / max);
  let h = '<svg class="an-hist" viewBox="0 0 '+W+' '+H+'" role="img" aria-label="Number of students in each five-mark band of the total score">';
  bins.forEach((b, i) => {
    const x = L + i * bw + 1, w = bw - 2, n = b.names.length, y0 = H - B;
    const lab = (i===9 ? "45–50" : b.lo + "–" + (b.lo+4));
    const tip = '<b>' + lab + ' marks · ' + n + ' student' + (n===1?'':'s') + '</b>' + esc(b.names.join(", "));
    if(n){
      const yt = y(n), r = Math.min(4, (y0 - yt) / 2);
      /* rounded data-end at the top, square at the baseline */
      h += '<path class="bar" d="M'+x+','+y0+' V'+(yt+r)+' Q'+x+','+yt+' '+(x+r)+','+yt+' H'+(x+w-r)+' Q'+(x+w)+','+yt+' '+(x+w)+','+(yt+r)+' V'+y0+' Z"/>';
      h += '<text class="cnt" x="'+(x+w/2)+'" y="'+(yt-6)+'" text-anchor="middle">'+n+'</text>';
    }
    h += '<rect class="hit" x="'+(x-1)+'" y="'+T+'" width="'+(w+2)+'" height="'+(H-T-B)+'" data-tip="'+esc(tip)+'" tabindex="0" aria-label="'+esc(lab+" marks: "+n+" students")+'"/>';
    h += '<text x="'+(x+w/2)+'" y="'+(H-B+16)+'" text-anchor="middle">'+lab+'</text>';
  });
  h += '<line class="base" x1="'+L+'" x2="'+(W-R)+'" y1="'+(H-B)+'" y2="'+(H-B)+'"/>';
  if(totals.length){
    const mean = totals.reduce((a,t) => a + t.v, 0) / totals.length;
    const mx = L + (W - L - R) * Math.min(mean, 50) / 50;
    h += '<line class="mean" x1="'+mx+'" x2="'+mx+'" y1="'+(T-12)+'" y2="'+(H-B)+'"/>';
    const anchor = mx > W - 120 ? "end" : "start", dx = anchor === "end" ? -5 : 5;
    h += '<text class="meanlab" x="'+(mx+dx)+'" y="'+(T-4)+'" text-anchor="'+anchor+'">class mean '+round1(mean)+'</text>';
  }
  h += '<text x="'+(W/2)+'" y="'+(H-2)+'" text-anchor="middle">Total mark out of '+MAX_TOTAL+'</text>';
  return h + '</svg>';
}

function bandLabel(b){ return b === 0 ? state.band0 : state.bandLabels[b-1]; }

function stackRow(name, sub, counts, names, maxB, meanTxt){
  const n = counts.reduce((a,b) => a + b, 0);
  let bar = '<div class="an-stack">';
  counts.forEach((k, b) => {
    if(b > maxB || !k) return;
    const tip = '<b>Band ' + b + ' · ' + esc(bandLabel(b)) + ' — ' + k + ' of ' + n + '</b>' + esc(names[b].join(", "));
    bar += '<div class="seg c'+b+'" style="flex:'+k+' 1 0" data-tip="'+esc(tip)+'" tabindex="0" aria-label="'
         + esc(name+", band "+b+": "+k+" students")+'">'+k+'</div>';
  });
  bar += '</div>';
  return '<div class="nm">'+esc(name)+(sub ? '<small>'+esc(sub)+'</small>' : '')+'</div>'+bar
       + '<div class="mb">'+meanTxt+'</div>';
}

function renderAnalysis(){
  const pane = $("#anPane");
  if(!pane) return;
  const all = state.students, marked = all.filter(started);
  if(!marked.length){
    pane.innerHTML = '<div class="empty"><strong>Nothing to analyse yet</strong>Enter marks on the Mark tab and the class picture builds here as you go.</div>';
    return;
  }
  const qs = questionStats(marked);
  const live = qs.filter(r => r.colOn);
  const unmarkedCols = qs.length - live.length;
  const totals = marked.map(st => ({name: st.name, v: rawTotal(st)}));
  const vals = totals.map(t => t.v);
  const mean = vals.reduce((a,b) => a + b, 0) / vals.length;
  const naCells = live.reduce((a, r) => a + r.na, 0);
  const naOf = live.length * marked.length;

  let h = '<div class="an-print-title">'+esc(state.meta.task || "Astronomy Test (CAT 5)")+' — class analysis'
        + (state.meta.cls ? ' · '+esc(state.meta.cls) : '')+'</div>';
  if(marked.length < all.length || unmarkedCols){
    h += '<div class="an-note">'
       + (marked.length < all.length ? (all.length - marked.length) + ' of ' + all.length + ' students have no marks yet and are left out. ' : '')
       + (unmarkedCols ? unmarkedCols + ' of ' + qs.length + ' parts have no marks for anyone yet, so totals are not final.' : '')
       + '</div>';
  }
  h += '<div class="an-tiles">'
     + anTile("Students marked", marked.length, "of " + all.length + " in the class")
     + anTile("Class mean", round1(mean) + "<span style='font-size:14px;color:var(--ink-faint)'> / "+MAX_TOTAL+"</span>", pct(mean, MAX_TOTAL) + "% of the marks")
     + anTile("Median", fmtMark(median(vals)), "half the class at or above this")
     + anTile("Range", fmtMark(Math.min(...vals)) + "–" + fmtMark(Math.max(...vals)), "lowest to highest total")
     + anTile("Not attempted", pct(naCells, naOf) + "%", naCells + " part" + (naCells===1?"":"s") + " left blank across the class")
     + '</div>';

  h += '<div class="an-sec"><h3>Spread of total marks</h3>'
     + '<p class="an-sub">How many students landed in each five-mark band. Hover or focus a bar to see who is in it.</p>'
     + histSVG(totals) + '</div>';

  /* ---- strands ---- */
  h += '<div class="an-sec"><h3>Bands by strand</h3>'
     + '<p class="an-sub">Where the class sits on each strand of the rubric, after the developmental penalty. Strands with a weak first band are the ones to reteach from the start.</p>'
     + '<div class="an-legend">' + [0,1,2,3,4].map(b => '<span><i class="c'+b+'"></i>'+b+' · '+esc(bandLabel(b))+'</span>').join("") + '</div>'
     + '<div class="an-rows">';
  const tableRows = [];
  STRANDS.forEach(s => {
    const counts = [0,0,0,0,0], names = [[],[],[],[],[]];
    let sum = 0, n = 0;
    marked.forEach(st => { const m = st.marks[s.id]; if(Number.isInteger(m)){ counts[m]++; names[m].push(st.name); sum += m; n++; } });
    const meanB = n ? round1(sum / n) : null;
    h += stackRow(s.name, s.sub + " · " + s.weight + " marks", counts, names, maxBandOf(s),
                  meanB === null ? "—" : "<b>" + meanB + "</b> / " + maxBandOf(s));
    tableRows.push([s.name, counts, maxBandOf(s), meanB]);
  });
  /* overall level, on the same 0–4 scale */
  const oc = [0,0,0,0,0], on = [[],[],[],[],[]];
  marked.forEach(st => { const lv = overallLevel(pctOf(st)); if(lv.key >= 0){ oc[lv.key]++; on[lv.key].push(st.name); } });
  h += '<div class="sep"></div>' + stackRow("Overall level", "weighted by each strand's marks", oc, on, 4, "");
  tableRows.push(["Overall level", oc, 4, null]);
  h += '</div>';
  h += '<details class="an-table"><summary>Show as a table</summary><table class="an-t"><thead><tr><th>Strand</th>'
     + [0,1,2,3,4].map(b => '<th class="n">Band '+b+'</th>').join("") + '<th class="n">Mean</th></tr></thead><tbody>'
     + tableRows.map(r => '<tr><td>'+esc(r[0])+'</td>' + r[1].map((k,b) => '<td class="n">'+(b > r[2] ? '—' : k)+'</td>').join("")
       + '<td class="n">'+(r[3] === null ? '' : r[3] + ' / ' + r[2])+'</td></tr>').join("")
     + '</tbody></table></details></div>';

  /* ---- questions ---- */
  const rows = anSort === "low"
    ? [...qs].sort((a,b) => (a.fac === null) - (b.fac === null) || (a.fac||0) - (b.fac||0))
    : MARK_COLS.map(ci => qs[ci]);
  h += '<div class="an-sec"><h3>Question by question</h3>'
     + '<p class="an-sub"><b>Facility</b> is the share of the available marks the class earned (a blank counts as 0); the dashed line is half. '
     + '<b>Demonstrated</b> is how many scored at least half, which is what counts towards a band. '
     + 'Parts under 50% facility are flagged to reteach; parts a quarter or more of the class skipped are flagged as skipped.</p>'
     + '<div class="an-sort" role="group" aria-label="Sort questions">'
     + '<button type="button" data-sort="paper" aria-pressed="'+(anSort==="paper")+'">Paper order</button>'
     + '<button type="button" data-sort="low" aria-pressed="'+(anSort==="low")+'">Lowest facility first</button></div>'
     + '<div class="an-tablewrap"><table class="an-t"><thead><tr><th>Part</th><th>Question</th><th>What it asks for</th>'
     + '<th class="n">Out of</th><th class="n">Mean</th><th>Facility</th><th class="n">Demonstrated</th><th class="n">Not attempted</th><th>Flag</th></tr></thead><tbody>';
  let prevPart = null;
  rows.forEach(r => {
    const c = r.c, brk = anSort === "paper" && prevPart !== null && prevPart !== c.part;
    prevPart = c.part;
    if(!r.colOn){
      h += '<tr'+(brk?' class="pstart"':'')+'><td>'+c.part+'</td><td class="q">'+esc(qLabel(c))+'</td><td class="lab">'+esc(c.label)+'</td>'
         + '<td class="n">'+fmtMark(c.max)+'</td><td colspan="5" style="color:var(--ink-faint)">Not marked yet</td></tr>';
      return;
    }
    const f = Math.round(r.fac * 100);
    const flags = (f < 50 ? '<span class="an-flag re">Reteach</span>' : '') + (r.naPct >= 25 ? '<span class="an-flag sk">Often skipped</span>' : '');
    h += '<tr'+(brk?' class="pstart"':'')+'><td>'+c.part+'</td><td class="q">'+esc(qLabel(c))+'</td><td class="lab">'+esc(c.label)+'</td>'
       + '<td class="n">'+fmtMark(c.max)+'</td><td class="n">'+round1(r.mean)+'</td>'
       + '<td><div class="an-fac" data-tip="'+esc('<b>'+qLabel(c)+' · '+f+'% facility</b>Mean '+round1(r.mean)+' of '+fmtMark(c.max)+' across '+r.n+' students')+'">'
       + '<span class="track"><span class="fill" style="width:'+f+'%"></span><span class="half"></span></span><b>'+f+'%</b></div></td>'
       + '<td class="n">'+r.donePct+'%</td><td class="n">'+r.naPct+'%</td><td>'+flags+'</td></tr>';
  });
  h += '</tbody></table></div></div>';

  pane.innerHTML = h;
  pane.querySelectorAll(".an-sort button").forEach(b => b.onclick = () => { anSort = b.dataset.sort; renderAnalysis(); });
}

function exportAnalysisCSV(){
  const marked = state.students.filter(started);
  const qs = questionStats(marked);
  const head = ["Question","Part","What it asks for","Out of","Students marked","Mean","Facility %","Demonstrated %","Not attempted %"];
  const lines = [head.map(csvCell).join(",")];
  MARK_COLS.forEach(ci => { const r = qs[ci], c = r.c;
    lines.push([qLabel(c), c.part, c.label, fmtMark(c.max), r.n,
      r.colOn ? round1(r.mean) : "", r.colOn ? Math.round(r.fac*100) : "", r.colOn ? r.donePct : "", r.colOn ? r.naPct : ""].map(csvCell).join(","));
  });
  download((state.meta.cls||"class")+"-astronomy-analysis-"+stamp()+".csv", lines.join("\n"), "text/csv;charset=utf-8");
  toast("Question analysis downloaded");
}

/* one floating tooltip for every [data-tip] in the analysis tab, on hover and on focus */
(function wireAnalysisTip(){
  const tip = document.createElement("div"); tip.id = "anTip"; tip.setAttribute("role", "tooltip");
  document.body.appendChild(tip);
  const show = (el, x, y) => { tip.innerHTML = el.getAttribute("data-tip"); tip.style.display = "block";
    const r = tip.getBoundingClientRect();
    tip.style.left = Math.max(8, Math.min(window.innerWidth - r.width - 8, x + 12)) + "px";
    tip.style.top  = Math.max(8, (y + 16 + r.height > window.innerHeight ? y - r.height - 12 : y + 16)) + "px"; };
  const hide = () => { tip.style.display = "none"; };
  document.addEventListener("mousemove", e => {
    const el = e.target.closest && e.target.closest("#anPane [data-tip]");
    if(el) show(el, e.clientX, e.clientY); else hide();
  });
  document.addEventListener("focusin", e => {
    const el = e.target.closest && e.target.closest("#anPane [data-tip]");
    if(el){ const r = el.getBoundingClientRect(); show(el, r.left + r.width/2, r.bottom); } else hide();
  });
  document.addEventListener("scroll", hide, true);
})();
'''
