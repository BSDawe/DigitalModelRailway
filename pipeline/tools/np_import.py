"""Northern Pacific east of Spokane, with the Camas Prairie in Idaho (Brendan, 27 Nov 2026) -> traces/npmw/np_mw.geojson (read by np_lines.py).
Source (private repo): traces/msrails/Northern_Pacific_Ry.kmz (Mississippi Rails 2024-6-20, Tony Howe and David Price).
Kept: pieces east of Spokane (lon > -117.45), not Oregon; left out: the "Abandoned" and "Structures" folders and pieces whose NAME says abandoned / old alignment / old route
(a description like "abandoned 1987" is after 1948 and kept). The Camas Prairie's own pieces (Clearwater Short Line: Arrow - Stites, Joseph - Culdesac - Craigmont - Grangeville)
are own 'up', as the Camas Prairie is drawn in Washington (wa_lines.py: NP / UP joint, drawn with the UP). Each piece keeps its name ("A ST to B ST": anchors, np_lines.ANCHORS).
Usage: python3 tools/np_import.py <Northern_Pacific_Ry.kmz>"""
import json, os, re, sys, zipfile
import xml.etree.ElementTree as ET
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
K = '{http://www.opengis.net/kml/2.2}'
SKIP = re.compile(r'abandon|old alignment|old route|original route|Big Sky|Colstrip|graded only|Cow Creek|Lincoln ND to Flasher', re.I)   # Lincoln - Flasher: not the 1948 route (the Mott trains run by Cannon Ball, Table 26)
KEEP = {'Breckenridge MN abandoned', 'Stites ID abandoned'}          # abandoned after 1948: the Breckenridge connection across the Red River; Kooskia - Stites
CPRR = re.compile(r'Clearwater Short Line|Camas Prairie')
z = zipfile.ZipFile(sys.argv[1]); root = ET.fromstring(z.read([n for n in z.namelist() if n.endswith('.kml')][0]))
feats = []
def walk(e, path):
    for c in e:
        if c.tag in (K + 'Folder', K + 'Document'): walk(c, path + [c.findtext(K + 'name') or ''])
        elif c.tag == K + 'Placemark':
            p = '/'.join(path); nm = (c.findtext(K + 'name') or '').strip(); d = (c.findtext(K + 'description') or '').strip().replace('\n', '; ')
            if re.search(r'Abandoned|Structures|/OR$', p) or (SKIP.search(nm) and nm not in KEEP): continue
            own = 'up' if CPRR.search(d) else 'np'
            for ls in c.iter(K + 'LineString'):
                pts = [tuple(map(float, x.split(',')[:2])) for x in ls.findtext(K + 'coordinates').split()]
                runs, cur = [], []
                for q in pts:
                    if q[0] > -117.45 and q[1] < 49.0005: cur.append(q)
                    elif cur: runs.append(cur); cur = []
                if cur: runs.append(cur)
                for r in runs:
                    if len(r) > 1:
                        feats.append(dict(type='Feature', properties=dict(own=own, name=nm, note=d[:160], src='Mississippi Rails, Northern_Pacific_Ry.kmz (2024-6-20)'),
                                          geometry=dict(type='LineString', coordinates=[[round(x, 7), round(y, 7)] for x, y in r])))
walk(root, [])
out = os.path.join(HERE, 'traces', 'npmw', 'np_mw.geojson')
json.dump(dict(type='FeatureCollection', features=feats), open(out, 'w'))
print(len(feats), 'pieces ->', out, sum(1 for f in feats if f['properties']['own'] == 'up'), 'Camas Prairie')
