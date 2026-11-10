"""New Brunswick / western Nova Scotia pieces from Brendan's big OpenStreetMap export of the region (overpass-turbo, 9 Nov 2026; (c) OpenStreetMap
contributors, ODbL). Brendan: not a preferred source, but not rough either; its labels are inconsistent about which line is which. So the pieces are found
as shortest paths over the export's railway ways (rail, abandoned, razed; way ends within 80 m tied) between fixed points, and checked against the
Official Guide's miles (April 25, 1948). Ways of a line already on file are dropped from the ends of a path (SKIP).
    python3 tools/mar_import_osm_region.py /path/to/export.geojson
-> traces/maritimes/cn_osm_region.geojson (own cn), cp_osm_region.geojson (own cp), mcrp.geojson (Maritime Coal, Railway & Power, own mcrp)."""
import json, math, os, sys
import networkx as nx
from scipy.spatial import cKDTree
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, '..', 'traces', 'maritimes')
W = {}
for f in json.load(open(sys.argv[1]))['features']:
    p = f['properties']
    if not (p.get('railway') or p.get('abandoned:railway') or p.get('razed:railway')) or p.get('railway') in ('platform', 'station', 'halt'): continue
    if f['geometry']['type'] == 'LineString': W[p['@id'].split('/')[1]] = (p, [(round(x, 7), round(y, 7)) for x, y in f['geometry']['coordinates']])
def km(a, b): return math.hypot((a[0] - b[0]) * 111.32 * math.cos(math.radians((a[1] + b[1]) / 2)), (a[1] - b[1]) * 110.57)
G = nx.Graph()
for wid, (p, c) in W.items():
    for a, b in zip(c, c[1:]):
        if a != b and not G.has_edge(a, b): G.add_edge(a, b, w=km(a, b), wid=wid)
N = list(G.nodes); T = cKDTree([(x * 76, y * 111.2) for x, y in N])
for e in [n for n in N if G.degree(n) == 1]:
    for j in T.query_ball_point((e[0] * 76, e[1] * 111.2), 0.08):
        if N[j] != e and not G.has_edge(e, N[j]): G.add_edge(e, N[j], w=km(e, N[j]) * 3, wid='tie')
def snap(pt): return N[T.query((pt[0] * 76, pt[1] * 111.2))[1]]
def piece(a, b, skip=(), avoid=()):
    def wt(u, v, e):   # ways named in avoid (or with that old operator) cost 5 times: keeps a path off a parallel line of another railway
        p = W[e['wid']][0] if e['wid'] in W else {}
        return e['w'] * (5 if (p.get('name') in avoid or p.get('old_railway_operator') in avoid) else 1)
    P = nx.shortest_path(G, snap(a), snap(b), weight=wt)
    nm = [W[G[u][v]['wid']][0].get('name') if G[u][v]['wid'] in W else None for u, v in zip(P, P[1:])]
    i, j = 0, len(nm)
    while i < j and nm[i] in skip: i += 1
    while j > i and nm[j - 1] in skip: j -= 1
    pts = P[i:j + 1]; ways = []
    for u, v in zip(pts, pts[1:]):
        w = G[u][v]['wid']
        if not ways or ways[-1] != w: ways.append(w)
    return [list(x) for x in pts], ways, sum(km(u, v) for u, v in zip(pts, pts[1:])) / 1.609344
