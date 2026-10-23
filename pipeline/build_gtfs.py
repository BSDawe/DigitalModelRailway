"""Build a GTFS feed for the B.C. Electric Fraser Valley line, June 16 1949,
from the transcribed timetable + KML geometry, and run plausibility checks."""
import csv, json, math, os, re, zipfile
from pyproj import Transformer
from shapely.geometry import LineString, Point
from xml.etree import ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'gtfs')
os.makedirs(OUT, exist_ok=True)
fwd = Transformer.from_crs(4326, 26910, always_xy=True).transform
inv = Transformer.from_crs(26910, 4326, always_xy=True).transform
MI = 1609.344

geo = json.load(open(os.path.join(HERE, 'geometry.json')))
route = LineString([fwd(*p) for p in geo['route']])

# ------------------------------------------------------------------ stations
# timetable name -> KML placemark name (None = not plotted in KML)
KML_NAME = {
    'VANCOUVER': 'CARRALL', 'New Westminster': 'New Westminster station', 'Shops': 'Shops/Liverpool station',
    "Hall's Prairie": 'Halls Prarie station', 'Langley Prairie': 'Langley Prarie station',
    'Burkart Road': 'Burkhart Road station', 'County Line': 'Country line station',
    'Mt. Lehman': 'Mount Lehman station', 'St. Nicholas': 'St.Nicholas station',
    'Delair Road': 'Delair station', 'Stewart Rd.': 'Stewart Road station',
    'Knight Road': 'Knight road station', 'CHILLIWACK': 'Chilliwack station', 'Kidd': None,
}
WB_ALIAS = {'Halls Prairie': "Hall's Prairie", 'Burkhart Road': 'Burkart Road'}
kml_st = {s['name']: s for s in geo['stations']}


def read(fn):
    return list(csv.DictReader(open(os.path.join(HERE, fn))))


eb = read('transcription_eastbound.csv')
wb = read('transcription_westbound.csv')
for r in wb:
    r['station'] = WB_ALIAS.get(r['station'], r['station'])

stations = []  # ordered east from Vancouver
for r in eb:
    name = r['station']
    kname = KML_NAME.get(name, f'{name} station')
    s = dict(name=name.title() if name.isupper() else name, tt_name=name,
             mile_eb=float(r['mileage']) if r['mileage'] else None)
    if kname == 'CARRALL':
        s['lonlat'] = geo['carrall']
        s['kml_note'] = 'Carrall Street station (KML Vancouver architecture layer)'
    elif kname and kname in kml_st:
        s['lonlat'] = kml_st[kname]['lonlat']
        m = re.search(r'Mile\s*(\d+(?:\.\d+)?)', kml_st[kname]['desc'])
        s['kml_mile'] = float(m.group(1)) if m else None
    else:
        s['lonlat'] = None
    stations.append(s)

# chainage along route for plotted stations
for s in stations:
    if s['lonlat']:
        p = Point(fwd(*s['lonlat']))
        s['chain_m'] = route.project(p)
        s['offset_m'] = route.distance(p)
# unplotted (Kidd): interpolate by timetable mileage between neighbours
for i, s in enumerate(stations):
    if s['lonlat'] is None:
        a, b = stations[i - 1], stations[i + 1]
        f = (s['mile_eb'] - a['mile_eb']) / (b['mile_eb'] - a['mile_eb'])
        s['chain_m'] = a['chain_m'] + f * (b['chain_m'] - a['chain_m'])
        s['offset_m'] = 0
        s['lonlat'] = inv(*route.interpolate(s['chain_m']).coords[0])
        s['kml_note'] = 'not plotted in KML; placed by timetable mileage'
# Arnold has no timetable mileage; use KML's
for s in stations:
    if s['mile_eb'] is None:
        s['mile_eb'] = s.get('kml_mile')
        s['mile_note'] = 'mileage blank in timetable; KML gives 60.8'

for i, s in enumerate(stations):
    s['stop_id'] = f'S{i:02d}'
by_name = {s['tt_name']: s for s in stations}


