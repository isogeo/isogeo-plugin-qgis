# -*- coding: utf-8 -*-
#! python3  # noqa: E265

# Standard library
import logging
from functools import partial
from pathlib import Path

# PyQT
# from QByteArray
from qgis.PyQt.QtCore import QSettings, QObject, pyqtSignal, Qt
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

qsettings = QSettings()
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
    """Basic class that holds utilitary methods for the plugin."""

    md_asked = pyqtSignal(str)

    def __init__(self, search_form_manager: object):
        # inheritance
        super().__init__()

        self.form_mng = search_form_manager
        self.tbl_result = self.form_mng.tbl_result
        self.tr = self.form_mng.tr

        self.layer_adder = LayerAdder()
        self.layer_adder.tr = self.tr
        self.layer_adder.tbl_result = self.tbl_result

        self.db_mng = DataBaseManager(self.tr)

        self.lim_checker = LimitationsChecker(self.layer_adder, self.tr)

        self.pix_geom_dict = {
            point_list: {"tooltip": "Point", "pix": pix_point},
            polygon_list: {"tooltip": "Polygon", "pix": pix_polyg},
            line_list: {"tooltip": "Line", "pix": pix_line},
            multi_list: {"tooltip": "MultiPolygon", "pix": pix_multi},
        }
        # set instanciate and load JSON file cache content
        self.cache_mng = CacheManager(self.layer_adder.geo_srv_mng)
        self.cache_mng.loader()
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

        tbl_result = self.tbl_result

        # Set table rows
        if api_results.get("total") >= 10:
            tbl_result.setRowCount(10)
        else:
            tbl_result.setRowCount(api_results.get("total"))

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
            md.keywords = [
                md.tags.get(kw) for kw in md.tags if kw.startswith("keyword:isogeo")
            ]
            # COLUMN 1 - Title and abstract
            # Displaying the metadata title inside a button
            title = md.title_or_name()
            if title:
                btn_md_title = QPushButton(plg_tools.format_button_title(title))
            else:
                btn_md_title = QPushButton(
                    self.tr("Undefined", context=__class__.__name__)
                )
                btn_md_title.setStyleSheet("font: italic")

            # Connecting the button to the full metadata popup
            btn_md_title.pressed.connect(partial(self.md_asked.emit, md._id))
            # Putting the abstract as a tooltip on this button
            if md.abstract:
                btn_md_title.setToolTip(md.abstract[:300])
            else:
                pass
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
                                self.tr(
                                    geom_item.get("tooltip"), context=__class__.__name__
                                )
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
                else:
                    lbl_geom.setPixmap(pix_nogeo)
                    lbl_geom.setToolTip(
                        self.tr("Unknown geometry", context=__class__.__name__)
                    )
            lbl_geom.setAlignment(Qt.AlignCenter)
            tbl_result.setCellWidget(count, 2, lbl_geom)

            # COLUMN 4 - Add options
            add_options_dict = {}

            # Build metadata portal URL if the setting is checked in "Settings" tab
            portal_md_url = self.build_md_portal_url(md._id)

            # Files and PostGIS direct access
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
                        add_options_dict[
                            self.tr("Data file", context=__class__.__name__)
                        ] = params
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
                        add_options_dict[
                            self.tr("Data file", context=__class__.__name__)
                        ] = params
                    else:
                        pass
                # If the data is a postGIS table and the connection has
                # been saved in QGIS.
                elif md.format == "postgis":
                    if (
                        md.path
                        and md.name
                        and md.path
                        in self.db_mng.dbms_specifics_infos.get("PostgreSQL").get(
                            "db_names"
                        )
                        and "." in md.name
                    ):
                        available_connections = [
                            pg_conn
                            for pg_conn in self.db_mng.dbms_specifics_infos.get(
                                "PostgreSQL"
                            ).get("connections")
                            if md.path == pg_conn.get("database")
                            and pg_conn.get("prefered")
                        ]
                        if not len(available_connections):
                            available_connections = [
                                pg_conn
                                for pg_conn in self.db_mng.dbms_specifics_infos.get(
                                    "PostgreSQL"
                                ).get("connections")
                                if md.path == pg_conn.get("database")
                            ]
                        else:
                            pass

                        for connection in available_connections:
                            if connection.get("tables"):
                                schema = md.name.split(".")[0]
                                table = md.name.split(".")[1]
                                tables_infos = connection.get("tables")
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
                                    options_key = "PostGIS - {}".format(
                                        connection.get("connection")
                                    )
                                    add_options_dict[options_key] = params
                                else:
                                    pass
                            else:
                                pass
                    else:
                        pass

                # If the data is a Oracle table and the connection has
                # been saved in QGIS.
                elif md.format == "oracle":
                    if (
                        md.path
                        and md.name
                        and md.path
                        in self.db_mng.dbms_specifics_infos.get("Oracle").get(
                            "db_names"
                        )
                        and "." in md.name
                    ):
                        available_connections = [
                            ora_conn
                            for ora_conn in self.db_mng.dbms_specifics_infos.get(
                                "Oracle"
                            ).get("connections")
                            if md.path == ora_conn.get("database")
                            and ora_conn.get("prefered")
                        ]
                        if not len(available_connections):
                            available_connections = [
                                ora_conn
                                for ora_conn in self.db_mng.dbms_specifics_infos.get(
                                    "Oracle"
                                ).get("connections")
                                if md.path == ora_conn.get("database")
                            ]
                        else:
                            pass

                        for connection in available_connections:
                            if connection.get("tables"):
                                schema = md.name.split(".")[0]
                                table = md.name.split(".")[1]
                                tables_infos = connection.get("tables")
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
                                    options_key = "Oracle - {}".format(
                                        connection.get("connection")
                                    )
                                    add_options_dict[options_key] = params
                                else:
                                    pass
                            else:
                                pass
                    else:
                        pass
                else:
                    logger.debug(
                        "Metadata {} has a format ({}) but it's not handled hear or path is"
                        "missing".format(md._id, md.format)
                    )
                    pass
            # Associated service layers
            if md.type == "vectorDataset" or md.type == "rasterDataset":
                for layer in md.serviceLayers:
                    service = layer.get("service")
                    if service is not None:
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
                            layer_title = geo_srv_mng.build_layer_title(
                                service_type, layer
                            )
                            btn_label = "{} : {}".format(service_type, layer_title)
                            add_options_dict[btn_label] = params
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
            # New association mode. For services metadata sheet, the layers
            # are stored in the purposely named include: "layers".
            elif md.type == "service":
                if md.layers is not None:
                    srv_details = {
                        "path": md.path,
                        "formatVersion": md.formatVersion,
                    }
                    if md.format in self.service_ico_dict:
                        service_type = md.format.upper()
                        for layer in md.layers:
                            layer_title = geo_srv_mng.build_layer_title(
                                service_type, layer
                            )
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
                    # PostGIS table
                    elif option_type.startswith("PostGIS"):
                        icon = ico_pgis
                    # Oracle table
                    elif option_type.startswith("Oracle"):
                        icon = ico_ora
                    # Data file
                    elif option_type.startswith(
                        self.tr("Data file", context=__class__.__name__)
                    ):
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
                    add_button.pressed.connect(
                        partial(self.lim_checker.check, data_info)
                    )
                    tbl_result.setCellWidget(count, 3, add_button)
                # Else, add a combobox, storing all possibilities.
                else:
                    combo = QComboBox()
                    for option in add_options_dict:
                        option_type = option.split(" : ")[0]
                        # services
                        if option_type.lower() in self.service_ico_dict:
                            icon = self.service_ico_dict.get(option_type.lower())
                        # PostGIS table
                        elif option.startswith("PostGIS"):
                            icon = ico_pgis
                        # PostGIS table
                        elif option.startswith("Oracle"):
                            icon = ico_ora
                        # Data file
                        elif option.startswith(
                            self.tr("Data file", context=__class__.__name__)
                        ):
                            icon = ico_file
                        # Unkown option
                        else:
                            logger.debug(
                                "Undefined add option type : {}/{} --> {}".format(
                                    option_type, option, params
                                )
                            )
                        # add a combobox item with the icon corresponding to the add option
                        combo.addItem(icon, option, add_options_dict.get(option))
                    # connect the widget to the adding method from LayerAdder class
                    data_info["layer"] = ("index", count)
                    combo.activated.connect(partial(self.lim_checker.check, data_info))
                    combo.model().sort(
                        0
                    )  # sort alphabetically on option prefix. see: #113
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
        # method ending
        return None

    # -- PRIVATE METHOD -------------------------------------------------------
    def _filepath_builder(self, metadata_path: str):
        """Build filepath from metadata path handling various cases. See: #129.

        :param str metadata_path: path found in metadata
        """
        # building
        filepath = Path(metadata_path)
        try:
            dir_file = str(filepath.parent.resolve())
        except OSError as e:
            logger.debug("'{}' is not a reguler path : {}".format(metadata_path, e))
            return False
        if dir_file not in self.cache_mng.cached_unreach_paths:
            try:
                with open(filepath) as f:
                    return str(filepath)
            except Exception as e:
                self.cache_mng.cached_unreach_paths.append(dir_file)
                logger.info(
                    "Path is not reachable and has been cached:{} / {}".format(
                        dir_file, e
                    )
                )
                return False
        else:
            logger.debug("Path has been ignored because it's cached.")
            return False

    def build_md_portal_url(self, metadata_id: str):
        """Build the URL of the metadata into Isogeo Portal (see https://github.com/isogeo/isogeo-plugin-qgis/issues/312)

        :param str metadata_id: id of the metadata
        """
        add_portal_md_url = int(
            qsettings.value("isogeo/settings/add_metadata_url_portal", 0)
        )
        portal_base_url = self.form_mng.input_portal_url.text()

        if add_portal_md_url and portal_base_url != "":
            portal_md_url = portal_base_url + metadata_id
        else:
            portal_md_url = ""

        return portal_md_url


# #############################################################################
# ##### Stand alone program ########
# ##################################
if __name__ == "__main__":
    """Standalone execution."""
