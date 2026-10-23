"""CP Kettle Valley and Kootenay lines (Table 151, 1948): Odlum - Hope - Brookmere - Princeton - Penticton - Midway - Grand Forks -
Castlegar - Nelson. Run after cn_north_build.py; adds line 'kv' to viz_data.json and the GTFS feed. Stations sit at printed mileage,
pinned to Odlum, Brookmere, Princeton, Penticton, Midway, Castlegar and Nelson along the traced route (kv_geometry.py)."""
import csv, json, math, os, pickle, re, zipfile
import numpy as np
from shapely.geometry import Point, LineString
from shapely.ops import substring
from bc_bits import K
from nrwn_graph import fwd, inv, MI
HERE = os.path.dirname(os.path.abspath(__file__)); GT = os.path.join(HERE, 'gtfs')
RT0 = pickle.load(open(os.path.join(HERE, 'kv_route.pkl'), 'rb'))['KV']          # runs Odlum (0) -> Nelson
# Grand Forks City spur (Brendan's 'City Branch' and 'City Wye' traces): Nos. 11 and 12 run into the city and back while at City Jct, so the spur
# is part of the route. It is run through the wye: in by the west leg, out by the east leg (No. 12, eastbound) and the reverse for No. 11 -
# each train heads in by its own leg; the short back-up move to regain the main line is not shown.
CBR = LineString([fwd(*p) for p in K['City Branch']]); CW = [fwd(*p) for p in K['City Wye']]
if RT0.distance(Point(CW[0])) < RT0.distance(Point(CW[-1])): CW = CW[::-1]      # apex (on the branch) -> main line
GF_A, GF_B, apex = RT0.project(Point(CBR.coords[0])), RT0.project(Point(CW[-1])), CBR.project(Point(CW[0]))
L1 = CBR.length; L2 = L1 - apex + LineString(CW).length
GF_CITY, GF_BN = GF_A + L1, GF_A + L1 + L2                                          # chains of the city station and of the east wye switch
def _join(*parts):
    out = []
    for part in parts:
        for q in part:
            if not out or math.dist(q, out[-1]) > 0.3: out.append(q)
    return LineString(out)
RT = _join(substring(RT0, 0, GF_A).coords, CBR.coords, list(substring(CBR, apex, L1).coords)[::-1], CW, substring(RT0, GF_B, RT0.length).coords)
def newchain(c): return c if c <= GF_A else c + (GF_BN - GF_B)                    # chain on RT0 -> chain on RT
print(f'  Grand Forks City spur: {L1/MI:.2f} mi in by the west leg, {L2/MI:.2f} mi out by the east leg (printed 1.6); switches {(GF_B-GF_A)/MI:.2f} mi apart; '
      f'trace ends {RT0.distance(Point(CBR.coords[0])):.0f} / {RT0.distance(Point(CW[-1])):.0f} m off the main line')

rows = list(csv.DictReader(l for l in open(os.path.join(HERE, 'cp_1948_table151_kv.csv')) if not l.startswith('#')))
mi = {r['station']: float(r['mile']) for r in rows}                              # miles from Nelson
ANCH = {'Odlum': 0.0, 'Brodie': RT0.project(Point(fwd(-120.941, 49.814))), 'Brookmere': RT0.project(Point(fwd(-120.875, 49.815))), 'Princeton': RT0.project(Point(fwd(-120.51, 49.46))),
        'Penticton': RT0.project(Point(fwd(-119.59, 49.49))), 'Midway': RT0.project(Point(fwd(-118.775, 49.01))), 'City Jct': (GF_A + GF_B) / 2,
        'Castlegar': RT0.project(Point(fwd(*json.load(open(os.path.join(HERE, 'castlegar_wye.json')))['wye']))), 'Nelson': RT0.length}   # Castlegar station at the wye (Brendan)
