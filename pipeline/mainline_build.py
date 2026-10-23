"""CN (April 1949) and CP (1948) trains on the NRWN-derived routes. Run after gn_build.py.
Adds lines cn, cp, cpm, cpw to viz_data.json and appends to the GTFS feed."""
import csv, json, math, os, pickle, re, zipfile
import numpy as np
from pyproj import Transformer
from shapely.geometry import LineString, Point
HERE = os.path.dirname(os.path.abspath(__file__)); GT = os.path.join(HERE, 'gtfs')
inv = Transformer.from_crs(26910, 4326, always_xy=True).transform
fwd = Transformer.from_crs(4326, 26910, always_xy=True).transform
MI = 1609.344
R = pickle.load(open(os.path.join(HERE, 'nrwn_routes.pkl'), 'rb'))
meta = json.load(open(os.path.join(HERE, 'nrwn_routes.json')))
# ---- Alberta: the main lines carried on from the B.C. boundary, over the Alberta file of the national network (nrwn/alberta.json, cut by
# nrwn/extract_alberta.py). CP: the Great Divide (Stephen) - Lake Louise - Banff - Calgary. CN: Yellowhead - Jasper - Edson - Edmonton, into the CN
# station by Brendan's trace of the old downtown loop (traces/edmonton_terminal.kml).
from nrwn_graph import Net
_inv = Transformer.from_crs(26910, 4326, always_xy=True).transform
import xml.etree.ElementTree as _ET
_loop = [tuple(map(float, t.split(',')[:2])) for t in next(_ET.parse(os.path.join(HERE, 'traces', 'edmonton_terminal.kml')).iter('{http://www.opengis.net/kml/2.2}coordinates')).text.split()]
_ab = Net([f for f in json.load(open(os.path.join(HERE, 'nrwn', 'alberta.json'))) if f['schema'].endswith('Track')]
          + [dict(schema='#kml_schema_ft_Track', data={'trackClassification': 'Main'}, coords=[_loop])])
EDSON, EDMONTON = (-116.430566, 53.579558), (-113.4917, 53.5470)      # the Edson station point in the network; the CN station, Edmonton
LAKE_LOUISE, BANFF, CALGARY, JASPER = (-116.1814, 51.4259), (-115.5756, 51.1811), (-114.0631, 51.0443), (-118.0796, 52.8762)   # the stations
BC_END = {k: R[k].length for k in ('CP', 'CN')}                    # where each route crossed the boundary, before the Alberta track is joined on
for _k, _via in (('CP', (LAKE_LOUISE, BANFF, CALGARY)), ('CN', (JASPER, EDSON, EDMONTON))):
    _t, _sn = _ab.route(_inv(*R[_k].coords[-1]), *_via)
    print(f'Alberta {_k}: joins {Point(R[_k].coords[-1]).distance(Point(_t.coords[0])):.0f} m from the end of the B.C. route, {_t.length / MI:.1f} mi, snaps {[round(x) for x in _sn]}')
    R[_k] = LineString(list(R[_k].coords) + list(_t.coords)[1:])

# ---- Alberta, east to the Saskatchewan boundary (October 2026): CN Edmonton - Wainwright - Chauvin (Table 75 of the May 1948 Official Guide,
# ab_cn_t075.csv) and CP Calgary - Medicine Hat - Walsh (Table 6, ab_cp_t006.csv). Track and station positions by ab_lines.py over the whole
# Alberta file (nrwn/alberta_all.json); the stations' places from the federal names file. Trains end at their last timed station in Alberta.
import ab_lines, ab_table
AB_E, EAST_CH, EAST_ROWS = {}, {}, {}
for _k, _spec in (('CN', dict(key='cn', rail='cn', legs=[dict(csv='ab_cn_t075.csv', a='Edmonton', b='Chauvin')], cols=None, places={'Edmonton': EDMONTON})),
                  ('CP', dict(key='cp', rail='cp', legs=[dict(csv='ab_cp_t143s.csv', a='Calgary', b='Gleichen'), dict(csv='ab_cp_t006.csv', a='Gleichen', b='Walsh')],
                              cols=None, places={'Calgary': CALGARY}, noplace=['Redcliff']))):   # Redcliff: a plain main-line row in Table 6 (the town point is 700 m off the line)     # the main line by Strathmore (Nos. 1 to 4; Brendan's trace, October 2026)
    _rows, _tr, _pieces = ab_lines.trace(_spec); ab_lines.report(dict(key=_k + ' east'), _rows, _pieces)
    _east = [q for _i, _p in enumerate(_pieces) for q in (_p['coords'] if _i == 0 else _p['coords'][1:])]
    AB_E[_k] = R[_k].length + math.dist(R[_k].coords[-1], _east[0])
    print(f'Alberta east {_k}: joins {math.dist(R[_k].coords[-1], _east[0]):.0f} m from the end of the route')
    EAST_CH[_k] = {r['name']: AB_E[_k] + r['d'] for r in _rows[1:]}
    EAST_ROWS[_k] = ab_table.load(os.path.join(HERE, _spec['legs'][-1]['csv']))      # the main table (CP: Table 6; the Strathmore file adds its calls below)
    R[_k] = LineString(list(R[_k].coords) + _east)
