# -*- coding: utf-8 -*-

from qgis.PyQt.QtCore import QSettings
import json
from pprint import pprint
from pathlib import Path

qsettings = QSettings()

config_settings = {
    "api_base_url": "isogeo/env/api_base_url",
    "api_auth_url": "isogeo/env/api_auth_url",
    "app_base_url": "isogeo/env/app_base_url",
    "help_base_url": "isogeo/env/help_base_url",
    "background_map_url": "isogeo/settings/background_map_url",
    "portal_base_url": "isogeo/settings/portal_base_url",
    "add_metadata_url_portal": "isogeo/settings/add_metadata_url_portal",
}

config_json_path = Path(r"C:\Users\SimonSAMPERE\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\isogeo-plugin-qgis\config.json")
with open(config_json_path, "r") as json_file:
    config_json_content = json.load(json_file)


for setting in config_settings:
    qsetting_key = config_settings[setting]
    qsetting_value = qsettings.value(qsetting_key)
    json_value = config_json_content.get(setting)
    if qsetting_value == json_value:
        print("☻ {} : '{}'".format(setting, json_value))
    else:
        print("Ø {} : '{}' vs '{}'".format(setting, json_value, qsetting_value))