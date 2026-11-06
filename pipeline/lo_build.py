"""Lake Ontario boats (Brendan, 5 November 2026): the Canadian National steamers Toronto - Port Dalhousie (S.S. Dalhousie City and S.S. Northumberland,
meeting the Niagara, St. Catharines & Toronto cars at Port Dalhousie) and the Ontario Car Ferry Co. (CN and Baltimore & Ohio) S.S. Ontario, Cobourg - Genesee
Docks (port of Rochester, N.Y.).

Source: the May 1948 Official Guide, beside the NS&T tables (dmr-sources scans/og1948_cnq/nst_cn_steamers_condensed.png).
Steamers, "Schedule effective May 21 until June 4, inclusive", 32 miles, printed in Daylight Saving time (shown here in standard time, an hour earlier):
leave Port Dalhousie double-dagger 8.30 a.m. (daily except Saturday), ) 11.05, disc 11.05 a.m., k 4.45 (Saturday), disc 6.30, k 10.05 p.m., (May 23 only) 12.00 night;
leave Toronto disc 8.15 a.m., disc 2.00, k 2.00, square 5.45 (Friday, and May 31), k 7.30, disc 9.30 p.m. Signs (the page's footnotes, Brendan): disc Sunday
and May 24 only, ) Monday May 31 only (left out), square Friday and May 31 only, k Saturday only, double dagger daily except Saturday. Crossing 2 h 30 min,
estimated from the Saturday turns (Toronto 2.00, Port Dalhousie 4.45, Toronto 7.30, Port Dalhousie 10.05). Which ship makes which sailing is estimated (two
ships on Sundays). The 12.00 night sailing of May 23 only is left out.
Car ferry, "Ontario Car Ferry Service between Cobourg, Ont., and Genesee Docks (Port of Rochester)", Eastern time: summer service daily June 30 - Sept. 12
(spring: Sunday, Monday, Thursday and Saturday from May 29): Genesee Docks 8.00 a.m., Cobourg 1.00 p.m.; Cobourg 3.00 p.m., Genesee Docks 8.00 p.m.
Points (Brendan): Toronto CN wharf, Port Dalhousie = the CN (Welland Railway) station point, Cobourg CN wharf, Genesee Docks. Water: Brendan's basemap tiles
and the Great Lakes layer (water_east.json, for the United States side). Times shown on the Pacific clock. Run after on_build."""
import csv, json, math, os, re
from shapely.geometry import MultiPolygon, Polygon
from shapely.ops import unary_union
from nrwn_graph import fwd, MI
import sea
from sea import Sea, SEA_VERSION
HERE = os.path.dirname(os.path.abspath(__file__)); GT = os.path.join(HERE, 'gtfs'); ROOT = os.path.dirname(HERE)
vd = json.load(open(os.path.join(HERE, 'viz_data.json')))
BOX = (-79.50, -77.45, 43.10, 44.05)

# ---------------- water: the basemap tiles (page projection) back to lon/lat, and water_east.json
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
_xs, _ys = zip(*[page_xy(lon, lat) for lon in BOX[:2] for lat in BOX[2:]])
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
for poly in json.load(open(os.path.join(HERE, 'water_east.json'))):
    rings = []
    for r in poly:
        lon, lat = r[0], r[1]; pts = [(lon / 1e4, lat / 1e4)]
        for i in range(2, len(r), 2): lon += r[i]; lat += r[i + 1]; pts.append((lon / 1e4, lat / 1e4))
        rings.append(pts)
    if not any(BOX[0] - 0.5 <= x <= BOX[1] + 0.5 and BOX[2] - 0.5 <= y <= BOX[3] + 0.5 for x, y in rings[0]): continue
    g = Polygon([sea.to_xy(*p) for p in rings[0]], [[sea.to_xy(*p) for p in h] for h in rings[1:]]); _polys.append(g if g.is_valid else g.buffer(0))
sea._U = unary_union(_polys)
if sea._U.geom_type == 'Polygon': sea._U = MultiPolygon([sea._U])

