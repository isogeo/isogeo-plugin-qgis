# ################################
# ######## Imports #################
# ################################

from osgeo import gdal
from urllib import unquote, urlencode
from sys import exit

try:
    from owslib.wfs import WebFeatureService
    from owslib.util import ServiceException
    #from owslib import crs
    import owslib
    print("Depencencies - owslib version: {}"
                .format(owslib.__version__))
except ImportError as e:
    print("Depencencies - owslib is not present")

try:
    from owslib.util import HTTPError
    print("Depencencies - HTTPError within owslib")
except ImportError as e:
    print("Depencencies - HTTPError not within owslib."
                 " Trying to get it from urllib2 directly.")
    from urllib2 import HTTPError

# ################################
# ######## Variables  ###############
# ################################

current_crs = str(iface.mapCanvas()
                                 .mapRenderer()
                                 .destinationCrs()
                                 .authid())

# sample WFS
wfs_url_in_v2_public_1 = "http://geoserv.weichand.de:8080/geoserver/wfs?request=GetCapabilities&service=WFS"
wfs_url_in_v2_public_2 = "http://noisy.hq.isogeo.fr:6090/geoserver/ows?service=wfs&request=GetCapabilities"
wfs_url_in_v2_public_3 = "http://magosm.magellium.com/geoserver/wfs?request=GetCapabilities"
wfs_url_in_v1_public = "http://noisy.hq.isogeo.fr:6090/geoserver/ows?service=wfs&version=1.1.0&request=GetCapabilities"
wfs_url_in_v2_auth_1 = "https://www.ppige-npdc.fr/geoserver/ayants-droits/wfs?request=GetCapabilities"
wfs_url_in_v2_mix_2 = "https://www.ppige-npdc.fr/geoserver/wfs?request=GetCapabilities"

# ################################
# ######## With OWSLib  ###############
# ################################

QgsMapLayerRegistry.instance().removeAllMapLayers()

print("Using OWSLib")

# opening WFS
wfs_url_getcap = wfs_url_in_v1_public

#try:
#    wfs = WebFeatureService(wfs_url_getcap)
#except ServiceException as e:
#    print("WFS - Bad operation: " + wfs_url_getcap, str(e))
#except HTTPError as e:
#    print("WFS - Service not reached: " + wfs_url_getcap, str(e))
#except Exception as e:
#    print(str(e))
#
#print(dir(wfs))
## contents', 'exceptions', 'getOperationByName', 'getServiceXML', 'getcapabilities',
## 'getfeatureinfo', 'getmap', 'identification', 'items',
## 'operations', 'password', 'provider', 'url', 'username', 'version']
#
## service responsible
#print(wfs.provider.name, wfs.provider.url)
#try:
#    print("Contact: ",
#          wfs.provider.contact.name,
#          wfs.provider.contact.email,
#          wfs.provider.contact.position,
#          wfs.provider.contact.organization,
#          wfs.provider.contact.address,
#          wfs.provider.contact.postcode,
#          wfs.provider.contact.city,
#          wfs.provider.contact.region,
#          wfs.provider.contact.country)
#except AttributeError as e:
#    print(str(e))
#
## check if GetFeature operation is available
#if not hasattr(wfs, "getfeature") or "GetFeature" not in [op.name for op in wfs.operations]:
#    print("Required GetFeature operation not available in: " + wfs_url_getcap)
#else:
#    print("GetFeature available")
#    pass
#
#if "DescribeFeatureType" not in [op.name for op in wfs.operations]:
#    print("Required DescribeFeatureType operation not available in: " + wfs_url_getcap)
#else:
#    print("DescribeFeatureType available")
#    pass
#
## get a layer
#print("Available layers: ", list(wfs.contents))
#layer_name = list(wfs.contents)[0]
#wfs_lyr = wfs[layer_name]
#try:
#    wfs_lyr = wfs["epci_2015"]
#except KeyError as e:
#    print("Asked layer is not present (anymore): ")
#layer_title = wfs_lyr.title
#layer_id = wfs_lyr.id
#print("First layer picked: ", layer_title, layer_name, layer_id)
#
## SRS
#print("Available SRS: ", wfs_lyr.crsOptions)
#wfs_lyr_crs_epsg = ["{}:{}".format(srs.authority, srs.code) for srs in wfs_lyr.crsOptions]
#print(wfs_lyr_crs_epsg)
#
#if current_crs in wfs_lyr_crs_epsg:
#    print("It's a SRS match! With map canvas: " + current_crs)
#    srs = current_crs
#elif "EPSG:4326" in wfs_lyr_crs_epsg:
#    print("It's a SRS match! With standard WGS 84 (EPSG:4326)")
#    srs = "EPSG:4326"
#else:
#    print("Searched SRS not available within service CRS.")
#    srs = wfs_lyr_crs_epsg[0]
#
## Style definition
#print("Available styles: ", wfs_lyr.styles)
##lyr_style = wfs_lyr.styles.keys()[0]
#
## GetFeature URL
#wfs_lyr_url = wfs.getOperationByName('GetFeature').methods
#wfs_lyr_url = wfs_lyr_url[0].get("url")
#if wfs_lyr_url[-1] != "&":
#    wfs_lyr_url = wfs_lyr_url + "&"
#else:
#    pass
#
## URL construction
#wfs_url_params = {"service": "WFS",
#                  "version": "1.0.0",
#                  "typename": layer_id,
#                  "srsname": srs,
#                  "username": "",
#                  "password": "",
#                  }
##wfs_url_final = unquote(urlencode(wfs_url_params))
#wfs_url_final = wfs_lyr_url + unquote(urlencode(wfs_url_params))
#print(wfs_url_final)
#



