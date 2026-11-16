"""Impossible speeds: every hop between two consecutive calls of a trip that would need more than the limit (trains 85 mph, steamers 30 mph)
over at least 3 miles. A hit means a station in the wrong place or a wrong time (Brendan, 16 Nov 2026: a standing check).
Distances are straight-line ground miles between the two stations (the least the train could travel, whatever the route drawn). Usage: python3 tools/check_speeds.py [viz_data.json]   (prints one line per distinct hop)"""
import bisect, collections, json, math, os, sys
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAIL, WATER, MIN_MI = 85.0, 30.0, 3.0
def ground(route):
    acc = [0.0]
    for p, q in zip(route, route[1:]):
        acc.append(acc[-1] + 3958.8 * math.hypot(math.radians(q[0] - p[0]) * math.cos(math.radians((p[1] + q[1]) / 2)), math.radians(q[1] - p[1])))
    return acc
def hops(viz):
    out = collections.OrderedDict()
    for L in viz.get('lines', []):
        r = L.get('route') or []
        if len(r) < 2: continue
        acc, ch = ground(r), [p[2] for p in r]
        g = lambda c: acc[min(bisect.bisect_left(ch, c), len(ch) - 1)]
        st = L['stations']; water = L.get('kind') == 'v' or any(t.get('water') for t in L['trips'][:1])
        for t in L['trips']:
            s = t['stops']
            for a, b in zip(s, s[1:]):
                dt = (b[1] - a[2]) / 3600.0; A, B = st[a[0]], st[b[0]]; dm = 3958.8 * math.hypot(math.radians(B['lon'] - A['lon']) * math.cos(math.radians((A['lat'] + B['lat']) / 2)), math.radians(B['lat'] - A['lat']))
                if dm >= MIN_MI and (dt <= 0 or dm / dt > (WATER if water else RAIL)):
                    k = (L['key'],) + tuple(sorted((A['name'], B['name'])))
                    e = out.setdefault(k, dict(line=L['key'], a=A['name'], b=B['name'], miles=round(dm, 1), tt=round(abs((B.get('mile') or 0) - (A.get('mile') or 0)), 1), mins=set(), trains=set()))
                    e['mins'].add(round(dt * 60)); e['trains'].add(str(t.get('num') or t.get('id')))
    return list(out.values())
if __name__ == '__main__':
    H = hops(json.load(open(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'viz_data.json'))))
    for e in H:
        print(f"{e['line']:10s} {e['a']} - {e['b']}: {e['miles']} mi apart (timetable {e['tt']}) in {sorted(e['mins'])} min; trains {', '.join(sorted(e['trains'])[:8])}")
    print(len(H), 'impossible hops')
