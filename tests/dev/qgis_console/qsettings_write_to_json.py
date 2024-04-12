# -*- coding: utf-8 -*-

from qgis.PyQt.QtCore import QSettings
from pprint import pprint
import json
from pathlib import Path

qsettings = QSettings()

isogeo_key_prefix = "isogeo/"
involved_keys = [key for key in qsettings.allKeys() if key.startswith(isogeo_key_prefix)]
qsettings_dict = {}
for key in involved_keys:
    qsettings_dict[key] = qsettings.value(key)

output_json_path = Path(r"C:\Users\SimonSAMPERE\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\isogeo-plugin-qgis\isogeo_qsettings_350_to_350.json")

with open(output_json_path, "w") as outfile:
    json.dump(qsettings_dict, outfile, sort_keys=True, indent=4
)