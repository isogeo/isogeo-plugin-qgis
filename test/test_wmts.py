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

# Ajoutés par moi
from qgis.utils import iface, plugin_times, QGis, reloadPlugin
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

from collections import OrderedDict
from functools import partial
import db_manager.db_plugins.postgis.connector as con
import operator
import time


# ===========================

# Boundless
bd_gc = "http://suite.opengeo.org/geoserver/gwc/service/wmts?request=GetCapabilities"
bd_lyr = "opengeo:countries"

# Isogeo
i_gc = "http://noisy.hq.isogeo.fr:6090/geoserver/gwc/service/wmts?REQUEST=GetCapabilities"
i_lyr = "Isogeo:WC2014_stadiums"
i_cpl = "http://noisy.hq.isogeo.fr:6090/geoserver/gwc/service/wmts?service=WMTS%26crs=EPSG:4326&dpiMode=7&featureCount=10&format=image/png&layers=Isogeo:WC2014_stadiums&styles=default&tileMatrixSet=EPSG:4326"

# Misc
msc_gc = "http://opencache.statkart.no/gatekeeper/gk/gk.open_wmts?service=WMTS&request=GetCapabilities"
msc_lyr = "Europakart"


layer = QgsRasterLayer(i_cpl, "Isogeo", "wtms")
if layer.isValid():
    QgsMapLayerRegistry.instance().addMapLayer(layer)
else:
    print("rooo")

#contextualWMSLegend=0&crs=EPSG:4326&dpiMode=7&featureCount=10&format=image/png&layers=Isogeo:WC2014_stadiums&styles=default&tileMatrixSet=EPSG:4326&url=http://noisy.hq.isogeo.fr:6090/geoserver/gwc/service/wmts?REQUEST%3DGetCapabilities


# WMS
# see: http://gis.stackexchange.com/questions/183485/load-wms-with-pyqgis/183751#183751

uri_separator = '&'
uri_url = 'url=http://geoservices.brgm.fr/geologie/'
# uri_username = 'username=user'
# uri_password = 'password=pass'
uri_format = 'format=image/png'
uri_layers = 'layers=BSS'
uri_crs = 'crs=EPSG:4326'
uri_styles = "styles="

url_with_params = uri_separator.join((uri_url,
                                      # uri_username,
                                      # uri_password,
                                      uri_format,
                                      uri_layers,
                                      uri_crs))
rlayer = QgsRasterLayer(url_with_params, 'norther', 'wms')
print rlayer.error().message()

# url = http://geoservices.brgm.fr/geologie?&layers=BSS&styles=&format=image/png
