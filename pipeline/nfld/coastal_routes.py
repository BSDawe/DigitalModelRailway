"""Newfoundland coastal steamer routes: ports in order with miles, from the CN folder "Lines in Newfoundland", May 8, 1949 (Folder N No. 1),
Steamship Service page (Brendan, 13 Nov 2026; https://rollymartincountry.blogspot.com/2022/02/cnr-1949-newfoundland-public-timetable.html).
'out' = outward only, 'in' = inward only, 'wx' = weather permitting, 'west' = going west only."""
ROUTES = {
 'placentia_west': ('Placentia Bay - West Run (every two weeks, Monday)', [
   (0, 'Argentia'), (21, 'Merasheen'), (26, 'Presque'), (29, "St. Kyran's"), (40, 'Paradise'), (46, 'Petite Forte'), (55, "St. Joseph's"),
   (62, 'Oderin'), (69, 'Baine Harbour'), (79, 'Flat Island'), (94, 'Marystown'), (108, 'Burin'), (110, 'Great Burin'), (113, 'Epworth'),
   (127, 'St. Lawrence'), (140, 'Lawn'), (150, "Lord's Cove", 'wx'), (154, 'Point au Gaul', 'wx'), (158, 'Lamaline'), (188, 'Fortune'), (193, 'Grand Bank')]),
 'placentia_bay': ('Placentia Bay - Bay Run (every two weeks, Monday)', [
   (0, 'Argentia'), (5, 'Ship Harbour'), (12, 'Iona'), (20, 'Red Island'), (28, 'Rosaru', 'out'), (35, 'Kingwell', 'out'), (45, 'Harbour Buffett'),
   (54, 'Haystack'), (63, "Spencer's Cove"), (73, 'Brule'), (76, 'North Harbour'), (82, 'Sound Island'), (88, 'Woody Island'), (93, 'Bar Haven'),
   (101, "Tack's Beach"), (108, 'Davis Cove'), (118, 'Clattice Harbour'), (121, "St. Leonard's"), (123, 'Isle Valen')]),
 'south_coast': ('South Coast and Fortune Bay Service (every two weeks)', [
   (0, 'Argentia'), (50, 'Marystown'), (64, 'Burin'), (79, 'St. Lawrence'), (124, 'Fortune'), (129, 'Grand Bank'), (148, 'Garnish'),
   (162, 'Point Enragee'), (175, "St. Bernard's"), (179, "Bay L'Argent"), (189, 'Terrenceville'), (206, "Anderson's Cove"), (214, 'Rencontre East'),
   (224, "Pool's Cove"), (234, 'Belleoram'), (238, 'St. Jacques'), (242, 'English Hr. West'), (245, 'Mose Ambrose'), (262, 'Jersey Hr.'),
   (264, 'Hr. Breton'), (283, 'Pass Island'), (295, 'Hermitage'), (298, 'Gaultois'), (317, 'Milltown'), (323, "St. Alban's"), (343, 'Pushthrough'),
   (369, 'Rencontre West'), (378, 'Francois'), (387, 'Cape La Hune'), (411, 'Ramea'), (422, 'Burgeo'), (452, 'Grand Bruit'), (462, 'La Poile'),
   (477, 'Rose Blanche'), (491, 'Isle au Morte', 'west'), (499, 'Port aux Basques')]),
 'lewisporte': ("St. John's - Lewisporte Service", [
   (0, "St. John's"), (60, 'Catalina'), (89, "King's Cove"), (110, 'East Port'), (117, 'Flat Island'), (123, "St. Brendan's"), (126, 'Deer Island'),
   (133, 'Indian Bay'), (144, 'Greenspond'), (149, 'Valleyfield'), (154, 'Wesleyville'), (173, 'Lumsden'), (189, 'Musgrave Hr.'), (193, 'Ladle Cove'),
   (204, 'Carmanville'), (211, 'Fredericton', 'out'), (221, 'Main Point (Big Bight)', 'out'), (224, 'Gander Bay', 'out'), (228, 'Victoria', 'out'),
   (243, 'Horwood', 'out'), (258, 'Stag Harbour', 'out'), (261, 'Indian Island'), (266, 'Seldom'), (279, 'Tilting'), (286, "Joe Batt's Arm"),
   (291, 'Fogo'), (297, 'Change Islands'), (306, 'Herring Neck'), (318, 'Twillingate'), (330, "Moreton's Hr."), (356, 'Lewisporte')]),
 'green_bay': ('Green Bay Service (leaving Lewisporte every Sunday)', [
   (0, 'Lewisporte'), (22, 'Exploits'), (33, 'Fortune Harbour'), (43, "Cottrell's Cove"), (48, 'Leading Tickles'), (58, 'Triton West'),
   (61, 'Brighton'), (68, "Pilley's Island"), (71, "Robert's Arm"), (75, 'Port Anson'), (85, 'Springdale'), (101, "Lush's Bight"), (107, 'Beaumont'),
   (114, 'Little Bay Islands'), (124, 'Little Bay'), (137, "Harry's Harbour"), (145, "Jackson's Cove", 'out'), (156, "King's Point", 'out'),
   (159, 'Rattling Brook', 'out'), (170, 'Burlington, N.W. Arm', 'out'), (179, "Nipper's Harbour"), (188, "Snook's Arm"), (193, 'Shoe Cove')]),
 'notre_dame': ('Notre Dame Bay Service (leaving Lewisporte every Thursday)', [
   (0, 'Lewisporte'), (11, 'Campbellton'), (23, 'Newstead'), (31, 'Summerford'), (44, "Moreton's Hr."), (50, "Tizzard's Hr."), (61, 'Twillingate'),
   (73, 'Herring Neck'), (90, "Boyd's Cove", 'in'), (98, 'Beaver Cove', 'in'), (110, 'Change Islands'), (116, 'Fogo')]),
 'labrador': ('Labrador Service (first voyage made in June)', [
   (0, "St. John's"), (40, 'Carbonear'), (90, 'Catalina'), (137, 'Wesleyville'), (214, 'Twillingate'), (319, 'St. Anthony'), (380, 'Battle Harbour'),
   (390, 'Spear Harbour'), (400, 'Francis Harbour'), (405, "Fishing Ship's Hr."), (410, 'Ship Harbour', 'out'), (417, 'Occasional Harbour', 'out'),
   (425, 'Square Islands'), (430, 'Dead Island'), (438, 'Snug Harbour'), (445, 'Venison Islands'), (450, "Hawk's Harbour"), (458, "Bolster's Rock"),
   (463, 'Comfort Bight'), (469, "Frenchman's Island"), (474, "Webber's Cove"), (479, 'Sandy Islands'), (484, 'Batteau'), (488, 'Black Tickle'),
   (493, 'Spotted Islands'), (499, 'Red Point'), (505, 'Indian Tickle'), (512, 'Wolf Islands'), (533, 'Black Islands'), (536, 'Grady'),
   (559, 'Cartwright'), (577, "Pack's Harbour"), (646, 'Rigolet', 'out'), (692, 'Indian Harbour'), (695, 'Smokey'), (705, 'White Bears', 'out'),
   (718, 'Emily Harbour'), (723, 'Holton'), (754, 'Cape Harrison'), (784, 'Iron Bound Islands'), (793, 'Macovik'), (802, 'Ailik'),
   (807, 'Turnavik'), (845, 'Hopedale')]),
 'cooks_harbour': ("St. John's - Cook's Harbour Service", [
   (0, "St. John's"), (60, 'Catalina'), (89, "King's Cove"), (125, 'Wesleyville'), (202, 'Twillingate'), (244, 'Little Bay Islands'),
   (254, "Nipper's Hr."), (281, 'La Scie'), (294, 'Horse Islands'), (306, 'Pacquet'), (322, 'Baie Verte'), (331, "Coachman's Cove"),
   (336, 'Fleur de Lys'), (358, 'Seal Cove'), (368, 'Bear Cove'), (373, 'Westport'), (390, 'Hampden'), (404, "Sop's Arm"), (410, "Jackson's Arm"),
   (450, 'Great Hr. Deep'), (466, 'Williamsport'), (475, 'Hooping Harbour'), (485, 'Canada Harbour'), (496, 'Roddickton'), (506, 'Englee'),
   (524, 'Grey Island'), (538, 'Conche'), (558, "St. Julien's"), (565, 'Fishot Island'), (579, 'St. Anthony'), (595, 'Griquet'), (607, 'Quirpon'),
   (614, 'Ship Cove'), (621, 'Raleigh'), (627, "Cook's Hr.")]),
 'battle_harbour': ('Corner Brook - Battle Harbour Service', [
   (0, 'Corner Brook'), (35, 'Trout River'), (48, 'Bonne Bay'), (77, 'Cow Head'), (83, "Parson's Pond"), (97, "Daniel's Hr."), (127, 'Port Saunders'),
   (139, 'Old Port au Choix'), (171, "St. Margaret's Bay"), (179, 'Brig Bay'), (195, "Flower's Cove"), (212, 'Forteau'), (220, 'Lance au Loup'),
   (240, 'Red Bay'), (270, 'Henley Hr.'), (292, 'Cape St. Charles'), (302, 'Battle Hr.')]),
}
