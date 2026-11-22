"""Rutland Railroad (Brendan, 21 Nov 2026) -> traces/maritimes/rut.geojson (read by mar_tracks with the other bank files). Own 'rut' (forest green and yellow, the known livery).
Sources: Mississippi Rails "Rutland_RR_VT.kmz" and "Rutland_RR_NY.kmz" (Tony Howe and David Price; raw files in the private repo, traces/rut/); the B&M Troy - Hoosick Jct. - state line
(White Creek) from Brendan's Mississippi Rails placemarks (traces/rut/brendan_bm_troy_white_creek.json), own 'bm'.
Status: 'ok', except pieces abandoned before 1948 ('pre1948'). Ties: piece ends 150 - 600 m from another line get a straight tie.
Usage: python3 tools/mar_import_rut.py <Rutland_RR_VT.kmz> <Rutland_RR_NY.kmz>"""
import json, math, os, re, sys, zipfile
import xml.etree.ElementTree as ET
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
K = '{http://www.opengis.net/kml/2.2}'
def kml(src):
    z = zipfile.ZipFile(src); return ET.fromstring(z.read([n for n in z.namelist() if n.endswith('.kml')][0]))
feats = []
def F(name, pts, note, status='ok', own='rut', constituent='Rutland Railroad', group='mississippi_rails'):
    return dict(type='Feature', properties=dict(own=own, name=name, constituent=constituent, branch=constituent, group=group, status=status, cost=1.0, note=note),
                geometry=dict(type='LineString', coordinates=[[round(x, 7), round(y, 7)] for x, y in pts]))
for src in sys.argv[1:3]:
    for c in kml(src).iter(K + 'Placemark'):
        n = c.find(K + 'name'); nm = (n.text or '').strip() if n is not None else ''
        d = c.find(K + 'description'); desc = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', (d.text or '') if d is not None else '')).strip()
        for q in c.iter(K + 'coordinates'):
            pts = [tuple(map(float, x.split(',')[:2])) for x in q.text.split()]
            if len(pts) < 2: continue
            yrs = [int(y) for y in re.findall(r'abandon\w*(?: approved)?(?: effective)?[^0-9]{0,12}(?:\d{1,2}-){0,2}(\d{4})', desc, re.I)]
            st = 'pre1948' if (yrs and min(yrs) < 1948) or re.search(r'old alignment', nm, re.I) else 'ok'
            feats.append(F(f'Rutland: {nm}', pts, 'Mississippi Rails (Tony Howe and David Price), KMZ supplied by Brendan' + (f'; KMZ note: {desc[:160]}' if desc else ''), st))
B = json.load(open(os.path.join(HERE, 'traces', 'rut', 'brendan_bm_troy_white_creek.json')))
for p in B['pieces']: feats.append(F('Boston & Maine: ' + p['name'], [tuple(q) for q in p['coords']], B['source'], own='bm', constituent='Boston & Maine', group='brendan'))
def km(a, b): return math.hypot((a[0] - b[0]) * 111.32 * math.cos(math.radians(a[1])), (a[1] - b[1]) * 110.57)
ok = [(f['properties']['name'], [tuple(q) for q in f['geometry']['coordinates']], f['properties']['own']) for f in feats if f['properties']['status'] == 'ok']
ties = []
for i, (nm, c, o) in enumerate(ok):
    for e in (c[0], c[-1]):
        for j, (n2, c2, o2) in enumerate(ok):
            if j == i: continue
            best = min((km(e, q), q) for q in c2)
            if 0.15 < best[0] < 0.6 and not any(km(e, t[0]) < 0.01 and t[3] == n2 for t in ties) and not any(km(t[0], best[1]) < 0.01 for t in ties):
                ties.append((e, best[1], nm, n2, best[0], o))
for e, q, a, b, d, o in ties:
    feats.append(F(f'tie, {a.split(": ")[-1]} - {b.split(": ")[-1]}', [e, q], f'tie (Claude): the piece ends {d * 1000:.0f} m from the other line', own=o, group='link'))
# Burlington: the line from Rutland and the line north to Alburgh end 0.76 km apart at the Burlington station (the trains reverse there): a dashed straight estimate
f = F('Rutland: Burlington station - the line north (est)', [(-73.2214, 44.4798), (-73.2262, 44.4856)], 'straight estimate (Claude): the two Mississippi Rails pieces end 0.76 km apart at Burlington', group='link')
f['properties']['est'] = True; feats.append(f)
json.dump(dict(type='FeatureCollection', features=feats), open(os.path.join(HERE, 'traces', 'maritimes', 'rut.geojson'), 'w'))
from collections import Counter
print(len(ties), 'ties;', len(feats), 'pieces', Counter(f['properties']['status'] for f in feats))
