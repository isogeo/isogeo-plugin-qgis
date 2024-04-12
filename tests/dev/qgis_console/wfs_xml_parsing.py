import requests
from xml.etree import ElementTree
from pprint import pprint

url_1 = "https://wxs.ign.fr/f4v4g9qykk6g8go7m4nfey4b/geoportail/wfs?request=GetCapabilities&service=wfs"
url_2 = "https://geoservices.business-geografic.com/adws/service/wfs/c0a853d2-bc07-11e8-b09f-61c8a2385105?SERVICE=WFS&REQUEST=GetCapabilities&ACCEPTVERSIONS=2.0.0,1.1.0,1.0.0"

li_urls = [
    url_1,
    url_2,
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

    xml_featureTypelist = xml_root.find(tag_prefix + "FeatureTypeList")
    
    for featureType in xml_featureTypelist.findall(tag_prefix + "FeatureType"):
        featureType_name = featureType.find(tag_prefix + "Name").text
        print(featureType_name)
