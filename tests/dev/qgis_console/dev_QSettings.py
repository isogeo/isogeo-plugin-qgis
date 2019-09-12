# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

# PyQT
from qgis.PyQt.QtCore import QSettings

# QGIS Qt Application settings
qsettings = QSettings()
# list subgroups
print(qsettings.childGroups())

# get Isogeo settings
qsettings.beginGroup("isogeo")
print(qsettings.childGroups())
print(qsettings.allKeys())

# exit Isogeo settings
qsettings.endGroup()
