# Image sources — Year 7 Space

The decks reference these three files locally so they work offline in class
and don't break if a URL moves. All three are NASA public domain.

Save them into this folder with exactly these filenames:

| Filename | Source | Used in |
|---|---|---|
| `moon-galileo.jpg` | https://images-assets.nasa.gov/image/PIA00405/PIA00405~orig.jpg | deck1 — The Moon |
| `milky-way-planck.jpg` | https://images-assets.nasa.gov/image/PIA18912/PIA18912~large.jpg | deck1 — First Nations: sky as living Country |
| `sun-sdo-193.jpg` | https://sdo.gsfc.nasa.gov/assets/img/latest/latest_1024_0193.jpg | deck1 — The Sun |

From this folder:

```bash
curl -L -o moon-galileo.jpg     "https://images-assets.nasa.gov/image/PIA00405/PIA00405~orig.jpg"
curl -L -o milky-way-planck.jpg "https://images-assets.nasa.gov/image/PIA18912/PIA18912~large.jpg"
curl -L -o sun-sdo-193.jpg      "https://sdo.gsfc.nasa.gov/assets/img/latest/latest_1024_0193.jpg"
```

`sun-sdo-193.jpg` is a **snapshot** of the Solar Dynamics Observatory's live
193 Å feed. The deck used to hotlink it, so the Sun slide showed a different
image every lesson. Re-run that last command whenever you want a fresher Sun.
