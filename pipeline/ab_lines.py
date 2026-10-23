"""Alberta secondary and branch lines: the shared machinery (a helper, not a build step: the steps ab_cn_build.py, ab_cp_build.py and
ab_nar_build.py import it).

A line is given as a list of legs, each a slice of a transcribed table (ab_*.csv, read by ab_table.py), joined end to end. For each line:
  1. every station that can be located gets a point: a station already on the map, a point given by hand, or the place of that name in the
     federal names file (places/cgn_ab_places.csv, Brendan, October 2026);
  2. between each pair of located stations the track is found in the national network (nrwn/alberta_all.json), with the Canadian Northern and
     Grand Trunk Pacific backup sets and Brendan's traces for track the network no longer has (CN and Northern Alberta lines only). The track
     is accepted when its length agrees with the printed miles; otherwise the two stations are joined by a STRAIGHT LINE, which the page draws
     dashed (segment 'est'), and the stretch is listed in the step's log;
  3. stations with no point of their own are put at their printed mileage between their neighbours;
  4. track already drawn by a line built earlier is not drawn twice (segment owner 'none').
Times in the tables are Mountain time: trips are made an hour earlier, in Pacific time, like the rest of the map."""
import csv, json, math, os, re
import xml.etree.ElementTree as ET
import numpy as np, networkx as nx
from pyproj import Transformer
from scipy.spatial import cKDTree
from shapely.geometry import LineString, Point
from shapely.strtree import STRtree
import ab_table
from backup_track import lines as backup_lines
HERE = os.path.dirname(os.path.abspath(__file__)); GT = os.path.join(HERE, 'gtfs'); MI = 1609.344
_T = Transformer.from_crs(4326, 26910, always_xy=True); _I = Transformer.from_crs(26910, 4326, always_xy=True)
fwd, inv = _T.transform, _I.transform
NS = '{http://www.opengis.net/kml/2.2}'
norm = lambda n: re.sub(r'\bso\.', 'south', n.lower()).replace('junc.', 'junction').strip()
ALIAS = {'hay lake': 'hay lakes', 'roundhill': 'round hill', 'athabaska': 'athabasca', 'greencourt': 'green court', 'dewinton': 'de winton', 'macleod': 'fort macleod',
         'hillspring': 'hill spring', 'cloverbar': 'clover bar', 'nemiscam': 'nemiskam', 'hobbema': 'maskwacis', "bull's head": 'bullshead', 'townlake': 'town lake',
         'matziwin': 'matzhiwin', 'bull pound': 'bullpound', 'benton': 'benton station'}
# points given by hand: (railway, station) -> lon, lat. Stations in the cities, which the names file gives only as a city centre.
HAND = {('cp', 'edmonton'): (-113.5090, 53.5395),           # the CP station, 109 Street south of Jasper Avenue, reached over the High Level Bridge
        ('cp', 'south edmonton'): (-113.4962, 53.5168),     # Strathcona station
        ('cn', 'calgary'): (-114.0655, 51.0370),            # the CN station, 18 Avenue at 1 Street S.W.
        ('cp', 'medicine hat'): (-110.6775, 50.0414),
        ('cn', 'camrose'): (-112.8206, 53.0184),            # the Canadian Northern station, 47 Avenue
        ('cn', 'hemaruka'): (-111.088742, 51.779578),       # Brendan, 4 October 2026: a point on the visible old right of way at the wye (51 46 46.48 N, 111 05 19.47 W)
        ('cp', 'jaydot'): (-110.076734, 49.248038),         # 8.3 printed miles on from Cressday along Brendan's Jaydot - Foremost trace (7 October 2026)
        ('cn', 'lloydminster'): (-110.005968, 53.284654),       # Brendan, 16 October 2026: the CN station
        ('cp', 'lloydminster'): (-110.003357, 53.285637),       # Brendan, 16 October 2026: the CP station
        ('cp', 'schuler'): (-110.09927, 50.337),             # end of the spur from Pivot (Brendan, 17 Oct 2026: the town point is in a lake)
        ('nar', 'waterways'): (-111.3370, 56.6970, 20000)}  # the old end of steel beside Fort McMurray (approximate): beyond where the track ends today

# Brendan's traces in traces/alberta_railway_bits.kml, by their order in the file, for each railway's graph:
#  0 CP via Strathmore, 1 CP Edmonton High Level Bridge, 2 Red Deer old CP line through town ("bypass (est)"), 3 CN downtown Red Deer access
#  over CP (after 1941), 4 CN to Red Deer wye, 5 Hines Creek, 6 Waterways, 7 Luscar, 8 Mountain Park, 9 Carbondale - Egremont, 10 CP Rocky
#  Mountain House, 11 High River - Macleod, 12 Glenwood - Raymond, 13 Turin, 14 Jaydot - Foremost, 15 Langdon - Wimborne, 16 Mossleigh -
#  Suffield, 17 Suffield wye, 18 Rimbey, 19 Warden Jct, 20 Warden - Hanna, 21 the Hemaruka line, 22 Empress - Irricana, 23 Rosemary - Rosedale
#  (CP; Trefoil - Rosedale joint with CN), 24 Cosway wye, 25 Cosway - Kneehill, 26 Botha - Compeer, 27 Star - Lloydminster,
#  28 Willingdon - Vegreville, 29 St. Paul - Heinsburg, 30 Abilene - Beaver River
BITS = {'cp': {0, 1, 2, 10, 11, 12, 13, 14, 15, 16, 17, 18, 22, 23, 24, 25, 26, 27, 28},
        'cn': {2, 3, 4, 5, 6, 7, 8, 9, 19, 20, 21, 23, 29, 30}}
