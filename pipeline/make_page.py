"""Assemble the page: page_template.html + viz_data.json + the water layer (water_embedded.json: B.C. and Puget Sound; water_alberta.json: Alberta
lakes and rivers, if present) -> fraser_valley_1949.html and site/index.html."""
import json, os, re
HERE = os.path.dirname(os.path.abspath(__file__))
tp = open(os.path.join(HERE, 'page_template.html')).read()
# B.C. and Puget Sound (water_embedded.json), or, made by water_extra.py, the same less the US side (water_bc_cut.json) with Washington's own
# water (water_wa.json) and the Gulf of Alaska (water_ak.json); and Alberta (water_alberta.json)
_cut = os.path.join(HERE, 'water_bc_cut.json')
water = json.load(open(_cut if os.path.exists(_cut) else os.path.join(HERE, 'water_embedded.json')))
for _f in (['water_wa.json', 'water_ak.json', 'water_fill.json', 'water_north.json', 'water_sk.json', 'water_east.json'] if os.path.exists(_cut) else []) + ['water_alberta.json']:
    if os.path.exists(os.path.join(HERE, _f)): water += json.load(open(os.path.join(HERE, _f)))
water = json.dumps(water, separators=(',', ':'))
html = tp.replace('__DATA__', open(os.path.join(HERE, 'viz_data.json')).read()).replace('__WATER__', water)
os.makedirs(os.path.join(HERE, 'site'), exist_ok=True)
for out in ('fraser_valley_1949.html', os.path.join('site', 'index.html')): open(os.path.join(HERE, out), 'w').write(html)
print('page', len(html), 'bytes')
