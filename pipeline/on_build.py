"""Ontario and Quebec, 1948 (Brendan, 23 October 2026): CP Tables 4, 58, 70, 75 and the boat trains 707/708 (CP timetable 1948); CN Tables 75 (east of
Armstrong) and 38 (Official Guide, April 25, 1948); the Ontario Northland (November 16, 1947) and the Algoma Central (April 25, 1948). Transcribed in
on_*.csv, times as printed (Eastern time), shown in Pacific time. One line for each file. Track and stations: on_lines.py (Delamere's collections).
New York Central and Delaware & Hudson trains of CP Table 18 to the border (on_nyc_t018.csv, on_dh_t018.csv).
Not built: on_soo_*.csv, on_dssa_*.csv, on_*full_*.csv and on_rut_*.csv (United States, no track yet) and the steamers in marine/ (no port positions yet)."""
import glob, os, re
import on_lines                                             # registers the railways, track graphs, places and the projection for this step
import ab_table, ab_lines
from ab_lines import build, trace, report
HERE = os.path.dirname(os.path.abspath(__file__))
TZ = ' Shown in Pacific time: three hours earlier than the Eastern time printed.'
TZA = ' Shown in Pacific time: four hours earlier than the Atlantic time printed.'
SRC = {'oncp': 'Canadian Pacific timetable, 1948', 'oncn': 'Official Guide, April 25, 1948', 'onr': 'Ontario Northland timetable, November 16, 1947',
       'acr': 'Algoma Central timetable, April 25, 1948', 'onnyc': 'Canadian Pacific timetable, 1948', 'ondh': 'Canadian Pacific timetable, 1948',
       'ontem': 'Official Guide, April 25, 1948', 'oncgt': 'Official Guide, April 1948', 'onrs': 'Official Guide, April 1948', 'onaj': 'Official Guide, March 1948', 'oncpcn': 'Canadian Pacific timetable, 1948', 'onnyco': 'Official Guide, April 25, 1948 (NYC Table 73; transcribed by Brendan)', 'onthb': 'Official Guide, April 25, 1948 (TH&B table) and Canadian Pacific timetable, 1948 (Table 56)', 'oncpthb': 'Canadian Pacific timetable, 1948', 'onlps': 'London & Port Stanley Railway timetable No. 76, May 21, 1947 (standing in for summer 1948)', 'ongrr': 'Canadian Pacific timetable, 1948 (Table 66) and Official Guide, 1948 (hourly service)', 'onlen': 'Canadian Pacific timetable, 1948', 'oncnfy': 'Official Guide, April 25, 1948 (CN Table 1, Quebec via ferry)'}
