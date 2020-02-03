# -*- coding: UTF-8 -*-
#! python3  # noqa E265

"""
    Isogeo API v1 - Enums for Limitation types entity accepted values.

    See: http://help.isogeo.com/api/complete/index.html
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# standard library
from enum import auto, Enum


# #############################################################################
# ########## Classes ###############
# ##################################
class LimitationTypes(Enum):
    """Closed list of accepted types for limitations in Isogeo API.

    :Example:

        >>> # parse members and values
        >>> print("{0:<30} {1:>20}".format("Enum", "Value"))
        >>> for tag in LimitationTypes:
        >>>     print("{0:<30} {1:>20}".format(tag, tag.value))
        Enum                                                    Value
        LimitationTypes.legal                                   1
        LimitationTypes.security                                2

        >>> # check if a var is an accepted value
        >>> print("legal" in LimitationTypes.__members__)
        True
        >>> print("Legal" in LimitationTypes.__members__)  # case sensitive
        False
        >>> print("security" in LimitationTypes.__members__)
        True

    See: https://docs.python.org/3/library/enum.html
    """

    legal = auto()
    security = auto()


# ##############################################################################
# ##### Stand alone program ########
# ##################################
if __name__ == "__main__":
    """standalone execution."""
    print("{0:<30} {1:>30}".format("Enum", "Value"))
    for tag in LimitationTypes:
        print("{0:<30} {1:>30}".format(tag, tag.value))

    print(len(LimitationTypes))

    print("legal" in LimitationTypes.__members__)
    print("Legal" in LimitationTypes.__members__)
    print("coordinateSystem" in LimitationTypes.__members__)
