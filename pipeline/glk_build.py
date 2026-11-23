"""Two summer excursion lines of 1948, from their Official Guide pages (Brendan, 23 Nov 2026). Times printed in DAYLIGHT time, shown an hour earlier (standard time, like the
railways), then on the Pacific clock. Copies gtwf_build.py / wmsc_build.py.
Cleveland & Buffalo Steamship Co. (the C. & B. Line), Chicago: daily service June 20 through Labor Day, 1948 (Central "Daylight Saving" time):
  Monday and Friday only, Chicago - Michigan City: lv. Chicago 9.30 a.m., ar. Michigan City 1.00 p.m.; lv. Michigan City 4.30 p.m., ar. Chicago 7.30 p.m.
  Daily except Monday and Friday, Chicago - St. Joseph - Benton Harbor: lv. Chicago 9.30 a.m., ar. St. Joseph 1.30 p.m., ar. Benton Harbor 1.45 p.m.;
    lv. Benton Harbor 4.15 p.m., lv. St. Joseph 4.30 p.m., ar. Chicago 8.45 p.m.
  Chicago evening lake cruises nightly (Mon. and Fri. 8.30 - 11.30 p.m.; other nights 9.30 p.m. - 12.30 a.m.; Saturday 9.30 p.m. - 1.00 a.m.): NOT drawn (no destination).
  Wharves: south-east corner of the Michigan Avenue Bridge, Chicago; Central Docks, Benton Harbor. Ship not named on the page.
Ashley & Dustin Steamer Line, the "Put-in-Bay Route", Detroit - Put-in-Bay - Cedar Point: steamer Put-in-Bay (2,500 passengers), June 1 - September 1, 1948 (Eastern
"Daylight Saving" time):
  Wednesday and Sunday: lv. Detroit 9.30 a.m., ar. Put-in-Bay 1.00 p.m., lv. 1.00 p.m., ar. Cedar Point 2.30 p.m.; lv. Cedar Point 5.00 p.m., ar. Put-in-Bay 6.30 p.m., lv. 6.30 p.m., ar. Detroit 10.30 p.m.
  Tuesday, Toledo: lv. Toledo 8.30 a.m., ar. Cedar Point 1.00 p.m.; lv. Cedar Point 4.00 p.m., ar. Toledo 8.30 p.m.
  Thursday and Friday, Put-in-Bay: lv. Detroit 9.30 a.m., ar. Put-in-Bay 1.00 p.m.; lv. Put-in-Bay 4.00 p.m., ar. Detroit 7.45 p.m.
  Saturday, Blue Water Bridge cruise: lv. Detroit 9.30 a.m., ar. Detroit 5.00 p.m. (drawn to the bridge and back; the turn at 1.15 p.m. is Claude's estimate).
  The Monday and Tuesday-night positioning runs Detroit - Toledo - Detroit are not printed (not drawn). Dock points APPROXIMATE (Claude); the Detroit dock is not printed.
Colours (C. & B. #3d5a80, A. & D. #8a3b12) are Claude's picks. Run after wmsc_build."""
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
BOXES = [(-87.75, -86.35, 41.60, 42.25),    # the south end of Lake Michigan: Chicago, Michigan City, St. Joseph - Benton Harbor
         (-83.62, -82.30, 41.35, 43.05)]    # Lake Erie's west end, the Detroit River, Lake St. Clair and the St. Clair River to the Blue Water Bridge
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
for _B in BOXES:
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


A = ' (approximate)'
P = {'CHI': ('Chicago (Michigan Avenue Bridge)', (-87.6240, 41.8885), 'Chicago, the C. & B. Line wharf at the south-east corner of the Michigan Avenue Bridge' + A, 1),
     'MCY': ('Michigan City', (-86.9040, 41.7275), 'Michigan City, Ind., the harbour' + A, 1),
     'SJO': ('St. Joseph', (-86.4830, 42.1100), 'St. Joseph, Mich., the harbour' + A, 1),
     'BHB': ('Benton Harbor (Central Docks)', (-86.4600, 42.1170), 'Benton Harbor, Mich., the Central Docks' + A, 1),
     'DET': ('Detroit (Ashley & Dustin dock)', (-83.0510, 42.3270), 'Detroit, the Ashley & Dustin dock (not printed; Claude\'s estimate)', 1),
     'PIB': ('Put-in-Bay', (-82.8195, 41.6535), 'Put-in-Bay, South Bass Island, the steamer dock' + A, 1),
     'CPT': ('Cedar Point', (-82.6850, 41.4825), 'Cedar Point (Sandusky), the steamer pier' + A, 1),
     'TOL': ('Toledo', (-83.5320, 41.6560), 'Toledo, the Maumee River docks' + A, 1),
     'BWB': ('Blue Water Bridge (cruise turning point)', (-82.4230, 42.9990), 'The Blue Water Bridge, Port Huron - Sarnia: the Saturday cruise turns here without landing (turning time estimated)', 0)}
