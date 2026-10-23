"""Steamers (1948), from the tables in the Canadian Pacific folder. Lake services: Slocan Lake (Table 158), Kootenay Lake (159), Arrow Lakes
(161). Coast services, on their summer sailings: the Triangle Route and Vancouver - Victoria (168, 168A), Vancouver - Nanaimo (169), the Gulf
Islands (170), Steveston - Sidney (170A), Vancouver - Westview - Comox (171), Vancouver - Prince Rupert (174), and the Puget Sound Navigation
Co. (Black Ball) boat Seattle - Port Angeles - Victoria (168, 168B).
Each service is a 'water' line in viz_data.json: a lane over the water layer between its ports (sea.py), drawn dotted with a boat on it.
Times: 'h.mma' as printed; '~h.mma' my estimate where the table prints only a.m./p.m. or 'about'; None = by distance between the timed ports.
Estimated times show as est. Landings served only on signal are named in the notes, not drawn. Run after interim_build.py."""
import csv, json, math, os, re, zipfile
from nrwn_graph import fwd, MI
from sea import Sea, SEA_VERSION
HERE = os.path.dirname(os.path.abspath(__file__)); GT = os.path.join(HERE, 'gtfs')
vd = json.load(open(os.path.join(HERE, 'viz_data.json')))
RAIL = {s['gid']: s for l in vd['lines'] for s in l['stations'] if s.get('gid') and not l.get('water')}       # railway stations a steamer meets

def hm(txt):
    m = re.match(r'(\d+)\.(\d+)([ap])', txt); h, mn = int(m.group(1)), int(m.group(2))
    if m.group(3) == 'p' and h != 12: h += 12
    if m.group(3) == 'a' and h == 12: h = 0
    return h * 3600 + mn * 60

# ---------------- ports: name -> (railway gid, or lon, lat), principal. Positions of landings are approximate (the wharf, as near as I can place it).
P = {
 # coast
 'Vancouver': (-123.1122, 49.2893, True), 'Victoria': (-123.37117, 48.42129, True), 'Victoria (Black Ball)': (-123.36996, 48.42309, True), 'Seattle (Lenora St. Dock)': (-122.3525, 47.6130, True),
 'Seattle (Colman Dock)': (-122.3390, 47.6025, True), 'Port Angeles': (-123.4310, 48.1215, True), 'Nanaimo': (-123.9330, 49.1660, True),
 'Steveston': (-123.1830, 49.1232, True), 'Sidney': (-123.3925, 48.6495, True), 'Anacortes': (-122.614545, 48.521834, True),
 'Galiano Island': (-123.316, 48.877, False), 'Mayne Island': (-123.299, 48.851, False), 'Ganges Harbour': (-123.500, 48.853, True),
 'Hope Bay': (-123.273, 48.803, False), 'Port Washington': (-123.318, 48.813, False), 'Saturna Island': (-123.197, 48.798, False),
 'South Pender Island': (-123.232, 48.748, False), 'James Island': (-123.360, 48.603, False),
 'Westview': (-124.52946, 49.83603, True), 'Blubber Bay': (-124.6215, 49.7955, False), 'Hornby Island': (-124.705, 49.520, False),
 'Denman Island': (-124.823, 49.534, False), 'Union Bay': ('EN_UNION_BAY', False), 'Comox': (-124.9275, 49.6705, True),
 'Englewood': (-126.862, 50.538, False), 'Alert Bay': (-126.933, 50.586, False), 'Port McNeill': (-127.085, 50.592, False), 'Port Hardy': (-127.487, 50.722, False),
 'Ocean Falls': (-127.694, 52.353, True), 'Butedale': (-128.692, 53.158, False), 'Prince Rupert': ('CNN_PRINCE_RUPERT', True),
 'Vancouver (C.N. dock)': (-123.0995, 49.2868, True), 'Ketchikan': (-131.647, 55.342, True),
 # Union Steamships (positions approximate: the landing, as near as I can place it)
 'Vancouver (Union Pier)': (-123.1040, 49.2858, True), 'Squamish (Government Dock)': ('PGE_SQUAMISH_DOCK', True),
 'Bowen Island': (-123.3295, 49.3795, True), 'Cowans Point': (-123.36261, 49.33632, False), 'Anvil Island': (-123.300, 49.523, False), 'Furry Creek': (-123.228, 49.583, False),
 'Britannia': (-123.207, 49.625, True), 'Woodfibre': (-123.254, 49.667, True), 'Gibsons': (-123.505, 49.3995, True), 'Granthams Landing': (-123.492, 49.4135, False),
 'Hopkins Landing': (-123.478, 49.4290, False), 'Williamsons Landing': (-123.472, 49.4560, False), 'Port Mellon': (-123.482, 49.5220, True), 'Seaside Park': (-123.487, 49.508, False),
 'McNab Creek': (-123.385, 49.563, False), 'New Brighton': (-123.447, 49.4505, False), 'Gambier Harbour': (-123.433, 49.4405, False), 'West Bay': (-123.410, 49.465, False),
 'East Bay': (-123.383, 49.468, False), 'Keats Island': (-123.478, 49.397, False),
 'Roberts Creek': (-123.640, 49.4185, False), 'Wilson Creek': (-123.715, 49.437, False), 'Sechelt': (-123.762, 49.469, True), 'Halfmoon Bay': (-123.912, 49.507, False),
 'Buccaneer Bay': (-123.990, 49.497, False), 'Pender Harbour': (-124.060, 49.632, True), 'Stillwater': (-124.317, 49.767, False), 'Van Anda': (-124.553, 49.758, False),
 'Savary Island': (-124.775, 49.947, False), 'Lund': (-124.765, 49.980, False), 'Bliss Landing': (-124.792, 50.037, False), 'Refuge Cove': (-124.843, 50.123, False),
 'Squirrel Cove': (-124.915, 50.118, False), 'Redonda Bay': (-124.957, 50.263, False), 'Stuart Island': (-125.133, 50.372, True), 'Whaletown': (-125.052, 50.108, False),
 'Mansons Landing': (-124.983, 50.068, False), 'Homfray Creek': (-124.635, 50.283, False), 'Salmon Bay': (-124.668, 50.432, False), 'Read Island': (-125.088, 50.187, False),
 'Heriot Bay': (-125.213, 50.103, False), 'Surge Narrows': (-125.118, 50.226, False), 'Bold Point': (-125.165, 50.170, False),
 'False Bay': (-124.353, 49.493, False), 'Campbell River': (-125.243, 50.022, True), 'Quathiaski Cove': (-125.218, 50.045, False), 'Bloedel': (-125.368, 50.127, False),
 'Rock Bay': (-125.480, 50.327, False), 'Shoal Bay': (-125.365, 50.458, False), 'Blind Channel': (-125.502, 50.413, False), 'Sayward': (-125.960, 50.397, False),
 'Port Neville': (-126.090, 50.493, False), 'Minstrel Island': (-126.303, 50.613, True), 'Glendale Cove': (-125.735, 50.672, False), 'Simoom Sound': (-126.500, 50.855, False),
 'Echo Bay': (-126.497, 50.752, False), 'Sullivan Bay': (-126.828, 50.885, True), 'Telegraph Cove': (-126.832, 50.547, False), 'Sointula': (-127.018, 50.628, False),
 'Shushartie Bay': (-127.858, 50.853, False), 'Goose Bay': (-127.660, 51.375, False), 'Dawsons Landing': (-127.577, 51.573, False), 'Rivers Inlet Cannery': (-127.255, 51.680, False),
 'Namu': (-127.867, 51.862, False), 'Bella Coola': (-126.795, 52.378, True), 'Bella Bella': (-128.143, 52.160, False), 'Klemtu': (-128.522, 52.593, False),
 # S.S. Chelohsin's camps and landings (Route 5), located by Brendan
 'Granite Bay': (-125.31083, 50.24028, False), 'Elk Bay': (-125.43861, 50.27750, False), 'Phillips Arm': (-125.35677, 50.54316, False), 'Loughborough Inlet': (-125.53720, 50.58353, False),
 'Fraser Bay': (-125.47316, 50.71352, False), 'Jackson Bay': (-125.75139, 50.51639, False), 'Bones Bay': (-126.35222, 50.58389, False), 'Thompson Sound': (-126.01328, 50.79573, False),
 'Kingcome Inlet': (-126.21897, 50.92973, False), 'Allison Harbour': (-127.51321, 51.04826, False),
 'Port Simpson': (-130.433, 54.562, False), 'Alice Arm': (-129.478, 55.470, False), 'Kincolith': (-129.982, 54.997, False), 'Stewart': (-129.993, 55.917, True),
 # Gulf Islands Ferry Co. (positions from the federal names file) and the North Vancouver ferries (Brendan's points)
 'Fulford Harbour': (-123.4500, 48.7667, True), 'Swartz Bay': (-123.4167, 48.6833, True),
 'North Vancouver': (-123.08073, 49.30992, True), 'Vancouver (NV Ferries)': (-123.10179, 49.28595, True),
 # Harbour Navigation Co., Indian Arm (Brendan, 10 October 2026): his points for Gore Ave. Dock, Belcarra Park, Camp Jubilee, Lake Buntzen and
 # Weldwood (a guess); the rest from the B.C. names file (to the nearest minute)
 # (revised 10 October, built 15 October: every landing on Brendan's points, Cosy Cove and Granite Falls added)
 'Vancouver (Gore Ave. Dock)': (-123.098232, 49.286388, True), 'Belcarra Park': (-122.928610, 49.313079, False), 'Deep Cove': (-122.946972, 49.326839, False),
 'Cosy Cove': (-122.919253, 49.327492, False), 'Woodlands': (-122.920781, 49.341831, False), 'Sunshine': (-122.914303, 49.345002, False),
 'Brighton Beach': (-122.898353, 49.359206, False), 'Thwaytes Landing': (-122.889626, 49.376517, False), 'Lake Buntzen': (-122.869705, 49.375285, False),
 'YMCA Camp Howdy / Camp Jubilee': (-122.889325, 49.371407, False), 'Granite Falls': (-122.862392, 49.451241, False), 'Weldwood': (-122.877844, 49.463031, False),
 'Wigwam Inn': (-122.885979, 49.461915, True),
 # Puget Sound Navigation Co. (Black Ball) ferries in Washington: positions from the Washington place names (ferry landings), approximate
 'Bremerton': (-122.625113, 47.561955, True), 'Edmonds': (-122.384100, 47.812923, True), 'Port Ludlow': (-122.683491, 47.925369, True),
 'Friday Harbor': (-123.014207, 48.535447, True),
 # lakes
 'Slocan City': ('SLO_SLOCAN_CITY', True), 'Silverton': (-117.357, 49.953, False), 'New Denver': (-117.377, 49.992, True), 'Rosebery': ('NAK_ROSEBERY', True),
 'Procter': ('CR_PROCTER', True), "Queen's Bay": (-116.933, 49.655, False), 'Kootenay Bay': (-116.872, 49.674, False), 'Ainsworth': (-116.910, 49.735, False),
 'Riondel': (-116.856, 49.763, False), 'Kaslo': (-116.911, 49.911, True), 'Lardeau': (-116.955, 50.146, True),
 'Robson West': ('KV_ROBSON_WEST', True), 'Deer Park': (-118.045, 49.417, False), 'Renata': (-118.100, 49.433, False), 'Edgewood': (-118.145, 49.783, False),
 'Burton City': (-117.885, 49.990, False), 'Arrow Park': (-117.925, 50.100, False), 'Nakusp': ('NAK_NAKUSP', True), 'Halcyon': (-117.905, 50.523, False),
 'Arrowhead': ('ARR_ARROWHEAD', True),
}
FULL = {'Westview': 'Westview (Powell River)', 'Vancouver': 'Vancouver (CP Pier)', 'Victoria': 'Victoria (CPR Steamship Terminal)', 'Victoria (Black Ball)': 'Victoria (Black Ball Terminal)'}
# landings Brendan has placed (so not "position approximate"), and what the station box says about them
PLACED = {'Vancouver': "Canadian Pacific's pier, where Canada Place stands today; the trains leave from the station at the head of the pier", 'Victoria': 'CPR Victoria Steamship Terminal',
          'Victoria (Black Ball)': 'Black Ball Line (Puget Sound Navigation Co.) terminal, Victoria', 'Westview': 'Steamer landing for Powell River', 'Cowans Point': 'Steamer landing, Bowen Island',
          'Granite Bay': 'Steamer landing', 'Elk Bay': 'Steamer landing', 'Phillips Arm': 'Steamer landing; called at fortnightly', 'Loughborough Inlet': 'Steamer landing',
          'Fraser Bay': 'Steamer landing; called at fortnightly', 'Jackson Bay': 'Steamer landing', 'Bones Bay': 'Steamer landing; called at by arrangement', 'Thompson Sound': 'Steamer landing',
          'Kingcome Inlet': 'Steamer landing; the guide lists it "via Simoom Sound"', 'Allison Harbour': 'Steamer landing; called at fortnightly',
          'Fulford Harbour': 'Ferry landing, Salt Spring Island (position from the Canadian Geographical Names file)', 'Swartz Bay': 'Ferry landing (position from the Canadian Geographical Names file)',
          'North Vancouver': 'North Vancouver ferry landing, foot of Lonsdale Avenue', 'Vancouver (NV Ferries)': 'North Vancouver ferry landing, Vancouver, foot of Columbia Street',
          'Bremerton': 'Ferry landing for the Navy Yard (position from the Washington place names)', 'Edmonds': 'Ferry landing (position from the Washington place names)',
          'Port Ludlow': 'Ferry landing (position of the place, from the Washington place names)', 'Friday Harbor': 'Ferry landing (position from the Washington place names)',
          'Anacortes': 'Black Ball ferry dock (Brendan)', 'Vancouver (Gore Ave. Dock)': 'Harbour Navigation Co. dock, foot of Gore Avenue (Brendan)', 'Belcarra Park': 'Landing (Brendan)', 'Deep Cove': 'Landing (Brendan)',
          'Cosy Cove': 'Landing (Brendan)', 'Woodlands': 'Landing (Brendan)', 'Sunshine': 'Landing (Brendan)', 'Brighton Beach': 'Landing (Brendan)', 'Thwaytes Landing': 'Landing (Brendan)',
          'Lake Buntzen': 'Landing at the Buntzen powerhouse (Brendan)', 'YMCA Camp Howdy / Camp Jubilee': 'Camp landing (Brendan)', 'Granite Falls': 'Landing (Brendan)',
          'Weldwood': 'Logging camp landing; position a guess (Brendan)', 'Wigwam Inn': 'Wigwam Inn, at the head of Indian Arm (Brendan)'}
ACTIVE = (-123.306, 48.862)                     # Active Pass: the Canadian Pacific's course between Vancouver and the Gulf Islands, Sidney and Victoria
VIA = {('Vancouver', 'Victoria'): [ACTIVE], ('Steveston', 'Sidney'): [ACTIVE], ('Sidney', 'Vancouver'): [ACTIVE], ('Ganges Harbour', 'Vancouver'): [ACTIVE],
       ('Anacortes', 'Sidney'): [(-123.005, 48.541)],       # the Anacortes boat by Friday Harbor
       # Admiralty Inlet, east of Port Townsend: kept on the course the lanes took before the Washington water came in (Brendan, 10 October 2026)
       ('Vancouver', 'Seattle (Lenora St. Dock)'): [(-122.807465, 48.276978), (-122.785867, 48.247898), (-122.777399, 48.225313), (-122.759016, 48.196824), (-122.742464, 48.175488), (-122.72067, 48.147837), (-122.704004, 48.127027), (-122.685999, 48.105934), (-122.655455, 48.070282), (-122.627668, 48.03519), (-122.591139, 47.98849), (-122.562951, 47.953284), (-122.543061, 47.929575), (-122.517668, 47.906008), (-122.500253, 47.885418)],
       ('Seattle (Colman Dock)', 'Port Angeles'): [(-122.503552, 47.854212), (-122.508204, 47.879948), (-122.521311, 47.904231), (-122.554101, 47.95249), (-122.587711, 47.995553), (-122.63284, 48.052511), (-122.670323, 48.095963), (-122.700101, 48.125912), (-122.736376, 48.145313), (-122.775704, 48.149094), (-122.814352, 48.142646), (-122.86111, 48.141955), (-122.894249, 48.148266), (-122.943088, 48.158026)],
       # the Cy Peck: down Fulford Harbour, out past Isabella Point and across Satellite Channel into Swartz Bay
       ('Fulford Harbour', 'Swartz Bay'): [(-123.4465, 48.7610), (-123.4330, 48.7500), (-123.4150, 48.7330), (-123.4050, 48.7200), (-123.4040, 48.7020), (-123.4110, 48.6890)]}
# the North Vancouver ferry (Brendan, 13 October 2026): not a straight line; leaving Vancouver it heads due north a short way, then bows round
# to Lonsdale. A quadratic curve whose control point is due north of the Columbia Street landing.
def _bow(a, b, c, n=14): return [((1 - t) ** 2 * a[0] + 2 * (1 - t) * t * b[0] + t * t * c[0], (1 - t) ** 2 * a[1] + 2 * (1 - t) * t * b[1] + t * t * c[1]) for t in (k / n for k in range(1, n))]
VIA[('Vancouver (NV Ferries)', 'North Vancouver')] = _bow((-123.10179, 49.28595), (-123.10179, 49.30050), (-123.08073, 49.30992))
BY_HAND = {frozenset(('Fulford Harbour', 'Swartz Bay')), frozenset(('North Vancouver', 'Vancouver (NV Ferries)'))}   # drawn through the points above
def port(n):
    v = P[n]
    if isinstance(v[0], str): r = RAIL[v[0]]; return dict(name=n, gid=v[0], lon=r['lon'], lat=r['lat'], principal=v[1], rail=True)
    return dict(name=FULL.get(n, n), gid='PORT_' + re.sub(r'\W+', '_', n.upper()).strip('_'), lon=v[0], lat=v[1], principal=v[2], rail=False, placed=PLACED.get(n))

