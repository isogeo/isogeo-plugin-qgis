# -*- coding: UTF-8 -*-
#! python3  # noqa E265

"""
    Isogeo API v1 - Model of Link entity

    See: http://help.isogeo.com/api/complete/index.html#definition-link
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# standard library
import pprint

# package
from isogeo_pysdk.enums import LinkKinds, LinkTypes


# #############################################################################
# ########## Classes ###############
# ##################################
class Link(object):
    """Links are entities included as subresource into metadata for data history title.

    :Example:

    .. code-block:: json

        {
            '_id': string (uuid),
            'actions': list,
            'kind': string,
            'parent_resource': string (uuid),
            'size': int,
            'title': string,
            'type': string,
            'url': string
        }
    """

    ATTR_TYPES = {
        "_id": str,
        "actions": list,
        "kind": str,
        "link": dict,
        "parent_resource": str,
        "size": int,
        "title": str,
        "type": str,
        "url": str,
    }

    ATTR_CREA = {
        "actions": list,
        "kind": str,
        "link": dict,
        "title": str,
        "type": str,
        "parent_resource": str,
        "url": str,
    }

    ATTR_MAP = {}

    def __init__(
        self,
        _id: str = None,
        actions: list = None,
        kind: str = None,
        link: dict = None,
        size: int = None,
        title: str = None,
        type: str = None,
        url: str = None,
        # implementation additional parameters
        parent_resource: str = None,
    ):
        """Link model."""

        # default values for the object attributes/properties
        self.__id = None
        self._actions = None
        self._kind = None
        self._link = None
        self._size = None
        self._title = None
        self._type = None
        self._url = None
        # additional parameters
        self.parent_resource = parent_resource

        # if values have been passed, so use them as objects attributes.
        # attributes are prefixed by an underscore '_'
        if _id is not None:
            self.__id = _id
        if actions is not None:
            self._actions = actions
        if kind is not None:
            self._kind = kind
        if link is not None:
            self._link = link
        if size is not None:
            self._size = size
        if title is not None:
            self._title = title
        if type is not None:
            self._type = type
        if url is not None:
            self._url = url

    # -- PROPERTIES --------------------------------------------------------------------
    # link UUID
    @property
    def _id(self) -> str:
        """Gets the id of this Link.

        :return: The id of this Link.
        :rtype: str
        """
        return self.__id

    @_id.setter
    def _id(self, _id: str):
        """Sets the id of this Link.

        :param str id: The id of this Link.
        """

        self.__id = _id

    # actions
    @property
    def actions(self) -> list:
        """Gets the actions of this Link.

        :return: The actions of this Link.
        :rtype: list
        """
        return self._actions

    @actions.setter
    def actions(self, actions: list):
        """Sets the actions of this Link.

        :param list actions: The actions of this Link.
        """

        self._actions = actions

    # kind
    @property
    def kind(self) -> str:
        """Gets the kind of this Link.

        :return: The kind of this Link.
        :rtype: str
        """
        return self._kind

    @kind.setter
    def kind(self, kind: str):
        """Sets the kind of this Link.

        :param str kind: The kind of this Link. Must be one of LINK_KIND_VALUES
        """

        # check kind value
        if kind not in LinkKinds.__members__:
            raise ValueError(
                "Link kind '{}' is not an accepted value. Must be one of: {}.".format(
                    kind, " | ".join([e.name for e in LinkKinds])
                )
            )

        self._kind = kind

    # link
    @property
    def link(self) -> dict:
        """Gets the associated link of this Link.

        :return: The associated link of this Link.
        :rtype: dict
        """
        return self._link

    @link.setter
    def link(self, link: dict):
        """Sets the associated link of this Link.

        :param dict link: The associated link of this Link.
        """

        self._link = link

    # size
    @property
    def size(self) -> int:
        """Gets the size of the hosted data.

        :return: The size of the hosted data.
        :rtype: int
        """
        return self._size

    # title
    @property
    def title(self) -> str:
        """Gets the title of this Link.

        :return: The title of this Link.
        :rtype: str
        """
        return self._title

    @title.setter
    def title(self, title: str):
        """Sets the title of this Link.

        :param str title: The title of this Link.
        """

        self._title = title

    # type
    @property
    def type(self) -> str:
        """Gets the type of this Link.

        :return: The type of this Link.
        :rtype: str
        """
        return self._type

    @type.setter
    def type(self, type: str):
        """Sets the type of this Link.

        :param str type: The type of this Link. Must be one of LINK_KIND_VALUES
        """

        # check type value
        if type not in LinkTypes.__members__:
            raise ValueError(
                "link type '{}' is not an accepted value. Must be one of: {}.".format(
                    type, " | ".join([e.name for e in LinkTypes])
                )
            )

        self._type = type

    # url
    @property
    def url(self) -> str:
        """Gets the url of this Link.

        :return: The url of this Link.
        :rurl: str
        """
        return self._url

    @url.setter
    def url(self, url: str):
        """Sets the url of this Link.

        :param str url: The url of this Link. Must be one of LINK_KIND_VALUES
        """

        self._url = url

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
        if issubclass(Link, dict):
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
        if issubclass(Link, dict):
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
        if not isinstance(other, Link):
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
    obj = Link()