# Nos. 7 and 8 ran by Carseland (Strangmuir, Carseland, Dalemead, Indus): Shepard - Gleichen by that line, for a line of their own ('cpc')
_cr, _ct, _cpcs = ab_lines.trace(dict(key='cpc', rail='cp', legs=[dict(csv='ab_cp_t006.csv', a='Shepard', b='Gleichen')], cols=None, places={})); ab_lines.report(dict(key='CP by Carseland'), _cr, _cpcs)
CARSE = [q for _i, _p in enumerate(_cpcs) for q in (_p['coords'] if _i == 0 else _p['coords'][1:])]
CARSE_D = {r['name']: r['d'] for r in _cr}
P2 = lambda txt: ab_table.shift_text(txt)                              # Mountain time as printed -> Pacific, like the rest of the tables here

# ---- milepost functions (re-derived from marker posts, same method as nrwn_build.py)
F = json.load(open(os.path.join(HERE, 'nrwn', 'region.json')))
_seen = {f['data'].get('NID') for f in F}
for _extra in ('okanagan.json', 'cnmain.json', 'cpmain.json'):
    _new = [f for f in json.load(open(os.path.join(HERE, 'nrwn', _extra))) if f['data'].get('NID') not in _seen]
    _seen |= {f['data'].get('NID') for f in _new}; F += _new
markers = [f for f in F if f['schema'] == '#kml_schema_ft_MarkerPost']
def mp_fn(route, sub, lo=0):
    pairs = sorted((float(f['data']['subdivision1Distance']), route.project(Point(fwd(*f['coords'][0][0]))))
                   for f in markers if f['data'].get('subdivision1Name') == sub
                   and route.distance(Point(fwd(*f['coords'][0][0]))) < 60
                   and route.project(Point(fwd(*f['coords'][0][0]))) >= lo)
    ms, cs = zip(*pairs); sign = 1 if np.polyfit(ms, cs, 1)[0] > 0 else -1
    keep = [pairs[0]]
    for m_, c in pairs[1:]:
        if (c - keep[-1][1]) * sign > 0: keep.append((m_, c))
    ms, cs = map(np.array, zip(*keep))
    def f(m):
        if m < ms.min(): return float(cs[0] + (m - ms[0]) * sign * MI)
        if m > ms.max(): return float(cs[-1] + (m - ms[-1]) * sign * MI)
        return float(np.interp(m, ms, cs))
    return f
cascade = mp_fn(R['CP'], 'Cascade')
yale = mp_fn(R['CN'], 'Yale', lo=meta['cn_shared'][1])
mission = mp_fn(R['CPM'], 'Mission', lo=meta['cpm_junction'])
ashcroft = mp_fn(R['CN'], 'Ashcroft', lo=meta['cn_shared'][1])      # CN above Boston Bar: Ashcroft sub mp = CN mile - 2672.5
thompson = mp_fn(R['CP'], 'Thompson')
okanagan = mp_fn(R['CNO'], 'Okanagan')                               # CN Okanagan sub mileposts = Table 306 miles                                # CP above North Bend: Thompson sub mp = CP mile - 2631.8
GN = LineString([fwd(*q) for q in json.load(open(os.path.join(HERE, 'gn_geometry.json')))['route']])
spur_len, shared_end = meta['cn_shared']; j = 13.61 * MI - (shared_end - spur_len)

# ---- time parsing
def times(txt):
    """'ar 5.30p / lv 5.40p' -> (arr, dep) in seconds (None where absent); '(prev day)'/'(next day)' parts dropped"""
    parts = [p.strip() for p in txt.split('/')]
    arr = dep = None
    for p in parts:
        if 'prev day' in p or 'next day' in p: continue
        m = re.search(r'(ar|lv)?\s*[a-z]?(\d+)\.(\d+)([ap])', p)
        if not m: continue
        h, mn = int(m.group(2)), int(m.group(3))
        if m.group(4) == 'p' and h != 12: h += 12
        if m.group(4) == 'a' and h == 12: h = 0
        t = h * 3600 + mn * 60
        if m.group(1) == 'ar': arr = t
        elif m.group(1) == 'lv': dep = t
        else: arr = dep = t
    if arr is None: arr = dep
    if dep is None: dep = arr
    return arr, dep

def monotonic(stops):
    base, prev = 0, -1
    for s in stops:
        for k in (1, 2):
            if s[k] + base < prev - 6 * 3600: base += 86400
            s[k] += base; prev = s[k]
    return stops

lines = {}
def line(key, label, kind, owner, route, dir_labels, segments=()):
    lines[key] = dict(key=key, kind=kind, label=label, mainline=True, owner=owner, route=route, stations=[], trips=[],
                      segments=list(segments), dirLabels=dir_labels, _idx={})
    return lines[key]
def station(L, name, chain, mile, gid, principal=False, note=''):
    if name in L['_idx']: return L['_idx'][name]
    L['_idx'][name] = len(L['stations'])
    L['stations'].append(dict(name=name, chain=chain, mile=mile, gid=gid, principal=principal, note=note))
    return L['_idx'][name]

PRINCIPAL = {'Vancouver', 'New Westminster', 'Mission', 'Agassiz', 'North Bend', 'Boston Bar', 'Hope', 'Chilliwack',
             'Coquitlam', 'Huntingdon', 'Port Mann', 'Fort Langley', 'Yale', 'Odlum', 'Matsqui', 'Lytton', 'Field', 'Golden', 'Glacier', 'Revelstoke', 'Sicamous', 'Salmon Arm', 'Chase', 'Stephen', "Spence's Bridge", 'Kamloops Jct', 'Kamloops', 'Vernon', 'Armstrong', 'Falkland', 'Lumby Jct', 'Kelowna', 'Oyama', 'Ashcroft', 'Tranquille', 'Blue River',
             'Wainwright', 'Tofield', 'Chauvin', 'Medicine Hat', 'Bassano', 'Brooks', 'Gleichen', 'Walsh', 'Red Pass Jct', 'Yellowhead', 'Mount Robson', 'Jasper', 'Edson', 'Edmonton', 'Calgary', 'Banff', 'Lake Louise', 'Valemount', 'Clearwater', 'Barriere', 'Avola', 'Birch Island'}

