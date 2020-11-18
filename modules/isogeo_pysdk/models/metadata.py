# -*- coding: UTF-8 -*-
#! python3  # noqa E265

"""
    Isogeo API v1 - Model of Metadata (= Resource) entity

    See: http://help.isogeo.com/api/complete/index.html#definition-resource
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# standard library
from hashlib import sha256
import logging
import pprint
import re
import unicodedata

# package
from ..enums import MetadataTypes

# others models
from .workgroup import Workgroup


# #############################################################################
# ########## Globals ###############
# ##################################

logger = logging.getLogger(__name__)

# for slugified title
_regex_slugify_strip = re.compile(r"[^\w\s-]")
_regex_slugify_hyphenate = re.compile(r"[-\s]+")


# #############################################################################
# ########## Classes ###############
# ##################################
class Metadata(object):
    """Metadata are the main entities in Isogeo.

    :Example:

    .. code-block:: json


        {
            "_abilities": [
                "string"
            ],
            "_created": "string (date-time)",
            "_creator": {
                "_abilities": [
                "string"
                ],
                "_created": "string (date-time)",
                "_id": "string (uuid)",
                "_modified": "string (date-time)",
                "areKeywordsRestricted": "boolean",
                "canCreateMetadata": "boolean",
                "code": "string",
                "contact": {
                "_created": "string (date-time)",
                "_id": "string (uuid)",
                "_modified": "string (date-time)",
                "addressLine1": "string",
                "addressLine2": "string",
                "addressLine3": "string",
                "available": "string",
                "city": "string",
                "count": "integer (int32)",
                "countryCode": "string",
                "email": "string",
                "fax": "string",
                "hash": "string",
                "name": "string",
                "organization": "string",
                "phone": "string",
                "type": "string",
                "zipCode": "string"
                },
                "keywordsCasing": "string",
                "metadataLanguage": "string",
                "themeColor": "string"
            },
            "_id": "string (uuid)",
            "_modified": "string (date-time)",
            "abstract": "string",
            "bbox": [
                "number (double)"
            ],
            "collectionContext": "string",
            "collectionMethod": "string",
            "conditions": [
                {
                "_id": "string (uuid)",
                "description": "string",
                "license": {
                    "_id": "string (uuid)",
                    "content": "string",
                    "count": "integer (int32)",
                    "link": "string",
                    "name": "string"
                }
                }
            ],
            "contacts": [
                {
                "_id": "string (uuid)",
                "contact": {
                    "_created": "string (date-time)",
                    "_id": "string (uuid)",
                    "_modified": "string (date-time)",
                    "addressLine1": "string",
                    "addressLine2": "string",
                    "addressLine3": "string",
                    "available": "string",
                    "city": "string",
                    "count": "integer (int32)",
                    "countryCode": "string",
                    "email": "string",
                    "fax": "string",
                    "hash": "string",
                    "name": "string",
                    "organization": "string",
                    "phone": "string",
                    "type": "string",
                    "zipCode": "string"
                },
                "role": "string"
                }
            ],
            "context": "object",
            "coordinate-system": "object",
            "created": "string (date-time)",
            "distance": "number (double)",
            "editionProfile": "string",
            "encoding": "string",
            "envelope": "object",
            "features": "integer (int32)",
            "format": "string",
            "formatVersion": "string",
            "geometry": "string",
            "height": "integer (int32)",
            "keywords": [
                {}
            ]
        }
    """

    # -- ATTRIBUTES --------------------------------------------------------------------
    ATTR_TYPES = {
        "_abilities": list,
        "_created": str,
        "_creator": dict,
        "_id": str,
        "_modified": str,
        "abstract": str,
        "collectionContext": str,
        "collectionMethod": str,
        "conditions": list,
        "contacts": list,
        "coordinateSystem": dict,
        "created": str,
        "distance": float,
        "editionProfile": str,
        "encoding": str,
        "envelope": dict,
        "events": list,
        "featureAttributes": list,
        "features": int,
        "format": str,
        "formatVersion": str,
        "geometry": str,
        "keywords": list,
        "language": str,
        "layers": list,
        "limitations": list,
        "links": list,
        "modified": str,
        "name": str,
        "operations": list,
        "path": str,
        "precision": str,
        "published": str,
        "scale": int,
        "series": bool,
        "serviceLayers": list,
        "specifications": list,
        "tags": list,
        "title": str,
        "topologicalConsistency": str,
        "type": str,
        "updateFrequency": str,
        "validFrom": str,
        "validTo": str,
        "validityComment": str,
    }

    ATTR_CREA = {
        "abstract": str,
        "collectionContext": str,
        "collectionMethod": str,
        "distance": float,
        "editionProfile": str,
        "encoding": str,
        "envelope": dict,
        "features": int,
        "format": str,
        "formatVersion": str,
        "geometry": str,
        "language": str,
        "name": str,
        "path": str,
        "precision": str,
        "scale": int,
        "series": bool,
        "title": str,
        "topologicalConsistency": str,
        "type": str,
        "updateFrequency": str,
        "validFrom": str,
        "validTo": str,
        "validityComment": str,
    }

    ATTR_MAP = {
        "coordinateSystem": "coordinate-system",
        "featureAttributes": "feature-attributes",
    }

    # -- CLASS METHODS -----------------------------------------------------------------
    @classmethod
    def clean_attributes(cls, raw_object: dict):
        """Renames attributes which are incompatible with Python (hyphens...). See related issue:
        https://github.com/isogeo/isogeo-api-py-minsdk/issues/82.

        :param dict raw_object: metadata dictionary returned by a request.json()

        :returns: the metadata with correct attributes
        :rtype: Metadata
        """
        for k, v in cls.ATTR_MAP.items():
            raw_object[k] = raw_object.pop(v, [])
        return cls(**raw_object)

    # -- CLASS INSTANCIATION -----------------------------------------------------------

    def __init__(
        self,
        _abilities: list = None,
        _created: str = None,
        _creator: dict = None,
        _id: str = None,
        _modified: str = None,
        abstract: str = None,
        collectionContext: str = None,
        collectionMethod: str = None,
        conditions: list = None,
        contacts: list = None,
        coordinateSystem: dict = None,
        created: str = None,
        distance: float = None,
        editionProfile: str = None,
        encoding: str = None,
        envelope: dict = None,
        events: list = None,
        featureAttributes: list = None,
        features: int = None,
        format: str = None,
        formatVersion: str = None,
        geometry: str = None,
        keywords: list = None,
        language: str = None,
        layers: list = None,
        limitations: list = None,
        links: list = None,
        modified: str = None,
        name: str = None,
        operations: list = None,
        path: str = None,
        precision: str = None,
        published: str = None,
        scale: int = None,
        series: bool = None,
        serviceLayers: list = None,
        specifications: list = None,
        tags: list = None,
        title: str = None,
        topologicalConsistency: str = None,
        type: str = None,
        updateFrequency: str = None,
        validFrom: str = None,
        validTo: str = None,
        validityComment: str = None,
    ):
        """Metadata model."""

        # default values for the object attributes/properties
        self.__abilities = None
        self.__created = None
        self.__creator = None
        self.__id = None
        self.__modified = None
        self._abstract = None
        self._collectionContext = None
        self._collectionMethod = None
        self._conditions = None
        self._contacts = None
        self._coordinateSystem = None
        self._creation = None  # = created
        self._distance = None
        self._editionProfile = None
        self._encoding = None
        self._envelope = None
        self._events = None
        self._featureAttributes = None
        self._features = None
        self._format = None
        self._formatVersion = None
        self._geometry = None
        self._keywords = None
        self._language = None
        self._layers = None
        self._limitations = None
        self._links = None
        self._modification = None  # = modified
        self._name = None
        self._operations = None
        self._path = None
        self._precision = None
        self._published = None
        self._scale = None
        self._series = None
        self._serviceLayers = None
        self._specifications = None
        self._tags = None
        self._title = None
        self._topologicalConsistency = None
        self._type = None
        self._updateFrequency = None
        self._validFrom = None
        self._validTo = None
        self._validityComment = None

        # if values have been passed, so use them as objects attributes.
        # attributes are prefixed by an underscore '_'
        if _abilities is not None:
            self.__abilities = _abilities
        if _created is not None:
            self.__created = _created
        if _creator is not None:
            self.__creator = _creator
        if _id is not None:
            self.__id = _id
        if _modified is not None:
            self.__modified = _modified
        if abstract is not None:
            self._abstract = abstract
        if collectionContext is not None:
            self._collectionContext = collectionContext
        if collectionMethod is not None:
            self._collectionMethod = collectionMethod
        if conditions is not None:
            self._conditions = conditions
        if contacts is not None:
            self._contacts = contacts
        if coordinateSystem is not None:
            self._coordinateSystem = coordinateSystem
        if created is not None:
            self._creation = created
        if distance is not None:
            self._distance = distance
        if editionProfile is not None:
            self._editionProfile = editionProfile
        if encoding is not None:
            self._encoding = encoding
        if envelope is not None:
            self._envelope = envelope
        if events is not None:
            self._events = events
        if featureAttributes is not None:
            self._featureAttributes = featureAttributes
        if features is not None:
            self._features = features
        if format is not None:
            self._format = format
        if formatVersion is not None:
            self._formatVersion = formatVersion
        if geometry is not None:
            self._geometry = geometry
        if keywords is not None:
            self._keywords = keywords
        if language is not None:
            self._language = language
        if layers is not None:
            self._layers = layers
        if limitations is not None:
            self._limitations = limitations
        if links is not None:
            self._links = links
        if modified is not None:
            self._modification = modified
        if name is not None:
            self._name = name
        if operations is not None:
            self._operations = operations
        if path is not None:
            self._path = path
        if precision is not None:
            self._precision = precision
        if published is not None:
            self._published = published
        if scale is not None:
            self._scale = scale
        if serviceLayers is not None:
            self._serviceLayers = serviceLayers
        if specifications is not None:
            self._specifications = specifications
        if tags is not None:
            self._tags = tags
        if title is not None:
            self._title = title
        if topologicalConsistency is not None:
            self._topologicalConsistency = topologicalConsistency
        if type is not None:
            self._type = type
        if updateFrequency is not None:
            self._updateFrequency = updateFrequency
        if validFrom is not None:
            self._validFrom = validFrom
        if validTo is not None:
            self._validTo = validTo
        if validityComment is not None:
            self._validityComment = validityComment

    # -- PROPERTIES --------------------------------------------------------------------
    # abilities of the user related to the metadata
    @property
    def _abilities(self) -> list:
        """Gets the abilities of this Metadata.

        :return: The abilities of this Metadata.
        :rtype: list
        """
        return self.__abilities

    # _created
    @property
    def _created(self) -> str:
        """Gets the creation datetime of the Metadata. Datetime format is:
        `%Y-%m-%dT%H:%M:%S+00:00`.

        :return: The created of this Metadata.
        :rtype: str
        """
        return self.__created

    # _modified
    @property
    def _modified(self) -> str:
        """Gets the last modification datetime of this Metadata. Datetime format is:
        `%Y-%m-%dT%H:%M:%S+00:00`.

        :return: The modified of this Metadata.
        :rtype: str
        """
        return self.__modified

    # metadata owner
    @property
    def _creator(self) -> dict:
        """Gets the creator of this Metadata.

        :return: The creator of this Metadata.
        :rtype: dict
        """
        return self.__creator

    # metadata UUID
    @property
    def _id(self) -> str:
        """Gets the id of this Metadata.

        :return: The id of this Metadata.
        :rtype: str
        """
        return self.__id

    @_id.setter
    def _id(self, _id: str):
        """Sets the id of this Metadata.

        :param str id: The id of this Metadata.
        """

        self.__id = _id

    # metadata description
    @property
    def abstract(self) -> str:
        """Gets the abstract.

        :return: The abstract of this Metadata.
        :rtype: str
        """
        return self._abstract

    @abstract.setter
    def abstract(self, abstract: str):
        """Sets the abstract used into Isogeo filters of this Metadata.

        :param str abstract: the abstract of this Metadata.
        """

        self._abstract = abstract

    # collection context
    @property
    def collectionContext(self) -> str:
        """Gets the collectionContext of this Metadata.

        :return: The collectionContext of this Metadata.
        :rtype: str
        """
        return self._collectionContext

    @collectionContext.setter
    def collectionContext(self, collectionContext: str):
        """Sets the collection context of this Metadata.

        :param str collectionContext: The collection context of this Metadata.
        """

        self._collectionContext = collectionContext

    # collection method
    @property
    def collectionMethod(self) -> str:
        """Gets the collection method of this Metadata.

        :return: The collection method of this Metadata.
        :rtype: str
        """
        return self._collectionMethod

    @collectionMethod.setter
    def collectionMethod(self, collectionMethod: str):
        """Sets the collection method of this Metadata.

        :param str collectionMethod: the collection method to set. Accepts markdown.
        """

        self._collectionMethod = collectionMethod

    # CGUs
    @property
    def conditions(self) -> list:
        """Gets the conditions of this Metadata.

        :return: The conditions of this Metadata.
        :rtype: list
        """
        return self._conditions

    @conditions.setter
    def conditions(self, conditions: list):
        """Sets conditions of this Metadata.

        :param list conditions: conditions to be set
        """

        self._conditions = conditions

    # contacts
    @property
    def contacts(self) -> list:
        """Gets the contacts of this Metadata.

        :return: The contacts of this Metadata.
        :rtype: list
        """
        return self._contacts

    @contacts.setter
    def contacts(self, contacts: list):
        """Sets the  of this Metadata.

        :param list contacts: to be set
        """

        self._contacts = contacts

    # coordinateSystem
    @property
    def coordinateSystem(self) -> dict:
        """Gets the coordinateSystem of this Metadata.

        :return: The coordinateSystem of this Metadata.
        :rtype: dict
        """
        return self._coordinateSystem

    @coordinateSystem.setter
    def coordinateSystem(self, coordinateSystem: dict):
        """Sets the coordinate systems of this Metadata.

        :param dict coordinateSystem: to be set
        """

        self._coordinateSystem = coordinateSystem

    # created
    @property
    def created(self) -> str:
        """Gets the creation date of the data described by the Metadata. It's the equivalent of the
        `created` original attribute (renamed to avoid conflicts with the _created` one).

        Date format is: `%Y-%m-%dT%H:%M:%S+00:00`.

        :return: The creation of this Metadata.
        :rtype: str
        """
        return self._creation

    # distance
    @property
    def distance(self) -> str:
        """Gets the distance of this Metadata.

        :return: The distance of this Metadata.
        :rtype: str
        """
        return self._distance

    @distance.setter
    def distance(self, distance: str):
        """Sets the  of this Metadata.

        :param str distance: to be set
        """

        self._distance = distance

    # editionProfile
    @property
    def editionProfile(self) -> str:
        """Gets the editionProfile of this Metadata.

        :return: The editionProfile of this Metadata.
        :rtype: str
        """
        return self._editionProfile

    @editionProfile.setter
    def editionProfile(self, editionProfile: str):
        """Sets the  of this Metadata.

        :param str editionProfile: to be set
        """

        self._editionProfile = editionProfile

    # encoding
    @property
    def encoding(self) -> str:
        """Gets the encoding of this Metadata.

        :return: The encoding of this Metadata.
        :rtype: str
        """
        return self._encoding

    @encoding.setter
    def encoding(self, encoding: str):
        """Sets the  of this Metadata.

        :param str encoding: to be set
        """

        self._encoding = encoding

    # envelope
    @property
    def envelope(self) -> str:
        """Gets the envelope of this Metadata.

        :return: The envelope of this Metadata.
        :rtype: str
        """
        return self._envelope

    @envelope.setter
    def envelope(self, envelope: str):
        """Sets the  of this Metadata.

        :param str envelope: to be set
        """

        self._envelope = envelope

    # events
    @property
    def events(self) -> list:
        """Gets the events of this Metadata.

        :return: The events of this Metadata.
        :rtype: list
        """
        return self._events

    @events.setter
    def events(self, events: list):
        """Sets the  of this Metadata.

        :param list events: to be set
        """

        self._events = events

    # featureAttributes
    @property
    def featureAttributes(self) -> list:
        """Gets the featureAttributes of this Metadata.

        :return: The featureAttributes of this Metadata.
        :rtype: list
        """
        return self._featureAttributes

    @featureAttributes.setter
    def featureAttributes(self, featureAttributes: list):
        """Sets the  of this Metadata.

        :param list featureAttributes: to be set
        """

        self._featureAttributes = featureAttributes

    # features
    @property
    def features(self) -> int:
        """Gets the features of this Metadata.

        :return: The features of this Metadata.
        :rtype: int
        """
        return self._features

    @features.setter
    def features(self, features: int):
        """Sets the  of this Metadata.

        :param int features: to be set
        """

        self._features = features

    # format
    @property
    def format(self) -> str:
        """Gets the format of this Metadata.

        :return: The format of this Metadata.
        :rtype: str
        """
        return self._format

    @format.setter
    def format(self, format: str):
        """Sets the  of this Metadata.

        :param str format: to be set
        """

        self._format = format

    # formatVersion
    @property
    def formatVersion(self) -> str:
        """Gets the formatVersion of this Metadata.

        :return: The formatVersion of this Metadata.
        :rtype: str
        """
        return self._formatVersion

    @formatVersion.setter
    def formatVersion(self, formatVersion: str):
        """Sets the  of this Metadata.

        :param str formatVersion: to be set
        """

        self._formatVersion = formatVersion

    # geometry
    @property
    def geometry(self) -> str:
        """Gets the geometry of this Metadata.

        :return: The geometry of this Metadata.
        :rtype: str
        """
        return self._geometry

    @geometry.setter
    def geometry(self, geometry: str):
        """Sets the  of this Metadata.

        :param str geometry: to be set
        """

        self._geometry = geometry

    # keywords
    @property
    def keywords(self) -> str:
        """Gets the keywords of this Metadata.

        :return: The keywords of this Metadata.
        :rtype: str
        """
        return self._keywords

    @keywords.setter
    def keywords(self, keywords: str):
        """Sets the  of this Metadata.

        :param str keywords: to be set
        """

        self._keywords = keywords

    # language
    @property
    def language(self) -> str:
        """Gets the language of this Metadata.

        :return: The language of this Metadata.
        :rtype: str
        """
        return self._language

    @language.setter
    def language(self, language: str):
        """Sets the  of this Metadata.

        :param str language: to be set
        """

        self._language = language

    # layers
    @property
    def layers(self) -> list:
        """Gets the layers of this Metadata.

        :return: The layers of this Metadata.
        :rtype: list
        """
        return self._layers

    @layers.setter
    def layers(self, layers: list):
        """Sets the  of this Metadata.

        :param list layers: to be set
        """

        self._layers = layers

    # limitations
    @property
    def limitations(self) -> str:
        """Gets the limitations of this Metadata.

        :return: The limitations of this Metadata.
        :rtype: str
        """
        return self._limitations

    @limitations.setter
    def limitations(self, limitations: str):
        """Sets the  of this Metadata.

        :param str limitations: to be set
        """

        self._limitations = limitations

    # links
    @property
    def links(self) -> str:
        """Gets the links of this Metadata.

        :return: The links of this Metadata.
        :rtype: str
        """
        return self._links

    @links.setter
    def links(self, links: str):
        """Sets the  of this Metadata.

        :param str links: to be set
        """

        self._links = links

    # modification
    @property
    def modified(self) -> str:
        """Gets the last modification date of the data described by this Metadata.

        It's the equivalent of the `created` original attribute (renamed to avoid conflicts with the _created` one).

        :return: The modification of this Metadata.
        :rtype: str
        """
        return self._modification

    # name
    @property
    def name(self) -> str:
        """Gets the name of this Metadata.

        :return: The name of this Metadata.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name: str):
        """Sets technical name of the Metadata.

        :param str name: technical name this Metadata.
        """

        self._name = name

    # operations
    @property
    def operations(self) -> list:
        """Gets the operations of this Metadata.

        :return: The operations of this Metadata.
        :rtype: list
        """
        return self._operations

    @operations.setter
    def operations(self, operations: list):
        """Sets the  of this Metadata.

        :param list operations: to be set
        """

        self._operations = operations

    # path
    @property
    def path(self) -> str:
        """Gets the path of this Metadata.

        :return: The path of this Metadata.
        :rtype: str
        """
        return self._path

    @path.setter
    def path(self, path: str):
        """Sets the  of this Metadata.

        :param str path: to be set
        """

        self._path = path

    # precision
    @property
    def precision(self) -> str:
        """Gets the precision of this Metadata.

        :return: The precision of this Metadata.
        :rtype: str
        """
        return self._precision

    @precision.setter
    def precision(self, precision: str):
        """Sets the  of this Metadata.

        :param str precision: to be set
        """

        self._precision = precision

    # published
    @property
    def published(self) -> str:
        """Gets the published of this Metadata.

        :return: The published of this Metadata.
        :rtype: str
        """
        return self._published

    @published.setter
    def published(self, published: str):
        """Sets the  of this Metadata.

        :param str published: to be set
        """

        self._published = published

    # scale
    @property
    def scale(self) -> str:
        """Gets the scale of this Metadata.

        :return: The scale of this Metadata.
        :rtype: str
        """
        return self._scale

    @scale.setter
    def scale(self, scale: str):
        """Sets the  of this Metadata.

        :param str scale: to be set
        """

        self._scale = scale

    # series
    @property
    def series(self) -> str:
        """Gets the series of this Metadata.

        :return: The series of this Metadata.
        :rtype: str
        """
        return self._series

    @series.setter
    def series(self, series: str):
        """Sets the  of this Metadata.

        :param str series: to be set
        """

        self._series = series

    # serviceLayers
    @property
    def serviceLayers(self) -> list:
        """Gets the serviceLayers of this Metadata.

        :return: The serviceLayers of this Metadata.
        :rtype: list
        """
        return self._serviceLayers

    @serviceLayers.setter
    def serviceLayers(self, serviceLayers: list):
        """Sets the  of this Metadata.

        :param list serviceLayers: to be set
        """

        self._serviceLayers = serviceLayers

    # specifications
    @property
    def specifications(self) -> str:
        """Gets the specifications of this Metadata.

        :return: The specifications of this Metadata.
        :rtype: str
        """
        return self._specifications

    @specifications.setter
    def specifications(self, specifications: str):
        """Sets the  of this Metadata.

        :param str specifications: to be set
        """

        self._specifications = specifications

    # tags
    @property
    def tags(self) -> str:
        """Gets the tags of this Metadata.

        :return: The tags of this Metadata.
        :rtype: str
        """
        return self._tags

    @tags.setter
    def tags(self, tags: str):
        """Sets the  of this Metadata.

        :param str tags: to be set
        """

        self._tags = tags

    # title
    @property
    def title(self) -> str:
        """Gets the title of this Metadata.

        :return: The title of this Metadata.
        :rtype: str
        """
        return self._title

    @title.setter
    def title(self, title: str):
        """Sets the  of this Metadata.

        :param str title: to be set
        """

        self._title = title

    # topologicalConsistency
    @property
    def topologicalConsistency(self) -> str:
        """Gets the topologicalConsistency of this Metadata.

        :return: The topologicalConsistency of this Metadata.
        :rtype: str
        """
        return self._topologicalConsistency

    @topologicalConsistency.setter
    def topologicalConsistency(self, topologicalConsistency: str):
        """Sets the  of this Metadata.

        :param str topologicalConsistency: to be set
        """

        self._topologicalConsistency = topologicalConsistency

    # type
    @property
    def type(self) -> str:
        """Gets the type of this Metadata.

        :return: The type of this Metadata.
        :rtype: str
        """
        return self._type

    @type.setter
    def type(self, type: str):
        """Sets the type of this Metadata.

        :param str type: The type of this Metadata.
        """

        # check type value
        if type not in MetadataTypes.__members__:
            raise ValueError(
                "Metadata type '{}' is not an accepted value. Must be one of: {}.".format(
                    type, " | ".join([e.name for e in MetadataTypes])
                )
            )

        self._type = type

    # updateFrequency
    @property
    def updateFrequency(self) -> str:
        """Gets the updateFrequency of this Metadata.

        :return: The updateFrequency of this Metadata.
        :rtype: str
        """
        return self._updateFrequency

    @updateFrequency.setter
    def updateFrequency(self, updateFrequency: str):
        """Sets the  of this Metadata.

        :param str updateFrequency: to be set
        """

        self._updateFrequency = updateFrequency

    # validFrom
    @property
    def validFrom(self) -> str:
        """Gets the validFrom of this Metadata.

        :return: The validFrom of this Metadata.
        :rtype: str
        """
        return self._validFrom

    @validFrom.setter
    def validFrom(self, validFrom: str):
        """Sets the  of this Metadata.

        :param str validFrom: to be set
        """

        self._validFrom = validFrom

    # validTo
    @property
    def validTo(self) -> str:
        """Gets the validTo of this Metadata.

        :return: The validTo of this Metadata.
        :rtype: str
        """
        return self._validTo

    @validTo.setter
    def validTo(self, validTo: str):
        """Sets the  of this Metadata.

        :param str validTo: to be set
        """

        self._validTo = validTo

    # validityComment
    @property
    def validityComment(self) -> str:
        """Gets the validityComment of this Metadata.

        :return: The validityComment of this Metadata.
        :rtype: str
        """
        return self._validityComment

    @validityComment.setter
    def validityComment(self, validityComment: str):
        """Sets the  of this Metadata.

        :param str validityComment: to be set
        """

        self._validityComment = validityComment

    # -- SPECIFIC TO IMPLEMENTATION ----------------------------------------------------
    @property
    def groupName(self) -> str:
        """Shortcut to get the name of the workgroup which owns the Metadata."""
        if isinstance(self._creator, dict):
            return self._creator.get("contact").get("name")
        elif isinstance(self._creator, Workgroup):
            return self._creator.contact.get("name")
        else:
            return None

    @property
    def groupId(self) -> str:
        """Shortcut to get the UUID of the workgroup which owns the Metadata."""
        if isinstance(self._creator, dict):
            return self._creator.get("_id")
        elif isinstance(self._creator, Workgroup):
            return self._creator._id
        else:
            return None

    # -- METHODS -----------------------------------------------------------------------
    def admin_url(self, url_base: str = "https://app.isogeo.com") -> str:
        """Returns the administration URL (https://app.isogeo.com) for this metadata.

        :param str url_base: base URL of admin site. Defaults to: https://app.isogeo.com

        :rtype: str
        """
        if self._creator is None:
            logger.warning("Creator is required to build admin URL")
            return False

        creator_id = self._creator.get("_id")
        return "{}/groups/{}/resources/{}/".format(url_base, creator_id, self._id)

    def title_or_name(self, slugged: bool = False) -> str:
        """Gets the title of this Metadata or the name if there is no title. It can return a
        slugified value.

        :param bool slugged: slugify title. Defaults to `False`.

        :returns: the title or the name of this Metadata.
        :rtype: str
        """
        if self._title:
            title_or_name = self._title
        elif self._name:
            title_or_name = self._name
        else:
            logger.warning(
                "Metadata has no title nor name. So this method is useless..."
            )
            return None

        # slugify
        if slugged:
            title_or_name = (
                unicodedata.normalize("NFKD", title_or_name)
                .encode("ascii", "ignore")
                .decode("ascii")
            )
            title_or_name = _regex_slugify_strip.sub("", title_or_name).strip().lower()
            title_or_name = _regex_slugify_hyphenate.sub("-", title_or_name)

        return title_or_name

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
        if issubclass(Metadata, dict):
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
        if issubclass(Metadata, dict):
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
        if not isinstance(other, Metadata):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other) -> bool:
        """Returns true if both objects are not equal."""
        return not self == other

    def signature(
        self,
        included_attributes: tuple = (
            "coordinateSystem",
            "envelope",
            "features",
            "featureAttributes",
            "format",
            "geometry",
            "groupId",
            "name",
            "path",
            "series",
            "title",
            "type",
        ),
    ) -> str:
        """Calculate a hash cumulating certain attributes values. Useful to Scan or comparison operations.

        :param tuple included_attributes: object attributes to include in hash. Default: \
            {("coordinateSystem","envelope","features","featuresAttributes","format","geometry","groupId","name","path","series","title","type")})
        """
        # instanciate the hash
        hasher = sha256()

        # parse attributes
        for i in included_attributes:
            # because hash.update requires a
            if getattr(self, i):
                hasher.update(getattr(self, i).encode())

        return hasher.hexdigest()


# ##############################################################################
# ##### Stand alone program ########
# ##################################
if __name__ == "__main__":
    """standalone execution."""
    test_sample = Metadata(title="abcd123")
    print(test_sample.signature())
