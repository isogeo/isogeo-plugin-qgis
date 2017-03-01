from datetime import datetime
from PyQt4.QtCore import QUrl
from PyQt4.QtNetwork import QNetworkAccessManager, QNetworkRequest

def request_download(manager):
    url = QUrl("http://sampleserver6.arcgisonline.com/arcgis/rest/services/WorldTimeZones/MapServer/WMTS?request=GetCapabilities")
    request = QNetworkRequest(url)
    print "Download start time: {}".format(datetime.now())
    manager.get( request )

def handle_download(reply):
    print "Download finish time: {}".format(datetime.now())
    print "Finished: {}".format(reply.isFinished())
    print "Bytes received: {}".format(len(reply.readAll()))

manager = QNetworkAccessManager()
manager.finished.connect( handle_download )
request_download(manager)