CP, PSN, CN, U = 'Canadian Pacific', 'Puget Sound Navigation Co.', 'Canadian National', 'Union Steamships Ltd.'
GIF, NVF, HNC = 'Gulf Islands Ferry Co.', 'North Vancouver ferries', 'Harbour Navigation Co.'
OPS = {CP: ('cpss', 'CP', '7A1E2C'), PSN: ('bb', 'PSN', '2B3A55'), CN: ('cnss', 'CN', '2F6B44'), U: ('uss', 'USS', '3A3D48'), GIF: ('gif', 'GIF', '2E6F73'), NVF: ('nvf', 'NVF', '7A5230'), HNC: ('hnc', 'HNC', '3D6B3A')}        # livery, GTFS agency, colour
# what a sailing is called in the panels (Brendan): the company's steamship, not the sailing's own description
OPLABEL = {CP: 'CP Steamship', PSN: 'Black Ball Line', CN: 'CN Steamship', U: 'Union Steamship', GIF: 'Gulf Islands Ferry', NVF: 'North Vancouver Ferry', HNC: 'Harbour Navigation', 'lake': 'CP Lake Steamer'}
# sources (Brendan): every CP table is from the 1948 Canadian Pacific timetable; the Black Ball, CN Steamships and White Pass tables are from the May 1948 Official Guide
SRC = {CP: 'Canadian Pacific timetable, 1948', PSN: 'Puget Sound Navigation Co., from the Official Guide, May 1948', CN: 'Canadian National Steamships, from the Official Guide, May 1948',
       U: 'Union Steamships Sailing Guide No. 138, effective May 31, 1948. The guide is printed in Daylight Saving Time; the times shown are an hour earlier, in standard time like the railways',
       GIF: 'Gulf Islands Ferry Co. summer schedule, 1941 (Brendan); crossing times estimated',
       NVF: 'North Vancouver ferries: reconstructed from the described service, not a printed timetable (Brendan, October 2026)',
       HNC: 'Harbour Navigation Co., summer 1948: departure times from Brendan, landing times estimated'}
DST = {U: 3600}                 # printed in Daylight Saving Time: shown an hour earlier (Brendan: standard time throughout)
D0, D1, D2, D3 = 0, 86400, 2 * 86400, 3 * 86400
def W(half, day=0):
    """a call the guide gives only as a.m. or p.m. on a day: timed by distance, kept inside that half day"""
    return ('W', day + (1800 if half == 'a' else 12 * 3600 + 900), day + (11 * 3600 + 2700 if half == 'a' else 23 * 3600 + 1800))
def T(txt, day=0):
    """one time, or 'ar / lv'; '~' marks an estimate. -> (arr, dep, printed?)"""
    est = '~' in txt; parts = [x.strip().lstrip('~') for x in txt.split('/')]
    a = hm(parts[0]) + day; b = hm(parts[-1]) + day
    if b < a: b += 86400
    return a, b, not est
# service: key, operator, livery, long name, table, lane resolution, seq of ports, sailings.
# sailing: (id, badge name, label, service days, vessel shown on the map or None, [(seq index, time or None), ...], note)
SV = []
def service(key, op, name, table, res, seq, sail, dirs): SV.append(dict(key=key, op=op, name=name, table=table, res=res, seq=seq, sail=sail, dirs=dirs))

# ---- Table 168 / 168A: Triangle Route and Vancouver - Victoria (Princess Kathleen, Charlotte, Joan, Elizabeth). Summer columns (after June 19 / June 20 - Sept. 7).
service('bvv', CP, 'Vancouver – Victoria – Seattle', 'Tables 168 and 168A', 150, ['Vancouver', 'Victoria', 'Seattle (Lenora St. Dock)'], [
  ('NV', 'Steamer', 'Night boat to Victoria', 'CP_DAILY', None, [(0, T('11.00p')), (1, T('6.00a', D1))], 'Vancouver to Victoria overnight, daily. One of the Princesses Kathleen, Charlotte, Joan and Elizabeth; the table does not say which.'),
  ('AV', 'Steamer', 'Afternoon boat to Victoria', 'CP_DAILY', None, [(0, T('3.15p')), (1, T('8.30p'))], 'Vancouver to Victoria, daily from June 20 to September 7.'),
  ('TS', 'Steamer', 'Triangle Route', 'CP_DAILY', None, [(0, T('10.30a')), (1, T('3.30p / 4.30p')), (2, T('9.30p'))], 'Triangle Route, daily: Vancouver to Victoria and on to Seattle (Lenora Street Dock). Table d\'hôte luncheon and dinner.'),
  ('TN', 'Steamer', 'Triangle Route', 'CP_DAILY', None, [(2, T('9.00a')), (1, T('12.55p / 1.45p')), (0, T('6.00p'))], 'Triangle Route, daily after June 19: Seattle to Victoria and on to Vancouver. Until June 19 it left Seattle at 7.50 a.m. and reached Vancouver at 6.35 p.m.'),
  ('VN', 'Steamer', 'Night boat to Vancouver', 'CP_DAILY', None, [(1, T('11.00p')), (0, T('6.00a', D1))], 'Victoria to Vancouver overnight, daily.'),
  ('VM', 'Steamer', 'Morning boat to Vancouver', 'CP_XSUN', None, [(1, T('10.30a')), (0, T('3.45p'))], 'Victoria to Vancouver, daily except Sunday from June 20 to September 7.'),
  ('VS', 'Steamer', 'Sunday boat to Vancouver', 'CP_SUN1', None, [(1, T('8.00a')), (0, T('1.15p'))], 'Victoria to Vancouver, Sundays from June 20 to September 7.')],
  ['to Victoria and Seattle', 'to Vancouver'])
service('bvs', CP, 'Vancouver – Seattle direct', 'Table 168', 150, ['Vancouver', 'Seattle (Lenora St. Dock)'], [
  ('S', 'Steamer', 'Night boat to Seattle', 'CP_DAILY', None, [(0, T('10.45p')), (1, T('7.30a', D1))], 'Vancouver to Seattle direct, overnight, daily after June 19. The lane is drawn by the shortest water route; the table does not give the course.'),
  ('N', 'Steamer', 'Night boat to Vancouver', 'CP_DAILY', None, [(1, T('11.00p')), (0, T('8.00a', D1))], 'Seattle to Vancouver direct, overnight, daily after June 19. The lane is drawn by the shortest water route; the table does not give the course.')],
  ['to Seattle', 'to Vancouver'])
# ---- Table 169: Vancouver - Nanaimo, June 25 to Sept. 7 (Princess Elaine, Victoria, Joan, Elizabeth)
_n = 'Vancouver – Nanaimo, June 25 to September 7. Connects at Nanaimo with the Esquimalt & Nanaimo trains.'
service('bvn', CP, 'Vancouver – Nanaimo', 'Table 169', 150, ['Vancouver', 'Nanaimo'],
  [(f'W{k}', 'Steamer', 'Nanaimo boat', svc, None, [(0, T(a)), (1, T(b))], _n) for k, (a, b, svc) in enumerate(
      [('7.15a', '9.45a', 'CP_DAILY'), ('8.15a', '11.00a', 'CP_DAILY'), ('10.00a', '12.30p', 'CP_DAILY'), ('2.00p', '4.45p', 'CP_SUN1'), ('2.15p', '4.45p', 'CP_DAILY'), ('5.15p', '7.45p', 'CP_DAILY')], 1)] +
  [(f'E{k}', 'Steamer', 'Vancouver boat', svc, None, [(1, T(a)), (0, T(b))], _n) for k, (a, b, svc) in enumerate(
      [('6.30a', '9.00a', 'CP_DAILY'), ('10.45a', '1.15p', 'CP_DAILY'), ('11.45a', '2.30p', 'CP_DAILY'), ('1.45p', '4.15p', 'CP_DAILY'), ('5.30p', '8.15p', 'CP_SUN1'), ('6.00p', '8.30p', 'CP_DAILY')], 1)],
  ['to Nanaimo', 'to Vancouver'])
# ---- Table 170A: Steveston - Sidney, Motor Princess, May 1 to Sept. 28
service('bss', CP, 'Steveston – Sidney', 'Table 170A', 150, ['Steveston', 'Sidney'], [
  ('S1', 'Motor Princess', 'Steveston – Sidney ferry', 'CP_DAILY', 'Motor Princess', [(0, T('11.15a')), (1, T('2.15p'))], 'Motor Princess, Steveston to Sidney, daily from May 1 to September 28.'),
  ('S2', 'Motor Princess', 'Steveston – Sidney ferry', 'CP_XSUN', 'Motor Princess', [(0, T('6.15p')), (1, T('9.00p'))], 'Motor Princess, Steveston to Sidney, daily except Sunday.'),
  ('N1', 'Motor Princess', 'Steveston – Sidney ferry', 'CP_DAILY', 'Motor Princess', [(1, T('7.15a')), (0, T('10.15a'))], 'Motor Princess, Sidney to Steveston, daily.'),
  ('N2', 'Motor Princess', 'Steveston – Sidney ferry', 'CP_XSUN', 'Motor Princess', [(1, T('2.45p')), (0, T('5.45p'))], 'Motor Princess, Sidney to Steveston, daily except Sunday.')],
  ['to Sidney', 'to Steveston'])
service('bsv', CP, 'Sidney – Vancouver (Sundays)', 'Table 170A', 150, ['Sidney', 'Vancouver'], [
  ('SU', 'Motor Princess', 'Sunday boat to Vancouver', 'CP_SUN1', 'Motor Princess', [(0, T('2.45p')), (1, T('8.30p'))], 'Motor Princess, Sundays only: Sidney to Vancouver by way of Gulf Islands ports, not calling at Steveston. The table does not name the ports, so none are shown.')],
  ['to Vancouver', 'to Sidney'])
# ---- Table 170: Gulf Island Service, Princess Mary. The table gives only the hour of leaving and 'about' the hour of arriving.
_g = ' The table prints only the departure and the approximate arrival; the island calls are timed by distance.'
service('bg1', CP, 'Gulf Islands (Mondays)', 'Table 170', 120, ['Vancouver', 'Galiano Island', 'Mayne Island', 'Ganges Harbour', 'Hope Bay', 'Saturna Island', 'South Pender Island', 'Victoria'], [
  ('M', 'Princess Mary', 'Gulf Island Service', 'CP_MON1', 'Princess Mary', [(0, T('8.00a'))] + [(k, None) for k in range(1, 7)] + [(7, T('~5.30p'))], 'Princess Mary, Mondays: Vancouver to Victoria by the Gulf Islands.' + _g)],
  ['to the Gulf Islands and Victoria', ''])
service('bg2', CP, 'Gulf Islands (Tuesdays)', 'Table 170', 120, ['Victoria', 'James Island', 'Port Washington', 'Ganges Harbour', 'Mayne Island', 'Galiano Island', 'Vancouver'], [
  ('T', 'Princess Mary', 'Gulf Island Service', 'CP_TUE1', 'Princess Mary', [(0, T('9.30a'))] + [(k, None) for k in range(1, 6)] + [(6, T('~6.30p'))], 'Princess Mary, Tuesdays: Victoria to Vancouver by the Gulf Islands.' + _g)],
  ['to the Gulf Islands and Vancouver', ''])
service('bg3', CP, 'Gulf Islands (Thursdays)', 'Table 170', 120, ['Vancouver', 'Galiano Island', 'Mayne Island', 'Hope Bay', 'Saturna Island', 'South Pender Island', 'Ganges Harbour', 'Vancouver'], [
  ('H', 'Princess Mary', 'Gulf Island Service', 'CP_THU1', 'Princess Mary', [(0, T('8.00a'))] + [(k, None) for k in range(1, 7)] + [(7, T('~7.00p'))], 'Princess Mary, Thursdays: Vancouver, round the Gulf Islands and back.' + _g)],
  ['round the Gulf Islands', ''])
service('bg4', CP, 'Gulf Islands (Saturdays)', 'Table 170', 120, ['Vancouver', 'Galiano Island', 'Mayne Island', 'Port Washington', 'Ganges Harbour', 'Vancouver'], [
  ('S', 'Princess Mary', 'Gulf Island Service', 'CP_SAT1', 'Princess Mary', [(0, T('8.00a'))] + [(k, None) for k in range(1, 5)] + [(5, T('~5.00p'))], 'Princess Mary, Saturdays: Vancouver, round the Gulf Islands and back.' + _g)],
  ['round the Gulf Islands', ''])
# ---- Table 171: Vancouver - Westview (Powell River) - Comox, Princess Mary. Only some hours are printed; the rest say just a.m. or p.m.
_c = ' The table prints the hours at Vancouver and Westview, at Hornby Island and leaving Comox; the other calls say only a.m. or p.m. and are estimated.'
service('bc1', CP, 'Vancouver – Westview – Comox (Tuesdays and Saturdays)', 'Table 171', 150, ['Vancouver', 'Westview', 'Hornby Island', 'Denman Island', 'Union Bay', 'Comox', 'Westview', 'Vancouver'], [
  ('TU', 'Princess Mary', 'Powell River and Comox boat', 'CP_TUE1', 'Princess Mary', [(0, T('10.45p')), (1, T('5.30a / 7.00a', D1)), (2, T('9.00a', D1)), (3, T('~11.15a', D1)), (4, T('~12.15p', D1)),
      (5, T('~1.00p / 1.30p', D1)), (6, T('~4.30p / 10.15p', D1)), (7, T('5.30a', D2))], 'Princess Mary: leaves Vancouver Tuesday night, Westview and Comox on Wednesday, back at Vancouver Thursday morning. Connects at Union Bay with the Esquimalt & Nanaimo.' + _c),
  ('SA', 'Princess Mary', 'Powell River and Comox boat', 'CP_SAT1', 'Princess Mary', [(0, T('10.45p')), (1, T('5.30a / 7.00a', D1)), (2, T('9.00a', D1)), (3, T('~11.15a', D1)), (4, T('~12.15p', D1)),
      (5, T('~1.00p / 5.00p', D1)), (6, T('~8.00p / 10.15p', D1)), (7, T('5.30a', D2))], 'Princess Mary: leaves Vancouver Saturday night, Westview and Comox on Sunday, back at Vancouver Monday morning. From May 23 it leaves Comox at 5.00 p.m. instead of 1.30; the Hornby Island call is made June 13 to September 12 only.' + _c)],
  ['to Westview and Comox, and back', ''])
service('bc2', CP, 'Vancouver – Westview – Comox (Thursdays)', 'Table 171', 150, ['Vancouver', 'Westview', 'Blubber Bay', 'Union Bay', 'Comox', 'Blubber Bay', 'Westview', 'Vancouver'], [
  ('TH', 'Princess Mary', 'Powell River and Comox boat', 'CP_THU1', 'Princess Mary', [(0, T('10.45p')), (1, T('5.30a / 7.00a', D1)), (2, T('~7.40a', D1)), (3, T('~11.15a', D1)),
      (4, T('~12.15p / 1.30p', D1)), (5, T('~4.15p', D1)), (6, T('~4.50p / 10.15p', D1)), (7, T('5.30a', D2))], 'Princess Mary: leaves Vancouver Thursday night, Westview, Blubber Bay and Comox on Friday, back at Vancouver Saturday morning.' + _c)],
  ['to Westview and Comox, and back', ''])
# ---- Table 174: Vancouver - Ocean Falls - Prince Rupert, Princess Adelaide, weekly
_p = ' The table gives no hours for the calls, and says only that Prince Rupert is reached Monday p.m.; those times are estimated.'
service('bpr', CP, 'Vancouver – Ocean Falls – Prince Rupert', 'Table 174', 200, ['Vancouver', 'Englewood', 'Alert Bay', 'Port McNeill', 'Port Hardy', 'Ocean Falls', 'Butedale', 'Prince Rupert'], [
  ('N', 'Princess Adelaide', 'Prince Rupert boat', 'CP_SAT1', 'Princess Adelaide', [(0, T('8.00p'))] + [(k, None) for k in range(1, 7)] + [(7, T('~3.00p', D2))], 'Princess Adelaide: leaves Vancouver every Saturday at 8.00 p.m. for Englewood, Alert Bay, Port McNeill, Port Hardy, Ocean Falls and Butedale, reaching Prince Rupert on Monday afternoon.' + _p),
  ('S', 'Princess Adelaide', 'Prince Rupert boat', 'CP_MON1', 'Princess Adelaide', [(7, T('10.00p'))] + [(k, None) for k in range(6, 0, -1)] + [(0, T('8.00a', D3))], 'Princess Adelaide: leaves Prince Rupert every Monday at 10.00 p.m., reaching Vancouver at 8.00 a.m. on Thursday.' + _p)],
  ['to Ocean Falls and Prince Rupert', 'to Vancouver'])
