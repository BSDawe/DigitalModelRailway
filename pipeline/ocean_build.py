"""Ocean liners for the week of 5 July 1948 (Brendan, 17 Nov 2026: "ocean liners should be a separate folder from the wider steamship folder for
ease of updating ... a separate heading on the map list"). Transatlantic passenger ships calling at Canadian ports in the week, drawn from the port out to
the edge of the map's water (or in from it), and gone beyond it. North American coastal ships (the Furness Red Cross Line to New York and Bermuda, the
Atlantic Charter, the Clarke ships, the Newfoundland Railway boats, the Alaska ships) stay with the steamers in lo_build.py and boats_build.py.

Sources and notes: marine/FOREIGN_TRADE_1948.md (Foreign Trade, 26 June 1948; the CP and Cunard - Donaldson lists), marine/pier21_arrivals_1948.csv
(the Pier 21 ship arrival database, scheduled arrival dates). Lanes: Brendan's basemap water, cached in ocean_legs.json (lo_legs.json is read as well).
A schedule change here re-runs only this step. Run after lo_build."""
import csv, json, math, os, re
from shapely.geometry import MultiPolygon, Polygon
from shapely.ops import unary_union
from nrwn_graph import fwd, MI
import sea
from sea import Sea, SEA_VERSION
HERE = os.path.dirname(os.path.abspath(__file__)); GT = os.path.join(HERE, 'gtfs'); ROOT = os.path.dirname(HERE)
vd = json.load(open(os.path.join(HERE, 'viz_data.json')))
ATL_BOX = (-74.30, -52.40, 40.30, 48.00)        # New York - Halifax - St. John's
GULF_BOX = (-74.00, -55.00, 45.40, 52.60)       # the St. Lawrence from Montreal, the Gulf, the Strait of Belle Isle

# ---------------- water: the basemap tiles (page projection) back to lon/lat
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
for _B in (ATL_BOX, GULF_BOX):
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

def gid(n): return 'PORT_' + re.sub(r'\W+', '_', n.upper()).strip('_')
def port(n, lon, lat, note): return dict(name=n, gid=gid(n), lon=lon, lat=lat, note=note)

# ---------------- lanes (cache ocean_legs.json; lo_build's lanes are reused)
_CF = os.path.join(HERE, 'ocean_legs.json'); CACHE = json.load(open(_CF)) if os.path.exists(_CF) else {}
_LO = os.path.join(HERE, 'lo_legs.json'); LO = json.load(open(_LO)) if os.path.exists(_LO) else {}
def lane(p, q, res, shore=500.0):
    ck = f'{SEA_VERSION}|{p[0]:.5f},{p[1]:.5f}|{q[0]:.5f},{q[1]:.5f}|{res}' + ('' if shore == 500.0 else f'|{shore}')
    if ck not in CACHE and ck in LO: CACHE[ck] = LO[ck]
    if ck not in CACHE:
        d = math.dist(fwd(*p), fwd(*q)); S = Sea([p, q], res=res, margin=max(8000.0, 0.3 * d), shore=shore); leg, land = S.leg(p, q)
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
def water_route(seq, res, shore=500.0):   # ports (dicts) and waypoints (lon, lat) in order; stations at the ports
    pts = []; idx = []; prev = None
    for p in seq:
        q = (p['lon'], p['lat']) if isinstance(p, dict) else p
        if prev is None: pts.append(q)
        else: pts += lane(prev, q, res, shore)[1:] + [q]
        if isinstance(p, dict): idx.append((p, len(pts) - 1))
        prev = q
    route = chain(pts)
    return route, [dict(name=p['name'], chain=route[i][2], lon=route[i][0], lat=route[i][1], mile=round(route[i][2] / MI, 1), lmile=round(route[i][2] / MI, 1), principal=True, kml='',
                        gid=p['gid'], xy=[p['lon'], p['lat']], note=p['note']) for p, i in idx]
def open_sea(seq, step=0.05):
    out = [seq[0]]
    for (a, b), (c, d) in zip(seq, seq[1:]):
        n = max(1, int(math.hypot(c - a, d - b) / step)); out += [(a + (c - a) * k / n, b + (d - b) * k / n) for k in range(1, n + 1)]
    return out
def gmi(route, i, j):
    return sum(3958.8 * math.hypot(math.radians(q[0] - p[0]) * math.cos(math.radians((p[1] + q[1]) / 2)), math.radians(q[1] - p[1])) for p, q in zip(route[i:j], route[i + 1:j + 1]))
