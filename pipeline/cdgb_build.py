"""Chicago, Duluth and Georgian Bay Transit Co.: the S.S. North American (Chicago - Mackinac Island - Parry Sound - Detroit - Cleveland - Buffalo, back by
Detroit and Mackinac) and the S.S. South American (Buffalo - Cleveland - Detroit - the Soo - Houghton - Port Arthur - Duluth, back by the Soo and Detroit),
from the timetable page Brendan supplied (7 November 2026; the year and the season are not printed). One round trip a week each: North American from Chicago
Saturdays and from Buffalo Wednesdays, South American from Buffalo Saturdays and from Duluth Wednesdays. Times printed in Eastern Standard Time (Chicago and Duluth
also in Central), shown on the Pacific clock: three hours earlier than Eastern, two earlier than Central.
Ports: Brendan's points (Buffalo is the Lackawanna (D.L.&W.) depot); Port Arthur is the C.P.R. dock and Duluth the Northern Pacific dock no. 4, the stops already on
file for the CP steamships and the Noronic. The printed passing points (Cove Island, the St. Clair River, the St. Mary's River, the Soo locks, Isle Royale) are
timing points on the page, not stops in the GTFS. The Keweenaw Waterway is in neither water layer: it is drawn here from rough points (Claude's, to be checked).
Same method as cp_lakes_build.py. Run after cp_manitoba_build."""
import csv, json, math, os, re
from shapely.geometry import MultiPolygon, Polygon
from nrwn_graph import fwd, MI
import sea
from sea import Sea, SEA_VERSION
HERE = os.path.dirname(os.path.abspath(__file__)); GT = os.path.join(HERE, 'gtfs')
vd = json.load(open(os.path.join(HERE, 'viz_data.json')))

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
sea._U = MultiPolygon(list(sea.water().geoms) + _east(os.path.join(HERE, 'water_east.json')))

def dms(s):
    v = [float(x) for x in re.findall(r'[\d.]+', s)]; lat = v[0] + v[1] / 60 + v[2] / 3600; lon = v[3] + v[4] / 60 + v[5] / 3600
    return (-lon if 'W' in s else lon, -lat if 'S' in s else lat)
OLD = {r[0]: (float(r[3]), float(r[2])) for r in csv.reader(open(os.path.join(GT, 'stops.txt'))) if r[0].startswith('PORT_')}
B = 'Brendan'
# key: (name, lon/lat, note, a stop?)
P = {'CHI': ('Chicago (Michigan Avenue Bridge)', dms('41°53\'18.79"N 87°37\'26.75"W'), 'S.E. corner, Michigan Avenue bridge, Chicago (Brendan)', 1),
     'BUF': ('Buffalo (Lackawanna Depot)', dms('42°52\'25.83"N 78°52\'37.82"W'), 'Foot of Main Street, Buffalo: the Lackawanna (D.L.&W.) depot (Brendan)', 1),
     'DET': ('Detroit (foot of Woodward Avenue)', dms('42°19\'36.03"N 83°02\'34.68"W'), 'Foot of Woodward Avenue, Detroit (Brendan)', 1),
     'CLE': ('Cleveland (foot of East Ninth Street)', dms('41°30\'40.26"N 81°41\'47.08"W'), 'Foot of East Ninth Street, Cleveland (Brendan)', 1),
     'MAC': ('Mackinac Island (Arnold Dock)', dms('45°50\'55.43"N 84°36\'55.78"W'), 'Arnold Dock, Mackinac Island (Brendan)', 1),
     'PS': ('Parry Sound (Town Dock)', dms('45°20\'19.88"N 80°02\'09.08"W'), 'Town Dock, Parry Sound (Brendan)', 1),
     'HOU': ('Houghton', dms('47°07\'21.27"N 88°34\'19.31"W'), 'Houghton, Mich., on the Keweenaw Waterway (Brendan)', 1),
     'PA': ('Port Arthur (C.P.R. Dock)', OLD['PORT_PORT_ARTHUR_C_P_R_DOCK'], 'C.P.R. dock, Port Arthur (Brendan)', 1),
     'DUL': ('Duluth (Northern Pacific Dock No. 4)', OLD['PORT_DULUTH_NORTHERN_PACIFIC_DOCK_NO_4'], 'Northern Pacific dock no. 4, Duluth (Brendan)', 1),
     # passing points printed in the timetable (rough positions)
     'COVE': ('Cove Island (enters Georgian Bay)', (-81.715, 45.370), 'Passing point: the Main Channel by Cove Island, into Georgian Bay', 0),
     'STC': ('St. Clair River (enters)', (-82.415, 43.030), 'Passing point: the head of the St. Clair River, Port Huron - Sarnia', 0),
     'STM': ('St. Mary\'s River (De Tour)', (-83.900, 45.975), 'Passing point: the foot of the St. Mary\'s River, De Tour Passage', 0),
     'SOO': ('"Soo" Locks', (-84.352, 46.504), 'Passing point: the locks at Sault Ste. Marie', 0),
     'IR': ('Isle Royale (Mott Island)', (-88.520, 48.090), 'Passing point: Isle Royale, by Mott Island and out by Passage Island', 0)}
