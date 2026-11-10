"""The Dominion Atlantic Railway (CP subsidiary) from the Wikipedia railway maps, Brendan's pull (QGIS, dominion_atlantic_railway.geojson, 10 Nov 2026):
Yarmouth - Digby (Western Counties), Digby - Annapolis, Annapolis - Windsor (Windsor & Annapolis), Windsor - Truro (Midland), Windsor - Windsor Junction
(Nova Scotia Railway, Windsor Branch), Kentville - Kingsport (Cornwallis Valley), and the North Mountain Railway.
    python3 tools/mar_import_dar.py /path/to/dominion_atlantic_railway.geojson
-> traces/maritimes/dar.geojson (own cp: drawn like the other CP subsidiaries, the E&N and the Quebec Central - Brendan, 10 Nov 2026; the Windsor Branch to
Windsor Jct. is the DAR's own). Junction vertices: an end of any line in traces/maritimes within 30 m of a DAR line gets a vertex put into the
DAR line there (the router ties track at points), as tools/mar_import_cgr.py does for its lines."""
import glob, html, json, math, os, re, sys
from shapely.geometry import LineString, Point
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, '..', 'traces', 'maritimes')
def _m(x, y): return (x * 111320 * math.cos(math.radians(45)), y * 110570)
NOTE = 'Wikipedia railway map (Wikimedia Commons map data: {}), pulled by Brendan, 10 Nov 2026.'
feats = []
for f in json.load(open(sys.argv[1]))['features']:
    p = f['properties']; con = html.unescape(re.sub('<[^>]+>', '', p.get('title') or '')).strip(); br = (p.get('description') or '').strip()
    src = re.search(r'title=([^&]+)', p.get('source_map') or ''); src = src.group(1).replace('+', ' ').replace('%28', '(').replace('%29', ')') if src else '?'
    feats.append(dict(type='Feature', properties=dict(own='cp', name=f'{con}: {br}' if br else con, constituent=con, branch=br, status='ok', cost=1,
                      note=NOTE.format(src)), geometry=dict(type='LineString', coordinates=[[round(x, 6), round(y, 6)] for x, y in f['geometry']['coordinates']])))
ENDS = [tuple(c) for f in feats for c in (f['geometry']['coordinates'][0], f['geometry']['coordinates'][-1])]
for fn in glob.glob(os.path.join(OUT, '*.geojson')):
    if os.path.basename(fn) == 'dar.geojson': continue
    for f in json.load(open(fn))['features']:
        if f['geometry']['type'] == 'LineString': c = f['geometry']['coordinates']; ENDS += [tuple(c[0]), tuple(c[-1])]
for f in feats:
    c = [tuple(x) for x in f['geometry']['coordinates']]; L = LineString([_m(*x) for x in c]); add = []
    for e in ENDS:
        P = Point(_m(*e))
        if L.distance(P) < 30 and min(math.dist(_m(*x), _m(*e)) for x in c) > 30: add.append(L.project(P))
    if not add: continue
    cum = [0.0]
    for a, b in zip(c, c[1:]): cum.append(cum[-1] + math.dist(_m(*a), _m(*b)))
    for d in sorted(set(add), reverse=True):
        i = max(k for k in range(len(cum) - 1) if cum[k] <= d); q = L.interpolate(d); k = 111320 * math.cos(math.radians(45))
        c.insert(i + 1, (round(q.x / k, 6), round(q.y / 110570, 6))); cum.insert(i + 1, d)
    f['geometry']['coordinates'] = [list(x) for x in c]; print(f"junction vertices: {len(set(add))} into {f['properties']['name']}")
json.dump(dict(type='FeatureCollection', features=feats), open(os.path.join(OUT, 'dar.geojson'), 'w'), separators=(',', ':'))
for f in feats:
    c = f['geometry']['coordinates']; print(f"{f['properties']['name'][:55]:55s} {sum(math.dist(_m(*a), _m(*b)) for a, b in zip(c, c[1:])) / 1609.34:6.1f} mi")
