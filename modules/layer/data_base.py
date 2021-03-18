# -*- coding: utf-8 -*-
#! python3  # noqa: E265

# Standard library
import logging
from configparser import ConfigParser
from pathlib import Path
from os import environ
from functools import partial

# PyQT
from qgis.PyQt.QtCore import QSettings
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QTableWidgetItem, QComboBox, QLabel, QAbstractButton, QDialogButtonBox

# PyQGIS
from qgis.core import QgsDataSourceUri

try:
    from qgis.core import Qgis
except ImportError:
    from qgis.core import QGis as Qgis

from db_manager.db_plugins.postgis.connector import PostGisDBConnector
from db_manager.db_plugins.postgis.plugin import PostGisDBPlugin

# UI classes
from ...ui.db_connections.dlg_db_connections import Isogeodb_connections

# ############################################################################
# ########## Globals ###############
# ##################################

qgis_version = int("".join(Qgis.QGIS_VERSION.split(".")[:2]))

qsettings = QSettings()
logger = logging.getLogger("IsogeoQgisPlugin")

connection_parameters_names = ["host", "port", "dbname", "user", "password"]

ico_pgis = QIcon(":/images/themes/default/mIconPostgis.svg")

# ############################################################################
# ########## Classes ###############
# ##################################


class DataBaseManager:
    """Basic class that holds methods used to facilitate data base connections for layer
     adding."""

    # def __init__(self, cache_manager: object):
    def __init__(self):
        """Class constructor."""
        pgservicefile_value = environ.get("PGSERVICEFILE", None)
        if pgservicefile_value:
            self.pg_configfile_path = Path(pgservicefile_value)
            if not self.pg_configfile_path.is_file():
                logger.warning(
                    "PostGIS connections configuration file can't be used : {} is no recognized as a file.".format(
                        str(self.pg_configfile_path)
                    )
                )
                self.pg_configfile_path = 0
            elif not self.pg_configfile_path.exists():
                logger.warning(
                    "PostGIS connections configuration file can't be used : {} doesn't exist or is not reachable.".format(
                        str(self.pg_configfile_path)
                    )
                )
                self.pg_configfile_path = 0
            else:
                pass
        else:
            self.pg_configfile_path = 0

        self.pg_connections = list
        self.build_postgis_dict()

        self.pgdb_config_dialog = Isogeodb_connections()
        self.pgdb_config_dialog.setWindowIcon(ico_pgis)

        self.pgdb_config_dialog.btnbox.clicked.connect(self.pgdb_config_dialog_slot)

    def config_file_parser(
        self, file_path: Path, connection_service: str, connection_name: str
    ):
        """ Retrieve connection parameters values stored into configuration fiel corresponding
        to the specified file_path.
        """
        # First, check if the configuration file can be read
        config = ConfigParser()
        try:
            config.read(file_path)
        except Exception as e:
            error_msg = "{} configuration file cannot be read : {}".format(file_path, e)
            self.pg_configfile_path = 0
            return 0, error_msg

        # Then check if a section exists into configuration file content corresponding to connection_service value
        available_connection_services = config.sections()
        if connection_service not in available_connection_services:
            error_msg = "'{}' entry is missing into '{}' configuration file content.".format(
                connection_service, file_path
            )
            self.pg_configfile_path = 0
            return 0, error_msg
        else:
            service_params = config[connection_service]

        # Finally, check if the configuration file section content fit expectations
        service_params_name = list(service_params.keys())
        expected_params_name = ["host", "port", "dbname", "user", "password"]
        li_missing_params = [
            param_name
            for param_name in expected_params_name
            if param_name not in service_params_name
        ]
        li_empty_params = [
            param_name
            for param_name in expected_params_name
            if service_params[param_name] == ""
        ]
        if len(li_missing_params):
            error_msg = "Parameters missing into '{}' connection service : {}".format(
                connection_service, li_missing_params
            )
            return 0, error_msg
        elif len(li_empty_params):
            error_msg = "Parameters empty into '{}' connection service : {}".format(
                connection_service, li_empty_params
            )
            return 0, error_msg
        # and retrieve its contant if it do
        else:
            connection_dict = {
                "database": service_params["dbname"],
                "host": service_params["host"],
                "port": service_params["port"],
                "username": service_params["user"],
                "password": service_params["password"],
                "connection": connection_name,
            }
            return 1, connection_dict

    def establish_postgis_connection(
        self,
        host: str,
        port: str,
        username: str,
        password: str,
        database: str,
        connection: str,
    ):
        """Set the connectin to a specific PostGIS database and return the corresponding QgsDataSourceUri and PostGisDBConnector.
        """
        if not isinstance(host, str):
            raise TypeError(
                "'host' argument value should be str, not : {}".format(type(host))
            )
        elif not isinstance(port, str):
            raise TypeError(
                "'port' argument value should be str, not : {}".format(type(port))
            )
        elif not isinstance(username, str):
            raise TypeError(
                "'username' argument value should be str, not : {}".format(
                    type(username)
                )
            )
        elif not isinstance(password, str):
            raise TypeError(
                "'password' argument value should be str, not : {}".format(
                    type(password)
                )
            )
        elif not isinstance(database, str):
            raise TypeError(
                "'database' argument value should be str, not : {}".format(
                    type(database)
                )
            )
        elif not isinstance(connection, str):
            raise TypeError(
                "'connection' argument value should be str, not : {}".format(
                    type(connection)
                )
            )
        else:
            pass

        # build the connection URI and set the connection
        uri = QgsDataSourceUri()
        uri.setConnection(host, port, database, username, password)
        if qgis_version >= 316:
            pgis_db_plg = PostGisDBPlugin(connection)
            c = PostGisDBConnector(uri, pgis_db_plg)
        else:
            c = PostGisDBConnector(uri)

        li_table_infos = [infos for infos in c.getTables() if infos[0] == 1]

        return uri, li_table_infos

    def store_pgdb_config_preferences(self, connection_list: []):
        """Called when one of the 3 dialog button box is clicked to execute appropriate operations."""
        # for db_name in self.pg_connections_dbname:
        #     li_connections = [conn for conn in self.pg_connections if conn.get("database") == db_name]
        #     if any(conn.get("connection") in connection_list for conn in li_connections):
        #         for connection in li_connections:
        #             if connection.get("connection") not in connection_list:
        #                 self.pg_connections.remove(connection)
        #             else:
        #                 pass
        #     else:
        #         pass      
        # return

    def build_postgis_dict(self):
        """Build the dict that stores informations about PostGIS connections."""
        final_list = []
        for k in sorted(qsettings.allKeys()):
            if k.startswith("PostgreSQL/connections/") and k.endswith("/database"):
                if len(k.split("/")) == 4:
                    connection_name = k.split("/")[2]
                    logger.debug("*=====* {}".format(connection_name))
                    # for traditionnal connections
                    password_saved = qsettings.value(
                        "PostgreSQL/connections/" + connection_name + "/savePassword"
                    )
                    user_saved = qsettings.value(
                        "PostgreSQL/connections/" + connection_name + "/saveUsername"
                    )
                    # for configuration file connections
                    connection_service = qsettings.value(
                        "PostgreSQL/connections/" + connection_name + "/service"
                    )
                    if password_saved == "true" and user_saved == "true":
                        connection_dict = {
                            "database": qsettings.value(
                                "PostgreSQL/connections/"
                                + connection_name
                                + "/database"
                            ),
                            "host": qsettings.value(
                                "PostgreSQL/connections/" + connection_name + "/host"
                            ),
                            "port": qsettings.value(
                                "PostgreSQL/connections/" + connection_name + "/port"
                            ),
                            "username": qsettings.value(
                                "PostgreSQL/connections/"
                                + connection_name
                                + "/username"
                            ),
                            "password": qsettings.value(
                                "PostgreSQL/connections/"
                                + connection_name
                                + "/password"
                            ),
                            "connection": connection_name,
                        }

                    elif connection_service != "" and self.pg_configfile_path:
                        connection_dict = self.config_file_parser(
                            self.pg_configfile_path, connection_service, connection_name
                        )
                        if connection_dict[0]:
                            connection_dict = connection_dict[1]
                        else:
                            logger.warning(connection_dict[1])
                            continue
                    else:
                        continue
                    conn = self.establish_postgis_connection(**connection_dict)
                    connection_dict["uri"] = conn[0]
                    connection_dict["tables"] = conn[1]

                    final_list.append(connection_dict)
                else:
                    pass
            else:
                pass

        self.pg_connections = final_list
        self.pg_connections_connection = [conn.get("connection") for conn in final_list]
        self.pg_connections_dbname = [conn.get("database") for conn in final_list]

    def fill_pgdb_config_tbl(self):
        """Fill the dialog table from informations about PostGIS database embed connection"""

        li_unique_pgdb_name = set(self.pg_connections_dbname)
        tbl = self.pgdb_config_dialog.tbl

        tbl.clear()
        li_header_labels = [
            "Database", "Connection"
        ]
        tbl.setHorizontalHeaderLabels(li_header_labels)
        tbl.setRowCount(len(li_unique_pgdb_name))

        row = 0
        for dbname in li_unique_pgdb_name:
            # COLUMN 1
            dbname_item = QLabel()
            dbname_item.setText(dbname)
            dbname_item.setMargin(5)
            tbl.setCellWidget(row, 0, dbname_item)

            # COLUMN 2
            cbb_conn = QComboBox()
            cbb_conn.addItem(" - ", 0)
            li_pgdb_conn = [conn.get("connection") for conn in self.pg_connections if conn.get("database") == dbname]
            li_pgdb_conn.sort()
            for connection in li_pgdb_conn:
                cbb_conn.addItem(connection, 1)
            tbl.setCellWidget(row, 1, cbb_conn)

            row += 1

        hheader = tbl.horizontalHeader()
        vheader = tbl.verticalHeader()
        hheader.setSectionResizeMode(1)
        # hheader.setSectionResizeMode(0, 3)
        # hheader.setSectionResizeMode(1, 1)
        vheader.setMinimumSectionSize(10)

        self.pgdb_config_dialog.show()

    def open_pgdb_config_dialog(self):
        """Build the dialog table from informations about PostGIS database embed connection, then
        display the dialog window to the user"""

        self.fill_pgdb_config_tbl()
        self.pgdb_config_dialog.show()

    def pgdb_config_dialog_slot(self, btn: QAbstractButton):
        """Called when one of the 3 dialog button box is clicked to execute appropriate operations."""

        btn_role = self.pgdb_config_dialog.btnbox.buttonRole(btn)

        # If "Save" button was clicked
        if btn_role == 0:
            tbl = self.pgdb_config_dialog.tbl

            row_count = tbl.rowCount()
            li_connection_name = []

            # Retrieve the option selected in each combobxs
            for i in range(0, row_count):
                cbbox = tbl.cellWidget(i, 1)
                current_userData = cbbox.itemData(cbbox.currentIndex())
                if current_userData:
                    li_connection_name.append(cbbox.currentText())
                else:
                    pass
            # If options have been selected, store user preferences
            if len(li_connection_name):
                self.store_pgdb_config_preferences(li_connection_name)
            else:
                pass
        # If "Cancel" button was clicked
        elif btn_role == 1:
            pass
        # If "Reset" button was clicked
        elif btn_role == 7:
            self.fill_pgdb_config_tbl()
        else:
            logger.warning("Unexpected buttonRole : {} (https://doc.qt.io/qt-5/qdialogbuttonbox.html#ButtonRole-enum)".format(btn_role))