def gid(k): return 'PORT_' + re.sub(r'\W+', '_', P[k][0].upper()).strip('_') if P[k][3] else 'PASS_CDGB_' + k
# the Keweenaw Waterway: Keweenaw Bay (lower entry) - Portage River - Portage Lake - Houghton - the ship canal - Lake Superior (upper entry). Rough points.
KEW_IN = [(-88.420, 46.965), (-88.455, 47.000), (-88.495, 47.040), (-88.535, 47.085), (-88.560, 47.112)]
KEW_OUT = [(-88.600, 47.133), (-88.635, 47.165), (-88.645, 47.205), (-88.632, 47.236), (-88.620, 47.262)]
PASSAGE = (-88.390, 48.212)          # between Passage Island and Blake Point
WHITEFISH = (-85.00, 46.93)          # as nn_build: out of Whitefish Bay
# a line: a list of ports (keys) and ('via', points) / ('track', points); Sea lanes between, Brendan-style tracks drawn straight
LINES = {
  'cdna_e': ['CHI', 'MAC', 'COVE', 'PS', ('via', [(-81.715, 45.370)]), 'STC', 'DET', 'CLE', 'BUF'],
  'cdna_w': ['BUF', 'DET', ('via', [(-82.415, 43.030)]), 'MAC', 'CHI'],
  'cdsa_w': ['BUF', 'CLE', 'DET', ('via', [(-82.415, 43.030)]), 'STM', 'SOO', ('via', [WHITEFISH]), ('track', KEW_IN), 'HOU', ('track', KEW_OUT), 'IR', ('via', [PASSAGE]), 'PA', 'DUL'],
  'cdsa_e': ['DUL', ('via', [WHITEFISH]), 'SOO', 'STM', ('via', [(-82.415, 43.030)]), 'DET', 'BUF'],
}
_CF = os.path.join(HERE, 'cdgb_legs.json'); CACHE = json.load(open(_CF)) if os.path.exists(_CF) else {}
def sealeg(p, q):
    d = math.dist(fwd(*p), fwd(*q)); res = 60 if d < 40000 else 120 if d < 150000 else 250
    ck = f'{SEA_VERSION}|{p[0]:.4f},{p[1]:.4f}|{q[0]:.4f},{q[1]:.4f}|{res}'
    if ck not in CACHE:
        S = Sea([p, q], res=res, margin=max(8000.0, 0.3 * d)); leg, land = S.leg(p, q)
        if land > 0.02:
            S2 = Sea([p, q], res=res, margin=max(30000.0, 1.2 * d)); leg2, land2 = S2.leg(p, q)
            if land2 < land: S, leg, land = S2, leg2, land2
        CACHE[ck] = [[round(x, 6), round(y, 6)] for x, y in leg]
        print(f"   ({p[0]:.3f},{p[1]:.3f}) - ({q[0]:.3f},{q[1]:.3f}) {d / 1000:.0f} km at {res} m: lane over {land * 100:.1f}% land; snaps {S.snap_m(p):.0f} / {S.snap_m(q):.0f} m")
        json.dump(CACHE, open(_CF, 'w'))
    return [tuple(x) for x in CACHE[ck]]
