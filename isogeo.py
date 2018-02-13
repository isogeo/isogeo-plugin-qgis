# -*- coding: utf-8 -*-

"""
/***************************************************************************
 Isogeo
                                 A QGIS plugin
 Isogeo search engine within QGIS
                              -------------------
        begin                : 2016-07-22
        git sha              : $Format:%H$
        copyright            : (C) 2016 by Isogeo, Theo Sinatti, GeoJulien
        email                : projects+qgis@isogeo.com
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
import os.path
import platform
import json
import base64
import urllib
import logging
from logging.handlers import RotatingFileHandler
from collections import OrderedDict
from functools import partial

# PyQT
# from QByteArray
from qgis.PyQt.QtCore import (QByteArray, QCoreApplication, QSettings,
                              Qt, QTranslator, QUrl, qVersion)
from qgis.PyQt.QtGui import (QAction, QIcon, QMessageBox, QStandardItemModel,
                             QStandardItem, QProgressBar)
from qgis.PyQt.QtNetwork import QNetworkAccessManager, QNetworkRequest

# PyQGIS
import db_manager.db_plugins.postgis.connector as con
from qgis.utils import iface, plugin_times, QGis
from qgis.core import (QgsAuthManager, QgsAuthMethodConfig,
                       QgsCoordinateReferenceSystem, QgsCoordinateTransform,
                       QgsDataSourceURI,
                       QgsMapLayerRegistry, QgsMessageLog,
                       QgsNetworkAccessManager,
                       QgsPoint, QgsRectangle, QgsRasterLayer, QgsVectorLayer)

# Initialize Qt resources from file resources.py
import resources

# UI classes
from ui.isogeo_dockwidget import IsogeoDockWidget  # main widget
from ui.auth.dlg_authentication import IsogeoAuthentication
from ui.credits.dlg_credits import IsogeoCredits
from ui.metadata.dlg_md_details import IsogeoMdDetails
from ui.quicksearch.dlg_quicksearch_new import QuicksearchNew
from ui.quicksearch.dlg_quicksearch_rename import QuicksearchRename

# Custom modules
from modules.api import IsogeoApiManager
from modules.metadata_display import MetadataDisplayer
from modules.results import ResultsManager
from modules.tools import Tools
from modules.url_builder import UrlBuilder

# ############################################################################
# ########## Globals ###############
# ##################################

# useful submodules and shortcuts
qgis_auth_mng = QgsAuthManager.instance()
custom_tools = Tools()
isogeo_api_mng = IsogeoApiManager()
msgBar = iface.messageBar()
network_mng = QNetworkAccessManager()
qsettings = QSettings()
srv_url_bld = UrlBuilder()

# LOG FILE ##
logger = logging.getLogger("IsogeoQgisPlugin")
logging.captureWarnings(True)
# logger.setLevel(logging.INFO)  # all errors will be get
logger.setLevel(logging.DEBUG)  # switch on it only for dev works
log_form = logging.Formatter("%(asctime)s || %(levelname)s "
                             "|| %(module)s - %(lineno)d ||"
                             "%(funcName)s || %(message)s")
logfile = RotatingFileHandler(os.path.join(
                              os.path.dirname(os.path.realpath(__file__)),
                              "log_isogeo_plugin.log"),
                              "a", 5000000, 1)
# logfile.setLevel(logging.INFO)
logfile.setLevel(logging.DEBUG)  # switch on it only for dev works
logfile.setFormatter(log_form)
logger.addHandler(logfile)

# icons
ico_bolt = QIcon(':/plugins/Isogeo/resources/bolt.svg')
ico_keyw = QIcon(':/plugins/Isogeo/resources/tag.svg')
ico_line = QIcon(':/plugins/Isogeo/resources/line.png')
ico_none = QIcon(':/plugins/Isogeo/resources/none.svg')
ico_poly = QIcon(':/plugins/Isogeo/resources/polygon.png')
ico_poin = QIcon(':/plugins/Isogeo/resources/point.png')

# ############################################################################
# ########## Classes ###############
# ##################################


class Isogeo:
    """QGIS Plugin Implementation."""

    logger.info('\n\n\t========== Isogeo Search Engine for QGIS ==========')
    logger.info('OS: {0}'.format(platform.platform()))
    try:
        logger.info('QGIS Version: {0}'.format(QGis.QGIS_VERSION))
    except UnicodeEncodeError:
        qgis_version = QGis.QGIS_VERSION.decode("latin1")
        logger.info('QGIS Version: {0}'.format(qgis_version))

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface

        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)

        # initialize locale
        locale = qsettings.value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'isogeo_search_engine_{}.qm'.format(locale))
        logger.info('Language applied: {0}'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)
            else:
                pass
        else:
            pass

        if locale == "fr":
            self.lang = "fr"
        else:
            self.lang = "en"

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Isogeo')
        self.toolbar = self.iface.addToolBar(u'Isogeo')
        self.toolbar.setObjectName(u'Isogeo')
        self.pluginIsActive = False
        self.dockwidget = None

        # network manager included within QGIS
        self.manager = QgsNetworkAccessManager.instance()
        # self.manager = QNetworkAccessManager()
        self.md_display = MetadataDisplayer(IsogeoMdDetails())

        # UI submodules
        self.auth_prompt_form = IsogeoAuthentication()
        self.quicksearch_new_dialog = QuicksearchNew()
        self.quicksearch_rename_dialog = QuicksearchRename()
        self.credits_dialog = IsogeoCredits()
        self.md_display = MetadataDisplayer(IsogeoMdDetails())
        self.results_mng = ResultsManager(self)

        # start variables
        self.savedSearch = "first"
        self.requestStatusClear = True
        self.loopCount = 0
        self.hardReset = False
        self.showResult = False
        self.showDetails = False
        self.store = False
        self.settingsRequest = False
        self.PostGISdict = srv_url_bld.build_postgis_dict(qsettings)

        self.currentUrl = ""
        # self.currentUrl = "https://v1.api.isogeo.com/resources/search?
        # _limit=10&_include=links&_lang={0}".format(self.lang)

        self.old_text = ""
        self.page_index = 1
        basepath = os.path.dirname(os.path.realpath(__file__))
        self.json_path = basepath + '/user_settings/saved_searches.json'

    # noinspection PyMethodMayBeStatic
    def tr(self, message, context="Isogeo"):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.
        :param message: String for translation.
        :type message: str, QString
        :context: str, QString
        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate(context, message)

    def add_action(self, ico_path, text, callback, enabled_flag=True, add_to_menu=True, add_to_toolbar=True, status_tip=None, whats_this=None, parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str
        :param text: Text that should be shown in menu items for this action.
        :type text: str
        :param callback: Function to be called when the action is triggered.
        :type callback: function
        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool
        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool
        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool
        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str
        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget
        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.
        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """
        ico = QIcon(ico_path)
        action = QAction(ico, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToWebMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""
        ico_path = ':/plugins/Isogeo/icon.png'
        self.add_action(
            ico_path,
            text=self.tr(u'Search within Isogeo catalogs'),
            callback=self.run,
            parent=self.iface.mainWindow())

    # --------------------------------------------------------------------------

    def onClosePlugin(self):
        """Cleanup necessary items here when plugin dockwidget is closed."""
        # disconnects
        self.dockwidget.closingPlugin.disconnect(self.onClosePlugin)

        # remove this statement if dockwidget is to remain
        # for reuse if plugin is reopened
        # Commented next statement since it causes QGIS crashe
        # when closing the docked window:
        self.dockwidget = None
        self.pluginIsActive = False
        # try:
        #     reloadPlugin("isogeo_search_engine")
        # except TypeError:
        #     pass
        # try:
        #     reloadPlugin("isogeo_search_engine_dev")
        # except TypeError:
        #     pass

    def unload(self):
        """Remove the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginWebMenu(
                self.tr(u'&Isogeo'), action)
            try:
                self.iface.mainWindow().statusBar().removeWidget(self.bar)
            except:
                pass
            self.iface.removeToolBarIcon(action)
            self.dockwidget = None
            logger.handlers = []
        # remove the toolbar
        del self.toolbar

    # --------------------------------------------------------------------------
    def user_authentication(self):
        """Test the validity of the user id and secret.
        This is the first major function the plugin calls when executed. It
        retrieves the id and secret from the config file. If they are set to
        their default value, it asks for them.
        If not, it tries to send a request.
        """
        self.user_id = qsettings.value("isogeo-plugin/user-auth/id", 0)
        self.user_secret = qsettings.value("isogeo-plugin/user-auth/secret", 0)
        if self.user_id != 0 and self.user_secret != 0:
            logging.info("User_authentication function is trying "
                         "to get a token from the id/secret")
            self.ask_for_token(self.user_id, self.user_secret)
        else:
            logging.info("No id/secret. User authentication function "
                         "is showing the auth window.")
            self.auth_prompt_form.show()

    def control_authentication(self):
        """Disable plugins features if authentication's parameters changed."""

        # Disable buttons save and cancel
        self.auth_prompt_form.btn_ok_cancel.setEnabled(False)

        # Disable all plugin's widgets
        self.switch_widgets_on_and_off(0)
        app_id = self.auth_prompt_form.ent_app_id.text()
        app_secret = self.auth_prompt_form.ent_app_secret.text()
        user_editor = self.auth_prompt_form.chb_isogeo_editor.isChecked()

        if app_id and app_secret:
            # old name maintained for compatibility reasons
            qsettings.setValue("isogeo-plugin/user-auth/id", app_id)
            qsettings.setValue("isogeo-plugin/user-auth/secret", app_secret)

            # new name to anticipate on future migration
            qsettings.setValue("isogeo/api_auth/id", app_id)
            qsettings.setValue("isogeo/api_auth/secret", app_secret)
            qsettings.setValue("isogeo/user/editor", int(user_editor))

    def write_ids_and_test(self):
        """Store the id & secret and launch the test function.
        Called when the authentification window is closed,
        it stores the values in the file, then call the
        user_authentification function to test them.
        """
        logging.info("Authentication window accepted. Writting"
                     " id/secret in QSettings.")
        app_id = self.auth_prompt_form.ent_app_id.text()
        app_secret = self.auth_prompt_form.ent_app_secret.text()
        user_editor = self.auth_prompt_form.chb_isogeo_editor.isChecked()

        # old name maintained for compatibility reasons
        qsettings.setValue("isogeo-plugin/user-auth/id", app_id)
        qsettings.setValue("isogeo-plugin/user-auth/secret", app_secret)

        # new name to anticipate on future migration
        qsettings.setValue("isogeo/api_auth/id", app_id)
        qsettings.setValue("isogeo/api_auth/secret", app_secret)
        qsettings.setValue("isogeo/user/editor", int(user_editor))

        # anticipating on QGIS Auth Management
        if qgis_auth_mng.authenticationDbPath():
            logger.info("TRACKING - AUTH: new QGIS system already initialized")
            auth_isogeo_id = qsettings.value("isogeo/app_auth/qgis_auth_id")
            # already initialised => we are inside a QGIS app.
            if (qgis_auth_mng.masterPasswordIsSet() and
               auth_isogeo_id in qgis_auth_mng.availableAuthMethodConfigs()):
                logger.info("TRACKING - AUTH: master password has been set"
                            " and Isogeo auth config already exists."
                            " Let's update it if needed.")
                # get existing Isogeo auth id
                auth_isogeo = qgis_auth_mng.availableAuthMethodConfigs()\
                                           .get(auth_isogeo_id)
                # update values from form
                auth_isogeo.setConfig("username", app_id)
                auth_isogeo.setConfig("password", app_secret)
                # check if method parameters are correctly set and store it
                if auth_isogeo.isValid():
                    qgis_auth_mng.updateAuthenticationConfig(auth_isogeo)
                else:
                    logger.error("AUTH - Fail to create and store configuration")
            elif (qgis_auth_mng.masterPasswordIsSet() and
                  auth_isogeo_id not in qgis_auth_mng.availableAuthMethodConfigs()):
                logger.info("TRACKING - AUTH: master password has been set"
                            " and Isogeo auth config doesn't exist yet")
                auth_isogeo_cfg = QgsAuthMethodConfig()
                auth_isogeo_cfg.setName("Isogeo")
                auth_isogeo_cfg.setMethod("Basic")
                auth_isogeo_cfg.setUri("https://v1.api.isogeo.com/about")
                auth_isogeo_cfg.setConfig("username", app_id)
                auth_isogeo_cfg.setConfig("password", app_secret)
                # check if method parameters are correctly set and store it
                if auth_isogeo_cfg.isValid():
                    qgis_auth_mng.storeAuthenticationConfig(auth_isogeo_cfg)
                    qsettings.setValue("isogeo/app_auth/qgis_auth_id",
                                       auth_isogeo_cfg.id())
                else:
                    logger.error("AUTH - Fail to create and store configuration")
            else:
                logger.debug("TRACKING - AUTH: master password is not set")
                pass
        else:
            pass

        # launch authentication
        self.user_authentication()

    def ask_for_token(self, c_id, c_secret):
        """Ask a token from Isogeo API authentification page.
        This send a POST request to Isogeo API with the user id and secret in
        its header. The API should return an access token
        """
        headervalue = "Basic " + base64.b64encode(c_id + ":" + c_secret)
        data = urllib.urlencode({"grant_type": "client_credentials"})
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

    def handle_token(self, answer):
        """Handle the API answer when asked for a token.
        This handles the API answer. If it has sent an access token, it calls
        the initialization function. If not, it raises an error, and ask
        for new IDs
        """
        logging.info("Asked a token and got a reply from the API.")
        bytarray = answer.readAll()
        content = str(bytarray)
        try:
            parsed_content = json.loads(content)
        except ValueError as e:
            if "No JSON object could be decoded" in e:
                msgBar.pushMessage(self.tr("Request to Isogeo failed: please "
                                           "check your Internet connection."),
                                   duration=10,
                                   level=msgBar.WARNING)
                logger.error("Internet connection failed")
                self.pluginIsActive = False
            else:
                pass
            return

        if 'access_token' in parsed_content:
            logging.debug("The API reply is an access token : "
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
            logging.error("The API reply is an error. ID and SECRET must be "
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
            logging.debug("The API reply has an unexpected form: {}"
                          .format(parsed_content))
            msgBar.pushMessage("Isogeo",
                               self.tr("API authentication failed."
                                       "Isogeo API answered: {}")
                                       .format(parsed_content.get('error')),
                               duration=10,
                               level=msgBar.CRITICAL)
            self.requestStatusClear = True

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

    def handle_api_reply(self, answer):
        """Handle the different possible Isogeo API answer.
        This is called when the answer from the API is finished. If it's
        content, it calls update_fields(). If it isn't, it means the token has
        expired, and it calls ask_for_token()
        """
        logging.info("Request sent to API and reply received.")
        bytarray = answer.readAll()
        content = str(bytarray)
        if answer.error() == 0 and content != "":
            logging.info("Reply is a result json.")
            if self.showDetails is False and self.settingsRequest is False:
                self.loopCount = 0
                parsed_content = json.loads(content)
                self.requestStatusClear = True
                self.update_fields(parsed_content)
                del parsed_content
            elif self.showDetails is True:
                self.showDetails = False
                self.loopCount = 0
                parsed_content = json.loads(content)
                self.requestStatusClear = True
                self.md_display.show_complete_md(parsed_content)
                del parsed_content
            elif self.settingsRequest is True:
                self.settingsRequest = False
                self.loopCount = 0
                parsed_content = json.loads(content)
                self.requestStatusClear = True
                self.write_shares_info(parsed_content)
                del parsed_content

        elif answer.error() == 204:
            logging.info("Token expired. Renewing it.")
            self.loopCount = 0
            self.requestStatusClear = True
            self.ask_for_token(self.user_id, self.user_secret)
        elif content == "":
            logging.info("Empty reply. Weither no catalog is shared with the "
                         "plugin, or there is a problem (2 requests sent "
                         "together)")
            if self.loopCount < 3:
                self.loopCount += 1
                answer.abort()
                del answer
                self.requestStatusClear = True
                self.ask_for_token(self.user_id, self.user_secret)
            else:
                self.requestStatusClear = True
                msgBar.pushMessage(
                    self.tr("The script is looping. Make sure you shared a "
                            "catalog with the plugin. If so, please report "
                            "this on the bug tracker."))
        else:
            self.requestStatusClear = True
            QMessageBox.information(iface.mainWindow(),
                                    self.tr("Error"),
                                    self.tr("You are facing an unknown error. "
                                            "Code: ") +
                                    str(answer.error()) +
                                    "\nPlease report tis on the bug tracker.")
        # method end
        return

    def update_fields(self, result):
        """Update the fields content.

        This takes an API answer and update the fields accordingly. It also
        calls show_results in the end. This may change, so results would be
        shown only when a specific button is pressed.
        """
        # logs
        logger.info("Update_fields function called on the API reply. reset = "
                    "{0}".format(self.hardReset))
        QgsMessageLog.logMessage("Query sent & received: {}"
                                 .format(result.get("query")),
                                 "Isogeo")
        # parsing
        tags = isogeo_api_mng.get_tags(result.get("tags"))
        self.old_text = self.dockwidget.txt_input.text()
        # Getting the index of selected items in each combobox
        params = self.save_params()
        # Show how many results there are
        self.results_count = result.get('total')
        self.dockwidget.btn_show.setText(
            str(self.results_count) + self.tr(" results"))
        # Setting the number of rows in the result table
        self.nb_page = str(custom_tools.results_pages_counter(self.results_count))
        self.dockwidget.lbl_page.setText(
            "page " + str(self.page_index) + self.tr(' on ') + self.nb_page)

        # ALIASES FOR FREQUENTLY CALLED WIDGETS
        cbb_contact = self.dockwidget.cbb_contact  # contact
        cbb_format = self.dockwidget.cbb_format  # formats
        cbb_geofilter = self.dockwidget.cbb_geofilter  # geographic
        cbb_geo_op = self.dockwidget.cbb_geo_op  # geometric operator
        cbb_inspire = self.dockwidget.cbb_inspire  # INSPIRE themes
        cbb_license = self.dockwidget.cbb_license  # license
        cbb_ob = self.dockwidget.cbb_ob  # sort parameter
        cbb_od = self.dockwidget.cbb_od  # sort direction
        cbb_owner = self.dockwidget.cbb_owner  # owners
        cbb_quicksearch = self.dockwidget.cbb_quicksearch  # quick searches
        cbb_srs = self.dockwidget.cbb_srs  # coordinate systems
        cbb_type = self.dockwidget.cbb_type  # metadata type
        tbl_result = self.dockwidget.tbl_result  # results table
        txt_input = self.dockwidget.txt_input  # search terms

        # RESET WiDGETS
        cbb_contact.clear()
        cbb_format.clear()
        cbb_geofilter.clear()
        cbb_inspire.clear()
        cbb_license.clear()
        cbb_owner.clear()
        cbb_srs.clear()
        cbb_type.clear()
        tbl_result.clearContents()
        tbl_result.setRowCount(0)

        # Filling the quick search combobox (also the one in settings tab)
        with open(self.json_path) as data_file:
            saved_searches = json.load(data_file)
        search_list = saved_searches.keys()
        search_list.pop(search_list.index('_default'))
        if '_current' in search_list:
            search_list.pop(search_list.index('_current'))
        cbb_quicksearch.clear()
        self.dockwidget.cbb_modify_sr.clear()

        # cbb_quicksearch.addItem(icon, self.tr('Quick Search'))
        cbb_quicksearch.addItem(ico_bolt, "")
        for i in search_list:
            cbb_quicksearch.addItem(i, i)
            self.dockwidget.cbb_modify_sr.addItem(i, i)

        width = cbb_quicksearch.view().sizeHintForColumn(0) + 5
        cbb_quicksearch.view().setMinimumWidth(width)
        # Initiating the "nothing selected" and "None" items in each combobox
        cbb_inspire.addItem(" - ")
        cbb_inspire.addItem(ico_none,
                            self.tr("None"),
                            "has-no:keyword:inspire-theme")
        cbb_owner.addItem(" - ")
        cbb_format.addItem(" - ")
        cbb_format.addItem(ico_none, self.tr("None"), "has-no:format")
        cbb_srs.addItem(" - ")
        cbb_srs.addItem(ico_none, self.tr("None"), "has-no:coordinate-system")
        cbb_geofilter.addItem(" - ")
        cbb_type.addItem(self.tr("All types"))
        cbb_contact.addItem(" - ")
        cbb_contact.addItem(ico_none, self.tr("None"), "has-no:contact")
        cbb_license.addItem(" - ")
        cbb_license.addItem(ico_none, self.tr("None"), "has-no:license")
        # Initializing the cbb that dont't need to be updated
        if self.savedSearch == "_default" or self.hardReset is True:
            tbl_result.horizontalHeader().setResizeMode(1)
            tbl_result.horizontalHeader().setResizeMode(1, 0)
            tbl_result.horizontalHeader().setResizeMode(2, 0)
            tbl_result.horizontalHeader().resizeSection(1, 80)
            tbl_result.horizontalHeader().resizeSection(2, 50)
            tbl_result.verticalHeader().setResizeMode(3)
            # Geographical operator cbb
            dict_operation = OrderedDict([(self.tr(
                'Intersects'), "intersects"),
                (self.tr('within'), "within"),
                (self.tr('contains'), "contains")])
            for key in dict_operation.keys():
                cbb_geo_op.addItem(key, dict_operation.get(key))
            # Order by cbb
            dict_ob = OrderedDict([(self.tr("Relevance"), "relevance"),
                                   (self.tr("Alphabetical order"), "title"),
                                   (self.tr("Data modified"), "modified"),
                                   (self.tr("Data created"), "created"),
                                   (self.tr("Metadata modified"), "_modified"),
                                   (self.tr("Metadata created"), "_created")]
                                  )
            for key in dict_ob.keys():
                cbb_ob.addItem(key, dict_ob.get(key))
            # Order direction cbb
            dict_od = OrderedDict([(self.tr("Descending"), "desc"),
                                   (self.tr("Ascendant"), "asc")]
                                  )
            for key in dict_od.keys():
                cbb_od.addItem(key, dict_od.get(key))

        # Filling comboboxes
        # Owners
        md_owners = tags.get("owners")
        for i in sorted(md_owners):
            cbb_owner.addItem(i, md_owners.get(i))
        # INSPIRE themes
        inspire = tags.get("inspire")
        for i in sorted(inspire):
            cbb_inspire.addItem(i, inspire.get(i))
        width = cbb_inspire.view().sizeHintForColumn(0) + 5
        cbb_inspire.view().setMinimumWidth(width)
        # Formats
        formats = tags.get("formats")
        for i in sorted(formats):
            cbb_format.addItem(i, formats.get(i))
        # Coordinate system
        srs = tags.get("srs")
        for i in sorted(srs):
            cbb_srs.addItem(i, srs.get(i))
        # Contacts
        contacts = tags.get("contacts")
        for i in sorted(contacts):
            cbb_contact.addItem(i, contacts.get(i))
        # Licenses
        licenses = tags.get("licenses")
        for i in sorted(licenses):
            cbb_license.addItem(i, licenses.get(i))
        # Resource type
        md_types = tags.get("types")
        for i in sorted(md_types):
            cbb_type.addItem(i, md_types.get(i))
        # Geographical filter
        cbb_geofilter.addItem(self.tr("Map canvas"), "mapcanvas")
        layers = QgsMapLayerRegistry.instance().mapLayers().values()
        for layer in layers:
            if layer.type() == 0:
                if layer.geometryType() == 2:
                    cbb_geofilter.addItem(ico_poly, layer.name(), layer)
                elif layer.geometryType() == 1:
                    cbb_geofilter.addItem(ico_line, layer.name(), layer)
                elif layer.geometryType() == 0:
                    cbb_geofilter.addItem(ico_poin, layer.name(), layer)

        # Putting all the comboboxes selected index to their previous
        # location. Necessary as all comboboxes items have been removed and
        # put back in place. We do not want each combobox to go back to their
        # default selected item
        if self.hardReset is False:
            if self.savedSearch is False:
                # Owners
                previous_index = cbb_owner.findData(params.get('owner'))
                cbb_owner.setCurrentIndex(previous_index)
                # Inspire keywords
                previous_index = cbb_inspire.findData(params.get('inspire'))
                cbb_inspire.setCurrentIndex(previous_index)
                # Data type
                previous_index = cbb_type.findData(params.get('datatype'))
                cbb_type.setCurrentIndex(previous_index)
                # Data format
                previous_index = cbb_format.findData(params.get('format'))
                cbb_format.setCurrentIndex(previous_index)
                # Coordinate system
                previous_index = cbb_srs.findData(params.get('srs'))
                cbb_srs.setCurrentIndex(previous_index)
                # Contact
                previous_index = cbb_contact.findData(params.get('contact'))
                cbb_contact.setCurrentIndex(previous_index)
                # License
                previous_index = cbb_license.findData(params.get('license'))
                cbb_license.setCurrentIndex(previous_index)
                # Sorting order
                cbb_ob.setCurrentIndex(cbb_ob.findData(params.get('ob')))
                # Sorting direction
                cbb_od.setCurrentIndex(cbb_od.findData(params.get('od')))
                # Quick searches
                previous_index = cbb_quicksearch.findData(params.get('favorite'))
                cbb_quicksearch.setCurrentIndex(previous_index)
                # Operator for geographical filter
                previous_index = cbb_geo_op.findData(params.get('operation'))
                cbb_geo_op.setCurrentIndex(previous_index)
                # Geographical filter
                if params.get('geofilter') == "mapcanvas":
                    previous_index = cbb_geofilter.findData("mapcanvas")
                    cbb_geofilter.setCurrentIndex(previous_index)
                else:
                    prev_index = cbb_geofilter.findText(params['geofilter'])
                    cbb_geofilter.setCurrentIndex(prev_index)
                # Filling the keywords special combobox (items checkable)
                # In the case where it isn't a saved research. So we have to
                # check the items that were previously checked
                model = QStandardItemModel(5, 1)  # 5 rows, 1 col
                # Creating the "None" option, always on top.
                none_item = QStandardItem(self.tr('None'))
                none_item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
                none_item.setData("has-no:keyword", 32)
                if none_item.data(32) in params.get('keys'):
                    none_item.setData(Qt.Checked, Qt.CheckStateRole)
                    model.insertRow(1, none_item)
                else:
                    none_item.setData(Qt.Unchecked, Qt.CheckStateRole)
                    model.insertRow(1, none_item)
                # Filling the combobox with all the normal items
                i = 2
                keywords = tags.get('keywords')
                selected_kwd = []
                for j in sorted(keywords):
                    item = QStandardItem(j)
                    item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
                    item.setData(keywords.get(j), 32)
                    # As all items have been destroyed and generated again, we
                    # have to set the checkstate (checked/unchecked) according
                    # to what the user had chosen.
                    if item.data(32) in params.get('keys'):
                        item.setData(Qt.Checked, Qt.CheckStateRole)
                        model.insertRow(0, item)
                        selected_kwd.append(j)
                    else:
                        item.setData(Qt.Unchecked, Qt.CheckStateRole)
                        model.setItem(i, 0, item)
                    i += 1
                # Creating the first item, that is just a banner for
                # the combobox.
                first_item = QStandardItem(self.tr('---- Keywords ----'))
                first_item.setIcon(ico_keyw)
                first_item.setSelectable(False)
                model.insertRow(0, first_item)
                model.itemChanged.connect(self.search)
                self.dockwidget.cbb_keywords.setModel(model)
                self.dockwidget.cbb_keywords.setToolTip(self.tr("Selected keywords:")
                                                        + "\n"
                                                        + "\n ".join(selected_kwd))
            # When it is a saved research, we have to look in the json, and
            # check the items accordingly (quite close to the previous case)
            else:
                # Opening the json and getting the keywords
                with open(self.json_path) as data_file:
                    saved_searches = json.load(data_file)
                search_params = saved_searches.get(self.savedSearch)
                keywords_list = []
                for a in search_params.keys():
                    if a.startswith("keyword"):
                        keywords_list.append(search_params.get(a))
                model = QStandardItemModel(5, 1)  # 5 rows, 1 col
                # None item, on top of the cbb
                none_item = QStandardItem(self.tr('None'))
                none_item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
                none_item.setData("has-no:keyword", 32)
                if none_item.data(32) in keywords_list:
                    none_item.setData(Qt.Checked, Qt.CheckStateRole)
                    model.insertRow(1, none_item)
                else:
                    none_item.setData(Qt.Unchecked, Qt.CheckStateRole)
                    model.insertRow(1, none_item)
                # Filling with the standard items
                i = 2
                keywords = tags.get('keywords')
                selected_kwd = []
                for j in sorted(keywords):
                    item = QStandardItem(j)
                    item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
                    item.setData(keywords.get(j), 32)
                    # As all items have been destroyed and generated again, we
                    # have to set the checkstate (checked/unchecked) according
                    # to what the user had chosen.
                    if a[0] in keywords_list:
                        item.setData(Qt.Checked, Qt.CheckStateRole)
                        model.insertRow(0, item)
                        selected_kwd.append(a[1])
                    else:
                        item.setData(Qt.Unchecked, Qt.CheckStateRole)
                        model.setItem(i, 0, item)
                    i += 1
                # Banner item
                first_item = QStandardItem(u"---- {} ----"
                                           .format(self.tr('Keywords')))
                first_item.setIcon(ico_keyw)
                first_item.setSelectable(False)
                model.insertRow(0, first_item)
                model.itemChanged.connect(self.search)
                self.dockwidget.cbb_keywords.setModel(model)
                self.dockwidget.cbb_keywords.setToolTip(self.tr("Selected keywords:")
                                                        + "\n"
                                                        + "\n ".join(selected_kwd))
                # Putting widgets to their previous states according
                # to the json content
                # Line edit content
                txt_input.setText(search_params.get('text'))
                # Owners
                saved_index = cbb_owner.findData(search_params.get('owner'))
                cbb_owner.setCurrentIndex(saved_index)
                # Inspire keywords
                value = search_params.get('inspire')
                saved_index = cbb_inspire.findData(value)
                cbb_inspire.setCurrentIndex(saved_index)
                # Formats
                saved_index = cbb_format.findData(search_params.get('format'))
                cbb_format.setCurrentIndex(saved_index)
                # Coordinate systems
                saved_index = cbb_srs.findData(search_params.get('srs'))
                cbb_srs.setCurrentIndex(saved_index)
                # Contact
                saved_index = cbb_contact.findData(search_params.get('contact'))
                cbb_contact.setCurrentIndex(saved_index)
                # License
                saved_index = cbb_license.findData(search_params.get('license'))
                cbb_license.setCurrentIndex(saved_index)
                # Geographical filter
                value = search_params.get('geofilter')
                saved_index = cbb_geofilter.findData(value)
                cbb_geofilter.setCurrentIndex(saved_index)
                # Operator for the geographical filter
                value = search_params.get('operation')
                saved_index = cbb_geo_op.findData(value)
                cbb_geo_op.setCurrentIndex(saved_index)
                # Data type
                saved_index = cbb_type.findData(search_params.get('datatype'))
                cbb_type.setCurrentIndex(saved_index)
                # Sorting order
                saved_index = cbb_ob.findData(search_params.get('ob'))
                cbb_ob.setCurrentIndex(saved_index)
                # Sorting direction
                saved_index = cbb_od.findData(search_params.get('od'))
                cbb_od.setCurrentIndex(saved_index)
                # Quick searches
                if self.savedSearch != "_default":
                    saved_index = cbb_quicksearch.findData(self.savedSearch)
                    cbb_quicksearch.setCurrentIndex(saved_index)
                self.savedSearch = False

        # In case of a hard reset, we don't have to worry about widgets
        # previous state as they are to be reset
        else:
            model = QStandardItemModel(5, 1)  # 5 rows, 1 col
            # None item
            none_item = QStandardItem(self.tr('None'))
            none_item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            none_item.setData("has-no:keyword", 32)
            if none_item.data(32) in params['keys']:
                none_item.setData(Qt.Checked, Qt.CheckStateRole)
                model.insertRow(1, none_item)
            else:
                none_item.setData(Qt.Unchecked, Qt.CheckStateRole)
                model.insertRow(1, none_item)
            # Standard items
            i = 2
            keywords = tags.get('keywords')
            for j in sorted(keywords):
                item = QStandardItem(j)
                item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
                item.setData(keywords.get(j), 32)
                # As all items have been destroyed and generated again, we have
                # to set the checkstate (checked/unchecked) according to what
                # the user had chosen
                item.setData(Qt.Unchecked, Qt.CheckStateRole)
                model.setItem(i, 0, item)
                i += 1
            # Banner item
            first_item = QStandardItem(u"---- {} ----"
                                       .format(self.tr('Keywords')))
            first_item.setIcon(ico_keyw)
            first_item.setSelectable(False)
            model.insertRow(0, first_item)
            model.itemChanged.connect(self.search)
            self.dockwidget.cbb_keywords.setModel(model)
            self.dockwidget.cbb_keywords.setToolTip(self.tr("No keyword selected"))
        # Coloring the Show result button
        self.dockwidget.btn_show.setStyleSheet(
            "QPushButton "
            "{background-color: rgb(255, 144, 0); color: white}")

        # Show result, if we want them to be shown (button 'show result', 'next
        # page' or 'previous page' pressed)
        if self.showResult is True:
            self.dockwidget.btn_next.setEnabled(True)
            self.dockwidget.btn_previous.setEnabled(True)
            cbb_ob.setEnabled(True)
            cbb_od.setEnabled(True)
            self.dockwidget.btn_show.setStyleSheet("")
            # self.dockwidget.btn_show.setToolTip(self.tr("Display results"))
            self.results_mng.show_results(result,
                                          self.dockwidget.tbl_result,
                                          progress_bar=self.bar)
            self.write_search_params('_current', search_kind="Current")
            self.store = True
        # Re enable all user input fields now the search function is
        # finished.
        self.switch_widgets_on_and_off()
        if self.results_count == 0:
            self.dockwidget.btn_show.setEnabled(False)
        # hard reset
        self.hardReset = False
        self.showResult = False

    def add_loading_bar(self):
        """Display a "loading" bar."""
        self.bar = QProgressBar()
        self.bar.setRange(0, 0)
        self.bar.setFixedWidth(120)
        iface.mainWindow().statusBar().insertPermanentWidget(0, self.bar)

    def add_layer(self, layer_info):
        """Add a layer to QGIS map canvas.

        Take layer index, search the required information to add it in
        the temporary dictionnary constructed in the show_results function.
        It then adds it.
        """
        logger.info("add_layer method called.")
        if layer_info[0] == "index":
            combobox = self.dockwidget.tbl_result.cellWidget(layer_info[1], 3)
            layer_info = combobox.itemData(combobox.currentIndex())
        elif layer_info[0] == "info":
            layer_info = layer_info[1]
        else:
            pass

        if type(layer_info) == list:
            # If the layer to be added is a vector file
            if layer_info[0] == "vector":
                path = layer_info[1]
                name = os.path.basename(path).split(".")[0]
                layer = QgsVectorLayer(path, layer_info[2], 'ogr')
                if layer.isValid():
                    lyr = QgsMapLayerRegistry.instance().addMapLayer(layer)
                    # fill QGIS metadata from Isogeo
                    lyr.setTitle(layer_info[2])
                    lyr.setAbstract(layer_info[3])
                    lyr.setKeywordList(",".join(layer_info[4]))
                    try:
                        QgsMessageLog.logMessage("Data layer added: {}"
                                                 .format(name),
                                                 "Isogeo")
                        logger.info("Vector layer added: {}".format(path))
                    except UnicodeEncodeError:
                        QgsMessageLog.logMessage(
                            "Vector layer added:: {}".format(
                                name.decode("latin1")), "Isogeo")
                        logger.info("Vector layer added: {}"
                                    .format(name.decode("latin1")))
                else:
                    logger.error("Invalid vector layer: {0}".format(path))
                    QMessageBox.information(
                        iface.mainWindow(),
                        self.tr('Error'),
                        self.tr('Vector layer is not valid.'))
            # If raster file
            elif layer_info[0] == "raster":
                path = layer_info[1]
                name = os.path.basename(path).split(".")[0]
                layer = QgsRasterLayer(path, layer_info[2])
                if layer.isValid():
                    lyr = QgsMapLayerRegistry.instance().addMapLayer(layer)
                    # fill QGIS metadata from Isogeo
                    lyr.setTitle(layer_info[2])
                    lyr.setAbstract(layer_info[3])
                    lyr.setKeywordList(",".join(layer_info[4]))
                    try:
                        QgsMessageLog.logMessage("Data layer added: {}"
                                                 .format(name),
                                                 "Isogeo")
                        logger.info("Raster layer added: {}".format(path))
                    except UnicodeEncodeError:
                        QgsMessageLog.logMessage(
                            "Raster layer added:: {}".format(
                                name.decode("latin1")), "Isogeo")
                        logger.info("Raster layer added: {}"
                                    .format(name.decode("latin1")))
                else:
                    logger.warning("Invalid raster layer: {0}".format(path))
                    QMessageBox.information(
                        iface.mainWindow(),
                        self.tr('Error'),
                        self.tr('Raster layer is not valid.'))
            # If EFS link
            elif layer_info[0] == 'arcgisfeatureserver':
                name = layer_info[1]
                uri = layer_info[2]
                layer = QgsVectorLayer(uri,
                                       name,
                                       'arcgisfeatureserver')
                if layer.isValid():
                    QgsMapLayerRegistry.instance().addMapLayer(layer)
                    logger.info("EFS layer added: {0}".format(uri))
                else:
                    error_msg = layer.error().message()
                    logger.warning("Invalid service: {0}"
                                   .format(uri, error_msg.encode("latin1")))
                    QMessageBox.information(iface.mainWindow(),
                                            self.tr('Error'),
                                            self.tr("EFS not valid. QGIS says: {}")
                                            .format(error_msg))
            # If EMS link
            elif layer_info[0] == 'arcgismapserver':
                name = layer_info[1]
                uri = layer_info[2]
                layer = QgsRasterLayer(uri,
                                       name,
                                       "arcgismapserver")
                if layer.isValid():
                    QgsMapLayerRegistry.instance().addMapLayer(layer)
                    logger.info("EMS layer added: {0}".format(uri))
                else:
                    error_msg = layer.error().message()
                    logger.warning("Invalid service: {0}"
                                   .format(uri, error_msg.encode("latin1")))
                    QMessageBox.information(iface.mainWindow(),
                                            self.tr('Error'),
                                            self.tr("EMS not valid. QGIS says: {}")
                                            .format(error_msg))
            # If WFS link
            elif layer_info[0] == 'WFS':
                url = layer_info[2]
                name = layer_info[1]
                layer = QgsVectorLayer(url, name, 'WFS')
                if layer.isValid():
                    QgsMapLayerRegistry.instance().addMapLayer(layer)
                    logger.info("WFS layer added: {0}".format(url))
                else:
                    error_msg = layer.error().message()
                    name_url = srv_url_bld.build_wfs_url(layer_info[3],
                                                         layer_info[4],
                                                         mode="complete")
                    if name_url[0] != 0:
                        layer = QgsVectorLayer(name_url[2], name_url[1], 'WFS')
                        if layer.isValid():
                            QgsMapLayerRegistry.instance().addMapLayer(layer)
                            logger.info("WFS layer added: {0}".format(url))
                        else:
                            error_msg = layer.error().message()
                            logger.warning("Invalid service: {0}"
                                           .format(url, error_msg.encode("latin1")))
                    else:
                        QMessageBox.information(
                            iface.mainWindow(),
                            self.tr('Error'),
                            self.tr("WFS is not valid. QGIS says: {}")
                                .format(error_msg))
            # If WMS link
            elif layer_info[0] == 'WMS':
                url = layer_info[2]
                name = layer_info[1]
                layer = QgsRasterLayer(url, name, 'wms', 1)
                if layer.isValid():
                    QgsMapLayerRegistry.instance().addMapLayer(layer)
                    logger.info("WMS layer added: {0}".format(url))
                else:
                    error_msg = layer.error().message()
                    name_url = srv_url_bld.build_wms_url(layer_info[3],
                                                         layer_info[4],
                                                         mode="complete")
                    if name_url[0] != 0:
                        layer = QgsRasterLayer(name_url[2], name_url[1], 'wms')
                        if layer.isValid():
                            QgsMapLayerRegistry.instance().addMapLayer(layer)
                            logger.info("WMS layer added: {0}".format(url))
                        else:
                            error_msg = layer.error().message()
                            logger.warning("Invalid service: {0}"
                                           .format(url, error_msg.encode("latin1")))
                    else:
                        QMessageBox.information(
                            iface.mainWindow(),
                            self.tr('Error'),
                            self.tr("WMS is not valid. QGIS says: {}")
                                .format(error_msg))
            # If WMTS link
            elif layer_info[0] == 'WMTS':
                url = layer_info[2]
                name = layer_info[1]
                layer = QgsRasterLayer(url, name, 'wms')
                if layer.isValid():
                    QgsMapLayerRegistry.instance().addMapLayer(layer)
                    logger.info("WMTS service layer added: {0}".format(url))
                else:
                    error_msg = layer.error().message()
                    logger.warning("Invalid service: {0}"
                                   .format(url, error_msg.encode("latin1")))
                    QMessageBox.information(
                        iface.mainWindow(),
                        self.tr('Error'),
                        self.tr("WMTS is not valid. QGIS says: {} {}")
                            .format(error_msg))
            else:
                pass
        # If the data is a PostGIS table
        elif type(layer_info) == dict:
            logger.info("Data type: PostGIS")
            # Give aliases to the data passed as arguement
            base_name = layer_info.get("base_name", "")
            schema = layer_info.get("schema", "")
            table = layer_info.get("table", "")
            # Retrieve the database information stored in the PostGISdict
            uri = QgsDataSourceURI()
            host = self.PostGISdict[base_name]['host']
            port = self.PostGISdict[base_name]['port']
            user = self.PostGISdict[base_name]['username']
            password = self.PostGISdict[base_name]['password']
            # set host name, port, database name, username and password
            uri.setConnection(host, port, base_name, user, password)
            # Get the geometry column name from the database connexion & table
            # name.
            c = con.PostGisDBConnector(uri)
            dico = c.getTables()
            for i in dico:
                if i[0 == 1] and i[1] == table:
                    geometry_column = i[8]
            # set database schema, table name, geometry column
            uri.setDataSource(schema, table, geometry_column)
            # Adding the layer to the map canvas
            layer = QgsVectorLayer(uri.uri(), table, "postgres")
            # layer.setTitle(layer_info.get("title", "notitle"))
            # layer.setAbstract(layer_info.get("abstract", ""))
            # layer.setKeywordList(",".join(layer_info.get("keywords", ())))
            if layer.isValid():
                lyr = QgsMapLayerRegistry.instance().addMapLayer(layer)
                # fill QGIS metadata from Isogeo
                lyr.setTitle(layer_info.get("title", "notitle"))
                lyr.setAbstract(layer_info.get("abstract", ""))
                lyr.setKeywordList(",".join(layer_info.get("keywords", ())))
                logger.info("Data added: {}".format(table))
            elif not layer.isValid() and\
                custom_tools.last_error[0] == "postgis" and\
                "prim" in custom_tools.last_error[1]:
                logger.info("PostGIS layer may be a view, "
                            "so key column is missing. "
                            "Trying to automatically set one...")
                # get layer fields to set as key column
                fields = layer.dataProvider().fields()
                fields_names = [i.name() for i in fields]
                # sort them by name containing id to better perf
                fields_names.sort(key=lambda x: ("id" not in x, x))
                for field in fields_names:
                    uri.setKeyColumn(field)
                    layer = QgsVectorLayer(uri.uri(True), table, "postgres")
                    if layer.isValid():
                        lyr = QgsMapLayerRegistry.instance().addMapLayer(layer)
                        # fill QGIS metadata from Isogeo
                        lyr.setTitle(layer_info.get("title", "notitle"))
                        lyr.setAbstract(layer_info.get("abstract", ""))
                        lyr.setKeywordList(",".join(layer_info.get("keywords", ())))
                        logger.info("PostGIS view layer added with [{}] as key column"
                                    .format(field))
                        return 1
                    else:
                        continue
            else:
                logger.info("Layer not valid. table = {0}".format(table))
                QMessageBox.information(
                    iface.mainWindow(),
                    self.tr("Error"),
                    self.tr("The PostGIS layer is not valid."
                            " Reason: {}".format(custom_tools.last_error)))
                return 0
        return 1

    def save_params(self):
        """Save the widgets state/index.

        This save the current state/index of each user input so we can put them
        back to their previous state/index after they have been updated
        (cleared and filled again).
        """
        # Getting the text in the search line
        text = self.dockwidget.txt_input.text()
        # get the data of the item which index is (comboboxes current index)
        owner_param = self.dockwidget.cbb_owner.itemData(
            self.dockwidget.cbb_owner.currentIndex())
        inspire_param = self.dockwidget.cbb_inspire.itemData(
            self.dockwidget.cbb_inspire.currentIndex())
        format_param = self.dockwidget.cbb_format.itemData(
            self.dockwidget.cbb_format.currentIndex())
        srs_param = self.dockwidget.cbb_srs.itemData(
            self.dockwidget.cbb_srs.currentIndex())
        contact_param = self.dockwidget.cbb_contact.itemData(
            self.dockwidget.cbb_contact.currentIndex())
        license_param = self.dockwidget.cbb_license.itemData(
            self.dockwidget.cbb_license.currentIndex())
        type_param = self.dockwidget.cbb_type.itemData(
            self.dockwidget.cbb_type.currentIndex())
        if self.dockwidget.cbb_geofilter.currentIndex() < 2:
            geofilter_param = self.dockwidget.cbb_geofilter.itemData(
                self.dockwidget.cbb_geofilter.currentIndex())
        else:
            geofilter_param = self.dockwidget.cbb_geofilter.currentText()
        favorite_param = self.dockwidget.cbb_quicksearch.itemData(
            self.dockwidget.cbb_quicksearch.currentIndex())
        operation_param = self.dockwidget.cbb_geo_op.itemData(
            self.dockwidget.cbb_geo_op.currentIndex())
        ob_param = self.dockwidget.cbb_ob.itemData(
            self.dockwidget.cbb_ob.currentIndex())
        od_param = self.dockwidget.cbb_od.itemData(
            self.dockwidget.cbb_od.currentIndex())
        # Saving the keywords that are selected : if a keyword state is
        # selected, he is added to the list
        key_params = []
        for i in xrange(self.dockwidget.cbb_keywords.count()):
            if self.dockwidget.cbb_keywords.itemData(i, 10) == 2:
                key_params.append(self.dockwidget.cbb_keywords.itemData(i, 32))

        params = {"owner": owner_param,
                  "inspire": inspire_param,
                  "format": format_param,
                  "srs": srs_param,
                  "favorite": favorite_param,
                  "keys": key_params,
                  "geofilter": geofilter_param,
                  "license": license_param,
                  "contact": contact_param,
                  "text": text,
                  "datatype": type_param,
                  "operation": operation_param,
                  "ob": ob_param,
                  "od": od_param,
                  }
        # check geographic filter
        if params.get('geofilter') == "mapcanvas":
            e = iface.mapCanvas().extent()
            extent = [e.xMinimum(),
                      e.yMinimum(),
                      e.xMaximum(),
                      e.yMaximum()]
            params['extent'] = extent
            epsg = int(iface.mapCanvas().mapRenderer(
            ).destinationCrs().authid().split(':')[1])
            params['epsg'] = epsg
            params['coord'] = self.get_coords('canvas')
        elif params.get('geofilter') in QgsMapLayerRegistry.instance().mapLayers().values():
            params['coord'] = self.get_coords(params.get('geofilter'))
        else:
            pass
        # saving params in QSettings
        qsettings.setValue("isogeo/settings/georelation", operation_param)

        logger.info(params)
        return params

    def search(self):
        """Build the request url to be sent to Isogeo API.

        This builds the url, retrieving the parameters from the widgets. When
        the final url is built, it calls send_request_to_isogeo_api
        """
        logger.info("Search function called. Building the "
                    "url that is to be sent to the API")
        # Disabling all user inputs during the search function is running
        self.switch_widgets_on_and_off(0)
        # STORING THE PREVIOUS SEARCH
        if self.store is True:
            # Open json file
            with open(self.json_path) as data_file:
                saved_searches = json.load(data_file)
            # Store the search
            name = self.tr("Last search")
            saved_searches[name] = saved_searches.get(
                '_current',
                "https://v1.api.isogeo.com/resources/search?&_limit=0")
            # Refresh the quick searches comboboxes content
            search_list = saved_searches.keys()
            search_list.pop(search_list.index('_default'))
            search_list.pop(search_list.index('_current'))
            self.dockwidget.cbb_quicksearch.clear()
            self.dockwidget.cbb_quicksearch.addItem(ico_bolt, self.tr('Quick Search'))
            self.dockwidget.cbb_modify_sr.clear()
            for i in search_list:
                self.dockwidget.cbb_quicksearch.addItem(i, i)
                self.dockwidget.cbb_modify_sr.addItem(i, i)
            # Write modifications in the json
            with open(self.json_path, 'w') as outfile:
                json.dump(saved_searches, outfile,
                          sort_keys=True, indent=4)
            self.store = False
        else:
            pass

        # STORING ALL THE INFORMATIONS NEEDED TO BUILD THE URL
        # Widget position
        params = self.save_params()
        # Info for _offset parameter
        self.page_index = 1
        params['page'] = self.page_index
        # Info for _limit parameter
        if self.showResult is True:
            params['show'] = True
        else:
            params['show'] = False
        # Info for _lang parameter
        params['lang'] = self.lang
        # URL BUILDING FUNCTION CALLED.
        self.currentUrl = isogeo_api_mng.build_request_url(params)
        logger.info(self.currentUrl)
        # Sending the request to Isogeo API
        if self.requestStatusClear is True:
            self.send_request_to_isogeo_api(self.token)
        else:
            pass

        # method end
        return

    def next_page(self):
        """Add the _offset parameter to the current url to display next page.

        Close to the search() function (lot of code in common) but
        triggered on the click on the change page button.
        """
        logger.info("next_page function called.")
        # Testing if the user is asking for a unexisting page (ex : page 6 out
        # of 5)
        if self.page_index >= custom_tools.results_pages_counter(self.results_count):
            return False
        else:
            # Adding the loading bar
            self.add_loading_bar()
            # Info about the widget status
            params = self.save_params()
            # Info for _limit parameter
            self.showResult = True
            params['show'] = True
            self.switch_widgets_on_and_off(0)
            # Building up the request
            self.page_index += 1
            params['page'] = self.page_index
            # Info for _lang parameter
            params['lang'] = self.lang
            # URL BUILDING FUNCTION CALLED.
            self.currentUrl = isogeo_api_mng.build_request_url(params)
            # Sending the request
            if self.requestStatusClear is True:
                self.send_request_to_isogeo_api(self.token)

    def previous_page(self):
        """Add the _offset parameter to the url to display previous page.

        Close to the search() function (lot of code in common) but
        triggered on the click on the change page button.
        """
        logger.info("previous_page function called.")
        # testing if the user is asking for something impossible : page 0
        if self.page_index < 2:
            return False
        else:
            # Adding the loading bar
            self.add_loading_bar()
            # Info about the widget status
            params = self.save_params()
            # Info for _limit parameter
            self.showResult = True
            params['show'] = True
            self.switch_widgets_on_and_off(0)
            # Building up the request
            self.page_index -= 1
            params['page'] = self.page_index
            # Info for _lang parameter
            params['lang'] = self.lang
            # URL BUILDING FUNCTION CALLED.
            self.currentUrl = isogeo_api_mng.build_request_url(params)
            # Sending the request
            if self.requestStatusClear is True:
                self.send_request_to_isogeo_api(self.token)

    def write_search_params(self, search_name, search_kind="Default"):
        """Write a new element in the json file when a search is saved."""
        # Open the saved_search file as a dict. Each key is a search name,
        # each value is a dict containing the parameters for this search name
        with open(self.json_path) as data_file:
            saved_searches = json.load(data_file)
        # If the name already exists, ask for a new one. ================ TO DO

        # Write the current parameters in a dict, and store it in the saved
        # search dict
        params = self.save_params()
        params['url'] = self.currentUrl
        for i in xrange(len(params.get('keys'))):
            params['keyword_{0}'.format(i)] = params.get('keys')[i]
        params.pop('keys', None)
        saved_searches[search_name] = params
        # writing file
        with open(self.json_path, 'w') as outfile:
            json.dump(saved_searches, outfile,
                      sort_keys=True, indent=4)
        # Log and messages
        logger.info("{} search stored: {}. Parameters: {}"
                    .format(search_kind, search_name, params))
        if search_kind != "Current":
            msgBar.pushMessage(self.tr("{} successfully saved: {}")
                                       .format(search_kind, search_name),
                               duration=3)
        else:
            pass
        return

    def set_widget_status(self):
        """Set a few variable and send the request to Isogeo API."""
        selected_search = self.dockwidget.cbb_quicksearch.currentText()
        if selected_search != self.tr('Quick Search'):
            logger.info("Set_widget_status function called. "
                        "User is executing a saved search.")
            self.switch_widgets_on_and_off(0)
            selected_search = self.dockwidget.cbb_quicksearch.currentText()
            with open(self.json_path) as data_file:
                saved_searches = json.load(data_file)
            if selected_search == "":
                self.savedSearch = '_default'
                search_params = saved_searches.get('_default')
            else:
                self.savedSearch = selected_search
                search_params = saved_searches[selected_search]
            self.currentUrl = search_params.get('url')
            if 'epsg' in search_params:
                epsg = int(iface.mapCanvas().mapRenderer(
                ).destinationCrs().authid().split(':')[1])
                if epsg == search_params.get('epsg'):
                    canvas = iface.mapCanvas()
                    e = search_params.get('extent')
                    rect = QgsRectangle(e[0], e[1], e[2], e[3])
                    canvas.setExtent(rect)
                    canvas.refresh()
                else:
                    canvas = iface.mapCanvas()
                    canvas.mapRenderer().setProjectionsEnabled(True)
                    canvas.mapRenderer().setDestinationCrs(
                        QgsCoordinateReferenceSystem(
                            search_params.get('epsg'),
                            QgsCoordinateReferenceSystem.EpsgCrsId))
                    e = search_params.get('extent')
                    rect = QgsRectangle(e[0], e[1], e[2], e[3])
                    canvas.setExtent(rect)
                    canvas.refresh()
            if self.requestStatusClear is True:
                self.send_request_to_isogeo_api(self.token)

    # ------------ Quicksearches ------------------------------------------

    def quicksearch_save(self):
        """Call the write_search() function and refresh the combobox."""
        # retrieve quicksearch given name and store it
        search_name = self.quicksearch_new_dialog.txt_quicksearch_name.text()
        self.write_search_params(search_name, search_kind="Quicksearch")
        # load all saved quicksearches and populate drop-down (combobox)
        with open(self.json_path, "r") as saved_searches_file:
            saved_searches = json.load(saved_searches_file)
        search_list = saved_searches.keys()
        search_list.pop(search_list.index('_default'))
        search_list.pop(search_list.index('_current'))
        self.dockwidget.cbb_quicksearch.clear()
        self.dockwidget.cbb_quicksearch.addItem(ico_bolt, self.tr('Quick Search'))
        self.dockwidget.cbb_modify_sr.clear()
        for i in search_list:
            self.dockwidget.cbb_quicksearch.addItem(i, i)
            self.dockwidget.cbb_modify_sr.addItem(i, i)
        # inform user
        # msgBar.pushMessage("Isogeo",
        #                    self.tr("New quicksearch saved: {}")\
        #                            .format(search_name),
        #                    level=msgBar.INFO,
        #                    duration=3)
        # method ending
        return

    def quicksearch_rename(self):
        """Modify the json file in order to rename a search."""
        old_name = self.dockwidget.cbb_modify_sr.currentText()
        with open(self.json_path, "r") as saved_searches_file:
            saved_searches = json.load(saved_searches_file)
        new_name = self.quicksearch_rename_dialog.txt_quicksearch_rename.text()
        saved_searches[new_name] = saved_searches[old_name]
        saved_searches.pop(old_name)
        search_list = saved_searches.keys()
        search_list.pop(search_list.index('_default'))
        search_list.pop(search_list.index('_current'))
        self.dockwidget.cbb_quicksearch.clear()
        self.dockwidget.cbb_quicksearch.addItem(ico_bolt, self.tr('Quick Search'))
        self.dockwidget.cbb_modify_sr.clear()
        for i in search_list:
            self.dockwidget.cbb_quicksearch.addItem(i, i)
            self.dockwidget.cbb_modify_sr.addItem(i, i)
        # Update JSON file
        with open(self.json_path, 'w') as outfile:
            json.dump(saved_searches, outfile,
                      sort_keys=True, indent=4)
        # inform user
        msgBar.pushMessage("Isogeo",
                           self.tr("Quicksearch renamed: from {} to {}")
                                   .format(old_name, new_name),
                           level=msgBar.INFO,
                           duration=3)
        # method ending
        return

    def quicksearch_remove(self):
        """Modify the json file in order to delete a search."""
        to_be_deleted = self.dockwidget.cbb_modify_sr.currentText()
        with open(self.json_path, "r") as saved_searches_file:
            saved_searches = json.load(saved_searches_file)
        saved_searches.pop(to_be_deleted)
        search_list = saved_searches.keys()
        search_list.pop(search_list.index('_default'))
        search_list.pop(search_list.index('_current'))
        self.dockwidget.cbb_quicksearch.clear()
        self.dockwidget.cbb_quicksearch.addItem(ico_bolt, self.tr('Quick Search'))
        self.dockwidget.cbb_modify_sr.clear()
        for i in search_list:
            self.dockwidget.cbb_quicksearch.addItem(i, i)
            self.dockwidget.cbb_modify_sr.addItem(i, i)
        # Update JSON file
        with open(self.json_path, 'w') as outfile:
            json.dump(saved_searches, outfile,
                      sort_keys=True, indent=4)
        # inform user
        msgBar.pushMessage("Isogeo",
                           self.tr("Quicksearch removed: {}")
                                   .format(to_be_deleted),
                           level=msgBar.INFO,
                           duration=3)
        # method ending
        return

    # ----------------------------------------------------------------

    def get_coords(self, filter):
        """Get the canvas coordinates in the right format and SRS (WGS84)."""
        if filter == 'canvas':
            e = iface.mapCanvas().extent()
            current_epsg = custom_tools.get_map_crs()
        else:
            index = self.dockwidget.cbb_geofilter.findText(filter)
            layer = self.dockwidget.cbb_geofilter.itemData(index)
            e = layer.extent()
            current_epsg = layer.crs().authid()
        # epsg code as integer
        current_epsg = int(current_epsg.split(':')[1])

        if current_epsg == 4326:
            coord = "{0},{1},{2},{3}".format(
                e.xMinimum(), e.yMinimum(), e.xMaximum(), e.yMaximum())
            return coord
        elif type(current_epsg) is int:
            current_srs = QgsCoordinateReferenceSystem(
                current_epsg, QgsCoordinateReferenceSystem.EpsgCrsId)
            wgs = QgsCoordinateReferenceSystem(
                4326, QgsCoordinateReferenceSystem.EpsgCrsId)
            xform = QgsCoordinateTransform(current_srs, wgs)
            minimum = xform.transform(QgsPoint(e.xMinimum(), e.yMinimum()))
            maximum = xform.transform(QgsPoint(e.xMaximum(), e.yMaximum()))
            coord = "{0},{1},{2},{3}".format(
                minimum[0], minimum[1], maximum[0], maximum[1])
            return coord
        else:
            logger.info('Wrong EPSG')
            return False

    def reinitialize_search(self):
        """Clear all widget, putting them all back to their default value.

        Clear all widget and send a request to the API (which ends up updating
        the fields : send_request() calls handle_reply(), which calls
        update_fields())
        """
        logger.info("Reinitialize_search function called.")
        self.hardReset = True
        self.dockwidget.txt_input.clear()
        self.dockwidget.cbb_keywords.clear()
        self.dockwidget.cbb_type.clear()
        self.dockwidget.cbb_geofilter.clear()
        self.dockwidget.cbb_owner.clear()
        self.dockwidget.cbb_inspire.clear()
        self.dockwidget.cbb_format.clear()
        self.dockwidget.cbb_srs.clear()
        self.dockwidget.cbb_license.clear()
        self.dockwidget.cbb_contact.clear()
        self.dockwidget.cbb_geo_op.clear()
        self.dockwidget.cbb_ob.clear()
        self.dockwidget.cbb_od.clear()
        self.search()

    def search_with_content(self):
        """Launch a search request that will end up in showing the results."""
        self.add_loading_bar()
        self.showResult = True
        self.search()

    def switch_widgets_on_and_off(self, mode=1):
        """Disable all the UI widgets when a request is being sent.

        Deactivate the widgets while a funcion is running so the user doesn't
        clic everywhere ending up in multiple requests being sent at the same
        time, making the plugin crash.
        """
        if mode:
            self.dockwidget.txt_input.setReadOnly(False)
            self.dockwidget.cbb_quicksearch.setEnabled(True)
            self.dockwidget.grp_filters.setEnabled(True)
            self.dockwidget.lyt_search.setEnabled(True)
            self.dockwidget.btn_reinit.setEnabled(True)
            self.dockwidget.btn_save.setEnabled(True)
            self.dockwidget.btn_show.setEnabled(True)
            self.dockwidget.tbl_result.setEnabled(True)
            self.dockwidget.cbb_keywords.setEnabled(True)

        else:
            self.dockwidget.txt_input.setReadOnly(True)
            self.dockwidget.cbb_quicksearch.setEnabled(False)
            self.dockwidget.grp_filters.setEnabled(False)
            self.dockwidget.lyt_search.setEnabled(False)
            self.dockwidget.btn_next.setEnabled(False)
            self.dockwidget.btn_previous.setEnabled(False)
            self.dockwidget.cbb_ob.setEnabled(False)
            self.dockwidget.cbb_od.setEnabled(False)
            self.dockwidget.btn_reinit.setEnabled(False)
            self.dockwidget.btn_save.setEnabled(False)
            self.dockwidget.btn_show.setEnabled(False)
            self.dockwidget.tbl_result.setEnabled(False)
            self.dockwidget.cbb_keywords.setEnabled(False)

    def show_popup(self, popup):
        """Open the pop up window that asks a name to save the search."""
        if popup == 'ask_name':
            self.quicksearch_new_dialog.show()
        elif popup == 'new_name':
            self.quicksearch_rename_dialog.show()
        elif popup == 'credits':
            self.credits_dialog.show()
        else:
            pass

    def send_details_request(self, md_id):
        """Send a request for aditionnal info about one data."""
        logger.info("Full metatada sheet asked. Building the url.")
        self.currentUrl = "https://v1.api.isogeo.com/resources/{}{}"\
                          .format(md_id,
                                  "?_include=conditions,contacts,"
                                  "coordinate-system,events,"
                                  "feature-attributes,limitations,"
                                  "keywords,specifications")
        self.showDetails = True
        if self.requestStatusClear is True:
            self.send_request_to_isogeo_api(self.token)
        else:
            pass

    def edited_search(self):
        """On the Qline edited signal, decide weither a search has to be launched."""
        try:
            logger.info("Editing finished signal sent.")
        except AttributeError:
            pass
        if self.dockwidget.txt_input.text() == self.old_text:
            try:
                logger.info("The lineEdit text hasn't changed."
                            " So pass without sending a request.")
            except AttributeError as e:
                logger.error(e)
                pass
            pass
        else:
            try:
                logger.info("The line Edit text changed."
                            " Calls the search function.")
            except AttributeError as e:
                logger.error(e)
                pass
            if self.dockwidget.txt_input.text() == "Ici c'est Isogeo !":
                custom_tools.special_search("isogeo")
                self.dockwidget.txt_input.clear()
                return
            elif self.dockwidget.txt_input.text() == "Picasa":
                custom_tools.special_search("picasa")
                self.dockwidget.txt_input.clear()
                return
            else:
                pass
            self.search()

    def test_qgis_style(self):
        """
            Check QGIS style applied to ensure compatibility with comboboxes.
            Avert the user and force change if the selected is not adapted.
            See: https://github.com/isogeo/isogeo-plugin-qgis/issues/137.
        """
        style_qgis = qsettings.value('qgis/style', "Default")
        if style_qgis in ("macintosh", "cleanlooks"):
            qsettings.setValue(u"qgis/style", u'Plastique')
            self.dockwidget.cbb_keywords.setEnabled(False)
            msgBar.pushMessage(self.tr("The '{}' QGIS style is not "
                                       "compatible with combobox. It has "
                                       "been changed. Please restart QGIS.")
                                       .format(style_qgis),
                               duration=0,
                               level=msgBar.WARNING)
            logging.info("The '{}' QGIS style is not compatible with combobox."
                         " Isogeo plugin changed it to 'Plastique'."
                         "Please restart QGIS."
                         .format(style_qgis))
        else:
            self.dockwidget.cbb_keywords.setEnabled(True)

    # ------------ SETTINGS - Shares -----------------------------------------

    def ask_shares_info(self, index):
        """TODO : Only if not already done before."""
        if index == 0:
            pass
        elif index == 1 and self.requestStatusClear is True:
            if self.dockwidget.txt_shares.toPlainText() == "":
                self.settingsRequest = True
                self.oldUrl = self.currentUrl
                self.currentUrl = 'https://v1.api.isogeo.com/shares'
                self.send_request_to_isogeo_api(self.token)
            else:
                pass
        else:
            pass
        QgsMessageLog.logMessage("Shares information retrieved in settings tab.",
                                 "Isogeo")
        # method end
        return

    def write_shares_info(self, content):
        """Write informations about the shares in the Settings pannel."""
        self.currentUrl = self.oldUrl
        text = u"<html>"  # opening html content
        # Isogeo application authenticated in the plugin
        app = content[0].get("applications")[0]
        text += self.tr(u"<p>This plugin is authenticated as "
                        u"<a href='{}'>{}</a> and ")\
                    .format(app.get("url", "https://isogeo.gitbooks.io/app-plugin-qgis/content"),
                            app.get("name", "Isogeo plugin for QGIS"))
        # shares feeding the application
        if len(content) == 1:
            text += self.tr(u" powered by 1 share:</p></br>")
        else:
            text += self.tr(u" powered by {0} shares:</p></br>")\
                        .format(len(content))
        # shares details
        for share in sorted(content):
            # share variables
            creator_name = share.get("_creator").get("contact").get("name")
            creator_email = share.get("_creator").get("contact").get("email")
            creator_id = share.get("_creator").get("_tag")[6:]
            share_url = "https://app.isogeo.com/groups/{}/admin/shares/{}"\
                        .format(creator_id, share.get("_id"))
            # formatting text
            text += u"<p><a href='{}'><b>{}</b></a></p>"\
                    .format(share_url,
                            share.get("name"))
            text += self.tr(u"<p>Updated: {}</p>")\
                        .format(custom_tools.handle_date(share.get("_modified")))
            text += self.tr(u"<p>Contact: {} - {}</p>")\
                        .format(creator_name,
                                creator_email)
            text += u"<p><hr></p>"
        text += u"</html>"
        self.dockwidget.txt_shares.setText(text)
        # method ending
        return

    # --------------------------------------------------------------------------

    # This function is launched when the plugin is activated.
    def run(self):
        """Run method that loads and starts the plugin."""
        if not self.pluginIsActive:
            self.pluginIsActive = True
            # dockwidget may not exist if:
            #    first run of plugin
            #    removed on close (see self.onClosePlugin method)
            if self.dockwidget is None:
                # Create the dockwidget (after translation) and keep reference
                self.dockwidget = IsogeoDockWidget()
                logger.info("Plugin load time: {}"
                            .format(plugin_times.get("isogeo_search_engine",
                                                     "NR")))

            # connect to provide cleanup on closing of dockwidget
            self.dockwidget.closingPlugin.connect(self.onClosePlugin)

            # show the dockwidget
            # TODO: fix to allow choice of dock location
            self.iface.addDockWidget(Qt.RightDockWidgetArea, self.dockwidget)
            self.dockwidget.show()

        # Fixing a qgis.core bug that shows a warning banner "connexion time
        # out" whenever a request is sent (even successfully) See :
        # http://gis.stackexchange.com/questions/136369/download-file-from-network-using-pyqgis-2-x#comment299999_136427
        # msgBar.widgetAdded.connect(msgBar.clearWidgets)

        """ --- CONNECTING FUNCTIONS --- """
        # Write in the config file when the user accept the authentification
        # window
        # self.auth_prompt_form.accepted.connect(self.write_ids_and_test)
        self.auth_prompt_form.btn_check_auth.pressed.connect(self.write_ids_and_test)

        # If user changes his id or his secret in parameters, buttons save and cancel are disabled
        # The user has to verify before by clicking on button check
        self.auth_prompt_form.ent_app_id.textEdited.connect(self.control_authentication)
        self.auth_prompt_form.ent_app_secret.textEdited.connect(self.control_authentication)

        # Connecting the comboboxes to the search function
        self.dockwidget.cbb_owner.activated.connect(self.search)
        self.dockwidget.cbb_inspire.activated.connect(self.search)
        self.dockwidget.cbb_format.activated.connect(self.search)
        self.dockwidget.cbb_srs.activated.connect(self.search)
        self.dockwidget.cbb_geofilter.activated.connect(self.search)
        self.dockwidget.cbb_type.activated.connect(self.search)
        self.dockwidget.cbb_contact.activated.connect(self.search)
        self.dockwidget.cbb_license.activated.connect(self.search)
        # Connecting the text input to the search function
        self.dockwidget.txt_input.editingFinished.connect(self.edited_search)
        # Connecting the radio buttons

        # Connecting the previous and next page buttons to their functions
        self.dockwidget.btn_next.pressed.connect(self.next_page)
        self.dockwidget.btn_previous.pressed.connect(self.previous_page)
        # Connecting the bug tracker button to its function
        self.dockwidget.btn_report.pressed.connect(
            partial(custom_tools.open_webpage,
                    link=self.tr(u'https://github.com/isogeo/isogeo-plugin-qgis/issues')
                    ))

        self.dockwidget.btn_help.pressed.connect(
            partial(custom_tools.open_webpage,
                    link="https://isogeo.gitbooks.io/app-plugin-qgis/content/"
                    ))
        # view credits
        self.dockwidget.btn_credits.pressed.connect(
            partial(self.show_popup, popup='credits'))
        # Connecting the "reinitialize search button" to a search without
        # filters
        self.dockwidget.btn_reinit.pressed.connect(self.reinitialize_search)
        # Change user
        self.dockwidget.btn_change_user.pressed.connect(
            partial(custom_tools.display_auth_form,
                    ui_auth_form=self.auth_prompt_form))

        # show results
        self.dockwidget.btn_show.pressed.connect(self.search_with_content)
        self.dockwidget.cbb_ob.activated.connect(self.search_with_content)
        self.dockwidget.cbb_od.activated.connect(self.search_with_content)

        # Button 'save favorite' connected to the opening of the pop up that
        # asks for a name
        self.dockwidget.btn_save.pressed.connect(
            partial(self.show_popup, popup='ask_name'))
        # Connect the accepted signal of the popup to the function that write
        # the search name and parameter to the file, and update the combobox
        self.quicksearch_new_dialog.accepted.connect(self.quicksearch_save)
        # Button 'rename search' connected to the opening of the pop up that
        # asks for a new name
        self.dockwidget.btn_rename_sr.pressed.connect(
            partial(self.show_popup, popup='new_name'))
        # Connect the accepted signal of the popup to the function that rename
        # a search.
        self.quicksearch_rename_dialog.accepted.connect(self.quicksearch_rename)
        # Connect the delete button to the delete function
        self.dockwidget.btn_delete_sr.pressed.connect(self.quicksearch_remove)
        # Connect the activation of the "saved search" combobox with the
        # set_widget_status function
        self.dockwidget.cbb_quicksearch.activated.connect(
            self.set_widget_status)
        # G default
        self.dockwidget.btn_default.pressed.connect(
            partial(self.write_search_params, '_default', "Default"))

        self.auth_prompt_form.btn_account_new.pressed.connect(partial(
            custom_tools.mail_to_isogeo, lang=self.lang))

        self.dockwidget.tabWidget.currentChanged.connect(self.ask_shares_info)

        self.dockwidget.txt_shares.setOpenLinks(False)
        self.dockwidget.txt_shares.anchorClicked.connect(custom_tools.open_webpage)

        # catch QGIS log messages
        QgsMessageLog.instance().messageReceived.connect(custom_tools.error_catcher)

        """ --- Actions when the plugin is launched --- """
        custom_tools.test_proxy_configuration()
        self.user_authentication()
        isogeo_api_mng.tr = self.tr
        self.dockwidget.txt_input.setFocus()
        self.test_qgis_style()
