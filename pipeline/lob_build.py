"""Huntsville and Lake of Bays Navigation Co. (Brendan, 5 November 2026): the S.S. Algonquin (Huntsville - Fairy Lake - Peninsula Lake - North Portage),
the Portage Flyer (the Huntsville and Lake of Bays Railway, North Portage - South Portage, with its switchback) and the S.S. Iroquois (South Portage -
Lake of Bays - Dorset), daily except Sunday.

Sources. The 1948 Official Guide, CN Table 126 (Brendan): Huntsville Dock steamers leave 8.00 a.m. (from train 47), arrive Dorset 12.45 p.m.; leave 3.25 p.m.
(from 55-53 and 41), arrive Dorset 8.00 p.m.; leave Dorset 6.30 a.m., arrive Huntsville 11.40 a.m. (for train 44); daily except Sunday. The calls and the
running pattern from the company's Summer Time Table, 1942 (Brendan; dmr-sources scans/marine/hlb_1942_summer.png). A MODEL day: those six printed times are
kept; the second sailing from Dorset (afternoon, as in 1942), the boats' meets at the Portages and every other time are estimated. Dwight and Glen Cove (a
private launch from South Portage) and Raymur Pines (no point) are left out.
Points: traces/ontario/brendan/lake_of_bays.kmz (Brendan); North and South Portage stations and the railway from the Ontario Railway Map Collection; the
Huntsville dock is the CN Huntsville station (Brendan: one station). The Flyer runs out to the end of the switchback spur south-west of North Portage and
backs from there (Brendan). Water for the lanes: Brendan's basemap tiles (basemap/tiles, level 8), which have these lakes; the pipeline water does not.
Times printed in Eastern Standard Time, shown on the Pacific clock (3 hours earlier). Run after on_build."""
import csv, json, math, os, re, zipfile
import xml.etree.ElementTree as ET
from shapely.geometry import MultiPolygon, Polygon, box
from shapely.ops import unary_union
from nrwn_graph import fwd, MI
import sea
from sea import Sea, SEA_VERSION
import on_lines
HERE = os.path.dirname(os.path.abspath(__file__)); GT = os.path.join(HERE, 'gtfs'); ROOT = os.path.dirname(HERE)
vd = json.load(open(os.path.join(HERE, 'viz_data.json')))
RAIL = {s['gid']: s for l in vd['lines'] for s in l['stations'] if s.get('gid') and not l.get('water')}
BOX = (-79.26, -78.86, 45.20, 45.38)

# ---------------- water for the lanes: the basemap tiles (page projection) back to lon/lat, then the lanes' projection
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
sea._U = unary_union(_polys)
if sea._U.geom_type == 'Polygon': sea._U = MultiPolygon([sea._U])

# ---------------- points
_ns = {'k': 'http://www.opengis.net/kml/2.2'}
KMZ = {}
for pm in ET.fromstring(zipfile.ZipFile(os.path.join(HERE, 'traces', 'ontario', 'brendan', 'lake_of_bays.kmz')).read('doc.kml')).iter('{http://www.opengis.net/kml/2.2}Placemark'):
    c = pm.find('.//k:coordinates', _ns)
    if c is None: continue
    nm = re.sub(r'\s*\(Est\)\s*$', '', pm.find('k:name', _ns).text.strip()); x = c.text.strip().split(',')
    KMZ[nm] = (float(x[0]), float(x[1]))
ORMC = {}
for o in on_lines.pieces():
    if 'Huntsville and Lake of Bays' not in ' '.join(o['path']): continue
    if o['kind'] == 'Point' and o.get('name') in ('North Portage station', 'South Portage station'):
        c = o['coords'][0] if isinstance(o['coords'][0], list) else o['coords']; ORMC[o['name']] = (c[0], c[1])
    if o['kind'] == 'LineString' and (o.get('desc') or '').startswith('When completed in 1905'): FLYER = [tuple(p[:2]) for p in o['coords']]
NP, SP = ORMC['North Portage station'], ORMC['South Portage station']
def gid(n): return 'PORT_' + re.sub(r'\W+', '_', n.upper()).strip('_')
NOTE = {'Huntsville': 'Huntsville station dock: the CN Huntsville station (Brendan)', 'North Portage': 'North Portage station, Peninsula Lake (Huntsville and Lake of Bays Railway; Ontario Railway Map Collection)',
        'South Portage': 'South Portage station, Lake of Bays (Huntsville and Lake of Bays Railway; Ontario Railway Map Collection)', 'Sekani': 'Sekani (Brendan: position estimated)'}
