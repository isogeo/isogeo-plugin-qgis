# -*- coding: UTF-8 -*-
#! python3  # noqa E265

"""
    Isogeo API v1 - Model of Event entity

    See: http://help.isogeo.com/api/complete/index.html#definition-event
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# standard library
import pprint

# submodules
from isogeo_pysdk.enums import EventKinds


# #############################################################################
# ########## Classes ###############
# ##################################
class Event(object):
    """Events are entities included as subresource into metadata for data history description.

    :Example:

    .. code-block:: json

        {
            '_id': string (uuid),
            'date': string (datetime),
            'description': string,
            'kind': string
        }
    """

    ATTR_TYPES = {
        "_id": str,
        "date": str,
        "description": str,
        "kind": str,
        "parent_resource": str,
    }

    ATTR_CREA = {"date": str, "description": str, "kind": str, "waitForSync": bool}

    ATTR_MAP = {}

    def __init__(
        self,
        _id: str = None,
        date: str = None,
        description: str = None,
        kind: str = None,
        parent_resource: str = None,
        waitForSync: bool = 1,
    ):
        """Event model."""

        # default values for the object attributes/properties
        self.__id = None
        self._date = None
        self._description = None
        self._kind = None
        # additional parameters
        self.parent_resource = parent_resource
        self.waitForSync = waitForSync

        # if values have been passed, so use them as objects attributes.
        # attributes are prefixed by an underscore '_'
        if _id is not None:
            self.__id = _id
        if date is not None:
            self._date = date
        if description is not None:
            self._description = description
        if kind is not None:
            self._kind = kind
        if parent_resource is not None:
            self._parent_resource = parent_resource
        if waitForSync is not None:
            self._waitForSync = waitForSync

    # -- PROPERTIES --------------------------------------------------------------------
    # event UUID
    @property
    def _id(self) -> str:
        """Gets the id of this Event.

        :return: The id of this Event.
        :rtype: str
        """
        return self.__id

    # date
    @property
    def date(self) -> str:
        """Gets the date of this Event.

        :return: The date of this Event.
        :rtype: str
        """
        return self._date

    @date.setter
    def date(self, date: str):
        """Sets the date of this Event.

        :param str date: The date of this Event.
        """

        self._date = date

    # description
    @property
    def description(self) -> str:
        """Gets the description of this Event.

        :return: The description of this Event.
        :rtype: str
        """
        return self._description

    @description.setter
    def description(self, description: str):
        """Sets the description of this Event.

        :param str description: The description of this Event. Accept markdown syntax.
        """

        self._description = description

    # kind
    @property
    def kind(self) -> str:
        """Gets the kind of this Event.

        :return: The kind of this Event.
        :rtype: str
        """
        return self._kind

    @kind.setter
    def kind(self, kind: str):
        """Sets the kind of this Event.

        :param str kind: The kind of this Event. Must be one of:

        - creation
        - publication
        - update
        """

        # check type value
        if kind not in EventKinds.__members__:
            raise ValueError(
                "Event kind '{}' is not an accepted value. Must be one of: {}.".format(
                    kind, " | ".join([e.name for e in EventKinds])
                )
            )

        self._kind = kind

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
        if issubclass(Event, dict):
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
        if issubclass(Event, dict):
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
        if not isinstance(other, Event):
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
    ct = Event()
