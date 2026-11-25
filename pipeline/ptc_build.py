"""Portland Traction Company, Oregon City Division (Brendan, 24 Nov 2026: "an additional interurban"). Stand-alone step (copies ter_build.py).
Sources:
- Times and stations: Portland Traction Company, Portland Railroad and Terminal Division, Time Table No. 2, effective February 1, 1948, Oregon City Division (Brendan's scan; private
  repo scans/ptc/). Pacific Standard Time. Transcribed below as printed (the timing points Portland, Golf Jct., Milwaukie, Oak Grove, Meldrum, Gladstone, Oregon City); the other
  stations of the list (with its miles) are timed by distance between them (estimated). Moorage and Harney Avenue have no miles printed: placed half-way (Claude).
- Track: Brendan's Portland Railway, Light & Power Co. KMZ (raw in the private repo, traces/oregon/), the Oregon City line joined from its pieces (traces/oregon/
  portland_traction_oregon_city.json): 1st & Washington - Hawthorne Bridge - East Portland - The Oaks - Golf Junction - Milwaukie - Oregon City, 14.07 mi traced (13.94 printed).
  Stations placed by the printed miles, stretched to the track between Portland, Golf Junction and Oregon City.
Signs: X daily except Sunday; XX daily except Saturday and Sunday; O Oak Grove local; M Milwaukie local; E East Portland only; L leaves East Portland 10 minutes before the Golf Jct.
time; * no stops north of Oak Grove except to pick up (southbound; the minor stops north of Oak Grove are left out); + likewise north of Island; # limited to Lakewood. Rows without a
Portland time begin at Golf Jct. "All Oak Grove trains make local stops on Saturday; all Oregon City trains make local stops on Sunday" (not modelled: the limited trains skip every day).
Colour #2f6f8f is Claude's pick."""
import csv, json, math, os
HERE = os.path.dirname(os.path.abspath(__file__))
GT = os.path.join(HERE, 'gtfs')
TR = json.load(open(os.path.join(HERE, 'traces', 'oregon', 'portland_traction_oregon_city.json')))
def km(a, b): return math.hypot((a[0] - b[0]) * 111.32 * math.cos(math.radians((a[1] + b[1]) / 2)), (a[1] - b[1]) * 110.57)
route, d = [], 0.0
for k, p in enumerate(TR['coords']):
    if k: d += km(TR['coords'][k - 1], p) * 1000
    route.append([p[0], p[1], round(d, 1)])
TOT = route[-1][2]
GOLF = min(route, key=lambda p: km(p, (-122.6538, 45.4584)))[2]
# (name, printed miles, timing column)
ST = [('Portland', 0, 'P'), ('East Portland', 0.81, None), ('Moorage', 2.37, None), ('The Oaks', 3.92, None), ('Chutes', 4.14, None), ('Spokane Ave.', 4.41, None),
      ('Harney Avenue', 4.72, None), ('Golf Junction', 5.02, 'G'), ('Ardgour', 5.45, None), ('Overlinks', 5.68, None), ('Knight', 5.96, None), ('Hendee', 6.07, None),
      ('Milwaukie', 6.31, 'M'), ('Island', 6.71, None), ('Lakewood', 7.14, None), ('Evergreen', 7.36, None), ('Silver Springs', 7.59, None), ('Torbank', 7.79, None),
      ('Courtney', 7.96, None), ('St. Theresa', 8.15, None), ('Oak Grove', 8.35, 'O'), ('Rupert', 8.75, None), ('Risley', 8.94, None), ('Concord', 9.19, None),
      ('Vinyard', 9.53, None), ('Naef', 9.86, None), ('Rothe', 10.07, None), ('Ashdale', 10.35, None), ('Jennings Lodge', 10.68, None), ('Hull Avenue', 10.84, None),
      ('Meldrum', 11.01, 'D'), ('Glen Echo', 11.14, None), ('Fern Ridge', 11.43, None), ('Gladstone', 11.95, 'S'), ('Park Place', 12.34, None), ('Oregon City', 13.94, 'C')]
