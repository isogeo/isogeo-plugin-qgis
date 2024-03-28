# -*- coding: utf-8 -*-
#! python3  # noqa: E265

# Standard library
import logging
import json
from pathlib import Path
from functools import partial

# PyQGIS
from qgis.utils import iface

# PyQT
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QMessageBox

# UI classes
from ..ui.quicksearch.dlg_quicksearch_new import QuicksearchNew
from ..ui.quicksearch.dlg_quicksearch_rename import QuicksearchRename

# submodule
from .settings_manager import SettingsManager

# ############################################################################
# ########## Globals ###############
# ##################################

logger = logging.getLogger("IsogeoQgisPlugin")

msgBar = iface.messageBar()

settings_mng = SettingsManager()

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
            self.dlg_new.accepted.connect(partial(self.check_already_exist, 0))
            self.dlg_rename.accepted.connect(partial(self.check_already_exist, 1))
        else:
            pass

        # path to json storage file for quicksearch
        self.json_path = Path(__file__).parents[1] / "_user" / "quicksearches.json"

        # Getting what the class need from ApiRequester to build search URL
        self.url_builder = object

        # Getting what the class need to build default search request URLs
        self.api_base_url = str

    def api_base_url_setter(self, value: str):
        self.api_base_url = value
        self.customize_settings_manager()

    def customize_settings_manager(self):
        settings_mng.api_base_url = self.api_base_url
        settings_mng.tr = self.tr
        settings_mng.load_quicksearches()
        logger.debug("SettingsManager initialized for quicksearches handling.")

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

        # If the name already exists, ask for a new one. ================ TO DO
        if search_kind == "Last":
            if search_name == "Last search" and "Dernière recherche" in self.get_quicksearches_names():
                settings_mng.remove_quicksearch("Dernière recherche")
            elif search_name == "Dernière recherche" and "Last search" in self.get_quicksearches_names():
                settings_mng.remove_quicksearch("Last search")
            else:
                pass
            # writing file
            settings_mng.save_quicksearch(
                search_name,
                settings_mng.quicksearches_content.get("_current", "{}/resources/search?&_limit=0".format(self.api_base_url))
            )
        else:
            # writing file
            settings_mng.save_quicksearch(search_name, self.fetch_params())

        # Log and messages
        logger.info(
            "{} search stored as '{}'.".format(search_kind, search_name)
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

    def check_already_exist(self, rename: bool = 0):

        if rename:
            search_name = self.dlg_rename.txt_quicksearch_rename.text()
            popup_title = self.tr("Isogeo - Rename quicksearch", __class__.__name__,)
            slot_func = self.rename
        else:
            search_name = self.dlg_new.txt_quicksearch_name.text()
            popup_title = self.tr("Isogeo - New quicksearch", __class__.__name__,)
            slot_func = self.save

        if search_name in self.get_quicksearches_names():
            popup = QMessageBox()
            popup.setWindowIcon(ico_bolt)
            popup.setWindowTitle(popup_title)
            popup.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            popup.setDefaultButton(QMessageBox.No)
            popup_txt = (
                "<b>{}</b>".format(
                    self.tr("Quicksearch '{}' already exists, do you want to overwrite it?", __class__.__name__,).format(search_name)
                )
            )
            popup.setText(popup_txt)
            popup.finished.connect(slot_func)
            popup.exec()
        else:
            slot_func(QMessageBox.Yes)

        return

    def save(self, i):
        """Call the write_params() function and refresh the combobox."""
        # retrieve quicksearch given name and store it
        if i == QMessageBox.Yes:
            search_name = self.dlg_new.txt_quicksearch_name.text()
            self.dlg_new.txt_quicksearch_name.setText("")
            self.write_params(search_name, search_kind="Quicksearch")
            # updating quick search widgets
            self.form_mng.pop_qs_cbbs(items_list=self.get_quicksearches_names())
            # method ending
            return
        else:
            return

    def rename(self, i):
        """Modify the json file in order to rename a search."""
        if i == QMessageBox.Yes:

            old_name = self.form_mng.cbb_quicksearch_edit.currentText()
            new_name = self.dlg_rename.txt_quicksearch_rename.text()
            self.dlg_rename.txt_quicksearch_rename.setText("")

            settings_mng.rename_quicksearch(old_name, new_name)
            # Update quick search widgets
            self.form_mng.pop_qs_cbbs(items_list=self.get_quicksearches_names())

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
        else:
            return

    def remove(self):
        """Modify the json file in order to delete a search."""

        to_remove = self.form_mng.cbb_quicksearch_edit.currentText()
        settings_mng.remove_quicksearch(to_remove)
        # Update quick search widgets
        self.form_mng.pop_qs_cbbs(items_list=self.get_quicksearches_names())

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

    def reset_default_search(self):

        search_name = "_default"

        settings_mng.save_quicksearch(
            search_name, settings_mng.get_default_quicksearch_content().get(search_name)
        )

        # Log and messages
        logger.info("Default search successfully reset.")
        msgBar.pushMessage(
            self.tr("Default search successfully reset.", context=__class__.__name__),
            duration=3,
        )

    def get_quicksearches(self):

        return settings_mng.quicksearches_content

    def get_quicksearches_names(self):

        saved_searches_names = list(self.get_quicksearches().keys())

        logger.debug(
            "{} quicksearch(es) found : {}".format(
                len(saved_searches_names), saved_searches_names
            )
        )

        return saved_searches_names