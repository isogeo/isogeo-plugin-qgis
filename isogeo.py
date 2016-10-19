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

# Ajouté par moi à partir de QByteArray
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, \
    Qt, QByteArray, QUrl
# Ajouté oar moi à partir de QMessageBox
from PyQt4.QtGui import QAction, QIcon, QMessageBox, QTableWidgetItem, \
    QStandardItemModel, QStandardItem, QComboBox, QPushButton, QLabel, \
    QPixmap, QProgressBar

# Initialize Qt resources from file resources.py
import resources

# Import the code for the DockWidget
from ui.isogeo_dockwidget import IsogeoDockWidget

# Import du code des autres fenêtres
from ui.auth.dlg_authentication import IsogeoAuthentication
from ui.name.ask_research_name import ask_research_name
from ui.rename.ask_new_name import ask_new_name
from ui.mddetails.isogeo_dlg_mdDetails import IsogeoMdDetails

import os.path

# Ajoutés par moi
from qgis.utils import iface, plugin_times, QGis, reloadPlugin
from qgis.core import QgsNetworkAccessManager, QgsPoint, \
    QgsCoordinateReferenceSystem, QgsCoordinateTransform, QgsVectorLayer, \
    QgsMapLayerRegistry, QgsRasterLayer, QgsDataSourceURI, QgsMessageLog, \
    QgsRectangle
from PyQt4.QtNetwork import QNetworkRequest
import json
import base64
import urllib
import logging
from logging.handlers import RotatingFileHandler
import platform  # about operating systems

from collections import OrderedDict
from functools import partial
import db_manager.db_plugins.postgis.connector as con
import operator

# Mes modules a moi
from modules.tools import Tools

# ############################################################################
# ########## Globals ###############
# ##################################

# LOG FILE ##
logger = logging.getLogger()
logging.captureWarnings(True)
logger.setLevel(logging.INFO)  # all errors will be get
# logger.setLevel(logging.DEBUG)  # switch on it only for dev works
log_form = logging.Formatter("%(asctime)s || %(levelname)s "
                             "|| %(module)s || %(message)s")
logfile = RotatingFileHandler(os.path.join(
                              os.path.dirname(os.path.realpath(__file__)),
                              "log_isogeo_plugin.log"),
                              "a", 5000000, 1)
logfile.setLevel(logging.DEBUG)
logfile.setFormatter(log_form)
logger.addHandler(logfile)

# ############################################################################
# ########## Classes ###############
# ##################################
tools = Tools()