LONG = {'on_cp_t004': 'Montreal – Ottawa – North Bay – Sudbury – Fort William', 'on_cp_t058': 'Toronto – MacTier – Parry Sound – Sudbury (and Port McNicoll)',
        'on_cp_t058b': 'Ypres – Camp Borden', 'on_cp_t058p': 'Toronto – Medonte – Port McNicoll (boat trains)', 'on_cp_t070': 'Sudbury – Sault Ste. Marie', 'on_cp_t070b': 'Sudbury – McKerrow – Little Current',
        'on_cp_t075': 'Sudbury – Creighton', 'on_cp_t062': 'Toronto – Streetsville – Orangeville – Owen Sound', 'on_cp_t063': 'Cataract – Erin – Fergus – Elora (mixed)', 'on_cp_t064': 'Saugeen – Durham – Hanover – Walkerton (mixed)', 'on_cp_t065': 'Orangeville – Mount Forest – Wingham – Teeswater (mixed)', 'on_cp_t068': 'Hamilton – Guelph Jct. – Guelph – Goderich (motor trains)', 'on_cp_t069': 'Woodstock – Ingersoll – St. Thomas (mixed)', 'on_cp_t069b': 'Woodstock – Ingersoll – Tillsonburg – Port Burwell (mixed)', 'on_cp_t069a': 'Woodstock – Zorra – St. Marys (mixed)', 'on_cp_t073': 'Mattawa – Timiskaming – Kipawa – Ville Marie – Angliers',
        'on_cn_t075a': 'Montreal – Coteau – Ottawa', 'on_cn_t059': 'Montreal – St. Hyacinthe – Richmond – Sherbrooke – Coaticook', 'on_cn_t060a': 'Coteau – Valleyfield (motor trains)', 'on_cn_t064': 'Montreal – Joliette – Shawinigan Falls – Garneau – Hervey – Riviere a Pierre', 'on_cn_t064q': 'Garneau – St. Prosper – Quebec', 'on_cn_t065': 'Montreal – Sorel – Nicolet – Trois Rivieres (ferry)', 'on_cn_t066': 'Sorel – St. Hyacinthe', 'on_cn_t068': 'Montreal – St. Isidore Jn. – Huntingdon (to Fort Covington, N.Y.)', 'on_cn_t068h': 'St. Isidore Jn. – Hemmingford', 'on_cn_t070': 'Montreal – St. Jerome – Huberdeau – Lac Remi', 'on_cn_t072': 'Montreal – St. Johns – Farnham – Granby – Waterloo', 'on_cn_t061': 'Montreal (Bonaventure) – Lachine – Vaudreuil – Coteau (suburban)', 'on_cn_t061c': 'Montreal – Coteau (Toronto line trains)', 'on_cn_t063': 'Montreal – L\'Epiphanie – Rawdon', 'on_cn_t075b': 'Ottawa – Pembroke – North Bay – Capreol – Armstrong',
        'on_cn_t122': 'Toronto – Beaverton – Parry Sound – Sudbury Jct. – Capreol', 'on_cn_t122a': 'Toronto – Allandale – Orillia – Parry Sound – Capreol', 'on_cn_t126': 'Toronto – Allandale – Orillia – Huntsville – North Bay', 'on_cn_t126b': 'Toronto – Beaverton – Huntsville – North Bay', 'on_cn_t126m': 'Toronto – Allandale – Collingwood – Meaford', 'on_cn_t126d': 'Allandale – Barrie – Orillia – Midland', 'on_cn_t126p': 'Allandale – Penetang', 'on_cn_t126c': 'Allandale – Camp Borden', 'on_cn_t126g': 'Scotia – Joe Lake – Algonquin Park', 'on_onr_t001n': 'The Northland: Toronto – Beaverton – North Bay – Timmins', 'on_cn_t038q': 'Quebec – Garneau – Hervey', 'on_cn_t038m': 'Montreal – Hervey',
        'on_cn_t038h': 'Hervey – La Tuque – Senneterre – Taschereau – Cochrane', 'on_cn_t038n': "Senneterre – Val d'Or – Noranda",
        'on_cn_t038t': 'Taschereau – Noranda', 'on_onr_t001': 'Toronto – Allandale – North Bay – Porquis – Timmins', 'on_onr_t001c': 'Porquis – Cochrane',
        'on_onr_t018m': 'Cochrane – Moosonee', 'on_onr_t018s': 'Swastika – Kirkland Lake – Rouyn – Noranda',
        'on_cn_t108': 'Cochrane – Kapuskasing – Hearst – Nakina', 'on_onr_t108': 'Cochrane – Kapuskasing (The Northland, over the CN)', 'on_cn_t116': 'Longlac – Port Arthur – Fort William',
        'on_cp_t023': 'Montreal – Farnham – Foster – Magog – Sherbrooke', 'on_cp_t024': 'Montreal – Farnham – Sutton – Newport – Boston (on this map to the border)',
        'on_cp_t033': 'Montreal (Windsor Station) – Trois Rivières – Quebec', 'on_cp_t033v': 'Montreal (Place Viger) – Trois Rivières – Quebec',
        'on_cp_t035': 'Lanoraie – Joliette – St. Gabriel', 'on_cp_t036': "Trois Rivières – Shawinigan Falls – Grand'Mère", 'on_cp_t037': 'Trois Rivières – Grandes Piles',
        'on_cp_t042': 'Montreal (Place Viger) – St. Jérôme – Ste. Agathe – Labelle – Mont-Laurier', 'on_cp_t042w': 'Montreal (Windsor Station) – St. Jérôme – Ste. Agathe – Labelle – Mont-Laurier',
        'on_cp_t042s': 'Montreal (Place Viger) – Ste. Thérèse – St. Lin',
        'on_cp_t043': 'Montreal – Vaudreuil – Rigaud – Vankleek Hill – Ottawa (Short Line)', 'on_cp_t044': 'Montreal (Place Viger) – Lachute – Montebello – Hull – Ottawa',
        'on_cp_t044w': 'Montreal (Windsor Station) – Lachute – Montebello – Hull – Ottawa', 'on_cp_t044a': 'Ottawa – Kemptville – Bedell – Prescott',
        'on_cp_t044p': 'Ottawa – Kemptville – Bedell – Smiths Falls (pool trains)', 'on_cp_t045': 'Ottawa – Hull – Shawville – Waltham', 'on_cp_t045a': 'Renfrew – Eganville',
        'on_cp_t046': 'Ottawa – Hull – Wakefield – Maniwaki', 'on_cp_t047': 'Ottawa – Carleton Place – Smiths Falls – Brockville',
        'on_cp_t048': 'Ottawa – Carleton Place – Renfrew – Pembroke – Chalk River',
        'on_cp_t008': 'Quebec – Thetford Mines – Sherbrooke – Beebe (Quebec Central; to Newport, Vt.)', 'on_cp_t008l': 'Levis – Vallée Jct. – Thetford Mines – Sherbrooke (Quebec Central)',
        'on_cp_t008f': 'Vallée Jct. – St. Georges – Lac Frontière (Quebec Central)', 'on_cp_t008m': 'Tring Jct. – Megantic (Quebec Central)',
        'on_cp_t010': 'Sherbrooke – Cookshire – Megantic – Boundary (Montreal – Saint John)',
        'on_tem_t001': 'Rivière du Loup – Cabano – Notre Dame du Lac – Ste. Rose (to Edmundston, N.B.)', 'on_cgt_t001': 'Mont Joli – Métis Beach – Matane',
        'on_rs_t001': 'Arvida – Port Alfred – Bagotville', 'on_aj_t001': "Isle Maligne – St. Joseph d'Alma – Saguenay Power",
        'on_cp_t050': 'Montreal – Smiths Falls – Tichborne – Belleville – Toronto (Lake Ontario Shore Line)', 'on_cp_t050o': 'Ottawa – Smiths Falls – Belleville – Toronto (Pool 23 / 24)',
        'on_cpcn_t049': 'Montreal (Windsor Station) – Cornwall – Kingston – Toronto (Pool 15 / 6, over the CN)', 'on_cp_t049w': 'Toronto – Galt – London – Windsor (for Detroit and Chicago)',
        'on_cp_t051': 'Montreal – Smiths Falls – Sharbot Lake – Peterboro – Toronto', 'on_cp_t051o': 'Ottawa – Smiths Falls – Sharbot Lake – Peterboro – Toronto (Pool 33 / 34)',
        'on_cp_t052': 'De Beaujeu – Cornwall', 'on_cp_t053': 'Havelock – Peterboro – Lindsay – Bobcaygeon', 'on_cp_t055': 'Kingston – Tichborne – Sharbot Lake – Renfrew',
        'on_nyco_t073': 'Ottawa – Finch – Cornwall – Helena, N.Y.', 'on_dh_t018': 'Montreal – Rouses Point – Albany – New York (on this map to the border)', 'on_nyc_t018': 'Montreal – Malone – Albany – New York (on this map to the border)',
        'on_thb_t056': 'Hamilton – Smithville – Welland – Fort Erie (to Buffalo)', 'on_thb_t056w': 'Hamilton – Brantford – Waterford', 'on_cpthb_t056': 'Toronto – Sunnyside – Hamilton (over the CN Lake Shore)',
        'on_cn_t001': 'Matapedia – Mont Joli – Riviere du Loup – Levis – Drummondville – Montreal (Halifax trains)', 'on_cn_t001n': 'Nicolet – St. Leonard – St. Hyacinthe – Montreal',
        'on_cn_t001a': 'Matapedia – New Carlisle – Gaspe', 'on_cn_t023': 'Edmundston – Monk – Charny – Quebec (Quebec part)', 'on_cn_t054': 'Levis – Villeroy – Fortierville (mixed)',
        'on_cn_t050': 'Quebec – Riviere a Pierre – Chambord – Chicoutimi', 'on_cn_t050m': 'Montreal – Riviere a Pierre', 'on_cn_t053': 'Quebec – Ste. Anne de Beaupre – Murray Bay – La Malbaie',
        'on_cnfy_t001': 'Quebec – Levis ferry', 'on_cn_t051': 'Montreal – St. Johns – Cantic – Rouses Point (Rutland trains; to the border)', 'on_cn_t051v': 'Montreal – St. Johns – Cantic (Central Vermont trains; to the border)',
        'on_cn_t051i': 'Montreal – St. Johns – Iberville', 'on_cn_t052': 'Richmond – Victoriaville – Lyster – Quebec', 'on_cn_t055': 'Chambord – Roberval – St. Felicien – Dolbeau',
        'on_lps_t001': 'London – St. Thomas – Port Stanley – Beach (electric)', 'on_grr_t066k': 'Galt (C.P.R.) – Preston – Kitchener (connecting trains)', 'on_grr_t066h': 'Galt (C.P.R.) – Preston – Hespeler (connecting trains)',
        'on_grr_t000k': 'Galt – Preston – Kitchener (hourly)', 'on_grr_t000h': 'Galt – Preston – Hespeler (hourly)', 'on_len_t067': 'Galt – Paris – Brantford – Waterford – Simcoe – Port Dover',
        'on_acr_t001': 'Sault Ste. Marie – Hawk Junction – Hearst', 'on_acr_t001m': 'Hawk Junction – Michipicoten'}
