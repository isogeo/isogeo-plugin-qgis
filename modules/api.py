# -*- coding: utf-8 -*-
from __future__ import (absolute_import, print_function, unicode_literals)
# Standard library
import base64
import json
import logging
from functools import partial
from urllib import urlencode

# PyQT
from PyQt4.QtCore import QByteArray, QSettings, QUrl
from PyQt4.QtGui import QMessageBox
from PyQt4.QtNetwork import QNetworkRequest

# PyQGIS
from qgis.core import QgsMessageLog
from qgis.utils import iface

# ############################################################################
# ########## Globals ###############
# ##################################

qsettings = QSettings()
logger = logging.getLogger("IsogeoQgisPlugin")

# ############################################################################
# ########## Classes ###############
# ##################################


class IsogeoApiManager(object):
    """Basic class that holds utilitary methods for the plugin."""

    def __init__(self):
        """Construct."""
        self.api_id = qsettings.value("isogeo-plugin/user-auth/id", 0)
        self.api_secret = qsettings.value("isogeo-plugin/user-auth/secret", 0)
        self.currentUrl = ""
        self.request_status_clear = 1
        self.tr = object

    # API COMMUNICATION ------------------------------------------------------

    def ask_for_token(self, c_id, c_secret):
        """Ask a token from Isogeo API authentification page.

        This send a POST request to Isogeo API with the user id and secret in
        its header. The API should return an access token
        """
        # check if API access are already set
        if self.api_id != 0 and self.api_secret != 0:
            logger.info("User_authentication function is trying "
                        "to get a token from the id/secret")
            self.request_status_clear = 1
            pass
        else:
            logger.error("No id/secret.")
            return 0

        # API token request
        headervalue = "Basic " + base64.b64encode(c_id + ":" + c_secret)
        data = urlencode({"grant_type": "client_credentials"})
        databyte = QByteArray()
        databyte.append(data)
        url = QUrl("https://id.api.isogeo.com/oauth/token")
        request = QNetworkRequest(url)
        request.setRawHeader("Authorization", headervalue)
        if self.request_status_clear:
            self.request_status_clear = 0
            token_reply = self.manager.post(request, databyte)
            token_reply.finished.connect(
                partial(self.handle_token, answer=token_reply))
            QgsMessageLog.logMessage("Authentication succeeded", "Isogeo")
        else:
            pass

    def handle_token(self, answer):
        """Handle the API answer when asked for a token.

        This handles the API answer. If it has sent an access token, it calls
        the initialization function. If not, it raises an error, and ask
        for new IDs
        """
        logger.info("Asked a token and got a reply from the API.")
        bytarray = answer.readAll()
        content = str(bytarray)
        parsed_content = json.loads(content)
        if "access_token" in parsed_content:
            logger.info("The API reply is an access token : "
                        "the request worked as expected.")
            # TO DO : Appeler la fonction d'initialisation
            self.token = "Bearer " + parsed_content["access_token"]
            if self.savedSearch == "first":
                self.requestStatusClear = True
                self.set_widget_status()
            else:
                self.requestStatusClear = True
                self.send_request_to_isogeo_api(self.token)
        # TO DO : Distinguer plusieurs cas d"erreur
        elif "error" in parsed_content:
            logger.error("The API reply is an error. Id and secret must be "
                         "invalid. Asking for them again.")
            QMessageBox.information(
                iface.mainWindow(), self.tr("Error"), parsed_content["error"])
            self.requestStatusClear = True
            self.auth_prompt_form.show()
        else:
            self.requestStatusClear = True
            logger.error("The API reply has an unexpected form : "
                         "{0}".format(parsed_content))
            QMessageBox.information(
                iface.mainWindow(), self.tr("Error"), self.tr("Unknown error"))

    def send_request_to_isogeo_api(self, token, limit=10):
        """Send a content url to the Isogeo API.

        This takes the currentUrl variable and send a request to this url,
        using the token variable.
        """
        myurl = QUrl(self.currentUrl)
        request = QNetworkRequest(myurl)
        request.setRawHeader("Authorization", token)
        if self.requestStatusClear is True:
            self.requestStatusClear = False
            api_reply = self.manager.get(request)
            api_reply.finished.connect(
                partial(self.handle_api_reply, answer=api_reply))
        else:
            pass

    # REQUEST and RESULTS ----------------------------------------------------

    def build_request_url(self, params):
        """Build the request url according to the widgets."""
        # Base url for a request to Isogeo API
        url = "https://v1.api.isogeo.com/resources/search?"
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
            filters += "&_include=links,serviceLayers,layers"
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

    def get_tags(self, tags):
        """Return a tag dictionnary from the API answer.

        This parse the tags contained in API_answer[tags] and class them so
        they are more easy to handle in other function such as
        update_fields()
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
            md_types[self.tr("Dataset", "IsogeoApiManager")] = "type:dataset"
        else:
            pass

        # storing dicts
        tags_parsed = {"actions": actions,
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
