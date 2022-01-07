import contextlib
import json
import os
import signal
import sqlite3
import sys
import threading
import time
import traceback
import uuid
import pandas as pd
import numpy as np
from functools import partial
from datatable import TableWindow

from PyQt5.QtCore import pyqtSignal, QDir
from PyQt5.QtWidgets import (
    QWidget,
    QFileDialog,
    QMessageBox
)
from PyQt5.uic import loadUi

import azm_sqlite_merge
import azq_server_api
import azq_utils
import db_layer_task
import db_preprocess
import qt_utils
import import_db_dialog

signal.signal(signal.SIGINT, signal.SIG_DFL)  # exit upon ctrl-c


class server_overview_widget(QWidget):
    progress_update_signal = pyqtSignal(int)
    status_update_signal = pyqtSignal(str)
    apply_done_signal = pyqtSignal(str)

    def __init__(self, parent, gvars):
        super().__init__(parent)
        self.closed = False
        self.gvars = gvars
        self.setupUi()
        self.req_body = {}
        self.apply_thread = None
        self.overview_db_fp = None
        self.devices_selection_df = None
        self.main_params_only = True
        self.auto_zoom = True
        self.pre_create_index = False
        self.derived_dfs = None


    def setupUi(self):
        # keep incase thread calls self after closed - self.setAttribute(Qt.WA_DeleteOnClose)
        self.ui = loadUi(azq_utils.get_module_fp("server_overview_widget.ui"), self)
        title = "ภาพรวมผลการวัดสัญญาณ" if azq_utils.is_lang_th() else "Server logs overview"
        self.setWindowTitle(title)
        now = azq_utils.datetime_now()
        last_day = now.replace(month=12, day=31)
        first_day = now.replace(month=1, day=1)
        self.ui.start_dateEdit.setDateTime(first_day)
        self.ui.end_dateEdit.setDateTime(last_day)

        self.applyButton.clicked.connect(self.apply)
        self.apply_done_signal.connect(self.apply_done)
        self.progress_update_signal.connect(self.progress)
        self.status_update_signal.connect(self.status)
        self.ui.phone_filter_pushButton.clicked.connect(self.on_click_phone_filter)
        self.ui.group_filter_pushButton.clicked.connect(self.on_click_group_filter)
        self.ui.showDbStatsButton.clicked.connect(self.showDbStats)
        self.main_params_only_checkBox.setChecked(True)
        enable_main_params_slot = partial(self.use_main_params_only, self.main_params_only_checkBox)
        disable_main_params_slot = partial(self.use_all_params, self.main_params_only_checkBox)
        self.main_params_only_checkBox.stateChanged.connect(
            lambda x: enable_main_params_slot() if x else disable_main_params_slot()
        )
        self.auto_zoom_checkBox.setChecked(True)
        enable_auto_zoom_slot = partial(self.auto_zoom_enable, self.auto_zoom_checkBox)
        disable_auto_zoom_slot = partial(self.auto_zoom_disable, self.auto_zoom_checkBox)
        self.auto_zoom_checkBox.stateChanged.connect(
            lambda x: enable_auto_zoom_slot() if x else disable_auto_zoom_slot()
        )
        self.pre_create_index_checkBox.setChecked(False)
        enable_pre_create_index_slot = partial(self.pre_create_index_enable, self.pre_create_index_checkBox)
        disable_pre_create_index_slot = partial(self.pre_create_index_disable, self.pre_create_index_checkBox)
        self.pre_create_index_checkBox.stateChanged.connect(
            lambda x: enable_pre_create_index_slot() if x else disable_pre_create_index_slot()
        )
        self.select_theme_lineEdit.setText("Default")
        self.select_theme_pushButton.clicked.connect(self.choose_theme)
        self.apply_read_server_facts = True
        self.setMinimumSize(450, 250)
        self.apply()

    def use_main_params_only(self, checkbox):
        self.main_params_only = True

    def use_all_params(self, checkbox):
        self.main_params_only = False

    def auto_zoom_enable(self, checkbox):
        self.auto_zoom = True

    def auto_zoom_disable(self, checkbox):
        self.auto_zoom = False

    def pre_create_index_enable(self, checkbox):
        self.pre_create_index = True

    def pre_create_index_disable(self, checkbox):
        self.pre_create_index = False

    def choose_theme(self):
        fileName, _ = QFileDialog.getOpenFileName(
            self, "Select file", QDir.rootPath(), "*.xml"
        )
        self.select_theme_lineEdit.setText(
            fileName
        ) if fileName else self.select_theme_lineEdit.setText("Default")

    def on_processing(self, processing, processing_text="Processing..."):
        if processing:
            self.progress(0)
            self.ui.scrollArea.setVisible(False)
            self.ui.applyButton.setEnabled(False)
            self.ui.applyButton.setText(processing_text)
            self.ui.progressBar.setVisible(True)
        else:
            self.ui.scrollArea.setVisible(True)
            self.ui.applyButton.setText("Download")
            self.ui.applyButton.setEnabled(True)
            self.ui.progressBar.setVisible(False)

    def read_input_to_vars(self):
        self.req_body = {}
        self.req_body["start_date"] = self.ui.start_dateEdit.date().toPyDate().isoformat()  # becomes like '2021-09-30'
        self.req_body["end_date"] = self.ui.end_dateEdit.date().toPyDate().isoformat()
        self.start_date = self.ui.start_dateEdit.date().toPyDate()
        self.end_date = self.ui.end_dateEdit.date().toPyDate()
        self.req_body["bin"] = int(self.ui.samp_rate_comboBox.currentText())
        self.req_body["filters_dict"] = {}
        if (self.devices_selection_df.selected == False).any():
            mask = self.devices_selection_df.selected == True
            imei_list = self.devices_selection_df.loc[mask, "imei_number"].values.tolist()
            self.req_body["filters_dict"]["imei_list"] = imei_list
        lhl_str = self.ui.log_hash_filter_lineEdit.text().strip()
        if lhl_str:
            lhl = None
            if "," in lhl_str:
                lhl = lhl_str.split(",")
            else:
                lhl = [lhl_str]
            lhl = [x.strip() for x in lhl]
            for log_hash in lhl:
                int(log_hash)  # log_hash must be numbers
            self.req_body["filters_dict"]["log_hash_list"] = lhl
        print("read_input_to_vars: req_body:", self.req_body)

    def status(self, msg):
        self.ui.status_label.setText(msg)

    def progress(self, val):
        self.ui.progressBar.setValue(val)

    def on_click_phone_filter(self):
        df = self.devices_selection_df.drop_duplicates("imei_number")
        names = (df.alias+": "+df.imei_number).values
        selected = (df.selected).values
        selection_mask = qt_utils.ask_selection(self, names, selected, "Device selection", "Please select:", use_filter=True)
        if selection_mask is not None:
            df_selected = df.iloc[selection_mask]
            self.devices_selection_df["selected"] = False
            self.devices_selection_df.loc[self.devices_selection_df.imei_number.isin(df_selected.imei_number), "selected"] = True
            self.update_selection_lables()

    def on_click_group_filter(self):
        selected_df = self.devices_selection_df.query("selected == True")
        groups = list(self.devices_selection_df.group_name.dropna().unique())
        ori_selected_groups = list(selected_df.group_name.dropna().unique())
        print("groups:", groups)
        print("ori_selected_groups:", ori_selected_groups)
        ori_selected_mask = [g in ori_selected_groups for g in groups]
        print("ori_selected_mask:", ori_selected_mask)
        selection_mask = qt_utils.ask_selection(
            self,
            groups,
            ori_selected_mask,
            "Group selection",
            "Please select:",
            use_filter=True
        )
        if selection_mask is not None:
            for i in range(len(selection_mask)):
                selected = selection_mask[i]
                g = groups[i]
                self.devices_selection_df.loc[self.devices_selection_df.group_name == g, "selected"] = selected
            self.update_selection_lables()

    def update_selection_lables(self):
        if self.devices_selection_df is None:
            return
        n_devs = len(self.devices_selection_df.imei_number.unique())
        n_groups = len(list(self.devices_selection_df.group_name.dropna().unique()))
        selected_df = self.devices_selection_df.query("selected == True")
        self.ui.phone_filter_pushButton.setText("{}/{} Devices".format(len(selected_df.imei_number.unique()), n_devs))
        self.ui.group_filter_pushButton.setText("{}/{} Groups".format(len(list(selected_df.group_name.dropna().unique())), n_groups))

    def closeEvent(self, event):
        self.closed = True
        self.qgis_iface = None

    def apply_done(self, msg):
        self.on_processing(False)
        dur = azq_utils.timer_print("overview_apply")
        if not msg.startswith("SUCCESS"):
            qt_utils.msgbox(msg, "Server overview apply failed", parent=self)
            self.status(msg[:50])
        else:
            if self.apply_read_server_facts:
                bins = [str(x) for x in sorted(list(self.overview_list_df.bin.unique()), reverse=True)]
                self.ui.samp_rate_comboBox.addItems(bins)
                self.devices_selection_df = self.devices_df.copy(deep=True)
                self.devices_selection_df["selected"] = True
                self.update_selection_lables()
                self.apply_read_server_facts = False
                self.status("Read server facts... done in %.02f secs" % dur)
            else:
                if self.gvars.main_window:
                    self.gvars.main_window.add_map_layer()
                self.status("Adding layers to QGIS...")
                self.progress_update_signal.emit(90)
                if self.gvars.qgis_iface:
                    db_layer_task.ui_thread_add_layers_to_qgis(self.gvars, self.table_to_layer_dict, self.layer_id_to_visible_flag_dict, self.last_visible_layer)
                    db_layer_task.set_active_layer(self.gvars, layer_name="overview_lte_inst_rsrp_1")
                self.progress_update_signal.emit(100)
                self.status("Completed in %.02f secs \n(%s\n%s\n%s\n%s)" % (dur, self.db_download_time, self.combine_azm_time, self.prepare_views_time, self.create_layers_time))
                print("self.auto_zoom", self.auto_zoom)
                if self.auto_zoom:
                    self.gvars.main_window.trigger_zoom_to_active_layer()

    def apply(self):
        self.ui.status_label.setText("")
        if self.select_theme_lineEdit.text() != "Default" and not os.path.isfile(
            self.select_theme_lineEdit.text()
        ):
            QMessageBox.critical(
                None,
                "Theme file not found",
                "Please choose a theme xml to use...",
                QMessageBox.Cancel,
            )
            return
        import_db_dialog.check_theme(theme_fp = self.select_theme_lineEdit.text())
        self.on_processing(True)
        try:
            azq_utils.timer_start("overview_apply")
            self.overview_db_fp = None
            if not self.apply_read_server_facts:
                self.read_input_to_vars()
            self.apply_thread = threading.Thread(
                target=self.apply_worker_func, args=(), daemon=True
            )
            # daemon threads close when program closes
            self.apply_thread.start()
        except:
            type_, value_, traceback_ = sys.exc_info()
            exstr = str(traceback.format_exception(type_, value_, traceback_))
            msg = "WARNING: apply failed - exception: {}".format(exstr)
            print(msg)
            qt_utils.msgbox(msg, "Server overview", self)
            self.ui.status_label.setText(msg)
            self.on_processing(False)

    def showDbStats(self):
        print("self.overview_list_df", self.overview_list_df)
        print("len:", len(self.overview_list_df))
        df = self.overview_list_df.copy()
        df.rename(columns={"start_time":"gen_start_time","end_time":"gen_done_time"}, inplace=True)
        widget = TableWindow(
            self,
            "Server overview DB list",
            custom_df=df,
            gc=self.gvars
        )
        wd = WidgetDialog(widget, self)
        wd.resize(600,400)
        wd.exec()

    def apply_worker_func(self):
        try:
            assert self.gvars.is_logged_in()
            if self.closed:
                raise Exception("window closed")
            print("apply_worker_func: apply_read_server_facts:", self.apply_read_server_facts)
            if self.apply_read_server_facts:
                self.overview_list_df = azq_server_api.api_overview_db_list_df(
                    self.gvars.login_dialog.server,
                    self.gvars.login_dialog.token
                )
                self.devices_df = azq_server_api.api_device_list_df(
                    self.gvars.login_dialog.server,
                    self.gvars.login_dialog.token
                )
                self.apply_done_signal.emit("SUCCESS")
                return
            if self.closed:
                raise Exception("window closed")
            self.status_update_signal.emit("Preparing folder...")
            downloaded_db_fp = azq_utils.tmp_gen_fp("overview_{}.db".format(uuid.uuid4()))
            assert not os.path.isfile(downloaded_db_fp)
            self.status_update_signal.emit("Server processing data...")
            azq_utils.timer_start("overview_perf_dl_azm")
            db_download_start_time = time.perf_counter()

            if self.closed:
                raise Exception("window closed")
            downloaded_db_fp_is_json_resp = False
            json_resp = None
            if self.gvars.login_dialog.is_local_container_nw_server():
                self.req_body["target_dir"] = azq_utils.tmp_gen_new_subdir()
                downloaded_db_fp_is_json_resp = True

            if self.closed:
                raise Exception("window closed")
            ret = azq_server_api.api_overview_db_download(self.gvars.login_dialog.server, self.gvars.login_dialog.token, downloaded_db_fp,
                                                          req_body=self.req_body, signal_to_emit_stats=self.status_update_signal)   
            db_download_end_time = time.perf_counter()
            self.db_download_time =  "DB Download Time: %.02f seconds" % float(db_download_end_time-db_download_start_time)
            azq_utils.timer_print("overview_perf_dl_azm")
            if self.closed:
                raise Exception("window closed")

            print("ret:", ret)
            assert os.path.isfile(ret)
            assert os.path.isfile(downloaded_db_fp)
            if downloaded_db_fp_is_json_resp:
                print("downloaded_db_fp_is_json_resp - mv db file from uapi's tmp to our tmp - START downloaded_db_fp:", downloaded_db_fp)
                with open(downloaded_db_fp, "r") as f:
                    json_resp = json.loads(f.read())
                    assert "db_fps" in json_resp
                    assert len(json_resp["db_fps"]) == 1
                    downloaded_db_fp = json_resp["db_fps"][0]
                print("downloaded_db_fp_is_json_resp - mv db file from uapi's tmp to our tmp - DONE")
            if self.closed:
                raise Exception("window closed")

            self.progress_update_signal.emit(30)
            db_files = [downloaded_db_fp]  # uapi now rets direct and signle db, no zips
            azq_utils.timer_print("overview_perf_extract_azm")
            print("got dbs from server, len(db_files):", len(db_files), "at:", downloaded_db_fp)
            # combined all the db_files in the zip
            azq_utils.timer_start("overview_perf_combine_azm")
            combine_azm_start_time = time.perf_counter()
            self.status_update_signal.emit("Merging all db partitions from server...")
            dbfp = None
            if len(db_files) > 1:
                assert len(db_files) <= 2  # max now in server, for > 2 months combines it will use yearly db so there it would be 1 db file
                dbfp = azm_sqlite_merge.merge(db_files)
            else:
                dbfp = db_files[0]
            assert os.path.isfile(dbfp)
            self.gvars.databasePath = dbfp
            combine_azm_end_time = time.perf_counter()
            self.combine_azm_time =  "DB combine combine time: %.02f seconds" % float(combine_azm_end_time-combine_azm_start_time)
            azq_utils.timer_print("overview_perf_combine_azm")

            if self.closed:
                raise Exception("window closed")
            azq_utils.timer_start("overview_perf_prepare_views")
            prepare_views_start_time = time.perf_counter()
            self.status_update_signal.emit("Prepare db views as per theme...")
            self.progress_update_signal.emit(50)
            if os.name == "nt":
                with contextlib.closing(sqlite3.connect(dbfp)) as dbcon:
                    db_preprocess.prepare_spatialite_views(dbcon, main_rat_params_only=self.main_params_only, pre_create_index = False, cre_table=False, start_date=self.start_date, end_date=self.end_date, time_bin_secs=self.req_body["bin"])  # no need to handle log_hash time sync so no need cre_table flag (layer get attr would be empty if it is a view in clickcanvas)
            else:
                import spatialite
                with contextlib.closing(spatialite.connect(dbfp)) as dbcon:
                    db_preprocess.prepare_spatialite_views(dbcon, main_rat_params_only=self.main_params_only, pre_create_index=self.pre_create_index, cre_table=False, start_date=self.start_date, end_date=self.end_date, time_bin_secs=self.req_body["bin"])
            prepare_views_end_time = time.perf_counter()
            self.prepare_views_time =  "Prepare Views Time: %.02f seconds" % float(prepare_views_end_time-prepare_views_start_time)
            azq_utils.timer_print("overview_perf_prepare_views")
            if self.closed:
                raise Exception("window closed")
            azq_utils.timer_start("overview_perf_create_layers")
            create_layers_start_time = time.perf_counter()
            self.status_update_signal.emit("Processing layers/legends as per theme...")
            self.progress_update_signal.emit(70)
            self.overview_db_fp = dbfp
            if self.gvars.qgis_iface:
                self.table_to_layer_dict, self.layer_id_to_visible_flag_dict, self.last_visible_layer = db_layer_task.create_layers(
                    self.gvars, db_fp=self.overview_db_fp, display_name_prefix="overview_", gen_theme_bucket_counts=False, main_rat_params_only=self.main_params_only
                )
                self.gvars.overview_opened = True

            ############## create kpi stats layers if present
            # get all tables starting with
            with contextlib.closing(sqlite3.connect(dbfp)) as dbcon:
                map_imei_devices_df = self.devices_df.copy(deep=True)
                map_imei_devices_df = map_imei_devices_df[["imei_number","alias","group_name"]].groupby(["imei_number","alias"]).agg({"group_name": lambda x: list(x)}).reset_index()
                map_log_hash_imei_df = pd.read_sql("SELECT log_hash, log_imei FROM dumped_logs", dbcon)
                tables = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table' and name NOT LIKE 'sqlite_%';", dbcon).name
                has_kpi_tables = False
                for table in tables:
                    if self.closed:
                        raise Exception("window closed")
                    if table.startswith("kpi_"):
                        has_kpi_tables = True
                        self.status_update_signal.emit("Create KPI layer: {}".format(table))
                        tdf = pd.read_sql("select * from {}".format(table), dbcon)
                        layer = azq_utils.create_layer_in_qgis(None, tdf, table, add_to_qgis=False)
                        if layer is not None:
                            self.table_to_layer_dict[table] = layer
                            self.layer_id_to_visible_flag_dict[layer.id()] = False
                if self.closed:
                    raise Exception("window closed")
                if has_kpi_tables:
                    try:
                        self.status_update_signal.emit("Create Cell-wise stats...")
                        self.derived_dfs = gen_site_kpi_dfs(dbcon, self.status_update_signal, map_imei_devices_df=map_imei_devices_df, map_log_hash_imei_df=map_log_hash_imei_df)
                        self.status_update_signal.emit("Create Cell-wise stats... done")
                        if self.derived_dfs is not None:
                            for table, tdf in self.derived_dfs.items():
                                try:
                                    self.status_update_signal.emit("Creating Cell-wise layer: {}".format(table))
                                    layer = azq_utils.create_layer_in_qgis(None, tdf, table, add_to_qgis=False)
                                    if layer is not None:
                                        self.table_to_layer_dict[table] = layer
                                        self.layer_id_to_visible_flag_dict[layer.id()] = False
                                    self.status_update_signal.emit("Creating Cell-wise layer: {}... done".format(table))
                                except Exception as ce:
                                    self.status_update_signal.emit("Creating Cell-wise layer: {}... failed: {}".format(table, ce))
                                    type_, value_, traceback_ = sys.exc_info()
                                    exstr = str(traceback.format_exception(type_, value_, traceback_))
                                    print("WARNING: gen cell wise layer failed - exception: {}".format(exstr))
                        # calc example pass/fail report
                    except:
                        type_, value_, traceback_ = sys.exc_info()
                        exstr = str(traceback.format_exception(type_, value_, traceback_))
                        print("WARNING: gen derived table failed - exception: {}".format(exstr))
            ############## create kpi stats summary table if present

            create_layers_end_time = time.perf_counter()
            self.create_layers_time = "Create Layers Time: %.02f seconds" % float(
                create_layers_end_time - create_layers_start_time)
            azq_utils.timer_print("overview_perf_create_layers")

            if self.closed:
                raise Exception("window closed")
            self.status_update_signal.emit("DONE")
            self.progress_update_signal.emit(100)
            self.apply_done_signal.emit("SUCCESS")
            return 0
        except:
            type_, value_, traceback_ = sys.exc_info()
            exstr = str(traceback.format_exception(type_, value_, traceback_))
            msg = "FAILED - WARNING: download_overview failed - exception: {}".format(exstr)
            print(msg)
            self.apply_done_signal.emit(msg)
            return -1
        return -2