# ---- Tables 168 and 168B: Puget Sound Navigation Co. (Black Ball), S.S. Chinook, all year, daily
service('bbb', PSN, 'Seattle – Port Angeles – Victoria', 'Tables 168 and 168B', 150, ['Seattle (Colman Dock)', 'Port Angeles', 'Victoria (Black Ball)'], [
  ('N0', 'Chinook', 'Black Ball night boat', 'CP_DAILY', 'Chinook', [(0, T('11.45p')), (1, T('4.30a / 6.00a', D1)), (2, T('7.15a', D1))], 'M.V. Chinook, Puget Sound Navigation Co.: leaves Seattle (Colman Ferry Terminal) daily at 11.45 p.m., lies at Port Angeles from 4.30 to 6.00 a.m. and reaches Victoria at 7.15. From the company\'s entry in the May 1948 Official Guide (dated May 15), and CP Tables 168 and 168B.'),
  ('S1', 'Chinook', 'Port Angeles ferry', 'CP_DAILY', 'Chinook', [(2, T('8.15a')), (1, T('9.30a'))], 'M.V. Chinook, Victoria to Port Angeles, daily all year.'),
  ('N1', 'Chinook', 'Port Angeles ferry', 'CP_DAILY', 'Chinook', [(1, T('10.30a')), (2, T('11.45a'))], 'M.V. Chinook, Port Angeles to Victoria, daily all year.'),
  ('S2', 'Chinook', 'Port Angeles ferry', 'CP_DAILY', 'Chinook', [(2, T('12.35p')), (1, T('1.50p'))], 'M.V. Chinook, Victoria to Port Angeles, daily all year.'),
  ('N2', 'Chinook', 'Port Angeles ferry', 'CP_DAILY', 'Chinook', [(1, T('3.00p')), (2, T('4.15p'))], 'M.V. Chinook, Port Angeles to Victoria, daily all year.')],
  ['to Port Angeles and Victoria', 'to Port Angeles and Seattle'])
service('bbd', PSN, 'Victoria – Seattle', 'Table 168', 150, ['Victoria (Black Ball)', 'Seattle (Colman Dock)'], [
  ('S', 'Chinook', 'Black Ball evening boat', 'CP_DAILY', 'Chinook', [(0, T('5.15p')), (1, T('9.30p'))], 'M.V. Chinook, Puget Sound Navigation Co.: Victoria to Seattle (Colman Ferry Terminal), daily. Four and a quarter hours, so drawn direct, not by Port Angeles.')],
  ['to Seattle', 'to Victoria'])
# ---- Puget Sound Navigation Co., Official Guide entry of May 15, 1948: Anacortes - San Juan Islands - Sidney (Chippewa or Vashon). The island calls are not timed.
_s = ' Motor vessel Chippewa or Vashon, by way of the San Juan Islands; the entry gives no hours for the island calls, so none are shown. From the company\'s entry in the May 1948 Official Guide (dated May 15).'
service('bba', PSN, 'Anacortes – San Juan Islands – Sidney', 'Puget Sound Navigation Co. entry dated May 15, 1948 (Official Guide, May 1948)', 120, ['Anacortes', 'Sidney'], [
  ('W1', 'Black Ball ferry', 'Sidney ferry', 'CP_DAILY', None, [(0, T('7.40a')), (1, T('10.30a'))], 'Anacortes to Sidney, daily.' + _s),
  ('W2', 'Black Ball ferry', 'Sidney ferry', 'CP_XSUN', None, [(0, T('2.10p')), (1, T('4.50p'))], 'Anacortes to Sidney, daily except Sundays and holidays.' + _s),
  ('E1', 'Black Ball ferry', 'Anacortes ferry', 'CP_DAILY', None, [(1, T('11.10a')), (0, T('1.40p'))], 'Sidney to Anacortes, daily.' + _s),
  ('E2', 'Black Ball ferry', 'Anacortes ferry', 'CP_XSUN', None, [(1, T('5.15p')), (0, T('8.10p'))], 'Sidney to Anacortes, daily except Sundays and holidays.' + _s)],
  ['to Sidney', 'to Anacortes'])
# ---- Canadian National Steamships, Pacific Coast Services: S.S. Prince Rupert, weekly (Official Guide, May 1948). Westview and Ocean Falls are
# printed only as a.m. or p.m.; they are timed by distance.
_cn = ' S.S. Prince Rupert, weekly. The table prints only a.m. or p.m. at Westview and Ocean Falls; those calls are timed by distance.'
service('bcn', CN, 'Vancouver – Ocean Falls – Prince Rupert – Ketchikan', 'Canadian National Steamships, Pacific Coast Services (Official Guide, May 1948)', 200,
  ['Vancouver (C.N. dock)', 'Westview', 'Ocean Falls', 'Prince Rupert', 'Ketchikan'], [
  ('N', 'Prince Rupert', 'Prince Rupert and Ketchikan boat', 'CP_MON1', 'Prince Rupert', [(0, T('9.00p')), (1, None), (2, None), (3, T('10.00a / 12.00a', D2)), (4, T('9.00a', D3))],
   'Leaves Vancouver Mondays at 9.00 p.m.; Prince Rupert Wednesday 10.00 a.m. to midnight; Ketchikan Thursday 9.00 a.m.' + _cn),
  ('S', 'Prince Rupert', 'Vancouver boat', 'CP_THU1', 'Prince Rupert', [(4, T('11.30a')), (3, T('7.00p / 11.15p')), (2, None), (1, T('9.00a', D2)), (0, T('2.00p', D2))],
   'Leaves Ketchikan Thursdays at 11.30 a.m.; Prince Rupert 7.00 to 11.15 p.m.; Westview Saturday 9.00 a.m.; Vancouver Saturday 2.00 p.m.' + _cn)],
  ['to Prince Rupert and Ketchikan', 'to Vancouver'])
# ---- Union Steamships Ltd., Sailing Guide No. 138, effective May 31, 1948 (Brendan's photographs). Entered here in Daylight Saving Time, as printed; shifted to standard time when the trips are made (DST).
# The guide prints hours for the Howe Sound and Sunshine Coast boats; for the northern and logging-camp routes it gives only the day and
# a.m. or p.m. at each call, so those calls are timed by distance inside their half day. Landings I cannot place are named in the notes only.
VP = 'Vancouver (Union Pier)'
def run(key, name, table, res, calls, tid, badge, label, svc, vessel, note, dirs):
    """a sailing whose calls, in order, make its own lane (ports may come round twice)"""
    service(key, U, name, table, res, [n for n, _ in calls], [(tid, badge, label, svc, vessel, [(k, t) for k, (_, t) in enumerate(calls)], note)], dirs)
# Route 8A: Vancouver - Squamish direct, S.S. Capilano, connecting with the Pacific Great Eastern
service('bu8a', U, 'Vancouver – Squamish direct', 'Route 8A', 120, [VP, 'Squamish (Government Dock)'], [
  ('N', 'Capilano', 'Squamish boat', 'CP_XSUN', 'Capilano', [(0, T('9.30a')), (1, T('12.45p'))], 'S.S. Capilano, daily except Sunday: Vancouver to Squamish dock direct, connecting with the Pacific Great Eastern.'),
  ('S', 'Capilano', 'Squamish boat', 'CP_XMON', 'Capilano', [(1, T('3.45p')), (0, T('7.00p'))], 'S.S. Capilano, daily except Monday: Squamish dock to Vancouver direct, connecting from the Pacific Great Eastern.'),
  ('SN', 'Steamer', 'Sunday night boat from Squamish', 'CP_SUN1', None, [(1, T('11.30p')), (0, T('~2.45a', D1))], 'Sunday night: leaves Squamish at 11.30 p.m. direct to Vancouver (Route 8). The arrival hour is cut off in the photograph and is estimated.')],
  ['to Squamish', 'to Vancouver'])
# Route 8: Bowen Island - Britannia - Woodfibre - Squamish, Lady Alexandra. Seq: 0 Vancouver, 1 Bowen, 2 Anvil Island, 3 Furry Creek, 4 Britannia, 5 Woodfibre, 6 Squamish
_8 = ' Route 8: only the hours shown without est. are printed.'
def n8(tid, svc, calls, what, badge='Lady Alexandra', vessel='Lady Alexandra'): return (tid, badge, 'Howe Sound boat', svc, vessel, calls, what + _8)
service('bu8', U, 'Vancouver – Bowen Island – Britannia – Woodfibre – Squamish', 'Route 8', 100, [VP, 'Bowen Island', 'Anvil Island', 'Furry Creek', 'Britannia', 'Woodfibre', 'Squamish (Government Dock)'], [
  n8('TuN', 'CP_TUE1', [(0, T('9.00a')), (1, None), (3, None), (4, None), (5, T('1.00p'))], 'Lady Alexandra, Tuesdays: Vancouver to Bowen Island, Furry Creek, Britannia and Woodfibre.'),
  n8('WeN', 'CP_WED1', [(0, T('9.00a')), (1, None), (4, None), (5, None), (6, T('2.00p'))], 'Lady Alexandra, Wednesdays: Vancouver to Bowen Island, Britannia, Woodfibre and Squamish.'),
  n8('ThN', 'CP_THU1', [(0, T('9.00a')), (1, None), (2, None), (4, None), (5, T('1.00p'))], 'Lady Alexandra, Thursdays: Vancouver to Bowen Island, Anvil Island, Britannia and Woodfibre.'),
  n8('FrN', 'CP_FRI1', [(0, T('9.00a')), (1, None), (4, None), (5, T('1.00p'))], 'Lady Alexandra, Fridays: Vancouver to Bowen Island, Britannia and Woodfibre.'),
  n8('SaN', 'CP_SAT1', [(0, T('9.00a')), (1, None), (4, None), (5, T('~1.00p'))], 'Lady Alexandra, Saturdays: Vancouver to Bowen Island, Britannia and Woodfibre (no arrival hour printed).'),
  n8('SuN', 'CP_SUN1', [(0, T('10.00a')), (1, None), (4, None), (5, None), (6, T('1.30p'))], 'Lady Alexandra, Sundays: Vancouver to Bowen Island, Britannia, Woodfibre and Squamish.'),
  n8('SuE', 'CP_SUN1', [(0, T('8.00p')), (4, None), (5, None), (6, T('~11.00p'))], 'Sunday evening steamer: Vancouver to Britannia, Woodfibre and Squamish, returning from Squamish at 11.30 p.m.', 'Steamer', None),
  n8('MoS', 'CP_MON1', [(6, T('2.30p')), (5, T('3.00p')), (4, T('3.30p')), (1, T('5.30p')), (0, T('6.45p'))], 'S.S. Capilano, Mondays: Squamish, Woodfibre, Britannia and Bowen Island to Vancouver.', 'Capilano', 'Capilano'),
  n8('TuS', 'CP_TUE1', [(5, T('3.00p')), (4, T('3.30p')), (1, T('5.00p')), (0, T('6.15p'))], 'Lady Alexandra, Tuesdays: Woodfibre, Britannia and Bowen Island to Vancouver.'),
  n8('WeS', 'CP_WED1', [(6, T('2.45p')), (5, T('3.30p')), (4, T('4.15p')), (1, T('6.00p')), (0, T('7.15p'))], 'Lady Alexandra, Wednesdays: Squamish, Woodfibre, Britannia and Bowen Island to Vancouver.'),
  n8('ThS', 'CP_THU1', [(5, T('3.00p')), (4, T('3.30p')), (1, T('5.00p')), (0, T('6.15p'))], 'Lady Alexandra, Thursdays: Woodfibre, Britannia and Bowen Island to Vancouver.'),
  n8('FrS', 'CP_FRI1', [(5, T('3.30p')), (4, T('4.15p')), (3, None), (1, T('6.00p')), (0, T('~7.15p'))], 'Lady Alexandra, Fridays: Woodfibre, Britannia, Furry Creek and Bowen Island to Vancouver (about 7.15 p.m.).'),
  n8('SaS', 'CP_SAT1', [(5, T('3.30p')), (4, T('4.15p')), (1, T('6.00p')), (0, T('7.15p'))], 'Lady Alexandra, Saturdays: Woodfibre, Britannia and Bowen Island to Vancouver.'),
  n8('SuS', 'CP_SUN1', [(6, T('3.00p')), (5, T('3.30p')), (4, T('4.00p')), (1, T('6.00p')), (0, T('7.15p'))], 'Lady Alexandra, Sundays: Squamish, Woodfibre, Britannia and Bowen Island to Vancouver.')],
  ['to Woodfibre and Squamish', 'to Vancouver'])
run('bu8m', 'Howe Sound (Mondays)', 'Routes 8 and 7', 100, [(VP, T('9.00a')), ('Bowen Island', None), ('Britannia', None), ('Woodfibre', T('1.00p / ~2.15p')), ('Port Mellon', T('~3.30p / 4.00p')), ('Gibsons', T('~4.45p / 5.00p')), (VP, T('7.00p'))],
    'MO', 'Lady Alexandra', 'Howe Sound boat', 'CP_MON1', 'Lady Alexandra', 'Lady Alexandra, Mondays: Vancouver to Bowen Island, Britannia and Woodfibre (1.00 p.m.), returning by Port Mellon (leaves 4.00) and Gibsons (leaves 5.00) to Vancouver at 7.00 p.m. The other hours are estimated.', ['round Howe Sound', ''])
# Vancouver - Bowen Island evening sailings (Route 8A page). The crossing time is taken from Route 8 (an hour and a quarter).
service('bub', U, 'Vancouver – Bowen Island evening sailings', 'Route 8A', 100, [VP, 'Bowen Island'], [
  ('SaE', 'Lady Alexandra', 'Moonlight Dance Cruise', 'CP_SAT1', 'Lady Alexandra', [(0, T('8.00p')), (1, T('~9.15p'))], 'Lady Alexandra, Saturday evenings at 8.00 p.m.: the Moonlight Dance Cruise to Bowen Island. Arrival estimated.'),
  ('SaR', 'Lady Alexandra', 'Moonlight Dance Cruise', 'CP_SAT1', 'Lady Alexandra', [(1, T('12.00a', D1)), (0, T('~1.15a', D1))], 'Lady Alexandra, leaving Bowen Island at midnight on Saturday. Arrival estimated.'),
  ('SuE', 'Lady Alexandra', 'Bowen Island evening boat', 'CP_SUN1', 'Lady Alexandra', [(0, T('7.30p')), (1, T('~8.45p'))], 'Lady Alexandra, Sunday evenings at 7.30 p.m. to Bowen Island. Arrival estimated.'),
  ('SuR', 'Lady Alexandra', 'Bowen Island evening boat', 'CP_SUN1', 'Lady Alexandra', [(1, T('9.00p')), (0, T('~10.15p'))], 'Lady Alexandra, leaving Bowen Island at 9.00 p.m. on Sundays. Arrival estimated.')],
  ['to Bowen Island', 'to Vancouver'])
# Route 7: West Howe Sound. A different round each day; the guide prints the leaving hours at a few calls.
_7 = ' West Howe Sound Route (Route 7); the guide does not name the boat. Hours marked est. are not printed.'
run('bu7a', 'West Howe Sound (Tuesdays)', 'Route 7', 100, [(VP, T('9.00a')), ('Cowans Point', None), ('Keats Island', None), ('Gibsons', None), ('Granthams Landing', None), ('Hopkins Landing', None),
    ('Port Mellon', T('~12.45p / 2.00p')), ('Seaside Park', None), ('New Brighton', None), ('Gibsons', T('~3.45p / 4.00p')), (VP, T('6.00p'))],
    'TU', 'Steamer', 'West Howe Sound boat', 'CP_TUE1', None, 'Tuesdays: Vancouver 9.00 a.m.; leaves Port Mellon 2.00 p.m. and Gibsons 4.00; Vancouver 6.00 p.m.' + _7, ['round West Howe Sound', ''])
run('bu7b', 'West Howe Sound (Wednesdays)', 'Route 7', 100, [(VP, T('9.00a')), ('Gibsons', None), ('Port Mellon', T('~12.00p / 1.00p')), ('Hopkins Landing', None), ('Granthams Landing', T('~2.20p / 2.30p')),
    ('Gibsons', T('~2.45p / 3.00p')), ('Gambier Harbour', None), ('West Bay', None), ('East Bay', None), (VP, T('~6.30p'))],
    'WE', 'Steamer', 'West Howe Sound boat', 'CP_WED1', None, 'Wednesdays: Vancouver 9.00 a.m.; leaves Port Mellon 1.00 p.m., Granthams Landing 2.30 and Gibsons 3.00; Vancouver about 6.30 p.m. Calls direct at Camp Artaban on June 2 and 16; other weeks by East Bay.' + _7, ['round West Howe Sound', ''])
run('bu7c', 'West Howe Sound (Thursdays)', 'Route 7', 100, [(VP, T('9.00a')), ('Gibsons', None), ('Granthams Landing', None), ('Hopkins Landing', None), ('Port Mellon', None), ('McNab Creek', None), ('Seaside Park', None),
    ('Port Mellon', T('~3.30p / 3.45p')), ('Gibsons', T('~5.00p / 5.15p')), (VP, T('7.15p'))],
    'TH', 'Steamer', 'West Howe Sound boat', 'CP_THU1', None, 'Thursdays: Vancouver 9.00 a.m.; leaves Port Mellon 3.45 p.m. and Gibsons 5.15; Vancouver 7.15 p.m.' + _7, ['round West Howe Sound', ''])
run('bu7d', 'West Howe Sound (Fridays)', 'Route 7', 100, [(VP, T('9.00a')), ('Gibsons', None), ('Granthams Landing', None), ('New Brighton', None), ('Williamsons Landing', None), ('Port Mellon', T('~12.30p / 1.15p')),
    ('Seaside Park', None), ('Hopkins Landing', None), ('Granthams Landing', T('~3.20p / 3.30p')), ('Gibsons', T('~3.45p / 4.00p')), (VP, T('6.00p'))],
    'FR', 'Steamer', 'West Howe Sound boat', 'CP_FRI1', None, 'Fridays: Vancouver 9.00 a.m.; leaves Port Mellon 1.15 p.m., Granthams Landing 3.30 and Gibsons 4.00; Vancouver 6.00 p.m.' + _7, ['round West Howe Sound', ''])
