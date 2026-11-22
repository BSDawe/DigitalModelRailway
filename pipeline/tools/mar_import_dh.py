"""Delaware & Hudson (Brendan, 21 Nov 2026) -> traces/maritimes/dh.geojson (read by mar_tracks with the other bank files). Own 'dh' (the D&H colour already in the page).
Sources: Mississippi Rails "Delaware__Hudson.kmz" (Tony Howe and David Price; raw file in the private repo, traces/dh/) and, for the D&H Montreal trains' run to New York over the
New York Central, the Hudson line from Brendan's Mississippi Rails "NYC_Canada_Export.kmz" (private repo traces/lv/): Albany Union Station - Poughkeepsie - Spuyten Duyvil -
Mott Haven Jct. (joining the Harlem line / Park Avenue pieces already in nec.geojson) and the Troy & Greenbush (Rensselaer - Troy). Own 'nyc'.
Status: 'ok'; 'pre1948' for old alignments (except the two at Saratoga Springs, where the 1948 station stood: the D&H line was moved off them only later; Brendan's station point
sits where they meet), pieces abandoned before 1948 and the Gravity Railroad; 'later' for nothing. Ties: piece ends 150 - 600 m from another line get a straight tie.
Troy Union Station (Brendan's point, 42.7316 N, 73.6867 W): over the Troy Union Railroad and Brendan's bridge trace (V206; V205 had dashed estimates).
Usage: python3 tools/mar_import_dh.py <Delaware__Hudson.kmz> <NYC_Canada_Export.kmz> <Troy_Union_RR.kmz>"""
import json, math, os, re, sys, zipfile
import xml.etree.ElementTree as ET
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
K = '{http://www.opengis.net/kml/2.2}'
def kml(src):
    z = zipfile.ZipFile(src); return ET.fromstring(z.read([n for n in z.namelist() if n.endswith('.kml')][0]))
feats = []
def F(name, pts, note, status='ok', own='dh', constituent='Delaware & Hudson', group='mississippi_rails', est=False):
    p = dict(own=own, name=name, constituent=constituent, branch=constituent, group=group, status=status, cost=1.0, note=note)
    if est: p['est'] = True
    return dict(type='Feature', properties=p, geometry=dict(type='LineString', coordinates=[[round(x, 7), round(y, 7)] for x, y in pts]))
SARATOGA_OK = ('Saratoga Springs NY old alignment', 'Saratoga Springs old alignment')
for c in kml(sys.argv[1]).iter(K + 'Placemark'):
    n = c.find(K + 'name'); nm = (n.text or '').strip() if n is not None else ''
    d = c.find(K + 'description'); desc = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', (d.text or '') if d is not None else '')).strip()
    for q in c.iter(K + 'coordinates'):
        pts = [tuple(map(float, x.split(',')[:2])) for x in q.text.split()]
        if len(pts) < 2: continue
        yrs = [int(y) for y in re.findall(r'abandon\w*(?: approved)?[^0-9]{0,12}(?:\d{1,2}-){0,2}(\d{4})', desc, re.I)]
        if nm in SARATOGA_OK: st = 'ok'
        elif re.search(r'old alignment|Gravity RR', nm) or (yrs and min(yrs) < 1948) or desc.lower() == 'abandoned': st = 'pre1948'
        else: st = 'ok'
        feats.append(F(f'Delaware & Hudson: {nm}', pts, 'Mississippi Rails (Tony Howe and David Price), KMZ supplied by Brendan' + (f'; KMZ note: {desc[:160]}' if desc else ''), st))
NYC_KEEP = ('Albany to Poughkeepsie NY', 'New York City to Poughkeepsie NY', 'Spuyten Duyvil NY to Mott Haven Jct', 'Albany Union Station', 'Troy NY to Greenbush NY')
for c in kml(sys.argv[2]).iter(K + 'Placemark'):
    n = c.find(K + 'name'); nm = (n.text or '').strip() if n is not None else ''
    if nm not in NYC_KEEP: continue
    for q in c.iter(K + 'coordinates'):
        pts = [tuple(map(float, x.split(',')[:2])) for x in q.text.split()]
        if len(pts) >= 2: feats.append(F(f'New York Central: {nm}', pts, 'Mississippi Rails NYC_Canada_Export.kmz, supplied by Brendan', own='nyc', constituent='New York Central'))
def km(a, b): return math.hypot((a[0] - b[0]) * 111.32 * math.cos(math.radians(a[1])), (a[1] - b[1]) * 110.57)
ok = [(f['properties']['name'], [tuple(q) for q in f['geometry']['coordinates']]) for f in feats if f['properties']['status'] == 'ok']
ties = []
for i, (nm, c) in enumerate(ok):
    for e in (c[0], c[-1]):
        for j, (n2, c2) in enumerate(ok):
            if j == i: continue
            best = min((km(e, q), q) for q in c2)
            if 0.15 < best[0] < 0.6 and not any(km(e, t[0]) < 0.01 and t[3] == n2 for t in ties) and not any(km(t[0], best[1]) < 0.01 for t in ties):
                ties.append((e, best[1], nm, n2, best[0]))
for e, q, a, b, d in ties:
    feats.append(F(f'tie, {a.split(": ")[-1]} - {b.split(": ")[-1]}', [e, q], f'tie (Claude): the piece ends {d * 1000:.0f} m from the other line', group='link'))
# Troy (Brendan, 21 Nov 2026): the Troy Union Railroad (jointly N.Y.C., D&H and B&M; Mississippi Rails "Troy_Union_RR.kmz", private repo traces/dh/) into Troy Union Station,
# own 'union' (the short terminal railways' colour), and Brendan's trace of the D&H bridge from Green Island (traces/dh/brendan_troy_bridge.json, own dh). Replaces the V205 dashed estimates.
if len(sys.argv) > 3:
    for c in kml(sys.argv[3]).iter(K + 'Placemark'):
        n = c.find(K + 'name'); nm = (n.text or '').strip() if n is not None else ''
        for q in c.iter(K + 'coordinates'):
            pts = [tuple(map(float, x.split(',')[:2])) for x in q.text.split()]
            if len(pts) >= 2: feats.append(F(f'Troy Union Railroad: {nm}', pts, 'Mississippi Rails Troy_Union_RR.kmz, supplied by Brendan (jointly N.Y.C., D&H, B&M)', own='union', constituent='Troy Union Railroad'))
B = json.load(open(os.path.join(HERE, 'traces', 'dh', 'brendan_troy_bridge.json')))
feats.append(F('D&H: Green Island - Troy bridge (Brendan)', B['coords'], B['source'], group='brendan'))
TU = [f for f in feats if f['properties']['own'] == 'union']
for f in [f for f in feats if f['properties']['name'] == 'New York Central: Troy NY to Greenbush NY']:   # the Troy & Greenbush end onto the Troy Union
    e = f['geometry']['coordinates'][-1]
    best = min(((km(e, q), q) for g in TU for q in g['geometry']['coordinates']), key=lambda x: x[0])
    feats.append(F('N.Y.C.: Troy & Greenbush - Troy Union Railroad tie', [e, best[1]], f'tie (Claude): {best[0] * 1000:.0f} m', own='nyc', constituent='New York Central', group='link'))
json.dump(dict(type='FeatureCollection', features=feats), open(os.path.join(HERE, 'traces', 'maritimes', 'dh.geojson'), 'w'))
from collections import Counter
print(len(ties), 'ties;', len(feats), 'pieces', Counter(f['properties']['status'] for f in feats))
