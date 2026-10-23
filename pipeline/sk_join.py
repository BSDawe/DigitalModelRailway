"""Through trains split across the section files (Brendan, 19 October 2026: "M165 seems to have been broken up ... other trains like train 62 ...").
Each file of the prairie tables is its own line, so a train that runs on from one table (or section) into the next showed as two or three trains.
Here each such train is joined into one: CHAINS lists the pieces in running order, as (spec key, column); the joined rows are written to
skj_<name>.csv (rows and cells exactly as in the section files, the meeting station made one row: arrival from the first piece, departure from
the next), the columns are taken out of the section lines, and one line is added for each joined train (a down chain and the up chain over the
same files share a line). Found by matching numbers at shared end stations within six hours (scan, 19 October), checked by hand; left out:
GN 7 / 8 and CP 7 / 8 at Winnipeg (different railways). The Mountaineer is joined from Chicago (OPTS: drawn as a CP train). No. 61 Regina -
Melville is joined: Table 192's "Winnipeg - Melville" line for 61 / 62 (Winnipeg 10.15 a.m. - Melville 5.15 p.m.; Melville 11.10 a.m. - Winnipeg
6.00 p.m.) is the through cars on Nos. 3 and 2 of Table 166, the same times (Brendan, 19 October): sk_cn_t192d is not built."""
import os, re
import ab_table
HERE = os.path.dirname(os.path.abspath(__file__))
C = lambda *p: [tuple(x.split(':')) for x in p]
CHAINS = {
 'cn65': (C('skcn192a:No65', 'skcn192b:M165', 'skcn182a:No65'), C('skcn182a:No66', 'skcn192b:M166', 'skcn192a:No66')),
 'cn27': (C('skcn199a:No27F', 'skcn199c:No27F'), C('skcn199c:M28S', 'skcn199a:M28S')),
 'cn61': (C('skcn192a:No61', 'skcn192b:No61'), C('skcn192b:No62', 'skcn192a:No62')),   # Regina section; the Winnipeg cars ride Nos. 3 / 2 (19 Oct)
 'cn63': (C('skcn168:No63', 'skcn192b:No63'), C('skcn192b:No64', 'skcn168:No64')),
 'cn70': (C('skcn200a:Mot70', 'skcn200b:Mot70'), C('skcn200b:Mot69', 'skcn200a:Mot69')),
 'cn71': (C('skcn193a:Mot71', 'skcn180:Mot71'), ()),
 'cn103': (C('skcn225d:Mot103', 'skcn225b:Mot103'), C('skcn225b:Mot106', 'skcn225d:Mot106')),
 'cp105': (C('skcp092a:No105', 'skcp092b:No105'), C('skcp092b:No106', 'skcp092a:No106')),
 'cp123': (C('skcp099a:No123', 'skcp106d:No123'), C('skcp106d:No124', 'skcp099a:No124')),
 'cp233': (C('skcp098a:M233', 'skcp098b:M233'), C('skcp098b:M234', 'skcp098a:M234')),
 'cn243': (C('skcn192b:M243', 'skcn182:M243'), C('skcn182:M244', 'skcn192b:M244')),
 'cp245': (C('skcp098a:M245', 'skcp103:M245'), C('skcp103:M246', 'skcp098a:M246')),
 'cn248': (C('skcn182:M248', 'skcn182a:M248'), C('skcn182a:M247', 'skcn182:M247')),
 'cn251': (C('skcn168:M251', 'skcn192b:M251'), C('skcn192b:M252', 'skcn168:M252')),
 'cp251': (C('skcp106b:M251', 'skcp106c:M251', 'skcp106d:M251'), ()),
 'cp252': (C('skcp106d:M252', 'skcp106c:M252', 'skcp106e:M252'), ()),
 'cp254': (C('skcp106e:M254', 'skcp106b:M254'), ()),
 'cn255': (C('skcn190:M255', 'skcn192b:M255'), C('skcn192b:M256', 'skcn190:M256')),
 'cn260': (C('skcn207:M260', 'skcn192b:M260'), ()),
 'cn270': (C('skcn193a:M270', 'skcn192b:M270'), ()),
 'cn293': (C('skcn199c:M293', 'skcn199a:M293'), C('skcn199a:M294', 'skcn199c:M294')),
 'cn315': (C('skcn175:M315', 'skcn176:M315'), C('skcn176:M316', 'skcn175:M316')),
 'cp327': (C('skcp116b:No327', 'skcp115:No327'), C('skcp115:No328', 'skcp116b:No328')),
 'cp405': (C('skcp111b:M405', 'skcp111a:M405'), C('skcp111a:M406', 'skcp111b:M406')),
 'cp429': (C('skcp123:M429', 'skcp123b:M429'), C('skcp123b:M430', 'skcp123:M430')),
 'cp433': (C('skcp110a:M433', 'skcp110b:M433'), C('skcp110b:M434', 'skcp110a:M434')),
 'cp439': (C('skcp125a:M439', 'skcp125b:M439'), C('skcp125b:M440', 'skcp125a:M440')),
 'cp449': (C('skcp092a:M449', 'skcp113:M449'), C('skcp113:M450', 'skcp092a:M450')),
 'cp481': (C('skcp117a:M481', 'skcp092a:M481'), C('skcp092a:M480', 'skcp117a:M480')),
 # the Mountaineer, one CP train Chicago - Medicine Hat (Brendan, 19 October): C&NW 403 / 404, the Soo leg, CP Table 108, CP Tables 6 (and the Medicine Hat file)
 'cp13': (C('skcnw017:No403', 'skcp108s:M13', 'skcp108:No13M', 'skcp005:No13'), C('skcp005:No14', 'skcp108:No14M', 'skcp108s:M14', 'skcnw017:No404')),
}

