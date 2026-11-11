"""Sydney & Louisburg Railway (Brendan, 11 Nov 2026: the Wikipedia map's GeoJSON, sydney_and_louisburg_railway.geojson).
Usage: python3 tools/mar_import_snl.py <geojson>  -> traces/maritimes/snl.geojson (own snl). Main line Sydney - Glace Bay - Louisburg; branches (Port Morien,
New Waterford, Broughton, Birch Grove) and the two former Dominion Coal Co. lines it acquired, kept with their descriptions. Short line (stage 3): waits for
its timetable."""
import json, os, sys
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
out = []
for f in json.load(open(sys.argv[1]))['features']:
    p = f['properties']; d = p.get('description') or ''
    acq = 'Dominion Coal' in p.get('title', '')
    name = ('Sydney & Louisburg: ' + (d if d and d != 'acquired' else 'main line Sydney - Louisburg') + (' (former Dominion Coal Co. line, acquired)' if acq else ''))
    out.append(dict(type='Feature', properties=dict(own='snl', name=name, constituent='Dominion Coal Company' if acq else 'Sydney and Louisburg Railway',
               branch=d or 'main', group='wiki', status='ok', cost=1.0, note="Wikipedia map data (Sydney and Louisburg Railway.map), from Brendan, 11 Nov 2026"),
               geometry=dict(type='LineString', coordinates=[[round(x, 7), round(y, 7)] for x, y in f['geometry']['coordinates']])))
json.dump(dict(type='FeatureCollection', features=out), open(os.path.join(HERE, 'traces', 'maritimes', 'snl.geojson'), 'w'))
print(len(out), 'pieces')
