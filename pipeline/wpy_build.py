"""White Pass & Yukon Route, Skagway - Whitehorse summer schedule, from the May 1948 Official Guide. The whole line, from three sources joined end
to end: Alaska from the old NTAD shape Brendan supplied (traces/wpy_alaska_ntad.tsv, coarse above Skagway), British Columbia from the national
network (nrwn/wpy.json) and the Yukon from the Yukon file of the same (nrwn/wpy_yt.json, cut from nrwn/yt.kml). Stations sit at their printed
mileage, scaled between the fixed points: Skagway, the summit boundary at White Pass (mile 20.4), Carcross station (67.5) and Whitehorse (110.7).
Reads nothing from the other steps."""
import csv, json, math, os, re, zipfile
from shapely.geometry import LineString, Point
from shapely.ops import substring
from nrwn_graph import Net, fwd, inv, MI
HERE = os.path.dirname(os.path.abspath(__file__)); GT = os.path.join(HERE, 'gtfs')
csv.field_size_limit(10 ** 9)
# Alaska: the NTAD arcs, chained by their node numbers from tidewater to the summit
arcs = {r['FRFRANODE']: (r['TOFRANODE'], [tuple(map(float, p.split())) for p in re.search(r'\(\((.*)\)\)', r['wkt_geom']).group(1).split(', ')])
        for r in csv.DictReader(open(os.path.join(HERE, 'traces', 'wpy_alaska_ntad.tsv')), delimiter='\t')}
node = (set(arcs) - {v[0] for v in arcs.values()}).pop(); AK = []
while node in arcs:
    node, pts = arcs[node]; AK += pts if not AK else pts[1:]
# British Columbia and the Yukon: the national network
F = json.load(open(os.path.join(HERE, 'nrwn', 'wpy.json')))
T_ = [p for f in F if f['schema'] == '#kml_schema_ft_Track' and f['data'].get('trackClassification') == 'Main' for c in f['coords'] for p in c]
BC, _ = Net(F).route(tuple(min(T_, key=lambda p: p[1])), tuple(max(T_, key=lambda p: p[1])))
Y = [dict(f, schema='#kml_schema_ft_Track') for f in json.load(open(os.path.join(HERE, 'nrwn', 'wpy_yt.json'))) if f['schema'] == '#Track']
CARCROSS, WHITEHORSE = (-134.706200, 60.164573), (-135.0493, 60.7214)       # the station point in the Yukon file; the depot at the foot of Main Street
YT, _ = Net(Y).route(tuple(inv(*BC.coords[-1])), CARCROSS, WHITEHORSE)
ak = [fwd(*p) for p in AK]
print(f'joins: Alaska-B.C. {math.dist(ak[-1], BC.coords[0]):.1f} m, B.C.-Yukon {math.dist(BC.coords[-1], YT.coords[0]):.1f} m')
pts = ak + list(BC.coords)[1:] + list(YT.coords)[1:]
RT = LineString([p for k, p in enumerate(pts) if k == 0 or math.dist(p, pts[k - 1]) > 0.5])
RT = substring(RT, 0, RT.project(Point(fwd(*WHITEHORSE))))
d_wp = LineString(ak).length; d_cc = RT.project(Point(fwd(*CARCROSS)))
FIX = [(0.0, 0.0), (20.4, d_wp), (67.5, d_cc), (110.7, RT.length)]
print(f'traced: Skagway-White Pass {d_wp / MI:.1f} mi (printed 20.4), White Pass-Carcross {(d_cc - d_wp) / MI:.1f} (47.1), Carcross-Whitehorse {(RT.length - d_cc) / MI:.1f} (43.2); '
      f'B.C. boundary to boundary {BC.length / MI:.1f} mi')
def at(mile):
    for (m0, d0), (m1, d1) in zip(FIX, FIX[1:]):
        if mile <= m1: return d0 + (mile - m0) / (m1 - m0) * (d1 - d0)
def hm(t):
    m = re.match(r'(\d+)\.(\d+)([ap])', t); h = int(m.group(1)) % 12 + (12 if m.group(3) == 'p' else 0); return h * 3600 + int(m.group(2)) * 60
ST = [('Skagway', 0.0, True, 'Alaska; the wharf and depot at tidewater'), ('White Pass', 20.4, True, 'the summit, on the Alaska - British Columbia boundary (2,885 ft)'),
      ('Log Cabin', 32.7, False, 'British Columbia (2,916 ft)'), ('Bennett', 40.6, True, 'British Columbia, at the head of Lake Bennett; the meal stop'),
      ('Carcross', 67.5, True, 'Yukon; steamer connection for the lakes'), ('Whitehorse', 110.7, True, 'Yukon; the head of navigation on the Yukon River')]
