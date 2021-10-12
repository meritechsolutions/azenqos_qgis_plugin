import contextlib
import os
import sqlite3
import sys
import time
import traceback
import threading
import pandas as pd

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
        self.add_layers_from_ui_thread()
        return True


    def finished(self, result):
        self.task_done_signal.emit(os.path.basename(__file__))

    def add_layers_from_ui_thread(self, select=False, ogr_mode=False):
        try:
            if self.gc.qgis_iface:
                # gc.mostFeaturesLayer = None
                print("db_layer_task.py add_layers_from_ui_thread 0")
                # Setting CRS
                my_crs = QgsCoordinateReferenceSystem(4326)
                QgsProject.instance().setCrs(my_crs)
                print("db_layer_task.py add_layers_from_ui_thread() 3 addVectorLayer")
                # geom_column = "geom"
                table_list = None
                with contextlib.closing(sqlite3.connect(self.dbPath)) as dbcon:
                    table_list = pd.read_sql("select f_table_name from geometry_columns", dbcon).f_table_name.values

                if ogr_mode:
                    #TODO add lower direct, non-ogr support?
                    self.gc.qgis_iface.addVectorLayer(self.dbPath, None, "ogr")
                else:
                    import qgis_layers_gen
                    last_visible_layer = None
                    table_to_layer_dict = {}
                    for table in table_list:
                        print("Adding table layer to UI:", table)
                        try:
                            import azq_utils
                            import system_sql_query
                            visible = False
                            if table in system_sql_query.rat_to_main_param_dict.values():
                                visible = True
                            layer = qgis_layers_gen.create_qgis_layer_from_spatialite_db(
                            self.dbPath, table, visible=visible, style_qml_fp=azq_utils.tmp_gen_fp("style_{}.qml".format(table)), add_to_qgis=False
                            )
                            table_to_layer_dict [table] = layer
                            if visible:
                                last_visible_layer = layer
                        except:
                            type_, value_, traceback_ = sys.exc_info()
                            exstr = str(traceback.format_exception(type_, value_, traceback_))
                            print("WARNING: create_qgis_layer_from_spatialite_db table {} failed exception: {}".format(
                                table, exstr
                            )
                        )
                        layers = table_to_layer_dict.values()
                        QgsProject.instance().addMapLayers(layers)
                        for layer in layers:
                            ltlayer = QgsProject.instance().layerTreeRoot().findLayer(layer.id())
                            ltlayer.setExpanded(False)
                            visible = False
                            if last_visible_layer is not None and last_visible_layer.id() == layer.id():
                                visible = True
                                self.gc.qgis_iface.setActiveLayer(last_visible_layer)
                            ltlayer.setItemVisibilityChecked(visible)

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


    def run_blocking(self, select=False):
        self.add_layers_from_ui_thread()



