from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *  # QAbstractTableModel, QVariant, Qt, pyqtSignal, QThread
from PyQt5.QtGui import *
try:
    from qgis.core import *
    from qgis.utils import *
    from qgis.gui import *
except:
    pass
import qt_utils


def create_qgis_layer_csv(csv_fp, layer_name="layer"):
    print("create_qgis_layer_csv() START")
    uri = "{}?crs=epsg:4326".format(csv_fp)
    print("csv uri: {}".format(uri))
    layer = QgsVectorLayer(uri, layer_name, "delimitedtext")
    QgsProject.instance().addMapLayers([layer])
    print("create_qgis_layer_csv() DONE")


def create_test_qgis_layer_py_objs():
    print("create_test_qgis_layer_action() impl START")

    fields = QgsFields()
    fields.append(QgsField("cell_id", QVariant.Int))

    layer = QgsVectorLayer("Point?crs=epsg:4326", "temporary_points", "memory")
    pr = layer.dataProvider()
    pr.addAttributes(fields)
    layer.updateFields()


    fet = QgsFeature()
    fet.setGeometry( QgsGeometry.fromPointXY(QgsPointXY(25.60278,-33.98113)) )

    pr.addFeatures( [ fet ] )
    layer.updateExtents()

    QgsProject.instance().addMapLayers([layer])
    print("create_test_qgis_layer_action() impl DONE")


