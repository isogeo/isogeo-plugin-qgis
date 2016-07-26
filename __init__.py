# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Isogeo
                                 A QGIS plugin
 Isogeo search engine within QGIS
                             -------------------
        begin                : 2016-07-22
        copyright            : (C) 2016 by Isogeo, Theo Sinatti, GeoJulien
        email                : projets+qgis@isogeo.fr
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load Isogeo class from file Isogeo.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .isogeo import Isogeo
    return Isogeo(iface)
