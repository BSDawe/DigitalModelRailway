"""Portland Traction Company, Portland Railroad and Terminal Division: the Oregon City and Gresham Divisions (Brendan, 24 Nov 2026: "an additional interurban").
Stand-alone step (copies ter_build.py).
Sources (Brendan: "WX4.org for the timetables, Mississippi Rails for the trace"):
- Times and stations: Time Table No. 2, effective February 1, 1948, Oregon City Division and Gresham Division (scans from WX4.org via Brendan; private repo scans/ptc/). Pacific
  Standard Time. Transcribed below as printed (the timing points); the other stations of each list (with its miles) are timed by distance between them (estimated). Oregon City:
  Moorage and Harney Avenue have no miles printed: placed half-way (Claude).
- Track: Mississippi Rails (Tony Howe and David Price) Portland Railway, Light & Power Co. KMZ via Brendan (raw in the private repo, traces/oregon/), each line joined from its
  pieces (traces/oregon/portland_traction_oregon_city.json, portland_traction_gresham.json): 1st & Washington - Hawthorne Bridge - East Portland - The Oaks - Golf Junction, then
  Milwaukie - Oregon City (14.0 mi traced, 13.94 printed) or Lents - Bellrose - Linneman Junction - Gresham (17.2 mi traced, 18.45 printed; the Gresham (Mt. Hood) depot end
  APPROXIMATE). Stations placed by the printed miles, stretched to the track between Portland, Golf Junction and the far end; Portland, East Portland and Golf Junction are shared.
Signs, Oregon City: X daily except Sunday; XX daily except Saturday and Sunday; O Oak Grove local; M Milwaukie local; E East Portland only; L leaves East Portland 10 minutes before
the Golf Jct. time; * no stops north of Oak Grove except to pick up (southbound; the minor stops north of Oak Grove are left out); + likewise north of Island; # limited to Lakewood.
"All Oak Grove trains make local stops on Saturday; all Oregon City trains make local stops on Sunday" (not modelled). Gresham: * daily except Sunday; ** daily except Saturday and
Sunday; S / B / K Stanley / Bell / Kendall only; G Gresham; L limited to Wichita; @ (the star) leave East Portland 10 minutes earlier; s arrive East Portland 10 minutes later.
Rows without a Portland time begin (or end) at Golf Jct. Colour #2f6f8f is Claude's pick."""
import csv, json, math, os
HERE = os.path.dirname(os.path.abspath(__file__))
GT = os.path.join(HERE, 'gtfs')
def km(a, b): return math.hypot((a[0] - b[0]) * 111.32 * math.cos(math.radians((a[1] + b[1]) / 2)), (a[1] - b[1]) * 110.57)
def load(fn):
    tr = json.load(open(os.path.join(HERE, 'traces', 'oregon', fn))); route, d = [], 0.0
    for k, p in enumerate(tr['coords']):
        if k: d += km(tr['coords'][k - 1], p) * 1000
        route.append([p[0], p[1], round(d, 1)])
    return route
NOTE = {'Portland': 'Portland, S.W. 1st Avenue and Washington Street', 'East Portland': 'East Portland, S.E. 1st Avenue and Hawthorne Boulevard',
        'Oregon City': 'Oregon City, 5th and Main Streets (the timetable\'s miles, 13.94, are to 3rd and Main)', 'Gresham': 'Gresham, the Mt. Hood depot (position approximate: the end of the traced line)'}