def edge_line(ports, out, res=500, shore=8000.0, edge_name='At sea'):
    route, st = water_route(ports, res, shore)
    pts = [(p[0], p[1]) for p in route] + open_sea([(route[-1][0], route[-1][1]), out])[1:]
    route = chain(pts); last = len(route) - 1
    for s_ in st: s_['chain'] = route[min(range(len(route)), key=lambda i: abs(route[i][0] - s_['lon']) + abs(route[i][1] - s_['lat']))][2]
    st.append(dict(name=edge_name, chain=route[last][2], lon=out[0], lat=out[1], mile=round(route[last][2] / MI, 1), lmile=round(route[last][2] / MI, 1), principal=False, kml='',
                   gid=gid(edge_name + f' {out[0]:.1f} {out[1]:.1f}'), xy=list(out), note=edge_name + ": the edge of the map's water; the ship sails on beyond it (or comes in from beyond it)."))
    return route, st
def ri(route, st, k): return min(range(len(route)), key=lambda i: abs(route[i][2] - st[k]['chain']))
def hm(txt):
    m = re.match(r'(\d+)\.(\d+)([ap])', txt); h, mn = int(m.group(1)), int(m.group(2))
    if m.group(3) == 'p' and h != 12: h += 12
    if m.group(3) == 'a' and h == 12: h = 0
    return h * 3600 + mn * 60
H = 3600; D = 86400; PAC_A = 4 * H; PAC_N = 5 * H + 1800; PAC_NY = 4 * H
def _dsvc(d0): return 'W_' + ''.join('1' if i == d0 % 7 else '0' for i in range(7))
LINES = []
def mkline(key, label, route, st, trips, labels, src, livery):
    LINES.append(dict(key=key, kind='v', label=label, mainline=True, water=True, ocean=True, livery=livery, src=src, owner='cn', route=route, stations=st, dirLabels=labels, segments=[], trips=trips))
    print(f'{key}: {label}, {route[-1][2] / MI:.1f} mi, {len(trips)} sailings')
# ports shared with lo_build (the same names, so the same stops in the feed)
def dms(t):
    a = [float(x) for x in re.findall(r"[\d.]+", t)]; return -(a[3] + a[4] / 60 + a[5] / 3600), a[0] + a[1] / 60 + a[2] / 3600
MTV = port('Montreal (Victoria Pier)', *dms('45°30\'33.91"N 73°32\'46.08"W'), 'Victoria Pier, Montreal harbour (Brendan)')
NYP = port('New York (Pier 96, North River)', -73.9945, 40.7716, 'Pier No. 96, North River, foot of West 56th Street, New York (Furness Red Cross Line; the point APPROXIMATE, Claude).')
HFX = port('Halifax (Furness Withy)', -63.5655, 44.6430, 'Halifax harbour, Furness, Withy & Co. agents, Water Street (the point APPROXIMATE, Claude).')
SJN = port("St. John's (harbour)", -52.7085, 47.5650, "St. John's harbour, Water Street wharves (Harvey & Co., agents; the point APPROXIMATE, Claude).")
BOS = port('Boston (Central Wharf)', -71.0497, 42.3593, "Central Wharf, Boston (Official Guide; Brendan, 9 Nov 2026; the point APPROXIMATE, the nearest wharf on the water layer).")

# ---------------- Ocean liners, week of 5 July 1948 (Brendan, 15 - 17 Nov 2026): transatlantic passenger ships, and passenger-carrying ships along the coast,
# calling at Canadian ports in the week; drawn from the port out to the edge of the map's water (or in from it) and gone beyond. Scheduled dates:
# the CP Montreal - Liverpool summer 1948 sailing list; the Pier 21 ship arrival database (scheduled arrival dates, marine/pier21_arrivals_1948.csv);
# Foreign Trade, 26 June 1948 (marine/FOREIGN_TRADE_1948.md); The Daily News, St. John's. Hours not printed and the times at the edge: ESTIMATED from
# each ship's service speed (Claude). The edge points: where the course leaves the basemap's water (Claude, from the tiles).
PAC_E = 3 * H
LINER_LINES = []
def at(day, hhmm, off):   # day 0 = Monday 5 July 1948; local time with off = Pacific + off -> Pacific seconds from Monday 0.00
    return day * D + hm(hhmm) - off
