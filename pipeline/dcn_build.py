"""Detroit and Cleveland Navigation Co., summer 1948 (Brendan, 17 Nov 2026: the company's sailing list; "All ships operate on Eastern Standard Time").
- Detroit and Cleveland Division, S.S. Eastern States: Detroit (Third Street Dock) 1.00 p.m. - Cleveland (East Ninth Street Pier) 8.30 p.m.; Cleveland 12.00
  night - Detroit 8.00 a.m.; daily in the summer months (first sailings June 25).
- Detroit and Buffalo Division, S.S. City of Detroit III and S.S. Greater Detroit: Detroit 5.30 p.m. - Buffalo (Main Street Dock) 9.00 a.m.; Buffalo 5.30 p.m. -
  Detroit 9.00 a.m.; daily (first sailings May 27 / 28).
- 7-day cruises, S.S. City of Cleveland III: Buffalo Saturday 9.30 p.m. - Detroit - Mackinac Island - Chicago Tuesday 2.00 p.m.; Chicago Tuesday 7.30 p.m. -
  Mackinac Island - Midland, Ont. - Detroit - Buffalo Saturday 2.30 p.m.
- Mid-week cruises, S.S. Western States: Detroit Monday 2.30 p.m. - Mackinac Island - Harbor Springs - Midland, Ont. - Detroit Friday 10.30 a.m.;
  week-end cruises: Detroit Friday 7.00 p.m. - Harbor Springs - Mackinac Island - Detroit Monday 7.00 a.m.
Shown on the Pacific clock (three hours earlier than Eastern). Ports: Brendan's points where the C.D.&G.B. already has them (Buffalo, Cleveland, Mackinac Island,
Chicago); the Detroit Third Street Dock, Harbor Springs and Midland are Claude's (APPROXIMATE). Same method as cdgb_build.py. Scans: private repo, scans/marine/dcnav_1948_*."""
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
def dms(s):
    v = [float(x) for x in re.findall(r'[\d.]+', s)]; lat = v[0] + v[1] / 60 + v[2] / 3600; lon = v[3] + v[4] / 60 + v[5] / 3600
    return (-lon if 'W' in s else lon, -lat if 'S' in s else lat)
P = {'CHI': ('Chicago (Michigan Avenue Bridge)', dms('41°53\'18.79"N 87°37\'26.75"W'), 'S.E. corner, Michigan Avenue bridge, Chicago (Brendan; the D.&C. dock not identified)', 1),
     'BUF': ('Buffalo (Lackawanna Depot)', dms('42°52\'25.83"N 78°52\'37.82"W'), 'Foot of Main Street, Buffalo: the D.&C. Main Street Dock (Brendan\'s point)', 1),
     'DTS': ('Detroit (Third Street Dock)', (-83.0555, 42.3252), 'D.&C. dock, foot of Third Street, Detroit (the point APPROXIMATE, Claude)', 1),
     'CLE': ('Cleveland (foot of East Ninth Street)', dms('41°30\'40.26"N 81°41\'47.08"W'), 'East Ninth Street Pier, Cleveland (Brendan\'s point)', 1),
     'MAC': ('Mackinac Island (Arnold Dock)', dms('45°50\'55.43"N 84°36\'55.78"W'), 'Mackinac Island (Brendan\'s point, the Arnold Dock)', 1),
     'HSP': ('Harbor Springs', (-84.9905, 45.4290), 'Harbor Springs, Mich., Little Traverse Bay (the point APPROXIMATE, Claude)', 1),
     'MID': ('Midland, Ont. (town dock)', (-79.8868, 44.7512), 'Midland, Ont., Georgian Bay: the town dock (the point APPROXIMATE, Claude)', 1),
     'STC': ('St. Clair River (enters)', (-82.415, 43.030), 'Passing point: the head of the St. Clair River, Port Huron - Sarnia', 0),
     'COVE': ('Cove Island (enters Georgian Bay)', (-81.715, 45.370), 'Passing point: the Main Channel by Cove Island, into Georgian Bay', 0)}