def place(route, ST, end_mi, div):
    TOT = route[-1][2]; at = lambda q: min(route, key=lambda p: km(p, q))[2]
    # anchors: printed miles -> metres along the track (Brendan, 24 Nov 2026: Linneman Jct. at the real junction; Oregon City's miles are to 3rd and Main, the cars run on to 5th)
    A = [(0, 0.0), (5.02, at((-122.6538, 45.4584)))]
    A += [(14.89, at((-122.4717, 45.4879))), (end_mi, TOT)] if div == 'gr' else [(13.94, TOT - 130.0)]
    def chain_of(mi):
        for (m0, c0), (m1, c1) in zip(A, A[1:]):
            if mi <= m1: return c0 + (mi - m0) / (m1 - m0) * (c1 - c0)
        return A[-1][1]
    out = []
    for nm, mi, col in ST:
        ch = TOT if nm == 'Oregon City' else chain_of(mi)
        j = max(i for i in range(len(route)) if route[i][2] <= ch); a, b = route[j], route[min(j + 1, len(route) - 1)]
        f = (ch - a[2]) / ((b[2] - a[2]) or 1)
        note = NOTE.get(nm, nm) + ('; placed by the printed miles (approximate)' if nm not in ('Portland', 'Oregon City', 'Gresham', 'Linneman Junction') else '')
        if nm == 'Linneman Junction': note = 'Linneman Junction: the junction of the Gresham and Cazadero lines (the trace)'
        if nm in ('Moorage', 'Harney Avenue'): note = nm + ': no miles printed; placed half-way between its neighbours (approximate)'
        out.append(dict(name=nm, chain=round(ch, 1), lon=round(a[0] + f * (b[0] - a[0]), 6), lat=round(a[1] + f * (b[1] - a[1]), 6), mile=mi,
                        principal=col is not None or nm == 'East Portland', gid='PTC_' + nm.upper().replace('.', '').replace(' ', '_'), note=note, zname=nm, city=nm))
    return out
# ---------------- Oregon City Division ----------------
OC_ST = [('Portland', 0, 'P'), ('East Portland', 0.81, None), ('Moorage', 2.37, None), ('The Oaks', 3.92, None), ('Chutes', 4.14, None), ('Spokane Ave.', 4.41, None),
      ('Harney Avenue', 4.72, None), ('Golf Junction', 5.02, 'G'), ('Ardgour', 5.45, None), ('Overlinks', 5.68, None), ('Knight', 5.96, None), ('Hendee', 6.07, None),
      ('Milwaukie', 6.31, 'M'), ('Island', 6.71, None), ('Lakewood', 7.14, None), ('Evergreen', 7.36, None), ('Silver Springs', 7.59, None), ('Torbank', 7.79, None),
      ('Courtney', 7.96, None), ('St. Theresa', 8.15, None), ('Oak Grove', 8.35, 'O'), ('Rupert', 8.75, None), ('Risley', 8.94, None), ('Concord', 9.19, None),
      ('Vinyard', 9.53, None), ('Naef', 9.86, None), ('Rothe', 10.07, None), ('Ashdale', 10.35, None), ('Jennings Lodge', 10.68, None), ('Hull Avenue', 10.84, None),
      ('Meldrum', 11.01, 'D'), ('Glen Echo', 11.14, None), ('Fern Ridge', 11.43, None), ('Gladstone', 11.95, 'S'), ('Park Place', 12.34, None), ('Oregon City', 13.94, 'C')]
