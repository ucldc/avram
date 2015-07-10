echo 'SET OAI ENRICHS'
python set_new_enrichements_item.py --harvest_type=OAI oai___.enrich
echo 'SET OAC ENRICHS'
python set_new_enrichements_item.py --harvest_type=OAC oac___.enrich
echo 'SET NUXEO ENRICHS'
python set_new_enrichements_item.py --harvest_type=NUX nux___.enrich
echo 'SET ALEPH ENRICHS'
python set_new_enrichements_item.py --harvest_type=ALX alx___.enrich
echo 'SET UCSF XML ENRICHS'
python set_new_enrichements_item.py --harvest_type=SFX sfx___.enrich
echo 'SET SOLR UCLA ENRICHS'
python set_new_enrichements_item.py --harvest_type=SLR --campus_id=10 solr_ucla__.enrich
echo 'SET SOLR UCSD ENRICHS'
python set_new_enrichements_item.py --harvest_type=SLR --campus_id=6 solr_ucsd__.enrich
echo 'SET OAI UCI ENRICHS'
python set_new_enrichements_item.py --harvest_type=OAI --campus_id=3 oai_uci__.enrich
echo 'SET MARC LAPL ENRICHS'
python set_new_enrichements_item.py --collection_id=26094 mrc__los-angeles-public-library_.enrich
echo 'SET MARC SFPL ENRICHS'
python set_new_enrichements_item.py --collection_id=26095 mrc__sfpl_.enrich
