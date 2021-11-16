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
        self.select_theme_lineEdit.setText("Default")
        self.select_theme_pushButton.clicked.connect(self.choose_theme)
        self.apply_read_server_facts = True
        self.setMinimumSize(403, 500)
        self.apply()

    def use_main_params_only(self, checkbox):
        self.main_params_only = True

    def use_all_params(self, checkbox):
        self.main_params_only = False

    def auto_zoom_enable(self, checkbox):
        self.auto_zoom = True

    def auto_zoom_disable(self, checkbox):
        self.auto_zoom = False

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
            self.ui.groupBox.setVisible(False)
            self.ui.applyButton.setEnabled(False)
            self.ui.applyButton.setText(processing_text)
            self.ui.progressBar.setVisible(True)
        else:
            self.ui.groupBox.setVisible(True)
            self.ui.applyButton.setText("Download")
            self.ui.applyButton.setEnabled(True)
            self.ui.progressBar.setVisible(False)

    def read_input_to_vars(self):
        self.req_body = {}
        self.req_body["start_date"] = self.ui.start_dateEdit.date().toPyDate().isoformat()  # becomes like '2021-09-30'
        self.req_body["end_date"] = self.ui.end_dateEdit.date().toPyDate().isoformat()
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
            combine_azm_end_time = time.perf_counter()
            self.combine_azm_time =  "Combine azm Time: %.02f seconds" % float(combine_azm_end_time-combine_azm_start_time)
            azq_utils.timer_print("overview_perf_combine_azm")

            if self.closed:
                raise Exception("window closed")
            azq_utils.timer_start("overview_perf_prepare_views")
            prepare_views_start_time = time.perf_counter()
            self.status_update_signal.emit("Prepare db views as per theme...")
            self.progress_update_signal.emit(50)
            with contextlib.closing(sqlite3.connect(dbfp)) as dbcon:
                db_preprocess.prepare_spatialite_views(dbcon, main_rat_params_only=self.main_params_only, cre_table=False, start_date=self.req_body["start_date"], end_date=self.req_body["end_date"])  # no need to handle log_hash time sync so no need cre_table flag (layer get attr would be empty if it is a view in clickcanvas)
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
            create_layers_end_time = time.perf_counter()
            self.create_layers_time =  "Create Layers Time: %.02f seconds" % float(create_layers_end_time-create_layers_start_time)
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

    
