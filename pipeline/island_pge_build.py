"""Esquimalt & Nanaimo (Table 164) and Pacific Great Eastern (April 1948 Official Guide) trains. Run after mainline_build.py.
Adds lines en (Victoria-Courtenay), ena (Parksville-Port Alberni) and pge (Squamish-Quesnel) to viz_data.json and the GTFS feed.
Track comes from island_pge_geometry.py (NRWN). E&N stations sit at their printed mileage along the traced track (139.6 mi
traced vs 139.7 printed); PGE stations at printed mileage, pinned to NRWN station points at Squamish, Shalalth, Lillooet and Williams Lake."""
import csv, json, math, os, pickle, re, zipfile
from shapely.geometry import Point
from nrwn_graph import fwd, inv, MI
HERE = os.path.dirname(os.path.abspath(__file__)); GT = os.path.join(HERE, 'gtfs')
R = pickle.load(open(os.path.join(HERE, 'island_pge_routes.pkl'), 'rb'))

def times(txt):
    arr = dep = None
    for m in re.finditer(r'(ar|lv)?\s*f?(\d+)\.(\d+)([ap])', txt):
        h, mn = int(m.group(2)), int(m.group(3))
        if m.group(4) == 'p' and h != 12: h += 12
        if m.group(4) == 'a' and h == 12: h = 0
        t = h * 3600 + mn * 60
        if m.group(1) == 'ar': arr = t
        elif m.group(1) == 'lv': dep = t
        else: arr = dep = t
    return (arr if arr is not None else dep), (dep if dep is not None else arr)

def monotonic(stops):
    base, prev = 0, -1
    for s in stops:
        for k in (1, 2):
            if s[k] + base < prev - 6 * 3600: base += 86400
            s[k] += base; prev = s[k]
    return stops

lines = {}
def line(key, kind, label, owner, route, dir_labels):
    lines[key] = dict(key=key, kind=kind, label=label, owner=owner, route=route, dirLabels=dir_labels, stations=[], trips=[], _idx={})
    return lines[key]
def station(L, name, chain, mile, gid, principal, note):
    L['_idx'][name] = len(L['stations'])
    L['stations'].append(dict(name=name, chain=chain, mile=mile, gid=gid, principal=principal, note=note))

# ================= E&N
EN_PRINCIPAL = {'Victoria', 'Shawnigan', 'Duncan', 'Chemainus', 'Ladysmith', 'Nanaimo', 'Parksville', 'Qualicum Beach',
                'Union Bay', 'Courtenay', 'Alberni', 'Port Alberni', 'Cameron Lake'}
en = line('en', 'i', 'Esquimalt & Nanaimo', 'cp', R['EN'], ['to Nanaimo and Courtenay', 'to Victoria'])
ena = line('ena', 'i', 'Esquimalt & Nanaimo', 'cp', R['PA'], ['to Port Alberni', 'to Parksville'])
rows = [r for r in csv.reader(l for l in open(os.path.join(HERE, 'en_1949_table164.csv')) if not l.startswith('#'))]
for ln, name, mile, *_ in rows:
    L, total = (en, 139.7) if ln == 'main' else (ena, 38.8)
    gid = 'EN_' + re.sub(r'\W+', '_', name.upper()).strip('_')
    ch = R['EN'].project(Point(R['PA'].coords[0])) if (ln, name) == ('main', 'Parksville') else float(mile) / total * L['route'].length
    station(L, name, ch, float(mile), gid, name in EN_PRINCIPAL,
            'Esquimalt & Nanaimo station' + (' (junction for Port Alberni)' if name == 'Parksville' else ''))
for col, num, ln, d in ((3, '1', 'main', 0), (4, '2', 'main', 1), (5, '3', 'alberni', 0), (6, '4', 'alberni', 1)):
    L = en if ln == 'main' else ena
    rs = [r for r in rows if r[0] == ln and r[col]]
    rs.sort(key=lambda r: float(r[2]), reverse=(d == 1))
    stops = [[L['_idx'][r[1]], *times(r[col]), 1] for r in rs]
    note = {'1': 'Victoria to Courtenay; connects at Parksville for Port Alberni.', '2': 'Courtenay to Victoria; connects at Parksville from Port Alberni.',
            '3': 'Port Alberni branch, connecting with No. 1 at Parksville.', '4': 'Port Alberni branch, connecting with No. 2 at Parksville.'}[num]
    L['trips'].append(dict(id='EN-' + num, num=num, name='', svc='EN_XSUN', dir=d, stops=monotonic(stops), note=note))

