"""Springfield - New Haven - New York - Washington (Brendan, 19 Nov 2026: "the remaining tracks necessary for CN Montreal - Washington trains"; may be replaced later by PRR and
NYNH&H traces) -> traces/maritimes/nec.geojson (read by mar_tracks with the other track bank files).
- Source: Brendan's NEC2.geojson, an export of the U.S. national rail network (FRA North American Rail Network: Amtrak-owned lines, with the Metro-North pieces at New Rochelle);
  raw file in the private repo, traces/nec/NEC2.geojson. Kept: the arcs inside Springfield - Washington (lon -77.1 .. -71.9, lat 38.85 .. 42.3) of the network classes main (M),
  other (O) and industry (I: the Hell Gate Bridge approaches are coded I); yards and sidings left out.
- Owners in 1948 (drawn so): Massachusetts, Connecticut and Westchester (north of 40.87 N): the New Haven (own nh); the New York Connecting Railroad (Hell Gate Bridge, jointly PRR and
  New Haven: the union-station colour, own union) in the Bronx and Queens; Manhattan (the Penn Station tunnels) and New Jersey to Washington: the Pennsylvania (own prr).
- Brendan's New York traces (20 Nov 2026; traces/nec/brendan_ny_pieces.json, KMLs in the private repo): the New Haven Woodlawn Jct. - state line (kept to where it meets the
  FRA arcs at New Rochelle; the rest duplicates them), the New York Central Harlem line Mott Haven Jct. - White Plains (split at Woodlawn Jct., where the New Haven trace
  starts) and the Grand Central Terminal final approach (Park Avenue), tied to the Harlem trace (0.17 km). Owners: own nh and own nyc. For the Ambassador's New York section.
Usage: python3 tools/mar_import_nec.py <NEC2.geojson>"""
import json, os, sys
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
d = json.load(open(sys.argv[1]))
def own(st, c):
    lon = sum(p[0] for p in c) / len(c); lat = sum(p[1] for p in c) / len(c)
    if st in ('MA', 'CT'): return 'nh'
    if st == 'NY':
        if lat >= 40.87: return 'nh'
        return 'prr' if lon < -73.96 else 'union'
    return 'prr'
NAME = {'nh': 'New York, New Haven & Hartford', 'union': 'New York Connecting Railroad (Hell Gate Bridge; PRR and New Haven)', 'prr': 'Pennsylvania Railroad'}
feats = []
for f in d['features']:
    p = f['properties']
    if p['NET'] not in ('M', 'O', 'I'): continue
    for c in f['geometry']['coordinates']:
        if not all(-77.1 < q[0] < -71.9 and 38.85 < q[1] < 42.3 for q in c) or len(c) < 2: continue
        o = own(p['STATEAB'], c)
        feats.append(dict(type='Feature', properties=dict(own=o, name=f"{NAME[o]}: FRA arc {p['FRAARCID']} ({p['STATEAB']})", constituent=NAME[o], branch='Northeast Corridor', group='fra_narn',
                          status='ok', cost=1.0 if p['NET'] == 'M' else 1.3, note=f"FRA rail network (Brendan's NEC2.geojson, 19 Nov 2026); 2020s owner {p['RROWNER1']}, class {p['NET']}"),
                          geometry=dict(type='LineString', coordinates=[[round(q[0], 7), round(q[1], 7)] for q in c])))
import math
_k = math.cos(math.radians(40.9)); _m = lambda a, b: math.hypot((a[0] - b[0]) * _k * 111320, (a[1] - b[1]) * 111320)
NY = json.load(open(os.path.join(HERE, 'traces', 'nec', 'brendan_ny_pieces.json')))
nec_pts = [q for f in feats for q in f['geometry']['coordinates']]
def near_nec(q): return min(_m(q, r) for r in nec_pts)
def piece(o, name, c, **kw):
    feats.append(dict(type='Feature', properties=dict(own=o, name=name, constituent=o, branch='New York', group='brendan_ny', status='ok', cost=1.0,
                      note="Brendan's trace, 20 Nov 2026", **kw), geometry=dict(type='LineString', coordinates=c)))
# the New Haven from Woodlawn: up to where it meets the FRA arcs (New Rochelle), then onto the nearest FRA vertex
nh = NY['nh_woodlawn']['coords']; cut = next(i for i, q in enumerate(nh) if near_nec(q) < 30)
nh = nh[:cut + 1] + [min(nec_pts, key=lambda r: _m(nh[cut], r))]
# the Harlem line, split at the vertex nearest the New Haven trace's start (Woodlawn Jct.); the New Haven trace starts there
h = NY['nyc_harlem']['coords']; j = min(range(len(h)), key=lambda i: _m(h[i], nh[0]))
nh = [h[j]] + nh
piece('nh', 'New York, New Haven & Hartford: Woodlawn Jct. - New Rochelle', nh)
piece('nyc', 'New York Central (Harlem): Mott Haven Jct. - Woodlawn Jct.', h[:j + 1])
piece('nyc', 'New York Central (Harlem): Woodlawn Jct. - White Plains', h[j:])
piece('nyc', 'New York Central: Grand Central Terminal - Mott Haven (Park Avenue)', NY['nyc_gct']['coords'] + [h[0]])
json.dump(dict(type='FeatureCollection', features=feats), open(os.path.join(HERE, 'traces', 'maritimes', 'nec.geojson'), 'w'))
from collections import Counter
print(len(feats), 'pieces', Counter(f['properties']['own'] for f in feats))
