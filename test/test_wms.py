# ################################
# ######## Imports #################
# ################################

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
layer_name = wms[list(wms.contents)[0]]

# is queryable
assert(layer_name.queryable)

