#!/usr/bin/env python3
"""Build the map's own tiled basemap: water from Brendan's layers and province/state borders, cut into tiles at several levels of detail.

  python3 basemap/build_tiles.py            writes basemap/tiles/index.json and basemap/tiles/<z>/<x>_<y>.json

Sources
- Water: the water layers the page has always drawn (pipeline/water_*.json, made by pipeline/water_extra.py and water_alberta.py from the
  Statistics Canada, Washington State and Alaska polygons Brendan supplied). They are merged, so where two layers overlap there is one water.
- Borders: Natural Earth 1:10m, provinces and states (admin 1) and the international boundary on land (admin 0), public domain; cut to the
  map's part of the continent and kept in basemap/sources/.

Tiles are in the page's own projection (the Lambert conformal conic in page_template.html, metres, y down, Vancouver at the origin), so the
page draws them as they are. If the projection in the page changes, change PROJ here to match and rebuild.

Level z covers the map with 2^z x 2^z squares of side SIDE / 2^z. Each level is simplified to TOL(z) = side / 1024 (about a pixel when a
tile is drawn 1024 pixels across); the last level (tiles of 64 km or less) keeps the source detail. Water polygons are cut a little larger
than their tile, so neighbouring tiles overlap and no seam shows. A tile holds:
  {"w": [polygon, ...], "b": [[kind, line], ...]}    polygon = [ring, ...]; ring or line = [x0, y0, dx, dy, ...] in whole metres
  kind: 0 international boundary, 1 province or state boundary
Only tiles with something in them are written; index.json lists them by level."""
import json, math, os, sys
import numpy as np
from shapely.geometry import Polygon, MultiPolygon, LineString, MultiLineString, box, mapping, shape
from shapely.ops import unary_union
from shapely.strtree import STRtree
from shapely import set_precision

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); PIPE = os.path.join(ROOT, 'pipeline')
OUT = os.path.join(HERE, 'tiles'); SRC = os.path.join(HERE, 'sources')
PROJ = dict(kind='lcc-sphere', R=6371008, lat1=49, lat2=61, lon0=-122.5, origin=[-122.5, 49.12])   # must match P() in page_template.html
EXTENT = (-170.0, 38.0, -50.0, 72.0)                           # lon/lat box the borders are cut to
FINEST = 64000                                                  # the last level's tiles are at most this many metres across
WATER_FILES = ['water_bc_cut.json', 'water_wa.json', 'water_ak.json', 'water_fill.json', 'water_north.json', 'water_sk.json', 'water_alberta.json', 'water_east.json']

def lcc():
    r = math.pi / 180; R = PROJ['R']; p1, p2, l0 = PROJ['lat1'] * r, PROJ['lat2'] * r, PROJ['lon0'] * r
    t = lambda p: np.tan(math.pi / 4 + p / 2)
    n = math.log(math.cos(p1) / math.cos(p2)) / math.log(t(p2) / t(p1)); F = math.cos(p1) * t(p1) ** n / n
    def raw(lon, lat):
        rho = R * F / np.power(t(np.asarray(lat) * r), n); th = n * (np.asarray(lon) * r - l0)
        return rho * np.sin(th), rho * np.cos(th)
    ox, oy = raw(*PROJ['origin'])
    return lambda lon, lat: (lambda q: (q[0] - ox, q[1] - oy))(raw(lon, lat))
P = lcc()

def proj_coords(c):
    a = np.asarray(c, dtype=float); x, y = P(a[:, 0], a[:, 1]); return np.column_stack([x, y])

def water_geoms():
    """each water body as the page fills it (even-odd over its rings), projected"""
    out = []
    for f in WATER_FILES:
        p = os.path.join(PIPE, f)
        if not os.path.exists(p): continue
        for poly in json.load(open(p)):
            rings = [proj_coords(np.cumsum(np.asarray(r, dtype=float).reshape(-1, 2), axis=0) / 1e4) for r in poly]
            rings = [r for r in rings if len(r) >= 3]
            if not rings: continue
            g = Polygon(rings[0], rings[1:])                        # the water files write the outline first, then the islands
            if not g.is_valid: g = g.buffer(0)
            if not g.is_empty: out.append(g)
    return out

def border_geoms():
    """Natural Earth lines cut to EXTENT, cached in sources/ (the download is 23 MB)"""
    os.makedirs(SRC, exist_ok=True); out = []
    for kind, name in ((0, 'ne_10m_admin_0_boundary_lines_land'), (1, 'ne_10m_admin_1_states_provinces_lines')):
        cut = os.path.join(SRC, name + '_cut.geojson')
        if not os.path.exists(cut):
            full = os.path.join(SRC, name + '.geojson')
            if not os.path.exists(full):
                sys.exit(f'missing {full}: download it from https://github.com/nvkelso/natural-earth-vector/tree/master/geojson')
            fc = json.load(open(full)); keep = []; ext = box(*EXTENT)
            for ft in fc['features']:
                if not ft.get('geometry'): continue
                g = shape(ft['geometry'])
                if not g.intersects(ext): continue
                if kind == 1 and ft['properties'].get('ADM0_A3') not in ('CAN', 'USA'): continue
                keep.append({'type': 'Feature', 'properties': {}, 'geometry': mapping(g.intersection(ext))})
            json.dump({'type': 'FeatureCollection', 'features': keep}, open(cut, 'w'))
        for ft in json.load(open(cut))['features']:
            g = shape(ft['geometry'])
            for ln in (g.geoms if hasattr(g, 'geoms') else [g]):
                if ln.geom_type == 'LineString' and len(ln.coords) > 1: out.append((kind, LineString(proj_coords(ln.coords))))
    return out

