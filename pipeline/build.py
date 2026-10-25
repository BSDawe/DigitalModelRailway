#!/usr/bin/env python3
"""Incremental build. Each step (one script, one or a few lines of the map) is run on its own and what it added or changed is saved as a part
file in parts/<step>.json: its lines for the page, and its rows for the GTFS feed. Putting the parts together (viz_data.json, gtfs/, the zip and
the page) is a cheap merge, so a fix to one line means re-running that step and the steps that read it, not the whole chain.

  python3 build.py              re-run only the steps that are out of date (script or input files changed, or a step they read was re-run)
  python3 build.py kv_build     re-run the named step(s) and whatever reads them
  python3 build.py --all        re-run everything
  python3 build.py --assemble   no step is run: merge the parts and write the page
  python3 build.py --status     list the steps, what they read, and which are out of date

Steps and their order are in steps.json. A step's script works exactly as before (reads viz_data.json and appends to gtfs/); build.py puts the
state of the earlier steps in place, runs it quietly (log in build_logs/), and keeps the difference. Only a summary and any failure are printed."""
import hashlib, json, os, re, subprocess, sys, time, zipfile
from collections import Counter
HERE = os.path.dirname(os.path.abspath(__file__)); os.chdir(HERE)
PARTS, GT, LOGS, VIZ, ZIP = 'parts', 'gtfs', 'build_logs', 'viz_data.json', 'bcer_fraser_valley_1949_gtfs.zip'
STEPS = json.load(open('steps.json'))['steps']
NAMES = [s['name'] for s in STEPS]
dumps = lambda o: json.dumps(o, separators=(',', ':'))
sha = lambda b: hashlib.sha1(b if isinstance(b, bytes) else b.encode()).hexdigest()[:12]

def inputs(step):
    """the script, the local modules it imports and the data files it names (found in its source), plus anything listed under 'inputs'"""
    seen, todo = [], [step['script']]
    while todo:
        f = todo.pop()
        if f in seen or not os.path.exists(f): continue
        seen.append(f); src = open(f).read()
        todo += [m + '.py' for m in re.findall(r'^\s*(?:from|import)\s+(\w+)', src, re.M)]
    files = set(seen) | set(step.get('inputs', []))
    import glob as _glob                                            # files a script finds by a pattern (a folder of traces) are inputs too
    pats = list(step.get('input_globs', []))                         # (24 October 2026: a new trace in traces/saskatchewan/ did not make sk_build stale)
    for f in seen:
        for m in re.findall(r"os\.path\.join\(HERE,\s*((?:'[^']*'\s*,\s*)*'[^']*\*[^']*')\s*\)", open(f).read()):
            pats.append(os.path.join(*re.findall(r"'([^']*)'", m)))
        for m in re.findall(r"glob\.glob\('([^']*\*[^']*)'\)", open(f).read()): pats.append(m)
    for pat in pats: files |= set(_glob.glob(pat))
    for f in seen:
        for m in re.findall(r"'([\w.-]+\.(?:csv|tsv|json|pkl|kml|kmz|gpkg|txt))'", open(f).read()): files |= {m, 'nrwn/' + m, 'traces/' + m, 'places/' + m}
    return sorted(f for f in files if os.path.exists(f) and f not in (VIZ, 'steps.json') and not f.startswith(PARTS))

def signature(step):
    return {f: sha(open(f, 'rb').read()) for f in inputs(step)}

# ---- state: the page data (a dict) and the GTFS files (name -> list of lines)
def read_state():
    viz = json.load(open(VIZ)) if os.path.exists(VIZ) else {}
    gt = {fn: open(os.path.join(GT, fn), newline='').read().splitlines(keepends=True) for fn in sorted(os.listdir(GT))} if os.path.isdir(GT) else {}
    return viz, gt