# ------------------------------------------------------------------ times
def to_secs(txt, pm):
    h, m = map(int, txt.split('.'))
    if pm and h != 12:
        h += 12
    return h * 3600 + m * 60


def fmt(sec):
    return f'{sec // 3600:02d}:{sec % 3600 // 60:02d}:{sec % 60:02d}'


# column -> (trip_id, direction_id, service, pm?)
EB_COLS = {'fri_only': ('FRI-EB', 0, 'FRI', False, 'Friday Market Special'),
           'train_2': ('2', 0, 'DAILY', False, None), 'train_4': ('4', 0, 'DAILY', True, None),
           'train_8': ('8', 0, 'DAILY', True, None)}
WB_COLS = {'fri_only': ('FRI-WB', 1, 'FRI', False, 'Friday Market Special'),
           'train_3': ('3', 1, 'DAILY', False, None), 'train_5': ('5', 1, 'DAILY', True, None),
           'train_7': ('7', 1, 'DAILY', True, None)}

trips = []  # dict(trip_id, dir, service, headsign, stops=[(stop, arr, dep, timepoint)])
for rows, cols in ((eb, EB_COLS), (wb, WB_COLS)):
    for col, (tid, d, svc, pm, label) in cols.items():
        st = [(by_name[r['station']], to_secs(r[col], pm)) for r in rows if r[col]]
        trips.append(dict(trip_id=tid, dir=d, service=svc, label=label,
                          headsign=st[-1][0]['name'],
                          stops=[(s, t, t, 1) for s, t in st]))

# Saturday late special: timepoints only; intermediate stops interpolated by distance
def special(tid, d, pts):
    """pts: list of (tt_name, arr, dep) timepoints in running order."""
    names = [s['tt_name'] for s in stations]
    i0, i1 = names.index(pts[0][0]), names.index(pts[-1][0])
    seq = stations[i0:i1 + 1] if i0 < i1 else stations[i1:i0 + 1][::-1]
    tp = {p[0]: p for p in pts}
    out = []
    for k, s in enumerate(seq):
        if s['tt_name'] in tp:
            _, a, b = tp[s['tt_name']]
            out.append([s, a, b, 1])
        else:
            out.append([s, None, None, 0])
    # fill gaps linearly by chainage
    known = [k for k, o in enumerate(out) if o[3] == 1]
    for ka, kb in zip(known, known[1:]):
        ca, cb = out[ka][0]['chain_m'], out[kb][0]['chain_m']
        ta, tb = out[ka][2], out[kb][1]
        for k in range(ka + 1, kb):
            f = (out[k][0]['chain_m'] - ca) / (cb - ca)
            t = round(ta + f * (tb - ta))
            out[k][1] = out[k][2] = t
    # Vancouver->NW: no stops
    out = [o for o in out if o[3] == 1 or not (o[0]['mile_eb'] < 12.5)]
    return dict(trip_id=tid, dir=d, service='SAT', label='Saturday Special for Mount Lehman',
                headsign=seq[-1]['name'], stops=[tuple(o) for o in out])


H = 3600
trips.append(special('SAT-EB', 0, [('VANCOUVER', 23 * H + 35 * 60, 23 * H + 35 * 60),
                                   ('New Westminster', 24 * H + 25 * 60, 24 * H + 25 * 60),
                                   ('Mt. Lehman', 25 * H + 45 * 60, 25 * H + 45 * 60)]))
trips.append(special('SAT-WB', 1, [('Mt. Lehman', 25 * H + 50 * 60, 25 * H + 50 * 60),
                                   ('New Westminster', 26 * H + 50 * 60, 26 * H + 50 * 60)]))


# ------------------------------------------------------------------ write GTFS
def write(name, header, rows):
    with open(os.path.join(OUT, name), 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)


write('agency.txt', ['agency_id', 'agency_name', 'agency_url', 'agency_timezone', 'agency_lang', 'agency_phone'],
      [['BCER', 'British Columbia Electric Railway', 'https://en.wikipedia.org/wiki/British_Columbia_Electric_Railway',
        'America/Vancouver', 'en', 'MA. 2421']])
