"""Great Northern east of Spokane and the Burlington Chicago - St. Paul (Brendan, 26 - 27 Nov 2026) -> traces/gnmw/gn_mw.geojson (read by gn_lines.py).
Sources (private repo): traces/msrails/Great_Northern.kmz (Mississippi Rails 2024-6-16, Tony Howe and David Price) and traces/msrails/Chicago_CBQ_Line.kmz.
Kept: GN pieces east of Spokane (lon > -117.45; the Pacific Jct. - Everett piece cut there), south of the border, not Oregon or California; left out: the "Abandoned" and
"Structures" folders and pieces named abandoned / old alignment / old route / later (Glasgow Air Force Base 1958, Intalco, the pellet plant). Each piece keeps its
name: "A ST to B ST" names give anchor points for the stations at its ends (gn_lines.ANCHORS).
Usage: python3 tools/gn_import.py <Great_Northern.kmz> <Chicago_CBQ_Line.kmz>"""
import json, os, re, sys, zipfile
import xml.etree.ElementTree as ET
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
K = '{http://www.opengis.net/kml/2.2}'
SKIP = re.compile(r'abandon|old alignment|old route|Old Cascade|Air Force|Intalco|Pellet|Creston|very approximate|Delta Yard|Old route', re.I)
def load(fn):
    z = zipfile.ZipFile(fn); return ET.fromstring(z.read([n for n in z.namelist() if n.endswith('.kml')][0]))
feats = []
def add(own, name, desc, pts, src):
    feats.append(dict(type='Feature', properties=dict(own=own, name=name, note=desc[:160], src=src, cost=1.0),
                      geometry=dict(type='LineString', coordinates=[[round(x, 7), round(y, 7)] for x, y in pts])))
def walk(e, path, own, src):
    for c in e:
        if c.tag in (K + 'Folder', K + 'Document'): walk(c, path + [c.findtext(K + 'name') or ''], own, src)
        elif c.tag == K + 'Placemark':
            p = '/'.join(path); nm = (c.findtext(K + 'name') or '').strip(); d = (c.findtext(K + 'description') or '').strip().replace('\n', '; ')
            if re.search(r'Abandoned|Structures', p) or SKIP.search(nm): continue          # the name only: a note like "abandoned 1987" is after 1948
            for ls in c.iter(K + 'LineString'):
                pts = [tuple(map(float, x.split(',')[:2])) for x in ls.findtext(K + 'coordinates').split()]
                if own == 'gn':                                            # east of Spokane, US side, north of Oregon: runs of points kept
                    keep = lambda q: q[0] > -117.45 and q[1] < 49.0005 and not (q[0] < -116.0 and q[1] < 46.0)
                    runs, cur = [], []
                    for q in pts:
                        if keep(q): cur.append(q)
                        elif cur: runs.append(cur); cur = []
                    if cur: runs.append(cur)
                    for r in runs:
                        if len(r) > 1: add(own, nm, d, r, src)
                elif len(pts) > 1: add(own, nm, d, pts, src)
walk(load(sys.argv[1]), [], 'gn', 'Mississippi Rails, Great_Northern.kmz (2024-6-16)')
walk(load(sys.argv[2]), [], 'cbq', 'Mississippi Rails, Chicago_CBQ_Line.kmz')
out = os.path.join(HERE, 'traces', 'gnmw', 'gn_mw.geojson')
json.dump(dict(type='FeatureCollection', features=feats), open(out, 'w'))
print(len(feats), 'pieces ->', out)
