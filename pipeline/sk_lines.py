"""Saskatchewan and Manitoba (Brendan, October 2026): track graphs and station places for the ab_lines.py machinery. A helper, imported by
sk_build.py.

Track: the national network for Saskatchewan and Manitoba (nrwn/sk_all.json, nrwn/mb_all.json, from Brendan's NRWN KMZs by nrwn/extract_prov.py;
yards left out) and the Alberta file near the boundary, with three backup sets for lines lifted since 1948: the Canadian Northern and Grand Trunk
Pacific sets (backup_track.py; CN lines only) and Brendan's OpenStreetMap export of abandoned, disused and razed railways in Saskatchewan
(traces/osm/osm_sk_abandoned_export.geojson, sidings, spurs and yards left out). A CN line is not routed over CP track, nor a CP line over CN
track; the short lines of today (former CN and CP branches) are open to both. The backups cost a little more, so the network is preferred.
Stations, in order: a point given by hand (the Winnipeg stations), a station of the same railway already on the map (the Alberta lines at the
boundary), a station of the national network of that name, and (Saskatchewan only) the federal names file, the place of that name nearest the
track. Manitoba stations other than the principal ones go by their printed mileage (Brendan, 10 October 2026: no Manitoba names file).
Every other station is put at its printed mileage between its located neighbours."""
import unicodedata, csv, glob, json, math, os, re
import numpy as np
from scipy.spatial import cKDTree
import ab_lines, ab_table
from ab_lines import fwd, norm
from backup_track import lines as backup_lines
HERE = os.path.dirname(os.path.abspath(__file__))

ab_lines.RAILS.update({'skcn': dict(kind='q', label='Canadian National', own='cn', agency='CN', color='2F6B44', pfx='CN'),
                       'skcp': dict(kind='p', label='Canadian Pacific', own='cp', agency='CP', color='7A1E2C', pfx='CP'),
                       'sknp': dict(kind='o', label='Northern Pacific', own='np', agency='NP', color='1F4E79', pfx='NP'),   # Winnipeg line (Table 14, 1947; 18 Oct)
                       'skgn': dict(kind='g', label='Great Northern', own='gn', agency='GN', color='E07B1A', pfx='GN'),
                       'skcnw': dict(kind='x', label='Chicago and North Western', own='cnw', agency='CNW', color='5C6E1A', pfx='CNW'),   # (19 Oct; colour Claude's pick)
                       'skww': dict(kind='j', label='Greater Winnipeg Water District Railway', own='gwwd', agency='GWWD', color='7A6A4F', pfx='GWWD')})   # (18 Oct; colour Claude's pick)    # Tables 7 and 9a, 1948 (18 Oct)
OWN = {'skcn': 'cn', 'skcp': 'cp', 'sknp': 'np', 'skgn': 'gn', 'skww': 'gwwd', 'skcnw': 'cnw'}
OWN_NAME = {'Canadian National': 'cn', 'Canadian Pacific': 'cp'}
BOX = (-111.0, -95.0, 48.9, 56.0)                                        # Saskatchewan, Manitoba to Winnipeg and the Flin Flon line, and the Alberta edge

# ---------------------------------------------------------------- track
def _nrwn():
    out = []
    for fn in ('sk_all.json', 'mb_all.json', 'alberta_all.json'):
        for f in json.load(open(os.path.join(HERE, 'nrwn', fn))):
            if fn == 'alberta_all.json' and not any(p[0] > BOX[0] for c in f['coords'] for p in c): continue
            out.append(f)
    return out
_NR = []
def nrwn():
    if not _NR: _NR.extend(_nrwn())
    return _NR
_OSM = {}
def _osm(service=False):
    """Brendan's OpenStreetMap exports of abandoned, disused and razed railways: Saskatchewan, and Manitoba (17 October 2026)"""
    if not _OSM:
        for fn in ('osm_sk_abandoned_export.geojson', 'osm_mb_abandoned_export.geojson'):
            p = os.path.join(HERE, 'traces', 'osm', fn)
            if os.path.exists(p):
                for f in json.load(open(p))['features']:
                    if f['geometry']['type'] == 'LineString':
                        sv = f['properties'].get('service'); _OSM.setdefault(bool(sv) and sv != 'no', []).append(f['geometry']['coordinates'])
    return _OSM.get(service, [])
