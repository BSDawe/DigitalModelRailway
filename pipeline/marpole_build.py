"""Lulu Island Lines, B.C. Electric card R 2M-9-47 (corrected to September 16, 1947), both sides.
Routes: 'lulu' Davie St -> Marpole -> Steveston;  'nwm' Marpole -> New Westminster."""
import csv, json, os, re, zipfile
from xml.etree import ElementTree as ET
from pyproj import Transformer
from shapely.geometry import LineString, Point
HERE = os.path.dirname(os.path.abspath(__file__)); GT = os.path.join(HERE, 'gtfs')
fwd = Transformer.from_crs(4326, 26910, always_xy=True).transform
inv = Transformer.from_crs(26910, 4326, always_xy=True).transform
MI = 1609.344
geo = json.load(open(os.path.join(HERE, 'marpole_geometry.json')))
RT = {k: LineString([fwd(*p) for p in geo[k]]) for k in ('lulu', 'nwm')}

# ---------------- KML Second District stations
NS = {'k': 'http://www.opengis.net/kml/2.2'}; K = '{http://www.opengis.net/kml/2.2}'
tree = ET.parse(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'British_Columbia_Electric_Railway_Company.kml'))
par = {c: p for p in tree.iter() for c in p}
def fpath(e):
    o = []
    while e in par:
        e = par[e]
        if e.tag == K + 'Folder': o.append(e.find('k:name', NS).text)
    return '/'.join(o[::-1])
KML = []
for p in tree.iter(K + 'Placemark'):
    if fpath(p).endswith('Second District/Stations'):
        d = p.find('k:description', NS); d = re.sub('<[^>]+>', '', (d.text or '') if d is not None else '').strip()
        KML.append(dict(name=p.find('k:name', NS).text, desc=d,
                        ll=tuple(map(float, p.find('.//k:coordinates', NS).text.split(',')[:2]))))

# ---------------- running times: (card name, KML name or None, minutes down, minutes up)  None = '—' / blank
V = [('Davie Street', 'Davie Street station', 0, 27), ('4th Avenue', '4th avenue station', 5, 22),
     ('9th Avenue', 'Broadway station', 8, 18), ('13th Avenue', '13th avenue station', 10, 17),
     ('16th Avenue', '16th avenue station', 12, 16), ('22nd Avenue', '22nd Avenue station', 13, 14),
     ('29th Avenue', '29th Avenue station', 14, 13), ('33rd Avenue', '33rd Avenue station', 15, 12),
     ('Strathcona East', 'Strathcona East station', 16, 11), ('Strathcona Place–37th Avenue', 'Strathcona station', 17, 10),
     ('Kerrisdale–41st Avenue', 'Kerrisdale station', 18, 9), ('45th Avenue', '45th Street station', 19, 8),
     ('49th Avenue', 'MaGee/49th Street station station', None, 7), ('51st Avenue', 'Royal/51st Street station', 20, None),
     ('57th Avenue', '57th (Shannon) Street station', 21, 6), ('64th Avenue', 'Shaugnessy/64th Street station', 23, 4),
     ('70th Avenue', '70th Street station', 24, 3), ('Granville Road', 'Granville station', 25, 1),
     ('Marpole', 'Marpole station', 27, 0)]
S = [('Marpole', 'Marpole station', 0, 27), ('Tucks', 'Tucks station', None, None), ('Bridgeport', 'Bridgeport station', 4, 23),
     ('Sexsmith', 'Sexsmith station', None, None), ('Cambie', 'Cambie station', 7, 21), ('Alexandra', 'Alexandra station', None, None),
     ('Lansdowne', 'Lansdowne station', 8, 20), ('Ferndale', 'Ferndale station', None, None), ('Garden City', 'Garden City station', None, None),
     ('Brighouse', 'Brighouse station', 14, 15), ('Lulu', 'Lulu station', 16, 12), ('Riverside', 'Riverside station', None, None),
     ('McCallum Road', 'McCallan Road station', None, None), ('Blundell', 'Blundell station', 18, 9),
     ('Francis Road', 'Francis station', None, None), ('Woodwards', 'Woodwards station', 21, 6), ('Cottages', 'Cottages station', None, None),
     ('Branscombe', 'Branscomb station', 23, 4), ('Steveston Wye', 'Steveston Wye station', None, None), ('Steveston', 'Steveston station', 27, 0)]