# ================= PGE (table dated March 1948, April 1948 Official Guide)
import numpy as np
pge = line('pge', 'r', 'Pacific Great Eastern', 'pge', R['PG'], ['to Lillooet and Quesnel', 'to Squamish'])
ANCHORS = {'Squamish': (-123.15798, 49.7188427), 'Shalalth': (-122.2207079, 50.729227), 'Lillooet': (-121.9358196, 50.6847013),
           'Williams Lake': (-122.1311388, 52.1194167)}                   # NRWN station points
PGE_NAME = {'Squamish Dock': 'Squamish (Government Dock)'}          # the timetable's "Squamish Dock" (Brendan, 8 October 2026)
PGE_PRINCIPAL = {'Squamish Dock', 'Squamish', 'Alta Lake', 'Pemberton', "D'Arcy", 'Shalalth', 'Lillooet', 'Clinton', 'Lone Butte',
                 'Lac La Hache', 'Williams Lake', 'Quesnel'}
prow = list(csv.DictReader(l for l in open(os.path.join(HERE, 'pge_1948_04.csv')) if not l.startswith('#')))   # April 1948 Official Guide (was Time Table 65, 1949)
mi = {r['station']: float(r['mile']) for r in prow}
am = [0.0] + [mi[n] for n in ANCHORS] + [mi['Quesnel']]
ac = [0.0] + [R['PG'].project(Point(fwd(*p))) for p in ANCHORS.values()] + [R['PG'].length]
for r in prow:                                                             # stations at printed mileage, pinned to the anchor stations
    n = r['station']
    station(pge, PGE_NAME.get(n, n), float(np.interp(mi[n], am, ac)), mi[n], 'PGE_' + re.sub(r'\W+', '_', n.upper()).strip('_'), n in PGE_PRINCIPAL,
            'Pacific Great Eastern station' + (' (Union Steamships connection to Vancouver)' if n == 'Squamish Dock' else ''))
    if n in PGE_NAME: pge['_idx'][n] = pge['_idx'][PGE_NAME[n]]
PGE_TRAINS = (('No1', 0, 'PGE_MWF', 'Connects at the Squamish government dock with the Union Steamships boat from Vancouver (Mondays, Wednesdays and Fridays). Overnight to Quesnel, with stages on to Prince George, Wells and Barkerville.'),
              ('No2', 1, 'PGE_TTS', 'Leaves Quesnel Tuesdays, Thursdays and Saturdays; overnight to the Squamish government dock for the Union Steamships boat to Vancouver.'))
for col, d, svc, note in PGE_TRAINS:
    rs = sorted((r for r in prow if r[col]), key=lambda r: float(r['mile']), reverse=(d == 1))
    stops = [[pge['_idx'][r['station']], *times(r[col]), 1] for r in rs]
    pge['trips'].append(dict(id='PGE-' + col[2:], num=col[2:], name='', svc=svc, dir=d, stops=monotonic(stops), note=note))

for L in lines.values():
    for t in L['trips']:
        f = lambda x: f'{x // 3600:02d}:{x % 3600 // 60:02d}'
        print(L['key'], t['id'], ' '.join(f"{L['stations'][a]['name'][:9]} {f(b)}" for a, b, c, _ in t['stops'][:4]), '...',
              ' '.join(f"{L['stations'][a]['name'][:9]} {f(b)}" for a, b, c, _ in t['stops'][-2:]))

# ---- viz
vd = json.load(open(os.path.join(HERE, 'viz_data.json')))
out = []
for L in lines.values():
    Rt = L['route']; route = []; acc = 0; prev = None
    for xy in Rt.simplify(2.0).coords:
        if prev: acc += math.dist(xy, prev)
        prev = xy; lon, lat = inv(*xy); route.append([round(lon, 6), round(lat, 6), round(acc, 1)])
    sc = acc / Rt.length
    st = []
    for s in L['stations']:
        lon, lat = inv(*Rt.interpolate(s['chain']).coords[0])
        st.append(dict(name=s['name'], chain=round(s['chain'] * sc, 1), lon=round(lon, 6), lat=round(lat, 6), mile=s['mile'],
                       principal=s['principal'], note=s['note'], kml='', gid=s['gid']))
    out.append(dict(key=L['key'], kind=L['kind'], label=L['label'], mainline=True, owner=L['owner'], route=route, stations=st,
                    dirLabels=L['dirLabels'], segments=[],
                    trips=[dict(id=t['id'], num=t['num'], name=t['name'], svc=t['svc'], dir=t['dir'], stops=t['stops'], note=t['note']) for t in L['trips']]))
