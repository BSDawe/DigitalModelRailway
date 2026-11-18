"""Grand Trunk Western (CN) track, 18 Nov 2026 -> traces/maritimes/gtw.geojson (own cn; read by mar_tracks with the other track bank files).
- The GTW system: Mississippi Rails "Grand_Trunk_Western.kmz" (Tony Howe and David Price; Brendan; raw file in the private repo, traces/msrails/).
- Brendan's own pieces (traces/gtw/brendan_gtw_pieces.json): Brush Street (Milwaukee Jct. - the Detroit riverfront), the old St. Clair Tunnel (Port Huron - Sarnia), and the line into
  Chicago: the GTW from Elsdon east to the Chicago & Western Indiana and the C&WI north into Dearborn Station (41 52 18.60 N, 87 37 45.18 W), picked by Claude as the shortest clean
  path through Brendan's Chicago export (Chicago_GTW_Export.kmz, 321 OSM pieces) (C&WI part own cwi: the joint terminal line).
- A straight link (est, dashed) Ferrysburg - Muskegon (not in the trace).
- A straight link (est, dashed) from the end of the Brush Street trace to the Brush Street station point used since V90 (about 800 m along the riverfront).
Usage: python3 tools/mar_import_gtw.py <Grand_Trunk_Western.kmz>"""
import json, math, os, re, sys, zipfile
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
z = zipfile.ZipFile(sys.argv[1]); s = z.read([n for n in z.namelist() if n.endswith('.kml')][0]).decode('utf-8', 'replace').replace('&amp;', '&').replace('&apos;', "'")
def F(own, name, pts, note, group='mississippi_rails', est=False):
    p = dict(own=own, name=name, constituent='Grand Trunk Western' if own == 'cn' else 'Chicago & Western Indiana', branch='Grand Trunk Western', group=group,
             status='ok', cost=1.0, note=note)
    if est: p['est'] = True
    return dict(type='Feature', properties=p, geometry=dict(type='LineString', coordinates=[[round(x, 7), round(y, 7)] for x, y in pts]))
feats = []
for pm in re.findall(r'<Placemark>.*?</Placemark>', s, re.S):
    n = re.search(r'<name>(.*?)</name>', pm, re.S); nm = n.group(1).strip() if n else ''
    pts = [tuple(map(float, x.split(',')[:2])) for c in re.findall(r'<coordinates>(.*?)</coordinates>', pm, re.S) for x in c.split()]
    if len(pts) > 1: feats.append(F('cn', 'Grand Trunk Western: ' + (nm or 'piece'), pts, 'Mississippi Rails (Tony Howe and David Price), KMZ supplied by Brendan, 18 Nov 2026'))
B = json.load(open(os.path.join(HERE, 'traces', 'gtw', 'brendan_gtw_pieces.json')))
feats.append(F('cn', 'Grand Trunk Western: Brush Street (Brendan)', B['brush'], "Brendan's trace, 18 Nov 2026", 'brendan'))
feats.append(F('cn', 'Grand Trunk Western: St. Clair Tunnel, Port Huron - Sarnia (Brendan)', B['tunnel'], "Brendan's trace, 18 Nov 2026", 'brendan'))
feats.append(F('cn', 'Grand Trunk Western: Brush Street trace end - Brush Street station (est)', [B['brush'][-1], (-83.03975698, 42.32851075)], 'straight estimate (Claude)', 'link', True))
feats.append(F('cn', 'Grand Trunk Western: Ferrysburg - Muskegon (est)', [(-86.234, 43.066), (-86.2599855, 43.2318052)], 'straight estimate (Claude): the Muskegon line north from Ferrysburg is not in the trace', 'link', True))
feats.append(F('cn', 'Grand Trunk Western: Richmond - the Romeo line (tie)', [(-82.7466527, 42.8088695), (-82.7458352, 42.8100815)], 'tie (Claude): the Romeo line ends 150 m from the Detroit - Port Huron line at Richmond', 'link'))
ch = B['chicago']; J = (-87.6369, 41.809)                                    # where the GTW meets the C&WI (east end of the GTW 49th St. piece)
k = min(range(len(ch)), key=lambda i: math.hypot(ch[i][0] - J[0], ch[i][1] - J[1]))
feats.append(F('cn', 'Grand Trunk Western: Elsdon - C&WI (Brendan export)', ch[:k + 1], "Brendan's Chicago export (OSM), path picked by Claude", 'brendan'))
feats.append(F('cwi', 'Chicago & Western Indiana: GTW junction - Dearborn Station (Brendan export)', ch[k:], "Brendan's Chicago export (OSM), path picked by Claude", 'brendan'))
json.dump(dict(type='FeatureCollection', features=feats), open(os.path.join(HERE, 'traces', 'maritimes', 'gtw.geojson'), 'w'))
print(len(feats), 'pieces')
