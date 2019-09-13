# -*- coding: UTF-8 -*-
#! python3

# ------------------------------------------------------------------------------
# Name:         Isogeo sample - Offline parser
# Purpose:      Exports each of 10 last updated metadata into an XML ISO19139
# Author:       Julien Moura (@geojulien)
#
# Python:       3.6+
# Created:      02/11/2017
# ------------------------------------------------------------------------------

# ##############################################################################
# ########## Libraries #############
# ##################################

# Standard library
import json
from os import path
from collections import defaultdict
import sys

# ############################################################################
# ########## Functions #############
# ##################################


def search_tags_as_filters(tags):
    """Get different tags as dicts ready to use as dropdown lists."""
    # set dicts
    actions = {}
    contacts = {}
    formats = {}
    inspire = {}
    keywords = {}
    licenses = {}
    md_types = dict()
    owners = defaultdict(str)
    srs = {}
    unused = {}
    # 0/1 values
    compliance = 0
    type_dataset = 0
    # parsing tags
    print(len(tags.keys()))
    i = 0
    for tag in sorted(tags.keys()):
        i += 1
        # actions
        if tag.startswith("action"):
            actions[tags.get(tag, tag)] = tag
            continue
        # compliance INSPIRE
        elif tag.startswith("conformity"):
            compliance = 1
            continue
        # contacts
        elif tag.startswith("contact"):
            contacts[tags.get(tag)] = tag
            continue
        # formats
        elif tag.startswith("format"):
            formats[tags.get(tag)] = tag
            continue
        # INSPIRE themes
        elif tag.startswith("keyword:inspire"):
            inspire[tags.get(tag)] = tag
            continue
        # keywords
        elif tag.startswith("keyword:isogeo"):
            keywords[tags.get(tag)] = tag
            continue
        # licenses
        elif tag.startswith("license"):
            licenses[tags.get(tag)] = tag
            continue
        # owners
        elif tag.startswith("owner"):
            owners[tags.get(tag)] = tag
            continue
        # SRS
        elif tag.startswith("coordinate-system"):
            srs[tags.get(tag)] = tag
            continue
        # types
        elif tag.startswith("type"):
            md_types[tags.get(tag)] = tag
            if tag in ("type:vector-dataset", "type:raster-dataset"):
                type_dataset += 1
            else:
                pass
            continue
        # ignored tags
        else:
            unused[tags.get(tag)] = tag
            continue

    # override API tags to allow all datasets filter - see #
    if type_dataset == 2:
        md_types["Donnée"] = "type:dataset"
    else:
        pass
    # printing
    # print("There are:"
    #       "\n{} actions"
    #       "\n{} contacts"
    #       "\n{} formats"
    #       "\n{} INSPIRE themes"
    #       "\n{} keywords"
    #       "\n{} licenses"
    #       "\n{} owners"
    #       "\n{} SRS"
    #       "\n{} types"
    #       "\n{} unused".format(len(actions),
    #                            len(contacts),
    #                            len(formats),
    #                            len(inspire),
    #                            len(keywords),
    #                            len(licenses),
    #                            len(owners),
    #                            len(srs),
    #                            len(md_types),
    #                            len(unused)
    #                            ))
    # storing dicts
    tags_parsed = {
        "actions": actions,
        "compliance": compliance,
        "contacts": contacts,
        "formats": formats,
        "inspire": inspire,
        "keywords": keywords,
        "licenses": licenses,
        "owners": owners,
        "srs": srs,
        "types": md_types,
        "unused": unused,
    }

    # method ending
    return tags_parsed


# ############################################################################
# ######### Main program ###########
# ##################################

if __name__ == "__main__":
    """Standalone execution"""
    # check file presence
    if not path.isfile("out_api_search_empty.json"):
        print("Input file not found." "You should first execute store_api_responses.py")
        sys.exit()
    else:
        pass

    # open and read JSON
    with open("out_api_search_empty.json") as data_file:
        data = json.load(data_file)

    # check data type
    if not type(data) == dict:
        print("Bad file type.")
        print(type(data))
        sys.exit()
    else:
        pass

    # TAGS
    tags = data.get("tags")
    filters = search_tags_as_filters(tags)
    print(type(filters), filters.keys())
    licenses = filters.get("licenses")
    owners = filters.get("owners")
    print(sorted(owners.keys()))
    print("END")