class Isogeo:
    """QGIS Plugin Implementation."""

    logging.info('\n\n\t========== Isogeo Search Engine for QGIS ==========')
    logging.info('OS: {0}'.format(platform.platform()))
    try:
        logging.info('QGIS Version: {0}'.format(QGis.QGIS_VERSION))
    except UnicodeEncodeError:
        logging.info('QGIS Version: 2.16.0 or 2.16.1')

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
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'isogeo_search_engine_{}.qm'.format(locale))
        logging.info('Language applied: {0}'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        if locale == "fr":
            self.lang = "fr"
        else:
            self.lang = "en"

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Isogeo')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'Isogeo')
        self.toolbar.setObjectName(u'Isogeo')

        # print "** INITIALIZING Isogeo"

        self.pluginIsActive = False

        self.dockwidget = None

        self.manager = QgsNetworkAccessManager.instance()

        self.auth_prompt_form = IsogeoAuthentication()

        self.ask_name_popup = ask_research_name()

        self.new_name_popup = ask_new_name()

        self.IsogeoMdDetails = IsogeoMdDetails()

        self.savedSearch = "first"

        self.requestStatusClear = True

        self.loopCount = 0

        self.hardReset = False

        self.showResult = False

        self.showDetails = False

        self.store = False

        self.settingsRequest = False

        self.PostGISdict = {}

        # self.currentUrl = "https://v1.api.isogeo.com/resources/search?
        # _limit=15&_include=links&_lang={0}".format(self.lang)

        self.old_text = ""

        self.page_index = 1

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.
        :param message: String for translation.
        :type message: str, QString
        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('Isogeo', message)

    def add_action(
            self,
            icon_path,
            text,
            callback,
            enabled_flag=True,
            add_to_menu=True,
            add_to_toolbar=True,
            status_tip=None,
            whats_this=None,
            parent=None):
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
        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
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
        icon_path = ':/plugins/Isogeo/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Search within Isogeo catalogs'),
            callback=self.run,
            parent=self.iface.mainWindow())

    # --------------------------------------------------------------------------

    def onClosePlugin(self):
        """Cleanup necessary items here when plugin dockwidget is closed."""
        # print "** CLOSING Isogeo"

        # disconnects
        self.dockwidget.closingPlugin.disconnect(self.onClosePlugin)

        # remove this statement if dockwidget is to remain
        # for reuse if plugin is reopened
        # Commented next statement since it causes QGIS crashe
        # when closing the docked window:
        # self.dockwidget = None
        self.pluginIsActive = False
        try:
            reloadPlugin("isogeo_search_engine")
        except TypeError:
            pass
        try:
            reloadPlugin("isogeo_plugin")
        except TypeError:
            pass

    def unload(self):
        """Remove the plugin menu item and icon from QGIS GUI."""
        # print "** UNLOAD Isogeo"

        for action in self.actions:
            self.iface.removePluginWebMenu(
                self.tr(u'&Isogeo'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    # --------------------------------------------------------------------------

    def get_path(self):
        """Retrieve the path to the folder where the plugin is."""
        basepath = os.path.dirname(os.path.realpath(__file__))
        return basepath

    def test_proxy_configuration(self):
        """Check the proxy configuration.

        if a proxy configuration is set up for the computer, and for QGIS.
        If none or both is set up, pass. But if there is a proxy config for the
        computer but not in QGIS, pops an alert message.
        """
        system_proxy_config = urllib.getproxies()
        if system_proxy_config == {}:
            logging.info("The OS doesn't use a proxy. => Proxy config : OK")
            pass
        else:
            s = QSettings()
            qgis_proxy = s.value("proxy/proxyEnabled", "")
            if str(qgis_proxy) == "true":
                http = system_proxy_config.get('http')
                if http is None:
                    pass
                else:
                    elements = http.split(':')
                    if len(elements) == 2:
                        host = elements[0]
                        port = elements[1]
                        qgis_host = s.value("proxy/proxyHost", "")
                        qgis_port = s.value("proxy/proxyPort", "")
                        if qgis_host == host:
                            if qgis_port == port:
                                logging.info("A proxy is set up both in QGIS "
                                             "and the OS and they match => "
                                             "Proxy config : OK")
                                pass
                            else:
                                QMessageBox.information(iface.mainWindow(
                                ), self.tr('Alert'),
                                    self.tr("Proxy issue : \nQGIS and your OS "
                                            "have different proxy set ups."))
                        else:
                            QMessageBox.information(iface.mainWindow(
                            ), self.tr('Alert'),
                                self.tr("Proxy issue : \nQGIS and your OS have"
                                        " different proxy set ups."))
                    elif len(elements) == 3 and elements[0] == 'http':
                        host_short = elements[1][2:]
                        host_long = elements[0] + ':' + elements[1]
                        port = elements[2]
                        qgis_host = s.value("proxy/proxyHost", "")
                        qgis_port = s.value("proxy/proxyPort", "")
                        if qgis_host == host_short or qgis_host == host_long:
                            if qgis_port == port:
                                logging.info("A proxy is set up both in QGIS"
                                             " and the OS and they match "
                                             "=> Proxy config : OK")
                                pass
                            else:
                                logging.info("OS and QGIS proxy ports do not "
                                             "match. => Proxy config : not OK")
                                QMessageBox.information(iface.mainWindow(
                                ), self.tr('Alert'),
                                    self.tr("Proxy issue : \nQGIS and your OS"
                                            " have different proxy set ups."))
                        else:
                            logging.info("OS and QGIS proxy hosts do not "
                                         "match. => Proxy config : not OK")
                            QMessageBox.information(iface.mainWindow(
                            ), self.tr('Alert'),
                                self.tr("Proxy issue : \nQGIS and your OS have"
                                        " different proxy set ups."))
            else:
                logging.info("OS uses a proxy but it isn't set up in QGIS."
                             " => Proxy config : not OK")
                QMessageBox.information(iface.mainWindow(
                ), self.tr('Alert'),
                    self.tr("Proxy issue : \nYou have a proxy set up on your"
                            " OS but none in QGIS.\nPlease set it up in "
                            "'Preferences/Options/Network'."))

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

    def write_ids_and_test(self):
        """Store the id & secret and launch the test function.

        Called when the authentification window is closed,
        it stores the values in the file, then call the
        user_authentification function to test them.
        """
        logging.info("Authentication window accepted. Writting"
                     " id/secret in QSettings.")
        user_id = self.auth_prompt_form.ent_app_id.text()
        user_secret = self.auth_prompt_form.\
            ent_app_secret.text()
        s = QSettings()
        s.setValue("isogeo-plugin/user-auth/id", user_id)
        s.setValue("isogeo-plugin/user-auth/secret", user_secret)

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
        parsed_content = json.loads(content)
        if 'access_token' in parsed_content:
            logging.info("The API reply is an access token : "
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
            logging.info("The API reply is an error. Id and secret must be "
                         "invalid. Asking for them again.")
            QMessageBox.information(
                iface.mainWindow(), self.tr("Error"), parsed_content['error'])
            self.requestStatusClear = True
            self.auth_prompt_form.show()
        else:
            self.requestStatusClear = True
            logging.info("The API reply has an unexpected form : "
                         "{0}".format(parsed_content))
            QMessageBox.information(
                iface.mainWindow(), self.tr("Error"), self.tr("Unknown error"))

    def send_request_to_isogeo_api(self, token, limit=15):
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
            elif self.showDetails is True:
                self.showDetails = False
                self.loopCount = 0
                parsed_content = json.loads(content)
                self.requestStatusClear = True
                self.show_complete_md(parsed_content)
            elif self.settingsRequest is True:
                self.settingsRequest = False
                self.loopCount = 0
                parsed_content = json.loads(content)
                self.requestStatusClear = True
                self.write_shares_info(parsed_content)

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
                iface.messageBar.pushMessage(
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
        logging.info("Update_fields function called on the API reply. reset = "
                     "{0}".format(self.hardReset))
        QgsMessageLog.logMessage("Query sent & received: {}"
                                 .format(result.get("query")),
                                 "Isogeo")
        # parsing
        tags = tools.get_tags(result)
        self.old_text = self.dockwidget.txt_input.text()
        # Getting the index of selected items in each combobox
        params = self.save_params()
        # Show how many results there are
        self.results_count = result['total']
        self.dockwidget.btn_show.setText(
            str(self.results_count) + u" résultats")
        # Setting the number of rows in the result table

        self.nb_page = str(tools.calcul_nb_page(self.results_count))
        self.dockwidget.lbl_page.setText(
            "page " + str(self.page_index) + self.tr(' on ') + self.nb_page)

        # CREATING ALIASES FOR THE FREQUENTLY CALLED WIDGETS
        # User text input
        txt_input = self.dockwidget.txt_input
        # Owners
        cbb_owner = self.dockwidget.cbb_owner
        # Inspire keywords
        cbb_inspire = self.dockwidget.cbb_inspire
        # Formats
        cbb_format = self.dockwidget.cbb_format
        # Coordinate systems
        cbb_srs = self.dockwidget.cbb_srs
        # Geographical filter
        cbb_geofilter = self.dockwidget.cbb_geofilter
        # Operator for the geographical filter
        cbb_geo_op = self.dockwidget.cbb_geo_op
        # Data type
        cbb_type = self.dockwidget.cbb_type
        # Sorting order
        cbb_ob = self.dockwidget.cbb_ob
        # Sorting direction
        cbb_od = self.dockwidget.cbb_od
        # Quick searches
        cbb_saved = self.dockwidget.cbb_saved
        # Action : view
        cb_view = self.dockwidget.checkBox
        # Action : download
        cb_dl = self.dockwidget.checkBox_2
        # Action : other
        cb_other = self.dockwidget.checkBox_3
        # Action : None
        cb_none = self.dockwidget.checkBox_4
        # Results table
        tbl_result = self.dockwidget.tbl_result

        # clearing the result table
        tbl_result.clearContents()
        tbl_result.setRowCount(0)
        # Clearing the user input comboboxes
        cbb_inspire.clear()
        cbb_owner.clear()
        cbb_format.clear()
        cbb_srs.clear()
        cbb_geofilter.clear()
        cbb_type.clear()
        # Filling the quick search combobox (also the one in settings tab)
        path = self.get_path() + '/user_settings/saved_searches.json'
        with open(path) as data_file:
            saved_searches = json.load(data_file)
        search_list = saved_searches.keys()
        search_list.pop(search_list.index('_default'))
        if '_current' in search_list:
            search_list.pop(search_list.index('_current'))
        cbb_saved.clear()
        self.dockwidget.cbb_modify_sr.clear()
        icon = QIcon(':/plugins/Isogeo/resources/bolt.svg')
        cbb_saved.addItem(icon, self.tr('Quick Search'))
        for i in search_list:
            cbb_saved.addItem(i, i)
            self.dockwidget.cbb_modify_sr.addItem(i, i)

        # Initiating the "nothing selected" and "None" items in each combobox
        cbb_inspire.addItem(" - ")
        icon = QIcon(':/plugins/Isogeo/resources/none.svg')
        cbb_inspire.addItem(icon,
                            self.tr("None"),
                            "has-no:keyword:inspire-theme")
        cbb_owner.addItem(" - ")
        cbb_format.addItem(" - ")
        cbb_format.addItem(icon, self.tr("None"), "has-no:format")
        cbb_srs.addItem(" - ")
        cbb_srs.addItem(icon, self.tr("None"), "has-no:coordinate-system")
        cbb_geofilter.addItem(" - ")
        cbb_type.addItem(self.tr("All types"))
        # Initializing the cbb that dont't need to be actualised.
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

        # Creating combobox items, with their displayed text, and their value
        # Owners
        ordered = sorted(tags.get("owner").items(), key=operator.itemgetter(1))
        for i in ordered:
            cbb_owner.addItem(i[1], i[0])
        # INSPIRE keywords
        ordered = sorted(tags.get('themeinspire').items(),
                         key=operator.itemgetter(1))
        for i in ordered:
            cbb_inspire.addItem(i[1], i[0])
        width = cbb_inspire.view().sizeHintForColumn(0) + 10
        cbb_inspire.view().setMinimumWidth(width)
        # Formats
        ordered = sorted(tags.get('formats').items(),
                         key=operator.itemgetter(1))
        for i in ordered:
            cbb_format.addItem(i[1], i[0])
        # Coordinate system
        ordered = sorted(tags.get('srs').items(), key=operator.itemgetter(1))
        for i in ordered:
            cbb_srs.addItem(i[1], i[0])
        # Resource type
        ordered = sorted(tags.get('type').items(), key=operator.itemgetter(1))
        for i in ordered:
            cbb_type.addItem(i[1], i[0])
        # Geographical filter
        cbb_geofilter.addItem(self.tr("Map canvas"), "mapcanvas")
        layers = QgsMapLayerRegistry.instance().mapLayers().values()
        polycon = QIcon(':/plugins/Isogeo/resources/polygon.png')
        linicon = QIcon(':/plugins/Isogeo/resources/line.png')
        pointicon = QIcon(':/plugins/Isogeo/resources/point.png')
        for layer in layers:
            if layer.type() == 0:
                if layer.geometryType() == 2:
                    cbb_geofilter.addItem(polycon, layer.name(), layer)
                elif layer.geometryType() == 1:
                    cbb_geofilter.addItem(linicon, layer.name(), layer)
                elif layer.geometryType() == 0:
                    cbb_geofilter.addItem(pointicon, layer.name(), layer)

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
                # Sorting order
                cbb_ob.setCurrentIndex(cbb_ob.findData(params.get('ob')))
                # Sorting direction
                cbb_od.setCurrentIndex(cbb_od.findData(params.get('od')))
                # Quick searches
                previous_index = cbb_saved.findData(params.get('favorite'))
                cbb_saved.setCurrentIndex(previous_index)
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
                ordered = sorted(tags.get('keywords').items(),
                                 key=operator.itemgetter(1))
                for a in ordered:
                    item = QStandardItem(a[1])
                    item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
                    item.setData(a[0], 32)
                    # As all items have been destroyed and generated again, we
                    # have to set the checkstate (checked/unchecked) according
                    # to what the user had chosen.
                    if item.data(32) in params.get('keys'):
                        item.setData(Qt.Checked, Qt.CheckStateRole)
                        model.insertRow(0, item)
                    else:
                        item.setData(Qt.Unchecked, Qt.CheckStateRole)
                        model.setItem(i, 0, item)
                    i += 1
                # Creating the first item, that is just a banner for
                # the combobox.
                first_item = QStandardItem(self.tr('---- Keywords ----'))
                icon = QIcon(':/plugins/Isogeo/resources/tag.svg')
                first_item.setIcon(icon)
                first_item.setSelectable(False)
                model.insertRow(0, first_item)
                model.itemChanged.connect(self.search)
                self.dockwidget.cbb_keywords.setModel(model)
            # When it is a saved research, we have to look in the json, and
            # check the items accordingly (quite close to the previous case)
            else:
                # Opening the json and getting the keywords
                path = self.get_path() + "/user_settings/saved_searches.json"
                with open(path) as data_file:
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
                ordered = sorted(tags.get('keywords').items(),
                                 key=operator.itemgetter(1))
                for a in ordered:
                    item = QStandardItem(a[1])
                    item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
                    item.setData(a[0], 32)
                    # As all items have been destroyed and generated again, we
                    # have to set the checkstate (checked/unchecked) according
                    # to what the user had chosen.
                    if a[0] in keywords_list:
                        item.setData(Qt.Checked, Qt.CheckStateRole)
                        model.insertRow(0, item)
                    else:
                        item.setData(Qt.Unchecked, Qt.CheckStateRole)
                        model.setItem(i, 0, item)
                    i += 1
                # Banner item
                first_item = QStandardItem(self.tr('---- Keywords ----'))
                icon = QIcon(':/plugins/Isogeo/resources/tag.svg')
                first_item.setIcon(icon)
                first_item.setSelectable(False)
                model.insertRow(0, first_item)
                model.itemChanged.connect(self.search)
                self.dockwidget.cbb_keywords.setModel(model)
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
                    saved_index = cbb_saved.findData(self.savedSearch)
                    cbb_saved.setCurrentIndex(saved_index)
                # Action : view
                if search_params.get('view'):
                    cb_view.setCheckState(Qt.Checked)
                # Action : download
                if search_params.get('download'):
                    cb_dl.setCheckState(Qt.Checked)
                # Action : other
                if search_params.get('other'):
                    cb_other.setCheckState(Qt.Checked)
                # Action : None
                if search_params.get('noaction'):
                    cb_none.setCheckState(Qt.Checked)
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
            ordered = sorted(tags.get('keywords').items(),
                             key=operator.itemgetter(1))
            for a in ordered:
                item = QStandardItem(a[1])
                item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
                item.setData(a[0], 32)
                # As all items have been destroyed and generated again, we have
                # to set the checkstate (checked/unchecked) according to what
                # the user had chosen
                item.setData(Qt.Unchecked, Qt.CheckStateRole)
                model.setItem(i, 0, item)
                i += 1
            # Banner item
            first_item = QStandardItem(self.tr('---- Keywords ----'))
            icon = QIcon(':/plugins/Isogeo/resources/tag.svg')
            first_item.setIcon(icon)
            first_item.setSelectable(False)
            model.insertRow(0, first_item)
            model.itemChanged.connect(self.search)
            self.dockwidget.cbb_keywords.setModel(model)
        # Make th checkboxes unckeckable if needed
        # View
        if 'action:view' in tags.get('actions'):
            cb_view.setEnabled(True)
        else:
            cb_view.setEnabled(False)
        # Download
        if 'action:download' in tags.get('actions'):
            cb_dl.setEnabled(True)
        else:
            cb_dl.setEnabled(False)
        # Other action
        if 'action:other' in tags.get('actions'):
            cb_other.setEnabled(True)
        else:
            cb_other.setEnabled(False)
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
            self.show_results(result)
            self.write_search_params('_current')
            self.store = True
        # Re enable all user input fields now the search function is
        # finished.
        self.switch_widgets_on_and_off('on')
        if self.results_count == 0:
            self.dockwidget.btn_show.setEnabled(False)
        # hard reset
        self.hardReset = False
        self.showResult = False

    def show_results(self, result):
        """Display the results in a table ."""
        logging.info("Show_results function called. Displaying the results")
        # Set rable rows
        if self.results_count >= 15:
            self.dockwidget.tbl_result.setRowCount(15)
        else:
            self.dockwidget.tbl_result.setRowCount(self.results_count)

        polygon_list = ["CurvePolygon", "MultiPolygon",
                        "MultiSurface", "Polygon", "PolyhedralSurface"]
        point_list = ["Point", "MultiPoint"]
        line_list = ["CircularString", "CompoundCurve", "Curve",
                     "LineString", "MultiCurve", "MultiLineString"]
        multi_list = ["Geometry", "GeometryCollection"]

        vectorformat_list = ['shp', 'dxf', 'dgn', 'filegdb', 'tab']
        rasterformat_list = ['esriasciigrid', 'geotiff',
                             'intergraphgdb', 'jpeg', 'png', 'xyz', 'ecw']

        # Get the name (and other informations) of all databases whose
        # connection is set up in QGIS
        qs = QSettings()
        if self.PostGISdict == {}:
            self.PostGISdict = tools.build_postgis_dict(qs)
        else:
            pass
        # Looping inside the table lines. For each of them, showing the title,
        # abstract, geometry type, and a button that allow to add the data
        # to the canvas.
        count = 0
        for i in result.get('results'):
            # Displaying the metadata title inside a button
            final_text = tools.format_button_title(i.get('title'))
            title_button = QPushButton(final_text)
            # Connecting the button to the full metadata popup
            title_button.pressed.connect(partial(
                self.send_details_request, md_id=i.get('_id')))
            # Putting the abstract as a tooltip on this button
            title_button.setToolTip(i.get('abstract'))
            # Insert it in column 1
            self.dockwidget.tbl_result.setCellWidget(
                count, 0, title_button)
            # Insert the modification date in column 2
            self.dockwidget.tbl_result.setItem(
                count, 1, QTableWidgetItem(
                    tools.handle_date(i.get('_modified'))))
            # Getting the geometry
            geometry = i.get('geometry')
            if geometry is not None:
                # If the geometry type is point, insert point icon in column 3
                if geometry in point_list:
                    label = QLabel()
                    pix = QPixmap(':/plugins/Isogeo/resources/point.png')
                    label.setPixmap(pix)
                    self.dockwidget.tbl_result.setCellWidget(count, 2, label)
                # If the type is polygon, insert polygon icon in column 3
                elif geometry in polygon_list:
                    label = QLabel()
                    pix = QPixmap(':/plugins/Isogeo/resources/polygon.png')
                    label.setPixmap(pix)
                    self.dockwidget.tbl_result.setCellWidget(count, 2, label)
                # If the type is line, insert line icon in column 3
                elif geometry in line_list:
                    label = QLabel()
                    pix = QPixmap(':/plugins/Isogeo/resources/line.png')
                    label.setPixmap(pix)
                    self.dockwidget.tbl_result.setCellWidget(count, 2, label)
                # If the type is multi, insert multi icon in column 3
                elif geometry in multi_list:
                    label = QLabel()
                    pix = QPixmap(':/plugins/Isogeo/resources/multi.png')
                    label.setPixmap(pix)
                    self.dockwidget.tbl_result.setCellWidget(count, 2, label)
                # If the type is TIN, insert TIN text in column 3
                elif geometry == "TIN":
                    self.dockwidget.tbl_result.setItem(
                        count, 2, QTableWidgetItem(u'TIN'))
                # If the type isn't any of the above, unknown(shouldn't happen)
                else:
                    self.dockwidget.tbl_result.setItem(
                        count, 2, QTableWidgetItem(
                            self.tr('Unknown geometry')))
            # If the data doesn't have a geometry type
            else:
                # It may be a raster, then raster icon in column 3
                if "rasterDataset" in i.get('type'):
                    label = QLabel()
                    pix = QPixmap(':/plugins/Isogeo/resources/raster.png')
                    label.setPixmap(pix)
                    self.dockwidget.tbl_result.setCellWidget(count, 2, label)
                # Or it isn't spatial, then "no geometry" icon in column 3
                else:
                    label = QLabel()
                    pix = QPixmap(':/plugins/Isogeo/resources/ban.png')
                    label.setPixmap(pix)
                    self.dockwidget.tbl_result.setCellWidget(count, 2, label)

            # We are still looping inside the table lines. For a given line, we
            # have displayed title, date, and geometry type. Now we have to
            # deal with the "add data" column. We need to see if the data can
            # be added directly, and/or using a geographical service.
            link_dict = {}

            if 'format' in i.keys():
                # If the data is a vector and the path is available, store
                # useful information in the dict
                if i.get('format') in vectorformat_list and 'path' in i:
                    path = tools.format_path(i.get('path'))
                    try:
                        open(path)
                        params = ["vector", path, i.get("title")]
                        link_dict[self.tr('Data file')] = params
                    except IOError:
                        pass
                # Same if the data is a raster
                elif i.get('format') in rasterformat_list and 'path' in i:
                    path = tools.format_path(i.get('path'))
                    try:
                        open(path)
                        params = ["raster", path]
                        link_dict[self.tr('Data file')] = params
                    except IOError:
                        pass
                # If the data is a postGIS table and the connexion has
                # been saved in QGIS.
                elif i.get('format') == 'postgis':
                    # Récupère le nom de la base de données
                    base_name = i.get('path')
                    if base_name in self.PostGISdict.keys():
                        params = {}
                        params['base_name'] = base_name
                        schema_table = i.get('name')
                        if schema_table is not None and "." in schema_table:
                            params['schema'] = schema_table.split(".")[0]
                            params['table'] = schema_table.split(".")[1]
                            link_dict[self.tr('PostGIS table')] = params
                        else:
                            pass
                    else:
                        pass
                else:
                    pass
            # We are now testing the WMS and WFS links that may be associated
            # to the metadata sheet

            # First, we look in "links". This is the old deprecated syntax.
            # At some point, all services should be associated using the new
            # one and this part of the code should be removed.
            for link in i.get('links'):
                # If the link is a WMS
                if link.get('kind') == 'wms':
                    # Test if all the needed information is in the url.
                    url = [link.get('title'), link.get('url')]
                    name_url = tools.build_wms_url(url)
                    # In which case, store it in the dict.
                    if name_url != 0:
                        link_dict[u"WMS : " + name_url[1]] = name_url
                    else:
                        pass
                # If the link is a WFS
                elif link.get('kind') == 'wfs':
                    url = [link.get('title'), link.get('url')]
                    name_url = tools.build_wfs_url(url)
                    if name_url != 0:
                        link_dict[u"WFS : " + name_url[1]] = name_url
                    else:
                        pass
                # If the link is a second level association
                elif link.get('type') == 'link':
                    _link = link.get('link')
                    if 'kind' in _link:
                        # WMS
                        if _link.get('kind') == 'wms':
                            url = [link.get('title'), link.get('url')]
                            name_url = tools.build_wms_url(url)
                            if name_url != 0:
                                link_dict[u"WMS : " + name_url[1]] = name_url
                            else:
                                pass
                        # WFS
                        elif _link.get('kind') == 'wfs':
                            url = [link.get('title'), link.get('url')]
                            name_url = tools.build_wfs_url(url)
                            if name_url != 0:
                                link_dict[u"WFS : " + name_url[1]] = name_url
                            else:
                                pass
                        else:
                            pass
                    else:
                        pass
                else:
                    pass
            # This is the new association mode. The layer and service
            # information are stored in the "serviceLayers" include, when
            # associated with a vector or raster data.
            d_type = i.get('type')
            if d_type == "vectorDataset" or d_type == "rasterDataset":
                for layer in i.get('serviceLayers'):
                    service = layer.get("service")
                    # WFS
                    if service.get("format") == "wfs":
                        name = layer.get("titles")[0].get("value", "WFS")
                        path = "{0}?typename={1}".format(service.get("path"),
                                                         layer.get("id"))
                        url = [name, path]
                        name_url = tools.build_wfs_url(url)
                        if name_url != 0:
                            link_dict[u"WFS : " + name_url[1]] = name_url
                        else:
                            pass
                    # WMS
                    elif service.get("format") == "wms":
                        name = layer.get("titles")[0].get("value", "WMS")
                        path = "{0}?layers={1}".format(service.get("path"),
                                                       layer.get("id"))
                        url = [name, path]
                        name_url = tools.build_wms_url(url)
                        if name_url != 0:
                            link_dict[u"WMS : " + name_url[1]] = name_url
                        else:
                            pass
                    else:
                        pass
            # New association mode. For services metadata sheet, the layers
            # are stored in the purposely named include : "layers".
            elif i.get('type') == "service":
                if i.get("layers") is not None:
                    # WFS
                    if i.get("format") == "wfs":
                        base_url = i.get("path")
                        for layer in i.get('layers'):
                            name = layer.get("titles")[0].get("value",
                                                              "wfslayer")
                            path = "{0}?typename={1}".format(base_url,
                                                             layer.get("id"))
                            url = [name, path]
                            name_url = tools.build_wfs_url(url)
                            if name_url != 0:
                                link_dict[u"WFS : " + name_url[1]] = name_url
                            else:
                                pass
                    # WMS
                    elif i.get("format") == "wms":
                        base_url = i.get("path")
                        for layer in i.get('layers'):
                            name = layer.get("titles")[0].get("value",
                                                              "wmslayer")
                            path = "{0}?layers={1}".format(base_url,
                                                           layer.get("id"))
                            url = [name, path]
                            name_url = tools.build_wms_url(url)
                            if name_url != 0:
                                link_dict[u"WMS : " + name_url[1]] = name_url
                            else:
                                pass
                    else:
                        pass
            else:
                pass

            # Now the plugin has tested every possibility for the layer to be
            # added. The "Add" column has to be filled accordingly.

            # If the data can't be added, just insert "can't" text.
            if link_dict == {}:
                text = self.tr("Can't be added")
                fake_button = QPushButton(text)
                fake_button.setStyleSheet("text-align: left")
                fake_button.setEnabled(False)
                self.dockwidget.tbl_result.setCellWidget(count, 3, fake_button)
            # If there is only one way for the data to be added, insert a
            # button.
            elif len(link_dict) == 1:
                text = link_dict.keys()[0]
                params = link_dict.get(text)
                if text.startswith("WMS"):
                    icon = QIcon(':/plugins/Isogeo/resources/wms.png')
                elif text.startswith("WFS"):
                    icon = QIcon(':/plugins/Isogeo/resources/wfs.png')
                elif text.startswith(self.tr('PostGIS table')):
                    icon = QIcon(':/plugins/Isogeo/resources/database.svg')
                elif text.startswith(self.tr('Data file')):
                    icon = QIcon(':/plugins/Isogeo/resources/file.svg')
                add_button = QPushButton(icon, text)
                add_button.setStyleSheet("text-align: left")
                add_button.pressed.connect(partial(self.add_layer,
                                                   layer_info=["info", params])
                                           )
                self.dockwidget.tbl_result.setCellWidget(count, 3, add_button)
            # Else, add a combobox, storing all possibilities.
            else:
                combo = QComboBox()
                for key in link_dict.keys():
                    if key.startswith("WMS"):
                        icon = QIcon(':/plugins/Isogeo/resources/wms.png')
                    elif key.startswith("WFS"):
                        icon = QIcon(':/plugins/Isogeo/resources/wfs.png')
                    elif key.startswith(self.tr('PostGIS table')):
                        icon = QIcon(':/plugins/Isogeo/resources/database.svg')
                    elif key.startswith(self.tr('Data file')):
                        icon = QIcon(':/plugins/Isogeo/resources/file.svg')
                    combo.addItem(icon, key, link_dict[key])
                combo.activated.connect(partial(self.add_layer,
                                                layer_info=["index", count]))
                self.dockwidget.tbl_result.setCellWidget(count, 3, combo)

            count += 1
        # Remove the "loading" bar
        iface.mainWindow().statusBar().removeWidget(self.bar)

    def add_loading_bar(self):
        """Display a "loading" bar."""
        self.bar = QProgressBar()
        self.bar.setRange(0, 0)
        self.bar.setFixedWidth(120)
        iface.mainWindow().statusBar().insertPermanentWidget(0, self.bar)

    def add_layer(self, layer_info):
        """Add a layer to QGIS map canvas.

        This take as an argument the index of the layer. From this index,
        search the information needed to add it in the temporary dictionnary
        constructed in the show_results function. It then adds it.
        """
        logging.info("Add_layer function called.")
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
                logging.info("Data type : vector")
                path = layer_info[1]
                name = os.path.basename(path).split(".")[0]
                layer = QgsVectorLayer(path, layer_info[2], 'ogr')
                if layer.isValid():
                    QgsMapLayerRegistry.instance().addMapLayer(layer)
                    try:
                        QgsMessageLog.logMessage("Data layer added: {}"
                                                 .format(name),
                                                 "Isogeo")
                        logging.info("Data layer added: {}".format(name))
                    except UnicodeEncodeError:
                        QgsMessageLog.logMessage(
                            "Data layer added:: {}".format(
                                name.decode("latin1")), "Isogeo")
                        logging.info("Data layer added: {}"
                                     .format(name.decode("latin1")))
                else:
                    logging.info("Layer not valid. path = {0}".format(path))
                    QMessageBox.information(
                        iface.mainWindow(),
                        self.tr('Error'),
                        self.tr('The layer is not valid.'))
            # If raster file
            elif layer_info[0] == "raster":
                logging.info("Data type : raster")
                path = layer_info[1]
                name = os.path.basename(path).split(".")[0]
                layer = QgsRasterLayer(path, name)
                if layer.isValid():
                    QgsMapLayerRegistry.instance().addMapLayer(layer)
                    logging.info("Data added")
                else:
                    logging.info("Layer not valid. path = {0}".format(path))
                    QMessageBox.information(
                        iface.mainWindow(),
                        self.tr('Error'),
                        self.tr('The layer is not valid.'))
            # If WMS link
            elif layer_info[0] == 'WMS':
                logging.info("Data type : WMS")
                url = layer_info[2]
                name = layer_info[1]
                layer = QgsRasterLayer(url, name, 'wms')
                if not layer.isValid():
                    logging.info("Layer not valid. path = {0}".format(url))
                    QMessageBox.information(
                        iface.mainWindow(),
                        self.tr('Error'),
                        self.tr("The linked service is not valid."))
                else:
                    QgsMapLayerRegistry.instance().addMapLayer(layer)
                    logging.info("Data added")
            # If WFS link
            elif layer_info[0] == 'WFS':
                logging.info("Data type : WFS")
                url = layer_info[2]
                name = layer_info[1]
                layer = QgsVectorLayer(url, name, 'WFS')
                if not layer.isValid():
                    logging.info("Layer not valid. path = {0}".format(url))
                    QMessageBox.information(
                        iface.mainWindow(),
                        self.tr('Error'),
                        self.tr("The linked service is not valid."))
                else:
                    QgsMapLayerRegistry.instance().addMapLayer(layer)
                    logging.info("Data added: ".format(name))
            else:
                pass
        # If the data is a PostGIS table
        elif type(layer_info) == dict:
            logging.info("Data type : PostGIS")
            # Give aliases to the data passed as arguement
            base_name = layer_info['base_name']
            schema = layer_info['schema']
            table = layer_info['table']
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
            if layer.isValid():
                QgsMapLayerRegistry.instance().addMapLayer(layer)
                logging.info("Data added")
            else:
                logging.info("Layer not valid. table = {0}".format(table))
                QMessageBox.information(
                    iface.mainWindow(),
                    self.tr('Error'),
                    self.tr("The PostGIS layer is not valid."))

    def save_params(self):
        """Save the widgets state/index.

        This save the current state/index of each user input so we can put them
        back to their previous state/index after they have been updated
        (cleared and filled again).
        """
        # get the data of the item which index is (get the combobox current
        # index)
        owner_param = self.dockwidget.cbb_owner.itemData(
            self.dockwidget.cbb_owner.currentIndex())
        inspire_param = self.dockwidget.cbb_inspire.itemData(
            self.dockwidget.cbb_inspire.currentIndex())
        format_param = self.dockwidget.cbb_format.itemData(
            self.dockwidget.cbb_format.currentIndex())
        srs_param = self.dockwidget.cbb_srs.itemData(
            self.dockwidget.cbb_srs.currentIndex())
        if self.dockwidget.cbb_geofilter.currentIndex() < 2:
            geofilter_param = self.dockwidget.cbb_geofilter.itemData(
                self.dockwidget.cbb_geofilter.currentIndex())
        else:
            geofilter_param = self.dockwidget.cbb_geofilter.currentText()
        favorite_param = self.dockwidget.cbb_saved.itemData(
            self.dockwidget.cbb_saved.currentIndex())
        type_param = self.dockwidget.cbb_type.itemData(
            self.dockwidget.cbb_type.currentIndex())
        operation_param = self.dockwidget.cbb_geo_op.itemData(
            self.dockwidget.cbb_geo_op.currentIndex())
        order_param = self.dockwidget.cbb_ob.itemData(
            self.dockwidget.cbb_ob.currentIndex())
        dir_param = self.dockwidget.cbb_od.itemData(
            self.dockwidget.cbb_od.currentIndex())
        # Getting the text in the search line
        text = self.dockwidget.txt_input.text()
        # Saving the keywords that are selected : if a keyword state is
        # selected, he is added to the list
        key_params = []
        for i in xrange(self.dockwidget.cbb_keywords.count()):
            if self.dockwidget.cbb_keywords.itemData(i, 10) == 2:
                key_params.append(self.dockwidget.cbb_keywords.itemData(i, 32))

        # Saving the checked checkboxes (useful for the search saving)
        if self.dockwidget.checkBox.isChecked():
            view_param = True
        else:
            view_param = False
        if self.dockwidget.checkBox_2.isChecked():
            download_param = True
        else:
            download_param = False
        if self.dockwidget.checkBox_3.isChecked():
            other_param = True
        else:
            other_param = False
        if self.dockwidget.checkBox_4.isChecked():
            noaction_param = True
        else:
            noaction_param = False

        params = {}
        params['owner'] = owner_param
        params['inspire'] = inspire_param
        params['format'] = format_param
        params['srs'] = srs_param
        params['favorite'] = favorite_param
        params['keys'] = key_params
        params['geofilter'] = geofilter_param
        params['view'] = view_param
        params['download'] = download_param
        params['other'] = other_param
        params['noaction'] = noaction_param
        params['text'] = text
        params['datatype'] = type_param
        params['operation'] = operation_param
        params['ob'] = order_param
        params['od'] = dir_param
        if params.get('geofilter') is not None:
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
            else:
                params['coord'] = self.get_coords(params.get('geofilter'))
        logging.info(params)
        return params

    def search(self):
        """Build the request url to be sent to Isogeo API.

        This builds the url, retrieving the parameters from the widgets. When
        the final url is built, it calls send_request_to_isogeo_api
        """
        logging.info("Search function called. Building the "
                     "url that is to be sent to the API")
        # Disabling all user inputs during the search function is running
        self.switch_widgets_on_and_off('off')
        # STORING THE PREVIOUS SEARCH
        if self.store is True:
            # Open json file
            path = self.get_path() + '/user_settings/saved_searches.json'
            with open(path) as data_file:
                saved_searches = json.load(data_file)
            # Store the search
            name = self.tr("Last search")
            saved_searches[name] = saved_searches['_current']
            # Refresh the quick searches comboboxes content
            search_list = saved_searches.keys()
            search_list.pop(search_list.index('_default'))
            search_list.pop(search_list.index('_current'))
            self.dockwidget.cbb_saved.clear()
            icon = QIcon(':/plugins/Isogeo/resources/bolt.png')
            self.dockwidget.cbb_saved.addItem(icon, self.tr('Quick Search'))
            self.dockwidget.cbb_modify_sr.clear()
            for i in search_list:
                self.dockwidget.cbb_saved.addItem(i, i)
                self.dockwidget.cbb_modify_sr.addItem(i, i)
            # Write modifications in the json
            with open(path, 'w') as outfile:
                    json.dump(saved_searches, outfile)
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
        self.currentUrl = tools.build_request_url(params)

        logging.info(self.currentUrl)
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
        logging.info("next_page function called. Building the url "
                     "that is to be sent to the API")
        # Testing if the user is asking for a unexisting page (ex : page 6 out
        # of 5)
        if self.page_index >= tools.calcul_nb_page(self.results_count):
            return False
        else:
            # Adding the loading bar
            self.add_loading_bar()
            # Info about the widget status
            params = self.save_params()
            # Info for _limit parameter
            self.showResult = True
            params['show'] = True
            self.switch_widgets_on_and_off('off')
            # Building up the request
            self.page_index += 1
            params['page'] = self.page_index
            # Info for _lang parameter
            params['lang'] = self.lang
            # URL BUILDING FUNCTION CALLED.
            self.currentUrl = tools.build_request_url(params)
            # Sending the request
            if self.requestStatusClear is True:
                self.send_request_to_isogeo_api(self.token)

    def previous_page(self):
        """Add the _offset parameter to the url to display previous page.

        Close to the search() function (lot of code in common) but
        triggered on the click on the change page button.
        """
        logging.info("previous_page function called. Building the "
                     "url that is to be sent to the API")
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
            self.switch_widgets_on_and_off('off')
            # Building up the request
            self.page_index -= 1
            params['page'] = self.page_index
            # Info for _lang parameter
            params['lang'] = self.lang
            # URL BUILDING FUNCTION CALLED.
            self.currentUrl = tools.build_request_url(params)
            # Sending the request
            if self.requestStatusClear is True:
                self.send_request_to_isogeo_api(self.token)

    def write_search_params(self, search_name):
        """Write a new element in the json file when a search is saved."""
        # Open the saved_search file as a dict. Each key is a search name,
        # each value is a dict containing the parameters for this search name
        bar = iface.messageBar()
        bar.pushMessage("search successfully saved.", duration=5)
        path = self.get_path() + '/user_settings/saved_searches.json'
        with open(path) as data_file:
            saved_searches = json.load(data_file)
        # If the name already exists, ask for a new one. (TO DO)

        # Write the current parameters in a dict, and store it in the saved
        # search dict
        params = self.save_params()
        params['url'] = self.currentUrl
        for i in xrange(len(params['keys'])):
            params['keyword_{0}'.format(i)] = params['keys'][i]
        params.pop('keys', None)
        saved_searches[search_name] = params
        with open(path, 'w') as outfile:
            json.dump(saved_searches, outfile)
        logging.info("Saved reseearch written. {0}".format(params))

    def set_widget_status(self):
        """Set a few variable and send the request to Isogeo API."""
        selected_search = self.dockwidget.cbb_saved.currentText()
        if selected_search != self.tr('Quick Search'):
            logging.info("Set_widget_status function called. "
                         "User is executing a saved search.")
            self.switch_widgets_on_and_off('off')
            selected_search = self.dockwidget.cbb_saved.currentText()
            path = self.get_path() + '/user_settings/saved_searches.json'
            with open(path) as data_file:
                saved_searches = json.load(data_file)
            if selected_search == "":
                self.savedSearch = '_default'
                search_params = saved_searches['_default']
            else:
                self.savedSearch = selected_search
                search_params = saved_searches[selected_search]
            self.currentUrl = search_params['url']
            if 'epsg' in search_params:
                epsg = int(iface.mapCanvas().mapRenderer(
                ).destinationCrs().authid().split(':')[1])
                if epsg == search_params['epsg']:
                    canvas = iface.mapCanvas()
                    e = search_params['extent']
                    rect = QgsRectangle(e[0], e[1], e[2], e[3])
                    canvas.setExtent(rect)
                    canvas.refresh()
                else:
                    canvas = iface.mapCanvas()
                    canvas.mapRenderer().setProjectionsEnabled(True)
                    canvas.mapRenderer().setDestinationCrs(
                        QgsCoordinateReferenceSystem(
                            search_params['epsg'],
                            QgsCoordinateReferenceSystem.EpsgCrsId))
                    e = search_params['extent']
                    rect = QgsRectangle(e[0], e[1], e[2], e[3])
                    canvas.setExtent(rect)
                    canvas.refresh()
            if self.requestStatusClear is True:
                self.send_request_to_isogeo_api(self.token)

    def save_search(self):
        """Call the write_search() function and refresh the combobox."""
        search_name = self.ask_name_popup.name.text()
        self.write_search_params(search_name)
        path = self.get_path() + '/user_settings/saved_searches.json'
        with open(path) as data_file:
            saved_searches = json.load(data_file)
        search_list = saved_searches.keys()
        search_list.pop(search_list.index('_default'))
        search_list.pop(search_list.index('_current'))
        self.dockwidget.cbb_saved.clear()
        icon = QIcon(':/plugins/Isogeo/resources/bolt.svg')
        self.dockwidget.cbb_saved.addItem(icon, self.tr('Quick Search'))
        self.dockwidget.cbb_modify_sr.clear()
        for i in search_list:
            self.dockwidget.cbb_saved.addItem(i, i)
            self.dockwidget.cbb_modify_sr.addItem(i, i)

    def rename_search(self):
        """Modify the json file in order to rename a search."""
        old_name = self.dockwidget.cbb_modify_sr.currentText()
        path = self.get_path() + '/user_settings/saved_searches.json'
        with open(path) as data_file:
            saved_searches = json.load(data_file)
        new_name = self.new_name_popup.name.text()
        saved_searches[new_name] = saved_searches[old_name]
        saved_searches.pop(old_name)
        search_list = saved_searches.keys()
        search_list.pop(search_list.index('_default'))
        search_list.pop(search_list.index('_current'))
        self.dockwidget.cbb_saved.clear()
        icon = QIcon(':/plugins/Isogeo/resources/bolt.svg')
        self.dockwidget.cbb_saved.addItem(icon, self.tr('Quick Search'))
        self.dockwidget.cbb_modify_sr.clear()
        for i in search_list:
            self.dockwidget.cbb_saved.addItem(i, i)
            self.dockwidget.cbb_modify_sr.addItem(i, i)
        with open(path, 'w') as outfile:
                json.dump(saved_searches, outfile)

    def delete_search(self):
        """Modify the json file in order to delete a search."""
        to_b_deleted = self.dockwidget.cbb_modify_sr.currentText()
        path = self.get_path() + '/user_settings/saved_searches.json'
        with open(path) as data_file:
            saved_searches = json.load(data_file)
        saved_searches.pop(to_b_deleted)
        search_list = saved_searches.keys()
        search_list.pop(search_list.index('_default'))
        search_list.pop(search_list.index('_current'))
        self.dockwidget.cbb_saved.clear()
        icon = QIcon(':/plugins/Isogeo/resources/bolt.svg')
        self.dockwidget.cbb_saved.addItem(icon, self.tr('Quick Search'))
        self.dockwidget.cbb_modify_sr.clear()
        for i in search_list:
            self.dockwidget.cbb_saved.addItem(i, i)
            self.dockwidget.cbb_modify_sr.addItem(i, i)
        with open(path, 'w') as outfile:
                json.dump(saved_searches, outfile)

    def get_coords(self, filter):
        """Get the canvas coordinates in the right format and SRS (WGS84)."""
        if filter == 'canvas':
            e = iface.mapCanvas().extent()
            current_epsg = int(iface.mapCanvas().mapRenderer(
            ).destinationCrs().authid().split(':')[1])
        else:
            layer = self.dockwidget.cbb_geofilter.itemData(filter)
            e = layer.extent()
            current_epsg = int(layer.crs().authid().split(':')[1])

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
            logging.info('Wrong EPSG')
            return False

    def reinitialize_search(self):
        """Clear all widget, putting them all back to their default value.

        Clear all widget and send a request to the API (which ends up updating
        the fields : send_request() calls handle_reply(), which calls
        update_fields())
        """
        logging.info("Reinitialize_search function called.")
        self.hardReset = True
        self.dockwidget.checkBox.setCheckState(Qt.Unchecked)
        self.dockwidget.checkBox_2.setCheckState(Qt.Unchecked)
        self.dockwidget.checkBox_3.setCheckState(Qt.Unchecked)
        self.dockwidget.checkBox_4.setCheckState(Qt.Unchecked)
        self.dockwidget.txt_input.clear()
        self.dockwidget.cbb_keywords.clear()
        self.dockwidget.cbb_type.clear()
        self.dockwidget.cbb_geofilter.clear()
        self.dockwidget.cbb_owner.clear()
        self.dockwidget.cbb_inspire.clear()
        self.dockwidget.cbb_format.clear()
        self.dockwidget.cbb_srs.clear()
        self.dockwidget.cbb_geo_op.clear()
        self.dockwidget.cbb_ob.clear()
        self.dockwidget.cbb_od.clear()
        self.search()

    def search_with_content(self):
        """Launch a search request that will end up in showing the results."""
        self.add_loading_bar()
        self.showResult = True
        self.search()

    def switch_widgets_on_and_off(self, mode):
        """Disable all the UI widgets when a request is being sent.

        Deactivate the widgets while a funcion is running so the user doesn't
        clic everywhere ending up in multiple requests being sent at the same
        time, making the plugin crash.
        """
        if mode == 'on':
            self.dockwidget.txt_input.setReadOnly(False)
            self.dockwidget.cbb_saved.setEnabled(True)
            self.dockwidget.grp_filters.setEnabled(True)
            self.dockwidget.widget.setEnabled(True)
            self.dockwidget.btn_reinit.setEnabled(True)
            self.dockwidget.btn_save.setEnabled(True)
            self.dockwidget.btn_show.setEnabled(True)
            self.dockwidget.tbl_result.setEnabled(True)

        else:
            self.dockwidget.txt_input.setReadOnly(True)
            self.dockwidget.cbb_saved.setEnabled(False)
            self.dockwidget.grp_filters.setEnabled(False)
            self.dockwidget.widget.setEnabled(False)
            self.dockwidget.btn_next.setEnabled(False)
            self.dockwidget.btn_previous.setEnabled(False)
            self.dockwidget.cbb_ob.setEnabled(False)
            self.dockwidget.cbb_od.setEnabled(False)
            self.dockwidget.btn_reinit.setEnabled(False)
            self.dockwidget.btn_save.setEnabled(False)
            self.dockwidget.btn_show.setEnabled(False)
            self.dockwidget.tbl_result.setEnabled(False)

    def show_popup(self, popup):
        """Open the pop up window that asks a name to save the search."""
        if popup == 'ask_name':
            self.ask_name_popup.show()
        elif popup == 'new_name':
            self.new_name_popup.show()

    def send_details_request(self, md_id):
        """Send a request for aditionnal info about one data."""
        logging.info("Full metatada sheet asked. Building the url.")
        self.currentUrl = "https://v1.api.isogeo.com/resources/"\
            + str(md_id)\
            + "?_include=contacts,limitations,conditions,events,feature-attributes"
        self.showDetails = True
        if self.requestStatusClear is True:
            self.send_request_to_isogeo_api(self.token)

    def show_complete_md(self, content):
        """Open the pop up window that shows the metadata sheet details."""
        logging.info("Displaying the whole metadata sheet.")
        tags = tools.get_tags(content)
        # Set the data title
        title = content.get('title')
        if title is not None:
            self.IsogeoMdDetails.lbl_title.setText(title)
        else:
            self.IsogeoMdDetails.lbl_title.setText("NR")
        # Set the data creation date
        creation_date = content.get('_created')
        if creation_date is not None:
            self.IsogeoMdDetails.val_data_crea.setText(
                tools.handle_date(creation_date))
        else:
            self.IsogeoMdDetails.val_data_crea.setText('NR')
        # Set the data last modification date
        modif_date = content.get('_modified')
        if modif_date is not None:
            self.IsogeoMdDetails.val_data_updt.setText(tools.handle_date(
                modif_date))
        else:
            self.IsogeoMdDetails.val_data_updt.setText('NR')
        # Set the date from which the data is valid
        valid_from = content.get('validFrom')
        if valid_from is not None:
            self.IsogeoMdDetails.val_valid_start.setText(tools.handle_date(
                valid_from))
        else:
            self.IsogeoMdDetails.val_valid_start.setText('NR')
        # Set the date from which the data stops being valid
        valid_to = content.get('validTo')
        if valid_to is not None:
            self.IsogeoMdDetails.val_valid_end.setText(tools.handle_date(
                valid_to))
        else:
            self.IsogeoMdDetails.val_valid_end.setText('NR')
        # Set the data owner
        if tags['owner'] != {}:
            self.IsogeoMdDetails.val_owner.setText(tags['owner'].values()[0])
        else:
            self.IsogeoMdDetails.val_owner.setText('NR')
        # Set the data coordinate system
        if tags['srs'] != {}:
            self.IsogeoMdDetails.val_srs.setText(tags['srs'].values()[0])
        else:
            self.IsogeoMdDetails.val_srs.setText('NR')
        # Set the data format
        if tags['formats'] != {}:
            self.IsogeoMdDetails.val_format.setText(
                tags['formats'].values()[0])
        else:
            self.IsogeoMdDetails.val_format.setText('NR')
        # Set the associated keywords list
        if tags['keywords'] != {}:
            keystring = ""
            for key in tags['keywords'].values():
                keystring += key + ", "
            keystring = keystring[:-2]
            self.IsogeoMdDetails.val_keywords.setText(keystring)
        else:
            self.IsogeoMdDetails.val_keywords.setText('None')
        # Set the associated INSPIRE themes list
        if tags['themeinspire'] != {}:
            inspirestring = ""
            for inspire in tags['themeinspire'].values():
                inspirestring += inspire + ", "
            inspirestring = inspirestring[:-2]
            self.IsogeoMdDetails.val_inspire_themes.setText(inspirestring)
        else:
            self.IsogeoMdDetails.val_inspire_themes.setText('None')
        # Set the data abstract
        abstract = content.get('abstract')
        if abstract is not None:
            self.IsogeoMdDetails.val_abstract.setText(content['abstract'])
        else:
            self.IsogeoMdDetails.val_abstract.setText('NR')
        # Set the collection method text
        coll_method = content.get('collectionMethod')
        if coll_method is not None:
            self.IsogeoMdDetails.val_method.setText(
                content['collectionMethod'])
        else:
            self.IsogeoMdDetails.val_method.setText('NR')
        coll_context = content.get('collectionContext')
        if coll_context is not None:
            self.IsogeoMdDetails.val_context.setText(
                content['collectionContext'])
        else:
            self.IsogeoMdDetails.val_context.setText('NR')
        # Set the data contacts (data creator, data manager, ...)
        ctc = content.get('contacts')
        if ctc is not None and ctc != []:
            ctc_text = ""
            for i in ctc:
                role = i.get('role')
                if role is not None:
                    ctc_text += "Role :\n" + role + "\n\n"
                else:
                    ctc_text += "Role :\nNR\n\n"
                contact = i.get('contact')
                if contact is not None:
                    ctc_text += "Contact :\n"
                    name = contact.get('name')
                    if name is not None:
                        ctc_text += name
                        org = contact.get('organization')
                        if org is not None:
                            ctc_text += " - " + org + "\n"
                        else:
                            ctc_text += "\n"
                    mail = contact.get('email')
                    if mail is not None:
                        ctc_text += mail + "\n"
                    phone = contact.get('phone')
                    if phone is not None:
                        ctc_text += phone + "\n"
                    adress = contact.get('addressLine1')
                    if adress is not None:
                        adress2 = contact.get('addressLine2')
                        if adress2 is not None:
                            ctc_text += adress + " - " + adress2 + "\n"
                        else:
                            ctc_text += adress + "\n"
                    zipc = contact.get('zipCode')
                    if zipc is not None:
                        ctc_text += zipc + "\n"
                    city = contact.get('city')
                    if city is not None:
                        ctc_text += city + "\n"
                    country = contact.get('countryCode')
                    if country is not None:
                        ctc_text += country + "\n"
                ctc_text += " ________________ \n\n"
            ctc_text = ctc_text[:-20]
            self.IsogeoMdDetails.val_contact.setText(ctc_text)
        else:
            self.IsogeoMdDetails.val_contact.setText("None")
        # Set the data events list (creation, multiple modifications, ...)
        self.IsogeoMdDetails.list_events.clear()
        if content['events'] != []:
            for i in content['events']:
                event = tools.handle_date(i['date']) + " : " + i['kind']
                if i['kind'] == 'update' and 'description' in i \
                        and i['description'] != '':
                    event += " (" + i['description'] + ")"
                self.IsogeoMdDetails.list_events.addItem(event)
        # Set the data usage conditions
        cond = content.get('conditions')
        if cond is not None and cond != []:
            cond_text = ""
            for i in cond:
                lc = i.get('license')
                if lc is not None:
                    name = lc.get('name')
                    if name is not None:
                        cond_text += name + "\n"
                    link = lc.get('link')
                    if link is not None:
                        cond_text += link + "\n"
                desc = i.get('description')
                if desc is not None and desc != []:
                    cond_text += desc + "\n"
                cond_text += " ________________ \n\n"
            cond_text = cond_text[:-20]
            self.IsogeoMdDetails.val_conditions.setText(cond_text)
        else:
            self.IsogeoMdDetails.val_conditions.setText("None")
        # Set the data usage limitations
        lim = content.get('limitations')
        if lim is not None and lim != []:
            lim_text = ""
            for i in lim:
                lim_type = i.get('type')
                if lim_type == 'legal':
                    restriction = i.get('restriction')
                    if restriction is not None:
                        lim_text += restriction + "\n"
                desc = i.get('description')
                if desc is not None and desc != []:
                    lim_text += desc + "\n"
                dr = i.get('directive')
                if dr is not None:
                    lim_text += "Directive :\n"
                    name = dr.get('name')
                    if name is not None:
                        lim_text += name + "\n"
                    dr_desc = dr.get('desc')
                    if dr_desc is not None:
                        lim_text += dr_desc + "\n"
                lim_text += " ________________ \n\n"
            lim_text = lim_text[:-20]
            self.IsogeoMdDetails.val_limitations.setText(lim_text)
        else:
            self.IsogeoMdDetails.val_limitations.setText("None")
        # Set the data attributes description
        if 'feature-attributes' in content:
            nb = len(content['feature-attributes'])
            self.IsogeoMdDetails.tbl_attributes.setRowCount(nb)
            count = 0
            for i in content['feature-attributes']:
                self.IsogeoMdDetails.tbl_attributes.setItem(
                    count, 0, QTableWidgetItem(i['name']))
                self.IsogeoMdDetails.tbl_attributes.setItem(
                    count, 1, QTableWidgetItem(i['dataType']))
                if 'description' in i:
                    self.IsogeoMdDetails.tbl_attributes.setItem(
                        count, 2, QTableWidgetItem(i['description']))
                count += 1
            self.IsogeoMdDetails.tbl_attributes.horizontalHeader(
            ).setStretchLastSection(True)
            self.IsogeoMdDetails.tbl_attributes.verticalHeader(
            ).setResizeMode(3)
        # Finally open the damn window
        self.IsogeoMdDetails.show()
        try:
            QgsMessageLog.logMessage("Detailed metadata displayed: {}"
                                     .format(title),
                                     "Isogeo")
        except UnicodeEncodeError:
            QgsMessageLog.logMessage("Detailed metadata displayed: {}"
                                     .format(title.encode("latin1")),
                                     "Isogeo")

    def edited_search(self):
        """On the Qline edited signal, decide weither a search has to be launched."""
        try:
            logging.info("Editing finished signal sent.")
        except AttributeError:
            pass
        if self.dockwidget.txt_input.text() == self.old_text:
            try:
                logging.info("The lineEdit text hasn't changed. So pass without sending a request.")
            except AttributeError:
                pass
            pass
        else:
            try:
                logging.info("The line Edit text changed. Calls the search function.")
            except AttributeError:
                pass
            self.search()

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
        self.currentUrl = self.oldUrl
        total = len(content)
        if total == 1:
            text = self.tr(u"<html><p><b><br/>This plugin is powered by 1 share.<br/></b></p>")
        else:
            text = self.tr(u"<html><p><b><br/>This plugin is powered by {0} shares.<br/></b></p>").format(total)
        text += u"<p>   ___________________________________________________________________   </p>"
        for share in content:
            text += u"<p><b>{0}</p></b>".format(share['name'])
            text += self.tr(u"<p>Modified: {0}</p>").format(tools.handle_date(share['_modified']))
            text += self.tr(u"<p>Contact: {0}</p>").format(share['_creator']['contact']['name'])
            text += self.tr(u"<p>Applications powered by this share:</p>")
            for a in share['applications']:
                text += u"<p>   - <a href='{0}'>{1}</a></p>".format(a['url'], a['name'])
            text += u"<p>   ___________________________________________________________________   </p>"
        #text = text[:-80]
        text += u"</html>"
        self.dockwidget.txt_shares.setText(text)

    # --------------------------------------------------------------------------

    # This function is launched when the plugin is activated.
    def run(self):
        """Run method that loads and starts the plugin."""
        if not self.pluginIsActive:
            self.pluginIsActive = True

            # print "** STARTING Isogeo"

            # dockwidget may not exist if:
            #    first run of plugin
            #    removed on close (see self.onClosePlugin method)
            if self.dockwidget is None:
                # Create the dockwidget (after translation) and keep reference
                self.dockwidget = IsogeoDockWidget()
                logging.info("Plugin load time: {}"
                             .format(plugin_times.get("isogeo_search_engine")))

            # connect to provide cleanup on closing of dockwidget
            self.dockwidget.closingPlugin.connect(self.onClosePlugin)

            # show the dockwidget
            # TODO: fix to allow choice of dock location
            self.iface.addDockWidget(Qt.RightDockWidgetArea, self.dockwidget)
            self.dockwidget.show()

        # Fixing a qgis.core bug that shows a warning banner "connexion time
        # out" whenever a request is sent (even successfully) See :
        # http://gis.stackexchange.com/questions/136369/download-file-from-network-using-pyqgis-2-x#comment299999_136427
        iface.messageBar().widgetAdded.connect(iface.messageBar().clearWidgets)

        """ --- CONNECTING FUNCTIONS --- """
        # Write in the config file when the user accept the authentification
        # window
        self.auth_prompt_form.accepted.connect(self.write_ids_and_test)
        # Connecting the comboboxes to the search function
        self.dockwidget.cbb_owner.activated.connect(self.search)
        self.dockwidget.cbb_inspire.activated.connect(self.search)
        self.dockwidget.cbb_format.activated.connect(self.search)
        self.dockwidget.cbb_srs.activated.connect(self.search)
        self.dockwidget.cbb_geofilter.activated.connect(self.search)
        self.dockwidget.cbb_type.activated.connect(self.search)
        # Connecting the text input to the search function
        self.dockwidget.txt_input.editingFinished.connect(self.edited_search)
        # Connecting the checkboxes to the search function
        self.dockwidget.checkBox.clicked.connect(self.search)
        self.dockwidget.checkBox_2.clicked.connect(self.search)
        self.dockwidget.checkBox_3.clicked.connect(self.search)
        self.dockwidget.checkBox_4.clicked.connect(self.search)
        # Connecting the radio buttons

        # Connecting the previous and next page buttons to their functions
        self.dockwidget.btn_next.pressed.connect(self.next_page)
        self.dockwidget.btn_previous.pressed.connect(self.previous_page)
        # Connecting the bug tracker button to its function
        self.dockwidget.btn_report.pressed.connect(
            partial(tools.open_webpage,
                    link='https://github.com/isogeo/isogeo-plugin-qgis/issues'
                    ))

        self.dockwidget.btn_help.pressed.connect(
            partial(tools.open_webpage,
                    link="https://github.com/isogeo/isogeo-plugin-qgis/wiki"
                    ))
        # Connecting the "reinitialize search button" to a search without
        # filters
        self.dockwidget.btn_reinit.pressed.connect(self.reinitialize_search)
        # Change user
        self.dockwidget.btn_change_user.pressed.connect(
            self.auth_prompt_form.show)
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
        self.ask_name_popup.accepted.connect(self.save_search)
        # Button 'rename search' connected to the opening of the pop up that
        # asks for a new name
        self.dockwidget.btn_rename_sr.pressed.connect(
            partial(self.show_popup, popup='new_name'))
        # Connect the accepted signal of the popup to the function that rename
        # a search.
        self.new_name_popup.accepted.connect(self.rename_search)
        # Connect the delete button to the delete function
        self.dockwidget.btn_delete_sr.pressed.connect(self.delete_search)
        # Connect the activation of the "saved search" combobox with the
        # set_widget_status function
        self.dockwidget.cbb_saved.activated.connect(
            self.set_widget_status)
        # G default
        self.dockwidget.btn_default.pressed.connect(
            partial(self.write_search_params, search_name='_default'))

        self.auth_prompt_form.btn_account_new.pressed.connect(partial(
            tools.mail_to_isogeo, lang=self.lang))

        self.dockwidget.tabWidget.currentChanged.connect(self.ask_shares_info)

        self.dockwidget.txt_shares.setOpenLinks(False)
        self.dockwidget.txt_shares.anchorClicked.connect(tools.open_webpage)

        """ --- Actions when the plugin is launched --- """
        # self.test_config_file_existence()
        self.test_proxy_configuration()
        self.user_authentication()
