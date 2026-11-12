"""Trains per week on every piece of Canadian track, in total and by railway, as a GeoJSON line file (Brendan, 11 Nov 2026).

  python3 tools/export_frequency.py [out.geojson]

Reads viz_data.json and gtfs/calendar.txt (run build.py first).
- Left out: boats, the electric interurbans (BCER, Grand River, Lake Erie & Northern, Montreal & Southern Counties, Niagara St. Catharines &
  Toronto, Quebec Railway Light & Power, London & Port Stanley) and track in the United States, except CN's line across northern Minnesota
  (Table 155, Rainy River - Sprague) and CP's line across Maine (Megantic - Vanceboro, with the Brownville Jct. trains).
- A train counts once on each piece of track it runs over, on each day it runs (a daily train is 7 a week, each direction counted).
- One network: every line's track is cut into points about 40 m apart and snapped to the nodes of track already placed (busiest first): within
  SNAP m of any track, or SNAP_OWN m of the same owner's track (two traces of one line can be 100 - 200 m apart), so the same track
  drawn in two files, or two versions of a line, falls onto one set of edges and its trains add up.
- Stubs: where the router runs out to a station off the main track and back, a train's path doubles back on itself; the doubling back is
  taken out (the stub is not counted unless a train ends or starts there).
- Edges with the same counts are joined into long lines.
"""
import json, csv, math, sys, os, collections
from shapely.geometry import LineString
sys.path.insert(0, os.path.dirname(__file__))
from border import in_us, _SEGS

HERE = os.path.join(os.path.dirname(__file__), '..')
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'scratchpad', 'trains_per_week.geojson')
SNAP, SNAP_OWN, STEP = 60.0, 120.0, 40.0
SIMPLIFY = 8.0                                       # m: the lines are thinned to within this of the track          # any track within 60 m is the same; the same railway's track within 250 m
INTERURBAN = set('ewscblnEMNQP')                    # BCER (all its kinds), GRR / LE&N, M&SC, NS&T, QRL&P, L&PS
US_OK = {'skcn155', 'oncp010'}                       # CN through Minnesota, CP through Maine
US_OK_STATIONS = {('oncp012', 'Vanceboro')}          # the CP Maine line's end at Vanceboro, in the Saint John - McAdam file
US_NAMES = ('N.Y.', 'Vt.', 'Mich.', 'Me.', 'Minn.', 'Wash.', 'Mont.', 'N.D.', 'Ida.', 'N.H.', 'Alaska', 'Ohio')
US_NEAR = {'Detroit (Brush Street)', 'Detroit Ferry Slip', 'Baudette', 'Warroad', 'Houlton', 'Vanceboro', 'Skagway'}
CA_NEAR = {'Morrisburg', 'Niagara Falls, Ont.', 'St. Stephen', 'Sault Ste. Marie', 'Missisquoi, Vt.', 'Lac Frontiere', 'Theriault', 'Baker Brook',
           'Estcourt', 'Cyr Junction', 'Martin', 'Clairs', 'Connors'}
GROUP = {'Dominion Atlantic': 'Canadian Pacific', 'Quebec Central': 'Canadian Pacific', 'Esquimalt & Nanaimo': 'Canadian Pacific'}   # as "On the line"
SHORT = {'Canadian National': 'CN', 'Canadian Pacific': 'CP', 'Ontario Northland': 'ONR', 'Northern Alberta Railways': 'NAR',
         'Pacific Great Eastern': 'PGE', 'Algoma Central': 'ACR', 'Newfoundland Railway': 'NFLD', 'White Pass & Yukon Route': 'WPYR',
         'Great Northern': 'GN', 'New York Central (Michigan Central)': 'NYC', 'New York Central': 'NYC', 'Delaware & Hudson': 'DH',
         'Toronto, Hamilton & Buffalo': 'THB', 'Temiscouata': 'TEM', 'Sydney & Louisburg': 'SL', 'Cumberland Railway & Coal': 'CRC',
         'Maritime Coal, Railway & Power': 'MCRP', 'Thousand Islands Railway': 'TIR', 'Roberval & Saguenay': 'RS', 'Alma & Jonquiere': 'AJ',
         'Canada & Gulf Terminal': 'CGT', 'Greater Winnipeg Water District Railway': 'GWWD', 'Spokane International': 'SI',
         'Portage Flyer (North Portage – South Portage)': 'HLB', 'Northern Pacific': 'NP', 'Milwaukee Road': 'MILW', 'Union Pacific': 'UP',
         'Spokane, Portland & Seattle': 'SPS', 'Camas Prairie': 'CPRR', 'Alaska Railroad': 'ARR'}

