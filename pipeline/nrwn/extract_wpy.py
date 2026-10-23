"""Pull the White Pass & Yukon track (B.C. portion) out of the national KML -> wpy.json."""
import json, xml.etree.ElementTree as ET
NS = '{http://www.opengis.net/kml/2.2}'
out = []
for ev, el in ET.iterparse('doc.kml'):
    if el.tag != NS + 'Placemark': continue
    sd = el.find(f'.//{NS}SchemaData'); coords = []
    for c in el.iter(NS + 'coordinates'):
        pts = [tuple(map(float, t.split(',')[:2])) for t in c.text.split()]
        if pts: coords.append(pts)
    if sd is not None and coords and any(-136.5 <= x <= -133.5 and 59.0 <= y <= 61.0 for c in coords for x, y in c):
        out.append(dict(schema=sd.get('schemaUrl'), data={s.get('name'): s.text for s in sd.findall(NS + 'SimpleData')}, coords=coords))
    el.clear()
json.dump(out, open('wpy.json', 'w')); print(len(out))
