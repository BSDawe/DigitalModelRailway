"""Arnold Transit Company, St. Ignace - Mackinac Island (Official Guide, May 1948; Brendan's image, 20 Nov 2026; private repo scans/og1948_dssa/arnold_transit.png).
Leaves St. Ignace 10.15 a.m., 1.45 p.m., 5.40 p.m.; leaves Mackinac Island 7.55 a.m., 12.30 p.m., 4.30 p.m. Eastern time; no day sign printed: daily (Brendan). The crossing
time is not printed: 30 minutes (Claude's estimate). Docks (Brendan): Mackinac Island, the Arnold Dock (the D.&C. port, dcn_build.py); St. Ignace, Dock No. 1. Not entered (no times
printed): Mackinaw City - Mackinac Island (service resumed June 1, 1948) and Mackinac Island - Les Cheneaux Islands (Coryell Island; resumed June 16, 1948). Water from the basemap
tiles, as in gtwf_build.py. Run after dcn_build (the Arnold Dock stop)."""
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
NIP_BOX = (-84.80, -84.55, 45.80, 45.92)   # the Straits of Mackinac, St. Ignace - Mackinac Island
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


P = {'MAC': ('Mackinac Island (Arnold Dock)', (-84.615494, 45.848731), 'Mackinac Island, the Arnold Dock (Brendan)', 1),
     'SIG': ('St. Ignace (Dock No. 1)', (-84.722672, 45.868471), 'St. Ignace, Dock No. 1 (Brendan, 20 Nov 2026)', 1)}
def gid(k): return 'PORT_' + re.sub(r'\W+', '_', P[k][0].upper()).strip('_')
LINES = {'atc_w': ['MAC', 'SIG'], 'atc_e': ['SIG', 'MAC']}
_CF = os.path.join(HERE, 'atc_legs.json'); CACHE = json.load(open(_CF)) if os.path.exists(_CF) else {}
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




NEW = []
NOTE = {'w': 'Arnold Transit Company, Mackinac Island to St. Ignace: leaves Mackinac Island {} (Eastern time); crossing time estimated (30 minutes). Daily. Shown in Pacific time.',
        'e': 'Arnold Transit Company, St. Ignace to Mackinac Island: leaves St. Ignace {} (Eastern time); crossing time estimated (30 minutes). Daily. Shown in Pacific time.'}
SRC = 'Arnold Transit Company: St. Ignace - Mackinac Island route, Official Guide, May 1948 (Brendan, 20 Nov 2026); shown on the Pacific clock'
DEP = {'w': [(7, 55, '7.55 a.m.'), (12, 30, '12.30 p.m.'), (16, 30, '4.30 p.m.')], 'e': [(10, 15, '10.15 a.m.'), (13, 45, '1.45 p.m.'), (17, 40, '5.40 p.m.')]}
for key, way in (('atc_w', 'w'), ('atc_e', 'e')):
    route, st = build(LINES[key])
    trips = []
    for h, m, txt in DEP[way]:
        t0 = h * 3600 + m * 60 - 3 * 3600; t1 = t0 + 1800
        trips.append(dict(id=f'ATC-{way.upper()}-{h:02d}{m:02d}', num='', name='Arnold Transit', svc='W_1111111', dir=0, stops=[[0, t0, t0, 1], [1, t1, t1, 1]], vessel='', note=NOTE[way].format(txt)))
    for s_ in st: s_.pop('key')
    NEW.append(dict(key=key, kind='v', label='Mackinac Island – St. Ignace (Arnold Transit)' if way == 'w' else 'St. Ignace – Mackinac Island (Arnold Transit)', mainline=True, water=True,
                    livery='atc', src=SRC, owner='atc', route=route, stations=st, dirLabels=['to ' + st[-1]['name'], ''], segments=[], trips=trips))
    print(f"{key}: {route[-1][2] / MI:.1f} mi of lane")
vd['lines'] = [x for x in vd['lines'] if x['key'] not in LINES] + NEW
open(os.path.join(HERE, 'viz_data.json'), 'w').write(json.dumps(vd, separators=(',', ':')))
def fmt(x): return f'{x // 3600:02d}:{x % 3600 // 60:02d}:{x % 60:02d}'
def app(name, rows_):
    with open(os.path.join(GT, name), 'a', newline='') as fh: csv.writer(fh).writerows(rows_)
def have(name, col=0): return set(r[col] for r in csv.reader(open(os.path.join(GT, name))))
if 'W_1111111' not in have('calendar.txt'): app('calendar.txt', [['W_1111111', *'1111111', '19490616', '19491231']])
if 'ATC' not in have('agency.txt'): app('agency.txt', [['ATC', 'Arnold Transit Company', 'https://en.wikipedia.org/wiki/Arnold_Transit_Company', 'America/Vancouver', 'en', '']])
gseen = have('stops.txt')
for L in NEW:
    st = L['stations']
    app('routes.txt', [['ATC_' + L['key'].upper(), 'ATC', L['label'], 'Arnold Transit', 4, '7A5C2E', 'FFFFFF',
                        'Arnold Transit Company, St. Ignace - Mackinac Island. The lane is a least-cost path over the water layers, not a surveyed course. Times on the Pacific clock.']])
    new = [[s['gid'], s['name'], f"{s['xy'][1]:.6f}", f"{s['xy'][0]:.6f}", s['note']] for s in st if s['gid'] not in gseen]
    app('stops.txt', new); gseen |= {r[0] for r in new}
    for t in L['trips']:
        app('shapes.txt', [[t['id'], f'{p[1]:.6f}', f'{p[0]:.6f}', k, f'{p[2]:.1f}'] for k, p in enumerate(L['route'])])
        app('trips.txt', [['ATC_' + L['key'].upper(), t['svc'], t['id'], st[t['stops'][-1][0]]['name'], 'Arnold Transit', 0, t['id']]])
        app('stop_times.txt', [[t['id'], fmt(a), fmt(b), st[i]['gid'], k, f"{st[i]['chain']:.1f}", 1] for k, (i, a, b, _) in enumerate(t['stops'], 1)])
