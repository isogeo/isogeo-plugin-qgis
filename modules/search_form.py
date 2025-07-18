# -*- coding: utf-8 -*-

# Standard library
import logging
from collections import OrderedDict

# PyQGIS
from qgis.core import (
    QgsProject,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform
)
from qgis.utils import iface

# PyQT
from qgis.PyQt.QtCore import pyqtSignal, Qt, QEvent
from qgis.PyQt.QtWidgets import QComboBox
from qgis.PyQt.QtGui import QIcon, QStandardItem

# UI classe
from ..ui.isogeo_dockwidget import IsogeoDockWidget  # main widget

# submodule
from .tools import IsogeoPlgTools
from .quick_search import QuickSearchManager
from .portal_base_url import PortalURLManager
from .results import ResultsManager

# ############################################################################
# ########## Globals ###############
# ##################################

logger = logging.getLogger("IsogeoQgisPlugin")
msgBar = iface.messageBar()

plg_tools = IsogeoPlgTools()

# icons
ico_od_asc = QIcon(":/plugins/Isogeo/resources/results/sort-alpha-asc.svg")
ico_od_desc = QIcon(":/plugins/Isogeo/resources/results/sort-alpha-desc.svg")
ico_ob_relev = QIcon(":/plugins/Isogeo/resources/results/star.svg")
ico_ob_alpha = QIcon(":/plugins/Isogeo/resources/results/sort-alpha.svg")
ico_ob_mcrea = QIcon(":/plugins/Isogeo/resources/results/sort-metadatacreated.svg")
ico_ob_mupda = QIcon(":/plugins/Isogeo/resources/results/sort-metadatamodified.svg")
ico_ob_dcrea = QIcon(":/plugins/Isogeo/resources/results/sort-datacreated.svg")
ico_ob_dupda = QIcon(":/plugins/Isogeo/resources/results/sort-datamodified.svg")
ico_none = QIcon(":/plugins/Isogeo/resources/none.svg")
ico_line = QIcon(":/images/themes/default/mIconLineLayer.svg")
ico_log = QIcon(":/images/themes/default/mActionFolder.svg")
ico_poin = QIcon(":/images/themes/default/mIconPointLayer.svg")
ico_poly = QIcon(":/images/themes/default/mIconPolygonLayer.svg")

# ############################################################################
# ########## Classes ###############
# ##################################