def gid(k): return 'PORT_' + re.sub(r'\W+', '_', P[k][0].upper()).strip('_') if P[k][3] else 'PASS_DCN_' + k
SC = (-82.415, 43.030); CV = (-81.715, 45.370)
LINES = {
  'dccl_e': ['DTS', 'CLE'], 'dccl_w': ['CLE', 'DTS'], 'dcbu_e': ['DTS', 'BUF'], 'dcbu_w': ['BUF', 'DTS'],
  'dc7_w': ['BUF', 'DTS', ('via', [SC]), 'MAC', 'CHI'],
  'dc7_e': ['CHI', 'MAC', ('via', [CV]), 'MID', ('via', [CV, SC]), 'DTS', 'BUF'],
  'dcwm': ['DTS', ('via', [SC]), 'MAC', 'HSP', ('via', [CV]), 'MID', ('via', [CV, SC]), 'DTS'],
  'dcwe': ['DTS', ('via', [SC]), 'HSP', 'MAC', ('via', [SC]), 'DTS'],
}
_CF = os.path.join(HERE, 'dcn_legs.json'); CACHE = json.load(open(_CF)) if os.path.exists(_CF) else {}
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
def T(day, t): return day * 86400 + hm(t) - 3 * 3600     # Eastern Standard Time to the Pacific clock
D = 'W_1111111'
SAIL = {   # line: (svc, ship, [(port key, arrive, leave)], text)
 'dccl_e': (D, 'Eastern States', [('DTS', None, T(0, '1.00p')), ('CLE', T(0, '8.30p'), None)], 'Detroit 1.00 p.m. daily, Cleveland 8.30 p.m.'),
 'dccl_w': (D, 'Eastern States', [('CLE', None, T(1, '12.00a')), ('DTS', T(1, '8.00a'), None)], 'Cleveland 12.00 night daily, Detroit 8.00 a.m.'),
 'dcbu_e': (D, 'City of Detroit III / Greater Detroit', [('DTS', None, T(0, '5.30p')), ('BUF', T(1, '9.00a'), None)], 'Detroit 5.30 p.m. daily, Buffalo 9.00 a.m.'),
 'dcbu_w': (D, 'City of Detroit III / Greater Detroit', [('BUF', None, T(0, '5.30p')), ('DTS', T(1, '9.00a'), None)], 'Buffalo 5.30 p.m. daily, Detroit 9.00 a.m.'),
 'dc7_w': ('W_0000010', 'City of Cleveland III', [('BUF', None, T(0, '9.30p')), ('DTS', T(1, '2.30p'), T(1, '7.30p')), ('MAC', T(2, '4.00p'), T(2, '5.00p')), ('CHI', T(3, '2.00p'), None)],
           '7-day cruise: Buffalo Saturday 9.30 p.m.; Detroit Sunday 2.30 p.m., leaving 7.30 p.m.; Mackinac Island Monday 4.00 p.m., leaving 5.00 p.m.; Chicago Tuesday 2.00 p.m. (Eastern time)'),
 'dc7_e': ('W_0100000', 'City of Cleveland III', [('CHI', None, T(0, '7.30p')), ('MAC', T(1, '4.00p'), T(1, '10.00p')), ('MID', T(2, '2.00p'), T(2, '4.30p')),
            ('DTS', T(3, '2.30p'), T(3, '9.30p')), ('BUF', T(4, '2.30p'), None)],
           '7-day cruise: Chicago Tuesday 7.30 p.m. (Eastern time); Mackinac Island Wednesday 4.00 p.m., leaving 10.00 p.m.; Midland, Ont., Thursday 2.00 p.m., leaving 4.30 p.m.; Detroit Friday 2.30 p.m., leaving 9.30 p.m.; Buffalo Saturday 2.30 p.m.'),
 'dcwm': ('W_1000000', 'Western States', [('DTS', None, T(0, '2.30p')), ('MAC', T(1, '12.00p'), T(2, '1.30a')), ('HSP', T(2, '7.00a'), T(2, '12.00p')), ('MID', T(3, '8.00a'), T(3, '12.00p')),
           ('DTS', T(4, '10.30a'), None)],
          'mid-week cruise: Detroit Monday 2.30 p.m.; Mackinac Island Tuesday 12.00 noon, leaving Wednesday 1.30 a.m.; Harbor Springs Wednesday 7.00 a.m., leaving 12.00 noon; Midland, Ont., Thursday 8.00 a.m., leaving 12.00 noon; Detroit Friday 10.30 a.m.'),
 'dcwe': ('W_0000100', 'Western States', [('DTS', None, T(0, '7.00p')), ('HSP', T(1, '7.30p'), T(2, '1.30a')), ('MAC', T(2, '7.00a'), T(2, '12.00p')), ('DTS', T(3, '7.00a'), None)],
          'week-end cruise: Detroit Friday 7.00 p.m.; Harbor Springs Saturday 7.30 p.m., leaving Sunday 1.30 a.m.; Mackinac Island Sunday 7.00 a.m., leaving 12.00 noon; Detroit Monday 7.00 a.m.'),
}
ALT = {'dcbu_e': [('W_1010101', 'Greater Detroit'), ('W_0101010', 'City of Detroit III')], 'dcbu_w': [('W_1010101', 'City of Detroit III'), ('W_0101010', 'Greater Detroit')]}
LABEL = {'dccl_e': ('Detroit – Cleveland', 'to Cleveland'), 'dccl_w': ('Cleveland – Detroit', 'to Detroit'), 'dcbu_e': ('Detroit – Buffalo', 'to Buffalo'), 'dcbu_w': ('Buffalo – Detroit', 'to Detroit'),
         'dc7_w': ('7-day cruise: Buffalo – Detroit – Mackinac Island – Chicago', 'to Chicago'), 'dc7_e': ('7-day cruise: Chicago – Midland – Detroit – Buffalo', 'to Buffalo'),
         'dcwm': ('Mid-week cruise: Detroit – Mackinac Island – Harbor Springs – Midland – Detroit', 'to Detroit'), 'dcwe': ('Week-end cruise: Detroit – Harbor Springs – Mackinac Island – Detroit', 'to Detroit')}
