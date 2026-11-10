# The Digital Model Railway — project state

Read this first. It is meant to be enough to start a short, single-task chat without replaying the project's history.
Last updated 10 November 2026 (Version 157: Maritime Coal, Railway & Power, Maccan - Joggins; Version 156: CP subsidiaries under their own names; SI its own heading; Version 155: the Princess Helene, Saint John - Digby; the DAR at the CN stations; Version 154: Dominion Atlantic timetables; Version 153: CP N.B. track; DAR drawn as CP; Version 152: Dominion Atlantic track (CP Maritimes begins); Version 151: the regional OSM export fills the N.B. gaps; Version 150: Middleton - Bridgetown on the Middleton & Victoria Beach; Version 149: the Pictou County lines are CN; Version 148: CN page 1117, the last of the CN Canadian timetables; Version 147: the queued fixes - steamer labels, broken estimated links, North Sydney, Canso train ferry and Mulgrave switchback, ESL, Campbellton, CN Edmundston; Version 146: CN page 1116, P.E.I., Pictou, Newcastle - Loggieville, Table 23 N.B. part, Borden - Cape Tormentine train ferry; Version 145: CN page 1115, N.S. and N.B. branches, Cabot Strait and Yarmouth - Boston steamers; Version 144: CN Table 4 Halifax - Truro - Moncton - Saint John; Version 143: the Maritimes begin: the Temiscouata to Edmundston and Connors, CN Tables 1, 1a and 2 in N.B. and N.S., the Maritime track bank; 142: the Chicago, Duluth & Georgian Bay steamers North American and South American; 141: C.S.L. boats named; 140: full rebuild; 135-139: Niagara, the Muskoka, Pointe au Baril and C.S.L. boats, motor trains, the Newfoundland Railway; Version 62 moved the project to git). For a new chat, read HANDOFF.md first (short), then the sections of this file it points to.

## What this is

Brendan Dawe's "digital model railroad": an animated map of passenger trains and steamers running to their summer-1948 timetables (B.C., Alberta,
Saskatchewan, Manitoba, the Lakehead, Washington, Alaska, the Yukon and the Midwest), plus a GTFS feed of the same.

**Since 22 October 2026 the project lives in git** (Version 62 was the last zip bundle):
- Public: **https://github.com/BSDawe/DigitalModelRailway**. The pipeline is in `pipeline/` (this file is `pipeline/STATE.md`), the basemap in
  `basemap/`. GitHub Pages publishes the map at **https://bsdawe.github.io/DigitalModelRailway/** (gtfs.zip beside it).
- Private: **BSDawe/DigitalModelRailwayPrivate**, the raw third-party files (original KMZ collections, full place-names files, the U of T rails
  file, scans), with the same paths under `pipeline/`. The list is `pipeline/tools/private_paths.txt` (also in `.gitignore`). Brendan's rule
  (22 Oct): raw files private, only the traces actually used are public.
- The old artifact (https://claude.ai/artifact/6BMpHzdMps4m8iMxZGTzq6) is no longer updated.

To publish: commit and push to `main`. The workflow (`.github/workflows/pages.yml`) runs `build.py --assemble` from the committed parts and
deploys `pipeline/site/`. It does not run the routing steps: run those here and commit their `parts/*.json`.

## Starting a fresh chat

1. Attach both repos (`add_repo` BSDawe/DigitalModelRailway with push, and BSDawe/DigitalModelRailwayPrivate if a step that reads raw files
   will be re-run). Clone the public one; clone the sources beside it and run `python3 pipeline/tools/link_sources.py <sources clone>`
   (symlinks the private files into place).
2. `cd pipeline; python3 build.py --status` shows every step and whether it is out of date ("ok, inputs absent" = its raw files are not linked;
   its saved part is used). `python3 build.py --assemble` writes the page and the site from the saved parts without running anything.
3. Do the one task. Re-run only what it touches (`python3 build.py`), check (see "Checks"), update this file (the fix list, the step table if a
   step was added, the version line at the top), commit with a message saying what changed, and push. New raw source files go to the sources
   repo and into `tools/private_paths.txt`; traces Brendan draws himself go in the public repo.

Needs Python with shapely, pyproj, numpy, networkx, scipy, scikit-image, Pillow, pyshp and playwright (Chromium at /opt/pw-browsers/chromium).
A full `build.py --all` now takes about 70-80 minutes (on_build alone about 60): run it in the background and do not write traces/ or timetable CSVs while it runs.

## The hosted site and the basemap (22 October 2026)

- `make_site.py` (run by `build.py` after `make_page.py`) writes `site/`: `index.html` (the template with `site_loader.js` in place of the
  map's script), `app.<hash>.js` (the template's script), `data/manifest.json`, `data/core.<hash>.json` (B.C. Electric base data) and one
  `data/<step>.<hash>.json` per build step (the lines that step last changed). Routes are packed as integer differences (1e-6 degree,
  0.1 m) and unpacked by the loader to the same numbers; checked identical to the single-file page in Chromium (stations, routes, trips,
  pixels). Hashed names: after an update a visitor downloads only the files that changed.
- `fraser_valley_1949.html` (single file, inline data and water) is still written for the checking tools (`tools/shots.py`, `tools/perf.py`).
- Basemap: `basemap/build_tiles.py` (about 5 minutes) merges the page's water layers (`water_*.json`, the same list as `make_page.py`) and adds
  Natural Earth borders (provinces/states and the international land boundary; cut copies in `basemap/sources/`), and cuts them into tiles
  at levels 0-7 (finest 40 km, source detail; coarser levels simplified to about a pixel), in the page's projection. **Re-run it after any
  change to the water files or to the projection (`PROJ` in build_tiles.py must match `P` in the template)**, and commit `basemap/tiles/`.
  The page (`TILES`, `tilesFor`, `loadTile` in the template) draws the tiles the view needs, a loaded parent standing in until a tile
  arrives. Borders: dashed, ink-soft at 45 %. The single-file page draws its inline water and no borders.
- Not done yet (stage 2, when the data outgrows loading everything at start): fetch line data by viewport. The page computes station
  positions and the boards from every line at start-up, so this needs the stations and trips split from the route geometry.

## Build

`build.py` runs steps listed in `steps.json`. Each step is one script that adds one or a few lines to the map. A step's result is kept in
`parts/<step>.json` (its lines for the page and its rows for the GTFS feed). Assembly merges the parts into `viz_data.json`, `gtfs/`, the GTFS
zip and the page. A step is re-run only if its script or an input file changed, or a step it reads was re-run.

    python3 build.py              # re-run what is out of date, assemble
    python3 build.py gn_build     # force a step (and whatever reads it)
    python3 build.py --all        # everything, about 35 s
    python3 build.py --assemble   # merge parts only
    python3 build.py --status

Output is quiet: one line per step run. Logs are in `build_logs/<step>.log`; read the log only when a step fails or a number needs checking.

| step | lines it makes or changes | reads (steps) | inputs |
|---|---|---|---|
| `base_viz` | Chilliwack line base data (frozen) | – | base_viz.json |
| `build_gtfs` | Chilliwack line GTFS | base_viz | geometry.json, transcription_eastbound/westbound.csv |
| `cp_build` | Central Park line | build_gtfs | BCER system KML, geometry.json, model.json |
| `bl_build` | Burnaby Lake line | cp_build | BCER system KML, bl_geometry.json |
| `marpole_build` | lulu, nwm | bl_build | BCER system KML, marpole_geometry.json |
| `gn_build` | gn (Vancouver–Seattle) | – | gn_geometry.json, gn_table90.csv, traces/gn_washington.kml |
| `mainline_build` | cn (Vancouver–Edmonton–Chauvin), cno, cp (Vancouver–Calgary–Walsh), cpm, cpw | – | cn_1949_*.csv, cn_1948_alberta.csv, cp_1948_table7.csv, ab_cn_t075.csv, ab_cp_t006.csv, ab_lines.py, nrwn_routes.pkl, nrwn/alberta.json, nrwn/alberta_all.json, places/cgn_ab_places.csv |
| `island_pge_build` | en, ena, pge | – | en_1949_table164.csv, pge_1948_04.csv, island_pge_routes.pkl |
| `cn_north_build` | cnn | – | cn_1949_tables225_226.csv, nrwn/north.json |
| `kv_build` | kv, x_gf | – | cp_1948_table151_kv.csv, kv_route.pkl, bc_railway_bits.kml |
| `cp_south_build` | cr (Nelson–Crowsnest–Lethbridge–Medicine Hat), tr, tl, x_col | – | tables written by the script itself, ab_cp_t151.csv, ab_lines.py, nrwn/south.json, cpmain.json, alberta.json, alberta_all.json |
| `si_build` | si (Yahk–Spokane) | cp_south_build | si_1947_10.csv, nrwn/south.json, traces/spokane_international.kml |
| `kv_through` | changes cp, kv, cr (through trains 11/12 etc.) | mainline, kv, cp_south | – |
| `cps_build` | cps | mainline_build | sicamous_armstrong.tsv (table inside the script) |
| `interim_build` | mer, slo, nak, kim, arr, x_mer; changes cno, kv | mainline, kv, cp_south, kv_through, cps | bc_railway_bits.kml, kvr_trails.kml, nakusp_end.kml, ntad_interim.tsv |
| `boats_build` | 41 steamer lines (b…) | all the rail steps a boat meets | sea.py, sea_legs.json (lane cache), water_union.pkl |
| `wpy_build` | wpy (Skagway–Whitehorse) | – | nrwn/wpy.json, nrwn/wpy_yt.json, traces/wpy_alaska_ntad.tsv |
| `nar_build` | nar (Edmonton–Dawson Creek) | mainline_build | nar_1948_04.csv, nrwn/alberta.json, nrwn/dawson.json, traces/nar_watino.kml, nar_dawson_creek_gap.kml, edmonton_terminal.kml |
| `ab_cn_build` | 18 CN lines in Alberta (cn_171 … cn_213f) | mainline_build, nar_build | ab_cn_t*.csv, ab_lines.py, nrwn/alberta_all.json, the two backup sets, places/cgn_ab_places.csv |
| `ab_cp_build` | 18 CP lines in Alberta (cp_138 … cp_120) | mainline_build, cp_south_build, kv_through | ab_cp_t*.csv, ab_lines.py, nrwn/alberta_all.json, places/cgn_ab_places.csv |
| `ab_nar_build` | nar_bh (Barrhead), nar_ww (Waterways), nar_hc (Hines Creek) | nar_build, ab_cn_build | ab_nar_t179*.csv, ab_lines.py, traces/nar_barrhead_branch.tsv |
| `nn_build` | nn (S.S. Noronic, Windsor - Duluth) | on_build (the Detroit ferry slip) | traces/lakes/northern_navigation_co.kmz, water_east.json, nn_legs.json (lane cache) |
| `cp_lakes_build` | cpgl (CP steamers Keewatin and Assiniboia, Port McNicoll - Fort William) | nn_build (the Sault dock), on_build (Port McNicoll) | traces/lakes/cp_great_lakes.kml, traces/lakes/northern_navigation_co.kmz, water_east.json, cpgl_legs.json (lane cache) |
| `cp_manitoba_build` | cpmb (CP S.S. Manitoba cruise, Port McNicoll - Owen Sound - Sault - Fort William) | cp_lakes_build (the Sault and Fort William stops), on_build (the two CP stations) | traces/lakes/cp_great_lakes.kml, traces/lakes/northern_navigation_co.kmz, water_east.json, cpmb_legs.json (lane cache) |

Rules that keep this working:

- **A new line is a new step**: a new script that adds its line to `viz_data.json` and appends its rows to `gtfs/`, plus an entry in `steps.json`
  (with `needs` only if it reads another step's lines). Copy `wpy_build.py` (stand-alone line) or `si_build.py` (shares a station and track with another line).
- Never `import` a build script from another script or a one-off check: importing runs it. Shared helpers live in `nrwn_graph.py`, `sea.py`, `bc_bits.py`.
- Scripts must not write the zip or the page; `build.py` does.
- `base_viz.json` is frozen: the script that first made the Chilliwack line's page data was not kept.
- Timetable transcriptions are CSV files, transcribed once. Fix a time by editing the CSV (or the table inside the script, for `cp_south_build`,
  `cps_build`, `boats_build`), not by re-reading the scan.
- User traces go in `traces/`. The national network extracts are `nrwn/*.json`; the 157 MB source `nrwn/doc.kml` is not in the bundle and is
  only needed by `nrwn/extract*.py` to cut a new extract.

## Track sources on hand

- `nrwn/*.json`: extracts of the national network (present-day track): B.C., the Yukon part of the White Pass, four Alberta corridors
  (`alberta.json`, used by the first Alberta extensions and left as it is) and all of Alberta without yards (`alberta_all.json`, cut by
  `nrwn/extract_alberta_all.py` from the Alberta file, 2017 vintage; used by `ab_lines.py`).
- `places/cgn_ab_places.csv`: the populated places (towns, hamlets, localities, railway points) of the federal Canadian Geographical Names
  file for Alberta, which Brendan supplied on 4 October: where the Alberta stations are. `alberta_water.gpkg`: his simplified Alberta lakes
  and rivers (see `water_alberta.py`).
- `places/cgn_bc/cgn_bc_csv_eng.csv`: the same federal names file for British Columbia (Brendan, 7 October, "for the record"; not used by
  any step yet). `places/cgn_bc_places.csv` holds its 2,344 populated places plus railway points, landings, harbours, ports and wharves:
  the source for B.C. stations and steamer landings that have no position yet (Chelohsin's ports, later sub-weekly sailings).
- `traces/`: Brendan's own traces (GN Washington, Spokane International, Watino, the Dawson Creek gap, the Edmonton downtown loop, the Barrhead branch, the White
  Pass in Alaska), plus `bc_railway_bits.kml`, `kvr_trails.kml` and the BCER system KML in the project folder.
- `traces/hr_rails/HR_rails_NEW.*` (filed 4 October, NOT USED YET; Brendan calls it a crude trace): "Historical Canadian Railroads", Cartography
  office, Geography Department, University of Toronto, 2020, https://doi.org/10.5683/SP2/UCCFVQ, Borealis, V2 (GEORIA). Licence CC BY-NC-SA 4.0
  (non-commercial, share-alike: say so to Brendan before it goes into anything published). A shapefile of every Canadian line with the years
  built and abandoned (`CNSTRCTD`, `ABNDND`), in a NAD27 Lambert projection (read the .prj). In Alberta: 422 pieces, 14,800 km, points about
  1.9 km apart, a median 180 m off today's track where track survives. It has a line past every dashed stretch on the map, a median 200 to
  900 m from the stations there (the stations, from the names file, are the better positions). Read with `pyshp` (`pip install pyshp`).
- **National network routings are preferred** (Brendan, 4 October). Wherever the national network has the track, route over it. The two sets
  below are backups for routes the network no longer contains: use them only for that track, joined on to the network at each end.
- Backup sets, loaded with `backup_track.py` (`lines('cnor' | 'gtp', text=..., box=...)`, or `features(...)` to route over with
  `nrwn_graph.Net`; `python3 backup_track.py` lists the western lines). Used by `ab_lines.py` for the CN and Northern Alberta lines in Alberta. Where they follow track that still exists
  they are exact (a median 2-3 m from the map's CN lines).
  - `traces/cnor_all.geojson`: the **Canadian Northern Railway** system, 144 lines and about 15,900 km coast to coast, each named by
    constituent company and sometimes branch. In the west: the Vancouver terminal and the Lulu Island line (Steveston), the two Vancouver
    Island lines (Victoria-Patricia Bay and Victoria towards Cowichan Lake), the Kamloops branch, and in Alberta the Canadian Northern Alberta
    line west of Edmonton (the original route, which differs in places from the line the CN used by 1948), Edmonton terminals, the Edmonton
    and Slave Lake (to Athabasca), the Alberta Midland (Edmonton-Calgary by Drumheller and Camrose), and the Whitecourt, St. Paul, Alliance,
    Brazeau and Steveville branches.
  - `traces/gtp_all.geojson`: the **Grand Trunk Pacific**, 13 lines and about 4,700 km: the main line Winnipeg-Edmonton-Jasper-Prince Rupert
    and its branches, in the west the Calgary branch (Tofield-Calgary), the Mountain Park branch and the Lovett branch (the Coal Branch,
    south of Edson). Like the Canadian Northern, its original line between Edmonton and the Yellowhead differs in places from the 1948 route.

## Alberta (Version 37, 4 October 2026)

Everything in Alberta to the Saskatchewan boundary, from the May 1948 Official Guide (CN and Northern Alberta, tables of April 25, 1948) and
the CP 1948 timetable. Brendan's rules: one Pacific clock (Mountain time shown an hour earlier); a train that goes on into Saskatchewan ends
at its last timed Alberta station; national network track first, then the backup sets and his traces; where there is no track at all a
straight line from station to station, **drawn dashed** (only those: NTAD track and his traces stay solid).

- **Transcriptions**: `ab_cn_t*.csv`, `ab_cp_t*.csv`, `ab_nar_t179*.csv`, one per table (or part of a table), Alberta stations only, times as
  printed (Mountain). The format, a reader and a checker are in `ab_table.py` (`python3 ab_table.py file.csv` flags times that go backwards
  and impossible speeds). Each file's comments say what was hard to read and what the signs mean. The scans are in `scans/` (not in the bundle);
  `scans/TRANSCRIBE.md` is the method used. Fix a time by editing the CSV.
- **`ab_lines.py`** (a helper, imported by the steps): a line is a list of legs (slices of tables joined end to end, so a train that runs over
  two tables is one trip). Each station gets a point: a station already on the map, a point given by hand (`HAND`, city stations), or the place
  of that name in the names file (`ALIAS` for changed spellings). Between located stations it looks for track in a graph of the Alberta
  network (the other big railway's track left out; for CN and N.A.R. the backup sets and traces are tied in wherever they run beside the
  network) and accepts it when its length agrees with the printed miles; otherwise a straight line, marked `est` in the line's `segments`.
  Stations without a point are put at their printed mileage. Track already drawn by an earlier line gets `owner: 'none'`. The step's log
  (`build_logs/ab_*.log`) lists traced against printed miles and every straight stretch. `AB_DRY=1 python3 ab_cp_build.py` traces without
  writing; `AB_DRY=cp_142` one line. Options in a line's spec: `cols` (which trains), `force` (accept the track between two stations whatever
  its length), `via` (a junction that is not a station), `places` (a point for one station).
- **Main lines** are part of the existing lines, so through trains run through: CN Edmonton–Chauvin and CP Calgary–Walsh in
  `mainline_build.py`, CP Lethbridge–Medicine Hat in `cp_south_build.py` (all three use `ab_lines.trace` for the track and the stations).
  CP No. 2 lies overnight at Calgary, so east of Calgary it is a second trip (`CP-2E`, shown as No. 2).
- **Days**: Alberta trips use service ids `W_` + seven digits, Monday first (`W_1010100` = Mon., Wed., Fri.); the page and the GTFS calendar
  read them directly. A train timed just after midnight Mountain time starts the evening before on the Pacific clock, and its days are moved back one.
- **Page**: dashed estimates; views "Edmonton, Red Deer and Lloydminster", "Calgary, Lethbridge and Medicine Hat", "Peace River, Athabasca and
  Waterways"; the sources note is capped in height; Alberta water from `water_alberta.json` (made by `water_alberta.py`, merged in `make_page.py`).
- **Straight estimates now on the map** (a trace from Brendan would replace any of them; put it in `traces/` and add it to the graph in
  `ab_lines.graph`): CN St. Paul–Heinsburg, Abilene–Bonnyville–Beaver River, New Brigden–Hemaruka, Hanna–Scapa–Warden, Rosedale–East Coulee–Trefoil, Cadomin–
  Mountain Park; N.A.R. Carbondale–Bon Accord–Egremont, Grimshaw–Hines Creek, and the last 8.6 mi into Waterways; CP Edmonton–South Edmonton
  (the High Level Bridge), High River–Macleod, Botha–Coronation–Compeer, Sunnybrook–Breton–Rimbey, Red Deer–Rocky Mountain House,
  Shepard–Irricana–Kneehill and Cosway–Wimborne, Empress–Bassano–Irricana, Bassano–Rosemary–Drumheller–Kneehill, Grantham–Lomond–Mossleigh,
  Star–Willingdon–Lloydminster, Vegreville–Willingdon, Piyami–Turin, Raymond–Cardston–Glenwood, Foremost–Manyberries–Jaydot.
- **Waiting on Brendan**: (1) **Jaydot** (CP Table 120, the last station before Saskatchewan, 8.3 mi east of Cressday) is in neither the names
  file nor on any track. It is drawn at an estimate, 8.3 miles on from Cressday along the line of Bain–Cressday (49.211, -110.080; `HAND` in
  `ab_lines.py`). The point he sent on 4 October (49.346067, -110.570411) lies between Manyberries and Bain, 22 miles west of Cressday, so it
  was not used; he may have another. Hemaruka (CN Table 211) came from him on 4 October: a point at the wye, in `HAND` in
  `ab_lines.py`; it is 19.5 mi in a straight line from Sedalia against 17.8 printed, noted in `ab_cn_t211.csv`. (2) Days not confirmed, the key being cut off on the scans: the Waterways trains
  (No. 7 out of Edmonton Mon., Wed., Fri.; Nos. 23, 24 and 8 worked out from one train set going round: see `ab_nar_t179c.csv`) and the Drumheller–Trefoil mixed (entered to East Coulee on
  Mon., Thu., Fri., Sat. and through to Trefoil on Tue.). (3) Figures marked `?` in the files: Table 6, No. 1 Tilley 6.34 p.m., No. 2 Cassils
  10.04 a.m. and Cluny 8.54 a.m. (the last digit could be 1); Table 139, M618 Throne 7.55 a.m.; Table 141, M615 Aspen Beach 8.25 a.m.
- **Northern Alberta train numbers** (Brendan, 4 October): the Guide's headings "7-23", "24-8", "7-25", "8-26" are pairs of trains. Nos. 7 and 8
  run Edmonton–Lac La Biche, 23 and 24 Lac La Biche–Waterways, 25 and 26 Carbondale–Busby–Barrhead (connecting with 7 and 8), 5 and 6
  McLennan–Hines Creek, 1 and 2 Edmonton–Dawson Creek. A heading of two numbers is never one train.
- **Left out, and why**: CP Table 133 (Fox Valley–Schuler–Empress: it crosses the boundary four times and only Schuler, Hilda and Empress are
  in Alberta; transcribed in `ab_cp_t133.csv`); CN Table 230 (Bodo is its only Alberta station; `ab_cn_t230.csv`); the mixed trains between
  Camrose and Mirror in a footnote to CN Table 208 (only the leaving time is printed); Suffield–Grantham on CP Table 137 ("temporarily
  discontinued"); the Strathmore line, by which CP Nos. 1 to 4 ran between Gleichen and Shepard (they are shown over the Carseland line; their
  Strathmore-line stops are in the comments of `ab_cp_t143a.csv`); the Hudson's Bay Company river boats (no schedule found).
- Station positions from the names file are the settlement, not the station building; in the cities the station is a hand point and
  approximate (CP Edmonton, South Edmonton, CN Calgary, CN Camrose, Medicine Hat, Waterways).

## Credits (Brendan, 4 October 2026)

To go on the page as a credits line with the next update (the footer now names only the National Railway Network, Statistics Canada and the
timetables). The federal sources are under open licences that ask for an attribution line: copy the wording from each licence page.

- B.C. Electric routes, and the station architecture KML (Carrall Street station): the **Canadian Electric Railway Map Collection**, a KMZ
  data set that has since disappeared from the internet.
- Main-line track: the **National Railway Network (NRWN)**, Natural Resources Canada. The White Pass in Alaska: **NTAD**, U.S. Bureau of
  Transportation Statistics.
- Canadian Northern and Grand Trunk Pacific track sets (`traces/cnor_all.geojson`, `gtp_all.geojson`): the maps embedded in the **Wikipedia** articles
  "Canadian Northern Railway" and "Grand Trunk Pacific Railway": cite and link the two articles (Brendan, 4 October), with Wikipedia's
  licence, CC BY-SA.
- Kettle Valley line: **https://www.kettlevalleyrailway.ca/map.html**
- Brendan's own traces, from Google Earth and OpenRailwayMap (OpenRailwayMap is OpenStreetMap data: "© OpenStreetMap contributors").
- Water: **Statistics Canada** lakes and rivers polygons (B.C. and Alberta). Alberta station positions: the **Canadian Geographical Names**
  database, Natural Resources Canada.
- Timetable scans: **Timetableworld.com** (the Official Guide, CP, CN, GN, S.I., E&N, PGE). It does not cover the B.C. Electric or Union
  Steamships timetables: their source is not recorded here.
- Washington State (Brendan, 9 October 2026, for the next stage; not used yet): railway KMLs by **Tony Howe and David Price, Mississippi
  Rails** (`traces/washington/Washington State/`: `Washington State Map 6-3-2018.kmz`, 364 placemarks in folders by railway: NP, S.I.,
  SP&S and its subsidiaries, UP/OWR&N, Milwaukee, GN, Washington short lines; `Spokane_Portland_&_Seattle.kmz`; and his screenshots in
  folders GN, NP, Milw, SP&S, UP and Washington Steamlines). Place names: **Washington State** (Department of Ecology's copy of the federal
  GNIS names, 42,945 features of every class; `places/wa/wa_place_names.csv`, columns FEATURE_NAME, FEATURE_CLASS, PRIM_LAT_DEC,
  PRIM_LONG_DEC; Populated Place 3,285, Locale 4,421). Brendan: "await further instructions".
- Inspiration: TRAVIC.

## The page data, briefly

`viz_data.json` → `lines[]`, each: `key, kind, label, mainline, owner, livery?, src?, water?, route [[lon,lat,chain_m]], stations [{name, chain, lon,
lat, mile, lmile?, principal, gid, note, xy?, slow?}], dirLabels, segments [{owner, a, b}], trips [{id, num, name, svc, dir, stops
[[stationIndex, arr, dep, timepoint]], note, vessel?}]`.

- `kind`: c Central Park, b Burnaby Lake, l Lulu Island, n Marpole–New Westminster, g Great Northern, q CN, p CP (and S.I.), i interim, r PGE,
  y White Pass, a Northern Alberta, v steamers. A new railway needs: a colour token, `.badge.<kind>`, a legend swatch, and entries in
  `KIND_LABEL`, `KIND_BADGE`, `KIND_COLOR`, the colour list in `readColors`, the kind list in `renderList`, a panel line in `renderTrain`,
  and its service days in `SERVICES` and the `days` labels (search the template for `nar` to see every place). Kind picks the badge and default colour; `livery` overrides the colour (`si`, `cpss`, `bb`, `cnss`, `uss`, `wpy`).
- `owner` colours the track; a `segments` entry overrides it for part of the route. `owner: 'none'` means another line already draws that
  track (through trains), so it is drawn once.
- Stations with the same `gid` on different lines are one station. The same gid may appear twice on one line (out-and-back spurs).
- `svc` must be one of the day lists in `SERVICES` in `page_template.html`; add new ones there and to `calendar.txt` in the step.
- Times are seconds after midnight; past-midnight runs keep counting (the page carries trips over for up to three days).
- Stop timepoint 0 = estimated time, shown "est.".
- Views (the menu bottom right) are boxes in `VIEWS` in `page_template.html`.

## Conventions Brendan has set

- Standardise on the May 1948 Official Guide wherever its schedule is the same as what is in the map (Brendan, 3 October). Done for the CN
  main line: all 118 times the Guide prints between Jasper and Hope equal the 1949 folder's, so the source is given as April 25, 1948, with
  the 1949 folder supplying the stations the condensed Guide table leaves out. Not yet checked against the Guide: Hope–Vancouver, the CN
  Okanagan (Table 306), the CN northern line (Tables 225, 226), and the PGE 1949 table.
- Timetable year: non-BCER railways standardised on 1948 (CP 1948 timetable; April/May 1948 Official Guide for PGE, Black Ball, CN Steamships,
  WP&Y); CN tables 1949; GN Table 90 summer 1947; Spokane International's own timetable, October 1947; Union Steamships Sailing Guide No. 138
  (31 May 1948).
- Alberta (3 October): for now only the through trains to Calgary, Lethbridge and Edmonton; Brendan may widen this later. The tables print
  Mountain time east of Field, Crowsnest and Jasper; everything is entered in Pacific time, an hour earlier, so the map has one clock.
  Alberta track is `nrwn/alberta.json`, cut from the Alberta file of the national network by `nrwn/extract_alberta.py` (three corridors;
  widen `BOX` there for more).
- Standard time throughout, like the railways. The Union Steamships guide is printed in Daylight Saving Time: it is entered as printed in
  `boats_build.py` and shifted an hour earlier when the trips are made (`DST`).
- Passenger services only. Steamers go in if they run at least weekly, including peak-season-only sailings. No road ferries. CP Tables 172 and
  173 are out (less than weekly). Okanagan Lake boats were replaced by the Greyhound bus by 1948. Black Ball: only routes touching Canada.
- Wyes are drawn if a passenger train would use them.
- A station that only mixed trains call at is drawn as a minor station (done on the page, from the trips; a steamer or passenger train calling
  keeps it principal).
- Where a steamer's name is known from elsewhere it is used as the ship's name (Minto, Moyie, the tug Rosebery); otherwise the badge reads
  "Steamer". Long names wrap to two lines in the station box.
- A sailing's heading names the place, not the pier ("Nanaimo to Vancouver"); the landing itself carries the pier in its name:
  Vancouver (CP Pier), Vancouver (Union Pier), Vancouver (C.N. dock), Victoria (CPR Steamship Terminal), Victoria (Black Ball Terminal).
- Landings Brendan has located are in `PLACED` in `boats_build.py` (marker at his coordinates, no "position approximate"). A camp he could not
  locate gets no landing: the boat just sails through the area, and the call is named in the sailing's note.
- Ownership: CP owns Sicamous–Vernon; CN owns Vernon–Kelowna and Campbell Creek Jct to the wye near Armstrong. Yahk–Kingsgate is CP track.
- Liveries: Spokane International black, a darker red, golden yellow. Chilliwack interurbans drawn as two smaller cars in train. Central Park
  stations round like the other interurban lines. Boat and WP&Y liveries are Claude's picks, not confirmed.
- Boat panels read "Nanaimo to Vancouver · Daily · CP Steamship" (the company's service, not a per-sailing description).
- Steamer lanes keep off Sturgeon, Roberts and Spanish Banks (`SHOALS` in `sea.py`); elsewhere the routed lanes are fine.
- CP's Vancouver pier was where Canada Place stands; Union Steamships at the foot of Carrall Street.
- Brendan's to-do list of tracings is his own list, not work for Claude; when he asks about it he wants to know what is outstanding.
- He prefers his own traces to stand-ins (NRWN/NTAD) wherever he has supplied one.

### Working with Brendan (added 4 October)

- Before launching parallel workers (agents) say what will be launched and roughly what it will cost, so he can redirect first. He is not
  against them; the 14 transcription workers used about 2.2 million tokens unannounced, and a batch of web look-ups for station positions ran
  for five minutes against his instruction before he could stop it.
- When he says "give me a list", give the list: he looks places up himself or supplies a file (the names file came that way).
- Shell network access is only package registries and GitHub; web pages are reachable only through search results.

## How the page draws (keep it smooth)

Everything that does not move (water, track, steamer lanes, stations and their names) is drawn once into an offscreen "base" canvas and redrawn
only when the view settles, moves past its spare margin, or the theme, size or selected station changes (`renderBase`, `drawBase` in
`page_template.html`). Each frame copies that picture and draws only the trains and boats. Long lines are cut into pieces with bounding boxes
and have coarser copies for zoomed-out views (`pieces`, `LOD`). So a frame costs the same however many lines there are; new lines add only to
the occasional base redraw.

- Anything new that is drawn every frame must be cheap and belong to a moving thing. Static things go in `renderBase`.
- `python3 tools/perf.py` prints frame times by view for a desktop and a phone-sized screen (headless, no GPU, so pessimistic). At Version 33:
  about 4 ms a frame still or panning (it was about 90 ms at Version 32), and 45–80 ms for a base redraw. Re-run it after adding lines.

## Bundle (retired 22 October 2026)

`tools/bundle.py` made the zips chats used to pass the project along (`bcer_project.zip`, `bcer_inputs.zip`). Replaced by the two repositories.

## Checks

    python3 tools/ab.py            # positions of every train at 24 moments vs tools/.baseline_viz.json: only the lines you meant to change should move
    python3 tools/check_gtfs.py    # ids unique, references resolve, times run forward
    python3 tools/perf.py          # frame times by view; see "How the page draws"
    python3 tools/shots.py '[{"name":"x","T":37800,"view":"sound","sel":"359"}]'    # screenshot to tools/out/x.png; look at one or two, not all

After an accepted build: `cp viz_data.json tools/.baseline_viz.json`.

## Fix list

### Done in Version 40 (8 October 2026, the scheduled update)
- 2 N.A.R. 5 and 6 passenger trains. 3 Selected train's route lit (`selRoute`, `drawSelRoute` in the page: one piece per run between stops, so a
  boat or train that doubles back is right; covered part at 28 % opacity, the rest 80 %, stops ringed). 5 Credits in the panel footer (links to
  the two Wikipedia articles and kettlevalleyrailway.ca). 6 Whitecourt trains by the main line to the St. Albert crossing (`via` points).
  8 Station panel is a departure board: Departures then Arrivals, "to"/"from" the real ends; list rows no longer say Eastbound/Westbound
  (`dirLabels` no longer read by the page). 9 and 17 Brendan's 31 Alberta traces in the graphs (`BITS` in `ab_lines.py`, by order in the file);
  every dashed stretch is gone (`dashed_estimates.kml` is empty); the CP Red Deer bypass (post-1948) is left out of both graphs (`LATER`), the
  CN reaches its downtown Red Deer station over CP track (`CN_OVER_CP` box, trace 2) and that stretch is drawn in CP colours (edge `own`,
  `BIT_OWNER`; 9.9 mi by the wye against 8.4 printed, accepted with `force`); Jaydot at 8.3 mi past Cressday along his trace; N.A.R. Waterways
  line on his Carbondale–Egremont trace (the old `via` points dropped). 10 "Hide boxes" toggle (controls bar; tap the small clock card or the
  panel heading to open again; starts minimised on a narrow screen; `S.min`, `setMin`, `insets()`; the phone panel sits above the control
  bar by its measured height, `--ctl`). 11 Rogers Pass by the Connaught Tunnel (`CONNAUGHT_PATH` in `nrwn_build.py`; route 519.1 mi against
  519.4 printed; Mount Macdonald and Shaughnessy tunnels 0 % used). 12 A mixed train's own first and last stops are drawn normally (not where
  it only enters or leaves the map: trips with a real end beyond). 13 Slider 3 a.m. to 3 a.m. 14 Chelohsin: the week without the fortnightly
  calls, turning at Sullivan Bay (~6.30 p.m. Wed); the southbound sailing starts there and calls at Simoom Sound 9.00 p.m.; `tools/check_vessels.py`
  (0 overlaps, 23 named vessels). 15 CN 195/196 from Jasper over the main line's track (`cn_north_build` now needs `mainline_build`); Table 166
  of the 1948 Guide: No. 195 leaves Jasper (Pacific time) 4.00 p.m. on its own, connecting with Nos. 1 and 3 from Edmonton, so no through
  running; the first rows agree with the 1949 table, except the 1948 table has no Yellowhead row. 16 CP Table 136 over the CN Kneehill–
  Drumheller–Rosedale (`CP_OVER_CN` box) and the joint line to Trefoil (trace 23). 18 Ships named (`SHIP` in `boats_build.py`; notes say the
  Joan/Elizabeth and Kathleen/Charlotte pairs could be the other way round). 19 Real ends (`real_ends.py`, applied in `build.py` finish).
  CP 3/4/7/8/13/14 ending at Medicine Hat is right: Table 6 times them nowhere east of it. 20 Cy Peck (`bfp`, livery `gif`). 21 Squamish
  (Government Dock) moved and renamed (one stop for PGE and boats, gid kept). 22 North Vancouver ferry (`bnv`, 152 sailings, livery `nvf`).

- Version 41 (8 Oct): Stettler has two stations (Brendan): CN on the north-south line at his point (`places` in `cn_209`), CP on the east-west
  line by its mileage (`noplace` in `cp_139`); before, both took the names file's point on the CN line and the CP route ran down to it, so
  2 km of CP line was drawn as CN. Today's track there is all Alberta Prairie Railway, in both graphs.

- Version 42 (8 Oct): **Strathmore.** The cp main line now runs Shepard–Strathmore–Gleichen on Brendan's trace (`ab_cp_t143s.csv`: Nos. 1–4's
  calls from Table 143, miles from Calgary; the east part in `mainline_build.py` is two legs, that file then Table 6). Nos. 7 and 8 (by
  Carseland, with stops) are on a line of their own, `cpc` (GTFS route CPCA): the main line's track (drawn by cp, segments 'none') except
  Shepard–Gleichen by Carseland, with the same station gids, so the boards still list them. On the cp line, Table 6's miles east of Gleichen
  are 4.5 less (counted by Strathmore); on cpc they are as printed. Nos. 13 and 14 (no calls between Calgary and Medicine Hat) are put on
  the Strathmore line: not confirmed. The page is about 0.35 MB bigger for cpc's copy of the route. `tools/ab.py` now names the trains moved.

### Waiting (Version 40)
- **Chelohsin fortnightly calls:** Phillips Arm, Fraser Bay and Allison Harbour are all left out of the week shown; whether Phillips Arm and
  Fraser Bay fall in the same week as Allison Harbour needs the guide's Route 5 page (not in the scans here).
- **CN M311/312 (Biggar):** Table 230 (Bodo) is not on the map, so there is nothing to give the real end to.
- **North Vancouver ferry peak windows** (7–9 a.m., 4–6 p.m.) are his default, unconfirmed. Liveries for the two ferries are Claude's picks.
- **Item 11, other crossings:** only Rogers Pass was checked (the route has no doubled-back edges, Spirals and Connaught covered 100 %).
- Credits are in the footer, which phones hide (as the sources were before).

### For the next update
23. (8 Oct, Brendan) **Rename the North Vancouver ferry landings**: "Foot of Lonsdale" becomes **North Vancouver**, "Foot of Columbia" becomes
   **Vancouver (NV Ferries)** (`P`, `PLACED`, `BY_HAND`, the `bnv` service's seq and name, and `_nvf()` labels in `boats_build.py`; gids follow
   the names). Sailing headings drop the bracket, so they read "North Vancouver to Vancouver".
24. (8 Oct, Brendan's guess) **The Mountaineer (Nos. 13 and 14) by Carseland**, not Strathmore: move them to the `cpc` line with Nos. 7 and 8
   in `mainline_build.py` (the `num not in ('7', '8')` tests, the `carse` rows, `LL = cpc if num in ('7', '8')`, and the route long name). They
   have no calls between Calgary and Medicine Hat; say in their note it is his best guess.

### Earlier items (kept for the record)

Brendan's list of 2–3 October (standard time; CP pier separate from the station; two-line ship names; "Steamer" badge; Cowans Point; steamer
names; Westview; the two Victoria terminals; mixed-only stations minor; the Chelohsin landings) was all done in Version 32. Nothing is waiting.
New items go here as he dictates them; do them only when he says to (he may expect them in the next rebuild — ask if it is not clear).
1. (3 Oct, "don't fix it yet, but consider") The S.I. terminal in Spokane was the Oregon Railroad & Navigation Co. (Union Pacific) station,
   Union Station on Trent Avenue, reached over UP track that is not in the S.I. trace. The trace ends 1.9 mi short by the timetable, and Union
   Station (about 47.6607, -117.4185) is 1.8 mi west of the trace's end, so the two agree. Options: a straight estimated run along Trent Avenue
   into the station, or a UP trace from Brendan.
2. (4 Oct, "for the next update") Northern Alberta Nos. 5 and 6 (McLennan–Hines Creek) are coaches and sleepers in the Guide, not a mixed
   train: in `ab_nar_t179a.csv` change `kind=mixed` to `kind=passenger` on both `#train` lines (they then show as No. 5 and No. 6, not M5
   and M6) and re-run `ab_nar_build`.
3. (4 Oct, held until he says) Light up a selected train's route, as TRAVIC does: when a train or boat is selected, draw its line between
   its first and last stop on top of the map in its colour, **dimmer for the part already covered and brighter for the part to come**, with
   its stops picked out. Page only (`page_template.html`): each trip's stops carry the distance along the line and each line's points carry
   the same distance, so cut the track between them; build the path when the selection changes, not every frame.
4. (4 Oct) Brendan is looking for more branch-line shapefiles or traces to replace the dashed estimates (listed in the Alberta section).
   A trace goes in `traces/` and into the graph in `ab_lines.graph` (see how `nar_barrhead_branch.tsv` is added).
5. (4 Oct, with the next update) Add a credits line to the page from the Credits section above.
6. (4 Oct, found with Brendan; change when he says) **St. Albert line out of Edmonton.** As drawn, CN Table 210 (Whitecourt) leaves the
   Edmonton station over the Canadian Northern set's direct line: 9.7 mi to St. Albert against 11.4 printed. If instead it follows the main
   line towards B.C. to where the two cross (53.5801, -113.5931; 6.6 mi) and turns north there, it is 11.2 mi. The historical file
   (`traces/hr_rails`) has no direct line and starts the St. Albert line at that point, so the direct line was gone by 1948. To change: in
   `ab_cn_build.py` give `cn_210` two `via` points on the main line (one about half way, one at the crossing) with `places` for them, and
   drop its `force`. The Athabasca line (Table 218) is drawn over the Northern Alberta to Morinville (25.9 mi against 26.0 printed), which
   fits: the file gives Morinville–St. Albert as abandoned in 1948, the 1946 Guide has a St. Albert stop and 24.7 mi, the 1948 Guide neither.
7. (4 Oct) Brendan: the straight dashed lines look fine; the historical file is for build and abandonment dates (routing decisions), not for
   bending the estimates.
8. (4 Oct, for the next rebuild; Brendan chose it) **Station panels become a departure board.** The "Eastbound / Westbound" headings with
   each line's fixed list of places are wrong off the original lines (at Calgary every CP arrival reads "Eastbound", to Kamloops, Revelstoke,
   Banff and Medicine Hat). Replace the direction groups with one list in time order, each row: time, train (number, name), and where it is
   going from here (its last stop; "from X" for a train that ends here). No compass words. Works the same for steamers and B.C. Electric
   cars. Settled with him: two lists one after the other, **Departures** (every train leaving: time it leaves, train, "to" its last stop) then
   **Arrivals** (every train arriving, through trains included: time it arrives, train, "from" its first stop). A through train is on both, so
   a station where the table prints an arrival and a departure shows each in its own list. A train that starts here is on Departures only,
   one that ends here on Arrivals only. The line's
   `dirLabels` are then no longer needed by the station panel (check where else the page uses them before removing).
9. (4 Oct, trace to come from Brendan) **Red Deer, CN terminal.** The CN trains of Table 204 reached their Red Deer terminal over CP track,
   swinging south of downtown; as drawn they follow the Canadian Northern set's spur, 5.6 mi from Red Deer Junction against 8.4 printed
   (accepted with `force` in `cn_204`). He will send a crude trace: add it to the graph in `ab_lines.graph` (the CN graph leaves CP track
   out, so the trace must cover the CP part), give Red Deer (CN) a `places` point at the terminal, and drop the `force`.
10. (5 Oct, for the next version) **Phones.** Brendan: the artifact is basically unusable on mobile. Add a way to minimise the info boxes:
   the title and legend card collapses to the clock and day (tap to open), the right-hand panel becomes a sheet that slides down to its
   heading, the control bar stays. One version for phone and desktop (the same toggle everywhere); on a narrow screen start collapsed. Page only: CSS, a toggle, and `insets()` must give the freed space
   back to the map so the views fit it. Check with `tools/shots.py` at a phone size (390 x 844) and `tools/perf.py`.
11. (5 Oct, for the next update) **Rogers Pass.** Brendan: coming from the west the CP route goes into the Mount Macdonald Tunnel (opened
   1988, so not there in 1948) and then jumps from inside it to the Connaught Tunnel as the shorter track. Likely cause: the two tunnels cross
   in plan and the route graph joins track that shares a point (or lies within 4 m), so it treats the crossing as a junction. In 1948 the line
   was the 1916 one: up the Beaver valley on the upper (Stoney Creek) line, through the Connaught Tunnel, Glacier station at its west portal,
   down the Illecillewaet. The 1988 line (the lower Beaver valley grade, the Mount Shaughnessy and Mount Macdonald tunnels) must be kept out.
   The CP route is `R['CP']` in `nrwn_routes.pkl` (made by `nrwn_build.py`): re-route that stretch with points forced onto the Connaught line
   (or leave the 1988 track out of the graph), check Glacier and the stations either side against the printed miles, and look for the same
   fault wherever a newer line crosses an older one (the Spiral Tunnels are 1909 and fine).
12. (5 Oct, for the next update) **Mixed-only stations.** The rule that a station only mixed trains call at is drawn minor gets an exception:
   a station where a mixed train starts or ends is drawn normally (as its `principal` flag in the data says). In `page_template.html`, where
   `only` is worked out, leave out each mixed trip's first and last stop. Default for trains cut at the Saskatchewan boundary (their first
   or last stop on the map is not where the train really starts or ends, e.g. Compeer, Hayter, Jaydot): that end does NOT count; the Alberta
   tables carry `from=` / `to=` for these, so `ab_lines.py` can mark the trip (the page already has a `beyond` field on trips). Brendan to confirm.
13. (5 Oct, for the next update) **A 24-hour time slider.** It runs 5 a.m. to 3 a.m. (`min="18000" max="97200"`, `TMIN`/`TMAX` 5 h and 27 h), so
   3 to 5 a.m. is never shown, and with Alberta the main lines are busy then (about 54 trips on the move at any moment between 2 and 4 a.m.,
   all services counted; fewest trips START in the hours 2, 3 and 4). **Settled: 3 a.m. to 3 a.m.** (the slider already ends there and the
   station boards already use a 3 a.m. window). Change the slider's min, `TMIN`, the
   tick labels, and the carry-over test `t.end <= k * 86400 + 5 * 3600`; check trains running through the boundary on each day.
14. (5 Oct, for the next update; looked into the same day) **Chelohsin in two places at once.** Union Route 5 is entered as two trips whose
   estimated times overlap on Wednesday evening: northbound `BU5N-N` runs Monday 5.00 p.m. to Wednesday 10.00 p.m. (ending at Allison
   Harbour), while southbound `BU5S-S` leaves Simoom Sound at 8.00 p.m. the same Wednesday. So from 8 to 10 p.m. there are two ships, one
   still northbound and one already southbound from a port the first has not come back to. The fault came in with the Version 32 landings
   (Allison Harbour added at the north end without moving the southbound start). Only the Vancouver hours are printed; the rest are
   estimates in `boats_build.py`. Fix: make the southbound trip start where and when the northbound ends (or join them as one voyage), in the
   guide's order of calls, and add a check to `tools/` that no vessel has overlapping trips. The Friday Alert Bay trip does not overlap.
   The root of it: the guide has Sullivan Bay and (fortnightly) Allison Harbour on Wednesday p.m. northbound AND the southbound leaving
   Simoom Sound on Wednesday p.m.; Allison Harbour is some three hours beyond Sullivan Bay each way, so a week that includes it cannot also
   leave Simoom Sound that evening. **Brendan's decision (5 Oct): show one week's version of the schedule, not every fortnightly call.** So
   pick one of the two weeks and enter only its calls (the fortnightly ones are Phillips Arm, Fraser Bay and Allison Harbour; Bones Bay is
   by arrangement). Read the guide's Route 5 page to see which fortnightly calls fall in the same week; unless it says otherwise use the week
   WITHOUT Allison Harbour, turning at Sullivan Bay, so the Wednesday evening departure from Simoom Sound works. Say in the trip note which
   week is shown and which calls the other week adds. The same rule for any other boat with alternate-week calls.
15. (6 Oct, for the update) **CN Nos. 195 and 196 end at Yellowhead: an artifact.** The table (`cn_1949_tables225_226.csv`) has No. 195
   leaving Jasper 4.00 p.m. and No. 196 reaching Jasper 6.00 a.m., with the rows Jasper to Yellowhead already in it; `cn_north_build.py`
   was written when the map stopped at the B.C. boundary and starts the cnn line at Yellowhead (`ANCH`, `BORDER`). Carry the line and both
   trains on to Jasper over the main line's track (drawn by the cn line: `owner 'none'`, as Yellowhead–Red Pass Jct is now), using the cn
   line's Jasper station (`CN_JASPER`); fix the notes and the GTFS route text ("Shown from the B.C. border"). While there, read the 1948
   Guide's Table 166 (Edmonton–Jasper–Prince Rupert, in `scans/og1948_cn/`) to see whether these trains or their cars ran through from
   Edmonton, and whether its times agree with the 1949 tables (the check promised when standardising on the May 1948 Guide).
16. (7 Oct, for the update; history from Brendan) **Drumheller valley: CP ran over the CN.** In 1927 the CPR got running rights over CN track
   from Kneehill to Eladesor Junction (Rosedale), and from there the line south-east toward Trefoil was built as JOINT track, used by both
   (sources he gave: zelmeroz.com/album_rail/ab/kozma/cnl_0002-Drumheller.pdf and the Atlas of Alberta Railways, chapter 15). So for CP
   Table 136 (`cp_136`, Bassano–Rosemary–Trefoil–East Coulee–Rosedale–Drumheller–Kneehill): Kneehill–Drumheller–Rosedale is CN track, which
   the network still has, so run it over the CN line instead of the dashed straight (the CP graph in `ab_lines.py` leaves CN track out: give a
   line a way to use the CN graph between two named stations); Rosedale–Trefoil is one track shared with CN Table 193 (`cn_193`), which the
   map already draws once (still a straight estimate until there is a trace). Say "over the Canadian National" / "joint line" in the station
   notes and the trip notes. Check the CP line from Calgary (`cp_143`), which ends at Kneehill, meets the CN there.
17. (7 Oct, for the update) **Brendan's Alberta traces: `traces/alberta_railway_bits.kml`** ("this should be everything"): 31 Google Earth
   lines, about 1,700 miles, one folder. They cover EVERY dashed stretch on the map (checked: all but a handful of the 213 stations on dashed
   stretches lie within 1 km of a trace), and more: `CP Via Strathmore` (Shepard–Gleichen, 44.9 mi, for CP Nos. 1 to 4 and their stops in the
   comments of `ab_cp_t143a.csv`), `CP Edmonton High Bridge`, `Red Deer Bypass (est)` with `CN Downtown Red Deer Post 1941 Access Via CP` and
   `CN to Red Deer Wye` (item 9), `Carbondale - Egremont`, `Hines Creek`, `Waterways`, `Luscar`, `Mountain Park`, `CP Rocky Mountain House`,
   `High River-Fort Mcleod` (stops about 4 km short of Macleod: join it to the cr line), `Glenwood-Raymond`, `Turin`, `Jaydot-Foremost` (runs
   on past Jaydot: place Jaydot at its printed mileage along it and drop the `HAND` estimate), `Langdon-Wimborne`, `Mossleigh` (Mossleigh–
   Suffield, the whole Lomond line), `Rimbey`, `Warden Jct`, `Empress` (Empress–Irricana), `aw` (Rosemary–Rosedale: the CP and joint line of
   item 16), `Cosway Wye`, `Cosway Kneehill`, and eight `Untitled Path`s, by their ends: Suffield wye; Warden–Hanna; Scapa-side to beyond
   New Brigden (the Hemaruka line); Botha–Compeer; Star–Lloydminster; Willingdon–Vegreville; St. Paul–Heinsburg; Abilene–Beaver River.
   To use: add them to the graphs in `ab_lines.graph` (CP ones to the CP graph, CN and N.A.R. ones to the CN graph; the Drumheller valley
   line to both), re-run, and the straight estimates should vanish; his traces are drawn SOLID (his rule). Then check each line's traced
   miles against the printed, and regenerate `dashed_estimates.kml` (it should come out nearly empty).
18. (8 Oct, for the update; Brendan's reading of CP Table 169) **Name the Nanaimo and night boats** (`bvn`, `bvv` in `boats_build.py`).
   Summer slots as entered fit three ships exactly:
   - Princess Elaine: Vancouver 10.00 a.m. to Nanaimo, back 1.45 p.m. (Vancouver 4.15); Vancouver 5.15 p.m., night at Nanaimo, back 6.30 a.m.
     (Vancouver 9.00). (Brendan: from the schedule to June 3.)
   - Princess Victoria: Vancouver 7.15 a.m., back 10.45 a.m. (Vancouver 1.15 p.m.); Vancouver 2.15 p.m., back 6.00 p.m. (Vancouver 8.30).
     (Brendan: from the June 4–24 and after-Sept. 7 table.)
   - Left over: Vancouver 8.15 a.m., back 11.45 a.m. (Vancouver 2.30 p.m.) daily, plus Sundays Vancouver 2.00 p.m., back 5.30 p.m.
     (Vancouver 8.15). Brendan: Joan and Elizabeth (also in Table 168) take the extra summer slots, he is not sure which. Claude's deduction:
     it is the night boat that came in from Victoria at 6.00 a.m., which does the Nanaimo trip and goes back to Victoria on the 11.00 p.m.
     night boat; so Joan and Elizabeth alternate day by day, and the two night boats get the same names (ship on the Victoria night boat
     on day d = the Nanaimo extra on day d = the Vancouver night boat of day d-1). A week has seven days, so the alternation breaks once a
     week. Split those daily trips into one per weekday (CP_MON1 … CP_SUN1 exist) to carry the names.
     **Brendan's decision (8 Oct): pick one week and name the ships on that assumption** (e.g. Joan on the Nanaimo extra on Monday,
     Elizabeth on Tuesday, and so on through Sunday), and say in each trip's note that in the alternate week it would be the other ship.
     **Better fit found the same evening (Claude, put to Brendan):** with Table 168's summer day boats included, two ships cover every
     Victoria and extra Nanaimo sailing in fixed DAILY rounds, no alternation and no weekly break:
       ship X: night boat Victoria 11.00 p.m. to Vancouver 6.00 a.m.; Nanaimo 8.15 a.m., back 11.45 a.m. (Vancouver 2.30 p.m.); afternoon
               boat Vancouver 3.15 p.m. to Victoria 8.30 p.m.; night boat again at 11.00 p.m.
       ship Y: night boat Vancouver 11.00 p.m. to Victoria 6.00 a.m.; morning boat Victoria 10.30 a.m. to Vancouver 3.45 p.m. (Sundays 8.00
               a.m. to 1.15 p.m., then the Sunday Nanaimo trip 2.00 p.m., back 5.30 p.m., Vancouver 8.15 p.m.); night boat again.
     X and Y are Joan and Elizabeth; which is which the times cannot tell. The Triangle Route works the same way with the other two
     (Kathleen and Charlotte): one ship Vancouver 10.30 a.m. – Victoria – Seattle 9.30 p.m., then Seattle 11.00 p.m. direct to Vancouver
     8.00 a.m.; the other the reverse (Seattle 9.00 a.m. – Victoria – Vancouver 6.00 p.m., then Vancouver 10.45 p.m. direct to Seattle
     7.30 a.m.). Again which is which is not in the times. **Brendan agreed (8 Oct): use these daily rounds, NOT the alternating week
     above.** Pick the names (say Joan = X, Elizabeth = Y; Kathleen = Vancouver-first Triangle, Charlotte = Seattle-first) and say in each
     note that the pairing could be the other way round. Elaine and Victoria as listed first.

19. (8 Oct, for the update) **Real origin and destination for trains that run off the map.** Shown when a train is clicked ("Vancouver to
   Montreal", then a quieter "on this map: Vancouver – Wainwright") and as the GTFS trip_headsign; stop times unchanged, nothing added to
   the timetable. Brendan supplies the real ends (list sent to him 8 Oct: CN 1–6, 9–12, 159/160, 267/268, 311/312; CP 1–4, 7/8, 13/14,
   51/52, 63/64, M419/420, M480/481, M611/612, M617/618, M643/644, 543/544, M809/810); take his answers as given, no lookups.
   **Brendan's answers (8 Oct, from more pages of the timetable):** CN 1/2 Montreal; CN 3/4 Toronto, and they are also named "Continental
   Limited" (add the name); CN 5/6, 9/10, 11/12 Winnipeg; CN 159/160 end where shown (Bonnyville–Fort Kent–Beaver River); CN M267/268
   Loverna; CN M311/312 Biggar. CP 1/2 Montreal; CP 3/4 Toronto (The Dominion); CP 7/8 Montreal (The Dominion); CP 13/14 Chicago; CP 51/52
   Winnipeg; CP M419/420 Wilkie; CP M480/481 Macklin; CP M617/618 Kerrobert; CP M643/644 Shaunavon. No change (real end is on the map):
   CP 63/64 Lloydminster, CP M611/612 (go with the table), CP 543/544 Coutts, CP M809/810 Huntingdon.
   Also check: CP 3/4, 7/8, 13/14 end at Medicine Hat on the map while No. 1/2 run on to Walsh (fine for 13/14 if they go by Moose Jaw;
   look at why 3/4 and 7/8 stop there).

20. (8 Oct, for the update) **Gulf Islands Ferry Co., MV Cy Peck, Fulford Harbour–Swartz Bay.** Source: Brendan's 1941 summer schedule
   (first a 1940 advertisement with only the 8.15/4.00 and 9.30/5.00 sailings). He knows the Cy Peck stayed on the route to at least 1951
   (with the company until it sold to BC Ferries, 1961), schedule broadly the same through the 1940s; the map's summer week fits a summer table.
   Daily except Wednesday: lv Fulford Harbour 8.15 a.m., 10.15 a.m., 4.00 p.m., 6.45 p.m.; lv Swartz Bay 9.30 a.m., 11.15 a.m., 5.00 p.m.,
   7.45 p.m. Wednesday only: lv Fulford Harbour 8.15 a.m.; lv Swartz Bay 7.00 p.m. (between them she makes irregular Gulf Islands excursions, per Brendan: no route to draw, so she is shown at Swartz Bay
   and the Wednesday note says "Irregular Gulf Islands excursions between these sailings").
   One ship alternates: F 8.15 → S, 9.30 → F, 10.15 → S, 11.15 → F; F 4.00 → S, 5.00 → F, 6.45 → S, 7.45 → F (nights at Fulford).
   Departures only are printed: crossing time an estimate, 40 min (S 9.30 back for F 10.15 caps it at 45 min; ~6 nautical miles);
   say so in the note unless Brendan gives one. Positions from the B.C. names file: Fulford Harbour community (48.7667, -123.4500, ferry
   at the head of the harbour), Swartz Bay landing (48.6833, -123.4167); sea lane down Fulford Harbour, round Isabella Point and across
   Satellite Channel/Colburne Passage (check the water outline, `sea.py`). Note on the trips: "Gulf Islands Ferry Co. Schedule from the
   1941 summer timetable; the Cy Peck was on the route through the 1940s." Add to credits (Brendan's 1941 schedule).

21. (8 Oct, for the update) **Squamish dock position and name** (Brendan): the dock is at 49.694717, -123.155131 and should be called
   "Squamish (Government Dock)". Now one stop PGE_SQUAMISH_DOCK "Squamish Dock (PGE)" at 49.696972, -123.153830 (~270 m north-east, on the
   PGE waterfront spur; `island_pge_geometry.py` SQUAMISH_DOCK, `boats_build.py` 'Squamish Dock' -> PGE stop) serves both the Union boats
   (Routes 8, 8A) and the PGE trains. **Brendan (8 Oct): his original pin for the PGE station was too far north; move the one shared stop
   to his new point and rename it "Squamish (Government Dock)"** (stop name, PRINCIPAL set, PGE notes, route long name "Squamish (Government
   Dock) – Lillooet – Quesnel", boats' 'Squamish Dock' key). Extend the PGE line from the old SQUAMISH_DOCK down the waterfront to the new
   point (~270 m; along any track in the traces, else a short straight piece drawn solid as his position) and keep the timetable miles.

22. (8 Oct, for the update; Brendan: "yes") **North Vancouver ferry**, Foot of Lonsdale (49.30991769874169, -123.08072971160446) – Foot of
   Columbia (49.28595029820523, -123.1017947490752), worked out with him in a separate chat on 5 October ("North Vancouver Ferry schedule"):
   no printed table, a reconstruction from the described service. 6 a.m. to midnight. Base: Ferry No. 4 alone, Lonsdale :00 and :30,
   Columbia :15 and :45 (2-minute turn). Weekday peaks about 7–9 a.m. and 4–6 p.m. (windows his default, not confirmed): Nos. 4 and 5,
   departures from both piers at :00, :20 and :40 (7-minute dwell, 40-minute round). Weekends base only. Crossing about 15 min (sailing
   13 min animated), straight line between the piers. An intended exception to the no-road-ferries rule (it worked as an interurban link).
   West Vancouver ferries out (ended February 1947). Note: "Times reconstructed from the described frequency, not a printed timetable."

### Ideas for a later update (not tomorrow's)
- (7 Oct) **Set the map in one real week**, e.g. Monday 5 July to Sunday 11 July 1948 (5 July 1948 was a Monday; the summer sailings and
  The Mountaineer both run then). The day selector reads dates, the title names the week, the map still loops it. It lets in services that
  run less than weekly, by their real dates: Princess Maquinna, West Coast of Vancouver Island (from Victoria every 8 days: July 5, 13, 21,
  29); Princess Louise and Princess Norah, Vancouver–Skagway; the Canadian Australasian Line (it leaves the map within a day or so: decide
  where its lane ends); others. Needs: their tables, B.C. port positions (the names file on hand is Alberta only), and the page's
  carry-over of a trip past its start raised from 3 days to the longest voyage. Brendan is saving this for a future update.
  (12 Oct) Week choice discussed: Brendan notes the Alaska Steamship and CP Alaska services hardly run in August, so a July week:
  5-11 July 1948 (second Friday 9 July: Table 130 monthly trains; Maquinna sails 5 July; but US July 4 holiday observed Mon 5 July) or
  12-18 July (no holiday; Maquinna 13 July; no second-Friday trains). Alaska Steamship dates known only to the 26 June sailing: July
  sailings extrapolated (Saturdays, Aleutian/Baranof alternating) unless a later list turns up.
  DECIDED (Brendan, 13 Oct 09:56): the map is set in the week Monday 5 - Sunday 11 July 1948. The Alaska Steamship pattern is assumed to
  continue for the Aleutian, Baranof AND Denali. Worked out from the printed dates (check at build time):
  - Aleutian: sailed Sat 26 June -> Ketchikan Mon 28, Juneau Tue 29, Seward Thu 1 July (9.00 p.m.), Valdez and Cordova Fri 2, Juneau Sun 4,
    Ketchikan Mon 5, Seattle Thu 8 a.m.; sails again Sat 10 July 9.00 a.m. (Ketchikan Mon 12).
  - Baranof: sails Sat 3 July -> Ketchikan Mon 5, Juneau Tue 6, Cordova and Valdez Thu 8, Seward Fri 9 (boat train Fri, not Thu: the
    Alaska Railroad boat special moves to Friday), Juneau Sun 11, Ketchikan Mon 12, Seattle Thu 15.
  - Denali (Kodiak route, every 21 days: 6 May, 27 May, 17 June -> 8 July): the 17 June trip ends Seattle 3 July; the 8 July sailing
    follows the 27 May pattern (it alternates): Ketchikan Sat 10, then outports, Kodiak about 15 July. Needs port points: Yakutat,
    Seldovia, Kodiak, the "outports" (unnamed: route by Kodiak only), and the Kodiak water (simp_north_coast.gpkg reaches -153.8 W).
  Other consequences: Table 130 second-Friday trains run (Fri 9 July; M464 not Fri; M463/M466 Sat 10); Princess Maquinna sails Victoria
  Mon 5 July; the Mountaineer runs; CP summer boats run; Monday 5 July is the US Independence Day holiday (Black Ball 'Sundays and
  holidays' sailings on Monday). Page work: day selector reads dates, title names the week, trips may run past the week's end and come
  back round (voyages up to about 15 days: raise the carry-over limit). Alaska Railroad boat special follows the Baranof (Fri 9 July).
  REVISED (Brendan, 13 Oct 10:01):
  - Monday 5 July is treated as an ordinary Monday (no US holiday sailings).
  - NO real-date rebuild: the page keeps its Monday-Sunday week and simply says it is approximately the week of 5 July 1948.
  - Page title: "The Digital Model Railway" (replaces "Railways of British Columbia"). Explanation line: "Mainline, interurban and
    steamship lines in the summer of 1948."
  - B.C. Electric trains carry a note that their timetables come from several years (1942-1949).
  - Steamships that sail less than weekly carry a note with the date of the sailing shown and how often they really run (e.g. Maquinna
    every 8 days; Denali every 3 weeks; Aleutian/Baranof each fortnightly, alternating weekly; Chelohsin fortnightly calls).
  - Any steamship routing that runs beyond the week is drawn in full, lane and ports of call, even where the ship does not get there within
    the week shown (e.g. the Denali's Kodiak route, the Alaska boats' ports).
  Ports (Brendan, 13 Oct 10:20): Yakutat 59.548500, -139.733907; Seldovia 59.440491, -151.720376; Kodiak 57.787078, -152.402206 (off
  the edge of the water layer: the ship simply disappears where the water ends).
  CP Table 172, Vancouver - Skagway (all year): cp_t172_skagway_1948.csv (Princess Louise and Princess Norah, sailings 23 and 26 June, 3 and
  7 July; ports Vancouver, Alert Bay, Prince Rupert, Ketchikan, Wrangell, Juneau, Skagway; only Vancouver timed). Connects at Skagway with
  the White Pass (Louise ar Wed 7 a.m., lv Thu 8 p.m.).
  CP Table 173, Princess Maquinna (west coast of Vancouver Island): cp_t173_maquinna_1948.csv (30 ports Victoria - Chamiss Bay; 5 July
  sailing). Ports to place from the B.C. names file; list unplaced ones for Brendan.
  Points (Brendan, 13 Oct 10:42) in cp_t172_173_ports.csv: Wrangell, Herbert Arm (est), Carmanah (est), Franklin River (est), Muchalat,
  Sydney Inlet; Markale (est, at Markale Point) and Bedwell River from the names file. Every other Maquinna port is in the names file
  (Port Renfrew, Clo-oose, Bamfield, Sarita, Ecoole, Kildonan, Green Cove, Ucluelet, Port Albion, Tofino, Clayoquot, Kakawis, Ahousat,
  Refuge Cove, Hesquiat, Nootka (Landing) for Nootka Cannery, Tahsis, Ceepeecee, Hecate (abandoned locality), Zeballos, Chamiss Bay).
- BRENDAN'S TO-DO (13 Oct): find out more about the White Pass & Yukon's connecting steamers mentioned in its table: S.S. Tutshi from
  Carcross to West Taku Arm (Tagish Lake), in connection with the CP steamships at Skagway; and the "modern sternwheel steamers" from
  Whitehorse to Dawson City twice a week. Need sailing days/times, ports and (for the lanes) the Yukon lake and river water.
  (13 Oct 11:10) Brendan's ESTIMATED British Yukon Navigation week: byn_1948_estimated.txt (Ship A Whitehorse Mon 20:00 - Dawson Wed
  04:00 - up Thu 06:00 - Stewart Landing Fri 15:00 - Whitehorse Sun 18:00; Ship B upstream from near Fort Selkirk Mon - Carmacks Tue
  22:00 - Whitehorse Thu 19:00; S.S. Keno Mayo Wed 08:00 - Stewart Landing Fri 11:00). Points raised with him: only one downstream
  sailing a week (the table says twice); the week does not loop cleanly for Ship B (mid-river Monday, idle in Whitehorse Sunday) or for
  the Keno (no return to Mayo). Needs: Yukon River / Lake Laberge / Stewart River water (or a river trace for the lanes); points for
  Whitehorse landing, Lake Laberge, Carmacks, Five Finger Rapids, Fort Selkirk, Stewart Landing, Dawson City, Mayo (no Yukon names file).
  AGREED (11:12): Claude's version (end of byn_1948_estimated.txt): Ship B adds a Friday 20:00 sailing from Whitehorse (Dawson Sun,
  back Thu), so twice a week; the Keno returns Fri 14:00 - Mayo Mon. A = Klondike, B = Casca (hypothetical; say so in the notes). Points
  received (11:25, in byn_1948_estimated.txt; downriver calls Carmacks and Fort Selkirk only, upriver every point). Still needed before
  building: Yukon River, Lake Laberge and Stewart River water, or a river trace for the lanes.
  Water received (13 Oct 11:32): traces/yukon/yukon_water.gpkg (StatCan hydro, EPSG:3347, one multipolygon, -141.0 to -123.8 W, 60.0 to
  69.2 N). Checked: the Yukon River from Whitehorse through Lake Laberge to Dawson and the Stewart River to Mayo are one connected water
  body (joining pieces within 30 m); all ten points lie on it or within 70 m. Add it to water_extra.py (page) and water_extra.pkl (lanes).
  The Yukon boats are ready to build.
- CN Steamships T.S.S. Prince George, Alaska cruises (Brendan, 13 Oct 11:57): cn_t315_prince_george_1948.csv (Table 315; 10-day cruises,
  Vancouver - Ocean Falls - Prince Rupert - Ketchikan - Taku Glacier - Juneau - Haines - Skagway and back by Wrangell and Gardiner Canal /
  Douglas Channel). Week shown: the 30 June cruise southbound (Skagway Mon 5 7.00 p.m. -> Vancouver Sat 10 9.30 a.m.) and the 10 July cruise
  leaving Sat 10 9.00 p.m. (to Ocean Falls Sun 11; drawn in full beyond the week). One ship: the week does not loop for her (a 10-day
  cycle), so show the two trips as dated and exempt her from the 'one ship in two places' wrap check if it complains. Alaska ports run on
  Alaska time (one hour behind Pacific north of Ketchikan): times shown in Pacific. Haines and Taku Glacier points received (12 Oct 12:02,
  in cp_t172_173_ports.csv). Still from the names file:
  Gardiner Canal / Douglas Channel (cruising point; names file); Ocean Falls from the map or names file.
- S.S. Tutshi (Brendan, 13 Oct 12:04): tutshi_1948_estimated.txt (model schedule: Mon/Thu/Sat Carcross - Taku Landing, Wed/Fri/Sun
  Carcross - Ben-My-Chree, overnight, Tue none; 2.00 p.m. out, 11.00 a.m. back; meets WP&Y Nos. 5, 3, 2). Taku Tram gone by 1936
  (Brendan): DECIDED Ben-My-Chree only, Wed and Sun, after excursion train No. 3 (end of the file). Ben-My-Chree point and
  northern B.C. water received (12:14; traces/yukon/bc_north_water.gpkg; needs a 678 m join at the Carcross narrows). WAS NEEDED: points for Carcross dock
  (or the WP&Y station), Golden Gate, Taku Landing, Ben-My-Chree; WATER for Bennett Lake, Nares Lake, Tagish Lake and Taku Arm: the Yukon
  file stops at 60 N and the B.C. water layer stops at 58.5 N, so the B.C. part (Taku Arm, West Taku Arm, Ben-My-Chree, Taku Landing,
  Atlin Lake) has no water yet.

## Washington State (planned; Brendan 9 October 2026, "await further instructions")

Files: see Credits (Mississippi Rails KMLs by Tony Howe and David Price; Washington State place names). The main KMZ is 364 lines only (no
station or milepost points), each named by its ends ("Kalama WA to Vancouver WA") with a description giving its length and its build,
transfer and abandonment dates ("Built by Northern Pacific RR 1880-81 ... to Burlington Northern RR 3-2-1970"): use the dates to keep
post-1948 track out and pre-1948 abandonments out, as with the Alberta historical file.
Brendan's rules so far:
- Seattle–Portland trains were pooled by UP, NP and GN: enter each pool train once (no duplicates across the three railways' tables).
- Seattle: UP and the Milwaukee used Union Station; GN and NP used King Street Station, next door. Two stations.
- UP reached Seattle past Tacoma by a different line from GN and NP (to be confirmed).
- The pool trains probably went by Point Defiance (not certain).
- Place stations by MILEPOSTS (printed mileage along the traced line, anchored at known stations) rather than by the place-names file,
  which is for anchors and checks.
- Include the extensions into Portland. Before launch Brendan will add UP track on the south bank (Oregon side) of the Columbia, connecting
  to Spokane.

Progress (9 Oct): one transcription worker (about 0.28 million tokens) wrote 40 files `wa_*.csv` from the scans in `scans/wa1948/` (its
notes: `scans/wa1948/PROGRESS.md`; instructions `scans/TRANSCRIBE_WA.md`). Brendan's UP south-bank traces:
`traces/washington/Oregon-Washington_RR_Navigation_Co.kmz` (110 lines, OR and WA). Puget Sound Navigation boats are in, treated like the
Black Ball. Idaho: trains end at their last timed Washington station; only trains that enter Washington are on the map (Oregon parts of their
runs included). SP&S served both NP and GN (Brendan). Duplicates to drop at build: GN Table 6 (= SP&S Table 1), the via-S.P.&S. blocks of
NP Table 3 and GN Table 5, UP Table 62 (= Camas Prairie Table 49), UP Table 66 (= 67/68 of Table 57), UP Table 74 (= NP 422/423), UP Table 75
and the pool trains of GN Table 46 and UP Table 5 (= NP Table 4); GN 355–360 Seattle–Vancouver already on the map. The worker filled some
Chicago / St. Paul far ends "from the usual routes", not the scans: to be confirmed by Brendan.

Brendan's decisions (9 Oct): (1) Oregon trains whose timetable and track we have and that share track with trains running through Washington
are in (UP 17/18 Portland Rose, 11/12 Idahoan, 105 City of Portland, Portland–The Dalles–Pendleton); they leave the map where the data ends.
(2) WI&M kept for now. (3) Far ends: confirmation list sent to him. (4) Pool trains routed as the timetable says (UP and GN: via
Steilacoom / Point Defiance; NP 422/423 by Lakeview and Fort Lewis). He is checking the ambiguous signs (list sent) and the odd figures.

Built (Version 43, 9 Oct): step `wa_build` (27 lines: np_*, gn_main/043/045, sps_main/004, up_*, cprr, milw_*), machinery `wa_lines.py`
(graphs per set of railways 'wa:np+up' over `wa_tracks.py`'s 1948 lines; loose trace ends tied within 150 m; stations: only principal
stations and table ends placed, from hand points, trace ends named after places, or the names file (nearest to track; `COUNTY` picks among
same-named places), the rest by printed mileage). `ab_lines.py` now has a `RAILS` registry, `EXT_GRAPH` / `EXT_PLACE` / `EXT_GID` hooks,
`make_graph(feed, tie_end, tie_loose)`, and spec options `graph`, `shift` (0 for Pacific-time tables), `ends`. Page: kinds o NP, d SP&S,
u UP (and Camas Prairie), m Milwaukee; colours --np --sps --up --milw (Claude's picks); views puget, inland, columbia; `fit()` no longer
spreads all points into Math.min (stack overflow with the bigger data).
Still open: straight estimates NP Eureka–Walla Walla (21 mi, no NP trace there), UP Dayton–Turner (8 mi), Milwaukee's last 0.7 mi into
Seattle; Wilma placed at the end of the Camas Prairie trace (approximate); Seattle Union Station, and the Spokane and Tacoma stations of each
railway, are approximate (city points or trace ends): list to Brendan. Far ends (confirmation list sent) not yet applied. PSN Bremerton,
Edmonds–Port Ludlow and San Juan inter-island sailings not yet built (no printed times: patterns to settle with Brendan); the Chinook's
Port Angeles–Victoria and the Anacortes–Sidney sailings were already on the map.

Brendan's far ends (9 Oct, to apply in `real_ends.py`; the WA trip ids are NP-1 etc.): NP 1/2 Chicago; NP 3/4 Chicago (not St. Paul); GN 1/2
and 3/4 Chicago; GN 27/28 St. Paul; MILW 15/16 and 17/18 Chicago; UP 17/18, 105/106 and 11/12 Chicago; NP 311–314 Lewiston; UP 67/68
Wallace; Camas Prairie 73/74 Lewiston; WI&M 1–4 Potlatch and Bovill (as the table: 1 and 4 Potlatch, 2 and 3 Bovill).
SP&S Portland sections (Brendan): in general the NP and GN Portland sections are destined for Chicago, and are the same train as the Seattle
sections unless the table says otherwise east of the junction points (Spokane / Pasco). Over the SP&S, draw those sections in their GN or NP
colours (the GN Empire Builder and Oriental Limited Portland sections, SP&S 1–4, in GN colours; the North Coast Limited's Pasco connection in
NP colours), unless they are SP&S trains in their own right (the locals 5/6 stay SP&S). Brendan: "await further input" before building.

Brendan's sign keys (9 Oct): UP Table 5: * daily, f flag; b, n and the other conditional stops are not modelled. UP Table 56: * daily,
dagger ex Sunday, double dagger ex Saturday, section Sunday only, f flag, k Saturday only, italic z Monday and Friday, sharp Tue/Thu/Sat,
solid circle mixed, solid square (ride in the caboose) mixed, solid triangle mixed. Milwaukee main line: * daily, dagger ex Sunday, section
Sunday only, f flag, k Saturday only, sharp = flag stop; other conditional stops not modelled. Milwaukee Table 76: paragraph ex Monday,
section Sunday only, a Tue/Thu/Sat, c Mon/Wed/Fri, d Tue/Sat, f flag, k Saturday only, solid triangle motor, square mixed, sharp Friday
only. GN Table 5: * daily, dagger ex Sunday, f and mu flag stops. GN Table 46: * daily, dagger ex Sunday, section Sunday only, # via
Greyhound (not modelled). SP&S: double dagger ex Saturday, k Saturday only. Camas Prairie (in the NP pages): * daily, dagger ex Sunday,
section Sunday only, i Mon and Fri, # ex Sunday via connecting train, solid circle motor.
Checked against the transcriptions: they agree (Warden–Marcellus Fridays only; Goldendale ex Saturday; Camas Prairie 73/74 daily). Asked
Brendan: Camas Prairie 73/74 are entered as mixed (the "M" over Table 49 and UP's mixed signs); his NP-page key makes a solid circle a motor.

Version 44 (9 Oct, from Brendan's 11:49–11:59 notes): city stations by railway (wa_lines BY_RAIL / CITY_GID: Seattle King St. and Union,
Spokane GN / Union / NP, Tacoma Union and Milwaukee, Portland Union, one Vancouver station at the wye); joins at Dayton and Seattle Union
Station; Milwaukee into Seattle over the UP; PSN Bremerton, Edmonds–Port Ludlow and San Juan boats; UP Table 5 Oregon (wa_up_t005or.csv);
Camas Prairie as passenger trains; NP/GN/SP&S into Portland over the SP&S side; GN Portland sections as sps_gn in GN colours; far ends.
Version 45 (9 Oct, Brendan's 12:07 and 14:23–14:32 notes):
- Page: a stretch of track between two route points takes the owner at its middle (a long straight stretch, Auburn–Stuck Jct, was undrawn).
- SP&S Spokane–Pasco on its own line (by Lamont and Washtucna, pinned from the names file; Washtucna moved 760 m onto the line); join of
  660 m east of Pasco between the SP&S line and its piece over the NP's Snake River bridge.
- UP Table 53 on UP track only (graph 'up'): join of 776 m at Wallula; Attalia and Kennewick by mileage.
- Milwaukee Table 84 on Milwaukee track only (it had been routed over the NP west of Chehalis).
- NP Table 60 (422/423) by the Prairie Line: Lakeview from the names file (Pierce County), the 'Lakewood WA old alignment' kept (KEEP_OLD:
  the only track joining the Prairie Line pieces). Brendan: Lakeview and Fort Lewis are off the main line; trains to and from north of Tacoma
  back out of Tacoma Union Station. 422/423 removed from np_pool (Table 60 is their route). Pool trains pinned to Steilacoom.
- UP pool trains 457/458 as their own line up_pool (rail up): Seattle Union Station by the UP line through Kent, Auburn, Sumner, North
  Puyallup (the UP/Milwaukee stations), then NP and SP&S to Portland.
- Names: NP 1/2 The North Coast Limited, NP 3/4 The Alaskan (real_ends.NAMES).
- Spokane International into Spokane Union Station over UP track from the end of Brendan's trace (1.89 mi; printed miles now fit to the end).
  Stop gid WA_SPOKANE_UNION_STATION. si_build now reads the Washington KMZs (steps.json inputs).
- CP main line: Redcliff by mileage (noplace). Table 6 gives it a plain main-line row (mile 2070.2, Nos. 1 and 2 only); the town point was
  700 m off the line and the route went down a spur and back.
- tools/spurs.py lists stations a line reaches by going out and back (Version 45 list sent to Brendan to check: Grand Forks City, Colvalli,
  Nicola, Tofield, Red Deer, Rosedale (CN, CP), Luscar, Wetaskiwin, Stirling (2), Milk River, Winagami, Cheney (NP, UP), Kennewick (SP&S),
  Umatilla, Colfax, Tiflis; Sunnyside/Midvale are the table's own spur).
Version 46 (9 Oct, Brendan 14:46–14:53): Milwaukee Table 84 starts at Chehalis (no train Maytown–Chehalis). By the 1935 joint trackage
agreement its trains ran over the NP Chehalis Junction – Dryad (16.83 mi; traced 16.9) and on Milwaukee rails Dryad – Raymond; the
Milwaukee's own Chehalis – Dryad line was sold to loggers. wa_lines.TRIM cuts the traces 'Raymond WA to Ruth WA' at Dryad (keeps the
Raymond part) and 'Ruth WA to Maytown WA' at Chehalis (keeps Chehalis – Maytown). Dryad pinned from the names file.
Next update (Brendan, 9 Oct 15:09–15:12; do not build ahead of him): one joint UP/Milwaukee Marengo station at 47.025833, -118.188611
(47°01'33"N 118°11'19"W; where the UP's Spokane line, used by the Milwaukee by trackage rights, met the Milwaukee's freight main line):
shared gid for up_main, up_pen and milw_main (now UP by mileage 3.5 km off, MILW at the trace end). Also offered: one UP/Milwaukee Cheney
station (UP now on the NP's point, MILW 160 m off by mileage) - not yet confirmed.
Decided (Brendan, 9 Oct 15:37): keep SP&S Table 1 as printed - the GN Portland sections 1/2 and 3/4 are trains of their own (sps_gn, GN
colours); the NP's Portland service is connections at Pasco (columns 1-3, 5-5, 6-4, 4-2), not separate trains. No change needed.
Waiting: Alaska Steamship Company (Brendan: departures every 7 days on the Alaskan Route) is not in the build; needs its schedule.

## Alaska (packaged 9 October 2026, not built; Brendan's shape file to come; do not build ahead of him)
Files: ak_ass_1948.csv (Alaska Steamship, Southeastern and Southwestern Alaska Route, 9 sailings 1 May - 26 June, dates per port),
ak_ass_denali_1948.csv (Kodiak route, three-weekly: record only, below the weekly rule), ak_arr_seward.csv (Seward - Anchorage, Thu/Fri/Sat
north, Wed/Thu/Fri south), ak_arr_whittier.csv (Whittier - Portage - Anchorage, daily ex Sunday; Whittier has no mile printed: nan),
ak_arr_fairbanks.csv (Anchorage - Fairbanks, Mon/Wed/Fri north, Tue/Thu/Sat south), ak_arr_sutton.csv (Sutton branch, Dec 1947, daily ex
Sunday). Scans in scans/ak1948/. Railroad times are 150th meridian time (two hours earlier than Pacific).
Alaska Steamship: weekly from Seattle every Saturday 9.00 a.m.; Aleutian and Baranof alternate, each on a 14-day cycle (12-day round trip).
Ketchikan Monday, Juneau Tuesday north; Juneau Sunday, Ketchikan Monday south; Seattle back Thursday a.m. BUT Seward differs by ship:
Aleutian arrives and leaves (9.00 p.m.) Thursday and calls Valdez and Cordova southbound Friday; Baranof calls Cordova and Valdez northbound
Thursday and is at Seward Friday. Only Seattle (9.00 a.m. / a.m.) and Seward (a.m. / 9.00 p.m.) have times.
Alaska Railroad specials (printed rule): Seward - Anchorage leaves 1 h 30 min after a ship arrives, not before 9.00 a.m. (next day 9.00 a.m.
if the ship arrives after 4.00 p.m.); Anchorage - Seward special for sailings, time announced.
Decided (Brendan, 9 Oct 22:12): one week only, the Aleutian week (Brendan 22:18: Seattle Sat 9.00 a.m., Ketchikan Mon, Juneau Tue, Seward Thu a.m. - 9.00 p.m., Valdez and Cordova Fri, Juneau Sun, Ketchikan Mon, Seattle Thu a.m.; boat special Seward Thu 9.00 a.m. AK = 11.00 a.m. Pacific); times at
ports with dates only to be estimated; Seward arrival taken as before 7.30 a.m., so the boat special leaves Seward 9.00 a.m.; the regular
Anchorage 2.30 p.m. (Wed/Thu/Fri) stands for the southbound special; all times shown in Pacific time (railroad +2 h).
Track (Brendan, 9 Oct 22:16): traces/alaska/ntad_alaska.geojson (NTAD North American Rail Network, Alaska: SUBDIV Seward 111.2 mi
[printed 114.3], Anchorage 356.7 mi [printed 356.0], Whittier 12.5 mi, Palmer Branch 7.5 mi [printed Matanuska - Palmer 6.5]; yard names
give Seward, Portage, Whittier, Anchorage, Healy, Nenana, Fairbanks) and traces/alaska/sutton_branch.geojson (his Palmer - Sutton piece,
13.2 mi [printed 12.4], joins the Palmer Branch end within 98 m). Other stations by printed mileage.
Water (Brendan, 9 Oct 22:29): traces/alaska/simp_north_coast.gpkg (EPSG:3347, Statistics Canada hydro; 5 polygons, one of 13,474
points): the Gulf of Alaska, Prince William Sound and Cook Inlet, -153.8 to -133.6 W, 56.6 to 61.5 N (Juneau north to Seward, Valdez,
Cordova, Anchorage). The existing water layer already reaches Ketchikan, Wrangell and Juneau (to 58.5 N). To merge like water_alberta.json.
Projection (Brendan, 9 Oct 22:33, for the next update): replace the page's flat projection (P() in page_template.html: plain lon/lat
scaled at 49.12 N, 35-55% too wide at 60-65 N) with Lambert conformal conic, standard parallels 49 and 61 N, central meridian 128 W
(StatCan Lambert EPSG:3347 rejected: its central meridian 91.87 W tilts north 28-50 degrees here). Only P() changes; chains are in metres.
Check after: page speed (tools/perf.py), the view presets, tools/shots.py.
Washington water (Brendan, 10 Oct 07:57, for the next update): places/wa/wawater_simplified.geojson (EPSG:2927 Washington State Plane
South, US feet; one multipolygon of 229 parts, 29,688 points; -124.71 to -116.19 W, 45.44 to 49.0 N): Puget Sound, Grays Harbor, Willapa
Bay, the Columbia (Portland - The Dalles - Wallula - Pasco), the Snake, Lake Roosevelt, Lake Chelan, Lake Pend Oreille (Idaho). Puget Sound
is already in water_embedded.json: Brendan (10 Oct 07:58): the Washington Puget Sound is less crude, so it REPLACES the Canadian data's
Puget Sound (cut the existing sea south of the boundary where the Washington layer covers it; check the join in the Strait of Juan de Fuca,
Haro Strait and Boundary Bay for slivers or gaps).
Open (asked Brendan 9 Oct): how to show the two-ship alternation in one week; times at ports with dates only; the Seward arrival hour (sets
the special); the southbound special's time; Pacific-time shift of +2 h for the railroad; the Jonesville - Eska branch is freight only (Brendan, 9 Oct): out.

## Harbour Navigation Co., Indian Arm (packaged 10 October 2026, not built)
harbour_nav_1948.csv: Vancouver (Gore Ave. Dock) - Belcarra Park - Deep Cove - Woodlands - Sunshine - Brighton Beach - Thwaytes Landing -
Lake Buntzen - YMCA Camp Howdy / Camp Jubilee - Weldwood - Wigwam Inn (Brendan's order, "zig-zag"). End times his; landing times estimated
(see the file). Mon-Sat four trips, one boat, the M.V. Scenic; Sunday four direct trips, two boats (second unnamed). Places from the B.C. names file: Belcarra (Village),
Deep Cove (Cove), Woodlands (Community), Sunshine, Brighton Beach, Thwaytes, Lake Buntzen, Wigwam Inn (Landings). Placed by Brendan
(10 Oct): Gore Ave. Dock, Belcarra Park, Camp Jubilee, Weldwood (a guess). Note: Camp Jubilee lies just north of Brighton Beach and south
of Thwaytes, but comes after Lake Buntzen in his order (a 1.5 km double-back); the names-file landings are only to the nearest minute.

## Version 47 (10 October 2026)
- Lambert conformal conic projection in page_template.html (P = LCC: parallels 49 and 61 N, central meridian 128 W, origin Vancouver).
- Water: water_extra.py (by hand) -> water_bc_cut.json (B.C. water less Puget Sound south of a line down the Quimper Peninsula, across
  Admiralty Inlet and Deception Pass), water_wa.json, water_ak.json, water_extra.pkl (for sea.py). make_page.py merges them. sea.py: Deception
  Pass closed to the lanes (SHOALS); SEA_VERSION v5. Lanes past Port Townsend pinned near their earlier course (VIA for Vancouver - Seattle
  and Seattle - Port Angeles, Brendan: the earlier routing was more correct); they still differ by up to 2 km off Point Wilson.
- Anacortes moved to the Black Ball dock (Brendan): 48.521834, -122.614545.
- Harbour Navigation Co. (bia, livery hnc): harbour_nav_1948.csv; M.V. Scenic.
- North Vancouver ferry landings renamed North Vancouver and Vancouver (NV Ferries) (item 23 done).
- The Mountaineer (13/14) on the cpc line by Carseland (item 24 done; Brendan's best guess, in the note).
- Joint UP/Milwaukee Marengo (WA_MARENGO, Brendan's point); UP Cheney by mileage on the UP (noplace), not the NP's point.
- Alaska Railroad (ak_build step, kind k, colour --arr, Claude's pick): arr_sew (with the Thursday boat special, estimated), arr_whi,
  arr_fai, arr_sut; times +2 h to Pacific (spec tznote in ab_lines). Portage at the Whittier branch junction (the yard is a spur).
  Views 'alaska' and 'gulf'. Fairbanks and Anchorage stations are at the NTAD yards (modern yards; check).
- Alaska Steamship NOT built yet: needs points for Seattle (Pier 42), Juneau, Valdez, Cordova and the Seward dock (asked Brendan). Plan
  (the week of 1 May): Aleutian northbound Sat - Fri (Seward Thu, Valdez and Cordova Fri, the trip ending at Cordova in the week shown) and
  Baranof southbound from Seward Fri 9.00 p.m. AK (the week before) to Seattle Thu; day-only calls timed by distance inside their day.

- NEXT RELEASE (Brendan, 10 Oct 10:45): a false straight-edged "peninsula" across the mouth of Admiralty Inlet, from Point Wilson NE towards
  Whidbey Island (Fort Ebey / Fort Casey): a strip neither water layer covers, between the Canadian data's crude straight shore and the
  northern edge of the Washington Puget Sound. Fill it (water polygon over the inlet mouth, or move the cut line so the two layers overlap
  there), then redraw the lanes (bump SEA_VERSION) and recheck the Port Townsend routes against his Google Maps screenshot (ferry tracks
  run mid-channel between Point Wilson and Admiralty Head).

- NEXT UPDATE (Brendan, 10 Oct 11:58): Harbour Navigation landings, new points and two new calls (Cosy Cove, Granite Falls), in this order:
  Vancouver (Gore Ave. Dock) 49.286388, -123.098232; Belcarra Park 49.313079, -122.928610; Deep Cove 49.326839, -122.946972;
  Cosy Cove 49.327492, -122.919253 (new); Woodlands 49.341831, -122.920781; Sunshine 49.345002, -122.914303;
  Brighton Beach 49.359206, -122.898353; Thwaytes 49.376517, -122.889626; Lake Buntzen 49.375285, -122.869705;
  Camp Jubilee 49.371407, -122.889325; Granite Falls 49.451241, -122.862392 (new); Weldwood 49.463031, -122.877844;
  Wigwam Inn 49.461915, -122.885979. Re-estimate the landing times in harbour_nav_1948.csv (two more calls in the same 2 hours) and
  update the ports in boats_build.py (P, PLACED).
  ORDER (Brendan 11:59: his list was not from a timetable; use a logical order): up the arm, Vancouver - Belcarra Park - Deep Cove -
  Cosy Cove - Woodlands - Sunshine - Brighton Beach - Camp Jubilee - Thwaytes - Lake Buntzen - Granite Falls - Weldwood - Wigwam Inn
  (west shore up to Thwaytes, one crossing to Buntzen and the east shore, the head last); down the arm the reverse.

- NEXT UPDATE (Brendan, 10 Oct 16:01; all estimates): Alaska Steamship ports: Seattle (Pier 42) 47.593257, -122.338091; Juneau
  58.297738, -134.405623; Valdez 61.124347, -146.361554; Cordova 60.548018, -145.768406; Seward (steamer dock) 60.115842, -149.434532.
  With these the Alaska Steamship sailings can be built (the plan is under Version 47 above).

- SASKATCHEWAN (Brendan, 10 Oct 18:25): 19 CP timetable scans filed in scans/cp1948_sk/ (README lists them: Table 5 main line to Broadview,
  Tables 98, 103-123, 125-131, 133-137). Not transcribed; scope of a Saskatchewan expansion not yet decided (track: the 2015 NRWN Saskatchewan
  file from the other chat; no Saskatchewan names file yet). Do not start without Brendan.
  Decided (Brendan, 10 Oct 18:29): scope Saskatchewan only (Manitoba is too big); trains running through into Manitoba are included, shown
  in Saskatchewan and ending at their last timed Saskatchewan station with their real far ends (as Alberta at the boundary). CN pages are
  coming. Track: NRWN Saskatchewan as the base, backfilled with 1948 lines from traces where it lacks them (as before). Brendan will add a
  Saskatchewan names file. Still waiting for: the CN pages, the names file, the NRWN Saskatchewan file in this workspace (prepared in the
  other chat: sk_tracks_slim.geojson, sk_stations.geojson, or the original nrwn_rfn_sk_kml_en_1.kmz).
  Received (10 Oct): places/cgn_sk/cgn_sk_csv_eng.csv (Saskatchewan names file); nrwn/nrwn_rfn_sk_kml_en_1.kmz (NRWN Saskatchewan).
  Transcribed (10 Oct, one worker, about 0.33M tokens; guide scans/TRANSCRIBE_SK.md): 51 files sk_cp_t*.csv with prov (SK/MB/AB) and tz (C/M)
  columns (ab_table.py now accepts them). A train printed in two tables is entered only in its own table. Doubts for Brendan: unexplained
  signs (Table 5 z, n, nn; 92 c; 130 dot and triangle; the key for 129-137 cut off); 130 M466 days not printed (Fri guessed); 116f Debden and
  Tobey miles not printed (58.0, 60.0 estimated); Table 6 '58 346' column read as 346; provinces unprinted (Lloydminster SK?; Table 128 Epping
  SK?, Rivercourse, McLaughlin, Paradise Valley AB?); 108 No. 315 Yellow Grass - Ibsen 5 mi in 4 min (misprint?); Table 116 vs 92 differ at
  Colonsay (301 1.50p vs 51 1.35p) and Table 117 vs 92 at Macklin (M481/M480). Not built: waiting for the CN pages.
  Brendan (10 Oct 20:03): Table 5 signs not modelled (plain times); Table 92 c = stops on signal (applied); Table 130 black dot = operates the
  second Friday of each month (shown as operating), black triangle = operates the Saturday following (M463, M466 set to Sat; M464 Mon,Wed);
  Table 6 "58 346" = two motor trains 58 and 346 (58 set to motor). Lloydminster sits on the boundary (a bi-provincial town): CHECK where the
  CN Lloydminster station was placed in the earlier Alberta build. Macklin agrees once read together: M481 ar 12.05 (117) / lv 12.30 (92);
  M480 ar 2.00 (92) / lv 2.50 (117). Colonsay: 51 and 301 are different trains, 15 minutes apart. Debden/Tobey estimates and No. 315's
  Yellow Grass - Ibsen time stay as they are.
  MANITOBA (Brendan): build the trains we have schedules and track for at least as far as Winnipeg. Table 5 extended Winnipeg - Brandon -
  Broadview (1, 3, 7, 53 / 2, 4, 8, 54). Tables 5 and 92 differ at Portage la Prairie by 5-10 min for 51/52/105/106 (kept in 92 only).
  Needed: Manitoba track (NRWN Manitoba) and a Manitoba names file. Tables 104 and 105 (all Manitoba) not transcribed.
  Received (10 Oct 20:15): nrwn/nrwn_rfn_mb_kml_en_1.kmz (NRWN Manitoba). Backfill for lines gone since 1948 (Brendan): the Canadian Northern
  and Grand Trunk Pacific sets (traces/cnor_all.geojson, traces/gtp_all.geojson, via backup_track.py) and traces/hr_rails (crude). The CP
  lines abandoned since 1948 have no backup set: list them for Brendan when the routing shows gaps. Still to come: Manitoba names file, CN pages.
  Brendan (10 Oct 20:19): Manitoba stations by printed mileage for now (no names file). Winnipeg Union Station (CN, GN, NP) 49.889092,
  -97.133408; Winnipeg CP station 49.904986, -97.131634.
  CN Saskatchewan pages (Brendan, 10 Oct 20:28): 17 scans in scans/cn1948_sk/ (Official Guide, April 25, 1948). Transcribed by one worker
  (guide scans/TRANSCRIBE_SK_CN.md; it hit the session limit at the very end, but every table was written): 39 files sk_cn_t*.csv, all
  passing ab_table.py (170's flag at Reserve is the M.T./C.T. change). Skipped: 161, 163, 183, 184, 189, 195 (Manitoba/Ontario/Minnesota
  only), 193, 216 (Alberta, done). Doubts (worker's PROGRESS.md, scratchpad/skcn): unexplained day signs g (173 M305, 175/176 M316),
  v (160 M295/M296, 165 M262: placeholder Wed), psi (176 Gravelbourg), dot (212 M380, 214 M336: placeholders); conflicting signs (174 e,
  201 h/k, 207 M259, 214 M275 y, 229 M332 k/h, M331 n/#, 232 M271 y, M272 k/h, 226 M287 y). Table 225 split in four sections (26 legs).
  Alberta check (Brendan 20:30): trains in the Saskatchewan tables that reach Alberta and are NOT on the map: CP Table 128 Lloydminster -
  Paradise Valley (M447/M448: Rivercourse, McLaughlin, Paradise Valley are in Alberta) and CP Table 133 Fox Valley - Schuler - Empress
  (M671/M672: left out earlier because it crosses the boundary four times). Both to be built with Saskatchewan.
  ALSO MISSING (Saskatchewan parts of CN tables already scanned in scans/og1948_cn, transcribed only for Alberta): Table 75 (Winnipeg -
  Saskatoon - Artland), 168 (Winnipeg - Kamsack - Saskatoon - Kindersley - Alsask), 171 (Winnipeg - Regina - Saskatoon - North Battleford -
  Marshall), 211 (Biggar - Loverna), 230 (Biggar - Unity - Cosine). Transcribe these before the build (same guide).
  Key for CN Tables 171-179C (Brendan, 12 Oct): * daily; dagger ex Sun; double dagger ex Sat; paragraph ex Mon; section Sun only;
  a MWF; b TuThSa; e Fri only; f flag; g Tue only; k Sat only; n Mon only; o Thu only; p Wed and Fri; t ex Tue; x Thu and Sat; y ex Wed;
  z Wed only (Brendan: the second "x" was z). Applied to 173b (M305 Tue, M306 Mon), 174 (M303, M389 Fri),
  175 (M316 Tue, M329 Wed,Fri, M315 Mon, M330 x -> Thu,Sat), 176 (M316 Tue, M315 Mon). The 193-201 and 180-184 keys differ from it.
  More keys (Brendan, 12 Oct 21:31): Tables 152-165 v = Tue only; Tables 203-215 black dot = Wed only; Table 176 psi = arrives 6.00 p.m.
  (Gravelbourg); Tables 192-201 h = Thu only, k = Sat only; Tables 203-216 and 224-233 y = Tue and Thu; Table 229 M331 n = Tue and Fri;
  Table 207 M259 sharp = Thu and Sat (Table 190's e the same). Applied to 160, 165 M262, 176, 201, 207, 212, 214, 226, 229a, 232.
  Then (21:35): 152-165 x = Mon only (165 M261 Mon); 224-233 h = Wed and Sat (229 M332, 232 M272 are h: Wed,Sat); 190 d = Tue only.
  All CN day signs settled.
  CN 75, 168, 171, 211, 230 Saskatchewan/Manitoba parts transcribed (12 Oct, one worker, about 0.24M tokens): sk_cn_t075 (Winnipeg -
  Chauvin; 1-4 left to sk_cn_t166, their intermediate times in comments; 11 and 12 split at Saskatoon by day signs), sk_cn_t168 (63, M251,
  9, 10, 64, M252; 15/16 left to 180), sk_cn_t171 (5 and 6 in full; 7/8 left to 172), sk_cn_t211 (M257 Mon Wed Thu Fri?, M258, M267, M268),
  sk_cn_t230 (M311 Fri, M312 Sat). Each ends at the first Alberta station, overlapping the ab_ files by one. BUILD NOTE: Nos. 5/6 Regina -
  Saskatoon are in both sk_cn_t171 and sk_cn_t172 (columns 5-59 / 60-6): build 5/6 from 171 and only 59/60 (Saskatoon - Prince Albert) from
  172. Doubts: 168 Runnymede mile 205.2 or 265.2 (265.2 entered), No. 64 McCreary 9.26 smudged, No. 63 Dauphin sign, Dana 451.1;
  171 Brada small square (No. 6); 211 M257 days (":" sign) against M258 Tue Thu Sat; u read as Fri (211, 230); 230 Unity 57.9 vs 56.9.
- NEXT UPDATE (Brendan, 12 Oct 21:46): Titlow is missing from the pool trains. NP Table 4 (the source of np_pool) does not print it; GN
  Table 46 and UP Table 5 give No. 401 a flag stop at Titlow 4.38 a.m. (GN mile 137, UP 135.0; between Steilacoom and Tacoma on the Point
  Defiance line). Add Titlow to wa_np_t004.csv (mile about 50 from Seattle by NP's count; check) with No. 401 f4.38a, and any other pool
  train GN 46 / UP 5 show stopping there; place it from the Washington names file.
- (Brendan, 12 Oct 23:01-23:08) CP No. 2's Calgary layover (in 12.35 p.m., out 7.00 next morning) is real: the timetable prints it in two
  places. Keep the split ('2E'). Its note already says it lies over at Calgary.

- Barkley Sound Transportation Co. (Brendan, 13 Oct 19:57): barkley_sound_1948_estimated.txt (Uchuck I Mon/Wed/Fri Port Alberni - Bamfield
  calls; Uchuck II Tue/Thu/Sat Port Alberni - Sechart - Broken Group - Ucluelet; 8.00 a.m. day round trips; estimated). Needs Sechart and a
  Broken Group point (both now received, 20:15; loop route agreed, see the file). Uchuck II confirmed for the 1948 season (Brendan). Mail boats; Sunday excursion 10.00 a.m. to Bamfield (Uchuck I,
  direct, back about 6.30 p.m.; model).

## Known gaps and open questions

- **Northern Alberta Railways**: Edmonton–Dawson Creek, Nos. 1 and 2, all on real track now (Brendan's traces for Watino and for the Alberta
  boundary to the Dawson Creek yard; traced Rycroft–Dawson Creek 138.8 mi against 138.2 printed). The Barrhead branch trains in the same table
  are not entered. NAR colour (dark blue) is Claude's pick. The old main line east of Rycroft and the Spirit River spur survive in the Alberta
  file as 'Spur' track, which is why the extract keeps spurs north of Edmonton. NAR and CN share the CN station (gid `CN_EDMONTON`) and the
  first 5 miles of track, drawn by the cn line.
- **CN to Edmonton**: Nos. 1 to 4 and the local trains 189 and 190, from the Guide's condensed table (only the stations it prints, east of
  Jasper). 189 runs Sun., Tue., Thu. and 190 Mon., Wed., Fri., by the Guide's own key to its signs (written out in `cn_1948_alberta.csv`),
  which also confirms the days of every CN mixed train on the main line.
- Alberta: see the Alberta section above for what is estimated, left out or waiting on Brendan.
- Lethbridge station sits where the present main line passes the old station site (about 400 m off).

- No water or coastline is drawn in Alaska, the Yukon, Idaho or eastern Washington (the water layer is B.C., Puget Sound and Alberta), so the
  White Pass line and the S.I. south of the border sit on plain paper.
- WP&Y in Alaska uses the coarse old NTAD shape: traced 18.8 mi against 20.4 printed, so the curves above Skagway are cut short.
- S.I. trace ends 1.9 miles short of the printed mileage at Spokane (east of the downtown station). Elsewhere traced and printed miles agree
  to within half a mile; stations are fixed at the border and at Corbin and Coeur d'Alene Junctions (where Brendan's branch traces leave).
- Chelohsin (Union Route 5): Phillips Arm, Fraser Bay and Allison Harbour are fortnightly calls and Bones Bay is by arrangement, but all are
  shown every week (to change: see the fix list, one week's version only). The guide lists Kingcome Inlet "via Simoom Sound", which may mean a connection rather than a call; it is drawn as a call
  at Brendan's coordinates. Southbound she is due at Vancouver Thursday p.m. (an earlier build had Friday a.m., a misreading).
- CP coast steamers that the tables do not name per sailing (Triangle Route, night boats, Nanaimo) still read "Steamer".
- GN south of Bellingham: printed whole miles, scaled to King Street Station. The Oriental Limited (Everett–Seattle only in Table 90) is not shown.
- Union Steamships: Thursday Rivers Inlet and Saturday Alaska sailings need their route pages; North Shore ferries are for the future.
- Possible future: BCER streetcars (zoom-dependent, headway-based); terrain hillshade.
- Brendan plans to share the map on Bluesky and host it on GitHub Pages (`site/index.html` is the same page).
- NEXT UPDATE (Brendan, 13 Oct 21:01): the North Vancouver ferry's straight line looks wrong; give it a modest curve. It is in BY_HAND
  (boats_build.py, straight across). Replace the straight lane with a gentle arc, either through a VIA waypoint a little off the
  midpoint or by a bowed curve, drawn the same way in both directions. Shape (Brendan, 21:04): leaving Vancouver (foot of Columbia)
  the boat heads due north a short distance, then bows round towards Lonsdale; the reverse trip follows the same path.
- NEW STEAMER (Brendan, 14 Oct 10:13; not built): SS Alaska (subsidiary of the Alaska Steamship Co.), Official Guide. Leaves Seattle
  Thursdays 1 and 15 July (every second Thursday) 9.00 a.m. (est); calls Ketchikan, Wrangell, Petersburg, Juneau, Haines, Skagway, Sitka.
  In the 5-11 July week it is the 1 July sailing, mid-voyage. Have points: Seattle Pier 42, Ketchikan, Wrangell, Juneau, Haines, Skagway.
  Need: Petersburg, Sitka points; the return route (Sitka direct to Seattle?); port times (estimate from Aleutian pace if none printed).
  (Brendan, 10:15) Other sources: the round trip is symmetrical for stops. Proposed estimate: Skagway the turning point; south via Haines,
  Juneau, Sitka (once, the Peril Strait side trip), Petersburg, Wrangell, Ketchikan, Seattle. Dates: Ketchikan Sat 3, Wrangell/Petersburg
  Sun 4, Juneau Mon 5, Haines/Skagway Tue 6, Haines/Juneau Wed 7, Sitka Thu 8, Petersburg/Wrangell Fri 9, Ketchikan Sat 10, Seattle arr Mon 12.
  (Brendan, 10:17) Points: Petersburg 56.812853,-132.964131; Sitka 57.051239,-135.344842 (added to cp_t172_173_ports.csv). All points in hand.
- UNION STEAMSHIPS, more of Sailing Guide No. 138 (Brendan, 14 Oct 16:12; scans/union1948/: northern_cruises.png, route4_header.png,
  route4_table.png; from ferriesbc.proboards.com). Not built.
  * Route 4, Queen Charlotte Islands Route, S.S. Coquitlam, every ten days (Thursdays or Mondays alternately), DST. Vancouver (Union Pier or
    Pier H) 9.00 p.m. June 3, 14, 24; July 5, 15, 26; Aug 5, 16, 26. IN THE WEEK: the Mon 5 July sailing: Alert Bay Tue 6, Pacofi and
    Cumshewa Inlet Camps Wed 7, Sandspit / Skidegate / Queen Charlotte City Thu 8, Masset Fri 9, Prince Rupert arr Fri 9; leaves Prince Rupert
    Sat 10 July 11.00 p.m.: Masset / Queen Charlotte City / Skidegate / Sandspit Sun 11, Cumshewa Mon 12, Alert Bay Tue 13, Vancouver Wed 14.
    Port Clements: alternate sailings only; the 5 July northbound and 10 July southbound only connect via Skidegate (no call that week).
    Pacofi southbound by arrangement only. Only Vancouver 9.00 p.m. and Prince Rupert 11.00 p.m. are printed; other hours estimated.
    Points: names file has Sandspit, Skidegate, Queen Charlotte (P.O.), Masset, Port Clements; Pacofi only as Pacofi Bay and Cumshewa only
    as the inlet (Brendan may give better points).
  * Northern Cruises page: Cruise 1 = Route 4; Cruise 2 Prince Rupert/Stewart Fri 9 p.m. = Route 1 (built); Cruise 3 Prince Rupert/Skeena
    Tue 9 p.m. = Route 2 (built); Cruise 4 Rivers Inlet / Bella Coola Thu 6.00 p.m. DST from 24 June, back the following Tue p.m. (5 days):
    weekly, NOT BUILT, needs its route page; S.S. Chilcotin Special DeLuxe Cruise to Alaska and the Gardner Canal, six days, Sat 9.00 p.m.
    PST from 12 June: weekly, NOT BUILT, needs its ports.
    (14 Oct 16:33) Cruise 4 is not the Catala: the same guide (No. 138) has her on Route 2, Tuesdays 9 p.m. to the following Monday, with
    no change noted from 24 June; a Thursday 6 p.m. sailing would find her up north. So a second boat; its route page would name it.
- NEXT UPDATE / FIX (Brendan, 14 Oct 17:44): NP main line east of Seattle (Stampede Pass line, Green River) follows a ~13 mi diversion
  around Howard A. Hanson Reservoir, built after 1948 (the dam came later). The 1948 line ran up the Green River valley floor, now under
  the reservoir. Needs the old alignment (Brendan's trace if he has one, else an estimate along the valley); the diversion also makes
  traced miles longer than printed there.
  (17:45-17:46) Correction (Brendan): the replaced stretch, near Eagle Gorge, is ~13 mi long in total; it is not 13 mi of extra track.
  The 1948 line is in the Mississippi Rails KMZ: placemark "old alignment" (12.4 mi, -121.9236,47.3241 to -121.7226,47.2399; Eagle Gorge
  ~-121.751,47.258), plus two short "old alignment" pieces nearby (1.1 and 0.3 mi near -121.90,47.31-47.33). wa_tracks.in_1948 drops every
  line named "old"; wa_lines KEEP_OLD already lets the Lakewood one back in. FIX: add the Eagle Gorge old alignment to KEEP_OLD (and check
  the two short pieces) and TRIM the relocated line between its ends (Veazey-Eagle Gorge and the west end of Eagle Gorge-Stampede Pass).
  Same rule may hide two other 1948 lines (to put to Brendan): "old alignment" in the St Paul Minneapolis & Manitoba folder, 16.4 mi,
  -120.61,47.58 to -120.74,47.73 (GN Wenatchee-Entiat, which wa_gn_t045 uses: likely the Rocky Reach Dam relocation); "Riaria old
  alignment", Camas Prairie, 3.4 mi near Riparia (wa_cprr_t049 uses Riparia: likely a Snake River dam relocation). The Washington-folder
  pieces near Kettle Falls (9.8 and 6.0 mi) are probably the Grand Coulee relocation, done before 1948, so they stay out.
- OSM SASKATCHEWAN (Brendan, 14 Oct 21:46): traces/osm/osm_sk_abandoned_export.geojson, OpenStreetMap export of railways tagged
  abandoned / disused / razed. 1,828 lines, ~5,980 km (abandoned 5,111, disused 764, razed 105). Box -110.68..-100.68, 48.96..53.88:
  Saskatchewan only (no Manitoba, nothing north of ~53.9). 241 pieces are sidings/spurs/yards (service tag): drop those. Few names
  (~160 named). Use: a third backfill source under NRWN, with the CNoR/GTP traces, for the lines lifted since 1948. OSM data (c)
  OpenStreetMap contributors, ODbL: credit it on the page.
- NEXT UPDATE FIX (Brendan, 14 Oct 22:37): Alaska Railroad trains missing from the "On the line" panel. Cause: renderList's kind loop
  (page_template.html ~line 810) lists 'c b l n g q p i r y a o d u m v' but not 'k'; add 'k' to the loop, to the 'yaodum' no-heading
  test and to the train unit list (KIND_LABEL needs k: 'Alaska Railroad' if absent).
  (Brendan, 15 Oct 08:34) Pacofi 52.831131,-131.881414, by Pacofi Creek: mark "est" (added to cp_t172_173_ports.csv). Cumshewa Inlet
  Camps still the names-file inlet point unless he sends one.
  (Brendan, 08:36) "Cumshewa Inlet Camps" (plural) = two calls: Aero (Aero Steamer Landing, north side of Gillatt Arm) 53.050833,-131.961389
  and Moresby Camp (head of Gillatt Arm) 53.049444,-132.035. Order: Pacofi, Aero, Moresby Camp, then Sandspit (reverse southbound); both
  on the guide's Cumshewa date, labelled as the Cumshewa Inlet Camps in the notes.
  (Brendan, 15 Oct 08:55) Chilcotin Alaska cruise: too speculative to estimate; left out until his archival work turns up the route.
  (Claude's reckoning, for reference only: six days with the Gardner Canal side trip reaches about Ketchikan, Wrangell at most.)
- CN READING DOUBTS SETTLED (Brendan, 15 Oct 09:06): 168 Runnymede 265.2, McCreary No. 64 9.26 a.m., Dauphin No. 63 sign is a smudge, Dana
  451.1 (all as entered); 171 Brada No. 6 = stops on signal Sun, Mon, Fri, Sat only (now f8.58a, days in the note); 211 M257 Mon Wed Thu
  Fri, u = Friday only (as entered); 230 Unity 57.9 on that page, u = Friday only (as entered).
- RULE (Brendan, 15 Oct 10:26): flag stops made only on certain days are shown as ordinary flag stops every day; the days go in the train's
  note. Fine by him.
- NEXT UPDATE (Brendan, 15 Oct 14:17): Seattle area ownership. Tacoma Milwaukee station - Black River Junction (approx 47.476302,
  -122.251934): continuous track, owned by the Milwaukee (drawn as MILW though UP trains use it). North of Black River Jct into Seattle
  Union Station: owned by UP. Check the line is unbroken between Tacoma MILW station and Black River, and that the owner switch falls at
  the junction (TRACK runs take the owner from each stretch's midpoint: may need splitting the stretch at the junction).
- (Brendan, 15 Oct 14:18) "a spot south of Seattle routes everything over NP; there should be parallel UP and NP tracks". Checked the V47
  shapes: trains already follow their own lines (UP pool and MILW on the UP/MILW Tacoma-Renton-Seattle line, NP/GN pool on NP via Stuck
  Jct and Black River; distance 0.0 km to own line in both stretches). Between Black River and Seattle the two lines are only ~50 m apart,
  so the likely fault is the drawn track (one line drawn, one owner colour) rather than routing. Asked Brendan to point at the spot.
- NEXT UPDATE (Brendan, 15 Oct 15:52): Walla Walla stations. traces/washington/walla_walla_stations.geojson. NP station at the end of the
  NP spur (end point -118.344050, 46.072774; spur from the NP KMZ, leaves at -118.342223, 46.070794). UP station at the end of Brendan's wye
  track (-118.356601,46.062310 ... -118.353720,46.061069): the station is the end away from the UP line; check which end joins it at build.
  Two stations (NP and UP), like Seattle and Spokane: add to wa_lines BY_RAIL/CITY_GID; add the wye to the UP track.
- NEXT UPDATE FIX (Brendan, 15 Oct 15:56): Turner. UP Table 60 prints Turner (mile 50) with no times: the trains end at Dayton. The build
  still forces the line on to Turner (wa_build up_060 force=[('Dayton','Turner')], a straight 8-mi estimate) and draws Turner as a principal
  station. Fix: drop the Dayton-Turner leg, the Turner station and "– Turner" from the route name.
- (Brendan, 15 Oct 16:01) Riparia: the re-routes near Riparia come from a dam built in 1961, so the 1948 line is the KMZ's "Riaria old
  alignment" (Camas Prairie, 3.4 mi): ADD to KEEP_OLD and trim the newer line between its ends (next update). Entiat: keep in the notes
  only; Brendan has nothing on it yet, so no change (GN Wenatchee-Entiat stays on the present alignment for now).
- NEXT UPDATE FIX (Brendan, 15 Oct 16:42): GN Portland sections (wa_build sps_gn, rail 'gnw', SP&S Table 1) do not show in the SP&S
  station boxes between Vancouver WA and Pasco. Cause: gid_for() takes the stop id from the spec's rail, so these trains got their own
  GN_* stops (GN_CAMAS, GN_STEVENSON, GN_LYLE, GN_WISHRAM, GN_PASCO, GN_KENNEWICK ...) sitting on the SPS_* ones. Fix: give sps_gn the
  SP&S stop ids (EXT_GID[('gnw', name)] = SPS_* for every Table 1 station, or a spec option stops='sps'); check no GN_* stops remain on
  the SP&S and that Spokane/Portland still resolve to the city stations.
- NEXT UPDATE (Brendan, 15 Oct 16:48): Portland approach. From 1946 the UP Portland-Seattle pool trains (up_pool, Nos. 457/458) ran over the
  SP&S/NP north-side route into Portland Union Station, not UP's own access; other UP trains (e.g. from the east, Table 5b) keep UP's route.
  V47 check: UP_POOL runs over UP's line via the North Portland point and east (lon to -122.668); NP_POOL goes the north-side way (west to
  -122.752) but passes 0.8 km from Brendan's North Portland point. North Portland station, one for all roads: 45.606192, -122.711997
  (printed in wa_np_t004, wa_gn_t046, wa_sps_t001, wa_up_t005b). Fix: route up_pool like np_pool south of Vancouver WA; one shared North
  Portland stop gid at that point; make sure the north-side route actually passes it (else check which track the NP pool takes there).
  (16:50) Brendan: the North Portland point is approximate: do NOT move tracks; snap the station to the north-side route nearest that point.
- NEXT UPDATE FIX (Brendan, 15 Oct 17:15): Attalia / Villard (Willard) Junction tangle. McNary Dam (Lake Wallula) relocations were finished
  about 1954, so 1948 = the original lines. The KMZ has old and new both passing the date filter (undated pieces pass): NP "Attalia original
  route" (8.6 mi, undated, KEEP) vs NP "Pasco to Zanger Jct WA" (18.2 mi, undated: probably includes the relocated stretch past Attalia:
  trim it where the original route replaces it); UP "Attalia WA to Villard Jct original route" (7.2 mi, 1905, KEEP) vs UP "Villard Jct
  new" (0.8 mi, undated: DROP). SP&S pieces built 1954/1957 are already out; those abandoned 1954/1958 are already in. Check the routed
  trains (NP Pasco-Wallula-Walla Walla, UP Wallula-Pasco-Spokane, SP&S near Pasco) use the original lines afterwards.
  (Brendan, 15 Oct 20:13) The parallel-track spot is from just south of Black River Junction to Seattle Union Station: draw the NP and the
  UP/MILW lines side by side there (they are ~50 m apart and currently draw as one). Combine with the MILW/UP ownership split at Black River.
- BUILD PLAN (Brendan, 20:13): two passes, each checked and published: (1) Washington fixes, new steamers, page fixes; (2) Saskatchewan and
  Manitoba. Back up Version 47 first; re-upload STATE.md to the project at the end.

## Version 48 (15 October 2026, pass 1 of the big update; published)
- Backup of Version 47: /home/claude/bcer_v47_backup_20261016_0412.tar.gz (whole bcer folder).
- Washington: Eagle Gorge (Hanson Dam), Riparia (1961 dam) and Attalia/Villard (McNary) put back on the 1948 lines (wa_lines KEEP_OLD,
  KEEP_OLD_AT, DROP, CUTS; cut pieces renamed '... [cut]'). Turner gone (up_060 ends at Dayton). Titlow f4.38a for No. 401 (wa_np_t004, mile
  49.9). GN Portland sections use the SP&S stop ids (EXT_GID). UP pool trains into Portland by the north side (graph 'upn+np+sps': UP track
  north of 46.5 N only). North Portland one station WA_NORTH_PORTLAND (HAND, on the SP&S track nearest Brendan's point). Walla Walla: NP
  station at the end of its spur, UP at the end of Brendan's wye (traces/washington/walla_walla_stations.geojson, BY_RAIL WW_NP/WW_UP).
  UP/MILW joint line owners: MILW Tacoma - Black River, UP Black River - Seattle Union (wa_lines _owner, feature 'own'). Parallel lines of
  different Washington railways are no longer merged when within 20 m (ab_lines OWN_APART; drawn track remembers its owner).
- Steamers (boats_build.py, block "the summer-1948 week additions"): Alaska Steamship (bas: Aleutian, Baranof; bad: Denali; bsa: S.S. Alaska),
  CP 172 (bca: Princess Louise/Norah), CP 173 (bcw: Princess Maquinna), CN 315 (bcg: Prince George), Union Route 4 (bu4: Coquitlam), BYN
  (byk: Klondike/Casca; bym: Keno; byt: Tutshi), Barkley Sound (bsb loop: Uchuck I/II; bse: Sunday excursion). Dated sailings carry 'd0'
  (day from Mon 5 July; page shows only their days in the week, no wrap; check_vessels handles them). Liveries byn, bst (Claude's picks).
  Masset lane routed round Rose Spit (VIA). Indian Arm landings revised (harbour_nav_1948.csv; all landing times estimated). North Vancouver
  ferry bowed (quadratic curve, VIA). ARR boat special moved to Friday (the Baranof).
- Water: water_extra.py adds water_north.json (Yukon + northern B.C., Carcross narrows join) and water_fill.json (Admiralty Inlet strip
  along the cut line); both in water_extra.pkl for the lanes. Kodiak stays off the water (lane crosses land there).
- Page: title "The Digital Model Railway"; sub line with "approximately the week of 5 July 1948"; BCER multi-year note; ARR in On the line
  and its source line; carry-over up to 6 days (8 for dated); new sources and credits in the footer. steps.json: wpy_build before boats_build.
- Checks: check_gtfs 0 problems; check_vessels 0 overlaps; ab.py vs V47: only the intended lines moved; tools/.baseline_viz.json = V48.

## Version 49 (15-16 October 2026, pass 2: Saskatchewan and Manitoba; published)
- New step sk_build (sk_build.py, helper sk_lines.py), after ak_build: one line per sk_c[np]_t*.csv file (84 lines), rails 'skcn'/'skcp'
  (kind q/p, owner cn/cp, prefix CN/CP), graphs 'sk:cn'/'sk:cp': NRWN Saskatchewan + Manitoba (nrwn/sk_all.json, mb_all.json from
  nrwn/extract_prov.py) + the Alberta file near the boundary; the other big railway's track left out, short lines open to both; backups CNoR
  and GTP (CN only) and the OSM abandoned/disused/razed set (both; sidings, spurs and yards dropped).
- Places: Winnipeg hand points (CN Union Station, CP station); stations already on the map at the Alberta boundary (their gids, so lines
  join); NRWN station names; the Saskatchewan names file (nearest the track; aliases Tichfield Junction, White Bear, Val Marie); the Alberta
  names file for the first Alberta station (and Acadia Valley). Manitoba: NRWN stations for principal stations only, the rest by mileage.
- Times: per-row zones (ab_lines spec 'tzrows'; TZ_SHIFT C -2 h, M -1 h; a 'C/M' row takes the zone of the station the train comes from for
  its arrival and of the next station for its departure). Checked: CN 5/6 at Lloydminster, CN 1 at Wainwright, CP 1 at Walsh meet the
  Alberta trips to the minute.
- Derived file sk_cn_t166w.csv: CN Nos. 1-4 Winnipeg - Saskatoon - Wainwright (Wainwright times from the CN main line trips), in place of
  Table 166's Winnipeg - Saskatoon - Edmonton. sk_cn_t172: Nos. 7/8 whole; 5-59 and 60-6 only Saskatoon - Prince Albert (skcn172s).
- PENDING (sk_build PENDING; need end points from Brendan): CN 165 and 174 (North Regina), 182a (Swan River), 190 (Neepawa), 192b (Flin Flon),
  192c (Cranberry Portage, Sherridon); CP 92b (Binscarth, Russell), 98b (Elm Creek, Gretna), 103 (Reston), 106c (Lauder, Deloraine),
  106d (Deloraine, Lyleton), 106e (Lauder).
- Straight-line estimates: 58 stretches, about 1,300 printed miles; the longest: CN Saskatoon - Melfort 118 (Table 170), Reserve - Crooked River
  60, Saskatoon - Laird 50 (Table 160), CP Welwyn - Stockholm 49 (107), CN Medstead - Turtleford 47, CP Chitek - Meadow Lake 44, Rosemound -
  North Battleford 43 (130), Gunnworth - Kyle 39, Medstead - Panton 37, Glenbush - Prinham 32, and CN Davin - Regina 23 (the Regina point).
  Saskatoon: the network station and the names file's point do not fit the 1948 track (the CN line through the city was moved): wants hand
  points for the CN and CP Saskatoon stations, and Regina Union Station.
- Speed warnings: CP 340 Pasqua - Belle Plaine 11.7 mi in 10 min (Table 6; check the reading); CP 315 Yellow Grass - Ibsen (as printed).
- Page: views Saskatchewan, Regina/Moose Jaw/Saskatoon, Winnipeg to Saskatchewan; SK/MB sources and the OSM credit in the footer.
- Checks: check_gtfs 0 problems; ab.py vs V48: nothing moved, only the new lines. tools/.baseline_viz.json = V49.

## Version 50 (15 October 2026, Brendan's 22:30 list; published)
- ROOT CAUSE of stray colours (UP bits on the NP, GN bits on the SP&S): make_graph dropped the 'own' of an edge when it split it to tie a
  loose point, so those pieces fell back to the line's own colour. Fixed (own kept). Also ab_lines fills gaps under 1.5 km between stretches of
  other track on Washington lines.
- Washington graphs: 'gn@spk' / 'up@spk' (that railway's track only inside Spokane, SPK_BOX): sps_main and sps_gn 'sps+np+gn@spk',
  milw_main 'milw+up@spk', milw_tac 'milw' (into the Milwaukee station by its own line and bridge, Tacoma - Morton). 'up~' = UP track at a
  higher cost: np_058 'np+up~' (NP Pasco - Ainsworth - Attalia on its own original line; UP only Attalia - Eureka, where the NP set has none).
  Features named '... rts on Northern Pacific' are drawn as NP track (Pasco - Ainsworth Jct).
- Ketchikan: lanes north by Tongass Narrows (VIA _KTN for Wrangell, Juneau, Taku Glacier, Kodiak; a water strip TONGASS in water_fill).
- Saskatchewan: CP Tables 5 and 6 one line (skcp005, Winnipeg - Walsh; Broadview zone C/M where they join); Table 108 Soo-Dominion 13/14
  dropped (until June 29), the Mountaineer kept; Table 122 Friday only (after May 15); Table 133 one line Fox Valley - Pivot - Schuler - Pivot -
  Hilda - Empress (with the Schuler - Hilda leg of ab_cp_t133.csv). Through trains: real_ends gives an SK piece that runs on into (or from)
  a train already on the map at the boundary the real ends of the whole run (CP 1 Montreal - Vancouver, CN 5 Winnipeg - Edmonton), and its
  name; ab_lines passes the #train from/to through (spec 'realends').
- Open with Brendan: the CN Lloydminster station (now -110.0335, 53.2811, 2 km west of the town; looks wrong to him); the projection's
  central meridian (proposal below).

## Version 51 (15 October 2026, 23:05; published)
- Through trains as one train: real_ends links an SK/MB piece and the train it meets at the Alberta boundary ('next' / 'prev' trip ids). The
  page shows the pieces in one timetable (the other pieces' calls greyed or plain, no miles), "On this map" from the first piece's origin to
  the last piece's end (CP No. 1: Winnipeg - Vancouver), and the selection (and Follow) moves on to the next piece when one arrives.
- CP Nos. 3 and 4 now reach Medicine Hat from Saskatchewan (derived file skx_cp_t006_medhat.csv: Walsh - Medicine Hat, times of the main-line
  trips there; Table 6 gives them no time at Walsh), so they meet the main-line trips. CN No. 4 (and 1-3) were already linked at Wainwright.

- (15 Oct 23:35, not yet built) Regina Union Station point from Brendan (50.452737, -104.608727) in sk_lines HAND for CN and CP. Davin - Regina straight:
  the 1948 CN approach from the east into the city was lifted in the Regina relocation (after 1948, Brendan); not in NRWN, not in the CNoR backup
  file (only the QLL&S line there), OSM only fragments. Wants a trace (or route to the end of today's track + short straight).

- (16 Oct 08:40, not yet built) Saskatoon hand points in sk_lines HAND: CN station 52.127597, -106.666647; CP station 52.132486, -106.671011. Brendan: CN
  main-line trains (the Continental) looped through the CN station on the old tracks through the middle of town and out by the CN tracks west of
  downtown back to the main line. The CNoR backup file has track within 70 m of the CN station (QLL&S) and 0.5 km (CNoR); check the loop at build.

- (16 Oct 08:49, not yet built) North Regina (old station, approx.) 50.469514, -104.655567 in HAND; CN 165 and 174 out of PENDING. Table 174 split: skcn174
  North Regina - Riverhurst (M303/M304; dry trace all on track, 118.4 mi vs 112.9 printed) and skcn174d Central Butte - Dunblane (derived
  skx_cn_t174_dunblane.csv, M389/M390; no track in any source: 33 mi straight). skcn165: Mawer - Main Centre 46 mi straight (no track; the
  line was run by the Construction Department in 1948).

- (16 Oct 12:47, not yet built) Brendan's Regina SE link trace: traces/saskatchewan/regina_se_link.geojson (all traces in that folder feed both SK graphs at
  cost 1.0; trace ends joined to the railway's Main within 1.5 km). CN may use CP track in the REGINA box (Union Station). Davin - Regina now on
  track. Hand points: North Battleford (shared, both railways) 52.7716, -108.2985; Lloydminster CN 53.284654, -110.005968 and CP 53.285637,
  -110.003357 (in sk_lines HAND and ab_lines HAND). Dry trace: 53 straight stretches, about 1,070 mi (was 58, about 1,300). Remaining are lifted
  branches; CP into North Battleford (130a, 130b, 131) has no CP track within 37 km; Battleford - North Battleford printed 13.9 mi for 2 mi apart.

- (16 Oct 14:04) Dalmeny - Laird: the CNoR Carlton Branch was in the backups but tied only to the OSM piece lying on it, never to the network.
  make_graph(tie_each=True) for the SK graphs: a backup point ties to the nearest edge of every other line within reach. Dalmeny - Laird and
  Oban - Cando now on track; dry trace 51 straight stretches, about 1,024 mi. Not yet built.

- (16 Oct 14:41) Joint CN/CP Rosemound - Battleford - North Battleford - Medstead (Brendan): sk_lines JOINT, CP may use CN track in the
  BATTLEFORDS box (-108.95..-108.0, 52.65..53.35) as CN in REGINA. Now on track: CP 130b North Battleford - Scentgrass, CP 131 North
  Battleford - Scentgrass. Still straight: Rosemound - Battleford ~27 mi (no track west of the end of track), Battleford - North Battleford
  (printed 13.9 mi, 2.5 mi apart: route unknown). Not yet built.

- (16 Oct 14:47) Battlefords (Brendan): CP uses the CN (CNoR backup) track Rosemound - Battleford; North Battleford trains reverse out of
  Battleford, go north over the bridge to the junction on the main line west of North Battleford (HAND battleford junction -108.3652, 52.8320)
  and come back east: via (Battleford, Battleford Junction, 7.9) on sk_cp_t130a and sk_cn_t212 (sk_build passes via). CP graph takes the CNoR/GTP
  backup pieces inside its JOINT boxes. Both now all on track; dry trace 47 straight, about 968 mi. Not yet built.

- (16 Oct 15:06) CP Table 132 Saskatchewan part was never entered (the Alberta files left 65/66 and M673/M674 to Saskatchewan): transcribed
  sk_cp_t132.csv (Nos. 65/66 Swift Current - Empress ex Sun; M673/M674 Swift Current - Pennant Tue) from the scan; dry trace all on track. Not built.

- (16 Oct 15:08) Boundary check: every Alberta table that prints Saskatchewan stations has its Saskatchewan file (132 was the only gap). Notes
  checked for trains NOT entered: all covered elsewhere, except CP Dominion 5/6 (Table 5 note: leave the main line at Portage for Table 92, but
  sk_cp_t092a has no 5/6; Table 94 not transcribed) - asked Brendan. CP Tables 94 and 99 (Manitoba) referenced, not transcribed.

- (16 Oct 21:17) Humboldt (Brendan): CP had trackage rights over the CN line through town and used the CN station. HUMBOLDT box in sk_lines JOINT
  for CP; HAND humboldt (both) 52.1975487, -105.1251600. CP 116b Bay Trail - Humboldt now on track (Fulda - Pilger 5.4 mi still straight). Not built.

- (16 Oct 22:51) Brendan's Sask_Parts.gpkg -> traces/saskatchewan/sask_parts_brendan.geojson (34 OSM disused/abandoned pieces, all in -108.45..-107.73,
  53.75..54.15: the Meadow Lake area). Traces now fed as loose (src b, cost 1.0). Fir Mountain (cp) 49.385992, -106.553414. Kelvington (cn) on the CNoR
  line -103.50627, 52.15953 (CN and CP side by side through town). Now on track: Chitek - Meadow Lake (116f, 131), Wood Mountain - Glentworth (125b),
  Lintlaw - Kelvington (182). Dry trace 42 straight, about 848 mi. Not built.

## Version 54 (16 Oct 2026, 23:xx)
- Sask_Parts_2.gpkg -> traces/saskatchewan/sask_parts_brendan_2.geojson (75 pieces, whole lines and connectors). All of 16 Oct's Saskatchewan work built:
  Regina (Union Station, SE link, CN over CP tracks), North Regina lines 165/174/174d, Saskatoon CN/CP, Battlefords joint + reversal, Humboldt joint,
  Lloydminster CN/CP (also Alberta), North Battleford, Kelvington, Fir Mountain, Dalmeny - Laird (tie_each), Table 132 Swift Current - Empress.
  Straight estimates left: 17, about 285 mi (Welwyn - Stockholm 49, Weyburn - Radville 25, Lloydminster - Hillmond 25, Birch Lake - Panton 24,
  Hardy - Bengough 21, Griffin - Weyburn 19, Fortune - Anglia 16, Glen Payne 15, Baird - Leinan 12, Dysart - Cupar 8, and short ones).

## Version 55 (16 Oct 2026, ~23:45)
- Regina: CP-operated track in the REGINA joint box carries own=cp in the CN graph, so the CP main through the city draws as CP (CN lines on it
  show CP colour). Battlefords/Humboldt CN track in the CP graph carries own=cn.
- Routing fallbacks (Brendan: find how his pieces link): the other railway's NRWN track outside joint boxes at cost x2.5 (no owner: lines changed
  hands since 1948), OSM service-tagged pieces at 1.6. Weyburn - Radville CP-labelled track counts as CN (CN_AS_OWN box; Brendan: mislabelled/sold).
- Saskatoon loop (Brendan's map): via (Saskatoon, Saskatoon loop, 3.0) on sk_cn_t075 and sk_cn_t166w; HAND saskatoon loop -106.672, 52.155:
  north from the station and round the west of the city to the yards.
- Straight left: 7 (Dysart - Cupar 7.7, Southall - Oungre 5.4, into Glen Payne 13.3, Rosetown - Anglia 7.8, three end-of-track bits under 1.1).

- (17 Oct 08:44, not built) CP Brandon station (Brendan) 49.849933, -99.951447 in HAND. CN Brandon: CNoR station on a lost downtown spur at the Prince Edward Hotel; trace coming from Brendan.

- (17 Oct 09:18, not built) CN Melville (Brendan) 50.926003, -102.807478. Melfort: Brendan pasted the Melville figures for it; asked again. Melfort has close
  parallel CN and CP alignments through the town centre; CP station at the same spot on its own line.

## Version 56 (17 Oct 2026, ~09:50)
- CN Brandon on Brendan's downtown spur trace (traces/saskatchewan/brandon_cn_spur.geojson; station at the Prince Edward Hotel, -99.950383, 49.846275).
  CP Brandon 49.849933, -99.951447; CN Melville 50.926003, -102.807478; Melfort CN and CP 52.859442, -104.611536.
- ab_lines fit(): for sk: graphs, when the cheapest route does not fit the printed miles, the shortest-by-distance route is tried. CN 171 Winnipeg -
  Brandon now fits (was 150 vs 135); CN 170 Saskatoon - Melfort 118.4 vs 118.3 printed.
- CP Rosetown by mileage on 117a and 113 (noplace; the point is the CN townsite station). Brendan double-checking. 117a all on track.
- Straight left: 6 (Dysart - Cupar, Southall - Oungre, Glen Payne, three end-of-track bits).

## Version 57 (17 Oct 2026)
- Brandon spur looked wrong: the trace-end joiner (_near_main, up to 1.5 km to the railway's main) drew a fake diagonal from the station end of the spur
  to the CN main. The joiner now runs only for traces flagged join_ends (the Regina SE link). Traces otherwise join only by the 60 m loose ties.

## TO DO: joint-station review (Brendan, 17 Oct 2026 12:43; review of 11:08, nothing changed yet)
Stations of different railways within 250 m (70 pairs; script: same check over viz_data.json stations by gid). Proposed:
1. Agreed shared, still two stops (merge to one gid): Regina (Union Station), North Battleford, Battleford, Humboldt (CN station, CP used it).
2. CN and CP on the same point because both took the names-file / network point (Brendan to say joint or separate, with points for separate ones):
   SK Prince Albert, Tisdale, Melfort (his point, 16 m), Medstead, Glenbush, Oban, Watson, Biggar, Dodsland, Young, Conquest, Nokomis, Yorkton,
   Wartime, Balcarres, Moose Jaw, Griffin, Weyburn, Carlyle, Estevan; MB Gladstone, Portage la Prairie; AB Drumheller (35 m), Willow Creek, East Coulee,
   Dorothy, Trefoil. (Medstead/Glenbush in the Battleford joint corridor and the Drumheller valley joint line may really be shared.)
3. Washington, NP-UP joint line Tacoma - Portland (merge): Steilacoom, East Olympia (53 m), Tenino, Bucoda, Centralia, Chehalis (+ Milwaukee: 3-way),
   Napavine, Winlock, Vader, Castle Rock, Ostrander, Kelso-Longview, Kalama, Woodland, Ridgefield, Felida. Likely shared too: Kent, Sumner,
   North Puyallup (41 m) (UP/MILW); Pasco, Kennewick (NP/SP&S); Ayer (UP/CPRR). Probably separate: Auburn (129 m), Easton (131 m), Cheney (162 m).
4. Leave as two: Seattle King Street / Union Station (52 m), New Westminster BCER / CP (67 m), the Vancouver and Victoria docks, Marpole - New Westminster stops.
5. Mistakes: Union Mill and Lacey (NP) on the same point; Mount Robson / Emperor 215 m apart (check).
- NEXT UPDATE (Brendan, 17 Oct 14:39): Portage la Prairie separate stations, now in sk_lines HAND (not built): CN 49.977393, -98.288247;
  CP 49.978187, -98.285903. CP on its own corridor through town: dry trace CP 5 / 92 Winnipeg - Portage - Brandon all on CP track; CP 92
  Portage - Gladstone still 0.3 mi on CN-labelled track (check at build). Takes Portage out of the joint-station review (group 2).
- NEXT UPDATE: joint-station review answers (Brendan, 17 Oct 20:18). Do groups 1 (merge Regina, North Battleford, Battleford, Humboldt),
  3 (merge the Washington NP-UP joint-line stations + Kent, Sumner, North Puyallup, Pasco, Kennewick, Ayer) and 4 (leave: Seattle, New Westminster,
  docks, all BCER stops are right). Union Mill is WEST of Lacey (fix the NP point). Emperor / Mount Robson are on different tracks: leave.
  Points already staged in sk_lines HAND (not built): Battleford (CN; both) 52.735633, -108.315475; Prince Albert union station (CN and CP: MERGE)
  53.198852, -105.752418; Biggar CN 52.0533, -107.9869; Yorkton CN 51.212301, -102.467137 / CP 51.209872, -102.463366 (approx.); Moose Jaw CN
  50.3944, -105.5262 / CP 50.3889, -105.5349; Estevan CP 49.1424, -102.9932, CN at the west end of traces/saskatchewan/estevan_cn.geojson
  (approx.; may extend further into town); Portage (above).
  Merge as one station: Melfort (adjacent, treat as one), Medstead, Glenbush; Alberta Drumheller valley (shared corridor, the CN station):
  Drumheller, Willow Creek, East Coulee, Dorothy, Trefoil.
  Check by printed mileposts (place each railway's station by its mileage, see whether they fall together): Tisdale (CP said to be west of the
  commercial centre), Oban (likely separate), Watson (separate), Dodsland, Young (separate), Conquest, Nokomis, Balcarres, Griffin (possibly
  shared), Weyburn (unlikely shared), Carlyle, Gladstone (possibly shared). Biggar CP: separate from the CN point. Wartime: CN station near the
  stop; the CP station probably out of town.
  Weyburn: the CN line diverting into the CP station is likely wrong (from earlier unclear instructions): check the Weyburn - Radville
  CN_AS_OWN box and the CN Weyburn routing.
- NEXT UPDATE (Brendan, 17 Oct 20:22): projection central meridian 128 W -> 122.5 W (page_template.html, Lambert conformal conic; keep standard
  parallels 49 and 61 N). Balances the lean at Fairbanks and Winnipeg (~20 deg each); Lower Mainland and Puget Sound upright. Check the views (fit
  boxes) and any hard-coded screen offsets after the change.
- Prairie water (17 Oct): Brendan's saskman_water.gpkg deleted at his request (mostly potholes). Wanted later, from a new source: only the North and
  South Saskatchewan rivers (and the main stem), Lake Winnipeg and Lake Manitoba.
- OPEN QUESTION to Brendan (17 Oct 20:39): restructure for a Canada-wide map (page + per-region data files loaded on demand, compact encoding,
  tiled basemap): as the next big item, or after the smaller fixes are published.
- (17 Oct 21:15) CN Nos. 1-4 rebuilt with Table 75 calls (sk_cn_t166w.csv; Brendan: they had lost their intermediate stops). Signs: e (Lazare) stops
  for revenue passengers to/from Winnipeg and beyond; z (Nokomis) stops on signal (entered f). Not built: Brendan will send more before the launch.
- NEXT UPDATE (Brendan, 17 Oct 21:24): prairie water, simplified: places/sk_water/saskman3.gpkg (layer saskman2__simplified, 1,006 polygons, ~47k
  points, EPSG:3347). Replaces the deleted file. Add via water_extra.py as water_sk.json (like water_north.json) and load in make_page.py.
- (17 Oct 21:35, not built) Southall - Oungre (CP 110b): 1.6 km gap between the end of the OSM old line (49.1884, -103.7312) and the CP main at
  Southall: replaced the fudge with Brendan's NRWN Bromhead subdivision YARD segments (traces/saskatchewan/southall_bromhead_yard.geojson;
  nrwn extract leaves out yard track, which is why it was missing). Table 110b all on track.
- (17 Oct 22:00, not built; Brendan) Traces: dysart_cupar_link.geojson (Dysart - Cupar now on track), glen_payne.geojson (two pieces, Malmgren -
  Rosetown - Glen Payne side). Yard track: nrwn/extract_prov.py <kml> <prov> yards -> nrwn/sk_yards.json, mb_yards.json, fed at cost 1.6 as
  last-resort connectors: the Table 120 stub gone. Still straight: Glen Payne - Stockdill - Gunnworth 13.3 mi (no track; Stockdill unplaced),
  Baljennie 0.7 mi (112), one 1.1 mi stub on 133a.
  CP Table 139 Saskatchewan stations added to skx_cp_t139_kerrobert.csv (Onward 8.6, Superb 15.1, Major 22.6, Fusilier 30.5; Brendan's reading).
  CP No. 340 Pasqua lv 6.40 - Belle Plaine ar 6.50, miles 1799.6 - 1789.4 (10.2 mi in 10 min): confirmed as printed (the 11.7 was the traced length).
  Rosetown CP: some sources put the station at the north end of town by the CP through tracks; kept by mileage for now.
  Wartime: CN by mileage = the hamlet point (40 m); CP by mileage 2.2 km NE (out of town, as Brendan expected): sk_cp_t117c noplace Wartime.
  Union Mill: Table 60 prints Union Mill then Lacey, both mile 68, going away from Tacoma: Union Mill is EAST of Lacey. Move it ~1 km east
  along the NP (wa_lines; next update). Estevan CN: leave as is.
  ORDER (Brendan): smaller fixes first, the restructure after.
- (17 Oct 23:00, not built; Brendan) Manitoba end points in sk_lines HAND; PENDING emptied. Dry traces: CN 182a Swan River, 190 Neepawa, 192b Flin
  Flon, 192c Cranberry Portage - Sherridon all on track. CP Manitoba branches straight (no CP abandoned-track source for Manitoba; the OSM export
  is Saskatchewan only): 92b Binscarth - Russell 11 mi; 98b Elm Creek - Gretna (printed 63.1); 103 Reston - Maryfield, Bender - Neelby, Peebles -
  Wolseley; 106c Lauder - Deloraine (printed 57, by Boissevain); 106d Deloraine - Lyleton; 106e Lauder - Fertile. Wants a Manitoba OSM export.
  Baljennie and Schuler at the ends of track (mileage agrees: Sonningdale - end 15.12 by track vs 15.1 printed; Pivot - end 6.22 vs 6.0):
  sk_lines HAND, and ab_lines HAND for Schuler (the Alberta line too). Union Mill -122.775020, 47.032424 and Lacey -122.810213, 47.036738 in wa_lines HAND.
  Glen Payne - Gunnworth: OSM has it (13.6 mi by track vs 13.1 printed); the straight is on the Malmgren side: track from Malmgren ends at
  51.6486 N, 107.9146 W, 4.2 km short of the north end of Brendan's Glen Payne trace (51.6180 N, 107.9493 W). Asked Brendan.
  CN Nos. 1-4: Table 75 notes A-D not needed (Brendan).
- (17 Oct 23:18, not built) Malmgren trace added to glen_payne.geojson (+ the Rosetown connector): CP 113 Perdue - Gunnworth all on track (63.8 vs 62.9).
  Manitoba OSM abandoned export -> traces/osm/osm_mb_abandoned_export.geojson (1,193 ways; sk_lines._osm reads both; service='no' counts as plain).
  Now on track: CP 92b Binscarth - Russell, 106e Lauder - Alida. Still straight: 98b Elm Creek - Gretna (shortest track 105 mi vs 63 printed: a gap
  on the direct line), 103 Reston - Maryfield / Bender - Neelby / Peebles - Wolseley, 106c Lauder - Deloraine (printed 57 by Boissevain; shortest
  28.5: needs the intermediate stations placed), 106d Deloraine - Lyleton. Root issue: Manitoba intermediate stations are unplaced (no names
  file; only principal NRWN stations), so routes can't be steered. Asked Brendan for the federal names file for Manitoba (as cgn_sk).
- (17 Oct 23:32) Squamish Dock station (Brendan): 49.684525, -123.164319. It is 1.3 km SW of the present dock station (the start of the PGE trace,
  49.694717, -123.155131) and about 1 km off the drawn track; 3.8 km from the Squamish station anchor, against 1.0 mi printed Dock - Squamish.
  Needs a trace from the end of the track to the dock (or a check of the Squamish anchor). Boats (bu8, bu8a) use the same dock point.

## Version 58 (17 Oct 2026, ~23:55; published)
- merge_stations.py (applied at assembly before real_ends): joint stations as one stop (gid) on the page and in GTFS: Regina, North Battleford,
  Battleford, Humboldt, Prince Albert, Melfort, Medstead, Glenbush; Drumheller valley (Drumheller, Willow Creek, East Coulee, Dorothy, Trefoil);
  Washington NP-UP joint line Steilacoom - Felida (Chehalis 3-way with MILW), Kent, Sumner, North Puyallup, Pasco, Kennewick, Ayer.
- Separate stations at their by-mileage positions (sk_lines HAND): CP Tisdale, Oban, Watson, Dodsland, Young, Conquest, Balcarres, Carlyle,
  Weyburn, Biggar (3 km NW of the CN); CN Nokomis; both Griffin and Gladstone. Brendan's points: Yorkton, Moose Jaw, Estevan, Biggar CN, Portage,
  Prince Albert, Battleford, Union Mill, Lacey, Manitoba end stations, Baljennie, Schuler (AB too). CP Wartime by mileage.
- CN_AS_OWN box east edge -103.88 (CN kept out of the Weyburn CP station).
- Projection central meridian 122.5 W. Prairie water (water_sk.json from saskman3.gpkg, 943 polygons, 0.42 MB).
- CN Nos. 1-4 with Table 75 stops; Table 139 stations; Southall yard, Glen Payne + Malmgren traces, Dysart - Cupar link; NRWN yard track and the
  Manitoba OSM export as connectors. Manitoba CN lines in; CP 92b, 106e in.
- Left: CP Manitoba 98b Elm Creek - Gretna, 103 (three gaps), 106c Lauder - Deloraine, 106d Deloraine - Lyleton (want the Manitoba names file);
  Squamish dock point (off the trace). Page 11.97 MB.
- NEXT UPDATE (Brendan, 17 Oct 23:43): PGE Squamish dock line, traces/pge_squamish_dock.geojson (dock station at its SW end, 49.683984, -123.164636).
  Put the PGE dock station there and start the PGE route on this trace (island_pge_build.py; ANCHORS/route); move the Union Steamships dock
  port (bu8, bu8a) to match; check Dock - Squamish against the printed 1.0 mi.
- NEXT UPDATE (Brendan, 18 Oct 10:10): CP Gretna branch trace, traces/saskatchewan/gretna_branch.geojson (cost 1.15 so the network track wins
  where both; trace features may now carry a 'cost'). Dry trace CP 98b Elm Creek - Gretna all on track, 61.5 vs 63.1 printed.
- NEXT UPDATE (Brendan, 18 Oct 10:18): CP Bender - Wolseley trace, traces/saskatchewan/bender_wolseley.geojson. Dry trace CP 103: Maryfield - Wolseley
  all on old-line/trace track (0.2 mi of CN-labelled track at Peebles); Fairlight by mileage. Still straight: Reston - Maryfield 28.5 mi.
- NEXT UPDATE (Brendan, 18 Oct 10:22): CP Maryfield - Reston trace (traces/saskatchewan/maryfield_reston.geojson): CP 103 Reston - Wolseley all on track.
- (18 Oct 10:23) CP 106d Deloraine - Lyleton: track was there; Lyleton point was 1 km off the end of the track (beyond the 600 m snap); moved onto it:
  all on track 36.7 vs 37.2. CP 106c Lauder - Deloraine: track exists by Boissevain (Lauder - Boissevain 38.1 by track vs 36.9 printed, Boissevain -
  Deloraine 20.8 vs 20.1) but Boissevain is unplaced, so the router takes the short way (28.5 vs 57). Needs a Boissevain point (asked Brendan).
- Lyleton (Brendan, 18 Oct 10:31): the OSM export stops at the wye outside town; the line ran on straight to 49.058625, -101.182417 (end of line):
  traces/saskatchewan/lyleton_end.geojson, Lyleton HAND there.
- Boissevain (Brendan, 18 Oct 10:35) 49.231058, -100.054508; trains back in and out from the west. CP 106c Lauder - Deloraine all on track 59.1 vs 57.0.
  All Saskatchewan/Manitoba straight estimates now cleared in the dry traces (next update).
- (18 Oct 18:05) Manitoba names file places/cgn_mb/cgn_mb_csv_eng.csv (Brendan); sk_lines _cgn reads it and Manitoba stations are now placed like
  Saskatchewan ones (no longer mileage-only). Dry traces: CN 190 only Rossburn Jct by mileage (was 14), CP 98a only Banting, CN 171 five.
  Next: complete Manitoba. CP Table 5 Fort William - Winnipeg not entered (scans have the whole table); Manitoba part Winnipeg - Ontario boundary.

## 19 Oct 2026: Manitoba CP tables
- sk_cp_t104 (Brandon - Lenore, M217/218 Tue/Fri) and sk_cp_t105 (Brandon - Miniota, M215/216 Tue/Fri, in and out of Rapid City from Gautier; Rapid City mile 35.3 is an estimate) entered; both dry-trace on track. Saved for the next build.
- sk_cp_t005e (Fort William - Winnipeg) entered, held in PENDING: needs Ontario track and names.
- Table 91 (Emerson - Winnipeg, Nos. 109/110) readings in hand, not yet entered.
- CREDIT for the next update: Paul Delamere, the Canadian Electric Railway Mapping Project and the Ontario Railway Map Collection (Brendan will use this work going forward). Add to the page credits.
- 18 Oct (later): Brendan's clearer scans saved in scans/cp1948_mb/. Entered: sk_cp_t096 (Winnipeg Beach - Gimli - Riverton, summer week), t097 (Winnipeg - East Selkirk - Molson - Great Falls),
  t099a (Winnipeg - Morris - La Riviere - Deloraine - Napinka, 121-124), t099c (Rosenfeld - Gretna M235/236), t099d (La Riviere - Windygates M249/250), t100 (Winnipeg - Arborg),
  t101 (Brandon - MacGregor - Portage via Varcoe), t102 (Brandon - Rapid City - Minnedosa). Table 92 MB rows replaced with all stations from Tables 93/94; 092b extended Binscarth - Russell - Inglis.
  t105 Rapid City now 35.8 (Table 102). sk_lines.canon folds accents (La Rivière). Table 93 adds nothing else (main line already in sk_cp_t005).
- Straight stretches for Brendan to trace: Russell - Inglis; Wood Bay - Purves and Snowflake - Mowbray (Windygates); Winnipeg - Birds Hill - Gonor, East Selkirk - Garson,
  St. Ouens - Molson - Lac du Bonnet - Great Falls (Table 97).
- Still to enter: Table 91 (Emerson - Winnipeg, 109/110), readings in hand.
- 18 Oct (evening): traces saved: russell_inglis, windygates_est (Brendan: speculative, hard to find), birdshill_beausejour. sk_cp_t097 noplace East Selkirk, Garson (names 1.6 km off trace).
  092b and 099d now all on track. Still straight: St. Ouens - Molson - Lac du Bonnet - Great Falls (Table 97).
- 18 Oct: molson_great_falls trace saved; sk_cp_t097 now all on track (84.6 mi drawn vs 80.3 printed). No straight stretches left in the new Manitoba CP tables.
- 18 Oct (late): NORTHERN PACIFIC added as a third prairie railway ('sknp', graph 'sk:np', pfx NP, colour as wa NP): sk_np_t014.csv (Table 14, May 18, 1947),
  Nos. 13/14 Manitoba Junction - Winnipeg, connections (No. 7/8 St. Paul, Duluth, Fargo) in notes. Track: traces/np/np_winnipeg.geojson (from Brendan's
  NP_Winnipeg.gpkg) + MB network track (0.55 km border connector at Emerson). NP_PROV keeps US names apart (Davidson MN). Dry trace all on track,
  267.6 mi drawn vs 256 printed (Manitoba Jct - Fertile 47.2 vs 44). Hand points: Manitoba Jct, Fertile, Crookston, Carthage Jct, Grand Forks (trace ends).
- GN Table 7 (Feb 8, 1948) scan saved scans/gn1948/gn_t007.png: Nos. 7/8 Winnipeg Limited St. Paul - Crookston - Noyes - Emerson - Winnipeg; 29/30 and
  131/132 US only. Asked Brendan where to start it. Emerson Jct - Winnipeg is the same (Midland Ry) line as NP: joint stations to merge.
- 18 Oct (later): GREAT NORTHERN added ('skgn', graph 'sk:gn', pfx GN, colour as wa GN). Track: traces/gn/gn_mn_nd.geojson cut from Brendan's
  Great_Northern.kmz (MN/ND, building outlines dropped; Elk River line cost 1.5 so Table 7 runs by Monticello). sk_gn_t007.csv (Feb 8, 1948: Nos. 7/8
  Winnipeg Limited, ST. PAUL - Winnipeg, Brendan: from St. Paul where it originates): all on track, 480.4 vs 457 printed. sk_gn_t009a.csv (307/308 Grand Forks -
  Gretna, No. 9/10 St. Paul in notes): on track to the border, last 0.5 mi into Gretna straight. GN Grand Forks point approximate (downtown) - ask.
  Hand points from named KMZ piece ends (St. Paul, Minneapolis, Alexandria, Fergus Falls, Barnesville, Warren). merge_stations: Winnipeg CN/NP/GN and
  NP/GN Emerson Jct - Morris - Portage Jct stations. Table 99 header confirmed (M235 Tue/Fri): GN 9a says the CP Gretna connection runs Mon/Thu - noted.
- 18 Oct: GN 7/8 rerouted Minneapolis - Elk River - St. Cloud (Brendan: crack trains ran by Elk River); Monticello line cost 1.5; Albertville/Monticello/Clearwater rows dropped. 483.2 mi drawn vs 457.
- 18 Oct: Grand Forks points from Brendan: NP 47.927156, -97.033178; GN 47.922247, -97.033647 (his '4 d 55' read as 47). Traces unchanged.
- 18 Oct (night): CN Manitoba tables from Brendan's Official Guide scans (scans/cn1948_mb/): entered t157 (Steep Rock spur in/out), t158, t159 (68/56/55; 32/31
  Saskatoon - Melfort stops added to t170), t161, t161a, t163, t167, t169, t183 (Hudson Bay Ry; M4 split at Wabowden, Mon-Wed layover), t184 (Somerset) +
  t184s (Sprague), t194, t195 (M229/230 only), t155w (M201/202 Winnipeg - Sprague). t155 (Port Arthur - Winnipeg, 33/34, M203-206) held in PENDING (Ontario +
  Minnesota CN line). Not entered: 156 (Ontario), 189 (Winnipeg - Fort Frances - Duluth, US), 162 (no times). Straight: Belleview - Virden (167),
  Ochre River - Rorketon (169). Doubts: M192 day sign (#, Mon/Thu), Cardinal mile 78.9 (15 min from Notre Dame de Lourdes 78.5).
- GWWD Railway added ('skww', own gwwd, colour #7a6a4f Claude's pick): sk_ww_t001 St. Boniface - Waugh, WINTER service entered (April), summer in notes. On track.
- Midland Railway of Manitoba: NP/GN track in MIDLAND box (border - Portage Jct, provisional) drawn as GN track (Brendan changed his mind: GN, not SP&S colour).
- 18 Oct (late night): GWWD switched to SUMMER (model week July 5: Brendan): down Tue/Thu/Sat 1.00p - 5.20p, up Mon/Wed/Fri 7.30a - 11.30a. Traces saved:
  ochre_river_rorketon (169 now on track), belleview_virden (+0.26 km join at Virden; 167 on track). MIDLAND (GN-drawn) box ends at Portage Junction 49.853;
  CN track into Union Station beyond. sk_cn_t189 (Fort Frances - Duluth, Nos. 20/19) transcribed, PENDING (Ontario/Minnesota track). Duluth in scope.
- 18 Oct (late night): SOO LINE: traces/soo/soo.kmz (Brendan) -> soo_mn_nd.geojson (Minneapolis - Glenwood - Ottertail - MP205 - Noyes; Minneapolis - Hankinson - Portal
  for the Mountaineer; Brendan's Soo Connector to the Milwaukee Road station) fed into the CP graph (drawn as CP). sk_cp_t091.csv (The Winnipeger 109/110,
  St. Paul - Winnipeg, scan cp1948_mb/t091.png): on track except St. Paul - Minneapolis (Milwaukee Road track: no trace yet, straight). 486.9 vs 464 printed.
  CP hand points: Minneapolis Milwaukee Road station (Brendan), St. Paul Union Station PROVISIONAL (= GN St Paul piece end), Glenwood, Thief River Falls, Noyes.
  Mountaineer US part: needs Soo timetable (St. Paul - Portal) - asked. Chicago (C&NW) extent - asked.
- 18 Oct (23:15): scans soo1947/soo_t002 (Table 2, Sept 7 1947), soo_t003 (Table 3, July 1947), cnw1948/t017*. sk_cp_t091 US stops now all from Soo Table 3.
  sk_cp_t108s.csv: the Mountaineer's Soo leg Minneapolis - Portal, times of Soo No. 3/4 (Sept table: summer Mountaineer times NOT in hand - eastbound doesn't
  connect: C&NW 404 lv Minneapolis 6.25a vs No. 4 ar 6.30a; North Portal 50 min off). On track 575 vs 551. sk_cnw_t017.csv (C&NW 403/404 Chicago - Minneapolis,
  Adams cut-off) PENDING: C&NW track + railway. place_for: US stations never match the map/names (Buffalo MN had matched Buffalo AB). Portal hand point (Soo piece end).
- 19 Oct: traces/milw/mpls_stpaul.geojson (Brendan): Milwaukee Road Minneapolis - St. Paul Union Station, drawn as owner milw (CP graph). St. Paul Union Station point = its end (cp and gn). 091 all on track 489.4. C&NW St. Paul - Chicago track still needed.
- 19 Oct: sk_cn_t200a via ('Regina','Regina Talmage wye',2.4): CN Talmage-line trains go north from Union Station round the wye west of North Regina (hand point -104.6435,50.4676, old GTP) and south across the CP main (no SE connector at the diamond: Brendan). Regina - Estlin now 19.2 drawn vs 18.8 printed (was 16.9).
- 19 Oct: kelowna_branch.kml Kelowna end replaced with Brendan's Kelowna Terminal Trace (station extant, 49.894133,-119.492851; trains enter from the east). Lumby Jct - Kelowna now 31.35 mi vs 31.3 printed (was 31.66). Old file kelowna_branch_v1.kml. Takes effect at next full build (nrwn_build -> mainline -> cps).
- 19 Oct: CN Table 172 columns 5-59 / 60-6: entered as Nos. 59 / 60 (Saskatoon - Prince Albert); 5 / 6 are Table 171 connections (Brendan).
- 19 Oct: SPLIT THROUGH TRAINS JOINED: sk_join.py (CHAINS: 29 joined trains, writes skj_<name>.csv, drops the columns from the section lines; sk_build
  SPECS = base + joined). Replaces the hand-made skx_cn_t192_65 (deleted). Left out: GN/CP 7-8 at Winnipeg, Mountaineer 13/14 at Moose Jaw (do with Soo leg),
  No. 61 Regina - Melville section (61/62 joined Winnipeg - Flin Flon). All joined trains on track.
- sk_lines: names-file matches now restricted to the station's province (Assiniboia SK had matched Assiniboia MB: Table 125 was 366 mi straight);
  ALIAS hudson bay jn -> hudson bay. Full dry run 137 lines: only straight left = skcp107b Kirkella - Welwyn 23.1 mi (pre-existing; the Tue/Sat 159/160
  by Kirkella - McAuley; McAuley unplaced: miles 83.6 entered vs 87.2 by Kirkella) and GN Gretna 0.5 mi.
- 19 Oct: traces/cnmn/cn_minnesota.geojson (Brendan): CN (DW&P) Duluth - Virginia - Cook - Ranier, Duluth terminal, Baudette - border (towards Middlebro). For sk_cn_t155 / t189 (still PENDING: Ontario track/names - Port Arthur - Rainy River, Fort Frances, and the two river crossings). Not yet fed to the CN graph.
- 19 Oct: sk_cn_t192d skipped: 61/62 Winnipeg section = through cars on CN No. 3 / No. 2 (Table 166, identical times; Brendan). skj_cn61 now Regina - Flin Flon (on track 439 vs 426).
- 19 Oct: C&NW RAILWAY ADDED ('skcnw', own cnw, pfx CNW, colour #5c6e1a olive, Claude's pick; graph sk:cnw = traces/cnw/cnw_mountaineer.geojson cut from
  Brendan's Chicago__Northwestern.kmz (Chicago - Kenosha - Racine - Milwaukee - Lake Shore Jct - Lindwerm - Adams cut-off - Necedah - Wyeville - Eau Claire -
  Hudson - Stillwater Jct - St. Paul; 3 short joins) + traces/milw). sk_cnw_t017 (403/404) out of PENDING; miles beyond Wyeville +12.5 (Table 17 prints
  Madison-route miles there); force St. Paul - Minneapolis (Milwaukee Road 12.3 vs 10.6). On track, 455.8 vs 419.2 (KMZ Chicago - Milwaukee 93 vs 85,
  Milwaukee - Wyeville 161 vs 154). Mountaineer still three lines (C&NW 403/404, Soo 108s, CP 108 + main line): through-join across railways not done.
- 19 Oct: C&NW points from Brendan: North Western Station Chicago 41.88269,-87.64029; Lake Front Depot Milwaukee 43.038944,-87.899722.
- 19 Oct: THE MOUNTAINEER ONE CP TRAIN (Brendan): sk_join chain cp13 (C&NW 403/404 + Soo 108s + CP 108 13M/14M + CP 005 legs 13/14), OPTS: drawn as CP
  (rail skcp108), notes give C&NW/Soo numbers. sk_join now handles multi-file lines (_pieces) and carries miles across files of one line. CP graph now
  includes traces/cnw (own cnw) and cp hand points Chicago/Milwaukee. skjcp13 Chicago - Medicine Hat on track, 1464 vs 1396. skcnw017 / skcp108s lines
  now empty (all their trains in the through train). KML of the C&NW routing sent: traces/cnw/mountaineer_cnw_routing.kml.
- 19 Oct: full local build OK (not published): 296 lines, page 12.9 MB. Mountaineer CP-13-SKJCP13 Chicago - Medicine Hat links next -> cpc CP-13 Medicine Hat - Vancouver (from Chicago, to Vancouver); 14 likewise. Removed NP/GN Cartier merge (GN 7/8 don't stop there).
- 19 Oct: ONTARIO (Paul Delamere's Ontario Railway Map Collection, Brendan's Lakehead_Routes.kmz, "first rank"): traces/ontario/lakehead_all.json (parsed);
  sk_lines: ontario() in ONT_BOX, owners by folder (ONT_OWN: Superior District / Kaministiquia / Keewatin = CP; O&RR, GTP, CGR, PAD&W = CN); fed to CN and CP
  graphs (main 1.0, sidings 1.6, other railway x2.5); ont_stations() for prov ON (first rank; ONT_ALIAS: CN Port Arthur = Prince Arthurs Landing, CP Port
  Arthur = Thunder Bay North - PROVISIONAL, asked). CN Minnesota traces in CN graph + Rainy River joins (Rainy River - Baudette; Duluth Jct - Ranier).
  PENDING emptied: sk_cp_t005e, sk_cn_t155, sk_cn_t189 now built; sk_cn_t156 (new, Port Arthur - Sioux Lookout). All on track.
- 19 Oct: lakehead_all.json re-parsed WITH descriptions; Ontario lines whose notes say abandoned before 1948 are skipped (found: GTP main line Westfort -
  Conmee, "abandoned after CN rationalization in 1924"; O&RR m7.5-10.9 removed 2000 = kept). Routes of 155/156 unchanged (did not use it).
  Local build: 300 lines, page 13.19 MB. TODO: no water for Lake Superior / Lake of the Woods / Rainy Lake / Lake Michigan (ask Brendan for a water file).
- 19 Oct: VERSION 59 PUBLISHED (300 lines, 13.19 MB). Brendan's Lakehead points: CN Port Arthur = Prince Arthur's Landing; CP Port Arthur 48.434547,-89.217683;
  CP Fort William = collection "Thunder Bay station" (timetable name kept); Dryden = collection point (HAND). CN Fort William = "Vickers Street branch line
  station": NOT in the collection - still the PAD&W "Fort William station" point (ask for coordinates). Page: Paul Delamere credited (CERMP + Ontario Railway
  Map Collection); sources sentence extended; new kinds x (C&NW) / j (GWWD) with legend/badges; views lakehead / midwest / chicago; fit() uses 4 corners.
  STILL TODO: water for Lake Superior / Lake of the Woods / Rainy Lake / Lake Michigan; attribution for the GN / Soo / C&NW / NP Midwest KMZs (ask).
- 19 Oct (after v59), FOR THE NEXT BUILD: CN Fort William point confirmed (Brendan). US track (GN/Soo/C&NW/NP KMZs) = Mississippi Rails (credit to add).
  Westside (CN 157/158) now HAND on the old St. James Street line (CNoR set; approximate, Portage Ave crossing): Grosse Isle trains leave Union Station south,
  west, then north up St. James St. (Brendan); 7.6 vs 6.9. GWWD St. Boniface terminal HAND (-97.0999, 49.8932). Missing (ask for scans): CN transcontinental
  Winnipeg - Sioux Lookout (Nos. 1-4 east of Winnipeg), CN Winnipeg - Beaconia - Pine Falls / Victoria Beach.
- 19 Oct: sk_ww_t001 now with the 16 intermediate stations of the GWWD 1974 timetable (scan cn1948_mb/gwwd_1974.jpg; Trans. Can. Hwy. omitted), times stretched evenly to the 1948 ends (down x1.33, up x1.23), miles scaled to 97.2. On track; Bruce and Sadlow by mileage (a Bruce elsewhere matched; Sadlow not in the names file).
- 20 Oct: CN Table 224 entered: sk_cn_t224 (Winnipeg - Beaconia - Grand Beach - Hillside Beach - Victoria Beach, 16 trains, days = those in the model week Mon July 5 - Sun July 11 1948; 67's natural sign read as Monday only - DOUBT) and sk_cn_t224p (M222/M221 Winnipeg - Pine Falls, ex Sun). ALIAS pine falls -> Powerview-Pine Falls. Both on track.

## 20 Oct 2026: CN Table 75 east of Winnipeg (not published)
- sk_cn_t075e.csv: Armstrong - Sioux Lookout - Redditt - Winnipeg, 16 trains (Nos. 1-4, M211-M216, 37/38, 551-554), days for July 5-11. Scans cn1948_mb/t075a.png, t075b.png.
- Dry trace on track, 412.5 traced vs 390.9 printed: a uniform ~5.5% excess, the UTM 10 scale error this far east (CP 005e shows the same). Ena by mileage.
- Nos. 1-4 link through Winnipeg to the 166W trips and on west (checked in a full build; page 13.30 MB).
- Not entered: Spl. Winnipeg-Redditt (Fridays in May/June/Sept only). Capreol-Armstrong: no track. Doubt: 552 sign read as z (Fri).

- Published as v60, 20 Oct 2026 ("Beaches, GWWD, Winnipeg-Armstrong").

## 20 Oct 2026: fixes (built, not published)
- CN Victoria Beach/Pine Falls: Pine Falls sub (Central Manitoba Rly in NRWN) treated as CN; birdshill_beausejour trace own=cp (x2.5 for CN). CN now leaves the main at -97.0647, 49.893 and crosses the CP Birds Hill line at the diamond; follows the modern dog-leg via -96.99 (Brendan to confirm).
- Names: CN 1-4 The Continental Limited (1/2 Montreal section, 3/4 Toronto section); CN 7/8 The Owl; CP 109/110 The Winnipeger; GN 1/2 Empire Builder, 3/4 Oriental Limited, 5/6 Cascadian, 7/8 Winnipeg Limited, 27/28 Fast Mail (St. Paul - Seattle).
- Published as v61, 20 Oct 2026 ("Train names, Victoria Beach routing").
- Next build: CN Holmfield - Deloraine trace (traces/saskatchewan/holmfield_deloraine.geojson, own cn; Brendan 20 Oct). skcn161a 95.3 traced / 95.9 printed.
- Next build: GN "St. Jean" entered as St. Jean Baptiste; CN/NP/GN St. Jean Baptiste and Ste. Agathe merged (merge_stations); CP Morris by mileage (on its own main line).
- Also merged CN with NP/GN at Morris, Letellier, Emerson Junction (Brendan, 20 Oct).
- Next build: Hudson Bay Jn. hand point by the wye (-102.39063, 52.86309; Brendan 20 Oct). Full dry trace: 141 on track, only the two known exceptions.
- Next build: CP Kirkella - McAuley trace (traces/saskatchewan/kirkella_mcauley.geojson, own cp). Still straight Manson - Welwyn 15.1 mi: McAuley point rejected (9.0 mi from Manson vs 5.1 printed); no track McAuley - Welwyn. Asked Brendan.
- Next build: GN Neche - Gretna over CP track (traces/gn/gn_neche_gretna.geojson own cp, extended straight 0.75 km north from the border to the CP station point; _us_graph honours own; GRETNA box draws CP); GN Gretna = CP station hand point; CP_GRETNA/GN_GRETNA merged. skgn009a 85.6/83.0 all on track.
- Next build: Noyes joint Soo/GN depot (-97.202881, 48.999178), CP_NOYES+GN_NOYES merged; CP Emerson depot hand point (-97.203364, 49.004692), separate; CN_EMERSON+GN_EMERSON merged (CN/GN station).
- Next build (20 Oct evening): CP Holmfield and CP Virden hand points; CN Holmfield, Hartney (t161a/t167) and CP Bienfait (t106b) by mileage; CN Virden hand point at the end of Brendan trace (approx.), the 0.26 km join to CP removed from belleview_virden. CP Carberry point withdrawn: 49 5 56 N lies ~85 km south of Carberry (broke skcp005); asked Brendan to re-check. Full dry: 140 on track + known 2.
- CP Carberry hand point corrected (-99.358826, 49.865718); skcp005 all on track. CN Virden stays at the trace end (Brendan OK). West Fort William stays two stations.
- S.S. Nenana (ARR river boat, Nenana - Marshall) estimated: nenana_1948_estimated.txt. Waiting for river course; question to Brendan on speeds and which week.
- Nenana: model week = sailing week, lv Nenana Tue 6 July (Brendan).
- S.S. Agulleit (NC Co., Marshall - St. Michael) estimate added to nenana_1948_estimated.txt; questions to Brendan on call order and distances.
- Tutshi: Brendan adds Tagish, Graham Inlet, Taku Landing (see tutshi_1948_estimated.txt); points / route questions to him.
- Tutshi milk run built into boats_build.py (next build): byt out Wed/Sun Carcross 12.30p - Tagish 2.15p - Rupert 7.20p - Taku Landing 8.45p - Ben-My-Chree 11.40p (125.8 mi lane); byr back Mon/Thu Ben-My-Chree 2.10a - Taku Landing 4.50a - Rupert 6.15a - Carcross 10.30a (105.1 mi, no Tagish). Estimated times.
- BRENDAN'S TO-DO (20 Oct): S.S. Keenora and M.S. Chicama II (Lake Winnipeg steamers) - schedules, ports, water.
- Keenora ad filed: keenora_1948_notes.txt (Mon noon Redwood Dock - Warrens Landing, 6-day cruise; Sunday Lockport excursions).
- Next build (21 Oct): CP Table 140 (sk_cp_t140.csv, M673/M674 Swift Current - Pennant - Wickett - Verlo, Tue; dropped from t132); Wickett - Fosterton 6.4 mi straight (no track; trace asked). CP Peebles hand point (-102.945918, 50.160378). CP 146-148 = NAR reprint; other gaps are unused numbers (Brendan). CN 162 Peebles - Handsworth: proposal sent.
- CN 162 entered (sk_cn_t162.csv), Tuesday freight with coach, GUESSED times (Brendan OK, noted in the train notes). No track: 21.8 mi straight; trace asked.
- Traces (21 Oct): traces/saskatchewan/verlo_gap.geojson (CP, from verlo_gap.gpkg) and peebles_handsworth.geojson (CN). skcp140 55.7/54.9 and skcn162 23.0/22.3, all on track.
- traffic_density.py -> traffic_density.gpkg (layer sections): trains/week per track section, per operator + track owner; rail only, trips wholly in the US left out. Built from the 22 Oct unpublished build. BCER Central Park / Burnaby Lake (pattern services) not counted.
- Published as v62, 23 Oct 2026 ("Manitoba stations, Peebles, Verlo, Tutshi").
- (23 Oct 2026) EASTERN WATER for the Ontario expansion (Brendan): places/east_water/eastern_lakes_and_ocean.gpkg (his simplified StatCan
  selection, EPSG:3347: Great Lakes, Lake of the Woods, Rainy Lake, larger Ontario lakes, the Atlantic side). water_east.py -> water_east.json
  (simplify 100 m), in make_page.py, make_site.py and basemap/build_tiles.py (WATER_FILES). Drawn only: not in water_extra.pkl, so no steamer
  lanes on it yet. Basemap border extent widened to 50 W, 38 N (Natural Earth cut copies regenerated). STATE.md stays public (Brendan).
- NEXT BASEMAP REBUILD (Brendan, 23 Oct 2026; do it the next time the water or projection changes, not before): speed up
  basemap/build_tiles.py. With the Atlantic in, the build takes about 25 min, nearly all spent carving open-ocean tiles out of the one huge
  Atlantic polygon (about 4,600 of 7,807 tiles lie east of 80 W, nearly all plain squares). In the tile loop, before intersecting, test
  whether a water part contains the tile box (shapely.prepare the parts once per level; parts[i].contains(bx)) and if so write the box as
  the tile's water. Expected build 5-10 min; output should match (compare tile counts and bytes). The Atlantic stays: Brendan expects to
  reach Newfoundland.
- ONTARIO AND QUEBEC SOURCES (Brendan, 23 Oct 2026): Paul Delamere's Ontario and Quebec collections are to be the track AND station source;
  apart from the timetables, no other sources (no NRWN Ontario/Quebec extract, no CGN names files) are planned. Only the Lakehead Routes KMZ is
  on hand so far (traces/ontario/lakehead_all.json; CP Superior District stops near Schreiber, about 87.3 W). The raw KMZs go to the private
  repo; the parsed pieces actually used go public (as with the Lakehead). Stations: use the collections' station points (the "Architecture"
  folders, as ont_stations() does at the Lakehead), with mileage placement where a station has no point.
- (23 Oct 2026) DELAMERE ONTARIO RAILWAY MAP COLLECTION received (private: traces/ontario/kmz_orm/Ontario_Railway_Map_Collection.kmz; parsed
  with tools/parse_kmz.py to traces/ontario/ontario_all.json, same format as lakehead_all.json, descriptions kept). 19,843 pieces: 13,204
  lines (about 30,000 km; CN 15,900 incl. GTR 10,100 and CNoR 4,700; CP 8,550; independents 3,600 incl. Algoma Central 1,580 and ONR
  1,290; American roads 2,080), 5,716 points of which 2,407 are stations (CN 1,265, CP 731). Extent 95.2 to 74.4 W, 42.0 to 51.3 N.
  Station notes often give the subdivision milepost ("Mile 146.2 of the Ignace subdivision"), station number and telegraph code: use
  the milepost for placement. Several towns have 1st/2nd/3rd stations: pick the one standing in 1948. Not found as station points:
  Toronto Union Station, Capreol, Port Arthur (Lakehead file has it), Winnipeg (out of area).
  Coverage check (main track, sidings left out, ends joined within 60 m), by railway: CP Fort William - Schreiber - White River - Chapleau
  - Sudbury - North Bay - Ottawa, Sudbury - Parry Sound - Toronto, Toronto - London - Windsor, Toronto - Owen Sound, Sudbury - Sault
  Ste. Marie, Kenora - Fort William all continuous; CP Toronto - Peterborough - Smiths Falls continuous with joins under 400 m. CN Lakehead
  - Nipigon - Longlac - Hornepayne - Foleyet, Armstrong - Nakina - Cochrane, Sioux Lookout - Armstrong, Capreol - Parry Sound - Toronto,
  North Bay - Huntsville - Toronto, Toronto - Kingston, Toronto - London - Sarnia, Hamilton - Niagara Falls continuous; ONR North Bay -
  Cochrane continuous. Breaks: CN at Capreol (338 m, 46.7104 -80.9253 / 46.7075 -80.9237) and at Brockville (56 m). 1948 ALIGNMENT:
  between Cardinal and Cornwall the file has both the pre-Seaway GTR main ("Former westbound main from Cornwall to Cardinal",
  "abandonment due to flooding by the St. Lawrence seaway opening in 1958") and today's line: route over the former, drop the latter
  (as KEEP_OLD / TRIM in wa_lines). 443 lines carry abandonment notes and 665 a year: filter post-1948 builds and pre-1948 abandonments
  by note, as with the Mississippi Rails KMZs. Quebec collection still to come. Coverage map: not kept (scratch).
- LATER (Brendan, 23 Oct 2026): Ontario interurbans still running in 1948, from Delamere's Canadian Electric Railway Mapping Project (the
  same collection the B.C. Electric KML came from). Not now; he will get to them.
- (23 Oct 2026) DELAMERE QUEBEC COLLECTION received (private: traces/quebec/kmz/Quebec.kmz; parsed to traces/quebec/quebec_all.json).
  The file calls itself "Quebec1.kmz" and is INCOMPLETE: 5,445 placemarks, 60 empty folders, among them CN Roberval subdivision main line,
  Matapedia and Gulf Railway main lines, Rouyn subdivision, Montreal Tunnel line, CP St. Maurice Valley and Drummondville subdivision main
  lines, St. Francis and Megantic main line (asked Brendan for a fuller save or a Quebec2). About 11,000 km of main track as received.
  STATIONS: the name is often in the DESCRIPTION, with a blank placemark name ("Gare Mont-Joli station"): read the label as name, else
  the first line of desc. About 1,030 station points (CN 601, CP 393); found for nearly every town (Levis, Riviere-du-Loup, Mont-Joli,
  Matapedia, Gaspe, Rimouski, Matane, Hull West, Lachute, Farnham, Lac-Megantic, Grand-Mere, St-Jerome); missing Roberval, Val-d'Or,
  Jonquiere (the empty folders). Only 7 give a milepost: intermediate stations by printed mileage. Track: Riviere-du-Loup - Mont-Joli - Matapedia - Gaspe
  continuous on CN (an earlier note that track stopped short of Matapedia was a wrong test position); CN Hervey - Chicoutimi about 68 km missing; several CP gaps around Montreal (Farnham, Joliette,
  St-Jerome) close only through other railways' pieces: recheck when the fuller file arrives.
- (23 Oct 2026) CHECK LATER (Brendan): CN Table 75 Valleyfield sections (on_cn_t075v.csv) are an interpretation (cars split/joined at Coteau,
  short Coteau - Valleyfield runs). Brendan agrees it makes sense; recheck against the Valleyfield timetables when he supplies them.

## Version 63 (23 October 2026): Ontario and Quebec, first pass (published to GitHub Pages)
- Timetables (Brendan's scans, private repo scans/on1948/01-19.png), transcribed by hand one table at a time: on_cp_t004 (Montreal - Fort William),
  on_cp_t058 / t058b / t058p (Toronto - Sudbury, Camp Borden, Port McNicoll boat trains), on_cp_t070 / t070b (Sudbury - Sault, Little Current mixed),
  on_cp_t075 (Creighton), on_cp_t707 (Toronto - Owen Sound boat trains, miles ESTIMATED 121), on_cn_t075a/v/b/t (Montreal - Ottawa, Valleyfield
  sections, Ottawa - North Bay - Capreol - Armstrong, Toronto - Capreol), on_cn_t038q/m/h/n/t (Quebec/Montreal - Hervey - Senneterre - Cochrane,
  Noranda), on_onr_t001 / t001c / t018m / t018s (ONR main line, Cochrane sections, Moosonee, Swastika - Noranda), on_acr_t001 / t001m (Algoma Central).
  Transcribed, NOT BUILT: on_soo_t070 / t070b (Soo Line, U.S.), on_dssa_t074 / t074c (DSS&A, U.S.), marine/ (Pointe au Baril, Muskoka Lakes, CP
  Keewatin / Assiniboia, S.S. Manitoba: waiting for port positions, marine/PORTS_NEEDED.md; Muskoka lakes water missing).
- Step on_build (on_build.py, helper on_lines.py): Delamere's collections are the track and the stations. on_lines switches ab_lines to a Lambert
  conic centred on Ontario for this step (UTM 10 overstates 8-18 % there); graphs per railway ('sk:oncp', 'sk:oncn', 'sk:onr', 'sk:acr'; own track
  1.0, sidings 1.6, other railways 2.5 drawn in their colour; other railways' sidings left out to keep the graphs small). Eastern time = -3 h (TZ 'E').
  New kinds h (Ontario Northland) and z (Algoma Central), colours Claude's picks; views nont, ontario, quebec. GTFS agencies ONR, ACR (and GWWD,
  missing since 18 Oct).
- Traced vs printed: CP 4 989.8 / 989.4; CN 75 east 858.4 / 852.7; ONR 476.9 / 486.8; ACR 294.4 / 296.0; all on track except straight estimates:
  CP Tottenham - Midhurst 30.5 mi (the CP line by Beeton not found as CP track), Ypres - Camp Borden 3.2, Worthington - Turbine 3.0; CN Hervey -
  Gouin 10.7, Quebec - Neuville 18.6 (CN Palais approach); ONR Larder Lake - Cheminis 8.7. Checks: ab.py vs V62 nothing moved; GTFS 1 problem (old).
- HAND POINTS BY CLAUDE (approximate, to confirm with Brendan): Toronto Union, Montreal Windsor and Central, Capreol, Timmins, Taschereau, Ypres,
  Camp Borden, CN Noranda-Rouyn (nearest CN line to the ONR station). Collection names aliased: Hervey -> Hervey Junction, Coteau -> Coteau Junction,
  Porquis -> Porquis Junction, Quebec -> Palais, Ottawa -> Ottawa Union, Port McNicoll -> Port McNicoll main.
- NOT YET: through running at the Lakehead (CP 1/2/3/4/7/8 and CN 1-4 end at Fort William / Armstrong here and start again on the Manitoba lines:
  link them in real_ends like the Saskatchewan pieces); the ACR days (printed Mon/Wed/Fri south of Hawk Jct but daily ex Sun north of it: asked).
- DONE in Version 64 (below). (Brendan, 23 Oct 2026 19:52): ONR track needs its own distinct colour. The ONR owns its track north of North Bay; south of North Bay
  its trains run over the CN (already drawn in CN colours, on_lines 'onr' graph CN at 1.2). The current --onr #1f5c3a is almost the same green as
  --cn #2f6b44, so ONR track reads as CN. Change --onr (light and dark) in page_template.html and the 'onr' colour in on_lines.RAILS; check the
  North Bay - Cochrane / Timmins / Moosonee / Swastika - Noranda track all draws in it and Toronto - North Bay stays CN. Colour: to pick with Brendan.

## Version 64 (23 October 2026, evening; published)
- ONR colour #febc11 (today's ONR yellow; Brendan), light and dark; ONR badge text dark. ONR own track North Bay - Cochrane / Timmins / Moosonee /
  Noranda draws yellow; Toronto - North Bay stays CN.
- traces/ontario/brendan/ontario_quebec_links.geojson (public; fed to the Ontario/Quebec graphs as own track of 'own', other railways at 2.5):
  Brendan's Hervey Junction gap, Camp Borden upper-station spur, Montreal Central Station wye (transcontinentals reach Central Station from the West
  Island, not the Mount Royal tunnel); straight connectors from the end of track to Gare Windsor (CP) and Gare Palais (CN); a 40 m CN tie at the
  Quebec junction (-71.2317, 46.8359) where two lines meet mid-piece.
- on_lines.despike(): drops single stray vertices (49 pieces; the ONR Noranda branch near Bear Lake jumped 2 mi north and back: 4.4 mi of false track,
  which made Larder Lake - Cheminis fail).
- Hand points (Brendan): Toronto = collection "2nd Toronto Union station"; Montreal CP = "Gare Windsor station", CN = "Gare Centrale station"; Quebec CN =
  "Gare Palais station"; Capreol 46.710925 -80.928981; Taschereau 48.662350 -78.680875 (he is not sure); Ypres 44.261342 -79.843000; Camp Borden lower
  44.269889 -79.891308, upper 44.286324 -79.886619 (on_build OVER places); CN Noranda 48.246808 -79.026961 (est). Aliases: Timmins = "Timmons station",
  Beaver Lake = "Bear Lake" (Brendan: probably the same; Beaver Lake ends up placed by mileage). Worthington and Turbine (CP 70, 70b) pinned to the Soo
  branch: the collection's points snap to the parallel Algoma Eastern line.
- No straight estimates left in Ontario/Quebec. Checks: check_gtfs 1 problem (old: CP-14-SKJCP13 at Minneapolis).
- TO DO (Brendan, 23 Oct 2026 21:08, small corrections for later; do not build ahead of him):
  * CN trains that do not call at Pembroke (Nos. 1 / 2) should run straight through on the through tracks at Pembroke Junction (on_cn_t075b).
  * Ottawa is one Union Station (one stop: done 24 Oct). CN trains back out of it; CP trains CAN run through but do not have to (Brendan, 24 Oct):
    route each by its table, a CP train backing out where its route comes and goes on the same side. Check the CN routes in and out.
  * Some "janky" uses of junctions in the Ontario/Quebec routings (Brendan has more; not now, keep on the list).
  * Table 116 (Longlac - Fort William, Nos. 79 / 80): the Toronto section may be a connection with Nos. 3 / 4 at Longlac rather than through cars
    (Brendan, not certain). Entered with from/to Toronto and the doubt in the notes; real_ends does not link them yet.
- (23 Oct 2026) CN Table 108 (Cochrane - Kapuskasing - Hearst - Nakina: Nos. 11 / 12, mixed M421 / M422) and Table 116 (Longlac - Port Arthur - Fort William:
  Nos. 79 / 80) transcribed (on_cn_t108, on_cn_t116); The Northland's Kapuskasing section Nos. 149 / 150 as ONR over the CN (on_onr_t108; ONR graph box
  widened west to 82.6 W). Port Arthur placed by mileage (the CN Port Arthur point does not fit the printed miles), sharing the CN_PORT_ARTHUR stop.
- (23 Oct 2026 21:46) FIXED: CN Nos. 1 / 2 (Montreal transcontinentals) ran North Bay - Capreol over the CP (Field had no point of its own; the cheapest
  route went by Sudbury). Field pinned on the CN line (Brendan: about -80.0243, 46.5235; on_lines HAND). Now North Bay - Capreol 83.7 mi traced
  (printed 83.4), all CN track.
- TO DO WHEN THE NEXT INTERURBAN IS ADDED (Brendan, 23 Oct 2026 21:57; REMIND HIM when he brings a new interurban, e.g. the Ontario lines from
  Delamere's electric railway file):
  * The B.C. Electric's line-by-line track colours (Central Park, Burnaby Lake, Lulu Island, Marpole - New Westminster: LINE_COLOR / station rings in
    page_template.html) are dated: all BCER track one colour.
  * All interurban track (every company) drawn in the same style as the Chilliwack line; lines and companies told apart by the CAR colour, not the track.
  * He is not satisfied with the interurban train icon: revisit later (not part of the above).
- (24 Oct 2026) Ottawa: one Union Station for CP and CN (Brendan: every train to Ottawa uses Union Station unless the table says otherwise). CP Table 4's
  "Ottawa" now shares stop OTTAWA_UNION (on_lines SHARED); Ottawa (Bank Street) stays separate (CN mixed M205 / M206). The routing part (CN backing out;
  CP may run through or back out) is still on the to-do list.
- (24 Oct 2026) FIXED: CN Table 161a Holmfield - Deloraine on Brendan's trace (it had run by Killarney). Two causes: (1) build.py did not count files a
  script finds by a pattern (glob of traces/<folder>/*.geojson) as inputs, so new traces never made sk_build (or on_build) stale; build.py now adds them
  (literal os.path.join(HERE, ..., '*...') and glob.glob('...*') patterns found in the scripts, plus steps.json "input_globs" for patterns built from
  variables: sk_build traces/np, traces/gn). (2) The trace's west end stopped 0.6 km short of the track through Deloraine and tied to nothing: a link
  north added in the same file, and the trace costs 0.7 so it beats the Killarney line. 99.6 mi traced, 95.9 printed. Only skcn161a moved (the CP lines
  through Deloraine shift by about 7 m where the link meets their track).

## Version 65 (24 October 2026): CP Tables 18, 19, 19A, 22 (Montreal - New York; Eastern Townships)
- Scans (private repo scans/cp1948_qc/): t018, t019, t019a, t020_022. Brendan asked for Tables 16-22 "all the same page". Tables 16, 16A and 17 are for a
  future Atlantic Canada build; Table 21 is a gap in the numbering (Brendan, 24 Oct 2026). Table 20 (Eastray - Kingsbury) is freight only. Transcribed by Claude.
- Table 18 (Montreal - New York). New railways in on_lines.RAILS: 'onnyc' (kind t, New York Central, own 'nyc', dark grey #3d3d3d / dark theme
  #a8a8a8, Brendan) and 'ondh' (kind f, Delaware & Hudson, own 'dh', #0f6fa8 / #6fb3e0, Claude's pick). GTFS agencies NYC and DH.
  * on_nyc_t018.csv: Windsor Station - Westmount - Montreal West over the CP, then at Adirondack Junction onto the St. Lawrence & Adirondack (owner()
    gives 'nyc' for the Quebec collection's American Railroads / New York Central folders; drawn dark grey) to the end of its trace at the border
    (-74.2423085, 44.9921679). 55.1 mi traced. No train numbers printed (trip ids NYC-ONNYC018-NYCn). UTICA LEFT OUT (Brendan, 24 Oct 2026).
  * on_dh_t018.csv: the same CP start, then the CP by Adirondack Junction and Delson to the end of CP track at (-73.3727996, 45.0103103) (Brendan).
    41.8 mi traced; all CP track (drawn CP).
  * Border times are NOT printed: estimated by mileage between Montreal West and Troy / Albany, marked '~' in the CSV (new: ab_lines reads '~' as an
    estimated time, timepoint 0, shown "est." on the page for kinds t and f too).
  * Full runs kept, not built: on_nycfull_t018.csv, on_dhfull_t018.csv (Troy, Albany, New York). "We will extend the Montreal - New York trains over the
    border at a future date" (Brendan).
  * Rutland trains (Montreal CENTRAL Station - New York, 387 mi, 2 each way, no numbers or intermediate times): on_rut_t018.csv, NOT BUILT. Asked
    Brendan: the Rutland ran over the CN from Central Station (to Rouses Point); leave it until the CN timetables, which detail it (24 Oct 2026).
  * D&H No. 37 entered with its times effective June 6 (until June 5: New York 9.00 a.m., Montreal 7.10 p.m.; in the note).
  * Montreal stops shared with the CP (SHARED: CP_MONTREAL_WINDSOR, CP_WESTMOUNT, CP_MONTREAL_WEST). Montreal West is placed by mileage, as in CP Table 4:
    the collection's "Montreal Ouest" point snaps to a dead-end siding and made Table 4 run out and back.
  * The 'nyc' and 'dh' graphs are boxed to the Montreal - border area and take CP sidings (the CP yard track at Montreal West is what joins the main
    line to the Adirondack line in the collection).
- Eastern Townships (CP): on_cp_t019m (Montreal - Farnham - Foster: Tables 19/19A print Montreal and Foster only, Farnham times from Table 22; No. 40
  runs daily except Saturday: Table 19 says ex Sat & Sun, 19A adds Sunday), on_cp_t019 (Foster - Waterloo - Drummondville; M253 Wickham 7.18 -
  Tourvilles f7.22 as printed, probably a misprint), on_cp_t019a (Foster - Knowlton - Sutton), on_cp_t022 (Farnham - St. Hyacinthe - St. Guillaume),
  on_cp_t022s (Farnham - Bedford - Stanbridge; the northbound mixed trains take an hour Stanbridge - Bedford, as printed).
  Aliases: Clearys -> Cleary, Tourvilles -> Tourville, Sutton -> "Sutton Flats", St. Guillaume -> St. Guillaume Junction, Stanbridge -> "Stanbridge
  Union" was wrong (a Central Vermont station): Stanbridge is the end of the 2.78 mi "Lake Champlain and St. Lawrence Junction Railway" Stanbridge
  junction segment (Brendan, 24 Oct 2026; on_build OVER places). Claude's straight tie removed. 13.8 mi traced, 13.8 printed.
- Checks: all new lines on track; no existing line moved (viz_data compared); check_gtfs 1 problem (old).
- TO DO (Brendan, 23 Oct): recheck the Valleyfield sections (CN Table 75, on_cn_t075v) when he supplies the Valleyfield timetables.

## Version 66 (24 October 2026): CP Tables 23, 24, 26 (Montreal - Sherbrooke, Montreal - Boston)
- Scans (private repo scans/cp1948_qc/): t023, t024 (printed sideways), t026_signs (Table 26 and the page's signs).
- on_cp_t023 (Table 23: Montreal - Farnham - Foster - Magog - Sherbrooke; Nos. 42, 40, 204, 202 / 41, 39, 215, 203, 205). REPLACES on_cp_t019m (deleted):
  Table 23 prints these trains in full. Its days differ from Table 19's: Nos. 42, 202, 39 daily here (Table 19 gives them only on the days they connect for
  Drummondville). No. 41's column sits half a row low on the curved page; read against No. 213's rows. Sherbrooke - Megantic is Table 10 (not in hand).
- on_cp_t024 (Table 24 Montreal - Boston, map part): Nos. 210 / 209 The Red Wing, 212 / 211 The Alouette, 214 / 213 Montreal - Newport, Vt., over the
  Table 23 stations to Farnham, then Brookport - Brigham - Cowansville - West Brome - Enlaugra - Sutton - Abercorn to the end of CP track at the border
  (-72.6637808, 45.0152297; Richford, Vt. next). Border times estimated by mileage ('~'). 209 Sutton 5.33 - West Brome 5.40 (7.7 mi in 7 min) as printed.
  NOT ON THE MAP: Glenton and Highwater, Que. (the CP dips through Richford, Vt. and back into Quebec before North Troy); join them when the U.S. track comes.
  Full run with the Boston & Maine connections: on_cpfull_t024.csv; mixed M770 / M769 Newport - Woodsville: on_cpfull_t024m.csv (not built).
- Table 26 Barre and Chelsea R.R. (Woodsville - Wells River - Montpelier): on_bch_t026.csv, not built (U.S.). Tables 16, 16A, 17: Atlantic build; 21: a gap.
- Aliases: South Stukely -> "Stukely South", St. Johns -> "St Jean sur Richelieu", Iberville -> "Iberville Junction". Eastray, Mount Orford, Petit lac
  Magog, Sweetsburg and the stations Montreal West - Ste. Brigide other than Delson, St. Johns, Iberville, Versailles are placed by mileage.
- Page fix: a main-line train's panel showed mile 0 at a shared station whose own mile is 0 on another line (Farnham on Table 22); the origin override is
  now for local lines only.
- Checks: no existing line moved (bar the deleted oncp019m); check_gtfs 1 problem (old).

## Version 67 (24 October 2026): CP page 13 (Tables 33, 35-39); train names
- Scans (private repo scans/cp1948_qc/): t033 (Montreal - Trois Rivieres - Quebec), t035_039.
- TRAIN NAMES (Brendan: "make sure to capture train names"): on_build now passes `name=` from the CSV #train lines to the trips (the CN and ONR CSVs
  already had them but on_build dropped them). Added: The Dominion (CP 4, 58), The Red Wing / The Alouette (CP 24), Frontenac (Pool 354 / 353) and
  Viger (Pool 356 / 355) (CP 33, printed down the columns); The Continental Limited and The Northland now show too.
- on_cp_t033 (Windsor Station trains: Pool 358, 356 Viger, 362, 354 Frontenac, CP 350 / Pool 353 Frontenac, CP 351, Pool 355 Viger, Pool 357) and
  on_cp_t033v (Place Viger trains: 352 / 349 Quebec; Sunday 378 / 375 to and from Lanoraie for St. Gabriel). Route Windsor - Montreal West - Park Avenue
  - Bordeaux - St. Martin Jct. - Terrebonne - Lanoraie - Berthier - Trois Rivieres - Quebec (Palais), shared stop CN_QUEBEC_PALAIS. Place Viger has no
  printed mileage: set to the traced distance (Park Avenue 6.2 mi). Pool trains noted "Pool train (CP - CN joint service)"; sleepers and the Montreal -
  Edmundston through car (Pool 356 - CN 68 / CN 67 - Pool 357) in the notes.
- NOT BUILT (Brendan, 24 Oct 2026): the CN trains of Table 33 (60, 4, 2 / 3, 59, 1: Central Station - Charny - Levis, ferry to Quebec), with the CN
  timetables: on_cnpool_t033.csv. Ferry Levis Station - Quebec wharf 46.81183142623051, -71.20161491263052 (marine/PORTS_NEEDED.md). Tables 38 (Quebec
  - Murray Bay - La Malbaie) and 39 (Quebec - Lac Edouard - Chicoutimi), "via Can. Nat. Rys.": on_cnvia_t038.csv, on_cnvia_t039.csv, with the CN tables.
- on_cp_t035 (Lanoraie - Joliette - St. Gabriel), on_cp_t036 (Trois Rivieres - Shawinigan Falls - Grand'Mere; No. 380 Trois Rivieres printed 7.30,
  before Les Forges 7.32: entered 7.50), on_cp_t037 (Trois Rivieres - Grandes Piles mixed; Garneau = the collection's CN "Garneau Junction" point).
- Hand points (Claude, to confirm): Montreal Park Avenue (-73.6240, 45.5307), approximate (no collection point; by mileage the two Montreal lines put it
  in two places); Lanoraie on the main line (-73.315943, 45.992274) beside the collection's station (its other "Lanoraie" is the old village end of the
  abandoned branch). CLAUDE'S TIE (to confirm): the Joliette branch ("Current") ends 480 m north of the main line at Lanoraie and joins it only by the
  abandoned line; a straight tie added to ontario_quebec_links.geojson. Aliases: Place Viger, De Sales -> St. Francois de Sales, Berthier ->
  Berthierville (the table brackets Berthier 62.5 / Berthierville 64.6 with a bus), Quebec -> Palais, Grand'Mere, Grandes Piles, Les Gres, La Gabelle.
  Trois Rivieres is placed by mileage on the Montreal - Quebec lines (its point snaps to a stub; Tables 36 / 37 start at the point).
- Garneau: CN Table 38's "Garneau" (oncn038q, -72.3848, 46.6715) and the collection's CN "Garneau Junction" (-72.6463, 46.6362, used for CP Table
  37) need not be the same place (Brendan, 24 Oct 2026; he has not checked the map). Left as is.
- DONE in Version 68 (Brendan, 24 Oct 2026): the Windsor Station - Quebec trains take the other side of the wye near Park Avenue (see below).
- Checks: only trip names changed on existing lines; check_gtfs 1 problem (old).

## Version 68 (24 October 2026): CP Table 42 (the Laurentians: St. Jerome - Ste. Agathe - Labelle - Mont-Laurier; St. Lin)
- Scans (private repo scans/cp1948_qc/): t042 (page 14, outbound), t042_up (page 15, inbound).
- on_cp_t042 (Place Viger trains, miles as printed from Place Viger: 439, 441 (from Park Avenue), 445, 457, 465, 463 / 464, 466, 452, 456),
  on_cp_t042w (Windsor Station trains: 453, 447, 451, 449, 455 / 448, 454, the Sunday "SPL." from Mont Rolland, 462, 458, 460; Table 42 prints no
  Windsor - Park Avenue miles: Table 33's 11.8, Place Viger miles + 5.7 beyond), on_cp_t042s (Place Viger - Ste. Therese - St. Lin: 471, 473, 469 /
  470, 472). Seasonal trains on their July days (441 Sat + Sun; 453 daily June 27 - Aug 29; 451, 449, 448, SPL, 458 in season), the printed dates and
  the parlour cars (453 to Labelle, 449 to Mont Laurier, 454 / 458 from Labelle, 460 from Mont Laurier) in the notes.
- NOT BUILT: the Montreal - Ste. Therese part of Table 44 trains (421, 427, 423 / 422, 428, 424): on_cpx_t042.csv, to join to Table 44.
- Table 42 gives Place Viger - Park Avenue as 6.1 mi: on_cp_t033v's Place Viger now at Park Avenue less 6.1 (was the traced 5.6).
- PARK AVENUE WYE (Brendan): ontario_quebec_links.geojson "Park Avenue wye, west leg" (the collection's "Outremont yard" piece from the Montreal West
  line round to the Park Avenue line), marked "replaces": on_lines._graph leaves out collection pieces with the same ends as a link that replaces them
  (two coincident yard pieces had kept the leg tied only to the yard, so the routes had gone to Mile End and reversed). Windsor Station trains (Tables 33,
  42) now run Montreal West - wye - Park Avenue - Bordeaux; on_cp_t033 1.7 km shorter. Links may also carry "cost" (a factor for their own railway).
- STILL JANKY (for Brendan's junction list): at Montreal West the Windsor trains for Park Avenue run a few hundred metres south onto the Adirondack line
  and back north (the collection has no north-facing curve there).
- Checks: only oncp033 / oncp033v moved; check_gtfs 1 problem (old).

## Version 69 (25 October 2026): CP Tables 43, 44, 44A, 45, 45A, 46, 47, 48 (Montreal - Ottawa and the Ottawa district)
- Scans (private repo scans/cp1948_qc/): t043_down, t043_up, t043_signs, t044, t044a, t045_046, t047, t048. "Wd. Stn." = Windsor Station (Brendan).
- MONTREAL WEST WYE, EAST LEG (Brendan, 24 Oct 2026): the curve by which trains between Windsor Station and Park Avenue leave the main line east of
  Montreal West (the collection has it only inside a long "Current" siding piece): ontario_quebec_links.geojson "Montreal West wye, east leg" (cost
  1.5 so the Adirondack / Delson trains keep the main line through Montreal West). Windsor - Park Avenue trains (33, 42w, 44w) no longer run out and
  back on the Adirondack line. Tables 23, 24 and 4 moved slightly (they had used the yard track; now the main line).
- on_cp_t043 (Short Line, Montreal - Vaudreuil - Rigaud - Vankleek Hill - Ottawa: through 503 / 502, 505 / 504, 507 / 506 and the Montreal suburban trains
  to Vaudreuil / Rigaud, up miles printed from Ottawa). Seasonal A / B marks are about Monday May 24 only (ignored for July).
- on_cp_t004 (transcontinentals 1, 7, 9 / 2, 8, 10): Table 43 and Table 48 intermediate stops added (Pointe Claire, St. Annes, Vaudreuil, Rigaud,
  St. Eugene, Vankleek Hill, Ottawa West, Westboro, Almonte, Arnprior, Cobden; Carleton Place and Pembroke Ar / Lv). The Ottawa - Chalk River locals
  (551, 557, 555 / 556, 558, 550) MOVED to on_cp_t048 with all their stops.
- on_cp_t044 (Place Viger trains 423 / 422) and on_cp_t044w (Windsor Station trains 421, 427 / 428, 424): Montreal - Park Avenue - Ste. Therese -
  Lachute - Montebello - Hull - Ottawa, with their Table 42 stops; on_cpx_t042.csv deleted (now built).
- on_cp_t044a (No. 29 / 30 Ottawa - Bedell - Prescott, the Ogdensburg ferry not built), on_cp_t044p (pool trains 23, 33 / 34, 24 Ottawa - Kemptville -
  Smiths Falls for Toronto, and the Bedell - Smiths Falls connection), on_cp_t045 (Ottawa - Hull - Shawville - Waltham), on_cp_t045a (Renfrew -
  Eganville mixed), on_cp_t046 (Ottawa - Wakefield - Maniwaki), on_cp_t047 (Ottawa - Carleton Place - Smiths Falls - Brockville: pool 559 / 560, 563 /
  562, mixed M561 / M564), on_cp_t048 (the Chalk River locals).
- Hand point (Claude, to confirm): CP Brockville at the end of the Brockville and Ottawa main line (-75.6904, 44.5934); the collection has no CP
  Brockville station (it had placed it at the CN station, leaving a 5.4 mi straight line).
- Checks: all on track; check_gtfs 1 problem (old).
- FOR THE NEXT UPDATE (Brendan, 25 Oct 2026; DONE in Version 73 for Brockville):
  * Brockville: CP trains of this era ran on from the end of the CP line down the CN track to Brockville Union Station (CN and CP), 44°35'31.98"N
    75°41'34.23"W = (-75.692842, 44.591217). Replace Claude's hand point (cp, brockville) with this, let the CP graph use the CN track there (as
    CP), and share one stop with CN Brockville (on_lines SHARED).
  * TO DO: the Prescott - Ogdensburg ferry (connection for Table 44A No. 29 / 30 at Prescott; also noted in marine/PORTS_NEEDED.md).

## Version 70 (25 October 2026): CP Tables 8 (Quebec Central) and 10 (the Quebec part of Montreal - Saint John); Dorion
- Scans (private repo scans/cp1948_qc/): t008, t008_signs, t010, t010_signs (both printed sideways).
- QUEBEC CENTRAL (Brendan, 25 Oct 2026): a CP property, drawn and run as CP (it is the collection's "Tring subdivisin", already owner cp). Trains use CP
  track where there is any and the CN where they must (Quebec - Scotts Jct. runs CN across the Quebec Bridge by Charny; Levis' first 4 mi CN).
  on_cp_t008 (Nos. 6 / 1: Quebec Palais - Scotts Jct. - Vallee Jct. - Tring Jct. - Thetford Mines - East Angus - Sherbrooke - North Hatley - Beebe Jct. -
  border, for Newport, Vt. and the Red Wing to Boston; border at the end of the Massawippi Valley line, times '~' by mileage to Newport);
  on_cp_t008l (Nos. 2 / 5 Levis - Sherbrooke); on_cp_t008f (Vallee Jct. - St. Georges - Lac Frontiere, unnumbered mixed); on_cp_t008m (Tring Jct. -
  Megantic, unnumbered mixed). Buses (Beebe Jct. - Rock Island shuttle, Sherbrooke - Newport buses) not entered. Ste. Marie by mileage (no CP point).
- on_cp_t010 (Table 10 west of the border: Sherbrooke - Cookshire - Scotstown - Megantic - Boundary, Que.): 40, 204, 42, M256 / 39, 41, M257 (the mixed
  trains lay over at Megantic: separate runs each side). Times west of Vanceboro taken as Eastern (the A.T. dittos are a misprint there; Table 8 prints
  "Megantic E.T."). Border-side times for 39, 41, 40, 42 estimated Holeb - Megantic. on_cp_t010 builds after Table 23 so Table 23's 39 - 42 keep their
  trip ids (on_build LATE).
- Hand point (Claude, to confirm): Boundary, Que. at the middle of the collection's "Boundry siding" (-70.7015, 45.5446).
- TO DO LATER (Brendan: ignore the routing outside Quebec for now): Table 10 east of Boundary (Maine: Jackman, Greenville, Brownville Jct., Vanceboro;
  New Brunswick: McAdam, Fredericton, Saint John, St. Andrews, St. Stephen, Woodstock; the CN Halifax - Truro - Moncton - Saint John trains and the
  P.E.I. ferry), the Bangor & Aroostook connection, Table 8 south of the border (Newport - Wells River - Boston / New York over the B&M and the New
  Haven), the Quebec - Levis ferry (QC Nos. 2 / 5), the Beebe Jct. - Rock Island bus.
- DORION (Brendan, 25 Oct 2026): CP "Vaudreuil (Dorion)" of 1948 is the collection's "Dorion" station (-74.0084965, 45.3865095); the collection's
  "Vaudreuil" is the modern commuter station. Hand point added; Table 43's mileage placed it within 100 m of that point (23.7 mi checks); Table 4 had
  used the modern station (Westmount - Vaudreuil traced 24.0 vs printed 21.7): now fixed.
- Checks: check_gtfs 1 problem (old); only oncp004 / oncp043 (Dorion) moved, and segment colouring on oncp033 / ondh018.
- TO DO (Brendan, 25 Oct 2026, reminder): fix the trains that stop at "expansion joints": trains pausing mid-run where nothing is printed, at joins
  between track pieces. Find where (likely the joins / ties between collection pieces or links, or a route point that doubles back) and make them run through.
- TO DO WHEN THE CN LEVIS TRAINS ARE BUILT (Brendan, 25 Oct 2026): one Levis station for CN and CP, and it is the CN station (the collection's CN
  "Levis", -71.18712, 46.81032; the Quebec Central Nos. 2 / 5 already start there). Share the stop: on_lines SHARED ('oncp', 'levis') and ('oncn', 'levis')
  -> the CN Levis gid.

## Version 71 (25 October 2026): Quebec's independent railways (Official Guide, 1948)
- Scans (private repo scans/og1948_qc/): canada_gulf_terminal, temiscouata, roberval_saguenay (the railway name is cut off in the scan: "Roberval and
  Saguenay Railway", Brendan), alma_jonquiere. Source: Official Guide of the Railways (Timetable World).
- Four new railways, each its own kind, colour (Claude's picks) and GTFS agency: Temiscouata (T, ontem, #9c2f6b), Canada & Gulf Terminal (G, oncgt,
  #5a5ea8), Roberval & Saguenay (R, onrs, #1b7f5c), Alma & Jonquiere (J, onaj, #4a6d8c). Upper-case kind letters (the lower-case ones are used up).
  on_lines.owner(): Temiscouata Railway (filed under CN in the collection; independent until 1949) -> 'tem'; Matapedia and Gulf (the C&GT) -> 'cgt';
  Roberval and Saguenay -> 'rs', its Alma and Jonquiere folder -> 'aj'.
- on_tem_t001: Riviere du Loup - Cabano - Notre Dame du Lac - Ste. Rose (Degelis) - New Brunswick line, Nos. 1 / 2 (mixed), ATLANTIC time (new TZ 'A',
  four hours ahead of Pacific; on_build OVER shift). Border times (~) by mileage Ste. Rose - St. Jacques. NOT BUILT (New Brunswick): St. Jacques,
  Edmundston (CP connection), the mixed 3 / 4 Edmundston - Connors. Riviere du Loup shares the CN stop id (CN_RIVIERE_DU_LOUP).
- on_cgt_t001: Mont Joli - Metis Beach - Matane, two each way ex Sun (unnumbered). Mont Joli shares CN_MONT_JOLI. CLAUDE'S TIE: a 25 m link where the C&GT
  meets the CN main east of Mont Joli (mid-piece, so the collection did not join them).
- on_rs_t001: No. 2 mixed Arvida - Bagotville only (one train, read up). CLAUDE'S TIE at the Port Alfred yard - main line meeting (mid-piece). Port Alfred -
  Ruisseau Rouge forced: the collection's line climbs by a hairpin, 7.7 mi of track for 6.0 printed. Hand point (Claude, approximate): Arvida by the R&S
  roundhouse (-71.1656, 48.4259); no station point.
- on_aj_t001: Isle Maligne - St. Joseph d'Alma - St. Bruno - Saguenay Power, M1 / M2 ex Sun. Hand point (Claude, approximate): Saguenay Power at the south
  end of the A&J main line by the CN (Hebertville Jct., -71.6365, 48.4483).
- Checks: all on track; nothing else moved; check_gtfs 1 problem (old).

## Version 72 (25 October 2026): CP Tables 49, 50 (Montreal / Ottawa - Toronto, Toronto - Windsor)
- Scans (private repo scans/cp1948_qc/): t049a, t049b, t049_signs, t050a, t050b.
- Brendan (25 Oct 2026): the pool trains at CN stations (Note A: 5, 17, 9, 109 / 16, 14, 10, from Central Station) wait for the CN tables
  (on_cnpool_t049.csv); build Pool 15 / 6 now; build west of Toronto to Windsor, Ont. (Detroit and the NYC to Chicago kept in notes).
- on_cpcn_t049: Pool 15 (The Canadian) / 6 (Royal York), Windsor Station - Westmount - Montreal West - CP to Dorval - CN main - Toronto. New rail
  'oncpcn' (kind p, drawn CP / CN by the track; own graph 'cpcn': CP and CN at 1.0, the Quebec "Mainline and sidings" folder counted as main line;
  CN stop ids). No miles printed: CN main-line miles measured along the collection (Windsor Station - Toronto 333.2). Claude's ties: Dorval CP - CN
  connection (11 m), Coteau main-line tie (the Quebec and Ontario collections' CN main line pieces end 5 m apart, unjoined: the CN Montreal - Cornwall
  route had gone by Ottawa). Hand point CN Cornwall on the main line.
- on_cp_t050 (Lake Ontario Shore Line, printed miles): Pool 21 Chicago Express / 22 The Overseas (Note A: CP stations; they run Smiths Falls - Tichborne -
  Belleville - Agincourt - Leaside, not the CN), 29 / 30 and 35 / 36 (Montreal - Glen Tay / Perth part; Table 51 beyond not in hand), 597 / 598 (Sun,
  Montreal - Smiths Falls), M85 / M86 (Smiths Falls - Tichborne - Trenton mixed; Kingston connections not entered). on_cp_t050o: Pool 23 / 24 Ottawa -
  Bedell - Smiths Falls - Tichborne - Toronto (daily except Saturday). Rosedale and Don placed by mileage (the collection's points are Toronto's).
- on_cp_t044p: the "Bedell - Smiths Falls connection" columns removed: they were the Montreal trains 29 / 30 of Table 50.
- on_cp_t049w: Toronto - Parkdale - West Toronto - Guelph Jct. - Galt - Woodstock - London - Chatham - Windsor (no miles printed: measured along the CP
  track, 227.9): 19 The Canadian, 37 Royal York, 21 Chicago Express, 635 The Michigan (daily ex Sat), 629, 631 / 20, 38, 22, 634, 630, 632. Detroit and
  the NYC connections (Chicago, Central time) in the notes; from / to Montreal and Chicago set.
- NOT BUILT: on_cnpool_t049.csv (CN-station pool trains), on_cpx_t050.csv (Pool 33 / 34 via Peterboro; 35 / 36 Table 51 parts). TO DO: Table 51 (Glen
  Tay - Havelock - Peterboro - Toronto), Table 55 (Kingston - Tichborne), Table 56 (Toronto - Hamilton), Detroit - Chicago (U.S.).
- Checks: all on track; only oncp044p moved (the removed columns); check_gtfs 1 problem (old). P15 Belleville - Port Hope 49 mi in 43 min (as printed).

## Version 73 (25 October 2026): Brockville Union Station, CP approach to Toronto Union from the east, CP Leaside
- Brockville Union Station (CN and CP; Brendan): hand points (cp / cn, brockville) at (-75.692842, 44.591217); shared stop BROCKVILLE_UNION for CP Table 47,
  Pool 15 / 6 and (later) the CN. CP trains run on from the end of the CP line down the CN track (drawn CN). Claude's earlier CP Brockville point removed.
- Toronto Union from the east (Brendan): CP trains take the CP connector east of the station (the collection's "Leaside to Union" line, Campbellford Lake
  Ontario and Western, which stops 200 m short of the station point): link "Toronto Union Station, CP approach from the east". Before, the Shore Line trains
  ran Leaside - North Toronto - West Toronto and into Union from the west (Leaside had been placed by mileage on that line). Hand points CP Leaside and CP Don
  (the collection's points). Tables 50 (both) 3.7 km shorter. Every line ending at Union moved by ~50 m (the station end now snaps to the link), and the ONR
  and CN Toronto - North Bay / Capreol lines now leave Union by the same CN track (ONR's had used a different CN line for 24 km).

## Version 74 (25 October 2026): CP Toronto - Windsor (full), Tables 51, 52, 53, 55
- Scans (private repo scans/cp1948_qc/): tw050a, tw050b (Toronto - London - Windsor - Detroit - Chicago, printed as a second "Table 50"), t051_055 (sideways), signs.
- on_cp_t049w REWRITTEN from the full table with printed miles and every stop: 635 The Michigan, 19 The Canadian, 707 (/ 709) and 705 Toronto - Streetsville,
  37 Royal York, 629, 631, 21 Chicago Express / 20, 630, 706, 38, 708 (/ 710), 632, 22 The Overseas, 634. Not entered: Guelph - Goderich (Table 68), St. Thomas
  (69), St. Marys (69A) connections, and the LONDON & PORT STANLEY RY. connections (electric: London - St. Thomas - Port Stanley; times printed for 635, 37,
  629, 631, 21 / 20, 630, 38, 632, 22) -> REMIND BRENDAN: an interurban (his interurban to-do applies). London (Quebec St.) by mileage. Built after the
  boat trains (on_build LATE) so the Owen Sound boat trains keep CP-707 / CP-708.
- on_cp_t051 (Table 51 via Peterboro, Montreal - Smiths Falls - Perth - Sharbot Lake - Havelock - Peterboro - Toronto): 35 / 36 in full (Montreal - Smiths Falls
  stops from Table 50; MOVED out of on_cp_t050), 601, 619 / 620, 604, 602 (Peterboro / Havelock - Toronto locals). on_cp_t051o: Pool 33 / 34 Ottawa - Bedell -
  Smiths Falls - Sharbot Lake - Peterboro - Toronto (on_cpx_t050.csv deleted).
- on_cp_t052 (De Beaujeu - Cornwall mixed M593 / M592, connecting with 35 / 30). on_cp_t053 (M605 / M606 Havelock - Peterboro - Dranoel - Lindsay - Bobcaygeon).
  on_cp_t055 (Kingston - Tichborne - Sharbot Lake - Renfrew mixed M617, M613 / M618, M612).
- DUPLICATES REMOVED: Table 43's 29, 35, 597 / 30, 36, 598 (Montreal - Vaudreuil) are the Table 50 / 51 trains: dropped from on_cp_t043; their Montreal West -
  St. Annes suburban stops (Grovehill ... Baie d'Urfe) added to on_cp_t050 (hand-merged after t049.py: rerunning t049.py loses them).
- Checks: all on track; check_gtfs 1 problem (old).
- (25 Oct 2026, Brendan) Zoomed-out views: below FAR_K = 0.0009 px/m (the Saskatchewan, Manitoba, Lakehead, Northern Ontario, Ontario and Quebec views;
  Regina 0.0012 and closer unchanged) only junctions and terminals are drawn (station hub: one neighbour or three or more in the network of all lines' consecutive stops; overlapping lines count once) and train-number labels are left off (a selected train keeps its number, a selected
  station is still drawn). page_template.html: FAR_K, the station loop in drawBase, the three number-label blocks.
- (25 Oct 2026) QUEBEC CENTRAL from the Official Guide (April 25, 1948; scan og1948_qc/quebec_central, signs; Brendan: the CP table is condensed): intermediate
  stations added to on_cp_t008 / t008l / t008f / t008m with the Guide's times and whole miles: Charny (CN; Nos. 6 / 1), East Broughton, Black Lake, Disraeli,
  Garthby, Weedon, Bishopton, Ayers Cliff (main line); St. Camille (Lac Frontiere branch); St. Victor, St. Evariste, Courcelles (Megantic branch, which had only
  its ends). CP times kept where both print one (Thetford Mines CP 6.13 / 9.52, Guide 6.18 / 10.00). Lac Frontiere up mixed: St. Georges 2.45 (Guide; my
  CP reading had 2.15). Guide signs: large dot = connecting train (the B&M south of Newport). NOT ADDED (ask Brendan): the Guide's Sherbrooke - Rock Island -
  Newport trains "34" / "35" (Sherbrooke 1.00 p.m. / Newport 11.25 a.m.), the Beebe Jct. - Rock Island - Stanstead shuttle with Nos. 6 / 1, and a Vallee Jct. -
  St. Georges run in the No. 6 column (6.20 - 7.20 p.m.): the July CP table showed buses or nothing there.
  RESOLVED by the Guide's signs (scan quebec_central_signs2): a = daily except Sunday, BUS (Sherbrooke - Newport 34 / 35); v = daily, connection via BUS (Beebe - Stanstead):
  both stay out. The Vallee Jct. - St. Georges 6.20 p.m. run in the No. 6 column (no sign): ADDED as a train, VF3 in on_cp_t008f (Brendan, 25 Oct 2026).
- (25 Oct 2026, Brendan) Station panel: the Departures / Arrivals headings are now a table row carrying the day's count (all calls of the open day, 3 a.m. to 3 a.m.,
  including local cars not listed) right-aligned in the time column (renderStation, CSS .tt tr.tt-head).
- FOR TABLE 56 (Toronto - Hamilton, not in hand yet; Brendan, 25 Oct 2026): CP / TH&B trains ran over the CN Lake Shore line between Toronto and the junction
  just before Hamilton (trackage rights), then TH&B to Hamilton (Hunter St.). Route them on the CN Lake Shore, drawn CN, not over a CP line.
- (25 Oct 2026) Brendan's trace "Ottawa east gap (CN Montreal - Ottawa)" (-75.596, 45.392 to -75.592, 45.390) in ontario_quebec_links.geojson: the CN Montreal -
  Ottawa trains (on_cn_t075a) had detoured north round the gap into Union Station; now direct, 0.6 mi shorter. oncp004 changed only in segment colouring.
- (25 Oct 2026) NYC Ottawa line: on_nyco_t073.csv (NYC Table 73, Official Guide April 25, 1948; TRANSCRIBED BY BRENDAN): Nos. 61 / 62 ex Sun, Helena, N.Y. -
  Rooseveltown - Uscan - Cornwall - Finch - Embrun - Russell - Ottawa (N.Y.C. Station = the collection's "Ottawa Mann Avenue"; not Union Station by 1948).
  New rail 'onnyco' (kind t, NYC grey) with its own graph 'nyco': the Ontario collection's NYC main line only (CN / CP track and NYC sidings caught the
  Cornwall stations) plus Brendan's trace over the border to Helena (links file). Finch shares stop CP_FINCH with CP Table 50 (Brendan: one station at the
  crossing). Hand points: Helena (trace end), Rooseveltown (on the trace, approximate), NYC Cornwall / Cornwall Jct. / Uscan moved onto the main line.
  Helena - Rooseveltown printed 13 mi, the trace ~4.5 (forced): 62.8 mi traced vs 72 printed. NYC place_for now uses its own stations, CP only for Montreal.
- (26 Oct 2026) Brendan's trace "Richford, Vt. (CP, Newport and Richford Ry.)" (links file): the CP line from the border south of Abercorn through Richford, Vt.
  to the border before Glenton, Que., missing from the collections. Table 24 (on_cp_t024) now runs on to Richford, Stevens Mills, Missisquoi (Vt.), Glenton and
  Highwater (Que.) and the end of CP track at the border before North Troy, Vt. (-72.4122, 45.0072; mile 92.7, times by mileage). The old border point south of
  Abercorn is gone.

## Version 78 (26 October 2026): CN Tables 122 and 126 (Toronto - Parry Sound - Capreol, Toronto - Orillia - North Bay)
- Scans (private repo scans/og1948_on/): cn122a, cn122b, cn122_signs, cn126a-c. Script: scratchpad on/t122.py (writes every file below, and rewrites on_onr_t001).
- Two Toronto - Washago routes: by Beaverton (Table 122 miles, Washago 88.9) and by Allandale / Barrie / Orillia (Table 126 miles, Washago 98.8). One file per
  route: on_cn_t122 (Beaverton - Parry Sound - Capreol: 37, 633, M215, 631 / 4, 634, M216, 632), on_cn_t122a (Allandale - Parry Sound - Capreol: 3 / 38; Table 122
  miles + 9.9 north of Washago), on_cn_t126 (Allandale - North Bay: 41, 43 / 44, 54, 56), on_cn_t126b (Beaverton - North Bay: 55, 53 / 156; Table 126 miles - 9.9).
  Branch sections: on_cn_t126m (Toronto - Allandale - Collingwood - Meaford: 45 / 42 in full; 41, 44, 38 sections), on_cn_t126d (Allandale - Orillia - Midland),
  on_cn_t126p (Penetang), on_cn_t126c (Camp Borden; mile 78.0 estimated), on_cn_t126g (Scotia - Joe Lake - Algonquin Park). Junction times of sections are
  not printed: estimated (~).
- DUPLICATES: on_cn_t075t (3 / 4, ends only) DELETED: No. 3 now in full in on_cn_t122a, No. 4 in on_cn_t122. ONR 47 / 46 (on_onr_t001) gained their Table 126
  stops by Allandale; ONR 49 / 50, The Northland, MOVED to on_onr_t001n (by Beaverton; ONR miles - 9.9); 49 now daily except Saturday (Table 126 sign). The
  633 / 634 Hamilton sections (Allandale - Washago) are the same times as 41 / 44: not entered again (notes). 37's and 55's Allandale-block times are 43's.
- ONR trains on the CN share the CN stop ids (on_lines ONR_ON_CN, post-pass in register; their places from the CN). Aliases: Severn = severn bridge,
  Muskoka Wharf = gravenhurst wharf, Scotia = scotia junction, Penetang = penetanguishene. HAND (APPROXIMATE, Claude): CN Allandale (on the main line by the
  Collingwood line junction), CN Camp Borden (end of the Grand Trunk spur from Angus) -> ask Brendan to confirm both.
- Don (Queen St. East): CN stop shares CP_DON (one station). Not entered: Buffalo / Niagara Falls rows (connections; Brendan), Sudbury Jct. - Sudbury and Winnipeg rows (connections), No. 148 (will not run June 27 -
  Sept. 5), Muskoka Wharf calls of No. 41 (June 14 - 24 only), Muskoka Lakes steamers (Muskoka Wharf - Beaumaris - Port Carling - Wigwassan - Royal Muskoka)
  and Huntsville Dock - Britannia - Bigwin Inn - Dorset steamers -> marine to-do. 42 (p: ex Sun and Mon, also Mon June 28 - Sept. 6) entered ex Sun.
- Readings to check: 43 Trout Creek printed 5.39, read 5.59?; untimed flag stops of 633 / 634 (Port Bolster ... Moorelands, Hydro Glen) and Orillia Institute
  estimated by miles.

## TO DO, Thursday evening 29 Oct 2026 (Brendan, 26 Oct 2026, 23:01)
- TO CHECK (Brendan, list added 29 Oct 2026): points and readings Claude placed or guessed in Versions 78 - 84:
  - CN 122 / 126: hand points CN Allandale and CN Camp Borden (Camp Borden mile 78.0 estimated); No. 43 Trout Creek printed 5.39, read 5.59; No. 42 (p: ex Sun
    and Mon, also Mon June 28 - Sept 6) entered ex Sun; estimated junction times of the branch sections and untimed flag stops.
  - Table 56 / TH&B: International Railway Bridge border point (mid-river); TH&B - Michigan Central tie at Welland; Welland station point.
  - L&PS: Colborne St., Philip St., Elm St. placed by estimated mileage; Stop 7 printed mile 9.0, read 7.8; No. 37 St. Thomas time smudged, read 1.46.
  - Table 50 (on_cp_t049w): No. 20 The Canadian probably read one row off (Komoka 5.20 / 5.35 and Puslinch 7.19 should be London 5.35 and Guelph Jct. 7.19,
    per Table 68): recheck against the scan.
  - Table 73: No. 50 Elma printed 8.09 (impossible), estimated 8.26; Crest by mileage (collection point ~2 mi short).
  - Table 69: Ostrander, Kinglake, Embro, Bennington, McConkey, Lind by mileage.
  - Table 65: hand points CP Wingham (branch end), Wingham Jct. (by Glenannan); the Wingham in-and-out reading of the miles. Table 63: Fergus - Elora 65 / 50
    min as printed. Cataract hand point (shared by Tables 62 and 63).
- RUN-THROUGH CANDIDATES added since 26 Oct: CP / TH&B Toronto - Buffalo trains (CP 721 = TH&B 372, 741 / 374, 801 / 380, 821 / 382; 712 / 371, 732 / 73, 752 / 375,
  792 / 379, 832 / 383) at Hamilton; M747 / M748 Orangeville - Cataract (Table 62) - Elora (Table 63) at Cataract.
- RUN-THROUGH TRAINS: re-configure trains split across files to run through as one trip, e.g. CN 3 / 4 Toronto - Capreol (on_cn_t122a / t122) - Armstrong -
  Winnipeg - Vancouver (on_cn_t075b, Manitoba / west files). Same for the other trains split by table (ONR 47 / 46 and 49 / 50 at North Bay, 54 -> 56 and
  55 -> 53 at Scotia, CP pool trains, etc.). Needs a join step in the build (trips with the same railway and number meeting at a shared stop).
- UNNUMBERED CONNECTING TRAINS: branch sections and connections printed in a parent train's column currently get the parent's number by default
  (e.g. on_cn_t126m / d / p / c / g: No. 41, 44, 38 ... sections). Brendan is uncertain of this practice. Review: through-car sections vs separate connecting
  trains; consider no number (or "connection to No. 41") where the table prints none.
- (Brendan, 23:03) Much may settle itself as the branch tables come in: their own numbers will replace the main-table sections (then delete the section
  files, e.g. on_cn_t126m / d / p / c / g, as duplicates). Wait for the branch tables before renumbering by hand.

## FOR THE NEXT BIG UPLOAD: how trains are drawn (Brendan, 27 Oct 2026)
- (Brendan, 28 Oct 2026, 09:28) INTERURBAN TRACK AND STATIONS: every interurban line drawn as a SOLID line with CIRCLE stations, as the Chilliwack line
  is now (not the railway double-dash track and square stations). Collapse all the B.C. Electric lines (Chilliwack, Central Park, Burnaby Lake, Lulu
  Island, Marpole - New Westminster) into ONE style, red (one legend entry instead of the five circles). The L&PS (kind 'P', its own dark blue / gold)
  in the same format: solid line, circle stations.
- INTERURBAN (B.C. Electric Chilliwack trains, now two coupled cars): draw like the mainline consists (drawConsist: laid along the track, true-ish length
  zoomed in) but FOUR capsules, all in the interurban red (no black locomotive: self-propelled cars), direction nose on the leading car. The local
  lines (Central Park, Burnaby Lake, Lulu Island) drawn THE SAME WAY (Brendan, 10:16: no need to tell them apart by drawing; the Chilliwack trains
  already carry train numbers).
- MOTOR TRAINS: DONE in Version 136 (6 Nov 2026), see that section. Earlier note: ON HOLD (Brendan, 27 Oct 2026, 10:16: hold off for now). Notes kept for later. (Asked whether plausible: yes): kind=motor is already in the CSVs (41 trains in 15 files: CN 633 / 634, Saskatchewan and Alberta
  CN / CP branch motor trains). Carry a motor flag into viz_data (ab_lines sets the name 'Motor train' only when the train has no name; use the kind,
  not the label) and draw a short consist: a power car in the railway colour with a nose, plus one trailer (2 capsules). Check the other files that print
  motor-train signs but are not tagged (e.g. Alberta CN 168 / 171 / 203, CP 6 / 138, Saskatchewan CN 199 / 211 / 212 / 214 ...; many mentions are motor
  BUSES, left out) and tag the real motor trains.
- page_template.html: drawConsist (n = 7 cars, 4 for local / mixed), the twin-car branch of the car drawing for the interurban.

## Version 79 (27 October 2026): Table 56 Toronto - Hamilton - Buffalo; the TH&B as its own railway
- Sources: CP timetable 1948 Table 56 (Brendan's image) and the Official Guide, April 25, 1948 TH&B table (Hamilton - Welland - Fort Erie with every station;
  Waterford - Brantford - Hamilton Nos. 144 / 145; Dunnville bus). Script: scratchpad on/t056.py (helpers on/t122lib.py).
- TH&B OWN COLOUR (Brendan, 27 Oct 2026: CP-filed but NYC majority-owned; between CP and NYC): new rail 'onthb', kind 'B', colour 6A4048 (dark mode c99aa3),
  Claude's pick; page_template wired (css vars, badge, legend, KIND_*, colours, kinds list). owner(): the collection's TH&B folder (under CP) -> 'thb';
  'American railroads / Canada Southern' -> 'nyc' (Michigan Central; was None).
- on_cpthb_t056 (rail 'oncpthb', CP colour, graph 'cpthb'): CP 731, 721, 741, 761, 801, 821, 763 / 712, 732, 752, 722, 792, 832, 762 Toronto - Sunnyside -
  Hamilton over the CN Lake Shore (trackage rights), then TH&B to Hunter Street. on_thb_t056: TH&B 372, 374, 76, 380, 382 / 371, 73, 375, 379, 383 Hamilton -
  Smithville - Welland, NYC Welland - Fort Erie (= Bridgeburg station point; Brendan: watch for NYC Bridgeburg) - International Boundary on the bridge (border
  times by mileage; Black Rock / Buffalo in notes). The through trains change numbers at Hamilton (CP 721 = TH&B 372 ...): RUN-THROUGH JOIN candidates.
  on_thb_t056w: TH&B 144 / 145 Waterford - Brantford - Hamilton: CONNECTIONS with the NYC at Waterford, not through service (Brendan doubts a through train).
- Gas-electric cars (Guide notes; Brendan): TH&B 73, 76, 144, 145 tagged kind=motor (motor drawing itself on hold).
- Michigan Central / Canada Southern = straight NYC (Brendan): owner 'nyc', drawn NYC grey.
- Agency THB added (on_build agencies list).
- Not entered: Welland - Niagara Falls rows (bus connections, the bus sign in the Guide), Dunnville / St. Anns buses.
- Links (APPROXIMATE, Claude): International Railway Bridge, Fort Erie - mid-river border; TH&B - Canada Southern eastbound main tie at Welland.
  Hand: TH&B Waterford = the NYC Waterford station (Brendan, 29 Oct 2026; through the BW&LE wye; stop NYC_WATERFORD); TH&B Hamilton = Hunter Street = the collection's "2nd West Hamilton station" (Brendan, 27 Oct 2026), Welland (NYC station point), Waterford (BW&LE station building), Fort Erie = Bridgeburg.

## Version 80 (27 October 2026): CP Table 62 Toronto - Orangeville - Owen Sound; CP Ontario paused for the week
- on_cp_t062 (CP timetable 1948, Brendan's image; scan cp1948_on/t062.png): 705, 707 (ex Sun), 709 (Sun) / 706, 708 (ex Sun), 710 (Sun) Toronto - Streetsville -
  Orangeville - Owen Sound, printed miles; M748 / M747 Cataract - Orangeville mixed (Elora line, Table 63, not in hand). Cataract, Melville, Fraxa by mileage.
- DUPLICATES REMOVED: on_cp_t707.csv (S.S. Manitoba boat trains 707 Thu / 708 Tue, ends only) DELETED: the regular 707 / 708 with the same times (notes
  carry the boat-train days). The Toronto - Streetsville columns 705, 707 (/ 709), 706, 708 (/ 710) dropped from on_cp_t049w.
- Brendan (27 Oct 2026): STOP CP ONTARIO HERE FOR THIS WEEK. Still to come: Tables 63 (Elora), 65 (Orangeville - Walkerton / Teeswater ...), others.
- (27 Oct 2026, Brendan) "On the line" panel: Next departures (and the next Central Park cars line) now at the TOP of the list (renderList in
  page_template). TH&B ('B') added to the few-trains kinds (no heading when none running). Page-only changes: `python3 build.py --assemble` (7 s), not a build.

## Version 81 (28 October 2026): London & Port Stanley Railway (the first interurban outside B.C.)
- Sources (private scans/lps/): Time Table No. 76, May 21, 1947 (USED, Brendan's choice: the 1947 summer as printed stands in for summer 1948); Time Table
  No. 80, June 8, 1949; Official Guide March 1948 (winter, 13 / 14 trains). Track and stops: the Canadian Electric Railway Mapping project KMZ (Brendan, same
  source as the BCER) -> traces/ontario/brendan/london_port_stanley.geojson (main line London - Beach, London station leads, St. Thomas track 81 to the
  N.Y.C. Depot; own 'lps'). The Ontario collection had only London - St. Thomas (owner now 'lps').
- on_lps_t001: 20 southbound / 20 northbound, L&PS numbers (Locals and Limiteds; 202 / 2 / 204 / 203 / 3 / 205 ex Sun; 36 / 37 night cars to / from the N.Y.C.
  Depot). EASTERN STANDARD TIME as printed. Stops: the timetable's ten; the all-train stops of the timetable note (Colborne St., Philip St., Stop 1, C.N.R. -
  Wabash Depot, Palm St., Elm St., Stop 23; times ~); the KMZ's numbered stops as flag stops of the locals (Brendan; ~f). Colborne, Philip, Elm by mileage
  (Claude). Stop 7 printed mile 9.0, read 7.8. Trains via the N.Y.C. Depot (8, 9) back out of the spur to Talbot Street (Brendan): Talbot St. row twice.
- Shared stops: L&PS London = CN_LONDON (same complex as the CN station; Brendan); C.N.R. - Wabash Depot = CN_ST_THOMAS.
- Drawing: new kind 'P', rail 'onlps', colour dark blue 1C2F5E with gold d4a62a (Brendan: L&PS livery dark blue and gold); drawConsist draws kind P as
  an interurban: four cars, no locomotive, gold band, nose on the leading car (the first use of the planned four-capsule interurban style).
- ab_table warns: estimated flag stops at the same minute as a timed neighbour (Crafts - Stop 19 - Whites, 2 min printed): cosmetic.

## Version 82 (28 October 2026): CP Table 68 Hamilton - Guelph Jct. - Guelph - Goderich
- on_cp_t068 (CP timetable 1948, Brendan's image; scan cp1948_on/t068.png): all MOTOR trains (sign: large dot; tagged kind=motor). 637 / 640 Hamilton (Hunter
  Street, THB_HAMILTON) - Waterdown - Guelph Jct. - Guelph - Elmira - Milverton - Goderich (ex Sun); Guelph Jct. - Guelph shuttles 643, 645, 647, 649 (ex Sat & Sun),
  651, 653 / 642, 644, 646 (Sat), 648, 650 (ex Sat & Sun), 652, 654. Miles: Hamilton branch as printed; Guelph Jct. - Goderich printed from Toronto, minus 19.9.
  Linwood by mileage.
- Connections NOT entered (Brendan, 28 Oct 2026: the Detroit / London - Guelph Jct. connecting trains wait for their own input if not already in): they ARE
  already in on_cp_t049w (Table 50): 21, 631, 629, 37 / 20, 630, 38, 22 at Guelph Jct.
- TO CHECK (on_cp_t049w, Table 50): No. 20 The Canadian. Table 68 prints it Detroit 2.55, LONDON 5.35, GUELPH JCT. 7.19, Toronto 8.30 a.m.; on_cp_t049w has
  Komoka 5.20 / 5.35 and Puslinch 7.19 with no London or Guelph Jct. call: probably a row slip in the Table 50 reading (London -> Komoka, Guelph Jct. ->
  Puslinch). Recheck against the Table 50 scan (cp1948 tw050a / tw050b).

## Version 83 (28 October 2026): CP Table 73 Mattawa - Timiskaming - Angliers
- on_cp_t073 (CP timetable 1948, Brendan's image; scans cp1948_on/t073.png, signs page27_signs.png): 49 / 50 ex Sun, Mattawa (CP Table 4 station) - Town Hall, Ont. -
  Timiskaming - Gendreau - Kipawa (spur: in and out) - Gendreau - Laniel - Fabre - Gaboury - Ville Marie (branch: in and out) - Gaboury - Lorrainville - Angliers.
  Gendreau and Gaboury printed twice (rows twice, like Pembroke Junction). Miles as printed.
- 50: Elma printed f8.09, impossible (Crest 8.04, 9.6 mi): estimated ~f8.26 (ask Brendan if his copy reads otherwise).
- Alias Timiskaming = the collection's 'Temiscaming'; Crest by mileage (the collection's point ~2 mi short). Mattawa - Timiskaming traced 42.5 mi, printed 37.9.
- Not entered: Chenier Bus Lines connections (Ville Marie - Belleterre, Rouyn, Noranda, New Liskeard).

## Version 84 (29 October 2026): CP Tables 63, 64, 65 (mixed branches off the Owen Sound line)
- Scan cp1948_on/t063_065.png. All mixed, daily except Sunday; the Toronto rows are the Table 62 connections (705 / 708), not entered.
- on_cp_t063: M747 / M748 Cataract - Erin - Fergus - Elora (continue to / from Orangeville in Table 62: run-through candidates). Fergus - Elora 2.4 mi in 65 / 50 min as printed.
- on_cp_t064: M715 / M716 Saugeen - Durham - Hanover - Walkerton.
- on_cp_t065: M753 / M756 Orangeville - Arthur - Mount Forest - Harriston - Wingham Jct. - Wingham - Glenannan - Teeswater. Wingham is a 4.5 mi branch: the
  trains run in and back out (the printed miles count both ways); Wingham Jct. row twice (the return call estimated ~). Hand points (Claude): CP Wingham (branch
  end), Wingham Jct. (branch junction by Glenannan), Cataract (where Table 62 had placed it by mileage).

## Version 85 (29 October 2026): CP Tables 69 and 69A (mixed)
- Scan cp1948_on/t069.png. All mixed, daily except Sunday; Toronto rows (Table 50 connections) not entered.
- on_cp_t069: M660 / M656 Woodstock - Ingersoll - Belmont - St. Thomas (M660 printed in the column headed "M660 / M655": its Woodstock - St. Thomas
  times). CP St. Thomas = the NYC (Michigan Central) station (Brendan, 29 Oct 2026): stop NYC_ST_THOMAS, shared with the L&PS N.Y.C. Depot; the CP trains run straight from the end of the CP line onto the NYC track to the station (link 'CP - NYC connection, St. Thomas': the NYC siding the CP line joins; drawn NYC). The first build had routed them through the yards and over CN and L&PS track (Brendan caught it).
- on_cp_t069b: M655 / M659 Woodstock - Ingersoll - Tillsonburg - Port Burwell (M655 Woodstock 10.00 from the first column, Ingersoll - Port Burwell from the second).
- on_cp_t069a: M681 / M682 Woodstock - Zorra - Embro - St. Marys (Woodstock - Zorra over the main line, 7.1 mi from Table 50; branch miles printed from Zorra).

## Version 89 (29 October 2026): CP electric lines, Grand River Railway and Lake Erie & Northern
- Sources: CP timetable 1948 Tables 66 / 67 (scan cp1948_on/t066_067.png), Official Guide 1948 GRR / L&N page and map (og1948_on/grr_len.png, grr_len_map.png);
  Canadian Electric Railway Mapping project KMZs (scans/cerm/) -> traces/ontario/brendan/grand_river.geojson (own 'grr': main lines, Kitchener Jct. wye and the
  left-fork private right of way to Queen Street, CPR Galt interchange; the Berlin & Bridgeport and Berlin & Waterloo street railways left out) and
  lake_erie_northern.geojson (own 'len', main line).
- Brendan (29 Oct 2026): CP properties, CP colours, drawn as interurbans (new kind 'E': four cars, no locomotive, CP colour, no band; rails 'ongrr' / 'onlen').
- GRR: on_grr_t066k / t066h: the Table 66 trains connecting with the CP at Galt, from / to the CP Galt station (stop CP_GALT, by the interchange wyes); each column
  is two trains, Galt - Preston - Kitchener (Queen Street; left fork at Kitchener Junction) and Galt - Preston - Hespeler (Brendan). Numbers = the CP trains they
  connect with, as headed. Up 631 = 38 and up 635 = 19 (same times): one train each. Hespeler trains' "Preston" entered at Joseph Street (the Hespeler line leaves
  before Preston station). on_grr_t000k / t000h: the Guide's hourly service RECONSTRUCTED (Galt :55 / Kitchener :10, Galt :25 / Hespeler :55, first / last cars
  as printed; running times estimated: Galt - Preston 10, Preston - Kitchener 25, Preston - Hespeler 12 min). Galt Main Street (GALT_MAIN_STREET) shared with the L&N.
  Miles: by distance between station points, scaled to the Guide / KMZ. Intermediate KMZ stations as flag stops (~f).
- L&N: on_len_t067: Table 67, 9 trains each way, unnumbered. All KMZ stops as flag stops (Brendan). Port Dover = the second station (1947 - 55, mile 50.3);
  Brantford Union station (L&N); L&N Waterford station (KMZ); Wilsonville printed mile 23.10, read 32.1 by position. Guide differences noted in the file.
- TO CHECK: the reconstructed hourly GRR pattern and running times; Joseph Street as the Hespeler trains' Preston stop.
- (29 Oct 2026, Brendan: "these tracks be styled as interurbans") page_template: track of owners lps / grr / len drawn as a SOLID line (no white dash),
  stations used only by interurban lines (kinds P, E) drawn as CIRCLES in the line colour; stations shared with a steam railway stay squares (Galt C.P.R.,
  N.Y.C. Depot St. Thomas). 

## Version 90 (29 October 2026): B.C. Electric in the uniform interurban style
- SAVED FIRST for a future "BCER system simulator" (Brendan): pipeline/archive/bcer_simulator/page_template_cd8a1b3.html + README (git tag bcer-simulator-base):
  the old BCER drawing (two-car Chilliwack trains, single local cars, double-track sides, passing-siding meeting halo), ink track, line-coloured station rings,
  five-ring legend, per-line "On the line" headings.
- Now (page_template): BCER track solid BCER red (Chilliwack and local lines alike); BCER stations red circles (no line colours); BCER cars drawn by drawConsist as
  the four-car interurban (inter = kinds P, E or any non-mainline train); legend: one "B.C. Electric" entry and one "Interurban station" ring; "On the line":
  one "B.C. Electric · N cars" heading (Chilliwack trains first, then the local cars). The planned four-capsule interurban cars are thereby done for all
  interurbans. Not carried over: the BCER double-track offset and the meeting halo (in the archive).

## Version 91 (29-30 October 2026): CN Quebec parts of the Maritime tables (Official Guide, April 25, 1948)
- Brendan: CP east of New Brunswick is done; start CN Maritime service, building only the Quebec parts. Scans (private og1948_cnq/): Table 1 (two pages), 1a, 23, 50,
  53, 54, signs. Script: scratchpad on/cn001.py.
- Brendan's answers (29 Oct): build the Quebec - Levis ferry now; start the Quebec lines at the N.B. boundary; build the branch trains over the parts shown;
  delete the CP-table holding files (on_cnpool_t033 = CN 1 - 4, 59, 60; on_cnvia_t038 / t039 = CN Tables 53 / 50): DELETED.
- on_cn_t001: N.B. boundary at the Restigouche (Matapedia) - Mont Joli - Riviere du Loup - Levis - Charny - Drummondville - St. Hyacinthe - Montreal (Central
  Station), Table 1 miles: 1 / 2 Maritime Express, 59 / 60 Scotian, 3 / 4 Ocean Limited, 31 / 32 Campbellton locals, 135 (RdL - Charny), 136 (Charny - RdL), 143,
  11, 23 / 16, 38. on_cn_t001q: 43 / 44 Quebec (Palais) - Charny - Chaudiere. on_cn_t001n: 241 (Sat), 141 / 142 Nicolet - St. Leonard - St. Hyacinthe (- Montreal).
  on_cn_t001a: 36 / 35 Matapedia - New Carlisle - Perce - Gaspe. on_cn_t023: 28-51, 67 / 27-52, 68 N.B. boundary - Monk - Charny - Quebec (ATLANTIC time to Monk,
  rows tz A). on_cn_t054: M255 / M256 Levis - Villeroy - Fortierville. on_cn_t050: Quebec - St. Raymond - Riviere a Pierre - Chambord - Chicoutimi (163, 211, 171,
  169, 161, 177 / 172, 162, 170, 164, 212); on_cn_t050m: 211 / 212 Montreal - Riviere a Pierre (no stations printed); on_cn_t050d: Chambord - Dolbeau sections
  (unnumbered, junction times estimated; D2 Dolbeau 11.55 p.m. reading UNCERTAIN). on_cn_t053: 176 / 175 (Tue - Sat), 173 (Sun) Quebec - Ste. Anne de Beaupre -
  Baie St. Paul - Murray Bay - La Malbaie (Ste. Anne mile 21.0 estimated; Pool 353 / 354 / 357 connections not entered).
- on_cnfy_t001 (rail 'oncnfy', kind v, drawn as a boat, GTFS route type 4; post-processed in on_build after build): Quebec - Levis ferry, one crossing per
  "Quebec (Via Ferry)" time printed in Table 1 (22 crossings, 10 - 12 min, estimated). Quebec wharf: Brendan's point; Levis: shared LEVIS stop.
- The new CN files are in on_build LATE, so the older trips keep their ids (CN 1 - 4 Continental, 11 / 12, 38 ...).
- Track: NTR Pelletier - St. Andre piece excluded (built after 1948; Brendan); links: NTR gap west of St. Isidore, Nicolet branch (collection piece dropped by the
  abandonment filter: Nicolet - wharf abandoned 1926, the rest 1955) and its tie at St. Leonard, ferry crossing. Hand points (APPROXIMATE, Claude): CN St. Hyacinthe
  (on the main line), Ste. Rosalie Junction, Ste. Rosalie, Bridge Street (Montreal), Nicolet, St. Charles (Bellechasse), Chambord (junction). Boundary points:
  Restigouche crossing (-66.93886, 47.97488), N.B. boundary on the NTR (-68.7317, 47.372). A&J Saguenay Power = CN Saguenay Power (shared).
- Doubts: 32 Luceville 3.20 - Mont Joli 3.25 (8.2 mi in 5 min, as read); 170 Valcartier 2.48 - Loretteville 2.55 (as read); R&S Arvida not shared with CN Arvida (ask).
- Not built: the N.B. parts of Tables 1, 1a, 23 (Maritime build); the CN pool trains Montreal - Quebec (Table 1 refers to another table, not in hand); the Sherbrooke
  and Nicolet line tables for 11 / 16 / 23 / 43 / 44.

## Version 92 (30 October 2026): CN Tables 51, 52, 55 (the last page of the CN Quebec tables)
- on_cn_t051: Rutland trains 52 / 51 The Mount Royal, 64 / 65 The Green Mountain Flyer, Montreal (Central) - St. Johns - Cantic - international boundary (to Rouses
  Point, N.Y.). on_cn_t051v: Central Vermont trains 20 The Washingtonian / 21 The Montrealer, 332 / 307 The Ambassador, Montreal - St. Johns - Cantic - boundary
  (to East Alburgh, Vt.). on_cn_t051i: 606, 608 / 605, 607 Montreal - St. Johns - Iberville (for Waterloo; that table not in hand). on_rut_t018.csv (CP Table 18
  Rutland ends-only) DELETED: the same trains. Hand: St. Johns, Cantic (= the collection's Lacolle Junction). Boundary points: ends of the collection's Rouses
  Point subdivision and Coteau & Province Line track. St. Johns - Iberville: a short straight (no bridge track in the collection).
- on_cn_t052: Richmond - Victoriaville - Lyster - Charny - Quebec: 42, 44, 46, 48 (Sun) / 41, 43, 45, 47 (Sun). Montreal times (connecting trains on the Montreal -
  Richmond line, = Table 1's 16 / 11 / 23 numbers on the Sherbrooke line) in the notes. on_cn_t001q (43 / 44 partial) DELETED. Richmond: Richmond, Que. (places).
- on_cn_t055: 193, 195 / 194, 196 Chambord - Roberval - St. Felicien - Dolbeau (confirms the 11.55 p.m. Dolbeau arrival = No. 195, from Chambord 9.50 p.m.).
  on_cn_t050d (estimated Dolbeau sections) DELETED.

## WAITING: Quebec Railway, Light & Power (Brendan, 30 Oct 2026)
- In 1948 the CN Murray Bay trains (Table 53: 176 / 175, 173) ran over the Quebec Railway, Light & Power Co. (Quebec - Ste. Anne de Beaupre - Murray Bay) by running
  rights; the collection shows it as CN because CN bought it in 1951. Brendan will upload the QRL&P's own information. When it goes in: the QRL&P track drawn as
  an interurban (its own railway, solid track, circle stations where it alone calls), the CN trains over it still drawn as ordinary CN trains.

## Version 93 (30 October 2026): CN Tables 59 (Quebec part), 59a, 60, 60a
- Scans (Brendan, 30 Oct; Timetable World screenshots of the Official Guide, May 1948 issue, tables dated April 25, 1948): Table 59 (three views), 59a, 60 / 60a,
  signs. Script: scratchpad on/t059.py.
- on_cn_t059: Montreal (Central) - St. Hyacinthe - Richmond - Sherbrooke - Coaticook - international boundary (129.4, the end of the collection's St. Lawrence &
  Atlantic track just short of Norton, Vt., 129.5; boundary times estimated). 25 trips. Down: 30 (Mon - Fri, Montreal - Ste. Rosalie) / 230 (Sat night, on to
  Richmond), 112 (Sun) and 12 (to Island Pond), 24 (to Sherbrooke), 124 (Sat, to St. Hyacinthe), 22 (Sun, to Actonvale), 218 (Sun, to Coaticook), 16 (Mon - Fri)
  / 126 (Sat, express beyond Richmond), 10 (Mon - Fri, to Richmond) / 210 (Sat, on to Island Pond), 602 (Richmond - Sherbrooke). Up: 17, 27 and 37 (from Ste.
  Rosalie), 601 (Sherbrooke - Richmond), 29 (Sun, from Richmond), 11, 111 (Sun), 9 (Mon - Fri, from Richmond) / 209 (Sat, from Island Pond), 39 (Sun, from
  Actonvale), 117 (Sun, from Coaticook), 23 (from Sherbrooke).
  - Model week: e and h as in summer (July 3 - Sept 4): No. 16 beyond Richmond Mon - Fri, 126 and 209 Saturdays. c, n, x, y conditional stops entered as flag stops.
  - ASSUMED: No. 17 daily except Sunday (the Portland end of its column, where the sign is, is not in the scans; its Quebec connection is ex Sun and No. 117 runs
    Sundays). 12: dagger (daily except Sunday), confirmed by Brendan.
  - The Quebec rows (Sherbrooke - Quebec passengers by the Table 52 trains at Richmond) are in the notes. U.S. part (Grand Trunk, Island Pond - Portland) not built.
- on_cn_t001: Nos. 11, 16, 23 removed (now whole in t059); St. Hubert - St. Hilaire rows added for No. 38 (Table 59 times). on_cn_t001n: the same rows; 241 Beloeil
  3.34 p.m. 241 is in Table 59 too: kept in t001n only.
- on_cn_t060a: Coteau - Soulanges - Valleyfield motor trains, 620 - 640 / 619 - 639 (crescent-sign trains 633 - 635, 634 - 638: Sunday trains that run on Mondays May 24 and Sept. 7 instead of Sundays May 23 and Sept. 6; Sundays in the model week, Brendan confirmed). on_cn_t075v (Valleyfield sections read from
  Table 75) DELETED: the same service.
- Table 59a (pool trains Montreal - Quebec): all duplicates, NOT entered: the pool trains 349 - 362 are built from CP Table 33; the CN columns are CN 1 - 4, 59, 60
  (Table 1) with the Levis ferry. Its ferry times differ from Table 1's by up to 10 min in places (e.g. No. 4: Quebec 11.50 p.m. vs 11.55); left as built.
- Table 60 (Danville Jct. - Lewiston, Maine): wholly U.S., not entered.
- Track: the collection's St. Lawrence & Atlantic main line Richmond - border doubles back for about 1.4 km south of Compton (trace 1.9 mi too long): replaced by a
  link without the doubled stretch. Ste. Rosalie: the St. L. & A. and the Drummondville line run 24 m apart from the junction past the station; a short link ties
  them at the station (one Ste. Rosalie stop for both lines; CP Table 22's Ste. Rosalie is the CP station, separate). Hand: CN Sherbrooke = the Grand Trunk station
  on rue du Depot (Brendan's point, 45.40055, -71.88820; the CP station is separate, about 850 m away, heritageguide.ca).
- Side effect: CP Table 8 at Lennoxville (where the CP crosses the St. L. & A.) no longer runs out and back north of the station: 0.8 mi shorter. Check on the map.

## Version 94 (30 October 2026): CN Tables 61 (Montreal suburban, Lakeshore) and 63 (Montreal - L'Epiphanie - Rawdon); page 1120
- Scans (Brendan, 30 Oct): Official Guide page 1120 (Tables 61, 63, signs). Script: scratchpad on/t061.py.
- on_cn_t061: suburban trains, Montreal (Bonaventure Station) - St. Henri - Lachine - Ste. Anne de Bellevue - Vaudreuil (and 25, 255, 261 / 26, 270 to and from
  Coteau). 32 trips: down 225, 227, 235, 237 (Sun), 249, 251, 255 (Sat), 253 (Sun), 259, 261 (Mon - Fri), 25, 263, 265, 271, 279, and the two "additional local
  trains" (Sat, Bonaventure 11.15 a.m. and 1.30 p.m. to Vaudreuil, ends only printed; unnumbered); up 226, 236, 238, 242, 244, 26, 252 (Sun), 254, 256, 262 (Sat),
  272, 274, 270 (Mon - Sat from Coteau) / 280 (Sun from Vaudreuil), 284. Bonaventure Station: the collection's point (Grand Trunk). Miles as printed (from Central
  Station; St. Henri 1.5 from Bonaventure), so Bonaventure - Lachine is shorter than the miles say.
  - No. 26: its dagger is printed at the Valleyfield (motor train) time: taken as daily except Sunday.
- on_cn_t061c: the Central Station trains of Table 61 that are not in Table 75, Montreal - Coteau only: 5 The La Salle (pool), 19 / 18, 14 The International
  Limited (pool), 78 (May 30 - Sept. 19; from beyond Coteau, origin not in the table). TO REPLACE with the CN Montreal - Toronto table (cf. on_cnpool_t049, held).
- on_cn_t075a: rows Pointe Claire, St. Dominique, Wilsonvale added from Table 61 (47, 48, 51, 152, 153); "Cedar-Cedres" corrected to Cedars-Cedres.
- on_cn_t063: Montreal (Central) - Mount Royal - Pointe aux Trembles - L'Epiphanie - Rawdon: 206 (Sun), 210 (Sat), M202 (mixed, Mon - Thu), 208 (Fri), M201 (mixed),
  205 (Sun); and the parts shown of the Joliette-line trains 110, 114, 216, 116 / 115, 215, 113, 109, 209 (to / from L'Epiphanie or Pointe aux Trembles; the rest
  not in hand). St. Alexis and Hamilton entered as "St. Alexis de Montcalm" and "Hamilton, Que." (stop ids apart from CN St. Alexis, Matapedia, and Hamilton, Ont.).
  CN L'Epiphanie kept separate from CP L'Epiphanie (ask Brendan if they shared a station).
- Track and places (corrected same day, Brendan): until 1961 the CN main line ran from Turcot West through Lachine station on the old Lachine line to Dorval;
  the Turcot West - Dorval line in the collection is the 1961 bypass. The two collection main-line pieces are replaced by copies that follow the old line between
  those junctions (links 'Grand Trunk main line in 1948'); the collection's Lachine station stands (no hand point). St. Dominique by its mileage (its point snaps to the other track of the double main line, which
  broke the Coteau fit). Many Lakeshore stations have no CN point in the collection (or only the CP's): placed by mileage.

## Version 96 (30 October 2026): CN Tables 64, 65, 66, 68, 70, 72 (Official Guide page 1121)
- Scans (Brendan, 30 Oct): page 1121 (Tables 64, 65, 66, 68, 70, 72; signs with Table 65). Script: scratchpad on/t064.py (t061.py must NOT be rerun as is: on_cn_t063.csv
  was edited after it, see below).
- on_cn_t064: Montreal - L'Epiphanie (Table 63 stops) - Joliette - Shawinigan Falls - Garneau - Hervey - Riviere a Pierre: 116 (Mon - Sat) / 216 (Sun) to Riviere a Pierre
  (the Montreal sections of 11 and 211), 114 to Hervey, 110 to Garneau, 698 Garneau - Hervey (Mon Wed Thu Fri, as Table 38); 115 (Mon - Sat) / 215 (Sun, all stations)
  from Riviere a Pierre, 113, 109, 209 (Sun) from Garneau, 697 Hervey - Garneau. on_cn_t064q: Garneau - St. Stanislas - St. Prosper - Portneuf - Quebec: 108 (Tue Thu Sat,
  sign b; Table 38 had it daily except Sunday), 107 (Mon Wed Fri).
  DELETED: on_cn_t038m, on_cn_t050m (Montreal - Hervey / Riviere a Pierre with no stations). on_cn_t038q: 107, 108, 697G, 698G and its Garneau row removed (Table 38 had
  put Garneau on the St. Prosper - Hervey line; it is on the Shawinigan line), Ecureuils and Portneuf rows added for 11 / 12. on_cn_t063: the Joliette-line columns
  (110, 114, 116, 216 / 109, 113, 115, 215, 209) removed (now whole in t064).
- on_cn_t065: Montreal - Longueuil - Sorel - Pierreville - Nicolet - Des Ormeaux - Trois Rivieres (Ferry): 138 / 137, motor trains 646 / 645 (Montreal - Nicolet). The
  "Trois Rivieres (Ferry)" end is the south-shore landing (end of the collection's track opposite Three Rivers); the printed times there seem to include the river
  crossing (Des Ormeaux - landing 1.8 mi in 25 / 45 min). The ferry itself is NOT built (ask Brendan).
- on_cn_t066: Sorel - Bellevue Jct. - St. Hyacinthe, mixed M268 (Tue Thu Sat) / M267 (Mon Wed Fri). St. Hyacinthe for these trains: the United Counties line's nearest
  point (1.7 km from the CN main-line station; the collection has no tie between them). ASK Brendan where they stopped.
- on_cn_t068: Montreal - Laprairie - St. Isidore Jn. - Ste. Martine - Howick - Huntingdon - boundary (to Fort Covington, N.Y.): 80 / 79 (ex Sun). on_cn_t068h: St. Isidore
  Jn. - St. Remi - Hemmingford mixed M200 (Tue Thu Sat) / M197 (Mon Wed Fri), and M198 / M199 St. Isidore Jn. - St. Remi. Beauharnois (passengers on freight) and
  Fort Covington - Massena (freight) not entered.
- on_cn_t070: Montreal - Fresniere - St. Jerome - Montfort - Huberdeau - Lac Remi; seasonal days read for the model week: 99 Sat + Sun, 97 / 95 Sat, 91 Mon - Fri, 93 Fri,
  90 Mon, 92 Tue - Sat, 94 Sat + Sun, 98 Sun, 100 Tue - Sun.
- on_cn_t072: Montreal - St. Johns - Iberville - (CP) Farnham - Granby - Waterloo: 606, 608 / 605, 607. Iberville: arrives at the C.V. station, leaves from Iberville
  (C.P.R.) = CP_IBERVILLE; Farnham Union Station = CP_FARNHAM (SHARED). on_cn_t051i DELETED (same trains to Iberville only).
- (Version 100, Brendan) Table 72 trains rerouted Iberville - Farnham over the CN (the collection's Stanstead, Shefford & Chambly main line St. Jean - Farnham, which
  also gives St. Johns - Iberville track: no more straight estimate). The two printed Iberville rows (arr. C.V. station 23.9, lve. Iberville 25.3 with "C.P.Ry.")
  are one stop with arr / lv times; the CP_IBERVILLE sharing and place were removed. Farnham (Union Station) still CP_FARNHAM.
- Renamed for unique stop ids (the id drops ", Que." and brackets only for matching): St. Boniface (Shawinigan), St. Louis (Richelieu), St. Isidore (Laprairie),
  Hamilton (Montcalm) (Table 63's, was "Hamilton, Que.").
- Track: links for the old CN main line through Mirabel (Deux Montagnes tie, St. Jerome tie, straight 1.3 km APPROXIMATE) and the Lake St. Louis & Province line
  St. Isidore Jn. - Hemmingford (the collection piece was dropped by the abandonment filter). Hand points (APPROXIMATE): CN Sorel (end of the Montreal - Sorel main),
  St. Isidore Junction, Lac Remi. Aliases: CN Shawinigan Falls = the collection's Shawinigan; Garneau = Garneau Junction.
- Open: CN and CP stations at Joliette, Shawinigan Falls, Garneau, St. Jerome, Waterloo, Granby kept separate (ask if any were shared).

## Version 97 (30 October 2026): Napierville Junction Railway (D&H)
- Brendan: the collection's CP Lacolle subdivision (Delson - Lacolle - Rouses Point) was in 1948 the Napierville Junction Railway, a Delaware & Hudson subsidiary.
  Link 'Napierville Junction Railway, Delson - Rouses Point (boundary)' (own dh, replaces the collection piece): drawn in D&H colour.
- NJR table (Official Guide, April 25, 1948; scan p1121_njr.png): on_dh_t018 now has St. Mathieu, St. Edouard, Napierville, Lacolle and CP Delson (shared CP_DELSON)
  with the NJR times; boundary times from the Rouses Point times (No. 34's had been estimated too late). No. 37 renamed No. 35: the NJR table shows No. 35 from
  June 6 with the times in the file (No. 37 last ran June 5). Miles Delson - boundary measured along the collection track. on_dhfull_t018 (held, not built)
  still says No. 37.

## Version 98 (30 October 2026): Brendan's answers on page 1121
- L'Epiphanie: CN and CP are different stations (as built). Stations printed separately for CN and CP stay two stations (Brendan's presumption).
- Sorel - St. Hyacinthe trains run to the main CN station: the United Counties line joins the main line west of St. Hyacinthe without a tie in the collection;
  link 'St. Hyacinthe: United Counties line to the main line' (162 m) added, the t066 place override removed (traced 37.0 mi, printed 36.8).
- CN Sorel station: Brendan's point (46.038944, -73.113775).
- Trois Rivieres ferry BUILT: on_cnfy_t065 (rail oncnfy, drawn as a boat like Quebec - Levis): two crossings, Three Rivers 4.30 p.m. (for No. 137) and to Three
  Rivers 11.45 a.m. (from No. 138), as printed; the landing times and the Three Rivers wharf point (-72.5385, 46.3425) are estimates. Table 65's "Trois Rivieres
  (Ferry)" rows now carry estimated landing times (138 ~ar 11.25 a.m., 137 ~lv 5.05 p.m.). BOXES['cnfy'] widened to take in Three Rivers.
- (later, Brendan) Three Rivers terminal at his point (46.340631, -72.538617); the ferry is the Compagnie de la Traverse du Saint-Laurent Ltee and is now SIMULATED as
  continuous summer service: two boats (Cite des Trois-Rivieres, 1930 - 1949, and Laviolette, per Brendan's source; the Laviolette's 1948 date not checked), a departure
  from each side every 30 min, 6.00 a.m. - 11.30 p.m. daily, 15-minute crossing (72 crossings; vessel names from the trip notes, shown on the page). Meets 138 (11.30
  boat) and 137 (Three Rivers 4.30 p.m.). Sources: troisrivieresnumerique.ca (Traversier Cite des Trois-Rivieres), patrimoinebecancour.com (La Grand Riviere).

## Version 101 (30 October 2026): the two ferries as their own companies
- Brendan: neither ferry is a CN service. Quebec - Levis: Quebec & Levis Ferry Co. (rail 'onqlf', agency QLF, file on_qlf_t001.csv); Three Rivers: Compagnie de la
  Traverse du Saint-Laurent Ltee (rail 'ontsl', agency TSL, file on_tsl_t065.csv). Rail 'oncnfy' and the on_cnfy_* files are gone (both new rails share the 'cnfy'
  graph). Page: liveries qlf (#34506b, funnel red) and tsl (#5a4a7a, funnel gold), Claude's picks; GTFS route type 4.
- Quebec - Levis rebuilt from Brendan's company pamphlet (summer): every 20 min 5 a.m. - midnight, every 30 min midnight - 1 a.m., hourly 1 - 5 a.m. Departures from
  Quebec at :00 / :20 / :40, from Levis at :10 / :30 / :50 (the pattern of every CN-printed ferry time). The CN times 4.20 a.m. (Quebec) and 4.30 a.m. (Levis) put the
  start of the 20-minute service at about 4.20. Night: Quebec 12.30, 1.00, 2.00, 3.00, 4.00; Levis 12.10, 12.40, 1.40, 2.40, 3.40 (3.40 CN-printed). Crossing 12 min
  (estimate). 129 crossings a day. Boats: three in the 20-minute service (Quebec :00 -> Levis :12, out of Levis :30 -> Quebec :42, out again at :00: an hour round
  for each boat), two in the half-hourly hour, one at night. Vessel names not known (not shown).

## Version 102 (30 October 2026): CN page 1124 - Tables 76, 77, 77a, 78, 78a
- Scans (Brendan, 30 Oct): page 1124 (p1124_*.png). Script: scratchpad on/t076.py.
- on_cn_t076: Ottawa (Union) - Arnprior - Renfrew - Golden Lake - Barrys Bay - Madawaska - Whitney: 89 (Mon - Sat) / 90 (Mon - Sat, on to Montreal as No. 50), 389 (Sat) / 390
  (Sun), mixed M219 / M220 (Fri) and M221 / M222 (Tue) Barrys Bay - Whitney. on_cn_t076p: Golden Lake - Pembroke connections printed in the 89 / 90 columns (numbered
  89 / 90: see the to-do on connecting-train numbers). Rock Lake and Two Rivers printed with no trains.
- on_cn_t078: Algonquin Park - Scotia - Parry Sound: 139 (MWF, June 28 - Sept. 6) / 140 (TThS, June 26 - Sept. 4) Algonquin Park - Scotia; 264 (MWF, June 28 - Sept. 3)
  Parry Sound - Scotia; mixed M263 (Sat) Algonquin Park - Scotia - Parry Sound. M264 (Mon, Fri) "will not run June 28 to Sept. 3": not entered. DOUBT: M263 has no such
  mark and is entered. on_cn_t126g (Algonquin Park sections read from Table 126) DELETED. Link: OA&PS main line without a stray vertex near Edgington (12 km spike).
  OA&PS Parry Sound / South Parry = the CN stations of Table 122 (same points in the collection).
- on_cn_t078a: Glen Robertson - Vankleek Hill - Hawkesbury, mixed M217 / M216 (Mon - Sat). Link: Vankleek line tied to the main line at Glen Robertson (273 m).
- on_cn_t077a: Montreal - Val Royal - St. Eustache-sur-le-Lac - Fresniere - St. Benoit - Grenville - Hawkesbury: 81 (Mon - Fri), 85 (Sat), 83 (Sun) / 82 (Mon - Sat),
  84 (Sun), with Table 77's suburban stops. Link: Hawkesbury station piece tied to the L'Orignal subdivision (about 380 m). Hawkesbury is one CN station for 77a and 78a.
- on_cn_t077: Montreal - Mount Royal - Val Royal - St. Eustache-sur-le-Lac - Pine Beach - Roger Beach - St. Joseph du Lac - Calumet Beach: 49 trips, nearly all motor
  trains; Calumet Beach service June 20 - Sept. 4. Trains whose Calumet part runs on fewer days are entered twice (S = the other days, to St. Eustache only: 359, 361,
  358, 360, 368). Unnumbered: the "additional trains" (Montreal 5.00 p.m. ex Sun, 8.15 p.m. Sun; St. Eustache 9.20 p.m. Sun) and the Saturday St. Eustache 2.00 p.m.
  - Calumet Beach run printed in No. 85's column. St. Eustache-sur-le-Lac = the collection's "St. Eustache (Junction)" station (Deux-Montagnes); Calumet Beach placed
  at Pointe-Calumet on the collection's "Pointe Calumet gravel pits spur" (APPROXIMATE, by the printed 5.6 mi).
- on_cn_t070: Mount Royal, Val Royal, Bigras Island, Laval sur le Lac, St. Eustache-sur-le-Lac rows added from Table 77 for 91, 92, 100.
- (Version 103, Brendan) Track gap on the tunnel line between Monklands and the Vertu wye: a long straight route stretch straddling the start of a line's own
  (not-shared) segment took the 'none' owner of its midpoint and went undrawn. page_template.html now cuts each route stretch at segment boundaries before
  splitting the track into owner runs (page only; ab_lines' own 'drawn' bookkeeping for later lines still works point by point: to fix if it bites).

## Version 104 (30 October 2026): CN page 1125 - Tables 79, 79a, 80, 81a, 81b, 81f
- Scans (Brendan, 30 Oct): page 1125 (p1125_*.png). Script: scratchpad on/t079.py.
- on_cn_t079: Toronto (Union) - Sunnyside - Oakville - Burlington - Hamilton (James St.): down 77, 101, 17 The Inter-City Limited, 73 (Sat), 85 (Sat), 83, 183 (Sun),
  79, 81 (Mon - Fri), 5, 89 The Maple Leaf, 15 The International Limited, 187 (Sat night), 9; up 74, 76, 94 The Maple Leaf, 14 The International Limited, 80,
  6 The Inter-City Limited, 92, 18, 108, 16. Montreal times (the CN Montreal - Toronto table, not in hand; 15, 187, 9 from Windsor Station) in the notes.
- on_cn_t079n: Hamilton (James St.) - Grimsby - St. Catharines - Merritton - Niagara Falls, Ont. - boundary on the bridge to Suspension Bridge, N.Y. (the end of the
  collection's Great Western main line): 102, 86, 186 (Sun), 90 The Maple Leaf, 184 (Sun, from 187), 84 (to Niagara Falls) / 93 The Maple Leaf, 95, 91, 107. The number
  changes at Hamilton (101/102, 83/86, 183/186, 89/90, 187/184; 93/94, 95/6, 91/92, 107/108): separate trips until the run-through join. U.S. connections in the notes.
- on_cn_t079a: Victoriaville - Aston Jct. - St. Gregoire - Des Ormeaux - Ferry Wharf (= the Trois Rivieres (Ferry) stop of Table 65): 137 / 138. They are the same
  numbers as Table 65's Montreal - wharf trains: 138 Montreal -> wharf -> Victoriaville, 137 Victoriaville -> wharf -> Montreal, reversing at the wharf (join later).
  on_cn_t065: the wharf row moved to 91.7 mi (Table 79a: 0.4 mi past Des Ormeaux); 137's wharf departure ~5.10 p.m.
- on_cn_t080: Brockville (Union) - Athens - Forfar - Westport mixed M335 (Tue Thu Fri), M339 (Wed Sat, Forfar - Westport) / M336 (Tue Fri, Westport - Forfar), M340 (Sun Tue Thu).
- on_cn_t081b: Forfar - Sydenham - Yarker - Napanee mixed M445 / M446 (Mon - Sat), M337 (Tue Fri) / M338 (Wed Sat).
- on_cn_t081f: Picton - Trenton - Trenton Jn. - Belleville mixed M353 / M351 (MWF; printed 353-354, 351-352). Trenton Jn. miles not printed (32.0 estimated).
- on_cn_t081a: Madoc - Madoc Jct. - Belleville mixed M364 / M365 (TThS).
- Track: links for the Great Western main line Hamilton - Niagara Falls and the Madoc subdivision Madoc Jct. - Madoc (both dropped by the abandonment filter because
  their notes mention later abandonments). Places: Hamilton (James St.) = the collection's '2nd Hamilton station' (-79.86457, 43.26584; Brendan); boundary at the end of the GW main line at the Niagara River bridge (-79.05833, 43.10923); CN Burlington on the main
  line at the junction (Freeman), by the printed miles (the collection's Burlington is on the old branch to the lake), APPROXIMATE. Sunnyside: one station with the CP
  trains (CP_SUNNYSIDE, SHARED). St. Catharines and Niagara Falls, Ont. by their mileage (their points did not fit the track).
- (Versions 105 - 106, 31 Oct, Brendan) Trenton station is off the main line; the main-line trains called at Trenton Junction. Brendan's point (44.09969, -77.57823,
  on the collection track where the Trenton subdivision, Central Ontario and Rideau subdivision lines meet) is TRENTON station (CN hand point); Trenton Junction is
  the collection's point on the main line. (Version 105 had them the wrong way round.)

## Version 107 (31 October 2026): CN Table 82 Montreal - Toronto (pool trains) and the Thousand Islands Railway
- Scans (Brendan, 31 Oct): Table 82 (two halves) and the pool-train signs. Script: scratchpad on/t082.py.
- on_cn_t082 (Montreal Central - Toronto Union): down 77 (Sun Tue Thu, May 30 - Sept. 19, Montreal - Prescott wharfs), 17 The Inter-City Limited, 19, 5 The La Salle,
  9 (Mon - Fri, Belleville - Toronto), 109 (Sun, Belleville - Toronto), M445 (Napanee - Belleville, from Forfar); up 14 The International Limited, 10 (Mon - Sat,
  Toronto - Belleville), 18 (Mon - Sat) and 118 (Sun, on as 18 from Brockville), 16 The Maple Leaf, 78 (Sun Tue Thu), M446 (Belleville - Napanee).
  on_cn_t082b: 25 / 26 Montreal (Bonaventure) - Coteau - Cornwall - Brockville (all stations). NOT ENTERED: pool 15 / 6 (Windsor Station, on_cpcn_t049) and 21 / 22
  (via CP lines, on_cp_t050). Ottawa connections (by Coteau, Table 75; Ottawa - Brockville), Valleyfield, Prescott - Ogdensburg ferry: in the notes.
  DELETED: on_cn_t061c (5, 14, 18, 19, 78 Montreal - Coteau) and on_cnpool_t049 (held pool trains). Conditional stops as flag stops.
- Thousand Islands Railway (rail 'ontir', kind K, agency TIR, colour #7a5a2e Claude's pick; on_tir_t082.csv): Gananoque - Gananoque Junction over its own line to
  Thousand Islands Jct. and the CN from there; Gananoque Junction = the CN station (shared stop). 8 unnumbered daily trips named "Susan Push", at the Gananoque times
  printed in Table 82 (Via T.I.Ry.) with junction times estimated (~15 min): 12.20 / 1.10 p.m. (No. 5), 1.20 / 2.15 p.m. (No. 14), 12.30 / 1.15 a.m. (No. 19; DOUBT: 1.15
  arrival only 7 min after the train's 1.08), 1.40 / 2.40 a.m. (Nos. 18 / 118). One engine covers all eight.
- Track: Cornwall - Cardinal is the pre-Seaway line (flooded 1958); the collection's pieces for it are crude (vertices up to 12 km apart), so Cornwall - Wales and
  Aultsville - Morrisburg are drawn as straight estimates. Mille Roches, Moulinette, Cardinal have no points (by mileage). Port Hope - Newcastle traces 17.6 mi for 15.6
  printed: CHECK the route there.
- Kingston (Brendan): the 1948 station is at 44.25389, -76.48477 (the collection's point, CN_KINGSTON, used by the pool and CN trains); the later VIA station further west did not exist.
- (Version 108, Brendan) Pre-Seaway main line: CN Cornwall = the collection's '1st Cornwall station', Morrisburg = '1st Morrisburg station', Cardinal = Cardinal/Edwardsburg
  (hand points; Iroquois by mileage, its point is the relocated town's). CN Tables 82 / 82b and the CP pool trains 15 / 6 (on_cpcn_t049) now run on the old line
  Cornwall - Cardinal. Aultsville - Morrisburg stays a straight estimate (the collection's old-line trace is very coarse there). St. Catharines (Great Western
  station; the other point was the Welland Railway's) and Niagara Falls, Ont. (GW station) now hand points; Niagara Falls - boundary 0.2 mi straight (the GW
  main line ends at the station).

## Version 109 (31 October 2026): CN Tables 90 (Toronto - London - Windsor / Sarnia) and 91 (Trenton - Maynooth); page 1127
- Scans (Brendan, 31 Oct): page 1127 (Tables 90, 91, 92 header; signs). Script: scratchpad on/t090.py (reads the Table 79 cells; on_cn_t079.csv was trimmed by it: do not rerun).
- on_cn_t090: Toronto - Hamilton (James St.) - (back out by Bayview Jct.) - Dundas - Brantford - Paris - Woodstock - London, whole trips with Table 79's Toronto - Hamilton
  stops: down 15 The International Limited, 5 The La Salle, 83 (ex Sun), 183 (Sun), 73 (Sat), 77 (ex Sun), 17 The Inter-City Limited, 9; up 14, 80, 6, 18 (ex Sun), 118 (Sun),
  16 The Maple Leaf. Their Table 79 columns REMOVED from on_cn_t079 (left there: 101, 85, 79, 81, 89, 187 / 74, 76, 94, 92, 108).
  on_cn_t090b: 75 (printed 75-83), 82, 20 The Ontario Limited: Toronto - Bayview - Dundas - London, not calling at Hamilton.
- on_cn_t090w: London - Glencoe - Chatham - Walkerville - Windsor: 105 La Salle, 83, 183, 117 Inter-City, 9 / 10 International, 12 Inter-City, 18, 118, 16 Maple Leaf.
  Windsor - Detroit (1.6 mi in about 45 min: across the river) NOT built, Detroit times in the notes: ASK Brendan (car ferry or tunnel).
- on_cn_t090s: London - Strathroy - Wyoming - Sarnia - boundary in the St. Clair Tunnel: 15, 5, 17, motor 605, 621 / 14, 6, 20, motor 606, 620. Petrolia: bus connections
  (not built); Table 92 (Wyoming - Petrolia) body not in the scans.
- Trains that split or change number at London (5 / 105, 17 / 117, 75 / 83, 12 / 6, 10 -> via Stratford) are separate trips per section (run-through join to-do).
- on_cn_t091: Trenton - Trenton Jn. - Marmora - Bannockburn - Ormsby Jn. - Coe Hill - Bancroft - Maynooth mixed: M313 (MWF, Trenton - Bancroft), M315 (Fri), M321 (Wed)
  Bancroft - Maynooth / M314 (TThS, Bancroft by Coe Hill to Trenton; Coe Hill arrival estimated), M316 (Sat), M320 (Wed). Miles run through the Coe Hill branch and back.
- Track: the Great Western main line London - Windsor (8 collection pieces) re-added as links (dropped by the abandonment filter; piece 23 London - Chatham is very coarse,
  trusted); pre-Seaway line Cornwall - Cardinal: the collection's eastbound and westbound pieces replaced by one line (they never met, so Aultsville - Morrisburg was a
  straight; Brendan: trust the file, it was very straight). Places: Windsor = the GW station at the river; Sarnia station; boundary at the end of the Sarnia branch
  (APPROXIMATE, 0.3 mi from Sarnia for 1.5 printed); Chatham, Brantford, Marmora by mileage.

## Version 110 (31 October 2026): CN Tables 98, 99, 100, 103 (the page after 1127)
- Scans (Brendan, 31 Oct): Tables 95 (Port Huron - Chicago: US only, not built), 98, 99, 100, 103 and the signs. Script: scratchpad on/t098.py.
- on_cn_t098: Beeton - Alliston - Creemore - Collingwood mixed M391 / M394 (ex Sun).
- on_cn_t099: Palmerston - Listowel - Wingham (CN, not the CP station) - Lucknow - Kincardine: 177, M331 / 176, M332 (ex Sun). Kincardine placed at the end
  of the collection's branch (no station point there; APPROXIMATE).
- on_cn_t100: Lindsay - Fenelon Falls - Kinmount - Howland - Gelert - Haliburton: 393 (Sat, summer), 89 The Highlander (Sat), M395 (Tue Thu), M389 (MWF; Lindsay - Watsons
  times not printed, taken from 391 as estimates) / M388 (printed a = MWF; ASK), M392 (Sat), 87 The Highlander (Sun).
  on_cn_t100b: Lindsay - Howland - York River - Bancroft (the old IB&O, joining the Central Ontario line at York River): M391 (Tue Thu; Sat leaves Howland 3.40), M323 (TThS).
  The branch miles are printed FROM HOWLAND (York River 50.9, Bancroft 53.7); entered from Lindsay. Howland - York River takes about 4 1/2 hours each way as printed.
  Names: Kinmount (Victoria) = CN_KINMOUNT_ONT (CN_KINMOUNT is the Minnesota one); Richmond (Carleton) = CN_RICHMOND_ONT (not Richmond, Que.); Lindsay at the CN (Victoria Railway) station, not CP_LINDSAY; Howland = Howland Junction station.
- on_cn_t103: Ottawa (Bank Street) - Richmond - Smiths Falls (C.N. Station) - Portland - Forfar mixed M445 / M446 (ex Sun; on to / from Napanee in on_cn_t081b). The Table 103
  pool trains are already in the CP files.
- To come from Brendan: the Windsor - Detroit CN car ferry details (Brendan: it is a CN ferry in this era); points for Chatham, Brantford, Marmora, Bronte, the Sarnia tunnel border.
- FOUND (31 Oct): stop ids shared by two far-apart stations of the same name (the feed sends trips to the wrong place): CN_ROSEDALE, CN_ARMSTRONG, CP_HAMMOND,
  CP_STRATHMORE, CP_BROOKS, CP_ERSKINE, CP_BUFFALO, CP_ROSEDALE, CP_GLENWOOD, CN_STE_ANNE, CN_CARDINAL, CN_ELGIN, CN_LAURIER, CP_DOUGLAS, CP_OGEMA, CP_GLADSTONE,
  CP_DRAKE, CP_ROCKHAVEN, CP_EAU_CLAIRE, CP_LAKESIDE (and near-twins CP_MCAULEY, CP_ROSETOWN_JCT). Kinmount and Richmond fixed in Version 110; the rest: offered to
  Brendan as one general fix (a distinct id when the same name is more than about 5 km away).
- Version 111 (31 Oct): split_stops.py (run at assembly after merge_stations): a stop id used by places more than 5 km apart gets one id per place (old id + line key,
  e.g. CN_CARDINAL_ONCN082); names on the page unchanged (Brendan: unique ids, not visible). 21 split; the B.C. place keeps the old id. 5522 stops.
- Windsor - Detroit (Brendan, 31 Oct): a CN TRAIN FERRY, coaches roll on and off to CN's Detroit terminal (Brush Street). Model: the Table 90 Windsor trains carry on over
  the river on a water crossing line (no boat, no track drawn), with holds for loading / unloading, to the border. CN had no tunnel access; buses only from 1955.
  BUILT in Version 112 (below).

## Version 112 (31 October 2026): Windsor - Detroit CN train ferry
- Brendan's KMZ (USGS quad 1947): Windsor ferry track (lead off the GW main to the slip), Windsor wharf (-83.03400, 42.32190), Detroit wharf (-83.03763, 42.32825),
  Detroit Brush Street station (-83.03976, 42.32851). Links added: 'CN Windsor ferry track' (own cn) and the crossing (own 'water': Windsor slip to mid-river, a smooth
  quadratic curve bowed about 150 m downstream / west; border at mid-course (-83.0374941, 42.3245451), APPROXIMATE).
- Page: a track run whose owner is 'water' is drawn as a dotted water line (like steamer lanes), no track; the train itself crosses (no boat).
- on_cn_t090w: rows Windsor Ferry Slip (110.4) and International Boundary (Detroit River, to Detroit, Mich.) (110.7) added (scratchpad patch; t090.py is NOT rerun).
  Times from the printed Windsor - Detroit interval I (40 - 65 min): to Detroit: Windsor ar T, lv T+0.11I, slip ar T+0.22I, lv T+0.55I, border T+0.67I; from
  Detroit mirrored (Windsor lv as printed). Windsor departure / arrival and the slip and border times estimated.
- The route reverses at Windsor station and runs back about 0.4 km along the main line to the slip (the path-finder ties the slip end to the main line, so it does not
  use the full length of the ferry lead). Detroit end (slip, Brush Street) in the notes only.

## Version 113 (31 October 2026): the Windsor - Detroit ferry finished (Brendan: fix the jump, include the Detroit side)
- on_cn_t090w now runs to Detroit (Brush Street) (Brendan's point -83.03976, 42.32851), by Windsor Ferry Slip (110.5) and Detroit Ferry Slip (111.0); the border stop is
  gone (the trains cross it). Rows made by scratchpad on/t090w_ferry.py from the Version 111 file (copy kept: scratchpad on_cn_t090w_v111.csv). Times: Windsor ar T,
  lv T+0.11I, Windsor slip T+0.22I - T+0.5I, Detroit slip T+0.75I - T+0.89I, Brush Street T+I as printed (mirrored from Detroit); I = printed Windsor - Detroit.
- Links (property net: true): Windsor ferry track, the crossing (own water, the whole course, bowed about 150 m downstream), the Detroit slip lead (east along the river)
  and the Brush Street station track (trains reverse at the lead's end). Trains reverse at Windsor station, run back to the ferry track junction and down the lead.
- on_lines: net links go into the graph as kind 'x' (a copy of ab_lines.make_graph, _make_graph): tied only at their loose ends, and traces are not tied onto them
  (the Great Western main line link tied itself to the Windsor slip end, 36 m away). ab_lines.py itself unchanged.
- Careful: the Quebec - Levis and Trois Rivieres ferry crossings are links named '... ferry crossing (Claude)': do not filter links by the word ferry.

## Version 114 (31 October 2026): page 1129, CN Tables 113, 113a, 114, 115, 119, 120, 121
- Script: scratchpad on/t113.py (also rewrites on_cn_t126d.csv; the old copy: scratchpad on_cn_t126d_v113.csv).
- on_cn_t113: Toronto - Stouffville - Uxbridge - Blackwater - Manilla - Lindsay - Peterboro - Millbrook - Port Hope: 92 / 95 (ex Sun), 88 The Highlander (Sat, Toronto - Lindsay; on as 89).
  on_cn_t113b: Toronto - Lindsay - Peterboro - Campbellford - Madoc Jct. - Belleville: 94 / 93 (ex Sun). Madoc Jct. - Madoc 364 / 365 = on_cn_t081a (same times).
  on_cn_t113h: The Highlander Sundays (87 from Haliburton, then 85): Lindsay - Lorneville - Blackwater - Toronto (Tables 115, 113a, 113 joined).
  Not entered: 84 and the first 85 - 87 (cancelled June 27 - Sept 5); 148 (113a, same). Table 119 = 10 / 92 / 95 / 5 (nothing new).
- on_cn_t113a: Blackwater - Lorneville - Beaverton East - Orillia - Coldwater - Midland: motor 603, 605 / 602, 604 (ex Sun), 107 / 106 (Sundays, summer). Midland Dock (603 in
  summer, no time) not entered (no point for it). on_cn_t126d now only 45D and 42D with the Orillia - Midland stations; 41D, 44D, 38D were 603, 604 and 106.
- on_cn_t114 Peterboro - Lakefield M373 / M372; on_cn_t115 Lindsay - Lorneville - Coboconk M387 / M386 (MWF), motor 601 / 606 (ex Sun).
- on_cn_t120 Brantford - Norwich Jct. - Norwich - Otterville - Norwich Jct. - Tillsonburg - Tillsonburg Jct.: M329 (with 331, 330, 333 round the loop) / M328 (ex Sun).
  READING: 328 leaves Norwich Jct. 5.15 and is at Norwich 5.25, printed in the Otterville sections with no Otterville time: entered as going round by Otterville
  without stopping (ASK Brendan; else Norwich Jct. - Norwich direct).
- on_cn_t121 Hamilton (James St.) - Caledonia - Jarvis - Simcoe (North / South) - Port Rowan 233 / 238; on_cn_t121d Simcoe (South) - Port Dover 236 / 235;
  on_cn_t121t Jarvis - Simcoe (North) - Delhi - Tillsonburg - Aylmer - St. Thomas M355 / M356 (ex Sun).
- Track: links re-added (dropped by the abandonment filter for notes about other sections): Toronto & Ottawa Ry. Blackwater - Manilla Jct. and Omemee - Peterboro;
  Hamilton & Lake Erie Hamilton - Caledonia - Jarvis (5 pieces; Jarvis - Port Dover, abandoned 1935, left out). Places: Blackwater = Blackwater Junction station,
  Manilla = Manilla Junction station, Brechin = the Midland Ry. point; Schepeler by mileage (the collection's line there is a 9.6 km straight).
- To check with Brendan: which Peterboro point is the 1948 CN station (by mileage now); No. 95 Campbellcroft 4.27 - Carmel f4.32 (5.2 mi in 5 min, as printed).
- TO CHECK (Brendan, 31 Oct 2026, 23:20): the CN Port Dover routing (on_cn_t121d Simcoe (South) - Port Dover, 236 / 235: traced 8.1 mi for 7.5 printed; Simcoe (South) by mileage).

## Version 115 (1 November 2026): Brendan's answers to the to-do list
- Hand points (on_lines HAND, all CN files): Chatham (the GW station; force Northwood - Chatham, the collection's line there is coarse and long), Brantford
  (Brendan's point, not in the collection), Marmora (the Central Ontario station), Kincardine (the collection's "Kinkardine" point), Peterboro (the Midland Ry.
  point, the primary station in 1948), Port Hope (the GT main-line station; Port Hope (Main St.) on Table 113 = the Midland Ry. station). Brantford (Colborne St.)
  on Table 120 at Brendan's point. CP Table 69: Embro, McConkey at their points (force: the printed miles disagree with the line); Ostrander = the CP Springford
  point, Kinglake = Kingslake.
- Track: the GT main-line old alignments by Port Hope ('Re-alignment.') and Bowmanville ('Abandoned mainline.') dropped (realigned 1900 - 1911); the
  Peterborough & Chemong dropped (Lakefield trains take the Millbrook - Lakefield branch); a Port Hope crossover between the collection's two main-line tracks
  (they meet only at their far ends); St. Clair Tunnel trace (Brendan) to the border mid-river, Sarnia = the CN Sarnia Tunnel station (was the Pere Marquette
  point); Table 56 border at the end of the International Railway Bridge track (Brendan's point); Midland Dock 0.2 mi along the Canada Steamship Lines siding.
- Timetables: M389 Lindsay - Watsons times (Brendan's reading); CP No. 20 (on_cp_t049w) re-entered from Brendan's scan (was one row off); Midland Dock call of 603.
- Brendan confirmed: M388 is a; 328 by Otterville (table heading "via Norwich and Otterville"); No. 95 as printed; M263 stays; TIR No. 19 as printed; Laviolette
  in 1948; Table 65 OK; Sorel trains at the main St. Hyacinthe station (already so).
- Manson - McAuley trace (Brendan, 1 Nov): the same line as traces/saskatchewan/kirkella_mcauley.geojson (not added twice). skcp107b still straight Manson -
  Welwyn: McAuley (trace end) is 9.0 mi from Manson for 5.1 printed, and there is no track McAuley - Welwyn.

## TO DO (1 November 2026, replaces the lists above) - SUPERSEDED 9 Nov 2026: the open items are in TODO.md (merged with OPEN_QUESTIONS.md)
- TO CHECK (Brendan): CN 122 / 126 Camp Borden (Brendan to trace); L&PS Colborne St., Philip St., Elm St., Stop 7, No. 37 St. Thomas; CP Table 73 No. 50 Elma
  (8.09 printed) and Crest; CP Table 69 Bennington, Lind (by mileage); CP Table 107 McAuley - Welwyn; CN Port Dover routing (Simcoe South - Port Dover).
- TO CHECK (Brendan, 2 Nov 2026): Iberville, CN Table 72: keep "lve. Iberville (C.P.Ry.) 25.3" only as the timing point after the reversal at the junction, or drop the row
  (Brendan doubts the trains ran into the CP station; trace of the short CN link up to the CP); NYC Tables 6 / 11 readings: 364 St. Thomas 11.28 - Aylmer p11.33
  (10.7 mi in 5 min), 366 Lythmore f4.23 - Cayuga 4.25, M362 Charing Cross 6.58 - Fargo 7.25; the Detroit River Tunnel portal and border point (APPROXIMATE, Brendan
  to trace); the Table 44 Petrolia / Oil Springs branch miles (estimated); Otterville.
- TO DO (Brendan, 3 Nov 2026): Canadian Pacific Car & Passenger Transfer Co. (the Prescott - Ogdensburg car ferry across the St. Lawrence).
- TO DO (Brendan, 4 Nov 2026): CN Peebles - Handsworth (sk_cn_t162; Saskatchewan): the intermediate stops (the table prints only Peebles and Handsworth).
- DONE (Version 135): the Cobourg - Genesee (Rochester) car ferry across Lake Ontario.
- BUILT in Version 140 (staged 4 Nov 2026): CN Table 124 Ridgeway at Brendan's point (-79.051745, 42.882312) (it had been placed by mileage on the line further
  north, so the trains ran the wrong way to Port Colborne); a short link across the gap by Fort Erie Junction station (Brendan: the Dunnville division
  yard track to the GTR 1873 connector), so the trains take the Buffalo & Lake Huron. Dry run: 116.2 / 114.9 mi, all on track (Fort Erie - Ridgeway 9.5 / 8.9).
- BUILT in Version 140 (staged 5 Nov 2026): H&LB landings not listed in the Official Guide shown as minor (lob_build MAJOR: Huntsville, Dorset, and the
  two Portages as the Flyer's ends; Brendan to say if the Portages should be minor too).
- TO DO (Brendan, 7 Nov 2026): check the Montreal suburban trains against the CN Montreal employee timetable of June 20, 1948:
  https://www.traingeek.ca/files/19480620-ett-montreal-16.pdf
- DONE (7 Nov 2026): the CN special train for westbound C.S.L. passengers is CN Table 82 No. 77 (Sun, Tue, Thu, Montreal 8.50 a.m. - Prescott 11.40).
  Brendan (CN employee timetable, June 20, 1948): 77 leaves the CN main line at Prescott Junction for the CP line into Prescott, by the wharf. Moved to its own
  file on_cn_t082d.csv (out of on_cn_t082.csv), ending at Prescott (C.P.R. Station) = CP_PRESCOTT (shared stop, SHARED ('oncn', 'prescott c p r')); connector
  "Prescott Junction" (estimated curve, south-east quadrant, CN NE leg to CP south leg) in ontario_quebec_links.geojson. Dry run 114.9 traced / 115.1 (est.), on track, ends on CP.
- WAITING ON BRENDAN: Quebec Railway, Light & Power; the Stratford table (No. 10); the Camp Borden trace; the remaining steamship points and waterways; the rest
  of the Official Guide pages.
- BUILD: run-through joins (London, Hamilton, North Bay, CN 3 / 4, CP / TH&B at Hamilton, Cataract); numbering of connecting sections (wait for the branch tables);
  Trois Rivieres south-shore landing times vs the ferry.
- IDEAS (considering only): streetcar texture; North Yonge interurban.
- FOUND (1 Nov, after Version 115): stations a little off the track get an in-and-out stub on the route (the train runs to the point and back): about 150
  cases in Ontario and Quebec, mostly 30 - 150 m, a few large (CP Kipawa 603 m, Ville Marie 739 m, Foster 461 m, St. Basile 438 m, Leaside 328 m; CN Windsor
  264 m is the ferry reversal, intended). Offered to Brendan as one general fix (stop on the track beside the point instead of running out to it).

## Version 116 (1 November 2026)
- Chatham: the collection's Great Western pieces through Chatham never reached the station (trains ran 2 km past and back: the 2.9 mi extra Brendan saw);
  the two duplicate 2-point links replaced by one net link through the station (end of the coarse London - Chatham piece, the station, the start of the
  Chatham - Windsor piece). Force removed. oncn090w 111.8 traced / 111.5 printed.
- CP 159 / 160 (skcp107b): McAuley - Welwyn IS in the NRWN (CP Rocanville subdivision, mb_all.json; it passes 44 m from the end of Brendan's Kirkella -
  McAuley trace). The straight came from the printed miles: Manson - McAuley 5.1 printed, 8.9 on the track. Hand points (sk_lines HAND) Kirkella, Manson (CGN,
  on the trace), McAuley (trace end); force Kirkella - Manson - McAuley - Welwyn. All on track (315.7 traced / 303.9 printed).
- STUBS (Brendan: fix, prairies too): stubs.py at assembly (after split_stops): where the route runs out to a station point and straight back (up to 800 m),
  the stub is cut, the station stops on the track where the stub left it, and the chains close up (viz route, stations, segments; GTFS shapes, stop_times
  shape_dist, stops.txt position). Kept: real reversals (the train leaves the way it came, heading turned more than about 100 degrees) and KEEP (Windsor ferry).
  Only lines whose GTFS route id is their key (all Ontario, Quebec, prairie, Alberta, Washington steps). About 267 cut; the largest: St. Gregoire 776 m, Fassett
  594 m, Peterboro 456 m, N.Y.C. Depot (St. Thomas) 442 m, Winagami 404 m, Hammond 371 m, Roblindale 336 m, Oriole 332 m, Maple Creek 311 m, Oak Lake 272 m.
- LEFT (about 90 stations): out-and-back stubs where the route turns back the way it came, kept as possible real reversals: e.g. Coe Hill (real),
  Trenton Junction, Bridge Street (Montreal, 232 m), Leaside 328 m, St. Basile 438 m, Foster 461 m, Kipawa 603 m, Ville Marie 739 m, Bulyea 459 m, Brandon
  387 m, Battleford 320 m, Avonlea 735 m; over 800 m not touched (Prinham 2.7 km, Schuler 1.3 km, Virden (107a) 1.0 km, Kennewick 1.0 km). To review with Brendan.
- Brendan (1 Nov): CN Brandon and Battleford reversals are real (added to stubs.KEEP; they were already kept). The rest of the list still to review.
- Version 117 (1 Nov): Bridge Street (Montreal) hand point moved onto the line the trains run (-73.551793, 45.485113): the old point sent every train from
  Central Station past it toward the Victoria Bridge and back (Montreal - St. Lambert 1.1 mi shorter now). Brendan: Bridge Street was an error he meant to fix;
  the exact 1948 station position still to confirm.
- stubs.py: a station whose stop id is shared with another railway is never moved (the cut had pulled the L&PS N.Y.C. Depot at St. Thomas off the NYC depot,
  Brendan); KEEP adds ('onlps001', 'N.Y.C. Depot'). 266 cut.

## Version 118 (1 November 2026): page 1130 (Tables 123, 124, 125; Table 122 already in)
- Script: scratchpad on/t123.py. on_cn_t123 Hamilton (James St.) - Burlington - Milton - Georgetown - Beeton - Allandale - Barrie, motor 660 (- 661) / 662 (- 663),
  ex Sun; Toronto - Georgetown connections in the notes; Allandale 11.00 - Barrie 11.38 as printed. Burlington by the collection (Aldershot - Burlington 3.7 mi
  traced for 2.9; which Burlington station the H&NW trains used: to check).
- on_cn_t124 (table number cut off in the scan; between 123 and 125): Fort Erie - Port Colborne - Dunnville - Caledonia - Brantford - Paris - Tavistock - Stratford,
  mixed M219 / M218 ex Sun. Black Rock: freight only (not entered). Fort Erie - Port Colborne traces 21.1 for 19.0.
- on_cn_t125 London - Exeter - Clinton Jn. - Clinton - Goderich, motor 603 / 604 ex Sun (same numbers as the Table 113a motor trains, other line).
  London, Huron & Bruce London - Clinton re-added as links (dropped by the abandonment filter for Clinton - Wingham Jct., 1941).
- Version 119 (1 Nov): Table 123 Burlington = the Table 90 station at the junction (-79.815227, 43.338803); the trains had run 1.8 km out to another
  Burlington point and back (Brendan's screenshot). 93.4 traced / 92.6. Table 124 Fort Erie: on the Canada Air Line beside the CN station (a vertex added by
  a net link); it had snapped to the Canada Southern main 14 m away and run to the bridge and back (Brendan). Fort Erie - Port Colborne 20.3 / 19.0.

## Version 120 (1 November 2026): page 1132 (Tables 127, 128, 136, 137, 138, 140)
- Script: scratchpad on/t127.py (also cuts on_cn_t126m to Toronto - Allandale); t123.py rerun for Table 125.
- on_cn_t127 Toronto - Brampton - Georgetown - Guelph - Kitchener - Stratford - St. Marys - London: down 39 (ex Sun), 139 (Sun), 37 (to Stratford), 175 and 27 (to
  Guelph), 11 (Mon - Fri), 111 (Sat), 29, 137 (Sun, to Stratford); up 10 (from London; the International Limited section - the "Stratford table" Brendan was to send),
  28, 34, 138 (Sun) from Stratford, 172, 36, 142 (summer Sun) from Guelph, 40 (daily, from London).
- on_cn_t127g Stratford - Mitchell - Seaforth - Clinton - Goderich: 37, 35 / 28, 34. Table 125 motor trains 603 / 604 now London - Clinton only: their printed
  Clinton - Goderich times are Nos. 35 / 34.
- on_cn_t127s Stratford - St. Marys Jct. - Lucan - Forest - Sarnia (CN Sarnia Tunnel station): motor 601 / 600.
- on_cn_t140 London - St. Marys - Stratford - Listowel - Palmerston: 170, 168 / 171 (Palmerston - London), 169 (Palmerston - Stratford; London by No. 29). Owen Sound
  (Palmerston - Owen Sound) in the notes.
- on_cn_t128 Palmerston - Mount Forest - Durham M333 / M334; on_cn_t136 Allandale - Elmvale - Penetang M397 / M398 (replaces on_cn_t126p, DELETED);
  on_cn_t137 Allandale - Collingwood - Meaford 63, 61 / 60 (e: Tue - Sat), 62, 160 (summer Sun); on_cn_t137c Allandale - Angus - Camp Borden 61 section / M396
  (replaces on_cn_t126c, DELETED; Camp Borden mile still estimated, Brendan to trace); on_cn_t126m cut to Toronto - Allandale (45 / 42; 41M, 44M, 38M removed).
  on_cn_t138 Parkhead - Wiarton M341, M337 / M336, M338 (Parkhead at the junction, APPROXIMATE).

## Version 121 (1 November 2026): pages 1133 - 1134 (CN Tables 143, 145; GTW Tables 146 - 154)
- Scans saved to dmr-sources (og1948_cnq/p1128_* to p1133_*, cp_t050_no20). Script: scratchpad on/t143.py.
- on_cn_t143 Hamilton (James St.) - Dundas - Lynden - Harrisburg - (St. George and back) - Galt - Preston - Hespeler - Guelph - Elora - Fergus - Palmerston - Harriston -
  Hanover - Chesley - Parkhead - Owen Sound: 173, 175 (from Guelph; Toronto - Guelph in on_cn_t127), M339 (Parkhead - Owen Sound) / 172 (to Guelph; on to Toronto in
  t127), 174 (to Hamilton), M340 (Owen Sound - Parkhead), 142 (summer Sun, Palmerston - Guelph). Link: GW original main Lynden - Harrisburg - St. George (part of
  collection piece 6028, dropped by the abandonment filter for Harrisburg - Alford, 1923). Brantford - St. George bus not entered.
- on_cn_t145 Palmerston - Harriston - Walkerton - Paisley - Port Elgin - Southampton: 179, M329 / 178, M330, 142 (summer Sun).
- GRAND TRUNK WESTERN (Michigan): TRANSCRIBED, NOT BUILT (United States): on_gtwfull_t146 (Durand - Bay City), t148 (Detroit - Port Huron), t149 (Jackson - Pontiac -
  Richmond), t150 (Detroit - Durand - Grand Rapids - Muskegon; Grand Haven mixed and the Muskegon - Milwaukee car ferry in its notes), t152 (Durand - Greenville),
  t153 (Pontiac - Caseville). Tables 151 (St. Thomas - Glencoe - Alvinston, Ontario) and 154: freight only.
- TO CHECK (Brendan): Parkhead station point (now at the junction of the Wiarton line, APPROXIMATE; used by Tables 138 and 143); St. George end of the stub.

## Version 122 (1 November 2026): Table 72 Iberville - Farnham by the CP (Brendan)
- Brendan: the direct CN (Stanstead, Shefford & Chambly) line Iberville - Farnham was abandoned in 1935; the trains run in to the CN Iberville station, north to
  the CP, reverse onto it and run over the CP to Farnham (CP station), then the CN again. Undoes Version 100's routing.
- on_cn_t072: Iberville split again: Iberville (CN station, 23.9; arrival down / departure up) and Iberville (C.P.) (25.3, = CP_IBERVILLE; departure down / arrival up)
  as printed. Collection piece 572 (desc "Main line from Saint-Jean to Farnham.") dropped; its St. Johns - Iberville part re-added as a link ending at the CN
  station; north from the CN station by the collection's East Richelieu Valley piece to the CP Adirondack line.
- The St. Johns - Iberville link now starts at the St. Johns station point (net link): the trains had run west to a wye and back first.

## Version 123 (1 November 2026): New York Central (Michigan Central) in Ontario; CP Windsor
- New railway key 'onmc' (label New York Central (Michigan Central), own nyc, agency NYC, pfx NYC; graph 'mc': NYC track only, box SW Ontario). Files on_mc_t*.csv.
  Script: scratchpad on/mc006.py. Scans: dmr-sources og1948_cnq/nyc_t006_t011_t044_*.
- on_mc_t006 (NYC Tables 6 / 11, the Canada Southern line, border to border): Detroit River Tunnel border (APPROXIMATE, straight link from the end of the Canada
  Southern main by the Windsor station; no trace) - Windsor (the '2nd Windsor station') - Essex - Ridgetown - St. Thomas - Tillsonburg - Waterford - Welland - Fort
  Erie - International Railway Bridge border (Brendan's point). East: 366 (motor, Windsor - St. Thomas a.m.), 366 (St. Thomas - Fort Erie p.m.), M362, 44, 8 The
  Wolverine, 364, 50 Empire State Express, 40 North Shore Limited (no Ontario stops printed: border times and St. Thomas estimated). West: 17 The Wolverine,
  33 New England Wolverine, M361, 365 (Fort Erie - St. Thomas a.m.), 365 (St. Thomas - Windsor p.m.), 35, 51 Empire State Express, 39 North Shore Limited.
  on_mc_t006n: 358 The Canadian - The Niagara (Windsor - Welland - Niagara Falls, Ont. - border at the bridge to Suspension Bridge).
  Not entered: the TH&B trains printed in these tables (in on_thb_t056), the Welland - Niagara Falls motor buses, The Detroiter 48 / 47 (no Ontario times), the
  Michigan-only trains. Several station points by mileage (Ruscomb, Comber, Fargo, Mull, Charing Cross, Ridgetown, West Lorne, Dutton, Cayuga, Edward: the
  collection points did not fit the line).
  DOUBTS: 364 St. Thomas 11.28 - Aylmer p11.33 (10.7 mi in 5 min) and 366 Lythmore f4.23 - Cayuga 4.25 as read; M362 Charing Cross 6.58 - Fargo 7.25.
- on_mc_t044 (NYC Table 44) St. Thomas - Alvinston - Oil City - Brigden - Courtright mixed M101 (MWF) / M102 (TThS), each split at the branch trips;
  on_mc_t044b Eddys - Oil Springs - Oil City - Petrolia Jct. - Petrolia: M105, M107, M103 / M104, M106, M108 (branch miles estimated).
- CP (on_cp_t049w): Windsor = the NYC Windsor station (Brendan: by 1948 CP trains used it; the old CP station was demolished in the 1930s); stop id NYC_WINDSOR
  (SHARED ('oncp', 'windsor')); force Walkerville Junction - Windsor (over the CP yard to the Michigan Central).
- Brendan doubts the Table 72 reversal into the CP Iberville station (asked how he reads it).

## Version 124 (2 November 2026): CP into Windsor over the Michigan Central connection
- Brendan: the Version 123 CP routing at Windsor was odd (up the CP yard toward the old ferry dock and back down the MC, then back to the station).
  New link (own cp, cost 0.8) "CP Windsor: connection from the CP main line to the Michigan Central, through the NYC Windsor station to the tunnel": the
  collection's CP Windsor siding that curves from the CP main line west of Walkerville onto the Canada Southern by the station, then the MC main through the
  station to the start of the tunnel link (ready for the trains to run on to Detroit). The force (Walkerville Junction - Windsor) removed.
  Dry run: 227.4 / 226.1 mi; Elmstead - Windsor now matches the printed 10.5; Walkerville Junction on its point.

## Version 125 (2 November 2026): scheduled speed beside Follow
- Page: the train panel's head shows "x m.p.h." right of the train number, beside Follow (Brendan, 2 Nov 2026: no explanation; period style "m.p.h.").
  segSpeed(): printed miles (station miles on the route; traced chainage if none) between the timed stops either side of the train (estimated / untimed
  stops skipped), from the departure time to the arrival time, rounded. Moving: the stretch it is on; standing at a station: the stretch ahead. Not shown
  for boats or at the terminus (B.C. Electric added the same day, by the traced track). Also a free data check (e.g. No. 364 St. Thomas - Aylmer).
- Ideas discussed, not built: through trains as linked trips (highlight end to end, one timetable with the hand-off row); multi-coloured pooled consists
  (CN / CP pool trains) and through cars from the Guide's equipment notes; a time-zone drop-down (Alaska - Newfoundland, plus "Local, as printed").

## Version 126 (2 November 2026): Selkirk Navigation Co., Lake Winnipeg (S.S. Keenora, M.S. Chicama II)
- boats_build.py, operator Selkirk Navigation Co. (livery 'snc', agency SNC, America/Winnipeg; colour Claude's pick #8A3B2B). A MODEL week (Brendan):
  from the advertisements only the Monday noon sailing from Redwood Dock and the Sunday Lockport cruise (2 - 8 p.m., 1937 ad); the rest estimated
  (about 9 mph, time at the calls for freight and flag stops, running through the nights). keenora_1948_notes.txt.
  snk: Keenora north Mon 12.00 Redwood Dock - Selkirk Wharf 3.00 / 4.30p - Gimli 9.00 / 10.00p - Hecla Island Tue 2.30 / 3.30a - Berens River 2.00 / 4.00p
  - Warren's Landing Wed 3.30a; south Thu 6.00a Warren's Landing - Grand Rapids 2.00 / 4.00p (a call, Brendan; no overnight) - Berens River Fri 4.30 /
  6.00a - Hecla 4.30 / 5.30p - Gimli 10.00 / 11.00p - Selkirk Sat 3.30 / 4.30a - Redwood Dock 8.00a. snl: Sunday cruise Redwood Dock 2.00p - Lockport
  4.00 / 5.30p - Redwood Dock 8.00p (Lockport by the St. Andrews Lock, APPROXIMATE). snc: Chicama II Wed Warren's Landing 7.00a - Norway House (HBC
  warehouse) 9.30 / 10.00a - Rossville 10.30a; back 3.00p - Norway House 3.30 / 4.00p - Warren's Landing 6.30p, over Brendan's trace
  (traces/manitoba/warrens_landing_norway_house.kml; the drawn water does not have this channel). Points: traces/manitoba/selkirk_navigation_points.kmz.
- Lanes: water_extra.py now adds the Manitoba part of saskman3 (Lake Winnipeg, the Red River) to water_extra.pkl (cached lanes unchanged).
- FIX: on_build.py rewrote gtfs/routes.txt with '\n' line endings (the csv files use '\r\n'): build.py then saw every row as changed, and rows that
  earlier steps added since on_build last ran landed above the header. Now kept with their endings.

## Version 127 (3 November 2026): Northern Navigation Co., the S.S. Noronic (Great Lakes)
- New step `nn_build.py` (needs on_build), line `nn`, GTFS route NN, agency NNC: one round trip a week, westbound from Windsor Fridays (NN-W, W_0000100), eastbound from Duluth
  Tuesdays (NN-E, W_0100000). Windsor (Government Dock) - Detroit - Sarnia (Pt. Edward) - Sault Ste. Marie (C.S.L. Dock) - Port Arthur (C.N.R. Dock) - Duluth (Northern Pacific
  Dock No. 4); 901.9 mi of lane. Timetable (a screenshot from Brendan, midsummer, Eastern time, Duluth Central; the weekdays are 1948's) and the ports: noronic_1948_notes.txt,
  traces/lakes/northern_navigation_co.kmz (Brendan's points). Eastern times are shown 3 hours earlier (one Pacific clock), Duluth's Central time 2 hours earlier.
- The Detroit call is the CN Windsor - Detroit car ferry slip (Brendan: the same pier): gid CN_DETROIT_FERRY_SLIP, one station for the boat and the ferry trains. That is why this is
  a step of its own after on_build, not part of boats_build.py (which runs before on_build and would have added a second stop with the same id). Detroit is printed on one side
  only each way, so it shows "est.".
- Lanes: the Great Lakes water (water_east.json, until now drawn only) is added to the lane mask inside nn_build.py (`sea._U`); sea.py, boats_build and its lane cache are untouched
  (boats_build stays "ok"). Own lane cache nn_legs.json. Grid by leg (60 m Windsor - Detroit, 100 m Detroit - Sarnia, 250 m the lake legs). Port Arthur - Sault Ste. Marie has three
  waypoints (Passage Island, mid-lake, off Whitefish Point): the raster path bends 45 degrees and cut the Keweenaw tip, and the layer has no Isle Royale.
- Livery `csl` (Canada Steamship Lines, for every CSL service later: Brendan: "the same livery, perhaps a bright red if that isn't taken"): --csl and --csl-funnel #d93a1c light,
  #ff7048 dark (Claude's pick, a warmer vermilion than the B.C. Electric red #d7261e so the two stay apart; not confirmed), .badge.v.csl, BOAT_COLOR, readColors.
- Page: new view "Lake Superior to Detroit" (`lakes`, menu bottom right). A box this far from the central meridian (122.5 W) turns on the page's projection, and `fit()` kept every
  point in the turned box's bounding rectangle (all of eastern Canada). VIEWS entries may now end in 'q': `fit()` then keeps only the points inside the turned box itself. Other views
  unchanged.
- Checks: check_vessels 35 named vessels, 0 overlaps; check_gtfs 1 problem (old: CP-14-SKJCP13 at Minneapolis); screenshots of the lakes, the Soo, Duluth and Detroit; page errors none.
- FIXED (Brendan, 3 Nov 2026): Selkirk Navigation (Version 126) times were stored as printed (Central); boats_build now shifts them two hours earlier onto the Pacific clock
  (`DST[SNC]`, Keenora Monday noon from Redwood Dock now 10.00), the trip note says so, and agency SNC is America/Vancouver like the others.
- Not entered: any other Northern Navigation / Canada Steamship Lines service. The scan of the timetable page is not in the repo (it should go in the private sources repo, scans/boats/).

## Version 128 (3 November 2026): Canadian Pacific Great Lakes steamers Keewatin and Assiniboia
- Source: the April 1948 CP timetable (Brendan: the same one used all along). The Noronic (Version 127) is from the May 1948 Official Guide; its SRC line and notes now say so.
- New step `cp_lakes_build` (key `cpgl`, livery `cpss`, CP): Port McNicoll (the CP station, gid CP_PORT_MCNICOLL) - Sault Ste. Marie (Government Dock, the Noronic's stop, same gid PORT_SAULT_STE_MARIE_C_S_L_DOCK so they merge) - Port Arthur (CPR Dock) - Fort William (CP Docks); dock points are Brendan's (traces/lakes/cp_great_lakes.kml). The connecting trains were already in the model.
- Four sailings, Eastern time minus 3 h, all printed: westbound Keewatin from Port McNicoll Tuesday 5.30 p.m., Assiniboia Saturday; eastbound Keewatin from Fort William Saturday 11.00 a.m., Assiniboia Tuesday 4.00 p.m. (Sault 11.45 a.m. / 12.30 p.m. westbound; Port Arthur 6.45 a.m., Fort William 8.30 a.m.). One round trip a week each, no overlaps.
- Lanes: 310 mi Port McNicoll - Sault (Georgian Bay, North Channel, St. Marys River), 313 mi Sault - Port Arthur (same three waypoints as the Noronic), 4.6 mi Port Arthur - Fort William. Speeds 15 - 17 mph. The Fort William dock lies about 2 km inland of the water layer, so the vessel is drawn to the shore end of the lane and the station marker sits on Brendan's point (as for the Noronic's docks).

## Version 129 (3 November 2026): Canadian Pacific S.S. Manitoba, the Great Lakes cruise
- Source: the April 1948 CP timetable, "Every Thursday, June 24 to August 26, inclusive" (Brendan, 3 Nov 2026). New step `cp_manitoba_build` (key `cpmb`, livery `cpss`).
- Port McNicoll and Owen Sound are the CP stations (CP_PORT_MCNICOLL, CP_OWEN_SOUND; Brendan: Owen Sound is the CP station); Sault Ste. Marie and Fort William are the same stops as Version 128's, so the ships merge on the page. Trains 707 / 708 were already in the model.
- Two trips on one ship, all times printed, Eastern minus 3 h: outbound Thursday (svc W_0001000) Port McNicoll 4.00 p.m., Owen Sound 10.00 p.m. - 11.00 p.m., Sault Friday 7.30 - 8.00 p.m., Fort William Saturday 5.00 p.m.; homeward Sunday (svc W_0000001) Fort William 6.00 p.m., Sault Monday 4.00 - 6.00 p.m., Owen Sound Tuesday 2.30 - 3.00 p.m., Port McNicoll 9.00 p.m. The cruise fare includes meals and berth on the ship at Fort William, where she lies Saturday evening to Sunday evening.
- Lanes 79 / 274 / 311 mi (Port McNicoll - Owen Sound, Owen Sound - Sault, Sault - Fort William with the Noronic's three waypoints); speeds 13 - 15 mph.
- Port Arthur - Fort William track (Brendan, 3 Nov 2026): his hand-drawn path (traces/lakes/cp_pa_fw_track.kml, 4.9 mi, drawn Fort William to Port Arthur) replaces the least-cost lane for Keewatin and Assiniboia; both docks now sit on it. The Manitoba (which does not call at Port Arthur) runs the Sault lane to the Port Arthur harbour mouth and then his track to Fort William (670 mi from Port McNicoll). Both steps list the KML as an input.

## Version 130 (4 November 2026): six more CN mixed trains, Foleyet - Hornepayne - Longlac - Nakina - Armstrong
- Source: the April 1948 CN timetable (not the Official Guide), Brendan, 4 Nov 2026. Unnumbered mixed trains added as columns MFH, MHL, MNA (down) and MHF, MLH, MAN (up) in `on_cn_t075b.csv` (line oncn075b): Foleyet 7.00 a.m. Sat for Hornepayne; Hornepayne 7.30 a.m. Fri for Foleyet; Hornepayne 7.30 a.m. Wed for Longlac; Longlac 9.30 a.m. Thu for Hornepayne; Nakina 7.00 a.m. Fri for Armstrong; Armstrong 8.00 a.m. Sat for Nakina. Eastern time.
- Only departures were supplied: every other time is estimated (`~`, shown est.) at 17 mph with 3 minutes at each intermediate stop (Elsas, Oba, Nagogami River, Cavell), so the runs are 6 - 9 hours. Replace with the printed times when Brendan supplies them.
- Rebuilding on_build needs the private sources: clone BSDawe/DigitalModelRailwayPrivate and run `python3 tools/link_sources.py <clone>` first (without them on_build fails at onacr001). It took about 10 minutes; nn_build, cp_lakes_build and cp_manitoba_build re-ran after it.

## Version 128 (4 November 2026): TH&B at the NYC stations
- on_lines SHARED: ('onthb', 'welland') NYC_WELLAND, ('onthb', 'fort erie') NYC_FORT_ERIE, ('onthb', 'international boundary') the NYC Black Rock border point
  (Brendan: two Wellands on top of each other).

## Version 129 (4 November 2026): stations (Brendan, 4 Nov, after a sweep for different stops on the same point)
- Carman: CN station (-98.003927, 49.508874), CP (-98.012480, 49.509258, estimated) (sk_lines HAND): the CN line is now straight through town (it had
  been routed round the CP loop south of town to the town point).
- Roland: CN and CP each by mileage on its own line (sk_build OVER noplace for sk_cn_t184 and sk_cp_t098b): east and south of the crossing. Points to come?
- Russell: CP station (-101.291910, 50.782035); CN as it was.
- merge_stations.py: Maryfield (CP trains at the CN station), Portage Junction (CN, NP, GN one station), St. Paul (CP and GN: Union Depot for every St. Paul
  railway unless a table says otherwise), Smooth Rock, Fauquier, Moonbeam, Kapuskasing (ONR over the CN: the CN stations). New MERGE_AFTER, applied after
  split_stops (build.py): Rosedale, Alta. (CN_ROSEDALE_CN_168 + CP_ROSEDALE), placed at (-112.630350, 51.419370) in ab_cn_build / ab_cp_build (estimated).
- Kept separate (Brendan): the NYC and CN Niagara border points (to be fixed with his CN track route).

## Version 130 (5 November 2026): North America Lambert; Brendan's new water basemap
- Projection: Lambert conformal conic, standard parallels 20 and 60 N, central meridian 96 W (ESRI:102009's, on a sphere), origin still Vancouver; in P()
  (page_template.html) and PROJ (basemap/build_tiles.py), which must match. Station / line data are lon/lat and follow.
- Basemap: Brendan's QGIS water layer (water_na.geojson, 51 MB, EPSG:4326; kept on his computer, not in the repo), tiled ON HIS COMPUTER:
  python basemap\build_tiles.py --water "C:\Users\info\Documents\Doodles\DMR Basemap\water_na.geojson" (OSGeo4W Shell, in
  C:\Users\info\Documents\GitHub\DigitalModelRailway), pushed on branch na-tiles, merged here with the page change in one push. 9 levels (0-8), 120 MB.
  Borders still Natural Earth cut to 38 N (EXTENT): going south of Cape May / Cape Mendocino needs a re-cut from the full files.
- Not changed: the steamer lanes still use the old water (sea.py / water_extra.pkl); the single-file page's WATER still the old water files.

## Version 131 (5 November 2026): Huntsville and Lake of Bays; Ridgeway
- New step lob_build.py (needs on_build; lines hla, hlf, hli; GTFS agency HLB; kind 'L' / livery 'hlb', dark teal #1F5F5B, Claude's pick): S.S. Algonquin
  (Huntsville - Fairy and Peninsula Lakes - North Portage), the Portage Flyer (North Portage - South Portage, the collection's line with its switchback spur:
  out to the spur end and back, Brendan), S.S. Iroquois (South Portage - Lake of Bays - Bigwin Inn - Dorset); daily except Sunday, two round trips. A MODEL day:
  printed (1948 Guide, CN Table 126, Brendan) Huntsville dock 8.00a / 3.25p, Dorset 12.45p / 8.00p, Dorset 6.30a, Huntsville 11.40a; the calls and the
  afternoon sailing from Dorset (1.15p) from the company's 1942 summer timetable (dmr-sources scans/marine/hlb_1942_summer.png); meets at the Portages and the
  landings between (timed by distance, flag calls) estimated. Huntsville dock = CN_HUNTSVILLE (Brendan). Left out: Dwight, Glen Cove (private launch), Raymur
  Pines (no point). Points traces/ontario/brendan/lake_of_bays.kmz; the lanes over Brendan's basemap tiles (level 8, read back from basemap/tiles; lob_legs.json).
- Built: the Table 124 Ridgeway / Fort Erie Junction fix (staged 4 Nov).

## Version 132 (5 November 2026): Montreal & Southern Counties (CN electric)
- New rail 'onmsc' (kind 'M', own 'msc', CN colours, drawn as an interurban: INTER_KIND / INTER_OWN), track Brendan's KMZ only (traces/quebec/msc.kmz ->
  traces/ontario/brendan/msc_track.geojson: main line, Ste. Angele branch, Granby piece; collection pieces skipped). on_msc_t001 (Interurban Division,
  Montreal McGill & Youville - Marieville - Granby, all trains incl. 820 / 821 East End - Montreal River Road) and on_msc_t001a (432 Montreal - Ste. Angele,
  453 Ste. Angele - Marieville). OG May 1948 (April 25, 1948); scan dmr-sources og1948_cnq/msc_interurban.png. Granby = CN_GRANBY ("Granby (C.N.Ry.)").
  No. 431's "a" stops (on signal Sundays only) left out. Suburban Division (streetcars) not entered (Brendan). Script: scratchpad on/msc.py.
  46.8 / 47.5 mi, 26.1 / 25.9 (Ste. Angele), all on track.
- Built: the H&LB minor landings (staged 5 Nov). Page: KIND_BADGE / KIND_LABEL for 'L' (H&LB) and 'M' (M&SC).
- STAGED FOR THE NEXT BUILD: GTFS agency MSC (missing: check_gtfs "no agency MSC").

## Version 133 (5 November 2026): Montreal and the M&SC (Brendan)
- M&SC Montreal terminal at the end of the station stub (McGill and Youville; link added to msc_track.geojson); Granby by Westview, Cowie Street and Miner
  (the diagonal Main Street line, abandoned 1925, dropped from msc_track.geojson). Every stop on file east of Mackayville added as a minor flag stop, times by
  mileage (24; the pre-1925 Gare Granby station left out; Albani 14.0 and Bennett's 17.65 by position, Mariecourt 10.5 and Miner 46.9 estimated); none for
  express 434 between East End and Chambly Basin, nor in 431's Sunday-only stretch. 47.6 / 47.5 mi.
- on_lines _graph: the M&SC links are used by the M&SC only and the M&SC uses only its own (Victoria Bridge - St. Lambert: interurban and main-line tracks
  apart). New CN links: Brendan's Victoria Bridge trace; the St. Lambert curved connector east of the station (Table 72 and the St. Johns trains no longer turn
  onto the bridge leg and back into St. Lambert).
- GTFS agency MSC added (the V132 gap).

## Version 134 (5 November 2026): Quebec Railway, Light & Power; CN Table 53 over it; time zones
- New rail 'onqrl' (kind 'Q', own 'qrl', maroon #8C1D40, interurban style), track Brendan's KMZ only (traces/quebec/qrlp.kmz -> traces/ontario/brendan/
  qrl_track.geojson: St. Paul Street - Limoilou link, main line to St. Joachim, double track, Montmorency Falls wye; St. Joachim - Cap Tourmente as CN).
  on_qrl_t001 (39 trains; printed in daylight time, all an hour earlier; running times Brendan's: Quebec - Falls 18, Falls - Ste. Anne 30, - Beaupre 5,
  - St. Joachim 5, the rest of the printed St. Joachim - Ste. Anne time recovery at Ste. Anne; the 12.30 a.m. car moves to 11.30 p.m. the evening before,
  days back one); on_qrl_t001m (Montmorency Falls cars every 15 minutes, 6.00 a.m. - 10.45 p.m. from Quebec, to the Elevator station; a slot left out on
  the days a through train is within 7 min). Every other station a flag stop. Giffard (in the heading only) not a stop. Kent House line closed (Brendan).
  Script scratchpad on/qrl.py. The CN may use the QRL&P links (trackage rights); no other railway. CN Table 53: Palais - Limoilou - QRL&P - St. Joachim
  (87.6 / 87.8 mi), shares QRL_STE_ANNE_DE_BEAUPRE and QRL_ST_JOACHIM.
- Page: time-zone selector (Alaska -2 ... Newfoundland +4.5 h from Pacific, standard time; hidden in Hide boxes mode; remembered per browser): hm() adds
  ZOFF, so the clock, slider ticks, timetables, boards and lists follow; the day name follows the shifted clock. tzNote(): the trip notes and sources say
  the zone the timetable was printed in (no "shown in Pacific time ..."). FIX the same evening: ZOFF declared with var (hm runs above its line).
- NS&T / CN steamers page (condensed tables) saved: dmr-sources og1948_cnq/nst_cn_steamers_condensed.png. Questions out to Brendan (track KMZ, Port
  Dalhousie cars, Toronto - Port Dalhousie boat, Cobourg - Genesee points, colours).

## Version 157 (10 November 2026): Maritime Coal, Railway & Power (the first short line)
- on_mcrp_t001.csv (Official Guide, April 1948; staged/maritimes/mcrp_official_guide.jpg): Maccan 1.20 p.m. - Joggins Mines 2.20 p.m.; Joggins Mines 10.15 a.m. -
  Maccan 11.15 a.m.; daily except Sunday; Atlantic (shift -14400). No numbers printed (num "Train"). River Hebert: no time printed, mile 7.1 and times
  estimated (~1.55 p.m. / ~10.40 a.m.), at the track nearest the village. Chignecto - Maccan branch freight only: not entered. 11.9 mi traced / 12 printed.
- New railway onmcrp (on_lines RAILS: kind C, own mcrp, agency MCRP, colour #4E5D2F, Claude's pick; BOXES; links-only graph like the NFR; SHARED
  ('onmcrp', 'maccan') -> CN_MACCAN). on_build: SRC, glob, rail and rw maps, the rail regex, the agency row, OVER (places on the track).
- Page: kind C wired in (CSS var, badge, legend, KIND_COLOR / LABEL / BADGE, the "On the line" headings). Also the Thousand Islands Railway (kind K), which
  had no KIND_LABEL / KIND_BADGE and no heading: now "Thousand Islands Railway" / "TIR".
- ab_lines: a small railway's station on a CN_ / CP_ stop is noted "Canadian National station; <railway> trains" (Maccan; also the Temiscouata at
  Riviere du Loup and the like).
- Checks: check_gtfs 1 known problem; 557 lines, 4063 trips, 6378 stops, 53 agencies.

## Version 156 (10 November 2026): CP subsidiaries under their own names; the "On the line" headings
- Brendan (10 Nov 2026): an unnamed train of a CP subsidiary shows the subsidiary's name when clicked (it also tells the train numbers apart). New on_build
  OVER option label (ab_lines: the line label and "<label> station" notes): 'Quebec Central' on on_cp_t008 / t008l / t008f / t008m, 'Dominion Atlantic' on
  on_cp_t900 / t900w / t900k. Their mixed trains are named "<label> mixed" (the page's mixed test now matches a label ending in "mixed"). E&N already
  showed "Esquimalt & Nanaimo".
- "On the line" panel: E&N (kind i), Quebec Central and the DAR listed under the Canadian Pacific heading; the Spokane International (kind p, railway
  'Spokane International') has its own heading, shown only when one of its trains is running (headOf in page_template.html).
- Checks: check_gtfs 1 known problem; 556 lines, 4061 trips, 6376 stops; only the seven QC / DAR lines changed (labels, mixed names).

## Version 155 (10 November 2026): Princess Helene; joint DAR stations; the mileage review list
- C.P.S.S. Saint John - Digby (lo_build.py, line cpbof; CP public timetable, April 1948, Brendan): S.S. Princess Helene, daily except Sunday, Saint John 7.30 a.m.
  - Digby 10.30 a.m., Digby 3.15 p.m. - Saint John 6.00 p.m. (Atlantic; dry dock April 25 - May 18 is outside the modelled week). Ports at Brendan's points:
  Saint John Long Wharf (-66.068242, 45.273589) and Digby Wharf (-65.752175, 44.626581); their own stops (steamer landings), livery cpss, agency CP; BOF_BOX
  added to the water tiles; GTFS LINES[13].
- Joint stations (Brendan, 10 Nov 2026): the DAR uses the CN stations at Halifax, Bedford, Windsor Junction, Truro and Middleton: merge_stations.py (CP_HALIFAX, CP_MIDDLETON,
  CP_BEDFORD_ONCP900, CP_WINDSOR_JUNCTION, CP_TRURO into the CN ids). Windsor Junction moved to Brendan's point (-63.639806, 44.786472), about 15 m from both
  the CN and DAR traces, in every file that places it.
- TODO.md: new section "Mileage to review" (Brendan: flag big gaps between printed and traced miles), from an ON_DRY run of the Maritime files. The largest:
  Halifax - Yarmouth +9.7 mi (Liverpool - Barrington Passage), Halifax - Sydney +3.2, Stellarton - Sunny Brae +2.3.
- Bedford goes in MERGE_AFTER (the DAR's id is CP_BEDFORD_ONCP900 only after split_stops). Brendan, 10 Nov 2026: Middleton is a joint CN / DAR station too.
- Checks: check_gtfs 1 known problem; 556 lines, 4061 trips, 6376 stops (5 DAR stops merged into CN's, 2 steamer landings added). No train's times changed.

## Version 154 (10 November 2026): Dominion Atlantic timetables
- Official Guide, April 1948, the DAR page (Brendan, 10 Nov 2026; Atlantic standard). Files (the guide numbers no DAR tables; keys oncp900*):
  on_cp_t900.csv Yarmouth - Digby - Kentville - Windsor - Halifax (100, 98, 96, 34 / 95, 97, 33, 99; 217.3 mi traced / 217.5), on_cp_t900w.csv Windsor -
  Truro (1, 3 / 2, 4; 57.7 / 59), on_cp_t900k.csv Kentville - Kingsport (13 / 12; 14.1 / 14). Evangeline Wharf on boat days (No. 98b Tue / Thu / Sat, 95b
  Tue / Thu, 99b leaving Halifax Mon / Wed / Fri), times estimated. DAR_PLACES in on_build.py. short 'Dominion Atlantic', src 'Official Guide, April 1948'.
- Trip ids: the DAR's Nos. 12 / 13 repeat CP main-line numbers kept in another part (mainline_build), which the taken-set in ab_lines does not see: new spec
  option tidpfx (ab_lines.trips_of) and the DAR files use 'DAR' (DAR-12 ...). No existing trip id changed.
- Checks: check_gtfs 1 known problem; 555 lines, 4059 trips, 6379 stops. No existing line changed.

## Version 153 (10 November 2026): CP's New Brunswick track; the DAR drawn as CP
- Brendan (10 Nov 2026): the DAR looks like the other CP subsidiaries (E&N, Quebec Central): mar_import_dar.py now writes own cp; the DAR owns the Windsor Branch.
- CP's N.B. lines from the regional OSM export: tools/mar_import_osm_cp_nb.py -> traces/maritimes/cp_osm_nb.geojson (own cp, 96 lines, ~598 mi): seed = ways
  named as a CP subdivision or with a CP-family old operator, inside N.B. (Maine side left for the U.S. folders); bridges of under 4 km; fixed-point paths for
  unlabelled stretches (Fredericton Jct. - Fredericton 21.5, McAdam - Woodstock 51.9, Hartland - Aroostook 42.1, Aroostook - Grand Falls 19.8, Grand Falls -
  Edmundston 38.2, Perth - Plaster Rock 27.2, Gibson - Minto - Chipman 47.3, Chipman - Norton 44.1, Watt Jct. - St. Stephen 19.6); tie edges written out as
  short connectors. NOT in the export: Woodstock - Hartland; the Gibson Subdivision Gibson - about Upper Kingsclear.
- oncn023 had taken 1.9 mi of CP track at St. Leonard to reach the CGN point: its St. Leonard is now on the NTR (-67.92645, 47.15949); stations by mileage
  shifted a little (Napadogan, Juniper, Plaster Rock). No other line changed. check_gtfs 1 known problem.

## Version 152 (10 November 2026): CP Maritimes begins - Dominion Atlantic track
- Brendan's Wikipedia-map pull of the Dominion Atlantic (QGIS layer; the geojson staged from his computer): tools/mar_import_dar.py ->
  traces/maritimes/dar.geojson, own dar, 7 lines: Yarmouth - Digby 65.6 mi, Digby - Annapolis 20.4, Annapolis - Windsor 83.3, Windsor - Truro (Midland) 57.3,
  Windsor - Windsor Jct. (Windsor Branch) 31.4, Kentville - Kingsport (Cornwallis Valley) 13.8, North Mountain 14.8. Junction vertices put into the DAR
  lines (Annapolis, Middleton) and, on re-running mar_import_cgr.py, into the CN lines (Truro, Windsor Jct.).
- No timetables yet; no line on the page changed (rebuilt and compared with V151). Questions (livery, Windsor Branch ownership, Yarmouth) in TODO.md.

## Version 151 (10 November 2026): Brendan's regional OSM export fills the N.B. gaps
- Source: Brendan's OpenStreetMap export of N.B. and western N.S. (9 Nov 2026; "not a preferred source, but not rough"; labels inconsistent). New tool
  tools/mar_import_osm_region.py: shortest paths over the export's railway ways (rail / abandoned / razed; way ends within 80 m tied; ways of another railway
  can be made 5x dearer) between fixed points, ways of lines already on file dropped from the ends. Output: traces/maritimes/cn_osm_region.geojson (cn),
  cp_osm_region.geojson (CP Saint John Union - Westfield Beach), mcrp.geojson (Maritime Coal, Railway & Power, Maccan - Joggins Mines, 11.8 mi; not yet timetabled).
- Pieces (miles vs printed): Saint John E&NA end - Union Station 2.8 (replaces the estimated link); CP Union - Westfield Beach 13.9 (14.0); Valley line
  Westfield Beach - Fredericton 69.1 (69.8), Fredericton - Woodstock 63.6 (63.0), Woodstock - Centreville 24.4 (25.8); Kent Northern 26.2 (26.4); Nelson Jct. -
  Chatham - Loggieville (replaces the estimated Nelson tie); Oxford Jct. connector 0.2; International Railway Tide Head - St. Leonard 106.4.
- tools/mar_import_cgr.py: fid 9 (Wikipedia International Railway into Campbellton) -> check (set aside); NEW junction vertices: any end of a line in the other
  files within 30 m of a Wikipedia line gets a vertex put into that line there (the Wikipedia lines' vertices are km apart and the router ties at points).
- on_build: t024 Chatham by mileage (no force); t033 Oak Point, Gagetown, Oromocto by mileage; t036 Tide Head back to its CGN point on the Intercolonial;
  t047 Rexton by mileage. All on track: oncn033 171.3 / 172.6, oncn047 26.3 / 26.4, oncn024 17.8 / 17.7, oncn036 137.4 / 137.1.
- Changed vs V150: oncn004 (its Saint John stretch no longer broken), oncn024, oncn033, oncn036, oncn047; oncn023 stations moved < 100 m (junction vertices).
- Maccan: the MCR&P station is the CN station (Brendan, 9 Nov 2026) - for when the short lines are built (STAGED.md, TODO.md).
- Checks: check_gtfs 1 known problem; 552 lines, 4042 trips, 6348 stops.

## Version 150 (9 November 2026): Middleton - Bridgetown on the Middleton & Victoria Beach
- Brendan (9 Nov 2026): the Canadian Northern trace runs on to Port Wade. CN Table 37's Wednesday mixed trains (M255 / M256) Middleton - Bridgetown use CN's
  own Middleton & Victoria Beach Railway, not the Dominion Atlantic (Claude had assumed DAR running; wrong). The importer had the whole line 'check'; it is
  now split at Bridgetown: Middleton - Bridgetown ok (13.3 mi; 14.4 printed), Bridgetown - Port Wade still 'check' (no 1948 train found).
- Bridgetown moved onto that line (-65.29019, 44.84499). oncn037: 67.4 mi traced, 69.4 printed, all on track.

## Version 149 (9 November 2026): the Pictou County lines are CN
- Brendan (9 Nov 2026): the Nova Scotia Coal Co., Acadia Coal Co., Nova Scotia Steel and Coal Co. and Vale Railway pieces are on the Wikipedia map because they
  were part of the CGR, so CN from 1923. tools/mar_import_cgr.py: NOT_CN emptied, all four owner cn in cn.geojson; industrial.geojson removed (empty).
- Only the drawing changed: oncn029 (Pictou), oncn039 (Thorburn) and oncn045 (Sunny Brae) now run on CN track throughout; no route or station moved.
- Checks: check_gtfs 1 known problem; 552 lines, 4042 trips, 6348 stops.
- TODO.md (9 Nov 2026) merges OPEN_QUESTIONS.md and the STATE.md TO DO lists: the one list from now on.

## Version 148 (9 November 2026): CN page 1117 - the last of CN's Canadian timetables
- New: t032 Mount Stewart Jct. - Montague - Georgetown (in and out of Montague; 37.0 / 36.7); t033 Saint John - Fredericton - Woodstock - Centreville (NO TRACK
  on file: broken straight estimates, 135.5 / 172.6); t034 Fredericton - McGivney - Blackville - Newcastle (Nos. 28 / 27, which replace on_cn_t023f, and the
  Mon / Wed / Fri motors, end times only; 113.8 / 114.4); t036 Campbellton - St. Leonard - Edmundston (International Railway; 137.0 / 137.1); t037 Bridgewater -
  New Germany - Middleton - Bridgetown (Middleton - Bridgetown on the Middleton & Victoria Beach (CN), see V150); t037a Bridgewater - New Germany - Caledonia (through Caledonia
  Jct. to New Germany and back; 39.8 / 39.5); t039 New Glasgow - Thorburn (Vale Railway); t041 Bathurst - Caraquet - Shippigan - Tracadie (in and out of
  Shippigan; 89.1 / 91.1); t045 New Glasgow - Stellarton - Sunny Brae (over the NSS&C railway; forced, 16.4 / 14.1 from Stellarton); t047 Richibucto - Kent Jct.
  (no track: straight estimate).
- on_cn_t023 gains Table 32a's Moncton - McGivney stations (North Branch, Chipman, Hardwood Ridge, Bantalor).
- Track: links_estimated adds the Pokemouche Junction tie (0.2 km, solid). Places: MAR_PLACES gains the page's points (CGN within 200 m of track; track ends
  Montague, Georgetown, Caledonia, Middleton (NS Central end), Thorburn, Sunny Brae; junctions Montague Jct., Caledonia Jct., Pokemouche Jct.; no-track lines
  at CGN points), plus CN Edmundston. t041's Tracadie is N.B.'s (own places); t005 pins N.S.'s Tracadie where it was. t036: Tide Head by mileage (noplace).
- Checks: check_gtfs 1 known problem; 552 lines, 4042 trips, 6348 stops. Compared with V147: only oncn023 changed among existing lines (oncn023f gone), 10 new.
- NEXT: trip chaining across the CN Maritime files (Brendan, 8 Nov 2026: "when we get all the CN maritime files in"; plan in staged/maritimes/STAGED.md).

## Version 147 (9 November 2026): the queued fixes (Brendan)
- Steamers: the NFR Cabot Strait steamer has no number or vessel (no label until clicked); Eastern Steamship Lines: S.S. Yarmouth (num / vessel 'Yarmouth'), Boston
  at Central Wharf (-71.0497, 42.3593, approximate), notes cite the ESL page's EDT times (the same instants as CN's Eastern standard ones; times unchanged).
- Broken (dashed) estimated links: a track-bank or Brendan-folder feature with "est": true is drawn as a straight estimate (on_lines draws it as owner 'est';
  ab_lines turns that stretch into an est segment). Marked: Saint John, Yarmouth, NFR Port-aux-Basques, NFR Argentia, NTR St. Isidore gap, Mirabel - St. Raymond
  tie, Great Western through Chatham, MC Detroit River tunnel. Solid: ties under ~0.5 km and the links Brendan asked for.
- North Sydney (Brendan's map, staged/maritimes/north_sydney_route_brendan.png): tools/mar_import_cgr.py splits fid 31 (old line round Little Bras d'Or, pre1948)
  and fid 30 (old North Sydney branch by old Sydney Mines, pre1948; the ferry-terminal spur stays ok). Importer re-run on the GeoPackage. Halifax - Sydney now
  291.5 mi traced (288.3 printed).
- Mulgrave - Point Tupper: train ferry in ferries.geojson (own water; removed from links_estimated). on_cn_t005: Mulgrave and Point Tupper rows ar / lv with a
  third of the printed interval held at each slip; new row "Mulgrave switchback" (185.5, tail end of Brendan's trace 98, ~3 min from Mulgrave) so the trains run
  out to the tail and back into Mulgrave.
- Campbellton: Brendan's point (-66.678886, 48.004637) everywhere (MAR_PLACES, on_cn_t001, t001a, t001s); the stray loop onto the International is gone.
  CN Edmundston: Brendan's point (-68.335511, 47.36165) for on_cn_t023 (the Temiscouata keeps its own).
- Checks: check_gtfs 1 known problem; 543 lines, 4009 trips, 6297 stops. Changed vs V146: the lines with new broken stretches (onmc006, onnfr001, onnfr003,
  oncn004, oncn009, oncn023, oncn070, oncn090w) and oncn001, oncn001a, oncn001s, oncn005, oncn013, esl.

## Version 146 (9 November 2026): CN page 1116 (Table 23 N.B. part, Newcastle - Loggieville, Pictou, P.E.I.), Borden - Cape Tormentine train ferry
- on_cn_t023 now runs Moncton - Pacific Junction - McGivney - Edmundston - Quebec (Table 23's N.B. part added; Nos. 51 / 52 taken out of on_cn_t001s). No. 51 Mon /
  Wed / Fri from Moncton. No. 52 from Quebec Tue / Thu / Sat reaches Edmundston 4.30 a.m. and leaves 6.00 a.m. Mon / Wed / Fri, so the Saturday train lies over until
  Monday: entered as 52 (Tue, Thu, through), 52s (Sat, Quebec - Edmundston), 52m (Mon, Edmundston - Moncton). 475.1 mi traced / 473.3. on_cn_t023f: Fredericton -
  McGivney, Nos. 28 / 27 (35.0 / 35.6).
- New: t024 Newcastle - Chatham - Loggieville (motors; 20.5 / 17.7, see Nelson below); t025 Charlottetown - Souris (60.1 / 60.1); t027 Charlottetown - Vernon -
  Murray Harbor (out and back to Vernon from Lake Verde; 54.4 / 55.7); t028 Charlottetown - Borden - Cape Tormentine - Sackville (39, 40, M41, M42 through on the
  car ferry; M206 Borden - Charlottetown; 89.0 / 88.7); t029 New Glasgow - Pictou (16.1 / 15.9); t030 Hopewell - New Glasgow - Pictou Landing (17.0 / 16.2); t031
  Charlottetown - Summerside - Tignish (115.9 / 115.7); t031a Elmira - Souris (14.9 / 14.7); t031b Summerside - Emerald Jct. - Borden, M207 (29.0 / 28.8).
  Not entered: Nos. 301 / 302 P.E.I. motors (last trips May 22 / 23), Table 31a's spring-only mixed trains, Table 28's connection rows (other tables).
- TRAIN FERRY Borden - Cape Tormentine (Brendan, 9 Nov 2026: like CN at Detroit): traces/maritimes/ferries.geojson, own 'water' (dotted water line; the train itself
  crosses), straight between the pier-track ends. Rows Borden (ferry slip) 43.0 and Cape Tormentine (ferry slip) 52.5 as printed; the trains creep the 0.8 mi between
  station and slip in the printed 15 - 45 min.
- Track: fid 26 (Harmony Jct. - Elmira, 9.9 mi = Table 31a) and fid 20 (Emerald Jct. - Kinkora - Albany, the Cape Traverse branch, which the Borden branch leaves)
  set ok in the importer. links_estimated: Nelson, a 0.2 km tie where the Intercolonial and the Chatham Branch cross (no junction in the Wikipedia data); on_build
  forces Derby Jct. - Chatham onto that track (printed Nelson Jct. is 1.4 mi short of the crossing: real connection wanted).
- Places: MAR_PLACES gains the page's CGN points within 200 m of track plus hand points (track ends: Fredericton, Loggieville, Pictou Landing, Murray Harbor, Vernon,
  Elmira, the two slips; junctions: Lake Verde, Emerald Jct.; projected: Charlottetown, Summerside; as on existing lines: Newcastle, Sackville, Stellarton, Pictou).
  MAR_PE (P.E.I. files) drops N.S.'s St. Peters and Bedford. noplace: St. Charles (t025). t024: Chatham at the Chatham Branch end.
- Mixed trains entered as plain numbers with kind=mixed (the page adds the M).
- Checks: check_gtfs 1 known problem; 543 lines, 4009 trips, 6296 stops, 52 agencies. Compared with V145: only oncn023 changed among existing lines, plus the 10 new.
- KNOWN: the Pictou trains run Stellarton - Westville over the coal companies' tracks (no CN piece joins the Pictou Town Branch; 1.2 km gap). oncn023 turns in
  0.7 km to Brendan's Edmundston point (stub cut). Open questions: TODO.md (was OPEN_QUESTIONS.md).
- NEXT: the queued fixes (TODO.md "Fixes queued") when Brendan says; trip chaining across the CN Maritime files; CP Maritimes.

## Version 145 (9 November 2026): CN page 1115 (Halifax - Sydney, N.S. branches, N.B. branches), Cabot Strait and Yarmouth - Boston steamers
- Timetables (Atlantic time, shift -4 h, places MAR_PLACES; each spur its own file so trains don't detour onto it): on_cn_t005 Halifax - Sydney (5, 7, 9 /
  6, 8 Sun-Fri, 8s Sat (Truro 6.10), 10; 286.5 traced / 288.3 printed); t007 Dartmouth - Upper Musquodoboit (68.8 / 69.3); t008 Point Tupper - Inverness (61.9 /
  61.6); t008a Point Tupper - St. Peters (29.4 / 28.9); t009 Halifax - Yarmouth (259.7 / 250: Lockeport in and out); t009a Mahone Bay - Lunenburg (6.8 / 6.6);
  t010 Moncton - Buctouche, Thursday only (32.7 / 32.4); t011 Halifax - Windsor Jct. - Waverley - Dartmouth motors 385, 381, 386, 378, 382 and 247 / 248 (29.2 /
  28.2); t012 Moncton - Point du Chene (19.2 / 18.6); t013 Campbellton - Dalhousie (15.9 / 15.1); t014 Moncton - Albert (57.9 / 58.1); t015 Moncton - Elgin
  (36.8 / 36.9); t015a Moncton - Havelock (35.0 / 35.3).
- on_cn_t004 restructured: Nos. 5 - 10 moved to t005 and the Waverley motors to t011; 23 trains left (379/380/383/384, 11, 20, 39 - 42, 13, 13s, 19, 43, 12, 14,
  44, 351 - 358). New files are in on_build's LAST set so older trip ids don't move.
- Track: traces/maritimes/cn_osm_sydney.geojson, Brendan's OSM export of the Sydney Subdivision (43 ways): the main was rerouted after the Intercolonial, and in
  1948 trains briefly use the North Sydney ferry-terminal spur before going on to Sydney. The North Sydney wye trace was scrapped (Brendan). links_estimated.geojson
  adds the Strait of Canso car-ferry link (Mulgrave - Point Tupper pier ends), Newfoundland Railway trace end - Port-aux-Basques (Brendan's point 47.5807910,
  -59.1423107, own nfr; the NFR now terminates there) and Yarmouth track end - Brendan's Yarmouth station point. All three wait for traces.
- Steamers (lo_build.py, GTFS LINES[11], [12]): Newfoundland Railway North Sydney - Port aux Basques (SaTuTh east / Mo, We, Fr west; livery nfr, agency NFR;
  Newfoundland time = Atlantic + 0.5 h); Eastern Steamship Lines Yarmouth - Boston India Wharf (Brendan's points; Yarmouth TuThSu 6.30 p.m. - Boston 7.30 a.m.,
  Boston MoWeFr 3.30 p.m. - Yarmouth 7.30 a.m.; Boston on EST; livery esl, new agency ESL, placeholder colour #7a2430). Tile boxes NFS_BOX, ESL_BOX.
- Fixed: the L&PS's Yarmouth, Ont. had been given Nova Scotia's point (a duplicate key in its places dict) - back at (-81.19345, 42.811999). Compared with the V144
  page, only onnfr001 (Port-aux-Basques), ontem001, oncn001 and oncn001a moved (all intended).
- Checks: check_gtfs 1 known problem; 533 lines, 3958 trips, 6231 stops, 52 agencies.
- TO CHECK (Brendan): No. 20 Folly Lake f3.35 (f3.25?); the second No. 13 (Sunday only); the "b" sign on 379 / 380; 382 dagger vs k; No. 26 dagger; 253 / 260 "-14"
  columns at Salisbury 1.35; traces for Saint John, Yarmouth and the NFR at Port-aux-Basques; approximate points (Halifax, Newcastle, Bathurst, Oxford, the ferry
  slips); is Dartmouth fid 40 the Narrows bridge line?
- NEXT: Table 23 N.B. part, Table 6 (Pictou) connections, P.E.I.; then trip chaining across the CN Maritime files (staged/maritimes/STAGED.md).

## Version 144 (8 November 2026): CN Table 4, Halifax - Truro - Moncton - Saint John (page 1114)
- Page numbers corrected (Brendan): Tables 1, 1a, 2 are page 1113 (not 1118); Table 4 is page 1114.
- on_cn_t001: the Halifax - Moncton stops of Nos. 1, 59, 3 / 2, 4, 60 from Table 4 (Moncton: ar / lv for all six). Halifax - Montreal 843.4 / 840.0 mi.
- on_cn_t001s now Moncton - Campbellton (25 / 26) and Moncton - Pacific Junction (51 / 52): Table 4 shows the Saint John times in Table 1 are connections
  (Brendan was right): No. 44 Saint John 7.05 a.m. - Moncton for 25, No. 14 for 51, No. 13 Moncton 2.55 p.m. - Saint John for 26 / 52 (in the notes).
- on_cn_t004 (new, 34 trains, 277.7 / 278.1 mi): Halifax - Windsor Jct. / Elmsdale motor trains 378 - 385; Halifax - Truro 5, 7, 9 / 6, 8, 8 (Sunday), 10;
  Truro - Moncton 11 (ex Sat) / 20; Sackville - Moncton 39, 41 / 40, 42 (41 / 42 June 28 - Sept. 11); Moncton - Saint John 13 (Psi: daily in July), 13 (Sunday-only
  column, TO CHECK), 19, 43 / 12, 14, 44; Saint John motor trains 351, 355, 357 / 352, 354, 358. Column pairs (3-13, 14-60, 7-11, 77-19, 20-12) entered as
  separate trains. NOT entered: the Painsec Junction - Moncton pieces of the Point du Chene / Buctouche trains (77, 279, 289 / 276, 292, 78): with their own
  table. Signs: "b" on 379 / 380 read as daily except Sat and Sun (complements 383 / 384 Sat only); 'ex Sat' is written "Sun,Mon,...,Fri" (ab_table has no
  "ex Sat").
- Places: Moncton = Brendan's station point (46.083305, -64.785932); traced Painsec Jct. - Moncton 7.6 mi (printed 6.9) and Moncton - Pacific Jct. 11.3 (12.2):
  the printed miles would put the station ~0.7 mi further east (kept as given). Saint John (Table 4) = Union Station with the estimated link. CGN points within
  200 m of the line for the Halifax - Saint John stations; the rest by mileage (Truro among them).
- Track: traces/maritimes/brendan_truro.geojson, Brendan's Truro Wye (trains now take it: Halifax - Moncton 0.5 mi shorter). Brendan's later traces go in
  brendan_<area>.geojson files.
- Checks: check_gtfs 1 known problem; ab.py: oncn001 / oncn001s moved (the new stops), oncn001s' Saint John part gone, oncn004 new. 518 lines, 3901 trips, 6141 stops.
- TO CHECK (Brendan): No. 20 Folly Lake f3.35 - Londonderry 3.41 a.m. (7.6 mi in 6 min: f3.25?); the second No. 13 column (Sunday only, Moncton 4.30 p.m.).

## Version 143 (8 November 2026): the Maritimes begin (Temiscouata in N.B.; CN page 1113: Tables 1, 1a, 2)
- MARITIME TRACK BANK: pipeline/traces/maritimes/ (README there: one file per owner or provenance; properties own, name, constituent, branch, note, cost, fid, group,
  status; status says only whether the TRACK was there in 1948: ok / check / post1948 / pre1948 / quebec_overlap). Read as one set by mar_tracks.py
  (features(owner=, status=, box=, dirs=); `python3 mar_tracks.py` = what is on file, connected groups, loose ends within 1.5 km). Files: cn.geojson (Wikipedia
  Canadian Government Railways map data, Brendan's CN_Maritimes.gpkg, plus the Inverness & Richmond, Halifax & South Western, Middleton & Victoria Beach from
  cnor_all.geojson), brendan.geojson (his Mulgrave - Point Tupper, Port Hawkesbury and Halifax North Street - Deepwater Terminal traces; Wikipedia track under them
  cut), tem.geojson / tem_osm.geojson (Temiscouata: Wikipedia N.B. part; OSM export by Brendan: Edmundston station leg, Connors branch from Baker Brook Junction,
  the 1941-abandoned riverside line as pre1948), industrial.geojson (colliery railways), links_estimated.geojson (Saint John: E&NA track end - Union Station,
  4.5 km straight, until Brendan's trace). Importers (one-shot records): tools/mar_import_cgr.py, tools/mar_import_osm_tem.py.
- U.S. railways (future) get folders of their own under traces/ (traces/mec, traces/bar ...), as do Canadian railways' tracks in the U.S. (CP across Maine:
  e.g. traces/cpme); plain own codes, no region prefix. mar_tracks.DIRS / dirs= borrows them where a Maritime line meets them.
- on_lines._links() now also reads the Maritime bank ('ok' pieces; read once); BOXES['tem'] to 47.15 N. steps.json: input_globs traces/maritimes/*.geojson for
  on_build and lob_build. The Maritime lines are built in on_build (Brendan: so through trains are one trip).
- Places: places/cgn_nb_places.csv, cgn_ns_places.csv, cgn_pe_places.csv (Brendan's CGN files, cut by tools/cgn_places.py; full files to go to the private repo).
- on_tem_t001 now to St. Jacques Church and Edmundston (81.5 / 81.5 mi); on_tem_t003 mixed 3 / 4 Edmundston - Baker Brook Junction (CN NTR by trackage rights,
  drawn CN) - Baker Brook - Clairs - Connors (31.1 / 31.6). Edmundston = Brendan's point, the CP / Temiscouata station (to share with CP later); Baker Brook
  Junction (-68.4950083, 47.3039499) Brendan's.
- on_cn_t001: the N.B. rows (Halifax, Moncton ... Newcastle, Bathurst ... Campbellton, Tide Head, Flatlands); the estimated boundary row gone (843.9 / 840.0 mi).
  Nos. 1 / 2: dagger at Halifax / Moncton only, daily west of Campbellton (Brendan): through trips on six days (CN-1-ONCN001 Mon - Sat, CN-2-ONCN001 Sun - Fri) plus
  the seventh day's Campbellton - Montreal run under the same number (CN-1-ONCN001-ONCN001, CN-2-ONCN001-ONCN001). Saint John times of 1 / 59 / 3 / 2 / 60 / 4
  are connections (notes). Atlantic rows to Campbellton, Eastern beyond (tzrows; Campbellton's E.T. departures entered +1 h); OVER tznote (new key) for the
  mixed-zone note. on_cn_t001s: 25 / 26 Saint John - Campbellton, 51 / 52 Saint John - Pacific Junction (Mon, Wed, Fri; on by the NTR, Table 23 N.B. part not in
  hand); Saint John = Union Station (Brendan, 45.276776, -66.064504); Saint John's mile 99.3 is Claude's (89.4 to Moncton; traced 277.0 / 276.3).
  on_cn_t001a: 36 / 35 from / to Campbellton. on_cn_t002 Oxford Jn. - Pugwash - Pictou motor 334 / 333 (into Pugwash and back), 332 / 331 Oxford Jn. - Oxford
  (78.0 / 78.4). New files sort LAST in on_build so no older trip id changes (CN 332, 51, 52 are also Rutland / CV numbers).
- Places (on_build OVER): CGN points on the line; Halifax = end of Brendan's trace 118 (South End station, APPROXIMATE: confirm); Moncton on the line at the printed
  12.2 mi from Pacific Junction (APPROXIMATE); Newcastle, Bathurst, Oxford: CGN town snapped onto the line (APPROXIMATE). By mileage: Berry Mills, Canaan, Kent Jn.,
  Barnaby River, Bartibog, Petit Rocher, Belledune, Jacquet River, New Mills, Eel River, McLeod, Baker Brook, Ledges, Little River Mills, Pugwash Jn., Wallace,
  Malagash, River John, Meadowville, Brown Point (Brendan may send points).
- Page: view "The Maritimes" (VIEWS maritimes, turned box 'q').
- Checks: check_gtfs 1 problem (the known Minneapolis one); ab.py: only oncn001 moved (CN-1-ONCN001, the days), new oncn001s, oncn002, ontem003 and the N.B. rows.
  517 lines, 3867 trips, 6097 stops.
- STILL NEEDED (Halifax - Moncton and Saint John - Moncton came in Version 144): Table 23 N.B. part; Saint John track trace; Oxford Jn. connector (MESL - Intercolonial
  204 m: the 002 trains found track anyway); No. 26 dagger at Campbellton (kept daily); Temiscouata No. 4 Baker Brook 8.15 - Edmundston 9.15 as read.
- TO DO (Brendan, 8 Nov 2026): trip chaining across files and steps when all the CN Maritime files are in (then again for CP): plan in staged/maritimes/STAGED.md
  (railway + number at the same stop, days compatible, auto under an hour, named trains only when the names agree, review list, GTFS block_id).
- TO DO, short lines (stage 3): Maritime Coal, Railway & Power; Sydney & Louisburg. Order (Brendan): 1 CN Maritimes, 2 CP Maritimes, 3 short lines, 4 U.S. connections.

## Version 142 (7 November 2026): Chicago, Duluth and Georgian Bay Transit Co.
- New step cdgb_build.py (after cp_manitoba_build; lane cache cdgb_legs.json), four lines, one weekly sailing each, from the Official Guide, May 1948 (page supplied by Brendan):
  cdna_e North American Chicago Sat 6.30p CST - Mackinac Island - Cove Island - Parry Sound (Town Dock) - St. Clair River - Detroit - Cleveland - Buffalo Wed 11.30a;
  cdna_w Buffalo Wed 7.30p - Detroit - Mackinac - Chicago Sat 10.45a CST; cdsa_w South American Buffalo Sat 8.30p - Cleveland - Detroit - St. Mary's River - Soo Locks -
  Houghton (Keweenaw Waterway) - Isle Royale - Port Arthur (C.P.R. Dock) - Duluth (N.P. Dock No. 4) Wed 9.00a CST; cdsa_e Duluth Wed 2.00p CST - Soo - Detroit - Buffalo Sat 11.00a.
- Ports from Brendan (Buffalo = the Lackawanna (D.L.&W.) depot, for a future DL&W line); Port Arthur and Duluth are the existing CP / Noronic stops. Printed passing
  points (Cove Island, St. Clair River, St. Mary's River at De Tour, Soo Locks, Isle Royale) are page timing points only, not GTFS stops (gids PASS_CDGB_*).
- Keweenaw Waterway is in neither lane layer: traced by hand off the basemap water (KEW_IN / KEW_OUT). Livery cdgb is a placeholder teal (#1d6b6b / #6cc5c5).
- Each boat is one ship (turnarounds: N.A. Buffalo 8 h, Chicago 7.75 h; S.A. Duluth 5 h, Buffalo 9.5 h).

## Version 141 (7 November 2026): C.S.L. boats named
- The boats carry their names (shown as the boat label, like the car ferry Ontario): Cayuga (Queenston - Toronto) and Kingston (lake steamer), both from a 1949-season account (Thousand Islands Life, "Niagara
  to the Sea"); Rapids Prince (the only rapids boat running by then: Rapids King laid up 1931, Rapids Queen retired 1929). Saguenay: "One of the Bateaux
  Blancs, the white fleet" (Brendan: the four Saguenay boats, Tadoussac, St. Lawrence, Quebec, Richelieu; the timetable needs three).

## Version 140 (7 November 2026): full rebuild
- Full build after the ab_lines.py change: motor trains are now flagged in the code (142 trips), not hand-patched parts. Train 77 (on_cn_t082d) runs over the
  CP from Prescott Junction into Prescott (by the wharf). Ridgeway and the H&LB minor landings are in. check_gtfs: 510 routes, 3851 trips; one problem, already known:
  CP-14-SKJCP13 at Minneapolis (the 1947 Soo arrival, 6.30 a.m., is after C&NW 404's 6.25 departure, as the note says).

## Version 139 (7 November 2026): Canada Steamship Lines, Lake Ontario - St. Lawrence - Saguenay
- From Brendan's Sailing Schedules season 1948 pages (dmr-sources scans/marine/csl_1948_*), Eastern Standard time as printed; ports: Brendan's points; Three Rivers and
  Quebec are the existing ferry wharves (TSL_THREE_RIVERS_FERRY_WHARF, QLF_QUEBEC_FERRY_WHARF, shared stops). All in lo_build.py, livery csl, agency CSL.
- csqt Toronto - Niagara-on-the-Lake - Queenston: Mon - Fri and Sat/Sun columns (summer); the Niagara Falls - Queenston motor coach (Canada Coach Lines) is a bus, not drawn.
- cslk lake steamer Toronto - Rochester (Municipal Dock) - Kingston - Alexandria Bay - Brockville - Prescott Dock: east Sat, Mon, Wed 1.30 p.m. (no Brockville call); west
  Sun, Tue, Thu from Prescott noon, Toronto 6.45 a.m. next day.
- csrp rapids steamer Prescott - Cornwall - Montreal (Victoria Pier), DOWNSTREAM ONLY (Brendan), Sun, Tue, Thu 7.45 a.m. - 6.30 p.m. Waypoints keep it on the old river through
  Soulanges (Coteau, the Cedars, the Cascades), not the modern Beauharnois power canal. Cornwall on the Cornwall Canal remnant (in the tiles). Lane mileage is grid-jagged (147 mi).
- DONE in Version 140: the westbound CN special (train 77) Montreal 8.50 a.m. - Cornwall 10.32 - Prescott 11.40 a.m., Sun, Tue, Thu, over the CP from Prescott Junction.
- cssg Montreal - Sorel - Three Rivers - Quebec - Murray Bay - St. Simeon - Tadoussac - Bagotville (St. Alphonse): daily both ways, two nights each way.

## Version 138 (7 November 2026): Muskoka Lakes steamers
- Muskoka Lakes Navigation Co., in lo_build.py; landings: Brendan's points (Bala = the CP station, Muskoka Wharf = the CN Gravenhurst wharf station, shared stops).
  Eastern Standard time as printed (both tables). Colour --mln #1f4e79 (dark #7fb0e0), agency MLN.
- CN (Table 126, og1948_on/cn126b.png), line mlcn Muskoka Wharf - Beaumaris - Port Carling - Wigwassan - Royal Muskoka: down 7.30 a.m. ex Sun (Sun 8.30,
  sign g) and 2.00 p.m. ex Sun (55-53 column; the 41 column's 1.45, June 14 - 24 only, left out); up 8.30 a.m. and 3.10 p.m. ex Sun, 3.45 p.m. Sun (156).
- CP (marine/on_muskoka_lakes_1948.csv), READING (Claude; Brendan, 7 Nov 2026: no better source short of the archives, keep it): the dagger (ex Sun) is on exactly the Lake Joseph landings, so a Lake
  Joseph boat (line mlj: Minett - Elgin House - Natural Park, ex Sun) meets the Bala boats at Minett; the two Bala boats (line mlcp: Bala - Beaumaris -
  Port Carling - Windermere - Wigwassan - Royal Muskoka - Minett - Rosseau) run daily: 7.30 a.m. (passes Beaumaris) - Rosseau 12.00, back 2.00 - Bala 7.00;
  2.00 p.m. - Rosseau 7.30, back 7.30 a.m. - Bala 11.40. Misprint read: Beaumaris 3.30 p.m. on the boat to Bala -> 5.30 estimated.
- WATER: the Port Carling canal (locks between the two ends of the Indian River) is missing from the basemap (Brendan): added in lo_build as a 30 m
  corridor. Port Sandfield (Rosseau - Joseph) is open in the tiles. The canal is not drawn on the map, only routed.

## Version 137 (7 November 2026): Pointe au Baril Island Transport
- Fred G. Barned's island boats on Georgian Bay, from the CP guide boat schedule (dmr-sources scans/cp1948_on/pab_island_transport.png), June 1 - Sept. 6
  table, Eastern Standard time (the 3.45 p.m. boat leaves after train 25, Pointe au Baril 3.29 p.m., CP Table 58). Landings: Brendan's Google Earth points.
- TWO BOATS (Brendan): they leave the Government Wharf together. Skerryvore boat (line pabs): out 45 min; its return is by appointment, so estimated
  (leaves 15 min after arriving, 45 min back). Ojibway boat (line pabo, a loop): Pointe au Baril - Bellevue - Ojibway - Pointe au Baril; the Sunday evening
  "Lv Bellevue 6.30" read as its Bellevue call. Daily ex Sun 6.30 a.m. and 3.45 p.m.; Sunday 7.30 a.m. and 5.30 p.m. May tri-weekly service left out.
- In lo_build.py (water for a second box, PAB_BOX, from the basemap tiles; lanes at 25 m). Colour --pab #8b4a2b (dark #d68a5f), agency PABIT.
- Run alone with build.stale_reason patched to 'lo_build' only, so the 14 steps still marked stale by the ab_lines change (Version 136) were left alone.

## Version 136 (6 November 2026): motor trains drawn like interurbans
- Brendan: known motor trains look like interurbans but run on the regular track. ab_lines emits motor=1 for kind=motor (all 153 tagged trains; 142 trips
  on the page, the rest are not built: GTW 34 / 35, three unnumbered Table 77 trips fold in elsewhere); page_template carries t.motor and drawConsist treats it
  as inter: four cars, no black locomotive, direction nose, in the RAILWAY'S colour (CP red, CN green ...). Track and station drawing unchanged (line kind decides).
- This version patched parts/*.json (motor=1 where name == 'Motor train', identical to what ab_lines now emits) and ran --assemble; the next full build
  reruns every ab_lines step because ab_lines.py changed (about 70 min). Untagged files only print the sign key, or motor BUSES; sk_cn_t212 dot left untagged.

- B.C. Electric livery (Brendan, 6 Nov 2026, 23:00): red and cream. Every BCER car (KIND_COLOR 'bcer', no line livery) gets a cream band (--bcer-cream #fff0c2,
  both themes) along its middle, like the WP&Y / SI gold bands, so the unnumbered cars no longer vanish on the red track. Legend swatch: red with a cream stripe.
## Version 135 (5 November 2026): Niagara, St. Catharines & Toronto; CN steamers Toronto - Port Dalhousie; Cobourg - Genesee car ferry; Newfoundland Railway
- New rail 'onnst' (kind 'N', own 'nst', CN colours like the M&SC, interurban style; agency NST). Track: Brendan's NS&T KMZ, stitched by scratchpad
  nst/track.py into traces/ontario/brendan/nst_track.geojson (St. Catharines Terminal - Lincoln Jct. - the high line - Thorold - Substation Jct.; Niagara
  Falls line - Bridge St. - Victoria Ave. - Tower Inn terminal; the wye's north leg and the Welland Division main line to Port Colborne; Geneva, St. Paul,
  James and Lake Streets and the Port Dalhousie Division to Lakeside Park). The NS&T uses its own links only, and nobody else uses them (as the M&SC).
  NOTE: the Welland Division main line is a Placemark straight under a Folder in the KMZ; an early parse missed it (Brendan caught it).
- CSVs from scratchpad on/nst.py, printed in daylight time, all an hour earlier: on_nst_t001 Thorold - Port Colborne (36), on_nst_t002 St. Catharines -
  Niagara Falls (39; Bridge and Victoria = Stop 69, Union Bus Terminal = Stop 70 / Tower Inn; the Niagara Falls, N.Y. leg left out: a bus transfer by
  1948, Brendan), on_nst_t003 Port Dalhousie cars every 20 minutes (from May 23; first and last cars as printed, 15 min each way estimated; 210).
  Every other KMZ stop a flag stop. Port Colborne = CN_PORT_COLBORNE (printed "C.N.R. Depot"). Thorold, Merritton, Niagara Falls stay separate from the CN.
- lo_build.py (new step after on_build): CN steamers Toronto (C.N.R. wharf) - Port Dalhousie (the CN station point), as printed May 21 - June 4; signs
  from the page's footnotes (Brendan; dmr-sources og1948_cnq/nst_cn_steamers_signs.png): disc Sunday and May 24, ) Monday May 31 (left out), square
  Friday and May 31, k Saturday, double dagger daily except Saturday. Crossing 2 h 30 (from the Saturday turns); ships per sailing estimated. Out of
  Toronto by the Eastern Gap (waypoints: the water lacks the Toronto Islands). Ontario Car Ferry Co. (CN / B&O, agency OCF) S.S. Ontario, Cobourg
  (C.N.R. wharf) - Genesee Docks, summer daily, Eastern time. Water: basemap tiles + water_east.json. Livery cnss.
- Page: kind N (label, badge NS&T, colour cn, --nst, interurban sets, kinds list, legend).
- (first build attempt failed: the NF track file was written into traces/ontario/brendan/ while on_build was reading it. Do not write traces during a build.)
- Newfoundland Railway (Brendan, 5 Nov 2026): rail 'onnfr' (kind 'W', own 'nfr', bright red #C8102E, agency NFR, steam style). Track: Wikipedia's Newfoundland
  Railway map data (CC-BY-4.0), traces/ontario/brendan/nfr_track.geojson (main line, Brigus cut-off and the Harbour Grace line, Carbonear, Placentia, Bonavista
  (one piece so the trains go round the Trinity Loop, which crosses itself where Wikipedia's two pieces met: Brendan), Lewisporte). Trepassey and Heart's
  Content branches left out (not in the Guide). Argentia branch ESTIMATED (straight, Argentia Jct. 1.0 mi short of the Placentia end to the CGN Argentia
  point): ask Brendan for a trace. Stations: CGN points (Brendan's cgn_nl_csv_eng.csv) snapped onto the track (scratchpad nf/places.py); St. John's
  Brendan's point; Stephenville = Stephenville Crossing; Holyrood, Tickle Harbour, Humbermouth, Curling, Trinity Junction by mileage. Every pair 'force'd
  (the printed whole miles and the Wikipedia trace differ by a mile here and there).
- CSVs from scratchpad on/nfr.py, schedule of January 11, 1948 (May 9 change not printed), Newfoundland time (row tz 'N', TZ_SHIFT -16200; page regex
  now reads "four and a half hours"): t001 main line (1, 15 to Millertown Jct., 2, 16 from Millertown Jct.), t002 Brigus branch mixed 7/8, t003 Argentia -
  Placentia mixed 5/6 (Placentia Jct. - Argentia Jct. - Placentia, back to Argentia Jct. - Argentia), t004 Bonavista mixed 27, 11, 12, 28, 24, t005 Lewisporte
  mixed (from the side note). Port-aux-Basques - North Sydney steamer: no times on the page, not built.