def ltrip(tid, ves, name, d, calls, note):
    d0 = math.floor((calls[0][2] - 3 * H) / D)
    return dict(id=tid, d0=d0, num=ves, name=name, svc=_dsvc(d0), dir=d, vessel=ves, stops=[[i, a - d0 * D, b - d0 * D, tp] for i, a, b, tp in calls], note=note)
def run(route, st, i, j, mph): return round(gmi(route, min(ri(route, st, i), ri(route, st, j)), max(ri(route, st, i), ri(route, st, j))) / mph * H)
def liner_line(key, label, route, st, trips, labels, src, livery, agency, desc):
    mkline(key, label, route, st, trips, labels, src, livery); LINER_LINES.append((LINES[-1], agency, desc))
QBC = port("Quebec (Wolfe's Cove)", -71.2372, 46.7889, "Wolfe's Cove, Quebec: the ocean liners' berth (the point APPROXIMATE, Claude).")
P21 = port('Halifax (Pier 21)', -63.5672, 44.6393, 'Pier 21, Halifax: the immigration and ocean passenger pier (the point APPROXIMATE, Claude).')
CHT = port('Charlottetown', -63.1235, 46.2310, 'Charlottetown harbour, P.E.I. (the point APPROXIMATE, Claude).')
EDGE_BI = (-48.52, 53.25)   # beyond the Strait of Belle Isle, on the course for the British Isles
EDGE_HX = (-46.91, 46.55)   # south of the Grand Banks, on the course from Halifax to the English Channel
BELLE = [(-69.65, 47.90), (-68.55, 48.62), (-66.50, 49.35), (-64.20, 49.95), (-61.50, 50.15), (-59.00, 50.85), (-56.80, 51.38), (-55.20, 51.82)]   # the St. Lawrence, north of Anticosti, Belle Isle
bi_route, bi_st = edge_line([MTV, QBC] + BELLE, EDGE_BI, 500, 500.0, 'At sea (Strait of Belle Isle, for Liverpool)')
CPN = ' Canadian Pacific Steamships, Montreal - Quebec - Liverpool, summer season 1948 (CP sailing list: Brendan, 15 Nov 2026). First class and tourist.'
EC_q = at(-2, '11.00a', PAC_E) + run(bi_route, bi_st, 0, 1, 18.4)
EC = [ltrip('CPSS-EMPCAN-E', 'Empress of Canada', 'Canadian Pacific steamship', 0,
            [[0, at(-2, '11.00a', PAC_E), at(-2, '11.00a', PAC_E), 1], [1, EC_q, EC_q + 2 * H, 0], [2, EC_q + 2 * H + run(bi_route, bi_st, 1, 2, 19.6), EC_q + 2 * H + run(bi_route, bi_st, 1, 2, 19.6), 0]],
            'R.M.S. Empress of Canada: sails Montreal 11.00 a.m. (Eastern standard time) Saturday July 3, Quebec that evening, out by the Strait of Belle Isle on Monday 5; due Liverpool July 10. Times after Montreal ESTIMATED (about 17 knots).' + CPN)]
liner_line('lcpe', 'Montreal – Quebec – Liverpool (Canadian Pacific, Empress of Canada)', bi_route, bi_st, EC, ['to Liverpool', 'to Montreal'],
           'Canadian Pacific Steamships sailing list, Montreal - Quebec - Liverpool, summer 1948 (Brendan); times after Montreal estimated', 'cpss', 'CP',
           'Canadian Pacific Steamships, Montreal - Liverpool, week of 5 July 1948; drawn to the edge of the map. Times estimated, on the Pacific clock.')
CUN = (' Cunard White Star (Cunard - Donaldson Canadian service), Liverpool - Quebec - Montreal. Arrival date: Pier 21 ship arrival database (scheduled); next sailing from'
       ' Montreal July 11 - 14 (Foreign Trade, 26 June 1948). Hours ESTIMATED (about 15 knots at sea).')
AS_m = at(6, '10.00a', PAC_E); AS_qd = AS_m - run(bi_route, bi_st, 0, 1, 16.1); AS_qa = AS_qd - 3 * H; AS_e = AS_qa - run(bi_route, bi_st, 1, 2, 17.3)
AS = [ltrip('CUN-ASCANIA-W', 'Ascania', 'Cunard steamship', 1, [[2, AS_e, AS_e, 0], [1, AS_qa, AS_qd, 0], [0, AS_m, AS_m, 0]],
            'R.M.S. Ascania: in from Liverpool by the Strait of Belle Isle, Quebec, Montreal Sunday July 11.' + CUN)]
