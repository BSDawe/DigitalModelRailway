"""Michigan Central (Chicago - Detroit) and the New York Central main line (Buffalo - Albany) -> traces/maritimes/mc.geojson (read by mar_tracks). Own 'nyc'.
Brendan, 22 Nov 2026: "Can we map this out? I'm ok with the final approach to Central Station being dashed for the moment" (NYC Tables 6, 7, 9, 11).
Source: Mississippi Rails "NYC_Canada_Export.kmz" (Tony Howe and David Price; Brendan; raw file in the private repo, traces/lv/). Only the pieces the passenger trains use are
taken (named in MAIN below); the Hudson line, Albany and Grand Central are already in dh.geojson / nec.geojson, the Niagara Falls - Tonawanda pieces in lv.geojson.
- Syracuse: in 1948 the passenger trains ran over the West Shore line through the 1936 station (the KMZ's "Syracuse (1948)" note: "only NYC passenger deviation over west shore
  line"); the West Shore piece is cut to its Syracuse stretch (west of 76.055 W) and tied to the main line at East Syracuse. The old street line (Syracuse existing / abandoned) is left out.
- Batavia: through the town (the in-town pieces), not the later bypass.
- Chicago (Brendan, 22 Nov 2026): Central Station is Illinois Central property, the Michigan Central running in by trackage rights over the IC from Kensington; no trace yet, so a
  DASHED estimate (own 'ic') from the Michigan Central's west end (the Indiana state line) by Kensington and Woodlawn (63d Street) to Central Station. La Salle Street Station (NYC and
  Rock Island; the Twilight Limited, by Englewood and the Lake Shore & Michigan Southern to Porter): a DASHED estimate La Salle Street - Englewood - the Michigan Central west end.
- Buffalo: the International Railway Bridge, Brendan's traces (traces/lv/brendan_international_bridge.json; V211 replaced Claude's dashed estimate).
Usage: python3 tools/mar_import_mc.py <NYC_Canada_Export.kmz> <NYC_Chicago.kmz>"""
import json, math, os, re, sys, zipfile
import xml.etree.ElementTree as ET
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = sys.argv[1]
z = zipfile.ZipFile(src); s = z.read([n for n in z.namelist() if n.endswith('.kml')][0])
K = '{http://www.opengis.net/kml/2.2}'
MAIN = {   # Michigan Central main line, the Detroit River tunnel; N.Y.C. Buffalo - Albany; Buffalo - Black Rock
    'Michigan Central': ('Detroit to Ypsilanti MI', 'Ann Arbor to Ypsilanti MI', 'Jackson MI to Ann Arbor MI', 'Marshall to Jackson MI', 'Kalamazoo MI to Marshall MI',
                         'Michigan City IN to Kalamazoo MI', 'Gary IN to Michigan City IN', 'Untitled Path@-87.467', 'Michigan Central Tunnel'),
    'New York Central': ('Buffalo NY to Depew NY', 'Batavia NY to Depew NY', 'Batavia abandoned@-78.225', 'Batavia existing@-78.193', 'Batavia NY abandoned@-78.170',
                         'Batavia NY to Rochester NY', 'Syracuse NY to Rochester NY', 'Utica NY to Syracuse NY', 'Utica NY to Schenectady, NY', 'Schenectady NY to Albany NY',
                         'Buffalo NY to Black Rock NY', 'Buffalo to Black Rock existing', 'Black Rock NY to Tonawanda NY', 'Rotterdam Jct to Syracuse NY',
                         'Utica NY to Boonville NY', 'Remsen NY to Lake Clear Jct NY', 'Lake Clear Jct to Saranac Lake NY', 'Saranac NY to Lake Placid NY')}   # the Adirondack Division (V211)
feats = []
def F(name, pts, note, group='mississippi_rails', est=False, own='nyc', constituent='New York Central'):
    p = dict(own=own, name=name, constituent=constituent, branch=constituent, group=group, status='ok', cost=1.0, note=note)
    if est: p['est'] = True
    return dict(type='Feature', properties=p, geometry=dict(type='LineString', coordinates=[[round(x, 7), round(y, 7)] for x, y in pts]))
want = {n.split('@')[0]: [] for v in MAIN.values() for n in v}
for c in ET.fromstring(s).iter(K + 'Placemark'):
    n = c.find(K + 'name'); nm = (n.text or '').strip() if n is not None else ''
    if nm not in want: continue
    for q in c.iter(K + 'coordinates'):
        pts = [tuple(map(float, x.split(',')[:2])) for x in q.text.split()]
        if len(pts) >= 2: want[nm].append(pts)
for co, names in MAIN.items():
    for n in names:
        nm, _, lon = n.partition('@')
        cands = want[nm]
        if lon: cands = [c for c in cands if abs(c[0][0] - float(lon)) < 0.002]
        assert cands, n
        for pts in cands:
            if nm == 'Rotterdam Jct to Syracuse NY': pts = [p for p in pts if p[0] <= -76.055]   # the West Shore through Syracuse only (the 1948 passenger route)
            label = 'Michigan Central' if co == 'Michigan Central' else 'New York Central'
            feats.append(F(f'{label}: {nm}', pts, 'Mississippi Rails NYC_Canada_Export.kmz (Tony Howe and David Price), supplied by Brendan', constituent=label))
