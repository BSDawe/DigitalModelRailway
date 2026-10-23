"""Shared helpers: a routable graph of NRWN track (main line preferred), shortest paths, and clean LineStrings (UTM 10N)."""
import math
import numpy as np, networkx as nx
from pyproj import Transformer
from shapely.geometry import LineString
fwd = Transformer.from_crs(4326, 26910, always_xy=True).transform
inv = Transformer.from_crs(26910, 4326, always_xy=True).transform
MI = 1609.344

class Net:
    def __init__(self, features, subs=None):
        self.G = G = nx.Graph(); key = lambda p: (round(p[0], 1), round(p[1], 1))
        for f in features:
            if f['schema'] != '#kml_schema_ft_Track': continue
            d = f['data']; cls = d.get('trackClassification'); sub = d.get('subdivision1Name')
            if subs and sub not in subs: continue
            for c in f['coords']:
                pts = [fwd(*p) for p in c]
                for a, b in zip(pts, pts[1:]):
                    w = math.dist(a, b) * (1.0 if cls in ('Main', 'Connecting') else 4.0)
                    ka, kb = key(a), key(b)
                    if ka != kb and (not G.has_edge(ka, kb) or G[ka][kb]['w'] > w):
                        G.add_edge(ka, kb, w=w, sub=sub, cls=cls)
        nodes = np.array(list(G.nodes)); nlist = list(G.nodes)
        for n in list(G.nodes):
            if G.degree(n) == 1:
                d = np.hypot(nodes[:, 0] - n[0], nodes[:, 1] - n[1])
                for j in np.where((d > 0) & (d < 4))[0]: G.add_edge(n, nlist[j], w=float(d[j]), sub='join', cls='join')
        self.nodes, self.nlist = nodes, nlist

    def near(self, xy, main=False):
        d = np.hypot(self.nodes[:, 0] - xy[0], self.nodes[:, 1] - xy[1])
        if main:
            ok = np.array([any(self.G[n][m].get('cls') == 'Main' for m in self.G[n]) for n in self.nlist])
            d = np.where(ok, d, 1e18)
        i = int(np.argmin(d)); return self.nlist[i], float(d[i])

    def route(self, *pts_lonlat, start_any=False):
        """Shortest main-line path through a sequence of lon/lat points; returns (LineString, snap distances)."""
        out, snaps = [], []
        for k, (a, b) in enumerate(zip(pts_lonlat, pts_lonlat[1:])):
            na, da = self.near(fwd(*a), not (start_any and k == 0))   # start_any: the first point may be on a spur
            nb, db = self.near(fwd(*b), True); snaps += [da, db]
            p = nx.shortest_path(self.G, na, nb, weight='w')
            out += p if not out else p[1:]
        clean = [out[0]]
        for p in out[1:]:
            if math.dist(p, clean[-1]) > 0.5: clean.append(p)
        return LineString(clean), snaps
