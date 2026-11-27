"""Chicago South Shore & South Bend Railroad (the South Shore Line; Brendan, 26 Nov 2026): Chicago (Randolph Street) - Kensington - Hammond - Gary - Michigan City - South Bend.
Sources:
- Times: Official Guide, May 1948 (the table dated April 25, 1948; Brendan's scans, private repo scans/cssb/), transcribed in timetables_cssb/cssb_east.txt and cssb_west.txt.
  Central Daylight time as printed; shown on the Pacific clock (three hours earlier). Holidays: the table says July 5, 1948 runs the Sunday schedule, and Brendan agreed
  (26 Nov 2026): on this line Monday 5 July is a Sunday (trains marked daily except Sunday, or except Sunday and holidays, do not run that day).
- Track: tools/cssb_extract.py -> traces/chicago/cssb_route.json: the CSS&SB from the KMZ Brendan sent (mapped by Doug Spurling) with the 1948 East Chicago street line and the line
  into downtown South Bend; Kensington - Randolph Street over the Illinois Central (Brendan: like the Michigan Central's trains, but through past Central Station to the IC's
  downtown commuter terminals), drawn as IC track.
- Stations: the IC stations shared with the Michigan Central (Central Station, Woodlawn, Kensington); the others by printed mileage along the line (approximate).
Livery: orange and maroon (Claude's pick; to confirm)."""
import csv, json, math, os, re
HERE = os.path.dirname(os.path.abspath(__file__))
GT = os.path.join(HERE, 'gtfs')
TT = os.path.join(HERE, 'timetables_cssb')
RJ = json.load(open(os.path.join(HERE, 'traces', 'chicago', 'cssb_route.json')))
C0 = math.cos(math.radians(41.7)); MI = 1609.34
def m(a, b): return math.hypot((a[0] - b[0]) * 111320 * C0, (a[1] - b[1]) * 110570)
route, d = [], 0.0
for k, p in enumerate(RJ['route']):
    if k: d += m(RJ['route'][k - 1], p)
    route.append([p[0], p[1], round(d, 1), p[2]])
TOT = route[-1][2]
IC_END = max(p[2] for p in route if p[3])
def proj(q):
    best = None
    for a, b in zip(route, route[1:]):
        dx, dy = b[0] - a[0], b[1] - a[1]; t = max(0, min(1, ((q[0] - a[0]) * dx + (q[1] - a[1]) * dy) / ((dx * dx + dy * dy) or 1e-18)))
        f = (a[0] + t * dx, a[1] + t * dy); dd = m(q, f)
        if best is None or dd < best[0]: best = (dd, a[2] + t * (b[2] - a[2]))
    return best[1]
def at(ch):
    for a, b in zip(route, route[1:]):
        if a[2] <= ch <= b[2]:
            t = (ch - a[2]) / ((b[2] - a[2]) or 1); return (a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1]))
    return tuple(route[-1][:2])
KENS = proj((-87.612394, 41.683606))
def by_mile(mi): return KENS + (mi - 14) / (90 - 14) * (TOT - KENS)
IC = 'Illinois Central station'
MILE = 'placed by its printed mileage (approximate)'
# name: (gid, display name, chain, principal, note)
ST = {
 'Randolph Street': ('IC_RANDOLPH_STREET', 'Randolph Street, Chicago', 0.0, True, IC + ' (suburban terminal)'),
 'Van Buren Street': ('IC_VAN_BUREN_STREET', 'Van Buren Street, Chicago', proj((-87.6241, 41.8768)), False, IC + ' (approximate)'),
 'Roosevelt Road': ('NYC_CHICAGO_CENTRAL_ILL', 'Central Station, Chicago', proj((-87.622271, 41.867509)), True, IC + ' (Roosevelt Road)'),
 'Hyde Park (53rd Street)': ('IC_HYDE_PARK_53RD', 'Hyde Park (53rd Street), Chicago', proj((-87.5875, 41.7995)), False, IC + ' (approximate)'),
 'Woodlawn (63rd Street)': ('NYC_WOODLAWN_63D_STREET_ILL', 'Woodlawn (63d Street), Ill.', proj((-87.590915, 41.778482)), False, IC),
 'Kensington': ('NYC_KENSINGTON_ILL', 'Kensington, Ill.', KENS, True, IC),
}
MILES = {'Ford City': 17, 'Hegewisch': 19, 'Burnham': 19.3, 'Hammond': 21, 'East Chicago': 23, 'Calumet': 24, 'Cudahy': 25, 'Gary': 31, 'Miller': 35, 'Ogden Dunes': 39,
         'Wilson': 40, 'Dune Acres': 45, 'Port Chester': 46, 'Tremont': 47, 'Michigan City': 56, 'Smith': 68, 'Lake Park': 74, 'Hudson Lake': 75, 'New Carlisle': 76,
         'Lydick': 83, "Chain O'Lakes": 84, 'Bendix Drive': 88, 'South Bend': 90}
