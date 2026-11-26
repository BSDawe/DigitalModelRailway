"""Chicago North Shore & Milwaukee Railroad (the North Shore Line; Brendan, 25 Nov 2026): Chicago - Milwaukee (Skokie Valley Route), the Shore Line (Chicago - Evanston -
Highland Park - Lake Bluff - Waukegan), Chicago - Libertyville - Mundelein (Skokie Valley Route), the Skokie Valley trains to Waukegan, and the Lake Bluff - Mundelein branch.
Sources:
- Times: CNS&M Timetable G-54, June 5, 1949 (reprint May 1950; Illinois Railway Museum CTA collection, http://irm-cta.org/NSL/TT/NSL%20Timetable%201949-06-05%20(2).pdf),
  every table, transcribed in timetables_cnsm/*.txt. The 1949 schedule stands in for July 1948 (Brendan: the April 1948 Official Guide shows the same pattern within a few
  minutes). Chicago Daylight Saving time as printed; trains printed "will not run during Daylight Saving Time" are left out. Shown on the Pacific clock (three hours earlier).
  Through trains between the Shore Line and the Milwaukee line (3, 201, 5, 611 north; 440, 608 south) are timed beyond North Chicago Junction from the Skokie Valley locals
  (estimated), except 440, which the Skokie Valley table prints to Edison Court.
- Track: Mississippi Rails (Tony Howe and David Price), Chicago interurbans KML, cut by tools/chi_extract.py into traces/chicago/cnsm_routes.json. Northbound trains go round the
  Loop by Wabash Avenue and Lake Street, southbound by Wells Street, Van Buren Street and the south-east wye (Brendan), so each direction is its own line on the page; track
  already drawn by another line is drawn once (owner none). 'L' track is the Chicago Transit Authority's (owner cta, the rapid-transit class, dark blue); the North Shore Line's
  own track (the Niles Center branch, the Skokie Valley, the Shore Line north of Linden Avenue, Wilmette) is turquoise.
- Stations: the file's station polygons (named ones as named; unnamed ones matched to the timetable's stations in order, by running time: approximate), the 'L' stations, and
  a few placed by street or running time (approximate).
- Electroliners (the starred trains) carry the name Electroliner. Livery: Electroliner turquoise and salmon (Brendan)."""
import csv, json, math, os, re
import numpy as np
from scipy.spatial import cKDTree
HERE = os.path.dirname(os.path.abspath(__file__))
GT = os.path.join(HERE, 'gtfs')
TT = os.path.join(HERE, 'timetables_cnsm')
RJ = json.load(open(os.path.join(HERE, 'traces', 'chicago', 'cnsm_routes.json')))
RT, POLY = RJ['routes'], RJ['polys']
C0 = math.cos(math.radians(42.0))
MI = 1609.34
def m(a, b): return math.hypot((a[0] - b[0]) * 111320 * C0, (a[1] - b[1]) * 110570)
def xy(p): return (p[0] * 111320 * C0, p[1] * 110570)
def chained(pts):
    out, d = [], 0.0
    for k, p in enumerate(pts):
        if k: d += m(pts[k - 1], p)
        out.append([p[0], p[1], round(d, 1), p[2]])
    return out
def proj(route, q):
    best = None
    for i in range(len(route) - 1):
        a, b = route[i], route[i + 1]; dx, dy = b[0] - a[0], b[1] - a[1]
        t = max(0, min(1, ((q[0] - a[0]) * dx + (q[1] - a[1]) * dy) / ((dx * dx + dy * dy) or 1e-18)))
        f = (a[0] + t * dx, a[1] + t * dy); dd = m(q, f)
        if best is None or dd < best[0]: best = (dd, a[2] + t * (b[2] - a[2]), f)
    return best
def at(route, ch):
    for a, b in zip(route, route[1:]):
        if a[2] <= ch <= b[2]:
            t = (ch - a[2]) / ((b[2] - a[2]) or 1); return (a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1]))
    return tuple(route[-1][:2]) if ch > 0 else tuple(route[0][:2])
