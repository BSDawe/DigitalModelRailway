"""Baltimore & Annapolis Railroad (Brendan, 25 Nov 2026): the electric line Baltimore (Camden Station) - Glen Burnie - Severna Park - Annapolis (Bladen Street). Stand-alone step
(copies ter_build.py).
Sources:
- Times and stations: the company's Official Guide entry, April 25, 1948 (Brendan's scan): 30 cars Baltimore - Annapolis and 25 back, only the end times printed, "Daylight
  Saving" time; * daily, the square daily except Sunday and holidays, k Saturday only (with "will not run holidays"). Holidays are ignored (standing rule). The 31 stations of its
  list, in order; the stations between the ends timed by distance (est.).
- Track: the Wikipedia trace of the line, with Brendan's edits (traces/maryland/Baltimore_and_Annapolis_Railroad_Brendan_Edits.kmz): the B&A route into Baltimore, the B&O
  tracks into Camden Station (trackage rights: drawn as B&O track), the Bladen Street station approach at Annapolis. Camden Station (B&O) and Bladen Street are the two ends.
- Station points: place-name points Brendan gave (25 Nov 2026: "placename, not station data"), each moved to the nearest point of the track: approximate.
Shown on the Pacific clock (Eastern Daylight less four hours). Colour: a period traction green (Brendan: green, standing out from the PRR and B&O); #3c8d40 is Claude's shade."""
import csv, json, math, os, zipfile
import xml.etree.ElementTree as ET
HERE = os.path.dirname(os.path.abspath(__file__))
GT = os.path.join(HERE, 'gtfs')
KMZ = os.path.join(HERE, 'traces', 'maryland', 'Baltimore_and_Annapolis_Railroad_Brendan_Edits.kmz')
K = '{http://www.opengis.net/kml/2.2}'
TR = {}
for p in ET.fromstring(zipfile.ZipFile(KMZ).read('doc.kml')).iter(K + 'Placemark'):
    for ls in p.iter(K + 'LineString'):
        TR[p.findtext(K + 'name').strip()] = [[float(v) for v in x.split(',')[:2]] for x in ls.findtext(K + 'coordinates').split()]
def m(a, b): return math.hypot((a[0] - b[0]) * 111320 * math.cos(math.radians((a[1] + b[1]) / 2)), (a[1] - b[1]) * 110570)
# Camden Station -> Annapolis: the B&O piece, the B&A Baltimore route, the main line (its first point is a stub past the Bladen Street junction: left off), the approach.
BO = TR['B&O Camden Station Tracks'][::-1]
pts = BO + TR['B&A Baltimre Terminal Route'][::-1][1:] + TR['Main Line'][::-1][1:-1] + TR['Bladen Street Station Approach'][::-1][1:]
route, d = [], 0.0
for k, p in enumerate(pts):
    if k: d += m(pts[k - 1], p)
    route.append([round(p[0], 7), round(p[1], 7), round(d, 1)])
TOT = route[-1][2]
BO_END = route[len(BO) - 1][2]
PLACES = [('Westport', 39.2618208, -76.6321284), ('English Consul', 39.2468786, -76.6337502), ('Rosemont', 39.2373295, -76.6346896),
          ('Baltimore Highlands', 39.2351056, -76.6329267), ('Pumphreys', 39.215278, -76.639722), ('North Linthicum', 39.21463, -76.6458179),
          ('Linthicum', 39.2023275895628, -76.65530904616111), ('Shipley', 39.1987189, -76.6563568), ('Woodlawn Heights', 39.1926079, -76.6491342),
          ('Garland', 39.1867747, -76.6383004), ('Ferndale', 39.1836637, -76.6401553), ('Glen Burnie', 39.1648, -76.6249437), ('Saunders Range', 39.1483249, -76.6143785),
          ('Oakwood', 39.1453731604711, -76.6134186045892), ('Marley', 39.13939284508374, -76.60507838351941), ('Elvaton', 39.12171463463421, -76.58973803223873),
          ('Pasadena', 39.110703363041615, -76.57826284862726), ('Earleigh Heights', 39.097572879700124, -76.56948982722079), ('Robinson', 39.0789989, -76.5530189),
          ('Severna Park', 39.070388, -76.5452409), ('Round Bay', 39.0620548, -76.5371851), ('Jones', 39.0562216, -76.5291292), ('Revell', 39.0424571, -76.5209448),
          ('Joyce', 39.0272205, -76.5211657), ('Arnold', 39.0320784, -76.5025431), ('Winchester', 39.0123669, -76.4985915), ('Severnside', 39.0017782, -76.48635),
          ('Wardour', 38.9942783, -76.4982946), ('West Annapolis', 38.9904868, -76.5021533)]
