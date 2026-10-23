"""CN and CP routes from the National Railway Network (NRWN) file, only the track our 1948-49 trains use.

Routes built (all in UTM 10N metres, then lon/lat):
  cn   CN station (Main St) -> GN line (shared, from Brendan's GN trace) -> Fraser bridge -> Yale sub -> Boston Bar -> Ashcroft sub -> Kamloops Jct -> Clearwater and Albreda subs -> Yellowhead (B.C. border)
  cno  Kamloops Jct -> Okanagan sub -> Vernon -> Lumby Jct -> Kelowna (Brendan's tracing)
  cp   Waterfront -> Cascade sub -> North Bend -> Thompson sub -> Kamloops -> Shuswap sub -> Revelstoke -> Mountain sub -> Field -> Laggan sub -> Great Divide
  cpm  Waterfront -> Cascade sub -> Mission -> Mission sub -> Huntingdon   (only the Mission sub part is drawn)
  cpw  Coquitlam -> Westminster sub -> New Westminster
Mileposts: Yale sub mp = CN 1949 mile - 2798.5; Cascade sub mp = CP 1948 mile - 2752.7; Mission sub mp as printed."""
import json, math, os
import numpy as np, networkx as nx
from pyproj import Transformer
from shapely.geometry import LineString, Point
from shapely.ops import substring
HERE = os.path.dirname(os.path.abspath(__file__))
fwd = Transformer.from_crs(4326, 26910, always_xy=True).transform
inv = Transformer.from_crs(26910, 4326, always_xy=True).transform
MI = 1609.344

F = json.load(open(os.path.join(HERE, 'nrwn', 'region.json')))
_seen = {f['data'].get('NID') for f in F}
for _extra in ('okanagan.json', 'cnmain.json', 'cpmain.json'):                  # Kamloops and the Okanagan; CN north of Kamloops to Yellowhead
    _new = [f for f in json.load(open(os.path.join(HERE, 'nrwn', _extra))) if f['data'].get('NID') not in _seen]
    _seen |= {f['data'].get('NID') for f in _new}; F += _new
tracks = [f for f in F if f['schema'] == '#kml_schema_ft_Track']
markers = [f for f in F if f['schema'] == '#kml_schema_ft_MarkerPost']

# ---------------- graph of all NRWN track (main preferred)
G = nx.Graph(); key = lambda p: (round(p[0], 1), round(p[1], 1))
for f in tracks:
    d = f['data']; cls = d.get('trackClassification'); sub = d.get('subdivision1Name')
    for c in f['coords']:
        pts = [fwd(*p) for p in c]
        for a, b in zip(pts, pts[1:]):
            w = math.dist(a, b) * (1.0 if cls in ('Main', 'Connecting') else 4.0)   # wye legs are 'Connecting'
            ka, kb = key(a), key(b)
            if ka != kb and (not G.has_edge(ka, kb) or G[ka][kb]['w'] > w):
                G.add_edge(ka, kb, w=w, sub=sub, cls=cls)
nodes = np.array(list(G.nodes)); nlist = list(G.nodes)
# join near-coincident endpoints (feature boundaries)
for n in list(G.nodes):
    if G.degree(n) == 1:
        d = np.hypot(nodes[:, 0] - n[0], nodes[:, 1] - n[1])
        for j in np.where((d > 0) & (d < 4))[0]: G.add_edge(n, nlist[j], w=float(d[j]), sub='join', cls='join')

def near(xy, sub=None):
    best, bd = None, 1e18
    for n in G.nodes:
        if sub and not any(G[n][m].get('sub') == sub for m in G[n]): continue
        d = math.dist(n, xy)
        if d < bd: best, bd = n, d
    return best, bd

def path(a_xy, b_xy, prefer=None, suba=None, subb=None):
    na, da = near(a_xy, suba); nb, db = near(b_xy, subb)
    def w(u, v, e):
        x = e['w']
        if prefer and e.get('sub') not in prefer and e.get('sub') != 'join': x *= 6
        return x
    p = nx.shortest_path(G, na, nb, weight=w)
    return p, da, db

def clean(pts):
    out = [pts[0]]
    for p in pts[1:]:
        if math.dist(p, out[-1]) > 0.5: out.append(p)
    return LineString(out)

