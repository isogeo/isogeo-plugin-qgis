# -*- coding: UTF-8 -*-
#! python3  # noqa E265

"""
    Isogeo API v1 - Model of ServiceLayer entity

    See: http://help.isogeo.com/api/complete/index.html#definition-serviceLayer
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
class ServiceLayer(object):
    """ServiceLayers are entities defining rules of data creation.

    :Example:

    .. code-block:: json

        {
            "_id": "string (uuid)",
            "id": "string",
            "mimeTypes": [
                "string"
            ],
            "titles": [
                {
                    "lang": "string",
                    "value": "string"
                }
            ]
        }
    """

    ATTR_TYPES = {
        "_id": str,
        "dataset": dict,
        "name": str,
        "mimeTypes": str,
        "titles": list,
    }

    ATTR_CREA = {"name": str, "titles": list}

    ATTR_MAP = {"name": "id"}

    def __init__(
        self,
        _id: str = None,
        dataset: dict = None,
        id: str = None,
        name: str = None,  # = id in API model but it's a reserved keyword in Python
        mimeTypes: str = None,
        titles: list = None,
        # additional parameters
        parent_resource: str = None,
    ):
        """ServiceLayer model."""

        # default values for the object attributes/properties
        self.__id = None
        self._dataset = None
        self._name = None
        self._mimeTypes = None
        self._titles = None
        # additional parameters
        self.parent_resource = parent_resource

        # if values have been passed, so use them as objects attributes.
        # attributes are prefixed by an underscore '_'
        if _id is not None:
            self.__id = _id
        if id is not None:
            self._name = id
        if dataset is not None:
            self._dataset = dataset
        if name is not None:
            self._name = name
        if mimeTypes is not None:
            self._mimeTypes = mimeTypes
        if titles is not None:
            self._titles = titles
        # additional parameters
        if parent_resource is not None:
            self._parent_resource = parent_resource

    # -- PROPERTIES --------------------------------------------------------------------
    # service layer UUID
    @property
    def _id(self) -> str:
        """Gets the id of this ServiceLayer.

        :return: The id of this ServiceLayer.
        :rtype: str
        """
        return self.__id

    # service layer associated dataset
    @property
    def dataset(self) -> dict:
        """Gets the dataset used for Isogeo filters of this ServiceLayer.

        :return: The dataset of this ServiceLayer.
        :rtype: dict
        """
        return self._dataset

    @dataset.setter
    def dataset(self, dataset: dict):
        """Sets the dataset used into Isogeo filters of this ServiceLayer.

        :param dict dataset: the dataset of this ServiceLayer.
        """

        self._dataset = dataset

    # service layer name
    @property
    def name(self) -> str:
        """Gets the name used for Isogeo filters of this ServiceLayer.

        :return: The name of this ServiceLayer.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name: str):
        """Sets the name used into Isogeo filters of this ServiceLayer.

        :param str name: the name of this ServiceLayer.
        """

        self._name = name

    # mimeTypes
    @property
    def mimeTypes(self) -> str:
        """Gets the mimeTypes of this ServiceLayer.

        :return: The mimeTypes of this ServiceLayer.
        :rtype: str
        """
        return self._mimeTypes

    @mimeTypes.setter
    def mimeTypes(self, mimeTypes: str):
        """Sets the mimeTypes of this ServiceLayer.

        :param str mimeTypes: The mimeTypes of this ServiceLayer.
        """

        self._mimeTypes = mimeTypes

    # titles
    @property
    def titles(self) -> list:
        """Gets the titles of this ServiceLayer.

        :return: The titles of this ServiceLayer.
        :rtype: list
        """
        return self._titles

    @titles.setter
    def titles(self, titles: list):
        """Sets the titles of this ServiceLayer.

        :param list titles: The titles of this ServiceLayer.
        """

        self._titles = titles

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
        if issubclass(ServiceLayer, dict):
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
        if issubclass(ServiceLayer, dict):
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
        if not isinstance(other, ServiceLayer):
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
    test_model = ServiceLayer()
    print(test_model.__dict__)
    print(test_model._id)
    print(test_model.__dict__.get("_id"))
    print(hasattr(test_model, "_id"))
    print(test_model.to_dict_creation())
    # print(test_model.to_str()
