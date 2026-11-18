"""Owen Sound Transportation Co. (with the Dominion Transportation Co., the "pool" service), summer 1948 (Brendan, 17 Nov 2026: "Let's add the Owen
Sound Transportation Company"; no 1948 schedule found: the pattern is from the company's history (Wikipedia, "Owen Sound Transportation Company", as
pasted by Brendan), every time ESTIMATED except the hours that history gives).
- S.S. Manitoulin, the "Turkey Trail" of the North Channel: Owen Sound Monday 11.15 p.m., Killarney Tuesday morning, Manitowaning, Little Current, Gore Bay,
  Meldrum Bay, Cockburn Island, Hilton Beach, Richards Landing, Sault Ste. Marie; by the 1940s on through the locks to Gargantua Harbour and Michipicoten
  instead of Mackinac Island; back over the same route to Owen Sound Saturday 4.30 a.m. Week-end trip: Owen Sound Saturday 11.15 p.m., Killarney,
  Manitowaning, Little Current, back to Owen Sound Monday 4.30 a.m. (the hours of the 1927 schedule, the last given; the Manitoulin ran until 1949).
- Tobermory - South Baymouth auto ferry, July - September: S.S. Norisle (1946; 50 cars, 250 passengers) and M.S. Normac. The crossing times and the number of
  crossings are ESTIMATED (Claude): about two hours, four crossings a day each.
Times are Eastern Standard Time, shown on the Pacific clock. Ports: points by Claude (APPROXIMATE) except Sault Ste. Marie (the C.S.L. dock already on the map)
and Michipicoten (the Algoma Central's Michipicoten station point, at the harbour). Same method as cdgb_build.py. Run after dcn_build."""
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

E = 'the point APPROXIMATE, Claude'
P = {'OS': ('Owen Sound (O.S.T. Co. dock)', (-80.9425, 44.5745), 'Owen Sound harbour, the Owen Sound Transportation Co. dock (' + E + ')', 1),
     'KIL': ('Killarney (steamer dock)', (-81.5110, 45.9705), 'Killarney, Ont. (' + E + ')', 1),
     'MAN': ('Manitowaning', (-81.8070, 45.7445), 'Manitowaning, Manitoulin Island (' + E + ')', 1),
     'LC': ('Little Current (dock)', (-81.9255, 45.9810), 'Little Current, Manitoulin Island (' + E + ')', 1),
     'GB': ('Gore Bay', (-82.4640, 45.9180), 'Gore Bay, Manitoulin Island (' + E + ')', 1),
     'MB': ('Meldrum Bay', (-83.1110, 45.9290), 'Meldrum Bay, Manitoulin Island (' + E + ')', 1),
     'CI': ('Cockburn Island (Tolsmaville)', (-83.3680, 45.9170), 'Tolsmaville, Cockburn Island (' + E + ')', 1),
     'HB': ('Hilton Beach', (-83.8930, 46.2560), 'Hilton Beach, St. Joseph Island (' + E + ')', 1),
     'RL': ("Richard's Landing", (-84.0390, 46.2960), "Richard's Landing, St. Joseph Island (" + E + ')', 1),
     'SSM': ('Sault Ste. Marie (C.S.L. Dock)', (-84.327090, 46.503184), 'Government Dock, Sault Ste. Marie, Ont.: the Canada Steamship Lines dock (Brendan, the Noronic\'s stop)', 1),
     'GAR': ('Gargantua Harbour', (-84.9370, 47.5650), 'Gargantua Harbour, Lake Superior (' + E + ')', 1),
     'MIC': ('Michipicoten (harbour)', (-84.900411, 47.962059), 'Michipicoten Harbour, Lake Superior (the Algoma Central\'s Michipicoten point)', 1),
     'TOB': ('Tobermory (ferry dock)', (-81.6640, 45.2560), 'Tobermory, Ont.: the ferry dock, Little Tub harbour (' + E + ')', 1),
     'SB': ('South Baymouth (ferry dock)', (-81.9920, 45.5555), 'South Baymouth, Manitoulin Island: the ferry dock (' + E + ')', 1),
     'SOO': ('"Soo" Locks', (-84.352, 46.504), 'Passing point: the locks at Sault Ste. Marie', 0)}
def gid(k): return 'PORT_' + re.sub(r'\W+', '_', P[k][0].upper()).strip('_') if P[k][3] else 'PASS_OSTC_' + k
WF = (-85.00, 46.93)
TURKEY = ['OS', 'KIL', 'MAN', 'LC', 'GB', 'MB', 'CI', 'HB', 'RL', 'SSM', ('via', [(-84.352, 46.504), WF]), 'GAR', 'MIC']
LINES = {'ostm_n': TURKEY, 'ostm_s': ['MIC', 'GAR', ('via', [WF, (-84.352, 46.504)]), 'SSM', 'RL', 'HB', 'CI', 'MB', 'GB', 'LC', 'MAN', 'KIL', 'OS'],
         'ostm_w': ['OS', 'KIL', 'MAN', 'LC', 'OS'], 'ostf_n': ['TOB', 'SB'], 'ostf_s': ['SB', 'TOB']}
