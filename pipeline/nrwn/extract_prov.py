"""All the track, stations and mileposts in a provincial file of the national network (yards left out) -> <prov>_all.json, for the
Saskatchewan and Manitoba lines (as extract_alberta_all.py). Usage: python3 nrwn/extract_prov.py <unzipped .kml> <prov> [yards]
(with 'yards': only the yard track -> <prov>_yards.json, a last-resort connector set; Brendan 17 Oct 2026)"""
import json, sys, os, xml.etree.ElementTree as ET
YARDS = len(sys.argv) > 3 and sys.argv[3] == 'yards'
NS = '{http://www.opengis.net/kml/2.2}'
out = []
for ev, el in ET.iterparse(sys.argv[1]):
    if el.tag != NS + 'Placemark': continue
    sd = el.find(f'.//{NS}SchemaData'); coords = []
    for c in el.iter(NS + 'coordinates'):
        pts = [tuple(map(float, t.split(',')[:2])) for t in c.text.split()]
        if pts: coords.append([[round(x, 6), round(y, 6)] for x, y in pts])
    if sd is not None and coords:
        kind = sd.get('schemaUrl').replace('#kml_schema_ft_', '').replace('#', '').split('_')[0]
        if kind in ('Track', 'Station', 'MarkerPost'):
            data = {s.get('name'): s.text for s in sd.findall(NS + 'SimpleData') if s.text not in (None, 'None', '-1', 'Unknown')}
            if (kind == 'Track' and data.get('trackClassification') == 'Yard') != YARDS: el.clear(); continue
            out.append(dict(schema='#kml_schema_ft_' + kind, data=data, coords=coords))
    el.clear()
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), sys.argv[2] + ('_yards.json' if YARDS else '_all.json')), 'w'), separators=(',', ':'))
print(len(out), 'features')
