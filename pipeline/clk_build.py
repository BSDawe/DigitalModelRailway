"""Clarke Steamship Co. coastal services in the lower St. Lawrence and the Gulf, week of 5 July 1948 (Brendan, 23 Nov 2026: "Let's go with the simulated schedule").
No 1948 timetable found: the sailing patterns are from "St Lawrence Saga" (clarkesteamship.wordpress.com, chapters 9 - 11) and the 1945 advertisement Brendan quoted; the
Lower St Lawrence Transportation Co. (Clarke's Rimouski subsidiary) from its 1950 brochure and 1950s schedules; the Matane seven days a week from the Matane historical
society's exhibition (Radio-Canada, 2018). Hours estimated except the printed departures (Montreal 7.30 p.m.; Rimouski 9 a.m.). Weekly patterns wrap round the week.
Ports APPROXIMATE (Claude). The Island Connector stays in lo_build.py. Copies glk_build.py (lanes over the basemap water)."""
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
BOXES = [(-73.65, -69.40, 45.45, 47.70),    # the St. Lawrence, Montreal - Quebec - below the Saguenay
         (-70.00, -60.50, 45.50, 50.45)]    # the estuary and the Gulf: North Shore, Gaspé coast, the Magdalens, Northumberland Strait
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
def _p(nm, ll, note, major=0): return (nm, ll, note + A, major)
P = {'MTL': ('Montreal (Victoria Pier)', (-73.5461, 45.5094), 'Montreal, Victoria Pier: the Clarke Steamship sailings', 1),
     'QUE': ("Quebec (Wolfe's Cove)", (-71.2372, 46.7889), "Quebec: the Clarke ships' berth", 1),
     'BCO': _p('Baie-Comeau', (-68.148, 49.219), 'Baie-Comeau, the wharf', 1), 'FRQ': _p('Franquelin', (-67.894, 49.287), 'Franquelin'),
     'GOD': _p('Godbout', (-67.595, 49.320), 'Godbout'), 'BTR': _p('Baie-Trinité', (-67.300, 49.418), 'Baie-Trinité'), 'PEN': _p('Pentecôte', (-67.170, 49.767), 'Pentecôte'),
     'CLC': _p('Clarke City', (-66.620, 50.160), 'Clarke City, the pier'), 'SEP': _p('Sept-Îles', (-66.381, 50.205), 'Sept-Îles, the wharf', 1),
     'RAT': _p('Rivière-au-Tonnerre', (-64.783, 50.275), 'Rivière-au-Tonnerre'), 'MIN': _p('Mingan', (-64.017, 50.293), 'Mingan'),
     'HSP': _p('Havre-Saint-Pierre', (-63.600, 50.232), 'Havre-Saint-Pierre, the wharf', 1), 'BJB': _p('Baie-Johan-Beetz', (-62.800, 50.287), 'Baie-Johan-Beetz'),
     'NAT': _p('Natashquan', (-61.818, 50.185), 'Natashquan', 1),
     'CCH': _p('Cap-Chat', (-66.690, 49.103), 'Cap-Chat'), 'SAM': _p('Sainte-Anne-des-Monts', (-66.493, 49.130), 'Sainte-Anne-des-Monts, the wharf', 1),
     'MLO': _p('Mont-Louis', (-65.730, 49.232), 'Mont-Louis'), 'RMA': _p('Rivière-Madeleine', (-65.320, 49.247), 'Rivière-Madeleine'),
     'GVA': _p('Grande-Vallée', (-65.130, 49.232), 'Grande-Vallée'), 'CLO': _p('Cloridorme', (-64.840, 49.182), 'Cloridorme'),
     'RAR': _p('Rivière-au-Renard', (-64.385, 49.000), 'Rivière-au-Renard'), 'GAS': _p('Gaspé', (-64.483, 48.830), 'Gaspé, the wharf', 1),
     'PIC': _p('Pictou', (-62.705, 45.677), 'Pictou, the steamer wharf', 1), 'SOU': _p('Souris', (-62.252, 46.352), 'Souris, P.E.I.', 1),
     'HAU': _p('Havre-Aubert', (-61.835, 47.238), 'Havre-Aubert (Amherst), Magdalen Islands', 1), 'CAM': _p('Cap-aux-Meules', (-61.858, 47.378), 'Cap-aux-Meules (Grindstone), Magdalen Islands', 1),
     'GEN': _p('Grande-Entrée', (-61.560, 47.553), 'Grande-Entrée (Grand Entry), Magdalen Islands'),
     'RIM': _p('Rimouski', (-68.524, 48.452), 'Rimouski, the wharf', 1), 'FOR': _p('Forestville', (-69.075, 48.735), 'Forestville', 1),
     'RAG': _p('Ragueneau', (-68.530, 49.060), 'Ragueneau'), 'MAT': _p('Matane', (-67.535, 48.853), 'Matane, the harbour', 1)}
