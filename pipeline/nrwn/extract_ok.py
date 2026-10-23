"""Pull NRWN features inside a bounding box out of the national KML (doc.kml, 157 MB).
region.json : Lower Mainland + Fraser Canyon to Spence's Bridge (lat to 50.55)
island.json : Vancouver Island to Courtenay and Port Alberni (E&N)
pge.json    : Squamish to Quesnel (PGE)"""
import json, xml.etree.ElementTree as ET
NS = '{http://www.opengis.net/kml/2.2}'
BOX = dict(okanagan=(-121.5, 49.8, -119.0, 50.85))
out = {k: [] for k in BOX}
for ev, el in ET.iterparse('doc.kml'):
    if el.tag != NS + 'Placemark': continue
    sd = el.find(f'.//{NS}SchemaData')
    coords = []
    for c in el.iter(NS + 'coordinates'):
        pts = [tuple(map(float, t.split(',')[:2])) for t in c.text.split()]
        if pts: coords.append(pts)
    if sd is not None and coords:
        data = {s.get('name'): s.text for s in sd.findall(NS + 'SimpleData')}
        for k, (x0, y0, x1, y1) in BOX.items():
            if any(x0 <= x <= x1 and y0 <= y <= y1 for c in coords for x, y in c):
                out[k].append(dict(schema=sd.get('schemaUrl'), data=data, coords=coords))
    el.clear()
for k, v in out.items():
    json.dump(v, open(f'{k}.json', 'w')); print(k, len(v))
