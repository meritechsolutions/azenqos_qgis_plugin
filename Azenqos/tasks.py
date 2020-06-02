import sys
import os

# Adding folder path
sys.path.insert(1, os.path.dirname(os.path.realpath(__file__)))

import global_config as gc

from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *  # QAbstractTableModel, QVariant, Qt, pyqtSignal, QThread
from PyQt5.QtSql import *  # QSqlQuery, QSqlDatabase
from PyQt5.QtGui import *
from qgis.core import *
from qgis.utils import *
from qgis.gui import *


class LayerTask(QgsTask):
    def __init__(self, desc, databasePath):
        QgsTask.__init__(self, desc)
        self.dbPath = databasePath
        self.start_time = None
        self.desc = desc
        self.exception = None
        self.vLayers = []

    def addMapToQgis(self):
        urlWithParams = ""
        # urlWithParams = 'type=xyz&url=http://a.tile.openstreetmap.org/%7Bz%7D/%7Bx%7D/%7By%7D.png&zmax=19&zmin=0&crs=EPSG3857'
        rlayer = QgsRasterLayer(urlWithParams, "Street map", "wms")
        if rlayer.isValid():
            QgsProject.instance().addMapLayer(rlayer)
            # self.azqGroup.addLayer(rlayer)
        else:
            QgsMessageLog.logMessage("Invalid layer")

    def run(self):
        QgsMessageLog.logMessage("[-- Start add layers --]", tag="Processing")
        self.start_time = time.time()

        return True

    def finished(self, result):
        if result:
            gc.mostFeaturesLayer = None
            self.addMapToQgis()
            uri = QgsDataSourceUri()
            uri.setDatabase(self.dbPath)
            gc.allLayers.sort(reverse=True)
            geom_column = "geom"
            for tableName in gc.allLayers:
                uri.setDataSource("", tableName, geom_column)
                vlayer = iface.addVectorLayer(uri.uri(), tableName, "spatialite")
                features = vlayer.featureCount()
                if gc.mostFeaturesLayer is None:
                    gc.mostFeaturesLayer = (tableName, features)
                elif features > gc.mostFeaturesLayer[1]:
                    gc.mostFeaturesLayer = (tableName, features)

                if vlayer:
                    symbol_renderer = vlayer.renderer()
                    if symbol_renderer:
                        symbol = symbol_renderer.symbol()
                        symbol.setColor(QColor(125, 139, 142))
                        symbol.symbolLayer(0).setStrokeColor(QColor(0, 0, 0))
                        symbol.setSize(2.4)
                    iface.layerTreeView().refreshLayerSymbology(vlayer.id())
                    vlayer.triggerRepaint()
                    if not tableName in gc.tableList:
                        gc.tableList.append(tableName)

            iface.mapCanvas().setSelectionColor(QColor("yellow"))

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
                    'Task "{name}" Exception: {exception}'.format(name=self.desc),
                    exception=self.exception,
                    tag="Exception",
                )
                raise self.exception


class QuitTask(QgsTask):
    def __init__(self, desc):
        QgsTask.__init__(self, desc)
        self.start_time = None
        self.desc = desc
        self.exception = None

    def run(self):
        QgsMessageLog.logMessage(
            "[-- Start Removing Dependencies --]", tag="Processing"
        )
        self.start_time = time.time()

        gc.azenqosDatabase.close()
        QSqlDatabase.removeDatabase(gc.azenqosDatabase.connectionName())
        names = QSqlDatabase.connectionNames()
        for name in names:
            QSqlDatabase.database(name).close()
            QSqlDatabase.removeDatabase(name)
        del gc.azenqosDatabase

        return True

    def finished(self, result):
        if result:
            project = QgsProject.instance()
            for (id_l, layer) in project.mapLayers().items():
                if layer.type() == layer.VectorLayer:
                    layer.removeSelection()
                to_be_deleted = project.mapLayersByName(layer.name())[0]
                project.removeMapLayer(to_be_deleted.id())
                layer = None

            QgsProject.instance().reloadAllLayers()
            QgsProject.instance().clear()
            gc.allLayers = []
            gc.tableList = []

            if len(gc.openedWindows) > 0:
                for window in gc.openedWindows:
                    window.close()
                    # window.reject()
                    del window
                gc.openedWindows = []
            QgsProject.removeAllMapLayers(QgsProject.instance())
            elapsed_time = time.time() - self.start_time
            QgsMessageLog.logMessage(
                "Elapsed time: " + str(elapsed_time) + " s.", tag="Processing"
            )
            QgsMessageLog.logMessage(
                "[-- End Removing Dependencies --]", tag="Processing"
            )
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
                    'Task "{name}" Exception: {exception}'.format(name=self.desc),
                    exception=self.exception,
                    tag="Exception",
                )
                raise self.exception
