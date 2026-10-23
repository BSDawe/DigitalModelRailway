# Transcribing the Canadian Pacific Saskatchewan timetables into CSV files

You are transcribing printed railway timetables (scans of a 1940s Canadian Pacific public timetable, about 1948) into CSV files for an animated
map of 1948 trains. Every figure matters: a wrong digit puts a train in the wrong place. Accuracy over speed. Never guess: a figure you cannot
read with certainty gets a `?` after it, and goes in your report.

Work in `/home/claude/bcer`. Scans: `scans/cp1948_sk/*.png` (see its README.md for which table is where) and, for four tables, the earlier
scans in `scans/cp1948/` (Table 6: table006_broadview_field_LARGE.png, table006_stations_miles_zoom.png, table006_broadview_calgary_field.png;
Table 92: table092_winnipeg_saskatoon_wilkie_edmonton.png and table092_wilkie_edmonton_LARGE.png; Table 132:
tables132_135_136_bassano_irricana_kneehill.png). Write only CSV files `sk_cp_t<table>.csv` in `/home/claude/bcer` (suffix a, b, c for
separate sections or lines of one table, e.g. sk_cp_t110a.csv Estevan - Neptune and sk_cp_t110b.csv Bromhead - Minton) and scratch images
under `/tmp/claude-0/-home-claude/c9180052-9db5-5855-a7ae-f6e0acde21e6/scratchpad/sk/`. Do not touch any other file.

## Reading the scans
Several pages are printed sideways. Do not read figures off the whole page. With Python (PIL is installed) crop the table into pieces (one
section, a few hundred pixels across), rotate if sideways, enlarge 3x to 4x with Image.LANCZOS, save to your scratch directory and look at each
piece with the Read tool. Read every time column in its own enlarged crop next to the station names. After writing a file, do a second,
independent pass: crop each column again (different crop boundaries), read it afresh and compare. Fix differences by looking a third time.
If a scan is too small to read a column with certainty, mark the figures `?` and say so; do not invent.

## What to enter (Brendan's rules)
- Passenger-carrying train columns only (passenger, mixed, motor). Leave out freight-only and bus columns.
- Enter each table in full, every station in printed order, with these exceptions:
  - Table 5: only the section Brandon - Broadview (the rest is Manitoba and Ontario).
  - Table 6: only Broadview - Hatton plus Walsh (the first Alberta station); Walsh and west are already entered elsewhere.
  - Tables 92, 120, 132, 133: only up to and including the first Alberta station (the Alberta parts are already entered). Table 92 from
    Winnipeg; Table 120 from Moose Jaw; Table 132 from Swift Current; Table 133 Fox Valley - Schuler and Hilda/Charmian - Estuary - Empress.
  - Tables 104, 105 (all Manitoba), 136, 137 (all Alberta, already entered): skip them and say so.
- Columns: `mile,station,principal,prov,tz,` then one column per train.
  - `prov`: SK, MB or AB for each station: from "Sask", "Man.", "Alta" printed after names, and otherwise by the stations either side
    (a station between two Saskatchewan stations is SK). Mark a row you are unsure of with `?` (e.g. `SK?`).
  - `tz`: C or M, the time zone the table prints for that row ("Central Time" / "Mountain Time" headings, "C.T." / "M.T." after a station).
    Where a station has an arrival in one zone and a departure in the other, write C/M and explain in the comments.
- Miles as printed (do not re-zero). Times exactly as printed, a.m./p.m. worked out from the A.M./P.M. headings and the changes down the column.
  12.00 noon is `12.00p`, midnight `12.00a`.
- principal = 1 for stations in capitals or heavy type, terminals and junctions; else 0.
- Seasonal trains and dates (e.g. Table 108 The Mountaineer, June 30 to September 11; Table 5 specials "Operates June 13..."): enter them, with
  the dates in the train's note.
- For a train that continues beyond the table (into Manitoba, Alberta, the U.S., or another table), put `from=` / `to=` with its real far end
  as printed in headings or notes (e.g. "Winnipeg", "St. Paul", "Lethbridge").

## File format
The Alberta format: read the top of `/home/claude/bcer/ab_table.py`; `ab_cp_t120.csv` is an example (it lacks the prov and tz columns, which are
new for Saskatchewan). In short:

    # comment lines: railway, table number and title, "Times as printed", the signs used and what they mean, anything in doubt
    #train col=M643 num=643 dir=down days="Wed,Fri" kind=mixed from="" to="Lethbridge" note="..."
    mile,station,principal,prov,tz,M643,M644
    0.0,Moose Jaw,1,SK,M,lv 9.00a,ar 5.40p

- One `#train` line per train column; `col` letters and digits only; `num` the number as printed without the M (kind=mixed says it).
- `dir=down` if the train runs down the rows as listed, `up` if up them. `days`: `daily`, `ex Sun`, or a list from Mon Tue Wed Thu Fri Sat Sun
  (no spaces), the days it leaves its first station in the file.
- A cell: `5.30p`; `lv 5.30p`; `ar 9.15p`; `ar 4.35a / lv 5.10a`; `f5.30p` for a flag stop; empty when it does not call.
- Names with a comma must be quoted. Drop "Sask"/"Man."/"Alta" from names (they go in prov); keep everything else as printed.

## Checking
Run `python3 ab_table.py <your file>` after each file. It flags times going backwards and speeds outside 6 to 62 mph. Look again at the scan for
every flag; if the scan really says so, leave it and explain it. (A time-zone change inside a table shows as a jump of an hour: explain it.)

## Order of work, and reporting as you go
Work through the tables in this order: 108, 116, 117-119, 120-122, 123, 125, 111, 109, 110, 112-115, 126-131, 133-135, 107, 106, 103, 98, 5, 6,
92, 132. After every few tables append a short section to
`/tmp/claude-0/-home-claude/c9180052-9db5-5855-a7ae-f6e0acde21e6/scratchpad/sk/PROGRESS.md` (files written; trains with days and kind;
figures in doubt; tables skipped and why), so progress can be followed and corrected while you work. If you receive a message while working,
read it and follow it.

## Your final report
Short and factual: files written and their trains; every figure or sign in doubt; tables skipped; anything odd. Do not paste the CSV contents.
