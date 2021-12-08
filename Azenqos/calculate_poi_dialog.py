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
    per_rat_df_list = []
    for rat in rat_to_table_and_primary_where_dict:
        try:
            sql = "select log_hash, time, geom, {} as value from {}".format(
                rat_to_main_param_dict[rat], rat_to_table_and_primary_where_dict[rat]
            )
            df = pd.read_sql(sql, dbcon, parse_dates=["Time"])
            df["name"] = rat_to_main_param_dict[rat]
            cov_column_name_list.append( rat_to_main_param_dict[rat])
            per_rat_df_list.append(df)
        except Exception as e:
            print("WARNING: gen per_rat_df failed:", e)
    df = pd.concat(per_rat_df_list, ignore_index=True)
    df.sort_values(["log_hash", "time"], inplace=True)
    df = df.loc[(df["geom"].notna()) & (df["value"].notna())].reset_index(drop=True)
    return df ,cov_column_name_list

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
        columns = [f.name() for f in layer.fields()] + ["geometry"]
        lon_col, lat_col = qgis_layers_gen.get_lon_lat_column_name(columns)
        row_list = []
        for feat in layer.getFeatures():
            row_list.append(dict(zip(columns, feat.attributes() + [feat.geometry().asWkt()])))
        df = pd.DataFrame(row_list, columns=columns)
        df.columns= df.columns.str.lower()
        df = df.drop(columns=[lon_col, lat_col])
        df["lon"] = df["geometry"].str.extract("\((\S+)\s", expand=False).astype(float)
        df["lat"] = df["geometry"].str.extract("\s(\S+)\)", expand=False).astype(float)
        df = df.drop(columns=["geometry"])
        df = df.dropna().reset_index(drop=True)
        df["radius"] = None
        self.df_columns = df.columns.tolist()
        cov_df_list = []
        cov_column_name_list = []
        
        if self.gc.databasePath is not None:
            with contextlib.closing(sqlite3.connect(self.gc.databasePath)) as dbcon:
                cov_df, cov_column_name_list = get_technology_df(dbcon, cov_column_name_list)
                cov_df["lat"] = cov_df["geom"].apply(lambda x: geomToLatLon(x)[0])
                cov_df["lon"] = cov_df["geom"].apply(lambda x: geomToLatLon(x)[1])
                if len(cov_df) > 0:
                    if self.apply_mode == True:
                        def filter_cov(row, cov_df, cov_column_name_list):
                            if row["lat"] is not None and row["lon"] is not None :
                                cov_df["poi_lat"] = row["lat"]
                                cov_df["poi_lon"] = row["lon"]
                                cov_df["dist"] = haversine(cov_df["poi_lat"], cov_df["poi_lon"], cov_df["lat"], cov_df["lon"]) * 1000.0
                                cov_df = cov_df.loc[cov_df["dist"] <= self.offset_meters]
                                for cov_column_name in cov_column_name_list:
                                    if len(cov_df) > 0:
                                        avg_cov_col = cov_column_name+"_average"
                                        if avg_cov_col not in self.avg_col_list:
                                            self.avg_col_list.append(avg_cov_col)
                                        row[avg_cov_col] = cov_df.loc[cov_df["name"] == cov_column_name, "value"].mean()
                                        row["radius"] = str(self.offset_meters / 1000.0) +"km."
                            return row
                        df = df.apply(lambda row: filter_cov(row, cov_df, cov_column_name_list), axis=1)
                        df = df[self.df_columns+self.avg_col_list]
                    else:
                        poi_df = df.reset_index()
                        cov_lon_df = cov_df.sort_values(by="lon").reset_index(drop=True)
                        poi_lon_df = poi_df.sort_values(by="lon").reset_index(drop=True)
                        cov_lat_df = cov_df.sort_values(by="lat").reset_index(drop=True)
                        poi_lat_df = poi_df.sort_values(by="lat").reset_index(drop=True)
                        df1 = pd.merge_asof(left=cov_lon_df, right=poi_lon_df, left_on=["lon"], right_on=["lon"] ,direction="nearest", allow_exact_matches=True, tolerance=self.offset, suffixes=("", "_not_use"))
                        df2 = pd.merge_asof(left=cov_lat_df, right=poi_lat_df, left_on=["lat"], right_on=["lat"] ,direction="nearest", allow_exact_matches=True, tolerance=self.offset, suffixes=("", "_not_use"))
                        df = df1.merge(df2, how="left", on="index", suffixes=("", "_not_use"))
                        print("df", df)

        df = df.loc[df["radius"].notna()].reset_index(drop=True)
        window_name = "Coverage" + self.radius + "m. around poi: " + self.layer_name
        self.on_result.emit(df, window_name)
