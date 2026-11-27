"""The South Shore Line's 1948 route -> traces/chicago/cssb_route.json (public; the raw KMZ stays in the private repo).
Usage: python3 tools/cssb_extract.py <Chicago_South_Shore__South_Bend.kmz>
Sources: the KMZ Brendan sent (26 Nov 2026; "mapped by Doug Spurling"): the CSS&SB main line, with the 1948 alignments from its "former" folder: the East Chicago street line
(abandoned 1956, replaced by the East Chicago bypass of 1954 - 1956, which is left out) and the line into downtown South Bend (abandoned 1970). Chicago: the Illinois Central
(Brendan: the South Shore trains run over the IC like the Michigan Central's, but on past Central Station to the IC's downtown commuter terminals, Van Buren Street and
Randolph Street): the IC trace already in traces/maritimes/mc.geojson ("Centralia to Chicago"), Kensington to its north end at Randolph Street.
Each point is [lon, lat, 1 if on IC track]."""
import json, math, os, sys, zipfile
import xml.etree.ElementTree as ET
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
K = '{http://www.opengis.net/kml/2.2}'
def m(a, b): return math.hypot((a[0] - b[0]) * 111320 * math.cos(math.radians(41.7)), (a[1] - b[1]) * 110570)
z = zipfile.ZipFile(sys.argv[1]); root = ET.fromstring(z.read([n for n in z.namelist() if n.endswith('.kml')][0]))
pieces = []
def walk(e, path):
    for c in e:
        if c.tag in (K + 'Folder', K + 'Document'): walk(c, path + [c.findtext(K + 'name') or ''])
        elif c.tag == K + 'Placemark':
            p = '/'.join(path); d = (c.findtext(K + 'description') or '')
            main = p.endswith('tracks - road, main') and 'Chicago South Shore' in (c.findtext(K + 'name') or '') and 'second main' not in d and 'Bypass' not in d and 'Kingsbury' not in d
            former = 'former' in p and 'second main' not in d and 'quarry' not in d and 'Chicago South Shore' in (c.findtext(K + 'name') or '')
            if main or former:
                for ls in c.iter(K + 'LineString'):
                    pieces.append([[float(v) for v in x.split(',')[:2]] for x in ls.findtext(K + 'coordinates').split()])
walk(root, [])
# chain from Kensington eastward: each time take the piece with an end nearest the current end
KENS = (-87.6122, 41.6842)
start = min(pieces, key=lambda c: min(m(c[0], KENS), m(c[-1], KENS)))
pieces.remove(start); css = start if m(start[0], KENS) < m(start[-1], KENS) else start[::-1]
while pieces:
    end = css[-1]
    best = min(pieces, key=lambda c: min(m(c[0], end), m(c[-1], end)))
    d = min(m(best[0], end), m(best[-1], end))
    if d > 400: break                                             # East Chicago: the street line leaves about 250 m from the old main's end
    pieces.remove(best); css += (best if m(best[0], end) <= m(best[-1], end) else best[::-1])[1:]
print(f'CSS&SB: {sum(m(a, b) for a, b in zip(css, css[1:])) / 1609.34:.2f} mi, ends {css[-1]}; pieces left out: {len(pieces)}')
ic = next(f for f in json.load(open(os.path.join(HERE, 'traces', 'maritimes', 'mc.geojson')))['features'] if f['properties']['name'] == 'Illinois Central: Centralia to Chicago')['geometry']['coordinates']
def foot(a, b, q):
    dx, dy = b[0] - a[0], b[1] - a[1]; t = max(0, min(1, ((q[0] - a[0]) * dx + (q[1] - a[1]) * dy) / ((dx * dx + dy * dy) or 1e-18)))
    return [a[0] + t * dx, a[1] + t * dy]
if ic[0][1] > ic[-1][1]: ic = ic[::-1]                                # south to north
k = min(range(len(ic) - 1), key=lambda i: m(foot(ic[i], ic[i + 1], css[0]), css[0]))
icn = [foot(ic[k], ic[k + 1], css[0])] + ic[k + 1:]                   # Kensington (the foot of the CSS&SB end on the IC) -> Randolph Street
print(f'IC: {sum(m(a, b) for a, b in zip(icn, icn[1:])) / 1609.34:.2f} mi, joined {m(icn[0], css[0]):.0f} m from the CSS&SB end')
route = [[round(p[0], 7), round(p[1], 7), 1] for p in icn[::-1]] + [[round(p[0], 7), round(p[1], 7), 0] for p in css]
json.dump(dict(source='CSS&SB: KMZ mapped by Doug Spurling (Brendan, 26 Nov 2026), main line with the 1948 East Chicago and South Bend alignments; IC: Mississippi Rails (mc.geojson)',
               route=route), open(os.path.join(HERE, 'traces', 'chicago', 'cssb_route.json'), 'w'))
print(f'route: {sum(m(a, b) for a, b in zip(route, route[1:])) / 1609.34:.2f} mi, {len(route)} points')
