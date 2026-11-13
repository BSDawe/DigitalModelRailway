"""Add station rows to an on_*.csv timetable, with the trains that stop there (Brendan, 12 Nov 2026: stations from the CN Montreal
District employee timetable of 20 June 1948).

  add_stops(file, [dict(name=, between=(A, eA, B, eB), e=, stops={num: 'S' | 'F' | 'f10.05a' ...}, prov=, tz=), ...], source='...')

- between: two stations next to each other in the file (in either order) and their mileages in the source; e: the new station's mileage in the
  same source. The new row's mile is put in proportion between the file's miles for A and B.
- stops: by train number (every column with that number). 'S' or 'F': the time is estimated from the train's nearest calls above and
  below in the file, in proportion to the mileage, and marked '~' (estimated, not printed); 'F' adds the flag. Any other value is the cell as is.
- A train with no call on one side of the new row is left out (and reported)."""
import csv, io, re, shlex, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from ab_table import cell

def fmt(t):
    t %= 86400; h, m = divmod(t // 60, 60)
    return f"{(h % 12) or 12}.{m:02d}{'a' if h < 12 else 'p'}"

def add_stops(fn, specs, report=print):
    lines = open(fn, encoding='utf-8').read().split('\n')
    head = [l for l in lines if l.startswith('#')]
    body = [l for l in lines if l.strip() and not l.startswith('#')]
    trains = [dict(kv.split('=', 1) for kv in shlex.split(l[6:].strip())) for l in head if l.startswith('#train')]
    R = list(csv.reader(body)); hdr = R[0]; rows = R[1:]
    ci = {h: i for i, h in enumerate(hdr)}
    dirs = {t['col']: t.get('dir', 'down') for t in trains}
    bynum = {}
    for t in trains: bynum.setdefault(t.get('num', ''), []).append(t['col'])
    new = set()
    for sp in specs:
        A, eA, B, eB = sp['between']
        ia = [i for i, r in enumerate(rows) if r[1] == A]; ib = [i for i, r in enumerate(rows) if r[1] == B]
        best = None
        for i in ia:
            for j in ib:
                lo, hi = min(i, j), max(i, j)
                if all(id(rows[k]) in new for k in range(lo + 1, hi)) and (best is None or hi - lo < best[1] - best[0]): best = (lo, hi, i, j)
        if best is None: report(f'  {fn}: {sp["name"]}: {A} / {B} not next to each other: left out'); continue
        lo, hi, i, j = best
        mA, mB = float(rows[i][0]), float(rows[j][0])
        mile = mA + (sp['e'] - eA) / (eB - eA) * (mB - mA)
        row = [f'{mile:.1f}', sp['name'], '0', sp.get('prov', rows[i][3]), sp.get('tz', rows[i][4])] + [''] * (len(hdr) - 5)
        # place it among any rows already added in this gap, in mileage order
        k = lo + 1
        up = float(rows[lo][0]) <= float(rows[hi][0])
        while k < hi and ((float(rows[k][0]) < mile) if up else (float(rows[k][0]) > mile)): k += 1
        rows.insert(k, row); new.add(id(row))
        made = []
        for num, how in sp['stops'].items():
            for col in bynum.get(str(num), []):
                c = ci[col]
                if how not in ('S', 'F'): row[c] = how; made.append(col); continue
                above = next((q for q in range(k - 1, -1, -1) if rows[q][c].strip() and cell(rows[q][c])), None)
                below = next((q for q in range(k + 1, len(rows)) if rows[q][c].strip() and cell(rows[q][c])), None)
                if above is None or below is None: report(f'  {fn}: {sp["name"]}: {col} has no call on both sides: left out'); continue
                (aa, ad, *_), (ba, bd, *_) = cell(rows[above][c]), cell(rows[below][c])
                ma, mb = float(rows[above][0]), float(rows[below][0])
                f = 0.5 if mb == ma else (mile - ma) / (mb - ma)
                if dirs[col] == 'up': t0, t1, f = bd, aa, 1 - f
                else: t0, t1 = ad, ba
                d = t1 - t0
                if d < -43200: d += 86400
                if d > 43200: d -= 86400
                t = t0 + round(d * f / 60) * 60
                row[c] = ('~f' if how == 'F' else '~') + fmt(t); made.append(col)
        report(f'  {fn}: + {sp["name"]} ({mile:.1f}) {len(made)} trains')
    out = io.StringIO(); w = csv.writer(out, lineterminator='\n'); w.writerow(hdr); w.writerows(rows)
    open(fn, 'w', encoding='utf-8').write('\n'.join(head) + '\n' + out.getvalue())
