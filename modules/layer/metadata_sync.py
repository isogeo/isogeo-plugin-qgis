# -*- coding: utf-8 -*-
#! python3  # noqa: E265

# Standard library
import logging


# ############################################################################
# ########## Globals ###############
# ##################################

logger = logging.getLogger("IsogeoQgisPlugin")

srv_types = ["WMS", "WFS", "EFS", "EMS", "WMTS"]
file_types = ["vector", "raster"]

# ############################################################################
# ########## Globals ###############
# ##################################


class MetadataSynchronizer:
    """Basic class that allow to fill some tabs of 'Layer's Properties' with metadatas"""

    def __init__(self):
        """Class constructor."""

    def basic_sync(self, layer, info):
        logger.debug("Filling {} layer's properties from : {}".format(layer.name, info))
        # If the data is a PostGIS table
        if isinstance(info, dict):
            self.filling_field(
                layer,
                info.get("title", "notitle"),
                info.get("abstract", ""),
                info.get("keywords", ()),
            )
        # If the data is a file or a service
        else:
            layer_type = info[0]
            # vector or raster file
            if layer_type in file_types:
                self.filling_field(layer, info[2], info[3], info[4])
            # services
            elif layer_type in srv_types:
                # WMS, WFS, EMS or EFS
                if layer_type != "WMTS":
                    self.filling_field(layer, info[6][0], info[6][1], info[6][2])
                # WMTS
                else:
                    self.filling_field(layer, info[3][0], info[3][1], info[3][2])
            else:
                pass
        return

    def filling_field(self, layer, title, abstract, kw_list):
        layer.setTitle(title)
        layer.setAbstract(abstract)
        layer.setKeywordList(",".join(kw_list))
        logger.debug(
            "'QGIS Server' tab from 'Layer's Properties' filled with basic info"
        )
        return