_cl = [dict(x) for x in bi_st]
liner_line('lcun', 'Liverpool – Quebec – Montreal (Cunard, Ascania)', bi_route, _cl, AS, ['to Liverpool', 'to Montreal'],
           'Pier 21 ship arrival database, 1948 (Brendan); Foreign Trade, 26 June 1948; Cunard - Donaldson brochure, 1948; hours estimated', 'cun', 'CUN',
           'Cunard White Star, Liverpool - Montreal, week of 5 July 1948; drawn from the edge of the map. Times estimated, on the Pacific clock.')
# Halifax, from the east: the Aquitania (Southampton - Halifax) and the Marine Marlin (Bremerhaven - Halifax - New York)
hx_route, hx_st = edge_line([P21, (-63.48, 44.50)], EDGE_HX, 500, 2000.0, 'At sea (for Southampton)')
AQ_h = at(7, '8.00a', PAC_A); AQ_e = AQ_h - run(hx_route, hx_st, 0, 1, 24.2)
AQ = [ltrip('CUN-AQUITANIA-W', 'Aquitania', 'Cunard steamship', 1, [[1, AQ_e, AQ_e, 0], [0, AQ_h, AQ_h, 0]],
            'R.M.S. Aquitania: Southampton to Halifax, due Monday July 12 (Pier 21 ship arrival database; the hour ESTIMATED, about 21 knots); she sails again from Halifax July 15 (Foreign Trade). Shown coming in on Sunday night.')]
liner_line('lcuq', 'Southampton – Halifax (Cunard, Aquitania)', hx_route, hx_st, AQ, ['to Southampton', 'to Halifax'],
           'Pier 21 ship arrival database, 1948 (Brendan); Foreign Trade, 26 June 1948; hours estimated', 'cun', 'CUN',
           'Cunard White Star, Southampton - Halifax, week of 5 July 1948; drawn from the edge of the map. Times estimated, on the Pacific clock.')
mm_route, mm_st = edge_line([NYP, (-73.80, 40.45), P21, (-63.48, 44.50)], EDGE_HX, 500, 8000.0, 'At sea (from Bremerhaven)')
MM_h = at(1, '8.00a', PAC_A); MM_e = MM_h - run(mm_route, mm_st, 1, 2, 18.4); MM_d = at(1, '8.00p', PAC_A); MM_n = MM_d + run(mm_route, mm_st, 0, 1, 18.4)
MM = [ltrip('USL-MARLIN-W', 'Marine Marlin', 'United States Lines steamship', 1, [[2, MM_e, MM_e, 0], [1, MM_h, MM_d, 0], [0, MM_n, MM_n, 0]],
            'S.S. Marine Marlin, United States Lines: Bremerhaven and Channel ports to Halifax, due Tuesday July 6 (Pier 21 ship arrival database: 500 passengers), and on to New York. Hours ESTIMATED (about 16 knots). One of the C4 "Marine" ships running austerity passenger sailings and emigrant voyages.')]
liner_line('lusl', 'Bremerhaven – Halifax – New York (United States Lines, Marine Marlin)', mm_route, mm_st, MM, ['to Bremerhaven', 'to New York'],
           'Pier 21 ship arrival database, 1948 (Brendan); hours estimated', 'usl', 'USL',
           'United States Lines, Bremerhaven - Halifax - New York, week of 5 July 1948; drawn from the edge of the map. Times estimated, on the Pacific clock.')
