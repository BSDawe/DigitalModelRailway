"""Burnaby Lake line geometry: Carrall St -> (street tracks) -> Fourth District main line -> (NW streets) -> New Westminster station."""
import json, math, contextlib, io
with contextlib.redirect_stdout(io.StringIO()):
    import geometry as g   # reuses the KML parse + street-track routing network
from shapely.geometry import LineString, Point

bl = [l for l in g.lines if l['path'].endswith('Fourth District/Main line')][0]
M = LineString(g.proj(bl['lonlat']))
if Point(M.coords[0]).x > Point(M.coords[-1]).x:   # make it run west -> east
    M = LineString(list(M.coords)[::-1])
nw_xy = g.D.coords[0]            # New Westminster station end of the Chilliwack main line
A_pts, a1, a2 = g.route(g.carrall_xy, M.coords[0])
C_pts, c1, c2 = g.route(M.coords[-1], nw_xy)
MI = 1609.344
print(f'Vancouver street section {LineString(A_pts).length/MI:.2f} mi (snap {a1:.0f}/{a2:.0f} m)')
print(f'Burnaby Lake right-of-way {M.length/MI:.2f} mi')
print(f'New Westminster streets {LineString(C_pts).length/MI:.2f} mi (snap {c1:.0f}/{c2:.0f} m)')
full = list(A_pts) + list(M.coords) + list(C_pts)
clean = [full[0]]
for p in full[1:]:
    if math.dist(p, clean[-1]) > 0.5: clean.append(p)
R = LineString(clean)
print(f'TOTAL {R.length/MI:.2f} mi')
# which named street tracks does each end use?
import re
def streets_on(pts):
    ls = LineString(pts); seen = []
    for l in g.net_lines:
        if 'Street railways' not in l['path']: continue
        s = LineString(g.proj(l['lonlat']))
        samp = [s.interpolate(i / 10, normalized=True) for i in range(11)]
        if sum(ls.distance(q) < 6 for q in samp) >= 8:
            d = re.sub('<[^>]+>', '', l['desc']).strip()
            if d and 'Intersection' not in d and d not in seen: seen.append(d[:90])
    return seen
print('Vancouver end via:', *streets_on(A_pts), sep='\n  ')
print('New Westminster end via:', *streets_on(C_pts), sep='\n  ')
json.dump(dict(route=[g.inv(x, y) for x, y in R.coords],
               pieces=dict(A=LineString(A_pts).length, M=M.length, C=LineString(C_pts).length)),
          open('bl_geometry.json', 'w'))
