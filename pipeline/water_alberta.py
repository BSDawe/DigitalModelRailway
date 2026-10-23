"""Alberta lakes and wide rivers for the page's water layer, from Brendan's GeoPackage (alberta_water.gpkg: Statistics Canada hydro polygons for
Alberta, already simplified by him, one multipolygon in EPSG:3347) -> water_alberta.json, in the same compact form as water_embedded.json
(each ring [lon0, lat0, dlon, dlat, ...] in steps of 1e-4 degree). make_page.py puts the two together. Not a build step: run it by hand if the
GeoPackage changes.   python3 water_alberta.py"""
import json, os, sqlite3
from shapely import wkb
from pyproj import Transformer
HERE = os.path.dirname(os.path.abspath(__file__))
to_ll = Transformer.from_crs(3347, 4326, always_xy=True).transform
c = sqlite3.connect(os.path.join(HERE, 'alberta_water.gpkg'))
table, col = c.execute('select table_name, column_name from gpkg_geometry_columns').fetchone()
def enc(coords):
    q = []
    for x, y in coords:
        lon, lat = to_ll(x, y); p = (round(lon * 1e4), round(lat * 1e4))
        if not q or p != q[-1]: q.append(p)
    if len(q) < 4: return None
    out = [q[0][0], q[0][1]]
    for a, b in zip(q, q[1:]): out += [b[0] - a[0], b[1] - a[1]]
    return out
data, npts = [], 0
for (b,) in c.execute(f'select "{col}" from "{table}"'):
    env = {0: 0, 1: 32, 2: 48, 3: 48, 4: 64}[(b[3] >> 1) & 7]; g = wkb.loads(bytes(b[8 + env:]))
    for p in (g.geoms if g.geom_type.startswith('Multi') else [g]):
        ext = enc(p.exterior.coords)
        if not ext: continue
        rings = [ext] + [h for h in (enc(r.coords) for r in p.interiors) if h]
        data.append(rings); npts += sum(len(r) // 2 for r in rings)
s = json.dumps(data, separators=(',', ':'))
open(os.path.join(HERE, 'water_alberta.json'), 'w').write(s)
print(f'{len(data)} water bodies, {npts} points, {len(s) / 1e6:.2f} MB')
