"""Ontario and Quebec, 1948 (Brendan, 23 October 2026): track graphs and station places for the ab_lines.py machinery. A helper, imported by
on_build.py.

Track and stations come from Paul Delamere's collections, the only source besides the timetables (Brendan, 23 October 2026): the Ontario Railway
Map Collection (traces/ontario/ontario_all.json) and his Quebec collection (traces/quebec/quebec_all.json), both parsed from the KMZs by
tools/parse_kmz.py and kept in the private repository. Whose track a piece is comes from its folder (Canadian National, Canadian Pacific, Ontario
Northland, Algoma Central, ...). A railway's own main track costs 1.0, its sidings and yards 1.6, other railways' track 2.5 (drawn in their
colour), independent and American lines 1.5. Pieces whose note says they were abandoned before 1948, and the CN Toronto bypass (1960s), are left out.

Stations, in order: a point given by hand (HAND), a station of that railway already on the map (the Lakehead and Winnipeg lines), a station point of
the collection for that railway (the name is in the placemark's name or, often in Quebec, its description), any railway's station point of that name;
every other station goes by its printed mileage between located neighbours.

PROJECTION: ab_lines works in UTM zone 10 metres, which overstates lengths here by 8 % (Lakehead) to 18 % (Montreal), so the check of traced
against printed miles would fail. This module switches ab_lines to a Lambert conformal conic centred on Ontario (parallels 44 and 50 N, central
meridian 84 W; scale within about 0.5 % from 42 to 52 N) for this step only: on_build.py runs in its own process. Graph names start 'sk:' so that
ab_lines' fallback to the shortest route by distance (written for Saskatchewan) applies here too."""
import json, math, os, re, unicodedata
import numpy as np
from pyproj import Transformer
from scipy.spatial import cKDTree
import ab_lines
HERE = os.path.dirname(os.path.abspath(__file__))

_T = Transformer.from_crs(4326, '+proj=lcc +lat_1=44 +lat_2=50 +lon_0=-84 +lat_0=46 +datum=WGS84 +units=m +no_defs', always_xy=True)
_I = Transformer.from_crs('+proj=lcc +lat_1=44 +lat_2=50 +lon_0=-84 +lat_0=46 +datum=WGS84 +units=m +no_defs', 4326, always_xy=True)
ab_lines.fwd, ab_lines.inv = _T.transform, _I.transform
ab_lines._T, ab_lines._I = _T, _I                                      # _xy() uses the transformer itself
fwd = _T.transform
ab_lines.TZ_SHIFT['E'] = -10800
ab_lines.TZ_SHIFT['A'] = -14400                                        # Atlantic time (the Temiscouata)                                        # Eastern time: three hours ahead of Pacific

ab_lines.RAILS.update({'oncn': dict(kind='q', label='Canadian National', own='cn', agency='CN', color='2F6B44', pfx='CN'),
                       'oncp': dict(kind='p', label='Canadian Pacific', own='cp', agency='CP', color='7A1E2C', pfx='CP'),
                       'onr': dict(kind='h', label='Ontario Northland', own='onr', agency='ONR', color='FEBC11', pfx='ONR'),          # colour: Brendan, 23 Oct 2026 (today's ONR yellow)
                       'acr': dict(kind='z', label='Algoma Central', own='acr', agency='ACR', color='8A3B12', pfx='ACR'),           # colour: Claude's pick
                       'onnyc': dict(kind='t', label='New York Central', own='nyc', agency='NYC', color='3D3D3D', pfx='NYC'),      # dark grey: Brendan, 24 Oct 2026
                       'ondh': dict(kind='f', label='Delaware & Hudson', own='dh', agency='DH', color='0F6FA8', pfx='DH'),         # colour: Claude's pick
                       # Quebec's independent railways (Official Guide, 1948; Brendan, 25 Oct 2026); colours Claude's picks
                       'ontem': dict(kind='T', label='Temiscouata', own='tem', agency='TEM', color='9C2F6B', pfx='TEM'),
                       'oncgt': dict(kind='G', label='Canada & Gulf Terminal', own='cgt', agency='CGT', color='5A5EA8', pfx='CGT'),
                       'onrs': dict(kind='R', label='Roberval & Saguenay', own='rs', agency='RS', color='1B7F5C', pfx='RS'),
                       'onnyco': dict(kind='t', label='New York Central', own='nyc', agency='NYC', color='3D3D3D', pfx='NYC'),   # NYC Ottawa - Helena (Brendan's Table 73 transcription)
                       'oncpcn': dict(kind='p', label='Canadian Pacific', own='cp', agency='CP', color='7A1E2C', pfx='CP'),   # CP pool trains over the CN (Table 49)
                       'onthb': dict(kind='B', label='Toronto, Hamilton & Buffalo', own='thb', agency='THB', color='6A4048', pfx='THB'),   # Brendan, 27 Oct 2026: its own colour, between CP and NYC (CP-filed, NYC majority-owned)
                       'oncpthb': dict(kind='p', label='Canadian Pacific', own='cp', agency='CP', color='7A1E2C', pfx='CP'),   # CP Toronto - Hamilton trains (Table 56): CN Lake Shore, then TH&B
                       'onlps': dict(kind='P', label='London & Port Stanley', own='lps', agency='LPS', color='1C2F5E', pfx='LPS'),   # electric interurban, City of London; dark blue and gold (Brendan, 28 Oct 2026)
                       'ongrr': dict(kind='E', label='Grand River Railway (CP electric)', own='grr', agency='GRR', color='7A1E2C', pfx='GRR'),   # CP electric lines: CP colours, drawn as interurbans (Brendan, 29 Oct 2026)
                       'onlen': dict(kind='E', label='Lake Erie & Northern (CP electric)', own='len', agency='LEN', color='7A1E2C', pfx='LEN'),
                       'oncnfy': dict(kind='v', label='Quebec – Levis ferry', own='cnfy', agency='CN', color='2F6B44', pfx='CNFY'),   # the ferry with the CN trains (CN Table 1; Brendan, 29 Oct 2026)
                       'onaj': dict(kind='J', label='Alma & Jonquiere', own='aj', agency='AJ', color='4A6D8C', pfx='AJ')})
