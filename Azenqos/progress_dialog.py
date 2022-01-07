import PyQt5
from PyQt5.QtWidgets import QDialog
from PyQt5.uic import loadUi
from PyQt5.QtGui import QIcon, QPixmap

import os

import azq_utils

class progress_dialog(QDialog):
    def __init__(self, title="Progress Bar"):
        super(progress_dialog, self).__init__(None)
        self.title = title
        self.setupUi()

    def setupUi(self):
        dirname = os.path.dirname(__file__)
        self.ui = loadUi(azq_utils.get_module_fp("progress_dialog.ui"), self)
        self.setWindowIcon(QIcon(QPixmap(os.path.join(dirname, "icon.png"))))
        self.setWindowTitle(self.title)
    
    def set_value(self, value):
        self.ui.progressBar.setValue(value)
    
    def closeEvent(self, event):
        event.ignore()
        self.hide()