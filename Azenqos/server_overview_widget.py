import contextlib
import datetime
import os
import signal
import sqlite3
import sys
import threading
import preprocess_azm
import traceback
import uuid

from PyQt5.QtCore import (
    Qt,
)
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import (
    QWidget,
)
from PyQt5.uic import loadUi

import azq_server_api
import azq_utils
import qt_utils
import db_preprocess
import db_layer_task


signal.signal(signal.SIGINT, signal.SIG_DFL)  # exit upon ctrl-c


class server_overview_widget(QWidget):
    progress_update_signal = pyqtSignal(int)
    status_update_signal = pyqtSignal(str)
    apply_done_signal = pyqtSignal(str)

    def __init__(self, parent, gvars):
        super().__init__(parent)
        self.gvars = gvars
        self.setupUi()
        self.config = {}
        self.apply_thread = None
        self.overview_db_fp = None

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
        self.config = {}
        self.config["start_date"] = self.ui.start_dateEdit.date().toPyDate()  # becomes like '2021-09-30'
        self.config["end_date"] = self.ui.end_dateEdit.date().toPyDate()
        self.config["bin"] = int(self.ui.samp_rate_comboBox.currentText())
        print("read_input_to_vars: config:", self.config)

    def status(self, msg):
        self.ui.status_label.setText(msg)

    def progress(self, val):
        self.ui.progressBar.setValue(val)

    def apply_done(self, msg):
        self.on_processing(False)
        if not msg.startswith("SUCCESS"):
            qt_utils.msgbox(msg, "Server overview apply failed", parent=self)
            self.status(msg[:50])
        else:
            if self.apply_read_server_facts:
                bins = sorted(list(self.overview_list_df.bin.unique()), reverse=True)
                self.ui.samp_rate_comboBox.addItems(bins)
                self.apply_read_server_facts = False
            if self.gvars.main_window:
                self.gvars.main_window.add_map_layer()
            self.status("Adding new layers to QGIS...")
            self.progress_update_signal.emit(80)
            db_layer_task.LayerTask(u"Add layers", self.overview_db_fp, self.gvars, None).run_blocking(select=True)
            self.status("Adding new layers to QGIS... done")

    def apply(self):
        self.ui.status_label.setText("")
        self.on_processing(True)
        try:
            self.overview_db_fp = None
            if not self.apply_read_server_facts:
                self.read_input_to_vars()
            self.apply_thread = threading.Thread(
                target=self.apply_worker_func, args=()
            )
            self.apply_thread.start()
        except Exception as e:
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
            if self.apply_read_server_facts:
                self.overview_list_df = azq_server_api.api_overview_db_df(
                    self.gvars.login_dialog.server,
                    self.gvars.login_dialog.token
                )
                return
            self.status_update_signal.emit("Preparing folder...")
            target_fp = azq_utils.tmp_gen_fp("overview.zip")
            if os.path.isfile(target_fp):
                os.remove(target_fp)
            assert not os.path.isfile(target_fp)
            self.status_update_signal.emit("Downloading data...")
            ret = azq_server_api.api_overview_db_download(self.gvars.login_dialog.server, self.gvars.login_dialog.token, target_fp,
                                                          overview_mode_params_dict={"y": self.config["start_date"].year, "m": self.config["start_date"].month, "bin": self.config["bin"]})
            print("ret:", ret)
            assert os.path.isfile(ret)
            assert os.path.isfile(target_fp)
            self.progress_update_signal.emit(50)

            self.status_update_signal.emit("Extracting compressed data...")
            self.progress_update_signal.emit(60)
            db_folder = azq_utils.tmp_gen_fp("tmp_overview_db_{}".format(uuid.uuid4()))
            assert not os.path.isdir(db_folder)
            os.makedirs(db_folder)
            assert os.path.isdir(db_folder)
            overview_db_fp = os.path.join(db_folder, "azqdata.db")
            assert not os.path.isfile(overview_db_fp)
            preprocess_azm.extract_entry_from_zip(
                target_fp, "azqdata.db", db_folder
            )
            assert os.path.isfile(overview_db_fp)

            self.status_update_signal.emit("Preparing database as per theme...")
            self.progress_update_signal.emit(70)
            with contextlib.closing(sqlite3.connect(overview_db_fp)) as dbcon:
                db_preprocess.prepare_spatialite_views(dbcon)
            self.overview_db_fp = overview_db_fp
            self.status_update_signal.emit("DONE")
            self.progress_update_signal.emit(100)
            self.apply_done_signal.emit("SUCCESS")
            return 0
        except Exception as e:
            type_, value_, traceback_ = sys.exc_info()
            exstr = str(traceback.format_exception(type_, value_, traceback_))
            msg = "WARNING: download_overview failed - exception: {}".format(exstr)
            self.apply_done_signal.emit("FAILED: "+msg)
            return -1
        return -2



    