def extend_to(L, t, term):
    """A through train with no printed time at the edge of the map: carry it to the edge at the speed of its nearest
    timed run. The added stop is marked tp=0 and shows as (est.) in the panel."""
    ti = L['_idx'][term]; ch = L['stations'][ti]['chain']; S = t['stops']
    if any(s[0] == ti for s in S): return
    far = lambda s: L['stations'][s[0]]['chain']
    if abs(ch - far(S[-1])) < abs(ch - far(S[0])):   # the edge lies ahead of the last stop: it comes last
        a, b = S[-2], S[-1]; v = abs(far(b) - far(a)) / max(b[1] - a[2], 60)
        x = b[2] + round(abs(ch - far(b)) / v / 60) * 60; S.append([ti, x, x, 0])
    else:
        a, b = S[0], S[1]; v = abs(far(b) - far(a)) / max(b[1] - a[2], 60)
        x = a[1] - round(abs(ch - far(a)) / v / 60) * 60; S.insert(0, [ti, x, x, 0])
        if x < 0:
            for s in S: s[1] += 86400; s[2] += 86400

def all_times(txt):
    """'ar 4.15p (prev day) / lv 6.45a' -> {'ar': 58500, 'lv': 24300}"""
    out = {}
    for m in re.finditer(r'(ar|lv)\s*(\d+)\.(\d+)([ap])', txt):
        h, mn = int(m.group(2)), int(m.group(3))
        if m.group(4) == 'p' and h != 12: h += 12
        if m.group(4) == 'a' and h == 12: h = 0
        out[m.group(1)] = h * 3600 + mn * 60
    return out

# ================= CN main: Vancouver - Kamloops Jct (Table 24) - Blue River - Red Pass Jct - Yellowhead (Table 23)
clearwater = mp_fn(R['CN'], 'Clearwater', lo=meta['cn_shared'][1])    # Clearwater sub mp = Table 23 mile - 2527.5 (0 at Blue River)
albreda = mp_fn(R['CN'], 'Albreda', lo=meta['cn_shared'][1])          # Albreda sub mp = Table 23 mile - 2395.2 (0 at Jasper)
KJ_PT = Point(fwd(-120.3484611, 50.718257))                           # NRWN Kamloops Jct station
cn = line('cn', 'Canadian National', 'q', 'cn', R['CN'], ['to Kamloops, Jasper, Edmonton and Wainwright', 'to Vancouver'],
          [dict(owner='none', a=spur_len, b=shared_end)])
t24 = list(csv.DictReader(open(os.path.join(HERE, 'cn_1949_04.csv'))))
t23 = list(csv.DictReader(l for l in open(os.path.join(HERE, 'cn_1949_table23.csv')) if not l.startswith('#')))
t23 += list(csv.DictReader(l for l in open(os.path.join(HERE, 'cn_1948_alberta.csv')) if not l.startswith('#')))   # Edmonton - Jasper (Official Guide, May 1948)
# east of Edmonton (Table 75): the Alberta rows; Nos. 1 to 4 keep the Edmonton entry they have, Nos. 11 and 12 take theirs from Table 75
for r in EAST_ROWS['CN']['rows']:
    cells = {c: P2(r.get(c, '')) for c in ('No1', 'No2', 'No3', 'No4', 'No11', 'No12')}
    if r['station'] == 'Edmonton': next(x for x in t23 if x['station'] == 'Edmonton').update(No11=cells['No11'], No12=cells['No12'])
    else: t23.append({'station': r['station'], 'mile': str(r['mile']), **cells})
for r in t23: r['mile'] = f"{float(r['mile']) + 6.0:.1f}"           # onto the Table 24 scale (through trains' Kamloops detour)
def cn_chain(name, mile):
    if name == 'Vancouver': return 0.0
    if name in EAST_CH['CN']: return EAST_CH['CN'][name]              # east of Edmonton
    if name == 'New Westminster': return spur_len + (13.0 * MI - j)
    if name == 'Kamloops Jct': return R['CN'].project(KJ_PT)
    if mile >= 2798.5: return yale(mile - 2798.5)
    if mile > 2672.9: return ashcroft(mile - 2672.5)
    m23 = mile - 6.0
    if m23 < 2412.7: return float(np.interp(m23, [2159.4, 2289.0, 2395.2, 2412.7], [AB_E['CN'], R['CN'].project(Point(fwd(*EDSON))), R['CN'].project(Point(fwd(*JASPER))),
                                                                                    min(BC_END['CN'], albreda(2412.7 - 2395.2))]))   # Edmonton - Edson - Jasper - Yellowhead, in Alberta
    return clearwater(m23 - 2527.5) if m23 >= 2527.5 else albreda(m23 - 2395.2)
for r in sorted(t24 + t23, key=lambda r: float(r['mile'])):
    if r['station'] in cn['_idx']: continue
    gid = 'GN_NEW_WESTMINSTER' if r['station'] == 'New Westminster' else 'CN_' + r['station'].upper().replace(' ', '_')
    station(cn, r['station'], cn_chain(r['station'], float(r['mile'])), float(r['mile']), gid,
            r['station'] in PRINCIPAL, 'Canadian National station' + (' (shared with the Great Northern)' if r['station'] == 'New Westminster' else ''))
