"""Canadian Pacific Great Lakes steamships Keewatin and Assiniboia, Port McNicoll - Sault Ste. Marie - Port Arthur - Fort William, from the 1948 CP timetable page Brendan
supplied (3 November 2026): from Port McNicoll every Tuesday (Keewatin) and Saturday (Assiniboia), from Fort William every Saturday (Keewatin) and Tuesday (Assiniboia),
June 5 to Sept. 11 (the weekdays are 1948's). Eastern Standard Time as printed, shown on the Pacific clock (three hours earlier). The connecting trains (703 / 704 Toronto,
1 / 4 Winnipeg) are in the model already. Port McNicoll is the CP station (gid CP_PORT_MCNICOLL); Sault Ste. Marie is the Government Dock, the same stop as the Noronic's;
Port Arthur and Fort William are CP docks (traces/lakes/cp_great_lakes.kml, Brendan's points). Same method as nn_build.py (Great Lakes water added to the lane mask here). Run after nn_build."""
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

# ---------------- ports: Brendan's points (the Sault dock is the Noronic's, from its KMZ; Port Arthur and Fort William from cp_great_lakes.kml)
_ns = {'k': 'http://www.opengis.net/kml/2.2'}
def _kml(root):
    out = {}
    for pm in root.iter('{http://www.opengis.net/kml/2.2}Placemark'):
        nm = pm.find('k:name', _ns).text.strip(); c = pm.find('k:Point/k:coordinates', _ns).text.strip().split(',')
        out[nm] = (float(c[0]), float(c[1]))
    return out
NNK = _kml(ET.fromstring(zipfile.ZipFile(os.path.join(HERE, 'traces', 'lakes', 'northern_navigation_co.kmz')).read('doc.kml')))
CPK = _kml(ET.parse(os.path.join(HERE, 'traces', 'lakes', 'cp_great_lakes.kml')).getroot())
SSM = 'Sault Ste. Marie (C.S.L. Dock)'
PORTS = [('Port McNicoll', 'CP_PORT_MCNICOLL', 'Port McNicoll, Ont.: the steamer leaves directly from the C.P.R. station (Brendan)'),
         (SSM, NNK[SSM], "Government Dock, Sault Ste. Marie, Ont. (Brendan); the Canada Steamship Lines dock, also called the Northern Navigation Dock, the Noronic's stop"),
         ('Port Arthur (C.P.R. Dock)', CPK['Port Arthur'], 'C.P.R. dock, Port Arthur (Brendan)'),
         ('Fort William (C.P.R. Docks)', CPK['Fort William'], 'C.P.R. docks, Fort William (Brendan)')]
def port(n, v, note):
    if isinstance(v, str): r = RAIL[v]; return dict(name=n, gid=v, lon=r['lon'], lat=r['lat'], rail=True, note=note)
    return dict(name=n, gid='PORT_' + re.sub(r'\W+', '_', n.upper()).strip('_'), lon=v[0], lat=v[1], rail=False, note=note)
ports = [port(*p) for p in PORTS]
ports[1]['gid'] = 'PORT_SAULT_STE_MARIE_C_S_L_DOCK'                  # the same stop as the Noronic's, so the two merge on the page

# ---------------- lanes (cache: cpgl_legs.json)
RES = {(0, 1): 250, (1, 2): 250, (2, 3): 60}
_CF = os.path.join(HERE, 'cpgl_legs.json'); CACHE = json.load(open(_CF)) if os.path.exists(_CF) else {}
VIA = {(1, 2): [(-85.00, 46.93), (-86.35, 47.35), (-88.15, 48.33)]}      # as nn_build: past Passage Island and across the lake (Sault towards Port Arthur)
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

# ---------------- times: Eastern Standard Time as printed, shown on the Pacific clock (- 3 h)
OFF = 3 * 3600
def hm(txt):
    m = re.match(r'(\d+)\.(\d+)([ap])', txt); h, mn = int(m.group(1)), int(m.group(2))
    if m.group(3) == 'p' and h != 12: h += 12
    if m.group(3) == 'a' and h == 12: h = 0
    return h * 3600 + mn * 60
E = lambda t, day=0: hm(t) + day * 86400
# (port index, arrival, departure, printed?): every time is printed; Port Arthur has one time only
WEST = [(0, E('5.30p'), E('5.30p'), 1), (1, E('11.45a', 1), E('12.30p', 1), 1), (2, E('6.45a', 2), E('6.45a', 2), 1), (3, E('8.30a', 2), E('8.30a', 2), 1)]
EASTK = [(3, E('11.00a'), E('11.00a'), 1), (2, E('12.30p'), E('12.30p'), 1), (1, E('8.30a', 1), E('11.30a', 1), 1), (0, E('6.30a', 2), E('6.30a', 2), 1)]
EASTA = [(3, E('4.00p'), E('4.00p'), 1), (2, E('5.30p'), E('5.30p'), 1), (1, E('1.00p', 1), E('2.00p', 1), 1), (0, E('8.30a', 2), E('8.30a', 2), 1)]
_n = (' Canadian Pacific Great Lakes steamship service, Port McNicoll - Sault Ste. Marie - Port Arthur - Fort William, June 5 to Sept. 11: from Port McNicoll Tuesdays (Keewatin) and Saturdays (Assiniboia),'
      ' from Fort William Saturdays (Keewatin) and Tuesdays (Assiniboia). Times printed in Eastern Standard Time and shown here in Pacific time, three hours earlier.')