GID = {'MTL': 'PORT_MONTREAL_VICTORIA_PIER', 'QUE': 'PORT_QUEBEC_WOLFE_S_COVE'}
def gid(k): return GID.get(k) or 'PORT_' + re.sub(r'\W+', '_', P[k][0].upper().replace('Î', 'I').replace('É', 'E').replace('È', 'E').replace('Ê', 'E')).strip('_')
_CF = os.path.join(HERE, 'clk_legs.json'); CACHE = json.load(open(_CF)) if os.path.exists(_CF) else {}
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

# ---- the voyages: (port, arrive, depart) as (day, h.mm) in Eastern Standard time, day 0 = Monday; a day past 6 runs into the next week (the weekly pattern wraps round)
LINES = {
 'clk_ns': dict(label='Montreal – North Shore – Natashquan (Clarke Steamship Co., North Shore)', ship='North Shore', co='CLK', days=None, stops=[
    ('MTL', None, (1, 19.30)), ('QUE', (2, 6.00), (2, 7.00)), ('BCO', (2, 23.00), (2, 23.30)), ('FRQ', (3, 0.45), (3, 1.00)), ('GOD', (3, 2.15), (3, 2.30)),
    ('BTR', (3, 4.00), (3, 4.15)), ('PEN', (3, 6.15), (3, 6.45)), ('CLC', (3, 10.00), (3, 10.30)), ('SEP', (3, 12.00), (3, 13.00)), ('RAT', (3, 18.30), (3, 19.00)),
    ('MIN', (3, 23.00), (3, 23.30)), ('HSP', (4, 0.30), (4, 6.00)), ('BJB', (4, 9.00), (4, 9.30)), ('NAT', (4, 13.00), (4, 16.00)), ('HSP', (4, 23.00), (4, 23.30)),
    ('SEP', (5, 9.00), (5, 14.00)), ('BCO', (5, 22.00), (6, 13.00)), ('QUE', (7, 6.00), (7, 18.00)), ('MTL', (8, 7.00), None)],
    note='s.s. North Shore, the Clarke express to the Quebec North Shore: weekly from Montreal (Victoria Pier), Tuesdays 7.30 p.m. (1946 - 47; 1948 season from May 12), 7-night '
         'voyage to Natashquan (alternate weeks 6 nights, Havre-Saint-Pierre). Ports as in 1946; calls and hours between are ESTIMATED.'),
 'clk_ng': dict(label='Montreal – Gaspé (Clarke Steamship Co., North Gaspé)', ship='North Gaspé', co='CLK', days=None, stops=[
    ('MTL', None, (1, 19.30)), ('QUE', (2, 6.00), (2, 8.00)), ('CCH', (3, 5.00), (3, 5.30)), ('SAM', (3, 6.30), (3, 8.00)), ('MLO', (3, 11.30), (3, 12.00)),
    ('RMA', (3, 14.30), (3, 15.00)), ('GVA', (3, 16.00), (3, 16.30)), ('CLO', (3, 18.00), (3, 18.30)), ('RAR', (3, 21.30), (3, 22.00)), ('GAS', (4, 1.00), (4, 14.00)),
    ('SAM', (5, 1.00), (5, 9.00)), ('QUE', (6, 7.00), (6, 18.00)), ('MTL', (7, 7.00), None)],
    note='m.v. North Gaspé, the Clarke 5 1/2-day Gaspé cruise: Montreal (Victoria Pier) Tuesday 7.30 p.m., Quebec Wednesday morning, Ste-Anne-des-Monts Thursday, Gaspé Friday, '
         'back by Ste-Anne-des-Monts Saturday and Quebec Sunday to Montreal Monday morning (the 1945 advertisement; 1948 season from May 11). Alternate weeks she made the 7-day '
         'cruise to the Magdalen Islands instead (Montreal Monday 7.30 p.m.); counting from May 11, the week of 5 July is a Gaspé week. Coast calls and hours ESTIMATED.'),
 'clk_mg2': dict(label='Pictou – Souris – Magdalen Islands (Clarke, Magdalen, Tuesdays)', ship='Magdalen', co='CLK', days=None, stops=[
    ('PIC', None, (1, 10.00)), ('SOU', (1, 15.30), (1, 16.30)), ('CAM', (2, 1.30), (2, 12.00)), ('SOU', (2, 21.00), (2, 22.00)), ('PIC', (3, 3.30), None)],
    note='s.s. Magdalen (Magdalen Islands Transportation Co., Clarke): the short 2-day Tuesday sailing from Pictou by Souris to Cap-aux-Meules (Grindstone) and back. Hours ESTIMATED.'),
 'clk_mg5': dict(label='Pictou – Souris – Magdalen Islands (Clarke, Magdalen, Thursdays)', ship='Magdalen', co='CLK', days=None, stops=[
    ('PIC', None, (3, 10.00)), ('SOU', (3, 15.30), (3, 16.30)), ('HAU', (4, 1.30), (4, 8.00)), ('CAM', (4, 10.00), (4, 16.00)), ('GEN', (4, 19.00), (5, 12.00)),
    ('CAM', (5, 15.00), (6, 12.00)), ('HAU', (6, 14.00), (7, 8.00)), ('SOU', (7, 17.00), (7, 18.00)), ('PIC', (7, 23.30), None)],
    note='s.s. Magdalen (Magdalen Islands Transportation Co., Clarke): the 5-day Thursday sailing from Pictou by Souris to Havre-Aubert (Amherst), Cap-aux-Meules (Grindstone) and '
         'Grande-Entrée, back by Cap-aux-Meules and Havre-Aubert. In the North Gaspé\'s Magdalens weeks it met her Friday arrival. Hours ESTIMATED.'),
 'lsl_rf': dict(label='Rimouski – Forestville (Lower St Lawrence Transportation Co., Rimouski)', ship='Rimouski', co='LSL', days=(0, 2, 3, 5), stops=[
    ('RIM', None, (0, 9.00)), ('FOR', (0, 11.30), (0, 14.00)), ('RIM', (0, 16.30), None)],
    note='m.v. Rimouski (Lower St Lawrence Transportation Co., the Clarke subsidiary at Rimouski): Rimouski 9 a.m. to Forestville Mondays, Wednesdays, Thursdays and Saturdays '
         '(1950 brochure, standing in for 1948). Return hours ESTIMATED.'),
 'lsl_rr': dict(label='Rimouski – Ragueneau (Lower St Lawrence Transportation Co., Rimouski)', ship='Rimouski', co='LSL', days=(1, 4), stops=[
    ('RIM', None, (0, 9.00)), ('RAG', (0, 12.30), (0, 13.30)), ('RIM', (0, 17.30), None)],
    note='m.v. Rimouski: Rimouski to Ragueneau Tuesdays and Fridays (1950s schedule, standing in for 1948). Hours ESTIMATED.'),
 'lsl_jb': dict(label='Rimouski – Baie-Comeau – Sept-Îles (Lower St Lawrence Transportation Co., Jean Brillant)', ship='Jean Brillant', co='LSL', days=(0, 3), stops=[
    ('RIM', None, (0, 9.00)), ('BCO', (0, 14.00), (0, 15.00)), ('SEP', (1, 1.00), (1, 10.00)), ('CLC', (1, 11.30), (1, 12.30)), ('RIM', (2, 2.00), None)],
    note='m.v. Jean Brillant (Lower St Lawrence Transportation Co.): the two-day sailings, Rimouski 9 a.m. Mondays and Thursdays (1950 brochure) by Baie-Comeau to Sept-Îles '
         '(arriving Tuesdays and Fridays, as in 1954), back by Clarke City. Hours ESTIMATED.'),
 'lsl_jbd': dict(label='Rimouski – Baie-Comeau (Lower St Lawrence Transportation Co., Jean Brillant, Wednesdays)', ship='Jean Brillant', co='LSL', days=(2,), stops=[
    ('RIM', None, (0, 9.00)), ('BCO', (0, 14.00), (0, 16.00)), ('RIM', (0, 21.00), None)],
    note='m.v. Jean Brillant: the Wednesday day trip, Rimouski 9 a.m. to Baie-Comeau and back (1950 brochure). Hours ESTIMATED.'),
 'lsl_mat': dict(label='Matane – Godbout – Franquelin – Baie-Comeau (Lower St Lawrence Transportation Co., Matane)', ship='Matane', co='LSL', days=(0, 1, 2, 3, 4, 5, 6), stops=[
    ('MAT', None, (0, 8.00)), ('GOD', (0, 11.00), (0, 11.15)), ('FRQ', (0, 12.30), (0, 13.00)), ('BCO', (0, 14.30), (0, 16.00)), ('MAT', (0, 20.30), None)],
    note='m.v. Matane (Matane 1; Lower St Lawrence Transportation Co.): Matane and the North Shore seven days a week, April to December, July 1938 - December 1961 (Société '
         'd\'histoire et de généalogie de Matane exhibition, Radio-Canada 2018). Ports as Brendan\'s note; the daily round trip and all hours ESTIMATED.')}
