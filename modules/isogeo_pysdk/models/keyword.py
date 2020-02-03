# -*- coding: UTF-8 -*-
#! python3  # noqa E265

"""
    Isogeo API v1 - Model of Keyword entity

    See: http://help.isogeo.com/api/complete/index.html#definition-keyword
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# standard library
import pprint

# other model
from isogeo_pysdk.models.thesaurus import Thesaurus


# #############################################################################
# ########## Classes ###############
# ##################################
class Keyword(object):
    """Keywords are entities used to organize and shares metadata of a workgroup.

    :Example:

    .. code-block:: json

        {
            '_abilities': [
                'keyword:delete',
                'keyword:restrict'
                ],
            '_created': None,
            '_id': 'ac56a9fbe6f348a79ec9899ebce2d6da',
            '_modified': None,
            '_tag': 'keyword:isogeo:tests-unitaires',
            'code': 'tests-unitaires',
            'count': {
                'isogeo': 0
                },
            'description': None,
            'text': 'tests unitaires',
            'thesaurus': {
                '_id': '1616597fbc4348c8b11ef9d59cf594c8',
                'code': 'isogeo'
                }
        }
    """

    ATTR_TYPES = {
        "_abilities": list,
        "_created": str,
        "_id": str,
        "_modified": str,
        "_tag": str,
        "code": str,
        "count": dict,
        "description": str,
        "thesaurus": Thesaurus,
        "text": str,
    }

    ATTR_CREA = {"text": str}

    ATTR_MAP = {}

    def __init__(
        self,
        _abilities: list = None,
        _created: str = None,
        _id: str = None,
        _modified: str = None,
        _tag: str = None,
        code: str = None,
        count: dict = None,
        description: str = None,  # only for INSPIRE and ISO19115 thesauri
        thesaurus: Thesaurus = None,
        text: bool = None,
    ):
        """Keyword model."""

        # default values for the object attributes/properties
        self.__abilities = None
        self.__created = None
        self.__id = None
        self.__modified = None
        self.__tag = None
        self._code = None
        self._count = None
        self._description = None
        self._thesaurus = (None,)
        self._text = None

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
        if _tag is not None:
            self.__tag = _tag
        if code is not None:
            self._code = code
        if count is not None:
            self._count = count
        if description is not None:
            self._description = description
        if text is not None:
            self._text = text

        # required
        self._thesaurus = thesaurus

    # -- PROPERTIES --------------------------------------------------------------------
    # keyword abilities
    @property
    def _abilities(self) -> str:
        """Gets the abilities of this Keyword.

        :return: The abilities of this Keyword.
        :rtype: str
        """
        return self.__abilities

    # keyword creation date
    @property
    def _created(self) -> str:
        """Gets the created of this Keyword.

        :return: The created of this Keyword.
        :rtype: str
        """
        return self.__created

    # keyword UUID
    @property
    def _id(self) -> str:
        """Gets the id of this Keyword.

        :return: The id of this Keyword.
        :rtype: str
        """
        return self.__id

    # keyword last modification date
    @property
    def _modified(self) -> str:
        """Gets the modified of this Keyword.

        :return: The modified of this Keyword.
        :rtype: str
        """
        return self.__modified

    # keyword tag for search
    @property
    def _tag(self) -> str:
        """Gets the tag of this Keyword.

        :return: The tag of this Keyword.
        :rtype: str
        """
        return self.__tag

    # code
    @property
    def code(self) -> str:
        """Gets the code of this Keyword.

        :return: The code of this Keyword.
        :rtype: str
        """
        return self._code

    # count
    @property
    def count(self) -> dict:
        """Gets the count of this Keyword.

        :return: The count of this Keyword.
        :rtype: dict
        """
        return self._count

    # description
    @property
    def description(self) -> str:
        """Gets the description of this Keyword.

        :return: The description of this Keyword.
        :rtype: str
        """
        return self._description

    @description.setter
    def description(self, description: str):
        """Sets the description of this Keyword.

        :param str description: The description of this Keyword.
        """

        self._description = description

    # text
    @property
    def text(self) -> bool:
        """Gets the text of this Keyword.

        :return: The text of this Keyword.
        :rtype: bool
        """
        return self._text

    @text.setter
    def text(self, text: bool):
        """Sets the text of this Keyword.

        :param bool text: The text of this Keyword. Must be one of GROUP_KIND_VALUES
        """

        self._text = text

    @property
    def thesaurus(self):
        """Gets the thesaurus of this Keyword.  # noqa: E501.

        :return: The thesaurus of this Keyword.  # noqa: E501
        :rtype: Thesaurus
        """
        return self._thesaurus

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
        if issubclass(Keyword, dict):
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
        if issubclass(Keyword, dict):
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
        if not isinstance(other, Keyword):
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
    fixture = Keyword(description="keyword text")
    to_crea = fixture.to_dict_creation()