# the CPR's running rights over the CN, Kneehill - Drumheller - Rosedale (1927): CN track in this box is in the CP graph too
CP_OVER_CN = (-112.80, -112.60, 51.39, 51.50)
BIT_OWNER = {2: 'cp'}                                          # a trace in another railway's graph that is that railway's track (drawn in its colour)
# the CN into its downtown Red Deer station over CP track (after 1941; Brendan): CP track in this box is in the CN graph too
CN_OVER_CP = (-113.84, -113.78, 52.3145, 52.36)
# track in the network that was built after 1948 and replaces track Brendan has traced: left out of both graphs (the CP's Red Deer bypass;
# the 1948 line through town is his trace 2)
LATER = [(-113.875, -113.8275, 52.2345, 52.3145)]
def _in(c, box): return all(box[0] <= p[0] <= box[1] and box[2] <= p[1] <= box[3] for p in c)

NOPLACE = {('cn', 'north edmonton')}                     # the names file's point is not the station: placed by its mileage
def _xy(pts):
    a = np.asarray(pts, float); x, y = _T.transform(a[:, 0], a[:, 1]); return list(zip(x.tolist(), y.tolist()))
def _kml(fn): return [[tuple(map(float, t.split(',')[:2])) for t in c.text.split()] for c in ET.parse(os.path.join(HERE, 'traces', fn)).iter(NS + 'coordinates')]
def _wkt(fn):
    return [[tuple(map(float, p.split()[:2])) for p in part.split(',')] for part in re.findall(r'\(([-\d., ]+)\)', open(os.path.join(HERE, 'traces', fn)).read())]

# ---------------------------------------------------------------- railways, and hooks for other regions (wa_lines.py)
# rail -> kind (page badge), label, owner (track colour), GTFS agency and colour, trip id prefix
RAILS = {'cn': dict(kind='q', label='Canadian National', own='cn', agency='CN', color='2F6B44', pfx='CN'),
         'cp': dict(kind='p', label='Canadian Pacific', own='cp', agency='CP', color='7A1E2C', pfx='CP'),
         'nar': dict(kind='a', label='Northern Alberta Railways', own='nar', agency='NAR', color='2C4F86', pfx='NAR')}
TZ_SHIFT = {'C': -7200, 'M': -3600, 'P': 0}                          # printed zone -> seconds to Pacific time
OWN_APART = {'np', 'up', 'milw', 'gn', 'sps'}                      # the Washington railways: parallel lines of two of them are both drawn
EXT_GRAPH, EXT_PLACE, EXT_GID = {}, {}, {}            # graph key -> function building (G, nodes, tree); rail -> function(name, own) -> place or None
# ---------------------------------------------------------------- the track graph
_key = lambda p: (round(p[0], 1), round(p[1], 1))
_G = {}
def graph(rail):
    """rail 'cn' (also used for the Northern Alberta) or 'cp'. Track of the other big railway is left out, so a train is never sent over it."""
    rail = 'cn' if rail == 'nar' else rail
    if rail in _G: return _G[rail]
    if rail in EXT_GRAPH: _G[rail] = EXT_GRAPH[rail](); return _G[rail]
    other = 'Canadian Pacific' if rail == 'cn' else 'Canadian National'
    def feed(add):
        for f in json.load(open(os.path.join(HERE, 'nrwn', 'alberta_all.json'))):
            if not f['schema'].endswith('Track'): continue
            fac = {'Main': 1.0, 'Connecting': 1.0, 'Siding': 1.3}.get(f['data'].get('trackClassification'), 1.5)
            if f['data'].get('operatorEnglishName', f['data'].get('ownerEnglishName')) == other:
                box = CP_OVER_CN if rail == 'cp' else CN_OVER_CP
                for c in f['coords']:                                     # only the other railway's track inside the running-rights box
                    run = []
                    for p in c + [None]:
                        if p is not None and _in([p], box): run.append(p); continue
                        if len(run) > 1: add(_xy(run), fac, 'n', 'cn' if rail == 'cp' else 'cp')     # the other railway's track, drawn in its colour
                        run = []
                continue
            for c in f['coords']:
                run = []
                for p in c + [None]:
                    if p is not None and not any(_in([p], b) for b in LATER): run.append(p); continue
                    if len(run) > 1: add(_xy(run), fac, 'n')
                    run = []
        if rail == 'cn':                                                  # backups and traces: only where the network has nothing (they cost a little more)
            for which in ('cnor', 'gtp'):
                for _n, _d, pts in backup_lines(which, box=(-120.2, -109.9, 48.9, 60.0)): add(_xy(pts), 1.2, 'b')
            for c in _kml('edmonton_terminal.kml') + _kml('nar_watino.kml') + _wkt('nar_barrhead_branch.tsv'): add(_xy(c), 1.0, 't')
        for i, c in enumerate(_kml('alberta_railway_bits.kml')):          # Brendan's Alberta traces (7 October 2026): each to the graph of the railway that used it
            if i in BITS[rail]: add(_xy(c), 1.0, 't', BIT_OWNER.get(i) if BIT_OWNER.get(i) != rail else None)
    _G[rail] = make_graph(feed)
    return _G[rail]