OVER = {'on_cn_t075b': dict(noplace=['Ottawa (Bank Street)']),
        'on_cp_t058b': dict(places={'Camp Borden (Lower Station)': (-79.891308, 44.269889),      # Brendan, 23 Oct 2026: "about here"
                                    'Camp Borden (Upper Station)': (-79.886619, 44.286324)}),    # at the end of its spur (his trace)
        'on_cp_t024': dict(places={'International Boundary (CP, to North Troy, Vt.)': (-72.4121988, 45.0071654)}),   # end of CP track east of Highwater (through Richford, Vt. on Brendan's trace)
        'on_cp_t008': dict(places={'International Boundary (QC, to Newport, Vt.)': (-72.171437, 45.0058471)}),   # the end of the Massawippi Valley line in the Quebec collection
        'on_tem_t001': dict(shift=-14400),
        'on_nyco_t073': dict(force=[('Helena, N.Y.', 'Rooseveltown, N.Y.')], short='NYC (Table 73)'),   # printed 13 mi; Brendan's trace about 4.5
        'on_cp_t049w': dict(noplace=['London (Quebec St.)']),
        'on_cp_t050': dict(noplace=['Rosedale']), 'on_cp_t050o': dict(noplace=['Rosedale']),   # the collection's "Rosedale" found is Toronto's
        'on_rs_t001': dict(force=[('Port Alfred', 'Ruisseau Rouge')]),   # the collection's line climbs out of Port Alfred by a hairpin: 7.7 mi of track for 6.0 printed
        'on_lps_t001': dict(places={'London': (-81.2471692, 42.9804778), 'Stop 1 (Thompson Road)': (-81.226183, 42.9676451), 'Stop 2 (Commissioners Road)': (-81.2166137, 42.9589094), 'Stop 3 (Pond Mills)': (-81.1958412, 42.9459336), 'Stop 3½': (-81.1942799, 42.9366985), 'Westminster': (-81.1943079, 42.92809), 'Stop 5 (Brockley)': (-81.1942273, 42.9153002), 'Stop 6': (-81.1941616, 42.9030048), 'Stop 7': (-81.1940822, 42.8905455), 'Stop 8': (-81.1939783, 42.8784147), 'Glanworth': (-81.1936632, 42.8648842), 'Stop 10': (-81.1937007, 42.8543084), 'Stop 11': (-81.1937554, 42.8490088), 'Stop 12': (-81.193687, 42.8366917), 'Stop 13': (-81.1935421, 42.8244852), 'Yarmouth': (-81.1934957, 42.8122714), 'Stop 15 (Edgeware Road)': (-81.1929216, 42.7999407), 'C.N.R. - Wabash Depot': (-81.1899826, 42.7838356), 'St. Thomas (Talbot Street)': (-81.1908909, 42.7792999), 'N.Y.C. Depot': (-81.186814, 42.778033), 'Palm Street': (-81.1932986, 42.7697446), 'Stop 17': (-81.1939141, 42.7551396), 'Stop 18': (-81.1938202, 42.7496263), 'Crafts': (-81.1938338, 42.7410715), 'Stop 19': (-81.1950389, 42.7354793), 'Whites': (-81.2029961, 42.7215981), 'Stop 21 (Union)': (-81.2084271, 42.7052755), 'Stop 22': (-81.2122591, 42.6917531), 'Stop 23': (-81.2174173, 42.6750514), 'Port Stanley': (-81.2147116, 42.665073), 'Beach': (-81.2208832, 42.6615504)}, noplace=['Colborne Street', 'Philip Street', 'Elm Street']),   # the Canadian Electric Railway Mapping project's stops (Brendan, 28 Oct 2026); NYC Depot: Brendan's point; the three by mileage
        'on_cp_t073': dict(noplace=['Crest']),   # the collection's Crest point sits ~2 mi short of the printed mileage (Snake Creek - Crest 11.9 mi of track, 13.7 printed)
        'on_grr_t066k': dict(places={'Galt': (-80.310689, 43.35897), 'Galt (C.P.R.)': (-80.315596, 43.368087), 'Preston': (-80.366801, 43.40038), 'Hagey': (-80.373924, 43.411265), 'Freeport': (-80.415696, 43.424777), 'Centerville': (-80.43089, 43.42849), 'Kitchener Junction': (-80.466034, 43.439341), 'Kitchener (Queen Street)': (-80.495376, 43.443387), 'Joseph Street': (-80.358425, 43.402177), 'Pattison': (-80.357272, 43.403169), 'Idylwild': (-80.340174, 43.415547), 'Stop (Hespeler line)': (-80.318495, 43.4278), 'Hespeler': (-80.311377, 43.431744)}),
        'on_grr_t066h': dict(places={'Galt': (-80.310689, 43.35897), 'Galt (C.P.R.)': (-80.315596, 43.368087), 'Preston': (-80.366801, 43.40038), 'Hagey': (-80.373924, 43.411265), 'Freeport': (-80.415696, 43.424777), 'Centerville': (-80.43089, 43.42849), 'Kitchener Junction': (-80.466034, 43.439341), 'Kitchener (Queen Street)': (-80.495376, 43.443387), 'Joseph Street': (-80.358425, 43.402177), 'Pattison': (-80.357272, 43.403169), 'Idylwild': (-80.340174, 43.415547), 'Stop (Hespeler line)': (-80.318495, 43.4278), 'Hespeler': (-80.311377, 43.431744)}),
        'on_grr_t000k': dict(places={'Galt': (-80.310689, 43.35897), 'Galt (C.P.R.)': (-80.315596, 43.368087), 'Preston': (-80.366801, 43.40038), 'Hagey': (-80.373924, 43.411265), 'Freeport': (-80.415696, 43.424777), 'Centerville': (-80.43089, 43.42849), 'Kitchener Junction': (-80.466034, 43.439341), 'Kitchener (Queen Street)': (-80.495376, 43.443387), 'Joseph Street': (-80.358425, 43.402177), 'Pattison': (-80.357272, 43.403169), 'Idylwild': (-80.340174, 43.415547), 'Stop (Hespeler line)': (-80.318495, 43.4278), 'Hespeler': (-80.311377, 43.431744)}),
        'on_grr_t000h': dict(places={'Galt': (-80.310689, 43.35897), 'Galt (C.P.R.)': (-80.315596, 43.368087), 'Preston': (-80.366801, 43.40038), 'Hagey': (-80.373924, 43.411265), 'Freeport': (-80.415696, 43.424777), 'Centerville': (-80.43089, 43.42849), 'Kitchener Junction': (-80.466034, 43.439341), 'Kitchener (Queen Street)': (-80.495376, 43.443387), 'Joseph Street': (-80.358425, 43.402177), 'Pattison': (-80.357272, 43.403169), 'Idylwild': (-80.340174, 43.415547), 'Stop (Hespeler line)': (-80.318495, 43.4278), 'Hespeler': (-80.311377, 43.431744)}),
        'on_len_t067': dict(places={'Galt': (-80.310689, 43.35897), 'Concession Street': (-80.3131353, 43.3542228), 'Soapworks': (-80.3149879, 43.3443084), 'McPhearson': (-80.3144342, 43.3299517), 'River Bridge': (-80.3137878, 43.3243445), 'Carrick': (-80.3139523, 43.2958921), 'McRae': (-80.3182736, 43.2884828), 'Glen Morris': (-80.3463053, 43.2763106), 'Robertson': (-80.3504235, 43.2427293), 'Blue Lake': (-80.352029, 43.2222621), 'Braeside': (-80.3571379, 43.2115268), 'Paris': (-80.3760973, 43.1948104), 'Oak Park': (-80.3511278, 43.1746555), 'Stuart': (-80.335397, 43.1596303), 'Hardy Road': (-80.3132403, 43.162077), 'Golf Club': (-80.297592, 43.1590157), 'West Mill Street': (-80.2845841, 43.1420483), 'Brantford': (-80.2692124, 43.1377531), 'Mount Pleasant Road': (-80.2748907, 43.1251036), 'Wilsonville': (-80.3087221, 42.9970315), 'Fairchild': (-80.2929592, 43.1089575), 'Lundy Lane': (-80.3094119, 43.0934463), 'Mount Pleasant': (-80.3175678, 43.079324), 'Maple Grove': (-80.3259226, 43.0584391), 'Oakland': (-80.3216096, 43.0337218), 'Lutesville': (-80.3037284, 42.9730697), 'Dundurn': (-80.3029751, 42.9637801), 'Stop 7 (Round Plains)': (-80.3061173, 42.9458574), 'Bunker Hill': (-80.3054253, 42.9345707), 'Waterford': (-80.3040457, 42.9312801), 'Cherry Valley': (-80.2962727, 42.9104538), 'Bloomsburg': (-80.3066176, 42.8838839), 'Colborne': (-80.3087406, 42.8584508), 'Simcoe North': (-80.3041755, 42.8463873), 'Simcoe': (-80.2988671, 42.8341321), 'Lynn Valley': (-80.2898801, 42.8105876), 'Stickney': (-80.2750448, 42.8005119), 'Bowlby': (-80.2401752, 42.788992), 'Main Street (Port Dover)': (-80.2125354, 42.7929134), 'Port Dover': (-80.2054291, 42.7914869)}),   # the Canadian Electric Railway Mapping project's stations (Brendan, 29 Oct 2026)
        'on_cn_t001': dict(places={'Provincial boundary (N.B., Restigouche River)': (-66.93886, 47.97488)}),   # where the Intercolonial crosses the Restigouche at Matapedia (Natural Earth boundary)
        'on_cn_t051': dict(places={'International Boundary (to Rouses Point, N.Y.)': (-73.37095, 45.01038)}),   # the end of the collection's Rouses Point subdivision
        'on_cn_t051v': dict(places={'International Boundary (to East Alburgh, Vt.)': (-73.24128, 45.01255)}),   # the end of the Coteau & Province Line track east of Cantic
        'on_cn_t052': dict(places={'Richmond': (-72.1482, 45.6651)}),
        'on_cn_t061': dict(places={'Montreal (Bonaventure Station)': (-73.5648669, 45.4958626)}, noplace=['St. Dominique']), 'on_cn_t061c': dict(noplace=['St. Dominique']), 'on_cn_t075a': dict(noplace=['St. Dominique']),   # St. Dominique: the collection point snaps to the other track of the double main line   # the Grand Trunk's Bonaventure Station (collection point)
        'on_cn_t066': dict(places={'St. Hyacinthe': (-72.9609545, 45.6265834)}),   # the United Counties line's nearest point to St. Hyacinthe (the collection has no tie to the CN main line there): ASK Brendan
        'on_cn_t065': dict(places={'Trois Rivieres (Ferry)': (-72.518, 46.3364)}),   # the end of the collection's CN track on the south shore opposite Three Rivers
        'on_cn_t068': dict(places={'International Boundary (to Fort Covington, N.Y.)': (-74.48584, 44.9976)}),   # the end of the collection's United States & Canada Railroad track
        'on_cn_t072': dict(places={'Iberville (C.P.R.)': (-73.239757, 45.311701), 'Farnham': (-72.979017, 45.282024)}),   # the CP stations (Farnham Union Station)
        'on_cn_t059': dict(places={'Richmond': (-72.1482, 45.6651), 'International Boundary (to Norton, Vt.)': (-71.7951269, 45.010647)}),   # Richmond, Que.; the end of the collection's St. Lawrence & Atlantic track at Norton   # Richmond, Que. (the collection also has a Richmond near Ottawa)
        'on_cn_t023': dict(places={'Provincial boundary (N.B., Table 23)': (-68.7317, 47.372)}, noplace=['St. Anselme']),   # St. Anselme: the collection's point is the Quebec Central's   # the end of the Quebec collection's NTR track at the N.B. boundary
        'on_cnfy_t001': dict(places={'Quebec (Ferry Wharf)': (-71.20161491263052, 46.81183142623051)}, short='Quebec – Levis ferry'),   # Brendan, 24 Oct 2026
        'on_thb_t056': dict(places={'International Boundary (Niagara River, to Black Rock, N.Y.)': (-78.9040, 42.9300)}),   # mid-river on the International Railway Bridge (approximate)
        'on_cp_t022s': dict(places={'Stanbridge': (-73.0198692, 45.1161065)}),   # end of the 2.78 mi Stanbridge junction segment (Brendan, 24 Oct 2026)
        'on_cp_t070': dict(places={'Worthington': (-81.4516144, 46.3826754), 'Turbine': (-81.5119836, 46.3741679)}),
        'on_cp_t070b': dict(places={'Worthington': (-81.4516144, 46.3826754), 'Turbine': (-81.5119836, 46.3741679)})}   # on the Soo branch (the collection's
                                                                  # points snap to the parallel Algoma Eastern line, which does not join between them)   # Bank Street by its mileage from Union Station (canon names both 'ottawa')
