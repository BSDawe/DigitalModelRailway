"""Burnaby Lake Line: stations + running-time pattern from 'Vancouver Street Car Timetables' p.24,
geometry from the Fourth District KML. Departures go in DEPS (none known yet -> no trips)."""
import csv, json, os, re, zipfile
from xml.etree import ElementTree as ET
from pyproj import Transformer
from shapely.geometry import LineString, Point
HERE = os.path.dirname(os.path.abspath(__file__)); GT = os.path.join(HERE, 'gtfs')
fwd = Transformer.from_crs(4326, 26910, always_xy=True).transform
inv = Transformer.from_crs(26910, 4326, always_xy=True).transform
MI = 1609.344
bl = json.load(open(os.path.join(HERE, 'bl_geometry.json')))
R = LineString([fwd(*p) for p in bl['route']])

# card: (name, KML placemark or None, minutes read down, minutes read up)
CARD = [('Vancouver', '*VAN', 0, 55), ('Slocan St.', 'Slocan station', 16, 36),
        ('Horne Payne', 'Hastings Townsite/Hornepayne station', 20, 32), ('Gilmore', 'Gilmore station', 22, 30),
        ('Queens', 'Queens station', 23, 29), ('Ardley', 'Ardley station', 24, 28), ('Murrin', 'Murrin station', 25, 27),
        ('Douglas Rd.', 'Douglas Road station', 26, 26), ('Sprott', 'Sprott street station', 28, 24),
        ('Burnaby Lake', 'Burnaby Lake station', 30, 22), ('Rayside', None, 32, 20), ('Vorce', 'Vorce station', 33, 19),
        ('Hill', 'Hill station', 35, 18), ('Cumberland Rd.', 'Cumberland', 36, 17), ('Stormont', None, 37, 16),
        ('Cariboo', 'Cariboo', 38, 15), ('Sapperton', 'Sapperton station', 42, 12),
        ('New Westminster', '*NW', 55, 0)]
# KML stations the card does not time (it lists only timed stops): flag stops
FLAG = {'6th avenue east station': '6th Avenue', 'Victoria station': 'Victoria Drive', 'Lakewood station': 'Lakewood',
        'Nanaimo Street station': 'Nanaimo Street', 'Clinton station': 'Clinton', 'Renfrew Street station': 'Renfrew Street',
        'Windermere station': 'Windermere', 'Cassair station': 'Cassiar'}

NS = {'k': 'http://www.opengis.net/kml/2.2'}; K = '{http://www.opengis.net/kml/2.2}'
tree = ET.parse(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'British_Columbia_Electric_Railway_Company.kml'))
par = {c: p for p in tree.iter() for c in p}
def fpath(e):
    o = []
    while e in par:
        e = par[e]
        if e.tag == K + 'Folder': o.append(e.find('k:name', NS).text)
    return '/'.join(o[::-1])
kml = {}
for p in tree.iter(K + 'Placemark'):
    if fpath(p).endswith('Fourth District/Stations'):
        kml[p.find('k:name', NS).text] = tuple(map(float, p.find('.//k:coordinates', NS).text.split(',')[:2]))

stops = []
for name, kn, down, up in CARD:
    if kn == '*VAN': ch, ll, note = 0.0, None, ''
    elif kn == '*NW': ch, ll, note = R.length, None, ''
    elif kn: ll = kml[kn]; ch = R.project(Point(fwd(*ll))); note = 'Shown as North Westminster in the 1933 timetable; Sunday cars in 1942 terminated here, with a bus on to New Westminster' if name == 'Sapperton' else ''
    else: ch, ll, note = None, None, 'not plotted in KML; placed midway between neighbours'
    stops.append(dict(name=name, chain=ch, lonlat=ll, down=down, up=up, tp=1, note=note))
for i, s in enumerate(stops):
    if s['chain'] is None:
        s['chain'] = (stops[i - 1]['chain'] + stops[i + 1]['chain']) / 2
        s['lonlat'] = inv(*R.interpolate(s['chain']).coords[0])
for kn, name in FLAG.items():
    ll = kml[kn]; stops.append(dict(name=name, chain=R.project(Point(fwd(*ll))), lonlat=ll, down=None, up=None, tp=0,
                                     note='flag stop on the KML, not timed on the card'))
stops.sort(key=lambda s: s['chain'])
assert [s['name'] for s in stops if s['tp']] == [c[0] for c in CARD]

def fill(key):
    known = [i for i, s in enumerate(stops) if s[key] is not None]
    t = {}
    for a, b in zip(known, known[1:]):
        for i in range(a, b + 1):
            f = (stops[i]['chain'] - stops[a]['chain']) / (stops[b]['chain'] - stops[a]['chain'])
            t[i] = round((stops[a][key] + f * (stops[b][key] - stops[a][key])) * 60)
    return t
