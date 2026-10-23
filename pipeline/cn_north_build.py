"""CN Jasper - Prince George - Prince Rupert (Tables 225 and 226, 1949), from Jasper.
Track from nrwn/north.json (NRWN, B.C. only), and from Jasper to the border the main line's own track (read from the cn line: needs mainline_build); adds line 'cnn' to viz_data.json and the GTFS feed.
Stations sit at printed mileage, pinned to NRWN station points at Yellowhead, Red Pass Jct, McBride, Prince George, Endako,
Smithers, Terrace and Prince Rupert."""
import csv, json, math, os, re, zipfile
import numpy as np
from shapely.geometry import Point, LineString
from nrwn_graph import Net, fwd, inv, MI
HERE = os.path.dirname(os.path.abspath(__file__)); GT = os.path.join(HERE, 'gtfs')

SUBS = {'Albreda', 'Robson', 'Tete Jaune', 'Fraser', 'Nechako', 'Telkwa', 'Bulkley', 'Skeena'}
net = Net(json.load(open(os.path.join(HERE, 'nrwn', 'north.json'))), subs=SUBS)
ANCH = [('Yellowhead', (-118.4753198, 52.891134)), ('Red Pass Jct', (-119.0038947, 52.9859644)), ('Emperor', (-119.2338301, 53.0143125)),
        ('McBride', (-120.1703005, 53.3005549)), ('Prince George', (-122.7441853, 53.9193171)), ('Endako', (-125.0213692, 54.0852532)),
        ('Smithers', (-127.1762186, 54.7777076)), ('Terrace', (-128.5827713, 54.5142371)), ('Prince Rupert', (-130.3293425, 54.3141871))]
BORDER = (-118.4644008, 52.8913423)            # east end of the B.C. track data: the Alberta border at Yellowhead Pass
RT, snaps = net.route(BORDER, *[p for _, p in ANCH])
# Jasper to the border: the cn line's track (built by mainline_build), so the trains start at Jasper as printed
_cn = next(L for L in json.load(open(os.path.join(HERE, 'viz_data.json')))['lines'] if L['key'] == 'cn')
_jch = next(s['chain'] for s in _cn['stations'] if s['gid'] == 'CN_JASPER')
_cnl = LineString([fwd(p[0], p[1]) for p in _cn['route']]); _bch = _cnl.project(Point(fwd(*BORDER)))
_pre = [fwd(p[0], p[1]) for p in _cn['route'] if _bch < p[2] < _jch][::-1]
_jxy = fwd(*next((s['lon'], s['lat']) for s in _cn['stations'] if s['gid'] == 'CN_JASPER'))
RT = LineString([_jxy] + _pre + list(RT.coords))
ANCH = [('Jasper', inv(*_jxy))] + ANCH
print(f'CN Yellowhead Pass - Prince Rupert {RT.length/MI:.1f} mi (timetable 1757.9-1054.8 = 703.1 from Yellowhead), snaps {[round(s) for s in snaps]}')

rows = list(csv.DictReader(l for l in open(os.path.join(HERE, 'cn_1949_tables225_226.csv')) if not l.startswith('#')))
rows = [r for r in rows if float(r['mile']) >= 1037.3]                    # from Jasper
mi = {r['station']: float(r['mile']) for r in rows}
am = [mi[n] for n, _ in ANCH]; ac = [RT.project(Point(fwd(*p))) for _, p in ANCH]
for (n, _), c in zip(ANCH, ac): print(f'  {n}: mile {mi[n]:.1f}, {c/MI:.1f} mi along the track')
def chain(m):
    if m <= am[0]: return ac[0] - (am[0] - m) * MI
    if m >= am[-1]: return min(RT.length, ac[-1] + (m - am[-1]) * MI)
    return float(np.interp(m, am, ac))

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

PRINCIPAL = {'Jasper', 'Yellowhead', 'Red Pass Jct', 'Tete Jaune', 'McBride', 'Dome Creek', 'Hansard', 'Prince George', 'Vanderhoof', 'Fort Fraser',
             'Endako', 'Burns Lake', 'Houston', 'Smithers', 'Hazelton', 'Kitwanga', 'Pacific', 'Terrace', 'Prince Rupert'}
stations, idx = [], {}
for r in rows:
    n = r['station']; idx[n] = len(stations)
    shared = mi[n] <= 1081.0                                             # Yellowhead - Red Pass Jct: the main line's stations
    stations.append(dict(name=n, chain=chain(mi[n]), mile=mi[n], principal=n in PRINCIPAL,
                         gid=('CN_' + n.upper().replace(' ', '_')) if shared else 'CNN_' + re.sub(r'\W+', '_', n.upper()).strip('_'),
                         note='Canadian National station' + (' (junction for Kamloops and Vancouver)' if n == 'Red Pass Jct' else '')))
TRAINS = (('No195', '195', 'CN_MWF', 0, 'Jasper (4.00 p.m.) to Prince Rupert, arriving 10.45 p.m. the next day. Coach, café-lounge and sleeping cars.'),
          ('No196', '196', 'CN_MWF', 1, 'Prince Rupert (8.00 p.m.) to Jasper, arriving 6.00 a.m. two days later. Connects at Prince Rupert with CN steamships.'),
          ('M389', 'M389', 'CN_TTS', 0, 'Mixed train, McBride to Prince George.'),
          ('M390', 'M390', 'CN_MWF', 1, 'Mixed train, Prince George to McBride.'))
