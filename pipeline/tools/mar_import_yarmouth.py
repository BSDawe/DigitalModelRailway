"""Yarmouth, N.S. (Brendan, 10 Nov 2026): the joint CN / Dominion Atlantic station and the Evangeline Wharf spur, from Brendan's small OSM export
(export__5_.geojson, abandoned railway ways round Yarmouth). Usage: python3 tools/mar_import_yarmouth.py <export.geojson>
-> traces/maritimes/yarmouth.geojson:
  - DAR (own cp): the Western Counties trace end south past the wharf to the station throat (way 98558732);
  - CN (own cn): the Halifax & Yarmouth trace end (junction south of town) north to that throat (ways 585963208, 585963207, 98558748, 98560137);
  - the Evangeline Wharf spur (own cp): no spur track in the export (a 19 m fragment of 'rail' only), a straight tie of 71 m from the main line
    to Brendan's pier point (trivially short: drawn solid). Left out: the station stub (98559361; the station point is put on the main line), the parallel siding 98558408, the Main
    Street street track, the line west (98581432) and the ways north of the DAR trace end (the DAR trace has them).
Brendan's points: CN and DAR Yarmouth station 43.82791431716285, -66.12238727842956; Evangeline Pier 43.83735336117989, -66.1222985749302 (approximate)."""
import json, os, sys
from shapely.geometry import LineString, Point
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W = {f['properties']['@id'][4:]: f['geometry']['coordinates'] for f in json.load(open(sys.argv[1]))['features']}
def chain(ids):
    out = []
    for i in ids:
        rev = i.startswith('-'); c = W[i.lstrip('-')][::-1] if rev else W[i.lstrip('-')]
        out += c if not out else c[1:] if c[0] == out[-1] else c
    return out
cn = chain(['-585963208', '-585963207', '98558748', '98560137'])           # junction (-66.12354, 43.82026) north to the throat (-66.12306, 43.82688)
dar = chain(['98558732'])                                                   # throat north to the DAR trace end (-66.11884, 43.84375)
PIER = (-66.1222985749302, 43.83735336117989)
L = LineString(dar); q = L.interpolate(L.project(Point(PIER)))
# put the spur's junction into the DAR piece as a vertex
acc = 0.0; ins = None
for i in range(len(dar) - 1):
    seg = LineString(dar[i:i + 2])
    if acc + seg.length >= L.project(Point(PIER)): ins = i + 1; break
    acc += seg.length
J = [round(q.x, 7), round(q.y, 7)]; dar = dar[:ins] + [J] + dar[ins:]
P = dict(constituent='', branch='Yarmouth', group='osm', status='ok', cost=1.0)
feats = [dict(type='Feature', properties=dict(P, own='cp', name='Dominion Atlantic: Yarmouth, Western Counties trace end - station', constituent='Western Counties Railway',
                                              note='OpenStreetMap way 98558732 (abandoned), export by Brendan, 10 Nov 2026'), geometry=dict(type='LineString', coordinates=dar)),
         dict(type='Feature', properties=dict(P, own='cn', name='Halifax & Yarmouth: Yarmouth, track end - station', constituent='Halifax and South Western Railway',
                                              note='OpenStreetMap ways 585963208, 585963207, 98558748, 98560137 (abandoned), export by Brendan, 10 Nov 2026'), geometry=dict(type='LineString', coordinates=cn)),
         dict(type='Feature', properties=dict(P, own='cp', name='Yarmouth: Evangeline Wharf spur (straight tie to the pier, 71 m)', constituent='',
                                              note="Straight tie (no spur in the export); Brendan's Evangeline Pier point, 10 Nov 2026 (approximate)"), geometry=dict(type='LineString', coordinates=[J, list(PIER)]))]
json.dump(dict(type='FeatureCollection', features=feats), open(os.path.join(HERE, 'traces', 'maritimes', 'yarmouth.geojson'), 'w'), indent=0)
from pyproj import Geod; G = Geod(ellps='WGS84')
for f in feats: c = f['geometry']['coordinates']; print(f['properties']['name'], round(sum(G.inv(*a, *b)[2] for a, b in zip(c, c[1:]))), 'm')