_n = ' Detroit and Cleveland Navigation Co., summer 1948 (Brendan). All ships operate on Eastern Standard Time; shown here in Pacific time. Passing points (the St. Clair River, Cove Island) are drawn, not timed.'
SRC = 'Detroit and Cleveland Navigation Co. sailing list, summer 1948 (Brendan); Eastern Standard Time as printed, shown on the Pacific clock'
NEW = []
for key, seq in LINES.items():
    route, st = build(seq)
    svc, ship, calls, txt = SAIL[key]
    assert [c[0] for c in calls] == [s['key'] for s in st], (key, [c[0] for c in calls], [s['key'] for s in st])
    stops = [[i, (a if a is not None else b), (b if b is not None else a), 1] for i, (k, a, b) in enumerate(calls)]
    assert stops[0][1] >= 0 and all(y[1] >= x[2] for x, y in zip(stops, stops[1:])), (key, stops)
    for x, y in zip(stops, stops[1:]):
        leg = (st[y[0]]['chain'] - st[x[0]]['chain']) / MI; h = (y[1] - x[2]) / 3600
        print(f"  {key} {st[x[0]]['name'][:30]:30s} - {st[y[0]]['name'][:30]:30s} {leg:6.1f} mi in {h:5.2f} h = {leg / h:5.1f} mph" + ('   !! check' if not 4 < leg / h < 25 else ''))
    tid = 'DCN-' + key.upper()
    if key in ALT:   # the two Buffalo boats: one each way each night, turn and turn about (which ship on which night ESTIMATED: Brendan, 17 Nov 2026)
        trips = [dict(id=f'{tid}-{k}', num=sh, name='D.&C. steamer', svc=sv, dir=0, stops=stops, vessel=sh,
                      note='S.S. ' + sh + ', ' + txt + '. The division\'s two ships, the City of Detroit III and the Greater Detroit, sailed one each way every night; which ship sailed on which night is ESTIMATED (turn and turn about).' + _n)
                 for k, (sv, sh) in enumerate(ALT[key])]
    else: trips = [dict(id=tid, num=ship, name='D.&C. steamer', svc=svc, dir=0, stops=stops, note='S.S. ' + ship + ', ' + txt + '.' + _n, vessel=ship)]
    for s in st: s.pop('key')
    lab, dl = LABEL[key]
    NEW.append(dict(key=key, kind='v', label=lab, mainline=True, water=True, livery='dcn', src=SRC, owner='dcn', route=route, stations=st, dirLabels=[dl, ''], segments=[], trips=trips))
    print(f"{key}: {route[-1][2] / MI:.1f} mi of lane, {len(st)} points")