down, up = fill('down'), fill('up')
for i in range(len(stops) - 1):
    a, b = stops[i], stops[i + 1]
    if a['tp'] and b['tp'] or True:
        pass
tps = [i for i, s in enumerate(stops) if s['tp']]
print('EB mph:', ' '.join(f"{(stops[b]['chain']-stops[a]['chain'])/MI/((down[b]-down[a])/3600):.0f}" for a, b in zip(tps, tps[1:])))
print('WB mph:', ' '.join(f"{(stops[b]['chain']-stops[a]['chain'])/MI/((up[a]-up[b])/3600):.0f}" for a, b in zip(tps, tps[1:])))

# ---------------- departures: Burnaby Lake Line time table R 1M-1-42 (January 1942), Sunday side
H, M_ = 3600, 60
def hh(h, m): return h * H + m * M_
SUN = dict(
    eb_sap=[hh(h, 30) for h in range(8, 24)],                  # 8.30 a.m. hourly to 11.30 p.m., to Sapperton
    eb_dgl=[hh(9, 0), hh(10, 0), hh(11, 0), hh(12, 0)],        # extra half-hourly cars to Douglas Road until noon
    wb_sap=[hh(7, 12), hh(7, 42), hh(8, 12)] + [hh(h, 42) for h in range(8, 23)],   # from Sapperton, last 10.42 p.m.
    wb_dgl=[hh(9, 26), hh(10, 26), hh(11, 26)],               # the half-hourly extras from Douglas Road
)
def pm(h, m): return hh(h + 12 if h != 12 else 12, m)
# Daily except Sundays side, effective January 16, 1942. * on the card = Vancouver to Douglas Road only.
WK_VAN = ['6.30a','7.00a','7.30a','8.00a','8.30a','9.00a*','9.30a','10.00a*','10.30a','11.00a*','11.30a','12.00p*',
          '12.30p','1.00p*','1.30p','2.00p*','2.30p','3.00p*','3.30p','4.00p*','4.30p','5.00p','5.30p','6.00p','6.30p',
          '7.00p*','7.30p','8.00p*','8.30p','9.00p*','9.30p','10.00p*','10.30p','11.00p*','11.30p','12.00m']
def parse(x):
    star = x.endswith('*'); x = x.rstrip('*'); suf = x[-1]; h, m = map(int, x[:-1].split('.'))
    if suf == 'p' and h != 12: h += 12
    if suf == 'm': h = 24
    return hh(h, m), star
WK_SAP = [hh(5, 42), hh(6, 12), hh(6, 42), hh(7, 12), hh(7, 42), hh(8, 12), hh(8, 42)] + [hh(h, 42) for h in range(9, 23)]
WK_DGL_ALL = list(range(hh(5, 56), hh(23, 26) + 1, 30 * 60))           # every 30 min, 5.56 a.m. to 11.26 p.m.
from_sap = {t + 14 * 60 for t in WK_SAP}                                 # Sapperton cars pass Douglas Road 14 min later
WK = dict(eb_sap=[t for t, st in map(parse, WK_VAN) if not st], eb_dgl=[t for t, st in map(parse, WK_VAN) if st],
          wb_sap=WK_SAP, wb_dgl=[t for t in WK_DGL_ALL if t not in from_sap])
print('weekday: to Sapperton', len(WK['eb_sap']), 'to Douglas', len(WK['eb_dgl']), 'from Sapperton', len(WK['wb_sap']),
      'from Douglas', len(WK['wb_dgl']))
DEPS = {'BL_SUN': SUN, 'BL_WKDY': WK}

# ---------------- viz block
vd = json.load(open(os.path.join(HERE, 'viz_data.json')))
route = []; acc = 0; prev = None
for xy in R.simplify(1.0).coords:
    if prev: acc += ((xy[0]-prev[0])**2 + (xy[1]-prev[1])**2) ** .5
    prev = xy; lon, lat = inv(*xy); route.append([round(lon, 6), round(lat, 6), round(acc, 1)])
scale = acc / R.length
st_out = []
for i, s in enumerate(stops):
    shared = {'Vancouver': 'S00', 'New Westminster': 'S01'}.get(s['name'])
    st_out.append(dict(name=s['name'], shared=shared, chain=round(s['chain'] * scale, 1),
                       lon=None if s['lonlat'] is None else round(s['lonlat'][0], 6),
                       lat=None if s['lonlat'] is None else round(s['lonlat'][1], 6), tp=s['tp'], note=s['note'],
                       mile=round(s['chain'] / MI, 1)))