def _graph(rail):
    me, other = ('Canadian National', 'Canadian Pacific') if rail == 'cn' else ('Canadian Pacific', 'Canadian National')
    def feed(add):
        for f in nrwn():
            if not f['schema'].endswith('Track'): continue
            op = f['data'].get('operatorEnglishName', f['data'].get('ownerEnglishName'))
            if op == 'Central Manitoba Railway': op = 'Canadian National'   # the Pine Falls subdivision: CN in 1948 (Brendan, 19 October: the Victoria Beach line)
            fac = {'Main': 1.0, 'Connecting': 1.0, 'Siding': 1.3}.get(f['data'].get('trackClassification'), 1.5) * (1.0 if op == me else 1.1)
            o = None
            if op == other and rail == 'cn' and any(_in(b, p) for b in CN_AS_OWN for c in f['coords'] for p in c): op = me; fac /= 1.1
            if op == other:
                if any(_in(b, p) for b in JOINT[rail] for c in f['coords'] for p in c): o = OWN_NAME[other]   # shared in 1948: drawn as the other railway's
                else: fac *= 2.5        # today's other-railway track elsewhere (lines changed hands since 1948): only where nothing else serves (16 October)
            for c in f['coords']:
                if len(c) > 1: add(ab_lines._xy(c), fac, 'n', o)
        for which in ('cnor', 'gtp'):
            for _n, _d, pts in backup_lines(which, box=BOX):
                if rail == 'cn': add(ab_lines._xy(pts), 1.2, 'b'); continue
                run = []                                                   # CP: only the pieces inside a joint section
                for p in pts + [None]:
                    if p is not None and any(_in(b, p) for b in JOINT[rail]): run.append(p); continue
                    if len(run) > 1: add(ab_lines._xy(run), 1.2, 'b', 'cn')
                    run = []
        for c in _osm(): add(ab_lines._xy(c), 1.25, 'b')
        for c in _osm(service=True): add(ab_lines._xy(c), 1.6, 'b')      # sidings, spurs and yards of the OSM export: connectors where nothing else serves
        for fn in ('sk_yards.json', 'mb_yards.json'):                     # the network's yard track (left out of *_all.json): last-resort connectors (17 Oct)
            p = os.path.join(HERE, 'nrwn', fn)
            if os.path.exists(p):
                for f in json.load(open(p)):
                    for c in f['coords']:
                        if len(c) > 1: add(ab_lines._xy(c), 1.6, 'b')
        for o in ontario():                                                # Ontario (the Lakehead collection): main lines 1.0, sidings and yards 1.6; the other railway's x2.5
            if o['kind'] != 'LineString' or len(o['coords']) < 2: continue
            if re.search(r'abandon\w*\s+(?:after|in|by)\b[^.]*\b1[89]\d\d|abandon\w*[^.]{0,80}\b19[0-4]\d', o.get('desc', ''), re.I): continue   # gone before 1948 (the GTP Westfort - Conmee main line, 1924; the PAD&W)
            ow = ont_owner(o['path']); main = 'Main line' in o['path'] or any(x in o['path'] for x in ('Ignace subdivision', 'Nepigon/Nipigon', 'Northern and Northwestern Railway'))
            fac = (1.0 if main else 1.6) * (2.5 if ow and ow != rail else 1.0)
            add(ab_lines._xy(o['coords']), fac, 'b', None if ow in (None, rail) else ow)
        if rail == 'cn':                                                   # CN (Duluth, Winnipeg & Pacific; Canadian National) in Minnesota, Brendan's KML (19 October)
            for fn in glob.glob(os.path.join(HERE, 'traces', 'cnmn', '*.geojson')):
                for f in json.load(open(fn))['features']: add(ab_lines._xy(f['geometry']['coordinates']), f['properties'].get('cost', 1.0), 'b')
            for a, b in (([-94.56805, 48.72259], [-94.59143, 48.71962]),    # the Rainy River: Rainy River (Ont.) - Baudette (Minn.)
                         ([-93.37882, 48.62238], [-93.35490, 48.61497])):   # the Rainy River: Duluth Junction (Fort Frances) - Ranier (Minn.)
                add(ab_lines._xy([a, b]), 1.0, 'b')
        for fn in glob.glob(os.path.join(HERE, 'traces', 'milw', '*.geojson')):   # Milwaukee Road, Minneapolis - St. Paul Union Station (Brendan, 19 October): drawn as Milwaukee
            for f in json.load(open(fn))['features']: add(ab_lines._xy(f['geometry']['coordinates']), f['properties'].get('cost', 1.0), 'b', f['properties'].get('own'))
        if rail == 'cp':                                                   # the C&NW, Chicago - St. Paul, for the Mountaineer (one CP train; 19 October): drawn as C&NW track
            for fn in glob.glob(os.path.join(HERE, 'traces', 'cnw', '*.geojson')):
                for f in json.load(open(fn))['features']: add(ab_lines._xy(f['geometry']['coordinates']), f['properties'].get('cost', 1.0), 'b', 'cnw')
        if rail == 'cp':                                                   # the Soo Line (CP-controlled) to Minneapolis, Brendan's KMZ (18 October)
            for fn in glob.glob(os.path.join(HERE, 'traces', 'soo', '*.geojson')):
                for f in json.load(open(fn))['features']: add(ab_lines._xy(f['geometry']['coordinates']), f['properties'].get('cost', 1.0), 'b')
        for fn in glob.glob(os.path.join(HERE, 'traces', 'saskatchewan', '*.geojson')):    # Brendan's traces of lines lifted since 1948 (both railways)
            for f in json.load(open(fn))['features']:
                c = f['geometry']['coordinates']; ow = f['properties'].get('own')             # 'own': the trace is that railway's (x2.5 for the other, drawn as its owner's)
                add(ab_lines._xy(c), f['properties'].get('cost', 1.0) * (2.5 if ow and ow != rail else 1.0), 'b', ow if ow and ow != rail else None)    # 'b': its points tie to track beside it (pieces join each other)
                for e in ((c[0], c[-1]) if f['properties'].get('join_ends') else ()):   # join a trace's ends to this railway's main track nearby (up to 1.5 km; the Regina link only)
                    q = _near_main(e, me)
                    if q: add(ab_lines._xy([e, q]), 1.0, 'n')
    return lambda: ab_lines.make_graph(feed, tie_end=150, tie_loose=60, tie_each=True)
