# -*- coding: UTF-8 -*-
#! python3  # noqa E265

"""
    Isogeo API v1 - Model of Limitation entity

    See: http://help.isogeo.com/api/complete/index.html
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# standard library
import pprint

# package
from ..enums import LimitationRestrictions, LimitationTypes
from .directive import Directive


# #############################################################################
# ########## Classes ###############
# ##################################
class Limitation(object):
    """Limitations are entities included as subresource into metadata which can contain a Directive.

    :Example:

    .. code-block:: json

        {
            "_id": "string (uuid)",
            "description": "string",
            "directive": "dict",
            "restriction": "string",
            "type": "string"
        }
    """

    ATTR_TYPES = {
        "_id": str,
        "description": str,
        "directive": int,
        "restriction": str,
        "type": str,
        "parent_resource": str,
    }

    ATTR_CREA = {
        "description": "str",
        "directive": Directive,
        "restriction": "str",
        "type": "str",
    }

    ATTR_MAP = {}

    def __init__(
        self,
        _id: str = None,
        description: str = None,
        directive: int = None,
        restriction: str = None,
        type: str = None,
        parent_resource: str = None,  # specific to implementation
    ):
        """Limitation model.

        :param str _id: object UUID, defaults to None
        :param str description: description of the license, defaults to None
        :param Directive directive: directive of associated metadata, defaults to None
        :param str restriction: URL of the complete license, defaults to None
        :param str type: limitation type, defaults to None
        :param str parent_resource: UUID of the metadata containgin the limitation
        """

        # default values for the object attributes/properties
        self.__id = None
        self._description = None
        self._directive = None
        self._restriction = None
        self._type = None
        # additional parameters
        self.parent_resource = parent_resource

        # if values have been passed, so use them as objects attributes.
        # attributes are prefixed by an underscore '_'
        if _id is not None:
            self.__id = _id
        if directive is not None:
            self._directive = directive
        if description is not None:
            self._description = description
        if restriction is not None:
            self._restriction = restriction
        if type is not None:
            self._type = type
        if parent_resource is not None:
            self._parent_resource = parent_resource

    # -- PROPERTIES --------------------------------------------------------------------
    # license UUID
    @property
    def _id(self) -> str:
        """Gets the id of this Limitation.

        :return: The id of this Limitation.
        :rtype: str
        """
        return self.__id

    # description
    @property
    def description(self) -> str:
        """Gets the description of this Limitation.

        :return: The description of this Limitation.
        :rtype: str
        """
        return self._description

    @description.setter
    def description(self, description: str):
        """Sets the description of this Limitation.

        :param str description: The description of this Limitation. Accept markdown syntax.
        """

        self._description = description

    # directive of resource restrictioned to the license
    @property
    def directive(self) -> Directive:
        """Gets the directive of this Limitation.

        :return: The directive of this Limitation.
        :rtype: Directive
        """
        return self._directive

    @directive.setter
    def directive(self, directive: Directive):
        """Sets the directive of this Limitation.

        :param Directive directive: The directive of this Limitation.
        """

        self._directive = directive

    # restriction
    @property
    def restriction(self) -> str:
        """Gets the restriction of this Limitation.

        :return: The restriction of this Limitation.
        :rtype: str
        """
        return self._restriction

    @restriction.setter
    def restriction(self, restriction: str):
        """Sets the restriction of this Limitation.

        :param str restriction: The restriction of this Limitation.
        """
        # check type value
        if restriction is not None and restriction not in LimitationRestrictions.__members__:
            raise ValueError(
                "Limitation restriction '{}' is not an accepted value. Must be one of: {}.".format(
                    type, " | ".join([e.name for e in LimitationRestrictions])
                )
            )

        self._restriction = restriction

    # type
    @property
    def type(self) -> str:
        """Gets the type of this Limitation.

        :return: The type of this Limitation.
        :rtype: str
        """
        return self._type

    @type.setter
    def type(self, type: str):
        """Sets the type of this Limitation.

        :param str type: The type of this Limitation.
        """
        # check type value
        if type not in LimitationTypes.__members__:
            raise ValueError(
                "Limitation type '{}' is not an accepted value. Must be one of: {}.".format(
                    type, " | ".join([e.name for e in LimitationTypes])
                )
            )

        self._type = type

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
        if issubclass(Limitation, dict):
            for key, value in self.items():
                result[key] = value

        return result

    def to_dict_creation(self) -> dict:
        """Returns the model properties as a dict structured for creation purpose (POST)"""
        result = {}

        for attr, _ in self.ATTR_CREA.items():
            # get attribute value
            value = getattr(self, attr)
            # switch attribute type for creation purpose
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
        if issubclass(Limitation, dict):
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
        if not isinstance(other, Limitation):
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
