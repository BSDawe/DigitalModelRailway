"""Pull the Alberta track needed for the extensions out of the Alberta file of the national network -> alberta.json.
Usage: python3 nrwn/extract_alberta.py <path to the unzipped Alberta .kml>. Corridors: CP Calgary - Banff - the Great Divide; CP Lethbridge -
Macleod - Crowsnest; CN Edmonton - Edson - Jasper - Yellowhead; the Northern Alberta Railways country north-west of Edmonton. Schema names are normalised to the B.C. file's ('#kml_schema_ft_Track')."""
import json, sys, os, xml.etree.ElementTree as ET
NS = '{http://www.opengis.net/kml/2.2}'
BOX = [(-116.45, -113.85, 50.85, 51.65), (-114.80, -112.70, 49.40, 49.95), (-118.55, -113.20, 52.75, 53.80),
       (-120.10, -113.30, 53.50, 56.10)]          # the last: the Northern Alberta Railways, Edmonton to the Peace River country
out = []
for ev, el in ET.iterparse(sys.argv[1]):
    if el.tag != NS + 'Placemark': continue
    sd = el.find(f'.//{NS}SchemaData'); coords = []
    for c in el.iter(NS + 'coordinates'):
        pts = [tuple(map(float, t.split(',')[:2])) for t in c.text.split()]
        if pts: coords.append([[round(x, 6), round(y, 6)] for x, y in pts])
    if sd is not None and coords:
        kind = sd.get('schemaUrl').replace('#kml_schema_ft_', '').replace('#', '').split('_')[0]
        cls = next((s.text for s in sd.findall(NS + 'SimpleData') if s.get('name') == 'trackClassification'), '') if kind == 'Track' else ''
        north = any(BOX[3][0] <= x <= BOX[3][1] and BOX[3][2] <= y <= BOX[3][3] and y > 53.85 for cc in coords for x, y in cc)
        # yards and spurs are left out, except spurs in the Peace River country, where what is left of the old N.A.R. main line is now classed as a spur
        if cls == 'Yard' or (cls == 'Spur' and not north): el.clear(); continue
        if kind in ('Track', 'Station', 'MarkerPost') and any(a <= x <= b and c <= y <= d for cc in coords for x, y in cc for a, b, c, d in BOX):
            data = {s.get('name'): s.text for s in sd.findall(NS + 'SimpleData') if s.text not in (None, 'None', '-1', 'Unknown')}
            out.append(dict(schema='#kml_schema_ft_' + kind, data=data, coords=coords))
    el.clear()
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'alberta.json'), 'w'), separators=(',', ':'))
print(len(out), 'features')
