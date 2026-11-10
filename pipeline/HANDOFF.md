# Digital Model Railway: handover for a new chat (8 November 2026)

Read this first, then STATE.md: "Starting a fresh chat", "Build", "Conventions Brendan has set", "Checks" and the "TO DO (1 November 2026)" list. The
version sections at the end of STATE.md (Versions 130-142) hold the details of recent work. Everything else in STATE.md is reference: search it, don't read it through.

## Where things stand
- Version 148 is published (https://bsdawe.github.io/DigitalModelRailway/): 552 lines, 4042 trips, 6348 stops, 52 agencies. CN's Canadian timetables are all in (Versions 143 - 148 in STATE.md); trip chaining is next.
- check_gtfs reports one problem, which is known and accepted: CP-14-SKJCP13 at Minneapolis. The 1947 Soo Line arrival (6.30 a.m.) is after C&NW 404 leaves (6.25).
- A leftover branch, `wip-cdgb`, is on GitHub (the proxy refused to delete it). It is merged; Brendan can delete it.

## Working with Brendan
- Unnamed ships carry no visible label on the map until clicked; never a stand-in such as "Steamer" (Brendan, 9 Nov 2026).
- A straight link that bridges a gap in the track is drawn DASHED, unless it is trivially short or Brendan asked for it; traces stay solid (Brendan, 9 Nov 2026). Give such a link "est": true in its geojson properties.
- When Brendan says "don't fix yet", queue it under "Fixes queued" in TODO.md, and ASK whether to include the queue before the next rebuild.
- TODO.md is the one list of open questions, material wanted from Brendan, and work for Claude (OPEN_QUESTIONS.md and the TO DO lists in STATE.md were merged into it, 9 Nov 2026). Add each new item there; when it is answered or done, move it to "Done and answered" with the date. Mirror it to the project with STATE and HANDOFF. Do not start new TO DO lists in STATE.md.
- Ask before building when something is unclear. Don't build ahead of him on items marked "waiting" or "do not build ahead".
- He dislikes slow work: batch changes into one rebuild, and run only the steps a change touches.
- Connections and buses are not trains, so they are not drawn.
- Times are shown on the Pacific clock. Notes say what time zone was printed (e.g. "Eastern Standard Time as printed").
- Most timetables come from the Official Guide, May 1948. Name the source in the trip notes and the line `src`.
- He sends places as DMS coordinates, KML or traces. Use his points as given. Shared stops use the gid already on file (e.g. CP_BALA, PORT_DULUTH_...).
- He doesn't need running commentary. Report what changed, what is uncertain, and anything he needs to check.

## Routine
- Test any page change in a browser (Playwright, `pipeline/site/` served on a local port) before pushing.
- Commit messages end with the Co-Authored-By / Claude-Session lines the session gives you.
- Pushing to `main` republishes the site (GitHub Actions runs `build.py --assemble` from the committed parts). So:
  - while a build is running, commit only source edits, never half-written `parts/`;
  - don't write files into traces/ or the timetable CSVs during a build;
  - unfinished work that must be pushed goes on a side branch.
- After each version: add a "## Version N" section to STATE.md and update its top line. Then mirror it to the claude.ai project:
  `Projects project_write(path='claude/STATE.md', local_path=<repo>/pipeline/STATE.md)` (and this file as `claude/HANDOFF.md`).
- If a stop hook says there are "unpushed commits" after a push, refresh the remote ref: `git fetch origin '+refs/heads/main:refs/remotes/origin/main'`.
- Run one step only:
  `python3 -c "import build; build.stale_reason=lambda s,p,r: 'asked' if s['name']=='lo_build' else None; build.main([])"`
- Full build: `timeout 7100 python3 -u build.py > log` in the background, about 70-80 minutes (on_build about 60).
- Ontario dry run: `ON_DRY='key*' python3 on_build.py`. Ontario connectors are in `traces/ontario/brendan/ontario_quebec_links.geojson`.

## Boats (recent work)
- `lo_build.py` holds the lake and river boats in Ontario and Quebec:
  - Pointe au Baril, the Muskoka Lakes, Huntsville & Lake of Bays, the Niagara and Cobourg boats, Canada Steamship Lines.
  - Helpers: port(), dms(), water_route(), mkline(), ctrip().
  - Water comes from basemap tiles plus `water_east.json`. A canal is added as a buffered line (see the Port Carling corridor).
- `cdgb_build.py` (new in Version 142) holds the North American and South American:
  - Lanes are cached in `cdgb_legs.json`.
  - The Keweenaw Waterway is hand-traced off the basemap water.
  - Printed passing points are page-only timing points (gids PASS_CDGB_*), not GTFS stops.
  - The livery is a placeholder teal.
- Fleet (Brendan):
  - The C.S.L. rapids boat is the Rapids Prince.
  - Cayuga (Niagara run) and Kingston (lake steamer) are named from a 1949-season account.
  - The four Saguenay boats are the Bateaux Blancs (the white fleet); the timetable needs three of them.
- A new livery needs: CSS vars in 3 places, `.badge.v.X`, a BOAT_COLOR entry, and an entry in the colors list.

## Maritimes (Version 143)
- Order (Brendan): 1 CN Maritimes, 2 CP Maritimes, 3 short lines (incl. Maritime Coal, Railway & Power; Sydney & Louisburg), 4 U.S. connections.
- Track: pipeline/traces/maritimes/ (README there), read by mar_tracks.py (`python3 mar_tracks.py` after adding a file). U.S. railways get their own folders.
- The Maritime timetables are built in on_build (on_cn_*, on_tem_*), so trains from Quebec run through as one trip. New files go in on_build's LAST set.
- Trip chaining across files: do it when all the CN Maritime files are in (plan: pipeline/staged/maritimes/STAGED.md).
- on_build now takes about 100 s (not 60 min); a full `build.py` after an on_build change takes about 8 min (lo_build 3 min).

## Open items
- Brendan is checking the Montreal suburban trains against the CN Montreal employee timetable of 20 June 1948 himself. Wait for his corrections.
- Brendan will send another page of C.S.L. routes.
- Still to do:
  - the Prescott - Ogdensburg car ferry (CP Car & Passenger Transfer Co.);
  - the CN Peebles - Handsworth intermediate stops;
  - the company colours for C.D.&G.B.;
  - the "TO CHECK" items in the STATE.md to-do list;
  - the joint-station review and the expansion-joint pauses (older to-dos in STATE.md).
- `claude/incoming-sk-nrwn.md` in the project is an old (10 October) note and is superseded by STATE.md.
