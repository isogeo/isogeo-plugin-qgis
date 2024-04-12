from qgis.core import QgsDataSourceUri, QgsProject, QgsApplication
from qgis.PyQt.QtSql import QSqlDatabase
import json
json_env_path = r"C:\Users\SimonSAMPERE\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\isogeo-plugin-qgis\tests\dev\qgis_console\env.json"
with open(json_env_path, "r", encoding="utf-8") as json_file:
    env = json.load(json_file)

uri = QgsDataSourceUri()
host=env.get("ajout_couche_oracle").get("host")
port=env.get("ajout_couche_oracle").get("port")
user=env.get("ajout_couche_oracle").get("user")
password=env.get("ajout_couche_oracle").get("password")

db_name = "{}/{}@{}:{}/{}".format(user, password, host, port, "isoora")

uri.setConnection(host, port, db_name, user, password)

sqlDriver = "QOCISPATIAL"
#sqlDriver = "QOCI"
#print(QSqlDatabase.isDriverAvailable(sqlDriver))

db = QSqlDatabase.addDatabase(sqlDriver, "Oracle_Isogeo_Test_Spatial")
db.setDatabaseName(db_name)
db.setUserName(user)
db.setPassword(password)
db.setHostName(host)
db.setPort(int(port))
db.setConnectOptions("OCI_ATTR_PREFETCH_ROWS")

print(db.isValid())
print(db.open())
print(db.lastError().databaseText())