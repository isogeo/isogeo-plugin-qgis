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
class BulkActions(Enum):
    """Closed list of accepted Application (metadata subresource) kinds in Isogeo API.

    :Example:

        >>> # parse members and values
        >>> print("{0:<30} {1:>20}".format("Enum", "Value"))
        >>> for md_kind in BulkActions:
        >>>     print("{0:<30} {1:>20}".format(md_kind, md_kind.value))
        Enum                                          Value
        BulkActions.add                                   1
        BulkActions.delete                                2
        BulkActions.update                                3

        >>> # check if a var is an accepted value
        >>> print("add" in BulkActions.__members__)
        True
        >>> print("Delete" in BulkActions.__members__)  # case sensitive
        False
        >>> print("truncate" in BulkActions.__members__)
        False

    See: https://docs.python.org/3/library/enum.html
    """

    add = auto()
    delete = auto()
    update = auto()


# ##############################################################################
# ##### Stand alone program ########
# ##################################
if __name__ == "__main__":
    """standalone execution."""
    print("{0:<30} {1:>20}".format("Enum", "Value"))
    for md_kind in BulkActions:
        print("{0:<30} {1:>20}".format(md_kind, md_kind.value))

    print(len(BulkActions))

    print("add" in BulkActions.__members__)
    print("Delete" in BulkActions.__members__)
    print("truncate" in BulkActions.__members__)
