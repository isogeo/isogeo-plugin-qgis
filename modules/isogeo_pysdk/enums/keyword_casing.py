# -*- coding: UTF-8 -*-
#! python3  # noqa E265

"""
    Isogeo API v1 - Enums for Workgroup's keywords casing

    See: http://help.isogeo.com/api/complete/index.html#definition-workgroup
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# standard library
from enum import Enum, auto


# #############################################################################
# ########## Classes ###############
# ##################################
class KeywordCasing(Enum):
    """Closed list of accepted Keyword casing in Isogeo API.

    :Example:

        >>> # parse members and values
        >>> print("{0:<30} {1:>20}".format("Enum", "Value"))
        >>> for i in KeywordCasing:
        >>>     print("{0:<30} {1:>20}".format(i, i.value))
        Enum                                          Value
        KeywordCasing.capitalized                         1
        KeywordCasing.lowercase                           2
        KeywordCasing.mixedcase                           3
        KeywordCasing.uppercase                           4

        >>> # check if a var is an accepted value
        >>> print("capitalized" in KeywordCasing.__members__)
        True
        >>> print("Uppercase" in KeywordCasing.__members__)  # case sensitive
        False
        >>> print("initials" in KeywordCasing.__members__)
        False

    See: https://docs.python.org/3/library/enum.html
    """

    capitalized = auto()
    lowercase = auto()
    mixedcase = auto()
    uppercase = auto()


# ##############################################################################
# ##### Stand alone program ########
# ##################################
if __name__ == "__main__":
    """standalone execution."""
    print("{0:<30} {1:>20}".format("Enum", "Value"))
    for i in KeywordCasing:
        print("{0:<30} {1:>20}".format(i, i.value))

    print(len(KeywordCasing))

    print("capitalized" in KeywordCasing.__members__)
    print("Uppercase" in KeywordCasing.__members__)
    print("initials" in KeywordCasing.__members__)