R_E = 6371000.0
def xy(lon, lat):
    """Mercator, in metres at the equator; a distance there times cos(latitude) is metres on the ground"""
    return R_E * math.radians(lon), R_E * math.log(math.tan(math.pi / 4 + math.radians(lat) / 2))
def gd(lon1, lat1, lon2, lat2):
    """metres between two nearby points"""
    k = math.cos(math.radians((lat1 + lat2) / 2))
    return math.hypot(math.radians(lon2 - lon1) * R_E * k, math.radians(lat2 - lat1) * R_E)
def dist_border_km(lon, lat):
    best, k = 1e9, math.cos(math.radians(lat))
    for a, b, x1, y1, x2, y2 in _SEGS:
        if a - 0.2 > lon or b + 0.2 < lon: continue
        px, py, vx, vy = (lon - x1) * k, lat - y1, (x2 - x1) * k, y2 - y1
        t = max(0, min(1, (px * vx + py * vy) / (vx * vx + vy * vy or 1)))
        best = min(best, math.hypot(px - t * vx, py - t * vy) * 111)
    return best

def station_us(L, s):
    """True for a station in the United States (that is not on one of the two lines kept)"""
    if L['key'] in US_OK or (L['key'], s['name']) in US_OK_STATIONS: return False
    n = s['name']
    if n.startswith('International Boundary'): return False                    # the cut at the border: keep track up to it
    if n in CA_NEAR: return False
    if n in US_NEAR or any(n.endswith(t) or (', ' + t) in n for t in US_NAMES): return True
    if dist_border_km(s['lon'], s['lat']) < 3: return False                  # Natural Earth is rough along the rivers: near it, Canada unless named
    return in_us(s['lon'], s['lat'])

def sub(route, c0, c1):
    """the route between chainages c0 < c1, as [lon, lat]"""
    out = []
    for i in range(len(route) - 1):
        a, b = route[i], route[i + 1]
        if b[2] < c0 or a[2] > c1: continue
        def at(c):
            f = 0 if b[2] == a[2] else (c - a[2]) / (b[2] - a[2])
            return [a[0] + f * (b[0] - a[0]), a[1] + f * (b[1] - a[1])]
        if not out: out.append(at(max(c0, a[2])) if a[2] < c0 else a[:2])
        out.append(at(c1) if b[2] > c1 else b[:2])
    return out

def clip_us(pts, from_ca):
    """the part of pts on the Canadian side, starting from the Canadian end (from_ca: pts[0] is in Canada)"""
    seq = pts if from_ca else pts[::-1]
    out = [seq[0]]
    for p in seq[1:]:
        if in_us(*p) and dist_border_km(*p) > 0.3: break
        out.append(p)
    return out if from_ca else out[::-1]

