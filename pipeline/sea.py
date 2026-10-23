"""Routes over water for the steamers: a raster of the water layer (water_union.pkl, EPSG:3347, built by water_build.py) and a least-cost
path between ports that keeps off the shore where there is room. Used by boats_build.py."""
import math, os, pickle
import numpy as np
from PIL import Image, ImageDraw
from pyproj import Transformer
from scipy import ndimage
from shapely.geometry import LineString, box
from skimage.graph import MCP_Geometric
HERE = os.path.dirname(os.path.abspath(__file__))
to_xy = Transformer.from_crs(4326, 3347, always_xy=True).transform
to_ll = Transformer.from_crs(3347, 4326, always_xy=True).transform
SEA_VERSION = 'v5'        # bump when the mask rules change, so cached lanes (sea_legs.json) are redrawn
# Banks that dry or nearly dry but are water in the layer: steamers kept to deep water round them (Brendan, from the chart of the Fraser mouth).
# Rough outlines, lon/lat, drawn generously over the adjoining land; the main channel from Steveston to Sand Heads is left open between the first two.
SHOALS = [
    # Sturgeon Bank: Point Grey to the Steveston jetty, out to the drop-off
    [(-123.255, 49.268), (-123.278, 49.262), (-123.297, 49.235), (-123.302, 49.200), (-123.306, 49.160), (-123.309, 49.125), (-123.306, 49.1105), (-123.280, 49.1150),
     (-123.250, 49.1215), (-123.222, 49.1265), (-123.200, 49.1290), (-123.185, 49.135), (-123.170, 49.150), (-123.170, 49.240), (-123.200, 49.262)],
    # Roberts Bank: south of the main channel to Tsawwassen
    [(-123.300, 49.1015), (-123.270, 49.1065), (-123.240, 49.1125), (-123.215, 49.1160), (-123.195, 49.1150), (-123.180, 49.1120), (-123.150, 49.090), (-123.100, 49.060),
     (-123.085, 49.030), (-123.085, 49.003), (-123.140, 49.000), (-123.185, 49.020), (-123.240, 49.045), (-123.280, 49.070), (-123.300, 49.090)],
    # Deception Pass: open water in the Washington layer, but not a ferry route (Brendan, 10 October 2026): closed to the lanes
    [(-122.668, 48.398), (-122.622, 48.398), (-122.622, 48.416), (-122.668, 48.416)],
    # Spanish Bank: the north shore of Point Grey
    [(-123.268, 49.270), (-123.262, 49.288), (-123.215, 49.289), (-123.190, 49.280), (-123.185, 49.272), (-123.230, 49.268)],
]
_U = None
def water():
    global _U
    if _U is None:
        _U = pickle.load(open(os.path.join(HERE, 'water_union.pkl'), 'rb'))
        _x = os.path.join(HERE, 'water_extra.pkl')                 # water_extra.py: Washington's water in place of the US side, and the Gulf of Alaska
        if os.path.exists(_x):
            X = pickle.load(open(_x, 'rb')); _U = _U.difference(X['cut']).union(X['add'])
    return _U

class Sea:
    """A water mask over the box around some lon/lat points. res: cell size in metres; shore: width of the band along the shore that costs extra."""
    def __init__(self, pts_lonlat, res=100.0, margin=6000.0, shore=500.0):
        xy = [to_xy(*p) for p in pts_lonlat]
        self.x0 = min(p[0] for p in xy) - margin; self.y1 = max(p[1] for p in xy) + margin
        x1 = max(p[0] for p in xy) + margin; y0 = min(p[1] for p in xy) - margin
        self.res = res; self.w = int((x1 - self.x0) / res) + 1; self.h = int((self.y1 - y0) / res) + 1
        bb = box(self.x0, y0, x1, self.y1); img = Image.new('L', (self.w, self.h), 0); d = ImageDraw.Draw(img)
        px = lambda c: [((x - self.x0) / res, (self.y1 - y) / res) for x, y in c]
        for g in water().geoms:
            b = g.bounds
            if b[2] < self.x0 or b[0] > x1 or b[3] < y0 or b[1] > self.y1: continue
            d.polygon(px(g.exterior.coords), fill=1)
            for r in g.interiors:
                if len(r.coords) >= 3: d.polygon(px(r.coords), fill=0)
        for sh in SHOALS: d.polygon(px([to_xy(*q) for q in sh]), fill=0)                 # banks count as land
        self.mask = np.array(img, dtype=bool)
        dist = ndimage.distance_transform_edt(self.mask) * res                    # metres from the shore, on the water
        self.cost = np.where(self.mask, 1.0 + 3.0 * np.clip(1.0 - dist / shore, 0, 1), 400.0)   # land is passable only as a last resort (a gap in the layer)
        _, self.near = ndimage.distance_transform_edt(~self.mask, return_indices=True)           # nearest water cell to any cell
    def cell(self, lonlat):
        x, y = to_xy(*lonlat); c, r = int((x - self.x0) / self.res), int((self.y1 - y) / self.res)
        r = min(max(r, 0), self.h - 1); c = min(max(c, 0), self.w - 1)
        return int(self.near[0][r, c]), int(self.near[1][r, c])
    def snap_m(self, lonlat):
        """how far the port had to move to reach water, metres"""
        x, y = to_xy(*lonlat); r, c = self.cell(lonlat)
        return math.hypot(self.x0 + (c + .5) * self.res - x, self.y1 - (r + .5) * self.res - y)
    def leg(self, a, b):
        """lon/lat points along the least-cost path from port a to port b, and the share of it that crosses land in the layer"""
        ra, rb = self.cell(a), self.cell(b)
        m = MCP_Geometric(self.cost, fully_connected=True); m.find_costs([ra], [rb]); path = m.traceback(rb)
        land = sum(1 for r, c in path if not self.mask[r, c]) / max(1, len(path))
        xy = [(self.x0 + (c + .5) * self.res, self.y1 - (r + .5) * self.res) for r, c in path]
        if len(xy) > 2:
            ln = LineString(xy).simplify(self.res * 1.2)
            xy = _smooth(list(ln.coords))
        return [to_ll(*p) for p in xy], land

def _smooth(pts, n=2):
    """Chaikin corner cutting, keeping the end points"""
    for _ in range(n):
        if len(pts) < 3: break
        out = [pts[0]]
        for p, q in zip(pts, pts[1:]):
            out += [(0.75 * p[0] + 0.25 * q[0], 0.75 * p[1] + 0.25 * q[1]), (0.25 * p[0] + 0.75 * q[0], 0.25 * p[1] + 0.75 * q[1])]
        out.append(pts[-1]); pts = out
    return pts
