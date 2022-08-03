# -*- coding: UTF-8 -*-
#! python3  # noqa E265

"""
    Isogeo API v1 - Model of CoordinateSystem entity

    See: http://help.isogeo.com/api/complete/index.html
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# standard library
import pprint


# #############################################################################
# ########## Classes ###############
# ##################################
class CoordinateSystem(object):
    """CoordinateSystems.

    :Example:

    .. code-block:: json

        {
            '_tag': 'coordinate-system:31154',
            'code': 31154,
            'name': 'Zanderij / TM 54 NW'
        }
    """

    ATTR_TYPES = {"_tag": str, "alias": str, "code": str, "name": str}

    ATTR_CREA = {}

    ATTR_MAP = {}

    def __init__(self, _tag: str = None, alias: str = None, code: str = None, name: str = None):
        """Coordinate-systems model."""

        # default values for the object attributes/properties
        self.__tag = None
        self._alias = None
        self._code = None
        self._name = None

        # if values have been passed, so use them as objects attributes.
        # attributes are prefixed by an underscore '_'
        if _tag is not None:
            self.__tag = _tag
        if alias is not None:
            self._alias = alias
        if code is not None:
            self._code = code
        if name is not None:
            self._name = name

    # -- PROPERTIES --------------------------------------------------------------------
    # tag
    @property
    def _tag(self) -> str:
        """Gets the tag used for Isogeo filters of this CoordinateSystem.

        :return: The tag of this CoordinateSystem.
        :rtype: str
        """
        return self.__tag

    # alias
    @property
    def alias(self) -> str:
        """Gets the custom alias of this CoordinateSystem in a workgroup.

        :return: The alias of this CoordinateSystem in a workgroup.
        :rtype: str
        """
        return self._alias

    @alias.setter
    def alias(self, alias: str):
        """Sets the custom alias of this CoordinateSystem.

        :param str alias: custom alias of the CoordinateSystem
        """

        self._alias = alias

    # EPSG code
    @property
    def code(self) -> str:
        """Gets the EPSG code of this CoordinateSystem.

        :return: The EPSG code of this CoordinateSystem.
        :rtype: str
        """
        return self._code

    # name
    @property
    def name(self) -> str:
        """Gets the name of this CoordinateSystem.

        :return: The name of this CoordinateSystem.
        :rtype: str
        """
        return self._name

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
        if issubclass(CoordinateSystem, dict):
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
        if issubclass(CoordinateSystem, dict):
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
        if not isinstance(other, CoordinateSystem):
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
    fixture = CoordinateSystem(name="CoordinateSystem Test")
    print(fixture)
