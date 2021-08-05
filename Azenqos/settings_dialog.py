import os
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


class settings_dialog(QDialog):


    def __init__(self, parent, gc, download_db_zip=True):
        super(settings_dialog, self).__init__(parent)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.gc = gc
        self.valid = False
        self.setupUi()

    def setupUi(self):
        dirname = os.path.dirname(__file__)
        self.setWindowIcon(QIcon(QPixmap(os.path.join(dirname, "icon.png"))))
        self.ui = loadUi(azq_utils.get_local_fp("settings_dialog.ui"), self)
        self.ui.sector_size_m_lineEdit.setText(
            azq_utils.read_local_file("sector_size_m")
        )
        

    def read_ui_input_to_vars(self):
        ret = []
        return ret


    def accept(self):
        print("login_dialog: accept()")
        if self.validate():
            self.done(QtWidgets.QDialog.Accepted)


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
        self.valid = True
        return True

