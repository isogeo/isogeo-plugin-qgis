# -*- coding: UTF-8 -*-
#! python3  # noqa E265

"""
    Isogeo API v1 - Model of Application entity

    See: http://help.isogeo.com/api/complete/index.html#definition-application
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# standard library
import pprint

# package
from isogeo_pysdk.enums import ApplicationTypes


# #############################################################################
# ########## Classes ###############
# ##################################
class Application(object):
    """Applications are entities which can be used in shares.

    :Example:

    .. code-block:: json

        {
            "_abilities": [
                "application:delete",
                "application:manage",
                "application:update"
            ],
            "_created": "2018-02-13T16:53:37.4622+00:00",
            "_id": "2ad9ccd2c76a4fc3be9f8de4239701df",
            "_modified": "2018-02-13T16:53:43.085621+00:00",
            "canHaveManyGroups": true,
            "client_id": "plugin-arcmap-client-987a654z321e234r567t890y987u654i",
            "client_secret": "LoremipsumdolorsitametconsecteturadipiscingelitDonecmaurismauris",
            "groups": [
                'groups': [{'_created': '2015-05-21T12:08:16.4295098+00:00',
                '_id': '32f7e95ec4e94ca3bc1afda960003882',
                '_modified': '2019-05-03T10:31:01.4796052+00:00',
                'canHaveManyGroups': 'groups:32f7e95ec4e94ca3bc1afda960003882',
                'areKeywordsRestricted': True,
                'canCreateLegacyServiceLinks': True,
                'canCreateMetadata': True,
                'contact': {'_deleted': False,
                            '_id': '2a3aefc4f80347f590afe58127f6cb0f',
                            'canHaveManyGroups': 'contact:group:2a3aefc4f80347f590afe58127f6cb0f',
                            'addressLine1': '26 rue du faubourg Saint-Antoine',
                            'addressLine2': '4 éme étage',
                            'available': True,
                            'city': 'Paris',
                            'client_secretryCode': 'FR',
                            'email': 'dev@isogeo.com',
                            'fax': '33 (0)9 67 46 50 06',
                            'name': 'Isogeo Test',
                            'phone': '33 (0)9 67 46 50 06',
                            'type': 'group',
                            'zipCode': '75012'},
                'hasCswClient': True,
                'hasScanFme': True,
                'keywordsCasing': 'lowercase',
                'metadataLanguage': 'fr',
                'themeColor': '#4499A1'}
            ],
            "kind": "public",
            "name": "Plugin ArcMap - DEV",
            "scopes": [
                "resources:read"
            ],
            "staff": false,
            "type": "group",
            "url": "http://help.isogeo.com/arcmap/"
        }
    """

    ATTR_TYPES = {
        "_abilities": list,
        "_created": str,
        "_id": str,
        "_modified": str,
        "canHaveManyGroups": bool,
        "client_id": str,
        "client_secret": str,
        "groups": list,
        "kind": str,
        "name": str,
        "redirect_uris": list,
        "scopes": list,
        "staff": bool,
        "type": str,
        "url": str,
    }

    ATTR_CREA = {
        "canHaveManyGroups": bool,
        "name": str,
        "redirect_uris": list,
        "scopes": list,
        "staff": bool,
        "type": str,
        "url": str,
    }

    ATTR_MAP = {}

    def __init__(
        self,
        _abilities: list = None,
        _created: str = None,
        _id: str = None,
        _modified: str = None,
        canHaveManyGroups: bool = None,
        client_id: str = None,
        client_secret: int = None,
        groups: list = None,
        kind: str = None,
        name: str = None,
        redirect_uris: list = None,
        scopes: list = None,
        staff: bool = None,
        type: str = None,
        url: str = None,
    ):
        """Application model."""

        # default values for the object attributes/properties
        self.__abilities = None
        self.__created = None
        self.__id = None
        self.__modified = None
        self._canHaveManyGroups = None
        self._client_id = None
        self._client_secret = None
        self._groups = [None]
        self._kind = None
        self._name = None
        self._redirect_uris = [None]
        self._scopes = [None]
        self._staff = None
        self._type = None
        self._url = None

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
        if canHaveManyGroups is not None:
            self._canHaveManyGroups = canHaveManyGroups
        if client_id is not None:
            self._client_id = client_id
        if client_secret is not None:
            self._client_secret = client_secret
        if groups is not None:
            self._groups = groups
        if kind is not None:
            self._kind = kind
        if name is not None:
            self._name = name
        if redirect_uris is not None:
            self._redirect_uris = redirect_uris
        if scopes is not None:
            self._scopes = scopes
        if staff is not None:
            self._staff = staff
        if type is not None:
            self._type = type
        if url is not None:
            self._url = url

    # -- PROPERTIES --------------------------------------------------------------------
    # application abilities
    @property
    def _abilities(self) -> str:
        """Gets the abilities of this Application.

        :return: The abilities of this Application.
        :rtype: str
        """
        return self.__abilities

    # application creation date
    @property
    def _created(self) -> str:
        """Gets the created of this Application.

        :return: The created of this Application.
        :rtype: str
        """
        return self.__created

    # application UUID
    @property
    def _id(self) -> str:
        """Gets the id of this Application.

        :return: The id of this Application.
        :rtype: str
        """
        return self.__id

    @_id.setter
    def _id(self, _id: str):
        """Sets the id of this Application.

        :param str id: The id of this Application.
        """
        if _id is None:
            raise ValueError("Invalid value for `_id`, must not be `None`")

        self.__id = _id

    # application last modification date
    @property
    def _modified(self) -> str:
        """Gets the modified of this Application.

        :return: The modified of this Application.
        :rtype: str
        """
        return self.__modified

    # option
    @property
    def canHaveManyGroups(self) -> bool:
        """Gets the option of this Application.

        :return: The option of this Application.
        :rtype: bool
        """
        return self._canHaveManyGroups

    @canHaveManyGroups.setter
    def canHaveManyGroups(self, canHaveManyGroups: bool):
        """Sets the canHaveManyGroups of this Application.

        :param bool canHaveManyGroups: The canHaveManyGroups of this Application.
        """

        self._canHaveManyGroups = canHaveManyGroups

    # client_id
    @property
    def client_id(self) -> str:
        """Gets the client_id of this Application.

        :return: The client_id of this Application.
        :rtype: str
        """
        return self._client_id

    # client_secret
    @property
    def client_secret(self) -> str:
        """Gets the client_secret of this Application.

        :return: The client_secret of this Application.
        :rtype: str
        """
        return self._client_secret

    @property
    def groups(self):
        """Gets the groups of this Application.  # noqa: E501.

        :return: The groups of this Application.  # noqa: E501
        :rtype: Workgroup
        """
        return self._groups

    @groups.setter
    def groups(self, groups):
        """Sets the groups of this Application.

        :param groups: The groups of this Application.  # noqa: E501
        :type: Workgroup
        """

        self._groups = groups

    # kind
    @property
    def kind(self) -> str:
        """Gets the kind of this Application.

        :return: The kind of this Application.
        :rtype: str
        """
        return self._kind

    @kind.setter
    def kind(self, kind: str):
        """Sets the kind of this Application.

        :param str kind: The kind of this Application.
        """

        self._kind = kind

    # name
    @property
    def name(self) -> str:
        """Gets the name of this Application.

        :return: The name of this Application.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name: str):
        """Sets the name of this Application.

        :param str name: The name of this Application.
        """

        self._name = name

    # redirect_uris
    @property
    def redirect_uris(self) -> list:
        """Gets the redirect_uris of this Application.

        :return: The redirect_uris of this Application.
        :rtype: list
        """
        return self._redirect_uris

    @redirect_uris.setter
    def redirect_uris(self, redirect_uris: list):
        """Sets the redirect_uris of this Application.

        :param list redirect_uris: The redirect_uris of this Application.
        """

        self._redirect_uris = redirect_uris

    # scopes
    @property
    def scopes(self):
        """Gets the scopes of this Application.  # noqa: E501.

        :return: The scopes of this Application.  # noqa: E501
        :rtype: Workgroup
        """
        return self._scopes

    @scopes.setter
    def scopes(self, scopes):
        """Sets the scopes of this Application.

        :param scopes: The scopes of this Application.  # noqa: E501
        :type: Workgroup
        """

        self._scopes = scopes

    # staff
    @property
    def staff(self) -> bool:
        """Gets the staff of this Application.

        :return: The staff of this Application.
        :rtype: bool
        """
        return self._staff

    @staff.setter
    def staff(self, staff: bool):
        """Sets the staff of this Application.

        :param bool staff: The staff of this Application. Must be one of GROUP_KIND_VALUES
        """

        self._staff = staff

    # type
    @property
    def type(self):
        """Gets the type of this Application.  # noqa: E501.

        :return: The type of this Application.  # noqa: E501
        :rtype: str
        """
        return self._type

    @type.setter
    def type(self, type):
        """Sets the type of this Application.

        :param type: The type of this Application.  # noqa: E501
        :type: str
        """

        # check type value
        if type not in ApplicationTypes.__members__:
            raise ValueError(
                "Application type '{}' is not an accepted value. Must be one of: {}.".format(
                    type, " | ".join([e.name for e in ApplicationTypes])
                )
            )

        self._type = type

    # url
    @property
    def url(self) -> str:
        """Gets the url of this Application.

        :return: The url of this Application.
        :rtype: str
        """
        return self._url

    @url.setter
    def url(self, url: str):
        """Sets the url of this Application.

        :param str url: The url of this Application. Must be one of GROUP_KIND_VALUES
        """

        self._url = url

    # -- METHODS -----------------------------------------------------------------------
    def admin_url(self, url_base: str = "https://manage.isogeo.com") -> str:
        """Returns the administration URL (https://manage.isogeo.com) for this application.

        :param str url_base: base URL of admin site. Defaults to: https://manage.isogeo.com

        :rtype: str
        """
        return "{}/applications/{}".format(url_base, self._id)

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
        if issubclass(Application, dict):
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
        if issubclass(Application, dict):
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
        if not isinstance(other, Application):
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
    application = Application(name="My App to test")