def specs():
    out = []
    LATE = {'on_cp_t010.csv', 'on_cp_t049w.csv', 'on_cn_t001.csv', 'on_cn_t001a.csv', 'on_cn_t001n.csv', 'on_cn_t023.csv', 'on_cn_t050.csv', 'on_cn_t050m.csv', 'on_cn_t053.csv', 'on_cn_t054.csv', 'on_cn_t051.csv', 'on_cn_t051v.csv', 'on_cn_t051i.csv', 'on_cn_t052.csv', 'on_cn_t055.csv', 'on_cn_t059.csv', 'on_cn_t060a.csv', 'on_cn_t061.csv', 'on_cn_t061c.csv', 'on_cn_t063.csv', 'on_cn_t064.csv', 'on_cn_t064q.csv', 'on_cn_t065.csv', 'on_cn_t066.csv', 'on_cn_t068.csv', 'on_cn_t068h.csv', 'on_cn_t070.csv', 'on_cn_t072.csv'}   # the CN Quebec tables (29 Oct 2026) after the older files, so the older trains (CN 1 - 4, 11, 12, 38 ...) keep their trip ids                              # continuations of trains another table names first (Table 23's 39 - 42 keep their trip ids)
    for fn in sorted(glob.glob(os.path.join(HERE, 'on_c[pn]_t*.csv')) + glob.glob(os.path.join(HERE, 'on_onr_t*.csv')) + glob.glob(os.path.join(HERE, 'on_acr_t*.csv'))
                     + glob.glob(os.path.join(HERE, 'on_dh_t*.csv')) + glob.glob(os.path.join(HERE, 'on_nyc_t*.csv'))
                     + glob.glob(os.path.join(HERE, 'on_cpcn_t*.csv')) + glob.glob(os.path.join(HERE, 'on_nyco_t*.csv')) + glob.glob(os.path.join(HERE, 'on_thb_t*.csv')) + glob.glob(os.path.join(HERE, 'on_cpthb_t*.csv')) + glob.glob(os.path.join(HERE, 'on_lps_t*.csv')) + glob.glob(os.path.join(HERE, 'on_cnfy_t*.csv')) + glob.glob(os.path.join(HERE, 'on_grr_t*.csv')) + glob.glob(os.path.join(HERE, 'on_len_t*.csv'))
                     + [f for x in ('tem', 'cgt', 'rs', 'aj') for f in glob.glob(os.path.join(HERE, f'on_{x}_t*.csv'))], key=lambda f: (os.path.basename(f) in LATE, f)):
        stem = os.path.basename(fn)[:-4]; o = OVER.get(stem, {})
        if o.get('skip'): continue
        rail = {'cp': 'oncp', 'cn': 'oncn', 'onr': 'onr', 'acr': 'acr', 'dh': 'ondh', 'nyc': 'onnyc', 'tem': 'ontem', 'cgt': 'oncgt', 'rs': 'onrs', 'aj': 'onaj', 'cpcn': 'oncpcn', 'nyco': 'onnyco', 'thb': 'onthb', 'cpthb': 'oncpthb', 'lps': 'onlps', 'grr': 'ongrr', 'len': 'onlen', 'cnfy': 'oncnfy'}[re.match(r'on_(cpthb|thb|lps|grr|len|cnfy|cpcn|nyco|cp|cn|onr|acr|dh|nyc|tem|cgt|rs|aj)_', stem).group(1)]
        R = ab_table.load(fn)['rows']; a, b = R[0]['station'], R[-1]['station']
        table = re.match(r'on_\w+?_t(\d+)', stem).group(1).lstrip('0')
        rw = {'oncp': 'CP', 'oncn': 'CN', 'onr': 'ONR', 'acr': 'ACR', 'ondh': 'D&H', 'onnyc': 'NYC', 'ontem': 'TEM', 'oncgt': 'C&GT', 'onrs': 'R&S', 'onaj': 'A&J', 'oncpcn': 'CP', 'onnyco': 'NYC', 'onthb': 'TH&B', 'oncpthb': 'CP', 'onlps': 'L&PS', 'ongrr': 'GRR', 'onlen': 'L&N', 'oncnfy': 'Ferry'}[rail]
        short = o.get('short', f'{rw} Table {table}' if rail in ('oncp', 'oncn', 'oncpcn', 'onthb', 'oncpthb', 'ongrr', 'onlen') else f'{rw} (CP Table {table})' if rail in ('ondh', 'onnyc') else ab_lines.RAILS[rail]['label'])
        key = stem.replace('on_', 'on').replace('_t', '')
        out.append(dict(key=key, rail=rail, graph='sk:' + rail, legs=[dict(csv=os.path.basename(fn))], dirs=['to ' + b, 'to ' + a], short=short,
                        long=o.get('long', LONG.get(stem, f'{a} – {b}')), src=f'{short} ({SRC[rail]})', cols=o.get('cols'), shift=o.get('shift', -10800), tzrows=True, tznote=TZA if o.get('shift') == -14400 else TZ,
                        names={**{t['col']: t['name'] for t in ab_table.load(fn)['trains'] if t.get('name')}, **o.get('names', {})}, notes=o.get('notes', {}), via=o.get('via', ()), noplace=o.get('noplace', ()), force=o.get('force', ()), places=o.get('places'), ends=True, realends=True))
    return out
