"""Merritt (Table 154), Slocan (Table 158 rail), Nakusp and Kimberley (Table 153) branch lines, built on Brendan's traces (KVR Trails, nakusp_end.kml,
bc_railway_bits.kml). Also sets Okanagan ownership (Brendan): CP owns Sicamous - Armstrong
- Vernon; CN owns Campbell Creek Jct - the wye near Armstrong and Vernon - Kelowna. Run after cps_build.py."""
import csv, json, math, os, re, zipfile
from shapely import wkt
from shapely.geometry import LineString, Point
from nrwn_graph import fwd, inv, MI
from shapely.ops import substring
from bc_bits import K as BITS
HERE = os.path.dirname(os.path.abspath(__file__)); GT = os.path.join(HERE, 'gtfs')
csv.field_size_limit(10 ** 9)
NT = {r['FRAARCID']: [p[:2] for ls in wkt.loads(r['wkt_geom']).geoms for p in ls.coords]
      for r in csv.DictReader(open(os.path.join(HERE, 'ntad_interim.tsv')), delimiter='\t')}
vd = json.load(open(os.path.join(HERE, 'viz_data.json')))
L = {l['key']: l for l in vd['lines']}
def st(line, name): return next(s for s in L[line]['stations'] if s['name'] == name)
def sub_route(line, a, b):
    """viz route points of an existing line between station chains a and b (in a -> b order)"""
    lo, hi = sorted((a, b)); pts = [(p[0], p[1]) for p in L[line]['route'] if lo <= p[2] <= hi]
    return pts if a <= b else pts[::-1]

def times(txt):
    arr = dep = None
    for m in re.finditer(r'(ar|lv)?\s*f?(\d+)\.(\d+)([ap])', txt):
        h, mn = int(m.group(2)), int(m.group(3))
        if m.group(4) == 'p' and h != 12: h += 12
        if m.group(4) == 'a' and h == 12: h = 0
        x = h * 3600 + mn * 60
        if m.group(1) == 'ar': arr = x
        elif m.group(1) == 'lv': dep = x
        else: arr = dep = x
    return (arr if arr is not None else dep), (dep if dep is not None else arr)

NEW = []
def build(key, label, dir_labels, legs, stops_def, trains, segments_none=(), principal=()):
    """legs: list of lon/lat point lists joined in order. stops_def: [(name, gid, leg_index, fraction_along_leg | (lon,lat))]"""
    pts, first = [], []
    for leg in legs:
        first.append(len(pts))
        for p in leg:
            if not pts or math.dist(fwd(*p), fwd(*pts[-1])) > 0.5: pts.append(p)
            elif len(pts) == first[-1]: first[-1] -= 1                    # the leg starts on the previous leg's last point
    R = LineString([fwd(*p) for p in pts])
    cum = [0.0]
    for a_, b_ in zip(R.coords, R.coords[1:]): cum.append(cum[-1] + math.dist(a_, b_))
    route = []; acc = 0.0; prev = None
    for xy in R.coords:
        if prev: acc += math.dist(xy, prev)
        prev = xy; lon, lat = inv(*xy); route.append([round(lon, 6), round(lat, 6), round(acc, 1)])
    stations = []
    for name, gid, li, f, mile, *more in stops_def:
        LL = LineString([fwd(*p) for p in legs[li]])
        ch = min(cum[-1], cum[min(first[li], len(cum) - 1)] + math.dist(R.coords[min(first[li], len(cum) - 1)], LL.coords[0]) + f * LL.length)
        lon, lat = inv(*R.interpolate(ch).coords[0])
        stations.append(dict(name=name, chain=round(ch, 1), lon=round(lon, 6), lat=round(lat, 6), mile=mile, principal=name in principal,
                             note='Canadian Pacific station', kml='', gid=gid, **(more[0] if more else {})))
    trips = []
    for col, num, svc, d, note in trains:
        seq = [(i, s) for i, s in enumerate(stops_def) if col in TT and TT[col][i]]
        seq = seq if d == 0 else seq[::-1]
        stops = [[i, *times(TT[col][i]), 1] for i, s in seq]
        base, prev = 0, -1
        for s in stops:
            for k in (1, 2):
                if s[k] + base < prev - 6 * 3600: base += 86400
                s[k] += base; prev = s[k]
        trips.append(dict(id=f'{key.upper()}-{num}', num=num, name='Mixed', svc=svc, dir=d, stops=stops, note=note))
        for (x, _, dx, _), (y, ty, _, _) in zip(stops, stops[1:]):
            dist = abs(stations[y]['chain'] - stations[x]['chain']) / MI; mins = (ty - dx) / 60
            if mins <= 0 or dist / (mins / 60) > 50: print('  !!', key, num, stations[x]['name'], stations[y]['name'], round(dist, 1), mins)
    segs = [dict(owner='none', a=stations[i]['chain'], b=stations[j]['chain']) for i, j in segments_none]
    NEW.append(dict(key=key, kind='p', label=label, mainline=True, owner='cp', route=route, stations=stations, dirLabels=dir_labels,
                    segments=segs, trips=trips, _R=R))
    print(f'{key}: {acc/MI:.1f} mi, {len(stations)} stations, {len(trips)} trips')

