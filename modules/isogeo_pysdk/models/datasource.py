# -*- coding: UTF-8 -*-
#! python3  # noqa E265

"""
    Isogeo API v1 - Model of Datasource entity

    See: http://help.isogeo.com/api/complete/index.html#definition-datasource
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# standard library
import pprint


# #############################################################################
# ########## Classes ###############
# ##################################
class Datasource(object):
    """Datasources are CSW client entry-points.

    :Example:

    .. code-block:: json

        {
            '_created': '2019-05-17T13:56:56.6162418+00:00',
            '_id': '2c891ce8692146c4901115a4232b13a2',
            '_modified': '2019-05-17T13:57:50.4434219+00:00',
            '_tag': 'data-source:2c891ce8692146c4901115a4232b13a2',
            'enabled': True,
            'lastSession': {
                '_created': '2019-05-17T13:58:06.5165889+00:00',
                '_id': 'ea99c37d809c4b1b9b4f257326ad1975',
                '_modified': '2019-05-17T13:58:28.5554966+00:00',
                'status': 'failed'
                },
            'location': 'http://ogc.geo-ide.developpement-durable.gouv.fr/csw/all-harvestable',
            'name': 'TEST - CSW entrypoint (datasource)',
            'resourceCount': 0,
            'sessions': [
                {
                    '_created': '2019-05-17T13:58:06.5165889+00:00',
                    '_id': 'ea99c37d809c4b1b9b4f257326ad1975',
                    '_modified': '2019-05-17T13:58:28.5554966+00:00',
                    'status': 'failed'
                }]
        }
    """

    ATTR_TYPES = {
        "_created": str,
        "_id": str,
        "_modified": str,
        "_tag": str,
        "enabled": bool,
        "lastSession": dict,
        "location": str,
        "name": str,
        "resourceCount": bool,
        "sessions": list,
    }

    ATTR_CREA = {"location": str, "name": str}

    ATTR_MAP = {}

    def __init__(
        self,
        _created: list = None,
        _id: str = None,
        _modified: str = None,
        _tag: str = None,
        enabled: bool = None,
        lastSession: dict = None,
        location: str = None,
        name: str = None,
        resourceCount: int = None,
        sessions: list = None,
    ):
        """Datasource model."""

        # default values for the object attributes/properties
        self.__created = None
        self.__id = None
        self.__modified = None
        self.__tag = None
        self._enabled = None
        self._lastSession = None
        self._location = None
        self._name = None
        self._resourceCount = None
        self._sessions = None

        # if values have been passed, so use them as objects attributes.
        # attributes are prefixed by an underscore '_'
        if _created is not None:
            self.__created = _created
        if _id is not None:
            self.__id = _id
        if _modified is not None:
            self.__modified = _modified
        if _tag is not None:
            self.__tag = _tag
        if enabled is not None:
            self._enabled = enabled
        if lastSession is not None:
            self._lastSession = lastSession
        if location is not None:
            self._location = location
        if name is not None:
            self._name = name
        if resourceCount is not None:
            self._resourceCount = resourceCount
        if sessions is not None:
            self._sessions = sessions

    # -- PROPERTIES --------------------------------------------------------------------
    # created of the user related to the metadata
    @property
    def _created(self) -> str:
        """Gets the created of this Catalog.

        :return: The created of this Catalog.
        :rtype: str
        """
        return self.__created

    # datasource UUID
    @property
    def _id(self) -> str:
        """Gets the id of this Datasource.

        :return: The id of this Datasource.
        :rtype: str
        """
        return self.__id

    # tag
    @property
    def _tag(self) -> str:
        """Gets the tag used for Isogeo filters of this Specification.

        :return: The tag of this Specification.
        :rtype: str
        """
        return self.__tag

    # _modified
    @property
    def _modified(self) -> str:
        """Gets the _modified of this Datasource.

        :return: The _modified of this Datasource.
        :rtype: str
        """
        return self.__modified

    # enabled of resource locationed to the datasource
    @property
    def enabled(self) -> bool:
        """Gets the enabled of this Datasource.

        :return: The enabled of this Datasource.
        :rtype: str
        """
        return self._enabled

    @enabled.setter
    def enabled(self, enabled: bool):
        """Sets the enabled of this Datasource.

        :param bool enabled: enabled of associated resources to the Datasource
        """

        self._enabled = enabled

    # lastSession
    @property
    def lastSession(self) -> dict:
        """Gets the lastSession of this Datasource.

        :return: The lastSession of this Datasource.
        :rtype: dict
        """
        return self._lastSession

    # location
    @property
    def location(self) -> str:
        """Gets the location (URL) of this Datasource.

        :return: The location (URL) of this Datasource.
        :rtype: str
        """
        return self._location

    @location.setter
    def location(self, location: str):
        """Sets the id of this Datasource.

        :param str XX: The id of this Datasource.
        """

        self._location = location

    # name
    @property
    def name(self) -> str:
        """Gets the name of this Datasource.

        :return: The name of this Datasource.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name: str):
        """Sets the name of this Datasource.

        :param str name: The name of this Datasource. Accept markdown syntax.
        """

        self._name = name

    # resourceCount
    @property
    def resourceCount(self) -> int:
        """Gets the resourceCount of this Datasource.

        :return: The resourceCount of this Datasource.
        :rtype: Workgroup
        """
        return self._resourceCount

    @resourceCount.setter
    def resourceCount(self, resourceCount: int):
        """Sets the resourceCount of this Datasource.

        :param int resourceCount: The resourceCount of this Datasource. Accept markdown syntax.
        """

        self._resourceCount = resourceCount

    # sessions
    @property
    def sessions(self) -> list:
        """Gets the sessions of this Datasource.

        :return: The sessions of this Datasource.
        :rtype: Workgroup
        """
        return self._sessions

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
        if issubclass(Datasource, dict):
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
        if issubclass(Datasource, dict):
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
        if not isinstance(other, Datasource):
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
    atasource = Datasource(
        name="Datasource Test", _modified="Test datasource _modified"
    )
    print(atasource)
