# -*- coding: UTF-8 -*-
#! python3
# ----------------------------------------------------------------------------

"""
    Complementary set of utils to use with Isogeo API.
"""

# ---------------------------------------------------------------------------

# #############################################################################
# ########## Libraries #############
# ##################################

# Standard library
import base64
import json
import logging
import quopri
import re
import uuid
from configparser import ConfigParser
from os import path
from urllib.parse import urlparse

# 3rd party
import requests

# modules
try:
    from . import checker
except (ImportError, ValueError, SystemError):
    import checker

# ##############################################################################
# ########## Globals ###############
# ##################################

checker = checker.IsogeoChecker()

# ##############################################################################
# ########## Classes ###############
# ##################################


class IsogeoUtils(object):
    """Complementary set of utilitary methods and functions to make it easier
    using Isogeo API.
    """

    API_URLS = {"prod": "api", "qa": "api.qa"}

    APP_URLS = {
        "prod": "https://app.isogeo.com",
        "qa": "https://qa-isogeo-app.azurewebsites.net",
    }

    CSW_URLS = {
        "prod": "https://app.isogeo.com",
        "qa": "http://services.api.qa.isogeo.com",
    }

    MNG_URLS = {
        "prod": "https://manage.isogeo.com",
        "qa": "https://qa-isogeo-manage.azurewebsites.net",
    }

    OC_URLS = {
        "prod": "https://open.isogeo.com",
        "qa": "https://qa-isogeo-open.azurewebsites.net",
    }

    WEBAPPS = {
        "csw_getcap": {
            "args": ("share_id", "share_token"),
            "url": "https://services.api.isogeo.com/ows/s/"
            "{share_id}/{share_token}?service=CSW"
            "&version=2.0.2&request=GetCapabilities",
        },
        "csw_getrec": {
            "args": ("md_uuid_urn", "share_id", "share_token"),
            "url": "https://services.api.isogeo.com/ows/s/"
            "{share_id}/{share_token}?service=CSW"
            "&version=2.0.2&request=GetRecordById"
            "&id={md_uuid_urn}&elementsetname=full"
            "&outputSchema=http://www.isotc211.org/2005/gmd",
        },
        "csw_getrecords": {  # https://github.com/isogeo/isogeo-api-py-minsdk/issues/44
            "args": ("share_id", "share_token"),
            "url": "https://services.api.isogeo.com/ows/s/"
            "{share_id}/{share_token}?service=CSW"
            "&version=2.0.2&request=GetRecords&ResultType=results"
            "&ElementSetName=brief&maxRecords=20"
            "&OutputFormat=application/xml"
            "&OutputSchema=http://www.opengis.net/cat/csw/2.0.2"
            "&namespace=xmlns(csw=http://www.opengis.net/cat/csw/2.0.2)"
            "&TypeNames=csw:Record&startPosition=1",
        },
        "oc": {
            "args": ("md_id", "share_id", "share_token"),
            "url": "https://open.isogeo.com/s/{share_id}" "/{share_token}/r/{md_id}",
        },
        "pixup_portal": {
            "args": ("md_id", "portal_url"),
            "url": "http://{portal_url}/?muid={md_id}",
        },
    }

    def __init__(self, proxies: dict = dict()):
        """Instanciate IsogeoUtils module.

        :param dict proxies: dictionary of proxy settings as described in
         requests. See: http://docs.python-requests.org/en/master/user/advanced/#proxies
        """
        self.platform, self.api_url, self.app_url, self.csw_url, self.mng_url, self.oc_url, self.ssl = (
            self.set_base_url()
        )
        self.proxies = proxies
        super(IsogeoUtils, self).__init__()

    def set_base_url(self, platform: str = "prod"):
        """Set Isogeo base URLs according to platform.

        :param str platform: platform to use. Options:

          * prod [DEFAULT]
          * qa
          * int
        """
        platform = platform.lower()
        self.platform = platform
        if platform == "prod":
            ssl = True
            logging.debug("Using production platform.")
        elif platform == "qa":
            ssl = False
            logging.debug("Using Quality Assurance platform (reduced perfs).")
        else:
            logging.error(
                "Platform must be one of: {}".format(" | ".join(self.API_URLS.keys()))
            )
            raise ValueError(
                3,
                "Platform must be one of: {}".format(" | ".join(self.API_URLS.keys())),
            )
        # method ending
        return (
            platform.lower(),
            self.API_URLS.get(platform),
            self.APP_URLS.get(platform),
            self.CSW_URLS.get(platform),
            self.MNG_URLS.get(platform),
            self.OC_URLS.get(platform),
            ssl,
        )

    def convert_uuid(self, in_uuid: str = str, mode: bool = 0):
        """Convert a metadata UUID to its URI equivalent. And conversely.

        :param str in_uuid: UUID or URI to convert
        :param int mode: conversion direction. Options:

          * 0 to HEX
          * 1 to URN (RFC4122)
          * 2 to URN (Isogeo specific style)

        """
        # parameters check
        if not isinstance(in_uuid, str):
            raise TypeError("'in_uuid' expected a str value.")
        else:
            pass
        if not checker.check_is_uuid(in_uuid):
            raise ValueError("{} is not a correct UUID".format(in_uuid))
        else:
            pass
        if not isinstance(mode, int):
            raise TypeError("'mode' expects an integer value")
        else:
            pass
        # handle Isogeo specific UUID in XML exports
        if "isogeo:metadata" in in_uuid:
            in_uuid = "urn:uuid:{}".format(in_uuid.split(":")[-1])
            logging.debug("Isogeo UUUID URN spotted: {}".format(in_uuid))
        else:
            pass
        # operate
        if mode == 0:
            return uuid.UUID(in_uuid).hex
        elif mode == 1:
            return uuid.UUID(in_uuid).urn
        elif mode == 2:
            urn = uuid.UUID(in_uuid).urn
            return "urn:isogeo:metadata:uuid:{}".format(urn.split(":")[2])
        else:
            raise ValueError("'mode' must be  one of: 0 | 1 | 2")

    def encoded_words_to_text(self, in_encoded_words: str):
        """Pull out the character set, encoding, and encoded text from the input
        encoded words. Next, it decodes the encoded words into a byte string,
        using either the quopri module or base64 module as determined by the
        encoding. Finally, it decodes the byte string using the
        character set and returns the result.

        See:

        - https://github.com/isogeo/isogeo-api-py-minsdk/issues/32
        - https://dmorgan.info/posts/encoded-word-syntax/

        :param str in_encoded_words: base64 or quori encoded character string.
        """
        # handle RFC2047 quoting
        if '"' in in_encoded_words:
            in_encoded_words = in_encoded_words.strip('"')
        # regex
        encoded_word_regex = r"=\?{1}(.+)\?{1}([B|Q])\?{1}(.+)\?{1}="
        # pull out
        try:
            charset, encoding, encoded_text = re.match(
                encoded_word_regex, in_encoded_words
            ).groups()
        except AttributeError:
            logging.debug("Input text was not encoded into base64 or quori")
            return in_encoded_words

        # decode depending on encoding
        if encoding == "B":
            byte_string = base64.b64decode(encoded_text)
        elif encoding == "Q":
            byte_string = quopri.decodestring(encoded_text)
        return byte_string.decode(charset)

    def get_isogeo_version(self, component: str = "api", prot: str = "https"):
        """Get Isogeo components versions. Authentication not required.

        :param str component: which platform component. Options:

          * api [default]
          * db
          * app

        """
        # which component
        if component == "api":
            version_url = "{}://v1.{}.isogeo.com/about".format(prot, self.api_url)
        elif component == "db":
            version_url = "{}://v1.{}.isogeo.com/about/database".format(
                prot, self.api_url
            )
        elif component == "app" and self.platform == "prod":
            version_url = "https://app.isogeo.com/about"
        elif component == "app" and self.platform == "qa":
            version_url = "https://qa-isogeo-app.azurewebsites.net/about"
        else:
            raise ValueError(
                "Component value must be one of: " "api [default], db, app."
            )

        # send request
        version_req = requests.get(version_url, proxies=self.proxies, verify=self.ssl)

        # checking response
        checker.check_api_response(version_req)

        # end of method
        return version_req.json().get("version")

    # -- URLs builders -------------------------------------------------------
    def get_edit_url(
        self,
        md_id: str = None,
        md_type: str = None,
        owner_id: str = None,
        tab: str = "identification",
    ):
        """Constructs the edition URL of a metadata.

        :param str md_id: metadata/resource UUID
        :param str owner_id: owner UUID
        :param str tab: target tab in the web form
        """
        # checks inputs
        if not checker.check_is_uuid(md_id) or not checker.check_is_uuid(owner_id):
            raise ValueError("One of md_id or owner_id is not a correct UUID.")
        else:
            pass
        if checker.check_edit_tab(tab, md_type=md_type):
            pass
        # construct URL
        return (
            "{}"
            "/groups/{}"
            "/resources/{}"
            "/{}".format(self.APP_URLS.get(self.platform), owner_id, md_id, tab)
        )

    def get_view_url(self, webapp: str = "oc", **kwargs):
        """Constructs the view URL of a metadata.

        :param str webapp: web app destination
        :param dict kwargs: web app specific parameters. For example see WEBAPPS
        """
        # build wbeapp URL depending on choosen webapp
        if webapp in self.WEBAPPS:
            webapp_args = self.WEBAPPS.get(webapp).get("args")
            # check kwargs parameters
            if set(webapp_args) <= set(kwargs):
                # construct and return url
                url = self.WEBAPPS.get(webapp).get("url")

                return url.format(**kwargs)
            else:
                raise TypeError(
                    "'{}' webapp expects {} argument(s): {}."
                    " Args passed: {}".format(
                        webapp, len(webapp_args), webapp_args, kwargs
                    )
                )
        else:
            raise ValueError(
                "'{}' is not a recognized webapp among: {}."
                " Try to register it.".format(self.WEBAPPS.keys(), webapp)
            )

    def register_webapp(self, webapp_name: str, webapp_args: list, webapp_url: str):
        """Register a new WEBAPP to use with the view URL builder.

        :param str webapp_name: name of the web app to register
        :param list webapp_args: dynamic arguments to complete the URL.
         Typically 'md_id'.
        :param str webapp_url: URL of the web app to register with
         args tags to replace. Example:
         'https://www.ppige-npdc.fr/portail/geocatalogue?uuid={md_id}'
        """
        # check parameters
        for arg in webapp_args:
            if arg not in webapp_url:
                raise ValueError(
                    "Inconsistent web app arguments and URL."
                    " It should contain arguments to replace"
                    " dynamically. Example: 'http://webapp.com"
                    "/isogeo?metadata={md_id}'"
                )
        # register
        self.WEBAPPS[webapp_name] = {"args": webapp_args, "url": webapp_url}

    def get_url_base_from_url_token(
        self, url_api_token: str = "https://id.api.isogeo.com/oauth/token"
    ):
        """Returns the Isogeo API root URL (which is not included into
        credentials file) from the token URL (which is always included).

        :param url_api_token str: url to Isogeo API ID token generator
        """
        in_parsed = urlparse(url_api_token)
        api_url_base = in_parsed._replace(
            path="", netloc=in_parsed.netloc.replace("id.", "")
        )
        return api_url_base.geturl()

    # -- SEARCH  --------------------------------------------------------------
    def pages_counter(self, total: int, page_size: int = 100) -> int:
        """Simple helper to handle pagination. Returns the number of pages for a
        given number of results.

        :param int total: count of metadata in a search request
        :param int page_size: count of metadata to display in each page
        """
        if total <= page_size:
            count_pages = 1
        else:
            if (total % page_size) == 0:
                count_pages = total / page_size
            else:
                count_pages = (total / page_size) + 1
        # method ending
        return int(count_pages)

    def tags_to_dict(self, tags=dict, prev_query=dict, duplicated: str = "rename"):
        """Reverse search tags dictionary to values as keys.
        Useful to populate filters comboboxes for example.

        :param dict tags: tags dictionary from a search request
        :param dict prev_query: query parameters returned after a search request. Typically `search.get("query")`.
        :param str duplicated: what to do about duplicated tags label. Values:

          * ignore - last tag parsed survives
          * merge - add duplicated in value as separated list (sep = '||')
          * rename [default] - if duplicated tag labels are part of different workgroup,
            so the tag label is renamed with workgroup.
        """
        # for rename option, get workgroups
        if duplicated == "rename":
            wgs = {k.split(":")[1]: v for k, v in tags.items() if k.startswith("owner")}
            # wgs = list(filter(lambda x[1]: x[0].startswith("owner"), tags.items()))
        elif duplicated == "ignore" or duplicated == "merge":
            wgs = None
        else:
            raise ValueError(
                "Duplicated value is not an accepted value."
                " Please refer to __doc__ method."
            )

        # inner function
        def _duplicate_mng(
            target_dict: dict, duplicate, mode: str = duplicated, workgroups: dict = wgs
        ):
            if mode == "merge":
                target_dict[duplicate[0]] += "||" + duplicate[1]
            elif mode == "rename":
                # get workgroup uuid
                if checker.check_is_uuid(k.split(":")[1]):
                    k_uuid = k.split(":")[1]
                else:
                    k_uuid = k.split(":")[2]
                # match with workgroups owners
                if k_uuid in workgroups:
                    repl = workgroups.get(k_uuid)
                else:
                    repl = k_uuid[:5]
                target_dict["{} ({})".format(duplicate[0], repl)] = duplicate[1]
            else:
                pass
            return

        # -- SEARCH TAGS -------------
        # output dicts structure
        tags_as_dicts = {
            "actions": {},
            "catalogs": {},
            "contacts": {},
            "data-sources": {},
            "formats": {},
            "inspires": {},
            "keywords": {},
            "licenses": {},
            "owners": {},
            "providers": {},
            "shares": {},
            "srs": {},
            "types": {},
        }

        # parsing tags and storing each one in a dict
        for k, v in sorted(tags.items()):
            if k.startswith("action"):
                tags_as_dicts.get("actions")[v] = k
                continue
            elif k.startswith("catalog"):
                if v in tags_as_dicts.get("catalogs") and duplicated != "ignore":
                    _duplicate_mng(tags_as_dicts.get("catalogs"), (v, k))
                else:
                    logging.debug(
                        "Duplicated catalog name: {}. Last catalog is retained.".format(
                            v
                        )
                    )
                    tags_as_dicts.get("catalogs")[v] = k
                continue
            elif k.startswith("contact"):
                if v in tags_as_dicts.get("contacts") and duplicated != "ignore":
                    _duplicate_mng(tags_as_dicts.get("contacts"), (v, k))
                else:
                    logging.debug(
                        "Duplicated contact name: {}. Last contact is retained.".format(
                            v
                        )
                    )
                    tags_as_dicts.get("contacts")[v] = k
                continue
            elif k.startswith("coordinate-system"):
                tags_as_dicts.get("srs")[v] = k
                continue
            elif k.startswith("data-source"):
                if v in tags_as_dicts.get("data-sources") and duplicated != "ignore":
                    _duplicate_mng(tags_as_dicts.get("data-sources"), (v, k))
                else:
                    logging.debug(
                        "Duplicated data-source name: {}. Last data-source is retained.".format(
                            v
                        )
                    )
                    tags_as_dicts.get("data-sources")[v] = k
                continue
            elif k.startswith("format"):
                tags_as_dicts.get("formats")[v] = k
                continue
            elif k.startswith("keyword:in"):
                tags_as_dicts.get("inspires")[v] = k
                continue
            elif k.startswith("keyword:is"):
                tags_as_dicts.get("keywords")[v] = k
                continue
            elif k.startswith("license"):
                if v in tags_as_dicts.get("licenses") and duplicated != "ignore":
                    _duplicate_mng(tags_as_dicts.get("licenses"), (v, k))
                else:
                    logging.debug(
                        "Duplicated license name: {}. Last license is retained.".format(
                            v
                        )
                    )
                    tags_as_dicts.get("licenses")[v] = k
                continue
            elif k.startswith("owner"):
                tags_as_dicts.get("owners")[v] = k
                continue
            elif k.startswith("provider"):
                # providers are particular bcause its value is always null.
                tags_as_dicts.get("providers")[k.split(":")[1]] = k
                continue
            elif k.startswith("share"):
                tags_as_dicts.get("shares")[v] = k
                continue
            elif k.startswith("type"):
                tags_as_dicts.get("types")[v] = k
                continue
            # ignored tags
            else:
                logging.debug("A tag has been ignored during parsing: {}".format(k))

        # -- QUERY TAGS -------------
        # handle share case
        if prev_query.get("_shares"):
            prev_query.get("_tags").append(
                "share:{}".format(prev_query.get("_shares")[0])
            )
        else:
            pass
        # output dict struture
        logging.debug(prev_query)
        query_as_dicts = {
            "_tags": {
                "actions": {},
                "catalogs": {},
                "contacts": {},
                "data-sources": {},
                "formats": {},
                "inspires": {},
                "keywords": {},
                "licenses": {},
                "owners": {},
                "providers": {},
                "shares": {},
                "srs": {},
                "types": {},
            },
            "_shares": prev_query.get("_shares"),
            "_terms": prev_query.get("_terms"),
        }

        # parsing and matching tags
        query_tags = query_as_dicts.get("_tags")
        for t in prev_query.get("_tags"):
            if t.startswith("action"):
                query_tags.get("actions")[tags.get(t)] = t
                continue
            elif t.startswith("catalog"):
                if v in query_tags.get("catalogs") and duplicated != "ignore":
                    _duplicate_mng(query_tags.get("catalogs"), (v, k))
                else:
                    logging.debug(
                        "Duplicated catalog name: {}. Last catalog is retained.".format(
                            v
                        )
                    )
                    query_tags.get("catalogs")[tags.get(t)] = t
                continue
            elif t.startswith("contact"):
                if v in query_tags.get("contacts") and duplicated != "ignore":
                    _duplicate_mng(query_tags.get("contacts"), (v, k))
                else:
                    logging.debug(
                        "Duplicated contact name: {}. Last contact is retained.".format(
                            v
                        )
                    )
                    query_tags.get("contacts")[tags.get(t)] = t
                continue
            elif t.startswith("coordinate-system"):
                query_tags.get("srs")[tags.get(t)] = t
                continue
            elif t.startswith("data-source"):
                if v in query_tags.get("data-sources") and duplicated != "ignore":
                    _duplicate_mng(query_tags.get("data-sources"), (v, k))
                else:
                    logging.debug(
                        "Duplicated data-source name: {}. Last data-source is retained.".format(
                            v
                        )
                    )
                    query_tags.get("data-sources")[tags.get(t)] = t
                continue
            elif t.startswith("format"):
                query_tags.get("formats")[tags.get(t)] = t
                continue
            elif t.startswith("keyword:in"):
                query_tags.get("inspires")[tags.get(t)] = t
                continue
            elif t.startswith("keyword:is"):
                query_tags.get("keywords")[tags.get(t)] = t
                continue
            elif t.startswith("license"):
                if v in query_tags.get("licenses") and duplicated != "ignore":
                    _duplicate_mng(query_tags.get("licenses"), (v, k))
                else:
                    logging.debug(
                        "Duplicated license name: {}. Last license is retained.".format(
                            v
                        )
                    )
                    query_tags.get("licenses")[tags.get(t)] = t
                continue
            elif t.startswith("owner"):
                query_tags.get("owners")[tags.get(t)] = t
                continue
            elif t.startswith("provider"):
                # providers are particular bcause its value is always null.
                query_tags.get("providers")[k.split(":")[1]] = k
                continue
            elif t.startswith("share"):
                query_tags.get("shares")[tags.get(t)] = t
                continue
            elif t.startswith("type"):
                query_tags.get("types")[tags.get(t)] = t
                continue
            # ignored tags
            else:
                logging.debug(
                    "A query tag has been ignored during parsing: {}".format(t)
                )

        # return the output
        return tags_as_dicts, query_as_dicts

    # -- SHARES MANAGEMENT ----------------------------------------------------
    def share_extender(self, share: dict, results_filtered: dict):
        """Extend share model with additional informations.

        :param dict share: share returned by API
        :param dict results_filtered: filtered search result
        """
        # add share administration URL
        creator_id = share.get("_creator").get("_tag")[6:]
        share["admin_url"] = "{}/groups/{}/admin/shares/{}".format(
            self.app_url, creator_id, share.get("_id")
        )
        # check if OpenCatalog is activated
        opencat_url = "{}/s/{}/{}".format(
            self.oc_url, share.get("_id"), share.get("urlToken")
        )
        if requests.head(opencat_url):
            share["oc_url"] = opencat_url
        else:
            pass
        # add metadata ids list
        share["mds_ids"] = (i.get("_id") for i in results_filtered)

        return share

    # -- API AUTH ------------------------------------------------------------
    def credentials_loader(self, in_credentials: str = "client_secrets.json") -> dict:
        """Loads API credentials from a file, JSON or INI.

        :param str in_credentials: path to the credentials file. By default,
          look for a client_secrets.json file.
        """
        accepted_extensions = (".ini", ".json")
        # checks
        if not path.isfile(in_credentials):
            raise IOError("Credentials file doesn't exist: {}".format(in_credentials))
        else:
            in_credentials = path.normpath(in_credentials)
        if path.splitext(in_credentials)[1] not in accepted_extensions:
            raise ValueError(
                "Extension of credentials file must be one of {}".format(
                    accepted_extensions
                )
            )
        else:
            kind = path.splitext(in_credentials)[1]
        # load, check and set
        if kind == ".json":
            with open(in_credentials, "r") as f:
                in_auth = json.loads(f.read())
            # check structure
            heads = ("installed", "web")
            if not set(in_auth).intersection(set(heads)):
                raise ValueError(
                    "Input JSON structure is not as expected."
                    " First key must be one of: {}".format(heads)
                )
            # set
            if "web" in in_auth:
                # json structure for group application
                auth_settings = in_auth.get("web")
                out_auth = {
                    "auth_mode": "group",
                    "client_id": auth_settings.get("client_id"),
                    "client_secret": auth_settings.get("client_secret"),
                    # if not specified, must be a former file then set classic scope
                    "scopes": auth_settings.get("scopes", ["resources:read"]),
                    "uri_auth": auth_settings.get("auth_uri"),
                    "uri_token": auth_settings.get("token_uri"),
                    "uri_base": self.get_url_base_from_url_token(
                        auth_settings.get("token_uri")
                    ),
                    "uri_redirect": None,
                }
            else:
                # assuming in_auth == 'installed'
                auth_settings = in_auth.get("installed")
                out_auth = {
                    "auth_mode": "user",
                    "client_id": auth_settings.get("client_id"),
                    "client_secret": auth_settings.get("client_secret"),
                    # if not specified, must be a former file then set classic scope
                    "scopes": auth_settings.get("scopes", ["resources:read"]),
                    "uri_auth": auth_settings.get("auth_uri"),
                    "uri_token": auth_settings.get("token_uri"),
                    "uri_base": self.get_url_base_from_url_token(
                        auth_settings.get("token_uri")
                    ),
                    "uri_redirect": auth_settings.get("redirect_uris", None),
                }
        else:
            # assuming file is an .ini
            ini_parser = ConfigParser()
            ini_parser.read(in_credentials)
            # check structure
            if "auth" in ini_parser._sections:
                auth_settings = ini_parser["auth"]
            else:
                raise ValueError(
                    "Input INI structure is not as expected."
                    " Section of credentials must be named: auth"
                )
            # set
            out_auth = {
                "auth_mode": auth_settings.get("CLIENT_TYPE"),
                "client_id": auth_settings.get("CLIENT_ID"),
                "client_secret": auth_settings.get("CLIENT_SECRET"),
                "uri_auth": auth_settings.get("URI_AUTH"),
                "uri_token": auth_settings.get("URI_TOKEN"),
                "uri_base": self.get_url_base_from_url_token(
                    auth_settings.get("URI_TOKEN")
                ),
                "uri_redirect": auth_settings.get("URI_REDIRECT"),
            }
        # method ending
        return out_auth


# #############################################################################
# ##### Stand alone program ########
# ##################################
if __name__ == "__main__":
    """Standalone execution."""
    utils = IsogeoUtils()
    print(
        utils.get_view_url(
            webapp="csw_getrecords",
            share_id="1e07910d365449b59b6596a9b428ecd9",
            share_token="TokenOhDearToken",
        )
    )
