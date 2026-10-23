"""Where trains that run off the map really start and end (Brendan, 8 October 2026, from the 1948 timetables). Nothing is added to the
timetable: the trip keeps its calls on the map, and gains 'from' / 'to' (the real ends beyond the map), which the page shows when the train is
selected ("Vancouver to Montreal", then "on this map: Vancouver – Wainwright"). In the GTFS feed the trip_headsign becomes the real destination.
Applied by build.py when the page and feed are put together (finish)."""
import csv, io

# trip id -> (real origin or None, real destination or None); None = the end on the map is the real one
REAL = {
    'CN-1': ('Montreal', None), 'CN-2': (None, 'Montreal'),
    'CN-3': ('Toronto', None), 'CN-4': (None, 'Toronto'),
    'CN-5': ('Winnipeg', None), 'CN-6': (None, 'Winnipeg'),
    'CN-9': ('Winnipeg', None), 'CN-10': (None, 'Winnipeg'),
    'CN-11': ('Winnipeg', None), 'CN-12': (None, 'Winnipeg'),
    'CN-M267': ('Loverna', None), 'CN-M268': (None, 'Loverna'),
    'CP-1': ('Montreal', None), 'CP-2': (None, 'Montreal'), 'CP-2E': ('Vancouver', 'Montreal'),
    'CP-3': ('Toronto', None), 'CP-4': (None, 'Toronto'),
    'CP-7': ('Montreal', None), 'CP-8': (None, 'Montreal'),
    'CP-13': ('Chicago', None), 'CP-14': (None, 'Chicago'),
    'CP-51': ('Winnipeg', None), 'CP-52': (None, 'Winnipeg'),
    'CP-M419': ('Wilkie', None), 'CP-M420': (None, 'Wilkie'),
    'CP-M481': ('Macklin', None), 'CP-M480': (None, 'Macklin'),
    'CP-M617': ('Kerrobert', None), 'CP-M618': (None, 'Kerrobert'),
    'CP-M643': ('Shaunavon', None), 'CP-M644': (None, 'Shaunavon'),
    # Washington (Brendan, 9 October 2026). Odd numbers come from the far end, even numbers go to it.
    **{f'{p}-{n}{sfx}': (('Chicago', None) if int(n) % 2 else (None, 'Chicago'))
       for p, ns, sfxs in (('NP', ('1', '2', '3', '4'), ('', '-TAC')), ('GN', ('1', '2', '3', '4'), ('', '-GN')), ('MILW', ('15', '16', '17', '18'), ('', '-TAC')),
                           ('UP', ('17', '18', '105', '106', '11', '12'), ('',)))
       for n in ns for sfx in sfxs},
    'GN-27': ('St. Paul', None), 'GN-28': (None, 'St. Paul'),
    'NP-311': (None, 'Lewiston'), 'NP-313': (None, 'Lewiston'), 'NP-312': ('Lewiston', None), 'NP-314': ('Lewiston', None),
    'UP-67': (None, 'Wallace'), 'UP-68': ('Wallace', None),
    'CPRR-74': (None, 'Lewiston'), 'CPRR-73': ('Lewiston', None),
}
# train names the trips carry beyond those in the tables (Brendan: CN 3 and 4 are also the Continental Limited)
NAMES = {'CN-3': 'The Continental Limited', 'CN-4': 'The Continental Limited',
         # Brendan, 9 October 2026: NP 1 and 2 are always the North Coast Limited; 3 and 4 at this time "The Alaskan" (and their Tacoma sections)
         **{f'NP-{n}{sfx}': nm for n, nm in (('1', 'The North Coast Limited'), ('2', 'The North Coast Limited'), ('3', 'The Alaskan'), ('4', 'The Alaskan'))
            for sfx in ('', '-TAC')}}

def apply(viz, gt):
    seen = set()
    for L in viz.get('lines', []):
        for t in L.get('trips', []):
            if t['id'] in REAL:
                o, d = REAL[t['id']]; seen.add(t['id'])
                if o: t['from'] = o
                if d: t['to'] = d
            if t['id'] in NAMES and not t.get('name'): t['name'] = NAMES[t['id']]
    # Through trains in pieces (Brendan, 15 October 2026): a train shown as two or more trips, one ending where the next of the same number
    # begins (the Saskatchewan and Alberta parts at the boundary; CP No. 2 lying over at Calgary as 2E): the pieces are linked ('next' /
    # 'prev', which the page shows and follows as one train) and each takes the real ends of the whole run, and its name.
    import re as _re
    first = lambda L, t: L['stations'][t['stops'][0][0]]
    last = lambda L, t: L['stations'][t['stops'][-1][0]]
    groups = {}
    for L in viz.get('lines', []):
        if L.get('water'): continue
        for t in L.get('trips', []):
            k = _re.sub(r'(\d)E$', r'\1', _re.sub(r'(-SK[A-Z0-9]+)+$', '', t['id']))
            groups.setdefault(k, []).append((L, t))
    extra = {}
    for k, ps in groups.items():
        if len(ps) < 2: continue
        for XL, x in ps:
            for YL, y in ps:
                if x is y or x.get('next') or y.get('prev') or last(XL, x)['gid'] != first(YL, y)['gid']: continue
                if (y['stops'][0][2] - x['stops'][-1][1]) % 86400 > 20 * 3600: continue        # it must leave within the day (2E: next morning)
                x['next'], y['prev'] = y['id'], x['id']
        byid = {t['id']: (L, t) for L, t in ps}
        for L, t in ps:
            if not (t.get('next') or t.get('prev')): continue
            h = (L, t)
            while h[1].get('prev') in byid and h[1]['prev'] != t['id']: h = byid[h[1]['prev']]
            e = (L, t)
            while e[1].get('next') in byid and e[1]['next'] != t['id']: e = byid[e[1]['next']]
            F = h[1].get('from') or first(*h)['name']; T = e[1].get('to') or last(*e)['name']
            extra[t['id']] = (F, T)
            nm = next((q.get('name') or NAMES.get(q['id']) for _, q in ps if q.get('name') or NAMES.get(q['id'])), None)
            if nm and not t.get('name'): t['name'] = nm
        for L, t in ps:
            if t['id'] in extra: t['from'], t['to'] = extra[t['id']]
    if 'trips.txt' in gt:
        rows = list(csv.reader(io.StringIO(''.join(gt['trips.txt']))))
        h = rows[0]; it, ih, isn = h.index('trip_id'), h.index('trip_headsign'), h.index('trip_short_name') if 'trip_short_name' in h else None
        for r in rows[1:]:
            if r[it] in REAL and REAL[r[it]][1]: r[ih] = REAL[r[it]][1]
            if r[it] in extra and extra[r[it]][1]: r[ih] = extra[r[it]][1]
            if isn is not None and r[it] in NAMES and NAMES[r[it]] not in r[isn]: r[isn] = (r[isn] + ' ' + NAMES[r[it]]).strip()
        out = io.StringIO(); csv.writer(out, lineterminator='\r\n' if gt['trips.txt'][0].endswith('\r\n') else '\n').writerows(rows)
        gt['trips.txt'] = out.getvalue().splitlines(keepends=True)
    return sorted(set(REAL) - seen)