# ---------------- Merritt (Table 154): Brookmere - (KV) - Brodie - Merritt - Nicola and back - Merritt - Spence's Bridge
# Track: KV to Brodie; KVR Trails Merritt Sub for the first 5.3 mi; then Brendan's 'ds' trace (Spence's Bridge - Merritt - Merritt Sub, which
# overlaps the Merritt Sub trace there); Brendan's Nicola Branch from Nicola Jct (Merritt station is placed at the junction, 25.3 mi from Brodie
# against 25.4 printed).
kv = L['kv']; bm, bd = st('kv', 'Brookmere'), st('kv', 'Brodie')
leg_kv = sub_route('kv', bm['chain'], bd['chain'])                        # Brookmere -> Brodie on the Kettle Valley
from kvr_trails import lines as _kvr
KT = {k: [inv(*p) for p in v] for k, v in _kvr().items()}
MS = LineString([fwd(*p) for p in KT['Merritt Sub']])
DS = LineString([fwd(*p) for p in BITS['ds']]).reverse()                   # Brodie end -> Spence's Bridge
join = MS.project(Point(DS.coords[0])); NBR = BITS['Nicola Branch'][::-1]  # Merritt -> Nicola
jct = DS.project(Point(fwd(*BITS['Nicola Branch'][-1])))
ll = lambda g: [inv(*p) for p in g.coords]
# Nicola Jct wye (Brendan's trace): the leg from the Brodie side onto the branch. A train from Brookmere takes it to Nicola and comes back down
# the branch to the switch at Merritt, heading on to Spence's Bridge; a train from Spence's Bridge does the reverse. No backing either way.
NJ = BITS['Nicola Jct'] if DS.distance(Point(fwd(*BITS['Nicola Jct'][0]))) < DS.distance(Point(fwd(*BITS['Nicola Jct'][-1]))) else BITS['Nicola Jct'][::-1]   # main -> branch
NB = LineString([fwd(*p) for p in NBR]); wsw = DS.project(Point(fwd(*NJ[0]))); apex = NB.project(Point(fwd(*NJ[-1])))
leg_bm = [(bd['lon'], bd['lat'])] + ll(substring(MS, 0, join)) + ll(substring(DS, 0, wsw))     # Brodie -> the wye switch
leg_wye = NJ                                                                                   # wye switch -> the branch
leg_nic = ll(substring(NB, apex, NB.length))                                                   # -> Nicola
leg_back = NBR[::-1]                                                                           # Nicola -> the branch switch at Merritt
leg_sb = ll(substring(DS, jct, DS.length))                                                     # -> Spence's Bridge
MERRITT = inv(*DS.interpolate(jct).coords[0])
print(f'  Merritt: Brodie - wye switch {LineString([fwd(*p) for p in leg_bm]).length/MI:.1f} mi, switch to switch {(jct-wsw)/MI:.2f} mi (Brodie - Merritt printed 25.4), '
      f'Nicola branch {NB.length/MI:.1f} mi, ' f"Merritt - Spence's Bridge {LineString([fwd(*p) for p in leg_sb]).length/MI:.1f} mi (printed 39.8)")
