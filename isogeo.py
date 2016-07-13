# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Isogeo
                                 A QGIS plugin
 This is the Isogeo plugin
                              -------------------
        begin                : 2016-07-13
        git sha              : $Format:%H$
        copyright            : (C) 2016 by Isogeo
        email                : theo.sinatti@isogeo.fr
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
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, Qt, QByteArray, QUrl
#Ajouté oar moi à partir de QMessageBox
from PyQt4.QtGui import QAction, QIcon, QMessageBox, QTableWidgetItem, QCheckBox, QStandardItemModel, QStandardItem

# Initialize Qt resources from file resources.py
import resources

# Import the code for the DockWidget
from isogeo_dockwidget import IsogeoDockWidget
# Import du code de la pop up d'authentification
from authentification import authentification

import os.path

#Ajoutés par moi
from qgis.utils import iface
from qgis.core import QgsNetworkAccessManager
from PyQt4.QtNetwork import QNetworkRequest
import ConfigParser
import json
import base64
import urllib
import time


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

        #print "** INITIALIZING Isogeo"

        self.pluginIsActive = False
        self.dockwidget = None

        self.authentification_window = authentification()


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
            text=self.tr(u'Search geodata'),
            callback=self.run,
            parent=self.iface.mainWindow())

    #--------------------------------------------------------------------------

    def onClosePlugin(self):
        """Cleanup necessary items here when plugin dockwidget is closed"""

        #print "** CLOSING Isogeo"

        # disconnects
        self.dockwidget.closingPlugin.disconnect(self.onClosePlugin)

        # remove this statement if dockwidget is to remain
        # for reuse if plugin is reopened
        # Commented next statement since it causes QGIS crashe
        # when closing the docked window:
        # self.dockwidget = None

        self.pluginIsActive = False


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""

        #print "** UNLOAD Isogeo"

        for action in self.actions:
            self.iface.removePluginWebMenu(
                self.tr(u'&Isogeo'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    #--------------------------------------------------------------------------
    
    # This retrieves the path to the folder where the plugin is (it usually is 'C:/user/.qgis2/python/plugin')
    def get_plugin_path(self):
            basepath = os.path.dirname(os.path.realpath(__file__))
            return basepath

    # Check if the file already exists and if not, create it. 
    def test_config_file_existence(self):
        self.config = ConfigParser.ConfigParser()
        self.config_path = self.get_plugin_path() + "/config.ini"
        if os.path.isfile(self.config_path):
            pass
        else:
            print "You've messed up something bruh !"
            config_file = open(self.config_path,'w')
            config.write(config_file)
            # TO DO : CREER UN TEMPLATE
            config_file.close()
    
    # This is the first major function the plugin calls when executed. It retrieves the id and secret from the config file. If they are set to their default value, it asks for them. if not it ties to send a request.
    def user_authentification(self):
        self.config.read(self.config_path)
        config_dict = {s:dict(self.config.items(s)) for s in self.config.sections()}
        self.user_id = config_dict['Isogeo_ids']['application_id']
        self.user_secret = config_dict['Isogeo_ids']['application_secret']
        if self.user_id != 'application_id':
            # Demande les identifiants dans une pop-up et écrit les.
            self.ask_for_token(self.user_id, self.user_secret)
        else:
            self.authentification_window.show()

    # When the authentification window is closed, stores the values in the file, then call the authentification function to test them.
    def write_ids_and_test(self):
        self.user_id = self.authentification_window.user_id_input.text()
        self.user_secret = self.authentification_window.user_secret_input.text()
        config_file = open(self.config_path,'w')
        self.config.set('Isogeo_ids', 'application_id', self.user_id)
        self.config.set('Isogeo_ids', 'application_secret', self.user_secret)
        self.config.write(config_file)
        config_file.close()

        self.user_authentification()

    # This send a POST request to Isogeo API with the user id and secret in its header. The API should return an access token
    def ask_for_token(self, c_id, c_secret):
        headervalue = "Basic " + base64.b64encode(c_id + ":" + c_secret)
        data = urllib.urlencode({"grant_type":"client_credentials"})
        dataByte = QByteArray()
        dataByte.append(data)
        manager = QgsNetworkAccessManager.instance()
        url = QUrl('https://id.api.isogeo.com/oauth/token')
        request = QNetworkRequest(url)
        request.setRawHeader("Authorization", headervalue)
        self.token_reply = manager.post( request, dataByte )
        self.token_reply.finished.connect(self.handle_token)

    # This handles the API answer. If it has sent an access token, it calls the initialization function. If not, it raises an error, and ask for new IDs
    def handle_token(self):
        bytarray = self.token_reply.readAll()
        content = str(bytarray)
        parsed_content = json.loads(content)
        if 'access_token' in parsed_content:
            self.token = "Bearer " + parsed_content['access_token']
            self.dockwidget.dump.setText(self.token)
        # TO DO : Distinguer plusieurs cas d'erreur
        elif 'error' in parsed_content:
            QMessageBox.information(iface.mainWindow(),'Erreur', parsed_content['error'])
            self.authentification_window.show()
        else:
            self.dockwidget.text_input.setText("Erreur inconnue.")

    #--------------------------------------------------------------------------

    def run(self):
        """Run method that loads and starts the plugin"""

        if not self.pluginIsActive:
            self.pluginIsActive = True

            #print "** STARTING Isogeo"

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

        # Save the user ids when the authentification window is accepted.
        self.authentification_window.accepted.connect(self.write_ids_and_test)

        # Firs actions at the opening of the plugin
        self.test_config_file_existence()
        self.user_authentification()