run('bu7e', 'West Howe Sound (Friday evenings)', 'Route 7', 100, [(VP, T('7.45p')), ('Bowen Island', None), ('Gibsons', None), ('Keats Island', None), ('Granthams Landing', None), (VP, T('~11.30p'))],
    'FE', 'Lady Alexandra', 'West Howe Sound boat', 'CP_FRI1', 'Lady Alexandra', 'Lady Alexandra, Friday evenings at 7.45 p.m.: Bowen Island, Gibsons, Keats Island and Granthams Landing, returning direct to Vancouver. Only the leaving hour is printed.' + _7, ['round West Howe Sound', ''])
run('bu7f', 'West Howe Sound (Saturdays)', 'Route 7', 100, [(VP, T('2.00p')), ('Bowen Island', None), ('Gibsons', None), ('Keats Island', None), ('Granthams Landing', None), ('Gambier Harbour', None),
    ('Port Mellon', T('~6.00p / 6.30p')), ('Seaside Park', None), (VP, T('~9.00p'))],
    'SA', 'Steamer', 'West Howe Sound boat', 'CP_SAT1', None, 'Saturdays: Vancouver 2.00 p.m.; leaves Port Mellon 6.30; direct to Vancouver about 9.00 p.m.' + _7, ['round West Howe Sound', ''])
run('bu7g', 'West Howe Sound (Sundays)', 'Route 7', 100, [(VP, T('9.30a')), ('Gibsons', None), ('Granthams Landing', None), ('Hopkins Landing', None), ('Seaside Park', None), ('Port Mellon', T('~1.30p / 2.30p')),
    ('Williamsons Landing', None), ('New Brighton', None), ('Gambier Harbour', None), ('Hopkins Landing', T('~3.35p / 3.45p')), ('Granthams Landing', T('~4.05p / 4.15p')), ('Keats Island', None),
    ('Gibsons', T('~4.50p / 5.00p')), (VP, T('7.00p'))],
    'SU', 'Steamer', 'West Howe Sound boat', 'CP_SUN1', None, 'Sundays: Vancouver 9.30 a.m.; leaves Port Mellon 2.30 p.m., Hopkins Landing not before 3.45, Granthams Landing 4.15 and Gibsons 5.00; Vancouver 7.00 p.m. Williamsons Landing and Keats Island are flag calls.' + _7, ['round West Howe Sound', ''])
run('bu7h', 'West Howe Sound (Sunday evenings)', 'Route 7', 100, [(VP, T('8.30p')), ('McNab Creek', None), ('Port Mellon', None), (VP, T('~12.45a', D1))],
    'SE', 'Steamer', 'West Howe Sound boat', 'CP_SUN1', None, 'Sunday evenings at 8.30 p.m.: McNab Creek and Port Mellon, returning direct to Vancouver. Only the leaving hour is printed.' + _7, ['round West Howe Sound', ''])
# Route 6: Sechelt - Pender Harbour - Westview - Refuge Cove - Cortez Island - Stuart Island, S.S. Lady Cecilia. Three round trips a week.
_6 = ' Route 6; hours marked est. are not printed.'
run('bu6a', 'Sunshine Coast and Stuart Island (Tuesdays)', 'Route 6', 120, [(VP, T('9.30a')), ('Roberts Creek', None), ('Wilson Creek', None), ('Sechelt', T('12.30p')), ('Pender Harbour', T('2.15p')), ('Westview', T('4.15p')),
    ('Van Anda', None), ('Blubber Bay', None), ('Lund', None), ('Refuge Cove', None), ('Squirrel Cove', None), ('Redonda Bay', None), ('Stuart Island', T('~12.30a / 3.30a', D1)),
    ('Bliss Landing', None), ('Lund', None), ('Savary Island', None), ('Blubber Bay', None), ('Van Anda', None), ('Westview', T('~9.00a / 9.30a', D1)), ('Stillwater', None),
    ('Pender Harbour', T('~11.30a / 11.45a', D1)), ('Sechelt', T('~1.30p / 1.45p', D1)), ('Wilson Creek', None), ('Roberts Creek', None), (VP, T('4.30p', D1))],
    'TU', 'Lady Cecilia', 'Sunshine Coast boat', 'CP_TUE1', 'Lady Cecilia', 'Lady Cecilia: leaves Vancouver Tuesday 9.30 a.m. for Sechelt, Pender Harbour, Westview and up to Stuart Island (Wednesday a.m.); back at Vancouver Wednesday 4.30 p.m. Also calls at Seaford.' + _6, ['to Westview and Stuart Island, and back', ''])
run('bu6b', 'Sunshine Coast and Cortes Island (Thursdays)', 'Route 6', 120, [(VP, T('9.30a')), ('Roberts Creek', None), ('Sechelt', T('12.00p')), ('Halfmoon Bay', None), ('Buccaneer Bay', None), ('Pender Harbour', T('2.45p')),
    ('Westview', T('5.00p')), ('Savary Island', None), ('Lund', None), ('Homfray Creek', None), ('Salmon Bay', None), ('Read Island', None), ('Heriot Bay', None), ('Surge Narrows', None), ('Bold Point', None),
    ('Whaletown', T('~6.30a / 7.30a', D1)), ('Mansons Landing', None), ('Lund', None), ('Blubber Bay', None), ('Van Anda', None), ('Westview', T('~1.00p / 1.30p', D1)), ('Pender Harbour', T('~3.30p / 3.45p', D1)),
    ('Halfmoon Bay', None), ('Sechelt', T('~5.45p / 6.00p', D1)), ('Roberts Creek', None), (VP, T('8.45p', D1))],
    'TH', 'Lady Cecilia', 'Sunshine Coast boat', 'CP_THU1', 'Lady Cecilia', 'Lady Cecilia: leaves Vancouver Thursday 9.30 a.m. for Sechelt, Pender Harbour, Westview, Toba Inlet and the Discovery Islands; leaves Whaletown Friday 7.30 a.m.; back at Vancouver Friday 8.45 p.m. Also calls at Merry Island.' + _6, ['to Westview and Cortes Island, and back', ''])
run('bu6c', 'Sunshine Coast and Stuart Island (Saturdays)', 'Route 6', 120, [(VP, T('1.00p')), ('Roberts Creek', None), ('Wilson Creek', None), ('Sechelt', T('4.00p')), ('Buccaneer Bay', None), ('Pender Harbour', T('6.00p')),
    ('Westview', T('8.00p')), ('Van Anda', None), ('Blubber Bay', None), ('Savary Island', None), ('Lund', None), ('Refuge Cove', None), ('Redonda Bay', None), ('Stuart Island', None),
    ('Whaletown', T('~6.30a / 7.30a', D1)), ('Mansons Landing', None), ('Lund', None), ('Savary Island', T('~11.30a / 11.45a', D1)), ('Westview', T('~1.00p / 1.30p', D1)), ('Pender Harbour', T('~3.30p / 3.45p', D1)),
    ('Buccaneer Bay', None), ('Halfmoon Bay', None), ('Sechelt', T('~5.45p / 6.00p', D1)), ('Wilson Creek', None), ('Roberts Creek', None), (VP, T('8.45p', D1))],
    'SA', 'Lady Cecilia', 'Sunshine Coast boat', 'CP_SAT1', 'Lady Cecilia', 'Lady Cecilia: leaves Vancouver Saturday 1.00 p.m. for Sechelt, Pender Harbour, Westview and Stuart Island; leaves Whaletown Sunday 7.30 a.m.; back at Vancouver Sunday 8.45 p.m.' + _6, ['to Westview and Stuart Island, and back', ''])
# Routes 5 and 5A: S.S. Chelohsin, the logging-camp boat. Only the hour of leaving Vancouver is printed.
_n = ' The guide gives only the day and a.m. or p.m. at each call; every hour but the leaving of Vancouver is estimated.'
_u = ' Camps the guide lists that are not placed, so the boat is simply shown passing through: Booth Logging Co., Smith & Osberg (for Port Harvey), Northwest Lumber Co. (Havannah Channel), Knight Inlet Cannery, B.C. Forest Products and Dot Logging Co.'
run('bu5n', 'Logging camps to Sullivan Bay (northbound)', 'Route 5', 150, [(VP, T('6.00p')), ('False Bay', W('p', D0)), ('Campbell River', W('a', D1)), ('Quathiaski Cove', W('a', D1)), ('Bloedel', W('a', D1)),
    ('Granite Bay', W('a', D1)), ('Elk Bay', W('a', D1)), ('Shoal Bay', W('p', D1)), ('Blind Channel', W('p', D1)), ('Loughborough Inlet', W('p', D1)),
    ('Jackson Bay', W('p', D1)), ('Port Neville', W('p', D1)), ('Minstrel Island', W('a', D2)), ('Bones Bay', W('a', D2)), ('Glendale Cove', W('a', D2)), ('Thompson Sound', W('a', D2)), ('Simoom Sound', None),
    ('Kingcome Inlet', W('p', D2)), ('Echo Bay', W('p', D2)), ('Sullivan Bay', T('~6.30p', D2))],
    'N', 'Chelohsin', 'Logging camp boat', 'CP_MON1', 'Chelohsin', 'S.S. Chelohsin: leaves Vancouver Mondays at 6.00 p.m. for Campbell River, Minstrel Island, Knight Inlet and Sullivan Bay (Wednesday). One week of the schedule is shown (Brendan, 5 October 2026): the week without the fortnightly calls. In the other week she also calls at Phillips Arm, Fraser Bay and Allison Harbour (fortnightly; which of them fall in the same week is not settled here). Bones Bay by arrangement.' + _u + _n, ['to Minstrel Island and Sullivan Bay', ''])
run('bu5s', 'Logging camps from Simoom Sound (southbound)', 'Route 5', 150, [('Sullivan Bay', T('~6.45p')), ('Simoom Sound', T('~9.00p')), ('Minstrel Island', W('a', D1)), ('Port Neville', W('a', D1)), ('Sayward', W('a', D1)), ('Shoal Bay', W('a', D1)),
    ('Bloedel', W('p', D1)), ('Quathiaski Cove', W('p', D1)), ('Campbell River', W('p', D1)), ('False Bay', W('p', D1)), (VP, T('~11.30p', D1))],
    'S', 'Chelohsin', 'Logging camp boat', 'CP_WED1', 'Chelohsin', 'S.S. Chelohsin, southbound: from Sullivan Bay back to Simoom Sound, which she leaves Wednesday p.m.; Minstrel Island Thursday a.m., reaching Vancouver Thursday p.m. Also calls at Smith & Osberg (for Port Harvey), which is not placed.' + _n, ['to Vancouver', ''])
run('bu5a', 'Campbell River and Alert Bay (Route 5A)', 'Route 5A', 150, [(VP, T('9.00p')), ('Stillwater', W('a', D1)), ('Campbell River', W('a', D1)), ('Quathiaski Cove', W('a', D1)), ('Bloedel', W('a', D1)), ('Rock Bay', W('a', D1)),
    ('Sayward', W('p', D1)), ('Englewood', W('p', D1)), ('Alert Bay', W('a', D2)), ('Sayward', W('a', D2)), ('Rock Bay', W('a', D2)), ('Bloedel', W('a', D2)), ('Quathiaski Cove', W('a', D2)),
    ('Campbell River', W('p', D2)), ('Blubber Bay', W('p', D2)), ('Van Anda', W('p', D2)), ('Stillwater', W('p', D2)), (VP, T('~7.00a', D3))],
    'F', 'Chelohsin', 'Alert Bay boat', 'CP_FRI1', 'Chelohsin', 'S.S. Chelohsin: leaves Vancouver Fridays at 9.00 p.m. for Campbell River, Sayward, Englewood and Alert Bay (Sunday a.m.), back at Vancouver Monday a.m. Also calls at Allison Logging Co., Forward Bay and Beaver Cove.' + _n, ['to Alert Bay, and back', ''])
# Route 1: Prince Rupert - Stewart, S.S. Cardena, weekly
run('bu1n', 'Vancouver – Prince Rupert – Stewart (northbound)', 'Route 1', 200, [(VP, T('9.00p')), ('Alert Bay', W('a', D1)), ('Port McNeill', W('a', D1)), ('Sointula', W('p', D1)), ('Port Hardy', W('p', D1)), ('Namu', W('p', D1)),
    ('Bella Bella', W('a', D2)), ('Klemtu', W('a', D2)), ('Butedale', W('a', D2)), ('Prince Rupert', T('~7.00p / 12.00a', D2)), ('Port Simpson', W('a', D3)), ('Alice Arm', W('a', D3)), ('Kincolith', W('a', D3)),
    ('Stewart', T('~8.00p', D3))],
    'N', 'Cardena', 'Prince Rupert and Stewart boat', 'CP_FRI1', 'Cardena', 'S.S. Cardena: leaves Vancouver Fridays at 9.00 p.m.; Prince Rupert Sunday p.m., leaving at midnight; Stewart (for Hyder, Alaska) Monday p.m. Also calls at Arrandale, and at Wales Island by arrangement.' + _n.replace('every hour but the leaving of Vancouver is', 'the hours other than leaving Vancouver and Prince Rupert are'), ['to Prince Rupert and Stewart', ''])
run('bu1s', 'Stewart – Prince Rupert – Vancouver (southbound)', 'Route 1', 200, [('Stewart', T('~9.00p')), ('Port Simpson', W('a', D1)), ('Prince Rupert', T('~10.30a / 1.30p', D1)), ('Butedale', W('p', D1)), ('Bella Bella', W('a', D2)),
    ('Namu', W('a', D2)), ('Port Hardy', T('~11.30a / 1.00p', D2)), ('Sointula', W('p', D2)), ('Alert Bay', W('p', D2)), ('Englewood', W('p', D2)), (VP, T('~9.00a', D3))],
    'S', 'Cardena', 'Vancouver boat', 'CP_MON1', 'Cardena', 'S.S. Cardena, southbound: leaves Stewart Monday p.m.; Prince Rupert Tuesday 1.30 p.m.; Port Hardy not before 1.00 p.m. Wednesday; Vancouver Thursday a.m. Only those two hours are printed; the rest are estimated.', ['to Vancouver', ''])
# Route 2: Port Hardy - Rivers Inlet - Bella Coola - Prince Rupert, S.S. Catala, weekly
run('bu2n', 'Vancouver – Rivers Inlet – Bella Coola – Prince Rupert (northbound)', 'Route 2', 200, [(VP, T('9.00p')), ('Campbell River', W('a', D1)), ('Sayward', W('a', D1)), ('Telegraph Cove', W('a', D1)), ('Englewood', W('a', D1)),
    ('Alert Bay', W('p', D1)), ('Port McNeill', W('p', D1)), ('Sointula', W('p', D1)), ('Port Hardy', W('p', D1)), ('Shushartie Bay', W('p', D1)), ('Goose Bay', W('a', D2)), ('Dawsons Landing', W('a', D2)),
    ('Rivers Inlet Cannery', W('a', D2)), ('Namu', None), ('Bella Coola', None), ('Ocean Falls', T('~10.30p', D2)), ('Bella Bella', W('a', D3)), ('Klemtu', W('a', D3)), ('Butedale', W('a', D3)), ('Prince Rupert', T('~8.00p', D3))],
    'N', 'Catala', 'Bella Coola and Prince Rupert boat', 'CP_TUE1', 'Catala', 'S.S. Catala: leaves Vancouver Tuesdays at 9.00 p.m. for Port Hardy, the Rivers Inlet canneries, Bella Coola, Ocean Falls and Prince Rupert (Friday p.m.). Also calls at Beaver Cove, Margaret Bay (fortnightly), several more canneries, South Bentinck Arm, New Bella Bella, Martins Dock, Hartley Bay (monthly) and the Skeena River canneries.' + _n, ['to Bella Coola and Prince Rupert', ''])
run('bu2s', 'Prince Rupert – Port Hardy – Vancouver (southbound)', 'Route 2', 200, [('Prince Rupert', T('9.00a')), ('Butedale', W('p', D0)), ('Klemtu', W('a', D1)), ('Bella Bella', W('a', D1)), ('Namu', W('a', D1)), ('Shushartie Bay', W('a', D1)),
    ('Port Hardy', W('p', D1)), ('Sointula', W('p', D1)), ('Port McNeill', W('p', D1)), ('Alert Bay', W('p', D1)), ('Englewood', W('p', D1)), (VP, T('~10.00a', D2))],
    'S', 'Catala', 'Vancouver boat', 'CP_SAT1', 'Catala', 'S.S. Catala, southbound: leaves Prince Rupert Saturdays at 9.00 a.m., reaching Vancouver Monday a.m. Beaver Cove by arrangement. Only the leaving hour is printed; the rest are estimated.', ['to Vancouver', ''])