cps_sb = st('cp', "Spence's Bridge")
TT = {'M805': ['lv 6.00a', '6.13a', 'f6.40a', 'f7.05a', 'ar 7.25a', 'ar 8.50a / lv 8.55a', 'lv 9.15a', 'f9.25a', 'f9.37a', 'f10.01a', 'f10.40a', 'f10.52a', 'f11.20a', 'ar 12.00p'],
      'M806': ['ar 1.35p', '1.20p', 'f12.40p', 'f12.00p', 'lv 11.15a', 'ar 10.30a / lv 10.35a', 'ar 10.05a', 'f9.55a', 'f9.42a', 'f9.23a', 'f8.53a', 'f8.42a', 'f8.20a', 'lv 7.45a']}
sb_miles = [(n, m) for n, m in (('Coutlee', 31.5), ('Coyle', 34.2), ('Canford', 39.9), ('Dot', 48.9), ('Agate', 51.9), ('Clapperton', 59.1))]
bm_miles = [('Kingsvale', 11.6), ('Glen Walker', 20.0)]
stops = [('Brookmere', bm['gid'], 0, 0.0, 0.0), ('Brodie', bd['gid'], 0, 1.0, 4.0)] + \
        [(n, 'MER_' + n.upper().replace(' ', '_'), 1, (m - 4.0) / (29.4 - 4.0), m) for n, m in bm_miles] + \
        [('Merritt', 'MER_MERRITT', 1, 1.0, 29.4, dict(xy=[round(MERRITT[0], 6), round(MERRITT[1], 6)])), ('Nicola', 'MER_NICOLA', 3, 1.0, 29.4),
         ('Merritt', 'MER_MERRITT', 4, 1.0, 29.4)] + \
        [(n, 'MER_' + n.upper(), 5, (m - 29.4) / (69.2 - 29.4), m) for n, m in sb_miles] + \
        [("Spence's Bridge", cps_sb['gid'], 5, 1.0, 69.2)]
build('mer', 'Canadian Pacific', ["to Merritt and Spence's Bridge", 'to Brookmere'], [leg_kv, leg_bm, leg_wye, leg_nic, leg_back, leg_sb], stops,
      [('M805', 'M805', 'CP_TF', 0, "Mixed train, Brookmere to Merritt, out to Nicola and back, then on to Spence's Bridge (Tuesdays and Fridays)."),
       ('M806', 'M806', 'CP_WS', 1, "Mixed train, Spence's Bridge to Merritt, out to Nicola and back, then on to Brookmere (Wednesdays and Saturdays).")],
      segments_none=[(0, 1)], principal={'Brookmere', 'Merritt', 'Nicola', "Spence's Bridge"})
EXTRA = [('x_mer', ll(substring(DS, wsw, jct)))]           # the main line between the two switches at Merritt: plain track (the route goes round by the wye)

# ---------------- Slocan (Table 158 rail): Nelson - (KV) - South Slocan - Slocan City; M841/M842 run through from Nelson
nel, ss = st('kv', 'Nelson'), st('kv', 'South Slocan')
leg_k = sub_route('kv', nel['chain'], ss['chain'])                          # Nelson -> South Slocan on the KV
leg_s = [(ss['lon'], ss['lat'])] + KT['C&K']                               # KVR Trails C&K trace (replaces the crude NTAD line)
TT = {'M841': ['lv 7.00a', 'f7.12a', 'f7.19a', 'f7.30a', 'ar 7.35a / lv 7.40a', '7.50a', '8.15a', '8.21a', 'f8.28a', 'f8.44a', '8.52a', '9.12a', 'f9.22a', 'ar 9.50a'],
      'M842': ['ar 5.25p', 'f5.07p', 'f5.00p', 'f4.50p', 'ar 4.20p / lv 4.46p', '4.10p', '3.45p', '3.39p', 'f3.32p', 'f3.16p', '3.08p', '2.47p', 'f2.36p', 'lv 2.15p']}
kvst = {s['name']: s for s in kv['stations']}
def frac_kv(n): return abs(kvst[n]['chain'] - nel['chain']) / abs(ss['chain'] - nel['chain'])
sl = [('Crescent Valley', 14.5), ('Slocan Park', 21.2), ('Passmore', 22.7), ('Vallican', 24.3), ('Lebahdo', 28.4), ('Winlaw', 30.4), ('Perrys', 35.5), ('Lemon Creek', 38.1)]
stops = [(n, kvst[n]['gid'], 0, frac_kv(n), kvst[n]['mile']) for n in ('Nelson', 'Taghum', 'Beasley', 'Bonnington', 'South Slocan')] + \
        [(n, 'SLO_' + n.upper().replace(' ', '_'), 1, (m - 11.9) / (43.2 - 11.9), m) for n, m in sl] + [('Slocan City', 'SLO_SLOCAN_CITY', 1, 1.0, 43.2)]
