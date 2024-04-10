# -*- coding: utf-8 -*-
#! python3  # noqa: E265

# Standard library
import logging
from pathlib import Path

# PyQGIS
from qgis.utils import iface

# ############################################################################
# ########## Globals ###############
# ##################################

logger = logging.getLogger("IsogeoQgisPlugin")

msgBar = iface.messageBar()

# ############################################################################
# ########## Classes ###############
# ##################################


class CacheManager:
    """Basic class to manage the cache system of the layer addition."""

    def __init__(self, geo_service_manager: object, settings_manager: object = None):

        self.cached_unreached_paths = list()
        # Translator
        self.tr = object
        # GeoServiceManagerModule used by LayerAdder which temporary cache has to be cleaned
        self.geo_srv_mng = geo_service_manager
        self.settings_mng = settings_manager
        self.settings_mng.load_cache()

    def clean_geoservice_cache(self):
        self.geo_srv_mng.service_cached_dict = {
            "WFS": {},
            "WMS": {},
            "WMTS": {},
            "EFS": {},
            "EMS": {},
        }

    def save_cache_to_qsettings(self):
        self.settings_mng.set_value(self.settings_mng.cache_qsetting_key, self.cached_unreached_paths)
        return

    def add_file_path(self, file_path: Path):
        self.cached_unreached_paths.append(file_path)
        self.save_cache_to_qsettings()
        return

    def loader(self):
        """Load ignored elements calling SettingsManager."""
        self.cached_unreached_paths = self.settings_mng.load_cache()
        return

    def cleaner(self):
        """Removes the stored elements and empties the JSON cache file."""
        self.cached_unreached_paths = []
        self.save_cache_to_qsettings()
        self.clean_geoservice_cache()
        logger.debug("Cache has been cleaned")
        msgBar.pushMessage(
            self.tr("Cache has been cleaned.", context=__class__.__name__), duration=3
        )
        return


# #############################################################################
# ##### Stand alone program ########
# ##################################
if __name__ == "__main__":
    """Standalone execution."""
