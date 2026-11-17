"""Writes the Newfoundland Railway timetable files (on_nfr_t001 .. t005) for the week of 5 July 1948 (Brendan, 16 Nov 2026: rebuild the
Newfoundland timetable from the 1948 table, the newspaper notices and the 1949 summer schedule; trains known only from the 1948 notices
are estimated from the timetables, "similar to the standard we've been using for steamships").

- Times, stations and miles: Canadian National Railways, "Lines in Newfoundland", Folder N No. 1, effective May 8, 1949 (the summer schedule;
  scans in the private repo, scans/nfld1949). Transcribed by Claude from Brendan's images, 16 Nov 2026.
- Which trains ran and when in July 1948: Newfoundland Railway notices in The Daily News, St. John's, 5 - 9 July 1948 (scans/nfld1948_daily_news):
  local express 5 p.m. Monday and Wednesday "for points to Corner Brook" and Saturday (connecting at Port aux Basques); foreign express
  5 p.m. Tuesday and Thursday; Overland Limited 10 a.m. Sundays; the regular 9 a.m. train to Argentia on Monday; and a train for Bonavista
  at 9 p.m. Wednesday (sleeper Trinity attached). All but the last are the 1949 folder's Nos. 15, 1, 3 and M5 on the same days and hours.
- The Wednesday 9 p.m. Bonavista train is not in the 1949 folder: St. John's - Clarenville is ESTIMATED on No. 15's running times (four hours
  later, '~'); from Clarenville it is taken to be the folder's M27 (Thursday 5.30 a.m.).
- Eastbound trains and all intermediate times are the 1949 folder's (the notices advertise departures from St. John's only).
- The station names already in the map (from the Official Guide of May 1948: Kelligrew's, Shoal Harbor, Stephenville, St. Andrews, Harbor Grace,
  Trinity Junction, Port-aux-Basques ...) are kept, so that their positions hold; stations new from the folder take its spelling.
- 'F': a stop on signal printed with no time ("f"): the time is put in between the train's neighbouring times by the miles ('~f').
- Newfoundland summer time ('NS'): an hour and a half ahead of Atlantic standard time (the folder, General Information).
    python3 tools/nfr_1949.py        (writes the five files in pipeline/)"""
import os, re, sys
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
from ab_table import cell
SRC = ('# Canadian National Railways, "Lines in Newfoundland", Folder N No. 1, May 8, 1949 (summer schedule), used for the week of 5 July 1948 with the days and trains of the\n'
       '# Newfoundland Railway notices in The Daily News, St. John\'s, 5 - 9 July 1948 (Brendan, 16 Nov 2026). Written by tools/nfr_1949.py: see its heading for the rules.\n'
       '# Newfoundland summer time (tz NS: an hour and a half ahead of Atlantic standard). "~": a time not printed, estimated. f: stops on signal.\n')