build('slo', 'Canadian Pacific', ['to Slocan City', 'to Nelson'], [leg_k, leg_s], stops,
      [('M841', 'M841', 'CP_MON1', 0, 'Mixed train, Nelson to Slocan City (Mondays), connecting with the CP steamer up Slocan Lake to Rosebery and the train to Nakusp.'),
       ('M842', 'M842', 'CP_WED1', 1, 'Mixed train, Slocan City to Nelson (Wednesdays), from Nakusp by train and the Slocan Lake steamer.')],
      segments_none=[(0, 4)], principal={'Nelson', 'South Slocan', 'Slocan City', 'Winlaw', 'Passmore'})
kv['trips'] = [t for t in kv['trips'] if t['num'] not in ('M841', 'M842')]       # now run through on the Slocan line

# ---------------- Nakusp (Table 158 rail, north part): Rosebery - Hills - Summit Lake - Brouse - Nakusp
# Track: KVR Trails N&SR line from Rosebery (its first 8 miles, Three Forks - Rosebery, have no 1948 passenger table) plus Brendan's
# trace of the last 9.5 miles into Nakusp (nakusp_end.kml).
import xml.etree.ElementTree as _ET
from shapely.ops import substring as _sub
_c = [tuple(map(float, t.split(',')[:2])) for t in _ET.parse(os.path.join(HERE, 'nakusp_end.kml')).getroot().find('.//{http://www.opengis.net/kml/2.2}coordinates').text.split()]
_ns = LineString([fwd(*p) for p in KT['N&SR']])
ROSEBERY = Point(fwd(-117.409, 50.032))                                    # Rosebery, on Slocan Lake
_r0 = _ns.project(ROSEBERY)
leg_n = [inv(*p) for p in _sub(_ns, _r0, _ns.length).coords] + _c
print(f'  Nakusp line: Rosebery {_ns.distance(ROSEBERY):.0f} m from the trace; Rosebery - Nakusp {LineString([fwd(*p) for p in leg_n]).length/MI:.1f} mi (timetable 28.4)')
TT = {'M841': ['lv 2.15p', 'f2.35p', '3.10p', '3.30p', 'ar 3.50p'], 'M842': ['ar 9.55a', 'f9.35a', '8.55a', 'f8.25a', 'lv 8.00a']}
nk = [('Rosebery', 67.2), ('Hills', 72.1), ('Summit Lake', 83.5), ('Brouse', 90.3), ('Nakusp', 95.6)]
stops = [(n, 'NAK_' + n.upper().replace(' ', '_'), 0, (m - 67.2) / (95.6 - 67.2), m) for n, m in nk]
build('nak', 'Canadian Pacific', ['to Nakusp', 'to Rosebery'], [leg_n], stops,
      [('M841', 'M841', 'CP_MON1', 0, 'Mixed train, Rosebery to Nakusp (Mondays), connecting from Nelson by the Slocan City train and the CP steamer up Slocan Lake.'),
       ('M842', 'M842', 'CP_WED1', 1, 'Mixed train, Nakusp to Rosebery (Wednesdays), connecting with the CP steamer down Slocan Lake and the train to Nelson.')],
      principal={'Rosebery', 'Nakusp', 'Summit Lake'})

# ---------------- Kimberley (Table 153): Cranbrook - Wanklyn - Wycliffe - Marysville - Chapman Camp - Kimberley
cb = st('cr', 'Cranbrook')
KB = BITS['Kimberley Branch']
# The branch leaves the present-day line 2.2 mi out of Cranbrook: 1.0 mi of that is the Crowsnest main line (drawn by the cr line), the rest is
# national-network track that the pre-1966 main line no longer covers.
leg0 = [tuple(p) for p in json.load(open(os.path.join(HERE, 'cranbrook_kimberley_jct.json')))]
_l0 = LineString([fwd(*p) for p in leg0]); shared_len = _l0.project(Point(fwd(*BITS['Cranbrook Pre-1966'][0])))
leg = leg0 + KB
print(f'  Kimberley: Cranbrook - branch switch {_l0.length/MI:.2f} mi ({shared_len/MI:.2f} shared with the main line), join gap {math.dist(fwd(*leg0[-1]), fwd(*KB[0])):.0f} m; '
      f'Cranbrook - Kimberley {LineString([fwd(*p) for p in leg]).length/MI:.1f} mi (printed 18.7)')
