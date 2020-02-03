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
class BulkTargets(Enum):
    """Closed list of accepted Application (metadata subresource) kinds in Isogeo API.

    :Example:

        >>> # parse members and values
        >>> print("{0:<30} {1:>20}".format("Enum", "Value"))
        >>> for md_kind in BulkTargets:
        >>>     print("{0:<30} {1:>20}".format(md_kind, md_kind.value))
        Enum                                          Value
        BulkTargets.title                                   1
        BulkTargets.abstract                                2
        BulkTargets.keywords                                3

        >>> # check if a var is an accepted value
        >>> print("title" in BulkTargets.__members__)
        True
        >>> print("Delete" in BulkTargets.__members__)  # case sensitive
        False
        >>> print("truncate" in BulkTargets.__members__)
        False

    See: https://docs.python.org/3/library/enum.html
    """

    # model: resource
    title = auto()
    abstract = auto()
    keywords = auto()
    catalogs = auto()
    contacts = auto()

    # model: dataset
    collectionContext = auto()
    collectionMethod = auto()
    validFrom = auto()
    validityComment = auto()
    distance = auto()
    scale = auto()
    codePage = auto()


# ##############################################################################
# ##### Stand alone program ########
# ##################################
if __name__ == "__main__":
    """standalone execution."""
    print("{0:<30} {1:>20}".format("Enum", "Value"))
    for md_kind in BulkTargets:
        print("{0:<30} {1:>20}".format(md_kind, md_kind.value))

    print(len(BulkTargets))

    print("title" in BulkTargets.__members__)
    print("Delete" in BulkTargets.__members__)
    print("truncate" in BulkTargets.__members__)
