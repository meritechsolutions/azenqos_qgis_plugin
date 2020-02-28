from PyQt5.QtGui import QColor
import time

events_layer = None
selected_ids = []
times = []
layers = QgsProject.instance().mapLayers().values()
for layer in layers:
    layer_name = layer.name()
    if type(layer).__name__ == "QgsVectorLayer":
        if layer_name == "events":
            events_layer = layer
            break

for feature in events_layer.getFeatures():
    times.append(feature["time"])
    selected_ids.append(feature.id())

events_layer.selectByIds(selected_ids)
renderer = QgsMarkerSymbol()

# Use is the column name when I have hexadecimals colors
# renderer.symbolLayers()[0].setDataDefinedProperty(QgsSymbolLayer.PropertyFillColor, QgsProperty.fromField("posid") );
# events_layer.setRenderer(QgsSingleSymbolRenderer(renderer))
print(events_layer)
iface.mapCanvas().setSelectionColor(QColor("red"))
