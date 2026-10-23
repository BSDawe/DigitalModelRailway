# Transcribing the 1948 Washington timetables into CSV files

You are transcribing printed railway timetables (scans of the 1948 Official Guide pages for the Northern Pacific, Great Northern, Spokane
Portland & Seattle, Union Pacific, Milwaukee Road and Washington Idaho & Montana) into CSV files. The files feed an animated map of 1948 trains,
so every figure matters: a wrong digit puts a train in the wrong place. Accuracy over speed. Never guess: a figure you cannot read with
certainty gets a `?` after it, and goes in your report.

Work in `/home/claude/bcer`. Scans are in `scans/wa1948/` (file names start with the railway: gn_, np_, sps_, up_, milw_, wim_). Write only the
CSV files `wa_<railway>_t<table>.csv` in `/home/claude/bcer` (e.g. `wa_np_t004.csv`, `wa_up_t057.csv`; suffix a, b for two sections of one
table) and scratch images under `/tmp/claude-0/-home-claude/c9180052-9db5-5855-a7ae-f6e0acde21e6/scratchpad/wa/`. Do not touch any other file.

## Reading the scans
The scans are small and several are printed sideways. Do not read figures off the whole page. With Python (PIL is installed) cut the table into
pieces (one section, a few hundred pixels across), rotate if the page is sideways, enlarge 3x to 4x with `Image.LANCZOS`, save to your scratch
directory and look at each piece with the Read tool. Read every time column in its own enlarged crop next to the station names. After writing a
file, do a second, independent pass: crop each column again (different crop boundaries), read it afresh and compare. Fix differences by looking
a third time. If a scan is too small to read a column with certainty, mark the figures `?` and say so; do not invent.

## What to enter (Brendan's rules)
- Passenger-carrying train columns only (passenger, mixed, motor). Leave out freight-only columns, and motor BUS columns (marked as bus, motor
  bus, or the "◆" sign in UP tables): highway services are not on the map.
- Only trains that enter WASHINGTON. For those, enter every station they serve in Washington, and also their stations in OREGON (Portland and
  the Union Pacific's Columbia River line on the south bank: Portland, The Dalles, Umatilla, Pendleton, etc.), because the map includes those
  runs. A table whose trains never enter Washington: skip it and say so.
- IDAHO: stop at the boundary. Enter Washington stations only; say in the comments which is the first Idaho station beyond and its mile, and
  put `from=` / `to=` on the train (the train's real far end as printed in the table heading or notes, e.g. "Chicago", "Lewiston").
  Exception: none. (The Bonners Ferry–Port Hill table is all Idaho: skip it.)
- Every station in the printed order, top to bottom, with the mile as printed (do not re-zero). Times exactly as printed: these tables are
  in PACIFIC time (say so in the comments; if a table section prints Mountain time, say so and enter as printed). Work out a.m./p.m. for every
  figure from the A.M./P.M. headings and changes down the column (and light/heavy type). 12.00 noon is `12.00p`, midnight `12.00a`.
- principal = 1 for stations printed in capitals or heavy type, terminals and junctions; else 0.
- The big main-line tables (NP Table 3, GN Table 5, UP Table 5, Milwaukee main line, SP&S Table 1) run far beyond Washington: enter only the
  Washington part (plus Oregon for SP&S and UP), with `from=`/`to=` for the far ends.
- Seattle–Tacoma–Portland trains are POOLED by the UP, NP and GN and appear in several tables (NP Table 4, GN Table 46, UP Table 5 and 75).
  Transcribe each table as printed anyway; in the report list which train numbers appear in more than one table, and any figure that differs.
  Note which Seattle station each table gives (King St. Station or Union Station) and any "Via Steilacoom" / "Via Point Defiance" notes.

## File format
Exactly the Alberta format: read the top of `/home/claude/bcer/ab_table.py`; `ab_nar_t179c.csv` is an example. In short:

    # comment lines: railway, table number and title, date of the table, "Times as printed: PACIFIC TIME", the signs used and what they mean,
    # the first Idaho station beyond and its mile (if any), anything in doubt
    #train col=No7 num=7 dir=down days="Mon,Wed,Fri" kind=mixed from="Chicago" to="Seattle" note="..."
    mile,station,principal,No7,No8
    0.0,Portland,1,lv 5.30p,ar 7.30a

- One `#train` line per train column. `col` letters and digits only. `num` the train number as printed (keep an M prefix out; kind=mixed).
  `dir=down` if the train runs down the rows as listed in the file, `up` if it runs up them.
- `days`: `daily`, `ex Sun`, or a comma list from Mon Tue Wed Thu Fri Sat Sun with no spaces (the days the train leaves its first station in the
  file), from the column heading and reference signs.
- `kind`: passenger, mixed or motor. `note`: train name, "via Steilacoom", through cars, anything a passenger would want. Short.
- A cell: `5.30p`; `lv 5.30p`; `ar 9.15p`; `ar 4.35a / lv 5.10a`; `f5.30p` for a flag stop; empty when the train does not call.
- One CSV for one line of route. If a table has separate sections (two branches), write separate files (a, b).
- Station names with a comma must be quoted. No "Wash." / "Ore." in the names, but keep "(King St. Sta.)" / "(Union Sta.)" for Seattle and
  "(S. P. & S.)", "(Union Sta.)" etc. where a city has two stations.

## Checking
Run `python3 ab_table.py <your file>` after each file. It flags times going backwards and speeds between calls outside 6 to 62 mph. Look again
at the scan for every flag: most are a misread digit, wrong a.m./p.m., or a mile misread. If the scan really says so, leave it and explain it.

## Order of work, and reporting as you go
Work through the scans one railway at a time in this order: NP, GN, SP&S, UP, Milwaukee, WI&M. After each railway, append a short section to
`/tmp/claude-0/-home-claude/c9180052-9db5-5855-a7ae-f6e0acde21e6/scratchpad/wa/PROGRESS.md` (files written; trains with days and kind; Idaho
boundary stations; figures in doubt; tables skipped and why), so progress can be followed and corrected while you work.

## Your final report
Short and factual: the files written and their trains; boundary stations; every figure or sign in doubt; tables skipped; pooled trains and
differences between tables; anything odd. Do not paste the CSV contents.
