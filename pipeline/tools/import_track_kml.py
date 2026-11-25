"""Read back a track KML that Brendan corrected by hand (the round trip of tools/export_track_kml.py; 24 Nov 2026).
Usage: python3 tools/import_track_kml.py SENT.kml RETURNED.kml [--write PREFIX]
Compares the two files and lists: pieces deleted, redrawn (same name, new coordinates), new paths, station pins moved (with distances). With --write, writes
traces/<PREFIX>_pieces.json (every piece as returned, by id, with the lines it serves) and traces/<PREFIX>_points.json (moved pins: gid -> [lon, lat]) for the line's step to use."""
import json, math, os, sys
import xml.etree.ElementTree as ET
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
K = '{http://www.opengis.net/kml/2.2}'
def read(fn):
    pcs, pins = {}, {}
    for p in ET.parse(fn).getroot().iter(K + 'Placemark'):
        nm = (p.find(K + 'name').text or '').strip(); d = p.find(K + 'description'); desc = (d.text or '') if d is not None else ''
        ls = p.find('.//' + K + 'LineString'); pt = p.find('.//' + K + 'Point')
        if ls is not None:
            pcs[nm] = dict(coords=[[float(v) for v in c.split(',')[:2]] for c in ls.find(K + 'coordinates').text.split()], desc=desc)
        elif pt is not None:
            pins[nm] = dict(xy=[float(v) for v in pt.find(K + 'coordinates').text.split(',')[:2]], desc=desc)
    return pcs, pins
def m(a, b): return math.hypot((a[0] - b[0]) * 111320 * math.cos(math.radians(a[1])), (a[1] - b[1]) * 110570)
def length(c): return sum(m(a, b) for a, b in zip(c, c[1:]))
sent, back = read(sys.argv[1]), read(sys.argv[2])
out = dict(deleted=[], redrawn=[], new=[], moved={})
for nm, pc in sent[0].items():
    if nm not in back[0]: out['deleted'].append(nm); print('DELETED  ', nm); continue
    a, b = pc['coords'], back[0][nm]['coords']
    if len(a) != len(b) or max(m(p, q) for p, q in zip(a, b)) > 1:
        out['redrawn'].append(nm); print(f"REDRAWN  {nm}: {length(a) / 1609.34:.2f} -> {length(b) / 1609.34:.2f} mi, {len(a)} -> {len(b)} points")
for nm in back[0]:
    if nm not in sent[0]: out['new'].append(nm); print(f"NEW PATH {nm}: {length(back[0][nm]['coords']) / 1609.34:.2f} mi")
for nm, pn in sent[1].items():
    if nm in back[1]:
        d = m(pn['xy'], back[1][nm]['xy'])
        if d > 1: out['moved'][nm.split(' | ')[0]] = back[1][nm]['xy']; print(f"MOVED    {nm}: {d:.0f} m")
    else: print('PIN DELETED', nm)
for nm, pc in back[0].items():
    if nm in sent[0] and pc['desc'] != sent[0][nm]['desc']: print('NOTE     ', nm, ':', pc['desc'][:200])
if '--write' in sys.argv:
    pre = sys.argv[sys.argv.index('--write') + 1]
    pieces = {nm.split(' | ')[0]: dict(name=nm, coords=pc['coords'], lines=[x.strip() for x in pc['desc'].split('Lines:')[1].split('.')[0].split(',')] if 'Lines:' in pc['desc'] else [])
              for nm, pc in back[0].items()}
    json.dump(dict(source=f'Brendan\'s hand corrections ({os.path.basename(sys.argv[2])})', pieces=pieces), open(os.path.join(HERE, 'traces', pre + '_pieces.json'), 'w'))
    json.dump(dict(source=f'Brendan\'s hand corrections ({os.path.basename(sys.argv[2])})', points=out['moved']), open(os.path.join(HERE, 'traces', pre + '_points.json'), 'w'))
    print('written', pre + '_pieces.json', pre + '_points.json')
