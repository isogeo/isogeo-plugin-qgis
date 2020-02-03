# -*- coding: UTF-8 -*-
#! python3  # noqa E265

"""
    Isogeo API v1 - Model of Metadata bulk report

    See: https://github.com/isogeo/isogeo-api-py-minsdk/issues/133
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# standard library
import pprint

# other model
from isogeo_pysdk.models.bulk_request import BulkRequest


# #############################################################################
# ########## Classes ###############
# ##################################
class BulkReport(object):
    """Bulk report used to perform batch operation add/remove/update on Isogeo resources (= metadatas)"""

    ATTR_TYPES = {"ignored": dict, "request": BulkRequest}

    def __init__(self, ignored: dict = None, request: BulkRequest = None):

        # default values for the object attributes/properties
        self._ignored = None
        self._request = None

        # if values have been passed, so use them as objects attributes.
        # attributes are prefixed by an underscore '_'
        if ignored is not None:
            self._ignored = ignored
        if request is not None:
            self._request = request

    # -- PROPERTIES --------------------------------------------------------------------
    # search target ignored
    @property
    def ignored(self) -> dict:
        """Gets the ignored operations of this Bulk Request.

        :return: igno of this Bulk Request.
        :rtype: dict
        """
        return self._ignored

    @ignored.setter
    def ignored(self, ignored: dict):
        """Sets the ignored of this Bulk Request.
        """

        self._ignored = ignored

    # search creation date
    @property
    def request(self) -> BulkRequest:
        """Gets the created of this Bulk Request.

        :return: The created of this Bulk Request.
        :rtype: BulkRequest
        """
        return self._request

    @request.setter
    def request(self, request: BulkRequest):
        """Sets the request of this Bulk Request.

        :param BulkRequest request: The request of this Bulk Request
        """

        self._request = request

    # -- METHODS -----------------------------------------------------------------------
    def to_dict(self) -> dict:
        """Returns the request properties as a dict."""
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
        if issubclass(BulkReport, dict):
            for key, value in self.items():
                result[key] = value

        return result

    def to_str(self) -> str:
        """Returns the string representation of the request."""
        return pprint.pformat(self.to_dict())

    def __repr__(self) -> str:
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other) -> bool:
        """Returns true if both objects are equal."""
        if not isinstance(other, BulkReport):
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
    test_sample = BulkReport()
