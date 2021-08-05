import os
import sys
import time
import traceback

try:
    from qgis.core import (
        QgsProject,
        QgsTask,
        QgsMessageLog,
        QgsRectangle,
        QgsLayerTreeLayer,
        QgsMapLayerType,
        QgsCoordinateReferenceSystem,
    )
except:
    pass


class LayerTask(QgsTask):
    def __init__(self, desc, databasePath, gc, task_done_signal):
        QgsTask.__init__(self, desc)
        print("start layertask: databasePath {}".format(databasePath))
        self.task_done_signal = task_done_signal
        self.dbPath = databasePath
        self.start_time = time.time()
        self.desc = desc
        self.exception = None
        self.vLayers = []
        self.gc = gc



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
        self.start_time = time.time()
        return True


    def finished(self, result):
        self.task_done_signal.emit(os.path.basename(__file__))

    def add_layers_from_ui_thread(self):
        try:
            if True:
                # gc.mostFeaturesLayer = None
                print("db_layer_task.py add_layers_from_ui_thread 0")

                print("db_layer_task.py add_layers_from_ui_thread() 3 addVectorLayer")
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
        except:
            type_, value_, traceback_ = sys.exc_info()
            exstr = str(traceback.format_exception(type_, value_, traceback_))
            print("WARNING: load cell file - exception: {}".format(exstr))
        print("add_layers_from_ui_thread() end")


    def run_blocking(self):
        self.run()
        self.add_layers_from_ui_thread()


