"""CN's Grand Trunk in the United States (KMZ trace "Grand Trunk Ry" by Mississippi Rails (Tony Howe and David Price), supplied by Brendan, 17 Nov 2026): Norton (the Quebec boundary) - Island Pond - Berlin - Gorham -
Bethel - South Paris - Danville Jct. - Portland (Grand Trunk station), with the Lewiston branch (Lewiston Jct. - Auburn - Lewiston) and the Norway branch.
The three border stubs in the same file (Rouses Point, N.Y.; Massena - Fort Covington, N.Y.; Alburgh Jct., Vt.) are kept with status 'later' (not used until
their trains are built). Usage: python3 tools/mar_import_gtr.py <Grand_Trunk_Ry.kmz>  -> traces/maritimes/cn_gtr.geojson (own cn).
The raw KMZ is in the private repo (traces/gtr/). Placemarks named "... abandoned" are abandoned today, in use in 1948 (the Portland station lead, Lewiston)."""
import json, os, re, sys, zipfile
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
s = zipfile.ZipFile(sys.argv[1]).read('doc.kml').decode('utf-8')
LATER = ("Rouse's Point",)          # Fort Covington (CN 79 / 80) and Alburgh (the Central Vermont) in use since 17 Nov 2026
feats = []
for nm, c in re.findall(r'<Placemark>.*?<name>(.*?)</name>.*?<coordinates>(.*?)</coordinates>', s, re.S):
    nm = nm.replace('&apos;', "'"); pts = []
    for x in c.split():
        lo, la = map(float, x.split(',')[:2]); p = [round(lo, 7), round(la, 7)]
        if not pts or p != pts[-1]: pts.append(p)
    later = any(k in nm for k in LATER)
    feats.append(dict(type='Feature', properties=dict(own='cn', name='Grand Trunk (CN): ' + nm, constituent='Grand Trunk Railway', branch='Grand Trunk (U.S.)', group='mississippi_rails',
                      status='later' if later else 'ok', cost=1.0, note="Mississippi Rails (Tony Howe and David Price) trace, KMZ supplied by Brendan, 17 Nov 2026",
                      why='border stub: for the trains through Rouses Point / Fort Covington / Alburgh, not built yet' if later else ''),
                      geometry=dict(type='LineString', coordinates=pts)))
json.dump(dict(type='FeatureCollection', features=feats), open(os.path.join(HERE, 'traces', 'maritimes', 'cn_gtr.geojson'), 'w'))
print(len(feats), 'pieces;', sum(f['properties']['status'] == 'ok' for f in feats), 'ok')
