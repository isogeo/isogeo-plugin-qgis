# -*- coding: utf-8 -*-

from qgis.PyQt.QtCore import QSettings
from pprint import pprint

qsettings = QSettings()

quicksearch_key_prefix = "isogeo/user/quicksearches/"
quicksearch_name = "test"
specific_quicksearch_key_prefix = "{}{}".format(quicksearch_key_prefix, quicksearch_name)
li_quicksearch_names = []

for key in qsettings.allKeys():
    if specific_quicksearch_key_prefix in key:
        print("{} : {}".format(key, qsettings.value(key)))
    else:
        pass

    if quicksearch_key_prefix in key and key.replace(quicksearch_key_prefix, "").split("/")[0] not in li_quicksearch_names:
        li_quicksearch_names.append(key.replace(quicksearch_key_prefix, "").split("/")[0])
    else:
        pass

pprint(li_quicksearch_names)