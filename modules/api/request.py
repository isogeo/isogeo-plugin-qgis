# -*- coding: utf-8 -*-

# Standard library
import logging
import json
import base64
from urllib.parse import urlencode
from functools import partial

# PyQGIS
from qgis.core import QgsNetworkAccessManager, QgsMessageLog
from qgis.utils import iface

# PyQT
from qgis.PyQt.QtCore import QByteArray, QUrl, QObject, pyqtSignal, pyqtSlot
from qgis.PyQt.QtNetwork import QNetworkRequest, QNetworkAccessManager, QNetworkReply

# ############################################################################
# ########## Globals ###############
# ##################################

logger = logging.getLogger("IsogeoQgisPlugin")
msgBar = iface.messageBar()

# ############################################################################
# ########## Classes ###############
# ##################################

# class ApiRequester(QObject):
class ApiRequester(QgsNetworkAccessManager):
    """Basic class to manage direct interactions with Isogeo's API :
        - Authentication request for token
        - Request about application's shares
        - Request about ressources
        - Building request URLs
    """

    token_sig = pyqtSignal(str)
    search_sig = pyqtSignal(dict)
    details_sig = pyqtSignal(dict)
    shares_sig = pyqtSignal(list)

    def __init__(self):
        # inheritance
        super().__init__()

        self.tr = object

        # API client parameters :
        # creds
        self.app_id = str
        self.app_secret = str
        # URL
        self.api_url_base = str
        self.api_url_auth = str
        self.api_url_token = str
        self.api_url_redirect = str

        # Requesting operation attributes
        # manage requesting
        self.loopCount = 0
        self.status_isClear = True
        # make request
        self.token = str
        self.currentUrl = str
        self.finished.connect(self.handle_reply)

    def setup_api_params(self, dict_params: dict):
        """Store API parameters of the application (URLs and credentials)
        in class attributes.

        :param dict dict_params: a dict containing API parameters provided
        by Authenticator().manage_api_initialization method.
        """
        logger.debug("Setting api parameters")   
        self.app_id = dict_params.get("app_id", "")
        self.app_secret = dict_params.get("app_secret", "")
        self.api_url_base = dict_params.get("url_base", "")
        self.api_url_auth = dict_params.get("url_auth", "")
        self.api_url_token = dict_params.get("url_token", "")
        self.api_url_redirect = dict_params.get("url_redirect", "")
        # sending an authentication request once API parameters are storer
        self.send_request("token")
        # self.auth_post_get_token()

    def create_request(self, request_type:str):
        """Creates a QNetworkRequest() with appropriate headers and URL
        according to the 'request_type' parameter.
        
        :param str request_type: type of request to create. Options:
            - 'token'
            - 'search'
            - 'details'
            - 'shares'

        :returns: the QNetworkRequest to send to the Isogeo's API

        :rtype: QNetworkRequest
        """
        logger.debug("Creating a '{}' request".format(request_type))
        # creating headers (same steps wathever request_type value)
        header_value = QByteArray()
        header_name = QByteArray()
        header_name.append("Authorization")
        # for token request
        if request_type == "token":
            # filling request header with credentials
            header_value.append("Basic ")
            header_value.append(base64.b64encode("{}:{}".format(self.app_id, self.app_secret).encode()))
            # creating the QNetworkRequest from oAuth2 authentication URL     
            request = QNetworkRequest(QUrl(self.api_url_token))
            # creating and setting the 'Content-type header' 
            ct_header_value = QByteArray()
            ct_header_value.append("application/json")
            request.setHeader(request.ContentTypeHeader, ct_header_value)
        # for other request_type, setting appropriate url
        else : 
            if request_type == "shares":
                url = QUrl("{}/shares".format(self.api_url_base))
            elif request_type == "search" or request_type == "details" :
                url = QUrl(self.currentUrl)
            else :
                logger.debug("Unkown request type asked : {}".format(request_type))
                raise ValueError
            # filling request header with token
            header_value.append(self.token)
            request = QNetworkRequest(url)
        # creating QNetworkRequest from appropriate url
        request.setRawHeader(header_name, header_value)
        return request

    def send_request(self, request_type: str = "search"):
        """ Sends a request to the Isogeo's API using QNetworkRequestManager.
        That's the handle_reply method which get the API's response. See below.
        
        :param str request_type: type of request to send. Options:
            - 'token'
            - 'search'
            - 'details'
            - 'shares'
        """
        logger.debug("-------------- Sending a '{}' request --------------".format(request_type))
        # creating the QNetworkRequest appropriate to the request_type
        request = self.create_request(request_type)
        logger.debug("to : {}".format(request.url().toString()))
        # post request for 'token' request 
        if request_type == "token":
            data = QByteArray()
            data.append(urlencode({"grant_type": "client_credentials"}))
            reply = self.post(request, data)
        # get request for other
        else :
            reply = self.get(request)
        return

    def handle_reply(self, reply: QNetworkReply):
        """Slot to QNetworkAccesManager.finished signal who handles the API's response to any type 
        of request : 'token', 'search', 'shares' or 'details'.

        The request's type is identicated from the url of the request from which the answer comes. 
        Depending on the reply's content validity and the request's type, an appropriated signal 
        is emitted with different data's value.

        - For token requests : the token_sig signal is emitted wathever the replys's content but the emitted 
        str's value depend on this content. A single slot is connected to this signal and acts 
        according to value of the string recieved (see isogeo.py : Isogeo.token_slot).
        - For other requests : for each type of request there is a corresponding signal but the reply's 
        parsed content is emitted wathever the request's type. Each signal is connected to an appropriate 
        slot (see isogeo.py).

        :param QNetworkReply reply: Isogeo API response
        """

        # retrieving API reply content
        bytarray = reply.readAll()
        content = bytarray.data().decode("utf8")
        # if reply's content is valid
        if reply.error() == 0 and content != "":
            try:
                parsed_content = json.loads(content)
            except ValueError as e:
                if "No JSON object could be decoded" in str(e):
                    logger.error("Internet connection failed")
                else:
                    pass
                return
        
            url = reply.url().toString()
            # for token request, one signal is emitted with different data's value
            # depending on the reply content
            if "token" in url:
                logger.debug("Handling reply to a 'token' request")
                logger.debug("(from : {}).".format(url))
                if 'access_token' in parsed_content:
                    QgsMessageLog.logMessage("Authentication succeeded", "Isogeo")
                    logger.debug("Access token retrieved.")
                    # storing token
                    self.token = "Bearer " + parsed_content.get('access_token')
                    self.token_sig.emit("tokenOK")
                elif 'error' in parsed_content:
                    logger.error("The API reply is an error: {}. ID and SECRET must be "
                                "invalid. Asking for them again."
                                .format(parsed_content.get('error')))
                    self.token_sig.emit("credIssue")
                else:
                    logger.debug("The API reply has an unexpected form: {}."
                                .format(parsed_content))
                    self.token_sig.emit("authIssue")
            # for other types of request, a different signal is emitted depending
            # on the type of request but the value of emitted data is always the 
            # reply's content
            else :
                self.loopCount = 0
                if "shares" in url:
                    logger.debug("Handling reply to a 'shares' request")
                    logger.debug("(from : {}).".format(url))
                    self.shares_sig.emit(parsed_content)
                elif "resources/search?" in url:
                    logger.debug("Handling reply to a 'search' request")
                    logger.debug("(from : {}).".format(url))
                    self.search_sig.emit(parsed_content)
                elif "resources/" in reply.url().toString():
                    logger.debug("Handling reply to a 'details' request")
                    logger.debug("(from : {}).".format(url))
                    self.details_sig.emit(parsed_content)
                else :
                    logger.debug("Unkown reply type")
                    return
            del parsed_content
        
        # if replys's content is invalid
        elif reply.error() == 204:
            logger.debug("Token expired. Renewing it.")
            self.loopCount = 0
            self.send_request("token")

        elif content == "":
            logger.error("Empty reply. Weither no catalog is shared with the "
                         "plugin, or there is a problem (2 requests sent "
                         "together)")
            if self.loopCount < 3:
                self.loopCount += 1
                reply.abort()
                # self.status_isClear = True
                self.send_request("token")
            else:
                # self.status_isClear = True
                msgBar.pushMessage(
                    self.tr("The script is looping. Make sure you shared a "
                            "catalog with the plugin. If so, please report "
                            "this on the bug tracker."))
                return
        else :
            logger.warning("Unknown error : {}".format(str(reply.error())))
            # self.status_isClear = True
            QMessageBox.information(self.iface.mainWindow(),
                                    self.tr("Error"),
                                    self.tr("You are facing an unknown error. "
                                            "Code: ") +
                                    str(answer.error()) +
                                    "\nPlease report it on the bug tracker.")
        return

    def build_request_url(self, params: dict):
        """Builds the request url according to the user selection. These URLs 
        are used by create_request.
        
        :param dict params: a dictionnary provided by Isogeo().get_params
        method

        :returns: the URL to send to the Isogeo's API for a search request.

        :rtype: str
        """
        # Base url for a request to Isogeo API
        url = "{}/resources/search?".format(self.api_url_base)
        # Build the url according to the params
        if params.get("text") != "":
            filters = params.get("text") + " "
        else:
            filters = ""
        # Keywords
        for keyword in params.get("keys"):
            filters += keyword + " "
        # Owner
        if params.get("owner") is not None:
            filters += params.get("owner") + " "
        # SRS
        if params.get("srs") is not None:
            filters += params.get("srs") + " "
        # INSPIRE keywords
        if params.get("inspire") is not None:
            filters += params.get("inspire") + " "
        # Format
        if params.get("format") is not None:
            filters += params.get("format") + " "
        # Data type
        if params.get("datatype") is not None:
            filters += params.get("datatype") + " "
        # Contact
        if params.get("contact") is not None:
            filters += params.get("contact") + " "
        # License
        if params.get("license") is not None:
            filters += params.get("license") + " "
        # Formating the filters
        if filters != "":
            filters = "q=" + filters[:-1]
        # Geographical filter
        if params.get("geofilter") is not None:
            if params.get("coord") is not False:
                filters += "&box={0}&rel={1}".format(params.get("coord"),
                                                    params.get("operation"))
            else:
                pass
        else:
            pass
        # Sorting order and direction
        if params.get("show"):
            filters += "&ob={0}&od={1}".format(params.get("ob"),
                                            params.get("od"))
            filters += "&_include=serviceLayers,layers"
            limit = 10
        else:
            limit = 0
        # Limit and offset
        offset = (params.get("page") - 1) * 10
        filters += "&_limit={0}&_offset={1}".format(limit, offset)
        # Language
        filters += "&_lang={0}".format(params.get("lang"))
        # BUILDING FINAL URL
        url += filters
        # method ending
        return url        

# #############################################################################
# ##### Stand alone program ########
# ##################################
if __name__ == '__main__':
    """Standalone execution."""
