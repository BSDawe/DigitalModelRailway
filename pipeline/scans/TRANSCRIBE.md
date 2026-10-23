# Transcribing a 1948 timetable scan into a CSV

You are transcribing printed railway timetables (scans of the May 1948 Official Guide, and of the Canadian Pacific's 1948 public timetable) into
CSV files. The files feed an animated map of 1948 trains, so every figure matters: a wrong digit puts a train in the wrong place. Accuracy over speed.
Never guess: a figure you cannot read with certainty gets a `?` after it, and goes in your report.

Work in `/home/claude/bcer`. Write only the CSV files named in your task (in `/home/claude/bcer`) and scratch images under the scratch directory
`/tmp/claude-0/-home-claude/c9180052-9db5-5855-a7ae-f6e0acde21e6/scratchpad/<your task name>/`. Do not touch any other file.

## Reading the scans
The scans are small. Do not read figures off the whole page. With Python (PIL is installed) cut the table into pieces (one table section, a
few hundred pixels across), rotate if the page is sideways, enlarge 3x to 4x with `Image.LANCZOS`, save to your scratch directory and look at
each piece with the Read tool. Read every time column in its own enlarged crop next to the station names. If a `_LARGE` version of a scan is
listed in your task, use it for the figures and the small one only for context.

After writing a file, do a second, independent pass: crop each column again (different crop boundaries), read it afresh and compare it with what
you wrote. Fix differences by looking a third time.

## What to enter
- Only stations in ALBERTA. Tables that cross from Saskatchewan: start at the first Alberta station (the timetable prints "Alta." or "Sask."
  after the stations each side of the boundary; places are also listed in your task where known). Say in the file's comments which is the
  last Saskatchewan station next to the boundary and its mile.
- Every Alberta station the table prints, in the order printed, top to bottom, with the mile as printed (do not re-zero the miles).
- Every passenger-carrying train column (passenger, mixed, motor). Leave out freight-only columns.
- Times exactly as printed (they are Mountain time; do not convert). Work out a.m./p.m. for every figure from the A.M./P.M. headings and
  changes down the column (and light/heavy type). 12.00 noon is `12.00p`, midnight `12.00a`.
- principal = 1 for stations printed in capitals or heavy type, terminals and junctions; else 0.

## File format
Read the top of `/home/claude/bcer/ab_table.py`: it describes the format exactly, and `ab_nar_t179b.csv` and `ab_nar_t179c.csv` are examples.
In short:

    # comment lines: railway, table number and title, date of the table, "Times as printed: MOUNTAIN TIME", the signs used and what
    # they mean, the last Saskatchewan station and its mile (if any), anything in doubt
    #train col=No7 num=7 dir=down days="Mon,Wed,Fri" kind=mixed from="Kerrobert" to="Lacombe" note="..."
    mile,station,principal,No7,No8
    0.0,Edmonton,1,lv 5.30p,ar 7.30a

- One `#train` line per train column. `col` is the CSV column name (letters and digits only, e.g. No7, M617). `num` is the train number as
  printed (keep an M prefix out of num; put kind=mixed). `dir=down` if the train runs down the rows as listed in the file, `up` if it runs up them.
- `days`: `daily`, `ex Sun`, or a comma list from Mon Tue Wed Thu Fri Sat Sun with no spaces (the days the train leaves its first station in the
  file). Get the days from the column heading and from the reference signs.
- `kind`: passenger, mixed or motor. `from` / `to`: where the train starts / ends when that is beyond the rows in the file (e.g. it comes from
  Saskatchewan, or runs through to another table). `note`: train name, through cars, meal stops and anything a passenger would want to know. Short.
- A cell: `5.30p`; `lv 5.30p` (first station); `ar 9.15p` (last station); `ar 4.35a / lv 5.10a` when both are printed; `f5.30p` for a stop on
  signal (flag stop); empty when the train does not call. Other reference signs: explain them in the comment lines, and put what matters to the
  schedule into `days` or `note`.
- One CSV for one line of route: a list of stations a train runs through in order. If a printed table has two separate sections (two
  branches, each with its own trains), write two files, with the suffixes `a` and `b`.
- Station names with a comma must be quoted. No "Alta." in the names.

## Checking
Run `python3 ab_table.py <your files>`. It lists each train and flags times that go backwards and speeds between calls outside 6 to 62 mph.
Look again at the scan for every flag: most are a misread digit, a wrong a.m./p.m., or a mile misread. A flag may also be real (a long
station stop, a layover): if the scan really says so, leave it and explain it in the comments.

## Your report (your final message)
Keep it short and factual:
1. the files written, and for each the trains with days, kind, first and last call and times;
2. the last Saskatchewan station and the first Alberta station, with miles, for tables that cross the boundary;
3. every figure or sign you could not read with certainty (station, column, what you entered), and any part of a scan that is not legible at all;
4. anything odd about the table (footnotes that change the schedule, trains that run only part of the way, connections).
Do not paste the CSV contents into the report.
