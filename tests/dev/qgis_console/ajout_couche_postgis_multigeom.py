# -*- coding: utf-8 -*-
from qgis.core import QgsDataSourceUri, QgsProject, QgsVectorLayer, QgsCoordinateReferenceSystem
from db_manager.db_plugins.postgis.connector import PostGisDBConnector
from db_manager.db_plugins.postgis.plugin import PostGisDBPlugin
from pprint import pprint
import json

json_env_path = r"C:\Users\SimonSAMPERE\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\isogeo-plugin-qgis\tests\dev\qgis_console\env.json"
with open(json_env_path, "r", encoding="utf-8") as json_file:
    env = json.load(json_file)

uri = QgsDataSourceUri()
host=env.get("ajout_couche_postgis_multigeom").get("host")
port=env.get("ajout_couche_postgis_multigeom").get("port")
db_name=env.get("ajout_couche_postgis_multigeom").get("db_name")
user=env.get("ajout_couche_postgis_multigeom").get("user")
password=env.get("ajout_couche_postgis_multigeom").get("password")
table_name = "multilines_2154_specchar_attributes"
table_name = "multigeom_2154"

uri.setConnection(aHost=host, aPort=port, aDatabase=db_name, aUsername=user, aPassword=password)

pgis_db_plg = PostGisDBPlugin("isogeo_test")
c = PostGisDBConnector(uri, pgis_db_plg)

for tab in c.getTables():
    if tab[2] == "sample" and tab[1] == table_name:
        print(tab)

uri.setWkbType(3)
uri.setDataSource("sample", table_name, "geom","","gid")
vlayer = QgsVectorLayer(uri.uri(), table_name, 'postgres')
uri.setSrid("2154")
vlayer.setCrs(QgsCoordinateReferenceSystem('EPSG:2154'))

print(vlayer.wkbType())
QgsProject.instance().addMapLayer(vlayer)

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
