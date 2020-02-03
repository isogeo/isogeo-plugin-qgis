# -*- coding: UTF-8 -*-
#! python3  # noqa E265

"""
    Isogeo API v1 - Enums for ResourceContact entity accepted roles

    See: http://help.isogeo.com/api/complete/index.html#/definitions/resourceContact
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# standard library
from enum import Enum


# #############################################################################
# ########## Classes ###############
# ##################################
class ContactRoles(Enum):
    """Closed list of accepted Contact roles in Isogeo API.

    :Example:

        >>> # parse members and values
        >>> print("{0:<30} {1:>20}".format("Enum", "Value"))
        >>> for role in ContactRoles:
        >>>     print("{0:<30} {1:>20}".format(role, role.value))
        Enum                                          Value
        ContactRoles.author                          author
        ContactRoles.pointOfContact          pointOfContact
        ...

        >>> # check if a var is an accepted value
        >>> print("author" in ContactRoles.__members__)
        True
        >>> print("Author" in ContactRoles.__members__)  # case sensitive
        False
        >>> print("follower" in ContactRoles.__members__)
        False

    See: https://docs.python.org/3/library/enum.html
    """

    author = "author"
    pointOfContact = "pointOfContact"
    custodian = "custodian"
    distributor = "distributor"
    originator = "originator"
    owner = "owner"
    principalInvestigator = "principalInvestigator"
    processor = "processor"
    publisher = "publisher"
    resourceProvider = "resourceProvider"
    user = "user"


# ##############################################################################
# ##### Stand alone program ########
# ##################################
if __name__ == "__main__":
    """standalone execution."""
    print("{0:<30} {1:>20}".format("Enum", "Value"))
    for role in ContactRoles:
        print("{0:<30} {1:>20}".format(role, role.value))

    print(len(ContactRoles))

    print("author" in ContactRoles.__members__)
    print("Author" in ContactRoles.__members__)
    print("follower" in ContactRoles.__members__)
