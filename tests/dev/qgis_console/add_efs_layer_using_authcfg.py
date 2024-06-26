from qgis.core import(
    QgsProject,
    QgsDataSourceUri,
    QgsVectorLayer
)


layer_uri = QgsDataSourceUri("authcfg=portal1 crs='EPSG:2154' url='https://carto.isogeo.net/server/rest/services/isogeo_test/PRIVE/FeatureServer/5'")
print(layer_uri)
vlayer = QgsVectorLayer(layer_uri.uri(False), 'test', 'arcgisfeatureserver')
print(vlayer.isValid())
QgsProject.instance().addMapLayer(vlayer)