def cross(route, lat):
    for a, b in zip(route, route[1:]):
        if (a[1] - lat) * (b[1] - lat) <= 0 and a[1] != b[1]:
            t = (lat - a[1]) / (b[1] - a[1]); return a[2] + t * (b[2] - a[2])
    raise ValueError(lat)
_svT = cKDTree([xy(p) for p in RT['sv']])
def compose(tail, north):
    if tail == 'branch': pts = RT['branch'] if north else RT['branch'][::-1]
    else:
        t = RT[tail]
        if tail == 'shore_mke':      # the Shore Line to the junction, then the Milwaukee line's own track (not a parallel track of the file)
            i = next(i for i in range(len(t)) if t[i][1] > 42.30 and _svT.query(xy(t[i]))[0] < 25)
            j = int(_svT.query(xy(t[i]))[1]); t = t[:i + 1] + RT['sv'][j + 1:]
        pts = RT['loop_n'] + t[1:] if north else t[::-1] + RT['loop_s'][1:]
    return chained(pts)
SV_N = compose('sv', True)
# North Chicago Junction: where the through track from the Shore Line joins the Milwaukee line
_sm = RT['shore_mke']
NCJ_PT = next(tuple(_sm[i][:2]) for i in range(len(_sm)) if _sm[i][1] > 42.30 and _svT.query(xy(_sm[i]))[0] < 25)

POL = 'station polygon in the Mississippi Rails file'
# canonical name: (gid, display name, point, principal, note). point: (lon, lat); ('lat', x) where the line crosses that latitude (a street); 'ncj'; 'end' (route end).
# None: placed by running time between placed stations, then moved to a station polygon of the file within 300 m if there is one (approximate).
S = {}
def st(name, gid=None, disp=None, pt=None, principal=False, note=None):
    S[name] = dict(gid=gid or 'CNSM_' + re.sub(r'[^A-Z0-9]+', '_', name.upper()).strip('_'), disp=disp or name, pt=pt, principal=principal, note=note)
