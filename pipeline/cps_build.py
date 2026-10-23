"""CP Sicamous - Armstrong - Vernon - Kelowna (Table 157, 1948): mixed trains M708 / M707, daily except Sunday.
Track: Sicamous - Armstrong from Brendan's export (sicamous_armstrong.tsv, the 'Kalamalka' subdivision); Armstrong - Kelowna shares the
Okanagan line already on the map (cno), marked owner 'none' here so it is drawn once. Run after kv_through.py."""
import csv, json, math, os, re, zipfile
from shapely import wkt
from shapely.geometry import LineString, Point
from shapely.ops import linemerge, unary_union
from nrwn_graph import fwd, inv, MI
HERE = os.path.dirname(os.path.abspath(__file__)); GT = os.path.join(HERE, 'gtfs')
csv.field_size_limit(10 ** 9)
rows = list(csv.DictReader(open(os.path.join(HERE, 'sicamous_armstrong.tsv')), delimiter='\t'))
SA = linemerge(unary_union([wkt.loads(r['wkt_geom']) for r in rows if r['TRACKS'] == '1']))
c = list(SA.coords)
if c[0][1] < c[-1][1]: c = c[::-1]                                     # Sicamous (north) first
SA_xy = LineString([fwd(*p[:2]) for p in c])
print(f'Sicamous-Armstrong trace {SA_xy.length/MI:.1f} mi (timetable 31.8)')

vd = json.load(open(os.path.join(HERE, 'viz_data.json')))
L = {l['key']: l for l in vd['lines']}
cno, cp = L['cno'], L['cp']
arm = next(s for s in cno['stations'] if s['name'] == 'Armstrong')
okan = [p for p in cno['route'] if p[2] >= arm['chain']]                 # Armstrong -> Kelowna, viz coordinates
route = []; acc = 0.0; prev = None
for xy in SA_xy.simplify(2.0).coords:
    if prev: acc += math.dist(xy, prev)
    prev = xy; lon, lat = inv(*xy); route.append([round(lon, 6), round(lat, 6), round(acc, 1)])
join = acc
for p in okan: route.append([p[0], p[1], round(join + p[2] - arm['chain'], 1)])
sc = acc / SA_xy.length

T157 = """mile,station,M708,M707
0.0,Sicamous,lv 10.15a,ar 7.45p
12.6,Mara,10.45a,7.10p
17.3,Grindrod,10.56a,6.58p
23.0,Enderby,11.10a,6.42p
26.8,Stepney,f11.19a,f6.33p
31.8,Armstrong,11.32a,6.20p
34.2,Realm,f11.41a,f6.10p
38.2,Larkin,f11.52a,f6.00p
46.2,Vernon,ar 12.15p / lv 12.45p,ar 5.15p / lv 5.40p
48.4,Lumby Jct,f12.50p,f5.05p
53.1,Kalamalka,f1.06p,f4.50p
60.0,Oyama,1.22p,4.30p
66.7,Winfield,f1.42p,f4.16p
70.2,Postill,f1.51p,f4.08p
73.8,Rutland,f2.00p,f4.00p
79.7,Kelowna,ar 2.15p,lv 3.45p
"""
open(os.path.join(HERE, 'cp_1948_table157.csv'), 'w').write('# CP Table 157 (1948), Sicamous - Vernon - Kelowna. M708 read down, M707 read up; daily except Sunday. f = flag stop.\n' + T157)
t = list(csv.DictReader(T157.splitlines()))
cno_by = {s['name']: s for s in cno['stations']}
stations = []
for r in t:
    n, m = r['station'], float(r['mile'])
    if m <= 31.8:                                                        # on the trace: printed mileage scaled to the traced length
        ch = (m / 31.8) * SA_xy.length * sc
        lon, lat = inv(*SA_xy.interpolate(m / 31.8 * SA_xy.length).coords[0])
        gid = 'CP_SICAMOUS' if n == 'Sicamous' else 'CPS_' + n.upper()
        if n == 'Armstrong': gid, (lon, lat) = arm['gid'], (arm['lon'], arm['lat'])
    else:                                                                # on the shared Okanagan line: reuse its station
        s = cno_by[n]; ch = join + s['chain'] - arm['chain']; gid, lon, lat = s['gid'], s['lon'], s['lat']
    stations.append(dict(name=n, chain=round(ch, 1), lon=round(lon, 6), lat=round(lat, 6), mile=m, principal=n in {'Sicamous', 'Enderby', 'Armstrong', 'Vernon', 'Kelowna'},
                         note='Canadian Pacific station' + (' (Shuswap & Okanagan)' if m <= 31.8 else ' (shared with Canadian National)'), kml='', gid=gid))
