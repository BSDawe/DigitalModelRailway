# Staged for the next full rebuild

BUILT in Version 143 (8 Nov 2026): the Témiscouata files and page 1113 (Tables 1, 1s, 1a, 2). What remains below: the trip-chaining plan and the open items.

Brendan, 8 Nov 2026: build these through the Quebec build (on_build / on_lines), together with the batch of CN Maritime track, in one rebuild. Nothing here is read by
any step until it is moved into `pipeline/`. Track: `traces/maritimes/` (`python3 mar_tracks.py` for what is there and how it joins).

## Files (move into pipeline/)
| file | what | replaces |
|---|---|---|
| `on_tem_t001.csv` | Témiscouata 1 / 2 through to St. Jacques Church and Edmundston (the estimated border row goes) | the live file |
| `on_tem_t003.csv` | Témiscouata mixed 3 / 4 Edmundston - Baker Brook - Clairs - Connors | new |
| `on_cn_t001.csv` | CN Table 1 with the N.B. rows Halifax - Moncton - Newcastle - Bathurst - Campbellton - Tide Head - Flatlands (the estimated boundary row goes) | the live file |
| `on_cn_t001s.csv` | CN Table 1, the Saint John trains: 25 / 26 Saint John - Campbellton, 51 / 52 Saint John - Pacific Junction (Mon., Wed., Fri.) | new |
| `on_cn_t001a.csv` | CN Table 1a with Campbellton (36 / 35 now start / end there) | the live file |
| `on_cn_t002.csv` | CN Table 2 Oxford Jn. - Pugwash - Pictou, motor trains 334 / 333, and 332 / 331 Oxford Jn. - Oxford | new |

## on_build / on_lines changes
1. on_lines `_links()`: also read the Maritime track bank, `mar_tracks.features(status='ok')`, each as a link with its own `own`. Widen `BOXES['tem']` to
   (-69.7, -68.25, 47.15, 47.95). The CN graph has no box, so it gets all the Maritime CN track.
2. Specs: `tzrows` for on_cn_t001 (Atlantic rows to Campbellton, Eastern beyond, as on_cn_t023) and on_cn_t001s; `shift=-14400` (Atlantic) for on_tem_t003,
   on_cn_t001s, on_cn_t002; titles: on_tem_t003 'Edmundston – Baker Brook – Clairs – Connors (mixed)', on_cn_t001s 'Saint John – Moncton – Campbellton',
   on_cn_t002 'Oxford Junction – Pugwash – Tatamagouche – Pictou'; on_cn_t001 / on_cn_t001a titles lose "(Quebec part)" wording.
3. The file order (on_build LATE) so existing trip ids stay.

## Places
- Brendan's: Edmundston (-68.322783, 47.367167), the CP / Témiscouata station ("I think"); Baker Brook Junction (-68.4950083, 47.3039499), the CN / Témiscouata
  junction, not a timetable station (the Connors branch starts there).
- CGN points on the track (within ~150 m), use as they are: St. Jacques Church (CGN Saint-Jacques), Caron Brook, Clairs (CGN Clair), Connors; Pacific Junction (railway
  point, 8 m), Coal Branch, Adamsville, Harcourt, Kent Junction, Rogersville, Derby Junction, Nash Creek, New Mills, Charlo, Dalhousie Junction, Campbellton, Tide Head,
  Flatlands; Oxford Junction, Pugwash, Tatamagouche, Denmark, Scotsburn, Pictou.
- NEED A POINT (the CGN point is the town, 0.3 - 13 km off the track; by mileage until then): Halifax (1.3 km), Saint John (5.7 km: and the track: see below), Moncton
  (1.1 km), Newcastle (436 m), Bathurst (1.4 km), Petit Rocher (1.1 km), Belledune (1.8 km), Jacquet River (571 m), Berry Mills (346 m), Canaan (462 m), Barnaby
  River (257 m), Bartibog (the CGN Bartibog is 13 km away), Oxford (645 m), Pugwash Junction (186 m), Wallace (3.1 km), Malagash (3.0 km), River John (1.1 km),
  Meadowville (1.2 km); no CGN name: Eel River, McLeod, Brown Point, Ledges, Little River Mills, Baker Brook (CGN point 1 km off).

## Still needed
- Track: Saint John: Wikipedia's European & North American ends 5 km north-east of the city; the line into the Saint John station is missing (trace). Oxford Junction:
  the Montreal & European Short Line ends 204 m from the Intercolonial (connector). The NTR between Pacific Junction and the boundary is on file.
- Tables: Halifax - Truro - Moncton (Table 1 gives only Halifax and Moncton); Saint John - Moncton (Saint John's mileage in on_cn_t001s is Claude's 89.4 mi to
  Moncton, to check); Table 23's N.B. part (51 / 52 and 27 / 28 on the NTR).
- Nos. 1 / 2 (Brendan, 8 Nov 2026): through trips on six days, plus the seventh day's Campbellton - Montreal run under the same number (see on_cn_t001.csv).
- To check (Brendan): No. 26 has a dagger (ex Sun) at Campbellton; the file keeps it daily. No. 4 Témiscouata Baker Brook 8.15 - Edmundston 9.15 a.m. (as read).

## Trip chaining (Brendan, 8 Nov 2026: do it when all the CN Maritime files are in; again for CP)
Generalise the through-train linking in `real_ends.py` (runs at assembly, ~10 s, no rebuild). Today it links only trips whose ids differ by '-SK...' / 'E'
suffixes (50 trips: the Saskatchewan / Alberta pieces, CP 2E). Plan:
- Match on railway (id prefix) + number, the last stop of one = the first stop of the next (same gid), and compatible days (the next piece's service days, shifted
  for midnight, cover the first's).
- Join automatically when the stop is under an hour; when both pieces carry a name, only if the names agree (Brendan, 8 Nov 2026: both confirmed). A piece
  without a name does not block a join: CP 1 / 2 is unnamed (perhaps the only unnamed long-distance train), and some pieces carry the name only in one file. Every other candidate goes to
  a review list in the build log; an explicit JOIN / NOJOIN table settles them.
- GTFS: a shared `block_id` for each chain (stay-seated through running).
- Found on Version 142 (re-assembled 8 Nov): 160 candidate pairs not linked today, e.g. CN 1 - 4 at Ottawa / Capreol / Armstrong, CP 1 - 8 at Fort William / Sudbury,
  CN 11 / 12 at Hervey / Fitzpatrick / Cochrane. Must NOT join: CN No. 1 Maritime Express arriving Montreal (Central) with CN No. 1 Continental leaving it (100 min;
  same number, different trains). To decide: Kootenay Central M681 at Cranbrook (8.5 h layover).

## Maritime Coal, Railway & Power Co. (Official Guide, April 1948; Brendan, 9 Nov 2026; staged/maritimes/mcrp_official_guide.jpg)
For later (stage 3, short lines). Atlantic time. Daily except Sunday (†). Connects with CN at Maccan.
- Maccan 1.20 p.m., via River Hebert, to Joggins Mines (12 miles) 2.20 p.m.
- Joggins Mines 10.15 a.m. to Maccan 11.15 a.m.
- So the train lies over at Joggins overnight. The return sits before the outbound in the day: it leaves Joggins 10.15 a.m. and gets back there at 2.20 p.m.
- Branch Chignecto - Maccan (3 miles) is freight only: not modelled.
- NEEDED: track (Maccan - River Hebert - Joggins; nothing in the bank yet), and a River Hebert time (not printed; interpolate by mileage).
