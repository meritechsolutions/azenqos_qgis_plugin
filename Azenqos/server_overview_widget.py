import contextlib
import datetime
import glob
import os
import signal
import sqlite3
import sys
import threading
import traceback
import uuid
import zipfile

from PyQt5.QtCore import (
    Qt,
)
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import (
    QWidget,
)
from PyQt5.uic import loadUi

import azm_sqlite_merge
import azq_server_api
import azq_utils
import db_layer_task
import db_preprocess
import qt_utils

signal.signal(signal.SIGINT, signal.SIG_DFL)  # exit upon ctrl-c


class server_overview_widget(QWidget):
    progress_update_signal = pyqtSignal(int)
    status_update_signal = pyqtSignal(str)
    apply_done_signal = pyqtSignal(str)

    def __init__(self, parent, gvars):
        super().__init__(parent)
        self.gvars = gvars
        self.setupUi()
        self.req_body = {}
        self.apply_thread = None
        self.overview_db_fp = None
        self.devices_selection_df = None

    def setupUi(self):
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.ui = loadUi(azq_utils.get_module_fp("server_overview_widget.ui"), self)
        self.setWindowTitle("Server logs overview")
        now = azq_utils.datetime_now()
        last_month = now - datetime.timedelta(days=30)
        self.ui.start_dateEdit.setDateTime(last_month)
        self.ui.end_dateEdit.setDateTime(now)

        self.applyButton.clicked.connect(self.apply)
        self.apply_done_signal.connect(self.apply_done)
        self.progress_update_signal.connect(self.progress)
        self.status_update_signal.connect(self.status)
        self.ui.phone_filter_pushButton.clicked.connect(self.on_click_phone_filter)
        self.ui.group_filter_pushButton.clicked.connect(self.on_click_group_filter)
        self.apply_read_server_facts = True
        self.setMinimumSize(320,350)
        self.apply()


    def on_processing(self, processing, processing_text="Processing..."):
        if processing:
            self.progress(0)
            self.ui.groupBox.setVisible(False)
            self.ui.applyButton.setEnabled(False)
            self.ui.applyButton.setText(processing_text)
            self.ui.progressBar.setVisible(True)
        else:
            self.ui.groupBox.setVisible(True)
            self.ui.applyButton.setText("Apply")
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
                self.progress_update_signal.emit(100)
                self.status("Completed in %.02f secs" % dur)

    def apply(self):
        self.ui.status_label.setText("")
        self.on_processing(True)
        try:
            azq_utils.timer_start("overview_apply")
            self.overview_db_fp = None
            if not self.apply_read_server_facts:
                self.read_input_to_vars()
            self.apply_thread = threading.Thread(
                target=self.apply_worker_func, args=()
            )
            self.apply_thread.start()
        except:
            type_, value_, traceback_ = sys.exc_info()
            exstr = str(traceback.format_exception(type_, value_, traceback_))
            msg = "WARNING: apply failed - exception: {}".format(exstr)
            print(msg)
            qt_utils.msgbox(msg, "Server overview", self)
            self.ui.status_label.setText(msg)
            self.on_processing(False)

    def apply_worker_func(self):
        try:
            assert self.gvars.is_logged_in()
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
            self.status_update_signal.emit("Preparing folder...")
            downloaded_db_fp = azq_utils.tmp_gen_fp("overview_{}.db".format(uuid.uuid4()))
            assert not os.path.isfile(downloaded_db_fp)
            self.status_update_signal.emit("Server processing data...")
            azq_utils.timer_start("overview_perf_dl_azm")
            ret = azq_server_api.api_overview_db_download(self.gvars.login_dialog.server, self.gvars.login_dialog.token, downloaded_db_fp,
                                                          req_body=self.req_body, signal_to_emit_stats=self.status_update_signal)
            azq_utils.timer_print("overview_perf_dl_azm")
            print("ret:", ret)
            assert os.path.isfile(ret)
            assert os.path.isfile(downloaded_db_fp)
            self.progress_update_signal.emit(30)
            '''
            self.status_update_signal.emit("Extracting compressed data...")
            self.progress_update_signal.emit(40)

            azq_utils.timer_start("overview_perf_extract_azm")
            # merge all dbs in zip to the target overview_db_fp
            tmpdir = azq_utils.tmp_gen_new_subdir()
            with zipfile.ZipFile(downloaded_db_fp, "r") as zip_file:
                zip_file.extractall(tmpdir)
            db_files = glob.glob(os.path.join(tmpdir, "*.db"))
            assert len(db_files)
            '''
            db_files = [downloaded_db_fp]  # uapi now rets direct and signle db, no zips

            azq_utils.timer_print("overview_perf_extract_azm")
            print("got dbs from server, len(db_files):", len(db_files), "at:", downloaded_db_fp)

            # combined all the db_files in the zip
            azq_utils.timer_start("overview_perf_combine_azm")
            self.status_update_signal.emit("Merging all db partitions from server...")
            dbfp = None
            if len(db_files) > 1:
                assert len(db_files) <= 2  # max now in server, for > 2 months combines it will use yearly db so there it would be 1 db file
                dbfp = azm_sqlite_merge.merge(db_files)
            else:
                dbfp = db_files[0]
            assert os.path.isfile(dbfp)
            azq_utils.timer_print("overview_perf_combine_azm")

            azq_utils.timer_start("overview_perf_prepare_views")
            self.status_update_signal.emit("Prepare db views as per theme...")
            self.progress_update_signal.emit(50)
            with contextlib.closing(sqlite3.connect(dbfp)) as dbcon:
                db_preprocess.prepare_spatialite_views(dbcon, cre_table=False)  # no need to handle log_hash time sync so no need cre_table flag (layer get attr would be empty if it is a view in clickcanvas)
            azq_utils.timer_print("overview_perf_prepare_views")

            azq_utils.timer_start("overview_perf_create_layers")
            self.status_update_signal.emit("Processing layers/legends as per theme...")
            self.progress_update_signal.emit(70)
            self.overview_db_fp = dbfp
            if self.gvars.qgis_iface:
                self.table_to_layer_dict, self.layer_id_to_visible_flag_dict, self.last_visible_layer = db_layer_task.create_layers(
                    self.gvars, db_fp=self.overview_db_fp, display_name_prefix="overview_")
            azq_utils.timer_print("overview_perf_create_layers")

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



    