def _cell(txt):
    """-> (arrival part, departure part) of a cell, each a plain time with its sign, or ''"""
    txt = (txt or '').strip()
    if not txt: return '', ''
    a = re.search(r'ar\s+([^/]+)', txt); d = re.search(r'lv\s+([^/]+)', txt)
    if a or d: return (a.group(1).strip() if a else (d.group(1).strip() if d else '')), (d.group(1).strip() if d else a.group(1).strip())
    return txt, txt

def _pieces(spec, col):
    """the calls of one column in a line, one piece for each of its files that has the column: [(csv, table, train, [row indices in running order])]"""
    out = []
    for leg in spec['legs']:
        t = ab_table.load(os.path.join(HERE, leg['csv']))
        tr = next((x for x in t['trains'] if x['col'] == col), None)
        if tr is None: continue
        idx = [c[0] for c in ab_table.calls(t, tr)]
        if 'a' in leg:
            names = [r['station'] for r in t['rows']]; lo, hi = sorted((names.index(leg['a']), names.index(leg['b'])))
            idx = [i for i in idx if lo <= i <= hi]
        if idx: out.append((leg['csv'], t, tr, idx))
    return out

# through trains over several railways, drawn as one railway's train: chain name -> dict(rail spec key whose railway it is, notes)
OPTS = {
 'cp13': dict(rail='skcp108', long='Chicago – Milwaukee – St. Paul – Minneapolis – Portal – Moose Jaw – Medicine Hat (The Mountaineer)',
              note_d="The Mountaineer (CP No. 13), June 29 to September 3 from Chicago. Chicago - Minneapolis as C&NW No. 403 (over the Milwaukee Road St. Paul - Minneapolis); Minneapolis - Portal over the Soo Line (times of Soo No. 3, September 1947 table: the summer Soo table is not in hand); CP No. 13 from North Portal (Table 108) by Moose Jaw (Tables 6) on to Vancouver.",
              note_u="The Mountaineer (CP No. 14), July 5 to September 4 into Chicago. CP No. 14 by Moose Jaw to North Portal (Table 108); Portal - Minneapolis over the Soo Line (times of Soo No. 4, September 1947 table: they do not meet C&NW 404's 6.25 a.m. Minneapolis departure); Minneapolis - Chicago as C&NW No. 404."),
}

