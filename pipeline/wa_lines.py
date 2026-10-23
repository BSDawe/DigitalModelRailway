"""Washington (and the Oregon runs of trains that enter Washington): track graphs and station places for the ab_lines.py machinery.
A helper, imported by wa_build.py.

Track: the traced lines in wa_tracks.py (Mississippi Rails KMLs and Brendan's OWR&N file), as they stood in 1948. A line is routed over the
track of the railways named in its spec's graph key ('wa:np', 'wa:np+up', ...), so a train is not sent over another railway's track unless
it had the right to run there.
Stations (Brendan, 9 October 2026: mileposts are more reliable than place names): only the PRINCIPAL stations of the tables (terminals,
junctions, towns in heavy type) are given a position, from (in order) a point given by hand, a station already on the map, the end of a traced
line named after the place, or the federal names file (places/wa/wa_places.csv); every other station goes at its printed mileage between them."""
import csv, glob, math, os, re
import ab_lines, ab_table, wa_tracks
from ab_lines import fwd, norm
HERE = os.path.dirname(os.path.abspath(__file__))

ab_lines.RAILS.update({
    'np': dict(kind='o', label='Northern Pacific', own='np', agency='NP', color='1F4E79', pfx='NP'),
    'gnw': dict(kind='g', label='Great Northern', own='gn', agency='GN', color='E07B1A', pfx='GN'),
    'sps': dict(kind='d', label='Spokane, Portland & Seattle', own='sps', agency='SPS', color='5B4A8B', pfx='SPS'),
    'up': dict(kind='u', label='Union Pacific', own='up', agency='UP', color='C9A227', pfx='UP'),
    'milw': dict(kind='m', label='Milwaukee Road', own='milw', agency='MILW', color='B5651D', pfx='MILW'),
    'cprr': dict(kind='u', label='Camas Prairie', own='up', agency='CPRR', color='C9A227', pfx='CPRR'),
    'wim': dict(kind='o', label='Washington, Idaho & Montana', own='np', agency='WIM', color='1F4E79', pfx='WIM')})

# ---------------------------------------------------------------- track
# an "old alignment" that was the line in 1948: at Lakewood it is the only track joining the Prairie Line from Tacoma to the line on to Nisqually
# (Fort Lewis; NP Table 60, Brendan 9 October 2026)
KEEP_OLD = {'Lakewood WA old alignment',
            'Riaria old alignment'}            # Riparia, Camas Prairie: the line before the Snake River dam (1961; Brendan, 15 October 2026)
# old alignments named only "old alignment": kept by a point at one of their ends
KEEP_OLD_AT = [('old alignment', (-121.9236, 47.3241))]     # NP Stampede line, Palmer - Eagle Gorge: the line before Howard A. Hanson Dam (1962; Brendan, 14 October 2026)
DROP = {'Villard Jct new'}                                    # UP, Villard Jct: part of the McNary Dam (Lake Wallula) relocation, about 1954 (Brendan, 15 October 2026)
def _keep(f):
    if f['name'] in DROP: return False
    if wa_tracks.in_1948(f) or f['name'] in KEEP_OLD: return True
    return any(f['name'] == nm and min(math.dist(fwd(*f['coords'][0]), fwd(*p)), math.dist(fwd(*f['coords'][-1]), fwd(*p))) < 200 for nm, p in KEEP_OLD_AT)
FEAT = [f for f in wa_tracks.features() if _keep(f)]
# stretches of present-day lines that replaced the old alignments above after 1948: (name, from near this point, to near this point) is cut out.
# The cut pieces are renamed '... [cut]' so their ends are not taken for the stations they are named after.
CUTS = [('Palmer WA to Auburn WA', (-121.8848, 47.3109), (-121.9236, 47.3241)),          # Hanson Dam relocation: Palmer to where the old line joins
        ('Veazey WA to Eagle Gorge WA', (-121.8795, 47.3125), (-121.7514, 47.2583)),     #   Palmer to Eagle Gorge
        ('Eagle Gorge WA to Stampede Pass WA', (-121.7514, 47.2583), (-121.7226, 47.2399)),   # Eagle Gorge to where the old line rejoins
        ('Riparia WA to WA/ID State Line', (-118.0907, 46.5774), (-118.0263, 46.5894)),  # Riparia (1961 dam)
        ('Pasco to Zanger Jct WA', (-118.9195, 46.1058), (-119.0253, 46.2049))]          # NP past Attalia: McNary relocation (the "Attalia original route" is kept)
