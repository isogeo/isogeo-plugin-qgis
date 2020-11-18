# -*- coding: UTF-8 -*-
#! python3  # noqa E265

"""
    Isogeo API v1 - Model of Format entity

    See: http://help.isogeo.com/api/complete/index.html#definition-format
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# standard library
import pprint


# #############################################################################
# ########## Classes ###############
# ##################################
class Format(object):
    """Formats are entities included as subresource into metadata for data history code.

    :Example:

    .. code-block:: json

        {
            "_id": string (uuid),
            "_tag": "format:dgn",
            "aliases": [
                "dgnv7",
                "dgnv8",
                "igds"
            ],
            "code": "dgn",
            "name": "DGN",
            "type": "dataset",
            "versions": [
                "v8",
                "V7",
                null
            ]
        }
    """

    ATTR_TYPES = {
        "_id": str,
        "_tag": str,
        "aliases": list,
        "code": str,
        "name": str,
        "type": str,
        "versions": list,
    }

    ATTR_CREA = {
        "aliases": list,
        "code": str,
        "name": str,
        "type": str,
        "versions": list,
    }

    ATTR_MAP = {}

    def __init__(
        self,
        _id: str = None,
        _tag: str = None,
        aliases: list = None,
        code: str = None,
        name: str = None,
        type: str = None,
        versions: list = None,
    ):
        """Format model."""

        # default values for the object attributes/properties
        self.__id = None
        self.__tag = None
        self._code = None
        self._name = None
        self._type = None
        self._aliases = None
        self._versions = None

        # if values have been passed, so use them as objects attributes.
        # attributes are prefixed by an underscore '_'
        if _id is not None:
            self.__id = _id
        if _tag is not None:
            self.__tag = _tag
        if aliases is not None:
            self._aliases = aliases
        if code is not None:
            self._code = code
        if name is not None:
            self._name = name
        if type is not None:
            self._type = type
        if versions is not None:
            self._versions = versions

    # -- PROPERTIES --------------------------------------------------------------------
    # format UUID
    @property
    def _id(self) -> str:
        """Gets the id of this Format.

        :return: The id of this Format.
        :rtype: str
        """
        return self.__id

    # _tag
    @property
    def _tag(self) -> str:
        """Gets the _tag of this Format.

        :return: The _tag of this Format.
        :rtype: str
        """
        return self.__tag

    # aliases
    @property
    def aliases(self) -> list:
        """Gets the aliases of this Format.

        :return: The aliases of this Format.
        :rtype: list
        """
        return self._aliases

    @aliases.setter
    def aliases(self, aliases: list):
        """Sets the aliases of this Format.

        :param list aliases: The aliases of this Format.
        """

        self._aliases = aliases

    # code
    @property
    def code(self) -> str:
        """Gets the code of this Format.

        :return: The code of this Format.
        :rtype: str
        """
        return self._code

    # name
    @property
    def name(self) -> str:
        """Gets the name of this Format.

        :return: The name of this Format.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name: str):
        """Sets the name of this Format.

        :param str name: The name of this Format.
        """

        self._name = name

    # type
    @property
    def type(self) -> str:
        """Gets the type of this Format.

        :return: The type of this Format.
        :rtype: str
        """
        return self._type

    @type.setter
    def type(self, type: str):
        """Sets the type of this Format.

        :param str type: The type of this Format.
        """

        self._type = type

    # versions
    @property
    def versions(self) -> list:
        """Gets the versions of this Format.

        :return: The versions of this Format.
        :rtype: list
        """
        return self._versions

    @versions.setter
    def versions(self, versions: list):
        """Sets the versions of this Format.

        :param list versions: The versions of this Format.
        """

        self._versions = versions

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
        if issubclass(Format, dict):
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
        if issubclass(Format, dict):
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
        if not isinstance(other, Format):
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
    ct = Format()
