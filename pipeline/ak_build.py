"""The Alaska Railroad, 1948 (Brendan, October 2026): Seward - Anchorage (with the boat special for the Alaska Steamship arrival), Whittier -
Portage - Anchorage, Anchorage - Curry - Fairbanks, and the Sutton branch, from ak_arr_*.csv (Official Guide; printed in 150th meridian time,
shown in Pacific time, two hours later). Track: NTAD North American Rail Network, Alaska (traces/alaska/ntad_alaska.geojson: Alaska Railroad
main lines and branches) and Brendan's Palmer - Sutton trace (traces/alaska/sutton_branch.geojson). Stations: the NTAD yards for Seward,
Portage, Whittier, Anchorage, Healy, Nenana and Fairbanks; Palmer at the end of the Palmer branch; Sutton at the end of Brendan's trace;
the rest by printed mileage. Machinery: ab_lines.py."""
import json, os
import ab_lines
from ab_lines import build, trace, report
HERE = os.path.dirname(os.path.abspath(__file__))
ab_lines.RAILS['arr'] = dict(kind='k', label='Alaska Railroad', own='arr', agency='ARR', color='26706A', pfx='ARR')

def _feed(add):
    g = json.load(open(os.path.join(HERE, 'traces', 'alaska', 'ntad_alaska.geojson')))
    for f in g['features']:
        p = f['properties']
        if p.get('RROWNER1') != 'ARR' or p.get('NET') not in ('M', 'I'): continue      # main lines and branches (not yards, sidings or the rail barge)
        geo = f['geometry']
        for line in (geo['coordinates'] if geo['type'] == 'MultiLineString' else [geo['coordinates']]):
            if len(line) > 1: add(ab_lines._xy(line), 1.0, 't', 'arr')
    s = json.load(open(os.path.join(HERE, 'traces', 'alaska', 'sutton_branch.geojson')))
    for f in s['features']: add(ab_lines._xy(f['geometry']['coordinates']), 1.0, 't', 'arr')
ab_lines.EXT_GRAPH['ak'] = lambda: ab_lines.make_graph(_feed, tie_end=150)
# stations with a position (lon, lat): the NTAD yards (centre of the yard tracks), the ends of the Palmer branch and of the Sutton trace
PLACE = {'Seward': (-149.42652, 60.13), 'Portage': (-148.980979, 60.838859),   # Portage: the junction of the Whittier branch (the yard is a spur)
         'Whittier': (-148.681, 60.77597), 'Anchorage': (-149.86863, 61.22647),
         'Healy': (-148.97337, 63.86458), 'Nenana': (-149.10219, 64.56075), 'Fairbanks': (-147.77867, 64.8509),
         'Palmer': (-149.114490, 61.598618), 'Sutton': (-148.876375, 61.709566)}
def _place(name):
    if name in PLACE: return (*PLACE[name], 'hand', 1500)
    return None                                                                 # by its printed mileage
ab_lines.EXT_PLACE['arr'] = _place
TZ = ' Shown in Pacific time, two hours later than the Alaska (150th meridian) time printed.'
SRC = 'Alaska Railroad, Official Guide, 1948'
def L(key, legs, dirs, long, src, names, **kw):
    legs = [dict(csv=l) if isinstance(l, str) else dict(csv=l[0], a=l[1], b=l[2]) for l in legs]
    return dict(key=key, rail='arr', graph='ak', legs=legs, dirs=dirs, short=src, long=long, src=src + ' (' + SRC + ')', cols=None,
                shift=7200, tznote=TZ, ends=False, names=names, **kw)
SPECS = [
 L('arr_sew', ['ak_arr_seward.csv'], ['to Anchorage', 'to Seward'], 'Seward – Portage – Anchorage', 'March 1948 schedule',
   {'No1': 'Seward train', 'No2': 'Seward train', 'SP': 'Boat train'}),
 L('arr_whi', ['ak_arr_whittier.csv'], ['to Anchorage', 'to Whittier'], 'Whittier – Portage – Anchorage', 'March 1948 schedule',
   {'WA': 'Whittier train', 'AW': 'Whittier train'}),
 L('arr_fai', ['ak_arr_fairbanks.csv'], ['to Fairbanks', 'to Anchorage'], 'Anchorage – Curry – McKinley Park – Nenana – Fairbanks', 'March 1948 schedule',
   {'N': 'Fairbanks train', 'S': 'Fairbanks train'}),
 L('arr_sut', ['ak_arr_sutton.csv'], ['to Sutton', 'to Anchorage'], 'Anchorage – Matanuska – Palmer – Sutton', 'Sutton Branch, December 1947',
   {'Out': 'Sutton train', 'Back': 'Sutton train'}),
]
if __name__ == '__main__':
    if os.environ.get('AK_DRY'):
        for s in SPECS:
            if os.environ['AK_DRY'] in ('1', s['key']):
                try: rows, trains, pieces = trace(s); report(s, rows, pieces)
                except SystemExit as e: print(' ', e)
    else:
        build(SPECS)
        import csv
        GT = os.path.join(HERE, 'gtfs'); have = {r[0] for r in csv.reader(open(os.path.join(GT, 'agency.txt')))}
        if 'ARR' not in have:
            with open(os.path.join(GT, 'agency.txt'), 'a', newline='') as fh:
                csv.writer(fh).writerow(['ARR', 'The Alaska Railroad', 'https://en.wikipedia.org/wiki/Alaska_Railroad', 'America/Vancouver', 'en', ''])
