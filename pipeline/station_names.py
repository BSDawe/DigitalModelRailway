"""Station names by zoom, and who owns a station (Brendan, 22 Nov 2026). Applied at assembly, after names.py.

Every station gets three names:
  city   the place, shown on the map when zoomed out (one label per city): "Montreal", "Toronto", "Vancouver".
  zname  the station, shown on the map when zoomed in: a station with a 1948 name is that name ("Windsor Station", "Union Station", "Grand Central Terminal",
         "North Western Terminal"; a street name alone: "Park Avenue", "125th Street", "James Street Station"); a station with no particular name in a place with more than one
         station is "Town (RR)" ("Vancouver (CPR)", "Vancouver (CN)", "Alliston (CN)"); a place with one station keeps its own name.
  name   the full name for panels, boards, search and the GTFS feed: zname, with ", city" added when zname does not already say where it is ("Union Station, Toronto").
Names that are places in their own right (West Toronto, Montreal Nord, Montreal West, North Edmonton) stay as they are. Alternative names in brackets
(St. Annes (Ste. Anne de Bellevue)), ferry slips, steamer landings and the interurban stop numbers are not station designators and are left alone.

Owner: the railway whose track is under the station (Brendan: "assume that the line under the station is the owner"; New York Penn Station: PRR). Joint terminal
companies' track (own 'union') gives the union-station owner; who actually owned each union station is still to check (TODO). 'served' lists the railways whose trains
call. No colour on main-line station markers (Brendan, 22 Nov 2026).

CPR (Brendan, 22 Nov 2026): the period abbreviation for the Canadian Pacific is CPR, everywhere the railway is abbreviated; CN stays CN."""
import math, re
from collections import Counter, defaultdict

