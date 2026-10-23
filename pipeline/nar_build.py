"""Northern Alberta Railways, Edmonton - McLennan - Rycroft (and Spirit River) - Grande Prairie - Dawson Creek, B.C.: trains No. 1 and No. 2 from the
table of April 25, 1948 in the May 1948 Official Guide (nar_1948_04.csv). Dawson Creek was reached from Alberta; the PGE did not get there until 1958.
Track: the Alberta file of the national network (nrwn/alberta.json), with Brendan's traces for the abandoned line by Watino (traces/nar_watino.kml)
and the old downtown loop to the CN station in Edmonton (traces/edmonton_terminal.kml), and the Dawson Creek end from the B.C. file (nrwn/dawson.json).
The line from the Alberta boundary by Tupper and Pouce Coupe to the east end of the Dawson Creek yard is in neither file: it is Brendan's trace
(traces/nar_dawson_creek_gap.kml). Between the CN station and the point where it leaves the CN line the track is drawn by the cn line (read from
viz_data.json: needs mainline_build).
The table is in Mountain time; the trips are made an hour earlier, in Pacific time. Reads nothing from the other steps."""
import csv, json, math, os, re
import xml.etree.ElementTree as ET
import numpy as np
from shapely.geometry import LineString, Point
from nrwn_graph import Net, fwd, inv, MI
HERE = os.path.dirname(os.path.abspath(__file__)); GT = os.path.join(HERE, 'gtfs')
NS = '{http://www.opengis.net/kml/2.2}'
def kml(fn): return [[tuple(map(float, t.split(',')[:2])) for t in c.text.split()] for c in ET.parse(os.path.join(HERE, 'traces', fn)).iter(NS + 'coordinates')]
def feat(c): return dict(schema='#kml_schema_ft_Track', data={'trackClassification': 'Main'}, coords=[c])
A = [f for f in json.load(open(os.path.join(HERE, 'nrwn', 'alberta.json'))) if f['schema'].endswith('Track')]
watino = kml('nar_watino.kml')[0]; terminal = kml('edmonton_terminal.kml')[0]
_n = Net(A)
print(f'  Watino trace: ends {_n.near(fwd(*watino[0]))[1]:.0f} m and {_n.near(fwd(*watino[-1]))[1]:.0f} m from the network')
net = Net(A + [feat(watino), feat(terminal)])
EDMONTON = (-113.4917, 53.5470)                                        # the Canadian National station, 104 Avenue at 100 Street
RYCROFT, SPIRIT_RIVER = (-118.7050, 55.7568), (-118.8272, 55.7790)   # Rycroft station, on the line in from the east; the end of the Spirit River spur
BORDER = (-120.001351, 55.485190)                                      # where the Alberta file's track ends, on the boundary
DC_YARD_EAST, DAWSON_CREEK = (-120.156845, 55.748660), (-120.2285, 55.7597)   # where the B.C. file's track begins; the N.A.R. station
def leg(n, *pts, start_any=False):
    r, sn = n.route(*pts, start_any=start_any); return list(r.coords), sn
a, s1 = leg(net, EDMONTON, (-113.5552, 53.5837), (-113.650, 53.801), (-113.851, 54.152), (-114.03, 55.165), (-114.770, 55.285), (-116.486, 55.432), (-116.905, 55.710), (-117.627, 55.716), RYCROFT)
def anyleg(*pts):                                                       # between points that may be on spur-class track (the old main line about Rycroft)
    import networkx as nx
    ns = [net.near(fwd(*p))[0] for p in pts]; out = []
    for u, v in zip(ns, ns[1:]):
        p = nx.shortest_path(net.G, u, v, weight='w'); out += p if not out else p[1:]
    return out
a = a[:-1] + anyleg(inv(*a[-1]), RYCROFT)[1:] if math.dist(a[-1], fwd(*RYCROFT)) > 30 else a
b = anyleg(RYCROFT, SPIRIT_RIVER)
d1, s2 = leg(net, RYCROFT, (-118.780, 55.349), (-118.795, 55.172), (-119.556, 55.331), BORDER, start_any=True)
est = [fwd(*p) for p in kml('nar_dawson_creek_gap.kml')[0]][1:]          # Brendan's trace across the gap in B.C.: the boundary to the Dawson Creek yard
d2 = leg(Net(json.load(open(os.path.join(HERE, 'nrwn', 'dawson.json')))), DC_YARD_EAST, DAWSON_CREEK)[0]
L = lambda p: LineString(p).length
_j0 = math.dist(d1[-1], fwd(*kml('nar_dawson_creek_gap.kml')[0][0]))
la, lb, ld1, lest, ld2 = L(a), L(b), L(d1), L([d1[-1]] + est), L(d2)
print(f'  Edmonton-Rycroft {la / MI:.1f} mi (printed 357.0); Spirit River spur {lb / MI:.1f} (printed 5.2); Rycroft-boundary {ld1 / MI:.1f}; '
      f'boundary-Dawson Creek yard {lest / MI:.1f} (trace; joins {_j0:.0f} m and {math.dist(est[-1], d2[0]):.0f} m) + {ld2 / MI:.1f} in the yard (printed Rycroft-Dawson Creek 138.2); snaps {[round(x) for x in s1 + s2]}')
