"""The dashed (straight-estimate) stretches of the map as a KML, for tracing over: python3 tools/dashed_kml.py -> dashed_estimates.kml
One line for each run of estimated track, named by its table and end stations, and in a second folder the stations along those runs."""
import json, os
from xml.sax.saxutils import escape
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
vd = json.load(open(os.path.join(HERE, 'viz_data.json'))); MI = 1609.344
lines, stns, seen = [], [], set()
for L in vd['lines']:
    est = sorted((s for s in L.get('segments', []) if s.get('est')), key=lambda s: s['a']); runs = []
    for s in est:
        if runs and abs(runs[-1][1] - s['a']) < 2: runs[-1][1] = s['b']
        else: runs.append([s['a'], s['b']])
    for a, b in runs:
        pts = [p for p in L['route'] if a - 1 <= p[2] <= b + 1]; st = [s for s in L['stations'] if a - 1 <= s['chain'] <= b + 1]
        if len(pts) < 2: continue
        ends = f"{st[0]['name']} – {st[-1]['name']}" if len(st) > 1 else (st[0]['name'] if st else '')
        lines.append((f"{L['src'].split(',')[0].replace(' Table', ', Table')}: {ends} ({(b - a) / MI:.0f} mi)", L['owner'], pts))
        for s in st:
            if (s['gid'], round(s['lon'], 4)) not in seen: seen.add((s['gid'], round(s['lon'], 4))); stns.append((s['name'], L['label'], s['mile'], s['lon'], s['lat']))
col = {'cn': 'ff446b2f', 'cp': 'ff2c1e7a', 'nar': 'ff864f2c'}
k = ['<?xml version="1.0" encoding="UTF-8"?>', '<kml xmlns="http://www.opengis.net/kml/2.2"><Document><name>Dashed lines: straight estimates on the railway map</name>']
for o, c in col.items(): k.append(f'<Style id="{o}"><LineStyle><color>{c}</color><width>3</width></LineStyle></Style>')
k.append('<Folder><name>Estimated track (straight from station to station)</name>')
for name, o, pts in lines:
    k.append(f'<Placemark><name>{escape(name)}</name><styleUrl>#{o}</styleUrl><LineString><tessellate>1</tessellate><coordinates>' + ' '.join(f'{p[0]},{p[1]},0' for p in pts) + '</coordinates></LineString></Placemark>')
k.append('</Folder><Folder><name>Stations on those stretches</name>')
for name, rr, mile, lon, lat in stns:
    k.append(f'<Placemark><name>{escape(name)}</name><description>{escape(rr)}, mile {mile}</description><Point><coordinates>{lon},{lat},0</coordinates></Point></Placemark>')
k.append('</Folder></Document></kml>')
open(os.path.join(HERE, 'dashed_estimates.kml'), 'w').write('\n'.join(k))
print(len(lines), 'lines,', len(stns), 'stations,', round(sum((p[-1][2] - p[0][2]) for _, _, p in lines) / MI), 'miles')
for name, _, _ in lines: print('  ', name)
