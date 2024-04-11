# -*- coding: utf-8 -*-

from qgis.PyQt.QtCore import QSettings
import json
from pprint import pprint
from pathlib import Path

qsettings = QSettings()

input_json_path = Path(r"C:\Users\SimonSAMPERE\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\isogeo-plugin-qgis\isogeo_qsettings_340.json")
with open(input_json_path, "r") as json_file:
    json_content = json.load(json_file)

for key in json_content:
    qsettings.setValue(key, json_content.get(key))