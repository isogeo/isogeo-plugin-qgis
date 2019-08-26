# -*- coding: utf-8 -*-

# Standard library
import logging
import json
from functools import partial
from collections import OrderedDict

# PyQGIS
from qgis.core import QgsMessageLog
from qgis.utils import iface

# PyQT
from qgis.PyQt.QtCore import QByteArray, QUrl, QObject, pyqtSignal, pyqtSlot
from qgis.PyQt.QtNetwork import QNetworkRequest, QNetworkAccessManager, QNetworkReply
from qgis.PyQt.QtGui import QIcon

# UI classe
from ..ui.isogeo_dockwidget import IsogeoDockWidget  # main widget

# submodule
from .tools import IsogeoPlgTools

# ############################################################################
# ########## Globals ###############
# ##################################

logger = logging.getLogger("IsogeoQgisPlugin")
msgBar = iface.messageBar()

plg_tools = IsogeoPlgTools()

dict_operation = OrderedDict([(self.tr(
    'Intersects'), "intersects"),
    (self.tr('within'), "within"),
    (self.tr('contains'), "contains")])

dict_ob = OrderedDict([(self.tr("Relevance"), (ico_ob_relev, "relevance")),
    (self.tr("Alphabetical order"), (ico_ob_alpha, "title")),
    (self.tr("Data modified"), (ico_ob_dupda, "modified")),
    (self.tr("Data created"), (ico_ob_dcrea, "created")),
    (self.tr("Metadata modified"), (ico_ob_mcrea, "_modified")),
    (self.tr("Metadata created"), (ico_ob_mupda, "_created"))])

# icons
ico_od_asc = QIcon(':/plugins/Isogeo/resources/results/sort-alpha-asc.svg')
ico_od_desc = QIcon(':/plugins/Isogeo/resources/results/sort-alpha-desc.svg')
ico_ob_relev = QIcon(":/plugins/Isogeo/resources/results/star.svg")
ico_ob_alpha = QIcon(':/plugins/Isogeo/resources/metadata/language.svg')
ico_ob_dcrea = QIcon(':/plugins/Isogeo/resources/datacreated.svg')
ico_ob_dupda = QIcon(':/plugins/Isogeo/resources/datamodified.svg')
ico_ob_mcrea = QIcon(':/plugins/Isogeo/resources/calendar-plus-o.svg')
ico_ob_mupda = QIcon(':/plugins/Isogeo/resources/calendar_blue.svg')
ico_bolt = QIcon(':/plugins/Isogeo/resources/search/bolt.svg')
ico_keyw = QIcon(':/plugins/Isogeo/resources/tag.svg')
ico_none = QIcon(':/plugins/Isogeo/resources/none.svg')
ico_line = QIcon(':/images/themes/default/mIconLineLayer.svg')
ico_log = QIcon(":/images/themes/default/mActionFolder.svg")
ico_poin = QIcon(':/images/themes/default/mIconPointLayer.svg')
ico_poly = QIcon(':/images/themes/default/mIconPolygonLayer.svg')

# ############################################################################
# ########## Classes ###############
# ##################################

