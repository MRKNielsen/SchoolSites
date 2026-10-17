# Image sources — Year 7 Space

Deck 1 references three photographs from this folder. They're stored locally
rather than hotlinked so the deck works without a network connection in class
and doesn't break if a NASA URL moves. All three are public domain.

Lesson 4 adds seven photographs of material we hold in the department — see
"Williams specimen photographs" below. Every other deck is inline SVG.

| Filename | Used on | Credit |
|---|---|---|
| `moon-galileo.jpg` | Lesson 1 — The Moon | NASA/JPL, Galileo spacecraft, 1992 |
| `sun-sdo-193.jpg` | Lesson 1 — The Sun | NASA/SDO, extreme UV 193 Å |
| `milky-way-planck.jpg` | Lesson 1 — First Nations: sky as living Country | ESA/NASA/JPL-Caltech, Planck |

## Fetching them

Run from **this folder** (`year7-science/space/img/`).

PowerShell:

```powershell
iwr "https://images-assets.nasa.gov/image/PIA00405/PIA00405~large.jpg" -OutFile moon-galileo.jpg
iwr "https://sdo.gsfc.nasa.gov/assets/img/latest/latest_1024_0193.jpg"  -OutFile sun-sdo-193.jpg
iwr "https://images-assets.nasa.gov/image/PIA18912/PIA18912~large.jpg"  -OutFile milky-way-planck.jpg
```

Git Bash / WSL:

```bash
curl -L -o moon-galileo.jpg     "https://images-assets.nasa.gov/image/PIA00405/PIA00405~large.jpg"
curl -L -o sun-sdo-193.jpg      "https://sdo.gsfc.nasa.gov/assets/img/latest/latest_1024_0193.jpg"
curl -L -o milky-way-planck.jpg "https://images-assets.nasa.gov/image/PIA18912/PIA18912~large.jpg"
```

Then open `deck1.html` and check slides 5 (The Moon), 7 (The Sun) and 10
(First Nations) — if all three show, you're done.

## Two notes

**Use `~large.jpg`, not `~orig.jpg`.** The NASA image library serves an
`~orig` version of each asset that can run to tens of megabytes. The slides
cap these at 22–30vh, so `~large` is already more resolution than a projector
can show, and it keeps the repo small. (An earlier version of this file
pointed at `~orig` for the Moon — that was a mistake.)

**`sun-sdo-193.jpg` is a snapshot of a live feed.** The SDO URL always returns
the most recent 193 Å image, so what you download is whatever the Sun looked
like that day. The deck used to hotlink it, which meant the Sun slide showed a
different image every lesson. Re-run that one command whenever you want a
fresher Sun — activity varies a lot across the solar cycle, and a shot with
visible coronal loops or a big active region teaches better than a quiet disc.

## Williams specimen photographs

Lesson 4 is built on material from **Prof. George E. Williams** (Department of
Earth Sciences, University of Adelaide), photographed and offered to the
school by his son **Stuart Williams** (Northcote High School), 20 Aug 2026.
**We hold the specimens** — they can be handled in class, which is the whole
point of the lesson.

| Filename | Shows |
|---|---|
| `poster-tidal-rhythmites.jpg` | Research poster: *Tidal deposits reveal Earth's past rotation rate — 400 days/year and 21.9 hours/day at 635 Ma* |
| `poster-acraman-1.jpg` | Research poster: *The Acraman asteroid impact, South Australia* (crater, shatter cone, satellite image) |
| `poster-acraman-2.jpg` | Second Acraman poster (Landsat, aeromagnetics, thin sections) |
| `acraman-shattered-dacite.jpg` | Shattered Yardea Dacite from the surrounds of the impact |
| `acraman-melted-dacite.jpg` | Melted dacite from beneath the impact point (sample WC-15Aiii) |
| `acraman-ejecta-breccia.jpg` | Dacite ejecta fragments, Flinders Ranges — ~300 km from Acraman |
| `acraman-fallout-sediment.jpg` | Flinders Ranges sediment disturbed by the impact, with dark fallout grains |

Extracted from the PDF portfolio Stuart emailed, at 200 dpi from the rendered
page rather than by pulling the embedded JPEGs — **the embedded images are
stored 180° from how the page displays them**, so extracting them directly
gives you upside-down rocks.

The four specimen photographs are matched to Stuart's descriptions by the
order he listed them in and by what is visible in each: chunky angular
fragments (shattered), smooth fine-grained pink (melted), clasts in a matrix
(ejecta breccia), parallel banding with dark grains (fallout in sediment).
**Check them against the physical labels before teaching** — sample WC-15Aiii
is the only one whose label is legible in the photograph.

These are not public domain. They are used here by permission for teaching at
Northcote High School, credited on-slide. Don't reuse them elsewhere without
asking Stuart.

Key figures from the rhythmite poster, which the lesson uses directly:

| | 635 Ma | Today |
|---|---|---|
| Solar days per lunar month | 30.5 ± 0.5 | 29.53 |
| Lunar months per year | 13.1 ± 0.1 | 12.37 |
| Solar days per year | 400 ± 7 | 365.24 |
| Length of solar day (hours) | 21.9 ± 0.4 | 24.00 |

Source: Williams, G.E. (2000). *Geological constraints on the Precambrian
history of Earth's rotation and the Moon's orbit.* Reviews of Geophysics 38,
37–59 (open access).
