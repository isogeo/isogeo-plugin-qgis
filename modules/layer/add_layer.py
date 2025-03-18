# -*- coding: utf-8 -*-
#! python3  # noqa: E265

# Standard library
import logging
import os

# PyQT
from qgis.PyQt.QtWidgets import QMessageBox

# PyQGIS
from qgis.core import (
    Qgis,
    QgsProject,
    QgsVectorLayer,
    QgsRasterLayer,
    QgsMessageLog,
    QgsApplication,
    QgsCoordinateReferenceSystem,
    QgsDataSourceUri,
    QgsWkbTypes,
    QgsNetworkAccessManager  # https://github.com/isogeo/isogeo-plugin-qgis/issues/467
)

from qgis.utils import iface

# Plugin modules
from ..tools import IsogeoPlgTools
from .metadata_sync import MetadataSynchronizer
from ..layer.geo_service import GeoServiceManager

# ############################################################################
# ########## Globals ###############
# ##################################

logger = logging.getLogger("IsogeoQgisPlugin")

plg_tools = IsogeoPlgTools()

li_datafile_types = ["vector", "raster"]

qgis_wms_formats = (
    "image/png",
    "image/png8",
    "image/jpeg",
    "image/svg",
    "image/gif",
    "image/geotiff",
    "image/tiff",
)

matching_wkb_SDO_GTYPE = {
    4: 7,
    5: 4,
    6: 5,
    7: 6,
}

li_wkb_multiGeom_ok = [[1, 4], [2, 5], [3, 6]]

qgis_version = Qgis.QGIS_VERSION
qgis_minor_version = int(qgis_version.split(".")[1])

# ############################################################################
# ##### Conditional imports ########
# ##################################

try:
    import requests

    logger.info("Dependencies - Requests version: {}".format(requests.__version__))
