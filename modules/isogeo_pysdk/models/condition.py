# -*- coding: UTF-8 -*-
#! python3  # noqa E265

"""
    Isogeo API v1 - Model of Condition entity

    See: http://help.isogeo.com/api/complete/index.html#definition-resourceCondition
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# standard library
import pprint

# others related models
from .license import License


# #############################################################################
# ########## Classes ###############
# ##################################
class Condition(object):
    """Conditions are entities defining general conditions of use (CGUs) of a data. It's mainly
    composed by a license and a description.

    :param str _id: object UUID
    :param str description: description of the condition
    :param dict license: license object or dict linked to the condition
    :param str parent_resource: UUID of the metadata containing the condition

    :Example:

    .. code-block:: json

        {
            "_id": "string (uuid)",
            "description": "string",
            "license": "string",
        }
    """

    ATTR_TYPES = {
        "_id": str,
        "description": str,
        "license": License,
        "parent_resource": str,
    }

    ATTR_CREA = {"description": "str", "license": License}

    ATTR_MAP = {}

    def __init__(
        self,
        _id: str = None,
        description: str = None,
        license: dict or License = None,
        # specific implementation
        parent_resource: str = None,
    ):

        # default values for the object attributes/properties
        self.__id = None
        self._description = None
        self._license = None
        self._parent_resource = None

        # if values have been passed, so use them as objects attributes.
        # attributes are prefixed by an underscore '_'
        if _id is not None:
            self.__id = _id
        if description is not None:
            self._description = description
        if license is not None and isinstance(license, License):
            self._license = license
        if license is not None and isinstance(license, dict):
            self._license = License(**license)
        if parent_resource is not None:
            self._parent_resource = parent_resource

    # -- PROPERTIES --------------------------------------------------------------------
    # condition UUID
    @property
    def _id(self) -> str:
        """Gets the id of this Condition.

        :return: The id of this Condition.
        :rtype: str
        """
        return self.__id

    # description
    @property
    def description(self) -> str:
        """Gets the description of this Condition.

        :return: The description of this Condition.
        :rtype: str
        """
        return self._description

    @description.setter
    def description(self, description: str):
        """Sets the description of this Condition.

        :param str description: The description of this Condition. Accept markdown syntax.
        """

        self._description = description

    @property
    def license(self) -> str:
        """Gets the license of this Condition.

        :return: The license of this Condition.
        :rtype: str
        """
        return self._license

    @license.setter
    def license(self, license: dict or License):
        """Sets the license of this Condition.

        :param dict license: The license of this Condition.
        """
        if isinstance(license, License):
            self._license = license
        elif isinstance(license, dict):
            self._license = License(**license)
        else:
            self._license = license
            raise Warning(
                "Invalid license parameter ({}) to set as license for this condition.".format(
                    license
                )
            )

    # parent metadata
    @property
    def parent_resource(self):
        """Gets the parent_resource of this Condition.

        :return: The parent_resource of this Condition.
        :rtype: UUID
        """
        return self._parent_resource

    @parent_resource.setter
    def parent_resource(self, parent_resource_UUID):
        """Sets the parent metadata UUID of this Condition.

        :return: The parent_resource of this Condition.
        :rtype: UUID
        """
        self._parent_resource = parent_resource_UUID

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
        if issubclass(Condition, dict):
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
        if issubclass(Condition, dict):
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
        if not isinstance(other, Condition):
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
    fixture = Condition(description="Test condition description")
    print(fixture)