st('Roosevelt Road', 'CNSM_ROOSEVELT', pt=(-87.62662, 41.86728), principal=True, note="the South Side 'L' 12th Street station, " + POL)
st('Adams & Wabash', 'CNSM_ADAMS_WABASH', pt=(-87.62612, 41.87954), principal=True, note="'L' station, " + POL)
st('Madison & Wabash', 'CNSM_MADISON_WABASH', pt=(-87.62620, 41.88205), note="'L' station, " + POL)
st('Randolph & Wabash', 'CNSM_RANDOLPH_WABASH', pt=(-87.62625, 41.88452), note="'L' station, " + POL)
st('Clark & Lake', 'CNSM_CLARK_LAKE', pt=(-87.63101, 41.88575), note="'L' station, " + POL)
st('Merchandise Mart', 'CNSM_MERCHANDISE_MART', pt=(-87.63402, 41.88916), note="'L' station; placed at the old Kinzie Street station of the file (approximate)")
st('Grand Avenue', 'CNSM_GRAND', pt=(-87.63560, 41.89160), note="'L' station, " + POL)
st('Chicago Avenue', 'CNSM_CHICAGO_AVE', pt=(-87.63608, 41.89685), note="'L' station, " + POL)
st('Belmont Avenue', 'CNSM_BELMONT', pt=(-87.65342, 41.93970), note="'L' station, " + POL)
st('Wilson Avenue', 'CNSM_WILSON', pt=(-87.65794, 41.96540), note="'L' Wilson Avenue terminal, " + POL)
st('Howard Street', 'CNSM_HOWARD', pt=(-87.67318, 42.01929), principal=True, note="'L' station, " + POL)
st('Randolph & Wells', 'CNSM_RANDOLPH_WELLS', pt=(-87.63393, 41.88512), note="'L' station (Randolph & Fifth), " + POL)
st('Madison & Wells', 'CNSM_MADISON_WELLS', pt=(-87.63385, 41.88202), note="'L' station (Madison & Fifth), " + POL)
st('Quincy & Wells', 'CNSM_QUINCY_WELLS', pt=(-87.63377, 41.87874), note="'L' station (Quincy & Fifth), " + POL)
st('LaSalle & Van Buren', 'CNSM_LASALLE_VB', pt=(-87.63186, 41.87688), note="'L' station, " + POL)
st('Dearborn-State-Van Buren', 'CNSM_DEARBORN_STATE_VB', pt=(-87.62846, 41.87692), note="'L' station, between the file's Dearborn and State stations")
# Evanston ('L', Evanston branch)
st('Church Street', disp='Church Street, Evanston', pt=('lat', 42.0491), note="'L' station, placed at Church Street (approximate)")
st('Foster Street', disp='Foster Street, Evanston', pt=(-87.68360, 42.05423), note="'L' station, " + POL)
st('Noyes Street', disp='Noyes Street, Evanston', pt=(-87.68348, 42.05804), note="'L' station, " + POL)
st('Central Street', disp='Central Street, Evanston', pt=(-87.68550, 42.06370), note="'L' station, " + POL)
st('Linden Avenue', disp='Linden Avenue, Wilmette', pt=(-87.69157, 42.07348), principal=True, note="'L' terminal, " + POL)
# Skokie Valley and Milwaukee
st('Dempster Street', 'CNSM_DEMPSTER', 'Dempster Street, Skokie', pt=('lat', 42.0412), note='placed where the line crosses Dempster Street (approximate)')
st('Briergate', disp='Briergate, West Highland Park', pt=(-87.81971, 42.17757), note=POL + ' (Briergate Station)')
st('Scranton Avenue', 'CNSM_SCRANTON_AVE', 'Scranton Avenue, Lake Bluff', pt=(-87.84806, 42.28030), note=POL + ' (a stop at Scranton Avenue)')
st("Downey's (West)", 'CNSM_DOWNEYS_WEST', "Downey's (West), Great Lakes", pt=(-87.84716, 42.30687), note=POL)
st('North Chicago Junction', 'CNSM_NORTH_CHICAGO_JCT', pt='ncj', note='at the junction of the Shore Line and the Milwaukee line (approximate)')
st('Edison Court', 'CNSM_EDISON_COURT', 'Edison Court, Waukegan', pt=(-87.84607, 42.35938), principal=True, note=POL + ' (Washington Street passenger station)')
st('Winthrop Harbor', disp='Winthrop Harbor', pt=('lat', 42.478751), note="placed on the line at the latitude of Brendan's Winthrop Harbor point (42.478751, -87.823666, about 1.8 km east of the line in the file): approximate")
st('Zion', 'CNSM_ZION', pt=(-87.84519, 42.45123), note=POL + ' (Salem Boulevard)')
st('Kenosha', 'CNSM_KENOSHA', pt=(-87.84219, 42.57711), principal=True, note=POL)
st('Racine', 'CNSM_RACINE', pt=('svmi', 66.4), principal=True, note='placed by the running times between Kenosha and Milwaukee (approximate)')
st('Harrison Street', 'CNSM_MKE_HARRISON', 'Harrison Street, Milwaukee', pt=('lat', 42.9990), note='placed where the line crosses Harrison Avenue (approximate)')
st('Mitchell Street', 'CNSM_MKE_MITCHELL', 'Mitchell Street, Milwaukee', pt=('lat', 43.0124), note='placed where the line crosses Mitchell Street (approximate)')
st('Greenfield Avenue', 'CNSM_MKE_GREENFIELD', 'Greenfield Avenue, Milwaukee', pt=('lat', 43.0168), note='placed where the line crosses Greenfield Avenue (approximate)')
st('National Avenue', 'CNSM_MKE_NATIONAL', 'National Avenue, Milwaukee', pt=('lat', 43.0237), note='placed where the line crosses National Avenue (approximate)')
st('6th & Michigan Sts.', 'CNSM_MILWAUKEE', 'Milwaukee (6th & Michigan)', pt=(-87.91867, 43.03712), principal=True, note='Downtown terminal, ' + POL)
# Waukegan, Mundelein
st('10th Street', disp='10th Street, Waukegan', pt=(-87.83347, 42.34065), principal=True, note=POL + ' (Waukegan 10th Street station)')
st('Mundelein', pt=(-88.00106, 42.27305), principal=True, note='at the end of the line in the file (approximate)')
st('Lake Bluff', principal=True)
st('Milw. Ave. (Main Sta.)', disp='Milwaukee Avenue, Libertyville', principal=True)
st('Highwood', principal=True)
TOWN = {'Wilmette Avenue (Main Sta.)': 'Wilmette', 'Forest Avenue': 'Wilmette', 'Indian Hill': 'Winnetka', 'Willow Road': 'Winnetka', 'Elm St. (Main Sta.)': 'Winnetka',
        'Eldorado Street': 'Winnetka', 'Hubbard Woods': 'Winnetka', 'Harbor Street': 'Glencoe', 'Park Av. (Main Sta.)': 'Glencoe', 'Green Bay Road': 'Glencoe',
        'Braeside': 'Highland Park', 'Ravinia': 'Highland Park', 'Beech Street': 'Highland Park', 'Lincoln Avenue': 'Highland Park', 'Central Av. (Main Sta.)': 'Highland Park',
        'Vine Avenue': 'Highland Park', 'Sacred Heart': 'Lake Forest', "Farwell's": 'Lake Forest', 'Deerpath Av. (Main Sta.)': 'Lake Forest', 'Scott Avenue': 'Lake Forest',
        'Noble Avenue': 'Lake Forest', 'Arden Shore': 'Lake Bluff', "Downey's (East)": 'Great Lakes', 'Main Gate': 'Great Lakes', '22nd Street': 'North Chicago',
        'Second Avenue': 'North Chicago', '18th Street': 'North Chicago', '14th Street': 'North Chicago', 'Harmswoods': 'West Evanston', 'Glenayre': 'Glenview',
        'Northfield': 'West Winnetka', 'Northbrook': 'West Glencoe', 'Woodridge': 'West Highland Park', 'Highmoor': 'West Highland Park', 'Sheridan Elms': 'West Lake Forest',
        'Deerpath (West)': 'West Lake Forest', '4th Street': 'Libertyville', 'Garfield Avenue': 'Libertyville'}