def build(seq):
    pts, at, last, straight, prev = [], {}, None, False, None
    for n in seq:
        if isinstance(n, str):
            q = P[n][1]
            if straight: pts.append(q)                                    # off the end of a drawn track: straight in
            elif last is not None: pts += sealeg(last, q)[1:] if pts else sealeg(last, q)
            elif not pts: pts.append(q)
            at[len(at)] = (n, len(pts) - 1); last = q; straight = False; prev = 'port'
        else:
            kind, ps = n
            for q in ps:
                if kind == 'via' or (q is ps[0] and prev == 'via'): pts += sealeg(last, q)[1:]      # a track joins a sea lane, or runs straight on from a port
                else: pts.append(q)
                last = q
            straight = kind == 'track'; prev = kind
    route = []; acc = 0.0; prev = None
    for lon, lat in pts:
        xy = fwd(lon, lat)
        if prev: acc += math.dist(xy, prev)
        prev = xy; route.append([round(lon, 6), round(lat, 6), round(acc, 1)])
    st = []
    for _, (k, i) in sorted(at.items()):
        nm, ll, note, stop = P[k]
        st.append(dict(name=nm, chain=route[i][2], lon=route[i][0], lat=route[i][1], mile=round(route[i][2] / MI, 1), lmile=round(route[i][2] / MI, 1), principal=bool(stop),
                       kml='', gid=gid(k), xy=[ll[0], ll[1]], note=note, key=k))
    return route, st

def hm(txt):
    m = re.match(r'(\d+)\.(\d+)([ap])', txt); h, mn = int(m.group(1)), int(m.group(2))
    if m.group(3) == 'p' and h != 12: h += 12
    if m.group(3) == 'a' and h == 12: h = 0
    return h * 3600 + mn * 60
