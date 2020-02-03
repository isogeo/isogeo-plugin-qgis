# -*- coding: UTF-8 -*-
#! python3  # noqa E265

"""
    Isogeo API v1 - Enums for Links kinds

    See: http://help.isogeo.com/api/complete/index.html#definition-resourceLink
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# standard library
from enum import Enum, auto


# #############################################################################
# ########## Classes ###############
# ##################################
class LinkKinds(Enum):
    """Closed list of accepted Link kinds in Isogeo API.

    :Example:

        >>> # parse members and values
        >>> print("{0:<30} {1:>20}".format("Enum", "Value"))
        >>> for i in LinkKinds:
        >>>     print("{0:<30} {1:>20}".format(i, i.value))
        Enum                                          Value
        LinkKinds.data                                    1
        LinkKinds.esriFeatureService                      2
        LinkKinds.esriMapService                          3
        LinkKinds.esriTileService                         4
        LinkKinds.url                                     5
        LinkKinds.wfs                                     6
        LinkKinds.wms                                     7
        LinkKinds.wmts                                    8

        >>> # check if a var is an accepted value
        >>> print("data" in LinkKinds.__members__)
        True
        >>> print("EsriFeatureService" in LinkKinds.__members__)  # case sensitive
        False
        >>> print("csw" in LinkKinds.__members__)
        False

    See: https://docs.python.org/3/library/enum.html
    """

    data = auto()
    esriFeatureService = auto()
    esriMapService = auto()
    esriTileService = auto()
    url = auto()
    wfs = auto()
    wms = auto()
    wmts = auto()


# ##############################################################################
# ##### Stand alone program ########
# ##################################
if __name__ == "__main__":
    """standalone execution."""
    print("{0:<30} {1:>20}".format("Enum", "Value"))
    for i in LinkKinds:
        print("{0:<30} {1:>20}".format(i, i.value))

    print(len(LinkKinds))

    print("wms" in LinkKinds.__members__)
    print("EsriFeatureService" in LinkKinds.__members__)
    print("csw" in LinkKinds.__members__)
