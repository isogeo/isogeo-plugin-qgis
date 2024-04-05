from qgis.PyQt.QtCore import QSettings
from pprint import pprint

qsettings = QSettings()
pprint(qsettings.value("isogeo/user/unreachable_filepath"))