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
from ..layer.geo_service import GeoServiceManager

# ############################################################################
# ########## Globals ###############
# ##################################

qsettings = QSettings()
logger = logging.getLogger("IsogeoQgisPlugin")

plg_tools = IsogeoPlgTools()
geo_srv_mng = GeoServiceManager()

li_datafile_types = ["vector", "raster"]

dict_service_types = {
    "WFS": [
        "WFS",
        QgsVectorLayer,
        geo_srv_mng.build_wfs_url
    ],
    "WMS": [
        "wms",
        QgsRasterLayer,
        geo_srv_mng.build_wms_url
    ],
    "EFS": [
        "arcgisfeatureserver",
        QgsVectorLayer,
        geo_srv_mng.build_efs_url
    ],
    "EMS": [
        "arcgismapserver",
        QgsRasterLayer,
        geo_srv_mng.build_ems_url
    ],
    "WMTS": [
        "wms",
        QgsRasterLayer,
        geo_srv_mng.build_wmts_url
    ]
}

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
        # self.geo_srv_mng = GeoServiceManager(self.cache_mng)

        # prepare layer adding from PostGIS table
        self.PostGISdict = dict()

        # catch QGIS log messages - see: https://gis.stackexchange.com/a/223965/19817
        QgsApplication.messageLog().messageReceived.connect(plg_tools.error_catcher)

    def invalid_layer_inform(self, data_type: str, data_source: str, error_msg: str):
        """Write a Warning into log fil + inform the user that the layer can't be added to the map canevas

        :param str data_type: the type of data ("vector", "raster", "WFS", "WMS", "EFS", "EMS" or "WMTS")
        :param str data_source: the path to data file or the URL to geographic service layer depending on data_type
        :param error_msg str: the QgsLayer error message
        """

        # Retrieving 'layer specific' informations
        if data_type in dict_service_types:
            layer_type = "service layer"
            data_name = data_source
        elif data_type in li_datafile_types:
            layer_type = "data file layer"
            data_type = data_type.capitalize()
            data_name = os.path.basename(data_source).split(".")[0]
        else:
            raise ValueError(
                "'data_type' argument value should be 'vector', 'raster', 'WFS', 'WMS', 'EMS', 'EFS' or 'WMTS'"
            )

        # Let's inform the user
        logger.warning(
            "Invalid {} {}: {}. QGIS says: {}".format(
                data_type, layer_type, data_source, error_msg
            )
        )
        QMessageBox.information(
            iface.mainWindow(),
            self.tr("Error", context=__class__.__name__),
            self.tr(
                "<strong>{} {} is not valid</strong> {}.<br><br><strong>QGIS says:</strong>{}".format(
                    data_type, layer_type, data_name, error_msg
                ),
                context=__class__.__name__,
            ),
        )

    def add_from_file(self, layer_label: str, path: str, data_type: str):
        """Add a layer to QGIS map canvas from a file.

        :param str layer_label: the name that gonna be given to layer into QGIS layers manager
        :param list path: the path to file from which the layer gonna be created
        :param data_type str: the type of data ("vector" or "raster")
        """
        # retrieving the name of the data file
        name = os.path.basename(path).split(".")[0]

        # Create the vector layer or the raster layer depending on data_type
        if data_type == "vector":
            layer = QgsVectorLayer(path, layer_label, "ogr")
        elif data_type == "raster":
            layer = QgsRasterLayer(path, layer_label)
        else:
            raise ValueError(
                "'data_type' argument value should be 'vector' or 'raster'"
            )

        # If the layer is valid, add it to the map canvas and inform the user
        if layer.isValid():
            lyr = QgsProject.instance().addMapLayer(layer)
            layer_is_ok = 1
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
            layer_is_ok = 0

        if not layer_is_ok:
            self.invalid_layer_inform(
                data_type=data_type, data_source=path, error_msg=error_msg
            )
            return 0, layer
        else:
            return lyr, layer

    # def add_from_service(
    #     self,
    #     layer_label: str,
    #     url: list,
    #     layer_name: str,
    #     service_type: str,
    #     additional_infos: list,
    # ):
    def add_from_service(
        self,
        service_type: str,
        api_layer: dict,
        service_details: dict,
    ):
        """Add a layer to QGIS map canvas from a Geographic Service Layer.

        :param str service_type: the type of the service ("WFS", "WMS", "EFS", "EMS" or "WMTS")
        :param dict api_layer: dict object containing Isogeo API informations about the layer
        :param dict service_details: dict object containing Isogeo API informations about the service
        """
        # If service_type argument value is invalid, raise error
        if service_type not in dict_service_types:
            raise ValueError(
                "'service_type' argument value should be 'WFS', 'WMS', 'EMS', 'EFS' or 'WMTS'"
            )
        # It it's valid, set local variables depending on it
        else:
            data_provider = dict_service_types.get(service_type)[0]
            QgsLayer = dict_service_types.get(service_type)[1]
            url_builder = dict_service_types.get(service_type)[2]

        # use GeoServiceManager to retrieve all the infos we need to add the layer to the canvas
        layer_infos = url_builder(api_layer, service_details)
        # If everything is ok, let's create the layer that we gonna try to add to the canvas
        if layer_infos[0]:
            url = layer_infos[2]
            layer_title = layer_infos[1]
            layer = QgsLayer(url, layer_title, data_provider)
        # else, informe the user about what went wrong #############################################################################
        else:
            error_msg = layer_infos[1]
            self.invalid_layer_inform(
                data_type=service_type, data_source=url, error_msg=error_msg
            )
            return 0

        # If the layer is valid, add it to the map canvas and inform the user
        if layer.isValid():
            lyr = QgsProject.instance().addMapLayer(layer)
            QgsMessageLog.logMessage(
                message="{} service layer added: {}".format(service_type, url),
                tag="Isogeo",
                level=0,
            )
            logger.debug("{} layer added: {}".format(service_type, url))
            layer_is_ok = 1
        # If the layer is not valid
        else:
            error_msg = layer.error().message()
            layer_is_ok = 0
            # Try to create it again without specifying data provider
            layer = QgsLayer(url, layer_title)
            if layer.isValid():
                lyr = QgsProject.instance().addMapLayer(layer)
                QgsMessageLog.logMessage(
                    message="{} service layer added: {}".format(
                        service_type, url
                    ),
                    tag="Isogeo",
                    level=0,
                )
                logger.debug("{} layer added without specifying the data provider: {}".format(service_type, url))
                layer_is_ok = 1
            else:
                error_msg = layer.error().message()
                layer_is_ok = 0

        if not layer_is_ok:
            self.invalid_layer_inform(
                data_type=service_type, data_source=url, error_msg=error_msg
            )
            return 0, layer
        else:
            return lyr, layer

    def add_from_database(self, layer_info: dict):
        """Add a layer to QGIS map canvas from a database table.

        :param dict layer_info: dictionnary containing informations needed to add the layer from the database table
        """

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
                        "PostGIS view layer added with [{}] as key column".format(field)
                    )
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

        return lyr, layer

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
            # If the layer to be added is from a file
            if layer_info[0] in li_datafile_types:
                added_layer = self.add_from_file(
                    layer_label=layer_label, path=layer_info[1], data_type=layer_info[0]
                )
            # If the layer to be added is from a geographic service
            elif layer_info[0] in dict_service_types:
                # added_layer = self.add_from_service(
                #     layer_label=layer_label,
                #     url=layer_info[2],
                #     layer_name=layer_info[1],
                #     service_type=layer_info[0],
                #     additional_infos=[layer_info[3], layer_info[4]],
                # )
                added_layer = self.add_from_service(
                    service_type=layer_info[0],
                    api_layer=layer_info[1],
                    service_details=layer_info[2]
                )
            else:
                raise ValueError(
                    "The data should be a file ('vector' or 'raster') or a geo service (OGC or ESRI), not : {}".format(
                        layer_info[0]
                    )
                )

        # If the data is a PostGIS table
        elif isinstance(layer_info, dict):
            added_layer = self.add_from_database(layer_info=layer_info)
        else:
            pass

        lyr = added_layer[0]
        layer = added_layer[1]
        # filling 'QGIS Server' tab of layer Properties
        if layer.isValid():
            try:
                self.md_sync.basic_sync(layer=lyr, info=layer_info)
            except IndexError as e:
                logger.debug(
                    "Not supported 'layer_info' format causes this error : {}".format(e)
                )
        else:
            pass
        return 1