NWB = [('Marpole', 'Marpole station', 0, 27), ('Shaughnessy Street', 'Shaughnessy Street station', None, None),
       ('Heather Street', 'Heather Street station', None, None), ('Ash Street', 'Ash Street station', None, None),
       ('Ontario Street', 'Ontario Street station', None, None), ('Main Street', 'Main Street station', 3, 22),
       ('Fraser Street', 'Fraser Street station', 4, 21), ('Campbell Road', 'Campbell Road station', 5, 20),
       ('Argyle', 'Argyle station', 6, 19), ('Rowlings', 'Rowlings/Nanaimo station', 7, 18), ('Jellicoe Street', 'Jellico station', 8, 16),
       ('Kerr Road', 'Kerr station', 9, 15), ('Dominion Mills', 'Dominion Mills station', 10, 14), ('Plywoods', 'Plywoods station', 11, 13),
       ('Boundary Road', 'Boundary station', 12, 12), ('Alberta', 'Alberta station', 13, 11), ('Glen Lyon', 'Glen Lyon station', 14, 10),
       ('Sussex', 'Sussex station', 15, None), ('Byrne Road', 'Byrne Road station', 16, 9), ('Trapp Road', 'Trapp Road station', 18, 8),
       ('Springs', 'Springs station', 19, 7), ('20th Street', '20th Street station', 20, 6), ('18th Street', None, None, 5),
       ('16th Street', None, 21, 4), ('14th Street', None, None, None), ('3rd Avenue', None, 23, 3), ('12th Street', None, 25, None),
       ('New Westminster', '*NW', 27, 0)]

def place(rk, rows):
    R = RT[rk]; out = []
    for name, kn, dn, up in rows:
        if kn == '*NW': ch, ll, desc = R.length, inv(*R.coords[-1]), ''
        elif kn:
            cands = [k for k in KML if k['name'] == kn]
            best = min(cands, key=lambda k: R.distance(Point(fwd(*k['ll']))))
            q = Point(fwd(*best['ll'])); off = R.distance(q)
            if off > 60: print(f'  !! {name}: {off:.0f} m off route')
            ch, ll, desc = R.project(q), best['ll'], best['desc']
        else: ch, ll, desc = None, None, ''
        out.append(dict(name=name, chain=ch, ll=ll, down=dn, up=up, desc=desc,
                        note='' if kn else 'not plotted in KML; placed by running time'))
    # unplotted: place by running time (down if known else up) between plotted neighbours
    for i, s in enumerate(out):
        if s['chain'] is not None: continue
        a = max(j for j in range(i) if out[j]['chain'] is not None); b = min(j for j in range(i + 1, len(out)) if out[j]['chain'] is not None)
        key = 'down' if s['down'] is not None and out[a]['down'] is not None and out[b]['down'] is not None else 'up'
        if s[key] is None or out[a][key] is None or out[b][key] is None: f = (i - a) / (b - a)
        else: f = (s[key] - out[a][key]) / (out[b][key] - out[a][key])
        s['chain'] = out[a]['chain'] + f * (out[b]['chain'] - out[a]['chain'])
        s['ll'] = inv(*R.interpolate(s['chain']).coords[0])
    bad = [(x['name'], y['name']) for x, y in zip(out, out[1:]) if y['chain'] <= x['chain']]
    if bad: print('  !! order problems', rk, bad)
    return out

lulu = place('lulu', V + S[1:])   # Davie ... Marpole ... Steveston (Marpole once)
nwm = place('nwm', NWB)
# Marpole row carries both sections' times: down = Davie-based, and a second clock from Marpole for Steveston
mi = [s['name'] for s in lulu].index('Marpole')
for s in lulu[mi + 1:]:
    s['down'] = None if s['down'] is None else s['down'] + 27    # minutes from Davie
    s['up'] = None if s['up'] is None else s['up']               # minutes from Steveston
for s in lulu[:mi + 1]:
    s['up'] = None if s['up'] is None else s['up'] + 27          # Marpole->Davie read up, shifted by Steveston->Marpole 27
lulu[mi]['up'] = 27

def fill(stops, key, rev=False):
    known = [i for i, s in enumerate(stops) if s[key] is not None]
    t = {}
    for a, b in zip(known, known[1:]):
        for i in range(a, b + 1):
            f = (stops[i]['chain'] - stops[a]['chain']) / (stops[b]['chain'] - stops[a]['chain'])
            t[i] = round((stops[a][key] + f * (stops[b][key] - stops[a][key])) * 60)
    return t
