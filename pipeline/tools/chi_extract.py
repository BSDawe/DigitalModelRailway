"""Cut the North Shore Line routes out of the Mississippi Rails Chicago interurbans KML (Brendan, 25 Nov 2026; private repo traces/chicago/Chicago_Interurbans_1948.kml)
and write them to the public traces/chicago/cnsm_routes.json (only the track the trains use, per the private / public rule).
Usage: python3 tools/chi_extract.py
The KML's pieces are joined where a piece end meets another piece (within 15 m) or another piece end (8 m); crossings without a piece end stay apart. Each route is the
shortest path through a few waypoints (station areas that fix the way: the Loop side, the Niles Center branch); out-and-back stubs are cut. The State Street subway and the
'L' yards are left out of the graph. The 'L' stretch is owned 'cta' (Chicago Transit Authority) up to Howard Street."""
import json, math, os, sys
import xml.etree.ElementTree as ET
import networkx as nx, numpy as np
from scipy.spatial import cKDTree
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KML = os.path.join(HERE, 'traces', 'chicago', 'Chicago_Interurbans_1948.kml')
K = '{http://www.opengis.net/kml/2.2}'
LINES = []
def walk(e, path):
    for c in e:
        if c.tag in (K + 'Folder', K + 'Document'): walk(c, path + [c.findtext(K + 'name') or ''])
        elif c.tag == K + 'Placemark':
            for ls in c.iter(K + 'LineString'):
                LINES.append(dict(path='/'.join(path), c=[[float(v) for v in x.split(',')[:2]] for x in ls.findtext(K + 'coordinates').split()]))
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
def route(wps):
    path = []
    for a, b in zip(wps, wps[1:]):
        sp = nx.shortest_path(G, near(a), near(b), weight='w'); path += sp if not path else sp[1:]
    out = []                                   # cut out-and-back stubs (a node visited twice)
    for n in path:
        if n in out: del out[out.index(n) + 1:]
        else: out.append(n)
    return [[round(v, 7) for v in P[n][0]] for n in out]
ROOSEVELT, CLARK_LAKE, QUINCY_WELLS, HOWARD = (-87.6266, 41.8673), (-87.6310, 41.8857), (-87.6338, 41.8787), (-87.6732, 42.0193)
DEMPSTER, MILWAUKEE = (-87.752, 42.041), (-87.9187, 43.0369)
R = dict(sv_north=route([ROOSEVELT, CLARK_LAKE, HOWARD, DEMPSTER, MILWAUKEE]), sv_south=route([MILWAUKEE, DEMPSTER, HOWARD, QUINCY_WELLS, ROOSEVELT]))
for k, c in R.items(): print(k, f'{sum(m(a, b) for a, b in zip(c, c[1:])) / 1609.34:.2f} mi, {len(c)} points')
json.dump(dict(source='Mississippi Rails (Tony Howe and David Price), Chicago interurbans 1948 KML (Brendan, 25 Nov 2026); routes cut by tools/chi_extract.py', routes=R),
          open(os.path.join(HERE, 'traces', 'chicago', 'cnsm_routes.json'), 'w'))
