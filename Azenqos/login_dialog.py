from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtSql import *
from PyQt5.QtGui import *
from PyQt5.uic import loadUi
import threading
import sys
import traceback
import os
import csv
import re
import pandas as pd
import numpy as np
from urllib.parse import urlparse
import requests
import azq_server_api
import azq_utils
import analyzer_vars
GUI_SETTING_NAME_PREFIX = "{}/".format(os.path.basename(__file__))
import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)  # exit upon ctrl-c
import time


class login_dialog(QDialog):

    progress_update_signal = pyqtSignal(int)
    status_update_signal = pyqtSignal(str)
    login_done_signal = pyqtSignal(str)
    
    def __init__(self, parent, gc):
        super(login_dialog, self).__init__(parent)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.gc = gc                
        self.setupUi()
        self.valid = False

        self.login_thread = None
        self.login_done_signal.connect(
            self.ui_thread_handler_login_completed
        )
        self.status_update_signal.connect(
            self.status_update
        )
        self.progress_update_signal.connect(
            self.progress_update
        )

        

    def setupUi(self):
        dirname = os.path.dirname(__file__)
        self.setWindowIcon(QIcon(QPixmap(os.path.join(dirname, "icon.png"))))
        self.ui = loadUi(azq_utils.get_local_fp("login_dialog.ui"), self)
        self.ui.pass_le.setEchoMode(QLineEdit.Password)
        self.ui.progressbar.setVisible(False)
        self.setWindowTitle("AZENQOS Server login")
        self.ui.server_url_le.setText(azq_utils.read_local_file("prev_login_dialog_server"))
        self.ui.login_le.setText(azq_utils.read_local_file("prev_login_dialog_user"))
        self.ui.lhl_le.setText(azq_utils.read_local_file("prev_login_dialog_lhl"))
        

    def read_ui_input_to_vars(self):
        self.server = self.ui.server_url_le.text()
        self.user = self.ui.login_le.text()
        self.passwd = self.ui.pass_le.text()
        self.lhl = self.ui.lhl_le.text()
        return [self.server, self.user, self.passwd, self.lhl]

    def progress_update(self, val):
        print("progress_update: {}".format(val))
        self.ui.progressbar.setValue(val)

    def status_update(self, val):
        print("status_update: {}".format(val))
        self.ui.label_status.setText(val)

    def ui_login_thread_start(self):
        self.ui.buttonBox.setEnabled(False)
        self.progress_update(0)
        self.status_update("")
        self.ui.progressbar.setVisible(True)

    def ui_login_thread_failed(self):
        self.ui.buttonBox.setEnabled(True)
        self.progress_update(0)
        self.status_update("Operation failed...")
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
                        self.login_done_signal
                    )
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

        azq_utils.write_local_file(
            "prev_login_dialog_server", self.server
        )
        print("self.user", self.user)
        azq_utils.write_local_file(
            "prev_login_dialog_user", self.user
        )
        azq_utils.write_local_file(
            "prev_login_dialog_lhl", self.lhl
        )

        ###### check lhl
        lhl = self.lhl.strip()
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


    def ui_thread_handler_login_completed(self, error):
        if error:
            QtWidgets.QMessageBox.critical(
                None,
                "Operation failed...",
                error,
                QtWidgets.QMessageBox.Ok,
            )
            self.ui_login_thread_failed()
        else:            
            self.done(QtWidgets.QDialog.Accepted)


"""
def login(args_dict):
    token = None
    host = urlparse(args_dict["server_url"]).netloc
    print("login host: %s" % host)
    assert args_dict["server_url"]
    assert args_dict["login"]
    assert args_dict["pass"]
    token = api_login_get_token(args_dict["login"], args_dict["pass"], host)
    return token


"""
