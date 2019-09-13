# -*- coding: UTF-8 -*-
#! python3

# ------------------------------------------------------------------------------
# Name:         Isogeo sample - Batch export to XML ISO19139
# Purpose:      Exports each of 10 last updated metadata into an XML ISO19139
# Author:       Isogeo
#
# Python:       3.5+
# Created:      14/11/2016
# Updated:      15/04/2019
# ------------------------------------------------------------------------------

# ##############################################################################
# ########## Libraries #############
# ##################################

# Standard library
from os import environ
from pathlib import Path
from timeit import default_timer

# Isogeo
from isogeo_pysdk import Isogeo

# #############################################################################
# ########## Globals ###############
# ##################################

# required subfolders
out_dir = Path("_output/")
out_dir.mkdir(exist_ok=True)

# ############################################################################
# ######### Main program ###########
# ##################################

if __name__ == "__main__":
    """Standalone execution"""
    chrono_start = default_timer()  # chrono

    # Authentication #########
    app_id = environ.get("ISOGEO_API_DEV_ID")
    app_token = environ.get("ISOGEO_API_DEV_SECRET")

    # start Isogeo
    isogeo = Isogeo(client_id=app_id, client_secret=app_token)

    # getting a token
    token = isogeo.connect()

    # Process #########
    latest_data_modified = isogeo.search(
        token, page_size=10, order_by="modified", whole_share=0
    )

    for md in latest_data_modified.get("results"):
        title = md.get("title")
        xml_stream = isogeo.xml19139(token, md.get("_id"))

        with open(out_dir / "{}.xml".format(title), "wb") as fd:
            for block in xml_stream.iter_content(1024):
                fd.write(block)

    # chrono
    chrono_end = default_timer()
    print("Done in: {:5.2f}s".format(chrono_end - chrono_start))
