# -*- coding: UTF-8 -*-
#! python3

# -----------------------------------------------------------------------------
# Name:         Isogeo
# Purpose:      Sample using Python minimalist SDK of Isogeo API to get links
#               and related resources, including secondary links
#
# Author:       Julien Moura (@geojulien)
#
# Python:       3.6+
# Created:      01/09/2016
# Updated:      01/09/2016
# -----------------------------------------------------------------------------

# #############################################################################
# ########## Libraries #############
# ##################################

# Standard library
from collections import OrderedDict  # ordered dictionary

# Isogeo
from isogeo_pysdk import Isogeo

# #############################################################################
# ######## Main program ############
# ##################################

if __name__ == "__main__":
    """Standalone execution"""
    # ------------ Specific imports ----------------
    from os import environ

    # ------------Authentication credentials ----------------
    client_id = environ.get("ISOGEO_API_DEV_ID")
    client_secret = environ.get("ISOGEO_API_DEV_SECRET")

    # ------------ Real start ----------------
    # instanciating the class
    isogeo = Isogeo(client_id=client_id, client_secret=client_secret, lang="fr")
    isogeo.connect()

    # let's search for metadatas!
    search = isogeo.search(
        query="owner:b81e0b3bc3124deeadbf59ad05c71a2a",
        page_size=10,
        whole_share=0,
        include=["layers", "links", "operations", "serviceLayers"],
    )

    # ------------ Parsing resources ----------------
    md_resources = OrderedDict()
    kind_ogc = ("wfs", "wms", "wmts")
    kind_esri = ("esriFeatureService", "esriMapService", "esriTileService")

    li_ogc_share = []
    li_esri_share = []
    li_dl_share = []

    for md in search.get("results"):
        if md.get("type") == "service":
            print("Services metadatas are excluded.")
            continue
        else:
            pass
        # reset
        md_resources.clear()
        li_ogc_md = []
        li_esri_md = []
        li_dl_md = []
        # annoucing metadata
        print("\n==\t " + md.get("name", md.get("_id")) + " | " + md.get("type"))
        rel_resources = md.get("links")
        rel_layers = md.get("serviceLayers")
        # Associated resources
        if rel_resources:
            md_resources["Associated links"] = len(rel_resources)
            # related resources
            for link in rel_resources:
                # only OGC
                if link.get("kind") in kind_ogc or (
                    link.get("type") == "link"
                    and link.get("link").get("kind") in kind_ogc
                ):
                    li_ogc_md.append((link.get("title"), link.get("url")))
                    md_resources["OGC links"] = len(li_ogc_md)
                    # adding to share list
                    li_ogc_share.extend(li_ogc_md)
                    continue
                else:
                    pass

                # only Esri
                if link.get("kind") in kind_esri or (
                    link.get("type") == "link"
                    and link.get("link").get("kind") in kind_esri
                ):
                    li_esri_md.append((link.get("title"), link.get("url")))
                    md_resources["Esri links"] = len(li_ogc_md)
                    # adding to share list
                    li_esri_share.extend(li_esri_md)
                    continue
                else:
                    pass

                # downloadable
                if (
                    link.get("kind") == "data"
                    and link.get("actions") == "download"
                    or (
                        link.get("type") == "link"
                        and link.get("link").get("kind") == "data"
                    )
                ):
                    li_dl_md.append((link.get("title"), link.get("url")))
                    md_resources["Download links"] = len(li_ogc_md)
                    # adding to share list
                    li_dl_share.extend(li_dl_md)
                    continue
                else:
                    pass

                # secondary
                if link.get("type") == "link":
                    # li_dl.append((link.get('title'), link.get('url')))
                    # print(link.get('kind'))
                    # print(link.get('link'), "\n")
                    continue
                else:
                    pass
        else:
            md_resources["Associated links"] = 0
            pass
        # SERVICE LAYERS
        if rel_layers:
            md_resources["Associated layers"] = len(rel_layers)
            for layer in md.get("serviceLayers"):
                service = layer.get("service")
                if service.get("format") == "wfs":
                    url = "{}?SERVICE={}&VERSION={}&typeNames={}".format(
                        service.get("path", "NONE"),
                        service.get("format").upper(),
                        service.get("formatVersion"),
                        layer.get("id"),
                    )
                    name = layer.get("titles")[0]
                    print(url)
                elif service.get("format") == "wms":
                    url = "{}?SERVICE={}&VERSION={}&layers={}".format(
                        service.get("path", "NONE"),
                        service.get("format").upper(),
                        service.get("formatVersion"),
                        layer.get("id"),
                    )
                    name = layer.get("titles")[0]
                    print(url)

                elif service.get("format") in kind_esri:
                    print("Esri: " + service.get("format"))
                    pass
                else:
                    print("Unknown: " + service.get("format"))
                    pass
        else:
            md_resources["Associated layers"] = 0
            pass

        print(md_resources)

    # print("\n\tOGC: ", li_ogc_share)
    # print("\n\tEsri: ", li_esri_share)
    # print("\n\tDownload: ", li_dl_share)
