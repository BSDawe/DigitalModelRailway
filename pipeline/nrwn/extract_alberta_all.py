"""All the track in the Alberta file of the national network (yards left out) -> alberta_all.json, for the Alberta branch lines.
Usage: python3 nrwn/extract_alberta_all.py <path to the unzipped Alberta .kml>. alberta.json (the corridors of the first Alberta extensions) is left as it is,
so the steps that read it do not change. Schema names are normalised to the B.C. file's ('#kml_schema_ft_Track')."""
import json, sys, os, xml.etree.ElementTree as ET
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
            if kind == 'Track' and data.get('trackClassification') == 'Yard': el.clear(); continue
            out.append(dict(schema='#kml_schema_ft_' + kind, data=data, coords=coords))
    el.clear()
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'alberta_all.json'), 'w'), separators=(',', ':'))
print(len(out), 'features')