# ---- Gulf Islands Ferry Co., M.V. Cy Peck, Fulford Harbour - Swartz Bay (Brendan's 1941 summer schedule; the Cy Peck was on the route through the 1940s)
_cp = ' Gulf Islands Ferry Co. Schedule from the 1941 summer timetable (Brendan); the Cy Peck was on the route through the 1940s. Only the departures are printed: the crossing time, about 40 minutes, is an estimate.'
_XW, _WE = 'W_1101111', 'W_0010000'
service('bfp', GIF, 'Fulford Harbour – Swartz Bay', "Gulf Islands Ferry Co. summer schedule, 1941", 60, ['Fulford Harbour', 'Swartz Bay'],
  [(f'S{k}', 'Cy Peck', 'Swartz Bay ferry', _XW, 'Cy Peck', [(0, T(a)), (1, T(b))], 'M.V. Cy Peck, Fulford Harbour to Swartz Bay, daily except Wednesday.' + _cp)
   for k, (a, b) in enumerate([('8.15a', '~8.55a'), ('10.15a', '~10.55a'), ('4.00p', '~4.40p'), ('6.45p', '~7.25p')], 1)] +
  [(f'F{k}', 'Cy Peck', 'Fulford Harbour ferry', _XW, 'Cy Peck', [(1, T(a)), (0, T(b))], 'M.V. Cy Peck, Swartz Bay to Fulford Harbour, daily except Wednesday.' + _cp)
   for k, (a, b) in enumerate([('9.30a', '~10.10a'), ('11.15a', '~11.55a'), ('5.00p', '~5.40p'), ('7.45p', '~8.25p')], 1)] +
  [('WS', 'Cy Peck', 'Swartz Bay ferry', _WE, 'Cy Peck', [(0, T('8.15a')), (1, T('~8.55a'))], 'M.V. Cy Peck, Wednesdays: Fulford Harbour to Swartz Bay at 8.15 a.m. Irregular Gulf Islands excursions between these sailings; she is shown lying at Swartz Bay.' + _cp),
   ('WF', 'Cy Peck', 'Fulford Harbour ferry', _WE, 'Cy Peck', [(1, T('7.00p')), (0, T('~7.40p'))], 'M.V. Cy Peck, Wednesdays: Swartz Bay to Fulford Harbour at 7.00 p.m., after the day\'s irregular Gulf Islands excursions.' + _cp)],
  ['to Swartz Bay', 'to Fulford Harbour'])
# ---- North Vancouver ferries, North Vancouver - Vancouver (NV Ferries): no printed table; reconstructed from the described service (Brendan, 5 October 2026)
_nv = ' North Vancouver ferry. No printed timetable: the times are reconstructed from the described service (6 a.m. to midnight, every 30 minutes, every 20 minutes in the weekday rush hours), not a printed table. The crossing took about 15 minutes.'
def _nvf():
    out, k = [], 0
    def add(ferry, a, b, frm, svc, peak):
        nonlocal k; k += 1
        tm = lambda x: f'{(x // 3600 - 1) % 12 + 1}.{x % 3600 // 60:02d}{"p" if x >= 43200 else "a"}'
        calls = [(frm, T(tm(a))), (1 - frm, T('~' + tm(b)))]
        out.append((f'{"L" if frm == 0 else "C"}{k}', ferry, 'Lonsdale ferry' if frm == 1 else 'Columbia ferry', svc, ferry, calls,
                    ('North Vancouver to Vancouver' if frm == 0 else 'Vancouver to North Vancouver') + (', weekday rush hour.' if peak else '.') + _nv))
    H = 3600; PEAKS = [(7 * H, 9 * H), (16 * H, 18 * H)]
    # weekends: Ferry No. 4 alone, Lonsdale :00 and :30, Columbia :15 and :45, 6 a.m. to midnight
    for t in range(6 * H, 24 * H, 1800):
        add('Ferry No. 4', t, t + 13 * 60, 0, 'W_0000011', False)
        if t + 15 * 60 < 24 * H: add('Ferry No. 4', t + 15 * 60, t + 28 * 60, 1, 'W_0000011', False)
    # weekdays: the same, but in the rush hours Nos. 4 and 5 both run and each pier has a boat at :00, :20 and :40
    t = 6 * H
    while t < 24 * H:
        pk = next((p for p in PEAKS if p[0] <= t < p[1]), None)
        if pk:
            for s in range(pk[0], pk[1], 1200):                         # No. 4 leaves Lonsdale at :00, :20, :40 on a 40-minute round; No. 5 the reverse
                four = (s - pk[0]) // 1200 % 2 == 0
                add('Ferry No. 4' if four else 'Ferry No. 5', s, s + 13 * 60, 0, 'W_1111100', True)
                add('Ferry No. 5' if four else 'Ferry No. 4', s, s + 13 * 60, 1, 'W_1111100', True)
            t = pk[1]; continue
        add('Ferry No. 4', t, t + 13 * 60, 0, 'W_1111100', False)
        if t + 15 * 60 < 24 * H: add('Ferry No. 4', t + 15 * 60, t + 28 * 60, 1, 'W_1111100', False)
        t += 1800
    return out
service('bnv', NVF, 'North Vancouver – Vancouver', 'North Vancouver ferries (reconstructed)', 30, ['North Vancouver', 'Vancouver (NV Ferries)'], _nvf(),
  ['to Vancouver', 'to North Vancouver'])
# ---- Harbour Navigation Co., Vancouver (Gore Ave. Dock) - Indian Arm - Wigwam Inn, summer 1948 (Brendan, 10 October 2026): harbour_nav_1948.csv.
# His departure times; the landings' times are Claude's estimates (~). Mon-Sat the M.V. Scenic (one boat, lying over at Wigwam Inn); Sunday two
# boats, direct: the Scenic taken for the 10.00 a.m. up and 4.00 p.m. down, the other boat not named.
import ab_table as _abt
_hn = _abt.load(os.path.join(HERE, 'harbour_nav_1948.csv')); _hseq = [r['station'] for r in _hn['rows']]
_HN = {'D1': ('Scenic', 'Morning boat down from Wigwam Inn, Monday to Saturday.'), 'U1': ('Scenic', 'Morning boat up to Wigwam Inn, Monday to Saturday.'),
       'D2': ('Scenic', 'Afternoon boat down from Wigwam Inn, Monday to Saturday ("late afternoon" arrival, read as 4.00).'),
       'U2': ('Scenic', 'Evening boat up to Wigwam Inn, Monday to Saturday (arrival not given: 2 hours assumed).'),
       'SU1': ('Scenic', 'Sunday, direct to Wigwam Inn.'), 'SD1': ('Scenic', 'Sunday, direct from Wigwam Inn.'),
       'SU2': (None, 'Sunday, direct to Wigwam Inn (the second Sunday boat, not named).'), 'SD2': (None, 'Sunday, direct from Wigwam Inn (the second Sunday boat, not named).')}
_hnn = ' Harbour Navigation Co., summer 1948: departure times as given; the times at the landings (and the arrivals not given) are estimated.'
def _hncalls(col):
    out = []
    for i, r in enumerate(_hn['rows']):
        c = (r.get(col) or '').strip()
        if not c: continue
        lv = c.startswith('lv'); t = re.sub(r'^(ar|lv)\s*', '', c)
        out.append((i, T(t if re.match(r'^(ar|lv)\s', c) else '~' + t)))   # the landing times are all estimates; only the end times are given
    return out[::-1] if col.startswith(('D', 'SD')) else out            # the down boats call from Wigwam Inn to Vancouver
service('bia', HNC, 'Vancouver – Indian Arm – Wigwam Inn', 'Harbour Navigation Co., summer 1948 (Brendan; estimated landing times)', 30, _hseq,
  [(col, v or 'Indian Arm boat', 'Wigwam Inn boat' if col.startswith(('U', 'SU')) else 'Indian Arm boat', 'W_1111110' if col[0] in 'DU' else 'W_0000001', v, _hncalls(col),
    ('M.V. Scenic. ' if v else '') + what + _hnn) for col, (v, what) in _HN.items()],
  ['to Wigwam Inn', 'to Vancouver'])

