"""Northern Navigation Co. (a Canada Steamship Lines subsidiary): the S.S. Noronic, Windsor - Detroit - Sarnia - Sault Ste. Marie - Port Arthur - Duluth,
one round trip a week through the summer (westbound from Windsor on Fridays, eastbound from Duluth on Tuesdays). Brendan, 3 November 2026.

Source: the timetable page Brendan supplied ("Midsummer, June 25 to September 3" westbound, "June 29 to September 7" eastbound; the year is not printed, the
weekdays are those of 1948), printed in Eastern Standard Time except Duluth (Central). Transcribed in noronic_1948_notes.txt. The map has one Pacific clock,
so every time is shown three hours earlier than the Eastern time printed (Duluth: the Central time printed, plus an hour to Eastern, less three).
Ports: traces/lakes/northern_navigation_co.kmz (Brendan's points). The Detroit call is the Grand Trunk wharf = the CN Windsor - Detroit car ferry slip
(gid CN_DETROIT_FERRY_SLIP, from on_build): one station for the Noronic and the ferry trains.
A separate step (not part of boats_build.py) so that boats_build and its lane cache stay as they were: the Great Lakes water (water_east.json, drawn
only until now) is added to the lane mask here. Run after on_build."""
import csv, json, math, os, re, zipfile
import xml.etree.ElementTree as ET
from shapely.geometry import MultiPolygon, Polygon
from nrwn_graph import fwd, MI
import sea
from sea import Sea, SEA_VERSION
HERE = os.path.dirname(os.path.abspath(__file__)); GT = os.path.join(HERE, 'gtfs')
vd = json.load(open(os.path.join(HERE, 'viz_data.json')))
RAIL = {s['gid']: s for l in vd['lines'] for s in l['stations'] if s.get('gid') and not l.get('water')}

# ---------------- the Great Lakes water for the lanes (water_east.json: the page's format, rings delta-encoded in 1e-4 degrees)
def _east(fn):
    out = []
    for poly in json.load(open(fn)):
        rings = []
        for r in poly:
            lon, lat = r[0], r[1]; pts = [sea.to_xy(lon / 1e4, lat / 1e4)]
            for i in range(2, len(r), 2): lon += r[i]; lat += r[i + 1]; pts.append(sea.to_xy(lon / 1e4, lat / 1e4))
            rings.append(pts)
        out.append(Polygon(rings[0], rings[1:]))
    return out
sea._U = MultiPolygon(list(sea.water().geoms) + _east(os.path.join(HERE, 'water_east.json')))     # the other layers have no water in the Great Lakes, so nothing is painted twice

# ---------------- ports: Brendan's points
_ns = {'k': 'http://www.opengis.net/kml/2.2'}
_z = zipfile.ZipFile(os.path.join(HERE, 'traces', 'lakes', 'northern_navigation_co.kmz'))
KMZ = {}
for pm in ET.fromstring(_z.read('doc.kml')).iter('{http://www.opengis.net/kml/2.2}Placemark'):
    nm = pm.find('k:name', _ns).text.strip(); c = pm.find('k:Point/k:coordinates', _ns).text.strip().split(',')
    KMZ[nm] = (float(c[0]), float(c[1]))
DETROIT = 'Detroit Ferry Slip'; _slip = RAIL['CN_DETROIT_FERRY_SLIP']
assert math.dist(fwd(*KMZ['Detroit Wharf']), fwd(_slip['lon'], _slip['lat'])) < 10, 'Brendan: the Detroit wharf is the CN ferry slip'
PORTS = [('Windsor (Government Dock)', KMZ['Windsor (Government Dock)'], 'Government Dock, Windsor (Brendan)'),
         (DETROIT, 'CN_DETROIT_FERRY_SLIP', "Grand Trunk Railway wharf, Detroit: the CN Windsor - Detroit car ferry slip (Brendan)"),
         ('Sarnia (Point Edward)', KMZ['Sarnia'], 'Sarnia, "Pt. Edward" in the timetable (Brendan)'),
         ('Sault Ste. Marie (C.S.L. Dock)', KMZ['Sault Ste. Marie (C.S.L. Dock)'], 'Canada Steamship Lines dock, Sault Ste. Marie, Ont.; also known as the Government Dock or the Northern Navigation Dock (Brendan)'),
         ('Port Arthur (C.N.R. Dock)', KMZ['Port Arthur (C.N.R. Dock)'], 'Canadian National Railways dock, Port Arthur (Brendan)'),
         ('Duluth (Northern Pacific Dock No. 4)', KMZ['Duluth (Northern Pacific Dock No. 4)'], 'Northern Pacific dock no. 4, Duluth (Brendan)')]
