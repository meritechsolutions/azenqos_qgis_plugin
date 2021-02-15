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

import azq_utils
import analyzer_vars
GUI_SETTING_NAME_PREFIX = "{}/".format(os.path.basename(__file__))
import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)  # exit upon ctrl-c
import time
import requests


class login_dialog(QDialog):
    
    def __init__(self, parent, gc):
        super(login_dialog, self).__init__(parent)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.gc = gc                
        self.setupUi()
        self.ret_dict = {}
        self.valid = False
        self.server_token = None
        self.login_thread = None
        
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
            self.done(QtWidgets.QDialog.Accepted)        
            self.ui.buttonBox.setEnabled(False)

        # start server login thread
        # thead will set buttonbox enabled if login failed
        # thread will close window and set self.server_token if success
        if self.login_thread is None or (self.login_thread.is_alive() == False):
            pass
        else:
            QtWidgets.QMessageBox.critical(
                None,
                "Please wait...",
                "Trying to log to server...",
                QtWidgets.QMessageBox.Ok,
            )
        

    def validate(self):
        self.ret_dict = self.get_result_dict()
        for key in self.ret_dict.keys():
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
        
        self.valid = True
        return True



if __name__ == "__main__":
    main()
