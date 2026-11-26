"""Chicago North Shore & Milwaukee Railroad (the North Shore Line; Brendan, 25 Nov 2026), first pass: the Chicago - Milwaukee trains of the Skokie Valley Route.
Sources:
- Times: CNS&M Timetable G-54, June 5, 1949 (reprint May 1950), pages 1 - 4 (Illinois Railway Museum CTA collection,
  http://irm-cta.org/NSL/TT/NSL%20Timetable%201949-06-05%20(2).pdf), transcribed in timetables_cnsm/sv_north.txt and sv_south.txt. The 1949 schedule stands in for July 1948
  (Brendan: the 1948 Official Guide, April 25, 1948, shows the same pattern within a few minutes). Chicago Daylight Saving time as printed; trains printed "will not run during
  Daylight Saving Time" are left out. Shown on the Pacific clock (three hours earlier).
- Track: Mississippi Rails (Tony Howe and David Price), Chicago interurbans KML, cut by tools/chi_extract.py into traces/chicago/cnsm_routes.json. Northbound trains go round the
  Loop by Wabash Avenue and Lake Street, southbound by Wells Street and Van Buren Street (Brendan), so each direction is its own line on the page. Roosevelt Road - Howard Street
  is Chicago Transit Authority 'L' track (owner cta, the rapid-transit class; Brendan: dark blue, not navy); the North Shore Line's own track (turquoise) from Howard Street.
- Stations: Mississippi Rails station polygons where they are named, 'L' stations from the same file, and the rest (Dempster Street, North Chicago Junction, Racine, the four
  Milwaukee street stops) placed by street or by the timetable's running times: approximate.
- Electroliners (the starred trains) carry the name Electroliner. Livery: Electroliner turquoise and salmon (Brendan)."""
import csv, json, math, os, re
HERE = os.path.dirname(os.path.abspath(__file__))
GT = os.path.join(HERE, 'gtfs')
TT = os.path.join(HERE, 'timetables_cnsm')
RT = json.load(open(os.path.join(HERE, 'traces', 'chicago', 'cnsm_routes.json')))['routes']
C0 = math.cos(math.radians(42.0))
def m(a, b): return math.hypot((a[0] - b[0]) * 111320 * C0, (a[1] - b[1]) * 110570)
def chained(pts):
    out, d = [], 0.0
    for k, p in enumerate(pts):
        if k: d += m(pts[k - 1], p)
        out.append([p[0], p[1], round(d, 1)])
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
    return tuple(route[-1][:2])
def cross(route, lat):
    for a, b in zip(route, route[1:]):
        if (a[1] - lat) * (b[1] - lat) <= 0 and a[1] != b[1]:
            t = (lat - a[1]) / (b[1] - a[1]); return a[2] + t * (b[2] - a[2])
    raise ValueError(lat)
