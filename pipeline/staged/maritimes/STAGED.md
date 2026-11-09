# Staged for the next full rebuild (Brendan, 8 Nov 2026: "do it with the batch of CN track for the rebuild")

Témiscouata Railway into New Brunswick, through the Quebec build (on_build / on_lines), as Brendan chose (one trip each for Nos. 1 / 2).

1. Move `on_tem_t001.csv` (replaces the live one: the estimated border row goes, St. Jacques Church and Edmundston come in) and `on_tem_t003.csv`
   (mixed 3 / 4 Edmundston - Connors) into `pipeline/`. on_build: a title for on_tem_t003 ('Edmundston – Baker Brook – Clairs – Connors (mixed)') and
   `'on_tem_t003': dict(shift=-14400)` like t001, plus the place points below in its spec dicts.
2. on_lines `_links()`: also read the Maritime track bank, `mar_tracks.features(status='ok')` (each as a link with its own `own`). For 'tem' that gives its
   N.B. line, the station leg and the Connors branch; the CN (NTR) Edmundston - Couturier Siding comes in as other-railway track (cost 2.5, drawn CN), which is
   the trackage-rights stretch. Widen `BOXES['tem']` to (-69.7, -68.25, 47.15, 47.95) (it stops at 47.3 N, short of Connors).
3. Places (on_tem_t001 / on_tem_t003 `places=`): Edmundston (-68.322783, 47.367167) Brendan's (47°22'1.80"N 68°19'22.02"W, "I think"; the CP / Témiscouata station);
   St. Jacques Church (-68.387346, 47.432644, CGN Saint-Jacques, 48 m off the line); Caron Brook (-68.584305, 47.288314), Clairs (-68.603364, 47.252649, CGN
   Clair), Connors (-68.822834, 47.211239), all CGN. Baker Brook, Ledges, Little River Mills by mileage.
4. Expected: Edmundston 81.46 / 81.5 mi; Connors 112.6 / 113.1. The old gid TEM_INTERNATIONAL_BOUNDARY_TEMISCOUATA_TO_EDMUNDSTON_N_B goes away.
5. Later: share the Edmundston stop with CP (same station) when CP Maritimes is built; the CN (NTR) Edmundston station is a separate one, 614 m south.
