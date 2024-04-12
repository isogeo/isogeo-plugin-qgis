# -*- coding: utf-8 -*-
#! python3  # noqa: E265

import urllib3
import requests

from xml.etree import ElementTree
from pprint import pprint

urllib3.disable_warnings()

li_wfs_url = [
    "https://magosm.magellium.com/geoserver/wfs?request=GetCapabilities&service=WFS",
    "http://www.sig.cg971.fr:8080/geoserver/wfs?request=GetCapabilities&service=WFS",
    "https://geoservices.business-geografic.com/adws/service/wfs/c0a853d2-bc07-11e8-b09f-61c8a2385105?request=GetCapabilities&service=WFS",
    "http://ws.carmencarto.fr/WFS/105/ONF_Forets?request=GetCapabilities&service=WFS",
]
li_services_cd31 = [
    ("https://wxs.ign.fr/f4v4g9qykk6g8go7m4nfey4b/geoportail/r/wms?request=GetCapabilities&service=WMS", "GetMap"),
    ("https://geoservices.business-geografic.com/adws/service/wfs/c0a853d2-bc07-11e8-b09f-61c8a2385105?request=GetCapabilities&service=WFS", "GetFeature"),
]

for url in li_services_cd31:
    service_dict = {}
    r = requests.get(url=url[0], verify=False)
    root = ElementTree.fromstring(r.text)
    main_op_name = url[1]
    main_op_elem = [elem for elem in root.iter() if (elem.attrib and elem.get("name") == main_op_name) or main_op_name in elem.tag]
    if len(main_op_elem) == 1:
        service_dict["{}_isAvailable".format(main_op_name)] = 1
        main_op_elem = main_op_elem[0]
        li_formatOptions = []
        for subelem in main_op_elem:
            if subelem.tag.endswith("Format"):
                li_formatOptions.append(subelem.text)
        service_dict["formatOptions"] = li_formatOptions
    elif len(main_op_elem) == 0:
        service_dict["{}_isAvailable".format(main_op_name)] = 0
    else:
        service_dict["{}_isAvailable".format(main_op_name)] = 1
    featureTypeList = [elem for elem in root.iter() if elem.tag.endswith("FeatureType") or elem.tag.endswith("Layer")]
    # pprint(featureTypeList)
    li_typenames = []
    for featureType in featureTypeList:
        for elem in featureType:
            if elem.tag.endswith("Name"):
                li_typenames.append(elem.text)
                break
            else:
                pass
    service_dict["typenames"] = li_typenames
    service_dict["version"] = root.get("version")
    pprint(service_dict)