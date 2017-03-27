# coding: utf-8
# Minimalist sample. For further, look at the plugin DockableMirrorMap code
from os import path

from PyQt4.QtGui import QDialog
from qgis.core import QgsMapLayerRegistry, QgsVectorLayer
from qgis.gui import QgsMapCanvas, QgsMapCanvasLayer
from qgis.utils import iface

new_dialog = QDialog()
new_dialog.resize(800, 600)

map_canvas = QgsMapCanvas(new_dialog)
map_canvas.setMinimumSize(800, 600)

geojson_contributors = path.join(
                               path.dirname(QgsApplication.developersMapFilePath()),
                                            'contributors.json')

layer = QgsVectorLayer(geojson_contributors, "QGIS Contributors", "ogr")

print(layer.isValid())

QgsMapLayerRegistry.instance().addMapLayer(layer, 0)

map_canvas_layer_list = [QgsMapCanvasLayer(layer)]

map_canvas.setExtent(layer.extent())
map_canvas.setLayerSet(map_canvas_layer_list)

new_dialog.show()

print(dir(map_canvas.map))