OWN = {'oncn': 'cn', 'oncp': 'cp', 'onr': 'onr', 'acr': 'acr', 'onnyc': 'nyc', 'ondh': 'dh', 'ontem': 'tem', 'oncgt': 'cgt', 'onrs': 'rs', 'onaj': 'aj', 'oncpcn': 'cpcn', 'onnyco': 'nyc', 'onthb': 'thb', 'oncpthb': 'cpthb', 'onlps': 'lps', 'ongrr': 'grr', 'onlen': 'len', 'oncnfy': 'cnfy'}
# the New York Central and the Delaware & Hudson (CP Table 18) run over the CP from Windsor Station; the NYC leaves it at Adirondack Junction for its
# own St. Lawrence & Adirondack line, the D&H follows the CP to the end of its track at the border (Brendan, 24 Oct 2026). Both stop at the border for now.

# ---------------------------------------------------------------- the collections
_D = []
def pieces():
    if not _D:
        for sub, fn in (('ontario', 'ontario_all.json'), ('quebec', 'quebec_all.json')):
            p = os.path.join(HERE, 'traces', sub, fn)
            if os.path.exists(p): _D.extend(json.load(open(p)))
    return _D
def owner(path):
    """whose track (or station) a piece of the collections is, from its folders"""
    top = path[2] if len(path) > 2 else ''
    sub = ' / '.join(path[3:])
    if 'Ontario Northland' in sub: return 'onr'
    if 'Algoma Central' in sub: return 'acr'
    if 'Algoma Eastern' in sub: return 'cp'
    if 'Temiscouata Railway' in sub: return 'tem'                       # independent until 1949 (the collection files it under CN)
    if 'Matap' in sub and 'Gulf' in sub: return 'cgt'                   # Canada & Gulf Terminal (filed under CN as the Matapedia and Gulf)
    if 'Alma and Jonquiere' in sub: return 'aj'
    if sub.startswith('Roberval and Saguenay'): return 'rs'
    if 'New York Central' in sub: return 'nyc'                          # the St. Lawrence & Adirondack (Adirondack Junction - Valleyfield - Huntingdon - border)                             # Sudbury - McKerrow - Little Current: CP from 1930
    if 'London and Port Stanley' in sub: return 'lps'                     # electric, City of London (filed under CN)
    if 'Toronto Hamilton and Buffalo' in sub: return 'thb'               # filed under CP (NYC majority-owned in 1948)
    if top.startswith('American railroads') and sub.startswith('Canada Southern'): return 'nyc'   # Michigan Central (NYC) in Ontario
    if top.startswith('Canadian National'): return 'cn'
    if top.startswith('Canadian Pacific'): return 'cp'
    return None
_GONE = re.compile(r'(?:abandon\w*|lifted|removed|closed)\s+(?:in\s+|by\s+|after\s+|c\.\s*)?(?:18\d\d|19[0-4]\d)\b', re.I)
class _Gone:                                                            # a piece abandoned before 1948, by its own note ("abandoned in 1924")
    @staticmethod
    def search(desc):                                                   # the long "Location: ..." railway histories mention old dates near
        return None if desc.lstrip().startswith('Location') else _GONE.search(desc)   # "abandoned" for other parts: not used to drop the piece
GONE = _Gone()
LATER = re.compile(r'Toronto bypass', re.I)                              # the CN bypass and MacMillan Yard (1960s)
def label(o):
    n = o.get('name') or ''
    if not n or n in ('Canadian Pacific Railway', 'Canadian National Railway', 'Untitled Placemark'): n = (o.get('desc') or '').split('\n')[0]
    return n.strip()