# Portland to Oregon City: sign, then P G M O D S C ('-' not served). Times h.mm, 24-hour from the light (a.m.) / dark (p.m.) face.
SOUTH = '''
 | 0.35 0.50 0.54 1.01 1.08 1.11 1.20
 | 1.35 1.50 1.54 2.01 2.08 2.11 2.20
 | 3.35 3.50 3.54 4.01 4.08 4.11 4.20
 | - 4.50 4.54 5.01 5.08 5.11 5.20
X | - 5.15 5.19 5.26 5.33 5.36 5.45
 | 5.30 5.46 5.50 5.57 6.04 6.07 6.16
X | - 6.15 6.19 6.26 6.33 6.36 6.45
OXXL | - 6.32 6.36 6.43 - - -
 | 6.30 6.46 6.50 6.57 7.04 7.07 7.16
OXXL | - 6.56 7.00 7.07 - - -
X | 7.00 7.16 7.20 7.27 7.34 7.37 7.46
OXX | 7.20 7.36 7.40 7.47 - - -
 | 7.30 7.46 7.51 7.57 8.04 8.08 8.17
X | 8.00 8.16 8.20 8.27 8.34 8.37 8.46
 | 8.30 8.46 8.50 8.57 9.04 9.07 9.16
 | 9.00 9.16 9.20 9.27 9.34 9.37 9.46
 | 9.30 9.46 9.50 9.57 10.04 10.07 10.16
 | 10.00 10.16 10.20 10.27 10.34 10.37 10.46
 | 10.30 10.46 10.50 10.57 11.04 11.07 11.16
 | 11.00 11.16 11.20 11.27 11.34 11.37 11.46
 | 11.30 11.46 11.50 11.57 12.04 12.07 12.16
 | 12.01 12.16 12.20 12.27 12.34 12.37 12.46
 | 12.30 12.46 12.50 12.57 13.04 13.07 13.16
 | 13.00 13.16 13.20 13.27 13.34 13.37 13.46
 | 13.30 13.46 13.50 13.57 14.04 14.07 14.16
 | 14.00 14.16 14.20 14.27 14.34 14.37 14.46
 | 14.30 14.46 14.50 14.57 15.04 15.07 15.16
 | 15.00 15.16 15.21 15.29 15.36 15.40 15.50
* | 15.30 15.45 15.50 15.56 16.03 16.07 16.20
OX | 15.35 15.51 15.58 16.07 - - -
+ | 16.00 16.16 16.20 16.27 16.35 16.39 16.50
MX | 16.05 16.21 16.26 - - - -
# | 16.30 16.46 16.50 16.57 17.06 17.10 17.20
OX | 16.35 16.51 16.56 17.03 - - -
* | 17.00 17.16 17.20 17.27 17.35 17.39 17.50
OX+ | 17.05 17.21 17.25 17.33 - - -
MXX | 17.10 17.26 17.30 - - - -
* | 17.30 17.46 17.50 17.58 18.06 18.10 18.20
OX+ | 17.35 17.51 17.55 18.03 - - -
MXX | 17.40 17.56 18.00 - - - -
* | 18.00 18.16 18.20 18.27 18.35 18.39 18.50
OX | 18.05 18.21 18.25 18.33 - - -
 | 18.30 18.46 18.50 18.57 19.04 19.07 19.18
 | 19.00 19.16 19.20 19.27 19.34 19.37 19.48
 | 19.30 19.46 19.50 19.57 20.04 20.07 20.18
 | 20.00 20.15 20.19 20.28 20.35 20.39 20.48
 | 20.30 20.46 20.51 20.58 21.05 21.09 21.18
 | 21.30 21.46 21.51 21.58 22.05 22.09 22.18
 | 22.30 22.46 22.51 22.58 23.05 23.09 23.18
 | 23.30 23.46 23.51 23.58 24.05 24.09 24.18'''
# Oregon City to Portland: sign, then C S D O M G P
NORTH = '''
 | 0.35 0.46 0.50 0.57 1.04 1.08 1.24
E | 1.28 1.37 1.40 1.47 1.54 1.58 -
 | 2.30 2.41 2.44 2.52 2.58 3.02 3.20
 | 4.30 4.41 4.44 4.52 4.58 5.02 5.20
 | 5.30 5.40 5.44 5.53 6.00 6.04 6.20
X | 6.00 6.11 6.15 6.24 6.31 6.35 6.51
OXX | - - - 6.48 6.54 6.59 7.15
 | 6.30 6.40 6.44 6.53 7.00 7.04 7.20
OXX | - - - 7.17 7.24 7.28 7.45
X | 7.00 7.11 7.15 7.24 7.31 7.35 7.51
 | 7.20 7.30 7.34 7.43 7.51 7.55 8.11
OXX | - - - 7.55 8.02 8.06 8.22
X | 8.00 8.12 8.16 8.25 8.32 8.36 8.53
 | 8.30 8.41 8.45 8.54 9.01 9.05 9.25
X | 9.00 9.11 9.15 9.24 9.31 9.35 9.55
 | 9.30 9.41 9.45 9.54 10.01 10.05 10.25
 | 10.00 10.11 10.15 10.24 10.31 10.35 10.55
 | 10.30 10.41 10.45 10.54 11.01 11.05 11.25
 | 11.00 11.11 11.15 11.24 11.31 11.35 11.55
 | 11.30 11.41 11.45 11.54 12.01 12.05 12.25
 | 12.01 12.11 12.15 12.24 12.31 12.35 12.55
 | 12.30 12.41 12.45 12.54 13.01 13.05 13.25
 | 13.00 13.11 13.15 13.24 13.31 13.35 13.55
 | 13.30 13.41 13.45 13.54 14.01 14.05 14.25
 | 14.00 14.11 14.15 14.24 14.31 14.35 14.55
 | 14.30 14.41 14.45 14.54 15.01 15.05 15.25
 | 15.00 15.11 15.15 15.25 15.32 15.37 15.55
 | 15.33 15.44 15.48 15.56 16.03 16.08 16.25
OX | - - - 16.12 16.20 16.24 16.40
 | 16.00 16.11 16.15 16.24 16.31 16.36 16.55
MX | - - - - 16.35 16.40 17.00
 | 16.30 16.40 16.44 16.53 17.00 17.04 17.25
OX | - - - 17.08 17.14 17.18 17.36
 | 17.00 17.10 17.14 17.23 17.30 17.34 17.52
MXX | - - - - 17.35 17.40 17.58
OXE | - - - 17.39 17.45 17.49 -
 | 17.30 17.40 17.44 17.53 18.00 18.05 18.25
MXEX | - - - - 18.05 18.09 -
OXE | - - - 18.09 18.15 18.19 -
 | 18.00 18.10 18.14 18.23 18.30 18.34 18.50
OXE | - - - 18.38 18.45 18.49 -
 | 18.30 18.40 18.44 18.53 19.00 19.04 19.25
 | 19.00 19.11 19.15 19.24 19.31 19.35 19.50
 | 19.30 19.41 19.45 19.54 20.01 20.05 20.20
 | 20.00 20.11 20.15 20.24 20.31 20.35 20.50
 | 20.30 20.39 20.42 20.50 20.56 21.00 21.20
 | 21.00 21.09 21.12 21.20 21.26 21.30 21.48
 | 21.30 21.39 21.42 21.50 21.56 22.00 22.20
 | 22.30 22.39 22.42 22.50 22.56 23.00 23.20
 | 23.30 23.39 23.42 23.50 23.56 23.59 24.20'''
