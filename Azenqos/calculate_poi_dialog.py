import PyQt5
from PyQt5.QtWidgets import QDialog, QComboBox, QCompleter
from PyQt5.uic import loadUi
from PyQt5.QtGui import QIcon, QPixmap, QIntValidator

try:
    from qgis.core import (
        QgsProject,
        QgsFeatureRequest,
    )
except:
    pass

import os
import contextlib
import sqlite3
import pandas as pd
import struct
from worker import Worker

import azq_cell_file
import azq_utils
import qgis_layers_gen
from add_param_dialog import CustomQCompleter

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

def geom_to_lat_lon(geomBlob):
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

def calculate_poi_cov(poi_list, cov_df, cov_column_name_list, lat_col, lon_col, offset, progress_signal):
    row_df_list = []
    
    len_poi =  len(poi_list)
    calculate_progress = 100/len_poi
    n = 0
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
            progress_signal.emit(int(calculate_progress*(n+1)))
            n += 1
            if len(cov_df_loc) > 0:
                for cov_column_name in cov_column_name_list:
                    avg_cov_col = cov_column_name+"_average"
                    row[avg_cov_col] = cov_df_loc.loc[cov_df_loc["name"] == cov_column_name, "value"].mean()

                row_df_list.append(row)
    df = pd.DataFrame(row_df_list)
    return df

def Average(lst):
    if len(lst) > 0:
        return sum(lst) / len(lst)
    return

def calculate_poi_cov_spatialite(poi_df, db_path, offset, progress_signal):
    df = poi_df.copy()
    import spatialite
    with contextlib.closing(spatialite.connect(db_path)) as dbcon:
        col_name_list = []
        n = 0
        for rat in rat_to_table_and_primary_where_dict:
            dbcon.execute("SELECT CreateSpatialIndex('{}', 'geom')".format(rat_to_table_and_primary_where_dict[rat]))
            progress_signal.emit(int(6*(n+1)))
            n += 1
            
        len_poi=  len(poi_df)
        calculate_progress = 76/len_poi
        for index, row in poi_df.iterrows():
            x = row["lon"]
            y = row["lat"]
            xmax = x+offset
            xmin = x-offset
            ymax = y+offset
            ymin = y-offset
            progress_signal.emit(int(calculate_progress*(index+1)+24))
            for rat in rat_to_table_and_primary_where_dict:
                avg = None
                try:
                    avg =  dbcon.execute("SELECT avg({}) FROM {} WHERE {}.ROWID IN (select ROWID from idx_{}_geom where xmin >= {} and xmin <= {} and ymin >= {} and Ymin <= {})".format(rat_to_main_param_dict[rat],rat_to_table_and_primary_where_dict[rat], rat_to_table_and_primary_where_dict[rat], rat_to_table_and_primary_where_dict[rat], xmin, xmax, ymin, ymax)).fetchone()
                except Exception as e:
                    print(e)
                col_name = rat_to_main_param_dict[rat]+"_average"
                if col_name not in col_name_list:
                    col_name_list.append(col_name)
                df.loc[index, col_name] = avg
        df = df.dropna(subset=col_name_list, how='all')
    return df

class calculate_poi(QDialog):
    def __init__(self, gc, result_signal, progress_signal):
        super(calculate_poi, self).__init__(None)
        self.radius = "1000"
        self.gc = gc
        self.result_signal = result_signal
        self.progress_signal = progress_signal
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
        self.progress_signal.emit(0)
        self.layer_name = self.ui.poiComboBox.currentText()
        self.radius = self.ui.radiusLineEdit.text()
        self.offset_meters = int(self.radius)
        self.offset = azq_cell_file.METER_IN_WGS84 * self.offset_meters
        self.avg_col_list = []
        layer = QgsProject.instance().mapLayersByName(self.layer_name)[0]
        columns = [f.name() for f in layer.fields()]
        self.lon_col, self.lat_col = qgis_layers_gen.get_lon_lat_column_name(columns)
        columns = [column.lower() for column in columns]
        self.poi_list = []
        for feat in layer.getFeatures(QgsFeatureRequest().setFlags(QgsFeatureRequest.NoGeometry)):
            if isinstance(feat[self.lon_col], float) and isinstance(feat[self.lon_col], float):
                self.poi_list.append(dict(zip(columns, feat.attributes())))
        self.cov_column_name_list = []
        if self.gc.databasePath is not None:
            if os.name == "nt":
                with contextlib.closing(sqlite3.connect(self.gc.databasePath)) as dbcon:
                    self.cov_df, self.cov_column_name_list = get_technology_df(dbcon, self.cov_column_name_list)
                    self.cov_df["lat"] = self.cov_df["geom"].apply(lambda x: geom_to_lat_lon(x)[0])
                    self.cov_df["lon"] = self.cov_df["geom"].apply(lambda x: geom_to_lat_lon(x)[1])
                    if len(self.poi_list) > 0:
                        worker = Worker(self.calculate_poi_window)
                        self.gc.threadpool.start(worker)
            else:
                self.poi_df = pd.DataFrame(self.poi_list)
                if len(self.poi_df) > 0:
                    self.poi_df = self.poi_df.rename(columns={self.lat_col: "lat", self.lon_col: "lon"})
                    worker = Worker(self.calculate_poi_linux)
                    self.gc.threadpool.start(worker)

    def calculate_poi_window(self):
        df = calculate_poi_cov(self.poi_list, self.cov_df, self.cov_column_name_list, self.lat_col, self.lon_col, self.offset, self.progress_signal)
        window_name = "Coverage " + str(self.offset / 1000.0) + "km. around poi: " + self.layer_name
        self.progress_signal.emit(100)
        self.result_signal.emit(df, window_name)

    def calculate_poi_linux(self):
        df = calculate_poi_cov_spatialite(self.poi_df, self.gc.databasePath, self.offset, self.progress_signal)
        window_name = "Coverage " + str(self.offset / 1000.0) + "km. around poi: " + self.layer_name
        self.progress_signal.emit(100)
        self.result_signal.emit(df, window_name)