PRINCIPAL = {'Glen Burnie', 'Severna Park'}
def near(q):
    best = None
    for i in range(len(route) - 1):
        a, b = route[i], route[i + 1]; dx, dy = b[0] - a[0], b[1] - a[1]
        t = max(0, min(1, ((q[0] - a[0]) * dx + (q[1] - a[1]) * dy) / ((dx * dx + dy * dy) or 1)))
        p = (a[0] + t * dx, a[1] + t * dy); dd = m(q, p)
        if best is None or dd < best[0]: best = (dd, p, a[2] + t * (b[2] - a[2]))
    return best
def stn(name, gid, ch, p, note, principal, zname=None, city=None):
    return dict(name=name, chain=round(ch, 1), lon=round(p[0], 6), lat=round(p[1], 6), mile=round(ch / 1609.34, 2), principal=principal, gid=gid, note=note,
                zname=zname or name, city=city or name)
ST = [stn('Camden Station, Baltimore', 'BNA_BALTIMORE_CAMDEN', 0.0, route[0], 'The B&A cars reach it by trackage rights over the B&O',
          True, 'Camden Station', 'Baltimore')]
for nm, la, lo in PLACES:
    off, p, ch = near((lo, la))
    ST.append(stn(nm, 'BNA_' + nm.upper().replace(' ', '_'), ch, p, f'Placed at the track nearest the place-name point ({off:.0f} m off), approximate',
                  nm in PRINCIPAL))
    print(f'  {nm:20s} {off:5.0f} m off, mile {ch / 1609.34:5.2f}')
ST.append(stn('Annapolis (Bladen Street)', 'BNA_ANNAPOLIS', TOT, route[-1], 'Bladen Street (Brendan)', True, 'Bladen Street', 'Annapolis'))
assert all(a['chain'] < b['chain'] for a, b in zip(ST, ST[1:]))

# The Official Guide, April 25, 1948 (Eastern Daylight): (sign, leave, arrive) as 24-hour h.mm. '*' daily, 'x' daily except Sunday (the square), 'k' Saturday only.
SOUTH = ('* 1.00 1.55, x 5.00 5.55, x 6.10 7.05, * 6.40 7.35, x 7.10 8.05, * 7.40 8.35, x 8.15 9.10, * 8.45 9.40, * 9.45 10.40, * 10.45 11.40, * 11.45 12.40, '
         'k 12.15 13.09, * 12.45 13.40, k 13.15 14.10, * 13.45 14.40, k 14.15 15.10, * 14.45 15.40, k 15.15 16.10, * 15.45 16.42, x 16.15 17.10, * 16.45 17.40, '
         'x 17.15 18.13, * 17.45 18.43, x 18.15 19.12, * 18.45 19.40, * 19.45 20.40, * 20.45 21.40, * 21.45 22.40, * 22.45 23.40, * 23.45 24.40')
NORTH = ('x 5.05 6.00, x 5.35 6.30, * 6.10 7.10, x 6.40 7.40, * 7.10 8.10, x 7.40 8.40, * 8.15 9.12, * 9.15 10.11, * 10.15 11.10, * 11.15 12.10, * 12.15 13.10, '
         'k 12.45 13.45, * 13.15 14.10, * 14.15 15.10, * 15.15 16.10, x 15.45 16.46, * 16.15 17.10, x 16.45 17.45, * 17.15 18.10, * 18.15 19.10, * 19.15 20.10, '
         '* 20.15 21.10, * 21.15 22.10, * 22.15 23.10, * 23.45 24.40')
