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
            'Concord NH to Wells River VT': 'bm', 'Bradford VT to Wells River VT': 'bm', 'White River Jct VT to Bradford VT': 'bm', 'Concord NH to White River Jct': 'bm'},
        1: {'Concord NH to Wells River VT': 'bm', 'Concord NH to White River Jct': 'bm', 'Concord NH to Nashua NH': 'bm', 'Lowell MA to Nashua NH': 'bm'},
        2: {'Boston to Lowell MA': 'bm', 'Lowell MA to Nashua NH': 'bm', 'Boston & Lowell new route into Boston': 'bm'}}
STATE = ['VT', 'NH', 'MA']
feats, seen = [], set()
for k, fn in enumerate(sys.argv[1:4]):
    for nm, pts in placemarks(fn):
        if nm not in WANT[k] or len(pts) < 2: continue
        key = (nm, tuple(pts[0]), tuple(pts[-1]))
        if key in seen: continue                                        # the New Hampshire map files Concord - Wells River in two folders
        seen.add(key); own = WANT[k][nm]
        feats.append(dict(type='Feature', properties=dict(own=own, name=f'{"Canadian Pacific" if own == "cp" else "Boston & Maine"}: {nm} ({STATE[k]} map)',
                      constituent='Canadian Pacific (ex Connecticut & Passumpsic Rivers)' if own == 'cp' and 'North Troy' not in nm else ('Canadian Pacific' if own == 'cp' else 'Boston & Maine'),
                      branch='New England', group='mississippi_rails', status='ok', cost=1.0, note='Mississippi Rails (Tony Howe and David Price) state map, KMZ supplied by Brendan, 17 Nov 2026'),
                      geometry=dict(type='LineString', coordinates=pts)))
NS = [-71.0618139, 42.3658083]                                  # Boston North Station (Brendan, 17 Nov 2026: 42 21 56.91 N, 71 3 42.53 W; "tracks should extend straight to this point")
end = [f for f in feats if 'new route into Boston' in f['properties']['name']][0]['geometry']['coordinates'][-1]
feats.append(dict(type='Feature', properties=dict(own='bm', name='Boston & Maine: track end - North Station (straight, Brendan)', constituent='Boston & Maine', branch='New England',
              group='brendan', status='ok', cost=1.0, note="Brendan, 17 Nov 2026: straight from the trace end to his North Station point"), geometry=dict(type='LineString', coordinates=[end, NS])))
json.dump(dict(type='FeatureCollection', features=feats), open(os.path.join(HERE, 'traces', 'maritimes', 'newengland.geojson'), 'w'))
print(len(feats), 'pieces')