def _cut(f):
    out = [f]
    for nm, p, q in CUTS:
        if f['name'] != nm: continue
        c = f['coords']; P, Q = fwd(*p), fwd(*q)
        i = min(range(len(c)), key=lambda k: math.dist(fwd(*c[k]), P)); j = min(range(len(c)), key=lambda k: math.dist(fwd(*c[k]), Q))
        i, j = min(i, j), max(i, j)
        out = [dict(f, name=f['name'] + ' [cut]', coords=s) for s in (c[:i + 1], c[j:]) if len(s) > 1]
    return out
FEAT = [g for f in FEAT for g in _cut(f)]
# whose track the UP/Milwaukee joint line south of Seattle is drawn as (Brendan, 15 October 2026): the Milwaukee's from Tacoma to Black River
# Junction (continuous, though the UP pool trains use it), the UP's from Black River Junction north into Seattle Union Station
BLACK_RIVER = (-122.251934, 47.476302)
def _owner(f):
    if 'rts on Northern Pacific' in (f['name'] or ''): return [dict(f, own='np')]   # the SP&S over the NP (Pasco - Ainsworth Jct): NP track
    if f['rail'] not in ('up', 'milw'): return [f]
    if f['name'] == 'Tacoma WA to Renton WA': return [dict(f, own='milw')]
    if f['name'] == 'Renton WA to Seattle WA':
        c = f['coords']; P = fwd(*BLACK_RIVER); k = min(range(len(c)), key=lambda i: math.dist(fwd(*c[i]), P))
        return [g for g in (dict(f, coords=c[:k + 1], own='milw'), dict(f, coords=c[k:], own='up')) if len(g['coords']) > 1]
    return [f]
FEAT = [g for f in FEAT for g in _owner(f)]
# Brendan's Walla Walla traces (15 October 2026): the NP station spur (from the NP KMZ) and the UP wye he drew to the UP station
import json as _json
for _f in _json.load(open(os.path.join(HERE, 'traces', 'washington', 'walla_walla_stations.geojson')))['features']:
    FEAT.append(dict(file='walla_walla_stations.geojson', path='', rail=_f['properties']['rail'], name=_f['properties']['name'], built=None, aband=None,
                     rights=False, coords=[tuple(p) for p in _f['geometry']['coordinates']]))
# lines that stood in 1948 only in part: (name, cut near this point, keep the part 'before' or 'after' it along the trace).
# The Milwaukee's Raymond branch (Brendan, 9 October 2026): by a joint trackage agreement of 1935 its trains ran over the NP between Chehalis
# Junction and Dryad (16.83 mi), and its own line between Chehalis and Dryad was sold to loggers; Milwaukee rails again from Dryad to Raymond.
TRIM = [('Raymond WA to Ruth WA', (-123.251254, 46.636768), 'before'),        # Dryad (names file)
        ('Ruth WA to Maytown WA', (-122.974800, 46.656500), 'after')]          # Chehalis (the Milwaukee's station, the end of its line from Longview)
def _trim(f):
    for nm, p, keep in TRIM:
        if f['name'] == nm:
            P = fwd(*p); c = f['coords']; k = min(range(len(c)), key=lambda i: math.dist(fwd(*c[i]), P))
            f = dict(f, coords=c[:k + 1] if keep == 'before' else c[k:])
    return f