# ---------------------------------------------------------------- track
def despike(c):
    """drop single stray vertices: a point far (over 400 m) from both its neighbours while they are close together (under 80 m). The collections
    have a few (the ONR Noranda branch near Bear Lake jumped 2 miles north and back, 4.4 mi of false track; Brendan, 23 October 2026)."""
    if len(c) < 3: return c
    kx = 111320 * math.cos(math.radians(c[0][1])); d = lambda a, b: math.hypot((a[0] - b[0]) * kx, (a[1] - b[1]) * 110540)
    out = [c[0]]
    for i in range(1, len(c) - 1):
        if d(c[i - 1], c[i + 1]) < 80 and d(c[i], c[i - 1]) > 400 and d(c[i], c[i + 1]) > 400: continue
        out.append(c[i])
    return out + [c[-1]]
def _links():
    out = []
    for fn in sorted(__import__('glob').glob(os.path.join(HERE, 'traces', 'ontario', 'brendan', '*.geojson'))): out += json.load(open(fn))['features']
    return out
BOXES = {'onr': (-82.6, -78.4, 43.5, 51.5), 'acr': (-85.2, -82.8, 46.3, 49.9), 'nyc': (-74.4, -73.4, 44.9, 45.6), 'dh': (-74.0, -73.2, 44.95, 45.6),
         'tem': (-69.7, -68.3, 47.3, 47.95), 'nyco': (-75.8, -74.6, 44.9, 45.5), 'cgt': (-68.4, -67.4, 48.5, 48.95), 'rs': (-71.4, -70.8, 48.25, 48.5), 'aj': (-71.9, -71.5, 48.4, 48.8), 'thb': (-80.5, -78.85, 42.85, 43.75), 'cpthb': (-80.5, -78.85, 42.85, 43.75), 'lps': (-81.35, -81.05, 42.6, 43.05), 'grr': (-80.56, -80.28, 43.33, 43.48), 'len': (-80.42, -80.18, 42.76, 43.38), 'cnfy': (-71.25, -71.15, 46.79, 46.83)}   # the small railways' graphs: their own part of the map only