ALIAS = {'Adams and Wabash': 'Adams & Wabash', 'Clark and Lake': 'Clark & Lake', 'Greenfield Ave.': 'Greenfield Avenue', 'Lake Bluff (Shore Line)': 'Lake Bluff'}
def canon(n): return ALIAS.get(n, n)
def read(fn):
    head, trains = None, []
    for line in open(os.path.join(TT, fn)):
        if line.startswith('#') or not line.strip(): continue
        if line.startswith('STATIONS'): head = [canon(s.strip()) for s in line.split('=', 1)[1].split(';')]; continue
        num, days, flags, ap, times = [x.strip() for x in line.split('|')]
        trains.append(dict(num=num, days=days, flags=flags.split(), ap=ap, times=times.split()))
    return head, trains
def tsec(tr):
    """Seconds after midnight Chicago time for each printed time (None where no stop), AM / PM worked out along the column; and the stop conditions."""
    out, prev = [], None
    for x in tr['times']:
        if x == '-': out.append(None); continue
        cond = x[0] if x[0].isalpha() else None; v = x[1:] if cond else x
        h, mm = map(int, v.split('.')); t = (h % 12) * 3600 + mm * 60
        if prev is None: t += 12 * 3600 if tr['ap'] == 'PM' else 0
        else:
            while t < prev: t += 12 * 3600
        prev = t; out.append((t, cond))
    return out
FILES = [('sv_north.txt', 'sv', True), ('mundelein_north.txt', 'mundelein', True), ('shore_north.txt', 'shore', True), ('branch_north.txt', 'branch', True),
         ('sv_south.txt', 'sv', False), ('waukegan_sv_south.txt', 'sv', False), ('mundelein_south.txt', 'mundelein', False), ('shore_south.txt', 'shore', False),
         ('waukegan10_sv_south.txt', 'sv_tenth', False), ('branch_south.txt', 'branch', False)]
