# -*- coding: UTF-8 -*-
#! python3  # noqa E265

"""
    Isogeo API v1 - Model of Workgroup entity

    See: http://help.isogeo.com/api/complete/index.html#definition-workgroup
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
class Workgroup(object):
    """Workgroups are entities containing metadata.

    :Example:

    .. code-block:: json

        {
            '_abilities': [
                'group:manage',
                'group:update'
            ],
            '_created': '2015-05-21T12:08:16.4295098+00:00',
            '_id': '32f7e95ec4e94ca3bc1afda960003882',
            '_modified': '2018-12-27T10:47:28.7880956+00:00',
            '_tag': 'owner:32f7e95ec4e94ca3bc1afda960003882',
            'areKeywordsRestricted': False,
            'canCreateLegacyServiceLinks': True,
            'canCreateMetadata': True,
            'contact': {
                '_deleted': False,
                '_id': '2a3aefc4f80347f590afe58127f6cb0f',
                '_tag': 'contact:group:2a3aefc4f80347f590afe58127f6cb0f',
                'addressLine1': '26 rue du faubourg Saint-Antoine',
                'addressLine2': '4éme étage',
                'addressLine3': 'bouton porte',
                'available': False,
                'city': 'Paris',
                'countryCode': 'FR',
                'email': 'dev@isogeo.com',
                'fax': '33 (0)9 67 46 50 06',
                'name': 'Isogeo Test',
                'phone': '33 (0)9 67 46 50 06',
                'type': 'group',
                'zipCode': '75012'
            },
            'hasCswClient': True,
            'hasScanFme': True,
            'keywordsCasing': 'lowercase',
            'limits': {
                'canDiffuse': False,
                'canShare': True,
                'Workgroups': {
                    'current': 1,
                    'max': -1
                },
                'resources': {
                    'current': 2,
                    'max': 20
                },
                'upload': {
                    'current': 0,
                    'max': 1073741824
                },
                'users': {
                    'current': 1,
                    'max': 2}
                },
            'metadataLanguage': 'fr',
            'themeColor': '#4499A1'
        }
    """

    ATTR_TYPES = {
        "_abilities": list,
        "_created": str,
        "_id": str,
        "_modified": str,
        "_tag": str,
        "areKeywordsRestricted": bool,
        "canCreateLegacyServiceLinks": bool,
        "canCreateMetadata": bool,
        "code": str,
        "contact": Contact,
        "hasCswClient": bool,
        "limits": dict,
        "keywordsCasing": str,
        "metadataLanguage": str,
        "themeColor": str,
    }

    ATTR_CREA = {
        "contact": Contact,
        "metadataLanguage": str,
        "canCreateLegacyServiceLinks": bool,
        "canCreateMetadata": bool,
    }

    ATTR_MAP = {
        "contact": [
            "contact.addressLine1",
            "contact.addressLine2",
            "contact.addressLine3",
            "contact.city",
            "contact.countryCode",
            "contact.email",
            "contact.fax",
            "contact.name",
            "contact.phone",
            "contact.zipCode",
        ]
    }

    def __init__(
        self,
        _abilities: list = None,
        _created: str = None,
        _id: str = None,
        _modified: str = None,
        _tag: str = None,
        areKeywordsRestricted: bool = None,
        canCreateLegacyServiceLinks: bool = None,
        canCreateMetadata: bool = None,
        code: str = None,
        contact: Contact = None,
        hasCswClient: bool = None,
        hasScanFme: bool = None,
        keywordsCasing: str = None,
        limits: dict = None,
        metadataLanguage: str = None,
        themeColor: str = None,
    ):
        """Workgroup model."""

        # default values for the object attributes/properties
        self.__abilities = None
        self.__created = None
        self.__id = None
        self.__modified = None
        self.__tag = None
        self._areKeywordsRestricted = None
        self._canCreateLegacyServiceLinks = None
        self._canCreateMetadata = None
        self._code = code
        self._contact = Contact
        self._hasCswClient = None
        self._keywordsCasing = None
        self._limits = None
        self._metadataLanguage = None
        self._themeColor = None

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
        if areKeywordsRestricted is not None:
            self._areKeywordsRestricted = areKeywordsRestricted
        if canCreateLegacyServiceLinks is not None:
            self._canCreateLegacyServiceLinks = canCreateLegacyServiceLinks
        if canCreateMetadata is not None:
            self._canCreateMetadata = canCreateMetadata
        if code is not None:
            self._code = code
        if hasCswClient is not None:
            self._hasCswClient = hasCswClient
        if keywordsCasing is not None:
            self._keywordsCasing = keywordsCasing
        if limits is not None:
            self._limits = limits
        if metadataLanguage is not None:
            self._metadataLanguage = metadataLanguage
        if themeColor is not None:
            self._themeColor = themeColor

        # required
        self._contact = contact

    # -- PROPERTIES --------------------------------------------------------------------
    # workgroup abilities
    @property
    def _abilities(self) -> str:
        """Gets the abilities of this Workgroup.

        :return: The abilities of this Workgroup.
        :rtype: str
        """
        return self.__abilities

    # workgroup creation date
    @property
    def _created(self) -> str:
        """Gets the created of this Workgroup.

        :return: The created of this Workgroup.
        :rtype: str
        """
        return self.__created

    # workgroup UUID
    @property
    def _id(self) -> str:
        """Gets the id of this Workgroup.

        :return: The id of this Workgroup.
        :rtype: str
        """
        return self.__id

    # workgroup last modification date
    @property
    def _modified(self) -> str:
        """Gets the modified of this Workgroup.

        :return: The modified of this Workgroup.
        :rtype: str
        """
        return self.__modified

    # Workgroup tag for search
    @property
    def _tag(self) -> str:
        """Gets the tag of this Workgroup.

        :return: The tag of this Workgroup.
        :rtype: str
        """
        return self.__tag

    # areKeywordsRestricted
    @property
    def areKeywordsRestricted(self) -> str:
        """Gets the areKeywordsRestricted of this Workgroup.

        :return: The areKeywordsRestricted of this Workgroup.
        :rtype: str
        """
        return self._areKeywordsRestricted

    @areKeywordsRestricted.setter
    def areKeywordsRestricted(self, areKeywordsRestricted: str):
        """Sets the areKeywordsRestricted of this Workgroup.

        :param str areKeywordsRestricted: The areKeywordsRestricted of this Workgroup.
        """

        self._areKeywordsRestricted = areKeywordsRestricted

    # canCreateMetadata
    @property
    def canCreateMetadata(self) -> bool:
        """Gets the canCreateMetadata of this Workgroup.

        :return: The canCreateMetadata of this Workgroup.
        :rtype: str
        """
        return self._canCreateMetadata

    @canCreateMetadata.setter
    def canCreateMetadata(self, canCreateMetadata: bool):
        """Sets the canCreateMetadata of this Workgroup.

        :param str canCreateMetadata: The canCreateMetadata of this Workgroup.
        """

        self._canCreateMetadata = canCreateMetadata

    # canCreateLegacyServiceLinks
    @property
    def canCreateLegacyServiceLinks(self) -> str:
        """Gets the canCreateLegacyServiceLinks of this Workgroup.

        :return: The canCreateLegacyServiceLinks of this Workgroup.
        :rtype: str
        """
        return self._canCreateLegacyServiceLinks

    @canCreateLegacyServiceLinks.setter
    def canCreateLegacyServiceLinks(self, canCreateLegacyServiceLinks: str):
        """Sets the canCreateLegacyServiceLinks of this Workgroup.

        :param str canCreateLegacyServiceLinks: The canCreateLegacyServiceLinks of this Workgroup. Must be one of GROUP_KIND_VALUES
        """

        self._canCreateLegacyServiceLinks = canCreateLegacyServiceLinks

    # code
    @property
    def code(self) -> str:
        """Gets the code of this Workgroup.

        :return: The code of this Workgroup.
        :rtype: str
        """
        return self._code

    # contact
    @property
    def contact(self) -> Contact:
        """Gets the contact of this Workgroup.

        :return: The contact of this Workgroup.
        :rtype: dict
        """
        return self._contact

    @contact.setter
    def contact(self, contact: Contact):
        """Sets the contact of this Workgroup.

        :param dict contact: The contact of this Workgroup.
        """

        if contact is None:
            raise ValueError("Invalid value for `contact`, must not be `None`")

        self._contact = contact

    # hasCswClient
    @property
    def hasCswClient(self) -> str:
        """Gets the hasCswClient of this Workgroup.

        :return: The hasCswClient of this Workgroup.
        :rtype: str
        """
        return self._hasCswClient

    @hasCswClient.setter
    def hasCswClient(self, hasCswClient: str):
        """Sets the hasCswClient of this Workgroup.

        :param str hasCswClient: The hasCswClient of this Workgroup. Must be one of GROUP_KIND_VALUES
        """

        self._hasCswClient = hasCswClient

    # keywordsCasing
    @property
    def keywordsCasing(self) -> str:
        """Gets the keywordsCasing of this Workgroup.

        :return: The keywordsCasing of this Workgroup.
        :rtype: str
        """
        return self._keywordsCasing

    @keywordsCasing.setter
    def keywordsCasing(self, keywordsCasing: str):
        """Sets the keywordsCasing of this Workgroup.

        :param str keywordsCasing: The keywordsCasing of this Workgroup. Must be one of GROUP_KIND_VALUES
        """

        self._keywordsCasing = keywordsCasing

    # limits
    @property
    def limits(self) -> dict:
        """Gets the limits of this Workgroup.

        :return: The limits of this Workgroup.
        :rtype: dict
        """
        return self._limits

    @limits.setter
    def limits(self, limits: dict):
        """Sets the limits of this Workgroup.

        :param dict limits: The limits of this Workgroup.
        """

        self._limits = limits

    # metadataLanguage
    @property
    def metadataLanguage(self) -> str:
        """Gets the metadataLanguage of this Workgroup.

        :return: The metadataLanguage of this Workgroup.
        :rtype: str
        """
        return self._metadataLanguage

    @metadataLanguage.setter
    def metadataLanguage(self, metadataLanguage: str):
        """Sets the metadataLanguage of this Workgroup.

        :param str metadataLanguage: The metadataLanguage of this Workgroup. Must be one of GROUP_KIND_VALUES
        """

        self._metadataLanguage = metadataLanguage

    # themeColor
    @property
    def themeColor(self) -> str:
        """Gets the themeColor of this Workgroup.

        :return: The themeColor of this Workgroup.
        :rtype: str
        """
        return self._themeColor

    @themeColor.setter
    def themeColor(self, themeColor: str):
        """Sets the themeColor of this Workgroup.

        :param str themeColor: The themeColor of this Workgroup. Must be one of GROUP_KIND_VALUES
        """

        self._themeColor = themeColor

    # -- SPECIFIC TO IMPLEMENTATION ----------------------------------------------------
    @property
    def name(self) -> str:
        """Shortcut to get the name of the workgroup."""
        if isinstance(self.contact, dict):
            return self.contact.get("name")
        elif isinstance(self.contact, Contact):
            return self.contact.name
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
        if issubclass(Workgroup, dict):
            for key, value in self.items():
                result[key] = value

        return result

    def to_dict_creation(self) -> dict:
        """Returns the model properties as a dict structured for creation purpose (POST)"""
        result = {}

        for attr in self.ATTR_CREA:
            # get attribute value
            value = getattr(self, attr)
            # switch attribute name for creation purpose
            if attr in self.ATTR_MAP:
                attr = self.ATTR_MAP.get(attr)
            # serialize depending on value type
            if isinstance(value, list):
                result[attr] = list(
                    map(lambda x: x.to_dict() if hasattr(x, "to_dict") else x, value)
                )
            # handle nested Contact properties
            elif isinstance(value, Contact):
                for i in attr:
                    result[i] = value.to_dict_creation().get(i.split(".")[1])
                # result[attr] = value.to_dict_creation().get(attr.split(".")[1])
            # handle other nested objects with 'to_dict' method
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
        if issubclass(Workgroup, dict):
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
        if not isinstance(other, Workgroup):
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
    obj = Workgroup()