# Furness Warren Line: R.M.S. Newfoundland, Liverpool - St. John's - Halifax - Boston and back. In Halifax July 2 (Pier 21) and loading there July 3 - 6 (Foreign Trade);
# due St. John's July 12 from Boston and Halifax, sailing the same day for Liverpool (The Daily News, July 7 - 9).
fw_route, fw_st = water_route([BOS, HFX, SJN], 500, 8000.0)
FWN = ' Furness Warren Line (Furness, Withy & Co.), Liverpool - St. John\'s - Halifax - Boston, passengers and freight. Hours ESTIMATED (about 13 knots).'
FW_hd = at(1, '6.00p', PAC_A); FW_b = FW_hd + run(fw_route, fw_st, 0, 1, 15.0)
FW_bd = at(4, '8.00a', PAC_A); FW_h = FW_bd + run(fw_route, fw_st, 0, 1, 15.0); FW_hd2 = at(5, '8.00p', PAC_A); FW_s = at(7, '1.30p', PAC_N)
FW = [ltrip('FWL-NFLD-S', 'Newfoundland', 'Furness Warren Line steamship', 1, [[1, FW_hd, FW_hd, 0], [0, FW_b, FW_b, 0]],
            'R.M.S. Newfoundland: Halifax Tuesday July 6 (after loading there July 3 - 6) for Boston.' + FWN),
      ltrip('FWL-NFLD-N', 'Newfoundland', 'Furness Warren Line steamship', 0, [[0, FW_bd, FW_bd, 0], [1, FW_h, FW_hd2, 0], [2, FW_s, FW_s, 0]],
            'R.M.S. Newfoundland: Boston Friday July 9, Halifax Saturday 10, due St. John\'s Monday July 12, sailing the same day for Liverpool.' + FWN)]
liner_line('fwl', "Boston – Halifax – St. John's (Furness Warren Line, Newfoundland)", fw_route, fw_st, FW, ["to St. John's", 'to Boston'],
           "The Daily News, St. John's, 7 - 9 July 1948; Pier 21 ship arrival database; Foreign Trade, 26 June 1948 (Brendan); hours estimated", 'frc', 'FRC',
           'Furness Warren Line, Boston - Halifax - St. John\'s, week of 5 July 1948. Times estimated, on the Pacific clock.')

json.dump(CACHE, open(_CF, 'w'))
keys = {L['key'] for L in LINES}
vd['lines'] = [x for x in vd['lines'] if x['key'] not in keys] + LINES
open(os.path.join(HERE, 'viz_data.json'), 'w').write(json.dumps(vd, separators=(',', ':')))

# ---------------- GTFS
def fmt(x): return f'{x // 3600:02d}:{x % 3600 // 60:02d}:{x % 60:02d}'
def app(name, rows_):
    with open(os.path.join(GT, name), 'a', newline='') as fh: csv.writer(fh).writerows(rows_)
def have(name, col=0): return set(r[col] for r in csv.reader(open(os.path.join(GT, name))))
for _a in (['CUN', 'Cunard White Star Limited', 'https://en.wikipedia.org/wiki/Cunard_Line'], ['USL', 'United States Lines', 'https://en.wikipedia.org/wiki/United_States_Lines']):
    if _a[0] not in have('agency.txt'): app('agency.txt', [_a + ['America/Vancouver', 'en', '']])
gseen = have('stops.txt')
for L, ag, desc in LINER_LINES:
    rid = L['key'].upper(); st = L['stations']
    app('routes.txt', [[rid, ag, L['label'], ' – '.join(s['name'] for s in st), 4, {'CP': '7A1E2C', 'FRC': '9E1B1B', 'CUN': 'B5121B', 'USL': '1B365D'}.get(ag, '1F4F9A'), 'FFFFFF', desc]])
    new = [[s['gid'], s['name'] + ('' if s['name'].startswith('At sea') else ' (steamer landing)'), f"{s['lat']:.6f}", f"{s['lon']:.6f}", s['note']] for s in st if s['gid'] not in gseen]
    gseen |= {r[0] for r in new}; app('stops.txt', new)
    for t in L['trips']:
        i0, i1 = t['stops'][0][0], t['stops'][-1][0]
        pts_ = [p for p in L['route'] if min(st[i0]['chain'], st[i1]['chain']) - 0.05 <= p[2] <= max(st[i0]['chain'], st[i1]['chain']) + 0.05]
        if i0 > i1: pts_ = pts_[::-1]
        app('shapes.txt', [[t['id'], f'{p[1]:.6f}', f'{p[0]:.6f}', k, f'{abs(p[2] - pts_[0][2]):.1f}'] for k, p in enumerate(pts_)])
        app('trips.txt', [[rid, t['svc'], t['id'], st[i1]['name'], t['num'], t['dir'], t['id']]])
        app('stop_times.txt', [[t['id'], fmt(a_), fmt(b_), st[i]['gid'], k, f"{abs(st[i]['chain'] - st[i0]['chain']):.1f}", tp] for k, (i, a_, b_, tp) in enumerate(t['stops'], 1)])
print(f'ocean_build: {len(LINES)} lines, {sum(len(L["trips"]) for L in LINES)} sailings')
