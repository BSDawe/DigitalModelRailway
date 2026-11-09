# Staged for the next full rebuild

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
- To check (Brendan): No. 1 has a dagger (ex Sun) at Halifax and Moncton, No. 2 at Moncton and Halifax, and No. 26 at Campbellton: the files keep "daily" for 1 / 2 (as
  the Quebec page) and 26. No. 4 Témiscouata Baker Brook 8.15 - Edmundston 9.15 a.m. (as read).
