from qgis.core import(
    QgsProject,
    QgsDataSourceUri,
    QgsRasterLayer
)


layer_uri = "crs='EPSG:2154' format='PNG32' layer='5' url='https://carto.isogeo.net/server/rest/services/isogeo_test/PRIVE/MapServer' authcfg='portal1'"
print(layer_uri)
rlayer = QgsRasterLayer(layer_uri, 'test', 'arcgismapserver')
print(rlayer.isValid())
QgsProject.instance().addMapLayer(rlayer)