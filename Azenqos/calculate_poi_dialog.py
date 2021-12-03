import PyQt5
from PyQt5.QtWidgets import QDialog, QComboBox, QCompleter
from PyQt5.uic import loadUi
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QIcon, QPixmap, QIntValidator

try:
    from qgis.core import (
        QgsProject,
        QgsPointXY,
        QgsRectangle
    )
except:
    pass

import os
import statistics
import pandas as pd

import azq_cell_file
import azq_utils
import qgis_layers_gen
from add_param_dialog import CustomQCompleter

COVERAGE_LAYER_DICT = {"nr_servingbeam_ss_rsrp_1":"nr_servingbeam_ss_rsrp_1", "lte_inst_rsrp_1":"lte_inst_rsrp_1", "wcdma_aset_rscp_1":"wcdma_aset_rscp_1", "gsm_rxlev_sub_dbm":"gsm_rxlev_sub_dbm", "overview_nr_servingbeam_ss_rsrp_1":"nr_servingbeam_ss_rsrp_1", "overview_lte_inst_rsrp_1":"lte_inst_rsrp_1", "overview_wcdma_aset_rscp_1":"wcdma_aset_rscp_1", "overview_gsm_rxlev_sub_dbm":"gsm_rxlev_sub_dbm", "ภาพรวม_ความแรงสัญญาณ_5G":"nr_servingbeam_ss_rsrp_1", "ภาพรวม_ความแรงสัญญาณ_4G":"lte_inst_rsrp_1", "ภาพรวม_ความแรงสัญญาณ_3G":"wcdma_aset_rscp_1", "ภาพรวม_ความแรงสัญญาณ_2G":"gsm_rxlev_sub_dbm"}


class calculate_poi(QDialog):
    on_result = pyqtSignal(object, object)
    def __init__(self):
        super(calculate_poi, self).__init__(None)
        self.radius = "1000"
        self.names = [layer.name() for layer in QgsProject.instance().mapLayers().values()]
        self.layer_name = self.names[0]
        self.setAttribute(PyQt5.QtCore.Qt.WA_DeleteOnClose)
        self.setupUi()

    def setupUi(self):
        dirname = os.path.dirname(__file__)
        self.ui = loadUi(azq_utils.get_module_fp("calculate_poi_dialog.ui"), self)
        self.setWindowIcon(QIcon(QPixmap(os.path.join(dirname, "icon.png"))))
        self.setWindowTitle("Calculate POI Coverage")
        self.ui.radiusLineEdit.setValidator(QIntValidator())
        self.ui.radiusLineEdit.setText(self.radius) 
        self.ui.poiComboBox.setEditable(True)
        self.ui.poiComboBox.setInsertPolicy(QComboBox.NoInsert)
        completer = CustomQCompleter(self.ui.poiComboBox)
        completer.setCompletionMode(QCompleter.PopupCompletion)
        completer.setModel(self.ui.poiComboBox.model())
        self.ui.poiComboBox.setCompleter(completer)
        for name in self.names:
            self.ui.poiComboBox.addItem(name)

        self.accepted.connect(self.on_ok_button_click)

    def on_ok_button_click(self):
        self.layer_name = self.ui.poiComboBox.currentText()
        self.radius = self.ui.radiusLineEdit.text()
        layer = QgsProject.instance().mapLayersByName(self.layer_name)[0]
        columns = [f.name() for f in layer.fields()]
        row_list = []
        for f in layer.getFeatures():
            row_list.append(dict(zip(columns, f.attributes())))
        
        df = pd.DataFrame(row_list, columns=columns)
        df.columns= df.columns.str.lower()
        lon_col, lat_col = qgis_layers_gen.get_lon_lat_column_name(columns)
        
        for index, row in df.iterrows():
            offset_meters = int(self.radius)
            offset = azq_cell_file.METER_IN_WGS84 * offset_meters
            lon = row[lon_col]
            lat = row[lat_col]
            if not isinstance(lon, float) or not isinstance(lat, float):
                continue
            p1 = QgsPointXY(lon - offset, lat - offset)
            p2 = QgsPointXY(lon + offset, lat + offset)
            rect = QgsRectangle(p1, p2)
            for cov_layer_name in COVERAGE_LAYER_DICT:
                try:
                    cov_layer = QgsProject.instance().mapLayersByName(cov_layer_name)[0]
                    nearby_features = cov_layer.getFeatures(rect)
                    cov_col = COVERAGE_LAYER_DICT[cov_layer_name]
                    cov_value_list = []
                    cov_value_list = [feat[cov_col] for feat in nearby_features]
                    if len(cov_value_list) > 0:
                        df.loc[index, "radius"] = self.radius
                        df.loc[index, cov_col+"_average"] = statistics.mean(cov_value_list)
                        df.loc[index, cov_col+"_max"] = max(cov_value_list)
                        df.loc[index, cov_col+"_min"] = min(cov_value_list)
                except:
                    pass

        df = df.loc[df["radius"].notna()].reset_index(drop=True)
        window_name = "Coverage" + self.radius + "m. around poi: " + self.layer_name
        self.on_result.emit(df, window_name)
