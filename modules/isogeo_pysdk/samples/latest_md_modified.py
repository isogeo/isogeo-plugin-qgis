# -*- coding: UTF-8 -*-
#! python3

# ------------------------------------------------------------------------------
# Name:         Isogeo sample - Latest modified datasets
# Purpose:      Get the latest modified datasets from an Isogeo share, using
#               the Isogeo API Python minimalist SDK.
# Author:       Julien Moura (@geojulien)
#
# Python:       3.6.+
# Created:      14/02/2016
# Updated:      18/02/2016
# ------------------------------------------------------------------------------

# ##############################################################################
# ########## Libraries #############
# ##################################

# Isogeo
from isogeo_pysdk import Isogeo

# ############################################################################
# ######### Main program ###########
# ##################################

if __name__ == "__main__":
    """Standalone execution"""
    # standard library
    from os import environ

    # ------------Authentication credentials ----------------
    client_id = environ.get("ISOGEO_API_DEV_ID")
    client_secret = environ.get("ISOGEO_API_DEV_SECRET")

    # ------------ Real start ----------------
    # instanciating the class
    isogeo = Isogeo(client_id=client_id, client_secret=client_secret, lang="fr")
    isogeo.connect()

    # ------------ REAL START ----------------------------
    latest_data_modified = isogeo.search(
        page_size=10, order_by="modified", whole_share=0, include=["events"]
    )

    print("Last 10 data updated \nTitle | datetime\n\t description")
    for md in latest_data_modified.get("results"):
        title = md.get("title")
        evt_description = md.get("events")[0].get("description")
        print(
            str("___________________\n\n{} | {} \n\t {}").format(
                title, md.get("modified")[:10], evt_description.encode("utf8")
            )
        )