SRC = {'CLK': 'Clarke Steamship Co.: sailing patterns from "St Lawrence Saga" (clarkesteamship.wordpress.com, chapters 9 - 11: the 1945 advertisement, 1946 - 48 notices); '
              'hours estimated (Brendan, 23 Nov 2026: a simulated schedule); shown in Pacific time',
       'LSL': 'Lower St Lawrence Transportation Co. (Clarke): 1950 brochure and 1950s schedules from "St Lawrence Saga" ch. 11, standing in for 1948; Matane daily from the SHGM '
              'exhibition (Radio-Canada, 2018); hours estimated (Brendan, 23 Nov 2026: a simulated schedule); shown in Pacific time'}
NEW = []
H = 3600
SHIFT = -3 * H                      # Eastern to Pacific
KNOWN = {('MTL', 19.30), ('RIM', 9.00)}   # printed departures; the rest estimated
def sec(dh): d, x = dh; h = int(x); return d * 86400 + h * 3600 + round((x - h) * 100) * 60 + SHIFT
for key, L in LINES.items():
    route, st = build([s[0] for s in L['stops']])
    trips = []
    for d0 in (L['days'] or (None,)):
        add = 0 if d0 is None else d0 * 86400
        rows = [(i, (sec(a) + add) if a else None, (sec(d) + add) if d else None, s, d) for i, (s, a, d) in enumerate(L['stops'])]
        # one trip per day of departure (the page carries a trip over for a few days only): a trip ends at the arrival after its last same-day departure
        k = 0
        while k < len(rows) - 1:
            day = rows[k][2] // 86400
            j = k
            while j < len(rows) - 1 and rows[j][2] is not None and rows[j][2] // 86400 == day: j += 1
            base = day * 86400
            stops = []
            for i in range(k, j + 1):
                _, a, dd, s, dsp = rows[i]
                a_ = (a if a is not None else dd) - base; d_ = (dd if dd is not None and i < j else (a if a is not None else dd)) - base
                if i == k: a_ = d_ = dd - base
                tp = 1 if (i == k and dsp and (s, dsp[1]) in KNOWN) else 0
                stops.append([i, a_, d_, tp])
            dow = day % 7
            svc = 'W_' + ''.join('1' if x == dow else '0' for x in range(7))
            trips.append(dict(id=f"{L['co']}-{key.upper()}-{dow}-{stops[0][0]:02d}", num='', name=L['ship'], svc=svc, dir=0, stops=stops, vessel=L['ship'], note=L['note']))
            k = j
    for s in st: s.pop('key')
    NEW.append(dict(key=key, kind='v', label=L['label'], mainline=True, water=True, livery='clk', src=SRC[L['co']], owner='clk', route=route, stations=st,
                    dirLabels=['', ''], segments=[], trips=trips))
    print(f"{key}: {route[-1][2] / MI:.0f} mi of lane, {len(st)} calls, {len(trips)} trips")
