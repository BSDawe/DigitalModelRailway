"""Cut the North Shore Line routes out of the Mississippi Rails Chicago interurbans KML (Brendan, 25 Nov 2026; private repo traces/chicago/Chicago_Interurbans_1948.kml)
and write them to the public traces/chicago/cnsm_routes.json (only the track the trains use, per the private / public rule).
Usage: python3 tools/chi_extract.py
The KML's pieces are joined where a piece end meets another piece (within 15 m) or another piece end (8 m); crossings without a piece end stay apart. Each route is the
shortest path through a few waypoints (station areas that fix the way: the Loop side, the Niles Center branch); out-and-back stubs are cut. The State Street subway and the
'L' yards are left out of the graph. Points on 'L' track are marked (owner cta, the Chicago Transit Authority)."""
import json, math, os, sys
import xml.etree.ElementTree as ET
import networkx as nx, numpy as np
from scipy.spatial import cKDTree
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KML = os.path.join(HERE, 'traces', 'chicago', 'Chicago_Interurbans_1948.kml')
K = '{http://www.opengis.net/kml/2.2}'
LINES, POLYS = [], []
def walk(e, path):
    for c in e:
        if c.tag in (K + 'Folder', K + 'Document'): walk(c, path + [c.findtext(K + 'name') or ''])
        elif c.tag == K + 'Placemark':
            for ls in c.iter(K + 'LineString'):
                LINES.append(dict(path='/'.join(path), c=[[float(v) for v in x.split(',')[:2]] for x in ls.findtext(K + 'coordinates').split()]))
            for pg in c.iter(K + 'Polygon'):
                cc = [[float(v) for v in x.split(',')[:2]] for x in pg.find('.//' + K + 'coordinates').text.split()]
                POLYS.append([sum(p[0] for p in cc) / len(cc), sum(p[1] for p in cc) / len(cc), (c.findtext(K + 'description') or '').strip()])
walk(ET.parse(KML).getroot(), [])
LINES = [l for l in LINES if 'State Street Subway' not in l['path'] and '/Yards' not in l['path']]
C0 = math.cos(math.radians(42.0))
def xy(p): return (p[0] * 111320 * C0, p[1] * 110570)
def m(a, b): return math.hypot((a[0] - b[0]) * 111320 * C0, (a[1] - b[1]) * 110570)
G = nx.Graph(); P = {}; nid = 0; ends = []
for li, l in enumerate(LINES):
    prev = None
    for k, p in enumerate(l['c']):
        P[nid] = (p, li)
        if prev is not None: G.add_edge(prev, nid, w=m(P[prev][0], p))
        if k in (0, len(l['c']) - 1): ends.append(nid)
        prev = nid; nid += 1
segs = list(G.edges()); A = np.array([xy(P[a][0]) for a, b in segs]); B = np.array([xy(P[b][0]) for a, b in segs])
for e in ends:
    q = np.array(xy(P[e][0])); AB = B - A; t = np.clip(((q - A) * AB).sum(1) / np.maximum((AB * AB).sum(1), 1e-9), 0, 1)
    D = np.hypot(*(A + AB * t[:, None] - q).T)
    for s in np.argsort(D)[:6]:
        a, b = segs[s]
        if D[s] > 15: break
        if P[a][1] == P[e][1] or not G.has_edge(a, b): continue
        f = A[s] + AB[s] * t[s]; nid += 1; P[nid] = ([f[0] / (111320 * C0), f[1] / 110570], P[a][1])
        G.remove_edge(a, b); G.add_edge(a, nid, w=m(P[a][0], P[nid][0])); G.add_edge(nid, b, w=m(P[nid][0], P[b][0])); G.add_edge(e, nid, w=float(D[s]))
        break
TE = cKDTree([xy(P[e][0]) for e in ends])
for i, j in TE.query_pairs(8): G.add_edge(ends[i], ends[j], w=m(P[ends[i]][0], P[ends[j]][0]))
NODES = list(G.nodes); TN = cKDTree([xy(P[n][0]) for n in NODES])
def near(q): return NODES[TN.query(xy(q))[1]]
def L_track(n): p = LINES[P[n][1]]['path']; return 'Rapid Transit' in p and 'Niles Center' not in p     # 'L' track (CTA); the Niles Center branch is North Shore Line track
def route(wps):
    path = []
    for a, b in zip(wps, wps[1:]):
        sp = nx.shortest_path(G, near(a), near(b), weight='w'); path += sp if not path else sp[1:]
    out = []                                   # cut out-and-back stubs (a node visited twice)
    for n in path:
        if n in out: del out[out.index(n) + 1:]
        else: out.append(n)
    return [[round(P[n][0][0], 7), round(P[n][0][1], 7), 1 if L_track(n) else 0] for n in out]