n = len(stops)
pat0 = [[i, down[i], down[i], stops[i]['tp']] for i in range(n)]
pat1 = [[i, up[i] if False else (55 * 60 - 0) - 0, 0, 0] for i in range(0)]
pat1 = [[i, up[i], up[i], stops[i]['tp']] for i in range(n - 1, -1, -1)]
names = [x['name'] for x in stops]
def trip(svc, d, t0, a, b):
    ia, ib = names.index(a), names.index(b)
    if d == 0:
        seq = range(ia, ib + 1); off = lambda i: down[i] - down[ia]
    else:
        seq = range(ia, ib - 1, -1); off = lambda i: up[i] - up[ia]
    return dict(svc=svc, dir=d, id=f"{svc}-{d}-{t0}-{b[:3]}", stops=[[i, t0 + off(i), t0 + off(i), stops[i]['tp']] for i in seq])
trips = []
for svc, D in DEPS.items():
    trips += ([trip(svc, 0, t, 'Vancouver', 'Sapperton') for t in D['eb_sap']] +
              [trip(svc, 0, t, 'Vancouver', 'Douglas Rd.') for t in D['eb_dgl']] +
              [trip(svc, 1, t, 'Sapperton', 'Vancouver') for t in D['wb_sap']] +
              [trip(svc, 1, t, 'Douglas Rd.', 'Vancouver') for t in D['wb_dgl']])
vd['bl'] = dict(route=route, stations=st_out, pattern={'0': pat0, '1': pat1}, trips=trips)

# ---------------- GTFS
def fmt(x): return f'{x // 3600:02d}:{x % 3600 // 60:02d}:{x % 60:02d}'
def app(name, rows):
    with open(os.path.join(GT, name), 'a', newline='') as f: csv.writer(f).writerows(rows)
app('routes.txt', [['BLL', 'BCER', 'Burnaby Lake', 'Vancouver – Sapperton – New Westminster (Burnaby Lake Line)', 2,
                    '1F7A99', 'FFFFFF', 'Running times from the 1942 Burnaby Lake Line time table (1933 where noted); Cars ran Vancouver–Sapperton; buses on to New Westminster.']])
app('calendar.txt', [['BL_SUN', 0, 0, 0, 0, 0, 0, 1, '19490616', '19491231'], ['BL_WKDY', 1, 1, 1, 1, 1, 1, 0, '19490616', '19491231']])
sid = {}
for i, x in enumerate(stops):
    if x['name'] == 'Vancouver': sid[i] = 'S00'; continue
    if x['name'] == 'New Westminster': sid[i] = 'S01'; continue
    sid[i] = f'B{i:02d}'
app('stops.txt', [[sid[i], x['name'], f"{x['lonlat'][1]:.6f}", f"{x['lonlat'][0]:.6f}", 'Burnaby Lake Line' + ('; ' + x['note'] if x['note'] else '')]
                  for i, x in enumerate(stops) if sid[i].startswith('B')])
shp = []
for shape_id, coords in (('BL_EB', list(R.coords)), ('BL_WB', list(R.coords)[::-1])):
    acc, prev = 0.0, None
    for k, xy in enumerate(coords):
        if prev: acc += ((xy[0]-prev[0])**2 + (xy[1]-prev[1])**2) ** .5
        prev = xy; lon, lat = inv(*xy); shp.append([shape_id, f'{lat:.6f}', f'{lon:.6f}', k, f'{acc:.1f}'])
app('shapes.txt', shp)
app('trips.txt', [['BLL', tr['svc'], tr['id'], names[tr['stops'][-1][0]], 'Burnaby Lake car', tr['dir'], 'BL_EB' if tr['dir'] == 0 else 'BL_WB'] for tr in trips])
rows = []
for tr in trips:
    for k, (i, a, b, tp) in enumerate(tr['stops'], 1):
        dist = stops[i]['chain'] if tr['dir'] == 0 else R.length - stops[i]['chain']
        rows.append([tr['id'], fmt(a), fmt(b), sid[i], k, f'{dist:.1f}', 1 if k in (1, len(tr['stops'])) else tp])
app('stop_times.txt', rows)
with zipfile.ZipFile(os.path.join(HERE, 'bcer_fraser_valley_1949_gtfs.zip'), 'w', zipfile.ZIP_DEFLATED) as z:
    for fn in sorted(os.listdir(GT)): z.write(os.path.join(GT, fn), fn)
print('BL trips', len(trips), 'stop_times', len(rows))
open(os.path.join(HERE, 'viz_data.json'), 'w').write(json.dumps(vd, separators=(',', ':')))
json.dump(dict(stops=stops, down=down, up=up), open(os.path.join(HERE, 'bl_model.json'), 'w'))
print('stations', n)
