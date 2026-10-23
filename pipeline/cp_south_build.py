"""CP southern lines (1948): Crowsnest route Nelson - Yahk - Cranbrook - Crowsnest (Table 151), Rocky Mountain Trench line
Golden - Lake Windermere - Fort Steele (Tables 152, 152A), and Castlegar - Trail (Table 155). Track: NRWN (south.json + cpmain.json).
Run after kv_build.py. Stations at printed mileage, pinned to anchor stations along each route."""
import csv, json, math, os, pickle, re, zipfile
import numpy as np
from shapely.geometry import Point, LineString
from nrwn_graph import Net, fwd, inv, MI
from shapely.ops import substring
from bc_bits import K
HERE = os.path.dirname(os.path.abspath(__file__)); GT = os.path.join(HERE, 'gtfs')
F = json.load(open(os.path.join(HERE, 'nrwn', 'south.json'))); seen = {f['data'].get('NID') for f in F}
F += [f for f in json.load(open(os.path.join(HERE, 'nrwn', 'cpmain.json'))) if f['data'].get('NID') not in seen]
net = Net(F)
# Alberta (nrwn/alberta.json, cut from the Alberta file of the national network by nrwn/extract_alberta.py): Crowsnest to Lethbridge by Macleod
LETHBRIDGE = (-112.8375, 49.6975)                                  # the Canadian Pacific station, Lethbridge
_ab = Net([f for f in json.load(open(os.path.join(HERE, 'nrwn', 'alberta.json'))) if f['schema'].endswith('Track')])
def alberta_tail(frm, *to):
    r, sn = _ab.route(frm, *to); print(f'  Alberta: {r.length/MI:.1f} mi, snaps {[round(x) for x in sn]}'); return r
# ---- Lethbridge to Medicine Hat (Table 151 east of Lethbridge, ab_cp_t151.csv): track and station positions by ab_lines.py, over nrwn/alberta_all.json
import ab_lines, ab_table
_e_rows, _e_trains, _e_pieces = ab_lines.trace(dict(key='cr', rail='cp', legs=[dict(csv='ab_cp_t151.csv', a='Lethbridge', b='Medicine Hat')], cols=None, places={'Lethbridge': LETHBRIDGE}))
ab_lines.report(dict(key='cr east'), _e_rows, _e_pieces)
EAST = LineString([q for k, p in enumerate(_e_pieces) for q in (p['coords'] if k == 0 else p['coords'][1:])])
EAST_ANCHORS = [(r['name'], inv(*EAST.interpolate(r['d']).coords[0])) for r in _e_rows[1:]]
_mh, _du = ab_lines.place('cp', 'Medicine Hat'), ab_lines.place('cp', 'Dunmore')          # Dunmore to Medicine Hat is the main line, drawn by the cp line
_main = ab_lines.path('cp', ab_lines.snap('cp', fwd(*_mh[:2]), 600)[0], ab_lines.snap('cp', fwd(*_du[:2]), 2500)[0], 40000)
EAST_SHARED = next((d for d in np.arange(EAST.length, 0, -50.0) if LineString(_main).distance(EAST.interpolate(d)) > 15), EAST.length) if _main else EAST.length
print(f'  Lethbridge - Medicine Hat: {EAST.length / MI:.1f} mi (printed 111.8), the last {(EAST.length - EAST_SHARED) / MI:.1f} mi over the main line from Dunmore')
def east_rows():
    """Table 151 east of Lethbridge as rows for the Crowsnest table: Pacific time, an hour earlier than printed"""
    out = []
    for r in ab_table.load(os.path.join(HERE, 'ab_cp_t151.csv'))['rows']:
        out.append({'mile': str(r['mile']), 'station': r['station'], **{c: ab_table.shift_text(r.get(c, '')) for c in ('No11', 'No12', 'No511', 'No512')}})
    return out
NELSON = inv(*pickle.load(open(os.path.join(HERE, 'kv_route.pkl'), 'rb'))['KV'].coords[-1])

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