# ---- Puget Sound Navigation Co. ferries in Washington (company entry, Official Guide, May 1948). The Guide gives only the pattern of these
# sailings, so the times are reconstructed (Brendan, 9 October 2026) and every one is marked estimated.
def _hm(x): return f'{(x // 3600 - 1) % 12 + 1}.{x % 3600 // 60:02d}{"p" if x % 86400 >= 43200 else "a"}'
def _pair(a, b, dep, run, extra=None):
    d0 = dep; d1 = dep + run
    return [(a, T('~' + _hm(d0), (d0 // 86400) * 86400)), (b, T('~' + _hm(d1), (d1 // 86400) * 86400))]
H = 3600
# Seattle - Bremerton (Navy Yard): "22 round trips daily at approximately 30 minute intervals, 5.45, 6.15 a.m. to 11.45 p.m.; last departure at
# night 1.10 a.m." Brendan: hourly at :45 early and late, half-hourly in between, to make 22; crossing about an hour (estimated).
_br = sorted([h * H + 45 * 60 for h in range(5, 24)] + [h * H + 15 * 60 for h in (13, 14, 15)]) + [25 * H + 10 * 60]
_bn = ' Puget Sound Navigation Co. (Black Ball Line), Seattle - Bremerton (Navy Yard) route, worked by the Willapa, Enetai and Kalakala. The Guide gives "22 round trips daily at approximately 30 minute intervals, 5.45, 6.15 a.m. to 11.45 p.m., last departure at night 1.10 a.m.": these times are reconstructed from that (hourly early and late, half-hourly in the middle of the day), not printed.'
service('bbr', PSN, 'Seattle – Bremerton', 'Puget Sound Navigation Co. entry dated May 15, 1948 (Official Guide, May 1948)', 100, ['Seattle (Colman Dock)', 'Bremerton'],
  [(f'W{k}', 'Black Ball ferry', 'Bremerton ferry', 'W_1111110' if t == 5 * H + 45 * 60 else 'CP_DAILY', None, _pair(0, 1, t, H), 'Seattle to Bremerton.' + _bn) for k, t in enumerate(_br, 1)] +
  [(f'E{k}', 'Black Ball ferry', 'Seattle ferry', 'W_1111110' if t == 5 * H + 45 * 60 else 'CP_DAILY', None, _pair(1, 0, t, H), 'Bremerton to Seattle.' + _bn) for k, t in enumerate(_br, 1)],
  ['to Bremerton', 'to Seattle'])
# Edmonds - Port Ludlow (Olympic Peninsula route, ferries Klickitat and Nisqually): "Ten round trips 6.30 a.m. to 10.30 p.m." Brendan: about
# every two hours with rush-hour extras, Edmonds meeting the GN trains if a pattern shows: leaving Edmonds at :30 past the even hours meets the
# trains that call at Edmonds (No. 356 7.53 a.m., No. 5 5.49 p.m., No. 357 9.47 p.m.). Crossing about 75 minutes (estimated).
_ed = [h * H + 30 * 60 for h in range(6, 23, 2)]
_en = ' Puget Sound Navigation Co. (Black Ball Line) Olympic Peninsula route, ferries Klickitat and Nisqually; auto stage from Port Ludlow for Port Townsend and the Olympic Peninsula. The Guide gives "ten round trips 6.30 a.m. to 10.30 p.m.": these times are reconstructed (about every two hours, with rush-hour extras, leaving Edmonds to meet the Great Northern trains), not printed.'
service('bel', PSN, 'Edmonds – Port Ludlow', 'Puget Sound Navigation Co. entry dated May 15, 1948 (Official Guide, May 1948)', 100, ['Edmonds', 'Port Ludlow'],
  [(f'W{k}', 'Black Ball ferry', 'Port Ludlow ferry', 'CP_DAILY', None, _pair(0, 1, t, 75 * 60), 'Edmonds to Port Ludlow.' + _en) for k, t in enumerate(_ed + [16 * H + 30 * 60], 1)] +
  [(f'E{k}', 'Black Ball ferry', 'Edmonds ferry', 'CP_DAILY', None, _pair(1, 0, t, 75 * 60), 'Port Ludlow to Edmonds.' + _en) for k, t in enumerate(_ed + [7 * H + 30 * 60], 1)],
  ['to Port Ludlow', 'to Edmonds'])
# Anacortes - San Juan Islands (motor vessels Chippewa or Vashon): leave Anacortes 8.25 a.m., 1.35 and 7.00 p.m. daily, 2.30 and 5.30 p.m. Sundays
# and holidays; leave Friday Harbor 5.40 and 10.45 a.m. and 4.15 p.m. daily; leave Orcas 4.00 and 7.00 p.m. Sundays and holidays. Brendan: for now
# all of them go to and from Friday Harbor. Crossing about 1 h 50 min (estimated; it fits the Sidney boat leaving Anacortes 7.40 a.m.).
_sj = ' Puget Sound Navigation Co. (Black Ball Line), Anacortes - San Juan Islands. The Guide prints the departures only; every sailing is shown to and from Friday Harbor for now (the Sunday boats leave Orcas), and the arrivals are estimated.'
service('bsj', PSN, 'Anacortes – San Juan Islands', 'Puget Sound Navigation Co. entry dated May 15, 1948 (Official Guide, May 1948)', 120, ['Anacortes', 'Friday Harbor'],
  [(f'W{k}', 'Black Ball ferry', 'San Juan Islands ferry', svc, None, [(0, T(a)), (1, T(b))], 'Anacortes to the San Juan Islands.' + _sj) for k, (a, b, svc) in enumerate(
      [('8.25a', '~10.15a', 'CP_DAILY'), ('1.35p', '~3.25p', 'CP_DAILY'), ('2.30p', '~4.20p', 'CP_SUN1'), ('5.30p', '~7.20p', 'CP_SUN1'), ('7.00p', '~8.50p', 'CP_DAILY')], 1)] +
  [(f'E{k}', 'Black Ball ferry', 'Anacortes ferry', svc, None, [(1, T(a)), (0, T(b))], 'San Juan Islands to Anacortes.' + _sj) for k, (a, b, svc) in enumerate(
      [('5.40a', '~7.30a', 'CP_DAILY'), ('10.45a', '~12.35p', 'CP_DAILY'), ('4.15p', '~6.05p', 'CP_DAILY'), ('4.00p', '~5.50p', 'CP_SUN1'), ('7.00p', '~8.50p', 'CP_SUN1')], 1)],
  ['to Friday Harbor', 'to Anacortes'])

# ---- ships named on Brendan's reading of CP Tables 168 and 169 (8 October 2026)
_jx = ' The ship is named on a reading of the tables: two ships work the night boats, the afternoon and morning boats and the extra Nanaimo trips in fixed daily rounds. Which is the Princess Joan and which the Princess Elizabeth the times do not say, so the pair could be the other way round.'
_kc = ' The ship is named on a reading of the tables: one ship works the Triangle Route from Vancouver and the night boat back from Seattle, the other the reverse. Which is the Princess Kathleen and which the Princess Charlotte the times do not say, so the pair could be the other way round.'
_ev = ' The ship is named on Brendan\'s reading of Table 169 (her slots in the spring and autumn tables).'
SHIP = {('bvv', 'NV'): ('Princess Elizabeth', _jx), ('bvv', 'VM'): ('Princess Elizabeth', _jx), ('bvv', 'VS'): ('Princess Elizabeth', _jx), ('bvn', 'W4'): ('Princess Elizabeth', _jx), ('bvn', 'E5'): ('Princess Elizabeth', _jx),
        ('bvv', 'VN'): ('Princess Joan', _jx), ('bvv', 'AV'): ('Princess Joan', _jx), ('bvn', 'W2'): ('Princess Joan', _jx), ('bvn', 'E3'): ('Princess Joan', _jx),
        ('bvv', 'TS'): ('Princess Kathleen', _kc), ('bvs', 'N'): ('Princess Kathleen', _kc), ('bvv', 'TN'): ('Princess Charlotte', _kc), ('bvs', 'S'): ('Princess Charlotte', _kc),
        ('bvn', 'W3'): ('Princess Elaine', _ev), ('bvn', 'E4'): ('Princess Elaine', _ev), ('bvn', 'W6'): ('Princess Elaine', _ev), ('bvn', 'E1'): ('Princess Elaine', _ev),
        ('bvn', 'W1'): ('Princess Victoria', _ev), ('bvn', 'E2'): ('Princess Victoria', _ev), ('bvn', 'W5'): ('Princess Victoria', _ev), ('bvn', 'E6'): ('Princess Victoria', _ev)}
for D in SV:
    D['sail'] = [(tid, SHIP[(D['key'], tid)][0], label, svc, SHIP[(D['key'], tid)][0], calls,
                  note.replace(' One of the Princesses Kathleen, Charlotte, Joan and Elizabeth; the table does not say which.', '') + SHIP[(D['key'], tid)][1])
                 if (D['key'], tid) in SHIP else (tid, badge, label, svc, vessel, calls, note) for tid, badge, label, svc, vessel, calls, note in D['sail']]
assert sum(1 for D in SV for x in D['sail'] if (D['key'], x[0]) in SHIP) == len(SHIP)

# ---- lake steamers
service('bsl', CP, 'Slocan Lake', 'Table 158', 80, ['Slocan City', 'Silverton', 'New Denver', 'Rosebery'], [
  ('UP', 'Rosebery', 'Slocan Lake steamer', 'CP_MON1', 'Rosebery', [(0, T('10.35a')), (1, None), (2, None), (3, T('1.35p'))], 'Canadian Pacific steamer up Slocan Lake (Mondays), between the train from Nelson and the train to Nakusp. Also calls on signal at Evans Creek, Veveys and Enterprise. The table does not name the boat; the lake service was worked by the tug Rosebery.'),
  ('DN', 'Rosebery', 'Slocan Lake steamer', 'CP_WED1', 'Rosebery', [(3, T('10.35a')), (2, None), (1, None), (0, T('1.35p'))], 'Canadian Pacific steamer down Slocan Lake (Wednesdays), between the train from Nakusp and the train to Nelson. Also calls on signal at Enterprise, Veveys and Evans Creek. The table does not name the boat; the lake service was worked by the tug Rosebery.')],
  ['to Rosebery', 'to Slocan City'])
_k = " Also calls on signal at Balfour, Walker's, Deanshaven, Princess Creek, Woodberry, Mirror Lake, Schuletty Creek, Johnsons and Argenta. The table does not name the boat; in 1948 it was the sternwheeler Moyie."
service('bkl', CP, 'Kootenay Lake', 'Table 159', 100, ['Procter', "Queen's Bay", 'Kootenay Bay', 'Ainsworth', 'Riondel', 'Kaslo', 'Lardeau'], [
  ('N', 'Moyie', 'Kootenay Lake steamer', 'CP_SAT1', 'Moyie', [(0, T('9.45a')), (1, None), (2, None), (3, None), (4, None), (5, T('1.00p')), (6, T('3.20p'))], 'Canadian Pacific steamer up Kootenay Lake (Saturdays), leaving Procter five minutes after No. 11 arrives.' + _k),
  ('S', 'Moyie', 'Kootenay Lake steamer', 'CP_SAT1', 'Moyie', [(6, T('3.50p')), (5, T('5.50p')), (4, None), (3, None), (2, None), (1, None), (0, T('9.00p'))], 'Canadian Pacific steamer down Kootenay Lake (Saturdays).' + _k)],
  ['to Kaslo and Lardeau', 'to Procter'])
_a = ' The table does not name the boat; in 1948 it was the sternwheeler Minto.'
service('bal', CP, 'Arrow Lakes', 'Table 161', 120, ['Robson West', 'Deer Park', 'Renata', 'Edgewood', 'Burton City', 'Arrow Park', 'Nakusp', 'Halcyon', 'Arrowhead'], [
  ('N1', 'Minto', 'Arrow Lakes steamer', 'CP_TF', 'Minto', [(0, T('12.20p'))] + [(k, None) for k in range(1, 6)] + [(6, T('10.20p'))], 'Canadian Pacific steamer up the Lower Arrow Lake (Tuesdays and Fridays), leaving Robson West on the arrival of No. 11 from Nelson. Regular calls also at Robson and Glen Devon, and on signal at a dozen other landings.' + _a),
  ('N2', 'Minto', 'Arrow Lakes steamer', 'CP_WS', 'Minto', [(6, T('8.00a')), (7, None), (8, T('11.45a'))], 'Canadian Pacific steamer up the Upper Arrow Lake (Wednesdays and Saturdays), meeting the mixed train for Revelstoke at Arrowhead. Calls at Fosthall on signal and at St. Leon on Wednesdays.' + _a),
  ('S1', 'Minto', 'Arrow Lakes steamer', 'CP_WS', 'Minto', [(8, T('1.05p')), (7, None), (6, T('5.00p'))], 'Canadian Pacific steamer down the Upper Arrow Lake (Wednesdays and Saturdays), leaving Arrowhead an hour after the mixed train from Revelstoke arrives. Calls at St. Leon on Saturdays and at Fosthall on Wednesdays.' + _a),
  ('S2', 'Minto', 'Arrow Lakes steamer', 'CP_MTH', 'Minto', [(6, T('4.30a'))] + [(k, None) for k in range(5, 0, -1)] + [(0, T('2.45p'))], 'Canadian Pacific steamer down the Lower Arrow Lake (Mondays and Thursdays), reaching Robson West in time for No. 12 to Nelson. Regular calls also at Glen Devon and Robson, and on signal at a dozen other landings.' + _a)],
  ['to Nakusp and Arrowhead', 'to Nakusp and Robson West'])

# ================================================================ the summer-1948 week additions (Brendan, 13-15 October 2026; built 15 October)
# The map's week is about Monday 5 - Sunday 11 July 1948. Ships that do not sail every week are shown by the real dates of that week: a sailing
# carries 'd0', the day it starts counted from Monday 5 July (-1 = Sunday 4 July), and is shown only on the days of the week it is out
# (a voyage begun before Monday appears from Monday; one still out on Sunday night is not carried round into Monday). The lanes are drawn in
# full, with every port, even where the ship does not get there in the week shown.
import csv as _csv
for _r in _csv.DictReader(l for l in open(os.path.join(HERE, 'cp_t172_173_ports.csv')) if not l.startswith('#')):
    P[_r['port']] = (float(_r['lon']), float(_r['lat']), _r['port'] in ('Wrangell', 'Petersburg', 'Sitka', 'Haines', 'Yakutat', 'Seldovia', 'Kodiak'))
    PLACED[_r['port']] = ('Cruising point, not a port of call (Brendan)' if 'cruising' in _r['source'] else 'Steamer landing (' + _r['source'] + ')')
P.update({
 # Alaska (Brendan, 10 and 13 October; all his estimates)
 'Seattle (Pier 42)': (-122.338091, 47.593257, True), 'Juneau': (-134.405623, 58.297738, True), 'Valdez': (-146.361554, 61.124347, True),
 'Cordova': (-145.768406, 60.548018, True), 'Seward (steamer dock)': (-149.434532, 60.115842, True), 'Skagway': ('WPY_SKAGWAY', True),
 # west coast of Vancouver Island (B.C. names file, to the nearest second; Kildonan to the nearest minute)
 'Port Renfrew': (-124.41667, 48.55, False), 'Clo-oose': (-124.825278, 48.662222, False), 'Bamfield': (-125.134722, 48.828611, True),
 'Sarita': (-125.03333, 48.88333, False), 'Ecoole': (-125.058333, 48.968333, False), 'Kildonan': (-125.0, 49.0, False), 'Green Cove': (-124.978056, 48.989444, False),
 'Port Alberni': ('EN_PORT_ALBERNI', True), 'Ucluelet': (-125.546111, 48.942778, True), 'Port Albion': (-125.536944, 48.946944, False),
 'Tofino': (-125.904444, 49.153056, True), 'Clayoquot': (-125.93333, 49.16667, False), 'Kakawis': (-125.917778, 49.183056, False),
 'Ahousat': (-126.067778, 49.283056, False), 'Refuge Cove (West Coast)': (-126.2625, 49.366667, False), 'Hesquiat': (-126.468056, 49.399722, False),
 'Nootka Cannery': (-126.618056, 49.616389, False), 'Tahsis': (-126.664444, 49.916389, True), 'Ceepeecee': (-126.713889, 49.873611, False),
 'Hecate': (-126.748056, 49.851111, False), 'Zeballos': (-126.846111, 49.9825, True), 'Chamiss Bay': (-127.288889, 50.069167, True),
 'Sechart': (-125.256047, 48.956582, False), 'Broken Group': (-125.291491, 48.910303, False),
 # Queen Charlotte Islands (names file; Pacofi, Aero and Moresby Camp from the ports file above)
 'Sandspit': (-131.81667, 53.25, False), 'Skidegate': (-131.99028, 53.266667, False), 'Queen Charlotte City': (-132.08472, 53.254167, True),
 'Masset': (-132.146667, 54.011111, True),
 'Gardner Canal': (-128.391667, 53.443056, False),
 # the Yukon (Brendan, 13 October) and Tagish Lake
 'Whitehorse Landing': (-135.049767, 60.720871, True), 'Upper Laberge': (-135.092295, 60.947996, False), 'Lower Laberge': (-135.227103, 61.394534, False),
 'Big Salmon': (-134.926223, 61.881685, False), 'Carmacks': (-136.282676, 62.090537, True), 'Five Finger Rapids': (-136.355926, 62.271012, False),
 'Fort Selkirk': (-137.389729, 62.775918, False), 'Stewart Landing': (-139.429242, 63.316040, True), 'Dawson City': (-139.435619, 64.063786, True),
 'Mayo': (-135.896955, 63.591014, True), 'Carcross': ('WPY_CARCROSS', True), 'Ben-My-Chree': (-134.447171, 59.415915, True),
 'Tagish': (-134.26758225271948, 60.31272882733381, False), 'Rupert': (-134.19563386978754, 59.60349049140551, False),
 'Taku Landing': (-133.85435593416207, 59.626000039588554, False)})
FULL.update({'Seward (steamer dock)': 'Seward', 'Refuge Cove (West Coast)': 'Refuge Cove', 'Gardner Canal': 'Gardner Canal and Douglas Channel',
             'Broken Group': 'Broken Group (est.)', 'Seattle (Pier 42)': 'Seattle (Pier 42)'})
PLACED.update({'Seattle (Pier 42)': 'Alaska Steamship Co., Pier 42 (Brendan, est.)', 'Juneau': 'Steamer dock (Brendan, est.)', 'Valdez': 'Steamer dock (Brendan, est.)',
               'Cordova': 'Steamer dock (Brendan, est.)', 'Seward (steamer dock)': 'Steamer dock, for the Alaska Railroad (Brendan, est.)',
               'Refuge Cove (West Coast)': 'Refuge Cove, at Hot Springs Cove (B.C. names file: the Refuge Cove reserve at Hot Springs Cove)',
               'Gardner Canal': 'Cruising point, not a port of call (B.C. names file: Gardner Canal)', 'Kodiak': 'Kodiak (Brendan): beyond the edge of the water layer; the lane there is not on water',
               'Sechart': 'Sechart Lodge (Brendan)', 'Broken Group': 'Estimated (Brendan): no regular landing, a pier where the boat met fishermen to trade',
               'Pacofi': 'Landing by Pacofi Creek (Brendan, est.)', 'Whitehorse Landing': 'British Yukon Navigation landing, Whitehorse (Brendan)',
               'Ben-My-Chree': 'Ben-My-Chree, West Taku Arm (Brendan)', 'Tagish': 'Tagish (Brendan)', 'Rupert': 'Rupert, the Graham Inlet call (Brendan: a guess)',
               'Taku Landing': 'Taku Landing, the old Taku Tram landing (Brendan)', 'Sandspit': 'Landing (B.C. names file)', 'Skidegate': 'Landing (B.C. names file)',
               'Queen Charlotte City': 'Landing (B.C. names file)', 'Masset': 'Landing (B.C. names file)'})
for _n in ('Upper Laberge', 'Lower Laberge', 'Big Salmon', 'Carmacks', 'Five Finger Rapids', 'Fort Selkirk', 'Stewart Landing', 'Dawson City', 'Mayo'):
    PLACED[_n] = 'Landing (Brendan)'
# Queen Charlotte City to Masset: out of Skidegate Inlet and up the east coast of Graham Island, round Rose Spit (the water layer would
# otherwise take the lane over the island by Masset Inlet)
VIA[('Queen Charlotte City', 'Masset')] = [(-131.93, 53.235), (-131.78, 53.27), (-131.70, 53.45), (-131.72, 53.70), (-131.70, 53.95), (-131.62, 54.12),
                                           (-131.80, 54.15), (-131.98, 54.10), (-132.12, 54.07)]
# north from Ketchikan: up Tongass Narrows past the Guard Islands into Clarence Strait (Brendan, 15 October 2026: the lanes went south first)
_KTN = [(-131.672, 55.356), (-131.700, 55.372), (-131.740, 55.398), (-131.800, 55.440)]
for _q in ('Wrangell', 'Juneau', 'Taku Glacier', 'Kodiak'): VIA[('Ketchikan', _q)] = _KTN
def Wd(day=0):
    """a call the schedule gives only by its date: timed by distance, kept inside that day"""
    return ('W', day + 6 * 3600, day + 22 * 3600)
def dsail(tid, badge, label, vessel, d0, calls, note):
    """a dated sailing: d0 = the day it starts, counted from Monday 5 July 1948"""
    return (tid, badge, label, 'W_' + ''.join('1' if i == d0 % 7 else '0' for i in range(7)), vessel, calls, note, {'d0': d0})
D4, D5, D6, D7, D8 = 4 * 86400, 5 * 86400, 6 * 86400, 7 * 86400, 8 * 86400

ASS, BYN, BST = 'Alaska Steamship Co.', 'British Yukon Navigation Co.', 'Barkley Sound Transportation Co.'
OPS.update({ASS: ('ass', 'ASS', '1F3A5F'), BYN: ('byn', 'BYN', '4F6B3A'), BST: ('bst', 'BST', '2F5D7C')})
OPLABEL.update({ASS: 'Alaska Steamship', BYN: 'British Yukon Navigation', BST: 'Barkley Sound boat'})
SRC.update({ASS: 'Alaska Steamship Company, 1948 sailing schedule (Official Guide); the July sailings continue the printed pattern (Brendan), and the hours other than at Seattle and Seward are estimated',
            BYN: 'British Yukon Navigation Co. (White Pass & Yukon Route), summer 1948: a model week estimated by Brendan, not a printed timetable',
            BST: 'Barkley Sound Transportation Co., Port Alberni, summer 1948: a model schedule (Brendan, from the British Colonist, 18 August 1949, and Jan Peterson, "Here Today, Here Tomorrow", 2001)'})
_wk = ' Shown by its dates in the week of 5 July 1948.'

# ---- Alaska Steamship Co.: Aleutian and Baranof, Seattle - Ketchikan - Juneau - (Cordova - Valdez) - Seward, each fortnightly, alternate Saturdays
# (ak_ass_1948.csv). Seattle and Seward hours printed (Seward in Alaska time, 150th meridian: shown two hours later, in Pacific time); the other
# calls are by date only and timed by distance inside the day.
_as = (' Alaska Steamship Co.: the Aleutian and the Baranof sail from Seattle (Pier 42) on alternate Saturdays at 9.00 a.m., so each ship sails'
       ' fortnightly; the schedule prints the hours only at Seattle and Seward, the other calls by date (timed here by distance). Connects at Seward'
       ' with the Alaska Railroad.' + _wk)
service('bas', ASS, 'Seattle – Ketchikan – Juneau – Cordova – Valdez – Seward', 'Alaska Steamship Co. sailing schedule, 1948', 250,
  ['Seattle (Pier 42)', 'Ketchikan', 'Juneau', 'Cordova', 'Valdez', 'Seward (steamer dock)', 'Juneau', 'Ketchikan', 'Seattle (Pier 42)'], [
  dsail('AS', 'Aleutian', 'Seattle boat', 'Aleutian', -1, [(6, Wd()), (7, Wd(D1)), (8, W('a', D4))],
        'S.S. Aleutian, southbound: the 26 June sailing coming home, from Seward (Thursday 1 July), Valdez and Cordova; Juneau Sunday 4 July, Ketchikan Monday 5, Seattle Thursday 8 July a.m.' + _as),
  dsail('AN', 'Aleutian', 'Alaska boat', 'Aleutian', 5, [(0, T('9.00a')), (1, Wd(D2))],
        'S.S. Aleutian, northbound: sails from Seattle Saturday 10 July at 9.00 a.m. for Ketchikan (Monday 12), Juneau and Seward (Thursday 15).' + _as),
  dsail('BN', 'Baranof', 'Alaska boat', 'Baranof', -2, [(0, T('9.00a')), (1, Wd(D2)), (2, Wd(D3)), (3, Wd(D5)), (4, Wd(D5)), (5, T('~9.00a', D6))],
        'S.S. Baranof, northbound: sailed from Seattle Saturday 3 July at 9.00 a.m.; Ketchikan Monday 5, Juneau Tuesday 6, Cordova and Valdez Thursday 8, Seward Friday 9 July a.m. (the boat train for Anchorage runs on Friday).' + _as),
  dsail('BS', 'Baranof', 'Seattle boat', 'Baranof', 4, [(5, T('11.00p')), (6, Wd(D2)), (7, Wd(D3))],
        'S.S. Baranof, southbound: leaves Seward Friday 9 July at 9.00 p.m. Alaska time (11.00 p.m. Pacific); Juneau Sunday 11, Ketchikan Monday 12, Seattle Thursday 15 July.' + _as)],
  ['to Alaska', 'to Seattle'])
# ---- Alaska Steamship Co.: Denali, Kodiak Island - Cook Inlet - Yakutat route, every three weeks (ak_ass_denali_1948.csv; the 8 July sailing follows
# the printed 27 May pattern: Ketchikan, the Kodiak outports, Kodiak, Seldovia, Seward, Yakutat, Ketchikan)
service('bad', ASS, 'Seattle – Ketchikan – Kodiak – Seldovia – Seward – Yakutat', 'Alaska Steamship Co. sailing schedule, 1948', 250,
  ['Seattle (Pier 42)', 'Ketchikan', 'Kodiak', 'Seldovia', 'Seward (steamer dock)', 'Yakutat', 'Ketchikan', 'Seattle (Pier 42)'], [
  dsail('DN', 'Denali', 'Kodiak boat', 'Denali', 3, [(0, T('9.00a')), (1, Wd(D2)), (2, Wd(D5))],
        'S.S. Denali, Kodiak Island - Cook Inlet - Yakutat route: sails from Seattle Thursday 8 July at 9.00 a.m. (every three weeks; the July date continues the printed 6 May, 27 May and 17 June sailings); Ketchikan Saturday 10, then the Kodiak outports (Tuesday and Wednesday, not named; drawn as Kodiak), Kodiak, Seldovia, Seward, Yakutat and home to Seattle about 31 July. Kodiak is beyond the edge of the map\'s water.' + _as.replace(' The Aleutian and the Baranof sail from Seattle (Pier 42) on alternate Saturdays at 9.00 a.m., so each ship sails fortnightly; the', ' The'))],
  ['to Kodiak', 'to Seattle'])
# ---- the S.S. Alaska (a subsidiary of the Alaska Steamship Co.; Official Guide): Seattle every second Thursday (1 and 15 July), 9.00 a.m. (est),
# Ketchikan, Wrangell, Petersburg, Juneau, Haines, Skagway and Sitka; the same calls coming back (Brendan, 14 October). All hours estimated.
service('bsa', ASS, 'Seattle – Ketchikan – Juneau – Skagway – Sitka', 'Official Guide, 1948 (S.S. Alaska)', 250,
  ['Seattle (Pier 42)', 'Ketchikan', 'Wrangell', 'Petersburg', 'Juneau', 'Haines', 'Skagway', 'Haines', 'Juneau', 'Sitka', 'Petersburg', 'Wrangell', 'Ketchikan', 'Seattle (Pier 42)'], [
  dsail('A', 'Alaska', 'Southeastern Alaska boat', 'Alaska', -1, [(3, Wd()), (4, Wd(D1)), (5, Wd(D2)), (6, Wd(D2)), (7, Wd(D3)), (8, Wd(D3)), (9, Wd(D4)), (10, Wd(D5)),
        (11, Wd(D5)), (12, Wd(D6)), (13, T('~8.00a', D8))],
        'S.S. Alaska (a subsidiary of the Alaska Steamship Co.): sails from Seattle every second Thursday, here the 1 July sailing (9.00 a.m.; Ketchikan Saturday 3, Wrangell and Petersburg Sunday 4), Juneau Monday 5, Haines and Skagway Tuesday 6 (she turns at Skagway), Haines and Juneau Wednesday 7, Sitka Thursday 8, Petersburg and Wrangell Friday 9, Ketchikan Saturday 10, Seattle about Monday 12. The Guide gives only the ports and the Seattle hour (itself estimated); the dates and the return calls are estimated (other sources: the same calls both ways).' + _wk)],
  ['to Skagway and Sitka', 'to Seattle'])

# ---- CP Table 172, Alaska service: Princess Louise and Princess Norah, Vancouver - Skagway, each about every 10-11 days (cp_t172_skagway_1948.csv;
# only Vancouver timed, the other calls a.m. or p.m. on a date)
_cs = (' Canadian Pacific Alaska service (Table 172): the Princess Louise and the Princess Norah sail from Vancouver at 9.00 p.m. on dates about'
       ' three and a half days apart, so each ship sails every ten or eleven days. Only Vancouver is timed; the other calls are printed as a.m. or p.m.'
       ' on a date (timed here by distance). Connects at Skagway with the White Pass & Yukon Route.' + _wk)
service('bca', CP, 'Vancouver – Prince Rupert – Ketchikan – Juneau – Skagway', 'Table 172', 250,
  ['Vancouver', 'Alert Bay', 'Prince Rupert', 'Ketchikan', 'Wrangell', 'Juneau', 'Skagway'], [
  dsail('NS1', 'Princess Norah', 'Vancouver boat', 'Princess Norah', -1, [(1, W('p')), (0, T('9.00a', D1))],
        'Princess Norah, southbound: the 26 June sailing coming home (Skagway Thursday 1 July); Alert Bay Sunday 4 p.m., Vancouver Monday 5 July 9.00 a.m.' + _cs),
  dsail('LN', 'Princess Louise', 'Skagway boat', 'Princess Louise', -1, [(1, W('a')), (2, W('a', D1)), (3, W('p', D1)), (4, W('a', D2)), (5, W('p', D2)), (6, W('a', D3))],
        'Princess Louise, northbound: sailed from Vancouver Saturday 3 July at 9.00 p.m.; Alert Bay Sunday a.m., Prince Rupert Monday a.m., Ketchikan Monday p.m., Wrangell Tuesday a.m., Juneau Tuesday p.m., Skagway Wednesday 7 July a.m.' + _cs),
  dsail('LS', 'Princess Louise', 'Vancouver boat', 'Princess Louise', 3, [(6, W('p')), (5, W('a', D1)), (4, W('p', D1)), (3, W('a', D2)), (2, W('p', D2)), (1, W('p', D3)), (0, T('9.00a', D4))],
        'Princess Louise, southbound: leaves Skagway Thursday 8 July p.m.; Juneau Friday a.m., Wrangell Friday p.m., Ketchikan Saturday a.m., Prince Rupert Saturday p.m., Alert Bay Sunday p.m., Vancouver Monday 12 July 9.00 a.m.' + _cs),
  dsail('NN2', 'Princess Norah', 'Skagway boat', 'Princess Norah', 2, [(0, T('9.00p')), (1, W('a', D1)), (2, W('a', D2)), (3, W('p', D2)), (4, W('a', D3)), (5, W('p', D3)), (6, W('a', D4))],
        'Princess Norah, northbound: sails from Vancouver Wednesday 7 July at 9.00 p.m.; Alert Bay Thursday a.m., Prince Rupert Friday a.m., Ketchikan Friday p.m., Wrangell Saturday a.m., Juneau Saturday p.m., Skagway Sunday 11 July a.m.' + _cs)],
  ['to Skagway', 'to Vancouver'])
# ---- CP Table 173, west coast of Vancouver Island: Princess Maquinna, from Victoria every 8 days (cp_t173_maquinna_1948.csv). No hours but the
# Victoria departure: the calls are timed by distance (estimated); the return calls (the same ports, reversed) are assumed.
_mq = [r.split(',', 1)[1].strip() for r in open(os.path.join(HERE, 'cp_t173_maquinna_1948.csv')) if re.match(r'^\d+,', r)]
_mq = [{'Sarita Bay': 'Sarita', 'Refuge Cove': 'Refuge Cove (West Coast)'}.get(n, n) for n in _mq]
service('bcw', CP, 'Victoria – West Coast of Vancouver Island – Chamiss Bay', 'Table 173', 150, _mq + _mq[-2::-1], [
  dsail('W', 'Princess Maquinna', 'West Coast boat', 'Princess Maquinna', 0,
        [(0, T('11.00p'))] + [(k, None) for k in range(1, 29)] + [(29, T('~9.00a / 2.00p', D4))] + [(k, None) for k in range(30, 58)] + [(58, T('~12.00p', D7))],
        'Princess Maquinna, west coast of Vancouver Island (Table 173): leaves Victoria every eight days at 11.00 p.m., here Monday 5 July; Chamiss Bay Friday 9 July, back at Victoria about noon Monday 12. The table gives no other hours: the calls are timed by distance, and the return calls (the same ports in reverse) are assumed.' + _wk)],
  ['to Chamiss Bay', 'to Victoria'])
# ---- CN Steamships Table 315: T.S.S. Prince George, 10-day Alaska cruises (cn_t315_prince_george_1948.csv; Pacific Standard Time)
_pg = (' T.S.S. Prince George (Canadian National Steamships, Table 315): ten-day Alaska cruises from Vancouver, every ten or eleven days from 19 June 1948.'
       ' The table prints a few hours; the calls given as a.m. or p.m. are timed by distance. Taku Glacier and Gardner Canal and Douglas Channel are'
       ' cruising points. Haines: to embark and disembark passengers only. Connects at Skagway with the White Pass & Yukon Route.' + _wk)
service('bcg', CN, 'Vancouver – Prince Rupert – Ketchikan – Juneau – Skagway (Alaska cruise)', 'Canadian National Steamships Table 315 (Official Guide, 1948)', 250,
  ['Vancouver (C.N. dock)', 'Ocean Falls', 'Prince Rupert', 'Ketchikan', 'Taku Glacier', 'Juneau', 'Haines', 'Skagway', 'Haines', 'Juneau', 'Wrangell', 'Ketchikan',
   'Prince Rupert', 'Gardner Canal', 'Ocean Falls', 'Vancouver (C.N. dock)'], [
  dsail('S', 'Prince George', 'Alaska cruise', 'Prince George', 0, [(7, T('7.00p')), (8, W('p')), (9, W('a', D1)), (10, W('p', D1)), (11, T('~10.00a / 12.00p', D2)),
        (12, T('7.00p / 11.15p', D2)), (13, W('a', D3)), (14, W('a', D4)), (15, T('9.30a', D5))],
        'The 30 June cruise coming south: leaves Skagway Monday 5 July 7.00 p.m.; Haines, Juneau Tuesday, Wrangell, Ketchikan Wednesday noon, Prince Rupert Wednesday 7.00 to 11.15 p.m., Gardner Canal and Douglas Channel Thursday, Ocean Falls Friday, Vancouver Saturday 10 July 9.30 a.m.' + _pg),
  dsail('N', 'Prince George', 'Alaska cruise', 'Prince George', 5, [(0, T('9.00p')), (1, W('p', D1)), (2, T('9.00a / 1.00p', D2))],
        'The 10 July cruise: leaves Vancouver Saturday 10 July 9.00 p.m.; Ocean Falls Sunday p.m., Prince Rupert Monday 12 July 9.00 a.m.' + _pg)],
  ['to Alaska', 'to Vancouver'])
# ---- Union Steamships Route 4, Queen Charlotte Islands Route: S.S. Coquitlam, every ten days (Thursdays or Mondays alternately), Daylight Saving
# Time (scans/union1948/). The 5 July sailing; only Vancouver 9.00 p.m. and Prince Rupert 11.00 p.m. are printed, the other calls by date.
# "Cumshewa Inlet Camps" are two calls (Brendan): Aero and Moresby Camp, in Gillatt Arm.
_q = (' S.S. Coquitlam, Queen Charlotte Islands Route (Union Route 4): from Vancouver (Union Pier or Pier H) every ten days at 9.00 p.m., on Thursdays'
      ' or Mondays alternately (June 3, 14, 24; July 5, 15, 26; August 5, 16, 26). The guide prints only the dates at the other calls (timed here by'
      ' distance). The Cumshewa Inlet Camps are shown as Aero and Moresby Camp (Gillatt Arm). Port Clements is called at on alternate sailings; on'
      ' this one it is reached by connection from Skidegate. Southbound the steamer calls at Pacofi by arrangement.' + _wk)
service('bu4', U, 'Vancouver – Queen Charlotte Islands – Prince Rupert', 'Route 4', 200,
  [VP, 'Alert Bay', 'Pacofi', 'Aero', 'Moresby Camp', 'Sandspit', 'Skidegate', 'Queen Charlotte City', 'Masset', 'Prince Rupert'], [
  dsail('N', 'Coquitlam', 'Queen Charlotte Islands boat', 'Coquitlam', 0, [(0, T('9.00p')), (1, Wd(D1)), (2, Wd(D2)), (3, Wd(D2)), (4, Wd(D2)), (5, Wd(D3)), (6, Wd(D3)),
        (7, Wd(D3)), (8, Wd(D4)), (9, Wd(D4))],
        'S.S. Coquitlam, northbound: leaves Vancouver Monday 5 July at 9.00 p.m.; Alert Bay Tuesday, Pacofi and the Cumshewa Inlet camps Wednesday, Sandspit, Skidegate and Queen Charlotte City Thursday, Masset and Prince Rupert Friday 9 July.' + _q),
  dsail('S', 'Coquitlam', 'Vancouver boat', 'Coquitlam', 5, [(9, T('11.00p')), (8, Wd(D1)), (7, Wd(D1)), (6, Wd(D1)), (5, Wd(D1)), (4, Wd(D2)), (3, Wd(D2)), (1, Wd(D3)), (0, Wd(D4))],
        'S.S. Coquitlam, southbound: leaves Prince Rupert Saturday 10 July at 11.00 p.m.; Masset, Queen Charlotte City, Skidegate and Sandspit Sunday, the Cumshewa Inlet camps Monday, Alert Bay Tuesday, Vancouver Wednesday 14 July.' + _q)],
  ['to the Queen Charlotte Islands and Prince Rupert', 'to Vancouver'])

# ---- British Yukon Navigation Co.: the sternwheelers Whitehorse - Dawson City twice a week, and the Keno on the Stewart River (byn_1948_estimated.txt):
# a MODEL week (Brendan), looping. Downriver the boats call only at Carmacks and Fort Selkirk; upriver at every landing.
_yb = (' British Yukon Navigation Co. (White Pass & Yukon Route). A MODEL week, not a record: the White Pass table says only that sternwheel'
       ' steamers run Whitehorse - Dawson City twice a week; the days, the hours and which boat runs which trip are estimated (Brendan).'
       ' Downriver the boats call only at Carmacks and Fort Selkirk; upriver at every landing. Connects at Whitehorse with the White Pass trains.')
_up = lambda d, extra: [(8, T('~6.00a'))] + extra + [(0, T('~6.00p' if d == 3 else '~7.00p', d * 86400))]
service('byk', BYN, 'Whitehorse – Carmacks – Dawson City', 'British Yukon Navigation Co. (model)', 200,
  ['Whitehorse Landing', 'Upper Laberge', 'Lower Laberge', 'Big Salmon', 'Carmacks', 'Five Finger Rapids', 'Fort Selkirk', 'Stewart Landing', 'Dawson City'], [
  ('KD', 'Klondike', 'Dawson City boat', 'W_1000000', 'Klondike', [(0, T('~8.00p')), (4, T('~12.00p / 12.15p', D1)), (6, None), (8, T('~4.00a', D2))],
   'S.S. Klondike, downriver: Whitehorse Monday 8.00 p.m., through Lake Laberge in the night, Carmacks Tuesday noon, Five Finger Rapids, Fort Selkirk, Dawson City Wednesday 4.00 a.m.' + _yb),
  ('KU', 'Klondike', 'Whitehorse boat', 'W_0001000', 'Klondike', _up(3, [(7, T('~3.00p / 5.00p', D1)), (6, None), (5, None), (4, None), (3, None), (2, None), (1, None)]),
   'S.S. Klondike, upriver: Dawson City Thursday 6.00 a.m., Stewart Landing Friday 3.00 p.m. (picking up the ore barge), Whitehorse Sunday 6.00 p.m.' + _yb),
  ('CD', 'Casca', 'Dawson City boat', 'W_0000100', 'Casca', [(0, T('~8.00p')), (4, T('~12.00p / 12.15p', D1)), (6, None), (8, T('~4.00a', D2))],
   'S.S. Casca, downriver: Whitehorse Friday 8.00 p.m., Carmacks Saturday noon, Fort Selkirk, Dawson City Sunday 4.00 a.m.' + _yb),
  ('CU', 'Casca', 'Whitehorse boat', 'W_0000001', 'Casca', _up(4, [(7, None), (6, Wd(D1)), (5, None), (4, T('~10.00p / 11.00p', D2)), (3, None), (2, None), (1, None)]),
   'S.S. Casca, upriver: Dawson City Sunday 6.00 a.m., Fort Selkirk Monday, Carmacks Tuesday 10.00 p.m. (the wood camp), Whitehorse Thursday 7.00 p.m.' + _yb)],
  ['to Dawson City', 'to Whitehorse'])
service('bym', BYN, 'Mayo – Stewart Landing', 'British Yukon Navigation Co. (model)', 150, ['Mayo', 'Stewart Landing'], [
  ('D', 'Keno', 'Stewart River boat', 'W_0010000', 'Keno', [(0, T('~8.00a')), (1, T('~11.00a', D2))], 'S.S. Keno, down the Stewart River: Mayo Wednesday 8.00 a.m., Stewart Landing Friday 11.00 a.m. (the silver ore for the Dawson boats).' + _yb),
  ('U', 'Keno', 'Stewart River boat', 'W_0000100', 'Keno', [(1, T('~2.00p')), (0, T('~12.00p', D3))], 'S.S. Keno, up the Stewart River: Stewart Landing Friday 2.00 p.m., Mayo Monday about noon.' + _yb)],
  ['to Stewart Landing', 'to Mayo'])
# ---- the S.S. Tutshi, Carcross - Ben-My-Chree (West Taku Arm), Wednesdays and Sundays after the Skagway - Carcross excursion train No. 3
# (tutshi_1948_estimated.txt; milk run of 20 October: Tagish, Rupert, Taku Landing as landings, Tagish outward only; times by
# straight-line distance x 1.15 at 12 mph, 15 min at each landing: estimates)
_tu = (' S.S. Tutshi (British Yukon Navigation Co.), Carcross to Ben-My-Chree on West Taku Arm, Wednesdays and Sundays, after the White Pass'
       ' excursion train No. 3 from Skagway; back at Carcross in the morning for the train south. Estimated from a description of the service, not a'
       ' printed timetable (Brendan).')
service('byt', BYN, 'Carcross – Tagish – Taku Arm – Ben-My-Chree', 'British Yukon Navigation Co. (estimated)', 120, ['Carcross', 'Tagish', 'Rupert', 'Taku Landing', 'Ben-My-Chree'], [
  ('O', 'Tutshi', 'Ben-My-Chree boat', 'W_0010001', 'Tutshi', [(0, T('~12.30p')), (1, T('~2.15p / 2.30p')), (2, T('~7.20p / 7.35p')), (3, T('~8.45p / 9.00p')), (4, T('~11.40p'))],
   'S.S. Tutshi: Carcross 12.30 p.m., calling at Tagish, Rupert (for Graham Inlet) and Taku Landing, to Ben-My-Chree late in the evening.' + _tu)],
  ['to Ben-My-Chree', 'to Carcross'])
service('byr', BYN, 'Ben-My-Chree – Taku Arm – Carcross', 'British Yukon Navigation Co. (estimated)', 120, ['Carcross', 'Rupert', 'Taku Landing', 'Ben-My-Chree'], [
  ('R', 'Tutshi', 'Carcross boat', 'W_1001000', 'Tutshi', [(3, T('~2.10a')), (2, T('~4.50a / 5.05a')), (1, T('~6.15a / 6.30a')), (0, T('~10.30a'))],
   'S.S. Tutshi: back from Ben-My-Chree overnight by Taku Landing and Rupert (Tagish is called at outward only), at Carcross 10.30 a.m. (Monday and Thursday) for the train south.' + _tu)],
  ['to Ben-My-Chree', 'to Carcross'])
# ---- Barkley Sound Transportation Co., Port Alberni: the mail boats Uchuck I and Uchuck II (barkley_sound_1948_estimated.txt): the Uchuck I to
# Bamfield on Mondays, Wednesdays and Fridays, the Uchuck II to Ucluelet on Tuesdays, Thursdays and Saturdays, each out and back the same way, and
# the Uchuck I's Sunday excursion to Bamfield. A model schedule (Brendan, 15 October: the loop in Jan Peterson's account is the Uchuck I alone,
# before the Uchuck II came; it gives the speed, not the 1948 route).
_bs = (' Barkley Sound Transportation Co.: the mail and passenger boats Uchuck I (to Bamfield) and Uchuck II (to Ucluelet; bought for the 1948 season),'
       ' each leaving Port Alberni at 8.00 a.m. and back the same evening. A model schedule (Brendan): the 8.00 a.m. departure is from the British'
       ' Colonist of 18 August 1949 and the speed from Jan Peterson\'s account of the Uchuck; the hours at the calls are estimated.')
service('bsb', BST, 'Port Alberni – Bamfield (Uchuck I)', 'Barkley Sound Transportation Co. (model)', 100,
  ['Port Alberni', 'Franklin River', 'Kildonan', 'Ecoole', 'Sarita', 'Bamfield'], [
  ('U1', 'Uchuck I', 'Bamfield mail boat', 'W_1010100', 'Uchuck I', [(0, T('8.00a')), (1, None), (2, None), (3, None), (4, None), (5, T('~1.00p'))],
   'M.V. Uchuck I, Mondays, Wednesdays and Fridays: Port Alberni to Bamfield.' + _bs),
  ('R1', 'Uchuck I', 'Port Alberni mail boat', 'W_1010100', 'Uchuck I', [(5, T('~1.30p')), (4, None), (3, None), (2, None), (1, None), (0, T('~6.30p'))],
   'M.V. Uchuck I, Mondays, Wednesdays and Fridays: Bamfield back to Port Alberni.' + _bs)],
  ['to Bamfield', 'to Port Alberni'])
service('bsu', BST, 'Port Alberni – Ucluelet (Uchuck II)', 'Barkley Sound Transportation Co. (model)', 100,
  ['Port Alberni', 'Sechart', 'Broken Group', 'Ucluelet'], [
  ('U2', 'Uchuck II', 'Ucluelet mail boat', 'W_0101010', 'Uchuck II', [(0, T('8.00a')), (1, None), (2, None), (3, T('~1.30p'))],
   'M.V. Uchuck II, Tuesdays, Thursdays and Saturdays: Port Alberni to Ucluelet.' + _bs),
  ('R2', 'Uchuck II', 'Port Alberni mail boat', 'W_0101010', 'Uchuck II', [(3, T('~2.00p')), (2, None), (1, None), (0, T('~7.00p'))],
   'M.V. Uchuck II, Tuesdays, Thursdays and Saturdays: Ucluelet back to Port Alberni.' + _bs)],
  ['to Ucluelet', 'to Port Alberni'])
service('bse', BST, 'Port Alberni – Bamfield (Sunday excursion)', 'Barkley Sound Transportation Co. (model)', 100, ['Port Alberni', 'Bamfield'], [
  ('O', 'Uchuck I', 'Sunday excursion', 'W_0000001', 'Uchuck I', [(0, T('10.00a')), (1, T('~1.15p'))], 'M.V. Uchuck I, Sunday excursion: Port Alberni 10.00 a.m. direct to Bamfield (no mail, no calls).' + _bs),
  ('R', 'Uchuck I', 'Sunday excursion', 'W_0000001', 'Uchuck I', [(1, T('~3.15p')), (0, T('~6.30p'))], 'M.V. Uchuck I, Sunday excursion: Bamfield about 3.15 p.m., back at Port Alberni about 6.30 p.m.' + _bs)],
  ['to Bamfield', 'to Port Alberni'])

# ---------------- lanes
LEGS = {}
_CF = os.path.join(HERE, 'sea_legs.json'); CACHE = json.load(open(_CF)) if os.path.exists(_CF) else {}        # computed lanes, kept between builds (delete the file to redraw them)
def lane(a, b, res):
    """lon/lat points from port a to port b over the water; the same leg is reused (reversed) wherever two services share it"""
    if (a['name'], b['name']) in LEGS: return LEGS[(a['name'], b['name'])]
    if (b['name'], a['name']) in LEGS: return LEGS[(b['name'], a['name'])][::-1]
    via = VIA.get((P_NAME[a['name']], P_NAME[b['name']])) or VIA.get((P_NAME[b['name']], P_NAME[a['name']]), [])[::-1] or []
    pts = [(a['lon'], a['lat'])] + list(via) + [(b['lon'], b['lat'])]; out = []
    if frozenset((P_NAME[a['name']], P_NAME[b['name']])) in BY_HAND:            # drawn by hand through the points: the water layer is too coarse here
        LEGS[(a['name'], b['name'])] = pts; return pts
    for p, q in zip(pts, pts[1:]):
        ck = f'{SEA_VERSION}|{p[0]:.4f},{p[1]:.4f}|{q[0]:.4f},{q[1]:.4f}|{res}'
        if ck not in CACHE:
            d = math.dist(fwd(*p), fwd(*q)); S = Sea([p, q], res=res, margin=max(8000.0, 0.3 * d))
            leg, land = S.leg(p, q)
            if land > 0.02:                                               # the water route may run outside the box: look wider before accepting a short cut over land
                S2 = Sea([p, q], res=res, margin=max(30000.0, 1.2 * d)); leg2, land2 = S2.leg(p, q)
                if land2 < land: S, leg, land = S2, leg2, land2
            CACHE[ck] = [[round(x, 6), round(y, 6)] for x, y in leg]
            if land > 0.02 or max(S.snap_m(p), S.snap_m(q)) > 1500: print(f"   !! {a['name']} - {b['name']}: {land * 100:.0f}% of the lane over land in the layer; snaps {S.snap_m(p):.0f} / {S.snap_m(q):.0f} m")
        leg = [tuple(x) for x in CACHE[ck]]; out += leg if not out else leg[1:]
    LEGS[(a['name'], b['name'])] = out
    return out
P_NAME = {}
NEW = []
for D in SV:
    ports = [port(n) for n in D['seq']]
    for n, p in zip(D['seq'], ports): P_NAME[p['name']] = n
    pts = []; at = []
    for k, p in enumerate(ports):
        if k == 0: pts.append((p['lon'], p['lat'])) if p['rail'] else None
        else:
            leg = lane(ports[k - 1], p, D['res'])
            pts += leg + ([(p['lon'], p['lat'])] if p['rail'] else [])            # a lane runs up to a railway station; other ports sit on the lane
        if k == 0 and not p['rail']:
            first = lane(p, ports[1], D['res'])[0]; pts.append(first)
        at.append(len(pts) - 1)
    route = []; acc = 0.0; prev = None
    for lon, lat in pts:
        xy = fwd(lon, lat)
        if prev: acc += math.dist(xy, prev)
        prev = xy; route.append([round(lon, 6), round(lat, 6), round(acc, 1)])
    stations = [dict(name=p['name'], chain=route[i][2], lon=route[i][0], lat=route[i][1], mile=round(route[i][2] / MI, 1), lmile=round(route[i][2] / MI, 1), principal=p['principal'], kml='', gid=p['gid'],
                     **({'xy': [p['lon'], p['lat']]} if p.get('placed') else {}), note=p.get('placed') or ('Steamer landing' + ('' if p['rail'] else ' (position approximate)'))) for p, i in zip(ports, at)]
    trips = []
    for sl in D['sail']:
        tid, badge, label, svc, vessel, calls, note = sl[:7]; extra = sl[7] if len(sl) > 7 else {}
        ch = [stations[i]['chain'] for i, _ in calls]; run_ = [0.0]
        for p_, q_ in zip(ch, ch[1:]): run_.append(run_[-1] + abs(q_ - p_))        # distance run along the sailing (it may double back)
        fixed = {k: (t[0], t[1]) for k, (_, t) in enumerate(calls) if t and t[0] != 'W'}                    # printed, or estimated by hand
        printed = {k for k, (_, t) in enumerate(calls) if t and t[0] != 'W' and t[2]}
        win = {k: (t[1], t[2]) for k, (_, t) in enumerate(calls) if t and t[0] == 'W'}
        for k in (0, len(calls) - 1):                                       # a sailing that begins or ends at a call given only by its date: middle of that day
            if k not in fixed and k in win: m_ = (win[k][0] + win[k][1]) / 2; fixed[k] = (m_, m_)
        def spread(pins):
            ks = sorted(pins); out = {}
            for k in range(len(calls)):
                if k in pins: out[k] = pins[k]; continue
                ka = max(j for j in ks if j < k); kb = min(j for j in ks if j > k); t0, t1 = pins[ka][1], pins[kb][0]
                x = t0 + (t1 - t0) * (run_[k] - run_[ka]) / max(1.0, run_[kb] - run_[ka]); out[k] = (x, x)
            return out
        pins = dict(fixed)
        for _ in range(len(calls)):                                         # a call the guide puts in a half day: timed by distance, and pinned to the edge of the half day if that falls outside it
            tm = spread(pins); bad = [(max(win[k][0] - tm[k][0], tm[k][0] - win[k][1]), k) for k in win if k not in pins]
            bad = [x for x in bad if x[0] > 60]
            if not bad: break
            k = max(bad)[1]; x = min(max(tm[k][0], win[k][0]), win[k][1]); pins[k] = (x, x)
        tm = spread(pins); arr = [tm[k][0] for k in range(len(calls))]; dep = [tm[k][1] for k in range(len(calls))]
        avg = run_[-1] / max(1.0, sum(arr[k + 1] - dep[k] for k in range(len(calls) - 1)))
        VMAX = max(16.0 * MI / 3600, 1.3 * avg)                             # and no faster than the boat could go
        for k in range(len(calls) - 2, -1, -1):
            if k not in fixed and dep[k] > arr[k + 1] - (run_[k + 1] - run_[k]) / VMAX: arr[k] = dep[k] = arr[k + 1] - (run_[k + 1] - run_[k]) / VMAX
        for k in range(1, len(calls)):
            if k not in fixed and arr[k] < dep[k - 1] + (run_[k] - run_[k - 1]) / max(22.0 * MI / 3600, 1.6 * avg): arr[k] = dep[k] = dep[k - 1] + (run_[k] - run_[k - 1]) / max(22.0 * MI / 3600, 1.6 * avg)
        off = DST.get(D['op'], 0)
        stops = [[i, int(round(arr[k] / 60.0)) * 60 - off, int(round(dep[k] / 60.0)) * 60 - off, 1 if k in printed else 0] for k, (i, _) in enumerate(calls)]
        assert stops[0][1] >= 0, (D['key'], tid)
        if off: note = note + ' Hours named in this note are the guide\'s Daylight Saving Time; the list above is in standard time, an hour earlier.'
        assert all(y[1] >= x[2] for x, y in zip(stops, stops[1:])), (D['key'], tid, stops)
        d = 0 if ch[-1] > ch[0] else 1; hrs = (stops[-1][1] - stops[0][2]) / 3600; run = run_[-1] / MI
        trips.append(dict(id=f"{D['key'].upper()}-{tid}", num=badge, name=OPLABEL['lake' if D['key'] in ('bsl', 'bkl', 'bal') else D['op']], svc=svc, dir=d, stops=stops, note=note, **({'vessel': vessel} if vessel else {}), **extra))
        print(f"  {D['key']} {tid:3s} {run:6.1f} mi in {hrs:5.2f} h = {run / hrs:4.1f} mph" + ('   !! check' if not 5 < run / hrs < 24 else ''))
    NEW.append(dict(key=D['key'], kind='v', label=D['op'], mainline=True, water=True, livery=OPS[D['op']][0], src=SRC[D['op']] + (' (sailings also in CP ' + D['table'] + ')' if D['op'] == PSN and D['table'].startswith('Table') else ''), owner='cp', route=route, stations=stations,
                    dirLabels=D['dirs'], segments=[], trips=trips, _D=D))
    print(f"{D['key']}: {D['name']}, {acc / MI:.1f} mi of lane, {len(stations)} calls, {len(trips)} sailings")
json.dump(CACHE, open(_CF, 'w'))
vd['lines'] = [x for x in vd['lines'] if not x.get('water') and x['key'] != 'ste'] + [{k: v for k, v in n.items() if k != '_D'} for n in NEW]
open(os.path.join(HERE, 'viz_data.json'), 'w').write(json.dumps(vd, separators=(',', ':')))

# ---------------- GTFS (route_type 4: ferry)
def fmt(x): return f'{x // 3600:02d}:{x % 3600 // 60:02d}:{x % 60:02d}'
def app(name, rows_):
    with open(os.path.join(GT, name), 'a', newline='') as fh: csv.writer(fh).writerows(rows_)
have = set(r[0] for r in csv.reader(open(os.path.join(GT, 'calendar.txt'))))
app('calendar.txt', [r for r in [['CP_MTH', 1, 0, 0, 1, 0, 0, 0, '19490616', '19491231'], ['CP_TUE1', 0, 1, 0, 0, 0, 0, 0, '19490616', '19491231'],
                                 ['CP_THU1', 0, 0, 0, 1, 0, 0, 0, '19490616', '19491231'], ['CP_FRI1', 0, 0, 0, 0, 1, 0, 0, '19490616', '19491231'],
                                 ['CP_XMON', 0, 1, 1, 1, 1, 1, 1, '19490616', '19491231']] if r[0] not in have])
app('calendar.txt', [[w, *w[2:], '19490616', '19491231'] for w in sorted({t['svc'] for n in NEW for t in n['trips'] if t['svc'].startswith('W_')}) if w not in have])
if 'USS' not in set(r[0] for r in csv.reader(open(os.path.join(GT, 'agency.txt')))):
    app('agency.txt', [['USS', 'Union Steamships Limited', 'https://en.wikipedia.org/wiki/Union_Steamship_Company_of_British_Columbia', 'America/Vancouver', 'en', '']])
for _ag in (['GIF', 'Gulf Islands Ferry Company', 'https://en.wikipedia.org/wiki/Gulf_Islands', 'America/Vancouver', 'en', ''],
            ['NVF', 'North Vancouver Ferries', 'https://en.wikipedia.org/wiki/North_Vancouver_(city)', 'America/Vancouver', 'en', ''],
            ['HNC', 'Harbour Navigation Co.', 'https://en.wikipedia.org/wiki/Indian_Arm', 'America/Vancouver', 'en', ''],
            ['ASS', 'Alaska Steamship Company', 'https://en.wikipedia.org/wiki/Alaska_Steamship_Company', 'America/Vancouver', 'en', ''],
            ['BYN', 'British Yukon Navigation Company (White Pass & Yukon Route)', 'https://en.wikipedia.org/wiki/White_Pass_and_Yukon_Route', 'America/Vancouver', 'en', ''],
            ['BST', 'Barkley Sound Transportation Company', 'https://en.wikipedia.org/wiki/Barkley_Sound', 'America/Vancouver', 'en', '']):
    if _ag[0] not in set(r[0] for r in csv.reader(open(os.path.join(GT, 'agency.txt')))): app('agency.txt', [_ag])
if 'PSN' not in set(r[0] for r in csv.reader(open(os.path.join(GT, 'agency.txt')))):
    app('agency.txt', [['PSN', 'Puget Sound Navigation Company (Black Ball Line)', 'https://en.wikipedia.org/wiki/Puget_Sound_Navigation_Company', 'America/Vancouver', 'en', '']])
gseen = set(r[0] for r in csv.reader(open(os.path.join(GT, 'stops.txt'))))
for n in NEW:
    D = n['_D']; S_ = n['stations']; K = n['key'].upper()
    app('routes.txt', [[K, OPS[D['op']][1], D['name'], ' – '.join(dict.fromkeys(s['name'] for s in S_ if s['principal'])), 4, OPS[D['op']][2], 'FFFFFF',
                        f"{'CP ' if D['table'].startswith('Table') else ''}{D['table']}{', 1948' if D['table'].startswith('Table') else ''}. Steamer; the lane is a least-cost path over the water layer, not a surveyed course."]])
    app('stops.txt', list({s['gid']: [s['gid'], s['name'] + ' (steamer landing)', f"{s['lat']:.6f}", f"{s['lon']:.6f}", s['note']] for s in S_ if s['gid'] not in gseen}.values())); gseen |= {s['gid'] for s in S_}
    for t in n['trips']:                                                   # one shape per sailing: the part of the lane it covers, in its direction
        i0, i1 = t['stops'][0][0], t['stops'][-1][0]; lo, hi = sorted((S_[i0]['chain'], S_[i1]['chain']))
        pts_ = [p for p in n['route'] if lo - 0.5 <= p[2] <= hi + 0.5]
        if t['dir'] == 1: pts_ = pts_[::-1]
        app('shapes.txt', [[t['id'], f'{p[1]:.6f}', f'{p[0]:.6f}', k, f'{abs(p[2] - pts_[0][2]):.1f}'] for k, p in enumerate(pts_)])
        app('trips.txt', [[K, t['svc'], t['id'], S_[i1]['name'], (t.get('vessel') or 'Steamer') + ' – ' + t['name'], t['dir'], t['id']]])
        app('stop_times.txt', [[t['id'], fmt(a_), fmt(b_), S_[i]['gid'], k, f"{abs(S_[i]['chain'] - S_[i0]['chain']):.1f}", tp] for k, (i, a_, b_, tp) in enumerate(t['stops'], 1)])
