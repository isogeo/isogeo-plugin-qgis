from owslib.csw import CatalogueServiceWeb

csw_url = "https://services.api.isogeo.com/ows/s/8d491301f61249139918e3710cd39eb7/c/355b870869204c39b0fb9deb44469f2a/wak8OBU2hQX6F6rtIe3fWiRCvzFH0?service=CSW&version=2.0.2&request=GetCapabilities"
csw = CatalogueServiceWeb(csw_url)
print(csw.identification.type)
print([op.name for op in csw.operations])
csw.getrecords()
for rec in csw.records:
    print(csw.records[rec].abstract)
    print(rec)