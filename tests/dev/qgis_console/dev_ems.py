# ################################
# ######## Imports #################
# ################################

from urllib import unquote, urlencode
from sys import exit

# ################################
# ######## Variables  ###############
# ################################

current_crs = str(iface.mapCanvas()
                                 .mapRenderer()
                                 .destinationCrs()
                                 .authid())

# sample EMS
ems_url_in_v2_public_1 = " crs='EPSG:4326' format='PNG32' layer='0' url='http://noisy.hq.isogeo.fr:6081/arcgis/rest/services/LimitesAdministrativesFR/EPCI/MapServer' table="" sql="

QgsMapLayerRegistry.instance().removeAllMapLayers()

# for comparison, manual URL
qgis_ems_lyr_manual = QgsRasterLayer(ems_url_in_v2_public_1, "Manual - Esri Map Service", "arcgismapserver")
if qgis_ems_lyr_manual.isValid():
    QgsMapLayerRegistry.instance().addMapLayer(qgis_ems_lyr_manual)
    print("EMS manual url build SUCCEED")
    pass
else:
    print(qgis_ems_lyr_manual.error().message())
    print("EMS manual url build FAILED")


# arcgisfeatureserver

 # to remove manual layer
# QgsMapLayerRegistry.instance().removeMapLayer(qgis_ems_lyr_manual)

# test with namespaces
# url="https://download.data.grandlyon.com/wfs/grandlyon&service=WFS&version=2.0.0&request=GetFeature&maxFeatures=1000&outputFormat=application/json;+subtype=geojson&srsName=EPSG:4326&typeNames=ms:adr_voie_lieu.adrarrond&namespaces=xmlns(ns,http://mapserver.gis.umn.edu/mapserver)"

