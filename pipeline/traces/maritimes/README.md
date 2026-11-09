# Maritime track bank

Track for the Maritime Provinces, 1948 (Brendan, 8 November 2026). **One file per owner or provenance; a new railway is a new file.** Everything here is read
together by `mar_tracks.py` (`python3 mar_tracks.py` prints what is on file and how it connects). Nothing is wired into a build step yet.

| file | what | source |
|---|---|---|
| `cn.geojson` | Canadian Government Railways / CN: Intercolonial, NTR (N.B.), PEI, Cape Breton, Nova Scotia Railway, E&NA, Canada Eastern ...; plus the Inverness & Richmond and Halifax & South Western from the Canadian Northern collection | Wikipedia maps (CGR map; `traces/cnor_all.geojson`), supplied by Brendan |
| `brendan.geojson` | Brendan's own traces: Mulgrave - Point Tupper (ferry piers, yards, Port Hawkesbury mainline), Halifax North Street - Deepwater Terminal. Wikipedia track under them was cut: his trace is the line there | Brendan |
| `industrial.geojson` | Colliery / steel railways on the map (not CN) | Wikipedia maps |

Provenance of the first import: `tools/mar_import_cgr.py` (one-shot, kept as the record). Raw input `CN_Maritimes.gpkg` is Brendan's (private-repo rule: raw files private,
only traces used are public).

## Properties (every feature is one LineString)
`own` railway code (`cn`, `tem`, later `cp`, `dar`, ...; the rail code the build step registers) - `name` - `constituent` (company as Wikipedia names it) - `branch` -
`note` (source line) - `cost` (1.0; lower = a link the trains must take) - `fid` (row in the source file, if any) - `group` (`wikipedia`, `cnor`, `brendan`) -
`status` - `why` (the open question, for `check` and `post1948`).

## Status words
`ok` use - `check` in the file but not used until decided (the question is in `why`) - `post1948` built after 1948 (Canso Causeway line, rail from May 1955) -
`not_cn` another company - `quebec_overlap` already in the Quebec collection. `mar_tracks.features()` takes `ok` unless told otherwise, so deciding a `check` piece is
changing one word.

## Adding a railway (CP, a short line, a US connection)
1. Put the track in a new `<name>.geojson` (same properties; `own` = its code; `status` `ok`). Brendan's traces of the same railway can go in their own file
   (`brendan_<area>.geojson`) with the collection piece under them cut.
2. `python3 mar_tracks.py --owner <code>`: the connected groups and the loose ends within 1.5 km (connector candidates). Connectors are ordinary features in a
   `links_<area>.geojson`, `cost` 0.9, `note` says estimated.
3. The step that builds the timetable registers the rail and reads `mt.features(owner=...)`. Through running over another railway's track (CN trains over CP
   rights, CN over the E&NA ...) = `owner=('cn', 'cp')` with the other owner's cost raised in the graph, as `on_lines._graph` does.

## Open
- Gaps to join (estimated links, Brendan to say): Gulf Shore - Caraquet 209 m; Montreal & European Short Line - Intercolonial 204 m; International Railway - NTR 487 m;
  Nova Scotia Railway - Dartmouth Branch 525 m; Liverpool & Milton - Halifax & South Western 676 m; Chatham Branch - Northern & Western 983 m; Pictou Town Branch -
  Nova Scotia Railway 1,180 m; Fredericton bridge extension - Chatham Branch 1,546 m. Cape Breton Railway (Wikipedia) ends 29.6 km short of other track.
- PEI is a separate network (Cape Tormentine - Borden car ferry); Mulgrave and Point Tupper are separate until the Strait of Canso ferry is built.
- Ties to the Quebec build: Restigouche crossing (-66.93886, 47.97488) and the NTR boundary point (-68.7317, 47.372).
