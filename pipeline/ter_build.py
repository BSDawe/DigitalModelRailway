"""Texas Electric Railway (Brendan, 23 Nov 2026): the Dallas interurban's two lines in 1948, Dallas - Denison and Dallas - Waco. Stand-alone step (copies wpy_build.py).
Sources:
- Track and stations: the trace by Ravenna (@bromaeosaur.bsky.social on Bluesky), supplied by Brendan (traces/texas/texas_electric.json, cut from her KML: the main lines and the
  station points; the raw KML is in the private repo, traces/texas/).
- 1948: the company's Official Guide page (Brendan's scan): "Fast and dependable schedules are operated almost every hour from 5:30 a.m. to 9:30 p.m." with the list of stations and
  miles (Denison Division: Dallas 0, Vickery 8.1, Richardson 14.8, Plano 20.2, Allen 26.3, McKinney 33.7, Melissa 40.6, Anna 45.2, Van Alstyne 50.5, Howe 56.8, Sherman 66.9,
  Denison 77.2; Waco Division: Dallas 0, Lancaster 14.4, Red Oak 20.5, Sterrett 23.8, Waxahachie 30.0, Forreston 39.1, Italy 44.4, Milford 49.9, Hillsboro 63.5, Abbott 73.1,
  West 78.9, Waco 96.5). The Corsicana Division (abandoned 1941) is not on it.
- Times: the passenger car schedule of March 1939 (american-rails.com/ter.html; Brendan: "a reference for 'almost hourly' and travel time"), Central Standard Time. Its timing
  points are taken as printed; the other 1948 stations get times by distance along the track (estimated, timepoint 0). Departures after 9.30 p.m. in 1939 (Dallas 11.05 p.m. to
  Waco; Denison 11.45 p.m. to Sherman) are left out by the 1948 page's "5:30 a.m. to 9:30 p.m." (Claude's reading). Daily (*) and daily except Sunday (dagger) as printed.
Shown on the Pacific clock (Central less two hours). Colour #c27c0e is Claude's pick."""
import csv, json, math, os
HERE = os.path.dirname(os.path.abspath(__file__))
GT = os.path.join(HERE, 'gtfs')
T = json.load(open(os.path.join(HERE, 'traces', 'texas', 'texas_electric.json')))
P = T['points']
def km(a, b): return math.hypot((a[0] - b[0]) * 111.32 * math.cos(math.radians((a[1] + b[1]) / 2)), (a[1] - b[1]) * 110.57)
def chain(pts):
    out, d = [], 0.0
    for k, p in enumerate(pts):
        if k: d += km(pts[k - 1], p) * 1000
        out.append([p[0], p[1], round(d, 1)])
    return out
DAL = P['Dallas Interurban Building']
# station: (name, 1948 miles, point name in the trace or None (placed by miles), timing point in the 1939 schedule)
LINES = {
    'ter_d': dict(label='Dallas – Denison (Texas Electric)', track=[DAL] + T['lines']['Dallas - Sherman'] + T['lines']['Sherman - Denison'][1:],
                  st=[('Dallas', 0, 'Dallas Interurban Building', 'Dallas'), ('Vickery', 8.1, None, None), ('Richardson', 14.8, 'Richardson station', None),
                      ('Plano', 20.2, 'Plano station', 'Plano'), ('Allen', 26.3, 'Allen station', None), ('McKinney', 33.7, 'McKinney station', 'McKinney'),
                      ('Melissa', 40.6, 'Melissa station', None), ('Anna', 45.2, 'Anna station', None), ('Van Alstyne', 50.5, 'Van Alstyne station', 'Van Alstyne'),
                      ('Howe', 56.8, 'Howe station', None), ('Sherman', 66.9, 'Sherman station', 'Sherman'), ('Denison', 77.2, 'Denison terminal', 'Denison')]),
    'ter_w': dict(label='Dallas – Waco (Texas Electric)', track=[DAL] + T['lines']['Dallas - Waco'],
                  st=[('Dallas', 0, 'Dallas Interurban Building', 'Dallas'), ('Lancaster', 14.4, 'Lancaster station', 'Lancaster'), ('Red Oak', 20.5, 'Red Oak station', None),
                      ('Sterrett', 23.8, None, None), ('Waxahachie', 30.0, 'Waxahachie station', 'Waxahachie'), ('Forreston', 39.1, 'Forreston station', None),
                      ('Italy', 44.4, 'Italy station', 'Italy'), ('Milford', 49.9, 'Milford station', None), ('Hillsboro', 63.5, 'Hillsboro station', 'Hillsboro'),
                      ('Abbott', 73.1, 'Abbott station', None), ('West', 78.9, 'West station', 'West'), ('Waco', 96.5, 'Waco terminal', 'Waco')])}