def write_state(viz, gt):
    os.makedirs(GT, exist_ok=True)
    for fn in os.listdir(GT):
        if fn not in gt: os.remove(os.path.join(GT, fn))
    for fn, lines in gt.items(): open(os.path.join(GT, fn), 'w', newline='').write(''.join(lines))
    if viz: open(VIZ, 'w').write(dumps(viz))
    elif os.path.exists(VIZ): os.remove(VIZ)

def diff(before, after):
    (v0, g0), (v1, g1) = before, after
    l0 = {l['key']: l for l in v0.get('lines', [])}; l1 = {l['key']: l for l in v1.get('lines', [])}
    k0 = [k for k in l0 if k in l1]; k1 = list(l1)
    changed = {k for k in l1 if k not in l0 or dumps(l0[k]) != dumps(l1[k])}
    part = dict(top={k: v for k, v in v1.items() if k != 'lines' and (k not in v0 or dumps(v0[k]) != dumps(v))}, top_removed=[k for k in v0 if k != 'lines' and k not in v1],
                lines_removed=[k for k in l0 if k not in l1], append=[], gtfs={})
    for cut in range(len(k1), -1, -1):                       # the lines moved to (or added at) the end; the rest keep their place
        tail = k1[cut:]
        if k1[:cut] == [k for k in k0 if k not in tail]: part['append'] = tail; break
    else: part['order'] = k1
    part['lines_set'] = {k: l1[k] for k in k1 if k in changed or k in part['append']}
    for fn in sorted(set(g0) | set(g1)):
        a, b = g0.get(fn, []), g1.get(fn)
        if b is None: part['gtfs'][fn] = dict(delete=True); continue
        if a == b: continue
        if b[:len(a)] == a: part['gtfs'][fn] = dict(removed=[], added=b[len(a):]); continue
        have = Counter(a); added = []
        for ln in b:
            if have[ln] > 0: have[ln] -= 1
            else: added.append(ln)
        part['gtfs'][fn] = dict(removed=[ln for ln, n in have.items() for _ in range(n)], added=added)
    return part

def apply(state, part):
    viz, gt = state
    for k in part['top_removed']: viz.pop(k, None)
    viz.update(part['top'])
    if part['lines_set'] or part['lines_removed'] or part['append'] or 'lines' in viz:
        lines = {l['key']: l for l in viz.get('lines', [])}
        for k in part['lines_removed']: lines.pop(k, None)
        for k in part['append']: lines.pop(k, None)
        for k, l in part['lines_set'].items(): lines[k] = l                          # in place if it was there, else at the end, in order
        if 'order' in part: lines = {k: lines[k] for k in part['order'] if k in lines} | lines
        if lines or 'lines' in viz: viz.pop('lines', None); viz['lines'] = list(lines.values())
    for fn, d in part['gtfs'].items():
        if d.get('delete'): gt.pop(fn, None); continue
        cur = gt.get(fn, [])
        if d['removed']:
            gone = Counter(d['removed']); keep = []
            for ln in cur:
                if gone[ln] > 0: gone[ln] -= 1
                else: keep.append(ln)
            cur = keep
        gt[fn] = cur + d['added']
    return viz, gt

def load_part(name):
    p = os.path.join(PARTS, name + '.json')
    return json.load(open(p)) if os.path.exists(p) else None

def stale_reason(step, part, rerun):
    if part is None: return 'no part yet'
    sig = signature(step)
    ch = [f for f in sig if part['sig'].get(f) != sig[f]]         # an input that is absent (bcer_inputs.zip not unpacked) does not make a step stale
    if ch: return 'changed: ' + ', '.join(ch[:4])
    dep = [d for d in step.get('needs', []) if d in rerun or part['needs_sig'].get(d) != part_sha(d)]
    if dep: return 'reads ' + ', '.join(dep)
    return None

def part_sha(name):
    p = os.path.join(PARTS, name + '.json')
    return sha(open(p, 'rb').read()) if os.path.exists(p) else None

