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
        email                : projets+qgis@isogeo.fr
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
    QStandardItemModel, QStandardItem, QComboBox

# Initialize Qt resources from file resources.py
import resources

# Import the code for the DockWidget
from isogeo_dockwidget import IsogeoDockWidget

# Import du code des autres fenêtres
from authentification import authentification

import os.path

# Ajoutés par moi
from qgis.utils import iface
from qgis.core import QgsNetworkAccessManager, QgsPoint, \
    QgsCoordinateReferenceSystem, QgsCoordinateTransform, QgsVectorLayer, \
    QgsMapLayerRegistry, QgsRasterLayer, QgsDataSourceURI
from PyQt4.QtNetwork import QNetworkRequest
import ConfigParser
import json
import base64
import urllib
import logging
from logging.handlers import RotatingFileHandler
import datetime
import webbrowser
from functools import partial
import db_manager.db_plugins.postgis.connector as con


class Isogeo:
    """QGIS Plugin Implementation."""

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
            'Isogeo_{}.qm'.format(locale))

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

        self.authentification_window = authentification()

        self.loopCount = 0

        self.hardReset = True

        self.showResult = True

        self.PostGISdict = {}

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
        """Cleanup necessary items here when plugin dockwidget is closed"""
        # print "** CLOSING Isogeo"

        # disconnects
        self.dockwidget.closingPlugin.disconnect(self.onClosePlugin)

        # remove this statement if dockwidget is to remain
        # for reuse if plugin is reopened
        # Commented next statement since it causes QGIS crashe
        # when closing the docked window:
        # self.dockwidget = None

        self.pluginIsActive = False

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

    def test_config_file_existence(self):
        """Check if the file already exists and if not, create it."""
        self.config = ConfigParser.ConfigParser()
        self.config_path = self.get_plugin_path() + "/config.ini"
        if os.path.isfile(self.config_path):
            pass
        else:
            QMessageBox.information(iface.mainWindow(
            ), 'Alerte', u"Vous avez détruit ou renommé le fichier config.ini."
                u"\nCe n'était pas une très bonne idée.")
            config_file = open(self.config_path, 'w')
            self.config.write(config_file)
            # TO DO : CREER UN TEMPLATE
            config_file.close()

    def test_proxy_configuration(self):
        """Check the proxy configuration.

        if a proxy configuration is set up for the computer, and for QGIS.
        If none or both is set up, pass. But if there is a proxy config for the
        computer but not in QGIS, pops an alert message.
        """
        system_proxy_config = urllib.getproxies()
        if system_proxy_config == {}:
            pass
        else:
            s = QSettings()
            qgis_proxy = s.value("proxy/proxyEnabled", "")
            if str(qgis_proxy) == 'true':
                pass
            else:
                QMessageBox.information(iface.mainWindow(
                ), 'Alerte', u"Problème de proxy : \nVotre ordinateur utilise "
                    u"un proxy, mais vous n'avez pas saisi ses paramètres dans"
                    u" QGIS.\nMerci de renseigner les paramètres proxy dans le"
                    u" menu 'Préférences/Option/Réseau'.")

    def user_authentification(self):
        """Test the validity of the user id and secret.

        This is the first major function the plugin calls when executed. It
        retrieves the id and secret from the config file. If they are set to
        their default value, it asks for them.
        If not, it tries to send a request.
        """
        self.config.read(self.config_path)
        config_dict = {s: dict(self.config.items(s))
                       for s in self.config.sections()}
        self.user_id = config_dict['Isogeo_ids']['application_id']
        self.user_secret = config_dict['Isogeo_ids']['application_secret']
        if self.user_id != 'application_id':
            # Demande les identifiants dans une pop-up et écrit les.
            self.ask_for_token(self.user_id, self.user_secret)
        else:
            self.authentification_window.show()

    def write_ids_and_test(self):
        """Store the id &secret and launch the test function.

        Called when the authentification window is closed,
        it stores the values in the file, then call the
        user_authentification function to test them.
        """
        self.user_id = self.authentification_window.user_id_input.text()
        self.user_secret = self.authentification_window.\
            user_secret_input.text()
        config_file = open(self.config_path, 'w')
        self.config.set('Isogeo_ids', 'application_id', self.user_id)
        self.config.set('Isogeo_ids', 'application_secret', self.user_secret)
        self.config.write(config_file)
        config_file.close()

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

    def handle_token(self):
        """Handle the API answer when asked for a token.

        This handles the API answer. If it has sent an access token, it calls
        the initialization function. If not, it raises an error, and ask
        for new IDs
        """
        bytarray = self.token_reply.readAll()
        content = str(bytarray)
        parsed_content = json.loads(content)
        if 'access_token' in parsed_content:
            # TO DO : Appeler la fonction d'initialisation
            self.token = "Bearer " + parsed_content['access_token']
            self.search()
        # TO DO : Distinguer plusieurs cas d'erreur
        elif 'error' in parsed_content:
            QMessageBox.information(
                iface.mainWindow(), 'Erreur', parsed_content['error'])
            self.authentification_window.show()
        else:
            self.dockwidget.text_input.setText("Erreur inconnue.")

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
        bytarray = self.API_reply.readAll()
        content = str(bytarray)
        if self.API_reply.error() == 0 and content != "":
            self.loopCount = 0
            parsed_content = json.loads(content)
            self.update_fields(parsed_content)
        elif self.API_reply.error() == 204:
            self.loopCount = 0
            self.ask_for_token(self.user_id, self.user_secret)
        elif content == "":
            if self.loopCount < 3:
                self.loopCount += 1
                self.API_reply = 0
                self.token_reply = 0
                self.ask_for_token(self.user_id, self.user_secret)
            else:
                QMessageBox.information(iface.mainWindow(
                ), 'Erreur :', u"Le script tourne en rond."
                    u"\nVérifiez que vous avez partagé bien partagé \nun ou "
                    u"plusieurs catalogues avec le plugin.\nSi c'est bien le "
                    u"cas, merci de rapporter\nce problème sur le bug tracker")
        else:
            QMessageBox.information(iface.mainWindow(), 'Erreur :',
                                    u"Vous rencontrez une erreur non encore "
                                    u"gérée.\nCode : " + str(
                self.API_reply.error()) + "\nMerci de le reporter sur le bug "
                u"tracker.")

    def update_fields(self, result):
        """Update the fields content.

        This takes an API answer and update the fields accordingly. It also
        calls show_results in the end. This may change, so results would be
        shown only when a specific button is pressed.
        """
        tags = self.get_tags(result)
        # Getting the index of selected items in each combobox
        self.params = self.save_params()
        # Show how many results there are
        self.results_count = result['total']
        self.dockwidget.nbresultat.setText(
            str(self.results_count) + u" résultats")
        # Setting the number of rows in the result table

        self.nb_page = str(self.calcul_nb_page(self.results_count))
        self.dockwidget.paging.setText(
            "page " + str(self.page_index) + " sur " + self.nb_page)
        # clearing the previous fields
        self.dockwidget.resultats.clearContents()
        self.dockwidget.inspire.clear()
        self.dockwidget.owner.clear()
        self.dockwidget.format.clear()
        self.dockwidget.sys_coord.clear()
        self.dockwidget.operation.clear()
        # Initiating the "nothing selected" item in each combobox
        self.dockwidget.inspire.addItem(" - ")
        self.dockwidget.owner.addItem(" - ")
        self.dockwidget.format.addItem(" - ")
        self.dockwidget.sys_coord.addItem(" - ")
        dictOperation = {"Intersectent": "intersects",
                         "Sont contenues": "within", "Contiennent": "contains"}
        for operationKey in dictOperation.keys():
            self.dockwidget.operation.addItem(
                operationKey, dictOperation[operationKey])
        if self.hardReset == True:
            self.dockwidget.operation.setCurrentIndex(
                self.dockwidget.operation.findData("intersects"))
        else:
            self.dockwidget.operation.setCurrentIndex(
                self.dockwidget.operation.findData(self.params['operation']))
        # Creating combobox items, with their displayed text, and their value
        for key in tags['owner']:
            self.dockwidget.owner.addItem(tags['owner'][key], key)
        for key in tags['themeinspire']:
            self.dockwidget.inspire.addItem(tags['themeinspire'][key], key)
        for key in tags['formats']:
            self.dockwidget.format.addItem(tags['formats'][key], key)
        for key in tags['srs']:
            self.dockwidget.sys_coord.addItem(tags['srs'][key], key)

        # Putting all the comboboxes selected index to their previous
        # location. Necessary as all comboboxes items have been removed and
        # put back in place. We do not want each combobox to go back to their
        # default selected item
        if self.hardReset == False:
            self.dockwidget.owner.setCurrentIndex(
                self.dockwidget.owner.findData(self.params['owner']))
            self.dockwidget.inspire.setCurrentIndex(
                self.dockwidget.inspire.findData(self.params['inspire']))
            # Set the combobox current index to (get the index of the item
            # which data is (saved data))
            self.dockwidget.format.setCurrentIndex(
                self.dockwidget.format.findData(self.params['format']))
            self.dockwidget.sys_coord.setCurrentIndex(
                self.dockwidget.sys_coord.findData(self.params['srs']))

            """ Filling the keywords special combobox (whose items are checkable) """
            self.model = QStandardItemModel(5, 1)  # 5 rows, 1 col
            firstItem = QStandardItem(u"---- Mots clés ----")
            firstItem.setSelectable(False)
            self.model.setItem(0, 0, firstItem)
            i = 1
            for key in tags['keywords']:
                item = QStandardItem(tags['keywords'][key])
                item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
                item.setData(key, 32)
                # As all items have been destroyed and generated again, we
                # have to set the checkstate (checked/unchecked) according to
                # what the user had chosen
                if item.data(32) in self.params['keys']:
                    item.setData(Qt.Checked, Qt.CheckStateRole)
                else:
                    item.setData(Qt.Unchecked, Qt.CheckStateRole)
                self.model.setItem(i, 0, item)
                i += 1
            self.model.itemChanged.connect(self.search)
            self.dockwidget.keywords.setModel(self.model)
        else:
            self.model = QStandardItemModel(5, 1)  # 5 rows, 1 col
            firstItem = QStandardItem(u"---- Mots clés ----")
            firstItem.setSelectable(False)
            self.model.setItem(0, 0, firstItem)
            i = 1
            for key in tags['keywords']:
                item = QStandardItem(tags['keywords'][key])
                item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
                item.setData(key, 32)
                # As all items have been destroyed and generated again, we have
                # to set the checkstate (checked/unchecked) according to what
                # the user had chosen
                item.setData(Qt.Unchecked, Qt.CheckStateRole)
                self.model.setItem(i, 0, item)
                i += 1
            self.model.itemChanged.connect(self.search)
            self.dockwidget.keywords.setModel(self.model)

        # Trying to make th checkboxes and radio buttons unckeckable if needed
        # View
        if 'action:view' in tags['actions']:
            self.dockwidget.checkBox.setCheckable(True)
            self.dockwidget.checkBox.setStyleSheet("color: black")
        else:
            self.dockwidget.checkBox.setCheckable(False)
            self.dockwidget.checkBox.setStyleSheet("color: grey")
        # Download
        if 'action:download' in tags['actions']:
            self.dockwidget.checkBox_2.setCheckable(True)
            self.dockwidget.checkBox_2.setStyleSheet("color: black")
        else:
            self.dockwidget.checkBox_2.setCheckable(False)
            self.dockwidget.checkBox_2.setStyleSheet("color: grey")
        # Other action
        if 'action:other' in tags['actions']:
            self.dockwidget.checkBox_3.setCheckable(True)
            self.dockwidget.checkBox_3.setStyleSheet("color: black")
        else:
            self.dockwidget.checkBox_3.setCheckable(False)
            self.dockwidget.checkBox_3.setStyleSheet("color: grey")

        # Show result, if we want them to be shown (button 'show result', 'next
        # page' or 'previous page' pressed)
        if self.showResult == True:
            self.show_results(result)
        # Re enable all user input fields now the research function is
        # finished.
        self.switch_widgets_on_and_off('on')
        # hard reset
        self.hardReset = False
        self.showResult = False

    # This function put the metadata sheets contained in the answer in the
    # table.
    def show_results(self, result):
        if self.results_count >= 15:
            self.dockwidget.resultats.setRowCount(15)
        else:
            self.dockwidget.resultats.setRowCount(self.results_count)

        polygonList = ["CurvePolygon", "MultiPolygon",
                       "MultiSurface", "Polygon", "PolyhedralSurface"]
        pointList = ["Point", "MultiPoint"]
        lineList = ["CircularString", "CompoundCurve", "Curve",
                    "LineString", "MultiCurve", "MultiLineString"]
        multiList = ["Geometry", "GeometryCollection"]

        vectorFormatList = ['shp', 'dxf', 'dgn', 'filegdb', 'tab']
        rasterFormatList = ['esriasciigrid', 'geotiff',
                            'intergraphgdb', 'jpeg', 'png', 'xyz']

        # Récupère tous les noms de bases de données dont la connexion est
        # enregistrée dans QGIS
        qs = QSettings()
        if self.PostGISdict == {}:
            for k in sorted(qs.allKeys()):
                if k.startswith("PostgreSQL/connections/") and k.endswith("/database"):
                    if len(k.split("/")) == 4:
                        connexionName = k.split("/")[2]
                        print connexionName
                        if qs.value('PostgreSQL/connections/' + connexionName + '/savePassword') == 'true' and qs.value('PostgreSQL/connections/' + connexionName + '/saveUsername') == 'true':
                            dictionary = {'name': qs.value('PostgreSQL/connections/' + connexionName + '/database'), 'host': qs.value('PostgreSQL/connections/' + connexionName + '/host'), 'port': qs.value(
                                'PostgreSQL/connections/' + connexionName + '/port'), 'username': qs.value('PostgreSQL/connections/' + connexionName + '/username'), 'password': qs.value('PostgreSQL/connections/' + connexionName + '/password')}
                            self.PostGISdict[
                                qs.value('PostgreSQL/connections/' + connexionName + '/database')] = dictionary

        count = 0
        for i in result['results']:
            self.dockwidget.resultats.setItem(
                count, 0, QTableWidgetItem(i['title']))
            try:
                self.dockwidget.resultats.item(
                    count, 0).setToolTip(i['abstract'])
            except:
                pass
            self.dockwidget.resultats.setItem(
                count, 1, QTableWidgetItem(self.handle_date(i['_modified'])))
            try:
                geometry = i['geometry']
                if geometry in pointList:
                    self.dockwidget.resultats.setItem(
                        count, 2, QTableWidgetItem(u'Ponctuel'))
                elif geometry in polygonList:
                    self.dockwidget.resultats.setItem(
                        count, 2, QTableWidgetItem(u'Surfacique'))
                elif geometry in lineList:
                    self.dockwidget.resultats.setItem(
                        count, 2, QTableWidgetItem(u'Linéaire'))
                elif geometry in multiList:
                    self.dockwidget.resultats.setItem(
                        count, 2, QTableWidgetItem(u'Géométrie composée'))
                elif geometry == "TIN":
                    self.dockwidget.resultats.setItem(
                        count, 2, QTableWidgetItem(u'TIN'))
                else:
                    self.dockwidget.resultats.setItem(
                        count, 2, QTableWidgetItem(u'Géométrie inconnue'))
            except:
                self.dockwidget.resultats.setItem(
                    count, 2, QTableWidgetItem(u"Pas de géométrie"))

            combo = QComboBox()
            linkDict = {}

            if 'format' in i.keys():
                if i['format'] in vectorFormatList and 'path' in i:
                    path = self.format_path(i['path'])
                    try:
                        testPath = open(path)
                        params = ["vector", path]
                        linkDict[u"Donnée fichier"] = params
                        #combo.addItem(u"Donnée fichier", params)

                    except IOError:
                        pass

                elif i['format'] in rasterFormatList and 'path' in i:
                    path = self.format_path(i['path'])
                    try:
                        testPath = open(path)
                        params = ["raster", path]
                        linkDict[u"Donnée fichier"] = params
                        #combo.addItem(u"Donnée fichier", params)
                    except IOError:
                        pass

                elif i['format'] == 'postgis':
                    # Récupère le nom de la base de données
                    baseName = i['path']

                    if baseName in self.PostGISdict.keys():
                        params = {}
                        params['baseName'] = baseName
                        params['schema'] = i['name'].split(".")[0]
                        params['table'] = i['name'].split(".")[1]
                        linkDict[u"Table PostGIS"] = params
                        #combo.addItem(u"Table PostGIS", params)
                        """
                        button = QPushButton("Ajouter")
                        button.pressed.connect(partial(self.addPostGisLayer, host = self.PostGISdict[baseName]['host'], port = self.PostGISdict[baseName]['port'], basename = baseName, user = self.PostGISdict[baseName]['username'], password = self.PostGISdict[baseName]['password'], schema = schema, table = table))
                        self.dockwidget.resultats.setCellWidget(count,3, button)"""

            for link in i['links']:
                if link['kind'] == 'wms':
                    name_url = self.build_wms_url(link['url'])
                    if name_url != 0:
                        linkDict[u"WMS : " + name_url[1]] = name_url
                        #combo.addItem(u"WMS : " + name_url[1], name_url)
                elif link['kind'] == 'wfs':
                    name_url = self.build_wfs_url(link['url'])
                    if name_url != 0:
                        linkDict[u"WFS : " + name_url[1]] = name_url
                        #combo.addItem(u"WFS" + name_url[1], name_url)

            for key in linkDict.keys():
                combo.addItem(key, linkDict[key])

            combo.activated.connect(partial(self.add_layer, layerIndex=count))
            self.dockwidget.resultats.setCellWidget(count, 3, combo)

            count += 1

    # This adds a layer
    def add_layer(self, layerIndex):
        layerInfo = self.dockwidget.resultats.cellWidget(layerIndex, 3).itemData(
            self.dockwidget.resultats.cellWidget(layerIndex, 3).currentIndex())
        if type(layerInfo) == list:
            if layerInfo[0] == "vector":
                path = layerInfo[1]
                name = os.path.basename(path).split(".")[0]
                layer = QgsVectorLayer(path, name, 'ogr')
                if layer.isValid():
                    QgsMapLayerRegistry.instance().addMapLayer(layer)
                else:
                    QMessageBox.information(
                        iface.mainWindow(), 'Erreur', "La couche n'est pas valide")

            elif layerInfo[0] == "raster":
                path = layerInfo[1]
                name = os.path.basename(path).split(".")[0]
                layer = QgsRasterLayer(path, name)
                if layer.isValid():
                    QgsMapLayerRegistry.instance().addMapLayer(layer)
                else:
                    QMessageBox.information(
                        iface.mainWindow(), 'Erreur', "La couche n'est pas valide")

            elif layerInfo[0] == 'WMS':
                url = layerInfo[2]
                name = layerInfo[1]
                layer = QgsRasterLayer(url, name, 'wms')
                if not layer.isValid():
                    QMessageBox.information(
                        iface.mainWindow(), 'Erreur', u"Le service renseigné n'est pas valide")
                else:
                    QgsMapLayerRegistry.instance().addMapLayer(layer)

            elif layerInfo[0] == 'WFS':
                url = layerInfo[2]
                name = layerInfo[1]
                layer = QgsVectorLayer(url, name, 'WFS')
                if not layer.isValid():
                    QMessageBox.information(
                        iface.mainWindow(), 'Erreur', u"Le service renseigné n'est pas valide")
                else:
                    QgsMapLayerRegistry.instance().addMapLayer(layer)

        elif type(layerInfo) == dict:
            # Give aliases to the data passed as arguement
            baseName = layerInfo['baseName']
            schema = layerInfo['schema']
            table = layerInfo['table']
            # Retrieve the database information stored in the PostGISdict
            uri = QgsDataSourceURI()
            host = self.PostGISdict[baseName]['host']
            port = self.PostGISdict[baseName]['port']
            user = self.PostGISdict[baseName]['username']
            password = self.PostGISdict[baseName]['password']
            # set host name, port, database name, username and password
            uri.setConnection(host, port, baseName, user, password)
            # Get the geometry column name from the database connexion & table
            # name.
            c = con.PostGisDBConnector(uri)
            dico = c.getTables()
            for i in dico:
                if i[0 == 1] and i[1] == table:
                    geometryColumn = i[8]
            # set database schema, table name, geometry column
            uri.setDataSource(schema, table, geometryColumn)
            # Adding the layer to the map canvas
            layer = QgsVectorLayer(uri.uri(), table, "postgres")
            if layer.isValid():
                QgsMapLayerRegistry.instance().addMapLayer(layer)
            else:
                QMessageBox.information(iface.mainWindow(
                ), 'Erreur', u"La couche PostGis n'est pas valide.\nCa craint.")

    # Tests weither all the needed information is provided in the url, and
    # then build the url in the syntax understood by QGIS, which is never the
    # syntax given by the user
    def build_wms_url(self, raw_url):
        baseUrl = raw_url.split("?")[0] + "?"
        list_parameters = raw_url.split("?")[1].split('&')
        valid = False
        styleDefined = False
        CRSdefined = False
        formatDefined = False
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
                styleDefined = True
                style = i
            elif "crs=" in ilow:
                CRSdefined = True
                CRS = i
            elif "format=" in ilow:
                formatDefined = True
                imgformat = i

        if valid == True:
            if baseUrl.lower().startswith('url='):
                finalUrl = baseUrl + "&" + layers
            else:
                finalUrl = "url=" + baseUrl + "&" + layers

            if styleDefined == True:
                finalUrl += '&' + style
            else:
                finalUrl += '&styles='

            if formatDefined == True:
                finalUrl += '&' + imgformat
            else:
                finalUrl += '&format=image/jpeg'

            if CRSdefined == True:
                finalUrl += '&' + CRS
            output = ["WMS", name, finalUrl]
            return output

        else:
            return 0

    """# Add a WMS layer, given a url
    def add_wms_layer(self, url, name, firstUrl):
        rlayer = QgsRasterLayer(url, name, 'wms')
        if not rlayer.isValid():
            QMessageBox.information(iface.mainWindow(),'Erreur', firstUrl + " -> " + url)
        else:
            #self.dockwidget.text_input.setText(firstUrl + " -> " + url)
            QgsMapLayerRegistry.instance().addMapLayer(rlayer)"""

    # Tests weither all the needed information is provided in the url, and
    # then build the url in the syntax understood by QGIS, which is never the
    # syntax given by the user
    def build_wfs_url(self, raw_url):
        baseUrl = raw_url.split("?")[0] + "?"
        list_parameters = raw_url.split("?")[1].split('&')
        valid = False
        SRSdefined = False
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
                SRSdefined = True
                SRS = i

        if valid == True:
            finalUrl = baseUrl + typename

            if SRSdefined == True:
                finalUrl += '&' + SRS

            finalUrl += '&service=WFS&version=1.0.0&request=GetFeature'

            output = ["WFS", name, finalUrl]
            return output

        else:
            return 0

    # Add a WFS alyer, given a url
    """def add_wfs_layer(self, url, name, firstUrl):
        layer = QgsVectorLayer(url, name, 'WFS')
        if not layer.isValid():
            QMessageBox.information(iface.mainWindow(),'Erreur', firstUrl + " -> " + url)
        else:
            #self.dockwidget.text_input.setText(firstUrl + " -> " + url)
            QgsMapLayerRegistry.instance().addMapLayer(layer)"""

    # This parse the tags contained in API_answer[tags] and class them so they
    # are more easy to handle in other function such as update_fields()
    def get_tags(self, answer):
        # Initiating the dicts
        tags = answer['tags']
        resources_types = {}
        owners = {}
        keywords = {}
        theminspire = {}
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
                theminspire[tag] = tags[tag]
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
                    self.dockwidget.text_input.setText(tag)
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
                    self.dockwidget.text_input.setText(tag)

        # Creating the final object the function will return : a dictionary of
        # dictionaries
        new_tags = {}
        new_tags['type'] = resources_types
        new_tags['owner'] = owners
        new_tags['keywords'] = keywords
        new_tags['themeinspire'] = theminspire
        new_tags['formats'] = formats
        new_tags['srs'] = srs
        new_tags['actions'] = actions

        return new_tags

    # This save the current state/index of each user input so they keep this
    # state/index after being updated (cleared and filled again)
    def save_params(self):
        # get the data of the item which index is (get the combobox current
        # index)
        owner_param = self.dockwidget.owner.itemData(
            self.dockwidget.owner.currentIndex())
        inspire_param = self.dockwidget.inspire.itemData(
            self.dockwidget.inspire.currentIndex())
        format_param = self.dockwidget.format.itemData(
            self.dockwidget.format.currentIndex())
        srs_param = self.dockwidget.sys_coord.itemData(
            self.dockwidget.sys_coord.currentIndex())
        operation_param = self.dockwidget.operation.itemData(
            self.dockwidget.operation.currentIndex())
        # Saving the keywords that are selected : if a keyword state is
        # selected, he is added to the list
        key_params = []
        for i in xrange(self.dockwidget.keywords.count()):
            if self.dockwidget.keywords.itemData(i, 10) == 2:
                key_params.append(self.dockwidget.keywords.itemData(i, 32))

        # Saving the checked checkboxes (useful for the list saving)
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

        params = {}
        params['owner'] = owner_param
        params['inspire'] = inspire_param
        params['format'] = format_param
        params['srs'] = srs_param
        params['keys'] = key_params
        params['operation'] = operation_param
        params['view'] = view_param
        params['download'] = download_param
        params['other'] = other_param
        return params

    # This builds the url, retrieving the parameters from the widgets. When
    # the final url is built, it calles send_request_to_isogeo_API
    def search(self):
        #self.logger.info('Dans la fonction search')
        # Disabling all user inputs during the research function is running
        self.switch_widgets_on_and_off('off')

        # Setting some variables
        self.page_index = 1
        self.currentUrl = 'https://v1.api.isogeo.com/resources/search?'
        # Getting the parameters chosen by the user from the combobox
        if self.dockwidget.owner.currentIndex() != 0:
            owner = self.dockwidget.owner.itemData(
                self.dockwidget.owner.currentIndex())
        else:
            owner = False
        if self.dockwidget.inspire.currentIndex() != 0:
            inspire = self.dockwidget.inspire.itemData(
                self.dockwidget.inspire.currentIndex())
        else:
            inspire = False
        if self.dockwidget.format.currentIndex() != 0:
            formats = self.dockwidget.format.itemData(
                self.dockwidget.format.currentIndex())
        else:
            formats = False
        if self.dockwidget.sys_coord.currentIndex() != 0:
            sys_coord = self.dockwidget.sys_coord.itemData(
                self.dockwidget.sys_coord.currentIndex())
        else:
            sys_coord = False
        # Getting the text entered in the text field
        filters = ""
        if self.dockwidget.text_input.text():
            filters += self.dockwidget.text_input.text() + " "

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
        # Adding the keywords that are checked (whose data[10] == 2)
        for i in xrange(self.dockwidget.keywords.count()):
            if self.dockwidget.keywords.itemData(i, 10) == 2:
                filters += self.dockwidget.keywords.itemData(i, 32) + " "

        # If the geographical filter is activated, build a spatial filter
        if self.dockwidget.checkBox_4.isChecked():
            if self.get_canvas_coordinates():
                filters = filters[:-1]
                filters += "&box=" + self.get_canvas_coordinates() + "&rel=" + \
                    self.dockwidget.operation.itemData(
                        self.dockwidget.operation.currentIndex()) + " "
            else:
                QMessageBox.information(iface.mainWindow(
                ), 'Erreur :', "Le système de coordonnée de votre canevas ne semble\npas défini avec un code EPSG.\nIl ne peut donc pas être interprété par QGIS.\nMerci de rapporter ce problème sur le bug tracker.")

        filters = "q=" + filters[:-1]
        # self.dockwidget.text_input.setText(encoded_filters)
        if filters != "q=":
            self.currentUrl += filters
        if self.showResult == True:
            self.currentUrl += "&_limit=15&_include=links"
        else:
            self.currentUrl += "&_limit=0"
        # self.dockwidget.dump.setText(self.currentUrl)
        self.send_request_to_Isogeo_API(self.token)

    # Close to the search() function but triggered on the change page button.
    def next_page(self):
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
            if self.dockwidget.owner.currentIndex() != 0:
                owner = self.dockwidget.owner.itemData(
                    self.dockwidget.owner.currentIndex())
            else:
                owner = False
            if self.dockwidget.inspire.currentIndex() != 0:
                inspire = self.dockwidget.inspire.itemData(
                    self.dockwidget.inspire.currentIndex())
            else:
                inspire = False
            if self.dockwidget.format.currentIndex() != 0:
                formats = self.dockwidget.format.itemData(
                    self.dockwidget.format.currentIndex())
            else:
                formats = False
            if self.dockwidget.sys_coord.currentIndex() != 0:
                sys_coord = self.dockwidget.sys_coord.itemData(
                    self.dockwidget.sys_coord.currentIndex())
            else:
                sys_coord = False
            # Getting the text entered in the text field
            filters = ""
            if self.dockwidget.text_input.text():
                filters += self.dockwidget.text_input.text() + " "

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
            # Adding the keywords that are checked (whose data[10] == 2)
            for i in xrange(self.dockwidget.keywords.count()):
                if self.dockwidget.keywords.itemData(i, 10) == 2:
                    filters += self.dockwidget.keywords.itemData(i, 32) + " "

            # If the geographical filter is activated, build a spatial filter
            if self.dockwidget.checkBox_4.isChecked():
                if self.get_canvas_coordinates():
                    filters = filters[:-1]
                    filters += "&box=" + self.get_canvas_coordinates() + "&rel=" + \
                        self.dockwidget.operation.itemData(
                            self.dockwidget.operation.currentIndex()) + " "
                else:
                    QMessageBox.information(iface.mainWindow(
                    ), 'Erreur :', "Le système de coordonnée de votre canevas ne semble\npas défini avec un code EPSG.\nIl ne peut donc pas être interprété par QGIS.\nMerci de rapporter ce problème sur le bug tracker.")

            filters = "q=" + filters[:-1]
            # self.dockwidget.text_input.setText(encoded_filters)
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

    # Close to the search() function but triggered on the change page button.
    def previous_page(self):
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
            if self.dockwidget.owner.currentIndex() != 0:
                owner = self.dockwidget.owner.itemData(
                    self.dockwidget.owner.currentIndex())
            else:
                owner = False
            if self.dockwidget.inspire.currentIndex() != 0:
                inspire = self.dockwidget.inspire.itemData(
                    self.dockwidget.inspire.currentIndex())
            else:
                inspire = False
            if self.dockwidget.format.currentIndex() != 0:
                formats = self.dockwidget.format.itemData(
                    self.dockwidget.format.currentIndex())
            else:
                formats = False
            if self.dockwidget.sys_coord.currentIndex() != 0:
                sys_coord = self.dockwidget.sys_coord.itemData(
                    self.dockwidget.sys_coord.currentIndex())
            else:
                sys_coord = False
            # Getting the text entered in the text field
            filters = ""
            if self.dockwidget.text_input.text():
                filters += self.dockwidget.text_input.text() + " "

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
            # Adding the keywords that are checked (whose data[10] == 2)
            for i in xrange(self.dockwidget.keywords.count()):
                if self.dockwidget.keywords.itemData(i, 10) == 2:
                    filters += self.dockwidget.keywords.itemData(i, 32) + " "

            # If the geographical filter is activated, build a spatial filter
            if self.dockwidget.checkBox_4.isChecked():
                if self.get_canvas_coordinates():
                    filters = filters[:-1]
                    filters += "&box=" + self.get_canvas_coordinates() + "&rel=" + \
                        self.dockwidget.operation.itemData(
                            self.dockwidget.operation.currentIndex()) + " "
                else:
                    QMessageBox.information(iface.mainWindow(
                    ), 'Erreur :', "Le système de coordonnée de votre canevas ne semble\npas défini avec un code EPSG.\nIl ne peut donc pas être interprété par QGIS.\nMerci de rapporter ce problème sur le bug tracker.")

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

    # Minor function, calculate the number of pages given a number of results.
    def calcul_nb_page(self, nb_fiches):
        if nb_fiches <= 15:
            nb_page = 1
        else:
            if (nb_fiches % 15) == 0:
                nb_page = (nb_fiches / 15)
            else:
                nb_page = (nb_fiches / 15) + 1
        return nb_page

    # Minor function, handle what the API gives as a date, and create a
    # datetime object with it.
    def handle_date(self, API_date):
        date = API_date.split("T")[0]
        year = int(date.split('-')[0])
        month = int(date.split('-')[1])
        day = int(date.split('-')[2])
        new_date = datetime.date(year, month, day)
        return new_date.strftime("%d / %m / %Y")
        return new_date

    # Get the canvas coordinates in the right format and SRS (WGS84)
    def get_canvas_coordinates(self):
        e = iface.mapCanvas().extent()
        currentEPSG = int(iface.mapCanvas().mapRenderer(
        ).destinationCrs().authid().split(':')[1])
        if currentEPSG == 4326:
            coord = "{0},{1},{2},{3}".format(
                e.xMinimum(), e.yMinimum(), e.xMaximum(), e.yMaximum())
            return coord
        elif type(currentEPSG) is int:
            currentSRS = QgsCoordinateReferenceSystem(
                currentEPSG, QgsCoordinateReferenceSystem.EpsgCrsId)
            wgs = QgsCoordinateReferenceSystem(
                4326, QgsCoordinateReferenceSystem.EpsgCrsId)
            xform = QgsCoordinateTransform(currentSRS, wgs)
            minimum = xform.transform(QgsPoint(e.xMinimum(), e.yMinimum()))
            maximum = xform.transform(QgsPoint(e.xMaximum(), e.yMaximum()))
            coord = "{0},{1},{2},{3}".format(
                minimum[0], minimum[1], maximum[0], maximum[1])
            return coord
        else:
            return False

    # Minor one line function. Opens the bugtracker on the default browser
    # (supposedly cross platform)
    def open_bugtracker(self):
        webbrowser.open(
            'https://github.com/isogeo/isogeo-plugin-qgis/issues', new=0, autoraise=True)

    # Clear all widget and send a request to the API (which ends up updating
    # the fields : send_request() calls handle_reply(), which calls
    # update_fields())
    def reinitialize_research(self):
        self.hardReset = True
        self.dockwidget.checkBox.setCheckState(Qt.Unchecked)
        self.dockwidget.checkBox_2.setCheckState(Qt.Unchecked)
        self.dockwidget.checkBox_3.setCheckState(Qt.Unchecked)
        self.dockwidget.checkBox_4.setCheckState(Qt.Unchecked)
        self.dockwidget.text_input.clear()
        self.dockwidget.keywords.clear()
        self.dockwidget.operation.clear()
        self.dockwidget.owner.clear()
        self.dockwidget.inspire.clear()
        self.dockwidget.format.clear()
        self.dockwidget.sys_coord.clear()
        self.search()

    # Given a windows formated path, it transforms it in a path understood by
    # QGIS (\ are replaced by /)
    def format_path(self, string):
        new_string = ""
        for character in string:
            if character == '\\':
                new_string += "/"
            else:
                new_string += character
        return new_string

    # Launch a search request that will end up in showing the results.
    def search_with_content(self):
        self.showResult = True
        self.search()

    # Deactivate the widgets while a funcion is running so the user doesn't
    # clic everywhere ending up in multiple requests being sent at the same
    # time, making the plugin crash.
    def switch_widgets_on_and_off(self, mode):
        if mode == 'on':
            self.dockwidget.text_input.setReadOnly(False)
            self.dockwidget.filters_box.setEnabled(True)
            self.dockwidget.geofilter_box.setEnabled(True)
            self.dockwidget.widget.setEnabled(True)
            self.dockwidget.next.setEnabled(True)
            self.dockwidget.previous.setEnabled(True)
            self.dockwidget.initialize.setEnabled(True)
            self.dockwidget.show_button.setEnabled(True)

        else:
            self.dockwidget.text_input.setReadOnly(True)
            self.dockwidget.filters_box.setEnabled(False)
            self.dockwidget.geofilter_box.setEnabled(False)
            self.dockwidget.widget.setEnabled(False)
            self.dockwidget.next.setEnabled(False)
            self.dockwidget.previous.setEnabled(False)
            self.dockwidget.initialize.setEnabled(False)
            self.dockwidget.show_button.setEnabled(False)

    # --------------------------------------------------------------------------

    # This function is launched when the plugin is activated.
    def run(self):
        """Run method that loads and starts the plugin"""

        if not self.pluginIsActive:
            self.pluginIsActive = True

            # print "** STARTING Isogeo"

            # dockwidget may not exist if:
            #    first run of plugin
            #    removed on close (see self.onClosePlugin method)
            if self.dockwidget == None:
                # Create the dockwidget (after translation) and keep reference
                self.dockwidget = IsogeoDockWidget()

            # connect to provide cleanup on closing of dockwidget
            self.dockwidget.closingPlugin.connect(self.onClosePlugin)

            # show the dockwidget
            # TODO: fix to allow choice of dock location
            self.iface.addDockWidget(Qt.RightDockWidgetArea, self.dockwidget)
            self.dockwidget.show()

        """ --- LOG LOG LOG --- """

        """self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)
        self.formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s')
        self.file_handler = RotatingFileHandler(self.get_plugin_path() + "/activity.log", 'a', 1000000, 1)
        self.file_handler.setLevel(logging.DEBUG)
        self.file_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.file_handler)
        self.steam_handler = logging.StreamHandler()
        self.steam_handler.setLevel(logging.DEBUG)
        self.logger.addHandler(self.steam_handler)"""

        # Fixing a qgis.core bug that shows a warning banner "connexion time
        # out" whenever a request is sent (even successfully) See :
        # http://gis.stackexchange.com/questions/136369/download-file-from-network-using-pyqgis-2-x#comment299999_136427
        iface.messageBar().widgetAdded.connect(iface.messageBar().clearWidgets)
        # Initiating values (TO DO : Move to init section)
        self.currentUrl = 'https://v1.api.isogeo.com/resources/search?'
        self.page_index = 1

        """ --- CONNECTING FUNCTIONS --- """
        # Write in the config file when the user accept the authentification
        # window
        self.authentification_window.accepted.connect(self.write_ids_and_test)
        # Connecting the comboboxes to the search function
        self.dockwidget.owner.activated.connect(self.search)
        self.dockwidget.inspire.activated.connect(self.search)
        self.dockwidget.format.activated.connect(self.search)
        self.dockwidget.sys_coord.activated.connect(self.search)
        self.dockwidget.operation.activated.connect(self.search)
        # Connecting the text input to the search function
        self.dockwidget.text_input.editingFinished.connect(self.search)
        # Connecting the checkboxes to the search function
        self.dockwidget.checkBox.clicked.connect(self.search)
        self.dockwidget.checkBox_2.clicked.connect(self.search)
        self.dockwidget.checkBox_3.clicked.connect(self.search)
        self.dockwidget.checkBox_4.clicked.connect(self.search)
        # Connecting the previous and next page buttons to their functions
        self.dockwidget.next.pressed.connect(self.next_page)
        self.dockwidget.previous.pressed.connect(self.previous_page)
        # Connecting the bug tracker button to its function
        self.dockwidget.report.pressed.connect(self.open_bugtracker)
        # Connecting the "reinitialize research button" to a research without
        # filters
        self.dockwidget.initialize.pressed.connect(self.reinitialize_research)
        # Change user
        self.dockwidget.changeUser.pressed.connect(
            self.authentification_window.show)
        # show results
        self.dockwidget.show_button.pressed.connect(self.search_with_content)

        """ --- Actions when the plugin is launched --- """
        self.test_config_file_existence()
        self.user_authentification()
        self.test_proxy_configuration()

        self.dockwidget.favorite_combo.setEnabled(False)
        self.dockwidget.save_favorite.setEnabled(False)
        self.dockwidget.groupBox.setEnabled(False)
        self.dockwidget.groupBox_2.setEnabled(False)
        self.dockwidget.groupBox_3.setEnabled(False)
        self.dockwidget.groupBox_4.setEnabled(False)
        self.dockwidget.tab_3.setEnabled(False)
