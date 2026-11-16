"""One spelling for one place (Brendan, 16 Nov 2026). Two railways, or a railway and a steamer line, sometimes print the same place differently
("Cutknife" CP, "Cut Knife" CN). The timetable files keep the name as printed; here, at assembly, the page and the GTFS feed get one spelling.
Only the same place under two spellings is listed, not different places with like names (LaSalle, Que. and La Salle, Man.)."""
SAME = {'Cloverbar': 'Clover Bar', 'Cutknife': 'Cut Knife', 'Grand Mere': "Grand'Mere", 'Port-aux-Basques': 'Port aux Basques'}
def apply(viz, gt):
    n = 0
    for L in viz.get('lines', []):
        for s in L.get('stations', []):
            if s.get('name') in SAME: s['name'] = SAME[s['name']]; n += 1
        for k in ('label', 'long'):
            for a, b in SAME.items():
                if isinstance(L.get(k), str) and a in L[k]: L[k] = L[k].replace(a, b)
    for fn in ('stops.txt', 'trips.txt', 'routes.txt'):
        if fn in gt:
            out = []
            for l in gt[fn]:
                for a, b in SAME.items():
                    if a in l: l = l.replace(a, b)
                out.append(l)
            gt[fn] = out
    return n