LINES = []
def build(key, label, dir_labels, csvfile, anchors, gid_pre, shared_gid, principal, trains, flip=False, splice=None, RT=None, none_to=None, tail=None, more=None, none_from=None):
    """anchors: [(station, lon/lat)] in route order (route runs first -> last; chain increases away from Vancouver)."""
    """tail: (LineString, n) - track beyond the B.C. network, joined on after the last B.C. anchor; the last n anchors lie on it."""
    RT, snaps = (RT, []) if RT is not None else net.route(*[p for _, p in (anchors[:-tail[1]] if tail else anchors)])
    if splice:      # replace the part of the NRWN route between the trace's two ends with Brendan's trace
        T = LineString([fwd(*p) for p in splice]); a, b = RT.project(Point(T.coords[0])), RT.project(Point(T.coords[-1]))
        print(f'  splice: ends {RT.distance(Point(T.coords[0])):.0f} / {RT.distance(Point(T.coords[-1])):.0f} m off the NRWN route; replaces {(b-a)/MI:.1f} mi with {T.length/MI:.1f} mi')
        RT = LineString(list(substring(RT, 0, a).coords) + list(T.coords) + list(substring(RT, b, RT.length).coords))
    if tail:
        print(f'  tail: joins {math.dist(RT.coords[-1], tail[0].coords[0]):.0f} m from the end of the B.C. route; {tail[0].length/MI:.1f} mi')
        RT = LineString(list(RT.coords) + list(tail[0].coords)[1:])
    rows = list(csv.DictReader(l for l in open(os.path.join(HERE, csvfile)) if not l.startswith('#')))
    for m in more or []:                                              # rows from another table: a station in both takes the other table's cells as well
        old = next((r for r in rows if r['station'] == m['station']), None)
        if old: old.update({k: v for k, v in m.items() if v and k not in ('mile', 'station')})
        else: rows.append(m)
    mi = {r['station']: float(r['mile']) for r in rows}
    ac = [RT.project(Point(fwd(*p))) for _, p in anchors]; ac[0] = 0.0; ac[-1] = RT.length
    am = [mi[n] for n, _ in anchors]
    sign = 1 if am[-1] > am[0] else -1
    def chain(m): return float(np.interp(sign * m, [sign * x for x in am], ac))
    print(f'{key}: {RT.length/MI:.1f} mi traced, timetable {abs(am[-1]-am[0]):.1f}; snaps {[round(s) for s in snaps]}')
    stations, idx = [], {}
    for r in sorted(rows, key=lambda r: sign * float(r['mile'])):
        n = r['station']; idx[n] = len(stations)
        stations.append(dict(name=n, chain=chain(mi[n]), mile=mi[n], principal=n in principal,
                             gid=shared_gid.get(n, gid_pre + re.sub(r'\W+', '_', n.upper()).strip('_')), note='Canadian Pacific station'))
    trips = []
    for col, num, name, svc, d, note in trains:
        rs = sorted((r for r in rows if r.get(col) and re.search(r'\d', r[col])), key=lambda r: sign * float(r['mile']), reverse=(d == 1))
        stops = [[idx[r['station']], *times(r[col]), 1] for r in rs]
        trips.append(dict(id=f'{key.upper()}-' + re.sub(r'[ .]', '', num), num=num.split('-')[0], name=name, svc=svc, dir=d, stops=monotonic(stops), note=note))
        f = lambda x: f'{x // 3600:02d}:{x % 3600 // 60:02d}'
        print(' ', num, ' '.join(f"{stations[a]['name'][:9]} {f(b)}" for a, b, c, _ in stops[:2]), '...', ' '.join(f"{stations[a]['name'][:9]} {f(b)}" for a, b, c, _ in stops[-2:]))
    for t in trips:
        for (a, _, da, _), (b, tb, _, _) in zip(t['stops'], t['stops'][1:]):
            dist = abs(stations[b]['chain'] - stations[a]['chain']) / MI; mins = (tb - da) / 60
            if mins <= 0 or dist / (mins / 60) > 50: print(f"   !! {t['id']} {stations[a]['name']}->{stations[b]['name']} {dist:.1f}mi/{mins:.0f}min")
    LINES.append(dict(key=key, label=label, dir_labels=dir_labels, RT=RT, stations=stations, trips=trips,
                      none_to=stations[idx[none_to]]['chain'] if none_to else None, none_from=RT.length - none_from if none_from else None))

