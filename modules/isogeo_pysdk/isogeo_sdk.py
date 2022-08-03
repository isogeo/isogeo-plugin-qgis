# -*- coding: UTF-8 -*-
#! python3

# -----------------------------------------------------------------------------
# Name:         Isogeo
# Purpose:      Python minimalist SDK to use Isogeo API
#
# Author:       Julien Moura @Isogeo
#
# Python:       3.5+
# Created:      22/12/2015
# Updated:      10/04/2019
# -----------------------------------------------------------------------------

# #############################################################################
# ########## Libraries #############
# ##################################

# Standard library
import locale
import logging
import re
from datetime import datetime, timedelta
from functools import wraps
from math import ceil
from sys import platform as opersys

# 3rd party library
from requests import ConnectionError, Session

# modules
try:
    from . import checker
    from . import utils
except (ImportError, ValueError, SystemError):
    import checker
    import utils

# ##############################################################################
# ########## Globals ###############
# ##################################

checker = checker.IsogeoChecker()
utils = utils.IsogeoUtils()
version = "2.21.2"

# #############################################################################
# ########## Classes ###############
# ##################################

__all__ = ["Isogeo", "IsogeoChecker", "IsogeoTranslator", "IsogeoUtils"]


class Isogeo(Session):
    """Abstraction class for Isogeo REST API.

    Online resources:
      * Full doc at: help.isogeo.com/api/

    :param str client_id: application oAuth2 identifier
    :param str client_secret: application oAuth2 secret
    :param dict proxy: dictionary of proxy settings as described in
     requests (http://docs.python-requests.org/en/master/user/advanced/#proxies)
    :param str auth_mode: oAuth2 mode to use
    :param str platform: to request production or quality assurance
    :param str lang: API localization ("en" or "fr").
    :param str app_name: to custom the application name and user-agent
    """

    # -- ATTRIBUTES -----------------------------------------------------------
    AUTH_MODES = {"group", "user_private", "user_public"}

    _THESAURI_DICT = {
        "isogeo": "1616597fbc4348c8b11ef9d59cf594c8",
        "inspire-theme": "926c676c380046d7af99bcae343ac813",
        "iso19115-topic": "926f969ee2bb470a84066625f68b96bb",
    }

    # -- BEFORE ALL -----------------------------------------------------------

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        proxy: dict = None,
        auth_mode: str = "group",
        platform: str = "prod",
        lang: str = "en",
        app_name: str = "isogeo-pysdk/{}".format(version),
    ):
        """Isogeo API class initialization."""
        super(Isogeo, self).__init__()
        self.client_id = client_id
        self.client_secret = client_secret
        self.app_name = app_name
        self.token = {}

        # checking internet connection
        if not checker.check_internet_connection(proxies=proxy):
            if proxy:
                logging.debug("Proxy enabled")
            raise EnvironmentError("Internet connection issue.")
        else:
            pass

        # testing parameters
        if len(client_secret) != 64:
            logging.error("App secret length issue: it should be 64 chars.")
            raise ValueError(1, "Bad secret value: it must be 64 chars.")
        else:
            pass

        # auth mode
        if auth_mode not in self.AUTH_MODES:
            logging.error("Not accepted auth mode: {}".format(auth_mode))
            raise ValueError("Mode value must be one of: ".format(" | ".join(self.AUTH_MODES)))
        else:
            self.auth_mode = auth_mode

        # platform to request
        (
            self.platform,
            self.api_url,
            self.app_url,
            self.csw_url,
            self.mng_url,
            self.oc_url,
            self.ssl,
        ) = utils.set_base_url(platform)

        # setting language
        if lang.lower() not in ("fr", "en"):
            logging.warning(
                "Isogeo API is only available in English ('en', "
                "default) or French ('fr'). "
                "Language has been set on English."
            )
            self.lang = "en"
        else:
            self.lang = lang.lower()

        # setting locale according to the language passed
        try:
            if opersys == "win32":
                if lang.lower() == "fr":
                    locale.setlocale(locale.LC_ALL, str("fra_fra"))
                else:
                    locale.setlocale(locale.LC_ALL, str("uk_UK"))
            else:
                if lang.lower() == "fr":
                    locale.setlocale(locale.LC_ALL, str("fr_FR.utf8"))
                else:
                    locale.setlocale(locale.LC_ALL, str("en_GB.utf8"))
        except locale.Error as e:
            logging.error("Selected locale ({}) is not installed: {}".format(lang.lower(), e))

        # handling proxy parameters
        # see: http://docs.python-requests.org/en/latest/user/advanced/#proxies
        if proxy and isinstance(proxy, dict) and "http" in proxy:
            logging.debug("Proxy enabled.")
            self.proxies = proxy
        elif proxy and not isinstance(proxy, dict):
            raise TypeError(
                "Proxy syntax error. Must be a dict:"
                "{ 'protocol': "
                "'http://user:password@proxy_url:port' }."
                " e.g.: "
                "{'http': 'http://martin:1234@10.1.68.1:5678',"
                "'https': 'http://martin:p4ssW0rde@10.1.68.1:5678'}"
            )
        else:
            self.proxies = {}
            logging.debug("No proxy set. Use default configuration.")
            pass

        # get API version
        # logging.debug("Isogeo API version: {}".format(utils.get_isogeo_version()))
        # logging.debug("Isogeo DB version: {}".format(utils.get_isogeo_version("db")))

    # -- API CONNECTION ------------------------------------------------------
    def connect(self, client_id: str = None, client_secret: str = None) -> dict:
        """Authenticate application and get token bearer.

        Isogeo API uses oAuth 2.0 protocol (https://tools.ietf.org/html/rfc6749)
        see: http://help.isogeo.com/api/fr/authentication/groupsapps.html

        :param str client_id: application oAuth2 identifier
        :param str client_secret: application oAuth2 secret
        """
        # instanciated or direct call
        if not client_id and not client_secret:
            client_id = self.client_id
            client_secret = self.client_secret
        else:
            pass

        # Basic Authentication header in Base64 (https://en.wikipedia.org/wiki/Base64)
        # see: http://tools.ietf.org/html/rfc2617#section-2
        # using Client Credentials Grant method
        # see: http://tools.ietf.org/html/rfc6749#section-4.4
        payload = {"grant_type": "client_credentials"}
        head = {"user-agent": self.app_name}

        # passing request to get a 24h bearer
        # see: http://tools.ietf.org/html/rfc6750#section-2
        id_url = "https://id.{}.isogeo.com/oauth/token".format(self.api_url)
        try:
            conn = self.post(
                id_url,
                auth=(client_id, client_secret),
                headers=head,
                data=payload,
                proxies=self.proxies,
                verify=self.ssl,
            )
        except ConnectionError as e:
            raise ConnectionError("Connection to Isogeo ID" "failed: {}".format(e))

        # just a fast check
        check_params = checker.check_api_response(conn)
        if check_params == 1:
            pass
        elif isinstance(check_params, tuple) and len(check_params) == 2:
            raise ValueError(2, check_params)

        # getting access
        self.token = conn.json()

        # add expiration date - calculating with a prevention of 10%
        expiration_delay = self.token.get("expires_in", 3600) - (
            self.token.get("expires_in", 3600) / 10
        )
        self.token["expires_at"] = datetime.utcnow() + timedelta(seconds=expiration_delay)

        # end of method
        return self.token

    # -- PROPERTIES -----------------------------------------------------------
    @property
    def header(self) -> dict:
        if self.auth_mode == "group":
            return {
                "Authorization": "Bearer {}".format(self.token.get("access_token")),
                "user-agent": self.app_name,
            }

    # -- DECORATORS -----------------------------------------------------------
    def _check_bearer_validity(decorated_func):
        """Check API Bearer token validity.

        Isogeo ID delivers authentication bearers which are valid during
        a certain time. So this decorator checks the validity of the token
        comparing with actual datetime (UTC) and renews it if necessary.
        See: http://tools.ietf.org/html/rfc6750#section-2

        :param decorated_func token: original function to execute after check
        """

        @wraps(decorated_func)
        def wrapper(self, *args, **kwargs):
            # compare token expiration date and ask for a new one if it's expired
            if datetime.now() < self.token.get("expires_at"):
                self.connect()
                logging.debug("Token was about to expire, so has been renewed.")
            else:
                logging.debug("Token is still valid.")
                pass

            # let continue running the original function
            return decorated_func(self, *args, **kwargs)

        return wrapper

    # -- API PATHS ------------------------------------------------------------
    @_check_bearer_validity
    def search(
        self,
        token: dict = None,
        query: str = "",
        bbox: list = None,
        poly: str = None,
        georel: str = None,
        order_by: str = "_created",
        order_dir: str = "desc",
        page_size: int = 100,
        offset: int = 0,
        share: str = None,
        specific_md: list = [],
        include: list = [],
        whole_share: bool = True,
        check: bool = True,
        augment: bool = False,
        tags_as_dicts: bool = False,
        prot: str = "https",
    ) -> dict:
        """Search within the resources shared to the application.

        It's the main method to use.

        :param str token: API auth token - DEPRECATED: token is now automatically included
        :param str query: search terms and semantic filters. Equivalent of
         **q** parameter in Isogeo API. It could be a simple
         string like *oil* or a tag like *keyword:isogeo:formations*
         or *keyword:inspire-theme:landcover*. The *AND* operator
         is applied when various tags are passed.
        :param list bbox: Bounding box to limit the search.
         Must be a 4 list of coordinates in WGS84 (EPSG 4326).
         Could be associated with *georel*.
        :param str poly: Geographic criteria for the search, in WKT format.
         Could be associated with *georel*.
        :param str georel: geometric operator to apply to the bbox or poly
         parameters.

         Available values (see: *isogeo.GEORELATIONS*):

          * 'contains',
          * 'disjoint',
          * 'equals',
          * 'intersects' - [APPLIED BY API if NOT SPECIFIED]
          * 'overlaps',
          * 'within'.

        :param str order_by: sorting results.

         Available values:

          * '_created': metadata creation date [DEFAULT if relevance is null]
          * '_modified': metadata last update
          * 'title': metadata title
          * 'created': data creation date (possibly None)
          * 'modified': data last update date
          * 'relevance': relevance score calculated by API [DEFAULT].

        :param str order_dir: sorting direction.

         Available values:
          * 'desc': descending
          * 'asc': ascending

        :param int page_size: limits the number of results.
         Useful to paginate results display. Default value: 100.
        :param int offset: offset to start page size
         from a specific results index
        :param str share: share UUID to filter on
        :param list specific_md: list of metadata UUIDs to filter on
        :param list include: subresources that should be returned.
         Must be a list of strings. Available values: *isogeo.SUBRESOURCES*
        :param bool whole_share: option to return all results or only the
         page size. *True* by DEFAULT.
        :param bool check: option to check query parameters and avoid erros.
         *True* by DEFAULT.
        :param bool augment: option to improve API response by adding
         some tags on the fly (like shares_id)
        :param bool tags_as_dicts: option to store tags as key/values by filter.
        :param str prot: https [DEFAULT] or http
         (use it only for dev and tracking needs).
        """
        # specific resources specific parsing
        specific_md = checker._check_filter_specific_md(specific_md)

        # sub resources specific parsing
        include = checker._check_filter_includes(include)

        # handling request parameters
        payload = {
            "_id": specific_md,
            "_include": include,
            "_lang": self.lang,
            "_limit": page_size,
            "_offset": offset,
            "box": bbox,
            "geo": poly,
            "rel": georel,
            "ob": order_by,
            "od": order_dir,
            "q": query,
            "s": share,
        }

        if check:
            checker.check_request_parameters(payload)
        else:
            pass

        # search request
        search_url = "{}://v1.{}.isogeo.com/resources/search".format(prot, self.api_url)
        try:
            search_req = self.get(
                search_url,
                headers=self.header,
                params=payload,
                proxies=self.proxies,
                verify=self.ssl,
            )
        except Exception as e:
            logging.error(e)
            raise Exception

        # fast response check
        checker.check_api_response(search_req)

        # serializing result into dict and storing resources in variables
        search_rez = search_req.json()
        resources_count = search_rez.get("total")  # total of metadatas shared

        # handling Isogeo API pagination
        # see: http://help.isogeo.com/api/fr/methods/pagination.html
        if resources_count > page_size and whole_share:
            # if API returned more than one page of results, let's get the rest!
            metadatas = []  # a recipient list
            payload["_limit"] = 100  # now it'll get pages of 100 resources
            # let's parse pages
            for idx in range(0, int(ceil(resources_count / 100)) + 1):
                payload["_offset"] = idx * 100
                search_req = self.get(
                    search_url,
                    headers=self.header,
                    params=payload,
                    proxies=self.proxies,
                    verify=self.ssl,
                )
                # storing results by addition
                metadatas.extend(search_req.json().get("results"))
            search_rez["results"] = metadatas
        else:
            pass

        # add shares to tags and query
        if augment:
            self.add_tags_shares(search_rez.get("tags"))
            if share:
                search_rez.get("query")["_shares"] = [share]
            else:
                search_rez.get("query")["_shares"] = []
        else:
            pass

        # store tags in dicts
        if tags_as_dicts:
            new_tags = utils.tags_to_dict(
                tags=search_rez.get("tags"), prev_query=search_rez.get("query")
            )
            # clear
            search_rez.get("tags").clear()
            search_rez.get("query").clear()
            # update
            search_rez.get("tags").update(new_tags[0])
            search_rez.get("query").update(new_tags[1])
        else:
            pass
        # end of method
        return search_rez

    @_check_bearer_validity
    def resource(
        self,
        token: dict = None,
        id_resource: str = None,
        subresource=None,
        include: list = [],
        prot: str = "https",
    ) -> dict:
        """Get complete or partial metadata about one specific resource.

        :param str token: API auth token
        :param str id_resource: metadata UUID to get
        :param list include: subresources that should be included.
         Must be a list of strings. Available values: 'isogeo.SUBRESOURCES'
        :param str prot: https [DEFAULT] or http
         (use it only for dev and tracking needs).
        """
        # if subresource route
        if isinstance(subresource, str):
            subresource = "/{}".format(checker._check_subresource(subresource))
        else:
            subresource = ""
            # _includes specific parsing
            include = checker._check_filter_includes(include)

        # handling request parameters
        payload = {"id": id_resource, "_include": include}
        # resource search
        md_url = "{}://v1.{}.isogeo.com/resources/{}{}".format(
            prot, self.api_url, id_resource, subresource
        )
        resource_req = self.get(
            md_url,
            headers=self.header,
            params=payload,
            proxies=self.proxies,
            verify=self.ssl,
        )
        checker.check_api_response(resource_req)

        # end of method
        return resource_req.json()

    # -- SHARES and APPLICATIONS ---------------------------------------------
    @_check_bearer_validity
    def shares(self, token: dict = None, prot: str = "https") -> dict:
        """Get information about shares which feed the application.

        :param str token: API auth token
        :param str prot: https [DEFAULT] or http
         (use it only for dev and tracking needs).
        """
        # passing auth parameter
        shares_url = "{}://v1.{}.isogeo.com/shares/".format(prot, self.api_url)
        shares_req = self.get(
            shares_url, headers=self.header, proxies=self.proxies, verify=self.ssl
        )

        # checking response
        checker.check_api_response(shares_req)

        # end of method
        return shares_req.json()

    @_check_bearer_validity
    def share(
        self,
        share_id: str,
        token: dict = None,
        augment: bool = False,
        prot: str = "https",
    ) -> dict:
        """Get information about a specific share and its applications.

        :param str token: API auth token
        :param str share_id: share UUID
        :param bool augment: option to improve API response by adding
         some tags on the fly.
        :param str prot: https [DEFAULT] or http
         (use it only for dev and tracking needs).
        """
        # passing auth parameter
        share_url = "{}://v1.{}.isogeo.com/shares/{}".format(prot, self.api_url, share_id)
        share_req = self.get(share_url, headers=self.header, proxies=self.proxies, verify=self.ssl)

        # checking response
        checker.check_api_response(share_req)

        # enhance share model
        share = share_req.json()
        if augment:
            share = utils.share_extender(
                share, self.search(whole_share=1, share=share_id).get("results")
            )
        else:
            pass

        # end of method
        return share

    # -- LICENCES ---------------------------------------------
    @_check_bearer_validity
    def licenses(self, token: dict = None, owner_id: str = None, prot: str = "https") -> dict:
        """Get information about licenses owned by a specific workgroup.

        :param str token: API auth token
        :param str owner_id: workgroup UUID
        :param str prot: https [DEFAULT] or http
         (use it only for dev and tracking needs).
        """
        # handling request parameters
        payload = {"gid": owner_id}

        # search request
        licenses_url = "{}://v1.{}.isogeo.com/groups/{}/licenses".format(
            prot, self.api_url, owner_id
        )
        licenses_req = self.get(
            licenses_url,
            headers=self.header,
            params=payload,
            proxies=self.proxies,
            verify=self.ssl,
        )

        # checking response
        req_check = checker.check_api_response(licenses_req)
        if isinstance(req_check, tuple):
            return req_check

        # end of method
        return licenses_req.json()

    @_check_bearer_validity
    def license(self, license_id: str, token: dict = None, prot: str = "https") -> dict:
        """Get details about a specific license.

        :param str token: API auth token
        :param str license_id: license UUID
        :param str prot: https [DEFAULT] or http
         (use it only for dev and tracking needs).
        """
        # handling request parameters
        payload = {"lid": license_id}

        # search request
        license_url = "{}://v1.{}.isogeo.com/licenses/{}".format(prot, self.api_url, license_id)
        license_req = self.get(
            license_url,
            headers=self.header,
            params=payload,
            proxies=self.proxies,
            verify=self.ssl,
        )

        # checking response
        checker.check_api_response(license_req)

        # end of method
        return license_req.json()

    # -- KEYWORDS -----------------------------------------------------------

    @_check_bearer_validity
    def thesauri(self, token: dict = None, prot: str = "https") -> dict:
        """Get list of available thesauri.

        :param str token: API auth token
        :param str prot: https [DEFAULT] or http
         (use it only for dev and tracking needs).
        """
        # passing auth parameter
        thez_url = "{}://v1.{}.isogeo.com/thesauri".format(prot, self.api_url)
        thez_req = self.get(thez_url, headers=self.header, proxies=self.proxies, verify=self.ssl)

        # checking response
        checker.check_api_response(thez_req)

        # end of method
        return thez_req.json()

    @_check_bearer_validity
    def thesaurus(
        self,
        token: dict = None,
        thez_id: str = "1616597fbc4348c8b11ef9d59cf594c8",
        prot: str = "https",
    ) -> dict:
        """Get a thesaurus.

        :param str token: API auth token
        :param str thez_id: thesaurus UUID
        :param str prot: https [DEFAULT] or http
         (use it only for dev and tracking needs).
        """
        # handling request parameters
        payload = {"tid": thez_id}

        # passing auth parameter
        thez_url = "{}://v1.{}.isogeo.com/thesauri/{}".format(prot, self.api_url, thez_id)
        thez_req = self.get(
            thez_url,
            headers=self.header,
            params=payload,
            proxies=self.proxies,
            verify=self.ssl,
        )

        # checking response
        checker.check_api_response(thez_req)

        # end of method
        return thez_req.json()

    @_check_bearer_validity
    def keywords(
        self,
        token: dict = None,
        thez_id: str = "1616597fbc4348c8b11ef9d59cf594c8",
        query: str = "",
        offset: int = 0,
        order_by: str = "text",
        order_dir: str = "desc",
        page_size: int = 20,
        specific_md: list = [],
        specific_tag: list = [],
        include: list = [],
        prot: str = "https",
    ) -> dict:
        """Search for keywords within a specific thesaurus.

        :param str token: API auth token
        :param str thez_id: thesaurus UUID
        :param str query: search terms
        :param int offset: pagination start
        :param str order_by: sort criteria. Available values :

            - count.group,
            - count.isogeo,
            - text

        :param str prot: https [DEFAULT] or http
         (use it only for dev and tracking needs).
        """
        # specific resources specific parsing
        specific_md = checker._check_filter_specific_md(specific_md)
        # sub resources specific parsing
        include = checker._check_filter_includes(include, "keyword")
        # specific tag specific parsing
        specific_tag = checker._check_filter_specific_tag(specific_tag)

        # handling request parameters
        payload = {
            "_id": specific_md,
            "_include": include,
            "_limit": page_size,
            "_offset": offset,
            "_tag": specific_tag,
            "tid": thez_id,
            "ob": order_by,
            "od": order_dir,
            "q": query,
        }

        # search request
        keywords_url = "{}://v1.{}.isogeo.com/thesauri/{}/keywords/search".format(
            prot, self.api_url, thez_id
        )

        kwds_req = self.get(
            keywords_url,
            headers=self.header,
            params=payload,
            proxies=self.proxies,
            verify=self.ssl,
        )

        # checking response
        checker.check_api_response(kwds_req)

        # end of method
        return kwds_req.json()

    # -- DOWNLOADS -----------------------------------------------------------
    @_check_bearer_validity
    def dl_hosted(
        self,
        token: dict = None,
        resource_link: dict = None,
        encode_clean: bool = 1,
        proxy_url: str = None,
        prot: str = "https",
    ) -> tuple:
        """Download hosted resource.

        :param str token: API auth token
        :param dict resource_link: link dictionary
        :param bool encode_clean: option to ensure a clean filename and avoid OS errors
        :param str proxy_url: proxy to use to download
        :param str prot: https [DEFAULT] or http
         (use it only for dev and tracking needs).

        Example of resource_link dict:

        .. code-block:: json

            {
            "_id": "g8h9i0j11k12l13m14n15o16p17Q18rS",
            "type": "hosted",
            "title": "label_of_hosted_file.zip",
            "url": "/resources/1a2b3c4d5e6f7g8h9i0j11k12l13m14n/links/g8h9i0j11k12l13m14n15o16p17Q18rS.bin",
            "kind": "data",
            "actions": ["download", ],
            "size": "2253029",
            }

        """
        # check resource link parameter type
        if not isinstance(resource_link, dict):
            raise TypeError("Resource link expects a dictionary.")
        else:
            pass
        # check resource link type
        if not resource_link.get("type") == "hosted":
            raise ValueError(
                "Resource link passed is not a hosted one: {}".format(resource_link.get("type"))
            )
        else:
            pass

        # handling request parameters
        payload = {"proxyUrl": proxy_url}

        # prepare URL request
        hosted_url = "{}://v1.{}.isogeo.com/{}".format(prot, self.api_url, resource_link.get("url"))

        # send stream request
        hosted_req = self.get(
            hosted_url,
            headers=self.header,
            stream=True,
            params=payload,
            proxies=self.proxies,
            verify=self.ssl,
        )
        # quick check
        req_check = checker.check_api_response(hosted_req)
        if not req_check:
            raise ConnectionError(req_check[1])
        else:
            pass

        # get filename from header
        content_disposition = hosted_req.headers.get("Content-Disposition")
        if content_disposition:
            filename = re.findall("filename=(.+)", content_disposition)[0]
        else:
            filename = resource_link.get("title")

        # remove special characters
        if encode_clean:
            filename = utils.encoded_words_to_text(filename)
            filename = re.sub(r"[^\w\-_\. ]", "", filename)

        # well-formed size
        in_size = resource_link.get("size")
        for size_cat in ("octets", "Ko", "Mo", "Go"):
            if in_size < 1024.0:
                out_size = "%3.1f %s" % (in_size, size_cat)
            in_size /= 1024.0

        out_size = "%3.1f %s" % (in_size, " To")

        # end of method
        return (hosted_req, filename, out_size)

    @_check_bearer_validity
    def xml19139(
        self,
        token: dict = None,
        id_resource: str = None,
        proxy_url=None,
        prot: str = "https",
    ):
        """Get resource exported into XML ISO 19139.

        :param str token: API auth token
        :param str id_resource: metadata UUID to export
        :param str proxy_url: proxy to use to download
        :param str prot: https [DEFAULT] or http
         (use it only for dev and tracking needs).
        """
        # check metadata UUID
        if not checker.check_is_uuid(id_resource):
            raise ValueError("Metadata ID is not a correct UUID.")
        else:
            pass

        # handling request parameters
        payload = {"proxyUrl": proxy_url, "id": id_resource}

        # resource search
        md_url = "{}://v1.{}.isogeo.com/resources/{}.xml".format(prot, self.api_url, id_resource)
        xml_req = self.get(
            md_url,
            headers=self.header,
            stream=True,
            params=payload,
            proxies=self.proxies,
            verify=self.ssl,
        )

        # end of method
        return xml_req

    # -- UTILITIES -----------------------------------------------------------
    def add_tags_shares(self, tags: dict = dict()):
        """Add shares list to the tags attributes in search results.

        :param dict tags: tags dictionary from a search request
        """
        # check if shares_id have already been retrieved or not
        if not hasattr(self, "shares_id"):
            shares = self.shares()
            self.shares_id = {"share:{}".format(i.get("_id")): i.get("name") for i in shares}
        else:
            pass
        # update query tags
        tags.update(self.shares_id)

    @_check_bearer_validity
    def get_app_properties(self, token: dict = None, prot: str = "https"):
        """Get information about the application declared on Isogeo.

        :param str token: API auth token
        :param str prot: https [DEFAULT] or http
         (use it only for dev and tracking needs).
        """
        # check if app properties have already been retrieved or not
        if not hasattr(self, "app_properties"):
            first_app = self.shares()[0].get("applications")[0]
            app = {
                "admin_url": "{}/applications/{}".format(self.mng_url, first_app.get("_id")),
                "creation_date": first_app.get("_created"),
                "last_update": first_app.get("_modified"),
                "name": first_app.get("name"),
                "type": first_app.get("type"),
                "kind": first_app.get("kind"),
                "url": first_app.get("url"),
            }
            self.app_properties = app
        else:
            pass

    @_check_bearer_validity
    def get_link_kinds(self, token: dict = None, prot: str = "https") -> dict:
        """Get available links kinds and corresponding actions.

        :param str token: API auth token
        :param str prot: https [DEFAULT] or http
         (use it only for dev and tracking needs).
        """
        # search request
        req_url = "{}://v1.{}.isogeo.com/link-kinds".format(prot, self.api_url)

        req = self.get(req_url, headers=self.header, proxies=self.proxies, verify=self.ssl)

        # checking response
        checker.check_api_response(req)

        # end of method
        return req.json()

    @_check_bearer_validity
    def get_directives(self, token: dict = None, prot: str = "https") -> dict:
        """Get environment directives which represent INSPIRE limitations.

        :param str token: API auth token
        :param str prot: https [DEFAULT] or http
         (use it only for dev and tracking needs).
        """
        # search request
        req_url = "{}://v1.{}.isogeo.com/directives".format(prot, self.api_url)

        req = self.get(req_url, headers=self.header, proxies=self.proxies, verify=self.ssl)

        # checking response
        checker.check_api_response(req)

        # end of method
        return req.json()

    @_check_bearer_validity
    def get_coordinate_systems(
        self, token: dict = None, srs_code: str = None, prot: str = "https"
    ) -> dict:
        """Get available coordinate systems in Isogeo API.

        :param str token: API auth token
        :param str srs_code: code of a specific coordinate system
        :param str prot: https [DEFAULT] or http
         (use it only for dev and tracking needs).
        """
        # if specific format
        if isinstance(srs_code, str):
            specific_srs = "/{}".format(srs_code)
        else:
            specific_srs = ""

        # search request
        req_url = "{}://v1.{}.isogeo.com/coordinate-systems{}".format(
            prot, self.api_url, specific_srs
        )

        req = self.get(req_url, headers=self.header, proxies=self.proxies, verify=self.ssl)

        # checking response
        checker.check_api_response(req)

        # end of method
        return req.json()

    @_check_bearer_validity
    def get_formats(self, token: dict = None, format_code: str = None, prot: str = "https") -> dict:
        """Get formats.

        :param str token: API auth token
        :param str format_code: code of a specific format
        :param str prot: https [DEFAULT] or http
         (use it only for dev and tracking needs).
        """
        # if specific format
        if isinstance(format_code, str):
            specific_format = "/{}".format(format_code)
        else:
            specific_format = ""

        # search request
        req_url = "{}://v1.{}.isogeo.com/formats{}".format(prot, self.api_url, specific_format)

        req = self.get(req_url, headers=self.header, proxies=self.proxies, verify=self.ssl)

        # checking response
        checker.check_api_response(req)

        # end of method
        return req.json()


