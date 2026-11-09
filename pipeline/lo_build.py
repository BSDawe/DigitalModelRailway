"""Lake Ontario boats (Brendan, 5 November 2026), and the Pointe au Baril Island Transport on Georgian Bay (7 November 2026, see below): the Canadian National steamers Toronto - Port Dalhousie (S.S. Dalhousie City and S.S. Northumberland,
meeting the Niagara, St. Catharines & Toronto cars at Port Dalhousie) and the Ontario Car Ferry Co. (CN and Baltimore & Ohio) S.S. Ontario, Cobourg - Genesee
Docks (port of Rochester, N.Y.).

Source: the May 1948 Official Guide, beside the NS&T tables (dmr-sources scans/og1948_cnq/nst_cn_steamers_condensed.png).
Steamers, "Schedule effective May 21 until June 4, inclusive", 32 miles, printed in Daylight Saving time (shown here in standard time, an hour earlier):
leave Port Dalhousie double-dagger 8.30 a.m. (daily except Saturday), ) 11.05, disc 11.05 a.m., k 4.45 (Saturday), disc 6.30, k 10.05 p.m., (May 23 only) 12.00 night;
leave Toronto disc 8.15 a.m., disc 2.00, k 2.00, square 5.45 (Friday, and May 31), k 7.30, disc 9.30 p.m. Signs (the page's footnotes, Brendan): disc Sunday
and May 24 only, ) Monday May 31 only (left out), square Friday and May 31 only, k Saturday only, double dagger daily except Saturday. Crossing 2 h 30 min,
estimated from the Saturday turns (Toronto 2.00, Port Dalhousie 4.45, Toronto 7.30, Port Dalhousie 10.05). Which ship makes which sailing is estimated (two
ships on Sundays). The 12.00 night sailing of May 23 only is left out.
Car ferry, "Ontario Car Ferry Service between Cobourg, Ont., and Genesee Docks (Port of Rochester)", Eastern time: summer service daily June 30 - Sept. 12
(spring: Sunday, Monday, Thursday and Saturday from May 29): Genesee Docks 8.00 a.m., Cobourg 1.00 p.m.; Cobourg 3.00 p.m., Genesee Docks 8.00 p.m.
Points (Brendan): Toronto CN wharf, Port Dalhousie = the CN (Welland Railway) station point, Cobourg CN wharf, Genesee Docks. Water: Brendan's basemap tiles
and the Great Lakes layer (water_east.json, for the United States side). Times shown on the Pacific clock. Run after on_build."""
import csv, json, math, os, re
from shapely.geometry import MultiPolygon, Polygon
from shapely.ops import unary_union
from nrwn_graph import fwd, MI
import sea
from sea import Sea, SEA_VERSION
HERE = os.path.dirname(os.path.abspath(__file__)); GT = os.path.join(HERE, 'gtfs'); ROOT = os.path.dirname(HERE)
vd = json.load(open(os.path.join(HERE, 'viz_data.json')))
BOX = (-79.50, -77.45, 43.10, 44.05)
PAB_BOX = (-80.60, -80.30, 45.48, 45.64)        # Pointe au Baril, Georgian Bay
MUSK_BOX = (-79.76, -79.33, 44.88, 45.29)       # the Muskoka lakes
CSL_BOX = (-79.50, -73.40, 43.10, 45.62)        # Canada Steamship Lines: Lake Ontario and the St. Lawrence to Montreal
SAG_BOX = (-73.60, -69.55, 45.45, 48.45)        # Canada Steamship Lines: Montreal - Quebec - the Saguenay
NFS_BOX = (-60.40, -58.95, 46.15, 47.65)        # the Cabot Strait: North Sydney - Port aux Basques (Newfoundland Railway steamer)
ESL_BOX = (-71.10, -65.90, 42.25, 43.95)        # the Gulf of Maine: Yarmouth - Boston (Eastern Steamship Lines)

# ---------------- water: the basemap tiles (page projection) back to lon/lat, and water_east.json
_idx = json.load(open(os.path.join(ROOT, 'basemap', 'tiles', 'index.json'))); _PJ = _idx['proj']
_r = math.pi / 180; _R = _PJ['R']; _p1, _p2, _l0 = _PJ['lat1'] * _r, _PJ['lat2'] * _r, _PJ['lon0'] * _r
_t = lambda p: math.tan(math.pi / 4 + p / 2)
_n = math.log(math.cos(_p1) / math.cos(_p2)) / math.log(_t(_p2) / _t(_p1)); _F = math.cos(_p1) * _t(_p1) ** _n / _n
def _raw(lon, lat): rho = _R * _F / _t(lat * _r) ** _n; th = _n * (lon * _r - _l0); return rho * math.sin(th), rho * math.cos(th)
_ox, _oy = _raw(*_PJ['origin'])
def page_xy(lon, lat): x, y = _raw(lon, lat); return x - _ox, y - _oy
def page_ll(x, y):
    X, Y = x + _ox, y + _oy; rho = math.copysign(math.hypot(X, Y), _n); th = math.atan2(X, Y)
    return (th / _n + _l0) / _r, (2 * math.atan((_R * _F / rho) ** (1 / _n)) - math.pi / 2) / _r
