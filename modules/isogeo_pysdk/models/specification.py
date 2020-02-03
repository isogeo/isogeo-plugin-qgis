# -*- coding: UTF-8 -*-
#! python3  # noqa E265

"""
    Isogeo API v1 - Model of Specification entity

    See: http://help.isogeo.com/api/complete/index.html#definition-specification

"""

# #############################################################################
# ########## Libraries #############
# ##################################

# standard library
import pprint


# #############################################################################
# ########## Classes ###############
# ##################################
class Specification(object):
    """Specifications are entities defining rules of data creation.

    :Example:

    .. code-block:: json

        {
            '_abilities': [],
            '_id': 'string (uuid)',
            '_tag': 'specification:isogeo:string (uuid)',
            'count': int,
            'link': string,
            'name': string,
            'published': '2016-06-30T00:00:00'
        }
    """

    ATTR_TYPES = {
        "_abilities": str,
        "_id": str,
        "_tag": str,
        "count": int,
        "link": str,
        "name": str,
        "owner": dict,
        "published": str,
    }

    ATTR_CREA = {"link": str, "name": str, "published": str}

    ATTR_MAP = {}

    def __init__(
        self,
        _abilities: list = None,
        _id: str = None,
        _tag: str = None,
        count: int = None,
        link: str = None,
        name: str = None,
        owner: dict = None,
        published: str = None,
    ):
        """Specification model."""

        # default values for the object attributes/properties
        self.__abilities = None
        self.__id = None
        self.__tag = None
        self._count = None
        self._link = None
        self._name = None
        self._owner = None
        self._published = None

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
        if link is not None:
            self._link = link
        if name is not None:
            self._name = name
        if owner is not None:
            self._owner = owner
        if published is not None:
            self._published = published

    # -- PROPERTIES --------------------------------------------------------------------
    # abilities of the user related to the metadata
    @property
    def _abilities(self) -> str:
        """Gets the abilities of this Catalog.

        :return: The abilities of this Catalog.
        :rtype: str
        """
        return self.__abilities

    # specification UUID
    @property
    def _id(self) -> str:
        """Gets the id of this Specification.

        :return: The id of this Specification.
        :rtype: str
        """
        return self.__id

    @_id.setter
    def _id(self, _id: str):
        """Sets the id of this Specification.

        :param str id: The id of this Specification.
        """

        self.__id = _id

    # specification UUID
    @property
    def _tag(self) -> str:
        """Gets the tag used for Isogeo filters of this Specification.

        :return: The tag of this Specification.
        :rtype: str
        """
        return self.__tag

    @_tag.setter
    def _tag(self, _tag: str):
        """Sets the tag used into Isogeo filters of this Specification.

        :param str _tag: the tag of this Specification.
        """

        self.__tag = _tag

    # count of resource linked to the specification
    @property
    def count(self) -> int:
        """Gets the id of this Specification.

        :return: The id of this Specification.
        :rtype: str
        """
        return self._count

    @count.setter
    def count(self, count: int):
        """Sets the count of this Specification.

        :param int count: count of associated resources to the Specification
        """

        self._count = count

    # link
    @property
    def link(self) -> str:
        """Gets the link (URL) of this Specification.

        :return: The link (URL) of this Specification.
        :rtype: str
        """
        return self._link

    @link.setter
    def link(self, link: str):
        """Sets the id of this Specification.

        :param str XX: The id of this Specification.
        """

        self._link = link

    # name
    @property
    def name(self) -> str:
        """Gets the id of this Specification.

        :return: The id of this Specification.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name: str):
        """Sets the id of this Specification.

        :param str XX: The id of this Specification.
        """

        self._name = name

    # workgroup owner
    @property
    def owner(self):
        """Gets the owner of this Specification.

        :return: The owner of this Specification.
        :rtype: Workgroup
        """
        return self._owner

    # published
    @property
    def published(self) -> str:
        """Gets the zip (postal) code of this Specification.

        :return: The zip (postal) code of this Specification.
        :rtype: str
        """
        return self._published

    @published.setter
    def published(self, published: str):
        """Sets the zip (postal) code of this Specification.

        :param str published: The zip (postal) code of this Specification.
        """

        self._published = published

    # -- SPECIFIC TO IMPLEMENTATION ----------------------------------------------------
    @property
    def isLocked(self) -> bool or None:
        """Shortcut to know if the Specification is owned by Isogeo or a workgroup.

        :returns:
            - None if tag is None too
            - True if the specification is owned by Isogeo = locked
            - False if the specification is owned by a workgroup = not locked
        """
        # if tag is not set, return None as well
        if self._tag is None:
            return None

        # if tag is set, have a look
        if ":isogeo:" in self._tag:
            return True
        else:
            return False

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
        if issubclass(Specification, dict):
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
        if issubclass(Specification, dict):
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
        if not isinstance(other, Specification):
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
    ct = Specification()
    print(ct.__dict__)
    print(ct._id)
    print(ct.__dict__.get("_id"))
    print(hasattr(ct, "_id"))
    print(ct.to_dict_creation())
    # print(ct.to_str()
