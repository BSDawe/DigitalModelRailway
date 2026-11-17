"""Copy the Pier 21 ship arrival database (Canadian Museum of Immigration at Pier 21) into one CSV file, page by page.

Brendan, 17 Nov 2026: the 1948 arrivals run to 35 pages on the site. Run this on your own computer (the site cannot be read from Claude's workspace).

Usage
  1. In your browser, open the database, set the filter to 1948 (and anything else you want), and copy the address of the results page.
  2. Run:
        python3 pier21_arrivals.py "PASTE-THE-ADDRESS-HERE"
     It reads page 1, 2, 3 ... (the site's ?page=0, 1, 2 ...) until a page comes back empty or repeats the one before,
     waiting two seconds between pages, and writes pier21_arrivals.csv next to where you run it.
  Options:  --pages 35        stop after this many pages
            --out file.csv    a different output file
            --delay 2         seconds between pages

Needs only Python 3 (no extra packages). If the site changes its layout and nothing is found, the script saves the first page as
pier21_page0.html so it can be looked at."""
import argparse, csv, html.parser, sys, time, urllib.parse, urllib.request

class Rows(html.parser.HTMLParser):
    """Collects every table row: header cells (th) and data cells (td), as text."""
    def __init__(self):
        super().__init__(); self.rows, self.head, self.row, self.cell, self.in_cell, self.is_th = [], [], None, [], False, False
    def handle_starttag(self, tag, attrs):
        if tag == 'tr': self.row = []
        elif tag in ('td', 'th') and self.row is not None: self.in_cell, self.is_th, self.cell = True, tag == 'th', []
        elif tag == 'br' and self.in_cell: self.cell.append(' ')
    def handle_endtag(self, tag):
        if tag in ('td', 'th') and self.in_cell:
            self.row.append((' '.join(''.join(self.cell).split()), self.is_th)); self.in_cell = False
        elif tag == 'tr' and self.row is not None:
            if self.row:
                if all(th for _, th in self.row): self.head = [t for t, _ in self.row]
                else: self.rows.append([t for t, _ in self.row])
            self.row = None
    def handle_data(self, data):
        if self.in_cell: self.cell.append(data)

def page_url(url, n):
    u = urllib.parse.urlsplit(url); q = urllib.parse.parse_qsl(u.query, keep_blank_values=True)
    q = [(k, v) for k, v in q if k != 'page'] + [('page', str(n))]
    return urllib.parse.urlunsplit(u._replace(query=urllib.parse.urlencode(q)))

def fetch(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (personal research; ship arrivals 1948)'})
    with urllib.request.urlopen(req, timeout=60) as r: return r.read().decode('utf-8', 'replace')

def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('url'); ap.add_argument('--pages', type=int, default=200); ap.add_argument('--out', default='pier21_arrivals.csv')
    ap.add_argument('--delay', type=float, default=2.0)
    a = ap.parse_args()
    head, out, last = None, [], None
    for n in range(a.pages):
        url = page_url(a.url, n)
        try: text = fetch(url)
        except Exception as e: print(f'page {n + 1}: could not read ({e}); stopping'); break
        p = Rows(); p.feed(text)
        if n == 0 and not p.rows:
            open('pier21_page0.html', 'w', encoding='utf-8').write(text)
            sys.exit('No table rows found on the first page; saved it as pier21_page0.html. Send that file to Claude.')
        if not p.rows or p.rows == last: print(f'page {n + 1}: no new rows; done'); break
        head = head or p.head; last = p.rows
        out += [[n + 1] + r for r in p.rows]
        print(f'page {n + 1}: {len(p.rows)} rows ({len(out)} in all)')
        time.sleep(a.delay)
    with open(a.out, 'w', newline='', encoding='utf-8') as fh:
        w = csv.writer(fh); w.writerow(['page'] + (head or [])); w.writerows(out)
    print(f'wrote {len(out)} rows to {a.out}')

if __name__ == '__main__': main()
