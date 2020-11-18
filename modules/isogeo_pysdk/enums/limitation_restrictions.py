# -*- coding: UTF-8 -*-
#! python3  # noqa E265

"""
    Isogeo API v1 - Enums for Limitation restrictions entity accepted values.

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
class LimitationRestrictions(Enum):
    """Closed list of accepted restrictions for limitations in Isogeo API.

    :Example:

        >>> # parse members and values
        >>> print("{0:<30} {1:>20}".format("Enum", "Value"))
        >>> for tag in LimitationRestrictions:
        >>>     print("{0:<30} {1:>20}".format(tag, tag.value))
        Enum                                                        Value
        LimitationRestrictions.copyright                            1
        LimitationRestrictions.intellectualPropertyRights           2
        LimitationRestrictions.license                              3
        LimitationRestrictions.other                                4
        LimitationRestrictions.patent                               5
        LimitationRestrictions.patentPending                        6
        LimitationRestrictions.trademark                            7

        >>> # check if a var is an accepted value
        >>> print("license" in LimitationRestrictions.__members__)
        True
        >>> print("License" in LimitationRestrictions.__members__)  # case sensitive
        False
        >>> print("other" in LimitationRestrictions.__members__)
        True

    See: https://docs.python.org/3/library/enum.html
    """

    copyright = auto()
    intellectualPropertyRights = auto()
    license = auto()
    other = auto()
    patent = auto()
    patentPending = auto()
    trademark = auto()


# ##############################################################################
# ##### Stand alone program ########
# ##################################
if __name__ == "__main__":
    """standalone execution."""
    print("{0:<30} {1:>30}".format("Enum", "Value"))
    for tag in LimitationRestrictions:
        print("{0:<30} {1:>20}".format(tag, tag.value))

    print(len(LimitationRestrictions))

    print("license" in LimitationRestrictions.__members__)
    print("License" in LimitationRestrictions.__members__)
