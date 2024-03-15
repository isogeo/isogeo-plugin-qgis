from qgis.core import Qgis, QgsGeometry, QgsPointXY, QgsFeature, QgsCoordinateReferenceSystem, QgsCoordinateTransform, QgsProject, QgsRenderContext, QgsVectorLayer
from qgis.utils import iface
from qgis.PyQt.QtGui import QColor

geojson_geometry = {"type":"Polygon","coordinates":[[[-179.1435034,51.2750512],[-178.3043662,28.3879122],[-178.3027184,28.3864647],[-173.9599503,26.0553246],[-155.6747556,18.9061171],[109.5612085,18.1693383],[109.5680445,18.1693383],[109.6157333,18.1761742],[109.7011825,18.2040876],[109.7087508,18.2072208],[179.4723413,51.3705508],[179.7750757,51.9554711],[179.7809351,51.9670271],[179.6642359,52.0285098],[179.6369735,52.0353458],[173.1272079,52.9949405],[172.7810979,53.0155297],[-156.4715063,71.4125023],[-159.5196427,70.8357608],[-159.5487768,70.830227],[-161.8881323,70.3539493],[-161.9430639,70.3395857],[-162.3085424,70.2412784],[-166.2226049,68.8858096],[-166.2367651,68.8748233],[-166.8290503,68.3513858],[-171.7393286,63.7912051],[-178.8588761,51.7957217],[-179.1435034,51.2750512]]]}

coords = geojson_geometry.get("coordinates")[0]
li_points = [QgsPointXY(round(i[0], 6), round(i[1], 6))for i in coords]

point_layer = QgsVectorLayer("Point?crs=epsg:4326", "envelope_points", "memory")
for point in li_points:
    point_feature = QgsFeature()
    point_feature.setGeometry(QgsGeometry.fromPointXY(point))
    point_layer.dataProvider().addFeatures([point_feature])

polygon_layer = QgsVectorLayer("Polygon?crs=epsg:4326", "envelope_polygon", "memory")
polygon_feature = QgsFeature()
polygon_feature.setGeometry(QgsGeometry.fromPolygonXY([li_points]))
polygon_layer.dataProvider().addFeatures([polygon_feature])

canvas = iface.mapCanvas()
qgs_prj = QgsProject.instance()

qgs_prj.addMapLayer(polygon_layer)
qgs_prj.addMapLayer(point_layer)

canvas.refresh()
