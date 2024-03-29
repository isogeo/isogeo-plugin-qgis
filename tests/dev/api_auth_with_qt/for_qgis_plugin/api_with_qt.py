# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ApiWithQt
                                 A QGIS plugin
 test API connexion with Qt in QGIS
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2019-06-12
        git sha              : $Format:%H$
        copyright            : (C) 2019 by Isogeo
        email                : projects+qgis@isogeo.com
 ***************************************************************************/
/***************************************************************************

    This module has been developed in accordance with this Issue: 
    https://github.com/isogeo/isogeo-plugin-qgis/issues/186 

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
# originial imports
# Initialize Qt resources from file resources.py
from .resources import *

# Import the code for the dialog
from .api_with_qt_dialog import ApiWithQtDialog
import os.path

# additional imports
# Standard library
from urllib.parse import urlencode
import os
import base64
import json
from functools import partial
import logging
from logging.handlers import RotatingFileHandler

# PyQT
from qgis.PyQt.QtNetwork import QNetworkAccessManager, QNetworkRequest
from qgis.PyQt.QtCore import (
    QUrl,
    QByteArray,
    QSettings,
    QTranslator,
    qVersion,
    QCoreApplication,
)
from qgis.PyQt.QtWidgets import QApplication, QAction
from qgis.PyQt.QtGui import QIcon

# PyQGIS
from qgis.core import QgsNetworkAccessManager, QgsProject
from qgis.utils import iface

# isogeo-pysdk
from .isogeo_pysdk import IsogeoUtils, Isogeo


class ApiWithQt:
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
        locale = QSettings().value("locale/userLocale")[0:2]
        locale_path = os.path.join(self.plugin_dir, "i18n", "ApiWithQt_{}.qm".format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > "4.3.3":
                QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr("&ApiWithQt")

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

        # additional initialization lines
        # getting creds
        self.utils = IsogeoUtils()
        self.app_creds = self.utils.credentials_loader(
            "C:\\Users\\Adminstrateur\\AppData\\Roaming\\QGIS\\QGIS3\\profiles\\default\\python\\plugins\\api_with_qt\\client_secrets.json"
        )
        self.app_id = self.app_creds.get("client_id")
        self.app_secrets = self.app_creds.get("client_secret")

        # prepare connection
        self.naMngr = QgsNetworkAccessManager.instance()
        self.token_url = "https://id.api.isogeo.com/oauth/token"
        self.request_url = "https://v1.api.isogeo.com/resources/search?_limit=0&_offset=0"
        self.token = ""

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
        return QCoreApplication.translate("ApiWithQt", message)

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
        parent=None,
    ):
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
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(self.menu, action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ":/plugins/api_with_qt/icon.png"
        self.add_action(
            icon_path,
            text=self.tr("API With Qt"),
            callback=self.run,
            parent=self.iface.mainWindow(),
        )

        # will be set False in run()
        self.first_start = True

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(self.tr("&ApiWithQt"), action)
            self.iface.removeToolBarIcon(action)

    # additional methode to check auth file validity and API authentication
    def pysdk_checking(self):
        isogeo = Isogeo(self.app_id, self.app_secrets)
        token = isogeo.connect()
        self.md_expected = isogeo.search(token=token, whole_share=0, page_size=0, augment=0).get(
            "total"
        )
        self.dlg.lbl_expected.setText("{} expected resources".format(self.md_expected))

    # additional methode to send token request to the API (with QgsNetworkAccessManager class)
    def api_authentification(self):
        # creating credentials header
        crd_header_value = QByteArray()
        crd_header_value.append("Basic ")
        crd_header_value.append(
            base64.b64encode("{}:{}".format(self.app_id, self.app_secrets).encode())
        )
        crd_header_name = QByteArray()
        crd_header_name.append("Authorization")

        # creating Content-Type header
        ct_header_value = QByteArray()
        ct_header_value.append("application/json")

        # creating request
        token_rqst = QNetworkRequest(QUrl(self.token_url))

        # setting headers
        token_rqst.setRawHeader(crd_header_name, crd_header_value)
        token_rqst.setHeader(token_rqst.ContentTypeHeader, ct_header_value)

        # creating data
        databyte = QByteArray()
        databyte.append(urlencode({"grant_type": "client_credentials"}))

        # requesting and handle reply
        token_reply = self.naMngr.post(token_rqst, databyte)
        token_reply.finished.connect(partial(self.api_handle_token, reply=token_reply))

    # additional methode to handle token reply from the API
    def api_handle_token(self, reply):
        # formatting API response
        bytarray = reply.readAll()
        content = bytarray.data().decode("utf8")

        # checking API response structure
        try:
            parsed_content = json.loads(content)
        except:
            return

        # chacking token existance in API response
        if "access_token" in parsed_content:
            # storing token
            self.token = "Bearer " + parsed_content.get("access_token")
            # sending resources request to the API with stored token
            self.api_get_request()
        else:
            pass

    # additionnal methode to send resources request to the API (with QgsNetworkAccessManager)
    def api_get_request(self):
        # creating credentials header
        crd_header_value = QByteArray()
        crd_header_value.append(self.token)
        crd_header_name = QByteArray()
        crd_header_name.append("Authorization")

        # creating request
        rqst = QNetworkRequest(QUrl(self.request_url))

        # setting credentials header
        rqst.setRawHeader(crd_header_name, crd_header_value)

        # sending request and handle API reply
        rqst_reply = self.naMngr.get(rqst)
        rqst_reply.finished.connect(partial(self.api_handle_request, reply=rqst_reply))

    # additional methode to handle reply from the API
    def api_handle_request(self, reply):
        # formatting API response
        bytarray = reply.readAll()
        content = bytarray.data().decode("utf8")

        # check API response structure
        try:
            parsed_content = json.loads(content)
        except:
            return

        # Storing and displaying the result provided by the API
        self.md_found = parsed_content.get("total")
        self.dlg.lbl_found.setText("{} resources found".format(self.md_found))

    def run(self):
        """Run method that performs all the real work"""

        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start == True:
            self.first_start = False
            self.dlg = ApiWithQtDialog()

        # additional lines to set ui and check credentials
        self.dlg.btn.clicked.connect(self.api_authentification)
        self.pysdk_checking()

        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # additional lines to clean the ui
            self.dlg.lbl_found.setText("")
            self.dlg.lbl_expected.setText("")
