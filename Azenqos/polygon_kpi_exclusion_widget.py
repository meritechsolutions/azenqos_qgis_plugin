from PyQt5.QtCore import (
    Qt,
)
from PyQt5.QtWidgets import (
    QWidget, QComboBox, QCompleter
)
from PyQt5.uic import loadUi
try:
    from qgis.utils import (
        spatialite_connect
    )
    from qgis.core import (
        QgsProject,
        QgsVectorLayer,
        QgsCoordinateReferenceSystem
    )
except:
    pass
import os
import sys
import traceback
import contextlib

from add_param_dialog import CustomQCompleter
import db_preprocess
import preprocess_azm
import azq_utils
import qt_utils

class polygon_kpi_exclusion(QWidget):
    def __init__(self, parent, gvars):
        super().__init__(parent)
        self.gvars = gvars
        self.layer_names = [layer.name() for layer in QgsProject.instance().mapLayers().values()]
        self.input_layer_name = self.layer_names[0]
        self.overlay_layer_name = self.layer_names[0]
        self.expression = ""
        self.filter_value = ""
        self.setup_ui()
        
    def setup_ui(self):
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.ui = loadUi(azq_utils.get_module_fp("polygon_kpi_exclusion_widget.ui"), self)
        title = "Calculate KPI from exclusion by polygon"
        self.setWindowTitle(title)
        
        self.ui.inputLayerComboBox.setEditable(True)
        self.ui.inputLayerComboBox.setInsertPolicy(QComboBox.NoInsert)
        completer = CustomQCompleter(self.ui.inputLayerComboBox)
        completer.setCompletionMode(QCompleter.PopupCompletion)
        completer.setModel(self.ui.inputLayerComboBox.model())
        self.ui.inputLayerComboBox.setCompleter(completer)
        self.ui.inputLayerComboBox.currentIndexChanged.connect(self.select_input_layer)
        
        self.ui.filterParamComboBox.setEditable(True)
        self.ui.filterParamComboBox.setInsertPolicy(QComboBox.NoInsert)
        completer = CustomQCompleter(self.ui.filterParamComboBox)
        completer.setCompletionMode(QCompleter.PopupCompletion)
        completer.setModel(self.ui.filterParamComboBox.model())
        self.ui.filterParamComboBox.setCompleter(completer)

        self.ui.overlayLayerComboBox.setEditable(True)
        self.ui.overlayLayerComboBox.setInsertPolicy(QComboBox.NoInsert)
        completer = CustomQCompleter(self.ui.overlayLayerComboBox)
        completer.setCompletionMode(QCompleter.PopupCompletion)
        completer.setModel(self.ui.overlayLayerComboBox.model())
        self.ui.overlayLayerComboBox.setCompleter(completer)
        for layer_name in self.layer_names:
            self.ui.inputLayerComboBox.addItem(layer_name)
            self.ui.overlayLayerComboBox.addItem(layer_name)
        self.calculateButton.clicked.connect(self.on_calculate_button_click)
        
    def select_input_layer(self):
        self.input_layer_name = self.ui.inputLayerComboBox.currentText()
        feature_layer = QgsProject.instance().mapLayersByName(self.input_layer_name)[0]
        if self.input_layer_name != "OSM":
            columns = [f.name() for f in feature_layer.fields()]
            for column in columns:
                self.ui.filterParamComboBox.addItem(column)
            if self.input_layer_name in columns:
                self.filter_value = self.input_layer_name
                self.filterParamComboBox.setCurrentText(self.input_layer_name)


    def on_calculate_button_click(self):
        self.input_layer_name = self.ui.inputLayerComboBox.currentText()
        self.overlay_layer_name = self.ui.overlayLayerComboBox.currentText()
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
            qt_utils.msgbox("Invalid expression format. Please input a valid expression")
            return
        
        feature_layer = QgsProject.instance().mapLayersByName(self.input_layer_name)[0]
        polygon_layer = QgsProject.instance().mapLayersByName(self.overlay_layer_name)[0]
        feature_list = [pt_feat for pt_feat in feature_layer.getFeatures()]
        polygon_list = [pt_feat for pt_feat in polygon_layer.getFeatures()]
        new_feature_list = []
        
        fields = feature_layer.fields()

        for feature in feature_list:
            is_in_polygon = False
            for polygon in polygon_list:
                if polygon.geometry().intersects(feature.geometry()):
                    x = feature[self.filter_value]
                    is_in_polygon = True
                    if eval(self.expression):
                        new_feature_list.append(feature)
                    break
            if not is_in_polygon:
                new_feature_list.append(feature)
        
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
        
        layer = QgsVectorLayer("Point", self.filter_value+"_"+self.expression, "memory")
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
        print("adding map layer done")