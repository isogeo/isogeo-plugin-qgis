# -*- coding: UTF-8 -*-
#! python3  # noqa E265

"""
    Isogeo API v1 - Enums for Search geographic filter's geometric relationship
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# standard library
from enum import Enum, auto


# #############################################################################
# ########## Classes ###############
# ##################################
class SearchGeoRelations(Enum):
    """Closed list of accepted geometric relationship as search filters.

    :Example:

        >>> # parse members and values
        >>> print("{0:<30} {1:>20}".format("Enum", "Value"))
        >>> for i in SearchGeoRelations:
        >>>     print("{0:<30} {1:>20}".format(i, i.value))
        Enum                                          Value
        SearchGeoRelations.contains                       1
        SearchGeoRelations.disjoint                       2
        SearchGeoRelations.equal                          3
        SearchGeoRelations.intersects                     4
        SearchGeoRelations.overlaps                       5
        SearchGeoRelations.within                         6

        >>> # check if a var is an accepted value
        >>> print("contains" in SearchGeoRelations.__members__)
        True
        >>> print("Overlaps" in SearchGeoRelations.__members__)  # case sensitive
        False
        >>> print("crosses" in SearchGeoRelations.__members__)
        False

    See: https://docs.python.org/3/library/enum.html
    """

    contains = auto()
    disjoint = auto()
    equal = auto()
    intersects = auto()
    overlaps = auto()
    within = auto()

    @classmethod
    def has_value(cls, value):
        return any(value == item.value for item in cls)


# ##############################################################################
# ##### Stand alone program ########
# ##################################
if __name__ == "__main__":
    """standalone execution."""
    print("{0:<30} {1:>20}".format("Enum", "Value"))
    for i in SearchGeoRelations:
        print("{0:<30} {1:>20}".format(i, i.value))

    print(len(SearchGeoRelations))

    print("contains" in SearchGeoRelations.__members__)
    print("Overlaps" in SearchGeoRelations.__members__)
    print("crosses" in SearchGeoRelations.__members__)
