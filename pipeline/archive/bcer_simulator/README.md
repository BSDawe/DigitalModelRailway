# B.C. Electric system simulator: the page as it was (29 October 2026)

Brendan (29 Oct 2026): keep the B.C. Electric code and styling the map ran on until now, for a future "BCER system simulator", before the BCER lines
were restyled into the uniform interurban style.

- `page_template_cd8a1b3.html`: the page template at commit cd8a1b3 (git tag `bcer-simulator-base`), with the BCER-specific drawing and panels:
  - drawTrain: Chilliwack trains as two coupled cars, local cars (Central Park, Burnaby Lake, Lulu Island, Marpole - New Westminster) as single cars,
    double-track running on the right, cars waiting in passing sidings with the pulsing meeting halo (st.e.meet), direction nose;
  - track: the BCER lines (PATH_ROUTE, PATH_LINES) in ink, stations as circles ringed in each line's colour (LINE_COLOR: local, lake, lulu, nwm);
  - legend: B.C. Electric car plus five line rings; the "On the line" panel with a Chilliwack line heading and one heading per local line, car counts,
    "Next Central Park cars"; the line-specific notes in the train panel.
- The data side (BCER lines, chains, meets, sidings) is unchanged in the pipeline (build steps for the Fraser Valley and the local lines).
