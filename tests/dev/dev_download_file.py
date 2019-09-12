import base64
from datetime import datetime
import json
import urllib

from PyQt4.QtCore import QUrl, QFile, QIODevice, QSettings, QByteArray
from PyQt4.QtNetwork import QNetworkAccessManager, QNetworkRequest

# --- GLOBALS -----------------------------------------------

qsettings = QSettings()
api_id = qsettings.value("isogeo-plugin/user-auth/id", 0)
api_secret = qsettings.value("isogeo-plugin/user-auth/secret", 0)
manager = QNetworkAccessManager()

# -- FUNCTIONS ---------------------------------------------


def ask_for_token(c_id, c_secret, request_status=True):
    """Ask a token from Isogeo API authentification page.

     This send a POST request to Isogeo API with the user id and secret in
     its header. The API should return an access token
     """
    headervalue = "Basic " + base64.b64encode(c_id + ":" + c_secret)
    data = urllib.urlencode({"grant_type": "client_credentials"})
    databyte = QByteArray()
    databyte.append(data)
    url = QUrl("https://id.api.isogeo.com/oauth/token")
    request = QNetworkRequest(url)
    request.setRawHeader("Authorization", headervalue)
    if request_status is True:
        request_status = False
        return request, databyte

    QgsMessageLog.logMessage("Authentication succeeded", "Isogeo")


def request_download(manager, target_url):
    url = QUrl(target_url)
    request = QNetworkRequest(url)
    print("Download start time: {}".format(datetime.now()))
    manager.get(request)


def handle_download(reply):
    print("Download finish time: {}".format(datetime.now()))
    print("Finished: {}".format(reply.isFinished()))
    # print "Bytes received: {}".format(len(reply.readAll()))
    print(type(reply), dir(reply), help(reply.write))
    url = reply.url().path()
    print(url)
    #    with open("C:\Users\julien.moura\Documents\GIS DataBase\youhou.xml", "wb") as fifi:
    #        fifi.write(reply.writeData())
    newFile = QFile()
    newFile.setFileName(".\youhou_2.htm")
    newFile.open(QIODevice.WriteOnly)
    newFile.write(reply.readAll())
    newFile.close()
    print("done")
    reply.deleteLater()


def read_data(reply):
    messageBuffer += reply.readAll()


# ---- Main ----------------------------------------------------


# print(dir(manager))
# manager.finished.connect( handle_download )

# with a simple web page
# url = "https://www.nextinpact.com/news/103770-google-annonce-android-o-liste-nouveautes-developer-preview-disponible.htm"
# request_download(manager, url)

# with an authenticated API request
req_token = ask_for_token(api_id, api_secret)
token_reply = manager.post(req_token[0], req_token[1])
# token_reply.finished.connect(
#     partial(self.handle_token, answer=token_reply))
token_reply.finished.connect(partial(self.handle_token, answer=token_reply))
bytarray = token_reply.readAll()
print("bbibit", bytarray, dir(bytarray))
content = str(bytarray)
parsed_content = json.loads(QByteArray.fromBase64(bytarray))
print(parsed_content)
