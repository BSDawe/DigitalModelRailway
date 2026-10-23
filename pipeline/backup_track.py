"""Backup track for routes the national network no longer contains (Brendan, 4 October 2026). NATIONAL NETWORK ROUTINGS ARE PREFERRED: use these
only for track the network does not have, joined on to the network at each end. A helper, not a build step: import it from a step that needs it.

  cnor  traces/cnor_all.geojson   the Canadian Northern Railway system: 144 lines, about 15,900 km, coast to coast
  gtp   traces/gtp_all.geojson    the Grand Trunk Pacific: 13 lines, about 4,700 km (the main line Winnipeg - Edmonton - Prince Rupert and branches)
Each line has the company ('title') and sometimes a branch name ('description').

  from backup_track import lines, features
  lines('cnor', text='Kamloops Branch')         -> [(name, description, [(lon, lat), ...]), ...]   name or description contains the text
  lines('gtp', box=(-121, -113, 49, 56))        -> every line with a point in the box (lon0, lon1, lat0, lat1); the set may be None for both
  features('gtp', box=...)                      -> the same as track features for nrwn_graph.Net, to route over together with the network
  python3 backup_track.py                       -> lists the lines west of 110 degrees"""
import json, os, re
HERE = os.path.dirname(os.path.abspath(__file__))
SETS = {'cnor': 'cnor_all.geojson', 'gtp': 'gtp_all.geojson'}
def _all(which):
    for k in ([which] if which else SETS):
        for f in json.load(open(os.path.join(HERE, 'traces', SETS[k])))['features']:
            p = f['properties']; g = f['geometry']
            for c in ([g['coordinates']] if g['type'] == 'LineString' else g['coordinates']):
                yield k, re.sub(r'<[^>]+>', '', p.get('title') or ''), p.get('description') or '', [tuple(q[:2]) for q in c]
def lines(which=None, text=None, box=None):
    out = []
    for k, name, desc, pts in _all(which):
        if text and text.lower() not in (name + '|' + desc).lower(): continue
        if box and not any(box[0] <= x <= box[1] and box[2] <= y <= box[3] for x, y in pts): continue
        out.append((name, desc, pts))
    return out
def features(which=None, text=None, box=None):
    return [dict(schema='#kml_schema_ft_Track', data={'trackClassification': 'Main', 'subdivision1Name': 'backup: ' + (d or n)}, coords=[pts]) for n, d, pts in lines(which, text, box)]
if __name__ == '__main__':
    import math
    for k in SETS:
        print(k)
        for n, d, pts in lines(k, box=(-135, -110, 48, 57)):
            km = sum(math.hypot((a[0] - b[0]) * math.cos(math.radians(a[1])) * 111.32, (a[1] - b[1]) * 110.57) for a, b in zip(pts, pts[1:]))
            print(f'  {km:7.1f} km  {n} | {d} | {pts[0][0]:.2f},{pts[0][1]:.2f} -> {pts[-1][0]:.2f},{pts[-1][1]:.2f}')
