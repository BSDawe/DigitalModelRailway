"""Track for the Esquimalt & Nanaimo (Victoria-Courtenay, Parksville-Port Alberni) and the PGE (Squamish-Quesnel),
from the NRWN extracts nrwn/island.json and nrwn/pge.json. Writes island_pge_routes.pkl."""
import json, os, pickle
from shapely.geometry import LineString
from nrwn_graph import Net, fwd, inv, MI
HERE = os.path.dirname(os.path.abspath(__file__))

isl = Net(json.load(open(os.path.join(HERE, 'nrwn', 'island.json'))), subs={'Victoria', 'Port Alberni'})
VIC_TRACK_END = (-123.3744, 48.4279)          # NRWN track ends at Vic West; the 1949 line crossed the Johnson St bridge
VIC_STATION = (-123.3697, 48.4288)            # E&N Victoria station, Store St at the foot of Johnson St
COURTENAY = (-125.0038, 49.6844)
EN, s1 = isl.route(VIC_TRACK_END, (-123.9447, 49.1640), COURTENAY)    # via Nanaimo
EN = LineString([fwd(*VIC_STATION)] + list(EN.coords))
# the Port Alberni sub leaves the Victoria sub at Parksville: start from its node nearest the main line
from shapely.geometry import Point
pa_nodes = [n for n in isl.G.nodes if any(isl.G[n][m].get('sub') == 'Port Alberni' and isl.G[n][m].get('cls') == 'Main' for m in isl.G[n])]
PJ = min(pa_nodes, key=lambda n: EN.distance(Point(n)))
PORT_ALBERNI = (-124.8120, 49.2340)
PA, s2 = isl.route(inv(*PJ), (-124.8050, 49.2580), PORT_ALBERNI)    # via Alberni
print('  Port Alberni sub junction', inv(*PJ), f'{EN.distance(Point(PJ)):.0f} m from the main line, at E&N mile {EN.project(Point(PJ))/MI:.1f} (Parksville 95.2)')
print(f'E&N Victoria-Courtenay {EN.length/MI:.1f} mi (timetable 139.7), snaps {[round(x) for x in s1]}')
print(f'E&N Parksville-Port Alberni {PA.length/MI:.1f} mi (timetable 38.8), snaps {[round(x) for x in s2]}')

pge = Net(json.load(open(os.path.join(HERE, 'nrwn', 'pge.json'))), subs={'Squamish', 'Lillooet', 'Prince George'})
SQUAMISH_DOCK = (-123.155131, 49.694717)      # Squamish (Government Dock), Brendan 8 October 2026 (his first pin, 270 m up the spur, was too far north); steamer connection to Vancouver
SQUAMISH = (-123.15798, 49.7188427)           # NRWN station, Squamish sub 40.4
QUESNEL = (-122.4883538, 52.9844483)          # NRWN station, Prince George sub 384.8
PG, s3 = pge.route(SQUAMISH_DOCK, SQUAMISH, (-121.9358, 50.6847), (-122.1311, 52.1194), QUESNEL, start_any=True)   # via Lillooet, Williams Lake
PG = LineString([fwd(*SQUAMISH_DOCK)] + list(PG.coords))
print('  PGE from the dock: first km', [tuple(round(v, 5) for v in inv(*PG.interpolate(d).coords[0])) for d in (0, 300, 600, 900, 1200, 1609)])
print(f'PGE Squamish-Quesnel {PG.length/MI:.1f} mi (timetable 347.0 from Squamish Dock), snaps {[round(x) for x in s3]}')
pickle.dump(dict(EN=EN, PA=PA, PG=PG), open(os.path.join(HERE, 'island_pge_routes.pkl'), 'wb'))
