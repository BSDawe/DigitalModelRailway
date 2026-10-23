"""Central Park Line (Vancouver – New Westminster local) from the 1949 timetable's frequency notes.

Run after build_gtfs.py: appends to gtfs/ and re-zips, and adds a compact `cp` block to viz_data.json.

Station list and timepoints from the Central Park Line timetable corrected to March 16, 1942
(45 minutes end to end); departures from the 1949 Fraser Valley timetable.
  * flag stops between printed timepoints are timed by distance
  * rush-hour extras ("service augmented by frequent trains in rush hours") are not modelled
"""
import csv, json, os, re, zipfile
from xml.etree import ElementTree as ET
from pyproj import Transformer
from shapely.geometry import LineString, Point

HERE = os.path.dirname(os.path.abspath(__file__))
GT = os.path.join(HERE, 'gtfs')
fwd = Transformer.from_crs(4326, 26910, always_xy=True).transform
MI = 1609.344
RUN_MIN = 45  # 1942 timetable
STREET_MPH = 13
DWELL = 15

geo = json.load(open(os.path.join(HERE, 'geometry.json')))
model = json.load(open(os.path.join(HERE, 'model.json')))
route = LineString([fwd(*p) for p in geo['route']])
A_END = geo['pieces_len_m']['A']
van = [s for s in model['stations'] if s['tt_name'] == 'VANCOUVER'][0]
nw = [s for s in model['stations'] if s['tt_name'] == 'New Westminster'][0]

# ---------------------------------------------------------------- stations on the route
NS = {'k': 'http://www.opengis.net/kml/2.2'}
K = '{http://www.opengis.net/kml/2.2}'
tree = ET.parse(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'British_Columbia_Electric_Railway_Company.kml'))
par = {c: p for p in tree.iter() for c in p}


def fpath(e):
    o = []
    while e in par:
        e = par[e]
        if e.tag == K + 'Folder':
            o.append(e.find('k:name', NS).text)
    return '/'.join(o[::-1])


def tidy(n):
    n = re.sub(r'\s+station$', '', n)
    return n[0].upper() + n[1:] if n else n


# 1942 Central Park Line timetable (corrected to March 16, 1942): station list, read down.
LIST_1942 = ['Cedar Cottage', 'Lakeview', 'Gladstone', 'Nanaimo Road', 'Beaconsfield', "Earl's Road",
             'Collingwood West', 'Collingwood East', 'Park Avenue', 'Central Park', 'Patterson', 'McKay',
             'West Burnaby', 'Dow Road', 'Jubilee', 'Royal Oak', 'Highland Park', 'Fraser Arm', 'Prenter',
             'McGregor', 'Leeside', 'Connaught Hill', 'Elsona', 'Mead']
KML_OF = {'Nanaimo Road': 'Nanaimo station', "Earl's Road": 'Earls Road station', 'Dow Road': 'Dow station',
          'McGregor': 'MacGregor station', 'Mead': 'Meads station'}
# minutes after departure, from the card (read down from a :10 departure; read up from an on-the-hour departure)
TP_EB = {'VANCOUVER': 0, 'Cedar Cottage': 15, 'Beaconsfield': 18, 'Collingwood East': 22, 'Central Park': 24,
         'Jubilee': 29, 'Fraser Arm': 34, 'Mead': 38, 'NEW WESTMINSTER': 45}
TP_WB = {'NEW WESTMINSTER': 0, 'Mead': 7, 'Fraser Arm': 11, 'Jubilee': 15, 'Central Park': 19,
         'Collingwood East': 22, 'Beaconsfield': 26, 'Cedar Cottage': 30, 'VANCOUVER': 45}

kml = {}
for p in tree.iter(K + 'Placemark'):
    if fpath(p).endswith('First District/Stations'):
        ll = tuple(map(float, p.find('.//k:coordinates', NS).text.split(',')[:2]))
        kml[p.find('k:name', NS).text] = ll

cp = []
for name in LIST_1942:
    kn = KML_OF.get(name, name + ' station')
    if kn in kml:
        ll = kml[kn]
        cp.append(dict(name=name, lonlat=ll, chain=route.project(Point(fwd(*ll))), note=''))
    else:
        cp.append(dict(name=name, lonlat=None, chain=None, note='not plotted in KML; placed midway between neighbours'))