# Chicago: Roosevelt Road ('L' 12th Street), the Loop junctions (Lake & Wells: J18; Van Buren & Wabash), the south-east wye leg used by southbound trains
ROOSEVELT, CLARK_LAKE, J18, QUINCY_WELLS, WYE, HOWARD = (-87.6266, 41.8673), (-87.6310, 41.8857), (-87.6339, 41.8857), (-87.6338, 41.8787), (-87.62616, 41.876938), (-87.6732, 42.0193)
DEMPSTER, MILWAUKEE, LINDEN = (-87.752, 42.041), (-87.9187, 43.0369), (-87.6915, 42.0733)
HIGHWOOD, LAKE_BLUFF, SCRANTON, NCJ, TENTH, MUNDELEIN = (-87.810, 42.205), (-87.8455, 42.2785), (-87.8481, 42.2803), (-87.8466, 42.3300), (-87.83347, 42.34065), (-88.00106, 42.27305)
SV_JCT = (-87.865, 42.2800)     # the Skokie Valley line meets the Mundelein branch (west of Scranton Avenue)
R = dict(
  loop_n=route([ROOSEVELT, CLARK_LAKE, J18]),                       # northbound: Wabash Avenue and Lake Street
  loop_s=route([J18, QUINCY_WELLS, WYE, ROOSEVELT]),                # southbound: Wells Street, Van Buren Street, the south-east wye
  sv=route([J18, HOWARD, DEMPSTER, MILWAUKEE]),                     # tails northward from Lake & Wells
  shore=route([J18, HOWARD, LINDEN, HIGHWOOD, LAKE_BLUFF, NCJ, TENTH]),
  shore_mke=route([J18, HOWARD, LINDEN, HIGHWOOD, LAKE_BLUFF, NCJ, MILWAUKEE]),
  mundelein=route([J18, HOWARD, DEMPSTER, SV_JCT, MUNDELEIN]),
  sv_tenth=route([J18, HOWARD, DEMPSTER, SCRANTON, NCJ, TENTH]),
  branch=route([LAKE_BLUFF, SCRANTON, MUNDELEIN]))
# The south-east wye leg (Van Buren Street to the South Side 'L' southbound) does not join the Van Buren track in the file: the shortest path went round the corner and
# back. Splice the leg in: Van Buren up to the leg's start, the leg, then on south.
def _has(c, q): return next((i for i, p in enumerate(c) if abs(p[0] - q[0]) < 2e-6 and abs(p[1] - q[1]) < 2e-6), None)
_A, _B = (-87.626412, 41.876995), (-87.626032, 41.876699)
_c = next(l['c'] for l in LINES if l['c'] and _has(l['c'], _A) is not None and _has(l['c'], _B) is not None)
_i, _j = _has(_c, _A), _has(_c, _B); LEG = _c[_i:_j + 1] if _i < _j else _c[_j:_i + 1][::-1]
c = R['loop_s']; k = next(i for i, p in enumerate(c) if p[0] > -87.62645 and p[1] < 41.8772)
j = next(i for i, p in enumerate(c) if m(p, LEG[-1]) < 3 or (i > k and p[1] < LEG[-1][1]))
R['loop_s'] = c[:k] + [[round(p[0], 7), round(p[1], 7), 1] for p in LEG] + c[j:]
for k, c in R.items(): print(k, f'{sum(m(a, b) for a, b in zip(c, c[1:])) / 1609.34:.2f} mi, {len(c)} points')
# station polygons (centres) within 120 m of a route: candidates for the stations the timetable names
_TR = cKDTree([xy(p) for c in R.values() for p in c])
PNEAR = [[round(p[0], 7), round(p[1], 7), p[2]] for p in POLYS if _TR.query(xy(p))[0] < 120]
print(len(PNEAR), 'station polygons near the routes')
json.dump(dict(source='Mississippi Rails (Tony Howe and David Price), Chicago interurbans 1948 KML (Brendan, 25 Nov 2026); routes cut by tools/chi_extract.py',
               note='Each point is [lon, lat, 1 if on \'L\' (CTA) track]. loop_n / loop_s: Roosevelt Road - Lake & Wells junction by Wabash / by Wells and Van Buren; the others run '
                    'north from the Lake & Wells junction (branch: Lake Bluff - Mundelein). A northbound route is loop_n + tail, a southbound one the tail reversed + loop_s.',
               routes=R, polys=PNEAR), open(os.path.join(HERE, 'traces', 'chicago', 'cnsm_routes.json'), 'w'))
