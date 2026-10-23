import json, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from xml.etree import ElementTree as ET
geo=json.load(open('geometry.json')); m=json.load(open('model.json'))
ns={'k':'http://www.opengis.net/kml/2.2'};K='{http://www.opengis.net/kml/2.2}'
t=ET.parse(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'British_Columbia_Electric_Railway_Company.kml'))
bg=[]
for ls in t.iter(K+'LineString'):
    ce=ls.find('k:coordinates',ns)
    if ce is None or not ce.text: continue
    c=[tuple(map(float,x.split(',')[:2])) for x in ce.text.split()]
    if len(c)>1: bg.append(c)
fig,axs=plt.subplots(1,2,figsize=(16,7),gridspec_kw={'width_ratios':[1.6,1]})
for ax,(x0,x1,y0,y1) in ((axs[0],(-123.13,-121.93,48.98,49.30)),(axs[1],(-123.115,-122.90,49.19,49.29))):
    for c in bg:
        xs,ys=zip(*c); ax.plot(xs,ys,color='#cccccc',lw=0.6)
    xs,ys=zip(*geo['route']); ax.plot(xs,ys,color='#B5121B',lw=2)
    for s in m['stations']:
        x,y=s['lonlat']
        if x0<x<x1 and y0<y<y1:
            ax.plot(x,y,'o',ms=3.5,color='#1f3a93',zorder=5)
            if ax is axs[1] or s['tt_name'] in ('VANCOUVER','New Westminster','Cloverdale',"Hall's Prairie",'Langley Prairie','Sperling','Beaver River','Mt. Lehman','Abbotsford','Huntingdon','Yarrow','CHILLIWACK','Kidd','Arnold','Woodroofe'):
                ax.annotate(s['name'],(x,y),fontsize=7,xytext=(3,3),textcoords='offset points')
    ax.set_xlim(x0,x1); ax.set_ylim(y0,y1); ax.set_aspect(1/0.654)
    ax.set_xticks([]);ax.set_yticks([])
axs[0].set_title('Vancouver – Chilliwack route traced from your KML (red), timetable stations (blue)')
axs[1].set_title('Vancouver end: routed over KML street tracks to Central Park line')
plt.tight_layout(); plt.savefig('route_check.png',dpi=130)
