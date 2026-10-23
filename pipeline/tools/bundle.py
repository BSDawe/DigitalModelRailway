"""Make the project bundles a fresh chat starts from (see STATE.md).
  bcer_project.zip   scripts, tables, traces, parts, template, STATE.md: enough to assemble the page and to re-run the light steps
  bcer_inputs.zip    the heavy inputs (national network extracts, the water layer): needed only to re-run the steps that read them
Unzip both into the same folder. Left out because they are rebuilt or not needed: gtfs/, viz_data.json, the page, site/, logs, screenshots,
old script versions, and the 157 MB national KML (nrwn/doc.kml)."""
import os, re, zipfile
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(HERE)
DROP = re.compile(r'(^|/)(__pycache__|gtfs|site|build_logs|images|out)/|\.png$|_v\d+\.|^viz_data\.json$|^fraser_valley_1949\.html$|\.zip$|^nrwn/(doc\.kml|nrwn\.kmz|region_old\.json)$|^steamer_build\.py$|^water\.json$|\.kmz$')
HEAVY = re.compile(r'^nrwn/.*\.json$|^water_union\.pkl$|\.gpkg$|\.kmz$')
LIGHT_NRWN = {'nrwn/wpy.json', 'nrwn/wpy_yt.json'}
files = sorted(os.path.relpath(os.path.join(d, f), HERE) for d, _, fs in os.walk(HERE) for f in fs)
KEEP = {'traces/washington/Washington State/Washington State Map 6-3-2018.kmz', 'traces/washington/Oregon-Washington_RR_Navigation_Co.kmz'}   # wa_tracks reads these
files = [f for f in files if (f in KEEP or not DROP.search(f)) and not f.startswith('.')]
sets = {'bcer_project.zip': [f for f in files if not HEAVY.search(f) or f in LIGHT_NRWN], 'bcer_inputs.zip': [f for f in files if HEAVY.search(f) and f not in LIGHT_NRWN]}
for name, fs in sets.items():
    with zipfile.ZipFile(name, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for f in fs: z.write(f)
    print(f'{name}: {len(fs)} files, {os.path.getsize(name) / 1e6:.1f} MB')
