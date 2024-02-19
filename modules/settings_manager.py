# -*- coding: utf-8 -*-
#! python3  # noqa: E265

# Standard library
import logging

# PyQGIS
from qgis.utils import iface

# PyQT
from qgis.PyQt.QtCore import QSettings


# ############################################################################
# ########## Globals ###############
# ##################################

logger = logging.getLogger("IsogeoQgisPlugin")
msgBar = iface.messageBar()

# ############################################################################
# ########## Classes ###############
# ##################################


class SettingsManager(QSettings):
    """Inheritance from Isogeo Python SDK utils class. It adds some
    specific tools for QGIS plugin."""

    def __init__(self):
        """Check and manage authentication credentials."""
        # instanciate
        super().__init__()

    def get_locale(self):
        """Return 'locale/userLocale' setting value about QGIS language configuration"""

        try:
            locale = str(self.value("locale/userLocale", "fr", type=str))[0:2]
        except TypeError as e:
            logger.error(
                "Bad type in QSettings: {}. Original error: {}".format(
                    type(self.value("locale/userLocale")), e
                )
            )
            locale = "fr"
        return locale

    def get_value(self, setting_name: str, default_value=None, type=None):
        if type is None:
            return self.value(setting_name, default_value)
        else:
            return self.value(setting_name, default_value, type)

    def set_value(self, setting_name: str, value):
        self.setValue(setting_name, value)
        return value


# #############################################################################
# ##### Stand alone program ########
# ##################################
if __name__ == "__main__":
    """Standalone execution."""
