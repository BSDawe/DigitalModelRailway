"""Station and landing candidates from a federal Canadian Geographical Names file (Natural Resources Canada, Open Government Licence - Canada):
every populated place, plus railway points, stations, landings, wharves, harbours, ports, breakwaters, deepwater terminals and post offices.
Writes places/cgn_<prov>_places.csv in the columns of cgn_bc_places.csv (name, kind, lat, lon, location). The full files are raw: they belong in the
private repository (places/cgn_<prov>/), only these cuts in the public one.
    python3 tools/cgn_places.py nb /path/to/cgn_nb_csv_eng.csv"""
import csv, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
KEEP = {'Railway Point', 'Station', 'Landing', 'Wharf', 'Harbour', 'Port', 'Breakwater', 'Deepwater Terminal', 'Post Office'}
prov, src = sys.argv[1], sys.argv[2]
rows = [r for r in csv.DictReader(open(src, encoding='utf-8-sig')) if r['Generic Category'] == 'Populated Place' or r['Generic Term'] in KEEP]
out = os.path.join(HERE, '..', 'places', f'cgn_{prov}_places.csv')
with open(out, 'w', newline='', encoding='utf-8') as fh:
    w = csv.writer(fh); w.writerow(['name', 'kind', 'lat', 'lon', 'location'])
    for r in sorted(rows, key=lambda r: r['Geographical Name']): w.writerow([r['Geographical Name'], r['Generic Term'], r['Latitude'], r['Longitude'], r['Location']])
print(out, len(rows))
