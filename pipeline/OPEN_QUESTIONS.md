# Open questions for Brendan

A running tally. Claude adds new questions as they come up and moves answered ones to "Answered" with the answer and date. Each item says what the build does in the meantime.
Last updated 9 November 2026 (Version 145).

## Timetable readings (CN, pages 1113 - 1115)
- [ ] No. 20, Folly Lake f3.35 - Londonderry 3.41 a.m. (7.6 mi in 6 min). Was it f3.25? Built as printed. (V144)
- [ ] The second No. 13 column, Sunday only, Moncton 4.30 p.m. Is this a real Sunday train? Entered as 13s. (V144)
- [ ] The "b" sign on 379 / 380. Read as daily except Sat and Sun, the complement of 383 / 384 (Sat only). (V144)
- [ ] 382: dagger or "k"? (V145)
- [ ] No. 26 at Campbellton has a dagger (ex Sun). The file keeps it daily. (V143)
- [ ] 253 / 260: the "-14" columns at Salisbury 1.35. What do they mean? (V145)
- [ ] Témiscouata No. 4: Baker Brook 8.15 - Edmundston 9.15 a.m., as read. (V143)

## Traces wanted (straight estimated links until then)
- [ ] Saint John: E&NA track end to Union Station (4.5 km). (V143)
- [ ] Yarmouth: track end to the station point. (V145)
- [ ] Newfoundland Railway: trace end to Port-aux-Basques. (V145)
- [ ] Oxford Junction connector (MESL to Intercolonial, a 204 m gap; the trains find track anyway). (V143)

## Points and track
- [ ] Approximate station points to confirm or replace: Halifax, Newcastle, Bathurst, Oxford, the Mulgrave / Point Tupper ferry slips. (V145)
- [ ] Edmundston station point: you marked it "I think". (V143)
- [ ] Is Dartmouth fid 40 the Narrows bridge line? For now, the part past fid 41 is pre-1948. (V145)
- [ ] Track bank pieces still marked "check": Wikipedia fids 8, 14, 17, 20, 23, 26. (V143)
- [ ] Moncton: the traced miles are Painsec Jct. 7.6 (6.9 printed) and Pacific Jct. 11.3 (12.2), which would put the station about 0.7 mi east. Kept your point as given. (V144)

## Housekeeping
- [ ] Licence of the Wikipedia Canadian Government Railways map data (for the credits). (V143)
- [ ] The raw GeoPackage, the CGN zips and the OSM exports belong in the private repo. Claude has read-only access there, so they need adding from your side. (V143)
- [ ] ESL livery colour: the placeholder is #7a2430. (V145)

## Fixes queued (Brendan, 9 Nov 2026: flagged, don't fix yet)
- [ ] Unnamed ships show a "Steamer" label. The rule is no visible label until clicked. Cause: the new NFR and ESL sailings in lo_build.py carry num='Steamer'. Older unnamed sailings show how it was done.
- [ ] Straight links over gaps must be drawn dashed, except trivially short ones or ones Brendan asked for. Cause: traces/maritimes/links_estimated.geojson is read into on_lines._links() as ordinary track, so the page gets no est flag and draws it solid. Affected: Saint John (4.5 km), Yarmouth, NFR Port-aux-Basques. The Canso car-ferry link (~1.2 km) is probably "trivially short". Also check the other Quebec-build straight estimates.

- [ ] North Sydney is misrouted (Brendan, 9 Nov 2026). The main should run from Boularderie across the Bras d'Or at the bridge, east toward Sydney Mines, loop round, then south through North Sydney to Leitches Creek and North West Arm, plus a spur to the ferry landing. His map is staged/maritimes/north_sydney_route_brendan.png. Check cn_osm_sydney.geojson against it: which OSM ways the trains took, and whether the Sydney Mines loop is on file.

- [ ] Mulgrave - Point Tupper is a TRAIN FERRY (Brendan, 9 Nov 2026), to be drawn like the Windsor - Detroit CN ferry (Version 112): the link becomes own 'water' (dotted water line, no track, no boat), the train itself crosses, and it holds at each slip for loading and unloading. Now: the 1.2 km link in links_estimated.geojson is own cn, drawn as track, with no slip holds. This replaces the "trivially short" call in the dashed-links item above.
- [ ] Mulgrave switchback (Brendan, 9 Nov 2026): on the Mulgrave side, trains run to the end of the switchback tail just before town, then reverse into Mulgrave, so the map shows the switchback. Check Brendan's Mulgrave traces (brendan.geojson, traces 65 and 107) for the tail. The path-finder will need a forced via point at the tail end, as with the Windsor station reversal.

- [ ] Campbellton stray track (Brendan's screenshot, 9 Nov 2026, No. 223). FOUND: the Campbellton station point (CGN, -66.6835, 47.9993) sits south of the Intercolonial, next to the end of the International Railway (fid 9, from St. Leonard). Trains that start or end at Campbellton (oncn013 Dalhousie, oncn001s from Moncton, oncn001a Gaspe) leave the point on the International's track and curve ~800 m round onto the main; the through trains (oncn001) are unaffected. Fix: put Campbellton on the Intercolonial at the 1948 station. QUESTION: does Brendan have a station point? Also check how fid 9 meets fid 43, so the International joins the main where it really did.

- [ ] Eastern Steamship Lines from the Official Guide (Brendan, 9 Nov 2026; staged/maritimes/esl_official_guide.png). S.S. YARMOUTH, June 2 - Sept. 26. Boston (Central Wharf) 4.30 p.m. EDT Mon, Wed, Fri, to Yarmouth (Evangeline Wharf) 7.30 a.m. AST. Yarmouth 6.30 p.m. AST Sun, Tue, Thu, to Boston 8.30 a.m. EDT. The TIMES ARE ALREADY RIGHT: CN Table 9 printed Boston in Eastern standard time (3.30 p.m., 7.30 a.m.), the same instants as the guide's EDT, and the map's Pacific standard clock gives 12.30 p.m. and 4.30 a.m. either way. Fix: move Boston to CENTRAL WHARF (Brendan, 9 Nov 2026: yes), name the boat "Yarmouth" (so no "Steamer" label), call Yarmouth "Evangeline Wharf" in the notes, and have the notes cite the guide's EDT times next to CN's.

## Answered
- Through trains: a train runs through as one trip; within one file, use the six-day / seventh-day split (8 Nov). Chaining across files waits until all the CN Maritime files are in, then again for CP. It joins automatically under an hour; named trains join only when the names agree (8 Nov).
- Saint John is a connecting train, not a through point. Union Station 45.276776, -66.064504 (8 Nov).
- The earlier page was 1113, not 1118; Table 4 is page 1114 (8 Nov).
- North Sydney: the wye is scrapped and the main follows the OSM Sydney Subdivision, with trains using the ferry spur (8 Nov).
- The NFR ferry is a Newfoundland Railway service, and the NFR terminates at 47.5807910, -59.1423107 (8 Nov).
