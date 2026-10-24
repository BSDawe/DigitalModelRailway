"""Ontario and Quebec, 1948 (Brendan, 23 October 2026): CP Tables 4, 58, 70, 75 and the boat trains 707/708 (CP timetable 1948); CN Tables 75 (east of
Armstrong) and 38 (Official Guide, April 25, 1948); the Ontario Northland (November 16, 1947) and the Algoma Central (April 25, 1948). Transcribed in
on_*.csv, times as printed (Eastern time), shown in Pacific time. One line for each file. Track and stations: on_lines.py (Delamere's collections).
Not built: on_soo_*.csv and on_dssa_*.csv (United States, no track yet) and the steamers in marine/ (no port positions yet)."""
import glob, os, re
import on_lines                                             # registers the railways, track graphs, places and the projection for this step
import ab_table
from ab_lines import build, trace, report
HERE = os.path.dirname(os.path.abspath(__file__))
TZ = ' Shown in Pacific time: three hours earlier than the Eastern time printed.'
SRC = {'oncp': 'Canadian Pacific timetable, 1948', 'oncn': 'Official Guide, April 25, 1948', 'onr': 'Ontario Northland timetable, November 16, 1947',
       'acr': 'Algoma Central timetable, April 25, 1948'}
LONG = {'on_cp_t004': 'Montreal – Ottawa – North Bay – Sudbury – Fort William', 'on_cp_t058': 'Toronto – MacTier – Parry Sound – Sudbury (and Port McNicoll)',
        'on_cp_t058b': 'Ypres – Camp Borden', 'on_cp_t058p': 'Toronto – Medonte – Port McNicoll (boat trains)', 'on_cp_t070': 'Sudbury – Sault Ste. Marie', 'on_cp_t070b': 'Sudbury – McKerrow – Little Current',
        'on_cp_t075': 'Sudbury – Creighton', 'on_cp_t707': 'Toronto – Owen Sound (boat trains)',
        'on_cn_t075a': 'Montreal – Coteau – Ottawa', 'on_cn_t075v': 'Coteau – Valleyfield', 'on_cn_t075b': 'Ottawa – Pembroke – North Bay – Capreol – Armstrong',
        'on_cn_t075t': 'Toronto – Capreol', 'on_cn_t038q': 'Quebec – Garneau – Hervey', 'on_cn_t038m': 'Montreal – Hervey',
        'on_cn_t038h': 'Hervey – La Tuque – Senneterre – Taschereau – Cochrane', 'on_cn_t038n': "Senneterre – Val d'Or – Noranda",
        'on_cn_t038t': 'Taschereau – Noranda', 'on_onr_t001': 'Toronto – North Bay – Porquis – Timmins', 'on_onr_t001c': 'Porquis – Cochrane',
        'on_onr_t018m': 'Cochrane – Moosonee', 'on_onr_t018s': 'Swastika – Kirkland Lake – Rouyn – Noranda',
        'on_acr_t001': 'Sault Ste. Marie – Hawk Junction – Hearst', 'on_acr_t001m': 'Hawk Junction – Michipicoten'}
OVER = {'on_cn_t075b': dict(noplace=['Ottawa (Bank Street)']),
        'on_cp_t058b': dict(places={'Camp Borden (Lower Station)': (-79.891308, 44.269889),      # Brendan, 23 Oct 2026: "about here"
                                    'Camp Borden (Upper Station)': (-79.886619, 44.286324)}),    # at the end of its spur (his trace)
        'on_cp_t070': dict(places={'Worthington': (-81.4516144, 46.3826754), 'Turbine': (-81.5119836, 46.3741679)}),
        'on_cp_t070b': dict(places={'Worthington': (-81.4516144, 46.3826754), 'Turbine': (-81.5119836, 46.3741679)})}   # on the Soo branch (the collection's
                                                                  # points snap to the parallel Algoma Eastern line, which does not join between them)   # Bank Street by its mileage from Union Station (canon names both 'ottawa')
def specs():
    out = []
    for fn in sorted(glob.glob(os.path.join(HERE, 'on_c[pn]_t*.csv')) + glob.glob(os.path.join(HERE, 'on_onr_t*.csv')) + glob.glob(os.path.join(HERE, 'on_acr_t*.csv'))):
        stem = os.path.basename(fn)[:-4]; o = OVER.get(stem, {})
        if o.get('skip'): continue
        rail = {'cp': 'oncp', 'cn': 'oncn', 'onr': 'onr', 'acr': 'acr'}[re.match(r'on_(cp|cn|onr|acr)_', stem).group(1)]
        R = ab_table.load(fn)['rows']; a, b = R[0]['station'], R[-1]['station']
        table = re.match(r'on_\w+?_t(\d+)', stem).group(1).lstrip('0')
        rw = {'oncp': 'CP', 'oncn': 'CN', 'onr': 'ONR', 'acr': 'ACR'}[rail]
        short = o.get('short', f'{rw} Table {table}' if rail in ('oncp', 'oncn') else {'onr': 'Ontario Northland', 'acr': 'Algoma Central'}[rail])
        key = stem.replace('on_', 'on').replace('_t', '')
        out.append(dict(key=key, rail=rail, graph='sk:' + rail, legs=[dict(csv=os.path.basename(fn))], dirs=['to ' + b, 'to ' + a], short=short,
                        long=o.get('long', LONG.get(stem, f'{a} – {b}')), src=f'{short} ({SRC[rail]})', cols=o.get('cols'), shift=-10800, tzrows=True, tznote=TZ,
                        names=o.get('names', {}), notes=o.get('notes', {}), via=o.get('via', ()), noplace=o.get('noplace', ()), force=o.get('force', ()), places=o.get('places'), ends=True, realends=True))
    return out
SPECS = specs()
on_lines.register([(s['rail'], s['legs'][0]['csv']) for s in SPECS])
if __name__ == '__main__':
    if os.environ.get('ON_DRY'):
        for s in SPECS:
            if os.environ['ON_DRY'] in ('1', s['key']) or (os.environ['ON_DRY'].endswith('*') and s['key'].startswith(os.environ['ON_DRY'][:-1])):
                try: rows, trains, pieces = trace(s); report(s, rows, pieces)
                except SystemExit as e: print(' ', e)
    else:
        build(SPECS)
        import csv
        GT = os.path.join(HERE, 'gtfs'); have = {r[0] for r in csv.reader(open(os.path.join(GT, 'agency.txt')))}
        with open(os.path.join(GT, 'agency.txt'), 'a', newline='') as fh:
            w = csv.writer(fh)
            for ag in (['ONR', 'Ontario Northland Railway', 'https://en.wikipedia.org/wiki/Ontario_Northland_Railway', 'America/Vancouver', 'en', ''],
                       ['ACR', 'Algoma Central Railway', 'https://en.wikipedia.org/wiki/Algoma_Central_Railway', 'America/Vancouver', 'en', ''],
                       ['GWWD', 'Greater Winnipeg Water District Railway', 'https://en.wikipedia.org/wiki/Greater_Winnipeg_Water_District_Railway', 'America/Vancouver', 'en', '']):   # GWWD: missing since 18 Oct
                if ag[0] not in have: w.writerow(ag)
