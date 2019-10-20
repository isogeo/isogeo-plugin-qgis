# -*- coding: utf-8 -*-

# Standard library
import logging
from collections import OrderedDict

# PyQGIS
from qgis.core import (
    QgsProject,
    QgsCoordinateReferenceSystem,
    QgsPointXY,
    QgsCoordinateTransform,
)
from qgis.utils import iface

# PyQT
from qgis.PyQt.QtCore import pyqtSignal, QSettings, Qt
from qgis.PyQt.QtWidgets import QComboBox
from qgis.PyQt.QtGui import QIcon, QStandardItemModel, QStandardItem

# UI classe
from ..ui.isogeo_dockwidget import IsogeoDockWidget  # main widget

# submodule
from .tools import IsogeoPlgTools
from .quick_search import QuickSearchManager
from .results import ResultsManager

# ############################################################################
# ########## Globals ###############
# ##################################

logger = logging.getLogger("IsogeoQgisPlugin")
msgBar = iface.messageBar()

plg_tools = IsogeoPlgTools()

qsettings = QSettings()
# icons
ico_od_asc = QIcon(":/plugins/Isogeo/resources/results/sort-alpha-asc.svg")
ico_od_desc = QIcon(":/plugins/Isogeo/resources/results/sort-alpha-desc.svg")
ico_ob_relev = QIcon(":/plugins/Isogeo/resources/results/star.svg")
ico_ob_alpha = QIcon(":/plugins/Isogeo/resources/metadata/language.svg")
ico_ob_dcrea = QIcon(":/plugins/Isogeo/resources/datacreated.svg")
ico_ob_dupda = QIcon(":/plugins/Isogeo/resources/datamodified.svg")
ico_ob_mcrea = QIcon(":/plugins/Isogeo/resources/calendar-plus-o.svg")
ico_ob_mupda = QIcon(":/plugins/Isogeo/resources/calendar_blue.svg")
ico_bolt = QIcon(":/plugins/Isogeo/resources/search/bolt.svg")
ico_keyw = QIcon(":/plugins/Isogeo/resources/tag.svg")
ico_none = QIcon(":/plugins/Isogeo/resources/none.svg")
ico_line = QIcon(":/images/themes/default/mIconLineLayer.svg")
ico_log = QIcon(":/images/themes/default/mActionFolder.svg")
ico_poin = QIcon(":/images/themes/default/mIconPointLayer.svg")
ico_poly = QIcon(":/images/themes/default/mIconPolygonLayer.svg")

# ############################################################################
# ########## Classes ###############
# ##################################


