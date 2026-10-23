"""Main-line traces from Brendan's KVR Trails KML (kvr_trails.kml), organised by rail trail. Only the railbed main lines are used:
bypasses (golden yellow), 'Title' guide lines, sidings, wyes and mine spurs are skipped. Returns UTM LineStrings keyed by name."""
import os, math, xml.etree.ElementTree as ET
from nrwn_graph import fwd
HERE = os.path.dirname(os.path.abspath(__file__))
NS = '{http://www.opengis.net/kml/2.2}'
MAIN = {('KVR/Coquihalla Sub', 'Coquihalla Sub'), ('KVR/Princeton Sub', 'Princeton Sub'), ('KVR/Carmi', 'Carmi2'), ('KVR/Carmi', 'Carmi'),
        ('C&W', 'C&W'), ('KVR/Merritt Sub', 'Merritt Sub'), ('C&KR', 'C&K'), ('N&SR', 'N&SR')}
def lines():
    out = {}
    def walk(el, path):
        for ch in el:
            if ch.tag in (NS + 'Folder', NS + 'Document'):
                nm = ch.find(NS + 'name'); walk(ch, path + [nm.text if nm is not None else '?'])
            elif ch.tag == NS + 'Placemark':
                nm = ch.find(NS + 'name'); key = ('/'.join(path[2:]), nm.text if nm is not None else '')
                ls = ch.find(f'.//{NS}LineString')
                if key in MAIN and ls is not None:
                    out[key[1]] = [fwd(*map(float, t.split(',')[:2])) for t in ls.find(NS + 'coordinates').text.split()]
    walk(ET.parse(os.path.join(HERE, 'kvr_trails.kml')).getroot(), [])
    return out