PRINC = {'Hammond', 'East Chicago', 'Gary', 'Michigan City', 'South Bend', 'Hegewisch', 'New Carlisle'}
DISP = {'Dune Acres': 'Dune Acres (Mineral Springs)', 'Tremont': 'Tremont (The Dunes)', 'Ford City': 'Ford City, Chicago', 'Hegewisch': 'Hegewisch, Chicago',
        'Burnham': 'Burnham, Ill.', 'Michigan City': 'Michigan City (South Shore)', 'South Bend': 'South Bend (South Shore)', 'Hammond': 'Hammond (South Shore)',
        'Gary': 'Gary (South Shore)', 'East Chicago': 'East Chicago (South Shore)'}
for nm, mi in MILES.items():
    ST[nm] = ('CSSB_' + re.sub(r'[^A-Z0-9]+', '_', nm.upper()).strip('_'), DISP.get(nm, nm), by_mile(mi) if mi < 90 else TOT, nm in PRINC,
              'South Shore Line station; ' + (MILE if mi < 90 else 'downtown terminal at the end of the 1948 line (approximate)'))
NAMES = sorted(ST, key=lambda n: ST[n][2]); IDX = {n: i for i, n in enumerate(NAMES)}
def read(fn):
    head, trains = None, []
    for line in open(os.path.join(TT, fn)):
        if line.startswith('#') or not line.strip(): continue
        if line.startswith('STATIONS'): head = [s.strip() for s in line.split('=', 1)[1].split(';')]; continue
        num, days, flags, ap, times = [x.strip() for x in line.split('|')]
        trains.append(dict(num=num, days=days, ap=ap, times=times.split()))
    return head, trains
def tsec(tr):
    out, prev = [], None
    for x in tr['times']:
        if x == '-': out.append(None); continue
        h, mm = map(int, x.lstrip('~').split('.')); t = (h % 12) * 3600 + mm * 60
        if prev is None: t += 12 * 3600 if tr['ap'] == 'PM' else 0
        else:
            while t < prev: t += 12 * 3600
        prev = t; out.append(t)
    return out
# Mon (the July 5 holiday: Sunday schedule) ... Sun
DAYS = {'*': '1111111', 'a': '0111110', 'y': '0111100'}
DAYTXT = {'*': 'daily', 'a': 'daily except Sunday and holidays', 'y': 'daily except Saturday, Sunday and holidays'}
SHIFT = -3 * 3600
ARR = {'602': ('Michigan City', 3 * 3600 + 25 * 60)}            # no Michigan City arrival printed: estimated from Smith 3.05 a.m.
EXTRA = {'GX': [('Gary', 0), ('Miller', 4 * 60), ('Ogden Dunes', 10 * 60), ('Wilson', 12 * 60), ('Dune Acres', 17 * 60), ('Port Chester', 18 * 60), ('Tremont', 21 * 60),
                ('Michigan City', 43 * 60)]}                    # the additional train Gary 6.57 p.m.: No. 203's running times from Gary (estimated)
NOTE = {'X108': 'Joins No. 8 at Gary (the columns merge).', 'X202': 'Joins No. 10 at Gary (the columns merge).', 'GX': 'The additional train, Gary to Michigan City; times after Gary estimated from No. 203.',
        '602': 'No Michigan City arrival printed (it leaves at 4.45 a.m.): estimated.', '5': 'Starts at Michigan City.', '6': 'Starts at Michigan City.', '200': 'Starts at Michigan City.'}