## let's try to add it to the map canvas
#qgis_wfs_lyr_auto = QgsVectorLayer(wfs_url_final, "Auto - " + layer_title, 'WFS')
#if qgis_wfs_lyr_auto.isValid():
#    QgsMapLayerRegistry.instance().addMapLayer(qgis_wfs_lyr_auto)
#    print("WFS auto url build SUCCEED")
#else:
#    print("WFS auto url build FAILED")
#    print(qgis_wfs_lyr_auto.error().message())

## URI

uri = QgsDataSourceURI()
uri.setParam ("url", wfs_url_getcap)
uri.setParam ( "typename", layer_id)
uri.setParam ( "version", "auto")
uri.setParam ( "srsname", srs")
uri.setParam ( "restrictToRequestBBOX", "1")

# let's try to add it to the map canvas
qgis_wfs_lyr_auto = QgsVectorLayer(uri.uri(), "Auto - " + layer_title, 'WFS')
if qgis_wfs_lyr_auto.isValid():
    QgsMapLayerRegistry.instance().addMapLayer(qgis_wfs_lyr_auto)
    print("WFS auto url build with URI DataSource SUCCEED")
else:
    print("WFS auto url build FAILED")
    print(qgis_wfs_lyr_auto.error().message())

## for comparison, manual URL
#manual_lyr = "http://geoserv.weichand.de:8080/geoserver/wfs?request=GetFeature&service=WFS&srsname=EPSG:31468&typename=bvv:vg_ex&version=1.0.0"
#qgis_wfs_lyr_manual = QgsVectorLayer(manual_lyr, "Manual - " + layer_title, 'WFS')
#if qgis_wfs_lyr_manual.isValid():
#    QgsMapLayerRegistry.instance().addMapLayer(qgis_wfs_lyr_manual)
#    print("WFS manual url build SUCCEED")
#    pass
#else:
#    print(qgis_wfs_lyr_manual.error().message())
#    print("WFS manual url build FAILED")

# to remove manual layer
# QgsMapLayerRegistry.instance().removeMapLayer(qgis_wfs_lyr_manual)

# ################################
# ######## With GDAL  ###############
# ################################

print("Using GDAL (ogr)")

QgsMapLayerRegistry.instance().removeAllMapLayers()

# Open the service
try:
    wfs_gdal = gdal.OpenEx(wfs_url_getcap)
except Exception as e:
    print(e)

print(dir(wfs_gdal))

# Get a layer
print("Available layers: ", wfs_gdal.GetLayerCount())
try:
    wfs_lyr = wfs_gdal.GetLayerByName("epci_2015")
except KeyError as e:
    print("Asked layer is not present (anymore): epci_2015")
wfs_lyr = wfs_gdal.GetLayerByIndex(0)
print(dir(wfs_lyr))
layer_title = wfs_lyr.GetMetadata().get("TITLE")
layer_name = wfs_lyr.GetName()
# layer_id = wfs_lyr
print("First layer picked: ", layer_title, layer_name)

# SRS
lyr_srs = wfs_lyr.GetSpatialRef()
lyr_srs.AutoIdentifyEPSG()
if lyr_srs.GetAuthorityName("PROJCS"):
    print("CRS type: projected")
    srs = "{}:{}".format(lyr_srs.GetAuthorityName("PROJCS"),
                                    lyr_srs.GetAuthorityCode("PROJCS"))
elif lyr_srs.GetAuthorityName("GEOGCS"):
    print("CRS type: geographic")
    srs = "{}:{}".format(lyr_srs.GetAuthorityName("GEOGCS"),
                                    lyr_srs.GetAuthorityCode("GEOGCS"))
else:
    print("SRS: undetermined CRS")
    pass

print(srs)

if current_crs in srs:
    print("It's a SRS match! With map canvas: " + current_crs)
elif "EPSG:4326" in srs:
    print("It's a SRS match! With standard WGS 84 (EPSG:4326)")
    srs = "EPSG:4326"
else:
    print("Searched SRS not available within service CRS.")
    srs = srs
