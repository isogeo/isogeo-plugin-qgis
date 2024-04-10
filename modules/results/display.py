# -*- coding: utf-8 -*-
#! python3  # noqa: E265

# Standard library
import logging
from functools import partial
from pathlib import Path

# PyQT
from qgis.PyQt.QtCore import QObject, pyqtSignal, Qt
from qgis.PyQt.QtGui import QIcon, QPixmap
from qgis.PyQt.QtWidgets import QTableWidgetItem, QComboBox, QPushButton, QLabel

# Plugin modules
from .cache import CacheManager
from ..tools import IsogeoPlgTools
from ..layer.add_layer import LayerAdder
from ..layer.limitations_checker import LimitationsChecker
from ..layer.geo_service import GeoServiceManager
from ..layer.database import DataBaseManager

# isogeo-pysdk
from ..isogeo_pysdk import Metadata

# ############################################################################
# ########## Globals ###############
# ##################################

plg_tools = IsogeoPlgTools()
geo_srv_mng = GeoServiceManager()

logger = logging.getLogger("IsogeoQgisPlugin")

# Isogeo geometry types
polygon_list = (
    "CurvePolygon",
    "MultiPolygon",
    "MultiSurface",
    "Polygon",
    "PolyhedralSurface",
)
point_list = ("Point", "MultiPoint")
line_list = (
    "CircularString",
    "CompoundCurve",
    "Curve",
    "LineString",
    "MultiCurve",
    "MultiLineString",
)
multi_list = ("Geometry", "GeometryCollection")
known_geom_list = polygon_list + point_list + line_list + multi_list

# Isogeo formats
li_formats_vect = ("shp", "dxf", "dgn", "filegdb", "tab")
li_formats_rastr = (
    "esriasciigrid",
    "geotiff",
    "intergraphgdb",
    "jpeg",
    "png",
    "xyz",
    "ecw",
)

# Qt icons
# see https://github.com/qgis/QGIS/blob/master/images/images.qrc
pix_point = QPixmap(":/images/themes/default/mIconPointLayer.svg")
pix_polyg = QPixmap(":/images/themes/default/mIconPolygonLayer.svg")
pix_line = QPixmap(":/images/themes/default/mIconLineLayer.svg")
pix_rastr = QPixmap(":/images/themes/default/mIconRaster.svg")
pix_multi = QPixmap(":/plugins/Isogeo/resources/multi.svg").scaledToWidth(20)
pix_nogeo = QPixmap(":/plugins/Isogeo/resources/none.svg").scaledToWidth(20)
pix_serv = QPixmap(":/plugins/Isogeo/resources/results/cloud.svg").scaledToWidth(20)
pix_table = QPixmap(":/images/themes/default/mIconTableLayer.svg").scaledToWidth(15)
ico_efs = QIcon(":/images/themes/default/mIconAfs.svg")
ico_ems = QIcon(":/images/themes/default/mIconAms.svg")
ico_wfs = QIcon(":/images/themes/default/mIconWfs.svg")
ico_wms = QIcon(":/images/themes/default/mIconWms.svg")
ico_wmts = QIcon(":/images/themes/default/mIconWcs.svg")
ico_pgis = QIcon(":/images/themes/default/mIconPostgis.svg")
ico_ora = QIcon(":/images/themes/default/mIconOracle.svg")
ico_file = QIcon(":/images/themes/default/mActionFileNew.svg")

# ############################################################################
# ########## Classes ###############
# ##################################


