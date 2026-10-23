"""Join the Kettle Valley trains into through trains on one combined route: Vancouver - (CP main) - Odlum - (Kettle Valley) - Nelson -
(Crowsnest) - B.C. border. Run after cp_south_build.py. Replaces line 'kv' with the combined route; the Vancouver-Odlum and Nelson-Crowsnest
parts are marked owner 'none' so they are drawn once, by the CP main line and the Crowsnest line. Removes the split pieces of Nos. 11, 12,
45 and 46 from the 'cp' and 'cr' lines. (The GTFS feed keeps them as separate trips per line.)"""
import json, os, math
HERE = os.path.dirname(os.path.abspath(__file__))
vd = json.load(open(os.path.join(HERE, 'viz_data.json')))
L = {l['key']: l for l in vd['lines']}
cp, kv, cr = L['cp'], L['kv'], L['cr']

def cut(route, upto):
    out = [p for p in route if p[2] <= upto]
    nxt = next((p for p in route if p[2] > upto), None)
    if nxt and out and out[-1][2] < upto:
        a = out[-1]; f = (upto - a[2]) / (nxt[2] - a[2])
        out.append([round(a[0] + f * (nxt[0] - a[0]), 6), round(a[1] + f * (nxt[1] - a[1]), 6), upto])
    return out
def idx(line, name): return next(i for i, s in enumerate(line['stations']) if s['name'] == name)

odl_cp = cp['stations'][idx(cp, 'Odlum')]['chain']
r1 = cut(cp['route'], odl_cp)
off2 = odl_cp
r2 = [[p[0], p[1], round(p[2] + off2, 1)] for p in kv['route']]
nel_kv = kv['stations'][idx(kv, 'Nelson')]['chain'] + off2
off3 = r2[-1][2]
r3 = [[p[0], p[1], round(p[2] + off3, 1)] for p in cr['route']]
route = r1 + r2 + r3

stations, gid_idx, gid_line, remap = [], {}, {}, {}
def add(line, off, keep, lm):       # lm: the part's printed mile -> miles from Vancouver by this route
    for i, s in enumerate(line['stations']):
        if not keep(s): continue
        if s['gid'] in gid_idx and gid_line[s['gid']] != line['key']: remap[(line['key'], i)] = gid_idx[s['gid']]; continue   # shared between parts
        gid_idx.setdefault(s['gid'], len(stations)); gid_line[s['gid']] = line['key']; remap[(line['key'], i)] = len(stations)      # (a second call on one line is kept)
        stations.append(dict(s, chain=round(s['chain'] + off, 1), lmile=round(lm(s['mile']), 1)))
NUMS = {'11', '12', '45', '46'}
used_cp = {si for t in cp['trips'] if t['num'] in NUMS for si, *_ in t['stops']}
van = cp['stations'][idx(cp, 'Vancouver')]['mile']; od_mile = van - cp['stations'][idx(cp, 'Odlum')]['mile']     # CP main line miles run from Montreal
kv_od = kv['stations'][idx(kv, 'Odlum')]['mile']; cr_nel = cr['stations'][idx(cr, 'Nelson')]['mile']
add(cp, 0, lambda s: cp['stations'].index(s) in used_cp and s['chain'] <= odl_cp + 1, lambda m: van - m)
add(kv, off2, lambda s: True, lambda m: od_mile + kv_od - m)
used_cr = {si for t in cr['trips'] if t['num'] in NUMS for si, *_ in t['stops']}
add(cr, off3, lambda s: cr['stations'].index(s) in used_cr, lambda m: od_mile + kv_od + cr_nel - m)
# Odlum and Nelson are shared between parts: keep one station, the gids differ between lines
for nm in ('Odlum', 'Nelson'):
    ids = [i for i, s in enumerate(stations) if s['name'] == nm]
    for k, v in list(remap.items()):
        if v in ids[1:]: remap[k] = ids[0]
order = sorted(range(len(stations)), key=lambda i: stations[i]['chain'])
pos = {old: new for new, old in enumerate(order)}
dupes = {i for nm in ('Odlum', 'Nelson') for i in [j for j, s in enumerate(stations) if s['name'] == nm][1:]}
keep_order = [i for i in order if i not in dupes]
pos = {old: new for new, old in enumerate(keep_order)}
new_stations = [stations[i] for i in keep_order]
def R(line, si): return pos[remap[(line['key'], si)]]

def merge(parts, d):
    seq = []
    for line, t in (parts if d == 0 else parts[::-1]):
        st = [[R(line, s[0]), s[1] % 86400, s[2] % 86400, s[3]] for s in t['stops']]
        if seq and seq[-1][0] == st[0][0]:
            seq[-1][2] = st[0][2]; st = st[1:]
        seq += st
    base, prev = 0, -1
    for s in seq:
        for k in (1, 2):
            if s[k] + base < prev - 6 * 3600: base += 86400
            s[k] += base; prev = s[k]
    return seq

trips = []
for num in ('11', '12', '45', '46'):
    parts = []
    for line in (cp, kv, cr):
        t = next((t for t in line['trips'] if t['num'] == num or (num == '12' and t['num'] == '12')), None)
        if t: parts.append((line, t))
    d = parts[0][1]['dir']
    kvt = next(t for l, t in parts if l is kv)
    stops = merge(parts, d)
    note = {'11': 'Kootenay Express: from Medicine Hat and Lethbridge over the Crowsnest, Nelson, the Kettle Valley and the Coquihalla to Vancouver.',
            '12': 'Kettle Valley Express: Vancouver over the Coquihalla and the Kettle Valley to Nelson, then the Crowsnest to Lethbridge and Medicine Hat.',
            '45': 'Penticton to Vancouver overnight, through the Coquihalla.', '46': 'Vancouver to Penticton overnight, through the Coquihalla.'}[num]
    trips.append(dict(id='KV-' + num, num=num, name=kvt['name'], svc=kvt['svc'], dir=d, stops=stops, note=note))
    f = lambda x: f'{x // 3600:02d}:{x % 3600 // 60:02d}'
    print(num, ' -> '.join(f"{new_stations[s[0]]['name']} {f(s[1])}" for s in (stops[0], stops[-1])), len(stops), 'stops')
for t in kv['trips']:
    if t['num'] in NUMS: continue
    trips.append(dict(t, stops=[[R(kv, s[0]), s[1], s[2], s[3]] for s in t['stops']]))
for (a, _, da, _), (b, tb, _, _) in ((x, y) for t in trips for x, y in zip(t['stops'], t['stops'][1:])):
    assert tb >= da, (new_stations[a]['name'], new_stations[b]['name'])
nel = next(s['chain'] for s in new_stations if s['name'] == 'Nelson')
odl = next(s['chain'] for s in new_stations if s['name'] == 'Odlum')
kvline = dict(kv, route=route, stations=new_stations, trips=trips, dirLabels=['to Penticton, Nelson, the Crowsnest, Lethbridge and Medicine Hat', 'to Hope and Vancouver'],
              segments=[dict(owner='none', a=0.0, b=odl), dict(owner='none', a=nel, b=route[-1][2])])
for line in (cp, cr): line['trips'] = [t for t in line['trips'] if t['num'] not in NUMS]
vd['lines'] = [kvline if l['key'] == 'kv' else l for l in vd['lines']]
open(os.path.join(HERE, 'viz_data.json'), 'w').write(json.dumps(vd, separators=(',', ':')))
print('kv through line:', len(new_stations), 'stations,', len(trips), 'trips; route', round(route[-1][2] / 1609.344, 1), 'mi')