# ---------------- ports (Brendan's points)
def gid(n): return 'PORT_' + re.sub(r'\W+', '_', n.upper()).strip('_')
def port(n, lon, lat, note): return dict(name=n, gid=gid(n), lon=lon, lat=lat, note=note)
TOR = port('Toronto (C.N.R. Wharf)', -79.37373709478712, 43.64070298018153, 'Canadian National wharf, Toronto harbour (Brendan)')
PDH = port('Port Dalhousie (C.N.R.)', -79.2625135, 43.2029713, 'Port Dalhousie: the CN (Welland Railway) station point, by the harbour; the NS&T cars at Lakeside Park, steps away (Brendan)')
COB = port('Cobourg (C.N.R. Wharf)', -78.1658271688718, 43.95537172092824, 'Canadian National wharf, Cobourg harbour (Brendan)')
GEN = port('Genesee Docks (Rochester)', -77.61655318811175, 43.22746248913674, 'Genesee Docks, Port of Rochester, N.Y., on the Genesee River (Brendan)')

# ---------------- lanes (cache lo_legs.json)
_CF = os.path.join(HERE, 'lo_legs.json'); CACHE = json.load(open(_CF)) if os.path.exists(_CF) else {}
def lane(p, q, res):
    ck = f'{SEA_VERSION}|{p[0]:.5f},{p[1]:.5f}|{q[0]:.5f},{q[1]:.5f}|{res}'
    if ck not in CACHE:
        d = math.dist(fwd(*p), fwd(*q)); S = Sea([p, q], res=res, margin=max(8000.0, 0.3 * d)); leg, land = S.leg(p, q)
        CACHE[ck] = [[round(x, 6), round(y, 6)] for x, y in leg]
        print(f'   lane {p[0]:.4f},{p[1]:.4f} - {q[0]:.4f},{q[1]:.4f}: over {land * 100:.1f}% land; snaps {S.snap_m(p):.0f} / {S.snap_m(q):.0f} m')
    return [tuple(x) for x in CACHE[ck]]
def chain(pts):
    route, acc, prev = [], 0.0, None
    for lon, lat in pts:
        xy = fwd(lon, lat)
        if prev: acc += math.dist(xy, prev)
        prev = xy; route.append([round(lon, 6), round(lat, 6), round(acc, 1)])
    return route
def water_line(a, b, res, via=()):
    seq = [(a['lon'], a['lat'])] + list(via) + [(b['lon'], b['lat'])]; pts = [seq[0]]
    for p, q in zip(seq, seq[1:]): pts += lane(p, q, res)[1:] + [q]
    route = chain(pts)
    st = [dict(name=p['name'], chain=route[i][2], lon=route[i][0], lat=route[i][1], mile=round(route[i][2] / MI, 1), lmile=round(route[i][2] / MI, 1), principal=True, kml='',
               gid=p['gid'], xy=[p['lon'], p['lat']], note=p['note']) for p, i in ((a, 0), (b, len(route) - 1))]
    return route, st
pd_route, pd_st = water_line(TOR, PDH, 120, [(-79.3600, 43.6375), (-79.3445, 43.6325), (-79.3380, 43.6260)])   # out of Toronto harbour by the Eastern Gap (the water layer lacks the Toronto Islands)
cf_route, cf_st = water_line(COB, GEN, 200)
json.dump(CACHE, open(_CF, 'w'))

# ---------------- times
def hm(txt):
    m = re.match(r'(\d+)\.(\d+)([ap])', txt); h, mn = int(m.group(1)), int(m.group(2))
    if m.group(3) == 'p' and h != 12: h += 12
    if m.group(3) == 'a' and h == 12: h = 0
    return h * 3600 + mn * 60
