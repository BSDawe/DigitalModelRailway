"""Canadian Pacific secondary and branch lines in Alberta, from the 1948 public timetable (transcribed in ab_cp_t*.csv).
The machinery is ab_lines.py: track from the national network; where the network no longer has the line, a straight estimate from station to
station (drawn dashed), the stations placed from the federal names file. Reads the lines already on the map for shared track and stations
(needs mainline_build and cp_south_build). The main line east of Calgary (Table 6) is part of the cp line, in mainline_build.py, and
Lethbridge - Medicine Hat (Table 151) part of the cr line, in cp_south_build.py."""
import os
from ab_lines import build, trace, report
def L(key, legs, dirs, long, tab, cols=None, **kw):
    legs = [dict(csv=l) if isinstance(l, str) else dict(csv=l[0], a=l[1], b=l[2]) for l in legs]
    return dict(key=key, rail='cp', legs=legs, dirs=dirs, short='CP ' + tab, long=long, src=f'Canadian Pacific Table {tab}, 1948 timetable', cols=cols, **kw)
SPECS = [
 L('cp_138', ['ab_cp_t138.csv'], ['to Red Deer, Wetaskiwin and Edmonton', 'to Calgary'], 'Calgary – Red Deer – Lacombe – Wetaskiwin – Edmonton', '138',
   cols=['No521', 'No522', 'No523', 'No524', 'No525', 'No526'], names={'No524': 'The Chinook', 'No525': 'The Chinook'}),
 L('cp_092', [('ab_cp_t138.csv', 'Edmonton', 'Wetaskiwin'), ('ab_cp_t092.csv', 'Wetaskiwin', 'Hayter')], ['to Camrose, Hardisty and Winnipeg', 'to Edmonton'],
   'Edmonton – Wetaskiwin – Camrose – Hardisty – Hayter', '92', cols=['No51', 'No52', 'M419', 'M420', 'M481', 'M480', 'No527', 'No528']),
 L('cp_149b', ['ab_cp_t149b.csv'], ['to Vulcan and Lethbridge', 'to Calgary'], 'Calgary – Aldersyde – Vulcan – Kipp – Lethbridge', '149'),
 L('cp_149', ['ab_cp_t149.csv'], ['to High River, Macleod and Lethbridge', 'to Calgary'], 'Calgary – High River – Macleod – Lethbridge', '149'),
 L('cp_139', [('ab_cp_t139b.csv', 'Lacombe', 'Coronation'), ('ab_cp_t139a.csv', 'Coronation', 'Compeer')], ['to Stettler, Coronation and Kerrobert', 'to Lacombe'],
   'Lacombe – Stettler – Coronation – Compeer', '139',
   noplace=['Stettler']),     # the CP station by its mileage on the east-west line (the names file's point is the CN station, on the north-south line)
 L('cp_141', ['ab_cp_t141.csv'], ['to Leduc, Breton and Lacombe', 'to South Edmonton'], 'South Edmonton – Leduc – Breton – Rimbey – Lacombe', '141'),
 L('cp_142', ['ab_cp_t142.csv'], ['to Rocky Mountain House', 'to Red Deer'], 'Red Deer – Sylvan Lake – Rocky Mountain House', '142',
   via=[('Red Deer', 'Forth', 2.0)]),      # the old Alberta Central left the Calgary line at Forth, south of Red Deer
 L('cp_143', ['ab_cp_t143a.csv'], ['to Irricana and Kneehill', 'to Calgary'], 'Calgary – Langdon – Irricana – Acme – Kneehill', '143', cols=['M632', 'M631']),
 L('cp_143w', [('ab_cp_t143a.csv', 'Calgary', 'Cosway'), 'ab_cp_t143b.csv'], ['to Irricana and Wimborne', 'to Calgary'], 'Calgary – Irricana – Cosway – Wimborne', '143', cols=['M629', 'M630']),
 L('cp_132', ['ab_cp_t132a.csv', 'ab_cp_t132b.csv'], ['to Bassano and Irricana', 'to Empress'], 'Empress – Bassano – Standard – Irricana', '132'),
 L('cp_136', ['ab_cp_t136.csv'], ['to Rosemary, Drumheller and Kneehill', 'to Bassano'], 'Bassano – Rosemary – East Coulee – Drumheller – Kneehill', '136'),
 L('cp_137', [('ab_cp_t137a.csv', 'Grantham', 'Lomond'), 'ab_cp_t137b.csv'], ['to Lomond and Aldersyde', 'to Vauxhall and Grantham'], 'Grantham – Vauxhall – Lomond – Aldersyde', '137'),
 L('cp_144', [('ab_cp_t144a.csv', 'Edmonton', 'Lloydminster')], ['to Willingdon and Lloydminster', 'to Edmonton'], 'Edmonton – Bruderheim – Willingdon – Two Hills – Lloydminster', '144'),
 L('cp_144v', ['ab_cp_t144b.csv'], ['to Willingdon', 'to Vegreville'], 'Vegreville – Willingdon', '144'),
 L('cp_145', ['ab_cp_t145.csv'], ['to Picture Butte and Turin', 'to Lethbridge'], 'Lethbridge – Picture Butte – Turin', '145'),
 L('cp_150', ['ab_cp_t150a.csv'], ['to Cardston and Glenwood', 'to Lethbridge'], 'Lethbridge – Stirling – Cardston – Glenwood', '150', cols=['M650', 'M651']),
 L('cp_150c', ['ab_cp_t150b.csv'], ['to Coutts', 'to Lethbridge'], 'Lethbridge – Stirling – Coutts', '150'),
 L('cp_120', [('ab_cp_t120.csv', 'Lethbridge', 'Jaydot')], ['to Foremost and Manyberries', 'to Lethbridge'], 'Lethbridge – Stirling – Foremost – Manyberries – Jaydot', '120'),
]
if __name__ == '__main__':
    if os.environ.get('AB_DRY'):
        for s in SPECS:
            if os.environ['AB_DRY'] in ('1', s['key']):
                try: rows, trains, pieces = trace(s); report(s, rows, pieces)
                except SystemExit as e: print(' ', e)
    else: build(SPECS)
