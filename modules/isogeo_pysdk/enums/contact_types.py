# -*- coding: UTF-8 -*-
#! python3  # noqa E265

"""
    Isogeo API v1 - Enums for Contact entity accepted types

    See: http://help.isogeo.com/api/complete/index.html#/definitions/resourceContact
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# standard library
from enum import Enum, auto


# #############################################################################
# ########## Classes ###############
# ##################################
class ContactTypes(Enum):
    """Closed list of accepted Contact types in Isogeo API.

    :Example:

        >>> # parse members and values
        >>> print("{0:<30} {1:>20}".format("Enum", "Value"))
        >>> for i in ContactTypes:
        >>>     print("{0:<30} {1:>20}".format(i, i.value))
        Enum                                          Value
        ContactTypes.custom                               1
        ContactTypes.group                                2
        ContactTypes.user                                 3

        >>> # check if a var is an accepted value
        >>> print("group" in ContactTypes.__members__)
        True
        >>> print("Custom" in ContactTypes.__members__)  # case sensitive
        False
        >>> print("global" in ContactTypes.__members__)
        False

    See: https://docs.python.org/3/library/enum.html
    """

    custom = auto()
    group = auto()
    user = auto()


# ##############################################################################
# ##### Stand alone program ########
# ##################################
if __name__ == "__main__":
    """standalone execution."""
    print("{0:<30} {1:>20}".format("Enum", "Value"))
    for i in ContactTypes:
        print("{0:<30} {1:>20}".format(i, i.value))

    print(len(ContactTypes))

    print("group" in ContactTypes.__members__)
    print("Custom" in ContactTypes.__members__)
    print("global" in ContactTypes.__members__)
