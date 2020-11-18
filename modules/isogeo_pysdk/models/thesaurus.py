# -*- coding: UTF-8 -*-
#! python3  # noqa E265

"""
    Isogeo API v1 - Model of Thesaurus entity

    See: http://help.isogeo.com/api/complete/index.html#definition-thesaurus
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# standard library
import pprint


# #############################################################################
# ########## Classes ###############
# ##################################
class Thesaurus(object):
    """Thesaurus are entities which can be used in shares.

    :Example:

    .. code-block:: JSON

        {
            '_abilities': [],
            '_id': '926f969ee2bb470a84066625f68b96bb',
            'code': 'iso19115-topic',
            'name': 'MD_TopicCategoryCode'
        }
    """

    ATTR_TYPES = {"_abilities": list, "_id": str, "code": str, "name": str}

    ATTR_CREA = {"name": str}

    ATTR_MAP = {}

    def __init__(
        self,
        _abilities: list = None,
        _id: str = None,
        code: str = None,
        name: str = None,
    ):
        """Thesaurus model."""

        # default values for the object attributes/properties
        self.__abilities = None
        self.__id = None
        self._code = None
        self._name = None

        # if values have been passed, so use them as objects attributes.
        # attributes are prefixed by an underscore '_'
        if _abilities is not None:
            self.__abilities = _abilities
        if _id is not None:
            self.__id = _id
        if code is not None:
            self._code = code
        if name is not None:
            self._name = name

    # -- PROPERTIES --------------------------------------------------------------------
    # thesaurus abilities
    @property
    def _abilities(self) -> str:
        """Gets the abilities of this Thesaurus.

        :return: The abilities of this Thesaurus.
        :rtype: str
        """
        return self.__abilities

    # thesaurus UUID
    @property
    def _id(self) -> str:
        """Gets the id of this Thesaurus.

        :return: The id of this Thesaurus.
        :rtype: str
        """
        return self.__id

    @_id.setter
    def _id(self, _id: str):
        """Sets the id of this Thesaurus.

        :param str id: The id of this Thesaurus.
        """
        if _id is None:
            raise ValueError("Invalid value for `_id`, must not be `None`")

        self.__id = _id

    # code
    @property
    def code(self) -> str:
        """Gets the code of this Thesaurus.

        :return: The code of this Thesaurus.
        :rtype: str
        """
        return self._code

    @code.setter
    def code(self, code: str):
        """Sets the code of this Thesaurus.

        :param str code: The code of this Thesaurus.
        """

        self._code = code

    # name
    @property
    def name(self) -> str:
        """Gets the name of this Thesaurus.

        :return: The name of this Thesaurus.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name: str):
        """Sets the name of this Thesaurus.

        :param str name: The name of this Thesaurus.
        """

        self._name = name

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
        if issubclass(Thesaurus, dict):
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
        if issubclass(Thesaurus, dict):
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
        if not isinstance(other, Thesaurus):
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
    thesaurus = Thesaurus(name="GEMET - INSPIRE themes")
    to_crea = thesaurus.to_dict_creation()
