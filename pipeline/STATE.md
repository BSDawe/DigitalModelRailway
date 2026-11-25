# The Digital Model Railway — project state

Read this first. It is meant to be enough to start a short, single-task chat without replaying the project's history.
Last updated 23 November 2026 (Version 219). This file is the current state and the standing rules; the version-by-version history is in CHANGELOG.md.

## What this is

Brendan Dawe's "digital model railroad": an animated map of passenger trains and steamers running to their summer-1948 timetables, from British Columbia, Alaska and
Washington across the Prairies, the Midwest, Ontario and Quebec to the Maritimes and Newfoundland, plus a GTFS feed of the same.
The target week is **Monday 5 to Sunday 11 July 1948**.

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
3. Do the one task. Re-run only what it touches (`python3 build.py`), check (see "Checks"), update this file and CHANGELOG.md (see "After each version"; the step table if a
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
| `atc_build` | atc_w, atc_e, atc_mc, atc_cm, atc_lc, atc_cl (Arnold Transit: St. Ignace, Mackinaw City, Les Cheneaux) | gtwf_build, dcn_build (the Arnold Dock) | water_east.json, basemap tiles, atc_legs.json (lane cache) |
| (on_build) `on_mc_t006*` | Michigan Central / N.Y.C. Chicago - New York (V210) | | traces/maritimes/mc.geojson (tools/mar_import_mc.py) |
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
- CN's Grand Trunk in New England (Norton - Portland, the Lewiston branch; traces/maritimes/cn_gtr.geojson) and the U.S. traces generally: **Mississippi Rails** (Tony Howe and David Price).
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

### Rules added in November 2026 (details in CHANGELOG.md under the version named)

- **The target week is Monday 5 - Sunday 11 July 1948.** Services that run less than weekly are shown by their real dated sailings in that week
  (`d0` on a trip: the day of the week it starts, which may be before Monday; single-day service codes). (V169)
- **Ships**: a ship is a passenger service if it was advertised for passengers, including passenger-carrying freighters (12 passengers);
  freighters not advertised that way are left out. No need to search for more of them. (V169 - V170)
- **The Newfoundland Railway** runs on the CN summer folder of May 1949 with the days and trains of the July 1948 notices; trains known only from
  the notices are estimated from the timetables (tools/nfr_1949.py). (V179)
- **Ships go by their schedules.** Only the Newfoundland Railway coastal boats, which had none, are drawn from reported positions (The Daily
  News, St. John's; `nfld/steamship_movements.md`), with the other calls put in between by distance. (V172)
- **Ocean liners** run from their Canadian port to the edge of the water file and then disappear; arrivals appear there (also the Denali and the
  Fort Amherst). They are in their own step, ocean_build.py, and list heading; North American coastal ships stay with the steamers (Bermuda counts as local). (V180)
- **A run is drawn whole**: ports along the same run that are not reached in the week are still part of the route (the Burgeo from Argentia). (V174)
- **Newfoundland outports** are minor stops; major stops are the railway connections, the ends of the runs and the larger towns (`NF_MAJOR`). (V173)
- **Record train links when transcribing** (Brendan, 21 Nov 2026): every new timetable file notes on its #train lines which trains continue under another number,
  split off as sections, join another train or carry through cars (`links="..."`, TIMETABLE_READING.md rule 8; ab_table.py). Not built into the page yet: Brendan
  decided against section links for now, but the information is to be kept.
  The Official Guide's through-train and car-service lists (with most railways' entries) are the authoritative source for through trains vs through cars vs
  connections (Brendan, 21 Nov 2026): transcribe them when supplied (CARS lines, TIMETABLE_READING.md rule 8); links read from timetable columns are provisional.
- **Number changes at Hamilton** (CN Table 79, printed in one column) are through trains: NUM_JOINS in real_ends.py (Brendan, 20 Nov 2026). (V204)
- **Through trains joined across pieces** need only overlap in their days; several partners on one side are allowed when their days are disjoint.
  Out-and-back joins are left alone. (V167)
- **Employee timetables**: S = stop, F = flag, L / A = leave / arrive; a plain time is a passing time, not a stop. (V168)
- **One spelling for one place** on the page and in the feed (`names.py`); the timetable files keep the name as printed. (V176)
- **Views set the clock**: choosing a view sets its time zone (`VIEW_TZ` in the page); local time is not the default otherwise. (V176)
- **State and province tags** (", Vt.", ", Mich." ...) stay in the data and the feed but are not shown on the page (shortName in the template; Brendan, 18 Nov 2026). Michigan station ids carry _MICH (on_lines.register).
- **Springfield, Mass.**: every railway's trains call at Springfield Union Station (42.106238, -72.593270), on the New York Central (Boston & Albany) line: NYC (B&A), B&M (and the Central Vermont trains it hosts) and the New Haven. North - south through trains reverse there (Brendan, 18 Nov 2026).
- **The Soo Line** and the **Duluth, South Shore & Atlantic** (CP subsidiaries) are drawn as CP with their own labels, Soo Line (like the Central Vermont and the GTW under CN; Brendan, 19 Nov 2026); its trains use the CP station at Sault Ste. Marie, Ont. The **B&O** is dark blue (#1D3461; Grand Central Station, Chicago, is B&O property). Short union / terminal railways (union depots, the C&WI) share one union-station colour, own 'union' (warm grey #8C8279; Brendan, 19 Nov 2026); a railway running through (the Milwaukee Road at St. Paul) keeps its own. Other railways' columns in a table (through-ticket arrangements) are not entered.
- **U.S. traces are from Mississippi Rails** (Tony Howe and David Price) unless Brendan says otherwise (17 Nov 2026); credit them so.
- **Train panels show the source and note for every railway** (Brendan, 23 Nov 2026: he likes the sources being available); a new kind needs no entry for it.
- **Test the page in a browser before every push** (V202 broke the page: a colour edit landed in the boat colour map).
- **Transcriptions** by another model follow `TIMETABLE_READING.md` (copy, don't interpret; check mode against an existing file).
- Scratch files and logs go in the session scratchpad, never in the repository.

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

## Checks

    python3 tools/ab.py            # positions of every train at 24 moments vs tools/.baseline_viz.json: only the lines you meant to change should move
    python3 tools/check_gtfs.py    # ids unique, references resolve, times run forward
    python3 tools/perf.py          # frame times by view; see "How the page draws"
    python3 tools/shots.py '[{"name":"x","T":37800,"view":"sound","sel":"359"}]'    # screenshot to tools/out/x.png; look at one or two, not all

After an accepted build: `cp viz_data.json tools/.baseline_viz.json`.
    python3 tools/check_speeds.py  # impossible speeds between consecutive calls (runs at every assembly; 3 known, see TODO.md); check_gtfs: 0 problems since V178

## Recent versions (one line each; the detail is in CHANGELOG.md)

- 219: Portland Traction Co., Portland - Oregon City (Time Table No. 2, February 1948; PRL&P KMZ track).
- 218: Clarke Steamship coastal services (North Shore, North Gaspé, Magdalen; the Rimouski / Matane motorships), simulated weekly schedules.
- 217: TH&B trains on to Black Rock and Buffalo (Central Terminal); train notes and sources shown for every railway.
- 216: the Texas Electric Railway (Dallas - Denison, Dallas - Waco; Ravenna's trace, 1939 times as the 1948 pattern).
- 215: D&H Albany / Troy routing (Green Island curve; no northerly Albany crossing); Norton N.B.; union station owners; Milwaukee Clipper, C. & B. Line, Put-in-Bay steamer.
- 214: the Gull one Maine Central train Saint John - Boston; Portland Union Station on track; Waterville, Bangor, McAdam points; Portland (Grand Trunk).
- 213: the Gull (Maine Central / B&M Boston - Portland - Bangor - Vanceboro); MC trains join the IC at Kensington.
- 212: CP Toronto - Windsor trains on to Detroit (Michigan Central Station).
- 211: Niagara and International bridges, Tonawanda bypass, Chicago approaches on track (IC brown), N.Y.C. Table 53, the Adirondack Division (Montreal - Utica, Lake Placid).
- 210: the Michigan Central Chicago - Detroit - Ontario - Buffalo and on to New York (N.Y.C. Tables 6, 7, 9, 11); Central Station and La Salle Street approaches dashed.
- 209: Seattle - Portland pool trains by operator (GN 401 / 402, 459 / 460; NP 407 / 408; UP 457 / 458); Saint John Union Station.
- 208: station names by zoom (city zoomed out, station zoomed in), CPR for CP, station owners from the track; North Bay ONR stops on the CN / CPR stations; Straits car ferry over water.
- 207: the Rutland Railroad (Tables 1, 4, 6; New York - Montreal through trains; Table 3 Boston waits for a B&M trace).
- 206: Troy Union Station over the Troy Union Railroad (union colour) and Brendan's Green Island bridge.
- 204: CN trains changing number at Hamilton (Table 79: 101/102, 89/90, 187/184, 93/94, 91/92, 107/108) joined as through trains.
- 200: Arnold Transit from the August 1950 Official Guide (stand-in for July 1948): five St. Ignace and five Mackinaw City sailings each way; Mackinac Island - Les Cheneaux - Cedarville.
- 199: the Straits of Mackinac car ferry drawn as a train ferry; Arnold Transit St. Ignace - Mackinac Island boats (atc_build.py).
- 198: the Duluth, South Shore & Atlantic and Mineral Range (Official Guide; drawn as CP, labelled DSS&A); Mackinac Straits car ferry; NP Ashland - Superior.
- 197: the Washingtonian and the Montrealer through to New York (Penn Station) and Washington over the New Haven, Hell Gate and the Pennsylvania (Brendan's NEC2 track).
- 181: Detroit and Cleveland Navigation Co. (dcn_build.py): Detroit - Cleveland, Detroit - Buffalo, and the cruises to Mackinac, Chicago, Harbor Springs, Midland.
- 180: ocean liners to the edge of the map's water, in their own step (ocean_build.py) and list heading; Island Connector; Fort Amherst and Denali cut at the edge.
- 179: the Newfoundland Railway on its summer schedule (May 1949 folder times, July 1948 notice days; tools/nfr_1949.py).
- 178: CP No. 14 arrives Minneapolis 6.10 a.m. (1948 C&NW timetable); the feed check is clean.
- 177: trips setting out between midnight and 3 a.m. Pacific shown the night before (the Bar Haven; 152 trips in all).
  search box; title; one spelling for one place; speed check at assembly; STATE.md split from CHANGELOG.md.
- 175: the North Sydney - Port aux Basques steamer named Cabot Strait.
- 172 - 174: the Newfoundland Railway coastal boats from reported positions; outports as minor stops; the Burgeo run whole.
- 169 - 171: Furness Red Cross and Blue Peter ships; Fort Amherst to Bermuda; ocean lanes kept off land; Argentia branch from OSM.
- 168: CN Montreal District employee timetable (June 1948): stations, Montreal Nord locals, Oka trains (ETT_MONTREAL_1948.md).
- 167: through-train joins on overlapping days.

## After each version

1. Add a "## Version N" section at the END of CHANGELOG.md (what changed, why, whose instruction, what is estimated).
2. In this file: the "Last updated" line, a line under "Recent versions" (drop the oldest when there are more than about eight), and any new
   standing rule under "Conventions Brendan has set". Update HANDOFF.md line 7 (version and counts) and TODO.md.
3. Commit, push the branch and main, watch the deploy, mirror STATE.md, HANDOFF.md and TODO.md to the claude.ai project (CHANGELOG.md is not
   mirrored: it is long and only searched).

## Export: trains per week (12 November 2026)
- tools/export_frequency.py (Brendan): a GeoJSON line file of trains per week on Canadian track, in total and by railway (CP with E&N / QC /
  DAR as "On the line"). Interurbans, boats and US track are left out, except CN through northern Minnesota (skcn155) and CP across Maine
  (oncp010, Vanceboro). tools/border.py: Canada / US side from Natural Earth 1:10m, with named exceptions near the rivers.
- Same track in two files: a piece between two stations takes another file's track when that file runs between the same stations at about the
  same length in the same place (gid paths); the rest are snapped to common nodes (60 m; 120 m for the same owner). Stubs: doubling back is
  taken out; a stub that leaves and rejoins by a different way is replaced by the shorter way already in the network. Each train counts once
  per edge per day it runs. Fields: trains_wk, trains_day, railways, files, one column per railway.