# 1939 columns: (days, {timing point: 'h.mm' 24-hour}) in running order. '*' daily, '+' daily except Sunday.
D_OUT = [('*', 'Sherman 7.13 Denison 7.40'), ('+', 'McKinney 7.12 Van Alstyne 7.42 Sherman 8.13 Denison 8.40')] + [
    (d, f'Dallas {h}.00 Plano {h}.50 McKinney {h + 1}.12 Van Alstyne {h + 1}.42 Sherman {h + 2}.13 Denison {h + 2}.40') for d, h in
    (('*', 7), ('*', 8), ('*', 9), ('*', 11), ('*', 13), ('+', 14), ('*', 15), ('*', 16), ('*', 17), ('*', 19), ('*', 21))] + [('+', 'Dallas 18.00 Plano 18.50 McKinney 19.12')]
D_IN = [('+', 'McKinney 6.20 Plano 6.43 Dallas 7.38'), ('*', 'Denison 5.40 Sherman 6.09 Van Alstyne 6.40 McKinney 7.08 Plano 7.30 Dallas 8.25')] + [
    (d, f'Denison {h}.00 Sherman {h}.29 Van Alstyne {h + 1}.00 McKinney {h + 1}.28 Plano {h + 1}.50 Dallas {h + 2}.40') for d, h in
    (('+', 7), ('*', 8), ('*', 10), ('*', 12), ('*', 14), ('*', 15), ('*', 16), ('*', 17), ('+', 18), ('*', 19), ('*', 21))]
W_OUT = [('+', 'Hillsboro 6.40 West 7.06 Waco 7.40'), ('*', 'Dallas 5.30 Lancaster 6.07 Waxahachie 6.34 Italy 6.56 Hillsboro 7.28 West 7.53 Waco 8.25')] + [
    (d, f'Dallas {h}.30 Lancaster {h + 1}.07 Waxahachie {h + 1}.34 Italy {h + 1}.56 Hillsboro {h + 2}.28 West {h + 2}.53 Waco {h + 3}.25') for d, h in
    (('*', 7), ('*', 8), ('*', 9), ('*', 11), ('*', 13), ('*', 14), ('*', 15), ('*', 16), ('*', 17), ('*', 19), ('*', 21))] + [('+', 'Dallas 18.15 Lancaster 18.58')]
W_IN = [('+', 'Lancaster 6.18 Dallas 6.55'), ('*', 'Waxahachie 6.35 Lancaster 7.02 Dallas 7.40'),
        ('*', 'Waco 5.20 West 5.52 Hillsboro 6.15 Italy 6.44 Waxahachie 7.09 Lancaster 7.36 Dallas 8.15')] + [
    (d, f'Waco {h}.00 West {h}.34 Hillsboro {h}.58 Italy {h + 1}.27 Waxahachie {h + 1}.51 Lancaster {h + 2}.18 Dallas {h + 2}.55') for d, h in
    (('*', 7), ('*', 8), ('*', 9), ('*', 11), ('*', 13), ('*', 14), ('*', 15), ('*', 16), ('*', 17), ('*', 19), ('*', 21))] + [('+', 'Waco 18.00 West 18.34 Hillsboro 18.58')]