def chain_of(mi):   # printed miles to metres along the track, stretched piecewise between Portland, Golf Junction and Oregon City
    return mi / 5.02 * GOLF if mi <= 5.02 else GOLF + (mi - 5.02) / (13.94 - 5.02) * (TOT - GOLF)
stations = []
for nm, mi, col in ST:
    ch = chain_of(mi)
    j = max(i for i in range(len(route)) if route[i][2] <= ch); a, b = route[j], route[min(j + 1, len(route) - 1)]
    f = (ch - a[2]) / ((b[2] - a[2]) or 1)
    gid = 'PTC_' + nm.upper().replace('.', '').replace(' ', '_')
    note = {'Portland': 'Portland, S.W. 1st Avenue and Washington Street', 'East Portland': 'East Portland, S.E. 1st Avenue and Hawthorne Boulevard',
            'Oregon City': 'Oregon City, 5th and Main Streets'}.get(nm, nm) + ('; placed by the printed miles (approximate)' if nm not in ('Portland', 'Oregon City') else '')
    if nm in ('Moorage', 'Harney Avenue'): note = nm + ': no miles printed; placed half-way between its neighbours (approximate)'
    stations.append(dict(name=nm, chain=round(ch, 1), lon=round(a[0] + f * (b[0] - a[0]), 6), lat=round(a[1] + f * (b[1] - a[1]), 6), mile=mi, principal=col is not None or nm == 'East Portland',
                         gid=gid, note=note, zname=nm, city=nm))
IDX = {c: i for i, (_, _, c) in enumerate(ST) if c}
# Portland to Oregon City: sign, then P G M O D S C ('-' not served; 'L' / first time at G with no P = begins at Golf Jct.). Times h.mm; a.m. / p.m. from the light / dark face.
SOUTH = '''
 | 0.35 0.50 0.54 1.01 1.08 1.11 1.20
 | 1.35 1.50 1.54 2.01 2.08 2.11 2.20
 | 3.35 3.50 3.54 4.01 4.08 4.11 4.20
 | - 4.50 4.54 5.01 5.08 5.11 5.20
X | - 5.15 5.19 5.26 5.33 5.36 5.45
 | 5.30 5.46 5.50 5.57 6.04 6.07 6.16
X | - 6.15 6.19 6.26 6.33 6.36 6.45
OXXL | - 6.32 6.36 6.43 - - -
 | 6.30 6.46 6.50 6.57 7.04 7.07 7.16
OXXL | - 6.56 7.00 7.07 - - -
X | 7.00 7.16 7.20 7.27 7.34 7.37 7.46
OXX | 7.20 7.36 7.40 7.47 - - -
 | 7.30 7.46 7.51 7.57 8.04 8.08 8.17
X | 8.00 8.16 8.20 8.27 8.34 8.37 8.46
 | 8.30 8.46 8.50 8.57 9.04 9.07 9.16
 | 9.00 9.16 9.20 9.27 9.34 9.37 9.46
 | 9.30 9.46 9.50 9.57 10.04 10.07 10.16
 | 10.00 10.16 10.20 10.27 10.34 10.37 10.46
 | 10.30 10.46 10.50 10.57 11.04 11.07 11.16
 | 11.00 11.16 11.20 11.27 11.34 11.37 11.46
 | 11.30 11.46 11.50 11.57 12.04 12.07 12.16
 | 12.01 12.16 12.20 12.27 12.34 12.37 12.46
 | 12.30 12.46 12.50 12.57 13.04 13.07 13.16
 | 13.00 13.16 13.20 13.27 13.34 13.37 13.46
 | 13.30 13.46 13.50 13.57 14.04 14.07 14.16
 | 14.00 14.16 14.20 14.27 14.34 14.37 14.46
 | 14.30 14.46 14.50 14.57 15.04 15.07 15.16
 | 15.00 15.16 15.21 15.29 15.36 15.40 15.50
* | 15.30 15.45 15.50 15.56 16.03 16.07 16.20
OX | 15.35 15.51 15.58 16.07 - - -
+ | 16.00 16.16 16.20 16.27 16.35 16.39 16.50
MX | 16.05 16.21 16.26 - - - -
# | 16.30 16.46 16.50 16.57 17.06 17.10 17.20
OX | 16.35 16.51 16.56 17.03 - - -
* | 17.00 17.16 17.20 17.27 17.35 17.39 17.50
OX+ | 17.05 17.21 17.25 17.33 - - -
MXX | 17.10 17.26 17.30 - - - -
* | 17.30 17.46 17.50 17.58 18.06 18.10 18.20
OX+ | 17.35 17.51 17.55 18.03 - - -
MXX | 17.40 17.56 18.00 - - - -
* | 18.00 18.16 18.20 18.27 18.35 18.39 18.50
OX | 18.05 18.21 18.25 18.33 - - -
 | 18.30 18.46 18.50 18.57 19.04 19.07 19.18
 | 19.00 19.16 19.20 19.27 19.34 19.37 19.48
 | 19.30 19.46 19.50 19.57 20.04 20.07 20.18
 | 20.00 20.15 20.19 20.28 20.35 20.39 20.48
 | 20.30 20.46 20.51 20.58 21.05 21.09 21.18
 | 21.30 21.46 21.51 21.58 22.05 22.09 22.18
 | 22.30 22.46 22.51 22.58 23.05 23.09 23.18
 | 23.30 23.46 23.51 23.58 24.05 24.09 24.18'''