FEAT = [_trim(f) for f in FEAT]
# short joins where two traces meet but do not touch (more than the 150 m tie): (railway, from, to)
JOINS = [('up', (-117.969384, 46.327751), (-117.965222, 46.330337)),     # Dayton: the NP line from Waitsburg and the OR&N line to Turner, 431 m apart
         ('up', (-122.327674, 47.587941), (-122.328587, 47.598514)),       # Seattle: the end of the traced line from Renton into Union Station (1.2 km, straight)
         ('milw', (-122.327674, 47.587941), (-122.328587, 47.598514)),
         ('up', (-118.913057, 46.095319), (-118.914952, 46.102165)),       # Wallula: the end of the line from Oregon and the lines to Villard Jct and Pataha, 776 m apart
         ('sps', (-118.944373, 46.243382), (-118.952875, 46.242745))]    # east of Pasco: the SP&S line from Spokane and its piece over the NP's Snake River bridge, 660 m apart
SPK_BOX = (-117.50, -117.32, 47.62, 47.70)                            # Spokane, between the NP, GN and Union stations
def _graph(rails):
    # 'upn': the UP's track north of 46.5 N only (Seattle - Tacoma): the UP pool trains, which from 1946 ran into Portland over the SP&S/NP
    # north-side route, not the UP's own access (Brendan, 15 October 2026)
    north = lambda pts: min(p[1] for p in pts) > 46.5
    use = lambda r, pts: r in rails or (r == 'up' and 'upn' in rails and north(pts))
    # 'gn@spk', 'up@spk': that railway's track only inside Spokane (to reach the city stations), not its lines that run beside the SP&S or
    # the Milwaukee elsewhere (Brendan, 15 October 2026: GN and UP pieces showing on SP&S and Milwaukee lines)
    spk = {r.split('@')[0] for r in rails if r.endswith('@spk')}
    inspk = lambda p: SPK_BOX[0] <= p[0] <= SPK_BOX[1] and SPK_BOX[2] <= p[1] <= SPK_BOX[3]
    dear = {r[:-1] for r in rails if r.endswith('~')}                  # 'up~': that railway's track at a higher cost (used only where its own is lacking)
    def feed(add):
        for f in FEAT:
            if use(f['rail'], f['coords']): add(ab_lines._xy(f['coords']), 1.0, 't', f.get('own', f['rail']))
            elif f['rail'] in dear: add(ab_lines._xy(f['coords']), 1.4, 't', f.get('own', f['rail']))
            elif f['rail'] in spk:
                run = []
                for p in f['coords'] + [None]:
                    if p is not None and inspk(p): run.append(p); continue
                    if len(run) > 1: add(ab_lines._xy(run), 1.0, 't', f.get('own', f['rail']))
                    run = []
        for r, p, q in JOINS:
            if use(r, [p, q]) or (r in spk and inspk(p) and inspk(q)): add(ab_lines._xy([p, q]), 1.0, 't', r)
    return lambda: ab_lines.make_graph(feed, tie_end=150)     # traces by different hands: a loose end is tied to track within 150 m
def register(key):
    """a graph over the track of the railways named in key ('np+up'), under the name 'wa:' + key"""
    ab_lines.EXT_GRAPH.setdefault('wa:' + key, _graph(set(key.split('+'))))

# ---------------------------------------------------------------- places
HAND = {  # points given by hand (city stations, which the names file gives only as the city centre). APPROXIMATE until Brendan places them.
    'portland': (-122.6768, 45.5290, 'Portland Union Station'),
    'portland (union sta.)': (-122.6768, 45.5290, 'Portland Union Station'),
    'seattle (king st. sta.)': (-122.329704, 47.598466, 'King Street Station (Brendan)'),
    'seattle (union sta.)': (-122.328587, 47.598514, 'Union Station (Brendan)'),
    'spokane (g. n. station)': (-117.418981, 47.661772, 'GN station (Brendan)'),
    'spokane (n. p. station)': (-117.415300, 47.656561, 'NP station (Brendan)'),
    'marengo': (-118.188611, 47.025833, 'joint UP / Milwaukee station (Brendan, 9 Oct: 47 01 33 N, 118 11 19 W)'),
    'union mill': (-122.775020, 47.032424, 'Union Mill, on the track (Brendan, 17 Oct; east of Lacey; both mile 68 in the tables)'),
    'lacey': (-122.810213, 47.036738, 'Lacey depot, still standing (Brendan, 17 Oct)'),
    'north portland': (-122.710337, 45.607388, 'one station for all roads (Brendan, 15 Oct: about 45 36 22 N, 122 42 43 W; on the SP&S track nearest it)'),
    'tucannon': (-118.18946, 46.56289, 'the names file\'s locality at the mouth of the Tucannon, on the Snake River line'),
}
ab_lines.EXT_GID.update({('gnw', 'Seattle (King St. Sta.)'): 'GN_SEATTLE', ('gnw', 'Seattle'): 'GN_SEATTLE',
                          ('up', 'Marengo'): 'WA_MARENGO', ('milw', 'Marengo'): 'WA_MARENGO'})     # one joint station
