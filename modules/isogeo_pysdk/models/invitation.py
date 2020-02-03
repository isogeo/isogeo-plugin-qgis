# -*- coding: UTF-8 -*-
#! python3  # noqa E265

"""
    Isogeo API v1 - Model of Invitation entity

    See: http://help.isogeo.com/api/complete/index.html#definition-invitation
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# standard library
import pprint

# others models
from isogeo_pysdk.models.workgroup import Workgroup


# #############################################################################
# ########## Classes ###############
# ##################################
class Invitation(object):
    """Invitations are CSW client entry-points.

    :Example:

    .. code-block:: json

        {
            "_id": "6c7c9e0c63a943f79ba1e00766d0082d",
            "_created": "2019-07-25T09:23:37.0975771+00:00",
            "_modified": "2019-07-25T09:23:37.0975771+00:00",
            "role": "admin",
            "email": "prenom.nom@organisation.code",
            "expiresIn": 657364,
            "group": {
                "_id": "string (uuid)",
                "_tag": "owner:string (uuid)",
                "_created": "2019-05-07T15:11:08.5202923+00:00",
                "_modified": "2019-07-25T09:13:29.7858081+00:00",
                "contact": {
                    "_id": "string (uuid)",
                    "_tag": "contact:group:string (uuid)",
                    "_deleted": false,
                    "type": "group",
                    "group": "Isogeo TEST",
                    "available": false
                },
                "canCreateMetadata": true,
                "canCreateLegacyServiceLinks": false,
                "areKeywordsRestricted": false,
                "hasCswClient": false,
                "hasScanFme": false,
                "keywordsCasing": "lowercase"
            }
    """

    ATTR_TYPES = {
        "_created": str,
        "_id": str,
        "_modified": str,
        "email": str,
        "expiresIn": int,
        "group": Workgroup,
        "role": str,
    }

    ATTR_CREA = {"email": str, "role": str, "group": str}

    ATTR_MAP = {}

    def __init__(
        self,
        _created: str = None,
        _id: str = None,
        _modified: str = None,
        email: dict = None,
        expiresIn: str = None,
        group: str = None,
        role: bool = None,
    ):
        """Invitation model."""

        # default values for the object attributes/properties
        self.__created = None
        self.__id = None
        self.__modified = None
        self._email = None
        self._expiresIn = None
        self._group = None
        self._role = None

        # if values have been passed, so use them as objects attributes.
        # attributes are prefixed by an underscore '_'
        if _created is not None:
            self.__created = _created
        if _id is not None:
            self.__id = _id
        if _modified is not None:
            self.__modified = _modified
        if email is not None:
            self._email = email
        if expiresIn is not None:
            self._expiresIn = expiresIn
        if group is not None:
            self._group = group
        if role is not None:
            self._role = role

    # -- PROPERTIES --------------------------------------------------------------------
    # created of the user related to the metadata
    @property
    def _created(self) -> str:
        """Gets the created of this Invitation.

        :return: The created of this Invitation.
        :rtype: str
        """
        return self.__created

    # invitation UUID
    @property
    def _id(self) -> str:
        """Gets the id of this Invitation.

        :return: The id of this Invitation.
        :rtype: str
        """
        return self.__id

    # _modified
    @property
    def _modified(self) -> str:
        """Gets the _modified of this Invitation.

        :return: The _modified of this Invitation.
        :rtype: str
        """
        return self.__modified

    # role of resource expiresIned to the invitation
    @property
    def role(self) -> bool:
        """Gets the role of this Invitation.

        :return: The role of this Invitation.
        :rtype: str
        """
        return self._role

    @role.setter
    def role(self, role: bool):
        """Sets the role of this Invitation.

        :param bool role: role of associated resources to the Invitation
        """

        self._role = role

    # email
    @property
    def email(self) -> str:
        """Gets the email of this Invitation.

        :return: The email of this Invitation.
        :rtype: str
        """
        return self._email

    # email
    @email.setter
    def email(self) -> str:
        """Sets the email of this Invitation.

        :return: The email of this Invitation.
        :rtype: str
        """
        return self._email

    # expiresIn
    @property
    def expiresIn(self) -> int:
        """Gets the expiresIn of this Invitation.

        :return: The expiresIn of this Invitation.
        :rtype: int
        """
        return self._expiresIn

    @expiresIn.setter
    def expiresIn(self, expiresIn: int):
        """Sets the id of this Invitation.

        :param int expiresIn: The id of this Invitation.
        """

        self._expiresIn = expiresIn

    # group
    @property
    def group(self) -> Workgroup:
        """Gets the group of this Invitation.

        :return: The group of this Invitation.
        :rtype: Workgroup
        """
        return self._group

    @group.setter
    def group(self, group: Workgroup):
        """Sets the group of this Invitation.

        :param Workgroup group: The group of this Invitation. Accept markdown syntax.
        """

        self._group = group

    # -- METHODS -----------------------------------------------------------------------
    def to_dict(self) -> dict:
        """Returns the model properties as a dict."""
        result = {}

        for attr, _ in self.ATTR_TYPES.items():
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(
                    map(lambda x: x.to_dict() if hasattr(x, "to_dict") else x, value)
                )
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(
                    map(
                        lambda item: (item[0], item[1].to_dict())
                        if hasattr(item[1], "to_dict")
                        else item,
                        value.items(),
                    )
                )
            else:
                result[attr] = value
        if issubclass(Invitation, dict):
            for key, value in self.items():
                result[key] = value

        return result

    def to_dict_creation(self) -> dict:
        """Returns the model properties as a dict structured for creation purpose (POST)"""
        result = {}

        for attr, _ in self.ATTR_CREA.items():
            # get attribute value
            value = getattr(self, attr)
            # switch attribute group for creation purpose
            if attr in self.ATTR_MAP:
                attr = self.ATTR_MAP.get(attr)
            if isinstance(value, list):
                result[attr] = list(
                    map(lambda x: x.to_dict() if hasattr(x, "to_dict") else x, value)
                )
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(
                    map(
                        lambda item: (item[0], item[1].to_dict())
                        if hasattr(item[1], "to_dict")
                        else item,
                        value.items(),
                    )
                )
            else:
                result[attr] = value
        if issubclass(Invitation, dict):
            for key, value in self.items():
                result[key] = value

        return result

    def to_str(self) -> str:
        """Returns the string representation of the model."""
        return pprint.pformat(self.to_dict())

    def __repr__(self) -> str:
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other) -> bool:
        """Returns true if both objects are equal."""
        if not isinstance(other, Invitation):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other) -> bool:
        """Returns true if both objects are not equal."""
        return not self == other


# ##############################################################################
# ##### Stand alone program ########
# ##################################
if __name__ == "__main__":
    """standalone execution."""
    atasource = Invitation(
        group="Invitation Test", _modified="Test invitation _modified"
    )
    print(atasource)
