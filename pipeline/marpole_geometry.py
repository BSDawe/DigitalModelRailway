"""Second District routes: Davie St -> Marpole -> Steveston ('lulu') and Marpole -> New Westminster ('nwm')."""
import json, math, contextlib, io, re
import numpy as np, networkx as nx
with contextlib.redirect_stdout(io.StringIO()):
    import geometry as g
from shapely.geometry import LineString, Point
from shapely.ops import substring
MI = 1609.344

sec = [l for l in g.lines if 'Second District' in l['path']]
mains = [l for l in sec if l['path'].endswith('Second District/Main line')]
for l in mains: print('main:', l['desc'][:50], len(l['lonlat']))
nwline = [l for l in mains if l['desc'].startswith('Lulu and New Westminster Line.') and 'Double' not in l['desc']][0]
stev = [l for l in mains if l['desc'].startswith('Lulu line to Steveston')][0]
N = LineString(g.proj(nwline['lonlat'])); S = LineString(g.proj(stev['lonlat']))
if Point(N.coords[0]).x > Point(N.coords[-1]).x: N = LineString(list(N.coords)[::-1])   # Kitsilano (west) -> NW (east)
if Point(S.coords[0]).y < Point(S.coords[-1]).y: S = LineString(list(S.coords)[::-1])   # Marpole (north) -> Steveston
jx = N.project(Point(S.coords[0]))
print(f'junction on NW line at {jx/MI:.2f} mi, gap {N.distance(Point(S.coords[0])):.0f} m')
kits_to_marpole = substring(N, 0, jx); marpole_to_nw = substring(N, jx, N.length)

# network: Vancouver streets + Second District + First District, for the Davie St and New Westminster ends
net = [l for l in g.lines if ('Street railways/British Columbia Electric Railway Vancouver' in l['path']
        or 'Street railways/British Columbia Electric Railway New Westminster' in l['path']
        or 'Second District' in l['path'] or 'First District' in l['path'] or 'Third District' in l['path'])
       and 'car house' not in l['path'].lower() and 'yard' not in l['path'].lower() and 'Terminal' not in l['path']]
G = nx.Graph(); ids_all = []; xy_all = []; dense = []
for i, l in enumerate(net):
    ls = LineString(g.proj(l['lonlat'])); n = max(2, int(ls.length / 8) + 1)
    pts = [ls.interpolate(k / (n - 1), normalized=True).coords[0] for k in range(n)]
    ids = [(i, k) for k in range(n)]
    for a, b, pa, pb in zip(ids, ids[1:], pts, pts[1:]): G.add_edge(a, b, w=math.dist(pa, pb))
    for a, p in zip(ids, pts): G.nodes[a]['xy'] = p
    dense.append((ids, pts)); ids_all += ids; xy_all += pts
xy_all = np.array(xy_all)
for ids, pts in dense:
    for nid, p in ((ids[0], pts[0]), (ids[-1], pts[-1])):
        d = np.hypot(xy_all[:, 0] - p[0], xy_all[:, 1] - p[1])
        for j in np.where(d < 12)[0]:
            if ids_all[j][0] != nid[0]: G.add_edge(nid, ids_all[j], w=float(d[j]) + 0.01)
def near(xy):
    d = np.hypot(xy_all[:, 0] - xy[0], xy_all[:, 1] - xy[1]); j = int(d.argmin()); return ids_all[j], float(d[j])
def route(a, b):
    na, da = near(a); nb, db = near(b)
    return [G.nodes[n]['xy'] for n in nx.shortest_path(G, na, nb, weight='w')], da, db

davie = [p for p in g.points if p['path'].endswith('Second District/Stations') and p['name'].startswith('Davie')][0]
dxy = g.fwd(*davie['lonlat'])
# Davie St -> Granville St -> False Creek (Kitsilano) trestle -> Kitsilano yard connection -> Arbutus line
loop = [l for l in g.lines if l['path'].endswith('Vancouver/Private right of ways') and l['desc'].startswith('Kitsilano loop line')]
loop = min(loop, key=lambda l: LineString(g.proj(l['lonlat'])).distance(Point(g.fwd(-123.1347, 49.2743))))
L = LineString(g.proj(loop['lonlat']))
if Point(L.coords[0]).x < Point(L.coords[-1]).x: L = LineString(list(L.coords)[::-1])     # east (Granville St) -> west
yard = [l for l in g.lines if 'Kitsilano yard' in l['path'] and l['desc'].strip().startswith('Kitsilano yard.')]
yard = min(yard, key=lambda l: math.dist(g.fwd(*l['lonlat'][-1][:2]), kits_to_marpole.coords[0]))
Y = LineString(g.proj(yard['lonlat']))
if math.dist(Y.coords[0], kits_to_marpole.coords[0]) < math.dist(Y.coords[-1], kits_to_marpole.coords[0]): Y = LineString(list(Y.coords)[::-1])
print(f'yard line ends {math.dist(Y.coords[-1], kits_to_marpole.coords[0]):.0f} m from Arbutus line start; '
      f'starts {L.distance(Point(Y.coords[0])):.0f} m from trestle line')
A0, a1, a2 = route(dxy, L.coords[0])
cut = L.project(Point(Y.coords[0]))
A = list(A0) + list(substring(L, 0, cut).coords) + list(Y.coords)
print(f'trestle section {cut/MI:.2f} mi, yard connection {Y.length/MI:.2f} mi')
nw_xy = g.D.coords[0]
C, c1, c2 = route(marpole_to_nw.coords[-1], nw_xy)
def streets_on(pts):
    ls = LineString(pts); seen = []
    for l in net:
        s = LineString(g.proj(l['lonlat'])); samp = [s.interpolate(i / 10, normalized=True) for i in range(11)]
        if sum(ls.distance(q) < 6 for q in samp) >= 8:
            d = re.sub('<[^>]+>', '', l['desc']).strip()
            if d and 'Intersection' not in d and d[:80] not in seen: seen.append(d[:80])
    return seen
print(f'Davie St -> Kitsilano: {LineString(A).length/MI:.2f} mi (snap {a1:.0f}/{a2:.0f}) via', *streets_on(A), sep='\n   ')
print(f'Kitsilano -> Marpole {kits_to_marpole.length/MI:.2f} mi; Marpole -> Steveston {S.length/MI:.2f} mi; '
      f'Marpole -> 12th St {marpole_to_nw.length/MI:.2f} mi')
print(f'12th St -> NW station: {LineString(C).length/MI:.2f} mi (snap {c1:.0f}/{c2:.0f}) via', *streets_on(C), sep='\n   ')
def clean(pts):
    out = [pts[0]]
    for p in pts[1:]:
        if math.dist(p, out[-1]) > 0.5: out.append(p)
    return out
lulu = clean(list(A) + list(kits_to_marpole.coords) + list(S.coords))
nwm = clean(list(marpole_to_nw.coords) + list(C))
print(f'lulu route {LineString(lulu).length/MI:.2f} mi; nwm route {LineString(nwm).length/MI:.2f} mi')
json.dump(dict(lulu=[g.inv(*p) for p in lulu], nwm=[g.inv(*p) for p in nwm], davie=davie['lonlat'],
               marpole_chain_lulu=LineString(A).length + kits_to_marpole.length), open('marpole_geometry.json', 'w'))
