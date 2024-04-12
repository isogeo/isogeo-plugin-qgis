# -*- coding: utf-8 -*-

from qgis.PyQt.QtCore import QSettings

qsettings = QSettings()

quicksearch_key_prefix = "isogeo/user/quicksearches"

li_involved_keys = [key for key in qsettings.allKeys() if key.startswith(quicksearch_key_prefix)]

if len(li_involved_keys):
    qsettings.remove(quicksearch_key_prefix)
    print("QSettings cleared :)")
else:
    print("QSettings already cleared")
