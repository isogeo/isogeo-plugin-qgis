# -*- coding: utf-8 -*-
from qgis.core import QgsDataSourceUri, QgsProject, QgsRasterLayer, QgsCoordinateReferenceSystem, QgsProviderRegistry 
from owslib.wms import WebMapService
from urllib.parse import urlencode, unquote, quote
from pprint import pprint
from qgis.utils import iface

#print(qgis.utils.iface.mapCanvas().size())
#li_wms_tup = [
#    ("https://cartotheque.smavd.org/index.php/lizmap/service/?repository=administratif&project=02_dpe_dpf&", "1.3.0"),
#    ("http://servicescarto.cloud-manche.fr/cgi-bin/net2java.pl?port=1002&", "1.1.1"),
#    ("https://geobretagne.fr/geoserver/lorientagglo/wms?", "1.3.0"),
#    ("https://wxs.ign.fr/essentiels/geoportail/r/wms?", "1.3.0"),
#    ("https://wxs.ign.fr/parcellaire/geoportail/r/wms?", "1.3.0"),
#    ("https://wxs.ign.fr/satellite/geoportail/r/wms?", "1.3.0"),
#    ("https://wxs.ign.fr/orthohisto/geoportail/r/wms?", "1.3.0"),
#    ("https://wxs.ign.fr/environnement/geoportail/r/wms?", "1.3.0"),
#    ("https://wxs.ign.fr/agriculture/geoportail/r/wms?", "1.3.0"),
#    ("https://wxs.ign.fr/f4v4g9qykk6g8go7m4nfey4b/geoportail/v/wms?", "1.3.0"),
#    ("https://wxs.ign.fr/f4v4g9qykk6g8go7m4nfey4b/geoportail/r/wms?", "1.3.0"),
#]

#for tup in li_wms_tup:
#    getCap_url = tup[0] + "request=GetCapabilities&service=WMS"
#    version = tup[1]
#    
#    print(getCap_url)
#
#    try:
#        wms = WebMapService(getCap_url, version)
#    except:
#        wms = WebMapService(getCap_url)
#        
#    for typename in list(wms.contents.keys()):
#        wms_lyr = wms[typename]
#        if not hasattr(wms_lyr, "boundingBoxWGS84") and not hasattr(wms_lyr, "boundingBox"):
#            print(typename)
#        else:
#            wgs84_bbox = wms_lyr.boundingBoxWGS84
#            bbox = wms_lyr.boundingBox
##            print(bbox[4])
#            bbox_crs = QgsCoordinateReferenceSystem(bbox[4])
#            print("{} --> {}".format(bbox[4], bbox_crs.isValid()))
##            print(bbox[0]<bbox[1])
#        
#    print("\n")

# WMS QGisServer --> 
#wms_url_base = "https://cartotheque.smavd.org/index.php/lizmap/service/?repository=administratif&project=02_dpe_dpf&"
#wms_url = wms_url_base + "SERVICE=WMS&"
#wms_url += "VERSION=1.1.1&"
#wms_url += "REQUEST=GetMap&"
#wms_url += "layers=Bassin versant de la Durance&"
#wms_url += "crs=CRS:84&"
#wms_url += "format=image/png&"
#wms_url += "styles="
#lyr = QgsRasterLayer(wms_url, baseName="wms_qgisserver")
#QgsProject.instance().addMapLayer(lyr)
#
#wms_url_params = {
#    "SERVICE": "WMS",
#    "VERSION": "1.1.1",
#    "REQUEST": "GetMap",
#    "layers": "Bassin versant de la Durance",
#    "crs": "CRS:84",
#    "format": "image/png",
#    "styles": "",
#}
#wms_url_bis = wms_url_base + unquote(urlencode(wms_url_params, "utf8", quote_via=quote))
#lyr = QgsRasterLayer(wms_url, baseName="wms_qgisserver")
#QgsProject.instance().addMapLayer(lyr)

#wms_url_params = {
#    "SERVICE": "WMS",
#    "VERSION": "1.1.1",
#    "REQUEST": "GetMap",
#    "layers": "Bassin versant de la Durance",
#    "crs": "CRS:84",
#    "format": "image/png",
#    "styles": "",
#    "repository": "administratif",
#    "project": "02_dpe_dpf"
#    
#}
#wms_url_bis = wms_url_base.split("?")[0] + "?" + unquote(urlencode(wms_url_params, "utf8", quote_via=quote))
#wms_url_bis="https://cartotheque.smavd.org/index.php/lizmap/service/?repository=administratif&project=02_dpe_dpf&SERVICE=WMS&VERSION=1.1.1&REQUEST=GetMap&layers=Bassin versant de la Durance&crs=CRS:84&format=image/png&styles="
#lyr = QgsRasterLayer(wms_url_bis, baseName="wms_qgisserver")
#QgsProject.instance().addMapLayer(lyr)

#print(wms_url == wms_url_bis)

#wms_url_getcap = wms_url_base + "request=GetCapabilities&service=wms"
#wms = WebMapService(wms_url_getcap, "1.1.1")

#url="https://geobretagne.fr/geoserver/lorientagglo/wms?service=WMS&version=1.3.0&request=GetMap&layers=cale_acces_mer&crs=EPSG:4326&format=image/png"
#lyr = QgsRasterLayer(url, baseName="wms_qgisserver")
#QgsProject.instance().addMapLayer(lyr)

