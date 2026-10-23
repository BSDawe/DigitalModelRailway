"""How long a frame takes, by view: python3 tools/perf.py. Headless Chromium has no GPU, so the numbers are pessimistic; compare before and after.
'still' = the view is not moving (playback); 'pan' = the view moves every frame (dragging, zooming, following a train)."""
import os, json
from playwright.sync_api import sync_playwright
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); out = os.path.join(HERE, 'tools', 'out'); os.makedirs(out, exist_ok=True)
open(os.path.join(out, 'page_test.html'), 'w').write('<!doctype html><meta charset="utf-8">' + open(os.path.join(HERE, 'fraser_valley_1949.html')).read())
JS = """() => { S.playing = false; const res = {};
  const states = () => { const s = []; for (const t of activeTrips(S.day)) { const st = tripState(t, S.T); if (st) s.push({ t, st }); } return s; };
  for (const v of ['lm', 'sound', 'kv', 'all']) { fit(v); S.T = 10 * 3600; const st = states();
    draw(st); let t0 = performance.now(); for (let i = 0; i < 20; i++) { S.T += 60; draw(states()); ctx.getImageData(0, 0, 1, 1); } const still = (performance.now() - t0) / 20;
    t0 = performance.now(); for (let i = 0; i < 20; i++) { view.cx += 40 / view.k / 20; draw(st); ctx.getImageData(0, 0, 1, 1); } const pan = (performance.now() - t0) / 20;
    res[v] = [Math.round(still * 10) / 10, Math.round(pan * 10) / 10, st.length]; }
  return res; }"""
with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/opt/pw-browsers/chromium')
    for name, vp, dpr in (('desktop 1500x900', {'width': 1500, 'height': 900}, 1), ('phone 390x844 @3x', {'width': 390, 'height': 844}, 3)):
        pg = b.new_page(viewport=vp, device_scale_factor=dpr); pg.goto('file://' + os.path.join(out, 'page_test.html')); pg.wait_for_timeout(2500)
        r = pg.evaluate(JS); print(name, ' '.join(f"{k}: still {v[0]} ms, pan {v[1]} ms ({v[2]} moving)" for k, v in r.items())); pg.close()
    b.close()