T = {'lulu': (fill(lulu, 'down'), fill(lulu, 'up')), 'nwm': (fill(nwm, 'down'), fill(nwm, 'up'))}
for rk, stops in (('lulu', lulu), ('nwm', nwm)):
    dn, up = T[rk]
    tp = [i for i, s in enumerate(stops) if s['down'] is not None]
    sp = ' '.join(f"{(stops[b]['chain']-stops[a]['chain'])/MI/((dn[b]-dn[a])/3600):.0f}" for a, b in zip(tp, tp[1:]))
    print(rk, 'EB mph between timed stations:', sp)
    tp = [i for i, s in enumerate(stops) if s['up'] is not None]
    sp = ' '.join(f"{(stops[b]['chain']-stops[a]['chain'])/MI/((up[a]-up[b])/3600):.0f}" for a, b in zip(tp, tp[1:]))
    print(rk, 'WB mph between timed stations:', sp)

# ---------------- departures
def seq(txt):
    """'5.30† 6.00† ...' in time order -> [(seconds, symbol)]; am/pm inferred from order (card: light a.m., heavy p.m.)"""
    out, base, prev = [], 0, -1
    for tok in txt.split():
        m = re.match(r'(\d+)\.(\d+)(.*)', tok); h, mn, sym = int(m.group(1)), int(m.group(2)), m.group(3)
        v = (h % 12) * 60 + mn
        while base + v <= prev: base += 12 * 60
        prev = base + v; out.append((prev * 60, sym))
    return out
LULU_NW_EB = seq('5.30† 6.00† 7.00† 8.00 10.00 12.00 2.00 4.00 5.00† 6.00 8.00 10.00 11.30')
LULU_NW_WB = seq('6.30† 7.00† 8.00† 9.00 11.00 1.00 3.00 5.00 6.00† 7.00 9.00 11.00 12.30')
STEV_EB = seq('5.00† 5.30† 6.00† 6.30† 7.00 8.00 9.00 10.00 11.00 12.00 1.00 2.00 2.30† 3.00 3.30† 4.00 4.30† 5.00 5.30† 6.00 '
              '6.30† 7.00 8.00 9.00 10.00 11.00 12.00 1.00x')
STEV_WB = seq('6.00† 6.30† 7.00† 7.30† 7.55 9.00 10.00 11.00 12.00 1.00 2.00 3.00 3.30† 4.00 4.30† 5.00 5.30† 6.00 6.30† 7.00 '
              '7.30† 8.00 9.00 10.00 11.00 12.00 1.00 2.00x')
MAR_EB = seq('5.00† 5.30† 6.00† 6.15† 6.30† 6.45† 7.00 7.15† 7.30 7.45† 8.00 8.15† 8.30 9.00 9.30 10.00 10.30 11.00 11.30 '
             '12.00 12.30 12.45* 1.00 1.15* 1.30 1.45* 2.00 2.15* 2.30 2.45* 3.00 3.15* 3.30 3.45† 4.00 4.15† 4.30 4.45† '
             '5.00 5.13†† 5.15* 5.23†† 5.30 5.45† 6.00 6.15† 6.30 7.00 7.30 8.00 8.30 9.00 9.30 10.00 10.30 11.00 11.30 '
             '12.00 12.30† 1.00x')
MAR_WB = seq('6.00† 6.30† 6.45† 7.00† 7.15† 7.30† 7.45† 7.55† 8.00 8.15† 8.23† 8.30 8.45† 9.00 9.30 10.00 10.30 11.00 '
             '11.30 12.00 12.30 1.00 1.15* 1.30 1.45* 2.00 2.15* 2.30 2.45* 3.00 3.15* 3.30 3.45* 4.00 4.15† 4.30 4.45† '
             '5.00 5.15† 5.30 5.45† 6.00 6.15† 6.30 6.45† 7.00 7.30 8.00 8.30 9.00 9.30 10.00 10.30 11.00 11.30 12.00 '
             '12.30 1.00 1.30 2.30x')
# day types: WKDY = Mon–Fri, SAT, SUN.  X (Sunday only) cars run after midnight -> the Saturday-night service day.
def runs(sym, day):
    if sym == '†': return day in ('WKDY', 'SAT')
    if sym == '††': return day == 'WKDY'
    if sym == '*': return day == 'SAT'
    if sym == 'x': return day == 'SAT'
    return True