def enc(coords):
    a = np.round(np.asarray(coords)).astype(np.int64)
    keep = np.ones(len(a), bool); keep[1:] = np.any(a[1:] != a[:-1], axis=1); a = a[keep]
    if len(a) < 2: return None
    d = a.copy(); d[1:] -= a[:-1]
    return d.ravel().tolist()

def polys(g):
    if g.is_empty: return []
    if g.geom_type == 'Polygon': return [g]
    if g.geom_type == 'MultiPolygon': return list(g.geoms)
    if hasattr(g, 'geoms'): return [q for h in g.geoms for q in polys(h)]
    return []

def lines(g):
    if g.is_empty: return []
    if g.geom_type == 'LineString': return [g]
    if hasattr(g, 'geoms'): return [q for h in g.geoms for q in lines(h)]
    return []

def main():
    print('reading water'); W = water_geoms()
    print(f'  {len(W)} bodies; merging'); water = unary_union(W)
    print('reading borders'); B = border_geoms()
    xs = [water.bounds[0], water.bounds[2]] + [b[1].bounds[i] for b in B for i in (0, 2)]
    ys = [water.bounds[1], water.bounds[3]] + [b[1].bounds[i] for b in B for i in (1, 3)]
    x0, y0 = math.floor(min(xs) / 1000) * 1000, math.floor(min(ys) / 1000) * 1000
    side = max(max(xs) - x0, max(ys) - y0); side = math.ceil(side / 1024) * 1024
    zmax = 0
    while side / 2 ** zmax > FINEST: zmax += 1
    print(f'  world {side / 1000:.0f} km square from ({x0:.0f}, {y0:.0f}); levels 0-{zmax}, finest tiles {side / 2 ** zmax / 1000:.1f} km')
    index = dict(proj=PROJ, origin=[x0, y0], side=side, zmax=zmax, tol=[], tiles={}, sources=['Water: Brendan Dawe, from Statistics Canada, '
                 'Washington State Department of Ecology and Alaska polygons', 'Borders: Natural Earth (public domain)'])
    if os.path.isdir(OUT):
        for d, _, fs in os.walk(OUT, topdown=False):
            for f in fs: os.remove(os.path.join(d, f))
    os.makedirs(OUT, exist_ok=True)
    total = 0
    for z in range(zmax + 1):
        s = side / 2 ** z; tol = 0 if z == zmax else s / 1024; index['tol'].append(tol)
        wz = water.simplify(tol, preserve_topology=True) if tol else water
        small = (6 * tol) ** 2                                      # lakes and islands under about 6 x 6 pixels are left out at this level
        wparts = []
        for p in polys(wz):
            if tol and p.area < small: continue
            if tol: p = Polygon(p.exterior, [h for h in p.interiors if Polygon(h).area >= small])
            wparts.append(p)
        bz = [(k, ln.simplify(tol) if tol else ln) for k, ln in B]
        wtree = STRtree(wparts); btree = STRtree([ln for _, ln in bz])
        n = int(2 ** z); names = []; ov = max(2.0, 2 * tol)
        os.makedirs(os.path.join(OUT, str(z)), exist_ok=True)
        for tx in range(n):
            for ty in range(n):
                bx = box(x0 + tx * s - ov, y0 + ty * s - ov, x0 + (tx + 1) * s + ov, y0 + (ty + 1) * s + ov)
                tile = {'w': [], 'b': []}
                for i in wtree.query(bx, predicate='intersects'):
                    for p in polys(wparts[i].intersection(bx)):
                        rings = [enc(p.exterior.coords)] + [enc(h.coords) for h in p.interiors]
                        rings = [r for r in rings if r and len(r) >= 6]
                        if rings: tile['w'].append(rings)
                bx0 = box(x0 + tx * s, y0 + ty * s, x0 + (tx + 1) * s, y0 + (ty + 1) * s)
                for i in btree.query(bx0, predicate='intersects'):
                    for ln in lines(bz[i][1].intersection(bx0)):
                        e = enc(ln.coords)
                        if e: tile['b'].append([bz[i][0], e])
                if not tile['w'] and not tile['b']: continue
                txt = json.dumps(tile, separators=(',', ':'))
                open(os.path.join(OUT, str(z), f'{tx}_{ty}.json'), 'w').write(txt); names.append(f'{tx}_{ty}'); total += len(txt)
        index['tiles'][str(z)] = names
        print(f'  level {z}: {len(names)} tiles, tolerance {tol:.0f} m')
    json.dump(index, open(os.path.join(OUT, 'index.json'), 'w'), separators=(',', ':'))
    print(f'basemap: {sum(len(v) for v in index["tiles"].values())} tiles, {total / 1e6:.1f} MB')

if __name__ == '__main__': main()
