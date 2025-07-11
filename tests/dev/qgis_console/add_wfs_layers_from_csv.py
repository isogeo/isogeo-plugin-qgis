import re
from pathlib import Path
from qgis.core import QgsProject, QgsVectorLayer, QgsRasterLayer

# Liste des couches à ajouter : (URL du service WFS, identifiant de la couche)
wfs_layers = [
    (
        "{http://localhost:8080/geoserver/apigdp-258}carte-des-pharmacies-de-paris",
        "https://carto.isogeo.net/geoserver/apigdp-258/wfs",
    ),
    (
        "{http://localhost:8080/geoserver/apigdp-258}les_bureaux_de_poste_et_agences_postales_en_idf",
        "https://carto.isogeo.net/geoserver/apigdp-258/wfs",
    ),
    (
        "{http://localhost:8080/geoserver/apigdp-258}test_no_geom",
        "https://carto.isogeo.net/geoserver/apigdp-258/wfs",
    ),
    (
        "{http://localhost:8080/geoserver/test}dtng_with_aliases",
        "https://carto.isogeo.net/geoserver/test/wfs",
    ),
    (
        "paris-2024-sites-olympiques-et-paralympiques-franciliens",
        "https://carto.isogeo.net/qgisserver-test",
    ),
    (
        "{https://geomatique.longueuil.quebec/public/services/ServicesBrossard/MapServer/WFSServer}Rue_OPA",
        "https://geomatique.longueuil.quebec/public/services/ServicesBrossard/ServicesBrossard/MapServer/WFSServer",
    ),
    (
        "{http://servizigis.regione.emilia-romagna.it/wfs/uso_del_suolo}_008_uso_suolo_ed2011",
        "http://servizigis.regione.emilia-romagna.it/wfs/uso_del_suolo",
    ),
    (
        "{https://gismaps.unc.edu/arcgis/services/CommunityBaseMap/MapServer/WFSServer}Tree_Inventory",
        "https://gismaps.unc.edu/arcgis/services/ESRI_Community_Maps/CommunityBaseMap/MapServer/WFSServer",
    ),
    (
        "{https://gismaps.unc.edu/arcgis/services/CommunityBaseMap/MapServer/WFSServer}Sidewalks",
        "https://gismaps.unc.edu/arcgis/services/ESRI_Community_Maps/CommunityBaseMap/MapServer/WFSServer",
    ),
]

print("Ajout des couches WFS")
for layer_name, url in wfs_layers:
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

print("Export des couches WFS en GEOJSON")
for layer in QgsProject.instance().mapLayers().values():
    if not isinstance(layer, QgsRasterLayer):
        geojson_path = Path(r"C:\Users\SimonSAMPERE\Downloads\geojson_wfs") / f"{layer.name()}.geojson"
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