# ---------------- transcriptions
CR = """# CP Table 151 (1948), Crowsnest route: Lethbridge - Macleod - Crowsnest (the Alberta border) - Fernie - Cranbrook - Yahk - Creston - Kootenay Landing - Procter - Nelson.
# Miles from Medicine Hat. Pacific time throughout: the table prints Mountain time east of Crowsnest, entered here an hour earlier. 11 and M681 westbound (read down), 12 and M682 eastbound (read up).
# M681 lies over at Cranbrook (ar 6.30 p.m., on at 3.00 a.m. to Yahk for the Spokane International). M829 (Mon.) / M830 (Sat.) are the Lake Windermere mixed trains (Table 152).
mile,station,No11,M681,M681b,No12,M682,M829,M830
111.8,Lethbridge,lv 8.45p,lv 8.30a,,ar 7.05a,ar 5.10p,,
118.1,Coalhurst,8.57p,8.50a,,6.54a,4.55p,,
119.7,Kipp,,,,,f4.50p,,
127.3,Monarch,f9.10p,9.08a,,6.41a,4.36p,,
134.4,Pearce,,f9.22a,,,f4.23p,,
143.4,Macleod,ar 9.40p / lv 10.20p,ar 9.40a / lv 10.00a,,ar 6.00a / lv 6.20a,ar 3.53p / lv 4.05p,,
153.3,Peigan,,f10.22a,,,f3.34p,,
158.7,Chokio,,f10.33a,,,f3.23p,,
163.9,Brocket,10.57p,10.45a,,5.28a,3.13p,,
172.9,Pincher,11.15p,11.10a,,5.14a,2.57p,,
179.9,Cowley,11.32p,11.30a,,4.55a,2.38p,,
184.3,Lundbreck,11.45p,11.40a,,4.45a,2.28p,,
190.9,Burmis,12.00a,11.58a,,4.33a,2.15p,,
196.3,Hillcrest,12.15a,12.15p,,4.19a,2.00p,,
198.2,Frank,12.23a,12.30p,,4.12a,1.50p,,
200.0,Blairmore,12.35a,12.47p,,4.05a,1.45p,,
203.6,Coleman,12.55a,1.05p,,3.56a,1.35p,,
207.8,Sentinel,f1.10a,f1.25p,,f3.46a,f1.25p,,
212.9,Crowsnest,ar 1.35a / lv 1.45a,ar 1.50p / lv 2.15p,,ar 3.25a / lv 3.35a,ar 12.45p / lv 1.10p,,
219.6,McGillivray,f2.01a,f2.33p,,f3.04a,f12.15p,,
225.5,Michel,2.15a,2.55p,,2.45a,11.55a,,
227.3,Natal,2.20a,3.00p,,2.40a,11.47a,,
231.0,Sparwood,f2.32a,f3.08p,,f2.32a,f11.39a,,
241.3,Hosmer,f2.51a,f3.30p,,2.10a,f11.18a,,
248.8,Fernie,3.10a,3.53p,,1.50a,11.02a,,
257.2,Morrissey,f3.27a,f4.13p,,f1.29a,f10.33a,,
267.0,Elko,f3.44a,f4.33p,,f1.12a,10.12a,,
271.7,Caithness,f3.50a,f4.46p,,f1.00a,f10.02a,,
274.6,Galloway,f3.54a,f4.52p,,f12.55a,f9.56a,,
279.9,Jaffray,4.02a,f5.05p,,12.44a,9.44a,,
284.1,Colvalli,f4.08a,f5.15p,,f12.36a,f9.34a,ar 11.10a,lv 2.10p
290.0,Wardner,4.16a,5.35p,,12.24a,9.22a,10.52a,2.30p
297.5,Mayook,f4.29a,f5.55p,,f12.09a,f9.05a,f10.32a,f2.50p
302.0,Rampart,f4.37a,f6.05p,,f12.01a,f8.56a,f10.22a,f3.00p
311.9,Cranbrook,ar 5.00a / lv 5.25a,ar 6.30p,lv 3.00a,ar 11.25p / lv 11.45p,ar 8.05a / lv 8.35a,lv 10.00a,ar 3.25p
317.3,Fassiferne,f5.36a,,f3.20a,f11.13p,f7.51a,,
320.0,Lumberton,f5.40a,,f3.30a,f11.08p,f7.44a,,
326.1,Jerome,f5.50a,,f3.44a,f10.56p,f7.30a,,
331.7,Moyie,6.00a,,f3.56a,f10.43p,f7.17a,,
333.7,Aldridge,f6.04a,,f4.00a,f10.39p,f7.13a,,
342.0,Tochty,f6.17a,,f4.17a,f10.23p,f6.56a,,
347.0,Ryan,f6.25a,,f4.27a,f10.14p,f6.46a,,
352.5,Yahk,ar 6.35a / lv 6.45a,,ar 4.40a,ar 9.56p / lv 10.04p,lv 6.35a,,
357.8,Goatfell,f6.55a,,,f9.45p,,,
367.3,McConnell,7.15a,,,9.21p,,,
374.4,Canyon,f7.30a,,,f8.59p,,,
376.1,Erickson,7.35a,,,8.52p,,,
379.3,Creston,7.48a,,,8.37p,,,
385.7,Wynndel,8.04a,,,8.22p,,,
391.7,Sirdar,8.16a,,,8.04p,,,
395.0,Kootenay Landing,f8.23a,,,f7.51p,,,
403.3,Tye,8.39a,,,7.32p,,,
410.9,Drewry,f8.57a,,,f7.09p,,,
419.4,Blake,f9.15a,,,f6.45p,,,
429.4,Procter,9.40a,,,6.20p,,,
431.8,Sunshine Bay,f9.46a,,,f6.15p,,,
434.1,Harrop,9.51a,,,6.10p,,,
439.9,Atbara,f10.03a,,,f5.58p,,,
444.2,Troup,f10.09a,,,f5.49p,,,
449.5,Nelson,ar 10.25a,,,lv 5.35p,,,
"""
TR = """# CP Tables 152 (Cranbrook - Lake Windermere) and 152A (Lake Windermere - Golden), 1948. Miles from Colvalli (Cranbrook side negative).
# Cranbrook - Colvalli is the main line (Table 151 prints these times); the train stands 25 minutes at Colvalli and reverses up the Kootenay Central.
# Colvalli - Fort Steele - Canalflat is today's line (NRWN): Brendan's Colvalli traces land on it and it measures 64.1 mi against 64.1 printed, so it is
# taken as the 1948 line. Fort Steele is placed by its printed mileage between Colvalli and Canalflat, not pinned to a map point.
# M829 Mon. and M830 Sat. (Cranbrook - Lake Windermere); M831 Tue. & Thu. and M832 Wed. & Fri. (Lake Windermere - Golden).
mile,station,M829,M830,M831,M832
-27.8,Cranbrook,lv 10.00a,ar 3.25p,,
-17.9,Rampart,f10.22a,f3.00p,,
-13.4,Mayook,f10.32a,f2.50p,,
-5.9,Wardner,10.52a,2.30p,,
0.0,Colvalli,ar 11.10a / lv 11.35a,ar 1.45p / lv 2.10p,,
9.0,Bull River,12.05p,f1.10p,,
15.4,Fenwick,f12.25p,f12.35p,,
23.0,Fort Steele,12.55p,12.10p,,
29.9,Doyle,f1.15p,f11.45a,,
35.3,Wasa,1.35p,11.25a,,
46.3,Skookumchuck,2.05p,10.50a,,
52.6,Torrent,f2.30p,f10.25a,,
64.1,Canalflat,3.15p,9.45a,,
68.9,Columbia Lake,f3.30p,f9.15a,,
77.1,Fairmont Hot Springs,3.50p,8.50a,,
83.3,Rushmere,f4.10p,f8.30a,,
88.4,Goldie Creek,f4.30p,f8.15a,,
92.8,Lake Windermere,ar 4.45p,lv 8.00a,lv 7.20a,ar 1.00p
101.4,Radium,,,7.45a,12.30p
107.1,Edgewater,,,8.05a,12.05p
112.1,Luxor,,,f8.25a,f11.35a
117.9,Brisco,,,8.45a,11.20a
125.6,Spillimacheen,,,9.10a,11.00a
132.6,Harrogate,,,9.35a,10.35a
143.7,Parson,,,10.10a,10.10a
151.5,McMurdo,,,10.35a,9.40a
162.1,Nicholson,,,11.05a,9.15a
166.7,Golden,,,ar 11.30a,lv 9.00a
"""
TL = """# CP Table 155 (1948), Castlegar - Trail. Trains 43 and 44 run through from Nelson (Table 151). Buses not shown.
mile,station,No43,No44
0.0,Castlegar,lv 7.10p,ar 10.55a
3.6,Kinnaird,f7.17p,f10.46a
5.9,Blueberry,f7.22p,f10.41a
8.0,Poupore,f7.26p,f10.37a
9.9,Genelle,f7.31p,f10.29a
12.6,Birchbank,f7.36p,f10.24a
18.7,Tadanac,7.53p,10.10a
20.1,Trail,ar 8.05p,lv 9.55a
"""
open(os.path.join(HERE, 'cp_1948_table151_crowsnest.csv'), 'w').write(CR)
open(os.path.join(HERE, 'cp_1948_tables152_152a.csv'), 'w').write(TR)
open(os.path.join(HERE, 'cp_1948_table155.csv'), 'w').write(TL)

