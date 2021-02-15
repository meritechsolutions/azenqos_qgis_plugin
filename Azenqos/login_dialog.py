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
import pandas as pd
import numpy as np
from urllib.parse import urlparse

import azq_utils
import analyzer_vars
GUI_SETTING_NAME_PREFIX = "{}/".format(os.path.basename(__file__))
import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)  # exit upon ctrl-c
import time


class login_dialog(QDialog):

    login_done_signal = pyqtSignal(str)
    
    def __init__(self, parent, gc):
        super(login_dialog, self).__init__(parent)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.gc = gc                
        self.setupUi()
        self.ret_dict = {}
        self.valid = False
        self.server_token = None
        self.login_thread = None
        self.login_done_signal.connect(
            self.ui_thread_handler_login_completed
        )

        

    def setupUi(self):
        dirname = os.path.dirname(__file__)
        self.setWindowIcon(QIcon(QPixmap(os.path.join(dirname, "icon.png"))))
        self.ui = loadUi(azq_utils.get_local_fp("login_dialog.ui"), self)
        self.setWindowTitle("AZENQOS Server login")
        self.ui.server_url_le.setText(azq_utils.read_local_file("prev_login_dialog_server_url"))
        self.ui.login_le.setText(azq_utils.read_local_file("prev_login_dialog_login"))
        self.ui.lhl_le.setText(azq_utils.read_local_file("prev_login_dialog_lhl"))
        

    def get_result_dict(self):
        ret_dict = {
            "server_url": self.ui.server_url_le.text(),
            "login": self.ui.login_le.text(),
            "pass": self.ui.pass_le.text(),            
            "lhl": self.ui.lhl_le.text(),
        }
        return ret_dict

    
    def accept(self):
        print("login_dialog: accept")        
        if self.validate():
            self.ui.buttonBox.setEnabled(False)
            if self.login_thread is None or (self.login_thread.is_alive() == False):
                self.login_thread = threading.Thread(target=self.login_and_dl_db_zip, args=())
                self.login_thread.start()
            else:
                QtWidgets.QMessageBox.critical(
                    None,
                    "Please wait...",
                    "Already trying to log to server...",
                    QtWidgets.QMessageBox.Ok,
                )

            
    def validate(self):
        self.ret_dict = self.get_result_dict()
        for key in self.ret_dict.keys():
            self.ret_dict[key] = str(self.ret_dict[key])
            val = self.ret_dict[key]
            if not val:        
                QtWidgets.QMessageBox.critical(
                    None,
                    "Missing data",
                    "Please complete all fields...",
                    QtWidgets.QMessageBox.Ok,
                )
                return False

        azq_utils.write_local_file(
            "prev_login_dialog_server_url", self.ret_dict["server_url"]
        )
        azq_utils.write_local_file(
            "prev_login_dialog_login", self.ret_dict["login"]
        )
        azq_utils.write_local_file(
            "prev_login_dialog_lhl", self.ret_dict["lhl"]
        )

        ###### check lhl
        lhl = self.ret_dict["lhl"].strip()
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
            assert urlparse(self.ret_dict["server_url"]).netloc
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

    
    def login_and_dl_db_zip(self):
        try:
            self.server_token = login(self.ret_dict)

            # TODO: call azq_json_api prepare db zip for the selection of log_hash_list, then dl zip to tmp
            
            self.login_done_signal.emit("")
        except:
            type_, value_, traceback_ = sys.exc_info()
            exstr = str(traceback.format_exception(type_, value_, traceback_))
            self.login_done_signal.emit(exstr)

            

    def ui_thread_handler_login_completed(self, error):
        if error:
            QtWidgets.QMessageBox.critical(
                None,
                "Login failed...",
                error,
                QtWidgets.QMessageBox.Ok,
            )
            self.ui.buttonBox.setEnabled(True)
        else:            
            self.done(QtWidgets.QDialog.Accepted)        



def login(args_dict):
    token = None
    host = urlparse(args_dict["server_url"]).netloc
    print("login host: %s" % host)
    assert args_dict["server_url"]
    assert args_dict["login"]
    assert args_dict["pass"]
    token = azq_utils.login_get_token(args_dict["login"], args_dict["pass"], host)
    return token

