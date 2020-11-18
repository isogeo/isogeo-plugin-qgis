# -*- coding: UTF-8 -*-
#! python3  # noqa E265

"""
    Isogeo API v1 - Enums for Workgroup statistics entity accepted tags

    See: http://help.isogeo.com/api/complete/index.html#operation--groups--gid--statistics-tag--tag--get
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# standard library
from enum import Enum


# #############################################################################
# ########## Classes ###############
# ##################################
class WorkgroupStatisticsTags(Enum):
    """Closed list of accepted tags for workgroup statistics in Isogeo API (used by the dashboard).

    :Example:

        >>> # parse members and values
        >>> print("{0:<30} {1:>20}".format("Enum", "Value"))
        >>> for tag in WorkgroupStatisticsTags:
        >>>     print("{0:<30} {1:>20}".format(tag, tag.value))
        Enum                                                    Value
        WorkgroupStatisticsTags.catalog                                catalog
        WorkgroupStatisticsTags.coordinateSystem             coordinate-system
        WorkgroupStatisticsTags.format                                  format
        WorkgroupStatisticsTags.inspireTheme             keyword:inspire-theme
        WorkgroupStatisticsTags.owner                                    owner

        >>> # check if a var is an accepted value
        >>> print("catalog" in WorkgroupStatisticsTags.__members__)
        True
        >>> print("Catalog" in WorkgroupStatisticsTags.__members__)  # case sensitive
        False
        >>> print("coordinate-system" in WorkgroupStatisticsTags.__members__)
        False
        >>> print("coordinateSystem" in WorkgroupStatisticsTags.__members__)
        True

    See: https://docs.python.org/3/library/enum.html
    """

    catalog = "catalog"
    contact = "contact"
    coordinateSystem = "coordinate-system"
    format = "format"
    inspireTheme = "keyword:inspire-theme"
    keyword = "keyword"
    owner = "owner"

    @classmethod
    def has_value(cls, value):
        return any(value == item.value for item in cls)


# ##############################################################################
# ##### Stand alone program ########
# ##################################
if __name__ == "__main__":
    """standalone execution."""
    print("{0:<30} {1:>30}".format("Enum", "Value"))
    for tag in WorkgroupStatisticsTags:
        print("{0:<30} {1:>30}".format(tag, tag.value))

    print(len(WorkgroupStatisticsTags))

    print("catalog" in WorkgroupStatisticsTags.__members__)
    print("Catalog" in WorkgroupStatisticsTags.__members__)
    print("coordinate-system" in WorkgroupStatisticsTags.__members__)
    print("coordinateSystem" in WorkgroupStatisticsTags.__members__)

    values = set(item.value for item in WorkgroupStatisticsTags)
    print("feature-attributes" in values)