_z = _idx['zmax']; _s = _idx['side'] / 2 ** _z; _polys = []
for _B in (BOX, PAB_BOX, MUSK_BOX, CSL_BOX, SAG_BOX, NFS_BOX, ESL_BOX):
  _xs, _ys = zip(*[page_xy(lon, lat) for lon in _B[:2] for lat in _B[2:]])
  for tx in range(int((min(_xs) - _idx['origin'][0]) // _s), int((max(_xs) - _idx['origin'][0]) // _s) + 1):
      for ty in range(int((min(_ys) - _idx['origin'][1]) // _s), int((max(_ys) - _idx['origin'][1]) // _s) + 1):
          fn = os.path.join(ROOT, 'basemap', 'tiles', str(_z), f'{tx}_{ty}.json')
          if not os.path.exists(fn): continue
          for poly in json.load(open(fn))['w']:
              rings = []
              for ring in poly:
                  x, y = ring[0], ring[1]; pts = [sea.to_xy(*page_ll(x, y))]
                  for i in range(2, len(ring), 2): x += ring[i]; y += ring[i + 1]; pts.append(sea.to_xy(*page_ll(x, y)))
                  if len(pts) >= 3: rings.append(pts)
              if rings:
                  g = Polygon(rings[0], rings[1:]); _polys.append(g if g.is_valid else g.buffer(0))
for poly in json.load(open(os.path.join(HERE, 'water_east.json'))):
    rings = []
    for r in poly:
        lon, lat = r[0], r[1]; pts = [(lon / 1e4, lat / 1e4)]
        for i in range(2, len(r), 2): lon += r[i]; lat += r[i + 1]; pts.append((lon / 1e4, lat / 1e4))
        rings.append(pts)
    if not any(B[0] - 0.5 <= x <= B[1] + 0.5 and B[2] - 0.5 <= y <= B[3] + 0.5 for B in (BOX, PAB_BOX, MUSK_BOX, CSL_BOX, SAG_BOX) for x, y in rings[0]): continue
    g = Polygon([sea.to_xy(*p) for p in rings[0]], [[sea.to_xy(*p) for p in h] for h in rings[1:]]); _polys.append(g if g.is_valid else g.buffer(0))
# canals the basemap lacks (Brendan, 7 Nov 2026: the Port Carling canal failed to make the water file): the locks between the Indian River ends
from shapely.geometry import LineString
for _c in ([(-79.5742, 45.1212), (-79.5752, 45.1203), (-79.5770, 45.1197), (-79.5790, 45.1190)],):
    _polys.append(LineString([sea.to_xy(*p) for p in _c]).buffer(30))
sea._U = unary_union(_polys)
if sea._U.geom_type == 'Polygon': sea._U = MultiPolygon([sea._U])

# ---------------- ports (Brendan's points)
def dms(t):   # 45°04'13.36"N 79°29'38.27"W -> lon, lat
    a = [float(x) for x in re.findall(r"[\d.]+", t)]; return -(a[3] + a[4] / 60 + a[5] / 3600), a[0] + a[1] / 60 + a[2] / 3600
def gid(n): return 'PORT_' + re.sub(r'\W+', '_', n.upper()).strip('_')
def port(n, lon, lat, note): return dict(name=n, gid=gid(n), lon=lon, lat=lat, note=note)
TOR = port('Toronto (C.N.R. Wharf)', -79.37373709478712, 43.64070298018153, 'Canadian National wharf, Toronto harbour (Brendan)')
PDH = port('Port Dalhousie (C.N.R.)', -79.2625135, 43.2029713, 'Port Dalhousie: the CN (Welland Railway) station point, by the harbour; the NS&T cars at Lakeside Park, steps away (Brendan)')
COB = port('Cobourg (C.N.R. Wharf)', -78.1658271688718, 43.95537172092824, 'Canadian National wharf, Cobourg harbour (Brendan)')
PAB = port('Pointe au Baril (Government Wharf)', -80.37897617850626, 45.59492455033443, 'Government Wharf, Pointe au Baril, Georgian Bay; Canadian Pacific station 2 miles inland (Brendan)')
SKE = port('Skerryvore', -80.38790250561203, 45.54048159737791, 'Skerryvore, Georgian Bay (Brendan)')
BEL = port('Bellevue', -80.50219116470214, 45.55749629211946, 'Bellevue, Georgian Bay (Brendan)')
OJI = port('Ojibway', -80.45691208451146, 45.53595001144631, 'Ojibway (the Ojibway Hotel), Georgian Bay (Brendan)')
MUSKOKA_NOTE = 'Muskoka Lakes Navigation Co. steamer landing (Brendan)'
def mport(n, t): lon, lat = dms(t); return port(n, lon, lat, MUSKOKA_NOTE)
MWF = dict(name='Muskoka Wharf', gid='CN_MUSKOKA_WHARF', lon=-79.391368, lat=44.920517, note='Muskoka Wharf, Gravenhurst: the Canadian National wharf station (Brendan)')
BALA = dict(name='Bala', gid='CP_BALA', lon=-79.613611, lat=45.013662, note='Bala: the Canadian Pacific station (Brendan)')
BEA = mport('Beaumaris', '45°04\'13.36"N 79°29\'38.27"W'); PCA = mport('Port Carling', '45°07\'14.04"N 79°34\'33.37"W')
WIN = mport('Windermere', '45°09\'48.22"N 79°33\'01.95"W'); WIG = mport('Wigwassan', '45°10\'16.59"N 79°34\'18.98"W')
RMU = mport('Royal Muskoka', '45°11\'23.77"N 79°35\'51.70"W'); MIN = mport('Minett', '45°09\'54.59"N 79°38\'47.16"W')
ROS = mport('Rosseau', '45°15\'15.01"N 79°38\'24.43"W'); ELG = mport('Elgin House', '45°06\'33.00"N 79°37\'49.42"W')
NAP = mport('Natural Park', '45°12\'52.78"N 79°41\'22.70"W')
CSLN = 'Canada Steamship Lines landing (Brendan)'
TCS = port('Toronto (Canada Steamship Lines)', *dms('43°38\'22.81"N 79°22\'33.44"W'), 'Canada Steamship Lines dock, foot of Yonge Street, Toronto (Brendan)')
QUE = port('Queenston', *dms('43°09\'56.73"N 79°03\'08.39"W'), 'Queenston dock, Niagara River: the coaches to Niagara Falls (Brendan)')
NOTL = port('Niagara-on-the-Lake', *dms('43°15\'21.93"N 79°03\'44.43"W'), CSLN)
ROC = port('Rochester (Municipal Dock)', *dms('43°15\'19.39"N 77°36\'25.42"W'), 'Municipal Dock, Rochester, N.Y. (Brendan)')
KGN = port('Kingston', *dms('44°13\'39.77"N 76°28\'45.88"W'), CSLN)
ALX = port('Alexandria Bay', *dms('44°20\'18.89"N 75°55\'10.10"W'), 'Alexandria Bay, N.Y., Thousand Islands (Brendan)')
BRK = port('Brockville', *dms('44°35\'11.79"N 75°40\'57.14"W'), 'Brockville wharf (Brendan)')
PRE = port('Prescott Dock', *dms('44°42\'38.80"N 75°30\'34.68"W'), 'Prescott Dock: lake and rapids steamers change here; the Canadian Pacific dock (Brendan)')
CORN = port('Cornwall', *dms('45°00\'41.29"N 74°44\'19.48"W'), 'Cornwall, on the Cornwall Canal (Brendan)')
MTV = port('Montreal (Victoria Pier)', *dms('45°30\'33.91"N 73°32\'46.08"W'), 'Victoria Pier, Montreal harbour (Brendan)')
SOR = port('Sorel', *dms('46°02\'45.11"N 73°07\'08.22"W'), CSLN)
TRV = dict(name='Three Rivers (Ferry Wharf)', gid='TSL_THREE_RIVERS_FERRY_WHARF', lon=-72.538617, lat=46.340631, note='Three Rivers: the ferry wharf (Brendan)')
QFW = dict(name='Quebec (Ferry Wharf)', gid='QLF_QUEBEC_FERRY_WHARF', lon=-71.201614, lat=46.811832, note='Quebec: the ferry wharf (Brendan)')
MUR = port('Murray Bay', *dms('47°37\'24.64"N 70°08\'19.76"W'), CSLN)
SIM = port('St. Simeon', *dms('47°50\'23.96"N 69°52\'23.00"W'), CSLN)
TAD = port('Tadoussac', *dms('48°08\'21.41"N 69°43\'36.59"W'), CSLN)
BAG = port('Bagotville (St. Alphonse)', *dms('48°20\'41.44"N 70°52\'36.48"W'), 'St. Alphonse wharf, Bagotville, on the Saguenay (Brendan)')
GEN = port('Genesee Docks (Rochester)', -77.61655318811175, 43.22746248913674, 'Genesee Docks, Port of Rochester, N.Y., on the Genesee River (Brendan)')

# ---------------- lanes (cache lo_legs.json)
_CF = os.path.join(HERE, 'lo_legs.json'); CACHE = json.load(open(_CF)) if os.path.exists(_CF) else {}
def lane(p, q, res):
    ck = f'{SEA_VERSION}|{p[0]:.5f},{p[1]:.5f}|{q[0]:.5f},{q[1]:.5f}|{res}'
    if ck not in CACHE:
        d = math.dist(fwd(*p), fwd(*q)); S = Sea([p, q], res=res, margin=max(8000.0, 0.3 * d)); leg, land = S.leg(p, q)
        CACHE[ck] = [[round(x, 6), round(y, 6)] for x, y in leg]
        print(f'   lane {p[0]:.4f},{p[1]:.4f} - {q[0]:.4f},{q[1]:.4f}: over {land * 100:.1f}% land; snaps {S.snap_m(p):.0f} / {S.snap_m(q):.0f} m')
    return [tuple(x) for x in CACHE[ck]]
def chain(pts):
    route, acc, prev = [], 0.0, None
    for lon, lat in pts:
        xy = fwd(lon, lat)
        if prev: acc += math.dist(xy, prev)
        prev = xy; route.append([round(lon, 6), round(lat, 6), round(acc, 1)])
    return route
def water_line(a, b, res, via=()):
    seq = [(a['lon'], a['lat'])] + list(via) + [(b['lon'], b['lat'])]; pts = [seq[0]]
    for p, q in zip(seq, seq[1:]): pts += lane(p, q, res)[1:] + [q]
    route = chain(pts)
    st = [dict(name=p['name'], chain=route[i][2], lon=route[i][0], lat=route[i][1], mile=round(route[i][2] / MI, 1), lmile=round(route[i][2] / MI, 1), principal=True, kml='',
               gid=p['gid'], xy=[p['lon'], p['lat']], note=p['note']) for p, i in ((a, 0), (b, len(route) - 1))]
    return route, st
pd_route, pd_st = water_line(TOR, PDH, 120, [(-79.3600, 43.6375), (-79.3445, 43.6325), (-79.3380, 43.6260)])   # out of Toronto harbour by the Eastern Gap (the water layer lacks the Toronto Islands)
cf_route, cf_st = water_line(COB, GEN, 200)
def water_path(ports, res):   # several landings in order along one lane
    pts = [(ports[0]['lon'], ports[0]['lat'])]; idx = [0]
    for a, b in zip(ports, ports[1:]):
        q = (b['lon'], b['lat']); pts += lane((a['lon'], a['lat']), q, res)[1:] + [q]; idx.append(len(pts) - 1)
    route = chain(pts)
    st = [dict(name=p['name'], chain=route[i][2], lon=route[i][0], lat=route[i][1], mile=round(route[i][2] / MI, 1), lmile=round(route[i][2] / MI, 1), principal=True, kml='',
               gid=p['gid'], xy=[p['lon'], p['lat']], note=p['note']) for p, i in zip(ports, idx)]
    return route, st
json.dump(CACHE, open(_CF, 'w'))

# ---------------- times
def hm(txt):
    m = re.match(r'(\d+)\.(\d+)([ap])', txt); h, mn = int(m.group(1)), int(m.group(2))
    if m.group(3) == 'p' and h != 12: h += 12
    if m.group(3) == 'a' and h == 12: h = 0
    return h * 3600 + mn * 60
DST, EST = 4 * 3600, 3 * 3600          # printed daylight time: an hour to standard, three more to the Pacific clock; printed Eastern (standard): three
SVC = {'xSun': 'W_1111110', 'Sun': 'W_0000001', 'xSat': 'W_1111101', 'Sat': 'W_0000010', 'Fri': 'W_0000100', 'daily': 'W_1111111'}
DAYS = {'xSun': 'daily except Sunday', 'Sun': 'Sunday (and May 24)', 'xSat': 'daily except Saturday', 'Sat': 'Saturday', 'Fri': 'Friday (and May 31)', 'daily': 'daily'}
CROSS = 150 * 60
def ptxt(t): return f"{t // 3600 % 12 or 12}.{t % 3600 // 60:02d} {'p.m.' if t % 86400 >= 43200 else 'a.m.'}"
_s = (' Canadian National steamer service Toronto - Port Dalhousie (32 miles), May 21 to June 4, 1948 (Official Guide); for the NS&T cars to St. Catharines at Port'
      ' Dalhousie. Printed in Daylight Saving time; the crossing (2 h 30 min) and the ship on each sailing estimated.')
STEAM = [  # (from, leave as printed, days, vessel, sign as printed)
    ('P', '8.30a', 'xSat', 'Dalhousie City', 'double dagger'), ('P', '11.05a', 'Sun', 'Northumberland', 'disc'), ('P', '4.45p', 'Sat', 'Dalhousie City', 'k'),
    ('P', '6.30p', 'Sun', 'Dalhousie City', 'disc'), ('P', '10.05p', 'Sat', 'Dalhousie City', 'k'),
    ('T', '8.15a', 'Sun', 'Northumberland', 'disc'), ('T', '2.00p', 'Sun', 'Dalhousie City', 'disc'), ('T', '2.00p', 'Sat', 'Dalhousie City', 'k'),
    ('T', '5.45p', 'Fri', 'Dalhousie City', 'square'), ('T', '7.30p', 'Sat', 'Dalhousie City', 'k'), ('T', '9.30p', 'Sun', 'Northumberland', 'disc')]
LINES = []
def mkline(key, label, route, st, trips, labels, src, livery):
    LINES.append(dict(key=key, kind='v', label=label, mainline=True, water=True, livery=livery, src=src, owner='cn', route=route, stations=st, dirLabels=labels, segments=[], trips=trips))
    print(f'{key}: {label}, {route[-1][2] / MI:.1f} mi, {len(trips)} sailings')
T = []
for k, (fr, lv, dy, ves, sg) in enumerate(STEAM):
    d = 0 if fr == 'T' else 1; t = hm(lv) - DST; i0, i1 = (0, 1) if d == 0 else (1, 0)
    a, b = pd_st[i0]['name'], pd_st[i1]['name']
    T.append(dict(id=f'LOPD-{fr}{lv.replace(".", "")}{dy}', num=ves, name='C.N. steamer', svc=SVC[dy], dir=d, vessel=ves, stops=[[i0, t, t, 1], [i1, t + CROSS, t + CROSS, 0]],
                  note=f'S.S. {ves}: {a} {ptxt(hm(lv) - 3600)} standard time ({lv[:-1]} {"a.m." if lv[-1] == "a" else "p.m."} daylight time as printed, sign {sg}: {DAYS[dy]}) to {b}.' + _s))
mkline('lopd', 'Toronto – Port Dalhousie (C.N. steamers)', pd_route, pd_st, T, ['to Port Dalhousie', 'to Toronto'],
       'Canadian National steamer service, Toronto - Port Dalhousie: the May 1948 Official Guide (Brendan); daylight time printed, shown in standard time', 'cnss')
_f = (' Ontario Car Ferry Co. (Canadian National and Baltimore & Ohio), summer service daily June 30 - Sept. 12, 1948 (spring: Sun., Mon., Thu. and Sat. from May 29).'
      ' Printed in Eastern time; carries railway cars and passengers.')
CF = [dict(id='LOCF-N', num='Ontario', name='Car ferry', svc=SVC['daily'], dir=1, vessel='Ontario', stops=[[1, hm('8.00a') - EST, hm('8.00a') - EST, 1], [0, hm('1.00p') - EST, hm('1.00p') - EST, 1]],
           note='S.S. Ontario: Genesee Docks (port of Rochester, N.Y.) 8.00 a.m. to Cobourg 1.00 p.m.' + _f),
      dict(id='LOCF-S', num='Ontario', name='Car ferry', svc=SVC['daily'], dir=0, vessel='Ontario', stops=[[0, hm('3.00p') - EST, hm('3.00p') - EST, 1], [1, hm('8.00p') - EST, hm('8.00p') - EST, 1]],
           note='S.S. Ontario: Cobourg 3.00 p.m. to Genesee Docks (port of Rochester, N.Y.) 8.00 p.m.' + _f)]
mkline('locf', 'Cobourg – Genesee Docks (Ontario Car Ferry Co.)', cf_route, cf_st, CF, ['to Rochester', 'to Cobourg'],
       'Ontario Car Ferry Co. (CN and B&O), Cobourg - Genesee Docks: the May 1948 Official Guide (Brendan); Eastern time as printed', 'cnss')
for L in LINES:
    for t in L['trips']:
        if len(t['stops']) != 2: continue
        (i, a, b, _), (j, a2, b2, _) = t['stops']; leg = abs(L['stations'][j]['chain'] - L['stations'][i]['chain']) / MI; h = (a2 - b) / 3600
        assert a >= 0 and a2 > b, t['id']
        if not 7 < leg / h < 18: print(f"  {t['id']}: {leg:.1f} mi in {h:.2f} h = {leg / h:.1f} mph  !! check")
# ---------------- Pointe au Baril Island Transport (Fred G. Barned), CP guide boat schedule, June 1 - Sept. 6 (Brendan, 7 Nov 2026)
# Printed in Eastern Standard time, like CP Table 58 (the 3.45 p.m. boat leaves after train 25, Pointe au Baril 3.29 p.m.).
# TWO BOATS (Brendan: "Skerryvore and Bellevue are quite far apart, they've got to be different boats"): both leave Pointe au Baril together;
# the Skerryvore boat runs out to Skerryvore (45 minutes); the other runs Bellevue - Ojibway and back to Pointe au Baril (the Sunday evening
# "Lv Bellevue 6.30" read as its Bellevue call, arrive and leave 6.30). "Leaving times not shown are by appointment": the Skerryvore boat's
# return is estimated (leaves 15 minutes after arriving, 45 minutes back). The May tri-weekly service (Tue, Thu, Sat after train 25) is outside the summer week.
_p = (' Pointe au Baril Island Transport, operated by Fred G. Barned: June 1 to Sept. 6, 1948 (Canadian Pacific guide). Printed in Eastern Standard time;'
      ' meets the Canadian Pacific trains at Pointe au Baril. Leaving times not shown are by appointment. Two boats leave Pointe au Baril together (Brendan).')
sk_route, sk_st = water_path([PAB, SKE], 25)
oj_route, oj_st = water_path([PAB, BEL, OJI, PAB], 25)
PABT = [  # (days, leave PaB, Skerryvore, Bellevue, Ojibway ar, Ojibway lv, PaB ar)
    ('xSun', '6.30a', '7.15a', '7.15a', '7.45a', '8.00a', '9.00a'),
    ('Sun', '7.30a', '8.15a', '8.15a', '8.45a', '9.00a', '9.45a'),
    ('xSun', '3.45p', '4.30p', '4.45p', '5.00p', '6.00p', '7.30p'),
    ('Sun', '5.30p', '6.15p', '6.30p', '7.00p', '7.15p', '8.30p')]
SK, OJ = [], []
for dy, a0, sk, be, oa, ol, pa in PABT:
    t0, t1, t2, t3, t4, t6 = (hm(x) - EST for x in (a0, sk, be, oa, ol, pa)); tag = a0.replace('.', ''); r0 = t1 + 15 * 60
    SK.append(dict(id=f'PABS-{tag}{dy}', num='Skerryvore boat', name='Island boat', svc=SVC[dy], dir=0, vessel='', stops=[[0, t0, t0, 1], [1, t1, t1, 1]],
                   note=f'Island boat: Pointe au Baril {ptxt(t0 + EST)} to Skerryvore {ptxt(t1 + EST)} ({DAYS[dy]}).' + _p))
    SK.append(dict(id=f'PABS-R{tag}{dy}', num='Skerryvore boat', name='Island boat', svc=SVC[dy], dir=1, vessel='', stops=[[1, r0, r0, 0], [0, r0 + 2700, r0 + 2700, 0]],
                   note=f'Island boat: Skerryvore back to Pointe au Baril ({DAYS[dy]}), times estimated: the return is by appointment.' + _p))
    OJ.append(dict(id=f'PABO-{tag}{dy}', num='Ojibway boat', name='Island boat', svc=SVC[dy], dir=0, vessel='',
                   stops=[[0, t0, t0, 1], [1, t2, t2, 1], [2, t3, t4, 1], [3, t6, t6, 1]],
                   note=f'Island boat: Pointe au Baril {ptxt(t0 + EST)} to Bellevue {ptxt(t2 + EST)} and Ojibway {ptxt(t3 + EST)}, back to Pointe au Baril {ptxt(t6 + EST)} ({DAYS[dy]}).' + _p))
mkline('pabs', 'Pointe au Baril – Skerryvore (Island Transport)', sk_route, sk_st, SK, ['to Skerryvore', 'to Pointe au Baril'],
       'Pointe au Baril Island Transport (Fred G. Barned): the Canadian Pacific guide boat schedule, June 1 - Sept. 6 (Brendan); Eastern Standard time as printed', 'pab')
mkline('pabo', 'Pointe au Baril – Bellevue – Ojibway (Island Transport)', oj_route, oj_st, OJ, ['round the islands', 'to Pointe au Baril'],
       'Pointe au Baril Island Transport (Fred G. Barned): the Canadian Pacific guide boat schedule, June 1 - Sept. 6 (Brendan); Eastern Standard time as printed', 'pab')
# ---------------- Muskoka Lakes Navigation Co. (Brendan, 7 Nov 2026). Eastern Standard time as printed (both tables), three hours to the Pacific clock.
# CN, Official Guide April 1948 Table 126 (dmr-sources og1948_on/cn126b.png): Muskoka Wharf - Beaumaris - Port Carling - Wigwassan - Royal Muskoka.
#   Summer columns: down 7.30 a.m. (g: daily ex Sun; Sundays an hour later, June 20 - Sept. 12) and 2.00 p.m. (the 55-53 column, from June 26; the 41
#   column's 1.45 p.m. is June 14 - 24 only, left out); up Royal Muskoka 8.30 a.m. and 3.10 p.m. (daily ex Sun), 3.45 p.m. Sundays (156 column).
# CP 1948 timetable (marine/on_muskoka_lakes_1948.csv, scans/on1948/08.png), from Bala. READING (Claude, to confirm): the dagger (daily ex Sun) falls
#   exactly on Elgin House and Natural Park, the Lake Joseph landings: a Lake Joseph boat, daily ex Sunday, meets the Bala boats at Minett (11.10 a.m.,
#   3.40, 5.50 and 8.20); the two Bala boats run daily: Bala 7.30 a.m. - Rosseau 12.00, back 2.00 p.m. - Bala 7.00; Bala 2.00 p.m. - Rosseau 7.30, back
#   7.30 a.m. - Bala 11.40. Misprint read: Beaumaris "3.30 p.m." on the 2.00 p.m. boat from Rosseau (the Bala - Beaumaris time of the other boat) -> 5.30
#   estimated, between Port Carling 5.00 and Bala 7.00. The 7.30 a.m. from Bala does not call at Beaumaris (it passes).
MLNOTE = ' Muskoka Lakes Navigation Co. steamer, summer 1948. Printed in Eastern Standard time.'
def mtrips(pfx, st_names, rows, dy, d, src_note, num='Muskoka steamer'):
    out = []
    for r in rows:
        stops = []
        for k, x in enumerate(r):
            if x is None: continue
            a, b = (x if isinstance(x, tuple) else (x, x)); f = 0 if a.startswith('~') else 1
            ta, tb = hm(a.lstrip('~')) - EST, hm(b.lstrip('~')) - EST; stops.append([k if d == 0 else len(r) - 1 - k, ta, tb, f])
        first = next(x for x in r if x is not None); first = first[1] if isinstance(first, tuple) else first
        names = [st_names[k] for k, x in enumerate(r) if x is not None]
        out.append(dict(id=f'{pfx}-{"DU"[d]}{first.lstrip("~").replace(".", "")}{dy}', num=num, name='Muskoka steamer', svc=SVC[dy], dir=d, vessel='', stops=stops,
                        note=f'{names[0]} {ptxt(hm(first.lstrip("~")))} to {names[-1]} ({DAYS[dy]}), calling at ' + ', '.join(names[1:-1]) + '.' + src_note + MLNOTE))
    return out
# CN: Muskoka Wharf, Beaumaris, Port Carling, Wigwassan, Royal Muskoka
cn_route, cn_st = water_path([MWF, BEA, PCA, WIG, RMU], 40)
CNM = ' Canadian National Table 126 (Official Guide, April 1948): meets the CN trains at Muskoka Wharf.'
CN_N = [s['name'] for s in cn_st]
M = (mtrips('MLCN', CN_N, [('7.30a', '8.40a', '9.35a', '10.15a', '10.30a'), ('2.00p', '3.20p', '4.05p', '4.55p', '5.15p')], 'xSun', 0, CNM)
     + mtrips('MLCN', CN_N, [('8.30a', '9.40a', '10.35a', '11.15a', '11.30a')], 'Sun', 0, CNM + ' On Sunday an hour later than the weekday boat.')
     + mtrips('MLCN', CN_N[::-1], [('8.30a', '8.50a', '9.45a', '10.30a', '11.45a'), ('3.10p', '3.20p', '4.00p', '5.00p', '6.10p')], 'xSun', 1, CNM)
     + mtrips('MLCN', CN_N[::-1], [('3.45p', '4.00p', '4.35p', '5.25p', '6.45p')], 'Sun', 1, CNM + ' Sundays June 27 - Aug. 29, and Mondays Aug. 2 and Sept. 6.'))
mkline('mlcn', 'Muskoka Wharf – Royal Muskoka (Muskoka Lakes steamers)', cn_route, cn_st, M, ['to Royal Muskoka', 'to Muskoka Wharf'],
       'Muskoka Lakes Navigation Co.: CN Table 126, Official Guide April 25, 1948 (Brendan); Eastern Standard time as printed', 'mln')
# CP: Bala, Beaumaris, Port Carling, Windermere, Wigwassan, Royal Muskoka, Minett, Rosseau
bp_route, bp_st = water_path([BALA, BEA, PCA, WIN, WIG, RMU, MIN, ROS], 40)
CPM = ' Canadian Pacific timetable 1948: meets the CP trains at Bala.'
BP_N = [s['name'] for s in bp_st]
M = (mtrips('MLCP', BP_N, [('7.30a', None, '9.40a', '10.30a', '10.40a', '10.50a', '11.10a', '12.00p'), ('2.00p', '3.30p', '4.30p', '5.10p', '5.15p', '5.30p', '5.50p', '7.30p')], 'daily', 0,
             CPM + ' Lake Joseph passengers change at Minett (except Sunday).')
     + mtrips('MLCP', BP_N[::-1], [('2.00p', '3.40p', '4.00p', '4.15p', '4.30p', '5.00p', '~5.30p', '7.00p'), ('7.30a', '8.20a', '8.45a', '9.00a', '9.10a', '10.00a', '10.40a', '11.40a')], 'daily', 1,
             CPM + ' Lake Joseph passengers join at Minett (except Sunday). The 2.00 p.m. boat: Beaumaris printed 3.30 p.m., read 5.30 (estimated).'))
mkline('mlcp', 'Bala – Rosseau (Muskoka Lakes steamers)', bp_route, bp_st, M, ['to Rosseau', 'to Bala'],
       'Muskoka Lakes Navigation Co.: Canadian Pacific timetable 1948 (Brendan); Eastern Standard time as printed', 'mln')
# Lake Joseph boat: Minett, Elgin House, Natural Park (daily ex Sunday)
lj_route, lj_st = water_path([MIN, ELG, NAP], 40)
LJN = [s['name'] for s in lj_st]
LJM = ' Canadian Pacific timetable 1948: the Lake Joseph landings, daily except Sunday; reading (Claude): a Lake Joseph boat meeting the Bala boats at Minett.'
M = (mtrips('MLJ', LJN, [('11.10a', None, '1.05p'), ('5.50p', '6.05p', None)], 'xSun', 0, LJM)
     + mtrips('MLJ', LJN[::-1], [('2.00p', '3.10p', '3.40p'), (None, '7.45a', '8.20a')], 'xSun', 1, LJM))
mkline('mlj', 'Minett – Elgin House – Natural Park (Lake Joseph steamer)', lj_route, lj_st, M, ['to Natural Park', 'to Minett'],
       'Muskoka Lakes Navigation Co.: Canadian Pacific timetable 1948 (Brendan); Eastern Standard time as printed; Lake Joseph boat a reading', 'mln')
# ---------------- Canada Steamship Lines, Sailing Schedules Season 1948 (Brendan, 7 Nov 2026; dmr-sources scans/marine/csl_1948_*.png). Eastern Standard
# time as printed, three hours to the Pacific clock. Ports: Brendan's points. The Niagara Falls - Queenston motor coach (Canada Coach Lines) is a bus: not drawn.
def water_route(seq, res):   # ports (dicts) and waypoints (lon, lat) in order; stations at the ports
    pts = []; idx = []; prev = None
    for p in seq:
        q = (p['lon'], p['lat']) if isinstance(p, dict) else p
        if prev is None: pts.append(q)
        else: pts += lane(prev, q, res)[1:] + [q]
        if isinstance(p, dict): idx.append((p, len(pts) - 1))
        prev = q
    route = chain(pts)
    return route, [dict(name=p['name'], chain=route[i][2], lon=route[i][0], lat=route[i][1], mile=round(route[i][2] / MI, 1), lmile=round(route[i][2] / MI, 1), principal=True, kml='',
                        gid=p['gid'], xy=[p['lon'], p['lat']], note=p['note']) for p, i in idx]
GAP = [(-79.3600, 43.6375), (-79.3445, 43.6325), (-79.3380, 43.6260)]   # the Eastern Gap (the water lacks the Toronto Islands)
SVC.update({'MoFr': 'W_1111100', 'SaSu': 'W_0000011', 'SaMoWe': 'W_1010010', 'SuTuTh': 'W_0101001'})
DAYS.update({'MoFr': 'Monday to Friday', 'SaSu': 'Saturday and Sunday (and July 1, Aug. 2, Sept. 6)', 'SaMoWe': 'Saturday, Monday and Wednesday', 'SuTuTh': 'Sunday, Tuesday and Thursday'})
CSLN_ = ' Canada Steamship Lines, season 1948. Printed in Eastern Standard time.'
CSL_BOAT = {'CSQT': 'Cayuga', 'CSLK': 'Kingston', 'CSRP': 'Rapids Prince', 'CSSG': 'Bateaux Blancs'}
def ctrip(pfx, st, d, dy, calls, note):   # calls: (station index, arrive, leave); '+' = next day, '~' = estimated
    def t(x): return hm(x.lstrip('+~')) - EST + (86400 if x.startswith('+') else 0)
    stops = [[i, t(a), t(b), 0 if a.startswith('~') else 1] for i, a, b in calls]
    i0, i1 = calls[0][0], calls[-1][0]
    return dict(id=f'{pfx}-{"DU"[d]}{calls[0][2].lstrip("+~").replace(".", "")}{dy}', num=CSL_BOAT[pfx], name='C.S.L. steamer', svc=SVC[dy], dir=d, vessel=CSL_BOAT[pfx], stops=stops,
                note=f"{st[i0]['name']} {ptxt(t(calls[0][2]) + EST)} to {st[i1]['name']} ({DAYS[dy]})." + note + CSLN_)
# Toronto - Niagara-on-the-Lake - Queenston
qt_route, qt_st = water_route([TCS] + GAP + [NOTL, QUE], 80)
QN = ' The Cayuga was on this run in 1949. Queenston - Toronto steamer, with the Canada Coach Lines motor coach to and from Niagara Falls.'
M = []
for dy, rows in (('MoFr', [('7.15a', '9.20a', '9.55a'), ('5.00p', '7.00p', '7.35p')]), ('SaSu', [('7.15a', '9.20a', '9.55a'), ('1.00p', '3.15p', '3.50p'), ('8.30p', '10.30p', '11.05p')])):
    for a, b, c in rows: M.append(ctrip('CSQT', qt_st, 0, dy, [(0, a, a), (1, b, b), (2, c, c)], QN + (' June 12 to Sept. 11.' if a == '8.30p' else '')))
for dy, rows in (('MoFr', [('10.05a', '10.40a', '12.40p'), ('7.40p', '8.20p', '10.20p')]), ('SaSu', [('10.05a', '10.40a', '12.40p'), ('5.30p', '6.05p', '8.05p'), ('11.15p', None, '+1.50a')])):
    for a, b, c in rows: M.append(ctrip('CSQT', qt_st, 1, dy, [(2, a, a)] + ([(1, b, b)] if b else []) + [(0, c, c)], QN + (' June 12 to Sept. 11; no call at Niagara-on-the-Lake.' if a == '11.15p' else '')))
mkline('csqt', 'Toronto – Queenston (Canada Steamship Lines)', qt_route, qt_st, M, ['to Queenston', 'to Toronto'],
       'Canada Steamship Lines, Sailing Schedules season 1948 (Brendan); Eastern Standard time as printed', 'csl')
# the lake steamer: Toronto - Rochester - Kingston - Alexandria Bay - Brockville - Prescott Dock
lk_route, lk_st = water_route([TCS] + GAP + [ROC, KGN, ALX, BRK, PRE], 150)
LN = ' The Kingston was on this run in 1949. Toronto - Rochester - 1000 Islands - Prescott - Montreal: the lake steamer; eastbound passengers change at Prescott Dock to the rapids steamer, westbound passengers come up from Montreal by Canadian National special train (Montreal 8.50 a.m., Prescott Dock 11.40 a.m.).'
M = [ctrip('CSLK', lk_st, 0, 'SaMoWe', [(0, '1.30p', '1.30p'), (1, '8.00p', '8.45p'), (2, '+2.40a', '+3.10a'), (3, '+5.20a', '+5.20a'), (5, '+7.30a', '+7.30a')],
           LN + ' May 29, then June 2 to Sept. 18. Does not stop at Brockville eastbound.'),
     ctrip('CSLK', lk_st, 1, 'SuTuTh', [(5, '12.00p', '12.00p'), (4, '1.00p', '1.00p'), (3, '2.35p', '2.35p'), (2, '4.50p', '5.00p'), (1, '11.30p', '11.50p'), (0, '+6.45a', '+6.45a')],
           LN + ' May 31 to Sept. 20; arrives Toronto Monday, Wednesday and Friday.')]
mkline('cslk', 'Toronto – Rochester – 1000 Islands – Prescott (Canada Steamship Lines)', lk_route, lk_st, M, ['to Prescott', 'to Toronto'],
       'Canada Steamship Lines, Sailing Schedules season 1948 (Brendan); Eastern Standard time as printed', 'csl')
# the rapids steamer, downstream only: Prescott Dock - Cornwall - Montreal (Victoria Pier)
SOULANGES = [(-74.210, 45.245), (-74.185, 45.275), (-74.155, 45.298), (-74.090, 45.302), (-74.030, 45.310), (-73.975, 45.322), (-73.930, 45.345)]   # the old river past Coteau, the Cedars and the Cascades (not the Beauharnois power canal)
rp_route, rp_st = water_route([PRE, CORN] + SOULANGES + [MTV], 60)
RN = (' The rapids steamer, downstream only: shoots the Galops, Rapide du Plat and Long Sault rapids (nine miles) and the Lachine Rapids (a drop of 56 feet);'
      ' westbound passengers go back by Canadian National special train. May 30, then June 3 to Sept. 19.')
M = [ctrip('CSRP', rp_st, 0, 'SuTuTh', [(0, '7.45a', '7.45a'), (1, '11.15a', '11.15a'), (2, '6.30p', '6.30p')], RN)]
mkline('csrp', 'Prescott – Montreal: the rapids (Canada Steamship Lines)', rp_route, rp_st, M, ['to Montreal', 'to Prescott'],
       'Canada Steamship Lines, Sailing Schedules season 1948 (Brendan); Eastern Standard time as printed', 'csl')
# Montreal - Quebec - Murray Bay - Tadoussac - the Saguenay (Brendan, 7 Nov 2026), daily both ways, two nights' sailing each way (two ships each way)
sg_route, sg_st = water_route([MTV, SOR, TRV, QFW, MUR, SIM, TAD, BAG], 120)
SN = ' One of the Bateaux Blancs, the white fleet of Saguenay steamers. Montreal - Quebec - Murray Bay - Tadoussac - Saguenay: daily from late May to late September.'
M = [ctrip('CSSG', sg_st, 0, 'daily', [(0, '6.45p', '6.45p'), (1, '9.45p', '9.45p'), (2, '+12.15a', '+12.15a'), (3, '+5.30a', '+7.30a'), (4, '+12.00p', '+1.00p'), (5, '+2.30p', '+2.30p'),
                                       (6, '+4.30p', '+5.30p'), (7, '+9.15p', '+9.15p')], SN),
     ctrip('CSSG', sg_st, 1, 'daily', [(7, '6.00a', '6.00a'), (6, '9.35a', '9.50a'), (5, '11.50a', '11.50a'), (4, '1.10p', '1.25p'), (3, '6.00p', '6.30p'), (2, '11.30p', '11.30p'),
                                       (1, '+2.15a', '+2.15a'), (0, '+7.00a', '+7.00a')], SN)]
mkline('cssg', 'Montreal – Quebec – the Saguenay (Canada Steamship Lines)', sg_route, sg_st, M, ['to the Saguenay', 'to Montreal'],
       'Canada Steamship Lines, Sailing Schedules season 1948 (Brendan); Eastern Standard time as printed', 'csl')

# North Sydney - Port aux Basques, the Newfoundland Railway steamer (Official Guide, April 25, 1948, CN page 1115; Brendan, 8 Nov 2026: a Newfoundland Railway service,
# from the end of the North Sydney track to his Port aux Basques point, where the railway ends too). North Sydney sails Sat., Tues., Thurs. 8.30 p.m. Atlantic, Port aux
# Basques 6.00 a.m. Newfoundland time (Atlantic + 30 min.); back Wed., Fri. 9.00 p.m. and Mon. 10.00 a.m. Newfoundland time, North Sydney 5.30 a.m. / 6.30 p.m. Atlantic.
def _gid_of(key, name):
    for L_ in vd['lines']:
        if L_['key'] == key:
            for s_ in L_['stations']:
                if s_['name'] == name: return s_['gid']
NSY = port('North Sydney', -60.2456, 46.2091, 'North Sydney: the end of the North Sydney track (Brendan, 8 Nov 2026), with the Canadian National trains.')
PAQ = port('Port aux Basques', -59.1423107, 47.5807910, "Port aux Basques terminal (Brendan's point, 8 Nov 2026), with the Newfoundland Railway trains.")
NSY['gid'] = _gid_of('oncn005', 'North Sydney') or NSY['gid']; PAQ['gid'] = _gid_of('onnfr001', 'Port-aux-Basques') or PAQ['gid']
ns_route, ns_st = water_route([NSY, PAQ], 150)
SVC.update({'SaTuTh': 'W_0101010', 'WeFr': 'W_0010100', 'Mo': 'W_1000000'}); DAYS.update({'SaTuTh': 'Saturday, Tuesday and Thursday', 'WeFr': 'Wednesday and Friday', 'Mo': 'Monday'})
NN = (' Newfoundland Railway steamer across the Cabot Strait, connecting with the Canadian National trains at North Sydney and the Newfoundland Railway at Port aux Basques.'
      ' Printed in Atlantic time at North Sydney and Newfoundland time (half an hour later) at Port aux Basques.')
def _ns(d, dy, a, b, txt): return dict(id=f'NFSS-{"DU"[d]}{dy}', num='Steamer', name='Newfoundland Railway steamer', svc=SVC[dy], dir=d, vessel='Steamer',
                                       stops=[[0 if d == 0 else 1, a, a, 1], [1 if d == 0 else 0, b, b, 1]], note=txt + NN)
NS = [_ns(0, 'SaTuTh', hm('8.30p') - 4 * 3600, 86400 + hm('6.00a') - 4 * 3600 - 1800, 'North Sydney Sat., Tues. and Thurs. 8.30 p.m. to Port aux Basques 6.00 a.m. (Newfoundland time) Sun., Wed. and Fri.'),
      _ns(1, 'WeFr', hm('9.00p') - 4 * 3600 - 1800, 86400 + hm('5.30a') - 4 * 3600, 'Port aux Basques Wed. and Fri. 9.00 p.m. (Newfoundland time) to North Sydney 5.30 a.m. Thurs. and Sat.'),
      _ns(1, 'Mo', hm('10.00a') - 4 * 3600 - 1800, hm('6.30p') - 4 * 3600, 'Port aux Basques Monday 10.00 a.m. (Newfoundland time) to North Sydney 6.30 p.m.')]
mkline('nfss', 'North Sydney – Port aux Basques (Newfoundland Railway steamer)', ns_route, ns_st, NS, ['to Port aux Basques', 'to North Sydney'],
       'Newfoundland Railway steamer, North Sydney - Port aux Basques: CN page 1115, Official Guide, April 25, 1948 (Brendan); Atlantic / Newfoundland time as printed', 'nfr')

# Yarmouth - Boston, Eastern Steamship Lines (CN Table 9, Official Guide, April 25, 1948, page 1115; Brendan, 8 Nov 2026: India Wharf, Boston, and his Yarmouth point).
# June 3 - Sept. 26: Yarmouth Tues., Thurs., Sun. 6.30 p.m. Atlantic time, Boston 7.30 a.m. Eastern time (taken as standard, Atlantic - 1 h); June 2 - Sept. 24: Boston
# Mon., Wed., Fri. 3.30 p.m. Eastern, Yarmouth 7.30 a.m. Atlantic. The May 28 / 31 sailings are outside the modelled week.
YAR = port('Yarmouth', -66.12249900355755, 43.83744377078616, "Yarmouth, N.S. (Brendan's point), with the Canadian National trains (Lovitt Street wharf on boat days).")
BOS = port('Boston (India Wharf)', -71.04892582977378, 42.358478309966216, "India Wharf, Boston (Brendan's point, 8 Nov 2026), Eastern Steamship Lines.")
YAR['gid'] = _gid_of('oncn009', 'Yarmouth') or YAR['gid']
es_route, es_st = water_route([YAR, BOS], 150)
SVC.update({'TuThSu': 'W_0101001', 'MoWeFr': 'W_1010100'}); DAYS.update({'TuThSu': 'Tuesday, Thursday and Sunday', 'MoWeFr': 'Monday, Wednesday and Friday'})
EN = ' Eastern Steamship Lines, Yarmouth - Boston (summer 1948). Printed in Atlantic time at Yarmouth, Eastern time at Boston.'
ES = [dict(id='ESL-DTuThSu', num='Steamer', name='Eastern Steamship Lines', svc=SVC['TuThSu'], dir=0, vessel='Steamer', stops=[[0, hm('6.30p') - 4 * 3600, hm('6.30p') - 4 * 3600, 1], [1, 86400 + hm('7.30a') - 3 * 3600, 86400 + hm('7.30a') - 3 * 3600, 1]],
           note='Yarmouth Tues., Thurs. and Sun. 6.30 p.m. (June 3 - Sept. 26) to Boston (India Wharf) 7.30 a.m.' + EN),
      dict(id='ESL-UMoWeFr', num='Steamer', name='Eastern Steamship Lines', svc=SVC['MoWeFr'], dir=1, vessel='Steamer', stops=[[1, hm('3.30p') - 3 * 3600, hm('3.30p') - 3 * 3600, 1], [0, 86400 + hm('7.30a') - 4 * 3600, 86400 + hm('7.30a') - 4 * 3600, 1]],
           note='Boston (India Wharf) Mon., Wed. and Fri. 3.30 p.m. (June 2 - Sept. 24) to Yarmouth 7.30 a.m.' + EN)]
mkline('esl', 'Yarmouth – Boston (Eastern Steamship Lines)', es_route, es_st, ES, ['to Boston', 'to Yarmouth'],
       'Eastern Steamship Lines, Yarmouth - Boston: CN Table 9, Official Guide, April 25, 1948 (Brendan); Atlantic / Eastern time as printed', 'esl')
keys = {L['key'] for L in LINES}
vd['lines'] = [x for x in vd['lines'] if x['key'] not in keys] + LINES
open(os.path.join(HERE, 'viz_data.json'), 'w').write(json.dumps(vd, separators=(',', ':')))

# ---------------- GTFS (ferry, route type 4)
def fmt(x): return f'{x // 3600:02d}:{x % 3600 // 60:02d}:{x % 60:02d}'
def app(name, rows_):
    with open(os.path.join(GT, name), 'a', newline='') as fh: csv.writer(fh).writerows(rows_)
def have(name, col=0): return set(r[col] for r in csv.reader(open(os.path.join(GT, name))))
cal = have('calendar.txt'); app('calendar.txt', [[w, *w[2:], '19490616', '19491231'] for w in sorted({t['svc'] for L in LINES for t in L['trips']}) if w not in cal])
if 'PABIT' not in have('agency.txt'): app('agency.txt', [['PABIT', 'Pointe au Baril Island Transport (Fred G. Barned)', 'https://en.wikipedia.org/wiki/Pointe_au_Baril', 'America/Vancouver', 'en', '']])
if 'CSL' not in have('agency.txt'): app('agency.txt', [['CSL', 'Canada Steamship Lines', 'https://en.wikipedia.org/wiki/Canada_Steamship_Lines', 'America/Vancouver', 'en', '']])
if 'MLN' not in have('agency.txt'): app('agency.txt', [['MLN', 'Muskoka Lakes Navigation and Hotel Co.', 'https://en.wikipedia.org/wiki/Muskoka_Lakes_Navigation_Company', 'America/Vancouver', 'en', '']])
if 'ESL' not in have('agency.txt'): app('agency.txt', [['ESL', 'Eastern Steamship Lines', 'https://en.wikipedia.org/wiki/Eastern_Steamship_Lines', 'America/Vancouver', 'en', '']])
if 'OCF' not in have('agency.txt'): app('agency.txt', [['OCF', 'Ontario Car Ferry Company (Canadian National and Baltimore & Ohio)', 'https://en.wikipedia.org/wiki/SS_Ontario_No._1', 'America/Vancouver', 'en', '']])
gseen = have('stops.txt')
_PDESC = 'Island boat, June 1 - Sept. 6, 1948. Times on the Pacific clock, three hours earlier than the Eastern Standard time printed.'
_MDESC = 'Muskoka Lakes Navigation Co. steamer, summer 1948. Times on the Pacific clock, three hours earlier than the Eastern Standard time printed.'
for L, ag, desc in ((LINES[0], 'CN', 'Canadian National steamers, May 21 - June 4, 1948. Times on the Pacific clock (printed in Eastern Daylight Saving time).'),
                    (LINES[1], 'OCF', 'S.S. Ontario, summer service. Times on the Pacific clock, three hours earlier than the Eastern time printed.'),
                    (LINES[2], 'PABIT', _PDESC), (LINES[3], 'PABIT', _PDESC), (LINES[4], 'MLN', _MDESC), (LINES[5], 'MLN', _MDESC), (LINES[6], 'MLN', _MDESC),
                    *((L_, 'CSL', 'Canada Steamship Lines, season 1948. Times on the Pacific clock, three hours earlier than the Eastern Standard time printed.') for L_ in LINES[7:11]),
                    (LINES[11], 'NFR', 'Newfoundland Railway steamer, North Sydney - Port aux Basques. Times on the Pacific clock (printed in Atlantic time at North Sydney, Newfoundland time at Port aux Basques).'),
                    (LINES[12], 'ESL', 'Eastern Steamship Lines, Yarmouth - Boston. Times on the Pacific clock (printed in Atlantic time at Yarmouth, Eastern time at Boston).')):
    rid = L['key'].upper(); st = L['stations']
    app('routes.txt', [[rid, ag, L['label'], ' – '.join(s['name'] for s in st), 4, {'PABIT': '8B4A2B', 'MLN': '1F4E79', 'CSL': 'D93A1C'}.get(ag, '2F6B44'), 'FFFFFF', desc]])
    new = [[s['gid'], s['name'] + ' (steamer landing)', f"{s['lat']:.6f}", f"{s['lon']:.6f}", s['note']] for s in st if s['gid'] not in gseen]
    gseen |= {r[0] for r in new}; app('stops.txt', new)
    for t in L['trips']:
        i0, i1 = t['stops'][0][0], t['stops'][-1][0]
        pts_ = [p for p in L['route'] if min(st[i0]['chain'], st[i1]['chain']) - 0.05 <= p[2] <= max(st[i0]['chain'], st[i1]['chain']) + 0.05]
        if i0 > i1: pts_ = pts_[::-1]
        app('shapes.txt', [[t['id'], f'{p[1]:.6f}', f'{p[0]:.6f}', k, f'{abs(p[2] - pts_[0][2]):.1f}'] for k, p in enumerate(pts_)])
        app('trips.txt', [[rid, t['svc'], t['id'], st[i1]['name'], t['num'], t['dir'], t['id']]])
        app('stop_times.txt', [[t['id'], fmt(a_), fmt(b_), st[i]['gid'], k, f"{abs(st[i]['chain'] - st[i0]['chain']):.1f}", tp] for k, (i, a_, b_, tp) in enumerate(t['stops'], 1)])
