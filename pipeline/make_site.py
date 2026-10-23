#!/usr/bin/env python3
"""Write the hosted site (site/) as a small page plus separate data files, instead of one page with everything inside it.

  site/index.html                    the page: styles, controls and a loader (no data)
  site/app.<hash>.js                 the map's code (page_template.html's script)
  site/data/manifest.json            what to load: the files below and the order of the lines
  site/data/core.<hash>.json         the B.C. Electric base data (Chilliwack line, Burnaby Lake line, context lines)
  site/data/<step>.<hash>.json       the lines each build step made, one file per step (by the step that last changed the line)
  site/tiles/<hash>/...              the basemap (water and borders), copied from basemap/tiles (see basemap/build_tiles.py); the folder
                                     is named by a hash of its index, so a rebuilt basemap gets a new folder and no stale tiles are served
  site/gtfs.zip                      copied by the Pages workflow

Routes are packed: each route is one list of integers, the first point in millionths of a degree and tenths of a metre along the line, then
the differences from the point before. The loader unpacks them to exactly the values in viz_data.json, so the map runs the same code on the
same numbers as the single-file page (fraser_valley_1949.html, still written by make_page.py for the checking tools).

File names carry a hash of their contents: a file that has not changed keeps its name and browsers keep using their copy, so after an update
a visitor downloads only the steps that changed. The manifest is small and fetched fresh each time."""
import hashlib, json, os, re, shutil
HERE = os.path.dirname(os.path.abspath(__file__)); os.chdir(HERE)
SITE, DATA = 'site', os.path.join('site', 'data')
dumps = lambda o: json.dumps(o, separators=(',', ':'), ensure_ascii=False)
h8 = lambda s: hashlib.sha1(s.encode()).hexdigest()[:10]

def pack(route):
    """[[lon, lat, d], ...] -> [lon0, lat0, d0, dlon, dlat, dd, ...] in 1e-6 degrees and decimetres"""
    out, p = [], (0, 0, 0)
    for lon, lat, d in route:
        q = (round(lon * 1e6), round(lat * 1e6), round(d * 10))
        out += [q[0] - p[0], q[1] - p[1], q[2] - p[2]]; p = q
    return out

def check_pack(route, packed):
    """unpacking must give back the same numbers (to the precision they are written in)"""
    a = b = c = 0
    for i, (lon, lat, d) in enumerate(route):
        a += packed[3 * i]; b += packed[3 * i + 1]; c += packed[3 * i + 2]
        if abs(a / 1e6 - lon) > 6e-7 or abs(b / 1e6 - lat) > 6e-7 or abs(c / 10 - d) > 0.06: raise SystemExit(f'pack error at point {i}: {lon, lat, d}')

def packed_line(L):
    L = dict(L)
    if 'route' in L:
        p = pack(L['route']); check_pack(L['route'], p); L['route'] = {'p': p}
    return L

def owners():
    """line key -> the step that last set it (replaying the parts in build order)"""
    steps = json.load(open('steps.json'))['steps']; own = {}
    for s in steps:
        f = os.path.join('parts', s['name'] + '.json')
        if not os.path.exists(f): continue
        part = json.load(open(f))
        for k in list(part.get('lines_set', {})) + part.get('append', []): own[k] = s['name']
    return own

def water():
    _cut = 'water_bc_cut.json'
    w = json.load(open(_cut if os.path.exists(_cut) else 'water_embedded.json'))
    for f in (['water_wa.json', 'water_ak.json', 'water_fill.json', 'water_north.json', 'water_sk.json', 'water_east.json'] if os.path.exists(_cut) else []) + ['water_alberta.json']:
        if os.path.exists(f): w += json.load(open(f))
    return w

def write(name, obj):
    s = dumps(obj); fn = f'{name}.{h8(s)}.json'
    open(os.path.join(DATA, fn), 'w').write(s)
    return {'name': name, 'file': fn, 'bytes': len(s.encode())}

def main():
    viz = json.load(open('viz_data.json'))
    if os.path.isdir(SITE):
        for f in os.listdir(SITE):                                    # old hashed files go; the single-file index.html is replaced below
            p = os.path.join(SITE, f)
            if f in ('data', 'tiles'): shutil.rmtree(p)
            elif re.match(r'app\.\w+\.js$', f) or f == 'index.html': os.remove(p)
    os.makedirs(DATA, exist_ok=True)
    own = owners(); lines = viz.get('lines', [])
    core = {k: v for k, v in viz.items() if k != 'lines'}
    if 'route' in core: p = pack(core['route']); check_pack(core['route'], p); core['route'] = {'p': p}
    if 'bl' in core and 'route' in core['bl']: core['bl'] = packed_line(core['bl'])
    files = [write('core', core)]
    groups = {}
    for L in lines: groups.setdefault(own.get(L['key'], 'other'), []).append(packed_line(L))
    for g, ls in groups.items(): files.append(write(g, {'lines': ls}))
    tiles_dir = os.path.join(os.path.dirname(HERE), 'basemap', 'tiles')
    tiles = None
    if os.path.exists(os.path.join(tiles_dir, 'index.json')):          # the tiled basemap; without it the page falls back to the water file
        idx = open(os.path.join(tiles_dir, 'index.json')).read(); tiles = 'tiles/' + h8(idx) + '/'
        shutil.copytree(tiles_dir, os.path.join(SITE, tiles))
    else:
        files.append(write('water', water()))
    tp = open('page_template.html').read()
    m = re.search(r'<script>\nconst DATA = __DATA__;\nconst WATER = __WATER__;[^\n]*\n(.*?)</script>', tp, re.S)
    if not m: raise SystemExit('make_site: the template script block was not found')
    app = 'const DATA = window.__DATA, WATER = window.__WATER;\n' + m.group(1)
    app_fn = f'app.{h8(app)}.js'; open(os.path.join(SITE, app_fn), 'w').write(app)
    manifest = {'files': files, 'order': [L['key'] for L in lines], 'app': app_fn, 'tiles': tiles}
    open(os.path.join(DATA, 'manifest.json'), 'w').write(dumps(manifest))
    loader = open('site_loader.js').read()
    page = tp[:m.start()] + '<script>\n' + loader + '</script>' + tp[m.end():]
    page = ('<!doctype html>\n<html lang="en">\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            '<meta name="description" content="Passenger trains and steamships of the summer of 1948, running to their timetables.">\n' + page)
    open(os.path.join(SITE, 'index.html'), 'w').write(page)
    tot = sum(f['bytes'] for f in files)
    print(f'site: page {len(page)} bytes, app {len(app)} bytes, data {tot} bytes in {len(files)} files')

if __name__ == '__main__': main()
