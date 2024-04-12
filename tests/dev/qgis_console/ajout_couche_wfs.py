# -*- coding: utf-8 -*-
from qgis.core import QgsDataSourceUri, QgsProject, QgsVectorLayer, QgsCoordinateTransform, QgsCoordinateReferenceSystem
from owslib.wfs import WebFeatureService
from pprint import pprint
from qgis.utils import iface

# WFS ArcGisServer --> ça marche
#wfs_url_base = "https://ligeo.paysdelaloire.fr/server/services/ENVIRONNEMENT/MapServer/WFSServer?"
#wfs_url_base += "REQUEST=GetFeature&"
#wfs_url_base += "SERVICE=WFS&"
#wfs_url_base += "TYPENAME=ENVIRONNEMENT:Etat_des_masses_d_eau_cours_d_eau&"
#wfs_url_base += "VERSION=auto&"
#lyr = QgsVectorLayer(wfs_url_base, baseName="wfs_arcgisserver", providerLib="WFS")
#QgsProject.instance().addMapLayer(lyr)
#wfs_url_getcap = wfs_url_base + "request=GetCapabilities&service=WFS"
#wfs = WebFeatureService(wfs_url_getcap)
#print(wfs)

# WFS GeoServer --> ça marche
#wfs_url_base = "https://geobretagne.fr/geoserver/lorientagglo/wfs?"
#wfs_url_base += "REQUEST=GetFeature&"
#wfs_url_base += "SERVICE=WFS&"
#wfs_url_base += "VERSION=auto&"
#wfs_url_base += "TYPENAME=lorientagglo:cale_acces_mer&"
#wfs_url_base += "SRSNAME=EPSG:2154"
#lyr = QgsVectorLayer(wfs_url_base, baseName="wfs_geoserver", providerLib="WFS")
#QgsProject.instance().addMapLayer(lyr)

# WFS Business geografic --> ça marche
#wfs_url_base = "https://sigtest.caenlamer.fr/adws/service/wfs/e320529d-fe70-11ea-a0b9-7d7b07f756ee?"
#wfs_url_base += "REQUEST=GetFeature&"
#wfs_url_base += "SERVICE=WFS&"
#wfs_url_base += "VERSION=1.1.0&"
#wfs_url_base += "TYPENAME=bg:_06185502-ff17-11ea-a0b9-7d7b07f756ee&"
#wfs_url_base += "SRSNAME=EPSG:3857"
#lyr = QgsVectorLayer(wfs_url_base, baseName="wfs_businessgeo", providerLib="WFS")
#QgsProject.instance().addMapLayer(lyr)

# WFS QGISServer --> ça marche
#wfs_url_base = "https://cartotheque.smavd.org/index.php/lizmap/service/?repository=administratif&project=02_dpe_dpf?"
#wfs_url_base += "REQUEST=GetFeature&"
#wfs_url_base += "SERVICE=WFS&"
#wfs_url_base += "VERSION=1.1.0&"
#wfs_url_base += "TYPENAME=Bassin_versant_de_la_Durance&"
#wfs_url_base += "SRSNAME=EPSG:2154"
#lyr = QgsVectorLayer(wfs_url_base, baseName="wfs_qgisserver", providerLib="WFS")
#QgsProject.instance().addMapLayer(lyr)

# WFS IGN --> ça marche
wfs_url_base = "https://wxs.ign.fr/parcellaire/geoportail/wfs?"
wfs_url_getcap = wfs_url_base + "request=GetCapabilities&service=WFS"
wfs = WebFeatureService(url=wfs_url_base, version="2.0.0")

#pprint(wfs.__dict__)
pprint(wfs["BDPARCELLAIRE-VECTEUR_WLD_BDD_WGS84G:parcelle"].crsOptions[0])
pprint(wfs["BDPARCELLAIRE-VECTEUR_WLD_BDD_WGS84G:parcelle"].crsOptions[0].__dict__)

#print(iface.mapCanvas().extent())
#print(iface.mapCanvas().mapSettings().destinationCrs().authid())

#canvas_crs = iface.mapCanvas().mapSettings().destinationCrs()
#destination_crs = QgsCoordinateReferenceSystem(4326, QgsCoordinateReferenceSystem.EpsgCrsId)
#coord_transformer = QgsCoordinateTransform(canvas_crs, destination_crs, QgsProject.instance())
#
#print(coord_transformer.sourceCrs().authid())
#print(coord_transformer.destinationCrs().authid())
#
#canvas_rectangle = iface.mapCanvas().extent()
#canvas_rectangle_transformed = coord_transformer.transform(canvas_rectangle)
#
#print(canvas_rectangle.toString())
#print(canvas_rectangle_transformed.toString())
#wfs_url_base = "https://wxs.ign.fr/parcellaire/geoportail/wfs/?SERVICE=WFS&REQUEST=GetFeature&VERSION=2.0.0&TYPENAMES=BDPARCELLAIRE-VECTEUR_WLD_BDD_WGS84G:parcelle&TYPENAME=BDPARCELLAIRE-VECTEUR_WLD_BDD_WGS84G:parcelle&STARTINDEX=0&COUNT=1000&SRSNAME=urn:ogc:def:crs:EPSG::4326"
#wfs_url_base += "&BBOX=43.61169986958212519,1.29383935984521892,43.61719201302528148,1.30655334777672771,urn:ogc:def:crs:EPSG::4326"
#lyr = QgsVectorLayer(wfs_url_base, baseName="BDPARCELLAIRE-VECTEUR_WLD_BDD_WGS84G:parcelle", providerLib="WFS")
#QgsProject.instance().addMapLayer(lyr)


# SMAVD

#wfs_url_base += "REQUEST=GetFeature&"
#wfs_url_base += "SERVICE=WFS&"
#wfs_url_base += "VERSION=1.1.0&"
#wfs_url_base += "TYPENAME=Bassin_versant_de_la_Durance&"
#wfs_url_base += "SRSNAME=EPSG:2154"
#lyr = QgsVectorLayer(wfs_url_base, baseName="wfs_qgisserver", providerLib="WFS")
#QgsProject.instance().addMapLayer(lyr)