def gid(k): return 'PORT_' + re.sub(r'\W+', '_', P[k][0].split(' (')[0].upper()).strip('_') + {'CHI': '_CB', 'DET': '_AD'}.get(k, '')
LINES = {'cbs_bh': ['CHI', 'SJO', 'BHB'], 'cbs_bhr': ['BHB', 'SJO', 'CHI'], 'cbs_mc': ['CHI', 'MCY'], 'cbs_mcr': ['MCY', 'CHI'],
         'ads_out': ['DET', 'PIB', 'CPT'], 'ads_back': ['CPT', 'PIB', 'DET'], 'ads_tol': ['TOL', 'CPT'], 'ads_tolr': ['CPT', 'TOL'], 'ads_bw': ['DET', 'BWB'], 'ads_bwr': ['BWB', 'DET']}
_CF = os.path.join(HERE, 'glk_legs.json'); CACHE = json.load(open(_CF)) if os.path.exists(_CF) else {}
def sealeg(p, q):
    d = math.dist(fwd(*p), fwd(*q)); res = 60 if d < 40000 else 120 if d < 150000 else 250
    ck = f'{SEA_VERSION}|{p[0]:.4f},{p[1]:.4f}|{q[0]:.4f},{q[1]:.4f}|{res}'
    rk = f'{SEA_VERSION}|{q[0]:.4f},{q[1]:.4f}|{p[0]:.4f},{p[1]:.4f}|{res}'
    if ck not in CACHE and rk in CACHE: return [tuple(x) for x in CACHE[rk][::-1]]   # the return sailing on the same lane, reversed
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
H = 3600
LINE_INFO = {'cbs': ('C. & B. Line', 'Cleveland & Buffalo Steamship Co. (C. & B. Line), Chicago: daily service June 20 through Labor Day, 1948, Official Guide (Brendan, 23 Nov 2026); printed in Central daylight time, shown in standard time on the Pacific clock', 'cbs', 'CBS', '3D5A80', -2 * H, ''),
             'ads': ('Put-in-Bay Route', 'Ashley & Dustin Steamer Line, the Put-in-Bay Route: 1948 schedule, June 1 - September 1, Official Guide (Brendan, 23 Nov 2026); printed in Eastern daylight time, shown in standard time on the Pacific clock', 'ads', 'ADS', '8A3B12', -3 * H, 'Put-in-Bay')}
# trips: line, days Mon..Sun, [(station index, arrive, depart) as printed, h.mm daylight], note
T = lambda x: int(x) * H + round((x - int(x)) * 100) * 60
TRIPS = [('cbs_bh', '0111011', [(0, None, 9.30), (1, 13.30, 13.30), (2, 13.45, None)], 'Chicago 9.30 a.m. to St. Joseph 1.30 p.m. and Benton Harbor 1.45 p.m., daily except Monday and Friday'),
         ('cbs_bhr', '0111011', [(0, None, 16.15), (1, 16.30, 16.30), (2, 20.45, None)], 'Benton Harbor 4.15 p.m., St. Joseph 4.30 p.m., to Chicago 8.45 p.m., daily except Monday and Friday'),
         ('cbs_mc', '1000100', [(0, None, 9.30), (1, 13.00, None)], 'Chicago 9.30 a.m. to Michigan City 1.00 p.m., Monday and Friday only'),
         ('cbs_mcr', '1000100', [(0, None, 16.30), (1, 19.30, None)], 'Michigan City 4.30 p.m. to Chicago 7.30 p.m., Monday and Friday only'),
         ('ads_out', '0010001', [(0, None, 9.30), (1, 13.00, 13.00), (2, 14.30, None)], 'Detroit 9.30 a.m., Put-in-Bay 1.00 p.m., Cedar Point 2.30 p.m., Wednesday and Sunday'),
         ('ads_back', '0010001', [(0, None, 17.00), (1, 18.30, 18.30), (2, 22.30, None)], 'Cedar Point 5.00 p.m., Put-in-Bay 6.30 p.m., Detroit 10.30 p.m., Wednesday and Sunday'),
         ('ads_out', '0001100', [(0, None, 9.30), (1, 13.00, None)], 'Detroit 9.30 a.m. to Put-in-Bay 1.00 p.m., Thursday and Friday'),
         ('ads_back', '0001100', [(1, None, 16.00), (2, 19.45, None)], 'Put-in-Bay 4.00 p.m. to Detroit 7.45 p.m., Thursday and Friday'),
         ('ads_tol', '0100000', [(0, None, 8.30), (1, 13.00, None)], 'Toledo 8.30 a.m. to Cedar Point 1.00 p.m., Tuesday'),
         ('ads_tolr', '0100000', [(0, None, 16.00), (1, 20.30, None)], 'Cedar Point 4.00 p.m. to Toledo 8.30 p.m., Tuesday'),
         ('ads_bw', '0000010', [(0, None, 9.30), (1, 13.15, None)], 'Saturday Blue Water Bridge cruise: Detroit 9.30 a.m., up the Detroit and St. Clair rivers to the bridge (turn estimated)'),
         ('ads_bwr', '0000010', [(0, None, 13.15), (1, 17.00, None)], 'Saturday Blue Water Bridge cruise: back down the rivers to Detroit 5.00 p.m.')]
