"""Integrity check of the GTFS feed in gtfs/: unique ids, every reference resolves, times run forward along each trip. Prints one line per problem, then a summary."""
import csv, os, collections
G = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'gtfs')
rd = lambda f: list(csv.DictReader(open(os.path.join(G, f), newline='')))
T = {f: rd(f + '.txt') for f in ('agency', 'routes', 'trips', 'stops', 'stop_times', 'calendar', 'shapes')}
bad = 0
def problem(msg):
    global bad; bad += 1
    if bad <= 25: print('!!', msg)
for f, k in (('agency', 'agency_id'), ('routes', 'route_id'), ('trips', 'trip_id'), ('stops', 'stop_id'), ('calendar', 'service_id')):
    for v, n in collections.Counter(r[k] for r in T[f]).items():
        if n > 1: problem(f'{f}: {k} {v} appears {n} times')
ids = {f: {r[k] for r in T[f]} for f, k in (('agency', 'agency_id'), ('routes', 'route_id'), ('trips', 'trip_id'), ('stops', 'stop_id'), ('calendar', 'service_id'), ('shapes', 'shape_id'))}
for r in T['routes']:
    if r['agency_id'] not in ids['agency']: problem(f"route {r['route_id']}: no agency {r['agency_id']}")
for r in T['trips']:
    for k, f in (('route_id', 'routes'), ('service_id', 'calendar'), ('shape_id', 'shapes')):
        if r.get(k) and r[k] not in ids[f]: problem(f"trip {r['trip_id']}: no {k} {r[k]}")
sec = lambda t: int(t[:-6]) * 3600 + int(t[-5:-3]) * 60 + int(t[-2:])
by = collections.defaultdict(list)
for r in T['stop_times']:
    if r['trip_id'] not in ids['trips']: problem(f"stop_time: no trip {r['trip_id']}")
    if r['stop_id'] not in ids['stops']: problem(f"stop_time: no stop {r['stop_id']} (trip {r['trip_id']})")
    by[r['trip_id']].append(r)
for t, rs in by.items():
    rs.sort(key=lambda r: int(r['stop_sequence'])); prev = -1
    for r in rs:
        a, d = sec(r['arrival_time']), sec(r['departure_time'])
        if a < prev or d < a: problem(f"trip {t}: time goes backwards at {r['stop_id']}"); break
        prev = d
for t in ids['trips'] - set(by): problem(f'trip {t} has no stop times')
print(f"GTFS: {len(T['agency'])} agencies, {len(T['routes'])} routes, {len(T['trips'])} trips, {len(T['stops'])} stops, {len(T['stop_times'])} stop times; {bad} problems")
