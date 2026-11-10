# A5 trial — Space Section 1 (workbook redesign)

A test of the A5 booklet approach before it touches the real booklet.
`../Space_Unit_Booklet_Yr7_8.tex` and its PDF are **not** modified.

```bash
cd year7-science/space/booklet/a5-test
python3 make_a5_test.py                      # writes Space_Section1_A5.tex from the master
python3 fill_a5.py Space_Section1_A5         # builds, then grows boxes to fill each page
```

- `make_a5_test.py` — slices Section 1 out of the master and applies the A5
  layout (see its docstring for every change). Fails if any word is lost.
- `fill_a5.py` — the Particle Model page filler with A5 geometry.
- `../art/lN-ink.pdf` — the ink lesson symbols, shared by the core and
  extension books. `tools/space_symbols.py` draws every symbol in colour (for
  the site) and ink (for the booklet) from one geometry; rerun it after a
  change.
- Headings are set in Outfit (`../fonts/Outfit-*.ttf`, OFL licence beside
  them), the site's heading face. Body text stays Lato.

Print `Space_Section1_A5.pdf` with the copier's **booklet** setting to test it.