def finish(state):
    viz, gt = state
    import merge_stations                                              # joint stations: one stop for two railways (Brendan, 17 October 2026)
    unused = merge_stations.apply(viz, gt)
    if unused: print('  merge_stations: no such stations', unused)
    import real_ends                                                   # where trains that run off the map really start and end
    miss = real_ends.apply(viz, gt)
    if 'calendar.txt' in gt:                                           # a service added by two steps (W_ day lists) is written once
        seen = set(); gt['calendar.txt'] = [l for l in gt['calendar.txt'] if not (l.split(',')[0] in seen or seen.add(l.split(',')[0]))]
    if miss: print('  real_ends: no such trips', miss)
    write_state(viz, gt)
    with zipfile.ZipFile(ZIP, 'w', zipfile.ZIP_DEFLATED) as z:
        for fn in sorted(gt): z.write(os.path.join(GT, fn), fn)
    out = subprocess.run([sys.executable, 'make_page.py'], capture_output=True, text=True)
    if out.returncode: sys.exit('make_page failed:\n' + out.stderr[-800:])
    site = subprocess.run([sys.executable, 'make_site.py'], capture_output=True, text=True)    # the hosted site: page + data files (GitHub Pages)
    if site.returncode: sys.exit('make_site failed:\n' + site.stderr[-800:])
    n = {fn: len(l) - 1 for fn, l in gt.items()}
    print(f"assembled: {len(viz.get('lines', []))} lines on the page; GTFS {n.get('routes.txt')} routes, {n.get('trips.txt')} trips, {n.get('stops.txt')} stops; {out.stdout.strip()}; {site.stdout.strip()}")

def main(argv):
    flags = {a for a in argv if a.startswith('--')}; named = [a for a in argv if not a.startswith('--')]
    for a in named:
        if a not in NAMES: sys.exit(f'no step called {a}; steps: ' + ' '.join(NAMES))
    os.makedirs(PARTS, exist_ok=True); os.makedirs(LOGS, exist_ok=True)
    if '--status' in flags:
        for s in STEPS:
            p = load_part(s['name']); why = stale_reason(s, p, set())
            gone = [f for f in (p['sig'] if p else {}) if not os.path.exists(f)]
            print(f"{s['name']:18s} {'OUT OF DATE (' + why + ')' if why else 'ok, inputs absent' if gone else 'ok':40s} lines: {' '.join(p['lines_set']) if p else '-':40.40s} reads: {' '.join(s.get('needs', [])) or '-'}")
        return
    state = ({}, {}); rerun = set()
    for s in STEPS:
        name = s['name']; part = load_part(name)
        why = None if '--assemble' in flags else 'asked' if ('--all' in flags or name in named) else stale_reason(s, part, rerun)
        if '--assemble' in flags and part is None: sys.exit(f'no part for {name}: run build.py first')
        if why is None: state = apply(state, part); continue
        write_state(*state); t0 = time.time()
        with open(os.path.join(LOGS, name + '.log'), 'w') as log:
            rc = subprocess.run([sys.executable, s['script']], stdout=log, stderr=subprocess.STDOUT).returncode
        if rc:
            print(f'FAILED: {name} (see {LOGS}/{name}.log)'); print(''.join(open(os.path.join(LOGS, name + '.log')).readlines()[-8:]))
            write_state(*state); sys.exit(1)
        after = read_state(); part = diff(state, after)
        part.update(step=name, sig=signature(s), needs_sig={d: part_sha(d) for d in s.get('needs', [])})
        open(os.path.join(PARTS, name + '.json'), 'w').write(dumps(part))
        state = after; rerun.add(name)
        print(f"ran {name:18s} {time.time() - t0:5.1f}s  ({why})  lines: {' '.join(part['lines_set']) or '-'}")
    if not rerun and '--assemble' not in flags: print('nothing out of date')
    finish(state)

if __name__ == '__main__': main(sys.argv[1:])
