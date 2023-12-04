from PyQt5.QtCore import (
    pyqtSignal,
    Qt,
    QVariant
)
from PyQt5.QtWidgets import (
    QWidget, QComboBox, QCompleter
)

from PyQt5.QtGui import QIcon, QPixmap, QIntValidator

from PyQt5.uic import loadUi
try:
    from qgis.utils import (
        spatialite_connect
    )
    from qgis.core import (
        QgsProject,
        QgsVectorLayer,
        QgsCoordinateReferenceSystem,
        QgsFeature,
        QgsGeometry,
        QgsField,
        QgsVectorDataProvider,
        QgsPointXY,
        QgsFeatureRequest
    )
except:
    pass
import os
import sys
import traceback
import contextlib
import math
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
import threading
from worker import Worker

from add_param_dialog import CustomQCompleter
import db_preprocess
import preprocess_azm
import azq_utils
import qt_utils
import progress_dialog

class near_cell_filter(QWidget):
    new_feature_signal = pyqtSignal(list)
    near_cell_filter_progress_signal = pyqtSignal(int)
    def __init__(self, parent, gvars):
        super().__init__(parent)
        self.gvars = gvars
        self.layer_names = [layer.name() for layer in QgsProject.instance().mapLayers().values()]
        self.filter_layer_name = self.layer_names[0]
        self.cell_file_layer_name = self.layer_names[0]
        self.near_cell_filter_progress = progress_dialog.progress_dialog("Filtering...")
        self.new_feature_signal.connect(self.add_new_layer)
        self.near_cell_filter_progress_signal.connect(self.update_filter_progress)
        self.radius = "1000"
        self.expression = ""
        self.filter_value = ""
        
        self.setup_ui()
        
    def setup_ui(self):
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.ui = loadUi(azq_utils.get_module_fp("near_cell_filter.ui"), self)
        title = "Near Cell Filter"
        self.setWindowTitle(title)
        
        self.ui.filterLayerComboBox.setEditable(True)
        self.ui.filterLayerComboBox.setInsertPolicy(QComboBox.NoInsert)
        completer = CustomQCompleter(self.ui.filterLayerComboBox)
        completer.setCompletionMode(QCompleter.PopupCompletion)
        completer.setModel(self.ui.filterLayerComboBox.model())
        self.ui.filterLayerComboBox.setCompleter(completer)
        self.ui.filterLayerComboBox.currentIndexChanged.connect(self.select_input_layer)
        
        self.ui.filterParamComboBox.setEditable(True)
        self.ui.filterParamComboBox.setInsertPolicy(QComboBox.NoInsert)
        completer = CustomQCompleter(self.ui.filterParamComboBox)
        completer.setCompletionMode(QCompleter.PopupCompletion)
        completer.setModel(self.ui.filterParamComboBox.model())
        self.ui.filterParamComboBox.setCompleter(completer)

        
        self.ui.radiusLineEdit.setValidator(QIntValidator())
        self.ui.radiusLineEdit.setText(self.radius) 

        self.ui.cellLayerComboBox.setEditable(True)
        self.ui.cellLayerComboBox.setInsertPolicy(QComboBox.NoInsert)
        completer = CustomQCompleter(self.ui.cellLayerComboBox)
        completer.setCompletionMode(QCompleter.PopupCompletion)
        completer.setModel(self.ui.cellLayerComboBox.model())
        self.ui.cellLayerComboBox.setCompleter(completer)
        for layer_name in self.layer_names:
            if layer_name == "OSM":
                continue
            self.ui.filterLayerComboBox.addItem(layer_name)
            self.ui.cellLayerComboBox.addItem(layer_name)
        self.startButton.clicked.connect(self.on_start_button_click)
        
    def select_input_layer(self):
        self.filter_layer_name = self.ui.filterLayerComboBox.currentText()
        feature_layer = QgsProject.instance().mapLayersByName(self.filter_layer_name)[0]
        if self.filter_layer_name != "OSM":
            columns = [f.name() for f in feature_layer.fields()]
            for column in columns:
                self.ui.filterParamComboBox.addItem(column)
            if self.filter_layer_name in columns:
                self.filter_value = self.filter_layer_name
                self.filterParamComboBox.setCurrentText(self.filter_layer_name)

    def create_circle_polygon(self, center_point, radius_degrees):
        circle_polygon = center_point.buffer(radius_degrees)
        return circle_polygon

    def check_intersection(self):
        new_feature_list = []
        filter_progress = 100/len(self.feature_list)
        index = 0
        for feature in self.feature_list:
            self.near_cell_filter_progress_signal.emit(int(filter_progress*(index+1)))
            for cell_polygon in self.cell_polygon_layer_list:
                if cell_polygon.geometry().intersects(feature.geometry()):
                    new_feature_list.append(feature)
                    break
            index += 1
        self.new_feature_signal.emit(new_feature_list)
        self.near_cell_filter_progress_signal.emit(100)

    def update_filter_progress(self, value):
        self.near_cell_filter_progress.set_value(value)
        

    def on_start_button_click(self):
        self.near_cell_filter_progress.show()
        self.filter_layer_name = self.ui.filterLayerComboBox.currentText()
        self.cell_file_layer_name = self.ui.cellLayerComboBox.currentText()
        self.filter_value = self.ui.filterParamComboBox.currentText()
        self.expression = self.ui.expressionLineEdit.text()
        
        if self.expression is None or self.expression == "":
            qt_utils.msgbox("Please input an expressionn")
            return
        
        x = 0
        try:
            test_eval = eval(self.expression)
            if not isinstance(test_eval, bool):
                raise Exception("")
        except:
            qt_utils.msgbox("Invalid expression format. Please input a valid expression", x)
            return
        
        self.radius = self.ui.radiusLineEdit.text()
        offset_meters = int(self.radius)

        self.feature_layer = QgsProject.instance().mapLayersByName(self.filter_layer_name)[0]
        subset_expression = self.expression
        subset_expression = subset_expression.replace("x", self.filter_value)
        subset_expression = subset_expression.replace("==", "=")
        self.feature_list = [pt_feat for pt_feat in self.feature_layer.getFeatures(QgsFeatureRequest().setFilterExpression(subset_expression))]
        ext = self.feature_layer.extent()
        
        degrees_per_meter = 1 / (111.32 * 1000)
        radius_degrees = offset_meters * degrees_per_meter

        xmin = ext.xMinimum() - radius_degrees
        xmax = ext.xMaximum() + radius_degrees
        ymin = ext.yMinimum() - radius_degrees
        ymax = ext.yMaximum() + radius_degrees

        subset_expression = f"lat > {ymin} and lat < {ymax} and lon > {xmin} and lon < {xmax}"
        cell_file_layer = QgsProject.instance().mapLayersByName(self.cell_file_layer_name)[0]
        cell_file_list = [pt_feat for pt_feat in cell_file_layer.getFeatures(QgsFeatureRequest().setFilterExpression(subset_expression))]
        layer_name = "Cell_polygon"
        cell_polygon_layer = QgsVectorLayer("Polygon?crs=EPSG:4326", layer_name, "memory")
        pr = cell_polygon_layer.dataProvider()

        fields = cell_file_layer.fields()
        pr.addAttributes(fields)
        cell_polygon_layer.updateFields()
        used_center_points = set()
        for cell in cell_file_list:
            attrs = cell.attributes()
            center_point = Point(float(cell["lon"]), float(cell["lat"]))
            if center_point in used_center_points:
                continue
            used_center_points.add(center_point)
            circle_polygon = self.create_circle_polygon(center_point, radius_degrees)
            qgs_geometry = QgsGeometry.fromWkt(circle_polygon.wkt)
            feature = QgsFeature()
            feature.setGeometry(qgs_geometry)
            feature.setAttributes(attrs) 
            pr.addFeature(feature)

        cell_polygon_layer.setOpacity(0.3)
        cell_polygon_layer.updateExtents()

        QgsProject.instance().addMapLayer(cell_polygon_layer)
        
        self.cell_polygon_layer_list = [pt_feat for pt_feat in cell_polygon_layer.getFeatures()]
        
        worker = Worker(self.check_intersection)
        self.gvars.threadpool.start(worker)

    def add_new_layer(self, new_feature_list):

        fields = self.feature_layer.fields()
        qml_fp = None
        table = preprocess_azm.get_table_for_column(self.filter_value)
        try:
            with contextlib.closing(spatialite_connect(self.gvars.databasePath)) as dbcon:
                qml_fp = db_preprocess.gen_style_qml_for_theme(None, table, None, self.filter_value, dbcon, to_tmp_file=True)
        except:
            type_, value_, traceback_ = sys.exc_info()
            exstr = str(traceback.format_exception(type_, value_, traceback_))
            print(
                "WARNING: getn style_qml_fpfailed exception: {}".format(
                    exstr
                )
            )
        
        layer = QgsVectorLayer("Point", self.filter_value+"_"+self.expression+"_near_cell", "memory")
        if qml_fp is not None:
            print("style_qml_fp:", qml_fp)
            if os.path.isfile(qml_fp):
                print("loading style file")
                layer.loadNamedStyle(qml_fp)
                print("loading style file done")
            else:
                print("not loading style file as file not found")

        layer.setCrs(QgsCoordinateReferenceSystem("EPSG:4326"))
        layer.dataProvider().addAttributes(fields)
        layer.updateFields()
        layer.dataProvider().addFeatures(new_feature_list)
        layer.updateExtents()
        layer.commitChanges()
        
        print("adding map layer")
        QgsProject.instance().addMapLayer(layer)
        ltlayer = QgsProject.instance().layerTreeRoot().findLayer(layer.id())
        ltlayer.setItemVisibilityChecked(True)
        
        self.near_cell_filter_progress.hide()
        print("adding map layer done")