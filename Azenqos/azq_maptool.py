class AzenqosPointTool(QgsMapTool):
    def __init__(self, canvas):
        QgsMapTool.__init__(self, canvas)
        self.canvas = canvas
        self.vectorLayers = []
        self.features = []
        self.getAllLayers()
        self.maxTime = None

    def canvasPressEvent(self, event):
        pass

    def canvasMoveEvent(self, event):
        x = event.pos().x()
        y = event.pos().y()

        point = self.canvas.getCoordinateTransform().toMapCoordinates(x, y)

    def canvasReleaseEvent(self, event):
        self.removeAllSelection()
        layerData = []
        times = []
        for layer in self.vectorLayers:
            if layer.featureCount() == 0:
                # There are no features - skip
                continue
            layerPoint = self.toLayerCoordinates(layer, event.pos())
            shortestDistance = float("inf")
            closestFeatureId = -1
            # Loop through all features in the layer
            for f in layer.getFeatures():
                dist = f.geometry().distance(QgsGeometry.fromPointXY(layerPoint))

                shortestDistance = dist
                closestFeatureId = f.id()
                if shortestDistance > -1.0 and shortestDistance <= 0.02:
                    info = (layer, closestFeatureId, shortestDistance)
                    layerData.append(info)
                    times.append(layer.getFeature(closestFeatureId).attribute("time"))

        if not len(layerData) > 0:
            # Looks like no vector layers were found - do nothing
            return

            # Sort the layer information by shortest distance
        layerData.sort(key=lambda element: element[2])

        selected_fid = []
        for (layer, closestFeatureId, shortestDistance) in layerData:
            selected_fid.append((layer, closestFeatureId, shortestDistance))
            layer.select(closestFeatureId)
        self.refreshAllLayers()

    def activate(self):
        pass

    def deactivate(self):
        pass

    def isZoomTool(self):
        return False

    def isTransient(self):
        return False

    def isEditTool(self):
        return True

    def getAllLayers(self):
        for layer in self.canvas.layers():
            if layer.type() != QgsMapLayerType.RasterLayer:
                self.vectorLayers.append(layer)

    def initialFeatures(self):
        for f in self.vectorLayers.getFeatures():
            self.features.append(f)

    def refreshAllLayers(self):
        self.canvas.refreshAllLayers()

    def removeAllSelection(self):
        for vlayer in self.vectorLayers:
            vlayer.removeSelection()

    def getMaxTime(self):
        return self.maxTime

    def setMaxTime(self, maxTime):
        self.maxTime = maxTime


tool = AzenqosPointTool(iface.mapCanvas())
iface.mapCanvas().setMapTool(tool)
