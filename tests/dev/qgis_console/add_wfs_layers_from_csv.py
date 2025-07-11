import re
from pathlib import Path
from qgis.core import QgsProject, QgsVectorLayer, QgsRasterLayer
import json
import os
import shutil

geoJSONPath = r'C:\Users\JulieGROSMAIRE\Documents\recette'

# Liste des couches à ajouter : (URL du service WFS, identifiant de la couche)
wfs_layers =  [
    (
         "https://carto.isogeo.net/geoserver/apigdp-258/wfs",
        "apigdp-258:carte-des-pharmacies-de-paris",
        "carte-des-pharmacies-de-paris",
        "Point",
        987,
        [
            [
                2.2582987,
                48.819679685000004
            ],
            [
                2.41114497,
                48.819679685000004
            ],
            [
                2.41114497,
                48.8188675
            ],
            [
                2.2582987,
                48.8188675
            ],
            [
                2.2582987,
                48.819679685000004
            ]
        ],
        [
            [
                2.2582987,
                48.900086
            ],
            [
                2.2598271627,
                48.900086
            ],
            [
                2.2598271627,
                48.8188675
            ],
            [
                2.2582987,
                48.8188675
            ],
            [
                2.2582987,
                48.900086
            ]
        ],
        [
            [
                2.3421594238977708,
                48.86613355082183
            ],
            [
                2.3424569274536817,
                48.86887432927019
            ],
            [
                2.3442419487891457,
                48.86897221144014
            ],
            [
                2.347216984348255,
                48.867993381129764
            ],
            [
                2.3492995092396307,
                48.86711241748962
            ],
            [
                2.349745764573498,
                48.86662298654768
            ],
            [
                2.3509357787971408,
                48.864958885561485
            ],
            [
                2.351382034131008,
                48.86309894254451
            ],
            [
                2.349150757461676,
                48.860259948964234
            ],
            [
                2.3464732254584777,
                48.85947675
            ],
            [
                2.3439444452332356,
                48.85957465054029
            ],
            [
                2.3415644167859497,
                48.860749442097614
            ],
            [
                2.3415644167859497,
                48.86104313568133
            ],
            [
                2.34379569345528,
                48.861924206098976
            ],
            [
                2.3452832112348347,
                48.862217892793716
            ],
            [
                2.3467707290143887,
                48.86251157776621
            ],
            [
                2.3467707290143887,
                48.86251157776621
            ],
            [
                2.3458782183466567,
                48.863392622350304
            ],
            [
                2.3436469416773247,
                48.86319683600447
            ],
            [
                2.3421594238977708,
                48.86270736679107
            ],
            [
                2.341266913230038,
                48.862315787975895
            ],
            [
                2.3388868847827506,
                48.86182631015135
            ],
            [
                2.3379943741150186,
                48.86182631015135
            ],
            [
                2.3376968705591077,
                48.8634905152362
            ],
            [
                2.339630643672528,
                48.86437154259803
            ],
            [
                2.342605679231637,
                48.864665214940864
            ],
            [
                2.344093197011191,
                48.8647631053391
            ],
            [
                2.3445394523450576,
                48.86486099554597
            ],
            [
                2.342605679231637,
                48.865644110312104
            ],
            [
                2.3417131685639045,
                48.865644110312104
            ],
            [
                2.337548118781153,
                48.8654483327687
            ],
            [
                2.334721835,
                48.86623143834972
            ],
            [
                2.3362093527795538,
                48.86662298654768
            ],
            [
                2.338143125892974,
                48.86711241748962
            ],
            [
                2.3402256507843497,
                48.86760184364769
            ],
            [
                2.3402256507843497,
                48.86760184364769
            ],
            [
                2.3408206578961717,
                48.86809126502189
            ],
            [
                2.3415644167859497,
                48.86936373820638
            ],
            [
                2.3421594238977708,
                48.86613355082183
            ]
        ]
    )
    ]

print("Ajout des couches WFS")
for url, layer_name, layer_title, geometryTrype, count, extentLength, extentHeight, extentRandom in wfs_layers:
    typename = re.sub("\{.*?}", "", layer_name)
    # Construction de l'URL de la couche WFS
    wfs_uri = f"{url}?TYPENAME={typename}&VERSION=auto&SERVICE=WFS&REQUEST=GetFeature"
    
    # Création de la couche vecteur WFS
    layer = QgsVectorLayer(wfs_uri, typename, providerLib="WFS")
    
    if layer.isValid():
        QgsProject.instance().addMapLayer(layer)
        print(f"✅ Couche ajoutée : {typename}")
    else:
        print(f"❌ Échec pour la couche : {typename}")
    
    #Selection largeur
    extentLengthData = '{ "type": "FeatureCollection", "features": [ { "type": "Feature", "properties": {}, "geometry": { "coordinates": ['+json.dumps(extentLength) +'], "type": "Polygon" } } ] }'
    extentLengthLayer = QgsVectorLayer(extentLengthData, "selectionExtentLength" + layer_name, "ogr")
    if extentLengthLayer.isValid():
        QgsProject.instance().addMapLayer(extentLengthLayer)
        print(f"✅ Polygone largeur de selection ajouté : {typename}")

    #Selection hauteur
    extentHeightData = '{ "type": "FeatureCollection", "features": [ { "type": "Feature", "properties": {}, "geometry": { "coordinates": ['+json.dumps(extentHeight) +'], "type": "Polygon" } } ] }'
    extentHeightLayer = QgsVectorLayer(extentHeightData, "selectionExtentHeight" + layer_name, "ogr")
    if extentHeightLayer.isValid():
        QgsProject.instance().addMapLayer(extentHeightLayer)
        print(f"✅ Polygone hauteur de selection ajouté : {typename}")

    #Selection autre
    extentRandomData = '{ "type": "FeatureCollection", "features": [ { "type": "Feature", "properties": {}, "geometry": { "coordinates": ['+json.dumps(extentRandom) +'], "type": "Polygon" } } ] }'
    extentRandomLayer = QgsVectorLayer(extentRandomData, "selectionExtentRandom" + layer_name, "ogr")
    if extentRandomLayer.isValid():
        QgsProject.instance().addMapLayer(extentRandomLayer)
        print(f"✅ Polygone autre de selection ajouté : {typename}")

    for selection in [extentLengthLayer, extentHeightLayer, extentRandomLayer]:
        processing.run('qgis:intersection', { \
            "INPUT": layer, \
            "OVERLAY": selection, \
            "INPUT_FIELDS": [field.name() for field in layer.fields()], \
            "OVERLAY_FIELDS_PREFIX": "", \
            "OUTPUT": geoJSONPath+ "\\" + selection.name().replace(':','')+'-result.geojson'})


print("Export des couches WFS en GEOJSON")
for layer in QgsProject.instance().mapLayers().values():
    if not isinstance(layer, QgsRasterLayer):
        geojson_path = Path(geoJSONPath) / f"{layer.name().replace(':','')}.geojson"
        QgsVectorFileWriter.writeAsVectorFormat(
            layer,
            str(geojson_path),
            "utf-8",
            driverName="GEOJSON",
            layerOptions=['COORDINATE_PRECISION=8']
        )
        if geojson_path.exists():
            print(f"✅ Couche exportée : {layer.name()}")
        else:
            print(f"❌ Échec pour l'export de la couche : {layer.name()}")