for i, s in enumerate(cp):  # Lakeview: midway between its neighbours
    if s['chain'] is None:
        s['chain'] = (cp[i - 1]['chain'] + cp[i + 1]['chain']) / 2
        from pyproj import Transformer as _T
        x, y = route.interpolate(s['chain']).coords[0]
        s['lonlat'] = _T.from_crs(26910, 4326, always_xy=True).transform(x, y)
assert all(a['chain'] < b['chain'] for a, b in zip(cp, cp[1:])), 'station order'
for i, s in enumerate(cp, 1):
    s['stop_id'] = f'C{i:02d}'
    s['mile'] = round(s['chain'] / MI, 2)
dropped = [n for n in kml if route.distance(Point(fwd(*kml[n]))) < 30
           and n not in {KML_OF.get(x, x + ' station') for x in LIST_1942}]
print('KML stations on route but not on the 1942 card:', dropped)

# ---------------------------------------------------------------- running-time pattern
# Printed stations are timepoints. Flag stops between them get times spaced by distance (no dwell).
seq = [dict(stop_id=van['stop_id'], name='VANCOUVER', chain=van['chain_m'])] + \
      [dict(stop_id=s['stop_id'], name=s['name'], chain=s['chain']) for s in cp] + \
      [dict(stop_id=nw['stop_id'], name='NEW WESTMINSTER', chain=nw['chain_m'])]


def pattern(stops, tp):
    out = []
    known = [k for k, s in enumerate(stops) if s['name'] in tp]
    for ka, kb in zip(known, known[1:]):
        ta, tb = tp[stops[ka]['name']] * 60, tp[stops[kb]['name']] * 60
        ca, cb = stops[ka]['chain'], stops[kb]['chain']
        for k in range(ka, kb):
            f = (stops[k]['chain'] - ca) / (cb - ca)
            out.append([stops[k]['stop_id'], round(ta + f * (tb - ta)), round(ta + f * (tb - ta)), 1 if k == ka else 0])
    last = stops[known[-1]]
    out.append([last['stop_id'], tp[last['name']] * 60, tp[last['name']] * 60, 1])
    return out


PAT = {0: pattern(seq, TP_EB), 1: pattern(seq[::-1], TP_WB)}
for d in (0, 1):
    pts = [(seq if d == 0 else seq[::-1])[k] for k in range(len(seq))]
    tps = [r for r in PAT[d] if r[3]]
    ch = {s['stop_id']: s['chain'] for s in seq}
    print('dir', d, ' '.join(f"{abs(ch[b[0]]-ch[a[0]])/MI/((b[1]-a[2])/3600):.0f}mph" for a, b in zip(tps, tps[1:])))
RUN_MIN = 45

# ---------------------------------------------------------------- departures (from the timetable panel)
def t(s):
    """'8.45a' -> seconds; 'p' pm; 'n' = after-midnight late car (service day continues past 24:00)"""
    h, m = map(int, s[:-1].split('.'))
    suf = s[-1]
    if suf == 'p' and h != 12:
        h += 12
    if suf == 'a' and h == 12:
        h = 0
    if suf == 'n':
        h = (0 if h == 12 else h) + 24
    return h * 3600 + m * 60


def every(start, end, step_min):
    return list(range(t(start), t(end) + 1, step_min * 60))


def uniq(xs):
    return sorted(set(xs))


VAN_LATE = [t(x) for x in ('12.05n', '12.20n', '12.35n', '1.00n', '1.30n')]
NW_LATE = [t(x) for x in ('11.40p', '12.00n', '12.40n')]
DEPS = {
    'CP_WKDY': {
        0: uniq([t(x) for x in '5.00a 5.50a 6.30a 6.50a 7.05a 7.25a 7.40a 7.50a 8.05a 8.25a'.split()]
                + every('8.45a', '11.45p', 20) + VAN_LATE),
        1: uniq([t('5.00a'), t('5.40a')] + every('6.00a', '11.20p', 20) + NW_LATE),
    },
    'CP_SUN': {
        0: uniq([t('6.00a'), t('6.50a')] + every('7.50a', '11.50p', 20) + VAN_LATE),
        1: uniq([t('6.00a')] + every('7.00a', '11.20p', 20) + NW_LATE),
    },
    'CP_SAT': {
        0: uniq([t(x) for x in '5.00a 5.50a 6.30a 6.50a 7.05a 7.25a'.split()]
                + every('7.45a', '9.45a', 20) + every('10.00a', '8.45p', 15) + every('9.05p', '11.45p', 20) + VAN_LATE),
        1: uniq([t('5.00a'), t('5.40a')] + every('6.00a', '9.00a', 20) + every('9.15a', '8.00p', 15)
                + every('8.20p', '11.20p', 20) + NW_LATE),
    },
}
for sv, d in DEPS.items():
    print(sv, 'from Vancouver', len(d[0]), 'from New Westminster', len(d[1]))


