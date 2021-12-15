import PyQt5
from PyQt5.QtWidgets import QDialog, QComboBox, QCompleter
from PyQt5.uic import loadUi
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QIcon, QPixmap, QIntValidator

try:
    from qgis.core import (
        QgsProject,
        QgsPointXY,
        QgsRectangle,
        QgsFeatureRequest,
        QgsSpatialIndex,
        QgsFeature
    )
except:
    pass

import os
import contextlib
import sqlite3
import pandas as pd
import numpy as np
import struct

import azq_cell_file
import azq_utils
import qgis_layers_gen
from add_param_dialog import CustomQCompleter

COVERAGE_LAYER_DICT = {"nr_servingbeam_ss_rsrp_1":"nr_servingbeam_ss_rsrp_1", "lte_inst_rsrp_1":"lte_inst_rsrp_1", "wcdma_aset_rscp_1":"wcdma_aset_rscp_1", "gsm_rxlev_sub_dbm":"gsm_rxlev_sub_dbm", "overview_nr_servingbeam_ss_rsrp_1":"nr_servingbeam_ss_rsrp_1", "overview_lte_inst_rsrp_1":"lte_inst_rsrp_1", "overview_wcdma_aset_rscp_1":"wcdma_aset_rscp_1", "overview_gsm_rxlev_sub_dbm":"gsm_rxlev_sub_dbm", "ภาพรวม_ความแรงสัญญาณ_5G":"nr_servingbeam_ss_rsrp_1", "ภาพรวม_ความแรงสัญญาณ_4G":"lte_inst_rsrp_1", "ภาพรวม_ความแรงสัญญาณ_3G":"wcdma_aset_rscp_1", "ภาพรวม_ความแรงสัญญาณ_2G":"gsm_rxlev_sub_dbm"}

rat_to_table_and_primary_where_dict = {
    "NR": "nr_cell_meas",
    "LTE": "lte_cell_meas",
    "WCDMA": "wcdma_cell_meas",
    "GSM": "gsm_cell_meas",
}
rat_to_main_param_dict = {
    "NR": "nr_servingbeam_ss_rsrp_1",
    "LTE": "lte_inst_rsrp_1",
    "WCDMA": "wcdma_aset_rscp_1",
    "GSM": "gsm_rxlev_sub_dbm",
}

def haversine(lat1, lon1, lat2, lon2, to_radians=True, earth_radius=6371):
    if to_radians:
        lat1, lon1, lat2, lon2 = np.radians([lat1, lon1, lat2, lon2])

    a = np.sin((lat2-lat1)/2.0)**2 + \
        np.cos(lat1) * np.cos(lat2) * np.sin((lon2-lon1)/2.0)**2

    return earth_radius * 2 * np.arcsin(np.sqrt(a))

def geomToLatLon(geomBlob):
    if geomBlob is None:
        return None
    lon = struct.unpack('d', geomBlob[43:51])[0]
    lat = struct.unpack('d', geomBlob[51:59])[0]
    return lat, lon

def get_technology_df(dbcon, cov_column_name_list):
    per_rat_df_list = []
    for rat in rat_to_table_and_primary_where_dict:
        try:
            sql = "select log_hash, time, geom, {} as value from {}".format(
                rat_to_main_param_dict[rat], rat_to_table_and_primary_where_dict[rat]
            )
            df = pd.read_sql(sql, dbcon, parse_dates=["Time"])
            df["name"] = rat_to_main_param_dict[rat]
            cov_column_name_list.append(rat_to_main_param_dict[rat])
            per_rat_df_list.append(df)
        except Exception as e:
            print("WARNING: gen per_rat_df failed:", e)
    df = pd.concat(per_rat_df_list, ignore_index=True)
    df.sort_values(["log_hash", "time"], inplace=True)
    df = df.loc[(df["geom"].notna()) & (df["value"].notna())].reset_index(drop=True)
    return df ,cov_column_name_list

