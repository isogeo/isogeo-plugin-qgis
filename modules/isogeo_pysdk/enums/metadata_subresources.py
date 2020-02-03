# -*- coding: UTF-8 -*-
#! python3  # noqa E265

"""
    Isogeo API v1 - Enums for Metadata subresources

    See: http://help.isogeo.com/api/complete/index.html#operation--resources--id--get
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# standard library
from enum import Enum


# #############################################################################
# ########## Classes ###############
# ##################################
class MetadataSubresources(Enum):
    """Closed list of accepted Metadata subresources that can be passed in `_include` queries
    paramater.

    :Example:

        >>> # parse members and values
        >>> print("{0:<30} {1:>20}".format("Enum", "Value"))
        >>> for i in MetadataSubresources:
        >>>     print("{0:<30} {1:>20}".format(i, i.value))
        Enum                                          Value
        MetadataSubresources.tags                                  1
        MetadataSubresources.link                                    2
        MetadataSubresources.url                                     3

        >>> # check if a var is an accepted value
        >>> print("tags" in MetadataSubresources.__members__)
        True
        >>> print("Links" in MetadataSubresources.__members__)  # case sensitive
        False
        >>> print("attributes" in MetadataSubresources.__members__)
        False

    See: https://docs.python.org/3/library/enum.html
    """

    _creator = "_creator"
    conditions = "conditions"
    contacts = "contacts"
    coordinateSystem = "coordinate-system"
    events = "events"
    featureAttributes = "feature-attributes"
    keywords = "keywords"
    layers = "layers"
    limitations = "limitations"
    links = "links"
    operations = "operations"
    serviceLayers = "serviceLayers"
    specifications = "specifications"
    tags = "tags"

    @classmethod
    def has_value(cls, value):
        return any(value == item.value for item in cls)


# ##############################################################################
# ##### Stand alone program ########
# ##################################
if __name__ == "__main__":
    """standalone execution."""
    print("{0:<30} {1:>20}".format("Enum", "Value"))
    for i in MetadataSubresources:
        print("{0:<30} {1:>20}".format(i, i.value))

    print(len(MetadataSubresources))

    print("tags" in MetadataSubresources.__members__)
    print("Links" in MetadataSubresources.__members__)
    print("attributes" in MetadataSubresources.__members__)

    values = set(item.value for item in MetadataSubresources)
    print("feature-attributes" in values)
