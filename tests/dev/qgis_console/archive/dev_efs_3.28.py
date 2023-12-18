# ################################
# ######## Imports #################
# ################################


# ################################
# ######## Variables  ###############
# ################################

current_crs = str(iface.mapCanvas().mapRenderer().destinationCrs().authid())

# sample EFS
efs_url_in_v2_public_1 = (
    "crs='EPSG:2154' filter='' url='https://carto.isogeo.net/server/rest/services/scan_services_1/EMS_EFS_WMS_WFS/FeatureServer/6' table'' sql=''"
    " sql="
)

QgsMapLayerRegistry.instance().removeAllMapLayers()


uri = QgsDataSourceURI()
uri.setParam("url", "url='https://carto.isogeo.net/server/rest/services/scan_services_1/EMS_EFS_WMS_WFS/FeatureServer/6")
# uri.setParam("typename", layer_id)
# uri.setParam("version", "auto")
uri.setParam("crs", "EPSG:2154")
# uri.setParam("restrictToRequestBBOX", "1")

# let's try to add it to the map canvas
qgis_efs_lyr_auto = QgsVectorLayer(uri.uri(), "EFS Isogeo", "arcgisfeatureserver")
QgsMapLayerRegistry.instance().addMapLayer(qgis_efs_lyr_auto)

# for comparison, manual URL
qgis_efs_lyr_manual = QgsVectorLayer(
    efs_url_in_v2_public_1, "Manual - Esri Feature Service", "arcgisfeatureserver"
)
if qgis_efs_lyr_manual.isValid():
    QgsMapLayerRegistry.instance().addMapLayer(qgis_efs_lyr_manual)
    print("EFS manual url build SUCCEED")
    pass
else:
    print(qgis_efs_lyr_manual.error().message())
    print("EFS manual url build FAILED")


# arcgisfeatureserver

# to remove manual layer
# QgsMapLayerRegistry.instance().removeMapLayer(qgis_ems_lyr_manual)

# test with namespaces
# url="https://download.data.grandlyon.com/wfs/grandlyon&service=WFS&version=2.0.0&request=GetFeature&maxFeatures=1000&outputFormat=application/json;+subtype=geojson&srsName=EPSG:4326&typeNames=ms:adr_voie_lieu.adrarrond&namespaces=xmlns(ns,http://mapserver.gis.umn.edu/mapserver)"