# ##############################################################################
# ##### Stand alone program ########
# ##################################
if __name__ == "__main__":
    """ standalone execution """
    # ------------ Specific imports ----------------
    from os import environ

    # ------------ Log & debug ----------------
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # ------------Authentication credentials ----------------
    client_id = environ.get("ISOGEO_API_DEV_ID")
    client_secret = environ.get("ISOGEO_API_DEV_SECRET")

    if not client_id or not client_secret:
        logging.critical("No API credentials set as env variables.")
        exit()
    else:
        pass

    # ------------ Real start ----------------
    # instanciating the class
    isogeo = Isogeo(
        client_id=client_id,
        client_secret=client_secret,
        auth_mode="group",
        lang="fr",
        # platform="qa"
    )

    # getting a token
    isogeo.connect()

    s = isogeo.search()
    print(len(s.get("results")))
    # print(s)

    # r = isogeo.resource(id_resource="2313f3f7e0f540c3ad2850d7c9c4c04d")
    # print(r)

    # t = isogeo.thesauri()
    # print(t)
    # tz = isogeo.thesaurus(thez_id=t[0].get("_id"))
    # print(tz)

    # memo : par défaut order_dir = asc
    # k = isogeo.keywords(
    #     thez_id="1616597fbc4348c8b11ef9d59cf594c8",
    #     order_by="count.isogeo",
    #     order_dir="desc",
    #     page_size=10,
    #     include="all",
    # )
    # print(k)

    # lics = isogeo.licenses(owner_id="32f7e95ec4e94ca3bc1afda960003882")
    # print(lics)

    # fmts = isogeo.get_formats()
    # # print(fmts)

    # srs = isogeo.get_coordinate_systems()
    # # print(srs)

    # dirs = isogeo.get_directives()
    # print(dirs)

    # lks = isogeo.get_link_kinds()
    # print(lks)
