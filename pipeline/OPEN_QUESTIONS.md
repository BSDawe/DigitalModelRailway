# Open questions for Brendan

A running tally. Claude adds new questions as they come up and moves answered ones to "Answered" with the answer and date. Each item says what the build does in the meantime.
Last updated 9 November 2026 (Version 147).

## Timetable readings (CN, pages 1113 - 1116)
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
- [ ] Témiscouata No. 4: Baker Brook 8.15 - Edmundston 9.15 a.m., as read. (V143)

## Traces wanted (straight estimated links until then)
- [ ] Saint John: E&NA track end to Union Station (4.5 km). (V143)
- [ ] Yarmouth: track end to the station point. (V145)
- [ ] Newfoundland Railway: trace end to Port-aux-Basques. (V145)
- [ ] Nelson Junction (Table 24). The Wikipedia traces of the Intercolonial and the Chatham Branch only cross, about 2 mi past Derby Junction. A 0.2 km estimated tie there lets the Newcastle - Loggieville motors run, 20.5 mi traced against 17.7 printed. The real connection is wanted. (V146)
- [ ] Stellarton - Westville (Table 29): no CN track joins the Pictou Town Branch to the main line (a 1.2 km gap), so the Pictou trains run over the coal companies' tracks (drawn white). A trace of CN's line is wanted. (V146)
- [ ] Borden - Cape Tormentine car ferry: the course across the strait is a straight estimate between the pier ends. (V146)
- [ ] Oxford Junction connector (MESL to Intercolonial, a 204 m gap; the trains find track anyway). (V143)

## Points and track
- [ ] Approximate station points to confirm or replace: Halifax, Newcastle, Bathurst, Oxford, the Mulgrave / Point Tupper ferry slips. (V145)
- [ ] Edmundston station point (the Témiscouata's): you marked it "I think". (V143) CN's own station: done (V147).
- [ ] Page 1116 approximate points: Charlottetown and Summerside (the town points moved onto the track), Fredericton (the end of the bridge track). (V146)
- [ ] Is Dartmouth fid 40 the Narrows bridge line? For now, the part past fid 41 is pre-1948. (V145)
- [ ] Track bank pieces still marked "check": Wikipedia fids 8, 14, 17, 23. (V143) Now in use: fid 26 Harmony Jct. - Elmira (9.9 mi, as Table 31a prints) and fid 20, the Cape Traverse branch from Emerald Jct. through Kinkora and Albany to the Borden branch. Was the stub on to Cape Traverse still there? (V146)
- [ ] Moncton: the traced miles are Painsec Jct. 7.6 (6.9 printed) and Pacific Jct. 11.3 (12.2), which would put the station about 0.7 mi east. Kept your point as given. (V144)

## Housekeeping
- [ ] Licence of the Wikipedia Canadian Government Railways map data (for the credits). (V143)
- [ ] The raw GeoPackage, the CGN zips and the OSM exports belong in the private repo. Claude has read-only access there, so they need adding from your side. (V143)
- [ ] ESL livery colour: the placeholder is #7a2430. (V145)

## Short lines (stage 3)
- [ ] Maritime Coal, Railway & Power: timetable filed (Official Guide, April 1948). Needs a trace Maccan - River Hebert - Joggins Mines. (9 Nov)
- [ ] Sydney & Louisburg: timetable and track. (8 Nov)

## Fixes done in Version 147 (9 Nov 2026)
- Unnamed ships carry no label (NFR Cabot Strait steamer); the Yarmouth - Boston boat is labelled with its name, S.S. Yarmouth, and sails from Central Wharf (approximate point).
- Estimated straight links are drawn broken: Saint John, Yarmouth, NFR Port-aux-Basques and Argentia, NTR St. Isidore gap, Mirabel - St. Raymond tie (St. Jerome), Great Western through Chatham (Ont.), Michigan Central Detroit River tunnel. Left solid: trivially short ties (Nelson 0.2 km, Lanoraie 0.5 km, others under 0.3 km) and the links Brendan asked for. A link is marked with "est": true in its geojson.
- North Sydney: the old Intercolonial pieces (round Little Bras d'Or, and by old Sydney Mines) are pre1948 in the importer; the trains take the OSM Sydney Subdivision by Bras d'Or, the loop, Sydney Mines and North Sydney (in and out of the ferry spur), then Leitches Creek.
- Mulgrave - Point Tupper is a train ferry (ferries.geojson, own water) with holds at both slips (a third of the printed interval each, estimated); the trains run out to the end of the Mulgrave switchback tail (row "Mulgrave switchback", ~3 min) and back into Mulgrave.
- Campbellton at Brendan's point on the main line (all Campbellton files). CN Edmundston at Brendan's point (47 21 41.94 N, 68 20 07.84 W), on_cn_t023.

## Answered
- Through trains: a train runs through as one trip; within one file, use the six-day / seventh-day split (8 Nov). Chaining across files waits until all the CN Maritime files are in, then again for CP. It joins automatically under an hour; named trains join only when the names agree (8 Nov).
- Saint John is a connecting train, not a through point. Union Station 45.276776, -66.064504 (8 Nov).
- The earlier page was 1113, not 1118; Table 4 is page 1114 (8 Nov).
- North Sydney: the wye is scrapped and the main follows the OSM Sydney Subdivision, with trains using the ferry spur (8 Nov).
- The NFR ferry is a Newfoundland Railway service, and the NFR terminates at 47.5807910, -59.1423107 (8 Nov).
