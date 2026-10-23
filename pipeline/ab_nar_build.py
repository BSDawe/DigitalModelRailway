"""Northern Alberta Railways branches, from the tables of April 25, 1948 in the May 1948 Official Guide (ab_nar_t179*.csv): McLennan - Peace River -
Hines Creek (Nos. 5, 6); Carbondale - Busby - Barrhead (Nos. 25, 26) (the branch from Busby is Brendan's trace, traces/nar_barrhead_branch.tsv); Edmonton - Carbondale -
Lac La Biche (Nos. 7, 8) - Waterways (Nos. 23, 24). The machinery is ab_lines.py. Reads the nar line for shared track and stations (needs nar_build and ab_cn_build)."""
import os
from ab_lines import build, trace, report
def L(key, csv_, dirs, long, tab, **kw):
    return dict(key=key, rail='nar', legs=[dict(csv=csv_)], dirs=dirs, short='NAR ' + tab, long=long, cols=None,
                src=f'Northern Alberta Railways, table of April 25, 1948 (Official Guide, May 1948, Table {tab})', **kw)
SPECS = [
 L('nar_bh', 'ab_nar_t179b.csv', ['to Barrhead', 'to Carbondale'], 'Carbondale – Morinville – Busby – Barrhead', '179b'),
 L('nar_ww', 'ab_nar_t179c.csv', ['to Lac La Biche and Waterways', 'to Edmonton'], 'Edmonton – Carbondale – Lac La Biche – Waterways', '179c',
   # the old line left the Barrhead line at Carbondale and ran by Bon Accord, Fedorah and Opal to Egremont (Brendan's trace, 7 October 2026)
   ),
 L('nar_hc', 'ab_nar_t179a.csv', ['to Peace River and Hines Creek', 'to McLennan'], 'McLennan – Peace River – Fairview – Hines Creek', '179a'),
]
if __name__ == '__main__':
    if os.environ.get('AB_DRY'):
        for s in SPECS: rows, trains, pieces = trace(s); report(s, rows, pieces)
    else: build(SPECS)
