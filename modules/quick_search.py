# -*- coding: utf-8 -*-
#! python3  # noqa: E265

# Standard library
import logging
import json
from pathlib import Path

# PyQGIS
from qgis.utils import iface

# PyQT
from qgis.PyQt.QtGui import QIcon

# UI classes
from ..ui.quicksearch.dlg_quicksearch_new import QuicksearchNew
from ..ui.quicksearch.dlg_quicksearch_rename import QuicksearchRename

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
    """A basic class to manage quick searches :
    - Create a new quick search by giving it a name and writing its parameters in the JSON file
    (`_user/quicksearches.json`)
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

        # Getting what the class need from ApiRequester to build search URL
        self.url_builder = object

        # Getting what the class need to build default search request URLs
        self.api_base_url = str

    def fetch_params(self):
        # Write the current parameters in a dict
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

        return params

    def write_params(self, search_name: str = "_default", search_kind: str = "Default"):
        """Write a new element in the json file when a search is saved."""
        # Open the saved_search file as a dict. Each key is a search name,
        # each value is a dict containing the parameters for this search name
        saved_searches = self.load_file()
        # If the name already exists, ask for a new one. ================ TO DO
        if search_kind == "Last":
            params = saved_searches.get(
                "_current", "{}/resources/search?&_limit=0".format(self.api_base_url)
            )
        else:
            params = self.fetch_params()

        saved_searches[search_name] = params
        # writing file
        self.dump_file(saved_searches)
        # Log and messages
        logger.info(
            "{} search stored as '{}'. Parameters: {}".format(search_kind, search_name, params)
        )
        if search_kind != "Current" and search_kind != "Last":
            msgBar.pushMessage(
                self.tr("{} successfully saved: {}", context=__class__.__name__).format(
                    search_kind, search_name
                ),
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
            self.tr("Quicksearch renamed: from {} to {}", context=__class__.__name__).format(
                old_name, new_name
            ),
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
            self.tr("Quicksearch removed: {}", context=__class__.__name__).format(to_remove),
            level=0,
            duration=3,
        )
        # method ending
        logger.debug("'{}' quicksearch removed from JSON file.".format(to_remove))
        return

    def get_default_file_content(self):
        """Return quicksearch.json file default content. usefull to reset JSON file content"""
        default_content = {
            "_default": {
                "contacts": None,
                "datatype": "type:dataset",
                "favorite": None,
                "formats": None,
                "geofilter": None,
                "inspire": None,
                "groupTheme": None,
                "lang": "fr",
                "licenses": None,
                "ob": "relevance",
                "od": "desc",
                "operation": "intersects",
                "owners": None,
                "page": 1,
                "show": True,
                "srs": None,
                "text": "",
                "url": "{}/resources/search?q=type:dataset&ob=relevance&od=desc&_include=serviceLayers,layers,limitations&_limit=10&_offset=0&_lang=fr".format(
                    self.api_base_url
                ),
            }
        }
        return default_content

    def load_file(self):

        try:
            with open(self.json_path, "r") as json_content:
                saved_searches = json.load(json_content)

            if not isinstance(saved_searches, dict):
                logger.warning(
                    "_user/quicksearches.json file content is not correctly formatted : {}.".format(
                        saved_searches
                    )
                )
                logger.warning("Let's replace it with the default content.")
                saved_searches = self.get_default_file_content()
                self.dump_file(saved_searches)
            elif "_default" not in saved_searches:
                logger.warning(
                    "Missing '_default' quicksearch in _user/quicksearches.json file content : {}.".format(
                        saved_searches
                    )
                )
                logger.warning("Let's add the default one.")
                # if default search is missing, let's adding it to JSON file content
                saved_searches["_default"] = self.get_default_file_content().get("_default")
                self.dump_file(saved_searches)
            else:
                for quicksearch in saved_searches:
                    quicksearch_url = saved_searches.get(quicksearch).get("url")
                    if self.api_base_url not in quicksearch_url:
                        default_search_parameters = quicksearch_url.split("/resources/search?")[1]
                        base_search_url = self.api_base_url + "/resources/search?"

                        saved_searches[quicksearch]["url"] = (
                            base_search_url + default_search_parameters
                        )
                        logger.warning(
                            "'{}' quicksearch : URL {} replaced with {}.".format(
                                quicksearch,
                                quicksearch_url,
                                base_search_url + default_search_parameters,
                            )
                        )
                    else:
                        pass
                self.dump_file(saved_searches)

        except Exception as e:
            if not self.json_path.exists() or not self.json_path.is_file():
                logger.warning(
                    "_user/quicksearches.json file can't be used : {} doesn't exist or is not a file : {}".format(
                        str(self.json_path), str(e)
                    )
                )
                logger.warning("Let's create one with default values: {}.".format(self.json_path))
                saved_searches = self.get_default_file_content()
                self.dump_file(saved_searches)
            else:
                logger.error("_user/quicksearches.json file can't be read : {}.".format(str(e)))
                saved_searches = 0

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

    def reset_default_search(self):

        search_name = "_default"
        # fetch current JSON file content
        saved_searches = self.load_file()
        # fetch default search default params
        params = self.get_default_file_content().get(search_name)
        # update JSON file content
        saved_searches[search_name] = params
        self.dump_file(saved_searches)

        # Log and messages
        logger.info("Default search successfully reset.")
        msgBar.pushMessage(
            self.tr("Default search successfully reset.", context=__class__.__name__),
            duration=3,
        )
        return
