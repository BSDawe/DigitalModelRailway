#!/usr/bin/env python3
"""Parse a KMZ/KML into the list format of traces/ontario/lakehead_all.json:
  [{"path": [file, folder, subfolder, ...], "name": ..., "kind": "Point" | "LineString" | "Polygon", "coords": [[lon, lat], ...], "desc": ...}]
A MultiGeometry gives one entry per part. Descriptions are kept (they carry build and abandonment notes in Paul Delamere's collections).

  python3 tools/parse_kmz.py <file.kmz|file.kml> <out.json>
"""
import json, os, re, sys, zipfile
import xml.etree.ElementTree as ET

def local(tag): return tag.rsplit('}', 1)[-1]

def coords(text):
    out = []
    for tok in (text or '').split():
        p = tok.split(',')
        if len(p) >= 2:
            try: out.append([round(float(p[0]), 7), round(float(p[1]), 7)])
            except ValueError: pass
    return out

def walk(el, path, out):
    for ch in el:
        t = local(ch.tag)
        if t in ('Document', 'Folder'):
            nm = next((c.text for c in ch if local(c.tag) == 'name'), None) or ''
            walk(ch, path + [nm.strip()] if t == 'Folder' or not path else path, out)
        elif t == 'Placemark':
            name = desc = ''
            for c in ch:
                if local(c.tag) == 'name': name = (c.text or '').strip()
                elif local(c.tag) == 'description': desc = re.sub(r'<[^>]+>', ' ', c.text or '').strip()
            for g in ch.iter():
                k = local(g.tag)
                if k in ('Point', 'LineString', 'LinearRing'):
                    cs = next((coords(c.text) for c in g if local(c.tag) == 'coordinates'), [])
                    if cs: out.append({'path': path, 'name': name, 'kind': 'Polygon' if k == 'LinearRing' else k, 'coords': cs, 'desc': desc})

def main(src, dst):
    if src.lower().endswith('.kmz'):
        z = zipfile.ZipFile(src); kml = next(n for n in z.namelist() if n.lower().endswith('.kml')); data = z.read(kml)
    else: data = open(src, 'rb').read()
    root = ET.fromstring(data); out = []
    walk(root, [os.path.basename(src)], out)
    json.dump(out, open(dst, 'w'), separators=(',', ':'))
    kinds = {}
    for o in out: kinds[o['kind']] = kinds.get(o['kind'], 0) + 1
    print(f'{dst}: {len(out)} pieces {kinds}')

if __name__ == '__main__': main(*sys.argv[1:3])
