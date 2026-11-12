# Reading a printed railway timetable: instructions for the transcriber

You will be given a scan or photo of one table from a 1940s railway timetable (an Official Guide page or a railway's public timetable). Copy it
exactly into the text format at the end. Someone else will check your work and turn it into data. Copy what is printed; do not interpret, correct
or complete it.

## The rules

1. **Copy, don't interpret.** Write every time, mileage, mark and station name as printed. Never work out a missing time, never "fix" a time that
   looks wrong, never move a value to the row where you think it belongs. If something looks wrong, copy it as printed and mention it in UNSURE.
2. **One printed row, one output row.** Read across each row with a ruler-like eye: the station name, its mileage and every train's cell on that
   same printed line. The most common mistake is a cell slipping up or down one row. Be most careful where:
   - a station name wraps onto two lines (e.g. "Corner of the Beach (Coin / du Banc)"): the times sit on one of the two lines. Give the station
     one row, with the times from whichever line they are printed on, and check the next station's row starts on the next time.
   - there is a run of rows with no times ("..", "–" or blank): count them. After a run, check the next time lands on the right station.
3. **Every cell gets a value**, from this list:

   | Printed | Write |
   |---|---|
   | a time, e.g. 10.05 | the time with a or p: `10.05a` |
   | a time with a flag mark (f, or a small italic f that can look like / or a slash): f10.05, 10f05, /10.05 | `f10.05a` |
   | a flag mark with no time | `f` |
   | any other small sign or reference letter by a time (v, s, x, ‡, †, a box, a dot) | the time, then the sign in brackets: `10.05a[v]`; a sign with no time: `[v]` |
   | ".." , "...", "–", "—" or a vertical line (the train does not stop) | `-` |
   | nothing at all (blank: the train does not run on that part of the table) | leave the cell empty |
   | "Ar." or "Dp." beside a time | `ar 8.55a` / `lv 9.30a` |

4. **A.M. and P.M.** Tables mark them at the top and bottom of each column, and often switch type (light face A.M., **bold** P.M.) or print
   "A.M."/"P.M."/"Noon"/"Night" inside the column where it changes. Track the change down each column and put `a` or `p` on every time.
   12.xx after 11.xx a.m. is `p`; 12.xx after 11.xx p.m. is `a`. If you cannot tell, write your best guess and add `?`.
5. **Stations with two rows (arrive and depart).** Some stations print two lines, e.g. "12.8 Ar } MATAPEDIA, QUE. {Dp" and ".0 Dp } { Ar". Give
   that station ONE row with both times in each cell: `ar 8.55a / lv 9.30a`. Reading up (right-hand columns), the labels are on the right and run
   the other way: the lower time is the arrival, the upper the departure. Always write the earlier time as `ar` and the later as `lv`.
   The mileage often restarts at .0 on the second line (a new section): put the restarted mileage in `mile2`.
6. **Doubt.** If a figure or mark is hard to read, write your best reading followed by `?` (e.g. `11.02p?`, `f?`) and list it under UNSURE with
   the row and train. Flag marks are small and easily missed: if a time looks like it might have a mark before it or inside it (10f25), say so.
7. **Headers and footnotes.** Copy each train's column heading (number, name, days line, e.g. "Sun. only", "Ex. Sun.", "Daily", signs) into its
   TRAIN line, and every footnote and sign explanation printed with the table into SIGNS / NOTES, word for word.
8. **Do not leave anything out.** Every station row, including rows where no train stops, and every train column, including ones that only run on
   part of the table. Connections printed in the table (e.g. "Quebec (via ferry)") are rows too.

## The output format

Plain text, exactly this shape. Use commas between cells; put a station name in double quotes if it contains a comma.

```
TABLE: <railway> <table number> | <title as printed> | <time zone as printed> | <source, page, date>
READ: <which train columns read down and which read up, as printed>
TRAIN <column number as printed> | dir=down or up | heading="<number, days line and signs as printed>" | name="<train name if printed>"
TRAIN ... (one line per train column, left to right)
SIGNS: <each sign and its meaning, as printed in the table's legend>
NOTES: <footnotes, word for word>
UNSURE: <row / train: what is unclear>; <...>   (write UNSURE: none if nothing)
mile,mile2,station,<train>,<train>,...
<rows, top to bottom>
```

- `mile`: the mileage as printed (keep `.0` as `0.0`). `mile2`: only when a station's second line restarts the count; otherwise empty.
- `station`: the name as printed, with any second name in brackets as printed: `Cross Point (Pte à la Croix)`. Keep accents. Keep the
  province or state if printed (`Campbellton, N.B.`). Leave out the dot leaders and any table-reference number after the name, but put it in
  NOTES (e.g. "Matapedia: see Table 30").
- Train columns in the same left-to-right order as the TRAIN lines, headed by the train number (`72`, `36`, ...). Two columns with the same
  number: add a letter (`36`, `36b`).

## Example (the top of CN Table 40, April 1948)

```
TABLE: CN 40 | Campbellton – Matapedia – New Carlisle – Gaspe | Eastern Time – Heure de l'Est | CN Public Timetable, April 1948, p. <n>
READ: 72 and 36 read down; 35 and 71 read up
TRAIN 72 | dir=down | heading="72 Sun. only A.M." | name=""
TRAIN 36 | dir=down | heading="36 Ex. Sun. A.M." | name=""
TRAIN 35 | dir=up | heading="35 Ex. Sun. P.M." | name=""
TRAIN 71 | dir=up | heading="71 Sun. only P.M." | name=""
SIGNS: f stops on signal; ▲ (key not printed with the table)
NOTES: Matapedia: Table 30.
UNSURE: Chandler / 71: 11.02 or 11.00; Janin / 36: f or ..
mile,mile2,station,72,36,35,71
0.0,,"Campbellton, N.B.",lv 8.25a,lv 8.25a,ar 5.20p,ar 6.05p
12.8,0.0,"Matapedia, Que.",ar 8.55a / lv 9.30a,ar 8.55a / lv 9.40a,ar 4.25p / lv 4.40p,ar 5.10p / lv 5.25p
4.7,,Sellars,-,f,f,-
12.8,,Cross Point (Pte à la Croix),f9.54a,10.05a,3.55p,f4.40p
22.1,,Pointe à la Garde,-,f10.25a,f,-
26.7,,Escuminac,f10.23a,f10.35a,f3.25p,f4.14p
...
173.3,,Corner of the Beach (Coin du Banc),-,f,f,-
177.4,,Barachois,4.49p,6.35p,7.55a,f9.30a
202.3,,"Gaspé, Que.",ar 5.50p,ar 7.45p,lv 6.45a,lv 8.30a
```

## Before you hand it in

- Count the station rows in your output and on the page: the same?
- For each train, read its column top to bottom on the page and in your output: the same values in the same order, every flag mark kept?
- Times in each column should run steadily one way (down columns get later going down; up columns get later going up). A time that breaks the
  order usually means a slipped row or a missed A.M./P.M. change: look again, and if it really is printed that way, copy it and say so in UNSURE.
