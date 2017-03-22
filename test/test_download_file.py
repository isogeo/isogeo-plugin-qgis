from datetime import datetime
from PyQt4.QtCore import QUrl, QFile, QIODevice
from PyQt4.QtNetwork import QNetworkAccessManager, QNetworkRequest

def request_download(manager):
    url = QUrl("https://www.nextinpact.com/news/103770-google-annonce-android-o-liste-nouveautes-developer-preview-disponible.htm")
    request = QNetworkRequest(url)
    print "Download start time: {}".format(datetime.now())
    manager.get( request )

def handle_download(reply):
    print "Download finish time: {}".format(datetime.now())
    print "Finished: {}".format(reply.isFinished())
    # print "Bytes received: {}".format(len(reply.readAll()))
    print(type(reply), dir(reply), help(reply.write))
    url = reply.url().path()
    print(url)
#    with open("C:\Users\julien.moura\Documents\GIS DataBase\youhou.xml", "wb") as fifi:
#        fifi.write(reply.writeData())
    newFile = QFile()
    newFile.setFileName("C:\Users\julien.moura\Documents\GIS DataBase\youhou_2.htm")
    newFile.open(QIODevice.WriteOnly)
    newFile.write(reply.readAll())
    newFile.close()
    print("done")
    reply.deleteLater()

def read_data(reply):
    messageBuffer += reply.readAll()
    

manager = QNetworkAccessManager()
# print(dir(manager))
manager.finished.connect( handle_download )
request_download(manager)

