"""Spokane International Railroad, Yahk - Kingsgate - Bonners Ferry - Sand Point - Spokane: trains No. 1 and No. 2 from the S.I.'s own timetable of
October 1947 (si_1947_10.csv, Brendan's scan), every station and flag stop. (The first build used the condensed version in CP Table 151, 1948.)
Track: Canadian Pacific from Yahk to the border at Kingsgate (NRWN, south.json), then Brendan's Spokane International trace
(traces/spokane_international.kml) from Eastport, Idaho, through Sand Point to Spokane. Drawn as CP track to the border and as S.I. track beyond;
the first miles out of Yahk are the Crowsnest main line, already drawn by the cr line (read from viz_data.json: needs cp_south_build).
Stations at printed mileage (from Yahk), fixed at Yahk, the border and the two branch junctions."""
import csv, json, math, os, re
import xml.etree.ElementTree as ET
import numpy as np
from shapely.geometry import Point, LineString
from shapely.ops import substring
from nrwn_graph import Net, fwd, inv, MI
HERE = os.path.dirname(os.path.abspath(__file__)); GT = os.path.join(HERE, 'gtfs')
net = Net(json.load(open(os.path.join(HERE, 'nrwn', 'south.json'))))
CP, snaps = net.route((-116.088, 49.088), (-116.181, 49.001))                     # Yahk to Kingsgate
NS = '{http://www.opengis.net/kml/2.2}'; K = {}
for pm in ET.parse(os.path.join(HERE, 'traces', 'spokane_international.kml')).iter(NS + 'Placemark'):
    c = pm.find('.//' + NS + 'coordinates')
    if c is not None: K[pm.find(NS + 'name').text] = [fwd(*map(float, t.split(',')[:2])) for t in c.text.split()]
pts = list(CP.coords)
for name in ('Sandpoint ID to Eastport ID', 'Sandpoint abandoned', 'WA/ID State Line to Sandpoint ID', 'Spokane WA to WA/ID State Line'):   # each drawn towards the border: reversed
    piece = K[name][::-1]
    if name.startswith('WA/ID'):          # this piece runs a little past the junction with the old line through Sand Point: start it there
        L_ = LineString(K[name]); piece = list(substring(L_, 0, L_.project(Point(pts[-1]))).coords)[::-1]
    print(f'  join to {name!r}: {math.dist(pts[-1], piece[0]):.0f} m'); pts += piece
# into Spokane Union Station (Brendan, 9 October 2026): from the end of his trace, east of downtown, over the Union Pacific's track (wa_lines)
import networkx as nx, wa_lines
_G = wa_lines._graph({'up'})()[0]
def _nn(p): return min(_G.nodes, key=lambda q: math.dist(q, p))
_in = nx.shortest_path(_G, _nn(pts[-1]), _nn(fwd(*wa_lines.SPK_US)), weight='len')
print(f'  into Spokane Union Station over UP track: {nx.path_weight(_G, _in, "len") / MI:.2f} mi')
pts += [p for p in _in] + [fwd(*wa_lines.SPK_US)]
RT = LineString([p for k, p in enumerate(pts) if k == 0 or math.dist(p, pts[k - 1]) > 0.5])
_si_end = RT.project(Point(_in[0]))                                     # where the S.I.'s own track ends and the UP's begins
rows = list(csv.DictReader(l for l in open(os.path.join(HERE, 'si_1947_10.csv')) if not l.startswith('#')))
# fixed points: Yahk, the border, and the two junctions where Brendan's branch traces leave the main line. Traced and printed miles agree to within
# half a mile from the border to Coeur d'Alene Junction; with the UP track from the trace's end into Union Station the line is the 25.5 printed on
# to Spokane, so stations beyond the junction go by their printed miles.
_cor = RT.project(Point(K['Corbin Jct to Bayview ID'][0])); _cda = RT.project(Point(K["Coeur d'Alene Jct to Coeur d'Alene ID"][0]))
FIX = [(0.0, 0.0), (10.5, CP.length), (112.4, _cor), (125.8, _cda), (float(rows[-1]['mile']), RT.length)]
print(f'si: Yahk-Kingsgate {CP.length / MI:.1f} mi traced (printed 10.5), Kingsgate-Spokane {(RT.length - CP.length) / MI:.1f} (printed 140.8); snaps {[round(s) for s in snaps]}')
def chain(m): return float(np.interp(m, [f[0] for f in FIX], [f[1] for f in FIX]))
def times(txt):
    arr = dep = None
    for m in re.finditer(r'(ar|lv)?\s*f?(\d+)\.(\d+)([ap])', txt):
        t = (int(m.group(2)) % 12 + (12 if m.group(4) == 'p' else 0)) * 3600 + int(m.group(3)) * 60
        if m.group(1) == 'ar': arr = t
        elif m.group(1) == 'lv': dep = t
        else: arr = dep = t
    return (arr if arr is not None else dep), (dep if dep is not None else arr)
