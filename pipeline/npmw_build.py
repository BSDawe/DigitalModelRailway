"""Northern Pacific east of Spokane and the Camas Prairie in Idaho (Brendan, 27 Nov 2026): the Official Guide, May 1948, pages 1090 - 1097 (tables of 1947 - 1948),
transcribed in timetables_np/*.csv and timetables_cprr/*.csv (times as printed, by the row's zone; shown in Pacific time). Machinery: ab_lines.py with the track and places
of np_lines.py. The main lines are built first, one file at a time, so the branches find their junction stations on the map. Through trains join the Washington lines
(np_main, np_044) at Spokane, Pullman and Sunshine, and the Winnipeg line (sknp014, already built from the 1947 timetable: np_t014.csv is not built again)."""
import glob, os, re
import np_lines, ab_table, ab_lines
from ab_lines import build, trace, report
HERE = os.path.dirname(os.path.abspath(__file__))
TZ = ' Shown in Pacific time: two hours earlier than the Central time printed, an hour earlier than the Mountain time.'
SRC = 'Official Guide, May 1948'
FIRST = ['np_t001', 'np_t005', 'np_t002', 'np_t002h', 'np_t002b', 'np_t003', 'np_t006', 'np_t006s']
SKIP = {'np_t014'}                                             # built in October (sknp014)
MSP = [('Minneapolis, Minn.', 'St. Paul, Minn.'), ('St. Paul, Minn.', 'Gloster, Minn.')]   # through St. Paul Union Depot (Brendan, 28 Nov 2026: not round by the Soo track); the NP pieces stop 0.9 km short of the depot
SC = [('Superior, Wis.', 'Carlton, Minn.')]                    # Superior - Carlton: the track found is 19 mi against 23 printed (the Superior terminal pieces): accepted
OVER = {'np_t005': dict(short='NP Table 5', long='Duluth – Superior – Brainerd – Staples', force=SC), 'np_t006': dict(short='NP Table 6 (via Superior)', force=[('Carlton, Minn.', 'Superior, Wis.'), ('Superior, Wis.', 'Duluth, Minn.'), ('Carlton, Minn.', 'Wrenshall, Minn.'), ('Wrenshall, Minn.', 'Cent. Ave., Superior, Wis.'), ('Carlton, Minn.', 'Cent. Ave., Superior, Wis.'), ('Cent. Ave., Superior, Wis.', 'Superior, Wis.'), ('Superior, Wis.', 'West Duluth, Minn.'), ('West Duluth, Minn.', 'Twentieth Avenue, Minn.')] + MSP),
        'np_t006s': dict(short='NP Table 6 (Short Line)', long='Minneapolis – St. Paul – Carlton – Thomson – Duluth', force=MSP), 'np_t002h': dict(short='NP Table 2 (via Helena)'), 'np_t002b': dict(short='NP Table 2 (via Butte)'),
        'np_t044i': dict(short='NP Table 44', long='Pullman – Moscow – Lewiston'), 'np_t015': dict(short='NP Table 15')}
sh = lambda s: re.sub(r',\s*(Minn\.|N\. Dak\.|S\. Dak\.|Mont\.|Idaho|Wis\.|Iowa|Ill\.|Wash\.|Man\.)$', '', s)
def spec(path):
    stem = os.path.basename(path)[:-4]; o = OVER.get(stem, {}); fn = os.path.relpath(path, HERE); tab = ab_table.load(path); R = tab['rows']
    a, b = R[0]['station'], R[-1]['station']; cp = stem.startswith('cprr')
    m = re.match(r'(?:np|cprr)_t0*(\d+)(\w*)', stem)
    short = o.get('short', ('CPRR Table ' if cp else 'NP Table ') + m.group(1) + (m.group(2) if not cp else ''))
    names = {t['col']: t['name'] for t in tab['trains'] if t.get('name')}
    return dict(key=('cpmw' if cp else 'npmw') + re.sub(r'^(np|cprr)_t', '', stem), rail='cpmw' if cp else 'npmw', graph='sk:cpmw' if cp else 'sk:npmw', legs=[dict(csv=fn)],
                dirs=['to ' + sh(b), 'to ' + sh(a)], short=short, long=o.get('long', f'{sh(a)} – {sh(b)}'), src=f"{short} ({SRC})", cols=o.get('cols'), shift=-7200, tzrows=True,
                tznote=TZ, names=names, notes={}, via=o.get('via', ()), noplace=(), force=o.get('force', ()), ends=True, realends=True)
FILES = sorted(glob.glob(os.path.join(HERE, 'timetables_np', 'np_*.csv'))) + sorted(glob.glob(os.path.join(HERE, 'timetables_cprr', 'cprr_*.csv')))
BYSTEM = {os.path.basename(f)[:-4]: f for f in FILES}
SPECS = [spec(BYSTEM[s]) for s in FIRST] + [spec(f) for s, f in BYSTEM.items() if s not in FIRST and s not in SKIP]
if __name__ == '__main__':
    if os.environ.get('NP_DRY'):
        for s in SPECS:
            if os.environ['NP_DRY'] in ('1', s['key']) or (os.environ['NP_DRY'].endswith('*') and s['key'].startswith(os.environ['NP_DRY'][:-1])):
                try: rows, trains, pieces = trace(s); report(s, rows, pieces)
                except SystemExit as e: print(' ', e)
    else:
        import json, csv
        vp = os.path.join(HERE, 'viz_data.json'); vd = json.load(open(vp))
        vd['lines'] = [L for L in vd['lines'] if not L['key'].startswith(('npmw', 'cpmw'))]; open(vp, 'w').write(json.dumps(vd, separators=(',', ':')))
        todo = list(SPECS)
        while todo:
            left = []
            for s in todo:
                np_lines._MAPX.clear(); np_lines.ANCH.clear()
                try: build([s])
                except SystemExit as e: left.append((s, e))
            if len(left) == len(todo):
                for s, e in left: print('  NOT BUILT:', e)
                break
            todo = [s for s, _ in left]
        GT = os.path.join(HERE, 'gtfs'); ap = os.path.join(GT, 'agency.txt'); rows = [r for r in csv.reader(open(ap)) if r]
        if not any(r[0] == 'CPRR' for r in rows):
            with open(ap, 'a', newline='') as fh: csv.writer(fh).writerow(['CPRR', 'Camas Prairie Railroad', 'https://en.wikipedia.org/wiki/Camas_Prairie_Railroad', 'America/Vancouver', 'en', ''])