#wms_url="http://servicescarto.cloud-manche.fr/cgi-bin/net2java.pl?port=1002&SERVICE=WMS&VERSION=1.1.1&REQUEST=GetMap&layers=COLLEGE_CD50&crs=EPSG:2154&format=image/png&styles=default&TRANSPARENT=TRUE&BBOX=348109.6961969923,6833115.327081832,412050.0922378402,6962898.024864406"
#lyr = QgsRasterLayer(wms_url, baseName="COLLEGE_CD50_plugin")
#QgsProject.instance().addMapLayer(lyr)

#wms_url_params = {
#    "SERVICE": "WMS",
#    "VERSION": "1.1.1",
#    "REQUEST": "GetMap",
#    "layers": "COLLEGE_CD50",
#    "crs": "EPSG:2154",
#    "format": "image/png",
##    "styles": default,
##    "TRANSPARENT": "TRUE",
#    "url": "http://servicescarto.cloud-manche.fr/cgi-bin/net2java.pl?port=1002"
#}
#wms_url_bis="url=http://servicescarto.cloud-manche.fr/cgi-bin/net2java.pl?port%3D1002&crs=EPSG:2154&dpiMode=7&format=image/png&layers=COLLEGE_CD50&styles&"
#
#lyr = QgsRasterLayer(wms_url_bis, "COLLEGE_CD50_good", "wms")
#QgsProject.instance().addMapLayer(lyr)
#wms_url_getcap="https://wxs.ign.fr/essentiels/geoportail/r/wms?SERVICE=WMS&REQUEST=GetCapabilities"
#wms = WebMapService(wms_url_getcap, "1.1.1")
#wms_layer = wms["ORTHOIMAGERY.ORTHOPHOTOS"]
#pprint(wms_layer.__dict__)
#wms_url = "https://wxs.ign.fr/essentiels/geoportail/r/wms?SERVICE=WMS&VERSION=1.3.0&REQUEST=GetMap&BBOX=-178.187,-85,175,85&CRS=CRS:84&WIDTH=854&HEIGHT=411&LAYERS=ORTHOIMAGERY.ORTHOPHOTOS&STYLES=&FORMAT=image/png&DPI=96&MAP_RESOLUTION=96&FORMAT_OPTIONS=dpi:96&TRANSPARENT=TRUE"
#wms_url = "https://wxs.ign.fr/essentiels/geoportail/r/wms?SERVICE=WMS&VERSION=1.3.0&REQUEST=GetMap&BBOX=-178.187,-85,175,85&CRS=EPSG:4326&WIDTH=854&HEIGHT=411&LAYERS=ORTHOIMAGERY.ORTHOPHOTOS&STYLES=&FORMAT=image/png&DPI=96&MAP_RESOLUTION=96&FORMAT_OPTIONS=dpi:96&TRANSPARENT=TRUE"
#layer = QgsRasterLayer(wms_url, wms_layer.title)
#QgsProject.instance().addMapLayer(layer)
#print(layer.isValid())

wms_layer_url = "SERVICE=WMS&VERSION=1.3.0&REQUEST=GetMap&layers=Une+belle+ligne&crs=EPSG:2154&format=image/png&styles=&TRANSPARENT=TRUE&BBOX=576227.8869208727,6450495.220395137,654285.1798996647,6858657.968743979&WIDTH=962&HEIGHT=847&url=https://carto.isogeo.net/qgisserver-test?"
#wms_layer_url = "layers=Une+belle+ligne&crs=EPSG:2154&format=image/jpeg&styles=&url=https://carto.isogeo.net/qgisserver-test"
#wms_layer_url = "SERVICE=WMS&VERSION=1.3.0&REQUEST=GetMap&layers=Cours+d'eau&crs=EPSG:3857&format=image/png&styles=&TRANSPARENT=TRUE&BBOX=510953.203,5353644.413,798718.946,5819046.213&WIDTH=962&HEIGHT=847&url=https://cartotheque.smavd.org/index.php/lizmap/service/?repository%3Dadministratif%26project%3D02_dpe_dpf%26"
#wms_layer_url = "layers=Cours+d'eau&crs=EPSG:3857&format=image/png&styles=&url=https://cartotheque.smavd.org/index.php/lizmap/service/?repository%3Dadministratif%26project%3D02_dpe_dpf%26"

uri = QgsDataSourceUri()
for param in wms_layer_url.split("&"):
    key = param.split("=")[0]
    val = param.split("=")[1]
    uri.setParam(key, val.replace("+", " "))

print(bytes(uri.encodedUri()).decode())

#wms_layer_config = dict(
#    styles="",
#    layers="Une belle ligne",
#    crs="EPSG:4326",
#    format="image/jpeg",
#    url="https://carto.isogeo.net/qgisserver-test"
#)
#uri = QgsDataSourceUri()
#for key, val in wms_layer_config.items():
#    uri.setParam(key, val)
#print(bytes(uri.encodedUri()).decode())
wms_layer_title = "QGIS_Server_Layer"
#layer = QgsRasterLayer(wms_layer_url, wms_layer_title)
layer = QgsRasterLayer(bytes(uri.encodedUri()).decode(), wms_layer_title, "wms")
QgsProject.instance().addMapLayer(layer)
