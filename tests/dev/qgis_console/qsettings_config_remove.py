# -*- coding: utf-8 -*-

from qgis.PyQt.QtCore import QSettings
import json
from pprint import pprint
from pathlib import Path

qsettings = QSettings()

li_config_settings_keys = [
    "isogeo/env/api_base_url",
    "isogeo/env/api_auth_url",
    "isogeo/env/app_base_url",
    "isogeo/env/help_base_url",
    "isogeo/settings/background_map_url",
    "isogeo/settings/portal_base_url",
    "isogeo/settings/add_metadata_url_portal",
]

for key in li_config_settings_keys:
    if key in qsettings.allKeys():
        qsettings.remove(key)
        pprint("{} removed".format(key))
    else:
        pprint("{} not found".format(key))