_CF = os.path.join(HERE, 'ostc_legs.json'); CACHE = json.load(open(_CF)) if os.path.exists(_CF) else {}
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
def T(day, t): return day * 86400 + hm(t) - 3 * 3600     # Eastern Standard Time to the Pacific clock
# anchors (port key: (arrive, leave)); the other calls are put in between by distance along the lane (ESTIMATED)
SAIL = {
 'ostm_n': ('W_1000000', 'Manitoulin', {'OS': (None, T(0, '11.15p')), 'KIL': (T(1, '7.30a'), T(1, '8.00a')), 'SSM': (T(2, '6.00a'), T(2, '8.00a')), 'MIC': (T(2, '9.00p'), None)},
            'S.S. Manitoulin, the North Channel ("Turkey Trail"): Owen Sound Monday 11.15 p.m.; Killarney Tuesday morning; Sault Ste. Marie Wednesday morning; Michipicoten Wednesday night'),
 'ostm_s': ('W_0001000', 'Manitoulin', {'MIC': (None, T(0, '6.00a')), 'SSM': (T(0, '7.00p'), T(0, '9.00p')), 'OS': (T(2, '4.30a'), None)},
            'S.S. Manitoulin, the North Channel ("Turkey Trail"), back over the same route: Michipicoten Thursday morning; Sault Ste. Marie Thursday evening; Owen Sound Saturday 4.30 a.m.'),
 'ostm_w': ('W_0000010', 'Manitoulin', {'OS': (None, T(0, '11.15p')), 'KIL': (T(1, '7.30a'), T(1, '8.00a')), 'LC': (T(1, '1.30p'), T(1, '6.00p')), 'OS@': (T(2, '4.30a'), None)},
            'S.S. Manitoulin, week-end trip: Owen Sound Saturday 11.15 p.m.; Killarney, Manitowaning and Little Current on Sunday; back at Owen Sound Monday 4.30 a.m.'),
}
FERRY = [   # (direction, ship, leave, arrive): every day, July - September (ESTIMATED)
 ('ostf_n', 'Normac', '7.00a', '9.15a'), ('ostf_s', 'Normac', '10.30a', '12.45p'), ('ostf_n', 'Normac', '2.00p', '4.15p'), ('ostf_s', 'Normac', '5.30p', '7.45p'),
 ('ostf_s', 'Norisle', '7.00a', '9.00a'), ('ostf_n', 'Norisle', '10.00a', '12.00p'), ('ostf_s', 'Norisle', '1.00p', '3.00p'), ('ostf_n', 'Norisle', '4.00p', '6.00p')]
LABEL = {'ostm_n': ('North Channel: Owen Sound – Sault Ste. Marie – Michipicoten', 'to Michipicoten'), 'ostm_s': ('North Channel: Michipicoten – Sault Ste. Marie – Owen Sound', 'to Owen Sound'),
         'ostm_w': ('Week-end trip: Owen Sound – Killarney – Little Current – Owen Sound', 'to Owen Sound'),
         'ostf_n': ('Tobermory – South Baymouth ferry', 'to South Baymouth'), 'ostf_s': ('South Baymouth – Tobermory ferry', 'to Tobermory')}
_n = (' Owen Sound Transportation Co., summer 1948. No 1948 schedule in hand: the days and hours are the company\'s pattern from its history (Wikipedia; Brendan), and the'
      ' times at the other calls are put in between by distance (ESTIMATED). Eastern Standard Time, shown here in Pacific time.')
_nf = (' Tobermory - South Baymouth auto ferry, July to September 1948: S.S. Norisle (1946; 50 cars, 250 passengers) and M.S. Normac. The crossing times and the number'
       ' of crossings a day are ESTIMATED (about two hours; four crossings a day each); no 1948 schedule in hand. Eastern Standard Time, shown here in Pacific time.')
SRC = 'Owen Sound Transportation Co.: history (Wikipedia; Brendan, 17 Nov 2026); no 1948 schedule in hand, all times estimated; shown on the Pacific clock'
NEW = []
def gmiles(route, i, j):
    return sum(3958.8 * math.hypot(math.radians(q[0] - p[0]) * math.cos(math.radians((p[1] + q[1]) / 2)), math.radians(q[1] - p[1])) for p, q in zip(route[i:j], route[i + 1:j + 1]))