pts = a + b[1:] + b[::-1][1:] + d1[1:] + est + d2[1:]
RT = LineString([p for k, p in enumerate(pts) if k == 0 or math.dist(p, pts[k - 1]) > 0.5])
# stations: route order, with the distance run so far as printed (the spur counted out and back)
rows = list(csv.DictReader(l for l in open(os.path.join(HERE, 'nar_1948_04.csv')) if not l.startswith('#')))
run = []; seen_spur = False
for r in rows:
    m = float(r['mile'])
    if r['station'] == 'Spirit River': seen_spur = True
    run.append(m + (2 * (362.2 - m) if seen_spur and r['station'] == 'Rycroft' else 0) if not (seen_spur and m != 357.0 and r['station'] != 'Spirit River') else m + 10.4)
m_border = 367.4 + ld1 / MI                                             # the boundary, by the traced distance from Rycroft
FIX = [(0.0, 0.0), (357.0, la), (362.2, la + lb), (367.4, la + 2 * lb), (m_border, la + 2 * lb + ld1), (495.2 + 10.4, RT.length)]
def chain(x): return float(np.interp(x, [f[0] for f in FIX], [f[1] for f in FIX]))
def times(txt):
    arr = dep = None
    for m in re.finditer(r'(ar|lv)?\s*f?(\d+)\.(\d+)([ap])', txt):
        t = (int(m.group(2)) % 12 + (12 if m.group(4) == 'p' else 0)) * 3600 + int(m.group(3)) * 60 - 3600       # Mountain -> Pacific
        if m.group(1) == 'ar': arr = t
        elif m.group(1) == 'lv': dep = t
        else: arr = dep = t
    return (arr if arr is not None else dep), (dep if dep is not None else arr)
NOTE = {'Edmonton': 'Edmonton: the Canadian National station, which the Northern Alberta used, reached by the downtown loop', 'Dunvegan Yards': "the Northern Alberta's own yards and shops, Edmonton",
        'McLennan': 'divisional point; junction for the Peace River line (not shown)', 'Rycroft': 'junction: the train runs out to Spirit River and back, calling here twice',
        'Spirit River': 'end of the spur from Rycroft', 'Tupper': 'station, British Columbia', 'Gundy': 'station, British Columbia', 'Pouce Coupe': 'station, British Columbia', 'Dawson Creek': 'Dawson Creek, B.C.: the end of steel, reached from Alberta. The PGE did not arrive until 1958'}
stations = []
for r, x in zip(rows, run):
    n = r['station']; d = chain(x); lon, lat = inv(*RT.interpolate(d).coords[0])
    stations.append(dict(name=n, d=d, lon=round(lon, 6), lat=round(lat, 6), mile=float(r['mile']), principal=r['principal'] == '1', gid='CN_EDMONTON' if n == 'Edmonton' else 'NAR_' + re.sub(r'\W+', '_', n.upper()).strip('_'),   # Edmonton: the CN's station
                         note='Northern Alberta Railways: ' + NOTE.get(n, 'flag stop' if r['No2'].startswith('f') and r['No1'].startswith('f') else 'station')))
    if r['principal'] == '1' or float(r['mile']) > 470: print(f"  {n:15s} mile {r['mile']:>6s}  {lat:.4f}, {lon:.4f}")
trips = []
for col, num, d, note in (('No1', '1', 0, 'Edmonton to Dawson Creek, leaving Edmonton daily except Sunday and arriving the next afternoon. First-class coaches and a standard sleeper; cafe car between Edmonton and Dimsdale.'),
                          ('No2', '2', 1, 'Dawson Creek to Edmonton, leaving Dawson Creek daily except Sunday and arriving the next morning. First-class coaches and a standard sleeper; cafe car between Dimsdale and Edmonton.')):
    stops = [[i, *times(r[col]), 1] for i, r in enumerate(rows)]
    if d == 1: stops.reverse()
    base, prev = 0, -1
    for s in stops:
        for k in (1, 2):
            if s[k] + base < prev - 6 * 3600: base += 86400
            s[k] += base; prev = s[k]
    assert stops[0][1] >= 0
    for (i, _, da, _), (j, tb, _, _) in zip(stops, stops[1:]):
        mph = abs(stations[j]['d'] - stations[i]['d']) / MI / max((tb - da) / 3600, 1e-9)
        if not 8 < mph < 45: print(f"  !! No. {num} {stations[i]['name']} -> {stations[j]['name']} {mph:.1f} mph")
    trips.append(dict(id='NAR-' + num, num=num, name='', svc='NAR_XSUN', dir=d, stops=stops, note=note + ' The table is in Mountain time; shown here in Pacific time, an hour earlier.'))
    f = lambda x: f'{x // 3600 % 24:02d}:{x % 3600 // 60:02d}'
    print(f"  No. {num}: {stations[stops[0][0]]['name']} {f(stops[0][2])} to {stations[stops[-1][0]]['name']} {f(stops[-1][1])} (+{stops[-1][1] // 86400} day), {len(stops)} stops")