LABEL = {'cbs_bh': 'Chicago – St. Joseph – Benton Harbor (C. & B. Line)', 'cbs_bhr': 'Benton Harbor – St. Joseph – Chicago (C. & B. Line)', 'cbs_mc': 'Chicago – Michigan City (C. & B. Line)',
         'cbs_mcr': 'Michigan City – Chicago (C. & B. Line)', 'ads_out': 'Detroit – Put-in-Bay – Cedar Point (steamer Put-in-Bay)', 'ads_back': 'Cedar Point – Put-in-Bay – Detroit (steamer Put-in-Bay)',
         'ads_tol': 'Toledo – Cedar Point (steamer Put-in-Bay)', 'ads_tolr': 'Cedar Point – Toledo (steamer Put-in-Bay)', 'ads_bw': 'Detroit – Blue Water Bridge cruise (steamer Put-in-Bay)',
         'ads_bwr': 'Blue Water Bridge cruise – Detroit (steamer Put-in-Bay)'}
for key, seq in LINES.items():
    co = key.split('_')[0]; nm, src, liv, ag, col, shift, ves = LINE_INFO[co]
    route, st = build(seq)
    trips = []
    for n, (k2, days, sts, txt) in enumerate(t for t in TRIPS if t[0] == key):
        stops = []
        for i, a, d in sts:
            a = T(a - 1) + shift if a is not None else None; d = T(d - 1) + shift if d is not None else None   # daylight to standard: an hour earlier
            stops.append([i, a if a is not None else d, d if d is not None else a, 1])
        dd = days
        if stops[0][2] < 0:
            for s in stops: s[1] += 86400; s[2] += 86400
            dd = days[1:] + days[0]
        trips.append(dict(id=f'{ag}-{key.upper()}-{dd}', num='', name=ves or nm, svc='W_' + dd, dir=0, stops=stops, vessel=ves,
                          note=f'{nm}: {txt} (daylight time, as printed). Summer 1948. Shown in Pacific (standard) time.'))
    for s in st: s.pop('key')
    NEW.append(dict(key=key, kind='v', label=LABEL[key], mainline=True, water=True, livery=liv, src=src, owner=liv, route=route, stations=st, dirLabels=['to ' + st[-1]['name'], ''], segments=[], trips=trips))
    print(f"{key}: {route[-1][2] / MI:.1f} mi of lane, {len(trips)} trips")
vd['lines'] = [x for x in vd['lines'] if x['key'] not in LINES] + NEW
open(os.path.join(HERE, 'viz_data.json'), 'w').write(json.dumps(vd, separators=(',', ':')))

def fmt(x): return f'{x // 3600:02d}:{x % 3600 // 60:02d}:{x % 60:02d}'
def app(name, rows_):
    with open(os.path.join(GT, name), 'a', newline='') as fh: csv.writer(fh).writerows(rows_)
def have(name, col=0): return set(r[col] for r in csv.reader(open(os.path.join(GT, name))))
cal = have('calendar.txt')
for d in sorted({t['svc'] for L in NEW for t in L['trips']} - cal):
    app('calendar.txt', [[d, *d[2:], '19490616', '19491231']]); cal.add(d)
ags = have('agency.txt')
for ag, an, url in (('CBS', 'Cleveland & Buffalo Steamship Company (C. & B. Line)', 'https://en.wikipedia.org/wiki/Cleveland_and_Buffalo_Transit_Company'),
                    ('ADS', 'Ashley & Dustin Steamer Line', 'https://en.wikipedia.org/wiki/Ashley_%26_Dustin_Steamer_Line')):
    if ag not in ags: app('agency.txt', [[ag, an, url, 'America/Vancouver', 'en', '']])
gseen = have('stops.txt')
for L in NEW:
    st = L['stations']; nm, src, liv, ag, col, shift, ves = LINE_INFO[L['key'].split('_')[0]]
    app('routes.txt', [[ag + '_' + L['key'].upper(), ag, L['label'], nm, 4, col, 'FFFFFF',
                        src + '. The lane is a least-cost path over the water layers, not a surveyed course.']])
    new = [[s['gid'], s['name'], f"{s['xy'][1]:.6f}", f"{s['xy'][0]:.6f}", s['note']] for s in st if s['gid'] not in gseen]
    app('stops.txt', new); gseen |= {r[0] for r in new}
    for t in L['trips']:
        app('shapes.txt', [[t['id'], f'{p[1]:.6f}', f'{p[0]:.6f}', k, f'{p[2]:.1f}'] for k, p in enumerate(L['route'])])
        app('trips.txt', [[ag + '_' + L['key'].upper(), t['svc'], t['id'], st[t['stops'][-1][0]]['name'], ves or nm, 0, t['id']]])
        app('stop_times.txt', [[t['id'], fmt(a), fmt(b), st[i]['gid'], k, f"{st[i]['chain']:.1f}", 1] for k, (i, a, b, _) in enumerate(t['stops'], 1)])