SPECS = specs()
on_lines.register([(s['rail'], s['legs'][0]['csv']) for s in SPECS])
if __name__ == '__main__':
    if os.environ.get('ON_DRY'):
        for s in SPECS:
            if os.environ['ON_DRY'] in ('1', s['key']) or (os.environ['ON_DRY'].endswith('*') and s['key'].startswith(os.environ['ON_DRY'][:-1])):
                try: rows, trains, pieces = trace(s); report(s, rows, pieces)
                except SystemExit as e: print(' ', e)
    else:
        build(SPECS)
        # the Quebec - Levis ferry: drawn and listed as a boat (kind v, on the water), GTFS route type 4
        import json as _j
        _vp = os.path.join(HERE, 'viz_data.json'); _vd = _j.load(open(_vp))
        for _L in _vd['lines']:
            if _L['key'].startswith('oncnfy'): _L.update(water=True, livery='cnss', segments=[]); [t.update(vessel=t.get('vessel') or '') for t in _L['trips']]
        open(_vp, 'w').write(_j.dumps(_vd, separators=(',', ':')))
        _rp = os.path.join(HERE, 'gtfs', 'routes.txt'); _rl = open(_rp).read().split('\n')
        open(_rp, 'w').write('\n'.join((_r.replace(',2,', ',4,', 1) if _r.startswith('ONCNFY') else _r) for _r in _rl))
        import csv
        GT = os.path.join(HERE, 'gtfs'); have = {r[0] for r in csv.reader(open(os.path.join(GT, 'agency.txt')))}
        with open(os.path.join(GT, 'agency.txt'), 'a', newline='') as fh:
            w = csv.writer(fh)
            for ag in (['ONR', 'Ontario Northland Railway', 'https://en.wikipedia.org/wiki/Ontario_Northland_Railway', 'America/Vancouver', 'en', ''],
                       ['ACR', 'Algoma Central Railway', 'https://en.wikipedia.org/wiki/Algoma_Central_Railway', 'America/Vancouver', 'en', ''],
                       ['TEM', 'Temiscouata Railway', 'https://en.wikipedia.org/wiki/Temiscouata_Railway', 'America/Vancouver', 'en', ''],
                       ['CGT', 'Canada & Gulf Terminal Railway', 'https://en.wikipedia.org/wiki/Canada_and_Gulf_Terminal_Railway', 'America/Vancouver', 'en', ''],
                       ['RS', 'Roberval and Saguenay Railway', 'https://en.wikipedia.org/wiki/Roberval_and_Saguenay_Railway', 'America/Vancouver', 'en', ''],
                       ['AJ', 'Alma and Jonquiere Railway', 'https://en.wikipedia.org/wiki/Alma_and_Jonqui%C3%A8re_Railway', 'America/Vancouver', 'en', ''],
                       ['GRR', 'Grand River Railway (Canadian Pacific)', 'https://en.wikipedia.org/wiki/Grand_River_Railway', 'America/Vancouver', 'en', ''],
                       ['LEN', 'Lake Erie and Northern Railway (Canadian Pacific)', 'https://en.wikipedia.org/wiki/Lake_Erie_and_Northern_Railway', 'America/Vancouver', 'en', ''],
                       ['LPS', 'London and Port Stanley Railway', 'https://en.wikipedia.org/wiki/London_and_Port_Stanley_Railway', 'America/Vancouver', 'en', ''],
                       ['THB', 'Toronto, Hamilton and Buffalo Railway', 'https://en.wikipedia.org/wiki/Toronto,_Hamilton_and_Buffalo_Railway', 'America/Vancouver', 'en', ''],
                       ['NYC', 'New York Central Railroad', 'https://en.wikipedia.org/wiki/New_York_Central_Railroad', 'America/Vancouver', 'en', ''],
                       ['DH', 'Delaware and Hudson Railroad', 'https://en.wikipedia.org/wiki/Delaware_and_Hudson_Railway', 'America/Vancouver', 'en', ''],
                       ['GWWD', 'Greater Winnipeg Water District Railway', 'https://en.wikipedia.org/wiki/Greater_Winnipeg_Water_District_Railway', 'America/Vancouver', 'en', '']):   # GWWD: missing since 18 Oct
                if ag[0] not in have: w.writerow(ag)
