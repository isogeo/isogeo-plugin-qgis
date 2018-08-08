# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
# Standard library
import base64
import json
import logging
from functools import partial
from os import path, rename
from urllib import urlencode
import time

# PyQT
from qgis.PyQt.QtCore import QByteArray, QSettings, QUrl
from qgis.PyQt.QtGui import QMessageBox
from qgis.PyQt.QtNetwork import QNetworkRequest

# PyQGIS
from qgis.core import (QgsMessageLog, QgsNetworkAccessManager)
from qgis.utils import iface

# Plugin modules
from .tools import IsogeoPlgTools

# ############################################################################
# ########## Globals ###############
# ##################################

logger = logging.getLogger("IsogeoQgisPlugin")
qsettings = QSettings()
plg_tools = IsogeoPlgTools()

# ############################################################################
# ########## Classes ###############
# ##################################


class IsogeoPlgApiMngr(object):
    """Isogeo API manager."""
    # ui reference - authentication form
    ui_auth_form = object

    # api parameters
    api_app_id = ""
    api_app_secret = ""
    api_url_base = "https://v1.api.isogeo.com/"
    api_url_auth = "https://id.api.isogeo.com/oauth/authorize"
    api_url_token = "https://id.api.isogeo.com/oauth/token"
    api_url_redirect = "http://localhost:5000/callback"

    # plugin credentials storage parameters
    credentials_storage = {
        "QSettings": 0,
        "oAuth2_file": 0,
        }
    auth_folder = ""

    # requests stuff
    req_status_isClear = True
    req_qgs_ntwk_mngr_auth = QgsNetworkAccessManager.instance()
    req_qgs_ntwk_mngr_md = QgsNetworkAccessManager.instance()
    req_qgs_ntwk_mngr_search = QgsNetworkAccessManager.instance()
    #req_qgs_ntwk_mngr.finished.connect(urlCallFinished)

    def __init__(self, auth_folder=r"../_auth"):
        """Check and manage authentication credentials."""
        # tooling - workaround circular of circular import...
        #plg_tools = IsogeoPlgTools()

        # API URLs - Prod
        self.platform, self.api_url, self.app_url, self.csw_url,\
            self.mng_url, self.oc_url, self.ssl = plg_tools.set_base_url("prod")

        # API requests
        self.currentUrl = ""

        # translation
        self.tr = object

        # authentication
        self.auth_folder = auth_folder

        # instanciate
        super(IsogeoPlgApiMngr, self).__init__ ()

    # MANAGER -----------------------------------------------------------------
    def manage_api_initialization(self):
        """Perform several operations to use Isogeo API:
        
        1. check if existing credentials are stored into QGIS or a file
        2. check if credentials are valid requesting Isogeo API ID
        """
        # try to retrieve existing credentials from potential sources
        self.credentials_storage["QSettings"] = self.credentials_check_qsettings()
        self.credentials_storage["oAuth2_file"] = self.credentials_check_file()

        # update class attributes from credentials found
        if self.credentials_storage.get("QSettings"):
            self.credentials_update("QSettings")
        elif self.credentials_storage.get("oAuth2_file"):
            self.credentials_update("oAuth2_file")
        else:
            logger.info("No credentials found. ")
            self.display_auth_form()
            return False

        return True

    # CREDENTIALS LOCATORS ----------------------------------------------------
    def credentials_check_qsettings(self):
        """Retrieve Isogeo API credentials within QGIS QSettings."""
        if "isogeo-plugin" in qsettings.childGroups():
            logger.warning("Old credentials found and removed in QGIS QSettings: isogeo-plugin")
            qsettings.remove("isogeo-plugin")
            return False
        elif "isogeo" in qsettings.childGroups():
            # looking in child groups and clean a little if needed
            qsettings.beginGroup("isogeo")
            if "app_auth" in qsettings.childGroups():
                qsettings.remove("isogeo/app_auth")
                logger.debug("QSettings clean up - app_auth")
                pass
            if "api_auth" in qsettings.childGroups():
                qsettings.remove("isogeo/api_auth")
                logger.debug("QSettings clean up - api_auth")
                pass
            if "auth" in qsettings.childGroups() \
            and not qsettings.contains("auth/app_id"):
                qsettings.remove("isogeo/auth")
                logger.debug("QSettings clean up - bad formatted auth")
                pass
            if "auth" in qsettings.childGroups() \
            and qsettings.contains("auth/app_id"):
                logger.debug("Credentials found within QGIS QSettings: isogeo/")
                pass
            qsettings.endGroup()
            return True
        else:
            pass
        logger.debug("No Isogeo credentials found within QGIS QSettings.")
        return False

    def credentials_check_file(self):
        """Retrieve Isogeo API credentials from a file stored inside the 
        plugin _auth subfolder.
        """
        credentials_filepath = path.join(self.auth_folder, "client_secrets.json")
        # check if a client_secrets.json fil is stored inside the _auth subfolder
        if not path.isfile(credentials_filepath):
            logger.debug("No credential files found: {}"
                         .format(credentials_filepath))
            return False
        # check file structure
        try:
            plg_tools.credentials_loader(credentials_filepath)
            logger.debug("Credentials found in {}".format(credentials_filepath))
        except Exception as e:
            logger.debug(e)
            return False
        # end of method
        return True

    # CREDENTIALS SAVER -------------------------------------------------------
    def credentials_storer(self, store_location="QSettings"):
        """Store class credentials attributes into the specified store_location.
        
        :param store_location str: name of targetted store location. Options:
            - QSettings
        """
        if store_location == "QSettings":
            logger.debug("youhou")
            qsettings.setValue("isogeo/auth/app_id", self.api_app_id)
            qsettings.setValue("isogeo/auth/app_secret", self.api_app_secret)
            qsettings.setValue("isogeo/auth/url_base", self.api_url_base)
            qsettings.setValue("isogeo/auth/url_auth", self.api_url_auth)
            qsettings.setValue("isogeo/auth/url_token", self.api_url_token)
            qsettings.setValue("isogeo/auth/url_redirect", self.api_url_redirect)
        else:
            pass
        logger.debug("Credentials stored into: {}".format(store_location))

    def credentials_update(self, credentials_source="QSettings"):
        """Update class attributes from specified credentials source."""
        # update class attributes
        if credentials_source == "QSettings":
            self.api_app_id = qsettings.value("isogeo/auth/app_id", "")
            self.api_app_secret = qsettings.value("isogeo/auth/app_secret", "")
            self.api_url_base = qsettings.value("isogeo/auth/url_base", "https://v1.api.isogeo.com/")
            self.api_url_auth = qsettings.value("isogeo/auth/url_auth", "https://id.api.isogeo.com/oauth/authorize")
            self.api_url_token = qsettings.value("isogeo/auth/url_token", "https://id.api.isogeo.com/oauth/token")
            self.api_url_redirect = qsettings.value("isogeo/auth/url_redirect", "http://localhost:5000/callback")
        elif credentials_source == "oAuth2_file":
            creds = plg_tools.credentials_loader(path.join(self.auth_folder,
                                                           "client_secrets.json"))
            self.api_app_id = creds.get("client_id")
            self.api_app_secret = creds.get("client_secret")
            self.api_url_base = creds.get("uri_base")
            self.api_url_auth = creds.get("uri_auth")
            self.api_url_token = creds.get("uri_token")
            self.api_url_redirect = creds.get("uri_redirect")
            #self.credentials_storer(store_location="QSettings")
        else:
            pass

        logger.debug("Credentials updated from: {}. Application ID used: {}"
                     .format(credentials_source, self.api_app_id))

    # AUTHENTICATION FORM -----------------------------------------------------
    def display_auth_form(self):
        """Show authentication form with prefilled fields."""
        # fillfull auth form fields from stored settings
        self.ui_auth_form.ent_app_id.setText(self.api_app_id)
        self.ui_auth_form.ent_app_secret.setText(self.api_app_secret)
        self.ui_auth_form.lbl_api_url_value.setText(self.api_url_base)
        self.ui_auth_form.chb_isogeo_editor.setChecked(qsettings
                                                  .value("isogeo/user/editor", 0))
        
        # display
        logger.debug("Authentication form filled and ready to be launched.")
        self.ui_auth_form.show()

    def credentials_uploader(self):
        """Get file selected by the user and loads API credentials into plugin.
        If the selected is compliant, credentials are loaded from then it's
        moved inside plugin\_auth subfolder.
        """
        # test file structure
        try:
            selected_file = path.normpath(self.ui_auth_form.btn_browse_credentials.filePath())
            api_credentials = plg_tools.credentials_loader(selected_file)
        except Exception as e:
            logger.error(e)
            QMessageBox.critical(self.ui_auth_form,
                                 self.tr("Alert", "IsogeoPlgApiMngr"),
                                 self.tr("The selected credentials file is not correct.",
                                         "IsogeoPlgApiMngr"))
        # move credentials file into the plugin file structure
        if path.isfile(path.join(self.auth_folder, "client_secrets.json")):
            rename(path.join(self.auth_folder, "client_secrets.json"),
                   path.join(self.auth_folder, "old_client_secrets_{}.json"
                                               .format(int(time.time())))
                   )
            logger.debug("client_secrets.json already existed. "
                         "Previous file has been renamed.")
        else:
            pass
        logger.debug("YARK {}".format(path.join(self.auth_folder, "client_secrets.json")))
        rename(selected_file,
               path.join(self.auth_folder, "client_secrets.json"))
        logger.debug("Selected credentials file has been moved into plugin"
                     "_auth subfolder")

        # set form
        self.ui_auth_form.ent_app_id.setText(api_credentials.get("client_id"))
        self.ui_auth_form.ent_app_secret.setText(api_credentials.get("client_secret"))
        self.ui_auth_form.lbl_api_url_value.setText(api_credentials.get("uri_auth"))

        # update class attributes from file
        self.credentials_update(credentials_source="oAuth2_file")

        # store into QSettings if existing
        self.credentials_storer(store_location="QSettings")

    # API COMMUNICATION ------------------------------------------------------
    def auth_req_token_post(self):
        """Send a POST request to the API ID token generator.

        This send a POST request to Isogeo API with the user id and secret in
        its header. The API should return an access token
        """
        # API URL token
        url = QUrl(self.api_url_token)
        # encode oAuth2 authentication into the header
        head_autoriz = "Basic " + base64.b64encode("{}:{}".format(self.api_app_id,
                                                                  self.api_app_secret))
        data = urlencode({"grant_type": "client_credentials"})
        databyte = QByteArray()
        databyte.append(data)
        # prepare request
        request = QNetworkRequest(url)
        request.setRawHeader("Authorization", head_autoriz)
        if self.req_status_isClear:
            self.req_status_isClear = False
            request_response =  self.req_qgs_ntwk_mngr_auth.post(request, databyte)
            request_response.finished.connect(self.auth_req_token_resp)
            #hoho = req_token.finished.connect(partial(self.auth_req_token_resp,
            #                                          resp_auth_token=req_token))
            logger.debug("youpi")
            logger.debug(type(request_response))
        else:
            logger.info("A request is already being processed")

        # 
        #logger.debug("Oh YEAH")
        #QgsMessageLog.logMessage("Authentication succeeded", "Isogeo")
        #return True

    def auth_req_token_resp(self, resp_auth_token):
        """Handle the API answer when asked for a token.
        This handles the API answer. If it has sent an access token, it calls
        the initialization function. If not, it raises an error, and ask
        for new IDs

        :param QNetworkReply resp_auth_token: Isogeo ID API response
        """
        logger.debug("Asked a token and got a reply from the API")
        logger.debug(type(resp_auth_token))
        bytarray = resp_auth_token.readAll()
        content = str(bytarray)
        try:
            parsed_content = json.loads(content)
            logger.debug("TOKENIZE")
        except ValueError as e:
            if "No JSON object could be decoded" in e:
                #msgBar.pushMessage(self.tr("Request to Isogeo failed: please "
                #                           "check your Internet connection."),
                #                   duration=10,
                #                   level=msgBar.WARNING)
                logger.error("Internet connection failed")
                #self.pluginIsActive = False
            else:
                pass
            return False

        if 'access_token' in parsed_content:
            logger.debug("The API reply is an access token : "
                          "the request worked as expected.")
            # Enable buttons "save and cancel"
            self.auth_prompt_form.btn_ok_cancel.setEnabled(True)
            self.dockwidget.setEnabled(True)

            # TO DO : Appeler la fonction d'initialisation
            self.token = "Bearer " + parsed_content.get('access_token')
            if self.savedSearch == "first":
                self.requestStatusClear = True
                self.set_widget_status()
            else:
                self.requestStatusClear = True
                self.send_request_to_isogeo_api(self.token)
        # TO DO : Distinguer plusieurs cas d'erreur
        elif 'error' in parsed_content:
            logger.error("The API reply is an error. ID and SECRET must be "
                          "invalid. Asking for them again.")
            # displaying auth form
            self.auth_prompt_form.ent_app_id.setText(self.user_id)
            self.auth_prompt_form.ent_app_secret.setText(self.user_secret)
            self.auth_prompt_form.btn_ok_cancel.setEnabled(False)
            self.auth_prompt_form.show()
            msgBar.pushMessage("Isogeo",
                               self.tr("API authentication failed."
                                       "Isogeo API answered: {}")
                                       .format(parsed_content.get('error')),
                               duration=10,
                               level=msgBar.WARNING)
            self.requestStatusClear = True
        else:
            logger.debug("The API reply has an unexpected form: {}"
                          .format(parsed_content))
            msgBar.pushMessage("Isogeo",
                               self.tr("API authentication failed."
                                       "Isogeo API answered: {}")
                                       .format(parsed_content.get('error')),
                               duration=10,
                               level=msgBar.CRITICAL)
            self.requestStatusClear = True


    def handle_token(self, answer):
        """Handle the API answer when asked for a token.

        This handles the API answer. If it has sent an access token, it calls
        the initialization function. If not, it raises an error, and ask
        for new IDs

        :param QNetworkReply answer: Isogeo API response
        """
        logger.info("Asked a token and got a reply from the API.")
        logger.debug(type(answer))
        bytarray = answer.readAll()
        content = str(bytarray)
        parsed_content = json.loads(content)
        if "access_token" in parsed_content:
            logger.info("The API reply is an access token : "
                        "the request worked as expected.")
            # TO DO : Appeler la fonction d'initialisation
            self.token = "Bearer " + parsed_content["access_token"]
            if self.savedSearch == "first":
                self.req_status_isClear = True
                self.set_widget_status()
            else:
                self.req_status_isClear = True
                self.send_request_to_isogeo_api(self.token)
        # TO DO : Distinguer plusieurs cas d"erreur
        elif "error" in parsed_content:
            logger.error("The API reply is an error. Id and secret must be "
                         "invalid. Asking for them again.")
            QMessageBox.information(
                        iface.mainWindow(),
                        self.tr("Error", "IsogeoPlgApiMngr"),
                        parsed_content["error"])
            self.req_status_isClear = True
            self.auth_prompt_form.show()
        else:
            self.req_status_isClear = True
            logger.error("The API reply has an unexpected form : "
                         "{0}".format(parsed_content))
            QMessageBox.information(
                        iface.mainWindow(),
                        self.tr("Error", "IsogeoPlgApiMngr"),
                        self.tr("Unknown error", "IsogeoPlgApiMngr"))

    def send_request_to_isogeo_api(self, token, limit=10):
        """Send a content url to the Isogeo API.

        This takes the currentUrl variable and send a request to this url,
        using the token variable.
        """
        myurl = QUrl(self.currentUrl)
        request = QNetworkRequest(myurl)
        request.setRawHeader("Authorization", token)
        if self.req_status_isClear is True:
            self.req_status_isClear = False
            api_reply = self.manager.get(request)
            api_reply.finished.connect(
                partial(self.handle_api_reply, answer=api_reply))
        else:
            pass

    # REQUEST and RESULTS ----------------------------------------------------
    def build_request_url(self, params):
        """Build the request url according to the widgets."""
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

# #############################################################################
# ##### Stand alone program ########
# ##################################
if __name__ == '__main__':
    """Standalone execution."""