REGINA = (-104.70, -104.45, 50.38, 50.48)                                  # Regina: CN trains used the Union Station tracks with CP in 1948
BATTLEFORDS = (-108.95, -108.0, 52.65, 53.35)                            # Rosemound - Battleford - North Battleford - Medstead: CP over CN track (joint; Brendan, 16 October)
HUMBOLDT = (-105.30, -104.95, 52.14, 52.26)                               # Humboldt: CP trackage rights over the CN line through town, to the CN station (Brendan, 16 October)
JOINT = {'cn': [REGINA], 'cp': [BATTLEFORDS, HUMBOLDT]}
CN_AS_OWN = [(-104.35, -103.88, 49.40, 49.72)]                            # (east edge short of Weyburn itself, 17 Oct: the CN must not wander into the CP station)                            # Weyburn - Radville: CN track, labelled CP in the network file (Brendan, 16 October)
def _in(b, p): return b[0] <= p[0] <= b[1] and b[2] <= p[1] <= b[3]
# ---------------------------------------------------------------- Ontario (Paul Delamere's Ontario Railway Map Collection, Brendan, 19 October 2026: "first rank")
ONT_OWN = {'Superior District': 'cp', 'Kaministiquita subdivision': 'cp', 'Keewatin subdivision': 'cp',
           'Ontario and Rainy River Railway': 'cn', 'Grand Trunk Pacific Railway': 'cn', 'Canadian Government Railway': 'cn', 'Port Arthur Duluth and Western Railway': 'cn'}
