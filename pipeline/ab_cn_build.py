"""Canadian National secondary and branch lines in Alberta, from the May 1948 Official Guide (tables of April 25, 1948; transcribed in ab_cn_t*.csv).
The machinery is ab_lines.py: track from the national network, the Canadian Northern and Grand Trunk Pacific backup sets where the network
has none, a straight estimate (drawn dashed) where neither has it. Reads the lines already on the map for shared track and stations
(needs mainline_build and nar_build). The main line east of Edmonton (Table 75) is part of the cn line, in mainline_build.py."""
import os
from ab_lines import build, trace, report
G = 'Canadian National Table %s, April 25, 1948 (Official Guide, May 1948)'
def L(key, legs, dirs, long, tab, cols=None, **kw):
    legs = [dict(csv=l) if isinstance(l, str) else dict(csv=l[0], a=l[1], b=l[2]) for l in legs]
    return dict(key=key, rail='cn', legs=legs, dirs=dirs, short='CN ' + tab, long=long, src=G % tab, cols=cols, **kw)
SPECS = [
 L('cn_171', [('ab_cn_t171.csv', 'Edmonton', 'Lloydminster')], ['to Vegreville and Lloydminster', 'to Edmonton'], 'Edmonton – Fort Saskatchewan – Vegreville – Vermilion – Lloydminster', '171'),
 L('cn_203', ['ab_cn_t203a.csv'], ['to St. Paul and Heinsburg', 'to Edmonton'], 'Edmonton – Smoky Lake – Abilene – St. Paul – Heinsburg', '203'),
 L('cn_203b', ['ab_cn_t203b.csv'], ['to Bonnyville and Beaver River', 'to Abilene'], 'Abilene – Bonnyville – Beaver River', '203'),
 L('cn_208', ['ab_cn_t208.csv'], ['to Camrose, Mirror and Calgary', 'to Edmonton'], 'Edmonton – Camrose – Mirror – Three Hills – Calgary', '208'),
 L('cn_205', ['ab_cn_t205.csv'], ['to Camrose and Alliance', 'to Edmonton'], 'Edmonton – Camrose – Alliance', '205'),
 L('cn_205b', ['ab_cn_t205b.csv'], ['to Tofield, Camrose and Alliance', 'to Edmonton'], 'Edmonton – Tofield – Camrose – Alliance', '205'),
 L('cn_168', [('ab_cn_t168.csv', 'Calgary', 'Sibbald')], ['to Drumheller, Hanna and Saskatoon', 'to Calgary'], 'Calgary – Drumheller – Hanna – Oyen – Sibbald', '168', cols=['No9', 'No10']),
 L('cn_209', [('ab_cn_t209.csv', 'Edmonton', 'Munson Junc.'), ('ab_cn_t168.csv', 'Munson Junction', 'Calgary')], ['to Stettler, Drumheller and Calgary', 'to Edmonton'],
   'Edmonton – Camrose – Stettler – Big Valley – Drumheller – Calgary', '209', cols=['No26', 'No25'],
   places={'Stettler': (-112.700115, 52.321648)}),   # the CN station, on the north-south line (Brendan, 8 October 2026)
 L('cn_204', ['ab_cn_t204.csv'], ['to Rocky Mountain House and Brazeau', 'to Mirror'], 'Mirror – Red Deer – Rocky Mountain House – Brazeau', '204',
   places={'Red Deer': (-113.805461, 52.271622)}, force=[('Red Deer Junction', 'Red Deer')]),   # 9.9 mi by the wye against 8.4 printed     # the downtown CN station, reached over CP track after 1941 (Brendan's traces)
 L('cn_217', ['ab_cn_t217.csv'], ['to Warden and Mirror', 'to Hanna'], 'Hanna – Warden – Alix – Mirror', '217'),
 L('cn_216', ['ab_cn_t216.csv'], ['to Camrose', 'to Vegreville'], 'Vegreville – Ryley – Camrose', '216'),
 L('cn_193', ['ab_cn_t193.csv'], ['to East Coulee and Trefoil', 'to Drumheller'], 'Drumheller – East Coulee – Trefoil', '193'),
 L('cn_215', ['ab_cn_t215.csv'], ['to Wardlow', 'to Hanna'], 'Hanna – Sunnynook – Wardlow', '215'),
 L('cn_211', ['ab_cn_t211.csv'], ['to Hemaruka', 'to Loverna'], 'New Brigden – Sedalia – Hemaruka', '211'),
 L('cn_210', ['ab_cn_t210.csv'], ['to Whitecourt', 'to Edmonton'], 'Edmonton – St. Albert – Onoway – Sangudo – Whitecourt', '210',
   # out of Edmonton by the main line towards B.C. to where the St. Albert line crossed it (the direct line was gone by 1948: traces/hr_rails)
   via=[('Edmonton', 'St. Albert line junction', 6.6), ('Edmonton', 'main line, west of Edmonton', 3.3)],
   places={'St. Albert line junction': (-113.5931, 53.5801), 'main line, west of Edmonton': (-113.53099, 53.572714)}),
 L('cn_218', ['ab_cn_t218.csv'], ['to Athabasca', 'to Edmonton'], 'Edmonton – Morinville – Clyde – Athabasca', '218'),
 L('cn_213', ['ab_cn_t213.csv'], ['to Luscar and Mountain Park', 'to Edson'], 'Edson – Coalspur – Luscar – Mountain Park', '213', cols=['No179', 'No180'], force=[('Leyland', 'Cadomin')]),
 L('cn_213f', [('ab_cn_t213.csv', 'Edson', 'Coalspur'), 'ab_cn_t213a.csv'], ['to Coalspur and Foothills', 'to Edson'], 'Edson – Coalspur – Foothills', '213 and 213a', cols=['M317', 'M318']),
]
if __name__ == '__main__':
    if os.environ.get('AB_DRY'):
        for s in SPECS:
            if os.environ['AB_DRY'] in ('1', s['key']): rows, trains, pieces = trace(s); report(s, rows, pieces)
    else: build(SPECS)
