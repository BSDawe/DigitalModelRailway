"""Cumberland Railway & Coal Co. (Brendan, 11 Nov 2026: the Wikipedia map's Spring Hill & Parrsborough Railway GeoJSON). Parrsboro - Springhill - the
Intercolonial west of Springhill Junction. Usage: python3 tools/mar_import_crc.py <geojson> -> traces/maritimes/crc.geojson (own crc; drawn in the Sydney &
Louisburg livery: the same parent, Dominion Steel & Coal)."""
import json, os, sys
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
f = json.load(open(sys.argv[1]))['features'][0]
out = [dict(type='Feature', properties=dict(own='crc', name='Cumberland Railway & Coal: Parrsboro - Springhill - Springhill Junction', constituent='Spring Hill and Parrsborough Railway',
            branch='main', group='wiki', status='ok', cost=1.0, note='Wikipedia map data (Spring Hill & Parrsborough Railway.map), from Brendan, 11 Nov 2026'),
            geometry=dict(type='LineString', coordinates=f['geometry']['coordinates']))]
json.dump(dict(type='FeatureCollection', features=out), open(os.path.join(HERE, 'traces', 'maritimes', 'crc.geojson'), 'w'))
from pyproj import Geod; G = Geod(ellps='WGS84'); c = f['geometry']['coordinates']
print(round(sum(G.inv(*a, *b)[2] for a, b in zip(c, c[1:])) / 1609.34, 1), 'mi')
