# -*- coding: utf-8 -*-
from qgis.core import QgsDataSourceUri, QgsProject, QgsRasterLayer
from owslib.wmts import WebMapTileService
from urllib.parse import urlencode, unquote, quote
from pprint import pprint 

# WMTS business geografic --> Ça marche
wmts_url_1="https://sigtest.caenlamer.fr/adws/service/wmts/e320529d-fe70-11ea-a0b9-7d7b07f756ee?&service=WMTS&request=GetCapabilities"
wmts_url_2="https://demo.lizmap.com/lizmap/index.php/lizmap/service/?repository=demo&project=lampadaires&service=WMTS&request=GetCapabilities"
wmts_url_3="https://wxs.ign.fr/beta/geoportail/wmts?SERVICE=WMTS&VERSION=1.0.0&REQUEST=GetCapabilities"
wmts_1=WebMapTileService("https://sigtest.caenlamer.fr/adws/service/wmts/e320529d-fe70-11ea-a0b9-7d7b07f756ee?&service=WMTS&request=GetCapabilities")
wmts_2=WebMapTileService("https://demo.lizmap.com/lizmap/index.php/lizmap/service/?repository=demo&project=lampadaires&service=WMTS&request=GetCapabilities")
wmts_3=WebMapTileService("https://wxs.ign.fr/beta/geoportail/wmts?SERVICE=WMTS&VERSION=1.0.0&REQUEST=GetCapabilities")
pprint(wmts_1.getOperationByName("GetTile").methods[0].get("url"))
pprint(wmts_2.getOperationByName("GetTile").methods[0].get("url"))
pprint(wmts_3.getOperationByName("GetTile").methods[0].get("url"))
#tms_dict = {}
#for tms in wmts_3.tilematrixsets:
#    crs_elem = wmts_3.tilematrixsets.get(tms).crs.split(":")
#    if len(crs_elem) == 2:
#        key = wmts_3.tilematrixsets.get(tms).crs
#    else:
#        key = "EPSG:" + crs_elem[-1]
#    tms_dict[key] = wmts_3.tilematrixsets.get(tms).identifier
#pprint(tms_dict)
#
#for lyr in wmts_3.contents:
#    pprint(wmts_3[lyr].title)
#    pprint(wmts_3[lyr]._tilematrixsets)
#