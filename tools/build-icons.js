/* ============================================================
   build-icons.js — regenerate the site icon set from one source.

     node tools/build-icons.js          # writes the SVG variants
     node tools/build-icons.js --png    # also rasterises (needs ImageMagick)

   The mark: a treble clef inside an electron-orbit atom, in chalk on a
   chalk-blue board. Derived from Kodie's Illustrator artwork with the
   outer ring and the coloured nucleus removed, and the remaining
   linework scaled up — the original read well large but turned to mush
   in a browser tab, and the ring plus nucleus were most of the clutter.

   SINGLE SOURCE OF TRUTH: assets/icons/mark.svg — the linework alone,
   square viewBox, `fill="currentColor"`, no background. Edit that file
   and re-run; every variant below is generated from it. Don't hand-edit
   the generated files.

   Everything is vector shapes, never <text>: an SVG favicon cannot load
   a webfont, so a type-based mark would fall back to whatever serif the
   OS has and render differently per machine.

   Outputs land in assets/icons/.
   ============================================================ */
const fs = require('fs');
const path = require('path');
const { execFileSync } = require('child_process');

const OUT = path.join(__dirname, '..', 'assets', 'icons');

/* Colours are duplicated from tokens.css on purpose — an icon file is
   fetched without the stylesheet, so it cannot read a CSS variable.
   If --accent-dark changes, update site.webmanifest and the THEME
   constant in tools/add-favicon.js to match. */
const BOARD = '#24576f';   /* --c-blue-700   */
const CHALK = '#f6f4ef';   /* --c-paper-warm */

const source = fs.readFileSync(path.join(OUT, 'mark.svg'), 'utf8');
const VB = Number((source.match(/viewBox="0 0 (\d+)/) || [])[1]);
const INNER = source.replace(/^[\s\S]*?<svg[^>]*>/, '').replace(/<\/svg>\s*$/, '')
                    .replace(/currentColor/g, CHALK);
if (!VB) throw new Error('could not read viewBox from assets/icons/mark.svg');

/* rx 0 = full bleed. iOS and Android apply their own mask, so a
   pre-rounded source would show dark corners inside their rounding. */
function build(opts) {
  const rx = opts.rx === undefined ? VB * 0.22 : opts.rx;
  const scale = opts.scale || 1;
  const off = (VB - VB * scale) / 2;
  return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ' + VB + ' ' + VB + '">' +
    '<rect width="' + VB + '" height="' + VB + '"' + (rx ? ' rx="' + rx.toFixed(1) + '"' : '') +
    ' fill="' + BOARD + '"/>' +
    '<g transform="translate(' + off.toFixed(1) + ',' + off.toFixed(1) + ') scale(' + scale + ')">' +
    INNER + '</g></svg>';
}

const files = {
  /* browser tab — keeps its own rounding, sits on the tab strip bare */
  'favicon.svg':       build({}),
  /* iOS home screen — square source, iOS rounds it itself */
  'icon-square.svg':   build({ rx: 0 }),
  /* Android maskable — linework inside the safe circle (middle 80%),
     board colour bleeding to every edge so any mask shape works */
  'icon-maskable.svg': build({ rx: 0, scale: 0.66 })
};

Object.keys(files).forEach(function (f) {
  fs.writeFileSync(path.join(OUT, f), files[f]);
  console.log('wrote assets/icons/' + f);
});

if (process.argv.indexOf('--png') === -1) {
  console.log('\n(run with --png to rasterise — needs ImageMagick)');
  return;
}

/* Density has to be derived from the viewBox, not hardcoded. ImageMagick
   rasterises an SVG at viewBox_units / 72 * density pixels, so a fixed
   high density against a 1000-unit viewBox asks for a ~17000px bitmap
   and dies with "cache resources exhausted". This targets ~1024px and
   then downsamples, which is plenty for a 512 icon. */
const DENSITY = (72 * 1024 / VB).toFixed(2);

function raster(src, out, size) {
  execFileSync('convert', ['-background', 'none', '-density', DENSITY,
    path.join(OUT, src), '-resize', size + 'x' + size, path.join(OUT, out)]);
  console.log('wrote assets/icons/' + out);
}

raster('icon-square.svg',   'apple-touch-icon.png',  180);
raster('favicon.svg',       'icon-192.png',          192);
raster('favicon.svg',       'icon-512.png',          512);
raster('icon-maskable.svg', 'icon-maskable-512.png', 512);

/* .ico carries 16/32/48 so old browsers and Windows pinned tiles get a
   sharp version at each, rather than downsampling one big bitmap. */
execFileSync('convert', ['-background', 'none', '-density', DENSITY,
  path.join(OUT, 'favicon.svg'), '-define', 'icon:auto-resize=48,32,16',
  path.join(OUT, 'favicon.ico')]);
console.log('wrote assets/icons/favicon.ico');