def build(specs):
    """write the joined files; -> (specs without the joined columns, the added specs)"""
    S = {s['key']: s for s in specs}; drop = {}; added = []
    for name, (down, up) in CHAINS.items():
        P = [(k, c) + p for k, c in down for p in _pieces(S[k], c)]
        Q = {(k, p[0]): p[1:] + (c,) for k, c in up for p in _pieces(S[k], c)}
        if up: assert [k for k, _ in up] == [k for k, _ in down][::-1], name
        rows = []                                            # [mile, station, principal, prov, tz, down cell, up cell]
        acc = 0.0; last = None                               # last: (spec key, printed mile) of the row before
        for n, (k, c, csv, t, tr, idx) in enumerate(P):
            R = t['rows']; q = Q.get((k, csv)); ui = set(q[2]) if q else set()
            ucol = q[3] if q else None
            span = range(min(idx + list(ui)), max(idx + list(ui)) + 1)
            order = [i for i in (span if tr['dir'] == 'down' else reversed(span)) if i in idx or i in ui]
            prev = None
            for i in order:
                r = R[i]
                if prev is not None: acc += abs(r['mile'] - R[prev]['mile'])
                prev = i
                dc = r.get(c, '') if i in idx else ''; uc = r.get(ucol, '') if ucol and i in ui else ''
                if rows and order.index(i) == 0 and rows[-1][1] == r['station']:          # the meeting station: one row
                    j = rows[-1]
                    da, _ = _cell(j[5]); _, dd = _cell(dc); _, ud = _cell(j[6]); ua, _ = _cell(uc)
                    j[5] = f'ar {da} / lv {dd}' if da and dd and da != dd else (da or dd)
                    j[6] = f'ar {ua} / lv {ud}' if ua and ud and ua != ud else (ua or ud)
                    if j[4] != r['tz']: j[4] = f"{j[4]}/{r['tz']}"
                    if r['principal'] == '1': j[2] = '1'
                    last = (k, r['mile']); continue
                if rows and order.index(i) == 0:
                    acc += abs(r['mile'] - last[1]) if last[0] == k else 0.5   # the next file of the same line (one mileage); else two stations at a border (Portal / North Portal)
                rows.append([round(acc, 1), r['station'], r['principal'], r['prov'], r['tz'], dc, uc]); last = (k, r['mile'])
        for k5 in (5, 6):
            got = [j for j in rows if j[k5]]
            if not got: continue
            first, last = (got[0], got[-1]) if k5 == 5 else (got[-1], got[0])
            if 'lv' not in first[k5]: first[k5] = 'lv ' + _cell(first[k5])[1]
            if 'ar' not in last[k5]: last[k5] = 'ar ' + _cell(last[k5])[0]
        o = OPTS.get(name, {})
        tr0 = P[0][4] if not o else next(p[4] for p in P if p[0] == o['rail'])
        secs = '; '.join(f"No. {tr['num']} {t['rows'][idx[0]]['station']} - {t['rows'][idx[-1]]['station']}" for k, c, csv, t, tr, idx in P)
        heads = [f"# Joined through train ({name}), sk_join.py: {', '.join(f'{k}:{c}' for k, c in down)}" + (f"; up {', '.join(f'{k}:{c}' for k, c in up)}" if up else ''),
                 '# Rows and times as in the section files (see them for the scans, signs and doubts). Miles: counted along the run from the first station.']
        nd = o.get('note_d') or f'Through train: {secs}. {P[0][4].get("note", "")}'
        tl = [f'#train col=D num={tr0["num"]} dir=down days="{tr0["days"]}" kind={tr0["kind"]} note="{nd}"']
        if up:
            U = [(k, c) + p for k, c in up for p in _pieces(S[k], c)]
            tru = U[0][4] if not o else next(p[4] for p in U if p[0] == o['rail'])
            usecs = '; '.join(f"No. {tr['num']} {t['rows'][idx[0]]['station']} - {t['rows'][idx[-1]]['station']}" for k, c, csv, t, tr, idx in U)
            nu = o.get('note_u') or f'Through train: {usecs}. {U[0][4].get("note", "")}'
            tl.append(f'#train col=U num={tru["num"]} dir=up days="{tru["days"]}" kind={tru["kind"]} note="{nu}"')
        fn = f'skj_{name}.csv'
        with open(os.path.join(HERE, fn), 'w') as f:
            f.write('\n'.join(heads + tl) + '\n')
            f.write('mile,station,principal,prov,tz,D' + (',U' if up else '') + '\n')
            for j in rows: f.write(','.join([str(j[0]), j[1] if ',' not in j[1] else f'"{j[1]}"', j[2], j[3], j[4], j[5]] + ([j[6]] if up else [])) + '\n')
        s0 = S[o.get('rail', down[0][0])]; a, b = rows[0][1], rows[-1][1]
        via = tuple(v for k, _ in down for v in S[k].get('via', ())); noplace = tuple(v for k, _ in down for v in S[k].get('noplace', ()))
        force = tuple(v for k, _ in down for v in S[k].get('force', ()))
        added.append(dict(s0, key='skj' + name, legs=[dict(csv=fn)], dirs=['to ' + b, 'to ' + a], long=o.get('long', f'{a} – {b} (through train No. {tr0["num"]})'),
                          cols=None, names={}, notes={}, via=via, noplace=noplace, force=force))
        for k, c in list(down) + list(up): drop.setdefault(k, set()).add(c)
    out = []
    for s in specs:
        if s['key'] in drop:
            allc = []
            for leg in s['legs']:
                for x in ab_table.load(os.path.join(HERE, leg['csv']))['trains']:
                    if x['col'] not in allc: allc.append(x['col'])
            cols = [c for c in allc if (s.get('cols') is None or c in s['cols']) and c not in drop[s['key']]]
            if not cols: continue
            s = dict(s, cols=cols)
        out.append(s)
    return out, added