names = {rk: [s['name'] for s in st] for rk, st in (('lulu', lulu), ('nwm', nwm))}
STOPS = {'lulu': lulu, 'nwm': nwm}
def mk(rk, svc, d, t0, a, b, extra=None):
    """trip on route rk from station a to b leaving at t0; times from the running-time columns"""
    dn, up = T[rk]; ia, ib = names[rk].index(a), names[rk].index(b)
    if d == 0: idx = range(ia, ib + 1); off = lambda i: dn[i] - dn[ia]
    else: idx = range(ia, ib - 1, -1); off = lambda i: up[i] - up[ia]
    rows = [[i, t0 + off(i), t0 + off(i), 1 if (STOPS[rk][i]['down'] if d == 0 else STOPS[rk][i]['up']) is not None else 0] for i in idx]
    if extra: extra(rows)
    return dict(rk=rk, svc=svc, dir=d, stops=rows)

trips = []; log = []
for day in ('WKDY', 'SAT', 'SUN'):
    svc = 'LU_' + day
    stev_eb = [t for t, s in STEV_EB if runs(s, day)]
    mar_eb = [t for t, s in MAR_EB if runs(s, day)]
    missing = [t for t in stev_eb if t not in mar_eb]
    if missing: log.append(f'{day}: Steveston departures not in Marpole list {missing}')
    for t in mar_eb:
        trips.append(mk('lulu', svc, 0, t, 'Davie Street', 'Steveston' if t in stev_eb else 'Marpole'))
    # westbound: Steveston trains reach Marpole +27 and leave on the next Marpole departure
    mar_wb = [t for t, s in MAR_WB if runs(s, day)]; used = set()
    for t in [t for t, s in STEV_WB if runs(s, day)]:
        arr = t + 27 * 60
        dep = min([m for m in mar_wb if m >= arr and m <= arr + 8 * 60 and m not in used], default=None)
        if dep is None: log.append(f'{day}: Steveston {t//3600}:{t%3600//60:02d} has no Marpole departure'); continue
        used.add(dep)
        def hold(rows, dep=dep, arr=arr):
            k = [r[0] for r in rows].index(names['lulu'].index('Marpole'))
            shift = dep - arr
            rows[k][2] += shift
            for r in rows[k + 1:]: r[1] += shift; r[2] += shift
        trips.append(mk('lulu', svc, 1, t, 'Steveston', 'Davie Street', hold))
    for t in mar_wb:
        if t not in used:
            dn, up = T['lulu']; mi_ = names['lulu'].index('Marpole')
            trips.append(mk('lulu', svc, 1, t, 'Marpole', 'Davie Street'))
    # New Westminster branch cars, connecting at Marpole
    for t, s in LULU_NW_EB:
        if runs(s, day): trips.append(mk('nwm', 'NM_' + day, 0, t + 27 * 60, 'Marpole', 'New Westminster'))
    for t, s in LULU_NW_WB:
        if runs(s, day): trips.append(mk('nwm', 'NM_' + day, 1, t, 'New Westminster', 'Marpole'))
print(*log, sep='\n')
from collections import Counter
print(Counter((t['svc'], t['rk'], t['dir'], names[t['rk']][t['stops'][-1][0]]) for t in trips))
for i, t in enumerate(trips): t['id'] = f"{t['svc']}-{t['dir']}-{t['stops'][0][1]}-{names[t['rk']][t['stops'][-1][0]][:4]}-{i}"
json.dump(dict(lulu=lulu, nwm=nwm, trips=trips, names=names), open(os.path.join(HERE, 'marpole_model.json'), 'w'), default=str)

# ---------------- viz + GTFS
vd = json.load(open(os.path.join(HERE, 'viz_data.json')))
LABEL = {'lulu': 'Lulu Island Line', 'nwm': 'Marpole–New Westminster'}
KIND = {'lulu': 'l', 'nwm': 'n'}
lines = []
for rk, stops in (('lulu', lulu), ('nwm', nwm)):
    R = RT[rk]; route = []; acc = 0; prev = None
    for xy in R.simplify(1.0).coords:
        if prev: acc += ((xy[0]-prev[0])**2 + (xy[1]-prev[1])**2) ** .5
        prev = xy; lon, lat = inv(*xy); route.append([round(lon, 6), round(lat, 6), round(acc, 1)])
    sc = acc / R.length
    st = []
    for s in stops:
        gid = {'Marpole': 'MARPOLE', 'New Westminster': 'S01'}.get(s['name'])
        desc = s['desc'] if s['desc'] not in ('No data.', '') else ''
        st.append(dict(name=s['name'], gid=gid, shared='S01' if s['name'] == 'New Westminster' else None,
                       chain=round(s['chain'] * sc, 1), lon=round(s['ll'][0], 6), lat=round(s['ll'][1], 6),
                       mile=round(s['chain'] / MI, 1), note=s['note'], kml=desc[:160],
                       principal=s['name'] in ('Davie Street', 'Marpole', 'Steveston', 'Brighouse')))
    mar = next(x['chain'] for x in st if x['name'] == 'Marpole')
    lines.append(dict(key=rk, kind=KIND[rk], label=LABEL[rk], route=route, stations=st,
                      doubleTo=mar if rk == 'lulu' else 0,
                      trips=[dict(id=t['id'], svc=t['svc'], dir=t['dir'], stops=t['stops']) for t in trips if t['rk'] == rk]))