LIMITED = 'The Continental Limited'
CN_TRAINS = [  # (columns in Table 24 / Table 23, number, name, service, dir, note)  dir 0 = away from Vancouver
    (('No1_wb', 'No1'), '1', LIMITED, 'CN_DAILY', 1, 'From Montreal and Toronto (shown from Wainwright, its last timed station in Alberta).'),
    (('No3_wb', 'No3'), '3', '', 'CN_DAILY', 1, 'From the east (shown from Wainwright, its last timed station in Alberta). Runs into Kamloops and back while at Kamloops Jct.'),
    (('No2_eb', 'No2'), '2', LIMITED, 'CN_DAILY', 0, 'To Toronto and Montreal (shown as far as Wainwright, its last timed station in Alberta).'),
    (('No4_eb', 'No4'), '4', '', 'CN_DAILY', 0, 'To the east (shown as far as Wainwright, its last timed station in Alberta).'),
    (('M395_wb',), 'M395', 'Mixed', 'CN_TF', 1, 'Mixed train, Kamloops (7.45 a.m.) to Boston Bar; lies over and goes on to Vancouver next day as M397.'),
    (('M397_wb',), 'M397', 'Mixed', 'CN_WS', 1, 'Mixed train, Boston Bar to Vancouver.'),
    (('M398_eb',), 'M398', 'Mixed', 'CN_TF', 0, 'Mixed train, Vancouver to Boston Bar; lies over and goes on next day as M396.'),
    (('M396_eb',), 'M396', 'Mixed', 'CN_WS', 0, 'Mixed train, Boston Bar to Kamloops (3.15 p.m.).'),
    (('M391',), 'M391', 'Mixed', 'CN_TF', 1, 'Mixed train, Jasper to Blue River.'),
    (('M393',), 'M393', 'Mixed', 'CN_TTS', 1, 'Mixed train, Blue River to Kamloops (3.15 p.m.).'),
    (('M394',), 'M394', 'Mixed', 'CN_MWF', 0, 'Mixed train, Kamloops (7.45 a.m.) to Blue River.'),
    (('M392',), 'M392', 'Mixed', 'CN_WS', 0, 'Mixed train, Blue River to Jasper.'),
    (('No189',), '189', '', 'CN_SUTT', 1, 'Local train, Edmonton to Jasper: Sundays, Tuesdays and Thursdays.'),
    (('No190',), '190', '', 'CN_MWF', 0, 'Local train, Jasper to Edmonton: Mondays, Wednesdays and Fridays.'),
    (('No11',), '11', '', 'CN_XSUN', 1, 'Local train from Winnipeg and Saskatoon, calling at every station; shown from Chauvin, the first station in Alberta. Daily except Sunday.'),
    (('No12',), '12', '', 'CN_XSUN', 0, 'Local train to Saskatoon and Winnipeg, calling at every station; shown as far as Chauvin, the last station in Alberta. Daily except Sunday.')]
for cols, num, name, svc, d, note in CN_TRAINS:
    cells = {}
    for r in t24 + t23:
        for c in cols:
            if r.get(c) and re.search(r'\d', r[c]):
                prev = cells.get(r['station'])
                if prev:                                   # a station in both tables (Kamloops Jct): keep the fuller entry
                    if len(r[c]) <= len(prev[1]): continue
                cells[r['station']] = (float(r['mile']), r[c])
    rs = sorted(cells.items(), key=lambda kv: kv[1][0], reverse=(d == 0))
    stops = [[cn['_idx'][n], *times(txt), 1] for n, (m, txt) in rs]
    cn['trips'].append(dict(id='CN-' + num, num=num, name=name, svc=svc, dir=d, stops=monotonic(stops), note=note))
# CN dir: 0 = away from Vancouver (increasing chain)

# ================= CN Okanagan line (Table 306): Kamloops Jct - Vernon - Lumby Jct (NRWN) - Kelowna (Brendan's tracing)
cno = line('cno', 'Canadian National', 'q', 'cn', R['CNO'], ['to Vernon and Kelowna', 'to Kamloops'])
t306 = list(csv.DictReader(l for l in open(os.path.join(HERE, 'cn_1949_table306.csv')) if not l.startswith('#')))
LJ_CH = okanagan(87.6)                                                 # Lumby Jct; beyond it stations sit at printed mileage along the tracing
def cno_chain(mile):
    if mile == 0.0: return 0.0
    if mile <= 87.6: return okanagan(mile)
    return LJ_CH + (mile - 87.6) / (118.9 - 87.6) * (R['CNO'].length - LJ_CH)
for r in t306:
    gid = 'CN_' + r['station'].upper().replace(' ', '_').replace("'", '')
    station(cno, r['station'], cno_chain(float(r['mile'])), float(r['mile']), gid, r['station'] in PRINCIPAL,
            'Canadian National station' + (' (junction with the main line)' if r['station'] == 'Kamloops Jct' else ''))
for col, num, d, note in (('No194', '194', 0, 'Okanagan train, Kamloops Jct to Kelowna, connecting with No. 2 from Vancouver. Buses on to Penticton (not shown).'),
                          ('No193', '193', 1, 'Okanagan train, Kelowna to Kamloops Jct, connecting with No. 3 for Vancouver.')):
    rs = sorted((r for r in t306 if r[col]), key=lambda r: float(r['mile']), reverse=(d == 1))
    stops = [[cno['_idx'][r['station']], *times(r[col]), 1] for r in rs]
    cno['trips'].append(dict(id='CN-' + num, num=num, name='Okanagan', svc='CN_XSUN', dir=d, stops=monotonic(stops), note=note))
    extend_to(cno, cno['trips'][-1], 'Kamloops Jct')