# ---------------- CP main: Waterfront -> North Bend
WATERFRONT = fwd(-123.1121, 49.2863); LYTTON_CP = fwd(-121.5734, 50.2437)          # NRWN CP station, Thompson sub 94.28
p, a, b = path(WATERFRONT, LYTTON_CP, prefer={'Cascade', 'Thompson'}, suba='Cascade', subb='Thompson')
CP_BORDER = fwd(-116.2863163, 51.4517348)                          # Alberta border at the Great Divide (Stephen), east end of the B.C. data
# The Spiral Tunnels: a siding link near the upper portal lets a shortest path skip both loops, so the route is pinned to the main track
# in order: Field side -> Lower Spiral Tunnel (Mount Ogden) -> Upper Spiral Tunnel (Cathedral Mountain) -> toward the Great Divide.
_tun = {}
for f in F:
    if f['schema'] == '#kml_schema_ft_LinearStructure' and 'Spiral' in (f['data'].get('structureEnglishName') or ''):
        c = [fwd(*q) for q in f['coords'][0]]; _tun[f['data']['structureEnglishName']] = c
SPIRAL_PATH = [fwd(-116.4842132, 51.3988166), fwd(-116.4259043, 51.422033), fwd(-116.4076983, 51.4338689)] + \
    [_tun['Lower Spiral Tunnel'][len(_tun['Lower Spiral Tunnel']) * k // 4] for k in (1, 2, 3)] + \
    [fwd(-116.4067667, 51.4382996), fwd(-116.4032946, 51.4321706), fwd(-116.416425, 51.4237956)] + \
    [_tun['Upper Spiral Tunnel'][len(_tun['Upper Spiral Tunnel']) * k // 4] for k in (3, 2, 1)] + \
    [fwd(-116.4205788, 51.4202355), fwd(-116.4181073, 51.4219631), fwd(-116.3831719, 51.4352839)]
# Rogers Pass: the 1948 line is the 1916 one through the Connaught Tunnel. The 1988 Mount Macdonald and Mount Shaughnessy tunnels cross it
# in plan and the shortest path jumped between them (Brendan, 5 October 2026), so the route is pinned to the Connaught Tunnel, west portal
# to east portal, and checked below to stay out of the two later tunnels.
for f in F:
    if f['schema'] == '#kml_schema_ft_LinearStructure' and (f['data'].get('structureEnglishName') or '') in ('Connaught Tunnel', 'Mount Macdonald Tunnel', 'Mount Shaughnessy Tunnel'):
        _tun[f['data']['structureEnglishName']] = [fwd(*q) for q in f['coords'][0]]
_ct = _tun['Connaught Tunnel']
if math.dist(_ct[0], fwd(-117.5117, 51.2699)) > math.dist(_ct[-1], fwd(-117.5117, 51.2699)): _ct = _ct[::-1]      # west portal first
CONNAUGHT_PATH = [_ct[len(_ct) * k // 8] for k in range(1, 8)]
SPIRAL_PATH = CONNAUGHT_PATH + SPIRAL_PATH
pe = []
for a_, b_ in zip([LYTTON_CP] + SPIRAL_PATH, SPIRAL_PATH + [CP_BORDER]):
    seg_, _, be = path(a_, b_, prefer={'Thompson', 'Shuswap', 'Mountain', 'Laggan'}, suba='Thompson' if a_ is LYTTON_CP else None,
                       subb='Laggan' if b_ is CP_BORDER else None)
    pe += seg_ if not pe else seg_[1:]
_rep = len(list(zip(pe, pe[1:]))) - len({frozenset(e) for e in zip(pe, pe[1:])})
_PL = LineString(pe)
print('  Spiral Tunnels: route covers', {n: round(_PL.intersection(LineString(c).buffer(3)).length / LineString(c).length * 100) for n, c in _tun.items()}, '% ; doubled-back edges', _rep)
# where the subdivisions change along Lytton -> border (Shuswap starts at Kamloops, Mountain at Revelstoke, Laggan at Field)
cp_subs, acc, last = {}, math.dist(p[0], p[0]), None
base = LineString(p).length
for u, v in zip(pe, pe[1:]):
    sb = G[u][v].get('sub')
    if sb in ('Shuswap', 'Mountain', 'Laggan') and sb not in cp_subs: cp_subs[sb] = base + acc
    acc += math.dist(u, v)
CP = clean(p + pe[1:])
print(f'CP Waterfront->Lytton {base/MI:.1f} mi (timetable 155.6); ->Great Divide {CP.length/MI:.1f} mi (timetable 2881.7-2362.3 = 519.4) snap {a:.0f}/{be:.0f} m')
print('  CP subdivision starts (mi from Waterfront):', {k: round(v / MI, 1) for k, v in cp_subs.items()},
      '(timetable: Kamloops 250.5, Revelstoke 379.3, Field 505.0)')

# ---------------- CP Mission branch: Mission (on Cascade) -> Huntingdon
HUNT = fwd(-122.2670, 49.0031)
# Vancouver trains take the west leg of the Mission wye: route straight from Waterfront to Huntingdon
p2, _, _ = path(WATERFRONT, HUNT, prefer={'Cascade', 'Mission'}, suba='Cascade', subb='Mission')
CPM = clean(p2)
MJ = 0.0                                                      # divergence from the CP main line
for d in np.arange(0, CPM.length, 5.0):
    if CP.distance(CPM.interpolate(d)) < 4: MJ = d
    elif d > 60 * MI: break
print('  wye: branch leaves the main line at', inv(*CPM.interpolate(MJ).coords[0]))
p2 = list(substring(CPM, MJ, CPM.length).coords)
print(f'CP Mission branch: junction at Cascade {MJ/MI:.1f} mi from Waterfront, branch {LineString(p2).length/MI:.1f} mi (timetable 10.1)')

# ---------------- CP Westminster branch: Coquitlam -> New Westminster
COQ = fwd(-122.7823, 49.2657)
nw_end = near(fwd(-122.927, 49.201), 'Westminster')[0]      # the Westminster sub's New Westminster end (not its Marpole piece)
p3, a3, b3 = path(COQ, nw_end, prefer={'Westminster'})
CPW = clean(p3); print(f'CP Coquitlam->New Westminster {CPW.length/MI:.1f} mi (timetable 8.4) end at {inv(*nw_end)}')

# ---------------- CN: CN station -> GN line -> bridge -> Yale sub -> Boston Bar -> Ashcroft sub -> Kamloops Jct
GN = LineString([fwd(*q) for q in json.load(open(os.path.join(HERE, 'gn_geometry.json')))['route']])
CN_STN = fwd(-123.0975, 49.2738); KAMLOOPS_JCT = fwd(-120.3484611, 50.718257)     # NRWN CN station, Ashcroft sub 0 (Kamloops Jct)
gn_join = GN.interpolate(0.95 * MI)                          # where the GN station spur leaves its main line
p4, a4, b4 = path(CN_STN, gn_join.coords[0])
spur = clean(p4)
j = GN.project(Point(p4[-1]))
BR_S = 13.61 * MI                                             # south end of the Fraser bridge on the GN trace
p5, a5, b5 = path(GN.interpolate(BR_S).coords[0], KAMLOOPS_JCT, prefer={'Yale', 'Ashcroft'}, subb='Ashcroft')
BORDER = fwd(-118.4644008, 52.8913423)                           # Alberta border at Yellowhead Pass (east end of the B.C. data)
p7, a7, b7 = path(KAMLOOPS_JCT, BORDER, prefer={'Clearwater', 'Albreda'}, suba='Ashcroft', subb='Albreda')
print(f'CN Kamloops Jct -> Blue River -> Red Pass Jct -> Yellowhead border {LineString(p7).length/MI:.1f} mi (Table 23: 2666.9-2412.7 = 254.2 less ~0.3 to the border)')
CN = clean(list(spur.coords) + list(substring(GN, j, BR_S).coords) + p5 + p7[1:])
cn_shared = (spur.length, spur.length + (BR_S - j))
print(f'CN: spur {spur.length/MI:.2f} mi, shared GN line {(BR_S-j)/MI:.2f} mi, Yale+Ashcroft subs {LineString(p5).length/MI:.1f} mi; '
      f'total {CN.length/MI:.1f} mi (timetable 2798.5+131.8-2672.5 = 257.8); snaps {a4:.0f}/{b4:.0f} {a5:.0f}/{b5:.0f} m')

# ---------------- milepost -> chain along a route, from NRWN marker posts
def mp_fn(route, sub, lo=0, hi=None):
    pairs = []
    for f in markers:
        if f['data'].get('subdivision1Name') != sub: continue
        q = Point(fwd(*f['coords'][0][0]))
        if route.distance(q) < 60:
            c = route.project(q)
            if c >= lo and (hi is None or c <= hi): pairs.append((float(f['data']['subdivision1Distance']), c))
    pairs.sort()
    # keep a monotonic sequence (mp and chain both increasing or both decreasing)
    ms, cs = zip(*pairs)
    sign = 1 if np.polyfit(ms, cs, 1)[0] > 0 else -1
    keep = [pairs[0]]
    for m_, c in pairs[1:]:
        if (c - keep[-1][1]) * sign > 0: keep.append((m_, c))
    ms, cs = map(np.array, zip(*keep))
    print(f'  {sub}: {len(keep)} mileposts on route, mp {ms.min():.0f}-{ms.max():.0f}')
    return lambda m: float(np.interp(m, ms, cs, left=np.nan, right=np.nan)) if ms.min() <= m <= ms.max() else \
        float(cs[0] + (m - ms[0]) * sign * MI) if m < ms.min() else float(cs[-1] + (m - ms[-1]) * sign * MI)

cascade = mp_fn(CP, 'Cascade')
yale = mp_fn(CN, 'Yale', lo=cn_shared[1])
mission = mp_fn(CPM, 'Mission', lo=MJ)
# ---------------- CN Okanagan line: Kamloops Jct -> Kamloops -> Vernon -> Lumby Jct (NRWN) -> Kelowna (Brendan's tracing)
LUMBY_JCT = fwd(-119.2686229, 50.2340336)
p6, a6, b6 = path(KAMLOOPS_JCT, LUMBY_JCT, prefer={'Okanagan'}, subb='Okanagan')
# Lumby Jct -> Kelowna: Brendan's tracing (kelowna_branch.kml; the line is not in the NRWN)
import xml.etree.ElementTree as ET
_kc = ET.parse(os.path.join(HERE, 'kelowna_branch.kml')).getroot().find('.//{http://www.opengis.net/kml/2.2}coordinates').text.split()
KEL = [fwd(*map(float, c.split(',')[:2])) for c in _kc][::-1]           # traced Kelowna -> Lumby Jct; reverse it
print(f'  Kelowna tracing: {LineString(KEL).length/MI:.1f} mi (timetable 118.9-87.6 = 31.3), joins NRWN {math.dist(KEL[0], p6[-1]):.0f} m from Lumby Jct')
CNO = clean(p6 + KEL[1:])
print(f'CN Okanagan Kamloops Jct->Kelowna {CNO.length/MI:.1f} mi (timetable 118.9), snaps {a6:.0f}/{b6:.0f} m')
out = dict(cp_subs=cp_subs, cp=[inv(*q) for q in CP.coords], cpm=[inv(*q) for q in CPM.coords], cpw=[inv(*q) for q in CPW.coords],
           cn=[inv(*q) for q in CN.coords], cno=[inv(*q) for q in CNO.coords], cn_shared=cn_shared, cpm_junction=MJ,
           checks={})
# spot checks: known places
for name, mp, fn, route in (('Agassiz (CP 58.9)', 58.9, cascade, CP), ('Mission (CP 87.3)', 87.3, cascade, CP),
                            ('Hope (CN 40.2)', 40.2, yale, CN), ('Chilliwack (CN 71.8)', 71.8, yale, CN),
                            ('Huntingdon (Mission 10.1)', 10.1, mission, CPM),
                            ('CP Lytton (Thompson 94.3)', 94.28, mp_fn(CP, 'Thompson'), CP),
                            ('CN Lytton (Ashcroft 98.7)', 98.7, mp_fn(CN, 'Ashcroft'), CN)):
    c = fn(mp); lon, lat = inv(*route.interpolate(c).coords[0]); print(f'  {name}: {lon:.4f},{lat:.4f}')
json.dump(out, open(os.path.join(HERE, 'nrwn_routes.json'), 'w'))
import pickle; pickle.dump(dict(CP=CP, CPM=CPM, CPW=CPW, CN=CN, CNO=CNO), open(os.path.join(HERE, 'nrwn_routes.pkl'), 'wb'))
