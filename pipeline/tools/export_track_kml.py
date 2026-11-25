"""Export drawn lines as a KML for Brendan to correct by hand in Google Earth, and read it back later (round trip; Brendan, 23 - 24 Nov 2026).
Usage: python3 tools/export_track_kml.py OUT.kml KEY [KEY ...]      (line keys or prefixes from viz_data.json, e.g. ptc_)
Each line's route is cut at its principal stations into pieces named "<ID> | <from> - <to>" (stable ids: line key + piece number); a stretch already exported for an earlier
line (the same points: shared track) is written once and its pieces list the lines using it. Stations are pins named "<gid> | <name>". Items placed by estimate (notes saying
approximate / estimated) are red. Edits that can be read back: delete a piece, redraw a piece (keep its name), draw a new path (any name), drag a pin."""
import json, os, sys, html
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
out, keys = sys.argv[1], sys.argv[2:]
vd = json.load(open(os.path.join(HERE, 'viz_data.json')))
lines = [L for L in vd['lines'] if any(L['key'] == k or L['key'].startswith(k) for k in keys)]
assert lines, keys
def esc(x): return html.escape(str(x), quote=False)
def coords(pts): return ' '.join(f'{p[0]:.7f},{p[1]:.7f},0' for p in pts)
seen = {}     # rounded segment -> piece id (shared track)
pieces, pins = [], {}
for L in lines:
    st = sorted(L['stations'], key=lambda s: s['chain'])
    cuts = [s for s in st if s.get('principal')] or [st[0], st[-1]]
    if cuts[0] is not st[0]: cuts.insert(0, st[0])
    if cuts[-1] is not st[-1]: cuts.append(st[-1])
    r = L['route']
    for n, (a, b) in enumerate(zip(cuts, cuts[1:]), 1):
        pts = [p for p in r if a['chain'] - 0.5 <= p[2] <= b['chain'] + 0.5]
        pts = [[a['lon'], a['lat']]] + [p[:2] for p in pts] + [[b['lon'], b['lat']]]
        sig = (a['gid'], b['gid'])                  # the same two stations: shared track, written once
        if sig in seen: seen[sig]['used'].append(L['key']); continue
        pc = dict(id=f"{L['key']}-{n:02d}", name=f"{a['name']} - {b['name']}", pts=pts, used=[L['key']], src=L.get('src', ''),
                  miles=round((b['chain'] - a['chain']) / 1609.34, 2), printed=round((b.get('mile') or 0) - (a.get('mile') or 0), 2),
                  est=any(s.get('gid', '').endswith(('GRESHAM',)) for s in (a, b)))
        seen[sig] = pc; pieces.append(pc)
    for s in st:
        if s['gid'] not in pins: pins[s['gid']] = s
STY = '''<Style id="track"><LineStyle><color>ff2f6f8f</color><width>4</width></LineStyle></Style>
<Style id="track_est"><LineStyle><color>ff0000ff</color><width>4</width></LineStyle></Style>
<Style id="stn"><IconStyle><scale>0.8</scale><Icon><href>http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png</href></Icon></IconStyle></Style>
<Style id="stn_est"><IconStyle><color>ff0000ff</color><scale>0.9</scale><Icon><href>http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png</href></Icon></IconStyle></Style>'''
k = ['<?xml version="1.0" encoding="UTF-8"?>', '<kml xmlns="http://www.opengis.net/kml/2.2"><Document>', f'<name>{esc(os.path.basename(out))}</name>',
     '<description>Digital Model Railway track for hand correction. Delete a piece that is wrong, redraw a piece (keep its name), draw any missing track as a new path, '
     'drag station pins to the right spot, and note anything in a description. Red = placed by estimate.</description>', STY, '<Folder><name>Track</name>']
for pc in pieces:
    d = (f"Lines: {', '.join(pc['used'])}. Traced {pc['miles']} mi" + (f", printed {pc['printed']} mi" if pc['printed'] else '') + f". Source: {pc['src']}")
    k.append(f"<Placemark><name>{esc(pc['id'] + ' | ' + pc['name'])}</name><description>{esc(d)}</description>"
             f"<styleUrl>#{'track_est' if pc['est'] else 'track'}</styleUrl><LineString><tessellate>1</tessellate><coordinates>{coords(pc['pts'])}</coordinates></LineString></Placemark>")
k.append('</Folder><Folder><name>Stations</name>')
for g, s in pins.items():
    est = any(w in (s.get('note') or '').lower() for w in ('approximate', 'estimate', 'half-way'))
    k.append(f"<Placemark><name>{esc(g + ' | ' + s['name'])}</name><description>{esc(s.get('note') or '')}" + (f" (printed mile {s['mile']})" if s.get('mile') is not None else '') +
             f"</description><styleUrl>#{'stn_est' if est else 'stn'}</styleUrl><Point><coordinates>{s['lon']:.7f},{s['lat']:.7f},0</coordinates></Point></Placemark>")
k.append('</Folder></Document></kml>')
open(out, 'w').write('\n'.join(k))
print(f'{out}: {len(pieces)} track pieces, {len(pins)} stations from {len(lines)} lines')
