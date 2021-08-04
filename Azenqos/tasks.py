import time

try:
    from qgis.core import (
        QgsProject,
        QgsTask,
        QgsMessageLog,
        QgsRasterLayer,
        QgsRectangle,
        QgsLayerTreeLayer,
        QgsMapLayerType,
        QgsCoordinateReferenceSystem,
    )
except:
    pass


class LayerTask(QgsTask):
    def __init__(self, desc, databasePath, gc, add_map=True):
        QgsTask.__init__(self, desc)
        print("start layertask: databasePath {}".format(databasePath))
        self.dbPath = databasePath
        self.start_time = None
        self.desc = desc
        self.exception = None
        self.vLayers = []
        self.gc = gc
        self.add_map=add_map

    def addMapToQgis(self):

        urlWithParams = (
            "type=xyz&url=http://a.tile.openstreetmap.org/%7Bz%7D/%7Bx%7D/%7By%7D.png"
        )

        rlayer = QgsRasterLayer(urlWithParams, "OSM", "wms")
        if rlayer.isValid():
            QgsProject.instance().addMapLayer(rlayer)
            # self.azqGroup.addLayer(rlayer)
        else:
            QgsMessageLog.logMessage("Invalid layer")

    def zoomToActiveLayer(self):
        root = QgsProject.instance().layerTreeRoot()
        groups = root.findGroups()
        extent = QgsRectangle()
        extent.setMinimal()
        if len(groups) > 0:
            for child in groups[0].children():
                if isinstance(child, QgsLayerTreeLayer):
                    extent.combineExtentWith(child.layer().extent())
        else:
            layers = root.findLayers()
            for child in layers:
                if isinstance(child, QgsLayerTreeLayer):
                    msg = "child.layer().type(): {}".format(child.layer().type())
                    print(msg)
                    QgsMessageLog.logMessage(msg)
                    try:
                        if child.layer().type() == QgsMapLayerType.VectorLayer:
                            extent.combineExtentWith(child.layer().extent())
                    except Exception as ne:
                        print(
                            "check QgsMapLayerType.VectorLayer failed: {} - try fallback to alt method".format(
                                ne
                            )
                        )
                        if child.layer().type() == 0:
                            extent.combineExtentWith(child.layer().extent())

            self.gc.qgis_iface.mapCanvas().setExtent(extent)
            self.gc.qgis_iface.mapCanvas().refresh()

    def run(self):
        if not self.gc.qgis_iface:
            return
        QgsMessageLog.logMessage("[-- Start add layers --]", tag="Processing")
        self.start_time = time.time()
        return True

    def finished(self, result):
        if result:
            # gc.mostFeaturesLayer = None
            if self.add_map:
                self.addMapToQgis()

                import spider_plot
                spider_plot.plot_rat_spider(self.gc.cell_files, self.gc.databasePath, "nr")
                spider_plot.plot_rat_spider(self.gc.cell_files, self.gc.databasePath, "lte")
                spider_plot.plot_rat_spider(self.gc.cell_files, self.gc.databasePath, "wcdma")
                spider_plot.plot_rat_spider(self.gc.cell_files, self.gc.databasePath, "gsm")

            # geom_column = "geom"
            self.gc.qgis_iface.addVectorLayer(self.dbPath, None, "ogr")

            # Setting CRS
            my_crs = QgsCoordinateReferenceSystem(4326)
            QgsProject.instance().setCrs(my_crs)

            self.zoomToActiveLayer()

            elapsed_time = time.time() - self.start_time
            QgsMessageLog.logMessage(
                "Elapsed time: " + str(elapsed_time) + " s.", tag="Processing"
            )
            QgsMessageLog.logMessage("[-- End add layers --]", tag="Processing")
        else:
            if self.exception is None:
                QgsMessageLog.logMessage(
                    'Task "{name}" not successful but without '
                    "exception (probably the task was manually "
                    "canceled by the user)".format(name=self.desc),
                    tag="Exception",
                )
            else:
                QgsMessageLog.logMessage(
                    'Task "{name}" Exception: {exception}'.format(
                        name=self.desc, exception=self.exception
                    ),
                    tag="Exception",
                )
                raise self.exception


class QuitTask(QgsTask):
    def __init__(self, desc, azenqosMain):
        QgsTask.__init__(self, desc)
        self.start_time = None
        self.desc = desc
        self.exception = None
        self.azqMain = azenqosMain

    def run(self):
        QgsMessageLog.logMessage(
            "[-- Start Removing Dependencies --]", tag="Processing"
        )
        self.start_time = time.time()
        return True

    def finished(self, result):
        if result:
            elapsed_time = time.time() - self.start_time
            QgsMessageLog.logMessage(
                "Elapsed time: " + str(elapsed_time) + " s.", tag="Processing"
            )
            QgsMessageLog.logMessage(
                "[-- End Removing Dependencies --]", tag="Processing"
            )
            """
            if self.azqMain.newImport is False:
                self.azqMain.databaseUi.removeMainMenu()
            """
        else:
            if self.exception is None:
                QgsMessageLog.logMessage(
                    'Task "{name}" not successful but without '
                    "exception (probably the task was manually "
                    "canceled by the user)".format(name=self.desc),
                    tag="Exception",
                )
            else:
                QgsMessageLog.logMessage(
                    'Task "{name}" Exception: {exception}'.format(
                        name=self.desc, exception=self.exception
                    ),
                    tag="Exception",
                )
                raise self.exception
