# -*- coding: UTF-8 -*-
#! python3  # noqa E265

"""
    Isogeo API v1 - Enums for Resource entity accepted types

    See: http://help.isogeo.com/api/complete/index.html#/definitions/resourceMetadata
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# standard library
from enum import Enum


# #############################################################################
# ########## Classes ###############
# ##################################
class MetadataTypes(Enum):
    """Closed list of accepted Metadata (= Resource) types in Isogeo API.

    :Example:

        >>> # parse members and values
        >>> print("{0:<30} {1:>20}".format("Enum", "Value"))
        >>> for md_type in MetadataTypes:
        >>>     print("{0:<30} {1:>20}".format(md_type, md_type.value))
        Enum                                          Value
        MetadataTypes.rasterDataset          raster-dataset
        MetadataTypes.resource                     resource
        MetadataTypes.service                       service
        MetadataTypes.vectorDataset          vector-dataset

        >>> # check if a var is an accepted value
        >>> print("rasterDataset" in MetadataTypes.__members__)
        True
        >>> print("Service" in MetadataTypes.__members__)  # case sensitive
        False
        >>> print("dataset" in MetadataTypes.__members__)
        False

    See: https://docs.python.org/3/library/enum.html
    """

    dataset = "dataset"
    rasterDataset = "raster-dataset"
    resource = "resource"
    service = "service"
    vectorDataset = "vector-dataset"

    @classmethod
    def has_value(cls, value):
        return any(value == item.value for item in cls)


# ##############################################################################
# ##### Stand alone program ########
# ##################################
if __name__ == "__main__":
    """standalone execution."""
    print("{0:<30} {1:>20}".format("Enum", "Value"))
    for md_type in MetadataTypes:
        print("{0:<30} {1:>20}".format(md_type, md_type.value))

    print(len(MetadataTypes))

    print("rasterDataset" in MetadataTypes.__members__)
    print("Service" in MetadataTypes.__members__)
    print("dataset" in MetadataTypes.__members__)
