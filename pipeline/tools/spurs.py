"""Stations a line reaches by going down a spur and back (the route doubles back on itself at the station): usually a station point placed
off the line. Usage: python3 tools/spurs.py"""
import json, math, os, bisect
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
v = json.load(open(os.path.join(HERE, 'viz_data.json')))
def at(r, ds, d):
    i = min(max(bisect.bisect_left(ds, d), 1), len(r) - 1); p, q = r[i - 1], r[i]; t = (d - p[2]) / (q[2] - p[2]) if q[2] > p[2] else 0
    return (p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t)
def m(a, b): return math.hypot((a[0] - b[0]) * 111320 * math.cos(math.radians(a[1])), (a[1] - b[1]) * 110574)
for L in v['lines']:
    if L.get('water'): continue
    r = L['route']; ds = [p[2] for p in r]
    for s in L['stations']:
        c = s['chain']
        if c < 400 or c > ds[-1] - 400: continue
        for off in (300, 600, 1200):
            if c - off < 0 or c + off > ds[-1]: break
            a, b = at(r, ds, c - off), at(r, ds, c + off)
            if m(a, b) < 0.25 * off: print(f"{L['key']:12s} {s['name']:28s} goes {off} m out and back"); break