from PyQt5.QtWidgets import (QDialog, QVBoxLayout)
class WidgetDialog(QDialog):
    def __init__(self, widget, parent=None):
        super(WidgetDialog, self).__init__(parent)
        layout = QVBoxLayout(self)
        # nice widget for editing the date
        self.widget = widget
        layout.addWidget(self.widget)

def get_common_df_lh_time_stats_sr(cell_df):
    lh = None
    last_log_imei = None
    last_phone = None
    last_group = None
    time = None
    time_first = None
    lat = None
    lon = None
    lhl = []
    log_imei_list = []
    group_list = []
    phone_list = []
    if len(cell_df):
        idxmaxtime = cell_df["time"].idxmax()
        time_first = cell_df["time"].min()
        lh = cell_df.log_hash.loc[idxmaxtime]
        if "log_imei" in cell_df.columns:
            last_log_imei = cell_df.log_imei.loc[idxmaxtime]
        if "alias" in cell_df.columns:
            last_phone = cell_df.alias.loc[idxmaxtime]
        if "group_name" in cell_df.columns:
            last_group = cell_df.group_name.loc[idxmaxtime]
        time = cell_df.time.loc[idxmaxtime]
        lat = cell_df.lat.loc[idxmaxtime]
        lon = cell_df.lon.loc[idxmaxtime]
        lhl = cell_df.log_hash.unique()
        if "log_imei" in cell_df.columns:
            log_imei_list = cell_df.log_imei.unique()
        if "alias" in cell_df.columns:
            phone_list = cell_df.alias.unique()
        if "group_name" in cell_df.columns:
            group_list = list(set([item for sublist in cell_df.group_name.values.tolist() for item in sublist]))
    return pd.Series(
        {
            "log_hash": lh,
            "time": time,
            "last_log_imei": last_log_imei,
            "last_phone_name": last_phone,
            "last_group_name": ",".join(pd.Series(last_group).astype(str).values),
            "time_first": time_first,
            "lat": lat,
            "lon": lon,
            "n_samples": len(cell_df),
            "n_logs": len(lhl),
            "log_list": ",".join(pd.Series(lhl).astype(str).values),
            "log_imei_list": ",".join(pd.Series(log_imei_list).astype(str).values),
            "phone_list": ",".join(pd.Series(phone_list).astype(str).values),
            "group_list": ",".join(pd.Series(group_list).astype(str).values)
        }
    )


