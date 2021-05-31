# -*- coding: utf-8 -*-
#! python3  # noqa: E265

# Standard library
import logging
from configparser import ConfigParser
from pathlib import Path
from os import environ

# PyQT
from qgis.PyQt.QtCore import QSettings, Qt
from qgis.PyQt.QtGui import QIcon, QCursor
from qgis.PyQt.QtWidgets import (
    QComboBox,
    QLabel,
    QAbstractButton,
)

# PyQGIS
from qgis.core import QgsDataSourceUri

try:
    from qgis.core import Qgis
except ImportError:
    from qgis.core import QGis as Qgis

from db_manager.db_plugins.postgis.connector import PostGisDBConnector
from db_manager.db_plugins.postgis.plugin import PostGisDBPlugin

from db_manager.db_plugins.oracle.connector import OracleDBConnector
from db_manager.db_plugins.oracle.plugin import OracleDBPlugin

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
ico_ora = QIcon(":/images/themes/default/mIconOracle.svg")

dbms_specifics_resources = {
    "Oracle": {
        "invalid_key": "isogeo/settings/invalid_ora_conn",
        "prefered_key": "isogeo/settings/prefered_ora_conn",
        "label": "Oracle",
        "windowIcon": ico_ora
    },
    "PostgreSQL": {
        "invalid_key": "isogeo/settings/invalid_pgdb_conn",
        "prefered_key": "isogeo/settings/prefered_pgdb_conn",
        "label": "PostGIS",
        "windowIcon": ico_pgis
    }
}

btnBox_ico_dict = {
    0: QIcon(":/plugins/Isogeo/resources/save.svg"),
    1: QIcon(":/images/themes/default/mActionRemove.svg"),
    7: QIcon(":/plugins/Isogeo/resources/undo.svg"),
}

# https://dataedo.com/kb/query/oracle/find-all-spatial-columns
ora_sys_tables = "('ANONYMOUS','CTXSYS','DBSNMP','EXFSYS','LBACSYS','MDSYS','MGMT_VIEW','OLAPSYS','OWBSYS','ORDPLUGINS','ORDSYS','SI_INFORMTN_SCHEMA','SYS','SYSMAN','SYSTEM','TSMSYS','WK_TEST','WKPROXY','WMSYS','XDB','APEX_040000','APEX_PUBLIC_USER','DIP','FLOWS_30000','FLOWS_FILES','MDDATA','ORACLE_OCM','XS$NULL','SPATIAL_CSW_ADMIN_USR','SPATIAL_WFS_ADMIN_USR','PUBLIC','OUTLN','WKSYS','APEX_040200')"
ora_geom_column_request = "select col.owner, col.table_name, column_name, data_type from sys.all_tab_cols col join sys.all_tables tab on col.owner = tab.owner and col.table_name = tab.table_name where col.data_type = 'SDO_GEOMETRY' and col.owner not in {} order by col.owner, col.table_name, column_id".format(ora_sys_tables)

arrow_cursor = QCursor(Qt.CursorShape(0))
hourglass_cursor = QCursor(Qt.CursorShape(3))

# ############################################################################
# ########## Classes ###############
# ##################################