def port(n, kmz=None):
    if n == 'Huntsville': r = RAIL['CN_HUNTSVILLE']; return dict(name=n, gid='CN_HUNTSVILLE', lon=r['lon'], lat=r['lat'], rail=True, note=NOTE[n])
    if n in ('North Portage', 'South Portage'): p = NP if n == 'North Portage' else SP; return dict(name=n, gid=gid(n), lon=p[0], lat=p[1], rail=True, note=NOTE[n])
    p = KMZ[kmz or n]; return dict(name=n, gid=gid(n), lon=p[0], lat=p[1], rail=False, note=NOTE.get(n, n + ' (Brendan)'))
ALG = [port('Huntsville'), port('Huntsville Town Dock'), port('Huntsville Memorial Park'), port('Haverland'), port('Grandview', 'Grandview'), port('Canal'), port('Deerhurst Inn'),
       port('Pow Wow Point'), port('Grassmere (Tally-Ho Inn)'), port('Winoka'), port('Isle Dunelg'), port('Sekani'), port('Springsyde'), port('North Portage')]
IRO = [port('South Portage'), port('Britannia'), port('Bona Vista'), port('Point Ideal'), port('Golf Grounds'), port('Robinsdale'), port('Clovelly', 'Clovellly'), port('Glenmount'),
       port('Bigwin Inn', 'Bigwin Is. (Bigwin Inn)'), port('Port Cunnington'), port('Fox Point'), port('Chevaliers'), port('Cliffdene'), port('Dorset')]

# ---------------- lanes (cache lob_legs.json)
_CF = os.path.join(HERE, 'lob_legs.json'); CACHE = json.load(open(_CF)) if os.path.exists(_CF) else {}
def lane(p, q, res):
    ck = f'{SEA_VERSION}|{p[0]:.5f},{p[1]:.5f}|{q[0]:.5f},{q[1]:.5f}|{res}'
    if ck not in CACHE:
        d = math.dist(fwd(*p), fwd(*q)); S = Sea([p, q], res=res, margin=max(2500.0, 0.4 * d)); leg, land = S.leg(p, q)
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
def water_line(ports, res):
    pts, at = [], []
    for k, p in enumerate(ports):
        if k == 0: pts.append((p['lon'], p['lat']))
        else:
            leg = lane((ports[k - 1]['lon'], ports[k - 1]['lat']), (p['lon'], p['lat']), res); pts += leg[1:] + [(p['lon'], p['lat'])]
        at.append(len(pts) - 1)
    route = chain(pts)
    return route, [dict(name=p['name'], chain=route[i][2], lon=route[i][0], lat=route[i][1], mile=round(route[i][2] / MI, 2), lmile=round(route[i][2] / MI, 2), principal=True, kml='',
                        gid=p['gid'], **({} if p['rail'] else {'xy': [p['lon'], p['lat']]}), note=p['note']) for p, i in zip(ports, at)]
alg_route, alg_st = water_line(ALG, 20)
iro_route, iro_st = water_line(IRO, 40)
json.dump(CACHE, open(_CF, 'w'))
# the Portage Flyer: the collection's line as drawn (North Portage, west to the end of the switchback spur, back, then down to South Portage)
_fr = chain(FLYER)
def _near(p): return min(range(len(_fr)), key=lambda i: math.dist(fwd(*p), fwd(_fr[i][0], _fr[i][1])))
_a, _b = _near(NP), _near(SP); fly_route = chain([tuple(x[:2]) for x in _fr[_a:_b + 1]])
fly_st = [dict(name=n, chain=fly_route[i][2], lon=fly_route[i][0], lat=fly_route[i][1], mile=round(fly_route[i][2] / MI, 2), lmile=round(fly_route[i][2] / MI, 2), principal=True, kml='',
               gid=gid(n), note=NOTE[n]) for n, i in (('North Portage', 0), ('South Portage', len(fly_route) - 1))]

# ---------------- times (Eastern Standard Time as printed; shown 3 hours earlier on the Pacific clock). '*' = printed in the 1948 Guide.
OFF = 3 * 3600
def hm(txt):
    m = re.match(r'(\d+)\.(\d+)([ap])', txt); h, mn = int(m.group(1)), int(m.group(2))
    if m.group(3) == 'p' and h != 12: h += 12
    if m.group(3) == 'a' and h == 12: h = 0
    return h * 3600 + mn * 60
def calls(st, seq, rev=False):
    """seq: 'time' per station in running order (one time = arrive and leave; 'a/b'; '*' printed)"""
    order = list(range(len(st)))[::-1] if rev else list(range(len(st)))
    assert len(seq) == len(order), (len(seq), len(order))
    out = []
    for i, tx in zip(order, seq):
        pr = int('*' in tx); tx = tx.replace('*', ''); a, b = (tx.split('/') + [tx])[:2]
        out.append([i, hm(a) - OFF, hm(b) - OFF, pr])
    assert all(y[1] >= x[2] for x, y in zip(out, out[1:])), out
    return out