def fmt(t):
    t %= 86400; h, m = divmod(t // 60, 60)
    return f"{(h % 12) or 12}.{m:02d}{'a' if h < 12 else 'p'}"
def write(fn, title, rows, trains):
    """rows: [(mile, name, principal)] in file order; trains: [(col, attrs, dir, {row index or name: cell})]"""
    name_ix = {}
    for i, r in enumerate(rows): name_ix.setdefault(r[1], i)
    grid = [[''] * len(trains) for _ in rows]
    for c, (col, attrs, d, cells) in enumerate(trains):
        for k, v in cells.items(): grid[k if isinstance(k, int) else name_ix[k]][c] = v
        order = range(len(rows)) if d == 'down' else range(len(rows) - 1, -1, -1)
        seq = [i for i in order if grid[i][c]]
        # times in running order, counting on past midnight
        tt, base, prev = {}, 0, None
        for i in seq:
            x = cell(grid[i][c])
            if not x: continue
            a, b = x[0] + base, x[1] + base
            if prev is not None and a < prev - 4 * 3600: base += 86400; a += 86400; b += 86400
            if b < a: b += 86400
            tt[i] = (a, b); prev = b
        for n, i in enumerate(seq):
            if grid[i][c] != 'F': continue
            lo = next(j for j in reversed(seq[:n]) if j in tt); hi = next(j for j in seq[n + 1:] if j in tt)
            f = (rows[i][0] - rows[lo][0]) / (rows[hi][0] - rows[lo][0])
            grid[i][c] = '~f' + fmt(tt[lo][1] + round((tt[hi][0] - tt[lo][1]) * f / 60) * 60)
    with open(os.path.join(HERE, fn), 'w', encoding='utf-8') as fh:
        fh.write(f'# Newfoundland Railway: {title}\n' + SRC)
        for col, attrs, d, _ in trains: fh.write(f'#train col={col} dir={d} {attrs}\n')
        fh.write('mile,station,principal,prov,tz,' + ','.join(t[0] for t in trains) + '\n')
        for r, g in zip(rows, grid):
            nm = f'"{r[1]}"' if ',' in r[1] else r[1]
            fh.write(f'{r[0]:g},{nm},{r[2]},NL,NS,' + ','.join(g) + '\n')
    print(fn, len(rows), 'stations,', len(trains), 'trains')
def D(txt):
    """'Name: cell; Name: cell' -> dict"""
    return dict((a.strip(), b.strip()) for a, b in (p.split(':', 1) for p in txt.split(';') if p.strip()))

# ---------------------------------------------------------------- the main line
MAIN = [(0, "St. John's", 1), (15.4, 'Manuels', 0), (19.3, "Kelligrew's", 0), (30.3, 'Holyrood', 0), (36.3, 'Avondale', 0), (41.8, 'Brigus Junction', 1), (45.0, "Maher's", 0),
        (49.2, 'Ocean Pond', 0), (54.6, 'Whitbourne', 1), (61.6, 'Placentia Junction', 1), (69.0, 'Long Harbour', 0), (80.0, 'Tickle Harbour', 0), (87.3, 'Rantem', 0), (89.0, 'Upshall', 0),
        (91.4, 'LaManche Siding', 0), (94.5, 'Southern Harbour', 0), (98.5, "Arnold's Cove", 0), (103.2, 'Come-By-Chance', 0), (110.0, "Goobie's", 0), (116.2, 'Northern Bight', 0),
        (131.1, 'Clarenville', 1), (132.8, 'Shoal Harbor', 0), (135.8, 'Shoal Harbour Pit', 0), (143.7, 'Thorburn Lake', 0), (150.9, 'Port Blandford', 1), (164.6, 'Terra Nova', 0),
        (181.0, 'Alexander Bay', 0), (190.0, 'Gambo', 1), (204.2, 'Benton', 0), (213.0, 'Gander', 1), (216.1, "Cobb's Camp", 0), (225.1, 'Monchy', 0), (229.3, 'Appleton', 0), (230.3, 'Glenwood', 0),
        (244.6, 'Notre Dame Junction', 1), (253.9, 'Norris Arm', 0), (262.1, "Jumper's Brook", 0), (267.3, "Bishop's Falls", 1), (276.1, 'Grand Falls', 1), (280.8, 'Red Cliff', 0), (294.3, 'Badger', 0),
        (301.5, "Collishaw's", 0), (302.7, 'Westlake', 0), (310.0, 'Millertown Junction', 1), (324.9, 'Quarry', 0), (332.8, 'Gaff Topsail', 0), (345.7, "Kitty's Brook", 0), (356.6, 'Howley', 0),
        (367.4, 'Northern Siding', 0), (373.6, 'Deer Lake', 1), (387.5, 'Pasadena', 0), (403.8, 'Humbermouth', 1), (405.0, 'Corner Brook', 1), (407.8, 'Curling', 0), (415.3, "Cook's Brook", 0),
        (424.8, 'Beaver Pond', 0), (430.1, 'Spruce Brook', 0), (438.4, "Harry's Brook", 0), (446.5, 'Black Duck', 0), (449.0, "White's Road", 0), (452.5, 'Stephenville', 1), (459.7, "St. George's", 1),
        (465.5, 'Flat Bay', 0), (469.5, 'St. Teresa', 0), (473.1, "Fishell's Siding", 0), (477.2, 'Heatherton', 0), (480.2, "Robinson's", 0), (482.1, 'Cartyville', 0), (484.7, 'Jeffreys', 0),
        (487.7, "St. Fintan's", 0), (498.3, 'Codroy Pond', 0), (512.7, 'South Branch', 0), (522.3, "Doyle's", 0), (525.4, 'Tompkins', 0), (527.9, 'St. Andrews', 0), (538.9, 'Cape Ray', 0),
        (547.2, 'Port-aux-Basques', 1)]
D15 = D("""St. John's: lv 5.00p; Manuels: f5.33p; Kelligrew's: f5.45p; Holyrood: 6.08p; Avondale: 6.27p; Brigus Junction: ar 6.42p / lv 6.53p; Maher's: f7.00p; Ocean Pond: F;
 Whitbourne: ar 7.23p / lv 7.35p; Placentia Junction: f7.52p; Long Harbour: F; Tickle Harbour: f8.38p; Rantem: F; Upshall: F; LaManche Siding: f9.27p; Southern Harbour: F; Arnold's Cove: 9.48p;
 Come-By-Chance: f10.02p; Goobie's: f10.28p; Northern Bight: 10.43p; Clarenville: ar 11.20p / lv 11.50p; Shoal Harbor: f11.55p; Shoal Harbour Pit: 12.03a; Thorburn Lake: f12.23a; Port Blandford: 12.43a;
 Terra Nova: 1.18a; Alexander Bay: 2.02a; Gambo: ar 2.27a / lv 2.37a; Benton: 3.20a; Gander: ar 3.43a / lv 4.10a; Cobb's Camp: f4.17a; Monchy: 4.37a; Appleton: f4.48a; Glenwood: 4.55a;
 Notre Dame Junction: ar 5.28a / lv 5.38a; Norris Arm: 6.03a; Bishop's Falls: ar 6.40a / lv 7.10a; Grand Falls: ar 7.33a / lv 7.45a; Badger: 8.40a; Collishaw's: F; Westlake: F; Millertown Junction: 9.35a;
 Quarry: f10.18a; Gaff Topsail: f10.36a; Kitty's Brook: f11.08a; Howley: 11.40a; Deer Lake: 12.30p; Pasadena: F; Humbermouth: ar 2.00p / lv 2.05p; Corner Brook: ar 2.08p""")
D15S = dict(D15); D15S.update(D("""Corner Brook: ar 2.08p / lv 2.40p; Curling: 2.50p; Cook's Brook: 3.10p; Beaver Pond: f3.34p; Spruce Brook: 3.50p; Harry's Brook: f4.15p; Black Duck: f4.37p;
 White's Road: f4.42p; Stephenville: ar 4.50p / lv 5.10p; St. George's: 5.35p; Flat Bay: F; St. Teresa: f6.00p; Fishell's Siding: f6.11p; Heatherton: F; Robinson's: 6.34p; Cartyville: f6.40p; Jeffreys: F;
 St. Fintan's: 7.00p; Codroy Pond: f7.30p; South Branch: f8.10p; Doyle's: 8.35p; Tompkins: f8.45p; St. Andrews: 8.55p; Cape Ray: f9.25p; Port-aux-Basques: ar 9.45p"""))
D1 = D("""St. John's: lv 5.00p; Manuels: f5.33p; Kelligrew's: f5.45p; Holyrood: 6.08p; Avondale: 6.25p; Brigus Junction: ar 6.39p / lv 6.49p; Maher's: f6.56p; Whitbourne: ar 7.17p / lv 7.24p;
 Tickle Harbour: f8.22p; Arnold's Cove: 9.23p; Come-By-Chance: f9.36p; Goobie's: f9.58p; Northern Bight: 10.13p; Clarenville: ar 10.50p / lv 11.10p; Shoal Harbor: f11.16p; Thorburn Lake: 11.40p;
 Port Blandford: 11.58p; Terra Nova: 12.32a; Alexander Bay: 1.08a; Gambo: ar 1.28a / lv 1.38a; Benton: 2.18a; Gander: 2.44a; Appleton: f3.18a; Glenwood: 3.23a; Notre Dame Junction: ar 3.54a / lv 4.03a;
 Norris Arm: 4.26a; Bishop's Falls: ar 5.00a / lv 5.30a; Grand Falls: ar 5.52a / lv 6.02a; Badger: 6.43a; Millertown Junction: 7.26a; Quarry: f8.05a; Gaff Topsail: f8.25a; Kitty's Brook: f8.53a;
 Howley: 9.20a; Deer Lake: 10.05a; Pasadena: F; Humbermouth: ar 11.30a / lv 11.35a; Corner Brook: ar 11.38a / lv 11.50a; Curling: 11.58a; Spruce Brook: 12.56p; Harry's Brook: f1.21p; Black Duck: 1.45p;
 White's Road: f1.50p; Stephenville: 2.05p; St. George's: 2.25p; Flat Bay: F; St. Teresa: f2.51p; Fishell's Siding: f3.01p; Heatherton: F; Robinson's: 3.25p; Cartyville: f3.30p; Jeffreys: F;
 St. Fintan's: 3.50p; South Branch: f5.00p; Doyle's: 5.25p; Tompkins: f5.35p; St. Andrews: 5.45p; Cape Ray: f6.15p; Port-aux-Basques: ar 6.40p""")
D3 = D("""St. John's: lv 10.00a; Manuels: f10.33a; Holyrood: f11.06a; Avondale: f11.23a; Brigus Junction: ar 11.37a / lv 11.43a; Whitbourne: ar 12.10p / lv 12.17p; Arnold's Cove: f1.57p;
 Northern Bight: f2.41p; Clarenville: ar 3.15p / lv 3.30p; Port Blandford: f4.14p; Terra Nova: f4.44p; Alexander Bay: f5.22p; Gambo: 5.47p; Benton: f6.17p; Gander: 6.38p; Appleton: f7.09p;
 Glenwood: f7.13p; Norris Arm: f8.12p; Bishop's Falls: ar 8.45p / lv 9.00p; Grand Falls: 9.25p; Red Cliff: 9.35p; Badger: 10.05p; Millertown Junction: 10.50p; Howley: 12.36a; Deer Lake: 1.15a;
 Humbermouth: ar 2.25a / lv 2.27a; Corner Brook: ar 2.30a / lv 2.40a; Curling: 2.50a; Spruce Brook: 3.48a; Stephenville: 4.48a; St. George's: 5.04a; Robinson's: 5.51a; Cartyville: f5.55a;
 St. Fintan's: 6.10a; South Branch: f7.16a; Doyle's: 7.38a; Tompkins: f7.48a; St. Andrews: 7.57a; Port-aux-Basques: ar 8.50a""")
B9 = D("""St. John's: lv 9.00p; Holyrood: ~10.08p; Avondale: ~10.27p; Brigus Junction: ~10.42p; Whitbourne: ~11.23p; Arnold's Cove: ~1.48a; Northern Bight: ~2.43a; Clarenville: ~3.20a""")
U2 = D("""Port-aux-Basques: lv 9.00a; Cape Ray: f9.20a; St. Andrews: 9.50a; Tompkins: f9.57a; Doyle's: 10.05a; South Branch: f10.30a; St. Fintan's: 11.40a; Jeffreys: F; Cartyville: f11.58a;
 Robinson's: 12.03p; Heatherton: F; Fishell's Siding: 12.24p; St. Teresa: f12.36p; Flat Bay: F; St. George's: 1.05p; Stephenville: 1.30p; White's Road: f1.40p; Black Duck: 1.45p; Harry's Brook: f2.10p;
 Spruce Brook: 2.30p; Cook's Brook: 3.10p; Curling: 3.30p; Corner Brook: ar 3.35p / lv 3.45p; Humbermouth: ar 3.48p / lv 3.50p; Pasadena: F; Deer Lake: 5.10p; Howley: 5.55p; Kitty's Brook: f6.25p;
 Gaff Topsail: f7.15p; Quarry: f7.33p; Millertown Junction: 8.20p; Badger: 9.05p; Red Cliff: 9.35p; Grand Falls: ar 9.45p / lv 9.55p; Bishop's Falls: ar 10.20p / lv 10.50p; Norris Arm: 11.20p;
 Notre Dame Junction: ar 11.44p / lv 11.51p; Glenwood: 12.23a; Gander: 1.10a; Benton: 1.34a; Gambo: ar 2.17a / lv 2.27a; Alexander Bay: 2.55a; Terra Nova: 3.34a; Port Blandford: 4.06a; Thorburn Lake: 4.30a;
 Clarenville: ar 5.00a / lv 5.20a; Northern Bight: 6.00a; Goobie's: f6.12a; Come-By-Chance: f6.30a; Arnold's Cove: 6.43a; Tickle Harbour: f7.35a; Whitbourne: ar 8.25a / lv 8.31a; Maher's: f8.48a;
 Brigus Junction: ar 8.55a / lv 9.01a; Avondale: 9.14a; Holyrood: 9.30a; Kelligrew's: 9.53a; Manuels: f10.04a; St. John's: ar 10.45a""")
U14 = D("""Port-aux-Basques: lv 9.00a; Cape Ray: f9.22a; St. Andrews: 9.55a; Tompkins: f10.03a; Doyle's: 10.12a; South Branch: f10.42a; Codroy Pond: f11.28a; St. Fintan's: 11.59a; Jeffreys: F;
 Cartyville: f12.20p; Robinson's: 12.28p; Heatherton: F; Fishell's Siding: f12.53p; St. Teresa: f1.08p; Flat Bay: F; St. George's: 1.42p; Stephenville: ar 2.00p / lv 2.10p; White's Road: 2.25p;
 Black Duck: f2.35p; Harry's Brook: f3.00p; Spruce Brook: 3.22p; Beaver Pond: f3.37p; Cook's Brook: f4.04p; Curling: 4.27p; Corner Brook: ar 4.35p / lv 4.50p; Humbermouth: ar 4.55p / lv 5.00p; Pasadena: F;
 Deer Lake: 6.18p; Northern Siding: 6.33p; Howley: 7.05p; Kitty's Brook: f7.35p; Gaff Topsail: f8.25p; Quarry: f8.43p; Millertown Junction: 9.30p; Westlake: F; Collishaw's: F; Badger: 10.15p;
 Grand Falls: ar 10.55p / lv 11.05p; Bishop's Falls: ar 11.30p / lv 11.59p; Norris Arm: 12.32a; Notre Dame Junction: ar 12.56a / lv 1.10a; Glenwood: 1.45a; Cobb's Camp: f2.20a; Gander: ar 2.28a / lv 2.44a;
 Benton: 3.10a; Gambo: ar 3.58a / lv 4.08a; Alexander Bay: 4.40a; Terra Nova: 5.25a; Port Blandford: 5.57a; Thorburn Lake: f6.20a; Shoal Harbor: f6.44a; Clarenville: ar 6.49a / lv 7.10a;
 Northern Bight: 7.51a; Goobie's: f8.03a; Come-By-Chance: f8.22a; Arnold's Cove: 8.36a; Southern Harbour: F; LaManche Siding: f8.55a; Upshall: F; Rantem: F; Tickle Harbour: f9.33a; Long Harbour: F;
 Placentia Junction: f10.10a; Whitbourne: 10.30a; Ocean Pond: F; Maher's: f10.48a; Brigus Junction: 11.00a; Avondale: 11.14a; Holyrood: 11.30a; Manuels: f12.04p; St. John's: ar 12.45p""")
U16 = D("""Corner Brook: lv 11.00a; Humbermouth: ar 11.05a / lv 11.08a; Pasadena: F; Deer Lake: 12.30p; Howley: 1.10p; Kitty's Brook: f1.36p; Gaff Topsail: f2.15p; Quarry: f2.33p; Millertown Junction: 3.15p;
 Westlake: F; Collishaw's: F; Badger: 4.03p; Grand Falls: ar 4.45p / lv 5.05p; Bishop's Falls: ar 5.30p / lv 6.00p; Jumper's Brook: 6.12p; Norris Arm: 6.30p; Notre Dame Junction: ar 6.50p / lv 7.01p;
 Glenwood: 7.32p; Cobb's Camp: f8.05p; Gander: ar 8.12p / lv 8.30p; Benton: 8.52p; Gambo: ar 9.29p / lv 9.38p; Alexander Bay: 10.05p; Terra Nova: 10.44p; Port Blandford: 11.16p; Thorburn Lake: 11.40p;
 Shoal Harbour Pit: 12.03a; Shoal Harbor: f12.09a; Clarenville: ar 12.14a / lv 12.35a; Northern Bight: 1.20a; Goobie's: f1.32a; Come-By-Chance: f1.56a; Arnold's Cove: 2.10a; Southern Harbour: F;
 LaManche Siding: f2.28a; Upshall: F; Rantem: F; Tickle Harbour: f3.05a; Long Harbour: F; Placentia Junction: f3.48a; Whitbourne: ar 4.03a / lv 4.15a; Ocean Pond: F; Maher's: f4.37a;
 Brigus Junction: ar 4.50a / lv 5.01a; Avondale: 5.17a; Holyrood: 5.40a; Manuels: f6.18a; St. John's: ar 7.00a""")
EQ = 'Coaches, dining car and standard sleeping cars (1949 folder).'
write('on_nfr_t001.csv', "main line, St. John's - Port-aux-Basques (547 miles; 3 ft. 6 in. gauge).", MAIN, [
 ('No15', f'num=15 days="Mon,Wed" kind=passenger note="Local express No. 15: St. John\'s 5.00 p.m. Monday and Wednesday for points to Corner Brook (2.08 p.m. next day): the days and hour of the Newfoundland Railway notices of July 1948; times of the May 1949 folder. {EQ}"', 'down', D15),
 ('No15S', f'num=15 days="Sat" kind=passenger note="Local express No. 15: St. John\'s 5.00 p.m. Saturday through to Port-aux-Basques (9.45 p.m. Sunday), connecting there with S.S. Burgeo for the South Coast and at Lewisporte with S.S. Springdale (notices of July 1948); times of the May 1949 folder. {EQ}"', 'down', D15S),
 ('No1', f'num=1 days="Tue,Thu" kind=passenger note="Foreign express No. 1: St. John\'s 5.00 p.m. Tuesday and Thursday to Port-aux-Basques (6.40 p.m. next day) for the North Sydney steamer: the days and hour of the notices of July 1948; times of the May 1949 folder. {EQ}"', 'down', D1),
 ('No3', 'num=3 days="Sun" kind=passenger name="The Overland Limited" note="The Overland Limited, No. 3: St. John\'s 10.00 a.m. Sundays, making direct connection for foreign points (notice of 9 July 1948), Port-aux-Basques 8.50 a.m. Monday for the 9.30 a.m. steamer; times of the May 1949 folder. Coaches, dining car, standard sleeping cars, compartment observation car."', 'down', D3),
 ('B9', 'num="" days="Wed" kind=passenger name="Bonavista train" to="Bonavista (No. 27 from Clarenville)" note="Train for points to Bonavista, St. John\'s 9.00 p.m. Wednesday, sleeper for Trinity attached (Newfoundland Railway notice, 7 July 1948). Not in any timetable in hand: the times to Clarenville are ESTIMATED on No. 15\'s running times; from Clarenville it is taken to be mixed No. 27 (Thursday 5.30 a.m., May 1949 folder)."', 'down', B9),
 ('No2', f'num=2 days="Sun,Wed,Fri" kind=passenger note="Express No. 2: Port-aux-Basques 9.00 a.m. Sunday, Wednesday and Friday (from the North Sydney steamer) to St. John\'s 10.45 a.m. next day. May 1949 folder; the 1948 notices do not give the eastbound trains. Coaches, dining car, standard sleeping cars; compartment observation car from Port-aux-Basques Wednesdays."', 'up', U2),
 ('No14', f'num=14 days="Tue" kind=passenger note="Express No. 14: Port-aux-Basques 9.00 a.m. Tuesday to St. John\'s 12.45 p.m. Wednesday. May 1949 folder; the 1948 notices do not give the eastbound trains. {EQ}"', 'up', U14),
 ('No16', f'num=16 days="Thu,Sat" kind=passenger note="Express No. 16: Corner Brook 11.00 a.m. Thursday and Saturday to St. John\'s 7.00 a.m. next day. May 1949 folder; the 1948 notices do not give the eastbound trains. {EQ}"', 'up', U16)])

# ---------------------------------------------------------------- St. John's - Brigus Junction (the mixed trains' part), then the branches
HEAD = [(0, "St. John's", 1), (8.9, 'Irvine', 0), (13.1, 'Topsail', 0), (15.4, 'Manuels', 0), (19.3, "Kelligrew's", 0), (21.0, 'Upper Gullies', 0), (23.8, 'Seal Cove', 0), (25.4, "Duff's", 0),
        (28.4, 'Briens', 0), (30.3, 'Holyrood', 0), (33.8, "Woodford's", 0), (36.3, 'Avondale', 0), (41.8, 'Brigus Junction', 1)]
DH = "St. John's: lv 9.00a; Irvine: f9.22a; Topsail: f9.30a; Manuels: f9.35a; Kelligrew's: 9.53a; Upper Gullies: F; Seal Cove: F; Duff's: f10.06a; Briens: F; Holyrood: 10.20a; Woodford's: f10.29a; Avondale: 10.40a; "
UH = "Avondale: 5.40p; Woodford's: f5.50p; Holyrood: 6.08p; Briens: F; Duff's: f6.20p; Seal Cove: F; Upper Gullies: F; Kelligrew's: f6.35p; Manuels: f6.45p; Topsail: f6.53p; Irvine: f7.05p; St. John's: ar 7.25p"
BR = HEAD + [(46.3, "Collier's Siding", 0), (48.1, "Turk's Gut Siding", 0), (52.9, 'Brigus', 1), (54.9, 'Cupids', 0), (57.1, 'Makinson', 0), (59.0, "Clarke's Beach", 0), (62.7, 'Country Road Siding', 0),
             (64.1, 'Bay Roberts', 1), (65.3, "Mercer's Siding", 0), (65.8, "Spaniard's Bay", 0), (68.3, 'Tilton', 0), (71.3, 'Riverhead Siding', 0), (74.3, 'Harbor Grace', 1), (76.8, "Bristol's Hope", 0),
             (80.2, 'Carbonear', 1)]
write('on_nfr_t002.csv', "Brigus branch, St. John's - Brigus Junction - Brigus - Bay Roberts - Harbor Grace - Carbonear (mixed trains). Carbonear is 80.2 miles from St. John's (the branch table's 48.4 is a misprint for 38.4). Three Mile Post (stops on signal during the fishing season) is left out.", BR, [
 ('M7', 'num=7 days="Tue,Thu,Sat" kind=mixed note="Mixed No. 7: St. John\'s 9.00 a.m. Tuesday, Thursday and Saturday to Carbonear 1.20 p.m. (May 1949 folder)."', 'down',
  D(DH + "Brigus Junction: ar 10.55a / lv 11.10a; Collier's Siding: F; Turk's Gut Siding: f11.26a; Brigus: 11.45a; Cupids: f11.51a; Makinson: f11.56a; Clarke's Beach: 12.05p; Country Road Siding: f12.15p; Bay Roberts: 12.24p; Mercer's Siding: F; Spaniard's Bay: 12.33p; Tilton: f12.41p; Riverhead Siding: f12.51p; Harbor Grace: 1.05p; Bristol's Hope: F; Carbonear: ar 1.20p")),
 ('M8', 'num=8 days="Tue,Thu,Sat" kind=mixed note="Mixed No. 8: Carbonear 3.05 p.m. Tuesday, Thursday and Saturday to St. John\'s 7.25 p.m. (May 1949 folder)."', 'up',
  D("Carbonear: lv 3.05p; Bristol's Hope: F; Harbor Grace: 3.28p; Riverhead Siding: f3.37p; Tilton: f3.45p; Spaniard's Bay: 3.55p; Mercer's Siding: F; Bay Roberts: 4.07p; Country Road Siding: f4.10p; Clarke's Beach: 4.23p; Makinson: f4.29p; Cupids: f4.34p; Brigus: 4.41p; Turk's Gut Siding: f4.53p; Collier's Siding: F; Brigus Junction: ar 5.10p / lv 5.24p; " + UH))])

AR = HEAD + [(45.0, "Maher's", 0), (49.2, 'Ocean Pond', 0), (54.6, 'Whitbourne', 1), (59.6, 'Spread Eagle', 0), (61.6, 'Placentia Junction', 1), (63.6, '2nd Mile', 0), (64.3, "Rhody's Pond", 0),
             (64.5, 'Beach Grove', 0), (66.8, 'Riverside', 0), (72.9, 'Ville Marie', 0), (76.4, 'Dunville', 0), (78.3, 'Barren Pond', 0), (79.6, 'Argentia Junction', 1), (80.6, 'Placentia', 1),
             (81.6, 'Argentia Junction', 0), (84.6, 'Argentia', 1)]
_n = {r[1]: i for i, r in enumerate(AR)}; _aj1 = len(AR) - 4; _aj2 = len(AR) - 2
M5 = D(DH + "Brigus Junction: ar 10.55a / lv 11.05a; Maher's: f11.13a; Ocean Pond: F; Whitbourne: ar 11.36a / lv 11.44a; Spread Eagle: F; Placentia Junction: ar 11.59a / lv 12.02p; 2nd Mile: F; Rhody's Pond: F; Beach Grove: F; Riverside: F; Ville Marie: f12.33p; Dunville: F; Barren Pond: F; Placentia: ar 12.58p / lv 1.06p; Argentia: ar 1.20p")
M5 = {(_n[k] if k != 'Argentia Junction' else k): v for k, v in M5.items()}; M5[_aj1] = 'ar 12.54p / lv 12.55p'; M5[_aj2] = 'ar 1.09p / lv 1.10p'
M6 = D("Argentia: lv 3.00p; Placentia: ar 3.14p / lv 3.24p; Barren Pond: F; Dunville: F; Ville Marie: f3.46p; Riverside: F; Beach Grove: F; Rhody's Pond: F; 2nd Mile: F; Placentia Junction: ar 4.13p / lv 4.15p; Spread Eagle: F; Whitbourne: ar 4.30p / lv 4.40p; Ocean Pond: F; Maher's: f5.04p; Brigus Junction: ar 5.14p / lv 5.24p; " + UH)
M6 = {_n[k]: v for k, v in M6.items()}; M6[_aj2] = 'ar 3.10p / lv 3.11p'; M6[_aj1] = 'ar 3.27p / lv 3.28p'
write('on_nfr_t003.csv', "Argentia - Placentia branches, St. John's - Placentia Junction - Argentia Junction - Placentia, back to Argentia Junction - Argentia (mixed trains; branch trains 43 / 44 and 41 / 42 between Argentia Junction and Placentia are the same train). Miles past Argentia Junction: the folder's, plus the mile back from Placentia.", AR, [
 ('M5', 'num=5 days="Mon,Wed,Fri" kind=mixed note="Mixed No. 5: St. John\'s 9.00 a.m. Monday, Wednesday and Friday to Placentia 12.58 p.m. and Argentia 1.20 p.m.; the regular 9 a.m. train to Argentia that met S.S. Bar Haven for the Bay Route on Monday 5 July 1948 (Newfoundland Railway notice). Times of the May 1949 folder."', 'down', M5),
 ('M6', 'num=6 days="Mon,Wed,Fri" kind=mixed note="Mixed No. 6: Argentia 3.00 p.m. Monday, Wednesday and Friday, Placentia 3.24 p.m., to St. John\'s 7.25 p.m. (May 1949 folder)."', 'up', M6)])

# ---------------------------------------------------------------- Bonavista branch (miles from Clarenville: the folder's from Shoal Harbour, plus 1.7)
BO = [(0, 'Clarenville', 1), (1.7, 'Shoal Harbor', 1)] + [(round(m + 1.7, 1), n, p) for m, n, p in [
      (.8, 'Church Siding', 0), (1.9, "Mill's Siding", 0), (3.4, 'Milton', 0), (4.0, 'Brickyard', 0), (5.5, "George's Brook", 0), (11.0, "Barrett's Siding", 0), (12.1, 'Twelfth Mile Siding', 0),
      (12.9, "Morley's Siding", 0), (18.0, 'Lethbridge', 1), (19.5, "Hancock's Siding", 0), (21.0, "Pye's Mill", 0), (23.7, "Strickland's Siding", 0), (25.1, 'New Country Siding', 0),
      (27.4, "Parson's Siding", 0), (30.0, 'Southern Bay', 0), (34.8, 'Princeton', 1), (37.0, 'Summerville', 0), (41.5, "Abbott's Siding", 0), (45.0, "Carey's Ridge", 0), (53.0, 'Trinity Junction', 1),
      (55.2, 'Lockston', 0), (57.8, 'Trinity East', 0), (59.3, 'Port Rexton', 1), (60.3, 'Port Rexton Ballast Pit', 0), (63.5, 'English Harbour', 0), (70.5, 'Camp 7', 0), (71.8, 'Wood Spur', 0),
      (77.5, 'Catalina', 1), (82.8, 'Elliston', 0), (88.0, 'Bonavista', 1)]]
FLAGS = ['Church Siding', "Mill's Siding", 'Milton', "George's Brook", "Barrett's Siding", "Morley's Siding", "Hancock's Siding", "Pye's Mill", "Strickland's Siding", "Parson's Siding", 'Summerville',
         "Abbott's Siding", 'Lockston', 'Port Rexton Ballast Pit', 'English Harbour']
TIMED = ['Clarenville', 'Shoal Harbor', 'Brickyard', 'Twelfth Mile Siding', 'Lethbridge', 'New Country Siding', 'Southern Bay', 'Princeton', "Carey's Ridge", 'Trinity Junction', 'Trinity East',
         'Port Rexton', 'Camp 7', 'Wood Spur', 'Catalina', 'Elliston', 'Bonavista']
def bon(cells):
    d = dict(zip(TIMED, [c.strip() for c in cells.split(';')])); assert len(d) == len(TIMED), cells
    d.update({f: 'F' for f in FLAGS}); return d
write('on_nfr_t004.csv', 'Bonavista branch, Clarenville - Shoal Harbor - Trinity Junction - Catalina - Bonavista (mixed trains). Miles from Clarenville (the folder counts from Shoal Harbour).', BO, [
 ('M11', 'num=11 days="Sun" kind=mixed note="Mixed No. 11, Bonavista branch: Clarenville 12.30 a.m. Sunday (after Saturday\'s local express) to Bonavista 5.30 a.m. (May 1949 folder)."', 'down',
  bon('lv 12.30a; ar 12.35a / lv 12.36a; f12.49a; f1.15a; 1.36a; f1.59a; f2.15a; 2.35a; f3.07a; 3.35a; f3.55a; 4.02a; f4.35a; f4.39a; 5.00a; f5.15a; ar 5.30a')),
 ('M23', 'num=23 days="Tue" kind=mixed note="Mixed No. 23, Bonavista branch: Clarenville 9.30 a.m. Tuesday to Bonavista 5.10 p.m. (May 1949 folder)."', 'down',
  bon('lv 9.30a; ar 9.35a / lv 9.40a; f9.57a; f10.30a; 11.10a; f11.35a; f11.59a; 12.30p; f1.15p; 2.00p; f2.20p; 2.30p; f3.28p; f3.40p; 4.15p; f4.50p; ar 5.10p')),
 ('M27', 'num=27 days="Thu" kind=mixed from="St. John\'s (9.00 p.m. Wednesday)" note="Mixed No. 27, Bonavista branch: Clarenville 5.30 a.m. Thursday to Bonavista 10.30 a.m. (May 1949 folder). Taken to be the continuation of the train for points to Bonavista that left St. John\'s at 9.00 p.m. Wednesday 7 July 1948 with the Trinity sleeper (Newfoundland Railway notice)."', 'down',
  bon('lv 5.30a; ar 5.35a / lv 5.36a; f5.49a; f6.15a; 6.36a; f6.59a; f7.15a; 7.35a; f8.07a; 8.35a; f8.55a; 9.02a; f9.35a; f9.39a; 10.00a; f10.15a; ar 10.30a')),
 ('M24', 'num=24 days="Wed" kind=mixed note="Mixed No. 24, Bonavista branch: Bonavista 9.00 a.m. Wednesday to Clarenville 4.00 p.m. (May 1949 folder)."', 'up',
  bon('ar 4.00p; ar 3.50p / lv 3.55p; f3.32p; f2.55p; 2.20p; f1.40p; f1.20p; 1.00p; f12.10p; 11.35a; f11.10a; 11.00a; f10.10a; f10.05a; 9.45a; f9.20a; lv 9.00a')),
 ('M12', 'num=12 days="Mon" kind=mixed note="Mixed No. 12, Bonavista branch: Bonavista 2.30 p.m. Monday to Clarenville 7.30 p.m. (May 1949 folder)."', 'up',
  bon('ar 7.30p; ar 7.23p / lv 7.25p; f7.08p; f6.42p; 6.22p; f5.56p; f5.40p; 5.25p; f4.47p; 4.24p; f4.07p; 4.02p; f3.25p; f3.21p; 3.04p; f2.46p; lv 2.30p')),
 ('M28', 'num=28 days="Thu" kind=mixed note="Mixed No. 28, Bonavista branch: Bonavista 5.30 p.m. Thursday to Clarenville 10.30 p.m. (May 1949 folder)."', 'up',
  bon('ar 10.30p; ar 10.23p / lv 10.25p; f10.08p; f9.42p; 9.22p; f8.56p; f8.40p; 8.25p; f7.47p; 7.24p; f7.07p; 7.02p; f6.25p; f6.21p; 6.04p; f5.46p; lv 5.30p'))])

# ---------------------------------------------------------------- Lewisporte branch
LW = [(0, 'Notre Dame Junction', 1), (9.3, 'Lewisporte', 1)]
def lw(col, num, days, d, a, b, extra=''):
    frm, to = ('Notre Dame Junction', 'Lewisporte') if d == 'down' else ('Lewisporte', 'Notre Dame Junction')
    pretty = lambda t: t[:-1] + (' a.m.' if t[-1] == 'a' else ' p.m.')
    return (col, f'num={num} days="{days}" kind=mixed note="Mixed No. {num}, Lewisporte branch: {frm} {pretty(a)} to {to} {pretty(b)} (May 1949 folder).{extra}"', d,
            {frm: 'lv ' + a, to: 'ar ' + b})
write('on_nfr_t005.csv', 'Lewisporte branch, Notre Dame Junction - Lewisporte (mixed trains meeting the expresses and the coastal steamers).', LW, [
 lw('M21', 21, 'Mon,Thu,Sat', 'down', '12.05a', '12.35a'), lw('M25', 25, 'Wed', 'down', '1.20a', '1.50a'), lw('M17', 17, 'Wed,Fri', 'down', '4.15a', '4.45a'),
 lw('M19', 19, 'Tue,Thu,Sun', 'down', '5.50a', '6.20a', ' Meets the local express from St. John\'s; with S.S. Springdale at Lewisporte (Thursday for Notre Dame Bay, Sunday for Green Bay: notices of July 1948).'),
 lw('M29', 29, 'Thu,Sat', 'down', '7.15p', '7.45p'),
 lw('M18', 18, 'Wed,Fri', 'up', '3.10a', '3.40a'), lw('M20', 20, 'Tue,Thu,Sun', 'up', '4.45a', '5.15a'), lw('M30', 30, 'Thu,Sat', 'up', '6.10p', '6.40p'),
 lw('M22', 22, 'Sun,Wed,Fri', 'up', '11.00p', '11.30p'), lw('M26', 26, 'Wed', 'up', '12.15a', '12.45a')])
