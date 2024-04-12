import requests
from xml.etree import ElementTree
from pprint import pprint

url_1 = "https://wxs.ign.fr/essentiels/geoportail/r/wms?request=GetCapabilities&service=WMS"
url_2 = "https://wxs.ign.fr/f4v4g9qykk6g8go7m4nfey4b/geoportail/v/wms?request=GetCapabilities&service=WMS"
url_3 = "https://wxs.ign.fr/f4v4g9qykk6g8go7m4nfey4b/geoportail/r/wms?request=GetCapabilities&service=WMS"

li_urls = [
    url_1,
#    url_2,
#    url_3, 
#    "https://jmap7dev-jakarta.jmaponline.net/wms_isogeo/wms?request=GetCapabilities&service=WMS",
#    "http://georisques.gouv.fr/services?request=GetCapabilities&service=WMS",
#    "https://carto.isogeo.net/geoserver/ows?request=GetCapabilities&service=WMS",
#    "http://carto.isogeo.net/qgisserver/env-test?request=GetCapabilities&service=WMS",
]

for url in li_urls:
    print("\n" + url)
    try:
        r = requests.get(url=url, verify=False)
    except:
        continue

    xml_root = ElementTree.fromstring(r.text)
    tag_prefix = xml_root.tag.split("}")[0] + "}"

    xml_cap = [child for child in xml_root if "Capability" in child.tag][0]
    
    xml_request = [child for child in xml_cap if "Request" in child.tag][0]
    xml_getMap = [child for child in xml_request.findall(tag_prefix + "GetMap")]
    
    tag_prefix = xml_root.tag.split("}")[0] + "}"

    xml_cap = [child for child in xml_root if "Capability" in child.tag][0]

    # check if get data operation is available + retrieve formatOptions
    xml_request = [child for child in xml_cap if "Request" in child.tag][0]
    main_op_elem = [child for child in xml_request.findall(tag_prefix + "GetMap")]
    if len(main_op_elem) == 1:
        print(main_op_elem[0].tag)
        li_formatOptions = [child.text for child in main_op_elem[0].findall(tag_prefix + "Format")]
        print(li_formatOptions)
    else:
        pass

    # retrieving CRS options common to all layers
    li_common_crs = [child.text for child in xml_cap.find(tag_prefix + "Layer").findall(tag_prefix + "CRS")]

    # retrieving layers typenames and building layers list (bbox, crs, typename)
    li_typenames = []
    li_layers = []
    for layer in xml_cap.find(tag_prefix + "Layer").findall(tag_prefix + "Layer"):
        # typename
        layer_dict = {}
        li_layer_typenames = [child.text for child in layer.findall(tag_prefix + "Name")]
        if not len(li_layer_typenames):
            continue
        else:
            li_typenames.append(li_layer_typenames[0])
            layer_dict["typename"] = li_layer_typenames[0]

        # CRS options
        li_layer_crs = [child.text for child in layer.findall(tag_prefix + "CRS")]
        if not len(li_layer_crs):
            layer_dict["crsOptions"] = li_common_crs
        else:
            layer_dict["crsOptions"] = li_common_crs + li_layer_crs

        # BBOX
#        wgs84_bbox = layer.find(tag_prefix + "EX_GeographicBoundingBox")
#        if len(wgs84_bbox) and "EPSG:4326" in layer_dict.get("crsOptions"):
#            xmin = str(wgs84_bbox.find(tag_prefix + "southBoundLatitude").text)
#            ymin = str(wgs84_bbox.find(tag_prefix + "westBoundLongitude").text)
#            xmax = str(wgs84_bbox.find(tag_prefix + "northBoundLatitude").text)
#            ymax = str(wgs84_bbox.find(tag_prefix + "eastBoundLongitude").text)
#            layer_dict["crsOptions"] = ["EPSG:4326"]
#            layer_dict["bbox"] = [xmin, ymin, xmax, ymax]
#        else:
        li_other_bboxes = [child for child in layer.findall(tag_prefix + "BoundingBox") if child.get("CRS") in layer_dict["crsOptions"]]
        if not len(li_other_bboxes):
            layer_dict["bbox"] = []
        else:
            xmin = str(li_other_bboxes[0].get("minx"))
            ymin = str(li_other_bboxes[0].get("miny"))
            xmax = str(li_other_bboxes[0].get("maxx"))
            ymax = str(li_other_bboxes[0].get("maxy"))

            layer_dict["crsOptions"] = [str(li_other_bboxes[0].get("CRS"))]
            layer_dict["bbox"] = [xmin, ymin, xmax, ymax]

        li_layers.append(layer_dict)
        
    pprint(li_layers)
    pprint(li_typenames)

#    if len(xml_getMap) == 1:
#        li_getMap_formats = [child.text for child in xml_getMap[0].findall(tag_prefix + "Format")]
#        print(li_getMap_formats)
#    else:
#        print(len(xml_getMap))
        
#    li_common_crs = [child.text for child in xml_cap.iter(tag_prefix + "CRS")]
#    for layer in xml_cap.find(tag_prefix + "Layer").findall(tag_prefix + "Layer"):
#        layer_dict = {}
#        li_layer_typenames = [child.text for child in layer.findall(tag_prefix + "Name")]
#        if not len(li_layer_typenames):
#            pass
#        else:
#            layer_dict["typename"] = li_layer_typenames[0]
#
#        li_layer_crs = [child.text for child in layer.findall(tag_prefix + "CRS")]
#        if not len(li_layer_crs):
#            layer_dict["crs"] = li_common_crs
#        else:
#            layer_dict["crs"] = li_common_crs + li_layer_crs
#
#        li_layer_bboxes = [child for child in layer.findall(tag_prefix + "BoundingBox")] + [child for child in layer.findall(tag_prefix + "EX_GeographicBoundingBox")]
#        for bbox in li_layer_bboxes:
#        if not len(li_layer_bboxes):
#            pass
#        else:
#            layer_dict["bbox"] = li_layer_bboxes[0]
#
#        pprint(layer_dict)
#    print(li_common_crs)
#    print(xml_cap.find(tag_prefix + "Layer").tag)
#    for layer in xml_cap.find(tag_prefix + "Layer").findall(tag_prefix + "Layer"):
#        print(layer.tag)
#        li_layer_crs = [child.text for child in layer.findall(tag_prefix + "CRS")]
#        if not len(li_layer_crs):
#            continue
#        else:
#            print(li_layer_crs)
    
#    li_typenames = []
#    for layer in xml_cap.find(tag_prefix + "Layer").findall(tag_prefix + "Layer"):
#        li_layer_typenames = [child.text for child in layer.findall(tag_prefix + "Name")]
#        if not len(li_layer_typenames):
#            continue
#        else:
#            layer_typename = li_layer_typenames[0]
#            li_typenames.append(li_layer_typenames[0])
#    print(li_typenames)

#        li_layer_bboxes = [child for child in layer.findall(tag_prefix + "BoundingBox")]
#
#        if not len(li_layer_bboxes):
#            continue
#        else:
#            layer_bbox = li_layer_bboxes[0]
#        print(layer_bbox.attrib)
#        
#        if len(layer_bbox.attrib):
#            print(layer_bbox.attrib)