ONT_BOX = (-95.4, -84.0, 47.5, 51.5)                                       # the Lakehead and north-western Ontario (the collection also covers southern Ontario)
_ONT = []
def ontario():
    """[(path, name, kind, coords)] of traces/ontario/lakehead_all.json inside ONT_BOX"""
    if not _ONT:
        p = os.path.join(HERE, 'traces', 'ontario', 'lakehead_all.json')
        if os.path.exists(p):
            for o in json.load(open(p)):
                if all(_in(ONT_BOX, q) for q in o['coords'][::max(1, len(o['coords']) // 4)]): _ONT.append(o)
    return _ONT
def ont_owner(path): return next((ONT_OWN[x] for x in path if x in ONT_OWN), None)
_ONTST = {}
def ont_stations():
    """(owner, canon name) -> (lon, lat); also (None, canon name)"""
    if not _ONTST:
        for o in ontario():
            if o['kind'] != 'Point' or not any('Station' in x for x in o['path']) or not re.search(r'station\.?$|junction$', o['name'], re.I): continue
            n = canon(re.sub(r'\s*station\.?$', '', o['name'], flags=re.I)); q = tuple(o['coords'][0])
            _ONTST.setdefault((ont_owner(o['path']), n), q); _ONTST.setdefault((None, n), q)
    return _ONTST
def _near_main(e, me, lim=1500):
    best = None; x0, y0 = fwd(*e[:2])
    for f in nrwn():
        if not f['schema'].endswith('Track') or f['data'].get('trackClassification') != 'Main': continue
        if f['data'].get('operatorEnglishName', f['data'].get('ownerEnglishName')) != me: continue
        for c in f['coords']:
            for p in c:
                x, y = fwd(*p[:2]); d = math.hypot(x - x0, y - y0)
                if d > 5 and d < lim and (best is None or d < best[0]): best = (d, p[:2])
    return best[1] if best else None
ab_lines.EXT_GRAPH['sk:cn'] = _graph('cn')
ab_lines.EXT_GRAPH['sk:cp'] = _graph('cp')
MIDLAND = (-97.70, -96.90, 48.99, 49.853)  # the Midland Railway of Manitoba (GN and NP joint), the border to Winnipeg: drawn as GN track (Brendan, 18 October:
                                           # "they should be GN tracks"); north edge at Portage Junction (49.8522): CN track into Union Station beyond (Brendan, 18 Oct)
GRETNA = (-97.60, -97.52, 48.99, 49.02)    # GN trains into the CP station at Gretna over CP track (Brendan, 20 October): drawn as CP
def _us_graph(sub, links=()):
    """An American railway into Manitoba: Brendan's traces in traces/<sub> (Minnesota and North Dakota) and on in Manitoba over the network track
    (CN-operated today at cost 1.0, other track 1.5); links: short joins at the border between a trace's end and the network track"""
    def feed(add):
        for f in nrwn():
            if not f['schema'].endswith('Track'): continue
            op = f['data'].get('operatorEnglishName', f['data'].get('ownerEnglishName'))
            fac = {'Main': 1.0, 'Connecting': 1.0, 'Siding': 1.3}.get(f['data'].get('trackClassification'), 1.5) * (1.0 if op == 'Canadian National' else 1.5)
            for c in f['coords']:
                if len(c) > 1: add(ab_lines._xy(c), fac, 'n', 'cp' if op == 'Canadian Pacific' and any(_in(GRETNA, p) for p in c) else 'gn' if any(_in(MIDLAND, p) for p in c) else 'cn')
        for fn in glob.glob(os.path.join(HERE, 'traces', sub, '*.geojson')):
            for f in json.load(open(fn))['features']: add(ab_lines._xy(f['geometry']['coordinates']), f['properties'].get('cost', 1.0), 'b', f['properties'].get('own'))
        for a, b in links: add(ab_lines._xy([a, b]), 1.0, 'n', 'gn' if _in(MIDLAND, b) else 'cn')
    return lambda: ab_lines.make_graph(feed, tie_end=150, tie_loose=60, tie_each=True)
# NP: Manitoba Junction - Pembina (traces/np, from NP_Winnipeg.gpkg) and the border at Emerson: the end of the Pembina trace to the network's track (0.55 km)
ab_lines.EXT_GRAPH['sk:np'] = _us_graph('np', [([-97.23556, 49.00047], [-97.2355, 49.0054])])
# GN: St. Paul - Barnesville - Crookston - St. Vincent - Noyes and Grand Forks - Neche (traces/gn/gn_mn_nd.geojson, cut from Brendan's Great_Northern.kmz)
ab_lines.EXT_GRAPH['sk:gn'] = _us_graph('gn')
def _cnw_graph():
    """C&NW Chicago - Milwaukee - Adams - Wyeville - Eau Claire - Hudson - St. Paul (traces/cnw, Brendan's KMZ), then Milwaukee Road track to Minneapolis (traces/milw)"""
    def feed(add):
        for sub in ('cnw', 'milw'):
            for fn in glob.glob(os.path.join(HERE, 'traces', sub, '*.geojson')):
                for f in json.load(open(fn))['features']: add(ab_lines._xy(f['geometry']['coordinates']), f['properties'].get('cost', 1.0), 'b', f['properties'].get('own'))
    return lambda: ab_lines.make_graph(feed, tie_end=150, tie_loose=60, tie_each=True)
ab_lines.EXT_GRAPH['sk:cnw'] = _cnw_graph()
def _ww_graph():
    """the Greater Winnipeg Water District Railway, St. Boniface - Waugh: its own track in the network file (cost 1.0), other track only to reach St. Boniface"""
    def feed(add):
        for f in nrwn():
            if not f['schema'].endswith('Track'): continue
            op = f['data'].get('operatorEnglishName', f['data'].get('ownerEnglishName'))
            for c in f['coords']:
                if len(c) > 1: add(ab_lines._xy(c), 1.0 if op == 'Greater Winnipeg Water District' else 2.0, 'n', None if op == 'Greater Winnipeg Water District' else 'cn')
    return lambda: ab_lines.make_graph(feed, tie_end=150, tie_loose=60, tie_each=True)
ab_lines.EXT_GRAPH['sk:ww'] = _ww_graph()

# ---------------------------------------------------------------- names
def canon(n):
    """one spelling for the variants the tables print (No. Battleford, N. Battleford, North Battleford)"""
    n = unicodedata.normalize('NFKD', n).encode('ascii', 'ignore').decode().lower().strip()   # La Rivi\u00e8re = La Riviere
    n = re.sub(r'\s*\(.*?\)', '', n)
    n = re.sub(r'^(no\.|n\.)\s*', 'north ', n); n = re.sub(r'^(so\.|s\.)\s*', 'south ', n)
    n = n.replace('junc.', 'junction').replace('jct.', 'junction').replace('st.', 'st').replace('.', '').replace("'", '')
    return re.sub(r'\s+', ' ', n).strip()
PROV = {}                                                                 # station name -> province, from the tables
US_PROV = {o: {r['station']: (r.get('prov') or '') for _fn in glob.glob(os.path.join(HERE, f'sk_{o}_t*.csv')) for r in ab_table.load(_fn)['rows']} for o in ('np', 'gn', 'cnw')}   # (Davidson, Minn. is not Davidson, Sask.)
ROWS = {}
for fn in sorted(glob.glob(os.path.join(HERE, 'sk_c*_t*.csv')) + glob.glob(os.path.join(HERE, 'sk_np_t*.csv')) + glob.glob(os.path.join(HERE, 'sk_gn_t*.csv')) + glob.glob(os.path.join(HERE, 'sk_ww_t*.csv')) + glob.glob(os.path.join(HERE, 'skx_*.csv'))):
    for r in ab_table.load(fn)['rows']:
        PROV.setdefault(r['station'], (r.get('prov') or '').rstrip('?'))
        ROWS.setdefault(r['station'], r)

# ---------------------------------------------------------------- places
HAND = {('cn', 'winnipeg'): (-97.133408, 49.889092, 'Winnipeg Union Station (CN, GN, NP; Brendan)'),
        ('cp', 'winnipeg'): (-97.131634, 49.904986, 'Canadian Pacific station, Winnipeg (Brendan)'),
        ('cn', 'saskatoon'): (-106.666647, 52.127597, 'Canadian National station, Saskatoon (Brendan, 16 October)'),
        ('cp', 'saskatoon'): (-106.671011, 52.132486, 'Canadian Pacific station, Saskatoon (Brendan, 16 October)'),
        ('cn', 'north regina'): (-104.655567, 50.469514, 'old North Regina station, approximate (Brendan, 16 October)'),
        ('cn', 'north battleford'): (-108.2985, 52.7716, 'North Battleford station (shared; Brendan, 16 October)'),
        ('cp', 'north battleford'): (-108.2985, 52.7716, 'North Battleford station (shared; Brendan, 16 October)'),
        ('cn', 'lloydminster'): (-110.005968, 53.284654, 'Canadian National station, Lloydminster (Brendan, 16 October)'),
        ('cp', 'lloydminster'): (-110.003357, 53.285637, 'Canadian Pacific station, Lloydminster (Brendan, 16 October)'),
        # 17 October 2026 (Brendan, 20:18), staged for the next update
        ('cn', 'battleford'): (-108.315475, 52.735633, 'Battleford station (CN; CP trains used it; Brendan, 17 October)'),
        ('cp', 'battleford'): (-108.315475, 52.735633, 'Battleford station (CN; CP trains used it; Brendan, 17 October)'),
        ('cn', 'prince albert'): (-105.752418, 53.198852, 'Prince Albert union station (CN and CP; Brendan, 17 October)'),
        ('cp', 'prince albert'): (-105.752418, 53.198852, 'Prince Albert union station (CN and CP; Brendan, 17 October)'),
        ('cn', 'biggar'): (-107.9869, 52.0533, 'Canadian National station, Biggar (Brendan, 17 October)'),
        ('cn', 'yorkton'): (-102.467137, 51.212301, 'Canadian National station, Yorkton (approx.; Brendan, 17 October)'),
        ('cp', 'yorkton'): (-102.463366, 51.209872, 'Canadian Pacific station, Yorkton (approx.; Brendan, 17 October)'),
        ('cn', 'moose jaw'): (-105.5262, 50.3944, 'Canadian National station, Moose Jaw (Brendan, 17 October)'),
        ('cp', 'moose jaw'): (-105.5349, 50.3889, 'Canadian Pacific station, Moose Jaw (Brendan, 17 October)'),
        ('cn', 'estevan'): (-102.989748, 49.140096, 'Canadian National station, Estevan (end of Brendan\'s approach trace, approx.; 17 October)'),
        ('cp', 'estevan'): (-102.9932, 49.1424, 'Canadian Pacific station, Estevan (Brendan, 17 October)'),
        # Manitoba end stations (Brendan, 17 October 2026, 23:00; several approximate)
        ('cn', 'swan river'): (-101.2714, 52.105, 'Swan River (Brendan, 17 October; approx.)'),
        ('cn', 'flin flon'): (-101.879672, 54.765181, 'Flin Flon (Brendan, 17 October; approx.)'),
        ('cn', 'cranberry portage'): (-101.381776, 54.585582, 'Cranberry Portage (Brendan, 17 October; approx.)'),
        ('cn', 'sherridon'): (-101.090328, 55.127049, 'Sherridon (Brendan, 17 October; approx.)'),
        ('cp', 'binscarth'): (-101.287072, 50.624008, 'Binscarth (Brendan, 17 October; approx.)'),
        ('cn', 'russell'): (-101.279512, 50.780127, 'Russell (Brendan, 17 October; approx.)'),
        ('cp', 'russell'): (-101.279512, 50.780127, 'Russell (Brendan, 17 October; approx.)'),
        ('cp', 'elm creek'): (-97.992802, 49.677939, 'Elm Creek (Brendan, 17 October; approx.)'),
        ('gn', 'gretna'): (-97.560689, 49.007441, 'Gretna, the CP station: GN trains end there over CP track (Brendan, 20 October)'),
        ('cp', 'gretna'): (-97.560689, 49.007441, 'Gretna (Brendan, 17 October; approx.)'),
        ('cp', 'reston'): (-101.094291, 49.555459, 'Reston (Brendan, 17 October; approx.)'),
        ('cp', 'lauder'): (-100.678078, 49.391876, 'Lauder (Brendan, 17 October; approx.)'),
        ('cp', 'deloraine'): (-100.493962, 49.193152, 'Deloraine (Brendan, 17 October; approx.)'),
        ('cp', 'boissevain'): (-100.054508, 49.231058, 'Boissevain; trains backed in and out from the west (Brendan, 18 October)'),
        ('cp', 'lyleton'): (-101.182417, 49.058625, 'Lyleton, at the end of the line (Brendan, 18 October)'),
        ('cp', 'neepawa'): (-99.465316, 50.238353, 'Neepawa CP station (estimated; Brendan, 17 October)'),
        ('cn', 'neepawa'): (-99.473944, 50.228518, 'Neepawa CN station (Brendan, 17 October)'),
        ('cp', 'baljennie'): (-107.89894, 52.54083, 'Baljennie, at the end of the track (Sonningdale - end of track 15.1 mi by the track = printed; Brendan, 17 October)'),
        ('cp', 'schuler'): (-110.09927, 50.337, 'Schuler, at the end of its spur (Pivot - end of track 6.2 mi by the track, printed 6.0; the town point is in a lake; Brendan, 17 October)'),
        # by printed mileage along each railway's own line (joint-station review, Brendan 17 Oct 2026): separate stations
        ('cp', 'tisdale'): (-104.04674, 52.84186, 'Tisdale CP station, by its printed mileage (separate station; 17 October)'),
        ('cp', 'oban'): (-108.1468, 52.1291, 'Oban CP station, by its printed mileage (separate station; 17 October)'),
        ('cp', 'watson'): (-104.52917, 52.13167, 'Watson CP station, by its printed mileage (separate station; 17 October)'),
        ('cp', 'dodsland'): (-108.83747, 51.80397, 'Dodsland CP station, by its printed mileage (separate station; 17 October)'),
        ('cp', 'young'): (-105.75326, 51.76393, 'Young CP station, by its printed mileage (separate station; 17 October)'),
        ('cp', 'conquest'): (-107.24813, 51.53275, 'Conquest CP station, by its printed mileage (separate station; 17 October)'),
        ('cn', 'nokomis'): (-105.01004, 51.50613, 'Nokomis CN station, by its printed mileage (separate station; 17 October)'),
        ('cp', 'balcarres'): (-103.54398, 50.80068, 'Balcarres CP station, by its printed mileage (separate station; 17 October)'),
        ('cn', 'griffin'): (-103.43445, 49.66216, 'Griffin CN station, by its printed mileage (separate station; 17 October)'),
        ('cp', 'griffin'): (-103.43681, 49.6689, 'Griffin CP station, by its printed mileage (separate station; 17 October)'),
        ('cp', 'carlyle'): (-102.26643, 49.63608, 'Carlyle CP station, by its printed mileage (separate station; 17 October)'),
        ('cn', 'gladstone'): (-98.95415, 50.22698, 'Gladstone CN station, by its printed mileage (separate station; 17 October)'),
        ('cp', 'gladstone'): (-98.94726, 50.22538, 'Gladstone CP station, by its printed mileage (separate station; 17 October)'),
        ('cp', 'weyburn'): (-103.85917, 49.66037, 'Weyburn CP station, by its printed mileage (separate station; 17 October)'),
        ('cp', 'biggar'): (-108.0102, 52.07724, 'Biggar CP station, by its printed mileage (separate station; 17 October)'),
        ('cn', 'battleford junction'): (-108.3652, 52.8320, 'the junction west of North Battleford where Battleford trains reversed (Brendan, 16 October)'),
        ('cp', 'battleford junction'): (-108.3652, 52.8320, 'the junction west of North Battleford where Battleford trains reversed (Brendan, 16 October)'),
        ('cn', 'humboldt'): (-105.1251600, 52.1975487, 'Canadian National station, Humboldt (CP trains used it too; Brendan, 16 October)'),
        ('cp', 'humboldt'): (-105.1251600, 52.1975487, 'Canadian National station, Humboldt (CP trains used it too; Brendan, 16 October)'),
        ('cp', 'fir mountain'): (-106.553414, 49.385992, 'Fir Mountain, on the line Glentworth - Wood Mountain (Brendan, 16 October)'),
        ('cn', 'kelvington'): (-103.50627, 52.15953, 'on the Canadian Northern line at Kelvington (CN and CP ran side by side through town; Brendan, 16 October)'),
        ('cn', 'saskatoon loop'): (-106.672, 52.155, 'on the CN line round the west of Saskatoon: main-line trains looped out of the station by it (Brendan, 16 October)'),
        ('cp', 'brandon'): (-99.951447, 49.849933, 'Canadian Pacific station, Brandon (Brendan, 17 October)'),
        ('cn', 'melville'): (-102.807478, 50.926003, 'Canadian National station, Melville (Brendan, 17 October)'),
        ('cn', 'brandon'): (-99.950383, 49.846275, 'Canadian National (Canadian Northern) station, Brandon, at the Prince Edward Hotel, on its downtown spur (Brendan, 17 October)'),
        ('cn', 'melfort'): (-104.611536, 52.859442, 'Melfort station (CN; Brendan, 17 October)'),
        ('cp', 'melfort'): (-104.611536, 52.859442, 'Melfort station (CP, on its own line beside CN; Brendan, 17 October)'),
        ('cn', 'portage la prairie'): (-98.288247, 49.977393, 'Canadian National station, Portage la Prairie (Brendan, 17 October)'),
        ('cp', 'portage la prairie'): (-98.285903, 49.978187, 'Canadian Pacific station, Portage la Prairie (Brendan, 17 October)'),
        ('cn', 'regina talmage wye'): (-104.6435, 50.4676, 'wye west of North Regina: the south leg of the line to Estlin and Talmage (old GTP; Brendan, 19 October)'),
        ('cn', 'regina'): (-104.608727, 50.452737, 'Regina Union Station (CP and CN; Brendan, 15 October)'),
        ('cp', 'regina'): (-104.608727, 50.452737, 'Regina Union Station (CP and CN; Brendan, 15 October)'),
        ('np', 'winnipeg'): (-97.133408, 49.889092, 'Winnipeg Union Station (CN, GN, NP; Brendan)'),
        # Northern Pacific in Minnesota and North Dakota: the ends of Brendan's trace pieces (traces/np/np_winnipeg.geojson, 18 October); they also hold the
        # route to the line the trains used (Ulen - Fertile - Crookston - Carthage Junction - Grand Forks, not the direct Ulen - Grand Forks line)
        ('np', 'manitoba junction'): (-96.247, 46.907, 'Manitoba Junction, Minn. (start of Brendan\'s trace)'),
        ('np', 'fertile'): (-96.280, 47.549, 'Fertile, Minn. (end of Brendan\'s trace piece)'),
        ('np', 'crookston'): (-96.599, 47.776, 'Crookston, Minn. (end of Brendan\'s trace piece)'),
        ('np', 'carthage junction'): (-96.921, 47.935, 'Carthage Junction, Minn. (end of Brendan\'s trace piece)'),
        ('np', 'grand forks'): (-97.033178, 47.927156, 'Northern Pacific station, Grand Forks, N.D. (Brendan, 18 October)'),
        # Great Northern: ends of the named pieces of Brendan's Great_Northern.kmz (18 October), holding the route St. Paul - Minneapolis - Monticello -
        # St. Cloud - Alexandria - Fergus Falls - Barnesville - Crookston - Warren - St. Vincent; Grand Forks approximate (downtown)
        # Soo Line - Canadian Pacific, Table 91 (The Winnipeger): Minneapolis is the Milwaukee Road station (Brendan, 18 October); St. Paul Union Station as the GN's
        # (to be confirmed); Glenwood, Thief River Falls, Noyes: ends of the Soo KMZ pieces
        ('cp', 'minneapolis'): (-93.262422, 44.980150, 'Milwaukee Road station, Minneapolis (Brendan, 18 October)'),
        ('cp', 'st paul'): (-93.077064, 44.952704, 'St. Paul Union Station (end of Brendan\'s Milwaukee Road trace, 19 October)'),
        ('cp', 'glenwood'): (-95.377, 45.667, 'Glenwood, Minn. (Soo piece end)'),
        ('cp', 'thief river falls'): (-96.195, 48.160, 'Thief River Falls, Minn. (Soo piece end)'),
        ('cp', 'carberry'): (-99.35882628601715, 49.865718420529376, 'Carberry, the CP station on its own main line (Brendan, 20 October)'),
        ('cp', 'peebles'): (-102.94591771845234, 50.16037806363752, 'Peebles, the CP station on its own line, not the CN (Brendan, 21 October; probable)'),
        ('cp', 'holmfield'): (-99.48436884805724, 49.13680243250864, 'Holmfield, the CP station (Brendan, 20 October; est.)'),
        ('cn', 'virden'): (-100.9415454126535, 49.85645841333349, 'Virden, the CN station: APPROXIMATE, the end of Brendan\'s Belleview - Virden trace (20 October)'),
        ('cp', 'virden'): (-100.92930045017407, 49.850795887423615, 'Virden, the CP station (Brendan, 20 October)'),
        ('cp', 'noyes'): (-97.202881, 48.999178, 'Noyes, Minn., the joint Soo (CP) - GN depot (Brendan, 20 October)'),
        ('gn', 'noyes'): (-97.202881, 48.999178, 'Noyes, Minn., the joint Soo (CP) - GN depot (Brendan, 20 October)'),
        ('cp', 'emerson'): (-97.203364, 49.004692, 'Emerson, the CP depot, apart from the CN / GN station (Brendan, 20 October)'),
        ('cp', 'portal'): (-102.549, 48.999, 'Portal, N.D. (end of the Soo Portal piece at the border)'),
        ('gwwd', 'st boniface'): (-97.0999, 49.8932, 'Greater Winnipeg Water District Railway terminal, St. Boniface (Brendan, 19 October)'),
        ('cn', 'hudson bay jn'): (-102.39063155323439, 52.86308885494455, 'Hudson Bay Junction station, by the wye (Brendan, 20 October)'),
        ('cn', 'westside'): (-97.2012, 49.8835, "Westside (Portage Ave.), on the old line along St. James Street (Canadian Northern set); trains from Grosse Isle come down it and into Union Station from the south (Brendan, 19 October): APPROXIMATE, Portage Ave. crossing"),
        ('cp', 'port arthur'): (-89.217683, 48.434547, 'Canadian Pacific station, Port Arthur (Brendan, 19 October)'),
        ('cp', 'fort william'): (-89.24722, 48.37807, 'Canadian Pacific station, Fort William ("Thunder Bay station" in the Ontario Railway Map Collection; Brendan, 19 October)'),
        ('cp', 'dryden'): (-92.84031, 49.78557, 'Dryden station, Ontario Railway Map Collection (correctly located: Brendan, 19 October)'),
        ('cn', 'port arthur'): (-89.21808, 48.43375, "Prince Arthur's Landing station, CN Port Arthur (Ontario Railway Map Collection; Brendan, 19 October)"),
        ('cn', 'duluth'): (-92.10337, 46.78113, 'Duluth, Minn. (end of the DW&P Duluth terminal piece of Brendan\'s KML)'),
        ('cp', 'chicago'): (-87.64029, 41.88269, 'North Western Station, Chicago (Brendan, 19 October)'),
        ('cp', 'milwaukee'): (-87.899722, 43.038944, 'C&NW Lake Front Depot, Milwaukee (Brendan, 19 October)'),
        ('cnw', 'chicago'): (-87.64029, 41.88269, 'North Western Station, Chicago (Brendan, 19 October)'),
        ('cnw', 'milwaukee'): (-87.899722, 43.038944, 'C&NW Lake Front Depot, Milwaukee (Brendan, 19 October)'),
        ('cnw', 'st paul'): (-93.077064, 44.952704, 'St. Paul Union Station (end of Brendan\'s Milwaukee Road trace)'),
        ('cnw', 'minneapolis'): (-93.262422, 44.980150, 'Milwaukee Road station, Minneapolis (Brendan, 18 October)'),
        ('gn', 'winnipeg'): (-97.133408, 49.889092, 'Winnipeg Union Station (CN, GN, NP; Brendan)'),
        ('gn', 'st paul'): (-93.077064, 44.952704, 'St. Paul Union Station (end of Brendan\'s Milwaukee Road trace, 19 October)'),
        ('gn', 'minneapolis'): (-93.268, 44.986, 'Minneapolis, Great Northern station area (start of the GN Monticello piece)'),
        ('gn', 'alexandria'): (-95.369, 45.891, 'Alexandria, Minn. (GN piece end)'),
        ('gn', 'fergus falls'): (-96.075, 46.285, 'Fergus Falls, Minn. (GN piece end)'),
        ('gn', 'barnesville'): (-96.427, 46.665, 'Barnesville, Minn. (GN piece end)'),
        ('gn', 'warren'): (-96.748, 48.156, 'Warren, Minn. (GN piece end)'),
        ('gn', 'grand forks'): (-97.033647, 47.922247, 'Great Northern station, Grand Forks, N.D. (Brendan, 18 October; latitude read as 47 deg 55\' 20.09")')}
_MAP = {}
def _map():
    """stations already on the map (the Alberta lines at the boundary): (owner, canon name) -> (lon, lat, gid)"""
    if _MAP: return _MAP
    _MAP['x'] = True
    for L in json.load(open(os.path.join(HERE, 'viz_data.json')))['lines']:
        if L.get('water') or L['key'].startswith('sk'): continue
        for s in L['stations']:
            if s['lon'] > BOX[0] - 0.6 and s['lat'] < 56.5: _MAP.setdefault((L['owner'], canon(s['name'])), (s['lon'], s['lat'], s['gid']))
    return _MAP
_ST = {}
def _stations():
    if _ST: return _ST
    for f in nrwn():
        if not f['schema'].endswith('Station'): continue
        d = f['data']; nm = d.get('stationEnglishName')
        if not nm: continue
        user = d.get('stationUser1EnglishName', '')
        _ST.setdefault(canon(nm), []).append((f['coords'][0][0][0], f['coords'][0][0][1], 'cn' if 'National' in user else 'cp' if 'Pacific' in user else ''))
    return _ST
_CG = {}
_TRK = []
def _track_tree():
    if not _TRK:
        pts = [fwd(*p) for f in nrwn() if f['schema'].endswith('Track') for c in f['coords'] for p in c[::4]]
        pts += [fwd(*p) for c in _osm() for p in c[::4]]
        _TRK.append(cKDTree(np.array(pts)))
    return _TRK[0]
KINDS = {'City', 'Town', 'Village', 'Resort Village', 'Hamlet', 'Organized Hamlet', 'Locality', 'Community', 'Unincorporated Area', 'Railway Point',
         'Railway Junction', 'Post Office', 'Northern Village', 'Northern Hamlet', 'Former Locality', 'Abandoned Locality', 'Urban Community', 'Settlement'}
def _cgn():
    if _CG: return _CG
    for fn in (('cgn_sk', 'cgn_sk_csv_eng.csv'), ('cgn_mb', 'cgn_mb_csv_eng.csv')):     # Saskatchewan, and Manitoba (Brendan, 18 October 2026)
        p = os.path.join(HERE, 'places', *fn)
        if not os.path.exists(p): continue
        for r in csv.DictReader(open(p, encoding='utf-8-sig')):
            if r.get('Generic Term') in KINDS or r.get('Generic Category') == 'Populated Place':
                _CG.setdefault(canon(r['Geographical Name']), []).append((float(r['Longitude']), float(r['Latitude']), r['Generic Term'], fn[0][-2:].upper()))
    return _CG
ONT_ALIAS = {('cn', 'port arthur'): 'prince arthurs landing',   # CP Port Arthur, CP Fort William, CN Port Arthur: HAND (Brendan, 19 October); CN Fort William: the Vickers Street station (point asked)
             ('cn', 'kakabeka falls'): 'kakabaka falls', ('cn', 'superior junc'): 'superior junction', ('cp', 'bonheur'): 'bonheurstation',
             }
ALIAS = {'pine falls': 'powerview-pine falls', 'hudson bay jn': 'hudson bay', 'st agathe': 'ste agathe', 'tichfield': 'tichfield junction', 'whitebear': 'white bear', 'valmarie': 'val marie'}   # table spelling -> names file spelling
_AB = {}
def _ab():
    if not _AB:
        for r in csv.DictReader(open(os.path.join(HERE, 'places', 'cgn_ab_places.csv'))): _AB.setdefault(canon(r['name']), (float(r['lon']), float(r['lat']), r['kind']))
    return _AB
def place_for(rail):
    own = OWN[rail]
    def f(name):
        c = canon(name)
        if (own, c) in HAND: h = HAND[(own, c)]; return (h[0], h[1], 'hand', 600)
        if (US_PROV[own] if own in US_PROV else PROV).get(name, '') == 'ON':          # Ontario: the collection's stations only (first rank), else by mileage
            q = ont_stations().get((own, ONT_ALIAS.get((own, c), c))) or ont_stations().get((None, ONT_ALIAS.get((own, c), c)))
            return (q[0], q[1], 'ontario', 600) if q else None
        if (US_PROV[own] if own in US_PROV else PROV).get(name, '') in ('MN', 'ND', 'WI', 'IL'): return None   # United States: hand points or mileage only (Buffalo, Minn. is not Buffalo, Alta.)
        m = _map().get((own, c))
        if m: return (m[0], m[1], 'map', 300)
        prov = (US_PROV[own] if own in US_PROV else PROV).get(name, '')
        if prov in ('MN', 'ND'): return None                                # United States: hand points only, else by mileage
        r = ROWS.get(name)
        principal = r is not None and r.get('principal') == '1'
        st = [s for s in _stations().get(c, []) if s[2] in (own, '')] or _stations().get(c, [])
        if st and (prov != 'MB' or principal or os.path.exists(os.path.join(HERE, 'places', 'cgn_mb', 'cgn_mb_csv_eng.csv'))):
            s = min(st, key=lambda s: _track_tree().query(fwd(s[0], s[1]))[0]); return (s[0], s[1], 'network station', 800)
        if prov == 'MB' and not os.path.exists(os.path.join(HERE, 'places', 'cgn_mb', 'cgn_mb_csv_eng.csv')): return None   # no Manitoba names file: by mileage
        if prov == 'AB' or (c in _ab() and c not in _cgn()):                # the first Alberta station (and Acadia Valley, printed as Saskatchewan)
            a = _ab().get(c)
            if a: return (a[0], a[1], a[2], 2500)
        g = _cgn().get(ALIAS.get(c, c))
        if g and prov in ('SK', 'MB'): g = [q for q in g if q[3] == prov] or None   # the station's own province (Assiniboia, Sask. is not Assiniboia, Man.; 19 Oct)
        if g:
            g = min(g, key=lambda q: _track_tree().query(fwd(q[0], q[1]))[0])
            return (g[0], g[1], g[2], 4000 if g[2] == 'City' else 2500)
        return None
    return f
for _r in ('skcn', 'skcp', 'sknp', 'skgn', 'skww', 'skcnw'):
    ab_lines.EXT_PLACE[_r] = place_for(_r)
# the stop ids: one station for each spelling, and the station already on the map where there is one (so the lines meet)
for _r, _own in OWN.items():
    for _n in PROV:
        _m = _map().get((_own, canon(_n)))
        ab_lines.EXT_GID[(_r, _n)] = _m[2] if _m else ab_lines.RAILS[_r]['pfx'] + '_' + re.sub(r'\W+', '_', canon(_n).upper()).strip('_')
