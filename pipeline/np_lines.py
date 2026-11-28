"""Northern Pacific east of Spokane and the Camas Prairie in Idaho (Brendan, 27 Nov 2026): track graph and station places for the ab_lines.py machinery.
A helper, imported by npmw_build.py (it imports gn_lines.py for the projection and the name helpers).

Track: traces/npmw/np_mw.geojson (tools/np_import.py: Mississippi Rails' Northern Pacific KMZ east of Spokane; the Camas Prairie's own pieces own 'cprr'), Brendan's Camas
Prairie piece at Lewiston (traces/npmw/np_links.geojson), and the track of lines already on the map near the shared stations (St. Paul - Minneapolis, Superior - Duluth,
Billings, Spokane, Pullman, the Camas Prairie in Washington), so the NP trains reach the union stations the earlier lines drew.
Stations: a hand point (HAND); a station already on the map that the NP shares (SHARE: St. Paul Union Depot, the Great Northern station at Minneapolis, Duluth Union Depot,
Superior Union Station, Billings, Butte Union Depot, the NP station at Spokane, the Winnipeg line's Manitoba Junction ...); the end of a KMZ piece named for the place; else by
printed mileage. Stop ids: NP_<NAME>_<STATE> (CPRR_ for the Camas Prairie's own stations)."""
import json, math, os, re
import ab_lines, gn_lines
from gn_lines import canon, dms
HERE = os.path.dirname(os.path.abspath(__file__))
gn_lines.STATES.update({'Man.': 'MB'})
STATES = gn_lines.STATES
def split(name):
    m = re.match(r'^(.*?),\s*(Minn\.|N\. Dak\.|S\. Dak\.|Mont\.|Idaho|Wis\.|Iowa|Ill\.|Wash\.|Man\.)$', name)
    return (m.group(1), STATES[m.group(2)]) if m else (name, '')
ab_lines.RAILS['npmw'] = dict(kind='o', label='Northern Pacific', own='np', agency='NP', color='1F4E79', pfx='NP')
ab_lines.RAILS['cpmw'] = dict(kind='CR', label='Camas Prairie', own='cprr', agency='CPRR', color='C46A8A', pfx='CPRR')
# ---------------------------------------------------------------- track
BOXES = [(-93.40, -92.95, 44.88, 45.08), (-92.25, -92.00, 46.65, 46.82), (-108.62, -108.40, 45.72, 45.85), (-117.50, -117.30, 47.60, 47.70), (-117.25, -117.04, 46.68, 46.78)]
def _map_pieces():
    """routes of lines already on the map inside the boxes near the shared stations, and the whole Camas Prairie line in Washington"""
    out = []
    for L in json.load(open(os.path.join(HERE, 'viz_data.json')))['lines']:
        if L['key'].startswith(('npmw', 'cpmw')) or L.get('water') or L.get('ocean'): continue
        c = [p[:2] for p in L['route']]
        if L['key'] == 'cprr': out.append(c); continue
        for x0, x1, y0, y1 in BOXES:
            cur = []
            for p in c:
                if x0 < p[0] < x1 and y0 < p[1] < y1: cur.append(p)
                elif cur:
                    if len(cur) > 1: out.append(cur)
                    cur = []
            if len(cur) > 1: out.append(cur)
    return out
def _graph(mine):
    def feed(add):
        for f in json.load(open(os.path.join(HERE, 'traces', 'npmw', 'np_mw.geojson')))['features'] + json.load(open(os.path.join(HERE, 'traces', 'npmw', 'np_links.geojson')))['features']:
            o = 'cprr' if f['properties']['own'] == 'up' else 'np'
            add(ab_lines._xy(f['geometry']['coordinates']), 1.0, 'b', None if o == mine else o)
        for c in _map_pieces(): add(ab_lines._xy(c), 1.05, 'b', 'none')         # drawn already by the earlier lines (shared track is found again in any case)
    return lambda: ab_lines.make_graph(feed, tie_end=150, tie_loose=60, tie_each=True)
ab_lines.EXT_GRAPH['sk:npmw'] = _graph('np')
ab_lines.EXT_GRAPH['sk:cpmw'] = _graph('cprr')
# ---------------------------------------------------------------- places
_LEW = json.load(open(os.path.join(HERE, 'traces', 'npmw', 'np_links.geojson')))['features'][0]['geometry']['coordinates'][0]
HAND = {('butte', 'MT'): (-dms(112, 31, 35.95), dms(46, 0, 3.58), 'Butte Union Depot (Brendan, 27 Nov 2026)'),
        ('superior', 'WI'): (-92.107400, 46.726609, 'Superior Union Station (Brendan, 27 Nov 2026; GN, shared with the NP)'),
        ('lewiston', 'ID'): (_LEW[0], _LEW[1], 'Lewiston: the end of the Camas Prairie piece (Brendan, 27 Nov 2026); approximate for the depot'),
        ('silver bow', 'MT'): (-dms(112, 40, 21.28), dms(46, 0, 16.90), 'Silver Bow (Brendan, 27 Nov 2026)')}

