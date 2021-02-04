# -*- coding: utf-8 -*-
#! python3  # noqa: E265

# Standard library
import logging
import json
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

    def __init__(self, geo_service_manager: object):
        # Path to JSON cache file
        self.cache_file = Path(__file__).parents[2] / "_user" / "cache.json"
        # Objects for storing inaccessible elements
        self.cached_dict = dict()
        self.cached_unreach_paths = list()
        self.cached_unreach_postgis = list()
        self.cached_unreach_service = {
            "WFS": [],
            "WMS": [],
            "WMTS": [],
            "EFS": [],
            "EMS": [],
        }
        # Translator
        self.tr = object
        # GeoServiceManagerModule used by LayerAdder wich temporary cache has to be cleaned
        self.geo_srv_mng = geo_service_manager

    def dumper(self):
        """Builds a dict from the stored inaccessible elements
        and dumps it into the JSON cache file.

        :returns: the dict dumped in the JSON file

        :rtype: dict
        """
        # prepare JSON file content
        self.cached_dict = {
            "files": list(set(self.cached_unreach_paths)),
            "PostGIS": list(set(self.cached_unreach_postgis)),
            "services": {
                "WFS": list(set(self.cached_unreach_service.get("WFS"))),
                "WMS": list(set(self.cached_unreach_service.get("WMS"))),
                "WMTS": list(set(self.cached_unreach_service.get("WMTS"))),
                "EFS": list(set(self.cached_unreach_service.get("EFS"))),
                "EMS": list(set(self.cached_unreach_service.get("EMS"))),
            }
        }
        with open(self.cache_file, "w") as cache:
            json.dump([self.cached_dict], cache, indent=4)
        logger.debug("Cache has been dumped")
        self.geo_srv_mng.service_cached_dict = {
            "WFS": dict(),
            "WMS": dict(),
            "WMTS": dict(),
            "EFS": dict(),
            "EMS": dict(),
        }

    def loader(self):
        """Load and store ignored elements from the JSON cache file."""
        try:
            with open(self.cache_file, "r") as cache:
                cache_loaded = json.load(cache)
            if len(cache_loaded) == 0:
                logger.debug("Empty cache file.")
            elif isinstance(cache_loaded[0], dict):
                self.cached_unreach_paths = cache_loaded[0].get("files")
                logger.debug("Cached unreachable file path has been successfuly loaded.")
                self.cached_unreach_postgis = cache_loaded[0].get("PostGIS")
                self.cached_unreach_service = cache_loaded[0].get("services")
                for srv_type, li_unreachable_srv in cache_loaded[0].get("services").items():
                    if len(li_unreachable_srv):
                        cached_srv_content = [tuple(unreachable_srv) for unreachable_srv in li_unreachable_srv]
                        self.cached_unreach_service[srv_type] = cached_srv_content
                    else:
                        self.cached_unreach_service[srv_type] = []
            else:
                logger.debug("Old cache file format detected.")
                self.cached_unreach_paths = cache_loaded
            return cache_loaded

        except ValueError:
            logger.error("Path JSON corrupted")
        except IOError:
            logger.debug("Cache file not found. Maybe because of first launch.")
            self.dumper()

    def cleaner(self):
        """Removes the stored elements and empties the JSON cache file."""
        self.cached_unreach_paths = []
        self.cached_unreach_postgis = []
        self.cached_unreach_service = {
            "WFS": [],
            "WMS": [],
            "WMTS": [],
            "EFS": [],
            "EMS": [],
        }
        self.dumper()
        logger.debug("Cache has been cleaned")
        self.geo_srv_mng.service_cached_dict = {
            "WFS": dict(),
            "WMS": dict(),
            "WMTS": dict(),
            "EFS": dict(),
            "EMS": dict(),
        }
        msgBar.pushMessage(
            self.tr("Cache has been cleaned.", context=__class__.__name__), duration=3
        )


# #############################################################################
# ##### Stand alone program ########
# ##################################
if __name__ == "__main__":
    """Standalone execution."""
