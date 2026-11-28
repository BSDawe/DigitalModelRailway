# To do and open questions

One list for the Digital Model Railway: questions for Brendan, material he is to supply, and work for Claude. It merges OPEN_QUESTIONS.md with the TO DO lists that were kept in STATE.md (the last of them: "TO DO (1 November 2026)"), as Brendan asked on 9 Nov 2026.
Ideas not yet planned are in IDEAS.md. Claude adds items as they come up. When one is answered or done, it moves to "Done and answered" with the date. Each open item says what the build does in the meantime. Version tags (V143) say when an item was raised.
Last updated 27 November 2026 (Version 238).

## Decisions for Brendan
- [ ] Unnumbered connecting trains: branch sections printed in a parent train's column take the parent's number (e.g. on_cn_t126m / d / p / c / g). Through cars or separate connecting trains? No number, or "connection to No. 41"? (26 Oct) Brendan: much may settle as the branch tables come in.
- [ ] CN Table 116 (Longlac - Fort William, Nos. 79 / 80): the Toronto section may be a connection with Nos. 3 / 4 at Longlac rather than through cars (Brendan not certain). Matters for chaining. (23 Oct)

## Waiting for Brendan
- [ ] Chicago interurbans (Brendan, 25 Nov 2026: "I'm gonna do it"): the Chicago North Shore & Milwaukee and the Chicago Aurora & Elgin. Track: Mississippi Rails
  (Chicago_Interurbans_1948.kml, private repo traces/chicago/): CNS&M 263 mi of pieces (with some Milwaukee Road), CA&E 101 mi (main line, Aurora, Batavia, Elgin, Geneva,
  Hillside and Mount Carmel spurs), and the Chicago 'L' by its pre-1947 companies. Stations are unnamed polygons on the interurbans (centroid onto the track; names from the
  timetables' station lists and miles); some 'L' polygons are named in their descriptions. The 'L' itself is NOT modelled for now (Brendan), but both interurbans run over 'L'
  track into the Loop (CNS&M by the North Side 'L' to Roosevelt Road; CA&E by the Garfield Park 'L' to Wells Street): draw those stretches as 'L' (CTA) track.
  Timetables: CNS&M Timetable G-54, June 5, 1949 (reprint May 1950; private repo scans/cnsm/), source to cite: Illinois Railway Museum CTA collection,
  http://irm-cta.org/NSL/TT/NSL%20Timetable%201949-06-05%20(2).pdf (Brendan, 25 Nov 2026). Use: running times between stations, station list and order, Electroliner numbers,
  and estimating 1948 summer trains missing from the 1948 Official Guide. Waiting for: the 1948 Official Guide page (Brendan sending); the CA&E timetable.
  Colours (Brendan, 25 Nov 2026): CTA ('L') track a dark blue, not navy (keep clear of the B&O #1D3461; Claude's shade, e.g. #2a5c8a); North Shore Line the Electroliner
  turquoise and salmon (two-colour livery like the S.I.); CA&E the late-period bright red and grey (so it does not blend with the CTA). The Electroliner trains carry the
  name "Electroliner" (train name on the trips that are Electroliners).
  Rapid transit (Brendan, 25 Nov 2026): the CTA track is its own rapid-transit class (an owner set beside INTER_OWN; GTFS route_type 1 if 'L' trains are ever scheduled),
  drawn mostly like interurban track. No on/off control (no control bloat). If 'L' trains come later: repeating patterns (like Central Park), summarised in the list and
  boards, stations thinned when zoomed out.

- [ ] Great Northern main line and the Burlington (Brendan, 26 Nov 2026): track received, NOT BUILT, waiting for the Official Guide pages (GN Seattle - St. Paul and branches;
  CB&Q Chicago - Twin Cities). Track (private repo traces/msrails/): Great_Northern.kmz (Mississippi Rails 2024-6-16: the whole GN system, Vancouver - St. Paul / Duluth, Washington
  branches, VV&E Curlew - Midway, the Oregon Trunk to Bieber; Brendan's own Vancouver - Seattle trace stays) and Chicago_CBQ_Line.kmz (Chicago - Aurora - Rochelle - Oregon - St. Paul,
  Aurora - Mendota). Empire Builder / Oriental Limited run through St. Paul - Chicago over the CB&Q. CB&Q colour: a silver (Brendan, 26 Nov 2026: "a sort of silver", the Zephyrs);
  Claude's shade #8d99a5 (dark theme #c3ccd4), kept clear of the union-station grey and the CA&E grey band. Chicago Union Station (Brendan, 26 Nov 2026): 41 52 43.92 N,
  87 38 20.10 W (41.878867, -87.638917); a union station (own 'union'), also for the Milwaukee Road, Pennsylvania and Alton trains when they come.
  Transcribed 27 Nov 2026 (timetables_gn/, Official Guide pp. 1067 - 1070): Table 1 (St. Paul - Willmar - Fargo - Grand Forks - Minot), Table 2 (St. Paul - St. Cloud - Fargo -
  New Rockford - Minot), Table 3 (Minot - Williston - Havre), Table 4 (Havre - Whitefish - Troy - Sand Point, with Table 5's Idaho rows), Table 7 (Nos. 29 / 30 and the Crookston -
  Noyes locals 131 / 132). Spokane - Seattle / Portland already in wa_gn_t005a / t005c. Still wanted: the CB&Q Chicago - St. Paul table; branch tables met on the way (12 Casselton /
  Devils Lake, 24 St. John, 25 Hannah, 28 Sarles, 47 Whitefish - Kalispell) if the branch trains are to run. Questions in the files' heads: No. 9 / 10 daily (Table 1) vs daily
  except Sunday west of Minot (Table 3); No. 209's 8.30 a.m. at Nolan; No. 12's blotted day sign at Fargo.
  Burlington section (Brendan, 27 Nov 2026): Chicago (Union Station) - St. Paul runs through WITHOUT STOPS for Nos. 1 - 4 until the CB&Q tables come (timetables_gn/gn_t001c_cbq.csv),
  as with the CV trains over the PRR. Branch tables to follow from Brendan: build after them.
  Page 1071 (27 Nov 2026): Table 8 Billings - Great Falls - Shelby (43 / 42; 239 / 240 Moccasin - Great Falls; 373 / 374 Great Falls - Power) and the Duluth - Grand Forks table
  (35 / 36; 105 / 106 Cass Lake - Bemidji; its table number not on the image). Burlington connections at Billings are not through trains (Brendan). Name: "The New Empire Builder"
  everywhere (Brendan, 27 Nov 2026): change wa_build.py's names for Nos. 1 / 2 at the GN build.
  Superior Union Station (Brendan, 27 Nov 2026): 46.726609, -92.107400 (GN, shared with the NP; the DSS&A used the Soo station in 1948 per its table). Duluth: GN trains at the
  Union Depot. All GN pages transcribed (1067 - 1077, Table 53 the last; timetables_gn/, 27 Nov 2026): BUILT in Version 233.

- [ ] on_lines.SHARED: the ('oncn' / 'oncp', 'toronto union') -> TORONTO_UNION entries were lost into a comment in V217; joined at assembly since V234 (merge_stations). Restore them
  in SHARED the next time on_build is re-run anyway.

- [ ] Washington, Idaho & Montana Ry. (Brendan, 27 Nov 2026): Palouse - Potlatch - Bovill, transcribed whole (timetables_wim/wim_t001.csv, table of March 1948; replaces the
  Palouse-only wa_wim_t001.csv of October). NOT BUILT: track wanted beyond the Washington State KMZ's 3.7 mi Palouse - Idaho line piece.

## Fixes queued (Brendan: "don't fix yet"; ask before the next rebuild whether to include them)
- [ ] SCALING WORK, scheduled (Brendan, 26 Nov 2026: do 1 and 2 on the first build after Thursday 26 Nov, 9 p.m. his time, when his weekly usage resets), planning for
  timetables all the way to Panama (perhaps 4 - 6 times today's data):
  1. DONE (V229 list skip; V230 parts/on_build/ folder of groups, site data by group). Was: split parts/on_build.json (35 MB, 60 commits, repository history
     750 MB; site chunk 5.6 MB re-downloaded on any change) by railway or region; new U.S. railways go in steps of their own meanwhile.
  2. Region loading ("stage 2" in STATE.md): the page loads a region's lines when it is viewed, so start-up (12 s and about 200 MB of memory now) depends on the view, not the
     continent; with it, the list and station boards scoped to the view (also in the 16 Nov ideas).
- [ ] Alcoa Steamship Co. (Brendan, 23 Nov 2026, Official Guide page): fortnightly sailings from Montreal and Halifax to Hamilton (Bermuda), St. Kitts, Antigua, St. Lucia,
  Barbados, St. Vincent, Grenada, Port of Spain, Georgetown; also calls Dominica, Montserrat, Martinique and Guadeloupe as cargo offers. No dates: like the other ocean sailings
  (draw to the edge of the water file), a dated July 1948 sailing is needed (Montreal Gazette / Halifax shipping columns, with the Lady boats).
- [ ] Seattle - Portland pool: the GN / NP / UP split of the trains is from the August 1952 Official Guide (V209); confirm for 1948 (Official Guide car-service lists).

## CP Maritimes (started 10 Nov 2026)
- [ ] DAR readings (V154): No. 33 (Windsor - Kentville, from No. 4) and No. 4 (Truro - Windsor) have no sign: entered daily except Sunday. No. 3 (34-3) entered Saturday only like No. 34. Boat days at Evangeline Wharf: No. 98 Tue., Thu., Sat. (the Boston boat in); No. 95 Tue., Thu. (the boat out; no No. 95 on Sundays); No. 99 leaving Halifax Mon., Wed., Fri. (Brendan: to the wharf on boat days only). Wharf times estimated.
- [ ] Not built yet from the DAR page: the Kentville - Kingsport bus. (V154) The Digby - Saint John steamer is in (V155).
- [ ] CP N.B. stations (V159): Saint John (Union Station), Westfield Beach and Norton entered as the CN stations (Norton: Claude's reading, TO CHECK). Kept apart from CN's: Woodstock, Chipman, Grand Falls, St. Leonard: joint or separate in 1948?
- [ ] CP N.B. readings (V159): Table 10: 39 from Saint John ex Sun, from Megantic daily (Monday train from Megantic entered as No39m); 42 east of Brownville Jct. ex Sun, No. 104 on Sundays; 41 ex Sun from Saint John, No. 103 on Sundays. M117 / M118 (Brownville Jct. - Greenville - Megantic) mixed: Greenville and Holeb arrivals estimated. The Gull 113 / 114 daily (June 20 - Sept. 5). Table 12A 105 waits at Fredericton Jct. 6.30 - 8.55 p.m. as printed. Table 15 Theriault, Sigas, L'Eglise printed "f" without times: left out.

## Questions: readings to check
- [ ] CA&E Sunday "frequent service" (Brendan, 26 Nov 2026: unsure how to proceed; for a future date). The Guide's note: first train from Chicago 7.00 a.m., last 2.35 a.m.;
  from Wheaton first 6.54 a.m., last 1.13 a.m. Claude's reading: a summary of the daily trains already in the table (the end times match the daily 2.35 a.m., the 1.13 a.m. from
  Wheaton and the additional Sunday 7.00 a.m.), not extra trains; the one misfit is the daily 5.30 a.m. from Wheaton (the note implies it does not run on Sundays). Built
  meanwhile: the daily trains as printed, the 5.30 a.m. daily; nothing extra for the frequent service.
- [ ] CN Montreal District employee timetable (20 June 1948), left open: No. 132 (St. Hyacinthe 11.58 p.m. ex Sat to the Drummondville
  subdivision: where to?); day differences 30 (daily), 280 (daily), 621 / 622 (daily), 100 (Sunday only) against the April Official Guide;
  Laurel (Official Guide) vs Lake Chapleau (employee timetable, 59.7 mi from Val Royal): the same station?; Dore Bay (flag for 155, 156, 193, 194,
  no mileage) and National Jct.; Montreal Nord, Ahuntsic and the stations between placed by mileage (points wanted).
### Maritimes: CN Official Guide pages 1113 - 1117
- [ ] No. 20, Folly Lake f3.35 - Londonderry 3.41 a.m. (7.6 mi in 6 min). Was it f3.25? Built as printed. (V144)
- [ ] The second No. 13 column, Sunday only, Moncton 4.30 p.m. Is this a real Sunday train? Entered as 13s. (V144)
- [ ] The "b" sign on 379 / 380. Read as daily except Sat and Sun, the complement of 383 / 384 (Sat only). (V144)
- [ ] 382: dagger or "k"? (V145)
- [ ] No. 26 at Campbellton has a dagger (ex Sun). The file keeps it daily. (V143)
- [ ] 253 / 260: the "-14" columns at Salisbury 1.35. What do they mean? (V145)
- [ ] No. 67 (Edmundston 4.00 p.m. - Quebec): the sign at Edmundston. Page 1116's legend makes the double dagger "daily except Saturday"; built Mon - Fri, as first read from the Quebec page. (V146)
- [ ] Table 24: the third westbound column is printed 305, the same as an eastbound one. Was it 306? Entered as 305. (V146)
- [ ] Table 25 M215 / M216: the sign read as the natural sign (Sun., Tue., Thu.). (V146)
- [ ] Table 31a: the second M62 has a double dagger. Read as the spring service and left out; the Tuesday M62 (first trip May 25) is in. (V146)
- [ ] Table 32 M57: printed a (Mon., Wed., Fri.) under a double-dagger heading; entered Mon., Wed., Fri. (V148)
- [ ] Table 37 M257: New Germany 4.15, then Caledonia Junction (1.1 mi) 4.46. Is that a wait at New Germany? Entered as printed. (V148)
- [ ] Ferrona Junction: Table 30 puts it 3.7 mi from Stellarton, Table 45 1.6 mi. Sunny Brae traces 16.4 mi from Stellarton against 14.1 printed (forced onto the track). (V148)
- [ ] Témiscouata No. 4: Baker Brook 8.15 - Edmundston 9.15 a.m., as read. (V143)

### Ontario and Quebec (carried from STATE.md)
- [ ] CN 122 / 126: hand points CN Allandale and CN Camp Borden (Camp Borden mile 78.0 estimated; Brendan to trace).
- [ ] L&PS: Colborne St., Philip St., Elm St. by estimated mileage; Stop 7 printed 9.0, read 7.8; No. 37 St. Thomas smudged, read 1.46.
- [ ] CP Table 73: No. 50 Elma printed 8.09 (impossible), estimated 8.26; Crest by mileage. CP Table 69: Bennington, Lind by mileage. CP Table 107: McAuley - Welwyn.
- [ ] CP Table 50 (on_cp_t049w): No. 20 The Canadian probably read one row off (London 5.35, Guelph Jct. 7.19 per Table 68): recheck against the scan.
- [ ] CN Port Dover routing (on_cn_t121d, Simcoe (South) - Port Dover: 8.1 mi traced, 7.5 printed).
- [ ] CN Table 72 Iberville: keep "lve. Iberville (C.P.Ry.) 25.3" only as the timing point after the reversal, or drop the row (Brendan doubts the trains ran into the CP station).
- [ ] NYC Tables 6 / 11: 364 St. Thomas 11.28 - Aylmer 11.33 (10.7 mi in 5 min); 366 Lythmore f4.23 - Cayuga 4.25; M362 Charing Cross 6.58 - Fargo 7.25. Table 44 Petrolia / Oil Springs miles (estimated); Otterville.
- [ ] GRR: the reconstructed hourly pattern and running times; Joseph Street as the Hespeler trains' Preston stop.
- [ ] Parkhead station point (APPROXIMATE, at the Wiarton line junction; Tables 138 and 143); St. George end of the stub.
- [ ] CN L'Epiphanie kept separate from CP L'Epiphanie: shared station?
- [ ] H&LB: should the two Portages be minor landings too?

## Mileage to review: traced vs printed (Brendan, 10 Nov 2026: flag big gaps for review)
Maritime tables where the traced line differs from the printed miles by 1 mi and 2 % or more, with the stretches that carry the gap. Build behaviour meanwhile: trains run on the traced line; stations off the track are placed by printed mileage. (V155)
- [x] CN Table 9, Halifax - Yarmouth: was +9.7 mi; the Lockeport Branch pruned (Lockeport the junction station; Brendan, 10 Nov 2026): now 252.0 traced to the wharf, 250.7 printed. Italy Cross - Liverpool 21.2 / 19.7 remains. (V158)
- [ ] CN Table 5, Halifax - Sydney: +3.2 (V155), +2.0 with Brendan's Sydney station point (V165). North Sydney - Sydney 17.0 / 15.1 (the run into the North Sydney ferry spur and out again); Bayfield Road - Tracadie - Monastery offset each other (the Tracadie point).
- [ ] CN Table 45, Stellarton - Sunny Brae: 16.4 / 14.1 (forced onto the track; see Ferrona Junction above).
- [ ] CN Table 37, Bridgewater - Bridgetown: 67.4 / 69.4; Middleton - Bridgetown 13.3 / 14.4.
- [ ] CN Table 41, Bathurst - Tracadie: 89.1 / 91.1; Bathurst - East Bathurst and East Bathurst - Stonehaven offset (the East Bathurst point); Pokemouche Junction - Shippigan 5.8 / 6.9.
- [ ] CN Table 27, Charlottetown - Murray Harbor: 54.4 / 55.7.
- [ ] CN Table 11, Halifax - Dartmouth: Burnside - Dartmouth 3.8 / 2.5 (the Dartmouth point, or fid 40 above).
- [ ] DAR Windsor - Truro: 57.7 / 59.0.
- [ ] CP Woodstock: Peel - Woodstock 18.7 traced / 17.2 printed, Woodstock - Debec Jct. 11.8 / 10.7, Carr - Woodstock 15.9 / 14.1: the Woodstock station point (names-file point moved onto the track) wanted. (V162)
- [ ] CP McAdam - Vanceboro 6.9 traced / 5.9 printed; Megantic - Boundary stretches +-0.7 (station points by mileage). (V159)
- [ ] Smaller ones (about 1 mi in a stretch): Moncton - Pacific Jct. 11.3 / 12.2 (the Moncton point, above); Boiestown - Doaktown 17.2 / 16.0; Borden - Cape Tormentine ferry 8.4 / 9.5 (the straight course); New Richmond - Caplan 9.7 / 10.8; Saint John - Centreville 171.3 / 172.6 overall.

## Questions: points and track
### Maritimes: points and track
- [ ] Approximate station points to confirm or replace: Halifax, Newcastle, Bathurst, Oxford, the Mulgrave / Point Tupper ferry slips. (V145)
- [ ] Edmundston station point (the Témiscouata's): you marked it "I think". (V143) CN's own station: done (V147).
- [ ] Page 1116 approximate points: Charlottetown and Summerside (the town points moved onto the track). (V146) CN Table 34 Fredericton (Intercolonial station, V161) - South Devon: 0.7 mi traced, 1.7 printed.
- [ ] Is Dartmouth fid 40 the Narrows bridge line? For now, the part past fid 41 is pre-1948. (V145)
- [ ] Track bank pieces still marked "check": Wikipedia fids 8, 14, 17, 23. (V143) Now in use: fid 26 Harmony Jct. - Elmira (9.9 mi, as Table 31a prints) and fid 20, the Cape Traverse branch from Emerald Jct. through Kinkora and Albany to the Borden branch. Was the stub on to Cape Traverse still there? (V146)
- [ ] Moncton: the traced miles are Painsec Jct. 7.6 (6.9 printed) and Pacific Jct. 11.3 (12.2), which would put the station about 0.7 mi east. Kept your point as given. (V144)

## Material wanted from Brendan
### Traces
- [ ] Springfield, Mass.: the wye track at the Connecticut River line / B&A junction is missing from the Mississippi Rails trace; needed before the New Haven trains (north - south through trains reverse at Union Station). (V189, Brendan 18 Nov 2026)
- [ ] Newfoundland Railway: trace end to Port-aux-Basques. (V145)
- [ ] Stellarton - Westville (Table 29): the Pictou trains run over the former Acadia Coal Co. and Nova Scotia Coal Co. lines (CN since V149). If CN's 1948 route went another way, a trace is wanted. (V146)
- [ ] Borden - Cape Tormentine car ferry: the course across the strait is a straight estimate between the pier ends. (V146)
- [ ] Pokemouche Junction: the Wikipedia Gulf Shore trace stops 0.2 km short of the Caraquet Railway; a short tie added (solid). (V148)
- [ ] Detroit River Tunnel portal and border point (APPROXIMATE).
- [ ] Camp Borden (CN 122 / 126).

### Timetables and points
- [ ] Source to follow up (Brendan, 23 Nov 2026): the Montreal & Southern Counties public timetables on Rolly Martin Country (D. J. Gagnon, Feb. 2022; the address says
  "nyc-m", but Brendan: it is the M&SC file): https://rollymartincountry.blogspot.com/2022/02/nyc-m-public-timetables-1924-1951.html. For the Suburban Division (only a
  frequency line in the Official Guide: 20 min Montreal - St. Lambert - Montreal South; 20 / 40 min Greenfield Park and Mackayville). The timetables are images: the scans are
  needed in a session to read them (the web fetch gets the text only). It includes an April 1951 timetable: a possible stand-in for 1948 (as the August 1950 Guide
  was for Arnold Transit), if the Suburban Division is in it.
- [ ] Quebec Railway, Light & Power; the Stratford table (No. 10); the remaining steamship points and waterways; the rest of the Official Guide pages.
- [ ] The Valleyfield timetables (then recheck CN Table 75's Valleyfield sections, on_cn_t075v). (23 Oct)
- [ ] CN Peebles - Handsworth (sk_cn_t162, Saskatchewan): the intermediate stops (the table prints only the ends). (4 Nov)
- [ ] Brendan's list of "janky" junction uses in the Ontario / Quebec routings (known: at Montreal West the Windsor trains for Park Avenue run a few hundred metres south onto the wrong leg). (23 Oct)

## Housekeeping
- [ ] Licence of the Wikipedia Canadian Government Railways map data (for the credits). (V143)
- [ ] The raw GeoPackage, the CGN zips and the OSM exports belong in the private repo. Claude can push there (checked 18 Nov 2026: the earlier "read-only" note was wrong); they need sending to a session so they can be committed. (V143)
- [ ] ESL livery colour: the placeholder is #7a2430. (V145)

## Work for Claude
- [ ] Build-out order (Brendan, 8 Nov 2026): 1 CN Maritimes (done, V148), 2 CP Maritimes, 3 short lines with 1948 passenger service, 4 U.S. connections (whole U.S. railways in time).
- [ ] Before the U.S. build-out: split parts/on_build.json (25 MB: Ontario, Quebec and the Maritimes in one file) by region or railway, so it stays under GitHub's 50 MB warning (100 MB refuses a push) and each version commits only the changed region; then have the page load a region's data when it is viewed. CP Maritimes is small enough to go first (Brendan, 10 Nov 2026).
- [ ] CP Table 8 south of the border (Newport - Wells River - Boston / New York); Table 25 (Montreal - Maine coast; Table 26, the Barre & Chelsea, done in Version 189); the Bangor & Aroostook and Maine Central / B&M connections at Brownville Jct., Mattawamkeag and Vanceboro (The Gull and The Pine Tree beyond Vanceboro); the Quebec - Levis ferry (QC Nos. 2 / 5); the Beebe Jct. - Rock Island bus. (25 Oct; U.S. stage) CP Table 10 east of Boundary and the N.B. tables: built (V159).
- [ ] The Prescott - Ogdensburg car ferry (Canadian Pacific Car & Passenger Transfer Co.). (3 Nov)
- [ ] Check the Montreal suburban trains against the CN Montreal employee timetable of June 20, 1948 (https://www.traingeek.ca/files/19480620-ett-montreal-16.pdf). (7 Nov)
- [ ] "Expansion joints": trains pausing mid-run where nothing is printed, at joins between track pieces; find and make them run through. (25 Oct)
- [ ] Pembroke Junction: CN Nos. 1 / 2 (not calling at Pembroke) should run straight through on the through tracks (on_cn_t075b). (23 Oct)
- [ ] Ottawa Union Station: CN trains back out; CP trains may run through or back out by their table. Check the CN routes in and out. (24 Oct)
- [ ] CP Table 51 (Glen Tay - Havelock - Peterboro - Toronto), Table 56 (Toronto - Hamilton), Detroit - Chicago (U.S.): check what is still unbuilt. (25 Oct)
- Interurban train icon: moved to IDEAS.md (27 Nov 2026).

## Remaining 1948 services (list of 11 Nov 2026)
- [ ] Soo Line, built in Version 194 (19 Nov 2026). Open items below. 29 tables transcribed from the Official Guide (May 1948, pages 1047 - 1052; scans in the private repo,
  scans/og1948_soo/): on_soo_t001 ... t026a.csv, built by on_build as CP lines labelled Soo Line (tidpfx SOO; SOO_PLACES; Central time). Track: traces/maritimes/soo.geojson
  (tools/mar_import_soo.py from the Mississippi Rails KMZ). All on track. Menasha: Table 16 runs Hilbert Jct. - Menasha - Neenah over the Milwaukee Road by trackage rights (Brendan, 19 Nov
  2026; MILW pieces own milw, Menasha at Brendan's point, probably the MILW station, shared). Ridgeland and Rice Lake branches: Brendan's traces (19.0 / 18.7 and 7.2 / 6.7 mi traced / printed). Superior - Duluth: Brendan's Soo connection, NP Grassy Point bridge and Duluth final-approach
  traces; Superior and Duluth stations at his points (19 Nov 2026). Sault Ste. Marie: the Soo trains use the CP station on the Ontario side (Brendan, 19 Nov 2026;
  CP_SAULT_STE_MARIE), over the International Bridge on the CP Sault branch of the Ontario collection, a 0.6 km dashed gap from the Michigan trace end (V196). St. Paul: the Soo joins the Northern Pacific 'Line A' at 44 57 38.70 N, 93 05 09.44 W
  (Brendan, 19 Nov 2026; trackage rights) and runs over it to Minneapolis and the Milwaukee Road station; Union Depot at Brendan's point 44 56 48.89 N, 93 05 07.30 W (also for the
  Winnipeger, the Mountaineer and the GN in sk_lines.py: the next build re-runs the Saskatchewan steps). No. 1 to the Great Northern station by the Soo Connector (the GN row's 0.5 mi
  is Claude's).
  To check: Table 7 Nos. 8 / 7 daily (Table 9: ex Sat / ex Mon); Table 7 No. 7 Bruce printed 7.35 (left out); Table 6 St. Croix Falls section (left out); Table 13 No. 160
  sign (# MWF or double dagger); Table 23 La Mars state; Chicago: Grand Central Station (B&O property) - Forest Park on Brendan's B&O Chicago Terminal trace (19 Nov 2026), own bo,
  B&O dark blue (#1D3461; dark theme #8AA6DC; Claude's pick of shade), 10.0 mi traced / 10.9 printed; Table 10 Nos. 3 / 4 and Table 26 Nos. 109 / 110 are the existing Mountaineer / Winnipeger (connections only).
- [ ] Arnold Transit (V200; boats unnamed since V201): August 1950 Official Guide times stand in for July 1948 (the May 1948 Guide's St. Ignace list looks off-season); crossing times
  35 / 40 minutes from the 1958 brochure. Mackinaw City State Ferry Dock point is Brendan's estimate. Les Cheneaux: the lane goes round the outside of the islands
  (Hessel channels closed at basemap resolution; a hand lane wanted?); Coryell Island (the 1948 terminus) not drawn.
- [ ] Delaware & Hudson (V205, Official Guide April 25, 1948). To check: (Troy Union Station on track since V206: Troy Union RR and Brendan's bridge;
  the bridge drawn as D&H: owner to confirm); No. 35 (The Laurentian, from June 6) D&H times estimated from No. 37's April times; Nos. 8 / 10 drawn together Troy - New York; station points placed at trace
  junctions (Fort Edward, Glens Falls, Plattsburg, Whitehall, Ticonderoga, Oneonta, Central Bridge, Sidney, Harpursville, Binghamton, Scranton, Carbondale) to confirm; Albany at
  Union Station (D&H trains used it; N.Y.C. trace); Scranton - Carbondale 17.1 mi traced, 16.0 printed. Rouses Point, N.Y.: the D&H station (also wanted for CN / Rutland 51, 52, 64, 65).
- [ ] Rutland Railroad (V207). Waiting: Brendan's B&M trace Boston - Fitchburg - Keene - Bellows Falls, then build Table 3 (on_rut_t003.csv, skipped in on_build until then).
  To check: No. 146's two Boston columns (Bellows Falls 4.20 / Boston 7.45 a.m. and 5.55 / 9.15 a.m.) have no day signs (the first entered daily); No. 88 and No. 8 both leave Rouses
  Point 12.40 p.m. (one train?); Burlington station: dashed 0.76 km between the two trace pieces (station track wanted); Larrabees Point: the end of the Addison branch placed at the
  lake shore (Claude); White Creek - North Bennington 2.9 mi traced, 1.9 printed; Rutland colours #234D20 / yellow #F2C230 are Claude's shades.
- [ ] White River Jct. - Boston, B&M 302 / 325 (the Red Wing's and the New Englander's Boston cars in one train): drawn as the CP's Red Wing for now; who owns the leg to be settled with the B&M timetables (Brendan, 17 Nov 2026).
- [ ] Boston & Maine's own trains (waiting for the B&M timetables): the Connecticut River trains of CV Table 5 (702, 72, 712, 78 / 79 the Red Wing's Springfield coach, 7060, 728, 703, 73, 7055, 717, 7059) and White River Jct. - Boston 320 / 313; the stations between White River Jct. / Plymouth and Concord.
- [ ] Central Vermont Table 1: St. Johns - St. Alexander (7.6 mi) is a straight estimate, drawn broken: the Quebec collection lacks that piece of the Montreal & Vermont Junction line (a trace wanted). East Northfield's point is approximate (at the Massachusetts line).
- [ ] Times to check against the scans (tools/check_speeds.py, V176): CP M253 Wickham 7.18 p.m. - Tourvilles f7.22 (5.9 mi; on_cp_t019.csv);
  MC 364 St. Thomas lv 11.28 p.m. - Aylmer f11.33 (10.7 mi; on_mc_t006.csv); CN 32 Luceville 3.20 p.m. - Mont Joli ar 3.25 (8.2 mi; on_cn_t001.csv).
- [ ] Saskatchewan's clock in the view menu: set to Mountain (CP changed at Broadview in 1948, Claude's reading); Brendan to confirm, also Lakehead (Central).
- Ideas from the 16 Nov 2026 review: moved to IDEAS.md (27 Nov 2026).
- [ ] TH&B pool trains (built V193, onthb056p; on to Buffalo Central Terminal since V217): look up the NYC numbers (Official Guide NYC Buffalo - Toronto table) and add them to the notes. (Old note:) The trains end at the
  international boundary; joining them to NYC trains into Buffalo waits for the NYC tables.
- [ ] NYC Montreal - Malone: Brendan says the Delamere file has the NYC stations as far as Athelstan (Glen Elm); only Athelstan uses its Delamere point. The others are placed by
  the collection or by printed mileage; check them against the Delamere placemarks if he wants (some are unnamed there).
- [ ] CN Cartierville branch (Montreal): not in the Delamere Quebec file, so not in the model (Brendan, 16 Nov 2026). A 1950 Central Station departure
  list (Brendan's notes) has ten Cartierville short trains each way and St. Eustache trains "via Cartierville"; the April 1948 Official Guide does not show
  them, and the June 1948 Montreal District employee timetable proves nothing: it begins the tunnel lines at Val Royal and Gohier (Central - Mount
  Royal - Val Royal was presumably in a Montreal Terminals timetable), so trains running only Central - Cartierville would not appear in it. Need: a trace of the branch (e.g. OSM abandoned railway) and a 1948
  source for any service (employee timetable page for that subdivision, or a 1948 suburban folder). Also check No. 365 (17:00): the 1950 list
  marks it "via Cartierville". The 1950 list otherwise matches the model's weekday trains at Central (inbound times are at Mount Royal, ~10 min earlier).
- [x] (Version 180; remaining: Laurentia, Beaverford, Lady Nelson / Lady Rodney need dates, e.g. the Montreal Gazette and Halifax shipping columns, July 1 - 12, 1948) Ocean liners, week of 5 July 1948 (Brendan, 15 Nov 2026): transatlantic and transpacific passenger ships, incl. passenger-carrying freighters
  - Lady boats (Brendan, 17 Nov 2026): an undated C.N. advertisement (https://bajanthings.com/wp-content/uploads/2020/03/lady-liner-voyages_advertisment.jpg.webp)
    has a summer Western Service Montreal - Bermuda - Nassau - Kingston - Belize and an Eastern Service Halifax - Boston - Bermuda - St. Kitts - Nevis - Antigua -
    Montserrat - Dominica - St. Lucia - Barbados - St. Vincent - Grenada - Trinidad - Georgetown; Boston "2 days" from Halifax. Probably pre-war (five Lady
    boats); Foreign Trade, 26 June 1948, has both Lady Nelson and Lady Rodney loading at Halifax for the Eastern Caribbean. Still needs a dated 1948 sailing.
  (CP Beaverburn / Beaverford, 12 passengers), drawn from their Canadian port to the EDGE OF THE WATER FILE and then gone (Brendan: "sail to the edge
  of the water file and then disappear"); arrivals in Canada in the week estimated the same way, appearing at the edge. Apply the same to the ships
  already on the map that leave the water: the Denali (Kodiak) and the Fort Amherst's Bermuda trip (both now drawn beyond the water layer).
  Known: Empress of Canada leaves Montreal 11 a.m. EST Sat July 3 (Liverpool July 10), so in the Gulf / Belle Isle on Mon 5; Beaverford loads at
  Montreal July 11 - 18 (arrives about the 10th?). Brendan is checking the Pier 21 arrivals database for the others (Aquitania, Samaria, Scythia,
  Ascania, Laurentia, Beaverbrae, Kota Inten, Tabinta, Volendam, Sobieski, Newfoundland, Nova Scotia, Lady Nelson, Lady Rodney). No transpacific
  liner at Vancouver that week (Aorangi resumed later in 1948: Brendan). Notes: marine/FOREIGN_TRADE_1948.md.
- [x] (Version 180) Island Connector (Clarke): Charlottetown July 8 - St. John's July 11, sailing July 11 for Montreal: with the ocean liners.
- [x] (Version 180) Furness Warren R.M.S. Newfoundland (Liverpool - St. John's - Halifax - Boston): due St. John's July 12 from Boston and Halifax, sailing same day for Liverpool (Daily News July 7). In the week she is coming north from Boston via Halifax: draw once a Halifax or Boston date turns up.
- Rule (Brendan, 15 Nov 2026): ships go by SCHEDULED times where there is one. Only the Newfoundland Railway boats are the exception: no schedule, so drawn from the ACTUAL reported positions in the Daily News (nfld/steamship_movements.md), interpolated between reports; mark them as shown from reports, not a timetable.
- [x] Newfoundland coastal steamers (Version 172) (Brendan researching; from Newfoundland Railway notices, The Daily News, 2 - 7 July 1948; nfld/steamship_movements.md): S.S. Bar Haven,
  Bay Route of Placentia Bay (from Argentia, Monday, after the 9 a.m. train); S.S. Northern Ranger, Corner Brook service to St. John's (from
  Corner Brook, Monday, after the 5 p.m. local express); S.S. Springdale, Green Bay service (from Lewisporte, after the Saturday local express);
  S.S. Kyle, Labrador service to Hopedale (St. John's, Dry Dock Wharf, Saturday 4 p.m.); M.V. Codroy, Corner Brook - Battle Harbour (freight).
  Not services: S.S. Tudor Prince (freighter, New York - St. John's - Corner Brook).
- [x] Newfoundland Railway summer schedule (done in Version 179). Reference: CN Newfoundland folder N No. 1, May 8, 1949 (Brendan, 13 Nov 2026; https://rollymartincountry.blogspot.com/2022/02/cnr-1949-newfoundland-public-timetable.html):
  its pattern matches the 1948 notices (15 Mon / Wed / Sat 5 p.m., 1 Tue / Thu 5 p.m., 3 Overland Limited Sun 10 a.m., M5 Argentia Mon / Wed / Fri 9 a.m.);
  summer Newfoundland time = Atlantic + 1.5 h. Not in 1949: the Wednesday 9 p.m. train for Bonavista (sleeper Trinity) of 7 July 1948. The folder also lists
  the coastal steamer routes (ports and mileages, no times). July 1948 notices: Sat 5 p.m. local express St. John's - Port aux Basques; Sun 10 a.m.
  Fast Overland Limited (direct foreign connection); Mon 5 p.m. local express to Corner Brook; Tue 5 p.m. foreign express. The model has the
  January 1948 timetable (1 Mon / Thu, 15 Wed / Sat, 2 / 16 Thu / Sun). Needs a summer timetable (running times, eastbound days, branches) and
  the Cabot Strait steamer re-dated to meet the summer trains.
- [ ] Rail: North Yonge Railways (TTC, Toronto - Richmond Hill; Brendan) (Wabash and Pere Marquette: no passenger service in Canada in 1948; Brendan). Streetcars out of scope so far.
- [ ] Investigate (Brendan, 16 Nov 2026), Quebec marine services in 1948:
  - Tadoussac - Baie-Sainte-Catherine ferry across the Saguenay mouth: N.M. Jacques-Cartier (1938 - 1958; 12 vehicles, 88 passengers). Need a 1948
    schedule or frequency (sources Brendan found: Societe des traversiers du Quebec post; https://www.tidesoftadoussac.com/ferries).
  - Clarke Steamship Company, North Shore coastal service (BUILT V218 as a simulated schedule; open: a real 1948 sailing list, the North Coaster / North Voyageur /
    North Pioneer, the North Shore's 1948 sailing day (Tuesday used; May 12, 1948 was a Wednesday), port points): Quebec, Montreal and South Shore ports to Baie-Comeau, Sept-Iles, Havre-Saint-Pierre,
    Blanc-Sablon (Route 138 not yet through); 1948 fleet incl. North Shore (II) (ex-corvette, 1946) and North Pioneer (1946). Sources:
    https://www.benjidog.co.uk/TheShipsList/ClarkeSSCo.php; https://semaphore.uqar.ca/id/eprint/2457/1/Les%20Clarke%20et%20la%20compagnie%20de%20transport%20du%20Bas%20St-Laurent%20%281921-1970%29.pdf;
    https://clarkesteamship.wordpress.com/tag/north-shore-power-railway-navigation-co/; https://www.boisestgilles.ca/content/historique-maritime.
    Need a 1948 sailing list (Clarke folder or newspaper). Also the Compagnie de transport du Bas-St-Laurent (Rimouski - North Shore) in the same thesis.
    FOUND (23 Nov 2026, from the full chapters of "St Lawrence Saga", clarkesteamship.wordpress.com, PDFs of chapters 9 - 11; Brendan pointed to the 1945 cruise advertisement):
    - 1948 season (notices May 1948): North Gaspé opened Tue May 11 from Victoria Pier, 7.30 p.m., alternating 5 1/2-day Gaspé cruises (every second Tuesday) and 7-day Magdalen
      Islands cruises (the following Monday); ports Quebec, Cap Chat, Ste-Anne-des-Monts, Mont-Louis, Rivière-Madeleine, Grande-Vallée, Cloridorme, Rivière-au-Renard, Gaspé
      (Magdalens: Havre-Aubert, Cap-aux-Meules). The 1945 advertisement gives the day-by-day pattern (Montreal Tue 7.30 p.m., Quebec Wed, Ste-Anne Thu, Gaspé Fri, back Ste-Anne Sat,
      Quebec Sun, Montreal Mon morning; Magdalens: Montreal Mon 7.30 p.m., Quebec Tue, Ste-Anne Wed, Gaspé Thu, Grindstone Fri, Gaspé and Ste-Anne Sat, Quebec Sun p.m., Montreal Mon p.m.).
      Counting the alternation from May 11 (estimate): Magdalens Mon June 28 - Mon July 5; Gaspé Tue July 6 - Mon July 12.
    - North Shore (express, 95 berths): weekly, 6- and 7-night voyages to Havre-St-Pierre and Natashquan; 1948 first sailing May 12 (a Wednesday; 1946 - 47 sailed Tuesdays
      7.30 p.m.; back at Quebec on Mondays). Ports (1946): Quebec, Baie-Comeau, Franquelin, Godbout, Baie-Trinité, Pentecôte, Clarke City, Sept-Îles, Rivière-au-Tonnerre, Mingan,
      Havre-St-Pierre; alternate weeks Baie-Johan-Beetz and Natashquan.
    - North Coaster: fortnightly Montreal - Havre-St-Pierre. North Voyageur: 12-day trips to Blanc-Sablon (1947 dates July 16, Aug. 13; left Market Basin 3 p.m.). North Pioneer:
      12-day North Coast cruises in 1947 (July 23, Aug. 6). 1948 dates for these three not found.
    - Magdalen (Magdalen Islands Transportation Co., Clarke): Pictou - Souris - the Magdalens, 5-day sailings Thursdays, 2-day sailings Tuesdays (to Cap-aux-Meules); connects
      with the North Gaspé's Friday arrival.
    - Competitor: CTMA (Havre-aux-Maisons, Havre-Aubert), Montreal - Quebec - North Shore - Gaspé - Magdalens from 1946: no schedule found.
    - Lower St Lawrence Transportation Co. (Clarke subsidiary, Rimouski; Brendan 23 Nov 2026 raised it): motorships Rimouski, Matane (1938), Jean Brillant (late 1930s), laid up
      at Quebec in winter. Brendan's note: Matane - Godbout - Franquelin - Baie-Comeau daily, timed to the trains; Rimouski and Jean Brillant several times a week to Forestville,
      Ragueneau, Baie-Comeau and on toward Sept-Îles. That note came from Gemini citing the UQAR thesis; the thesis has no such schedule (checked 23 Nov 2026: no
      days, times or train connections; Godbout only in 1962), so it is NOT a source. Thesis: Jean-Brillant, Matane (1938), Rimouski (1939), built at Sorel; the Jean-Brillant
      ran Miami - Nassau 1942 - 46 (back by Aug. 1947). Leads it cites: L'Echo du Bas Saint-Laurent 4 Nov 1950; Camu, Problèmes de transport... (1960), p. 57. St Lawrence Saga ch. 11 gives no 1948 schedule; nearest: the 1950 brochure (Rimouski 9 a.m.;
      Rimouski to Forestville Mon., Wed., Thu., Sat.; Jean Brillant two-day cruises on her Mon. and Thu. sailings, one-day Wed. to Baie-Comeau), 1954 (Sept-Îles arrivals: Jean
      Brillant Tue., Fri.; Matane Wed., Sat.) and 1958 (Matane 10 a.m. Mon., Sat. to Baie-Comeau, Franquelin, Godbout, Baie-Trinité; Tue., Thu. also Pentecôte, Shelter Bay, Sept-Îles).
  The map has only Canada Steamship Lines' Montreal - Quebec - Saguenay (cssg) in this area.
- [ ] Water (Owen Sound Transportation Co. done in Version 183, estimated: a 1948 schedule would firm it up; Ontario Northland's Chief Commanda on Lake Nipissing done in Version 185, highly speculative: the regular 1948 days and hours wanted); Pelee Island and Wolfe Island ferries; Northumberland Ferries (Wood Islands - Caribou); Grand Manan ferry; Clarke Steamship (Gaspe, North Shore). Lake Winnipeg (Keenora) is in; the northern river boats were no longer scheduled common carriers after 1947 (Brendan).

## Cross-border trains cut at the border (stage 4; list of 11 Nov 2026)
- [x] The Ambassador's New York section (CV Table 5, Nos. 74 / 77) runs to Grand Central (V201, Brendan's New Haven / Harlem / GCT traces). (V197: the
  Washingtonian / Montrealer run to Washington on Brendan's NEC2 track; the New Haven and PRR traces may replace it later; New Haven colour #B5651D is Claude's pick).
Each runs to an International Boundary point (time estimated) or to the last Canadian station; the U.S. part waits for the U.S. railways.
- [ ] Niagara River, Black Rock (Buffalo): Michigan Central through trains Windsor - Fort Erie (8 Wolverine, 17, 33 New England Wolverine, 35, 39 / 40 North Shore Limited, 44, 50 / 51 Empire State Express, 364, motors 365 / 366); TH&B Hamilton - Buffalo 73, 76, 371, 372, 374, 375, 379, 380, 382, 383 (through from / to Toronto as CP 7xx / 8xx).
- [ ] The Maple Leaf (Brendan, 20 Nov 2026; Official Guide L.V. Washington - New York table, top rows in the private repo, scans/og1948_lv/maple_leaf_toronto_buffalo_geneva.png).
  Plan: a CN train Toronto - Buffalo, AND a connecting Lehigh Valley train Buffalo - New York (Pennsylvania Station).
  BUILT (V202, V203): the CN train to Buffalo (L.V. station), on_cn_t079n.csv; Suspension Bridge and Niagara Falls, N.Y. (downtown) at Brendan's N.Y.C. station points; the N.Y.C.
  Niagara Falls - Tonawanda - Niagara Jct. from his NYC_Canada_Export.kmz. Open: Depew times estimated; Depew - Buffalo 9.9 mi traced, 8.5 printed (forced); Lehigh Valley red #A3262A is
  Claude's pick. Still to build: the L.V. Buffalo - New York train (rest of the table and the L.V. track east of Batavia is in the KMZ).
  - Read so far (Eastern time). South: Toronto *6.30 p.m., Sunnyside 6.41, Hamilton 7.35, St. Catharines ar 8.18, Niagara Falls, Ont. ar 8.40, Suspension Bridge ar 8.50 (C.N.);
    Suspension Bridge lv *9.00, Niagara Falls, N.Y. ar 9.10, Buffalo ar 10.25 (L.V., 35.1 mi); Buffalo lv h9.40 p.m. (L.V.), Geneva ar 11.39 p.m. ... North: Buffalo ar 4.42 a.m.;
    Buffalo lv h3.50 a.m., Niagara Falls, N.Y. 5.11, Suspension Bridge ar 5.18 (L.V.); Suspension Bridge lv *5.30 (C.N.), Niagara Falls, Ont. 5.45, St. Catharines 6.09, Hamilton
    6.55, Sunnyside 7.44, Toronto ar 7.55 a.m. Note h: the trains connect at Depew, not Buffalo (Depew is not on the map yet).
  - Track (Brendan): the L.V. runs as far north as its own track goes, then N.Y.C. trackage rights to Niagara Falls; in 1948 Niagara Falls trains came over the bridge into the
    N.Y.C. Niagara Falls station, then backed out onto the line along the top of the gorge towards Buffalo. The connection from the station onto the gorge line is Brendan's trace
    (traces/lv/brendan_niagara_gorge_connection.json, own nyc; KML in the private repo; missing from the Mississippi Rails file). Wanted: the rest of the L.V. table (Geneva -
    New York), L.V. / N.Y.C. traces Niagara Falls - Buffalo - Depew - New York, a Depew point (Brendan: 42 54 35.36 N, 78 41 56.96 W; Buffalo L.V. station 42 52 38.87 N, 78 52 31.52 W; L.V. KMZ received 20 Nov 2026). Niagara Falls, N.Y. (N.Y.C. station, also for the L.V.): Brendan's point 43 06 37.09 N, 79 03 04.77 W (43.110303, -79.051325; 20 Nov 2026).
- [x] (V211, Brendan's bridge traces) Niagara Falls bridges (Brendan, 20 Nov 2026): fix the bridge situation. CN and the N.Y.C. had separate bridges, close together; on the map the CN line disappears at the
  international boundary (mid-bridge, where the Ontario collection ends) and the N.Y.C. track jumps across onto the CN bridge (Claude's 0.4 km tie, own nyc, boundary - the junction at
  the U.S. end; tools/mar_import_lv.py). Wanted: the CN bridge drawn whole as CN to the U.S. side and its connection to the N.Y.C., and the N.Y.C. bridge if trains used it.
- [ ] The Gull (V213, V214): wanted: a Lewiston point (Waterville, Bangor at Brendan's points; Portland on track); the B&M station miles (estimated). No. 8's
  dagger at Vanceboro (daily except Sunday) against the column heading (daily June 20 - Sept. 6): entered as the dagger. The rest of MEC Table 2 and B&M Table 8 not entered (Brendan).
- [ ] Michigan Central / N.Y.C. (built V210, V211). Approximate points: Terrace Station, Black Rock; the TH&B trains (DONE V217: on to Buffalo) still end at the Niagara River boundary: run them into
  Buffalo with the Table 6 / 11 times; the N.Y.C. Niagara Falls sections of Nos. 44 / 50 (Table 7) not drawn; the Batavia bypass and Rome / Herkimer alignments: check for 1948.
- [ ] Adirondack Division (V211): Lake Clear Junction, Saranac Lake, Lake Placid points approximate; Utica - Albany - New York for the Montreal trains (on_nycfull_t018.csv) waits for the
  main-line timetable rows.
- [ ] Michigan Central Table 6 (Chicago and Detroit to Niagara Falls and Buffalo, April 25, 1948; Brendan's scan 22 Nov 2026) transcribed, NOT BUILT: on_nycfull_t006.csv
  (Chicago - Detroit, all 16 trains incl. The Mercury, Twilight Ltd., Advance Wolverine, Motor City Special; Welland - Niagara Falls, N.Y.; Welland - Fort Erie - Buffalo incl. TH&B
  380 / 382 / 372 / 374). Needs Michigan Central track Chicago - Detroit and into Buffalo. Found: Nos. 48 The Detroiter and 40 run Detroit - Buffalo via Canada with no Ontario stop
  (48 not on the map yet); No. 358 runs on from Niagara Falls, N.Y. to Buffalo. Checks from the scan: 364 Aylmer p11.33, M362 Fargo 7.25, 366 Lythmore f4.23 are as printed
  (Aylmer probably a misprint). Its UNSURE list is in the file's head.
  Also transcribed, NOT BUILT (Brendan's scans of 22 Nov 2026): Table 11 (westbound, U.S. parts in full: on_nycfull_t011.csv; 20 columns incl. 341, 321, 323, 345 / 347, 315 Motor
  City Special, 31 Twilight Limited, 75 The Mercury, TH&B 371 / 375 / 379 / 383); and from NYC Tables 7 and 9 only the through-Canada trains (Brendan: "through-Canada trains only"):
  on_nycfull_t007x.csv (8, 40, 44, 48, 50 Buffalo - New York) and on_nycfull_t009x.csv (17, 35 The Iroquois, 39, 47, 51 New York - Buffalo). No. 47 / 48 The Detroiter print no
  Buffalo time (Detroit - New York via Ontario, Pullman only; neither is on the map yet).
  Chicago stations (Brendan, 22 Nov 2026): Central Station, Illinois Central property, MC trains by trackage rights over the IC: 41 52 05 N, 87 37 19 W (41.868056, -87.621944);
  IC colours brown and orange (a new railway colour; shades to pick). La Salle Street Station, joint NYC and Rock Island: 41 52 35.71 N, 87 37 56.06 W (41.876586, -87.632239).
- [ ] Niagara River, Suspension Bridge: CN Hamilton - Niagara Falls, N.Y. 86, 90 / 93 The Maple Leaf (see above), 91, 95, 102, 107, 186; MC 358 The Canadian - The Niagara.
- [ ] Detroit River: MC trains above at the tunnel (Windsor - Detroit); NEXT (Brendan, 20 Nov 2026): his NYC_Canada_Export.kmz (Mississippi Rails, private repo traces/lv/) has the
  Michigan Central tunnel and Detroit lines (not the Chicago terminal access): take the CP trains on to Detroit (Detroit times in on_cp_t049w.csv's notes); later string the NYC lines
  together by the Canada Southern. CP Toronto - Windsor 19, 20, 21, 22, 37, 38, 634, 635 (and the pool trains 6 / 22 from Detroit) stop at Windsor. CN's Detroit sections (Brush Street) are built to Detroit.
- [x] St. Clair Tunnel (done in Version 191): CN 5 The La Salle, 6 / 17 The Inter-City Limited, 14 / 15 The International Limited, 20 The Ontario Limited (Grand Trunk Western to Chicago).
  Version 190: GTW Tables 146, 148, 149, 150, 152, 153 built; St. Clair Tunnel, Brush Street and the Chicago line (Elsdon - C&WI - Dearborn Station) in the track. Version 191: CN Table 95 (Port Huron - Chicago) built; the Chicago trains run through to Dearborn Station. Open: a colour for the C&WI (own cwi; Elsdon - Dearborn is drawn in it); the car ferry docks (approximate).
  Grand Trunk Western trace received (Mississippi Rails, Brendan 18 Nov 2026; KMZ in the private repo, traces/msrails/Grand_Trunk_Western.kmz): Port Huron - Flint - Lansing - Battle Creek -
  South Bend - Chicago (to Elsdon), Detroit - Port Huron, Detroit - Pontiac - Durand - Grand Rapids - Muskegon, and branches. Missing (Brendan): the old St. Clair Tunnel (Sarnia - Port Huron),
  Detroit Brush Street station access, and the joint line into Chicago (Elsdon - Dearborn Station, C&WI). Wanted: the Official Guide GTW pages (1948) for the times beyond Port Huron / Detroit.
- [x] Rouses Point, N.Y.: D&H (V205) and Rutland (V207) trains run through to New York.
- [x] East Alburgh, Vt.: CN / Central Vermont 20, 21, 307, 332: done in Version 188 (to Springfield and Boston). Beyond Springfield (New Haven, Pennsylvania) waits for Connecticut / New York track and timetables.
- [x] Norton, Vt. (Island Pond, Portland): CN 11, 12, 16, 17, 111, 112, 126, 209, 210. Done in Version 186: on to Island Pond, Nos. 16 / 126 and 17 through to Portland, the Lewiston branch (Grand Trunk).
- [x] North Troy / Newport, Vt.: CP 209, 210 The Red Wing, 211, 212 The Alouette, 213, 214 (Boston & Maine to Boston): done in Version 187. Still open: Quebec Central 1 / 6 (Beebe - Newport, to meet the Red Wing), B&M station stops between Plymouth / White River Jct. and Concord (with the B&M timetables).
- [x] Malone, N.Y.: New York Central Montreal - Malone, all trains (Version 192); beyond Malone (Utica, Albany, New York: on_nycfull_t018.csv) waits for the NYC. Fort Covington, N.Y.: CN 79 / 80 (done in Version 188, into Fort Covington). Fort Covington station (Brendan, 17 Nov 2026, "tolerably comfortable guessing"): 44 59 36.17 N, 74 29 45.01 W (44.993381, -74.495836); the Grand Trunk trace (Mississippi Rails, traces/maritimes/cn_gtr.geojson, status 'later') ends about 1 km east of it.
- [x] (V213) Vanceboro, Me.: CP 113 / 114 The Gull (Maine Central to Boston); The Pine Tree through cars on CP 40. The Gull to be drawn as Maine Central / B&M-owned (Brendan, 17 Nov 2026). Needs CP Table 11 or the MEC (Vanceboro - Bangor - Portland) and B&M (Portland - Boston) tables. Portland Union Station (Brendan): 43.652243, -70.280710.
- [ ] Fort Frances / International Falls: CN 19 / 20 (Duluth, Winnipeg & Pacific to Duluth).
- [ ] Ending at a border station, connections only (to check): CP 27 / 28 Sault Ste. Marie, Ont. (Soo Line); CP 543 / 544 Coutts (Sweet Grass, Great Northern); CN 600 / 601, 605 / 606, 620 / 621 Sarnia; CN 77 and CP 29 / 30 Prescott (the Ogdensburg car ferry); CN M218 / M219 Fort Erie.

## Short lines (stage 3)
- [x] Cumberland Railway & Coal (Parrsboro - Springhill - Springhill Jct.): built (V164), S&L livery.
- [x] Maritime Coal, Railway & Power: built (V157), Maccan (the CN station) - River Hebert - Joggins Mines. River Hebert times estimated. Colour #4E5D2F is Claude's pick.
- [ ] Sydney & Louisburg at Sydney: Brendan's estimated station point on the S&L trace (V165). Sydney - Victoria Jct. 3.0 mi traced / 4.0 printed.
- [x] Sydney & Louisburg: built (V163). Colour #5B3A8C is Claude's pick. Victoria Jct. - Glace Bay 9.9 mi traced / 11.0 printed (the trace may take a later route).

## Done and answered
### Done in Version 238 (27 Nov 2026)
- Superior - Duluth on NP track (Brendan's piece). All GN lines on track except 0.8 mi into Sioux City Union Depot.
### Done in Version 237 (27 Nov 2026)
- Tilden Jct. - Red Lake Falls and Mossmain - Billings on NP track (Brendan's pieces). Only Superior - Duluth still straight (NP traces to come).
### Done in Version 236 (27 Nov 2026)
- Sioux Falls - Watertown on the South Dakota Central trace (Brendan). Still dashed: Tilden Jct. - Red Lake Falls, Superior - Duluth, Mossmain - Billings.
### Done in Version 235 (27 Nov 2026)
- Stone Arch Bridge route from Brendan's piece; Great Northern station approaches tidied.
### Done in Version 234 (27 Nov 2026)
- GN: Stone Arch Bridge routing (estimated link over the bridge; a trace wanted), Milaca - St. Cloud, Moccasin - Lewistown (Brendan's piece), Garretson - Sioux Falls; Toronto
  Union Station one stop; Chicago "Union Station". Waiting: Brendan's NP traces for Superior - Duluth (and Mossmain - Billings); Sioux Falls - Watertown and Tilden Jct. -
  Red Lake Falls traces.
### Done in Version 233 (27 Nov 2026)
- The Great Northern east of Spokane (50 lines) and the Burlington through section to Chicago. Open: the dashed stretches (Sioux Falls - Watertown, Tilden Jct. - Red Lake Falls,
  Moccasin - Lewistown, Milaca - St. Cloud, Garretson - Sioux Falls, Mossmain - Billings on the NP, Superior - Duluth on the NP): traces or points wanted; most small stations by
  printed mileage (approximate); town points by Claude for Havre, Shelby, Williston, Whitefish, Billings, Bemidji, Sandstone, Elbow Lake, Sioux City, Hutchinson, Sweet Grass,
  Lewistown; the Burlington's own trains (CB&Q tables wanted); the Northern Pacific's Superior trains to share Superior Union Station.
### Done in Version 232 (26 Nov 2026)
- Alaska Transportation Co., S.S. George Washington: Seattle (Pier 58) - Ketchikan - Juneau - Haines - Skagway - Sitka - Ketchikan - Seattle, 8-day cruise every ten days
  (Official Guide ad, May 1948; Daily Alaska Empire, 25 May 1948). Open: livery (Claude's pick); Pier 58 point (est.); port days estimated.
### Done in Version 231 (26 Nov 2026)
- The South Shore Line. Open: station points (all South Shore stations by printed mileage; Randolph Street, Van Buren Street, Hyde Park approximate); the livery (orange and
  maroon, Claude's pick); the Michigan City street running is as in the 2020 map (check for 1948).
### Done in Version 230 (26 Nov 2026)
- Scaling step 1: parts/on_build/ as a folder of railway groups; site data files by group; Mixed train icon in the guide.
### Done in Version 229 (26 Nov 2026)
- Chicagoland view (replaces the North Shore Line and CA&E views); shorter station panels; "On the line" idle while the boxes are hidden; the colour guide (tools/legend.py);
  Buffalo: Terrace Station trains by the Niagara Branch, the others by the Belt Line.
### Done in Version 228 (26 Nov 2026)
- The Chicago Aurora and Elgin. Open: the Sunday "frequent service" Chicago - Wheaton (only first and last trains printed) not drawn; the estimated extra trains; E1455's
  mixed signs; Wayne (the file has an old and a new station location; the old one used).
### Done in Version 227 (25 Nov 2026)
- North Shore Line southbound trains drawn facing forward; Winthrop Harbor (No. 516) at Brendan's place-name latitude.
### Done in Version 226 (25 Nov 2026)
- North Shore Line complete from the 1949 timetable; Loop south-east wye; one track north of the Loop. Open: station points placed by running time (most Shore Line, Skokie
  Valley and Mundelein stations: approximate, each says so in its note; a KML pass like Portland's would fix them); the Lake Bluff -
  Linden Avenue dog-leg at Wilmette follows the file. 
### Done in Version 225 (25 Nov 2026)
- North Shore Line first pass: Chicago - Milwaukee (Skokie Valley Route). Next: the Shore Line (pages 5 - 8; timetables_cnsm/shore_north_PARTIAL.txt has 509 - 531 and 201 / 3 / 5),
  Chicago - Libertyville - Mundelein (pages 9 - 10), the Lake Bluff - Mundelein branch locals (page 9), then the CA&E. Approximate station points to confirm (Racine, North Chicago
  Junction, Dempster Street, the Milwaukee street stops, Merchandise Mart).
### Done in Version 224 (25 Nov 2026)
- Animation jerkiness (Brendan): fixed in the page (list rebuild throttled, day's trips cached, off-screen trains skipped). Tell Claude if a view is still jerky.
### Done in Version 223 (25 Nov 2026)
- Baltimore & Annapolis Railroad built (bna_build.py). Open: station points are place names snapped to the track (approximate; Joyce 1.2 km, Severnside 0.6 km off the track):
  real station points would replace them; the view sits partly under the header (the colour-guide item in "Fixes queued").
### Done in Version 222 (24 Nov 2026)
- Portland Traction track from Brendan's corrected KML (tools/import_track_kml.py). Re-exported for any further correction. Open: the Oregon City 3rd and Main anchor (assumed
  130 m short of 5th and Main: a pin at 3rd and at 5th & Main would settle it); the inbound way on 1st Avenue is not drawn; the Gresham depot position (17.08 mi traced, 18.45 printed).
### Done in Version 220 (24 Nov 2026)
- Portland Traction Gresham Division; Oregon City weekend local stops. Track KML for hand correction sent; corrections applied in V222. Open: the Gresham depot position (17.1 mi traced, 18.45 printed).
### Done in Version 219 (24 Nov 2026)
- Portland Traction Co., Oregon City Division (Time Table No. 2, February 1, 1948; track from the PRL&P KMZ). Open: Moorage and Harney Avenue positions (no miles printed); colour.
### Done in Version 218 (23 Nov 2026)
- Clarke Steamship coastal services, simulated weekly schedules: North Shore (Montreal - Natashquan), North Gaspé (Gaspé cruise; the week stays a Gaspé week by the count from May 11, Brendan 23 Nov 2026), Magdalen (Pictou - Magdalens), and the Lower St
  Lawrence Transportation Co. motorships Rimouski, Jean Brillant and Matane.
### Done in Version 217 (23 Nov 2026)
- TH&B trains on to Black Rock and Buffalo (Central Terminal) over the Michigan Central. Train panels show source and note for every railway.
### Done in Version 216 (23 Nov 2026)
- The Texas Electric Railway, Dallas - Denison and Dallas - Waco. Colour: stays as Claude's pick (Brendan: basic interurban colours, unimportant). Open: dropping the 1939 departures after 9.30 p.m. (Claude's reading of the 1948 page's
  "5:30 a.m. to 9:30 p.m."; the 5.20 / 5.40 a.m. first cars are kept); Vickery and Sterrett placed by miles.
### Done in Version 215 (23 Nov 2026)
- D&H routing at Albany / Troy / Green Island (Green Island curve; Nos. 8 / 10 by Troy, reverse, Watervliet, Albany Union Station; no northerly Albany crossing).
- Norton, N.B. at Brendan's point (CN station, CPR uses it); union station owners (Toronto, Ottawa, St. Paul, Troy, Spokane, Seattle, Tacoma, Washington, Dearborn, Saint John); Fredericton fixed.
- Milwaukee Clipper; C. & B. Line (Chicago evening cruises still open: draw or leave out?); Ashley & Dustin Put-in-Bay steamer (dock points approximate).
### Done in Version 214 (23 Nov 2026)
- The Gull one Maine Central train Saint John - Boston; Portland (Grand Trunk); Portland & Rochester track into Union Station; Waterville correction; Bangor and McAdam points.
### Answered (22 Nov 2026)
- No. 346 Ypsilanti 9.55 - Wayne 10.00 and Kalamazoo 7.07 - Galesburg 7.12, No. 341 Marshall - Ceresco: misprints in the Guide; left as printed (Brendan).
### Done in Version 213 (22 Nov 2026)
- The Gull, Boston - Portland - Bangor - Vanceboro (MEC Nos. 23 / 8); Michigan Central trains join the IC at Kensington.
### Done in Version 212 (22 Nov 2026)
- CP Toronto - Windsor trains on to Detroit (Michigan Central Station).
### Done in Version 211 (22 Nov 2026)
- Niagara bridges, International Bridge, Tonawanda bypass, Chicago terminal approaches (Brendan's traces and KMZ); Table 53; the Adirondack Division.
### Done in Version 210 (22 Nov 2026)
- The Michigan Central Chicago - Detroit and its through trains on to Buffalo and New York (Tables 6, 7, 9, 11); Buffalo Central Terminal and Michigan Central Station named.
### Done in Version 209 (22 Nov 2026)
- GN Seattle - Portland pool trains (401 / 402, 459 / 460) drawn as GN; Saint John Union Station named.
### Done in Version 208 (22 Nov 2026)
- Station names by zoom (city zoomed out; station name or "Town (RR)" zoomed in); Park Avenue, 125th Street, Grand Central Terminal, North Western Terminal, Winnipeg and
  Seattle Union Stations, King Street Station, "(Milwaukee)", Niagara Falls NY / ON, Davie Street and Carrall Street; CPR for CP; station owner from the track under the station.
- Duluth: CN_DULUTH identified as the Union Depot; NOT moved (Brendan, 22 Nov 2026: keep the point, keep the identification).
- North Bay: the ONR stops on the CN and CPR stations (the extra pair placed by mileage is gone).
- Straits of Mackinac car ferry: drawn over the water.
### Done in Version 204 (20 Nov 2026)
- CN Table 79 trains changing number at Hamilton joined (101/102, 89/90, 187/184, 93/94, 91/92, 107/108). Left: 9 / 84 (one column, 2-hour wait, 84 ex Sun), 95 / 6, 83 / 86, 183 / 186.
### Fixes done in Version 201 (20 Nov 2026)
- Arnold Transit boats unnamed (the 1958 M.S. Ottawa name taken off).
- Out-and-back joins (Spl Kenora - Winnipeg - Kenora, skcp005e; mixed M332 Eyre - Acadia Valley - Eyre, skcn229b; linked to their own return trips by the older group-key chaining in
  real_ends.py): left as they are (Brendan, 20 Nov 2026: unimportant; leave unless it causes issues). Removed from the queue.
### Fixes done in Version 194 (19 Nov 2026)
- Stanbridge union station at the Delamere point (45.11758, -73.03388); the CP trains reach it over the Delamere Stanbridge junction siding; the dashed estimate is gone.
### Fixes done in Version 193 (18 Nov 2026)
- CV Table 1 St. Johns - St. Alexander on the SS&C piece up to the M&VJ wye; Stanbridge CP / CV union station; the St. Jerome straight tie removed; Barre & Chelsea plum; TH&B pool trains through Toronto - boundary in TH&B livery.
### Fixes done in Version 147 (9 Nov 2026)
- Unnamed ships carry no label (NFR Cabot Strait steamer); the Yarmouth - Boston boat is labelled with its name, S.S. Yarmouth, and sails from Central Wharf (approximate point).
- Estimated straight links are drawn broken: Saint John, Yarmouth, NFR Port-aux-Basques and Argentia, NTR St. Isidore gap, Mirabel - St. Raymond tie (St. Jerome), Great Western through Chatham (Ont.), Michigan Central Detroit River tunnel. Left solid: trivially short ties (Nelson 0.2 km, Lanoraie 0.5 km, others under 0.3 km) and the links Brendan asked for. A link is marked with "est": true in its geojson.
- North Sydney: the old Intercolonial pieces (round Little Bras d'Or, and by old Sydney Mines) are pre1948 in the importer; the trains take the OSM Sydney Subdivision by Bras d'Or, the loop, Sydney Mines and North Sydney (in and out of the ferry spur), then Leitches Creek.
- Mulgrave - Point Tupper is a train ferry (ferries.geojson, own water) with holds at both slips (a third of the printed interval each, estimated); the trains run out to the end of the Mulgrave switchback tail (row "Mulgrave switchback", ~3 min) and back into Mulgrave.
- Campbellton at Brendan's point on the main line (all Campbellton files). CN Edmundston at Brendan's point (47 21 41.94 N, 68 20 07.84 W), on_cn_t023.

### Answered
- Through trains at Toronto: all joined (Brendan, 11 Nov 2026). Montreal: held; CN 16 Montreal - Portland is not The Maple Leaf. (V166)
- Trip chaining (11 Nov 2026): same-numbered pieces at non-major stations are one train; hubs by ruling; a section with a new number is a new train from the split (the Amtrak way). Built V166.
- CP N.B. track (V162): the missing lines are in Brendan's export (unlabelled ways with small gaps; joined). Points: St. Stephen, Bonny River, Houlton, CP Edmundston (separate from CN's). CN Table 36 at St. Leonard stops on the NTR. (Brendan, 10 Nov 2026)
- Fredericton (V161): CP at York Street Station, CN at the Intercolonial station, Brendan's points (10 Nov 2026).
- Yarmouth (V158, V160): Brendan's OSM export and points: separate CN and DAR stations (V160; one station in V158-159 from a copy-paste slip); Evangeline Wharf (Lovitt Street in CN Table 9 is another name for it) served by both railways' boat trains (CN Nos. 87b / 88b added); the Boston boat at the wharf. Maccan moved to Brendan's point on the Intercolonial (CN and MCR&P). (Brendan, 10 Nov 2026)
- The Dominion Atlantic uses the CN stations at Halifax, Bedford, Windsor Junction, Truro and Middleton: one stop each (merge_stations.py). Windsor Junction at Brendan's point, 44 47 11.3 N, 63 38 23.3 W, for both railways (Brendan, 10 Nov 2026; V155).
- The C.P.S.S. Saint John - Digby steamer (S.S. Princess Helene, daily except Sunday; CP public timetable, April 1948) at Brendan's Long Wharf and Digby Wharf points (10 Nov 2026; V155).
- Newcastle - Loggieville: the OSM line is fine, probably built after 1923 (Brendan, 10 Nov 2026).
- International Railway: leaving the Intercolonial at Tide Head is right if the timetable calls there (Brendan, 10 Nov 2026).
- The Dominion Atlantic is drawn like the other CP subsidiaries (E&N, Quebec Central): own cp. It owns the Windsor Branch to Windsor Jct. (Brendan, 10 Nov 2026)
- Brendan's regional OpenStreetMap export (9 Nov 2026; N.B. and western N.S.) filled these gaps (V151): Saint John E&NA - Union Station; the Saint John Valley line (Saint John - Westfield Beach on CP, Westfield Beach - Fredericton - Woodstock - Centreville: 171.3 mi traced / 172.6); the Kent Northern (26.3 / 26.4); Nelson Junction - Chatham - Loggieville (Newcastle - Loggieville 17.8 / 17.7); the Oxford Junction connector; the International Railway, which leaves the Intercolonial at Tide Head (Tide Head now on the Intercolonial; Campbellton - Edmundston 137.4 / 137.1); the Maritime Coal, Railway & Power track (Maccan - Joggins Mines 11.8 / 12).
- Middleton - Bridgetown (Table 37) is CN's own Middleton & Victoria Beach Railway (the Canadian Northern trace to Port Wade), not the Dominion Atlantic (Brendan, 9 Nov 2026; V150). On to Port Wade still "check" (no 1948 train found).
- The four Pictou County lines on the Wikipedia map (Nova Scotia Coal Co., Acadia Coal Co., Nova Scotia Steel and Coal Co., Vale Railway) were part of the CGR, so CN from 1923: now CN track (Brendan, 9 Nov 2026; V149).
- Through trains: a train runs through as one trip; within one file, use the six-day / seventh-day split (8 Nov). Chaining across files waits until all the CN Maritime files are in, then again for CP. Named trains join only when the names agree (8 Nov). The under-an-hour rule is reopened (9 Nov): see Decisions.
- Saint John is a connecting train, not a through point. Union Station 45.276776, -66.064504 (8 Nov).
- The earlier page was 1113, not 1118; Table 4 is page 1114 (8 Nov).
- North Sydney: the wye is scrapped and the main follows the OSM Sydney Subdivision, with trains using the ferry spur (8 Nov).
- The NFR ferry is a Newfoundland Railway service, and the NFR terminates at 47.5807910, -59.1423107 (8 Nov).
