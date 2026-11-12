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
    _auto_chain(viz, gt)
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
    _spread(viz, extra)
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


# Through trains across timetable files (Brendan, 11 November 2026): a piece that ends where another piece of the same number begins is the same
# train, "same-numbered trains at non-major stations are highly unlikely to not be the same train"; at Montreal and Toronto numbers are reused (CN 1 / 2 are
# both The Maritime Express and The Continental Limited at Montreal), so joins there wait for his rulings (HUB_JOINS). Sections: a train keeps its
# number through a split; a section under a new number is a new train from the split (as Amtrak shows the Empire Builder and its Portland section).
# A join needs: the same number (an M prefix ignored), the same stop, the next piece leaving within 3 hours, the days agreeing (allowing for midnight),
# names that do not differ (no name matches any), not a turnaround (back to where the first came from), and one partner only on each side.
HUBS = ('Montreal',)   # Brendan, 11 Nov 2026: Toronto - Montreal the only same-number places; then the Toronto candidates "are all Toronto through trains".
# Montreal stays held: CN 16 Montreal - Portland, Me. is a different train from No. 16 The Maple Leaf (Detroit - Toronto - Montreal).
HUB_JOINS = set()          # (first trip id, next trip id) ruled by Brendan at the hubs
CPF = {'Canadian Pacific', 'Dominion Atlantic', 'Quebec Central'}
GENERIC = {'', 'local', 'mixed', 'motor train', 'train', 'motor', 'mixed train', 'gas-electric car', 'quebec central', 'dominion atlantic'}

def _cal(gt):
    import csv as _csv, io as _io
    days = {}
    if 'calendar.txt' in gt:
        for r in _csv.DictReader(_io.StringIO(''.join(gt['calendar.txt']))):
            days[r['service_id']] = frozenset(i for i, d in enumerate(('monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday')) if r[d] == '1')
    return days

def _nm(t):
    import re as _re
    n = (t.get('name') or '').strip()
    return '' if n.lower() in GENERIC or n.lower().startswith('canadian ') else _re.sub(r'^the ', '', n, flags=_re.I).lower()

def _auto_chain(viz, gt):
    import re as _re
    cal = _cal(gt); ends, starts = {}, {}
    for L in viz.get('lines', []):
        if L.get('water') or L.get('kind') == 'v': continue
        st = L['stations']
        for t in L.get('trips', []):
            if not t.get('stops') or t.get('svc') not in cal: continue
            num = _re.sub(r'^M', '', str(t.get('num') or ''))
            if not _re.match(r'^\d+$', num): continue
            a, b = st[t['stops'][0][0]], st[t['stops'][-1][0]]
            p = dict(L=L, t=t, num=num, nm=_nm(t), days=cal[t['svc']], a=a, b=b)
            ends.setdefault(b['gid'], []).append(p); starts.setdefault(a['gid'], []).append(p)
    cand = []
    for g, E in ends.items():
        for x in E:
            for y in starts.get(g, []):
                if x['t'] is y['t'] or x['num'] != y['num']: continue
                if x['L']['label'] != y['L']['label'] and not {x['L']['label'], y['L']['label']} <= CPF: continue
                if x['nm'] and y['nm'] and x['nm'] != y['nm']: continue
                if y['b']['gid'] == x['a']['gid']: continue                                    # a turnaround
                ta, td = x['t']['stops'][-1][1], y['t']['stops'][0][2]; gap = (td - ta) % 86400
                if gap > 3 * 3600: continue
                sh = ((ta + gap) // 86400) - (td // 86400)
                if frozenset((d + sh) % 7 for d in x['days']) != y['days']: continue
                hub = any(x['b']['name'].startswith(h) for h in HUBS)
                if hub and (x['t']['id'], y['t']['id']) not in HUB_JOINS: continue
                cand.append((x, y))
    nx, ny = {}, {}
    for x, y in cand: nx[id(x['t'])] = nx.get(id(x['t']), 0) + 1; ny[id(y['t'])] = ny.get(id(y['t']), 0) + 1
    n = 0
    for x, y in cand:
        if nx[id(x['t'])] > 1 or ny[id(y['t'])] > 1 or x['t'].get('next') or y['t'].get('prev'): continue
        x['t']['next'], y['t']['prev'] = y['t']['id'], x['t']['id']; n += 1
    print(f'  real_ends: {n} through-train joins across pieces (same number, not at a hub)')

def _spread(viz, extra):
    """Every linked chain: each piece takes the real ends of the whole run and its name."""
    byid = {t['id']: (L, t) for L in viz.get('lines', []) for t in L.get('trips', [])}
    first = lambda L, t: L['stations'][t['stops'][0][0]]['name']
    last = lambda L, t: L['stations'][t['stops'][-1][0]]['name']
    for L, t in list(byid.values()):
        if not (t.get('next') or t.get('prev')) or t['id'] in extra: continue
        chain = [(L, t)]; seen = {t['id']}
        while chain[0][1].get('prev') in byid and chain[0][1]['prev'] not in seen: chain.insert(0, byid[chain[0][1]['prev']]); seen.add(chain[0][1]['id'])
        while chain[-1][1].get('next') in byid and chain[-1][1]['next'] not in seen: chain.append(byid[chain[-1][1]['next']]); seen.add(chain[-1][1]['id'])
        F = chain[0][1].get('from') or first(*chain[0]); T = chain[-1][1].get('to') or last(*chain[-1])
        nm = next((q.get('name') for _, q in chain if _nm(q)), None)
        for QL, q in chain:
            if q['id'] in extra: continue
            extra[q['id']] = (F, T); q['from'], q['to'] = F, T
            if nm and not _nm(q): q['name'] = nm
