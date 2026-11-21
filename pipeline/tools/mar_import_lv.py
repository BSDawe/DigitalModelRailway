"""Lehigh Valley R.R. (Brendan, 20 Nov 2026) -> traces/maritimes/lv.geojson (read by mar_tracks with the other bank files). Own 'lv'.
Source: Mississippi Rails "Lehigh_Valley.kmz" (Tony Howe and David Price; Brendan; raw file in the private repo, traces/lv/). Status: 'ok', except pieces abandoned before 1948 or
old alignments ('pre1948'), sidings, spurs and the historic-map folders ('later'), except the historic-map pieces within 2 km of the Buffalo station
(the terminal tracks are only there). Ties: piece ends 150 - 600 m from another line get a straight tie.
Niagara Falls (Brendan, 20 Nov 2026): the L.V. ran as far north as its own track went (Niagara Jct., North Tonawanda, by the Depew & Tonawanda line) and on by N.Y.C. trackage rights
to Niagara Falls; trains came over the bridge into the N.Y.C. Niagara Falls station and backed out onto the line along the top of the gorge. Brendan's trace of the connection from
the station onto the gorge line (traces/lv/brendan_niagara_gorge_connection.json, own nyc); the station at his point. The N.Y.C. between the gorge line and Niagara Jct. is not on
file: a straight estimate (dashed) until a trace comes.
Usage: python3 tools/mar_import_lv.py <Lehigh_Valley.kmz>"""
import json, math, os, re, sys, zipfile
import xml.etree.ElementTree as ET
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = sys.argv[1]
s = (zipfile.ZipFile(src).read([n for n in zipfile.ZipFile(src).namelist() if n.endswith('.kml')][0]) if src.endswith('.kmz') else open(src, 'rb').read())
K = '{http://www.opengis.net/kml/2.2}'
feats = []
def F(name, pts, note, status='ok', constituent='Lehigh Valley', group='mississippi_rails', est=False, own='lv'):
    p = dict(own=own, name=name, constituent=constituent, branch='Lehigh Valley', group=group, status=status, cost=1.0, note=note)
    if est: p['est'] = True
    return dict(type='Feature', properties=p, geometry=dict(type='LineString', coordinates=[[round(x, 7), round(y, 7)] for x, y in pts]))
BUF = (-78.875422, 42.877464)   # the L.V. Buffalo station (Brendan, 20 Nov 2026: 42 52 38.87 N, 78 52 31.52 W)
LATER = ('LV Sidings', 'Shown on 1917', 'Shown on 1915')
def walk(e, folder):
    for c in e:
        if c.tag in (K + 'Folder', K + 'Document'):
            n = c.find(K + 'name'); nm = (n.text or '').strip() if n is not None else ''
            walk(c, nm if c.tag == K + 'Folder' else folder)
        elif c.tag == K + 'Placemark':
            n = c.find(K + 'name'); nm = (n.text or '').strip() if n is not None else ''
            d = c.find(K + 'description'); desc = re.sub(r'<[^>]+>', ' ', (d.text or '') if d is not None else '').strip()
            for q in c.iter(K + 'coordinates'):
                pts = [tuple(map(float, x.split(',')[:2])) for x in q.text.split()]
                if len(pts) < 2: continue
                yrs = [int(y) for y in re.findall(r'abandon\w*(?: approved)?[^0-9]{0,12}(?:\d{1,2}-){0,2}(\d{4})', desc, re.I)]
                if re.search(r'old alignment|abandoned before', nm + ' ' + desc, re.I) or (yrs and min(yrs) < 1948): st = 'pre1948'
                elif any(folder.startswith(x) for x in LATER) and min(math.hypot((x - BUF[0]) * 81.5, (y - BUF[1]) * 111.0) for x, y in pts) < 2.0: st = 'ok'   # the Buffalo terminal: only in the historic-map folders
                elif any(folder.startswith(x) for x in LATER) or re.search(r'spur|siding', nm, re.I): st = 'later'
                else: st = 'ok'
                feats.append(F(f'Lehigh Valley ({folder}): {nm}', pts, 'Mississippi Rails (Tony Howe and David Price), KMZ supplied by Brendan' + (f'; KMZ note: {desc[:160]}' if desc else ''), st))
walk(ET.fromstring(s), 'Lehigh Valley')
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
    feats.append(F(f'L.V.: tie, {a.split(": ")[-1]} - {b.split(": ")[-1]}', [e, q], f'tie (Claude): the piece ends {d * 1000:.0f} m from the other line', group='link'))
print(len(ties), 'ties')
G = json.load(open(os.path.join(HERE, 'traces', 'lv', 'brendan_niagara_gorge_connection.json')))
g = [tuple(q) for q in G['coords']]; STA = tuple(G['station']['lonlat']); BOUNDARY = (-79.05833, 43.10923); NIAGARA_JCT = (-78.8370446, 43.019476)
feats.append(F('N.Y.C.: the Suspension Bridge approach, the international boundary - the Niagara Falls station junction', [BOUNDARY, g[0]], 'tie (Claude): 0.4 km over the bridge approach',
               group='link', own='nyc', constituent='New York Central'))
feats.append(F('N.Y.C.: Niagara Falls station track (Brendan\'s station point)', [g[0], STA], "Brendan's station point, 20 Nov 2026 (0.2 km from his connection trace)", group='brendan', own='nyc', constituent='New York Central'))
feats.append(F(G['name'] + ' (Brendan)', g, G['source'], group='brendan', own='nyc', constituent='New York Central'))
feats.append(F('N.Y.C.: Niagara Falls (gorge line) - Niagara Jct., North Tonawanda (est)', [g[-1], NIAGARA_JCT], 'straight estimate (Claude): the N.Y.C. line along the river is not on file yet (trace wanted)',
               group='link', est=True, own='nyc', constituent='New York Central'))
json.dump(dict(type='FeatureCollection', features=feats), open(os.path.join(HERE, 'traces', 'maritimes', 'lv.geojson'), 'w'))
from collections import Counter
print(len(feats), 'pieces', Counter(f['properties']['status'] for f in feats))
