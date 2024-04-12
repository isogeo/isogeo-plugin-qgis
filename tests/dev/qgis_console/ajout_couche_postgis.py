# -*- coding: utf-8 -*-
from qgis.core import QgsDataSourceUri, QgsProject
from db_manager.db_plugins.postgis.connector import PostGisDBConnector
from db_manager.db_plugins.postgis.plugin import PostGisDBPlugin
from pprint import pprint
import json

json_env_path = r"C:\Users\SimonSAMPERE\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\isogeo-plugin-qgis\tests\dev\qgis_console\env.json"
with open(json_env_path, "r", encoding="utf-8") as json_file:
    env = json.load(json_file)

uri = QgsDataSourceUri()
host=env.get("ajout_couche_postgis").get("host")
port=env.get("ajout_couche_postgis").get("port")
db_name=env.get("ajout_couche_postgis").get("db_name")
user=env.get("ajout_couche_postgis").get("user")
password=env.get("ajout_couche_postgis").get("password")

uri.setConnection(aHost=host, aPort=port, aDatabase=db_name, aUsername=user, aPassword=password)

pgis_db_plg = PostGisDBPlugin("AlwaysData_isogeoReader")
c = PostGisDBConnector(uri, pgis_db_plg)

#tables = c.getTables("test")
#pprint(tables)
#pprint(c.getTablePrivileges("test.ADMIN_EXPRESS_COMMUNE"))
#pprint(c.getTablePrivileges("ign.ADMIN_EXPRESS_EPCI"))
#view = tables[5]
#pprint(c.core_connection.tables())
#uri.setDataSource(view[2], view[1], view[8])
#layer = QgsVectorLayer(uri.uri(), "DPTS_NVLL_AQUITAINE", "postgres")
#field_names = [i.name() for i in layer.dataProvider().fields()]
#sorted_field_names = field_names.sort(key=lambda x: ("id" not in x, x))
#pprint(field_names)
#pprint(sorted_field_names)
#lyr = QgsProject.instance().addMapLayer(layer)
