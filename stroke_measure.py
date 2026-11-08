from math import hypot
from statistics import median
from shapely.geometry import Polygon,LineString,Point
from shapely.ops import unary_union

def rings(glyph):
 start=0
 for end in glyph.endPtsOfContours:
  yield list(glyph.coordinates[start:end+1]);start=end+1

def area(p):
 return sum(x*v-y*u for (x,y),(u,v) in zip(p,p[1:]+p[:1]))

def ink_shape(glyph):
 outer=[];inner=[]
 for ring in rings(glyph):
  polygon=Polygon(ring)
  if not polygon.is_valid:polygon=polygon.buffer(0)
  if polygon.is_empty:continue
  (outer if area(ring)<0 else inner).append(polygon)
 ink=unary_union(outer)
 return ink.difference(unary_union(inner)) if inner else ink

def measure(glyph):
 ink=ink_shape(glyph)
 candidates=[]
 for ring in rings(glyph):
  for a,b in zip(ring,ring[1:]+ring[:1]):
   dx,dy=b[0]-a[0],b[1]-a[1];length=hypot(dx,dy)
   if length<9:continue
   candidates.append((length,a,b))
 candidates.sort(reverse=True)
 widths=[]
 for length,a,b in candidates[:96]:
  dx,dy=b[0]-a[0],b[1]-a[1];nx,ny=dy/length,-dx/length
  x,y=(a[0]+b[0])/2,(a[1]+b[1])/2
  start=(x+nx*.3,y+ny*.3);end=(x+nx*130,y+ny*130)
  segment=LineString([start,end])
  cross=ink.intersection(segment)
  pieces=list(cross.geoms) if hasattr(cross,'geoms') else [cross]
  for piece in pieces:
   if piece.geom_type=='LineString' and piece.distance(Point(start))<.15:
    width=piece.length+.3
    if 9<width<65:widths.append(width)
    break
 if not widths:return None
 widths.sort()
 return median(widths[:max(3,round(len(widths)*.65))])