NB, SB = chained(RT['sv_north']), chained(RT['sv_south'])
MI = 1609.34
# Station points: (lon, lat) from the Mississippi Rails file (station polygons, the 'L' stations), or ('lat', latitude) where the line crosses a street, or ('mi', miles on the
# northbound route) by the running times. (gid, name, point, principal, note)
POL = 'station polygon in the Mississippi Rails file'
STN = {
 'Roosevelt Road': ('CNSM_ROOSEVELT', 'Roosevelt Road', (-87.62662, 41.86728), True, "the South Side 'L' 12th Street station, " + POL),
 'Adams and Wabash': ('CNSM_ADAMS_WABASH', 'Adams & Wabash', (-87.62612, 41.87954), True, "'L' station, " + POL),
 'Madison & Wabash': ('CNSM_MADISON_WABASH', 'Madison & Wabash', (-87.62620, 41.88205), False, "'L' station, " + POL),
 'Randolph & Wabash': ('CNSM_RANDOLPH_WABASH', 'Randolph & Wabash', (-87.62625, 41.88452), False, "'L' station, " + POL),
 'Clark and Lake': ('CNSM_CLARK_LAKE', 'Clark & Lake', (-87.63101, 41.88575), False, "'L' station, " + POL),
 'Merchandise Mart': ('CNSM_MERCHANDISE_MART', 'Merchandise Mart', (-87.63402, 41.88916), False, "'L' station; placed at the old Kinzie Street station of the file (approximate)"),
 'Grand Avenue': ('CNSM_GRAND', 'Grand Avenue', (-87.63560, 41.89160), False, "'L' station, " + POL),
 'Chicago Avenue': ('CNSM_CHICAGO_AVE', 'Chicago Avenue', (-87.63608, 41.89685), False, "'L' station, " + POL),
 'Belmont Avenue': ('CNSM_BELMONT', 'Belmont Avenue', (-87.65342, 41.93970), False, "'L' station, " + POL),
 'Wilson Avenue': ('CNSM_WILSON', 'Wilson Avenue', (-87.65794, 41.96540), False, "'L' Wilson Avenue terminal, " + POL),
 'Howard Street': ('CNSM_HOWARD', 'Howard Street', (-87.67318, 42.01929), True, "'L' station, " + POL),
 'Dempster Street': ('CNSM_DEMPSTER', 'Dempster Street, Skokie', ('lat', 42.0412), False, 'placed where the line crosses Dempster Street (approximate)'),
 'Scranton Avenue': ('CNSM_SCRANTON_AVE', 'Scranton Avenue, Lake Bluff', (-87.84806, 42.28030), False, POL + ' (a stop at Scranton Avenue)'),
 "Downey's (West)": ('CNSM_DOWNEYS_WEST', "Downey's (West), Great Lakes", (-87.84716, 42.30687), False, POL),
 'North Chicago Junction': ('CNSM_NORTH_CHICAGO_JCT', 'North Chicago Junction', ('mi', 38.8), False, 'placed by the running times between Downey\'s and Edison Court (approximate)'),
 'Edison Court': ('CNSM_EDISON_COURT', 'Edison Court, Waukegan', (-87.84607, 42.35938), True, POL + ' (Washington Street passenger station)'),
 'Zion': ('CNSM_ZION', 'Zion', (-87.84519, 42.45123), False, POL + ' (Salem Boulevard)'),
 'Kenosha': ('CNSM_KENOSHA', 'Kenosha', (-87.84219, 42.57711), True, POL),
 'Racine': ('CNSM_RACINE', 'Racine', ('mi', 66.4), True, 'placed by the running times between Kenosha and Milwaukee (approximate)'),
 'Harrison Street': ('CNSM_MKE_HARRISON', 'Harrison Street, Milwaukee', ('lat', 42.9990), False, 'placed where the line crosses Harrison Avenue (approximate)'),
 'Mitchell Street': ('CNSM_MKE_MITCHELL', 'Mitchell Street, Milwaukee', ('lat', 43.0124), False, 'placed where the line crosses Mitchell Street (approximate)'),
 'Greenfield Ave.': ('CNSM_MKE_GREENFIELD', 'Greenfield Avenue, Milwaukee', ('lat', 43.0168), False, 'placed where the line crosses Greenfield Avenue (approximate)'),
 'National Avenue': ('CNSM_MKE_NATIONAL', 'National Avenue, Milwaukee', ('lat', 43.0237), False, 'placed where the line crosses National Avenue (approximate)'),
 '6th & Michigan Sts.': ('CNSM_MILWAUKEE', 'Milwaukee (6th & Michigan)', 'end', True, 'Downtown terminal, ' + POL),
 'Randolph & Wells': ('CNSM_RANDOLPH_WELLS', 'Randolph & Wells', (-87.63393, 41.88512), False, "'L' station (Randolph & Fifth), " + POL),
 'Madison & Wells': ('CNSM_MADISON_WELLS', 'Madison & Wells', (-87.63385, 41.88202), False, "'L' station (Madison & Fifth), " + POL),
 'Quincy & Wells': ('CNSM_QUINCY_WELLS', 'Quincy & Wells', (-87.63377, 41.87874), False, "'L' station (Quincy & Fifth), " + POL),
 'LaSalle & Van Buren': ('CNSM_LASALLE_VB', 'LaSalle & Van Buren', (-87.63186, 41.87688), False, "'L' station, " + POL),
 'Dearborn-State-Van Buren': ('CNSM_DEARBORN_STATE_VB', 'Dearborn-State-Van Buren', (-87.62846, 41.87692), False, "'L' station, between the file's Dearborn and State stations"),
}
STN['Greenfield Avenue'] = STN['Greenfield Ave.']
def place(route, names, north):
    out = []
    for nm in names:
        gid, name, pt, principal, note = STN[nm]
        if pt == 'end': ch = route[-1][2] if north else 0.0
        elif pt[0] == 'lat': ch = cross(route, pt[1])
        elif pt[0] == 'mi': ch = proj(route, at(NB, pt[1] * MI))[1]
        else: ch = proj(route, pt)[1]
        p = at(route, ch)
        out.append(dict(name=name, chain=round(ch, 1), lon=round(p[0], 6), lat=round(p[1], 6), mile=round(ch / MI, 2), principal=principal, gid=gid, note=note))
    return out
