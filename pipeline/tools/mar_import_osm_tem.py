"""Temiscouata Railway in New Brunswick from Brendan's OpenStreetMap export of the abandoned railways around Edmundston (overpass-turbo, 9 Nov 2026 UTC;
(c) OpenStreetMap contributors, ODbL) -> traces/maritimes/tem_osm.geojson, own 'tem'. One-shot, kept as the record.
    python3 tools/mar_import_osm_tem.py /path/to/export.geojson
Brendan (8 Nov 2026): in 1948 the Temiscouata ran over the CN (NTR) by trackage rights between Edmundston and Baker Brook, its own track west of there to
Connors. So: the station's west-facing leg down to the NTR; the Connors branch from the NTR at Couturier Siding (a CGN railway point, 4 m from the NTR) by
Baker Brook, Caron Brook, Clair, Ledges and Little River Mills to Connors, one piece; the two short tails past Connors; and the original riverside line
Edmundston - Baker Brook as 'pre1948' (abandoned 1941 in the U of T historical rails file). Checked against the Official Guide (April 25, 1948) miles from
Edmundston (81.5): Caron Brook 98.6 / 98.8, Clairs 101.3 / 101.7, Connors 112.6 / 113.1 (CGN points on the track)."""
import json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, '..', 'traces', 'maritimes', 'tem_osm.geojson')
OSM = {f['properties']['@id'].split('/')[1]: f for f in json.load(open(sys.argv[1]))['features']}
def chain(ids):
    pts = []; n0 = -1
    for i in ids:
        c = [tuple(p) for p in OSM[i]['geometry']['coordinates']]
        if pts:
            if len(pts) == n0 and min(math.dist(pts[0], c[0]), math.dist(pts[0], c[-1])) < min(math.dist(pts[-1], c[0]), math.dist(pts[-1], c[-1])): pts = pts[::-1]   # turn the first way to face the second
            if math.dist(c[-1], pts[-1]) < math.dist(c[0], pts[-1]): c = c[::-1]
            assert math.dist(c[0], pts[-1]) < 0.0005, i
            c = c[1:] if math.dist(c[0], pts[-1]) < 1e-7 else c
        pts += c
        if len(pts) == len(c): n0 = len(pts)
    return pts
def orient(ids, first):   # start the chain at the given end of its first way
    c = chain(ids); return c if math.dist(c[0], first) < math.dist(c[-1], first) else c[::-1]
NOTE = 'OpenStreetMap (c) OpenStreetMap contributors, ODbL; export supplied by Brendan, 8 Nov 2026 (ways: {})'
PIECES = [('Temiscouata Railway: Edmundston station - NTR (west leg)', ['847846930', '847846929', '847846928', '409427033'], (-68.3231, 47.3675), 'ok', None),
          ('Temiscouata Railway: Connors branch (Couturier Siding - Baker Brook - Clair - Connors)',
           ['136572900', '847846923', '136545145', '847846922', '917643611', '917643612', '764299884', '1032358071', '764299886', '1032358073', '1032358070', '764299885',
            '764299882', '136545150', '764412579', '764412573', '764412575', '764412574', '764412576', '119324207', '119324407', '119324115'], (-68.4947, 47.3039), 'ok', None),
          ('Temiscouata Railway: Connors, track beyond the station (1)', ['119324372'], (-68.8228, 47.2117), 'ok', None),
          ('Temiscouata Railway: Connors, track beyond the station (2)', ['119324384'], (-68.8228, 47.2117), 'ok', None),
          ('Temiscouata Railway: riverside line Edmundston - Baker Brook', ['847846924'], (-68.3279, 47.3614), 'pre1948',
           'abandoned 1941 (U of T historical rails); in 1948 the trains ran over the CN (NTR) by trackage rights (Brendan)')]
fs = []
for name, ids, first, status, why in PIECES:
    p = dict(own='tem', name=name, constituent='Temiscouata Railway', branch=name.split(': ', 1)[1], note=NOTE.format(', '.join(ids)), cost=1.0, fid=None, group='osm', status=status)
    if why: p['why'] = why
    fs.append(dict(type='Feature', properties=p, geometry=dict(type='LineString', coordinates=[[round(x, 7), round(y, 7)] for x, y in orient(ids, first)])))
json.dump(dict(type='FeatureCollection', features=fs), open(OUT, 'w'), separators=(',', ':'))
print(OUT, len(fs))