am = [mi[n] for n in ANCH][::-1]; ac = list(ANCH.values())[::-1]                # increasing Nelson-mile order
def chain(m): return float(np.interp(m, am, ac))
for n, c in ANCH.items(): print(f'  anchor {n}: mile {mi[n]}, {c/MI:.1f} mi from Odlum')
hope = Point(fwd(-121.4415, 49.3800)); print(f'  Hope station point is {RT0.distance(hope):.0f} m off the route')

def times(txt):
    arr = dep = None
    for m in re.finditer(r'(ar|lv)?\s*[fg]?(\d+)\.(\d+)([ap])', txt):
        h, mn = int(m.group(2)), int(m.group(3))
        if m.group(4) == 'p' and h != 12: h += 12
        if m.group(4) == 'a' and h == 12: h = 0
        t = h * 3600 + mn * 60
        if m.group(1) == 'ar': arr = t
        elif m.group(1) == 'lv': dep = t
        else: arr = dep = t
    return (arr if arr is not None else dep), (dep if dep is not None else arr)
def monotonic(stops):
    base, prev = 0, -1
    for s in stops:
        for k in (1, 2):
            if s[k] + base < prev - 6 * 3600: base += 86400
            s[k] += base; prev = s[k]
    return stops

PRINCIPAL = {'Nelson', 'Castlegar', 'Grand Forks', 'Greenwood', 'Midway', 'Rock Creek', 'Beaverdell', 'Carmi', 'McCulloch', 'Penticton',
             'West Summerland', 'Princeton', 'Coalmont', 'Tulameen', 'Brookmere', 'Coquihalla', 'Hope', 'Odlum', 'South Slocan', 'Cascade'}
stations, idx = [], {}
for r in sorted(rows, key=lambda r: -float(r['mile'])):                         # Odlum first: chain increases away from Vancouver
    n = r['station']; idx[n] = len(stations)
    if n == 'City Jct':       # west switch, the city station at the end of the spur, and the east switch (the same station, called at twice)
        note = 'Canadian Pacific, junction for the Grand Forks City spur'
        stations += [dict(name=n, chain=GF_A, mile=mi[n], principal=False, gid='KV_CITY_JCT', note=note),
                     dict(name='Grand Forks City', chain=GF_CITY, mile=round(mi[n] + 1.6, 1), principal=True, gid='KV_GRAND_FORKS_CITY', slow=True,
                          note='Canadian Pacific, city station at the end of the spur from City Jct (1.6 miles); trains ran in and backed out'),
                     dict(name=n, chain=GF_BN, mile=mi[n], principal=False, gid='KV_CITY_JCT', note=note)]
        continue
    stations.append(dict(name=n, chain=newchain(chain(mi[n])), mile=mi[n], principal=n in PRINCIPAL,
                         gid='CP_ODLUM' if n == 'Odlum' else 'KV_' + re.sub(r'\W+', '_', n.upper()).strip('_'),
                         note='Canadian Pacific station' + (' (Kettle Valley junction with the main line)' if n == 'Odlum' else
                                                           ' (junction for Merritt and Spence\'s Bridge)' if n == 'Brookmere' else
                                                           ' (Slocan line)' if n == 'South Slocan' else ' (for Trail)' if n == 'Castlegar' else '')))
