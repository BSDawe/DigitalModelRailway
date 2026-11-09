"""Maritime track bank (Brendan, 8 November 2026): the files in traces/maritimes/ read as one set, whatever railway or provenance, so a new railway is a new
file and nothing here changes. A helper, not a build step: import it from the Maritimes step (or its graph module) that needs track. See
traces/maritimes/README.md for the file layout, the properties and the status words.

  import mar_tracks as mt
  mt.features(owner='cn')                       -> [dict(coords=[(lon, lat), ...], own=..., name=..., status=..., cost=..., ...), ...]  status 'ok' only
  mt.features(owner=('cn', 'cp'), status=('ok', 'check'), box=(lon0, lon1, lat0, lat1))
  python3 mar_tracks.py                         -> what is on file (km by file, owner, status) and how the pieces connect
  python3 mar_tracks.py --owner cn --status ok,check --tie 150 --gaps 1500
      components of the track graph (ends tied to other track within --tie metres, as the loader does) and the loose ends that lie within --gaps
      metres of other track: the candidates for a connector. Run it after adding a file."""
import glob, json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); DIR = os.path.join(HERE, 'traces', 'maritimes')
STATUS = {'ok': 'use', 'check': 'in the file, not used until decided (see why)', 'post1948': 'built after 1948', 'not_cn': 'another company (industrial railway)',
          'quebec_overlap': 'already in the Quebec collection'}
def files():
    return sorted(glob.glob(os.path.join(DIR, '*.geojson')))
def features(owner=None, status=('ok',), box=None, names=None):
    """owner: a code or a collection of codes (None = all); status: the words to take (None = all); box: (lon0, lon1, lat0, lat1), a piece is kept if any point is in it;
    names: files to read (stems, e.g. ('cn', 'brendan')), None = all"""
    owner = {owner} if isinstance(owner, str) else (set(owner) if owner else None); status = {status} if isinstance(status, str) else (set(status) if status else None)
    out = []
    for fn in files():
        if names and os.path.splitext(os.path.basename(fn))[0] not in names: continue
        for f in json.load(open(fn))['features']:
            p = dict(f['properties']); c = [tuple(q[:2]) for q in f['geometry']['coordinates']]
            if owner and p['own'] not in owner: continue
            if status and p['status'] not in status: continue
            if box and not any(box[0] <= x <= box[1] and box[2] <= y <= box[3] for x, y in c): continue
            p['coords'] = c; p['file'] = os.path.splitext(os.path.basename(fn))[0]; out.append(p)
    return out
def _report(owner, status, tie, gaps):
    from pyproj import Transformer
    from shapely.geometry import LineString, Point
    from shapely.strtree import STRtree
    T = Transformer.from_crs(4326, 32620, always_xy=True)
    allf = features(None, None); L = lambda c: LineString([T.transform(x, y) for x, y in c]).length / 1000
    print('on file (km):'); tab = {}
    for p in allf: k = (p['file'], p['own'], p['status']); tab[k] = tab.get(k, 0) + L(p['coords'])
    for k, v in sorted(tab.items()): print(f'  {k[0]:11s} {k[1]:6s} {k[2]:15s} {v:8.1f}')
    use = features(owner, status); ls = [LineString([T.transform(x, y) for x, y in p['coords']]) for p in use]; tree = STRtree(ls)
    parent = list(range(len(ls)))
    def find(a):
        while parent[a] != a: parent[a] = parent[parent[a]]; a = parent[a]
        return a
    loose = []
    for i, l in enumerate(ls):
        for end in (l.coords[0], l.coords[-1]):
            pt = Point(end); best = (1e18, None)
            for j in tree.query(pt.buffer(max(tie, gaps))):
                if j != i:
                    d = ls[j].distance(pt)
                    if d < best[0]: best = (d, j)
            if best[1] is not None and best[0] <= tie: parent[find(i)] = find(best[1])
            elif best[1] is not None and best[0] <= gaps: loose.append((best[0], i, best[1]))
    comp = {}
    for i in range(len(ls)): comp.setdefault(find(i), []).append(i)
    comps = sorted(comp.values(), key=lambda c: -sum(ls[i].length for i in c))
    print(f'\n{len(use)} pieces (owner {owner or "all"}, status {",".join(status) if status else "all"}) in {len(comps)} connected groups (ends tied within {tie} m):')
    for c in comps:
        names = sorted({use[i]['constituent'] for i in c}); print(f'  {sum(ls[i].length for i in c) / 1000:8.1f} km  {len(c):3d} pieces  {"; ".join(names)[:150]}')
    print(f'\nloose ends within {gaps} m of other track (connector candidates):')
    seen = set()
    for d, i, j in sorted(loose):
        key = (use[i]['name'], use[j]['name'])
        if key in seen: continue
        seen.add(key); print(f'  {d:6.0f} m  {use[i]["name"][:46]}  ->  {use[j]["name"][:46]}')
if __name__ == '__main__':
    a = sys.argv[1:]; opt = lambda k, d: a[a.index(k) + 1] if k in a else d
    st = opt('--status', 'ok'); _report(opt('--owner', None) and opt('--owner', None).split(','), None if st == 'all' else st.split(','), float(opt('--tie', 150)), float(opt('--gaps', 1500)))
