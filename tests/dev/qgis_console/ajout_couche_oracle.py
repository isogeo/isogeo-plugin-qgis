# -*- coding: utf-8 -*-
from qgis.core import (
    QgsDataSourceUri,
    QgsProject,
    QgsApplication,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransformContext,
    QgsWkbTypes
)
from db_manager.db_plugins.oracle.connector import OracleDBConnector
from db_manager.db_plugins.oracle.plugin import OracleDBPlugin
import os
import sqlite3
from pprint import pprint
import json
from qgis.utils import iface

canvas = iface.mapCanvas()

json_env_path = r"C:\Users\SimonSAMPERE\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\isogeo-plugin-qgis\tests\dev\qgis_console\env.json"
with open(json_env_path, "r", encoding="utf-8") as json_file:
    env = json.load(json_file)

uri = QgsDataSourceUri()
host=env.get("ajout_couche_oracle").get("host")
port=env.get("ajout_couche_oracle").get("port")
db_name=env.get("ajout_couche_oracle").get("db_name")
user=env.get("ajout_couche_oracle").get("user")
password=env.get("ajout_couche_oracle").get("password")

uri.setConnection(host, port, db_name, user, password)

#ora_db_plg = OracleDBPlugin("Oracle_Isogeo_Test_Spatial")
#print(ora_db_plg.connect())
#c = OracleDBConnector(uri, ora_db_plg)

c = OracleDBConnector(uri, "Oracle_Isogeo_Test_Spatial")
#query = u"SELECT count(*) FROM v$option WHERE parameter = 'Spatial' AND value = 'TRUE'"
#query = u"SELECT * FROM ALL_SDO_INDEX_METADATA"
#query = u"select owner as schema_name, view_name from sys.all_views order by owner, view_name"
#query = u"SELECT object_name AS table_name FROM user_objects WHERE object_type = 'TABLE'"
#query = u"SELECT DISTINCT owner FROM all_objects WHERE object_type IN ('TABLE','VIEW','SYNONYM') ORDER BY owner"
#query = u"SELECT DISTINCT owner FROM all_sdo_geom_metadata ORDER BY owner"
#query = u"SELECT table_name FROM user_tables"
#query = u"SELECT SDO_VERSION FROM DUAL"
#query = "select object_name from all_objects where object_type = 'TABLE' and owner = 'ISOGEO_TEST_SPATIAL'"
query = "select col.owner as schema_name, col.table_name, column_name, data_type from sys.all_tab_cols col join sys.all_tables tab on col.owner = tab.owner and col.table_name = tab.table_name where col.data_type = 'SDO_GEOMETRY' and col.owner not in ('ANONYMOUS','CTXSYS','DBSNMP','EXFSYS', 'LBACSYS', 'MDSYS', 'MGMT_VIEW','OLAPSYS','OWBSYS','ORDPLUGINS', 'ORDSYS', 'SI_INFORMTN_SCHEMA','SYS','SYSMAN','SYSTEM', 'TSMSYS','WK_TEST', 'WKPROXY','WMSYS','XDB','APEX_040000', 'APEX_PUBLIC_USER','DIP', 'FLOWS_30000','FLOWS_FILES','MDDATA', 'ORACLE_OCM', 'XS$NULL', 'SPATIAL_CSW_ADMIN_USR', 'SPATIAL_WFS_ADMIN_USR', 'PUBLIC', 'OUTLN', 'WKSYS', 'APEX_040200') order by col.owner, col.table_name, column_id"
#query = "select SRID from user_sdo_geom_metadata where table_name = 'ARRONDISSEMENT_DEPARTEMENTAL'"

ora_table_geomType_request = "select DISTINCT c.GEOM.GET_GTYPE() from ISOGEO_TEST_SPATIAL.HUMANOIDE c"
table_geomType_response = c._fetchall(c._execute(None, ora_table_geomType_request))
pprint([int(elem[0]) for elem in table_geomType_response])
#request = c._execute(None, query)
#result = c._fetchall(request)
#layer_srid = str(int(result[0][0]))
#layer_crs = QgsCoordinateReferenceSystem("EPSG:" + layer_srid)

#map_crs = canvas.mapSettings().destinationCrs()
#
#layerOptions = QgsVectorLayer.LayerOptions()
#layerOptions.fallbackCrs = map_crs
#layerOptions.skipCrsValidation=True

uri.setDataSource("ISOGEO_TEST_SPATIAL","HUMANOIDE", "GEOM")
wkbType = QgsWkbTypes().Type(7)
uri.setWkbType(3)
uri.setSrid("2154")

layer = QgsVectorLayer(
    path=uri.uri(),
    baseName="HUMANOIDE",
    providerLib="oracle",
)
print(layer.wkbType())
layer.setCrs(QgsCoordinateReferenceSystem("EPSG:2154"))
#print(layer.crs())
#
#coordTransCont = QgsCoordinateTransformContext()
#coordTransCont.calculateCoordinateOperation(
#    source=layer_crs,
#    destination=map_crs,
#)
#coordTransCont.addCoordinateOperation(
#    sourceCrs=layer_crs,
#    destinationCrs=map_crs,
#    coordinateOperationProjString=""
#)
#print(coordTransCont.coordinateOperations())
#print(coordTransCont.hasTransform(source=layer_crs,destination=map_crs))
#print(coordTransCont.readSettings())

#layer.setTransformContext(coordTransCont)
#layer.setTransformContext(QgsProject.instance().transformContext())

lyr = QgsProject.instance().addMapLayer(layer)

#query = "select TABLE_NAME from user_sdo_geom_metadata"
#result = c._fetchall(c._execute(None, query))
#pprint(result)

#print(c.getInfo())
#print(c._connectionInfo())
#print(c.hasSpatialSupport())
#print(c._checkGeometryColumnsTable())
#print(c.getSpatialInfo())
#print(c.getSchemas())
#print(c.hasCache())
#print(c.getVectorTables())
#print(c.getSchemaPrivileges("ISOGEO_TEST_SPATIAL"))
#print(c.getVectorTables("ISOGEO_TEST_SPATIAL"))
#print(c.hasCache())

#cache_file_path = os.path.join(QgsApplication.qgisSettingsDirPath(), u"data_sources_cache.db")
#print(os.path.isfile(cache_file_path))
#print(sqlite3.connect(cache_file_path))

#uri.setDataSource("ISOGEO_TEST_SPATIAL","DEPARTEMENT", "GEOM")
#layer = QgsVectorLayer(uri.uri(), "DEPARTEMENT", "oracle")
#lyr = QgsProject.instance().addMapLayer(layer)
#pprint([i.name() for i in layer.dataProvider().fields()])

#lyr = QgsProject.instance().addMapLayer(layer)
#uri.setDataSource("ISOGEO_TEST_SPATIAL","ARRONDISSEMENT_DEPARTEMENTAL", "GEOMETRY")
#layer = QgsVectorLayer(uri.uri(), "ARRONDISSEMENT_DEPARTEMENTAL", "oracle")
#lyr = QgsProject.instance().addMapLayer(layer)

#uri.setWkbType(QGis.WkbPolygon)
# v = QgsVectorLayer(uri.uri(), "MY_LAYER", "oracle")
# QgsMapRegistry.instance().addMapLayer(v, True)