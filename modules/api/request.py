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
from qgis.PyQt.QtCore import QByteArray, QUrl, QObject, pyqtSignal
from qgis.PyQt.QtNetwork import QNetworkRequest

# ############################################################################
# ########## Globals ###############
# ##################################

logger = logging.getLogger("IsogeoQgisPlugin")
msgBar = iface.messageBar()

# ############################################################################
# ########## Classes ###############
# ##################################

class ApiRequester(QObject):
    """Basic class to manage direct interactions with Isogeo's API :
        - Authentication request for token
        - Request about ressources
        - Building request URLs
    """

    reply_ready = pyqtSignal()
    token_received = pyqtSignal(str)

    def __init__(self):

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
        self.currentURL = str
        self.oldUrl = str
        self.qgs_nam = QgsNetworkAccessManager.instance()
        # store api reply 
        self.reply_content = {}

        # inheritance
        super().__init__()

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

        self.api_auth_post_get_token()

    def api_auth_post_get_token(self):
        """Ask a token from Isogeo API authentification page.
        This send a POST request to Isogeo API with the user id and secret in
        its header. The API should return an access token.

        That's the api_auth_handle_token method which get the API's response. See below.
        """
        logger.debug("Use loaded credentials to authenticate the plugin.")

        # creating credentials header
        header_value = QByteArray()
        header_value.append("Basic ")
        header_value.append(base64.b64encode("{}:{}".format(self.app_id, self.app_secret).encode()))

        header_name = QByteArray()
        header_name.append("Authorization")
        
        # creating Content-Type header
        ct_header_value = QByteArray()
        ct_header_value.append("application/json")

        #creating data
        databyte = QByteArray()
        databyte.append(urlencode({"grant_type": "client_credentials"}))

        # build URL request
        url = QUrl(self.api_url_token)
        request = QNetworkRequest(url)
        
        # setting headers
        request.setRawHeader(header_name, header_value)
        request.setHeader(request.ContentTypeHeader, ct_header_value)
        
        if self.status_isClear is True:
            self.status_isClear = False
            logger.debug("Token POST request sent to {}".format(request.url()))

            token_reply = self.qgs_nam.post(request, databyte)
            token_reply.finished.connect(partial(self.api_auth_handle_token, answer = token_reply))

        else:
            logger.debug("Network in use. Try again later.")
    
    def api_auth_handle_token(self, answer: object):
        """Handle the API answer when asked for a token.
        This handles the API answer. The token_received signal is emitted
        providing data (str) whose value dependes on the content of the 
        answer. Options:
            - 'noInternet' 
            - 'tokenOk'
            - 'credIssue'
            - 'authIssue'
        The Isogeo().token_result method is connected to this signal and launches
        different actions depending on tha data provided's value once the API's
        response is received and handled.

        :param QNetworkReply answer: Isogeo ID API response
        """
        logger.debug("Asked a token and got a reply from the API: {}".format(answer))
        bytarray = answer.readAll()
        content = bytarray.data().decode("utf8")
        # check API response structure
        try:
            parsed_content = json.loads(content)
        except ValueError as e:
            if "No JSON object could be decoded" in str(e):
                logger.error("Internet connection failed")
                self.token_received.emit("noInternet")

            else:
                pass
            return

        self.status_isClear = True
        # if structure is OK, parse and check response status
        if 'access_token' in parsed_content:
            QgsMessageLog.logMessage("Authentication succeeded", "Isogeo")
            logger.debug("Access token retrieved.")
            self.token = "Bearer " + parsed_content.get('access_token')
            self.token_received.emit("tokenOk")

        # TO DO : Distinguer plusieurs cas d'erreur
        elif 'error' in parsed_content:
            logger.error("The API reply is an error: {}. ID and SECRET must be "
                         "invalid. Asking for them again."
                         .format(parsed_content.get('error')))
            self.token_received.emit("credIssue")

        else:
            logger.debug("The API reply has an unexpected form: {}"
                          .format(parsed_content))
            self.token_received.emit("authIssue")
        
    def api_get_requests(self):
        """Send a content url to the Isogeo API.
        This takes the currentUrl class attribute and send a request to this url,
        using the token class attribute. 
        
        That's the api_requests_handle_reply method which get the API's response. See below.
        """
        logger.debug("Send a request to the 'currentURL' set: {}."
                     .format(self.currentUrl))
        
        # creating credentials header
        header_value = QByteArray()
        header_value.append(self.token)
        header_name = QByteArray()
        header_name.append("Authorization")
        
        myurl = QUrl(self.currentUrl)
        request = QNetworkRequest(myurl)
        request.setRawHeader(header_name, header_value)
        if self.status_isClear is True:
            self.status_isClear = False
            api_reply = self.qgs_nam.get(request)
            api_reply.finished.connect(partial(self.api_requests_handle_reply, answer=api_reply))
        else:
            pass

    def api_requests_handle_reply(self, answer: object):
        """Handle the different possible Isogeo API answer.
        This is called when the answer from the API is finished. 
            -If no error occured and the API's response is not empty, 
            the reply_ready signal is emitted. The Isogeo class' method 
            connected to this signal depends on the context in which the 
            api_get_requests method was called. 
            - If API's response is empty, an error message is displayed to 
            the user. 
            - In other cases, api_auth_post_get_token() method is called.

        :param QNetworkReply answer: Isogeo API search response
        """
        logger.info("Request sent to API and reply received.")
        bytarray = answer.readAll()
        content = bytarray.data().decode("utf8")
        if answer.error() == 0 and content != "":
            logger.debug("Reply is a result json.")
            self.loopCount = 0
            self.status_isClear = True

            parsed_content = json.loads(content)
            self.reply_content = parsed_content
            del parsed_content
            self.reply_ready.emit()
                    
        elif answer.error() == 204:
            logger.debug("Token expired. Renewing it.")
            self.loopCount = 0
            self.status_isClear = True
            self.api_auth_post_get_token()
        elif content == "":
            logger.error("Empty reply. Weither no catalog is shared with the "
                         "plugin, or there is a problem (2 requests sent "
                         "together)")
            if self.loopCount < 3:
                self.loopCount += 1
                answer.abort()
                del answer
                self.status_isClear = True
                self.api_auth_post_get_token()
            else:
                self.status_isClear = True
                msgBar.pushMessage(
                    self.tr("The script is looping. Make sure you shared a "
                            "catalog with the plugin. If so, please report "
                            "this on the bug tracker."))
        else:
            self.status_isClear = True
            QMessageBox.information(self.iface.mainWindow(),
                                    self.tr("Error"),
                                    self.tr("You are facing an unknown error. "
                                            "Code: ") +
                                    str(answer.error()) +
                                    "\nPlease report it on the bug tracker.")
        # method end
        return

    def build_request_url(self, params: dict):
            """Build the request url according to the user selection. These URLs 
            are used by api_get_requests.
            
            :param dict params: a dictionnary provided by Isogeo().get_params
            method
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