# mixed trains that start or end at Kamloops town run the 3 miles to or from Kamloops Jct on the Okanagan line
for num, svc, d, t0, t1 in (('M393', 'CN_TTS', 0, '2.50p', '3.15p'), ('M396', 'CN_WS', 0, '2.50p', '3.15p'),
                            ('M395', 'CN_TF', 1, '7.45a', '8.10a'), ('M394', 'CN_MWF', 1, '7.45a', '8.15a')):
    a_, b_ = (('Kamloops Jct', 'Kamloops') if d == 0 else ('Kamloops', 'Kamloops Jct'))
    ta, tb = times(t0)[0], times(t1)[0]
    cno['trips'].append(dict(id=f'CN-{num}-K', num=num, name='Mixed', svc=svc, dir=d, note='Mixed train, between Kamloops town and Kamloops Jct.',
                             stops=[[cno['_idx'][a_], ta, ta, 1], [cno['_idx'][b_], tb, tb, 1]]))

# ================= CP main, Mission branch, Westminster branch
cp = line('cp', 'Canadian Pacific', 'p', 'cp', R['CP'], ['to Kamloops, Revelstoke, Banff, Calgary and Medicine Hat', 'to Vancouver'])
cpm = line('cpm', 'Canadian Pacific', 'p', 'cp', R['CPM'], ['to Mission and Huntingdon', 'to Vancouver'],
           [dict(owner='none', a=0, b=meta['cpm_junction'])])
cpw = line('cpw', 'Canadian Pacific', 'p', 'cp', R['CPW'], ['to New Westminster', 'to Coquitlam'])
t7 = [r for r in csv.DictReader(l for l in open(os.path.join(HERE, 'cp_1948_table7.csv')) if not l.startswith('#'))]
# east of Calgary (Table 6): one row for each call, like the rest of the table; at Calgary the arrival (or departure) is joined to the entry already there
_who = {r['train']: r for r in t7}
_STR = ab_table.load(os.path.join(HERE, 'ab_cp_t143s.csv'))
for _t in EAST_ROWS['CP']['trains']:
    num = _t['num']; dirn = 'west' if _t['dir'] == 'down' else 'east'
    _rows = EAST_ROWS['CP']['rows']
    if num not in ('7', '8', '13', '14'):                                   # by Strathmore: Table 143's calls between Calgary and Gleichen
        _rows = [r for r in _rows if r['mile'] <= 2189.1 or r['station'] == 'Calgary'] + \
                [dict(r, **({_t['col']: r.get(_t['col'], '')} if _t['col'] in r else {_t['col']: ''})) for r in _STR['rows'] if r['station'] not in ('Calgary', 'Gleichen')]
    for r in _rows:
        txt = P2(r.get(_t['col'], ''))
        if not re.search(r'\d', txt): continue
        if num == '2':                                                    # No. 2 lies at Calgary overnight (in from the west 12.35 p.m., out 7.00 next morning): east of Calgary it is a train of its own
            t7.append(dict(direction=dirn, train='2E', name='', days='Daily', station=r['station'], mile=str(r['mile']), time=txt, flag=''))
        elif r['station'] == 'Calgary':
            old = next(x for x in t7 if x['train'] == num and x['station'] == 'Calgary')
            old['time'] = f"{txt} / {old['time']}" if dirn == 'west' else f"{old['time']} / {txt}"
        else: t7.append(dict(direction=dirn, train=num, name=_who[num]['name'], days=_who[num]['days'], station=r['station'], mile=str(r['mile']), time=txt, flag='',
                             **({'carse': 1} if num in ('7', '8', '13', '14') and 2189.1 < r['mile'] < 2240.1 else {})))
tb = [r for r in csv.DictReader(l for l in open(os.path.join(HERE, 'cp_1948_branches.csv')) if not l.startswith('#'))]
ODLUM = Point(fwd(-(121 + 29/60 + 4/3600), 49 + 22/60 + 59/3600))      # Odlum, north side of the river (Brendan)
def cp_station(L, name, mile):
    if name in EAST_CH['CP'] and mile <= 2189.1: mile = round(mile - 4.5, 1)   # east of Gleichen, Table 6's miles are by Carseland: the main line goes by Strathmore, 4.5 mi longer
    ch = EAST_CH['CP'][name] if name in EAST_CH['CP'] else R['CP'].project(ODLUM) if name == 'Odlum' else cascade(mile - 2752.7) if mile >= 2752.7 else thompson(mile - 2631.8) if mile >= 2631.2 else cp_east(mile)
    return station(L, name, ch, mile, 'CP_' + name.upper().replace(' ', '_'), name in PRINCIPAL, 'Canadian Pacific station')
# east of Kamloops the NRWN has no mileposts: pin stations to the subdivision changes (Kamloops, Revelstoke, Field) and the Great Divide
_cs = meta['cp_subs']
_am = [2240.1, 2322.0, 2356.7, 2362.3, 2376.7, 2502.4, 2631.2]          # Calgary, Banff, Lake Louise, Stephen (the Great Divide), Field, Revelstoke, Kamloops
_ac = [AB_E['CP'], R['CP'].project(Point(fwd(*BANFF))), R['CP'].project(Point(fwd(*LAKE_LOUISE))), BC_END['CP'], _cs['Laggan'], _cs['Mountain'], thompson(2631.2 - 2631.8)]
def cp_east(mile): return float(np.interp(mile, _am, _ac))
SVC = {'Daily': 'CP_DAILY', 'Except Sunday': 'CP_XSUN'}
KV = {'11', '45', 'KVX', '12', '46'}
by_train = {}
for r in t7: by_train.setdefault((r['train'], r['direction']), []).append(r)
for r in sorted((r for r in t7 if r['train'] not in ('M809', 'M810') and not r['station'].startswith('Hope (KV)') and not r.get('carse')), key=lambda r: -float(r['mile'])):
    cp_station(cp, r['station'], float(r['mile']))                   # every station first, in order along the line
