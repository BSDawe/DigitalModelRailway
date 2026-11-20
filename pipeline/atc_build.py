"""Arnold Transit Company: St. Ignace - Mackinac Island, Mackinaw City - Mackinac Island and Mackinac Island - Les Cheneaux Islands (Cedarville).
The May 1948 Official Guide (private repo scans/og1948_dssa/arnold_transit.png) prints only three St. Ignace sailings each way (an off-season list: two of its five columns
are blank) and no times for the Mackinaw City route (resumed June 1, 1948) or the Les Cheneaux route (to Coryell Island; resumed June 16, 1948). Brendan, 20 Nov 2026: use the
August 1950 Official Guide (scans/og1948_dssa/arnold_transit_og1950aug.png) for all three, as a stand-in for July 1948. Crossing times are not printed: 35 minutes St. Ignace and
40 minutes Mackinaw City, from the July 1958 Arnold Line brochure. Daily (Brendan). Docks (Brendan): Mackinac Island, the Arnold Dock (the D.&C. port, dcn_build.py); St. Ignace,
Dock No. 1; Mackinaw City, the State Ferry Dock (estimated); the Les Cheneaux Club landing; Cedarville. Water from the basemap tiles, as in gtwf_build.py. Run after dcn_build."""
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
NIP_BOX = (-84.80, -84.30, 45.76, 46.03)   # the Straits of Mackinac and the Les Cheneaux Islands
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
     'SIG': ('St. Ignace (Dock No. 1)', (-84.722672, 45.868471), 'St. Ignace, Dock No. 1 (Brendan, 20 Nov 2026)', 1),
     'MCD': ('Mackinaw City (State Ferry Dock)', (-84.721967, 45.781418), 'Mackinaw City, the State Ferry Dock (Brendan, 20 Nov 2026: estimated)', 1),
     'LCC': ('Les Cheneaux Club', (-84.395544, 45.990478), 'Les Cheneaux Club landing (Brendan, 20 Nov 2026)', 1),
     'CED': ('Cedarville', (-84.360068, 45.995288), 'Cedarville dock (Brendan, 20 Nov 2026)', 1)}
def gid(k): return 'PORT_' + re.sub(r'\W+', '_', P[k][0].upper()).strip('_')
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
SRC = ('Arnold Transit Company, Official Guide, August 1950 (Brendan, 20 Nov 2026; private repo scans/og1948_dssa/arnold_transit_og1950aug.png), standing in for July 1948: '
       'the May 1948 Guide prints three St. Ignace sailings and no times for the Mackinaw City and Les Cheneaux routes (resumed June 1 and June 16, 1948). '
       'Crossing times from the July 1958 Arnold Line brochure. Shown on the Pacific clock')
def T(s_):
    h, m = map(int, s_[:-1].split('.')); h = h % 12 + (12 if s_[-1] == 'p' else 0); return h * 3600 + m * 60 - 3 * 3600   # Eastern to Pacific
def txt(s_): return s_[:-1] + (' a.m.' if s_[-1] == 'a' else ' p.m.')
# key: (label, stops, [(times at each stop, ...)], note) - a single time at the first stop plus a running time, or a time at every stop
ROUTES = {
  'atc_w':  ('Mackinac Island – St. Ignace (Arnold Transit)', ['MAC', 'SIG'], [(t, 35) for t in ('7.55a', '10.15a', '12.30p', '3.15p', '5.15p')]),
  'atc_e':  ('St. Ignace – Mackinac Island (Arnold Transit)', ['SIG', 'MAC'], [(t, 35) for t in ('9.00a', '11.15a', '1.30p', '4.15p', '6.15p')]),
  'atc_mc': ('Mackinac Island – Mackinaw City (Arnold Transit)', ['MAC', 'MCD'], [(t, 40) for t in ('10.15a', '12.15p', '2.15p', '5.00p', '8.00p')]),
  'atc_cm': ('Mackinaw City – Mackinac Island (Arnold Transit)', ['MCD', 'MAC'], [(t, 40) for t in ('9.00a', '11.15a', '1.15p', '3.15p', '6.45p')]),
  'atc_lc': ('Mackinac Island – Les Cheneaux Islands (Arnold Transit)', ['MAC', 'LCC', 'CED'], [('1.15p', '3.05p', '3.40p')]),
  'atc_cl': ('Les Cheneaux Islands – Mackinac Island (Arnold Transit)', ['CED', 'LCC', 'MAC'], [('3.45p', '4.20p', '6.15p')]),
}
LINES = {k: v[1] for k, v in ROUTES.items()}
for key, (label, seq, sched) in ROUTES.items():
    route, st = build(seq)
    trips = []
    for row in sched:
        if isinstance(row[1], int): ts = [T(row[0]), T(row[0]) + row[1] * 60]; run = f'; crossing {row[1]} minutes (the 1958 brochure)'
        else: ts = [T(x) for x in row]; run = ''
        stops_txt = ', '.join(f"{P[k][0]} {txt(x)}" for k, x in zip(seq, row)) if not run else f"leaves {P[seq[0]][0]} {txt(row[0])}"
        note = (f'Arnold Transit Company, {label.split(" (")[0]}: {stops_txt} (Eastern time{run}). Daily. August 1950 Official Guide times, standing in for July 1948'
                + ('; stops on signal at landings between Hessel and Cedarville; the 1948 Guide names Coryell Island as the end of the route' if key in ('atc_lc', 'atc_cl') else '')
                + '. Shown in Pacific time.')
        trips.append(dict(id=f'ATC-{key[4:].upper()}-{ts[0] // 3600 + 3:02d}{ts[0] % 3600 // 60:02d}', num='', name='Arnold Transit', svc='W_1111111', dir=0,
                          stops=[[i, t, t, 1] for i, t in enumerate(ts)], vessel='M.S. Ottawa (1958)' if key in ('atc_lc', 'atc_cl') else '', note=note))
    for s_ in st: s_.pop('key')
    NEW.append(dict(key=key, kind='v', label=label, mainline=True, water=True, livery='atc', src=SRC, owner='atc', route=route, stations=st,
                    dirLabels=['to ' + st[-1]['name'], ''], segments=[], trips=trips))
    print(f"{key}: {route[-1][2] / MI:.1f} mi of lane, {len(trips)} trips")
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
                        'Arnold Transit Company (August 1950 Official Guide times, standing in for July 1948). The lane is a least-cost path over the water layers, not a surveyed course. Times on the Pacific clock.']])
    new = [[s['gid'], s['name'], f"{s['xy'][1]:.6f}", f"{s['xy'][0]:.6f}", s['note']] for s in st if s['gid'] not in gseen]
    app('stops.txt', new); gseen |= {r[0] for r in new}
    for t in L['trips']:
        app('shapes.txt', [[t['id'], f'{p[1]:.6f}', f'{p[0]:.6f}', k, f'{p[2]:.1f}'] for k, p in enumerate(L['route'])])
        app('trips.txt', [['ATC_' + L['key'].upper(), t['svc'], t['id'], st[t['stops'][-1][0]]['name'], 'Arnold Transit', 0, t['id']]])
        app('stop_times.txt', [[t['id'], fmt(a), fmt(b), st[i]['gid'], k, f"{st[i]['chain']:.1f}", 1] for k, (i, a, b, _) in enumerate(t['stops'], 1)])