class SearchFormManager(IsogeoDockWidget):
    """Basic class to manage IsogeoDockwidget UI module (ui/isogeo_dockwidget.py).
    It performs different tasks :
        - update widgets (clear, fill and set appropriate status)
        - fill the results table calling ResultsManager.show_results method
        - save search parameters selected by the user, which is useful for updating
        widgets or building search request's URL.
    Most of its methods are called by Isogeo.search_slot method which launched after
    the results of a search request has been parsed and validated.
    """

    # Simple signal to connect keywords special combobox with Isogeo.search method
    kw_sig = pyqtSignal()

    def __init__(self, trad: object = None, settings_manager: object = None):
        # inheritance
        super().__init__()

        self.tr = trad
        self.settings_mng = settings_manager

        # disable wheel event on combobox
        for cbb in self.findChildren(QComboBox):
            cbb.installEventFilter(self)

        # match between widgets and metadata fields
        self.match_widget_field = {
            self.cbb_type: "datatype",
            self.cbb_format: "formats",
            self.cbb_owner: "owners",
            self.cbb_inspire: "inspire",
            self.cbb_grpTh: "groupTheme",
            self.cbb_srs: "srs",
            self.cbb_contact: "contacts",
            self.cbb_license: "licenses",
        }

        # Static dictionaries for filling static widgets
        self.dict_operation = OrderedDict(
            [
                (self.tr("intersects", context=__class__.__name__), "intersects"),
                (self.tr("within", context=__class__.__name__), "within"),
                (self.tr("contains", context=__class__.__name__), "contains"),
            ]
        )

        # groupTheme, geofilter, type, format, owner, inspire, srs, contact and license
        self.cbbs_search_advanced = [
            cbbox for cbbox in self.grp_filters.findChildren(QComboBox) if cbbox != self.cbb_chck_kw
        ]
        # order by, order direction
        self.cbbs_order = {
            self.cbb_ob: (
                (self.tr("Relevance", context=__class__.__name__), ico_ob_relev, "relevance"),
                (self.tr("Alphabetical order", context=__class__.__name__), ico_ob_alpha, "title"),
                (self.tr("Data modified", context=__class__.__name__), ico_ob_dupda, "modified", self.tr("Data modification date", context=__class__.__name__)),
                (self.tr("Data created", context=__class__.__name__), ico_ob_dcrea, "created", self.tr("Data creation date", context=__class__.__name__)),
                (self.tr("Metadata modified", context=__class__.__name__), ico_ob_mupda, "_modified", self.tr("Metadata modification date", context=__class__.__name__)),
                (self.tr("Metadata created", context=__class__.__name__), ico_ob_mcrea, "_created", self.tr("Metadata creation date", context=__class__.__name__)),
            ),
            self.cbb_od: (
                (self.tr("Descending", context=__class__.__name__), ico_od_desc, "desc"),
                (self.tr("Ascending", context=__class__.__name__), ico_od_asc, "asc"),
            )
        }

        # Setting quick search manager
        self.qs_mng = QuickSearchManager(
            search_form_manager=self,
            settings_manager=self.settings_mng
        )
        self.qs_mng.settings_mng = self.settings_mng
        # Connecting quick search widgets to QuickSearchManager's methods
        self.btn_quicksearch_save.pressed.connect(self.qs_mng.dlg_new.show)
        self.btn_rename_sr.pressed.connect(self.qs_mng.dlg_rename.show)
        self.btn_delete_sr.pressed.connect(self.qs_mng.remove)
        self.btn_default_save.pressed.connect(self.qs_mng.write_params)
        self.btn_default_reset.pressed.connect(self.qs_mng.reset_default_search)

        # Setting portal base URL manager
        self.portalURL_mng = PortalURLManager(settings_manager=self.settings_mng)
        # Connecting portal base URL configuration button to PortalURLManager's methods
        self.btn_open_portalURL_config_dialog.pressed.connect(self.portalURL_mng.open_dialog)

        # Setting result manager
        self.results_mng = ResultsManager(
            search_form_manager=self,
            settings_manager=self.settings_mng
        )

    def eventFilter(self, obj, event):  # https://github.com/isogeo/isogeo-plugin-qgis/issues/455
        if event.type() == QEvent.Wheel:
            return True
        else:
            return False

    def update_cbb_keywords(self, tags_keywords: dict = {}, selected_keywords: list = [], selected_keywords_labels: list = []):
        """Keywords combobox is specific because items are checkable.
        See: https://github.com/isogeo/isogeo-plugin-qgis/issues/159

        :param dict tags_keywords: keywords found in search tags.
        :param list selected_keywords: keywords (codes) already checked.
        :param list selected_keywords_labels: keywords (label) already checked, argument added for
            no results searches (https://github.com/isogeo/isogeo-plugin-qgis/issues/436)
        """
        selected_keywords_lbls = self.cbb_chck_kw.checkedItems()  # for tooltip
        logger.debug(
            "Updating keywords combobox with {} items, including {} selected.".format(
                len(tags_keywords), len(selected_keywords_lbls)
            )
        )
        # shortcut
        model = self.cbb_chck_kw.model()

        # disconnect the widget before updating
        try:
            model.itemChanged.disconnect()
        except TypeError:
            pass

        # clear the the combobox content
        model.clear()

        # parse keywords and check selected
        cbb_chck_kw_width = self.cbb_chck_kw.width() - 10
        cbb_chck_kw_fm = self.cbb_chck_kw.fontMetrics()

        # Only for no results searches, when comboboxe is filled from params and not tags
        # https://github.com/isogeo/isogeo-plugin-qgis/issues/436
        if not len(tags_keywords) and len(selected_keywords) and len(selected_keywords_labels):
            for i in range(len(selected_keywords)):
                tag_label = selected_keywords_labels[i]
                tag_code = selected_keywords[i]
                item = QStandardItem()
                # format combobox item label fit the widget width
                tag_label_width = cbb_chck_kw_fm.size(1, tag_label).width()
                if tag_label_width > cbb_chck_kw_width:
                    item.setText(cbb_chck_kw_fm.elidedText(tag_label, 1, cbb_chck_kw_width))
                    item.setToolTip(tag_code)
                else:
                    item.setText(tag_label)

                item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
                item.setData(tag_code, 32)
                item.setData(Qt.Checked, Qt.CheckStateRole)
                model.insertRow(0, item)
        # For all other searches
        else:
            row_i = 0  # row index
            for tag_label, tag_code in sorted(tags_keywords.items(), key=lambda item: item[1]):
                item = QStandardItem()
                # format combobox item label fit the widget width
                tag_label_width = cbb_chck_kw_fm.size(1, tag_label).width()
                if tag_label_width > cbb_chck_kw_width:
                    item.setText(cbb_chck_kw_fm.elidedText(tag_label, 1, cbb_chck_kw_width))
                    item.setToolTip(tag_label)
                else:
                    item.setText(tag_label)

                item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
                item.setData(tag_code, 32)
                if len(selected_keywords) == 0 or tag_code not in selected_keywords:
                    item.setData(Qt.Unchecked, Qt.CheckStateRole)
                    model.setItem(row_i, 0, item)
                elif tag_code in selected_keywords:
                    item.setData(Qt.Checked, Qt.CheckStateRole)
                    model.insertRow(0, item)
                else:
                    pass
                row_i += 1

        # connect keyword selected -> launch search
        model.itemChanged.connect(self.kw_sig.emit)

        # add tooltip with selected keywords. see: #107#issuecomment-341742142
        if len(selected_keywords):
            tooltip = "{}\n - {}".format(
                self.tr("Selected keywords:", context=__class__.__name__),
                "\n - ".join(selected_keywords_lbls),
            )
        else:
            tooltip = self.tr("No keyword selected", context=__class__.__name__)
        self.cbb_chck_kw.setToolTip(tooltip)

    def pop_as_cbbs(self, tags: dict):
        """Called by Isogeo.search_slot method. Clears Advanced search comboboxes
        and fills them from 'tags' parameter.

        :param dict tags: 'tags' parameter of Isogeo.search_slot method.
        """
        logger.debug("Filling Advanced search comboboxes from tags")

        # Clear widgets then add the "nothing selected" option
        for cbb in self.cbbs_search_advanced:
            cbb.clear()
            cbb.addItem(" - ")
        # Filling advanced search comboboxes (except geo filter)
        for cbb in self.match_widget_field.keys():
            field_tags = tags.get(self.match_widget_field.get(cbb))
            for tag in field_tags:
                cbb.addItem(tag, field_tags.get(tag))
        # Filling geo filter combobox
        self.cbb_geofilter.addItem(self.tr(" Map canvas", context=__class__.__name__), "mapcanvas")
        layers = QgsProject.instance().mapLayers().values()
        for layer in layers:
            if layer.type() == 0 and layer.name() != "Metadata envelope":
                if layer.geometryType() == 2:
                    self.cbb_geofilter.addItem(ico_poly, layer.name())
                elif layer.geometryType() == 1:
                    self.cbb_geofilter.addItem(ico_line, layer.name())
                elif layer.geometryType() == 0:
                    self.cbb_geofilter.addItem(ico_poin, layer.name())
        # Format combobox items text to fit with widget width
        for cbb in self.cbbs_search_advanced:
            cbb_width = cbb.width() - 20
            cbb_fm = cbb.fontMetrics()

            for i in range(cbb.count()):
                item_label = cbb.itemText(i)
                item_label_width = cbb_fm.size(1, item_label).width()
                if item_label_width > cbb_width:
                    cbb.setItemText(i, cbb_fm.elidedText(item_label, 1, cbb_width))
                    cbb.setItemData(i, item_label, Qt.ToolTipRole)
                else:
                    pass
        # Filling order by and direction cbb
        for cbb in self.cbbs_order:
            cbb.clear()
            for tup in self.cbbs_order[cbb]:
                cbb.addItem(tup[1], tup[0], tup[2])
                if len(tup) == 4:
                    cbb.setItemData(cbb.count() - 1, tup[3], Qt.ToolTipRole)
                else:
                    pass

        return

    def pop_qs_cbbs(self, items_list: list = None):
        """Called by Isogeo.search_slot method. Clears quick searches comboboxes
        (also the one in settings tab) and fills them from 'items_list' parameter.

        :param list items_list: a list of quick search's names
        from _user/quicksearches.json file.
        """
        logger.debug("Filling quick searches comboboxes")
        # building the list of widgets' items'content
        if items_list is None:
            qs_list = self.qs_mng.get_quicksearches_names()
        else:
            qs_list = items_list
        qs_list.pop(qs_list.index("_default"))
        if "_current" in qs_list:
            qs_list.pop(qs_list.index("_current"))
        # clear widgets
        self.cbb_quicksearch_use.clear()
        self.cbb_quicksearch_edit.clear()
        # filling widgets from the saved searches list built above
        self.cbb_quicksearch_use.addItem(self.tr("Quicksearches", context=__class__.__name__))
        for qs in qs_list:
            self.cbb_quicksearch_use.addItem(qs, qs)
            self.cbb_quicksearch_edit.addItem(qs, qs)
        return

    def set_ccb_index(self, params: dict, quicksearch: str = ""):
        """Called by Isogeo.search_slot method. It sets the status of widgets
        according to the user's selection or the quick search performed.

        :param dict params: parameters saved in _user/quicksearches.json in case
        of quicksearch. Otherwise  : parameters selected by the user retrieved at
        the beginning of the Isogeo.search_slot method.
        :param str quicksearch: empty string if no quicksearch performed.
        Otherwise:the name of the quicksearch performed.
        """
        logger.debug("Settings widgets statut according to these parameters : \n{}".format(params))
        # for Advanced search Combobox except geo_filter
        for cbb in self.match_widget_field.keys():
            field_name = self.match_widget_field.get(cbb)
            dest_index = cbb.findData(params.get(field_name))
            # For no result searches, we need to create items from paramas before setting index
            # because there is no tags so comboboxes are empty 
            # https://github.com/isogeo/isogeo-plugin-qgis/issues/436
            if dest_index == -1 and params.get("labels", False):
                item_text = params.get("labels").get(field_name)
                cbb.addItem(item_text, params.get(field_name))
                dest_index = cbb.findData(params.get(field_name))
            else:
                pass
            cbb.setCurrentIndex(dest_index)

        # for geo filter
        if params.get("geofilter") == "mapcanvas":
            geof_index = self.cbb_geofilter.findData("mapcanvas")
        elif params.get("geofilter") is None:
            geof_index = self.cbb_geofilter.findText(" - ")
        else:
            geof_index = self.cbb_geofilter.findText(params.get("geofilter"))
        self.cbb_geofilter.setCurrentIndex(geof_index)

        # for use quick search
        if quicksearch == "" or quicksearch == "_default":
            qs_index = 0
        else:
            qs_index = self.cbb_quicksearch_use.findData(quicksearch)
        self.cbb_quicksearch_use.setCurrentIndex(qs_index)

        # for text label
        self.txt_input.setText(params.get("text"))

        # for geo_op
        geoop_index = self.cbb_geo_op.findData(params.get("operation"))
        self.cbb_geo_op.setCurrentIndex(geoop_index)

        # for sorting order and direction
        self.cbb_ob.setCurrentIndex(self.cbb_ob.findData(params.get("ob")))
        self.cbb_ob.setToolTip(
            self.tr("Order by: ", context=__class__.__name__) + self.cbb_ob.currentText()
        )
        # self.cbb_ob.setStyleSheet(r"QToolTip {color: black}")
        self.cbb_od.setCurrentIndex(self.cbb_od.findData(params.get("od")))
        self.cbb_od.setToolTip(
            self.tr("Order direction: ", context=__class__.__name__) + self.cbb_od.currentText()
        )

        return

    def fill_tbl_result(self, results: list, page_index: int, results_count: int):
        """Called by Isogeo.search_slot method. It sets some widgets' statuts
        in order to display results.

        :param int page_index: results table's page index.
        :param int results_count: number of metadata to be displayed in the
        table.
        :param list results: a list containing the content of the 'results' key
        of API's reply to a search request
        """
        nb_page = plg_tools.results_pages_counter(total=results_count)
        if nb_page == 1:
            self.btn_next.setEnabled(False)
            self.btn_previous.setEnabled(False)
        elif page_index < 2:
            self.btn_previous.setEnabled(False)
            self.btn_next.setEnabled(True)
        elif page_index == nb_page:
            self.btn_next.setEnabled(False)
            self.btn_previous.setEnabled(True)
        else:
            self.btn_next.setEnabled(True)
            self.btn_previous.setEnabled(True)

        self.cbb_ob.setEnabled(True)
        self.cbb_od.setEnabled(True)
        self.btn_show.setToolTip(self.tr("Display results", context=__class__.__name__))

        self.results_mng.show_results(results)
        self.qs_mng.write_params("_current", search_kind="Current")

    def switch_widgets_on_and_off(self, mode=1):
        """Disable all the UI widgets when a request is being sent.

        Deactivate the widgets while a function is running so the user doesn't
        clic everywhere ending up in multiple requests being sent at the same
        time, making the plugin crash.

        :param int mode: 1 to enable widgets, 0 to disable
        """
        if mode:
            self.txt_input.setReadOnly(False)
            self.tab_search.setEnabled(True)
        else:
            self.txt_input.setReadOnly(True)
            self.tab_search.setEnabled(False)

    def init_steps(self):
        """Called by Isogeo.search_slot method in case of reset or "_default"
        quicksearch. It initialise the widgets that don't need to be updated
        """
        # Geographical operator cbb
        self.cbb_geo_op.clear()
        for key in self.dict_operation.keys():
            self.cbb_geo_op.addItem(key, self.dict_operation.get(key))
        # Advanced search cbb
        for cbb in self.cbbs_search_advanced:
            cbb.setStyleSheet("combobox-popup: 0; font-size: 12px")
        # Order by and direction cbb
        for cbb in self.cbbs_order:
            cbb.setStyleSheet("QComboBox {combobox-popup: 0; color: transparent; font-size: 12px} QListView {color: black; icon-size: 20px} QToolTip {color: black}")
            # cbb.setStyleSheet("QComboBox {combobox-popup: 0; color: transparent; font-size: 12px} QListView {color: black; icon-size: 20px; selection-background-color: lightgray; selection-color: black} QToolTip {color: black}")
            cbb.view().setSpacing(2)

    def reinit_widgets(self):
        """Called by Isogeo.reinitialize_search method to clear search widgets."""
        # clear widgets
        for cbb in self.tab_search.findChildren(QComboBox):
            cbb.clear()
        self.cbb_geo_op.clear()
        self.txt_input.clear()
        return

    def save_params(self):
        """Save the widgets state/index.

        This save the current state/index of each user input in a dict so we can
        put them back to their previous state/index after they have been updated
        (cleared and filled again). The dict is also used to build search requests
        URL.

        :returns: a dictionary whose keys correspond to the names of the different
        user input and values correspond to the user's sélection in  each of these
        inputs (None if nothing selected).

        :rtype: dict
        """
        params = {}
        # in case when the search will have no results, we need to store infos to fill comboboxes
        # because tags will be empty  (https://github.com/isogeo/isogeo-plugin-qgis/issues/436)
        params["labels"] = {}
        # get the data of the item which index is (comboboxes current index)
        for cbb in self.match_widget_field:
            field = self.match_widget_field.get(cbb)
            item = cbb.itemData(cbb.currentIndex())
            params[field] = item
            params["labels"][field] = cbb.currentText()

        if self.cbb_geofilter.currentText() == " - ":
            params["geofilter"] = None
        elif self.cbb_geofilter.itemData(self.cbb_geofilter.currentIndex()) == "mapcanvas":
            params["geofilter"] = "mapcanvas"
        else:
            params["geofilter"] = self.cbb_geofilter.currentText()

        params["favorite"] = self.cbb_quicksearch_use.itemData(
            self.cbb_quicksearch_use.currentIndex()
        )

        # Getting the text in the search line
        params["text"] = self.txt_input.text()

        params["operation"] = self.cbb_geo_op.itemData(self.cbb_geo_op.currentIndex())
        params["ob"] = self.cbb_ob.itemData(self.cbb_ob.currentIndex())
        params["od"] = self.cbb_od.itemData(self.cbb_od.currentIndex())
        # Saving the keywords that are selected : if a keyword state is
        # selected, he is added to the list
        key_params = []
        labels_key_params = []
        for txt in self.cbb_chck_kw.checkedItems():
            item_index = self.cbb_chck_kw.findText(txt, Qt.MatchFixedString)
            key_params.append(self.cbb_chck_kw.itemData(item_index, 32))
            labels_key_params.append(txt)
        params["keys"] = key_params
        params["labels"]["keys"] = labels_key_params
        # check geographic filter
        layer_names = [lyr.name() for lyr in QgsProject.instance().mapLayers().values()]
        if params.get("geofilter") == "mapcanvas":
            e = iface.mapCanvas().extent()
            extent = [e.xMinimum(), e.yMinimum(), e.xMaximum(), e.yMaximum()]
            params["extent"] = extent
            params["epsg"] = plg_tools.get_map_crs()
            params["coord"] = self.get_coords("canvas")
        elif params.get("geofilter") in layer_names:
            params["coord"] = self.get_coords(params.get("geofilter"))
        else:
            pass
        # saving params in QSettings
        self.settings_mng.set_value("isogeo/settings/georelation", params.get("operation"))
        return params

    def get_coords(self, filter: str):
        """Get the extent's coordinates of a layer or canvas in the right format
        and SRS (WGS84).

        :param str filter: the name of the element which we want to get extent's
        coordinates.

        :returns: the x and y coordinates of the canvas' Southwestern and
        Northeastern vertexes.

        :rtype: str
        """
        qgs_prj = QgsProject.instance()
        if filter == "canvas":
            extent = iface.mapCanvas().extent()
            currentCrs = plg_tools.get_map_crs()
        else:
            layer = qgs_prj.mapLayersByName(filter)[0]
            extent = layer.extent()
            currentCrs = layer.crs().authid()

        # If coordinates already are WGS84 we can use them
        if currentCrs == "EPSG:4326":
            coord = "{},{},{},{}".format(extent.xMinimum(), extent.yMinimum(), extent.xMaximum(), extent.yMaximum())
            return coord
        # Else, we have to convert them to WGS84
        else:
            wgs84_crs = QgsCoordinateReferenceSystem("EPSG:4326")
            crs_converter = QgsCoordinateTransform(QgsCoordinateReferenceSystem(currentCrs), wgs84_crs, qgs_prj)

            wgs84_bounds = wgs84_crs.bounds()
            extent_wgs84 = crs_converter.transformBoundingBox(extent)

            # because of https://github.com/isogeo/isogeo-plugin-qgis/issues/437
            if wgs84_bounds.contains(extent_wgs84):
                pass
            else:
                if extent_wgs84.xMinimum() < wgs84_bounds.xMinimum():
                    extent_wgs84.setXMinimum(wgs84_bounds.xMinimum())
                else:
                    pass

                if extent_wgs84.yMinimum() < wgs84_bounds.yMinimum():
                    extent_wgs84.setYMinimum(wgs84_bounds.yMinimum())
                else:
                    pass

                if extent_wgs84.xMaximum() > wgs84_bounds.xMaximum():
                    extent_wgs84.setXMaximum(wgs84_bounds.xMaximum())
                else:
                    pass

                if extent_wgs84.yMaximum() > wgs84_bounds.yMaximum():
                    extent_wgs84.setYMaximum(wgs84_bounds.yMaximum())
                else:
                    pass

            coord = "{},{},{},{}".format(
                extent_wgs84.xMinimum(), extent_wgs84.yMinimum(), extent_wgs84.xMaximum(), extent_wgs84.yMaximum()
            )

            return coord


# #############################################################################
# ##### Stand alone program ########
# ##################################
if __name__ == "__main__":
    """Standalone execution."""
