"""One-shot import of Brendan's CN Maritimes bank (8 November 2026): CN_Maritimes.gpkg = Wikipedia's Canadian Government Railways map data (51 lines, from the
maps embedded in the Wikipedia articles) + 82 of Brendan's own traces (Mulgrave - Point Tupper, Halifax North Street - Deepwater Terminal, Pacific Junction)
-> traces/maritimes/cn.geojson, brendan.geojson, industrial.geojson. The CN pieces of the Canadian Northern collection (Inverness & Richmond, Halifax & South
Western, Middleton & Victoria Beach) are added from traces/cnor_all.geojson. Kept as the record of what was done; later additions are new files in
traces/maritimes/ (see its README), not re-runs of this.
    python3 tools/mar_import_cgr.py /path/to/CN_Maritimes.gpkg
Status describes the TRACK (there in 1948 or not); who may use it is 'own'. Steps: names cleaned of HTML; duplicates dropped (York & Carleton twice); Wikipedia lines cut where they lie within 15 m of one of Brendan's traces (his trace is
the line there); Halifax & Cape Breton split at his junction (trace 65: the 1948 line to Mulgrave / the post-1955 causeway leg); the NTR cut at the N.B. boundary
point already used by the Quebec build (the tail before it is in the Quebec collection); every piece gets a status (see README)."""
import sqlite3, struct, re, html, json, os, sys
from pyproj import Transformer
from shapely.geometry import LineString, Point
from shapely.ops import unary_union, substring
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); OUT = os.path.join(ROOT, 'traces', 'maritimes')
T = Transformer.from_crs(4326, 32620, always_xy=True); TI = Transformer.from_crs(32620, 4326, always_xy=True)
def coords(g):
    env = {0: 0, 1: 32, 2: 48, 3: 48, 4: 64}[(g[3] >> 1) & 7]; w = g[8 + env:]; bo = '<' if w[0] == 1 else '>'
    n = struct.unpack(bo + 'I', w[5:9])[0]; return [struct.unpack(bo + 'dd', w[9 + 16 * i:25 + 16 * i]) for i in range(n)]
F = {}
for fid, g, t, d in sqlite3.connect(sys.argv[1]).execute('select fid, geom, title, description from canadian_government_railways'):
    F[fid] = dict(fid=fid, title=html.unescape(re.sub('<[^>]+>', '', t)) if t else None, desc=d or '', coords=coords(g))
# Brendan's Port Hawkesbury mainline piece (deleted from the gpkg by accident, sent as WKT 8 Nov 2026 17:06)
F[134] = dict(fid=134, title=None, desc='', coords=[(-61.36827384679986, 45.61901294088560), (-61.36808345009756, 45.61868770600618), (-61.3676247971208, 45.61808524490734), (-61.36552264328927, 45.61584731551746), (-61.36441164302639, 45.61469616436128), (-61.36344997237266, 45.61363276957500), (-61.36283838639224, 45.61309697530393), (-61.36201651032662, 45.61256635754631), (-61.35998730015884, 45.61136243008631), (-61.35939660279224, 45.61105581391578), (-61.35855014309822, 45.61067867360224), (-61.35597167463180, 45.60974423468279), (-61.35413657536540, 45.60916750254024), (-61.35350714921275, 45.60894008540781), (-61.35309521158032, 45.60870627732125)])
for f in F.values(): f['ls'] = LineString([T.transform(x, y) for x, y in f['coords']])
NOTE_W = 'Wikipedia map data, Canadian Government Railways (and the linked railway maps), supplied by Brendan, 8 Nov 2026'
NOTE_B = "Brendan's trace, 8 Nov 2026"; NOTE_C = 'Canadian Northern collection (Wikipedia maps), traces/cnor_all.geojson'
FILES = {'cn': [], 'brendan': [], 'industrial': []}; REPORT = []
def add(file, ls, own, name, note, fid, group, status, why=None, constituent=None, branch=None):
    if ls.length < 1: return
    p = dict(own=own, name=name, constituent=constituent or name, branch=branch or '', note=note, cost=1.0, fid=fid, group=group, status=status)
    if why: p['why'] = why
    FILES[file].append(dict(type='Feature', properties=p, geometry=dict(type='LineString', coordinates=[[round(a, 6), round(b, 6)] for a, b in (TI.transform(x, y) for x, y in ls.coords)])))
# ---- Brendan's traces: 52-115 Mulgrave - Point Tupper (+ 134), 116-131 Halifax; 95 = the causeway approach (post-1955)
tup = list(range(52, 116)) + [134]; hal = list(range(116, 132)); btr = []
for i in tup + hal:
    area = 'Mulgrave - Point Tupper' if i in tup else 'Halifax Deepwater Terminal and North Street'
    add('brendan', F[i]['ls'], 'cn', f"{area}: Brendan's trace {i}", NOTE_B, i, 'brendan', 'post1948' if i == 95 else 'ok', constituent=area,
        why="the causeway approach west of Port Hastings Jct. (rail across the Canso Causeway from May 1955; the Inverness & Richmond starts at traces 62 / 92)" if i == 95 else None)
    btr.append(F[i]['ls'])
