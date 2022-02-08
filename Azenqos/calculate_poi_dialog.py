import PyQt5
from PyQt5.QtWidgets import QDialog, QComboBox, QCompleter
from PyQt5.uic import loadUi
from PyQt5.QtGui import QIcon, QPixmap, QIntValidator

try:
    from qgis.utils import (
        spatialite_connect
    )
    from qgis.core import (
        QgsProject,
        QgsFeatureRequest,
    )
except:
    pass

import os
import contextlib
import pandas as pd
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
rat_to_main_param_list_dict = {
    "NR": ["nr_servingbeam_ss_rsrp_1", "nr_servingbeam_ss_rsrq_1", "nr_servingbeam_ss_sinr_1"],
    "LTE": ["lte_inst_rsrp_1", "lte_inst_rsrq_1", "lte_sinr_1"],
    "WCDMA": ["wcdma_aset_ecio_1", "wcdma_aset_rscp_1"],
    "GSM": ["gsm_rxlev_sub_dbm", "gsm_rxqual_sub"],
}
other_table_param_dict = {
    "ping": ["ping_rtt"],
    "android_info_1sec": ["data_trafficstat_dl_mbps", "data_trafficstat_ul_mbps"],
}

def calculate_poi_cov_spatialite(poi_df, db_path, offset, progress_signal):
    df = poi_df.copy()
    with contextlib.closing(spatialite_connect(db_path)) as dbcon:
        col_name_list = []
        count_col_name_list = []
        existing_rat_list = []
        existing_other_table_list = []
        for rat in rat_to_table_and_primary_where_dict:
            try:
                dbcon.execute("select ROWID from idx_{}_geom limit 1".format(rat_to_table_and_primary_where_dict[rat])).fetchone()
            except:
                try:
                    dbcon.execute("SELECT CreateSpatialIndex('{}', 'geom')".format(rat_to_table_and_primary_where_dict[rat]))
                except:
                    pass
        
        for table in other_table_param_dict:
            try:
                dbcon.execute("select ROWID from idx_{}_geom limit 1".format(table)).fetchone()
            except:
                try:
                    dbcon.execute("SELECT CreateSpatialIndex('{}', 'geom')".format(table))
                except:
                    pass
        
        for rat in rat_to_table_and_primary_where_dict:
            try:
                dbcon.execute("select ROWID from idx_{}_geom limit 1".format(rat_to_table_and_primary_where_dict[rat])).fetchone()
                existing_rat_list.append(rat)
            except:
                pass
        
        for table in other_table_param_dict:
            try:
                dbcon.execute("select ROWID from idx_{}_geom limit 1".format(table)).fetchone()
                existing_other_table_list.append(table)
            except:
                pass
            
        len_poi=  len(poi_df)
        calculate_progress = 100/len_poi
        for index, row in poi_df.iterrows():
            x = row["lon"]
            y = row["lat"]
            xmax = x+offset
            xmin = x-offset
            ymax = y+offset
            ymin = y-offset
            progress_signal.emit(int(calculate_progress*(index+1)))
            if len(existing_rat_list) > 0:
                for rat in existing_rat_list:
                    avg = []
                    avg_sql_list = []
                    for main_param in rat_to_main_param_list_dict[rat]:
                        avg_sql_list.append("avg({}), count({})".format(main_param, main_param))
                    try:
                        avg =  dbcon.execute("SELECT {} FROM {} WHERE {}.ROWID IN (select ROWID from idx_{}_geom where xmin >= {} and xmin <= {} and ymin >= {} and Ymin <= {})".format(",".join(avg_sql_list), rat_to_table_and_primary_where_dict[rat], rat_to_table_and_primary_where_dict[rat], rat_to_table_and_primary_where_dict[rat], xmin, xmax, ymin, ymax)).fetchone()
                    except Exception as e:
                        print(e)
                    n = 0
                    if len(avg) > 0:
                        for main_param in rat_to_main_param_list_dict[rat]:
                            avg_col_name = main_param+"_average"
                            count_col_name = main_param+"_count"
                            if avg[n] is not None and avg[n+1] > 0:
                                if avg_col_name not in col_name_list:
                                    col_name_list.append(avg_col_name)
                                if count_col_name not in col_name_list:
                                    col_name_list.append(count_col_name)
                                    count_col_name_list.append(count_col_name)
                                df.loc[index, avg_col_name] = avg[n]
                            n += 1
                            if avg[n] is not None and avg[n] > 0:
                                df.loc[index, count_col_name] = avg[n]
                            n += 1
            if len(existing_other_table_list) > 0:
                for table in existing_other_table_list:
                    avg_sql_list = []
                    for main_param in other_table_param_dict[table]:
                        avg_sql_list.append("avg({}), count({})".format(main_param, main_param))
                    try:
                        avg =  dbcon.execute("SELECT {} FROM {} WHERE {}.ROWID IN (select ROWID from idx_{}_geom where xmin >= {} and xmin <= {} and ymin >= {} and Ymin <= {})".format(",".join(avg_sql_list), table, table, table, xmin, xmax, ymin, ymax)).fetchone()
                    except Exception as e:
                        print(e)
                    n = 0
                    if len(avg) > 0:
                        for main_param in other_table_param_dict[table]:
                            avg_col_name = main_param+"_average"
                            count_col_name = main_param+"_count"
                            if avg[n] is not None and avg[n+1] > 0:
                                if avg_col_name not in col_name_list:
                                    col_name_list.append(avg_col_name)
                                if count_col_name not in col_name_list:
                                    col_name_list.append(count_col_name)
                                    count_col_name_list.append(count_col_name)
                                df.loc[index, avg_col_name] = avg[n]
                            n += 1
                            if avg[n] is not None and avg[n] > 0:
                                df.loc[index, count_col_name] = avg[n]
                            n += 1
        if set(col_name_list).issubset(df.columns):
            df = df.dropna(subset=col_name_list, how='all')
            df[count_col_name_list] = df[count_col_name_list].fillna(0).astype(int)
        else:
            df = pd.DataFrame(columns=df.columns)
    return df

class calculate_poi(QDialog):
    def __init__(self, gc, result_signal, progress_signal, open_signal):
        super(calculate_poi, self).__init__(None)
        self.radius = "1000"
        self.gc = gc
        self.result_signal = result_signal
        self.progress_signal = progress_signal
        self.open_signal = open_signal
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
        self.open_signal.emit()
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
            self.poi_df = pd.DataFrame(self.poi_list)
            if len(self.poi_df) > 0:
                self.poi_df = self.poi_df.rename(columns={self.lat_col: "lat", self.lon_col: "lon"})
                worker = Worker(self.calculate_poi)
                self.gc.threadpool.start(worker)

    def calculate_poi(self):
        df = calculate_poi_cov_spatialite(self.poi_df, self.gc.databasePath, self.offset, self.progress_signal)
        window_name = "Coverage " + str(self.offset_meters / 1000.0) + "km. around poi: " + self.layer_name
        self.progress_signal.emit(100)
        self.result_signal.emit(df, window_name)

