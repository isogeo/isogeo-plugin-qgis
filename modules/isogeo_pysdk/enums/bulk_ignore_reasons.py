# -*- coding: UTF-8 -*-
#! python3  # noqa E265

"""
    Isogeo API v1 - Enums for bulk ignore reasons

"""

# #############################################################################
# ########## Libraries #############
# ##################################

# standard library
from enum import Enum, auto


# #############################################################################
# ########## Classes ###############
# ##################################
class BulkIgnoreReasons(Enum):
    """Closed list of accepted Application (metadata subresource) kinds in Isogeo API.

    :Example:

        >>> # parse members and values
        >>> print("{0:<30} {1:>20}".format("Enum", "Value"))
        >>> for md_kind in BulkIgnoreReasons:
        >>>     print("{0:<30} {1:>20}".format(md_kind, md_kind.value))
        Enum                                          Value
        BulkIgnoreReasons.AlreadyPresent                  1
        BulkIgnoreReasons.Forbidden                       2
        BulkIgnoreReasons.Invalid                         3
        BulkIgnoreReasons.NotApplicable                   4
        BulkIgnoreReasons.NotFound                        5

        >>> # check if a var is an accepted value
        >>> print("alreadyPresent" in BulkIgnoreReasons.__members__)
        True
        >>> print("NotValid" in BulkIgnoreReasons.__members__)  # case sensitive
        False
        >>> print("NotExists" in BulkIgnoreReasons.__members__)
        False

    See: https://docs.python.org/3/library/enum.html
    """

    alreadyPresent = auto()
    forbidden = auto()
    invalid = auto()
    notApplicable = auto()
    notFound = auto()


# ##############################################################################
# ##### Stand alone program ########
# ##################################
if __name__ == "__main__":
    """standalone execution."""
    print("{0:<30} {1:>20}".format("Enum", "Value"))
    for md_kind in BulkIgnoreReasons:
        print("{0:<30} {1:>20}".format(md_kind, md_kind.value))

    print(len(BulkIgnoreReasons))

    print("alreadyPresent" in BulkIgnoreReasons.__members__)
    print("NotValid" in BulkIgnoreReasons.__members__)
    print("NotExists" in BulkIgnoreReasons.__members__)
