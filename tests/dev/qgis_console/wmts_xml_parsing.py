import requests
from xml.etree import ElementTree
from pprint import pprint
from owslib.wmts import WebMapTileService

url_1 = "https://wxs.ign.fr/f4v4g9qykk6g8go7m4nfey4b/geoportail/wmts/?SERVICE=WMTS&VERSION=1.0.0&REQUEST=GetCapabilities"

li_urls = [
    url_1,
#    url_2,
#    url_3, 
#    "https://jmap7dev-jakarta.jmaponline.net/wms_isogeo/wms?request=GetCapabilities&service=WMS",
#    "http://georisques.gouv.fr/services?request=GetCapabilities&service=WMS",
#    "https://carto.isogeo.net/geoserver/ows?request=GetCapabilities&service=WMS",
#    "http://carto.isogeo.net/qgisserver/env-test?request=GetCapabilities&service=WMS",
]

#service = WebMapTileService(url=url_1, version="1.0.0")
#pprint(service.__dict__)
#pprint([service.tilematrixsets.get(tms).__dict__ for tms in service.tilematrixsets])

for url in li_urls:
    print("\n" + url)
    try:
        r = requests.get(url=url, verify=False)
    except:
        continue

    xml_root = ElementTree.fromstring(r.text)
    tag_prefix = xml_root.tag.split("}")[0] + "}"
    print(tag_prefix)

    xml_operationsMetadata = [child for child in xml_root if "OperationsMetadata" in child.tag][0]
    main_op_elem = [ope for ope in xml_operationsMetadata if "GetTile" in ope.get("name")]
    print(main_op_elem[0].get("name"))

    # retrieving TMS
    dict_tms = {}
    for tms in xml_root.find(tag_prefix + "Contents").findall(tag_prefix + "TileMatrixSet"):
        # identifier
        li_tms_id = [child.text for child in tms if child.tag.endswith("Identifier")]
        li_tms_crs = [child.text for child in tms if child.tag.endswith("SupportedCRS")]

        if not len(li_tms_id) or not len(li_tms_crs):
            continue
        else:
            dict_tms[li_tms_id[0]] = li_tms_crs[0]
    pprint(dict_tms)

    # retrieving layers typenames and building layers list (bbox, tms, typename)
    li_typenames = []
    li_layers = []
    print(xml_root.find(tag_prefix + "Contents"))
    for layer in xml_root.find(tag_prefix + "Contents").findall(tag_prefix + "Layer"):
        layer_dict = {}
        # typename
        li_layer_typenames = [child.text for child in layer if child.tag.endswith("Identifier")]
        if not len(li_layer_typenames):
            continue
        else:
            li_typenames.append(li_layer_typenames[0])
            layer_dict["typename"] = li_layer_typenames[0]
        # format
        li_layer_formats = [child.text for child in layer if child.tag.endswith("Format")]
        if not len(li_layer_formats):
            layer_dict["format"] = ""
        else:
            layer_dict["format"] = li_layer_formats[0]
        # tms
        xml_tmsLink = [child for child in layer if child.tag.endswith("TileMatrixSetLink")][0]
        li_layer_tms = [child.text for child in xml_tmsLink if child.tag.endswith("TileMatrixSet")]
        if not len(li_layer_tms):
            layer_dict["tms"] = ""
        else:
            layer_dict["tms"] = li_layer_tms[0]
        # crs
        layer_dict["crs"] = dict_tms.get(layer_dict.get("tms"))
        
        li_layers.append(layer_dict)

    pprint(li_typenames)
    pprint(li_layers)