# Oregon City to Portland: sign, then C S D O M G P
NORTH = '''
 | 0.35 0.46 0.50 0.57 1.04 1.08 1.24
E | 1.28 1.37 1.40 1.47 1.54 1.58 -
 | 2.30 2.41 2.44 2.52 2.58 3.02 3.20
 | 4.30 4.41 4.44 4.52 4.58 5.02 5.20
 | 5.30 5.40 5.44 5.53 6.00 6.04 6.20
X | 6.00 6.11 6.15 6.24 6.31 6.35 6.51
OXX | - - - 6.48 6.54 6.59 7.15
 | 6.30 6.40 6.44 6.53 7.00 7.04 7.20
OXX | - - - 7.17 7.24 7.28 7.45
X | 7.00 7.11 7.15 7.24 7.31 7.35 7.51
 | 7.20 7.30 7.34 7.43 7.51 7.55 8.11
OXX | - - - 7.55 8.02 8.06 8.22
X | 8.00 8.12 8.16 8.25 8.32 8.36 8.53
 | 8.30 8.41 8.45 8.54 9.01 9.05 9.25
X | 9.00 9.11 9.15 9.24 9.31 9.35 9.55
 | 9.30 9.41 9.45 9.54 10.01 10.05 10.25
 | 10.00 10.11 10.15 10.24 10.31 10.35 10.55
 | 10.30 10.41 10.45 10.54 11.01 11.05 11.25
 | 11.00 11.11 11.15 11.24 11.31 11.35 11.55
 | 11.30 11.41 11.45 11.54 12.01 12.05 12.25
 | 12.01 12.11 12.15 12.24 12.31 12.35 12.55
 | 12.30 12.41 12.45 12.54 13.01 13.05 13.25
 | 13.00 13.11 13.15 13.24 13.31 13.35 13.55
 | 13.30 13.41 13.45 13.54 14.01 14.05 14.25
 | 14.00 14.11 14.15 14.24 14.31 14.35 14.55
 | 14.30 14.41 14.45 14.54 15.01 15.05 15.25
 | 15.00 15.11 15.15 15.25 15.32 15.37 15.55
 | 15.33 15.44 15.48 15.56 16.03 16.08 16.25
OX | - - - 16.12 16.20 16.24 16.40
 | 16.00 16.11 16.15 16.24 16.31 16.36 16.55
MX | - - - - 16.35 16.40 17.00
 | 16.30 16.40 16.44 16.53 17.00 17.04 17.25
OX | - - - 17.08 17.14 17.18 17.36
 | 17.00 17.10 17.14 17.23 17.30 17.34 17.52
MXX | - - - - 17.35 17.40 17.58
OXE | - - - 17.39 17.45 17.49 -
 | 17.30 17.40 17.44 17.53 18.00 18.05 18.25
MXEX | - - - - 18.05 18.09 -
OXE | - - - 18.09 18.15 18.19 -
 | 18.00 18.10 18.14 18.23 18.30 18.34 18.50
OXE | - - - 18.38 18.45 18.49 -
 | 18.30 18.40 18.44 18.53 19.00 19.04 19.25
 | 19.00 19.11 19.15 19.24 19.31 19.35 19.50
 | 19.30 19.41 19.45 19.54 20.01 20.05 20.20
 | 20.00 20.11 20.15 20.24 20.31 20.35 20.50
 | 20.30 20.39 20.42 20.50 20.56 21.00 21.20
 | 21.00 21.09 21.12 21.20 21.26 21.30 21.48
 | 21.30 21.39 21.42 21.50 21.56 22.00 22.20
 | 22.30 22.39 22.42 22.50 22.56 23.00 23.20
 | 23.30 23.39 23.42 23.50 23.56 23.59 24.20'''
