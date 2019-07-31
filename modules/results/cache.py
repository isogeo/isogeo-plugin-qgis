# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

# Standard library
import logging
import json

# ############################################################################
# ########## Globals ###############
# ##################################

logger = logging.getLogger("IsogeoQgisPlugin")

# ############################################################################
# ########## Classes ###############
# ##################################


class CacheManager():
    """Basic class to manage the cache system of the layer addition. 
    """

    def __init__(self, path_cache_file : str = None):
        # Path to JSON cache file
        if isinstance(path_cache_file, str):
            self.cache_file = path_cache_file
        elif path_cache_file != None:
            raise TypeError("str expected")
        else:
            raise ValueError("path to JSON cache file must be given to instantiate CacheManager")

        # Objects for storing inaccessible elements 
        self.cached_dict = {}
        self.cached_unreach_paths = []
        self.cached_unreach_postgis = []
        self.cached_unreach_srv = []

    def dumper(self):
        """Builds a dict from the stored inaccessible elements 
        and dumps it into the JSON cache file.

        :returns: the dict dumped in the JSON file

        :rtype: dict
        """
        self.cached_dict = {"files" : list(set(self.cached_unreach_paths)),
                            "PostGIS" : list(set(self.cached_unreach_postgis)),
                            "services" : list(set(self.cached_unreach_srv))}
        logger.debug("cached_dict : {}".format(self.cached_dict))

        with open(self.cache_file, 'w') as cache:
            json.dump([self.cached_dict], cache, indent=4)
        logger.debug("Paths cache has been dumped")
        
        return self.cached_dict

    def loader(self):
        """Load and store ignored elements from the JSON cache file.
        
        :returns: the content of the JSON cache file

        :rtype: dict
        """
        try:
            with open(self.cache_file, 'r') as cache:
                cache_loaded = json.load(cache)
            logger.debug("cache_loaded : {}".format(cache_loaded))
            if isinstance(cache_loaded[0], dict) :
                self.cached_unreach_paths = cache_loaded[0].get("files")
                self.cached_unreach_postgis = cache_loaded[0].get("PostGIS")
                self.cached_unreach_srv = cache_loaded[0].get("services")
                logger.debug("Paths cache has been loaded")
            else:
                logger.debug("Old cache file format detected")
                self.cached_unreach_paths = cache_loaded
            return cache_loaded

        except ValueError as e:
            logger.error("Path JSON corrupted")
        except IOError:
        	logger.debug("Paths cache file not found. Maybe because of first launch.")
        	self.dumper()

    def cleaner(self):
        """Removes the stored elements and empties the JSON cache file."""
        self.cached_unreach_paths = []
        self.cached_unreach_postgis = []
        self.cached_unreach_srv = []
        self.dumper()
        logger.debug("Cache has been cleaned")

# #############################################################################
# ##### Stand alone program ########
# ##################################
if __name__ == '__main__':
    """Standalone execution."""
