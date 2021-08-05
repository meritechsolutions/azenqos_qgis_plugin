import os
import threading
from urllib.parse import urlparse

import numpy as np
import pandas as pd
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QDialog, QLineEdit
from PyQt5.uic import loadUi

import azq_server_api
import azq_utils

GUI_SETTING_NAME_PREFIX = "{}/".format(os.path.basename(__file__))
import signal

signal.signal(signal.SIGINT, signal.SIG_DFL)  # exit upon ctrl-c
import qt_utils


class login_dialog(QDialog):

    progress_update_signal = pyqtSignal(int)
    status_update_signal = pyqtSignal(str)
    login_done_signal = pyqtSignal(str)

    def __init__(self, parent, gc, download_db_zip=True):
        super(login_dialog, self).__init__(parent)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.gc = gc
        self.setupUi()
        self.valid = False
        self.downloaded_zip_fp = None
        self.download_db_zip = download_db_zip

        self.server = None
        self.user = None
        self.lhl = None
        self.token = None

        self.login_thread = None
        self.login_done_signal.connect(self.on_login_done)
        self.status_update_signal.connect(self.on_status_update)
        self.progress_update_signal.connect(self.on_progress_update)

    def setupUi(self):
        dirname = os.path.dirname(__file__)
        self.setWindowIcon(QIcon(QPixmap(os.path.join(dirname, "icon.png"))))
        self.ui = loadUi(azq_utils.get_local_fp("login_dialog.ui"), self)
        self.ui.pass_le.setEchoMode(QLineEdit.Password)
        self.ui.progressbar.setVisible(False)
        self.setWindowTitle("AZENQOS Server login")
        self.ui.server_url_le.setText(
            azq_utils.read_local_file("prev_login_dialog_server")
        )
        self.ui.login_le.setText(azq_utils.read_local_file("prev_login_dialog_user"))
        self.ui.lhl_le.setText(azq_utils.read_local_file("prev_login_dialog_lhl"))

    def read_ui_input_to_vars(self):
        self.server = self.ui.server_url_le.text().strip()
        self.user = self.ui.login_le.text().strip()
        self.passwd = self.ui.pass_le.text().strip()
        self.lhl = self.ui.lhl_le.text().strip()
        return [self.server, self.user, self.passwd, self.lhl]

    def on_progress_update(self, val):
        print("progress_update: {}".format(val))
        self.ui.progressbar.setValue(val)

    def on_status_update(self, val):
        print("status_update: {}".format(val))
        self.ui.label_status.setText(val)

    def ui_login_thread_start(self):
        self.ui.buttonBox.setEnabled(False)
        self.on_progress_update(0)
        self.on_status_update("")
        self.ui.progressbar.setVisible(True)

    def ui_login_thread_failed(self):
        self.ui.buttonBox.setEnabled(True)
        self.on_progress_update(0)
        self.on_status_update("Operation failed...")
        self.ui.progressbar.setVisible(False)

    def accept(self):
        print("login_dialog: accept()")
        if self.validate():
            if self.login_thread is None or (self.login_thread.is_alive() == False):
                self.ui_login_thread_start()
                self.login_thread = threading.Thread(
                    target=azq_server_api.api_login_and_dl_db_zip,
                    args=(
                        self.server,
                        self.user,
                        self.passwd,
                        self.lhl,
                        self.progress_update_signal,
                        self.status_update_signal,
                        self.login_done_signal,
                        self.on_zip_downloaded,
                        self.download_db_zip,
                    ),
                )
                self.login_thread.start()
            else:
                QtWidgets.QMessageBox.critical(
                    None,
                    "Please wait...",
                    "Already trying to log to server...",
                    QtWidgets.QMessageBox.Ok,
                )

    def validate(self):
        vars = self.read_ui_input_to_vars()
        for val in vars:
            if not val:
                QtWidgets.QMessageBox.critical(
                    None,
                    "Missing data",
                    "Please complete all fields...",
                    QtWidgets.QMessageBox.Ok,
                )
                return False

        azq_utils.write_local_file("prev_login_dialog_server", self.server)
        print("self.user", self.user)
        azq_utils.write_local_file("prev_login_dialog_user", self.user)
        azq_utils.write_local_file("prev_login_dialog_lhl", self.lhl)

        ###### check lhl
        lhl = self.lhl
        if "," in lhl:
            lhl = lhl.split(",")
        else:
            lhl = [lhl]
        try:
            lhl = pd.Series(lhl, dtype=np.int64)
        except:
            QtWidgets.QMessageBox.critical(
                None,
                "Invalid log_hash list",
                "Provided log_hash list must be numbers and commas only",
                QtWidgets.QMessageBox.Ok,
            )
            return False

        try:
            if not self.server.startswith("https://"):
                self.server = "https://"+self.server
            assert urlparse(self.server).netloc
        except:
            QtWidgets.QMessageBox.critical(
                None,
                "Invalid server url",
                "Provided a valid server URL. Example: https://test0.azenqos.com",
                QtWidgets.QMessageBox.Ok,
            )
            return False

        self.valid = True
        return True

    def on_zip_downloaded(self, zip_fp):
        print("on_zip_downloaded: self %s zip_fp %s" % (self, zip_fp))
        self.downloaded_zip_fp = zip_fp

    def on_login_done(self, error):
        print("on_login_done: error: {}".format(error))
        success = False
        if error.startswith("SUCCESS,"):
            self.token = error.split(",")[1]
            success = True
        if not success:
            QtWidgets.QMessageBox.critical(
                self, "Operation failed...", error, QtWidgets.QMessageBox.Ok,
            )
            self.ui_login_thread_failed()
        else:
            qt_utils.msgbox("Login successful", parent=self)
            print("on_login_done self.downloaded_zip_fp: %s" % self.downloaded_zip_fp)
            self.done(QtWidgets.QDialog.Accepted)
