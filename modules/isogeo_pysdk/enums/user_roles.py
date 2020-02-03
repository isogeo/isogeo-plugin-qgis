# -*- coding: UTF-8 -*-
#! python3  # noqa E265

"""
    Isogeo API v1 - Enums for ResourceContact entity accepted roles

    See: http://help.isogeo.com/api/complete/index.html#definition-user
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# standard library
from enum import Enum


# #############################################################################
# ########## Classes ###############
# ##################################
class UserRoles(Enum):
    """Closed list of accepted Contact roles in Isogeo API.

    :Example:

        >>> # parse members and values
        >>> print("{0:<30} {1:>20}".format("Enum", "Value"))
        >>> for role in UserRoles:
        >>>     print("{0:<30} {1:>20}".format(role, role.value))
        Enum                                          Value
        UserRoles.admin                          admin
        UserRoles.writer          writer
        ...

        >>> # check if a var is an accepted value
        >>> print("admin" in UserRoles.__members__)
        True
        >>> print("Author" in UserRoles.__members__)  # case sensitive
        False
        >>> print("follower" in UserRoles.__members__)
        False

    See: https://docs.python.org/3/library/enum.html
    """

    admin = "admin"
    writer = "writer"
    reader = "reader"


# ##############################################################################
# ##### Stand alone program ########
# ##################################
if __name__ == "__main__":
    """standalone execution."""
    print("{0:<30} {1:>20}".format("Enum", "Value"))
    for role in UserRoles:
        print("{0:<30} {1:>20}".format(role, role.value))

    print(len(UserRoles))

    print("admin" in UserRoles.__members__)
    print("Author" in UserRoles.__members__)
    print("follower" in UserRoles.__members__)