DST, EST = 4 * 3600, 3 * 3600          # printed daylight time: an hour to standard, three more to the Pacific clock; printed Eastern (standard): three
SVC = {'Sun': 'W_0000001', 'xSat': 'W_1111101', 'Sat': 'W_0000010', 'Fri': 'W_0000100', 'daily': 'W_1111111'}
DAYS = {'Sun': 'Sunday (and May 24)', 'xSat': 'daily except Saturday', 'Sat': 'Saturday', 'Fri': 'Friday (and May 31)', 'daily': 'daily'}
CROSS = 150 * 60
def ptxt(t): return f"{t // 3600 % 12 or 12}.{t % 3600 // 60:02d} {'p.m.' if t % 86400 >= 43200 else 'a.m.'}"
_s = (' Canadian National steamer service Toronto - Port Dalhousie (32 miles), May 21 to June 4, 1948 (Official Guide); for the NS&T cars to St. Catharines at Port'
      ' Dalhousie. Printed in Daylight Saving time; the crossing (2 h 30 min) and the ship on each sailing estimated.')
STEAM = [  # (from, leave as printed, days, vessel, sign as printed)
    ('P', '8.30a', 'xSat', 'Dalhousie City', 'double dagger'), ('P', '11.05a', 'Sun', 'Northumberland', 'disc'), ('P', '4.45p', 'Sat', 'Dalhousie City', 'k'),
    ('P', '6.30p', 'Sun', 'Dalhousie City', 'disc'), ('P', '10.05p', 'Sat', 'Dalhousie City', 'k'),
    ('T', '8.15a', 'Sun', 'Northumberland', 'disc'), ('T', '2.00p', 'Sun', 'Dalhousie City', 'disc'), ('T', '2.00p', 'Sat', 'Dalhousie City', 'k'),
    ('T', '5.45p', 'Fri', 'Dalhousie City', 'square'), ('T', '7.30p', 'Sat', 'Dalhousie City', 'k'), ('T', '9.30p', 'Sun', 'Northumberland', 'disc')]
LINES = []
def mkline(key, label, route, st, trips, labels, src, livery):
    LINES.append(dict(key=key, kind='v', label=label, mainline=True, water=True, livery=livery, src=src, owner='cn', route=route, stations=st, dirLabels=labels, segments=[], trips=trips))
    print(f'{key}: {label}, {route[-1][2] / MI:.1f} mi, {len(trips)} sailings')
T = []
for k, (fr, lv, dy, ves, sg) in enumerate(STEAM):
    d = 0 if fr == 'T' else 1; t = hm(lv) - DST; i0, i1 = (0, 1) if d == 0 else (1, 0)
    a, b = pd_st[i0]['name'], pd_st[i1]['name']
    T.append(dict(id=f'LOPD-{fr}{lv.replace(".", "")}{dy}', num=ves, name='C.N. steamer', svc=SVC[dy], dir=d, vessel=ves, stops=[[i0, t, t, 1], [i1, t + CROSS, t + CROSS, 0]],
                  note=f'S.S. {ves}: {a} {ptxt(hm(lv) - 3600)} standard time ({lv[:-1]} {"a.m." if lv[-1] == "a" else "p.m."} daylight time as printed, sign {sg}: {DAYS[dy]}) to {b}.' + _s))
mkline('lopd', 'Toronto – Port Dalhousie (C.N. steamers)', pd_route, pd_st, T, ['to Port Dalhousie', 'to Toronto'],
       'Canadian National steamer service, Toronto - Port Dalhousie: the May 1948 Official Guide (Brendan); daylight time printed, shown in standard time', 'cnss')
_f = (' Ontario Car Ferry Co. (Canadian National and Baltimore & Ohio), summer service daily June 30 - Sept. 12, 1948 (spring: Sun., Mon., Thu. and Sat. from May 29).'
      ' Printed in Eastern time; carries railway cars and passengers.')
CF = [dict(id='LOCF-N', num='Ontario', name='Car ferry', svc=SVC['daily'], dir=1, vessel='Ontario', stops=[[1, hm('8.00a') - EST, hm('8.00a') - EST, 1], [0, hm('1.00p') - EST, hm('1.00p') - EST, 1]],
           note='S.S. Ontario: Genesee Docks (port of Rochester, N.Y.) 8.00 a.m. to Cobourg 1.00 p.m.' + _f),
      dict(id='LOCF-S', num='Ontario', name='Car ferry', svc=SVC['daily'], dir=0, vessel='Ontario', stops=[[0, hm('3.00p') - EST, hm('3.00p') - EST, 1], [1, hm('8.00p') - EST, hm('8.00p') - EST, 1]],
           note='S.S. Ontario: Cobourg 3.00 p.m. to Genesee Docks (port of Rochester, N.Y.) 8.00 p.m.' + _f)]