# ---------------- lines (route order: away from Vancouver)
build('cr', 'Canadian Pacific', ['to Cranbrook, the Crowsnest, Lethbridge and Medicine Hat', 'to Nelson'], 'cp_1948_table151_crowsnest.csv',
      [('Nelson', NELSON), ('Procter', (-116.957, 49.619)), ('Creston', (-116.513, 49.098)), ('Yahk', (-116.088, 49.088)),
       ('Moyie', (-115.835, 49.288)), ('Cranbrook', (-115.7727, 49.5117)), ('Colvalli', K['Cranbrook Pre-1966'][-1]), ('Fernie', (-115.063, 49.504)), ('Crowsnest', (-114.693, 49.632)), ('Lethbridge', LETHBRIDGE)] + EAST_ANCHORS,
      'CR_', {'Nelson': 'KV_NELSON', 'Colvalli': 'CP_COLVALLI', 'Medicine Hat': 'CP_MEDICINE_HAT'},
      {'Nelson', 'Creston', 'Yahk', 'Cranbrook', 'Fernie', 'Michel', 'Crowsnest', 'Procter', 'Kootenay Landing', 'Moyie', 'Wardner', 'Elko', 'Lethbridge', 'Macleod', 'Pincher', 'Blairmore', 'Coleman', 'Medicine Hat', 'Taber', 'Bow Island'},
      [('No11', '11', 'Kootenay Express', 'CP_DAILY', 1, 'From Medicine Hat and Lethbridge by the Crowsnest; on to Vancouver by the Kettle Valley.'),
       ('No12', '12', 'Kettle Valley Express', 'CP_DAILY', 0, 'From Vancouver by the Kettle Valley; Nelson to Lethbridge by the Crowsnest, and on to Medicine Hat.'),
       ('No511', '511', '', 'CP_XSUN', 1, 'Medicine Hat to Lethbridge, daily except Sunday: the morning connection off the main line trains from the east.'),
       ('No512', '512', '', 'CP_XSUN', 0, 'Lethbridge to Medicine Hat, daily except Sunday: the evening connection for the main line trains to the east.'),
       ('M681', 'M681', 'Mixed', 'CP_DAILY', 1, 'Mixed train from Lethbridge and Macleod to Cranbrook, where it lies over until 3.00 a.m.'),
       ('M681b', 'M681-2', 'Mixed', 'CP_DAILY', 1, 'Mixed train, Cranbrook to Yahk, connecting with the Spokane International for Spokane.'),
       ('M682', 'M682', 'Mixed', 'CP_DAILY', 0, 'Mixed train, Yahk to Cranbrook and on to Macleod and Lethbridge.')],
      splice=K['Cranbrook Pre-1966'], more=east_rows(), none_from=EAST.length - EAST_SHARED,
      tail=(LineString(list(alberta_tail((-114.69298, 49.631951), LETHBRIDGE).coords) + list(EAST.coords)[1:]), 1 + len(EAST_ANCHORS)))