# towns no piece is named for (Claude's points for the towns, approximate; the station snaps to the track within 2.5 km)
for _l in '''dickinson ND 46.8792 -102.7896
beach ND 46.9180 -104.0044
bismarck ND 46.8083 -100.7837
mandan ND 46.8267 -100.8896
jamestown ND 46.9105 -98.7084
valley city ND 46.9233 -98.0032
fargo ND 46.8772 -96.7898
moorhead MN 46.8738 -96.7676
casselton ND 46.9008 -97.2112
staples MN 46.3555 -94.7922
wadena MN 46.4425 -95.1361
brainerd MN 46.3580 -94.2008
little falls MN 45.9763 -94.3625
st cloud MN 45.5640 -94.1500
carlton MN 46.6638 -92.4249
hinckley MN 46.0113 -92.9441
wyoming MN 45.3364 -92.9969
rush city MN 45.6855 -92.9655
bemidji MN 47.4736 -94.8803
international falls MN 48.6011 -93.4108
glendive MT 47.1053 -104.7125
miles city MT 46.4083 -105.8406
forsyth MT 46.2663 -106.6778
livingston MT 45.6624 -110.5610
bozeman MT 45.6770 -111.0429
logan MT 45.8852 -111.4383
helena MT 46.6000 -112.0300
garrison MT 46.5208 -112.8128
missoula MT 46.8750 -113.9950
paradise MT 47.3880 -114.8030
sand point ID 48.2766 -116.5533
moscow ID 46.7324 -117.0002
carrington ND 47.4497 -99.1262
new rockford ND 47.6800 -99.1379
oberon ND 47.9236 -99.2040
lamoure ND 46.3572 -98.2945
oakes ND 46.1386 -98.0901
linton ND 46.2666 -100.2329
mckenzie ND 46.8303 -100.4140
mott ND 46.3725 -102.3271
killdeer ND 47.3719 -102.7541
taylors falls MN 45.4019 -92.6522
grantsburg WI 45.7763 -92.6827
turtle lake ND 47.5214 -100.8935
wahpeton ND 46.2652 -96.6059
fergus falls MN 46.2830 -96.0776
marion ND 46.6119 -98.3376
cooperstown ND 47.4444 -98.1240
mchenry ND 47.5761 -98.5862
sanborn ND 46.9444 -98.2240
pingree ND 47.1608 -98.9101
wilton ND 47.1586 -100.7843
leeds ND 48.2886 -99.4365
streeter ND 46.6566 -99.3554
edgeley ND 46.3606 -98.7140
lisbon ND 46.4416 -97.6812
morris MN 45.5861 -95.9139
sauk centre MN 45.7375 -94.9525
esmond ND 48.0330 -99.7651
gardiner MT 45.0319 -110.7058
three forks MT 45.8927 -111.5522
whitehall MT 45.8705 -112.0975
deer lodge MT 46.3966 -112.7303
orofino ID 46.4793 -116.2551
grangeville ID 45.9266 -116.1224
stites ID 46.0913 -115.9759
culdesac ID 46.3746 -116.6688
cloquet MN 46.7216 -92.4593
aitkin MN 46.5330 -93.7102
walker MN 47.1014 -94.5872
detroit lakes MN 46.8172 -95.8453'''.splitlines():
    *_n, _st, _la, _lo = _l.split(); HAND.setdefault((' '.join(_n), _st), (float(_lo), float(_la), ' '.join(_n).title() + ' (town; approximate)'))
_OL = [f['geometry']['coordinates'] for f in json.load(open(os.path.join(HERE, 'traces', 'npmw', 'np_mw.geojson')))['features'] if f['properties']['name'].startswith('Ollie MT')]
if _OL: _e = min((_OL[0][0], _OL[0][-1]), key=lambda p: p[0]); HAND[('ollie', 'MT')] = (_e[0], _e[1], 'Ollie: the west end of the piece "Ollie MT to MT/ND State Line"')
SHARE = {('st paul', 'MN'): 'CP_ST_PAUL', ('minneapolis', 'MN'): 'GN_MINNEAPOLIS', ('duluth', 'MN'): 'CN_DULUTH', ('superior', 'WI'): 'GN_SUPERIOR_WI',
         ('billings', 'MT'): 'GN_BILLINGS_MT', ('mossmain', 'MT'): 'GN_MOSSMAIN_MT', ('butte', 'MT'): 'BUTTE_UNION_MT', ('spokane', 'WA'): 'WA_SPOKANE_NP_STATION',
         ('pullman', 'WA'): 'NP_PULLMAN', ('sunshine', 'WA'): 'NP_SUNSHINE', ('manitoba jct', 'MN'): 'NP_MANITOBA_JUNCTION', ('almota', 'WA'): 'CPRR_ALMOTA',
         ('riparia', 'WA'): 'CPRR_RIPARIA', ('crookston', 'MN'): 'NP_CROOKSTON', ('silver bow', 'MT'): 'BAP_SILVER_BOW'}
