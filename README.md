# The Digital Model Railway

An animated map of passenger trains and steamships running to their timetables of the summer of 1948 (approximately the week of 5 July 1948),
from British Columbia and Alaska to Washington, the Prairies, the Lakehead and the American Midwest, plus a GTFS feed of the same services.
Inspired by [TRAVIC](https://tracker.geops.ch/).

The map is published from this repository to GitHub Pages; the GTFS feed is at `gtfs.zip` next to the page.

## How it is built

Everything lives in [`pipeline/`](pipeline/). Read [`pipeline/STATE.md`](pipeline/STATE.md) first: it is the working record of the project
(sources, rules, decisions and the list of open fixes).

- **Timetables** are transcribed by hand from the printed timetables into CSV files (`ab_*.csv`, `sk_*.csv`, `wa_*.csv`, …), one per table.
  A wrong time is fixed by editing its CSV.
- **Track** comes from extracts of the National Railway Network (`nrwn/`), traces (`traces/`) and backup sets for lines lifted since 1948.
- **Steps**: each line on the map is made by one build step (listed in `pipeline/steps.json`). A step's result is saved in
  `pipeline/parts/<step>.json`, so only the steps whose inputs change are re-run.
- **Assembly** merges the parts into the page and the GTFS feed. This is what the Pages workflow runs on every push
  (`.github/workflows/pages.yml`).

```
cd pipeline
python3 build.py --status     # every step, and whether it is out of date
python3 build.py              # re-run what is out of date, then assemble
python3 build.py --assemble   # merge the saved parts only (what the deploy does)
```

Re-running the routing steps needs Python with shapely, pyproj, numpy, networkx, scipy, scikit-image, Pillow and pyshp.

## Private sources

Raw third-party files (the original KMZ collections, the full place-names files, timetable scans, data under non-commercial licences) are not
in this repository. They are kept privately with the same paths and linked in with `python3 pipeline/tools/link_sources.py`; the list is
`pipeline/tools/private_paths.txt`. Without them the build still assembles the map: the steps that read them use their saved parts.

## Credits

See [CREDITS.md](CREDITS.md).
