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
    QStandardItemModel, QStandardItem, QComboBox, QPushButton, QLabel, QPixmap

# Initialize Qt resources from file resources.py
import resources

# Import the code for the DockWidget
from isogeo_dockwidget import IsogeoDockWidget

# Import du code des autres fenêtres
from dlg_authentication import IsogeoAuthentication
from ask_research_name import ask_research_name
from isogeo_dlg_mdDetails import IsogeoMdDetails

import os.path

# Ajoutés par moi
from qgis.utils import iface, QGis, reloadPlugin
from qgis.core import QgsNetworkAccessManager, QgsPoint, \
    QgsCoordinateReferenceSystem, QgsCoordinateTransform, QgsVectorLayer, \
    QgsMapLayerRegistry, QgsRasterLayer, QgsDataSourceURI, QgsMessageLog, \
    QgsRectangle
from PyQt4.QtNetwork import QNetworkRequest
import ConfigParser
import json
import base64
import urllib
import logging
from logging.handlers import RotatingFileHandler
import platform  # about operating systems
import datetime
import webbrowser
from functools import partial
import db_manager.db_plugins.postgis.connector as con
import operator

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

class Isogeo:
    """QGIS Plugin Implementation."""

    logging.info('\n\n\t============== Isogeo Search Engine for QGIS =============')
    logging.info('OS: {0}'.format(platform.platform()))
    logging.info('QGIS Version: {0}'.format(QGis.QGIS_VERSION))

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

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Isogeo')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'Isogeo')
        self.toolbar.setObjectName(u'Isogeo')

        # print "** INITIALIZING Isogeo"

        self.pluginIsActive = False

        self.dockwidget = None

        self.auth_prompt_form = IsogeoAuthentication()

        self.ask_name_popup = ask_research_name()

        self.IsogeoMdDetails = IsogeoMdDetails()

        self.savedResearch = "first"

        self.loopCount = 0

        self.hardReset = False

        self.showResult = False

        self.showDetails = False

        self.PostGISdict = {}

        self.currentUrl = 'https://v1.api.isogeo.com/resources/search?_limit=15&_include=links'

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
        reloadPlugin('isogeo_plugin')

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

    def get_plugin_path(self):
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
                                logging.info("A proxy is set up both in QGIS and the OS and they match => Proxy config : OK")
                                pass
                            else:
                                QMessageBox.information(iface.mainWindow(
                                ), self.tr('Alert'), self.tr("Proxy issue : \nQGIS and your OS have different proxy set ups."))
                        else:
                            QMessageBox.information(iface.mainWindow(
                                ), self.tr('Alert'), self.tr("Proxy issue : \nQGIS and your OS have different proxy set ups."))
                    elif len(elements) == 3 and elements[0] == 'http':
                        host_short = elements[1][2:]
                        host_long = elements[0] + ':' + elements[1]
                        port = elements[2]
                        qgis_host = s.value("proxy/proxyHost", "")
                        qgis_port = s.value("proxy/proxyPort", "")
                        if qgis_host == host_short or qgis_host == host_long:
                            if qgis_port == port:
                                logging.info("A proxy is set up both in QGIS and the OS and they match => Proxy config : OK")
                                pass
                            else:
                                logging.info("OS and QGIS proxy ports do not match. => Proxy config : not OK")
                                QMessageBox.information(iface.mainWindow(
                                ), self.tr('Alert'), self.tr("Proxy issue : \nQGIS and your OS have different proxy set ups."))
                        else:
                            logging.info("OS and QGIS proxy hosts do not match. => Proxy config : not OK")
                            QMessageBox.information(iface.mainWindow(
                                ), self.tr('Alert'), self.tr("Proxy issue : \nQGIS and your OS have different proxy set ups."))
            else:
                logging.info("OS uses a proxy but it isn't set up in QGIS. => Proxy config : not OK")
                QMessageBox.information(iface.mainWindow(
                                ), self.tr('Alert'), self.tr("Proxy issue : \nYou have a proxy set up on your OS but none in QGIS.\nPlease set it up in 'Preferences/Options/Network'."))

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
            logging.info("User_authentication function is trying to get a token from the id/secret")
            self.ask_for_token(self.user_id, self.user_secret)
        else:
            logging.info("No id/secret. User authentication function is showing the auth window.")
            self.auth_prompt_form.show()

    def write_ids_and_test(self):
        """Store the id & secret and launch the test function.

        Called when the authentification window is closed,
        it stores the values in the file, then call the
        user_authentification function to test them.
        """
        logging.info("Authentication window accepted. Writting id/secret in QSettings.")
        user_id = self.auth_prompt_form.ent_app_id.text()
        user_secret = self.auth_prompt_form.\
            ent_app_secret.text()
        s = QSettings()
        s.setValue("isogeo-plugin/user-auth/id", user_id)
        s.setValue("isogeo-plugin/user-auth/secret", user_secret)

        self.user_authentification()

    def ask_for_token(self, c_id, c_secret):
        """Ask a token from Isogeo API authentification page.

        This send a POST request to Isogeo API with the user id and secret in
        its header. The API should return an access token
        """
        headervalue = "Basic " + base64.b64encode(c_id + ":" + c_secret)
        data = urllib.urlencode({"grant_type": "client_credentials"})
        databyte = QByteArray()
        databyte.append(data)
        manager = QgsNetworkAccessManager.instance()
        url = QUrl('https://id.api.isogeo.com/oauth/token')
        request = QNetworkRequest(url)
        request.setRawHeader("Authorization", headervalue)
        self.token_reply = manager.post(request, databyte)
        self.token_reply.finished.connect(self.handle_token)

        QgsMessageLog.logMessage("Authentication succeeded", "Isogeo")

    def handle_token(self):
        """Handle the API answer when asked for a token.

        This handles the API answer. If it has sent an access token, it calls
        the initialization function. If not, it raises an error, and ask
        for new IDs
        """
        logging.info("Asked a token and got a reply from the API.")
        bytarray = self.token_reply.readAll()
        content = str(bytarray)
        parsed_content = json.loads(content)
        if 'access_token' in parsed_content:
            logging.info("The API reply is an access token : the request worked as expected.")
            # TO DO : Appeler la fonction d'initialisation
            self.token = "Bearer " + parsed_content['access_token']
            if self.savedResearch == "first":
                self.set_widget_status()
            else:
                self.send_request_to_Isogeo_API(self.token)
        # TO DO : Distinguer plusieurs cas d'erreur
        elif 'error' in parsed_content:
            logging.info("The API reply is an error. Id and secret must be invalid. Asking for them again.")
            QMessageBox.information(
                iface.mainWindow(), self.tr('Error'), parsed_content['error'])
            self.auth_prompt_form.show()
        else:
            logging.info("The API reply has an unexpected form : {0}".format(parsed_content))
            QMessageBox.information(
                iface.mainWindow(), self.tr('Error'), self.tr('Unknown error'))

    def send_request_to_Isogeo_API(self, token, limit=15):
        """Send a content url to the Isogeo API.

        This takes the currentUrl variable and send a request to this url,
        using the token variable.
        """
        myurl = QUrl(self.currentUrl)
        request = QNetworkRequest(myurl)
        request.setRawHeader("Authorization", token)
        manager = QgsNetworkAccessManager.instance()
        self.API_reply = manager.get(request)
        self.API_reply.finished.connect(self.handle_API_reply)

    def handle_API_reply(self):
        """Handle the different possible Isogeo API answer.

        This is called when the answer from the API is finished. If it's
        content, it calls update_fields(). If it isn't, it means the token has
        expired, and it calls ask_for_token()
        """
        logging.info("Request sent to API and reply received.")
        bytarray = self.API_reply.readAll()
        content = str(bytarray)
        if self.API_reply.error() == 0 and content != "":
            logging.info("Reply is a result json.")
            if self.showDetails is False:
                self.loopCount = 0
                parsed_content = json.loads(content)
                self.update_fields(parsed_content)
            else:
                self.showDetails = False
                self.loopCount = 0
                parsed_content = json.loads(content)
                self.show_complete_md(parsed_content)

        elif self.API_reply.error() == 204:
            logging.info("Token expired. Renewing it.")
            self.loopCount = 0
            self.ask_for_token(self.user_id, self.user_secret)
        elif content == "":
            logging.info("Empty reply. Weither no catalog is shared with the plugin, or there is a problem (2 requests sent together)")
            if self.loopCount < 3:
                self.loopCount += 1
                del self.API_reply
                del self.token_reply
                self.ask_for_token(self.user_id, self.user_secret)
            else:
                QMessageBox.information(iface.mainWindow(
                ), self.tr('Error'), self.tr('The script is looping. Make sure you shared a catalog with the plugin. If so, please report this on the bug tracker.'))
        else:
            QMessageBox.information(iface.mainWindow(), self.tr('Error'),
                                    self.tr('You are facing an unknown error. Code: ') + str(
                self.API_reply.error()) + "\nPlease report tis on the bug tracker.")

    def update_fields(self, result):
        """Update the fields content.

        This takes an API answer and update the fields accordingly. It also
        calls show_results in the end. This may change, so results would be
        shown only when a specific button is pressed.
        """
        logging.info("Update_fields function called on the API reply. reset = {0}, savedResearch ={1}".format(self.hardReset, self.save_research))
        tags = self.get_tags(result)
        # Getting the index of selected items in each combobox
        self.params = self.save_params()
        # Show how many results there are
        self.results_count = result['total']
        self.dockwidget.btn_show.setText(
            str(self.results_count) + u" résultats")
        # Setting the number of rows in the result table

        self.nb_page = str(self.calcul_nb_page(self.results_count))
        self.dockwidget.lbl_page.setText(
            "page " + str(self.page_index) + self.tr(' on ') + self.nb_page)
        # clearing the previous fields
        self.dockwidget.tbl_result.clearContents()
        self.dockwidget.tbl_result.setRowCount(0)

        self.dockwidget.cbb_inspire.clear()
        self.dockwidget.cbb_owner.clear()
        self.dockwidget.cbb_format.clear()
        self.dockwidget.cbb_srs.clear()
        self.dockwidget.cbb_operation.clear()

        path = self.get_plugin_path() + '/saved_researches.json'
        with open(path) as data_file:
            saved_researches = json.load(data_file)
        research_list = saved_researches.keys()
        research_list.pop(research_list.index('_default'))
        self.dockwidget.cbb_saved.clear()
        self.dockwidget.cbb_saved.addItem(" - ")
        for i in research_list:
            self.dockwidget.cbb_saved.addItem(i, i)

        # Initiating the "nothing selected" item in each combobox
        self.dockwidget.cbb_inspire.addItem(" - ")
        self.dockwidget.cbb_owner.addItem(" - ")
        self.dockwidget.cbb_format.addItem(" - ")
        self.dockwidget.cbb_srs.addItem(" - ")
        dict_operation = {self.tr('Intersects'): "intersects",
                          self.tr('within'): "within",
                          self.tr('contains'): "contains"}
        for operationKey in dict_operation.keys():
            self.dockwidget.cbb_operation.addItem(
                operationKey, dict_operation[operationKey])
        if self.hardReset is True:
            self.dockwidget.cbb_operation.setCurrentIndex(
                self.dockwidget.cbb_operation.findData("intersects"))
        else:
            self.dockwidget.cbb_operation.setCurrentIndex(
                self.dockwidget.cbb_operation.findData(self.params['operation']))
        # Creating combobox items, with their displayed text, and their value
        ordered = sorted(tags['owner'].items(), key=operator.itemgetter(1))
        for i in ordered:
            self.dockwidget.cbb_owner.addItem(i[1], i[0])
        ordered = sorted(tags['themeinspire'].items(), key=operator.itemgetter(1))
        for i in ordered:
            self.dockwidget.cbb_inspire.addItem(i[1], i[0])
        ordered = sorted(tags['formats'].items(), key=operator.itemgetter(1))
        for i in ordered:
            self.dockwidget.cbb_format.addItem(i[1], i[0])
        ordered = sorted(tags['srs'].items(), key=operator.itemgetter(1))
        for i in ordered:
            self.dockwidget.cbb_srs.addItem(i[1], i[0])

        # Putting all the comboboxes selected index to their previous
        # location. Necessary as all comboboxes items have been removed and
        # put back in place. We do not want each combobox to go back to their
        # default selected item
        if self.hardReset is False:
            self.dockwidget.cbb_owner.setCurrentIndex(
                self.dockwidget.cbb_owner.findData(self.params['owner']))
            self.dockwidget.cbb_inspire.setCurrentIndex(
                self.dockwidget.cbb_inspire.findData(self.params['inspire']))
            # Set the combobox current index to (get the index of the item
            # which data is (saved data))
            self.dockwidget.cbb_format.setCurrentIndex(
                self.dockwidget.cbb_format.findData(self.params['format']))
            self.dockwidget.cbb_srs.setCurrentIndex(
                self.dockwidget.cbb_srs.findData(self.params['srs']))
            self.dockwidget.cbb_saved.setCurrentIndex(
                self.dockwidget.cbb_saved.findData(
                    self.params['favorite']))

            # Filling the keywords special combobox (whose items are checkable)
            if self.savedResearch is False:
                self.model = QStandardItemModel(5, 1)  # 5 rows, 1 col
                i = 1
                ordered = sorted(tags['keywords'].items(), key=operator.itemgetter(1))
                for a in ordered:
                    item = QStandardItem(a[1])
                    item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
                    item.setData(a[0], 32)
                    # As all items have been destroyed and generated again, we
                    # have to set the checkstate (checked/unchecked) according
                    # to what the user had chosen
                    if item.data(32) in self.params['keys']:
                        item.setData(Qt.Checked, Qt.CheckStateRole)
                        self.model.insertRow(0, item)
                    else:
                        item.setData(Qt.Unchecked, Qt.CheckStateRole)
                        self.model.setItem(i, 0, item)
                    i += 1
                first_item = QStandardItem(self.tr('---- Keywords ----'))
                first_item.setSelectable(False)
                self.model.insertRow(0, first_item)
                self.model.itemChanged.connect(self.search)
                self.dockwidget.cbb_keywords.setModel(self.model)
            else:
                path = self.get_plugin_path() + '/saved_researches.json'
                with open(path) as data_file:
                    saved_researches = json.load(data_file)
                research_params = saved_researches[self.savedResearch]
                keywords_list = []
                for a in research_params.keys():
                    if a.startswith("keyword"):
                        keywords_list.append(research_params[a])
                self.model = QStandardItemModel(5, 1)  # 5 rows, 1 col
                i = 1
                ordered = sorted(tags['keywords'].items(), key=operator.itemgetter(1))
                for a in ordered:
                    item = QStandardItem(a[1])
                    item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
                    item.setData(a[0], 32)
                    # As all items have been destroyed and generated again, we
                    # have to set the checkstate (checked/unchecked) according
                    # to what the user had chosen.
                    if a[0] in keywords_list:
                        item.setData(Qt.Checked, Qt.CheckStateRole)
                        self.model.insertRow(0, item)
                    else:
                        item.setData(Qt.Unchecked, Qt.CheckStateRole)
                        self.model.setItem(i, 0, item)
                    i += 1
                first_item = QStandardItem(self.tr('---- Keywords ----'))
                first_item.setSelectable(False)
                self.model.insertRow(0, first_item)
                self.model.itemChanged.connect(self.search)
                self.dockwidget.cbb_keywords.setModel(self.model)
        else:
            self.model = QStandardItemModel(5, 1)  # 5 rows, 1 col
            i = 1
            ordered = sorted(tags['keywords'].items(), key=operator.itemgetter(1))
            for a in ordered:
                item = QStandardItem(a[1])
                item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
                item.setData(a[0], 32)
                # As all items have been destroyed and generated again, we have
                # to set the checkstate (checked/unchecked) according to what
                # the user had chosen
                item.setData(Qt.Unchecked, Qt.CheckStateRole)
                self.model.setItem(i, 0, item)
                i += 1
            first_item = QStandardItem(self.tr('---- Keywords ----'))
            first_item.setSelectable(False)
            self.model.insertRow(0, first_item)
            self.model.itemChanged.connect(self.search)
            self.dockwidget.cbb_keywords.setModel(self.model)

        # Trying to make th checkboxes and radio buttons unckeckable if needed
        # View
        if 'action:view' in tags['actions']:
            self.dockwidget.checkBox.setEnabled(True)
        else:
            self.dockwidget.checkBox.setEnabled(False)
        # Download
        if 'action:download' in tags['actions']:
            self.dockwidget.checkBox_2.setEnabled(True)
        else:
            self.dockwidget.checkBox_2.setEnabled(False)
        # Other action
        if 'action:other' in tags['actions']:
            self.dockwidget.checkBox_3.setEnabled(True)
        else:
            self.dockwidget.checkBox_3.setEnabled(False)
        # Vector
        if 'type:vector-dataset' in tags['type']:
            self.dockwidget.rdb_vector.setEnabled(True)
        else:
            self.dockwidget.rdb_vector.setEnabled(False)
        # Raster
        if 'type:raster-dataset' in tags['type']:
            self.dockwidget.rdb_raster.setEnabled(True)
        else:
            self.dockwidget.rdb_raster.setEnabled(False)
        # Resource
        if 'type:resource' in tags['type']:
            self.dockwidget.rdb_resource.setEnabled(True)
        else:
            self.dockwidget.rdb_resource.setEnabled(False)
        # Service
        if 'type:service' in tags['type']:
            self.dockwidget.rdb_service.setEnabled(True)
        else:
            self.dockwidget.rdb_service.setEnabled(False)

        self.dockwidget.btn_show.setStyleSheet(
            "QPushButton "
            "{background-color: rgb(255, 144, 0); color: white}")

        # Putting the comboboxs to the right indexes in the case of a saved
        # research.
        if self.savedResearch is not False:
            path = self.get_plugin_path() + '/saved_researches.json'
            with open(path) as data_file:
                saved_researches = json.load(data_file)
            research_params = saved_researches[self.savedResearch]
            self.dockwidget.txt_input.setText(research_params['text'])
            self.dockwidget.cbb_owner.setCurrentIndex(
                self.dockwidget.cbb_owner.findData(research_params['owner']))
            self.dockwidget.cbb_inspire.setCurrentIndex(
                self.dockwidget.cbb_inspire.findData(research_params['inspire']))
            self.dockwidget.cbb_format.setCurrentIndex(
                self.dockwidget.cbb_format.findData(research_params['format']))
            self.dockwidget.cbb_srs.setCurrentIndex(
                self.dockwidget.cbb_srs.findData(research_params['srs']))
            self.dockwidget.cbb_operation.setCurrentIndex(
                self.dockwidget.cbb_operation.findData(
                    research_params['operation']))
            self.dockwidget.cbb_saved.setCurrentIndex(
                self.dockwidget.cbb_saved.findData(self.savedResearch))
            if research_params['view']:
                self.dockwidget.checkBox.setCheckState(Qt.Checked)
            if research_params['download']:
                self.dockwidget.checkBox_2.setCheckState(Qt.Checked)
            if research_params['other']:
                self.dockwidget.checkBox_3.setCheckState(Qt.Checked)
            if research_params['geofilter']:
                self.dockwidget.checkBox_4.setCheckState(Qt.Checked)
            if research_params['datatype'] is not False:
                if research_params['datatype'] == "vector":
                    self.dockwidget.rdb_vector.setChecked(True)
                elif research_params['datatype'] == "raster":
                    self.dockwidget.rdb_raster.setChecked(True)
                elif research_params['datatype'] == "resource":
                    self.dockwidget.rdb_resource.setChecked(True)
                elif research_params['datatype'] == "service":
                    self.dockwidget.rdb_service.setChecked(True)
            self.savedResearch = False

        # Show result, if we want them to be shown (button 'show result', 'next
        # page' or 'previous page' pressed)
        if self.showResult is True:
            self.dockwidget.btn_next.setEnabled(True)
            self.dockwidget.btn_previous.setEnabled(True)
            self.dockwidget.btn_show.setStyleSheet("")
            self.show_results(result)
        # Re enable all user input fields now the research function is
        # finished.
        self.switch_widgets_on_and_off('on')
        # hard reset
        self.hardReset = False
        self.showResult = False

    def show_results(self, result):
        """Display the results in a table ."""
        logging.info("Show_results function called. Displaying the results")
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
                             'intergraphgdb', 'jpeg', 'png', 'xyz']

        # Get the name (and other informations) of all databases whose
        # connection is set up in QGIS
        qs = QSettings()
        if self.PostGISdict == {}:
            for k in sorted(qs.allKeys()):
                if k.startswith("PostgreSQL/connections/")\
                        and k.endswith("/database"):
                    if len(k.split("/")) == 4:
                        connection_name = k.split("/")[2]
                        password_saved = qs.value('PostgreSQL/connections/' +
                                                  connection_name +
                                                  '/savePassword')
                        user_saved = qs.value('PostgreSQL/connections/' +
                                              connection_name +
                                              '/saveUsername')
                        if password_saved == 'true' and user_saved == 'true':
                            dictionary = {'name':
                                          qs.value('PostgreSQL/connections/' +
                                                   connection_name +
                                                   '/database'),
                                          'host':
                                          qs.value('PostgreSQL/connections/' +
                                                   connection_name +
                                                   '/host'),
                                          'port':
                                          qs.value('PostgreSQL/connections/' +
                                                   connection_name +
                                                   '/port'),
                                          'username':
                                          qs.value('PostgreSQL/connections/' +
                                                   connection_name +
                                                   '/username'),
                                          'password':
                                          qs.value('PostgreSQL/connections/' +
                                                   connection_name +
                                                   '/password')}
                            self.PostGISdict[
                                qs.value('PostgreSQL/connections/' +
                                         connection_name +
                                         '/database')
                            ] = dictionary
        # Looping on the table line. For each of them, showing the title, the
        # abstract, the geometry type, and a button that allow to add the data
        # to the canvas.
        count = 0
        for i in result['results']:
            words = i['title'].split(' ')
            line_length = 0
            lines = []
            string = ""
            for word in words:
                line_length += len(word)
                if line_length < 22:
                    string += word + " "
                else:
                    line_length = len(word)
                    lines.append(string[:-1])
                    string = word + " "
            if string[:-1] not in lines:
                lines.append(string[:-1])
            final_text = ""
            for line in lines:
                final_text += line + "\n"
            final_text = final_text[:-1]
            button = QPushButton(final_text)
            button.pressed.connect(partial(
                self.send_details_request, md_id=i['_id']))
            try:
                button.setToolTip(i['abstract'])
            except:
                pass
            self.dockwidget.tbl_result.setCellWidget(
                count, 0, button)
            self.dockwidget.tbl_result.setItem(
                count, 1, QTableWidgetItem(self.handle_date(i['_modified'])))
            try:
                geometry = i['geometry']
                if geometry in point_list:
                    label = QLabel()
                    pix = QPixmap(':/plugins/Isogeo/resources/point.png')
                    label.setPixmap(pix)
                    self.dockwidget.tbl_result.setCellWidget(count, 2, label)
                elif geometry in polygon_list:
                    label = QLabel()
                    pix = QPixmap(':/plugins/Isogeo/resources/polygon.png')
                    label.setPixmap(pix)
                    self.dockwidget.tbl_result.setCellWidget(count, 2, label)
                elif geometry in line_list:
                    label = QLabel()
                    pix = QPixmap(':/plugins/Isogeo/resources/line.png')
                    label.setPixmap(pix)
                    self.dockwidget.tbl_result.setCellWidget(count, 2, label)
                elif geometry in multi_list:
                    label = QLabel()
                    pix = QPixmap(':/plugins/Isogeo/resources/multi.png')
                    label.setPixmap(pix)
                    self.dockwidget.tbl_result.setCellWidget(count, 2, label)
                elif geometry == "TIN":
                    self.dockwidget.tbl_result.setItem(
                        count, 2, QTableWidgetItem(u'TIN'))
                else:
                    self.dockwidget.tbl_result.setItem(
                        count, 2, QTableWidgetItem(self.tr('Unknown geometry')))
            except:
                if "type:raster-dataset" in i['tags']:
                    label = QLabel()
                    pix = QPixmap(':/plugins/Isogeo/resources/raster.png')
                    label.setPixmap(pix)
                    self.dockwidget.tbl_result.setCellWidget(count, 2, label)
                else:
                    label = QLabel()
                    pix = QPixmap(':/plugins/Isogeo/resources/none.png')
                    label.setPixmap(pix)
                    self.dockwidget.tbl_result.setCellWidget(count, 2, label)

            combo = QComboBox()
            link_dict = {}

            if 'format' in i.keys():
                if i['format'] in vectorformat_list and 'path' in i:
                    path = self.format_path(i['path'])
                    try:
                        test_path = open(path)
                        params = ["vector", path]
                        link_dict[self.tr('Data file')] = params

                    except IOError:
                        pass

                elif i['format'] in rasterformat_list and 'path' in i:
                    path = self.format_path(i['path'])
                    try:
                        test_path = open(path)
                        params = ["raster", path]
                        link_dict[self.tr('Data file')] = params
                    except IOError:
                        pass

                elif i['format'] == 'postgis':
                    # Récupère le nom de la base de données
                    base_name = i['path']

                    if base_name in self.PostGISdict.keys():
                        params = {}
                        params['base_name'] = base_name
                        params['schema'] = i['name'].split(".")[0]
                        params['table'] = i['name'].split(".")[1]
                        link_dict[self.tr('PostGIS table')] = params

            for link in i['links']:
                if link['kind'] == 'wms':
                    name_url = self.build_wms_url(link['url'])
                    if name_url != 0:
                        link_dict[u"WMS : " + name_url[1]] = name_url
                elif link['kind'] == 'wfs':
                    name_url = self.build_wfs_url(link['url'])
                    if name_url != 0:
                        link_dict[u"WFS : " + name_url[1]] = name_url
                elif link['type'] == 'link':
                    if link['link']['kind'] == 'wms':
                        name_url = self.build_wms_url(link['url'])
                        if name_url != 0:
                            link_dict[u"WMS : " + name_url[1]] = name_url
                    elif link['link']['kind'] == 'wfs':
                        name_url = self.build_wfs_url(link['url'])
                        if name_url != 0:
                            link_dict[u"WFS : " + name_url[1]] = name_url

            for key in link_dict.keys():
                combo.addItem(key, link_dict[key])

            combo.activated.connect(partial(self.add_layer, layer_index=count))
            self.dockwidget.tbl_result.setCellWidget(count, 3, combo)

            count += 1
        self.dockwidget.tbl_result.horizontalHeader().setResizeMode(1)
        self.dockwidget.tbl_result.horizontalHeader().setResizeMode(1, 0)
        self.dockwidget.tbl_result.horizontalHeader().setResizeMode(2, 0)
        self.dockwidget.tbl_result.horizontalHeader().resizeSection(1, 80)
        self.dockwidget.tbl_result.horizontalHeader().resizeSection(2, 50)
        self.dockwidget.tbl_result.verticalHeader().setResizeMode(3)

    def add_layer(self, layer_index):
        """Add a layer to QGIS map canvas.

        This take as an argument the index of the layer. From this index,
        search the information needed to add it in the temporary dictionnary
        constructed in the show_results function. It then adds it.
        """
        logging.info("Add_layer function called.")
        combobox = self.dockwidget.tbl_result.cellWidget(layer_index, 3)
        layer_info = combobox.itemData(combobox.currentIndex())
        if type(layer_info) == list:
            if layer_info[0] == "vector":
                logging.info("Data type : vector")
                path = layer_info[1]
                name = os.path.basename(path).split(".")[0]
                layer = QgsVectorLayer(path, name, 'ogr')
                if layer.isValid():
                    QgsMapLayerRegistry.instance().addMapLayer(layer)
                    logging.info("Data added")
                else:
                    logging.info("Layer not valid. path = {0}".format(path))
                    QMessageBox.information(
                        iface.mainWindow(), self.tr('Error'),
                                            self.tr('The layer is not valid.'))

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
                        iface.mainWindow(), self.tr('Error'),
                                            self.tr('The layer is not valid.'))

            elif layer_info[0] == 'WMS':
                logging.info("Data type : WMS")
                url = layer_info[2]
                name = layer_info[1]
                layer = QgsRasterLayer(url, name, 'wms')
                if not layer.isValid():
                    logging.info("Layer not valid. path = {0}".format(url))
                    QMessageBox.information(
                        iface.mainWindow(), self.tr('Error'),
                                            self.tr("The linked service is not valid."))
                else:
                    QgsMapLayerRegistry.instance().addMapLayer(layer)
                    logging.info("Data added")

            elif layer_info[0] == 'WFS':
                logging.info("Data type : WFS")
                url = layer_info[2]
                name = layer_info[1]
                layer = QgsVectorLayer(url, name, 'WFS')
                if not layer.isValid():
                    logging.info("Layer not valid. path = {0}".format(url))
                    QMessageBox.information(
                        iface.mainWindow(), self.tr('Error'),
                                            self.tr("The linked service is not valid."))
                else:
                    QgsMapLayerRegistry.instance().addMapLayer(layer)
                    logging.info("Data added")

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
                QMessageBox.information(iface.mainWindow(),
                                        self.tr('Error'),
                                        self.tr("The PostGIS layer is not valid.")
                                        )

    def build_wms_url(self, raw_url):
        """Reformat the input WMS url so it fits QGIS criterias.

        Tests weither all the needed information is provided in the url, and
        then build the url in the syntax understood by QGIS.
        """
        input_url = raw_url.split("?")[0] + "?"
        list_parameters = raw_url.split("?")[1].split('&')
        valid = False
        style_defined = False
        srs_defined = False
        format_defined = False
        for i in list_parameters:
            ilow = i.lower()
            if "layers=" in ilow:
                valid = True
                name = i.split('=')[1]
                layers = i
            elif "layer=" in ilow:
                valid = True
                name = i.split('=')[1]
                layers = "layers=" + name
            elif "styles=" in ilow:
                style_defined = True
                style = i
            elif "crs=" in ilow:
                srs_defined = True
                srs = i
            elif "format=" in ilow:
                format_defined = True
                imgformat = i

        if valid is True:
            if input_url.lower().startswith('url='):
                output_url = input_url + "&" + layers
            else:
                output_url = "url=" + input_url + "&" + layers

            if style_defined is True:
                output_url += '&' + style
            else:
                output_url += '&styles='

            if format_defined is True:
                output_url += '&' + imgformat
            else:
                output_url += '&format=image/jpeg'

            if srs_defined is True:
                output_url += '&' + srs
            output = ["WMS", name, output_url]
            return output

        else:
            return 0

    def build_wfs_url(self, raw_url):
        """Reformat the input WFS url so it fits QGIS criterias.

        Tests weither all the needed information is provided in the url, and
        then build the url in the syntax understood by QGIS.
        """
        input_url = raw_url.split("?")[0] + "?"
        list_parameters = raw_url.split("?")[1].split('&')
        valid = False
        srs_defined = False
        for i in list_parameters:
            ilow = i.lower()
            if "typename=" in ilow:
                valid = True
                name = i.split('=')[1]
                typename = i
            elif "layers=" in ilow or "layer=" in ilow:
                valid = True
                name = i.split('=')[1]
                typename = "typename=" + name
            elif "srsname=" in ilow:
                srs_defined = True
                srs = i

        if valid is True:
            output_url = input_url + typename

            if srs_defined is True:
                output_url += '&' + srs

            output_url += '&service=WFS&version=1.0.0&request=GetFeature'

            output = ["WFS", name, output_url]
            return output

        else:
            return 0

    def get_tags(self, answer):
        """Return a tag dictionnary from the API answer.

        This parse the tags contained in API_answer[tags] and class them so
        they are more easy to handle in other function such as update_fields()
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
        # loops that sort each tag in the corresponding dict, keeping the same
        # "key : value" structure.
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
                    actions[tag] = u'Visualisable'
                elif tag.startswith('action:download'):
                    actions[tag] = u'Téléchargeable'
                elif tag.startswith('action:other'):
                    actions[tag] = u'Autre action'
                # Test : to be removed eventually
                else:
                    actions[tag] = u'fonction get_tag à revoir'
                    self.dockwidget.txt_input.setText(tag)
            # resources type
            elif tag.startswith('type'):
                if tag.startswith('type:vector'):
                    resources_types[tag] = u'Données vecteur'
                elif tag.startswith('type:raster'):
                    resources_types[tag] = u'Données raster'
                elif tag.startswith('type:resource'):
                    resources_types[tag] = u'Ressource'
                elif tag.startswith('type:service'):
                    resources_types[tag] = u'Service géographique'
                # Test : to be removed eventually
                else:
                    resources_types[tag] = u'fonction get_tag à revoir'
                    # self.dockwidget.txt_input.setText(tag)

        # Creating the final object the function will return : a dictionary of
        # dictionaries
        new_tags = {}
        new_tags['type'] = resources_types
        new_tags['owner'] = owners
        new_tags['keywords'] = keywords
        new_tags['themeinspire'] = themeinspire
        new_tags['formats'] = formats
        new_tags['srs'] = srs
        new_tags['actions'] = actions

        return new_tags

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
        operation_param = self.dockwidget.cbb_operation.itemData(
            self.dockwidget.cbb_operation.currentIndex())
        favorite_param = self.dockwidget.cbb_saved.itemData(
            self.dockwidget.cbb_saved.currentIndex())
        # Getting the text in the research line
        text = self.dockwidget.txt_input.text()
        # Saving the keywords that are selected : if a keyword state is
        # selected, he is added to the list
        key_params = []
        for i in xrange(self.dockwidget.cbb_keywords.count()):
            if self.dockwidget.cbb_keywords.itemData(i, 10) == 2:
                key_params.append(self.dockwidget.cbb_keywords.itemData(i, 32))

        # Saving the checked checkboxes (useful for the research saving)
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
            geofilter_param = True
        else:
            geofilter_param = False

        # Saving the checked radio button (useful for the research saving)
        if self.dockwidget.rdb_raster.isChecked():
            datatype = "raster"
        elif self.dockwidget.rdb_resource.isChecked():
            datatype = "resource"
        elif self.dockwidget.rdb_vector.isChecked():
            datatype = "vector"
        elif self.dockwidget.rdb_service.isChecked():
            datatype = "service"
        else:
            datatype = False

        params = {}
        params['owner'] = owner_param
        params['inspire'] = inspire_param
        params['format'] = format_param
        params['srs'] = srs_param
        params['favorite'] = favorite_param
        params['keys'] = key_params
        params['operation'] = operation_param
        params['view'] = view_param
        params['download'] = download_param
        params['other'] = other_param
        params['geofilter'] = geofilter_param
        params['text'] = text
        params['datatype'] = datatype
        if geofilter_param:
            e = iface.mapCanvas().extent()
            extent = [e.xMinimum(), e.yMinimum(), e.xMaximum(), e.yMaximum()]
            params['extent'] = extent
            epsg = int(iface.mapCanvas().mapRenderer(
            ).destinationCrs().authid().split(':')[1])
            params['epsg'] = epsg
        return params

    def search(self):
        """Build the request url to be sent to Isogeo API.

        This builds the url, retrieving the parameters from the widgets. When
        the final url is built, it calls send_request_to_isogeo_API
        """
        logging.info("Search function called. Building the url that is to be sent to the API")
        # Disabling all user inputs during the research function is running
        self.switch_widgets_on_and_off('off')

        # Setting some variables
        self.page_index = 1
        self.currentUrl = 'https://v1.api.isogeo.com/resources/search?'
        # Getting the parameters chosen by the user from the combobox
        if self.dockwidget.cbb_owner.currentIndex() != 0:
            owner = self.dockwidget.cbb_owner.itemData(
                self.dockwidget.cbb_owner.currentIndex())
        else:
            owner = False
        if self.dockwidget.cbb_inspire.currentIndex() != 0:
            inspire = self.dockwidget.cbb_inspire.itemData(
                self.dockwidget.cbb_inspire.currentIndex())
        else:
            inspire = False
        if self.dockwidget.cbb_format.currentIndex() != 0:
            formats = self.dockwidget.cbb_format.itemData(
                self.dockwidget.cbb_format.currentIndex())
        else:
            formats = False
        if self.dockwidget.cbb_srs.currentIndex() != 0:
            sys_coord = self.dockwidget.cbb_srs.itemData(
                self.dockwidget.cbb_srs.currentIndex())
        else:
            sys_coord = False
        # Getting the text entered in the text field
        filters = ""
        if self.dockwidget.txt_input.text():
            filters += self.dockwidget.txt_input.text() + " "

        # Adding the content of the comboboxes to the request
        if owner:
            filters += owner + " "
        if inspire:
            filters += inspire + " "
        if formats:
            filters += formats + " "
        if sys_coord:
            filters += sys_coord + " "
        # Actions in checkboxes
        if self.dockwidget.checkBox.isChecked():
            filters += "action:view "
        if self.dockwidget.checkBox_2.isChecked():
            filters += "action:download "
        if self.dockwidget.checkBox_3.isChecked():
            filters += "action:other "
        # Data type in radio buttons
        if self.dockwidget.rdb_raster.isChecked():
            filters += "type:raster-dataset "
        elif self.dockwidget.rdb_vector.isChecked():
            filters += "type:vector-dataset "
        elif self.dockwidget.rdb_resource.isChecked():
            filters += "type:resource "
        elif self.dockwidget.rdb_service.isChecked():
            filters += "type:service "
        # Adding the keywords that are checked (whose data[10] == 2)
        for i in xrange(self.dockwidget.cbb_keywords.count()):
            if self.dockwidget.cbb_keywords.itemData(i, 10) == 2:
                filters += self.dockwidget.cbb_keywords.itemData(i, 32) + " "

        # If the geographical filter is activated, build a spatial filter
        if self.dockwidget.checkBox_4.isChecked():
            if self.get_canvas_coordinates():
                filters = filters[:-1]
                filters += "&box=" + self.get_canvas_coordinates() + "&rel=" +\
                    self.dockwidget.cbb_operation.itemData(self.dockwidget.
                                                       operation.currentIndex()
                                                       ) + " "
            else:
                QMessageBox.information(iface.mainWindow(
                ), "Erreur :",
                    u"Le système de coordonnée de votre canevas ne "
                    u"semble\npas défini avec un code EPSG.\nIl ne peut donc "
                    u"pas être interprété par QGIS.\nMerci de rapporter ce "
                    u"problème sur le bug tracker.")

        filters = "q=" + filters[:-1]
        # self.dockwidget.txt_input.setText(encoded_filters)
        if filters != "q=":
            self.currentUrl += filters
        if self.showResult is True:
            self.currentUrl += "&_limit=15&_include=links"
        else:
            self.currentUrl += "&_limit=0"
        # self.dockwidget.dump.setText(self.currentUrl)
        self.send_request_to_Isogeo_API(self.token)

    def next_page(self):
        """Add the _offset parameter to the current url to display next page.

        Close to the search() function (lot of code in common) but
        triggered on the click on the change page button.
        """
        logging.info("next_page function called. Building the url that is to be sent to the API")
        # Testing if the user is asking for a unexisting page (ex : page 15 out
        # of 14)
        if self.page_index >= self.calcul_nb_page(self.results_count):
            return False
        else:
            self.showResult = True
            self.switch_widgets_on_and_off('off')
            # Building up the request
            self.page_index += 1
            self.currentUrl = 'https://v1.api.isogeo.com/resources/search?'
            # Getting the parameters chosen by the user from the combobox
            if self.dockwidget.cbb_owner.currentIndex() != 0:
                owner = self.dockwidget.cbb_owner.itemData(
                    self.dockwidget.cbb_owner.currentIndex())
            else:
                owner = False
            if self.dockwidget.cbb_inspire.currentIndex() != 0:
                inspire = self.dockwidget.cbb_inspire.itemData(
                    self.dockwidget.cbb_inspire.currentIndex())
            else:
                inspire = False
            if self.dockwidget.cbb_format.currentIndex() != 0:
                formats = self.dockwidget.cbb_format.itemData(
                    self.dockwidget.cbb_format.currentIndex())
            else:
                formats = False
            if self.dockwidget.cbb_srs.currentIndex() != 0:
                sys_coord = self.dockwidget.cbb_srs.itemData(
                    self.dockwidget.cbb_srs.currentIndex())
            else:
                sys_coord = False
            # Getting the text entered in the text field
            filters = ""
            if self.dockwidget.txt_input.text():
                filters += self.dockwidget.txt_input.text() + " "

            # Adding the content of the comboboxes to the request
            if owner:
                filters += owner + " "
            if inspire:
                filters += inspire + " "
            if formats:
                filters += formats + " "
            if sys_coord:
                filters += sys_coord + " "
            # Actions in checkboxes
            if self.dockwidget.checkBox.isChecked():
                filters += "action:view "
            if self.dockwidget.checkBox_2.isChecked():
                filters += "action:download "
            if self.dockwidget.checkBox_3.isChecked():
                filters += "action:other "
            # Data type in radio buttons
            if self.dockwidget.rdb_raster.isChecked():
                filters += "type:raster-dataset "
            elif self.dockwidget.rdb_vector.isChecked():
                filters += "type:vector-dataset "
            elif self.dockwidget.rdb_resource.isChecked():
                filters += "type:resource "
            elif self.dockwidget.rdb_service.isChecked():
                filters += "type:service "
            # Adding the keywords that are checked (whose data[10] == 2)
            for i in xrange(self.dockwidget.cbb_keywords.count()):
                if self.dockwidget.cbb_keywords.itemData(i, 10) == 2:
                    filters += self.dockwidget.cbb_keywords.itemData(i, 32) + " "

            # If the geographical filter is activated, build a spatial filter
            if self.dockwidget.checkBox_4.isChecked():
                if self.get_canvas_coordinates():
                    filters = filters[:-1]
                    filters += "&box=" + self.get_canvas_coordinates() +\
                        "&rel=" + \
                        self.dockwidget.cbb_operation.itemData(
                            self.dockwidget.cbb_operation.currentIndex()) + " "
                else:
                    QMessageBox.information(iface.mainWindow(
                    ), self.tr("Error"),
                       self.tr("Your canvas coordinate system is not defined with a EPSG code."))

            filters = "q=" + filters[:-1]
            # self.dockwidget.txt_input.setText(encoded_filters)
            if filters != "q=":
                self.currentUrl += filters
                self.currentUrl += "&_offset=" + \
                    str((15 * (self.page_index - 1))) + \
                    "&_limit=15&_include=links"
            else:
                self.currentUrl += "_offset=" + \
                    str((15 * (self.page_index - 1))) + \
                    "&_limit=15&_include=links"
            # self.dockwidget.dump.setText(self.currentUrl)
            self.send_request_to_Isogeo_API(self.token)

    def previous_page(self):
        """Add the _offset parameter to the url to display previous page.

        Close to the search() function (lot of code in common) but
        triggered on the click on the change page button.
        """
        logging.info("previous_page function called. Building the url that is to be sent to the API")
        # testing if the user is asking for something impossible : page 0
        if self.page_index < 2:
            return False
        else:
            self.showResult = True
            self.switch_widgets_on_and_off('off')
            # Building up the request
            self.page_index -= 1
            self.currentUrl = 'https://v1.api.isogeo.com/resources/search?'
            # Getting the parameters chosen by the user from the combobox
            if self.dockwidget.cbb_owner.currentIndex() != 0:
                owner = self.dockwidget.cbb_owner.itemData(
                    self.dockwidget.cbb_owner.currentIndex())
            else:
                owner = False
            if self.dockwidget.cbb_inspire.currentIndex() != 0:
                inspire = self.dockwidget.cbb_inspire.itemData(
                    self.dockwidget.cbb_inspire.currentIndex())
            else:
                inspire = False
            if self.dockwidget.cbb_format.currentIndex() != 0:
                formats = self.dockwidget.cbb_format.itemData(
                    self.dockwidget.cbb_format.currentIndex())
            else:
                formats = False
            if self.dockwidget.cbb_srs.currentIndex() != 0:
                sys_coord = self.dockwidget.cbb_srs.itemData(
                    self.dockwidget.cbb_srs.currentIndex())
            else:
                sys_coord = False
            # Getting the text entered in the text field
            filters = ""
            if self.dockwidget.txt_input.text():
                filters += self.dockwidget.txt_input.text() + " "

            # Adding the content of the comboboxes to the request
            if owner:
                filters += owner + " "
            if inspire:
                filters += inspire + " "
            if formats:
                filters += formats + " "
            if sys_coord:
                filters += sys_coord + " "
            # Actions in checkboxes
            if self.dockwidget.checkBox.isChecked():
                filters += "action:view "
            if self.dockwidget.checkBox_2.isChecked():
                filters += "action:download "
            if self.dockwidget.checkBox_3.isChecked():
                filters += "action:other "
            # Data type in radio buttons
            if self.dockwidget.rdb_raster.isChecked():
                filters += "type:raster-dataset "
            elif self.dockwidget.rdb_vector.isChecked():
                filters += "type:vector-dataset "
            elif self.dockwidget.rdb_resource.isChecked():
                filters += "type:resource "
            elif self.dockwidget.rdb_service.isChecked():
                filters += "type:service "
            # Adding the keywords that are checked (whose data[10] == 2)
            for i in xrange(self.dockwidget.cbb_keywords.count()):
                if self.dockwidget.cbb_keywords.itemData(i, 10) == 2:
                    filters += self.dockwidget.cbb_keywords.itemData(i, 32) + " "

            # If the geographical filter is activated, build a spatial filter
            if self.dockwidget.checkBox_4.isChecked():
                if self.get_canvas_coordinates():
                    filters = filters[:-1]
                    filters += "&box=" + self.get_canvas_coordinates() + \
                        "&rel=" + \
                        self.dockwidget.cbb_operation.itemData(
                            self.dockwidget.cbb_operation.currentIndex()) + " "
                else:
                    QMessageBox.information(iface.mainWindow(
                    ), self.tr("Error"),
                       self.tr("Your canvas coordinate system is not defined with a EPSG code."))
            filters = "q=" + filters[:-1]

            if filters != "q=":
                if self.page_index == 1:
                    self.currentUrl += filters + "&_limit=15&_include=links"
                else:
                    self.currentUrl += filters + "&_offset=" + \
                        str((15 * (self.page_index - 1))) + \
                        "&_limit=15&_include=links"
            else:
                if self.page_index == 1:
                    self.currentUrl += "_limit=15&_include=links"
                else:
                    self.currentUrl += "&_offset=" + \
                        str((15 * (self.page_index - 1))) + \
                        "&_limit=15&_include=links"

            # self.dockwidget.dump.setText(self.currentUrl)
            self.send_request_to_Isogeo_API(self.token)

    def write_research_params(self, research_name):
        """Write a new element in the json file when a research is saved."""
        # Open the saved_research file as a dict. Each key is a research name,
        # each value is a dict containing the parameters for this research name
        path = self.get_plugin_path() + '/saved_researches.json'
        with open(path) as data_file:
            saved_researches = json.load(data_file)
        # If the name already exists, ask for a new one. (TO DO)
        if research_name in saved_researches.keys() and research_name != '_default':
            pass
        else:
            # Write the current parameters in a dict, and store it in the saved
            # research dict
            params = self.save_params()
            params['url'] = self.currentUrl
            for i in xrange(len(params['keys'])):
                params['keyword_{0}'.format(i)] = params['keys'][i]
            params.pop('keys', None)
            saved_researches[research_name] = params
            with open(path, 'w') as outfile:
                json.dump(saved_researches, outfile)
            logging.info("Saved reseearch written. {0}".format(params))

    def set_widget_status(self):
        """Set a few variable and send the request to Isogeo API."""
        logging.info("Set_widget_status function called. User is executing a saved research.")
        self.switch_widgets_on_and_off('off')
        selected_research = self.dockwidget.cbb_saved.currentText()
        path = self.get_plugin_path() + '/saved_researches.json'
        with open(path) as data_file:
            saved_researches = json.load(data_file)
        if selected_research == "":
            self.savedResearch = '_default'
            research_params = saved_researches['_default']
        else:
            self.savedResearch = selected_research
            research_params = saved_researches[selected_research]
        self.currentUrl = research_params['url']
        if research_params['geofilter']:
            epsg = int(iface.mapCanvas().mapRenderer(
            ).destinationCrs().authid().split(':')[1])
            if epsg == research_params['epsg']:
                canvas = iface.mapCanvas()
                e = research_params['extent']
                rect = QgsRectangle(e[0], e[1], e[2], e[3])
                canvas.setExtent(rect)
                canvas.refresh()
            else:
                canvas = iface.mapCanvas()
                canvas.mapRenderer().setProjectionsEnabled(True)
                canvas.mapRenderer().setDestinationCrs(
                    QgsCoordinateReferenceSystem(
                        research_params['epsg'],
                        QgsCoordinateReferenceSystem.EpsgCrsId))
                e = research_params['extent']
                rect = QgsRectangle(e[0], e[1], e[2], e[3])
                canvas.setExtent(rect)
                canvas.refresh()
        self.send_request_to_Isogeo_API(self.token)

    def save_research(self):
        """Call the write_research() function and refresh the combobox."""
        research_name = self.ask_name_popup.name.text()
        self.write_research_params(research_name)
        path = self.get_plugin_path() + '/saved_researches.json'
        with open(path) as data_file:
            saved_researches = json.load(data_file)
        research_list = saved_researches.keys()
        research_list.pop(research_list.index('_default'))
        self.dockwidget.cbb_saved.clear()
        for i in research_list:
            self.dockwidget.cbb_saved.addItem(i, i)

    def calcul_nb_page(self, nb_fiches):
        """Calculate the number of pages given a number of results."""
        if nb_fiches <= 15:
            nb_page = 1
        else:
            if (nb_fiches % 15) == 0:
                nb_page = (nb_fiches / 15)
            else:
                nb_page = (nb_fiches / 15) + 1
        return nb_page

    def handle_date(self, input_date):
        """Create a date object with the string given as a date by the API."""
        date = input_date.split("T")[0]
        year = int(date.split('-')[0])
        month = int(date.split('-')[1])
        day = int(date.split('-')[2])
        new_date = datetime.date(year, month, day)
        return new_date.strftime("%d/%m/%Y")
        return new_date

    def get_canvas_coordinates(self):
        """Get the canvas coordinates in the right format and SRS (WGS84)."""
        e = iface.mapCanvas().extent()
        current_epsg = int(iface.mapCanvas().mapRenderer(
        ).destinationCrs().authid().split(':')[1])
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
            return False

    def open_bugtracker(self):
        """Open the bugtracker on the user's default browser."""
        webbrowser.open(
            'https://github.com/isogeo/isogeo-plugin-qgis/issues',
            new=0,
            autoraise=True)

    def reinitialize_research(self):
        """Clear all widget, putting them all back to their default value.

        Clear all widget and send a request to the API (which ends up updating
        the fields : send_request() calls handle_reply(), which calls
        update_fields())
        """
        logging.info("Reinitialize_research function called.")
        self.hardReset = True
        self.dockwidget.checkBox.setCheckState(Qt.Unchecked)
        self.dockwidget.checkBox_2.setCheckState(Qt.Unchecked)
        self.dockwidget.checkBox_3.setCheckState(Qt.Unchecked)
        self.dockwidget.checkBox_4.setCheckState(Qt.Unchecked)
        self.dockwidget.rdb_raster.setChecked(False)
        self.dockwidget.rdb_resource.setChecked(False)
        self.dockwidget.rdb_vector.setChecked(False)
        self.dockwidget.rdb_service.setChecked(False)
        self.dockwidget.rdb_alltypes.setChecked(True)
        self.dockwidget.txt_input.clear()
        self.dockwidget.cbb_keywords.clear()
        self.dockwidget.cbb_operation.clear()
        self.dockwidget.cbb_owner.clear()
        self.dockwidget.cbb_inspire.clear()
        self.dockwidget.cbb_format.clear()
        self.dockwidget.cbb_srs.clear()
        self.search()

    def format_path(self, string):
        """Reformat windows path for them to be understood by QGIS."""
        new_string = ""
        for character in string:
            if character == '\\':
                new_string += "/"
            else:
                new_string += character
        return new_string

    def search_with_content(self):
        """Launch a search request that will end up in showing the results."""
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
            self.dockwidget.grp_filters.setEnabled(True)
            self.dockwidget.grp_geofilter.setEnabled(True)
            self.dockwidget.widget.setEnabled(True)
            self.dockwidget.btn_reinit.setEnabled(True)
            self.dockwidget.btn_show.setEnabled(True)
            self.dockwidget.btn_show.setEnabled(True)

        else:
            self.dockwidget.txt_input.setReadOnly(True)
            self.dockwidget.grp_filters.setEnabled(False)
            self.dockwidget.grp_geofilter.setEnabled(False)
            self.dockwidget.widget.setEnabled(False)
            self.dockwidget.btn_next.setEnabled(False)
            self.dockwidget.btn_previous.setEnabled(False)
            self.dockwidget.btn_reinit.setEnabled(False)
            self.dockwidget.btn_show.setEnabled(False)
            self.dockwidget.btn_show.setEnabled(False)

    def show_popup(self):
        """Open the pop up window that asks a name to save the research."""
        self.ask_name_popup.show()

    def send_details_request(self, md_id):
        """Send a request for aditionnal info about one data."""
        logging.info("Full metatada sheet asked. Building the url.")
        self.currentUrl = 'https://v1.api.isogeo.com/resources/' + str(md_id) + '?_include=contacts,limitations,conditions,events,feature-attributes'
        self.showDetails = True
        self.send_request_to_Isogeo_API(self.token)

    def show_complete_md(self, content):
        """Open the pop up window that shows the metadata sheet details."""
        logging.info("Displaying the whole metadata sheet.")
        tags = self.get_tags(content)
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
                self.handle_date(creation_date))
        else:
            self.IsogeoMdDetails.val_data_crea.setText('NR')
        # Set the data last modification date
        modif_date = content.get('_modified')
        if modif_date is not None:
            self.IsogeoMdDetails.val_data_updt.setText(self.handle_date(
                modif_date))
        else:
            self.IsogeoMdDetails.val_data_updt.setText('NR')
        # Set the date from which the data is valid
        valid_from = content.get('validFrom')
        if valid_from is not None:
            self.IsogeoMdDetails.val_valid_start.setText(self.handle_date(
                valid_from))
        else:
            self.IsogeoMdDetails.val_valid_start.setText('NR')
        # Set the date from which the data stops being valid
        valid_to = content.get('validTo')
        if valid_to is not None:
            self.IsogeoMdDetails.val_valid_end.setText(self.handle_date(
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
                event = self.handle_date(i['date']) + " : " + i['kind']
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
        # Initiating values (TO DO : Move to init section)

        """ --- CONNECTING FUNCTIONS --- """
        # Write in the config file when the user accept the authentification
        # window
        self.auth_prompt_form.accepted.connect(self.write_ids_and_test)
        # Connecting the comboboxes to the search function
        self.dockwidget.cbb_owner.activated.connect(self.search)
        self.dockwidget.cbb_inspire.activated.connect(self.search)
        self.dockwidget.cbb_format.activated.connect(self.search)
        self.dockwidget.cbb_srs.activated.connect(self.search)
        self.dockwidget.cbb_operation.activated.connect(self.search)
        # Connecting the text input to the search function
        self.dockwidget.txt_input.editingFinished.connect(self.search)
        # Connecting the checkboxes to the search function
        self.dockwidget.checkBox.clicked.connect(self.search)
        self.dockwidget.checkBox_2.clicked.connect(self.search)
        self.dockwidget.checkBox_3.clicked.connect(self.search)
        self.dockwidget.checkBox_4.clicked.connect(self.search)
        # Connecting the radio buttons
        self.dockwidget.rdb_raster.clicked.connect(self.search)
        self.dockwidget.rdb_resource.clicked.connect(self.search)
        self.dockwidget.rdb_vector.clicked.connect(self.search)
        self.dockwidget.rdb_service.clicked.connect(self.search)
        self.dockwidget.rdb_alltypes.clicked.connect(self.search)
        # Connecting the previous and next page buttons to their functions
        self.dockwidget.btn_next.pressed.connect(self.next_page)
        self.dockwidget.btn_previous.pressed.connect(self.previous_page)
        # Connecting the bug tracker button to its function
        self.dockwidget.btn_report.pressed.connect(self.open_bugtracker)
        # Connecting the "reinitialize research button" to a research without
        # filters
        self.dockwidget.btn_reinit.pressed.connect(self.reinitialize_research)
        # Change user
        self.dockwidget.btn_change_user.pressed.connect(
            self.auth_prompt_form.show)
        # show results
        self.dockwidget.btn_show.pressed.connect(self.search_with_content)

        # Button 'save favorite' connected to the opening of the pop up that
        # asks for a name
        self.dockwidget.btn_save.pressed.connect(self.show_popup)
        # Connect the accepted signal of the popup to the function that write
        # the research name and parameter to the file, and update the combobox
        self.ask_name_popup.accepted.connect(self.save_research)
        # Connect the activation of the "saved research" combobox with the
        # set_widget_status function
        self.dockwidget.cbb_saved.activated.connect(
            self.set_widget_status)
        #G default
        self.dockwidget.btn_default.pressed.connect(partial(self.write_research_params, research_name='_default'))

        """ --- Actions when the plugin is launched --- """
        # self.test_config_file_existence()
        self.user_authentication()
        self.test_proxy_configuration()
        # self.dockwidget.cbb_saved.setEnabled(False)
        # self.dockwidget.btn_save.setEnabled(False)
        self.dockwidget.groupBox.setEnabled(False)
        # self.dockwidget.groupBox_2.setEnabled(False)
        self.dockwidget.groupBox_3.setEnabled(False)
        self.dockwidget.groupBox_4.setEnabled(False)
        self.dockwidget.tab_3.setEnabled(False)
        # self.dockwidget.tabWidget.currentChanged.connect(self.show_popup)