write('feed_info.txt', ['feed_publisher_name', 'feed_publisher_url', 'feed_lang', 'feed_start_date', 'feed_end_date',
                        'feed_version'],
      [['Historical reconstruction from B.C. Electric public timetable corrected to June 16 1949',
        'https://en.wikipedia.org/wiki/British_Columbia_Electric_Railway', 'en', '19490616', '19491231',
        '1949-06-16-pilot']])
write('routes.txt', ['route_id', 'agency_id', 'route_short_name', 'route_long_name', 'route_type', 'route_color',
                     'route_text_color', 'route_desc'],
      [['FVL', 'BCER', 'Fraser Valley', 'Vancouver – Chilliwack', 2, 'B5121B', 'FFFFFF',
        'Chilliwack interurban via Central Park and New Westminster. No stops between Vancouver and New Westminster.']])
write('calendar.txt', ['service_id', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday',
                       'start_date', 'end_date'],
      [['DAILY', 1, 1, 1, 1, 1, 1, 1, '19490616', '19491231'],
       ['FRI', 0, 0, 0, 0, 1, 0, 0, '19490616', '19491231'],
       ['SAT', 0, 0, 0, 0, 0, 1, 0, '19490616', '19491231']])
write('stops.txt', ['stop_id', 'stop_name', 'stop_lat', 'stop_lon', 'stop_desc'],
      [[s['stop_id'], s['name'], f"{s['lonlat'][1]:.6f}", f"{s['lonlat'][0]:.6f}",
        f"Mile {s['mile_eb']}" + (f"; {s['kml_note']}" if s.get('kml_note') else '')] for s in stations])

# shapes: EB = route, WB = reversed
shape_rows = []
L = route.length
for sid, coords in (('EB', list(route.coords)), ('WB', list(route.coords)[::-1])):
    acc, prev = 0.0, None
    for k, xy in enumerate(coords):
        if prev:
            acc += math.dist(prev, xy)
        prev = xy
        lon, lat = inv(*xy)
        shape_rows.append([sid, f'{lat:.6f}', f'{lon:.6f}', k, f'{acc:.1f}'])
write('shapes.txt', ['shape_id', 'shape_pt_lat', 'shape_pt_lon', 'shape_pt_sequence', 'shape_dist_traveled'],
      shape_rows)

write('trips.txt', ['route_id', 'service_id', 'trip_id', 'trip_headsign', 'trip_short_name', 'direction_id',
                    'shape_id'],
      [['FVL', t['service'], t['trip_id'], t['headsign'],
        t['label'] or f"Train {t['trip_id']}", t['dir'], 'EB' if t['dir'] == 0 else 'WB'] for t in trips])

st_rows = []
for t in trips:
    for seq, (s, a, d, tp) in enumerate(t['stops'], 1):
        dist = s['chain_m'] if t['dir'] == 0 else L - s['chain_m']
        st_rows.append([t['trip_id'], fmt(a), fmt(d), s['stop_id'], seq, f'{dist:.1f}', tp])
write('stop_times.txt', ['trip_id', 'arrival_time', 'departure_time', 'stop_id', 'stop_sequence',
                         'shape_dist_traveled', 'timepoint'], st_rows)

with zipfile.ZipFile(os.path.join(HERE, 'bcer_fraser_valley_1949_gtfs.zip'), 'w', zipfile.ZIP_DEFLATED) as z:
    for fn in sorted(os.listdir(OUT)):
        z.write(os.path.join(OUT, fn), fn)

json.dump(dict(stations=[{k: v for k, v in s.items()} for s in stations],
               trips=[dict(trip_id=t['trip_id'], dir=t['dir'], service=t['service'], label=t['label'],
                           stops=[(s['stop_id'], a, d, tp) for s, a, d, tp in t['stops']]) for t in trips],
               route_len_m=L),
          open(os.path.join(HERE, 'model.json'), 'w'))
print('trips', len(trips), 'stop_times', len(st_rows), 'stations', len(stations))
