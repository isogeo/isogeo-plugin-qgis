# -*- coding: utf-8 -*-
#! python3  # noqa: E265

# Standard library
import logging
import os

# PyQT
from qgis.PyQt.QtCore import QSettings
from qgis.PyQt.QtWidgets import QMessageBox

# PyQGIS
import db_manager.db_plugins.postgis.connector as pgis_con
from qgis.core import (
    QgsDataSourceUri,
    QgsProject,
    QgsVectorLayer,
    QgsRasterLayer,
    QgsMessageLog,
    QgsApplication,
)
from qgis.utils import iface

# Plugin modules
from ..tools import IsogeoPlgTools
from .metadata_sync import MetadataSynchronizer
from .geo_service import GeoServiceManager

# ############################################################################
# ########## Globals ###############
# ##################################

qsettings = QSettings()
logger = logging.getLogger("IsogeoQgisPlugin")

plg_tools = IsogeoPlgTools()
geo_srv_mng = GeoServiceManager()

qgis_wms_formats = (
    "image/png",
    "image/png8",
    "image/jpeg",
    "image/svg",
    "image/gif",
    "image/geotiff",
    "image/tiff",
)

# ############################################################################
# ##### Conditional imports ########
# ##################################

try:
    import requests

    logger.info("Depencencies - Requests version: {}".format(requests.__version__))
except ImportError:
    logger.warning("Depencencies - Requests not available")

# ############################################################################
# ########## Classes ###############
# ##################################


