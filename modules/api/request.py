# -*- coding: utf-8 -*-

# Standard library
import logging
import json
import base64
from urllib.parse import urlencode

# PyQGIS
from qgis.core import QgsNetworkAccessManager, QgsMessageLog
from qgis.utils import iface

# PyQT
from qgis.PyQt.QtCore import QByteArray, QUrl, pyqtSignal
from qgis.PyQt.QtNetwork import QNetworkRequest, QNetworkReply
from qgis.PyQt.QtWidgets import QMessageBox

# ############################################################################
# ########## Globals ###############
# ##################################

logger = logging.getLogger("IsogeoQgisPlugin")
msgBar = iface.messageBar()

# ############################################################################
# ########## Classes ###############
# ##################################


class ApiRequester(QgsNetworkAccessManager):
    """Basic class to manage direct interactions with Isogeo's API :
        - Authentication request for tokenl
        - Request about application's shares
        - Request about ressources
        - Building request URLs
    """

    api_sig = pyqtSignal(str)
    search_sig = pyqtSignal(dict, dict)
    details_sig = pyqtSignal(dict, dict)
    shares_sig = pyqtSignal(list)
    error_sig = pyqtSignal(str)

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

    def create_request(self, request_type: str):
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
            header_value.append(
                base64.b64encode("{}:{}".format(self.app_id, self.app_secret).encode())
            )
            # creating the QNetworkRequest from oAuth2 authentication URL
            request = QNetworkRequest(QUrl(self.api_url_token))
            # creating and setting the 'Content-type header'
            ct_header_value = QByteArray()
            ct_header_value.append("application/json")
            request.setHeader(request.ContentTypeHeader, ct_header_value)
        # for other request_type, setting appropriate url
        else:
            if request_type == "shares":
                url = QUrl("{}/shares".format(self.api_url_base))
            elif request_type == "search" or request_type == "details":
                url = QUrl(self.currentUrl)
            else:
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
        logger.debug(
            "-------------- Sending a '{}' request --------------".format(request_type)
        )
        # creating the QNetworkRequest appropriate to the request_type
        request = self.create_request(request_type)
        logger.debug("to : {}".format(request.url().toString()))
        # post request for 'token' request
        if request_type == "token":
            data = QByteArray()
            data.append(urlencode({"grant_type": "client_credentials"}))
            self.post(request, data)
        # get request for other
        else:
            self.get(request)
        return

    def handle_reply(self, reply: QNetworkReply):
        """Slot to QNetworkAccesManager.finished signal who handles the API's response to any type
        of request : 'token', 'search', 'shares' or 'details'.

        The request's type is identicated from the url of the request from which the answer comes.
        Depending on the reply's content validity and the request's type, an appropriated signal
        is emitted with different data's value.

        - For token requests : the api_sig signal is emitted wathever the replys's content but
        the mitted str's value depend on this content. A single slot is connected to this signal
        and acts according to value of the string recieved (see isogeo.py : Isogeo.token_slot).
        - For other requests : for each type of request there is a corresponding signal but the
        reply's parsed content is emitted wathever the request's type. Each signal is connected to
        an appropriate slot (see isogeo.py).

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
                    logger.error(
                        "'No JSON object could be decoded' --> Internet connection failed"
                    )
                    self.api_sig.emit("internet_issue")
                else:
                    pass
                return
            url = reply.url().toString()
            # for token request, one signal is emitted passing a string whose
            # value depend on the reply content
            if "token" in url:
                logger.debug("Handling reply to a 'token' request")
                logger.debug("(from : {}).".format(url))

                if "access_token" in parsed_content:
                    logger.debug("Authentication succeeded, access token retrieved.")

                    QgsMessageLog.logMessage(
                        message="Authentication succeeded", tag="Isogeo", level=0
                    )

                    # storing token
                    self.token = "Bearer " + parsed_content.get("access_token")
                    self.api_sig.emit("ok")

                elif "error" in parsed_content:
                    logger.error(
                        "Authentication request failed. 'error' in parsed_content, may be "
                        "because of invalid credentials \n API's reply content : {}".format(
                            parsed_content
                        )
                    )
                    self.api_sig.emit("creds_issue")

                else:
                    logger.warning(
                        "Authentication request failed. API's reply's has an unexpected form."
                        "\n API's reply content : {}".format(parsed_content)
                    )
                    self.api_sig.emit("unkown_reply")

            # for other types of request, a different signal is emitted depending
            # on the type of request but always passing the reply's content
            else:
                self.loopCount = 0
                if "shares" in url:
                    logger.debug("Handling reply to a 'shares' request")
                    logger.debug("(from : {}).".format(url))
                    if len(parsed_content) > 0:
                        self.shares_sig.emit(parsed_content)
                    else :
                        self.api_sig.emit("shares_issue")
                elif "resources/search?" in url:
                    logger.debug("Handling reply to a 'search' request")
                    logger.debug("(from : {}).".format(url))
                    self.search_sig.emit(
                        parsed_content, self.get_tags(parsed_content.get("tags"))
                    )
                elif "resources/" in reply.url().toString():
                    logger.debug("Handling reply to a 'details' request")
                    logger.debug("(from : {}).".format(url))
                    self.details_sig.emit(
                        parsed_content, self.get_tags(parsed_content.get("tags"))
                    )
                else:
                    logger.debug("Unkown reply type : {}".format(parsed_content))
            del parsed_content

        # if replys's content is invalid
        elif reply.error() == 204:
            logger.debug("Token expired. Renewing it.")
            self.loopCount = 0
            self.send_request("token")

        elif reply.error() >= 101 and reply.error() <= 105:
            logger.error(
                "Request to the API failed. Proxy issue code received : {}"
                "\nsee https://doc.qt.io/qt-5/qnetworkreply.html#NetworkError-enum".format(
                    str(reply.error())
                )
            )
            self.api_sig.emit("proxy_issue")

        elif reply.error() == 302:
            logger.error(
                "Request to the API failed. Redirecting code received : 302."
                "Creds may be invalid or a proxy error wasn't catched."
            )
            self.api_sig.emit("creds_issue")

        elif content == "":
            if self.loopCount < 3:
                self.loopCount += 1
                reply.abort()
                self.send_request("token")
            else:
                logger.error(
                    "Request to the API failed. Empty reply for the third time. "
                    "Weither no catalog is shared with the plugin, or there is a "
                    "problem (2 requests sent together)"
                )
                self.api_sig.emit("shares_issue")

        else:
            logger.warning(
                "Request to the API failed. Unkown error : {}"
                "\n(see https://doc.qt.io/qt-5/qnetworkreply.html#NetworkError-enum)".format(
                    str(reply.error())
                )
            )

            self.api_sig.emit("unkown_error")
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
        if params.get("owners") is not None:
            filters += params.get("owners") + " "
        # SRS
        if params.get("srs") is not None:
            filters += params.get("srs") + " "
        # INSPIRE keywords
        if params.get("inspire") is not None:
            filters += params.get("inspire") + " "
        # Format
        if params.get("formats") is not None:
            filters += params.get("formats") + " "
        # Data type
        if params.get("types") is not None:
            filters += params.get("types") + " "
        # Contact
        if params.get("contacts") is not None:
            filters += params.get("contacts") + " "
        # License
        if params.get("licenses") is not None:
            filters += params.get("licenses") + " "
        # Formating the filters
        if filters != "":
            filters = "q=" + filters[:-1]
        # Geographical filter
        if params.get("geofilter") is not None:
            if params.get("coord") is not False:
                filters += "&box={0}&rel={1}".format(
                    params.get("coord"), params.get("operation")
                )
            else:
                pass
        else:
            pass
        # Sorting order and direction
        if params.get("show"):
            filters += "&ob={0}&od={1}".format(params.get("ob"), params.get("od"))
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

    def get_tags(self, tags: dict):
        """ This parse the tags contained in API_answer[tags] and class them so
        they are more easy to handle in other function such as update_fields()

        :param dict tags: a dict of tags as thez are return by the API

        return: a dict containing one dict for each type of tags

        rtype: dict(dict)
        """
        # set dicts
        actions = {}
        contacts = {}
        formats = {}
        inspire = {}
        keywords = {}
        licenses = {}
        md_types = {}
        owners = {}
        srs = {}
        # unused = {}
        # 0/1 values
        compliance = 0
        type_dataset = 0
        # parsing tags
        for tag in sorted(tags.keys()):
            # actions
            if tag.startswith("action"):
                actions[tags.get(tag, tag)] = tag
                continue
            # compliance INSPIRE
            elif tag.startswith("conformity"):
                compliance = 1
                continue
            # contacts
            elif tag.startswith("contact"):
                contacts[tags.get(tag)] = tag
                continue
            # formats
            elif tag.startswith("format"):
                formats[tags.get(tag)] = tag
                continue
            # INSPIRE themes
            elif tag.startswith("keyword:in"):
                inspire[tags.get(tag)] = tag
                continue
            # keywords
            elif tag.startswith("keyword:is"):
                keywords[tags.get(tag)] = tag
                continue
            # licenses
            elif tag.startswith("license"):
                licenses[tags.get(tag)] = tag
                continue
            # owners
            elif tag.startswith("owner"):
                owners[tags.get(tag)] = tag
                continue
            # SRS
            elif tag.startswith("coordinate-system"):
                srs[tags.get(tag)] = tag
                continue
            # types
            elif tag.startswith("type"):
                md_types[tags.get(tag)] = tag
                if tag in ("type:vector-dataset", "type:raster-dataset"):
                    type_dataset += 1
                continue
            # ignored tags
            else:
                # unused[tags.get(tag, tag)] = tag
                continue

        # override API tags to allow all datasets filter - see #
        if type_dataset == 2:
            md_types[self.tr("Dataset", "ApiRequester")] = "type:dataset"
        else:
            pass

        # storing dicts
        tags_parsed = {
            "actions": actions,
            "compliance": compliance,
            "contacts": contacts,
            "formats": formats,
            "inspire": inspire,
            "keywords": keywords,
            "licenses": licenses,
            "owners": owners,
            "srs": srs,
            "types": md_types,
            # "unused": unused
        }

        # method ending
        logger.info("Tags retrieved")
        return tags_parsed


# #############################################################################
# ##### Stand alone program ########
# ##################################
if __name__ == "__main__":
    """Standalone execution."""
