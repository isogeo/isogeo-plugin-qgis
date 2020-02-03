# -*- coding: UTF-8 -*-
#! python3  # noqa E265

"""
    Isogeo API v1 - Enums for Session entity accepted status

    See: http://help.isogeo.com/api/complete/index.html#definition-session
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# standard library
from enum import Enum, auto


# #############################################################################
# ########## Classes ###############
# ##################################
class SessionStatus(Enum):
    """Closed list of accepted session (CSW) status values in Isogeo API.

    :Example:

        >>> # parse members and values
        >>> print("{0:<30} {1:>20}".format("Enum", "Value"))
        >>> for i in SessionStatus:
        >>>     print("{0:<30} {1:>20}".format(i, i.value))
        Enum                                          Value
        SessionStatus.canceled                            1
        SessionStatus.failed                              2
        SessionStatus.started                             3
        SessionStatus.succeeded                           4

        >>> # check if a var is an accepted value
        >>> print("started" in SessionStatus.__members__)
        True
        >>> print("Failed" in SessionStatus.__members__)  # case sensitive
        False
        >>> print("aborted" in SessionStatus.__members__)
        False

    See: https://docs.python.org/3/library/enum.html
    """

    canceled = auto()
    failed = auto()
    started = auto()
    succeeded = auto()


# ##############################################################################
# ##### Stand alone program ########
# ##################################
if __name__ == "__main__":
    """standalone execution."""
    print("{0:<30} {1:>20}".format("Enum", "Value"))
    for md_statu in SessionStatus:
        print("{0:<30} {1:>20}".format(md_statu, md_statu.value))

    print(len(SessionStatus))

    print("started" in SessionStatus.__members__)
    print("Failed" in SessionStatus.__members__)
    print("aborted" in SessionStatus.__members__)