# dir 0 = away from Vancouver (Odlum -> Nelson, eastbound)
TRAINS = (('No11', '11', 'Kootenay Express', 'CP_DAILY', 1, 'Nelson to Vancouver by the Kettle Valley, through the Coquihalla. From Medicine Hat and Lethbridge by the Crowsnest.'),
          ('No12', '12', 'Kettle Valley Express', 'CP_DAILY', 0, 'Vancouver to Nelson by the Kettle Valley; on by the Crowsnest to Lethbridge and Medicine Hat.'),
          ('No45', '45', '', 'CP_DAILY', 1, 'Penticton to Vancouver overnight, through the Coquihalla.'),
          ('No46', '46', '', 'CP_DAILY', 0, 'Vancouver to Penticton overnight, through the Coquihalla.'),
          ('M807', 'M807', 'Mixed', 'CP_SUN1', 1, 'Mixed train, Brookmere to Odlum through the Coquihalla (Sundays). The timetable prints only Brookmere, Hope and Odlum.'),
          ('M808', 'M808', 'Mixed', 'CP_MON1', 0, 'Mixed train, Odlum to Brookmere through the Coquihalla (Mondays). The timetable prints only Odlum, Hope and Brookmere.'),
          ('No43', '43', '', 'CP_DAILY', 1, 'Nelson to Castlegar, on to Trail (Table 155).'),
          ('No44', '44', '', 'CP_DAILY', 0, 'Castlegar to Nelson; from Trail (Table 155).'),
          ('M841', 'M841', 'Mixed', 'CP_MON1', 1, 'Mixed train, Nelson to South Slocan, on to Slocan City (Table 158, not yet traced). Mondays.'),
          ('M842', 'M842', 'Mixed', 'CP_WED1', 0, 'Mixed train from Slocan City (Table 158, not yet traced); South Slocan to Nelson. Wednesdays.'))
trips = []
for col, num, name, svc, d, note in TRAINS:
    rs = sorted((r for r in rows if r[col]), key=lambda r: float(r['mile']), reverse=(d == 0))
    stops = [[idx[r['station']], *times(r[col]), 1] for r in rs]
    k = next((k for k, x in enumerate(stops) if x[0] == idx['City Jct']), None)
    if k is not None:         # Brendan's times: the printed table gives only the City Jct arrival and departure
        w, c, e = idx['City Jct'], idx['City Jct'] + 1, idx['City Jct'] + 2; hm = lambda h, m: h * 3600 + m * 60
        stops[k:k + 1] = {'12': [[w, hm(11, 58), hm(11, 58), 1], [c, hm(12, 8), hm(12, 8), 1], [e, hm(12, 18), hm(12, 18), 1]],
                          '11': [[e, hm(15, 31), hm(15, 31), 1], [c, hm(15, 40), hm(15, 50), 1], [w, hm(16, 0), hm(16, 0), 1]]}[num]
    trips.append(dict(id='KV-' + num, num=num, name=name, svc=svc, dir=d, stops=monotonic(stops), note=note))
bad = []
for t in trips:
    for (a, _, da, _), (b, tb, _, _) in zip(t['stops'], t['stops'][1:]):
        dist = abs(stations[b]['chain'] - stations[a]['chain']) / MI; mins = (tb - da) / 60
        if mins <= 0 or dist / (mins / 60) > 50: bad.append(f"{t['id']} {stations[a]['name']}->{stations[b]['name']} {dist:.1f}mi/{mins:.0f}min")
    f = lambda x: f'{x // 3600:02d}:{x % 3600 // 60:02d}'
    print(' ', t['id'], ' '.join(f"{stations[a]['name'][:9]} {f(b)}" for a, b, c, _ in t['stops'][:2]), '...', ' '.join(f"{stations[a]['name'][:9]} {f(b)}" for a, b, c, _ in t['stops'][-2:]))
print('  fast/odd runs:', bad or 'none')

# ---- viz
vd = json.load(open(os.path.join(HERE, 'viz_data.json')))
route = []; acc = 0; prev = None
for xy in RT.simplify(2.0).coords:
    if prev: acc += math.dist(xy, prev)
    prev = xy; lon, lat = inv(*xy); route.append([round(lon, 6), round(lat, 6), round(acc, 1)])
sc = acc / RT.length
st = []
for s in stations:
    lon, lat = inv(*RT.interpolate(s['chain']).coords[0])
    st.append(dict(name=s['name'], chain=round(s['chain'] * sc, 1), lon=round(lon, 6), lat=round(lat, 6), mile=s['mile'],
                   principal=s['principal'], note=s['note'], kml='', gid=s['gid'], **({'slow': True} if s.get('slow') else {})))
