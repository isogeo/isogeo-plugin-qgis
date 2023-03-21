# -*- coding: utf-8 -*-
""" A script to remove Isogeo's settings from QGIS' settings.
Usefull to test first authentication to Isogeo plugin.

"""

from qgis.PyQt.QtCore import QSettings

qsettings = QSettings()

if "isogeo" in qsettings.childGroups():
    print("'isogeo' child group detected in QSettings --> removing it")
    qsettings.remove("isogeo")
else:
    print("QSettings already cleared")