class LayerAdder:
    """Basic class that holds methods used to add layers to canvas."""

    def __init__(self):
        """Class constructor."""

        self.tbl_result = None
        self.tr = object
        self.md_sync = MetadataSynchronizer()

        # add layer from PostGIS table
        self.PostGISdict = dict()
        # catch QGIS log messages - see: https://gis.stackexchange.com/a/223965/19817
        QgsApplication.messageLog().messageReceived.connect(plg_tools.error_catcher)

    def add_from_file(self, layer_label: str, path: str, data_type: str):
        """Add a layer to QGIS map canvas from a file.

        :param str layer_label: the name that gonna be given to layer into QGIS layers manager
        :param list path: the path to file from which the layer gonna be created
        :data_type str: the type of data ("vector" or "raster")
        """
        # retrieving the name of the data file
        name = os.path.basename(path).split(".")[0]

        # Create the vector layer or the raster layer depending on data_type
        if data_type == "vector":
            layer = QgsVectorLayer(path, layer_label, "ogr")
        elif data_type == "raster":
            layer = QgsRasterLayer(path, layer_label)
        else:
            raise TypeError("'data_type' argument value should be 'vector' or 'raster'")

        # If the layer is valid, add it to the map canvas and inform the user
        if layer.isValid():
            lyr = QgsProject.instance().addMapLayer(layer)
            try:
                QgsMessageLog.logMessage(
                    message="Data layer added: {}".format(name), tag="Isogeo", level=0,
                )
                logger.debug("{} layer added: {}".format(data_type.capitalize(), path))
            except UnicodeEncodeError:
                QgsMessageLog.logMessage(
                    message="{} layer added:: {}".format(
                        data_type.capitalize(), name.decode("latin1")
                    ),
                    tag="Isogeo",
                    level=0,
                )
                logger.debug(
                    "{} layer added: {}".format(
                        data_type.capitalize(), name.decode("latin1")
                    )
                )
        # If it's not, just inform the user
        else:
            error_msg = layer.error().message()
            logger.warning(
                "Invalid {} layer: {}. QGIS says: {}".format(data_type, path, error_msg)
            )
            QMessageBox.information(
                iface.mainWindow(),
                self.tr("Error", context=__class__.__name__),
                self.tr(
                    "{} not valid {}. QGIS says: {}".format(
                        data_type.capitalize(), path, error_msg
                    ),
                    context=__class__.__name__,
                ),
            )

        return lyr

    def add_from_service(self, layer_label: str, path: list, url: str):
        """Add a layer to QGIS map canvas from a file.
        """
        return

    def adding(self, layer_info):
        """Add a layer to QGIS map canvas.

        Take layer index, search the required information to add it in
        the temporary dictionnary constructed in the show_results function.
        It then adds it.
        """
        # one of many add-on option
        if layer_info[0] == "index":
            combobox = self.tbl_result.cellWidget(layer_info[1], 3)
            layer_label = self.tbl_result.cellWidget(layer_info[1], 0).text()
            layer_info = combobox.itemData(combobox.currentIndex())
        # the only add_on option available
        elif layer_info[0] == "info":
            layer_label = self.tbl_result.cellWidget(layer_info[2], 0).text()
            layer_info = layer_info[1]
        else:
            pass
        self.md_sync.tr = self.tr
        logger.info("Adding a layer from those parameters :{}".format(layer_info))

        if type(layer_info) == list:
            # If the layer to be added is a vector file
            if layer_info[0] == "vector" or layer_info[0] == "raster":
                lyr = self.add_from_file(
                    layer_label=layer_label, path=layer_info[1], data_type=layer_info[0]
                )
            # If EFS link
            elif layer_info[0] == "EFS":
                name = layer_info[1]
                uri = layer_info[2]
                layer = QgsVectorLayer(uri, layer_label, "arcgisfeatureserver")
                if layer.isValid():
                    lyr = QgsProject.instance().addMapLayer(layer)
                    logger.debug("EFS layer added: {}".format(uri))
                else:
                    error_msg = layer.error().message()
                    logger.warning(
                        "Invalid service: {}. QGIS says: {}".format(uri, error_msg)
                    )
                    QMessageBox.information(
                        iface.mainWindow(),
                        self.tr("Error", context=__class__.__name__),
                        self.tr(
                            "EFS not valid. QGIS says: {}".format(error_msg),
                            context=__class__.__name__,
                        ),
                    )
            # If EMS link
            elif layer_info[0] == "EMS":
                name = layer_info[1]
                uri = layer_info[2]
                layer = QgsRasterLayer(uri, layer_label, "arcgismapserver")
                if layer.isValid():
                    lyr = QgsProject.instance().addMapLayer(layer)
                    logger.debug("EMS layer added: {}".format(uri))
                else:
                    error_msg = layer.error().message()
                    logger.warning(
                        "Invalid service: {}. QGIS says: {}".format(uri, error_msg)
                    )
                    QMessageBox.information(
                        iface.mainWindow(),
                        self.tr("Error", context=__class__.__name__),
                        self.tr(
                            "EMS not valid. QGIS says: {}".format(error_msg),
                            context=__class__.__name__,
                        ),
                    )
            # If WFS link
            elif layer_info[0] == "WFS":
                name = layer_info[1]
                url = layer_info[2]
                layer = QgsVectorLayer(url, layer_label, "WFS")
                if layer.isValid():
                    lyr = QgsProject.instance().addMapLayer(layer)
                    logger.debug("WFS layer added: {}".format(url))
                else:
                    error_msg = layer.error().message()
                    name_url = geo_srv_mng.build_wfs_url(
                        layer_info[3], layer_info[4], mode="complete"
                    )
                    if name_url[0] != 0:
                        layer = QgsVectorLayer(name_url[2], layer_label, "WFS")
                        if layer.isValid():
                            lyr = QgsProject.instance().addMapLayer(layer)
                            logger.debug("WFS layer added: {}".format(url))
                        else:
                            error_msg = layer.error().message()
                            logger.warning(
                                "Invalid service: {}. QGIS says: {}".format(
                                    url, error_msg
                                )
                            )
                    else:
                        QMessageBox.information(
                            iface.mainWindow(),
                            self.tr("Error", context=__class__.__name__),
                            self.tr(
                                "WFS is not valid. QGIS says: {}".format(error_msg),
                                context=__class__.__name__,
                            ),
                        )
                        pass
            # If WMS link
            elif layer_info[0] == "WMS":
                name = layer_info[1]
                url = layer_info[2]
                layer = QgsRasterLayer(url, layer_label, "wms")
                if layer.isValid():
                    lyr = QgsProject.instance().addMapLayer(layer)
                    logger.debug("WMS layer added: {}".format(url))
                else:
                    error_msg = layer.error().message()
                    name_url = geo_srv_mng.build_wms_url(
                        layer_info[3], layer_info[4], mode="complete"
                    )
                    if name_url[0] != 0:
                        layer = QgsRasterLayer(name_url[2], layer_label, "wms")
                        if layer.isValid():
                            lyr = QgsProject.instance().addMapLayer(layer)
                            logger.debug("WMS layer added: {}".format(url))
                        else:
                            error_msg = layer.error().message()
                            logger.warning(
                                "Invalid service: {}. QGIS says: {}".format(
                                    url, error_msg
                                )
                            )
                    else:
                        QMessageBox.information(
                            iface.mainWindow(),
                            self.tr("Error", context=__class__.__name__),
                            self.tr(
                                "WMS is not valid. QGIS says: {}".format(error_msg),
                                context=__class__.__name__,
                            ),
                        )
            # If WMTS link
            elif layer_info[0] == "WMTS":
                name = layer_info[1]
                url = layer_info[2]
                layer = QgsRasterLayer(url, layer_label, "wms")
                if layer.isValid():
                    lyr = QgsProject.instance().addMapLayer(layer)
                    logger.debug("WMTS service layer added: {}".format(url))
                else:
                    error_msg = layer.error().message()
                    logger.warning(
                        "Invalid service: {}. QGIS says: {}".format(url, error_msg)
                    )
                    QMessageBox.information(
                        iface.mainWindow(),
                        self.tr("Error", context=__class__.__name__),
                        self.tr(
                            "WMTS is not valid. QGIS says: {}".format(error_msg),
                            context=__class__.__name__,
                        ),
                    )
            else:
                pass

        # If the data is a PostGIS table
        elif isinstance(layer_info, dict):
            logger.debug("Data type: PostGIS")
            # Give aliases to the data passed as arguement
            base_name = layer_info.get("base_name", "")
            schema = layer_info.get("schema", "")
            table = layer_info.get("table", "")
            # Retrieve the database information stored in the PostGISdict
            uri = QgsDataSourceUri()
            host = self.PostGISdict[base_name]["host"]
            port = self.PostGISdict[base_name]["port"]
            user = self.PostGISdict[base_name]["username"]
            password = self.PostGISdict[base_name]["password"]
            # set host name, port, database name, username and password
            uri.setConnection(host, port, base_name, user, password)
            # Get the geometry column name from the database connexion & table
            # name.
            c = pgis_con.PostGisDBConnector(uri)
            dico = c.getTables()
            for i in dico:
                if i[0 == 1] and i[1] == table:
                    geometry_column = i[8]
            # set database schema, table name, geometry column
            uri.setDataSource(schema, table, geometry_column)
            # Adding the layer to the map canvas
            layer = QgsVectorLayer(uri.uri(), table, "postgres")
            if layer.isValid():
                lyr = QgsProject.instance().addMapLayer(layer)
                logger.debug("Data added: {}".format(table))
            elif (
                not layer.isValid()
                and plg_tools.last_error[0] == "postgis"
                and "prim" in plg_tools.last_error[1]
            ):
                logger.debug(
                    "PostGIS layer may be a view, "
                    "so key column is missing. "
                    "Trying to automatically set one..."
                )
                # get layer fields to set as key column
                fields = layer.dataProvider().fields()
                fields_names = [i.name() for i in fields]
                # sort them by name containing id to better perf
                fields_names.sort(key=lambda x: ("id" not in x, x))
                for field in fields_names:
                    uri.setKeyColumn(field)
                    layer = QgsVectorLayer(uri.uri(True), table, "postgres")
                    if layer.isValid():
                        lyr = QgsProject.instance().addMapLayer(layer)
                        logger.debug(
                            "PostGIS view layer added with [{}] as key column".format(
                                field
                            )
                        )
                        # filling 'QGIS Server' tab of layer Properties
                        self.md_sync.basic_sync(layer=lyr, info=layer_info)
                        return 1
                    else:
                        continue
            else:
                logger.debug("Layer not valid. table = {}".format(table))
                QMessageBox.information(
                    iface.mainWindow(),
                    self.tr("Error", context=__class__.__name__),
                    self.tr(
                        "The PostGIS layer is not valid."
                        " Reason: {}".format(plg_tools.last_error),
                        context=__class__.__name__,
                    ),
                )
                return 0
        # filling 'QGIS Server' tab of layer Properties
        if lyr.isValid():
            try:
                self.md_sync.basic_sync(layer=lyr, info=layer_info)
            except IndexError as e:
                logger.debug(
                    "Not supported 'layer_info' format causes this error : {}".format(e)
                )
        else:
            pass
        return 1