# ---------------------------------------------------------------- append to GTFS
def fmt(sec):
    return f'{sec // 3600:02d}:{sec % 3600 // 60:02d}:{sec % 60:02d}'


def append(name, rows):
    with open(os.path.join(GT, name), 'a', newline='') as f:
        csv.writer(f).writerows(rows)


append('routes.txt', [['CPL', 'BCER', 'Central Park', 'Vancouver – New Westminster (Central Park Line)', 2,
                       '6A4C93', 'FFFFFF', 'Local cars via Central Park. Running times from the March 16 1942 Central Park Line timetable; flag-stop times estimated.']])
append('calendar.txt', [['CP_WKDY', 1, 1, 1, 1, 1, 0, 0, '19490616', '19491231'],
                        ['CP_SAT', 0, 0, 0, 0, 0, 1, 0, '19490616', '19491231'],
                        ['CP_SUN', 0, 0, 0, 0, 0, 0, 1, '19490616', '19491231']])
append('stops.txt', [[s['stop_id'], s['name'], f"{s['lonlat'][1]:.6f}", f"{s['lonlat'][0]:.6f}",
                      f"Central Park Line, {s['mile']} mi from Carrall St"] for s in cp])
L = model['route_len_m']
chain_of = {s['stop_id']: s['chain'] for s in cp}
chain_of[van['stop_id']] = van['chain_m']
chain_of[nw['stop_id']] = nw['chain_m']
trip_rows, st_rows = [], []
for sv, d in DEPS.items():
    for direction, deps in d.items():
        for dep in deps:
            tid = f"{sv}-{'EB' if direction == 0 else 'WB'}-{fmt(dep)[:5].replace(':', '')}"
            head = 'New Westminster' if direction == 0 else 'Vancouver'
            trip_rows.append(['CPL', sv, tid, head, 'Central Park car', direction, 'EB' if direction == 0 else 'WB'])
            pat = PAT[direction]
            for k, (sid, a, b, tp) in enumerate(pat, 1):
                dist = chain_of[sid] if direction == 0 else L - chain_of[sid]
                st_rows.append([tid, fmt(dep + a), fmt(dep + b), sid, k, f'{dist:.1f}', tp])
append('trips.txt', trip_rows)
append('stop_times.txt', st_rows)
with zipfile.ZipFile(os.path.join(HERE, 'bcer_fraser_valley_1949_gtfs.zip'), 'w', zipfile.ZIP_DEFLATED) as z:
    for fn in sorted(os.listdir(GT)):
        z.write(os.path.join(GT, fn), fn)
print('GTFS: +', len(trip_rows), 'trips, +', len(st_rows), 'stop_times')

# ---------------------------------------------------------------- viz data
vd = json.load(open(os.path.join(HERE, 'viz_data.json')))
vd['stations'] = [s for s in vd['stations'] if not s['id'].startswith('C')]
base_n = len(vd['stations'])
for s in cp:
    vd['stations'].append(dict(id=s['stop_id'], name=s['name'], mile=round(s['chain'] / MI, 1),
                               chain=round(s['chain'], 1), lon=round(s['lonlat'][0], 6),
                               lat=round(s['lonlat'][1], 6), principal=False, line='cp',
                               note='Central Park Line station' + ('; ' + s['note'] if s['note'] else ''), kml=''))
idx = {s['id']: i for i, s in enumerate(vd['stations'])}
vd['cp'] = dict(pattern={str(k): [[idx[sid], a, b, tp] for sid, a, b, tp in v] for k, v in PAT.items()},
                deps={sv: {str(k): v for k, v in d.items()} for sv, d in DEPS.items()},
                runMin=RUN_MIN)
open(os.path.join(HERE, 'viz_data.json'), 'w').write(json.dumps(vd, separators=(',', ':')))
print('viz stations', len(vd['stations']))
