"""Montreal - Boston track in New England (17 Nov 2026), from the Mississippi Rails state maps (Tony Howe and David Price; KMZ files supplied by Brendan,
raw files in the private repo, traces/msrails/). Writes traces/maritimes/newengland.geojson:
- CP (own cp): North Troy - Newport, and Newport - Barton - St. Johnsbury - Wells River (the old Connecticut & Passumpsic Rivers line, filed under the
  Boston & Maine in the maps; CP's in 1948 by CP Table 8, "Riys." column: C.P. from Newport to Wells River and Woodsville).
- Boston & Maine (own bm): Wells River - Woodsville; Woodsville - Plymouth - Concord; Wells River - Bradford - White River Jct. - Concord; Concord - Manchester -
  Nashua; Nashua - Lowell; Lowell - Boston, with the "new route" into North Station.
Usage: python3 tools/mar_import_newengland.py <Vermont.kmz> <New_Hampshire.kmz> <Massachusetts.kmz>"""
import json, os, re, sys, zipfile
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def placemarks(fn):
    z = zipfile.ZipFile(fn); s = z.read([n for n in z.namelist() if n.endswith('.kml')][0]).decode('utf-8', 'replace').replace('&amp;', '&').replace('&apos;', "'")
    for pm in re.findall(r'<Placemark>.*?</Placemark>', s, re.S):
        n = re.search(r'<name>(.*?)</name>', pm, re.S); c = re.findall(r'<coordinates>(.*?)</coordinates>', pm, re.S)
        pts = []
        for x in ' '.join(c).split():
            lo, la = map(float, x.split(',')[:2]); p = [round(lo, 7), round(la, 7)]
            if not pts or p != pts[-1]: pts.append(p)
        yield (n.group(1).strip() if n else ''), pts
WANT = {0: {'North Troy VT to Newport VT': 'cp', 'Barton VT to Newport VT': 'cp', 'St Johnsbury VT to Barton VT': 'cp', 'Wells River VT to St Johnsbury VT': 'cp',
            'Concord NH to Wells River VT': 'bm', 'Bradford VT to Wells River VT': 'bm', 'White River Jct VT to Bradford VT': 'bm', 'Concord NH to White River Jct': 'bm',
            'Newport VT to VT Canada Line': 'cp',                                                     # Newport - Derby Line: the Quebec Central's (Q.C. in CP Table 8)
            'Fonda Jct to NY State Line': 'cn', 'St Albans VT to Fonda Jct': 'cn', 'Fonda Jct to Canada Border': 'cn', 'Essex Jct to St Albans VT': 'cn',
            'Northfield VT to Essex Jct': 'cn', 'White River Jct to Northfield VT': 'cn', 'White River Jct to Windsor VT': 'cn', "Miller's Falls MA to Brattleboro VT": 'cn',   # Central Vermont (CN subsidiary, drawn as CN; Brendan, 17 Nov 2026)
            'Bellows Falls VT to Windsor VT': 'bm', 'Brattleboro VT to Bellows Falls VT': 'bm'},
        1: {'Concord NH to Wells River VT': 'bm', 'Concord NH to White River Jct': 'bm', 'Concord NH to Nashua NH': 'bm', 'Lowell MA to Nashua NH': 'bm'},
        2: {'Boston to Lowell MA': 'bm', 'Lowell MA to Nashua NH': 'bm', 'Boston & Lowell new route into Boston': 'bm',
            'Cabotville (Chicopee Jct) to MA/VT State Line': 'bm', 'Springfield MA to Cabotville (Chicopee Jct)': 'bm'}}         # the Connecticut River line (B&M), South Vernon - Springfield
STATE = ['VT', 'NH', 'MA']
feats, seen = [], set()
for k, fn in enumerate(sys.argv[1:4]):
    for nm, pts in placemarks(fn):
        if nm not in WANT[k] or len(pts) < 2: continue
        key = (nm, tuple(pts[0]), tuple(pts[-1]))
        if key in seen or (k == 0 and nm in ('Bellows Falls VT to Windsor VT', 'Brattleboro VT to Bellows Falls VT') and any(f['properties']['name'].endswith(nm + ' (VT map)') for f in feats)): continue                                        # the New Hampshire map files Concord - Wells River in two folders
        seen.add(key); own = WANT[k][nm]
        feats.append(dict(type='Feature', properties=dict(own=own, name=f'{dict(cp="Canadian Pacific", bm="Boston & Maine", cn="Central Vermont (CN)")[own]}: {nm} ({STATE[k]} map)',
                      constituent='Central Vermont Railway' if own == 'cn' else 'Quebec Central (Massawippi Valley)' if 'Canada Line' in nm else 'Canadian Pacific (ex Connecticut & Passumpsic Rivers)' if own == 'cp' and 'North Troy' not in nm else ('Canadian Pacific' if own == 'cp' else 'Boston & Maine'),
                      branch='New England', group='mississippi_rails', status='ok', cost=1.0, note='Mississippi Rails (Tony Howe and David Price) state map, KMZ supplied by Brendan, 17 Nov 2026'),
                      geometry=dict(type='LineString', coordinates=pts)))
# Springfield Union Station (Brendan, 18 Nov 2026: 42.106238, -72.593270) is on the New York Central (Boston & Albany) main line: every train calls there, so trains from the
# Connecticut River line (B&M, and the Central Vermont's) back in or out. A slice of the B&A main line within 4 km of the station (own nyc), until the B&A is built.
import math
SU = (-72.59327009959836, 42.106238230164)
def _m(p, q): return math.hypot((p[0] - q[0]) * 111320 * math.cos(math.radians(42.1)), (p[1] - q[1]) * 110540)
for nm, pts in placemarks(sys.argv[3]):
    if nm == 'Worcester MA to NY/MA State Line':
        sl = [p for p in pts if _m(p, SU) < 4000]
        feats.append(dict(type='Feature', properties=dict(own='nyc', name='New York Central (Boston & Albany): main line through Springfield (MA map, slice)', constituent='Boston & Albany (NYC)',
                      branch='New England', group='mississippi_rails', status='ok', cost=1.0, note='Mississippi Rails (Tony Howe and David Price) state map; slice within 4 km of Springfield Union Station'),
                      geometry=dict(type='LineString', coordinates=sl)))
NS = [-71.0618139, 42.3658083]                                  # Boston North Station (Brendan, 17 Nov 2026: 42 21 56.91 N, 71 3 42.53 W; "tracks should extend straight to this point")
end = [f for f in feats if 'new route into Boston' in f['properties']['name']][0]['geometry']['coordinates'][-1]
feats.append(dict(type='Feature', properties=dict(own='bm', name='Boston & Maine: track end - North Station (straight, Brendan)', constituent='Boston & Maine', branch='New England',
              group='brendan', status='ok', cost=1.0, note="Brendan, 17 Nov 2026: straight from the trace end to his North Station point"), geometry=dict(type='LineString', coordinates=[end, NS])))
json.dump(dict(type='FeatureCollection', features=feats), open(os.path.join(HERE, 'traces', 'maritimes', 'newengland.geojson'), 'w'))
print(len(feats), 'pieces')
