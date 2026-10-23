"""Regression check: where every train and boat is at 24 sample moments, before and after. Usage: python3 tools/ab.py [baseline_viz.json]
The baseline defaults to tools/.baseline_viz.json (copy viz_data.json there once a build is accepted). Prints, per line, how many positions are the
same, moved more than 30 m, gone or new, so a change can be seen to touch only the lines it was meant to."""
import sys, json, os, collections
from playwright.sync_api import sync_playwright
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); out = os.path.join(HERE, 'tools', 'out'); os.makedirs(out, exist_ok=True)
base = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'tools', '.baseline_viz.json')
tp = open(os.path.join(HERE, 'page_template.html')).read().replace('__WATER__', '{"type":"FeatureCollection","features":[]}') if False else open(os.path.join(HERE, 'page_template.html')).read().replace('__WATER__', open(os.path.join(HERE, 'water_embedded.json')).read())
for f, data in (('a', base), ('b', os.path.join(HERE, 'viz_data.json'))):
    open(os.path.join(out, f + '.html'), 'w').write('<!doctype html><meta charset="utf-8">' + tp.replace('__DATA__', open(data).read()))
JS = """() => { const out = {}; for (const day of ['mon','wed','sat','sun']) for (const T of [6*3600, 9.5*3600, 12.1*3600, 15.75*3600, 20*3600, 23.5*3600]) {
   for (const t of activeTrips(day)) { const st = tripState(t, T); if (st) out[day+'|'+T+'|'+t.id] = [t.rk, Math.round(st.x), Math.round(st.y), st.moving]; } } return out; }"""
with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/opt/pw-browsers/chromium'); res = []
    for f in ('a', 'b'):
        pg = b.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto('file://' + os.path.join(out, f + '.html')); pg.wait_for_timeout(2500); res.append(pg.evaluate(JS)); print(f, len(res[-1]), 'positions', errs[:3])
    b.close()
A, B = res; diff, miss, new, same, moved_ids = (collections.Counter() for _ in range(5))
for k, v in A.items():
    if k not in B: miss[v[0]] += 1
    elif abs(v[1] - B[k][1]) > 30 or abs(v[2] - B[k][2]) > 30: diff[v[0]] += 1; moved_ids[k.split('|')[2]] += 1
    else: same[v[0]] += 1
for k, v in B.items():
    if k not in A: new[v[0]] += 1
print('same', sum(same.values()), 'on', len(same), 'lines'); print('moved >30 m', dict(diff), 'trains:', dict(moved_ids)); print('gone', dict(miss)); print('new', dict(new))
