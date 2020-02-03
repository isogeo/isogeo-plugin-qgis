# -*- coding: UTF-8 -*-
#! python3  # noqa E265

"""
    Isogeo API v1 - Model of Share entity

    See: http://help.isogeo.com/api/complete/index.html#definition-share
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# standard library
import logging
import pprint

# other model
from isogeo_pysdk.models.workgroup import Workgroup

# #############################################################################
# ########## Globals ###############
# ##################################

logger = logging.getLogger(__name__)


# #############################################################################
# ########## Classes ###############
# ##################################
class Share(object):
    """Shares are entities used to publish catalog(s) of metadata to applications.

    :Example:

    .. code-block:: json

        {
            "_created": "string (date-time)",
            "_creator": {
                "_abilities": [
                "string"
                ],
                "_created": "string (date-time)",
                "_id": "string (uuid)",
                "_modified": "string (date-time)",
                "areKeywordsRestricted": "boolean",
                "canCreateMetadata": "boolean",
                "catalogs": "string",
                "contact": {
                "_created": "string (date-time)",
                "_id": "string (uuid)",
                "_modified": "string (date-time)",
                "addressLine1": "string",
                "addressLine2": "string",
                "addressLine3": "string",
                "available": "string",
                "city": "string",
                "groups": "integer (int32)",
                "groupsryCode": "string",
                "email": "string",
                "fax": "string",
                "hash": "string",
                "name": "string",
                "organization": "string",
                "phone": "string",
                "type": "string",
                "zipCode": "string"
                },
                "keywordsCasing": "string",
                "metadataLanguage": "string",
                "themeColor": "string"
            },
            "_id": "string (uuid)",
            "_modified": "string (date-time)",
            "applications": [
                {
                "_created": "string (date-time)",
                "_id": "string (uuid)",
                "_modified": "string (date-time)",
                "canHaveManyGroups": "boolean",
                "client_id": "string",
                "client_secret": "string",
                "groups": [
                    {
                    "_abilities": [
                        "string"
                    ],
                    "_created": "string (date-time)",
                    "_id": "string (uuid)",
                    "_modified": "string (date-time)",
                    "areKeywordsRestricted": "boolean",
                    "canCreateMetadata": "boolean",
                    "catalogs": "string",
                    "contact": {
                        "_created": "string (date-time)",
                        "_id": "string (uuid)",
                        "_modified": "string (date-time)",
                        "addressLine1": "string",
                        "addressLine2": "string",
                        "addressLine3": "string",
                        "available": "string",
                        "city": "string",
                        "groups": "integer (int32)",
                        "groupsryCode": "string",
                        "email": "string",
                        "fax": "string",
                        "hash": "string",
                        "name": "string",
                        "organization": "string",
                        "phone": "string",
                        "type": "string",
                        "zipCode": "string"
                    },
                    "keywordsCasing": "string",
                    "metadataLanguage": "string",
                    "themeColor": "string"
                    }
                ],
                "kind": "string",
                "name": "string",
                "redirect_uris": [
                    "string"
                ],
                "scopes": [
                    "string"
                ],
                "staff": "boolean",
                "url": "string"
                }
            ],
            "catalogs": [
                {
                "$scan": "boolean",
                "_abilities": [
                    "string"
                ],
                "_created": "string (date-time)",
                "_id": "string (uuid)",
                "_modified": "string (date-time)"
                }
            ]
        }
    """

    ATTR_TYPES = {
        "_created": str,
        "_creator": Workgroup,
        "_id": str,
        "_modified": str,
        "applications": list,
        "catalogs": list,
        "groups": list,
        "name": str,
        "rights": list,
        "type": str,
        "urlToken": str,
    }

    ATTR_CREA = {
        # "applications": list,
        # "catalogs": list,
        # "groups": list,
        "name": str,
        "rights": list,
        "type": str,
    }

    ATTR_MAP = {}

    def __init__(
        self,
        _created: str = None,
        _creator: Workgroup = None,
        _id: str = None,
        _modified: str = None,
        applications: list = None,
        catalogs: list = None,
        groups: list = None,
        name: str = None,
        rights: list = None,
        type: str = None,
        urlToken: str = None,
    ):
        """Share model."""

        # default values for the object attributes/properties
        self.__created = None
        self.__creator = (None,)
        self.__id = None
        self.__modified = None
        self._applications = None
        self._catalogs = None
        self._groups = None
        self._name = None
        self._rights = None
        self._type = None
        self._urlToken = None

        # if values have been passed, so use them as objects attributes.
        # attributes are prefixed by an underscore '_'
        if _created is not None:
            self.__created = _created
        if _creator is not None:
            self.__creator = _creator
        if _id is not None:
            self.__id = _id
        if _modified is not None:
            self.__modified = _modified
        if applications is not None:
            self._applications = applications
        if catalogs is not None:
            self._catalogs = catalogs
        if groups is not None:
            self._groups = groups
        if name is not None:
            self._name = name
        if rights is not None:
            self._rights = rights
        if type is not None:
            self._type = type
        if urlToken is not None:
            self._urlToken = urlToken

    # -- PROPERTIES --------------------------------------------------------------------
    # share creator
    @property
    def _creator(self) -> Workgroup:
        """Gets the creator of this Share.

        :return: The creator of this Share.
        :rtype: Workgroup
        """
        return self.__creator

    # share creation date
    @property
    def _created(self) -> str:
        """Gets the created of this Share.

        :return: The created of this Share.
        :rtype: str
        """
        return self.__created

    # share UUID
    @property
    def _id(self) -> str:
        """Gets the id of this Share.

        :return: The id of this Share.
        :rtype: str
        """
        return self.__id

    # share last modification date
    @property
    def _modified(self) -> str:
        """Gets the modified of this Share.

        :return: The modified of this Share.
        :rtype: str
        """
        return self.__modified

    # applications
    @property
    def applications(self) -> list:
        """Gets the applications of this Share.

        :return: The applications of this Share.
        :rtype: str
        """
        return self._applications

    # catalogs
    @property
    def catalogs(self) -> list:
        """Gets the catalogs of this Share.

        :return: The catalogs of this Share.
        :rtype: str
        """
        return self._catalogs

    # name
    @property
    def name(self) -> str:
        """Gets the name of this Share.

        :return: The name of this Share.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name: str):
        """Sets the name of this Share.

        :param str name: The name of this Share.
        """

        self._name = name

    # groups
    @property
    def groups(self) -> list:
        """Gets the groups of this Share.

        :return: The groups of this Share.
        :rtype: list
        """
        return self._groups

    @groups.setter
    def groups(self, groups: list):
        """Sets the groups of this Share.

        :param list groups: The groups of this Share.
        """

        self._groups = groups

    @property
    def rights(self) -> list:
        """Gets the rights of this Share.

        :return: The rights of this Share.
        :rtype: str
        """
        return self._rights

    @rights.setter
    def rights(self, rights: list):
        """Sets the rights of this Share.

        :param list rights: The rights of this Share.
        """

        self._rights = rights

    @property
    def type(self) -> str:
        """Gets the type of this Share.

        :return: The type of this Share.
        :rtype: str
        """
        return self._type

    # urlToken
    @property
    def urlToken(self) -> str:
        """Gets the urlToken of this Share.

        :return: The urlToken of this Share.
        :rtype: str
        """
        return self._urlToken

    # -- METHODS -----------------------------------------------------------------------
    def admin_url(self, url_base: str = "https://app.isogeo.com") -> str:
        """Returns the administration URL (https://app.isogeo.com) for this share.

        :param str url_base: base URL of admin site. Defaults to: https://app.isogeo.com

        :rtype: str
        """
        creator_id = self._creator.get("_tag")[6:]
        return "{}/groups/{}/admin/shares/{}".format(url_base, creator_id, self._id)

    def opencatalog_url(
        self, url_base: str = "https://open.isogeo.com"
    ) -> str or bool or None:
        """Returns the OpenCatalog URL for this share or None if OpenCatalog is not enabled.

        :param str url_base: base URL of OpenCatalog. Defaults to: https://open.isogeo.com

        :returns:

            - False if the share type is not 'application'
            - None if OpenCatalog is not enabled in the share
            - URL of the OpenCatalog when everything is fine
        """
        # opencatalog URL is valid only for share's of type 'application'
        if self.type != "application":
            logger.warning(
                "Only shares of type 'application' can have an OpenCatalog URL, "
                "not '{}'.".format(self.type)
            )
            return False
        # check if the urlToken exists which means that OpenCatalog URL is not allowed
        if self.urlToken is None:
            return None

        return "{}/s/{}/{}".format(url_base, self._id, self.urlToken)

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
        if issubclass(Share, dict):
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
            # process value depending on attr type
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
        if issubclass(Share, dict):
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
        if not isinstance(other, Share):
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
    model = Share(name="Test Share model")
    to_crea = model.to_dict_creation()
