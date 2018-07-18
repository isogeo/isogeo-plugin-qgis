# -*- coding: UTF-8 -*-
#!/usr/bin/env python
from __future__ import (absolute_import, unicode_literals)
# ----------------------------------------------------------------------------

"""
    Complementary set of tools to make some checks on requests to Isogeo API.
"""

# Created:      18/08/2017
# ---------------------------------------------------------------------------

# #############################################################################
# ########## Libraries #############
# ##################################

# Standard library
from collections import Counter
import logging
from six import string_types
import socket
from uuid import UUID
import warnings

# ##############################################################################
# ########## Globals ###############
# ##################################

FILTER_KEYS = {"action": [],
               "catalog": [],
               "contact:group": [],
               "contact:isogeo": [],
               "coordinate-system": [],
               "data-source": [],
               "format": [],
               "has-no": [],
               "keyword:isogeo": [],
               "keyword:inspire-theme": [],
               "license:group": [],
               "license:isogeo": [],
               "owner": [],
               "provider": [],
               "text": [],
               "type": []}

FILTER_ACTIONS = ("download",
                  "other",
                  "view"
                  )

FILTER_PROVIDERS = ("manual",
                    "auto"
                    )

FILTER_TYPES = ("dataset",
                "raster-dataset",
                "vector-dataset",
                "resource",
                "service"
                )

GEORELATIONS = ("contains",
                "disjoint",
                "equal",
                "intersects",
                "overlaps",
                "within"
                )

WG_KEYWORDS_CASING = ("capitalized",
                      "lowercase",
                      "mixedCase",
                      "uppercase",
                      )

EDIT_TABS = {"identification": ",".join(FILTER_TYPES),
             "history": ",".join(FILTER_TYPES),
             "geography": "dataset, raster-dataset, vector-dataset, service",
             "quality": "dataset, raster-dataset, vector-dataset, service",
             "attributes": "vector-dataset, series",
             "constraints": ",".join(FILTER_TYPES),
             "resources": ",".join(FILTER_TYPES),
             "contacts": ",".join(FILTER_TYPES),
             "advanced": ",".join(FILTER_TYPES),
             "metadata": ",".join(FILTER_TYPES),
             }

_SUBRESOURCES_MD = ("_creator",
                    "conditions",
                    "contacts",
                    "coordinate-system",
                    "events",
                    "feature-attributes",
                    "keywords",
                    "layers",
                    "limitations",
                    "links",
                    "operations",
                    "serviceLayers",
                    "specifications",
                    "tags",
                    )

_SUBRESOURCES_KW = ("count",
                    )

# ##############################################################################
# ########## Classes ###############
# ##################################