SCHED = {'ter_d': (D_OUT, D_IN), 'ter_w': (W_OUT, W_IN)}
SHIFT = -2 * 3600   # Central to Pacific
SVC = {'*': 'W_1111111', '+': 'W_1111110'}
def parse(s):
    w = s.split(); out = []
    i = 0
    while i < len(w):
        j = i
        while '.' not in w[j]: j += 1
        h, m = w[j].split('.'); out.append((' '.join(w[i:j]), int(h) * 3600 + int(m) * 60)); i = j + 1
    return out

vd = json.load(open(os.path.join(HERE, 'viz_data.json')))
NEW, rows = [], dict(routes=[], stops=[], shapes=[], trips=[], st=[])
for key, L in LINES.items():
    route = chain(L['track'])
    tot = route[-1][2]
    def near(pt):
        best = min(range(len(route) - 1), key=lambda k: km(pt, route[k]) + km(pt, route[k + 1]) - km(route[k], route[k + 1]))
        a, b = route[best], route[best + 1]
        dx, dy = b[0] - a[0], b[1] - a[1]
        t = max(0, min(1, ((pt[0] - a[0]) * dx + (pt[1] - a[1]) * dy) / ((dx * dx + dy * dy) or 1)))
        q = (a[0] + t * dx, a[1] + t * dy)
        return q, a[2] + t * (b[2] - a[2]), km(pt, q) * 1000
    st = []
    for nm, mi, pn, tp in L['st']:
        if pn:
            q, ch, off = near(P[pn]); note = f'Texas Electric Railway station (point from Ravenna\'s trace; {off:.0f} m off the track)'
        else:
            st.append(None); continue
        st.append(dict(name=nm, chain=round(ch, 1), lon=round(q[0], 6), lat=round(q[1], 6), mile=mi, principal=tp is not None, gid='TER_' + nm.upper().replace(' ', '_'), note=note,
                       zname=nm, city=nm))
    for k, (nm, mi, pn, tp) in enumerate(L['st']):   # placed by the 1948 miles between its neighbours
        if st[k] is None:
            a, b = st[k - 1], st[k + 1]
            ch = a['chain'] + (b['chain'] - a['chain']) * (mi - a['mile']) / (b['mile'] - a['mile'])
            j = max(i for i in range(len(route)) if route[i][2] <= ch); p0, p1 = route[j], route[min(j + 1, len(route) - 1)]
            f = (ch - p0[2]) / ((p1[2] - p0[2]) or 1)
            st[k] = dict(name=nm, chain=round(ch, 1), lon=round(p0[0] + f * (p1[0] - p0[0]), 6), lat=round(p0[1] + f * (p1[1] - p0[1]), 6), mile=mi, principal=False,
                         gid='TER_' + nm.upper().replace(' ', '_'), note='Texas Electric Railway station (placed by the 1948 miles, approximate)', zname=nm, city=nm)
        print(f"  {key} {nm:12s} {mi:5.1f} mi printed, {st[k]['chain'] / 1609.34:5.1f} traced")
    idx = {s['name']: i for i, s in enumerate(st)}
    trips = []
    for d_, cols in enumerate(SCHED[key]):
        for n, (days, s) in enumerate(cols):
            tp = [(idx[a], t) for a, t in parse(s)]
            if tp[0][1] > 21 * 3600 + 30 * 60: continue
            seq = range(tp[0][0], tp[-1][0] + 1) if d_ == 0 else range(tp[0][0], tp[-1][0] - 1, -1)
            given = dict(tp); stops = []
            for i in seq:
                if i in given: t = given[i]; flag = 1
                else:   # by distance between the timing points either side
                    pa = max((p for p in tp if (p[0] < i if d_ == 0 else p[0] > i)), key=lambda p: p[0] if d_ == 0 else -p[0])
                    pb = min((p for p in tp if (p[0] > i if d_ == 0 else p[0] < i)), key=lambda p: p[0] if d_ == 0 else -p[0])
                    f = (st[i]['chain'] - st[pa[0]]['chain']) / (st[pb[0]]['chain'] - st[pa[0]]['chain'])
                    t = round((pa[1] + f * (pb[1] - pa[1])) / 60) * 60; flag = 0
                stops.append([i, t + SHIFT, t + SHIFT, flag])
            h, m = divmod(tp[0][1] // 60, 60)
            first = f"{(h - 1) % 12 + 1}.{m:02d} {'a.m.' if h < 12 else 'p.m.'}"
            trips.append(dict(id=f"TER-{key[-1].upper()}{'NS'[d_]}-{n:02d}", num='Car', name='Texas Electric', svc=SVC[days], dir=d_, stops=stops, motor=True,
                              note=f"Texas Electric interurban, {st[stops[0][0]]['name']} {first} (Central time) to {st[stops[-1][0]]['name']}, "
                                   f"{'daily' if days == '*' else 'daily except Sunday'}. Times from the March 1939 schedule (the 1948 Guide: almost hourly, 5.30 a.m. - 9.30 p.m.); "
                                   f"stations not in the 1939 table timed by distance (est.). Shown in Pacific time."))
    NEW.append(dict(key=key, kind='X', label=L['label'], mainline=True, owner='ter', src='Texas Electric Railway: Official Guide 1948 (station list, "almost every hour from 5:30 a.m. to 9:30 p.m."); times from the March 1939 schedule; track and stations from Ravenna\'s trace (@bromaeosaur.bsky.social)',
                    route=route, stations=st, dirLabels=['to ' + st[-1]['name'], 'to Dallas'], segments=[], trips=trips))
    print(f'{key}: {tot / 1609.34:.1f} mi traced ({L["st"][-1][1]} printed), {len(trips)} trips')
vd['lines'] = [x for x in vd['lines'] if x['key'] not in LINES] + NEW
open(os.path.join(HERE, 'viz_data.json'), 'w').write(json.dumps(vd, separators=(',', ':')))

def fmt(x): return f'{x // 3600:02d}:{x % 3600 // 60:02d}:{x % 60:02d}'
def app(name, rows_):
    with open(os.path.join(GT, name), 'a', newline='') as fh: csv.writer(fh).writerows(rows_)
def have(name, col=0): return set(r[col] for r in csv.reader(open(os.path.join(GT, name))))
cal = have('calendar.txt')
for d in sorted({t['svc'] for L in NEW for t in L['trips']} - cal): app('calendar.txt', [[d, *d[2:], '19490616', '19491231']])
if 'TER' not in have('agency.txt'): app('agency.txt', [['TER', 'Texas Electric Railway', 'https://en.wikipedia.org/wiki/Texas_Electric_Railway', 'America/Vancouver', 'en', '']])
seen = have('stops.txt')
for L in NEW:
    st = L['stations']; tot = L['route'][-1][2]
    app('routes.txt', [['TER_' + L['key'].upper(), 'TER', L['label'].split(' (')[0], L['label'], 0, 'C27C0E', 'FFFFFF', L['src'] + '. Times on the Pacific clock.']])
    new = [[s['gid'], s['name'], f"{s['lat']:.6f}", f"{s['lon']:.6f}", s['note']] for s in st if s['gid'] not in seen]
    app('stops.txt', new); seen |= {r[0] for r in new}
    for sid, pts in ((L['key'].upper() + '_OUT', L['route']), (L['key'].upper() + '_IN', L['route'][::-1])):
        app('shapes.txt', [[sid, f'{p[1]:.6f}', f'{p[0]:.6f}', k, f"{(p[2] if sid.endswith('OUT') else tot - p[2]):.1f}"] for k, p in enumerate(pts)])
    for t in L['trips']:
        app('trips.txt', [['TER_' + L['key'].upper(), t['svc'], t['id'], st[t['stops'][-1][0]]['name'], 'Texas Electric', t['dir'], L['key'].upper() + ('_OUT' if t['dir'] == 0 else '_IN')]])
        app('stop_times.txt', [[t['id'], fmt(a), fmt(b), st[i]['gid'], k, f"{(st[i]['chain'] if t['dir'] == 0 else tot - st[i]['chain']):.1f}", tp] for k, (i, a, b, tp) in enumerate(t['stops'], 1)])
