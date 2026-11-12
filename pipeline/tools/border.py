"""Which side of the Canada - US boundary a point is on: count crossings of the Natural Earth 1:10m boundary on a ray due north (to 75 N).
West of 141 W is Alaska. Approximate where Natural Earth simplifies the boundary through rivers and lakes (within about a kilometre)."""
import json, os
_SRC = os.path.join(os.path.dirname(__file__), '..', '..', 'basemap', 'sources', 'ne_10m_admin_0_boundary_lines_land_cut.geojson')
_SEGS = []
for f in json.load(open(_SRC))['features']:
    g = f['geometry']
    for c in (g['coordinates'] if g['type'] == 'MultiLineString' else [g['coordinates']]):
        for (x1, y1), (x2, y2) in zip(c, c[1:]):
            if x1 != x2: _SEGS.append((min(x1, x2), max(x1, x2), x1, y1, x2, y2))
_SEGS.sort()
import bisect
_XS = [s[0] for s in _SEGS]
_W = max(s[1] - s[0] for s in _SEGS)

def in_us(lon, lat):
    if lon < -141.0: return lat < 72                        # Alaska
    n = 0
    i = bisect.bisect_left(_XS, lon - _W)
    while i < len(_SEGS) and _SEGS[i][0] <= lon:
        a, b, x1, y1, x2, y2 = _SEGS[i]; i += 1
        if not (a <= lon < b): continue
        y = y1 + (y2 - y1) * (lon - x1) / (x2 - x1)
        if y > lat: n += 1
    return n % 2 == 1