vd['lines'] = [x for x in vd['lines'] if x['key'] not in LINES] + NEW
open(os.path.join(HERE, 'viz_data.json'), 'w').write(json.dumps(vd, separators=(',', ':')))

def fmt(x): return f'{x // 3600:02d}:{x % 3600 // 60:02d}:{x % 60:02d}'
def app(name, rows_):
    with open(os.path.join(GT, name), 'a', newline='') as fh: csv.writer(fh).writerows(rows_)
def have(name, col=0): return set(r[col] for r in csv.reader(open(os.path.join(GT, name))))
cal = have('calendar.txt')
for d in sorted({t['svc'] for L in NEW for t in L['trips']} - cal): app('calendar.txt', [[d, *d[2:], '19490616', '19491231']]); cal.add(d)
ags = have('agency.txt')
for ag, an, url in (('CLK', 'Clarke Steamship Company', 'https://en.wikipedia.org/wiki/Clarke_Steamship_Company'),
                    ('LSL', 'Lower St Lawrence Transportation Co. (Clarke Steamship)', 'https://clarkesteamship.wordpress.com/')):
    if ag not in ags: app('agency.txt', [[ag, an, url, 'America/Vancouver', 'en', '']])
seen = have('stops.txt')
for L in NEW:
    st = L['stations']; co = LINES[L['key']]['co']
    app('routes.txt', [[co + '_' + L['key'].upper(), co, L['label'], LINES[L['key']]['ship'], 4, '6B2D2D', 'FFFFFF', L['src'] + '. The lane is a least-cost path over the water layers, not a surveyed course.']])
    new = [[s['gid'], s['name'], f"{s['xy'][1]:.6f}", f"{s['xy'][0]:.6f}", s['note']] for s in st if s['gid'] not in seen]
    new = [r for i, r in enumerate(new) if r[0] not in {x[0] for x in new[:i]}]
    app('stops.txt', new); seen |= {r[0] for r in new}
    for t in L['trips']:
        app('shapes.txt', [[t['id'], f'{p[1]:.6f}', f'{p[0]:.6f}', k, f'{p[2]:.1f}'] for k, p in enumerate(L['route'])])
        app('trips.txt', [[co + '_' + L['key'].upper(), t['svc'], t['id'], st[t['stops'][-1][0]]['name'], t['vessel'], 0, t['id']]])
        app('stop_times.txt', [[t['id'], fmt(a), fmt(b), st[i]['gid'], k, f"{st[i]['chain']:.1f}", 1] for k, (i, a, b, _) in enumerate(t['stops'], 1)])