# Through trains between the Shore Line and the Milwaukee line: (file, train): (tail, [(station, minutes after (+) or before (-) the train's North Chicago Junction time)])
LOCAL_N = [('Edison Court', 6), ('Zion', 12), ('Kenosha', 21), ('Racine', 31), ('Harrison Street', 51), ('Mitchell Street', 54), ('Greenfield Avenue', 56),
           ('National Avenue', 58), ('6th & Michigan Sts.', 63)]           # No. 405's running times from North Chicago Junction
LOCAL_S = [('6th & Michigan Sts.', -65), ('National Avenue', -61), ('Greenfield Avenue', -59), ('Mitchell Street', -57), ('Harrison Street', -53), ('Racine', -33),
           ('Kenosha', -23), ('Zion', -14), ('Edison Court', -7)]            # No. 404's
THROUGH = {('shore_north.txt', '3'): ('shore_mke', LOCAL_N), ('shore_north.txt', '201'): ('shore_mke', LOCAL_N[:2]), ('shore_north.txt', '611'): ('shore_mke', LOCAL_N[:2]),
           ('shore_north.txt', '5'): ('shore_mke', LOCAL_N[:1]), ('shore_south.txt', '608'): ('shore_mke', LOCAL_S),
           ('shore_south.txt', '516'): ('shore_mke', [('Winthrop Harbor', -16), ('Zion', -13), ('Edison Court', -7)]),
           ('shore_south.txt', '440'): ('shore_mke', [('6th & Michigan Sts.', '1.00'), ('National Avenue', '1.04'), ('Greenfield Avenue', '1.06'), ('Mitchell Street', '1.08'),
                                                     ('Harrison Street', '1.12'), ('Racine', '1.32'), ('Kenosha', '1.42'), ('Zion', '1.51'), ('Edison Court', '1.58')])}
THROUGH_NOTE = {'3': 'runs on to Milwaukee (times beyond North Chicago Junction not printed: estimated)', '201': 'runs on to Zion (times beyond North Chicago Junction estimated)',
                '611': 'runs on to Zion (times beyond North Chicago Junction estimated)', '5': 'runs on to Edison Court in Daylight Saving time (time estimated)',
                '608': 'from Milwaukee in Daylight Saving time (times before North Chicago Junction estimated)',
                '440': 'from Milwaukee (Skokie Valley table) and by the Shore Line south of North Chicago Junction',
                '516': 'from Winthrop Harbor in Daylight Saving time (times before North Chicago Junction not printed: estimated)'}