# 1948 names of named stations (gid -> (zoomed-in name, city)); Brendan's list of 22 Nov 2026 and the terminals already on the map
NAMED = {
    'CN_PORTLAND_ME': ('Portland (Grand Trunk)', 'Portland'),   # Brendan, 23 Nov 2026
    'MEC_PORTLAND_UNION_ME': ('Union Station', 'Portland'),   # Portland, Maine (Brendan's point; V213)
    'NYC_UTICA_N_Y': ('Union Station', 'Utica'),   # N.Y.C., tenants D.L.&W. and N.Y.O.&W. (Brendan, 22 Nov 2026)
    'NYC_CHICAGO_CENTRAL_ILL': ('Central Station', 'Chicago'), 'NYC_CHICAGO_LA_SALLE_STREET_ILL': ('La Salle Street Station', 'Chicago'),   # V210 (Brendan, 22 Nov 2026)
    'NYC_DETROIT_MICH': ('Michigan Central Station', 'Detroit'), 'NYC_BUFFALO_CENTRAL_TERMINAL_N_Y': ('Central Terminal', 'Buffalo'), 'NYC_BUFFALO_TERRACE_STA_N_Y': ('Terrace Station', 'Buffalo'),
    'CP_MONTREAL_WINDSOR': ('Windsor Station', 'Montreal'), 'CN_MONTREAL_CENTRAL': ('Central Station', 'Montreal'),
    'CN_MONTREAL_BONAVENTURE': ('Bonaventure Station', 'Montreal'), 'CN_BONAVENTURE': ('Bonaventure Station', 'Montreal'),
    'CP_MONTREAL_PLACE_VIGER': ('Place Viger Station', 'Montreal'), 'CP_MONTREAL_PARK_AVENUE': ('Park Avenue', 'Montreal'),
    'MSC_MONTREAL': ('Montreal (M&SC)', 'Montreal'),
    'TORONTO_UNION': ('Union Station', 'Toronto'), 'OTTAWA_UNION': ('Union Station', 'Ottawa'), 'CN_OTTAWA_BANK_STREET': ('Bank Street', 'Ottawa'),
    'NYC_OTTAWA_N_Y_C': ('Ottawa (NYC)', 'Ottawa'),
    'CN_QUEBEC_PALAIS': ('Palais Station', 'Quebec'), 'QRL_QUEBEC_ST_PAUL_STREET': ('St. Paul Street', 'Quebec'),
    'CN_NEW_YORK_GRAND_CENTRAL_N_Y': ('Grand Central Terminal', 'New York'), 'CN_NEW_YORK_PENNSYLVANIA_N_Y': ('Pennsylvania Station', 'New York'),
    'DH_NEW_YORK_125TH_STREET_N_Y': ('125th Street', 'New York'),
    'CN_CHICAGO_DEARBORN_ILL': ('Dearborn Station', 'Chicago'), 'CP_CHICAGO_GRAND_CENTRAL_ILL': ('Grand Central Station', 'Chicago'),
    'CP_CHICAGO': ('North Western Terminal', 'Chicago'),
    'CN_WASHINGTON_UNION_D_C': ('Union Station', 'Washington'), 'CP_BOSTON_NORTH': ('North Station', 'Boston'),
    'CN_DETROIT_BRUSH_STREET': ('Brush Street', 'Detroit'),
    'GN_SEATTLE': ('King Street Station', 'Seattle'), 'WA_SEATTLE_UNION_STATION': ('Union Station', 'Seattle'),
    'WA_SPOKANE_UNION_STATION': ('Union Station', 'Spokane'), 'WA_TACOMA_UNION_STATION': ('Union Station', 'Tacoma'),
    'WA_TACOMA_MILW_STATION': ('Tacoma (Milwaukee)', 'Tacoma'),
    'CN_WINNIPEG': ('Union Station', 'Winnipeg'),
    'CN_DULUTH': ('Union Depot', 'Duluth'), 'CP_DULUTH_MINN': ('Duluth (Soo Line)', 'Duluth'),
    'CP_ST_PAUL': ('Union Depot', 'St. Paul'),
    'CP_MINNEAPOLIS': ('Minneapolis (Milwaukee)', 'Minneapolis'), 'GN_MINNEAPOLIS': ('Great Northern Station', 'Minneapolis'),
    'DH_TROY_N_Y': ('Union Station', 'Troy'), 'DH_ALBANY_N_Y': ('Union Station', 'Albany'),
    'CN_BUFFALO_LEHIGH_VALLEY_N_Y': ('Buffalo (LV)', 'Buffalo'),
    'CN_NIAGARA_FALLS': ('Niagara Falls, ON (CN)', 'Niagara Falls, ON'), 'NYC_NIAGARA_FALLS': ('Niagara Falls, ON (NYC)', 'Niagara Falls, ON'),
    'CN_NIAGARA_FALLS_N_Y': ('Niagara Falls, NY', 'Niagara Falls, NY'),
    'CN_HAMILTON_JAMES_ST': ('James Street Station', 'Hamilton'),
    'CP_FREDERICTON': ('Union Station', 'Fredericton'),
    'CN_SAINT_JOHN': ('Union Station', 'Saint John'),                 # CN and CPR (Brendan, 22 Nov 2026)
    'S00': ('Carrall Street', 'Vancouver'),
}
BY_NAME = {'Davie Street': ('Davie Street', 'Vancouver'), 'Vancouver': ('Carrall Street', 'Vancouver')}   # gid-less: the B.C. Electric     # B.C. Electric stations without ids on the page
# railway abbreviations, by the label of the line that owns the track (CPR subsidiaries keep their own) and then by track owner
ABBR_LABEL = {'Canadian Pacific': 'CPR', 'Soo Line': 'Soo Line', 'Duluth, South Shore & Atlantic': 'DSS&A', 'Esquimalt & Nanaimo': 'E&N', 'Quebec Central': 'QC',
              'Dominion Atlantic': 'DAR', 'Spokane International': 'SI', 'Central Vermont': 'CV', 'Grand Trunk Western': 'GTW', 'Canadian National': 'CN'}
ABBR_OWN = {'ic': 'IC', 'cp': 'CPR', 'cn': 'CN', 'gn': 'GN', 'np': 'NP', 'milw': 'Milwaukee', 'up': 'UP', 'sps': 'SP&S', 'nyc': 'NYC', 'dh': 'D&H', 'rut': 'Rutland', 'bm': 'B&M',
            'nh': 'New Haven', 'prr': 'PRR', 'bo': 'B&O', 'lv': 'LV', 'thb': 'TH&B', 'onr': 'ONR', 'nar': 'NAR', 'pge': 'PGE', 'msc': 'M&SC', 'grr': 'GRR', 'len': 'L&N',
            'lps': 'L&PS', 'nst': 'NS&T', 'qrl': 'QRL&P', 'tem': 'Temiscouata', 'si': 'SI', 'acr': 'ACR', 'snl': 'S&L', 'cnw': 'C&NW', 'wpy': 'WP&Y', 'arr': 'Alaska RR',
            'mec': 'MEC', 'cwi': 'C&WI', 'nfr': 'Nfld. Ry.', 'aj': 'Algoma Jct.', 'cgt': 'CGT', 'crc': 'CR&C', 'mcrp': 'MCR&P', 'rs': 'Roberval & Saguenay', 'tir': 'TIR',
            'gwwd': 'GWWD', 'bc': 'B&C', 'union': 'Union', 'bcer': 'BCER'}