SVC = 'W_1111110'
_m = (' Huntsville and Lake of Bays Navigation Co., daily except Sunday: a MODEL day. Printed in the 1948 Official Guide (CN Table 126): Huntsville dock 8.00 a.m. and 3.25 p.m.,'
      ' Dorset 12.45 p.m. and 8.00 p.m.; Dorset 6.30 a.m., Huntsville 11.40 a.m. The calls and the rest of the pattern from the company\'s 1942 summer timetable; the second sailing from'
      ' Dorset and every other time estimated. Most landings are flag calls (stop on arrangement). Eastern Standard Time, shown here three hours earlier on the Pacific clock.')
# each sailing: (leave, arrive); the landings between are timed in proportion to the distance along the lane (flag calls, no dwell)
A_DN1, A_DN2, A_UP1, A_UP2 = ('8.00a*', '9.35a'), ('3.25p*', '4.52p'), ('10.05a', '11.40a*'), ('5.00p', '6.35p')
I_DN1, I_DN2, I_UP1, I_UP2 = ('10.20a', '12.45p*'), ('5.30p', '8.00p*'), ('6.30a*', '9.30a'), ('1.15p', '4.15p')
def spread(st, ends, rev=False):
    order = list(range(len(st)))[::-1] if rev else list(range(len(st)))
    c0, c1 = st[order[0]]['chain'], st[order[-1]]['chain']; t0, t1 = hm(ends[0].rstrip('*')), hm(ends[1].rstrip('*'))
    seq = []
    for i in order:
        t = t0 + (t1 - t0) * abs(st[i]['chain'] - c0) / abs(c1 - c0); tx = f"{int(t // 3600) % 12 or 12}.{int(round(t % 3600 / 60)) if round(t % 3600 / 60) < 60 else 59:02d}{'p' if t >= 12 * 3600 else 'a'}"
        seq.append(tx)
    seq[0], seq[-1] = ends[0], ends[1]
    return calls(st, seq, rev)
LINES = []
def line(key, kind, label, route, st, trips, labels, vessel, num, livery=None):
    T = []
    for tid, d, cs, note in trips:
        T.append(dict(id=f'{key.upper()}-{tid}', num=num, name=label, svc=SVC, dir=d, stops=cs, note=note + _m, **({'vessel': vessel} if vessel else {})))
        for (i, a, b, pr), (j, a2, b2, pr2) in zip(cs, cs[1:]):
            leg = abs(st[j]['chain'] - st[i]['chain']) / MI; h = (a2 - b) / 3600
            if h > 0 and not 2 < leg / h < 16 and leg > 0.3: print(f'  {key}-{tid} {st[i]["name"][:20]} - {st[j]["name"][:20]}: {leg:.1f} mi in {h * 60:.0f} min = {leg / h:.1f} mph  !! check')
    L = dict(key=key, kind=kind, label=label, mainline=True, src='Huntsville and Lake of Bays: the 1948 Official Guide (CN Table 126) and the company\'s 1942 summer timetable (Brendan); a model day, mostly estimated',
             owner='hlb', route=route, stations=st, dirLabels=labels, segments=[], trips=T)
    if kind == 'v': L.update(water=True, livery=livery)
    LINES.append(L); print(f'{key}: {label}, {route[-1][2] / MI:.1f} mi, {len(st)} stops, {len(T)} trips')
line('hla', 'v', 'Huntsville – Fairy Lake – Peninsula Lake – North Portage', alg_route, alg_st,
     [('D1', 0, spread(alg_st, A_DN1), 'S.S. Algonquin: Huntsville station dock 8.00 a.m. (from train 47) through Fairy and Peninsula Lakes to North Portage, for the Portage Flyer.'),
      ('U1', 1, spread(alg_st, A_UP1, True), 'S.S. Algonquin: North Portage (from the Portage Flyer) to Huntsville station dock 11.40 a.m., for train 44.'),
      ('D2', 0, spread(alg_st, A_DN2), 'S.S. Algonquin: Huntsville station dock 3.25 p.m. (from trains 55-53 and 41) to North Portage.'),
      ('U2', 1, spread(alg_st, A_UP2, True), 'S.S. Algonquin: North Portage (from the Portage Flyer) to Huntsville station dock, evening.')],
     ['to North Portage', 'to Huntsville'], 'Algonquin', 'Algonquin', 'hlb')