# ---------------- Gresham Division ----------------
GR_ST = [('Portland', 0, 'P'), ('East Portland', 0.81, None), ('Golf Junction', 5.02, 'G'), ('East Seventeenth St.', 5.37, None), ('Sellwood Gardens', 5.64, None),
      ('Ardenwald', 6.06, 'A'), ('Berkeley', 6.53, None), ('Errol', 6.91, None), ('Brookwild', 7.22, None), ('Stanley', 7.54, 'T'), ('Wichita', 7.76, None), ('Bell', 8.15, 'B'),
      ('Luther', 8.70, None), ('Kendall', 9.04, 'K'), ('Somerfeldt', 9.28, None), ('Watson', 9.71, None), ('Lents', 10.34, None), ('Arnaud', 10.81, None),
      ('Kirkpatrick', 11.11, None), ('Gilbert', 11.39, None), ('Ramapo', 11.67, None), ('Bellrose', 12.10, 'R'), ('Wilson', 12.52, None), ('Sycamore', 13.21, None),
      ('Jenne', 14.14, None), ('Linneman Junction', 14.89, None), ('Gresham', 18.45, 'H')]
# Portland to Bellrose and Gresham: sign, then P G A T B K R H
GSOUTH = '''
 | 0.30 0.45 0.48 0.51 0.54 0.56 1.03 -
@ | - 5.05 5.08 5.11 5.13 5.15 5.22 -
 | - 5.36 5.40 5.44 5.46 5.48 5.55 -
G@ | - 6.01 6.04 6.08 6.11 6.13 6.20 6.35
@ | - 6.07 6.11 6.14 6.17 6.19 6.25 -
B** | 6.20 6.36 6.39 6.44 6.46 - - -
 | 6.45 7.01 7.05 7.09 7.11 7.14 7.22 -
* | 7.15 7.31 7.35 7.38 7.41 7.43 7.52 -
 | 7.45 8.01 8.05 8.08 8.11 8.14 8.22 -
* | 8.45 9.01 9.05 9.08 9.11 9.14 9.22 -
G | 9.15 9.31 9.35 9.38 9.41 9.43 9.52 10.06
* | 10.15 10.31 10.35 10.38 10.41 10.43 10.52 -
 | 11.15 11.31 11.35 11.38 11.41 11.43 11.52 -
* | 11.45 12.01 12.05 12.08 12.11 12.13 12.22 -
 | 12.45 13.01 13.05 13.08 13.11 13.13 13.22 -
 | 14.15 14.31 14.35 14.38 14.41 14.43 14.52 -
*B | 15.10 15.26 15.29 15.33 15.36 - - -
 | 15.45 16.01 16.05 16.08 16.11 16.13 16.22 -
* | 16.15 16.31 16.35 16.38 16.41 16.43 16.52 -
 | 16.45 17.01 17.05 17.08 17.11 17.13 17.22 -
GL | 17.15 17.30 17.33 17.36 17.40 17.42 17.49 18.01
S** | 17.20 17.36 17.39 17.42 - - - -
* | 17.45 18.01 18.05 18.08 18.11 18.14 18.23 -
 | 18.15 18.31 18.34 18.39 18.41 18.43 18.50 -
* | 19.15 19.31 19.34 19.38 19.40 19.42 19.50 -
K | 19.45 20.01 20.04 20.08 20.10 20.12 - -
 | 20.50 21.05 21.08 21.12 21.15 21.18 21.26 -
 | 22.15 22.30 22.33 22.37 22.40 22.42 22.50 -
B | 23.35 23.50 23.53 23.57 23.59 - - -'''
# Gresham and Bellrose to Portland: sign, then H R K B T A G P
GNORTH = '''
s | - - - 0.04 0.06 0.09 0.12 -
 | - 1.10 1.17 1.19 1.21 1.24 1.27 -
* | - 5.30 5.38 5.41 5.44 5.48 5.51 6.10
 | - 6.00 6.08 6.11 6.14 6.18 6.21 6.40
* | - 6.30 6.38 6.41 6.44 6.48 6.51 7.10
B* | - - - 7.05 7.10 7.14 7.18 7.36
 | 6.43 7.00 7.08 7.11 7.14 7.18 7.22 7.40
 | - 7.30 7.38 7.41 7.44 7.48 7.51 8.10
* | - 8.00 8.08 8.11 8.14 8.18 8.21 8.40
 | - 8.30 8.38 8.41 8.44 8.48 8.51 9.10
* | - 9.30 9.38 9.41 9.44 9.48 9.51 10.10
 | 10.15 10.30 10.38 10.41 10.44 10.48 10.51 11.10
* | - 11.00 11.08 11.11 11.14 11.18 11.21 11.40
 | - 12.01 12.08 12.11 12.14 12.18 12.21 12.40
* | - 12.30 12.38 12.41 12.44 12.48 12.51 13.10
 | - 13.30 13.38 13.41 13.44 13.48 13.51 14.10
 | - 15.00 15.08 15.11 15.14 15.18 15.21 15.40
B* | - - - 15.41 15.44 15.47 15.51 16.10
 | - 16.30 16.38 16.41 16.44 16.48 16.51 17.10
* | - 17.00 17.08 17.11 17.14 17.18 17.21 17.40
 | - 17.30 17.38 17.41 17.44 17.48 17.51 18.10
sS** | - - - - 17.48 17.51 17.54 -
* | - 18.28 18.35 18.37 18.39 18.42 18.45 19.02
s | 18.20 18.35 18.43 18.45 18.48 18.51 18.54 -
 | - 19.00 19.08 19.10 19.13 19.16 19.19 19.36
*s | - 19.55 20.03 20.05 20.08 20.12 20.15 -
 | - - 20.17 20.19 20.21 20.24 20.27 20.45
 | - 21.31 21.38 21.40 21.43 21.47 21.50 22.08
 | - 22.55 23.02 23.04 23.06 23.09 23.13 23.30'''
