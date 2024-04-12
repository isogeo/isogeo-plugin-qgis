# -*- coding: utf-8 -*-
from qgis.core import (
    QgsDataSourceUri,
    QgsProject,
    QgsApplication,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransformContext,
    QgsWkbTypes,
    QgsProviderRegistry,
    QgsVectorLayer
)
from db_manager.db_plugins.oracle.connector import OracleDBConnector
from db_manager.db_plugins.oracle.plugin import OracleDBPlugin
import os
import sqlite3
from pprint import pprint
import json
from qgis.utils import iface

pprint(QgsProviderRegistry.instance().providerList())

canvas = iface.mapCanvas()

json_env_path = r"C:\Users\SimonSAMPERE\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\isogeo-plugin-qgis\tests\dev\qgis_console\env.json"
with open(json_env_path, "r", encoding="utf-8") as json_file:
    env = json.load(json_file)

uri = QgsDataSourceUri()
host=env.get("ajout_couche_oracleSDE").get("host")
port=env.get("ajout_couche_oracleSDE").get("port")
db_name=env.get("ajout_couche_oracleSDE").get("db_name")
user=env.get("ajout_couche_oracleSDE").get("user")
password=env.get("ajout_couche_oracleSDE").get("password")

uri.setConnection(host, port, db_name, user, password)


c = OracleDBConnector(uri, "Oracle_sys")
oraSDE_sys_tables = "('ANONYMOUS','CTXSYS','DBSNMP','EXFSYS','LBACSYS','MDSYS','MGMT_VIEW','OLAPSYS','OWBSYS','ORDPLUGINS','ORDSYS','SI_INFORMTN_SCHEMA','SYS','SYSMAN','SYSTEM','TSMSYS','WK_TEST','WKPROXY','WMSYS','XDB','APEX_040000','APEX_PUBLIC_USER','DIP','FLOWS_30000','FLOWS_FILES','MDDATA','ORACLE_OCM','XS$NULL','SPATIAL_CSW_ADMIN_USR','SPATIAL_WFS_ADMIN_USR','PUBLIC','OUTLN','WKSYS','APEX_040200', 'SDE')"
oraSDE_geom_column_tab_request = "select col.owner, col.table_name, column_name, data_type from sys.all_tab_cols col join sys.all_tables tab on col.owner = tab.owner and col.table_name = tab.table_name where col.data_type = 'ST_GEOMETRY' and col.owner not in {} order by col.owner, col.table_name, column_id".format(
    oraSDE_sys_tables
)
oraSDE_geom_column_v_request = "select col.owner, col.table_name, column_name, data_type from sys.all_tab_cols col join sys.all_views v on col.owner = v.owner and col.table_name = v.view_name where col.data_type = 'ST_GEOMETRY' and col.owner not in {} order by col.owner, col.table_name, column_id".format(
    oraSDE_sys_tables
)

geom_column_response = c._fetchall(c._execute(None, oraSDE_geom_column_tab_request)) + c._fetchall(c._execute(None, oraSDE_geom_column_v_request))
sde_table_infos = geom_column_response[0]
pprint(sde_table_infos)

oraSDE_table_srid_request = "select SRID from SDE.GEOMETRY_COLUMNS where G_TABLE_NAME = '{}' and G_TABLE_SCHEMA = '{}'".format(sde_table_infos[1], sde_table_infos[0])
table_srid_response = c._fetchall(c._execute(None, oraSDE_table_srid_request))
table_srid = table_srid_response[0][0]
pprint(table_srid)

oraSDE_spatial_ref_request = "select AUTH_SRID from SDE.SPATIAL_REFERENCES where SRID = {}".format(table_srid)
srid_code_response = c._fetchall(c._execute(None, oraSDE_spatial_ref_request))
table_srid_code = str(int(srid_code_response[0][0]))
pprint(table_srid_code)

uri.setDataSource(sde_table_infos[0],sde_table_infos[1], sde_table_infos[2])
#wkbType = QgsWkbTypes().Type(7)
#uri.setWkbType(3)
#uri.setSrid("2154")

layer = QgsVectorLayer(
    path=uri.uri(),
    baseName=sde_table_infos[1],
    providerLib="sde",
)
#print(layer.wkbType())
#layer.setCrs(QgsCoordinateReferenceSystem("EPSG:{}".format(table_srid_code)))
#lyr = QgsProject.instance().addMapLayer(layer)