# Nos. 7 and 8: their own line, the main line's track (drawn by the cp line) but by Carseland between Shepard and Gleichen
from shapely.ops import substring as _sub
_sh, _gl = EAST_CH['CP']['Shepard'], EAST_CH['CP']['Gleichen']
_cl = LineString(CARSE)
_c_gl = _sh + _cl.length                                                 # chain of Gleichen on cpc (Carseland trace from Shepard to Gleichen)
_cpc_route = LineString(list(_sub(R['CP'], 0, _sh).coords) + CARSE[1:] + list(_sub(R['CP'], _gl, R['CP'].length).coords)[1:])
cpc = line('cpc', 'Canadian Pacific', 'p', 'cp', _cpc_route, ['to Calgary, Carseland and Medicine Hat', 'to Vancouver'],
           [dict(owner='none', a=0, b=_sh), dict(owner='none', a=_c_gl, b=_cpc_route.length)])
def cpc_station(name, mile):
    if name in CARSE_D and name not in ('Shepard', 'Gleichen'):
        ch = _sh + CARSE_D[name] - CARSE_D['Shepard']
    else:
        i = cp_station(cp, name, mile); ch = cp['stations'][i]['chain']
        if ch >= _gl - 1: ch = ch - _gl + _c_gl                            # east of Gleichen: the printed (Carseland) miles
        else: mile = cp['stations'][i]['mile']
    return station(cpc, name, ch, mile, 'CP_' + name.upper().replace(' ', '_'), name in PRINCIPAL, 'Canadian Pacific station' + (', on the line by Carseland' if name in ('Strangmuir', 'Carseland', 'Dalemead', 'Indus') else ''))
for (num, dirn), rs in by_train.items():
    rs = [r for r in rs if not r['station'].startswith('Hope (KV)')]
    if num in ('M809', 'M810'): continue                                  # built on the Mission branch route below
    d = 0 if dirn == 'east' else 1
    rs.sort(key=lambda r: float(r['mile']), reverse=(d == 0))
    LL = cpc if num in ('7', '8', '13', '14') else cp
    stops = [[(cpc_station if LL is cpc else (lambda n, m: cp_station(cp, n, m)))(r['station'], float(r['mile'])), *times(r['time']), 1] for r in rs]
    num2 = '12' if num == 'KVX' else num
    shown = '2' if num == '2E' else num2
    name = rs[0]['name'] or ''
    note = ('Kettle Valley train between Odlum and Vancouver; it continues over the Kettle Valley line (Hope, Brookmere, Penticton, Nelson).'
            if num in KV else ('To Banff, Calgary and Medicine Hat, and on to the east (shown as far as its last timed station in Alberta).' if d == 0 else 'From the east (shown from its first timed station in Alberta), Medicine Hat, Calgary and Banff.')
            + (' Between Gleichen and Shepard it ran by Strathmore, a line since lifted (Brendan\'s trace).' if num in ('1', '2E', '3', '4') else
               ' Between Shepard and Gleichen it ran by Carseland.' if num in ('7', '8') else
               ' Between Shepard and Gleichen it is shown by Carseland (Brendan\'s best guess; it has no calls between Calgary and Medicine Hat).' if num in ('13', '14') else '')
            + (' Summer train (No. 13 from Chicago June 29 to Sept. 3; No. 14 from Vancouver July 2 to Sept. 1).' if num in ('13', '14') else ''))
    if num == '2E': note = 'No. 2 east of Calgary: it comes in from Vancouver at 12.35 p.m. (Mountain time), lies over, and leaves at 7.00 next morning for Medicine Hat and the east (shown as far as Walsh, its last timed station in Alberta).' + note[note.index(' Between'):]
    if num == '2': note = 'From Vancouver to Calgary, where it lies overnight; it goes on east at 7.00 next morning (shown as a second No. 2).'
    LL['trips'].append(dict(id='CP-' + num2, num=shown, name=name, svc=SVC[rs[0]['days']], dir=d, stops=monotonic(stops), note=note))
