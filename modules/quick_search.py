# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

# Standard library
import logging
import json
from functools import partial
from pathlib import Path

# PyQGIS
from qgis.utils import iface

# PyQT
from qgis.PyQt.QtGui import QIcon

# UI classes
from ..ui.quicksearch.dlg_quicksearch_new import QuicksearchNew
from ..ui.quicksearch.dlg_quicksearch_rename import QuicksearchRename

# Plugin modules
from .api import ApiRequester

# ############################################################################
# ########## Globals ###############
# ##################################

logger = logging.getLogger("IsogeoQgisPlugin")

msgBar = iface.messageBar()

ico_bolt = QIcon(":/plugins/Isogeo/resources/search/bolt.svg")

# ############################################################################
# ########## Classes ###############
# ##################################


class QuickSearchManager:
    """ A basic class to manage quick searches :
        - Create a new quick search by giving it a name and writing its parameters in the JSON file (`_user/quicksearches.json`)
        - Rename a quick search
        - Delete a quick search
    """

    def __init__(self, search_form_manager: object = None):

        if search_form_manager:
            # Getting wath the class need from Isogeo
            self.form_mng = search_form_manager
            self.tr = self.form_mng.tr
            self.lang = str

            # Setting ui elements
            self.dlg_new = QuicksearchNew()
            self.dlg_rename = QuicksearchRename()

            # Connecting ui
            self.dlg_new.accepted.connect(self.save)
            self.dlg_rename.accepted.connect(self.rename)
        else:
            pass

        # path to json storage file for quicksearch
        self.json_path = Path(__file__).parents[1] / "_user" / "quicksearches.json"

        # Getting wath the class need from ApiRequester to build search URL
        self.url_builder = object

    def write_params(self, search_name: str = "_default", search_kind: str = "Default"):
        """Write a new element in the json file when a search is saved."""
        # Open the saved_search file as a dict. Each key is a search name,
        # each value is a dict containing the parameters for this search name
        saved_searches = self.load_file()
        # If the name already exists, ask for a new one. ================ TO DO
        if search_kind == "Last":
            params = saved_searches.get(
                "_current", "https://api.isogeo.com/resources/search?&_limit=0"
            )
        else:
            # Write the current parameters in a dict, and store it in the saved
            # search dict
            params = self.form_mng.save_params()
            # Info for _offset parameter
            self.page_index = 1
            params["page"] = self.page_index
            # Info for _limit parameter
            params["show"] = True
            # Info for _lang parameter
            params["lang"] = self.lang
            # building request url
            params["url"] = self.url_builder(params)

            for i in range(len(params.get("keys"))):
                params["keyword_{0}".format(i)] = params.get("keys")[i]
            params.pop("keys", None)

        saved_searches[search_name] = params
        # writing file
        self.dump_file(saved_searches)
        # Log and messages
        logger.debug(
            "{} search stored: {}. Parameters: {}".format(
                search_kind, search_name, params
            )
        )
        if search_kind != "Current" and search_kind != "Last":
            msgBar.pushMessage(
                self.tr("{} successfully saved: {}").format(search_kind, search_name),
                duration=3,
            )
        else:
            pass
        return

    def save(self):
        """Call the write_search() function and refresh the combobox."""
        # retrieve quicksearch given name and store it
        search_name = self.dlg_new.txt_quicksearch_name.text()
        self.write_params(search_name, search_kind="Quicksearch")
        # load all saved quicksearches and populate drop-down (combobox)
        saved_searches = self.load_file()
        search_list = list(saved_searches.keys())
        # updating quick search widgets
        self.form_mng.pop_qs_cbbs(items_list=search_list)
        # method ending
        return

    def rename(self):
        """Modify the json file in order to rename a search."""
        old_name = self.form_mng.cbb_quicksearch_edit.currentText()
        new_name = self.dlg_rename.txt_quicksearch_rename.text()

        saved_searches = self.load_file()
        saved_searches[new_name] = saved_searches[old_name]
        saved_searches.pop(old_name)
        search_list = list(saved_searches.keys())
        self.form_mng.pop_qs_cbbs(items_list=search_list)
        # Update JSON file
        self.dump_file(content=saved_searches)
        # inform user
        msgBar.pushMessage(
            "Isogeo",
            self.tr("Quicksearch renamed: from {} to {}").format(old_name, new_name),
            level=0,
            duration=3,
        )
        # method ending
        logger.debug("'{}' quicksearch renamed '{}'".format(old_name, new_name))
        return

    def remove(self):
        """Modify the json file in order to delete a search."""
        to_remove = self.form_mng.cbb_quicksearch_edit.currentText()
        saved_searches = self.load_file()
        saved_searches.pop(to_remove)
        search_list = list(saved_searches.keys())
        # updating quick search widgets
        self.form_mng.pop_qs_cbbs(items_list=search_list)
        # Update JSON file
        self.dump_file(content=saved_searches)
        # inform user
        msgBar.pushMessage(
            "Isogeo",
            self.tr("Quicksearch removed: {}").format(to_remove),
            level=0,
            duration=3,
        )
        # method ending
        logger.debug("'{}' quicksearch removed from JSON file.".format(to_remove))
        return

    def load_file(self):
        with open(self.json_path, "r") as saved_searches_file:
            saved_searches = json.load(saved_searches_file)
        logger.debug(
            "{} quicksearche(s) found : {}".format(
                len(saved_searches.keys()), list(saved_searches.keys())
            )
        )
        return saved_searches

    def dump_file(self, content: dict):
        with open(self.json_path, "w") as outfile:
            json.dump(content, outfile, sort_keys=True, indent=4)
        return
