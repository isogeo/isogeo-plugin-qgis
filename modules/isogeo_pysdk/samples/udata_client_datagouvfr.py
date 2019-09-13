# -*- coding: UTF-8 -*-
#! python3
# -----------------------------------------------------------------------------
# Name:         UData Python Client
# Purpose:      Abstraction class to manipulate data.gouv.fr API
#
# Author:       Julien Moura (@geojulien)
#
# Python:       3.6+
# -----------------------------------------------------------------------------

# #############################################################################
# ########## Libraries #############
# ##################################

# Standard library
import logging
from os import environ
from sys import platform as opersys

# 3rd party library
import requests

# ##############################################################################
# ############ Globals ############
# #################################

# LOG
logger = logging.getLogger("uDataPyClient")

# #############################################################################
# ########## Classes ###############
# ##################################


class DataGouvFr(object):
    """Use DataGouvFR REST API.

    Full doc at (French): https://www.data.gouv.fr/fr/apidoc/
    """

    base_url = "https://www.data.gouv.fr/api/1/"

    def __init__(self, api_key=environ.get("DATAGOUV_API_KEY", None)):
        """
        """
        super(DataGouvFr, self).__init__()
        if api_key:
            self.api_key = api_key
        else:
            raise ValueError

        # load basic attributes
        self.get_filters_values()

    def org_datasets(self, org_id="isogeo", page_size=25, x_fields=None):
        """"""
        # handling request parameters
        payload = {"org": org_id, "size": page_size, "X-Fields": x_fields}

        # search request
        # head = {"X-API-KEY": self.api_key}
        search_url = "{}organizations/{}/datasets/".format(
            self.base_url,
            org_id,
            # page_size
        )

        search_req = requests.get(
            search_url,
            # headers=head,
            params=payload,
        )

        # serializing result into dict and storing resources in variables
        logger.debug(search_req.url)
        return search_req.json()

    def search_datasets(
        self,
        license=None,
        format=None,
        query=None,
        featured=None,
        owner=None,
        organization=None,
        badge=None,
        reuses=None,
        page_size=20,
        x_fields=None,
    ):
        """Search datasets within uData portal."""
        # handling request parameters
        payload = {"badge": badge, "size": page_size, "X-Fields": x_fields}

        # search request
        # head = {"X-API-KEY": self.api_key}
        search_url = "{}/datasets".format(
            self.base_url,
            # org_id,
            # page_size
        )

        search_req = requests.get(
            search_url,
            # headers=head,
            params=payload,
        )

        # serializing result into dict and storing resources in variables
        logger.debug(search_req.url)
        return search_req.json()

    # -- UTILITIES -----------------------------------------------------------
    def get_filters_values(self):
        """Get different filters values as dicts."""
        # DATASETS --
        # badges
        self._DST_BADGES = requests.get(self.base_url + "datasets/badges/").json()
        # licences
        self._DST_LICENSES = {
            l.get("id"): l.get("title")
            for l in requests.get(self.base_url + "datasets/licenses").json()
        }
        # frequencies
        self._DST_FREQUENCIES = {
            f.get("id"): f.get("label")
            for f in requests.get(self.base_url + "datasets/frequencies").json()
        }
        # ORGANIZATIONS --
        # badges
        self._ORG_BADGES = requests.get(self.base_url + "organizations/badges/").json()
        # # licences
        # self._DST_LICENSES = {l.get("id"): l.get("title")
        #                   for l in requests.get(self.base_url + "datasets/licenses").json()}
        # # frequencies
        # self._DST_FREQUENCIES = {f.get("id"): f.get("label")
        #                      for f in requests.get(self.base_url + "datasets/frequencies").json()}
        # SPATIAL --
        # granularities
        self._GRANULARITIES = {
            g.get("id"): g.get("name")
            for g in requests.get(self.base_url + "spatial/granularities").json()
        }
        # levels
        self._LEVELS = {
            g.get("id"): g.get("name")
            for g in requests.get(self.base_url + "spatial/levels").json()
        }
        # MISC --
        # facets
        self._FACETS = (
            "all",
            "badge",
            "featured",
            "format",
            "geozone",
            "granularity",
            "license",
            "owner",
            "organization",
            "reuses",
            "tag",
            "temporal_coverage",
        )
        # reuses
        self._REUSES = ("none", "few", "quite", "many")


# ##############################################################################
# ##### Stand alone program ########
# ##################################
if __name__ == "__main__":
    """ standalone execution """
    # some organizations to play with
    orgas = {
        "ign": "534fff80a3a7292c64a77e41",
        "insee": "534fff81a3a7292c64a77e5c",
        "isogeo": "54a13044c751df096c04805a",
    }
    # start playing
    api_key = environ.get("DATAGOUV_API_KEY")
    app = DataGouvFr()
    print(dir(app))
    org_ds = app.org_datasets(org_id=orgas.get("isogeo"))
    print(sorted(org_ds[0].keys()), len(org_ds), org_ds[0].get("id"))
    search_ds = app.search_datasets(badge="spd")
    print(sorted(search_ds.keys()), len(search_ds), search_ds.get("total"))
