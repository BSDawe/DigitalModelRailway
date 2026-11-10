"""CP's line across Maine (Brendan, 10 Nov 2026, two KMZ traces): the International Railway of Maine (CP), the Quebec boundary at Boundary / Lowelltown -
Jackman - Greenville - Brownville Jct. - Mattawamkeag, and the Maine Central from Mattawamkeag to Vanceboro, over which the CP ran (trackage rights).
Usage: python3 tools/mar_import_cp_maine.py <IRM.kmz> <MEC.kmz>  -> traces/maritimes/cp_maine.geojson (the IRM own cp; the Maine Central piece own mec, drawn in
the Maine Central / Boston & Maine gold (Brendan, 10 Nov 2026: B&M / MEC livery maroon and gold; the two may share a style). When the U.S. railways get their own
folders it may move to a Maine Central file)."""
import json, os, re, sys, zipfile
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def kml_line(fn):
    s = zipfile.ZipFile(fn).read('doc.kml').decode('utf-8')
    c = re.search(r'<coordinates>(.*?)</coordinates>', s, re.S).group(1).split()
    out = []
    for x in c:
        lo, la = map(float, x.split(',')[:2]); p = [round(lo, 7), round(la, 7)]
        if not out or p != out[-1]: out.append(p)
    return out
irm, mec = kml_line(sys.argv[1]), kml_line(sys.argv[2])
P = dict(group='brendan', status='ok', cost=1.0, branch='Maine')
feats = [dict(type='Feature', properties=dict(P, own='cp', name='International Railway of Maine (CP): Quebec boundary - Jackman - Greenville - Brownville Jct. - Mattawamkeag',
                                              constituent='International Railway of Maine', note="Brendan's trace (KMZ), 10 Nov 2026"), geometry=dict(type='LineString', coordinates=irm)),
         dict(type='Feature', properties=dict(P, own='mec', name='Maine Central: Mattawamkeag - Vanceboro (CP trackage rights)', constituent='Maine Central Railroad',
                                              note="Brendan's trace (KMZ), 10 Nov 2026; Maine Central track (own mec)"), geometry=dict(type='LineString', coordinates=mec))]
json.dump(dict(type='FeatureCollection', features=feats), open(os.path.join(HERE, 'traces', 'maritimes', 'cp_maine.geojson'), 'w'))
from pyproj import Geod; G = Geod(ellps='WGS84')
for f in feats: c = f['geometry']['coordinates']; print(f['properties']['name'][:50], round(sum(G.inv(*a, *b)[2] for a, b in zip(c, c[1:])) / 1609.34, 1), 'mi')