def t(x): h, m = x.split('.'); return int(h) * 3600 + int(m) * 60
def rows(block, cols):
    for line in block.strip('\n').split('\n'):
        sign, ts = line.split('|'); sign = sign.strip(); ts = ts.split()
        yield sign, {c: t(v) for c, v in zip(cols, ts) if v != '-'}
def make_trips(key, stations, ST, blocks, div, describe):
    IDX = {c: i for i, (_, _, c) in enumerate(ST) if c}
    G = IDX['G']; trips = []
    for d_, (block, cols) in enumerate(blocks):
        for n, (sign, tp) in enumerate(rows(block, cols)):
            exsatsun = 'XX' in sign or '**' in sign
            days = 'W_1111100' if exsatsun else 'W_1111110' if ('X' in sign or '*' in sign) else 'W_1111111'
            given = {IDX[c]: v for c, v in tp.items()}
            if ('L' in sign and div == 'oc') or '@' in sign: given[1] = given[G] - 600              # leaves East Portland 10 minutes before the Golf Jct. time
            if 'E' in sign and div == 'oc':                                                        # East Portland only: arrival by distance from Golf Jct.
                given[1] = given[G] + round((stations[G]['chain'] - stations[1]['chain']) / (stations[G]['chain'] - stations[0]['chain']) * 16) * 60
            if 's' in sign and div == 'gr': given[1] = given[G] + 600                                # arrive East Portland 10 minutes later
            lo, hi = min(given), max(given)
            last = sign[-1:] if sign else ''
            skip_to = ({'*': IDX['O'], '+': 13, '#': 14} if div == 'oc' else {})
            skip_to = skip_to.get(last) if div == 'oc' else (10 if 'L' in sign else None)          # Gresham L: limited to Wichita
            seq = list(range(lo, hi + 1))
            if d_ == 1: seq = seq[::-1]
            pts = sorted(given.items())
            # Oregon City Division: "All Oak Grove trains make Local Stops on Saturday. All Oregon City trains make Local Stops on Sunday" -> a limited car is two trips
            variants = [(days, skip_to, '')]
            if skip_to is not None and div == 'oc':
                if sign.startswith('O'): variants = [('W_1111100', skip_to, ''), ('W_0000010', None, '; on Saturdays all local stops')]
                else: variants = [('W_1111110', skip_to, ''), ('W_0000001', None, '; on Sundays all local stops')]
            far = stations[hi if d_ == 0 else lo]['name'] if div == 'gr' else None
            for vdays, vskip, vnote in variants:
                stops = []
                for i in seq:
                    if i in given: stops.append([i, given[i], given[i], 1]); continue
                    if vskip is not None and d_ == 0 and i < vskip and not stations[i]['principal']: continue
                    a = max(p for p in pts if p[0] < i); b = min(p for p in pts if p[0] > i)
                    f = (stations[i]['chain'] - stations[a[0]]['chain']) / (stations[b[0]]['chain'] - stations[a[0]]['chain'])
                    v = round((a[1] + f * (b[1] - a[1])) / 60) * 60
                    stops.append([i, v, v, 0])
                first = stops[0][1]; h, m = divmod(first // 60, 60)
                extra = describe(sign)
                if far: extra = ('Gresham train' if 'Gresham' in (stations[lo]['name'], stations[hi]['name']) else
                                 (stations[hi]['name'] if stations[hi]['name'] not in ('Golf Junction',) else stations[lo]['name']) + ' car', extra[1])
                lim = extra[1] if vskip is not None or div == 'gr' else extra[1].split('; no stops')[0].split('; limited')[0]
                dd = {'W_1111110': ', daily except Sunday', 'W_1111100': ', daily except Saturday and Sunday', 'W_0000010': ', Saturdays', 'W_0000001': ', Sundays'}.get(vdays, '')
                note = (f"Portland Traction Co. {extra[0]}, leaves {stations[stops[0][0]]['name']} {(h - 1) % 12 + 1}.{m:02d} {'a.m.' if h % 24 < 12 else 'p.m.'}"
                        f"{dd}{lim}{vnote}. "
                        f"Time Table No. 2, February 1, 1948 (Pacific Standard Time; WX4.org); stations between the timing points timed by distance (est.).").replace('.. ', '. ')
                trips.append(dict(id=f"PTC-{key.upper()}-{'SN'[d_]}-{n:02d}{'' if vdays == days or len(variants) == 1 else '-' + vdays[2:].index('1').__str__()}",
                                  num='Car', name='Portland Traction', svc=vdays, dir=d_, stops=stops, note=note))
    return trips
def oc_desc(sign):
    what = {'O': 'Oak Grove local', 'M': 'Milwaukie local'}.get(sign[:1], 'Oregon City train')
    x = ('; East Portland only' if 'E' in sign else '') + ('; no stops north of Oak Grove except to pick up' if sign.endswith('*') else '') + \
        ('; no stops north of Island except to pick up' if sign.endswith('+') else '') + ('; limited to Lakewood' if sign.endswith('#') else '')
    return what, x
def gr_desc(sign):
    what = 'Gresham train' if 'G' in sign else {'S': 'Stanley car', 'B': 'Bell car', 'K': 'Kendall car'}.get(sign.replace('*', '').replace('s', '')[:1], 'Bellrose car')
    return what, ('; limited to Wichita' if 'L' in sign else '') + ('; East Portland only' if 's' in sign else '')
SRC = ('Portland Traction Co., {}: Time Table No. 2, effective February 1, 1948 (WX4.org, via Brendan); track from the Mississippi Rails (Tony Howe and David Price) '
       'Portland Railway, Light & Power Co. KMZ (via Brendan)')
LINES = []
for key, fn, ST, end_mi, blocks, div, desc, label, dl in (
        ('ptc_oc', 'portland_traction_oregon_city.json', OC_ST, 13.94, ((SOUTH, 'PGMODSC'), (NORTH, 'CSDOMGP')), 'oc', oc_desc, 'Portland – Oregon City (Portland Traction)', 'Oregon City'),
        ('ptc_gr', 'portland_traction_gresham.json', GR_ST, 18.45, ((GSOUTH, 'PGATBKRH'), (GNORTH, 'HRKBTAGP')), 'gr', gr_desc, 'Portland – Bellrose – Gresham (Portland Traction)', 'Gresham')):
    route = load(fn); stations = place(route, ST, end_mi, div)
    trips = make_trips(key, stations, ST, blocks, div, desc)
    LINES.append(dict(key=key, kind='Y', label=label, mainline=True, owner='ptc', src=SRC.format(label.split(' (')[0] + (' (Oregon City Division)' if div == 'oc' else ' (Gresham Division)')),
                      route=route, stations=stations, dirLabels=['to ' + dl, 'to Portland'], segments=[], trips=trips))
    print(f"{key}: {route[-1][2] / 1609.34:.2f} mi traced ({end_mi} printed), {len(trips)} trips")
vd = json.load(open(os.path.join(HERE, 'viz_data.json')))
vd['lines'] = [x for x in vd['lines'] if x['key'] not in ('ptc_oc', 'ptc_gr')] + LINES
open(os.path.join(HERE, 'viz_data.json'), 'w').write(json.dumps(vd, separators=(',', ':')))

def fmt(x): return f'{x // 3600:02d}:{x % 3600 // 60:02d}:{x % 60:02d}'
def app(name, rows_):
    with open(os.path.join(GT, name), 'a', newline='') as fh: csv.writer(fh).writerows(rows_)
def have(name, col=0): return set(r[col] for r in csv.reader(open(os.path.join(GT, name))))
cal = have('calendar.txt')
for d in sorted({tr['svc'] for L in LINES for tr in L['trips']} - cal): app('calendar.txt', [[d, *d[2:], '19490616', '19491231']])
if 'PTC' not in have('agency.txt'): app('agency.txt', [['PTC', 'Portland Traction Company', 'https://en.wikipedia.org/wiki/Portland_Traction_Company', 'America/Vancouver', 'en', '']])
seen = have('stops.txt')
for L in LINES:
    route, stations, TOT, R = L['route'], L['stations'], L['route'][-1][2], L['key'].upper()
    new = [[s['gid'], s['name'], f"{s['lat']:.6f}", f"{s['lon']:.6f}", s['note']] for s in stations if s['gid'] not in seen]
    app('stops.txt', new); seen |= {r[0] for r in new}
    app('routes.txt', [[R, 'PTC', L['label'].split(' (')[0].split(' – ')[-1], L['label'], 0, '2F6F8F', 'FFFFFF', L['src'] + '. Times on the Pacific clock.']])
    app('shapes.txt', [[R + '_S', f'{p[1]:.6f}', f'{p[0]:.6f}', k, f'{p[2]:.1f}'] for k, p in enumerate(route)])
    app('shapes.txt', [[R + '_N', f'{p[1]:.6f}', f'{p[0]:.6f}', k, f'{TOT - p[2]:.1f}'] for k, p in enumerate(route[::-1])])
    for tr in L['trips']:
        app('trips.txt', [[R, tr['svc'], tr['id'], stations[tr['stops'][-1][0]]['name'], 'Portland Traction', tr['dir'], R + '_' + 'SN'[tr['dir']]]])
        app('stop_times.txt', [[tr['id'], fmt(a), fmt(b), stations[i]['gid'], k, f"{(stations[i]['chain'] if tr['dir'] == 0 else TOT - stations[i]['chain']):.1f}", tp]
                               for k, (i, a, b, tp) in enumerate(tr['stops'], 1)])