def t(x): h, m = x.split('.'); return int(h) * 3600 + int(m) * 60
def rows(block, cols):
    for line in block.strip('\n').split('\n'):
        sign, ts = line.split('|'); sign = sign.strip(); ts = ts.split()
        yield sign, {c: t(v) for c, v in zip(cols, ts) if v != '-'}
trips = []
for d_, (block, cols) in enumerate(((SOUTH, 'PGMODSC'), (NORTH, 'CSDOMGP'))):
    for n, (sign, tp) in enumerate(rows(block, cols)):
        days = 'W_1111100' if 'XX' in sign else 'W_1111110' if 'X' in sign else 'W_1111111'
        given = {IDX[c]: v for c, v in tp.items()}
        if 'L' in sign: given[1] = given[IDX['G']] - 600                                   # leaves East Portland 10 minutes earlier
        if 'E' in sign:                                                                     # East Portland only (northbound): arrival by distance from Golf Jct.
            g = IDX['G']; given[1] = given[g] + round((stations[g]['chain'] - stations[1]['chain']) / (stations[g]['chain'] - stations[0]['chain']) * 16) * 60
        lo, hi = min(given), max(given)
        skip_to = {'*': IDX['O'], '+': 13, '#': 14}.get(sign[-1] if sign else '', None)     # limited: no stops north of Oak Grove / Island / Lakewood
        seq = list(range(lo, hi + 1))
        if d_ == 1: seq = seq[::-1]
        pts = sorted(given.items())
        stops = []
        for i in seq:
            if i in given: stops.append([i, given[i], given[i], 1]); continue
            if skip_to is not None and d_ == 0 and i < skip_to and not stations[i]['principal']: continue
            a = max(p for p in pts if p[0] < i); b = min(p for p in pts if p[0] > i)
            f = (stations[i]['chain'] - stations[a[0]]['chain']) / (stations[b[0]]['chain'] - stations[a[0]]['chain'])
            v = round((a[1] + f * (b[1] - a[1])) / 60) * 60
            stops.append([i, v, v, 0])
        first = stops[0][1]; h, m = divmod(first // 60, 60)
        what = {'O': 'Oak Grove local', 'M': 'Milwaukie local'}.get(sign[:1], 'Oregon City train')
        trips.append(dict(id=f"PTC-{'SN'[d_]}-{n:02d}", num='Car', name='Portland Traction', svc=days, dir=d_, stops=stops,
                          note=(f"Portland Traction Co. {what}, leaves {stations[stops[0][0]]['name']} {(h - 1) % 12 + 1}.{m:02d} {'a.m.' if h % 24 < 12 else 'p.m.'}"
                               f"{', daily except Sunday' if days == 'W_1111110' else ', daily except Saturday and Sunday' if days == 'W_1111100' else ''}"
                               f"{'; East Portland only' if 'E' in sign else ''}{'; no stops north of Oak Grove except to pick up' if sign.endswith('*') else ''}"
                               f"{'; no stops north of Island except to pick up' if sign.endswith('+') else ''}{'; limited to Lakewood' if sign.endswith('#') else ''}. "
                               "Time Table No. 2, February 1, 1948 (Pacific Standard Time); stations between the timing points timed by distance (est.).").replace('.. ', '. ')))
SRC = 'Portland Traction Co., Oregon City Division: Time Table No. 2, effective February 1, 1948 (Brendan); track from the Portland Railway, Light & Power Co. KMZ (Brendan)'
NEW = [dict(key='ptc_oc', kind='Y', label='Portland – Oregon City (Portland Traction)', mainline=True, owner='ptc', src=SRC, route=route, stations=stations,
            dirLabels=['to Oregon City', 'to Portland'], segments=[], trips=trips)]
print(f"ptc_oc: {TOT / 1609.34:.2f} mi traced (13.94 printed), Golf Junction at {GOLF / 1609.34:.2f} (5.02), {len(trips)} trips")
vd = json.load(open(os.path.join(HERE, 'viz_data.json')))
vd['lines'] = [x for x in vd['lines'] if x['key'] != 'ptc_oc'] + NEW
open(os.path.join(HERE, 'viz_data.json'), 'w').write(json.dumps(vd, separators=(',', ':')))

def fmt(x): return f'{x // 3600:02d}:{x % 3600 // 60:02d}:{x % 60:02d}'
def app(name, rows_):
    with open(os.path.join(GT, name), 'a', newline='') as fh: csv.writer(fh).writerows(rows_)
def have(name, col=0): return set(r[col] for r in csv.reader(open(os.path.join(GT, name))))
cal = have('calendar.txt')
for d in sorted({tr['svc'] for tr in trips} - cal): app('calendar.txt', [[d, *d[2:], '19490616', '19491231']])
if 'PTC' not in have('agency.txt'): app('agency.txt', [['PTC', 'Portland Traction Company', 'https://en.wikipedia.org/wiki/Portland_Traction_Company', 'America/Vancouver', 'en', '']])
seen = have('stops.txt')
app('stops.txt', [[s['gid'], s['name'], f"{s['lat']:.6f}", f"{s['lon']:.6f}", s['note']] for s in stations if s['gid'] not in seen])
app('routes.txt', [['PTC_OC', 'PTC', 'Oregon City', 'Portland – Oregon City (Portland Traction)', 0, '2F6F8F', 'FFFFFF', SRC + '. Times on the Pacific clock.']])
app('shapes.txt', [['PTC_OC_S', f'{p[1]:.6f}', f'{p[0]:.6f}', k, f'{p[2]:.1f}'] for k, p in enumerate(route)])
app('shapes.txt', [['PTC_OC_N', f'{p[1]:.6f}', f'{p[0]:.6f}', k, f'{TOT - p[2]:.1f}'] for k, p in enumerate(route[::-1])])
for tr in trips:
    app('trips.txt', [['PTC_OC', tr['svc'], tr['id'], stations[tr['stops'][-1][0]]['name'], 'Portland Traction', tr['dir'], 'PTC_OC_' + 'SN'[tr['dir']]]])
    app('stop_times.txt', [[tr['id'], fmt(a), fmt(b), stations[i]['gid'], k, f"{(stations[i]['chain'] if tr['dir'] == 0 else TOT - stations[i]['chain']):.1f}", tp]
                           for k, (i, a, b, tp) in enumerate(tr['stops'], 1)])
