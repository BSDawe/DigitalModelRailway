#!/usr/bin/env python3
"""Link the private source files (raw third-party data, scans, big names files) into this pipeline folder.

The public repository holds the code, the timetable transcriptions, Brendan's own traces and the cut-down extracts the map is drawn from.
The raw files those came from live in the private repository BSDawe/DigitalModelRailway-sources, laid out with the same paths under
pipeline/. Without them the build still works: the steps that read them say "ok, inputs absent" and their saved parts are used.

  python3 tools/link_sources.py [path to the sources clone]      default: $DMR_SOURCES, else ../../DigitalModelRailway-sources

Each private file is symlinked into place (nothing is copied, so nothing private can be committed by mistake: .gitignore lists them too).
  python3 tools/link_sources.py --check     list the private paths and whether each is present here
"""
import os, sys
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRIVATE = os.path.join(HERE, 'tools', 'private_paths.txt')

def paths():
    return [l.strip() for l in open(PRIVATE) if l.strip() and not l.startswith('#')]

def main(argv):
    if '--check' in argv:
        for p in paths(): print(('present ' if os.path.exists(os.path.join(HERE, p)) else 'absent  ') + p)
        return
    args = [a for a in argv if not a.startswith('--')]
    src = args[0] if args else os.environ.get('DMR_SOURCES', os.path.join(HERE, '..', '..', 'DigitalModelRailway-sources'))
    src = os.path.abspath(os.path.join(src, 'pipeline') if os.path.isdir(os.path.join(src, 'pipeline')) else src)
    if not os.path.isdir(src): sys.exit(f'no sources folder at {src}')
    n = 0
    for p in paths():
        a, b = os.path.join(src, p.rstrip('/')), os.path.join(HERE, p.rstrip('/'))
        if not os.path.exists(a): print('not in sources:', p); continue
        if os.path.lexists(b): continue
        os.makedirs(os.path.dirname(b), exist_ok=True); os.symlink(a, b); n += 1
    print(f'linked {n} private paths from {src}')

if __name__ == '__main__': main(sys.argv[1:])