def T(day, t, z='E'): return day * 86400 + hm(t) - (3 if z == 'E' else 2) * 3600     # printed Eastern (or Central) to the Pacific clock
SAIL = {   # line: (svc, ship, [(port key, arrive, leave)], text)
 'cdna_e': ('W_0000010', 'North American', [('CHI', None, T(0, '6.30p', 'C')), ('MAC', T(1, '5.30p'), T(1, '9.30p')), ('COVE', T(2, '8.30a'), T(2, '8.30a')),
            ('PS', T(2, '1.30p'), T(2, '3.30p')), ('STC', T(3, '8.30a'), T(3, '8.30a')), ('DET', T(3, '1.30p'), T(3, '3.00p')), ('CLE', T(3, '10.30p'), T(3, '11.30p')), ('BUF', T(4, '11.30a'), None)],
            'eastbound: Chicago Saturday 6.30 p.m. C.S.T.; Mackinac Island Sunday 5.30 p.m., leaving 9.30 p.m.; enters Georgian Bay at Cove Island Monday 8.30 a.m.; Parry Sound 1.30 p.m., leaving 3.30 p.m.; '
            'enters the St. Clair River Tuesday 8.30 a.m.; Detroit 1.30 p.m., leaving 3.00 p.m.; Cleveland 10.30 p.m., leaving 11.30 p.m.; Buffalo Wednesday 11.30 a.m.'),
 'cdna_w': ('W_0010000', 'North American', [('BUF', None, T(0, '7.30p')), ('DET', T(1, '1.30p'), T(1, '3.00p')), ('MAC', T(2, '12.30p'), T(2, '2.00p')), ('CHI', T(3, '10.45a', 'C'), None)],
            'westbound: Buffalo Wednesday 7.30 p.m.; Detroit Thursday 1.30 p.m., leaving 3.00 p.m.; Mackinac Island Friday 12.30 p.m., leaving 2.00 p.m.; Chicago Saturday 10.45 a.m. C.S.T.'),
 'cdsa_w': ('W_0000010', 'South American', [('BUF', None, T(0, '8.30p')), ('CLE', T(1, '8.00a'), T(1, '9.00a')), ('DET', T(1, '4.30p'), T(1, '6.00p')), ('STM', T(2, '2.30p'), T(2, '2.30p')),
            ('SOO', T(2, '6.30p'), T(2, '6.30p')), ('HOU', T(3, '9.00a'), T(3, '10.30a')), ('IR', T(3, '3.30p'), T(3, '3.30p')), ('PA', T(3, '7.30p'), T(3, '9.30p')), ('DUL', T(4, '9.00a', 'C'), None)],
            'westbound: Buffalo Saturday 8.30 p.m.; Cleveland Sunday 8.00 a.m., leaving 9.00 a.m.; Detroit 4.30 p.m., leaving 6.00 p.m.; enters the St. Mary\'s River Monday 2.30 p.m.; passes the "Soo" locks 6.30 p.m.; '
            'Houghton (by the Keweenaw Waterway) Tuesday 9.00 a.m., leaving 10.30 a.m.; passes Isle Royale (by Mott and Passage Islands) 3.30 p.m.; Port Arthur 7.30 p.m., leaving 9.30 p.m.; Duluth Wednesday 9.00 a.m. C.S.T.'),
 'cdsa_e': ('W_0010000', 'South American', [('DUL', None, T(0, '2.00p', 'C')), ('SOO', T(1, '4.00p'), T(1, '4.00p')), ('STM', T(1, '8.00p'), T(1, '8.00p')), ('DET', T(2, '3.30p'), T(2, '6.00p')), ('BUF', T(3, '11.00a'), None)],
            'eastbound: Duluth Wednesday 2.00 p.m. C.S.T.; passes the "Soo" locks Thursday 4.00 p.m.; leaves the St. Mary\'s River 8.00 p.m.; Detroit Friday 3.30 p.m., leaving 6.00 p.m.; Buffalo Saturday 11.00 a.m.'),
}
LABEL = {'cdna_e': ('North American: Chicago – Parry Sound – Buffalo', 'to Buffalo'), 'cdna_w': ('North American: Buffalo – Mackinac Island – Chicago', 'to Chicago'),
         'cdsa_w': ('South American: Buffalo – Port Arthur – Duluth', 'to Duluth'), 'cdsa_e': ('South American: Duluth – Buffalo', 'to Buffalo')}
_n = (' Chicago, Duluth and Georgian Bay Transit Co.: one round trip a week each (year and season not printed on the page). Times printed in Eastern Standard Time'
      ' (Chicago and Duluth in Central too) and shown here in Pacific time. Passing points printed in the timetable are shown as timing points, not calls.')