vd['lines'] = [x for x in vd['lines'] if x['key'] not in LINES] + NEW
open(os.path.join(HERE, 'viz_data.json'), 'w').write(json.dumps(vd, separators=(',', ':')))

# ---------------- GTFS (route_type 4); passing points are left out
def fmt(x): return f'{x // 3600:02d}:{x % 3600 // 60:02d}:{x % 60:02d}'
def app(name, rows_):
    with open(os.path.join(GT, name), 'a', newline='') as fh: csv.writer(fh).writerows(rows_)
def have(name, col=0): return set(r[col] for r in csv.reader(open(os.path.join(GT, name))))
if 'DCN' not in have('agency.txt'): app('agency.txt', [['DCN', 'Detroit and Cleveland Navigation Company', 'https://en.wikipedia.org/wiki/Detroit_and_Cleveland_Navigation_Company', 'America/Vancouver', 'en', '']])
cal = have('calendar.txt')
app('calendar.txt', [[w, *w[2:], '19490616', '19491231'] for w in sorted({SAIL[k][0] for k in LINES} | {v for a in ALT.values() for v, _ in a}) if w not in cal])
gseen = have('stops.txt')
for L in NEW:
    st = L['stations']; t = L['trips'][0]
    app('routes.txt', [['DCN_' + L['key'].upper(), 'DCN', L['label'], ' – '.join(s['name'] for s in st if s['principal']), 4, 'B0702A', 'FFFFFF',
                        'Detroit and Cleveland Navigation Co. The lane is a least-cost path over the water layers, not a surveyed course. Times on the Pacific clock.']])
    new = [[s['gid'], s['name'] + ' (steamer landing)', f"{s['xy'][1]:.6f}", f"{s['xy'][0]:.6f}", s['note']] for s in st if s['principal'] and s['gid'] not in gseen]
    app('stops.txt', new); gseen |= {r[0] for r in new}
    for t in L['trips']:
        app('shapes.txt', [[t['id'], f'{p[1]:.6f}', f'{p[0]:.6f}', k, f'{p[2]:.1f}'] for k, p in enumerate(L['route'])])
        app('trips.txt', [['DCN_' + L['key'].upper(), t['svc'], t['id'], st[t['stops'][-1][0]]['name'], t['vessel'], 0, t['id']]])
        rows = [(i, a, b) for i, a, b, _ in t['stops'] if st[i]['principal']]
        app('stop_times.txt', [[t['id'], fmt(a), fmt(b), st[i]['gid'], k, f"{st[i]['chain']:.1f}", 1] for k, (i, a, b) in enumerate(rows, 1)])