ab_lines.EXT_GID.update({(r, 'North Portland'): 'WA_NORTH_PORTLAND' for r in ('np', 'gnw', 'sps', 'up')})
_GN = {}                                                              # every place of each name (there are several Newports)
for r in csv.DictReader(open(os.path.join(HERE, 'places', 'wa', 'wa_places.csv'))):
    _GN.setdefault(r['name'].lower(), []).append((float(r['lon']), float(r['lat']), r['kind'], r['county']))
import numpy as np
from scipy.spatial import cKDTree
_TRK = cKDTree(np.array([fwd(*p) for f in FEAT for p in f['coords'][::3]]))
def _gn(name):
    """the place of that name nearest to any traced track"""
    c = _GN.get(name)
    if not c: return None
    if name in COUNTY: c = [g for g in c if g[3] == COUNTY[name]] or c
    return min(c, key=lambda g: _TRK.query(fwd(g[0], g[1]))[0])
COUNTY = {'newport': 'Pend Oreille', 'sunnyside': 'Yakima', 'lakeview': 'Pierce'}                                 # where the names file has several places of the name, the one meant
# the ends of traced lines named after places ("Kalama WA to Vancouver WA"): the end nearer the place in the names file, or the end two lines share
_ENDS = {}
def _ends():
    if _ENDS: return _ENDS
    cand = {}
    for f in FEAT:
        m = re.match(r'(.+?)\s+(?:WA|OR|ID)?\s*to\s+(.+?)\s*(?:WA|OR|ID)?$', f['name'] or '')
        if not m: continue
        for nm in (m.group(1), m.group(2)):
            nm = re.sub(r'\s+(WA|OR|ID)$', '', nm.strip()).lower()
            cand.setdefault(nm, []).append((f['coords'][0], f['coords'][-1]))
    for nm, pairs in cand.items():
        pts = [p for pr in pairs for p in pr]
        g = _gn(nm)
        if g:
            best = min(pts, key=lambda p: math.dist(fwd(*p), fwd(g[0], g[1])))
            if math.dist(fwd(*best), fwd(g[0], g[1])) < 6000: _ENDS[nm] = best; continue
        if len(pairs) > 1:                                             # a point two of its lines share
            shared = [p for i, pr in enumerate(pairs) for p in pr if any(math.dist(fwd(*p), fwd(*q)) < 400 for j, pr2 in enumerate(pairs) if j != i for q in pr2)]
            if shared: _ENDS[nm] = shared[0]
    return _ENDS
ANCHOR = set()                                                         # the principal stations of all the tables
for fn in glob.glob(os.path.join(HERE, 'wa_*.csv')):
    for r in ab_table.load(fn)['rows']:
        if r['principal'] == '1': ANCHOR.add(r['station'])
    R = ab_table.load(fn)['rows']; ANCHOR.update((R[0]['station'], R[-1]['station']))      # and the ends of every table