IC = ('Newcastle Subdivision', 'Subdivision Newcastle', 'Springhill Subdivision', 'Mont-Joli Subdivision', 'Subdivision Mont-Joli', 'Edmundston Subdivision', "Subdivision d'Edmundston")
NOTE = 'OpenStreetMap (c) OpenStreetMap contributors, ODbL; Brendan\'s regional export, 9 Nov 2026; path between fixed points, {} ways ({}). {}'
SPECS = [   # file, own, name, from, to, skip, note
    ('cn', 'cn', 'Saint John: European & North American track end - Union Station', (-66.02982, 45.31028), (-66.06450447009931, 45.276776220069436), (),
     'Replaces the estimated link (2.8 mi).'),
    ('cp', 'cp', 'Saint John Union Station - Westfield Beach (CP McAdam Subdivision)', (-66.06450447009931, 45.276776220069436), (-66.2319719, 45.3518393), (),
     'CP track; the CN Saint John Valley trains (Table 33) run over it: 13.8 mi, 14.0 printed.'),
    ('cn', 'cn', 'Saint John & Quebec Railway (Valley line): Westfield Beach - Gagetown - Oromocto - Fredericton', (-66.229536, 45.34961), (-66.6401, 45.95023), ('McAdam Subdivision',),
     'Table 33: Westfield Beach - Fredericton 69.8 mi printed.', ('McAdam Subdivision', 'CP', 'Canadian Pacific Railway', 'Fredericton Subdivision', 'Gibson Subdivision')),
    ('cn', 'cn', 'Saint John & Quebec Railway (Valley line): Fredericton - Woodstock', (-66.6401, 45.95023), (-67.598333, 46.152222), (), 'Table 33: 63.0 mi printed.'),
    ('cn', 'cn', 'Saint John & Quebec Railway (Valley line): Woodstock - Centreville', (-67.598333, 46.152222), (-67.71163, 46.430804), (), 'Table 33: 25.8 mi printed.'),
    ('cn', 'cn', 'Kent Northern: Kent Junction - Rexton - Richibucto', (-65.33683, 46.584266), (-64.868952, 46.681071), IC, 'Table 47: 26.4 mi printed.'),
    ('cn', 'cn', 'Chatham Branch: Nelson Junction - South Nelson - Chatham - Loggieville', (-65.59292, 46.95927), (-65.38395, 47.07181), IC,
     'Table 24 (Newcastle - Loggieville 17.7 mi printed). Replaces the estimated Nelson tie.'),
    ('cn', 'cn', 'Oxford Junction: Short Line - Intercolonial', (-63.87638, 45.69367), (-63.86, 45.68), IC, 'Closes the 204 m gap (the other leg in the export runs along the Intercolonial: not taken).'),
    ('cn', 'cn', 'International Railway: Tide Head - Upsalquitch - Kedgwick - St. Quentin - St. Leonard', (-66.767257, 47.983602), (-67.925, 47.1625), IC,
     'Table 36: the International leaves the Intercolonial at Tide Head (Campbellton - St. Leonard 111.9 mi printed). The Wikipedia trace (fid 9) into Campbellton is set aside.'),
    ('mcrp', 'mcrp', 'Maritime Coal, Railway & Power: Maccan - River Hebert - Joggins Mines', (-64.2523, 45.7238), (-64.4478, 45.6954), IC,
     'Official Guide, April 1948: Maccan - Joggins Mines 12 miles.'),
]
FILES = {}
for spec in SPECS:
    fn, own, name, a, b, skip, note = spec[:7]; c, ways, mi = piece(a, b, skip, spec[7] if len(spec) > 7 else ())
    print(f'{name[:70]:70s} {mi:6.1f} mi  {len(ways)} ways')
    FILES.setdefault(fn, []).append(dict(type='Feature', properties=dict(own=own, name=name, constituent=name.split(':')[0], branch='', status='ok', cost=1,
        note=NOTE.format(len(ways), ', '.join(w for w in ways if w != 'tie')[:400] + ('...' if len(', '.join(ways)) > 400 else ''), note)), geometry=dict(type='LineString', coordinates=c)))
for fn, v in FILES.items():
    json.dump(dict(type='FeatureCollection', features=v), open(os.path.join(OUT, {'cn': 'cn_osm_region', 'cp': 'cp_osm_region', 'mcrp': 'mcrp'}[fn] + '.geojson'), 'w'), separators=(',', ':'))
