# -*- coding: utf-8 -*-

# Standard library
import base64
from functools import partial
import json
import logging
from urllib import urlencode

# PyQT
from PyQt4.QtCore import QByteArray, QFile, QIODevice, QSettings, QUrl
from PyQt4.QtNetwork import QNetworkAccessManager, QNetworkRequest

# PyQGIS
from qgis.core import QgsMessageLog

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
        url = QUrl('https://id.api.isogeo.com/oauth/token')
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
        if 'access_token' in parsed_content:
            logger.info("The API reply is an access token : "
                         "the request worked as expected.")
            # TO DO : Appeler la fonction d'initialisation
            self.token = "Bearer " + parsed_content['access_token']
            if self.savedSearch == "first":
                self.requestStatusClear = True
                self.set_widget_status()
            else:
                self.requestStatusClear = True
                self.send_request_to_isogeo_api(self.token)
        # TO DO : Distinguer plusieurs cas d'erreur
        elif 'error' in parsed_content:
            logger.error("The API reply is an error. Id and secret must be "
                          "invalid. Asking for them again.")
            QMessageBox.information(
                iface.mainWindow(), self.tr("Error"), parsed_content['error'])
            self.requestStatusClear = True
            self.auth_prompt_form.show()
        else:
            self.requestStatusClear = True
            logger.error("The API reply has an unexpected form : "
                          "{0}".format(parsed_content))
            QMessageBox.information(
                iface.mainWindow(), self.tr("Error"), self.tr("Unknown error"))

    # def handle_api_reply(self, answer):
    #     """Handle the different possible Isogeo API answer.

    #     This is called when the answer from the API is finished. If it's
    #     content, it calls update_fields(). If it isn't, it means the token has
    #     expired, and it calls ask_for_token()
    #     """
    #     logger.info("Request sent to API and reply received.")
    #     bytarray = answer.readAll()
    #     content = str(bytarray)
    #     if answer.error() == 0 and content != "":
    #         logger.info("Reply is a result json.")
    #         if self.showDetails is False and self.settingsRequest is False:
    #             self.loopCount = 0
    #             parsed_content = json.loads(content)
    #             self.requestStatusClear = True
    #             self.update_fields(parsed_content)
    #         elif self.showDetails is True:
    #             self.showDetails = False
    #             self.loopCount = 0
    #             parsed_content = json.loads(content)
    #             self.requestStatusClear = True
    #             self.show_complete_md(parsed_content)
    #         elif self.settingsRequest is True:
    #             self.settingsRequest = False
    #             self.loopCount = 0
    #             parsed_content = json.loads(content)
    #             self.requestStatusClear = True
    #             self.write_shares_info(parsed_content)

    #     elif answer.error() == 204:
    #         logger.info("Token expired. Renewing it.")
    #         self.loopCount = 0
    #         self.requestStatusClear = True
    #         self.ask_for_token(self.user_id, self.user_secret,
    #                            self.requestStatusClear)
    #     elif content == "":
    #         logger.info("Empty reply. Weither no catalog is shared with the "
    #                     "plugin, or there is a problem (2 requests sent "
    #                     "together)")
    #         if self.loopCount < 3:
    #             self.loopCount += 1
    #             answer.abort()
    #             del answer
    #             self.requestStatusClear = True
    #             self.ask_for_token(self.user_id, self.user_secret,
    #                                self.requestStatusClear)
    #         else:
    #             self.requestStatusClear = True
    #             msgBar.pushMessage(
    #                 self.tr("The script is looping. Make sure you shared a "
    #                         "catalog with the plugin. If so, please report "
    #                         "this on the bug tracker."))
    #     else:
    #         self.requestStatusClear = True
    #         QMessageBox.information(iface.mainWindow(),
    #                                 self.tr("Error"),
    #                                 self.tr("You are facing an unknown error. "
    #                                         "Code: ") +
    #                                 str(answer.error()) +
    #                                 "\nPlease report tis on the bug tracker.")
    #     # method end
    #     return

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
        url = 'https://v1.api.isogeo.com/resources/search?'
        # Build the url according to the params
        if params.get("text") != "":
            filters = params.get("text") + " "
        else:
            filters = ""
        # Owner
        if params.get('owner') is not None:
            filters += params.get('owner') + " "
        # INSPIRE keywords
        if params.get('inspire') is not None:
            filters += params.get('inspire') + " "
        # Format
        if params.get('format') is not None:
            filters += params.get('format') + " "
        # Data type
        if params.get('datatype') is not None:
            filters += params.get('datatype') + " "
        # Action : view
        if params.get("view"):
            filters += "action:view "
        # Action : download
        if params.get("download"):
            filters += "action:download "
        # Action : Other
        if params.get("other"):
            filters += "action:other "
        # No actions
        if params.get("noaction"):
            filters += "has-no:action "
        # Keywords
        for keyword in params.get("keys"):
            filters += keyword + " "
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

    def get_tags(self, answer):
        """Return a tag dictionnary from the API answer.

        This parse the tags contained in API_answer[tags] and class them so
        they are more easy to handle in other function such as
        update_fields()
        """
        # Initiating the dicts
        tags = answer.get('tags')
        resources_types = {}
        owners = {}
        keywords = {}
        themeinspire = {}
        formats = {}
        srs = {}
        actions = {}
        conformity = 0
        # loops that sort each tag in the corresponding dict, keeping the
        # same "key : value" structure.
        for tag in tags.keys():
            # owners
            if tag.startswith('owner'):
                owners[tag] = tags.get(tag)
            # custom keywords
            elif tag.startswith('keyword:isogeo'):
                keywords[tag] = tags.get(tag)
            # INSPIRE themes
            elif tag.startswith('keyword:inspire-theme'):
                themeinspire[tag] = tags.get(tag)
            # formats
            elif tag.startswith('format'):
                formats[tag] = tags.get(tag)
            # coordinate systems
            elif tag.startswith('coordinate-system'):
                srs[tag] = tags.get(tag)
            # available actions (the last 2 are a bit specific as the value
            # field is empty and have to be filled manually)
            elif tag.startswith('action'):
                if tag.startswith('action:view'):
                    actions[tag] = u'View'
                elif tag.startswith('action:download'):
                    actions[tag] = u'Download'
                elif tag.startswith('action:other'):
                    actions[tag] = u'Other action'
                # Test : to be removed eventually
                else:
                    actions[tag] = u'fonction get_tag à revoir'
                    self.dockwidget.txt_input.setText(tag)
            # resources type
            elif tag.startswith('type'):
                if tag.startswith('type:vector'):
                    resources_types[tag] = u'Vecteur'
                elif tag.startswith('type:raster'):
                    resources_types[tag] = u'Raster'
                elif tag.startswith('type:resource'):
                    resources_types[tag] = u'Ressource'
                elif tag.startswith('type:service'):
                    resources_types[tag] = u'Service géographique'
            elif tag.startswith('conformity'):
                conformity = 1

        # Creating the final object the function will return : a dictionary
        # of dictionaries
        new_tags = {}
        new_tags['type'] = resources_types
        new_tags['owner'] = owners
        new_tags['keywords'] = keywords
        new_tags['themeinspire'] = themeinspire
        new_tags['formats'] = formats
        new_tags['srs'] = srs
        new_tags['actions'] = actions
        new_tags['inspire_conformity'] = conformity

        # log
        logger.info("Tags retrieved")
        # method ending
        return new_tags
