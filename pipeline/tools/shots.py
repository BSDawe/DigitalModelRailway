"""Screenshots of the built page, for checking by eye. Usage: python3 tools/shots.py '<json list>' [outdir]
Each item: {"name": "x", "T": seconds, "day": "mon", and either "view": "<view key>" or "lon", "lat", "k" (pixels per metre, e.g. 0.02), optional "sel": trip id, "st": station name}"""
import sys, json, os
from playwright.sync_api import sync_playwright
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, 'tools', 'out'); os.makedirs(out, exist_ok=True)
open(os.path.join(out, 'page_test.html'), 'w').write('<!doctype html><meta charset="utf-8">' + open(os.path.join(HERE, 'fraser_valley_1949.html')).read())
with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/opt/pw-browsers/chromium'); pg = b.new_page(viewport={'width': 1500, 'height': 900}); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('console', lambda m: m.type == 'error' and errs.append(m.text))
    pg.goto('file://' + os.path.join(out, 'page_test.html')); pg.wait_for_timeout(3000)
    for s in json.loads(sys.argv[1]):
        js = """(s) => { S.playing = false; S.day = s.day || 'mon'; S.T = s.T; S.follow = false;
                 if (s.view) { fit(s.view); } else { const [x, y] = P(s.lon, s.lat); view.k = s.k; view.cx = x + (s.dx||0)/s.k; view.cy = y + (s.dy||0)/s.k; }
                 S.sel = s.sel ? { kind: 'train', id: s.sel } : (s.st != null ? {kind:'station', i: ST.findIndex(q => q.name === s.st)} : null); panelKey = ''; }"""
        pg.evaluate(js, s); pg.wait_for_timeout(800); pg.screenshot(path=os.path.join(out, s['name'] + '.png'))
    print('page errors:', [e for e in errs if 'ERR_' not in e][:5]); b.close()
