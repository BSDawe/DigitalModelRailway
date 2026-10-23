# Transcribing the Canadian National Saskatchewan timetables (Official Guide, April 25, 1948)

Same method, format and checking as scans/TRANSCRIBE_SK.md (read it first: crops enlarged 3-4x, two independent passes, '?' for any figure
not certain, prov and tz columns, python3 ab_table.py on every file, PROGRESS.md as you go). Differences:

- Scans: scans/cn1948_sk/*.png (17 images; file names give the tables). Write files sk_cn_t<table>.csv (a, b, c for sections or lines).
- Scratch and PROGRESS.md: /tmp/claude-0/-home-claude/c9180052-9db5-5855-a7ae-f6e0acde21e6/scratchpad/skcn/
- The key to signs is printed on the pages (e.g. on the Table 193-201 page and the Table 180-184 page): use it and quote it in the comments.
  Light/heavy type is not used; times have small "A M"/"P M" heads and sometimes a.m./p.m. by column. A letter before a time is a days sign
  (e.g. a = Mon Wed Fri, b = Tue Thu Sat ...) or f = flag stop: put the days in the train's days= field where they apply to the whole train,
  and explain any that apply to one station only in the comments.
- "+" (coupon station) and the telegraph sign after names: drop them from station names.
- Scope (Brendan): Saskatchewan, plus the Manitoba sections of trains that enter Saskatchewan (through to Winnipeg). Enter:
  - 166: only Winnipeg - Saskatoon - Edmonton as printed (two lines: Winnipeg 0, Saskatoon 470.4, Edmonton 801.5); Edmonton and west is done.
  - 170, 172, 173, 174, 175, 176, 180, 182, 182a, 187, 190, 192 (Saskatchewan parts and Manitoba parts of the same trains, including Hudson
    Bay Jct - The Pas - Flin Flon / Sherridon since those trains run from Saskatchewan), 193a, 196, 199, 200, 201, 207, 212, 214, 225, 226,
    229, 232, 160, 165.
  - Skip and say so: 161 Portage la Prairie - Alonsa, 163 Belmont - Brandon, 183 The Pas - Churchill, 184 Winnipeg - Emerson - Sprague,
    189 Winnipeg - Duluth, 195 Dauphin - Beulah (all Manitoba/Ontario/Minnesota only; 195 trains 15/16 to Winnipeg are in 180); 193
    Drumheller - Trefoil and 216 Vegreville - Camrose (Alberta, already done).
  - Already in the Alberta files and not to be entered again: the Alberta parts of 166 and of trains continuing from Saskatchewan into Alberta
    (Tables 168, 171, 211, 230 are already transcribed for Alberta; not part of this set).
- "Additional Trains" notes under tables (e.g. 192, 193a, 214, 180): enter them as trains with the stations given, and say so.
- Trains printed in two tables: enter each only in its own table (the one that names its full run), and list the overlaps in the report.

Order: 172, 166, 170, 180, 190, 192, 196, 199, 200, 201, 173, 174, 175, 176, 165, 160, 182, 182a, 187, 193a, 207, 212, 214, 225, 226, 229, 232.
Final report: short and factual (files and trains, doubts, skipped tables, overlaps, oddities).