def port(n, v, note):
    if isinstance(v, str): r = RAIL[v]; return dict(name=n, gid=v, lon=r['lon'], lat=r['lat'], rail=True, note=note)
    return dict(name=n, gid='PORT_' + re.sub(r'\W+', '_', n.upper()).strip('_'), lon=v[0], lat=v[1], rail=False, note=note)
ports = [port(*p) for p in PORTS]

# ---------------- lanes (cache: nn_legs.json). The short river legs need a fine grid, the long lake legs a coarse one.
RES = {(0, 1): 60, (1, 2): 100, (2, 3): 250, (3, 4): 250, (4, 5): 250}
_CF = os.path.join(HERE, 'nn_legs.json'); CACHE = json.load(open(_CF)) if os.path.exists(_CF) else {}
# Waypoints on the open lake (Brendan's rule: lanes on the water layer, not surveyed courses). The least-cost raster path bends 45 degrees and cuts the Keweenaw tip
# on the long crossing, so Port Arthur - Sault Ste. Marie is steered past Passage Island (north end of Isle Royale, which the layer lacks) and across the middle of the lake.
VIA = {(3, 4): [(-85.00, 46.93), (-86.35, 47.35), (-88.15, 48.33)]}                      # listed from Sault Ste. Marie towards Port Arthur
def lane(k):
    a, b = ports[k], ports[k + 1]; res = RES[(k, k + 1)]
    seq = [(a['lon'], a['lat'])] + VIA.get((k, k + 1), []) + [(b['lon'], b['lat'])]; out = []
    for p, q in zip(seq, seq[1:]):
        ck = f'{SEA_VERSION}|{p[0]:.4f},{p[1]:.4f}|{q[0]:.4f},{q[1]:.4f}|{res}'
        if ck not in CACHE:
            d = math.dist(fwd(*p), fwd(*q)); S = Sea([p, q], res=res, margin=max(8000.0, 0.3 * d)); leg, land = S.leg(p, q)
            if land > 0.02:
                S2 = Sea([p, q], res=res, margin=max(30000.0, 1.2 * d)); leg2, land2 = S2.leg(p, q)
                if land2 < land: S, leg, land = S2, leg2, land2
            CACHE[ck] = [[round(x, 6), round(y, 6)] for x, y in leg]
            print(f"   {a['name']} - {b['name']} ({p[0]:.2f},{p[1]:.2f} to {q[0]:.2f},{q[1]:.2f}): lane over {land * 100:.1f}% land; snaps {S.snap_m(p):.0f} / {S.snap_m(q):.0f} m")
        leg = [tuple(x) for x in CACHE[ck]]; out += leg if not out else leg[1:]
    return out
pts, at = [], []
for k, p in enumerate(ports):
    if k == 0: pts.append((p['lon'], p['lat'])) if p['rail'] else None
    else: pts += lane(k - 1) + ([(p['lon'], p['lat'])] if p['rail'] else [])            # a lane runs up to a railway station; other ports sit on the lane (as in boats_build)
    if k == 0 and not p['rail']: pts.append(lane(0)[0])
    at.append(len(pts) - 1)
json.dump(CACHE, open(_CF, 'w'))
route = []; acc = 0.0; prev = None
for lon, lat in pts:
    xy = fwd(lon, lat)
    if prev: acc += math.dist(xy, prev)
    prev = xy; route.append([round(lon, 6), round(lat, 6), round(acc, 1)])
stations = [dict(name=p['name'], chain=route[i][2], lon=route[i][0], lat=route[i][1], mile=round(route[i][2] / MI, 1), lmile=round(route[i][2] / MI, 1), principal=True, kml='', gid=p['gid'],
                 **({} if p['rail'] else {'xy': [p['lon'], p['lat']]}), note=p['note']) for p, i in zip(ports, at)]

