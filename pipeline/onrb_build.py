"""Ontario Northland boat service on Lake Nipissing: M.V. Chief Commanda, North Bay - Callander - Keyston Lodge - Dokis (French River), summer 1948
(Brendan, 17 Nov 2026). HIGHLY SPECULATIVE: no regular 1948 timetable in hand. Brendan's understanding is three trips a week, pencilled in as Monday,
Wednesday and Friday; the hours (North Bay 10.00 a.m., back 5.30 p.m.) are from the special Old Home Week schedule of August 1948 (souvenir booklet,
https://icsoh.nipissingu.ca/pdf/Public/Old%20Home%20Week%20-%20Souvenir%20Booklet%20-%201948.pdf, a scan with no text layer, not read by Claude).
The calls in between, the turn at Dokis and the direct run home are ESTIMATED (Claude) by distance. Ports: Brendan's points. Times printed in Eastern
Daylight Time (Brendan), shown on the Pacific clock. Same method as ostc_build.py. Run after ostc_build."""
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
# water: the basemap tiles (page projection) back to lon/lat, as in lo_build.py (Lake Nipissing is not in water_east.json)
from shapely.ops import unary_union
ROOT = os.path.dirname(HERE)
NIP_BOX = (-80.20, -79.25, 46.00, 46.45)
_idx = json.load(open(os.path.join(ROOT, 'basemap', 'tiles', 'index.json'))); _PJ = _idx['proj']
_r = math.pi / 180; _R = _PJ['R']; _p1, _p2, _l0 = _PJ['lat1'] * _r, _PJ['lat2'] * _r, _PJ['lon0'] * _r
_t = lambda p: math.tan(math.pi / 4 + p / 2)
_n = math.log(math.cos(_p1) / math.cos(_p2)) / math.log(_t(_p2) / _t(_p1)); _F = math.cos(_p1) * _t(_p1) ** _n / _n
def _raw(lon, lat): rho = _R * _F / _t(lat * _r) ** _n; th = _n * (lon * _r - _l0); return rho * math.sin(th), rho * math.cos(th)
_ox, _oy = _raw(*_PJ['origin'])
def page_xy(lon, lat): x, y = _raw(lon, lat); return x - _ox, y - _oy
def page_ll(x, y):
    X, Y = x + _ox, y + _oy; rho = math.copysign(math.hypot(X, Y), _n); th = math.atan2(X, Y)
    return (th / _n + _l0) / _r, (2 * math.atan((_R * _F / rho) ** (1 / _n)) - math.pi / 2) / _r