# Windermere line: Cranbrook - (main line, Brendan's pre-1966 trace) - Colvalli, reverse, - Fort Steele - Golden. The Lake Windermere mixed trains
# (M829/M830) run through from Cranbrook, so the line starts there; Cranbrook - Colvalli is drawn by the cr line.
_cr = LINES[0]; _ci = {s['name']: s['chain'] for s in _cr['stations']}
CB, COL = (-115.7727, 49.5117), K['Cranbrook Pre-1966'][-1]
_north, _sn = net.route(COL, (-115.632, 49.624), (-115.82, 50.15), (-116.03, 50.50), (-116.39, 50.91), (-116.963, 51.299))
_trRT = LineString(list(substring(_cr['RT'], _ci['Cranbrook'], _ci['Colvalli']).coords) + list(_north.coords))
print(f'  Windermere line: Cranbrook - Colvalli {(_ci["Colvalli"] - _ci["Cranbrook"]) / MI:.1f} mi (printed 27.8); Colvalli - Fort Steele on NRWN, snaps {[round(x) for x in _sn[:2]]}')
# Cranbrook station to the Kimberley branch switch, on the national network (for interim_build.py)
_fs, _ = net.route(CB, (-115.632, 49.624)); _kb = substring(_fs, 0, _fs.project(Point(fwd(*K['Kimberley Branch'][0]))))     # (today's line to Fort Steele passes the switch)
json.dump([list(inv(*p)) for p in _kb.coords], open(os.path.join(HERE, 'cranbrook_kimberley_jct.json'), 'w'))
build('tr', 'Canadian Pacific', ['to Lake Windermere and Golden', 'to Colvalli and Cranbrook'], 'cp_1948_tables152_152a.csv',
      [('Cranbrook', CB), ('Colvalli', COL), ('Canalflat', (-115.82, 50.15)), ('Lake Windermere', (-116.03, 50.50)),
       ('Spillimacheen', (-116.39, 50.91)), ('Golden', (-116.963, 51.299))],
      'TR_', {'Golden': 'CP_GOLDEN', 'Cranbrook': 'CR_CRANBROOK', 'Rampart': 'CR_RAMPART', 'Mayook': 'CR_MAYOOK', 'Wardner': 'CR_WARDNER', 'Colvalli': 'CP_COLVALLI'},
      {'Cranbrook', 'Wardner', 'Fort Steele', 'Wasa', 'Skookumchuck', 'Canalflat', 'Fairmont Hot Springs', 'Lake Windermere', 'Radium', 'Edgewater', 'Brisco', 'Spillimacheen', 'Parson', 'Golden'},
      [('M829', 'M829', 'Mixed', 'CP_MON1', 0, 'Mixed train, Cranbrook to Lake Windermere (Mondays): by the main line to Colvalli, where it stands 25 minutes and reverses, then up the Kootenay Central through Fort Steele.'),
       ('M830', 'M830', 'Mixed', 'CP_SAT1', 1, 'Mixed train, Lake Windermere to Cranbrook (Saturdays): down the Kootenay Central to Colvalli, where it stands 25 minutes and reverses, then the main line to Cranbrook.'),
       ('M831', 'M831', 'Mixed', 'CP_TTH', 0, 'Mixed train, Lake Windermere to Golden (Tuesdays and Thursdays).'),
       ('M832', 'M832', 'Mixed', 'CP_WF', 1, 'Mixed train, Golden to Lake Windermere (Wednesdays and Fridays).')],
      RT=_trRT, none_to='Colvalli')
