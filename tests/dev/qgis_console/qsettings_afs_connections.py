from qgis.PyQt.QtCore import QSettings
from pprint import pprint

qsettings = QSettings()

li_involved_keys = [key for key in qsettings.allKeys() if "arcgisfeatureserver/items" in key and ("url" in key or "authcfg" in key)]

afs_connections = {}
for key in li_involved_keys:
    afs_name = key.split("/")[-2]
    
    if afs_name not in afs_connections:
        afs_connections[afs_name] = {}
    else:
        pass

    if "url" in key:
        afs_connections[afs_name]["url"] = qsettings.value(key)
    elif "authcfg" in key:
        afs_connections[afs_name]["authcfg"] = qsettings.value(key)
    else:
        pass
    

pprint(afs_connections)