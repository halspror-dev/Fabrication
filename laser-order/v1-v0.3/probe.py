import ezdxf, math
from shapely.geometry import Polygon, Point, LineString
def ents(n):
    msp = ezdxf.readfile(f"out/{n}.dxf").modelspace()
    C = [(round(e.dxf.center.x,3), round(e.dxf.center.y,3), round(2*e.dxf.radius,3)) for e in msp if e.dxftype()=="CIRCLE"]
    P = [Polygon([p[:2] for p in e.get_points()]) for e in msp if e.dxftype()=="LWPOLYLINE"]
    P.sort(key=lambda p:-p.area)
    return C, P
def ray(poly, o, ang, L=5):
    r = LineString([o, (o[0]+L*math.cos(ang), o[1]+L*math.sin(ang))])
    x = r.intersection(poly.exterior)
    pts = [x] if x.geom_type=="Point" else list(getattr(x,"geoms",[]))
    return round(min(Point(o).distance(p) for p in pts),4)
# collar: axis at (1.70, 2.80)
C,P = ents("collar"); kh = P[1]; ax=(1.70,2.80)
print("collar circles", C)
print(" seat radius fwd/back (expect .5625):", ray(kh,ax,0), ray(kh,ax,math.pi))
print(" seat radius toward handle side (expect .5625):", ray(kh,ax,math.pi/2))
bh=(1.70,2.00); print(" big hole radius fwd/away (expect .6875):", ray(kh,bh,0), ray(kh,bh,-math.pi/2))
print(" slot half width at mid (expect .5625):", ray(kh,(1.70,2.40),0), ray(kh,(1.70,2.40),math.pi))
print(" outline bounds", [round(v,3) for v in P[0].bounds])
C,P = ents("keeper"); print("keeper outline", [round(v,3) for v in P[0].bounds])
o=(0.875,2.75)  # notch center on the notched edge
print(" notch radius (expect .65):", ray(P[0].buffer(0),o,-math.pi/2), ray(P[0],o,-math.pi/4))
sl=P[1]; print(" slot bounds (expect x .7745-.9755, y 0.2045-1.8955 from far edge):", [round(v,4) for v in sl.bounds])
C,P = ents("frame"); print("frame circles", C); print(" pivot slot bounds", [round(v,4) for v in P[1].bounds], "outline", [round(v,3) for v in P[0].bounds])
C,P = ents("trigger"); print("trigger circles", C, "outline", [round(v,3) for v in P[0].bounds])
