"""Saskatchewan and Manitoba, 1948 (Brendan, October 2026): the Canadian Pacific (1948 timetable) and Canadian National (Official Guide, April 25,
1948) tables of Saskatchewan, with the trains that run through into Manitoba as far as Winnipeg, transcribed in sk_cp_t*.csv and sk_cn_t*.csv
(times as printed, in Central or Mountain time by the row's 'tz'; shown in Pacific time). A line ends at its first Alberta station, where the
Alberta lines already on the map take over. One line for each file (a table or a section of one). Machinery: ab_lines.py, with the track and
places of sk_lines.py."""
import glob, os, re
import sk_lines                                             # registers the railways, track graphs and places
import ab_table
from ab_lines import build, trace, report
HERE = os.path.dirname(os.path.abspath(__file__))
TZ = ' Shown in Pacific time: two hours earlier than the Central time printed, an hour earlier than the Mountain time.'
SRC = {'skcp': 'Canadian Pacific timetable, 1948', 'skcn': 'Official Guide, April 25, 1948', 'sknp': 'Northern Pacific timetable, May 18, 1947', 'skgn': 'Great Northern timetable, February 8, 1948', 'skww': 'Official Guide, April 1948', 'skcnw': 'Official Guide, April 25, 1948'}
# per file: what to take (cols), a leg (a, b), train names, and other spec options
OVER = {
 'sk_cp_t005': dict(legs=['sk_cp_t005.csv', 'sk_cp_t006.csv', 'skx_cp_t006_medhat.csv'], long='Winnipeg – Brandon – Broadview – Regina – Moose Jaw – Swift Current – Medicine Hat', short='CP Tables 5 and 6'),
 'sk_cp_t006': dict(skip=True),                                           # joined to Table 5 at Broadview (one train Winnipeg - Walsh)
 'sk_cp_t108': dict(cols=['No315', 'No13M', 'No14M', 'No316']),            # the Soo-Dominion 13/14 run until June 29: the Mountaineer runs in July
 # Table 133: Fox Valley - Pivot - Schuler, back to Pivot, and on by Hilda to Empress: the Schuler - Hilda leg is in ab_cp_t133.csv
 'sk_cp_t133a': dict(legs=['sk_cp_t133a.csv', ('ab_cp_t133.csv', 'Schuler', 'Hilda'), 'sk_cp_t133b.csv'], long='Fox Valley – Pivot – Schuler – Hilda – Leader – Empress'),
 'sk_cp_t133b': dict(skip=True),
 'sk_cp_t139k': dict(file='skx_cp_t139_kerrobert', long='Kerrobert – Court (– Compeer, on to Coronation)'),   # the Saskatchewan end of Table 139
 'sk_cn_t174': dict(leg=('North Regina', 'Riverhurst'), cols=['M303', 'M304'], long='North Regina – Moose Jaw – Central Butte – Riverhurst'),
 'sk_cn_t174d': dict(file='skx_cn_t174_dunblane', long='Central Butte – Dunblane'),     # the Dunblane branch of Table 174 (Mixed 389 / 390)
 # Battleford - North Battleford, 13.9 miles (Brendan, 16 October): out of Battleford, north over the river to the junction on the main line west of
 # North Battleford, and back east into North Battleford
 # Regina - Estlin (Talmage line): out of Union Station north on the CN towards North Regina, round the wye west of it and south, crossing the CP main west of
 # the station (no south-east connector at the CN/CP diamond in 1948: Brendan, 19 October, from period topographic maps)
 'sk_cn_t200a': dict(via=[('Regina', 'Regina Talmage wye', 2.4)]),
 'sk_cp_t130a': dict(via=[('Battleford', 'Battleford Junction', 7.9)]),
 'sk_cn_t212': dict(via=[('Battleford', 'Battleford Junction', 7.9)]),
 # main-line trains loop out of Saskatoon station north and round the west of the city (Brendan, 16 October)
 'sk_cn_t075': dict(via=[('Saskatoon', 'Saskatoon loop', 3.0)]),
 # Rosetown: the point is the CN (Canadian Northern) townsite station; CP's line skirts the town, so CP Rosetown goes by its mileage (Brendan, 17 October)
 'sk_cp_t117a': dict(noplace=['Rosetown']),
 'sk_cp_t113': dict(noplace=['Rosetown']),
 'sk_cp_t117c': dict(noplace=['Wartime']),   # CP Wartime by its mileage: 2.2 km NE of the hamlet (the CN station; Brendan, 17 October)
 'sk_cp_t097': dict(noplace=['East Selkirk', 'Garson']),   # names-file points 1.6 km off Brendan's Birds Hill - Beausejour trace: placed by mileage (18 Oct)
 'sk_cn_t166': dict(skip=True),                                           # Nos. 1-4: built from the derived file (to Wainwright)
 'sk_cn_t166w': dict(via=[('Saskatoon', 'Saskatoon loop', 3.0)], long='Winnipeg – Saskatoon – Wainwright (Continental Limited and No. 3/4)', names={'No1': 'The Continental Limited', 'No2': 'The Continental Limited', 'No3': 'The Continental Limited', 'No4': 'The Continental Limited'}),
 'sk_cn_t172': dict(cols=['No7', 'No8'], names={'No7': 'The Owl', 'No8': 'The Owl'}),                                  # Nos. 5/6 Regina - Saskatoon are entered from Table 171
 'sk_cn_t172s': dict(file='sk_cn_t172', leg=('Saskatoon', 'Prince Albert'), cols=['No5', 'No60'],
                     long='Saskatoon – Prince Albert (Nos. 59 and 60)'),   # 59 / 60 their own trains; 5 / 6 connections in the same column (Brendan, 19 October)
}
# waiting for a point from Brendan for an end station (no Manitoba names file; North Regina is not in the Saskatchewan one)
OVER['sk_cp_t108s'] = dict(short='Soo Line Table 2', long='Minneapolis – Glenwood – Enderlin – Minot – Portal (The Mountaineer)')
OVER['sk_cn_t192d'] = dict(skip=True)   # 61 / 62 Winnipeg - Melville = through cars on CN Nos. 3 / 2 (sk_cn_t166w), same times (Brendan, 19 October)
OVER['sk_cnw_t017'] = dict(long='Chicago – Milwaukee – Eau Claire – St. Paul – Minneapolis (The Mountaineer)', force=[('St. Paul', 'Minneapolis')])   # over the Milwaukee Road to its station (Brendan): 12.3 mi, the C&NW prints 10.6 to its own
OVER['sk_cp_t091'] = dict(names={'No109': 'The Winnipeger', 'No110': 'The Winnipeger'})                 # train names (Brendan, 19 October)
OVER['sk_gn_t007'] = dict(names={'No7': 'The Winnipeg Limited', 'No8': 'The Winnipeg Limited'})
OVER['sk_cn_t161a'] = dict(noplace=['Holmfield'])   # CN Holmfield on its own line, by mileage (Brendan, 20 October: separate stations)
OVER['sk_cn_t167'] = dict(noplace=['Hartney'])   # CN Virden (its line did not join the CP's through town) and Hartney: own stations, by mileage (Brendan, 20 October)
OVER['sk_cp_t106b'] = dict(noplace=['Bienfait'])   # CP Bienfait on its own line, by mileage; the point is the CN station (Brendan, 20 October)
OVER['sk_cp_t099a'] = dict(noplace=['Morris'])   # CP Morris: on its own main line, by its mileage, not the town point (Brendan, 20 October)
OVER['sk_cp_t132'] = dict(cols=['No65', 'No66'])   # M673 / M674 run on to Verlo: entered whole in sk_cp_t140.csv (Table 140, 21 October)
OVER['sk_ww_t001'] = dict(short='Greater Winnipeg Water District Railway', long='St. Boniface – Waugh')
PENDING = {}                                                               # all end points in (Brendan, 17 October 23:00)
def specs():
    out = []
    files = sorted(glob.glob(os.path.join(HERE, 'sk_c*_t*.csv')) + glob.glob(os.path.join(HERE, 'sk_np_t*.csv')) + glob.glob(os.path.join(HERE, 'sk_gn_t*.csv')) + glob.glob(os.path.join(HERE, 'sk_ww_t*.csv')))
    stems = [os.path.basename(f)[:-4] for f in files] + [k for k, v in OVER.items() if 'file' in v]
    for stem in stems:
        o = OVER.get(stem, {})
        if o.get('skip') or (o.get('file') or stem) in PENDING: continue
        fn = (o.get('file') or stem) + '.csv'
        t = ab_table.load(os.path.join(HERE, fn)); R = t['rows']
        rail = 'skcnw' if stem.startswith('sk_cnw') else 'skcn' if stem.startswith('sk_cn') else 'sknp' if stem.startswith('sk_np') else 'skgn' if stem.startswith('sk_gn') else 'skww' if stem.startswith('sk_ww') else 'skcp'
        m = re.match(r'sk_(?:c[np]|np|gn|ww|cnw)_t(\d+)', stem); table = int(m.group(1))
        a, b = o.get('leg', (R[0]['station'], R[-1]['station']))
        legs = [dict(csv=fn, a=a, b=b)] if 'leg' in o else [dict(csv=fn)]
        if 'legs' in o:
            legs = [dict(csv=l) if isinstance(l, str) else dict(csv=l[0], a=l[1], b=l[2]) for l in o['legs']]
            b = ab_table.load(os.path.join(HERE, legs[-1]['csv']))['rows'][-1]['station']
        rw = {'skcn': 'CN', 'skcp': 'CP', 'sknp': 'NP', 'skgn': 'GN', 'skww': 'GWWD', 'skcnw': 'C&NW'}[rail]
        key = stem.replace('sk_cnw_t', 'skcnw').replace('sk_cn_t', 'skcn').replace('sk_cp_t', 'skcp').replace('sk_np_t', 'sknp').replace('sk_gn_t', 'skgn').replace('sk_ww_t', 'skww')
        short = o.get('short', f'{rw} Table {table}')
        out.append(dict(key=key, rail=rail, graph='sk:' + rail[2:], legs=legs, dirs=['to ' + b, 'to ' + a], short=short,
                        long=o.get('long', f'{a} – {b}'), src=f'{short} ({SRC[rail]})', cols=o.get('cols'), shift=-3600, tzrows=True, tznote=TZ,
                        names=o.get('names', {}), notes=o.get('notes', {}), via=o.get('via', ()), noplace=o.get('noplace', ()), force=o.get('force', ()), ends=True, realends=True))
    return out
import sk_join                                              # through trains split across section files, joined (19 October)
_base, _joined = sk_join.build(specs())
SPECS = _base + _joined
if __name__ == '__main__':
    if os.environ.get('SK_DRY'):
        for s in SPECS:
            if os.environ['SK_DRY'] in ('1', s['key']) or (os.environ['SK_DRY'].endswith('*') and s['key'].startswith(os.environ['SK_DRY'][:-1])):
                try: rows, trains, pieces = trace(s); report(s, rows, pieces)
                except SystemExit as e: print(' ', e)
    else:
        build(SPECS)
