"""Duluth, South Shore & Atlantic and its Mineral Range R.R. (a CP subsidiary; Brendan, 20 Nov 2026) -> traces/maritimes/dssa.geojson (read by mar_tracks with the other bank files).
Drawn as CP (own cp), like the Soo Line. Source: Mississippi Rails "Duluth South Shore & Atlantic.kmz" (Tony Howe and David Price; Brendan; raw file in the private repo,
traces/dssa/). Status: 'ok', except pieces marked abandoned or old alignment ('pre1948'), the White Pine branch (built 1952-53: 'post1948') and the Mineral Range's unnamed paths and
mine spurs ('later', not needed by the passenger trains). Ties: piece ends 150 - 600 m from another line get a straight tie (the loader ties ends within 150 m itself).
The Straits of Mackinac car ferry (Mackinac Transportation Co.), Mackinaw City dock - St. Ignace dock: a train ferry (own water) on a straight course between Brendan's
dock points; Brendan's lead from the St. Ignace dock.
Usage: python3 tools/mar_import_dssa.py <doc.kml or .kmz>"""
import json, math, os, re, sys, zipfile
import xml.etree.ElementTree as ET
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = sys.argv[1]
s = (zipfile.ZipFile(src).read([n for n in zipfile.ZipFile(src).namelist() if n.endswith('.kml')][0]) if src.endswith('.kmz') else open(src, 'rb').read())
K = '{http://www.opengis.net/kml/2.2}'
feats = []
def F(name, pts, note, status='ok', constituent='Duluth, South Shore & Atlantic', group='mississippi_rails', est=False, own='cp'):
    p = dict(own=own, name=name, constituent=constituent, branch='Duluth, South Shore & Atlantic', group=group, status=status, cost=1.0, note=note)
    if est: p['est'] = True
    return dict(type='Feature', properties=p, geometry=dict(type='LineString', coordinates=[[round(x, 7), round(y, 7)] for x, y in pts]))
def walk(e, folder):
    for c in e:
        if c.tag in (K + 'Folder', K + 'Document'):
            n = c.find(K + 'name'); walk(c, 'Mineral Range R.R.' if n is not None and 'Mineral Range' in (n.text or '') else folder)
        elif c.tag == K + 'Placemark':
            n = c.find(K + 'name'); nm = (n.text or '').strip() if n is not None else ''
            d = c.find(K + 'description'); desc = re.sub(r'<[^>]+>', ' ', (d.text or '') if d is not None else '').strip()
            pts = [tuple(map(float, x.split(',')[:2])) for q in c.iter(K + 'coordinates') for x in q.text.split()]
            if len(pts) < 2: continue
            yrs = [int(y) for y in re.findall(r'abandon\w*(?: approved)?[^0-9]{0,12}(?:\d{1,2}-){0,2}(\d{4})', desc, re.I)]   # 'abandoned 1903', 'abandonment approved 9-22-1927'
            if re.search(r'old alignment', nm, re.I) or (yrs and min(yrs) < 1948): st = 'pre1948'
            elif re.search(r'1952', desc): st = 'post1948'
            elif folder == 'Mineral Range R.R.' and (nm == 'Untitled Path' or re.search(r'Mine|spur|Mill|Tamarack|Mohawk|original', nm, re.I)): st = 'later'
            else: st = 'ok'
            if nm.startswith('Allouez MN to Nestoria'):   # abandoned west of Marengo Jct. in 1934 (Brendan, 20 Nov 2026): the trains use the Soo to Ashland and the NP on to Superior
                k = min(range(len(pts)), key=lambda i: (pts[i][0] + 90.8179367) ** 2 + (pts[i][1] - 46.4339916) ** 2)
                feats.append(F(f'{folder}: Allouez - Marengo Jct. (abandoned 1934)', pts[:k + 1], 'Mississippi Rails; the DSS&A abandoned its own line between Marengo Junction and Superior in 1934 and ran by trackage rights over the Soo Line and the Northern Pacific by Ashland and Iron River (Brendan, 20 Nov 2026)', 'pre1948', folder))
                feats.append(F(f'{folder}: Marengo Jct. - Nestoria', pts[k:], 'Mississippi Rails, KMZ supplied by Brendan', st, folder))
                continue
            feats.append(F(f'{folder}: {nm}', pts, 'Mississippi Rails (Tony Howe and David Price), KMZ supplied by Brendan' + (f'; KMZ note: {desc[:160]}' if desc else ''), st, folder))