except ImportError:
    logger.warning("Dependencies - Requests not available")

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

        # prepare layer adding from geo service datas
        self.geo_srv_mng = GeoServiceManager()
        self.dict_service_types = {
            "WFS": ["WFS", QgsVectorLayer, self.geo_srv_mng.build_wfs_url],
            "WMS": ["wms", QgsRasterLayer, self.geo_srv_mng.build_wms_url],
            "EFS": ["arcgisfeatureserver", QgsVectorLayer, self.geo_srv_mng.build_efs_url],
            "EMS": ["arcgismapserver", QgsRasterLayer, self.geo_srv_mng.build_ems_url],
            "WMTS": ["wms", QgsRasterLayer, self.geo_srv_mng.build_wmts_url],
        }

        # catch QGIS log messages - see: https://gis.stackexchange.com/a/223965/19817
        QgsApplication.messageLog().messageReceived.connect(plg_tools.error_catcher)

    def invalid_layer_inform(self, data_type: str, data_source: str, error_msg: str):
        """Write a Warning into log fil + inform the user that the layer can't be added to the map canevas

        :param str data_type: the type of data ("vector", "raster", "WFS", "WMS", "EFS", "EMS" or "WMTS")
        :param str data_source: the path to data file or the URL to geographic service layer depending on data_type
        :param error_msg str: the QgsLayer error message
        """

        # Retrieving 'layer specific' informations
        if data_type in self.dict_service_types:
            layer_type = self.tr("Service layer", context=__class__.__name__)
            data_name = data_source
        elif data_type in li_datafile_types:
            layer_type = self.tr("Data file layer", context=__class__.__name__)
            data_type = data_type.capitalize()
            data_name = os.path.basename(data_source).split(".")[0]
        elif data_type == "PostGIS" or data_type == "Oracle":
            layer_type = self.tr("The table", context=__class__.__name__)
            data_name = data_source
        else:
            raise ValueError(
                "'data_type' argument value should be 'PostGIS', 'Oracle, 'vector', 'raster', 'WFS', 'WMS', 'EMS', 'EFS' or 'WMTS'"
            )

        # Let's inform the user
        logger.warning(
            "Invalid {} layer: {}. QGIS says: {}".format(data_type, data_source, error_msg)
        )
        msg = "<b>{} ({}) ".format(layer_type, data_type)
        msg += self.tr("is not valid", context=__class__.__name__)
        msg += ": <i>{}</i>".format(data_name)
        msg += ".</b><br><b>"
        msg += self.tr("Error:", context=__class__.__name__)
        msg += "</b><strong>{}</strong>".format(error_msg)

        QMessageBox.warning(
            iface.mainWindow(),
            self.tr("The layer can't be added", context=__class__.__name__),
            msg,
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
            raise ValueError("'data_type' argument value should be 'vector' or 'raster'")

        # If the layer is valid, add it to the map canvas and inform the user
        if layer.isValid():
            lyr = QgsProject.instance().addMapLayer(layer)
            layer_is_ok = 1
            try:
                QgsMessageLog.logMessage(
                    message="Data layer added: {}".format(name),
                    tag="Isogeo",
                    level=0,
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
                    "{} layer added: {}".format(data_type.capitalize(), name.decode("latin1"))
                )
        # If it's not, just inform the user
        else:
            error_msg = layer.error().message()
            layer_is_ok = 0

        if not layer_is_ok:
            self.invalid_layer_inform(data_type=data_type, data_source=path, error_msg=error_msg)
            return 0
        else:
            return lyr, layer

    def add_service_layer(
        self,
        layer_url: str,
        layer_title: str,
        service_type: str,
    ):
        """Add a geo service layer from its URL. Usefull for WMS multi-layer

        :param str layer_url: the url of the geo service layer
        :param str layer_title: the title to give to the added layer
        :param str service_type: the type of the geo service ("WFS", "WMS", "EFS", "EMS" or "WMTS")
        """
        # retrieve geo service type specific informations
        data_provider = self.dict_service_types.get(service_type)[0]
        QgsLayer = self.dict_service_types.get(service_type)[1]
        # create the layer
        if service_type in ["EFS", "EMS"]:  # https://github.com/isogeo/isogeo-plugin-qgis/issues/467
            QgsNetworkAccessManager.instance().cache().clear()
            layer = QgsLayer(layer_url, layer_title, data_provider)
        else:
            layer = QgsLayer(layer_url, layer_title, data_provider)
        # If the layer is valid, add it to the map canvas and inform the user
        if layer.isValid():
            lyr = QgsProject.instance().addMapLayer(layer)
            QgsMessageLog.logMessage(
                message="{} service layer added: {}".format(service_type, layer_url),
                tag="Isogeo",
                level=0,
            )
            logger.debug("{} layer added: {}".format(service_type, layer_url))
            layer_is_ok = 1
        # If the layer is not valid
        else:
            error_msg = layer.error().message()
            layer_is_ok = 0
            # Handling QGISServer Layers : https://github.com/isogeo/isogeo-plugin-qgis/issues/463
            layer_uri = QgsDataSourceUri()
            for param in layer_url.split("&"):
                key = param.split("=")[0]
                if key == "layers":
                    val = param.split("=")[1].replace("+", " ")
                else:
                    val = param.split("=")[1]
                layer_uri.setParam(key, val)
            layer_uri = bytes(layer_uri.encodedUri()).decode()
            layer = QgsLayer(layer_uri, layer_title, "wms")
            if layer.isValid():
                lyr = QgsProject.instance().addMapLayer(layer)
                QgsMessageLog.logMessage(
                    message="{} service layer added: {}".format(service_type, layer_url),
                    tag="Isogeo",
                    level=0,
                )
                logger.warning(
                    "{} layer added re-building QgsDataSourceUri: {}".format(
                        service_type, layer_uri
                    )
                )
                layer_is_ok = 1
            # If the layer is still not valid
            else:
                # Try to create it again without specifying data provider
                layer = QgsLayer(layer_url, layer_title)
                if layer.isValid():
                    lyr = QgsProject.instance().addMapLayer(layer)
                    QgsMessageLog.logMessage(
                        message="{} service layer added: {}".format(service_type, layer_url),
                        tag="Isogeo",
                        level=0,
                    )
                    logger.warning(
                        "{} layer added without specifying the data provider: {}".format(
                            service_type, layer_url
                        )
                    )
                    layer_is_ok = 1
                else:
                    error_msg = layer.error().message()
                    layer_is_ok = 0

        if not layer_is_ok:
            self.invalid_layer_inform(
                data_type=service_type, data_source=layer_url, error_msg=error_msg
            )
            return 0
        else:
            return lyr, layer

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
        if service_type not in self.dict_service_types:
            raise ValueError(
                "'service_type' argument value should be 'WFS', 'WMS', 'EMS', 'EFS' or 'WMTS'"
            )
        # It it's valid, set local variables depending on it
        else:
            url_builder = self.dict_service_types.get(service_type)[2]

        # use GeoServiceManager to retrieve all the infos we need to add the layer to the canvas
        layer_infos = url_builder(api_layer, service_details)
        # If everything is ok, let's create the layer that we gonna try to add to the canvas
        if layer_infos[0]:
            layer_url = layer_infos[2]
            layer_title = layer_infos[1]
        # else, informe the user about what went wrong
        else:
            error_msg = layer_infos[1]
            self.invalid_layer_inform(
                data_type=service_type,
                data_source=api_layer.get("id"),
                error_msg=error_msg,
            )
            return 0
        if isinstance(layer_url, list):
            added_layer = []
            for url in layer_url:
                index = layer_url.index(url)
                added = self.add_service_layer(url, layer_title[index], service_type)
                added_layer.append(added)
        else:
            added_layer = self.add_service_layer(layer_url, layer_title, service_type)
        return added_layer

    def add_from_pg_database(self, layer_info: dict):
        """Add a layer to QGIS map canvas from a Postgres database table.

        :param dict layer_info: dictionary containing informations needed to add the layer from the database table
        """

        logger.debug("Data type: PostGIS")
        # Give aliases to the data passed as argument
        db_connection = layer_info.get("connection", "")
        conn_name = db_connection.get("connection")
        base_name = layer_info.get("base_name", "")
        schema = layer_info.get("schema", "")
        table_name = layer_info.get("table", "")

        if not len(db_connection):
            error_msg = "None registered connection could be find for '{}' database.".format(
                base_name
            )
            self.invalid_layer_inform(
                data_type="PostGIS",
                data_source=schema + "." + table_name,
                error_msg=error_msg,
            )
            return 0
        else:
            uri = db_connection.get("uri")

        # Retrieve information about the table or the view from the database connection
        table_infos = [
            tab for tab in db_connection.get("tables") if tab[1] == table_name and tab[2] == schema
        ]
        if len(table_infos):
            table_infos = table_infos[0]
            if table_infos[0]:
                geometry_column = table_infos[8]
            else:
                geometry_column = None
            table = [schema, table_name, geometry_column]

            # Create a vector layer from retrieved infos
            # set database schema, table name, geometry column
            uri.setDataSource(table[0], table[1], table[2])

            li_layers_to_add = []
            if table[2] is None:  # in case of DTNG
                if qgis_minor_version >= 30:
                    uri.setWkbType(Qgis.WkbType(100))
                else:
                    uri.setWkbType(100)
                layer = QgsVectorLayer(uri.uri(), table[1], "postgres")
                li_layers_to_add.append(layer)
            else:
                # in case of multi-geometry table:
                li_geomTypes = []
                # first, request Postgres database about specific table geometry types
                try:
                    db_connector = db_connection.get("db_connector")
                    pg_table_geomType_request = "SELECT DISTINCT ST_GeometryType({}) FROM {}.\"{}\"".format(
                        table[2], table[0], table[1]
                    )
                    table_geomType_response = db_connector._fetchall(
                        db_connector._execute(None, pg_table_geomType_request)
                    )
                    for elem in table_geomType_response:
                        geomtype_label = elem[0].replace("ST_", "")
                        if hasattr(QgsWkbTypes(), geomtype_label):
                            geomtype_WKB = getattr(QgsWkbTypes(), geomtype_label)
                            li_geomTypes.append(geomtype_WKB)
                        else:
                            logger.warning(
                                "'{}.{}' PostGIS table geometry type '{}' could not be converted as WKB".format(
                                    table[0], table[1], elem[0]
                                )
                            )
                    li_geomTypes.sort()
                    for wkb_multiGeom_ok in li_wkb_multiGeom_ok:
                        if wkb_multiGeom_ok[0] in li_geomTypes and wkb_multiGeom_ok[1] in li_geomTypes:
                            del li_geomTypes[li_geomTypes.index(wkb_multiGeom_ok[0])]
                        else:
                            pass
                except Exception as e:
                    logger.warning(
                        "'{}.{}' PostGIS table geometry type could not be fetched : {}".format(
                            table[0], table[1], e
                        )
                    )
                    li_geomTypes = []

                is_multi_geom = 0
                # in case of point&multi-point, line&multi-line, polygon&multi-polygon,
                # QGIS is able to handle, so let's consider that the geometry type is multiple only
                # if there is 2 geometry types which are not [5, 1], [6, 2] or [7, 3]
                # or if there is more than 2 different geometry types
                if len(li_geomTypes) <= 1:
                    pass
                elif all(li_geomTypes != pg_multiGeom_ok for pg_multiGeom_ok in li_wkb_multiGeom_ok):
                    is_multi_geom = 1
                else:
                    pass
                # Building the layer
                li_geomType_layers = []
                if len(li_geomTypes) == 0:
                    if qgis_minor_version >= 30:
                        uri.setWkbType(Qgis.WkbType(100))
                    else:
                        uri.setWkbType(100)
                    layer = QgsVectorLayer(uri.uri(), table[1], "postgres")
                    li_geomType_layers.append(layer)
                elif not is_multi_geom:
                    if qgis_minor_version >= 30:
                        uri.setWkbType(Qgis.WkbType(li_geomTypes[0]))
                    else:
                        uri.setWkbType(li_geomTypes[0])
                    layer = QgsVectorLayer(uri.uri(), table[1], "postgres")
                    li_geomType_layers.append(layer)
                else:
                    li_geomTypes.sort(reverse=True)
                    for geomType in li_geomTypes:
                        if qgis_minor_version >= 30:
                            uri.setWkbType(Qgis.WkbType(geomType))
                        else:
                            uri.setWkbType(geomType)
                        layer = QgsVectorLayer(uri.uri(), table[1], "postgres")
                        li_geomType_layers += [layer]

                for geomType_layer in li_geomType_layers:
                    # If the layer is valid that's find
                    if geomType_layer.isValid():
                        li_layers_to_add.append(geomType_layer)
                    # If it's not and the table seems to be a view, let's try to handle that
                    elif not geomType_layer.isValid() and plg_tools.last_error[0] == "postgis" and "prim" in plg_tools.last_error[1]:
                        logger.warning(
                            "PostGIS layer may be a view, so key column is missing. Trying to automatically set one..."
                        )
                        # get layer fields name to set as key column
                        fields_names = [i.name() for i in layer.dataProvider().fields()]
                        # sort them by name containing id to better perf
                        fields_names.sort(key=lambda x: ("id" not in x, x))
                        for field in fields_names:
                            uri = db_connection.get("uri")
                            uri.setDataSource(table[0], table[1], table[2])
                            uri.setKeyColumn(field)
                            if qgis_minor_version >= 30:
                                uri.setWkbType(Qgis.WkbType(geomType_layer.dataProvider().wkbType()))
                            else:
                                uri.setWkbType(geomType_layer.dataProvider().wkbType())
                            layer = QgsVectorLayer(uri.uri(True), table[1], "postgres")
                            if layer.isValid():
                                logger.info("'{}' chose as key column to add {}.{} PostGIS view".format(field, schema, table_name))
                                li_layers_to_add.append(layer)
                                break
                            else:
                                continue
                        # let's prepare error message for the user just in case none field could be used as key column
                        error_msg = "The '{}' database view retrieved using '{}' data base connection is not valid : {}".format(
                            base_name, conn_name, plg_tools.last_error[1]
                        )
                    # If it's just not, let's prepare error message for the user
                    else:
                        logger.error(
                            "Layer not valid. table = {} : {}".format(table, plg_tools.last_error)
                        )
                        error_msg = "The '{}' database table retrieved using '{}' database connection is not valid : {}".format(
                            base_name, conn_name, plg_tools.last_error[1]
                        )
        # If none information could be find for this table, let's prepare error message for the user
        else:
            error_msg = "The table cannot be find into '{}' database using '{}' data base connection.".format(
                base_name, conn_name
            )

        # If the vector layer could be properly created, let's add it to the canvas
        added_layer = []
        if len(li_layers_to_add):
            for layer in li_layers_to_add:
                logger.debug("Data added: {} (geometry type : {})".format(table_name, layer.wkbType()))

                lyr = QgsProject.instance().addMapLayer(layer)
                added_layer.append([lyr, layer])
            return added_layer
        # else, let's inform the user
        else:
            self.invalid_layer_inform(
                data_type="PostGIS",
                data_source=schema + "." + table_name,
                error_msg=error_msg,
            )
            return 0

    def add_from_ora_database(self, layer_info: dict):
        """Add a layer to QGIS map canvas from an Oracle database table.

        :param dict layer_info: dictionary containing informations needed to add the layer from the database table
        """

        logger.debug("Data type: Oracle")
        # Give aliases to the data passed as argument
        db_connection = layer_info.get("connection", "")
        conn_name = db_connection.get("connection")
        base_name = layer_info.get("base_name", "")
        schema = layer_info.get("schema", "")
        table_name = layer_info.get("table", "")

        if not len(db_connection):
            error_msg = "None registered connection could be find for '{}' database.".format(
                base_name
            )
            self.invalid_layer_inform(
                data_type="Oracle",
                data_source=schema + "." + table_name,
                error_msg=error_msg,
            )
            return 0
        else:
            uri = db_connection.get("uri")

        # Retrieve information about the table or the view from the database connection
        table_infos = [
            tab for tab in db_connection.get("tables") if tab[0] == schema and tab[1] == table_name
        ][0]
        geometry_column = table_infos[2]
        table = [schema, table_name, geometry_column]

        # Create a vector layer from retrieved infos
        # set database schema, table name, geometry column
        uri.setDataSource(table[0], table[1], table[2])

        li_layers_to_add = []
        if table[2] is None:  # in case of DTNG
            if qgis_minor_version >= 30:
                uri.setWkbType(Qgis.WkbType(100))
            else:
                uri.setWkbType(100)
            layer = QgsVectorLayer(uri.uri(), table[1], "oracle")
            li_layers_to_add.append(layer)
        else:
            # in case of multi-geometry table:
            # first, request Oracle database about specific table geometry types
            try:
                db_connector = db_connection.get("db_connector")
                ora_table_geomType_request = "select DISTINCT c.{}.GET_GTYPE() from {}.{} c order by c.{}.GET_GTYPE() asc".format(
                    table[2], table[0], table[1], table[2]
                )
                table_geomType_response = db_connector._fetchall(
                    db_connector._execute(None, ora_table_geomType_request)
                )
                li_geomTypes = []
                for elem in table_geomType_response:
                    try:
                        geomtype_WKB = matching_wkb_SDO_GTYPE.get(int(elem[0]), int(elem[0]))
                        li_geomTypes.append(geomtype_WKB)
                    except Exception as e:
                        logger.warning(
                            "'{}.{}' Oracle table geometry type '{}' could not be converted as WKB".format(
                                table[0], table[1], elem[0]
                            )
                        )
                        logger.warning(e)
                li_geomTypes.sort()
                for wkb_multiGeom_ok in li_wkb_multiGeom_ok:
                    if wkb_multiGeom_ok[0] in li_geomTypes and wkb_multiGeom_ok[1] in li_geomTypes:
                        del li_geomTypes[li_geomTypes.index(wkb_multiGeom_ok[0])]
                    else:
                        pass

            except Exception as e:
                logger.warning(
                    "'{}.{}' Oracle table geometry type could not be fetched : {}".format(
                        table[0], table[1], e
                    )
                )
                li_geomTypes = []

            is_multi_geom = 0
            # in case of point&multi-point, line&multi-line, polygone&multi-polygone,
            # QGIS is able to handle, so let's consider that the geometry type is multiple only
            # if there is 2 geometry types which are not [5, 1], [6, 2] or [7, 3]
            # or if there is more than 2 differents geometry types
            if len(li_geomTypes) <= 1:
                pass
            elif all(li_geomTypes != ora_multiGeom_ok for ora_multiGeom_ok in li_wkb_multiGeom_ok):
                is_multi_geom = 1
            else:
                pass
            # Building the layer
            li_geomType_layers = []
            if len(li_geomTypes) == 0:
                if qgis_minor_version >= 30:
                    uri.setWkbType(Qgis.WkbType(100))
                else:
                    uri.setWkbType(100)
                layer = QgsVectorLayer(uri.uri(), table[1], "oracle")
                li_geomType_layers.append(layer)
            elif not is_multi_geom:
                if qgis_minor_version >= 30:
                    uri.setWkbType(Qgis.WkbType(li_geomTypes[0]))
                else:
                    uri.setWkbType(li_geomTypes[0])
                layer = QgsVectorLayer(uri.uri(), table[1], "oracle")
                li_geomType_layers.append(layer)
            else:
                li_geomTypes.sort(reverse=True)
                for geomType in li_geomTypes:
                    if qgis_minor_version >= 30:
                        uri.setWkbType(Qgis.WkbType(geomType))
                    else:
                        uri.setWkbType(geomType)
                    layer = QgsVectorLayer(uri.uri(), table[1], "oracle")
                    li_geomType_layers += [layer]

            for geomType_layer in li_geomType_layers:
                # If the layer is valid that's find
                if geomType_layer.isValid():
                    li_layers_to_add.append(geomType_layer)
                # If it's not and the table seems to be a view, let's try to handle that
                elif not geomType_layer.isValid() and plg_tools.last_error[0] == "oracle":
                    logger.warning(
                        "Oracle layer may be a view, so key column is missing. Trying to automatically set one..."
                    )
                    # get layer fields name to set as key column
                    fields_names = [i.name() for i in geomType_layer.dataProvider().fields()]
                    # sort them by name containing id to better perf
                    fields_names.sort(key=lambda x: ("id" not in x, x))
                    for field in fields_names:
                        uri = db_connection.get("uri")
                        uri.setDataSource(table[0], table[1], table[2])
                        uri.setKeyColumn(field)
                        if qgis_minor_version >= 30:
                            uri.setWkbType(Qgis.WkbType(geomType_layer.dataProvider().wkbType()))
                        else:
                            uri.setWkbType(geomType_layer.dataProvider().wkbType())
                        layer = QgsVectorLayer(uri.uri(True), table[1], "oracle")
                        if layer.isValid():
                            logger.debug(
                                "'{}' chose as key column to add Oracle view".format(field)
                            )
                            li_layers_to_add.append(layer)
                            break
                        else:
                            continue
                    # let's prepare error message for the user just in case none field could be used as key column
                    error_msg = "The '{}' database view retrieved using '{}' database connection is not valid : {}".format(
                        base_name, conn_name, plg_tools.last_error[1]
                    )
                # If it's just not, let's prepare error message for the user
                else:
                    logger.debug(
                        "Layer not valid. table = {} : {}".format(table, plg_tools.last_error)
                    )
                    error_msg = "The '{}' database table retrieved using '{}' database connection is not valid : {}".format(
                        base_name, conn_name, plg_tools.last_error[1]
                    )

        # If the vector layer could be properly created, let's add it to the canvas
        added_layer = []
        if len(li_layers_to_add):
            for layer in li_layers_to_add:
                logger.debug("Data added: {} (geomtype : {})".format(table_name, layer.wkbType()))

                table_infos = [
                    tab
                    for tab in db_connection.get("tables")
                    if tab[0] == schema and tab[1] == table_name
                ][0]

                if (
                    isinstance(table_infos[3], float)
                    or isinstance(table_infos[3], int)
                    or isinstance(table_infos[3], str)
                ):
                    table_srid = str(int(table_infos[3]))
                    table_crs = QgsCoordinateReferenceSystem("EPSG:" + table_srid)
                    layer.setCrs(table_crs)
                else:
                    pass

                lyr = QgsProject.instance().addMapLayer(layer)
                added_layer.append([lyr, layer])
            return added_layer
        # else, let's inform the user
        else:
            self.invalid_layer_inform(
                data_type="Oracle",
                data_source=schema + "." + table_name,
                error_msg=error_msg,
            )
            return 0

    def adding(self, layer_info):
        """Add a layer to QGIS map canvas.

        Take layer index, search the required information to add it in
        the temporary dictionary constructed in the show_results function.
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

        logger.info("Adding a layer from those parameters :")
        if isinstance(layer_info, dict):
            for key in layer_info:
                if key != "connection":
                    logger.info("> {} : {}".format(key, layer_info.get(key)))
                else:
                    pass
        else:
            logger.info("> {}".format(layer_info))

        if type(layer_info) is list:
            # If the layer to be added is from a file
            if layer_info[0] in li_datafile_types:
                added_layer = self.add_from_file(
                    layer_label=layer_label, path=layer_info[1], data_type=layer_info[0]
                )
            # If the layer to be added is from a geographic service
            elif layer_info[0] in self.dict_service_types:
                added_layer = self.add_from_service(
                    service_type=layer_info[0],
                    api_layer=layer_info[1],
                    service_details=layer_info[2],
                )
            else:
                raise ValueError(
                    "The data should be a file ('vector' or 'raster') or a geo service (OGC or ESRI), not : {}".format(
                        layer_info[0]
                    )
                )

        # If the data is a PostGIS table
        elif isinstance(layer_info, dict):
            if layer_info.get("dbms") == "PostgreSQL":
                added_layer = self.add_from_pg_database(layer_info=layer_info)
            else:
                added_layer = self.add_from_ora_database(layer_info=layer_info)

        else:
            pass

        # method ending for for WMS multi-layer
        if isinstance(added_layer, list):
            return_value = 0
            for added in added_layer:
                if not added:
                    pass
                else:
                    lyr = added[0]
                    layer = added[1]
                    if layer.isValid():
                        self.md_sync.basic_sync(layer=lyr, info=layer_info)
                    else:
                        pass
                    return_value = 1
        # method ending for other layers
        # If the layer haven't been added return 0
        elif not added_layer:
            return_value = 0
        # else fil 'QGIS Server' tab of layer Properties using MetadataSynchronizer
        else:
            lyr = added_layer[0]
            layer = added_layer[1]
            if layer.isValid():
                self.md_sync.basic_sync(layer=lyr, info=layer_info)
                return_value = 1
            else:
                return_value = 0

        return return_value
