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
from enum import Enum, auto


# #############################################################################
# ########## Classes ###############
# ##################################
class EditionProfiles(Enum):
    """Closed list of accepted edition profiles values in Isogeo API.

    :Example:

        >>> # parse members and values
        >>> print("{0:<30} {1:>20}".format("Enum", "Value"))
        >>> for i in EditionProfiles:
        >>>     print("{0:<30} {1:>20}".format(i, i.value))
        Enum                                          Value
        EditionProfiles.csw                               1
        EditionProfiles.manual                            2

        >>> # check if a var is an accepted value
        >>> print("rasterDataset" in EditionProfiles.__members__)
        True
        >>> print("Service" in EditionProfiles.__members__)  # case sensitive
        False
        >>> print("dataset" in EditionProfiles.__members__)
        False

    See: https://docs.python.org/3/library/enum.html
    """

    csw = auto()
    manual = auto()


# ##############################################################################
# ##### Stand alone program ########
# ##################################
if __name__ == "__main__":
    """standalone execution."""
    print("{0:<30} {1:>20}".format("Enum", "Value"))
    for md_type in EditionProfiles:
        print("{0:<30} {1:>20}".format(md_type, md_type.value))

    print(len(EditionProfiles))

    print("csw" in EditionProfiles.__members__)
    print("Manual" in EditionProfiles.__members__)
    print("scan" in EditionProfiles.__members__)