def gen_tp_stats_per_group(cell_df, tp_col):
    common_sr = get_common_df_lh_time_stats_sr(cell_df)
    max_tp = None
    max_tp_lh = None
    if len(cell_df):
        idxmax = cell_df[tp_col].idxmax()
        max_tp = cell_df[tp_col].loc[idxmax]
        max_tp_lh = cell_df.log_hash.loc[idxmax]
        kbps_to_mbps = True
        if tp_col.endswith("_mbps"):
            kbps_to_mbps = False
        if max_tp is not None and kbps_to_mbps:
            max_tp /= 1000.0
    return pd.concat(
        [
            common_sr,
            pd.Series(
                {
                    "max_tp_mbps": max_tp,
                    "max_tp_log_hash": max_tp_lh
                }
            )
        ]
    )


def gen_call_stats_per_group(cell_df, unused_param):
    common_sr = get_common_df_lh_time_stats_sr(cell_df)
    cssr = None
    n_init = None
    n_blocks = None
    n_drops = None
    n_end = None
    n_setup = None
    csd_avg = None
    csd_min = None
    csd_max = None
    if len(cell_df):
        n_init = len(cell_df)
        n_blocks = len(cell_df[cell_df.call_end_type == "Call Block"])
        n_drops = len(cell_df[cell_df.call_end_type == "Call Drop"])
        n_end = len(cell_df[cell_df.call_end_type == "Call End"])
        n_setup = len(cell_df[pd.notnull(cell_df.call_setup_time) | pd.notnull(cell_df.call_established_time)])
        csd_avg = cell_df.call_setup_duration.mean()
        csd_max = cell_df.call_setup_duration.max()
        csd_min = cell_df.call_setup_duration.min()
    if n_init:
        cssr = (n_setup*100.0)/n_init
    return pd.concat(
        [
            common_sr,
            pd.Series(
                {
                "cssr": cssr,
                "csd_avg": csd_avg,
                "csd_min": csd_min,
                "csd_max": csd_max,
                "n_init": n_init,
                "n_setup": n_setup,
                "n_blocks": n_blocks,
                "n_drops": n_drops,
                "n_end": n_end,
                }
            )
        ]
    )