SRC = 'Chicago, Duluth and Georgian Bay Transit Co. timetable (S.S. North American, S.S. South American), supplied by Brendan, 7 November 2026; year not printed. Eastern Standard Time as printed (Chicago, Duluth Central), shown on the Pacific clock'
NEW = []
for key, seq in LINES.items():
    route, st = build(seq)
    svc, ship, calls, txt = SAIL[key]
    idx = {s['key']: i for i, s in enumerate(st)}
    assert [c[0] for c in calls] == [s['key'] for s in st], (key, [c[0] for c in calls], [s['key'] for s in st])
    stops = [[idx[k], (a if a is not None else b), (b if b is not None else a), 1] for k, a, b in calls]
    assert stops[0][1] >= 0 and all(y[1] >= x[2] for x, y in zip(stops, stops[1:])), (key, stops)
    for x, y in zip(stops, stops[1:]):
        leg = (st[y[0]]['chain'] - st[x[0]]['chain']) / MI; h = (y[1] - x[2]) / 3600
        print(f"  {key} {st[x[0]]['name'][:30]:30s} - {st[y[0]]['name'][:30]:30s} {leg:6.1f} mi in {h:5.2f} h = {leg / h:5.1f} mph" + ('   !! check' if not 6 < leg / h < 21 else ''))
    tid = 'CDGB-' + key.upper()
    trip = dict(id=tid, num=ship, name='C.D.&G.B. steamer', svc=svc, dir=0, stops=stops, note='S.S. ' + ship + ', ' + txt + _n, vessel=ship)
    for s in st: s.pop('key')
    lab, dl = LABEL[key]
    NEW.append(dict(key=key, kind='v', label=lab, mainline=True, water=True, livery='cdgb', src=SRC, owner='cdgb', route=route, stations=st, dirLabels=[dl, ''], segments=[], trips=[trip]))
    print(f"{key}: {route[-1][2] / MI:.1f} mi of lane, {len(st)} points")
vd['lines'] = [x for x in vd['lines'] if x['key'] not in LINES] + NEW
open(os.path.join(HERE, 'viz_data.json'), 'w').write(json.dumps(vd, separators=(',', ':')))

# ---------------- GTFS (route_type 4); passing points are left out
def fmt(x): return f'{x // 3600:02d}:{x % 3600 // 60:02d}:{x % 60:02d}'
def app(name, rows_):
    with open(os.path.join(GT, name), 'a', newline='') as fh: csv.writer(fh).writerows(rows_)
def have(name, col=0): return set(r[col] for r in csv.reader(open(os.path.join(GT, name))))
if 'CDGB' not in have('agency.txt'): app('agency.txt', [['CDGB', 'Chicago, Duluth and Georgian Bay Transit Company', 'https://en.wikipedia.org/wiki/SS_South_American', 'America/Vancouver', 'en', '']])
cal = have('calendar.txt')
app('calendar.txt', [[w, *w[2:], '19490616', '19491231'] for w in sorted({SAIL[k][0] for k in LINES}) if w not in cal])
gseen = have('stops.txt')
for L in NEW:
    st = L['stations']; t = L['trips'][0]
    app('routes.txt', [['CDGB_' + L['key'].upper(), 'CDGB', L['label'], ' – '.join(s['name'] for s in st if s['principal']), 4, '1D6B6B', 'FFFFFF',
                        'S.S. ' + t['vessel'] + ', Chicago, Duluth and Georgian Bay Transit Co. The lane is a least-cost path over the water layers, not a surveyed course. Times on the Pacific clock.']])
    new = [[s['gid'], s['name'] + ' (steamer landing)', f"{s['xy'][1]:.6f}", f"{s['xy'][0]:.6f}", s['note']] for s in st if s['principal'] and s['gid'] not in gseen]
    app('stops.txt', new); gseen |= {r[0] for r in new}
    app('shapes.txt', [[t['id'], f'{p[1]:.6f}', f'{p[0]:.6f}', k, f'{p[2]:.1f}'] for k, p in enumerate(L['route'])])
    app('trips.txt', [['CDGB_' + L['key'].upper(), t['svc'], t['id'], st[t['stops'][-1][0]]['name'], t['vessel'] + ' – ' + L['label'].split(': ')[1], 0, t['id']]])
    rows = [(i, a, b) for i, a, b, _ in t['stops'] if st[i]['principal']]
    app('stop_times.txt', [[t['id'], fmt(a), fmt(b), st[i]['gid'], k, f"{st[i]['chain']:.1f}", 1] for k, (i, a, b) in enumerate(rows, 1)])
