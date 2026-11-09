"""Build the two-glyph maintenance release from the 2.2.9 outline master."""

from pathlib import Path
from runpy import run_path
from zipfile import ZipFile, ZIP_DEFLATED

from fontTools.ttLib import TTFont
from fontTools.ttLib.tables.TupleVariation import TupleVariation

ROOT = Path(__file__).resolve().parent
BASE = ROOT / 'dist/lingguang-2.2.9/LianshengLingguangti-2.2.9-Variable.ttf'
OUT = ROOT / 'dist/lingguang-2.2.10'
STEM = 'LianshengLingguangti-2.2.10'

# Leave white space on both sides of the central dot and sweep.
BAN = [
    [(3, 17), (16, 16), (29, 14)],
    [(6, 40), (17, 39), (27, 37)],
    [(2, 67), (16, 65), (31, 61)],
    [(17, 16), (17, 40), (15, 64)],
    [(43, 13), (49, 25)],
    [(59, 24), (54, 47), (46, 72), (34, 91)],
    [(68, 20), (82, 18), (98, 19)],
    [(70, 49), (82, 47), (95, 48)],
    [(66, 80), (81, 79), (99, 76)],
    [(83, 18), (82, 48), (81, 78)],
]

def build():
    helpers = run_path(str(ROOT / 'build-lingguang-2.2.9.py'))
    OUT.mkdir(parents=True, exist_ok=True)
    with TTFont(BASE) as font:
        glyf, variations = font['glyf'], font['gvar'].variations
        cmap = font.getBestCmap()
        shen = cmap[ord('深')]
        glyph = glyf[shen]
        keep = []
        contours = []
        start = 0
        for end in glyph.endPtsOfContours:
            points = list(glyph.coordinates[start:end + 1])
            if min(y for _, y in points) <= 600:
                keep.extend(range(start, end + 1))
                contours.append(points)
            start = end + 1
        assert len(contours) == glyph.numberOfContours - 1
        keep.extend(range(start, start + 4))  # Preserve phantom point deltas.
        for variation in variations[shen]:
            variation.calcInferredDeltas(list(glyph.coordinates) + [(0, 0)] * 4, glyph.endPtsOfContours)
            variation.coordinates = [variation.coordinates[i] for i in keep]
        helpers['store_regular'](glyph, contours, glyf)

        ban = cmap[ord('班')]
        glyph = glyf[ban] = helpers['remake'](glyf[ban], BAN)
        contours = [helpers['clean'](list(ring)) for ring in helpers['rings'](glyph)]
        helpers['store_regular'](glyph, contours, glyf)
        regular = list(glyph.coordinates)
        bold = [p for ring in contours for p in helpers['expand'](ring)]
        variations[ban] = [TupleVariation({'wght': (0, 1, 1)},
            [(u-x, v-y) for (x, y), (u, v) in zip(regular, bold)] + [(0, 0)] * 4)]
        font['hmtx'][ban] = font['hmtx'][ban][0], glyph.xMin

        for record in font['name'].names:
            if record.nameID in (3, 5):
                record.string = record.toUnicode().replace('2.229', '2.230')
            elif record.nameID == 13:
                record.string = record.toUnicode() + ' Modified 2026-11-09: corrected the outlines of U+6DF1 and U+73ED.'
        font['head'].fontRevision = 2.230
        font.save(OUT / f'{STEM}-Variable.ttf')

    readme = (ROOT / 'README-2.2.10.txt').read_bytes()
    (OUT / 'README.txt').write_bytes(readme)
    with ZipFile(OUT / f'{STEM}.zip', 'w', ZIP_DEFLATED) as release:
        release.write(OUT / f'{STEM}-Variable.ttf', f'{STEM}-Variable.ttf')
        release.writestr('README.txt', readme)
        for filename in ('ARPHICPL.TXT', 'ARPHICPL-zh_CN.TXT', 'UPSTREAM-COPYING.txt', 'MAKEMEHANZI-LGPL.txt'):
            release.write(ROOT / 'vendor' / filename, filename)

if __name__ == '__main__':
    build()