NOTE = {'Yahk': 'Canadian Pacific station; the Spokane International leaves the Crowsnest line just west of here (Curzon)', 'Glenlily': 'Canadian Pacific flag stop (times from CP Table 151)',
        'Kingsgate': 'the border: Kingsgate, B.C., and Eastport, Idaho, at the same mile. Customs stop, twenty minutes',
        'Sand Point': 'Spokane International station, Idaho (Sandpoint), on the old line through the town. Connections with the Northern Pacific and the Great Northern',
        'Bonners Ferry': 'Spokane International station, Idaho. Connection with the Great Northern',
        "Coeur d'Alene Junction": "Spokane International station, Idaho; junction for the branch to Coeur d'Alene",
        'Spokane': 'Spokane Union Station, Washington (with the Union Pacific and the Milwaukee Road)'}
stations = []
for r in rows:
    n = r['station']; d = chain(float(r['mile'])); lon, lat = inv(*RT.interpolate(d).coords[0])
    stations.append(dict(name=n, d=d, lon=round(lon, 6), lat=round(lat, 6), mile=float(r['mile']), principal=r['bold'] == '1',
                         gid='CR_YAHK' if n == 'Yahk' else 'WA_SPOKANE_UNION_STATION' if n == 'Spokane' else 'SI_' + re.sub(r'\W+', '_', n.upper()).strip('_'),
                         note=NOTE.get(n, 'Spokane International ' + ('station' if not r['No1'].startswith('f') else 'flag stop') + (', Washington' if float(r['mile']) > 132 else ', Idaho'))))
    if r['bold'] == '1': print(f"  {n:22s} mile {r['mile']:>6s}  {lat:.4f}, {lon:.4f}")
TRAINS = [('No1', 'S.I. 1', 0, 'Spokane International No. 1, Yahk to Spokane, daily. It leaves Yahk ten minutes after No. 11 arrives from Lethbridge and Cranbrook, and stands twenty minutes at the border.'),
          ('No2', 'S.I. 2', 1, 'Spokane International No. 2, Spokane to Yahk, daily, leaving Spokane at 11.59 the night before. At Yahk it connects with the mixed train to Cranbrook and with No. 11 for Nelson and Vancouver.')]
trips = []
for col, num, d, note in TRAINS:
    stops = [[i, *times(r[col]), 1] for i, r in enumerate(rows) if r.get(col)]
    if d == 1: stops.reverse()
    base, prev = 0, -1
    for s in stops:                                                               # past midnight: keep the clock running
        for k in (1, 2):
            if s[k] + base < prev - 6 * 3600: base += 86400
            s[k] += base; prev = s[k]
    trips.append(dict(id='SI-SI' + col[-1], num=num, name='Spokane International', svc='CP_DAILY', dir=d, stops=stops, note=note))
    for (a, _, da, _), (b, tb, _, _) in zip(stops, stops[1:]):
        mph = abs(stations[b]['d'] - stations[a]['d']) / MI / ((tb - da) / 3600)
        if not 8 < mph < 50: print(f"  !! {num} {stations[a]['name']} -> {stations[b]['name']} {mph:.1f} mph")
    print(f"  {num}: {len(stops)} stops, {stations[stops[0][0]]['name']} {stops[0][2] // 3600:02d}:{stops[0][2] % 3600 // 60:02d} to {stations[stops[-1][0]]['name']} {stops[-1][1] // 3600 % 24:02d}:{stops[-1][1] % 3600 // 60:02d}")
