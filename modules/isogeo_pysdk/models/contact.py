# -*- coding: UTF-8 -*-
#! python3  # noqa E265

"""
    Isogeo API v1 - Model of Contact entity

    See: http://help.isogeo.com/api/complete/index.html#definition-contact
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# standard library
import pprint


# #############################################################################
# ########## Classes ###############
# ##################################
class Contact(object):
    """Contacts are entities used into Isogeo adress book that can be associated to metadata."""

    ATTR_TYPES = {
        "_abilities": str,
        "_id": str,
        "_tag": str,
        "addressLine1": str,
        "addressLine2": str,
        "addressLine3": str,
        "city": str,
        "count": int,
        "countryCode": str,
        "email": str,
        "fax": str,
        "hash": str,
        "name": str,
        "organization": str,
        "owner": dict,
        "phone": str,
        "type": str,
        "zipCode": str,
    }

    ATTR_CREA = {
        "addressLine1": "str",
        "addressLine2": "str",
        "addressLine3": "str",
        "city": "str",
        "countryCode": "str",
        "email": "str",
        "fax": "str",
        "name": "str",
        "organization": "str",
        "phone": "str",
        "zipCode": "str",
    }

    ATTR_MAP = {
        "fax": "faxNumber",
        "organization": "organizationName",
        "phone": "phoneNumber",
    }

    def __init__(
        self,
        _abilities: list = None,
        _deleted: bool = None,
        _id: str = None,
        _tag: str = None,
        addressLine1: str = None,
        addressLine2: str = None,
        addressLine3: str = None,
        available: bool = None,
        city: str = None,
        count: int = None,
        countryCode: str = None,
        email: str = None,
        fax: str = None,
        hash: str = None,
        name: str = None,
        organization: str = None,
        owner: dict = None,
        phone: str = None,
        type: str = None,
        zipCode: str = None,
        # auto-generated or deprecated
        created=None,
        modified=None,
    ):
        """Contact model."""

        # default values for the object attributes/properties
        self.__abilities = None
        self.__id = None
        self.__tag = None
        self._addressLine1 = None
        self._addressLine2 = None
        self._addressLine3 = None
        self._available = None
        self._city = None
        self._count = None
        self._countryCode = None
        self._email = None
        self._fax = None
        self._hash = None
        self._name = None
        self._organization = None
        self._owner = None
        self._phone = None
        self._type = None
        self._zipCode = None
        self._hash = None
        self._created = None
        self._modified = None

        # if values have been passed, so use them as objects attributes.
        # attributes are prefixed by an underscore '_'
        if _abilities is not None:
            self.__abilities = _abilities
        if _deleted is not None:
            self._deleted = _deleted
        if _id is not None:
            self.__id = _id
        if _tag is not None:
            self.__tag = _tag
        if addressLine1 is not None:
            self._addressLine1 = addressLine1
        if addressLine2 is not None:
            self._addressLine2 = addressLine2
        if addressLine3 is not None:
            self._addressLine3 = addressLine3
        if available is not None:
            self._available = available
        if city is not None:
            self._city = city
        if count is not None:
            self._count = count
        if countryCode is not None:
            self._countryCode = countryCode
        if email is not None:
            self._email = email
        if fax is not None:
            self._fax = fax
        if hash is not None:
            self._hash = hash
        if name is not None:
            self._name = name
        if organization is not None:
            self._organization = organization
        if owner is not None:
            self._owner = owner
        if phone is not None:
            self._phone = phone
        if type is not None:
            self._type = type
        if zipCode is not None:
            self._zipCode = zipCode
        # auto-generated or deprecated
        if created is not None:
            self._created = created
        if modified is not None:
            self._modified = modified

    # -- PROPERTIES --------------------------------------------------------------------
    # abilities of the user related to the metadata
    @property
    def _abilities(self) -> str:
        """Gets the abilities of this Catalog.

        :return: The abilities of this Catalog.
        :rtype: str
        """
        return self.__abilities

    # contact UUID
    @property
    def _id(self) -> str:
        """Gets the id of this Contact.

        :return: The id of this Contact.
        :rtype: str
        """
        return self.__id

    # contact search tag
    @property
    def _tag(self) -> str:
        """Gets the tag used for Isogeo filters of this Contact.

        :return: The tag of this Contact.
        :rtype: str
        """
        return self.__tag

    # adress first line
    @property
    def addressLine1(self) -> str:
        """Gets the id of this Contact.

        :return: The id of this Contact.
        :rtype: str
        """
        return self._addressLine1

    @addressLine1.setter
    def addressLine1(self, addressLine1: str):
        """Sets the first line of the address of this Contact.

        :param str addressLine1: The first address line of this Contact.
        """

        self._addressLine1 = addressLine1

    # adress second line
    @property
    def addressLine2(self) -> str:
        """Gets the id of this Contact.

        :return: The second address line of this Contact.
        :rtype: str
        """
        return self._addressLine2

    @addressLine2.setter
    def addressLine2(self, addressLine2: str):
        """Sets the id of this Contact.

        :param str addressLine2: The second address line of this Contact.
        """

        self._addressLine2 = addressLine2

    # adress third line
    @property
    def addressLine3(self) -> str:
        """Gets the third address line of this Contact.

        :return: The The third address line of this Contact.
        :rtype: str
        """
        return self._addressLine3

    @addressLine3.setter
    def addressLine3(self, addressLine3: str):
        """Sets the third address line of this Contact.

        :param str addressLine3: The The third address line of this Contact.
        """

        self._addressLine3 = addressLine3

    # available
    @property
    def available(self) -> bool:
        """Gets the availibility of this Contact.

        :return: The availibility of this Contact.
        :rtype: str
        """
        return self._available

    @available.setter
    def available(self, available: bool):
        """Sets the availability of this Contact for edition actions.

        :param str available: The availability of this Contact.
        """

        self._available = available

    # city
    @property
    def city(self) -> str:
        """Gets the city of this Contact.

        :return: The city of this Contact.
        :rtype: str
        """
        return self._city

    @city.setter
    def city(self, city: str):
        """Sets the city of this Contact.

        :param str city: The city of this Contact.
        """

        self._city = city

    # count of resource linked to the contact
    @property
    def count(self) -> int:
        """Gets the id of this Contact.

        :return: The id of this Contact.
        :rtype: str
        """
        return self._count

    @count.setter
    def count(self, count: int):
        """Sets the count of this Contact.

        :param int count: count of associated resources to the Contact
        """

        self._count = count

    # country code
    @property
    def countryCode(self) -> str:
        """Gets the country code of this Contact.

        :return: The country code of this Contact.
        :rtype: str
        """
        return self._countryCode

    @countryCode.setter
    def countryCode(self, countryCode: str):
        """Sets the country code of this Contact.

        :param str countryCode: The country code of this Contact.
        """

        self._countryCode = countryCode

    # email
    @property
    def email(self) -> str:
        """Gets the email of this Contact.

        :return: The email of this Contact.
        :rtype: str
        """
        return self._email

    @email.setter
    def email(self, email: str):
        """Sets the email of this Contact.

        :param str email: The id of this Contact.
        """

        self._email = email

    # fax number
    @property
    def fax(self) -> str:
        """Gets the fax of this Contact.

        :return: The fax of this Contact.
        :rtype: str
        """
        return self._fax

    @fax.setter
    def fax(self, fax: str):
        """Sets the fax of this Contact.

        :param str XX: The fax of this Contact.
        """

        self._fax = fax

    # hash
    @property
    def hash(self) -> str:
        """Gets the hash of this Contact.

        :return: The hash of this Contact.
        :rtype: str
        """
        return self._hash

    @hash.setter
    def hash(self, hash: str):
        """Sets the hash of this Contact.

        :param str XX: The hash of this Contact.
        """

        self._hash = hash

    # name
    @property
    def name(self) -> str:
        """Gets the name of this Contact.

        :return: The name of this Contact.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name: str):
        """Sets the name of this Contact.

        :param str name: The name of this Contact.
        """

        self._name = name

    # organization
    @property
    def organization(self) -> str:
        """Gets the organization of this Contact.

        :return: The organization of this Contact.
        :rtype: str
        """
        return self._organization

    @organization.setter
    def organization(self, organization: str):
        """Sets the organization of this Contact.

        :param str organization: The organization of this Contact.
        """

        self._organization = organization

    # workgroup owner
    @property
    def owner(self):
        """Gets the owner of this Specification.

        :return: The owner of this Specification.
        :rtype: Workgroup
        """
        return self._owner

    # phone
    @property
    def phone(self) -> str:
        """Gets the phone number of this Contact.

        :return: The phone number of this Contact.
        :rtype: str
        """
        return self._phone

    @phone.setter
    def phone(self, phone: str):
        """Sets the phone number of this Contact.

        :param str phone: The phone number of this Contact.
        """

        self._phone = phone

    # type
    @property
    def type(self) -> str:
        """Gets the type of this Contact.

        :return: The type of this Contact.
        :rtype: str
        """
        return self._type

    @type.setter
    def type(self, type: str):
        """Sets the type of this Contact.

        :param str type: The type of this Contact.
        """

        self._type = type

    # zipCode
    @property
    def zipCode(self) -> str:
        """Gets the zip (postal) code of this Contact.

        :return: The zip (postal) code of this Contact.
        :rtype: str
        """
        return self._zipCode

    @zipCode.setter
    def zipCode(self, zipCode: str):
        """Sets the zip (postal) code of this Contact.

        :param str zipCode: The zip (postal) code of this Contact.
        """

        self._zipCode = zipCode

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
        if issubclass(Contact, dict):
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
        if issubclass(Contact, dict):
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
        if not isinstance(other, Contact):
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
    ct = Contact()