bu = unary_union(btr).buffer(15)
# ---- Wikipedia pieces
NOT_CN = {28: ('nscc', 'Railroad of the Nova Scotia Coal Co.'), 33: ('acc', 'Railroad of the Acadia Coal Co.'), 36: ('nssc', 'Railway of the Nova Scotia Steel and Coal Co.'), 37: ('vale', 'Vale Railway')}
# 'check' = was this track there in 1948? (Whether trains ran over it is the timetables' business, not the track's: a branch with no train is simply not routed over.)
CHECK = {8: 'Realignment at Tide Head: alternate alignment, which one was in use in 1948?', 17: 'NB&PEI "Ferry Reroute": earlier or later than 1948?',
         20: 'Cape Traverse branch: still there in 1948?', 23: 'PEI Short Line Cutoff: there in 1948?', 26: 'PEI main line realignment to Elmira: before or after 1948?',
         41: 'Dartmouth Branch 1896: superseded alignment? (compare fid 40)', 11: 'Elgin, Petitcodiac & Havelock: still there in 1948?', 12: 'Elgin Branch: still there in 1948?',
         14: 'Albert Southern: still there in 1948?', 13: 'Albert Railway: still there in 1948?'}
for fid, f in F.items():
    if 51 < fid < 132 or fid == 134: continue
    if fid == 7: REPORT.append('fid 7 York and Carleton: exact duplicate of fid 1, dropped'); continue
    title, branch = f['title'], f['desc']
    if fid == 133: title, branch = 'Intercolonial Railway', 'Pacific Jct 1915'
    if fid == 132: title, branch = 'Intercolonial Railway', 'Moncton - Pacific Jct. approach (NTR wye)'
    nm = f'{title}: {branch}' if branch else title
    own, status, why, file = 'cn', 'ok', None, 'cn'
    if fid in NOT_CN: own, nm, file = NOT_CN[fid][0], NOT_CN[fid][1], 'industrial'; title = nm     # status stays 'ok': whose track it is is 'own', not the status
    if fid in CHECK: status, why = 'check', CHECK[fid]
    if fid == 4: own, status, why = 'tem', 'quebec_overlap', 'Temiscouata Railway: mostly in Quebec, which already has it (ontem)'
    ls = f['ls']; pieces = [(ls, nm, status, why)]
    if fid == 29:
        j = F[65]['ls'].interpolate(0); d = ls.project(j); REPORT.append(f'fid 29 split {d:.0f} m along at Brendan\'s junction (trace 65), gap {ls.distance(j):.0f} m')
        pieces = [(substring(ls, 0, d), nm + ' (west of Mulgrave junction)', status, why), (substring(ls, d, ls.length), nm + ' (north leg to the causeway)', 'post1948', "Auld's Cove - Canso Causeway line: rail across the causeway from May 1955")]
    if fid == 6:
        bd = Point(T.transform(-68.7317, 47.372)); d = ls.project(bd); REPORT.append(f'fid 6 NTR cut {d / 1000:.1f} km along at the N.B. boundary point ({ls.distance(bd):.0f} m off)')
        pieces = [(substring(ls, 0, d), nm + ' (west of the N.B. boundary)', 'quebec_overlap', 'the Quebec collection already carries the NTR to the N.B. boundary'), (substring(ls, d, ls.length), nm, status, why)]
    for g, n, s, w in pieces:
        if s in ('ok', 'check') and g.intersects(bu):
            left = g.difference(bu); parts = [x for x in (list(left.geoms) if hasattr(left, 'geoms') else [left]) if not x.is_empty and x.length >= 60]
            REPORT.append(f'fid {fid} {n[:40]}: {g.length - sum(x.length for x in parts):.0f} m of {g.length:.0f} m under Brendan\'s traces cut, {len(parts)} piece(s) kept')
            for m, x in enumerate(parts): add(file, x, own, n + (f' (part {m + 1})' if len(parts) > 1 else ''), NOTE_W, fid, 'wikipedia', s, w, title, branch)
        else: add(file, g, own, n, NOTE_W, fid, 'wikipedia', s, w, title, branch)
# ---- Canadian Northern collection: the Maritime pieces
for f in json.load(open(os.path.join(ROOT, 'traces', 'cnor_all.geojson')))['features']:
    p = f['properties']
    if p['source_map'] not in ('Inverness and Richmond Railway', 'Halifax and South Western Railway', 'Middleton and Victoria Beach Railway'): continue
    g = f['geometry']; title = html.unescape(re.sub('<[^>]+>', '', p['title'])); br = p.get('description') or ''; vb = 'Victoria Beach' in title
    for c in ([g['coordinates']] if g['type'] == 'LineString' else g['coordinates']):
        add('cn', LineString([T.transform(x, y) for x, y in c]), 'cn', f'{title}: {br}' if br else title, NOTE_C, None, 'cnor', 'check' if vb else 'ok', 'Middleton - Victoria Beach: still there in 1948?' if vb else None, title, br)
os.makedirs(OUT, exist_ok=True)
for k, v in FILES.items(): json.dump(dict(type='FeatureCollection', features=v), open(os.path.join(OUT, k + '.geojson'), 'w'), separators=(',', ':'))
print({k: len(v) for k, v in FILES.items()}); print('\n'.join(REPORT))