class ResultsManager(QObject):
    """Basic class that holds utility methods for the plugin."""

    md_asked = pyqtSignal(str)

    def __init__(self, search_form_manager: object = None, settings_manager: object = None):
        # inheritance
        super().__init__()

        self.settings_mng = settings_manager
        self.form_mng = search_form_manager
        self.tbl_result = self.form_mng.tbl_result
        self.tr = self.form_mng.tr

        self.layer_adder = LayerAdder()
        self.layer_adder.tr = self.tr
        self.layer_adder.tbl_result = self.tbl_result

        self.db_mng = DataBaseManager(trad=self.tr, settings_manager=self.settings_mng)

        self.lim_checker = LimitationsChecker(self.layer_adder, self.tr)

        self.pix_geom_dict = {
            point_list: {"tooltip": "Point", "pix": pix_point},
            polygon_list: {"tooltip": "Polygon", "pix": pix_polyg},
            line_list: {"tooltip": "Line", "pix": pix_line},
            multi_list: {"tooltip": "MultiPolygon", "pix": pix_multi},
        }
        # set instantiate and load JSON file cache content
        self.cache_mng = CacheManager(geo_service_manager=self.layer_adder.geo_srv_mng, settings_manager=self.settings_mng)
        self.cache_mng.tr = self.tr

        self.service_ico_dict = {
            "efs": ico_efs,
            "ems": ico_ems,
            "wfs": ico_wfs,
            "wms": ico_wms,
            "wmts": ico_wmts,
        }

    def show_results(self, api_results):
        """Display the results in a table."""

        logger.info("Results manager called. Displaying the results")
        try:
            self.tbl_result.horizontalHeader().sectionResized.disconnect()
        except TypeError:
            pass

        tbl_result = self.tbl_result

        tbl_result.setRowCount(len(api_results.get("results")))

        # dimensions (see https://github.com/isogeo/isogeo-plugin-qgis/issues/276)
        hheader = tbl_result.horizontalHeader()
        # make the entire width of the table is occupied
        hheader.setSectionResizeMode(1)
        # make date and icone columns width adapted to their content
        # so title and adding columns occupy the rest of the available width
        hheader.setSectionResizeMode(1, 3)
        hheader.setSectionResizeMode(2, 3)

        vheader = tbl_result.verticalHeader()

        # Looping inside the table lines. For each of them, showing the title,
        # abstract, geometry type, and a button that allow to add the data
        # to the canvas.
        count = 0
        for i in api_results.get("results"):
            md = Metadata.clean_attributes(i)
            # get metadata's keywords from tags, they will be displayed in QGIS
            # 'layer properties' if the layer is added to the canvas
            md.keywords = [md.tags.get(kw) for kw in md.tags if kw.startswith("keyword:isogeo")]
            # COLUMN 1 - Title and abstract
            # Displaying the metadata title inside a button
            title = md.title_or_name()
            if title:
                btn_md_title = QPushButton(title)
            else:
                btn_md_title = QPushButton(self.tr("Undefined", context=__class__.__name__))
                btn_md_title.setStyleSheet("font: italic")

            # Connecting the button to the full metadata popup
            btn_md_title.pressed.connect(partial(self.md_asked.emit, md._id))

            # Insert it in column 1
            tbl_result.setCellWidget(count, 0, btn_md_title)

            # COLUMN 2 - Data last update
            lbl_date = QLabel(tbl_result)
            lbl_date.setText(plg_tools.handle_date(md._modified))
            lbl_date.setMargin(5)
            lbl_date.setAlignment(Qt.AlignCenter)
            tbl_result.setCellWidget(count, 1, lbl_date)

            # COLUMN 3 - Geometry type
            lbl_geom = QLabel(tbl_result)
            if md.geometry:
                if md.geometry == "TIN":
                    tbl_result.setItem(count, 2, QTableWidgetItem("TIN"))
                elif md.geometry in known_geom_list:
                    for geom_type in self.pix_geom_dict:
                        if md.geometry in geom_type:
                            geom_item = self.pix_geom_dict.get(geom_type)
                            lbl_geom.setPixmap(geom_item.get("pix"))
                            lbl_geom.setToolTip(
                                self.tr(geom_item.get("tooltip"), context=__class__.__name__)
                            )
                        else:
                            continue
                else:
                    tbl_result.setItem(
                        count,
                        2,
                        QTableWidgetItem("?"),
                    )
            else:
                if "rasterDataset" in md.type:
                    lbl_geom.setPixmap(pix_rastr)
                    lbl_geom.setToolTip(self.tr("Raster", context=__class__.__name__))
                elif "service" in md.type:
                    lbl_geom.setPixmap(pix_serv)
                    lbl_geom.setToolTip(self.tr("Service", context=__class__.__name__))
                elif "noGeoDataset" in md.type:
                    lbl_geom.setPixmap(pix_table)
                    lbl_geom.setToolTip(self.tr("Table", context=__class__.__name__))
                else:
                    lbl_geom.setPixmap(pix_nogeo)
                    lbl_geom.setToolTip(self.tr("Unknown geometry", context=__class__.__name__))
            lbl_geom.setAlignment(Qt.AlignCenter)
            tbl_result.setCellWidget(count, 2, lbl_geom)

            # COLUMN 4 - Add options
            add_options_dict = {}

            # Build metadata portal URL if the setting is checked in "Settings" tab
            portal_md_url = self.build_md_portal_url(md._id)

            # Files and tables direct access
            if md.format:
                # If the data is a vector and the path is available, store
                # useful information in the dict
                if md.format in li_formats_vect and md.path:
                    add_path = self._filepath_builder(md.path)
                    if add_path:
                        params = [
                            "vector",
                            add_path,
                            md.title,
                            md.abstract,
                            md.keywords,
                            portal_md_url,
                        ]
                        add_options_dict[self.tr("Data file", context=__class__.__name__)] = params
                    else:
                        pass
                # Same if the data is a raster
                elif md.format in li_formats_rastr and md.path:
                    add_path = self._filepath_builder(md.path)
                    if add_path:
                        params = [
                            "raster",
                            add_path,
                            md.title,
                            md.abstract,
                            md.keywords,
                            portal_md_url,
                        ]
                        add_options_dict[self.tr("Data file", context=__class__.__name__)] = params
                    else:
                        pass
                # If the data is a postGIS table and the connection has
                # been saved in QGIS.
                elif md.format == "postgis" and self.db_mng.pgis_available:
                    if (
                        md.path
                        and md.name
                        and md.path
                        in self.db_mng.dbms_specifics_infos.get("PostgreSQL").get("db_names")
                        and "." in md.name
                    ):
                        available_connections = [
                            pg_conn
                            for pg_conn in self.db_mng.dbms_specifics_infos.get("PostgreSQL").get(
                                "connections"
                            )
                            if (
                                md.path == pg_conn.get("database")
                                or md.path == pg_conn.get("database_alias")
                            )
                            and pg_conn.get("prefered")
                        ]
                        if not len(available_connections):
                            available_connections = [
                                pg_conn
                                for pg_conn in self.db_mng.dbms_specifics_infos.get(
                                    "PostgreSQL"
                                ).get("connections")
                                if md.path == pg_conn.get("database")
                                or md.path == pg_conn.get("database_alias")
                            ]
                        else:
                            pass

                        for connection in available_connections:
                            if "tables" in connection:
                                pass
                            else:
                                conn = self.db_mng.establish_postgis_connection(**connection)
                                if not conn:
                                    connection["uri"] = 0
                                    connection["tables"] = 0
                                    self.db_mng.dbms_specifics_infos["PostgreSQL"][
                                        "invalid_connections"
                                    ].append(connection.get("connection"))
                                    logger.info(
                                        "'{}' connection saved as invalid".format(
                                            connection.get("connection")
                                        )
                                    )
                                    continue
                                else:
                                    connection["uri"] = conn[0]
                                    connection["tables"] = conn[1]
                                    connection["db_connector"] = conn[2]

                            tables_infos = connection.get("tables")
                            if tables_infos == 0:
                                pass
                            else:
                                schema = md.name.split(".")[0]
                                table = md.name.split(".")[1]
                                if any(
                                    infos[2] == schema and infos[1] == table
                                    for infos in tables_infos
                                ):
                                    params = {
                                        "base_name": md.path,
                                        "schema": schema,
                                        "table": table,
                                        "connection": connection,
                                        "abstract": md.abstract,
                                        "title": md.title,
                                        "keywords": md.keywords,
                                        "md_portal_url": portal_md_url,
                                        "dbms": "PostgreSQL",
                                    }
                                    options_key = "PostgreSQL - {}".format(
                                        connection.get("connection")
                                    )
                                    add_options_dict[options_key] = params
                                else:
                                    pass
                        self.db_mng.set_qsettings_connections(
                            "PostgreSQL",
                            "invalid",
                            self.db_mng.dbms_specifics_infos.get("PostgreSQL").get(
                                "invalid_connections"
                            ),
                        )
                    else:
                        pass

                # If the data is a Oracle table and the connection has
                # been saved in QGIS.
                elif md.format == "oracle" and self.db_mng.ora_available:
                    if (
                        md.path
                        and md.name
                        and any(
                            md.path in self.db_mng.dbms_specifics_infos.get("Oracle").get(key)
                            for key in ["db_names", "db_aliases"]
                        )
                        and "." in md.name
                    ):
                        available_connections = [
                            ora_conn
                            for ora_conn in self.db_mng.dbms_specifics_infos.get("Oracle").get(
                                "connections"
                            )
                            if (
                                md.path == ora_conn.get("database")
                                or md.path == ora_conn.get("database_alias")
                            )
                            and ora_conn.get("prefered")
                        ]
                        if not len(available_connections):
                            available_connections = [
                                ora_conn
                                for ora_conn in self.db_mng.dbms_specifics_infos.get("Oracle").get(
                                    "connections"
                                )
                                if md.path == ora_conn.get("database")
                                or md.path == ora_conn.get("database_alias")
                            ]
                        else:
                            pass

                        for connection in available_connections:
                            if "tables" in connection:
                                pass
                            else:
                                conn = self.db_mng.establish_oracle_connection(**connection)
                                if not conn:
                                    connection["uri"] = 0
                                    connection["tables"] = 0
                                    connection["db_connector"] = 0
                                    self.db_mng.dbms_specifics_infos["Oracle"][
                                        "invalid_connections"
                                    ].append(connection.get("connection"))
                                    logger.info(
                                        "'{}' connection saved as invalid".format(
                                            connection.get("connection")
                                        )
                                    )
                                    continue
                                else:
                                    connection["uri"] = conn[0]
                                    connection["tables"] = conn[1]
                                    connection["db_connector"] = conn[2]

                            tables_infos = connection.get("tables")
                            if tables_infos == 0:
                                pass
                            else:
                                schema = md.name.split(".")[0]
                                table = md.name.split(".")[1]
                                if any(
                                    infos[0] == schema and infos[1] == table
                                    for infos in tables_infos
                                ):
                                    params = {
                                        "base_name": md.path,
                                        "schema": schema,
                                        "table": table,
                                        "connection": connection,
                                        "abstract": md.abstract,
                                        "title": md.title,
                                        "keywords": md.keywords,
                                        "md_portal_url": portal_md_url,
                                        "dbms": "Oracle",
                                    }
                                    options_key = "Oracle - {}".format(connection.get("connection"))
                                    add_options_dict[options_key] = params
                                else:
                                    pass
                        self.db_mng.set_qsettings_connections(
                            "Oracle",
                            "invalid",
                            self.db_mng.dbms_specifics_infos.get("Oracle").get(
                                "invalid_connections"
                            ),
                        )
                    else:
                        pass

                elif md.format.lower() in self.service_ico_dict:
                    pass
                else:
                    logger.debug(
                        "Metadata {} has a format ({}) but it's not handled hear or path is"
                        " missing".format(md._id, md.format)
                    )
                    pass
            # Associated service layers
            if md.type == "vectorDataset" or md.type == "rasterDataset" or md.type == "noGeoDataset":
                for layer in md.serviceLayers:
                    service = layer.get("service")
                    if service is not None and service.get("format") and not (service.get("format") in ["ems", "efs"] and layer.get("type") == "table"):
                        srv_details = {
                            "path": service.get("path", "NR"),
                            "formatVersion": service.get("formatVersion"),
                        }
                        service_type = service.get("format").upper()
                        if service.get("format") in self.service_ico_dict:
                            params = [service_type, layer, srv_details]
                        else:
                            params = [0]
                            logger.debug(
                                "Unexpected service format detected for '{}' metadata : {}".format(
                                    md._id, service
                                )
                            )
                            continue

                        if params[0] != 0:
                            basic_md = [
                                md.title,
                                md.abstract,
                                md.keywords,
                                portal_md_url,
                            ]
                            params.append(basic_md)
                            layer_title = geo_srv_mng.build_layer_title(service_type, layer)
                            btn_label = "{} : {}".format(service_type, layer_title)
                            dict_key = "{}-*-{}".format(btn_label, service.get("_id"))  # for #408
                            add_options_dict[dict_key] = params
                        else:
                            logger.warning(
                                "Faile to build service URL for {} layer '{}' (of metadata {}): {}".format(
                                    service.get("format").upper(),
                                    layer.get("id"),
                                    md._id,
                                    params[1],
                                )
                            )
                            pass
                    else:
                        pass

            # New association mode. For services metadata sheet, the layers
            # are stored in the purposely named include: "layers".
            elif md.type == "service":
                if md.layers is not None:
                    srv_details = {
                        "path": md.path,
                        "formatVersion": md.formatVersion,
                    }
                    if md.format.lower() in self.service_ico_dict:
                        service_type = md.format.upper()
                        for layer in md.layers:
                            if md.format.lower() in ["ems", "efs"] and layer.get("type") == "table":
                                continue
                            else:
                                layer_title = geo_srv_mng.build_layer_title(service_type, layer)
                                btn_label = "{} : {}".format(service_type, layer_title)
                                params = [service_type, layer, srv_details]
                                basic_md = [
                                    md.title,
                                    md.abstract,
                                    md.keywords,
                                    portal_md_url,
                                ]
                                params.append(basic_md)
                                add_options_dict[btn_label] = params
                    else:
                        pass
            else:
                pass
            # Now the plugin has tested every possibility for the layer to be
            # added. The "Add" column has to be filled accordingly.

            # If the data can't be added, just insert "can't" text.
            if add_options_dict == {}:
                text = self.tr("Can't be added", context=__class__.__name__)
                fake_button = QPushButton(text)
                fake_button.setStyleSheet("text-align: left")
                fake_button.setEnabled(False)
                tbl_result.setCellWidget(count, 3, fake_button)
            # If the data can be added
            else:
                data_info = {"limitations": None, "layer": None}
                # retrieves data limitations
                data_info["limitations"] = md.limitations

                # If there is only one way for the data to be added, insert a button.
                if len(add_options_dict) == 1:
                    text = list(add_options_dict.keys())[0]
                    params = add_options_dict.get(text)
                    option_type = text.split(" : ")[0]
                    # services
                    if option_type.lower() in self.service_ico_dict:
                        icon = self.service_ico_dict.get(option_type.lower())
                    # Postgre table
                    elif option_type.startswith("Postgre"):
                        icon = ico_pgis
                    # Oracle table
                    elif option_type.startswith("Oracle"):
                        icon = ico_ora
                    # Data file
                    elif option_type.startswith(self.tr("Data file", context=__class__.__name__)):
                        icon = ico_file
                    # Unkown option
                    else:
                        logger.debug(
                            "Undefined add option type : {}/{} --> {}".format(
                                option_type, text, params
                            )
                        )
                    # create the add button with the icon corresponding to the add option
                    add_button = QPushButton(icon, option_type)
                    add_button.setStyleSheet("text-align: left")
                    # connect the widget to the adding method from LayerAdder class
                    data_info["layer"] = ("info", params, count)
                    add_button.pressed.connect(partial(self.lim_checker.check, data_info))
                    tbl_result.setCellWidget(count, 3, add_button)
                # Else, add a combobox, storing all possibilities.
                else:
                    combo = QComboBox()
                    combo.installEventFilter(self.form_mng)
                    for option in add_options_dict:
                        option_type = option.split(" : ")[0]
                        # services
                        if option_type.lower() in self.service_ico_dict:
                            icon = self.service_ico_dict.get(option_type.lower())
                        # Postgre table
                        elif option.startswith("Postgre"):
                            icon = ico_pgis
                        # Oracle table
                        elif option.startswith("Oracle"):
                            icon = ico_ora
                        # Data file
                        elif option.startswith(self.tr("Data file", context=__class__.__name__)):
                            icon = ico_file
                        # Unkown option
                        else:
                            logger.debug(
                                "Undefined add option type : {}/{} --> {}".format(
                                    option_type, option, params
                                )
                            )
                        # add a combobox item with the icon corresponding to the add option
                        if "-*-" in option:
                            option_label = "".join(option.split("-*-")[:-1])  # for #408
                        else:
                            option_label = option
                        combo.addItem(icon, option_label, add_options_dict.get(option))
                    # connect the widget to the adding method from LayerAdder class
                    data_info["layer"] = ("index", count)
                    combo.activated.connect(partial(self.lim_checker.check, data_info))
                    combo.model().sort(0)  # sort alphabetically on option prefix. see: #113
                    tbl_result.setCellWidget(count, 3, combo)

            # make the widget (button or combobox) width the same as the column width
            tbl_result.cellWidget(count, 3).setFixedWidth(hheader.sectionSize(3))
            count += 1

        # dimensions bis (see https://github.com/isogeo/isogeo-plugin-qgis/issues/276)
        # last column take the width of his content
        hheader.setSectionResizeMode(3, 3)
        # the height of the row adapts to the content without falling below 30px
        vheader.setMinimumSectionSize(30)
        vheader.setSectionResizeMode(3)
        # adapt title column button width content to column width
        title_column_width = hheader.sectionSize(0)
        scrollBar_width = tbl_result.verticalScrollBar().sizeHint().width()
        max_width = title_column_width - scrollBar_width - 10
        for i in range(tbl_result.rowCount()):
            btn_title = tbl_result.cellWidget(i, 0)
            btn_title.setToolTip(btn_title.text())
            plg_tools.format_widget_title(btn_title, max_width)

            # format add_option combobox item labels to fit the combobox width
            combo = tbl_result.cellWidget(i, 3)
            if isinstance(combo, QComboBox):
                combo_width = combo.width() - 50
                combo_fm = combo.fontMetrics()

                for i in range(combo.count()):
                    item_label = combo.itemText(i)
                    item_label_width = combo_fm.size(1, item_label).width()
                    if item_label_width > combo_width:
                        combo.setItemText(i, combo_fm.elidedText(item_label, 1, combo_width))
                        combo.setItemData(i, item_label, Qt.ToolTipRole)
                    else:
                        pass
            else:
                pass
        hheader.sectionResized.connect(partial(self.section_resized_slot))  # https://github.com/isogeo/isogeo-plugin-qgis/issues/438
        # method ending
        return None

    def section_resized_slot(self, *args):
        """ https://github.com/isogeo/isogeo-plugin-qgis/issues/438
        """

        scrollBar_width = self.tbl_result.verticalScrollBar().sizeHint().width()
        max_width = args[2] - scrollBar_width - 10

        for i in range(self.tbl_result.rowCount()):
            btn_title = self.tbl_result.cellWidget(i, 0)
            btn_title.setText(btn_title.toolTip())
            plg_tools.format_widget_title(btn_title, max_width)

    # -- PRIVATE METHOD -------------------------------------------------------
    def _filepath_builder(self, metadata_path: str):
        """Build filepath from metadata path handling various cases. See: #129.

        :param str metadata_path: path to the dataset found in metadata
        """
        # building
        filepath = Path(metadata_path)
        try:
            dir_file = str(filepath.parent.resolve())
        except OSError as e:
            logger.debug("'{}' is not a regular path : {}".format(metadata_path, e))
            return False
        if dir_file not in self.cache_mng.cached_unreached_paths:
            try:
                with open(filepath):
                    pass
            except Exception as e:
                self.cache_mng.add_file_path(dir_file)
                logger.info("{} path is not reachable and has been cached:".format(dir_file))
                logger.info("{}".format(e))
                return False
            return str(filepath)
        else:
            logger.debug("Path has been ignored because it's cached.")
            return False

    def build_md_portal_url(self, metadata_id: str):
        """Build the URL of the metadata into Isogeo Portal (see https://github.com/isogeo/isogeo-plugin-qgis/issues/312)

        :param str metadata_id: id of the metadata
        """
        add_portal_md_url = int(self.settings_mng.get_value("isogeo/settings/add_metadata_url_portal", 0))
        portal_base_url = self.settings_mng.get_value("isogeo/settings/portal_base_url", "")

        if add_portal_md_url and portal_base_url != "":
            portal_md_url = portal_base_url + "/" + metadata_id
        else:
            portal_md_url = ""

        return portal_md_url


# #############################################################################
# ##### Stand alone program ########
# ##################################
if __name__ == "__main__":
    """Standalone execution."""