walk(ET.fromstring(s), 'Duluth, South Shore & Atlantic')
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
    feats.append(F(f'DSS&A: tie, {a.split(": ")[-1]} - {b.split(": ")[-1]}', [e, q], f'tie (Claude): the piece ends {d * 1000:.0f} m from the other line', group='link'))
    print(f'  tie {d * 1000:.0f} m: {a} -> {b}')
NP = json.load(open(os.path.join(HERE, 'traces', 'dssa', 'brendan_np_superior_ashland.json')))['np_superior_ashland']
feats.append(F('Northern Pacific: Superior - Iron River - Ashland (Mississippi Rails; Brendan)', NP, "Brendan, 20 Nov 2026: the DSS&A by trackage rights since 1934 (KMZ note: built by the Northern Pacific RR 1881-85)", group='mississippi_rails', own='np', constituent='Northern Pacific'))
feats.append(F('Superior: the approach to the Soo Line station used by the DSS&A (Brendan)', json.load(open(os.path.join(HERE, 'traces', 'dssa', 'brendan_np_superior_ashland.json')))['superior_soo_approach'],
               "Brendan's trace, 20 Nov 2026", group='brendan', own='np', constituent='Northern Pacific'))
feats.append(F('Superior: gap between the approach and the end of the NP Superior - Ashland trace (est)', [(-92.0564246, 46.715331), (-92.0365866, 46.7004672)],
               'straight estimate (Claude): 2.2 km between the two traces', group='link', est=True, own='np'))
feats.append(F('DSS&A: Marengo Junction, the main line - the Soo Line Ashland line (tie at the crossing)', [(-90.8179367, 46.4339916), (-90.8175603, 46.4347037)],
               'tie (Claude): the DSS&A trains turn here onto the Soo Line (Wisconsin Central) for Ashland (84 m between the two traces at the crossing)', group='link'))
feats.append(F('DSS&A: St. Ignace, the lead to the car ferry dock (Brendan)', [(-84.72067136523755, 45.86573660638453), (-84.72001445489376, 45.86547872876946), (-84.7195510663993, 45.86535717533018),
               (-84.71864172444918, 45.86519983606163), (-84.71814945207575, 45.86519583913775), (-84.7170295807914, 45.86544662636462), (-84.71575189724673, 45.86573624098808)],
               "Brendan's trace, 20 Nov 2026", group='brendan'))
feats.append(F('Mackinaw City - St. Ignace car ferry (Straits of Mackinac)', [(-84.719617, 45.7799), (-84.715364, 45.865875)],
               "Train ferry (Brendan, 20 Nov 2026: drawn as a train ferry, like Mulgrave - Point Tupper): the Mackinac Transportation Co.'s car ferries between Brendan's dock points, Mackinaw City 45 46 47.64 N, 84 43 10.62 W and St. Ignace 45 51 57.15 N, 84 42 55.31 W. Course APPROXIMATE (straight).",
               group='link', own='water', constituent='Mackinac Transportation Co. car ferry (Straits of Mackinac)'))
json.dump(dict(type='FeatureCollection', features=feats), open(os.path.join(HERE, 'traces', 'maritimes', 'dssa.geojson'), 'w'))
from collections import Counter
print(len(feats), 'pieces', Counter(f['properties']['status'] for f in feats))
