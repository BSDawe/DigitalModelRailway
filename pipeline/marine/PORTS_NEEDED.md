# Ontario steamer ports still to be placed (Brendan, 23 Oct 2026: build the steamers once he supplies port locations)

- Pointe au Baril Island Transport: BUILT in Version 137 (7 Nov 2026), points from Brendan.
- Muskoka Lakes Navigation: Bala (steamer wharf), Beaumaris, Port Carling, Windermere, Wigwassan, Royal Muskoka, Rosseau, Minett, Elgin House, Natural Park
- CP Great Lakes (Keewatin, Assiniboia) and S.S. Manitoba: Port McNicoll, Owen Sound, Sault Ste. Marie (which wharf), Port Arthur, Fort William (the CP dock)
- Water: Georgian Bay, Owen Sound, St. Marys River and Lake Superior are in the eastern water layer (checked), but not yet in the steamer routing
  (water_extra.pkl): adding them re-routes every existing lane, so do it with the first eastern boat.
- Muskoka water (checked 7 Nov 2026): the BASEMAP TILES (as used by lo_build) have Lakes Muskoka, Rosseau and Joseph; the Port Carling lock cut is not
  water there (too narrow): a waypoint. water_east.json still lacks them. Also CN Table 126 prints Muskoka Wharf - Beaumaris - Port Carling - Wigwassan -
  Royal Muskoka steamers: not transcribed yet.
- Quebec - Levis ferry (CN connection, CP Table 33; times in on_cnpool_t033.csv): Brendan, 24 Oct 2026: from Levis Station to the Quebec wharf at
  46.81183142623051, -71.20161491263052. Levis Station: the Quebec collection has CN "Levis" at 46.81032, -71.18712 (to confirm). To build with the
  CN Montreal - Levis trains (CN timetables); the St. Lawrence at Quebec needs adding to the steamer routing then.
- Prescott - Ogdensburg ferry (CP Table 44A, connection with Nos. 29 / 30 at Prescott): to do (Brendan, 25 Oct 2026); needs the Prescott and
  Ogdensburg landings and the St. Lawrence there in the steamer routing; times not printed in Table 44A.