vd['lines'] = lines
open(os.path.join(HERE, 'viz_data.json'), 'w').write(json.dumps(vd, separators=(',', ':')))

def fmt(x): return f'{x // 3600:02d}:{x % 3600 // 60:02d}:{x % 60:02d}'
def app(name, rows):
    with open(os.path.join(GT, name), 'a', newline='') as f: csv.writer(f).writerows(rows)
app('routes.txt', [['LUL', 'BCER', 'Lulu Island', 'Vancouver (Davie St) – Marpole – Steveston', 2, '5D7A1F', 'FFFFFF',
                    'Lulu Island Lines card corrected to September 16, 1947. Includes Marpole short turns.'],
                   ['NWM', 'BCER', 'Marpole–New Westminster', 'Marpole – New Westminster', 2, '5B6B8C', 'FFFFFF',
                    'Lulu Island Lines card, September 16, 1947; branch cars connecting at Marpole with Vancouver trains.']])
app('calendar.txt', [[p + '_WKDY', 1, 1, 1, 1, 1, 0, 0, '19490616', '19491231'] for p in ('LU', 'NM')] +
                    [[p + '_SAT', 0, 0, 0, 0, 0, 1, 0, '19490616', '19491231'] for p in ('LU', 'NM')] +
                    [[p + '_SUN', 0, 0, 0, 0, 0, 0, 1, '19490616', '19491231'] for p in ('LU', 'NM')])
sid = {}
rows = []
for rk, stops in (('lulu', lulu), ('nwm', nwm)):
    for i, s in enumerate(stops):
        if s['name'] == 'New Westminster': sid[(rk, i)] = 'S01'; continue
        if s['name'] == 'Marpole': sid[(rk, i)] = 'L_MARPOLE'
        else: sid[(rk, i)] = f"{'L' if rk == 'lulu' else 'N'}{i:02d}"
        if sid[(rk, i)] not in [r[0] for r in rows]:
            rows.append([sid[(rk, i)], s['name'], f"{s['ll'][1]:.6f}", f"{s['ll'][0]:.6f}",
                         LABEL[rk] + ('; ' + s['note'] if s['note'] else '')])
app('stops.txt', rows)
shp = []
for rk in ('lulu', 'nwm'):
    for shape_id, coords in ((rk.upper() + '_OUT', list(RT[rk].coords)), (rk.upper() + '_IN', list(RT[rk].coords)[::-1])):
        acc, prev = 0.0, None
        for k, xy in enumerate(coords):
            if prev: acc += ((xy[0]-prev[0])**2 + (xy[1]-prev[1])**2) ** .5
            prev = xy; lon, lat = inv(*xy); shp.append([shape_id, f'{lat:.6f}', f'{lon:.6f}', k, f'{acc:.1f}'])
app('shapes.txt', shp)
app('trips.txt', [['LUL' if t['rk'] == 'lulu' else 'NWM', t['svc'], t['id'], names[t['rk']][t['stops'][-1][0]],
                   LABEL[t['rk']] + ' car', t['dir'], t['rk'].upper() + ('_OUT' if t['dir'] == 0 else '_IN')] for t in trips])
st_rows = []
for t in trips:
    R = RT[t['rk']]
    for k, (i, a, b, tp) in enumerate(t['stops'], 1):
        c = STOPS[t['rk']][i]['chain']; dist = c if t['dir'] == 0 else R.length - c
        st_rows.append([t['id'], fmt(a), fmt(b), sid[(t['rk'], i)], k, f'{dist:.1f}', 1 if k in (1, len(t['stops'])) else tp])
app('stop_times.txt', st_rows)
with zipfile.ZipFile(os.path.join(HERE, 'bcer_fraser_valley_1949_gtfs.zip'), 'w', zipfile.ZIP_DEFLATED) as z:
    for fn in sorted(os.listdir(GT)): z.write(os.path.join(GT, fn), fn)
print('GTFS + ', len(trips), 'trips', len(st_rows), 'stop_times')
