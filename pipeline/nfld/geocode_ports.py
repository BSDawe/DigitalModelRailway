"""Points for the Newfoundland coastal-steamer ports (nfld/coastal_routes.py) from the federal Canadian Geographical Names file
(Natural Resources Canada, Open Government Licence - Canada). Populated places first, then harbours, wharves and the like, then any
feature (islands, capes); a name found more than once takes the one nearest the route's previous port. Overrides (FIX) for names the
1949 folder spells differently. Writes nfld/coastal_ports.csv (route, port, lon, lat, how).
    python3 nfld/geocode_ports.py /path/to/cgn_nl_csv_eng.csv"""
import csv, math, os, re, sys, unicodedata
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from coastal_routes import ROUTES
HERE = os.path.dirname(os.path.abspath(__file__))
def norm(s):
    s = ''.join(c for c in unicodedata.normalize('NFKD', s.lower().replace('’', "'")) if not unicodedata.combining(c))
    s = re.sub(r'\bhr\b\.?', 'harbour', s); s = re.sub(r"[.'`]", '', s); s = re.sub(r'\s*\(.*?\)', '', s)
    return re.sub(r'\s+', ' ', s).strip()
FIX = {  # folder name -> CGN name (Claude: spellings and modern names)
 'isle au morte': 'isle aux morts', 'pushthrough': 'pushthrough', 'mose ambrose': 'mose ambrose', 'point enragee': 'point enragee',
 'old port au choix': 'port au choix', 'main point': 'main point', 'burlington, nw arm': 'burlington', 'hooping harbour': 'hooping harbour',
 'snooks arm': 'snooks arm', 'fishot island': 'fishot island', 'great harbour deep': 'harbour deep', 'macovik': 'makkovik', 'smokey': 'smokey',
 'ailik': 'cape aillik', 'grady': 'grady harbour', 'east port': 'eastport', 'pacquet': 'pacquet', 'triton west': 'triton', 'rosaru': 'rosaru',
 'great burin': 'great burin harbour', 'rosaru': 'rose au rue', 'brule': 'great brule', 'fredericton': 'frederickton', 'lushs bight': 'lushes bight',
 'newstead': 'newstead harbour', 'dead island': 'dead islands', 'hawks harbour': 'hawke harbour', 'spotted islands': 'spotted island',
 'iron bound islands': 'ironbound islands', 'turnavik': 'turnavik island', 'la scie': 'lascie', 'roddickton': 'roddickton-bide arm',
 'grey island': 'grey islands harbour', 'paradise': 'great paradise', 'victoria': 'victoria cove', 'webbers cove': 'webber harbour',
 'wolf islands': 'north wolf island', 'black islands': 'black island', 'indian island': 'indian islands', 'st margarets bay': 'st margaret bay', 'lance au loup': 'lanse au loup',
}
# not in the names file: placed between their neighbours on the route, in proportion to the folder's miles (Claude; APPROXIMATE)
BETWEEN = {"Bolster's Rock", 'White Bears', 'Fishot Island'}
rows = list(csv.DictReader(open(sys.argv[1], encoding='utf-8-sig')))
KEEP = {'Railway Point', 'Station', 'Landing', 'Wharf', 'Harbour', 'Port', 'Breakwater', 'Post Office'}
def rank(r): return 0 if r['Generic Category'] == 'Populated Place' else 1 if r['Generic Term'] in KEEP else 2
by = {}
for r in rows: by.setdefault(norm(r['Geographical Name']), []).append(r)
def km(a, b): return 6371 * math.hypot(math.radians(a[0] - b[0]) * math.cos(math.radians((a[1] + b[1]) / 2)), math.radians(a[1] - b[1]))
SEED = {'placentia_west': (-53.97, 47.30), 'placentia_bay': (-53.97, 47.30), 'south_coast': (-53.97, 47.30), 'lewisporte': (-52.71, 47.57),
        'green_bay': (-55.10, 49.25), 'notre_dame': (-55.10, 49.25), 'labrador': (-52.71, 47.57), 'cooks_harbour': (-52.71, 47.57), 'battle_harbour': (-57.95, 48.95)}
out, miss = [], []
for key, (title, ports) in ROUTES.items():
    prev = SEED[key]; pm = 0
    for p in ports:
        n = norm(p[1]); n = FIX.get(n, n); c = by.get(n, [])
        if not c or p[1] in BETWEEN: miss.append((key, p[1])); out.append([key, p[1], None, None, 'between']); continue
        # within reach of the previous port (the folder's miles, with room for the coast's turns) the best kind of feature wins; otherwise the nearest
        reach = (p[0] - pm) * 1.609 * 1.4 + 25
        ok = [r for r in c if km((float(r['Longitude']), float(r['Latitude'])), prev) <= reach]
        best = min(ok, key=lambda r: (rank(r), km((float(r['Longitude']), float(r['Latitude'])), prev))) if ok else \
               min(c, key=lambda r: km((float(r['Longitude']), float(r['Latitude'])), prev))
        ll = (float(best['Longitude']), float(best['Latitude'])); prev = ll; pm = p[0]
        out.append([key, p[1], ll[0], ll[1], f"CGN {best['Geographical Name']} ({best['Generic Term']}, {best['Location']}){'; ' + str(len(c)) + ' of the name' if len(c) > 1 else ''}"])
for k, o in enumerate(out):
    if o[2] is not None: continue
    mi = {q[1]: q[0] for q in ROUTES[o[0]][1]}
    a = next(x for x in reversed(out[:k]) if x[0] == o[0] and x[2] is not None); b = next(x for x in out[k + 1:] if x[0] == o[0] and x[2] is not None)
    f = (mi[o[1]] - mi[a[1]]) / (mi[b[1]] - mi[a[1]])
    o[2], o[3] = round(a[2] + f * (b[2] - a[2]), 6), round(a[3] + f * (b[3] - a[3]), 6); o[4] = f'not in the names file: between {a[1]} and {b[1]} by the miles (APPROXIMATE)'
with open(os.path.join(HERE, 'coastal_ports.csv'), 'w', newline='') as fh:
    w = csv.writer(fh); w.writerow(['route', 'port', 'lon', 'lat', 'how']); w.writerows(out)
print(len(out), 'placed;', len(miss), 'missing:', miss)