for key, seq in LINES.items():
    route, st = build(seq)
    keys = [s['key'] for s in st]
    ix = lambda c: min(range(len(route)), key=lambda i: abs(route[i][2] - st[c]['chain']))
    gm = [gmiles(route, 0, ix(c)) for c in range(len(st))]
    if key in SAIL:
        svc, ship, anc, txt = SAIL[key]
        A = {}
        for k, v in anc.items():
            c = len(st) - 1 if k.endswith('@') else keys.index(k)
            A[c] = (v[0] if v[0] is not None else v[1], v[1] if v[1] is not None else v[0])
        ks = sorted(A); stops = []
        for c in range(len(st)):
            if c in A: a, b = A[c]
            else:
                lo = max(k for k in ks if k < c); hi = min(k for k in ks if k > c)
                a = b = round(A[lo][1] + (gm[c] - gm[lo]) / (gm[hi] - gm[lo]) * (A[hi][0] - A[lo][1]))
            stops.append([c, a, b, 1 if c in A else 0])
        trips = [dict(id='OSTC-' + key.upper(), num=ship, name='O.S.T. Co. steamer', svc=svc, dir=0, stops=stops, vessel=ship, note=txt + '.' + _n)]
    else:
        trips = [dict(id=f'OSTC-{key.upper()}-{k}', num=sh, name='O.S.T. Co. ferry', svc='W_1111111', dir=0, vessel=sh,
                      stops=[[0, T(0, a), T(0, a), 0], [1, T(0, b), T(0, b), 0]], note=f'{("S.S." if sh == "Norisle" else "M.S.")} {sh}: leaves {a[:-1]} {"a.m." if a[-1] == "a" else "p.m."}, arrives {b[:-1]} {"a.m." if b[-1] == "a" else "p.m."} (ESTIMATED).' + _nf)
                 for k, (kk, sh, a, b) in enumerate(f for f in FERRY if f[0] == key)]
    for t in trips:
        s_ = t['stops']; assert s_[0][1] >= 0 and all(y[1] >= x[2] for x, y in zip(s_, s_[1:])), (key, s_)
    for s in st: s.pop('key')
    lab, dl = LABEL[key]
    NEW.append(dict(key=key, kind='v', label=lab, mainline=True, water=True, livery='ostc', src=SRC, owner='ostc', route=route, stations=st, dirLabels=[dl, ''], segments=[], trips=trips))
    print(f"{key}: {route[-1][2] / MI:.1f} mi of lane, {len(st)} points, {len(trips)} trips")
vd['lines'] = [x for x in vd['lines'] if x['key'] not in LINES] + NEW
open(os.path.join(HERE, 'viz_data.json'), 'w').write(json.dumps(vd, separators=(',', ':')))

# ---------------- GTFS (route_type 4); passing points are left out
def fmt(x): return f'{x // 3600:02d}:{x % 3600 // 60:02d}:{x % 60:02d}'
def app(name, rows_):
    with open(os.path.join(GT, name), 'a', newline='') as fh: csv.writer(fh).writerows(rows_)
def have(name, col=0): return set(r[col] for r in csv.reader(open(os.path.join(GT, name))))
if 'OSTC' not in have('agency.txt'): app('agency.txt', [['OSTC', 'Owen Sound Transportation Company', 'https://en.wikipedia.org/wiki/Owen_Sound_Transportation_Company', 'America/Vancouver', 'en', '']])
cal = have('calendar.txt')
app('calendar.txt', [[w, *w[2:], '19490616', '19491231'] for w in sorted({v[0] for v in SAIL.values()} | {'W_1111111'}) if w not in cal])
gseen = have('stops.txt')
for L in NEW:
    st = L['stations']; t = L['trips'][0]
    app('routes.txt', [['OSTC_' + L['key'].upper(), 'OSTC', L['label'], ' – '.join(s['name'] for s in st if s['principal']), 4, '5C3D7A', 'FFFFFF',
                        'Owen Sound Transportation Co. (times estimated). The lane is a least-cost path over the water layers, not a surveyed course. Times on the Pacific clock.']])
    new = [[s['gid'], s['name'] + ' (steamer landing)', f"{s['xy'][1]:.6f}", f"{s['xy'][0]:.6f}", s['note']] for s in st if s['principal'] and s['gid'] not in gseen]
    app('stops.txt', new); gseen |= {r[0] for r in new}
    for t in L['trips']:
        app('shapes.txt', [[t['id'], f'{p[1]:.6f}', f'{p[0]:.6f}', k, f'{p[2]:.1f}'] for k, p in enumerate(L['route'])])
        app('trips.txt', [['OSTC_' + L['key'].upper(), t['svc'], t['id'], st[t['stops'][-1][0]]['name'], t['vessel'], 0, t['id']]])
        rows = [(i, a, b) for i, a, b, _ in t['stops'] if st[i]['principal']]
        app('stop_times.txt', [[t['id'], fmt(a), fmt(b), st[i]['gid'], k, f"{st[i]['chain']:.1f}", 1] for k, (i, a, b) in enumerate(rows, 1)])
