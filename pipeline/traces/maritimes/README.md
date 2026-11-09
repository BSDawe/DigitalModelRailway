# Maritime track bank

Track for the Maritime Provinces, 1948 (Brendan, 8 November 2026). **One file per owner or provenance; a new railway is a new file.** Everything here is read
together by `mar_tracks.py` (`python3 mar_tracks.py` prints what is on file and how it connects). Nothing is wired into a build step yet.

| file | what | source |
|---|---|---|
| `cn.geojson` | Canadian Government Railways / CN: Intercolonial, NTR (N.B.), PEI, Cape Breton, Nova Scotia Railway, E&NA, Canada Eastern ...; plus the Inverness & Richmond and Halifax & South Western from the Canadian Northern collection | Wikipedia maps (CGR map; `traces/cnor_all.geojson`), supplied by Brendan |
| `brendan.geojson` | Brendan's own traces: Mulgrave - Point Tupper (ferry piers, yards, Port Hawkesbury mainline), Halifax North Street - Deepwater Terminal. Wikipedia track under them was cut: his trace is the line there | Brendan |
| `industrial.geojson` | Colliery / steel railways on the map (own codes `nscc`, `acc`, `nssc`, `vale`) | Wikipedia maps |

Provenance of the first import: `tools/mar_import_cgr.py` (one-shot, kept as the record). Raw input `CN_Maritimes.gpkg` is Brendan's (private-repo rule: raw files private,
only traces used are public).

## Properties (every feature is one LineString)
`own` railway code (`cn`, `tem`, later `cp`, `dar`, ...; the rail code the build step registers) - `name` - `constituent` (company as Wikipedia names it) - `branch` -
`note` (source line) - `cost` (1.0; lower = a link the trains must take) - `fid` (row in the source file, if any) - `group` (`wikipedia`, `cnor`, `brendan`) -
`status` - `why` (the open question, for `check` and `post1948`).

## Status words
The status says whether the TRACK was there in 1948, nothing else: who may run over it is `own` (a step asks for its owners), and whether a train ran over
it is the timetables' business (a branch with no train is just not routed over). `ok` there - `check` there in 1948? (the question is in `why`; not used
until decided) - `post1948` built after 1948 (Canso Causeway line, rail from May 1955) - `quebec_overlap` the same track is already in the Quebec collection.
`mar_tracks.features()` takes `ok` unless told otherwise, so deciding a `check` piece is changing one word.

## Where a railway goes
- **Canadian railway track in the Maritimes** (CN, CP, a short line): a file here, named for the railway (`cp.geojson`, `sl.geojson` ...).
- **A U.S. railway** (Boston & Maine, Maine Central, Bangor & Aroostook, Central Vermont ...): a folder of its own under `traces/`, named by its code
  (`traces/mec/`, `traces/bar/`), like `traces/milw`, `traces/soo`, `traces/np`. Never in this folder: each will be a whole railway with its own build
  later, and the Maritimes step only borrows the piece it meets (`mar_tracks.DIRS`, or `dirs=`), as `sk_lines` borrows `traces/milw` and `traces/cnmn`.
- **A Canadian railway's track in the U.S.** (CP across Maine, Boundary - Jackman - Brownville Jct. - Vanceboro, with Maine Central rights east of
  Mattawamkeag; CN's Grand Trunk to Portland): its own folder too, like `traces/cnmn` (CN in Minnesota), e.g. `traces/cpme/`.
- **Codes are global**: `own` is the same code everywhere in the project (`cn`, `cp`, `np`, `milw`, `nyc`, `dh`, `tem` ...), plain, no region prefix.
  Check `grep -o "own='[a-z_]*'" *.py` before picking a new one.

## Adding a railway (CP, a short line, a US connection)
1. Put the track in a new file where the section above says (same properties; `own` = its code; `status` `ok`). Brendan's traces of the same railway can go in their own file
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