TRIPS = [('KW', 'Keewatin', 'W_0100000', WEST, 0, 'westbound: Port McNicoll Tuesday 5.30 p.m.; Sault Ste. Marie (Government Dock) Wednesday 11.45 a.m., leaving 12.30 p.m.; Port Arthur Thursday 6.45 a.m.; Fort William 8.30 a.m.'),
         ('AW', 'Assiniboia', 'W_0000010', WEST, 0, 'westbound: Port McNicoll Saturday 5.30 p.m.; Sault Ste. Marie (Government Dock) Sunday 11.45 a.m., leaving 12.30 p.m.; Port Arthur Monday 6.45 a.m.; Fort William 8.30 a.m.'),
         ('KE', 'Keewatin', 'W_0000010', EASTK, 1, 'eastbound: Fort William Saturday 11.00 a.m.; Port Arthur 12.30 p.m.; Sault Ste. Marie (Government Dock) Sunday 8.30 a.m., leaving 11.30 a.m.; Port McNicoll Monday 6.30 a.m.'),
         ('AE', 'Assiniboia', 'W_0100000', EASTA, 1, 'eastbound: Fort William Tuesday 4.00 p.m.; Port Arthur 5.30 p.m.; Sault Ste. Marie (Government Dock) Wednesday 1.00 p.m., leaving 2.00 p.m.; Port McNicoll Thursday 8.30 a.m.')]
trips = []
for tid, ves, svc, calls, d, txt in TRIPS:
    stops = [[i, int(round(a / 60.0)) * 60 - OFF, int(round(b / 60.0)) * 60 - OFF, pr] for i, a, b, pr in calls]
    assert stops[0][1] >= 0 and all(y[1] >= x[2] for x, y in zip(stops, stops[1:])), (tid, stops)
    run = abs(stations[calls[-1][0]]['chain'] - stations[calls[0][0]]['chain']) / MI; hrs = (stops[-1][1] - stops[0][2]) / 3600
    for (i, a, b, pr), (j, a2, b2, pr2) in zip(stops, stops[1:]):
        leg = abs(stations[j]['chain'] - stations[i]['chain']) / MI; h = (a2 - b) / 3600
        print(f"  CPGL-{tid} {stations[i]['name'][:22]:22s} - {stations[j]['name'][:22]:22s} {leg:6.1f} mi in {h:5.2f} h = {leg / h:5.1f} mph" + ('   !! check' if not 4 < leg / h < 21 and leg > 5 else ''))
    trips.append(dict(id=f'CPGL-{tid}', num=ves, name='CP Great Lakes', svc=svc, dir=d, stops=stops, note='S.S. ' + ves + ', ' + txt + _n, vessel=ves))
    print(f'CPGL-{tid}: {run:.1f} mi in {hrs:.1f} h = {run / hrs:.1f} mph overall')
SRC = 'Canadian Pacific timetable, April 1948 (Port McNicoll - Fort William steamships), supplied by Brendan, 3 November 2026. Eastern Standard Time as printed, shown on the Pacific clock'
LINE = dict(key='cpgl', kind='v', label='CP Great Lakes Steamships', mainline=True, water=True, livery='cpss', src=SRC, owner='cp', route=route, stations=stations,
            dirLabels=['to Fort William', 'to Port McNicoll'], segments=[], trips=trips)
vd['lines'] = [x for x in vd['lines'] if x['key'] != 'cpgl'] + [LINE]
open(os.path.join(HERE, 'viz_data.json'), 'w').write(json.dumps(vd, separators=(',', ':')))
print(f"cpgl: Port McNicoll - Fort William, {acc / MI:.1f} mi of lane, {len(stations)} calls, {len(trips)} sailings")

# ---------------- GTFS (route_type 4: ferry)
def fmt(x): return f'{x // 3600:02d}:{x % 3600 // 60:02d}:{x % 60:02d}'
def app(name, rows_):
    with open(os.path.join(GT, name), 'a', newline='') as fh: csv.writer(fh).writerows(rows_)
def have(name, col=0): return set(r[col] for r in csv.reader(open(os.path.join(GT, name))))
app('calendar.txt', [[w, *w[2:], '19490616', '19491231'] for w in sorted({t['svc'] for t in trips}) if w not in have('calendar.txt')])
app('routes.txt', [['CPGL', 'CP', 'Port McNicoll – Sault Ste. Marie – Port Arthur – Fort William', ' – '.join(s['name'] for s in stations), 4, '7A1E2C', 'FFFFFF',
                    'Keewatin and Assiniboia, Canadian Pacific Great Lakes steamships. The lane is a least-cost path over the water layer, not a surveyed course. Times on the Pacific clock, three hours earlier than the Eastern time printed.']])
gseen = have('stops.txt')
app('stops.txt', [[s['gid'], s['name'] + ' (steamer landing)', f"{s['lat']:.6f}", f"{s['lon']:.6f}", s['note']] for s in stations if s['gid'] not in gseen])
for t in trips:
    i0, i1 = t['stops'][0][0], t['stops'][-1][0]; lo, hi = sorted((stations[i0]['chain'], stations[i1]['chain']))
    pts_ = [p for p in route if lo - 0.5 <= p[2] <= hi + 0.5]
    if t['dir'] == 1: pts_ = pts_[::-1]
    app('shapes.txt', [[t['id'], f'{p[1]:.6f}', f'{p[0]:.6f}', k, f'{abs(p[2] - pts_[0][2]):.1f}'] for k, p in enumerate(pts_)])
    app('trips.txt', [['CPGL', t['svc'], t['id'], stations[i1]['name'], t['vessel'] + ' – ' + t['name'], t['dir'], t['id']]])
    app('stop_times.txt', [[t['id'], fmt(a_), fmt(b_), stations[i]['gid'], k, f"{abs(stations[i]['chain'] - stations[i0]['chain']):.1f}", tp] for k, (i, a_, b_, tp) in enumerate(t['stops'], 1)])