def ampm(s): h, mm = divmod(s // 60, 60); h %= 24; return f"{(h - 1) % 12 + 1}.{mm:02d} {'a.m.' if h < 12 else 'p.m.'}"
trips = []
for fn, east in (('cssb_east.txt', True), ('cssb_west.txt', False)):
    head, trains = read(fn)
    for tr in trains:
        tt = tsec(tr); stops = [(head[i], t, 1) for i, t in enumerate(tt) if t is not None]
        if tr['num'] in EXTRA:
            t0 = stops[0][1]; stops = [(nm, t0 + off, 1 if not off else 0) for nm, off in EXTRA[tr['num']]]
        arr = {}
        if tr['num'] in ARR: arr[ARR[tr['num']][0]] = ARR[tr['num']][1]
        rows = []
        for nm, t, tp in stops:
            a = arr.get(nm, t); rows.append([IDX[nm], a + SHIFT, t + SHIFT, tp])
        rows.sort(key=lambda r: ST[NAMES[r[0]]][2] * (1 if east else -1))
        dd = DAYS[tr['days']]; svc_days = [i for i in range(7) if dd[i] == '1']
        if rows[0][1] < 0:
            for r in rows: r[1] += 86400; r[2] += 86400
            svc_days = sorted((i - 1) % 7 for i in svc_days)
        assert all(x[2] <= y[1] for x, y in zip(rows, rows[1:])), (tr['num'], rows)
        frm, to = NAMES[rows[0][0]], NAMES[rows[-1][0]]
        num = tr['num'] if tr['num'] != 'GX' else 'Train'
        trips.append(dict(id=f"CSSB-{tr['num']}", num=num, name='South Shore Line', svc='W_' + ''.join('1' if i in svc_days else '0' for i in range(7)), dir=0 if east else 1,
                          stops=rows, motor=True,
                          note=(f"No. {tr['num']}, " if num != 'Train' else '') + f"{ST[frm][1]} {ampm(stops[0][1])} to {ST[to][1]} {ampm(stops[-1][1])} (Central Daylight time, as printed); "
                               f"{DAYTXT[tr['days']]} (Monday 5 July 1948 ran the Sunday schedule). " + (NOTE.get(tr['num'], '') + ' ' if tr['num'] in NOTE else '') +
                               'Official Guide, May 1948. Shown in Pacific time.'))
stations = []
for nm in NAMES:
    gid, disp, ch, pr, note = ST[nm]; p = at(ch)
    stations.append(dict(name=disp, chain=round(ch, 1), lon=round(p[0], 6), lat=round(p[1], 6), mile=round(ch / MI, 2), principal=pr, gid=gid, note=note))
SRC = ("South Shore Line (Chicago South Shore & South Bend): Official Guide, May 1948 (Brendan's scan); track: Doug Spurling's map (via Brendan) with the 1948 East Chicago and "
       "South Bend lines; Illinois Central (Mississippi Rails) into Chicago")
LINE = dict(key='cssb', kind='I', label='Chicago – Gary – Michigan City – South Bend (South Shore Line)', mainline=True, owner='cssb', livery='cssb', src=SRC,
            route=[[p[0], p[1], p[2]] for p in route], stations=stations, dirLabels=['to South Bend', 'to Chicago'], segments=[dict(owner='ic', a=0.0, b=round(IC_END, 1))], trips=trips)
print(f'cssb: {TOT / MI:.2f} mi ({IC_END / MI:.2f} on the IC), {len(stations)} stations, {len(trips)} trips')
if os.environ.get('CSSB_DRY'):
    for s in stations: print(f"   {s['mile']:6.2f} {s['name']}")
    raise SystemExit
vd = json.load(open(os.path.join(HERE, 'viz_data.json')))
vd['lines'] = [x for x in vd['lines'] if x['key'] != 'cssb'] + [LINE]
open(os.path.join(HERE, 'viz_data.json'), 'w').write(json.dumps(vd, separators=(',', ':')))
def fmt(x): return f'{x // 3600:02d}:{x % 3600 // 60:02d}:{x % 60:02d}'
def app(name, rows_):
    with open(os.path.join(GT, name), 'a', newline='') as fh: csv.writer(fh).writerows(rows_)
def have(name, col=0): return set(r[col] for r in csv.reader(open(os.path.join(GT, name))))
cal = have('calendar.txt')
for dd in sorted({t['svc'] for t in trips} - cal): app('calendar.txt', [[dd, *dd[2:], '19490616', '19491231']])
if 'CSSB' not in have('agency.txt'): app('agency.txt', [['CSSB', 'Chicago South Shore and South Bend Railroad', 'https://en.wikipedia.org/wiki/Chicago_South_Shore_and_South_Bend_Railroad', 'America/Vancouver', 'en', '']])
seen = have('stops.txt')
app('stops.txt', [[s['gid'], s['name'], f"{s['lat']:.6f}", f"{s['lon']:.6f}", s['note']] for s in stations if s['gid'] not in seen])
app('routes.txt', [['CSSB', 'CSSB', 'South Shore Line', LINE['label'], 0, 'E0701E', 'FFFFFF', SRC + '. Times on the Pacific clock.']])
app('shapes.txt', [['CSSB_E', f'{p[1]:.6f}', f'{p[0]:.6f}', k, f'{p[2]:.1f}'] for k, p in enumerate(route)])
app('shapes.txt', [['CSSB_W', f'{p[1]:.6f}', f'{p[0]:.6f}', k, f'{TOT - p[2]:.1f}'] for k, p in enumerate(route[::-1])])
for t in trips:
    app('trips.txt', [['CSSB', t['svc'], t['id'], stations[t['stops'][-1][0]]['name'], 'South Shore Line', t['dir'], 'CSSB_' + 'EW'[t['dir']]]])
    app('stop_times.txt', [[t['id'], fmt(a), fmt(b), stations[i]['gid'], k, f"{(stations[i]['chain'] if t['dir'] == 0 else TOT - stations[i]['chain']):.1f}", tp]
                           for k, (i, a, b, tp) in enumerate(t['stops'], 1)])
