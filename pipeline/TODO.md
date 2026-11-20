# To do and open questions

One list for the Digital Model Railway: questions for Brendan, material he is to supply, and work for Claude. It merges OPEN_QUESTIONS.md with the TO DO lists that were kept in STATE.md (the last of them: "TO DO (1 November 2026)"), as Brendan asked on 9 Nov 2026.
Claude adds items as they come up. When one is answered or done, it moves to "Done and answered" with the date. Each open item says what the build does in the meantime. Version tags (V143) say when an item was raised.
Last updated 17 November 2026 (Version 180).

## Decisions for Brendan
- [ ] Fredericton Union Station (CN): Brendan's item, 10 Nov 2026. To be taken up; CN's Fredericton is now the Intercolonial station (V161). (V162)
- [ ] Norton (CP Table 16, Norton - Chipman mixed): did the CP trains use the CN station? Entered for now at the CN Norton stop (Claude's reading). (V159)
- [ ] Unnumbered connecting trains: branch sections printed in a parent train's column take the parent's number (e.g. on_cn_t126m / d / p / c / g). Through cars or separate connecting trains? No number, or "connection to No. 41"? (26 Oct) Brendan: much may settle as the branch tables come in.
- [ ] CN Table 116 (Longlac - Fort William, Nos. 79 / 80): the Toronto section may be a connection with Nos. 3 / 4 at Longlac rather than through cars (Brendan not certain). Matters for chaining. (23 Oct)

## Fixes queued (Brendan: "don't fix yet"; ask before the next rebuild whether to include them)
- [ ] SOO LINE READY, BUILD HELD (Brendan, 19 Nov 2026: "Hold the build"). 29 tables transcribed from the Official Guide (May 1948, pages 1047 - 1052; scans in the private repo,
  scans/og1948_soo/): on_soo_t001 ... t026a.csv, built by on_build as CP lines labelled Soo Line (tidpfx SOO; SOO_PLACES; Central time). Track: traces/maritimes/soo.geojson
  (tools/mar_import_soo.py from the Mississippi Rails KMZ). The NEXT on_build run builds them (the glob is wired in): ask Brendan before any rebuild. Dry run (ON_DRY='onsoo*') all on
  track except these straight estimates, waiting for traces or points: Superior - West Duluth - Duluth Soo Line station
  (3.9 mi), Barron - Ridgeland (Table 17), Cameron - Rice Lake (Table 22), Menasha (2.5 km tie, est). Points wanted: Sault Ste. Marie, Mich. Soo station (trace end used), Superior
  (Winter St. and Ogden Ave.; trace end used), Duluth (Superior St. and 6th Ave. W.; estimated point), No. 1 into the Great Northern station at Minneapolis (built to the Milwaukee Road
  station). To check: Table 7 Nos. 8 / 7 daily (Table 9: ex Sat / ex Mon); Table 7 No. 7 Bruce printed 7.35 (left out); Table 6 St. Croix Falls section (left out); Table 13 No. 160
  sign (# MWF or double dagger); Table 23 La Mars state; Chicago: Grand Central Station (B&O property) - Forest Park on Brendan's B&O Chicago Terminal trace (19 Nov 2026), own bo,
  B&O dark blue (#1D3461; dark theme #8AA6DC; Claude's pick of shade), 10.0 mi traced / 10.9 printed; Table 10 Nos. 3 / 4 and Table 26 Nos. 109 / 110 are the existing Mountaineer / Winnipeger (connections only).
- [ ] Stanbridge union station at the Delamere point (Brendan, 19 Nov 2026; V193 used the wrong point): "Gare Stanbridge Union station", CP St. Guillaume subdivision,
  45.1175797, -73.0338785 (quebec_all.json; the collection lookup missed it under the name "Stanbridge Union"). V193 put the merged CP_STANBRIDGE / CN_STANBRIDGE stop at the
  CV track end (45.11138, -73.02607; on_build.py on_cp_t022s and on_cn_t001v places) with an est CP link (-73.0198692, 45.1161065 -> -73.02607, 45.11138) in
  ontario_quebec_links.geojson. To do: both places to the Delamere point; remove the est link (the CP Stanbridge junction track runs to about -73.032); check how the CV
  (on_cn_t001v) track reaches the point and tie it if needed (report the tie length).
- [ ] Out-and-back joins (left for now, Brendan 11 Nov 2026: could be one train movement): Spl Kenora - Winnipeg - Kenora (skcp005e) and mixed M332
  Eyre - Acadia Valley - Eyre (skcn229b) are linked to their own return trips by the older group-key chaining in real_ends.py.

## CP Maritimes (started 10 Nov 2026)
- [ ] DAR readings (V154): No. 33 (Windsor - Kentville, from No. 4) and No. 4 (Truro - Windsor) have no sign: entered daily except Sunday. No. 3 (34-3) entered Saturday only like No. 34. Boat days at Evangeline Wharf: No. 98 Tue., Thu., Sat. (the Boston boat in); No. 95 Tue., Thu. (the boat out; no No. 95 on Sundays); No. 99 leaving Halifax Mon., Wed., Fri. (Brendan: to the wharf on boat days only). Wharf times estimated.
- [ ] Not built yet from the DAR page: the Kentville - Kingsport bus. (V154) The Digby - Saint John steamer is in (V155).
- [ ] CP N.B. stations (V159): Saint John (Union Station), Westfield Beach and Norton entered as the CN stations (Norton: Claude's reading, TO CHECK). Kept apart from CN's: Woodstock, Chipman, Grand Falls, St. Leonard: joint or separate in 1948?
- [ ] CP N.B. readings (V159): Table 10: 39 from Saint John ex Sun, from Megantic daily (Monday train from Megantic entered as No39m); 42 east of Brownville Jct. ex Sun, No. 104 on Sundays; 41 ex Sun from Saint John, No. 103 on Sundays. M117 / M118 (Brownville Jct. - Greenville - Megantic) mixed: Greenville and Holeb arrivals estimated. The Gull 113 / 114 daily (June 20 - Sept. 5). Table 12A 105 waits at Fredericton Jct. 6.30 - 8.55 p.m. as printed. Table 15 Theriault, Sigas, L'Eglise printed "f" without times: left out.

## Questions: readings to check
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
- [ ] Interurban train icon: Brendan is not satisfied; revisit later. (23 Oct)

## Remaining 1948 services (list of 11 Nov 2026)
- [ ] White River Jct. - Boston, B&M 302 / 325 (the Red Wing's and the New Englander's Boston cars in one train): drawn as the CP's Red Wing for now; who owns the leg to be settled with the B&M timetables (Brendan, 17 Nov 2026).
- [ ] Boston & Maine's own trains (waiting for the B&M timetables): the Connecticut River trains of CV Table 5 (702, 72, 712, 78 / 79 the Red Wing's Springfield coach, 7060, 728, 703, 73, 7055, 717, 7059) and White River Jct. - Boston 320 / 313; the stations between White River Jct. / Plymouth and Concord.
- [ ] Central Vermont Table 1: St. Johns - St. Alexander (7.6 mi) is a straight estimate, drawn broken: the Quebec collection lacks that piece of the Montreal & Vermont Junction line (a trace wanted). East Northfield's point is approximate (at the Massachusetts line).
- [ ] Times to check against the scans (tools/check_speeds.py, V176): CP M253 Wickham 7.18 p.m. - Tourvilles f7.22 (5.9 mi; on_cp_t019.csv);
  MC 364 St. Thomas lv 11.28 p.m. - Aylmer f11.33 (10.7 mi; on_mc_t006.csv); CN 32 Luceville 3.20 p.m. - Mont Joli ar 3.25 (8.2 mi; on_cn_t001.csv).
- [ ] Saskatchewan's clock in the view menu: set to Mountain (CP changed at Broadview in 1948, Claude's reading); Brendan to confirm, also Lakehead (Central).
- [ ] Ideas from the 16 Nov 2026 review, not taken up yet: side panels scoped to the view (legend, next departures, B.C. Electric list); station
  boards in the station's own time and opening at the next departure; label overlaps (Montreal terminals, Toronto waterfront, Vancouver steamers);
  shareable links (view, day, time, selection in the address; about 40 lines); ship schedule edits without the 6 1/2-minute lane rebuild.
- [ ] TH&B pool trains (built V193, onthb056p): look up the NYC numbers (Official Guide NYC Buffalo - Toronto table) and add them to the notes. The trains end at the
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
  - Clarke Steamship Company, North Shore coastal service: Quebec, Montreal and South Shore ports to Baie-Comeau, Sept-Iles, Havre-Saint-Pierre,
    Blanc-Sablon (Route 138 not yet through); 1948 fleet incl. North Shore (II) (ex-corvette, 1946) and North Pioneer (1946). Sources:
    https://www.benjidog.co.uk/TheShipsList/ClarkeSSCo.php; https://semaphore.uqar.ca/id/eprint/2457/1/Les%20Clarke%20et%20la%20compagnie%20de%20transport%20du%20Bas%20St-Laurent%20%281921-1970%29.pdf;
    https://clarkesteamship.wordpress.com/tag/north-shore-power-railway-navigation-co/; https://www.boisestgilles.ca/content/historique-maritime.
    Need a 1948 sailing list (Clarke folder or newspaper). Also the Compagnie de transport du Bas-St-Laurent (Rimouski - North Shore) in the same thesis.
  The map has only Canada Steamship Lines' Montreal - Quebec - Saguenay (cssg) in this area.
- [ ] Water (Owen Sound Transportation Co. done in Version 183, estimated: a 1948 schedule would firm it up; Ontario Northland's Chief Commanda on Lake Nipissing done in Version 185, highly speculative: the regular 1948 days and hours wanted); Pelee Island and Wolfe Island ferries; Northumberland Ferries (Wood Islands - Caribou); Grand Manan ferry; Clarke Steamship (Gaspe, North Shore). Lake Winnipeg (Keenora) is in; the northern river boats were no longer scheduled common carriers after 1947 (Brendan).

## Cross-border trains cut at the border (stage 4; list of 11 Nov 2026)
Each runs to an International Boundary point (time estimated) or to the last Canadian station; the U.S. part waits for the U.S. railways.
- [ ] Niagara River, Black Rock (Buffalo): Michigan Central through trains Windsor - Fort Erie (8 Wolverine, 17, 33 New England Wolverine, 35, 39 / 40 North Shore Limited, 44, 50 / 51 Empire State Express, 364, motors 365 / 366); TH&B Hamilton - Buffalo 73, 76, 371, 372, 374, 375, 379, 380, 382, 383 (through from / to Toronto as CP 7xx / 8xx).
- [ ] Niagara River, Suspension Bridge: CN Hamilton - Niagara Falls, N.Y. 86, 90 / 93 The Maple Leaf (Lehigh Valley to New York), 91, 95, 102, 107, 186; MC 358 The Canadian - The Niagara.
- [ ] Detroit River: MC trains above at the tunnel (Windsor - Detroit); CP Toronto - Windsor 19, 20, 21, 22, 37, 38, 634, 635 (and the pool trains 6 / 22 from Detroit) stop at Windsor. CN's Detroit sections (Brush Street) are built to Detroit.
- [x] St. Clair Tunnel (done in Version 191): CN 5 The La Salle, 6 / 17 The Inter-City Limited, 14 / 15 The International Limited, 20 The Ontario Limited (Grand Trunk Western to Chicago).
  Version 190: GTW Tables 146, 148, 149, 150, 152, 153 built; St. Clair Tunnel, Brush Street and the Chicago line (Elsdon - C&WI - Dearborn Station) in the track. Version 191: CN Table 95 (Port Huron - Chicago) built; the Chicago trains run through to Dearborn Station. Open: a colour for the C&WI (own cwi; Elsdon - Dearborn is drawn in it); the car ferry docks (approximate).
  Grand Trunk Western trace received (Mississippi Rails, Brendan 18 Nov 2026; KMZ in the private repo, traces/msrails/Grand_Trunk_Western.kmz): Port Huron - Flint - Lansing - Battle Creek -
  South Bend - Chicago (to Elsdon), Detroit - Port Huron, Detroit - Pontiac - Durand - Grand Rapids - Muskegon, and branches. Missing (Brendan): the old St. Clair Tunnel (Sarnia - Port Huron),
  Detroit Brush Street station access, and the joint line into Chicago (Elsdon - Dearborn Station, C&WI). Wanted: the Official Guide GTW pages (1948) for the times beyond Port Huron / Detroit.
- [ ] Rouses Point, N.Y.: D&H 7, 8, 9, 10, 34, 35 (Montreal - New York); CN Rutland trains 51, 52, 64, 65.
- [x] East Alburgh, Vt.: CN / Central Vermont 20, 21, 307, 332: done in Version 188 (to Springfield and Boston). Beyond Springfield (New Haven, Pennsylvania) waits for Connecticut / New York track and timetables.
- [x] Norton, Vt. (Island Pond, Portland): CN 11, 12, 16, 17, 111, 112, 126, 209, 210. Done in Version 186: on to Island Pond, Nos. 16 / 126 and 17 through to Portland, the Lewiston branch (Grand Trunk).
- [x] North Troy / Newport, Vt.: CP 209, 210 The Red Wing, 211, 212 The Alouette, 213, 214 (Boston & Maine to Boston): done in Version 187. Still open: Quebec Central 1 / 6 (Beebe - Newport, to meet the Red Wing), B&M station stops between Plymouth / White River Jct. and Concord (with the B&M timetables).
- [x] Malone, N.Y.: New York Central Montreal - Malone, all trains (Version 192); beyond Malone (Utica, Albany, New York: on_nycfull_t018.csv) waits for the NYC. Fort Covington, N.Y.: CN 79 / 80 (done in Version 188, into Fort Covington). Fort Covington station (Brendan, 17 Nov 2026, "tolerably comfortable guessing"): 44 59 36.17 N, 74 29 45.01 W (44.993381, -74.495836); the Grand Trunk trace (Mississippi Rails, traces/maritimes/cn_gtr.geojson, status 'later') ends about 1 km east of it.
- [ ] Vanceboro, Me.: CP 113 / 114 The Gull (Maine Central to Boston); The Pine Tree through cars on CP 40. The Gull to be drawn as Maine Central / B&M-owned (Brendan, 17 Nov 2026). Needs CP Table 11 or the MEC (Vanceboro - Bangor - Portland) and B&M (Portland - Boston) tables. Portland Union Station (Brendan): 43.652243, -70.280710.
- [ ] Fort Frances / International Falls: CN 19 / 20 (Duluth, Winnipeg & Pacific to Duluth).
- [ ] Ending at a border station, connections only (to check): CP 27 / 28 Sault Ste. Marie, Ont. (Soo Line); CP 543 / 544 Coutts (Sweet Grass, Great Northern); CN 600 / 601, 605 / 606, 620 / 621 Sarnia; CN 77 and CP 29 / 30 Prescott (the Ogdensburg car ferry); CN M218 / M219 Fort Erie.

## Short lines (stage 3)
- [x] Cumberland Railway & Coal (Parrsboro - Springhill - Springhill Jct.): built (V164), S&L livery.
- [x] Maritime Coal, Railway & Power: built (V157), Maccan (the CN station) - River Hebert - Joggins Mines. River Hebert times estimated. Colour #4E5D2F is Claude's pick.
- [ ] Sydney & Louisburg at Sydney: Brendan's estimated station point on the S&L trace (V165). Sydney - Victoria Jct. 3.0 mi traced / 4.0 printed.
- [x] Sydney & Louisburg: built (V163). Colour #5B3A8C is Claude's pick. Victoria Jct. - Glace Bay 9.9 mi traced / 11.0 printed (the trace may take a later route).

## Done and answered
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
