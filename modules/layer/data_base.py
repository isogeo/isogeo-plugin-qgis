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

# Plugin modules

# ############################################################################
# ########## Globals ###############
# ##################################

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
