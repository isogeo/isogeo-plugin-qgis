# -*- coding: utf-8 -*-
from __future__ import (division,
                        print_function, unicode_literals)

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
import sys

# PyQT
# from QByteArray
from qgis.PyQt.QtCore import (QByteArray, QCoreApplication, QSettings,
                              Qt, QTranslator, QUrl, qVersion)
from qgis.PyQt.QtGui import (QAction, QComboBox, QIcon, QMessageBox,
                             QStandardItemModel, QStandardItem, QProgressBar)
from qgis.PyQt.QtNetwork import QNetworkRequest

# PyQGIS
import db_manager.db_plugins.postgis.connector as pgis_con
from qgis.utils import iface, plugin_times, QGis
from qgis.core import (QgsCoordinateReferenceSystem, QgsCoordinateTransform,
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

# Plugin modules
from modules import IsogeoPlgApiMngr
from modules import MetadataDisplayer
from modules import ResultsManager
from modules import IsogeoPlgTools
from modules import UrlBuilder

# ############################################################################
# ########## Globals ###############
# ##################################

# plugin directory path
plg_basepath = os.path.dirname(os.path.realpath(__file__))
plg_reg_name = os.path.basename(plg_basepath)

# force encoding
reload(sys)
sys.setdefaultencoding('utf-8')

# QGIS useful tooling and shortcuts
msgBar = iface.messageBar()
qsettings = QSettings()

# required subfolders
plg_logdir = os.path.join(plg_basepath, "_logs")

if not os.path.exists(os.path.join(plg_basepath, "_auth")):
    os.mkdir(os.path.join(plg_basepath, "_auth"))
if not os.path.exists(plg_logdir):
    os.mkdir(plg_logdir)
if not os.path.exists(os.path.join(plg_basepath, "_user")):
    os.mkdir(os.path.join(plg_basepath, "_user"))


# plugin internal submodules
plg_api_mngr = IsogeoPlgApiMngr(auth_folder=os.path.join(plg_basepath, "_auth"))
plg_tools = IsogeoPlgTools(auth_folder=os.path.join(plg_basepath, "_auth"))
plg_url_bldr = UrlBuilder()

# -- LOG FILE --------------------------------------------------------
# log level depends on plugin directory name
if plg_reg_name == plg_tools.plugin_metadata(base_path=plg_basepath, value="name"):
    log_level = logging.WARNING
elif "beta" in plg_tools.plugin_metadata(base_path=plg_basepath)\
  or "dev" in plg_tools.plugin_metadata(base_path=plg_basepath, value="name"):
    log_level = logging.DEBUG
else:
    log_level = logging.DEBUG

logger = logging.getLogger("IsogeoQgisPlugin")
logging.captureWarnings(True)
logger.setLevel(log_level)
log_form = logging.Formatter("%(asctime)s || %(levelname)s "
                             "|| %(module)s - %(lineno)d ||"
                             " %(funcName)s || %(message)s")
logfile = RotatingFileHandler(os.path.join(plg_logdir,
                                           "log_isogeo_plugin.log"),
                              "a", 5000000, 1)
logfile.setLevel(log_level)
logfile.setFormatter(log_form)
logger.addHandler(logfile)

# icons
ico_od_asc = QIcon(':/plugins/Isogeo/resources/results/sort-alpha-asc.svg')
ico_od_desc = QIcon(':/plugins/Isogeo/resources/results/sort-alpha-desc.svg')
ico_ob_relev = QIcon(":/plugins/Isogeo/resources/results/star.svg")
ico_ob_alpha = QIcon(':/plugins/Isogeo/resources/metadata/language.svg')
ico_ob_dcrea = QIcon(':/plugins/Isogeo/resources/datacreated.svg')
ico_ob_dupda = QIcon(':/plugins/Isogeo/resources/datamodified.svg')
ico_ob_mcrea = QIcon(':/plugins/Isogeo/resources/calendar-plus-o.svg')
ico_ob_mupda = QIcon(':/plugins/Isogeo/resources/calendar_blue.svg')
ico_bolt = QIcon(':/plugins/Isogeo/resources/search/bolt.svg')
ico_keyw = QIcon(':/plugins/Isogeo/resources/tag.svg')
ico_none = QIcon(':/plugins/Isogeo/resources/none.svg')
ico_line = QIcon(':/images/themes/default/mIconLineLayer.svg')
ico_log = QIcon(":/images/themes/default/mActionFolder.svg")
ico_poin = QIcon(':/images/themes/default/mIconPointLayer.svg')
ico_poly = QIcon(':/images/themes/default/mIconPolygonLayer.svg')

# ############################################################################
# ########## Classes ###############
# ##################################


class Isogeo:
    """Isogeo plugin for QGIS LTR."""

    # attributes
    plg_version = plg_tools.plugin_metadata(base_path=plg_basepath)

    logger.info('\n\n\t========== Isogeo Search Engine for QGIS ==========')
    logger.info('OS: {0}'.format(platform.platform()))
    logger.info('QGIS Version: {0}'.format(QGis.QGIS_VERSION))
    logger.info('Plugin version: {0}'.format(plg_version))
    logger.info('Log level: {0}'.format(log_level))

    def __init__(self, iface):
        """Constructor.

        :param QgsInterface iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
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
        self.qgs_ntwk_mngr = QgsNetworkAccessManager.instance()

        # UI submodules
        self.auth_prompt_form = IsogeoAuthentication()
        self.quicksearch_new_dialog = QuicksearchNew()
        self.quicksearch_rename_dialog = QuicksearchRename()
        self.credits_dialog = IsogeoCredits()
        self.md_display = MetadataDisplayer(IsogeoMdDetails())
        self.results_mng = ResultsManager(self)

        # link UI and submodules
        plg_api_mngr.ui_auth_form = self.auth_prompt_form
        self.results_mng.paths_cache = os.path.realpath(os.path.join(plg_basepath,
                                                                     "_user",
                                                                     "paths_cache.json"))

        # start variables
        self.savedSearch = "first"
        self.loopCount = 0
        self.hardReset = False
        self.showResult = False
        self.showDetails = False
        self.store = False
        self.settingsRequest = False
        self.PostGISdict = plg_url_bldr.build_postgis_dict(qsettings)

        self.currentUrl = ""
        # self.currentUrl = "https://v1.api.isogeo.com/resources/search?
        # _limit=10&_include=links&_lang={0}".format(self.lang)

        self.old_text = ""
        self.page_index = 1
        self.json_path = os.path.realpath(os.path.join(plg_basepath,
                                                       "_user/quicksearches.json"))

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

        :param str icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :param str text: Text that should be shown in menu items for this action.
        :param function callback: Function to be called when the action is triggered.
        :param bool enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :param bool add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :param bool add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :param str status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :param QWidget parent: Parent widget for the new action. Defaults None.
        :param str whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.
        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """
        ico = QIcon(ico_path)
        action = QAction(ico, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)
        action.setToolTip("Isogeo (v{})"
                          .format(self.plg_version))

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

    # -------------------------------------------------------------------------

    def onClosePlugin(self):
        """Cleanup necessary items here when plugin dockwidget is closed."""
        # save cache
        self.results_mng._cache_dumper()
        # disconnects
        self.dockwidget.closingPlugin.disconnect(self.onClosePlugin)

        # remove this statement if dockwidget is to remain
        # for reuse if plugin is reopened
        # Commented next statement since it causes QGIS crashe
        # when closing the docked window:
        self.dockwidget = None
        self.pluginIsActive = False

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

    # -------------------------------------------------------------------------
    def user_authentication(self):
        """Test the validity of the user id and secret.
        This is the first major function the plugin calls when executed. It
        retrieves the id and secret from the config file. If they are set to
        their default value, it asks for them.
        If not, it tries to send a request.
        """
        plg_api_mngr.req_status_isClear = False
        self.dockwidget.tab_search.setEnabled(False)
        if plg_api_mngr.manage_api_initialization():
            self.dockwidget.tab_search.setEnabled(True)
            plg_api_mngr.req_status_isClear = True
            self.api_auth_post_get_token()

    def write_ids_and_test(self):
        """Store the id & secret and launch the test function.
        Called when the authentification window is closed,
        it stores the values in the file, then call the
        user_authentification function to test them.
        """
        plg_api_mngr.credentials_storer()

        # launch authentication
        self.user_authentication()

    # -- API - AUTHENTICATION -------------------------------------------------
    def api_auth_post_get_token(self):
        """Ask a token from Isogeo API authentification page.
        This send a POST request to Isogeo API with the user id and secret in
        its header. The API should return an access token.

        That's the api_auth_handle_token method which get the API response. See below.
        """
        logger.debug("Use loaded credentials to authenticate the plugin.")
        # build header with credentials
        headervalue = "Basic " + base64.b64encode("{}:{}"
                                                  .format(plg_api_mngr.api_app_id,
                                                          plg_api_mngr.api_app_secret))
        data = urllib.urlencode({"grant_type": "client_credentials"})
        databyte = QByteArray()
        databyte.append(data)
        # build URL request
        url = QUrl(plg_api_mngr.api_url_token)
        request = QNetworkRequest(url)
        request.setRawHeader("Authorization", headervalue)
        if plg_api_mngr.req_status_isClear is True:
            plg_api_mngr.req_status_isClear = False
            logger.debug("Token POST request sent to {}".format(request.url()))
            token_reply = self.qgs_ntwk_mngr.post(request, databyte)
            token_reply.finished.connect(
                partial(self.api_auth_handle_token, answer=token_reply))
        else:
            logger.debug("Network in use. Try again later.")

    def api_auth_handle_token(self, answer):
        """Handle the API answer when asked for a token.
        This handles the API answer. If it has sent an access token, it calls
        the initialization function. If not, it raises an error, and ask
        for new IDs

        :param QNetworkReply answer: Isogeo ID API response
        """
        logger.debug("Asked a token and got a reply from the API: {}")
        bytarray = answer.readAll()
        content = str(bytarray)
        # check API response structure
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

        # if structure is OK, parse and check response status
        if 'access_token' in parsed_content:
            QgsMessageLog.logMessage("Authentication succeeded", "Isogeo")
            logger.debug("Access token retrieved.")
            # Enable buttons "save and cancel"
            self.dockwidget.setEnabled(True)

            # TO DO : Appeler la fonction d'initialisation
            self.token = "Bearer " + parsed_content.get('access_token')
            if self.savedSearch == "first":
                logger.debug("First search since plugin started.")
                plg_api_mngr.req_status_isClear = True
                self.set_widget_status()
            else:
                plg_api_mngr.req_status_isClear = True
                self.api_get_requests(self.token)
        # TO DO : Distinguer plusieurs cas d'erreur
        elif 'error' in parsed_content:
            logger.error("The API reply is an error: {}. ID and SECRET must be "
                         "invalid. Asking for them again."
                         .format(parsed_content.get('error')))
            # displaying auth form
            plg_api_mngr.display_auth_form()
            msgBar.pushMessage("Isogeo",
                               self.tr("API authentication failed."
                                       "Isogeo API answered: {}")
                                       .format(parsed_content.get('error')),
                               duration=10,
                               level=msgBar.WARNING)
            plg_api_mngr.req_status_isClear = True
        else:
            logger.debug("The API reply has an unexpected form: {}"
                          .format(parsed_content))
            msgBar.pushMessage("Isogeo",
                               self.tr("API authentication failed."
                                       "Isogeo API answered: {}")
                                       .format(parsed_content.get('error')),
                               duration=10,
                               level=msgBar.CRITICAL)
            plg_api_mngr.req_status_isClear = True

    # -- API - REQUEST --------------------------------------------------------
    def api_get_requests(self, token):
        """Send a content url to the Isogeo API.
        This takes the currentUrl variable and send a request to this url,
        using the token variable.

        :param str token: Isogeo ID oAuth2 bearer
        """
        logger.debug("Send a request to the 'currentURL' set: {}."
                     .format(self.currentUrl))
        myurl = QUrl(self.currentUrl)
        request = QNetworkRequest(myurl)
        request.setRawHeader("Authorization", token)
        if plg_api_mngr.req_status_isClear is True:
            plg_api_mngr.req_status_isClear = False
            logger.debug("Search request sent to {}".format(request.url()))
            api_reply = self.qgs_ntwk_mngr.get(request)
            api_reply.finished.connect(
                partial(self.api_requests_handle_reply, answer=api_reply))
        else:
            pass

    def api_requests_handle_reply(self, answer):
        """Handle the different possible Isogeo API answer.
        This is called when the answer from the API is finished. If it's
        content, it calls update_fields(). If it isn't, it means the token has
        expired, and it calls api_auth_post_get_token().

        For support, see: https://gis.stackexchange.com/a/136427/19817

        :param QNetworkReply answer: Isogeo API search response
        """
        logger.info("Request sent to API and reply received.")
        bytarray = answer.readAll()
        content = str(bytarray)
        if answer.error() == 0 and content != "":
            logger.debug("Reply is a result json.")
            if not self.showDetails and not self.settingsRequest:
                self.loopCount = 0
                parsed_content = json.loads(content)
                plg_api_mngr.req_status_isClear = True
                self.update_fields(parsed_content)
                del parsed_content
            elif self.showDetails:
                self.showDetails = False
                self.loopCount = 0
                parsed_content = json.loads(content)
                plg_api_mngr.req_status_isClear = True
                self.md_display.show_complete_md(parsed_content)
                del parsed_content
            elif self.settingsRequest:
                self.settingsRequest = False
                self.loopCount = 0
                parsed_content = json.loads(content)
                plg_api_mngr.req_status_isClear = True
                self.write_shares_info(parsed_content)
                del parsed_content

        elif answer.error() == 204:
            logger.debug("Token expired. Renewing it.")
            self.loopCount = 0
            plg_api_mngr.req_status_isClear = True
            self.api_auth_post_get_token()
        elif content == "":
            logger.error("Empty reply. Weither no catalog is shared with the "
                         "plugin, or there is a problem (2 requests sent "
                         "together)")
            if self.loopCount < 3:
                self.loopCount += 1
                answer.abort()
                del answer
                plg_api_mngr.req_status_isClear = True
                self.api_auth_post_get_token()
            else:
                plg_api_mngr.req_status_isClear = True
                msgBar.pushMessage(
                    self.tr("The script is looping. Make sure you shared a "
                            "catalog with the plugin. If so, please report "
                            "this on the bug tracker."))
        else:
            plg_api_mngr.req_status_isClear = True
            QMessageBox.information(self.iface.mainWindow(),
                                    self.tr("Error"),
                                    self.tr("You are facing an unknown error. "
                                            "Code: ") +
                                    str(answer.error()) +
                                    "\nPlease report it on the bug tracker.")
        # method end
        #return

    # -- UI - UPDATE SEARCH FORM ----------------------------------------------
    def update_fields(self, result):
        """Update search form fields from search tags and previous search.

        This takes an API answer and update the fields accordingly. It also
        calls show_results in the end. This may change, so results would be
        shown only when a specific button is pressed.
        """
        # logs
        logger.debug("Update_fields function called on the API reply. reset = "
                     "{}".format(self.hardReset))
        QgsMessageLog.logMessage("Query sent & received: {}"
                                 .format(result.get("query")),
                                 "Isogeo")
        # getting and parsing tags
        tags = plg_api_mngr.get_tags(result.get("tags"))
        # save entered text and filters in search form
        self.old_text = self.dockwidget.txt_input.text()
        params = self.save_params()

        # Show how many results there are
        self.results_count = result.get('total')
        self.dockwidget.btn_show.setText(
            str(self.results_count) + self.tr(" results"))
        page_count = str(plg_tools.results_pages_counter(total=self.results_count))
        self.dockwidget.lbl_page.setText(
            "page " + str(self.page_index) + self.tr(' on ') + page_count)

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
        cbb_quicksearch_use = self.dockwidget.cbb_quicksearch_use  # quick searches
        cbb_srs = self.dockwidget.cbb_srs  # coordinate systems
        cbb_type = self.dockwidget.cbb_type  # metadata type
        tbl_result = self.dockwidget.tbl_result  # results table
        txt_input = self.dockwidget.txt_input  # search terms

        # RESET WiDGETS
        for cbb in self.cbbs_search_advanced:
            cbb.clear()
        tbl_result.clearContents()
        tbl_result.setRowCount(0)

        # Quicksearches combobox (also the one in settings tab)
        with open(self.json_path) as data_file:
            saved_searches = json.load(data_file)
        search_list = saved_searches.keys()
        search_list.pop(search_list.index('_default'))
        if '_current' in search_list:
            search_list.pop(search_list.index('_current'))
        cbb_quicksearch_use.clear()
        self.dockwidget.cbb_quicksearch_edit.clear()
        cbb_quicksearch_use.addItem(ico_bolt, self.tr('Quicksearches'))
        for i in search_list:
            cbb_quicksearch_use.addItem(i, i)
            self.dockwidget.cbb_quicksearch_edit.addItem(i, i)

        # Advanced search comboboxes (filters others than keywords)
        # Initiating the "nothing selected"
        for cbb in self.cbbs_search_advanced:
            cbb.addItem(" - ")
        # Initializing the cbb that dont't need to be updated
        if self.savedSearch == "_default" or self.hardReset is True:
            logger.debug("Default search or reset.")
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
            dict_ob = OrderedDict([(self.tr("Relevance"), (ico_ob_relev, "relevance")),
                                   (self.tr("Alphabetical order"), (ico_ob_alpha, "title")),
                                   (self.tr("Data modified"), (ico_ob_dupda, "modified")),
                                   (self.tr("Data created"), (ico_ob_dcrea, "created")),
                                   (self.tr("Metadata modified"), (ico_ob_mcrea, "_modified")),
                                   (self.tr("Metadata created"), (ico_ob_mupda, "_created"))]
                                  )
            for k, v in dict_ob.items():
                cbb_ob.addItem(v[0], k, v[1])

            # Order direction cbb
            dict_od = OrderedDict([(self.tr("Descending"), (ico_od_desc, "desc")),
                                   (self.tr("Ascending"), (ico_od_asc, "asc"))]
                                  )

            for k, v in dict_od.items():
                cbb_od.addItem(v[0], k, v[1])
        else:
            logger.debug("Not default search nor reset.")
            pass

        # Filling comboboxes from tags
        # Owners
        md_owners = tags.get("owners")
        for i in md_owners:
            cbb_owner.addItem(i, md_owners.get(i))
        # INSPIRE themes
        inspire = tags.get("inspire")
        for i in inspire:
            cbb_inspire.addItem(i, inspire.get(i))
        # Formats
        formats = tags.get("formats")
        for i in formats:
            cbb_format.addItem(i, formats.get(i))
        # Coordinate system
        srs = tags.get("srs")
        for i in srs:
            cbb_srs.addItem(i, srs.get(i))
        # Contacts
        contacts = tags.get("contacts")
        for i in contacts:
            cbb_contact.addItem(i, contacts.get(i))
        # Licenses
        licenses = tags.get("licenses")
        for i in licenses:
            cbb_license.addItem(i, licenses.get(i))
        # Resource type
        md_types = tags.get("types")
        for i in md_types:
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

        # sorting comboboxes
        for cbb in self.cbbs_search_advanced:
            cbb.model().sort(0)
     
        # Putting all the comboboxes selected index to their previous
        # location. Necessary as all comboboxes items have been removed and
        # put back in place. We do not want each combobox to go back to their
        # default selected item
        if self.hardReset is False:
            logger.debug("Classical search or quicksearch (no reset search)")
            if self.savedSearch is False:
                logger.debug("Classic search case (not quicksearch)")
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
                previous_index = cbb_quicksearch_use.findData(params.get('favorite'))
                cbb_quicksearch_use.setCurrentIndex(previous_index)
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
                self.update_cbb_keywords(tags_keywords=tags.get('keywords'),
                                         selected_keywords=params.get('keys'))
            # When it is a saved research, we have to look in the json, and
            # check the items accordingly (quite close to the previous case)
            else:
                logger.debug("Quicksearch case: {}".format(self.savedSearch))
                # Opening the json to get keywords
                with open(self.json_path) as data_file:
                    saved_searches = json.load(data_file)
                search_params = saved_searches.get(self.savedSearch)
                keywords_list = [v for k,v in search_params.items()\
                                 if k.startswith("keyword")]
                self.update_cbb_keywords(tags_keywords=tags.get('keywords'),
                                         selected_keywords=keywords_list)
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
                    saved_index = cbb_quicksearch_use.findData(self.savedSearch)
                    cbb_quicksearch_use.setCurrentIndex(saved_index)
                self.savedSearch = False

        # In case of a hard reset, we don't have to worry about widgets
        # previous state as they are to be reset
        else:
            logger.debug("Reset search")
            self.update_cbb_keywords(tags_keywords=tags.get('keywords'))

        # tweaking
        plg_tools._ui_tweaker(ui_widgets=self.dockwidget.tab_search.findChildren(QComboBox))

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
        else:
            self.dockwidget.btn_show.setEnabled(True)
        # hard reset
        self.hardReset = False
        self.showResult = False

    def update_cbb_keywords(self, tags_keywords={}, selected_keywords=[]):
        """Keywords combobox is specific because items are checkable.
        See: https://github.com/isogeo/isogeo-plugin-qgis/issues/159

        :param dict tags_keywords: keywords found in search tags
        :param list selected_keywords: keywords (codes) already checked
        """
        logger.debug("Updating keywords combobox with {} items."
                     .format(len(tags_keywords)))
        model = QStandardItemModel(5, 1)  # 5 rows, 1 col
        logger.debug(type(selected_keywords))
        logger.debug(selected_keywords)
        # parse keywords and check selected
        i = 0   # row index
        selected_keywords_lbls = []   # for tooltip
        for tag_label, tag_code in sorted(tags_keywords.items()):
            i += 1
            item = QStandardItem(tag_label)
            item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            item.setData(tag_code, 32)
            if not selected_keywords or self.hardReset or tag_code not in selected_keywords:
                item.setData(Qt.Unchecked, Qt.CheckStateRole)
                model.setItem(i, 0, item)
            elif tag_code in selected_keywords:
                item.setData(Qt.Checked, Qt.CheckStateRole)
                model.insertRow(0, item)
                selected_keywords_lbls.append(tag_label)
            else:
                pass

        # first item = label for the combobox.
        first_item = QStandardItem("---- {} ----"
                                   .format(self.tr('Keywords')))
        first_item.setIcon(ico_keyw)
        first_item.setSelectable(False)
        model.insertRow(0, first_item)

        # connect keyword selected -> launch search
        model.itemChanged.connect(self.search)

        # add the built model to the combobox
        self.dockwidget.cbb_keywords.setModel(model)

        # add tooltip with selected keywords. see: #107#issuecomment-341742142
        if selected_keywords:
            tooltip = "{}\n - {}".format(self.tr("Selected keywords:"),
                                         "\n - ".join(selected_keywords_lbls))
        else:
            tooltip =  self.tr("No keyword selected")
        self.dockwidget.cbb_keywords.setToolTip(tooltip)

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
        favorite_param = self.dockwidget.cbb_quicksearch_use.itemData(
            self.dockwidget.cbb_quicksearch_use.currentIndex())
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
            epsg = int(plg_tools.get_map_crs().split(':')[1])
            params['epsg'] = epsg
            params['coord'] = self.get_coords('canvas')
        elif params.get('geofilter') in QgsMapLayerRegistry.instance().mapLayers().values():
            params['coord'] = self.get_coords(params.get('geofilter'))
        else:
            pass
        # saving params in QSettings
        qsettings.setValue("isogeo/settings/georelation", operation_param)
        logger.debug(params)
        return params

    def search(self):
        """Build the request url to be sent to Isogeo API.

        This builds the url, retrieving the parameters from the widgets. When
        the final url is built, it calls api_get_requests
        """
        logger.debug("Search function called. Building the "
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
                "{}/resources/search?&_limit=0"
                .format(plg_api_mngr.api_url_base))
            # Refresh the quick searches comboboxes content
            search_list = saved_searches.keys()
            search_list.pop(search_list.index('_default'))
            search_list.pop(search_list.index('_current'))
            self.dockwidget.cbb_quicksearch_use.clear()
            self.dockwidget.cbb_quicksearch_use.addItem(ico_bolt, self.tr('Quick Search'))
            self.dockwidget.cbb_quicksearch_edit.clear()
            for i in search_list:
                self.dockwidget.cbb_quicksearch_use.addItem(i, i)
                self.dockwidget.cbb_quicksearch_edit.addItem(i, i)
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
        self.currentUrl = plg_api_mngr.build_request_url(params)
        logger.debug(self.currentUrl)
        # Sending the request to Isogeo API
        if plg_api_mngr.req_status_isClear is True:
            self.api_get_requests(self.token)
        else:
            pass

        # method end
        return

    def next_page(self):
        """Add the _offset parameter to the current url to display next page.

        Close to the search() function (lot of code in common) but
        triggered on the click on the change page button.
        """
        logger.debug("next_page function called.")
        # Testing if the user is asking for a unexisting page (ex : page 6 out
        # of 5)
        if self.page_index >= plg_tools.results_pages_counter(total=self.results_count):
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
            self.currentUrl = plg_api_mngr.build_request_url(params)
            # Sending the request
            if plg_api_mngr.req_status_isClear is True:
                self.api_get_requests(self.token)

    def previous_page(self):
        """Add the _offset parameter to the url to display previous page.

        Close to the search() function (lot of code in common) but
        triggered on the click on the change page button.
        """
        logger.debug("previous_page function called.")
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
            self.currentUrl = plg_api_mngr.build_request_url(params)
            # Sending the request
            if plg_api_mngr.req_status_isClear is True:
                self.api_get_requests(self.token)

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
        logger.debug("{} search stored: {}. Parameters: {}"
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
        selected_search = self.dockwidget.cbb_quicksearch_use.currentText()
        logger.debug("Quicksearch selected: {}".format(selected_search))
        if selected_search != self.tr("Quicksearches"):
            self.switch_widgets_on_and_off(0)   # disable search form
            # load quicksearches
            with open(self.json_path) as data_file:
                saved_searches = json.load(data_file)
            logger.debug(saved_searches.keys())
            # check if selected search can be found
            if selected_search in saved_searches:
                self.savedSearch = selected_search
                search_params = saved_searches.get(selected_search)
                logger.debug("Quicksearch found in saved searches and"
                             " related search params have just been loaded from.")
            elif selected_search not in saved_searches and "_default" in saved_searches:
                logger.warning("Selected search ({}) not found."
                               "'_default' will be used instead.")
                self.savedSearch = '_default'
                search_params = saved_searches.get('_default')
            else:
                logger.error("Selected search ({}) and '_default' do not exist."
                             .format(selected_search))
                return

            # Check projection settings in loaded search params
            if 'epsg' in search_params:
                logger.debug("Specific SRS found in search params: {}"
                             .format(epsg))
                epsg = int(plg_tools.get_map_crs().split(':')[1])
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
            # load request
            self.currentUrl = search_params.get('url')
            if plg_api_mngr.req_status_isClear is True:
                self.api_get_requests(self.token)
            else:
                logger.info("A request to the API is already running."
                            "Please wait and try again later.")
        else:
            logger.debug("No quicksearch selected. Launch '_default' search.")
            self.savedSearch = "_default"
            self.reinitialize_search()

    # -- SEARCH --------------------------------------------------------------
    def edited_search(self):
        """On the Qline edited signal, decide weither a search has to be launched."""
        try:
            logger.debug("Editing finished signal sent.")
        except AttributeError:
            pass
        if self.dockwidget.txt_input.text() == self.old_text:
            try:
                logger.debug("The lineEdit text hasn't changed."
                             " So pass without sending a request.")
            except AttributeError as e:
                logger.error(e)
                pass
            pass
        else:
            try:
                logger.debug("The line Edit text changed."
                            " Calls the search function.")
            except AttributeError as e:
                logger.error(e)
                pass
            if self.dockwidget.txt_input.text() == "Ici c'est Isogeo !":
                plg_tools.special_search("isogeo")
                self.dockwidget.txt_input.clear()
                return
            elif self.dockwidget.txt_input.text() == "Picasa":
                plg_tools.special_search("picasa")
                self.dockwidget.txt_input.clear()
                return
            else:
                pass
            self.search()

    def reinitialize_search(self):
        """Clear all widget, putting them all back to their default value.

        Clear all widget and send a request to the API (which ends up updating
        the fields : send_request() calls handle_reply(), which calls
        update_fields())
        """
        logger.debug("Reset search function called.")
        self.hardReset = True
        # clear widgets
        for cbb in self.dockwidget.tab_search.findChildren(QComboBox):
            cbb.clear()
        self.dockwidget.cbb_geo_op.clear()
        self.dockwidget.txt_input.clear()
        # launch search
        self.search()

    def search_with_content(self):
        """Launch a search request that will end up in showing the results."""
        self.add_loading_bar()
        self.showResult = True
        self.search()

    # -- QUICKSEARCHES  -------------------------------------------------------
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
        self.dockwidget.cbb_quicksearch_use.clear()
        self.dockwidget.cbb_quicksearch_use.addItem(ico_bolt, self.tr('Quick Search'))
        self.dockwidget.cbb_quicksearch_edit.clear()
        for i in search_list:
            self.dockwidget.cbb_quicksearch_use.addItem(i, i)
            self.dockwidget.cbb_quicksearch_edit.addItem(i, i)
        # method ending
        return

    def quicksearch_rename(self):
        """Modify the json file in order to rename a search."""
        old_name = self.dockwidget.cbb_quicksearch_edit.currentText()
        with open(self.json_path, "r") as saved_searches_file:
            saved_searches = json.load(saved_searches_file)
        new_name = self.quicksearch_rename_dialog.txt_quicksearch_rename.text()
        saved_searches[new_name] = saved_searches[old_name]
        saved_searches.pop(old_name)
        search_list = saved_searches.keys()
        search_list.pop(search_list.index('_default'))
        search_list.pop(search_list.index('_current'))
        self.dockwidget.cbb_quicksearch_use.clear()
        self.dockwidget.cbb_quicksearch_use.addItem(ico_bolt, self.tr('Quick Search'))
        self.dockwidget.cbb_quicksearch_edit.clear()
        for i in search_list:
            self.dockwidget.cbb_quicksearch_use.addItem(i, i)
            self.dockwidget.cbb_quicksearch_edit.addItem(i, i)
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
        to_be_deleted = self.dockwidget.cbb_quicksearch_edit.currentText()
        with open(self.json_path, "r") as saved_searches_file:
            saved_searches = json.load(saved_searches_file)
        saved_searches.pop(to_be_deleted)
        search_list = saved_searches.keys()
        search_list.pop(search_list.index('_default'))
        search_list.pop(search_list.index('_current'))
        self.dockwidget.cbb_quicksearch_use.clear()
        self.dockwidget.cbb_quicksearch_use.addItem(ico_bolt, self.tr('Quick Search'))
        self.dockwidget.cbb_quicksearch_edit.clear()
        for i in search_list:
            self.dockwidget.cbb_quicksearch_use.addItem(i, i)
            self.dockwidget.cbb_quicksearch_edit.addItem(i, i)
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

    # -- RESULTS to MAP ----------------------------------------------------------
    def add_layer(self, layer_info):
        """Add a layer to QGIS map canvas.

        Take layer index, search the required information to add it in
        the temporary dictionnary constructed in the show_results function.
        It then adds it.
        """
        logger.debug("add_layer method called.")
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
                        logger.debug("Vector layer added: {}".format(path))
                    except UnicodeEncodeError:
                        QgsMessageLog.logMessage(
                            "Vector layer added:: {}".format(
                                name.decode("latin1")), "Isogeo")
                        logger.debug("Vector layer added: {}"
                                    .format(name.decode("latin1")))
                else:
                    logger.error("Invalid vector layer: {0}".format(path))
                    QMessageBox.information(
                        self.iface.mainWindow(),
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
                        logger.debug("Raster layer added: {}".format(path))
                    except UnicodeEncodeError:
                        QgsMessageLog.logMessage(
                            "Raster layer added:: {}".format(
                                name.decode("latin1")), "Isogeo")
                        logger.debug("Raster layer added: {}"
                                    .format(name.decode("latin1")))
                else:
                    logger.warning("Invalid raster layer: {0}".format(path))
                    QMessageBox.information(
                        self.iface.mainWindow(),
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
                    logger.debug("EFS layer added: {0}".format(uri))
                else:
                    error_msg = layer.error().message()
                    logger.warning("Invalid service: {0}. QGIS says: {}"
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
                    logger.debug("EMS layer added: {0}".format(uri))
                else:
                    error_msg = layer.error().message()
                    logger.warning("Invalid service: {0}. QGIS says: {}"
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
                    logger.debug("WFS layer added: {0}".format(url))
                else:
                    error_msg = layer.error().message()
                    name_url = plg_url_bldr.build_wfs_url(layer_info[3],
                                                         layer_info[4],
                                                         mode="complete")
                    if name_url[0] != 0:
                        layer = QgsVectorLayer(name_url[2], name_url[1], 'WFS')
                        if layer.isValid():
                            QgsMapLayerRegistry.instance().addMapLayer(layer)
                            logger.debug("WFS layer added: {0}".format(url))
                        else:
                            error_msg = layer.error().message()
                            logger.warning("Invalid service: {0}. QGIS says: {}"
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
                    logger.debug("WMS layer added: {0}".format(url))
                else:
                    error_msg = layer.error().message()
                    name_url = plg_url_bldr.build_wms_url(layer_info[3],
                                                         layer_info[4],
                                                         mode="complete")
                    if name_url[0] != 0:
                        layer = QgsRasterLayer(name_url[2], name_url[1], 'wms')
                        if layer.isValid():
                            QgsMapLayerRegistry.instance().addMapLayer(layer)
                            logger.debug("WMS layer added: {0}".format(url))
                        else:
                            error_msg = layer.error().message()
                            logger.warning("Invalid service: {0}. QGIS says: {}"
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
                    logger.debug("WMTS service layer added: {0}".format(url))
                else:
                    error_msg = layer.error().message()
                    logger.warning("Invalid service: {}. QGIS says: {}"
                                   .format(url, error_msg))
                    QMessageBox.information(
                        iface.mainWindow(),
                        self.tr('Error'),
                        self.tr("WMTS is not valid. QGIS says: {}")
                            .format(error_msg))
            else:
                pass
        # If the data is a PostGIS table
        elif type(layer_info) == dict:
            logger.debug("Data type: PostGIS")
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
            c = pgis_con.PostGisDBConnector(uri)
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
                logger.debug("Data added: {}".format(table))
            elif not layer.isValid() and\
                plg_tools.last_error[0] == "postgis" and\
                "prim" in plg_tools.last_error[1]:
                logger.debug("PostGIS layer may be a view, "
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
                        logger.debug("PostGIS view layer added with [{}] as key column"
                                    .format(field))
                        return 1
                    else:
                        continue
            else:
                logger.debug("Layer not valid. table = {0}".format(table))
                QMessageBox.information(
                    iface.mainWindow(),
                    self.tr("Error"),
                    self.tr("The PostGIS layer is not valid."
                            " Reason: {}".format(plg_tools.last_error)))
                return 0
        return 1


    # -- UTILS ----------------------------------------------------------------
    def add_loading_bar(self):
        """Display a progress bar."""
        self.bar = QProgressBar()
        self.bar.setRange(0, 0)
        self.bar.setFixedWidth(120)
        self.iface.mainWindow().statusBar().insertPermanentWidget(0, self.bar)

    def get_coords(self, filter):
        """Get the canvas coordinates in the right format and SRS (WGS84)."""
        if filter == 'canvas':
            e = iface.mapCanvas().extent()
            current_epsg = plg_tools.get_map_crs()
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
            logger.debug('Wrong EPSG')
            return False

    def switch_widgets_on_and_off(self, mode=1):
        """Disable all the UI widgets when a request is being sent.

        Deactivate the widgets while a funcion is running so the user doesn't
        clic everywhere ending up in multiple requests being sent at the same
        time, making the plugin crash.
        """
        if mode:
            self.dockwidget.txt_input.setReadOnly(False)
            self.dockwidget.tab_search.setEnabled(True)
        else:
            self.dockwidget.txt_input.setReadOnly(True)
            self.dockwidget.tab_search.setEnabled(False)

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
        """Send a request for aditionnal info about one data.
        
        :param str md_id: UUID of metadata to retrieve
        """
        logger.debug("Full metatada sheet asked. Building the url.")
        self.currentUrl = "{}/resources/{}{}"\
                          .format(plg_api_mngr.api_url_base,
                                  md_id,
                                  "?_include=conditions,contacts,"
                                  "coordinate-system,events,"
                                  "feature-attributes,limitations,"
                                  "keywords,specifications")
        self.showDetails = True
        if plg_api_mngr.req_status_isClear is True:
            self.api_get_requests(self.token)
        else:
            pass

    # -- SETTINGS - Shares ----------------------------------------------------
    def ask_shares_info(self, index):
        """TODO : Only if not already done before."""
        if index == 0:
            pass
        elif index == 1 and plg_api_mngr.req_status_isClear is True:
            if self.dockwidget.txt_shares.toPlainText() == "":
                self.settingsRequest = True
                self.oldUrl = self.currentUrl
                self.currentUrl = "{}/shares".format(plg_api_mngr.api_url_base)
                self.api_get_requests(self.token)
            else:
                pass
        else:
            pass
        QgsMessageLog.logMessage("Shares information retrieved in settings tab.",
                                 "Isogeo")
        # method end
        return

    def write_shares_info(self, content):
        """Write informations about the shares in the Settings pannel.
        See: #87

        :param content dict: share informations from Isogeo API
        """
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
                        .format(plg_tools.handle_date(share.get("_modified")))
            text += self.tr(u"<p>Contact: {} - {}</p>")\
                        .format(creator_name,
                                creator_email)
            text += u"<p><hr></p>"
        text += u"</html>"
        self.dockwidget.txt_shares.setText(text)
        # method ending
        return

    # -- LAUNCH PAD------------------------------------------------------------
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
                logger.debug("Plugin load time: {}"
                             .format(plugin_times.get(plg_reg_name, "NR")))

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

        """ --- CONNECTING UI WIDGETS <-> FUNCTIONS --- """
        # shortcuts
        self.cbbs_search_advanced = self.dockwidget.grp_filters.findChildren(QComboBox)
        # -- Search form ------------------------------------------------------
        # search terms text input
        self.dockwidget.txt_input.editingFinished.connect(self.edited_search)
        # reset search button
        self.dockwidget.btn_reinit.pressed.connect(self.reinitialize_search)
        # filters comboboxes
        self.dockwidget.cbb_contact.activated.connect(self.search)
        self.dockwidget.cbb_format.activated.connect(self.search)
        self.dockwidget.cbb_geofilter.activated.connect(self.search)
        self.dockwidget.cbb_inspire.activated.connect(self.search)
        self.dockwidget.cbb_license.activated.connect(self.search)
        self.dockwidget.cbb_owner.activated.connect(self.search)
        self.dockwidget.cbb_srs.activated.connect(self.search)
        self.dockwidget.cbb_type.activated.connect(self.search)

        # -- Results table ----------------------------------------------------
        # show and order results
        self.dockwidget.btn_show.pressed.connect(self.search_with_content)
        self.dockwidget.cbb_ob.activated.connect(self.search_with_content)
        self.dockwidget.cbb_od.activated.connect(self.search_with_content)
        # pagination
        self.dockwidget.btn_next.pressed.connect(self.next_page)
        self.dockwidget.btn_previous.pressed.connect(self.previous_page)
        
        # -- Quicksearches ----------------------------------------------------
        # select and use
        self.dockwidget.cbb_quicksearch_use.activated.connect(self.set_widget_status)
        self.dockwidget.btn_quicksearch_save.pressed.connect(partial(self.show_popup, popup='ask_name'))
        # create and save
        self.quicksearch_new_dialog.accepted.connect(self.quicksearch_save)
        # rename
        self.quicksearch_rename_dialog.accepted.connect(self.quicksearch_rename)

        # -- Settings tab - Search --------------------------------------------
        # quicksearches
        self.dockwidget.btn_rename_sr.pressed.connect(partial(self.show_popup,  # rename
                                                              popup='new_name'))
        self.dockwidget.btn_delete_sr.pressed.connect(self.quicksearch_remove)  # delete

        # default search
        self.dockwidget.btn_default_save.pressed.connect(
            partial(self.write_search_params, '_default', "Default"))

        # -- Settings tab - Application authentication ------------------------
        # Change user -> see below for authentication form
        self.dockwidget.btn_change_user.pressed.connect(
            partial(plg_api_mngr.display_auth_form))
        # share text window
        self.dockwidget.txt_shares.setOpenLinks(False)
        self.dockwidget.txt_shares.anchorClicked.connect(plg_tools.open_webpage)

        # -- Settings tab - Resources -----------------------------------------
        # report and log - see #53 and  #139
        self.dockwidget.btn_log_dir.setIcon(ico_log)
        self.dockwidget.btn_log_dir.pressed.connect(partial(plg_tools.open_dir_file,
                                                            target=plg_logdir))
        self.dockwidget.btn_report.pressed.connect(
            partial(plg_tools.open_webpage,
                    link=u"https://github.com/isogeo/isogeo-plugin-qgis/issues/new?title={} - plugin v{} QGIS {} ({})&labels=bug&milestone=4"
                         .format(self.tr("TITLE ISSUE REPORTED"),
                                 plg_tools.plugin_metadata(base_path=plg_basepath),
                                 QGis.QGIS_VERSION,
                                 platform.platform())
                    ))
        # help button
        self.dockwidget.btn_help.pressed.connect(
            partial(plg_tools.open_webpage,
                    link="https://isogeo.gitbooks.io/app-plugin-qgis/content/"
                    ))
        # view credits - see: #52
        self.dockwidget.btn_credits.pressed.connect(partial(self.show_popup, popup='credits'))

        # -- Authentication form ----------------------------------------------
        # credentials file browser -> loader - see #149
        self.auth_prompt_form.btn_browse_credentials.fileChanged.connect(plg_api_mngr.credentials_uploader)
        # If user changes his id or his secret in parameters, buttons save and cancel are disabled
        # The user has to verify before by clicking on button check - see #99
        self.auth_prompt_form.btn_check_auth.pressed.connect(self.write_ids_and_test)
        self.auth_prompt_form.chb_isogeo_editor.stateChanged.connect(lambda: qsettings.setValue("isogeo/user/editor",
                                                                             int(self.auth_prompt_form.chb_isogeo_editor.isChecked())))
        # button to request an account by email
        self.auth_prompt_form.btn_account_new.pressed.connect(partial(plg_tools.mail_to_isogeo, lang=self.lang))

        """ ------ CUSTOM CONNECTIONS ------------------------------------- """
        # get shares only if user switch on tabs
        self.dockwidget.tabWidget.currentChanged.connect(self.ask_shares_info)
        # catch QGIS log messages - see: https://gis.stackexchange.com/a/223965/19817
        QgsMessageLog.instance().messageReceived.connect(plg_tools.error_catcher)

        """ ------- EXECUTED AFTER PLUGIN IS LAUNCHED --------------------- """
        self.dockwidget.setWindowTitle("Isogeo - {}".format(self.plg_version))
        # add translator method in others modules
        plg_tools.tr = self.tr
        plg_api_mngr.tr = self.tr
        # checks
        plg_tools.test_proxy_configuration() #22
        self.dockwidget.cbb_keywords.setEnabled(plg_tools.test_qgis_style())  # see #137
        self.dockwidget.txt_input.setFocus()
        self.user_authentication()

# #############################################################################
# ##### Stand alone program ########
# ##################################
if __name__ == '__main__':
    """Standalone execution."""
