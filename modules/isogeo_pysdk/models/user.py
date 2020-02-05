# -*- coding: UTF-8 -*-
#! python3  # noqa E265

"""
    Isogeo API v1 - Model of User entity

    See: http://help.isogeo.com/api/complete/index.html#definition-user
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# standard library
import pprint

# submodels
from .contact import Contact


# #############################################################################
# ########## Classes ###############
# ##################################
class User(object):
    """Users in Isogeo platform.

    :Example:

    .. code-block:: json

        {
            "_abilities": [
                "string"
            ],
            "_created": "string (date-time)",
            "_id": "string (uuid)",
            "_modified": "string (date-time)",
            "contact": {
                "_created": "string (date-time)",
                "_id": "string (uuid)",
                "_modified": "string (date-time)",
                "addressLine1": "string",
                "addressLine2": "string",
                "addressLine3": "string",
                "available": "string",
                "city": "string",
                "count": "integer (int32)",
                "countryCode": "string",
                "email": "string",
                "fax": "string",
                "hash": "string",
                "name": "string",
                "organization": "string",
                "phone": "string",
                "type": "string",
                "zipCode": "string"
            },
            "language": "string",
            "staff": "boolean",
            "timezone": "string"
        }
    """

    ATTR_TYPES = {
        "_abilities": list,
        "_created": str,
        "_id": str,
        "_modified": str,
        "contact": Contact,
        "language": str,
        "mailchimp": dict,
        "staff": bool,
        "timezone": str,
    }

    ATTR_CREA = {
        "contact": Contact,
        "language": str,
        "mailchimp": str,
        "staff": bool,
        "timezone": str,
    }

    ATTR_MAP = {
        # "staff": "IsOgeo"
    }

    def __init__(
        self,
        _abilities: list = None,
        _created: str = None,
        _id: str = None,
        _modified: str = None,
        contact: Contact = None,
        language: str = None,
        mailchimp: dict = None,
        memberships: dict = None,
        staff: bool = None,
        timezone: str = None,
    ):
        """User model."""

        # default values for the object attributes/properties
        self.__abilities = None
        self.__created = None
        self.__id = None
        self.__modified = None
        self._contact = Contact
        self._language = None
        self._mailchimp = None
        self._memberships = None
        self._staff = None
        self._timezone = None

        # if values have been passed, so use them as objects attributes.
        # attributes are prefixed by an underscore '_'
        if _abilities is not None:
            self.__abilities = _abilities
        if _created is not None:
            self.__created = _created
        if _id is not None:
            self.__id = _id
        if _modified is not None:
            self.__modified = _modified
        if contact is not None:
            self._contact = Contact(**contact)
        if language is not None:
            self._language = language
        if mailchimp is not None:
            self._mailchimp = mailchimp
        if staff is not None:
            self._staff = staff
        if timezone is not None:
            self._timezone = timezone

    # -- PROPERTIES --------------------------------------------------------------------
    # abilities
    @property
    def _abilities(self):
        """Gets the abilities of this User.  # noqa: E501.

        :return: The abilities of this User.  # noqa: E501
        :rtype: Abilities
        """
        return self.__abilities

    # creation date
    @property
    def _created(self) -> str:
        """Gets the created used for Isogeo filters of this User.

        :return: The created of this User.
        :rtype: str
        """
        return self.__created

    # user UUID
    @property
    def _id(self) -> str:
        """Gets the id of this User.

        :return: The id of this User.
        :rtype: str
        """
        return self.__id

    # last update
    @property
    def _modified(self) -> str:
        """Gets the modified used for Isogeo filters of this User.

        :return: The modified of this User.
        :rtype: str
        """
        return self.__modified

    # contact
    @property
    def contact(self) -> Contact:
        """Gets the contact of this user.

        :return: The contact of this user.
        :rtype: Contact
        """
        return self._contact

    @contact.setter
    def contact(self, contact: Contact):
        """Sets the contact of this user.

        :param dict contact: The contact of this user.
        """

        if contact is None:
            raise ValueError("Invalid value for `contact`, must not be `None`")

        self._contact = Contact(**contact)

    # language
    @property
    def language(self) -> str:
        """Gets the id of this User.

        :return: The id of this User.
        :rtype: str
        """
        return self._language

    @language.setter
    def language(self, language: str):
        """Sets the first line of the address of this User.

        :param str language: The first address line of this User.
        """

        self._language = language

    # mailchimp subscriptions
    @property
    def mailchimp(self) -> str:
        """Gets the id of this User.

        :return: The second address line of this User.
        :rtype: str
        """
        return self._mailchimp

    @mailchimp.setter
    def mailchimp(self, mailchimp: str):
        """Sets the id of this User.

        :param str mailchimp: The second address line of this User.
        """

        self._mailchimp = mailchimp

    # staff status
    @property
    def staff(self) -> bool:
        """Staff status for the User.

        :return: the staff status of the User
        :rtype: bool
        """
        return self._staff

    @staff.setter
    def staff(self, staff: bool):
        """Sets the staff status of this User.

        :param bool staff: The new staff status for the User.
        """

        self._staff = staff

    # timezone
    @property
    def timezone(self) -> str:
        """Gets the timezone of this User.

        :return: The timezone of this User.
        :rtype: str
        """
        return self._timezone

    @timezone.setter
    def timezone(self, timezone: str):
        """Sets the timezone of this User.

        :param str timezone: The timezone of this User.
        """

        self._timezone = timezone

    # -- SPECIFIC TO IMPLEMENTATION ----------------------------------------------------
    @property
    def name(self) -> str:
        """Shortcut to get the name from the contact data linked to the user."""
        if isinstance(self._contact, dict):
            return self._contact.get("name")
        elif isinstance(self._contact, Contact):
            return self._contact.name
        else:
            return None

    @property
    def email(self) -> str:
        """Shortcut to get the email from the contact data linked to the user."""
        if isinstance(self._contact, dict):
            return self._contact.get("email")
        elif isinstance(self.contact, Contact):
            return self.contact.email
        else:
            return None

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
        if issubclass(User, dict):
            for key, value in self.items():
                result[key] = value

        return result

    def to_dict_creation(self) -> dict:
        """Returns the model properties as a dict structured for creation purpose (POST)"""
        result = {}

        for attr, _ in self.ATTR_CREA.items():
            # get attribute value
            value = getattr(self, attr)
            # switch attribute name for creation purpose
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
        if issubclass(User, dict):
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
        if not isinstance(other, User):
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
    obj = User()
    print(obj)
