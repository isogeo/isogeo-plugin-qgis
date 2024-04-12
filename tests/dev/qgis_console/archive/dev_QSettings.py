# -*- coding: utf-8 -*-
#! python3  # noqa: E265

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
