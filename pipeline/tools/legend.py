"""Rewrite the railway colour guide in page_template.html (Brendan, 23 Nov 2026): a list you can open and close, one swatch per railway, ordered by trains per week (busiest
first, no counts shown); subsidiaries and interurban subsidiaries are not listed apart from their parent; railways whose track is drawn but which run no trains of their own on
the map come last. Below it, sample icons for a train, a motor train and a steamer. It does not run at every build: run it by hand when railways are added.
Usage: python3 tools/legend.py    (needs the page built: it counts trains per week in fraser_valley_1949.html with Playwright)"""
import html, json, os, re, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TPL = os.path.join(HERE, 'page_template.html')
PAGE = os.path.join(HERE, 'fraser_valley_1949.html')
JS = r"""
const { chromium } = require('playwright');
(async () => { const b = await chromium.launch(); const p = await b.newPage();
  await p.goto('file://' + process.argv[2]); await p.waitForFunction(() => typeof TRIPS !== 'undefined' && TRIPS.length > 0, null, {timeout: 120000});
  const r = await p.evaluate(() => { const cnt = {};
    for (const d of Object.keys(SERVICES)) { const seen = new Set();
      for (const t of activeTrips(d)) { if (t.carry || t.early || t.water || seen.has(t.id)) continue; seen.add(t.id);
        const k = t.livery || KIND_COLOR[t.kind] || t.kind; cnt[k] = (cnt[k] || 0) + 1; } }
    return cnt; });
  console.log(JSON.stringify(r)); await b.close(); })();
"""
NAME = {'cn': 'Canadian National', 'cp': 'Canadian Pacific', 'bcer': 'B.C. Electric', 'gn': 'Great Northern', 'pge': 'Pacific Great Eastern', 'si': 'Spokane International',
        'wpy': 'White Pass & Yukon', 'nar': 'Northern Alberta', 'np': 'Northern Pacific', 'sps': 'Spokane, Portland & Seattle', 'up': 'Union Pacific', 'milw': 'Milwaukee Road',
        'arr': 'Alaska Railroad', 'gwwd': 'Greater Winnipeg Water District', 'onr': 'Ontario Northland', 'acr': 'Algoma Central', 'nfr': 'Newfoundland Railway',
        'nyc': 'New York Central', 'dh': 'Delaware & Hudson', 'tem': 'Temiscouata', 'cgt': 'Canada & Gulf Terminal', 'rs': 'Roberval & Saguenay', 'aj': 'Alma & Jonquière',
        'tir': 'Thousand Islands', 'mcrp': 'Maritime Coal, Railway & Power', 'snl': 'Sydney & Louisburg and Cumberland Railway', 'thb': 'Toronto, Hamilton & Buffalo',
        'hlb': 'Huntsville & Lake of Bays', 'lps': 'London & Port Stanley', 'qrl': 'Quebec Railway, Light & Power', 'ter': 'Texas Electric', 'ptc': 'Portland Traction',
        'bna': 'Baltimore & Annapolis', 'cnsm': 'North Shore Line', 'cae': 'Chicago Aurora & Elgin', 'rut': 'Rutland', 'mec': 'Maine Central', 'bc': 'Barre & Chelsea'}
TRACK_ONLY = {'prr': 'Pennsylvania', 'nh': 'New Haven', 'bm': 'Boston & Maine', 'cnw': 'Chicago & North Western', 'ic': 'Illinois Central', 'lv': 'Lehigh Valley',
              'bo': 'Baltimore & Ohio', 'cwi': 'Chicago & Western Indiana', 'cta': "Chicago Transit Authority ('L')", 'union': 'Union and terminal stations'}
def main():
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False) as f: f.write(JS); js = f.name
    out = subprocess.run(['node', js, PAGE], capture_output=True, text=True, timeout=600)
    os.unlink(js)
    cnt = json.loads(out.stdout.strip().splitlines()[-1])
    t = open(TPL).read()
    def band(k):
        for suf in ('gold', 'cream'):
            if f'--{k}-{suf}:' in t: return f'--{k}-{suf}'
        return None
    def sw(k, name):
        b = band(k)
        style = f'--c: var(--{k})' + (f'; --band: var({b})' if b else '')
        return f'<span><i class="sw rail{" banded" if b else ""}" style="{style}"></i>{html.escape(name)}</span>'
    rows = [sw(k, NAME[k]) for k, n in sorted(cnt.items(), key=lambda kv: -kv[1]) if k in NAME]
    missing = [k for k in cnt if k not in NAME]
    if missing: print('no name for', missing, file=sys.stderr)
    rows += [sw(k, nm) for k, nm in TRACK_ONLY.items() if f'--{k}:' in t]
    block = ('<!-- legend:start (tools/legend.py) -->\n    <details class="rails"><summary>Railway colours</summary><div class="legend">' + ''.join(rows) + '</div></details>\n'
             '    <div class="legend"><span><i class="sw consist plain"></i>Train</span><span><i class="sw motor"></i>Motor train</span><span><i class="sw boat"></i>Steamer</span></div>\n'
             '    <!-- legend:end -->')
    if '<!-- legend:start' in t: t = re.sub(r'<!-- legend:start.*?<!-- legend:end -->', lambda _: block, t, flags=re.S)
    else:
        i = t.index('    <div class="legend">\n      <span><i class="sw consist bcer"></i>'); j = t.index('</div>', i) + len('</div>')
        t = t[:i] + '    ' + block + t[j:]
    if '.sw.rail {' not in t:
        css = ('.sw.rail { width: 14px; height: 8px; border-radius: 2px; background: var(--c); } '
               '.sw.rail.banded { background: linear-gradient(var(--c) 0 30%, var(--band) 30% 70%, var(--c) 70%); }\n'
               '.sw.consist.plain { --gn: var(--muted); } .sw.motor { width: 20px; height: 7px; border-radius: 2px; --gn: var(--muted); '
               'background: linear-gradient(90deg, var(--gn) 0 47%, var(--paper) 47% 53%, var(--gn) 53%); }\n'
               'details.rails summary { cursor: pointer; font: 600 12px/1.6 var(--display); color: var(--ink); list-style: revert; margin-top: 6px; }\n'
               'details.rails .legend { margin-top: 4px; }\n')
        t = t.replace('.sw.ring { width: 10px;', css + '.sw.ring { width: 10px;', 1)
    open(TPL, 'w').write(t)
    print(f'{len(rows)} railways in the guide')
if __name__ == '__main__': main()