OWNER_NAME = {'IC': 'Illinois Central', 'MEC': 'Maine Central', 'CPR': 'Canadian Pacific Railway', 'CN': 'Canadian National', 'GN': 'Great Northern', 'NP': 'Northern Pacific', 'Milwaukee': 'Milwaukee Road',
              'UP': 'Union Pacific', 'SP&S': 'Spokane, Portland & Seattle', 'NYC': 'New York Central', 'D&H': 'Delaware & Hudson', 'Rutland': 'Rutland Railroad',
              'B&M': 'Boston & Maine', 'New Haven': 'New York, New Haven & Hartford', 'PRR': 'Pennsylvania Railroad', 'B&O': 'Baltimore & Ohio', 'LV': 'Lehigh Valley',
              'TH&B': 'Toronto, Hamilton & Buffalo', 'ONR': 'Ontario Northland', 'NAR': 'Northern Alberta Railways', 'PGE': 'Pacific Great Eastern', 'Union': 'a joint terminal company',
              'Soo Line': 'Soo Line', 'DSS&A': 'Duluth, South Shore & Atlantic', 'E&N': 'Esquimalt & Nanaimo', 'QC': 'Quebec Central', 'DAR': 'Dominion Atlantic',
              'CV': 'Central Vermont', 'GTW': 'Grand Trunk Western', 'C&NW': 'Chicago & North Western', 'C&WI': 'Chicago & Western Indiana'}
TAG = re.compile(r',\s*(Vt|N\.\s?H|Me|Mass|Mich|N\.\s?Y|Conn|R\.\s?I|Ont|Que|N\.\s?B|N\.\s?S|Man|Sask|Alta|B\.\s?C|Wis|Minn|Ind|Ill|Ohio|Pa|Wash|Ore|Mont|Idaho|N\.\s?D|Alaska|D\.\s?C)\.?$')
STREET = re.compile(r'\b(St\.|Street|Avenue|Ave\.|Road|Rd\.)$')
def cpr(s):    # the Canadian Pacific's period abbreviation
    if not isinstance(s, str): return s
    s = re.sub(r'\(C\.P\.R?\.\)', '(CPR)', s); s = re.sub(r'\bC\.P\.R\.(?= Station| station)', 'CPR', s)
    return re.sub(r'\bCP\b(?!_)', 'CPR', s)
def tagless(n): return TAG.sub('', n)
def base(n): return tagless(n).split(' (')[0].strip()
OWNER_FIX = {'MEC_LAWRENCE_MASS': 'B&M', 'MEC_HAVERHILL_MASS': 'B&M', 'NYC_CHICAGO_CENTRAL_ILL': 'IC'}   # Illinois Central property, the Michigan Central by trackage rights (Brendan, 22 Nov 2026); its approach is a dashed estimate
def owner_at(L, chain):
    for s in L.get('segments', []):
        if s['a'] - 1 <= chain <= s['b'] + 1 and s.get('owner') not in (None, 'none'): return s['owner']
    return L.get('owner') if L.get('owner') not in (None, 'none') else None