TT = {'M823': ['lv 7.15a', 'f7.36a', 'f7.46a', 'f8.05a', '8.25a', 'ar 8.45a'], 'M824': ['ar 12.55p', 'f12.20p', 'f11.03a', 'f10.44a', 'f10.35a', 'lv 10.05a']}
km = [('Cranbrook', 0.0), ('Wanklyn', 6.0), ('Wycliffe', 8.7), ('Marysville', 14.5), ('Chapman Camp', 17.2), ('Kimberley', 18.7)]
stops = [(n, cb['gid'] if n == 'Cranbrook' else 'KIM_' + n.upper().replace(' ', '_'), 0, m / 18.7, m) for n, m in km]
build('kim', 'Canadian Pacific', ['to Kimberley', 'to Cranbrook'], [leg], stops,
      [('M823', 'M823', 'CP_XSUN', 0, 'Mixed train, Cranbrook to Kimberley (daily except Sunday).'),
       ('M824', 'M824', 'CP_XSUN', 1, 'Mixed train, Kimberley to Cranbrook (daily except Sunday).')],
      principal={'Cranbrook', 'Kimberley', 'Marysville'})
NEW[-1]['segments'] = [dict(owner='none', a=0.0, b=round(shared_len, 1))]     # Cranbrook - junction is drawn by the cr line

# ---------------- Arrowhead (Table 161, rail part): Revelstoke - Greenslide - Wigwam - Sidmouth - Arrowhead; Brendan's trace
rv = st('cp', 'Revelstoke'); cpR = LineString([fwd(p[0], p[1]) for p in L['cp']['route']]); AR = BITS['Arrowhead']
if math.dist(fwd(*AR[0]), fwd(rv['lon'], rv['lat'])) > math.dist(fwd(*AR[-1]), fwd(rv['lon'], rv['lat'])): AR = AR[::-1]      # Revelstoke end first
r0, r1 = cpR.project(Point(fwd(rv['lon'], rv['lat']))), cpR.project(Point(fwd(*AR[0])))
leg_rv = ll(substring(cpR, r0, r1))                                        # Revelstoke station -> the branch switch, on the main line
rv_len = abs(r1 - r0)
print(f'  Arrowhead: switch {rv_len/MI:.2f} mi from Revelstoke station ({cpR.distance(Point(fwd(*AR[0]))):.0f} m off the main line); '
      f'Revelstoke - Arrowhead {(rv_len + LineString([fwd(*p) for p in AR]).length)/MI:.1f} mi (printed 27.4)')
TT = {'M802': ['lv 9.50a', 'f10.50a', 'f11.15a', '11.50a', 'ar 12.05p'], 'M801': ['ar 3.05p', 'f2.30p', 'f2.00p', '1.30p', 'lv 1.15p']}
ah = [('Greenslide', 151.7), ('Wigwam', 144.4), ('Sidmouth', 137.3), ('Arrowhead', 134.0)]
stops = [('Revelstoke', rv['gid'], 0, 0.0, 161.4)] + [(n, 'ARR_' + n.upper(), 1, max(0.0, ((161.4 - m) * MI - rv_len) / ((161.4 - 134.0) * MI - rv_len)), m) for n, m in ah]
build('arr', 'Canadian Pacific', ['to Arrowhead', 'to Revelstoke'], [leg_rv, AR], stops,
      [('M802', 'M802', 'CP_WS', 0, 'Mixed train, Revelstoke to Arrowhead (Wednesdays and Saturdays), connecting with the Canadian Pacific steamer down the Arrow Lakes to Nakusp (Table 161).'),
       ('M801', 'M801', 'CP_WS', 1, 'Mixed train, Arrowhead to Revelstoke (Wednesdays and Saturdays), connecting from the Canadian Pacific steamer up the Arrow Lakes from Nakusp (Table 161).')],
      principal={'Revelstoke', 'Arrowhead'})
NEW[-1]['segments'] = [dict(owner='none', a=0.0, b=round(rv_len, 1))]         # station - switch is drawn by the CP main line

