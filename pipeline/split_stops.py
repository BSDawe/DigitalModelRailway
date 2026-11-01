"""Stations with one stop id but far apart (31 October 2026): a name shared by two different places (CP Hammond B.C. and Ont., CN Cardinal Man. and Ont. ...)
had one stop id, so the feed sent trips to the wrong place. Each place more than SPLIT_KM from the first gets its own id (the old id + the line key);
the names on the page stay as they are (Brendan: unique ids, not visible). Applied at assembly, after merge_stations and before real_ends."""
import csv, io, math
SPLIT_KM = 5.0
def km(a, b): return math.hypot((a[0] - b[0]) * 111.32 * math.cos(math.radians((a[1] + b[1]) / 2)), (a[1] - b[1]) * 110.57)
def apply(viz, gt):
    by = {}
    for L in viz.get('lines', []):
        for s in L.get('stations', []):
            if s.get('gid'): by.setdefault(s['gid'], []).append((L['key'], s))
    routes = {r[0].lower() for r in csv.reader(io.StringIO(''.join(gt.get('routes.txt', []))))}
    new = {}; rows = {}; done = []                                        # (line key, old id) -> new id; new id -> stops.txt row
    for g, lst in by.items():
        cl = []                                                           # [(anchor (lon, lat), [line keys], first station)]
        for k, s in lst:
            p = (s['lon'], s['lat'])
            for c in cl:
                if km(c[0], p) <= SPLIT_KM: c[1].append(k); break
            else: cl.append((p, [k], s))
        if len(cl) < 2: continue
        home = next((i for i, c in enumerate(cl) if any(k not in routes for k in c[1])), 0)   # the place of lines whose routes are not named after them (B.C.) keeps the id
        for i, (p, ks, s0) in enumerate(cl):
            if i == home: continue
            nid = f'{g}_{ks[0].upper()}'
            for k in ks: new[(k, g)] = nid
            rows[nid] = [nid, f"{s0['name']} ({ks[0].upper()})", f'{p[1]:.6f}', f'{p[0]:.6f}', s0.get('note', '')]
            done.append(nid)
    if not new: return done
    for L in viz.get('lines', []):
        for s in L.get('stations', []):
            if (L['key'], s.get('gid')) in new: s['gid'] = new[(L['key'], s['gid'])]
    def table(fn): return list(csv.reader(io.StringIO(''.join(gt[fn]))))
    def put(fn, t): buf = io.StringIO(); csv.writer(buf, lineterminator='\n').writerows(t); gt[fn] = buf.getvalue().splitlines(keepends=True)
    tr = table('trips.txt'); h = tr[0]; route_of = {r[h.index('trip_id')]: r[h.index('route_id')].lower() for r in tr[1:] if r}
    st = table('stop_times.txt'); h = st[0]; ti, si = h.index('trip_id'), h.index('stop_id')
    for r in st[1:]:
        if r and (route_of.get(r[ti]), r[si]) in new: r[si] = new[(route_of[r[ti]], r[si])]
    put('stop_times.txt', st)
    sp = table('stops.txt'); have = {r[0] for r in sp[1:] if r}
    sp += [rows[n][:len(sp[0])] for n in rows if n not in have]
    put('stops.txt', sp)
    return done
