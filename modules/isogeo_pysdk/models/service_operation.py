# -*- coding: UTF-8 -*-
#! python3  # noqa E265

"""
    Isogeo API v1 - Model of ServiceOperation entity

    See: http://help.isogeo.com/api/complete/index.html#definition-serviceOperation
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# standard library
import pprint

# submodels
# from isogeo_pysdk.models.resource import Resource as Metadata


# #############################################################################
# ########## Classes ###############
# ##################################
class ServiceOperation(object):
    """ServiceOperations are entities defining rules of data creation.

    :Example:

    .. code-block:: json

        {
            "_id": "string (uuid)",
            "mimeTypesIn": [
                "string"
            ],
            "mimeTypesOut": [
                "string"
            ],
            "name": "string",
            "url": "string",
            "verb": "string"
        }
    """

    ATTR_TYPES = {
        "_id": str,
        "mimeTypesIn": list,
        "mimeTypesOut": list,
        "name": str,
        "url": str,
        "verb": str,
    }

    ATTR_CREA = {"name": str, "verb": str}

    ATTR_MAP = {}

    def __init__(
        self,
        _id: str = None,
        mimeTypesIn: str = None,
        mimeTypesOut: str = None,
        name: str = None,
        url: str = None,
        verb: str = None,
        # additional parameters
        parent_resource: str = None,
    ):
        """ServiceOperation model."""

        # default values for the object attributes/properties
        self.__id = None
        self._mimeTypesIn = None
        self._mimeTypesOut = None
        self._name = None
        self._url = None
        self._verb = None
        # additional parameters
        self.parent_resource = parent_resource

        # if values have been passed, so use them as objects attributes.
        # attributes are prefixed by an underscore '_'
        if _id is not None:
            self.__id = _id
        if mimeTypesIn is not None:
            self._mimeTypesIn = mimeTypesIn
        if mimeTypesOut is not None:
            self._mimeTypesOut = mimeTypesOut
        if name is not None:
            self._name = name
        if url is not None:
            self._url = url
        if verb is not None:
            self._verb = verb
        # additional parameters
        if parent_resource is not None:
            self._parent_resource = parent_resource

    # -- PROPERTIES --------------------------------------------------------------------
    # service layer UUID
    @property
    def _id(self) -> str:
        """Gets the id of this ServiceOperation.

        :return: The id of this ServiceOperation.
        :rtype: str
        """
        return self.__id

    # service layer associated mimeTypesIn
    @property
    def mimeTypesIn(self) -> dict:
        """Gets the mimeTypesIn used for Isogeo filters of this ServiceOperation.

        :return: The mimeTypesIn of this ServiceOperation.
        :rtype: dict
        """
        return self._mimeTypesIn

    @mimeTypesIn.setter
    def mimeTypesIn(self, mimeTypesIn: dict):
        """Sets the mimeTypesIn used into Isogeo filters of this ServiceOperation.

        :param dict mimeTypesIn: the mimeTypesIn of this ServiceOperation.
        """

        self._mimeTypesIn = mimeTypesIn

    # mimeTypesOut
    @property
    def mimeTypesOut(self) -> str:
        """Gets the mimeTypesOut of this ServiceOperation.

        :return: The mimeTypesOut of this ServiceOperation.
        :rtype: str
        """
        return self._mimeTypesOut

    @mimeTypesOut.setter
    def mimeTypesOut(self, mimeTypesOut: str):
        """Sets the mimeTypesOut of this ServiceOperation.

        :param str mimeTypesOut: The mimeTypesOut of this ServiceOperation.
        """

        self._mimeTypesOut = mimeTypesOut

    # service layer name
    @property
    def name(self) -> str:
        """Gets the name used for Isogeo filters of this ServiceOperation.

        :return: The name of this ServiceOperation.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name: str):
        """Sets the name used into Isogeo filters of this ServiceOperation.

        :param str name: the name of this ServiceOperation.
        """

        self._name = name

    # url
    @property
    def url(self) -> list:
        """Gets the url of this ServiceOperation.

        :return: The url of this ServiceOperation.
        :rtype: list
        """
        return self._url

    @url.setter
    def url(self, url: list):
        """Sets the url of this ServiceOperation.

        :param list url: The url of this ServiceOperation.
        """

        self._url = url

    # verb
    @property
    def verb(self) -> list:
        """Gets the verb of this ServiceOperation.

        :return: The verb of this ServiceOperation.
        :rtype: list
        """
        return self._verb

    @verb.setter
    def verb(self, verb: list):
        """Sets the verb of this ServiceOperation.

        :param list verb: The verb of this ServiceOperation.
        """

        self._verb = verb

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
        if issubclass(ServiceOperation, dict):
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
        if issubclass(ServiceOperation, dict):
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
        if not isinstance(other, ServiceOperation):
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
    test_model = ServiceOperation()
    print(test_model.__dict__)
    print(test_model._id)
    print(test_model.__dict__.get("_id"))
    print(hasattr(test_model, "_id"))
    print(test_model.to_dict_creation())
    # print(test_model.to_str()
