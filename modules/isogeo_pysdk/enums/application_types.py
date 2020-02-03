# -*- coding: UTF-8 -*-
#! python3  # noqa E265

"""
    Isogeo API v1 - Enums for Resource entity accepted kinds

    See: http://help.isogeo.com/api/complete/index.html#definition-application
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# standard library
from enum import Enum, auto


# #############################################################################
# ########## Classes ###############
# ##################################
class ApplicationTypes(Enum):
    """Closed list of accepted Application (metadata subresource) kinds in Isogeo API.

    :Example:

        >>> # parse members and values
        >>> print("{0:<30} {1:>20}".format("Enum", "Value"))
        >>> for md_kind in ApplicationTypes:
        >>>     print("{0:<30} {1:>20}".format(md_kind, md_kind.value))
        Enum                                          Value
        ApplicationTypes.group                            1
        ApplicationTypes.user                             2

        >>> # check if a var is an accepted value
        >>> print("group" in ApplicationTypes.__members__)
        True
        >>> print("User" in ApplicationTypes.__members__)  # case sensitive
        False
        >>> print("confidential" in ApplicationTypes.__members__)
        False

    See: https://docs.python.org/3/library/enum.html
    """

    group = auto()
    user = auto()


# ##############################################################################
# ##### Stand alone program ########
# ##################################
if __name__ == "__main__":
    """standalone execution."""
    print("{0:<30} {1:>20}".format("Enum", "Value"))
    for md_kind in ApplicationTypes:
        print("{0:<30} {1:>20}".format(md_kind, md_kind.value))

    print(len(ApplicationTypes))

    print("group" in ApplicationTypes.__members__)
    print("User" in ApplicationTypes.__members__)
    print("confidential" in ApplicationTypes.__members__)
