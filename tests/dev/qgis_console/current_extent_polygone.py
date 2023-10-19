from qgis.core import Qgis, QgsRectangle, QgsGeometry, QgsPointXY, QgsFeature, QgsCoordinateReferenceSystem, QgsCoordinateTransform, QgsProject, QgsRenderContext, QgsRasterLayer, QgsVectorLayer
from qgis.utils import iface
from qgis.PyQt.QtGui import QColor

current_crs = iface.mapCanvas().mapSettings().destinationCrs()
wgs84_crs = QgsCoordinateReferenceSystem(4326, QgsCoordinateReferenceSystem.EpsgCrsId)

CRS_converter = QgsCoordinateTransform(current_crs, wgs84_crs, QgsProject.instance())


currentCRS_rectangle = iface.mapCanvas().extent()
coord_currentCRS = "{},{},{},{}".format(currentCRS_rectangle.xMinimum(), currentCRS_rectangle.yMinimum(), currentCRS_rectangle.xMaximum(), currentCRS_rectangle.yMaximum())

wgs84_rectangle = CRS_converter.transformBoundingBox(currentCRS_rectangle)
coord_wgs84 = "{},{},{},{}".format(wgs84_rectangle.xMinimum(), wgs84_rectangle.yMinimum(), wgs84_rectangle.xMaximum(), wgs84_rectangle.yMaximum())

points_currentCRS = [
    QgsPointXY(currentCRS_rectangle.xMinimum(), currentCRS_rectangle.yMaximum()),
    QgsPointXY(currentCRS_rectangle.xMaximum(), currentCRS_rectangle.yMaximum()),
    QgsPointXY(currentCRS_rectangle.xMaximum(), currentCRS_rectangle.yMinimum()),
    QgsPointXY(currentCRS_rectangle.xMinimum(), currentCRS_rectangle.yMinimum())
]
bbox_geometry_currentCRS = QgsGeometry.fromPolygonXY([points_currentCRS])
bbox_polygon_currentCRS = QgsFeature()
bbox_polygon_currentCRS.setGeometry(bbox_geometry_currentCRS)
bbox_layer_currentCRS = QgsVectorLayer("Polygon?crs=epsg:{}".format(int(str(current_crs.authid()).split(":")[1])), "BoundingBox_currentCRS", "memory")
bbox_layer_currentCRS.dataProvider().addFeatures([bbox_polygon_currentCRS])

points_wgs84 = [
    QgsPointXY(wgs84_rectangle.xMinimum(), wgs84_rectangle.yMaximum()),
    QgsPointXY(wgs84_rectangle.xMaximum(), wgs84_rectangle.yMaximum()),
    QgsPointXY(wgs84_rectangle.xMaximum(), wgs84_rectangle.yMinimum()),
    QgsPointXY(wgs84_rectangle.xMinimum(), wgs84_rectangle.yMinimum())
]
bbox_geometry_wgs84 = QgsGeometry.fromPolygonXY([points_wgs84])
bbox_polygon_wgs84 = QgsFeature()
bbox_polygon_wgs84.setGeometry(bbox_geometry_wgs84)
bbox_layer_wgs84 = QgsVectorLayer("Polygon?crs=epsg:{}".format(int(str(wgs84_crs.authid()).split(":")[1])), "BoundingBox_wgs84", "memory")
bbox_layer_wgs84.dataProvider().addFeatures([bbox_polygon_wgs84])

canvas = iface.mapCanvas()
qgs_prj = QgsProject.instance()

canvas.mapSettings().setDestinationCrs(current_crs)
symbols = bbox_layer_currentCRS.renderer().symbols(QgsRenderContext())
symbol = symbols[0]
symbol.setColor(QColor.fromRgb(255, 20, 147))
symbol.setOpacity(0.25)
qgs_prj.addMapLayer(bbox_layer_currentCRS)

canvas.mapSettings().setDestinationCrs(wgs84_crs)
symbols = bbox_layer_wgs84.renderer().symbols(QgsRenderContext())
symbol = symbols[0]
symbol.setColor(QColor.fromRgb(255, 20, 147))
symbol.setOpacity(0.25)
qgs_prj.addMapLayer(bbox_layer_wgs84)