line('hlf', 'L', 'Portage Flyer (North Portage – South Portage)', fly_route, fly_st,
     [('U1', 1, calls(fly_st, ['9.35a', '9.55a'], True), 'The Portage Flyer: South Portage to North Portage, the Iroquois\'s passengers for the Algonquin; out to the end of the switchback spur and back.'),
      ('D1', 0, calls(fly_st, ['10.00a', '10.15a']), 'The Portage Flyer: North Portage to South Portage, the Algonquin\'s passengers for the Iroquois; out to the end of the switchback spur and back.'),
      ('U2', 1, calls(fly_st, ['4.25p', '4.45p'], True), 'The Portage Flyer: South Portage to North Portage, afternoon.'),
      ('D2', 0, calls(fly_st, ['4.55p', '5.15p']), 'The Portage Flyer: North Portage to South Portage, afternoon.')],
     ['to South Portage', 'to North Portage'], None, 'Portage Flyer')
line('hli', 'v', 'South Portage – Lake of Bays – Bigwin Inn – Dorset', iro_route, iro_st,
     [('U1', 1, spread(iro_st, I_UP1, True), 'S.S. Iroquois: Dorset 6.30 a.m. across Lake of Bays to South Portage, for the Portage Flyer.'),
      ('D1', 0, spread(iro_st, I_DN1), 'S.S. Iroquois: South Portage (from the Portage Flyer) across Lake of Bays by Bigwin Inn to Dorset 12.45 p.m.'),
      ('U2', 1, spread(iro_st, I_UP2, True), 'S.S. Iroquois: Dorset early afternoon to South Portage (estimated, as in 1942).'),
      ('D2', 0, spread(iro_st, I_DN2), 'S.S. Iroquois: South Portage (from the Portage Flyer) to Dorset 8.00 p.m.')],
     ['to Dorset', 'to South Portage'], 'Iroquois', 'Iroquois', 'hlb')
keys = {L['key'] for L in LINES}
vd['lines'] = [x for x in vd['lines'] if x['key'] not in keys] + LINES
open(os.path.join(HERE, 'viz_data.json'), 'w').write(json.dumps(vd, separators=(',', ':')))

# ---------------- GTFS (ferry 4, the Flyer 2)
def fmt(x): return f'{x // 3600:02d}:{x % 3600 // 60:02d}:{x % 60:02d}'
def app(name, rows_):
    with open(os.path.join(GT, name), 'a', newline='') as fh: csv.writer(fh).writerows(rows_)
def have(name, col=0): return set(r[col] for r in csv.reader(open(os.path.join(GT, name))))
if SVC not in have('calendar.txt'): app('calendar.txt', [[SVC, *SVC[2:], '19490616', '19491231']])
if 'HLB' not in have('agency.txt'): app('agency.txt', [['HLB', 'Huntsville and Lake of Bays Navigation Company', 'https://en.wikipedia.org/wiki/Portage_Flyer', 'America/Vancouver', 'en', '']])
gseen = have('stops.txt')
for L in LINES:
    rid = L['key'].upper(); st = L['stations']; rt = 2 if L['kind'] == 'L' else 4
    app('routes.txt', [[rid, 'HLB', L['label'], ' – '.join(s['name'] for s in st), rt, '1F5F5B', 'FFFFFF', 'Huntsville and Lake of Bays, a model day (mostly estimated). Times on the Pacific clock, three hours earlier than the Eastern time printed.']])
    new = [[s['gid'], s['name'] + ('' if L['kind'] == 'L' or s['gid'].startswith('CN_') else ' (steamer landing)'), f"{s['lat']:.6f}", f"{s['lon']:.6f}", s['note']] for s in st if s['gid'] not in gseen]
    gseen |= {r[0] for r in new}; app('stops.txt', new)
    for t in L['trips']:
        i0, i1 = t['stops'][0][0], t['stops'][-1][0]; lo, hi = sorted((st[i0]['chain'], st[i1]['chain']))
        pts_ = [p for p in L['route'] if lo - 0.5 <= p[2] <= hi + 0.5]
        if t['dir'] == 1 and st[i0]['chain'] > st[i1]['chain']: pts_ = pts_[::-1]
        app('shapes.txt', [[t['id'], f'{p[1]:.6f}', f'{p[0]:.6f}', k, f'{abs(p[2] - pts_[0][2]):.1f}'] for k, p in enumerate(pts_)])
        app('trips.txt', [[rid, t['svc'], t['id'], st[i1]['name'], t['num'], t['dir'], t['id']]])
        app('stop_times.txt', [[t['id'], fmt(a_), fmt(b_), st[i]['gid'], k, f"{abs(st[i]['chain'] - st[i0]['chain']):.1f}", tp] for k, (i, a_, b_, tp) in enumerate(t['stops'], 1)])
