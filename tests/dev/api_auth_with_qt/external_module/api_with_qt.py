"""
/***************************************************************************
 Isogeo
                              -------------------
        begin                : 2019-06-12
        git sha              : $Format:%H$
        copyright            : (C) 2019 by Isogeo, Simon Sampere
        email                : projects+qgis@isogeo.com
 ***************************************************************************/
/***************************************************************************

    This module has been developed in accordance with this Issue: 
    https://github.com/isogeo/isogeo-plugin-qgis/issues/185 

 ***************************************************************************/
/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

# Standard library
from urllib.parse import urlencode
import os
import base64
import json
from functools import partial
import logging
from logging.handlers import RotatingFileHandler

# PyQT
from qgis.PyQt.QtNetwork import QNetworkAccessManager, QNetworkRequest
from qgis.PyQt.QtCore import QUrl, QByteArray
from qgis.PyQt.QtWidgets import QApplication

# Third part library
from isogeo_pysdk import IsogeoUtils, Isogeo

# UI class
from ui import AuthWidget

# -- LOG FILE --------------------------------------------------------
basepath = os.path.dirname(os.path.realpath(__file__))
logdir = os.path.join(basepath, "_logs")

if not os.path.exists(logdir):
    os.mkdir(logdir)

log_level = logging.DEBUG

logger = logging.getLogger("IsogeoAPIAuthWithQT")
logging.captureWarnings(True)

logger.setLevel(log_level)
log_form = logging.Formatter(
    "%(asctime)s || %(levelname)s " "|| %(module)s - %(lineno)d ||" " %(funcName)s || %(message)s"
)
logfile = RotatingFileHandler(os.path.join(logdir, "log_api_with_pyqt.log"), "a", 5000000, 1)

logfile.setLevel(log_level)
logfile.setFormatter(log_form)

logger.addHandler(logfile)

# ############################################################################
# ########## Classes ###############
# ##################################


class ApiConnection:
    def __init__(self, auth_file):

        logger.debug("\n================== ISOGEO API WITH QT ==================")

        # getting credentials :
        logger.debug("Getting credentials")
        self.utils = IsogeoUtils()
        self.app_creds = self.utils.credentials_loader(auth_file)
        self.app_id = self.app_creds.get("client_id")
        self.app_secrets = self.app_creds.get("client_secret")

        # for connection :
        self.naMngr = QNetworkAccessManager()
        self.token_url = "https://id.api.isogeo.com/oauth/token"
        self.request_url = "https://v1.api.isogeo.com/resources/search?_limit=0&_offset=0"
        self.token = ""

        # for ui :
        logger.debug("Processing and displaying UI")
        self.app = QApplication([])
        self.ui = AuthWidget()
        self.ui.resize(350, 100)
        self.ui.btn.clicked.connect(self.api_authentification)
        self.pysdk_checking()
        self.ui.show()
        self.app.exec()

    def pysdk_checking(self):
        logger.debug("\n------------------ isogeo-pysdk ------------------")
        logger.debug("Checking credentials")
        try:
            isogeo = Isogeo(self.app_id, self.app_secrets)
            isogeo.connect()
        except OSError as e:
            logger.debug("Credentials issue : {}".format(e))
            return
        except ValueError as e:
            logger.debug("Credentials issue : {}".format(e))
            return

        self.md_expected = isogeo.search(whole_share=0, page_size=0, augment=0).get("total")
        self.ui.lbl_expected.setText("{} expected resources".format(self.md_expected))
        logger.debug(
            "isogeo-pysdk validates the authentication file, {} accessible resources".format(
                self.md_expected
            )
        )

    def api_authentification(self):
        logger.debug("\n------------------ Authentication ------------------")

        # creating credentials header
        logger.debug("Creating credentials header")

        crd_header_value = QByteArray()
        crd_header_value.append("Basic ")
        crd_header_value.append(
            base64.b64encode("{}:{}".format(self.app_id, self.app_secrets).encode())
        )

        crd_header_name = QByteArray()
        crd_header_name.append("Authorization")

        # creating Content-Type header
        logger.debug("Creating 'Content-Type' header")

        ct_header_value = QByteArray()
        ct_header_value.append("application/json")

        # creating request
        token_rqst = QNetworkRequest(QUrl(self.token_url))
        logger.debug("Creating token request : {}".format(token_rqst.url()))

        # setting headers
        token_rqst.setRawHeader(crd_header_name, crd_header_value)
        logger.debug(
            "Setting credentials header : {}".format(token_rqst.rawHeader(crd_header_name))
        )

        token_rqst.setHeader(token_rqst.ContentTypeHeader, ct_header_value)
        logger.debug(
            "Setting 'Content-Type' header : {}".format(
                token_rqst.header(token_rqst.ContentTypeHeader)
            )
        )

        # creating data
        data = QByteArray()
        data.append(urlencode({"grant_type": "client_credentials"}))
        logger.debug("Creating data : {}".format(data))

        # requesting and handle reply
        logger.debug("Asking for token")
        token_reply = self.naMngr.post(token_rqst, data)
        token_reply.finished.connect(partial(self.api_handle_token, reply=token_reply))

    def api_handle_token(self, reply):
        logger.debug("\n------------------ Token retrieval ------------------")
        logger.debug("Token asked and API reply received : {}".format(reply))

        logger.debug("Storage and formatting of the reply")
        bytarray = reply.readAll()
        content = bytarray.data().decode("utf8")

        # check API response structure
        try:
            parsed_content = json.loads(content)
        except:
            logger.debug("Reply format issue")
            return
        logger.debug("Reply format is good")

        if "access_token" in parsed_content:
            self.token = "Bearer " + parsed_content.get("access_token")
            logger.debug("TOKEN STORED")
            self.api_get_request()
        else:
            logger.debug("ya une couille dans la magouille : {}".format(parsed_content))

    def api_get_request(self):
        logger.debug("\n------------------ Sending request ------------------")

        # creating credentials header
        logger.debug("Creating credentials header")

        crd_header_value = QByteArray()
        crd_header_value.append(self.token)

        crd_header_name = QByteArray()
        crd_header_name.append("Authorization")

        # creating request
        rqst = QNetworkRequest(QUrl(self.request_url))
        logger.debug("Creating request : {}".format(rqst.url()))

        # setting credentials header
        rqst.setRawHeader(crd_header_name, crd_header_value)
        logger.debug("Setting credentials header : {}".format(rqst.rawHeader(crd_header_name)))

        # sending request
        rqst_reply = self.naMngr.get(rqst)
        logger.debug("Sending request")

        rqst_reply.finished.connect(partial(self.api_handle_request, reply=rqst_reply))

    def api_handle_request(self, reply):
        logger.debug("\n------------------ Reply retrieval ------------------")
        logger.debug("Request sent and API reply received : {}".format(reply))

        logger.debug("Storage and formatting of the reply")
        bytarray = reply.readAll()
        content = bytarray.data().decode("utf8")

        # check API response structure
        try:
            parsed_content = json.loads(content)
        except:
            logger.debug("Reply format issue")
            return
        logger.debug("Reply format is good")

        self.md_found = parsed_content.get("total")
        logger.debug("RESULT STORED")
        self.ui.lbl_found.setText("{} resources found".format(self.md_found))

        if self.md_found == self.md_expected:
            logger.debug("!!! It's working !!!")
        else:
            logger.debug("It's NOT working")


# #############################################################################
# ##### Stand alone program ########
# ##################################

if __name__ == "__main__":
    Api = ApiConnection("client_secrets.json")