def read(fn):
    head, trains = None, []
    for line in open(os.path.join(TT, fn)):
        if line.startswith('#') or not line.strip(): continue
        if line.startswith('STATIONS'): head = [s.strip() for s in line.split('=', 1)[1].split(';')]; continue
        num, days, flags, ap, times = [x.strip() for x in line.split('|')]
        trains.append(dict(num=num, days=days, flags=flags, ap=ap, times=times.split()))
    return head, trains
DAYS = {'daily': '1111111', 'daily exc Sun': '1111110', 'Sun only': '0000001', 'Sat & Sun only': '0000011', 'Sat only': '0000010', 'daily exc Sat & Sun': '1111100'}
COND = {'K': '1111100', 'J': '1111110', 'L': '0000010', 'M': '1111101', 'S': '0000001', 'W': '0000011'}   # conditional stops (Mon first)
DAYNAME = ['Mon.', 'Tue.', 'Wed.', 'Thu.', 'Fri.', 'Sat.', 'Sun.']
SHIFT = -3 * 3600     # Chicago Daylight Saving to Pacific Standard
def times(tr):
    """Seconds after midnight Chicago time for each printed time, AM / PM worked out along the column."""
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
def ampm(s): h, mm = divmod(s // 60, 60); h %= 24; return f"{(h - 1) % 12 + 1}.{mm:02d} {'a.m.' if h < 12 else 'p.m.'}"
LINES, ALLST = [], {}
for key, fn, route, north in (('cnsm_svn', 'sv_north.txt', NB, True), ('cnsm_svs', 'sv_south.txt', SB, False)):
    head, trains = read(fn)
    st = place(route, head, north)
    order = sorted(range(len(st)), key=lambda i: st[i]['chain'])
    assert order == list(range(len(st))), [st[i]['name'] for i in order]
    for s in st: ALLST.setdefault(s['gid'], s)
    trips = []
    for tr in trains:
        tt = times(tr); base = DAYS[tr['days']]
        groups = {}
        for dd in range(7):                     # split by day where a stop is conditional
            if base[dd] != '1': continue
            stops = tuple(i for i, v in enumerate(tt) if v and (not v[1] or COND[v[1]][dd] == '1'))
            groups.setdefault(stops, []).append(dd)
        elec = 'E' in tr['flags'].split()
        for g, (stops, dds) in enumerate(groups.items()):
            svc = 'W_' + ''.join('1' if d in dds else '0' for d in range(7))
            sts = [[i, tt[i][0] + SHIFT, tt[i][0] + SHIFT, 1] for i in stops]
            frm, to = st[stops[0]]['name'], st[stops[-1]]['name']
            days = 'daily' if len(dds) == 7 else ', '.join(DAYNAME[d] for d in dds)
            num = re.sub(r'\D', '', tr['num'])
            trips.append(dict(id=f"CNSM-{tr['num']}" + (f'-{g}' if len(groups) > 1 else ''), num=num, name='Electroliner' if elec else 'North Shore Line', svc=svc,
                              dir=0 if north else 1, stops=sts, motor=True,
                              note=(f'Electroliner No. {num}' if elec else f'No. {num}') + f', {frm} {ampm(tt[stops[0]][0])} to {to} {ampm(tt[stops[-1]][0])} (Chicago Daylight '
                                   f'Saving time, as printed); {days}. CNS&M Timetable G-54, June 5, 1949, standing in for July 1948. Shown in Pacific time.'))
    # track owners: 'L' (cta) up to Howard Street; on the southbound line the stretch shared with the northbound line is drawn once (owner none)
    hw = next(s['chain'] for s in st if s['gid'] == 'CNSM_HOWARD')
    if north:
        owner, segs = 'cnsm', [dict(owner='cta', a=0.0, b=hw)]
    else:
        owner, segs, cur = 'none', [], None
        for k, p in enumerate(route):
            own = proj(NB, p)[0] > 6 and p[2] > hw
            if own and cur is None: cur = route[max(k - 1, 0)][2]
            if not own and cur is not None: segs.append(dict(owner='cta', a=cur, b=p[2])); cur = None
        if cur is not None: segs.append(dict(owner='cta', a=cur, b=route[-1][2]))
    src = ('CNS&M Timetable G-54, June 5, 1949 (Illinois Railway Museum CTA collection, irm-cta.org), standing in for July 1948; track Mississippi Rails (Tony Howe and '
           'David Price); \'L\' track Chicago Transit Authority')
    LINES.append(dict(key=key, kind='F', label=f"Chicago – Milwaukee (North Shore Line, Skokie Valley Route, {'northbound by Wabash' if north else 'southbound by Wells'})",
                      mainline=True, owner=owner, livery='cnsm', src=src, route=[[round(p[0], 7), round(p[1], 7), p[2]] for p in route], stations=st,
                      dirLabels=['to Milwaukee', 'to Chicago'], segments=segs, trips=trips))
    print(f"{key}: {route[-1][2] / MI:.2f} mi, {len(st)} stations, {len(trips)} trips; segments {[(s['owner'], round(s['a']), round(s['b'])) for s in segs]}")
    for s in st: print(f"   {s['mile']:6.2f} {s['name']}")
if os.environ.get('CNSM_DRY'): raise SystemExit   # CNSM_DRY=1: place and time without writing
vd = json.load(open(os.path.join(HERE, 'viz_data.json')))
vd['lines'] = [x for x in vd['lines'] if not x['key'].startswith('cnsm_')] + LINES
open(os.path.join(HERE, 'viz_data.json'), 'w').write(json.dumps(vd, separators=(',', ':')))

def fmt(x): return f'{x // 3600:02d}:{x % 3600 // 60:02d}:{x % 60:02d}'
def app(name, rows_):
    with open(os.path.join(GT, name), 'a', newline='') as fh: csv.writer(fh).writerows(rows_)
def have(name, col=0): return set(r[col] for r in csv.reader(open(os.path.join(GT, name))))
cal = have('calendar.txt')
for d in sorted({t['svc'] for L in LINES for t in L['trips']} - cal): app('calendar.txt', [[d, *d[2:], '19490616', '19491231']])
if 'CNSM' not in have('agency.txt'): app('agency.txt', [['CNSM', 'Chicago North Shore & Milwaukee Railroad', 'https://en.wikipedia.org/wiki/Chicago_North_Shore_and_Milwaukee_Railroad', 'America/Vancouver', 'en', '']])
seen = have('stops.txt')
app('stops.txt', [[s['gid'], s['name'], f"{s['lat']:.6f}", f"{s['lon']:.6f}", s['note']] for s in ALLST.values() if s['gid'] not in seen])
for L in LINES:
    rid = L['key'].upper()
    app('routes.txt', [[rid, 'CNSM', 'North Shore Line', L['label'], 0, '2AA198', 'FFFFFF', L['src'] + '. Times on the Pacific clock.']])
    app('shapes.txt', [[rid, f'{p[1]:.6f}', f'{p[0]:.6f}', k, f'{p[2]:.1f}'] for k, p in enumerate(L['route'])])
    for t in L['trips']:
        app('trips.txt', [[rid, t['svc'], t['id'], L['stations'][t['stops'][-1][0]]['name'], t['name'], t['dir'], rid]])
        app('stop_times.txt', [[t['id'], fmt(a), fmt(b), L['stations'][i]['gid'], k, f"{L['stations'][i]['chain']:.1f}", tp] for k, (i, a, b, tp) in enumerate(t['stops'], 1)])
