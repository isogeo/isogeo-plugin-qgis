from qgis.core import QgsProject, QgsRasterLayer
from qgis.utils import iface

qgs_prj = QgsProject.instance()

for layer in qgs_prj.mapLayers().values():
    if not isinstance(layer, QgsRasterLayer):
       qgs_prj.removeMapLayer(layer)

#print(iface.mapCanvas().extent())