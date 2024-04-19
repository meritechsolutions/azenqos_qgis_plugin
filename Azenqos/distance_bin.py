from PyQt5.QtCore import (
    Qt, QVariant
)
from PyQt5.QtWidgets import (
    QWidget, QComboBox, QCompleter
)
from PyQt5.uic import loadUi
try:
    from qgis.core import (
        QgsProject,
        QgsFeatureRequest
    )
except:
    pass
import sqlite3
import contextlib
import pandas as pd

from add_param_dialog import CustomQCompleter
import db_preprocess
import distance
import log_exporter
import preprocess_azm
import azq_utils
import qt_utils

class distance_bin(QWidget):
    def __init__(self, parent, gvars):
        super().__init__(parent)
        self.gvars = gvars
        self.layer_names = [layer.name() for layer in QgsProject.instance().mapLayers().values()]
        self.input_layer_name = self.layer_names[0]
        self.distance = ""
        self.main_parameter = ""
        self.setup_ui()
        
    def setup_ui(self):
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.ui = loadUi(azq_utils.get_module_fp("distance_bin.ui"), self)
        title = "Distance Binning"
        self.setWindowTitle(title)
        
        self.ui.inputLayerComboBox.setEditable(True)
        self.ui.inputLayerComboBox.setInsertPolicy(QComboBox.NoInsert)
        completer = CustomQCompleter(self.ui.inputLayerComboBox)
        completer.setCompletionMode(QCompleter.PopupCompletion)
        completer.setModel(self.ui.inputLayerComboBox.model())
        self.ui.inputLayerComboBox.setCompleter(completer)
        self.ui.inputLayerComboBox.currentIndexChanged.connect(self.select_input_layer)
        
        for layer_name in self.layer_names:
            self.ui.inputLayerComboBox.addItem(layer_name)
        self.calculateButton.clicked.connect(self.on_calculate_button_click)

    def select_input_layer(self):
        self.input_layer_name = self.ui.inputLayerComboBox.currentText()
        feature_layer = QgsProject.instance().mapLayersByName(self.input_layer_name)[0]
        if self.input_layer_name != "OSM":
            columns = [f.name() for f in feature_layer.fields()]
            for column in columns:
                self.ui.parameterComboBox.addItem(column)
            if self.input_layer_name in columns:
                self.filter_value = self.input_layer_name
                self.parameterComboBox.setCurrentText(self.input_layer_name)

    def on_calculate_button_click(self):
        self.input_layer_name = self.ui.inputLayerComboBox.currentText()
        self.main_parameter = self.ui.parameterComboBox.currentText()
        self.distance = self.ui.distanceLineEdit.text()
        if self.distance is None or self.distance == "":
            qt_utils.msgbox("Please input a distance")
            return

        distance_bin_meters = 0.0
        try:
            distance_bin_meters = float(self.distance)
            if not isinstance(distance_bin_meters, float):
                raise Exception("")
        except:
            qt_utils.msgbox("Invalid input. The distance must be a numerical value")
            return
        
        layer_columns = ["log_hash", "time", "posid", "seqid", "netid"]
        layer_columns.append(self.main_parameter)

        feature_layer = QgsProject.instance().mapLayersByName(self.input_layer_name)[0]
        feature_list = [pt_feat for pt_feat in feature_layer.getFeatures(QgsFeatureRequest().setFlags(QgsFeatureRequest.NoGeometry))]
        filter_feature_list = []
        for feature in feature_list:
            attrs = [None if isinstance(feature[layer_column], QVariant) and feature[layer_column].isNull() else feature[layer_column] for layer_column in layer_columns]
            filter_feature_list.append(attrs)
            
        df = pd.DataFrame(filter_feature_list, columns=layer_columns)
        
        
        if ((("lat" not in df.columns) and ("lon" not in df.columns)) and (("positioning_lat" not in df.columns) and ("positioning_lon" not in df.columns))) and self.gvars.databasePath is not None:
            print("need to merge lat and lon")
            with contextlib.closing(sqlite3.connect(self.gvars.databasePath)) as dbcon:
                df = preprocess_azm.merge_lat_lon_into_df(dbcon, df).rename(
                    columns={"positioning_lat": "lat", "positioning_lon": "lon"}
                )
        
        distance_bin_agg_dict = log_exporter.gen_distance_bin_agg_dict(df)
        
        ori_cols = df.columns.values.tolist()
        df_prepare_data = distance.df_distance_bin_meters(df, "lat", "lon",
                                                        distance_bin_meters, agg_dict=distance_bin_agg_dict,
                                                        keep_new_cols=False)
        df_prepare_data = df_prepare_data[ori_cols]
        
        if self.gvars.is_indoor:
            location_sqlstr = "select time, log_hash, positioning_lat, positioning_lon from location where positioning_lat is not null and positioning_lon is not null"
            df_location = pd.read_sql(location_sqlstr, dbcon, parse_dates=['time'])
            df_prepare_data = db_preprocess.add_pos_lat_lon_to_indoor_df(df_prepare_data, df_location).rename(
            columns={"positioning_lat": "lat", "positioning_lon": "lon"}).reset_index(drop=True)
            if "geom" in df_prepare_data.columns:
                del df_prepare_data["geom"]

        azq_utils.create_layer_in_qgis(self.gvars.databasePath, df_prepare_data, self.input_layer_name+"_binning_"+self.distance, theme_param = self.main_parameter)