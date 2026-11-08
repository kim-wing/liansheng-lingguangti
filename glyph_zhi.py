"""Redraw 制 and reuse its upper form in 掣 and 製."""
from fontTools.pens.ttGlyphPen import TTGlyphPen
from shapely.geometry import LineString
from shapely.geometry.polygon import orient
from shapely.ops import unary_union


LEFT = (
    ((287,718),(263,652),(215,607)),
    ((257,636),(362,645),(508,663)),
    ((149,509),(347,524),(554,542)),
    ((237,409),(237,330),(222,249)),
    ((238,411),(363,421),(509,436),(504,341),(491,284),(464,306)),
    ((396,757),(392,495),(389,251),(380,34)),
)
HAND = (
    ((614,345),(486,316),(350,303)),
    ((295,242),(460,248),(649,266)),
    ((148,153),(451,160),(783,181)),
    ((479,323),(486,185),(483,58),(462,31),(408,49)),
)
CLOTHING = (
    ((456,367),(487,331)),
    ((220,298),(450,305),(704,328)),
    ((474,307),(379,203),(225,126)),
    ((370,192),(372,49),(454,89)),
    ((676,229),(615,189),(547,164)),
    ((478,247),(553,141),(663,79),(782,47)),
)


def contours(glyph):
    start = 0
    for end in glyph.endPtsOfContours:
        yield list(glyph.coordinates[start:end+1])
        start = end+1


def drawn(strokes, radius):
    ink = unary_union([LineString(path).buffer(radius,cap_style='flat',
                        join_style='mitre',mitre_limit=1.5) for path in strokes])
    for part in getattr(ink,'geoms',[ink]):
        polygon = orient(part,sign=-1)
        for ring in (polygon.exterior,*polygon.interiors):
            yield list(ring.coords)[:-1]


def outline(rings):
    pen = TTGlyphPen(None)
    for ring in rings:
        points = [tuple(map(round,p)) for p in ring]
        pen.moveTo(points[0])
        for p in points[1:]:
            pen.lineTo(p)
        pen.closePath()
    glyph = pen.glyph()
    glyph.recalcBounds(None)
    return glyph


def revise_zhi(font):
    cmap = font.getBestCmap()
    glyf = font['glyf']
    zhi = cmap[ord('制')]
    right = [ring for ring in contours(glyf[zhi]) if min(p[0] for p in ring) >= 580]
    assert len(right) == 2
    left = list(drawn(LEFT,15))
    upper = [[(120+x*.77,397+y*.55) for x,y in ring] for ring in (*left,*right)]
    variants = {'制':outline([*left,*right]), '掣':outline([*upper,*drawn(HAND,14)]),
                '製':outline([*upper,*drawn(CLOTHING,14)])}
    for char,glyph in variants.items():
        code = ord(char)
        name = cmap.get(code)
        if name is None:
            name = f'uni{code:04X}'
            font.setGlyphOrder([*font.getGlyphOrder(),name])
            for table in font['cmap'].tables:
                if table.isUnicode():
                    table.cmap[code] = name
        advance = font['hmtx'].metrics.get(name,(950,0))[0]
        glyf[name] = glyph
        font['hmtx'][name] = advance,glyph.xMin