def main():
    viz = json.load(open(os.path.join(HERE, 'viz_data.json')))
    cal = {}
    for r in csv.DictReader(open(os.path.join(HERE, 'gtfs', 'calendar.txt'))):
        cal[r['service_id']] = sum(r[d] == '1' for d in ('monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'))
    nocal = collections.Counter()
    # ---- pieces: per line, the track between neighbouring station chainages, and the trains over each
    pieces = []                                   # (L, c0, c1, pts)
    trips = []                                    # (railway, weight, [piece ids in order])
    for L in viz['lines']:
        if L.get('water') or L.get('kind') == 'v' or L.get('kind') in INTERURBAN or not L.get('trips'): continue
        rw = GROUP.get(L['label'], L['label'])
        st, route = L['stations'], L['route']
        us = [station_us(L, s) for s in st]
        cuts = sorted({s['chain'] for s in st})
        gat = {}
        for s_ in st: gat.setdefault(s_['chain'], s_.get('gid'))
        pid = {}
        for t in L['trips']:
            w = cal.get(t.get('svc'))
            if not w: nocal[t.get('svc')] += 1; continue
            seq = []
            for (i, *_), (j, *_) in zip(t['stops'], t['stops'][1:]):
                a, b = st[i], st[j]
                if us[i] and us[j]: continue
                lo, hi = sorted((a['chain'], b['chain']))
                ks = [k for k in range(len(cuts) - 1) if cuts[k] >= lo and cuts[k + 1] <= hi]
                if a['chain'] > b['chain']: ks = ks[::-1]
                for k in ks:
                    side = None if not (us[i] or us[j]) else ('a' if us[j] else 'b')     # the Canadian end, when one end is in the US
                    key = (k, side if side else '')
                    if key not in pid:
                        pts = sub(route, cuts[k], cuts[k + 1])
                        if len(pts) < 2: pid[key] = None; continue
                        if side:
                            # only the piece touching the border needs cutting; others between are wholly on one side
                            m = pts[len(pts) // 2]
                            if in_us(*m) and dist_border_km(*m) > 3: pid[key] = None; continue
                            pts = clip_us(pts, from_ca=(side == 'a') == (a['chain'] < b['chain']))
                            if len(pts) < 2: pid[key] = None; continue
                        pid[key] = len(pieces); pieces.append((L['key'], pts, L.get('owner') or L['key'], None if side else gat.get(cuts[k]), None if side else gat.get(cuts[k + 1])))
                    if pid[key] is not None: seq.append((pid[key], a['chain'] > b['chain']))
            if seq: trips.append((rw, w, seq, L['key']))
    # ---- one network: snap every piece onto common nodes, busiest first so they set the geometry
    load = collections.Counter()
    for rw, w, seq, _ in trips:
        for p, _r in seq: load[p] += w
    # ---- the same track in two files: a piece between two stations that another (busier) file already runs between, by way of the same
    # stations or others, at about the same length and in the same place, takes that file's track instead of its own
    import heapq
    def plen(pts): return sum(gd(*p1, *p2) for p1, p2 in zip(pts, pts[1:]))
    CG = collections.defaultdict(list); alias = {}; canon = []
    def find(ga, gb, lim):
        best, h, seen = {ga: 0}, [(0, ga, [])], set()
        while h:
            d, u, path = heapq.heappop(h)
            if u == gb: return d, path
            if u in seen: continue
            seen.add(u)
            for v, q, l, rv in CG[u]:
                nd = d + l
                if nd <= lim and nd < best.get(v, 1e18): best[v] = nd; heapq.heappush(h, (nd, v, path + [(q, rv)]))
        return None
    def near(pts, path):
        qs = [pt for q, _ in path for pt in pieces[q][1][::max(1, len(pieces[q][1]) // 200)]]
        for pt in (pts[len(pts) // 4], pts[len(pts) // 2], pts[3 * len(pts) // 4]):
            if min(gd(*pt, *q) for q in qs) > 1500: return False
        return True
    for p in sorted(range(len(pieces)), key=lambda p: -load[p]):
        lk, pts, own, ga, gb = pieces[p]
        if ga and gb and ga != gb:
            L0 = plen(pts); tol = max(0.04 * L0, 1000)
            r = find(ga, gb, L0 + tol)
            if r and abs(r[0] - L0) <= tol and near(pts, r[1]): alias[p] = r[1]; continue
            l = L0; CG[ga].append((gb, p, l, False)); CG[gb].append((ga, p, l, True))
        canon.append(p)
    def expand(seq):
        out = []
        for p, rev in seq:
            if p in alias:
                a = alias[p]
                out += [(q, not rv) for q, rv in a[::-1]] if rev else list(a)
            else: out.append((p, rev))
        return out
    trips = [(rw, w, expand(seq), lk) for rw, w, seq, lk in trips]
    load = collections.Counter()
    for rw, w, seq, _ in trips:
        for p, _r in seq: load[p] += w
    print(f'{len(alias)} pieces take another file\'s track; {len(canon)} pieces of track')
    nodes, grid, adj = [], collections.defaultdict(list), collections.defaultdict(set)
    GM = SNAP_OWN / math.cos(math.radians(62))         # grid cells in Mercator metres, at least SNAP_OWN on the ground up to 62 N
    def cand(lon, lat, own, me):
        """the nearest node of other pieces: within SNAP, or within SNAP_OWN if the same owner's (None if none), and its distance"""
        x, y = xy(lon, lat); gx, gy = int(x // GM), int(y // GM); best, bd = None, 1e9
        for i in (gx - 1, gx, gx + 1):
            for j in (gy - 1, gy, gy + 1):
                for n in grid[(i, j)]:
                    if npiece[n] == me: continue
                    d = gd(nodes[n][0], nodes[n][1], lon, lat)
                    if d < bd and (d < SNAP or (d < SNAP_OWN and nown[n] == own)): best, bd = n, d
        return best, bd
    def new_node(lon, lat, own, me):
        x, y = xy(lon, lat); n = len(nodes); nodes.append((lon, lat, x, y)); grid[(int(x // GM), int(y // GM))].append(n); npiece.append(me); nown.append(own)
        return n
    def keep_snaps(cs):
        """which snaps to keep. A run of snapped points keeps its ends only while they stay about as close as the run as a whole (so a trace
        that leaves another at a junction leaves where it parts, not by a jump of up to SNAP_OWN); a run never closer than SNAP is kept only
        if it is long (two traces of the same line), not a passing brush with another of the owner's lines."""
        ok = [c[0] is not None for c in cs]
        i = 0
        while i < len(cs):
            if not ok[i]: i += 1; continue
            j = i
            while j < len(cs) and ok[j]: j += 1
            ds = sorted(c[1] for c in cs[i:j]); med = ds[len(ds) // 2]; lim = max(SNAP, med + 50)
            a, b = i, j - 1
            while a <= b and cs[a][1] > lim: ok[a] = False; a += 1
            while b >= a and cs[b][1] > lim: ok[b] = False; b -= 1
            if ds[0] >= SNAP and (j - i) * STEP < 1000:
                for k in range(i, j): ok[k] = False
            i = j
        return ok
    npiece, nown = [], []
    def path(m, n, depth=5):
        """a short way already in the network from m to n"""
        prev, fr = {m: None}, [m]
        for _ in range(depth):
            nf = []
            for u in fr:
                for v in adj[u]:
                    if v in prev: continue
                    prev[v] = u
                    if v == n:
                        out = [n]
                        while prev[out[-1]] is not None: out.append(prev[out[-1]])
                        return out[::-1][1:]
                    nf.append(v)
            fr = nf
        return None
    pnodes = {}
    for p in sorted(canon, key=lambda p: -load[p]):
        pts, own, seq = pieces[p][1], pieces[p][2], []
        dense = []
        for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
            d = gd(x1, y1, x2, y2)
            k = max(1, int(d // STEP))
            dense += [(x1 + (x2 - x1) * f / k, y1 + (y2 - y1) * f / k) for f in range(k)]
        dense.append(tuple(pts[-1]))
        cs = [cand(lon, lat, own, p) for lon, lat in dense]
        ok = keep_snaps(cs)
        for (lon, lat), (c, _), k in zip(dense, cs, ok):
            n = c if k else new_node(lon, lat, own, p)
            if seq and n == seq[-1]: continue
            if seq and n not in adj[seq[-1]]:
                via = path(seq[-1], n)
                if via: seq += via; continue
                adj[seq[-1]].add(n); adj[n].add(seq[-1])
            seq.append(n)
        pnodes[p] = seq
    # ---- stubs that go out to a station and come back by another way (a triangle): where a train's path leaves track near a station and
    # comes back near it within DET_ALONG m (the straight distance under 90% of the way round), and the network has a shorter way between the two points (the
    # main line, or another file's trace of the same track), the train takes that way. Only at the stations along the way, not where the train starts or ends.
    import numpy as np
    DET_W, DET_ALONG = 80, 4000.0
    def short_way(a, b, avoid, lim):
        best, h = {a: 0.0}, [(0.0, a, None)]
        prev = {}
        while h:
            d, u, pu = heapq.heappop(h)
            if d > best.get(u, 1e18): continue
            if u == b:
                out = [b]
                while out[-1] != a: out.append(prev[out[-1]])
                return out[::-1]
            for v in adj[u]:
                if v in avoid: continue
                nd = d + gd(nodes[u][0], nodes[u][1], nodes[v][0], nodes[v][1])
                if nd <= lim and nd < best.get(v, 1e18): best[v] = nd; prev[v] = u; heapq.heappush(h, (nd, v, u))
        return None
    DSTAT = collections.Counter()
    def detours(st, juncs):
        DSTAT['calls'] += 1
        br = [k for k, n in enumerate(st) if len(adj[n]) >= 3]
        if len(br) < 2: return st
        A = [0.0]
        for u, v in zip(st, st[1:]): A.append(A[-1] + gd(nodes[u][0], nodes[u][1], nodes[v][0], nodes[v][1]))
        cands = []
        for x, i in enumerate(br):
            for j in br[x + 1:]:
                al = A[j] - A[i]
                if al > DET_ALONG: break
                if al < 300 or j - i < 3: continue
                D = gd(nodes[st[i]][0], nodes[st[i]][1], nodes[st[j]][0], nodes[st[j]][1])
                if D < 0.9 * al: cands.append((D / al, i, j, al))
        onpath, taken, rep = set(st), [], []
        for _, i, j, al in sorted(cands)[:300]:
            if any(not (j <= a or i >= b) for a, b in taken): continue
            DSTAT['try'] += 1
            alt = short_way(st[i], st[j], (), al - 50)
            if alt and alt != st[i:j + 1] and not (set(alt[1:-1]) - set(st[i:j + 1])) & onpath:
                taken.append((i, j)); rep.append((i, j, alt)); DSTAT['done'] += 1
        for i, j, alt in sorted(rep, reverse=True): st = st[:i] + alt + st[j + 1:]
        return st
    # ---- each train's path, with the doubling back at stubs taken out; count each edge once per train
    edge = collections.defaultdict(collections.Counter); esrc = collections.defaultdict(set)
    cache = {}
    for rw, w, seq, lk in trips:
        key = tuple(seq)
        if key not in cache:
            st, jn = [], []
            for p, rev in seq:
                ns = pnodes[p][::-1] if rev else pnodes[p]
                for n in ns:
                    if st and n == st[-1]: continue
                    if len(st) >= 2 and n == st[-2]: st.pop(); continue
                    st.append(n)
                jn.append(st[-1] if st else None)
            st = detours(st, set(jn[:-1]))
            cache[key] = {tuple(sorted(e)) for e in zip(st, st[1:])}
        for e in cache[key]: edge[e][rw] += w; esrc[e].add(lk)
    print(f"stub detours replaced: {DSTAT['done']}")
    # ---- join edges with the same counts into lines
    g = collections.defaultdict(list)
    for (a, b) in edge: g[a].append(b); g[b].append(a)
    sig = {e: tuple(sorted(c.items())) for e, c in edge.items()}
    src_of = {}
    used, feats = set(), []
    def walk(a, b):
        line, s = [a, b], sig[tuple(sorted((a, b)))]
        used.add(tuple(sorted((a, b))))
        while len(g[line[-1]]) == 2:
            nx = [v for v in g[line[-1]] if v != line[-2]]
            if not nx: break
            e = tuple(sorted((line[-1], nx[0])))
            if e in used or sig[e] != s: break
            used.add(e); line.append(nx[0]); src_of.setdefault(id(line), set()).update(esrc[e])
        return line, s
    starts = [n for n in g if len(g[n]) != 2] + list(g)
    for a in starts:
        for b in g[a]:
            if tuple(sorted((a, b))) in used: continue
            ln, s = walk(a, b)
            # extend backwards too, when a started mid-run
            back, _ = (walk(a, [v for v in g[a] if v != b][0]) if len(g[a]) == 2 and tuple(sorted((a, [v for v in g[a] if v != b][0]))) not in used
                       and sig[tuple(sorted((a, [v for v in g[a] if v != b][0])))] == s else ([a], None))
            ln = back[::-1] + ln[1:]
            c = dict(s); tot = sum(c.values())
            srcs = set().union(*(esrc[tuple(sorted(q))] for q in zip(ln, ln[1:])))
            props = {'trains_wk': tot, 'trains_day': round(tot / 7, 1), 'railways': ', '.join(f'{SHORT.get(k, k)} {v}' for k, v in sorted(c.items(), key=lambda kv: -kv[1])), 'files': ' '.join(sorted(srcs))}
            for k, v in c.items(): props[SHORT.get(k, k)] = v
            xs = [(nodes[n][2], nodes[n][3]) for n in ln]
            keep = LineString(xs).simplify(SIMPLIFY / math.cos(math.radians(nodes[ln[0]][1]))).coords if len(xs) > 2 else xs
            ks = {xy_: k for k, xy_ in enumerate(xs)}
            coords = [[round(nodes[ln[ks[tuple(q)]]][0], 5), round(nodes[ln[ks[tuple(q)]]][1], 5)] for q in keep]
            feats.append({'type': 'Feature', 'properties': props, 'geometry': {'type': 'LineString', 'coordinates': coords}})
    cols = sorted({k for f in feats for k in f['properties'] if k not in ('trains_wk', 'trains_day', 'railways', 'files')})
    for f in feats:
        for k in cols: f['properties'].setdefault(k, 0)
    json.dump({'type': 'FeatureCollection', 'features': feats}, open(OUT, 'w'), separators=(',', ':'))
    km = sum(gd(*p, *q) for f in feats for p, q in zip(f['geometry']['coordinates'], f['geometry']['coordinates'][1:])) / 1000
    print(f'{OUT}: {len(feats)} lines, {km:,.0f} km, {len(nodes)} nodes; railways: {", ".join(cols)}; trips without a calendar: {dict(nocal)}')

if __name__ == '__main__': main()