# Mission branch mixed trains: Vancouver - Mission (Table 7) + Mission - Huntingdon (Table 162)
for num, d in (('M810', 0), ('M809', 1)):
    main = [r for r in t7 if r['train'] == num]
    br = [r for r in tb if r['train'] == num and r['table'] == '162']
    MISSION_STN = Point(fwd(-122.3098, 49.1335))                    # CP Mission station on the main line
    ABBY_STN = Point(fwd(-122.2890, 49.0504))                        # NRWN CP station point (Mission sub 6.47), beside the BCER station
    def cpm_station(r, branch):
        if r['station'] == 'Mission':                                   # trains use the west leg: stop on it, 'close enough' to the station
            return station(cpm, 'Mission', R['CPM'].project(MISSION_STN), 2840.0, 'CP_MISSION', True, 'Canadian Pacific station')
        if branch and r['station'] == 'Abbotsford':
            return station(cpm, 'Abbotsford', R['CPM'].project(ABBY_STN), 2846.7, 'CPM_ABBOTSFORD', True, 'Canadian Pacific, Mission branch')
        if branch and r['station'] != 'Mission':
            mp = float(r['mile']); return station(cpm, r['station'], mission(mp), 2840.0 + mp, 'CPM_' + r['station'].upper(), r['station'] in PRINCIPAL, 'Canadian Pacific, Mission branch')
        mile = float(r['mile']) if not branch else 2840.0
        return station(cpm, r['station'], cascade(mile - 2752.7), mile, 'CP_' + r['station'].upper().replace(' ', '_'), r['station'] in PRINCIPAL, 'Canadian Pacific station')
    seq = []
    if d == 0:
        for r in sorted(main, key=lambda r: -float(r['mile'])):
            if r['station'] != 'Mission': seq.append((r, False))
        for r in sorted(br, key=lambda r: float(r['mile'])): seq.append((r, True))
    else:
        for r in sorted(br, key=lambda r: -float(r['mile'])): seq.append((r, True))
        for r in sorted(main, key=lambda r: float(r['mile'])):
            if r['station'] != 'Mission': seq.append((r, False))
    stops = [[cpm_station(r, b), *times(r['time']), 1] for r, b in seq]
    cpm['trips'].append(dict(id='CP-' + num, num=num, name='Mixed', svc='CP_XSUN', dir=d, stops=monotonic(stops),
                             note='Vancouver–Mission–Huntingdon mixed train (Tables 7 and 162), crossing the Fraser on the Mission bridge.'))
# Westminster branch (Table 163)
from shapely.ops import substring
CPNW = Point(fwd(-(122 + 54/60 + 42.03/3600), 49 + 12/60 + 2.89/3600))   # CP New Westminster station (still standing)
R['CPW'] = CPW = substring(R['CPW'], 0, R['CPW'].project(CPNW))       # branch ends at the station
cpw['route'] = CPW
L163 = CPW
for num in ('M814', 'M816', 'M813', 'M815'):
    rs = [r for r in tb if r['table'] == '163' and r['train'] == num]
    d = 0 if rs[0]['direction'] == 'south' else 1
    rs.sort(key=lambda r: float(r['mile']), reverse=(d == 1))
    stops = []
    for r in rs:
        mp = float(r['mile'])
        gid = 'CP_COQUITLAM' if r['station'] == 'Coquitlam' else 'CPW_' + r['station'].upper().replace(' ', '_')
        si = station(cpw, r['station'], mp / 8.4 * CPW.length, 2865.2 + mp, gid, r['station'] in PRINCIPAL, 'Canadian Pacific, New Westminster branch')
        stops.append([si, *times(r['time']), 1])
    cpw['trips'].append(dict(id='CP-' + num, num=num, name='Mixed', svc='CP_DAILY', dir=d, stops=monotonic(stops),
                             note='Coquitlam–New Westminster mixed train (Table 163), connecting with main line trains at Coquitlam.'))

# ---- sanity: implied speeds
for L in lines.values():
    for t in L['trips']:
        bad = []
        for (a, _, da, _), (b, tb_, _, _) in zip(t['stops'], t['stops'][1:]):
            dist = abs(L['stations'][b]['chain'] - L['stations'][a]['chain']) / MI; mins = (tb_ - da) / 60
            if mins <= 0 or dist / (mins / 60) > 60: bad.append(f"{L['stations'][a]['name']}->{L['stations'][b]['name']} {dist:.1f}mi/{mins:.0f}min")
        print(f"{L['key']:4s} {t['id']:8s} {t['name'][:22]:22s} {len(t['stops']):2d} stops {'!! ' + '; '.join(bad) if bad else ''}")

# ---- viz
vd = json.load(open(os.path.join(HERE, 'viz_data.json')))
# what the train panel gives as the source (Brendan: standardise on the 1948 Official Guide where its schedule is the same)
SRC = {'cn': 'Canadian National, schedule of April 25, 1948 (Official Guide, May 1948), with the stations between its entries from the 1949 folder, where every time the Guide prints is the same'}
out = []
for L in lines.values():
    Rt = L['route']; route = []; acc = 0; prev = None
    for xy in Rt.simplify(1.0).coords:
        if prev: acc += ((xy[0]-prev[0])**2 + (xy[1]-prev[1])**2) ** .5
        prev = xy; lon, lat = inv(*xy); route.append([round(lon, 6), round(lat, 6), round(acc, 1)])
    sc = acc / Rt.length
    st = []
    for s in L['stations']:
        lon, lat = inv(*Rt.interpolate(s['chain']).coords[0])
        st.append(dict(name=s['name'], chain=round(s['chain'] * sc, 1), lon=round(lon, 6), lat=round(lat, 6), mile=s['mile'],
                       principal=s['principal'], note=s['note'], kml='', gid=s['gid']))
    out.append(dict(key=L['key'], kind=L['kind'], label=L['label'], mainline=True, owner=L['owner'], route=route, stations=st,
                    dirLabels=L['dirLabels'], segments=[dict(owner=g['owner'], a=round(g['a'] * sc, 1), b=round(g['b'] * sc, 1)) for g in L['segments']],
                    **({'src': SRC[L['key']]} if L['key'] in SRC else {}),
                    trips=[dict(id=t['id'], num=t['num'], name=t['name'], svc=t['svc'], dir=t['dir'], stops=t['stops'], note=t['note']) for t in L['trips']]))
vd['lines'] = [x for x in vd['lines'] if x['key'] not in lines] + out
open(os.path.join(HERE, 'viz_data.json'), 'w').write(json.dumps(vd, separators=(',', ':')))