class SearchFormManager():
    """
    """
    fields_ready = pyqtSignal()

    def __init__(self):
        # inheritance
        self.dockwidget = IsogeoDockWidget()

        self.tr = object

    def update_fields(self, result: dict):
        """Update search form fields from search tags and previous search.
        Slot connected to ApiRequster.search_sig (see modules/api/requester.py)
        This takes an API answer ('result' parameter) and update the fields 
        accordingly. It also calls show_results in the end. This may change,  
        so results would be shown only when a specific button is pressed.

        :param dict result: Parsed content of search request's reply
        """
        logger.debug("Update_fields function called on the API reply. reset = "
                     "{}".format(self.hardReset))
        QgsMessageLog.logMessage("Query sent & received: {}"
                                 .format(result.get("query")),
                                 "Isogeo")
        # getting and parsing tags
        tags = self.authenticator.get_tags(result.get("tags"))
        # save entered text and filters in search form
        self.old_text = self.dockwidget.txt_input.text()
        params = self.save_params()

        # Show how many results there are
        self.results_count = result.get('total')
        self.dockwidget.btn_show.setText(
            str(self.results_count) + self.tr(" results"))
        page_count = str(plg_tools.results_pages_counter(total=self.results_count))
        self.dockwidget.lbl_page.setText(
            "page " + str(self.page_index) + self.tr(' on ') + page_count)

        # ALIASES FOR FREQUENTLY CALLED WIDGETS
        cbb_contact = self.dockwidget.cbb_contact  # contact
        cbb_format = self.dockwidget.cbb_format  # formats
        cbb_geofilter = self.dockwidget.cbb_geofilter  # geographic
        cbb_geo_op = self.dockwidget.cbb_geo_op  # geometric operator
        cbb_inspire = self.dockwidget.cbb_inspire  # INSPIRE themes
        cbb_license = self.dockwidget.cbb_license  # license
        cbb_ob = self.dockwidget.cbb_ob  # sort parameter
        cbb_od = self.dockwidget.cbb_od  # sort direction
        cbb_owner = self.dockwidget.cbb_owner  # owners
        cbb_quicksearch_use = self.dockwidget.cbb_quicksearch_use  # quick searches
        cbb_srs = self.dockwidget.cbb_srs  # coordinate systems
        cbb_type = self.dockwidget.cbb_type  # metadata type
        tbl_result = self.dockwidget.tbl_result  # results table
        txt_input = self.dockwidget.txt_input  # search terms

        # RESET WiDGETS
        for cbb in self.cbbs_search_advanced:
            cbb.clear()
        tbl_result.clearContents()
        tbl_result.setRowCount(0)

        # Quicksearches combobox (also the one in settings tab)
        with open(self.json_path) as data_file:
            saved_searches = json.load(data_file)
        search_list = list(saved_searches.keys())
        search_list.pop(search_list.index('_default'))
        if '_current' in search_list:
            search_list.pop(search_list.index('_current'))
        cbb_quicksearch_use.clear()
        self.dockwidget.cbb_quicksearch_edit.clear()
        cbb_quicksearch_use.addItem(ico_bolt, self.tr('Quicksearches'))
        for i in search_list:
            cbb_quicksearch_use.addItem(i, i)
            self.dockwidget.cbb_quicksearch_edit.addItem(i, i)

        # Advanced search comboboxes (filters others than keywords)
        # Initiating the "nothing selected"
        for cbb in self.cbbs_search_advanced:
            cbb.addItem(" - ")
        # Initializing the cbb that dont't need to be updated
        if self.savedSearch == "_default" or self.hardReset is True:
            logger.debug("Default search or reset.")
            tbl_result.horizontalHeader().setSectionResizeMode(1)
            tbl_result.horizontalHeader().setSectionResizeMode(1, 0)
            tbl_result.horizontalHeader().setSectionResizeMode(2, 0)
            tbl_result.horizontalHeader().resizeSection(1, 80)
            tbl_result.horizontalHeader().resizeSection(2, 50)
            tbl_result.verticalHeader().setSectionResizeMode(3)
            # Geographical operator cbb
            for key in dict_operation.keys():
                cbb_geo_op.addItem(key, dict_operation.get(key))

            # Order by cbb
            for k, v in dict_ob.items():
                cbb_ob.addItem(v[0], k, v[1])

            # Order direction cbb
            dict_od = OrderedDict([(self.tr("Descending"), (ico_od_desc, "desc")),
                                   (self.tr("Ascending"), (ico_od_asc, "asc"))]
                                  )

            for k, v in dict_od.items():
                cbb_od.addItem(v[0], k, v[1])
        else:
            logger.debug("Not default search nor reset.")
            pass

        # Filling comboboxes from tags
        # Owners
        md_owners = tags.get("owners")
        for i in md_owners:
            cbb_owner.addItem(i, md_owners.get(i))
        # INSPIRE themes
        inspire = tags.get("inspire")
        for i in inspire:
            cbb_inspire.addItem(i, inspire.get(i))
        # Formats
        formats = tags.get("formats")
        for i in formats:
            cbb_format.addItem(i, formats.get(i))
        # Coordinate system
        srs = tags.get("srs")
        for i in srs:
            cbb_srs.addItem(i, srs.get(i))
        # Contacts
        contacts = tags.get("contacts")
        for i in contacts:
            cbb_contact.addItem(i, contacts.get(i))
        # Licenses
        licenses = tags.get("licenses")
        for i in licenses:
            cbb_license.addItem(i, licenses.get(i))
        # Resource type
        md_types = tags.get("types")
        for i in md_types:
            cbb_type.addItem(i, md_types.get(i))
        # Geographical filter
        cbb_geofilter.addItem(self.tr("Map canvas"), "mapcanvas")
        layers = QgsProject.instance().mapLayers().values()
        for layer in layers:
            if layer.type() == 0:
                if layer.geometryType() == 2:
                    cbb_geofilter.addItem(ico_poly, layer.name())
                elif layer.geometryType() == 1:
                    cbb_geofilter.addItem(ico_line, layer.name())
                elif layer.geometryType() == 0:
                    cbb_geofilter.addItem(ico_poin, layer.name())

        # sorting comboboxes
        for cbb in self.cbbs_search_advanced:
            cbb.model().sort(0)
     
        # Putting all the comboboxes selected index to their previous
        # location. Necessary as all comboboxes items have been removed and
        # put back in place. We do not want each combobox to go back to their
        # default selected item
        if self.hardReset is False:
            logger.debug("Classical search or quicksearch (no reset search)")
            if self.savedSearch is False:
                logger.debug("Classic search case (not quicksearch)")
                # Owners
                previous_index = cbb_owner.findData(params.get('owner'))
                cbb_owner.setCurrentIndex(previous_index)
                # Inspire keywords
                previous_index = cbb_inspire.findData(params.get('inspire'))
                cbb_inspire.setCurrentIndex(previous_index)
                # Data type
                previous_index = cbb_type.findData(params.get('datatype'))
                cbb_type.setCurrentIndex(previous_index)
                # Data format
                previous_index = cbb_format.findData(params.get('format'))
                cbb_format.setCurrentIndex(previous_index)
                # Coordinate system
                previous_index = cbb_srs.findData(params.get('srs'))
                cbb_srs.setCurrentIndex(previous_index)
                # Contact
                previous_index = cbb_contact.findData(params.get('contact'))
                cbb_contact.setCurrentIndex(previous_index)
                # License
                previous_index = cbb_license.findData(params.get('license'))
                cbb_license.setCurrentIndex(previous_index)
                # Sorting order
                cbb_ob.setCurrentIndex(cbb_ob.findData(params.get('ob')))
                # Sorting direction
                cbb_od.setCurrentIndex(cbb_od.findData(params.get('od')))
                # Quick searches
                previous_index = cbb_quicksearch_use.findData(params.get('favorite'))
                cbb_quicksearch_use.setCurrentIndex(previous_index)
                # Operator for geographical filter
                previous_index = cbb_geo_op.findData(params.get('operation'))
                cbb_geo_op.setCurrentIndex(previous_index)
                # Geographical filter
                if params.get('geofilter') == "mapcanvas":
                    previous_index = cbb_geofilter.findData("mapcanvas")
                    cbb_geofilter.setCurrentIndex(previous_index)
                else:
                    prev_index = cbb_geofilter.findText(params['geofilter'])
                    cbb_geofilter.setCurrentIndex(prev_index)
                # Filling the keywords special combobox (items checkable)
                # In the case where it isn't a saved research. So we have to
                # check the items that were previously checked
                self.update_cbb_keywords(tags_keywords=tags.get('keywords'),
                                         selected_keywords=params.get('keys'))
            # When it is a saved research, we have to look in the json, and
            # check the items accordingly (quite close to the previous case)
            else:
                logger.debug("Quicksearch case: {}".format(self.savedSearch))
                # Opening the json to get keywords
                with open(self.json_path) as data_file:
                    saved_searches = json.load(data_file)
                search_params = saved_searches.get(self.savedSearch)
                keywords_list = [v for k,v in search_params.items() if k.startswith("keyword")]
                self.update_cbb_keywords(tags_keywords=tags.get('keywords'),
                                         selected_keywords=keywords_list)
                # Putting widgets to their previous states according
                # to the json content
                # Line edit content
                txt_input.setText(search_params.get('text'))
                # Owners
                saved_index = cbb_owner.findData(search_params.get('owner'))
                cbb_owner.setCurrentIndex(saved_index)
                # Inspire keywords
                value = search_params.get('inspire')
                saved_index = cbb_inspire.findData(value)
                cbb_inspire.setCurrentIndex(saved_index)
                # Formats
                saved_index = cbb_format.findData(search_params.get('format'))
                cbb_format.setCurrentIndex(saved_index)
                # Coordinate systems
                saved_index = cbb_srs.findData(search_params.get('srs'))
                cbb_srs.setCurrentIndex(saved_index)
                # Contact
                saved_index = cbb_contact.findData(search_params.get('contact'))
                cbb_contact.setCurrentIndex(saved_index)
                # License
                saved_index = cbb_license.findData(search_params.get('license'))
                cbb_license.setCurrentIndex(saved_index)
                # Geographical filter
                value = search_params.get('geofilter')
                saved_index = cbb_geofilter.findData(value)
                cbb_geofilter.setCurrentIndex(saved_index)
                # Operator for the geographical filter
                value = search_params.get('operation')
                saved_index = cbb_geo_op.findData(value)
                cbb_geo_op.setCurrentIndex(saved_index)
                # Data type
                saved_index = cbb_type.findData(search_params.get('datatype'))
                cbb_type.setCurrentIndex(saved_index)
                # Sorting order
                saved_index = cbb_ob.findData(search_params.get('ob'))
                cbb_ob.setCurrentIndex(saved_index)
                # Sorting direction
                saved_index = cbb_od.findData(search_params.get('od'))
                cbb_od.setCurrentIndex(saved_index)
                # Quick searches
                if self.savedSearch != "_default":
                    saved_index = cbb_quicksearch_use.findData(self.savedSearch)
                    cbb_quicksearch_use.setCurrentIndex(saved_index)
                self.savedSearch = False

        # In case of a hard reset, we don't have to worry about widgets
        # previous state as they are to be reset
        else:
            logger.debug("Reset search")
            self.update_cbb_keywords(tags_keywords=tags.get('keywords'))

        # tweaking
        plg_tools._ui_tweaker(ui_widgets=self.dockwidget.tab_search.findChildren(QComboBox))

        # Coloring the Show result button
        self.dockwidget.btn_show.setStyleSheet(
            "QPushButton "
            "{background-color: rgb(255, 144, 0); color: white}")

        # Show result, if we want them to be shown (button 'show result', 'next
        # page' or 'previous page' pressed)
        if self.showResult is True:
            self.dockwidget.btn_next.setEnabled(True)
            self.dockwidget.btn_previous.setEnabled(True)
            cbb_ob.setEnabled(True)
            cbb_od.setEnabled(True)
            self.dockwidget.btn_show.setStyleSheet("")
            # self.dockwidget.btn_show.setToolTip(self.tr("Display results"))
            self.results_mng.show_results(result,
                                          self.dockwidget.tbl_result,
                                          progress_bar=self.bar)
            self.quicksearch.write_params('_current', search_kind="Current")
            self.store = True
        # Re enable all user input fields now the search function is
        # finished.
        self.switch_widgets_on_and_off()

        if self.results_count == 0:
            self.dockwidget.btn_show.setEnabled(False)
        else:
            self.dockwidget.btn_show.setEnabled(True)
        # hard reset
        self.hardReset = False
        self.showResult = False
    
    self.switch_widgets_on_and_off(1)

    def update_cbb_keywords(self, tags_keywords:dict ={}, selected_keywords:list =[]):
        """Keywords combobox is specific because items are checkable.
        See: https://github.com/isogeo/isogeo-plugin-qgis/issues/159

        :param dict tags_keywords: keywords found in search tags
        :param list selected_keywords: keywords (codes) already checked
        """
        logger.debug("Updating keywords combobox with {} items."
                     .format(len(tags_keywords)))

        selected_keywords_lbls = self.dockwidget.cbb_chck_kw.checkedItems()  # for tooltip
        model = QStandardItemModel(5, 1)  # 5 rows, 1 col
        logger.debug(type(selected_keywords))
        logger.debug(selected_keywords)
        # parse keywords and check selected
        i = 0   # row index
        for tag_label, tag_code in sorted(tags_keywords.items()):
            i += 1
            item = QStandardItem(tag_label)
            item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            item.setData(tag_code, 32)
            if not selected_keywords or self.hardReset or tag_code not in selected_keywords:
                item.setData(Qt.Unchecked, Qt.CheckStateRole)
                model.setItem(i, 0, item)
            elif tag_code in selected_keywords:
                item.setData(Qt.Checked, Qt.CheckStateRole)
                model.insertRow(0, item)
            else:
                pass
        # first item = label for the combobox.
        first_item = QStandardItem("---- {} ----"
                                   .format(self.tr('Keywords')))
        first_item.setIcon(ico_keyw)
        first_item.setSelectable(False)
        model.insertRow(0, first_item)

        # connect keyword selected -> launch search
        model.itemChanged.connect(self.search)

        # add the built model to the combobox
        self.dockwidget.cbb_chck_kw.setModel(model)

        # add tooltip with selected keywords. see: #107#issuecomment-341742142
        if selected_keywords:
            tooltip = "{}\n - {}".format(self.tr("Selected keywords:"), "\n - ".join(selected_keywords_lbls))
        else:
            tooltip =  self.tr("No keyword selected")
        self.dockwidget.cbb_chck_kw.setToolTip(tooltip)

    def save_params(self):
        """Save the widgets state/index.

        This save the current state/index of each user input so we can put them
        back to their previous state/index after they have been updated
        (cleared and filled again).
        """
        # Getting the text in the search line
        text = self.dockwidget.txt_input.text()
        # get the data of the item which index is (comboboxes current index)
        owner_param = self.dockwidget.cbb_owner.itemData(
            self.dockwidget.cbb_owner.currentIndex())
        inspire_param = self.dockwidget.cbb_inspire.itemData(
            self.dockwidget.cbb_inspire.currentIndex())
        format_param = self.dockwidget.cbb_format.itemData(
            self.dockwidget.cbb_format.currentIndex())
        srs_param = self.dockwidget.cbb_srs.itemData(
            self.dockwidget.cbb_srs.currentIndex())
        contact_param = self.dockwidget.cbb_contact.itemData(
            self.dockwidget.cbb_contact.currentIndex())
        license_param = self.dockwidget.cbb_license.itemData(
            self.dockwidget.cbb_license.currentIndex())
        type_param = self.dockwidget.cbb_type.itemData(
            self.dockwidget.cbb_type.currentIndex())
        if self.dockwidget.cbb_geofilter.currentIndex() < 2:
            geofilter_param = self.dockwidget.cbb_geofilter.itemData(
                self.dockwidget.cbb_geofilter.currentIndex())
        else:
            geofilter_param = self.dockwidget.cbb_geofilter.currentText()
        favorite_param = self.dockwidget.cbb_quicksearch_use.itemData(
            self.dockwidget.cbb_quicksearch_use.currentIndex())
            
        operation_param = self.dockwidget.cbb_geo_op.itemData(
            self.dockwidget.cbb_geo_op.currentIndex())
        ob_param = self.dockwidget.cbb_ob.itemData(
            self.dockwidget.cbb_ob.currentIndex())
        od_param = self.dockwidget.cbb_od.itemData(
            self.dockwidget.cbb_od.currentIndex())
        # Saving the keywords that are selected : if a keyword state is
        # selected, he is added to the list
        key_params = []
        for txt in self.dockwidget.cbb_chck_kw.checkedItems():
            item_index = self.dockwidget.cbb_chck_kw.findText(txt, Qt.MatchFixedString)
            key_params.append(self.dockwidget.cbb_chck_kw.itemData(item_index, 32))

        params = {"owner": owner_param,
                  "inspire": inspire_param,
                  "format": format_param,
                  "srs": srs_param,
                  "favorite": favorite_param,
                  "keys": key_params,
                  "geofilter": geofilter_param,
                  "license": license_param,
                  "contact": contact_param,
                  "text": text,
                  "datatype": type_param,
                  "operation": operation_param,
                  "ob": ob_param,
                  "od": od_param,
                  }
        # check geographic filter
        if params.get('geofilter') == "mapcanvas":
            e = iface.mapCanvas().extent()
            extent = [e.xMinimum(), e.yMinimum(), e.xMaximum(), e.yMaximum()]
            params['extent'] = extent
            epsg = int(plg_tools.get_map_crs().split(':')[1])
            params['epsg'] = epsg
            params['coord'] = self.get_coords('canvas')
        elif params.get('geofilter') in [lyr.name() for lyr in QgsProject.instance().mapLayers().values()]:
            params['coord'] = self.get_coords(params.get('geofilter'))
        else:
            pass
        # saving params in QSettings
        qsettings.setValue("isogeo/settings/georelation", operation_param)
        logger.debug(params)
        return params

    def switch_widgets_on_and_off(self, mode=1):
        """Disable all the UI widgets when a request is being sent.

        Deactivate the widgets while a funcion is running so the user doesn't
        clic everywhere ending up in multiple requests being sent at the same
        time, making the plugin crash.
        """
        if mode:
            self.dockwidget.txt_input.setReadOnly(False)
            self.dockwidget.tab_search.setEnabled(True)
        else:
            self.dockwidget.txt_input.setReadOnly(True)
            self.dockwidget.tab_search.setEnabled(False)

    def clear_widgets(self):
        for cbb in self.dockwidget.tab_search.findChildren(QComboBox):
            cbb.clear()
        self.dockwidget.cbb_geo_op.clear()
        self.dockwidget.txt_input.clear()

    def reinitialize_search(self):
        """Clear all widget, putting them all back to their default value.

        Clear all widget and send a request to the API (which ends up updating
        the fields : send_request() calls handle_reply(), which calls
        update_fields())
        """
        logger.debug("Reset search function called.")
        self.hardReset = True
        # clear widgets
        self.clear_widgets()
        # launch search
        self.search()

# #############################################################################
# ##### Stand alone program ########
# ##################################
if __name__ == '__main__':
    """Standalone execution."""
