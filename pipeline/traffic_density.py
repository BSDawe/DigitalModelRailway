"""Trains per week on each section of track (Brendan, 22 Oct 2026). Reads the built page data (viz_data.json) and the GTFS calendar;
writes traffic_density.gpkg (layer 'sections'): one LineString per run of track with the same counts.
Counted: rail only (no steamers); each trip once per day it runs (a through train split across sections is several trips, each on its own track,
so it is counted once on any piece); trips wholly in the United States are left out (trains that enter Canada are kept whole, US part included).
Columns: total (trains per week), one column per operator (the railway running the train, not the track owner), and 'track' (the track owner drawn)."""
import json, os, csv, io, zipfile, collections
import geopandas as gpd
from shapely.geometry import LineString
HERE = os.path.dirname(os.path.abspath(__file__))
V = json.load(open(os.path.join(HERE, 'viz_data.json')))
DAYS = {}
with zipfile.ZipFile(os.path.join(HERE, 'bcer_fraser_valley_1949_gtfs.zip')) as z:
    for r in csv.DictReader(io.TextIOWrapper(z.open('calendar.txt'), 'utf-8-sig')):
        DAYS[r['service_id']] = sum(int(r[d]) for d in ('monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'))
def days(svc):
    if svc in DAYS: return DAYS[svc]
    if svc.startswith('W_') and len(svc) == 9: return svc[2:].count('1')
    raise SystemExit(f'unknown service {svc}')
OP = {'q': 'cn', 'p': 'cp', 'g': 'gn', 'o': 'np', 'i': 'en', 'r': 'pge', 'y': 'wpy', 'a': 'nar', 'd': 'sps', 'u': 'up', 'm': 'milw', 'k': 'arr', 'x': 'cnw',
      'j': 'gwwd', 'c': 'bcer', 'b': 'bcer', 'l': 'bcer', 'n': 'bcer'}
def canada(lon, lat):
    if lon <= -141: return False                                   # Alaska
    if lon < -135.0 and 54.7 < lat < 60: return False              # the Alaska panhandle (Skagway, White Pass)
    if lon > -95.15: return lat > 48.0                             # Ontario (Duluth etc. below 48)
    if lon < -123.2: return lat >= 48.3                            # Vancouver Island
    return lat >= 48.999
lines = [dict(kind=L['kind'], own=L.get('owner'), route=L['route'], stations=L['stations'], trips=L['trips'], segments=L.get('segments', [])) for L in V['lines'] if L['kind'] != 'v']
lines.append(dict(kind='c', own='bcer', route=V['route'], stations=V['stations'], trips=V['trips'], segments=[]))    # the Fraser Valley line
K = lambda a, b: tuple(sorted(((round(a[0], 6), round(a[1], 6)), (round(b[0], 6), round(b[1], 6)))))
count = collections.defaultdict(collections.Counter)            # segment key -> operator -> trains per week
owner = {}
for L in lines:
    R = L['route']; ch = [p[2] for p in R]; op = OP[L['kind']]
    for s in L['segments']:
        for i in range(len(R) - 1):
            m = (ch[i] + ch[i + 1]) / 2
            if s['a'] <= m <= s['b'] and s['owner'] not in ('none', None): owner[K(R[i], R[i + 1])] = s['owner']
    for i in range(len(R) - 1): owner.setdefault(K(R[i], R[i + 1]), L['own'] or OP[L['kind']])
    for t in L['trips']:
        st = [L['stations'][s[0]] for s in t['stops']]
        if not any(canada(s['lon'], s['lat']) for s in st): continue
        a, b = min(s['chain'] for s in st), max(s['chain'] for s in st); n = days(t['svc'])
        for i in range(len(R) - 1):
            if ch[i] >= a - 1 and ch[i + 1] <= b + 1: count[K(R[i], R[i + 1])][op] += n
OPS = sorted({o for c in count.values() for o in c})
feats, done = [], set()
def emit(run, key):
    if len(run) > 1:
        c = dict(key[0]); feats.append(dict(geometry=LineString(run), total=sum(c.values()), track=key[1] or '', **{o: c.get(o, 0) for o in OPS}))
for L in lines:
    R = L['route']; run, cur = [], None
    for i in range(len(R) - 1):
        k = K(R[i], R[i + 1])
        if k in done or k not in count:
            emit(run, cur); run, cur = [], None; continue
        key = (tuple(sorted(count[k].items())), owner.get(k)); done.add(k)
        if run and key == cur: run.append(R[i + 1][:2])
        else: emit(run, cur); run, cur = [R[i][:2], R[i + 1][:2]], key
    emit(run, cur)
g = gpd.GeoDataFrame(feats, crs='EPSG:4326')
g.to_file(os.path.join(HERE, 'traffic_density.gpkg'), layer='sections', driver='GPKG')
print(len(g), 'sections;', 'operators:', ', '.join(OPS), '; busiest:', g.sort_values('total').iloc[-1][['total'] + OPS].to_dict())
