"""Chicago Aurora and Elgin Railroad (Brendan, 26 Nov 2026): Chicago (Wells Street) - Wheaton - Aurora, Batavia and Elgin.
Sources:
- Times: the Official Guide, May 1948 (the CA&E table is dated April 1948; Brendan's scans, private repo scans/cae/), transcribed in timetables_cae/cae_west.txt and
  cae_east.txt. Central Daylight Saving time as printed; shown on the Pacific clock (three hours earlier). Each column is one train from Wells Street dividing at Wheaton into
  sections for Aurora, Batavia (by Warrenville) and Elgin (by Lakewood), and the reverse: the Aurora section (or, without one, the Elgin section) runs through to Wells Street,
  the others start or end at Wheaton. The table's footnote stops (Canal Street, Marshfield Avenue, Kedzie Avenue and Laramie Avenue in Chicago; Oak Park, Forest Park, Maywood,
  Bellwood) are timed from its running times (Marshfield 4 minutes, Laramie about 15) and by distance between them: estimated. The "additional trains" lists (Chicago - Wheaton,
  Wheaton - Elgin / Aurora / Batavia, Batavia - Wheaton) and the additional Sunday service are timed from printed trains with the same stops (estimated); the Sunday "frequent
  service" to Wheaton, given only as first and last trains, is not drawn. St. Charles and Geneva are served by CA&E motor coaches from Lakewood (the St. Charles - Geneva
  Transfer): buses are not drawn; the trains' notes name the connection.
- Track: Mississippi Rails (Tony Howe and David Price), Chicago interurbans KML, cut by tools/chi_extract.py (traces/chicago/cnsm_routes.json, cae_* routes): Wells Street
  terminal and the Garfield Park 'L' (Chicago Transit Authority track, owner cta) to Forest Park, the CA&E's own line beyond.
- Stations: the file's named station polygons. Livery: late-period bright red and grey (Brendan: so it does not blend with the CTA)."""
import csv, json, math, os, re
from scipy.spatial import cKDTree
HERE = os.path.dirname(os.path.abspath(__file__))
GT = os.path.join(HERE, 'gtfs')
TT = os.path.join(HERE, 'timetables_cae')
RT = json.load(open(os.path.join(HERE, 'traces', 'chicago', 'cnsm_routes.json')))['routes']
C0 = math.cos(math.radians(42.0)); MI = 1609.34
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
POL = 'station polygon in the Mississippi Rails file'
ST = {   # name: (gid, display, point, principal, note)
 'Wells Street': ('CAE_WELLS_ST', 'Wells Street, Chicago', (-87.63426, 41.87765), True, "CA&E terminal (Wells Street Terminal), " + POL),
 'Canal Street': ('CAE_CANAL_ST', 'Canal Street, Chicago', (-87.63994, 41.87732), False, "'L' station (Union Station), " + POL),
 'Marshfield Avenue': ('CAE_MARSHFIELD', 'Marshfield Avenue, Chicago', (-87.66848, 41.87578), False, "'L' station, " + POL),
 'Kedzie Avenue': ('CAE_KEDZIE', 'Kedzie Avenue, Chicago', (-87.70562, 41.87323), False, "'L' station, " + POL),
 'Laramie Avenue': ('CAE_LARAMIE', 'Laramie Avenue, Chicago', (-87.75398, 41.87261), False, "'L' station (52nd Street terminal), " + POL),
 'Oak Park': ('CAE_OAK_PARK', 'Oak Park', (-87.79433, 41.87265), False, POL),
 'Forest Park': ('CAE_FOREST_PARK', 'Forest Park', (-87.81468, 41.87403), False, "'L' Des Plaines Avenue station, " + POL),
 'Maywood': ('CAE_MAYWOOD', 'Maywood', (-87.83922, 41.87524), False, POL + ' (5th Avenue station)'),
 'Bellwood': ('CAE_BELLWOOD', 'Bellwood', (-87.87877, 41.87927), False, POL + ' (Bellwood Avenue station)'),
 'Elmhurst (York St.)': ('CAE_ELMHURST', 'Elmhurst (York Street)', (-87.94053, 41.88446), False, POL),
 'Villa Park (Villa Ave.)': ('CAE_VILLA_PARK', 'Villa Park (Villa Avenue)', (-87.96952, 41.88571), False, POL),
 'Lombard': ('CAE_LOMBARD', 'Lombard', (-88.01795, 41.88180), False, POL),
 'Glen Ellyn': ('CAE_GLEN_ELLYN', 'Glen Ellyn', (-88.06713, 41.87568), False, POL),
 'Wheaton': ('CAE_WHEATON', 'Wheaton', (-88.10697, 41.86433), True, POL + ' (Wheaton passenger depot)'),
 'Warrenville': ('CAE_WARRENVILLE', 'Warrenville', (-88.18150, 41.82387), False, POL),
 'Aurora': ('CAE_AURORA', 'Aurora', (-88.31193, 41.75853), True, POL + ' (Aurora depot)'),
 'Batavia': ('CAE_BATAVIA', 'Batavia', (-88.30666, 41.84985), True, POL + ' (Batavia depot)'),
 'Lakewood': ('CAE_LAKEWOOD', 'Lakewood (St. Charles - Geneva Transfer)', (-88.20230, 41.91505), False, POL + '; CA&E motor coaches to and from St. Charles and Geneva'),
 'Wayne': ('CAE_WAYNE', 'Wayne', (-88.24120, 41.95070), False, POL),
 'Elgin': ('CAE_ELGIN', 'Elgin', (-88.28502, 42.03693), True, POL + ' (Chicago Street depot)'),
}
FOOT = ['Canal Street', 'Marshfield Avenue', 'Kedzie Avenue', 'Laramie Avenue', 'Oak Park', 'Forest Park', 'Maywood', 'Bellwood']
TRUNK = ['Wells Street', 'Elmhurst (York St.)', 'Villa Park (Villa Ave.)', 'Lombard', 'Glen Ellyn', 'Wheaton']
SEC = {'aurora': ['Warrenville', 'Aurora'], 'batavia': ['Warrenville', 'Batavia'], 'elgin': ['Lakewood', 'Wayne', 'Elgin']}
def read(fn):
    head, trains = None, []
    for line in open(os.path.join(TT, fn)):
        if line.startswith('#') or not line.strip(): continue
        if line.startswith('STATIONS'): head = [s.strip() for s in line.split('=', 1)[1].split(';')]; continue
        tid, days, flags, ap, times = [x.strip() for x in line.split('|')]
        trains.append(dict(id=tid, days=days, ap=ap, times=dict(zip(head, times.split()))))
    return head, trains
