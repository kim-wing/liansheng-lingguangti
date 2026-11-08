"""Rename the current font, rebuild 存-family parts and balance pen widths."""
from pathlib import Path
from runpy import run_path
from statistics import median
import json,gzip
from zipfile import ZipFile,ZIP_DEFLATED

from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._g_l_y_f import GlyphCoordinates
from fontTools.ttLib.tables.TupleVariation import TupleVariation
from shapely.geometry import Polygon
from PIL import Image,ImageDraw,ImageFont

from glyph_zhi import drawn,outline
from stroke_measure import measure,rings
ROOT=Path(__file__).resolve().parent
BASE=ROOT/'dist/liansheng-2.2.8/LianshengYouzhiti-2.2.8-Variable.ttf'
OUT=ROOT/'dist/lingguang-2.2.9'
NAME='LianshengLingguangti-2.2.9'
FONT=OUT/f'{NAME}-Variable.ttf'
TARGET=32
pen=run_path(str(ROOT/'build-uniform-weight.py'))
area=pen['area'];clean=pen['clean_contour'];offsets=pen['offsets'];expand=pen['expand']
HEADER=[[(20,28),(52,25),(85,23)],[(57,10),(50,29),(38,45),(17,60)],[(28,49),(28,94)]]
CHILD=[[(52,49),(83,46),(70,61)],[(64,60),(68,75),(67,91),(61,96),(54,92)],[(45,77),(71,74),(94,72)]]
CUN=HEADER+CHILD
ZAI=HEADER+[[(49,63),(91,60)],[(70,47),(69,91)],[(44,95),(95,91)]]
GRASS=[[(12,47),(90,43)],[(34,12),(36,86)],[(69,10),(67,84)]]
LEATHER=[[(10,19),(90,16)],[(32,8),(32,37)],[(69,7),(68,36)],[(32,37),(68,35)],[(24,49),(24,69)],[(24,50),(78,46),(77,68)],[(24,69),(77,67)],[(50,36),(51,95)],[(11,83),(91,79)]]

def fitted(paths,box):
    xs,ys=zip(*(p for path in paths for p in path))
    x0,y0,x1,y1=min(xs),min(ys),max(xs),max(ys)
    left,top,right,bottom=box
    return [[(left+(x-x0)*(right-left)/(x1-x0),top+(y-y0)*(bottom-top)/(y1-y0)) for x,y in path] for path in paths]
JIAN=[*fitted(GRASS,(6,2,94,23)),*fitted(CUN,(6,37,96,98))]
CHA=[*fitted(GRASS,(6,2,94,23)),*fitted(ZAI,(6,37,96,98))]
REPAIRS={
    '存':CUN,'荐':JIAN,'在':ZAI,'茬':CHA,
    '鞯':[*fitted(LEATHER,(2,9,32,97)),*fitted(JIAN,(45,3,98,97))]
}

def remake(glyph,paths):
    # Fit the skeleton inside the approved glyph envelope, using one pen size
    # for small components and large components alike.
    x0,y0,x1,y1=glyph.xMin,glyph.yMin,glyph.xMax,glyph.yMax
    placed=fitted(paths,(x0+16,-y1+16,x1-16,-y0-16))
    up=[[(x,-y) for x,y in path] for path in placed]
    return outline(list(drawn(up,TARGET/2)))

def shift_ring(points,distance):
    vectors=offsets(points)
    def moved(amount):
        return [(round(x+amount*u),round(y+amount*v)) for (x,y),(u,v) in zip(points,vectors)]
    initial=area(points)
    if distance<=0 or initial<=0:
        return moved(distance)
    valid=Polygon(points).is_valid
    for fraction in (1,.9,.8,.7,.6,.5,.4,.3,.2,.1,0):
        result=moved(distance*fraction)
        if not initial*.35<=area(result)<=initial:
            continue
        if valid and not Polygon(result).is_valid:
            continue
        return result
    return points

def store_regular(glyph,contours,glyf):
    coordinates=[];ends=[]
    for points in contours:
        coordinates.extend(points);ends.append(len(coordinates)-1)
    glyph.coordinates=GlyphCoordinates(coordinates)
    glyph.endPtsOfContours=ends
    glyph.numberOfContours=len(ends)
    glyph.flags=bytearray([1]*len(coordinates))
    glyph.flags[0]|=0x40
    glyph.recalcBounds(glyf)

def rename(font):
    for record in font['name'].names:
        value=record.toUnicode()
        value=value.replace('莲生幼稚体','莲生灵光体').replace('蓮生幼稚體','蓮生靈光體')
        value=value.replace('Liansheng Youzhiti','Liansheng Lingguangti').replace('LianshengYouzhiti','LianshengLingguangti')
        value=value.replace('2.228','2.229')
        if record.nameID==13:
            value+=' Modified 2026-11-08: rebuilt Cun components and normalized pen thickness. Renamed as Liansheng Lingguangti.'
        record.string=value
    font['head'].fontRevision=2.229