# the main line between the two wye switches at City Jct: the route goes round by the spur, so this piece is drawn as plain track
xr = []; xa = 0.0; xp = None
for xy in substring(RT0, GF_A, GF_B).coords:
    if xp: xa += math.dist(xy, xp)
    xp = xy; lon, lat = inv(*xy); xr.append([round(lon, 6), round(lat, 6), round(xa, 1)])
vd['lines'] = [x for x in vd['lines'] if x['key'] not in ('x_gf', 'gf')] + [dict(key='x_gf', kind='p', label='Canadian Pacific', mainline=True, owner='cp', route=xr,
                                                                                stations=[], dirLabels=['', ''], segments=[], trips=[])]
line = dict(key='kv', kind='p', label='Canadian Pacific', mainline=True, owner='cp', route=route, stations=st,
            dirLabels=['to Penticton and Nelson', 'to Hope and Vancouver'], segments=[], trips=trips)
vd['lines'] = [x for x in vd['lines'] if x['key'] != 'kv'] + [line]
open(os.path.join(HERE, 'viz_data.json'), 'w').write(json.dumps(vd, separators=(',', ':')))

# ---- GTFS
def fmt(x): return f'{x // 3600:02d}:{x % 3600 // 60:02d}:{x % 60:02d}'
def app(name, rows_):
    with open(os.path.join(GT, name), 'a', newline='') as fh: csv.writer(fh).writerows(rows_)
app('routes.txt', [['CPK', 'CP', 'CP Kettle Valley', 'Hope – Penticton – Midway – Castlegar – Nelson', 2, '7A1E2C', 'FFFFFF', 'CP Table 151, 1948. Track from a hand trace of the Kettle Valley line.']])
app('calendar.txt', [['CP_SUN1', 0, 0, 0, 0, 0, 0, 1, '19490616', '19491231'], ['CP_MON1', 1, 0, 0, 0, 0, 0, 0, '19490616', '19491231'],
                     ['CP_WED1', 0, 0, 1, 0, 0, 0, 0, '19490616', '19491231']])
seen = set(r[0] for r in csv.reader(open(os.path.join(GT, 'stops.txt'))))
app('stops.txt', list({s['gid']: [s['gid'], s['name'] + ' (CP)', f"{s['lat']:.6f}", f"{s['lon']:.6f}", s['note']] for s in st if s['gid'] not in seen}.values()))
shp = []
for sid, coords in (('KV_OUT', list(RT.coords)), ('KV_IN', list(RT.coords)[::-1])):
    a, p = 0.0, None
    for k, xy in enumerate(coords):
        if p: a += math.dist(p, xy)
        p = xy; lon, lat = inv(*xy); shp.append([sid, f'{lat:.6f}', f'{lon:.6f}', k, f'{a:.1f}'])
app('shapes.txt', shp)
app('trips.txt', [['CPK', t['svc'], t['id'], stations[t['stops'][-1][0]]['name'], f"{t['num']} {t['name']}".strip(), t['dir'],
                   'KV_OUT' if t['dir'] == 0 else 'KV_IN'] for t in trips])
app('stop_times.txt', [[t['id'], fmt(a), fmt(b), stations[i]['gid'], k, f"{(stations[i]['chain'] if t['dir'] == 0 else RT.length - stations[i]['chain']):.1f}", 1]
                       for t in trips for k, (i, a, b, tp) in enumerate(t['stops'], 1)])
with zipfile.ZipFile(os.path.join(HERE, 'bcer_fraser_valley_1949_gtfs.zip'), 'w', zipfile.ZIP_DEFLATED) as z:
    for fn in sorted(os.listdir(GT)): z.write(os.path.join(GT, fn), fn)
print('kv', len(st), 'stations', len(trips), 'trips')
