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
from qgis.PyQt.QtCore import QByteArray, QUrl, pyqtSignal
from qgis.PyQt.QtNetwork import QNetworkRequest, QNetworkReply

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
        - Parsing API's answer tags
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

    def setup_api_params(self, dict_params: dict):
        """Store API parameters of the application (URLs and credentials) in class
        attributes.

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
        """Creates a QNetworkRequest() with appropriate headers and URL according to the
        'request_type' parameter.

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
        """ Sends a request to the Isogeo's API using QNetworkRequestManager. That's the
        handle_reply method which get the API's response. See below.

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
            req = self.post(request, data)
        # get request for other
        else:
            req = self.get(request)
        # since https://github.com/isogeo/isogeo-plugin-qgis/issues/288, the slot is
        # connected to the request's signal and no more to QgsNetworkAccessManager's one
        # because otherweise, the plugin doesn't work on QGIS 3.8.x
        req.finished.connect(partial(self.handle_reply, req))
        return

    def handle_reply(self, reply: QNetworkReply):
        """Slot to QNetworkAccesManager.finished signal who handles the API's response
        to any type of request: 'token', 'search', 'shares' or 'details'.

        The request's type is identicated from the url of the request from which the
        answer comes. Depending on the reply's content validity and the request's type,
        an appropriated signal is emitted with different data's value.

        - api_sig is emitted when a token request is handled or when there is a problem
        with the API response. 2 slots are connected to api_sig:

            - Isogeo.token_slot: it calls the necessary methods to initialize the plugin
            when authentication is successful (when "ok" is emitted) and disables the
            plugin when it's not (when other than "ok" str is emitted).

            - UserInformer.request_slot: it displays to user the appropriated message
            when a problem with the API response is detected (when other than "ok" str
            is emitted) depending on the origin ofthe problem.

        - search_sig is emitted when the API response to a search request is handled.
        Isogeo.search_slot() is connected to this signal

        - details_sig is emitted when the API response to a details request is handled.
        MetadataDisplayer.show_complete_md() is connected to this signal

        - shares_sig is emitted when the API response to a shares request is handled.
        SharesParser.send_share_info() is connected to this signal

        :param QNetworkReply reply: Isogeo API response
        """
        url = reply.url().toString()
        logger.debug(
            "API answer from {} : \n {} --> {}".format(
                url, reply.attribute(0), reply.attribute(1)
            )
        )
        # retrieving API reply content
        bytarray = reply.readAll()
        content = bytarray.data().decode("utf8")
        # if reply's content is valid
        if reply.error() == 0 and content != "":
            try:
                parsed_content = json.loads(content)
            except ValueError as e:
                if "No JSON object could be decoded" in str(e):
                    logger.error("{} --> Internet connection failed".format(str(e)))
                    self.api_sig.emit("internet_issue")
                else:
                    pass
                return
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
                    self.shares_sig.emit(parsed_content)
                elif "resources/search?" in url:
                    logger.debug("Handling reply to a 'search' request")
                    self.search_sig.emit(
                        parsed_content, self.get_tags(parsed_content.get("tags"))
                    )
                elif "resources/" in reply.url().toString():
                    logger.debug("Handling reply to a 'details' request")
                    self.details_sig.emit(
                        parsed_content, self.get_tags(parsed_content.get("tags"))
                    )
                else:
                    logger.debug("Unkown reply type : {}".format(parsed_content))

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
                "Request to the API failed. 'the requested operation is "
                "invalid for this protocol' : 302. Creds may be invalid "
                "or a proxy error wasn't catched."
            )
            self.api_sig.emit("creds_issue")

        elif content != "":
            logger.warning(
                "Request to the API failed. Unkown error : {}"
                "\n(see https://doc.qt.io/qt-5/qnetworkreply.html#NetworkError-enum)"
                "\n Unexpected reply content : {}".format(
                    str(reply.error()), parsed_content
                )
            )

            self.api_sig.emit("unkown_error")

        else:
            if self.loopCount < 3:
                self.loopCount += 1
                reply.abort()
                self.send_request("token")
            else:
                logger.error(
                    "Request to the API failed. Empty reply for the third time. "
                    "Weither no catalog is shared with the plugin, or there is no "
                    "Internet connection. (qt error code : {} / http status code : {})".format(
                        str(reply.error()), reply.attribute(0)
                    )
                )
                self.api_sig.emit("internet_issue")

        reply.deleteLater()
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
        if params.get("datatype") is not None:
            filters += params.get("datatype") + " "
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
            md_types[self.tr("Dataset", context=__class__.__name__)] = "type:dataset"
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
            "datatype": md_types,
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
