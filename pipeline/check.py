import json, csv, re, math, itertools
from xml.etree import ElementTree as ET
from pyproj import Transformer
from shapely.geometry import LineString, Point

fwd = Transformer.from_crs(4326, 26910, always_xy=True).transform
MI = 1609.344
m = json.load(open('model.json'))
geo = json.load(open('geometry.json'))
route = LineString([fwd(*p) for p in geo['route']])
S = {s['stop_id']: s for s in m['stations']}
st = m['stations']
L = m['route_len_m']
out = []
P = out.append

# ---------- 1. station placement
P('## 1. Station placement vs timetable mileage')
nw = [s for s in st if s['tt_name'] == 'New Westminster'][0]
bad = []
for s in st:
    chain_mi = (s['chain_m'] - nw['chain_m']) / MI + 12.5  # aligned at New Westminster
    s['chain_mi'] = chain_mi
    diff = chain_mi - s['mile_eb']
    flag = abs(diff) > 0.25 or s['offset_m'] > 60
    if flag:
        bad.append(s)
    P(f"{'!!' if flag else '  '} {s['name']:<18} tt {s['mile_eb']:>5}  track {chain_mi:6.2f}  diff {diff:+.2f}  "
      f"off-line {s['offset_m']:4.0f} m  kml_mile {s.get('kml_mile')}")
order_ok = all(a['chain_m'] < b['chain_m'] for a, b in zip(st, st[1:]))
P(f'stations in order along track: {order_ok}')

# ---------- 2. EB vs WB printed mileages
P('\n## 2. Eastbound vs westbound printed mileages (WB converted to miles from Vancouver)')
eb = {r['station']: r for r in csv.DictReader(open('transcription_eastbound.csv'))}
alias = {'Halls Prairie': "Hall's Prairie", 'Burkhart Road': 'Burkart Road'}
for r in csv.DictReader(open('transcription_westbound.csv')):
    n = alias.get(r['station'], r['station'])
    if r['mileage'] and eb[n]['mileage']:
        conv = round(76.3 - float(r['mileage']), 1)
        if abs(conv - float(eb[n]['mileage'])) > 0.05:
            P(f"   {n}: EB {eb[n]['mileage']}  WB {r['mileage']} (= {conv} from Vancouver)")

# ---------- 3. speeds
P('\n## 3. Implied speeds between consecutive stops (flag > 45 mph or < 8 mph)')
maxv = 0
for t in m['trips']:
    for (a, ta, da, tpa), (b, tb, db, tpb) in zip(t['stops'], t['stops'][1:]):
        d = abs(S[b]['chain_m'] - S[a]['chain_m']) / MI
        mins = (tb - da) / 60
        v = d / (mins / 60) if mins > 0 else float('inf')
        if S[a]['tt_name'] == 'VANCOUVER' or S[b]['tt_name'] == 'VANCOUVER':
            P(f"   info  train {t['trip_id']:<7} Vancouver–New Westminster street/ROW run: {d:.1f} mi in {mins:.0f} min = {v:.0f} mph")
            continue
        maxv = max(maxv, v if v != float('inf') else 0)
        if v > 45 or v < 8:
            P(f"!! train {t['trip_id']:<7} {S[a]['name']} → {S[b]['name']}: {d:.2f} mi in {mins:.0f} min = "
              f"{'∞' if v == float('inf') else f'{v:.0f}'} mph  (tp {tpa}{tpb})")
    tot = abs(S[t['stops'][-1][0]]['chain_m'] - S[t['stops'][0][0]]['chain_m']) / MI
    P(f"   train {t['trip_id']:<7} overall {tot:.1f} mi in {(t['stops'][-1][1]-t['stops'][0][2])/60:.0f} min "
      f"= {tot/((t['stops'][-1][1]-t['stops'][0][2])/3600):.1f} mph")

# ---------- 4. meets
# passing sidings from KML
ns = {'k': 'http://www.opengis.net/kml/2.2'}
K = '{http://www.opengis.net/kml/2.2}'
tree = ET.parse(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'British_Columbia_Electric_Railway_Company.kml'))
parent = {c: p for p in tree.iter() for c in p}
def fpath(e):
    o = []
    while e in parent:
        e = parent[e]
        if e.tag == K + 'Folder':
            o.append(e.find('k:name', ns).text)
    return '/'.join(o[::-1])
sidings = []
for p in tree.iter(K + 'Placemark'):
    fp = fpath(p)
    if 'Third District' in fp and 'Sidings' in fp:
        d = p.find('k:description', ns)
        d = re.sub('<[^>]+>', '', (d.text or '') if d is not None else '')
        c = [tuple(map(float, x.split(',')[:2])) for x in p.find('.//k:coordinates', ns).text.split()]
        ls = LineString([fwd(*q) for q in c])
        a, b = route.project(Point(ls.coords[0])), route.project(Point(ls.coords[-1]))
        sidings.append(dict(desc=d.strip()[:70], lo=min(a, b), hi=max(a, b)))


def pos(t, sec):
    """chainage of trip t at time sec (None if not running)"""
    s = t['stops']
    if sec < s[0][2] or sec > s[-1][1]:
        return None
    for (a, ta, da, _), (b, tb, db, _) in zip(s, s[1:]):
        if ta <= sec <= da:
            return S[a]['chain_m']
        if da <= sec <= tb:
            f = (sec - da) / (tb - da) if tb > da else 1
            return S[a]['chain_m'] + f * (S[b]['chain_m'] - S[a]['chain_m'])
    return S[s[-1][0]]['chain_m']


P('\n## 4. Where opposing trains meet on the single track (from the timetable, minute by minute)')
svc_days = {'DAILY': {'mon', 'fri', 'sat'}, 'FRI': {'fri'}, 'SAT': {'sat'}}
meets = []
for a, b in itertools.product([t for t in m['trips'] if t['dir'] == 0], [t for t in m['trips'] if t['dir'] == 1]):
    if not (svc_days[a['service']] & svc_days[b['service']]):
        continue
    prev = None
    for sec in range(0, 30 * 3600, 15):
        pa, pb = pos(a, sec), pos(b, sec)
        if pa is None or pb is None:
            prev = None
            continue
        d = pb - pa
        if prev is not None and (d <= 0 < prev or abs(d) < 1):
            nearest = min(m['stations'], key=lambda s: abs(s['chain_m'] - pa))
            sd = [x for x in sidings if x['lo'] - 150 <= pa <= x['hi'] + 150]
            meets.append((a['trip_id'], b['trip_id'], sec, pa, nearest, sd))
            break
        prev = d
for ta, tb, sec, pa, near, sd in meets:
    hh, mm = divmod(sec // 60, 60)
    P(f"   {ta:>6} × {tb:<6} {hh % 24:02d}:{mm:02d}  at mile {(pa - nw['chain_m'])/MI + 12.5:5.1f} "
      f"(nearest station {near['name']}, {abs(near['chain_m']-pa):.0f} m)  "
      f"siding in KML: {sd[0]['desc'] if sd else 'NONE'}")

open('check_report.txt', 'w').write('\n'.join(out))
print('\n'.join(out))
