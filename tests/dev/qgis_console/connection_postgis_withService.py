# -*- coding: utf-8 -*-
from qgis.core import QgsDataSourceUri, QgsProject, QgsVectorLayer
from db_manager.db_plugins.postgis.connector import PostGisDBConnector
from db_manager.db_plugins.postgis.plugin import PostGisDBPlugin
from pprint import pprint
import json

json_env_path = r"C:\Users\SimonSAMPERE\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\isogeo-plugin-qgis\tests\dev\qgis_console\env.json"
with open(json_env_path, "r", encoding="utf-8") as json_file:
    env = json.load(json_file)

uri = QgsDataSourceUri()

host=env.get("connection_postgis_withService").get("host")
port=env.get("connection_postgis_withService").get("port")
db_name=env.get("connection_postgis_withService").get("db_name")
user=env.get("connection_postgis_withService").get("user")
password=env.get("connection_postgis_withService").get("password")
service = "isogeo_test@margarita"

#uri.setConnection(aHost=host, aPort=port, aDatabase=base_name, aUsername=user, aPassword=password)
uri.setConnection(aService=service, aDatabase=db_name, aUsername=user, aPassword=password)
uri.setParam("username", "")

pgis_db_plg = PostGisDBPlugin(service)
c = PostGisDBConnector(uri, pgis_db_plg)

tables = c.getTables("test")
pprint(tables)
#pprint(c.getTablePrivileges("test.ADMIN_EXPRESS_COMMUNE"))
#pprint(c.getTablePrivileges("ign.ADMIN_EXPRESS_EPCI"))
#view = tables[5]
#pprint(c.core_connection.tables())
#uri.setKeyColumn("geom")

uri.setDataSource("test", "DEPARTEMENT", "geom")
layer = QgsVectorLayer(uri.uri(), "DEPARTEMENT_script", "postgres")
#field_names = [i.name() for i in layer.dataProvider().fields()]
#sorted_field_names = field_names.sort(key=lambda x: ("id" not in x, x))
#pprint(field_names)
#pprint(sorted_field_names)
lyr = QgsProject.instance().addMapLayer(layer)
