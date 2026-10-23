"""No boat in two places at once: for every named vessel, its sailings over the week (by their service days) must not overlap.
    python3 tools/check_vessels.py"""
import csv, json, os
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEEK = 7 * 86400
cal = {r['service_id']: [int(r[d]) for d in ('monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday')]
       for r in csv.DictReader(open(os.path.join(HERE, 'gtfs', 'calendar.txt')))}
vd = json.load(open(os.path.join(HERE, 'viz_data.json')))
spans, dated = {}, {}
for L in vd['lines']:
    for t in L.get('trips', []):
        v = t.get('vessel')
        if not v: continue
        a, b = t['stops'][0][2], t['stops'][-1][1]
        if 'd0' in t:                                                  # a dated sailing: only its days in the week, not carried round
            a2, b2 = max(0, t['d0'] * 86400 + a), min(WEEK, t['d0'] * 86400 + b)
            if a2 < b2: dated.setdefault(v, []).append((a2, b2, t['id']))
            continue
        days = cal.get(t['svc'])
        if days is None: print(f'  ?? {t["id"]}: service {t["svc"]} not in calendar.txt'); continue
        for d, on in enumerate(days):
            if on: spans.setdefault(v, []).append((d * 86400 + a, d * 86400 + b, t['id'], d))
bad = 0
for v, ds in sorted(dated.items()):
    if v in spans: print(f'  ?? {v}: has both dated and weekly sailings'); bad += 1
    ds = sorted(ds)
    for (a1, b1, i1), (a2, b2, i2) in zip(ds, ds[1:]):
        if a2 < b1: bad += 1; print(f'  !! {v}: {i1} (dated) runs to {b1 / 86400:.2f} d, but {i2} leaves at {a2 / 86400:.2f} d')
for v, ss in sorted(spans.items()):
    ss = sorted(ss + [(a + WEEK, b + WEEK, i, d) for a, b, i, d in ss if b > WEEK - 86400] + [(a - WEEK, b - WEEK, i, d) for a, b, i, d in ss if a >= WEEK])
    for (a1, b1, i1, d1), (a2, b2, i2, d2) in zip(ss, ss[1:]):
        if a2 < b1 and i1 != i2:
            bad += 1; day = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
            print(f'  !! {v}: {i1} ({day[d1]}) runs to {(b1 % 86400) // 3600:02d}:{b1 % 3600 // 60:02d} {day[(b1 // 86400) % 7]}, but {i2} ({day[d2]}) leaves at {(a2 % 86400) // 3600:02d}:{a2 % 3600 // 60:02d} {day[(a2 // 86400) % 7]}')
print(f'{len(spans)} named vessels, {sum(len(s) for s in spans.values())} sailings a week; {bad} overlaps')
