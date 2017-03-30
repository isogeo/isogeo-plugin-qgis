# coding: utf-8
# Minimalist sample. For further, look at the plugin DockableMirrorMap code
from os import path

from PyQt4.QtGui import QDialog
from qgis.core import QgsMapLayerRegistry, QgsVectorLayer, QgsCoordinateReferenceSystem, QgsRasterLayer
from qgis.gui import QgsMapCanvas, QgsMapCanvasLayer
from qgis.utils import iface

new_dialog = QDialog()
new_dialog.resize(800, 600)

# SRS
crs_wgs84 = QgsCoordinateReferenceSystem(4326)

# raster layer
world_wmts_url = "contextualWMSLegend=0&crs=EPSG:4326&dpiMode=7&"\
                 "featureCount=10&format=image/jpeg&layers=opengeo:countries&"\
                 "styles=&tileMatrixSet=EPSG:4326&"\
                 "url=http://suite.opengeo.org/geoserver/gwc/service/wmts?request%3DGetCapabilities"
world_lyr = QgsRasterLayer(world_wmts_url, "Countries", 'wms')
print(world_lyr.isValid())

# vector layer
geojson_contributors = path.join(
                               path.dirname(QgsApplication.developersMapFilePath()),
                                            'contributors.json')

layer = QgsVectorLayer(geojson_contributors, "QGIS Contributors", "ogr")
layer.setLayerTransparency(35)
print(layer.isValid())

# managing map canvas
map_canvas = QgsMapCanvas(new_dialog)
map_canvas.setMinimumSize(800, 600)
map_canvas.mapRenderer().setDestinationCrs(crs_wgs84)
QgsMapLayerRegistry.instance().addMapLayers([layer, world_lyr], 0)
map_canvas_layer_list = [QgsMapCanvasLayer(layer), QgsMapCanvasLayer(world_lyr)]
map_canvas.setExtent(layer.extent())
map_canvas.setLayerSet(map_canvas_layer_list)

new_dialog.show()

print(dir(map_canvas.map))
print(map_canvas.layers())
