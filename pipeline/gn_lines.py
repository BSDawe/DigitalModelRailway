"""Great Northern east of Spokane, with the Burlington Chicago - St. Paul (Brendan, 27 Nov 2026): track graph and station places for the ab_lines.py machinery.
A helper, imported by gn_build.py (its own process: the projection is switched here).

Track: traces/gnmw/gn_mw.geojson (tools/gn_import.py: Mississippi Rails' Great Northern KMZ east of Spokane, and the CB&Q Chicago - St. Paul, own cbq), with the
Northern Pacific and Soo pieces at Superior - Duluth from traces/maritimes/soo.geojson (drawn in their owners' colours) and Brendan's Milwaukee Road trace's
St. Paul Union Depot end (traces/milw).
Stations, in order: a point given by hand (HAND); a station already on the map (the Great Northern lines built before, and this step's own main lines when the
branches are built); the end of a KMZ piece named for that place ("Powers Lake ND to Grenora ND"); else by printed mileage between located neighbours.
Stop ids: a station the earlier GN lines share keeps its id (SHARE); every other station is GN_<NAME>_<STATE>, so Lyons, S. Dak. is not Lyons, Wash.
PROJECTION: a Lambert conformal conic for the northern plains (parallels 42 and 48 N, central meridian 100 W), so traced and printed miles agree."""
import json, math, os, re, unicodedata
from pyproj import Transformer
import ab_lines, ab_table
HERE = os.path.dirname(os.path.abspath(__file__))
_P = '+proj=lcc +lat_1=42 +lat_2=48 +lon_0=-100 +lat_0=45 +datum=WGS84 +units=m +no_defs'
_T = Transformer.from_crs(4326, _P, always_xy=True); _I = Transformer.from_crs(_P, 4326, always_xy=True)
ab_lines.fwd, ab_lines.inv = _T.transform, _I.transform
ab_lines._T, ab_lines._I = _T, _I
fwd = _T.transform
ab_lines.RAILS['gnmw'] = dict(kind='g', label='Great Northern', own='gn', agency='GN', color='E07B1A', pfx='GN')
STATES = {'Minn.': 'MN', 'N. Dak.': 'ND', 'S. Dak.': 'SD', 'Mont.': 'MT', 'Idaho': 'ID', 'Wis.': 'WI', 'Iowa': 'IA', 'Ill.': 'IL', 'Wash.': 'WA'}
def split(name):
    m = re.match(r'^(.*?),\s*(Minn\.|N\. Dak\.|S\. Dak\.|Mont\.|Idaho|Wis\.|Iowa|Ill\.|Wash\.)$', name)
    return (m.group(1), STATES[m.group(2)]) if m else (name, '')
def canon(n):
    n = unicodedata.normalize('NFKD', n).encode('ascii', 'ignore').decode().lower()
    n = re.sub(r'\s*\(.*?\)', '', n).replace("'", '').replace('.', '').replace('junc', 'jct').replace('junction', 'jct')
    n = re.sub(r'\bsaint\b', 'st', n); n = n.replace('jcttion', 'jct')
    return re.sub(r'\s+', ' ', n).strip()
# ---------------------------------------------------------------- track
def _graph():
    def feed(add):
        F = json.load(open(os.path.join(HERE, 'traces', 'gnmw', 'gn_mw.geojson')))['features']
        for f in F:
            o = f['properties']['own']; add(ab_lines._xy(f['geometry']['coordinates']), 1.0, 'b', None if o == 'gn' else o)
        for fn in ('gn_mn_nd.geojson', 'gn_neche_gretna.geojson'):              # Brendan's GN traces of October (the Winnipeg line): preferred where they run
            for f in json.load(open(os.path.join(HERE, 'traces', 'gn', fn)))['features']:
                if f['geometry']['type'] == 'LineString': add(ab_lines._xy(f['geometry']['coordinates']), 0.9, 'b', None)
        for f in json.load(open(os.path.join(HERE, 'traces', 'gnmw', 'gn_links.geojson')))['features']:   # Brendan's pieces and Claude's estimated links
            add(ab_lines._xy(f['geometry']['coordinates']), f['properties'].get('cost', 1.0), 'b', 'est' if f['properties'].get('est') else None)
        for f in json.load(open(os.path.join(HERE, 'traces', 'maritimes', 'soo.geojson')))['features']:   # Superior - Duluth: the NP and Soo pieces there
            c = f['geometry']['coordinates']
            if f['properties'].get('status') != 'ok' or not all(-92.25 < p[0] < -92.0 and 46.65 < p[1] < 46.82 for p in c): continue
            add(ab_lines._xy(c), 1.5, 'b', 'np')                                # the GN into Duluth by Northern Pacific trackage rights (Brendan, 27 Nov 2026)
        add(ab_lines._xy([(-92.107400, 46.726609), (-92.1061363, 46.7285855)]), 1.0, 'b', 'np')          # Superior Union Station to the NP connection
        mp = json.load(open(os.path.join(HERE, 'traces', 'milw', 'mpls_stpaul.geojson')))['features'][0]['geometry']['coordinates']
        k = min(range(len(mp)), key=lambda i: (mp[i][0] + 93.085361) ** 2 + (mp[i][1] - 44.946914) ** 2)
        add(ab_lines._xy(mp[max(0, k - 30):k + 30]), 1.2, 'b', 'union')        # St. Paul Union Depot's approaches (Brendan's Milwaukee Road trace)
    return lambda: ab_lines.make_graph(feed, tie_end=150, tie_loose=60, tie_each=True)