class SearchFormManager(IsogeoDockWidget):
    """ Basic class to manage IsogeoDockwidget UI module (ui/isogeo_dockwidget.py).
    It performs different tasks :
        - update widgets (clear, fill and set appropriate status)
        - fill the results table calling ResultsManager.show_results method
        - save search parameters selected by the user, wich is useful for updating
        widgets or building search request's URL.
    Most of its methods are called by Isogeo.search_slot method which launched after
    the results of a search request has been parsed and validated.
    """

    # Simple signal to connect keywords special combobox with Isogeo.search method
    kw_sig = pyqtSignal()

    def __init__(self, trad):
        # inheritance
        super().__init__()

        self.tr = trad
        # geofilter, type, format, owner, inspire, srs, contact and license
        self.cbbs_search_advanced = self.grp_filters.findChildren(QComboBox)
        # match between widgets and metadata fields
        self.match_widget_field = {
            self.cbb_type: "types",
            self.cbb_format: "formats",
            self.cbb_owner: "owners",
            self.cbb_inspire: "inspire",
            self.cbb_srs: "srs",
            self.cbb_contact: "contacts",
            self.cbb_license: "licenses",
        }

        # Static dictionnaries for filling static widgets
        self.dict_operation = OrderedDict(
            [
                (self.tr("Intersects", context=__class__.__name__), "intersects"),
                (self.tr("within", context=__class__.__name__), "within"),
                (self.tr("contains", context=__class__.__name__), "contains"),
            ]
        )
        self.dict_ob = OrderedDict(
            [
                (
                    self.tr("Relevance", context=__class__.__name__),
                    (ico_ob_relev, "relevance"),
                ),
                (
                    self.tr("Alphabetical order", context=__class__.__name__),
                    (ico_ob_alpha, "title"),
                ),
                (
                    self.tr("Data modified", context=__class__.__name__),
                    (ico_ob_dupda, "modified"),
                ),
                (
                    self.tr("Data created", context=__class__.__name__),
                    (ico_ob_dcrea, "created"),
                ),
                (
                    self.tr("Metadata modified", context=__class__.__name__),
                    (ico_ob_mcrea, "_modified"),
                ),
                (
                    self.tr("Metadata created", context=__class__.__name__),
                    (ico_ob_mupda, "_created"),
                ),
            ]
        )
        self.dict_od = OrderedDict(
            [
                (
                    self.tr("Descending", context=__class__.__name__),
                    (ico_od_desc, "desc"),
                ),
                (self.tr("Ascending", context=__class__.__name__), (ico_od_asc, "asc")),
            ]
        )

        # Setting quick search manager
        self.qs_mng = QuickSearchManager(self)
        # Connecting quick search widgets to QuickSearchManager's methods
        self.btn_quicksearch_save.pressed.connect(self.qs_mng.dlg_new.show)
        self.btn_rename_sr.pressed.connect(self.qs_mng.dlg_rename.show)
        self.btn_delete_sr.pressed.connect(self.qs_mng.remove)
        self.btn_default_save.pressed.connect(self.qs_mng.write_params)

        # Setting result manager
        self.results_mng = ResultsManager(self)

    def update_cbb_keywords(
        self, tags_keywords: dict = {}, selected_keywords: list = []
    ):
        """Keywords combobox is specific because items are checkable.
        See: https://github.com/isogeo/isogeo-plugin-qgis/issues/159

        :param dict tags_keywords: keywords found in search tags.
        :param list selected_keywords: keywords (codes) already checked.
        """
        selected_keywords_lbls = self.cbb_chck_kw.checkedItems()  # for tooltip
        logger.debug(
            "Updating keywords combobox with {} items, including {} selected.".format(
                len(tags_keywords), len(selected_keywords_lbls)
            )
        )

        model = QStandardItemModel(5, 1)  # 5 rows, 1 col
        # parse keywords and check selected
        i = 0  # row index
        for tag_label, tag_code in sorted(tags_keywords.items()):
            i += 1
            item = QStandardItem(tag_label)
            item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            item.setData(tag_code, 32)
            if len(selected_keywords) == 0 or tag_code not in selected_keywords:
                item.setData(Qt.Unchecked, Qt.CheckStateRole)
                model.setItem(i, 0, item)
            elif tag_code in selected_keywords:
                item.setData(Qt.Checked, Qt.CheckStateRole)
                model.insertRow(0, item)
            else:
                pass
        # first item = label for the combobox.
        first_item = QStandardItem(
            "---- {} ----".format(self.tr("Keywords", context=__class__.__name__))
        )
        first_item.setIcon(ico_keyw)
        first_item.setSelectable(False)
        model.insertRow(0, first_item)

        # connect keyword selected -> launch search
        model.itemChanged.connect(self.kw_sig.emit)

        # add the built model to the combobox
        self.cbb_chck_kw.setModel(model)

        # add tooltip with selected keywords. see: #107#issuecomment-341742142
        if selected_keywords:
            tooltip = "{}\n - {}".format(
                self.tr("Selected keywords:", context=__class__.__name__),
                "\n - ".join(selected_keywords_lbls),
            )
        else:
            tooltip = self.tr("No keyword selected", context=__class__.__name__)
        self.cbb_chck_kw.setToolTip(tooltip)

    def pop_as_cbbs(self, tags: dict):
        """ Called by Isogeo.search_slot method. Clears Advanced search comboboxes
        and fills them from 'tags' parameter.

        :param dict tags: 'tags' parameter of Isogeo.search_slot method.
        """
        logger.debug("Filling Advanced search comboboxes from tags")
        # clear widgets
        for cbb in self.cbbs_search_advanced:
            cbb.clear()
        # Initiating the "nothing selected"
        for cbb in self.cbbs_search_advanced:
            cbb.addItem(" - ")
        # Filling advanced search comboboxes (except geo filter)
        for cbb in self.match_widget_field.keys():
            field_tags = tags.get(self.match_widget_field.get(cbb))
            for tag in field_tags:
                cbb.addItem(tag, field_tags.get(tag))
        # Filling geo filter combobox
        self.cbb_geofilter.addItem(
            self.tr("Map canvas", context=__class__.__name__), "mapcanvas"
        )
        layers = QgsProject.instance().mapLayers().values()
        for layer in layers:
            if layer.type() == 0:
                if layer.geometryType() == 2:
                    self.cbb_geofilter.addItem(ico_poly, layer.name())
                elif layer.geometryType() == 1:
                    self.cbb_geofilter.addItem(ico_line, layer.name())
                elif layer.geometryType() == 0:
                    self.cbb_geofilter.addItem(ico_poin, layer.name())
        return

    def pop_qs_cbbs(self, items_list: list = None):
        """ Called by Isogeo.search_slot method. Clears quick searches comboboxes
        (also the one in settings tab) and fills them from 'items_list' parameter.

        :param list items_list: a list of quick searche's names
        from _user/quicksearches.json file.
        """
        logger.debug("Filling quick searches comboboxes")
        # building the list of widgets' items'content
        if items_list is None:
            qs_list = list(self.qs_mng.load_file().keys())
        else:
            qs_list = items_list
        qs_list.pop(qs_list.index("_default"))
        if "_current" in qs_list:
            qs_list.pop(qs_list.index("_current"))
        # clear widgets
        self.cbb_quicksearch_use.clear()
        self.cbb_quicksearch_edit.clear()
        # filling widgets from the saved searches list built above
        self.cbb_quicksearch_use.addItem(
            ico_bolt, self.tr("Quicksearches", context=__class__.__name__)
        )
        for qs in qs_list:
            self.cbb_quicksearch_use.addItem(qs, qs)
            self.cbb_quicksearch_edit.addItem(qs, qs)
        return

    def set_ccb_index(self, params: dict, quicksearch: str = ""):
        """ Called by Isogeo.search_slot method. It sets the status of widgets
        according to the user's selection or the quick search performed.

        :param dict params: parameters saved in _user/quicksearches.json in case
        of quicksearch. Otherwise  : parameters selected by the user retrieved at
        the beginning of the Isogeo.search_slot method.
        :param str quicksearch: empty string if no quicksearch performed.
        Otherwise:the name of the quicksearch performed.
        """
        logger.debug(
            "Settings widgets statut according to these parameters : \n{}".format(
                params
            )
        )
        # for Advanced search Combobox except geo_filter
        for cbb in self.match_widget_field.keys():
            field_name = self.match_widget_field.get(cbb)
            dest_index = cbb.findData(params.get(field_name))
            cbb.setCurrentIndex(dest_index)
        # for geo filter, use quick search, and text label if quicksearch is True
        if quicksearch == "":
            if params.get("geofilter") == "mapcanvas":
                dest_index = self.cbb_geofilter.findData("mapcanvas")
                self.cbb_geofilter.setCurrentIndex(dest_index)
            else:
                dest_index = self.cbb_geofilter.findText(params["geofilter"])
                self.cbb_geofilter.setCurrentIndex(dest_index)
            dest_index = self.cbb_quicksearch_use.findData(params.get("favorite"))
            self.cbb_quicksearch_use.setCurrentIndex(dest_index)
        else:
            dest_index = self.cbb_geofilter.findData(params.get("geofilter"))
            self.cbb_geofilter.setCurrentIndex(dest_index)
            if quicksearch != "_default":
                saved_index = self.cbb_quicksearch_use.findData(quicksearch)
                self.cbb_quicksearch_use.setCurrentIndex(saved_index)
            else:
                pass
            self.txt_input.setText(params.get("text"))
        # for geo_op
        dest_index = self.cbb_geo_op.findData(params.get("operation"))
        self.cbb_geo_op.setCurrentIndex(dest_index)

        # for sorting order and direction
        self.cbb_ob.setCurrentIndex(self.cbb_ob.findData(params.get("ob")))
        self.cbb_od.setCurrentIndex(self.cbb_od.findData(params.get("od")))

        return

    def fill_tbl_result(self, content: dict, page_index: int, results_count: int):
        """ Called by Isogeo.search_slot method. It sets some widgets' statuts
        in order to display results.

        :param int page_index: results table's page index.
        :param int results_count: number of metadata to be displayed in the
        table.
        :param dict content: a dict containing the parsed content of API's reply
        to a search request
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

        self.results_mng.show_results(api_results=content)
        self.qs_mng.write_params("_current", search_kind="Current")

    def switch_widgets_on_and_off(self, mode=1):
        """Disable all the UI widgets when a request is being sent.

        Deactivate the widgets while a funcion is running so the user doesn't
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
        """ Called by Isogeo.search_slot method in case of reset or "_default"
        quicksearch. It initialise the widgets that don't need to be updated
        """
        # Geographical operator cbb
        self.cbb_geo_op.clear()
        for key in self.dict_operation.keys():
            self.cbb_geo_op.addItem(key, self.dict_operation.get(key))
        # Order by cbb
        self.cbb_ob.clear()
        for k, v in self.dict_ob.items():
            self.cbb_ob.addItem(v[0], k, v[1])
        # Order direction cbb
        self.cbb_od.clear()
        for k, v in self.dict_od.items():
            self.cbb_od.addItem(v[0], k, v[1])

    def reinit_widgets(self):
        """ Called by Isogeo.reinitialize_search method to clear search widgets.
        """
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
        # get the data of the item which index is (comboboxes current index)
        for cbb in self.match_widget_field:
            field = self.match_widget_field.get(cbb)
            item = cbb.itemData(cbb.currentIndex())
            params[field] = item

        if self.cbb_geofilter.currentIndex() < 2:
            params["geofilter"] = self.cbb_geofilter.itemData(
                self.cbb_geofilter.currentIndex()
            )
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
        for txt in self.cbb_chck_kw.checkedItems():
            item_index = self.cbb_chck_kw.findText(txt, Qt.MatchFixedString)
            key_params.append(self.cbb_chck_kw.itemData(item_index, 32))
        params["keys"] = key_params
        # check geographic filter
        if params.get("geofilter") == "mapcanvas":
            e = iface.mapCanvas().extent()
            extent = [e.xMinimum(), e.yMinimum(), e.xMaximum(), e.yMaximum()]
            params["extent"] = extent
            epsg = int(plg_tools.get_map_crs().split(":")[1])
            params["epsg"] = epsg
            params["coord"] = self.get_coords("canvas")
        elif params.get("geofilter") in [
            lyr.name() for lyr in QgsProject.instance().mapLayers().values()
        ]:
            params["coord"] = self.get_coords(params.get("geofilter"))
        else:
            pass
        # saving params in QSettings
        qsettings.setValue("isogeo/settings/georelation", params.get("operation"))
        return params

    def get_coords(self, filter: str):
        """Get the extent's coordinates of a layer or canvas in the right format
        and SRS (WGS84).

        :param str filter: the name of the element wich we want to get extent's
        coordinates.

        :returns: the x and y coordinates of the canvas' Southwestern and
        Northeastern vertexes.

        :rtype: str
        """
        if filter == "canvas":
            e = iface.mapCanvas().extent()
            current_epsg = plg_tools.get_map_crs()
        else:
            layer = QgsProject.instance().mapLayersByName(filter)[0]
            e = layer.extent()
            current_epsg = layer.crs().authid()
        # epsg code as integer
        current_epsg = int(current_epsg.split(":")[1])

        if current_epsg == 4326:
            coord = "{0},{1},{2},{3}".format(
                e.xMinimum(), e.yMinimum(), e.xMaximum(), e.yMaximum()
            )
            return coord
        elif type(current_epsg) is int:
            current_srs = QgsCoordinateReferenceSystem(
                current_epsg, QgsCoordinateReferenceSystem.EpsgCrsId
            )
            wgs = QgsCoordinateReferenceSystem(
                4326, QgsCoordinateReferenceSystem.EpsgCrsId
            )
            xform = QgsCoordinateTransform(current_srs, wgs, QgsProject.instance())
            minimum = xform.transform(QgsPointXY(e.xMinimum(), e.yMinimum()))
            maximum = xform.transform(QgsPointXY(e.xMaximum(), e.yMaximum()))
            coord = "{0},{1},{2},{3}".format(
                minimum[0], minimum[1], maximum[0], maximum[1]
            )
            return coord
        else:
            logger.debug("Wrong EPSG")
            return False


# #############################################################################
# ##### Stand alone program ########
# ##################################
if __name__ == "__main__":
    """Standalone execution."""
