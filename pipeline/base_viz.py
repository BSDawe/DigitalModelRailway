"""The Fraser Valley (Chilliwack) line as first built: its route, stations, trips and the map context, kept as base_viz.json because the script
that first made them was not kept. This step starts viz_data.json from it; every other step adds to that."""
import os, shutil
HERE = os.path.dirname(os.path.abspath(__file__))
shutil.copy(os.path.join(HERE, 'base_viz.json'), os.path.join(HERE, 'viz_data.json'))
print('base page data in place')
