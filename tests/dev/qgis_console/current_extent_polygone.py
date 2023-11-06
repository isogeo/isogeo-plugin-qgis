from qgis.core import Qgis, QgsGeometry, QgsPointXY, QgsFeature, QgsCoordinateReferenceSystem, QgsCoordinateTransform, QgsProject, QgsRenderContext, QgsVectorLayer
from qgis.utils import iface
from qgis.PyQt.QtGui import QColor

current_crs = iface.mapCanvas().mapSettings().destinationCrs()

current_crs_bound_wgs84 = current_crs.bounds()
wgs84_crs = QgsCoordinateReferenceSystem(4326, QgsCoordinateReferenceSystem.EpsgCrsId)

CRS_converter = QgsCoordinateTransform(current_crs, wgs84_crs, QgsProject.instance())

current_crs_bound = CRS_converter.transformBoundingBox(current_crs_bound_wgs84, Qgis.TransformDirection(1))
currentCRS_rectangle = iface.mapCanvas().extent()

if current_crs_bound.contains(currentCRS_rectangle):
    print("inbound")
    pass
else:
    print("outbound")
    if currentCRS_rectangle.xMinimum() < current_crs_bound.xMinimum():
        currentCRS_rectangle.setXMinimum(current_crs_bound.xMinimum())
    else:
        pass

    if currentCRS_rectangle.yMinimum() < current_crs_bound.yMinimum():
        currentCRS_rectangle.setYMinimum(current_crs_bound.yMinimum())
    else:
        pass

    if currentCRS_rectangle.xMaximum() > current_crs_bound.xMaximum():
        currentCRS_rectangle.setXMaximum(current_crs_bound.xMaximum())
    else:
        pass

    if currentCRS_rectangle.yMaximum() > current_crs_bound.yMaximum():
        currentCRS_rectangle.setYMaximum(current_crs_bound.yMaximum())
    else:
        pass

wgs84_rectangle = CRS_converter.transformBoundingBox(currentCRS_rectangle)

currentCRS_rectangle = iface.mapCanvas().extent()
points_currentCRS = [
    QgsPointXY(currentCRS_rectangle.xMinimum(), currentCRS_rectangle.yMaximum()),
    QgsPointXY(currentCRS_rectangle.xMaximum(), currentCRS_rectangle.yMaximum()),
    QgsPointXY(currentCRS_rectangle.xMaximum(), currentCRS_rectangle.yMinimum()),
    QgsPointXY(currentCRS_rectangle.xMinimum(), currentCRS_rectangle.yMinimum())
]
bbox_geometry_currentCRS = QgsGeometry.fromPolygonXY([points_currentCRS])
bbox_polygon_currentCRS = QgsFeature()
bbox_polygon_currentCRS.setGeometry(bbox_geometry_currentCRS)
bbox_layer_currentCRS = QgsVectorLayer("Polygon?crs={}".format(current_crs.authid().lower()), "BoundingBox_currentCRS", "memory")
bbox_layer_currentCRS.dataProvider().addFeatures([bbox_polygon_currentCRS])

wgs84_xMin = wgs84_rectangle.xMinimum()
wgs84_yMin = wgs84_rectangle.yMinimum()
wgs84_xMax = wgs84_rectangle.xMaximum()
wgs84_yMax = wgs84_rectangle.yMaximum()
points_wgs84 = [
    QgsPointXY(wgs84_xMin, wgs84_yMax),
    QgsPointXY(wgs84_xMax, wgs84_yMax),
    QgsPointXY(wgs84_xMax, wgs84_yMin),
    QgsPointXY(wgs84_xMin, wgs84_yMin)
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