# ---- GTFS
def fmt(x): return f'{x // 3600:02d}:{x % 3600 // 60:02d}:{x % 60:02d}'
def app(name, rows):
    with open(os.path.join(GT, name), 'a', newline='') as f: csv.writer(f).writerows(rows)
app('agency.txt', [['CN', 'Canadian National Railways', 'https://en.wikipedia.org/wiki/Canadian_National_Railway', 'America/Vancouver', 'en', ''],
                   ['CP', 'Canadian Pacific Railway', 'https://en.wikipedia.org/wiki/Canadian_Pacific_Railway', 'America/Vancouver', 'en', '']])
app('routes.txt', [['CNR', 'CN', 'CN', 'Vancouver – Kamloops Jct – Jasper – Edmonton – Wainwright – Chauvin', 2, '2F6B44', 'FFFFFF', 'Schedule of April 25, 1948 (Official Guide, May 1948); intermediate stations from CN Tables 23 and 24, 1949, whose times agree. Pacific time throughout.'],
                   ['CNO', 'CN', 'CN Okanagan', 'Kamloops Jct – Vernon – Kelowna', 2, '2F6B44', 'FFFFFF', 'CN Table 306, 1949. Lumby Jct–Kelowna track from a tracing.'],
                   ['CPR', 'CP', 'CP', 'Vancouver – Kamloops – Revelstoke – Field – Banff – Calgary – Strathmore – Medicine Hat – Walsh (and Kettle Valley trains from Odlum)', 2, '7A1E2C', 'FFFFFF', 'CP Tables 6 and 7, 1948. Pacific time throughout.'],
                   ['CPM', 'CP', 'CP Mission', 'Vancouver – Mission – Huntingdon', 2, '7A1E2C', 'FFFFFF', 'CP Tables 7 and 162, 1948.'],
                   ['CPW', 'CP', 'CP Westminster', 'Coquitlam – New Westminster', 2, '7A1E2C', 'FFFFFF', 'CP Table 163, 1948.'],
                   ['CPCA', 'CP', 'CP by Carseland', 'Vancouver – Calgary – Carseland – Medicine Hat (Nos. 7 and 8, The Dominion; Nos. 13 and 14, The Mountaineer)', 2, '7A1E2C', 'FFFFFF', 'CP Tables 6 and 7, 1948. Pacific time throughout.']])
app('calendar.txt', [['CN_SUTT', 0, 1, 0, 1, 0, 0, 1, '19490616', '19491231'], ['CN_DAILY', 1, 1, 1, 1, 1, 1, 1, '19490616', '19491231'], ['CN_WS', 0, 0, 1, 0, 0, 1, 0, '19490616', '19491231'],
                     ['CN_TF', 0, 1, 0, 0, 1, 0, 0, '19490616', '19491231'],
                     ['CN_MWF', 1, 0, 1, 0, 1, 0, 0, '19490616', '19491231'], ['CN_TTS', 0, 1, 0, 1, 0, 1, 0, '19490616', '19491231'], ['CN_XSUN', 1, 1, 1, 1, 1, 1, 0, '19490616', '19491231'], ['CP_DAILY', 1, 1, 1, 1, 1, 1, 1, '19490616', '19491231'],
                     ['CP_XSUN', 1, 1, 1, 1, 1, 1, 0, '19490616', '19491231']])
seen = set(r[0] for r in csv.reader(open(os.path.join(GT, 'stops.txt'))))
srows = []
for L in out:
    for s in L['stations']:
        if s['gid'] not in seen: seen.add(s['gid']); srows.append([s['gid'], f"{s['name']} ({'CN' if L['key'] in ('cn', 'cno') else 'CP'})", f"{s['lat']:.6f}", f"{s['lon']:.6f}", s['note']])
app('stops.txt', srows)
rid = {'cn': 'CNR', 'cno': 'CNO', 'cp': 'CPR', 'cpm': 'CPM', 'cpw': 'CPW', 'cpc': 'CPCA'}
shp, trows, strows = [], [], []
for L in out:
    Rt = lines[L['key']]['route']
    for sid, coords in ((L['key'].upper() + '_OUT', list(Rt.coords)), (L['key'].upper() + '_IN', list(Rt.coords)[::-1])):
        a, p = 0.0, None
        for k, xy in enumerate(coords):
            if p: a += math.dist(p, xy)
            p = xy; lon, lat = inv(*xy); shp.append([sid, f'{lat:.6f}', f'{lon:.6f}', k, f'{a:.1f}'])
    for t in L['trips']:
        trows.append([rid[L['key']], t['svc'], t['id'], L['stations'][t['stops'][-1][0]]['name'], f"{t['num']} {t['name']}".strip(), t['dir'],
                      L['key'].upper() + ('_OUT' if t['dir'] == 0 else '_IN')])
        for k, (i, a, b, tp) in enumerate(t['stops'], 1):
            c = lines[L['key']]['stations'][i]['chain']; dist = c if t['dir'] == 0 else Rt.length - c
            strows.append([t['id'], fmt(a), fmt(b), L['stations'][i]['gid'], k, f'{dist:.1f}', 1])
app('shapes.txt', shp); app('trips.txt', trows); app('stop_times.txt', strows)
with zipfile.ZipFile(os.path.join(HERE, 'bcer_fraser_valley_1949_gtfs.zip'), 'w', zipfile.ZIP_DEFLATED) as z:
    for fn in sorted(os.listdir(GT)): z.write(os.path.join(GT, fn), fn)
print({k: (len(v['stations']), len(v['trips'])) for k, v in lines.items()})
