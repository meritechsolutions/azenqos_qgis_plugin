import os
import signal
import sys
import threading
import traceback
import uuid

import pandas as pd
from PyQt5.QtCore import (
    Qt,
)
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import (
    QWidget, QFileDialog, QInputDialog,
)
from PyQt5.uic import loadUi
from qgis._core import QgsProject, QgsVectorFileWriter

import azq_server_api
import azq_utils
import qt_utils

signal.signal(signal.SIGINT, signal.SIG_DFL)  # exit upon ctrl-c
REQUIRED_COL_ALT_NAMES = {
    "band": ["lte_band_1"],
    "lat": ["positioning_lat", "latitude", "y"],
    "lon": ["positioning_lon", "longitude", "x"]
}
MAX_PREDICT_POINTS = 100 * 1000

class predict_widget(QWidget):
    progress_update_signal = pyqtSignal(int)
    status_update_signal = pyqtSignal(str)
    apply_done_signal = pyqtSignal(str)
    server_fact_read_done_signal = pyqtSignal(str)

    def __init__(self, parent, gvars):
        super().__init__(parent)
        self.title = "AI - Server predict"
        self.gvars = gvars
        self.setupUi()
        self.config = {}
        self.apply_thread = None
        self.overview_db_fp = None
        self.closed = False
        if self.gvars.main_window is not None:
            self.gvars.main_window.reg_map_tool_click_point(self.map_tool_click_point)

    def setupUi(self):
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.ui = loadUi(azq_utils.get_module_fp("server_predict_widget.ui"), self)
        self.setWindowTitle("Server AI prediction")
        self.ui.mode_combo.addItems(["Single point", "Multi point from CSV", "Multi point from QGIS Layer"])
        self.ui.lat_lon_le.setText(azq_utils.read_settings_file("prev_predict_lat_lon"))
        self.ui.band_le.setText(azq_utils.read_settings_file("prev_predict_band"))

        self.ui.mode_combo.currentIndexChanged.connect(self.on_input_mode_changed)
        self.applyButton.clicked.connect(self.apply)
        self.apply_done_signal.connect(self.apply_done)
        self.progress_update_signal.connect(self.progress)
        self.status_update_signal.connect(self.status)
        self.apply_read_server_facts = True
        self.setMinimumSize(320,350)
        self.apply()

    def on_input_mode_changed(self):
        if self.ui.mode_combo.currentIndex() == 0:
            self.ui.lat_lon_le.setEnabled(True)
            self.ui.band_le.setEnabled(True)
        else:
            self.ui.lat_lon_le.setEnabled(False)
            self.ui.band_le.setEnabled(False)

    def map_tool_click_point(self, point, button):
        print("predict_widget map_tool_click_point:", point)
        if point is not None and not self.closed:
            self.ui.lat_lon_le.setText("{},{}".format(point.y(), point.x()))

    def on_processing(self, processing, processing_text="Processing..."):
        if processing:
            self.progress(0)
            self.ui.groupBox.setVisible(False)
            self.ui.groupBox_2.setVisible(False)
            self.ui.applyButton.setEnabled(False)
            self.ui.applyButton.setText(processing_text)
            self.ui.progressBar.setVisible(True)
        else:
            self.ui.groupBox.setVisible(True)
            self.ui.groupBox_2.setVisible(True)
            self.ui.applyButton.setText("Predict")
            self.ui.applyButton.setEnabled(True)
            self.ui.progressBar.setVisible(False)

    def read_input_to_vars(self):
        assert self.gvars.is_logged_in()
        self.config = {}
        self.input_df = None

        self.model = self.models_df.iloc[self.ui.model_combo.currentIndex()]
        print("self.model:", self.model)

        if self.ui.mode_combo.currentIndex() == 0: # single input
            self.config["lat_lon"] = self.ui.lat_lon_le.text().strip()  # becomes like '2021-09-30'
            if not self.config["lat_lon"]:
                raise Exception("Lat, Lon not specified")
            if not "," in self.config["lat_lon"]:
                raise Exception("Lat,Lon field needs to have a comma: ,")
            parts = self.config["lat_lon"].strip().split(",")
            if not len(parts) == 2:
                raise Exception("Lat,Lon field needs to have only 2 values splitted by comma")
            azq_utils.write_settings_file("prev_predict_lat_lon", self.config["lat_lon"])
            self.config["lat"] = float(parts[0].strip())
            self.config["lon"] = float(parts[1].strip())
            self.config["band"] = self.ui.band_le.text().strip()
            if not self.config["band"]:
                raise Exception("Band not specified")
            azq_utils.write_settings_file("prev_predict_band", self.config["band"])
            self.config["band"] = int(self.config["band"])
            self.input_df = pd.DataFrame(
                {
                    "band":[self.config["band"]],
                    "lat":[self.config["lat"]],
                    "lon":[self.config["lon"]]
                }
            )
            print("self.input_df:", self.input_df)
        elif self.ui.mode_combo.currentIndex() == 1: # csv file
            fp, _ = QFileDialog.getOpenFileName(
                self, "lat/lon/band CSV for prediction", "", "*.csv"
            )
            self.predict_csv(fp)
        elif self.ui.mode_combo.currentIndex() == 2:  # from qgis layers
            project = QgsProject.instance()
            layer_name_to_layer = {}
            for (id_l, layer) in project.mapLayers().items():
                if layer.type() == layer.VectorLayer:
                    layer_name_to_layer[layer.name()] = layer
            print("layers:", layer_name_to_layer.keys())
            if len(layer_name_to_layer):
                items = layer_name_to_layer.keys()
                item, ok = QInputDialog.getItem(self, "Predict from route of existing layer",
                "Choose existing layer", items, 0, False)
                if ok and item:
                    fp = azq_utils.tmp_gen_fp("tmp_layer_csv_{}.csv".format(uuid.uuid4()))
                    assert not os.path.isfile(fp)
                    QgsVectorFileWriter.writeAsVectorFormat(layer_name_to_layer[item], fp, "utf-8", driverName="CSV", layerOptions=['GEOMETRY=AS_XYZ'])
                    assert os.path.isfile(fp)
                    self.predict_csv(fp)
                else:
                    return
            else:
                qt_utils.msgbox("No vector layers present", "No layers", self)
                return
        assert self.input_df is not None
        assert len(self.input_df)
        if len(self.input_df) > MAX_PREDICT_POINTS:
            raise Exception("Too many points: {} vs max {}".format(len(self.input_df), MAX_PREDICT_POINTS))
        print("read_input_to_vars: config:", self.config)

    def predict_csv(self, fp, band=None):
        if not fp:
            return
        if not os.path.isfile(fp):
            qt_utils.msgbox("File not found: {}".format(fp), "File not found", self)
            return
        df = pd.read_csv(fp)
        if len(df) == 0:
            qt_utils.msgbox("data has no rows", "Empty data", self)
            return
        cols = df.columns
        cols = [col.lower() for col in cols]
        df.columns = cols
        print("cols pre ren:", df.columns)
        required_cols = set(REQUIRED_COL_ALT_NAMES.keys())
        for rq in required_cols:
            if rq not in df.columns:
                alt_names = REQUIRED_COL_ALT_NAMES[rq]
                for alt_name in alt_names:
                    if alt_name in df.columns:
                        df.rename(columns={alt_name:rq}, inplace=True)
        print("cols post ren:", df.columns)
        if "band" not in df.columns:
            band = qt_utils.ask_text(self, "Band for prediction", "Please input the Band").strip()
            band = int(band)
            df["band"] = band
        assert "band" in df.columns
        if band is not  None:
            df["band"] = band
        for col in required_cols:
            if col not in df.columns:
                qt_utils.msgbox("Required column not present: {} in file:\n{}".format(col, fp), "Column missing", self)
                return
            try:
                df[col] = pd.to_numeric(df[col])
            except:
                type_, value_, traceback_ = sys.exc_info()
                exstr = str(traceback.format_exception(type_, value_, traceback_))
                msg = "WARNING: to_numeric failed - exception: {}".format(exstr)
                qt_utils.msgbox("Required column not numeric: {} in file:\n{}\nexception:{}".format(col, fp, msg), "Not numbers", self)
                print(msg)
                return
            null_mask = pd.isnull(df[col])
            if null_mask.any():
                first_row = null_mask[null_mask == True].iloc[0]
                qt_utils.msgbox("Required column {} has empty/missing field at row number: {} in file:\n{}".format(col, first_row, fp),
                                "Missing values", self)
                return
        self.input_df = df

    def status(self, msg):
        self.ui.status_label.setText(msg)

    def progress(self, val):
        self.ui.progressBar.setValue(val)

    def apply_done(self, msg):
        self.on_processing(False)
        if not msg.startswith("SUCCESS"):
            qt_utils.msgbox(msg, "Apply failed", parent=self)
            self.status(msg[:20])
        else:
            if self.apply_read_server_facts:
                self.apply_read_server_facts = False
                models_df = self.models_df
                models_df = sort_models_df(models_df)
                models = models_df.apply(model_row_to_text_sum, axis=1)
                print("models:", models)
                self.ui.model_combo.addItems(models)
            else:
                if self.ret_df is not None and len(self.ret_df) and not (pd.isnull(self.ret_df[self.model.param])).all():
                    self.ui.result_text.setHtml(msg)
                    self.status("Adding prediction to QGIS...")
                    assert "lat" in self.ret_df.columns
                    azq_utils.create_layer_in_qgis(None, self.ret_df, "prediction_"+model_row_to_text_sum(self.model), theme_param=self.model.param)
                    assert "lon" in self.ret_df.columns
                    self.status("Adding prediction to QGIS... done")
                else:
                    msg = "Failed - there were likely no tests done near your target prediction areas.\nTip: Try use a 'combined' model."
                    print(msg)
                    qt_utils.msgbox(msg, "failed", self)
                    self.ui.result_text.setHtml(msg)
                    return

    def apply(self):
        self.ui.status_label.setText("")
        self.ui.result_text.setText("")
        self.on_processing(True)
        try:
            self.overview_db_fp = None
            if self.apply_read_server_facts:
                self.on_processing(True, processing_text="Reading server data...")
            else:
                self.read_input_to_vars()
            self.ret_df = None
            self.apply_thread = threading.Thread(
                target=self.apply_worker_func, args=(),
                daemon=True
            )
            # daemon threads close when program closes
            self.apply_thread.start()
        except:
            type_, value_, traceback_ = sys.exc_info()
            exstr = str(traceback.format_exception(type_, value_, traceback_))
            msg = "WARNING: apply failed - exception: {}".format(exstr)
            print(msg)
            qt_utils.msgbox(msg, "Failed", self)
            self.ui.result_text.setText(msg)
            self.on_processing(False)


    def apply_worker_func(self):
        try:
            assert self.gvars.is_logged_in()
            if self.apply_read_server_facts:
                if not self.gvars.is_logged_in():
                    raise Exception("Please login to server first")
                    # avail server samplings
                models_df = azq_server_api.api_predict_models_list_df(
                    self.gvars.login_dialog.server,
                    self.gvars.login_dialog.token
                )
                print("models_df:", models_df)
                self.models_df = models_df
                print("models_df:", models_df)
                result_text = "SUCCESS - server ai models list read successfully."
            else:
                assert self.input_df is not None
                assert len(self.input_df)
                self.status_update_signal.emit("Asking server for prediction...")
                self.progress_update_signal.emit(0)
                body_dict = {
                "y":int(self.model.y),
                "m":int(self.model.m),
                "grid_size_meters":int(self.model.grid_size_meters),
                "bin":int(self.model.bin),
                "param": self.model.param,
                "lat": self.input_df.lat.values.tolist(),
                "lon": self.input_df.lon.values.tolist(),
                "band": self.input_df.band.values.tolist()
                }
                self.ret_df = azq_server_api.api_predict_df(
                    self.gvars.login_dialog.server,
                    self.gvars.login_dialog.token,
                    body_dict=body_dict
                )
                invalid_geom_mask = (self.ret_df.lat == 0.0) & (self.ret_df.lon == 0.0)
                self.ret_df.loc[invalid_geom_mask, "lat"] = None
                self.ret_df.loc[invalid_geom_mask, "lon"] = None
                self.ret_df.loc[invalid_geom_mask, "param"] = None
                assert self.model.param in self.ret_df.columns
                n = len(self.ret_df)
                head_n = 100
                if n < head_n:
                    head_n = n
                result_text = """SUCCESS
                <br/>
                 <b>AI Model:</b> {} - server: {}
                 <br/>
                 <br/>
                 <b>Results:</b> n_rows: {}, showing first {} rows:             
                 {}
                 <br/>
                 <br/>
                 <b>Stats:</b>             
                 {}
                 <br/>
                 <br/> 
                 For all samples please see/export the attribute table of the created qgis layer.
                """.format(model_row_to_text_sum(self.model), self.gvars.login_dialog.server, n, head_n, self.ret_df.head(head_n).to_html(), self.ret_df.describe().to_html())
                self.progress_update_signal.emit(100)
            self.apply_done_signal.emit(result_text)
            return 0
        except:
            type_, value_, traceback_ = sys.exc_info()
            exstr = str(traceback.format_exception(type_, value_, traceback_))
            msg = "WARNING: download_overview failed - exception: {}".format(exstr)
            self.apply_done_signal.emit("FAILED: "+msg)
            return -1
        return -2

    def closeEvent(self, event):
        if self.gvars.main_window is not None:
            self.gvars.main_window.dereg_map_tool_click_point(self.map_tool_click_point)
        self.closed = True

def sort_models_df(models_df):
    models_df["rat_g"] = models_df.param.apply(lambda param: param_to_rat_g(param))
    models_df = models_df.sort_values(["y", "m", "rat_g", "grid_size_meters"], ascending=[False, False, False, True])
    return models_df

def model_row_to_text_sum(row):
    ret = "{}G_{}_{}-{} ({} logs) {}".format(int(row.rat_g), row.param.replace("_1", ""), "%04d" % int(row.y), "%02d" % int(row.m) if row.m != 0 else "whole_year", row.n_logs,
                                    "combined model" if row.grid_size_meters == -1 else "model per grid: {} m.".format(
                                        row.grid_size_meters))

    return ret


def param_to_rat_g(param):
    if param.startswith("lte_"):
        return 4
    if param.startswith("wcdma_"):
        return 3
    if param.startswith("nr_"):
        return 5
    if param.startswith("gsm_"):
        return 2
    return -1