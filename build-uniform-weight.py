"""Build compatible masters by offsetting each local outline normal."""
from math import hypot
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables.TupleVariation import TupleVariation
from fontTools.ttLib.tables._g_l_y_f import GlyphCoordinates
from shapely.geometry import Polygon

ROOT=Path(__file__).resolve().parent
BASE=ROOT/'dist/liansheng-2.2.6/LianshengYouzhiti-2.2.6-Variable.ttf'
OUT=ROOT/'dist/liansheng-2.2.7'
FONT=OUT/'LianshengYouzhiti-2.2.7-Variable.ttf'
RADIUS=10

def area(points):
    return sum(x*v-y*u for (x,y),(u,v) in zip(points,points[1:]+points[:1]))

def clean_contour(points):
    points=[p for i,p in enumerate(points) if p!=points[i-1]]
    result=[]
    for i,p in enumerate(points):
        a,b=points[i-1],points[(i+1)%len(points)]
        cross=(p[0]-a[0])*(b[1]-p[1])-(p[1]-a[1])*(b[0]-p[0])
        dot=(p[0]-a[0])*(b[0]-p[0])+(p[1]-a[1])*(b[1]-p[1])
        if cross or dot<0:
            result.append(p)
    return result

def offsets(points):
    normals=[]
    for a,b in zip(points,points[1:]+points[:1]):
        dx,dy=b[0]-a[0],b[1]-a[1]
        length=hypot(dx,dy)
        normals.append((-dy/length,dx/length))
    vectors=[]
    for i,(nx,ny) in enumerate(normals):
        px,py=normals[i-1]
        ux,uy=px+nx,py+ny
        length=hypot(ux,uy)
        if length<.01:
            vectors.append((nx,ny))
        else:
            ux,uy=ux/length,uy/length
            miter=min(1.55,1/max(.01,ux*nx+uy*ny))
            vectors.append((ux*miter,uy*miter))
    return vectors

def expand(points):
    vectors=offsets(points)
    winding=area(points)
    def candidate(amount):
        return [(round(x+amount*u),round(y+amount*v))
                for (x,y),(u,v) in zip(points,vectors)]
    if winding<=0:
        return candidate(RADIUS)
    # Counters need optical space at heavy weights. Limit only their inward
    # contraction, while every outside stroke edge receives the full radius.
    polygon=Polygon(points)
    valid=polygon.is_valid
    if winding<20:
        return points
    for step in range(100,0,-1):
        target=candidate(RADIUS*step/100)
        if not winding*.35<=area(target)<=winding:
            continue
        if valid and not Polygon(target).is_valid:
            continue
        return target
    return points

def build():
    OUT.mkdir(exist_ok=True,parents=True)
    with TTFont(BASE) as font:
        glyf=font['glyf']
        for name in font.getGlyphOrder():
            glyph=glyf[name]
            if glyph.numberOfContours<=0:
                continue
            regular=[];bold=[];ends=[];start=0
            for end in glyph.endPtsOfContours:
                points=clean_contour(list(glyph.coordinates[start:end+1]))
                start=end+1
                if len(points)<3:
                    continue
                regular.extend(points)
                bold.extend(expand(points))
                ends.append(len(regular)-1)
            glyph.coordinates=GlyphCoordinates(regular)
            glyph.endPtsOfContours=ends
            glyph.numberOfContours=len(ends)
            glyph.flags=bytearray([1]*len(regular))
            glyph.flags[0]|=0x40
            glyph.recalcBounds(glyf)
            font['gvar'].variations[name]=[TupleVariation({'wght':(0,1,1)},
                [(u-x,v-y) for (x,y),(u,v) in zip(regular,bold)]+[(0,0)]*4)]
        font['head'].fontRevision=2.227
        for record in font['name'].names:
            if record.nameID in (3,5):
                record.string=record.toUnicode().replace('2.226','2.227')
        font.save(FONT)
    with TTFont(BASE) as old,TTFont(FONT) as new:
        assert old.getBestCmap()==new.getBestCmap()
        assert old.reader['fvar']==new.reader['fvar']
        for name in old.getGlyphOrder():
            assert old['hmtx'][name]==new['hmtx'][name]
    note='莲生幼稚体 2.2.7 字重试用版\n2026-11-07：清理轮廓上的重复及共线节点，沿每条笔画边缘的局部法线增粗。外轮廓统一使用 10 字体单位的偏移，转角采用限长接合。\n密集字的小字腔单独限制向内收缩量，避免堵口。保留 400–650 字重轴以及 2.2.6 的大小、高低和长笔画设计。\n字体依 Arphic Public License 分发。\n'
    (OUT/'README.txt').write_text(note)
    with ZipFile(OUT/'LianshengYouzhiti-2.2.7.zip','w',ZIP_DEFLATED) as z:
        for p in (FONT,OUT/'README.txt'):
            z.write(p,p.name)
        for name in ('ARPHICPL.TXT','ARPHICPL-zh_CN.TXT','UPSTREAM-COPYING.txt','MAKEMEHANZI-LGPL.txt'):
            z.write(ROOT/'vendor'/name,name)
    print(FONT)

if __name__=='__main__':
    build()