def times(txt):
    arr = dep = None
    for mm in re.finditer(r'(ar|lv)?\s*f?(\d+)\.(\d+)([ap])', txt):
        h, mn = int(mm.group(2)), int(mm.group(3))
        if mm.group(4) == 'p' and h != 12: h += 12
        if mm.group(4) == 'a' and h == 12: h = 0
        x = h * 3600 + mn * 60
        if mm.group(1) == 'ar': arr = x
        elif mm.group(1) == 'lv': dep = x
        else: arr = dep = x
    return (arr if arr is not None else dep), (dep if dep is not None else arr)
trips = []
for col, d, note in (('M708', 0, 'Mixed train, Sicamous (connecting with the CP main line) to Vernon and Kelowna; Greyhound buses on to Penticton.'),
                     ('M707', 1, 'Mixed train, Kelowna and Vernon to Sicamous, connecting with the CP main line.')):
    rs = sorted(range(len(t)), reverse=(d == 1))
    trips.append(dict(id='CPS-' + col, num=col, name='Mixed', svc='CP_XSUN', dir=d, note=note, stops=[[i, *times(t[i][col]), 1] for i in rs]))
for tr in trips:
    for (a, _, da, _), (b, tb, _, _) in zip(tr['stops'], tr['stops'][1:]):
        dist = abs(stations[b]['chain'] - stations[a]['chain']) / MI; mins = (tb - da) / 60
        if mins <= 0 or dist / (mins / 60) > 50: print('  !!', tr['id'], stations[a]['name'], stations[b]['name'], round(dist, 1), mins)
line = dict(key='cps', kind='p', label='Canadian Pacific', mainline=True, owner='cp', route=route, stations=stations,
            dirLabels=['to Vernon and Kelowna', 'to Sicamous'], segments=[dict(owner='none', a=round(join, 1), b=route[-1][2])], trips=trips)
vd['lines'] = [x for x in vd['lines'] if x['key'] != 'cps'] + [line]
open(os.path.join(HERE, 'viz_data.json'), 'w').write(json.dumps(vd, separators=(',', ':')))

def fmt(x): return f'{x // 3600:02d}:{x % 3600 // 60:02d}:{x % 60:02d}'
def app(name, rows_):
    with open(os.path.join(GT, name), 'a', newline='') as fh: csv.writer(fh).writerows(rows_)
seen = set(r[0] for r in csv.reader(open(os.path.join(GT, 'stops.txt'))))
app('routes.txt', [['CPS', 'CP', 'CP Okanagan', 'Sicamous – Vernon – Kelowna', 2, '7A1E2C', 'FFFFFF', 'CP Table 157, 1948.']])
app('stops.txt', [[s['gid'], s['name'] + ' (CP)', f"{s['lat']:.6f}", f"{s['lon']:.6f}", s['note']] for s in stations if s['gid'] not in seen])
shp = []
for sid, pts in (('CPS_OUT', route), ('CPS_IN', route[::-1])):
    tot = route[-1][2]
    for k, p in enumerate(pts): shp.append([sid, f'{p[1]:.6f}', f'{p[0]:.6f}', k, f"{(p[2] if sid == 'CPS_OUT' else tot - p[2]):.1f}"])
app('shapes.txt', shp)
app('trips.txt', [['CPS', tr['svc'], tr['id'], stations[tr['stops'][-1][0]]['name'], f"{tr['num']} Mixed", tr['dir'], 'CPS_OUT' if tr['dir'] == 0 else 'CPS_IN'] for tr in trips])
app('stop_times.txt', [[tr['id'], fmt(a), fmt(b), stations[i]['gid'], k, f"{(stations[i]['chain'] if tr['dir'] == 0 else route[-1][2] - stations[i]['chain']):.1f}", 1]
                       for tr in trips for k, (i, a, b, tp) in enumerate(tr['stops'], 1)])
with zipfile.ZipFile(os.path.join(HERE, 'bcer_fraser_valley_1949_gtfs.zip'), 'w', zipfile.ZIP_DEFLATED) as z:
    for fn in sorted(os.listdir(GT)): z.write(os.path.join(GT, fn), fn)
print('cps', len(stations), 'stations', len(trips), 'trips; Sicamous at', stations[0]['lat'], stations[0]['lon'])
