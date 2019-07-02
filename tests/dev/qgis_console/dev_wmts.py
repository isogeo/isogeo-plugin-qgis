# ################################
# ######## Imports #################
# ################################

from urllib import unquote, urlencode
from sys import exit

try:
    from owslib.wmts import WebMapTileService
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

QgsMapLayerRegistry.instance().removeAllMapLayers()

# sample WMTS
wmts_url_in_public_1 = "http://suite.opengeo.org/geoserver/gwc/service/wmts?request=getcapabilities"  # bd_lyr = "opengeo:countries"
wmts_url_in_public_2 = "http://noisy.hq.isogeo.fr:6090/geoserver/gwc/service/wmts?REQUEST=GetCapabilities" # i_lyr = "Isogeo:WC2014_stadiums"
wmts_url_in_public_3 = "http://opencache.statkart.no/gatekeeper/gk/gk.open_wmts?service=WMTS&request=GetCapabilities"  # msc_lyr = "Europakart"
wmts_url_in_public_4_esri = "http://data.geus.dk/arcgis/rest/services/OneGeologyGlobal/S071_G2500_OneGeology/MapServer/WMTS?request=GetCapabilities"
wmts_url_in_public_5_esri = "http://sampleserver6.arcgisonline.com/arcgis/rest/services/WorldTimeZones/MapServer/WMTS?REQUEST=GetCapabilities&SERVICE=WMTS"
wmts_url_in_publc_6 = "http://openlayers.org/en/v4.0.1/examples/data/WMTSCapabilities.xml?request=GetCapabilities&service=WMTS"
wmts_url_in_publc_7 = "https://www.ppige-npdc.fr/geoserver/gwc/service/wmts?REQUEST=GetCapabilities"

# opening WMTS
wmts_url_getcap = wmts_url_in_public_1

try:
    wmts = WebMapTileService(wmts_url_getcap)
except TypeError as e:
    print("OWSLib mixing str and unicode args", str(e))
    wmts = WebMapTileService(unicode(wmts_url_getcap))
except ServiceException as e:
    print("WMTS - Bad operation: " + wmts_url_getcap, str(e))
except HTTPError as e:
    print("WMTS - Service not reached: " + wmts_url_getcap, str(e))
except Exception, e:
    print(str(e))
    tout

print(dir(wmts))
#'buildTileRequest', 'contents', 'getOperationByName', 'getServiceXML', 'getfeatureinfo', 
#'gettile', 'identification', 'items', 'operations', 'password', 'provider',
#'serviceMetadataURL', 'themes', 'tilematrixsets', 'url', 'username', 'version']

# service responsible
#print(wmts.provider.name, wmts.provider.url)
#print("Contact: ", wmts.provider.contact.name,
#                           wmts.provider.contact.email,
#                           wmts.provider.contact.position,
#                           wmts.provider.contact.organization,
#                           wmts.provider.contact.address,
#                           wmts.provider.contact.postcode,
#                           wmts.provider.contact.city,
#                           wmts.provider.contact.region,
#                           wmts.provider.contact.country)

# check if GetTile operation is available
if not hasattr(wmts, "gettile") or "GetTile" not in [op.name for op in wmts.operations]:
    print("Required GetTile operation not available in: " + wmts_url_getcap)
else:
    print("GetTile available")
    pass

# Get a layer
print("Available layers: ", list(wmts.contents))
layer_name = list(wmts.contents)[0]
wmts_lyr = wmts[layer_name]
layer_title = wmts_lyr.title
layer_id = wmts_lyr.id
print("First layer picked: ", layer_title, layer_name, layer_id)


# Tile Matrix Set & SRS
print("Available tile matrix sets: ", wmts_lyr.tilematrixsets, type(wmts_lyr.tilematrixsets))
def_tile_matrix_set = wmts_lyr.tilematrixsets[0]
print(dir(def_tile_matrix_set))

if current_crs in wmts_lyr.tilematrixsets:
    print("It's a SRS match! With map canvas: " + current_crs)
    tile_matrix_set = wmts.tilematrixsets.get(current_crs).identifier
    srs = current_crs
elif "EPSG:4326" in wmts_lyr.tilematrixsets:
    print("It's a SRS match! With standard WGS 84 (EPSG:4326)")
    tile_matrix_set = wmts.tilematrixsets.get("EPSG:4326").identifier
    srs = "EPSG:4326"
elif "EPSG:900913" in wmts_lyr.tilematrixsets:
    print("It's a SRS match! With Google (EPSG:900913)")
    tile_matrix_set = wmts.tilematrixsets.get("EPSG:900913").identifier
    srs = "EPSG:900913"
else:
    print("Searched SRS not available within service CRS.")
    tile_matrix_set = wmts.tilematrixsets.get(def_tile_matrix_set).identifier
    srs = tile_matrix_set

# Format definition
wmts_lyr_formats = wmts.getOperationByName('GetTile').formatOptions
formats_image = [f.split(" ", 1)[0] for f in wmts_lyr_formats
                          if f in qgis_wms_formats]
if len(formats_image):
    if "image/png" in formats_image:
        layer_format = "image/png"
    elif "image/jpeg" in formats_image:
        layer_format = "image/jpeg"
    else:
        layer_format = formats_image[0]
else:
    # try with PNG
    layer_format = "image/png"

# Style definition
print("Available styles: ", wmts_lyr.styles)
lyr_style = wmts_lyr.styles.keys()[0]

# Themes listing
#print("Available themes: ", wmts.themes)
#lyr_themes = wmts.themes.keys()[0]


# GetTile URL
wmts_lyr_url = wmts.getOperationByName('GetTile').methods
wmts_lyr_url = wmts_lyr_url[0].get("url")
if wmts_lyr_url[-1] == "&":
    wmts_lyr_url = wmts_lyr_url[:-1]
else:
    pass

# URL construction
wmts_url_params = {"SERVICE": "WMTS",
                           "VERSION": "1.0.0",
                           "REQUEST": "GetCapabilities",
                           "layers": layer_id,
                           "crs": srs,
                           "format": layer_format,
                           "styles": "",
                           "tileMatrixSet": tile_matrix_set,
                           "url": wmts_lyr_url,
                            }
wmts_url_final = unquote(urlencode(wmts_url_params))
print(wmts_url_final)

# let's try to add it to the map canvas
qgis_wmts_lyr_manual = QgsRasterLayer(wmts_url_final, "Auto - " + layer_title, 'wms')
if qgis_wmts_lyr_manual.isValid():
    QgsMapLayerRegistry.instance().addMapLayer(qgis_wmts_lyr_manual)
else:
    print(qgis_wmts_lyr_manual.error().message())

manual_lyr = "contextualWMSLegend=0&crs=EPSG:4326&dpiMode=7&featureCount=10&format=image/jpeg&layers=usa:states&styles=&tileMatrixSet=EPSG:4326&url=http://suite.opengeo.org/geoserver/gwc/service/wmts?request%3DGetCapabilities"
qgis_wmts_lyr = QgsRasterLayer(manual_lyr, "Manual - " + layer_title, 'wms')
if qgis_wmts_lyr.isValid():
    QgsMapLayerRegistry.instance().addMapLayer(qgis_wmts_lyr)
    pass
else:
    print(qgis_wmts_lyr.error().message())

# to remove manual layer
# QgsMapLayerRegistry.instance().removeMapLayer(qgis_wmts_lyr_manual)