class IsogeoChecker(object):
    """Complementary set of tools to make some checks on requests
    to Isogeo API.
    """

    def __init__(self):
        super(IsogeoChecker, self).__init__()

    def check_internet_connection(self, remote_server="www.isogeo.com"):
        """Test if an internet connection is operational.
        Src: http://stackoverflow.com/a/20913928/2556577.

        :param str remote_server: remote server used to check
        """
        try:
            # see if we can resolve the host name -- tells us if there is
            # a DNS listening
            host = socket.gethostbyname(remote_server)
            # connect to the host -- tells us if it's reachable
            sock = socket.create_connection((host, 80), 2)
            sock.close()
            return True
        except Exception as e:
            logging.error(e)
            return False

    def check_bearer_validity(self, token, connect_mtd):
        """Check API Bearer token validity.

        Isogeo ID delivers authentication bearers which are valid during
        a certain time. So this method checks the validity of the token
        with a 30 mn anticipation limit, and renews it if necessary.
        See: http://tools.ietf.org/html/rfc6750#section-2

        FI: 24h = 86400 seconds, 30 mn = 1800, 5 mn = 300

        :param tuple token: auth bearer to check.
         Structure: (bearer, expiration_date)
        :param isogeo_pysdk.connect connect_mtd: method herited
         from Isogeo PySDK to get new bearer
        """
        if token[1] < 60:
            token = connect_mtd
            logging.debug("Token was about to expire, so has been renewed.")
        else:
            logging.debug("Token is still valid.")
            pass

        # end of method
        return token

    def check_api_response(self, response):
        """Check API response and raise exceptions if needed.

        :param requests.models.Response response: request response to check
        """
        # check response
        if response.status_code == 200:
            return True
        elif response.status_code >= 400:
            logging.error("{}: {} - {} - URL: {}"
                          .format(response.status_code,
                                  response.reason,
                                  response.json().get("error"),
                                  response.request.url))
            return False, response.status_code

    def check_request_parameters(self, parameters=dict):
        """Check parameters passed to avoid errors and help debug.

        :param dict response: search request parameters
        """
        # -- SEMANTIC QUERY ---------------------------------------------------
        li_args = parameters.get("q").split()
        logging.debug(li_args)

        # Unicity
        li_filters = [i.split(":")[0] for i in li_args]
        filters_count = Counter(li_filters)
        li_filters_must_be_unique = ("coordinate-system",
                                     "format",
                                     "owner",
                                     "type")
        for i in filters_count:
            if i in li_filters_must_be_unique and filters_count.get(i) > 1:
                raise ValueError("This query filter must be unique: {}"
                                 " and it occured {} times."
                                 .format(i, filters_count.get(i)))

        # dict
        dico_query = FILTER_KEYS.copy()
        for i in li_args:
            if i.startswith("action"):
                dico_query["action"].append(i.split(":")[1:][0])
                continue
            elif i.startswith("catalog"):
                dico_query["catalog"].append(i.split(":")[1:][0])
                continue
            elif i.startswith("contact") and i.split(":")[1] == "group":
                dico_query["contact:group"].append(i.split(":")[1:][1])
                continue
            elif i.startswith("contact"):
                dico_query["contact:isogeo"].append(i.split(":", 1)[1])
                continue
            elif i.startswith("coordinate-system"):
                dico_query["coordinate-system"].append(i.split(":")[1:][0])
                continue
            elif i.startswith("data-source"):
                dico_query["data-source"].append(i.split(":")[1:][0])
                continue
            elif i.startswith("format"):
                dico_query["format"].append(i.split(":")[1:][0])
                continue
            elif i.startswith("has-no"):
                dico_query["has-no"].append(i.split(":")[1:][0])
                continue
            elif i.startswith("keyword:isogeo"):
                dico_query["keyword:isogeo"].append(i.split(":")[1:][1])
                continue
            elif i.startswith("keyword:inspire-theme"):
                dico_query["keyword:inspire-theme"].append(i.split(":")[1:][1])
                continue
            elif i.startswith("license:isogeo"):
                dico_query["license:isogeo"].append(i.split(":")[1:][1:])
                continue
            elif i.startswith("license"):
                dico_query["license:group"].append(i.split(":", 1)[1:][0:])
                continue
            elif i.startswith("owner"):
                dico_query["owner"].append(i.split(":")[1:][0])
                continue
            elif i.startswith("provider"):
                dico_query["provider"].append(i.split(":")[1:][0])
                continue
            elif i.startswith("type"):
                dico_query["type"].append(i.split(":")[1:][0])
                continue
            else:
                logging.debug(i.split(":")[1], i.split(":")[1].isdigit())
                dico_query["text"].append(i)
                continue

        # Values
        dico_filters = {i.split(":")[0]: i.split(":")[1:] for i in li_args}
        if dico_filters.get("type", ("dataset",))[0].lower() not in FILTER_TYPES:
            raise ValueError("type value must be one of: {}"
                             .format(" | ".join(FILTER_TYPES)))
        elif dico_filters.get("action", ("download",))[0].lower() not in FILTER_ACTIONS:
            raise ValueError("action value must be one of: {}"
                             .format(" | ".join(FILTER_ACTIONS)))
        elif dico_filters.get("provider", ("manual",))[0].lower() not in FILTER_PROVIDERS:
            raise ValueError("provider value must be one of: {}"
                             .format(" | ".join(FILTER_PROVIDERS)))
        else:
            logging.debug(dico_filters)

        # -- GEOGRAPHIC -------------------------------------------------------
        in_box = parameters.get("box")
        in_geo = parameters.get("geo")
        # geometric relation
        in_rel = parameters.get("rel")
        if in_rel and in_box is None and in_geo is None:
            raise ValueError("'rel' should'nt be used without box or geo.")
        elif in_rel not in GEORELATIONS and in_rel is not None:
            raise ValueError("{} is not a correct value for 'georel'."
                             " Must be one of: {}."
                             .format(in_rel, " | ".join(GEORELATIONS)))

    def check_is_uuid(self, uuid_str):
        """Check if it's an Isogeo UUID handling specific form.

        :param str uuid_str: UUID string to check
        """
        # check uuid type
        if not isinstance(uuid_str, string_types):
            raise TypeError("'uuid_str' expected a str value.")
        else:
            pass
        # handle Isogeo specific UUID in XML exports
        if "isogeo:metadata" in uuid_str:
            uuid_str = "urn:uuid:{}".format(uuid_str.split(":")[-1])
        else:
            pass
        # test it
        try:
            uid = UUID(uuid_str)
            return uid.hex == uuid_str.replace('-', '')\
                                      .replace('urn:uuid:', '')
        except ValueError as e:
            logging.error("uuid ValueError. {} ({})  -- {}"
                          .format(type(uuid_str), uuid_str, e))
            return False

    def check_edit_tab(self, tab, md_type):
        """Check if asked tab is part of Isogeo web form and reliable
        with metadata type.

        :param str tab: tab to check. Must be one one of EDIT_TABS attribute
        :param str md_type: metadata type. Must be one one of FILTER_TYPES
        """
        # check parameters types
        if not isinstance(tab, string_types):
            raise TypeError("'tab' expected a str value.")
        else:
            pass
        if not isinstance(md_type, string_types):
            raise TypeError("'md_type' expected a str value.")
        else:
            pass
        # check parameters values
        if tab not in EDIT_TABS:
            raise ValueError("'{}' isn't a valid edition tab. "
                             "Available values: {}"
                             .format(tab, " | ".join(EDIT_TABS))
                             )
        else:
            pass
        if md_type not in FILTER_TYPES:
            raise ValueError("'{}' isn't a valid metadata type. "
                             "Available values: {}"
                             .format(tab, " | ".join(FILTER_TYPES))
                             )
        else:
            pass
        # check adequation tab/md_type
        if md_type not in EDIT_TABS.get(tab):
            raise ValueError("'{}'  isn't a valid tab for a '{}'' metadata."
                             " Only for these types: {}."
                             .format(tab, md_type, EDIT_TABS.get(tab))
                             )
        else:
            return True

    # -- FILTERS -------------------------------------------------------------
    def _check_filter_specific_md(self, specific_md):
        """Check if specific_md parameter is valid.

        :param list specific_md: list of specific metadata UUID to check
        """
        if isinstance(specific_md, list):
            if len(specific_md) > 0:
                # checking UUIDs and poping bad ones
                for md in specific_md:
                    if not self.check_is_uuid(md):
                        specific_md.remove(md)
                        logging.error("Metadata UUID is not correct: {}"
                                      .format(md))
                # joining survivors
                specific_md = ",".join(specific_md)
            else:
                specific_md = ""
        else:
            raise TypeError("'specific_md' expects a list")
        return specific_md

    def _check_filter_specific_tag(self, specific_tag):
        """Check if specific_tag parameter is valid.

        :param list specific_tag: list of specific tag to check
        """
        if isinstance(specific_tag, list):
            if len(specific_tag) > 0:
                specific_tag = ",".join(specific_tag)
            else:
                specific_tag = ""
        else:
            raise TypeError("'specific_tag' expects a list")
        return specific_tag

    def _check_filter_includes(self, includes, resource="metadata"):
        """Check if specific_resources parameter is valid.

        :param list includes: sub resources to check
        :param str resource: resource type to check sub resources.
         Must be one of: metadata | keyword.
        """
        # check resource parameter
        if resource == "metadata":
            ref_subresources = _SUBRESOURCES_MD
        elif resource == "keyword":
            ref_subresources = _SUBRESOURCES_KW
        else:
            raise ValueError("Must be one of: metadata | keyword.")

        # sub resources manager
        if isinstance(includes, string_types)\
           and includes.lower() == "all":
            includes = ",".join(ref_subresources)
        elif isinstance(includes, list):
            if len(includes) > 0:
                includes = ",".join(includes)
            else:
                includes = ""
        else:
            raise TypeError("'includes' expect a list or a str='all'")
        return includes

    def _check_subresource(self, subresource):
        """Check if specific_resources parameter is valid.

        :param str resource: subresource to check.
        """
        warnings.warn("subresource in URL is deprecated."
                      " Use _include mecanism instead.", DeprecationWarning)
        l_subresources = ("conditions", "contacts", "coordinate-system",
                          "events", "feature-attributes", "keywords",
                          "layers", "limitations", "links", "operations",
                          "specifications")
        if isinstance(subresource, string_types):
            if subresource in l_subresources:
                subresource = subresource
            elif subresource == "tags":
                subresource = "keywords"
                logging.debug("'tags' is an include not a subresource."
                              " Don't worry, it has be automatically renamed "
                              "into 'keywords' which is the correct subresource.")
            elif subresource == "serviceLayers":
                subresource = "layers"
                logging.debug("'serviceLayers' is an include not a subresource."
                              " Don't worry, it has be automatically renamed "
                              "into 'layers' which is the correct subresource.")
            else:
                raise ValueError("Invalid subresource. Must be one of: {}"
                                 .format("|".join(l_subresources)))
        else:
            raise TypeError("'subresource' expects a str")
        return subresource


# ##############################################################################
# ##### Stand alone program ########
# ##################################
if __name__ == '__main__':
    """Standalone execution."""
    checker = IsogeoChecker()
