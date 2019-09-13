# -*- coding: UTF-8 -*-
#! python3

# ------------------------------------------------------------------------------
# Name:         Isogeo sample - Get OpenCatalog if exists in shares

# Author:       Julien Moura (@geojulien)
#
# Python:       2.7.x
# Created:      14/02/2016
# Updated:      18/02/2016
# ------------------------------------------------------------------------------

# ##############################################################################
# ########## Libraries #############
# ##################################

# 3rd party library
import requests

# Isogeo
from isogeo_pysdk import Isogeo

# ############################################################################
# ######### Main program ###########
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

    # ------------ REAL START ----------------------------
    shares = isogeo.shares()
    print("This application is supplied by {} shares: ".format(len(shares)))

    for share in shares:
        # Share caracteristics
        name = share.get("name").encode("utf8")
        creator_name = share.get("_creator").get("contact").get("name")
        creator_id = share.get("_creator").get("_tag")[6:]
        print("\nShare name: ", name, " owned by workgroup ", creator_name)

        # OpenCatalog URL construction
        share_details = isogeo.share(share_id=share.get("_id"))
        url_OC = "http://open.isogeo.com/s/{}/{}".format(
            share.get("_id"), share_details.get("urlToken")
        )

        # Testing URL
        request = requests.get(url_OC)
        if request.status_code == 200:
            print("OpenCatalog available at: ", url_OC)
        else:
            print(
                "OpenCatalog is not set for this share."
                "\nGo and add it: https://app.isogeo.com/groups/{}/admin/shares/{}".format(
                    creator_id, share.get("_id")
                )
            )