# ---------------- times: Eastern Standard Time as printed (Duluth: Central, + 1 h), shown on the Pacific clock (- 3 h)
D0, D1, D2, D3, D4 = (n * 86400 for n in range(5)); OFF = 3 * 3600
def hm(txt):
    m = re.match(r'(\d+)\.(\d+)([ap])', txt); h, mn = int(m.group(1)), int(m.group(2))
    if m.group(3) == 'p' and h != 12: h += 12
    if m.group(3) == 'a' and h == 12: h = 0
    return h * 3600 + mn * 60
E = lambda t, day=0: hm(t) + day                    # Eastern, as printed
C = lambda t, day=0: hm(t) + day + 3600             # Central, as printed (Duluth) -> Eastern
# (port index, arrival, departure, printed?): Detroit has one side printed, the other estimated, so it is shown "est."
WEST = [(0, E('9.30p'), E('9.30p'), 1), (1, E('9.50p'), E('11.00p'), 0), (2, E('6.45a', D1), E('4.30p', D1), 1), (3, E('9.45a', D2), E('12.00p', D2), 1),
        (4, E('6.30a', D3), E('6.30p', D3), 1), (5, C('7.30a', D4), C('7.30a', D4), 1)]
EAST = [(5, C('4.30p'), C('4.30p'), 1), (4, E('7.00a', D1), E('1.00p', D1), 1), (3, E('8.30a', D2), E('10.30a', D2), 1), (2, E('6.30a', D3), E('11.00a', D3), 1),
        (1, E('3.30p', D3), E('4.30p', D3), 0), (0, E('4.45p', D3), E('4.45p', D3), 1)]
_nn = (' Northern Navigation Co. (Canada Steamship Lines), midsummer schedule: westbound from Windsor Fridays June 25 - Sept. 3, eastbound from Duluth Tuesdays June 29 - Sept. 7;'
       ' one round trip a week. Times printed in Eastern Standard Time (Duluth in Central) and shown here in Pacific time, three hours earlier. The Detroit call is printed on one side only'
       ' (westbound leaving 11.00 p.m., eastbound arriving 3.30 p.m.): the other side is estimated.')
NOTE = {'W': 'S.S. Noronic, westbound: Windsor (Government Dock) Friday 9.30 p.m.; Detroit (Grand Trunk wharf) 11.00 p.m.; Sarnia (Pt. Edward) Saturday 6.45 a.m., leaving 4.30 p.m.; Sault Ste. Marie (C.S.L. dock) Sunday 9.45 a.m., leaving noon;'
               ' Port Arthur (C.N.R. dock) Monday 6.30 a.m., leaving 6.30 p.m.; Duluth (Northern Pacific dock no. 4) Tuesday 7.30 a.m., Central time.' + _nn,
        'E': 'S.S. Noronic, eastbound: Duluth (Northern Pacific dock no. 4) Tuesday 4.30 p.m., Central time; Port Arthur (C.N.R. dock) Wednesday 7.00 a.m., leaving 1.00 p.m.; Sault Ste. Marie (C.S.L. dock) Thursday 8.30 a.m., leaving 10.30 a.m.;'
               ' Sarnia (Pt. Edward) Friday 6.30 a.m., leaving 11.00 a.m.; Detroit (Grand Trunk wharf) 3.30 p.m.; Windsor (Government Dock) 4.45 p.m.' + _nn}
