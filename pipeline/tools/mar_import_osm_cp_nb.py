"""Canadian Pacific's New Brunswick lines from Brendan's regional OpenStreetMap export (9 Nov 2026; (c) OpenStreetMap contributors, ODbL). Brendan: CP's
N.B. track is in that export (10 Nov 2026); its labels are inconsistent. Seed: every railway way (rail, abandoned, razed) named as a CP subdivision or
carrying a CP-family old operator (CP, New Brunswick Railway, Shore Line Railway, Tobique Valley, the Minto coal railways), inside New Brunswick (the
Maine side of the border is left for the U.S. folders). Gaps between seed pieces are bridged by the shortest railway path through the export's other
ways when it is under 4 km. Ways already in cp_osm_region.geojson (Saint John Union - Westfield Beach) are left out. Pieces are merged into lines.
    python3 tools/mar_import_osm_cp_nb.py /path/to/export.geojson   -> traces/maritimes/cp_osm_nb.geojson (own cp)"""
import json, math, os, sys
import networkx as nx
from shapely.geometry import LineString, MultiLineString
from shapely.ops import linemerge
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, '..', 'traces', 'maritimes')
CPN = {'McAdam Subdivision', 'Mattawamkeag Subdivision', 'St Stephen Subdivision', 'St Andrews Subdivision', 'St. Andrews Subdivision', 'Milltown Spur', 'Shore Line Subdivision',
       'Shore line Subdivision', 'Fredericton Subdivision', 'Gibson Subdivision', 'Shogomoc Subdivision', 'Aroostook Subdivision', 'Edmundston Subdivision',
       "Subdivision d'Edmundston", 'Tobique Subdivision', 'Minto Subdivision', 'Southampton Subdivision', 'West Saint John Spur', 'Chipman Wye'}
CPO = {'CP', 'Canadian Pacific Railway', 'New Brunswick Railway', 'Shore Line Railway', 'Tobique Valley Railway', 'Fredericton & Grand Lake Coal & Railway', 'New Brunswick Coal and Railway'}
def in_nb(x, y):   # rough N.B. - Maine border, for CP's lines: west of Vanceboro (the Mattawamkeag line), west of the boundary line (Aroostook - Fort Fairfield),
    if y < 45.70: return x > -67.435   # south of the Saint John River above Grand Falls
    if y < 47.07: return x > -67.79
    return x > -67.79 - (y - 47.07) / 0.29 * 0.55
def km(a, b): return math.hypot((a[0] - b[0]) * 111.32 * math.cos(math.radians((a[1] + b[1]) / 2)), (a[1] - b[1]) * 110.57)
W = {}
for f in json.load(open(sys.argv[1]))['features']:
    p = f['properties']
    if f['geometry']['type'] != 'LineString' or not (p.get('railway') or p.get('abandoned:railway') or p.get('razed:railway')) or p.get('railway') in ('platform', 'station', 'halt'): continue
    W[p['@id'].split('/')[1]] = (p, [(round(x, 7), round(y, 7)) for x, y in f['geometry']['coordinates']])
done = set()
for f in json.load(open(os.path.join(OUT, 'cp_osm_region.geojson')))['features']: done |= {(round(x, 7), round(y, 7)) for x, y in f['geometry']['coordinates']}
seed = {w for w, (p, c) in W.items() if (p.get('name') in CPN or p.get('old_railway_operator') in CPO) and sum(in_nb(*q) for q in c) > len(c) / 2
        and not all(q in done for q in c)}
G = nx.Graph()
for w, (p, c) in W.items():
    for a, b in zip(c, c[1:]):
        if a != b: G.add_edge(a, b, w=km(a, b), wid=w)
from scipy.spatial import cKDTree
_N = list(G.nodes); _T = cKDTree([(x * 76, y * 111.2) for x, y in _N])
for e in [n for n in _N if G.degree(n) == 1]:   # way ends within 80 m of another way's node: tied (the export's ways do not always share nodes)
    for j in _T.query_ball_point((e[0] * 76, e[1] * 111.2), 0.08):
        if _N[j] != e and not G.has_edge(e, _N[j]): G.add_edge(e, _N[j], w=km(e, _N[j]) * 3, wid='tie')
S = nx.Graph()
for w in seed:
    c = W[w][1]; S.add_edges_from(zip(c, c[1:]))
comps = list(nx.connected_components(S)); ends = []
for i, cp in enumerate(comps):
    for n in cp:
        if S.degree(n) == 1: ends.append((i, n))
