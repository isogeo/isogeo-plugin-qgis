# ################################
# ######## Imports #################
# ################################

from urllib import unquote, urlencode
from sys import exit

try:
    from owslib.wms import WebMapService
    from owslib.wfs import WebFeatureService
    from owslib.util import ServiceException
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

qgis_wms_formats = ('image/png', 'image/png8',
                              'image/jpeg',
                              'image/svg',
                              'image/gif',
                              'image/geotiff', 'image/tiff')

# ################################
# ######## Script  #################
# ################################

# opening WMS
wms_url_getcap = "http://geobretagne.fr/geoserver/lorientagglo/wms?request=GetCapabilities&service=WMS"

try:
    wms = WebMapService(wms_url_getcap)
except ServiceException as e:
    print("WMS - Bad operation: " + wms_url_getcap, str(e))
except HTTPError as e:
    print("WMS - Service not reached: " + wms_url_getcap, str(e))
except Exception as e:
    print(str(e))

print(dir(wms))
# contents', 'exceptions', 'getOperationByName', 'getServiceXML', 'getcapabilities',
# 'getfeatureinfo', 'getmap', 'identification', 'items',
# 'operations', 'password', 'provider', 'url', 'username', 'version']

# check if GetMap operation is available
if not hasattr(wms, "getmap") or "GetMap" not in [op.name for op in wms.operations]:
    print("Required GetMap operation not available in: " + wms_url_getcap)
else:
    print("GetMap available")
    pass

# get a layer
print("Available layers: ", list(wms.contents))
layer_name = list(wms.contents)[0]
wms_lyr = wms[layer_name]
layer_title = wms_lyr.title

# is queryable
assert(wms_lyr.queryable)

# SRS
print("Available SRS: ", wms_lyr.crsOptions)
if current_crs in wms_lyr.crsOptions:
    print("It's a SRS match! With map canvas: " + current_crs)
    srs = current_crs
elif "EPSG:4326" in wms_lyr.crsOptions:
    print("It's a SRS match! With standard WGS 84 (EPSG:4326)")
    srs = "EPSG:4326"
else:
    print("Searched SRS not available within service CRS.")
    srs = ""

# Format definition
wms_lyr_formats = wms.getOperationByName('GetMap').formatOptions
formats_image = [f.split(" ", 1)[0] for f in wms_lyr_formats
                          if f in qgis_wms_formats]
if "image/png" in formats_image:
    layer_format = "image/png"
elif "image/jpeg" in formats_image:
    layer_format = "image/jpeg"
else:
    layer_format = formats_image[0]

# Style definition
print("Available styles: ", wms_lyr.styles)
lyr_style = wms_lyr.styles.keys()[0]

# GetMap URL
wms_lyr_url = wms.getOperationByName('GetMap').methods
wms_lyr_url = wms_lyr_url[0].get("url")
if wms_lyr_url[-1] == "&":
    wms_lyr_url = wms_lyr_url[:-1]
else:
    pass

# URL construction
wms_url_params = {"service": "WMS",
                           #"version": "1.3.0",
                           "request": "GetMap",
                           "layers": layer_name,
                           "crs": srs,
                           "format": layer_format,
                           "styles": lyr_style,
                           "url": wms_lyr_url,
                            }
wms_url_final = unquote(urlencode(wms_url_params))
print(wms_url_final)

# let's try to add it to the map canvas
qgis_wms_lyr = QgsRasterLayer(wms_url_final, "Auto - " + layer_title, 'wms')
if qgis_wms_lyr.isValid():
    QgsMapLayerRegistry.instance().addMapLayer(qgis_wms_lyr)
else:
    print(qgis_wms_lyr.error().message())

manual_lyr = "layers=prescription_pct&crs=EPSG:4326&version=1.1.0&url=http://geobretagne.fr/geoserver/lorientagglo/wms?SERVICE=WMS&service=WMS&format=image/png&styles=&request=GetMap"
qgis_wms_lyr = QgsRasterLayer(manual_lyr, "Manual - " + layer_title, 'wms')
if qgis_wms_lyr.isValid():
    QgsMapLayerRegistry.instance().addMapLayer(qgis_wms_lyr)
else:
    print(qgis_wms_lyr.error().message())
