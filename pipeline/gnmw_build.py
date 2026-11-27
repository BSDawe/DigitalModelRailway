"""Great Northern east of Spokane (Brendan, 27 Nov 2026): the Official Guide, May 1948, pages 1067 - 1077 (tables of February 8, 1948 and November 30, 1947),
transcribed in timetables_gn/*.csv (times as printed, by the row's zone; shown in Pacific time), with the through trains Chicago - St. Paul over the Burlington
(ends only until the CB&Q tables come: Brendan, 27 Nov 2026). Machinery: ab_lines.py with the track and places of gn_lines.py. The main lines are built first,
one file at a time, so the branches find their junction stations on the map. The trains join the Washington line (gn_main) at Newport and Spokane, and the
St. Paul - Winnipeg line (skgn007) keeps Nos. 7 / 8."""
import glob, os, re
import gn_lines, ab_table, ab_lines
from ab_lines import build, trace, report
HERE = os.path.dirname(os.path.abspath(__file__))
TZ = ' Shown in Pacific time: two hours earlier than the Central time printed, an hour earlier than the Mountain time.'
SRC = 'Official Guide, May 1948'
OVER = {'gn_t002': dict(cols=['No29', 'No11', 'No199', 'No209', 'No27', 'No1', 'No12', 'No200', 'No30', 'No28', 'No2']),   # Nos. 7 / 8: the Winnipeg Limited, built in skgn007
        'gn_t001c_cbq': dict(short='Burlington Route (GN through trains)', long='Chicago – St. Paul (Burlington Route)', src='Official Guide, May 1948, GN Tables 1 and 2: Burlington connection rows'),
        'gn_duluth_gf': dict(short='GN Duluth – Grand Forks', long='Duluth – Superior – Grand Rapids – Bemidji – Crookston – Grand Forks')}
FIRST = ['gn_t001c_cbq', 'gn_t001', 'gn_t002', 'gn_t003', 'gn_t004', 'gn_t053', 'gn_t007', 'gn_duluth_gf', 'gn_t008', 'gn_t038']
def spec(stem):
    o = OVER.get(stem, {}); fn = os.path.join('timetables_gn', stem + '.csv'); R = ab_table.load(os.path.join(HERE, fn))['rows']
    a, b = R[0]['station'], R[-1]['station']
    m = re.match(r'gn_t(\d+)(\w*)', stem)
    short = o.get('short', f"GN Table {int(m.group(1))}{m.group(2) if m and m.group(2) and not m.group(2).startswith('c_') else ''}" if m else stem)
    names = {t['col']: t['name'] for t in ab_table.load(os.path.join(HERE, fn))['trains'] if t.get('name')}
    sh = lambda s: re.sub(r',\s*(Minn\.|N\. Dak\.|S\. Dak\.|Mont\.|Idaho|Wis\.|Iowa|Ill\.|Wash\.)$', '', s)
    return dict(key='gnmw' + stem[3:].replace('_', ''), rail='gnmw', graph='sk:gnmw', legs=[dict(csv=fn)], dirs=['to ' + sh(b), 'to ' + sh(a)], short=short,
                long=o.get('long', f'{sh(a)} – {sh(b)}'), src=f"{short} ({o.get('src', SRC)})", cols=o.get('cols'), shift=-7200, tzrows=True, tznote=TZ,
                names=names, notes={}, via=(), noplace=(), force=o.get('force', ()), ends=True, realends=True)
STEMS = sorted(os.path.basename(f)[:-4] for f in glob.glob(os.path.join(HERE, 'timetables_gn', 'gn_*.csv')))
SPECS = [spec(s) for s in FIRST] + [spec(s) for s in STEMS if s not in FIRST]
if __name__ == '__main__':
    if os.environ.get('GN_DRY'):
        for s in SPECS:
            if os.environ['GN_DRY'] in ('1', s['key']) or (os.environ['GN_DRY'].endswith('*') and s['key'].startswith(os.environ['GN_DRY'][:-1])):
                try: rows, trains, pieces = trace(s); report(s, rows, pieces)
                except SystemExit as e: print(' ', e)
    else:
        import json
        vp = os.path.join(HERE, 'viz_data.json'); vd = json.load(open(vp))         # this step's lines from an earlier run: not a source of places
        vd['lines'] = [L for L in vd['lines'] if not L['key'].startswith('gnmw')]; open(vp, 'w').write(json.dumps(vd, separators=(',', ':')))
        todo = list(SPECS)
        while todo:                                               # one at a time: each line's stations are on the map for the next; a line whose end
            left = []                                             # station is not placed yet is tried again after the others
            for s in todo:
                gn_lines._MAPX.clear(); gn_lines.ANCH.clear()
                try: build([s])
                except SystemExit as e: left.append((s, e))
            if len(left) == len(todo):
                for s, e in left: print('  NOT BUILT:', e)
                break
            todo = [s for s, _ in left]