# (the Spokane International, Yahk - Kingsgate - Spokane, is its own step: si_build.py)
build('tl', 'Canadian Pacific', ['to Trail', 'to Castlegar'], 'cp_1948_table155.csv',
      [('Castlegar', tuple(json.load(open(os.path.join(HERE, 'castlegar_wye.json')))['wye'])), ('Trail', (-117.708, 49.097))], 'TL_', {'Castlegar': 'KV_CASTLEGAR'}, {'Castlegar', 'Trail', 'Tadanac'},
      [('No43', '43', '', 'CP_DAILY', 0, 'Through from Nelson (Table 151) to Trail.'), ('No44', '44', '', 'CP_DAILY', 1, 'Trail to Castlegar, through to Nelson (Table 151).')])

# ---------------- viz + GTFS
vd = json.load(open(os.path.join(HERE, 'viz_data.json')))
def fmt(x): return f'{x // 3600:02d}:{x % 3600 // 60:02d}:{x % 60:02d}'
def app(name, rows_):
    with open(os.path.join(GT, name), 'a', newline='') as fh: csv.writer(fh).writerows(rows_)
app('calendar.txt', [['CP_SAT1', 0, 0, 0, 0, 0, 1, 0, '19490616', '19491231'], ['CP_TTH', 0, 1, 0, 1, 0, 0, 0, '19490616', '19491231'],
                     ['CP_WF', 0, 0, 1, 0, 1, 0, 0, '19490616', '19491231']])