def build():
    OUT.mkdir(parents=True,exist_ok=True)
    changes={}
    with TTFont(BASE) as font:
        glyf=font['glyf'];cmap=font.getBestCmap();font['gvar']
        for char,paths in REPAIRS.items():
            name=cmap[ord(char)]
            glyf[name]=remake(glyf[name],paths)
        targets={name:chr(code) for code,name in cmap.items()
                 if 0x3400<=code<=0x9fff or chr(code).isascii() and chr(code).isalnum()}
        for i,(name,char) in enumerate(targets.items(),1):
            glyph=glyf[name]
            if glyph.numberOfContours<=0:
                continue
            before=measure(glyph)
            contours=[clean(list(points)) for points in rings(glyph)]
            contours=[p for p in contours if len(p)>=3]
            store_regular(glyph,contours,glyf)
            adjustment=0
            if before is not None:
                for attempt in range(2):
                    current=measure(glyph)
                    if current is None or abs(current-TARGET)<=1.1:
                        break
                    distance=max(-2.5,min(6.5,(TARGET-current)/2))
                    contours=[clean(shift_ring(p,distance)) for p in contours]
                    contours=[p for p in contours if len(p)>=3]
                    store_regular(glyph,contours,glyf)
                    adjustment+=distance
            # Rebuild the heavy endpoint from the corrected Regular master.
            # This keeps a fixed growth radius across differently sized glyphs.
            regular=[];bold=[];ends=[]
            for points in contours:
                regular.extend(points);bold.extend(expand(points));ends.append(len(regular)-1)
            store_regular(glyph,contours,glyf)
            font['hmtx'][name]=font['hmtx'][name][0],glyph.xMin
            font['gvar'].variations[name]=[TupleVariation({'wght':(0,1,1)},
                [(u-x,v-y) for (x,y),(u,v) in zip(regular,bold)]+[(0,0)]*4)]
            after=measure(glyph)
            changes[char]=dict(before=round(before,2) if before else None,
                after=round(after,2) if after else None,offset=round(adjustment,2),rebuilt=char in REPAIRS)
            if i%1000==0:print('Measured',i,flush=True)
        rename(font)
        low=high=0
        for name in font.getGlyphOrder():
            glyph=glyf[name]
            if glyph.numberOfContours>0:
                low=min(low,glyph.yMin-17);high=max(high,glyph.yMax+17)
        font['OS/2'].usWinAscent=max(font['OS/2'].usWinAscent,high)
        font['OS/2'].usWinDescent=max(font['OS/2'].usWinDescent,-low)
        font['hhea'].ascent=max(font['hhea'].ascent,high)
        font['hhea'].descent=min(font['hhea'].descent,low)
        font.save(FONT)
    with TTFont(BASE) as old,TTFont(FONT) as new:
        assert old.getBestCmap()==new.getBestCmap()
        for code,name in old.getBestCmap().items():
            assert old['hmtx'][name][0]==new['hmtx'][name][0]
        assert new['name'].getName(1,3,1,0x804).toUnicode()=='莲生灵光体'
        assert new['fvar'].axes[0].minValue==400 and new['fvar'].axes[0].maxValue==650
    (OUT/'stroke-audit.json').write_text(json.dumps(changes,ensure_ascii=False,indent=2))
    note='莲生灵光体\nLiansheng Lingguangti\n\n作者：莲生\n正式发布版 2.2.9\n\n手写风格可变字体，支持中文、英文、数字与常用符号。\n字重范围：400–650。可免费用于个人及商业项目。\n\n安装与使用\nmacOS：双击 TTF 文件，在“字体册”中安装。\nWindows：右键 TTF 文件，选择“安装”。\n安装后在应用的字体列表中选择“莲生灵光体”或“Liansheng Lingguangti”。\n字重调节需要应用支持可变字体。\n\n开源与反馈\nhttps://github.com/kim-wing/liansheng-lingguangti\n\n版权与授权\n莲生的原创贡献：Copyright © 2026 莲生。\n本字体依随附 Arphic Public License 分发，保留上游版权声明。\n修改与再分发请遵循完整授权条款，并标明修改内容与日期。\n\nEnglish\nA handwritten-style variable font by Liansheng, supporting Chinese, Latin,\nnumbers and common symbols. Weight range: 400–650. Free for personal\nand commercial use under the accompanying Arphic Public License.\nInstall the TTF and select Liansheng Lingguangti in your application.\nVariable weight adjustment requires a compatible application.\n'
    (OUT/'README.txt').write_text(note)
    with ZipFile(OUT/f'{NAME}.zip','w',ZIP_DEFLATED) as z:
        for p in (FONT,OUT/'README.txt'):z.write(p,p.name)
        for n in ('ARPHICPL.TXT','ARPHICPL-zh_CN.TXT','UPSTREAM-COPYING.txt','MAKEMEHANZI-LGPL.txt'):
            z.write(ROOT/'vendor'/n,n)
    return changes

if __name__=='__main__':
    audit=build()
    values=[r['after'] for r in audit.values() if r['after'] is not None]
    print('Measured glyphs',len(values),'Median width',round(median(values),2))
    print(FONT)
