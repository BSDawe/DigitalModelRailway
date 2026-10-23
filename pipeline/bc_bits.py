"""Brendan's 'BC Railway Bits' traces (bc_railway_bits.kml): K[name] = [(lon, lat), ...]."""
import os, re
HERE = os.path.dirname(os.path.abspath(__file__))
K = {}
for m in re.finditer(r'<Placemark>(.*?)</Placemark>', open(os.path.join(HERE, 'bc_railway_bits.kml')).read(), re.S):
    b = m.group(1)
    K[re.search(r'<name>(.*?)</name>', b).group(1)] = [tuple(map(float, p.split(',')[:2])) for p in re.search(r'<coordinates>(.*?)</coordinates>', b, re.S).group(1).split()]
