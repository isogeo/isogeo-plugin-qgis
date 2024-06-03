from qgis.PyQt.QtCore import QSettings, QUrl
from qgis.PyQt.QtNetwork import QNetworkRequest, QNetworkReply, QSslError
from qgis.core import(
    QgsProject,
    QgsNetworkAccessManager,
    QgsDataSourceUri,
    QgsApplication,
    QgsArcGisPortalUtils,
    QgsArcGisRestContext,
    QgsArcGisRestUtils,
    QgsVectorLayer
)
import json
from pprint import pprint
from functools import partial

# qsettings = QSettings()
# for key in qsettings.allKeys():
#     if "arcgis" in key:
#         pprint(key)
# pprint("done")

# arcgis_portal_utils = QgsArcGisPortalUtils()
# pprint(dir(arcgis_portal_utils))

# auth_mng = QgsApplication.authManager()
# pprint(auth_mng)
# pprint(dir(auth_mng))

getCap_url = "https://carto.isogeo.net/server/rest/services/isogeo_test/PRIVE/FeatureServer/?f=json"
# quri = QgsDataSourceUri(getCap_url)
# authCfg = 'portal1'
# quri.setParam("authcfg", authCfg)

# qnam = QgsNetworkAccessManager.instance()
# request = QNetworkRequest(QUrl(getCap_url))
# reply = qnam.blockingGet(request, "portal1")

# reply_content_str = reply.content().data().decode("utf8")
# print(reply_content_str)
# print(type(reply_content_str))
# reply_content_json = json.loads(reply_content_str)
# print(reply_content_json)
# print(type(reply_content_json))

layer_uri = QgsDataSourceUri("crs='EPSG:2154' url='https://carto.isogeo.net/server/rest/services/isogeo_test/PRIVE/FeatureServer/5' ")
layer_uri.setParam("authcfg", "portal1")
print(layer_uri.uri(False))
vlayer = QgsVectorLayer(layer_uri.uri(False), 'test', 'arcgisfeatureserver')

QgsProject.instance().addMapLayer(vlayer)
# print(vlayer.isValid())