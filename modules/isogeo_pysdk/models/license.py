# -*- coding: UTF-8 -*-
#! python3  # noqa E265

"""
    Isogeo API v1 - Model of License entity

    See: http://help.isogeo.com/api/complete/index.html#definition-license
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# standard library
import pprint


# #############################################################################
# ########## Classes ###############
# ##################################
class License(object):
    """Licenses are entities included as subresource into metadata.

    :Example:

    .. code-block:: json

        {
            "_id": "string (uuid)",
            "content": "string",
            "count": "integer (int32)",
            "link": "string",
            "name": "string"
        }

    Attributes:
      ATTR_TYPES (dict): basic structure of license attributes. {"attribute name": "attribute type"}.
      ATTR_CREA (dict): only attributes used to POST requests. {"attribute name": "attribute type"}
    """

    ATTR_TYPES = {
        "_abilities": str,
        "_id": str,
        "_tag": str,
        "content": str,
        "count": int,
        "link": str,
        "name": str,
        "owner": dict,
    }

    ATTR_CREA = {"content": "str", "link": "str", "name": "str"}

    ATTR_MAP = {}

    def __init__(
        self,
        _abilities: list = None,
        _id: str = None,
        _tag: str = None,
        count: int = None,
        content: str = None,
        link: str = None,
        name: str = None,
        owner: dict = None,
    ):
        """License model.

        :param list _abilities: list of attached abilities, defaults to None
        :param str _id: object UUID, defaults to None
        :param str _tag: search tag code, defaults to None
        :param int count: count of associated metadata, defaults to None
        :param str content: description of the license, defaults to None
        :param str link: URL of the complete license, defaults to None
        :param str name: defaults to None
        :param dict owner: group which own the license, defaults to None
        """

        # default values for the object attributes/properties
        self.__abilities = None
        self.__id = None
        self.__tag = None
        self._content = None
        self._count = None
        self._link = None
        self._name = None
        self._owner = None

        # if values have been passed, so use them as objects attributes.
        # attributes are prefixed by an underscore '_'
        if _abilities is not None:
            self.__abilities = _abilities
        if _id is not None:
            self.__id = _id
        if _tag is not None:
            self.__tag = _tag
        if count is not None:
            self._count = count
        if content is not None:
            self._content = content
        if link is not None:
            self._link = link
        if name is not None:
            self._name = name
        if owner is not None:
            self._owner = owner

    # -- PROPERTIES --------------------------------------------------------------------
    # abilities of the user related to the metadata
    @property
    def _abilities(self) -> str:
        """Gets the abilities of this License.

        :return: The abilities of this License.
        :rtype: str
        """
        return self.__abilities

    # license UUID
    @property
    def _id(self) -> str:
        """Gets the id of this License.

        :return: The id of this License.
        :rtype: str
        """
        return self.__id

    # tag
    @property
    def _tag(self) -> str:
        """Gets the tag used in search filters.

        :return: The tag of this License.
        :rtype: str
        """
        return self.__tag

    # content
    @property
    def content(self) -> str:
        """Gets the content of this License.

        :return: The content of this License.
        :rtype: str
        """
        return self._content

    @content.setter
    def content(self, content: str):
        """Sets the content of this License.

        :param str content: The content of this License. Accept markdown syntax.
        """

        self._content = content

    # count of resource linked to the license
    @property
    def count(self) -> int:
        """Gets the count of this License.

        :return: The count of this License.
        :rtype: int
        """
        return self._count

    # link
    @property
    def link(self) -> str:
        """Gets the link (URL) of this License.

        :return: The link (URL) of this License.
        :rtype: str
        """
        return self._link

    @link.setter
    def link(self, link: str):
        """Sets the link of this License.

        :param str link: The link (URL) of this License.
        """

        self._link = link

    # name
    @property
    def name(self) -> str:
        """Gets the name of this License.

        :return: The name of this License.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name: str):
        """Sets the name of this License.

        :param str name: The name of this License.
        """

        self._name = name

    # workgroup owner
    @property
    def owner(self):
        """Gets the owner of this License.

        :return: The owner of this License.
        :rtype: Workgroup
        """
        return self._owner

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
        if issubclass(License, dict):
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
        if issubclass(License, dict):
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
        if not isinstance(other, License):
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
    lic = License(name="License Test", content="Test license content")
    print(lic)