def calculate_poi_cov(poi_list, cov_df, cov_column_name_list, lat_col, lon_col, offset):
    row_df_list = []
    for row in poi_list:
        try:
            poi_lat = float(row[lat_col])
            poi_lon = float(row[lon_col])
        except:
            pass
        if isinstance(poi_lat, float) and isinstance(poi_lon, float):
            cov_df["poi_lat"] = poi_lat
            cov_df["poi_lon"] = poi_lon
            cov_df_loc = cov_df.loc[(abs(cov_df["lat"] - cov_df["poi_lat"]) <= offset) & (abs(cov_df["lon"] - cov_df["poi_lon"]) <= offset) ]
            if len(cov_df_loc) > 0:
                for cov_column_name in cov_column_name_list:
                    avg_cov_col = cov_column_name+"_average"
                    row[avg_cov_col] = cov_df_loc.loc[cov_df_loc["name"] == cov_column_name, "value"].mean()

                row_df_list.append(row)
    return row_df_list

def Average(lst):
    if len(lst) > 0:
        return sum(lst) / len(lst)
    return

def calculate_poi_cov_spatialite(poi_df, db_path, offset):
    df = poi_df.copy()
    import spatialite
    with spatialite.connect(db_path) as dbcon:
        for index, row in poi_df.iterrows():
            x = row["lon"]
            y = row["lat"]
            for rat in rat_to_table_and_primary_where_dict:
                cov_list = []
                try:
                    cov_list = dbcon.execute("SELECT {} FROM {} WHERE st_intersects(st_buffer(makepoint({},{}), {}), geom) limit 10".format(
                        rat_to_main_param_dict[rat], rat_to_table_and_primary_where_dict[rat], x, y, offset)).fetchall()
                    cov_list = [x[0] for x in cov_list]
                except Exception as e:
                    print(e)
                avg = Average(cov_list)
                print(avg)
                df.loc[index, rat_to_main_param_dict[rat]+"_average"] = avg
    return df

class calculate_poi(QDialog):
    on_result = pyqtSignal(object, object)
    def __init__(self, gc, apply_mode=True):
        super(calculate_poi, self).__init__(None)
        self.apply_mode = apply_mode
        self.radius = "1000"
        self.gc = gc
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
        self.offset_meters = int(self.radius)
        self.offset = azq_cell_file.METER_IN_WGS84 * self.offset_meters
        self.avg_col_list = []
        layer = QgsProject.instance().mapLayersByName(self.layer_name)[0]
        columns = [f.name() for f in layer.fields()]
        self.lon_col, self.lat_col = qgis_layers_gen.get_lon_lat_column_name(columns)
        columns = [column.lower() for column in columns]
        poi_list = []
        for feat in layer.getFeatures(QgsFeatureRequest().setFlags(QgsFeatureRequest.NoGeometry)):
            if isinstance(feat[self.lon_col], float) and isinstance(feat[self.lat_col], float):
                poi_list.append(dict(zip(columns, feat.attributes())))
        df = pd.DataFrame()
        cov_column_name_list = []
        print(self.offset)
        if self.gc.databasePath is not None:
            if os.name == "nt":
                row_df_list = []
                with contextlib.closing(sqlite3.connect(self.gc.databasePath)) as dbcon:
                    cov_df, cov_column_name_list = get_technology_df(dbcon, cov_column_name_list)
                    cov_df["lat"] = cov_df["geom"].apply(lambda x: geomToLatLon(x)[0])
                    cov_df["lon"] = cov_df["geom"].apply(lambda x: geomToLatLon(x)[1])
                    if len(poi_list) > 0:
                        row_df_list = calculate_poi_cov(poi_list, cov_df, cov_column_name_list, self.lat_col, self.lon_col, self.offset )
                    df = pd.DataFrame(row_df_list)
            else:
                poi_df = pd.DataFrame(poi_list)
                poi_df = poi_df.rename(columns={self.lat_col: "lat", self.lon_col: "lon"})
                df = calculate_poi_cov_spatialite(poi_df, self.gc.databasePath, self.offset)

        window_name = "Coverage " + str(self.offset_meters / 1000.0) + "km. around poi: " + self.layer_name
        self.on_result.emit(df, window_name)
