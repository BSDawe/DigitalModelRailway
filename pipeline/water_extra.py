"""Water beyond B.C. and Alberta (October 2026), from Brendan's files:
  places/wa/wawater_simplified.geojson  Washington (Puget Sound, the Columbia, the Snake, lakes): EPSG:2927, US survey feet
  traces/alaska/simp_north_coast.gpkg   the Gulf of Alaska, Prince William Sound and Cook Inlet: EPSG:3347
The Washington Puget Sound is better drawn than the Canadian data's (Brendan, 10 October 2026), so the Canadian water south of the
international boundary is cut away (US_SIDE, an approximate line down the Strait of Georgia, Boundary Pass, Haro Strait and the Strait of Juan
de Fuca) and the Washington layer used there instead.
Writes, for the page (make_page.py): water_bc_cut.json (water_embedded.json less Puget Sound), water_wa.json, water_ak.json; and for the
steamer lanes (sea.py): water_extra.pkl (EPSG:3347: the US side to cut, and the Washington and Alaska water to add).
Not a build step: run it by hand if the files change.   python3 water_extra.py"""
import json, os, pickle, sqlite3
from shapely import wkb
from shapely.geometry import LineString, Polygon, shape
from shapely.ops import transform, unary_union
from pyproj import Transformer
HERE = os.path.dirname(os.path.abspath(__file__))
ll_from_2927 = Transformer.from_crs(2927, 4326, always_xy=True).transform
to_3347 = Transformer.from_crs(4326, 3347, always_xy=True).transform
ll_from_3347 = Transformer.from_crs(3347, 4326, always_xy=True).transform
# the US side of the boundary, lon/lat (approximate where it runs through the straits)
US_SIDE = Polygon([(-126.5, 48.49), (-124.73, 48.49), (-124.0, 48.29), (-123.25, 48.25), (-123.20, 48.40), (-123.25, 48.55), (-123.25, 48.68),
                   (-123.12, 48.73), (-123.00, 48.78), (-123.32, 49.0), (-110.0, 49.0), (-110.0, 44.0), (-126.5, 44.0)])

def enc_poly(p):
    def enc(coords):
        q = []
        for lon, lat in coords:
            r = (round(lon * 1e4), round(lat * 1e4))
            if not q or r != q[-1]: q.append(r)
        if len(q) < 4: return None
        out = [q[0][0], q[0][1]]
        for a, b in zip(q, q[1:]): out += [b[0] - a[0], b[1] - a[1]]
        return out
    ext = enc(p.exterior.coords)
    return [ext] + [h for h in (enc(r.coords) for r in p.interiors) if h] if ext else None
def dec(poly):
    rings = []
    for r in poly:
        lon, lat = r[0], r[1]; pts = [(lon / 1e4, lat / 1e4)]
        for i in range(2, len(r), 2): lon += r[i]; lat += r[i + 1]; pts.append((lon / 1e4, lat / 1e4))
        rings.append(pts)
    return Polygon(rings[0], rings[1:])
def parts(g): return [g] if g.geom_type == 'Polygon' else [p for p in getattr(g, 'geoms', []) if p.geom_type == 'Polygon']
def write(name, polys):
    data = [e for e in (enc_poly(p) for p in polys) if e]
    s = json.dumps(data, separators=(',', ':')); open(os.path.join(HERE, name), 'w').write(s)
    print(f'{name}: {len(data)} polygons, {sum(len(r) // 2 for d in data for r in d)} points, {len(s) / 1e6:.2f} MB')

# Washington (read first: the cut is where its Puget Sound is)
g = json.load(open(os.path.join(HERE, 'places', 'wa', 'wawater_simplified.geojson')))
wa = unary_union([transform(ll_from_2927, shape(f['geometry'])) for f in g['features']])
if not wa.is_valid: wa = wa.buffer(0)
# The Washington file has Puget Sound proper (south of Admiralty Inlet and Deception Pass) but not the Strait of Juan de Fuca, the San Juan
# Islands or Bellingham Bay: the Canadian water is cut only south of a line across Admiralty Inlet and Deception Pass, and kept everywhere else (the Washington
# rivers and lakes simply lie over it: the page fills each polygon, so an overlap does not show).
# The line: down the Quimper Peninsula to Point Wilson (the Strait of Juan de Fuca is left alone), across Admiralty Inlet (Point Wilson - Admiralty Head), up Whidbey Island to Deception Pass and across Skagit Bay to the mainland.
CUT = Polygon([(-123.25, 46.9), (-123.25, 47.6), (-123.0, 47.8), (-122.80, 48.05), (-122.754, 48.144), (-122.680, 48.162), (-122.655, 48.405), (-122.60, 48.41),
               (-122.45, 48.41), (-121.9, 48.41), (-121.9, 46.9)])