def _graph(me):
    """the track graph for one railway. Every piece goes in as network-like track ('n': its ends tie to track within 150 m) rather than as a backup
    ('b': every point tied to track beside it), and other railways' sidings and yards are left out: the full collections as backups made graphs of
    about two million points each, more than the machine holds four of (23 October 2026)."""
    box = BOXES.get(me)
    def covered(c):                                                     # a collection piece that one of the links replaces (same ends, within 120 m)
        kx = 111320 * math.cos(math.radians(c[0][1])); d = lambda p, q: math.hypot((p[0] - q[0]) * kx, (p[1] - q[1]) * 110540)
        return any(f['properties'].get('replaces') and ((d(c[0], g[0]) < 120 and d(c[-1], g[-1]) < 120) or (d(c[0], g[-1]) < 120 and d(c[-1], g[0]) < 120))
                   for f in _links() for g in [f['geometry']['coordinates']])
    def feed(add):
        for o in pieces():
            if o['kind'] != 'LineString' or len(o['coords']) < 2: continue
            if GONE.search(o.get('desc', '')) or any(LATER.search(x) for x in o['path']) or 'Pelletierjunction to near St. Andre' in (o.get('desc') or ''): continue   # NTR Pelletier - St. Andre: built after 1948 (Brendan, 29 Oct 2026)
            c = despike(o['coords'])
            if len(c) > 3 and covered(c): continue
            if box and not any(box[0] <= p[0] <= box[1] and box[2] <= p[1] <= box[3] for p in c[::max(1, len(c) // (6 if me in ('onr', 'acr') else 200))]) \
               and not any(box[0] <= p[0] <= box[1] and box[2] <= p[1] <= box[3] for p in (c[0], c[-1])): continue
            ow = owner(o['path']); side = any(re.search(r'siding|yard|spur', x, re.I) for x in o['path'])
            if me in ('thb', 'cpthb'):                                      # Table 56: CN Lake Shore (CP / TH&B trackage rights), TH&B, the NYC (Michigan Central) to Fort Erie
                if ow not in ('cn', 'cp', 'thb', 'nyc') or side: continue
                fac, draw = 1.0, (None if ow == me else ow)
            elif me == 'nyco':                                                # NYC Ottawa line: its own track; other railways' main lines dear
                if ow != 'nyc' or side: continue                            # its own main line only (CN / CP track and NYC sidings beside it caught the stations)
                fac, draw = 1.0, None
            elif me == 'cpcn' and ow in ('cp', 'cn'):                         # Pool 15 / 6 (CP Table 49): Windsor Station over the CP to Dorval, then the CN to Toronto
                if side and not any(re.search(r'main', x, re.I) for x in o['path']): continue   # "Toronto Montreal - Mainline and sidings" is the main line
                fac, draw = 1.0, ow
            elif ow == me: fac, draw = (1.6 if side else 1.0), None
            elif me in ('nyc', 'dh') and ow == 'cp': fac, draw = (1.6 if side else 1.0), 'cp'   # over the CP from Windsor Station (its yard tracks join the Adirondack line at Montreal West)
            elif side: continue
            elif me == 'onr' and ow == 'cn': fac, draw = 1.2, 'cn'           # ONR trains run Toronto - North Bay over the CN
            elif me in ('nyc', 'dh') and ow == 'nyc': fac, draw = 2.5, 'nyc'
            elif ow in ('cn', 'cp', 'onr', 'acr', 'thb', 'lps', 'nyc', 'grr', 'len'): fac, draw = 2.5, ow
            else: fac, draw = 1.5, None
            add(ab_lines._xy(c), fac, 'n', draw)
        for f in _links():                                              # Brendan's traces and connectors (traces/ontario/brendan/)
            ow = f['properties']['own']; c = f['geometry']['coordinates']
            if box and not any(box[0] <= p[0] <= box[1] and box[2] <= p[1] <= box[3] for p in c): continue
            mine = ow == me or (me == 'cpcn' and ow in ('cp', 'cn')) or (me == 'nyco' and ow == 'nyc') or (me in ('thb', 'cpthb') and ow in ('cn', 'cp', 'thb', 'nyc'))
            add(ab_lines._xy(c), f['properties'].get('cost', 1.0) if mine else 2.5, 't', None if ow == me else ow)   # 'cost': a link the trains must take (cheaper than the track beside it)
    return lambda: ab_lines.make_graph(feed, tie_end=150, tie_loose=60)
for _r, _o in OWN.items(): ab_lines.EXT_GRAPH['sk:' + _r] = _graph(_o)
ab_lines.EXT_GRAPH['sk:onnyco'] = _graph('nyco')

# ---------------------------------------------------------------- names
def canon(n):
    n = unicodedata.normalize('NFKD', n).encode('ascii', 'ignore').decode().lower().strip()
    n = re.sub(r'\s*\(.*?\)', '', n)
    n = re.sub(r',\s*(ont|que|mich|wis|minn)\.?$', '', n)                   # "Sault Ste. Marie, Ont."
    n = re.sub(r'^(gare|care)\s+', '', n)                                # Quebec: "Gare Mont-Joli station"
    n = re.sub(r'\b(station|flag stop)\b\.?', '', n)
    n = re.sub(r'^(?:\d(?:st|nd|rd|th)|deux)\s+', '', n)                 # "1st Windsor station", "Gare deux Drummondville station 1st"
    n = re.sub(r'\s+\d(?:st|nd|rd|th)$', '', n)
    n = n.replace('junc.', 'junction').replace('jct.', 'junction').replace('jct', 'junction').replace('st.', 'st ').replace('ste.', 'ste ')
    n = n.replace('-', ' ').replace('.', ' ').replace("'", '')
    return re.sub(r'\s+', ' ', n).strip()

# ---------------------------------------------------------------- places
# Points given by hand: APPROXIMATE, Claude's from general knowledge, to be confirmed by Brendan (the collections have no point for them)
_TU = (-79.380688, 43.645186, 'Toronto Union Station (the collection\'s "2nd Toronto Union station"; Brendan, 23 Oct 2026)')
_HUNTER = (-79.8691523, 43.253237, 'TH&B Hamilton (Hunter Street) station: the collection\'s "2nd West Hamilton station" (TH&B, filed under CP; Brendan, 27 Oct 2026)')
_FE = (-78.9163205, 42.9283318, 'Fort Erie (NYC / Michigan Central), the collection\'s Bridgeburg station by the International Bridge (Bridgeburg was renamed Fort Erie in 1932)')
HAND = {('thb', 'toronto'): _TU, ('cpthb', 'toronto'): _TU, ('thb', 'hamilton'): _HUNTER, ('cpthb', 'hamilton'): _HUNTER, ('cp', 'hamilton'): _HUNTER, ('thb', 'fort erie'): _FE,
        ('thb', 'welland'): (-79.2503608, 42.9765386, 'Welland (NYC / Michigan Central station used by the TH&B), APPROXIMATE: the collection\'s Welland point by the Canada Southern'),
        ('thb', 'waterford'): (-80.29625, 42.93341, 'TH&B Waterford = the NYC (Canada Southern) Waterford station (Brendan, 29 Oct 2026): the TH&B trains run through the BW&LE wye onto the NYC'),
        ('cp', 'cataract'): (-80.018278, 43.828291, 'CP Cataract: where Table 62 placed it by mileage (no point in the collection); junction for the Elora line (Table 63)'),
        ('cp', 'wingham'): (-81.3195, 43.8872, 'CP Wingham: the end of the Wingham branch (the collection\'s point is the CN station)'),
        ('cp', 'wingham junction'): (-81.2474, 43.9239, 'CP Wingham Jct.: where the Wingham branch leaves the Teeswater line, by Glenannan (Claude, from the miles: Wingham Jct. 124.7, Wingham 129.2, Glenannan 134.1)'),
        ('cp', 'st thomas'): (-81.1860511, 42.7779249, 'CP St. Thomas = the NYC (Michigan Central) station (Brendan, 29 Oct 2026); the collection\'s point'),
        ('cn', 'st hyacinthe'): (-72.9391349, 45.6298369, 'CN St. Hyacinthe, on the main line (the collection\'s point is off the line, 1.9 km west); APPROXIMATE, Claude'),
        ('cn', 'ste rosalie junction'): (-72.9091837, 45.6363857, 'CN Ste. Rosalie Junction: where the Drummondville line (Drummond County Railroad) meets the St. Lawrence & Atlantic'),
        ('cn', 'ste rosalie'): (-72.8940748, 45.6399046, 'CN Ste. Rosalie, on the Drummondville line 0.4 mi from the junction (by the printed miles); APPROXIMATE, Claude'),
        ('cn', 'bridge street'): (-73.5515986, 45.4843264, 'CN Bridge Street, Montreal (Pointe St. Charles), on the main line; APPROXIMATE, Claude (the collection\'s Bridge Street is Ottawa\'s)'),
        ('cn', 'nicolet'): (-72.6095388, 46.2280408, 'CN Nicolet, on the branch from St. Leonard (the collection files it as abandoned sidings); APPROXIMATE, Claude'),
        ('cn', 'st johns'): (-73.2546656, 45.3031519, 'CN St. Johns (St. Jean), on the Rouses Point subdivision (no point in the collection); APPROXIMATE, Claude'),
        ('cn', 'cantic'): (-73.3494352, 45.0640152, 'CN Cantic = the collection\'s Lacolle Junction: where the Central Vermont line to East Alburgh leaves the Rouses Point line; APPROXIMATE'),
        ('cn', 'chambord'): (-72.0554882, 48.421918, 'CN Chambord (Junction): where the Roberval line leaves the Lac St. Jean line; the end of the collection\'s Roberval subdivision'),
        ('cn', 'st charles'): (-70.9473, 46.7724, 'CN St. Charles (de Bellechasse): the collection\'s point on the Intercolonial (it has a second St. Charles at Quebec)'),
        ('cp', 'toronto'): _TU, ('cn', 'toronto'): _TU, ('onr', 'toronto'): _TU,
        ('cp', 'montreal'): (-73.567980, 45.497179, 'Windsor Station, Montreal (the collection\'s "Gare Windsor station"; Brendan, 23 Oct 2026)'),
        ('cn', 'montreal'): (-73.567251, 45.500458, 'Central Station, Montreal (the collection\'s "Gare Centrale station"; Brendan, 23 Oct 2026)'),
        ('cn', 'quebec'): (-71.213860, 46.817443, 'Quebec, Palais Station (the collection\'s "Gare Palais station"; Brendan, 23 Oct 2026)'),
        ('cn', 'capreol'): (-80.928981, 46.710925, 'Capreol (Brendan, 23 Oct 2026)'),
        ('cn', 'field'): (-80.0243, 46.5235, 'Field, Ont., on the CN North Bay - Capreol line (Brendan, 23 Oct 2026: approximately)'),
        ('cn', 'taschereau'): (-78.680875, 48.662350, 'Taschereau (Brendan, 23 Oct 2026: not sure, for now)'),
        ('cp', 'ypres'): (-79.843000, 44.261342, 'Ypres, junction for Camp Borden (Brendan, 23 Oct 2026)'),
        ('cn', 'noranda rouyn'): (-79.026961, 48.246808, 'CN Noranda-Rouyn (Brendan, 23 Oct 2026, estimate)'),
        ('cp', 'port arthur'): (-89.217683, 48.434547, 'Canadian Pacific station, Port Arthur (Brendan, 19 October)'),
        ('cp', 'fort william'): (-89.24722, 48.37807, 'Canadian Pacific station, Fort William (Brendan, 19 October)'),
        ('cp', 'lanoraie'): (-73.315943, 45.992274, 'Lanoraie, on the main line beside the collection\'s station point (its other "Lanoraie" is the old village end of the abandoned branch)'),
        ('cp', 'montreal park avenue'): (-73.6240, 45.5307, 'Park Avenue Station, Montreal (Claude, approximate: Park Avenue at the CP line; no point in the collection)'),
        ('cp', 'boundary'): (-70.7015, 45.5446, 'Boundary, Que. (CP Table 10): the middle of the collection\'s "Boundry siding", by the border (Claude, to confirm)'),
        ('cp', 'vaudreuil'): (-74.0084965, 45.3865095, 'Vaudreuil (Dorion): the CP station of 1948 is the collection\'s "Dorion" (its "Vaudreuil" is the modern commuter station; Brendan, 25 Oct 2026)'),
        ('tem', 'international boundary'): (-68.4807425, 47.487259, 'the end of the Temiscouata track in the Quebec collection, at the New Brunswick line'),
        ('tem', 'ste rose'): (-68.6395756, 47.5488634, 'Ste. Rose (du Degele), the collection\'s point'),
        ('rs', 'arvida'): (-71.1656, 48.4259, 'Arvida, by the Roberval & Saguenay roundhouse (Claude, approximate: no station point in the collection)'),
        ('aj', 'saguenay power'): (-71.6365122, 48.4483422, 'Saguenay Power: the south end of the Alma & Jonquiere main line, at the CN (Hebertville Jct.; Claude, approximate)'),
        ('cn', 'cornwall'): (-74.7434434, 45.0421843, 'Cornwall CN, on the main line beside the collection\'s station point (which snaps to a siding)'),
        ('cp', 'brockville'): (-75.692842, 44.591217, 'Brockville Union Station (CN and CP; Brendan, 25 Oct 2026): CP trains run on from the end of the CP line down the CN track'),
        ('cn', 'brockville'): (-75.692842, 44.591217, 'Brockville Union Station (CN and CP; Brendan, 25 Oct 2026)'),
        ('cp', 'leaside'): (-79.3578985, 43.7028199, 'CP Leaside, the collection\'s point (Brendan, 25 Oct 2026: it had been placed by mileage on the North Toronto line)'),
        ('cn', 'allandale'): (-79.689458, 44.3767402, 'CN Allandale (Barrie), APPROXIMATE: Claude, on the CN main line by the junction with the Collingwood line (no point in the collection)'),
        ('cn', 'camp borden'): (-79.8984, 44.2678, 'CN Camp Borden, APPROXIMATE: Claude, the end of the Grand Trunk spur from Angus (no point in the collection)'),
        ('cp', 'don'): (-79.3544042, 43.6576529, 'CP Don station, the collection\'s point, on the Leaside - Union connector'),
        ('nyc', 'cornwall'): (-74.7509129, 45.0151306, 'NYC Cornwall, on the NYC main line beside the collection\'s point (which snaps to a siding or other track)'),
        ('nyc', 'cornwall junction'): (-74.7598314, 45.025622, 'NYC Cornwall Junction, on the NYC main line beside the collection\'s point (which snaps to a siding or other track)'),
        ('nyc', 'uscan'): (-74.7422455, 44.9992329, 'NYC Uscan, on the NYC main line beside the collection\'s point (which snaps to a siding or other track)'),
        ('nyc', 'helena'): (-74.72524822374909, 44.92622056365477, 'Helena, N.Y.: the end of Brendan\'s trace (25 Oct 2026)'),
        ('nyc', 'rooseveltown'): (-74.73355, 44.98045, 'Rooseveltown, N.Y., on Brendan\'s trace at the bridge (Claude, approximate)'),
        ('nyc', 'international boundary'): (-74.2423085, 44.9921679, 'the end of the St. Lawrence & Adirondack trace in the Quebec collection, at the border (Brendan, 24 Oct 2026)'),
        ('dh', 'international boundary'): (-73.3727996, 45.0103103, 'the end of CP track toward Rouses Point (Brendan, 24 Oct 2026)')}
_MAP = {}
def _map():
    """stations already on the map in north-western Ontario (the Lakehead lines; not Minnesota or Wisconsin: Eau Claire, Wis. is not Eau Claire, Ont.)"""
    if not _MAP:
        _MAP['x'] = True
        p = os.path.join(HERE, 'viz_data.json')
        for L in (json.load(open(p))['lines'] if os.path.exists(p) else []):
            if L.get('water') or L['key'].startswith('on'): continue
            for s in L['stations']:
                if -95.5 < s['lon'] < -84.0 and 48.0 < s['lat'] < 52.0: _MAP.setdefault((L['owner'], canon(s['name'])), (s['lon'], s['lat'], s['gid']))
    return _MAP
_ST = {}
def stations():
    """(owner, canon name) -> [(lon, lat)] of the collections' station points; also (None, canon)"""
    if not _ST:
        for o in pieces():
            if o['kind'] != 'Point': continue
            lb = label(o)
            if not (any('station' in x.lower() for x in o['path']) or re.search(r'\bstation\b|\bgare\b', lb, re.I)): continue
            if re.search(r'bridge|culvert|tower|roundhouse|shed', ' '.join(o['path']), re.I) and not re.search(r'station|gare', lb, re.I): continue
            c = canon(lb)
            if not c: continue
            q = tuple(o['coords'][0][:2]); ow = owner(o['path'])
            _ST.setdefault((ow, c), []).append(q); _ST.setdefault((None, c), []).append(q)
    return _ST
_TRK = {}
def track_tree(own):
    if own not in _TRK:
        pts = [fwd(*p[:2]) for o in pieces() if o['kind'] == 'LineString' and owner(o['path']) == own for p in o['coords'][::3]]
        _TRK[own] = cKDTree(np.array(pts)) if pts else None
    return _TRK[own]
ALIAS = {('nyc', 'harrison'): 'harrisons corners', ('nyc', 'helena, n y'): 'helena', ('nyc', 'rooseveltown, n y'): 'rooseveltown', ('nyc', 'ottawa'): 'ottawa mann avenue',('aj', 'isle maligne'): 'ile maligne', ('aj', 'st joseph dalma'): 'st joseph de alma', ('rs', 'laterriere junction'): 'laterriere junction',('cn', 'hervey'): 'hervey junction', ('cn', 'severn'): 'severn bridge', ('cn', 'muskoka wharf'): 'gravenhurst wharf', ('cn', 'scotia'): 'scotia junction', ('cn', 'penetang'): 'penetanguishene', ('cn', 'coteau'): 'coteau junction', ('onr', 'porquis'): 'porquis junction',
         ('cp', 'port mcnicoll'): 'port mcnicoll main', ('onr', 'timmins'): 'timmons', ('onr', 'beaver lake'): 'bear lake', ('cn', 'ottawa'): 'ottawa union', ('cp', 'ottawa'): 'ottawa union',
         ('cp', 'clearys'): 'cleary', ('cp', 'tourvilles'): 'tourville', ('cp', 'sutton'): 'sutton flats',
         ('cp', 'st guillaume'): 'st guillaume junction',
         ('cp', 'south stukely'): 'stukely south', ('cp', 'st johns'): 'st jean sur richelieu', ('cp', 'iberville'): 'iberville junction',
         ('cp', 'montreal place viger'): 'viger', ('cp', 'de sales'): 'st francois de sales', ('cp', 'berthier'): 'berthierville', ('cp', 'quebec'): 'palais',
         ('cp', 'grandmere'): 'grand mere', ('cp', 'grandes piles'): 'grand piles', ('cp', 'les gres'): 'gres', ('cp', 'la gabelle'): 'gabelle',
         ('cp', 'garneau'): 'garneau junction', ('cp', 'timiskaming'): 'temiscaming',
         ('cp', 'lac frontiere'): 'frontiere', ('cp', 'megantic'): 'lac megantic', ('cp', 'scotts junction'): 'scott junction', ('cp', 'thetford mines'): 'thetford',
         ('cp', 'st joseph'): 'st joseph de beauce', ('cp', 'mcleods'): 'mcleod crossing', ('cp', 'trudel'): 'trudell', ('cp', 'beebe junction'): 'beebe junction'}   # CP Tables 8, 10   # CP Tables 33-37   # CP Tables 23-24   # CP Tables 19-22   # table name -> collection name
def place_for(rail):
    own = OWN[rail]
    def f(name):
        c = canon(name); c = ALIAS.get((own, c), c)
        if (own, c) in HAND: h = HAND[(own, c)]; return (h[0], h[1], 'hand', 800)
        if own == 'dh' or (own == 'nyc' and c in ('montreal', 'westmount', 'montreal west')): return place_for('oncp')(name)
        if own == 'cpcn': return place_for('oncp')(name) if c.startswith('montreal') or c in ('westmount', 'toronto', 'toronto union') else (place_for('oncn')(name) or place_for('oncp')(name))          # the stations in Montreal are the CP's
        if own in ('tem', 'cgt') and c in ('riviere du loup', 'mont joli'): return place_for('oncn')(name)   # the CN stations
        if own == 'onr' and name in ONR_ON_CN: return place_for('oncn')(name)   # Toronto - North Bay: the ONR trains call at the CN stations
        m = _map().get((own, c))
        if m: return (m[0], m[1], 'map', 300)
        for key in ((own, c), (None, c)):
            st = stations().get(key)
            if st:
                t = track_tree(own if key[0] else None) if key[0] else None
                q = min(st, key=lambda q: t.query(fwd(*q))[0]) if t is not None else st[0]
                return (q[0], q[1], 'collection' if key[0] else 'collection (other railway)', 700)
        return None
    return f
for _r in OWN: ab_lines.EXT_PLACE[_r] = place_for(_r)

# ---------------------------------------------------------------- stop ids: one station per railway and name, shared where the trains used one station
SHARED = {('onr', 'toronto union'): 'TORONTO_UNION', ('oncn', 'toronto union'): 'TORONTO_UNION', ('oncp', 'toronto union'): 'TORONTO_UNION',
          ('oncn', 'ottawa union'): 'OTTAWA_UNION', ('oncp', 'ottawa union'): 'OTTAWA_UNION',
          ('oncp', 'ottawa'): 'OTTAWA_UNION', ('oncn', 'ottawa'): 'OTTAWA_UNION',   # Brendan, 24 Oct 2026: every train to Ottawa uses Union Station unless the table says otherwise (Bank Street)
          ('onr', 'north bay'): 'CN_NORTH_BAY',                           # "North Bay (C.N.)": ONR trains used the CN station
          ('onr', 'cochrane'): 'CN_COCHRANE',
          ('oncp', 'quebec'): 'CN_QUEBEC_PALAIS',
          ('ontem', 'riviere du loup'): 'CN_RIVIERE_DU_LOUP', ('oncgt', 'mont joli'): 'CN_MONT_JOLI',   # at the CN stations (the CN trains there are not built yet)
          ('oncp', 'brockville'): 'BROCKVILLE_UNION', ('oncpcn', 'brockville'): 'BROCKVILLE_UNION', ('oncn', 'brockville'): 'BROCKVILLE_UNION',   # Brockville Union Station (Brendan)
          ('oncp', 'levis'): 'LEVIS', ('oncn', 'levis'): 'LEVIS',          # one Levis station for CN and CP (Quebec Central; Brendan, 25 Oct 2026)                          # one Palais Station (CP Table 33 and CN Table 38)                             # one station at Cochrane (CN Table 38 and the ONR)
          ('oncn', 'don'): 'CP_DON',                                       # Don (Queen St. East): one station, CN Table 122 and CP Table 50
          ('onthb', 'toronto union'): 'TORONTO_UNION', ('oncpthb', 'toronto union'): 'TORONTO_UNION', ('onthb', 'toronto'): 'TORONTO_UNION', ('oncpthb', 'toronto'): 'TORONTO_UNION',
          ('onthb', 'hamilton'): 'THB_HAMILTON', ('oncpthb', 'hamilton'): 'THB_HAMILTON', ('oncp', 'hamilton'): 'THB_HAMILTON',   # Hunter Street: CP and TH&B trains
          ('onthb', 'waterford'): 'NYC_WATERFORD',   # the NYC station (Brendan)
          ('oncp', 'st thomas'): 'NYC_ST_THOMAS', ('onlps', 'n y c depot'): 'NYC_ST_THOMAS',   # CP trains used the NYC (Michigan Central) station at St. Thomas (Brendan); the L&PS N.Y.C. Depot
          ('ongrr', 'galt'): 'GALT_MAIN_STREET', ('onlen', 'galt'): 'GALT_MAIN_STREET',   # one Main Street station for the GRR and the L&N (KMZ; Brendan)
          ('ongrr', 'galt c p r'): 'CP_GALT',                              # Table 66 trains: the CP Galt station (Brendan)
          ('oncnfy', 'levis'): 'LEVIS', ('onaj', 'saguenay power'): 'CN_SAGUENAY_POWER',   # the ferry lands at Levis station; A&J meets the CN at Saguenay Power
          ('onlps', 'london'): 'CN_LONDON', ('onlps', 'c n r wabash depot'): 'CN_ST_THOMAS',   # L&PS London station: part of the CN London station complex (Brendan); C.N.R. - Wabash Depot = CN St. Thomas
          ('onnyco', 'finch'): 'CP_FINCH',                                 # Finch: one station at the NYC - CP crossing (Brendan, 25 Oct 2026)
          ('oncpcn', 'toronto union'): 'TORONTO_UNION', ('oncpcn', 'toronto'): 'TORONTO_UNION',
          **{(r, c): g for r in ('onnyc', 'ondh', 'oncpcn') for c, g in (('montreal', 'CP_MONTREAL_WINDSOR'), ('westmount', 'CP_WESTMOUNT'), ('montreal west', 'CP_MONTREAL_WEST'))}}   # the NYC and D&H used the CP stations
ONR_ON_CN = {'Parkdale', 'St. Clair Avenue', 'Aurora', 'Newmarket', 'Allandale', 'Barrie', 'Orillia', 'Atherley', 'Longford', 'Hawkestone', 'Washago', 'Gravenhurst',
             'Bracebridge', 'Utterson', 'Huntsville', 'Scotia', 'Emsdale', "Burk's Falls", 'Sundridge', 'South River', 'Trout Creek', 'Powassan', 'Callander', 'Beaverton'}   # CN Table 126 stations of ONR 46 / 47 / 49 / 50
def register(files):
    import ab_table
    for rail, fn in files:
        for r in ab_table.load(os.path.join(HERE, fn))['rows']:
            n = r['station']; c = canon(n); cu = canon(re.sub(r'[()]', ' ', n).replace(' Station', ''))
            if (rail, cu) in SHARED: ab_lines.EXT_GID[(rail, n)] = SHARED[(rail, cu)]; continue
            if (rail, c) in SHARED and not (rail == 'onr' and c == 'north bay' and 'C.P.' in n) and not ('(' in n and 'Union' not in n and c == 'ottawa'): ab_lines.EXT_GID[(rail, n)] = SHARED[(rail, c)]; continue   # Ottawa (Bank Street) stays its own
            m = _map().get((OWN[rail], c))
            full = canon(re.sub(r'[()]', ' ', n))                         # the whole name: Ottawa (Bank Street) is not Ottawa (Union Station)
            ab_lines.EXT_GID[(rail, n)] = m[2] if m else ('CN' if rail == 'oncpcn' else ab_lines.RAILS[rail]['pfx']) + '_' + re.sub(r'\W+', '_', full.upper()).strip('_')
    for (rail, n) in list(ab_lines.EXT_GID):
        if rail == 'onr' and n in ONR_ON_CN and ('oncn', n) in ab_lines.EXT_GID: ab_lines.EXT_GID[(rail, n)] = ab_lines.EXT_GID[('oncn', n)]   # one stop at each CN station
