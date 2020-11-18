# -*- coding: UTF-8 -*-
#! python3  # noqa E265

"""
    Isogeo API v1 - Enums for Links actions

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
class LinkActions(Enum):
    """Closed list of accepted Link actions in Isogeo API.

    :Example:

        >>> # parse members and values
        >>> print("{0:<30} {1:>20}".format("Enum", "Value"))
        >>> for i in LinkActions:
        >>>     print("{0:<30} {1:>20}".format(i, i.value))
        Enum                                          Value
        LinkActions.download                              1
        LinkActions.other                                 2
        LinkActions.view                                  3

        >>> # check if a var is an accepted value
        >>> print("download" in LinkActions.__members__)
        True
        >>> print("Other" in LinkActions.__members__)  # case sensitive
        False
        >>> print("extract" in LinkActions.__members__)
        False

    See: https://docs.python.org/3/library/enum.html
    """

    download = auto()
    other = auto()
    view = auto()


# ##############################################################################
# ##### Stand alone program ########
# ##################################
if __name__ == "__main__":
    """standalone execution."""
    print("{0:<30} {1:>20}".format("Enum", "Value"))
    for i in LinkActions:
        print("{0:<30} {1:>20}".format(i, i.value))

    print(len(LinkActions))

    print("download" in LinkActions.__members__)
    print("Other" in LinkActions.__members__)
    print("extract" in LinkActions.__members__)
