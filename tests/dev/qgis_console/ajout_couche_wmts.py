# -*- coding: utf-8 -*-
from qgis.core import QgsDataSourceUri, QgsProject, QgsRasterLayer
from owslib.wmts import WebMapTileService
from urllib.parse import urlencode, unquote, quote

# WMTS business geografic --> Ça marche
wmts_url_base="https://sigtest.caenlamer.fr/adws/service/wmts/e320529d-fe70-11ea-a0b9-7d7b07f756ee?"
wmts_url_getCap= wmts_url_base + "service=WMTS&request=GetCapabilities"
wmts = WebMapTileService(wmts_url_getCap)
print(wmts.version)

wmts_url_layer = ""
wmts_url_layer += "crs=EPSG:3857&"
#wmts_url_layer += "crs=EPSG:900913"
wmts_url_layer += "format=image/jpeg&"
wmts_url_layer += "layers=global_jpeg&"
wmts_url_layer += "styles=default&"
wmts_url_layer += "tileMatrixSet=GoogleMapsCompatible&"
wmts_url_layer += "url=https://sigtest.caenlamer.fr/adws/service/wmts/e320529d-fe70-11ea-a0b9-7d7b07f756ee?"
wmts_url_layer += quote("service=WMTS&")
wmts_url_layer += quote("request=GetCapabilities&")
wmts_url_layer += quote("version=1.0.0&")



print(wmts_url_layer)
lyr = QgsRasterLayer(wmts_url_layer, "wmts_qgisserver", "wms")
if lyr.isValid():
    QgsProject.instance().addMapLayer(lyr)
else:
    print(lyr.error().message())
    pass