# -*- coding: UTF-8 -*-
#! python3  # noqa E265

"""
    Isogeo API v1 - Model of Conformity entity

    See: http://help.isogeo.com/api/complete/index.html#definition-resourceConformity
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# standard library
import pprint

# others related models
from isogeo_pysdk.models import Specification


# #############################################################################
# ########## Classes ###############
# ##################################
class Conformity(object):
    """Conformity is an entity defining if a data respects a specification. It's a quality
    indicator. It's mainly composed by a specification and a boolean.

    :param str _id: object UUID
    :param bool conformant: conformity with the specification
    :param dict specification: specification object or dict linked to the conformity
    :param str parent_resource: UUID of the metadata containing the conformity

    :Example:

    .. code-block:: json

        {
            "conformant": "bool",
            "specification": "string",
        }
    """

    ATTR_TYPES = {
        "conformant": bool,
        "specification": Specification,
        "parent_resource": str,
    }

    ATTR_CREA = {"conformant": "bool", "specification": Specification}

    ATTR_MAP = {}

    def __init__(
        self,
        conformant: bool = None,
        specification: dict or Specification = None,
        # specific implementation
        parent_resource: str = None,
    ):

        # default values for the object attributes/properties
        self._conformant = None
        self._specification = None
        self._parent_resource = None

        # if values have been passed, so use them as objects attributes.
        # attributes are prefixed by an underscore '_'
        if conformant is not None:
            self._conformant = conformant
        if specification is not None and isinstance(specification, Specification):
            self._specification = specification
        if specification is not None and isinstance(specification, dict):
            self._specification = Specification(**specification)
        if parent_resource is not None:
            self._parent_resource = parent_resource

    # -- PROPERTIES --------------------------------------------------------------------
    # conformant
    @property
    def conformant(self) -> bool:
        """Gets the conformant status.

        :return: The conformant status
        :rtype: bool
        """
        return self._conformant

    @conformant.setter
    def conformant(self, conformant: bool):
        """Sets the conformant status.

        :param bool conformant: The conformant status for the specification.
        """

        self._conformant = conformant

    @property
    def specification(self) -> Specification:
        """Gets the specification of this Conformity.

        :return: The specification of this Conformity.
        :rtype: Specification
        """
        return self._specification

    @specification.setter
    def specification(self, specification: dict or Specification):
        """Sets the specification of this Conformity.

        :param dict specification: The specification of this Conformity.
        """
        if isinstance(specification, Specification):
            self._specification = specification
        elif isinstance(specification, dict):
            self._specification = Specification(**specification)
        else:
            self._specification = specification
            raise Warning(
                "Invalid specification parameter ({}) to set as specification for this conformity.".format(
                    specification
                )
            )

    # parent metadata
    @property
    def parent_resource(self):
        """Gets the parent_resource of this Conformity.

        :return: The parent_resource of this Conformity.
        :rtype: UUID
        """
        return self._parent_resource

    @parent_resource.setter
    def parent_resource(self, parent_resource_UUID):
        """Sets the parent metadata UUID of this Conformity.

        :return: The parent_resource of this Conformity.
        :rtype: UUID
        """
        self._parent_resource = parent_resource_UUID

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
        if issubclass(Conformity, dict):
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
        if issubclass(Conformity, dict):
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
        if not isinstance(other, Conformity):
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
    fixture = Conformity(conformant=1, specification=Specification())
    print(fixture)
