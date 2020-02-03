# -*- coding: UTF-8 -*-
#! python3  # noqa E265

"""
    Isogeo API v1 - Enums for Links types

    See: http://help.isogeo.com/api/complete/index.html#definition-resourceLink
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# standard library
from enum import Enum, auto


# #############################################################################
# ########## Classes ###############
# ##################################
class LinkTypes(Enum):
    """Closed list of accepted Link types in Isogeo API.

    :Example:

        >>> # parse members and values
        >>> print("{0:<30} {1:>20}".format("Enum", "Value"))
        >>> for i in LinkTypes:
        >>>     print("{0:<30} {1:>20}".format(i, i.value))
        Enum                                          Value
        LinkTypes.hosted                                  1
        LinkTypes.link                                    2
        LinkTypes.url                                     3

        >>> # check if a var is an accepted value
        >>> print("hosted" in LinkTypes.__members__)
        True
        >>> print("Link" in LinkTypes.__members__)  # case sensitive
        False
        >>> print("external" in LinkTypes.__members__)
        False

    See: https://docs.python.org/3/library/enum.html
    """

    hosted = auto()
    link = auto()
    url = auto()


# ##############################################################################
# ##### Stand alone program ########
# ##################################
if __name__ == "__main__":
    """standalone execution."""
    print("{0:<30} {1:>20}".format("Enum", "Value"))
    for i in LinkTypes:
        print("{0:<30} {1:>20}".format(i, i.value))

    print(len(LinkTypes))

    print("hosted" in LinkTypes.__members__)
    print("Link" in LinkTypes.__members__)
    print("external" in LinkTypes.__members__)
