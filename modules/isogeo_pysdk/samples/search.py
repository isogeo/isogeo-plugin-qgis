# -*- coding: UTF-8 -*-
#! python3

# -----------------------------------------------------------------------------
# Name:         Isogeo
# Purpose:      Python minimalist SDK to use Isogeo API
#
# Author:       Julien Moura (@geojulien)
#
# Python:       3.6+
# Created:      22/12/2015
# Updated:      10/01/2016
# -----------------------------------------------------------------------------

# #############################################################################
# ########## Libraries #############
# ##################################

# Standard library
from random import randrange  # to get a random resource

# Isogeo
from isogeo_pysdk import Isogeo
from isogeo_pysdk import IsogeoTranslator

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
    search = isogeo.search()

    print(sorted(search.keys()))
    print(search.get("query"))
    print("Total count of metadatas shared: ", search.get("total"))
    print("Count of resources got by request: {}\n".format(len(search.get("results"))))

    # get one random resource
    hatnumber = randrange(0, len(search.get("results")))
    my_resource = isogeo.resource(
        search.get("results")[hatnumber].get("_id"), include="all", prot="https"
    )

    print(sorted(my_resource.keys()))

    # use integrated translator
    tr = IsogeoTranslator("FR")
    if my_resource.get("contacts"):
        ct = my_resource.get("contacts")[0]
        print("\nRaw contact role: " + ct.get("role"))
        # English
        tr = IsogeoTranslator("EN")
        print("English contact role: " + tr.tr("roles", ct.get("role")))
        # French
        tr = IsogeoTranslator("FR")
        print("Rôle du contact en français: " + tr.tr("roles", ct.get("role")))
    else:
        print("This resource doesn't have any contact. Try again!")