def apply(viz, gt):
    lines = [L for L in viz['lines']]
    owners, labels, served, pos, names_of = defaultdict(Counter), defaultdict(Counter), defaultdict(set), {}, {}
    for L in lines:
        for s in L['stations']:
            g = s.get('gid') or ('NAME:' + s['name'])
            o = owner_at(L, s.get('chain', 0))
            if o: owners[g][o] += 1; labels[g][(o, L.get('label', ''))] += 1
            served[g].add(ABBR_LABEL.get(L.get('label', ''), ABBR_OWN.get(L.get('owner') or '', L.get('label', ''))))
            pos.setdefault(g, (s['lon'], s['lat'])); names_of.setdefault(g, s['name'])
    def abbr(g):
        if g in OWNER_FIX: return OWNER_FIX[g]
        if not owners[g]: return None
        o = owners[g].most_common(1)[0][0]
        lab = max((n, l) for (oo, l), n in labels[g].items() if oo == o)[1]
        return ABBR_LABEL.get(lab) if o in ('cp', 'cn') and lab in ABBR_LABEL else ABBR_OWN.get(o, o.upper())
    # places with more than one station: same base name within 25 km, different ids (steam railways only; landings and the B.C. Electric keep their names)
    km = lambda a, b: math.hypot((a[0] - b[0]) * 111.3 * math.cos(math.radians(a[1])), (a[1] - b[1]) * 111.0)
    water = {s.get('gid') for L in lines if L.get('water') or L.get('kind') in ('v', 'O') for s in L['stations']}
    groups = defaultdict(list)
    for g, n in names_of.items():
        if g in water or g.startswith('NAME:'): continue
        groups[base(n)].append(g)
    multi = set()
    for b, gs in groups.items():
        for g in gs:
            if any(h != g and km(pos[g], pos[h]) < 25 for h in gs): multi.add(g)
    out = {}
    for g, n in names_of.items():
        n0 = cpr(n)
        if g in NAMED: z, c = NAMED[g]
        elif g.startswith('NAME:') and n in BY_NAME: z, c = BY_NAME[n]
        elif g in water: z, c = n0, base(n0)
        elif g in multi:
            b = base(n0); inner = re.search(r'\((.*)\)', tagless(n0))
            if inner and STREET.search(inner.group(1)): z = re.sub(r'\bSt\.$', 'Street', re.sub(r'\bAve\.$', 'Avenue', inner.group(1)))
            elif inner and inner.group(1) in ('CPR', 'C.N. Station', 'C.N.', 'N.Y.C. Station'): z = f"{b} ({'CN' if 'C.N' in inner.group(1) else 'NYC' if 'N.Y.C' in inner.group(1) else 'CPR'})"
            elif inner: z = tagless(n0)                     # other designators (Lower Station, North Sta., ferry): as printed
            else:
                a = abbr(g); z = f'{b} ({a})' if a else tagless(n0)
            c = b
        else: z, c = n0, base(n0)
        full = z if (c in z or z == c) else f'{z}, {c}'
        o = abbr(g)
        out[g] = dict(zname=z, city=c, name=full, owner=o, served=sorted(x for x in served[g] if x))
    # one 'Town (RR)' per railway: if two stations of one place come out the same, keep their printed names
    seen = defaultdict(list)
    for g, d in out.items():
        if g in multi and g not in NAMED: seen[(d['zname'], d['city'])].append(g)
    for k, gs in seen.items():
        if len(gs) > 1:
            for g in gs:
                if any(km(pos[g], pos[h]) < 25 for h in gs if h != g):
                    z = tagless(cpr(names_of[g])); out[g].update(zname=z, name=z if out[g]['city'] in z else f"{z}, {out[g]['city']}")
    n = 0
    for L in lines:
        for k in ('label', 'long', 'short', 'src'):
            if isinstance(L.get(k), str): L[k] = cpr(L[k])
        for t in L.get('trips', []):
            for k in ('note', 'name'):
                if isinstance(t.get(k), str): t[k] = cpr(t[k])
        for s in L['stations']:
            d = out.get(s.get('gid') or ('NAME:' + s['name']))
            if not d: continue
            keep = s['name']; s.update(name=d['name'], zname=d['zname'], city=d['city']); n += keep != d['name']
            if d['owner'] and s.get('gid') not in water and not s.get('gid', '').startswith('PORT_'):
                on = OWNER_NAME.get(d['owner'], d['owner']); others = [x for x in d['served'] if x != d['owner']]
                old = s.get('note') or ''
                old = re.sub(r"^(Canadian National|Canadian Pacific|Ontario Northland|Delaware & Hudson|New York Central|Rutland|Soo Line|Great Northern|Northern Pacific|[A-Z][\w&.' -]{0,40}) station[;.,]?\s*", '', old)   # the default "<railway> station"
                s['note'] = f"{on} station" + (f"; also served by {', '.join(others)}" if others else '') + (f". {old}" if old else '')
    for s in viz.get('stations', []):                    # the Chilliwack line's base data (B.C. Electric): the Vancouver terminal is Carrall Street
        if s.get('id') == 'S00': s.update(name='Carrall Street, Vancouver', zname='Carrall Street', city='Vancouver')
        else: s.setdefault('zname', s['name']); s.setdefault('city', s['name'])
    for s in viz.get('bl', {}).get('stations', []):       # the Burnaby Lake line starts at the same terminal
        if s.get('name') == 'Vancouver': s.update(name='Carrall Street, Vancouver', zname='Carrall Street', city='Vancouver')
    if 'stops.txt' in gt:
        rows = gt['stops.txt']; outr = [rows[0]]
        import csv, io
        for l in rows[1:]:
            r = next(csv.reader([l])); d = out.get(r[0])
            if r[0] == 'S00': d = dict(name='Carrall Street, Vancouver', owner=None)
            if d:
                r[1] = d['name']
                if d['owner'] and len(r) > 4 and not r[0].startswith('PORT_') and r[0] not in water:
                    on = OWNER_NAME.get(d['owner'], d['owner']); others = [OWNER_NAME.get(x, x) for x in d.get('served', []) if x != d['owner']]
                    rest = r[4]
                    while True:                              # drop the old "<railway> station" / "<railway> trains" lead-ins
                        m = re.match(r"^[A-Z][\w&.',() -]{0,60}:? (station|trains)(; also served by [^;.]*)?[;.,]?\s*", rest)
                        if not m: break
                        rest = rest[m.end():]
                    r[4] = f"{on} station" + (f"; also served by {', '.join(others)}" if others else '') + (f"; {rest}" if rest else '')
            b = io.StringIO(); csv.writer(b, lineterminator='\n').writerow(r); outr.append(b.getvalue())
        gt['stops.txt'] = outr
    return n
