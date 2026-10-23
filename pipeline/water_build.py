"""Water base layer from Brendan's BC water GeoPackage (bc_water.gpkg: StatCan hydro polygons, ocean + lakes + wide rivers,
EPSG:3347). Adjoining pieces are merged, small ponds and islets dropped, outlines simplified, and the result written as
compact lon/lat rings to water.json for the map page."""
import json, os, sqlite3, sys
from shapely import wkb
from shapely.geometry import box, Polygon, MultiPolygon
from shapely.ops import unary_union, transform
from pyproj import Transformer
HERE = os.path.dirname(os.path.abspath(__file__))
TOL = float(sys.argv[1]) if len(sys.argv) > 1 else 80.0          # simplify tolerance, metres
MIN_WATER = 1.0e6                                                 # drop water bodies under 1 km2
MIN_ISLAND = 0.15e6                                               # drop islands under 0.15 km2
to_ll = Transformer.from_crs(3347, 4326, always_xy=True).transform
to_xy = Transformer.from_crs(4326, 3347, always_xy=True).transform
c = sqlite3.connect(os.path.join(HERE, 'bc_water.gpkg'))
geoms = []
for (b,) in c.execute('select geom from bcocean2'):
    env = {0: 0, 1: 32, 2: 48, 3: 48, 4: 64}[(b[3] >> 1) & 7]
    g = wkb.loads(bytes(b[8 + env:]))
    if not g.is_valid: g = g.buffer(0)
    geoms.append(g)
print(len(geoms), 'pieces')
# map area: a lon/lat box around everything on the map, in the file's projection (densified so the edges curve properly)
import numpy as np
W, S, E, N = -142.0, 44.5, -113.8, 58.5      # well beyond every map view, so the sea never shows a clipped edge
edge = [(x, S) for x in np.linspace(W, E, 60)] + [(E, y) for y in np.linspace(S, N, 60)] + [(x, N) for x in np.linspace(E, W, 60)] + [(W, y) for y in np.linspace(N, S, 60)]
area = Polygon([to_xy(*p) for p in edge])
import pickle, shapely, time
cache = os.path.join(HERE, 'water_union.pkl')
if os.path.exists(cache): U0 = pickle.load(open(cache, 'rb'))
else:
    t0 = time.time(); ab = area.bounds
    near = [g for g in geoms if not (g.bounds[2] < ab[0] or g.bounds[0] > ab[2] or g.bounds[3] < ab[1] or g.bounds[1] > ab[3])]
    snapped = shapely.set_precision(near, 1.0)                    # 1 m grid: shared edges coincide, so adjoining pieces merge cleanly
    U0 = shapely.union_all(snapped).intersection(area)
    pickle.dump(U0, open(cache, 'wb')); print(f'merged {len(near)} pieces in {time.time()-t0:.0f} s')
# full detail inside the area the map shows; a coarse outline beyond it (far coast and open ocean, seen only at the widest zoom)
iW, iS, iE, iN = -131.2, 48.0, -113.8, 55.7
iedge = [(x, iS) for x in np.linspace(iW, iE, 60)] + [(iE, y) for y in np.linspace(iS, iN, 60)] + [(x, iN) for x in np.linspace(iE, iW, 60)] + [(iW, y) for y in np.linspace(iN, iS, 60)]
inner = Polygon([to_xy(*p) for p in iedge])
U_in = U0.intersection(inner).simplify(TOL, preserve_topology=True)
U_out = U0.difference(inner).simplify(600.0, preserve_topology=True)
polys = [p for U in (U_in, U_out) for p in (U.geoms if hasattr(U, 'geoms') else [U]) if p.geom_type == 'Polygon' and p.area >= MIN_WATER]
polys = [p for p in polys if not (p.within(U_out.envelope) and p.area < 25e6 and not p.intersects(inner))]   # no small lakes far outside the map
rings = []; npts = 0
for p in polys:
    ext = [[round(v, 4) for v in to_ll(*q)] for q in p.exterior.coords]
    holes = [[[round(v, 4) for v in to_ll(*q)] for q in h.coords] for h in p.interiors if Polygon(h).area >= MIN_ISLAND]
    rings.append([ext] + holes); npts += len(ext) + sum(len(h) for h in holes)
# flat, compact encoding: each ring as [lon0, lat0, dlon, dlat, ...] in 1e-4 degree integer steps
def enc(r):
    out = [round(r[0][0] * 1e4), round(r[0][1] * 1e4)]
    for a, b in zip(r, r[1:]): out += [round(b[0] * 1e4) - round(a[0] * 1e4), round(b[1] * 1e4) - round(a[1] * 1e4)]
    return out
data = [[enc(r) for r in poly] for poly in rings]
s = json.dumps(data, separators=(',', ':'))
open(os.path.join(HERE, 'water.json'), 'w').write(s)
print(f'tolerance {TOL:.0f} m: {len(polys)} water bodies, {npts} points, {len(s)/1e6:.2f} MB')