# times as printed, reading down for 5, 3, 1 and up for 2, 6: (arrive, leave) where the table gives both
TR = {
 '5': ('WP_MTTFS', 0, ['8.45a', '10.25a', '11.00a', ('11.25a', '11.55a'), ('1.09p', '1.22p'), '3.20p'], 'Mondays, Tuesdays, Thursdays, Fridays and Saturdays.'),
 '3': ('WP_SW', 0, ['8.30a', '9.40a', '10.15a', '10.35a', '11.40a', None], 'Sundays and Wednesdays, Skagway to Carcross only; the table marks it as a steamer connection.'),
 '1': ('WP_SW', 0, ['10.00a', '11.40a', '12.15p', ('12.40p', '1.15p'), ('2.29p', '2.42p'), '4.40p'], 'Sundays and Wednesdays.'),
 '2': ('WP_SW', 1, ['4.25p', '2.45p', '2.10p', ('1.15p', '1.45p'), ('11.50a', '12.06p'), '10.15a'], 'Sundays and Wednesdays.'),
 '6': ('WP_MTTFS', 1, ['3.05p', '1.25p', '12.50p', ('11.55a', '12.25p'), '10.46a', '9.10a'], 'Mondays, Tuesdays, Thursdays, Fridays and Saturdays.'),
}
route = []; acc = 0.0; prev = None
for xy in RT.simplify(2.0).coords:
    if prev: acc += math.dist(xy, prev)
    prev = xy; lon, lat = inv(*xy); route.append([round(lon, 6), round(lat, 6), round(acc, 1)])
sc = acc / RT.length
stations = []
for n, mile, pr, note in ST:
    d = at(mile); lon, lat = inv(*RT.interpolate(d).coords[0])
    stations.append(dict(name=n, chain=round(d * sc, 1), lon=round(lon, 6), lat=round(lat, 6), mile=mile, principal=pr, kml='', gid='WPY_' + n.upper().replace(' ', '_'),
                         note='White Pass & Yukon Route: ' + note))
    print(f'  {n:11s} mile {mile:5.1f}  {lat:.4f}, {lon:.4f}')
trips = []
for num, (svc, d, times, days) in TR.items():
    stops = []
    for i, t in enumerate(times):
        if t is None: continue
        a, b = (hm(t[0]), hm(t[1])) if isinstance(t, tuple) else (hm(t), hm(t))
        stops.append([i, a, b, 1])
    if d == 1: stops.reverse()
    ends = (stations[stops[0][0]]['name'], stations[stops[-1][0]]['name'])
    trips.append(dict(id='WPY-' + num, num=num, name='White Pass & Yukon', svc=svc, dir=d, stops=stops, note=f'{ends[0]} to {ends[1]}, {days} Summer schedule; narrow gauge.'))
    print(' ', num, [(stations[i]['name'], f'{a // 3600:02d}:{a % 3600 // 60:02d}', f'{b // 3600:02d}:{b % 3600 // 60:02d}') for i, a, b, _ in stops])
    assert all(x[2] <= y[1] for x, y in zip(stops, stops[1:])), num
vd = json.load(open(os.path.join(HERE, 'viz_data.json')))
vd['lines'] = [x for x in vd['lines'] if x['key'] != 'wpy'] + [dict(key='wpy', kind='y', label='White Pass & Yukon Route', mainline=True, livery='wpy', owner='wpy', route=route, stations=stations,
                                                               dirLabels=['to Carcross and Whitehorse', 'to Skagway'], segments=[], trips=trips, src='Official Guide, May 1948')]
open(os.path.join(HERE, 'viz_data.json'), 'w').write(json.dumps(vd, separators=(',', ':')))
def fmt(x): return f'{x // 3600:02d}:{x % 3600 // 60:02d}:{x % 60:02d}'
def app(name, rows_):
    with open(os.path.join(GT, name), 'a', newline='') as fh: csv.writer(fh).writerows(rows_)
app('agency.txt', [['WPY', 'White Pass & Yukon Route', 'https://en.wikipedia.org/wiki/White_Pass_and_Yukon_Route', 'America/Vancouver', 'en', '']])
app('calendar.txt', [['WP_MTTFS', 1, 1, 0, 1, 1, 1, 0, '19490616', '19491231'], ['WP_SW', 0, 0, 1, 0, 0, 0, 1, '19490616', '19491231']])
app('routes.txt', [['WPY', 'WPY', 'White Pass & Yukon', 'Skagway – White Pass – Bennett – Carcross – Whitehorse', 2, '4F7A28', 'FFFFFF', 'Summer schedule, from the Official Guide, May 1948. Times as printed.']])
app('stops.txt', [[s['gid'], s['name'] + ' (WP&Y)', f"{s['lat']:.6f}", f"{s['lon']:.6f}", s['note']] for s in stations])
tot = route[-1][2]
for sid, pts_ in (('WPY_OUT', route), ('WPY_IN', route[::-1])):
    app('shapes.txt', [[sid, f'{p[1]:.6f}', f'{p[0]:.6f}', k, f"{(p[2] if sid.endswith('OUT') else tot - p[2]):.1f}"] for k, p in enumerate(pts_)])
app('trips.txt', [['WPY', t['svc'], t['id'], stations[t['stops'][-1][0]]['name'], 'No. ' + t['num'], t['dir'], 'WPY_OUT' if t['dir'] == 0 else 'WPY_IN'] for t in trips])
app('stop_times.txt', [[t['id'], fmt(a), fmt(b), stations[i]['gid'], k, f"{(stations[i]['chain'] if t['dir'] == 0 else tot - stations[i]['chain']):.1f}", tp] for t in trips for k, (i, a, b, tp) in enumerate(t['stops'], 1)])
print(f'wpy: {acc / MI:.1f} mi, {len(stations)} stations, {len(trips)} trips')
