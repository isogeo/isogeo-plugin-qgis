# table
base_name = "geofla"
schema = "lareunion"
table = "chefslieu974"

# uri constructor
uri = QgsDataSourceURI()

uri.setConnection(host, port, base_name, user, password)
uri.setDataSource(schema, table, "geom")
# uri.setKeyColumn('id')

layer = QgsVectorLayer(uri.uri(True), table, "postgres")
print(layer.error().message())

print(layer.isValid())
QgsMapLayerRegistry.instance().addMapLayer(layer)

print(layer.error().message())

# get fields
prov = layer.dataProvider()
prov.fields().field(0).name()

fields = prov.fields()

# for field in fields:
#    print(field.name(), field.typeName())

i = 0

while not layer.isValid():
    i += 1
    fifi = fields.field(i).name()
    print(fifi)
    uri.setKeyColumn(fifi)
    layer = QgsVectorLayer(uri.uri(True), table, "postgres")

QgsMapLayerRegistry.instance().addMapLayer(layer)
