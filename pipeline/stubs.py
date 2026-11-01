"""Station stubs (Brendan, 1 November 2026): a station point a little off the track made the route run out to it and back (an in-and-out stub on the
map, the train driving out and back). At assembly the stub is cut out: the station stops on the track where the stub left it, and the chains after it
(viz route, stations, owner segments; GTFS shapes and stop_times shape_dist_traveled) close up. Lines whose route id is not their key (the older B.C.
steps) are left alone. KEEP: real reversals (the Windsor ferry: trains back out of Windsor station to the slip)."""
import csv, io, math
MAX_M = 800.0
KEEP = {('oncn090w', 'Windsor'), ('skcn171', 'Brandon'), ('skcn201', 'Battleford'), ('skcp130a', 'Battleford')}   # real reversals (Brendan, 1 Nov 2026)
def _d(a, b): return math.hypot((a[0] - b[0]) * 111320 * math.cos(math.radians(a[1])), (a[1] - b[1]) * 110540)
def apply(viz, gt):
    def table(fn): return list(csv.reader(io.StringIO(''.join(gt[fn]))))
    def put(fn, t): buf = io.StringIO(); csv.writer(buf, lineterminator='\n').writerows(t); gt[fn] = buf.getvalue().splitlines(keepends=True)
    routes = {r[0] for r in table('routes.txt')[1:] if r}
    fix, done, moved = {}, [], {}
    for L in viz.get('lines', []):
        R = L.get('route') or []
        if L['key'].upper() not in routes or not R or len(R[0]) < 3: continue
        st = L.get('stations', []); cuts = []
        at = {round(p[2], 1): k for k, p in enumerate(R)}
        for s in st[1:-1]:
            if (L['key'], s['name']) in KEEP: continue
            t = at.get(round(s['chain'], 1))
            if t is None: continue
            K = 0
            while t - K - 1 >= 0 and t + K + 1 < len(R) and _d(R[t - K - 1], R[t + K + 1]) < 3.0: K += 1
            if K == 0: continue
            lo, hi = R[t - K][2], R[t + K][2]
            if not (5 < s['chain'] - lo <= MAX_M) or any(lo < c[1] and c[0] < hi for c in cuts): continue
            a, b = t - K - 1, t + K + 1                               # a real reversal (the train comes in on one line and leaves on another the way it came): keep
            while a > 0 and _d(R[a], R[t - K]) < 150: a -= 1              # headings measured over 150 m or more (short pieces are noisy)
            while b < len(R) - 1 and _d(R[b], R[t + K]) < 150: b += 1
            if a >= 0 and b < len(R):
                kx = math.cos(math.radians(R[t][1]))
                u = ((R[t - K][0] - R[a][0]) * kx, R[t - K][1] - R[a][1]); v = ((R[b][0] - R[t + K][0]) * kx, R[b][1] - R[t + K][1])
                nu, nv = math.hypot(*u), math.hypot(*v)
                if nu and nv and (u[0] * v[0] + u[1] * v[1]) / nu / nv < -0.17: continue
            cuts.append((lo, hi, s, t - K))
        if not cuts: continue
        cuts.sort(key=lambda c: c[0])
        def f(c, cuts=cuts):
            sh = 0.0
            for lo, hi, _, _ in cuts:
                if c >= hi - 0.05: sh += hi - lo
                elif c > lo + 0.05: return round(lo - sh, 1)
                else: break
            return round(c - sh, 1)
        acc = R[-1][2]
        for lo, hi, s, base in cuts:
            s['lon'], s['lat'] = R[base][0], R[base][1]; moved[s['gid']] = (s['lon'], s['lat'])
            done.append(f"{L['key']} {s['name']} {round(s['chain'] - lo)} m")
        for s in st: s['chain'] = f(s['chain'])
        L['route'] = [[p[0], p[1], f(p[2])] for p in R if not any(lo + 0.05 < p[2] < hi - 0.05 for lo, hi, _, _ in cuts)]
        for g in L.get('segments', []): g['a'], g['b'] = f(g['a']), f(g['b'])
        fix[L['key'].upper()] = (f, acc, cuts)
    if not fix: return done
    tr = table('trips.txt'); h = tr[0]; ri, ti, di = h.index('route_id'), h.index('trip_id'), h.index('direction_id')
    of = {r[ti]: (r[ri], r[di]) for r in tr[1:] if r}
    stt = table('stop_times.txt'); h = stt[0]; ti2, si = h.index('trip_id'), h.index('shape_dist_traveled')
    for r in stt[1:]:
        if not r or r[ti2] not in of or of[r[ti2]][0] not in fix: continue
        f, acc, _ = fix[of[r[ti2]][0]]; x = float(r[si])
        r[si] = f'{(f(x) if of[r[ti2]][1] == "0" else f(acc) - f(acc - x)):.1f}'
    put('stop_times.txt', stt)
    sh = table('shapes.txt'); out = [sh[0]]; seq = {}
    for r in sh[1:]:
        if not r: continue
        rid, kind = r[0].rsplit('_', 1) if '_' in r[0] else (r[0], '')
        if rid not in fix or kind not in ('OUT', 'IN'): out.append(r); continue
        f, acc, cuts = fix[rid]; x = float(r[4]); c = x if kind == 'OUT' else acc - x
        if any(lo + 0.05 < c < hi - 0.05 for lo, hi, _, _ in cuts): continue
        r[4] = f'{(f(x) if kind == "OUT" else f(acc) - f(acc - x)):.1f}'; r[3] = str(seq.setdefault(r[0], 0)); seq[r[0]] += 1; out.append(r)
    put('shapes.txt', out)
    sp = table('stops.txt')
    for r in sp[1:]:
        if r and r[0] in moved: r[2], r[3] = f'{moved[r[0]][1]:.6f}', f'{moved[r[0]][0]:.6f}'
    put('stops.txt', sp)
    return done
