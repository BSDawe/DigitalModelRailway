#!/usr/bin/env python3
"""Water for Ontario and the east (Brendan, 23 October 2026): places/east_water/eastern_lakes_and_ocean.gpkg, his simplified selection from
Statistics Canada hydro (EPSG:3347): the Great Lakes, Lake of the Woods, Rainy Lake, the larger Ontario lakes and the Atlantic side.
Writes water_east.json in the page's water format (rings delta-encoded in 1e-4 degrees), drawn by make_page.py and cut into the basemap
tiles by basemap/build_tiles.py. Drawn only: no steamer lanes use it yet (a Great Lakes boat would need it added to water_extra.pkl).

Kept separate from water_extra.py so that adding it does not rewrite water_extra.pkl (which would make boats_build re-route every lane)."""
import json, os, sqlite3
from shapely import wkb
from shapely.ops import transform, unary_union
from pyproj import Transformer
HERE = os.path.dirname(os.path.abspath(__file__))
ll_from_3347 = Transformer.from_crs(3347, 4326, always_xy=True).transform

def gpkg(fn):
    c = sqlite3.connect(os.path.join(HERE, fn)); table, col = c.execute('select table_name, column_name from gpkg_geometry_columns').fetchone()
    out = []
    for (b,) in c.execute(f'select "{col}" from "{table}"'):
        env = {0: 0, 1: 32, 2: 48, 3: 48, 4: 64}[(b[3] >> 1) & 7]; g = wkb.loads(bytes(b[8 + env:])); out.append(g if g.is_valid else g.buffer(0))
    return unary_union(out)

def enc(coords):
    out, prev = [], None
    for lon, lat in coords:
        r = (round(lon * 1e4), round(lat * 1e4))
        if r == prev: continue
        out += list(r) if prev is None else [r[0] - prev[0], r[1] - prev[1]]; prev = r
    return out

def parts(g): return [g] if g.geom_type == 'Polygon' else [p for p in getattr(g, 'geoms', []) if p.geom_type == 'Polygon']

polys = [q for q in parts(transform(ll_from_3347, gpkg('places/east_water/eastern_lakes_and_ocean.gpkg').simplify(100))) if q.area > 5e-5]
data = [[r for r in [enc(p.exterior.coords)] + [enc(h.coords) for h in p.interiors] if len(r) >= 6] for p in polys]
s = json.dumps([d for d in data if d], separators=(',', ':')); open(os.path.join(HERE, 'water_east.json'), 'w').write(s)
print(f'water_east.json: {len(data)} bodies, {len(s) / 1e6:.2f} MB')
