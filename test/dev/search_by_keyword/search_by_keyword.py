"""
/***************************************************************************
 Isogeo
                              -------------------
        begin                : 2019-07-08
        git sha              : $Format:%H$
        copyright            : (C) 2019 by Isogeo, Simon Sampere
        email                : projects+qgis@isogeo.com
 ***************************************************************************/
/***************************************************************************

    This module has been developed in accordance with this Issue: 
    https://github.com/isogeo/isogeo-plugin-qgis/issues/194

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
import sys

# PyQT
from qgis.PyQt.QtNetwork import QNetworkAccessManager, QNetworkRequest
from qgis.PyQt.QtCore import QUrl, QByteArray, Qt
from qgis.PyQt.QtWidgets import QApplication
from qgis.PyQt.QtGui import QStandardItemModel, QStandardItem

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
log_form = logging.Formatter("%(asctime)s || %(levelname)s "
                             "|| %(module)s - %(lineno)d ||"
                             " %(funcName)s || %(message)s")
logfile = RotatingFileHandler(os.path.join(logdir, "log_api_with_pyqt.log"),"a", 5000000, 1)

logfile.setLevel(log_level)
logfile.setFormatter(log_form)

logger.addHandler(logfile)

# ############################################################################
# ########## Classes ###############
# ##################################

class KeyWordsSelection():
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

        # init variables :
        self.token = ""
        self.search_type = "init"
        self.checked_kw = {}

        # for ui (launch and display):
        logger.debug("Processing and displaying UI")
        self.app = QApplication(sys.argv)
        self.ui = AuthWidget()
        self.ui.resize(400 , 100)
        self.pysdk_checking()
        self.api_authentification()
        self.ui.btn_reset.pressed.connect(self.reset)
        self.ui.show()
        self.app.exec()

    def pysdk_checking(self):
        logger.debug("\n--------------- isogeo-pysdk ---------------")
        logger.debug("Checking credentials")
        try :
            isogeo = Isogeo(self.app_id, self.app_secrets)
            isogeo.connect()
        except OSError as e: 
            logger.debug("Credentials issue : {}".format(e))
            return
        except ValueError as e:
            logger.debug("Credentials issue : {}".format(e))
            return

        if self.search_type == "init":
            result = isogeo.search(whole_share=0, page_size=0, augment=0, tags_as_dicts=1)
        else :
            query = " ".join(list(self.checked_kw.keys()))
            result = isogeo.search(whole_share=0, page_size=0, augment=0, tags_as_dicts=1, query=query)

        self.tags_expected = result.get("tags")
        self.kw_expected_nb = len(self.tags_expected.get("keywords"))
        self.ui.lbl_expected.setText("Expected : {} resources and {} keywords".format(result.get("total") ,self.kw_expected_nb))
        logger.debug(
            "isogeo-pysdk validates the authentication file, {} accessible resources".format(result.get("total")))

    def api_authentification(self):
        logger.debug("\n------------------ Authentication ------------------")
        
        # creating credentials header
        crd_header_value = QByteArray()
        crd_header_value.append("Basic ")
        crd_header_value.append(base64.b64encode("{}:{}".format(self.app_id, self.app_secrets).encode()))

        crd_header_name = QByteArray()
        crd_header_name.append("Authorization")

        # creating Content-Type header
        ct_header_value = QByteArray()
        ct_header_value.append("application/json")

        # creating request
        token_rqst = QNetworkRequest(QUrl(self.token_url))
        
        # setting headers
        token_rqst.setRawHeader(crd_header_name, crd_header_value)
        token_rqst.setHeader(token_rqst.ContentTypeHeader, ct_header_value)
        
        # creating data
        data = QByteArray()
        data.append(urlencode({"grant_type": "client_credentials"}))

        # requesting and handle reply
        logger.debug("Asking for token")
        token_reply = self.naMngr.post(token_rqst, data)
        token_reply.finished.connect(partial(self.api_handle_token, reply = token_reply))

    def api_handle_token(self, reply):
        logger.debug("Token asked and API reply received")

        # formating API response
        bytarray = reply.readAll()
        content = bytarray.data().decode("utf8")

        # check API response structure
        try:
            parsed_content = json.loads(content)
        except :
            logger.debug("Reply format issue")
            return

        # check API response content
        if 'access_token' in parsed_content:
            self.token = "Bearer " + parsed_content.get('access_token')
            self.api_get_request()
        else :
            logger.debug("ya une couille dans la magouille : {}".format(parsed_content))

    def api_get_request(self):
        logger.debug("\n----------------- Sending request -----------------")

        # creating credentials header
        crd_header_value = QByteArray()
        crd_header_value.append(self.token)
        crd_header_name = QByteArray()
        crd_header_name.append("Authorization")

        #creating request
        rqst = QNetworkRequest(QUrl(self.request_url))

        # setting credentials header
        rqst.setRawHeader(crd_header_name, crd_header_value)#sending request

        rqst_reply = self.naMngr.get(rqst)
        rqst_reply.finished.connect(partial(self.api_handle_request, reply=rqst_reply))

    def api_handle_request(self, reply):
        logger.debug("Request sent and API reply received")
        bytarray = reply.readAll()
        content = bytarray.data().decode("utf8")
        
        if reply.error() == 0:
            # check API response structure
            try:
                parsed_content = json.loads(content)
            except:
                logger.debug("Reply format issue")
                return

            # check API response content
            self.tags_found = parsed_content.get("tags")
            self.kw_found = {}
            for tag in sorted(self.tags_found):
                if tag.startswith("keyword:is"):
                    self.kw_found[tag] = self.tags_found.get(tag)
                else :
                    pass
            
            # displaying result
            self.ui.lbl_found.setText("Found : {} resources and {} keywords".format(parsed_content.get("total") ,len(self.kw_found)))

            if self.search_type == "init":
                if len(self.kw_found) == self.kw_expected_nb :
                    logger.debug("!!! It's working !!!")
                else :
                    logger.debug("It's NOT working")
            else :
                pass

            # filling keywords checkable combo box
            self.pop_kw_cbbox()

        elif self.search_type != "init":
            logger.debug("token expired, renewing it")
            self.api_authentification()

        else :
            pass

    def pop_kw_cbbox(self):
        logger.debug(
            "\n-------------- Poping Keywords ComboBox --------------")
        
        # to prepare the filling
        self.ui.kw_cbbox.clear()
        if self.search_type != "init":
            self.ui.kw_cbbox.activated.disconnect(self.get_checked_kw)

        # filling the combobox with checkable items
        self.ui.kw_cbbox.addItem("-- Keywords --")
        first_item = self.ui.kw_cbbox.model().item(0, 0)
        first_item.setEnabled(False)
        i = 1
        for kw_code, kw_lbl in self.kw_found.items() :
            
            if self.search_type == "kw" and kw_code in self.checked_kw.keys():
                self.ui.kw_cbbox.insertItem(1, kw_lbl)
                item = self.ui.kw_cbbox.model().item(1, 0)
                item.setCheckState(Qt.Checked)
            else : 
                self.ui.kw_cbbox.addItem(kw_lbl)
                item = self.ui.kw_cbbox.model().item(i, 0)
                item.setCheckState(Qt.Unchecked)
            item.setData(kw_code, 32)
            i += 1
        logger.debug("Keywords Combobox filled")

        self.ui.kw_cbbox.setEnabled(True)
        # connecting to a signal returning the checked item's index
        self.ui.kw_cbbox.activated.connect(self.get_checked_kw)
    
    def get_checked_kw(self, index):
        logger.debug(
            "\n------------ Getting Checked Keywords ------------")

        self.ui.kw_cbbox.setEnabled(False)
        self.ui.kw_cbbox.setCurrentText(self.ui.kw_cbbox.itemText(index))

        # Testing if checked keyword is already in the dict is easier than 
        # testing if the user checked or unchecked it :
        # removing the selected keyword from the dict if it is already in        
        if self.ui.kw_cbbox.itemData(index, 32) in self.checked_kw.keys():
            del self.checked_kw[self.ui.kw_cbbox.itemData(index, 32)]
        # adding the selected keyword to the dict if it is not already in
        else:
            self.checked_kw[self.ui.kw_cbbox.itemData(index, 32)] = self.ui.kw_cbbox.itemText(index)
        logger.debug("ckeched kw : {}".format(self.checked_kw))

        self.ui.lbl_selection.setText("{} keywords selected".format(len(self.checked_kw)))
        self.ui.kw_cbbox.setToolTip(" / ".join(list(self.checked_kw.values())))
        # now selected keywords are stocked, time to request the API 
        self.kw_search()
            
    def kw_search(self):
        logger.debug(
            "\n------------ Searching with keywords -------------")
        # preparing the request
        self.search_type = "kw"
        self.request_url = self.url_builder()
        self.pysdk_checking()
        # launching the request
        self.api_get_request()

    def url_builder(self):
        logger.debug(
            "\n------------------ Building URL ------------------")
        # adding selected keywords to the request URL
        search_url = "https://v1.api.isogeo.com/resources/search?q="
        for kw in self.checked_kw:
            search_url += "{} ".format(str(kw))
        logger.debug("URL : {}".format(search_url))
        return search_url[:-1]
    
    def reset(self):
        logger.debug("----------------- RESET -------------------")
        self.search_type = "reset"
        self.checked_kw = {}
        self.request_url = "https://v1.api.isogeo.com/resources/search?_limit=0&_offset=0"
        self.ui.lbl_selection.setText("")
        self.ui.kw_cbbox.setToolTip("")
        self.pysdk_checking()
        self.api_get_request()

# #############################################################################
# ##### Stand alone program ########
# ##################################

if __name__ == "__main__":
    Api = KeyWordsSelection("client_secrets.json")
