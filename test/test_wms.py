from owslib.wms import WebMapService
from owslib.util import HTTPError, ServiceException

try:
    wms = WebMapService(wms_url_getcap)
except HTTPError as e:
#   print("rooo", HTTPError.message.__str__,
#            HTTPError.errno,
#            HTTPError.reason,
#            HTTPError.getcode)
    print(str(e))