def _clean(name): return re.sub(r'\s*\(.*\)$', '', name).strip().lower()
# the city stations of each railway (Brendan, 9 October 2026), for the tables that print only the city's name
SEA_KS, SEA_US = (-122.329704, 47.598466), (-122.328587, 47.598514)
SPK_GN, SPK_US, SPK_NP = (-117.418981, 47.661772), (-117.418711, 47.660367), (-117.415300, 47.656561)
TAC, TAC_MILW = (-122.435975, 47.245889), (-122.431133, 47.238750)
WW_NP, WW_UP = (-118.344050, 46.072774), (-118.353720, 46.061069)   # Walla Walla: the NP station at the end of its spur, the UP's at the end of Brendan's wye (15 Oct 2026)
VAN = (-122.687470, 45.628164)      # Vancouver, Wash.: one station for the SP&S, NP, GN and pool trains, at the wye (Brendan; where the traces meet)
BY_RAIL = {('np', 'seattle'): SEA_KS, ('gnw', 'seattle'): SEA_KS, ('milw', 'seattle'): SEA_US, ('up', 'seattle'): SEA_US,
           ('np', 'spokane'): SPK_NP, ('sps', 'spokane'): SPK_NP, ('gnw', 'spokane'): SPK_GN, ('up', 'spokane'): SPK_US, ('milw', 'spokane'): SPK_US,
           ('cprr', 'spokane'): SPK_US, ('np', 'tacoma'): TAC, ('gnw', 'tacoma'): TAC, ('up', 'tacoma'): TAC, ('milw', 'tacoma'): TAC_MILW,
           ('np', 'walla walla'): WW_NP, ('up', 'walla walla'): WW_UP,
           ('np', 'vancouver'): VAN, ('sps', 'vancouver'): VAN, ('gnw', 'vancouver'): VAN, ('up', 'vancouver'): VAN}
# one station for each city station, whichever railway's table names it (the gid; King Street is the GN station already on the map)
CITY_GID = {SEA_KS: 'GN_SEATTLE', SEA_US: 'WA_SEATTLE_UNION_STATION', SPK_GN: 'WA_SPOKANE_GN_STATION', SPK_US: 'WA_SPOKANE_UNION_STATION',
            SPK_NP: 'WA_SPOKANE_NP_STATION', TAC: 'WA_TACOMA_UNION_STATION', TAC_MILW: 'WA_TACOMA_MILW_STATION', (-122.6768, 45.5290): 'PORTLAND_UNION_STATION',
            VAN: 'WA_VANCOUVER_STATION'}
for _r in ('np', 'gnw', 'sps', 'up', 'milw', 'cprr', 'wim'):
    for _n in ('Portland', 'Portland (Union Sta.)', 'Seattle', 'Seattle (King St. Sta.)', 'Seattle (Union Sta.)', 'Spokane', 'Spokane (G. N. Station)',
               'Spokane (N. P. Station)', 'Tacoma', 'Vancouver'):
        _k = (_r, _n.lower())
        _p = BY_RAIL.get(_k) or (HAND[_n.lower()][:2] if _n.lower() in HAND else None)
        if _p and tuple(_p) in CITY_GID: ab_lines.EXT_GID[(_r, _n)] = CITY_GID[tuple(_p)]
def place_for(rail):
    def f(name):
        k = (rail, name.lower())
        if k in BY_RAIL: return (*BY_RAIL[k], 'hand', 600)
        return place(name)
    return f
def place(name):
    n = name.lower()
    if n in HAND: h = HAND[n]; return (h[0], h[1], 'hand', 600)
    if name not in ANCHOR: return None                                  # by its printed mileage
    c = _clean(name)
    if c in _ends(): p = _ends()[c]; return (p[0], p[1], 'trace end', 1500)
    g = _gn(c)
    if g: return (g[0], g[1], g[2], 3000)
    return None
for _r in ('np', 'gnw', 'sps', 'up', 'milw', 'cprr', 'wim'): ab_lines.EXT_PLACE[_r] = place_for(_r)
# the Portland sections of GN Nos. 1-4 (rail 'gnw') run over the SP&S (Table 1): they call at the SP&S's own stations, not GN copies of them
# (Brendan, 15 October 2026: the GN trains were missing from the SP&S station boxes)
import re as _re
for _row in ab_table.load(os.path.join(HERE, 'wa_sps_t001.csv'))['rows']:
    _n = _row['station']
    if ('gnw', _n) not in ab_lines.EXT_GID:
        ab_lines.EXT_GID[('gnw', _n)] = ab_lines.EXT_GID.get(('sps', _n)) or 'SPS_' + _re.sub(r'\W+', '_', _n.upper()).strip('_')