def make_graph(feed, tie_end=40, tie_loose=30, tie_each=False):
    """feed(add) adds the lines: add(points in UTM 10N metres, weight factor, source 'n' network / 'b' backup / 't' trace, owner or None).
    Returns (G, nodes, tree), with loose ends and traces tied to track they run beside."""
    G = nx.Graph(); fid = [0]; loose = []                             # loose: the points of the backups and traces, to be tied to track they run beside
    def dens(pts, step=150.0):
        out = [pts[0]]
        for q in pts[1:]:
            p = out[-1]; n = int(math.dist(p, q) // step)
            out += [(p[0] + (q[0] - p[0]) * k / (n + 1), p[1] + (q[1] - p[1]) * k / (n + 1)) for k in range(1, n + 1)] + [q]
        return out
    def add(pts, fac, src, own=None):
        fid[0] += 1
        pts = dens(pts, 200.0 if src == 'n' else 150.0)                 # no long gaps between points: a station snaps to the nearest one
        if src != 'n': loose.extend((_key(p), fid[0]) for p in pts)
        for a, b in zip(pts, pts[1:]):
            ka, kb = _key(a), _key(b); d = math.dist(a, b)
            if ka != kb and (not G.has_edge(ka, kb) or G[ka][kb]['w'] > d * fac): G.add_edge(ka, kb, w=d * fac, len=d, src=src, fid=fid[0], own=own)
    feed(add)
    # ties: (1) loose ends of the network to track passing within 40 m; (2) every point of a backup line or trace to other track within 30 m, so a
    # route can leave the network for the backup wherever the network stops, and come back where it starts again
    edges = list(G.edges(data=True)); geoms = [LineString([u, v]) for u, v, _ in edges]; tree = STRtree(geoms); splits = {}
    def tie(n, radius, skip, each=False):
        # each (tie_each): to the nearest edge of every other line within reach, not only the nearest one (Saskatchewan, 16 October 2026: a backup
        # line lying on another backup tied only to that one and never to the network beside both)
        P = Point(n); best = {}
        for i in tree.query(P.buffer(radius)):
            u, v, att = edges[i]
            if n in (u, v) or skip(u, v, att): continue
            d = geoms[i].distance(P); k = att['fid'] if each else 0
            if d <= radius and (k not in best or d < best[k][0]): best[k] = (d, i)
        for d, i in best.values(): splits.setdefault(i, []).append((geoms[i].project(P), n, d))
    for n in [n for n in G if G.degree(n) == 1]:
        close = nx.single_source_dijkstra_path_length(G, n, cutoff=max(250, 3 * tie_end), weight='len')
        tie(n, tie_end, lambda u, v, att: u in close or v in close)
    for n, f in dict(loose).items(): tie(n, tie_loose, lambda u, v, att, f=f: att['fid'] == f, tie_each)
    for i, hits in splits.items():
        u, v, att = edges[i]; L = geoms[i].length; fac = att['w'] / att['len']; prev, pd = u, 0.0
        if G.has_edge(u, v): G.remove_edge(u, v)
        for t, n, d in sorted(hits):
            p = _key(geoms[i].interpolate(t).coords[0])
            if p != prev and t - pd > 0.05: G.add_edge(prev, p, w=(t - pd) * fac, len=t - pd, src=att['src'], fid=att['fid'], own=att.get('own')); prev, pd = p, t
            if n != prev and not G.has_edge(n, prev): G.add_edge(n, prev, w=max(d, 0.1), len=max(d, 0.1), src='join', fid=0)
        if prev != v: G.add_edge(prev, v, w=(L - pd) * fac, len=L - pd, src=att['src'], fid=att['fid'], own=att.get('own'))   # keep whose track it is
    nodes = list(G.nodes)
    return (G, nodes, cKDTree(np.array(nodes)))

def snap(rail, xy, radius):
    G, nodes, tree = graph(rail); d, i = tree.query(xy)
    return (nodes[i], float(d)) if d <= radius else (None, float(d))

def path(rail, a, b, limit):
    """track from node a to node b no longer than limit metres (weighted), or None"""
    G = graph(rail)[0]
    try: _, p = nx.single_source_dijkstra(G, a, target=b, cutoff=limit, weight='w')
    except (nx.NetworkXNoPath, KeyError): return None
    return p

# ---------------------------------------------------------------- where the stations are
_P = {}
def _places():
    if _P: return _P
    _P['cgn'] = {}
    for r in csv.DictReader(open(os.path.join(HERE, 'places', 'cgn_ab_places.csv'))):
        _P['cgn'].setdefault(r['name'].lower(), (float(r['lon']), float(r['lat']), r['kind']))
    _P['viz'] = {}
    for L in json.load(open(os.path.join(HERE, 'viz_data.json')))['lines']:
        west = {'cn': -118.6, 'cp': -116.3, 'cr': -114.75, 'nar': -120.0}.get(L['key'])       # the Alberta part of each line the new ones meet
        if west is None: continue                                   # (not the Alberta lines themselves: they are placed afresh each time)
        for s in L['stations']:
            if s['lon'] > west: _P['viz'].setdefault((L['owner'], norm(s['name'])), (s['lon'], s['lat'], s['gid']))
    return _P
def place(rail, name, own=None):
    """-> (lon, lat, how, radius within which track is looked for), or None. how: 'map' (a station already on the map), 'hand', or the kind of place"""
    if own and name in own: return (*own[name], 'hand', 600)
    if rail in EXT_PLACE: return EXT_PLACE[rail](name)
    n = norm(name); P = _places()
    if (rail, n) in HAND: h = HAND[(rail, n)]; return (h[0], h[1], 'hand', h[2] if len(h) > 2 else 600)
    if (rail, n) in P['viz']: return (*P['viz'][(rail, n)][:2], 'map', 150)
    if rail == 'nar' and ('cn', n) in P['viz'] and n == 'edmonton': return (*P['viz'][('cn', n)][:2], 'map', 150)
    c = P['cgn'].get(ALIAS.get(n, n))
    if c and (rail, n) not in NOPLACE: return (c[0], c[1], c[2], 4000 if c[2] == 'City' else 2500)
    return None
def gid_for(rail, name):
    if rail in EXT_PLACE: return EXT_GID.get((rail, name)) or RAILS[rail]['pfx'] + '_' + re.sub(r'\W+', '_', name.upper()).strip('_')
    n = norm(name); P = _places()
    if (rail, n) in P['viz']: return P['viz'][(rail, n)][2]
    if rail == 'nar' and n == 'edmonton': return 'CN_EDMONTON'
    return rail.upper() + '_' + re.sub(r'\W+', '_', name.upper().replace('SO.', 'SOUTH').replace('JUNC.', 'JUNCTION')).strip('_')

# ---------------------------------------------------------------- a line from its legs
def rows_of(spec):
    """the stations of a line in order, from its legs: [dict(name, mile, run, principal, cells={col: [parsed cells in leg order]})], and the trains"""
    rows, trains = [], {}
    for leg in spec['legs']:
        tab = ab_table.load(os.path.join(HERE, leg['csv'])); R = tab['rows']; names = [norm(r['station']) for r in R]
        i0 = names.index(norm(leg['a'])) if leg.get('a') else 0
        i1 = (len(names) - 1 - names[::-1].index(norm(leg['b']))) if leg.get('b') else len(R) - 1
        part = R[min(i0, i1):max(i0, i1) + 1]
        if i0 > i1: part = part[::-1]
        for tr in tab['trains']:
            if spec.get('cols') and tr['col'] not in spec['cols']: continue
            along = (tr['dir'] == 'down') != (i0 > i1)
            t = trains.setdefault(tr['col'], dict(tr, along=along))
            assert t['along'] == along, (spec['key'], tr['col'])
        for k, r in enumerate(part):
            cells = {c: ab_table.cell(r.get(c, '')) for c in trains if c in r}
            cells = {c: v for c, v in cells.items() if v}
            name = r['station'].replace('Junc.', 'Junction').replace('So. ', 'South ')
            if k == 0 and rows and norm(rows[-1]['name']) == norm(name):             # the join: the same station ends one leg and begins the next
                for c, v in cells.items(): rows[-1]['cells'].setdefault(c, []).append(v)
                if r.get('tz') and rows[-1].get('tz') and r['tz'] != rows[-1]['tz']: rows[-1]['tz'] += '/' + r['tz']   # two tables meeting where the time changes (Broadview)
                rows[-1]['pm'] = r['mile']; continue
            run = 0.0 if not rows else rows[-1]['run'] + abs(r['mile'] - (part[k - 1]['mile'] if k else rows[-1]['pm']))
            rows.append(dict(name=name, mile=r['mile'], pm=r['mile'], run=run, principal=r['principal'] == '1', cells={c: [v] for c, v in cells.items()}, src=leg['csv'],
                             tz=r.get('tz'), prov=r.get('prov')))
    trains = {c: t for c, t in trains.items() if sum(c in r['cells'] for r in rows) >= 2}
    for after, name, miles in spec.get('via', ()):                    # a point the line passes that is not a station (a junction): after a station, so many miles on
        i = next(k for k, r in enumerate(rows) if r['name'] == after)
        rows.insert(i + 1, dict(name=name, mile=rows[i]['mile'], pm=rows[i]['pm'], run=rows[i]['run'] + miles, principal=False, cells={}, src=''))
    return rows, trains

def trace(spec, log=print):
    """-> rows (each with 'xy' and 'd', metres along the line), pieces [(coords, est)], for the line"""
    rail = spec['rail']; gk = spec.get('graph', rail); rows, trains = rows_of(spec)
    for r in rows:
        p = place(rail, r['name'], spec.get('places'))
        if p and r['name'] not in spec.get('noplace', ()):
            r['raw'] = fwd(p[0], p[1]); r['how'] = p[2]; r['node'], r['off'] = snap(gk, r['raw'], p[3])
    A = [i for i, r in enumerate(rows) if 'raw' in r]
    missing = [r['name'] for r in (rows[0], rows[-1]) if 'raw' not in r]
    if missing: raise SystemExit(f"{spec['key']}: no position for the end station(s) {missing}")
    # a located station much farther from its located neighbours than the printed miles allow is the wrong place of that name: leave it to its mileage
    far = lambda m, o: math.dist(m['raw'], o['raw']) > abs(m['run'] - o['run']) * MI * 1.10 + 2500
    while True:
        bad = {}
        for k in range(len(A) - 1):
            if far(rows[A[k]], rows[A[k + 1]]): bad[k] = bad.get(k, 0) + 1; bad[k + 1] = bad.get(k + 1, 0) + 1
        bad = {k: v for k, v in bad.items() if 0 < k < len(A) - 1 and rows[A[k]]['how'] not in ('map', 'hand')}
        if not bad: break
        k = max(bad, key=lambda k: (bad[k], -abs(k - len(A) / 2))); m = rows[A[k]]
        log(f"    ?? {m['name']} ({m['how']}) does not fit its neighbours' miles ({math.dist(m['raw'], rows[A[k - 1]]['raw']) / MI:.1f} mi from {rows[A[k - 1]]['name']}, printed {abs(m['run'] - rows[A[k - 1]]['run']):.1f}): its position is not used")
        for f in ('raw', 'how', 'node', 'off'): m.pop(f, None)
        A.pop(k)
    G = graph(gk)[0]
    def fit(a, b, extra=0.0):
        """the track between two located stations, if its length agrees with the printed miles"""
        dm = abs(b['run'] - a['run']) * MI
        if not (a.get('node') and b.get('node')) or a['node'] == b['node']: return None
        forced = bool({(a['name'], b['name']), (b['name'], a['name'])} & set(spec.get('force', ())))
        p = path(gk, a['node'], b['node'], max((dm * 1.25 + 4000 + a['off'] + b['off']) * 1.5, 40000 if forced else 0))
        ok = lambda p: p and (abs(LineString(p).length + extra - dm) <= max(0.15 * dm, 2000) + a['off'] + b['off'] or forced)
        if ok(p): return p
        if gk.startswith('sk:'):                                      # Saskatchewan (17 October 2026): the shortest track by distance, when the cheapest
            try: q = nx.shortest_path(G, a['node'], b['node'], weight='len')    # route (over the network) is not the one the printed miles describe
            except nx.NetworkXNoPath: q = None
            if ok(q): return q
    weak = lambda r: r['how'] not in ('map', 'hand')
    # a place whose point is off the station (a junction outside its village): if the track fits from its neighbours to each other but not to it, it goes by its mileage
    k = 1
    while k < len(A) - 1:
        a, m, b = rows[A[k - 1]], rows[A[k]], rows[A[k + 1]]
        if m['how'] != 'hand' and (m['node'] or m['off'] < 6000) and a.get('node') and b.get('node') and not (fit(a, m) and fit(m, b)) and fit(a, b):
            log(f"    {m['name']}: the track fits between {a['name']} and {b['name']} but not to the point for {m['name']}; placed by its mileage")
            for f in ('raw', 'how', 'node', 'off'): m.pop(f, None)
            A.pop(k)
        else: k += 1
    # track that ends short of a place (the line beyond is gone): the track is used to its end, and a straight line from there to the place
    k = 0
    while k < len(A):
        m = rows[A[k]]
        if m['how'] != 'map' and m['node'] and m['off'] > 700 and G.degree(m['node']) == 1:
            end = dict(name='(end of track)', mile=m['mile'], pm=m['pm'], principal=False, cells={}, src='', raw=m['node'], how='hand', node=m['node'], off=0.0)
            sides = []
            for side in (-1, 1):
                if 0 <= k + side < len(A):
                    o = rows[A[k + side]]; e = dict(end, run=m['run'] + side * m['off'] / MI)
                    if (e['run'] - o['run']) * side < 0 and fit(o, e): sides.append((side, e))
            if sides: m['node'] = None
            for side, e in sorted(sides, reverse=True):                 # the far side first, so the nearer index stays good
                i = A[k] + 1 if side > 0 else A[k]; rows.insert(i, e)
                A[:] = [x + (x >= i) for x in A]; A.insert(k + 1 if side > 0 else k, i)
                if side < 0: k += 1
            k += len([1 for side, _ in sides if side > 0])
        k += 1
    pieces, d = [], 0.0; rows[A[0]]['d'] = 0.0
    pt = lambda r: r['node'] if r['node'] else r['raw']
    for ia, ib in zip(A, A[1:]):
        a, b = rows[ia], rows[ib]; dm = (b['run'] - a['run']) * MI
        coords = fit(a, b); est = coords is None
        if est: coords = [pt(a), pt(b)]
        owns = [None] * (len(coords) - 1) if est else [G[u][v].get('own') if G.has_edge(u, v) else None for u, v in zip(coords, coords[1:])]
        L = LineString(coords).length if coords[0] != coords[-1] else 0.0
        pieces.append(dict(coords=coords, est=est, a=ia, b=ib, len=L, dm=dm, owns=owns))
        for i in range(ia + 1, ib + 1): rows[i]['d'] = d + (L * (rows[i]['run'] - a['run']) / (b['run'] - a['run']) if b['run'] > a['run'] else L)
        d += L
    return rows, trains, pieces

def report(spec, rows, pieces, log=print):
    tot = sum(p['len'] for p in pieces) / MI; pm = rows[-1]['run']; est = [p for p in pieces if p['est']]
    log(f"  {spec['key']:9s} {rows[0]['name']} - {rows[-1]['name']}: {tot:.1f} mi traced, {pm:.1f} printed; "
        + (f"{sum(p['len'] for p in est) / MI:.1f} mi straight estimate" if est else 'all on track')
        + (f"; by mileage only: {', '.join(r['name'] for r in rows if 'raw' not in r)}" if any('raw' not in r for r in rows) else ''))
    run = []
    for p in pieces:
        if p['est'] and run and run[-1][1] == p['a']: run[-1][1] = p['b']; run[-1][2] += p['len']; run[-1][3] += p['dm']
        elif p['est']: run.append([p['a'], p['b'], p['len'], p['dm']])
    for a, b, L, dm in run: log(f"      straight: {rows[a]['name']} - {rows[b]['name']}  {L / MI:.1f} mi (printed {dm / MI:.1f})")
    for p in pieces:
        if p['est'] and p['len'] < 0.8 * p['dm'] - 800: log(f"      short: {rows[p['a']]['name']} - {rows[p['b']]['name']} straight {p['len'] / MI:.1f} mi, printed {p['dm'] / MI:.1f}")
    for p in pieces:
        if not p['est'] and abs(p['len'] - p['dm']) > max(0.06 * p['dm'], 900): log(f"      note: {rows[p['a']]['name']} - {rows[p['b']]['name']} track {p['len'] / MI:.1f} mi, printed {p['dm'] / MI:.1f}")

# ---------------------------------------------------------------- trips
def svc_of(days): return 'W_' + ''.join(map(str, days))
def trips_of(spec, rows, trains, stn_index, taken, log=print):
    out = []; pfx = RAILS[spec['rail']]['pfx']
    for col, tr in trains.items():
        order = range(len(rows)) if tr['along'] else range(len(rows) - 1, -1, -1); calls = []
        for i in order:
            cs = rows[i]['cells'].get(col)
            if not cs: continue
            first, last = (cs[0], cs[-1]) if tr['along'] else (cs[-1], cs[0])
            calls.append([i, first[0], last[1]])
        base, prev = 0, None
        zone = lambda j: (rows[calls[j][0]].get('tz') or '') if 0 <= j < len(calls) else ''
        for ci, c in enumerate(calls):
            # the zone the row is printed in, where the table says (Saskatchewan and Manitoba: 'C' Central, 'M' Mountain; at the station where
            # the time changes, 'C/M': the arrival in the zone the train comes from, the departure in the zone it goes on to); otherwise the spec's shift
            tz = rows[c[0]].get('tz') if spec.get('tzrows') else None
            for k in (1, 2):
                z = tz
                if tz and '/' in tz:
                    nb = zone(ci - 1) if k == 1 else zone(ci + 1)
                    if not nb or '/' in nb: nb = zone(ci + 1) if k == 1 else zone(ci - 1)
                    z = nb if nb and '/' not in nb else tz.split('/')[0 if k == 1 else -1]
                sh = TZ_SHIFT[z] if z else spec.get('shift', -3600)
                x = c[k] + sh + base
                if prev is not None and x < prev - 4 * 3600: base += 86400; x += 86400
                prev = x; c[k] = x                                          # in Pacific time (Alberta: Mountain less an hour; 0 where the tables print Pacific time)
        days = ab_table.weekdays(tr['days'])
        if calls and calls[0][1] < 0:                                       # by the Pacific clock it starts late the evening before
            for c in calls: c[1] += 86400; c[2] += 86400
            days = days[1:] + days[:1]
        for (i, _, da), (j, tb, _) in zip(calls, calls[1:]):
            mph = abs(rows[j]['d'] - rows[i]['d']) / MI / max((tb - da) / 3600, 1e-9)
            if tb <= da or mph > 66: log(f"    !! {spec['key']} {col}: {rows[i]['name']} -> {rows[j]['name']} {abs(rows[j]['d'] - rows[i]['d']) / MI:.1f} mi in {(tb - da) / 60:.0f} min")
        mixed = tr['kind'] == 'mixed'; num = ('M' if mixed and tr['num'] else '') + tr['num']
        if not num: num = 'Mixed' if mixed else 'Train'                 # the Guide prints no number
        tid = f"{pfx}-{num}" if tr['num'] else f"{pfx}-{spec['key'].split('_')[-1].upper()}-{col}"
        while tid in taken: tid += '-' + spec['key'].split('_')[-1].upper()
        taken.add(tid)
        name = spec.get('names', {}).get(col, 'Mixed' if mixed else 'Motor train' if tr['kind'] == 'motor' else '')
        ends = ((f" From {tr['from']}." if tr.get('from') else '') + (f" To {tr['to']}." if tr.get('to') else '')) if spec.get('ends', True) else ''
        note = (spec.get('notes', {}).get(col) or tr.get('note', '')).strip()
        note = (note + ('' if not note or note.endswith('.') else '.') + ends + (spec.get('tznote', ' Shown in Pacific time, an hour earlier than the Mountain time printed.') if spec.get('shift', -3600) else '')).strip()
        out.append(dict(id=tid, num=num, name=name, svc=svc_of(days), dir=0 if tr['along'] else 1, stops=[[stn_index[i], a, b, 1] for i, a, b in calls], note=note,
                        **({k: tr[k] for k in ('from', 'to') if tr.get(k)} if spec.get('realends') else {})))
    return out

# ---------------------------------------------------------------- build and write
def build(specs, log=print):
    """build the lines, add them to viz_data.json and the GTFS feed"""
    vd = json.load(open(os.path.join(HERE, 'viz_data.json'))); keys = {s['key'] for s in specs}
    vd['lines'] = [L for L in vd['lines'] if L['key'] not in keys]
    drawn, drawn_own = [], []                                          # track already on the map, and whose track it is drawn as
    def remember(xy, o=None):
        if len(xy) > 1: drawn.append(LineString(xy)); drawn_own.append(o)
    def own_at(L_owner, segs, c):
        for s in segs:
            if s['owner'] != 'none' and not s.get('est') and s['a'] <= c <= s['b']: return s['owner']
        return L_owner
    for L in vd['lines']:
        if L.get('mainline') and not L.get('water'):
            xy = _xy([p[:2] for p in L['route']]); segs = L.get('segments', []); none = [(s['a'], s['b']) for s in segs if s['owner'] == 'none']
            run, ro = [], None
            for p, q in zip(xy, L['route']):
                o = own_at(L.get('owner'), segs, q[2])
                if any(a <= q[2] <= b for a, b in none) or (run and o != ro): remember(run, ro); run = []
                if not any(a <= q[2] <= b for a, b in none): run.append(p); ro = o
            remember(run, ro)
    taken = {t['id'] for L in vd['lines'] for t in L.get('trips', [])}
    seen_stop = set(r[0] for r in csv.reader(open(os.path.join(GT, 'stops.txt'))))
    seen_svc = set(r[0] for r in csv.reader(open(os.path.join(GT, 'calendar.txt'))))
    G = dict(routes=[], stops=[], shapes=[], trips=[], times=[], cal=[])
    for spec in specs:
        rows, trains, pieces = trace(spec, log); report(spec, rows, pieces, log)
        rail = spec['rail']; RI = RAILS[rail]; own = RI['own']
        # geometry: each piece simplified on its own, so the stations at its ends stay on the line
        pts, cum, segs, acc = [], [], [], 0.0; scale = {}; other = []
        for p in pieces:
            c = list(LineString(p['coords']).simplify(2.0).coords) if len(p['coords']) > 2 else p['coords']
            a0 = acc
            for k, q in enumerate(c):
                if k: acc += math.dist(q, c[k - 1])
                if k or not pts: pts.append(q); cum.append(acc)
            scale[p['a']] = (a0, acc, rows[p['a']]['d'], rows[p['b']]['d'])
            if p['est']: segs.append(dict(owner=own, a=round(a0, 1), b=round(acc, 1), est=1))
            elif any(p.get('owns', ())):                              # over another railway's track: that stretch in its colour
                raw = [0.0]
                for u, v in zip(p['coords'], p['coords'][1:]): raw.append(raw[-1] + math.dist(u, v))
                f = (acc - a0) / raw[-1] if raw[-1] else 0.0; k = 0
                while k < len(p['owns']):
                    o = p['owns'][k]
                    if not o: k += 1; continue
                    j = k
                    while j + 1 < len(p['owns']) and p['owns'][j + 1] == o: j += 1
                    if raw[j + 1] - raw[k] > 150: other.append(dict(owner=o, a=round(a0 + raw[k] * f, 1), b=round(a0 + raw[j + 1] * f, 1)))
                    k = j + 1
        def chain(d):
            for a0, a1, d0, d1 in scale.values():
                if d0 <= d <= d1: return a0 + (a1 - a0) * ((d - d0) / (d1 - d0) if d1 > d0 else 0)
            return acc
        line = LineString(pts) if len(pts) > 1 else None
        # shared with track already drawn: sampled every 100 m. Track drawn as another of the PARALLEL railways' (OWN_APART) is not shared even
        # when it runs within 20 m (NP and UP side by side between Black River and Seattle, Brendan 15 October 2026)
        tree = STRtree(drawn) if drawn else None; shared = []
        own_new = lambda x: next((o['owner'] for o in other if o['a'] <= x <= o['b']), own)
        apart = lambda o1, o2: o1 in OWN_APART and o2 in OWN_APART and o1 != o2
        if tree is not None:
            ds = np.arange(0, acc + 1, 100.0); hit = []
            for x in ds:
                P = line.interpolate(float(x)); near = tree.query(P.buffer(20)); on = own_new(float(x))
                hit.append(any(drawn[i].distance(P) < 20 and not apart(drawn_own[i], on) for i in near))
            k = 0
            while k < len(ds):
                if hit[k]:
                    j = k
                    while j + 1 < len(ds) and hit[j + 1]: j += 1
                    if ds[j] - ds[k] >= 400: shared.append((max(0.0, float(ds[k]) - 50), min(acc, float(ds[j]) + 50)))
                    k = j + 1
                else: k += 1
        est_segs = []
        for s in segs:                                                # an estimate that an earlier line already drew is simply not drawn again
            if not any(a <= s['a'] + 60 and b >= s['b'] - 60 for a, b in shared): est_segs.append(s)
        segments = [dict(owner='none', a=round(a, 1), b=round(b, 1)) for a, b in shared] + est_segs
        segments += [o for o in other if not any(a <= o['a'] + 60 and b >= o['b'] - 60 for a, b in shared)]
        if own in OWN_APART:                                          # a short gap between stretches of other track would show in this line's colour
            ss = sorted((x for x in segments if not x.get('est')), key=lambda x: x['a']); fill = []
            for x, y in zip(ss, ss[1:]):
                if 0 < y['a'] - x['b'] < 1500 and x['owner'] != own and y['owner'] != own:
                    o = x['owner'] if x['owner'] == y['owner'] else (y['owner'] if x['owner'] == 'none' else x['owner'] if y['owner'] == 'none' else x['owner'])
                    fill.append(dict(owner=o, a=x['b'], b=y['a']))
            segments += fill
        run, ro = [], None                                            # remember this line's track, piece by piece with whose it is
        for q, c in zip(pts, cum):
            o = own_new(c)
            if run and o != ro: remember(run, ro); run = [run[-1]]
            run.append(q); ro = o
        remember(run, ro)
        stn_i = {}; st = []
        for i, r in enumerate(rows):
            if not r['cells']: continue
            ch = chain(r['d']); lon, lat = inv(*line.interpolate(ch).coords[0]); stn_i[i] = len(st)
            on_est = any(s['a'] - 1 <= ch <= s['b'] + 1 for s in segs)
            how = 'position from the federal names file' if r.get('how') not in (None, 'map', 'hand') else 'placed by its printed mileage' if 'raw' not in r else ''
            note = RI['label'] + ' station' + ('; on a stretch drawn as a straight estimate' if on_est else '')
            st.append(dict(name=r['name'], chain=round(ch, 1), lon=round(lon, 6), lat=round(lat, 6), mile=r['mile'], principal=r['principal'], note=note, kml='', gid=gid_for(rail, r['name'])))
        trips = trips_of(spec, rows, trains, stn_i, taken, log)
        route = [[round(lo, 6), round(la, 6), round(c, 1)] for (lo, la), c in zip((inv(*q) for q in pts), cum)]
        vd['lines'].append(dict(key=spec['key'], kind=RI['kind'], label=RI['label'],
                                mainline=True, owner=own, route=route, stations=st, dirLabels=spec['dirs'], segments=segments, trips=trips, src=spec['src']))
        rid = spec['key'].upper()
        G['routes'].append([rid, RI['agency'], spec['short'], spec['long'], 2, RI['color'], 'FFFFFF',
                            spec['src'] + (('.' + spec['tznote']) if spec.get('tznote') and spec.get('shift', -3600) else '. Pacific time, an hour earlier than the Mountain time printed.' if spec.get('shift', -3600) else '. Pacific time.') + (' Part of the track is a straight-line estimate.' if est_segs else '')])
        for s in st:
            if s['gid'] not in seen_stop: seen_stop.add(s['gid']); G['stops'].append([s['gid'], f"{s['name']} ({rid.split('_')[0]})", f"{s['lat']:.6f}", f"{s['lon']:.6f}", s['note']])
        for sid, seq in ((rid + '_OUT', list(zip(pts, cum))), (rid + '_IN', [(q, acc - c) for q, c in zip(pts[::-1], cum[::-1])])):
            for k, (q, c) in enumerate(seq):
                lon, lat = inv(*q); G['shapes'].append([sid, f'{lat:.6f}', f'{lon:.6f}', k, f'{c:.1f}'])
        fmt = lambda x: f'{x // 3600:02d}:{x % 3600 // 60:02d}:{x % 60:02d}'
        for t in trips:
            if t['svc'] not in seen_svc: seen_svc.add(t['svc']); G['cal'].append([t['svc'], *t['svc'][2:], '19490616', '19491231'])
            G['trips'].append([rid, t['svc'], t['id'], st[t['stops'][-1][0]]['name'], (('No. ' + t['num']) if t['num'] not in ('Mixed', 'Train') else t['num']), t['dir'], rid + ('_OUT' if t['dir'] == 0 else '_IN')])
            for k, (i, a, b, tp) in enumerate(t['stops'], 1):
                G['times'].append([t['id'], fmt(a), fmt(b), st[i]['gid'], k, f"{(st[i]['chain'] if t['dir'] == 0 else acc - st[i]['chain']):.1f}", 1])
        log(f"            {len(st)} stations, {len(trips)} trains: {' '.join(t['id'] for t in trips)}")
    open(os.path.join(HERE, 'viz_data.json'), 'w').write(json.dumps(vd, separators=(',', ':')))
    for name, k in (('routes.txt', 'routes'), ('stops.txt', 'stops'), ('shapes.txt', 'shapes'), ('trips.txt', 'trips'), ('stop_times.txt', 'times'), ('calendar.txt', 'cal')):
        with open(os.path.join(GT, name), 'a', newline='') as fh: csv.writer(fh).writerows(G[k])
