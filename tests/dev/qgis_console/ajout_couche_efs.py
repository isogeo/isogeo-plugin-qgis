# -*- coding: utf-8 -*-
from qgis.core import QgsDataSourceUri, QgsProject, QgsVectorLayer
from owslib.wfs import WebFeatureService

# EFS ArcGisServer --> marche pas
wfs_url_base = "crs='EPSG:2154' filter='' url='https://carto.isogeo.net/server/rest/services/scan_services_1/EMS_EFS_WMS_WFS/FeatureServer/11' table='' sql=''"
wfs_url_base = "crs='EPSG:2154' url='https://carto.isogeo.net/server/rest/services/scan_services_1/EMS_EFS_WMS_WFS/FeatureServer/10'"

lyr = QgsVectorLayer(wfs_url_base, baseName="efs_arcgisserver", providerLib="arcgisfeatureserver")

QgsProject.instance().addMapLayer(lyr)

#if not lyr.isValid():
#    QgsProject.instance().removeMapLayer(lyr.id())
#else:
#    pass