mkline('locf', 'Cobourg – Genesee Docks (Ontario Car Ferry Co.)', cf_route, cf_st, CF, ['to Rochester', 'to Cobourg'],
       'Ontario Car Ferry Co. (CN and B&O), Cobourg - Genesee Docks: the May 1948 Official Guide (Brendan); Eastern time as printed', 'cnss')
for L in LINES:
    for t in L['trips']:
        (i, a, b, _), (j, a2, b2, _) = t['stops']; leg = abs(L['stations'][j]['chain'] - L['stations'][i]['chain']) / MI; h = (a2 - b) / 3600
        assert a >= 0 and a2 > b, t['id']
        if not 7 < leg / h < 18: print(f"  {t['id']}: {leg:.1f} mi in {h:.2f} h = {leg / h:.1f} mph  !! check")
keys = {L['key'] for L in LINES}
vd['lines'] = [x for x in vd['lines'] if x['key'] not in keys] + LINES
open(os.path.join(HERE, 'viz_data.json'), 'w').write(json.dumps(vd, separators=(',', ':')))

# ---------------- GTFS (ferry, route type 4)
def fmt(x): return f'{x // 3600:02d}:{x % 3600 // 60:02d}:{x % 60:02d}'
def app(name, rows_):
    with open(os.path.join(GT, name), 'a', newline='') as fh: csv.writer(fh).writerows(rows_)
def have(name, col=0): return set(r[col] for r in csv.reader(open(os.path.join(GT, name))))
cal = have('calendar.txt'); app('calendar.txt', [[w, *w[2:], '19490616', '19491231'] for w in sorted({t['svc'] for L in LINES for t in L['trips']}) if w not in cal])
if 'OCF' not in have('agency.txt'): app('agency.txt', [['OCF', 'Ontario Car Ferry Company (Canadian National and Baltimore & Ohio)', 'https://en.wikipedia.org/wiki/SS_Ontario_No._1', 'America/Vancouver', 'en', '']])
gseen = have('stops.txt')
for L, ag, desc in ((LINES[0], 'CN', 'Canadian National steamers, May 21 - June 4, 1948. Times on the Pacific clock (printed in Eastern Daylight Saving time).'),
                    (LINES[1], 'OCF', 'S.S. Ontario, summer service. Times on the Pacific clock, three hours earlier than the Eastern time printed.')):
    rid = L['key'].upper(); st = L['stations']
    app('routes.txt', [[rid, ag, L['label'], ' – '.join(s['name'] for s in st), 4, '2F6B44', 'FFFFFF', desc]])
    new = [[s['gid'], s['name'] + ' (steamer landing)', f"{s['lat']:.6f}", f"{s['lon']:.6f}", s['note']] for s in st if s['gid'] not in gseen]
    gseen |= {r[0] for r in new}; app('stops.txt', new)
    for t in L['trips']:
        i0, i1 = t['stops'][0][0], t['stops'][-1][0]
        pts_ = L['route'] if i0 == 0 else L['route'][::-1]
        app('shapes.txt', [[t['id'], f'{p[1]:.6f}', f'{p[0]:.6f}', k, f'{abs(p[2] - pts_[0][2]):.1f}'] for k, p in enumerate(pts_)])
        app('trips.txt', [[rid, t['svc'], t['id'], st[i1]['name'], t['num'], t['dir'], t['id']]])
        app('stop_times.txt', [[t['id'], fmt(a_), fmt(b_), st[i]['gid'], k, f"{abs(st[i]['chain'] - st[i0]['chain']):.1f}", tp] for k, (i, a_, b_, tp) in enumerate(t['stops'], 1)])
