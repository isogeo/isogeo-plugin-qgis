# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

# Standard library
import logging
import json
import os
from functools import partial

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

ico_bolt = QIcon(':/plugins/Isogeo/resources/search/bolt.svg')

# ############################################################################
# ########## Classes ###############
# ##################################

class QuickSearchManager():

    def __init__(self, isogeo_plg):
    
        # Getting wath the class need from Isogeo for the moment
        self.dockwidget = isogeo_plg.dockwidget
        self.save_params = isogeo_plg.save_params
        self.json_path = isogeo_plg.json_path
        self.tr = isogeo_plg.tr
        self.lang = isogeo_plg.lang

        # Getting wath the class need from ApiRequester to build search URL
        self.request_url_builder = object

        # Setting ui elements from plugin dockwidget
        self.btn_save = self.dockwidget.btn_quicksearch_save
        self.btn_rename = self.dockwidget.btn_rename_sr
        self.btn_delete = self.dockwidget.btn_delete_sr
        self.btn_default = self.dockwidget.btn_default_save

        self.dlg_new = QuicksearchNew()
        self.dlg_rename = QuicksearchRename()

        self.cbb_use = self.dockwidget.cbb_quicksearch_use
        self.cbb_edit = self.dockwidget.cbb_quicksearch_edit

        # Connecting ui
        self.btn_save.pressed.connect(self.dlg_new.show)
        self.btn_rename.pressed.connect(self.dlg_rename.show)
        self.btn_delete.pressed.connect(self._remove)
        self.btn_default.pressed.connect(partial(self.write_params, '_default', "Default"))

        self.dlg_new.accepted.connect(self._save)
        self.dlg_rename.accepted.connect(self._rename)

    def write_params(self, search_name, search_kind="Default"):
        """Write a new element in the json file when a search is saved."""
        # Open the saved_search file as a dict. Each key is a search name,
        # each value is a dict containing the parameters for this search name
        with open(self.json_path) as data_file:
            saved_searches = json.load(data_file)
        # If the name already exists, ask for a new one. ================ TO DO

        # Write the current parameters in a dict, and store it in the saved
        # search dict
        params = self.save_params()

        # Info for _offset parameter
        self.page_index = 1
        params['page'] = self.page_index
        # Info for _limit parameter
        params['show'] = True
        # Info for _lang parameter
        params['lang'] = self.lang
        # building request url
        params['url'] = self.request_url_builder(params)

        for i in range(len(params.get('keys'))):
            params['keyword_{0}'.format(i)] = params.get('keys')[i]
        params.pop('keys', None)
        saved_searches[search_name] = params
        # writing file
        with open(self.json_path, 'w') as outfile:
            json.dump(saved_searches, outfile,
                      sort_keys=True, indent=4)
        # Log and messages
        logger.debug("{} search stored: {}. Parameters: {}"
                    .format(search_kind, search_name, params))
        if search_kind != "Current":
            msgBar.pushMessage(self.tr("{} successfully saved: {}")
                                       .format(search_kind, search_name),
                               duration=3)
        else:
            pass
        return
    
    def _save(self):
        """Call the write_search() function and refresh the combobox."""
        # retrieve quicksearch given name and store it
        search_name = self.dlg_new.txt_quicksearch_name.text()
        self.write_params(search_name, search_kind="Quicksearch")
        # load all saved quicksearches and populate drop-down (combobox)
        with open(self.json_path, "r") as saved_searches_file:
            saved_searches = json.load(saved_searches_file)
        search_list = list(saved_searches.keys())
        search_list.pop(search_list.index('_default'))
        search_list.pop(search_list.index('_current'))
        self.cbb_use.clear()
        self.cbb_use.addItem(ico_bolt, self.tr('Quick Search'))
        self.cbb_edit.clear()
        for i in search_list:
            self.cbb_use.addItem(i, i)
            self.cbb_edit.addItem(i, i)
        # method ending
        return
    
    def _rename(self):
        """Modify the json file in order to rename a search."""
        old_name = self.cbb_edit.currentText()
        with open(self.json_path, "r") as saved_searches_file:
            saved_searches = json.load(saved_searches_file)
        new_name = self.dlg_rename.txt_quicksearch_rename.text()
        saved_searches[new_name] = saved_searches[old_name]
        saved_searches.pop(old_name)
        search_list = list(saved_searches.keys())
        search_list.pop(search_list.index('_default'))
        search_list.pop(search_list.index('_current'))
        self.cbb_use.clear()
        self.cbb_use.addItem(ico_bolt, self.tr('Quick Search'))
        self.cbb_edit.clear()
        for i in search_list:
            self.cbb_use.addItem(i, i)
            self.cbb_edit.addItem(i, i)
        # Update JSON file
        with open(self.json_path, 'w') as outfile:
            json.dump(saved_searches, outfile,
                      sort_keys=True, indent=4)
        # inform user
        msgBar.pushMessage("Isogeo",
                           self.tr("Quicksearch renamed: from {} to {}")
                                   .format(old_name, new_name),
                           level=0,
                           duration=3)
        # method ending
        return

    def _remove(self):
        """Modify the json file in order to delete a search."""
        to_be_deleted = self.cbb_edit.currentText()
        with open(self.json_path, "r") as saved_searches_file:
            saved_searches = json.load(saved_searches_file)
        saved_searches.pop(to_be_deleted)
        search_list = list(saved_searches.keys())
        search_list.pop(search_list.index('_default'))
        search_list.pop(search_list.index('_current'))
        self.cbb_use.clear()
        self.cbb_use.addItem(ico_bolt, self.tr('Quick Search'))
        self.cbb_edit.clear()
        for i in search_list:
            self.cbb_use.addItem(i, i)
            self.cbb_edit.addItem(i, i)
        # Update JSON file
        with open(self.json_path, 'w') as outfile:
            json.dump(saved_searches, outfile,
                      sort_keys=True, indent=4)
        # inform user
        msgBar.pushMessage("Isogeo",
                           self.tr("Quicksearch removed: {}")
                                   .format(to_be_deleted),
                           level=0,
                           duration=3)
        # method ending
        return