DAYS = {'daily': '1111111', 'daily exc Sun': '1111110', 'Sun only': '0000001', 'Sat & Sun only': '0000011', 'Sat only': '0000010', 'daily exc Sat & Sun': '1111100'}
COND = {'K': '1111100', 'J': '1111110', 'L': '0000010', 'M': '1111101', 'S': '0000001', 'W': '0000011'}
DAYNAME = ['Mon.', 'Tue.', 'Wed.', 'Thu.', 'Fri.', 'Sat.', 'Sun.']
SHIFT = -3 * 3600
def ampm(s): h, mm = divmod(s // 60, 60); h %= 24; return f"{(h - 1) % 12 + 1}.{mm:02d} {'a.m.' if h < 12 else 'p.m.'}"

ROUTES = {}
def route_of(tail, north):
    k = (tail, north)
    if k not in ROUTES: ROUTES[k] = compose(tail, north)
    return ROUTES[k]
CAND = [p for p in POLY if not p[2] or re.search(r'Station|Depot|Stop|Platform|Sta\b', p[2]) and not re.search(r'Freight|Sub-?Station|Frieght', p[2])]
PLACED = {}    # canonical name -> (lon, lat)
USEDPOLY = set()
def fixed_point(name, route):
    pt = S.get(name, {}).get('pt')
    if pt is None: return None
    if pt == 'ncj': return NCJ_PT
    if pt[0] == 'lat': return at(route, cross(route, pt[1]))
    if pt[0] == 'svmi': return at(SV_N, pt[1] * MI)
    return pt
def place_file(fn, tail, north):
    head, trains = read(fn)
    route = route_of(tail, north)
    known = {}
    for nm in head:
        p = PLACED.get(nm) or fixed_point(nm, route)
        if p is not None: known[nm] = proj(route, p)[1]
    todo = [nm for nm in head if nm not in known]
    for nm in todo:                      # by running time between placed stations, on a train calling at both
        i = head.index(nm); best = None
        for tr in trains:
            tt = tsec(tr)
            if not tt[i]: continue
            a = next((j for j in range(i - 1, -1, -1) if tt[j] and head[j] in known), None)
            b = next((j for j in range(i + 1, len(head)) if tt[j] and head[j] in known), None)
            if a is None or b is None: continue
            span = tt[b][0] - tt[a][0]
            if span <= 0: continue
            ch = known[head[a]] + (known[head[b]] - known[head[a]]) * (tt[i][0] - tt[a][0]) / span
            if best is None or b - a < best[0]: best = (b - a, ch)
        if best: known[nm] = best[1]
    # move a running-time station to a station polygon of the file within 300 m along the line, nearest first
    est = [nm for nm in todo if nm in known]
    pc = [(k, proj(route, (p[0], p[1]))) for k, p in enumerate(CAND) if k not in USEDPOLY]
    pc = [(k, r[1], r[2]) for k, r in pc if r[0] < 60]
    pairs = sorted((abs(ch - known[nm]), nm, k, ch, f) for nm in est for k, ch, f in pc if abs(ch - known[nm]) < 300)
    done = set()
    for d, nm, k, ch, f in pairs:
        if nm in done or k in USEDPOLY: continue
        known[nm] = ch; USEDPOLY.add(k); done.add(nm); S.setdefault(nm, {})['snap'] = round(d)
    for nm in head:
        if nm in known and nm not in PLACED: PLACED[nm] = at(route, known[nm])
    missing = [nm for nm in head if nm not in known]
    assert not missing, (fn, missing)
for fn, tail, north in FILES: place_file(fn, tail, north)
for (fn, num), (tail, extra) in THROUGH.items():
    for nm, _ in extra:
        if nm not in PLACED: PLACED[nm] = fixed_point(nm, SV_N)

def stn_note(nm):
    s = S.get(nm, {})
    if s.get('note'): return s['note']
    if 'snap' in s: return f'placed at a station polygon in the Mississippi Rails file matched by running time ({s["snap"]} m from the running-time position): approximate'
    return 'placed by running time between neighbouring stations (approximate)'
def disp(nm):
    s = S.get(nm, {})
    if s.get('disp'): return s['disp']
    return f'{nm}, {TOWN[nm]}' if nm in TOWN else nm
def gid(nm): return S[nm]['gid'] if 'gid' in S.get(nm, {}) else 'CNSM_' + re.sub(r'[^A-Z0-9]+', '_', nm.upper()).strip('_')

LINES, ALLST = {}, {}
LABEL = {'sv': 'Chicago – Milwaukee (Skokie Valley Route)', 'shore': 'Chicago – Waukegan (Shore Line)', 'shore_mke': 'Shore Line – Milwaukee through trains',
         'mundelein': 'Chicago – Libertyville – Mundelein (Skokie Valley Route)', 'sv_tenth': 'Waukegan (10th Street) – Chicago by the Skokie Valley',
         'branch': 'Lake Bluff – Libertyville – Mundelein'}
for fn, tail0, north in FILES:
    head, trains = read(fn)
    for tr in trains:
        num = tr['num']; tail, extra = THROUGH.get((fn, num), (tail0, []))
        key = f"cnsm_{tail}_{'n' if north else 's'}"
        L = LINES.setdefault(key, dict(tail=tail, north=north, trips=[], names=set()))
        tt = tsec(tr)
        stops = [(head[i], v[0], v[1], 1) for i, v in enumerate(tt) if v]
        if extra:
            ncj = next(t for nm, t, c, tp in stops if nm == 'North Chicago Junction')
            for nm, off in extra:
                if isinstance(off, str):
                    h, mm = map(int, off.split('.')); stops.append((nm, (h % 12) * 3600 + mm * 60, None, 1))
                else: stops.append((nm, ncj + off * 60, None, 0))
        L['names'].update(nm for nm, *_ in stops)
        L['trips'].append((fn, tr, stops))
order = ['cnsm_sv_n', 'cnsm_sv_s', 'cnsm_shore_n', 'cnsm_shore_s', 'cnsm_mundelein_n', 'cnsm_mundelein_s', 'cnsm_branch_n', 'cnsm_branch_s', 'cnsm_shore_mke_n',
         'cnsm_shore_mke_s', 'cnsm_sv_tenth_s']
DRAWN = []   # points of the track already drawn (every ~5 m)
def densify(route):
    out = []
    for a, b in zip(route, route[1:]):
        n = max(1, int(m(a, b) // 5))
        for k in range(n): out.append((a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n))
    return out
OUT = []
src = ('CNS&M Timetable G-54, June 5, 1949 (Illinois Railway Museum CTA collection, irm-cta.org), standing in for July 1948; track Mississippi Rails (Tony Howe and '
       "David Price); 'L' track Chicago Transit Authority")
for key in order:
    if key not in LINES: continue
    L = LINES[key]; route = route_of(L['tail'], L['north'])
    names = sorted(L['names'], key=lambda nm: proj(route, PLACED[nm])[1])
    st_ = []
    for nm in names:
        ch = proj(route, PLACED[nm])[1]; p = at(route, ch)
        s = dict(name=disp(nm), chain=round(ch, 1), lon=round(p[0], 6), lat=round(p[1], 6), mile=round(ch / MI, 2), principal=bool(S.get(nm, {}).get('principal')),
                 gid=gid(nm), note=stn_note(nm))
        st_.append(s); ALLST.setdefault(s['gid'], s)
    idx = {nm: i for i, nm in enumerate(names)}
    # track: drawn once; 'L' (cta) or North Shore Line (cnsm)
    tree = cKDTree([xy(p) for p in DRAWN]) if DRAWN else None
    segs, cur = [], None
    for a, b in zip(route, route[1:]):
        shared = tree is not None and tree.query(xy(a))[0] < 5 and tree.query(xy(b))[0] < 5
        own = 'none' if shared else ('cta' if a[3] and b[3] else 'cnsm')
        if cur and cur['owner'] == own and abs(cur['b'] - a[2]) < 0.01: cur['b'] = b[2]
        else: cur = dict(owner=own, a=a[2], b=b[2]); segs.append(cur)
    segs = [s for s in segs if s['owner'] != 'none']
    DRAWN += densify(route)
    trips = []
    for fn, tr, stops in L['trips']:
        stops = sorted(stops, key=lambda s: idx[s[0]])
        base = DAYS[tr['days']]; groups = {}
        for dd in range(7):
            if base[dd] != '1': continue
            ss = tuple(k for k, s in enumerate(stops) if not s[2] or COND[s[2]][dd] == '1')
            groups.setdefault(ss, []).append(dd)
        elec = 'E' in tr['flags']
        for g, (ss, dds) in enumerate(groups.items()):
            sel = [stops[k] for k in ss]
            sts = [[idx[nm], t + SHIFT, t + SHIFT, tp] for nm, t, c, tp in sel]
            assert all(x[1] <= y[1] for x, y in zip(sts, sts[1:])), (key, tr['num'], sts)
            if sts[0][1] < 0:          # after midnight in Chicago, the evening before on the Pacific clock: a day earlier
                for x in sts: x[1] += 86400; x[2] += 86400
                dds = sorted((d - 1) % 7 for d in dds)
            svc = 'W_' + ''.join('1' if d in dds else '0' for d in range(7))
            days = 'daily' if len(dds) == 7 else ', '.join(DAYNAME[d] for d in dds)
            num = re.sub(r'\D', '', tr['num']); frm, to = disp(sel[0][0]), disp(sel[-1][0])
            extra = THROUGH_NOTE.get(tr['num'])
            trips.append(dict(id=f"CNSM-{tr['num']}" + (f'-{g}' if len(groups) > 1 else ''), num=num, name='Electroliner' if elec else 'North Shore Line', svc=svc,
                              dir=0, gdir=0 if L['north'] else 1, stops=sts, motor=True,   # each line's route runs the way its trains go: dir 0 on the page
                              note=(f'Electroliner No. {num}' if elec else f'No. {num}') + f', {frm} {ampm(sel[0][1])} to {to} {ampm(sel[-1][1])} (Chicago Daylight Saving '
                                   f'time, as printed); {days}' + ('' if days.endswith('.') else '.') + (f' {extra[0].upper() + extra[1:]}.' if extra else '') +
                                   ' CNS&M Timetable G-54, June 5, 1949, standing in for July 1948. Shown in Pacific time.'))
    lab = LABEL[L['tail']] + (', northbound' if L['north'] else ', southbound') + (' (by Wabash)' if L['north'] and L['tail'] != 'branch' else ' (by Wells)' if L['tail'] != 'branch' else '')
    OUT.append(dict(key=key, kind='F', label=lab, mainline=True, owner='none', livery='cnsm', src=src, route=[[p[0], p[1], p[2]] for p in route], stations=st_,
                    dirLabels=['northbound', 'southbound'] if L['north'] else ['southbound', 'northbound'], segments=segs, trips=trips))
    print(f"{key}: {route[-1][2] / MI:.2f} mi, {len(st_)} stations, {len(trips)} trips, drawn {sum(s['b'] - s['a'] for s in segs) / MI:.1f} mi")
ids = [t['id'] for L in OUT for t in L['trips']]; assert len(ids) == len(set(ids)), [i for i in ids if ids.count(i) > 1]
if os.environ.get('CNSM_DRY'):
    for nm in sorted(PLACED, key=lambda n: PLACED[n][1]): print(f"   {PLACED[nm][1]:.5f},{PLACED[nm][0]:.5f}  {disp(nm):40s} {stn_note(nm)[:70]}")
    raise SystemExit
vd = json.load(open(os.path.join(HERE, 'viz_data.json')))
vd['lines'] = [x for x in vd['lines'] if not x['key'].startswith('cnsm_')] + OUT
open(os.path.join(HERE, 'viz_data.json'), 'w').write(json.dumps(vd, separators=(',', ':')))

def fmt(x): return f'{x // 3600:02d}:{x % 3600 // 60:02d}:{x % 60:02d}'
def app(name, rows_):
    with open(os.path.join(GT, name), 'a', newline='') as fh: csv.writer(fh).writerows(rows_)
def have(name, col=0): return set(r[col] for r in csv.reader(open(os.path.join(GT, name))))
cal = have('calendar.txt')
for d in sorted({t['svc'] for L in OUT for t in L['trips']} - cal): app('calendar.txt', [[d, *d[2:], '19490616', '19491231']])
if 'CNSM' not in have('agency.txt'): app('agency.txt', [['CNSM', 'Chicago North Shore & Milwaukee Railroad', 'https://en.wikipedia.org/wiki/Chicago_North_Shore_and_Milwaukee_Railroad', 'America/Vancouver', 'en', '']])
seen = have('stops.txt')
app('stops.txt', [[s['gid'], s['name'], f"{s['lat']:.6f}", f"{s['lon']:.6f}", s['note']] for s in ALLST.values() if s['gid'] not in seen])
for L in OUT:
    rid = L['key'].upper()
    app('routes.txt', [[rid, 'CNSM', 'North Shore Line', L['label'], 0, '1F9E96', 'FFFFFF', L['src'] + '. Times on the Pacific clock.']])
    app('shapes.txt', [[rid, f'{p[1]:.6f}', f'{p[0]:.6f}', k, f'{p[2]:.1f}'] for k, p in enumerate(L['route'])])
    for t in L['trips']:
        app('trips.txt', [[rid, t['svc'], t['id'], L['stations'][t['stops'][-1][0]]['name'], t['name'], t['gdir'], rid]])
        app('stop_times.txt', [[t['id'], fmt(a), fmt(b), L['stations'][i]['gid'], k, f"{L['stations'][i]['chain']:.1f}", tp] for k, (i, a, b, tp) in enumerate(t['stops'], 1)])