trips = []
for col, num, svc, d, note in TRAINS:
    rs = sorted((r for r in rows if re.search(r'\d', r[col])), key=lambda r: float(r['mile']), reverse=(d == 1))
    stops = [[idx[r['station']], *times(r[col]), 1] for r in rs]
    trips.append(dict(id='CN-' + num, num=num, name='Mixed' if num.startswith('M') else '', svc=svc, dir=d, stops=monotonic(stops), note=note))
    f = lambda x: f'{x // 3600:02d}:{x % 3600 // 60:02d}'
    print(' ', num, ' '.join(f"{stations[a]['name'][:9]} {f(b)}" for a, b, c, _ in stops[:2]), '...', ' '.join(f"{stations[a]['name'][:9]} {f(b)}" for a, b, c, _ in stops[-2:]))
bad = []
for t in trips:
    for (a, _, da, _), (b, tb, _, _) in zip(t['stops'], t['stops'][1:]):
        dist = abs(stations[b]['chain'] - stations[a]['chain']) / MI; mins = (tb - da) / 60
        if mins <= 0 or dist / (mins / 60) > 50: bad.append(f"{t['id']} {stations[a]['name']}->{stations[b]['name']} {dist:.1f}mi/{mins:.0f}min")
print('  fast/odd runs:', bad or 'none')

# ---- viz
vd = json.load(open(os.path.join(HERE, 'viz_data.json')))
route = []; acc = 0; prev = None
for xy in RT.simplify(3.0).coords:
    if prev: acc += math.dist(xy, prev)
    prev = xy; lon, lat = inv(*xy); route.append([round(lon, 6), round(lat, 6), round(acc, 1)])
sc = acc / RT.length
st = []
for s in stations:
    lon, lat = inv(*RT.interpolate(s['chain']).coords[0])
    st.append(dict(name=s['name'], chain=round(s['chain'] * sc, 1), lon=round(lon, 6), lat=round(lat, 6), mile=s['mile'],
                   principal=s['principal'], note=s['note'], kml='', gid=s['gid']))
line = dict(key='cnn', kind='q', label='Canadian National', mainline=True, owner='cn', route=route, stations=st,
            dirLabels=['to Prince George and Prince Rupert', 'to Jasper'], trips=trips,
            segments=[dict(owner='none', a=0.0, b=round(stations[idx['Red Pass Jct']]['chain'] * sc, 1))])   # drawn by the main line
vd['lines'] = [x for x in vd['lines'] if x['key'] != 'cnn'] + [line]
open(os.path.join(HERE, 'viz_data.json'), 'w').write(json.dumps(vd, separators=(',', ':')))

# ---- GTFS
def fmt(x): return f'{x // 3600:02d}:{x % 3600 // 60:02d}:{x % 60:02d}'
def app(name, rows_):
    with open(os.path.join(GT, name), 'a', newline='') as fh: csv.writer(fh).writerows(rows_)
app('routes.txt', [['CNN', 'CN', 'CN Prince Rupert', 'Jasper – Prince George – Prince Rupert', 2, '2F6B44', 'FFFFFF', 'CN Tables 225 and 226, 1949.']])
seen = set(r[0] for r in csv.reader(open(os.path.join(GT, 'stops.txt'))))
app('stops.txt', [[s['gid'], s['name'] + ' (CN)', f"{s['lat']:.6f}", f"{s['lon']:.6f}", s['note']] for s in st if s['gid'] not in seen])
shp = []
for sid, coords in (('CNN_OUT', list(RT.coords)), ('CNN_IN', list(RT.coords)[::-1])):
    a, p = 0.0, None
    for k, xy in enumerate(coords):
        if p: a += math.dist(p, xy)
        p = xy; lon, lat = inv(*xy); shp.append([sid, f'{lat:.6f}', f'{lon:.6f}', k, f'{a:.1f}'])
app('shapes.txt', shp)
app('trips.txt', [['CNN', t['svc'], t['id'], stations[t['stops'][-1][0]]['name'], f"{t['num']} {t['name']}".strip(), t['dir'],
                   'CNN_OUT' if t['dir'] == 0 else 'CNN_IN'] for t in trips])
app('stop_times.txt', [[t['id'], fmt(a), fmt(b), stations[i]['gid'], k, f"{(stations[i]['chain'] if t['dir'] == 0 else RT.length - stations[i]['chain']):.1f}", 1]
                       for t in trips for k, (i, a, b, tp) in enumerate(t['stops'], 1)])
with zipfile.ZipFile(os.path.join(HERE, 'bcer_fraser_valley_1949_gtfs.zip'), 'w', zipfile.ZIP_DEFLATED) as z:
    for fn in sorted(os.listdir(GT)): z.write(os.path.join(GT, fn), fn)
print('cnn', len(st), 'stations', len(trips), 'trips')
