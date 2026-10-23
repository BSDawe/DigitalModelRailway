"""Washington (and the Oregon lines of trains that enter Washington): the traced track, by railway, as it stood in 1948. A helper.
Sources (Brendan, October 2026): Mississippi Rails KMLs by Tony Howe and David Price (traces/washington/Washington State/*.kmz) and
Brendan's Oregon-Washington RR & Navigation file (traces/washington/Oregon-Washington_RR_Navigation_Co.kmz). Each line's description gives
when it was built and abandoned: track built after 1948 or abandoned in or before 1948 is left out."""
import json, os, re, zipfile
import xml.etree.ElementTree as ET
HERE = os.path.dirname(os.path.abspath(__file__)); NS = '{http://www.opengis.net/kml/2.2}'
FILES = ['traces/washington/Washington State/Washington State Map 6-3-2018.kmz', 'traces/washington/Oregon-Washington_RR_Navigation_Co.kmz']
RAIL = [('Northern Pacific', 'np'), ('Great Northern', 'gn'), ('Spokane_Portland', 'sps'), ('Spokane Portland', 'sps'), ('Union Pacific', 'up'),
        ('Oregon-Washington', 'up'), ('Oregon RR', 'up'), ('Milwaukee', 'milw'), ('Spokane International', 'si'), ('Camas Prairie', 'cprr')]
YEAR = r'(18[5-9]\d|19\d\d|20\d\d)'
def dates(desc):
    built = aband = None
    for ln in desc.splitlines():
        ys = [int(y) for y in re.findall(YEAR, ln)]
        if not ys: continue
        l = ln.lower()
        if re.search(r'aband|removed|taken up', l): aband = min(ys) if aband is None else min(aband, min(ys))
        elif re.search(r'built|constr|opened|completed|started', l) and built is None: built = min(ys)
    return built, aband
def features():
    out = []
    for fn in FILES:
        z = zipfile.ZipFile(os.path.join(HERE, fn)); root = ET.fromstring(z.read([n for n in z.namelist() if n.endswith('.kml')][0]))
        def walk(el, path):
            for ch in el:
                tag = ch.tag.replace(NS, '')
                if tag in ('Folder', 'Document'): n = ch.find(NS + 'name'); walk(ch, path + [n.text if n is not None else ''])
                elif tag == 'Placemark':
                    n = ch.find(NS + 'name'); d = ch.find(NS + 'description'); desc = (d.text or '') if d is not None else ''
                    p = ' / '.join(path); rail = next((r for k, r in RAIL if k in p), 'short')
                    if 'SP&S side' in (n.text if n is not None else ''): rail = 'sps'       # Brendan's connector into Portland Union Station, used by the SP&S, NP and GN
                    b, a = dates(desc)
                    for c in ch.iter(NS + 'coordinates'):
                        pts = [tuple(map(float, t.split(',')[:2])) for t in c.text.split()]
                        if len(pts) > 1: out.append(dict(file=os.path.basename(fn), path=p, rail=rail, name=n.text if n is not None else '', built=b, aband=a,
                                                         rights='Trackage Rights' in p or 'trackage rights' in p, coords=pts))
        walk(root, [])
    return out
def in_1948(f):
    if re.search(r'\bold\b', f['name'] or '', re.I): return False         # "old alignment", "Old Cascade Tunnel" (a line named "... abandoned" is abandoned today, not necessarily by 1948)
    return not ((f['built'] and f['built'] > 1948) or (f['aband'] and f['aband'] <= 1948))
if __name__ == '__main__':
    F = features()
    print(len(F), 'lines;', sum(in_1948(f) for f in F), 'in 1948')
    for f in F:
        if not in_1948(f): print('  out:', f['rail'], f['name'], 'built', f['built'], 'abandoned', f['aband'])
