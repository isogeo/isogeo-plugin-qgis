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
        copyright            : (C) by Isogeo
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
import requests
import os.path
import platform
import json
import base64
from urllib.parse import urlencode
import logging
from logging.handlers import RotatingFileHandler
from collections import OrderedDict
from functools import partial

# PyQT
from qgis.PyQt.QtCore import QByteArray, QCoreApplication, QSettings, Qt, QTranslator, QUrl, qVersion, QSize, pyqtSlot

from qgis.PyQt.QtWidgets import QAction, QComboBox, QMessageBox, QProgressBar
from qgis.PyQt.QtGui import QIcon, QStandardItemModel, QStandardItem

from qgis.PyQt.QtNetwork import QNetworkRequest

# PyQGIS

from qgis.utils import iface, plugin_times

from qgis.core import (QgsCoordinateReferenceSystem, QgsCoordinateTransform, QgsDataSourceUri, QgsMessageLog, QgsPointXY, QgsRectangle, QgsRasterLayer, QgsVectorLayer, QgsProject,
                       QgsApplication)

try:
    from qgis.core import Qgis
except ImportError:
    from qgis.core import QGis as Qgis

# Initialize Qt resources from file resources.py
from . import resources

# UI classes
from .ui.isogeo_dockwidget import IsogeoDockWidget  # main widget
from .ui.credits.dlg_credits import IsogeoCredits
from .ui.metadata.dlg_md_details import IsogeoMdDetails
from .ui.quicksearch.dlg_quicksearch_new import QuicksearchNew
from .ui.quicksearch.dlg_quicksearch_rename import QuicksearchRename

# Plugin modules
from .modules import Authenticator
from .modules import ApiRequester
from .modules import MetadataDisplayer
from .modules import ResultsManager
from .modules import IsogeoPlgTools
from .modules import QuickSearchManager
from .modules import SharesParser

# ############################################################################
# ########## Globals ###############
# ##################################

# plugin directory path
plg_basepath = os.path.dirname(os.path.realpath(__file__))
plg_reg_name = os.path.basename(plg_basepath)

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
plg_tools = IsogeoPlgTools(auth_folder=os.path.join(plg_basepath, "_auth"))

# -- LOG FILE --------------------------------------------------------
# log level depends on plugin directory name
if plg_reg_name == plg_tools.plugin_metadata(base_path=plg_basepath, value="name"):
    log_level = logging.WARNING
elif "beta" in plg_tools.plugin_metadata(base_path=plg_basepath) or "dev" in plg_reg_name:
    log_level = logging.DEBUG
