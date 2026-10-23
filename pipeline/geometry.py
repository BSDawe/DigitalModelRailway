"""Build the Vancouver–Chilliwack route polyline from the BCER KML.

Pieces:
  A  Carrall St station -> 15th Ave & Commercial   (routed over Vancouver street-railway tracks)
  B  First District private right of way to New Westminster (12th St)
  C  12th St -> New Westminster station            (routed over NW street tracks)
  D  Third District main line NW -> Chilliwack
"""
import json, math, os
from xml.etree import ElementTree as ET
import networkx as nx
from pyproj import Transformer
from shapely.geometry import LineString, Point
from shapely.ops import linemerge

KML = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'British_Columbia_Electric_Railway_Company.kml')
NS = {'k': 'http://www.opengis.net/kml/2.2'}
K = '{http://www.opengis.net/kml/2.2}'
fwd = Transformer.from_crs(4326, 26910, always_xy=True).transform
inv = Transformer.from_crs(26910, 4326, always_xy=True).transform

tree = ET.parse(KML)
parent = {c: p for p in tree.iter() for c in p}


def folder_path(e):
    out = []
    while e in parent:
        e = parent[e]
        if e.tag == K + 'Folder':
            out.append(e.find('k:name', NS).text)
    return '/'.join(reversed(out))


def coords(p):
    return [tuple(map(float, c.split(',')[:2])) for c in p.find('.//k:coordinates', NS).text.split()]


lines, points = [], []
for p in tree.iter(K + 'Placemark'):
    fp = folder_path(p)
    nm_el = p.find('k:name', NS)
    name = (nm_el.text or '') if nm_el is not None else ''
    d = p.find('k:description', NS)
    desc = (d.text or '') if d is not None else ''
    if p.find('.//k:LineString', NS) is not None:
        for ls in p.findall('.//k:LineString', NS):
            c = [tuple(map(float, x.split(',')[:2])) for x in ls.find('k:coordinates', NS).text.split()]
            if len(c) >= 2:
                lines.append(dict(path=fp, name=name, desc=desc, lonlat=c))
    elif p.find('.//k:Point', NS) is not None:
        points.append(dict(path=fp, name=name, desc=desc, lonlat=coords(p)[0]))


def proj(ll):
    return [fwd(x, y) for x, y in ll]


def sel(pred):
    return [l for l in lines if pred(l)]


# ---- main pieces
first_main = sel(lambda l: l['path'].endswith('First District/Main line'))
third_main = sel(lambda l: l['path'].endswith('Third District/Main line') and 'Chilliwack' in l['desc'])[0]
pieceB = [l for l in first_main if l['desc'].startswith('Private right of way beginning at 15th')][0]

B = LineString(proj(pieceB['lonlat']))
D = LineString(proj(third_main['lonlat']))

# ---- routing network for the street sections
net_lines = sel(lambda l: ('Street railways/British Columbia Electric Railway Vancouver' in l['path']
                           or 'Street railways/British Columbia Electric Railway New Westminster' in l['path']
                           or 'First District' in l['path'] or 'Third District' in l['path'])
                and 'car house' not in l['path'].lower() and 'yard' not in l['path'].lower())

G = nx.Graph()
STEP = 8.0  # densify to 8 m so endpoints can snap onto segment interiors
dense = []
for i, l in enumerate(net_lines):
    ls = LineString(proj(l['lonlat']))
    n = max(2, int(ls.length / STEP) + 1)
    pts = [ls.interpolate(k / (n - 1), normalized=True).coords[0] for k in range(n)]
    ids = [(i, k) for k in range(n)]
    for (a, pa), (b, pb) in zip(zip(ids, pts), zip(ids[1:], pts[1:])):
        G.add_edge(a, b, w=math.dist(pa, pb))
    for a, pa in zip(ids, pts):
        G.nodes[a]['xy'] = pa
    dense.append((ids, pts))

# snap every line endpoint onto the nearest vertex of any other line within 12 m
import numpy as np
allid = [nid for ids, _ in dense for nid in ids]
allxy = np.array([p for _, pts in dense for p in pts])
for ids, pts in dense:
    for nid, p in ((ids[0], pts[0]), (ids[-1], pts[-1])):
        d = np.hypot(allxy[:, 0] - p[0], allxy[:, 1] - p[1])
        for j in np.where(d < 12)[0]:
            if allid[j][0] != nid[0]:
                G.add_edge(nid, allid[j], w=float(d[j]) + 0.01)


def nearest_node(xy):
    d = np.hypot(allxy[:, 0] - xy[0], allxy[:, 1] - xy[1])
    j = int(d.argmin())
    return allid[j], float(d[j])


def route(a_xy, b_xy):
    na, da = nearest_node(a_xy)
    nb, db = nearest_node(b_xy)
    path = nx.shortest_path(G, na, nb, weight='w')
    return [G.nodes[n]['xy'] for n in path], da, db


carrall = [p for p in points if p['name'] == 'Carrall Street station'][0]
carrall_xy = fwd(*carrall['lonlat'])
A_pts, da, db = route(carrall_xy, B.coords[0])
C_pts, dc, dd = route(B.coords[-1], D.coords[0])
print(f'A snap {da:.0f}/{db:.0f} m, len {LineString(A_pts).length/1609.34:.2f} mi')
print(f'B len {B.length/1609.34:.2f} mi')
print(f'C snap {dc:.0f}/{dd:.0f} m, len {LineString(C_pts).length/1609.34:.2f} mi')
print(f'D len {D.length/1609.34:.2f} mi')

full = list(A_pts) + list(B.coords) + list(C_pts) + list(D.coords)
# drop consecutive duplicates / tiny back-steps
clean = [full[0]]
for p in full[1:]:
    if math.dist(p, clean[-1]) > 0.5:
        clean.append(p)
route_ls = LineString(clean)
print(f'TOTAL {route_ls.length/1609.34:.2f} mi (timetable: 76.3)')

# ---- stations
third_st = [p for p in points if p['path'].endswith('Third District/Stations')]
json.dump(dict(
    route=[inv(x, y) for x, y in route_ls.coords],
    pieces_len_m=dict(A=LineString(A_pts).length, B=B.length, C=LineString(C_pts).length, D=D.length),
    carrall=carrall['lonlat'],
    stations=[dict(name=p['name'], desc=p['desc'], lonlat=p['lonlat']) for p in third_st],
), open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'geometry.json'), 'w'))
