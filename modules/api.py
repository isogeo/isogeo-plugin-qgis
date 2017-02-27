# -*- coding: utf-8 -*-

# Standard library
import base64
from functools import partial
import logging
from urllib import urlencode

# PyQT
from PyQt4.QtCore import QByteArray, QSettings, QUrl
from PyQt4.QtNetwork import QNetworkRequest

# PyQGIS
from qgis.core import QgsMessageLog


class IsogeoApiManager(object):
    """Basic class that holds utilitary methods for the plugin."""

    def ask_for_token(self, c_id, c_secret):
        """Ask a token from Isogeo API authentification page.

        This send a POST request to Isogeo API with the user id and secret in
        its header. The API should return an access token
        """
        headervalue = "Basic " + base64.b64encode(c_id + ":" + c_secret)
        data = urlencode({"grant_type": "client_credentials"})
        databyte = QByteArray()
        databyte.append(data)
        url = QUrl('https://id.api.isogeo.com/oauth/token')
        request = QNetworkRequest(url)
        request.setRawHeader("Authorization", headervalue)
        if self.requestStatusClear is True:
            self.requestStatusClear = False
            token_reply = self.manager.post(request, databyte)
            token_reply.finished.connect(
                partial(self.handle_token, answer=token_reply))

        QgsMessageLog.logMessage("Authentication succeeded", "Isogeo")

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
            limit = 15
        else:
            limit = 0
        # Limit and offset
        offset = (params.get("page") - 1) * 15
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
        tags = answer['tags']
        resources_types = {}
        owners = {}
        keywords = {}
        themeinspire = {}
        formats = {}
        srs = {}
        actions = {}
        # loops that sort each tag in the corresponding dict, keeping the
        # same "key : value" structure.
        for tag in tags.keys():
            # owners
            if tag.startswith('owner'):
                owners[tag] = tags[tag]
            # custom keywords
            elif tag.startswith('keyword:isogeo'):
                keywords[tag] = tags[tag]
            # INSPIRE themes
            elif tag.startswith('keyword:inspire-theme'):
                themeinspire[tag] = tags[tag]
            # formats
            elif tag.startswith('format'):
                formats[tag] = tags[tag]
            # coordinate systems
            elif tag.startswith('coordinate-system'):
                srs[tag] = tags[tag]
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

        # log
        logging.info("Tags retrieved")
        # method ending
        return new_tags

    def user_authentication(self):
        """Test the validity of the user id and secret.

        This is the first major function the plugin calls when executed. It
        retrieves the id and secret from the config file. If they are set to
        their default value, it asks for them.
        If not, it tries to send a request.
        """
        s = QSettings()
        self.user_id = s.value("isogeo-plugin/user-auth/id", 0)
        self.user_secret = s.value("isogeo-plugin/user-auth/secret", 0)
        if self.user_id != 0 and self.user_secret != 0:
            logging.info("User_authentication function is trying "
                         "to get a token from the id/secret")
            self.ask_for_token(self.user_id, self.user_secret)
        else:
            logging.info("No id/secret. User authentication function "
                         "is showing the auth window.")
            self.auth_prompt_form.show()
