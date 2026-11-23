"""The Gull's route (Brendan, 22 Nov 2026: Maine Central Table 2 and B&M Table 8 pages): Boston & Maine Boston - Wilmington - Lawrence - Haverhill - Exeter - Dover - South Berwick -
Portland (the Western Route) and the Maine Central Portland - Danville Jct. - Lewiston - Waterville (the Back Route), Portland - Brunswick - Augusta - Waterville (the Lower Road) and
Waterville - Bangor - Mattawamkeag -> traces/maritimes/mec.geojson (read by mar_tracks). Mattawamkeag - Vanceboro is in cp_maine.geojson (own mec).
Source: Mississippi Rails state maps (Tony Howe and David Price; Brendan; raw files in the private repo, traces/msrails/): Maine, New Hampshire, Massachusetts.
Usage: python3 tools/mar_import_mec.py <msrails folder>"""
import json, math, os, sys, zipfile
import xml.etree.ElementTree as ET
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
K = '{http://www.opengis.net/kml/2.2}'
WANT = {('Massachusetts', 'Wilmington Jct to Boston MA'): 'bm', ('Massachusetts', 'Wilmington MA to MA/NH State Line'): 'bm',
        ('New_Hampshire', 'MA/NH State Line to NH/ME State Line'): 'bm', ('Maine', 'South Berwick ME to Portland ME'): 'bm',
        ('Maine', 'Portland to South Windham ME'): 'mec', ('Maine', 'Portland ME to Augusta ME'): 'mec', ('Maine', 'Augusta ME to Waterville ME'): 'mec',
        ('Maine', 'Royal Jct to Danville Jct'): 'mec', ('Maine', 'Danville Jct to Waterville ME'): 'mec', ('Maine', 'Waterville ME to Bangor ME'): 'mec',
        ('Maine', 'Bangor ME to Mattawamkeag ME'): 'mec'}
feats = []
def F(name, pts, note, own, group='mississippi_rails'):
    return dict(type='Feature', properties=dict(own=own, name=name, constituent={'bm': 'Boston & Maine', 'mec': 'Maine Central'}[own], branch='', group=group, status='ok', cost=1.0,
                note=note), geometry=dict(type='LineString', coordinates=[[round(x, 7), round(y, 7)] for x, y in pts]))
got = set()
for st in ('Massachusetts', 'New_Hampshire', 'Maine'):
    z = zipfile.ZipFile(os.path.join(sys.argv[1], f'{st}_State_Map.kmz'))
    for c in ET.fromstring(z.read([n for n in z.namelist() if n.endswith('.kml')][0])).iter(K + 'Placemark'):
        n = c.find(K + 'name'); nm = (n.text or '').strip() if n is not None else ''
        if (st, nm) not in WANT: continue
        for q in c.iter(K + 'coordinates'):
            pts = [tuple(map(float, x.split(',')[:2])) for x in q.text.split()]
            if len(pts) < 2: continue
            got.add((st, nm)); own = WANT[(st, nm)]
            feats.append(F(f"{'Boston & Maine' if own == 'bm' else 'Maine Central'}: {nm} ({st.replace('_', ' ')} map)", pts,
                           'Mississippi Rails state map (Tony Howe and David Price), supplied by Brendan', own))
assert got == set(WANT), set(WANT) - got
def km(a, b): return math.hypot((a[0] - b[0]) * 111.32 * math.cos(math.radians(a[1])), (a[1] - b[1]) * 110.57)
ok = [(f['properties']['name'], f['properties']['own'], [tuple(q) for q in f['geometry']['coordinates']]) for f in feats]
ties = []
for i, (nm, ow, c) in enumerate(ok):
    for e in (c[0], c[-1]):
        best = min(((km(e, q), q, n2) for j, (n2, o2, c2) in enumerate(ok) if j != i for q in c2), default=None)
        if best and 0.03 < best[0] < 1.0 and not any(km(e, t[0]) < 0.01 or (km(e, t[1]) < 0.01 and km(best[1], t[0]) < 0.01) for t in ties):
            ties.append((e, best[1], nm, best[2], best[0], ow))
for e, q, a, b, d, ow in ties:
    feats.append(F(f'tie, {a.split(": ")[-1]} - {b.split(": ")[-1]}', [e, q], f'tie (Claude): the piece ends {d * 1000:.0f} m from the other piece', ow, group='link'))
print(len(ties), 'ties:', [(t[2].split(': ')[-1][:30], t[3].split(': ')[-1][:30], round(t[4] * 1000)) for t in ties])
# Portland Union Station (Brendan: 43.652243, -70.280710): tie the station to the nearest track
UNION = (-70.280710, 43.652243)
near = min(((km(UNION, q), q, nm, ow) for nm, ow, c in ok for q in c))
print('Union Station is', round(near[0] * 1000), 'm from', near[2])
# Union Station - Woodfords - Deering Jct. (the start of the Maine Central main line, Portland - Augusta): not in the state map; a DASHED estimate (a trace wanted)
f = F('Maine Central: Union Station - Woodfords - Deering Jct., estimate', [(-70.2798, 43.6479), UNION, (-70.2855, 43.6735), (-70.2913587, 43.6876073)],
      'estimate (Claude), drawn broken: the Portland Terminal line from Union Station to the Maine Central main line is not in the Mississippi Rails Maine map', 'mec', group='link')
f['properties']['est'] = True; feats.append(f)
json.dump(dict(type='FeatureCollection', features=feats), open(os.path.join(HERE, 'traces', 'maritimes', 'mec.geojson'), 'w'))
print(len(feats), 'pieces')
