# To do and open questions

One list for the Digital Model Railway: questions for Brendan, material he is to supply, and work for Claude. It merges OPEN_QUESTIONS.md with the TO DO lists that were kept in STATE.md (the last of them: "TO DO (1 November 2026)"), as Brendan asked on 9 Nov 2026.
Claude adds items as they come up. When one is answered or done, it moves to "Done and answered" with the date. Each open item says what the build does in the meantime. Version tags (V143) say when an item was raised.
Last updated 11 November 2026 (Version 166).

## Decisions for Brendan
- [ ] Fredericton Union Station (CN): Brendan's item, 10 Nov 2026. To be taken up; CN's Fredericton is now the Intercolonial station (V161). (V162)
- [ ] Norton (CP Table 16, Norton - Chipman mixed): did the CP trains use the CN station? Entered for now at the CN Norton stop (Claude's reading). (V159)
- [ ] Unnumbered connecting trains: branch sections printed in a parent train's column take the parent's number (e.g. on_cn_t126m / d / p / c / g). Through cars or separate connecting trains? No number, or "connection to No. 41"? (26 Oct) Brendan: much may settle as the branch tables come in.
- [ ] CN Table 116 (Longlac - Fort William, Nos. 79 / 80): the Toronto section may be a connection with Nos. 3 / 4 at Longlac rather than through cars (Brendan not certain). Matters for chaining. (23 Oct)

## Fixes queued (Brendan: "don't fix yet"; ask before the next rebuild whether to include them)
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
- [ ] The raw GeoPackage, the CGN zips and the OSM exports belong in the private repo. Claude has read-only access there, so they need adding from your side. (V143)
- [ ] ESL livery colour: the placeholder is #7a2430. (V145)

## Work for Claude
- [ ] Build-out order (Brendan, 8 Nov 2026): 1 CN Maritimes (done, V148), 2 CP Maritimes, 3 short lines with 1948 passenger service, 4 U.S. connections (whole U.S. railways in time).
- [ ] Before the U.S. build-out: split parts/on_build.json (25 MB: Ontario, Quebec and the Maritimes in one file) by region or railway, so it stays under GitHub's 50 MB warning (100 MB refuses a push) and each version commits only the changed region; then have the page load a region's data when it is viewed. CP Maritimes is small enough to go first (Brendan, 10 Nov 2026).
- [ ] CP Table 8 south of the border (Newport - Wells River - Boston / New York); Tables 25 / 26 (Montreal - Maine coast, Barre & Chelsea); the Bangor & Aroostook and Maine Central / B&M connections at Brownville Jct., Mattawamkeag and Vanceboro (The Gull and The Pine Tree beyond Vanceboro); the Quebec - Levis ferry (QC Nos. 2 / 5); the Beebe Jct. - Rock Island bus. (25 Oct; U.S. stage) CP Table 10 east of Boundary and the N.B. tables: built (V159).
- [ ] The Prescott - Ogdensburg car ferry (Canadian Pacific Car & Passenger Transfer Co.). (3 Nov)
- [ ] Check the Montreal suburban trains against the CN Montreal employee timetable of June 20, 1948 (https://www.traingeek.ca/files/19480620-ett-montreal-16.pdf). (7 Nov)
- [ ] "Expansion joints": trains pausing mid-run where nothing is printed, at joins between track pieces; find and make them run through. (25 Oct)
- [ ] Pembroke Junction: CN Nos. 1 / 2 (not calling at Pembroke) should run straight through on the through tracks (on_cn_t075b). (23 Oct)
- [ ] Ottawa Union Station: CN trains back out; CP trains may run through or back out by their table. Check the CN routes in and out. (24 Oct)
- [ ] CP Table 51 (Glen Tay - Havelock - Peterboro - Toronto), Table 56 (Toronto - Hamilton), Detroit - Chicago (U.S.): check what is still unbuilt. (25 Oct)
- [ ] Interurban train icon: Brendan is not satisfied; revisit later. (23 Oct)

## Remaining 1948 services (list of 11 Nov 2026)
- [ ] Rail: North Yonge Railways (TTC, Toronto - Richmond Hill; Brendan) (Wabash and Pere Marquette: no passenger service in Canada in 1948; Brendan). Streetcars out of scope so far.
- [ ] Water: Owen Sound Transportation Co. (Manitoulin: Norisle, Normac); Pelee Island and Wolfe Island ferries; Northumberland Ferries (Wood Islands - Caribou); Grand Manan ferry; Clarke Steamship (Gaspe, North Shore). Lake Winnipeg (Keenora) is in; the northern river boats were no longer scheduled common carriers after 1947 (Brendan).

## Cross-border trains cut at the border (stage 4; list of 11 Nov 2026)
Each runs to an International Boundary point (time estimated) or to the last Canadian station; the U.S. part waits for the U.S. railways.
- [ ] Niagara River, Black Rock (Buffalo): Michigan Central through trains Windsor - Fort Erie (8 Wolverine, 17, 33 New England Wolverine, 35, 39 / 40 North Shore Limited, 44, 50 / 51 Empire State Express, 364, motors 365 / 366); TH&B Hamilton - Buffalo 73, 76, 371, 372, 374, 375, 379, 380, 382, 383 (through from / to Toronto as CP 7xx / 8xx).
- [ ] Niagara River, Suspension Bridge: CN Hamilton - Niagara Falls, N.Y. 86, 90 / 93 The Maple Leaf (Lehigh Valley to New York), 91, 95, 102, 107, 186; MC 358 The Canadian - The Niagara.
- [ ] Detroit River: MC trains above at the tunnel (Windsor - Detroit); CP Toronto - Windsor 19, 20, 21, 22, 37, 38, 634, 635 (and the pool trains 6 / 22 from Detroit) stop at Windsor. CN's Detroit sections (Brush Street) are built to Detroit.
- [ ] St. Clair Tunnel: CN 5 The La Salle, 6 / 17 The Inter-City Limited, 14 / 15 The International Limited, 20 The Ontario Limited (Grand Trunk Western to Chicago).
- [ ] Rouses Point, N.Y.: D&H 7, 8, 9, 10, 34, 35 (Montreal - New York); CN Rutland trains 51, 52, 64, 65.
- [ ] East Alburgh, Vt.: CN / Central Vermont 20, 21, 307, 332 (New York, Washington, Boston).
- [ ] Norton, Vt. (Island Pond, Portland): CN 11, 12, 16, 17, 111, 112, 126, 209, 210.
- [ ] North Troy / Newport, Vt.: CP 209, 210 The Red Wing, 211, 212 The Alouette, 213, 214 (Boston & Maine to Boston); Quebec Central 1 / 6 (through to Boston and New York).
- [ ] Malone, N.Y.: New York Central Montreal - New York (4 trains). Fort Covington, N.Y.: CN 79 / 80.
- [ ] Vanceboro, Me.: CP 113 / 114 The Gull (Maine Central to Boston); The Pine Tree through cars on CP 40.
- [ ] Fort Frances / International Falls: CN 19 / 20 (Duluth, Winnipeg & Pacific to Duluth).
- [ ] Ending at a border station, connections only (to check): CP 27 / 28 Sault Ste. Marie, Ont. (Soo Line); CP 543 / 544 Coutts (Sweet Grass, Great Northern); CN 600 / 601, 605 / 606, 620 / 621 Sarnia; CN 77 and CP 29 / 30 Prescott (the Ogdensburg car ferry); CN M218 / M219 Fort Erie.

## Short lines (stage 3)
- [x] Cumberland Railway & Coal (Parrsboro - Springhill - Springhill Jct.): built (V164), S&L livery.
- [x] Maritime Coal, Railway & Power: built (V157), Maccan (the CN station) - River Hebert - Joggins Mines. River Hebert times estimated. Colour #4E5D2F is Claude's pick.
- [ ] Sydney & Louisburg at Sydney: Brendan's estimated station point on the S&L trace (V165). Sydney - Victoria Jct. 3.0 mi traced / 4.0 printed.
- [x] Sydney & Louisburg: built (V163). Colour #5B3A8C is Claude's pick. Victoria Jct. - Glace Bay 9.9 mi traced / 11.0 printed (the trace may take a later route).

## Done and answered
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
