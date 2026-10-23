"""Joint stations (Brendan, 17 October 2026): stations of two or three railways that were one station in 1948 become one stop on the page
and in the GTFS feed. Applied at assembly, before real_ends. The first id of each group is kept (its position and name)."""
import csv, io
MERGE = [
 # Saskatchewan: agreed shared or union stations
 ['CN_REGINA', 'CP_REGINA'], ['CN_NORTH_BATTLEFORD', 'CP_NORTH_BATTLEFORD'], ['CN_BATTLEFORD', 'CP_BATTLEFORD'], ['CN_HUMBOLDT', 'CP_HUMBOLDT'],
 ['CN_PRINCE_ALBERT', 'CP_PRINCE_ALBERT'], ['CN_MELFORT', 'CP_MELFORT'], ['CN_MEDSTEAD', 'CP_MEDSTEAD'], ['CN_GLENBUSH', 'CP_GLENBUSH'],
 # Alberta: the Drumheller valley, CP over the CN (the CN stations)
 ['CN_DRUMHELLER', 'CP_DRUMHELLER'], ['CN_WILLOW_CREEK', 'CP_WILLOW_CREEK'], ['CN_EAST_COULEE', 'CP_EAST_COULEE'], ['CN_DOROTHY', 'CP_DOROTHY'],
 ['CN_TREFOIL', 'CP_TREFOIL'],
 # Washington: the NP - UP joint line Tacoma - Portland, and the other shared stations
 ['NP_STEILACOOM', 'UP_STEILACOOM'], ['NP_EAST_OLYMPIA', 'UP_EAST_OLYMPIA'], ['NP_TENINO', 'UP_TENINO'], ['NP_BUCODA', 'UP_BUCODA'],
 ['NP_CENTRALIA', 'UP_CENTRALIA'], ['NP_CHEHALIS', 'UP_CHEHALIS', 'MILW_CHEHALIS'], ['NP_NAPAVINE', 'UP_NAPAVINE'], ['NP_WINLOCK', 'UP_WINLOCK'],
 ['NP_VADER', 'UP_VADER'], ['NP_CASTLE_ROCK', 'UP_CASTLE_ROCK'], ['NP_OSTRANDER', 'UP_OSTRANDER'], ['NP_KELSO_LONGVIEW', 'UP_KELSO_LONGVIEW'],
 ['NP_KALAMA', 'UP_KALAMA'], ['NP_WOODLAND', 'UP_WOODLAND'], ['NP_RIDGEFIELD', 'UP_RIDGEFIELD'], ['NP_FELIDA', 'UP_FELIDA'],
 ['UP_KENT', 'MILW_KENT'], ['UP_SUMNER', 'MILW_SUMNER'], ['UP_NORTH_PUYALLUP', 'MILW_NORTH_PUYALLUP'],
 ['NP_PASCO', 'SPS_PASCO'], ['NP_KENNEWICK', 'SPS_KENNEWICK'], ['UP_AYER', 'CPRR_AYER'],
 # Manitoba: Winnipeg Union Station (CN, NP, GN), and the Emerson Junction - Morris - Winnipeg line the NP and GN both used (18 October)
 ['CN_WINNIPEG', 'NP_WINNIPEG', 'GN_WINNIPEG'], ['CN_EMERSON_JUNCTION', 'NP_EMERSON_JN', 'GN_EMERSON_JUNCTION'], ['CN_LETELLIER', 'NP_LETELLIER', 'GN_LETELLIER'],
 ['CN_ST_JEAN_BAPTISTE', 'NP_ST_JEAN_BAPTISTE', 'GN_ST_JEAN_BAPTISTE', 'GN_ST_JEAN'], ['CN_MORRIS', 'NP_MORRIS', 'GN_MORRIS'],
 ['CN_STE_AGATHE', 'NP_ST_AGATHE', 'GN_ST_AGATHE'],   # CN, NP and GN one station each (Brendan, 20 October)
 ['NP_PORTAGE_JUNCTION', 'GN_PORTAGE_JUNCTION'], ['CP_GRETNA', 'GN_GRETNA'], ['CP_NOYES', 'GN_NOYES'], ['CN_EMERSON', 'GN_EMERSON'],
]
TO = {g: grp[0] for grp in MERGE for g in grp[1:]}

def apply(viz, gt):
    seen = set()
    for L in viz.get('lines', []):
        for s in L.get('stations', []):
            if s.get('gid') in TO: s['gid'] = TO[s['gid']]; seen.add(s['gid'])
    def redo(fn, col):
        if fn not in gt: return
        rows = list(csv.reader(io.StringIO(''.join(gt[fn]))))
        h = rows[0]; k = h.index(col); out = [h]; ids = set()
        for r in rows[1:]:
            if not r: continue
            if r[k] in TO: r[k] = TO[r[k]]
            if fn == 'stops.txt':
                if r[k] in ids: continue
                ids.add(r[k])
            out.append(r)
        buf = io.StringIO(); csv.writer(buf, lineterminator='\n').writerows(out); gt[fn] = buf.getvalue().splitlines(keepends=True)
    redo('stops.txt', 'stop_id'); redo('stop_times.txt', 'stop_id')
    return sorted(set(TO.values()) - seen)