trips = []
for tid, svc, calls, d in (('W', 'W_0000100', WEST, 0), ('E', 'W_0100000', EAST, 1)):
    stops = [[i, int(round(a / 60.0)) * 60 - OFF, int(round(b / 60.0)) * 60 - OFF, pr] for i, a, b, pr in calls]
    assert stops[0][1] >= 0 and all(y[1] >= x[2] for x, y in zip(stops, stops[1:])), (tid, stops)
    run = abs(stations[calls[-1][0]]['chain'] - stations[calls[0][0]]['chain']) / MI; hrs = (stops[-1][1] - stops[0][2]) / 3600
    for (i, a, b, pr), (j, a2, b2, pr2) in zip(stops, stops[1:]):
        leg = abs(stations[j]['chain'] - stations[i]['chain']) / MI; h = (a2 - b) / 3600
        print(f"  NN-{tid} {stations[i]['name'][:22]:22s} - {stations[j]['name'][:22]:22s} {leg:6.1f} mi in {h:5.2f} h = {leg / h:5.1f} mph" + ('   !! check' if not 4 < leg / h < 21 and leg > 5 else ''))
    trips.append(dict(id=f'NN-{tid}', num='Noronic', name='Northern Navigation', svc=svc, dir=d, stops=stops, note=NOTE[tid], vessel='Noronic'))
    print(f'NN-{tid}: {run:.1f} mi in {hrs:.1f} h = {run / hrs:.1f} mph overall')
SRC = ('Northern Navigation Co. (Canada Steamship Lines), midsummer timetable from the May 1948 Official Guide, supplied by Brendan, 3 November 2026. Eastern Standard Time as printed, '
       'Duluth in Central, shown on the Pacific clock')
LINE = dict(key='nn', kind='v', label='Northern Navigation Co.', mainline=True, water=True, livery='csl', src=SRC, owner='cp', route=route, stations=stations,
            dirLabels=['to Duluth', 'to Windsor'], segments=[], trips=trips)
vd['lines'] = [x for x in vd['lines'] if x['key'] != 'nn'] + [LINE]
open(os.path.join(HERE, 'viz_data.json'), 'w').write(json.dumps(vd, separators=(',', ':')))
print(f"nn: Windsor - Duluth, {acc / MI:.1f} mi of lane, {len(stations)} calls, {len(trips)} sailings")

# ---------------- GTFS (route_type 4: ferry)
def fmt(x): return f'{x // 3600:02d}:{x % 3600 // 60:02d}:{x % 60:02d}'
def app(name, rows_):
    with open(os.path.join(GT, name), 'a', newline='') as fh: csv.writer(fh).writerows(rows_)
def have(name, col=0): return set(r[col] for r in csv.reader(open(os.path.join(GT, name))))
app('calendar.txt', [[w, *w[2:], '19490616', '19491231'] for w in sorted({t['svc'] for t in trips}) if w not in have('calendar.txt')])
if 'NNC' not in have('agency.txt'): app('agency.txt', [['NNC', 'Northern Navigation Company (Canada Steamship Lines)', 'https://en.wikipedia.org/wiki/SS_Noronic', 'America/Vancouver', 'en', '']])
app('routes.txt', [['NN', 'NNC', 'Windsor – Detroit – Sarnia – Sault Ste. Marie – Port Arthur – Duluth', ' – '.join(s['name'] for s in stations), 4, 'D93A1C', 'FFFFFF',
                    'S.S. Noronic, midsummer schedule. Steamer; the lane is a least-cost path over the water layer, not a surveyed course. Times on the Pacific clock, three hours earlier than the Eastern time printed.']])
gseen = have('stops.txt')
app('stops.txt', [[s['gid'], s['name'] + ' (steamer landing)', f"{s['lat']:.6f}", f"{s['lon']:.6f}", s['note']] for s in stations if s['gid'] not in gseen])
for t in trips:
    i0, i1 = t['stops'][0][0], t['stops'][-1][0]; lo, hi = sorted((stations[i0]['chain'], stations[i1]['chain']))
    pts_ = [p for p in route if lo - 0.5 <= p[2] <= hi + 0.5]
    if t['dir'] == 1: pts_ = pts_[::-1]
    app('shapes.txt', [[t['id'], f'{p[1]:.6f}', f'{p[0]:.6f}', k, f'{abs(p[2] - pts_[0][2]):.1f}'] for k, p in enumerate(pts_)])
    app('trips.txt', [['NN', t['svc'], t['id'], stations[i1]['name'], 'Noronic – ' + t['name'], t['dir'], t['id']]])
    app('stop_times.txt', [[t['id'], fmt(a_), fmt(b_), stations[i]['gid'], k, f"{abs(stations[i]['chain'] - stations[i0]['chain']):.1f}", tp] for k, (i, a_, b_, tp) in enumerate(t['stops'], 1)])