ab_lines.EXT_GRAPH['sk:gnmw'] = _graph()
# ---------------------------------------------------------------- places
def dms(d, m, s): return d + m / 60 + s / 3600
HAND = {('portland jct', 'ND'): (-dms(97, 22, 10.72), dms(47, 33, 39.72), 'Portland Junction (Brendan, 27 Nov 2026)'),
        ('superior', 'WI'): (-92.107400, 46.726609, 'Superior Union Station (Brendan, 27 Nov 2026; GN, shared with the NP)'),
        ('chicago', 'IL'): (-87.638917, 41.878867, 'Chicago Union Station (Brendan, 26 Nov 2026: 41 52 43.92 N, 87 38 20.10 W)'),
        # towns on the main line that no piece is named for (Claude's points for the towns, approximate; the station snaps to the track)
        ('havre', 'MT'): (-109.6841, 48.5500, 'Havre (town; approximate)'), ('shelby', 'MT'): (-111.8569, 48.5053, 'Shelby (town; approximate)'),
        ('williston', 'ND'): (-103.6177, 48.1467, 'Williston (town; approximate)'), ('whitefish', 'MT'): (-114.3376, 48.4111, 'Whitefish (town; approximate)'),
        ('billings', 'MT'): (-108.5017, 45.7836, 'Billings (town; approximate; the GN reached it over the NP from Mossmain)'),
        ('bemidji', 'MN'): (-94.8808, 47.4736, 'Bemidji (town; approximate)'), ('sandstone', 'MN'): (-92.8674, 46.1311, 'Sandstone (town; approximate)'),
        ('stone arch bridge', 'MN'): (-93.2525, 44.9806, 'Stone Arch Bridge (the route of the St. Paul - Minneapolis trains; Brendan, 27 Nov 2026)'),
        ('elbow lake', 'MN'): (-95.9767, 45.9940, 'Elbow Lake (town; approximate)'), ('sioux city', 'IA'): (-96.4003, 42.4963, 'Sioux City (town; approximate)'),
        ('hutchinson', 'MN'): (-94.3700, 44.8877, 'Hutchinson (town; approximate)'), ('lewistown', 'MT'): (-109.4282, 47.0625, 'Lewistown (town; approximate)'), ('sweet grass', 'MT'): (-111.9575, 48.9974, 'Sweet Grass (town; approximate)')}
# stations the Great Northern lines already on the map share: (canon name, state) -> gid (their position is taken from the map)
SHARE = {('st paul', 'MN'): 'CP_ST_PAUL', ('minneapolis', 'MN'): 'GN_MINNEAPOLIS', ('duluth', 'MN'): 'CN_DULUTH', ('noyes', 'MN'): 'CP_NOYES',
         ('newport', 'WA'): 'GN_NEWPORT', ('spokane', 'WA'): 'WA_SPOKANE_GN_STATION'}
_MAPX = {}
def _map():
    """gid -> (lon, lat), every station on the map (read afresh each phase: gn_build clears it)"""
    if not _MAPX:
        for L in json.load(open(os.path.join(HERE, 'viz_data.json')))['lines']:
            for s in L['stations']: _MAPX.setdefault(s['gid'], (s['lon'], s['lat']))
        for L in json.load(open(os.path.join(HERE, 'viz_data.json')))['lines']:        # the earlier GN lines' own stations (St. Cloud, Grand Forks, Grafton ...)
            if L['key'].startswith(('skgn',)):
                st = 'ND' if L['key'] == 'skgn009a' else 'MN'
                for s in L['stations']:
                    if s['gid'].startswith('GN_') and s['lat'] < 48.999: SHARE.setdefault((canon(s['name']), st), s['gid'])
    return _MAPX
