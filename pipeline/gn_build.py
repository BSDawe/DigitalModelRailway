"""Great Northern, Table 90 (summer 1947): Vancouver - New Westminster - White Rock - Blaine - Bellingham - Everett - Seattle.
Track: Brendan's GN KML to Bellingham (gn_geometry.json), then his Washington set (traces/gn_washington.kml) to King Street Station.
Run after marpole_build.py: adds a 'gn' line to viz_data.json and appends to the GTFS feed."""
import csv, json, os, re, zipfile
from pyproj import Transformer
from shapely.geometry import LineString
from shapely.ops import substring
HERE = os.path.dirname(os.path.abspath(__file__)); GT = os.path.join(HERE, 'gtfs')
fwd = Transformer.from_crs(4326, 26910, always_xy=True).transform
inv = Transformer.from_crs(26910, 4326, always_xy=True).transform
MI = 1609.344

R0 = LineString([fwd(*p) for p in json.load(open(os.path.join(HERE, 'gn_geometry.json')))['route']])        # Vancouver to the end of the first trace, in Bellingham
# south of Bellingham: Brendan's Great Northern set for Washington (traces/gn_washington.kml), four pieces end to end, each drawn the other way round
import xml.etree.ElementTree as ET
from shapely.geometry import Point
_NS = '{http://www.opengis.net/kml/2.2}'; _K = {}
for _pm in ET.parse(os.path.join(HERE, 'traces', 'gn_washington.kml')).iter(_NS + 'Placemark'):
    _c = _pm.find('.//' + _NS + 'coordinates')
    if _c is not None: _K.setdefault(_pm.find(_NS + 'name').text, [fwd(*map(float, t.split(',')[:2])) for t in _c.text.split()])
KING_ST = fwd(-122.3301, 47.5984)                                                  # King Street Station, Seattle
_se = LineString(_K['Seattle WA to Everett WA']); _eb = _K['Everett WA to Burlington WA']
_se = substring(_se, _se.project(Point(KING_ST)), _se.project(Point(_eb[0])))     # King Street to where the Burlington line leaves it at Everett
pts = list(R0.coords)
for piece in (_K['Belleville WA to Fairhaven WA'][::-1], _K['Burlington WA to Belleville WA'][::-1], _eb[::-1], list(_se.coords)[::-1]):
    print(f'  join {((pts[-1][0]-piece[0][0])**2 + (pts[-1][1]-piece[0][1])**2) ** .5:.0f} m'); pts += piece
R = LineString([p for k, p in enumerate(pts) if k == 0 or pts[k - 1] != p])
print(f'GN track: Vancouver to the end of the first trace {R0.length/MI:.2f} mi; to King Street Station {R.length/MI:.2f} mi (printed 154)')

# Vancouver to Bellingham: timetable mileages match the traced track to within ~0.2 mi, so stations sit at their printed mileage.
# Bellingham to Seattle: printed mileage (whole miles) scaled so that Seattle, 154, falls at King Street Station.
STATIONS = [('Vancouver', 0.0, True), ('New Westminster', 13.0, True), ('Colebrook', 24.0, False),
            ('Crescent', 28.0, False), ('Ocean Park', 29.0, False), ('White Rock', 33.0, True), ('Blaine', 36.0, True),
            ('Custer', 43.0, False), ('Ferndale', 49.0, False), ('Bellingham', 58.0, True), ('South Bellingham', 61.0, False), ('Samish', 71.0, False),
            ('Bow', 75.0, False), ('Burlington', 82.0, True), ('Mount Vernon', 86.0, True), ('Fir', 91.0, False), ('Stanwood', 98.0, False),
            ('Silvana', 104.0, False), ('English', 108.0, False), ('Marysville', 115.0, False), ('Everett', 122.0, True), ('Mukilteo', 126.0, False),
            ('Meadowdale', 133.0, False), ('Edmonds', 137.0, False), ('Richmond Beach', 140.0, False), ('Ballard', 148.0, False), ('Interbay', 150.0, False),
            ('Seattle', 154.0, True)]
def chain_of(mile): return mile * MI if mile <= 58 else 58 * MI + (mile - 58) / (154 - 58) * (R.length - 58 * MI)
BRIDGE = (13.17 * MI, 13.61 * MI)                   # Fraser River bridge, shared with BCER: federal -> CN

def parse(t):
    m = re.match(r'(f?)(\d+)\.(\d+)([ap])', t)
    h, mn = int(m.group(2)), int(m.group(3))
    if m.group(4) == 'p' and h != 12: h += 12
    if m.group(4) == 'a' and h == 12: h = 0
    return h * 3600 + mn * 60, m.group(1) == 'f'

