"""Washington State, 1948 (Brendan, October 2026): Northern Pacific, Great Northern, Spokane Portland & Seattle, Union Pacific, Milwaukee Road,
Camas Prairie and the Washington Idaho & Montana, from the Official Guide pages he supplied (transcribed in wa_*.csv; times printed in
Pacific time). Trains end at their last timed station in Washington (Idaho side); the Oregon runs of trains that enter Washington are
included, and the UP's Oregon trains that share their track. Pooled Seattle–Portland trains are entered once (NP Table 4).
Machinery: ab_lines.py with the Washington track and places of wa_lines.py."""
import os
import wa_lines                                             # registers the Washington railways, track graphs and places
from ab_lines import build, trace, report
OG = 'Official Guide, 1948'
def L(key, rail, graph, legs, dirs, long, src, cols=None, **kw):
    wa_lines.register(graph)
    legs = [dict(csv=l) if isinstance(l, str) else dict(csv=l[0], a=l[1], b=l[2]) for l in legs]
    return dict(key=key, rail=rail, graph='wa:' + graph, legs=legs, dirs=dirs, short=src.split(',')[0], long=long, src=src + ' (' + OG + ')', cols=cols,
                shift=0, ends=False, **kw)
# the SP&S's own line between Spokane and Pasco (by Lamont and Washtucna), not the NP's by Ritzville: two of its towns from the names file
SPS_PLACES = {'Lamont': (-117.9052213, 47.2015493), 'Washtucna': (-118.307738, 46.749980)}      # Washtucna: the names file's town, 760 m off the line, moved onto it
SPECS = [
 # Northern Pacific
 L('np_main', 'np', 'np', ['wa_np_t003a.csv'], ['to Seattle', 'to Spokane'], 'Spokane – Pasco – Yakima – Ellensburg – Auburn – Seattle', 'NP Table 3'),
 L('np_tac', 'np', 'np', ['wa_np_t003b.csv'], ['to Tacoma', 'to East Auburn'], 'East Auburn – Tacoma (Tacoma sections of the main line trains)', 'NP Table 3'),
 L('np_pool', 'np', 'np+sps', ['wa_np_t004.csv'], ['to Tacoma and Portland', 'to Seattle'], 'Seattle – Tacoma – Centralia – Vancouver – Portland (pool trains of the NP, GN and UP)', 'NP Table 4',
   cols=['No402', 'No408', 'No460', 'No407', 'No459', 'No401'],
   places={'Steilacoom': (-122.6026274, 47.1698197)}),     # by Point Defiance and Steilacoom (the names file's town), not the Prairie Line by Lakeview
 # the UP's pool trains (Table 4 notes): from Seattle Union Station by the UP's own line through Kent, Auburn, Sumner and North Puyallup to Tacoma,
 # then over the NP and the SP&S to Portland
 L('up_pool', 'up', 'upn+np+sps', [('wa_np_t004.csv', 'Seattle (Union Sta.)', 'Portland')], ['to Tacoma and Portland', 'to Seattle'], 'Seattle (Union Station) – Tacoma – Centralia – Vancouver – Portland (UP pool trains; into Portland by the SP&S/NP north-side route from 1946)',
   'NP Table 4', cols=['No458', 'No457'], noplace=['Puyallup'],
   places={'Steilacoom': (-122.6026274, 47.1698197), 'Kent': (-122.240969, 47.380957), 'Auburn': (-122.23899, 47.305682),      # Kent, Auburn, Sumner and North
           'Sumner': (-122.246302, 47.209906), 'North Puyallup': (-122.278838, 47.208289)}),                                      # Puyallup: the UP/Milwaukee stations   # Nos. 422/423 are entered from Table 60, by Lakeview and Fort Lewis (Brendan)
 L('np_044', 'np', 'np', ['wa_np_t044.csv'], ['to Pullman', 'to Spokane'], 'Spokane – Marshall – Pullman', 'NP Table 44'),
 L('np_046', 'np', 'np', ['wa_np_t046.csv'], ['to Coulee City', 'to Spokane'], 'Spokane – Cheney – Davenport – Coulee City', 'NP Table 46'),
 L('np_058', 'np', 'np+up~', ['wa_np_t058.csv'], ['to Walla Walla', 'to Pasco'], 'Pasco – Walla Walla', 'NP Table 58',
   ),     # the NP's Walla Walla station: wa_lines BY_RAIL (the end of its station spur, Brendan 15 Oct 2026)
 L('np_060', 'np', 'np', ['wa_np_t060.csv'], ['to Olympia and Hoquiam', 'to Seattle'], 'Seattle – Tacoma – St. Clair – Olympia – Aberdeen – Hoquiam', 'NP Table 60'),
 L('np_062', 'np', 'np', ['wa_np_t062.csv'], ['to South Bend', 'to Centralia'], 'Centralia – Chehalis – Raymond – South Bend', 'NP Table 62',
   places={'Chehalis': (-122.97095, 46.65935)}, force=[('Centralia', 'Chehalis')]),    # the table counts its miles from Chehalis (Centralia and Chehalis both 0)
 # Great Northern
 L('gn_main', 'gnw', 'gn', ['wa_gn_t005a.csv'], ['to Seattle', 'to Spokane'], 'Newport – Spokane – Wenatchee – Everett – Seattle', 'GN Table 5',
   names={'No1': 'The Empire Builder', 'No2': 'The Empire Builder', 'No3': 'The Oriental Limited', 'No4': 'The Oriental Limited',
          'No5': 'The Cascadian', 'No6': 'The Cascadian', 'No27': 'The Fast Mail', 'No28': 'The Fast Mail'}),   # names (Brendan, 19 October 2026)
 L('gn_043', 'gnw', 'gn', ['wa_gn_t043.csv'], ['to Mansfield', 'to Wenatchee'], 'Wenatchee – Mansfield', 'GN Table 43'),
 L('gn_045', 'gnw', 'gn', ['wa_gn_t045.csv'], ['to Oroville', 'to Wenatchee'], 'Wenatchee – Chelan – Omak – Oroville', 'GN Table 45'),
 # Spokane, Portland & Seattle (it served both the NP and the GN)
 L('sps_main', 'sps', 'sps+np+gn@spk', ['wa_sps_t001.csv'], ['to Pasco and Portland', 'to Spokane'], 'Spokane – Pasco – Wishram – Vancouver – Portland', 'SP&S Table 1',
   cols=['No5', 'No6'], places=SPS_PLACES, force=[('Spokane (N. P. Station)', 'Spokane (G. N. Station)')]),
 # the Portland sections of the Great Northern's Empire Builder (1/2) and Oriental Limited (3/4) over the SP&S: GN trains, drawn in GN colours
 # (Brendan, 9 October 2026), the same trains as the Seattle sections east of Spokane; the SP&S draws the track
 L('sps_gn', 'gnw', 'sps+np+gn@spk', ['wa_sps_t001.csv'], ['to Pasco and Portland', 'to Spokane'], 'Spokane – Pasco – Vancouver – Portland (Portland sections of GN Nos. 1 to 4, over the SP&S)',
   'SP&S Table 1', cols=['No1', 'No2', 'No3', 'No4'], places=SPS_PLACES, force=[('Spokane (N. P. Station)', 'Spokane (G. N. Station)')],
   names={'No1': 'The Empire Builder', 'No2': 'The Empire Builder', 'No3': 'The Oriental Limited', 'No4': 'The Oriental Limited'}),
 L('sps_004', 'sps', 'sps', ['wa_sps_t004.csv'], ['to Lyle', 'to Goldendale'], 'Goldendale – Lyle', 'SP&S Table 4'),
 # Union Pacific
 L('up_main', 'up', 'up+np', [('wa_up_t056a.csv', 'Portland', 'Umatilla'), ('wa_up_t056c.csv', 'Umatilla', 'Spokane')], ['to Spokane', 'to Portland'],
   'Portland – The Dalles – Umatilla – Ayer – Spokane', 'UP Table 56', cols=['No19', 'No20'], noplace=['Cheney']),   # Cheney: the UP's, by mileage (not the NP's point)
 L('up_pen', 'up', 'up+np', [('wa_up_t056b.csv', 'Pendleton', 'Umatilla'), ('wa_up_t056c.csv', 'Umatilla', 'Spokane')], ['to Spokane', 'to Pendleton'],
   'Pendleton – Umatilla – Ayer – Spokane', 'UP Table 56', cols=['No65', 'No66'], noplace=['Cheney']),
 L('up_or', 'up', 'up', ['wa_up_t005or.csv'], ['to Portland', 'to Pendleton'], 'Pendleton – The Dalles – Portland (trains to and from the east, by the Cut-off)', 'UP Table 5'),
 L('up_057', 'up', 'up+cprr+np', [('wa_up_t057.csv', 'Ayer', 'Spokane')], ['to Spokane', 'to Ayer'], 'Ayer – Colfax; Tekoa – Spokane', 'UP Table 57', noplace=['Tucannon', 'Riparia']),
 L('up_053', 'up', 'up', ['wa_up_t053.csv'], ['to Yakima', 'to Wallula'], 'Wallula – Kennewick – Sunnyside – Yakima', 'UP Table 53', noplace=['Attalia', 'Kennewick']),
 L('up_061', 'up', 'up', ['wa_up_t061.csv'], ['to Walla Walla', 'to Wallula'], 'Wallula – Walla Walla', 'UP Table 61'),
 L('up_060', 'up', 'up+np', [('wa_up_t060.csv', 'Walla Walla', 'Dayton')], ['to Dayton', 'to Walla Walla'], 'Walla Walla – Bolles – Dayton', 'UP Table 60'),   # Turner (mile 50) has no times: the trains end at Dayton (Brendan, 15 Oct 2026)
 L('cprr', 'cprr', 'up+cprr+np', [('wa_up_t056d.csv', 'Ayer', 'Riparia'), ('wa_up_t062.csv', 'Riparia', 'Wilma')], ['to Lewiston', 'to Ayer'],
   'Ayer – Riparia – Almota – Wilma (for Lewiston)', 'UP Tables 56 and 62',
   places={'Wilma': (-117.03974, 46.43112)}, noplace=['Tucannon']),        # APPROXIMATE: the end of the Camas Prairie trace at the Idaho line
 # Milwaukee Road
 L('milw_main', 'milw', 'milw+up@spk', ['wa_milw_t003a.csv'], ['to Seattle', 'to Spokane'], 'Manito – Othello – Ellensburg – Cle Elum – Seattle', 'Milwaukee main line'),
 L('milw_tac', 'milw', 'milw', ['wa_milw_t003b.csv'], ['to Tacoma', 'to Seattle'], 'Seattle – Black River – Tacoma', 'Milwaukee main line'),
 L('milw_076', 'milw', 'milw', ['wa_milw_t076.csv'], ['to Marcellus', 'to Warden'], 'Warden – Marcellus', 'Milwaukee Table 76'),
 L('milw_077', 'milw', 'milw', ['wa_milw_t077.csv'], ['to Moses Lake', 'to Othello'], 'Othello – Warden – Moses Lake', 'Milwaukee Table 77'),
 L('milw_084', 'milw', 'milw+np', [('wa_milw_t084.csv', 'Chehalis', 'Raymond')], ['to Raymond', 'to Chehalis'],
   'Chehalis – Dryad (over the NP) – Raymond (the mixed trains start and end at Chehalis; Maytown – Chehalis has no train)', 'Milwaukee Table 84',
   places={'Dryad': (-123.251254, 46.636768)}),     # joint trackage with the NP Chehalis Junction – Dryad, 16.83 mi (1935 agreement; Brendan)
]
if __name__ == '__main__':
    if os.environ.get('WA_DRY'):
        for s in SPECS:
            if os.environ['WA_DRY'] in ('1', s['key']):
                try: rows, trains, pieces = trace(s); report(s, rows, pieces)
                except SystemExit as e: print(' ', e)
    else:
        build(SPECS)
        import csv
        GT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gtfs'); have = {r[0] for r in csv.reader(open(os.path.join(GT, 'agency.txt')))}
        with open(os.path.join(GT, 'agency.txt'), 'a', newline='') as fh:
            csv.writer(fh).writerows([a for a in [
                ['NP', 'Northern Pacific Railway', 'https://en.wikipedia.org/wiki/Northern_Pacific_Railway', 'America/Vancouver', 'en', ''],
                ['SPS', 'Spokane, Portland and Seattle Railway', 'https://en.wikipedia.org/wiki/Spokane,_Portland_and_Seattle_Railway', 'America/Vancouver', 'en', ''],
                ['UP', 'Union Pacific Railroad', 'https://en.wikipedia.org/wiki/Union_Pacific_Railroad', 'America/Vancouver', 'en', ''],
                ['MILW', 'Chicago, Milwaukee, St. Paul and Pacific Railroad', 'https://en.wikipedia.org/wiki/Milwaukee_Road', 'America/Vancouver', 'en', ''],
                ['CPRR', 'Camas Prairie Railroad', 'https://en.wikipedia.org/wiki/Camas_Prairie_Railroad', 'America/Vancouver', 'en', ''],
                ['GN', 'Great Northern Railway', 'https://en.wikipedia.org/wiki/Great_Northern_Railway_(U.S.)', 'America/Vancouver', 'en', '']] if a[0] not in have])