vd = json.load(open(os.path.join(HERE, 'viz_data.json')))
cr = LineString([fwd(p[0], p[1]) for p in next(l for l in vd['lines'] if l['key'] == 'cr')['route']])
shared = next((d for d in np.arange(0, CP.length, 25.0) if cr.distance(RT.interpolate(d)) > 15), 0.0)
print(f'  S.I. trains share the main line for {shared / MI:.1f} mi out of Yahk (Curzon)')
route = []; acc = 0.0; prev = None
for xy in RT.simplify(2.0).coords:
    if prev: acc += math.dist(xy, prev)
    prev = xy; lon, lat = inv(*xy); route.append([round(lon, 6), round(lat, 6), round(acc, 1)])
sc = acc / RT.length
st = [dict(name=s['name'], chain=round(s['d'] * sc, 1), lon=s['lon'], lat=s['lat'], mile=s['mile'], principal=s['principal'], note=s['note'], kml='', gid=s['gid']) for s in stations]
vd['lines'] = [x for x in vd['lines'] if x['key'] != 'si'] + [dict(key='si', kind='p', label='Spokane International', mainline=True, owner='cp', route=route, stations=st, livery='si',
    dirLabels=['to Kingsgate and Spokane', 'to Yahk'], trips=trips, src='Spokane International Railroad timetable, October 1947',
    segments=[dict(owner='none', a=0.0, b=round(float(shared) * sc, 1)), dict(owner='si', a=round(CP.length * sc, 1), b=round(_si_end * sc, 1)),
              dict(owner='up', a=round(_si_end * sc, 1), b=round(acc, 1))])]
open(os.path.join(HERE, 'viz_data.json'), 'w').write(json.dumps(vd, separators=(',', ':')))
def fmt(x): return f'{x // 3600:02d}:{x % 3600 // 60:02d}:{x % 60:02d}'
def app(name, rows_):
    with open(os.path.join(GT, name), 'a', newline='') as fh: csv.writer(fh).writerows(rows_)
have = set(r[0] for r in csv.reader(open(os.path.join(GT, 'stops.txt'))))
app('agency.txt', [['SI', 'Spokane International Railway', 'https://en.wikipedia.org/wiki/Spokane_International_Railroad', 'America/Vancouver', 'en', '']])
app('routes.txt', [['SIR', 'SI', 'Spokane International', 'Yahk – Kingsgate – Bonners Ferry – Sand Point – Spokane', 2, '9C1A12', 'FFFFFF', 'Spokane International timetable, October 1947. CP track to the border (National Railway Network), S.I. track beyond.']])
app('stops.txt', [[s['gid'], 'Spokane Union Station' if s['gid'] == 'WA_SPOKANE_UNION_STATION' else s['name'] + ' (S.I.)', f"{s['lat']:.6f}", f"{s['lon']:.6f}", s['note']] for s in st if s['gid'] not in have])
for sid, coords in (('SI_OUT', list(RT.coords)), ('SI_IN', list(RT.coords)[::-1])):
    a, p, shp = 0.0, None, []
    for k, xy in enumerate(coords):
        if p: a += math.dist(p, xy)
        p = xy; lon, lat = inv(*xy); shp.append([sid, f'{lat:.6f}', f'{lon:.6f}', k, f'{a:.1f}'])
    app('shapes.txt', shp)
app('trips.txt', [['SIR', t['svc'], t['id'], st[t['stops'][-1][0]]['name'], f"{t['num']} {t['name']}", t['dir'], 'SI_OUT' if t['dir'] == 0 else 'SI_IN'] for t in trips])
app('stop_times.txt', [[t['id'], fmt(a), fmt(b), st[i]['gid'], k, f"{(stations[i]['d'] if t['dir'] == 0 else RT.length - stations[i]['d']):.1f}", 1] for t in trips for k, (i, a, b, tp) in enumerate(t['stops'], 1)])
print(f'si: {RT.length / MI:.1f} mi, {len(st)} stations, {len(trips)} trips')
