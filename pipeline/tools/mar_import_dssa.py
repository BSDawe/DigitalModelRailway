"""Duluth, South Shore & Atlantic and its Mineral Range R.R. (a CP subsidiary; Brendan, 20 Nov 2026) -> traces/maritimes/dssa.geojson (read by mar_tracks with the other bank files).
Drawn as CP (own cp), like the Soo Line. Source: Mississippi Rails "Duluth South Shore & Atlantic.kmz" (Tony Howe and David Price; Brendan; raw file in the private repo,
traces/dssa/). Status: 'ok', except pieces marked abandoned or old alignment ('pre1948'), the White Pine branch (built 1952-53: 'post1948') and the Mineral Range's unnamed paths and
mine spurs ('later', not needed by the passenger trains). Ties: piece ends 150 - 600 m from another line get a straight tie (the loader ties ends within 150 m itself).
The Straits of Mackinac car ferry, Mackinaw City - St. Ignace: a dashed straight estimate (no trace; Mackinaw City point APPROXIMATE).
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
feats.append(F('DSS&A: Marengo Junction, the main line - the Soo Line Ashland line (tie at the crossing)', [(-90.8179367, 46.4339916), (-90.8175603, 46.4347037)],
               'tie (Claude): the DSS&A trains turn here onto the Soo Line (Wisconsin Central) for Ashland (84 m between the two traces at the crossing)', group='link'))
feats.append(F('DSS&A: the Straits of Mackinac car ferry, Mackinaw City - St. Ignace (est)', [(-84.7275, 45.7800), (-84.7155, 45.8625)],
               'straight estimate (Claude): the car ferry across the Straits (no trace); Mackinaw City point APPROXIMATE', group='link', est=True))
json.dump(dict(type='FeatureCollection', features=feats), open(os.path.join(HERE, 'traces', 'maritimes', 'dssa.geojson'), 'w'))
from collections import Counter
print(len(feats), 'pieces', Counter(f['properties']['status'] for f in feats))
