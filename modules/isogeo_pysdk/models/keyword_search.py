# -*- coding: UTF-8 -*-
#! python3  # noqa E265

"""
    Isogeo API v1 - Model of Keyword search entity

    See: http://help.isogeo.com/api/complete/index.html#definition-search
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# standard library
import pprint


# #############################################################################
# ########## Classes ###############
# ##################################
class KeywordSearch(object):
    """Keyword searchs are entities used to organize and shares metadata of a workgroup.

    .. code-block:: json
    """

    """
    Attributes:
      ATTR_TYPES (dict): basic structure of search attributes. {"attribute name": "attribute type"}.
    """
    ATTR_TYPES = {"limit": int, "offset": int, "results": list, "total": int}

    def __init__(
        self,
        limit: int = None,
        offset: int = None,
        results: list = None,
        total: int = None,
    ):
        """keywords/search?

        model
        """

        # default values for the object attributes/properties
        self._limit = None
        self._offset = None
        self._results = None
        self._total = None

        # if values have been passed, so use them as objects attributes.
        # attributes are prefixed by an underscore '_'
        if limit is not None:
            self._limit = limit
        if offset is not None:
            self._offset = offset
        if results is not None:
            self._results = results
        if total is not None:
            self._total = total

    # -- PROPERTIES --------------------------------------------------------------------
    # page size
    @property
    def limit(self) -> int:
        """Gets the created of this Keyword search.

        :return: The created of this Keyword search.
        :rtype: str
        """
        return self._limit

    @limit.setter
    def limit(self, limit: int):
        """Sets the limit of this InlineResponse2001.

        :param int limit: The limit of this Keyword Search
        """

        self._limit = limit

    # pagination start
    @property
    def offset(self) -> int:
        """Gets the offset of this Keyword search.

        :return: The offset of this Keyword search.
        :rtype: int
        """
        return self._offset

    @offset.setter
    def offset(self, offset: int):
        """Sets the offset of this Keyword search.

        :param int offset: The id of this Keyword search.
        """

        self._offset = offset

    # search results tags
    @property
    def results(self) -> str:
        """Gets the tag of this Keyword search.

        :return: The tag of this Keyword search.
        :rtype: str
        """
        return self._results

    @results.setter
    def results(self, results):
        """Sets the results of this InlineResponse2001.

        :param results: The results of this InlineResponse2001.  # noqa: E501
        :type: list[Keyword]
        """

        self._results = results

    @property
    def total(self) -> str:
        """Gets the total of this Keyword search.

        :return: The total of this Keyword search.
        :rtype: str
        """
        return self._total

    @total.setter
    def total(self, total: str):
        """Sets the total of this Keyword search.

        :param str total: The total of this Keyword search.
        """

        self._total = total

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
        if issubclass(KeywordSearch, dict):
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
        if not isinstance(other, KeywordSearch):
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
    search = KeywordSearch()