_MAPX = {}
def _map():
    if not _MAPX:
        for L in json.load(open(os.path.join(HERE, 'viz_data.json')))['lines']:
            for s in L['stations']: _MAPX.setdefault(s['gid'], (s['lon'], s['lat']))
    return _MAPX
ANCH = {}
ALIAS = {('kildeer', 'ND'): ('killdeer', 'ND'), ('edgely', 'ND'): ('edgeley', 'ND'), ('juliaette', 'ID'): ('juliaetta', 'ID'), ('glouster', 'MN'): ('gloster', 'MN'),
         ('centre city', 'MN'): ('center city', 'MN'), ('moffit', 'ND'): ('moffitt', 'ND'), ('sydney', 'MT'): ('sidney', 'MT'), ('la moure', 'ND'): ('lamoure', 'ND'),
         ('central ave superior', 'WI'): ('cent ave superior', 'WI')}
def _anchors():
    """(canon name, state) -> (lon, lat): the ends of KMZ pieces named "A ST to B ST" (as gn_lines._anchors)"""
    if ANCH: return ANCH
    cand = {}
    for f in json.load(open(os.path.join(HERE, 'traces', 'npmw', 'np_mw.geojson')))['features']:
        m = re.match(r'^(.+?)\s+to\s+(.+)$', f['properties']['name'])
        if not m: continue
        c = f['geometry']['coordinates']; ends = (tuple(c[0]), tuple(c[-1])); keys = []
        for nm in (m.group(1), m.group(2)):
            nm = nm.strip().rstrip(',')
            if re.search(r'State Line|^\d', nm): keys.append(None); continue
            mm = re.match(r'^(.*?),?\s+(MN|ND|SD|MT|ID|WI|IA|IL|WA)$', nm)
            k = (canon(mm.group(1)), mm.group(2)) if mm else (canon(nm), '')
            keys.append(ALIAS.get(k, k))
        if keys[0] and keys[1]:
            if keys[0][1] == '' and keys[1][1]: keys[0] = (keys[0][0], keys[1][1])
            if keys[1][1] == '' and keys[0][1]: keys[1] = (keys[1][0], keys[0][1])
        for i, k in enumerate(keys):
            if k: cand.setdefault(k, []).append((ends, i, keys))
    km = lambda a, b: math.hypot((a[0] - b[0]) * 75.0, (a[1] - b[1]) * 111.0)
    seed = {}
    for k, h in HAND.items(): seed[k] = h[:2]
    for k in cand:
        g = SHARE.get(k)
        if g and g in _map(): seed[k] = _map()[g]
    for k, L in cand.items():
        if k in seed or len(L) < 2: continue
        pts = [e for ends, _, _ in L for e in ends]
        n = lambda p: sum(1 for ends, _, _ in L if min(km(p, e) for e in ends) < 2.0)
        best = max(pts, key=n)
        if n(best) > 1: ANCH[k] = best
    known = lambda k: seed.get(k) or ANCH.get(k)
    for _ in range(4):
        for k, L in cand.items():
            if k in ANCH or k in seed: continue
            for ends, i, keys in L:
                other = keys[1 - i]; o = known(other) if other else None
                if o: ANCH[k] = max(ends, key=lambda e: km(e, o)); break
    for k, v in seed.items(): ANCH.setdefault(k, v)
    return ANCH
def gid(name, pfx='NP_'):
    n, st = split(name); c = canon(n)
    return SHARE.get((c, st)) or ('NP_LEWISTON_ID' if (c, st) == ('lewiston', 'ID') else pfx + re.sub(r'\W+', '_', c.upper()).strip('_') + (('_' + st) if st else ''))
def place(name):
    n, st = split(name); c = canon(n)
    if (c, st) in HAND: h = HAND[(c, st)]; return (h[0], h[1], 'hand', 700 if 'Brendan' in h[2] else 2500)
    m = _map().get(gid(name))
    if m: return (m[0], m[1], 'map', 300)
    a = _anchors().get((c, st))
    if a: return (a[0], a[1], 'piece end', 1500)
    return None
ab_lines.EXT_PLACE['npmw'] = place
ab_lines.EXT_PLACE['cpmw'] = place
_G0 = ab_lines.EXT_GID.get
class _G(dict):
    def get(self, k, d=None):
        if k[0] == 'npmw': return gid(k[1])
        if k[0] == 'cpmw': return gid(k[1], 'CPRR_')
        return _G0(k, d)
ab_lines.EXT_GID = _G()