def km(a, b): return math.hypot((a[0] - b[0]) * 111.32 * math.cos(math.radians(a[1])), (a[1] - b[1]) * 110.57)
# Chicago (V211): Brendan's Mississippi Rails "NYC_Chicago.kmz" (22 Nov 2026; private repo traces/msrails/): the Michigan Central to Kensington, the Illinois Central main line
# (Kensington - Woodlawn - Central Station, own 'ic': the MC by trackage rights) with the Central Station connector and the MC - IC connector, and the New York Central's Lake Shore &
# Michigan Southern (Porter wye - the state line - Englewood - La Salle Street; Brendan: "a MC train to La Salle will diverge at Porter and take the main NYC line into La Salle Street").
# The V210 dashed estimates are gone.
CHI = {'IL/IN State Line to South Bend IN': 'nyc', 'LS&MS NYC': 'nyc', 'NYC-LaSalle Track': 'nyc', 'Terminal Track': 'nyc', 'Porter (Wye Track)': 'nyc', 'Untitled Path@-87.612': 'nyc',
       'Centralia to Chicago': 'ic', 'Central Station Connector': 'ic', 'MC-IC Connector': 'ic'}
if len(sys.argv) > 2:
    z2 = zipfile.ZipFile(sys.argv[2]); s2 = z2.read([n for n in z2.namelist() if n.endswith('.kml')][0])
    got = set()
    for c in ET.fromstring(s2).iter(K + 'Placemark'):
        n = c.find(K + 'name'); nm = (n.text or '').strip() if n is not None else ''
        for q in c.iter(K + 'coordinates'):
            pts = [tuple(map(float, x.split(',')[:2])) for x in q.text.split()]
            key = nm if nm in CHI else (f'{nm}@{pts[-1][0]:.3f}' if len(pts) > 1 else '')
            if key not in CHI or len(pts) < 2: continue
            got.add(key); own = CHI[key]
            if nm == 'Centralia to Chicago': pts = [p for p in pts if p[1] >= 41.60]   # the Chicago end only (Kensington - Central Station)
            feats.append(F(('Illinois Central: ' if own == 'ic' else 'New York Central: ') + nm, pts, 'Mississippi Rails NYC_Chicago.kmz (Tony Howe and David Price), supplied by Brendan',
                           own=own, constituent='Illinois Central' if own == 'ic' else 'New York Central'))
    assert got == set(CHI), set(CHI) - got
ICT = json.load(open(os.path.join(HERE, 'traces', 'lv', 'brendan_ic_terminal.json')))   # Brendan, 22 Nov 2026: the IC terminal track into Central Station
feats.append(F(ICT['name'] + ' (Brendan)', [tuple(q) for q in ICT['coords']], ICT['source'], group='brendan', own='ic', constituent='Illinois Central'))
# ties between the pieces' ends (150 m - 1 km apart: the KMZ draws the pieces separately)
ok = [(f['properties']['name'], [tuple(q) for q in f['geometry']['coordinates']]) for f in feats]
ties = []
for i, (nm, c) in enumerate(ok):
    for e in (c[0], c[-1]):
        best = min(((km(e, q), q, n2) for j, (n2, c2) in enumerate(ok) if j != i for q in c2), default=None)
        if best and 0.05 < best[0] < 1.0 and not any(km(e, t[0]) < 0.01 or (km(e, t[1]) < 0.01 and km(best[1], t[0]) < 0.01) for t in ties):
            ties.append((e, best[1], nm, best[2], best[0]))
for e, q, a, b, d in ties:
    feats.append(F(f'N.Y.C.: tie, {a.split(": ")[-1]} - {b.split(": ")[-1]}', [e, q], f'tie (Claude): the piece ends {d * 1000:.0f} m from the other piece', group='link'))   # all under 1 km: solid
print(len(ties), 'ties:', [(t[2].split(': ')[-1], t[3].split(': ')[-1], round(t[4] * 1000)) for t in ties])
# Buffalo: the International Railway Bridge, Brendan's traces (22 Nov 2026): A from the boundary over the bridge onto the Black Rock line towards Buffalo, B the leg north towards Tonawanda
TB = json.load(open(os.path.join(HERE, 'traces', 'lv', 'brendan_tonawanda_bypass.json')))   # Brendan, 22 Nov 2026: the Tonawanda bypass (early 20th century), in place of the KMZ's old route
feats.append(F(TB['name'] + ' (Brendan)', [tuple(q) for q in TB['coords']], TB['source'], group='brendan'))
IB = json.load(open(os.path.join(HERE, 'traces', 'lv', 'brendan_international_bridge.json')))
for pc in IB['pieces']:
    feats.append(F(f"Michigan Central: {pc['name']} (Brendan)", [tuple(q) for q in pc['coords']], IB['source'], group='brendan'))
json.dump(dict(type='FeatureCollection', features=feats), open(os.path.join(HERE, 'traces', 'maritimes', 'mc.geojson'), 'w'))
print(len(feats), 'pieces')
