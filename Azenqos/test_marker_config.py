from random import randrange

# Get the active layer (must be a vector layer)
layer = qgis.utils.iface.activeLayer()

# get unique values
fni = layer.fields().lookupField('posid')
unique_values = layer.dataProvider().uniqueValues(fni)

# define categories
categories = []
for unique_value in unique_values:
    # initialize the default symbol for this geometry type
    symbol = QgsSymbol.defaultSymbol(layer.geometryType())

    # configure a symbol layer
    layer_style = {}
    layer_style['color'] = '%d, %d, %d' % (randrange(0,256), randrange(0,256), randrange(0,256))
    layer_style['outline'] = '#000000'
    layer_style['size'] = '10.0'
    symbol_layer = QgsSimpleFillSymbolLayer.create(layer_style)
    # replace default symbol layer with the configured one
    if symbol_layer is not None:
        symbol.changeSymbolLayer(0, symbol_layer)
        symbol.setSize(4)

    # create renderer object
    category = QgsRendererCategory(unique_value, symbol, str(unique_value))
    # entry for the list of category items
    categories.append(category)

# create renderer object
renderer = QgsCategorizedSymbolRenderer('posid', categories)

# assign the created renderer to the layer
if renderer is not None:
    layer.setRenderer(renderer)

layer.triggerRepaint()