ANCH = {}
ALIAS = {('watford city', 'ND'): ('watford', 'ND'), ('garretson', 'SD'): ('garretson', 'MN')}
def _anchors():
    """(canon name, state) -> (lon, lat): the ends of KMZ pieces named "A ST to B ST". Which end is which: a name that several pieces carry is the end they
    share (within 2 km); a name on one piece only takes the end that the piece's other name does not claim, and failing that the piece's own order."""
    if ANCH: return ANCH
    cand = {}
    for f in json.load(open(os.path.join(HERE, 'traces', 'gnmw', 'gn_mw.geojson')))['features']:
        m = re.match(r'^(.+?)\s+to\s+(.+)$', f['properties']['name'])
        if not m: continue
        c = f['geometry']['coordinates']; ends = (tuple(c[0]), tuple(c[-1])); keys = []
        for nm in (m.group(1), m.group(2)):
            mm = re.match(r'^(.*?)\s+(MN|ND|SD|MT|ID|WI|IA|IL|WA)$', nm.strip().rstrip(','))
            keys.append((canon(mm.group(1)), mm.group(2)) if mm else (canon(nm.strip()), ''))
        if keys[0][1] == '' and keys[1][1]: keys[0] = (keys[0][0], keys[1][1])     # a name without its state takes the other's ("Rock Lake to Hansboro ND")
        if keys[1][1] == '' and keys[0][1]: keys[1] = (keys[1][0], keys[0][1])
        for i, k in enumerate(keys): cand.setdefault(k, []).append((ends, i))
    km = lambda a, b: math.hypot((a[0] - b[0]) * 75.0, (a[1] - b[1]) * 111.0)
    seed = {}                                                             # names already placed: the hand points and the stations on the map
    for (c, st), h in HAND.items(): seed[(c, st)] = h[:2]
    for k in cand:
        if k[1]: g = [gid(k[0] + ', ' + {v: kk for kk, v in STATES.items()}[k[1]])]
        else: g = [x for x in _map() if x and re.match('GN_' + re.sub(r'\W+', '_', k[0].upper()).strip('_') + r'(_[A-Z]{2})?$', x)]   # a piece name without its state
        g = [x for x in g if x in _map()]
        if len(g) == 1: seed[k] = _map()[g[0]]                              # placed already (an earlier line, this step's main lines included)
    for k, L in cand.items():                                             # a name several pieces carry: the end they share
        if k in seed or len(L) < 2: continue
        pts = [e for ends, _ in L for e in ends]
        n = lambda p: sum(1 for ends, _ in L if min(km(p, e) for e in ends) < 2.0)
        best = max(pts, key=n)
        if n(best) > 1: ANCH[k] = best
    known = lambda k: seed.get(k) or ANCH.get(k)
    for _ in range(4):                                                    # a piece with one end known: the other name takes the other end
        for k, L in cand.items():
            if k in ANCH or k in seed: continue
            for ends, i in L:
                other = next((kk for kk, LL in cand.items() for e2, j in LL if e2 is ends and j != i), None)
                o = known(other) if other else None
                if o: ANCH[k] = max(ends, key=lambda e: km(e, o)); break
    return ANCH                                                           # a name settled by neither is not used (the piece's own order is often reversed)
def gid(name):
    n, st = split(name); c = canon(n)
    _map()
    return SHARE.get((c, st)) or 'GN_' + re.sub(r'\W+', '_', c.upper()).strip('_') + (('_' + st) if st else '')
def place(name):
    n, st = split(name); c = canon(n)
    if os.environ.get('GN_DEBUG') and os.environ['GN_DEBUG'] in name: print('DEBUG place', name, gid(name), _map().get(gid(name)), _anchors().get((c, st)))
    if (c, st) in HAND: h = HAND[(c, st)]; return (h[0], h[1], 'hand', 700 if 'Brendan' in h[2] else 2500)
    g = gid(name); m = _map().get(g)
    if m: return (m[0], m[1], 'map', 300)
    a = _anchors().get(ALIAS.get((c, st), (c, st)))
    if a: return (a[0], a[1], 'piece end', 1500)
    return None
ab_lines.EXT_PLACE['gnmw'] = place
class _G(dict):
    def get(self, k, d=None): return gid(k[1]) if k[0] == 'gnmw' else d
ab_lines.EXT_GID = _G(ab_lines.EXT_GID)