class DataBaseManager:
    """Basic class that holds methods used to facilitate data base connections for layer
     adding."""

    # def __init__(self, cache_manager: object):
    def __init__(self, tr):
        """Class constructor."""

        self.tr = tr

        # Check PGSERVICEFILE env var value if it exists
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

        self.dbms_specifics_infos = {
            "Oracle": {
                "prefered_connections": [],
                "invalid_connections": [],
                "connections": [],
                "db_names": []
            },
            "PostgreSQL": {
                "prefered_connections": [],
                "invalid_connections": [],
                "connections": [],
                "db_names": []
            }
        }

        # Retrieved prefered connections saved into QSettings
        self.fetch_qsettings_connections(dbms="PostgreSQL", connections_kind="prefered")
        self.fetch_qsettings_connections(dbms="Oracle", connections_kind="prefered")

        # Retrieved invalid connections saved into QSettings
        self.fetch_qsettings_connections(dbms="PostgreSQL", connections_kind="invalid")
        self.fetch_qsettings_connections(dbms="Oracle", connections_kind="invalid")

        # retrieve informations about registered database connections from QSettings
        self.build_connection_dict(dbms="PostgreSQL")
        self.build_connection_dict(dbms="Oracle")

        # set UI module
        self.pgdb_config_dialog = Isogeodb_connections()

        for btn in self.pgdb_config_dialog.btnbox.buttons():
            btn_role = self.pgdb_config_dialog.btnbox.buttonRole(btn)
            icon = btnBox_ico_dict.get(btn_role)
            btn.setIcon(icon)

        self.pgdb_config_dialog.btn_reload_conn.clicked.connect(
            self.pgdb_conn_reload_slot
        )

        self.pgdb_config_dialog.btnbox.clicked.connect(self.pgdb_config_dialog_slot)

        self.tbl = self.pgdb_config_dialog.tbl

    def set_qsettings_connections(self, dbms: str, connections_kind: str, li_connections: list):
        """ Save the list of invalid connections in QSettings
        """

        if not isinstance(li_connections, list):
            raise TypeError("'li_connections' argument value should be a list, not : {}".format(type(li_connections)))
        elif not isinstance(dbms, str):
            raise TypeError("'dbms' argument value should be a str, not : {}".format(type(dbms)))
        elif dbms not in ["PostgreSQL", "Oracle"]:
            raise ValueError("'dbms' argument value should be 'PostgreSQL' or 'Oracle', not : {}".format(dbms))
        elif not isinstance(connections_kind, str):
            raise TypeError("'connections_kind' argument value should be a str, not : {}".format(type(connections_kind)))
        elif connections_kind not in ["invalid", "prefered"]:
            raise ValueError("'connections_kind' argument value should be 'invalid' or 'prefered', not : {}".format(connections_kind))
        else:
            qsettings_key = dbms_specifics_resources.get(dbms).get("{}_key".format(connections_kind))

        qsettings.setValue(
            qsettings_key, li_connections
        )

    def fetch_qsettings_connections(self, dbms: str, connections_kind: str):
        """ Retrieve the list of invalid or prefered (depending on connections_kind) connections saved in QSettings
        """

        if not isinstance(dbms, str):
            raise TypeError("'dbms' argument value should be str, not : {}".format(type(dbms)))
        elif dbms not in ["PostgreSQL", "Oracle"]:
            raise ValueError("'dbms' argument value should be 'PostgreSQL' or 'Oracle', not : {}".format(dbms))
        elif not isinstance(connections_kind, str):
            raise TypeError("'connections_kind' argument value should be a str, not : {}".format(type(connections_kind)))
        elif connections_kind not in ["invalid", "prefered"]:
            raise ValueError("'connections_kind' argument value should be 'invalid' or 'prefered', not : {}".format(connections_kind))
        else:
            qsettings_key = dbms_specifics_resources.get(dbms).get("{}_key".format(connections_kind))

        if qsettings.value(qsettings_key):
            self.dbms_specifics_infos[dbms]["invalid_connections"] = qsettings.value(
                qsettings_key
            )
            logger.info(
                "{} connections_kind {} connection retrieved from QSettings.".format(
                    len(self.dbms_specifics_infos.get(dbms).get("invalid_connections")), dbms
                )
            )
        else:
            self.dbms_specifics_infos[dbms]["invalid_connections"] = []
            self.set_qsettings_connections(dbms, connections_kind, [])

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
                "service": connection_service,
                "database": service_params["dbname"],
                "host": service_params["host"],
                "port": service_params["port"],
                "username": service_params["user"],
                "password": service_params["password"],
                "connection": connection_name,
            }
            return 1, connection_dict

    def qsettings_content_parser(self, dbms: str, connection_name: str):
        """ Retrieve connection parameters values stored into QSettings corresponding to specific
        dbms and connection.
        """

        conn_prefix = "{}/connections/{}".format(dbms, connection_name)

        database = qsettings.value(conn_prefix + "/database")
        host = qsettings.value(conn_prefix + "/host")
        port = qsettings.value(conn_prefix + "/port")
        username = qsettings.value(conn_prefix + "/username")
        password = qsettings.value(conn_prefix + "/password")

        connection_dict = {
            "service": "",
            "database": database,
            "host": host,
            "port": port,
            "username": username,
            "password": password,
            "connection": connection_name,
        }
        return 1, connection_dict

    def check_connection_params_type(
        self,
        service: str = "",
        host: str = "",
        port: str = "",
        username: str = "",
        password: str = "",
        database: str = "",
        connection: str = "",
    ):
        """Check connection parameters given as arguments to methods :
            * establish_oracle_connection
            * establish_postgis_connection
        """

        error_msg = ""
        if not isinstance(host, str):
            error_msg = "'host' argument value should be str, not : {}".format(type(host))
        elif not isinstance(service, str):
            error_msg = "'service' argument value should be str, not : {}".format(type(service))
        elif not isinstance(port, str):
            error_msg = "'port' argument value should be str, not : {}".format(type(port))
        elif not isinstance(username, str):
            error_msg = "'username' argument value should be str, not : {}".format(type(username))
        elif not isinstance(password, str):
            error_msg = "'password' argument value should be str, not : {}".format(type(password))
        elif not isinstance(database, str):
            error_msg = "'database' argument value should be str, not : {}".format(type(database))
        elif not isinstance(connection, str):
            error_msg = "'connection' argument value should be str, not : {}".format(type(connection))
        else:
            return 1

        return error_msg

    def build_connection_uri(
        self,
        service: str = "",
        host: str = "",
        port: str = "",
        username: str = "",
        password: str = "",
        database: str = ""
    ):
        """Build connection URI used by methods :
            * establish_oracle_connection
            * establish_postgis_connection
        """

        uri = QgsDataSourceUri()
        if service == "":
            logger.debug("*=====* tradi connection")
            uri.setConnection(aHost=host, aPort=port, aDatabase=database, aUsername=username, aPassword=password)
        else:
            logger.debug("*=====* service connection")
            uri.setConnection(aService=service, aDatabase=database, aUsername=username, aPassword=password)

        return uri

    def establish_postgis_connection(
        self,
        service: str = "",
        host: str = "",
        port: str = "",
        username: str = "",
        password: str = "",
        database: str = "",
        connection: str = "",
    ):
        """Set the connection to a specific PostGIS database and return the corresponding QgsDataSourceUri and tables infos.
        """
        check_params = self.check_connection_params_type(service, host, port, username, password, database, connection)
        if check_params == 1:
            pass
        else:
            raise TypeError(check_params)

        # build the connection URI and set the connection
        uri = self.build_connection_uri(service, host, port, username, password, database)

        try:
            if qgis_version >= 316:
                pgis_db_plg = PostGisDBPlugin(connection)
                c = PostGisDBConnector(uri, pgis_db_plg)
            else:
                c = PostGisDBConnector(uri)
        except Exception as e:
            logger.warning(
                "Faile to establish connection to {} PostGIS database using those informations : service:{}, host:{}, port:{}, username:{}, password:{}".format(
                    database, service, host, port, username, password
                )
            )
            logger.error(str(e))
            return 0

        li_table_infos = [infos for infos in c.getTables() if infos[0] == 1]

        return uri, li_table_infos

    def establish_oracle_connection(
        self,
        service: str = "",
        host: str = "",
        port: str = "",
        username: str = "",
        password: str = "",
        database: str = "",
        connection: str = "",
    ):
        """Set the connection to a specific Oracle database and return the corresponding QgsDataSourceUri and tables infos.
        """

        check_params = self.check_connection_params_type(service, host, port, username, password, database, connection)
        if check_params == 1:
            pass
        else:
            raise TypeError(check_params)

        # build the connection URI and set the connection
        uri = self.build_connection_uri(service, host, port, username, password, database)

        try:
            if qgis_version >= 316:
                ora_db_plg = connection
                c = OracleDBConnector(uri, ora_db_plg)
            else:
                c = OracleDBConnector(uri)
        except Exception as e:
            logger.warning(
                "Faile to establish connection to {} Oracle database using those informations : service:{}, host:{}, port:{}, username:{}, password:{}".format(
                    database, service, host, port, username, password
                )
            )
            logger.error(str(e))
            return 0

        li_table_infos = c._fetchall(c._execute(None, ora_geom_column_request))

        return uri, li_table_infos

    def build_connection_dict(self, dbms: str, skip_invalid: bool = True):
        """Build the dict that stores informations about PostgreSQL or Oracle connections."""

        if not isinstance(dbms, str):
            raise TypeError("'dbms' argument value should be str, not : {}".format(type(dbms)))
        elif dbms not in ["PostgreSQL", "Oracle"]:
            raise ValueError("'dbms' argument value should be 'PostgreSQL' or 'Oracle', not : {}".format(dbms))
        else:
            dbms_prefix = "{}/connections/".format(dbms)
            if dbms == "PostgreSQL":
                establish_conn_func = self.establish_postgis_connection
            else:
                establish_conn_func = self.establish_oracle_connection

        li_connections = []
        li_db_names = []
        for k in sorted(qsettings.allKeys()):
            if k.startswith(dbms_prefix) and k.endswith("/database"):
                if len(k.split("/")) == 4:
                    connection_name = k.split("/")[2]

                    password_saved = qsettings.value(
                        dbms_prefix + connection_name + "/savePassword"
                    )
                    user_saved = qsettings.value(
                        dbms_prefix + connection_name + "/saveUsername"
                    )
                    connection_service = qsettings.value(
                        dbms_prefix + connection_name + "/service"
                    )

                    # For "traditionnaly" registered connections
                    if password_saved == "true" and user_saved == "true":
                        connection_dict = self.qsettings_content_parser(dbms=dbms, connection_name=connection_name)
                        if connection_dict[0]:
                            connection_dict = connection_dict[1]
                        else:
                            logger.warning(connection_dict[1])

                    # For connections configured using config file and service
                    # elif connection_service != "" and self.pg_configfile_path:
                    elif connection_service != "":
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

                    if connection_name in self.dbms_specifics_infos.get(dbms).get("invalid_connections") and skip_invalid:
                        pass
                    else:
                        conn = establish_conn_func(**connection_dict)
                        if not conn:
                            connection_dict["uri"] = 0
                            connection_dict["tables"] = 0
                            self.dbms_specifics_infos[dbms]["invalid_connections"].append(connection_name)
                            logger.info(
                                "'{}' connection saved as invalid".format(
                                    connection_name
                                )
                            )
                            continue
                        else:
                            connection_dict["uri"] = conn[0]
                            connection_dict["tables"] = conn[1]

                        if connection_dict.get("connection") in self.dbms_specifics_infos.get(dbms).get("prefered_connections"):
                            connection_dict["prefered"] = 1
                        else:
                            connection_dict["prefered"] = 0

                        li_connections.append(connection_dict)

                        if connection_dict.get("database") not in li_db_names:
                            li_db_names.append(connection_dict.get("database"))
                        else:
                            pass
                else:
                    pass
            else:
                pass

        self.dbms_specifics_infos[dbms]["connections"] = li_connections
        self.dbms_specifics_infos[dbms]["db_names"] = li_db_names

        self.set_qsettings_connections(dbms, "invalid", self.dbms_specifics_infos.get(dbms).get("invalid_connections"))

    def switch_widgets_on_and_off(self, mode: bool = 1):
        """1 to switch widgets on and 0 to switch widgets off"""

        if mode:
            self.pgdb_config_dialog.setCursor(arrow_cursor)
        else:
            self.pgdb_config_dialog.setCursor(hourglass_cursor)

        self.pgdb_config_dialog.setEnabled(mode)
        self.pgdb_config_dialog.btnbox.setEnabled(mode)
        self.pgdb_config_dialog.btn_reload_conn.setEnabled(mode)
        self.tbl.setEnabled(mode)

    def fill_pgdb_config_tbl(self, dbms):
        """Fill the dialog table from informations about PostGIS database embed connection"""

        if not isinstance(dbms, str):
            raise TypeError("'dbms' argument value should be str, not : {}".format(type(dbms)))
        elif dbms not in ["PostgreSQL", "Oracle"]:
            raise ValueError("'dbms' argument value should be 'PostgreSQL' or 'Oracle', not : {}".format(dbms))
        else:
            pass

        self.switch_widgets_on_and_off(0)

        # Clean and initiate the tab
        self.tbl.clear()
        li_header_labels = [self.tr("Database"), self.tr("Connection")]
        self.tbl.setHorizontalHeaderLabels(li_header_labels)
        self.tbl.setRowCount(0)

        # Fill the tab
        row_index = 0
        for dbname in self.dbms_specifics_infos.get(dbms).get("db_names"):
            li_pgdb_conn = [
                conn for conn in self.dbms_specifics_infos.get(dbms).get("connections") if conn.get("database") == dbname
            ]
            # Add a line to the tab only if there is several connections
            if len(li_pgdb_conn) > 1:
                self.tbl.insertRow(row_index)
                # COLUMN 1 - database name
                dbname_item = QLabel()
                dbname_item.setText(dbname)
                dbname_item.setMargin(5)
                self.tbl.setCellWidget(row_index, 0, dbname_item)

                # COLUMN 2 - connections ComboBox
                cbb_conn = QComboBox()
                cbb_conn.addItem(" - ", 0)
                # fill combobox
                sorted(li_pgdb_conn, key=lambda i: i["database"])
                current_index = 0
                index = 1
                for connection in li_pgdb_conn:
                    cbb_conn.addItem(connection.get("connection"), 1)
                    if connection.get("prefered"):
                        current_index = index
                    else:
                        pass
                    index += 1
                cbb_conn.setCurrentIndex(current_index)
                self.tbl.setCellWidget(row_index, 1, cbb_conn)
                row_index += 1
            else:
                # self.tbl.removeRow(row_index)
                pass

        hheader = self.tbl.horizontalHeader()
        vheader = self.tbl.verticalHeader()
        hheader.setSectionResizeMode(1)
        vheader.setMinimumSectionSize(10)

        self.switch_widgets_on_and_off(1)

    def open_db_config_dialog(self, dbms: str):
        """Build the dialog table from informations about PostGIS database embed connection, then
        display the dialog window to the user"""

        if not isinstance(dbms, str):
            raise TypeError("'dbms' argument value should be str, not : {}".format(type(dbms)))
        elif dbms not in ["PostgreSQL", "Oracle"]:
            raise ValueError("'dbms' argument value should be 'PostgreSQL' or 'Oracle', not : {}".format(dbms))
        else:
            label = dbms_specifics_resources.get(dbms).get("label")
            windowIcon = dbms_specifics_resources.get(dbms).get("windowIcon")

        self.pgdb_config_dialog.setWindowIcon(windowIcon)
        self.pgdb_config_dialog.setWindowTitle(self.tr("{} database configuration".format(label)))
        self.pgdb_config_dialog.label.setText(self.tr("Choose the embed connection to be used to access to each {} database".format(label)))
        self.fill_pgdb_config_tbl(dbms)
        self.pgdb_config_dialog.setWindowOpacity(1)
        self.pgdb_config_dialog.exec()

    def pgdb_config_dialog_slot(self, btn: QAbstractButton):
        """Called when one of the 3 dialog button box is clicked to execute appropriate operations."""

        if "Oracle" in self.pgdb_config_dialog.windowTitle():
            dbms = "Oracle"
        else:
            dbms = "PostgreSQL"

        btn_role = self.pgdb_config_dialog.btnbox.buttonRole(btn)

        # If "Save" button was clicked
        if btn_role == 0:
            row_count = self.tbl.rowCount()
            li_connection_name = []
            # Retrieve the option selected in each combobxs
            for i in range(0, row_count):
                cbbox = self.tbl.cellWidget(i, 1)
                current_userData = cbbox.itemData(cbbox.currentIndex())
                if current_userData:
                    li_connection_name.append(cbbox.currentText())
                else:
                    pass
            # If options have been selected, store user preferences
            self.dbms_specifics_infos[dbms]["prefered_connections"] = li_connection_name
            self.build_connection_dict(dbms=dbms)
            self.set_qsettings_connections(dbms, "prefered", li_connection_name)
        # If "Cancel" button was clicked
        elif btn_role == 1:
            pass
        # If "Reset" button was clicked
        elif btn_role == 7:
            self.fill_pgdb_config_tbl(dbms)
        else:
            logger.warning(
                "Unexpected buttonRole : {} (https://doc.qt.io/qt-5/qdialogbuttonbox.html#ButtonRole-enum)".format(
                    btn_role
                )
            )

    def pgdb_conn_reload_slot(self):
        """Called when 'Reload embed connection(s)' is clicked to execute appropriate operations."""

        if "Oracle" in self.pgdb_config_dialog.windowTitle():
            dbms = "Oracle"
        else:
            dbms = "PostgreSQL"

        self.dbms_specifics_infos[dbms]["invalid_connections"] = []
        self.build_connection_dict(dbms=dbms, skip_invalid=False)
        self.fill_pgdb_config_tbl(dbms)
        return
