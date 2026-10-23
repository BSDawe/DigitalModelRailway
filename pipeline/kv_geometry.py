"""Kettle Valley route Odlum - Hope - Coquihalla - Brodie - Brookmere - Princeton - Penticton - Carmi - Midway - Grand Forks - Castlegar - Nelson.
Track (Brendan): Odlum - Hope from his own KVRR trace (kvrr.gpkg); Hope - Brodie (Coquihalla Sub), Brodie - Penticton (Princeton Sub),
Penticton - Midway (Carmi) and Midway - Robson West (C&W) from the KVR Trails KML; Robson West - Castlegar - Nelson from the NRWN.
Writes kv_route.pkl and castlegar_wye.json."""
import json, math, os, pickle, sqlite3
import numpy as np
from shapely import wkb
from shapely.geometry import LineString, Point
from shapely.ops import substring, linemerge, unary_union
from nrwn_graph import Net, fwd, inv, MI
from kvr_trails import lines
HERE = os.path.dirname(os.path.abspath(__file__))
T = {k: LineString(v) for k, v in lines().items()}

# Odlum - Hope: Brendan's own trace
def gpkg_lines(path):
    c = sqlite3.connect(path); out = []
    for (b,) in c.execute('select geom from kvrr'):
        if b is None: continue
        env = {0: 0, 1: 32, 2: 48, 3: 48, 4: 64}[(b[3] >> 1) & 7]; g = wkb.loads(bytes(b[8 + env:]))
        out += [LineString([fwd(*p[:2]) for p in L.coords]) for L in (g.geoms if hasattr(g, 'geoms') else [g])]
    return out
ODLUM = Point(fwd(-121.4844, 49.3831)); HOPE = Point(fwd(-121.4415, 49.3800))
pieces = gpkg_lines(os.path.join(HERE, 'kvrr.gpkg'))
start = min(pieces, key=lambda L: L.distance(ODLUM))
merged = linemerge(unary_union([L for L in pieces if L.distance(start) < 30 or L.distance(HOPE) < 2000]))
K = min((merged.geoms if hasattr(merged, 'geoms') else [merged]), key=lambda L: L.distance(ODLUM) + L.distance(HOPE))
if Point(K.coords[0]).distance(ODLUM) > Point(K.coords[-1]).distance(ODLUM): K = LineString(K.coords[::-1])
COQ = LineString(T['Coquihalla Sub'].coords[::-1])                       # traced Brodie -> Odlum; run Odlum -> Brodie
h_c = COQ.project(HOPE); hk = K.project(Point(COQ.interpolate(h_c)))
leg1 = substring(K, 0, hk); leg2 = substring(COQ, h_c, COQ.length)
print(f'  Odlum-Hope (own trace) {leg1.length/MI:.2f} mi; Hope on the Coquihalla Sub {COQ.distance(HOPE):.0f} m from the station point')
PRN = LineString(T['Princeton Sub'].coords[::-1])                        # Brodie -> Penticton
CAR = LineString(list(T['Carmi2'].coords) + list(T['Carmi'].coords)[1:]) # Penticton -> Midway
CW = T['C&W']                                                            # Midway -> Robson West
# Robson West - Castlegar - Nelson: the NRWN, as before
F = json.load(open(os.path.join(HERE, 'nrwn', 'south.json')))
net = Net(F)
cw_end = inv(*CW.coords[-1]); NELSON_PT = (-117.29, 49.49)
TAIL, snaps = net.route(cw_end, NELSON_PT, start_any=True)   # the C&W survives into Castlegar as a NRWN spur
legs = [leg1, leg2, PRN, CAR, CW, TAIL]
names = ['Odlum-Hope', 'Hope-Brodie', 'Brodie-Penticton', 'Penticton-Midway', 'Midway-Robson W', 'Robson W-Nelson']
pts = []
for nm, L in zip(names, legs):
    c = list(L.coords)
    if pts:
        gap = math.dist(pts[-1], c[0]); gap_r = math.dist(pts[-1], c[-1])
        if gap_r < gap: c = c[::-1]; gap = gap_r
        print(f'  join into {nm}: {gap:.0f} m')
    for p in c:
        if not pts or math.dist(p, pts[-1]) > 0.5: pts.append(p)
    print(f'  {nm}: {L.length/MI:.1f} mi')
KV = LineString(pts)
print(f'KV Odlum -> Nelson {KV.length/MI:.1f} mi (timetable 425.5)')
TT = {'Odlum': 0, 'Hope': 2.3, 'Brodie': 52.6, 'Brookmere': 56.6, 'Princeton': 94.7, 'Penticton': 165.2, 'McCulloch': 222.3, 'Beaverdell': 256.6,
      'Midway': 298.9, 'Grand Forks': 330.8, 'Castlegar': 399.8, 'Nelson': 425.5}
pickle.dump(dict(KV=KV), open(os.path.join(HERE, 'kv_route.pkl'), 'wb'))

# Castlegar station is at the wye where the Trail line leaves (Brendan)
TRAIL = (-117.708, 49.097)
Tr, _ = net.route(TRAIL, inv(*KV.coords[-1]))
j = next(d for d in np.arange(0, Tr.length, 10.0) if KV.distance(Tr.interpolate(d)) < 5)
json.dump(dict(wye=inv(*Tr.interpolate(j).coords[0])), open(os.path.join(HERE, 'castlegar_wye.json'), 'w'))
print('  Castlegar wye', inv(*Tr.interpolate(j).coords[0]), f'{KV.project(Tr.interpolate(j))/MI:.1f} mi from Odlum (timetable 399.8)')