added = set(); TIES = set()   # tie edges a path used: written out as short connectors
for i, n in ends:   # bridge each loose seed end to the nearest other seed component within 4 km of railway
    dist, path = nx.single_source_dijkstra(G, n, cutoff=4.0, weight='w')
    best = min(((d, m) for m, d in dist.items() if m not in comps[i] and m in S and d > 0), default=None)
    if best:
        P = path[best[1]]; added |= {G[u][v]['wid'] for u, v in zip(P, P[1:])} - seed - {'tie'}; TIES |= {(u, v) for u, v in zip(P, P[1:]) if G[u][v]['wid'] == 'tie'}
# NOT in the export (10 Nov 2026): Woodstock - Hartland, and the Gibson Subdivision from Gibson (Fredericton) to about Upper Kingsclear - traces wanted.
# Lines whose OSM ways are mostly unlabelled: the shortest path between fixed points (CN-named ways 5x dearer), added whole.
CNN = {'Newcastle Subdivision', 'Napadogan Subdivision', 'Sussex Subdivision', 'Springhill Subdivision', 'Oromocto Subdivision', 'Valley Line', 'Centreville Subdivision', 'Pelletier Subdivision'}
def wt(u, v, e): p = W[e['wid']][0] if e['wid'] in W else {}; return e['w'] * (5 if p.get('name') in CNN or 'Canadian National' in str(p.get('operator')) else 1)
def node(pt): return min(G.nodes, key=lambda n: km(n, pt))
PAIRS = [('Fredericton Jct. - Fredericton', (-66.6186, 45.6623), (-66.6401, 45.9502)), ('McAdam - Debec - Woodstock', (-67.3264, 45.5939), (-67.5983, 46.1522)),
         ('Hartland - Florenceville - Bath - Aroostook', (-67.5153, 46.2988), (-67.7183, 46.7886)), ('Aroostook - Perth - Grand Falls', (-67.7183, 46.7886), (-67.7392, 47.0469)),
         ('Grand Falls - Edmundston', (-67.7392, 47.0469), (-68.3228, 47.3672)),
         ('Perth - Plaster Rock', (-67.7, 46.74), (-67.395, 46.9097)), ('Fredericton - Minto - Chipman', (-66.6300, 45.9600), (-65.8775, 46.1778)),
         ('Chipman - Norton', (-65.8775, 46.1778), (-65.70, 45.64)), ('Watt Jct. - St. Stephen', (-67.17, 45.42), (-67.2775, 45.1947))]
for nm, a, b in PAIRS:
    try: P = nx.shortest_path(G, node(a), node(b), weight=wt)
    except nx.NetworkXNoPath: print(f'{nm:35s} NO PATH'); continue
    ws = {G[u][v]['wid'] for u, v in zip(P, P[1:])} - {'tie'}; TIES |= {(u, v) for u, v in zip(P, P[1:]) if G[u][v]['wid'] == 'tie'}
    print(f'{nm:35s} {sum(G[u][v]["w"] for u, v in zip(P, P[1:])) / 1.609:6.1f} mi, {len(ws - seed - added)} ways added'); added |= ws - seed
lines = linemerge(MultiLineString([LineString(W[w][1]) for w in (seed | added) - {'tie'}] + [LineString([u, v]) for u, v in TIES]))
geoms = list(lines.geoms) if lines.geom_type == 'MultiLineString' else [lines]
feats = []
for g in geoms:
    c = [[round(x, 7), round(y, 7)] for x, y in g.coords]
    if sum(km(a, b) for a, b in zip(c, c[1:])) < 0.3 and len(geoms) > 1 and not any(tuple(c[0]) in t or tuple(c[-1]) in t for t in TIES): continue
    feats.append(dict(type='Feature', properties=dict(own='cp', name='Canadian Pacific (N.B.)', constituent='Canadian Pacific', branch='', status='ok', cost=1,
        note='OpenStreetMap (c) OpenStreetMap contributors, ODbL; Brendan\'s regional export, 9 Nov 2026; CP-family ways in N.B. and the short gaps between them (tools/mar_import_osm_cp_nb.py).'),
        geometry=dict(type='LineString', coordinates=c)))
json.dump(dict(type='FeatureCollection', features=feats), open(os.path.join(OUT, 'cp_osm_nb.geojson'), 'w'), separators=(',', ':'))
print(f'seed {len(seed)} ways, bridges {len(added)} ways, {len(feats)} lines, {sum(sum(km(a, b) for a, b in zip(f["geometry"]["coordinates"], f["geometry"]["coordinates"][1:])) for f in feats) / 1.609:.0f} mi')
