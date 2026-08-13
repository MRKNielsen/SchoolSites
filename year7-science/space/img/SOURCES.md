# Image sources — Year 7 Space

Deck 1 references three photographs from this folder. They're stored locally
rather than hotlinked so the deck works without a network connection in class
and doesn't break if a NASA URL moves. All three are public domain.

Nothing else in the unit uses photographs — decks 2–8 are entirely inline SVG.

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