else:
    log_level = logging.INFO

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
    logger.info('QGIS Version: {0}'.format(Qgis.QGIS_VERSION))
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
        self.plg_basepath = os.path.realpath(os.path.dirname(__file__))

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

        # UI submodules
        self.quicksearch_new_dialog = QuicksearchNew()
        self.quicksearch_rename_dialog = QuicksearchRename()
        self.credits_dialog = IsogeoCredits()

        # SUBMODULES
        # instanciating
        self.md_display = MetadataDisplayer(IsogeoMdDetails())

        self.results_mng = ResultsManager(self)
        self.results_mng.cache_mng.loader()

        self.approps_mng = SharesParser()
        self.approps_mng.tr = self.tr

        self.authenticator = Authenticator(auth_folder=os.path.join(self.plg_basepath, "_auth"))

        self.api_requester = ApiRequester()
        self.api_requester.tr = self.tr
        
        # connecting
        self.api_requester.token_sig.connect(self.token_slot)
        self.api_requester.search_sig.connect(self.update_fields)
        self.api_requester.details_sig.connect(self.md_display.show_complete_md)
        self.api_requester.shares_sig.connect(self.approps_mng.send_share_info)

        self.approps_mng.shares_ready.connect(self.write_shares_info) 

        # start variables
        self.savedSearch = "first"
        self.loopCount = 0
        self.hardReset = False
        self.showResult = False
        self.showDetails = False
        self.store = False
        self.PostGISdict = self.results_mng.build_postgis_dict(qsettings)

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
        self.results_mng.cache_mng.dumper()
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
        self.dockwidget.tab_search.setEnabled(False)

        api_init = self.authenticator.manage_api_initialization()
        if api_init[0]:
            self.dockwidget.tab_search.setEnabled(True)
            self.api_requester.setup_api_params(api_init[1])

    def write_ids_and_test(self):
        """Store the id & secret and launch the test function.
        Called when the authentification window is closed,
        it stores the values in the file, then call the
        user_authentification function to test them.
        """
        self.authenticator.credentials_storer()
        # launch authentication
        self.user_authentication()
    
    def token_slot(self, token_signal: str):
        logger.debug(token_signal)
        if token_signal == "tokenOK":
            if self.savedSearch == "first":
                logger.debug("First search since plugin started.")
                self.set_widget_status()  
                logger.debug("Asking application properties to the Isogeo API.")
                self.api_requester.send_request(request_type = "shares")     
            else:
                self.api_requester.send_request()
        elif token_signal == "credIssue":
            self.authenticator.display_auth_form()
            msgBar.pushMessage("Isogeo",
                               self.tr("API authentication failed.Isogeo API answered: {}")
                                       .format(parsed_content.get('error')),
                               duration=10,
                               level=1)
        elif token_signal == "authIssue":
            msgBar.pushMessage("Isogeo",
                               self.tr("API authentication failed.Isogeo API answered: {}")
                                       .format(parsed_content.get('error')),
                               duration=10,
                               level=2)
        else:
            msgBar.pushMessage(self.tr("Request to Isogeo failed: please check your Internet connection."),
                                   duration=10,
                                   level=1)
            self.pluginIsActive = False

    # -- UI - UPDATE SEARCH FORM ----------------------------------------------
    def update_fields(self, result: dict):
        """Update search form fields from search tags and previous search.
        Slot connected to ApiRequster.search_sig (see modules/api/requester.py)
        This takes an API answer ('result' parameter) and update the fields 
        accordingly. It also calls show_results in the end. This may change,  
        so results would be shown only when a specific button is pressed.

        :param dict result: Parsed content of search request's reply
        """
        logger.debug("Update_fields function called on the API reply. reset = "
                     "{}".format(self.hardReset))
        QgsMessageLog.logMessage("Query sent & received: {}"
                                 .format(result.get("query")),
                                 "Isogeo")
        # getting and parsing tags
        tags = self.authenticator.get_tags(result.get("tags"))
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
        search_list = list(saved_searches.keys())
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
            tbl_result.horizontalHeader().setSectionResizeMode(1)
            tbl_result.horizontalHeader().setSectionResizeMode(1, 0)
            tbl_result.horizontalHeader().setSectionResizeMode(2, 0)
            tbl_result.horizontalHeader().resizeSection(1, 80)
            tbl_result.horizontalHeader().resizeSection(2, 50)
            tbl_result.verticalHeader().setSectionResizeMode(3)
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
        layers = QgsProject.instance().mapLayers().values()
        for layer in layers:
            if layer.type() == 0:
                if layer.geometryType() == 2:
                    cbb_geofilter.addItem(ico_poly, layer.name())
                elif layer.geometryType() == 1:
                    cbb_geofilter.addItem(ico_line, layer.name())
                elif layer.geometryType() == 0:
                    cbb_geofilter.addItem(ico_poin, layer.name())

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
                keywords_list = [v for k,v in search_params.items() if k.startswith("keyword")]
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
            # self.write_search_params('_current', search_kind="Current")
            self.quicksearch.write_params('_current', search_kind="Current")
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

        selected_keywords_lbls = self.dockwidget.cbb_chck_kw.checkedItems()  # for tooltip
        model = QStandardItemModel(5, 1)  # 5 rows, 1 col
        logger.debug(type(selected_keywords))
        logger.debug(selected_keywords)
        # parse keywords and check selected
        i = 0   # row index
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
        self.dockwidget.cbb_chck_kw.setModel(model)

        # add tooltip with selected keywords. see: #107#issuecomment-341742142
        if selected_keywords:
            tooltip = "{}\n - {}".format(self.tr("Selected keywords:"), "\n - ".join(selected_keywords_lbls))
        else:
            tooltip =  self.tr("No keyword selected")
        self.dockwidget.cbb_chck_kw.setToolTip(tooltip)

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
        for txt in self.dockwidget.cbb_chck_kw.checkedItems():
            item_index = self.dockwidget.cbb_chck_kw.findText(txt, Qt.MatchFixedString)
            key_params.append(self.dockwidget.cbb_chck_kw.itemData(item_index, 32))

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
            extent = [e.xMinimum(), e.yMinimum(), e.xMaximum(), e.yMaximum()]
            params['extent'] = extent
            epsg = int(plg_tools.get_map_crs().split(':')[1])
            params['epsg'] = epsg
            params['coord'] = self.get_coords('canvas')
        elif params.get('geofilter') in [lyr.name() for lyr in QgsProject.instance().mapLayers().values()]:
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
        the final url is built, it calls get_request
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
                .format(self.api_requester.api_url_base))
            # Refresh the quick searches comboboxes content
            search_list = list(saved_searches.keys())
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
        self.api_requester.currentUrl = self.api_requester.build_request_url(params)
        logger.debug(self.api_requester.currentUrl)
        # Sending the request to Isogeo API
        self.api_requester.send_request()
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
            self.api_requester.currentUrl = self.api_requester.build_request_url(params)
            # Sending the request
            self.api_requester.send_request()
                
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
            self.api_requester.currentUrl = self.api_requester.build_request_url(params)
            # Sending the request
            self.api_requester.send_request()
                      
    def set_widget_status(self):
        """Set a few variable and send the request to Isogeo API."""
        selected_search = self.dockwidget.cbb_quicksearch_use.currentText()
        logger.debug("Quicksearch selected: {}".format(selected_search))
        # load quicksearches
        with open(self.json_path) as data_file:
            saved_searches = json.load(data_file)
        if selected_search != self.tr("Quicksearches"):
            self.switch_widgets_on_and_off(0)   # disable search form
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
            self.api_requester.currentUrl = search_params.get('url')
            self.api_requester.send_request()
        else:
            if self.savedSearch == "first":
                logger.debug("First search. Launch '_default' search.")

                self.savedSearch = "_default"
                search_params = saved_searches.get('_default')

                self.api_requester.currentUrl = search_params.get('url')
                self.api_requester.send_request()

            else :
                logger.debug("No quicksearch selected.")

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
            layer = QgsProject.instance().mapLayersByName(filter)[0]
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
            xform = QgsCoordinateTransform(current_srs, wgs, QgsProject.instance())
            minimum = xform.transform(QgsPointXY(e.xMinimum(), e.yMinimum()))
            maximum = xform.transform(QgsPointXY(e.xMaximum(), e.yMaximum()))
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
        self.api_requester.currentUrl = "{}/resources/{}{}".format(self.api_requester.api_url_base, md_id,
            "?_include=conditions,contacts,coordinate-system,events,feature-attributes,limitations,keywords,specifications")
        self.api_requester.send_request("details")

    def write_shares_info(self, text:str):
        """Write informations about the shares in the Settings pannel.
        See: #87

        :param text str: share informations from Isogeo API
        """
        logger.debug("Displaying application properties.")
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
        self.quicksearch = QuickSearchManager(self)
        self.quicksearch.request_url_builder = self.api_requester.build_request_url
        # select and use
        self.dockwidget.cbb_quicksearch_use.activated.connect(self.set_widget_status)

        # # -- Settings tab - Search --------------------------------------------
        # button to empty the cache of filepaths #135
        self.dockwidget.btn_cache_trash.pressed.connect(self.results_mng.cache_mng.cleaner)

        # -- Settings tab - Application authentication ------------------------
        # Change user -> see below for authentication form
        self.dockwidget.btn_change_user.pressed.connect(self.authenticator.display_auth_form)
        # share text window
        self.dockwidget.txt_shares.setOpenLinks(False)
        self.dockwidget.txt_shares.anchorClicked.connect(plg_tools.open_webpage)

        # -- Settings tab - Resources -----------------------------------------
        # report and log - see #53 and  #139
        self.dockwidget.btn_log_dir.setIcon(ico_log)
        self.dockwidget.btn_log_dir.pressed.connect(partial(plg_tools.open_dir_file,
                                                            target=plg_logdir))
        self.dockwidget.btn_report.pressed.connect(partial(plg_tools.open_webpage,
                    link=u"https://github.com/isogeo/isogeo-plugin-qgis/issues/new?title={} - plugin v{} QGIS {} ({})&labels=bug&milestone=4".format(self.tr("TITLE ISSUE REPORTED"),
                    plg_tools.plugin_metadata(base_path=plg_basepath),
                    Qgis.QGIS_VERSION,
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
        self.authenticator.ui_auth_form.btn_check_auth.pressed.connect(self.write_ids_and_test)

        """ ------ CUSTOM CONNECTIONS ------------------------------------- """
        # get shares only if user switch on tabs
        # catch QGIS log messages - see: https://gis.stackexchange.com/a/223965/19817
        QgsApplication.messageLog().messageReceived.connect(plg_tools.error_catcher)

        """ ------- EXECUTED AFTER PLUGIN IS LAUNCHED --------------------- """
        self.dockwidget.setWindowTitle("Isogeo - {}".format(self.plg_version))
        # add translator method in others modules
        plg_tools.tr = self.tr
        self.authenticator.tr = self.tr
        self.authenticator.lang = self.lang
        # checks
        plg_tools.test_proxy_configuration() #22
        self.dockwidget.cbb_chck_kw.setEnabled(plg_tools.test_qgis_style())  # see #137
        # self.dockwidget.cbb_chck_kw.setMaximumSize(QSize(250, 25))
        self.dockwidget.txt_input.setFocus()
        self.user_authentication()

# #############################################################################
# ##### Stand alone program ########
# ##################################
if __name__ == '__main__':
    """Standalone execution."""
