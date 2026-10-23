"""Reader for the Alberta timetable transcriptions (ab_*.csv). A helper, not a build step.

File layout:
  # free comment lines: the table, its date, the time printed (Mountain), the signs, anything in doubt
  #train col=No7 num=7 dir=down days="Mon,Wed,Fri" kind=mixed from="Kerrobert" to="Lacombe" note="..."
  mile,station,principal,No7,No8
  0.0,Edmonton,1,lv 5.30p,ar 7.30a

One '#train' line for each train column. dir=down: the train runs down the rows as listed (times get later downwards); dir=up: it runs up them.
days: 'daily', 'ex Sun', or a comma list of Mon Tue Wed Thu Fri Sat Sun (the days it leaves its first station in the file).
kind: passenger, mixed or motor. from/to: where the train starts and ends if that is beyond the rows of the file.
A cell: '5.30p' (one time), 'lv 5.30p', 'ar 4.35a', 'ar 4.35a / lv 5.10a'; 'f' before a time = stops on signal; empty = does not call;
'12.00p' is noon and '12.00a' midnight; a '?' after a time marks a figure that could not be read with certainty.

  python3 ab_table.py file.csv ...     checks each file: times in order, speeds between calls plausible"""
import csv, re, shlex, sys
DAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
def load(fn):
    meta, trains, body = [], [], []
    for ln in open(fn):
        if ln.startswith('#train'):
            trains.append(dict(kv.split('=', 1) for kv in shlex.split(ln[6:].strip())))
        elif ln.startswith('#'): meta.append(ln[1:].strip())
        elif ln.strip(): body.append(ln)
    rows = list(csv.DictReader(body))
    for r in rows: r['mile'] = float(r['mile'])
    return dict(meta=meta, trains=trains, rows=rows)
def cell(txt):
    """-> (arr, dep, flag, doubt) in seconds after midnight as printed, or None if the train does not call"""
    arr = dep = None
    for m in re.finditer(r'(ar|lv)?\s*[a-z]?\s*(\d+)\.(\d+)([ap])', txt or ''):
        t = (int(m.group(2)) % 12 + (12 if m.group(4) == 'p' else 0)) * 3600 + int(m.group(3)) * 60
        if m.group(1) == 'ar': arr = t
        elif m.group(1) == 'lv': dep = t
        else: arr = dep = t
    if arr is None and dep is None: return None
    return (arr if arr is not None else dep), (dep if dep is not None else arr), bool(re.search(r'\bf\s*\d', txt)), '?' in txt
def shift_text(txt, secs=-3600):
    """the same cell with every time moved by secs (Mountain to Pacific: an hour earlier); a '?' is dropped"""
    def f(m):
        t = ((int(m.group(1)) % 12 + (12 if m.group(3) == 'p' else 0)) * 3600 + int(m.group(2)) * 60 + secs) % 86400
        return f"{(t // 3600 - 1) % 12 + 1}.{t % 3600 // 60:02d}{'p' if t >= 43200 else 'a'}"
    return re.sub(r'(\d+)\.(\d+)([ap])', f, (txt or '').replace('?', ''))
def calls(tab, tr, shift=0):
    """the calls of one train in running order: [(row index, arr, dep, flag)], times counting on past midnight, plus shift seconds"""
    idx = range(len(tab['rows'])) if tr['dir'] == 'down' else range(len(tab['rows']) - 1, -1, -1)
    out, base, prev = [], 0, None
    for i in idx:
        c = cell(tab['rows'][i].get(tr['col'], ''))
        if not c: continue
        t = []
        for x in c[:2]:
            x += base
            if prev is not None and x < prev - 4 * 3600: base += 86400; x += 86400
            prev = x; t.append(x + shift)
        out.append((i, t[0], t[1], c[2]))
    return out
def weekdays(days):
    d = days.strip()
    if d == 'daily': return [1] * 7
    if d == 'ex Sun': return [1, 1, 1, 1, 1, 1, 0]
    got = [x.strip() for x in d.split(',')]
    assert all(x in DAYS for x in got), days
    return [int(x in got) for x in DAYS]
def check(fn):
    tab = load(fn); bad = 0
    cols = [c for c in tab['rows'][0] if c not in ('mile', 'station', 'principal', 'prov', 'tz')]     # prov, tz: Saskatchewan files
    if sorted(cols) != sorted(t['col'] for t in tab['trains']): print(f'  !! columns {cols} against #train lines {[t["col"] for t in tab["trains"]]}'); bad += 1
    for tr in tab['trains']:
        for k in ('col', 'num', 'dir', 'days', 'kind'):
            if k not in tr: print(f'  !! {tr.get("col")}: no {k}'); bad += 1
        weekdays(tr['days']); cs = calls(tab, tr); R = tab['rows']
        if len(cs) < 2: print(f'  !! {tr["col"]}: {len(cs)} calls'); bad += 1; continue
        for (i, a1, d1, _), (j, a2, d2, _) in zip(cs, cs[1:]):
            dm = abs(R[j]['mile'] - R[i]['mile']); dt = (a2 - d1) / 3600
            if dt <= 0 or d2 < a2: print(f'  !! {tr["col"]}: time goes back {R[i]["station"]} -> {R[j]["station"]}'); bad += 1
            elif not 6 < dm / dt < 62: print(f'  ?  {tr["col"]}: {R[i]["station"]} -> {R[j]["station"]} {dm:.1f} mi in {dt * 60:.0f} min = {dm / dt:.0f} mph'); bad += 1
        f = lambda x: f'{x // 3600 % 24:02d}:{x % 3600 // 60:02d}'
        print(f'  {tr["col"]:8s} No. {tr["num"]:8s} {tr["days"]:16s} {tr["kind"]:9s} {R[cs[0][0]]["station"]} {f(cs[0][2])} -> {R[cs[-1][0]]["station"]} {f(cs[-1][1])}, {len(cs)} calls, '
              f'{abs(R[cs[-1][0]]["mile"] - R[cs[0][0]]["mile"]) / max((cs[-1][1] - cs[0][2]) / 3600, 1e-9):.0f} mph overall')
    m = [r['mile'] for r in tab['rows']]
    if m != sorted(m) and m != sorted(m, reverse=True): print('  ?  miles are not in order (fine only if the table has a spur or a second mileage)')
    return bad
if __name__ == '__main__':
    for fn in sys.argv[1:]:
        print(fn); n = check(fn); print('  ok' if not n else f'  {n} to look at')
