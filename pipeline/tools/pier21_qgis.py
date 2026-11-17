# Pier 21 ship arrivals for one year, into a CSV file. For the QGIS Python console (Brendan, 17 Nov 2026).
#
# In QGIS: Plugins > Python Console > Show Editor > open this file > Run (the green arrow). Progress prints in the console.
# The CSV is saved in your home folder (the path is printed at the end). Needs nothing beyond the Python that comes with QGIS.
#
# How it works: the database (https://pier21.ca/immigration-records/ship-arrival-database) can only be filtered by ship, so the script
# sorts the whole list by year and jumps to the pages with the year you want (a few test pages, then the run of that year), waiting a
# second and a half between pages. If the site will not sort by year, it reads every page instead (about 1,430 pages: half an hour or more).
YEAR = 1948
BASE = 'https://pier21.ca/immigration-records/ship-arrival-database'
DELAY = 1.5

import csv, html.parser, os, re, time, urllib.parse, urllib.request

class Rows(html.parser.HTMLParser):
    def __init__(self):
        super().__init__(); self.rows, self.head, self.row, self.cell, self.in_cell, self.is_th = [], [], None, [], False, False
    def handle_starttag(self, tag, attrs):
        if tag == 'tr': self.row = []
        elif tag in ('td', 'th') and self.row is not None: self.in_cell, self.is_th, self.cell = True, tag == 'th', []
    def handle_endtag(self, tag):
        if tag in ('td', 'th') and self.in_cell: self.row.append((' '.join(''.join(self.cell).split()), self.is_th)); self.in_cell = False
        elif tag == 'tr' and self.row is not None:
            if self.row:
                if all(th for _, th in self.row): self.head = [t for t, _ in self.row]
                else: self.rows.append([t for t, _ in self.row])
            self.row = None
    def handle_data(self, data):
        if self.in_cell: self.cell.append(data)

_cache = {}
def page(n, sort=True):
    """(header, rows) of page n (0 = the first page)"""
    key = (n, sort)
    if key in _cache: return _cache[key]
    q = {'page': n}
    if sort: q.update(order='field_year', sort='asc')
    url = BASE + '?' + urllib.parse.urlencode(q)
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (personal research: ship arrivals)'})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=60) as r: text = r.read().decode('utf-8', 'replace')
            break
        except Exception as e:
            print(f'  page {n + 1}: {e}; trying again'); time.sleep(5)
    else: raise RuntimeError(f'could not read page {n + 1}')
    time.sleep(DELAY)
    p = Rows(); p.feed(text)
    _cache[key] = (p.head, p.rows)
    return _cache[key]

def years(head, rows):
    yi = next((i for i, h in enumerate(head) if 'year' in h.lower()), None)
    out = []
    for r in rows:
        txt = r[yi] if yi is not None and yi < len(r) else ' '.join(r)
        m = re.search(r'\b(19[0-9]{2})\b', txt); out.append(int(m.group(1)) if m else None)
    return out

head, rows = page(0)
if not rows: raise RuntimeError('No table found on the first page: the site may have changed. Tell Claude.')
print('columns:', head)

# does sorting by year work? the first page and a page well in should be in order
_, r50 = page(50)
y0, y50 = [y for y in years(head, rows) if y], [y for y in years(head, r50) if y]
sorted_ok = y0 and y50 and max(y0) <= min(y50)
found = []
if sorted_ok:
    print('the list sorts by year: looking for', YEAR)
    lo, hi = 0, 1
    while True:                                    # find a page past the year
        ys = [y for y in years(head, page(hi)[1]) if y]
        if not ys or min(ys) > YEAR: break
        lo, hi = hi, hi * 2
    while hi - lo > 1:                             # the first page whose last year is YEAR or later
        mid = (lo + hi) // 2
        ys = [y for y in years(head, page(mid)[1]) if y]
        if ys and max(ys) < YEAR: lo = mid
        else: hi = mid
    n = lo
    while True:
        h, rs = page(n)
        if not rs: break
        ys = years(head, rs)
        mine = [[n + 1] + r for r, y in zip(rs, ys) if y == YEAR]
        found += mine
        print(f'page {n + 1}: {len(mine)} of {len(rs)} rows are {YEAR} ({len(found)} in all)')
        if ys and all(y and y > YEAR for y in ys): break
        n += 1
else:
    print('the list will not sort by year: reading every page (this takes a while)')
    n, last = 0, None
    while True:
        h, rs = page(n, sort=False)
        if not rs or rs == last: break
        last = rs
        mine = [[n + 1] + r for r, y in zip(rs, years(head, rs)) if y == YEAR]
        found += mine
        if mine or n % 25 == 0: print(f'page {n + 1}: {len(mine)} rows are {YEAR} ({len(found)} in all)')
        n += 1

out = os.path.join(os.path.expanduser('~'), f'pier21_arrivals_{YEAR}.csv')
with open(out, 'w', newline='', encoding='utf-8') as fh:
    w = csv.writer(fh); w.writerow(['page'] + head); w.writerows(found)
print(f'{len(found)} arrivals in {YEAR} saved to {out}')
