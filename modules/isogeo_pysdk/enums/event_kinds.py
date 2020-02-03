# -*- coding: UTF-8 -*-
#! python3  # noqa E265

"""
    Isogeo API v1 - Enums for Resource entity accepted kinds

    See: http://help.isogeo.com/api/complete/index.html#definition-resourceEvent
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# standard library
from enum import Enum, auto


# #############################################################################
# ########## Classes ###############
# ##################################
class EventKinds(Enum):
    """Closed list of accepted Event (metadata subresource) kinds in Isogeo API.

    :Example:

        >>> # parse members and values
        >>> print("{0:<30} {1:>20}".format("Enum", "Value"))
        >>> for md_kind in EventKinds:
        >>>     print("{0:<30} {1:>20}".format(md_kind, md_kind.value))
        Enum                                          Value
        EventKinds.creation                               1
        EventKinds.publication                            2
        EventKinds.update                                 3

        >>> # check if a var is an accepted value
        >>> print("creation" in EventKinds.__members__)
        True
        >>> print("Update" in EventKinds.__members__)  # case sensitive
        False
        >>> print("modification" in EventKinds.__members__)
        False

    See: https://docs.python.org/3/library/enum.html
    """

    creation = auto()
    publication = auto()
    update = auto()


# ##############################################################################
# ##### Stand alone program ########
# ##################################
if __name__ == "__main__":
    """standalone execution."""
    print("{0:<30} {1:>20}".format("Enum", "Value"))
    for md_kind in EventKinds:
        print("{0:<30} {1:>20}".format(md_kind, md_kind.value))

    print(len(EventKinds))

    print("creation" in EventKinds.__members__)
    print("Update" in EventKinds.__members__)
    print("modification" in EventKinds.__members__)