# ---------------- Okanagan ownership (Brendan): CP Armstrong (wye) - Vernon on the CN Okanagan line; CN draws Vernon - Kelowna
cno = L['cno']; a_, v_ = st('cno', 'Armstrong')['chain'], st('cno', 'Vernon')['chain']
cno['segments'] = [s for s in cno.get('segments', []) if s['owner'] != 'cp'] + [dict(owner='cp', a=a_, b=v_)]
cps = L['cps']                                                             # CP's own Sicamous - Armstrong trace is drawn by the cps line

for n in NEW: n.pop('_R')
XL = []
for key, pts_ in EXTRA:               # plain track with no stations or trains
    r_ = []; acc_ = 0.0; prev_ = None
    for lon, lat in pts_:
        xy = fwd(lon, lat)
        if prev_: acc_ += math.dist(xy, prev_)
        prev_ = xy; r_.append([round(lon, 6), round(lat, 6), round(acc_, 1)])
    XL.append(dict(key=key, kind='p', label='Canadian Pacific', mainline=True, owner='cp', route=r_, stations=[], dirLabels=['', ''], segments=[], trips=[]))
vd['lines'] = [x for x in vd['lines'] if x['key'] not in {n['key'] for n in NEW + XL} | {'gf', 'ste'}] + NEW + XL
open(os.path.join(HERE, 'viz_data.json'), 'w').write(json.dumps(vd, separators=(',', ':')))

# ---------------- GTFS
def fmt(x): return f'{x // 3600:02d}:{x % 3600 // 60:02d}:{x % 60:02d}'
def app(name, rows_):
    with open(os.path.join(GT, name), 'a', newline='') as fh: csv.writer(fh).writerows(rows_)
app('calendar.txt', [['CP_TF', 0, 1, 0, 0, 1, 0, 0, '19490616', '19491231'], ['CP_WS', 0, 0, 1, 0, 0, 1, 0, '19490616', '19491231']])
gseen = set(r[0] for r in csv.reader(open(os.path.join(GT, 'stops.txt'))))
RID = {'nak': ('CPNK', 'CP Nakusp', 'Rosebery – Nakusp'), 'mer': ('CPMR', 'CP Merritt', "Brookmere – Merritt – Spence's Bridge"), 'slo': ('CPSL', 'CP Slocan', 'Nelson – South Slocan – Slocan City'),
       'kim': ('CPKM', 'CP Kimberley', 'Cranbrook – Kimberley'), 'arr': ('CPAR', 'CP Arrowhead', 'Revelstoke – Arrowhead')}
for n in NEW:
    rid, short, longn = RID[n['key']]; S = n['stations']; tot = n['route'][-1][2]
    app('routes.txt', [[rid, 'CP', short, longn, 2, '7A1E2C', 'FFFFFF', 'CP 1948.' + '']])
    app('stops.txt', list({s['gid']: [s['gid'], s['name'] + ' (CP)', f"{s['lat']:.6f}", f"{s['lon']:.6f}", s['note']] for s in S if s['gid'] not in gseen}.values())); gseen |= {s['gid'] for s in S}
    shp = []
    for sid, pts in ((n['key'].upper() + '_OUT', n['route']), (n['key'].upper() + '_IN', n['route'][::-1])):
        for k, p in enumerate(pts): shp.append([sid, f'{p[1]:.6f}', f'{p[0]:.6f}', k, f"{(p[2] if sid.endswith('OUT') else tot - p[2]):.1f}"])
    app('shapes.txt', shp)
    app('trips.txt', [[rid, t['svc'], t['id'], S[t['stops'][-1][0]]['name'], f"{t['num']} Mixed", t['dir'], n['key'].upper() + ('_OUT' if t['dir'] == 0 else '_IN')] for t in n['trips']])
    app('stop_times.txt', [[t['id'], fmt(a), fmt(b), S[i]['gid'], k, f"{(S[i]['chain'] if t['dir'] == 0 else tot - S[i]['chain']):.1f}", 1]
                           for t in n['trips'] for k, (i, a, b, tp) in enumerate(t['stops'], 1)])
with zipfile.ZipFile(os.path.join(HERE, 'bcer_fraser_valley_1949_gtfs.zip'), 'w', zipfile.ZIP_DEFLATED) as z:
    for fn in sorted(os.listdir(GT)): z.write(os.path.join(GT, fn), fn)