route = []; acc = 0.0; prev = None
for xy in RT.simplify(2.0).coords:
    if prev: acc += math.dist(xy, prev)
    prev = xy; lon, lat = inv(*xy); route.append([round(lon, 6), round(lat, 6), round(acc, 1)])
sc = acc / RT.length
st = [dict(name=s['name'], chain=round(s['d'] * sc, 1), lon=s['lon'], lat=s['lat'], mile=s['mile'], principal=s['principal'], note=s['note'], kml='', gid=s['gid']) for s in stations]
vd = json.load(open(os.path.join(HERE, 'viz_data.json')))
_cn = LineString([fwd(p[0], p[1]) for p in next(l for l in vd['lines'] if l['key'] == 'cn')['route']])
shared = next((d for d in np.arange(0, 12 * MI, 25.0) if _cn.distance(RT.interpolate(d)) > 15), 0.0)       # out of the CN station over the CN's own track
print(f'  shares the CN line for {shared / MI:.1f} mi out of the Edmonton station')
vd['lines'] = [x for x in vd['lines'] if x['key'] != 'nar'] + [dict(key='nar', kind='a', label='Northern Alberta Railways', mainline=True, owner='nar', route=route, stations=st,
    dirLabels=['to Grande Prairie and Dawson Creek', 'to Edmonton'], segments=[dict(owner='none', a=0.0, b=round(float(shared) * sc, 1))] if shared else [], trips=trips, src='Northern Alberta Railways, from the Official Guide, May 1948')]
open(os.path.join(HERE, 'viz_data.json'), 'w').write(json.dumps(vd, separators=(',', ':')))
def fmt(x): return f'{x // 3600:02d}:{x % 3600 // 60:02d}:{x % 60:02d}'
def app(name, rows_):
    with open(os.path.join(GT, name), 'a', newline='') as fh: csv.writer(fh).writerows(rows_)
app('agency.txt', [['NAR', 'Northern Alberta Railways', 'https://en.wikipedia.org/wiki/Northern_Alberta_Railways', 'America/Vancouver', 'en', '']])
app('calendar.txt', [['NAR_XSUN', 1, 1, 1, 1, 1, 1, 0, '19490616', '19491231']])
app('routes.txt', [['NAR', 'NAR', 'Northern Alberta', 'Edmonton – McLennan – Rycroft – Spirit River – Grande Prairie – Dawson Creek', 2, '2C4F86', 'FFFFFF',
                    'Table of April 25, 1948 (Official Guide, May 1948). Pacific time, an hour earlier than the Mountain time printed. ']])
seen = set(r[0] for r in csv.reader(open(os.path.join(GT, 'stops.txt'))))        # Edmonton is the CN's stop, already in the feed
app('stops.txt', [[s['gid'], s['name'] + ' (NAR)', f"{s['lat']:.6f}", f"{s['lon']:.6f}", s['note']] for s in st if not (s['gid'] in seen or seen.add(s['gid']))])
for sid, coords in (('NAR_OUT', list(RT.coords)), ('NAR_IN', list(RT.coords)[::-1])):
    a_, p, shp = 0.0, None, []
    for k, xy in enumerate(coords):
        if p: a_ += math.dist(p, xy)
        p = xy; lon, lat = inv(*xy); shp.append([sid, f'{lat:.6f}', f'{lon:.6f}', k, f'{a_:.1f}'])
    app('shapes.txt', shp)
app('trips.txt', [['NAR', t['svc'], t['id'], st[t['stops'][-1][0]]['name'], 'No. ' + t['num'], t['dir'], 'NAR_OUT' if t['dir'] == 0 else 'NAR_IN'] for t in trips])
app('stop_times.txt', [[t['id'], fmt(a_), fmt(b_), st[i]['gid'], k, f"{(stations[i]['d'] if t['dir'] == 0 else RT.length - stations[i]['d']):.1f}", 1] for t in trips for k, (i, a_, b_, tp) in enumerate(t['stops'], 1)])
print(f'nar: {RT.length / MI:.1f} mi of route (the spur twice), {len(st)} calls, {len(trips)} trips')