SVC = {'*': 'W_1111111', 'x': 'W_1111110', 'k': 'W_0000010'}
DAYS = {'*': 'daily', 'x': 'daily except Sunday', 'k': 'Saturday only'}
SHIFT = -4 * 3600   # Eastern Daylight to Pacific Standard
def sec(x): h, mm = x.split('.'); return int(h) * 3600 + int(mm) * 60
def ampm(s): h, mm = divmod(s // 60, 60); h %= 24; return f"{(h - 1) % 12 + 1}.{mm:02d} {'a.m.' if h < 12 else 'p.m.'}"
trips = []
for d_, block in enumerate((SOUTH, NORTH)):
    for n, col in enumerate(block.split(', ')):
        sign, a, b = col.split(); t0, t1 = sec(a), sec(b)
        seq = list(range(len(ST))) if d_ == 0 else list(range(len(ST) - 1, -1, -1))
        base = t0 + SHIFT
        if base < 0: base += 24 * 3600          # 1.00 a.m. Eastern Daylight: 9.00 p.m. Pacific the evening before (a daily car, so the days stay daily)
        assert sign == '*' or base >= t0 + SHIFT
        stops = []
        for i in seq:
            f = ST[i]['chain'] / TOT if d_ == 0 else 1 - ST[i]['chain'] / TOT
            t = base + round(f * (t1 - t0) / 60) * 60
            stops.append([i, t, t, 1 if i in (0, len(ST) - 1) else 0])
        frm, to = ('Baltimore', 'Annapolis') if d_ == 0 else ('Annapolis', 'Baltimore')
        trips.append(dict(id=f"BNA-{'SN'[d_]}-{n:02d}", num='Car', name='Baltimore & Annapolis', svc=SVC[sign], dir=d_, stops=stops, motor=True,
                          note=f'Baltimore & Annapolis car, leaves {frm} {ampm(t0)} (Eastern Daylight time, as printed), arrives {to} {ampm(t1)}; {DAYS[sign]}. '
                               f'Official Guide, April 25, 1948 (only the ends printed; the stations between timed by distance, est.). Shown in Pacific time.'))
SRC = ('Baltimore & Annapolis Railroad: Official Guide, April 25, 1948 (Brendan\'s scan); track from the Wikipedia trace with Brendan\'s edits (the B&O into Camden Station by '
       'trackage rights); station points from place names (approximate)')
LINE = dict(key='bna', kind='Z', label='Baltimore – Annapolis (Baltimore & Annapolis)', mainline=True, owner='bna', src=SRC, route=route, stations=ST,
            dirLabels=['to Annapolis', 'to Baltimore'], segments=[dict(owner='bo', a=0.0, b=round(BO_END, 1))], trips=trips)
print(f'bna: {TOT / 1609.34:.2f} mi traced ({BO_END / 1609.34:.2f} on the B&O), {len(ST)} stations, {len(trips)} trips')
vd = json.load(open(os.path.join(HERE, 'viz_data.json')))
vd['lines'] = [x for x in vd['lines'] if x['key'] != 'bna'] + [LINE]
open(os.path.join(HERE, 'viz_data.json'), 'w').write(json.dumps(vd, separators=(',', ':')))

def fmt(x): return f'{x // 3600:02d}:{x % 3600 // 60:02d}:{x % 60:02d}'
def app(name, rows_):
    with open(os.path.join(GT, name), 'a', newline='') as fh: csv.writer(fh).writerows(rows_)
def have(name, col=0): return set(r[col] for r in csv.reader(open(os.path.join(GT, name))))
cal = have('calendar.txt')
for d in sorted({t['svc'] for t in trips} - cal): app('calendar.txt', [[d, *d[2:], '19490616', '19491231']])
if 'BNA' not in have('agency.txt'): app('agency.txt', [['BNA', 'Baltimore & Annapolis Railroad', 'https://en.wikipedia.org/wiki/Baltimore_and_Annapolis_Railroad', 'America/Vancouver', 'en', '']])
seen = have('stops.txt')
app('stops.txt', [[s['gid'], s['name'], f"{s['lat']:.6f}", f"{s['lon']:.6f}", s['note']] for s in ST if s['gid'] not in seen])
app('routes.txt', [['BNA', 'BNA', 'Baltimore – Annapolis', LINE['label'], 0, '3C8D40', 'FFFFFF', SRC + '. Times on the Pacific clock.']])
app('shapes.txt', [['BNA_S', f'{p[1]:.6f}', f'{p[0]:.6f}', k, f'{p[2]:.1f}'] for k, p in enumerate(route)])
app('shapes.txt', [['BNA_N', f'{p[1]:.6f}', f'{p[0]:.6f}', k, f'{TOT - p[2]:.1f}'] for k, p in enumerate(route[::-1])])
for t in trips:
    app('trips.txt', [['BNA', t['svc'], t['id'], ST[t['stops'][-1][0]]['name'], 'Baltimore & Annapolis', t['dir'], 'BNA_' + 'SN'[t['dir']]]])
    app('stop_times.txt', [[t['id'], fmt(a), fmt(b), ST[i]['gid'], k, f"{(ST[i]['chain'] if t['dir'] == 0 else TOT - ST[i]['chain']):.1f}", tp]
                           for k, (i, a, b, tp) in enumerate(t['stops'], 1)])
