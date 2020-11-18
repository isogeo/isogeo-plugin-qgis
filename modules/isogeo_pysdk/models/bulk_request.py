# -*- coding: UTF-8 -*-
#! python3  # noqa E265

"""
    Isogeo API v1 - Model of Metadata bulk request

    See: https://github.com/isogeo/isogeo-api-py-minsdk/issues/133
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# standard library
import pprint

# other model
from ..enums import BulkActions, BulkTargets
from .metadata import Metadata


# #############################################################################
# ########## Classes ###############
# ##################################
class BulkRequest(object):
    """Bulk request used to perform batch operation add/remove/update on Isogeo resources (= metadatas)"""

    ATTR_TYPES = {"action": object, "model": int, "query": dict, "target": list}

    def __init__(
        self,
        action: str = None,
        model: int = None,
        query: dict = None,
        target: str = None,
    ):

        # default values for the object attributes/properties
        self._action = None
        self._model = None
        self._query = None
        self._target = None

        # if values have been passed, so use them as objects attributes.
        # attributes are prefixed by an underscore '_'
        if action is not None:
            self._action = action
        if model is not None:
            self._model = model
        if query is not None:
            self._query = query
        if target is not None:
            self._target = target

    # -- PROPERTIES --------------------------------------------------------------------
    # search target action
    @property
    def action(self) -> str:
        """Gets the abilities of this Bulk Request.

        :return: The abilities of this Bulk Request.
        :rtype: str
        """
        return self._action

    @action.setter
    def action(self, action: str):
        """Sets the action of this Bulk Request. \
            Must be one of the values of `isogeo_pysdk..enums.bulk_actions`.
        """

        # check if it's conformant with the enum
        if action not in BulkActions.__members__:
            raise ValueError(
                "'{}' is not an accepted value for 'action'. Must be one of: {}.".format(
                    action, " | ".join([e.name for e in BulkActions])
                )
            )

        self._action = action

    # search creation date
    @property
    def model(self) -> list:
        """Gets the created of this Bulk Request.

        :return: The created of this Bulk Request.
        :rtype: list
        """
        return self._model

    @model.setter
    def model(self, model: list):
        """Sets the model of this Bulk Request.

        :param list model: The model of this Bulk Request
        """

        self._model = model

    # search last modification date
    @property
    def query(self) -> dict:
        """Gets the modified of this Bulk Request.

        :return: The modified of this Bulk Request.
        :rtype: dict
        """
        return self._query

    @query.setter
    def query(self, query: dict):
        """Sets the query of this Bulk Request.

        :param query: The query of this Bulk Request.  # noqa: E501
        :type: object
        """

        self._query = query

    # search target tags
    @property
    def target(self) -> str:
        """Gets the tag of this Bulk Request.

        :return: The tag of this Bulk Request.
        :rtype: str
        """

        return self._target

    @target.setter
    def target(self, target: str):
        """Sets the target of this Bulk Request. \
            Must be one of the values of `isogeo_pysdk..enums.bulk_targets`.

        :param target: The target of this Bulk Request.  # noqa: E501
        :type: str
        """

        # check if it's conformant with the enum
        if target not in BulkTargets.__members__:
            raise ValueError(
                "'{}' is not an accepted value for 'target'. Must be one of: {}.".format(
                    target, " | ".join([e.name for e in BulkTargets])
                )
            )

        self._target = target

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
        if issubclass(BulkRequest, dict):
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
        if not isinstance(other, BulkRequest):
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
    test_sample = BulkRequest()