def gen_dur_stats_per_group(cell_df, dur_col):
    cell_df = cell_df[pd.notnull(cell_df[dur_col])]  # rm empty rows
    common_sr = get_common_df_lh_time_stats_sr(cell_df)
    max_dur = None
    max_dur_lh = None
    min_dur = None
    min_dur_lh = None
    avg_dur = None
    if len(cell_df):
        idxmax = cell_df[dur_col].idxmax()
        idxmin = cell_df[dur_col].idxmin()
        max_dur = cell_df[dur_col].loc[idxmax]
        max_dur_lh = cell_df.log_hash.loc[idxmax]
        min_dur = cell_df[dur_col].loc[idxmin]
        min_dur_lh = cell_df.log_hash.loc[idxmin]
        avg_dur = cell_df[dur_col].mean()
    return pd.concat(
        [
            common_sr,
            pd.Series(
                {
                    "avg_dur": avg_dur,
                    "max_dur": max_dur,
                    "max_dur_log_hash": max_dur_lh,
                    "min_dur": min_dur,
                    "min_dur_log_hash": min_dur_lh,
                }
            )
        ]
    )


def print_and_emit(msg, update_signal=None):
    print(msg)
    update_signal.emit(msg) if update_signal is not None else None


def gen_site_kpi_dfs(dbcon, update_signal=None, raise_if_failed=False, map_imei_devices_df=None, map_log_hash_imei_df=None):
    ret = {}
    tables = list(pd.read_sql("SELECT name FROM sqlite_master WHERE type='table' and name NOT LIKE 'sqlite_%';", dbcon).name)
    #print("tables:", tables)

    kpi_table_to_apply_func_and_param = {
        "kpi_ims_reg": (gen_dur_stats_per_group, "duration"),
        "kpi_attach": (gen_dur_stats_per_group, "dur"),
        "kpi_detach": (gen_dur_stats_per_group, "dur"),
        "kpi_fdd_to_tdd": (gen_dur_stats_per_group, "duration"),
        "kpi_ftp_dl": (gen_tp_stats_per_group, "ftp_dl"),
        "kpi_ftp_ul": (gen_tp_stats_per_group, "ftp_ul"),
        "kpi_gsm_to_lte": (gen_dur_stats_per_group, "duration"),
        "kpi_interfreq": (gen_dur_stats_per_group, "duration"),
        "kpi_intersite": (gen_dur_stats_per_group, "duration"),
        "kpi_intersite_volte": (gen_dur_stats_per_group, "duration"),
        "kpi_intrasite": (gen_dur_stats_per_group, "duration"),
        "kpi_intrasite_volte": (gen_dur_stats_per_group, "duration"),
        "kpi_lte_to_gsm": (gen_dur_stats_per_group, "duration"),
        "kpi_ping_rtt": (gen_dur_stats_per_group, "ping_rtt_each"),
        "kpi_ping_rtp": (gen_dur_stats_per_group, "prev_time_diff_rx_mute"),
        "kpi_srvcc": (gen_dur_stats_per_group, "duration_millis"),
        "kpi_tdd_to_fdd": (gen_dur_stats_per_group, "duration"),
    }
    for t in ["kpi_csfb", "kpi_csfb_gsm", "kpi_volte"]:
        kpi_table_to_apply_func_and_param[t] = (gen_call_stats_per_group, None)

    nt = len(kpi_table_to_apply_func_and_param)
    it = 0
    for table, fp in kpi_table_to_apply_func_and_param.items():
        if table in tables:
            it += 1
            try:
                print_and_emit("Calc site-wise stats for {} [{}/{}]".format(table, it, nt), update_signal)
                afunc, aparam = fp
                #assert map_imei_devices_df is not None
                #assert map_log_hash_imei_df is not None
                df = get_table_df_gb_lte_sib1_enbid(table, dbcon, map_imei_devices_df=map_imei_devices_df, map_log_hash_imei_df=map_log_hash_imei_df).apply(
                    lambda cell_df: afunc(cell_df, aparam)
                )
                df = df.drop(["lte_sib1_mcc", "lte_sib1_mnc", "lte_sib1_tac", "lte_sib1_enb_id"], axis=1, errors='ignore')
                df = df.reset_index()
                new_table_name = table.replace("kpi_", "site_kpi_", 1)

                if new_table_name == "site_kpi_volte":
                    df["criteria_n_init_above_5"] = df.n_init > 5
                    df["criteria_cssr_above_95"] = df.cssr > 95
                    df["criteria_drop_rate_less_5"] = ((df.n_drops*100.0)/df.n_init) < 5
                    df["criterias_passed"] = df["criteria_n_init_above_5"] & df["criteria_cssr_above_95"] & df["criteria_drop_rate_less_5"]
                elif new_table_name == "site_kpi_ftp_dl":
                    df["criteria_max_tp_above_15_mbps"] = df.max_tp_mbps > 5
                    df["criterias_passed"] = df["criteria_max_tp_above_15_mbps"]

                ret[new_table_name] = df
            except Exception as ex:
                if raise_if_failed:
                    raise ex
                type_, value_, traceback_ = sys.exc_info()
                exstr = str(traceback.format_exception(type_, value_, traceback_))
                print("WARNING: gen_cell_stats_dfs table: {} failed - exception: {}".format(table, exstr))

    return ret


def get_table_df_gb_lte_sib1_enbid(table, dbcon, map_imei_devices_df=None, map_log_hash_imei_df=None):
    df = pd.read_sql("select * from {}".format(table), dbcon, parse_dates=["time"])
    df["log_hash"] = df["log_hash"].astype(np.int64)
    if map_log_hash_imei_df is not None:
        df = df.merge(map_log_hash_imei_df, left_on="log_hash", right_on='log_hash')
    if map_imei_devices_df is not None:
        df = df.merge(map_imei_devices_df, left_on="log_imei", right_on='imei_number')
    gb = df.groupby(["lte_sib1_mcc", "lte_sib1_mnc", "lte_sib1_tac", "lte_sib1_enb_id"], as_index=False)
    return gb