rows = list(csv.DictReader(l for l in open(os.path.join(HERE, 'gn_table90.csv')) if not l.startswith('#')))
names = [s[0] for s in STATIONS]
trips = []
for r in rows:
    d = 0 if r['direction'] == 'south' else 1
    seq = names if d == 0 else names[::-1]
    stops = []
    for n in seq:
        if r.get(n):
            t, flag = parse(r[n])
            stops.append([names.index(n), t, t, 1])
    assert all(x[1] < y[1] for x, y in zip(stops, stops[1:])), r['train']
    trips.append(dict(id=r['train'], name=r['name'], svc='GN_DAILY', dir=d, stops=stops))
    print(r['train'], r['name'], len(stops), 'stops', [(names[s[0]], s[1] // 3600, s[1] % 3600 // 60) for s in (stops[0], stops[-1])])

# ---------------- viz
vd = json.load(open(os.path.join(HERE, 'viz_data.json')))
route = []; acc = 0; prev = None
for xy in R.simplify(1.0).coords:
    if prev: acc += ((xy[0]-prev[0])**2 + (xy[1]-prev[1])**2) ** .5
    prev = xy; lon, lat = inv(*xy); route.append([round(lon, 6), round(lat, 6), round(acc, 1)])
sc = acc / R.length
st = []
for n, mile, principal in STATIONS:
    c = min(chain_of(mile), R.length)
    lon, lat = inv(*R.interpolate(c).coords[0])
    if mile > 58: print(f'  {n:16s} mile {mile:5.0f}  {lat:.4f}, {lon:.4f}')
    st.append(dict(name=n, chain=round(c * sc, 1), lon=round(lon, 6), lat=round(lat, 6), mile=mile, principal=principal,
                   note='Great Northern station', kml='', gid='GN_' + n.upper().replace(' ', '_')))
gn = dict(key='gn', kind='g', label='Great Northern', mainline=True, owner='gn', route=route, stations=st, dirLabels=['to Bellingham, Everett and Seattle', 'to Vancouver'],
          segments=[dict(owner='cn', a=round(BRIDGE[0] * sc, 1), b=round(BRIDGE[1] * sc, 1), note='Fraser River bridge (federal)')],
          trips=[dict(id=t['id'], svc=t['svc'], dir=t['dir'], stops=t['stops'], name=t['name']) for t in trips])
vd['lines'] = [L for L in vd.get('lines', []) if L['key'] != 'gn'] + [gn]
open(os.path.join(HERE, 'viz_data.json'), 'w').write(json.dumps(vd, separators=(',', ':')))

# ---------------- GTFS
def fmt(x): return f'{x // 3600:02d}:{x % 3600 // 60:02d}:{x % 60:02d}'
def app(name, rows):
    with open(os.path.join(GT, name), 'a', newline='') as f: csv.writer(f).writerows(rows)
app('agency.txt', [['GN', 'Great Northern Railway', 'https://en.wikipedia.org/wiki/Great_Northern_Railway_(U.S.)', 'America/Vancouver', 'en', '']])
app('routes.txt', [['GNR', 'GN', 'GN', 'Vancouver – Bellingham – Everett – Seattle', 2, 'D98A1C', 'FFFFFF', 'Great Northern Table 90, summer 1947.']])
app('calendar.txt', [['GN_DAILY', 1, 1, 1, 1, 1, 1, 1, '19490616', '19491231']])
app('stops.txt', [[s['gid'], s['name'] + ' (GN)', f"{s['lat']:.6f}", f"{s['lon']:.6f}", 'Great Northern'] for s in st])
shp = []
for shape_id, coords in (('GN_S', list(R.coords)), ('GN_N', list(R.coords)[::-1])):
    a, p = 0.0, None
    for k, xy in enumerate(coords):
        if p: a += ((xy[0]-p[0])**2 + (xy[1]-p[1])**2) ** .5
        p = xy; lon, lat = inv(*xy); shp.append([shape_id, f'{lat:.6f}', f'{lon:.6f}', k, f'{a:.1f}'])
app('shapes.txt', shp)
app('trips.txt', [['GNR', 'GN_DAILY', 'GN' + t['id'], 'Seattle' if t['dir'] == 0 else 'Vancouver', f"{t['id']} {t['name']}".strip(),
                   t['dir'], 'GN_S' if t['dir'] == 0 else 'GN_N'] for t in trips])
rows = []
for t in trips:
    for k, (i, a, b, tp) in enumerate(t['stops'], 1):
        c = chain_of(STATIONS[i][1]); dist = c if t['dir'] == 0 else R.length - c
        rows.append(['GN' + t['id'], fmt(a), fmt(b), st[i]['gid'], k, f'{dist:.1f}', 1])
app('stop_times.txt', rows)
print('GN trips', len(trips))