# B.C. water with Puget Sound cut away
bc = []
for poly in json.load(open(os.path.join(HERE, 'water_embedded.json'))):
    p = dec(poly)
    if not p.is_valid: p = p.buffer(0)
    if p.intersects(CUT): bc += [q for q in parts(p.difference(CUT)) if q.area > 1e-6]
    else: bc += parts(p)
write('water_bc_cut.json', bc)
write('water_wa.json', parts(wa))
# Alaska
c = sqlite3.connect(os.path.join(HERE, 'traces', 'alaska', 'simp_north_coast.gpkg'))
table, col = c.execute('select table_name, column_name from gpkg_geometry_columns').fetchone()
ak3347 = []
for (b,) in c.execute(f'select "{col}" from "{table}"'):
    env = {0: 0, 1: 32, 2: 48, 3: 48, 4: 64}[(b[3] >> 1) & 7]; geom = wkb.loads(bytes(b[8 + env:]))
    ak3347.append(geom if geom.is_valid else geom.buffer(0))
ak3347 = unary_union(ak3347)
write('water_ak.json', parts(transform(ll_from_3347, ak3347)))
# The mouth of Admiralty Inlet (Brendan, 10 October 2026): a strip neither layer covers, between the Canadian data's straight shore from Point
# Wilson towards Fort Ebey and the north edge of the Washington Puget Sound. A hand polygon over the open water, kept a few hundred metres off
# the shores of Point Wilson and Whidbey Island (Admiralty Head, Ebey's Landing, Fort Ebey).
FILL = LineString([(-122.7505, 48.1475), (-122.7200, 48.1530), (-122.6890, 48.1600)]).buffer(0.0045, cap_style=2)   # the strip along the cut line (about 400 m each side)
# Tongass Narrows at Ketchikan (Brendan, 15 October 2026: ships leaving Ketchikan for the north went south first): the layer lacks the narrows
# north of the town, so a strip of water along its middle to the Guard Islands
TONGASS = LineString([(-131.640, 55.335), (-131.655, 55.346), (-131.672, 55.356), (-131.700, 55.372), (-131.722, 55.386), (-131.740, 55.398)]).buffer(0.0025, cap_style=1)
FILL = unary_union([FILL, TONGASS])
open(os.path.join(HERE, 'water_fill.json'), 'w').write(json.dumps([enc_poly(p) for p in parts(FILL)], separators=(',', ':')))
# The Yukon (Brendan, 13 October 2026): traces/yukon/yukon_water.gpkg, the Yukon River, Lake Laberge and the Stewart River (StatCan hydro,
# EPSG:3347, from 60 N), and traces/yukon/bc_north_water.gpkg (northern B.C., 54.75 to 60.65 N: Bennett, Nares and Tagish Lakes, Taku Arm).
# Bennett Lake is 678 m short of Nares Lake at the Carcross narrows: a short water join there for the Tutshi.
def gpkg(fn):
    c = sqlite3.connect(os.path.join(HERE, fn)); table, col = c.execute('select table_name, column_name from gpkg_geometry_columns').fetchone()
    out = []
    for (b,) in c.execute(f'select "{col}" from "{table}"'):
        env = {0: 0, 1: 32, 2: 48, 3: 48, 4: 64}[(b[3] >> 1) & 7]; g = wkb.loads(bytes(b[8 + env:])); out.append(g if g.is_valid else g.buffer(0))
    return unary_union(out)
from shapely.geometry import LineString
narrows = transform(to_3347, LineString([(-134.7122, 60.1677), (-134.7004, 60.1699)])).buffer(60)
north3347 = unary_union([gpkg('traces/yukon/yukon_water.gpkg'), gpkg('traces/yukon/bc_north_water.gpkg'), narrows])
write('water_north.json', [q for q in parts(transform(ll_from_3347, north3347.simplify(80))) if q.area > 5e-5])
# Saskatchewan and Manitoba (Brendan, 17 October 2026): places/sk_water/saskman3.gpkg, his simplified selection (the Saskatchewan rivers, Lake
# Winnipeg, Lake Manitoba and the larger lakes; StatCan hydro, EPSG:3347). Drawn only; no boats on it.
write('water_sk.json', [q for q in parts(transform(ll_from_3347, gpkg('places/sk_water/saskman3.gpkg').simplify(100))) if q.area > 5e-5])
# for the lanes
pickle.dump(dict(cut=transform(to_3347, CUT), add=unary_union([transform(to_3347, wa), ak3347, transform(to_3347, FILL), north3347])),
            open(os.path.join(HERE, 'water_extra.pkl'), 'wb'))
print('water_extra.pkl written')
