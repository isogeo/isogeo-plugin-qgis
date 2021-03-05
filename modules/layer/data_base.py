# -*- coding: utf-8 -*-
#! python3  # noqa: E265

# Standard library
import logging
from configparser import ConfigParser
from pathlib import Path
from os import environ

# PyQT
from qgis.PyQt.QtCore import QSettings

# PyQGIS
from qgis.core import QgsDataSourceUri

try:
    from qgis.core import Qgis
except ImportError:
    from qgis.core import QGis as Qgis

from db_manager.db_plugins.postgis.connector import PostGisDBConnector
from db_manager.db_plugins.postgis.plugin import PostGisDBPlugin

# ############################################################################
# ########## Globals ###############
# ##################################

qgis_version = int("".join(Qgis.QGIS_VERSION.split(".")[:2]))

qsettings = QSettings()
logger = logging.getLogger("IsogeoQgisPlugin")

connection_parameters_names = ["host", "port", "dbname", "user", "password"]

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

        self.pg_connections = self.build_postgis_dict(qsettings)

    def config_file_parser(self, file_path: Path, connection_service: str):
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
                "name": service_params["dbname"],
                "host": service_params["host"],
                "port": service_params["port"],
                "username": service_params["user"],
                "password": service_params["password"],
                "connection": connection_service,
            }
            return 1, connection_dict

    def build_postgis_dict(self, input_dict):
        """Build the dict that stores informations about PostGIS connections."""
        final_list = []
        for k in sorted(input_dict.allKeys()):
            if k.startswith("PostgreSQL/connections/") and k.endswith("/database"):
                if len(k.split("/")) == 4:
                    connection_name = k.split("/")[2]
                    logger.debug("*=====* {}".format(connection_name))
                    # for traditionnal connections
                    password_saved = input_dict.value(
                        "PostgreSQL/connections/" + connection_name + "/savePassword"
                    )
                    user_saved = input_dict.value(
                        "PostgreSQL/connections/" + connection_name + "/saveUsername"
                    )
                    # for configuration file connections
                    connection_service = input_dict.value(
                        "PostgreSQL/connections/" + connection_name + "/service"
                    )
                    if password_saved == "true" and user_saved == "true":
                        connection_dict = {
                            "name": input_dict.value(
                                "PostgreSQL/connections/"
                                + connection_name
                                + "/database"
                            ),
                            "host": input_dict.value(
                                "PostgreSQL/connections/" + connection_name + "/host"
                            ),
                            "port": input_dict.value(
                                "PostgreSQL/connections/" + connection_name + "/port"
                            ),
                            "username": input_dict.value(
                                "PostgreSQL/connections/"
                                + connection_name
                                + "/username"
                            ),
                            "password": input_dict.value(
                                "PostgreSQL/connections/"
                                + connection_name
                                + "/password"
                            ),
                            "connection": connection_name,
                        }
                        final_list.append(connection_dict)
                    elif connection_service != "" and self.pg_configfile_path:
                        connection_dict = self.config_file_parser(
                            self.pg_configfile_path, connection_service
                        )
                        if connection_dict[0]:
                            final_list.append(connection_dict[1])
                        else:
                            logger.warning(connection_dict[1])

                    else:
                        continue
                else:
                    pass
            else:
                pass
        return final_list

    def establish_pg_connection(self, database_name: str):
        """Set the connectin to a specific PotGIS databse and return the corresponding QgsDataSourceUri and PostGisDBConnector.

        :param str database_name: the name of the database
        """
        conn_params = [
            connection
            for connection in self.pg_connections
            if connection.get("name") == database_name
        ][0]  # TO DO : add the possibility to chosse database connection
        host = conn_params.get("host")
        port = conn_params.get("port")
        user = conn_params.get("username")
        password = conn_params.get("password")
        conn_name = conn_params.get("connection")

        # build the connection URI and set the connection
        uri = QgsDataSourceUri()
        uri.setConnection(host, port, database_name, user, password)
        if qgis_version >= 316:
            pgis_db_plg = PostGisDBPlugin(conn_name)
            c = PostGisDBConnector(uri, pgis_db_plg)
        else:
            c = PostGisDBConnector(uri)

        return uri, c, conn_name
