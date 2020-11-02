# -*- coding: UTF-8 -*-
#! python3  # noqa E265

"""
    Isogeo API v1 - Enums for Share entity accepted types.

    See: http://help.isogeo.com/api/complete/index.html#definition-share
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# standard library
from enum import Enum, auto


# #############################################################################
# ########## Classes ###############
# ##################################
class ShareTypes(Enum):
    """Closed list of accepted session (CSW) status values in Isogeo API.

    :Example:

        >>> # parse members and values
        >>> print("{0:<30} {1:>20}".format("Enum", "Value"))
        >>> for i in ShareTypes:
        >>>     print("{0:<30} {1:>20}".format(i, i.value))
        Enum                                          Value
        ShareTypes.canceled                            1
        ShareTypes.failed                              2
        ShareTypes.started                             3
        ShareTypes.succeeded                           4

        >>> # check if a var is an accepted value
        >>> print("application" in ShareTypes.__members__)
        True
        >>> print("Group" in ShareTypes.__members__)  # case sensitive
        False
        >>> print("user" in ShareTypes.__members__)
        False

    See: https://docs.python.org/3/library/enum.html
    """

    application = auto()
    group = auto()


# ##############################################################################
# ##### Stand alone program ########
# ##################################
if __name__ == "__main__":
    """standalone execution."""
    print("{0:<30} {1:>20}".format("Enum", "Value"))
    for md_statu in ShareTypes:
        print("{0:<30} {1:>20}".format(md_statu, md_statu.value))

    print(len(ShareTypes))

    print("application" in ShareTypes.__members__)
    print("Group" in ShareTypes.__members__)
    print("user" in ShareTypes.__members__)