def parse(tr):
    """{station: (seconds, cond)}: each printed time put in the 12-hour turn nearest the column's first time (sections are not in time order down the column)."""
    vals = [v for v in tr['times'].values() if v != '-']
    def raw(x): c = x[0] if x[0].isalpha() else None; v = x[1:] if c else x; h, mm = map(int, v.split('.')); return (h % 12) * 3600 + mm * 60, c
    first = raw(vals[0])[0] + (12 * 3600 if tr['ap'] == 'PM' else 0)
    out = {}
    for nm, x in tr['times'].items():
        if x == '-': continue
        t, c = raw(x)
        t = min((t + k * 12 * 3600 for k in range(4)), key=lambda v: abs(v - first - 1800))
        out[nm] = (t, c)
    return out
DAYS = {'daily': '1111111', 'daily exc Sun': '1111110', 'daily exc Sat': '1111101', 'Sun only': '0000001', 'Sat & Sun only': '0000011', 'Sat only': '0000010',
        'daily exc Sat & Sun': '1111100'}
COND = {'L': '0000010', 'S': '0000001', 'J': '1111110'}
DAYNAME = ['Mon.', 'Tue.', 'Wed.', 'Thu.', 'Fri.', 'Sat.', 'Sun.']
SHIFT = -3 * 3600
ROUTE = {k: chained(RT['cae_' + k]) for k in ('aurora', 'batavia', 'elgin')}
CH = {k: {nm: proj(r, ST[nm][2])[1] for nm in ST if proj(r, ST[nm][2])[0] < 150} for k, r in ROUTE.items()}
def ampm(s): h, mm = divmod(s // 60, 60); h %= 24; return f"{(h - 1) % 12 + 1}.{mm:02d} {'a.m.' if h < 12 else 'p.m.'}"
def add_foot(stops, branch, west):
    """The footnote stops between Wells Street and the first stop printed west of it (estimated): Marshfield 4 minutes and Laramie 15 from Wells Street, the rest by distance."""
    ch = CH[branch]; d = dict((nm, (t, c, tp)) for nm, t, c, tp in stops)
    if 'Wells Street' not in d: return stops
    tw = d['Wells Street'][0]; nxt = next(nm for nm in TRUNK[1:] if nm in d); tn = d[nxt][0]
    sgn = 1 if west else -1
    fixed = {'Wells Street': 0, 'Marshfield Avenue': 4 * 60, 'Laramie Avenue': 15 * 60}
    pts = [('Wells Street', ch['Wells Street'], 0), ('Marshfield Avenue', ch['Marshfield Avenue'], 240), ('Laramie Avenue', ch['Laramie Avenue'], 900),
           (nxt, ch[nxt], abs(tn - tw))]
    out = list(stops)
    for nm in FOOT:
        c = ch[nm]
        if nm in fixed: off = fixed[nm]
        else:
            a, b = next((p, q) for p, q in zip(pts, pts[1:]) if p[1] <= c <= q[1])
            off = a[2] + (b[2] - a[2]) * (c - a[1]) / ((b[1] - a[1]) or 1)
        out.append((nm, tw + sgn * int(round(off / 60)) * 60, None, 0))
    return out
TRIPS = {k: [] for k in ROUTE}
def make(stops, branch, west, days, tid, note):
    stops = add_foot(stops, branch, west)
    stops.sort(key=lambda s: CH[branch][s[0]] * (1 if west else -1))
    base = DAYS[days]; groups = {}
    for dd in range(7):
        if base[dd] != '1': continue
        ss = tuple(k for k, s in enumerate(stops) if not s[2] or COND[s[2]][dd] == '1')
        groups.setdefault(ss, []).append(dd)
    for g, (ss, dds) in enumerate(groups.items()):
        sel = [stops[k] for k in ss]
        sts = [[nm, t + SHIFT, tp] for nm, t, c, tp in sel]
        if sts[0][1] < 0:
            for x in sts: x[1] += 86400
            dds = sorted((d - 1) % 7 for d in dds)
        assert all(a[1] <= b[1] for a, b in zip(sts, sts[1:])), (tid, sts)
        dtxt = 'daily' if len(dds) == 7 else ', '.join(DAYNAME[d] for d in dds)
        frm, to = ST[sel[0][0]][1], ST[sel[-1][0]][1]
        TRIPS[branch].append(dict(id=f'CAE-{tid}' + (f'-{g}' if len(groups) > 1 else ''), num='Train', name='Chicago Aurora & Elgin', svc='W_' + ''.join('1' if d in dds else '0' for d in range(7)),
                                  dir=0 if west else 1, stops=sts, motor=True,
                                  note=f"{frm} {ampm(sel[0][1])} to {to} {ampm(sel[-1][1])} (Central Daylight Saving time, as printed); {dtxt.rstrip('.')}. {note}"
                                       'Footnote stops (Canal Street to Bellwood) timed from the table\'s running times: estimated. Official Guide, May 1948. Shown in Pacific time.'))
def column(tr, west, days=None, tid=None, extra=''):
    tt = parse(tr); days = days or tr['days']; tid = tid or tr['id']
    trunk = [(nm, *tt[nm], 1) for nm in TRUNK if nm in tt]
    secs = {k: [(nm, *tt[nm], 1) for nm in v if nm in tt] for k, v in SEC.items()}
    secs = {k: v for k, v in secs.items() if any(nm in ('Aurora', 'Batavia', 'Elgin') for nm, *_ in v)}
    whe = [s for s in trunk if s[0] == 'Wheaton']
    main = 'aurora' if 'aurora' in secs else 'elgin' if 'elgin' in secs else 'batavia' if 'batavia' in secs else None
    coach = ' Motor coach connection at Lakewood for St. Charles and Geneva.' if 'elgin' in secs else ''
    if main is None: make(trunk, 'aurora', west, days, tid, extra); return
    make(trunk + secs[main], main, west, days, tid, extra + (coach if main == 'elgin' else ''))
    for k, v in secs.items():
        if k == main: continue
        sec = whe + v if whe else v
        part = 'Section ' + ('from Wheaton' if west else 'to Wheaton') + (', joining' if not west else ', dividing') + ' the Wells Street train there. '
        make(sec, k, west, days, f'{tid}-{k[0].upper()}', part + extra + (coach if k == 'elgin' else ''))
_, WEST = read('cae_west.txt'); _, EAST = read('cae_east.txt')
IDX = {t['id']: t for t in WEST + EAST}
for tr in WEST: column(tr, True)
for tr in EAST: column(tr, False)
# "Additional trains" and additional Sunday service, timed from printed trains with the same stops (template column, new first time as 'h.mm AM/PM', days, sections kept)
def shifted(tid, start, days, keep, newid, note):
    tr = IDX[tid]; tt = parse(tr)
    first = [nm for nm in tr['times'] if tr['times'][nm] != '-' and nm in keep]
    v, ap = start.split(); h, mm = map(int, v.split('.')); new = (h % 12) * 3600 + mm * 60 + (12 * 3600 if ap == 'PM' else 0)
    t0 = min(tt[nm][0] for nm in first)
    times = {nm: ('-' if nm not in keep or tr['times'][nm] == '-' else None) for nm in tr['times']}
    off = new - t0
    stops = {nm: tt[nm][0] + off for nm in tr['times'] if times[nm] is None}
    fake = dict(id=newid, days=days, ap='AM', times={nm: '-' for nm in tr['times']})
    for nm, t in stops.items(): h2, m2 = divmod((t % 86400) // 60, 60); fake['times'][nm] = f'{(h2 % 12) or 12}.{m2:02d}'
    fake['ap'] = 'AM' if (min(stops.values()) % 86400) < 12 * 3600 else 'PM'
    # keep the first time's 12-hour turn: rebuild with absolute seconds
    column_abs(fake, stops, tid.startswith('W'), days, newid, note)
def column_abs(fake, stops, west, days, tid, note):
    tr = dict(fake); tt = {nm: (t, None) for nm, t in stops.items()}
    global parse
    old = parse; parse = lambda _tr, tt=tt: tt
    try: column(tr, west, days, tid, note)
    finally: parse = old
ALLW = set(TRUNK)
EST = 'Listed among the "additional trains" without times; timed from a printed train with the same stops (estimated). '
ADD_W = [('12.18 AM', 'daily'), ('1.35 AM', 'daily'), ('6.40 AM', 'daily exc Sun'), ('7.15 AM', 'daily exc Sun'), ('7.40 AM', 'daily exc Sun'), ('9.10 AM', 'daily'),
         ('10.10 AM', 'daily'), ('11.10 AM', 'daily'), ('12.10 PM', 'daily'), ('1.10 PM', 'daily'), ('1.35 PM', 'daily'), ('2.10 PM', 'daily'), ('2.35 PM', 'daily'),
         ('3.10 PM', 'daily'), ('3.40 PM', 'daily exc Sun'), ('4.47 PM', 'daily exc Sat & Sun'), ('4.57 PM', 'daily exc Sun'), ('5.35 PM', 'Sat & Sun only'),
         ('5.37 PM', 'daily exc Sat & Sun'), ('5.55 PM', 'daily exc Sun'), ('7.10 PM', 'daily'), ('10.45 PM', 'daily'), ('11.15 PM', 'daily')]
for s, d in ADD_W: shifted('W2035', s, d, ALLW, 'WX' + s.replace('.', '').replace(' ', ''), EST)
ADD_E = [('6.02 AM', 'daily exc Sun'), ('6.44 AM', 'daily exc Sun'), ('6.50 AM', 'daily exc Sun'), ('6.53 AM', 'daily exc Sun'), ('6.55 AM', 'daily exc Sun'),
         ('7.15 AM', 'daily exc Sat & Sun'), ('7.22 AM', 'daily exc Sun'), ('7.43 AM', 'daily exc Sun'), ('7.56 AM', 'daily exc Sun'), ('9.00 AM', 'daily exc Sun'),
         ('10.00 AM', 'daily'), ('10.30 AM', 'daily'), ('12.30 PM', 'daily'), ('1.00 PM', 'daily'), ('2.00 PM', 'daily'), ('2.30 PM', 'daily exc Sat'), ('3.00 PM', 'daily'),
         ('3.30 PM', 'daily'), ('4.00 PM', 'daily'), ('6.00 PM', 'daily'), ('9.30 PM', 'daily'), ('10.00 PM', 'daily'), ('11.00 PM', 'daily')]
WHE_E = {'Wheaton', 'Glen Ellyn', 'Lombard', 'Villa Park (Villa Ave.)', 'Elmhurst (York St.)', 'Wells Street'}
for s, d in ADD_E: shifted('E0930', s, d, WHE_E, 'EX' + s.replace('.', '').replace(' ', ''), EST)
for s in ['4.15 AM', '5.14 AM']: shifted('W0905', s, 'daily exc Sun', {'Wheaton', 'Lakewood', 'Wayne', 'Elgin'}, 'WE' + s.replace('.', '').replace(' ', ''), EST)
shifted('W0905', '4.30 AM', 'daily exc Sun', {'Wheaton', 'Warrenville', 'Aurora'}, 'WA0430AM', EST)
for s in ['5.00 AM', '5.28 AM']: shifted('W0905', s, 'daily exc Sun', {'Wheaton', 'Warrenville', 'Batavia'}, 'WB' + s.replace('.', '').replace(' ', ''), EST)
shifted('E0043', '1.40 AM', 'daily', {'Batavia', 'Warrenville', 'Wheaton'}, 'EB0140AM', EST)
SUN = 'Additional Sunday service; timed from the weekday train at about the same hour (estimated). '
for s, tpl in [('7.00 AM', 'W0700'), ('8.00 AM', 'W0800'), ('4.05 PM', 'W1605'), ('5.05 PM', 'W1708'), ('6.05 PM', 'W1810')]:
    shifted(tpl, s, 'Sun only', set(TRUNK) | {'Warrenville', 'Aurora', 'Batavia', 'Lakewood', 'Wayne', 'Elgin'}, 'WS' + s.replace('.', '').replace(' ', ''), SUN)
for s, tpl in [('6.00 AM', 'E0549'), ('7.28 AM', 'E0714'), ('5.28 PM', 'E1728')]:
    shifted(tpl, s, 'Sun only', {'Elgin', 'Wayne', 'Lakewood'} | WHE_E, 'ESE' + s.replace('.', '').replace(' ', ''), SUN)
for s, tpl in [('6.00 AM', 'E0505'), ('7.30 AM', 'E0714'), ('5.30 PM', 'E1728')]:
    shifted(tpl, s, 'Sun only', {'Aurora', 'Warrenville'} | WHE_E, 'ESA' + s.replace('.', '').replace(' ', ''), SUN)
for s, tpl in [('7.28 AM', 'E0650'), ('5.28 PM', 'E1728')]:
    shifted(tpl, s, 'Sun only', {'Batavia', 'Warrenville', 'Wheaton'}, 'ESB' + s.replace('.', '').replace(' ', ''), SUN)
for s, keep, k in [('5.00 AM', {'Wheaton', 'Lakewood', 'Wayne', 'Elgin'}, 'E'), ('6.55 AM', {'Wheaton', 'Lakewood', 'Wayne', 'Elgin'}, 'E'),
                   ('5.25 AM', {'Wheaton', 'Warrenville', 'Aurora'}, 'A'), ('6.55 AM', {'Wheaton', 'Warrenville', 'Aurora'}, 'A'), ('6.55 AM', {'Wheaton', 'Warrenville', 'Batavia'}, 'B')]:
    shifted('W0905', s, 'Sun only', keep, f'WS{k}' + s.replace('.', '').replace(' ', ''), SUN)

# lines: one per branch, both directions; track drawn once, 'L' track owned cta
OUT, DRAWN, ALLST = [], [], {}
def densify(route):
    out = []
    for a, b in zip(route, route[1:]):
        n = max(1, int(m(a, b) // 5))
        for k in range(n): out.append((a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n))
    return out
SRC = ("Chicago Aurora and Elgin: Official Guide, May 1948 (Brendan's scan); track Mississippi Rails (Tony Howe and David Price); 'L' track Chicago Transit Authority")
LABEL = {'aurora': 'Chicago – Wheaton – Aurora (CA&E)', 'batavia': 'Chicago – Wheaton – Batavia (CA&E)', 'elgin': 'Chicago – Wheaton – Elgin (CA&E)'}
for br in ('aurora', 'elgin', 'batavia'):
    route = ROUTE[br]; trips = TRIPS[br]
    names = sorted({s[0] for t in trips for s in t['stops']} | ({'Wells Street', 'Wheaton'}), key=lambda nm: CH[br][nm])
    idx = {nm: i for i, nm in enumerate(names)}
    st_ = []
    for nm in names:
        gid, disp, pt, pr, note = ST[nm]; ch = CH[br][nm]; p = at(route, ch)
        s = dict(name=disp, chain=round(ch, 1), lon=round(p[0], 6), lat=round(p[1], 6), mile=round(ch / MI, 2), principal=pr, gid=gid, note=note)
        st_.append(s); ALLST.setdefault(gid, s)
    tree = cKDTree([xy(p) for p in DRAWN]) if DRAWN else None
    segs, cur = [], None
    for a, b in zip(route, route[1:]):
        shared = tree is not None and tree.query(xy(a))[0] < 5 and tree.query(xy(b))[0] < 5
        own = 'none' if shared else ('cta' if a[3] and b[3] else 'cae')
        if cur and cur['owner'] == own and abs(cur['b'] - a[2]) < 0.01: cur['b'] = b[2]
        else: cur = dict(owner=own, a=a[2], b=b[2]); segs.append(cur)
    segs = [s for s in segs if s['owner'] != 'none']
    DRAWN += densify(route)
    for t in trips: t['stops'] = [[idx[nm], s, s, tp] for nm, s, tp in t['stops']]
    OUT.append(dict(key='cae_' + br, kind='H', label=LABEL[br], mainline=True, owner='none', livery='cae', src=SRC,
                    route=[[p[0], p[1], p[2]] for p in route], stations=st_, dirLabels=['westbound', 'eastbound'], segments=segs, trips=trips))
    print(f"cae_{br}: {route[-1][2] / MI:.2f} mi, {len(st_)} stations, {len(trips)} trips, drawn {sum(s['b'] - s['a'] for s in segs) / MI:.1f} mi")
ids = [t['id'] for L in OUT for t in L['trips']]; assert len(ids) == len(set(ids)), sorted(i for i in set(ids) if ids.count(i) > 1)
if os.environ.get('CAE_DRY'): raise SystemExit
vd = json.load(open(os.path.join(HERE, 'viz_data.json')))
vd['lines'] = [x for x in vd['lines'] if not x['key'].startswith('cae_')] + OUT
open(os.path.join(HERE, 'viz_data.json'), 'w').write(json.dumps(vd, separators=(',', ':')))
def fmt(x): return f'{x // 3600:02d}:{x % 3600 // 60:02d}:{x % 60:02d}'
def app(name, rows_):
    with open(os.path.join(GT, name), 'a', newline='') as fh: csv.writer(fh).writerows(rows_)
def have(name, col=0): return set(r[col] for r in csv.reader(open(os.path.join(GT, name))))
cal = have('calendar.txt')
for d in sorted({t['svc'] for L in OUT for t in L['trips']} - cal): app('calendar.txt', [[d, *d[2:], '19490616', '19491231']])
if 'CAE' not in have('agency.txt'): app('agency.txt', [['CAE', 'Chicago Aurora and Elgin Railroad', 'https://en.wikipedia.org/wiki/Chicago_Aurora_and_Elgin_Railroad', 'America/Vancouver', 'en', '']])
seen = have('stops.txt')
app('stops.txt', [[s['gid'], s['name'], f"{s['lat']:.6f}", f"{s['lon']:.6f}", s['note']] for s in ALLST.values() if s['gid'] not in seen])
for L in OUT:
    rid = L['key'].upper()
    app('routes.txt', [[rid, 'CAE', 'CA&E', L['label'], 0, 'C8102E', 'FFFFFF', L['src'] + '. Times on the Pacific clock.']])
    app('shapes.txt', [[rid, f'{p[1]:.6f}', f'{p[0]:.6f}', k, f'{p[2]:.1f}'] for k, p in enumerate(L['route'])])
    for t in L['trips']:
        app('trips.txt', [[rid, t['svc'], t['id'], L['stations'][t['stops'][-1][0]]['name'], t['name'], t['dir'], rid]])
        app('stop_times.txt', [[t['id'], fmt(a), fmt(b), L['stations'][i]['gid'], k, f"{L['stations'][i]['chain']:.1f}", tp] for k, (i, a, b, tp) in enumerate(t['stops'], 1)])