_z = _idx['zmax']; _s = _idx['side'] / 2 ** _z; _polys = []
for _B in (NIP_BOX,):
  _xs, _ys = zip(*[page_xy(lon, lat) for lon in _B[:2] for lat in _B[2:]])
  for tx in range(int((min(_xs) - _idx['origin'][0]) // _s), int((max(_xs) - _idx['origin'][0]) // _s) + 1):
      for ty in range(int((min(_ys) - _idx['origin'][1]) // _s), int((max(_ys) - _idx['origin'][1]) // _s) + 1):
          fn = os.path.join(ROOT, 'basemap', 'tiles', str(_z), f'{tx}_{ty}.json')
          if not os.path.exists(fn): continue
          for poly in json.load(open(fn))['w']:
              rings = []
              for ring in poly:
                  x, y = ring[0], ring[1]; pts = [sea.to_xy(*page_ll(x, y))]
                  for i in range(2, len(ring), 2): x += ring[i]; y += ring[i + 1]; pts.append(sea.to_xy(*page_ll(x, y)))
                  if len(pts) >= 3: rings.append(pts)
              if rings:
                  g = Polygon(rings[0], rings[1:]); _polys.append(g if g.is_valid else g.buffer(0))
sea._U = unary_union(_polys)
if sea._U.geom_type == 'Polygon': sea._U = MultiPolygon([sea._U])
print('water polygons', len(_polys))

P = {'NB': ('North Bay (Government Dock)', (-79.473313, 46.312207), 'North Bay, the Government Dock on Lake Nipissing (Brendan)', 1),
     'CAL': ('Callander (wharf)', (-79.369353, 46.221278), 'Callander, the wharf on Callander Bay (Brendan)', 1),
     'KEY': ('Keyston Lodge', (-79.864038, 46.205394), 'Keyston Lodge, Lake Nipissing (Brendan)', 1),
     'DOK': ('Dokis', (-80.023760, 46.130662), 'Dokis, at the French River outlet of Lake Nipissing (Brendan)', 1)}
def gid(k): return 'PORT_' + re.sub(r'\W+', '_', P[k][0].upper()).strip('_')
LINES = {'onrb': ['NB', 'CAL', 'KEY', 'DOK', 'NB']}
_CF = os.path.join(HERE, 'onrb_legs.json'); CACHE = json.load(open(_CF)) if os.path.exists(_CF) else {}
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



def T(day, h, m=0): return day * 86400 + h * 3600 + m * 60 - 4 * 3600     # Eastern Daylight Time as printed (Brendan, 17 Nov 2026) to the Pacific clock
NEW = []
def gmiles(route, i, j):
    return sum(3958.8 * math.hypot(math.radians(q[0] - p[0]) * math.cos(math.radians((p[1] + q[1]) / 2)), math.radians(q[1] - p[1])) for p, q in zip(route[i:j], route[i + 1:j + 1]))
NOTE = ('M.V. Chief Commanda (Ontario Northland boat service), North Bay to the French River and back: leaves North Bay 10.00 a.m., back 5.30 p.m. '
        'HIGHLY SPECULATIVE: no regular 1948 timetable in hand; three trips a week (pencilled in as Monday, Wednesday and Friday) on the hours of the special '
        'Old Home Week schedule of August 1948; the calls at Callander, Keyston Lodge and Dokis and the turn at Dokis are ESTIMATED by distance. '
        'Eastern Daylight Time as printed, shown here in Pacific time.')
SRC = 'Ontario Northland boat service, M.V. Chief Commanda: Old Home Week souvenir booklet, North Bay, August 1948 (hours); days pencilled in (Brendan, 17 Nov 2026); highly speculative; shown on the Pacific clock'
route, st = build(LINES['onrb'])
ix = lambda c: min(range(len(route)), key=lambda i: abs(route[i][2] - st[c]['chain']))
gm = [gmiles(route, 0, ix(c)) for c in range(len(st))]
t0, t1 = T(0, 10), T(0, 17, 30); run = t1 - t0; turn = 3600     # an hour at Dokis; the rest of the day at an even speed
v = gm[-1] / ((run - turn - 2 * 600) / 3600)       # ten minutes at each call on the way out
stops, t = [[0, t0, t0, 1]], t0
for c in range(1, len(st)):
    t += round((gm[c] - gm[c - 1]) / v * 3600 / 60) * 60
    if c == len(st) - 1: stops.append([c, t1, t1, 1]); break
    d = turn if st[c]['key'] == 'DOK' else 600
    stops.append([c, t, t + d, 0]); t += d
print('miles', [round(x, 1) for x in gm], f'{v:.1f} mph', [(st[s[0]]['key'], s[1] // 3600, s[1] % 3600 // 60) for s in stops])
trips = [dict(id='ONRB-CHIEF-COMMANDA', num='Chief Commanda', name='Ontario Northland boat', svc='W_1010100', dir=0, stops=stops, vessel='Chief Commanda', note=NOTE)]
for s_ in [stops]: assert all(y[1] >= x[2] for x, y in zip(s_, s_[1:])), s_
for s in st: s.pop('key')
NEW.append(dict(key='onrb', kind='v', label='Lake Nipissing: North Bay – Callander – Keyston Lodge – Dokis (French River) – North Bay', mainline=True, water=True, livery='onr', src=SRC,
                owner='onr', route=route, stations=st, dirLabels=['to North Bay', ''], segments=[], trips=trips))
print(f"onrb: {route[-1][2] / MI:.1f} mi of lane, {len(st)} points")
vd['lines'] = [x for x in vd['lines'] if x['key'] not in LINES] + NEW
open(os.path.join(HERE, 'viz_data.json'), 'w').write(json.dumps(vd, separators=(',', ':')))

def fmt(x): return f'{x // 3600:02d}:{x % 3600 // 60:02d}:{x % 60:02d}'
def app(name, rows_):
    with open(os.path.join(GT, name), 'a', newline='') as fh: csv.writer(fh).writerows(rows_)
def have(name, col=0): return set(r[col] for r in csv.reader(open(os.path.join(GT, name))))
if 'W_1010100' not in have('calendar.txt'): app('calendar.txt', [['W_1010100', *'1010100', '19490616', '19491231']])
gseen = have('stops.txt')
for L in NEW:
    st = L['stations']
    app('routes.txt', [['ONRB_' + L['key'].upper(), 'ONR', L['label'], 'Chief Commanda', 4, 'FEBC11', '1D1A10',
                        'Ontario Northland boat service (highly speculative times). The lane is a least-cost path over the water layers, not a surveyed course. Times on the Pacific clock.']])
    new = [[s['gid'], s['name'] + ' (steamer landing)', f"{s['xy'][1]:.6f}", f"{s['xy'][0]:.6f}", s['note']] for s in st if s['gid'] not in gseen]
    app('stops.txt', new); gseen |= {r[0] for r in new}
    for t in L['trips']:
        app('shapes.txt', [[t['id'], f'{p[1]:.6f}', f'{p[0]:.6f}', k, f'{p[2]:.1f}'] for k, p in enumerate(L['route'])])
        app('trips.txt', [['ONRB_' + L['key'].upper(), t['svc'], t['id'], st[t['stops'][-1][0]]['name'], t['vessel'], 0, t['id']]])
        app('stop_times.txt', [[t['id'], fmt(a), fmt(b), st[i]['gid'], k, f"{st[i]['chain']:.1f}", 1] for k, (i, a, b, _) in enumerate(t['stops'], 1)])