vd['lines'] = [x for x in vd['lines'] if x['key'] not in lines] + out
open(os.path.join(HERE, 'viz_data.json'), 'w').write(json.dumps(vd, separators=(',', ':')))

# ---- GTFS
def fmt(x): return f'{x // 3600:02d}:{x % 3600 // 60:02d}:{x % 60:02d}'
def app(name, rows):
    with open(os.path.join(GT, name), 'a', newline='') as f: csv.writer(f).writerows(rows)
app('agency.txt', [['EN', 'Esquimalt and Nanaimo Railway (Canadian Pacific)', 'https://en.wikipedia.org/wiki/Esquimalt_and_Nanaimo_Railway', 'America/Vancouver', 'en', ''],
                   ['PGE', 'Pacific Great Eastern Railway', 'https://en.wikipedia.org/wiki/BC_Rail', 'America/Vancouver', 'en', '']])
app('routes.txt', [['ENR', 'EN', 'E&N', 'Victoria – Nanaimo – Courtenay', 2, '7A1E2C', 'FFFFFF', 'E&N Table 164, 1949.'],
                   ['ENA', 'EN', 'E&N Alberni', 'Parksville – Port Alberni', 2, '7A1E2C', 'FFFFFF', 'E&N Table 164, 1949.'],
                   ['PGR', 'PGE', 'PGE', 'Squamish (Government Dock) – Lillooet – Quesnel', 2, '8CC07A', '1B1D27', 'PGE, March 1948 table (April 1948 Official Guide). Steamer connection to Vancouver not shown.']])
app('calendar.txt', [['EN_XSUN', 1, 1, 1, 1, 1, 1, 0, '19490616', '19491231'], ['PGE_MWF', 1, 0, 1, 0, 1, 0, 0, '19490530', '19491231'],
                     ['PGE_WFS', 0, 0, 1, 0, 1, 0, 1, '19490530', '19491231'], ['PGE_TTS', 0, 1, 0, 1, 0, 1, 0, '19490531', '19490910']])
seen = set(r[0] for r in csv.reader(open(os.path.join(GT, 'stops.txt'))))
srows = []
for L in out:
    for s in L['stations']:
        if s['gid'] not in seen: seen.add(s['gid']); srows.append([s['gid'], f"{s['name']} ({'PGE' if L['key'] == 'pge' else 'E&N'})", f"{s['lat']:.6f}", f"{s['lon']:.6f}", s['note']])
app('stops.txt', srows)
rid = {'en': 'ENR', 'ena': 'ENA', 'pge': 'PGR'}
shp, trows, strows = [], [], []
for L in out:
    Rt = lines[L['key']]['route']
    for sid, coords in ((L['key'].upper() + '_OUT', list(Rt.coords)), (L['key'].upper() + '_IN', list(Rt.coords)[::-1])):
        a, p = 0.0, None
        for k, xy in enumerate(coords):
            if p: a += math.dist(p, xy)
            p = xy; lon, lat = inv(*xy); shp.append([sid, f'{lat:.6f}', f'{lon:.6f}', k, f'{a:.1f}'])
    for t in L['trips']:
        trows.append([rid[L['key']], t['svc'], t['id'], L['stations'][t['stops'][-1][0]]['name'], f"{t['num']} {t['name']}".strip(), t['dir'],
                      L['key'].upper() + ('_OUT' if t['dir'] == 0 else '_IN')])
        for k, (i, a, b, tp) in enumerate(t['stops'], 1):
            c = lines[L['key']]['stations'][i]['chain']; dist = c if t['dir'] == 0 else Rt.length - c
            strows.append([t['id'], fmt(a), fmt(b), L['stations'][i]['gid'], k, f'{dist:.1f}', 1])
app('shapes.txt', shp); app('trips.txt', trows); app('stop_times.txt', strows)
with zipfile.ZipFile(os.path.join(HERE, 'bcer_fraser_valley_1949_gtfs.zip'), 'w', zipfile.ZIP_DEFLATED) as z:
    for fn in sorted(os.listdir(GT)): z.write(os.path.join(GT, fn), fn)
print({k: (len(v['stations']), len(v['trips'])) for k, v in lines.items()})
