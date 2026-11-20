"""Soo Line (Minneapolis, St. Paul & Sault Ste. Marie, with the leased Wisconsin Central), 19 Nov 2026 -> traces/maritimes/soo.geojson (read by mar_tracks with the
other track bank files). Drawn as CP (own cp; Brendan, 19 Nov 2026: "Draw as CP, Soo label", like the Central Vermont and the GTW under CN).
- Source: Mississippi Rails "Minneapolis St Paul & Saulte St Marie.kmz" (Tony Howe and David Price; Brendan; raw file in the private repo, traces/soo/kmz/doc.kml).
- Status: 'ok' throughout (the Soo Line's own tables, Brendan's Official Guide pages of 19 Nov 2026, run in the Ontario step as CP lines labelled Soo Line). The CP Soo lines
  west of Minneapolis built earlier (the Winnipeger, the Mountaineer) stay in the Saskatchewan step on traces/soo/soo_mn_nd.geojson, cut from the same KMZ. Pieces marked
  abandoned or old alignment in the KMZ are 'pre1948'; the North Dakota mine spurs, Riverdale and the Garrison Dam relocations (New Town, the Custer and Ironton "new
  route" pieces) are 'post1948'.
- Superior - Duluth: the Soo connection to the Northern Pacific and the NP Grassy Point bridge (Brendan's traces, 19 Nov 2026; own np); and the final approach to the
  Duluth Soo depot (Brendan's trace).
- Chicago: the Baltimore & Ohio Chicago Terminal from Forest Park into Grand Central Station (Brendan's traces, 19 Nov 2026; own bo, B&O dark blue).
- Minneapolis (Milwaukee Road station) - St. Paul Union Station: Brendan's Milwaukee Road trace (traces/milw/mpls_stpaul.geojson; own milw), as for the Winnipeger.
Usage: python3 tools/mar_import_soo.py <doc.kml or .kmz>"""
import json, os, re, sys, zipfile
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = sys.argv[1]
s = (zipfile.ZipFile(src).read([n for n in zipfile.ZipFile(src).namelist() if n.endswith('.kml')][0]) if src.endswith('.kmz') else open(src, 'rb').read()).decode('utf-8', 'replace')
feats = []
def F(own, name, pts, note, status='ok', constituent='Soo Line', group='mississippi_rails', est=False):
    p = dict(own=own, name=name, constituent=constituent, branch='Soo Line', group=group, status=status, cost=1.0, note=note)
    if est: p['est'] = True
    return dict(type='Feature', properties=p, geometry=dict(type='LineString', coordinates=[[round(x, 7), round(y, 7)] for x, y in pts]))
# the Placemarks, with the folder they sit in (Wisconsin Central or the Soo proper)
import xml.etree.ElementTree as ET
K = '{http://www.opengis.net/kml/2.2}'
def walk(e, folder):
    for c in e:
        if c.tag in (K + 'Folder', K + 'Document'):
            n = c.find(K + 'name'); walk(c, 'Wisconsin Central' if n is not None and 'Wisconsin Central' in (n.text or '') else folder)
        elif c.tag == K + 'Placemark':
            n = c.find(K + 'name'); nm = (n.text or '').strip() if n is not None else ''
            d = c.find(K + 'description'); desc = re.sub(r'<[^>]+>', ' ', (d.text or '') if d is not None else '').strip()
            pts = [tuple(map(float, x.split(',')[:2])) for q in c.iter(K + 'coordinates') for x in q.text.split()]
            if len(pts) < 2: continue
            if re.search(r'old alignment|abandon', nm + ' ' + desc, re.I): st = 'pre1948'
            elif re.search(r'Falkirk|Coal Creek|Riverdale|new route|Newtown', nm): st = 'post1948'
            else: st = 'ok'
            if nm.startswith('Hilbert WI to Menasha'): feats.append(F('milw', f'Milwaukee Road: {nm} (Soo trackage rights)', pts, 'Mississippi Rails; Milwaukee Road track, the Soo by trackage rights (KMZ note; Brendan, 19 Nov 2026)', st, 'Milwaukee Road')); continue
            feats.append(F('cp', f'{folder}: {nm}', pts, 'Mississippi Rails (Tony Howe and David Price), KMZ supplied by Brendan' + (f'; KMZ note: {desc[:160]}' if desc else ''), st, folder))
walk(ET.fromstring(s.encode('utf-8')), 'Soo Line')
M = json.load(open(os.path.join(HERE, 'traces', 'milw', 'mpls_stpaul.geojson')))['features'][0]
feats.append(dict(type='Feature', properties=dict(own='milw', name='Milwaukee Road: Minneapolis (Milwaukee Road station) - St. Paul Union Station (Brendan)', constituent='Milwaukee Road',
              branch='Soo Line', group='brendan', status='ok', cost=1.0, note="Brendan's trace, 19 Oct 2026 (traces/milw/mpls_stpaul.geojson)"), geometry=M['geometry']))