gseen = set(r[0] for r in csv.reader(open(os.path.join(GT, 'stops.txt'))))
RID = {'cr': ('CPC', 'CP Crowsnest', 'Nelson – Cranbrook – Crowsnest – Lethbridge – Medicine Hat'), 'tr': ('CPT', 'CP Windermere', 'Cranbrook – Colvalli – Lake Windermere – Golden'), 'tl': ('CPTL', 'CP Trail', 'Castlegar – Trail'), 'si': ('SIR', 'Spokane International', 'Yahk – Kingsgate')}
for L in LINES:
    RT = L['RT']; route = []; acc = 0; prev = None
    for xy in RT.simplify(2.0).coords:
        if prev: acc += math.dist(xy, prev)
        prev = xy; lon, lat = inv(*xy); route.append([round(lon, 6), round(lat, 6), round(acc, 1)])
    sc = acc / RT.length; st = []
    for s in L['stations']:
        lon, lat = inv(*RT.interpolate(s['chain']).coords[0])
        st.append(dict(name=s['name'], chain=round(s['chain'] * sc, 1), lon=round(lon, 6), lat=round(lat, 6), mile=s['mile'], principal=s['principal'], note=s['note'], kml='', gid=s['gid']))
    vd['lines'] = [x for x in vd['lines'] if x['key'] != L['key']] + [dict(key=L['key'], kind='p', label=L['label'], mainline=True, owner='cp', route=route, stations=st,
                                                                          **({'livery': 'si'} if L['key'] == 'si' else {}), dirLabels=L['dir_labels'], segments=([dict(owner='none', a=0.0, b=round(L['none_to'] * sc, 1))] if L['none_to'] else []) + ([dict(owner='none', a=round(L['none_from'] * sc, 1), b=round(acc, 1))] if L.get('none_from') else []), trips=L['trips'])]
    rid, short, longn = RID[L['key']]
    app('routes.txt', [[rid, 'CP', short, longn, 2, '7A1E2C', 'FFFFFF', 'CP 1948. Track from the National Railway Network.']])
    app('stops.txt', [[s['gid'], s['name'] + ' (CP)', f"{s['lat']:.6f}", f"{s['lon']:.6f}", s['note']] for s in st if s['gid'] not in gseen]); gseen |= {s['gid'] for s in st}
    shp = []
    for sid, coords in ((L['key'].upper() + '_OUT', list(RT.coords)), (L['key'].upper() + '_IN', list(RT.coords)[::-1])):
        a, p = 0.0, None
        for k, xy in enumerate(coords):
            if p: a += math.dist(p, xy)
            p = xy; lon, lat = inv(*xy); shp.append([sid, f'{lat:.6f}', f'{lon:.6f}', k, f'{a:.1f}'])
    app('shapes.txt', shp)
    S = L['stations']
    app('trips.txt', [[rid, t['svc'], t['id'], S[t['stops'][-1][0]]['name'], f"{t['num']} {t['name']}".strip(), t['dir'], L['key'].upper() + ('_OUT' if t['dir'] == 0 else '_IN')] for t in L['trips']])
    app('stop_times.txt', [[t['id'], fmt(a), fmt(b), S[i]['gid'], k, f"{(S[i]['chain'] if t['dir'] == 0 else RT.length - S[i]['chain']):.1f}", 1]
                           for t in L['trips'] for k, (i, a, b, tp) in enumerate(t['stops'], 1)])
def extra(key, pts_lonlat):
    route = []; acc = 0.0; prev = None
    for lon, lat in pts_lonlat:
        xy = fwd(lon, lat)
        if prev: acc += math.dist(xy, prev)
        prev = xy; route.append([round(lon, 6), round(lat, 6), round(acc, 1)])
    vd['lines'] = [x for x in vd['lines'] if x['key'] != key] + [dict(key=key, kind='p', label='Canadian Pacific', mainline=True, owner='cp', route=route,
                                                                       stations=[], dirLabels=['', ''], segments=[], trips=[])]
extra('x_col', K['Wye'])      # Colvalli wye, west leg: no train runs over it on the map (trains reverse at the station), but an engine would turn on it
open(os.path.join(HERE, 'viz_data.json'), 'w').write(json.dumps(vd, separators=(',', ':')))
with zipfile.ZipFile(os.path.join(HERE, 'bcer_fraser_valley_1949_gtfs.zip'), 'w', zipfile.ZIP_DEFLATED) as z:
    for fn in sorted(os.listdir(GT)): z.write(os.path.join(GT, fn), fn)