# Junction ties: a branch whose end lies 150 - 600 m from other track (the loader ties ends within 150 m itself) gets a straight tie to the nearest point of that track
import math
def km(a, b): return math.hypot((a[0] - b[0]) * 111.32 * math.cos(math.radians(a[1])), (a[1] - b[1]) * 110.57)
ok = [(f['properties']['name'], [tuple(q) for q in f['geometry']['coordinates']]) for f in feats if f['properties']['status'] == 'ok']
ties = []
for i, (nm, c) in enumerate(ok):
    for e in (c[0], c[-1]):
        for j, (n2, c2) in enumerate(ok):                                 # each other line separately: Owen ends 200 m from the Abbotsford - Chippewa Falls line it crosses
            if j == i: continue
            best = min((km(e, q), q) for q in c2)
            if 0.15 < best[0] < 0.6 and not any(km(e, t[0]) < 0.01 and t[3] == n2 for t in ties) and not any(km(t[0], best[1]) < 0.01 for t in ties):
                ties.append((e, best[1], nm, n2, best[0]))
for e, q, a, b, d in ties:
    feats.append(F('cp', f'Soo Line: tie, {a.split(": ")[-1]} - {b.split(": ")[-1]}', [e, q], f'tie (Claude): the piece ends {d * 1000:.0f} m from the other line', group='link'))
    print(f'  tie {d * 1000:.0f} m: {a} -> {b}')
BO = json.load(open(os.path.join(HERE, 'traces', 'soo', 'brendan_soo_pieces.json')))   # Brendan, 19 Nov 2026: Grand Central Station is B&O property; the B&O is dark blue
for k, nm in (('grand_central', 'Grand Central Station - Ogden Ave. / Kenton'), ('west', 'Kenton - Forest Park')):
    feats.append(dict(type='Feature', properties=dict(own='bo', name=f'Baltimore & Ohio Chicago Terminal: {nm} (Brendan)', constituent='Baltimore & Ohio', branch='Soo Line', group='brendan',
                  status='ok', cost=1.0, note="Brendan's trace, 19 Nov 2026 (traces/soo/brendan_soo_pieces.json): the Soo Line into Grand Central Station"), geometry=dict(type='LineString', coordinates=BO[k])))
feats.append(F('cp', 'Soo Line: Superior, connection to the Northern Pacific (Brendan)', BO['superior_np_connection'], "Brendan's trace, 19 Nov 2026", group='brendan'))
feats.append(dict(type='Feature', properties=dict(own='np', name='Northern Pacific: Grassy Point bridge, Superior - Duluth (Brendan)', constituent='Northern Pacific', branch='Soo Line', group='brendan',
              status='ok', cost=1.0, note="Brendan's trace, 19 Nov 2026: the Soo trains' way from Superior to West Duluth and Duluth"), geometry=dict(type='LineString', coordinates=BO['np_grassy_point_bridge'])))
feats.append(F('cp', 'Soo Line: Duluth, final approach to the Soo depot (Brendan)', BO['duluth_final_approach'], "Brendan's trace, 19 Nov 2026: the Soo Line depot (shared with the DSS&A and the DM&N) to the NP Grassy Point line", group='brendan'))
feats.append(F('cp', 'Soo Line: Ridgeland branch, Barron - Ridgeland (Brendan)', BO['ridgeland_branch'], "Brendan's trace, 19 Nov 2026 (Table 17)", group='brendan'))
feats.append(F('cp', 'Soo Line: Cameron - Rice Lake (Brendan)', BO['rice_lake_branch'], "Brendan's trace, 19 Nov 2026 (Table 22)", group='brendan'))
feats.append(F('cp', 'Soo Line: Sault Ste. Marie, Mich. (trace end) - the International Bridge - the CP station, Sault Ste. Marie, Ont. (est)', [(-84.3634230, 46.5033144), (-84.3219190, 46.5101980)],
               'straight estimate (Claude): the Soo trains use the CP station on the Ontario side (Brendan, 19 Nov 2026); no trace of the International Bridge yet', group='link', est=True))
feats.append(dict(type='Feature', properties=dict(own='milw', name='Milwaukee Road: Menasha - Neenah (Mississippi Rails; Brendan)', constituent='Milwaukee Road', branch='Soo Line', group='mississippi_rails',
              status='ok', cost=1.0, note="Brendan, 19 Nov 2026: Menasha station is reached by trackage rights over the MILW (Table 16, Hilbert Jct. - Menasha - Neenah)"), geometry=dict(type='LineString', coordinates=BO['milw_menasha_neenah'])))
json.dump(dict(type='FeatureCollection', features=feats), open(os.path.join(HERE, 'traces', 'maritimes', 'soo.geojson'), 'w'))
from collections import Counter
print(len(feats), 'pieces', Counter(f['properties']['status'] for f in feats))
